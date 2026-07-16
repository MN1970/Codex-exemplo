"""
SQLAlchemy ORM model for Agent
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class AgentStatus(str, enum.Enum):
    """Agent operational status"""
    OPERACIONAL = "Operacional"
    BETA = "Beta"
    PARCIAL = "Parcial"
    INATIVO = "Inativo"
    DESCONTINUADO = "Descontinuado"


class AgentTier(str, enum.Enum):
    """Model tier for agent"""
    HAIKU = "Haiku"
    SONNET = "Sonnet"
    OPUS = "Opus"
    HAIKU_TO_SONNET = "Haiku→Sonnet"
    SONNET_TO_OPUS = "Sonnet/Opus"


class AgentEixo(str, enum.Enum):
    """Eixo classification"""
    HORIZONTAL = "Horizontal"  # Transversal agents
    VERTICAL = "Vertical"      # Segment-specific agents
    LIFECYCLE = "Lifecycle"    # Phase-specific agents


class Agent(Base):
    """Agent registry model"""
    __tablename__ = "agents"

    # Primary key
    id = Column(String(50), primary_key=True, index=True)  # e.g., "manta-00", "manta-03-s8"

    # Core fields
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)  # e.g., "Manta 00", "Manta 03-S8"
    aliases = Column(JSON, default=list)  # JSON array of alternative names
    description = Column(String(1000), nullable=True)

    # Classification
    eixo = Column(SQLEnum(AgentEixo), nullable=False, index=True)
    tier = Column(SQLEnum(AgentTier), nullable=False)
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.OPERACIONAL, index=True)

    # Operations
    service_url = Column(String(500), nullable=True)  # URL to agent service or documentation
    routing_keywords = Column(JSON, default=list)  # Keywords for automatic routing

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_agent_eixo_status', 'eixo', 'status'),
        Index('idx_agent_eixo_tier', 'eixo', 'tier'),
        Index('idx_agent_status', 'status'),
        Index('idx_agent_tier', 'tier'),
    )

    def __repr__(self):
        return f"<Agent {self.code}: {self.name}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "aliases": self.aliases or [],
            "description": self.description,
            "eixo": self.eixo.value if isinstance(self.eixo, AgentEixo) else self.eixo,
            "tier": self.tier.value if isinstance(self.tier, AgentTier) else self.tier,
            "status": self.status.value if isinstance(self.status, AgentStatus) else self.status,
            "service_url": self.service_url,
            "routing_keywords": self.routing_keywords or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }
