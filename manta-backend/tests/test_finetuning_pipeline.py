"""
tests/test_finetuning_pipeline.py — Suíte de `ml/finetuning.py` (pipeline
de fine-tuning LoRA por segmento: prepare_dataset, create_trainer, train,
save_adapter, load_adapter) e do endpoint `POST /ml/finetune`
(routers/ml.py).

Nome do arquivo deliberadamente distinto de `tests/test_finetuning.py`
(suíte já existente de `ml/lora_finetuner.py`, o módulo de fine-tuning
anterior/paralelo) — evita colisão entre os dois módulos de fine-tuning
que convivem neste repositório.

Roda 100% offline: usa `demo_mode=True` (ver
ml/finetuning.py::build_demo_base_model_and_tokenizer) em vez do
Mistral-7B real, para não depender de rede/GPU/download de pesos do
Hugging Face Hub em CI — mesmo princípio do encoder "hashing" em
tests/test_routing_ml.py. O contrato exercitado (prepare_dataset →
create_trainer → train → save_adapter → load_adapter, e o endpoint
HTTP) é idêntico ao usado com o Mistral-7B real; só a qualidade do
modelo muda.
"""
import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from ml.finetuning import (
    SUPPORTED_SEGMENTS,
    LoRAAdapterConfig,
    TrainingConfig,
    build_demo_base_model_and_tokenizer,
    create_trainer,
    generate,
    load_adapter,
    prepare_dataset,
    resolve_dataset_path,
    run_finetuning_pipeline,
    save_adapter,
    train,
)


# ---------------------------------------------------------------------------
# Segmentos suportados / datasets
# ---------------------------------------------------------------------------


def test_supported_segments_matches_claude_md_verticals():
    """Os 5 segmentos verticais expandidos em v4.2 (S6-S10) — ver
    CLAUDE.md 'MAPA COMPLETO DE AGENTES'."""
    assert set(SUPPORTED_SEGMENTS) == {"saneamento", "energia", "portos", "aeroportos", "barragens"}


def test_resolve_dataset_path_saneamento_exists():
    assert resolve_dataset_path("saneamento").exists()


def test_prepare_dataset_missing_file_raises_file_not_found(tmp_path):
    _, tokenizer = build_demo_base_model_and_tokenizer(["texto de exemplo qualquer"])
    with pytest.raises(FileNotFoundError):
        prepare_dataset("saneamento", tokenizer, dataset_path=tmp_path / "nao_existe.json")


# ---------------------------------------------------------------------------
# Pipeline completa (offline, demo_mode) — prepare_dataset -> create_trainer
# -> train -> save_adapter -> load_adapter
# ---------------------------------------------------------------------------


