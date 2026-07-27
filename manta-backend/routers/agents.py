"""
routers/agents.py — Registro de agentes (espelha o mapa do CLAUDE.md
master: agentes em 3 eixos — horizontais, verticais por segmento,
ciclo de vida) + endpoint de invocação (streaming SSE) usado pelo
Canvas do frontend.

Em produção este catálogo viria do Supabase (tabela `agents`); aqui
está embutido como fixture para o skeleton subir sem dependências.

O endpoint `/agents/{slug}/invoke` simula a chamada real ao modelo do
agente (não há integração com um provider LLM neste skeleton) mas
implementa o contrato de ponta a ponta que o Canvas espera: streaming
via Server-Sent Events e persistência da sessão completa (prompt +
resposta) — em Postgres quando o pool está disponível, com fallback em
memória (mesmo padrão de `routers/feedback.py`).
"""
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from pg_pool import acquire_optional

logger = logging.getLogger("manta.agents")
router = APIRouter(prefix="/agents", tags=["agents"])


class AgentStatus(str, Enum):
    operacional = "operacional"
    parcial = "parcial"
    planejado = "planejado"


class Agent(BaseModel):
    code: str
    slug: str
    name: str
    aliases: List[str] = []
    tier: str
    status: AgentStatus
    axis: str  # "horizontal" | "vertical" | "lifecycle"


AGENT_REGISTRY: List[Agent] = [
    # Eixo 1 — Horizontais
    Agent(code="Manta 00", slug="maestro", name="maestro", aliases=["maestro", "manta-router"], tier="Haiku→Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 01", slug="claims", name="claims", aliases=["02-C", "manta-claims"], tier="Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 02", slug="contratual", name="contratual", aliases=["manta-02", "contratual"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 04", slug="imobiliario", name="imobiliario", aliases=["manta-04"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 05", slug="orcamento", name="orcamento", aliases=["manta-05"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 06", slug="modelagem", name="modelagem", aliases=["manta-06"], tier="Sonnet/Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 07", slug="cronograma", name="cronograma", aliases=["manta-07"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 13", slug="bd", name="bd", aliases=["manta-13", "business-dev"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 14", slug="apresentacoes", name="apresentacoes", aliases=["manta-14-pptx"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 15", slug="advisory", name="advisory", aliases=["manta-15", "advisory"], tier="Sonnet/Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 16", slug="arquiteto-ia", name="arquiteto-ia", aliases=["manta-15-arq"], tier="Opus", status=AgentStatus.operacional, axis="horizontal"),
    # Eixo 2 — Verticais por segmento (C3)
    Agent(code="Manta 03-S1", slug="agente-infraestrutura-s1", name="agente-infraestrutura (S1 - Rodovias)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S2", slug="agente-infraestrutura-s2", name="agente-infraestrutura (S2 - OAE)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S3", slug="agente-infraestrutura-s3", name="agente-infraestrutura (S3 - Ferrovia)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S4", slug="agente-infraestrutura-s4", name="agente-infraestrutura (S4 - Metrô)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S5", slug="agente-infraestrutura-s5", name="agente-infraestrutura (S5 - Túneis)", tier="Sonnet", status=AgentStatus.parcial, axis="vertical"),
    Agent(code="Manta 03-S6", slug="agente-portos", name="agente-portos", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S7", slug="agente-aeroportos", name="agente-aeroportos", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S8", slug="agente-saneamento", name="agente-saneamento", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S9", slug="agente-energia", name="agente-energia", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S10", slug="agente-barragens", name="agente-barragens", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
]

LIFECYCLE_PHASES: List[str] = [
    "Estudo prévio / EVTE",
    "Projeto básico",
    "Projeto executivo",
    "Obra em execução",
    "Operação & manutenção",
    "Processo competitivo / licitação",
    "Due diligence / M&A",
    "Encerramento / descomissionamento",
]

# Fallback em memória para sessões de invocação, usado quando o pool
# Postgres não está disponível (mesmo padrão de routers/feedback.py).
_SESSION_STORE: List["AgentSession"] = []


def _find_by_slug(slug: str) -> Optional[Agent]:
    needle = slug.lower()
    for agent in AGENT_REGISTRY:
        if agent.slug.lower() == needle:
            return agent
    return None


@router.get("", response_model=List[Agent], summary="Lista todos os agentes")
async def list_agents(axis: Optional[str] = None) -> List[Agent]:
    if axis:
        return [a for a in AGENT_REGISTRY if a.axis == axis]
    return AGENT_REGISTRY


@router.get("/lifecycle", summary="Fases do ciclo de vida (Eixo 3)")
async def list_lifecycle_phases() -> List[str]:
    return LIFECYCLE_PHASES


# ---------------------------------------------------------------------------
# Invocação de agente — POST /agents/{slug}/invoke (streaming SSE) +
# histórico de sessões.
# ---------------------------------------------------------------------------


class InvokeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    user_email: Optional[str] = None


class AgentSession(BaseModel):
    id: str
    agent_code: str
    agent_slug: str
    prompt: str
    response: str
    user_email: Optional[str] = None
    created_at: datetime


def _sse(event: str, data: dict) -> bytes:
    """Codifica um evento no formato Server-Sent Events."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


def _build_reply(agent: Agent, prompt: str) -> str:
    """Gera a resposta simulada do agente.

    Este skeleton não tem um provider LLM configurado — em produção,
    este ponto chamaria o modelo do tier do agente (ver coluna "Tier
    default" do CLAUDE.md master) com o system prompt do
    `.claude/agents/{nome}.md` correspondente e o RAG da coleção do
    segmento. Aqui devolvemos um texto determinístico que referencia o
    agente e ecoa o prompt, suficiente para exercitar o streaming e a
    persistência de sessão ponta a ponta.
    """
    return (
        f"[{agent.code} · {agent.name}] Recebido (tier {agent.tier}, "
        f"status {agent.status.value}). "
        f"Prompt: \"{prompt.strip()}\". "
        "Esta é uma resposta simulada — nenhum provider LLM está "
        "configurado neste skeleton. Em produção, este agente "
        "consultaria a coleção RAG do seu segmento e responderia com o "
        "system prompt definido em .claude/agents/."
    )


async def _persist_session(pool, record: AgentSession) -> None:
    if pool is None:
        logger.info("agents: DB indisponível, guardando sessão em memória (%s)", record.id)
        _SESSION_STORE.append(record)
        return
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO agent_sessions
                (id, agent_code, agent_slug, prompt, response, user_email, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            record.id, record.agent_code, record.agent_slug,
            record.prompt, record.response, record.user_email, record.created_at,
        )


@router.post(
    "/{slug}/invoke",
    summary="Invoca um agente com um prompt (streaming SSE) e salva a sessão",
)
async def invoke_agent(slug: str, payload: InvokeRequest, request: Request) -> StreamingResponse:
    agent = _find_by_slug(slug)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agente '{slug}' não encontrado.")

    # Capturado antes de entrar no gerador — `Request` não é mais usável
    # depois que a resposta HTTP começa a ser streamada.
    pool = getattr(request.app.state, "db_pool", None)

    async def event_stream() -> AsyncIterator[bytes]:
        session_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        yield _sse("meta", {
            "session_id": session_id,
            "agent_slug": agent.slug,
            "agent_code": agent.code,
        })

        reply = _build_reply(agent, payload.prompt)
        words = reply.split(" ")
        parts: List[str] = []
        try:
            for i, word in enumerate(words):
                delta = word if i == len(words) - 1 else word + " "
                parts.append(delta)
                yield _sse("chunk", {"delta": delta})
                # Pequeno atraso para simular geração token-a-token real
                # (e exercitar o streaming incremental no cliente).
                await asyncio.sleep(0.02)
        finally:
            full_response = "".join(parts)
            if full_response:
                record = AgentSession(
                    id=session_id,
                    agent_code=agent.code,
                    agent_slug=agent.slug,
                    prompt=payload.prompt,
                    response=full_response,
                    user_email=payload.user_email,
                    created_at=created_at,
                )
                await _persist_session(pool, record)

        yield _sse("done", {"session_id": session_id, "full_response": full_response})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Evita que proxies (ex.: nginx) façam buffer do stream.
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{slug}/sessions",
    response_model=List[AgentSession],
    summary="Histórico de sessões recentes de um agente",
)
async def list_agent_sessions(slug: str, request: Request, limit: int = 20) -> List[AgentSession]:
    agent = _find_by_slug(slug)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agente '{slug}' não encontrado.")

    async with acquire_optional(request) as conn:
        if conn is not None:
            rows = await conn.fetch(
                """
                SELECT id, agent_code, agent_slug, prompt, response, user_email, created_at
                FROM agent_sessions
                WHERE agent_slug = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                slug, limit,
            )
            return [AgentSession(**dict(r)) for r in rows]

    matching = [s for s in _SESSION_STORE if s.agent_slug == slug]
    return list(reversed(matching))[:limit]


@router.get("/{code}", response_model=Agent, summary="Detalhe de um agente por código, slug ou nome")
async def get_agent(code: str) -> Agent:
    needle = code.lower()
    for agent in AGENT_REGISTRY:
        if needle in (agent.code.lower(), agent.slug.lower(), agent.name.lower()):
            return agent
    raise HTTPException(status_code=404, detail=f"Agente '{code}' não encontrado.")
