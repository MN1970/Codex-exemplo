"""
SQLAlchemy ORM models for Knowledge Base
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Index, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class KnowledgeCategory(str, enum.Enum):
    """Knowledge document categories"""
    AGENT_PROFILE = "Agent Profile"
    ROUTING_RULE = "Routing Rule"
    DOCUMENTATION = "Documentation"
    ARCHITECTURE = "Architecture"
    EXTERNAL_RESOURCE = "External Resource"
    SKILL = "Skill"
    RUNBOOK = "Runbook"


class ExternalSourceType(str, enum.Enum):
    """Type of external source"""
    DIRECT = "direct"                # Direct link
    SNAPSHOT = "snapshot"            # Web.Archive snapshot
    WAYBACK = "wayback"              # Wayback Machine archive


class ExternalSourceStatus(str, enum.Enum):
    """Status of external source"""
    LIVE = "live"                    # Still accessible
    SNAPSHOT = "snapshot"            # Using archived version
    ARCHIVED = "archived"            # No longer accessible
    ERROR = "error"                  # Last check had error


class KnowledgeDocument(Base):
    """Knowledge base document"""
    __tablename__ = "knowledge_documents"

    # Primary key
    id = Column(String(100), primary_key=True, index=True)

    # Content
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Markdown or plain text
    summary = Column(String(1000), nullable=True)

    # Classification
    category = Column(SQLEnum(KnowledgeCategory), nullable=False, index=True)
    eixo_tags = Column(JSON, default=list)  # Tags for eixo (e.g., ["S1", "S8"])
    agent_ids = Column(JSON, default=list)  # Associated agent IDs
    tags = Column(JSON, default=list)  # Custom tags

    # Source
    source_url = Column(String(1000), nullable=True, index=True)
    source_repo = Column(String(500), nullable=True)  # Source repository
    source_path = Column(String(500), nullable=True)  # Path in source repo

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Relations
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")
    external_sources = relationship("ExternalSource", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_knowledge_category', 'category'),
        Index('idx_knowledge_eixo', 'category'),  # For filtering by eixo_tags
        Index('idx_knowledge_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<KnowledgeDocument {self.id}: {self.title}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category.value if isinstance(self.category, KnowledgeCategory) else self.category,
            "eixo_tags": self.eixo_tags or [],
            "agent_ids": self.agent_ids or [],
            "tags": self.tags or [],
            "source_url": self.source_url,
            "source_repo": self.source_repo,
            "source_path": self.source_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "chunk_count": len(self.chunks) if self.chunks else 0,
            "external_sources_count": len(self.external_sources) if self.external_sources else 0,
        }


class KnowledgeChunk(Base):
    """Chunked content from knowledge documents (for search)"""
    __tablename__ = "knowledge_chunks"

    # Primary key
    id = Column(String(150), primary_key=True, index=True)  # doc_id:chunk_index

    # Foreign key
    doc_id = Column(String(100), ForeignKey("knowledge_documents.id"), nullable=False, index=True)

    # Content
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    section_title = Column(String(500), nullable=True)  # Heading or section name

    # Search support
    embedding_vector = Column(String(5000), nullable=True)  # Placeholder for future embedding JSON
    token_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relation
    document = relationship("KnowledgeDocument", back_populates="chunks")

    # Indexes
    __table_args__ = (
        Index('idx_chunk_doc_id', 'doc_id'),
        Index('idx_chunk_index', 'chunk_index'),
    )

    def __repr__(self):
        return f"<KnowledgeChunk {self.id}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "section_title": self.section_title,
            "token_count": self.token_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ExternalSource(Base):
    """External resource links associated with knowledge documents"""
    __tablename__ = "external_sources"

    # Primary key
    id = Column(String(150), primary_key=True, index=True)  # doc_id:source_index

    # Foreign key
    doc_id = Column(String(100), ForeignKey("knowledge_documents.id"), nullable=False, index=True)

    # URL
    url = Column(String(2000), nullable=False)
    title = Column(String(500), nullable=True)

    # Type and status
    source_type = Column(SQLEnum(ExternalSourceType), default=ExternalSourceType.DIRECT, nullable=False)
    status = Column(SQLEnum(ExternalSourceStatus), default=ExternalSourceStatus.LIVE, nullable=False, index=True)

    # Snapshot management
    snapshot_url = Column(String(2000), nullable=True)  # Web.Archive or Wayback snapshot
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_status_code = Column(Integer, nullable=True)  # HTTP status

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relation
    document = relationship("KnowledgeDocument", back_populates="external_sources")

    # Indexes
    __table_args__ = (
        Index('idx_external_doc_id', 'doc_id'),
        Index('idx_external_status', 'status'),
        Index('idx_external_checked_at', 'last_checked_at'),
    )

    def __repr__(self):
        return f"<ExternalSource {self.id}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type.value if isinstance(self.source_type, ExternalSourceType) else self.source_type,
            "status": self.status.value if isinstance(self.status, ExternalSourceStatus) else self.status,
            "snapshot_url": self.snapshot_url,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "last_status_code": self.last_status_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
