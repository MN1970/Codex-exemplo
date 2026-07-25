# Advanced Routing (LLM Tie-Breaker) — Phase 3.5 Implementation Guide

**Target**: `manta-hub/maestro/advanced_router.py`  
**Model**: Claude Sonnet (tie-breaking logic)  
**Trigger**: Score gap < 15% or primary_score < 70%  
**Timeline**: Phase 3.5 (Feb 01 - Feb 28, 2027)

This guide implements LLM-assisted disambiguation for ambiguous routing cases where keyword-only scoring is inconclusive.

---

## Overview

```
User Query
  ↓
Maestro Router (keyword-based scoring)
  ├── Calculate scores for all agents
  ├── Identify primary and secondary agents
  ├── Check: score_gap < 15% OR primary_score < 70%?
  │
  ├─→ YES (ambiguous): dispatch to Advanced Router
  │        ↓
  │        LLM Tie-Breaker (Sonnet)
  │        ├── Prompt: "Which agent is best for this query?"
  │        ├── Input: query + top-2 agent descriptions
  │        ├── Output: recommendation + reasoning
  │        ├── Update: primary_agent + confidence
  │        └── Log: maestro_tiebreaker_events
  │        ↓
  │        (Use updated primary agent)
  │
  └─→ NO (clear): route to primary agent normally
```

---

## Part 1: Advanced Router Implementation

```python
# manta-hub/maestro/advanced_router.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RouterContext:
    """Context for advanced routing decision."""
    user_prompt: str
    primary_agent: str
    primary_score: float
    secondary_agent: str
    secondary_score: float
    routing_scores: Dict[str, float]
    ambiguity_reason: str
    agent_descriptions: Dict[str, str]

@dataclass
class RoutingDecision:
    """Result of advanced routing."""
    primary_agent: str
    confidence: float
    reasoning: str
    tie_breaker_used: bool
    timestamp: str

class AdvancedRouter:
    """LLM-assisted tie-breaking for ambiguous routing."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic()
        self.model = model

    def should_use_tie_breaker(
        self,
        primary_score: float,
        secondary_score: float,
    ) -> bool:
        """
        Determine if tie-breaker should be used.

        Criteria:
        1. Score gap < 15 percentage points (0.15)
        2. Primary score < 70% confidence (0.70)
        """
        score_gap = primary_score - secondary_score

        return score_gap < 0.15 or primary_score < 0.70

    def resolve_ambiguity(
        self,
        context: RouterContext,
    ) -> RoutingDecision:
        """
        Use LLM to resolve ambiguous routing.

        Args:
            context: Routing context with query + top agents

        Returns:
            Updated routing decision with LLM reasoning
        """

        # Build system prompt
        system_prompt = self._build_system_prompt(context)

        # Build user message
        user_message = self._build_user_message(context)

        # Call LLM
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        # Parse response
        response_text = response.content[0].text
        decision = self._parse_decision(response_text, context)

        return decision

    def _build_system_prompt(self, context: RouterContext) -> str:
        """Build system prompt for tie-breaker."""
        return """You are the Maestro Router's tie-breaker. Your job is to resolve ambiguous 
routing decisions by choosing the single best agent for a user query.

You will be given:
1. User query (original question/request)
2. Top 2 candidate agents with their scores
3. Agent descriptions (expertise areas)

Your job:
- Analyze the query carefully
- Consider what each agent specializes in
- Recommend ONE agent as primary (most suitable)
- If truly equal, recommend the one with higher keyword score

Output format:
```json
{
    "primary_agent": "agent-slug",
    "confidence": 0.85,
    "reasoning": "Short explanation of why this agent is best"
}
```

Be concise and decisive. No hedging. The user will dispatch to this agent."""

    def _build_user_message(self, context: RouterContext) -> str:
        """Build user message for tie-breaker."""
        return f"""Query: {context.user_prompt}

Candidate Agents:
1. {context.primary_agent} (score: {context.primary_score:.2f})
   Description: {context.agent_descriptions.get(context.primary_agent, 'N/A')}

2. {context.secondary_agent} (score: {context.secondary_score:.2f})
   Description: {context.agent_descriptions.get(context.secondary_agent, 'N/A')}

Ambiguity reason: {context.ambiguity_reason}

Which agent should handle this query? Output JSON."""

    def _parse_decision(
        self,
        response_text: str,
        context: RouterContext,
    ) -> RoutingDecision:
        """Parse LLM response into routing decision."""
        try:
            # Extract JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                # Fallback: use primary score
                logger.warning(f"Could not parse tie-breaker response: {response_text}")
                return RoutingDecision(
                    primary_agent=context.primary_agent,
                    confidence=context.primary_score,
                    reasoning="Tie-breaker parsing failed; using keyword score",
                    tie_breaker_used=False,
                    timestamp=datetime.utcnow().isoformat(),
                )

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            # Validate agent selection
            chosen_agent = data.get("primary_agent", context.primary_agent)
            if chosen_agent not in [context.primary_agent, context.secondary_agent]:
                chosen_agent = context.primary_agent

            return RoutingDecision(
                primary_agent=chosen_agent,
                confidence=float(data.get("confidence", 0.85)),
                reasoning=data.get("reasoning", ""),
                tie_breaker_used=True,
                timestamp=datetime.utcnow().isoformat(),
            )

        except Exception as e:
            logger.error(f"Error parsing tie-breaker response: {e}")
            # Fallback to primary score
            return RoutingDecision(
                primary_agent=context.primary_agent,
                confidence=context.primary_score,
                reasoning="Tie-breaker error; using keyword score",
                tie_breaker_used=False,
                timestamp=datetime.utcnow().isoformat(),
            )
```

