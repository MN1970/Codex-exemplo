"""
Pydantic schemas for Knowledge Base request/response
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.knowledge import KnowledgeCategory, ExternalSourceType, ExternalSourceStatus


class ExternalSourceResponse(BaseModel):
    """Response schema for external source"""
    id: str
    doc_id: str
    url: str
    title: Optional[str]
    source_type: str
    status: str
    snapshot_url: Optional[str]
    last_checked_at: Optional[datetime]
    last_status_code: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeChunkResponse(BaseModel):
    """Response schema for knowledge chunk"""
    id: str
    doc_id: str
    chunk_text: str
    chunk_index: int
    section_title: Optional[str]
    token_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentCreate(BaseModel):
    """Schema for creating a knowledge document"""
    id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(default=None, max_length=1000)
    category: KnowledgeCategory
    eixo_tags: Optional[List[str]] = Field(default_factory=list)
    agent_ids: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    source_url: Optional[str] = Field(default=None, max_length=1000)
    source_repo: Optional[str] = Field(default=None, max_length=500)
    source_path: Optional[str] = Field(default=None, max_length=500)
    created_by: Optional[str] = Field(default=None, max_length=255)

    class Config:
        use_enum_values = False


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating a knowledge document"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    content: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[KnowledgeCategory] = None
    eixo_tags: Optional[List[str]] = None
    agent_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    source_url: Optional[str] = Field(default=None, max_length=1000)
    source_repo: Optional[str] = Field(default=None, max_length=500)
    source_path: Optional[str] = Field(default=None, max_length=500)
    updated_by: Optional[str] = Field(default=None, max_length=255)

    class Config:
        use_enum_values = False


class KnowledgeDocumentResponse(BaseModel):
    """Response schema for knowledge document"""
    id: str
    title: str
    content: str
    summary: Optional[str]
    category: str
    eixo_tags: List[str]
    agent_ids: List[str]
    tags: List[str]
    source_url: Optional[str]
    source_repo: Optional[str]
    source_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    chunk_count: int
    external_sources_count: int

    class Config:
        from_attributes = True


class KnowledgeDocumentDetailResponse(BaseModel):
    """Detailed response schema for knowledge document with chunks and sources"""
    id: str
    title: str
    content: str
    summary: Optional[str]
    category: str
    eixo_tags: List[str]
    agent_ids: List[str]
    tags: List[str]
    source_url: Optional[str]
    source_repo: Optional[str]
    source_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    chunks: List[KnowledgeChunkResponse] = Field(default_factory=list)
    external_sources: List[ExternalSourceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class KnowledgeDocumentListResponse(BaseModel):
    """List response with pagination"""
    documents: List[KnowledgeDocumentResponse]
    total: int
    limit: int
    offset: int
    filters: dict = {}


class KnowledgeSearchResponse(BaseModel):
    """Search results response"""
    results: List[KnowledgeDocumentResponse]
    total: int
    limit: int
    offset: int
    query: str
    filters: dict = {}


class KnowledgeCategoryResponse(BaseModel):
    """Response listing available categories"""
    categories: List[str]
    count: int


class KnowledgeIngestRequest(BaseModel):
    """Request schema for ingesting documents from GitHub"""
    repo_owner: str = Field(..., min_length=1)
    repo_name: str = Field(..., min_length=1)
    paths: Optional[List[str]] = Field(default_factory=list)  # Optional path filter
    branch: Optional[str] = Field(default="main")

    class Config:
        use_enum_values = False


class KnowledgeIngestResponse(BaseModel):
    """Response from ingest operation"""
    status: str
    ingested_count: int
    failed_count: int
    errors: List[str] = []
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
