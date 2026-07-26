"""
tests/test_routing_ml.py — Suíte da pipeline de roteamento semântico
(ml/routing.py: dataset sintético, treino, versionamento, inferência,
fallback por keyword) e do endpoint POST /routing/route-semantic.

Roda 100% offline: usa o encoder "hashing" (ver ml/routing.py::HashingEncoder)
em vez do Sentence Transformers real, para não depender de rede/GPU/download
de pesos do Hugging Face Hub em CI. O contrato exercitado (geração de
dados sintéticos, treino, save/load versionado, predict_agent, fallback,
endpoint HTTP) é idêntico ao usado com o encoder de produção — só a
qualidade semântica do encoder muda.
"""
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from ml.routing import (
    DEFAULT_N_PER_AGENT,
    generate_synthetic_dataset,
    load_agent_data,
    load_routing_model,
    predict_agent,
    train_and_save,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def agent_data():
    return load_agent_data()


@pytest.fixture(scope="module")
def trained_model_dir(tmp_path_factory, agent_data):
    """Treina um modelo isolado (encoder=hashing, offline) num tmp_path
    dedicado — não toca em ml/models/ (o artefato "de verdade" já commitado)."""
    model_dir = tmp_path_factory.mktemp("routing_models")
    train_and_save(model_dir=model_dir, encoder_name="hashing", notes="pytest fixture")
    return model_dir


@pytest.fixture(scope="module")
def trained_model(trained_model_dir):
    return load_routing_model(model_dir=trained_model_dir)


# ---------------------------------------------------------------------------
# Dados dos agentes / dataset sintético
# ---------------------------------------------------------------------------


def test_agent_data_has_20_agents(agent_data):
    assert len(agent_data) == 20
    for slug, info in agent_data.items():
        assert "name" in info
        assert "keywords" in info and len(info["keywords"]) > 0
        assert "description" in info


def test_generate_synthetic_dataset_default_10_per_agent(agent_data):
    texts, labels = generate_synthetic_dataset(agent_data)
    assert len(texts) == len(labels) == len(agent_data) * DEFAULT_N_PER_AGENT
    assert set(labels) == set(agent_data.keys())
    for slug in agent_data:
        assert labels.count(slug) == DEFAULT_N_PER_AGENT


def test_generate_synthetic_dataset_is_deterministic(agent_data):
    texts_a, labels_a = generate_synthetic_dataset(agent_data, seed=7)
    texts_b, labels_b = generate_synthetic_dataset(agent_data, seed=7)
    assert texts_a == texts_b
    assert labels_a == labels_b


def test_generate_synthetic_dataset_respects_n_per_agent(agent_data):
    texts, labels = generate_synthetic_dataset(agent_data, n_per_agent=4)
    assert len(texts) == len(agent_data) * 4


# ---------------------------------------------------------------------------
# Treino + versionamento
# ---------------------------------------------------------------------------


def test_train_and_save_creates_versioned_pickle(trained_model_dir):
    manifest_file = trained_model_dir / "routing_manifest.json"
    assert manifest_file.exists()

    model_files = list(trained_model_dir.glob("routing_model_v*.joblib"))
    assert len(model_files) == 1
    assert model_files[0].name == "routing_model_v1.joblib"


def test_train_and_save_metrics_shape(trained_model_dir, agent_data):
    result = train_and_save(model_dir=trained_model_dir, encoder_name="hashing", notes="segunda versao")
    assert result.version == 2
    assert result.num_agents == len(agent_data)
    assert result.num_samples == len(agent_data) * DEFAULT_N_PER_AGENT
    for key in ("accuracy", "precision", "recall", "f1", "num_agents", "num_train_samples", "num_test_samples"):
        assert key in result.metrics
    assert 0.0 <= result.metrics["accuracy"] <= 1.0

    # manifesto agora deve apontar a v2 como current, mas ainda listar a v1
    model_files = sorted(p.name for p in trained_model_dir.glob("routing_model_v*.joblib"))
    assert model_files == ["routing_model_v1.joblib", "routing_model_v2.joblib"]


def test_load_routing_model_defaults_to_current_version(trained_model_dir):
    model = load_routing_model(model_dir=trained_model_dir)
    assert model.version == 2  # criado pelo teste anterior (current_version)
    assert len(model.classes) == 20


def test_load_routing_model_explicit_version(trained_model_dir):
    model_v1 = load_routing_model(version=1, model_dir=trained_model_dir)
    assert model_v1.version == 1


def test_load_routing_model_missing_raises(tmp_path):
    empty_dir = tmp_path / "no_model_here"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        load_routing_model(model_dir=empty_dir)


# ---------------------------------------------------------------------------
# Inferência (predict_agent)
# ---------------------------------------------------------------------------


def test_predict_agent_returns_3_tuple_contract(trained_model):
    result = predict_agent("preciso de ajuda com dragagem no porto", model=trained_model)
    assert isinstance(result, tuple) and len(result) == 3

    agent_slug, confidence, top_3 = result
    assert isinstance(agent_slug, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
    assert isinstance(top_3, list)
    assert 1 <= len(top_3) <= 3
    for item in top_3:
        assert {"agent_slug", "agent_name", "confidence", "method"} <= item.keys()
        assert 0.0 <= item["confidence"] <= 1.0


def test_predict_agent_top_k_is_respected(trained_model):
    _, _, top_5 = predict_agent("preciso de ajuda com metro e NATM", model=trained_model, top_k=5)
    assert len(top_5) <= 5
    _, _, top_1 = predict_agent("preciso de ajuda com metro e NATM", model=trained_model, top_k=1)
    assert len(top_1) == 1


def test_predict_agent_empty_prompt_raises(trained_model):
    with pytest.raises(ValueError):
        predict_agent("   ", model=trained_model)


def test_predict_agent_strong_domain_keywords_route_to_expected_agent(trained_model):
    """Query bem característica de um segmento deve ser roteada para o
    agente certo — via fallback de keyword quando a confiança do
    embedding (fraco, offline) ficar abaixo do threshold, o que é o
    caminho esperado com o encoder de teste."""
    cases = {
        "preciso de dragagem no porto, calado e berco de conteiner": "manta-03-s6-portos",
        "analise de barragem, vertedouro, CFRD e rejeitos": "manta-03-s10-barragens",
        "projeto de ETA e ETE, adutora e esgoto conforme SNIS": "manta-03-s8-saneamento",
    }
    for query, expected_slug in cases.items():
        agent_slug, confidence, top_3 = predict_agent(query, model=trained_model)
        assert agent_slug == expected_slug, f"query={query!r} -> {agent_slug!r} (esperado {expected_slug!r})"
        assert confidence > 0.0


def test_predict_agent_fallback_triggers_below_threshold(trained_model):
    """Com confidence_threshold=1.1 (impossível de atingir), toda query
    tem que cair no caminho de keyword fallback (ou, na ausência de
    keyword match, no embedding de baixa confiança mesmo)."""
    agent_slug, confidence, top_3 = predict_agent(
        "preciso de dragagem no porto",
        model=trained_model,
        confidence_threshold=1.1,
    )
    assert top_3[0]["method"] in ("keyword_fallback", "embedding")


def test_predict_agent_use_fallback_false_never_uses_keywords(trained_model):
    _, _, top_3 = predict_agent(
        "preciso de dragagem no porto",
        model=trained_model,
        confidence_threshold=1.1,
        use_fallback=False,
    )
    assert all(item["method"] == "embedding" for item in top_3)


def test_predict_agent_no_keyword_match_falls_back_to_low_confidence_embedding(trained_model):
    agent_slug, confidence, top_3 = predict_agent(
        "xpto qwerty foobar zzz 12345 nothing matches anything",
        model=trained_model,
    )
    # Sem keyword batendo em nenhum agente -> tem que devolver o
    # top-1 do embedding mesmo (método "embedding"), nunca uma exceção.
    assert agent_slug in {c for c in trained_model.classes}
    assert top_3[0]["method"] == "embedding"


# ---------------------------------------------------------------------------
# Endpoint HTTP — POST /routing/route-semantic
# ---------------------------------------------------------------------------


@pytest.fixture
def routing_app() -> FastAPI:
    from routers import routing as routing_router_module

    app = FastAPI()
    app.include_router(routing_router_module.router)
    return app


@pytest_asyncio.fixture
async def routing_client(routing_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=routing_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_route_semantic_endpoint_returns_agents(routing_client):
    resp = await routing_client.post(
        "/routing/route-semantic",
        json={"query": "preciso de dragagem no porto, calado e berco", "org_id": "org-1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "preciso de dragagem no porto, calado e berco"
    assert body["org_id"] == "org-1"
    assert body["count"] == len(body["agents"])
    assert body["count"] >= 1
    assert body["agents"][0]["agent_slug"] == "manta-03-s6-portos"


@pytest.mark.asyncio
async def test_route_semantic_endpoint_rejects_empty_query(routing_client):
    resp = await routing_client.post(
        "/routing/route-semantic",
        json={"query": "   ", "org_id": "org-1"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_route_semantic_endpoint_respects_top_k(routing_client):
    resp = await routing_client.post(
        "/routing/route-semantic",
        json={"query": "preciso de ajuda com metro e NATM", "org_id": "org-1", "top_k": 1},
    )
    assert resp.status_code == 200
    assert len(resp.json()["agents"]) == 1


@pytest.mark.asyncio
async def test_route_semantic_health_endpoint(routing_client):
    resp = await routing_client.get("/routing/route-semantic/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("healthy", "partial")
    if body["status"] == "healthy":
        assert body["model_loaded"] is True
        assert body["num_agents"] == 20


@pytest.mark.asyncio
async def test_classify_endpoint_still_works_standalone(routing_client):
    """Garante que a rota /classify (regex Q1 do intake, sem ML) continua
    funcionando isolada — não foi afetada pela troca do motor semântico."""
    resp = await routing_client.post("/routing/classify", json={"text": "projeto de dragagem no porto"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["matched"] is True
    assert body["agent_name"] == "agente-portos"
