"""
rag_store.py — Camada de integração RAG (RagChunk + pgvector) sobre o
ORM canônico de `database.py`.

Complementa `routers/rag.py` (que fala com o pool asyncpg cru contra o
schema legado de `scripts/init.sql`): aqui a persistência e a busca por
similaridade rodam contra o schema versionado por Alembic
(`organizations`/`agents`/`rag_chunks`, com RLS multi-org — ver
`alembic/versions/0003_rls_policies.py`).

Duas funções:

  - `create_rag_chunk(...)`   — computa o embedding do conteúdo
    (`ml.embeddings.embed_text`) e insere um `RagChunk`.
  - `search_similar(...)`     — computa o embedding da query e devolve
    os `RagChunk` mais próximos por similaridade de cosseno (pgvector
    `<=>`, exposto pelo SQLAlchemy via `Vector.cosine_distance`).

As duas assumem que a `AsyncSession` recebida já está com o contexto de
RLS setado para a organização certa (ver `database.get_org_scoped_session`
/ `database.set_org_context`) — filtramos por `org_id` explicitamente
também na query da aplicação, como segunda camada de isolamento (não só
confiar na RLS do banco).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import RagChunk
from ml.embeddings import embed_text


async def create_rag_chunk(
    session: AsyncSession,
    *,
    org_id: str,
    collection: str,
    prefix: str,
    content: str,
    agent_id: Optional[str] = None,
    meta: Optional[dict] = None,
) -> RagChunk:
    """Computa o embedding do conteúdo e persiste um `RagChunk`.

    Args:
        session: sessão SQLAlchemy já com o contexto RLS setado (ver
            `database.get_org_scoped_session(org_id)`).
        org_id: organização dona do chunk (grava na coluna `org_id`;
            precisa bater com o contexto RLS da sessão, senão o INSERT
            é rejeitado pela policy `rag_chunks_org_isolation`).
        collection: coleção RAG (ex.: "saneamento", "energia").
        prefix: prefixo de storage da coleção (ex.: "san:").
        content: texto do chunk — vira o embedding via `embed_text`.
        agent_id: agente vertical dono do chunk, se aplicável.
        meta: metadados livres (JSONB) — default `{}`.

    Returns:
        O `RagChunk` já persistido (com `id`/`created_at` preenchidos
        após o flush).

    Raises:
        ValueError: se `content` for vazio/whitespace.
    """
    if not content or not content.strip():
        raise ValueError("content não pode ser vazio")

    embedding = await embed_text(content)

    chunk = RagChunk(
        org_id=org_id,
        agent_id=agent_id,
        collection=collection,
        prefix=prefix,
        content=content,
        embedding=embedding,
        meta=meta or {},
    )
    session.add(chunk)
    await session.flush()
    return chunk


@dataclass
class SimilarChunk:
    """Resultado de `search_similar`: o chunk + o score de similaridade
    (cosine similarity, não distância — 1.0 = idêntico, 0.0 = ortogonal,
    negativo = oposto)."""

    chunk: RagChunk
    score: float


async def search_similar(
    session: AsyncSession,
    *,
    org_id: str,
    query: str,
    top_k: int = 5,
    collection: Optional[str] = None,
) -> list[SimilarChunk]:
    """Busca os `top_k` chunks mais similares à `query` (embedding +
    cosine similarity via pgvector).

    Args:
        session: sessão SQLAlchemy já com o contexto RLS setado.
        org_id: escopo de organização (aplicado também na query, além
            da RLS do banco — isolamento em duas camadas).
        query: texto de busca — vira o embedding via `embed_text`.
        top_k: número máximo de resultados (deve ser >= 1).
        collection: filtra por coleção RAG; `None` busca em todas as
            coleções da organização.

    Returns:
        Lista de `SimilarChunk` ordenada por similaridade decrescente
        (mais similar primeiro), tamanho <= top_k. Chunks sem embedding
        (`embedding IS NULL`, ainda não processados por
        `tasks/embed_rag_chunks.py`) são excluídos do resultado.

    Raises:
        ValueError: se `top_k` for < 1.
    """
    if top_k < 1:
        raise ValueError("top_k deve ser >= 1")

    query_embedding = await embed_text(query)
    distance = RagChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(RagChunk, distance.label("distance"))
        .where(RagChunk.org_id == org_id)
        .where(RagChunk.embedding.is_not(None))
    )
    if collection is not None:
        stmt = stmt.where(RagChunk.collection == collection)
    stmt = stmt.order_by(distance).limit(top_k)

    result = await session.execute(stmt)
    return [
        SimilarChunk(chunk=chunk, score=1.0 - float(dist))
        for chunk, dist in result.all()
    ]