---

## Part 2: Integration with Maestro Router

```python
# manta-hub/maestro/router.py (EXTENDED)

from advanced_router import AdvancedRouter, RouterContext

class MaestroRouter:
    def __init__(self):
        self.advanced_router = AdvancedRouter()
        # ... existing initialization

    def route_and_respond(self, user_prompt: str) -> Dict:
        """
        Main routing logic with optional tie-breaking.
        """

        # 1. Score all agents (keyword-based)
        scores = self._score_agents(user_prompt)

        primary_agent = max(scores, key=scores.get)
        primary_score = scores[primary_agent]

        # Get runner-up
        remaining = {a: s for a, s in scores.items() if a != primary_agent}
        secondary_agent = max(remaining, key=remaining.get) if remaining else None
        secondary_score = remaining[secondary_agent] if secondary_agent else 0

        score_gap = primary_score - secondary_score

        # 2. Check if tie-breaker needed
        if self.advanced_router.should_use_tie_breaker(primary_score, secondary_score):
            logger.info(f"Ambiguous routing detected (gap {score_gap:.2f}); using tie-breaker")

            # 3. Resolve with LLM
            context = RouterContext(
                user_prompt=user_prompt,
                primary_agent=primary_agent,
                primary_score=primary_score,
                secondary_agent=secondary_agent,
                secondary_score=secondary_score,
                routing_scores=scores,
                ambiguity_reason=f"Score gap {score_gap:.2f} < 0.15 or primary score {primary_score:.2f} < 0.70",
                agent_descriptions=self._get_agent_descriptions(),
            )

            decision = self.advanced_router.resolve_ambiguity(context)

            # 4. Log tie-breaker event
            self._log_tiebreaker_event(
                user_prompt=user_prompt,
                primary_from_keywords=primary_agent,
                primary_from_llm=decision.primary_agent,
                confidence=decision.confidence,
                reasoning=decision.reasoning,
            )

            # Use LLM decision
            primary_agent = decision.primary_agent
            primary_score = decision.confidence

        # 5. Dispatch to final agent
        response = self._dispatch(primary_agent, user_prompt)

        # 6. Log routing event
        self._log_routing_event(
            user_prompt=user_prompt,
            routed_agent=primary_agent,
            confidence=primary_score,
            tie_breaker_used=(primary_agent != max(scores, key=scores.get)),
        )

        return {
            "agent": primary_agent,
            "confidence": primary_score,
            "response": response,
        }

    def _get_agent_descriptions(self) -> Dict[str, str]:
        """Get agent descriptions for tie-breaker context."""
        # Load from CLAUDE.md or agent .md files
        return {
            "agente-saneamento": "Especialista em saneamento básico (ETA, ETE, adução, drenagem urbana)",
            "agente-energia": "Especialista em transmissão e distribuição de energia (LT, subestações, leilões ANEEL)",
            "agente-portos": "Especialista em projetos portuários e hidroviários (dragagem, cais, terminais)",
            "agente-aeroportos": "Especialista em infraestrutura aeroportuária (pistas, pátios, TPS, ANAC)",
            "agente-barragens": "Especialista em barragens (CFRD, CCR, rejeitos, SIGBM)",
        }

    def _log_tiebreaker_event(self, **kwargs):
        """Log tie-breaker usage to database."""
        self.db.table("maestro_tiebreaker_events").insert({
            "timestamp": datetime.utcnow().isoformat(),
            "user_prompt": kwargs.get("user_prompt"),
            "primary_from_keywords": kwargs.get("primary_from_keywords"),
            "primary_from_llm": kwargs.get("primary_from_llm"),
            "confidence": kwargs.get("confidence"),
            "reasoning": kwargs.get("reasoning"),
        }).execute()

    def _log_routing_event(self, **kwargs):
        """Log routing decision."""
        # ... existing logging
        pass
```

