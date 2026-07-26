"""
routers/rag.py — Coleções RAG (Supabase pgvector), conforme tabela
"RAG — Coleções em Supabase" do CLAUDE.md master.

Query real usa pgvector (`<->`/`<=>` operador de distância) contra a
tabela `rag_chunks(collection, prefix, content, embedding vector(N))`.
Se o banco não estiver disponível, os endpoints degradam para 503 em
vez de derrubar a app — ver database.acquire_optional.

Este módulo também expõe o Knowledge Hub: upload de documentos
(PDF/txt/md), listagem/filtro/remoção de documentos e busca semântica
"rica" (cards com título, snippet, score, agente e fonte) usada pelo
front-end em RAGSearch.tsx / KnowledgeHub.tsx.

    GET    /rag/collections        — coleções RAG disponíveis
    POST   /rag/query              — busca crua (legado, mantido p/ compat)
    POST   /rag/search             — busca semântica "rica" (cards)
    POST   /rag/upload             — upload de documento (multipart)
    GET    /rag/documents          — lista documentos (filtros agente/data/tipo)
    DELETE /rag/documents/{doc_id} — remove documento (cascade nos chunks)
"""
from __future__ import annotations

import io
import logging
import re
import uuid
from datetime import date, datetime
from typing import List, Optional

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel, Field

from pg_pool import acquire_optional
from ml.embeddings import embed_text

logger = logging.getLogger("manta.rag")

router = APIRouter(prefix="/rag", tags=["rag"])


# ---------------------------------------------------------------------------
# Coleções (agentes verticais que têm RAG dedicado)
# ---------------------------------------------------------------------------
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

_COLLECTION_NAMES = {c.name for c in COLLECTIONS}
_PREFIX_BY_COLLECTION = {c.name: c.storage_prefix for c in COLLECTIONS}


def _prefix_for(collection: str) -> str:
    return _PREFIX_BY_COLLECTION.get(collection, "gen:")


def _require_known_collection(collection: str) -> None:
    if collection not in _COLLECTION_NAMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coleção/agente '{collection}' não existe. Válidas: {sorted(_COLLECTION_NAMES)}",
        )


def _vector_literal(embedding: List[float]) -> str:
    """Serializa um embedding para o formato textual que o pgvector
    entende (ex.: "[0.1,0.2,...]"). `asyncpg` não tem um codec nativo
    para o tipo `vector` — sem isso, passar a lista Python direto como
    bind parameter falha com `DataError: expected str, got list`. O
    `::vector` no SQL faz o cast desse texto para o tipo real."""
    return "[" + ",".join(repr(float(x)) for x in embedding) + "]"


@router.get("/collections", response_model=List[Collection], summary="Lista coleções RAG disponíveis")
async def list_collections() -> List[Collection]:
    return COLLECTIONS


# ---------------------------------------------------------------------------
# Schema (rag_documents + colunas extras de rag_chunks) — best-effort no
# startup da app (ver app.py lifespan → rag.ensure_schema). Degrada para
# no-op se o pool não estiver disponível; cada operação que precisar do
# schema falha isoladamente com 503 via acquire_optional, sem derrubar
# a aplicação inteira.
# ---------------------------------------------------------------------------
_SCHEMA_SQL = """
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

CREATE INDEX IF NOT EXISTS idx_rag_documents_collection ON rag_documents (collection);
CREATE INDEX IF NOT EXISTS idx_rag_documents_created_at ON rag_documents (created_at);

ALTER TABLE rag_chunks ADD COLUMN IF NOT EXISTS document_id UUID REFERENCES rag_documents(id) ON DELETE CASCADE;
ALTER TABLE rag_chunks ADD COLUMN IF NOT EXISTS chunk_index INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_rag_chunks_document_id ON rag_chunks (document_id);
"""


