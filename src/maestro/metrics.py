"""
Maestro OS v6.0 — Metrics Collection & Performance Profiling
Tracks execution time, consensus rate, token usage, and agent response times.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class AgentMetrics:
    """Metrics for individual agent execution."""
    agent_name: str
    start_time: str
    end_time: Optional[str] = None
    duration_secs: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    tokens_used: int = 0
    output_size_chars: int = 0
    error: Optional[str] = None


@dataclass
class ConsensusMetrics:
    """Metrics for consensus voting round."""
    aspect: str
    num_voters: int
    num_candidates: int
    votes_received: int
    votes_needed: int  # 3/5 threshold
    decision_made: bool
    escalated: bool
    duration_secs: float = 0.0


@dataclass
class ExecutionMetrics:
    """Metrics for complete workflow execution."""
    workflow_id: str
    project_id: str
    complexity_level: str  # simple, medium, complex
    num_agents: int

    start_time: str
    end_time: Optional[str] = None
    total_duration_secs: float = 0.0

    # Phase-level metrics
    fan_out_duration_secs: float = 0.0
    consensus_duration_secs: float = 0.0
    aggregate_duration_secs: float = 0.0

    # Agent metrics
    agent_metrics: List[AgentMetrics] = field(default_factory=list)

    # Consensus metrics
    consensus_rounds: List[ConsensusMetrics] = field(default_factory=list)

    # Token metrics
    total_tokens_used: int = 0
    tokens_budget: int = 0
    token_utilization_pct: float = 0.0

    # Consensus metrics
    total_decisions: int = 0
    auto_resolved: int = 0
    escalated: int = 0
    consensus_rate_pct: float = 0.0

    # ML inference metrics
    ml_routing_latency_ms: float = 0.0
    ml_duration_latency_ms: float = 0.0
    ml_risk_latency_ms: float = 0.0

    # Engineering analysis metrics
    engineering_analyses_executed: int = 0
    norm_checks_passed: int = 0
    what_if_scenarios_run: int = 0

    # Output metrics
    output_size_mb: float = 0.0
    artifacts_generated: List[str] = field(default_factory=list)

    # Quality metrics
    success: bool = False
    error: Optional[str] = None


@dataclass
class PerformanceReport:
    """Aggregated performance report for a workflow execution."""
    execution_metrics: ExecutionMetrics

    # Derived metrics
    execution_time_min: float = 0.0
    agents_per_minute: float = 0.0
    tokens_per_agent: float = 0.0
    avg_agent_response_time_secs: float = 0.0

    # Comparisons against targets
    target_execution_time_min: float = 15.0
    target_consensus_rate_pct: float = 85.0
    target_token_budget: int = 600_000
    target_agent_response_secs: float = 30.0

    # Pass/fail
    execution_time_met: bool = False
    consensus_rate_met: bool = False
    token_budget_met: bool = False
    agent_response_met: bool = False
    overall_success: bool = False

    def __post_init__(self):
        """Calculate derived metrics and targets."""
        self.execution_time_min = self.execution_metrics.total_duration_secs / 60.0

        if self.execution_metrics.num_agents > 0:
            self.agents_per_minute = (
                self.execution_metrics.num_agents / self.execution_time_min
                if self.execution_time_min > 0 else 0
            )

        if self.execution_metrics.num_agents > 0:
            self.tokens_per_agent = (
                self.execution_metrics.total_tokens_used / self.execution_metrics.num_agents
            )

        if len(self.execution_metrics.agent_metrics) > 0:
            avg_duration = sum(a.duration_secs for a in self.execution_metrics.agent_metrics) / len(self.execution_metrics.agent_metrics)
            self.avg_agent_response_time_secs = avg_duration

        # Set targets based on complexity
        if self.execution_metrics.complexity_level == "simple":
            self.target_execution_time_min = 8.0
            self.target_token_budget = 300_000
        elif self.execution_metrics.complexity_level == "medium":
            self.target_execution_time_min = 10.0
            self.target_token_budget = 450_000
        else:  # complex
            self.target_execution_time_min = 15.0
            self.target_token_budget = 600_000

        # Evaluate targets
        self.execution_time_met = self.execution_time_min <= self.target_execution_time_min
        self.consensus_rate_met = self.execution_metrics.consensus_rate_pct >= self.target_consensus_rate_pct
        self.token_budget_met = self.execution_metrics.total_tokens_used <= self.target_token_budget
        self.agent_response_met = self.avg_agent_response_time_secs <= self.target_agent_response_secs

        self.overall_success = (
            self.execution_metrics.success and
            self.execution_time_met and
            self.consensus_rate_met and
            self.token_budget_met and
            self.agent_response_met
        )


class MetricsCollector:
    """Collects and aggregates metrics throughout workflow execution."""

    def __init__(self, workflow_id: str, project_id: str, num_agents: int, complexity_level: str):
        """Initialize metrics collector."""
        self.execution_metrics = ExecutionMetrics(
            workflow_id=workflow_id,
            project_id=project_id,
            num_agents=num_agents,
            complexity_level=complexity_level,
            start_time=datetime.utcnow().isoformat(),
            tokens_budget=self._calculate_budget(num_agents)
        )

    def _calculate_budget(self, num_agents: int) -> int:
        """Calculate token budget based on agent count."""
        if num_agents <= 8:
            return 300_000
        elif num_agents <= 12:
            return 450_000
        else:
            return 600_000

    def add_agent_metric(self, agent_name: str, duration_secs: float, tokens: int, status: str, output_chars: int = 0, error: str = None):
        """Record agent execution metric."""
        metric = AgentMetrics(
            agent_name=agent_name,
            start_time=datetime.utcnow().isoformat(),
            duration_secs=duration_secs,
            tokens_used=tokens,
            status=status,
            output_size_chars=output_chars,
            error=error
        )
        metric.end_time = datetime.utcnow().isoformat()
        self.execution_metrics.agent_metrics.append(metric)
        self.execution_metrics.total_tokens_used += tokens

    def add_consensus_metric(self, aspect: str, num_voters: int, num_candidates: int, decision_made: bool, escalated: bool, duration_secs: float):
        """Record consensus voting metric."""
        metric = ConsensusMetrics(
            aspect=aspect,
            num_voters=num_voters,
            num_candidates=num_candidates,
            votes_received=num_voters,
            votes_needed=3,  # 3/5 threshold
            decision_made=decision_made,
            escalated=escalated,
            duration_secs=duration_secs
        )
        self.execution_metrics.consensus_rounds.append(metric)

        self.execution_metrics.total_decisions += 1
        if decision_made and not escalated:
            self.execution_metrics.auto_resolved += 1
        if escalated:
            self.execution_metrics.escalated += 1

    def set_phase_duration(self, phase: str, duration_secs: float):
        """Record phase duration."""
        if phase == "fan_out":
            self.execution_metrics.fan_out_duration_secs = duration_secs
        elif phase == "consensus":
            self.execution_metrics.consensus_duration_secs = duration_secs
        elif phase == "aggregate":
            self.execution_metrics.aggregate_duration_secs = duration_secs

    def set_ml_metrics(self, routing_ms: float, duration_ms: float, risk_ms: float):
        """Record ML inference latencies."""
        self.execution_metrics.ml_routing_latency_ms = routing_ms
        self.execution_metrics.ml_duration_latency_ms = duration_ms
        self.execution_metrics.ml_risk_latency_ms = risk_ms

    def set_engineering_metrics(self, analyses: int, norm_checks: int, scenarios: int):
        """Record engineering analysis counts."""
        self.execution_metrics.engineering_analyses_executed = analyses
        self.execution_metrics.norm_checks_passed = norm_checks
        self.execution_metrics.what_if_scenarios_run = scenarios

    def add_artifact(self, artifact_name: str):
        """Record generated artifact."""
        self.execution_metrics.artifacts_generated.append(artifact_name)

    def finalize(self, success: bool, error: Optional[str] = None):
        """Finalize metrics collection."""
        self.execution_metrics.end_time = datetime.utcnow().isoformat()
        self.execution_metrics.total_duration_secs = (
            sum(a.duration_secs for a in self.execution_metrics.agent_metrics) +
            sum(c.duration_secs for c in self.execution_metrics.consensus_rounds)
        )

        self.execution_metrics.token_utilization_pct = (
            (self.execution_metrics.total_tokens_used / self.execution_metrics.tokens_budget) * 100
            if self.execution_metrics.tokens_budget > 0 else 0
        )

        if self.execution_metrics.total_decisions > 0:
            self.execution_metrics.consensus_rate_pct = (
                (self.execution_metrics.auto_resolved / self.execution_metrics.total_decisions) * 100
            )

        self.execution_metrics.success = success
        self.execution_metrics.error = error

    def get_report(self) -> PerformanceReport:
        """Generate performance report."""
        return PerformanceReport(self.execution_metrics)

    def to_json(self) -> str:
        """Serialize metrics to JSON."""
        data = {
            "workflow_id": self.execution_metrics.workflow_id,
            "project_id": self.execution_metrics.project_id,
            "complexity_level": self.execution_metrics.complexity_level,
            "num_agents": self.execution_metrics.num_agents,
            "start_time": self.execution_metrics.start_time,
            "end_time": self.execution_metrics.end_time,
            "total_duration_secs": self.execution_metrics.total_duration_secs,
            "total_tokens_used": self.execution_metrics.total_tokens_used,
            "token_utilization_pct": self.execution_metrics.token_utilization_pct,
            "consensus_rate_pct": self.execution_metrics.consensus_rate_pct,
            "auto_resolved": self.execution_metrics.auto_resolved,
            "escalated": self.execution_metrics.escalated,
            "success": self.execution_metrics.success,
        }
        return json.dumps(data, indent=2)

    def format_summary(self) -> str:
        """Format human-readable summary."""
        report = self.get_report()

        lines = [
            "=" * 60,
            "MAESTRO OS v6.0 — EXECUTION METRICS",
            "=" * 60,
            "",
            f"Workflow ID: {self.execution_metrics.workflow_id}",
            f"Project: {self.execution_metrics.project_id}",
            f"Complexity: {self.execution_metrics.complexity_level.upper()}",
            f"Agents: {self.execution_metrics.num_agents}",
            "",
            "EXECUTION TIME:",
            f"  Total: {report.execution_time_min:.1f} min (target: {report.target_execution_time_min:.1f} min) {'✓' if report.execution_time_met else '✗'}",
            f"  Fan-out: {self.execution_metrics.fan_out_duration_secs:.1f}s",
            f"  Consensus: {self.execution_metrics.consensus_duration_secs:.1f}s",
            f"  Aggregate: {self.execution_metrics.aggregate_duration_secs:.1f}s",
            f"  Avg agent: {report.avg_agent_response_time_secs:.1f}s (target: {report.target_agent_response_secs:.0f}s) {'✓' if report.agent_response_met else '✗'}",
            "",
            "CONSENSUS VOTING:",
            f"  Auto-resolved: {self.execution_metrics.auto_resolved}/{self.execution_metrics.total_decisions} ({self.execution_metrics.consensus_rate_pct:.0f}%) (target: {report.target_consensus_rate_pct:.0f}%) {'✓' if report.consensus_rate_met else '✗'}",
            f"  Escalated: {self.execution_metrics.escalated}",
            "",
            "TOKEN USAGE:",
            f"  Used: {self.execution_metrics.total_tokens_used:,} / {report.target_token_budget:,} ({self.execution_metrics.token_utilization_pct:.0f}%) {'✓' if report.token_budget_met else '✗'}",
            f"  Per agent: {report.tokens_per_agent:,.0f}",
            "",
            "ML INFERENCE:",
            f"  Routing: {self.execution_metrics.ml_routing_latency_ms:.0f}ms",
            f"  Duration: {self.execution_metrics.ml_duration_latency_ms:.0f}ms",
            f"  Risk: {self.execution_metrics.ml_risk_latency_ms:.0f}ms",
            "",
            "ENGINEERING ANALYSIS:",
            f"  Structural analyses: {self.execution_metrics.engineering_analyses_executed}",
            f"  Norm checks: {self.execution_metrics.norm_checks_passed}",
            f"  What-if scenarios: {self.execution_metrics.what_if_scenarios_run}",
            "",
            "ARTIFACTS:",
            f"  Generated: {len(self.execution_metrics.artifacts_generated)} outputs",
            f"  Size: {self.execution_metrics.output_size_mb:.1f} MB",
            "",
            f"Status: {'✓ SUCCESS' if report.overall_success else '✗ FAILED'}",
            "" if not self.execution_metrics.error else f"Error: {self.execution_metrics.error}",
            "=" * 60,
        ]

        return "\n".join(lines)
