"""
Pydantic schemas for Agent request/response
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.agent import AgentStatus, AgentTier, AgentEixo


class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    aliases: Optional[List[str]] = Field(default_factory=list)
    description: Optional[str] = Field(default=None, max_length=1000)
    eixo: AgentEixo
    tier: AgentTier
    status: Optional[AgentStatus] = AgentStatus.OPERACIONAL
    service_url: Optional[str] = Field(default=None, max_length=500)
    routing_keywords: Optional[List[str]] = Field(default_factory=list)
    created_by: Optional[str] = Field(default=None, max_length=255)

    class Config:
        use_enum_values = False


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    aliases: Optional[List[str]] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=1000)
    tier: Optional[AgentTier] = None
    status: Optional[AgentStatus] = None
    service_url: Optional[str] = Field(default=None, max_length=500)
    routing_keywords: Optional[List[str]] = Field(default=None)
    updated_by: Optional[str] = Field(default=None, max_length=255)

    class Config:
        use_enum_values = False


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: str
    name: str
    code: str
    aliases: List[str]
    description: Optional[str]
    eixo: str  # Enum value as string
    tier: str  # Enum value as string
    status: str  # Enum value as string
    service_url: Optional[str]
    routing_keywords: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Schema for list of agents"""
    agents: List[AgentResponse]
    total: int
    limit: int
    offset: int
    filters: Optional[dict] = None


class AgentDetailResponse(BaseModel):
    """Schema for single agent detail"""
    agent: AgentResponse


class ErrorResponse(BaseModel):
    """Schema for error response"""
    detail: str
    status_code: int
    error_type: Optional[str] = None