async def ensure_schema(pool: asyncpg.Pool | None) -> None:
    """Cria/alinha `rag_documents` e as colunas novas de `rag_chunks`.
    Chamado uma vez no lifespan da app (best-effort, nunca derruba o
    startup — ver app.py)."""
    if pool is None:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(_SCHEMA_SQL)
        logger.info("rag: schema de documentos verificado/criado com sucesso")
    except Exception:  # noqa: BLE001 - degrada, não derruba
        logger.warning("rag: não foi possível garantir o schema de rag_documents (banco indisponível?)")


# ---------------------------------------------------------------------------
# Busca crua (legado — mantido para compatibilidade com integrações
# existentes que já chamam POST /rag/query)
# ---------------------------------------------------------------------------
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


@router.post("/query", response_model=QueryResponse, summary="Busca semântica crua (pgvector) numa coleção — legado")
async def query_collection(payload: QueryRequest, request: Request) -> QueryResponse:
    _require_known_collection(payload.collection)

    embedding = _vector_literal(await embed_text(payload.query))

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


# ---------------------------------------------------------------------------
# Busca "rica" — usada pelo RAGSearch.tsx (cards com título/snippet/score)
# ---------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(min_length=1, description="Texto de busca do usuário.")
    collection: Optional[str] = Field(
        default=None,
        description="Filtra por agente/coleção (ex.: 'saneamento'). Omitido/null busca em todas.",
    )
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    chunk_id: int
    document_id: Optional[str] = None
    title: str
    snippet: str
    score: float
    agent: str
    source: str
    file_type: Optional[str] = None
    created_at: Optional[datetime] = None


def _normalize_collection_filter(collection: Optional[str]) -> Optional[str]:
    if not collection or collection.lower() == "all" or collection.lower() == "todos":
        return None
    _require_known_collection(collection)
    return collection


def _snippet(content: str, max_len: int = 280) -> str:
    content = " ".join(content.split())
    if len(content) <= max_len:
        return content
    return content[: max_len - 1].rstrip() + "…"


