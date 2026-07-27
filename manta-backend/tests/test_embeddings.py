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


def test_get_device_returns_a_valid_device_string():
    """Chamada direta (sem mock) — `_get_device` só decide entre
    cuda/mps/cpu consultando `torch`, nunca baixa nem carrega nada, então
    é seguro rodar de verdade neste ambiente (CPU-only) para cobrir seu
    corpo por completo."""
    device = embeddings_module._get_device()
    assert device in ("cuda", "mps", "cpu")


def test_load_model_success_path_builds_and_caches_singleton(monkeypatch):
    """Cobre o caminho feliz de `_load_model` (linha `_model =
    SentenceTransformer(...)` incluída) sem baixar o modelo real —
    troca a CLASSE `SentenceTransformer` por um dublê leve que só
    precisa aceitar `(model_name, device=...)`."""
    monkeypatch.setattr(embeddings_module, "_model", None)
    monkeypatch.setattr(embeddings_module, "_model_device", None)

    class _FakeConstructedSentenceTransformer:
        def __init__(self, model_name, device=None):
            self.model_name = model_name
            self.device = device

    monkeypatch.setattr(embeddings_module, "SentenceTransformer", _FakeConstructedSentenceTransformer)

    loaded = embeddings_module._load_model()

    assert isinstance(loaded, _FakeConstructedSentenceTransformer)
    assert loaded.model_name == EMBEDDING_MODEL_NAME
    assert embeddings_module._model is loaded  # singleton cacheado


async def test_embed_text_wraps_encode_failures_in_runtime_error(monkeypatch):
    class _BoomOnEncode:
        def encode(self, *args, **kwargs):
            raise RuntimeError("falha simulada no encode")

    monkeypatch.setattr(embeddings_module, "_model", _BoomOnEncode())

    with pytest.raises(RuntimeError, match="Falha ao gerar embedding"):
        await embed_text("texto qualquer")


async def test_embed_texts_wraps_encode_failures_in_runtime_error(monkeypatch):
    class _BoomOnEncode:
        def encode(self, *args, **kwargs):
            raise RuntimeError("falha simulada no encode em lote")

    monkeypatch.setattr(embeddings_module, "_model", _BoomOnEncode())

    with pytest.raises(RuntimeError, match="Falha ao gerar embeddings em batch"):
        await embed_texts(["texto 1", "texto 2"])


def test_load_model_wraps_failures_in_runtime_error(monkeypatch):
    monkeypatch.setattr(embeddings_module, "_model", None)

    class _BoomSentenceTransformer:
        def __init__(self, *args, **kwargs):
            raise OSError("modelo indisponível (sem rede)")

    monkeypatch.setattr(embeddings_module, "SentenceTransformer", _BoomSentenceTransformer)
    monkeypatch.setattr(embeddings_module, "_get_device", lambda: "cpu")

    with pytest.raises(RuntimeError, match="Falha ao carregar embedding model"):
        embeddings_module._load_model()


# ---------------------------------------------------------------------------
# Similaridade de cosseno — shape (norma L2) e comportamento da métrica.
#
# `_FakeSentenceTransformer` (acima) gera um vetor pseudo-aleatório por
# texto (via hash) — ótimo para testar shape/determinismo/ordem, mas sem
# nenhuma relação semântica real entre textos parecidos. Para testar a
# MÉTRICA de similaridade (não só o shape do vetor), usamos aqui um
# segundo dublê — `_WordOverlapEncoder` — que constrói vetores bag-of-
# words determinísticos: textos que compartilham palavras ficam com
# cosine similarity alta; textos sem nenhuma palavra em comum ficam
# próximos de zero. Continua 100% offline/determinístico, só isola uma
# propriedade diferente do contrato (similaridade, não só dimensão).
# ---------------------------------------------------------------------------


def _cosine_similarity(a, b) -> float:
    a_arr = np.asarray(a, dtype=np.float64)
    b_arr = np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


class _WordOverlapEncoder:
    """Dublê determinístico bag-of-words: cosine similarity alta para
    textos com palavras em comum, baixa para textos sem overlap nenhum."""

    def _vector_for(self, text: str) -> np.ndarray:
        vec = np.zeros(EMBEDDING_DIMENSIONS, dtype=np.float64)
        for word in text.lower().split():
            idx = abs(hash(word)) % EMBEDDING_DIMENSIONS
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

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
        vectors = [self._vector_for(t) for t in inputs]
        result = np.stack(vectors)
        return result if is_batch else result[0]


