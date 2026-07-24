"""
CAG Shadow Mode Orchestrator — Runs CAG parallel to v4.2 RAG for comparison
Version: 1.0
Purpose: 30-day A/B test comparing CAG vs RAG before GA launch
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# =============================================================================
# TYPES
# =============================================================================

@dataclass
class ShadowResult:
    """Comparison result from shadow run"""
    session_id: str
    query: str
    timestamp: str

    # RAG (v4.2) results
    rag_agent: str
    rag_latency_ms: float
    rag_confidence: float
    rag_response_text: str

    # CAG (v5.0) results
    cag_selected_agents: List[str]
    cag_latency_ms: float
    cag_avg_confidence: float
    cag_final_response: str

    # Comparison metrics
    agent_match: bool  # Did CAG select the same primary agent as RAG?
    confidence_delta: float  # CAG confidence - RAG confidence
    latency_delta_ms: float  # CAG latency - RAG latency
    latency_delta_pct: float  # (CAG latency / RAG latency - 1) * 100

    # Metadata
    cag_metadata: Dict  # CAG execution metadata

    def to_dict(self) -> Dict:
        """Convert to dict for logging"""
        return asdict(self)

# =============================================================================
# SHADOW ORCHESTRATOR
# =============================================================================

class ShadowModeOrchestrator:
    """
    Runs CAG and v4.2 RAG in parallel, compares results, logs discrepancies.

    Flow:
    1. Incoming query
    2. Dispatch to v4.2 RAG (synchronous, current prod)
    3. Dispatch to CAG (async, new system)
    4. Collect results from both
    5. Compare outputs (agent selection, confidence, latency)
    6. Log comparison to Supabase (cag_shadow_logs table)
    7. Return RAG result to user (no disruption)
    8. Background: analyze CAG vs RAG discrepancies
    """

    def __init__(self, rag_handler, cag_orchestrator, debug: bool = False):
        """
        Args:
            rag_handler: v4.2 RAG system (sync callable)
            cag_orchestrator: CAG orchestrator (async callable)
            debug: verbose logging
        """
        self.rag_handler = rag_handler
        self.cag_orchestrator = cag_orchestrator
        self.debug = debug
        self.results_buffer = []  # in-memory buffer for batching to Supabase
        self.buffer_size = 100  # flush every N results

    async def shadow_run(
        self,
        query: str,
        session_id: str,
        rag_context: Optional[Dict] = None
    ) -> Tuple[Dict, ShadowResult]:
        """
        Runs query through both RAG and CAG, returns RAG result + comparison.

        Args:
            query: user query
            session_id: for tracking
            rag_context: optional context dict for RAG (agent pool, intent classes, etc.)

        Returns:
            (rag_result, shadow_result) where rag_result goes to user
        """
        start_time = time.time()

        # =====================================================================
        # DISPATCH 1: Run v4.2 RAG (synchronous)
        # =====================================================================
        rag_start = time.time()
        try:
            rag_result = self.rag_handler(
                query=query,
                session_id=session_id,
                context=rag_context or {}
            )
            rag_latency_ms = (time.time() - rag_start) * 1000
            rag_success = True
        except Exception as e:
            if self.debug:
                print(f"[SHADOW] RAG error: {e}")
            rag_result = {
                'error': str(e),
                'query': query,
                'agent': 'error'
            }
            rag_latency_ms = (time.time() - rag_start) * 1000
            rag_success = False

        rag_primary_agent = rag_result.get('selected_agent') or rag_result.get('agent', 'unknown')
        rag_confidence = rag_result.get('confidence', 0.0)
        rag_response = rag_result.get('response_text', '')

        # =====================================================================
        # DISPATCH 2: Run CAG (asynchronous, fire-and-forget)
        # =====================================================================
        cag_start = time.time()
        try:
            cag_result = await self.cag_orchestrator.orchestrate(
                query=query,
                selected_agents=None,  # will be determined by classifier
                agent_responses_dict={},
                session_id=session_id
            )
            cag_latency_ms = (time.time() - cag_start) * 1000
            cag_success = True
        except Exception as e:
            if self.debug:
                print(f"[SHADOW] CAG error: {e}")
            cag_result = {
                'error': str(e),
                'query': query,
                'selected_agents': []
            }
            cag_latency_ms = (time.time() - cag_start) * 1000
            cag_success = False

        cag_selected_agents = cag_result.get('selected_agents', [])
        cag_primary_agent = cag_selected_agents[0] if cag_selected_agents else 'none'
        cag_avg_confidence = cag_result.get('metadata', {}).get('avg_confidence', 0.0)
        cag_response = cag_result.get('final_response', '')

        # =====================================================================
        # COMPARISON LOGIC
        # =====================================================================
        agent_match = (
            rag_success and cag_success and
            rag_primary_agent == cag_primary_agent
        )
        confidence_delta = cag_avg_confidence - rag_confidence
        latency_delta_ms = cag_latency_ms - rag_latency_ms
        latency_delta_pct = (
            (cag_latency_ms / rag_latency_ms - 1) * 100
            if rag_latency_ms > 0 else 0.0
        )

        # =====================================================================
        # CREATE SHADOW RESULT
        # =====================================================================
        shadow_result = ShadowResult(
            session_id=session_id,
            query=query,
            timestamp=datetime.utcnow().isoformat(),

            rag_agent=rag_primary_agent,
            rag_latency_ms=rag_latency_ms,
            rag_confidence=rag_confidence,
            rag_response_text=rag_response[:500],  # truncate for storage

            cag_selected_agents=cag_selected_agents,
            cag_latency_ms=cag_latency_ms,
            cag_avg_confidence=cag_avg_confidence,
            cag_final_response=cag_response[:500],  # truncate for storage

            agent_match=agent_match,
            confidence_delta=confidence_delta,
            latency_delta_ms=latency_delta_ms,
            latency_delta_pct=latency_delta_pct,

            cag_metadata=cag_result.get('metadata', {})
        )

        # =====================================================================
        # BUFFER & LOG
        # =====================================================================
        self.results_buffer.append(shadow_result)

        if self.debug:
            print(f"[SHADOW] {query[:50]}... | RAG: {rag_primary_agent} ({rag_latency_ms:.0f}ms) | "
                  f"CAG: {cag_primary_agent} ({cag_latency_ms:.0f}ms) | Match: {agent_match}")

        if len(self.results_buffer) >= self.buffer_size:
            # TODO: flush to Supabase cag_shadow_logs
            if self.debug:
                print(f"[SHADOW] Flushing {len(self.results_buffer)} results to Supabase...")
            self.results_buffer.clear()

        # =====================================================================
        # RETURN RAG RESULT TO USER (no disruption)
        # =====================================================================
        return rag_result, shadow_result

    async def flush_buffer(self) -> None:
        """Flush remaining results to Supabase"""
        if self.results_buffer:
            if self.debug:
                print(f"[SHADOW] Final flush of {len(self.results_buffer)} results to Supabase...")
            # TODO: write to cag_shadow_logs table
            self.results_buffer.clear()

# =============================================================================
# SHADOW MODE AGGREGATOR (30-day analysis)
# =============================================================================

class ShadowModeAnalyzer:
    """
    Analyzes 30 days of shadow mode data to determine if CAG is ready for pilot.

    Success criteria:
    - Intent classification accuracy ≥ 90%
    - End-to-end latency within 10% of RAG (CAG ≤ RAG * 1.10)
    - No critical errors (error rate < 0.1%)
    - Agent match rate ≥ 85% (CAG primary agent matches RAG)
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def analyze_results(
        self,
        shadow_results: List[ShadowResult],
        duration_days: int = 30
    ) -> Dict:
        """
        Analyze shadow mode results and compute go/no-go metrics.

        Args:
            shadow_results: list of ShadowResult objects
            duration_days: analysis period (default 30)

        Returns:
            {
                'duration_days': duration,
                'total_queries': count,
                'accuracy_metrics': {...},
                'latency_metrics': {...},
                'agent_match_rate': float,
                'error_rate': float,
                'go_decision': bool,
                'blockers': [list of issues],
                'recommendations': [list of actions]
            }
        """

        if not shadow_results:
            return {'error': 'No results to analyze'}

        total = len(shadow_results)

        # =====================================================================
        # ACCURACY: Agent Match Rate
        # =====================================================================
        matches = sum(1 for r in shadow_results if r.agent_match)
        agent_match_rate = matches / total if total > 0 else 0.0

        # =====================================================================
        # LATENCY: CAG vs RAG comparison
        # =====================================================================
        rag_latencies = [r.rag_latency_ms for r in shadow_results if r.rag_latency_ms > 0]
        cag_latencies = [r.cag_latency_ms for r in shadow_results if r.cag_latency_ms > 0]

        rag_p50 = sorted(rag_latencies)[len(rag_latencies)//2] if rag_latencies else 0
        rag_p95 = sorted(rag_latencies)[int(len(rag_latencies)*0.95)] if rag_latencies else 0
        rag_p99 = sorted(rag_latencies)[int(len(rag_latencies)*0.99)] if rag_latencies else 0

        cag_p50 = sorted(cag_latencies)[len(cag_latencies)//2] if cag_latencies else 0
        cag_p95 = sorted(cag_latencies)[int(len(cag_latencies)*0.95)] if cag_latencies else 0
        cag_p99 = sorted(cag_latencies)[int(len(cag_latencies)*0.99)] if cag_latencies else 0

        latency_delta_pct_avg = sum(r.latency_delta_pct for r in shadow_results) / total

        # Within target: CAG ≤ RAG * 1.10 (10% slower is acceptable)
        within_target = cag_p95 <= rag_p95 * 1.10

        # =====================================================================
        # ERROR RATE
        # =====================================================================
        errors = sum(1 for r in shadow_results if 'error' in r.rag_response_text.lower() or 'error' in r.cag_final_response.lower())
        error_rate = errors / total if total > 0 else 0.0

        # =====================================================================
        # CONFIDENCE DELTA
        # =====================================================================
        confidence_deltas = [r.confidence_delta for r in shadow_results]
        avg_confidence_delta = sum(confidence_deltas) / len(confidence_deltas) if confidence_deltas else 0.0

        # =====================================================================
        # DECISION LOGIC
        # =====================================================================
        blockers = []
        recommendations = []

        if agent_match_rate < 0.85:
            blockers.append(f"Agent match rate {agent_match_rate:.1%} < 85% threshold")
        else:
            recommendations.append(f"✅ Agent match rate {agent_match_rate:.1%} meets threshold")

        if not within_target:
            blockers.append(f"Latency CAG p95 {cag_p95:.0f}ms > RAG p95 {rag_p95:.0f}ms * 1.10")
        else:
            recommendations.append(f"✅ Latency CAG p95 {cag_p95:.0f}ms within 10% of RAG p95 {rag_p95:.0f}ms")

        if error_rate > 0.001:
            blockers.append(f"Error rate {error_rate:.1%} > 0.1% threshold")
        else:
            recommendations.append(f"✅ Error rate {error_rate:.1%} < 0.1% threshold")

        go_decision = len(blockers) == 0

        return {
            'duration_days': duration_days,
            'total_queries': total,
            'accuracy_metrics': {
                'agent_match_rate': agent_match_rate,
                'avg_confidence_delta': avg_confidence_delta
            },
            'latency_metrics': {
                'rag_p50_ms': rag_p50,
                'rag_p95_ms': rag_p95,
                'rag_p99_ms': rag_p99,
                'cag_p50_ms': cag_p50,
                'cag_p95_ms': cag_p95,
                'cag_p99_ms': cag_p99,
                'avg_delta_pct': latency_delta_pct_avg,
                'within_10pct_target': within_target
            },
            'error_rate': error_rate,
            'go_decision': go_decision,
            'blockers': blockers,
            'recommendations': recommendations,
            'next_phase': 'PILOT' if go_decision else 'TUNING_REQUIRED'
        }

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Shadow Mode Orchestrator ready.")
    print("Configure in maestro.py or main entrypoint.")
