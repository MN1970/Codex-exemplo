"""
Database operations for Agent model
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.models.agent import Agent, AgentStatus, AgentTier, AgentEixo
from app.schemas.agent import AgentCreate, AgentUpdate


def get_agent_by_id(db: Session, agent_id: str) -> Optional[Agent]:
    """Get agent by ID"""
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_code(db: Session, code: str) -> Optional[Agent]:
    """Get agent by code"""
    return db.query(Agent).filter(Agent.code == code).first()


def get_agents(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    eixo: Optional[AgentEixo] = None,
    status: Optional[AgentStatus] = None,
    tier: Optional[AgentTier] = None,
) -> tuple[List[Agent], int]:
    """Get agents with filtering and pagination"""
    query = db.query(Agent)

    # Apply filters
    if eixo:
        query = query.filter(Agent.eixo == eixo)
    if status:
        query = query.filter(Agent.status == status)
    if tier:
        query = query.filter(Agent.tier == tier)

    # Get total count before pagination
    total = query.count()

    # Apply pagination and sorting
    agents = query.order_by(desc(Agent.created_at)).offset(offset).limit(limit).all()

    return agents, total


def create_agent(db: Session, agent_create: AgentCreate) -> Agent:
    """Create a new agent"""
    # Check if agent with same ID already exists
    existing = db.query(Agent).filter(Agent.id == agent_create.id).first()
    if existing:
        raise ValueError(f"Agent with ID '{agent_create.id}' already exists")

    # Check if agent with same code already exists
    existing_code = db.query(Agent).filter(Agent.code == agent_create.code).first()
    if existing_code:
        raise ValueError(f"Agent with code '{agent_create.code}' already exists")

    db_agent = Agent(
        id=agent_create.id,
        name=agent_create.name,
        code=agent_create.code,
        aliases=agent_create.aliases or [],
        description=agent_create.description,
        eixo=agent_create.eixo,
        tier=agent_create.tier,
        status=agent_create.status or AgentStatus.OPERACIONAL,
        service_url=agent_create.service_url,
        routing_keywords=agent_create.routing_keywords or [],
        created_by=agent_create.created_by,
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(
    db: Session, agent_id: str, agent_update: AgentUpdate
) -> Optional[Agent]:
    """Update an existing agent"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return None

    # Update fields if provided
    update_data = agent_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_agent, field, value)

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: str) -> bool:
    """Delete an agent (soft delete by archiving)"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return False

    # Soft delete: set status to inactive
    db_agent.status = AgentStatus.INATIVO
    db.add(db_agent)
    db.commit()
    return True


def hard_delete_agent(db: Session, agent_id: str) -> bool:
    """Permanently delete an agent from database"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return False

    db.delete(db_agent)
    db.commit()
    return True


def list_agents_by_eixo(db: Session, eixo: AgentEixo) -> List[Agent]:
    """Get all agents for a specific eixo"""
    return (
        db.query(Agent)
        .filter(Agent.eixo == eixo)
        .order_by(Agent.code)
        .all()
    )


def list_agents_by_status(db: Session, status: AgentStatus) -> List[Agent]:
    """Get all agents with a specific status"""
    return (
        db.query(Agent)
        .filter(Agent.status == status)
        .order_by(Agent.code)
        .all()
    )


def search_agents(db: Session, search_term: str) -> List[Agent]:
    """Search agents by name, code, or aliases"""
    search_pattern = f"%{search_term}%"
    return (
        db.query(Agent)
        .filter(
            Agent.name.ilike(search_pattern)
            | Agent.code.ilike(search_pattern)
        )
        .order_by(Agent.code)
        .all()
    )


def get_agent_count(db: Session) -> int:
    """Get total count of agents"""
    return db.query(Agent).count()
