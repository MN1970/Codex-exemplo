"""
tasks/feedback_analytics.py — Analytics semanal de feedback e alertas automáticos
para agentes com baixo desempenho.

Agendamento: rodar toda segunda-feira 09:00 UTC via APScheduler ou Celery.
Fluxo:
1. Agregação semanal: calcula avg_rating, std_dev, count por agent_slug
2. Trend detection: compara com semana anterior
3. Alertas: dispara se avg_rating < 3.5 por 2 semanas consecutivas
4. Retraining trigger: submete fine-tuning job automático se avg < 3.0 por 2 semanas
5. Slack notification: envia resumo para #agent-performance

Exporta:
    - run_feedback_analytics_pipeline(org_id: str | None) — entry point principal
    - compute_agent_stats() — agregação por agent
    - detect_trend() — comparação semana vs semana anterior
    - trigger_retraining_job() — submete job LoRA se necessário
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    Agent,
    Feedback,
    FeedbackAlert,
    Organization,
    SessionLocal,
    set_org_context,
)

logger = logging.getLogger("manta.feedback_analytics")

# Threshold padrão: agente é alerta se avg_rating cair abaixo disto
DEFAULT_ALERT_THRESHOLD = 3.5
# Threshold crítico: dispara retraining automático se avg < isto por 2 semanas
RETRAINING_THRESHOLD = 3.0


class AgentStats:
    """Agregação semanal de feedback para um agente."""

    def __init__(
        self,
        agent_slug: str,
        avg_rating: float,
        feedback_count: int,
        std_dev: float | None = None,
        trend: str = "stable",
        week_start: datetime | None = None,
    ):
        self.agent_slug = agent_slug
        self.avg_rating = avg_rating
        self.feedback_count = feedback_count
        self.std_dev = std_dev
        self.trend = trend
        self.week_start = week_start or datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"<AgentStats slug={self.agent_slug!r} avg={self.avg_rating:.2f} "
            f"count={self.feedback_count} trend={self.trend!r}>"
        )


async def compute_agent_stats(
    session: AsyncSession, agent_id: str, weeks_back: int = 1
) -> AgentStats | None:
    """Computa avg_rating, std_dev, count para um agente nos últimos
    `weeks_back` semanas (padrão 1 = última semana completa).

    Retorna None se nenhum feedback no período.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks_back)

    # Agregação SQL: avg(rating), stddev(rating), count
    stmt = (
        select(
            func.avg(Feedback.rating).label("avg_rating"),
            func.stddev(Feedback.rating).label("std_dev"),
            func.count(Feedback.id).label("count"),
        )
        .where(Feedback.agent_id == agent_id)
        .where(Feedback.created_at >= cutoff_date)
    )

    result = await session.execute(stmt)
    row = result.first()

    if row and row[2] > 0:  # count > 0
        return AgentStats(
            agent_slug=(await session.execute(select(Agent.slug).where(Agent.id == agent_id))).scalar_one_or_none()
            or "unknown",
            avg_rating=float(row[0]) if row[0] is not None else 0.0,
            feedback_count=int(row[2]),
            std_dev=float(row[1]) if row[1] is not None else None,
        )
    return None


async def detect_trend(
    session: AsyncSession, agent_id: str, current_week: AgentStats, threshold: float = 3.5
) -> str:
    """Compara avg_rating desta semana com semana anterior,
    retorna "up", "down" ou "stable"."""

    prev_week_stats = await compute_agent_stats(session, agent_id, weeks_back=2)
    if prev_week_stats is None:
        return "stable"

    delta = current_week.avg_rating - prev_week_stats.avg_rating
    if delta > 0.2:
        return "up"
    elif delta < -0.2:
        return "down"
    return "stable"


