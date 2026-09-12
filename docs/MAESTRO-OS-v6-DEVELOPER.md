# Maestro OS v6.0 — Developer Guide

**Version:** 6.0.0  
**Audience:** Engineers extending Maestro with new components  
**Last Updated:** 2026-07-26  

---

## Table of Contents

1. [Adding a New Agent](#adding-a-new-agent)
2. [Creating Custom Workflows](#creating-custom-workflows)
3. [Extending Consensus Logic](#extending-consensus-logic)
4. [Adding New ML Models](#adding-new-ml-models)
5. [Implementing Custom Norm Parser Rules](#implementing-custom-norm-parser-rules)
6. [Debugging Multi-Agent Execution](#debugging-multi-agent-execution)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## Adding a New Agent

### Prerequisites

- Agent name follows Manta convention: `agente-{segment-code}` or `manta-{number}`
- Agent tier: "sonnet" (default), "opus", or "haiku"
- Integration with 8-phase lifecycle: estudo_previo → descomissionamento

### Step 1: Register Agent in Detector

Edit `src/maestro/detector.py`:

```python
# In DetectionResult.agents_pool:
KNOWN_AGENTS = {
    "agente-novo": {
        "name": "agente-novo",
        "tier": "sonnet",
        "segment": "S12",  # New segment
        "role": "vertical",  # vertical or horizontal
        "applicable_types": ["infrastructure_linear", "multi_segment"],
    },
    # ... existing agents ...
}

# In ComplexityDetector._select_agents():
if "novo-keyword" in description.lower():
    agents.append({"name": "agente-novo", "tier": "sonnet"})
```

### Step 2: Create Agent Skill (if using Claude)

Create `.claude/agents/agente-novo.md`:

```markdown
# agente-novo — Segment S12 Specialist

**Responsibilities:**
- Analysis of new segment type
- Integration with existing phases
- Cross-segment dependencies

**Tool Access:**
- Read, Grep, Glob, Bash, WebSearch, WebFetch

**Models:**
- Sonnet (default), Opus for complex analysis

**Trigger Patterns:**
- IF menção a novo-keyword | new-keyword
  → agente-novo [PRIORITY]
```

### Step 3: Update Agent Pool in Supabase

```sql
INSERT INTO agent_pool (name, segment, tier, status, created_at)
VALUES ('agente-novo', 'S12', 'sonnet', 'active', now());
```

### Step 4: Test Integration

```python
from src.maestro.detector import ComplexityDetector

detector = ComplexityDetector()
result = detector.detect_from_description("novo-keyword project")

assert "agente-novo" in [a["name"] for a in result.agents_selected]
assert result.num_segments >= 1
```

---

## Creating Custom Workflows

### Workflow YAML Structure

Create `workflows/custom-project.yaml`:

```yaml
project:
  id: "proj-custom-001"
  type: "infrastructure_linear|multi_segment"
  segments: ["S1", "S2"]
  description: "Project description for detector"
  priority: "high"  # high, medium, low

agents:
  - name: "agente-infraestrutura-S1"
    tier: "sonnet"
    role: "primary"
  - name: "manta-05"
    tier: "sonnet"
    role: "support"

phases:
  - name: "fan_out"
    timeout_secs: 600
    agents: ["agente-infraestrutura-S1", "manta-05"]
    parallel: true
    
    # Parallel execution with shared context
    context:
      base_cost: 500_000_000
      base_duration_days: 365
      budget_risk_level: "high"

  - name: "consensus"
    # Voting on critical decisions
    aspects:
      - aspect: "cronograma"
        description: "Project timeline validation"
        voters: ["agente-infraestrutura-S1", "manta-07"]
        num_candidates: 3
        threshold: 2  # Majority of voters
        confidence_min: 0.75

      - aspect: "orçamento"
        voters: ["agente-infraestrutura-S1", "manta-05"]
        threshold: 2
        escalation_policy: "human_review"

  - name: "aggregate"
    timeout_secs: 120
    output_format: "docx+json"
    include_metrics: true
    include_audit_trail: true
    compression: "gzip"
```

### Validation & Testing

```python
from src.maestro.parser import WorkflowParser

parser = WorkflowParser()

# Parse and validate
try:
    workflow = parser.parse(open("workflows/custom.yaml").read())
    print(f"✓ Valid workflow: {workflow.project.id}")
except WorkflowValidationError as e:
    print(f"✗ Validation failed: {e}")

# Test with detector
from src.maestro.orchestrator import MaestroOrchestrator

orchestrator = MaestroOrchestrator()
execution = orchestrator.execute_workflow(
    project_id="proj-test-001",
    description="Test project description",
    workflow_yaml=open("workflows/custom.yaml").read()
)

# Verify results
assert execution.consensus_results is not None
assert execution.aggregated_output is not None
```

---

## Extending Consensus Logic

### Custom Voting Strategy

Extend `src/maestro/consensus.py`:

```python
from src.maestro.consensus import ConsensusEngine, ConsensusResult, ConsensusStatus

class CustomConsensusEngine(ConsensusEngine):
    """Custom voting logic for specific domains."""

    def execute_vote(self, votes, threshold=3, aspect="decision"):
        """Override with custom logic."""
        
        # Example: confidence-weighted voting
        total_confidence = sum(v.confidence for v in votes)
        avg_confidence = total_confidence / len(votes) if votes else 0
        
        # Require higher consensus if low confidence
        if avg_confidence < 0.70:
            adjusted_threshold = int(threshold * 1.5)  # Require more votes
        else:
            adjusted_threshold = threshold
        
        # Count votes per candidate
        candidate_votes = {}
        for vote in votes:
            candidate_id = vote.candidate.value
            if candidate_id not in candidate_votes:
                candidate_votes[candidate_id] = []
            candidate_votes[candidate_id].append(vote)
        
        # Find winner
        for candidate_id, candidate_votes_list in candidate_votes.items():
            if len(candidate_votes_list) >= adjusted_threshold:
                return ConsensusResult(
                    status=ConsensusStatus.DECIDED,
                    winner=candidate_votes_list[0].candidate,
                    reason=f"Consensus {len(candidate_votes_list)}/{len(votes)} with avg confidence {avg_confidence:.2f}"
                )
        
        # No consensus reached
        return ConsensusResult(
            status=ConsensusStatus.ESCALATED,
            reason=f"Could not reach {adjusted_threshold}/{len(votes)} threshold"
        )

# Test custom engine
engine = CustomConsensusEngine()
result = engine.execute_vote(votes, threshold=3, aspect="test")
print(result.status)
```

### Dynamic Threshold Adjustment

```python
class DynamicConsensusEngine(ConsensusEngine):
    """Consensus that adjusts threshold based on complexity."""

    def __init__(self, project_complexity="medium"):
        super().__init__()
        self.project_complexity = project_complexity

    def _calculate_threshold(self, num_voters):
        """Adjust threshold by complexity."""
        if self.project_complexity == "simple":
            return max(2, int(num_voters * 0.5))  # 50%
        elif self.project_complexity == "medium":
            return max(3, int(num_voters * 0.6))  # 60%
        else:  # complex
            return max(4, int(num_voters * 0.75))  # 75%
```

---

## Adding New ML Models

### Add Routing Model Variant

Extend `src/maestro/ml_trainer.py`:

```python
from src.maestro.ml_trainer import MLModel

class CustomRoutingModel(MLModel):
    """Custom routing model using ensemble approach."""

    def __init__(self):
        self.model_type = "ensemble"
        self.base_models = []
        self._load_models()

    def _load_models(self):
        """Load multiple base models."""
        # Example: combine XGBoost + Neural Net
        import xgboost as xgb
        self.xgb_model = xgb.XGBClassifier()
        self.nn_model = self._build_neural_net()

    def _build_neural_net(self):
        """Build neural network for ensemble."""
        # Implement NN architecture
        pass

    def predict(self, features):
        """Ensemble prediction."""
        xgb_pred = self.xgb_model.predict_proba(features)
        nn_pred = self.nn_model.predict(features)
        
        # Average predictions (60% XGBoost, 40% NN)
        ensemble_pred = 0.6 * xgb_pred + 0.4 * nn_pred
        return ensemble_pred

# Use in inference service
from src.maestro.ml_inference import InferenceService

service = InferenceService(
    routing_model=CustomRoutingModel(),
    duration_model=DurationPredictor(),
    risk_model=RiskClassifier()
)

result = service.infer("proj-id", "description")
```

### Model Training & Validation

```python
import json
from src.maestro.ml_trainer import MLTrainer, TrainingConfig

config = TrainingConfig(
    train_test_split=0.8,
    epochs=50,
    batch_size=32,
    learning_rate=0.001,
    early_stopping=True
)

trainer = MLTrainer(config)

# Collect traces (historical data)
traces = [
    {
        "project_id": "proj-001",
        "features": [...],
        "duration_minutes": 580,
        "agents_used": ["agente-portos", "agente-energia"],
        "outcome": "success"
    },
    # ... more traces ...
]

# Train models
metrics = trainer.train_all(traces)

# Validate
print(f"Routing accuracy: {metrics['routing_accuracy']:.2%}")
print(f"Duration RMSE: {metrics['duration_rmse']:.0f} min")
print(f"Risk AUC: {metrics['risk_auc']:.3f}")

# Save models
trainer.save_models("models/checkpoint_v6.0.1")
```

---

## Implementing Custom Norm Parser Rules

### Add Lei/Standard Rules

Extend `src/maestro/norm_parser.py`:

```python
from src.maestro.norm_parser import NormativeRule, ConstraintCategory

class CustomNormParser:
    """Custom parser for domain-specific norms."""

    def parse_custom_standard(self):
        """Extract custom normative rules."""
        rules = [
            NormativeRule(
                rule_id="custom-001",
                source="Norma Técnica MANTA v2.0",
                category=ConstraintCategory.STRUCTURAL,
                description="Custom structural requirement",
                requirement="Requirement description",
                verification_method="How to verify compliance",
                applies_to=["infrastructure_linear", "multi_segment"],
                penalty_if_violated="Consequence of violation",
                is_mandatory=True
            ),
            # ... more rules ...
        ]
        return rules

# Use in compliance checking
from src.maestro.norm_parser import ComplianceChecker

checker = ComplianceChecker()
custom_parser = CustomNormParser()

# Add custom rules to checker
custom_rules = custom_parser.parse_custom_standard()
checker.all_rules.extend(custom_rules)

# Run compliance check
compliant, warnings, violations = checker.check_compliance(
    project_type="infrastructure_linear",
    project_features={"custom_feature": True}
)
```

### Regex-Based Rule Extraction

```python
import re

class RegexNormParser:
    """Extract rules using regex patterns."""

    PATTERNS = {
        "safety_requirement": r"Requirement:\s*(.+?)(?:\n|$)",
        "verification_method": r"Verify:\s*(.+?)(?:\n|$)",
        "penalty": r"Penalty:\s*(.+?)(?:\n|$)",
    }

    def parse_document(self, text):
        """Parse normative document using regex."""
        rules = []
        
        for rule_id, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                rules.append({
                    "pattern": rule_id,
                    "content": match.group(1)
                })
        
        return rules
```

---

## Debugging Multi-Agent Execution

### Enable Detailed Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maestro_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Execute with logging
from src.maestro.orchestrator import MaestroOrchestrator

orchestrator = MaestroOrchestrator()
logger.info(f"Starting workflow: proj-001")

execution = orchestrator.execute_workflow(
    project_id="proj-001",
    description="Debug project",
    workflow_yaml=yaml_string
)

logger.info(f"Workflow completed: {execution.status}")
```

### Agent Response Tracing

```python
from src.maestro.metrics import MetricsCollector

# Collect metrics with tracing
metrics = MetricsCollector("wf-debug", "proj-001", num_agents=8, complexity_level="simple")

# Log each agent
for agent_metric in metrics.execution_metrics.agent_metrics:
    print(f"{agent_metric.agent_name}:")
    print(f"  Duration: {agent_metric.duration_secs:.1f}s")
    print(f"  Tokens: {agent_metric.tokens_used:,}")
    print(f"  Status: {agent_metric.status}")
    if agent_metric.error:
        print(f"  Error: {agent_metric.error}")
```

### Consensus Voting Debug

```python
from src.maestro.consensus import ConsensusEngine

engine = ConsensusEngine()

# Trace voting process
votes_by_candidate = {}
for vote in votes:
    candidate_id = vote.candidate.value
    if candidate_id not in votes_by_candidate:
        votes_by_candidate[candidate_id] = []
    votes_by_candidate[candidate_id].append(vote)
    
    print(f"Vote: {vote.voter} → {candidate_id} (confidence: {vote.confidence:.2f})")

print(f"\nCandidate tally:")
for candidate_id, candidate_votes in votes_by_candidate.items():
    print(f"  {candidate_id}: {len(candidate_votes)} votes")

result = engine.execute_vote(votes, threshold=3, aspect="test")
print(f"\nResult: {result.status.value}")
```

---

## Troubleshooting Guide

### Issue 1: Consensus Escalates Frequently

**Symptom:** >15% of decisions escalated (target <15%)

**Causes:**
- Voters have divergent opinions
- Threshold too high for number of voters
- Candidate proposals too different

**Solutions:**
```python
# Option 1: Lower threshold
result = engine.execute_vote(votes, threshold=2)  # Majority instead of 3/5

# Option 2: Expand voter set
voters = ["S1", "S2", "S3", "S4", "S5"]  # More voters increases chance

# Option 3: Pre-cluster similar candidates
candidates_clustered = cluster_similar_candidates(candidates)
result = engine.execute_vote(votes, threshold=3)
```

### Issue 2: Execution Exceeds Token Budget

**Symptom:** `token_utilization > 100%`

**Causes:**
- Too many agents (8-16)
- Long-running agents (verbose outputs)
- Repeated API calls

**Solutions:**
```python
# Option 1: Reduce agent count
detection = detector.detect_from_description(description)
detection.agents_selected = detection.agents_selected[:8]  # Reduce to 8

# Option 2: Optimize ML models for token efficiency
ml_service.clear_cache()  # Avoid redundant inferences

# Option 3: Summarize agent outputs
result.output = summarize(result.output, max_tokens=1000)
```

### Issue 3: Agent Timeout (>30s response)

**Symptom:** Some agents fail with `TimeoutError`

**Causes:**
- Agent overloaded
- Network latency
- Large output size

**Solutions:**
```python
# Option 1: Increase timeout
executor = QueueExecutor(max_workers=8, max_queue=16)
executor.timeout_secs = 45  # Increase from 30s

# Option 2: Parallelize agent work
# Split large analysis into multiple agents

# Option 3: Use fallback/cache
from src.maestro.ml_inference import InferenceService
service = InferenceService(..., cache_size=5000)  # Larger cache
```

### Issue 4: Queue Depth Exceeds Capacity (>16)

**Symptom:** Tasks rejected with `QueueFullError`

**Causes:**
- Queue buffer too small
- Worker pool too small (max 8)
- High arrival rate

**Solutions:**
```python
# Option 1: Increase queue size (limited by API concurrency)
executor = QueueExecutor(max_workers=8, max_queue=32)  # But max 8 concurrent

# Option 2: Reduce submission rate (pace task submission)
for task in tasks:
    executor.enqueue_task(task)
    time.sleep(0.1)  # Rate limit submissions

# Option 3: Use batch processing (group tasks)
executor.execute_batch(tasks, batch_size=4)
```

### Issue 5: ML Model Low Accuracy

**Symptom:** `routing_accuracy < 70%` or `risk_auc < 0.75`

**Causes:**
- Insufficient training data
- Imbalanced classes
- Poor features

**Solutions:**
```python
# Option 1: Collect more training data
# Expand historical project database

# Option 2: Improve features
from src.maestro.ml_features import FeatureEngineer
engineer = FeatureEngineer()
features = engineer.infer_characteristics_v2(description)  # Enhanced

# Option 3: Ensemble approach
custom_model = CustomRoutingModel()  # Combine multiple models

# Option 4: Retrain with better hyperparameters
trainer = MLTrainer(TrainingConfig(
    learning_rate=0.0001,
    epochs=100,
    early_stopping=True,
    regularization=0.01
))
```

---

## Best Practices

### Do's ✓
- ✓ Use dataclasses for structured data
- ✓ Log all state transitions
- ✓ Validate YAML workflows before execution
- ✓ Test with sample projects before production
- ✓ Monitor token utilization continuously
- ✓ Cache ML inferences when possible
- ✓ Rotate agents in consensus voting

### Don'ts ✗
- ✗ Don't modify agent pool during execution
- ✗ Don't exceed 16 agents (architectural limit)
- ✗ Don't skip consensus validation (always verify 3/5)
- ✗ Don't log sensitive PII (R1 compliance)
- ✗ Don't hardcode thresholds (make configurable)
- ✗ Don't retry indefinitely (max 3 attempts)
- ✗ Don't execute synchronously (use async/queue)

---

## Support

**Issues?** Check:
1. This guide (troubleshooting section)
2. API docs (`MAESTRO-OS-v6-API.md`)
3. Code comments in `src/maestro/*.py`
4. Execution logs in `maestro_debug.log`

**Contributing?** Follow:
- PEP 8 style guide
- Type hints on all functions
- Docstrings on public methods
- Test coverage >80%
- Commit messages with references

---

**Version:** 6.0.0  
**Last Updated:** 2026-07-26  
**Maintained by:** Manta IA Team
