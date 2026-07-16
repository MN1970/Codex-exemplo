"""
SQLAlchemy ORM model for SyncEvent
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Index, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class SyncEventType(str, enum.Enum):
    """Sync event type"""
    AGENT_REGISTERED = "AgentRegistered"
    AGENT_UPDATED = "AgentUpdated"
    AGENT_DELETED = "AgentDeleted"
    TOOL_REGISTERED = "ToolRegistered"
    TOOL_UPDATED = "ToolUpdated"
    TOOL_STATUS_CHANGED = "ToolStatusChanged"
    KNOWLEDGE_SYNCED = "KnowledgeSynced"
    CONFIGURATION_UPDATED = "ConfigurationUpdated"
    SYNC_ERROR = "SyncError"


class SyncDirection(str, enum.Enum):
    """Direction of synchronization"""
    PULL = "Pull"  # From Manta Hub to Portal
    PUSH = "Push"  # From Portal to Manta Hub
    BIDIRECTIONAL = "Bidirectional"


class SyncEventStatus(str, enum.Enum):
    """Sync event execution status"""
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    SUCCESS = "Success"
    PARTIAL_SUCCESS = "PartialSuccess"
    FAILED = "Failed"


class SyncEvent(Base):
    """Synchronization event log model"""
    __tablename__ = "sync_events"

    # Primary key
    id = Column(String(100), primary_key=True, index=True)

    # Event details
    event_type = Column(SQLEnum(SyncEventType), nullable=False, index=True)
    direction = Column(SQLEnum(SyncDirection), nullable=False, index=True)
    status = Column(SQLEnum(SyncEventStatus), nullable=False, default=SyncEventStatus.PENDING, index=True)

    # Source information
    source = Column(String(255), nullable=False)  # "manta-hub", "local", etc.
    source_system_id = Column(String(255), nullable=True)

    # Sync details
    items_synced = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    items_skipped = Column(Integer, default=0)

    # Payload and results
    payload_json = Column(JSON, nullable=True)  # The data that was synced
    metadata_json = Column(JSON, default=dict)  # Additional context
    error_message = Column(Text, nullable=True)  # Error details if failed
    result_json = Column(JSON, nullable=True)  # Result details

    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Tracking
    duration_seconds = Column(Integer, nullable=True)
    triggered_by = Column(String(255), nullable=True)  # User or system that triggered sync
    correlation_id = Column(String(100), nullable=True)  # For tracking related syncs

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_sync_timestamp', 'timestamp'),
        Index('idx_sync_status', 'status'),
        Index('idx_sync_event_type', 'event_type'),
        Index('idx_sync_direction', 'direction'),
        Index('idx_sync_source', 'source'),
        Index('idx_sync_correlation_id', 'correlation_id'),
    )

    def __repr__(self):
        return f"<SyncEvent {self.id}: {self.event_type.value} - {self.status.value}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type.value if isinstance(self.event_type, SyncEventType) else self.event_type,
            "direction": self.direction.value if isinstance(self.direction, SyncDirection) else self.direction,
            "status": self.status.value if isinstance(self.status, SyncEventStatus) else self.status,
            "source": self.source,
            "source_system_id": self.source_system_id,
            "items_synced": self.items_synced,
            "items_failed": self.items_failed,
            "items_skipped": self.items_skipped,
            "payload_json": self.payload_json,
            "metadata_json": self.metadata_json or {},
            "error_message": self.error_message,
            "result_json": self.result_json,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "triggered_by": self.triggered_by,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
