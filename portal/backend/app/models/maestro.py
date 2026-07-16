"""
Pydantic models for Maestro routing service
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class RoutingConfidence(str, Enum):
    """Confidence levels for routing decisions"""
    EXACT = "exact"        # Exact keyword match (0.95-1.0)
    HIGH = "high"          # Multiple keyword matches (0.75-0.95)
    MEDIUM = "medium"      # Partial keyword match (0.5-0.75)
    LOW = "low"            # Heuristic match (0.25-0.5)
    FALLBACK = "fallback"  # No match, routing to Maestro (0.0-0.25)


class RoutingIntent(BaseModel):
    """User intent extracted from input text"""
    agent_code: str = Field(..., description="Agent code (e.g., '03-S8')")
    agent_name: str = Field(..., description="Agent name in Portuguese")
    agent_id: str = Field(..., description="Full agent ID (e.g., 'manta-03-s8')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Routing confidence (0-1)")
    confidence_level: RoutingConfidence = Field(..., description="Confidence level category")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that matched in input")
    eixo: str = Field(..., description="Eixo (Horizontal, Vertical, or Lifecycle)")
    segment: Optional[str] = Field(None, description="Segment name (for vertical agents)")
    service_url: Optional[str] = Field(None, description="Service endpoint URL")
    aliases: List[str] = Field(default_factory=list, description="Agent aliases")
    tier: str = Field(..., description="Model tier (Haiku, Sonnet, Opus, etc.)")
    status: str = Field(..., description="Agent status (Operacional, Beta, etc.)")


class AgentProfile(BaseModel):
    """Complete agent profile for listing and discovery"""
    id: str = Field(..., description="Agent ID (e.g., 'manta-00')")
    code: str = Field(..., description="Agent code (e.g., 'Manta 00')")
    name: str = Field(..., description="Agent name in Portuguese")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    description: Optional[str] = Field(None, description="Agent description")
    eixo: str = Field(..., description="Classification: Horizontal, Vertical, or Lifecycle")
    segment: Optional[str] = Field(None, description="Segment for vertical agents")
    tier: str = Field(..., description="Default model tier")
    status: str = Field(..., description="Operational status")
    service_url: Optional[str] = Field(None, description="Service endpoint URL")
    routing_keywords: List[str] = Field(default_factory=list, description="Keywords for routing")
    routing_pattern: Optional[str] = Field(None, description="Regex pattern for routing")


class RouteRequest(BaseModel):
    """Request to route a user query"""
    user_input: str = Field(..., min_length=1, description="User query or message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class RouteResponse(BaseModel):
    """Response with routing decision"""
    intent: RoutingIntent = Field(..., description="Detected intent and agent assignment")
    fallback: bool = Field(False, description="True if routed to Maestro (fallback)")
    explanation: str = Field(..., description="Human-readable routing explanation")


class AgentsListResponse(BaseModel):
    """List of all available agents"""
    agents: List[AgentProfile] = Field(..., description="List of agent profiles")
    count: int = Field(..., description="Total number of agents")
    horizontais_count: int = Field(..., description="Count of horizontal agents")
    verticais_count: int = Field(..., description="Count of vertical agents")


class RuleMatch(BaseModel):
    """Information about a matched routing rule"""
    agent_code: str
    matched_keywords: List[str]
    match_count: int
    confidence: float
    rule_pattern: str


class RouteDebugResponse(BaseModel):
    """Debug information about routing decision"""
    intent: RoutingIntent
    rule_matches: List[RuleMatch] = Field(default_factory=list, description="All matched rules")
    top_matches: List[RuleMatch] = Field(default_factory=list, description="Top 3 matching rules")
    explanation: str
