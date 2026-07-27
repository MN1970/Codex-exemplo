"""
SQLAlchemy models for workflow management.

Provides data models for storing and managing agent workflows,
including workflow definitions, executions, and event histories.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
    Text,
    ForeignKey,
    Index,
    Enum,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from manta_backend.db import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow execution status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Workflow(Base):
    """
    Stores workflow definitions.

    Attributes:
        id: Unique workflow identifier
        org_id: Organization ID (multi-tenancy)
        name: Workflow name
        description: Long-form workflow description
        definition: JSON definition of workflow (nodes, edges, metadata)
        created_by: User ID of creator
        updated_by: User ID of last updater
        is_active: Whether workflow is active/available
        created_at: Creation timestamp
        updated_at: Last update timestamp
        version: Version number for tracking changes
    """
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(String(256), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # {nodes, edges, metadata}
    created_by = Column(String(256), nullable=False)
    updated_by = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow")
    versions = relationship("WorkflowVersion", back_populates="workflow")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_workflow_org_created", "org_id", "created_at"),
        Index("idx_workflow_org_active", "org_id", "is_active"),
        Index("idx_workflow_created", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "id": str(self.id),
            "org_id": self.org_id,
            "name": self.name,
            "description": self.description,
            "definition": self.definition,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }


class WorkflowVersion(Base):
    """
    Tracks workflow version history for auditing and rollback.

    Attributes:
        id: Unique version identifier
        workflow_id: Reference to parent workflow
        version: Version number
        definition: JSON definition at this version
        created_by: User who made the change
        created_at: Timestamp of version creation
        change_summary: Summary of changes made
    """
    __tablename__ = "workflow_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    version = Column(Integer, nullable=False)
    definition = Column(JSON, nullable=False)
    created_by = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary = Column(Text, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="versions")

    __table_args__ = (
        Index("idx_workflow_version_lookup", "workflow_id", "version"),
    )


class WorkflowExecution(Base):
    """
    Tracks workflow execution instances.

    Attributes:
        id: Unique execution identifier
        workflow_id: Reference to workflow definition
        user_id: User who initiated execution
        org_id: Organization ID
        status: Current execution status
        input_data: Input data provided to workflow
        output_data: Final output data (if completed)
        events: Array of execution events
        started_at: When execution started
        completed_at: When execution completed/failed
        error_message: Error message if failed
        metadata: Additional execution metadata
    """
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(String(256), nullable=False)
    org_id = Column(String(256), nullable=False, index=True)
    status = Column(
        Enum(WorkflowStatus),
        default=WorkflowStatus.PENDING,
        nullable=False,
        index=True
    )
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    events = Column(JSON, default=list, nullable=False)  # Array of events
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

    __table_args__ = (
        Index("idx_execution_workflow_status", "workflow_id", "status"),
        Index("idx_execution_org_user", "org_id", "user_id"),
        Index("idx_execution_started", "started_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary."""
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "user_id": self.user_id,
            "org_id": self.org_id,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "events": self.events,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class ExecutionEvent(Base):
    """
    Tracks individual events during workflow execution.

    Attributes:
        id: Unique event identifier
        execution_id: Reference to execution
        node_id: ID of node that triggered event
        event_type: Type of event (e.g., "node_started", "node_completed")
        timestamp: When event occurred
        data: Event-specific data (output, status, etc.)
        error: Error information if applicable
    """
    __tablename__ = "execution_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=False)
    node_id = Column(String(256), nullable=False)
    event_type = Column(String(128), nullable=False)  # node_started, node_completed, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_event_execution", "execution_id"),
        Index("idx_event_timestamp", "timestamp"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": str(self.id),
            "execution_id": str(self.execution_id),
            "node_id": self.node_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "error": self.error,
        }
