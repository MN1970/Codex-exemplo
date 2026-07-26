"""
routers/routing.py — Motor de roteamento do Maestro (Manta 00).

ML-based semantic routing with fallback to keyword matching.
Implementa as regras de Q1 do intake descritas no CLAUDE.md master
(seção "ROUTING — Maestro") usando classification via TF-IDF + Logistic
Regression com fallback para regex keyword matching.
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

from ml.routing_classifier import RoutingClassifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routing", tags=["routing"])

# Global classifier instance
_classifier: Optional[RoutingClassifier] = None


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


def initialize_classifier(model_dir: Optional[str] = None) -> Optional[RoutingClassifier]:
    """
    Initialize the global classifier instance.

    Args:
        model_dir: Path to model directory. Defaults to ./models
    """
    global _classifier

    if _classifier is not None:
        return _classifier

    try:
        _classifier = RoutingClassifier(model_dir=model_dir)
        _classifier.load_model()
        logger.info("ML Classifier initialized and loaded")
        return _classifier
    except Exception as e:
        logger.warning(f"Model files not found or error loading: {e}. Using keyword-based routing only.")
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
    Semantic routing endpoint using ML classifier.

    Takes a user query and returns top-3 agent recommendations with confidence.
    Falls back to keyword matching if ML confidence scores are too low.

    Args:
        request: RoutingRequest with query, org_id, and optional parameters

    Returns:
        RoutingResponse with list of recommended agents
    """
    global _classifier

    # Validate input
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query exceeds maximum length (2000 chars)")

    # Check classifier is loaded
    if _classifier is None:
        logger.warning("ML classifier not available, falling back to keyword-based routing")
        # Fallback to keyword-based classification
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
        # Get predictions from ML classifier
        if request.use_fallback:
            predictions = _classifier.predict_with_fallback(
                query=request.query,
                top_k=request.top_k,
                confidence_threshold=request.confidence_threshold,
            )
        else:
            predictions = _classifier.predict(
                query=request.query,
                top_k=request.top_k,
                confidence_threshold=request.confidence_threshold,
            )

        # Convert to response model
        agents = [AgentPrediction(**pred) for pred in predictions]

        response = RoutingResponse(
            agents=agents,
            query=request.query,
            org_id=request.org_id,
            count=len(agents),
        )

        logger.info(f"Routed query (org: {request.org_id}, agents: {len(agents)})")
        return response

    except Exception as e:
        logger.error(f"Error during routing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


@router.get("/route-semantic/health")
async def health_check() -> Dict:
    """
    Health check for routing service.

    Returns:
        Status and metrics if classifier is loaded
    """
    global _classifier

    if _classifier is None:
        return {
            "status": "partial",
            "message": "ML classifier not loaded, using keyword-based routing",
            "classifier_loaded": False,
        }

    return {
        "status": "healthy",
        "classifier_loaded": True,
        "metrics": _classifier.metrics,
        "num_agents": len(_classifier.agent_data),
    }
