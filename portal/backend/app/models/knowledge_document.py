"""
SQLAlchemy ORM model for KnowledgeDocument
"""

from sqlalchemy import Column, String, DateTime, JSON, Index, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class DocumentCategory(str, enum.Enum):
    """Knowledge document category"""
    RAG = "RAG"  # Retrieval-Augmented Generation
    ARCHITECTURE = "Architecture"
    ROUTING = "Routing"
    RUNBOOK = "Runbook"
    REFERENCE = "Reference"
    POLICY = "Policy"
    GUIDE = "Guide"


class DocumentStatus(str, enum.Enum):
    """Document status in the knowledge base"""
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"
    DEPRECATED = "Deprecated"


class KnowledgeDocument(Base):
    """Knowledge document registry model"""
    __tablename__ = "knowledge_documents"

    # Primary key
    id = Column(String(100), primary_key=True, index=True)

    # Core fields
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), nullable=False, unique=True, index=True)
    description = Column(String(1000), nullable=True)
    content = Column(Text, nullable=False)  # Full document content

    # Classification
    category = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default=DocumentStatus.PUBLISHED.value, index=True)
    tags = Column(JSON, default=list)  # Free-form tags for flexible categorization

    # Eixo and segment association
    eixo_tags = Column(JSON, default=list)  # Associated eixos: ["Horizontal", "Vertical", etc.]
    segment_tags = Column(JSON, default=list)  # Segments: ["Saneamento", "Energia", etc.]
    agent_tags = Column(JSON, default=list)  # Associated agents: ["manta-08", "agente-saneamento", etc.]

    # Sourcing
    source_url = Column(String(500), nullable=True)  # Original source if synced
    source_system = Column(String(100), nullable=True)  # e.g., "sharepoint", "manta-hub", "local"
    external_id = Column(String(255), nullable=True)  # ID in external system

    # RAG configuration
    is_rag_enabled = Column(Boolean, default=True)  # Enable for RAG retrieval
    chunk_strategy = Column(String(50), default="sentence")  # "sentence", "paragraph", "page"
    embedding_model = Column(String(100), nullable=True)  # e.g., "text-embedding-3-small"
    last_embedded_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    version = Column(String(50), default="1.0.0")
    language = Column(String(10), default="pt-BR")  # ISO 639-1 code
    author = Column(String(255), nullable=True)
    reviewer = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_knowledge_category', 'category'),
        Index('idx_knowledge_status', 'status'),
        Index('idx_knowledge_eixo_tags', 'eixo_tags'),  # JSON index if supported
        Index('idx_knowledge_segment_tags', 'segment_tags'),
        Index('idx_knowledge_agent_tags', 'agent_tags'),
        Index('idx_knowledge_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<KnowledgeDocument {self.id}: {self.title}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "content": self.content,
            "category": self.category,
            "status": self.status,
            "tags": self.tags or [],
            "eixo_tags": self.eixo_tags or [],
            "segment_tags": self.segment_tags or [],
            "agent_tags": self.agent_tags or [],
            "source_url": self.source_url,
            "source_system": self.source_system,
            "external_id": self.external_id,
            "is_rag_enabled": self.is_rag_enabled,
            "chunk_strategy": self.chunk_strategy,
            "embedding_model": self.embedding_model,
            "last_embedded_at": self.last_embedded_at.isoformat() if self.last_embedded_at else None,
            "version": self.version,
            "language": self.language,
            "author": self.author,
            "reviewer": self.reviewer,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }
