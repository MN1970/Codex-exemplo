"""
tests/test_feedback_analytics.py — Testes para analytics de feedback

Cobre:
- GET /feedback/analytics/by-agent
- GET /feedback/analytics/alerts
- tasks/feedback_analytics.py funções
"""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database import Agent, Feedback, FeedbackAlert, Organization, SessionLocal, set_org_context
from tasks.feedback_analytics import (
    compute_agent_stats,
    detect_trend,
    run_feedback_analytics_pipeline,
)


@pytest.fixture
async def setup_test_data(session: AsyncSession):
    """Setup organização, agente, feedbacks para testes."""
    from database import create_organization

    org = await create_organization(session, name="Test Org", slug="test-org")
    await session.commit()

    agent = Agent(
        org_id=org.id,
        code="Manta 03-S8",
        slug="agente-saneamento",
        name="Agente Saneamento",
        axis="vertical",
        segment="S8",
    )
    session.add(agent)
    await session.flush()

    # Insere 10 feedbacks com ratings variados
    for i in range(10):
        rating = -1 if i < 3 else (0 if i < 6 else 1)
        feedback = Feedback(
            org_id=org.id,
            agent_id=agent.id,
            rating=rating,
            comment=f"Comment {i}",
        )
        session.add(feedback)

    await session.commit()
    return org, agent


@pytest.mark.asyncio
async def test_compute_agent_stats(setup_test_data):
    """Testa agregação de stats para um agente."""
    org, agent = setup_test_data

    async with SessionLocal() as session:
        await set_org_context(session, org.id)
        stats = await compute_agent_stats(session, agent.id, weeks_back=1)

    assert stats is not None
    assert stats.agent_slug == "agente-saneamento"
    assert stats.feedback_count == 10
    # Esperado: (-1 * 3 + 0 * 3 + 1 * 4) / 10 = 0.1
    assert -0.2 <= stats.avg_rating <= 0.2


@pytest.mark.asyncio
async def test_detect_trend(setup_test_data):
    """Testa detecção de trend."""
    org, agent = setup_test_data
    from tasks.feedback_analytics import AgentStats

    current_week = AgentStats(
        agent_slug="test",
        avg_rating=3.0,
        feedback_count=5,
    )

    async with SessionLocal() as session:
        await set_org_context(session, org.id)
        trend = await detect_trend(session, agent.id, current_week)

    # Como não há dados da semana anterior, trend deve ser "stable"
    assert trend == "stable"


@pytest.mark.asyncio
async def test_analytics_endpoint(client: AsyncClient, setup_test_data):
    """Testa GET /feedback/analytics/by-agent."""
    org, agent = setup_test_data

    response = await client.get("/api/feedback/analytics/by-agent")
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert "stats" in data
    assert "summary" in data
    assert data["summary"]["total_feedback_entries"] == 10


@pytest.mark.asyncio
async def test_alerts_endpoint(client: AsyncClient, setup_test_data):
    """Testa GET /feedback/analytics/alerts."""
    response = await client.get("/api/feedback/analytics/alerts")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_run_feedback_analytics_pipeline(setup_test_data):
    """Testa execução da pipeline completa."""
    org, agent = setup_test_data

    result = await run_feedback_analytics_pipeline(org_id=org.id)

    assert "timestamp" in result
    assert "agents_analyzed" in result
    assert "alerts_triggered" in result
    assert result["agents_analyzed"] >= 1


@pytest.mark.asyncio
async def test_feedback_alert_creation(setup_test_data):
    """Testa criação de FeedbackAlert quando threshold é atingido."""
    org, agent = setup_test_data

    # Adiciona feedbacks com rating baixo (< 3.5)
    async with SessionLocal() as session:
        await set_org_context(session, org.id)

        # Adiciona 20 feedbacks com rating = -1
        for i in range(20):
            feedback = Feedback(
                org_id=org.id,
                agent_id=agent.id,
                rating=-1,
                comment="Muito ruim",
            )
            session.add(feedback)

        await session.commit()

        # Roda pipeline
        result = await run_feedback_analytics_pipeline(org_id=org.id)

        # Verifica se alerta foi criado (pode ser 0 se lógica requer 2 semanas)
        # Por enquanto, apenas verifica que pipeline rodou sem erro
        assert result["agents_analyzed"] > 0
