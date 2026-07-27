"""
FastAPI router for workflow management endpoints.

Provides REST API for creating, managing, and executing agent workflows.
Includes workflow definitions, execution tracking, and event streaming.
"""

from typing import List, Optional, Dict, Any, AsyncGenerator
from uuid import UUID
from datetime import datetime
import json
from enum import Enum

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    BackgroundTasks,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from manta_backend.db import get_db
from manta_backend.models.workflows import (
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
    ExecutionEvent,
    WorkflowVersion,
)
from manta_backend.auth import get_current_user

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ============================================================================
# Pydantic Models
# ============================================================================

class WorkflowNode(BaseModel):
    """Represents a node in the workflow graph."""
    id: str = Field(..., description="Unique node ID")
    type: str = Field(..., description="Node type: agent, condition, merger, start, end")
    agent_id: Optional[str] = Field(None, description="Agent ID for agent nodes")
    label: str = Field(..., description="Display label")
    position: Dict[str, float] = Field(default_factory=dict, description="x, y coordinates")
    config: Dict[str, Any] = Field(default_factory=dict, description="Node-specific configuration")
    handoff_conditions: Optional[List[Dict[str, Any]]] = Field(
        None, description="Conditions for routing output"
    )

    @validator("type")
    def validate_type(cls, v):
        valid_types = ["agent", "condition", "merger", "start", "end"]
        if v not in valid_types:
            raise ValueError(f"type must be one of {valid_types}")
        return v


class WorkflowEdge(BaseModel):
    """Represents a connection between nodes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique edge ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label (e.g., condition result)")
    condition: Optional[Dict[str, Any]] = Field(None, description="Routing condition")
    data: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata")


class WorkflowDef(BaseModel):
    """Complete workflow definition."""
    nodes: List[WorkflowNode] = Field(..., description="Workflow nodes")
    edges: List[WorkflowEdge] = Field(..., description="Workflow edges")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (tags, categories, etc.)"
    )


class WorkflowCreate(BaseModel):
    """Request to create a new workflow."""
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2048)
    definition: WorkflowDef


class WorkflowUpdate(BaseModel):
    """Request to update a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2048)
    definition: Optional[WorkflowDef] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    """Complete workflow response."""
    id: str
    org_id: str
    name: str
    description: Optional[str]
    definition: WorkflowDef
    created_by: str
    updated_by: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


