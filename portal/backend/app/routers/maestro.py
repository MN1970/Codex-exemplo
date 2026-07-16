"""
FastAPI router for Maestro routing service endpoints
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from app.models.maestro import (
    RouteRequest,
    RouteResponse,
    AgentsListResponse,
    RouteDebugResponse,
    RuleMatch,
)
from app.services.maestro_service import MaestroRouter

# Initialize router
router = APIRouter(prefix="/api/maestro", tags=["Maestro Routing"])
maestro = MaestroRouter()


@router.post(
    "/route",
    response_model=RouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Route user input to appropriate agent",
    description="Analyzes user input and determines the best agent to handle the request"
)
async def route_request(request: RouteRequest) -> RouteResponse:
    """
    Route a user query to the appropriate agent.

    Routes based on keyword matching and pattern recognition across all 20 agents
    (11 horizontal + 5 vertical infrastructure S1-S4 + 5 vertical new S6-S10).

    Example requests:
    - "Como calcular um orçamento?" → Manta 05 (Orçamento)
    - "Preciso de um cronograma para minha obra" → Manta 07 (Cronograma)
    - "Qual é o procedimento para uma ETA?" → Manta 03-S8 (Saneamento)
    - "Análise de barragem com CFRD" → Manta 03-S10 (Barragens)
    """
    try:
        intent = maestro.detect_intent(request.user_input)

        # Determine if fallback to Maestro
        is_fallback = (
            intent.agent_id == "manta-00" and
            intent.confidence < 0.25
        )

        explanation = f"Roteado para {intent.agent_name} (confiança: {intent.confidence:.1%})"
        if is_fallback:
            explanation = (
                f"Nenhuma correspondência exata encontrada. "
                f"Roteamento para Maestro para assistência adicional."
            )

        return RouteResponse(
            intent=intent,
            fallback=is_fallback,
            explanation=explanation,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing error: {str(e)}"
        )


@router.post(
    "/route/debug",
    response_model=RouteDebugResponse,
    status_code=status.HTTP_200_OK,
    summary="Debug routing decision with detailed match information",
    description="Returns all matching rules and confidence scores for debugging"
)
async def route_debug(request: RouteRequest) -> RouteDebugResponse:
    """
    Debug version of route endpoint.

    Returns detailed information about:
    - All matched routing rules
    - Top 3 matching candidates
    - Confidence scores for each
    - Matched keywords

    Useful for understanding routing decisions and tuning patterns.
    """
    try:
        user_input_lower = request.user_input.lower()
        all_matches = []

        # Check all rules
        for rule_key, rule in maestro.ROUTING_RULES.items():
            match_result = maestro._match_rule(
                rule_key,
                rule,
                user_input_lower,
                request.user_input
            )
            if match_result:
                all_matches.append(match_result)

        # Sort by confidence
        all_matches.sort(
            key=lambda x: (x.confidence, x.match_count),
            reverse=True
        )

        # Get top 3
        top_matches = all_matches[:3]

        # Get primary intent
        primary_intent = maestro.detect_intent(request.user_input)

        return RouteDebugResponse(
            intent=primary_intent,
            rule_matches=all_matches,
            top_matches=top_matches,
            explanation=(
                f"Primary match: {primary_intent.agent_name} "
                f"(confidence: {primary_intent.confidence:.1%}). "
                f"Total rules matched: {len(all_matches)}"
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug error: {str(e)}"
        )


@router.get(
    "/agents",
    response_model=AgentsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all available agents",
    description="Returns complete profiles of all 20 agents with routing keywords"
)
async def list_agents(
    eixo: Optional[str] = Query(
        None,
        description="Filter by Eixo (Horizontal, Vertical, Lifecycle)"
    )
) -> AgentsListResponse:
    """
    List all 20 registered agents.

    Optionally filter by Eixo:
    - Horizontal: cross-domain agents (Maestro, Claims, Contratual, etc.)
    - Vertical: segment-specific agents (Rodovias, OAE, Portos, Aeroportos, etc.)
    - Lifecycle: phase-specific agents (not yet implemented)

    Returns:
    - Complete agent profiles with IDs, codes, names, aliases
    - Routing keywords for each agent
    - Model tier and operational status
    - Service URLs (when available)
    """
    try:
        if eixo:
            agents = maestro.list_agents_by_eixo(eixo)
        else:
            agents = maestro.list_agents()

        horizontais = [a for a in agents if a.eixo.lower() == "horizontal"]
        verticais = [a for a in agents if a.eixo.lower() == "vertical"]

        return AgentsListResponse(
            agents=agents,
            count=len(agents),
            horizontais_count=len(horizontais),
            verticais_count=len(verticais),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List agents error: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get agent profile by ID",
    description="Retrieve detailed information about a specific agent"
)
async def get_agent(agent_id: str):
    """
    Get complete profile for a specific agent.

    Parameters:
    - agent_id: Agent ID (e.g., 'manta-00', 'manta-03-s8')

    Returns agent profile with:
    - Full name and description
    - Routing keywords and patterns
    - Model tier and status
    - Service endpoint URL (when applicable)
    - Associated segment or domain
    """
    try:
        profile = maestro.get_agent_profile(agent_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found"
            )

        return profile.dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get agent error: {str(e)}"
        )


@router.get(
    "/agents/search",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Search agents by keyword",
    description="Find agents by name, code, or routing keywords"
)
async def search_agents(
    q: str = Query(..., min_length=1, description="Search query")
):
    """
    Search agents by query string.

    Searches across:
    - Agent names (PT-BR)
    - Agent codes (e.g., 'Manta 00')
    - Agent IDs (e.g., 'manta-00')
    - Aliases
    - Routing keywords

    Example: 'porto' → [agente-portos, agente-saneamento with 'porto' keyword]
    """
    try:
        results = maestro.search_agents(q)

        return {
            "query": q,
            "count": len(results),
            "agents": [a.dict() for a in results],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get(
    "/health",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Health check for Maestro service",
    description="Verify Maestro routing service is operational"
)
async def maestro_health():
    """Check Maestro service health"""
    return {
        "status": "operational",
        "service": "maestro-router",
        "agents_count": len(maestro.ROUTING_RULES),
        "version": "4.2",
        "eixos": ["Horizontal", "Vertical", "Lifecycle"],
    }
