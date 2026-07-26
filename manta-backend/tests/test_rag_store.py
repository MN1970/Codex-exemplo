"""
tests/test_rag_store.py — Suíte de INTEGRAÇÃO de `rag_store.py` (RagChunk
+ pgvector) contra um Postgres real com a extensão `vector` instalada.

Roda contra `RAG_STORE_TEST_DATABASE_URL` (default: banco local
`manta_test`, criado especificamente para esta suíte — ver setup em
`scripts/init.sql`/README para o equivalente de produção). Se o banco
não estiver acessível, os testes são pulados (`pytest.skip`) em vez de
falhar — mesma filosofia de degradação usada pelo app em produção
(`pg_pool.create_pool`/`acquire_optional`).

`ml.embeddings.embed_text` é mockado com um embedding determinístico
por palavra-chave (ver `_fake_embed_text`): isso deixa o teste
independente de rede/GPU/pesos do Sentence Transformers, mas ainda
exercita o caminho real de ponta a ponta — INSERT de um vetor pgvector
de verdade, índice ivfflat, operador `<=>` de distância de cosseno via
SQLAlchemy (`Vector.cosine_distance`) — que é exatamente o que
`ml/embeddings.py` real precisa produzir (mesma dimensão, mesmo shape).

RLS (`alembic/versions/0003_rls_policies.py`) não é aplicada neste
schema de teste (criado via `Base.metadata.create_all`, que só cria
tabelas/índices, não policies) — o isolamento por organização testado
aqui é o de `rag_store.search_similar` (filtro `WHERE org_id = ...` na
query da aplicação), a segunda camada de isolamento que já funciona
independente da RLS do banco.
"""
from __future__ import annotations

import os
import uuid

import numpy as np
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import rag_store
from database import Base, EMBEDDING_DIM, Organization, RagChunk

TEST_DATABASE_URL = os.environ.get(
    "RAG_STORE_TEST_DATABASE_URL",
    "postgresql+asyncpg://manta_test:manta_test@localhost:5432/manta_test",
)

# Vocabulário usado pelo embedding falso — cada termo vira uma dimensão
# "ativada" (one-hot-ish); textos com termos em comum ficam próximos no
# espaço de cosseno, textos sem termos em comum ficam ortogonais. Isso
# torna a ordenação de `search_similar` 100% previsível no teste, sem
# precisar rodar o modelo real.
_TOPIC_TERMS = ["saneamento", "energia", "portos", "aeroportos", "barragens"]


async def _fake_embed_text(text_in: str) -> list[float]:
    vec = np.zeros(EMBEDDING_DIM, dtype=float)
    lowered = text_in.lower()
    for i, term in enumerate(_TOPIC_TERMS):
        if term in lowered:
            vec[i] = 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


@pytest.fixture(autouse=True)
def _mock_embeddings(monkeypatch):
    # rag_store.py faz `from ml.embeddings import embed_text` — o nome
    # vive no namespace de rag_store, então é isso que precisa ser
    # substituído (patchear ml.embeddings.embed_text não afetaria a
    # referência já importada em rag_store).
    monkeypatch.setattr(rag_store, "embed_text", _fake_embed_text)


@pytest_asyncio.fixture(scope="module")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, future=True)
    try:
        async with eng.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        await eng.dispose()
        pytest.skip(
            f"Postgres de teste indisponível em {TEST_DATABASE_URL} ({exc}). "
            "Suba um Postgres com pgvector e exporte RAG_STORE_TEST_DATABASE_URL "
            "para rodar esta suíte de integração."
        )
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _schema(engine):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session(session_factory):
    async with session_factory() as session:
        yield session
        await session.rollback()


async def _make_org(session: AsyncSession, slug_prefix: str) -> Organization:
    org = Organization(name=f"Org {slug_prefix}", slug=f"{slug_prefix}-{uuid.uuid4().hex[:8]}")
    session.add(org)
    await session.flush()
    return org


# ---------------------------------------------------------------------------
# create_rag_chunk
# ---------------------------------------------------------------------------
async def test_create_rag_chunk_persists_with_real_pgvector_embedding(db_session):
    org = await _make_org(db_session, "create")

    chunk = await rag_store.create_rag_chunk(
        db_session,
        org_id=org.id,
        collection="saneamento",
        prefix="san:",
        content="Estudo de saneamento básico e drenagem urbana em São Paulo.",
    )
    await db_session.flush()

    assert chunk.id is not None
    assert chunk.org_id == org.id
    assert chunk.collection == "saneamento"
    assert chunk.embedding is not None
    assert len(chunk.embedding) == EMBEDDING_DIM
    assert any(v != 0.0 for v in chunk.embedding)


