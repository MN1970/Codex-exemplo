"""
routers/routing.py — Motor de roteamento do Maestro (Manta 00).

ML-based semantic routing with fallback to keyword matching.
Implementa as regras de Q1 do intake descritas no CLAUDE.md master
(seção "ROUTING — Maestro"). O endpoint POST /route-semantic usa o
classificador semântico de ml/routing.py (Sentence Transformers +
Logistic Regression, treinado sobre os 20 agentes) com fallback
determinístico para keyword matching quando a confiança fica abaixo do
threshold — ver ml/routing.py::predict_agent().

O endpoint GET /rules e POST /classify continuam sendo o motor de
keyword/regex puro (Q1 do intake, sem ML) — usado como fallback e como
rota independente para quem só quer a regra determinística.
"""
import logging
import re
from typing import List, Optional, Dict
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import sys

# Add parent directories to path for imports
router_dir = Path(__file__).parent
backend_dir = router_dir.parent
sys.path.insert(0, str(backend_dir))

from ml.routing import (
    RoutingModel,
    load_routing_model,
    predict_agent as ml_predict_agent,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routing", tags=["routing"])

# Cache do modelo semântico (lazy — carregado no primeiro request de
# /route-semantic, não bloqueia o startup da app se o modelo ainda não
# tiver sido treinado). Ver initialize_semantic_model().
_semantic_model: Optional[RoutingModel] = None
_semantic_model_load_failed: bool = False


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


class RoutingRequest(BaseModel):
    """Request model for semantic routing."""
    query: str = Field(..., description="User query text")
    org_id: str = Field(..., description="Organization ID")
    top_k: int = Field(3, ge=1, le=10, description="Number of top agents to return")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    use_fallback: bool = Field(True, description="Use keyword fallback if ML confidence is low")


class AgentPrediction(BaseModel):
    """Single agent prediction."""
    agent_slug: str
    agent_name: str
    confidence: float
    method: Optional[str] = None


class RoutingResponse(BaseModel):
    """Response model for semantic routing."""
    agents: List[AgentPrediction]
    query: str
    org_id: str
    count: int


def initialize_semantic_model(force_reload: bool = False) -> Optional[RoutingModel]:
    """
    Carrega (e cacheia) o modelo semântico de ml/routing.py.

    Chamado lazily no primeiro POST /route-semantic — não bloqueia o
    startup da app se o modelo ainda não tiver sido treinado
    (`python -m ml.routing train`). Nesse caso, o endpoint degrada para
    keyword-based routing puro (mesma lógica de /classify).

    Args:
        force_reload: ignora o cache e tenta carregar de novo (útil depois
            de treinar uma nova versão em runtime).
    """
    global _semantic_model, _semantic_model_load_failed

    if _semantic_model is not None and not force_reload:
        return _semantic_model

    try:
        _semantic_model = load_routing_model()
        _semantic_model_load_failed = False
        logger.info(
            "Semantic routing model loaded: v%d (%s, %d agentes)",
            _semantic_model.version, _semantic_model.embedding_model, len(_semantic_model.agent_data),
        )
        return _semantic_model
    except Exception as e:
        _semantic_model_load_failed = True
        logger.warning(f"Semantic routing model not available ({e}). Using keyword-based routing only.")
        return None


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


@router.post("/route-semantic", response_model=RoutingResponse)
async def route_semantic(request: RoutingRequest) -> RoutingResponse:
    """
    Endpoint de roteamento semântico (Sentence Transformers + Logistic
    Regression — ver ml/routing.py::predict_agent()).

    Recebe uma query e devolve até `top_k` agentes recomendados com
    confiança. Se a confiança do top-1 do embedding ficar abaixo de
    `confidence_threshold` (default 0.7) e `use_fallback=True`, a decisão
    cai para keyword matching determinístico sobre as keywords dos 20
    agentes.

    Args:
        request: RoutingRequest com query, org_id e parâmetros opcionais

    Returns:
        RoutingResponse com a lista de agentes recomendados
    """
    # Validate input
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query exceeds maximum length (2000 chars)")

    model = initialize_semantic_model()

    if model is None:
        logger.warning("Semantic model not available, falling back to keyword-based routing")
        classify_req = ClassifyRequest(text=request.query)
        classify_resp = await classify(classify_req)

        if classify_resp.matched:
            agents = [AgentPrediction(
                agent_slug=classify_resp.agent_code,
                agent_name=classify_resp.agent_name,
                confidence=0.8,
                method="keyword_match"
            )]
        else:
            agents = []

        return RoutingResponse(
            agents=agents,
            query=request.query,
            org_id=request.org_id,
            count=len(agents),
        )

    try:
        _, _, top_predictions = ml_predict_agent(
            request.query,
            top_k=request.top_k,
            confidence_threshold=request.confidence_threshold,
            model=model,
            use_fallback=request.use_fallback,
        )

        agents = [AgentPrediction(**pred) for pred in top_predictions]

        response = RoutingResponse(
            agents=agents,
            query=request.query,
            org_id=request.org_id,
            count=len(agents),
        )

        logger.info(f"Routed query (org: {request.org_id}, agents: {len(agents)})")
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during routing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


@router.get("/route-semantic/health")
async def health_check() -> Dict:
    """
    Health check do roteamento semântico.

    Returns:
        Status e metadados do modelo (versão, encoder, métricas) se carregado.
    """
    model = initialize_semantic_model()

    if model is None:
        return {
            "status": "partial",
            "message": "Semantic model not loaded, using keyword-based routing",
            "model_loaded": False,
        }

    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": model.version,
        "embedding_model": model.embedding_model,
        "metrics": {k: v for k, v in model.metrics.items() if k != "classification_report"},
        "num_agents": len(model.agent_data),
    }
