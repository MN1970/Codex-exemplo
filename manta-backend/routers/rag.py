"""
routers/rag.py — Coleções RAG (Supabase pgvector), conforme tabela
"RAG — Coleções em Supabase" do CLAUDE.md master.

Query real usa pgvector (`<->` operador de distância) contra a tabela
`rag_chunks(collection, prefix, content, embedding vector(N))`. Se o
banco não estiver disponível, o endpoint degrada para 503 em vez de
derrubar a app — ver database.acquire_optional.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from pg_pool import acquire_optional
from fastapi import Request
from ml.embeddings import embed_text

router = APIRouter(prefix="/rag", tags=["rag"])


class Collection(BaseModel):
    name: str
    storage_prefix: str
    sources: str
    status: str


COLLECTIONS: List[Collection] = [
    Collection(name="saneamento", storage_prefix="san:", sources="SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES", status="v4.2"),
    Collection(name="energia", storage_prefix="ene:", sources="ANEEL editais, R1-R5 EPE, ONS, IEEE", status="v4.2"),
    Collection(name="portos", storage_prefix="por:", sources="ANTAQ, PIANC, editais BNDES/ANTAQ", status="v4.2"),
    Collection(name="aeroportos", storage_prefix="aer:", sources="ANAC/RBAC, ICAO Annex 14, FAA ACs", status="v4.2"),
    Collection(name="barragens", storage_prefix="bar:", sources="ICOLD, CBDB, SIGBM, Lei 12.334", status="v4.2"),
]


class QueryRequest(BaseModel):
    collection: str
    query: str
    top_k: int = 5


class QueryMatch(BaseModel):
    content: str
    score: float


class QueryResponse(BaseModel):
    collection: str
    matches: List[QueryMatch]


@router.get("/collections", response_model=List[Collection], summary="Lista coleções RAG disponíveis")
async def list_collections() -> List[Collection]:
    return COLLECTIONS


@router.post("/query", response_model=QueryResponse, summary="Busca semântica (pgvector) numa coleção")
async def query_collection(payload: QueryRequest, request: Request) -> QueryResponse:
    if payload.collection not in {c.name for c in COLLECTIONS}:
        raise HTTPException(status_code=404, detail=f"Coleção '{payload.collection}' não existe.")

    embedding = await embed_text(payload.query)

    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG (Supabase/pgvector) indisponível no momento.",
            )
        rows = await conn.fetch(
            """
            SELECT content, 1 - (embedding <=> $1::vector) AS score
            FROM rag_chunks
            WHERE collection = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
            """,
            embedding,
            payload.collection,
            payload.top_k,
        )
        matches = [QueryMatch(content=r["content"], score=float(r["score"])) for r in rows]

    return QueryResponse(collection=payload.collection, matches=matches)
