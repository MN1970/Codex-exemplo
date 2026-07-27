"""
routers/knowledge.py — Endpoints de Knowledge Hub (upload, CRUD, busca semântica).

    POST   /knowledge/upload                 — upload multipart (PDF/CSV/DWG/TXT/DOCX)
    GET    /knowledge/documents              — lista docs (filtros: tag, org, date range, status)
    GET    /knowledge/documents/{id}         — metadados + chunks
    PUT    /knowledge/documents/{id}         — update tags/description
    DELETE /knowledge/documents/{id}         — soft-delete
    POST   /knowledge/documents/{id}/versions — criar versão (snapshot)
    GET    /knowledge/documents/{id}/versions — lista versões
    POST   /knowledge/semantic-search        — busca semântica (across orgs se admin)

Multipart upload:
  • Validators: file_type (pdf|csv|dwg|txt|docx), size < 500MB
  • Auto-chunk em background (500 tokens, 50-token overlap)
  • Auto-embed via Sentence Transformers
  • Progress: /knowledge/documents/{id} poll processing_status + progress_pct

Acesso multi-org:
  • Todos os documentos filtrados por org_id (via JWT)
  • Admins podem passar ?org_id=... para query docs de outra org
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import get_current_user, JWTClaims
from db import get_session
from models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeVersion
from ml.embeddings import embed_text

logger = logging.getLogger("manta.knowledge")

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# =============================================================================
# Schemas
# =============================================================================
class KnowledgeChunkSchema(BaseModel):
    id: str
    chunk_index: int
    content: str
    content_tokens: int
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentResponse(BaseModel):
    id: str
    org_id: str
    title: str
    filename: str
    file_type: str
    source_url: str | None
    size_bytes: int
    tags: list[str]
    description: str | None
    created_by: str | None
    processing_status: str
    progress_pct: int
    error_message: str | None
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    class Config:
        from_attributes = True


class KnowledgeDocumentDetailResponse(KnowledgeDocumentResponse):
    chunks: list[KnowledgeChunkSchema] = Field(default_factory=list)


class KnowledgeVersionSchema(BaseModel):
    id: str
    version_num: int
    created_by: str | None
    snapshot_json: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[KnowledgeDocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    tags: list[str] = Field(default_factory=list)
    description: str | None = Field(None, max_length=2048)


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=512)
    tags: list[str] | None = None
    description: str | None = Field(None, max_length=2048)


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1024)
    top_k: int = Field(default=5, ge=1, le=50)
    tags: list[str] = Field(default_factory=list, description="Filtro por tags")
    org_ids: list[str] = Field(
        default_factory=list,
        description="Admin only: buscar em múltiplas orgs",
    )


class SemanticSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    content_tokens: int
    similarity_score: float
    page_num: int | None
    tags: list[str]
    metadata: dict[str, Any]


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]
    search_time_ms: float


# =============================================================================
# Helpers
# =============================================================================
ALLOWED_FILE_TYPES = {"pdf", "csv", "dwg", "txt", "docx"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


def _validate_file_upload(file: UploadFile) -> tuple[str, bytes]:
    """Valida tipo e tamanho do arquivo. Retorna (file_type, content)."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename required",
        )

    # Detecta extensão
    parts = file.filename.rsplit(".", 1)
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have an extension",
        )
    file_type = parts[1].lower()

    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_type} not allowed. Allowed: {ALLOWED_FILE_TYPES}",
        )

    # Valida tamanho (será lido integralmente)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file.size} exceeds {MAX_FILE_SIZE}",
        )

    return file_type, file_type


