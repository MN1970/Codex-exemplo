"""
Database access layer for Knowledge Base
"""

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
import logging

from app.models.knowledge import (
    KnowledgeDocument,
    KnowledgeChunk,
    ExternalSource,
    KnowledgeCategory,
    ExternalSourceStatus,
)
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
)

logger = logging.getLogger(__name__)


def get_knowledge_documents(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    category: Optional[KnowledgeCategory] = None,
    eixo: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> Tuple[List[KnowledgeDocument], int]:
    """Get knowledge documents with optional filters"""
    query = db.query(KnowledgeDocument)

    if category:
        query = query.filter(KnowledgeDocument.category == category)

    if eixo:
        # Filter by eixo_tags containing the value
        query = query.filter(KnowledgeDocument.eixo_tags.contains([eixo]))

    if agent_id:
        # Filter by agent_ids containing the value
        query = query.filter(KnowledgeDocument.agent_ids.contains([agent_id]))

    total = query.count()
    documents = query.order_by(KnowledgeDocument.created_at.desc()).limit(limit).offset(offset).all()

    return documents, total


def get_knowledge_document_by_id(db: Session, doc_id: str) -> Optional[KnowledgeDocument]:
    """Get a knowledge document by ID"""
    return db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()


def search_knowledge_documents(
    db: Session,
    query: str,
    limit: int = 100,
    offset: int = 0,
    category: Optional[KnowledgeCategory] = None,
    eixo: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> Tuple[List[KnowledgeDocument], int]:
    """Full-text search on knowledge documents"""
    search_filter = and_(
        or_(
            KnowledgeDocument.title.ilike(f"%{query}%"),
            KnowledgeDocument.content.ilike(f"%{query}%"),
            KnowledgeDocument.summary.ilike(f"%{query}%"),
        )
    )

    db_query = db.query(KnowledgeDocument).filter(search_filter)

    if category:
        db_query = db_query.filter(KnowledgeDocument.category == category)

    if eixo:
        db_query = db_query.filter(KnowledgeDocument.eixo_tags.contains([eixo]))

    if agent_id:
        db_query = db_query.filter(KnowledgeDocument.agent_ids.contains([agent_id]))

    total = db_query.count()
    documents = db_query.order_by(KnowledgeDocument.created_at.desc()).limit(limit).offset(offset).all()

    return documents, total


def create_knowledge_document(
    db: Session,
    doc_create: KnowledgeDocumentCreate,
) -> KnowledgeDocument:
    """Create a new knowledge document"""
    # Check if document already exists
    existing = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_create.id).first()
    if existing:
        raise ValueError(f"Document with id '{doc_create.id}' already exists")

    document = KnowledgeDocument(
        id=doc_create.id,
        title=doc_create.title,
        content=doc_create.content,
        summary=doc_create.summary,
        category=doc_create.category,
        eixo_tags=doc_create.eixo_tags or [],
        agent_ids=doc_create.agent_ids or [],
        tags=doc_create.tags or [],
        source_url=doc_create.source_url,
        source_repo=doc_create.source_repo,
        source_path=doc_create.source_path,
        created_by=doc_create.created_by,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def update_knowledge_document(
    db: Session,
    doc_id: str,
    doc_update: KnowledgeDocumentUpdate,
) -> Optional[KnowledgeDocument]:
    """Update a knowledge document"""
    document = get_knowledge_document_by_id(db, doc_id)
    if not document:
        return None

    # Update fields
    if doc_update.title is not None:
        document.title = doc_update.title
    if doc_update.content is not None:
        document.content = doc_update.content
    if doc_update.summary is not None:
        document.summary = doc_update.summary
    if doc_update.category is not None:
        document.category = doc_update.category
    if doc_update.eixo_tags is not None:
        document.eixo_tags = doc_update.eixo_tags
    if doc_update.agent_ids is not None:
        document.agent_ids = doc_update.agent_ids
    if doc_update.tags is not None:
        document.tags = doc_update.tags
    if doc_update.source_url is not None:
        document.source_url = doc_update.source_url
    if doc_update.source_repo is not None:
        document.source_repo = doc_update.source_repo
    if doc_update.source_path is not None:
        document.source_path = doc_update.source_path
    if doc_update.updated_by is not None:
        document.updated_by = doc_update.updated_by

    db.commit()
    db.refresh(document)

    return document


def delete_knowledge_document(db: Session, doc_id: str) -> bool:
    """Delete a knowledge document (and all associated chunks and sources)"""
    document = get_knowledge_document_by_id(db, doc_id)
    if not document:
        return False

    db.delete(document)
    db.commit()

    return True


def create_knowledge_chunk(
    db: Session,
    doc_id: str,
    chunk_text: str,
    chunk_index: int,
    section_title: Optional[str] = None,
    token_count: int = 0,
) -> KnowledgeChunk:
    """Create a knowledge chunk"""
    chunk_id = f"{doc_id}:{chunk_index}"

    chunk = KnowledgeChunk(
        id=chunk_id,
        doc_id=doc_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        section_title=section_title,
        token_count=token_count,
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def get_knowledge_chunks_by_doc(db: Session, doc_id: str) -> List[KnowledgeChunk]:
    """Get all chunks for a document"""
    return (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.doc_id == doc_id)
        .order_by(KnowledgeChunk.chunk_index.asc())
        .all()
    )


def delete_knowledge_chunks_by_doc(db: Session, doc_id: str) -> int:
    """Delete all chunks for a document"""
    count = db.query(KnowledgeChunk).filter(KnowledgeChunk.doc_id == doc_id).delete()
    db.commit()
    return count


def create_external_source(
    db: Session,
    doc_id: str,
    url: str,
    source_index: int,
    title: Optional[str] = None,
    source_type: str = "direct",
) -> ExternalSource:
    """Create an external source"""
    source_id = f"{doc_id}:source:{source_index}"

    source = ExternalSource(
        id=source_id,
        doc_id=doc_id,
        url=url,
        title=title,
        source_type=source_type,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def get_external_sources_by_doc(db: Session, doc_id: str) -> List[ExternalSource]:
    """Get all external sources for a document"""
    return db.query(ExternalSource).filter(ExternalSource.doc_id == doc_id).all()


def get_external_sources_by_status(
    db: Session,
    status: ExternalSourceStatus,
) -> List[ExternalSource]:
    """Get external sources by status"""
    return db.query(ExternalSource).filter(ExternalSource.status == status).all()


def update_external_source_status(
    db: Session,
    source_id: str,
    status: ExternalSourceStatus,
    status_code: Optional[int] = None,
) -> Optional[ExternalSource]:
    """Update external source status"""
    source = db.query(ExternalSource).filter(ExternalSource.id == source_id).first()
    if not source:
        return None

    source.status = status
    if status_code is not None:
        source.last_status_code = status_code
    source.last_checked_at = func.now()

    db.commit()
    db.refresh(source)

    return source


def delete_external_source(db: Session, source_id: str) -> bool:
    """Delete an external source"""
    source = db.query(ExternalSource).filter(ExternalSource.id == source_id).first()
    if not source:
        return False

    db.delete(source)
    db.commit()

    return True