---

## Part 3: Database Schema

```sql
-- maestro_tiebreaker_events table
CREATE TABLE maestro_tiebreaker_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    user_prompt TEXT NOT NULL,
    primary_from_keywords VARCHAR(50),
    primary_from_llm VARCHAR(50),
    confidence FLOAT,
    reasoning TEXT,
    model_used VARCHAR(50) DEFAULT 'claude-sonnet-4-20250514'
);

-- Update maestro_routing_trace to include tie_breaker_used
ALTER TABLE maestro_routing_trace
ADD COLUMN IF NOT EXISTS tie_breaker_used BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS tie_breaker_reasoning TEXT;

CREATE INDEX idx_tiebreaker_timestamp ON maestro_tiebreaker_events(timestamp);
CREATE INDEX idx_tiebreaker_effectiveness ON maestro_tiebreaker_events(primary_from_keywords, primary_from_llm);
```

---

## Part 4: Effectiveness Monitoring

```python
# maestro-monitoring/tiebreaker_analytics.py

class TiebreakerAnalytics:
    """Analyze tie-breaker effectiveness."""

    def __init__(self, db):
        self.db = db

    def get_effectiveness_metrics(self, days: int = 7) -> Dict:
        """Calculate tie-breaker effectiveness."""

        # Query events
        result = self.db.table("maestro_tiebreaker_events").select(
            "*"
        ).gte("timestamp", f"now()-{days} days").execute()

        events = result.data
        total = len(events)

        if total == 0:
            return {"total_events": 0, "effectiveness": 0.0}

        # Count when LLM changed decision
        changed = sum(
            1 for e in events
            if e["primary_from_keywords"] != e["primary_from_llm"]
        )

        # Get user feedback on tie-breaker decisions
        feedback_result = self.db.table("maestro_user_feedback").select(
            "correct_agent"
        ).filter(
            "tie_breaker_used", "eq", True
        ).gte("timestamp", f"now()-{days} days").execute()

        feedback = feedback_result.data
        approved = sum(
            1 for f in feedback
            if f["correct_agent"] == f["routed_agent"]
        )

        approval_rate = (approved / len(feedback)) if feedback else 0.0

        return {
            "total_events": total,
            "decisions_changed": changed,
            "change_rate": changed / total if total > 0 else 0.0,
            "approval_rate": approval_rate,
            "effectiveness": approval_rate if approval_rate > 0 else 0.5,
        }

    def get_confusion_cases(self, days: int = 7) -> List[Dict]:
        """Get cases where tie-breaker frequently activates."""

        result = self.db.rpc(
            "get_top_tiebreaker_pairs",
            {"days": days}
        ).execute()

        return result.data
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| **Tie-Breaker Usage Rate** | 5-10% of queries | maestro_tiebreaker_events count |
| **Approval Rate** | >85% | User feedback on tie-breaker decisions |
| **Decision Change Rate** | 30-50% | Keywords vs LLM agreement |
| **Latency Addition** | <500ms | Tie-breaker query latency |

---

## Deployment Checklist

- [ ] Implement AdvancedRouter class
- [ ] Implement tie-breaker trigger logic
- [ ] Integrate with MaestroRouter
- [ ] Create maestro_tiebreaker_events table
- [ ] Write unit tests (10+ test cases)
- [ ] Deploy to staging
- [ ] Monitor for 2 weeks
- [ ] Analyze effectiveness metrics
- [ ] Tune trigger thresholds if needed
- [ ] Enable for production with canary (10% → 50% → 100%)

---

**Status**: Ready for implementation  
**Owner**: Maestro team (manta-hub)  
**Timeline**: Phase 3.5 (Feb 01 - Feb 28, 2027)
