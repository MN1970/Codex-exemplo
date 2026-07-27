"""
tests/test_rag_search_endpoint.py — Suíte de INTEGRAÇÃO de `POST /rag/search`
(routers/rag.py) contra um Postgres real com pgvector — o schema legado
de `scripts/init.sql` (pool asyncpg cru, sem org_id/RLS), que é o que o
Knowledge Hub (RAGSearch.tsx/KnowledgeHub.tsx) efetivamente usa em
produção.

Roda contra `RAG_SEARCH_TEST_DATABASE_URL` (default: banco local
`manta_test_legacy`). Se indisponível, os testes são pulados — mesma
filosofia de degradação de `pg_pool.create_pool`.

`ml.embeddings.embed_text` é mockado (determinístico por palavra-chave,
mesma técnica de tests/test_rag_store.py) para não depender de
rede/GPU — mas o INSERT/SELECT contra a coluna `vector(384)` real e o
operador de distância de cosseno `<=>` do pgvector rodam de verdade.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import asyncpg
import httpx
import numpy as np
import pytest
import pytest_asyncio
from fastapi import FastAPI

import routers.rag as rag_router_module
from routers.rag import router as rag_router

TEST_DATABASE_URL = os.environ.get(
    "RAG_SEARCH_TEST_DATABASE_URL",
    "postgresql://manta_test:manta_test@localhost:5432/manta_test_legacy",
)

_TOPIC_TERMS = ["saneamento", "energia", "portos", "aeroportos", "barragens"]
_EMBEDDING_DIM = 384

_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_documents (
    id           UUID PRIMARY KEY,
    collection   TEXT NOT NULL,
    title        TEXT NOT NULL,
    filename     TEXT NOT NULL,
    file_type    TEXT NOT NULL DEFAULT '',
    source       TEXT NOT NULL DEFAULT 'upload',
    size_bytes   BIGINT NOT NULL DEFAULT 0,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_chunks (
    id          BIGSERIAL PRIMARY KEY,
    collection  TEXT NOT NULL,
    prefix      TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384),
    document_id UUID REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def _fake_vector(text_in: str) -> list[float]:
    vec = np.zeros(_EMBEDDING_DIM, dtype=float)
    lowered = text_in.lower()
    for i, term in enumerate(_TOPIC_TERMS):
        if term in lowered:
            vec[i] = 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


async def _fake_embed_text(text_in: str) -> list[float]:
    return _fake_vector(text_in)


@pytest.fixture(autouse=True)
def _mock_embeddings(monkeypatch):
    # routers/rag.py faz `from ml.embeddings import embed_text` — precisa
    # patchear o nome já importado no módulo do router, não em ml.embeddings.
    monkeypatch.setattr(rag_router_module, "embed_text", _fake_embed_text)


@pytest_asyncio.fixture
async def pool():
    """Pool asyncpg criado e fechado DENTRO do mesmo teste (função).
    asyncpg prende conexões ao event loop em que foram criadas —
    pytest-asyncio (modo `auto`) cria um event loop novo por função de
    teste, então um pool com escopo "module" sobrevive ao loop que o
    criou e quebra no teste seguinte com erros de "event loop is
    closed"/"another operation is in progress". Recriar o pool (e
    truncar as tabelas) a cada teste é o preço de manter cada teste
    isolado no seu próprio loop."""
    try:
        db_pool = await asyncpg.create_pool(dsn=TEST_DATABASE_URL, min_size=1, max_size=4)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(
            f"Postgres de teste indisponível em {TEST_DATABASE_URL} ({exc}). "
            "Suba um Postgres com pgvector e exporte RAG_SEARCH_TEST_DATABASE_URL "
            "para rodar esta suíte de integração."
        )
        return
    async with db_pool.acquire() as conn:
        await conn.execute(_SCHEMA_SQL)
        await conn.execute("TRUNCATE rag_chunks, rag_documents RESTART IDENTITY CASCADE")
    yield db_pool
    await db_pool.close()


@pytest.fixture
def test_app(pool) -> FastAPI:
    app = FastAPI()
    app.include_router(rag_router)
    app.state.db_pool = pool
    return app


@pytest_asyncio.fixture
async def client(test_app: FastAPI):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


async def _insert_chunk(pool: asyncpg.Pool, *, collection: str, prefix: str, content: str) -> int:
    literal = "[" + ",".join(repr(float(x)) for x in _fake_vector(content)) + "]"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO rag_chunks (collection, prefix, content, embedding)
            VALUES ($1, $2, $3, $4::vector)
            RETURNING id
            """,
            collection,
            prefix,
            content,
            literal,
        )
    return row["id"]