def _load_saneamento_texts() -> list[str]:
    with open(resolve_dataset_path("saneamento"), "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [item.get("text", "") for item in raw]


@pytest.fixture(scope="module")
def demo_base():
    """Modelo/tokenizer demo (GPT-2 minúsculo, offline) treinado no
    próprio dataset de saneamento — reaproveitado só pelos testes que
    NÃO aplicam LoRA (`get_peft_model` modifica os submódulos do modelo
    base em memória, então reusar um modelo já "LoRA-ficado" entre
    testes gera o warning "modify a model with PEFT for a second time"
    — testes que chamam create_trainer()/apply_lora_adapter() usam
    `fresh_demo_base`, função-scoped, em vez deste)."""
    return build_demo_base_model_and_tokenizer(_load_saneamento_texts())


@pytest.fixture
def fresh_demo_base():
    """Igual a `demo_base`, mas função-scoped — usado pelos testes que
    aplicam LoRA ao modelo (create_trainer/apply_lora_adapter mutam os
    submódulos do modelo em memória; reusar a mesma instância entre
    testes dispararia o warning "modify a model with PEFT for a second
    time" do peft)."""
    return build_demo_base_model_and_tokenizer(_load_saneamento_texts())


def test_prepare_dataset_tokenizes_saneamento(demo_base):
    _, tokenizer = demo_base
    dataset = prepare_dataset("saneamento", tokenizer, max_seq_length=64, num_examples=6)
    assert len(dataset) == 6
    assert set(dataset.column_names) == {"input_ids", "attention_mask", "labels"}
    assert len(dataset[0]["input_ids"]) == 64
    assert dataset[0]["labels"] == dataset[0]["input_ids"]


def test_create_trainer_applies_lora_adapter(fresh_demo_base):
    model, tokenizer = fresh_demo_base
    dataset = prepare_dataset("saneamento", tokenizer, max_seq_length=64, num_examples=6)

    adapter = LoRAAdapterConfig(r=4, lora_alpha=8, target_modules=["c_attn"])
    trainer = create_trainer(
        model, adapter, dataset, tokenizer,
        training_config=TrainingConfig(num_epochs=1, batch_size=2, validation_split=0.0),
    )

    from peft import PeftModel

    assert isinstance(trainer.model, PeftModel)


def test_full_pipeline_train_save_load_roundtrip(tmp_path):
    """Fim-a-fim: run_finetuning_pipeline(demo_mode=True) treina, salva
    o adapter em disco, e o adapter recarregado gera texto (mesmo que a
    qualidade seja baixa — é só um smoke test mecânico da pipeline, não
    da qualidade do fine-tune)."""
    result = run_finetuning_pipeline(
        segment="saneamento",
        epochs=1,
        demo_mode=True,
        max_examples=6,
        output_dir=tmp_path / "saneamento_adapter",
    )

    assert result.segment == "saneamento"
    assert result.base_model == "demo-tiny-gpt2-offline"
    assert result.metrics.num_train_steps > 0
    assert result.metrics.loss > 0

    adapter_dir = tmp_path / "saneamento_adapter"
    assert (adapter_dir / "adapter_config.json").exists()
    assert (adapter_dir / "adapter_model.safetensors").exists()
    assert (adapter_dir / "metrics.json").exists()

    saved_metrics = json.loads((adapter_dir / "metrics.json").read_text(encoding="utf-8"))
    assert saved_metrics["segment"] == "saneamento"

    # load_adapter() exige base_model explícito para adapters demo (o
    # modelo demo não é recarregável do Hub por nome).
    with pytest.raises(ValueError):
        load_adapter(adapter_dir)

    with open(resolve_dataset_path("saneamento"), "r", encoding="utf-8") as f:
        raw = json.load(f)
    texts = [item.get("text", "") for item in raw]
    base_model, tokenizer = build_demo_base_model_and_tokenizer(texts)

    loaded = load_adapter(adapter_dir, base_model=base_model)
    text = generate(loaded, tokenizer, "SNIS", max_new_tokens=8)
    assert isinstance(text, str) and len(text) > 0


def test_save_adapter_without_tokenizer_still_saves_weights(tmp_path, fresh_demo_base):
    model, tokenizer = fresh_demo_base
    dataset = prepare_dataset("saneamento", tokenizer, max_seq_length=64, num_examples=4)
    trainer = create_trainer(
        model, LoRAAdapterConfig(target_modules=["c_attn"]), dataset, tokenizer,
        training_config=TrainingConfig(num_epochs=1, batch_size=2, validation_split=0.0),
    )
    metrics = train(trainer, segment="saneamento", base_model_name="demo-tiny-gpt2-offline")

    out = save_adapter(trainer.model, tmp_path / "no_tokenizer_adapter", metrics=metrics)
    assert (tmp_path / "no_tokenizer_adapter" / "adapter_config.json").exists()
    assert (tmp_path / "no_tokenizer_adapter" / "metrics.json").exists()
    assert not (tmp_path / "no_tokenizer_adapter" / "tokenizer_config.json").exists()
    assert out == str(tmp_path / "no_tokenizer_adapter")


@pytest.mark.parametrize("segment", ["energia", "portos", "aeroportos", "barragens"])
def test_prepare_dataset_works_for_other_segments_when_dataset_present(segment, demo_base):
    """Só roda de fato se o dataset do segmento já existir em data/ (ver
    docs/DEPLOY-v4.2.md checklist) — os outros 4 segmentos (além de
    saneamento) ainda podem não ter dataset commitado dependendo do
    estado do repositório."""
    path = resolve_dataset_path(segment)
    if not path.exists():
        pytest.skip(f"dataset ainda não existe para {segment!r}: {path}")

    _, tokenizer = demo_base
    dataset = prepare_dataset(segment, tokenizer, max_seq_length=64, num_examples=4)
    assert len(dataset) == 4


# ---------------------------------------------------------------------------
# Endpoint HTTP — POST /ml/finetune
# ---------------------------------------------------------------------------


@pytest.fixture
def ml_app(tmp_path, monkeypatch) -> FastAPI:
    from routers import ml as ml_router_module

    # Evita poluir manta-backend/ml/adapters/ com artefatos de teste —
    # redireciona o output default da pipeline para um tmp_path.
    monkeypatch.setattr("ml.finetuning.DEFAULT_OUTPUT_DIR", tmp_path)
    ml_router_module._MEMORY_JOBS.clear()

    app = FastAPI()
    app.include_router(ml_router_module.router)
    return app


@pytest_asyncio.fixture
async def ml_client(ml_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=ml_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


async def _poll_until_done(client: httpx.AsyncClient, job_id: str, timeout_s: float = 30.0) -> dict:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout_s
    while loop.time() < deadline:
        resp = await client.get(f"/ml/finetune/{job_id}")
        body = resp.json()
        if body["status"] in ("completed", "failed"):
            return body
        await asyncio.sleep(0.2)
    raise AssertionError(f"job {job_id} não terminou em {timeout_s}s")


@pytest.mark.asyncio
async def test_post_finetune_rejects_unknown_segment(ml_client):
    resp = await ml_client.post("/ml/finetune", json={"segment": "rodovias", "epochs": 1})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_post_finetune_returns_202_queued(ml_client):
    resp = await ml_client.post(
        "/ml/finetune", json={"segment": "saneamento", "epochs": 1, "demo_mode": True}
    )
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "queued"
    assert body["segment"] == "saneamento"
    assert body["id"]


@pytest.mark.asyncio
async def test_finetune_job_completes_and_produces_adapter(ml_client):
    resp = await ml_client.post(
        "/ml/finetune",
        json={"segment": "saneamento", "epochs": 1, "demo_mode": True},
    )
    job_id = resp.json()["id"]

    final = await _poll_until_done(ml_client, job_id)

    assert final["status"] == "completed"
    assert final["adapter_path"]
    assert final["loss"] is not None
    assert final["num_train_steps"] > 0
    assert Path(final["adapter_path"]).exists()


@pytest.mark.asyncio
async def test_get_finetune_job_404_for_unknown_id(ml_client):
    resp = await ml_client.get("/ml/finetune/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_finetune_jobs_filters_by_segment(ml_client):
    resp = await ml_client.post(
        "/ml/finetune", json={"segment": "saneamento", "epochs": 1, "demo_mode": True}
    )
    job_id = resp.json()["id"]
    await _poll_until_done(ml_client, job_id)

    resp = await ml_client.get("/ml/finetune", params={"segment": "saneamento"})
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) >= 1
    assert all(j["segment"] == "saneamento" for j in jobs)
