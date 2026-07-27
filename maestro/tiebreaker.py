"""
Phase 3.5: Advanced Routing - LLM Tie-Breaker Service

Handles disambiguation of close routing scores using Claude Sonnet (Manta 16).
Implements score gap detection, Manta 16 invocation, score adjustment, and
confidence boosting based on feedback history.

Author: Maestro Team
Version: v1.0
Status: Production-Ready
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum

import anthropic
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoutingStatus(str, Enum):
    """Status of routing decision."""
    STANDARD = "standard"
    TIEBREAKER = "tiebreaker"
    FALLBACK = "fallback"


@dataclass
class Agent:
    """Agent metadata."""
    id: str
    name: str
    tier: str
    segment: str  # S1-S10
    description: str


@dataclass
class TieBreakerResult:
    """Result of tie-breaker invocation."""
    selected_agent: str
    confidence: float
    reasoning: str
    adjusted_scores: Dict[str, float]
    original_scores: Dict[str, float]
    invocation_time_ms: float
    status: RoutingStatus
    cost_usd: float
    timestamp: datetime


class ScoreGapDetector:
    """Detects when routing scores are within tie-breaker threshold."""

    def __init__(
        self,
        gap_threshold: float = 0.10,
        min_score: float = 0.70,
        min_candidates: int = 2
    ):
        """
        Initialize gap detector.

        Args:
            gap_threshold: Score gap between top-2 agents triggering tie-breaker
            min_score: Minimum score to consider for routing
            min_candidates: Minimum candidates above min_score to trigger tie-breaker
        """
        self.gap_threshold = gap_threshold
        self.min_score = min_score
        self.min_candidates = min_candidates

    def should_trigger_tiebreaker(
        self,
        scores: Dict[str, float]
    ) -> Tuple[bool, Dict]:
        """
        Determine if tie-breaker should be invoked.

        Args:
            scores: Dict mapping agent_id to confidence score

        Returns:
            (should_trigger, metadata)
        """
        if not scores or len(scores) < self.min_candidates:
            return False, {"reason": "insufficient_candidates"}

        # Filter scores >= min_score
        qualified_scores = {
            agent: score
            for agent, score in scores.items()
            if score >= self.min_score
        }

        if len(qualified_scores) < self.min_candidates:
            return False, {"reason": "insufficient_qualified_candidates"}

        # Sort by score descending
        sorted_agents = sorted(
            qualified_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_score = sorted_agents[0][1]
        second_score = sorted_agents[1][1]
        gap = top_score - second_score

        # Check if gap is below threshold
        if gap < self.gap_threshold:
            return True, {
                "reason": "score_gap_below_threshold",
                "top_score": top_score,
                "second_score": second_score,
                "gap": gap,
                "threshold": self.gap_threshold,
                "candidates": len(qualified_scores)
            }

        return False, {"reason": "clear_winner", "gap": gap}


class TieBreakerInvoker:
    """Invokes Manta 16 (Claude Sonnet) for semantic disambiguation."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 500,
        temperature: float = 0.3,
        timeout_ms: int = 350
    ):
        """
        Initialize tie-breaker invoker.

        Args:
            api_key: Anthropic API key
            model: Claude model ID
            max_tokens: Max tokens in response
            temperature: Reasoning temperature (low = consistent)
            timeout_ms: Timeout for API call
        """
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_ms = timeout_ms

    async def invoke_manta16(
        self,
        query: str,
        candidates: Dict[str, Tuple[Agent, float]],
        context: Optional[Dict] = None
    ) -> TieBreakerResult:
        """
        Invoke Manta 16 for tie-breaker decision.

        Args:
            query: Original routing query
            candidates: Dict[agent_id] = (agent_metadata, score)
            context: Optional routing context (project, domain, RAG snippets)

        Returns:
            TieBreakerResult with Sonnet reasoning and adjusted scores
        """
        start_time = time.time()

        # Build prompt for Manta 16
        prompt = self._build_tiebreaker_prompt(query, candidates, context)

        try:
            # Invoke Sonnet with timeout
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                ),
                timeout=self.timeout_ms / 1000.0
            )

            # Parse response
            reasoning = response.content[0].text
            invocation_time_ms = (time.time() - start_time) * 1000

            # Extract adjusted scores from reasoning
            adjusted_scores = self._parse_adjusted_scores(
                reasoning,
                candidates
            )

            # Determine selected agent (highest adjusted score)
            selected_agent = max(adjusted_scores.items(), key=lambda x: x[1])[0]

            # Calculate confidence
            confidence = self._calculate_confidence(adjusted_scores, reasoning)

            # Estimate cost (Sonnet: ~$3/1M input, ~$15/1M output tokens)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(reasoning.split()) * 1.3
            cost_usd = (input_tokens * 3 + output_tokens * 15) / 1_000_000

            return TieBreakerResult(
                selected_agent=selected_agent,
                confidence=confidence,
                reasoning=reasoning,
                adjusted_scores=adjusted_scores,
                original_scores={
                    agent_id: score
                    for agent_id, (_, score) in candidates.items()
                },
                invocation_time_ms=invocation_time_ms,
                status=RoutingStatus.TIEBREAKER,
                cost_usd=cost_usd,
                timestamp=datetime.utcnow()
            )

        except asyncio.TimeoutError:
            logger.warning(
                f"Tie-breaker timeout after {self.timeout_ms}ms, falling back"
            )
            # Return fallback with original scores
            return self._create_fallback_result(candidates, RoutingStatus.FALLBACK)

        except Exception as e:
            logger.error(f"Tie-breaker error: {e}")
            return self._create_fallback_result(candidates, RoutingStatus.FALLBACK)

    def _build_tiebreaker_prompt(
        self,
        query: str,
        candidates: Dict[str, Tuple[Agent, float]],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for Manta 16 semantic disambiguation."""
        candidates_text = "\n".join([
            f"- {agent.name} (ID: {agent_id}, Segment: {agent.segment}, "
            f"Score: {score:.2f})\n  {agent.description}"
            for agent_id, (agent, score) in candidates.items()
        ])

        rag_context = ""
        if context and "rag_snippets" in context:
            snippets = context["rag_snippets"][:3]  # Top 3 snippets
            rag_context = "\n\nRelevant Documentation:\n" + "\n---\n".join(
                snippets
            )

        prompt = f"""You are Manta 16, an expert routing specialist for infrastructure projects.

User Query:
{query}

Candidate Agents (close scores - tie-breaker needed):
{candidates_text}

{rag_context if rag_context else ""}

Analyze the query carefully:
1. Identify the primary domain/segment (infrastructure, saneamento, energia, etc)
2. Note any secondary domains mentioned
3. Consider segment-specific keywords and standards
4. Recommend the BEST FIT agent

Respond in JSON format:
{{
  "selected_agent_id": "agent-xxx",
  "reasoning": "Brief explanation (2-3 sentences)",
  "confidence": 0.85,
  "domain_analysis": "Identified domains and keywords",
  "score_adjustments": {{
    "agent-xxx": 0.92,
    "agent-yyy": 0.88
  }}
}}"""
        return prompt

    def _parse_adjusted_scores(
        self,
        reasoning: str,
        candidates: Dict[str, Tuple[Agent, float]]
    ) -> Dict[str, float]:
        """Parse adjusted scores from Sonnet response."""
        try:
            # Try to extract JSON from reasoning
            json_start = reasoning.find("{")
            json_end = reasoning.rfind("}") + 1
            json_str = reasoning[json_start:json_end]
            data = json.loads(json_str)

            if "score_adjustments" in data:
                return data["score_adjustments"]
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: return original scores with small boost to top candidate
        original_scores = {
            agent_id: score
            for agent_id, (_, score) in candidates.items()
        }
        top_agent = max(original_scores.items(), key=lambda x: x[1])[0]
        original_scores[top_agent] += 0.02  # Small boost
        return original_scores

    def _calculate_confidence(
        self,
        adjusted_scores: Dict[str, float],
        reasoning: str
    ) -> float:
        """Calculate confidence in tie-breaker decision."""
        if not adjusted_scores:
            return 0.5

        # Base confidence from score gap
        sorted_scores = sorted(adjusted_scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            gap = sorted_scores[0] - sorted_scores[1]
            confidence = min(0.95, 0.5 + gap)
        else:
            confidence = 0.7

        # Boost if reasoning mentions specific keywords
        keywords = ["clearly", "unambiguously", "specific", "explicitly"]
        keyword_count = sum(1 for kw in keywords if kw in reasoning.lower())
        confidence += (keyword_count * 0.05)

        return min(1.0, confidence)

    def _create_fallback_result(
        self,
        candidates: Dict[str, Tuple[Agent, float]],
        status: RoutingStatus
    ) -> TieBreakerResult:
        """Create fallback result when tie-breaker fails."""
        original_scores = {
            agent_id: score
            for agent_id, (_, score) in candidates.items()
        }
        selected_agent = max(original_scores.items(), key=lambda x: x[1])[0]

        return TieBreakerResult(
            selected_agent=selected_agent,
            confidence=0.6,
            reasoning="Fallback: Using highest original score",
            adjusted_scores=original_scores,
            original_scores=original_scores,
            invocation_time_ms=0,
            status=status,
            cost_usd=0.0,
            timestamp=datetime.utcnow()
        )


class ScoreAdjuster:
    """Adjusts routing scores based on tie-breaker reasoning."""

    @staticmethod
    def adjust_scores(
        original_scores: Dict[str, float],
        adjusted_scores: Dict[str, float],
        confidence: float,
        confidence_weight: float = 0.8
    ) -> Dict[str, float]:
        """
        Blend original and adjusted scores based on confidence.

        Args:
            original_scores: Scores from Phase 1 routing
            adjusted_scores: Scores from Sonnet reasoning
            confidence: Confidence in tie-breaker decision
            confidence_weight: Weight for adjusted scores (0.0-1.0)

        Returns:
            Final blended scores
        """
        if confidence < 0.60:
            # Low confidence: trust original scores more
            return original_scores

        # Blend scores: high confidence → more weight on adjusted
        blend_weight = confidence * confidence_weight

        final_scores = {}
        all_agents = set(original_scores.keys()) | set(adjusted_scores.keys())

        for agent_id in all_agents:
            orig = original_scores.get(agent_id, 0.5)
            adj = adjusted_scores.get(agent_id, orig)

            # Weighted blend
            final_scores[agent_id] = (
                orig * (1 - blend_weight) +
                adj * blend_weight
            )

        return final_scores


class ConfidenceBooster:
    """Boosts scores based on feedback history and recent performance."""

    def __init__(self, feedback_db):
        """
        Initialize booster.

        Args:
            feedback_db: Reference to feedback database/cache
        """
        self.feedback_db = feedback_db

    async def boost_from_history(
        self,
        agent_id: str,
        window_days: int = 7
    ) -> float:
        """
        Calculate boost multiplier from feedback history.

        Args:
            agent_id: Agent to evaluate
            window_days: Window for recent feedback (default 7 days)

        Returns:
            Multiplier (0.95 - 1.05) for score adjustment
        """
        if not self.feedback_db:
            return 1.0

        try:
            # Get feedback stats for agent
            stats = await self.feedback_db.get_approval_stats(
                agent_id,
                window_days
            )

            approval_rate = stats.get("approval_rate", 0.0)
            recent_wins = stats.get("recent_wins", 0)
            recent_losses = stats.get("recent_losses", 0)

            # Base multiplier
            multiplier = 1.0

            # Boost for high approval rate
            if approval_rate > 0.85:
                multiplier += 0.03
            elif approval_rate > 0.80:
                multiplier += 0.01

            # Boost for recent wins
            if recent_wins > 3:
                multiplier += 0.02

            # Penalty for recent losses
            if recent_losses > 2:
                multiplier -= 0.03

            # Clamp to valid range
            return max(0.95, min(1.05, multiplier))

        except Exception as e:
            logger.error(f"Error calculating boost for {agent_id}: {e}")
            return 1.0


# Example usage
if __name__ == "__main__":
    import os

    async def example():
        """Example tie-breaker invocation."""
        # Initialize components
        detector = ScoreGapDetector(gap_threshold=0.10)
        invoker = TieBreakerInvoker(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-5-sonnet-20241022"
        )

        # Example query and scores
        query = "Projeto de saneamento com lagoas de tratamento e adutora submersas"

        scores = {
            "agente-saneamento": 0.92,
            "agente-infraestrutura-s1": 0.88,
            "agente-energia": 0.65
        }

        # Check if tie-breaker needed
        should_trigger, metadata = detector.should_trigger_tiebreaker(scores)
        print(f"Tie-breaker trigger: {should_trigger}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")

        if should_trigger:
            # Prepare candidates
            candidates = {
                "agente-saneamento": (
                    Agent(
                        "agente-saneamento",
                        "Agente Saneamento",
                        "Sonnet",
                        "S8",
                        "Especialista em saneamento, ETAs, ETEs"
                    ),
                    scores["agente-saneamento"]
                ),
                "agente-infraestrutura-s1": (
                    Agent(
                        "agente-infraestrutura-s1",
                        "Agente Infraestrutura S1",
                        "Sonnet",
                        "S1",
                        "Especialista em rodovias"
                    ),
                    scores["agente-infraestrutura-s1"]
                )
            }

            # Invoke tie-breaker
            result = await invoker.invoke_manta16(query, candidates)
            print(f"\nTie-breaker Result:")
            print(f"  Selected Agent: {result.selected_agent}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Reasoning: {result.reasoning[:200]}...")
            print(f"  Latency: {result.invocation_time_ms:.0f}ms")
            print(f"  Cost: ${result.cost_usd:.4f}")

    asyncio.run(example())