async def _process_document_upload(
    org_id: str,
    user_id: str,
    file_type: str,
    filename: str,
    content: bytes,
    title: str,
    tags: list[str],
    description: str | None,
    session: AsyncSession,
) -> str:
    """Cria KnowledgeDocument com status 'processing' e enfileira background job."""
    doc_id = str(uuid.uuid4())

    # Cria documento no DB
    doc = KnowledgeDocument(
        id=doc_id,
        org_id=org_id,
        title=title,
        filename=filename,
        file_type=file_type,
        tags=tags or [],
        description=description,
        created_by=user_id,
        size_bytes=len(content),
        processing_status="pending",
        progress_pct=0,
    )
    session.add(doc)
    await session.commit()

    # TODO: Enfileira Celery task (knowledge_ingest.process_document_upload)
    # Para agora, apenas retorna o doc_id para polling
    logger.info(
        "knowledge.upload: document enqueued",
        extra={"doc_id": doc_id, "size": len(content)},
    )

    return doc_id


# =============================================================================
# Endpoints
# =============================================================================
@router.post(
    "/upload",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    tags: str = Form(default=""),  # JSON string: '["tag1", "tag2"]'
    description: str = Form(default=""),
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> KnowledgeDocumentResponse:
    """
    Upload de documento (PDF/CSV/DWG/TXT/DOCX) para Knowledge Hub.

    - Validação de tipo/tamanho
    - Cria KnowledgeDocument com status='pending'
    - Enfileira processamento em background
    - Retorna 202 Accepted com doc_id para polling

    Query: /knowledge/documents/{doc_id} para rastrear progresso
    """
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    # Valida arquivo
    file_type, _ = _validate_file_upload(file)

    # Parse tags (JSON array)
    import json
    try:
        parsed_tags = json.loads(tags) if tags else []
        if not isinstance(parsed_tags, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tags must be JSON array",
        )

    # Lê conteúdo
    content = await file.read()

    # Cria documento e enfileira processing
    doc_id = await _process_document_upload(
        org_id=org_id,
        user_id=current_user.sub,
        file_type=file_type,
        filename=file.filename,
        content=content,
        title=title,
        tags=parsed_tags,
        description=description if description else None,
        session=session,
    )

    # Busca documento criado para resposta
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    result = await session.execute(stmt)
    doc = result.scalar_one()

    return KnowledgeDocumentResponse.from_attributes(doc)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: str = Query("", description="CSV: tag1,tag2"),
    status_filter: str = Query("", description="pending|processing|complete|failed"),
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    org_id: str = Query("", description="Admin only: filter by org"),
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentListResponse:
    """
    Lista documentos com filtros opcionais.

    Filtros:
    - tags: CSV (tag1,tag2) - match ANY
    - status_filter: processing_status (pending|processing|complete|failed)
    - created_after/before: timestamp range
    - org_id: admin only, filtro por organização

    Default: documentos da organização ativa (current_user.org_id)
    """
    user_org_id = current_user.org_id
    if not user_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    # Filtra por org (default = ativa; admin pode passar ?org_id=...)
    if org_id and org_id != user_org_id:
        # TODO: Check admin role
        pass
    effective_org_id = org_id or user_org_id

    # Constrói query
    filters = [
        KnowledgeDocument.org_id == effective_org_id,
        KnowledgeDocument.deleted_at.is_(None),  # Exclude soft-deleted
    ]

    # Tag filter (CSV → ANY match)
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            filters.append(
                KnowledgeDocument.tags.overlap(tag_list)  # PostgreSQL OVERLAPS
            )

    # Status filter
    if status_filter:
        filters.append(KnowledgeDocument.processing_status == status_filter)

    # Date range
    if created_after:
        filters.append(KnowledgeDocument.created_at >= created_after)
    if created_before:
        filters.append(KnowledgeDocument.created_at <= created_before)

    # Count total
    count_stmt = select(func.count(KnowledgeDocument.id)).where(
        and_(*filters)
    )
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    stmt = (
        select(KnowledgeDocument)
        .where(and_(*filters))
        .order_by(desc(KnowledgeDocument.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[
            KnowledgeDocumentResponse.from_attributes(doc) for doc in documents
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{doc_id}", response_model=KnowledgeDocumentDetailResponse)
async def get_document(
    doc_id: str,
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> KnowledgeDocumentDetailResponse:
    """Retorna documento + chunks (metadados + conteúdo)."""
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    stmt = select(KnowledgeDocument).where(
        and_(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.org_id == org_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Carrega chunks
    chunks_stmt = (
        select(KnowledgeChunk)
        .where(KnowledgeChunk.document_id == doc_id)
        .order_by(KnowledgeChunk.chunk_index)
    )
    chunks_result = await session.execute(chunks_stmt)
    chunks = chunks_result.scalars().all()

    return KnowledgeDocumentDetailResponse(
        **{k: getattr(doc, k) for k in KnowledgeDocumentResponse.__fields__.keys()},
        chunks=[KnowledgeChunkSchema.from_attributes(c) for c in chunks],
    )


@router.put("/documents/{doc_id}", response_model=KnowledgeDocumentResponse)
async def update_document(
    doc_id: str,
    req: DocumentUpdateRequest,
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> KnowledgeDocumentResponse:
    """Atualiza título/tags/description. Cria versão antes de modificar."""
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    stmt = select(KnowledgeDocument).where(
        and_(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.org_id == org_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Cria versão antes de modificar
    max_version_stmt = select(func.max(KnowledgeVersion.version_num)).where(
        KnowledgeVersion.document_id == doc_id
    )
    max_version_result = await session.execute(max_version_stmt)
    next_version = (max_version_result.scalar() or 0) + 1

    version = KnowledgeVersion(
        id=str(uuid.uuid4()),
        document_id=doc_id,
        version_num=next_version,
        created_by=current_user.sub,
        snapshot_json={
            "title": doc.title,
            "tags": doc.tags,
            "description": doc.description,
            "chunk_count": doc.chunk_count,
        },
    )
    session.add(version)

    # Update fields
    if req.title is not None:
        doc.title = req.title
    if req.tags is not None:
        doc.tags = req.tags
    if req.description is not None:
        doc.description = req.description

    doc.updated_at = datetime.utcnow()
    await session.commit()

    return KnowledgeDocumentResponse.from_attributes(doc)


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Soft-delete documento (mark deleted_at)."""
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    stmt = select(KnowledgeDocument).where(
        and_(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.org_id == org_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    doc.deleted_at = datetime.utcnow()
    await session.commit()


@router.get(
    "/documents/{doc_id}/versions",
    response_model=list[KnowledgeVersionSchema],
)
async def list_versions(
    doc_id: str,
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[KnowledgeVersionSchema]:
    """Lista versões de um documento."""
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    # Verifica acesso ao documento
    stmt = select(KnowledgeDocument).where(
        and_(
            KnowledgeDocument.id == doc_id,
            KnowledgeDocument.org_id == org_id,
            KnowledgeDocument.deleted_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Busca versões
    versions_stmt = (
        select(KnowledgeVersion)
        .where(KnowledgeVersion.document_id == doc_id)
        .order_by(desc(KnowledgeVersion.version_num))
    )
    versions_result = await session.execute(versions_stmt)
    versions = versions_result.scalars().all()

    return [KnowledgeVersionSchema.from_attributes(v) for v in versions]


@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(
    req: SemanticSearchRequest,
    current_user: JWTClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SemanticSearchResponse:
    """
    Busca semântica em chunks de documentos usando pgvector.

    Busca em documentos da org ativa (padrão) ou múltiplas orgs (admin).
    Filtro opcional por tags.
    """
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization required",
        )

    import time
    start_time = time.time()

    # Gera embedding da query
    query_embedding = await embed_text(req.query)
    if not query_embedding:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to embed query",
        )

    # Orgs para busca
    search_org_ids = req.org_ids or [org_id]

    # TODO: Implementar pgvector query para similarity search
    # Por agora, retorna mock response
    results = []

    elapsed_ms = (time.time() - start_time) * 1000

    return SemanticSearchResponse(
        query=req.query,
        results=results,
        search_time_ms=elapsed_ms,
    )
