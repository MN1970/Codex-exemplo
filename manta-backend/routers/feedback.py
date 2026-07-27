"""
routers/feedback.py — Captura de feedback de uso dos agentes
(thumbs up/down, comentário livre), para loop de melhoria contínua do
Maestro. Persiste em Postgres (tabela `agent_feedback`); se o DB não
estiver disponível, aceita o feedback em memória (fallback dev-only)
em vez de falhar o request.

Novos endpoints (INICIATIVA 3 — Feedback Analytics):
- GET /feedback/analytics/by-agent: agregação semanal por agente
  (avg_rating, trend, feedback_count, tags frequentes negativas)
- GET /feedback/analytics/alerts: lista alertas disparados (low-rated agents)
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Agent, Feedback, FeedbackAlert, Organization, SessionLocal
from pg_pool import acquire_optional

logger = logging.getLogger("manta.feedback")
router = APIRouter(prefix="/feedback", tags=["feedback"])

# Fallback em memória, apenas para o skeleton funcionar sem banco.
_MEMORY_STORE: List["FeedbackRecord"] = []


class FeedbackIn(BaseModel):
    agent_code: str
    rating: int = Field(..., ge=-1, le=1, description="-1 = ruim, 0 = neutro, 1 = bom")
    comment: Optional[str] = None
    user_email: Optional[str] = None


class FeedbackRecord(FeedbackIn):
    id: str
    created_at: datetime


class AgentAnalyticsStat(BaseModel):
    """Estatísticas semanais agregadas de um agente."""

    agent_slug: str
    agent_code: Optional[str] = None
    avg_rating: float
    feedback_count: int
    std_dev: Optional[float] = None
    trend: str = "stable"  # up|down|stable
    rating_distribution: dict[str, int] = {}  # "-1": count, "0": count, "1": count
    negative_comment_tags: List[str] = []  # palavras frequentes em comentários negativos


class FeedbackAlertInfo(BaseModel):
    """Informação de alerta disparado."""

    id: str
    agent_slug: str
    agent_code: Optional[str] = None
    avg_rating: float
    feedback_count: int
    trend: str
    threshold: float
    action_taken: str
    triggered_at: datetime
    metadata: dict[str, Any] = {}


class FeedbackAnalyticsResponse(BaseModel):
    """Resposta agregada do GET /feedback/analytics/by-agent."""

    timestamp: datetime
    stats: List[AgentAnalyticsStat]
    summary: dict[str, Any] = {}


@router.post("", response_model=FeedbackRecord, summary="Registra feedback sobre um agente")
async def submit_feedback(payload: FeedbackIn, request: Request) -> FeedbackRecord:
    record = FeedbackRecord(
        id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )

    async with acquire_optional(request) as conn:
        if conn is not None:
            await conn.execute(
                """
                INSERT INTO agent_feedback (id, agent_code, rating, comment, user_email, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                record.id, record.agent_code, record.rating,
                record.comment, record.user_email, record.created_at,
            )
        else:
            logger.info("feedback: DB indisponível, guardando em memória (%s)", record.id)
            _MEMORY_STORE.append(record)

    return record


@router.get("", response_model=List[FeedbackRecord], summary="Lista feedback recente (fallback em memória)")
async def list_feedback(limit: int = 50) -> List[FeedbackRecord]:
    return _MEMORY_STORE[-limit:]