async def test_embed_text_vectors_are_l2_normalized():
    """normalize_embeddings=True (ml/embeddings.py) — todo vetor não-vazio
    tem que ter norma L2 ~= 1.0, senão cosine similarity != dot product."""
    vector = await embed_text("saneamento e drenagem urbana")
    norm = float(np.linalg.norm(np.asarray(vector)))
    assert norm == pytest.approx(1.0, abs=1e-5)


async def test_cosine_similarity_of_identical_text_with_itself_is_one():
    vector = await embed_text("edital ANEEL de transmissão")
    similarity = _cosine_similarity(vector, vector)
    assert similarity == pytest.approx(1.0, abs=1e-6)


async def test_cosine_similarity_of_near_duplicate_text_is_very_high():
    """Mesmo texto com espaçamento/whitespace diferente é normalizado
    (strip) antes de embarcar — o vetor resultante é idêntico, então a
    similaridade tem que ser exatamente 1.0, não só 'alta'."""
    v1 = await embed_text("aeroporto")
    v2 = await embed_text("  aeroporto  ")
    assert _cosine_similarity(v1, v2) == pytest.approx(1.0, abs=1e-6)


def test_cosine_similarity_is_higher_for_texts_sharing_vocabulary(monkeypatch):
    """Com um encoder cuja similaridade É semanticamente significativa
    (bag-of-words), dois textos que compartilham palavras-chave de
    domínio devem ficar mais próximos entre si do que qualquer um deles
    fica de um texto de domínio totalmente diferente."""
    monkeypatch.setattr(embeddings_module, "_model", _WordOverlapEncoder())

    saneamento_a = np.asarray(_WordOverlapEncoder()._vector_for("saneamento adutora esgoto tratamento"))
    saneamento_b = np.asarray(_WordOverlapEncoder()._vector_for("saneamento drenagem urbana SNIS"))
    barragem = np.asarray(_WordOverlapEncoder()._vector_for("barragem vertedouro CFRD rejeitos"))

    sim_related = _cosine_similarity(saneamento_a, saneamento_b)
    sim_unrelated = _cosine_similarity(saneamento_a, barragem)

    assert sim_related > sim_unrelated
    assert sim_unrelated == pytest.approx(0.0, abs=1e-9)  # nenhuma palavra em comum


async def test_cosine_similarity_is_higher_for_texts_sharing_vocabulary_via_embed_text(monkeypatch):
    """Mesma asserção acima, mas passando pelo contrato público
    embed_text (não só o encoder cru) — garante que embed_text não
    introduz nenhuma distorção (ex.: normalização extra) que quebre a
    ordenação relativa de similaridade."""
    monkeypatch.setattr(embeddings_module, "_model", _WordOverlapEncoder())

    v_saneamento_a = await embed_text("saneamento adutora esgoto tratamento")
    v_saneamento_b = await embed_text("saneamento drenagem urbana SNIS")
    v_barragem = await embed_text("barragem vertedouro CFRD rejeitos")

    sim_related = _cosine_similarity(v_saneamento_a, v_saneamento_b)
    sim_unrelated = _cosine_similarity(v_saneamento_a, v_barragem)

    assert sim_related > sim_unrelated


def test_cosine_similarity_is_bounded_between_zero_and_one_for_nonnegative_vectors():
    """Vetores bag-of-words têm contagens >= 0, então o cosseno entre
    dois deles nunca é negativo (e nunca excede 1, por Cauchy-Schwarz)."""
    encoder = _WordOverlapEncoder()
    pairs = [
        ("porto e dragagem", "aeroporto e pista"),
        ("metro e NATM", "ferrovia e trilho"),
        ("barragem e CFRD", "barragem e CFRD"),
    ]
    for text_a, text_b in pairs:
        sim = _cosine_similarity(encoder._vector_for(text_a), encoder._vector_for(text_b))
        assert -1e-9 <= sim <= 1.0 + 1e-9


async def test_embed_texts_similarity_matrix_diagonal_is_self_similarity():
    """Constrói a matriz de similaridade par-a-par de um pequeno batch e
    confirma shape (NxN), simetria e diagonal == 1.0 (cada texto é
    perfeitamente similar a si mesmo)."""
    texts = ["rodovia e pavimento", "ferrovia e trilho", "metrô e NATM"]
    vectors = await embed_texts(texts)

    n = len(texts)
    matrix = [[_cosine_similarity(vectors[i], vectors[j]) for j in range(n)] for i in range(n)]

    assert len(matrix) == n and all(len(row) == n for row in matrix)
    for i in range(n):
        assert matrix[i][i] == pytest.approx(1.0, abs=1e-6)
    for i in range(n):
        for j in range(n):
            assert matrix[i][j] == pytest.approx(matrix[j][i], abs=1e-9)  # simetria
