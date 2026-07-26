"""
tests/test_embeddings.py — Suíte unitária de `ml/embeddings.py`.

Todos os testes fazem monkeypatch do singleton do modelo (`ml.embeddings._model`)
com um dublê leve — nada baixa/roda o Sentence Transformers real (`all-MiniLM-L6-v2`)
aqui, então a suíte roda sem GPU, sem rede e em milissegundos. O contrato
testado (assinatura async, shape do vetor, ordem preservada em batch,
tratamento de texto vazio) é o mesmo que o modelo real precisa satisfazer —
ver tests/test_rag_store.py para o caminho que efetivamente insere/busca
no Postgres+pgvector.
"""
from __future__ import annotations

import numpy as np
import pytest

import ml.embeddings as embeddings_module
from ml.embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL_NAME,
    embed_batch,
    embed_text,
    embed_texts,
    get_model_info,
)


class _FakeSentenceTransformer:
    """Dublê determinístico do SentenceTransformer real: cada texto vira
    um vetor derivado do seu hash (mesmo texto -> mesmo vetor sempre;
    textos diferentes -> vetores [quase certamente] diferentes), sem
    precisar carregar pesos de rede neural nenhuns."""

    def encode(
        self,
        texts,
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
        batch_size: int | None = None,
        show_progress_bar: bool | None = None,
    ):
        is_batch = isinstance(texts, list)
        inputs = texts if is_batch else [texts]

        vectors = []
        for text in inputs:
            rng = np.random.default_rng(abs(hash(text)) % (2**32))
            vec = rng.random(EMBEDDING_DIMENSIONS).astype(np.float32)
            if normalize_embeddings:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            vectors.append(vec)

        result = np.stack(vectors)
        return result if is_batch else result[0]


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    """Instala o dublê como singleton já 'carregado' antes de cada teste,
    e limpa o singleton depois — isolamento total entre testes."""
    monkeypatch.setattr(embeddings_module, "_model", _FakeSentenceTransformer())
    monkeypatch.setattr(embeddings_module, "_model_device", "cpu")
    yield
    monkeypatch.setattr(embeddings_module, "_model", None)
    monkeypatch.setattr(embeddings_module, "_model_device", None)


# ---------------------------------------------------------------------------
# embed_text
# ---------------------------------------------------------------------------
async def test_embed_text_returns_vector_of_expected_dimension():
    vector = await embed_text("saneamento básico e drenagem urbana")
    assert isinstance(vector, list)
    assert len(vector) == EMBEDDING_DIMENSIONS
    assert all(isinstance(x, float) for x in vector)


async def test_embed_text_is_deterministic_for_same_input():
    v1 = await embed_text("edital ANEEL de transmissão")
    v2 = await embed_text("edital ANEEL de transmissão")
    assert v1 == v2


async def test_embed_text_differs_for_different_input():
    v1 = await embed_text("porto e dragagem")
    v2 = await embed_text("barragem e vertedouro")
    assert v1 != v2


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
async def test_embed_text_empty_or_whitespace_returns_zero_vector(blank):
    vector = await embed_text(blank)
    assert vector == [0.0] * EMBEDDING_DIMENSIONS


async def test_embed_text_strips_whitespace_before_encoding():
    v1 = await embed_text("aeroporto")
    v2 = await embed_text("  aeroporto  ")
    assert v1 == v2


# ---------------------------------------------------------------------------
# embed_texts (batch) — e o alias embed_batch
# ---------------------------------------------------------------------------
async def test_embed_texts_empty_list_returns_empty_list():
    assert await embed_texts([]) == []


async def test_embed_texts_matches_embed_text_per_item():
    texts = ["rodovia", "ferrovia", "metrô"]
    batch_result = await embed_texts(texts)
    individual_results = [await embed_text(t) for t in texts]

    assert len(batch_result) == len(texts)
    for batch_vec, individual_vec in zip(batch_result, individual_results):
        assert batch_vec == pytest.approx(individual_vec)


async def test_embed_texts_preserves_order():
    texts = ["primeiro", "segundo", "terceiro"]
    result = await embed_texts(texts)

    # Cada vetor do batch deve bater com o embed_text do MESMO índice,
    # não de outro (garante que a reordenação por índice original está
    # correta mesmo misturando textos vazios no meio do batch).
    assert result[0] == await embed_text(texts[0])
    assert result[1] == await embed_text(texts[1])
    assert result[2] == await embed_text(texts[2])
    assert result[0] != result[1] != result[2]


async def test_embed_texts_handles_blank_entries_within_batch():
    texts = ["rodovia", "", "ferrovia", "   "]
    result = await embed_texts(texts)

    assert len(result) == 4
    assert result[1] == [0.0] * EMBEDDING_DIMENSIONS
    assert result[3] == [0.0] * EMBEDDING_DIMENSIONS
    assert result[0] == await embed_text("rodovia")
    assert result[2] == await embed_text("ferrovia")


async def test_embed_texts_all_blank_returns_all_zero_vectors():
    result = await embed_texts(["", "  ", ""])
    assert result == [[0.0] * EMBEDDING_DIMENSIONS] * 3


async def test_embed_batch_is_alias_for_embed_texts():
    assert embed_batch is embed_texts


async def test_embed_batch_still_works_for_backward_compat():
    """tasks/embed_rag_chunks.py importa `embed_batch` — garante que o
    alias continua funcionando como uma chamada de batch normal."""
    result = await embed_batch(["saneamento", "energia"])
    assert len(result) == 2
    assert all(len(v) == EMBEDDING_DIMENSIONS for v in result)


# ---------------------------------------------------------------------------
# get_model_info
# ---------------------------------------------------------------------------
def test_get_model_info_reports_loaded_state(fake_model):
    info = get_model_info()
    assert info["model_name"] == EMBEDDING_MODEL_NAME
    assert info["dimensions"] == EMBEDDING_DIMENSIONS
    assert info["device"] == "cpu"
    assert info["status"] == "carregado"


def test_get_model_info_reports_not_loaded_when_model_is_none(monkeypatch):
    monkeypatch.setattr(embeddings_module, "_model", None)
    monkeypatch.setattr(embeddings_module, "_model_device", None)
    info = get_model_info()
    assert info["status"] == "não carregado"
    assert info["device"] == "não carregado"


# ---------------------------------------------------------------------------
# _load_model — lazy singleton (só testável isolando o import do
# construtor real do SentenceTransformer, que não instalamos/baixamos aqui)
# ---------------------------------------------------------------------------
def test_load_model_reuses_existing_singleton(monkeypatch):
    sentinel = _FakeSentenceTransformer()
    monkeypatch.setattr(embeddings_module, "_model", sentinel)

    loaded = embeddings_module._load_model()

    assert loaded is sentinel  # não deve tentar (re)carregar/baixar nada


def test_load_model_wraps_failures_in_runtime_error(monkeypatch):
    monkeypatch.setattr(embeddings_module, "_model", None)

    class _BoomSentenceTransformer:
        def __init__(self, *args, **kwargs):
            raise OSError("modelo indisponível (sem rede)")

    monkeypatch.setattr(embeddings_module, "SentenceTransformer", _BoomSentenceTransformer)
    monkeypatch.setattr(embeddings_module, "_get_device", lambda: "cpu")

    with pytest.raises(RuntimeError, match="Falha ao carregar embedding model"):
        embeddings_module._load_model()
