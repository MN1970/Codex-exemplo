# Maestro OS v6.0 — API Reference

**Version:** 6.0.0  
**Release Date:** 2026-07-26  
**Status:** Beta  

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Workflow DSL](#workflow-dsl)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Error Handling](#error-handling)
7. [Performance Tuning](#performance-tuning)
8. [Example Workflows](#example-workflows)

---

## Architecture Overview

Maestro OS v6.0 is a 5-layer orchestration system for parallel multi-agent analysis:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Layer 5: ML Intelligence                         │
│  (Routing Adapter, Duration Predictor, Risk Classifier)                 │
├─────────────────────────────────────────────────────────────────────────┤
│                        Layer 4: Aggregation                             │
│  (Output consolidation: DOCX, JSON, Matrix)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                        Layer 3: Consensus Engine                        │
│  (Votação 3/5 super-maioria, escalação, tie-breaking)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                        Layer 2: Orchestration                           │
│  (Fan-out scheduler, Queue executor, Rate limiter)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                   Layer 1: Complexity Detection                         │
│  (Segment detection, agent selection, token budgeting)                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Characteristics

- **Dynamic Agent Scaling:** 8–16 agents based on project complexity
- **Parallel Execution:** Max 8 concurrent agents with queue buffer up to 16
- **Consensus Voting:** 3/5 super-majority threshold with subset-relevant voters
- **Rate Limiting:** Exponential backoff (2s, 4s, 8s, 16s) to prevent API throttling
- **ML Integration:** Real-time routing, duration, and risk predictions
- **Engineering Analysis:** Structural calculations, normative compliance, what-if simulation

---

## Core Components

### 1. ComplexityDetector

Analyzes project description to detect segments and select agent pool.

```python
from src.maestro.detector import ComplexityDetector

detector = ComplexityDetector()
detection = detector.detect_from_description(
    "Porto terminal Paranaguá + Energia + Saneamento"
)

print(detection.num_segments)        # 3
print(detection.complexity_level)    # "medium"
print(len(detection.agents_selected))  # 12
print(detection.token_budget)        # 450_000
```

**Output:** `DetectionResult` with:
- `num_segments`: int (1-5+)
- `complexity_level`: str ("simple", "medium", "complex")
- `agents_selected`: List[Dict] with agent names and tiers
- `token_budget`: int (300k-600k)
- `reasoning`: str (explanation)

---

### 2. WorkflowParser

Parses YAML workflow definitions into validated AST.

```python
from src.maestro.parser import WorkflowParser

parser = WorkflowParser()
workflow = parser.parse(yaml_string)

# Validates against:
# - Known agents (S1-S11, A1-A10)
# - Project types
# - Phase sequencing
# - Consensus thresholds
```

**YAML Structure:**
```yaml
project:
  id: "proj-001"
  type: "multi_segment"
  segments: ["S7", "S10", "S9"]

agents:
  - name: "agente-portos"
    tier: "sonnet"

phases:
  - name: "fan_out"
    agents: ["agente-portos", ...]
  - name: "consensus"
    aspects:
      - aspect: "orçamento"
        voters: ["agente-portos", "manta-05"]
        threshold: 3
  - name: "aggregate"
    output_format: "docx+json"
```

---

### 3. MaestroOrchestrator

End-to-end workflow execution coordinator.

```python
from src.maestro.orchestrator import MaestroOrchestrator

orchestrator = MaestroOrchestrator()
execution = orchestrator.execute_workflow(
    project_id="proj-porto",
    description="Terminal portuário com dragagem",
    workflow_yaml=yaml_string
)

# Access results
print(execution.consensus_results)
print(execution.aggregated_output)
print(execution.metrics)
```

**Execution Flow:**
1. Detect complexity (Detector)
2. Parse workflow (Parser)
3. Fan-out agents (QueueExecutor, max 8 concurrent)
4. Consensus voting (ConsensusEngine, 3/5 threshold)
5. Aggregate outputs (DOCX, JSON, Matrix)

---

### 4. ConsensusEngine

Super-majority voting (3/5) with confidence weighting.

```python
from src.maestro.consensus import ConsensusEngine, Candidate, Vote

engine = ConsensusEngine()

candidates = [
    Candidate("R$ 500M", confidence=0.85, source="S6"),
    Candidate("R$ 1.15B", confidence=0.88, source="A5"),
    Candidate("R$ 1.10B", confidence=0.80, source="A15"),
]

votes = [
    Vote("S6", candidates[0], 0.85),
    Vote("A5", candidates[1], 0.88),
    Vote("A15", candidates[2], 0.80),
]

result = engine.execute_vote(votes, threshold=3, aspect="orçamento")
# result.status: "decided", "escalated", or "tied"
# result.winner: Candidate (if decided)
# result.escalation_reason: str (if escalated)
```

---

### 5. QueueExecutor

Manages concurrent agent execution with rate limiting.

```python
from src.maestro.queue_executor import QueueExecutor

executor = QueueExecutor(max_workers=8, max_queue=16)

# Enqueue tasks (up to 16 buffered)
executor.enqueue_task(Task("task-001", "agente-portos", {...}))
executor.enqueue_task(Task("task-002", "agente-energia", {...}))

# Execute all (max 8 simultaneous)
results = executor.execute_all()

# Results with rate-limit recovery
for result in results:
    print(result.agent_name, result.status)  # "completed" or "failed"
```

---

### 6. MLInferenceService

Real-time ML predictions (routing, duration, risk).

```python
from src.maestro.ml_inference import InferenceService
from src.maestro.ml_trainer import RoutingModel, DurationPredictor, RiskClassifier

service = InferenceService(
    RoutingModel(),
    DurationPredictor(),
    RiskClassifier()
)

result = service.infer("proj-id", "Porto + Energia + Saneamento")

print(result.routing.suggested_agents)     # ["agente-portos", "agente-energia", ...]
print(result.duration.estimated_minutes)   # 580 (9.7 hours)
print(result.risk.risk_score)              # 65.0 (HIGH)
print(result.risk.risk_factors)            # ["Risco geotécnico", ...]
print(result.risk.mitigations)             # ["Realizar sondagens adicionais", ...]
```

---

### 7. ComplianceChecker

Validates projects against normative rules (Lei 12.334, ICOLD, CBDB).

```python
from src.maestro.norm_parser import ComplianceChecker

checker = ComplianceChecker()

compliant, warnings, violations = checker.check_compliance(
    project_type="barragem",
    project_features={"pae": True, "piezometro": True}
)

print(compliant)    # ["✓ lei-12334-001: ...", ...]
print(violations)   # ["✗ lei-12334-003: RSB não realizada", ...]

# Generate report
report = checker.generate_compliance_report(
    project_id="proj-001",
    project_type="barragem",
    features=features
)
print(report)
```

---

### 8. WhatIfSimulator

Scenario analysis: delay, budget, risk impacts.

```python
from src.maestro.simulator import WhatIfSimulator, Scenario, ScenarioType

simulator = WhatIfSimulator()

scenarios = [
    Scenario("sc-delay", ScenarioType.DELAY, "3-month delay", 
             delay_days=90, affected_agent="S7"),
    Scenario("sc-budget", ScenarioType.BUDGET_OVERRUN, "Budget +15%",
             budget_increase_pct=15.0),
    Scenario("sc-risk", ScenarioType.RISK_ESCALATION, "Risk +10%",
             risk_increase_pct=10.0),
]

results = simulator.compare_scenarios(
    base_duration_min=6300,
    base_cost=1_150_000_000,
    base_risk=0.35,
    scenarios=scenarios,
    segments_involved=["S7", "S10", "S9"],
    risk_level="medium"
)

for result in results:
    print(f"{result.scenario.name}:")
    print(f"  Duration: +{result.duration_increase_pct:.1f}%")
    print(f"  Cost: +{result.cost_increase_pct:.1f}%")
    print(f"  Risk: +{result.risk_increase_pct:.1f}%")
    print(f"  Recommendation: {result.recommendation}")
```

---

## Workflow DSL

### YAML Syntax

```yaml
project:
  id: "proj-unique-id"
  type: "infrastructure|industrial|service|multi_segment"
  segments: ["S1", "S7", "S10"]
  description: "Project description"

agents:
  - name: "agent-name"
    tier: "sonnet|opus|haiku"
    role: "primary|secondary|support"

phases:
  - name: "fan_out"
    parallel: true
    agents: ["agent1", "agent2"]
    timeout_secs: 600

  - name: "consensus"
    aspects:
      - aspect: "orçamento"
        voters: ["S6", "S10", "A5", "A15"]
        candidates: 5
        threshold: 3

  - name: "aggregate"
    format: "docx+json"
    include_metrics: true
    include_summary: true
```

### Valid Project Types

- `infrastructure_linear` (rodovia, ferrovia)
- `infrastructure_oae` (pontes, viadutos)
- `industrial` (barragem, energia)
- `saneamento` (ETA, ETE)
- `multi_segment` (2+ tipos)

### Valid Segments

- S1–S4: Infrastructure (rodovia, OAE, ferrovia, metrô)
- S5: Imobiliário
- S6–S11: Verticals (edificações, portos, aeroportos, saneamento, energia, barragens)

---

## API Reference

### MaestroOrchestrator.execute_workflow()

Execute a complete workflow from start to finish.

```python
def execute_workflow(
    project_id: str,
    description: str,
    workflow_yaml: str,
    token_budget: Optional[int] = None,
    timeout_secs: int = 900
) -> WorkflowExecution:
    """
    Args:
        project_id: Unique project identifier
        description: Project description (used by detector)
        workflow_yaml: YAML workflow definition
        token_budget: Token budget override (default: auto-calculated)
        timeout_secs: Total execution timeout (default: 15 min)

    Returns:
        WorkflowExecution with results, metrics, and timing

    Raises:
        ValueError: Invalid workflow or project type
        TimeoutError: Execution exceeded timeout
        RateLimitError: API rate limit exceeded (retried with backoff)
    """
```

### ConsensusEngine.execute_vote()

Execute consensus voting for aspect decision.

```python
def execute_vote(
    votes: List[Vote],
    threshold: int = 3,
    aspect: str = "decision"
) -> ConsensusResult:
    """
    Args:
        votes: List of Vote objects from voters
        threshold: Votes needed for auto-decision (default: 3 of 5)
        aspect: Aspect being voted on (for logging)

    Returns:
        ConsensusResult with status (decided/escalated/tied), winner, reasoning
    """
```

### MLInferenceService.infer()

Predict routing, duration, and risk for project.

```python
def infer(
    project_id: str,
    description: str
) -> InferenceResult:
    """
    Args:
        project_id: Project identifier
        description: Project description

    Returns:
        InferenceResult with:
        - routing: RoutingSuggestion (agents, confidence, alternatives)
        - duration: DurationEstimate (minutes, confidence interval)
        - risk: RiskAssessment (score 0-100, factors, mitigations)
    """
```

### WhatIfSimulator.compare_scenarios()

Compare multiple scenarios' impacts.

```python
def compare_scenarios(
    base_duration_min: int,
    base_cost: float,
    base_risk: float,
    scenarios: List[Scenario],
    segments_involved: List[str],
    risk_level: str = "medium"
) -> List[ScenarioResult]:
    """
    Args:
        base_duration_min: Baseline project duration (minutes)
        base_cost: Baseline project cost (currency)
        base_risk: Baseline project risk (0-1)
        scenarios: Scenarios to simulate
        segments_involved: Segments affected
        risk_level: Risk level (low, medium, high)

    Returns:
        List of ScenarioResult ordered by impact (highest first)
    """
```

---

## Configuration

### Agent Pool (20 total)

**Vertical Agents (S1–S11):**
- S1: agente-infraestrutura (rodovia)
- S2: agente-infraestrutura (OAE)
- S3: agente-infraestrutura (ferrovia)
- S4: agente-infraestrutura (metrô)
- S6: agente-edificacoes
- S7: agente-portos
- S8: agente-aeroportos
- S9: agente-saneamento
- S10: agente-energia
- S11: agente-barragens

**Horizontal Agents (A1–A15):**
- A1: manta-01 (claims)
- A2: manta-02 (contratual)
- A4: manta-04 (imobiliário)
- A5: manta-05 (orçamento)
- A6: manta-06 (modelagem)
- A7: manta-07 (cronograma)
- A13: manta-13 (BD)
- A14: manta-14 (apresentações)
- A15: manta-15 (advisory)

### Token Budgets (Dynamic)

| Complexity | Agents | Budget | Per-Agent |
|-----------|--------|--------|-----------|
| Simple    | 8      | 300k   | 37.5k     |
| Medium    | 12     | 450k   | 37.5k     |
| Complex   | 16     | 600k   | 37.5k     |

### Concurrency Limits

- **Max Concurrent Workers:** 8 agents simultaneously
- **Queue Buffer:** Up to 16 queued tasks
- **Rate Limit Recovery:** Exponential backoff (2s → 4s → 8s → 16s)
- **Agent Response Timeout:** 30 seconds per agent

---

## Error Handling

### Exception Hierarchy

```
MaestroException (base)
├─ DetectionError (complexity detection failed)
├─ WorkflowValidationError (invalid YAML/agents)
├─ ConsensusError (voting failed to converge)
├─ ExecutionError (agent execution failed)
├─ RateLimitError (API throttling, auto-retried)
├─ TimeoutError (execution exceeded timeout)
└─ ComplianceError (normative violation)
```

### Recovery Strategies

**Rate Limiting (429):**
- Automatic exponential backoff: 2s → 4s → 8s → 16s
- Max 3 retries per task
- Queue buffering up to 16 tasks

**Consensus Escalation (<3/5):**
- Automatic escalation to human review
- Logged in audit trail
- Retry with expanded voter set

**Agent Timeout (>30s):**
- Automatic timeout and mark as "failed"
- Continue with remaining agents
- Log in execution metrics

---

## Performance Tuning

### Target Metrics

| Metric | Simple (8a) | Medium (12a) | Complex (16a) |
|--------|------------|-------------|--------------|
| Execution Time | <8 min | <10 min | <15 min |
| Consensus Rate | >85% | >85% | >85% |
| Token Usage | <300k | <450k | <600k |
| Agent Latency | <30s | <30s | <30s |

### Optimization Checklist

- [ ] Verify max 8 concurrent workers (prevent rate limits)
- [ ] Monitor queue buffer (target <4 queued tasks)
- [ ] Check token utilization (target <80%)
- [ ] Review consensus rate (target >85% auto-resolved)
- [ ] Profile agent response times (target <20s median)
- [ ] Monitor ML inference latency (<100ms each)

### Scaling Strategy

**If execution slow (<1 task/min):**
1. Check queue executor worker count (should be 8)
2. Review agent response times (log long-running agents)
3. Profile consensus voting (may need faster voters)

**If tokens exceed budget:**
1. Reduce consensus round complexity (fewer aspects)
2. Parallelize more (fan-out larger subset)
3. Cache ML inference results

---

## Example Workflows

### Example 1: Simple Rodovia (8 agents)

```yaml
project:
  id: "proj-br101"
  type: "infrastructure_linear"
  segments: ["S1"]
  description: "BR-101 Rodovia 200km pavimentação DNIT"

agents:
  - name: "agente-infraestrutura-S1"
    tier: "sonnet"

phases:
  - name: "fan_out"
    agents: ["agente-infraestrutura-S1", "manta-05", "manta-07", "manta-01", "manta-02"]
  
  - name: "consensus"
    aspects:
      - aspect: "cronograma"
        voters: ["agente-infraestrutura-S1", "manta-07"]
        threshold: 2
  
  - name: "aggregate"
    format: "docx+json"
```

**Expected:** 8 agents, 8 min execution, 300k tokens

### Example 2: Medium Porto + Energia + Saneamento (12 agents)

```yaml
project:
  id: "proj-pe-sa"
  type: "multi_segment"
  segments: ["S7", "S10", "S9"]
  description: "Porto Paranaguá + Energia + Saneamento AySA"

agents:
  - name: "agente-portos"
  - name: "agente-energia"
  - name: "agente-saneamento"
  - name: "manta-05"
  - name: "manta-07"
  - name: "manta-15"

phases:
  - name: "fan_out"
    agents: ["agente-portos", "agente-energia", "agente-saneamento", "manta-05", "manta-07", "manta-15"]
  
  - name: "consensus"
    aspects:
      - aspect: "orçamento"
        voters: ["agente-portos", "agente-energia", "agente-saneamento", "manta-05", "manta-15"]
        threshold: 3
      - aspect: "cronograma"
        voters: ["agente-portos", "agente-energia", "agente-saneamento", "manta-07"]
        threshold: 3
  
  - name: "aggregate"
    format: "docx+json"
    include_metrics: true
```

**Expected:** 12 agents, 10 min execution, 450k tokens, >85% auto-resolved

### Example 3: Complex Multimodal (16 agents)

```yaml
project:
  id: "proj-multimodal-sp"
  type: "multi_segment"
  segments: ["S1", "S2", "S3", "S4", "S9", "S10", "S11"]
  description: "Complexo multimodal: rodovia + OAE + ferrovia + metrô + barragem + energia + saneamento"

phases:
  - name: "fan_out"
    agents:
      - "agente-infraestrutura-S1"
      - "agente-infraestrutura-S2"
      - "agente-infraestrutura-S3"
      - "agente-infraestrutura-S4"
      - "agente-saneamento"
      - "agente-energia"
      - "agente-barragens"
      - "manta-05"
      - "manta-07"
      - "manta-06"
      - "manta-15"
      - "manta-01"
      - "manta-02"
      - "manta-13"
      - "manta-14"
      - "maestro"
  
  - name: "consensus"
    aspects:
      - aspect: "orçamento"
        voters: ["S1", "S2", "S9", "S10", "manta-05"]
        threshold: 3
      - aspect: "cronograma"
        voters: ["manta-07", "S1", "S2", "S3"]
        threshold: 3
      - aspect: "risco"
        voters: ["manta-01", "S9", "S10", "S11"]
        threshold: 3
  
  - name: "aggregate"
    format: "docx+json"
    include_metrics: true
```

**Expected:** 16 agents, <15 min execution, <600k tokens

---

## Support & Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Consensus escalated | <3/5 votes agree | Expand voter set or review candidates |
| Timeout (>15 min) | Slow agents or network | Profile agents, check queue depth |
| Rate limit 429 | >8 concurrent agents | Reduce concurrency (queue buffers) |
| Token budget exceeded | Too many agents | Reduce agent count or split phases |

### Debugging

**Enable metrics logging:**
```python
metrics = MetricsCollector(workflow_id, project_id, num_agents, complexity)
# ... execute workflow ...
print(metrics.format_summary())
json_metrics = metrics.to_json()
```

**Check agent logs:**
```bash
grep "agente-portos" execution.log
grep "status: failed" execution.log
```

**Validate workflow YAML:**
```python
parser = WorkflowParser()
parsed = parser.parse(yaml_string)
print(parser.validate())  # Returns errors if invalid
```

---

**Version:** 6.0.0  
**Last Updated:** 2026-07-26  
**License:** Manta Associados (Internal)
