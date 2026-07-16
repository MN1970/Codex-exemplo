"""
FastAPI router for Knowledge Base management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.knowledge import KnowledgeCategory
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentDetailResponse,
    KnowledgeDocumentListResponse,
    KnowledgeSearchResponse,
    KnowledgeCategoryResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    ErrorResponse,
)
from app.db import knowledge as knowledge_db
from app.services.knowledge_service import KnowledgeBaseManager

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


@router.get("", response_model=KnowledgeDocumentListResponse)
async def list_documents(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    eixo: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
):
    """
    List all knowledge documents with optional filtering and pagination.

    Query parameters:
    - limit: Number of documents per page (default: 100, max: 500)
    - offset: Starting position for pagination (default: 0)
    - category: Filter by category (Agent Profile, Routing Rule, etc.)
    - eixo: Filter by eixo tag (e.g., S1, S8, Horizontal)
    - agent_id: Filter by associated agent ID
    """
    try:
        # Parse category enum if provided
        category_enum = None
        if category:
            try:
                category_enum = KnowledgeCategory[category.upper().replace("-", "_").replace(" ", "_")]
            except KeyError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid category: {category}. Must be one of: {', '.join(c.name for c in KnowledgeCategory)}"
                )

        documents, total = knowledge_db.get_knowledge_documents(
            db,
            limit=limit,
            offset=offset,
            category=category_enum,
            eixo=eixo,
            agent_id=agent_id,
        )

        responses = [KnowledgeDocumentResponse.model_validate(doc.to_dict()) for doc in documents]

        return KnowledgeDocumentListResponse(
            documents=responses,
            total=total,
            limit=limit,
            offset=offset,
            filters={
                "category": category,
                "eixo": eixo,
                "agent_id": agent_id,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    eixo: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
):
    """
    Full-text search on knowledge documents.

    Query parameters:
    - q: Search query (required)
    - limit: Number of results per page (default: 100, max: 500)
    - offset: Starting position for pagination (default: 0)
    - category: Filter by category
    - eixo: Filter by eixo tag
    - agent_id: Filter by associated agent ID
    """
    try:
        # Parse category enum if provided
        category_enum = None
        if category:
            try:
                category_enum = KnowledgeCategory[category.upper().replace("-", "_").replace(" ", "_")]
            except KeyError:
                raise HTTPException(status_code=422, detail=f"Invalid category: {category}")

        documents, total = knowledge_db.search_knowledge_documents(
            db,
            query=q,
            limit=limit,
            offset=offset,
            category=category_enum,
            eixo=eixo,
            agent_id=agent_id,
        )

        responses = [KnowledgeDocumentResponse.model_validate(doc.to_dict()) for doc in documents]

        return KnowledgeSearchResponse(
            results=responses,
            total=total,
            limit=limit,
            offset=offset,
            query=q,
            filters={
                "category": category,
                "eixo": eixo,
                "agent_id": agent_id,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", response_model=KnowledgeDocumentDetailResponse)
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    """
    Get a specific knowledge document with chunks and external sources.
    """
    try:
        document = knowledge_db.get_knowledge_document_by_id(db, doc_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

        # Get chunks and external sources
        from app.schemas.knowledge import KnowledgeChunkResponse, ExternalSourceResponse

        chunks = knowledge_db.get_knowledge_chunks_by_doc(db, doc_id)
        chunk_responses = [KnowledgeChunkResponse.model_validate(chunk.to_dict()) for chunk in chunks]

        sources = knowledge_db.get_external_sources_by_doc(db, doc_id)
        source_responses = [ExternalSourceResponse.model_validate(source.to_dict()) for source in sources]

        doc_dict = document.to_dict()
        return KnowledgeDocumentDetailResponse(
            **doc_dict,
            chunks=chunk_responses,
            external_sources=source_responses,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=KnowledgeDocumentDetailResponse, status_code=201)
async def create_document(
    doc_create: KnowledgeDocumentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new knowledge document.
    """
    try:
        document = knowledge_db.create_knowledge_document(db, doc_create)

        from app.schemas.knowledge import KnowledgeChunkResponse, ExternalSourceResponse

        chunks = knowledge_db.get_knowledge_chunks_by_doc(db, document.id)
        chunk_responses = [KnowledgeChunkResponse.model_validate(chunk.to_dict()) for chunk in chunks]

        sources = knowledge_db.get_external_sources_by_doc(db, document.id)
        source_responses = [ExternalSourceResponse.model_validate(source.to_dict()) for source in sources]

        doc_dict = document.to_dict()
        return KnowledgeDocumentDetailResponse(
            **doc_dict,
            chunks=chunk_responses,
            external_sources=source_responses,
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{doc_id}", response_model=KnowledgeDocumentDetailResponse)
async def update_document(
    doc_id: str,
    doc_update: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing knowledge document.

    Only provided fields will be updated.
    """
    try:
        document = knowledge_db.update_knowledge_document(db, doc_id, doc_update)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

        from app.schemas.knowledge import KnowledgeChunkResponse, ExternalSourceResponse

        chunks = knowledge_db.get_knowledge_chunks_by_doc(db, document.id)
        chunk_responses = [KnowledgeChunkResponse.model_validate(chunk.to_dict()) for chunk in chunks]

        sources = knowledge_db.get_external_sources_by_doc(db, document.id)
        source_responses = [ExternalSourceResponse.model_validate(source.to_dict()) for source in sources]

        doc_dict = document.to_dict()
        return KnowledgeDocumentDetailResponse(
            **doc_dict,
            chunks=chunk_responses,
            external_sources=source_responses,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """
    Delete a knowledge document and all associated chunks and sources.
    """
    try:
        success = knowledge_db.delete_knowledge_document(db, doc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=KnowledgeCategoryResponse)
async def get_categories():
    """
    Get list of available knowledge document categories.
    """
    try:
        categories = [cat.value for cat in KnowledgeCategory]
        return KnowledgeCategoryResponse(
            categories=categories,
            count=len(categories),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=KnowledgeIngestResponse)
async def ingest_from_github(
    request: KnowledgeIngestRequest,
    db: Session = Depends(get_db),
):
    """
    Ingest knowledge documents from a GitHub repository.

    This endpoint will:
    1. Clone or fetch the repository
    2. Parse documentation files (CLAUDE.md, README.md, *.md)
    3. Extract metadata and chunk content
    4. Create knowledge documents with full-text search support
    """
    try:
        manager = KnowledgeBaseManager(db)
        result = await manager.ingest_from_github(
            repo_owner=request.repo_owner,
            repo_name=request.repo_name,
            paths=request.paths,
            branch=request.branch,
        )

        return KnowledgeIngestResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