@router.post("/search", response_model=List[SearchResult], summary="Busca semântica com resultados em cards (título, snippet, score, agente, fonte)")
async def search(payload: SearchRequest, request: Request) -> List[SearchResult]:
    collection = _normalize_collection_filter(payload.collection)
    embedding = _vector_literal(await embed_text(payload.query))

    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG (Supabase/pgvector) indisponível no momento.",
            )
        rows = await conn.fetch(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.content,
                c.collection,
                d.title AS doc_title,
                d.filename AS doc_filename,
                d.file_type AS doc_file_type,
                d.created_at AS doc_created_at,
                1 - (c.embedding <=> $1::vector) AS score
            FROM rag_chunks c
            LEFT JOIN rag_documents d ON d.id = c.document_id
            WHERE ($2::text IS NULL OR c.collection = $2)
            ORDER BY c.embedding <=> $1::vector
            LIMIT $3
            """,
            embedding,
            collection,
            payload.top_k,
        )

    results: List[SearchResult] = []
    for r in rows:
        content = r["content"] or ""
        title = r["doc_title"] or r["doc_filename"] or f"Chunk #{r['chunk_id']} — {r['collection']}"
        results.append(
            SearchResult(
                chunk_id=r["chunk_id"],
                document_id=str(r["document_id"]) if r["document_id"] else None,
                title=title,
                snippet=_snippet(content),
                score=float(r["score"]) if r["score"] is not None else 0.0,
                agent=r["collection"],
                source=r["doc_filename"] or "chunk manual (sem documento associado)",
                file_type=r["doc_file_type"],
                created_at=r["doc_created_at"],
            )
        )
    return results


@router.get("/chunks/{chunk_id}", response_model=SearchResult, summary="Detalhe de um chunk (para o modal ChunkViewer)")
async def get_chunk(chunk_id: int, request: Request) -> SearchResult:
    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Banco indisponível.")
        row = await conn.fetchrow(
            """
            SELECT
                c.id AS chunk_id, c.document_id, c.content, c.collection,
                d.title AS doc_title, d.filename AS doc_filename,
                d.file_type AS doc_file_type, d.created_at AS doc_created_at
            FROM rag_chunks c
            LEFT JOIN rag_documents d ON d.id = c.document_id
            WHERE c.id = $1
            """,
            chunk_id,
        )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk não encontrado.")

    title = row["doc_title"] or row["doc_filename"] or f"Chunk #{row['chunk_id']} — {row['collection']}"
    return SearchResult(
        chunk_id=row["chunk_id"],
        document_id=str(row["document_id"]) if row["document_id"] else None,
        title=title,
        snippet=row["content"] or "",
        score=1.0,
        agent=row["collection"],
        source=row["doc_filename"] or "chunk manual (sem documento associado)",
        file_type=row["doc_file_type"],
        created_at=row["doc_created_at"],
    )


# ---------------------------------------------------------------------------
# Extração de texto + chunking (upload)
# ---------------------------------------------------------------------------
def _guess_file_type(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def _sanitize_extracted_text(text: str) -> str:
    """Remove bytes NUL (Postgres/asyncpg rejeitam `\\x00` em `text` com
    `CharacterNotInRepertoireError`) e detecta lixo binário: se uma
    fração grande dos caracteres for de controle (fora de \\t\\n\\r),
    o "texto" provavelmente veio de um arquivo binário mal identificado
    como texto puro (ex.: .bin enviado sem PDF/DOCX reconhecido) —
    nesse caso devolve string vazia, e o endpoint de upload responde
    422 em vez de indexar lixo ou derrubar a inserção no banco."""
    cleaned = text.replace("\x00", "")
    if not cleaned:
        return ""

    sample = cleaned[:5000]
    control_chars = sum(1 for ch in sample if ord(ch) < 32 and ch not in "\t\n\r")
    if control_chars / len(sample) > 0.05:
        return ""
    return cleaned


def _extract_text(raw: bytes, filename: str, content_type: str) -> str:
    """Extrai texto do arquivo enviado. PDF via pypdf; txt/md como
    utf-8 direto; qualquer outro tipo tenta utf-8 best-effort (funciona
    para a maioria dos formatos texto-puro; binários não suportados
    resultam em string vazia e o endpoint responde 422)."""
    ext = _guess_file_type(filename)

    if ext == "pdf" or content_type == "application/pdf":
        try:
            from pypdf import PdfReader  # import local: dependência opcional

            reader = PdfReader(io.BytesIO(raw))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages_text)
        except Exception:  # noqa: BLE001
            logger.exception("rag.upload: falha ao extrair texto do PDF '%s'", filename)
            text = ""
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="ignore")

    return _sanitize_extracted_text(text)


def _chunk_text(text: str, max_len: int = 900, overlap: int = 150) -> List[str]:
    """Quebra o texto em pedaços de até `max_len` caracteres, respeitando
    parágrafos quando possível. Parágrafos maiores que `max_len` são
    fatiados em janelas fixas com sobreposição `overlap` (preserva
    contexto entre chunks vizinhos)."""
    normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not normalized:
        return []

    paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
    chunks: List[str] = []
    buffer = ""

    for para in paragraphs:
        candidate = f"{buffer}\n\n{para}".strip() if buffer else para
        if len(candidate) <= max_len:
            buffer = candidate
            continue

        if buffer:
            chunks.append(buffer)

        if len(para) <= max_len:
            buffer = para
        else:
            start = 0
            while start < len(para):
                end = start + max_len
                chunks.append(para[start:end])
                start = end - overlap
            buffer = ""

    if buffer:
        chunks.append(buffer)

    return chunks or [normalized[:max_len]]


# ---------------------------------------------------------------------------
# Documentos — upload, listagem, remoção (Knowledge Hub)
# ---------------------------------------------------------------------------
class DocumentOut(BaseModel):
    id: str
    collection: str
    title: str
    filename: str
    file_type: str
    source: str
    size_bytes: int
    chunk_count: int
    created_at: datetime


def _row_to_document(row) -> DocumentOut:
    return DocumentOut(
        id=str(row["id"]),
        collection=row["collection"],
        title=row["title"],
        filename=row["filename"],
        file_type=row["file_type"],
        source=row["source"],
        size_bytes=row["size_bytes"],
        chunk_count=row["chunk_count"],
        created_at=row["created_at"],
    )


@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de documento (PDF/txt/md) — extrai texto, faz chunking e indexa embeddings",
)
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="Arquivo a indexar (PDF recomendado; txt/md também suportados)."),
    collection: str = Form(..., description="Agente/coleção de destino (ex.: saneamento, energia, portos, aeroportos, barragens)."),
    title: Optional[str] = Form(default=None, description="Título de exibição. Default: nome do arquivo."),
) -> DocumentOut:
    _require_known_collection(collection)

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Arquivo vazio.")

    filename = file.filename or "documento-sem-nome"
    text_content = _extract_text(raw, filename, file.content_type or "")
    if not text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não foi possível extrair texto do arquivo (formato não suportado ou PDF sem texto/escaneado).",
        )

    chunks = _chunk_text(text_content)
    if not chunks:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Documento sem conteúdo aproveitável.")

    doc_id = str(uuid.uuid4())
    file_type = _guess_file_type(filename) or (file.content_type or "desconhecido")
    prefix = _prefix_for(collection)
    display_title = title or filename

    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG (Supabase/pgvector) indisponível no momento.",
            )
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                INSERT INTO rag_documents
                    (id, collection, title, filename, file_type, source, size_bytes, chunk_count, created_at)
                VALUES ($1, $2, $3, $4, $5, 'upload', $6, $7, now())
                RETURNING id, collection, title, filename, file_type, source, size_bytes, chunk_count, created_at
                """,
                doc_id,
                collection,
                display_title,
                filename,
                file_type,
                len(raw),
                len(chunks),
            )

            for idx, chunk in enumerate(chunks):
                embedding = _vector_literal(await embed_text(chunk))
                await conn.execute(
                    """
                    INSERT INTO rag_chunks (collection, prefix, content, embedding, document_id, chunk_index)
                    VALUES ($1, $2, $3, $4::vector, $5, $6)
                    """,
                    collection,
                    prefix,
                    chunk,
                    embedding,
                    doc_id,
                    idx,
                )

    return _row_to_document(row)


