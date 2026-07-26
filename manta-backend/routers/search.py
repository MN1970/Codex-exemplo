"""
routers/search.py — Busca semântica otimizada com pgvector.

Exporta endpoints para busca semântica em tempo real:
  - GET /search?q=query&limit=10&collection=... — busca rápida (cards)
  - GET /search/related/{chunk_id} — chunks similares a um dado chunk

Diferença com rag.py:
  - rag.py: foco em upload/gerenciamento de documentos (POST/DELETE)
  - search.py: foco em busca otimizada (GET) com cache de embeddings
"""
from __future__ import annotations

import logging
from typing import List, Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from pg_pool import acquire_optional
from ml.embeddings import embed_text

logger = logging.getLogger("manta.search")

router = APIRouter(prefix="/search", tags=["search"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SearchHit(BaseModel):
    """Um resultado de busca semântica."""

    chunk_id: int
    content: str
    score: float = Field(description="Score de similaridade (0-1)")
    document_id: Optional[str] = None
    document_title: Optional[str] = None
    document_filename: Optional[str] = None
    file_type: Optional[str] = None
    collection: str


class SearchResponse(BaseModel):
    """Resposta da busca semântica."""

    query: str
    collection: Optional[str] = Field(
        default=None,
        description="Coleção filtrada (se especificada)",
    )
    total_hits: int
    results: List[SearchHit]
    took_ms: int = Field(description="Tempo de execução em milisegundos")


# ---------------------------------------------------------------------------
# Validação de collection
# ---------------------------------------------------------------------------
VALID_COLLECTIONS = {"saneamento", "energia", "portos", "aeroportos", "barragens"}


def _validate_collection(collection: Optional[str]) -> Optional[str]:
    """Valida e normaliza o nome da coleção. Retorna None se 'all'/vazio."""
    if not collection or collection.lower() in ("all", "todos", ""):
        return None
    if collection.lower() not in VALID_COLLECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coleção inválida '{collection}'. Válidas: {sorted(VALID_COLLECTIONS)}",
        )
    return collection.lower()


# ---------------------------------------------------------------------------
# Busca semântica (endpoint principal)
# ---------------------------------------------------------------------------
@router.get("", response_model=SearchResponse, summary="Busca semântica em chunks RAG")
async def semantic_search(
    request: Request,
    q: str = Query(..., min_length=1, description="Texto de busca"),
    limit: int = Query(10, ge=1, le=100, description="Máximo de resultados"),
    collection: Optional[str] = Query(
        None,
        description="Filtra por coleção (ex.: 'saneamento', 'energia'). Omitido = todas.",
    ),
) -> SearchResponse:
    """Busca semântica otimizada em chunks RAG via pgvector.

    Algoritmo:
    1. Embarcar query com Sentence Transformers
    2. Buscar top-N chunks mais similares via operador pgvector <=>
    3. Retornar resultados com score de similaridade (0-1)

    Score = 1 - (distância euclidiana do embedding)
    """
    import time

    start_time = time.perf_counter()

    # Validar collection
    validated_collection = _validate_collection(collection)

    # Embarcar query
    try:
        query_embedding = await embed_text(q)
    except Exception as e:
        logger.exception("search: falha ao embarcar query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao processar busca: {e}",
        ) from e

    # Buscar chunks similares
    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG indisponível no momento.",
            )

        rows = await conn.fetch(
            """
            SELECT
                c.id,
                c.content,
                c.collection,
                c.document_id,
                d.title AS document_title,
                d.filename AS document_filename,
                d.file_type,
                1 - (c.embedding <=> $1::vector) AS score
            FROM rag_chunks c
            LEFT JOIN rag_documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
              AND ($2::text IS NULL OR c.collection = $2)
            ORDER BY c.embedding <=> $1::vector
            LIMIT $3
            """,
            query_embedding,
            validated_collection,
            limit,
        )

    end_time = time.perf_counter()
    took_ms = int((end_time - start_time) * 1000)

    results = [
        SearchHit(
            chunk_id=r["id"],
            content=r["content"] or "",
            score=float(r["score"]) if r["score"] is not None else 0.0,
            document_id=str(r["document_id"]) if r["document_id"] else None,
            document_title=r["document_title"],
            document_filename=r["document_filename"],
            file_type=r["file_type"],
            collection=r["collection"],
        )
        for r in rows
    ]

    return SearchResponse(
        query=q,
        collection=validated_collection,
        total_hits=len(results),
        results=results,
        took_ms=took_ms,
    )


# ---------------------------------------------------------------------------
# Chunks similares (encontrar documentos relacionados)
# ---------------------------------------------------------------------------
class RelatedChunk(BaseModel):
    """Chunk relacionado a um chunk de origem."""

    chunk_id: int
    content: str
    score: float
    document_title: Optional[str]
    distance: float = Field(description="Distância euclidiana (raw, não normalizada)")


@router.get(
    "/related/{chunk_id}",
    response_model=List[RelatedChunk],
    summary="Encontra chunks similares a um chunk específico",
)
async def find_related_chunks(
    request: Request,
    chunk_id: int,
    limit: int = Query(5, ge=1, le=50),
) -> List[RelatedChunk]:
    """Encontra chunks com embedding similar ao de um chunk dado
    (útil para "documentos relacionados").

    Algoritmo:
    1. Buscar embedding do chunk_id
    2. Encontrar top-limit chunks com embedding mais similar
    3. Excluir o próprio chunk da resposta
    """
    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG indisponível.",
            )

        # Buscar embedding do chunk original
        source_row = await conn.fetchrow(
            "SELECT embedding FROM rag_chunks WHERE id = $1", chunk_id
        )
        if not source_row or source_row["embedding"] is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk {chunk_id} não encontrado ou sem embedding.",
            )

        source_embedding = source_row["embedding"]

        # Encontrar similares (excluindo a origem)
        rows = await conn.fetch(
            """
            SELECT
                c.id,
                c.content,
                c.embedding <-> $1::vector AS distance,
                1 - (c.embedding <=> $1::vector) AS score,
                d.title AS document_title
            FROM rag_chunks c
            LEFT JOIN rag_documents d ON d.id = c.document_id
            WHERE c.id != $2
              AND c.embedding IS NOT NULL
            ORDER BY c.embedding <-> $1::vector
            LIMIT $3
            """,
            source_embedding,
            chunk_id,
            limit,
        )

    return [
        RelatedChunk(
            chunk_id=r["id"],
            content=r["content"] or "",
            score=float(r["score"]) if r["score"] is not None else 0.0,
            document_title=r["document_title"],
            distance=float(r["distance"]) if r["distance"] is not None else 0.0,
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Debug endpoint
# ---------------------------------------------------------------------------
@router.get("/debug/model-info", summary="Info sobre embedding model (debug)")
async def model_info() -> dict:
    """Retorna informações sobre o modelo de embeddings em uso
    (device, dimensão, status)."""
    from ml.embeddings import get_model_info

    return get_model_info()
