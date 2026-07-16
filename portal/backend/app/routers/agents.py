"""
FastAPI router for Agent management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.agent import AgentStatus, AgentTier, AgentEixo
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse,
    AgentDetailResponse,
    ErrorResponse,
)
from app.db import agent as agent_db

router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.get("", response_model=AgentListResponse)
async def list_agents(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    eixo: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """
    List all agents with optional filtering and pagination.

    Query parameters:
    - limit: Number of agents per page (default: 100, max: 500)
    - offset: Starting position for pagination (default: 0)
    - eixo: Filter by eixo (Horizontal, Vertical, Lifecycle)
    - status: Filter by status (Operacional, Beta, etc.)
    - tier: Filter by tier (Haiku, Sonnet, Opus, etc.)
    - search: Search term for name or code
    """
    try:
        # Parse enum filters
        eixo_enum = None
        if eixo:
            try:
                eixo_enum = AgentEixo[eixo.upper().replace("-", "_")]
            except KeyError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid eixo: {eixo}. Must be one of: {', '.join(e.name for e in AgentEixo)}"
                )

        status_enum = None
        if status:
            # Convert status string to enum
            for s in AgentStatus:
                if s.value.lower() == status.lower():
                    status_enum = s
                    break
            if not status_enum:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid status: {status}. Must be one of: {', '.join(s.value for s in AgentStatus)}"
                )

        tier_enum = None
        if tier:
            # Convert tier string to enum
            for t in AgentTier:
                if t.value.lower() == tier.lower():
                    tier_enum = t
                    break
            if not tier_enum:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid tier: {tier}. Must be one of: {', '.join(t.value for t in AgentTier)}"
                )

        # Search or filter
        if search:
            agents = agent_db.search_agents(db, search)
            total = len(agents)
            agents = agents[offset : offset + limit]
        else:
            agents, total = agent_db.get_agents(
                db, limit=limit, offset=offset, eixo=eixo_enum, status=status_enum, tier=tier_enum
            )

        # Convert to response
        agent_responses = [AgentResponse.model_validate(agent.to_dict()) for agent in agents]

        return AgentListResponse(
            agents=agent_responses,
            total=total,
            limit=limit,
            offset=offset,
            filters={
                "eixo": eixo,
                "status": status,
                "tier": tier,
                "search": search,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Get a specific agent by ID.
    """
    try:
        agent = agent_db.get_agent_by_id(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        agent_response = AgentResponse.model_validate(agent.to_dict())
        return AgentDetailResponse(agent=agent_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=AgentDetailResponse, status_code=201)
async def create_agent(
    agent_create: AgentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new agent.

    Body parameters:
    - id: Unique identifier for the agent (e.g., "manta-00", "manta-03-s8")
    - name: Human-readable name
    - code: Agent code (e.g., "Manta 00", "Manta 03-S8")
    - aliases: List of alternative names
    - description: Description of the agent
    - eixo: Classification (Horizontal, Vertical, Lifecycle)
    - tier: Model tier (Haiku, Sonnet, Opus, etc.)
    - status: Operational status (default: Operacional)
    - service_url: URL to agent service or documentation
    - routing_keywords: Keywords for automatic routing
    - created_by: Username of creator
    """
    try:
        agent = agent_db.create_agent(db, agent_create)
        agent_response = AgentResponse.model_validate(agent.to_dict())
        return AgentDetailResponse(agent=agent_response)

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{agent_id}", response_model=AgentDetailResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing agent.

    Only provided fields will be updated.
    """
    try:
        agent = agent_db.update_agent(db, agent_id, agent_update)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        agent_response = AgentResponse.model_validate(agent.to_dict())
        return AgentDetailResponse(agent=agent_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Delete (archive) an agent by setting status to INATIVO.

    This is a soft delete. Use hard_delete for permanent removal.
    """
    try:
        success = agent_db.delete_agent(db, agent_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/by-eixo/{eixo}", response_model=AgentListResponse)
async def get_agents_by_eixo(
    eixo: str,
    db: Session = Depends(get_db),
):
    """
    Get all agents for a specific eixo.
    """
    try:
        try:
            eixo_enum = AgentEixo[eixo.upper().replace("-", "_")]
        except KeyError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid eixo: {eixo}. Must be one of: {', '.join(e.name for e in AgentEixo)}"
            )

        agents = agent_db.list_agents_by_eixo(db, eixo_enum)
        agent_responses = [AgentResponse.model_validate(agent.to_dict()) for agent in agents]

        return AgentListResponse(
            agents=agent_responses,
            total=len(agents),
            limit=len(agents),
            offset=0,
            filters={"eixo": eixo}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/by-status/{status}", response_model=AgentListResponse)
async def get_agents_by_status(
    status: str,
    db: Session = Depends(get_db),
):
    """
    Get all agents with a specific status.
    """
    try:
        status_enum = None
        for s in AgentStatus:
            if s.value.lower() == status.lower():
                status_enum = s
                break

        if not status_enum:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status: {status}. Must be one of: {', '.join(s.value for s in AgentStatus)}"
            )

        agents = agent_db.list_agents_by_status(db, status_enum)
        agent_responses = [AgentResponse.model_validate(agent.to_dict()) for agent in agents]

        return AgentListResponse(
            agents=agent_responses,
            total=len(agents),
            limit=len(agents),
            offset=0,
            filters={"status": status}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