@router.get(
    "/documents",
    response_model=List[DocumentOut],
    summary="Lista documentos indexados (filtros por agente, tipo e período)",
)
async def list_documents(
    request: Request,
    collection: Optional[str] = Query(default=None, description="Filtra por agente/coleção."),
    file_type: Optional[str] = Query(default=None, description="Filtra por extensão (ex.: pdf, txt)."),
    date_from: Optional[date] = Query(default=None, description="Documentos criados a partir desta data (inclusive)."),
    date_to: Optional[date] = Query(default=None, description="Documentos criados até esta data (inclusive)."),
    q: Optional[str] = Query(default=None, description="Filtro textual por título/nome de arquivo."),
) -> List[DocumentOut]:
    if collection is not None:
        _require_known_collection(collection)

    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG (Supabase/pgvector) indisponível no momento.",
            )
        rows = await conn.fetch(
            """
            SELECT id, collection, title, filename, file_type, source, size_bytes, chunk_count, created_at
            FROM rag_documents
            WHERE ($1::text IS NULL OR collection = $1)
              AND ($2::text IS NULL OR file_type = $2)
              AND ($3::date IS NULL OR created_at >= $3::date)
              AND ($4::date IS NULL OR created_at < ($4::date + interval '1 day'))
              AND ($5::text IS NULL OR title ILIKE '%' || $5 || '%' OR filename ILIKE '%' || $5 || '%')
            ORDER BY created_at DESC
            """,
            collection,
            file_type,
            date_from,
            date_to,
            q,
        )

    return [_row_to_document(r) for r in rows]


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove um documento e seus chunks (cascade)",
)
async def delete_document(document_id: str, request: Request) -> None:
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="document_id inválido (esperado UUID).")

    async with acquire_optional(request) as conn:
        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Banco RAG (Supabase/pgvector) indisponível no momento.",
            )
        result = await conn.execute("DELETE FROM rag_documents WHERE id = $1", document_id)

    if result == "DELETE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")