@router.get(
    "/analytics/by-agent",
    response_model=FeedbackAnalyticsResponse,
    summary="Estatísticas semanais agregadas por agente",
)
async def get_analytics_by_agent(
    org_id: Optional[str] = None,
    weeks_back: int = 1,
    session: AsyncSession = Depends(SessionLocal),
) -> FeedbackAnalyticsResponse:
    """
    Retorna analytics agregadas por agente (última semana por padrão).

    Métricas por agente:
    - avg_rating: rating médio (-1 a 1)
    - feedback_count: número de feedback registrados
    - std_dev: desvio padrão
    - trend: "up", "down", "stable" (comparado com semana anterior)
    - rating_distribution: contagem de ratings por valor
    - negative_comment_tags: palavras frequentes em comentários negativos

    Query params:
    - org_id: filtrar por organização (padrão: global)
    - weeks_back: quantas semanas atrás? (padrão: 1 = última semana)
    """

    cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks_back)

    # Busca todos os agents (filtrado por org_id se fornecido)
    query = select(Agent.id, Agent.slug, Agent.code)
    if org_id:
        query = query.where(Agent.org_id == org_id)
    agents = (await session.execute(query)).all()

    stats_list: List[AgentAnalyticsStat] = []
    total_feedback = 0
    alerts_count = 0

    for agent_id, agent_slug, agent_code in agents:
        # Agregação de feedback
        agg_stmt = select(
            func.avg(Feedback.rating).label("avg_rating"),
            func.stddev(Feedback.rating).label("std_dev"),
            func.count(Feedback.id).label("count"),
        ).where(and_(Feedback.agent_id == agent_id, Feedback.created_at >= cutoff_date))

        agg_result = (await session.execute(agg_stmt)).first()

        if agg_result is None or agg_result[2] == 0:
            continue

        avg_rating = float(agg_result[0]) if agg_result[0] is not None else 0.0
        std_dev = float(agg_result[1]) if agg_result[1] is not None else None
        feedback_count = int(agg_result[2])

        # Rating distribution
        dist_stmt = (
            select(Feedback.rating, func.count(Feedback.id).label("cnt"))
            .where(and_(Feedback.agent_id == agent_id, Feedback.created_at >= cutoff_date))
            .group_by(Feedback.rating)
        )
        dist_rows = (await session.execute(dist_stmt)).all()
        rating_dist = {str(r[0]): r[1] for r in dist_rows}

        # Negative comment tags (placeholder: extrai palavras de comentários com rating=-1)
        negative_tags: List[str] = []
        if feedback_count > 0:
            comment_stmt = select(Feedback.comment).where(
                and_(
                    Feedback.agent_id == agent_id,
                    Feedback.rating == -1,
                    Feedback.created_at >= cutoff_date,
                    Feedback.comment.isnot(None),
                )
            )
            comments = (await session.execute(comment_stmt)).scalars().all()
            # TODO: implementar extração de tags via NLP (word frequency, etc.)
            # Por enquanto, placeholder
            negative_tags = []

        # Trend detection (compara com semana anterior)
        prev_cutoff = cutoff_date - timedelta(weeks=1)
        prev_agg_stmt = select(
            func.avg(Feedback.rating).label("avg_rating"),
        ).where(
            and_(
                Feedback.agent_id == agent_id,
                Feedback.created_at >= prev_cutoff,
                Feedback.created_at < cutoff_date,
            )
        )
        prev_result = (await session.execute(prev_agg_stmt)).first()
        prev_avg = float(prev_result[0]) if prev_result and prev_result[0] is not None else None

        trend = "stable"
        if prev_avg is not None:
            delta = avg_rating - prev_avg
            if delta > 0.2:
                trend = "up"
            elif delta < -0.2:
                trend = "down"

        stat = AgentAnalyticsStat(
            agent_slug=agent_slug,
            agent_code=agent_code,
            avg_rating=avg_rating,
            feedback_count=feedback_count,
            std_dev=std_dev,
            trend=trend,
            rating_distribution=rating_dist,
            negative_comment_tags=negative_tags,
        )
        stats_list.append(stat)
        total_feedback += feedback_count

    # Resumo
    summary = {
        "total_agents_analyzed": len(agents),
        "agents_with_feedback": len(stats_list),
        "total_feedback_entries": total_feedback,
        "avg_rating_all_agents": (
            float(sum(s.avg_rating for s in stats_list) / len(stats_list)) if stats_list else 0.0
        ),
    }

    return FeedbackAnalyticsResponse(timestamp=datetime.now(timezone.utc), stats=stats_list, summary=summary)


@router.get(
    "/analytics/alerts",
    response_model=List[FeedbackAlertInfo],
    summary="Lista alertas disparados (agentes com baixo desempenho)",
)
async def get_feedback_alerts(
    org_id: Optional[str] = None,
    limit: int = 50,
    session: AsyncSession = Depends(SessionLocal),
) -> List[FeedbackAlertInfo]:
    """
    Retorna alertas disparados nas últimas 4 semanas.

    Query params:
    - org_id: filtrar por organização
    - limit: máximo de alertas a retornar (padrão: 50)
    """

    cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=4)

    query = select(FeedbackAlert).where(FeedbackAlert.triggered_at >= cutoff_date)
    if org_id:
        query = query.where(FeedbackAlert.org_id == org_id)
    query = query.order_by(desc(FeedbackAlert.triggered_at)).limit(limit)

    alerts = (await session.execute(query)).scalars().all()

    # Enriquece com agent_code (FK opcional)
    result: List[FeedbackAlertInfo] = []
    for alert in alerts:
        agent_code = None
        if alert.agent_id:
            agent = await session.execute(select(Agent.code).where(Agent.id == alert.agent_id))
            agent_code = agent.scalar_one_or_none()

        result.append(
            FeedbackAlertInfo(
                id=alert.id,
                agent_slug=alert.agent_slug,
                agent_code=agent_code,
                avg_rating=alert.avg_rating,
                feedback_count=alert.feedback_count,
                trend=alert.trend,
                threshold=alert.threshold,
                action_taken=alert.action_taken,
                triggered_at=alert.triggered_at,
                metadata=alert.metadata,
            )
        )

    return result
