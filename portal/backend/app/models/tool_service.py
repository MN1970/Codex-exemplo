"""
SQLAlchemy ORM model for ToolService
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ServiceStatus(str, enum.Enum):
    """Tool service operational status"""
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OFFLINE = "Offline"
    MAINTENANCE = "Maintenance"
    UNKNOWN = "Unknown"


class ToolService(Base):
    """Tool service registry model"""
    __tablename__ = "tool_services"

    # Primary key
    id = Column(String(50), primary_key=True, index=True)  # e.g., "balanço", "paisagismo", "askcad"

    # Core fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    version = Column(String(50), nullable=True)

    # Service location
    port = Column(Integer, nullable=False, unique=True)
    base_url = Column(String(500), nullable=True)  # e.g., http://localhost:8000
    health_check_url = Column(String(500), nullable=True)  # e.g., /api/health

    # Status and monitoring
    status = Column(SQLEnum(ServiceStatus), nullable=False, default=ServiceStatus.UNKNOWN, index=True)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_check_interval_seconds = Column(Integer, default=30)

    # Configuration
    endpoints_json = Column(JSON, default=dict)  # Supported endpoints and their documentation
    config_json = Column(JSON, default=dict)  # Service-specific configuration

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_tool_status', 'status'),
        Index('idx_tool_port', 'port'),
    )

    def __repr__(self):
        return f"<ToolService {self.id}: {self.name}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "port": self.port,
            "base_url": self.base_url,
            "health_check_url": self.health_check_url,
            "status": self.status.value if isinstance(self.status, ServiceStatus) else self.status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "endpoints_json": self.endpoints_json or {},
            "config_json": self.config_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }
