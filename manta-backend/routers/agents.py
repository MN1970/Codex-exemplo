"""
routers/agents.py — Registro de agentes (espelha o mapa do CLAUDE.md
master: 20 agentes em 3 eixos — horizontais, verticais por segmento,
ciclo de vida).

Em produção este catálogo viria do Supabase (tabela `agents`); aqui
está embutido como fixture para o skeleton subir sem dependências.
"""
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentStatus(str, Enum):
    operacional = "operacional"
    parcial = "parcial"
    planejado = "planejado"


class Agent(BaseModel):
    code: str
    name: str
    aliases: List[str] = []
    tier: str
    status: AgentStatus
    axis: str  # "horizontal" | "vertical" | "lifecycle"


AGENT_REGISTRY: List[Agent] = [
    # Eixo 1 — Horizontais
    Agent(code="Manta 00", name="maestro", aliases=["maestro", "manta-router"], tier="Haiku→Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 01", name="claims", aliases=["02-C", "manta-claims"], tier="Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 02", name="contratual", aliases=["manta-02", "contratual"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 04", name="imobiliario", aliases=["manta-04"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 05", name="orcamento", aliases=["manta-05"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 06", name="modelagem", aliases=["manta-06"], tier="Sonnet/Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 07", name="cronograma", aliases=["manta-07"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 13", name="bd", aliases=["manta-13", "business-dev"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 14", name="apresentacoes", aliases=["manta-14-pptx"], tier="Sonnet", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 15", name="advisory", aliases=["manta-15", "advisory"], tier="Sonnet/Opus", status=AgentStatus.operacional, axis="horizontal"),
    Agent(code="Manta 16", name="arquiteto-ia", aliases=["manta-15-arq"], tier="Opus", status=AgentStatus.operacional, axis="horizontal"),
    # Eixo 2 — Verticais por segmento (C3)
    Agent(code="Manta 03-S1", name="agente-infraestrutura (S1 - Rodovias)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S2", name="agente-infraestrutura (S2 - OAE)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S3", name="agente-infraestrutura (S3 - Ferrovia)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S4", name="agente-infraestrutura (S4 - Metrô)", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S5", name="agente-infraestrutura (S5 - Túneis)", tier="Sonnet", status=AgentStatus.parcial, axis="vertical"),
    Agent(code="Manta 03-S6", name="agente-portos", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S7", name="agente-aeroportos", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S8", name="agente-saneamento", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S9", name="agente-energia", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
    Agent(code="Manta 03-S10", name="agente-barragens", tier="Sonnet", status=AgentStatus.operacional, axis="vertical"),
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


@router.get("", response_model=List[Agent], summary="Lista todos os agentes")
async def list_agents(axis: Optional[str] = None) -> List[Agent]:
    if axis:
        return [a for a in AGENT_REGISTRY if a.axis == axis]
    return AGENT_REGISTRY


@router.get("/lifecycle", summary="Fases do ciclo de vida (Eixo 3)")
async def list_lifecycle_phases() -> List[str]:
    return LIFECYCLE_PHASES


@router.get("/{code}", response_model=Agent, summary="Detalhe de um agente por código")
async def get_agent(code: str) -> Agent:
    for agent in AGENT_REGISTRY:
        if agent.code.lower() == code.lower() or agent.name.lower() == code.lower():
            return agent
    raise HTTPException(status_code=404, detail=f"Agente '{code}' não encontrado.")
