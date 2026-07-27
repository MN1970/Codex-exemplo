"""
models/knowledge.py — SQLAlchemy models para Knowledge Hub (CRUD documentos,
chunking, versionamento, acesso multi-org).

Desenho:
    Organization ──< KnowledgeDocument >── User (created_by)
    KnowledgeDocument ──< KnowledgeChunk >── embedding (pgvector)
    KnowledgeDocument ──< KnowledgeVersion >── snapshot

Recursos:
  • Soft-delete (deleted_at, preserva histórico)
  • Versionamento (snapshot_json de cada documento)
  • Suporte pgvector (embeddings dos chunks)
  • Tags (string array, filtro via OVERLAPS/contains)
  • Multi-org (todos os documentos cabem em org_id)
  • Progress tracking (processing_status, progress_pct)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Array,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _new_uuid() -> str:
    return str(uuid.uuid4())


# =============================================================================
# KnowledgeDocument — metadados do documento (PDF, CSV, DWG, TXT, DOCX)
# =============================================================================
class KnowledgeDocument(Base):
    """Documento enviado ao Knowledge Hub. Suporta:
    - Soft-delete (deleted_at)
    - Múltiplos arquivos tipos (PDF, CSV, DWG, TXT, DOCX)
    - Tags para organização/filtro
    - Chunking automático (chunks em KnowledgeChunk)
    - Rastreamento de progresso (processing_status: 'pending'|'processing'|'complete'|'failed')
    """

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint("org_id", "id", name="uq_knowledge_org_doc"),
    )

    # Identidade
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)

    # Arquivo
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="pdf|csv|dwg|txt|docx"
    )
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Metadados
    tags: Mapped[list[str]] = mapped_column(
        Array(String(128)), default=list, nullable=False,
        comment="Tags para organização: ['rodovia', 'pavimentação', ...]"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Processamento
    processing_status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        comment="pending|processing|complete|failed",
    )
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Soft-delete"
    )

    # Contadores
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relacionamentos
    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    versions: Mapped[list[KnowledgeVersion]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeDocument id={self.id!r} org_id={self.org_id!r} title={self.title!r}>"


# =============================================================================
# KnowledgeChunk — chunks do documento com embedding (pgvector)
# =============================================================================
class KnowledgeChunk(Base):
    """Chunk de um documento (500 tokens padrão, 50-token overlap).
    Armazena:
    - content: texto do chunk
    - embedding: vetor da Sentence Transformers (pgvector)
    - metadata: JSON com page, section, start_pos, etc.
    """

    __tablename__ = "knowledge_chunks"

    # Identidade
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conteúdo
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="Approximation: len(content.split())"
    )

    # Embedding (pgvector)
    # Em Postgres: embedding vector(N) onde N = dimensão do modelo Sentence Transformers
    # (padrão: all-MiniLM-L6-v2 = 384 dimensões)
    embedding: Mapped[list[float] | None] = mapped_column(
        nullable=True, comment="pgvector embedding (384 dims padrão)"
    )

    # Metadados do chunk
    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        comment="page: int, section: str, start_pos: int, source_file: str",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento
    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")

    def __repr__(self) -> str:
        return (
            f"<KnowledgeChunk id={self.id!r} doc_id={self.document_id!r} "
            f"idx={self.chunk_index}>"
        )


# =============================================================================
# KnowledgeVersion — versionamento de documentos (snapshot para rollback)
# =============================================================================
class KnowledgeVersion(Base):
    """Versão/snapshot de um documento para histórico e rollback.
    Armazena um snapshot em JSON (metadados + metadata relevante).
    Permite: "compare this version to previous" e "revert to version N".
    """

    __tablename__ = "knowledge_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_num", name="uq_doc_version"),
    )

    # Identidade
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Versionamento
    version_num: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Snapshot (JSON serialização do documento + metadata)
    snapshot_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        comment="""
        {
            "title": "...",
            "description": "...",
            "tags": [...],
            "chunk_count": N,
            "metadata": {...}
        }
        """,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento
    document: Mapped[KnowledgeDocument] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return (
            f"<KnowledgeVersion doc_id={self.document_id!r} "
            f"v{self.version_num}>"
        )