async def trigger_retraining_job(
    session: AsyncSession, org_id: str, agent_id: str, agent_slug: str
) -> dict[str, Any]:
    """Submete um FineTuneJob automático para um agente com avg_rating
    < RETRAINING_THRESHOLD por 2 semanas. Retorna metadata do job criado.

    Nota: isso integra com ml/finetuning.py — ver imports lá."""

    # Para não criar dependência circular, importa lazy aqui
    try:
        from database import FineTuneJob

        # Extrai segment do slug do agente (ex: "agente-saneamento" -> "saneamento")
        segment = agent_slug.replace("agente-", "").replace("-", "_")

        job = FineTuneJob(
            org_id=org_id,
            segment=segment,
            base_model="mistralai/Mistral-7B-v0.1",
            epochs=3,
            status="queued",
        )
        session.add(job)
        await session.flush()

        logger.info(
            "Retraining job submitted for agent_slug=%s (job_id=%s)",
            agent_slug,
            job.id,
        )

        return {
            "job_id": job.id,
            "segment": segment,
            "status": "queued",
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
    except Exception as e:
        logger.error("Failed to submit retraining job: %s", e)
        return {"error": str(e)}


async def run_feedback_analytics_pipeline(org_id: str | None = None) -> dict[str, Any]:
    """Entry point principal: roda aggregação semanal, detecta alertas,
    dispara retraining se necessário, e notifica via Slack.

    Se org_id é None, roda para TODAS as organizações.

    Retorna stats: número de agentes analisados, alertas disparados, etc.
    """

    async with SessionLocal() as session:
        if org_id:
            await set_org_context(session, org_id)

        # Busca todas as organizações ativas se org_id for None
        if org_id is None:
            stmt = select(Organization.id).where(Organization.is_active is True)
            org_ids = (await session.execute(stmt)).scalars().all()
        else:
            org_ids = [org_id]

        total_agents_analyzed = 0
        total_alerts_triggered = 0
        alerts_created = []

        for current_org_id in org_ids:
            # Seta contexto RLS se rodando multi-org
            if org_id is None:
                await set_org_context(session, current_org_id)

            # Busca todos os agents desta org
            stmt = select(Agent.id, Agent.slug).where(Agent.org_id == current_org_id)
            agents = (await session.execute(stmt)).all()

            for agent_id, agent_slug in agents:
                total_agents_analyzed += 1
                stats = await compute_agent_stats(session, agent_id, weeks_back=1)

                if stats is None:
                    logger.debug("No feedback for agent_slug=%s", agent_slug)
                    continue

                # Detecta trend
                trend = await detect_trend(session, agent_id, stats)
                stats.trend = trend

                logger.info(
                    "Agent analytics: %s (avg=%.2f, count=%d, trend=%s)",
                    agent_slug,
                    stats.avg_rating,
                    stats.feedback_count,
                    trend,
                )

                # Verifica se deve disparar alerta
                if stats.avg_rating < DEFAULT_ALERT_THRESHOLD:
                    # Conta quantas semanas consecutivas está abaixo
                    weeks_below = 0
                    for weeks_back in [1, 2, 3]:
                        check_stats = await compute_agent_stats(
                            session, agent_id, weeks_back=weeks_back
                        )
                        if check_stats and check_stats.avg_rating < DEFAULT_ALERT_THRESHOLD:
                            weeks_below = weeks_back
                        else:
                            break

                    if weeks_below >= 2:
                        # Dispara alerta
                        action = "slack_notified"
                        metadata: dict[str, Any] = {
                            "weeks_below_threshold": weeks_below,
                            "prev_rating": None,
                        }

                        # Se está crítico, submete retraining também
                        if stats.avg_rating < RETRAINING_THRESHOLD:
                            retraining_result = await trigger_retraining_job(
                                session, current_org_id, agent_id, agent_slug
                            )
                            action = "retraining_job_submitted"
                            metadata["retraining"] = retraining_result

                        alert = FeedbackAlert(
                            org_id=current_org_id,
                            agent_id=agent_id,
                            agent_slug=agent_slug,
                            avg_rating=stats.avg_rating,
                            feedback_count=stats.feedback_count,
                            trend=trend,
                            threshold=DEFAULT_ALERT_THRESHOLD,
                            action_taken=action,
                            metadata=metadata,
                        )
                        session.add(alert)
                        await session.flush()

                        total_alerts_triggered += 1
                        alerts_created.append(
                            {
                                "agent_slug": agent_slug,
                                "avg_rating": stats.avg_rating,
                                "action": action,
                            }
                        )

                        logger.warning(
                            "ALERT: agent_slug=%s avg_rating=%.2f (action=%s)",
                            agent_slug,
                            stats.avg_rating,
                            action,
                        )

        await session.commit()

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents_analyzed": total_agents_analyzed,
            "alerts_triggered": total_alerts_triggered,
            "alerts": alerts_created,
        }

        logger.info("Feedback analytics pipeline completed: %s", result)
        return result


# Placeholder para Slack notification (integrar com routers/webhooks se necessário)
async def send_slack_alert(agent_slug: str, avg_rating: float, action: str) -> None:
    """Envia alerta para #agent-performance (placeholder)."""
    message = (
        f":warning: Agent `{agent_slug}` avg rating: {avg_rating:.2f} "
        f"(action: {action})"
    )
    logger.info("Slack alert (placeholder): %s", message)
    # TODO: integrar com requests.post(SLACK_WEBHOOK_URL, json={...})