# ---------------------------------------------------------------------------
# POST /rag/search
# ---------------------------------------------------------------------------
async def test_search_ranks_matching_collection_first(client: httpx.AsyncClient, pool: asyncpg.Pool):
    await _insert_chunk(pool, collection="saneamento", prefix="san:", content="Plano de saneamento básico e adutoras.")
    await _insert_chunk(pool, collection="energia", prefix="ene:", content="Leilão de transmissão de energia elétrica.")
    await _insert_chunk(pool, collection="portos", prefix="por:", content="Dragagem em portos como o de Santos.")

    resp = await client.post("/rag/search", json={"query": "saneamento", "top_k": 3})

    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 3
    assert results[0]["agent"] == "saneamento"
    assert results[0]["score"] == pytest.approx(1.0, abs=1e-6)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


async def test_search_filters_by_collection(client: httpx.AsyncClient, pool: asyncpg.Pool):
    await _insert_chunk(pool, collection="saneamento", prefix="san:", content="saneamento e energia combinados")
    await _insert_chunk(pool, collection="energia", prefix="ene:", content="saneamento e energia combinados")

    resp = await client.post("/rag/search", json={"query": "energia", "collection": "energia", "top_k": 10})

    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["agent"] == "energia"


async def test_search_unknown_collection_returns_404(client: httpx.AsyncClient):
    resp = await client.post("/rag/search", json={"query": "x", "collection": "nao-existe"})
    assert resp.status_code == 404


async def test_search_respects_top_k(client: httpx.AsyncClient, pool: asyncpg.Pool):
    for i in range(5):
        await _insert_chunk(pool, collection="barragens", prefix="bar:", content=f"barragens, projeto número {i}")

    resp = await client.post("/rag/search", json={"query": "barragens", "top_k": 2})

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_search_response_includes_document_metadata(client: httpx.AsyncClient, pool: asyncpg.Pool):
    doc_id = str(uuid.uuid4())
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO rag_documents (id, collection, title, filename, file_type, size_bytes, chunk_count, created_at)
            VALUES ($1, 'aeroportos', 'Edital ANAC', 'edital.pdf', 'pdf', 1024, 1, $2)
            """,
            doc_id,
            datetime.now(timezone.utc),
        )
        literal = "[" + ",".join(repr(float(x)) for x in _fake_vector("aeroportos pista de pouso ICAO")) + "]"
        await conn.execute(
            """
            INSERT INTO rag_chunks (collection, prefix, content, embedding, document_id, chunk_index)
            VALUES ('aeroportos', 'aer:', 'aeroportos pista de pouso ICAO', $1::vector, $2, 0)
            """,
            literal,
            doc_id,
        )

    resp = await client.post("/rag/search", json={"query": "aeroportos", "top_k": 5})

    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Edital ANAC"
    assert results[0]["document_id"] == doc_id
    assert results[0]["source"] == "edital.pdf"
    assert results[0]["file_type"] == "pdf"


async def test_search_degrades_to_503_without_db_pool():
    app = FastAPI()
    app.include_router(rag_router)
    app.state.db_pool = None

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post("/rag/search", json={"query": "saneamento"})

    assert resp.status_code == 503
