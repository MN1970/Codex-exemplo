"""
routers/routing.py — Motor de roteamento do Maestro (Manta 00).

Implementa em código as regras de Q1 do intake descritas no CLAUDE.md
master (seção "ROUTING — Maestro"): dado um texto livre, casa palavras-
chave por segmento e devolve o agente vertical recomendado.
"""
import re
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/routing", tags=["routing"])


class RoutingRule(BaseModel):
    agent_code: str
    agent_name: str
    keywords_pattern: str


# Ordem importa: primeira regra que casar vence (mesma ordem do CLAUDE.md).
ROUTING_RULES: List[RoutingRule] = [
    RoutingRule(agent_code="Manta 03-S8", agent_name="agente-saneamento",
                keywords_pattern=r"saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS"),
    RoutingRule(agent_code="Manta 03-S9", agent_name="agente-energia",
                keywords_pattern=r"transmiss[ãa]o|\bLT\b|subesta[çc][ãa]o|ANEEL|RAP|leil[ãa]o transmiss[ãa]o|ONS|EPE"),
    RoutingRule(agent_code="Manta 03-S6", agent_name="agente-portos",
                keywords_pattern=r"porto|terminal|ANTAQ|dragagem|mol(h|)e|ber[çc]o|calado|cont[êe]iner|granel"),
    RoutingRule(agent_code="Manta 03-S7", agent_name="agente-aeroportos",
                keywords_pattern=r"aeroporto|pista (de )?pouso|ANAC|ICAO|TPS|TECA|balizamento"),
    RoutingRule(agent_code="Manta 03-S10", agent_name="agente-barragens",
                keywords_pattern=r"barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF"),
    RoutingRule(agent_code="Manta 03-S1", agent_name="agente-infraestrutura (S1)",
                keywords_pattern=r"rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT"),
    RoutingRule(agent_code="Manta 03-S2", agent_name="agente-infraestrutura (S2)",
                keywords_pattern=r"ponte|viaduto|OAE|NBR ?7187|t[úu]nel rodovi[áa]rio"),
    RoutingRule(agent_code="Manta 03-S3", agent_name="agente-infraestrutura (S3)",
                keywords_pattern=r"ferrovia|trilho|AMV|dormente|via permanente"),
    RoutingRule(agent_code="Manta 03-S4", agent_name="agente-infraestrutura (S4)",
                keywords_pattern=r"metr[oô]|esta[çc][ãa]o|NATM|PSD|linha 4|linha 5|VLT"),
]


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    matched: bool
    agent_code: Optional[str] = None
    agent_name: Optional[str] = None
    matched_keyword: Optional[str] = None


@router.get("/rules", response_model=List[RoutingRule], summary="Lista as regras de routing (Q1)")
async def list_rules() -> List[RoutingRule]:
    return ROUTING_RULES


@router.post("/classify", response_model=ClassifyResponse, summary="Classifica um texto e retorna o agente vertical")
async def classify(payload: ClassifyRequest) -> ClassifyResponse:
    for rule in ROUTING_RULES:
        match = re.search(rule.keywords_pattern, payload.text, flags=re.IGNORECASE)
        if match:
            return ClassifyResponse(
                matched=True,
                agent_code=rule.agent_code,
                agent_name=rule.agent_name,
                matched_keyword=match.group(0),
            )
    return ClassifyResponse(matched=False)
