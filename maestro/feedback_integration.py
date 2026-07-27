"""
Phase 3.5: Feedback Integration for Tie-Breaker

Tracks user corrections and feedback from tie-breaker decisions.
Implements score boosting based on feedback history and weekly
statistical analysis to improve routing over time.

Author: Maestro Team
Version: v1.0
Status: Production-Ready
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import asyncpg
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Integer

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Type of feedback."""
    APPROVED = "approved"  # User confirmed tie-breaker decision
    CORRECTED = "corrected"  # User selected different agent
    TIMEOUT = "timeout"  # Tie-breaker timed out
    ERROR = "error"  # Tie-breaker API error


@dataclass
class FeedbackRecord:
    """User feedback on routing decision."""
    routing_id: str
    query: str
    tiebreaker_decision: str  # Agent selected by tie-breaker
    user_correction: Optional[str]  # Agent user actually selected
    feedback_type: FeedbackType
    user_id: str
    confidence: float  # Tie-breaker confidence
    adjusted_scores: Dict[str, float]
    timestamp: datetime
    week_number: int


class FeedbackAnalyzer:
    """Analyzes user feedback and learns from corrections."""

    def __init__(self, db_pool: asyncpg.Pool):
        """
        Initialize feedback analyzer.

        Args:
            db_pool: asyncpg connection pool to Supabase
        """
        self.db_pool = db_pool

    async def record_feedback(
        self,
        routing_id: str,
        query: str,
        tiebreaker_decision: str,
        user_correction: Optional[str],
        user_id: str,
        confidence: float,
        adjusted_scores: Dict[str, float]
    ) -> None:
        """
        Record user feedback on routing decision.

        Args:
            routing_id: ID of routing decision
            query: Original routing query
            tiebreaker_decision: Agent selected by tie-breaker
            user_correction: Agent user actually selected (if different)
            user_id: ID of user providing feedback
            confidence: Tie-breaker confidence
            adjusted_scores: Final adjusted scores used
        """
        # Determine feedback type
        if user_correction is None:
            feedback_type = FeedbackType.APPROVED
        elif user_correction == tiebreaker_decision:
            feedback_type = FeedbackType.APPROVED
        else:
            feedback_type = FeedbackType.CORRECTED

        week_number = datetime.utcnow().isocalendar()[1]

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO routing_feedback (
                        routing_id, query, tiebreaker_invoked,
                        tiebreaker_decision, user_id, user_approved,
                        correction_agent_id, correction_confidence,
                        adjusted_scores, feedback_type, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                    routing_id,
                    query,
                    True,  # tiebreaker_invoked
                    tiebreaker_decision,
                    user_id,
                    feedback_type == FeedbackType.APPROVED,
                    user_correction,
                    confidence,
                    adjusted_scores,
                    feedback_type.value,
                    datetime.utcnow()
                )

                # Update tiebreaker_metrics
                await self._update_metrics(
                    tiebreaker_decision,
                    user_correction,
                    week_number
                )

                logger.info(
                    f"Recorded feedback: routing={routing_id}, "
                    f"type={feedback_type.value}"
                )

        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            raise

    async def _update_metrics(
        self,
        tiebreaker_decision: str,
        user_correction: Optional[str],
        week_number: int
    ) -> None:
        """Update weekly metrics for tie-breaker."""
        is_success = user_correction is None or user_correction == tiebreaker_decision

        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tiebreaker_metrics (
                    week_number, invocation_count, success_count, failure_count
                ) VALUES ($1, 1, $2, $3)
                ON CONFLICT (week_number) DO UPDATE SET
                    invocation_count = tiebreaker_metrics.invocation_count + 1,
                    success_count = tiebreaker_metrics.success_count + $2,
                    failure_count = tiebreaker_metrics.failure_count + $3
                """,
                week_number,
                1 if is_success else 0,
                0 if is_success else 1
            )

    async def get_approval_stats(
        self,
        agent_id: str,
        window_days: int = 7
    ) -> Dict:
        """
        Get approval statistics for agent.

        Args:
            agent_id: Agent to analyze
            window_days: Window for analysis (default 7 days)

        Returns:
            {
                'approval_rate': 0.87,
                'total_decisions': 150,
                'approvals': 130,
                'corrections': 20,
                'recent_wins': 5,  # Last 3 days
                'recent_losses': 1,
                'trend': 'up'  # week-over-week
            }
        """
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        recent_cutoff = datetime.utcnow() - timedelta(days=3)

        try:
            async with self.db_pool.acquire() as conn:
                # Total stats for window
                row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as total_decisions,
                        SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) as approvals,
                        SUM(CASE WHEN NOT user_approved THEN 1 ELSE 0 END) as corrections
                    FROM routing_feedback
                    WHERE (tiebreaker_decision = $1 OR correction_agent_id = $1)
                        AND tiebreaker_invoked = true
                        AND timestamp >= $2
                    """,
                    agent_id,
                    cutoff_date
                )

                total = row["total_decisions"] or 0
                approvals = row["approvals"] or 0

                # Recent stats
                recent_row = await conn.fetchrow(
                    """
                    SELECT
                        SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) as recent_wins,
                        SUM(CASE WHEN NOT user_approved THEN 1 ELSE 0 END) as recent_losses
                    FROM routing_feedback
                    WHERE (tiebreaker_decision = $1 OR correction_agent_id = $1)
                        AND tiebreaker_invoked = true
                        AND timestamp >= $2
                    """,
                    agent_id,
                    recent_cutoff
                )

                # Trend (previous week vs current week)
                prev_week_row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as prev_total,
                        SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) as prev_approvals
                    FROM routing_feedback
                    WHERE (tiebreaker_decision = $1 OR correction_agent_id = $1)
                        AND tiebreaker_invoked = true
                        AND timestamp >= $2 - INTERVAL '7 days'
                        AND timestamp < $2
                    """,
                    agent_id,
                    cutoff_date
                )

                approval_rate = approvals / total if total > 0 else 0.0

                # Calculate trend
                prev_total = prev_week_row["prev_total"] or 0
                prev_approvals = prev_week_row["prev_approvals"] or 0
                prev_rate = prev_approvals / prev_total if prev_total > 0 else 0.0

                trend = "up" if approval_rate > prev_rate else (
                    "down" if approval_rate < prev_rate else "stable"
                )

                return {
                    "approval_rate": approval_rate,
                    "total_decisions": total,
                    "approvals": approvals,
                    "corrections": row["corrections"] or 0,
                    "recent_wins": recent_row["recent_wins"] or 0,
                    "recent_losses": recent_row["recent_losses"] or 0,
                    "trend": trend
                }

        except Exception as e:
            logger.error(f"Error getting approval stats: {e}")
            return {
                "approval_rate": 0.0,
                "total_decisions": 0,
                "approvals": 0,
                "corrections": 0,
                "recent_wins": 0,
                "recent_losses": 0,
                "trend": "unknown"
            }


class ScoreBoosting:
    """Boosts scores based on feedback history."""

    def __init__(self, feedback_analyzer: FeedbackAnalyzer):
        """
        Initialize score boosting.

        Args:
            feedback_analyzer: Reference to FeedbackAnalyzer instance
        """
        self.analyzer = feedback_analyzer

    async def get_feedback_boost(
        self,
        agent_id: str,
        recent_window_days: int = 7
    ) -> float:
        """
        Calculate score boost multiplier from feedback.

        Args:
            agent_id: Agent to evaluate
            recent_window_days: Window for analysis

        Returns:
            Multiplier (0.95 - 1.05) for score adjustment
        """
        stats = await self.analyzer.get_approval_stats(
            agent_id,
            recent_window_days
        )

        approval_rate = stats["approval_rate"]
        recent_wins = stats["recent_wins"]
        recent_losses = stats["recent_losses"]

        multiplier = 1.0

        # Boost for high approval rate
        if approval_rate > 0.90:
            multiplier += 0.04
        elif approval_rate > 0.85:
            multiplier += 0.03
        elif approval_rate > 0.80:
            multiplier += 0.01

        # Boost for recent wins
        if recent_wins >= 5:
            multiplier += 0.02
        elif recent_wins >= 3:
            multiplier += 0.01

        # Penalty for recent losses
        if recent_losses >= 3:
            multiplier -= 0.04
        elif recent_losses >= 2:
            multiplier -= 0.02
        elif recent_losses == 1:
            multiplier -= 0.01

        # Trend adjustment
        if stats["trend"] == "up":
            multiplier += 0.01
        elif stats["trend"] == "down":
            multiplier -= 0.01

        return max(0.95, min(1.05, multiplier))


class WeeklyRecommendationJob:
    """Analyzes tie-breaker performance and recommends adjustments."""

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        feedback_analyzer: FeedbackAnalyzer
    ):
        """
        Initialize job.

        Args:
            db_pool: Database connection pool
            feedback_analyzer: Reference to FeedbackAnalyzer
        """
        self.db_pool = db_pool
        self.analyzer = feedback_analyzer

    async def run_weekly_analysis(self) -> Dict:
        """
        Run comprehensive weekly analysis.

        Executes every Monday 08:00 UTC.

        Returns:
            {
                'week_number': 30,
                'overall_approval_rate': 0.84,
                'recommendations': [
                    {
                        'type': 'gap_threshold',
                        'action': 'increase',
                        'current': 0.10,
                        'suggested': 0.12,
                        'reason': 'Approval rate below 80% target'
                    }
                ],
                'agent_performance': [
                    {
                        'agent_id': 'agente-saneamento',
                        'approval_rate': 0.87,
                        'invocations': 45,
                        'trend': 'up'
                    }
                ]
            }
        """
        try:
            week_number = datetime.utcnow().isocalendar()[1]

            async with self.db_pool.acquire() as conn:
                # Get overall metrics
                metrics = await conn.fetchrow(
                    """
                    SELECT
                        invocation_count,
                        success_count,
                        failure_count,
                        avg_latency_ms,
                        cost_usd
                    FROM tiebreaker_metrics
                    WHERE week_number = $1
                    """,
                    week_number
                )

                invocations = metrics["invocation_count"] or 0
                successes = metrics["success_count"] or 0
                overall_approval = successes / invocations if invocations > 0 else 0.0

                # Get per-agent performance
                agent_rows = await conn.fetch(
                    """
                    SELECT
                        COALESCE(tiebreaker_decision, correction_agent_id) as agent_id,
                        COUNT(*) as invocations,
                        SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) as approvals
                    FROM routing_feedback
                    WHERE tiebreaker_invoked = true
                        AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY agent_id
                    """
                )

                agent_performance = []
                for row in agent_rows:
                    agent_id = row["agent_id"]
                    invocations = row["invocations"]
                    approvals = row["approvals"] or 0
                    approval_rate = approvals / invocations if invocations > 0 else 0.0

                    # Get trend
                    stats = await self.analyzer.get_approval_stats(agent_id, 14)

                    agent_performance.append({
                        "agent_id": agent_id,
                        "approval_rate": approval_rate,
                        "invocations": invocations,
                        "trend": stats["trend"]
                    })

            # Generate recommendations
            recommendations = self._generate_recommendations(
                overall_approval,
                metrics,
                agent_performance
            )

            # Store results
            await self._store_analysis_results(
                week_number,
                overall_approval,
                recommendations
            )

            logger.info(
                f"Weekly analysis complete: approval={overall_approval:.2%}, "
                f"recommendations={len(recommendations)}"
            )

            return {
                "week_number": week_number,
                "overall_approval_rate": overall_approval,
                "invocations": invocations,
                "recommendations": recommendations,
                "agent_performance": agent_performance
            }

        except Exception as e:
            logger.error(f"Error in weekly analysis: {e}")
            raise

    def _generate_recommendations(
        self,
        approval_rate: float,
        metrics: Dict,
        agent_performance: List[Dict]
    ) -> List[Dict]:
        """Generate actionable recommendations."""
        recommendations = []

        # Gap threshold adjustment
        if approval_rate < 0.80:
            recommendations.append({
                "type": "gap_threshold",
                "action": "increase",
                "current": 0.10,
                "suggested": 0.12,
                "reason": f"Approval rate {approval_rate:.1%} below 80% target"
            })
        elif approval_rate > 0.90:
            recommendations.append({
                "type": "gap_threshold",
                "action": "decrease",
                "current": 0.10,
                "suggested": 0.08,
                "reason": f"Approval rate {approval_rate:.1%} well above target"
            })

        # Latency recommendations
        latency = metrics.get("avg_latency_ms", 0)
        if latency > 400:
            recommendations.append({
                "type": "latency_optimization",
                "action": "reduce_tokens",
                "current": 500,
                "suggested": 300,
                "reason": f"Avg latency {latency:.0f}ms approaching 500ms limit"
            })

        # Agent-specific recommendations
        for agent in agent_performance:
            if agent["approval_rate"] < 0.75 and agent["invocations"] > 10:
                recommendations.append({
                    "type": "agent_review",
                    "agent_id": agent["agent_id"],
                    "action": "review_routing_rules",
                    "reason": f"Low approval rate {agent['approval_rate']:.1%}"
                })

        return recommendations

    async def _store_analysis_results(
        self,
        week_number: int,
        approval_rate: float,
        recommendations: List[Dict]
    ) -> None:
        """Store analysis results for reporting."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tiebreaker_analysis (
                    week_number, overall_approval_rate, recommendations,
                    timestamp
                ) VALUES ($1, $2, $3, $4)
                ON CONFLICT (week_number) DO UPDATE SET
                    overall_approval_rate = $2,
                    recommendations = $3,
                    timestamp = $4
                """,
                week_number,
                approval_rate,
                recommendations,
                datetime.utcnow()
            )


# Example usage
if __name__ == "__main__":
    async def example():
        """Example feedback tracking."""
        # Would be initialized with real connection pool
        # analyzer = FeedbackAnalyzer(db_pool)
        # await analyzer.record_feedback(...)
        print("Feedback integration module ready for integration")

    asyncio.run(example())