class ExecutionInput(BaseModel):
    """Input for executing a workflow."""
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for workflow execution"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class ExecutionEventModel(BaseModel):
    """Event during workflow execution."""
    id: str
    execution_id: str
    node_id: str
    event_type: str
    timestamp: datetime
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """Workflow execution status and results."""
    id: str
    workflow_id: str
    user_id: str
    org_id: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    events: List[ExecutionEventModel]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    total: int
    page: int
    page_size: int
    items: List[WorkflowResponse]


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow",
)
async def create_workflow(
    request: WorkflowCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """
    Create a new workflow definition.

    - **name**: Workflow name
    - **description**: Optional description
    - **definition**: Workflow nodes, edges, and metadata
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization",
        )

    workflow = Workflow(
        org_id=org_id,
        name=request.name,
        description=request.description,
        definition=request.definition.dict(),
        created_by=current_user.get("user_id"),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return WorkflowResponse.from_orm(workflow)


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List workflows",
)
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or description"),
    is_active: Optional[bool] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse:
    """
    List workflows with pagination and filtering.

    - **page**: Page number (1-indexed)
    - **page_size**: Items per page
    - **search**: Optional text search
    - **is_active**: Filter by active status
    """
    org_id = current_user.get("org_id")
    query = db.query(Workflow).filter(Workflow.org_id == org_id)

    if is_active is not None:
        query = query.filter(Workflow.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Workflow.name.ilike(search_pattern)) |
            (Workflow.description.ilike(search_pattern))
        )

    total = query.count()
    workflows = (
        query.order_by(desc(Workflow.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[WorkflowResponse.from_orm(w) for w in workflows],
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow definition",
)
async def get_workflow(
    workflow_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """Retrieve a specific workflow definition."""
    org_id = current_user.get("org_id")
    workflow = (
        db.query(Workflow)
        .filter(and_(Workflow.id == workflow_id, Workflow.org_id == org_id))
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return WorkflowResponse.from_orm(workflow)


@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update workflow",
)
async def update_workflow(
    workflow_id: UUID,
    request: WorkflowUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """Update workflow definition and metadata."""
    org_id = current_user.get("org_id")
    workflow = (
        db.query(Workflow)
        .filter(and_(Workflow.id == workflow_id, Workflow.org_id == org_id))
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Save current version before updating
    old_definition = workflow.definition
    workflow.version += 1

    if request.name is not None:
        workflow.name = request.name
    if request.description is not None:
        workflow.description = request.description
    if request.definition is not None:
        workflow.definition = request.definition.dict()
    if request.is_active is not None:
        workflow.is_active = request.is_active

    workflow.updated_by = current_user.get("user_id")
    workflow.updated_at = datetime.utcnow()

    # Create version entry
    version_record = WorkflowVersion(
        workflow_id=workflow.id,
        version=workflow.version - 1,
        definition=old_definition,
        created_by=current_user.get("user_id"),
        change_summary="Workflow updated via API",
    )
    db.add(version_record)

    db.commit()
    db.refresh(workflow)

    return WorkflowResponse.from_orm(workflow)


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
)
async def delete_workflow(
    workflow_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete a workflow (sets is_active to False)."""
    org_id = current_user.get("org_id")
    workflow = (
        db.query(Workflow)
        .filter(and_(Workflow.id == workflow_id, Workflow.org_id == org_id))
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    workflow.is_active = False
    workflow.updated_by = current_user.get("user_id")
    workflow.updated_at = datetime.utcnow()
    db.commit()


@router.post(
    "/{workflow_id}/execute",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start workflow execution",
)
async def execute_workflow(
    workflow_id: UUID,
    request: ExecutionInput,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    """
    Start a new workflow execution.

    Returns execution ID for tracking progress via GET /workflows/executions/{execution_id}
    """
    org_id = current_user.get("org_id")
    workflow = (
        db.query(Workflow)
        .filter(and_(Workflow.id == workflow_id, Workflow.org_id == org_id))
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot execute inactive workflow",
        )

    execution = WorkflowExecution(
        workflow_id=workflow.id,
        user_id=current_user.get("user_id"),
        org_id=org_id,
        status=WorkflowStatus.PENDING,
        input_data=request.input_data,
        metadata=request.metadata,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Queue execution as background task
    background_tasks.add_task(
        _execute_workflow_task,
        execution_id=str(execution.id),
        workflow=workflow,
    )

    return ExecutionResponse.from_orm(execution)


@router.get(
    "/executions/{execution_id}",
    response_model=ExecutionResponse,
    summary="Track execution progress",
)
async def get_execution(
    execution_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    """Get execution status and event history."""
    execution = (
        db.query(WorkflowExecution)
        .filter(
            and_(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.org_id == current_user.get("org_id"),
            )
        )
        .first()
    )

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    # Reconstruct events from the events array
    events = []
    if execution.events:
        for event_data in execution.events:
            events.append(ExecutionEventModel(**event_data))

    response_dict = {
        "id": str(execution.id),
        "workflow_id": str(execution.workflow_id),
        "user_id": execution.user_id,
        "org_id": execution.org_id,
        "status": execution.status.value,
        "input_data": execution.input_data,
        "output_data": execution.output_data,
        "events": events,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "error_message": execution.error_message,
        "metadata": execution.metadata,
    }

    return ExecutionResponse(**response_dict)


@router.get(
    "/executions/{execution_id}/stream",
    summary="Stream execution events (SSE)",
)
async def stream_execution(
    execution_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream execution events via Server-Sent Events (SSE)."""
    execution = (
        db.query(WorkflowExecution)
        .filter(
            and_(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.org_id == current_user.get("org_id"),
            )
        )
        .first()
    )

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for workflow execution."""
        import time
        import asyncio

        last_event_count = 0
        while True:
            db.refresh(execution)

            # Send new events
            if execution.events and len(execution.events) > last_event_count:
                for event_data in execution.events[last_event_count:]:
                    event_json = json.dumps(event_data)
                    yield f"data: {event_json}\n\n"
                last_event_count = len(execution.events)

            # Send status update
            status_update = {
                "type": "status_update",
                "status": execution.status.value,
                "timestamp": datetime.utcnow().isoformat(),
            }
            yield f"data: {json.dumps(status_update)}\n\n"

            # If execution is complete, send final event
            if execution.status in (
                WorkflowStatus.COMPLETED,
                WorkflowStatus.FAILED,
                WorkflowStatus.CANCELLED,
            ):
                final_event = {
                    "type": "execution_complete",
                    "status": execution.status.value,
                    "output": execution.output_data,
                    "error": execution.error_message,
                }
                yield f"data: {json.dumps(final_event)}\n\n"
                break

            await asyncio.sleep(1)  # Poll interval

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ============================================================================
# Background Tasks
# ============================================================================

async def _execute_workflow_task(execution_id: str, workflow: Workflow) -> None:
    """
    Background task to execute a workflow.

    This is a simplified executor. In production, integrate with:
    - Agent invocation system
    - MCP tools
    - Event bus for real-time updates
    """
    from manta_backend.db import SessionLocal

    db = SessionLocal()
    try:
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()

        if not execution:
            return

        execution.status = WorkflowStatus.RUNNING
        execution.events = execution.events or []

        workflow_def = workflow.definition
        nodes = {node["id"]: node for node in workflow_def.get("nodes", [])}

        # Start with "start" nodes
        current_nodes = [n for n in nodes.values() if n.get("type") == "start"]

        output_data = {}

        # Simplified execution: process nodes in order
        for node in current_nodes:
            event = {
                "id": str(uuid.uuid4()),
                "execution_id": execution_id,
                "node_id": node["id"],
                "event_type": "node_started",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"label": node.get("label")},
                "error": None,
            }
            execution.events.append(event)

            try:
                # Process node based on type
                if node.get("type") == "agent":
                    # TODO: Call agent via MCP or API
                    node_output = {"status": "completed", "agent_id": node.get("agent_id")}
                elif node.get("type") == "condition":
                    node_output = {"condition_result": True}
                else:
                    node_output = {}

                output_data[node["id"]] = node_output

                completion_event = {
                    "id": str(uuid.uuid4()),
                    "execution_id": execution_id,
                    "node_id": node["id"],
                    "event_type": "node_completed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": node_output,
                    "error": None,
                }
                execution.events.append(completion_event)

            except Exception as e:
                error_event = {
                    "id": str(uuid.uuid4()),
                    "execution_id": execution_id,
                    "node_id": node["id"],
                    "event_type": "node_failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": None,
                    "error": {"message": str(e), "type": type(e).__name__},
                }
                execution.events.append(error_event)
                execution.status = WorkflowStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                db.commit()
                return

        execution.status = WorkflowStatus.COMPLETED
        execution.output_data = output_data
        execution.completed_at = datetime.utcnow()

    except Exception as e:
        execution.status = WorkflowStatus.FAILED
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()

    finally:
        db.commit()
        db.close()


import uuid