async def test_create_rag_chunk_rejects_empty_content(db_session):
    org = await _make_org(db_session, "empty")

    with pytest.raises(ValueError):
        await rag_store.create_rag_chunk(
            db_session, org_id=org.id, collection="saneamento", prefix="san:", content="   "
        )


async def test_create_rag_chunk_defaults_meta_to_empty_dict(db_session):
    org = await _make_org(db_session, "meta")

    chunk = await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="energia", prefix="ene:", content="Leilão de transmissão ANEEL."
    )
    assert chunk.meta == {}


# ---------------------------------------------------------------------------
# search_similar
# ---------------------------------------------------------------------------
async def test_search_similar_ranks_matching_topic_first(db_session):
    org = await _make_org(db_session, "search")

    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="saneamento", prefix="san:",
        content="Plano de saneamento básico e adutoras da região metropolitana.",
    )
    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="energia", prefix="ene:",
        content="Leilão de transmissão de energia elétrica e subestações.",
    )
    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="portos", prefix="por:",
        content="Dragagem e berços de atracação no porto de Santos.",
    )
    await db_session.flush()

    results = await rag_store.search_similar(db_session, org_id=org.id, query="saneamento", top_k=3)

    assert len(results) == 3
    assert results[0].chunk.collection == "saneamento"
    # Ordenado por similaridade decrescente.
    assert results[0].score >= results[1].score >= results[2].score
    # O match exato deve ficar bem próximo de 1.0 (mesma direção, normalizado).
    assert results[0].score == pytest.approx(1.0, abs=1e-6)


async def test_search_similar_respects_collection_filter(db_session):
    org = await _make_org(db_session, "filter")

    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="saneamento", prefix="san:", content="saneamento e energia combinados",
    )
    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="energia", prefix="ene:", content="saneamento e energia combinados",
    )
    await db_session.flush()

    results = await rag_store.search_similar(
        db_session, org_id=org.id, query="energia", top_k=10, collection="energia"
    )

    assert len(results) == 1
    assert results[0].chunk.collection == "energia"


async def test_search_similar_respects_top_k(db_session):
    org = await _make_org(db_session, "topk")

    for i in range(5):
        await rag_store.create_rag_chunk(
            db_session, org_id=org.id, collection="barragens", prefix="bar:", content=f"barragem número {i}",
        )
    await db_session.flush()

    results = await rag_store.search_similar(db_session, org_id=org.id, query="barragens", top_k=2)
    assert len(results) == 2


async def test_search_similar_rejects_non_positive_top_k(db_session):
    org = await _make_org(db_session, "badtopk")
    with pytest.raises(ValueError):
        await rag_store.search_similar(db_session, org_id=org.id, query="x", top_k=0)


async def test_search_similar_is_isolated_by_org_id(db_session):
    org_a = await _make_org(db_session, "orga")
    org_b = await _make_org(db_session, "orgb")

    await rag_store.create_rag_chunk(
        db_session, org_id=org_a.id, collection="aeroportos", prefix="aer:", content="aeroportos org A",
    )
    await rag_store.create_rag_chunk(
        db_session, org_id=org_b.id, collection="aeroportos", prefix="aer:", content="aeroportos org B",
    )
    await db_session.flush()

    results_a = await rag_store.search_similar(db_session, org_id=org_a.id, query="aeroportos", top_k=10)

    assert len(results_a) == 1
    assert results_a[0].chunk.org_id == org_a.id
    assert "org A" in results_a[0].chunk.content


async def test_search_similar_excludes_chunks_without_embedding(db_session):
    org = await _make_org(db_session, "noembed")

    # Chunk sem embedding (ainda não processado por tasks/embed_rag_chunks.py)
    # inserido diretamente via ORM, sem passar por create_rag_chunk.
    pending_chunk = RagChunk(
        org_id=org.id, collection="portos", prefix="por:", content="porto pendente de embarque", embedding=None,
    )
    db_session.add(pending_chunk)

    await rag_store.create_rag_chunk(
        db_session, org_id=org.id, collection="portos", prefix="por:", content="porto já embarcado",
    )
    await db_session.flush()

    results = await rag_store.search_similar(db_session, org_id=org.id, query="portos", top_k=10)

    assert len(results) == 1
    assert results[0].chunk.content == "porto já embarcado"
