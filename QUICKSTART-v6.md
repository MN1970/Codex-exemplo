# Maestro OS v6.0 — Quick Start Guide

**Maestro OS v6.0** is a parallel multi-agent orchestration system for infrastructure projects. It combines intelligent agent routing, ML inference, and engineering analysis to deliver comprehensive project analysis in 8–15 minutes.

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/MN1970/Codex-exemplo.git
cd Codex-exemplo

# Verify installation
./maestro.sh healthcheck

# Expected output:
# ✅ CLAUDE.md v5.0.1 (20 agents)
# ✅ Phase A: Detector + Consensus
# ✅ Phase B: ML Inference + Trainer
# ✅ Phase C: Code Executor + Norm Parser
# ✅ Test Suites: Smoke + Integration
```

## Core Commands

### 1. Detect Project Complexity (Phase A)

Automatically identify project complexity and select 8–16 agents.

```bash
./maestro.sh detect "Terminal portuário Paranaguá com dragagem 3m"
```

**Output:**
```json
{
  "num_segments": 1,
  "complexity": "simple",
  "agents": ["agente-portos", "manta-05", "manta-07", ...],
  "token_budget": 300000
}
```

### 2. Run ML Inference (Phase B)

Predict routing decisions, project duration, and risk scores.

```bash
./maestro.sh infer proj-001 "Porto + Energia + Saneamento (3 segmentos)"
```

**Output:**
```json
{
  "routing_agents": 12,
  "duration_minutes": 105,
  "risk_score": 65.5
}
```

### 3. Execute Workflow (Phase C)

Run a complete workflow with all agents in parallel.

```bash
./maestro.sh execute examples/workflow-medium-porto-energia-saneamento.yaml
```

This executes:
- **Fan-out** (5 min): 12 agents analyze in parallel
- **Consensus** (1.5 min): Vote on budget, schedule, risk
- **Aggregate** (0.8 min): Consolidate outputs

**Total time:** ~10 minutes

### 4. Consensus Voting

Execute 3/5 super-majority voting on critical decisions.

```bash
./maestro.sh consensus "orçamento" agent1 agent2 agent3
```

### 5. What-If Simulation

Analyze impact of delays, budget overruns, or risk escalations.

```bash
./maestro.sh simulate DELAY --days 90 --segment S7
```

### 6. Run Tests

Validate the Maestro OS v6.0 installation.

```bash
# Smoke tests (5 representative projects)
./maestro.sh test smoke

# Integration tests (full-stack validation)
./maestro.sh test integration

# All tests
./maestro.sh test all
```

### 7. System Status

Display Maestro OS v6.0 capabilities and configuration.

```bash
# Human-readable format
./maestro.sh status

# JSON format
./maestro.sh status --format json
```

## Example Workflows

Three example workflows are provided in `examples/`:

### Simple Project (1 segment, 8 agents, ~8 min)

```bash
./maestro.sh execute examples/workflow-simple-rodovia.yaml
```

**Scenario:** BR-101 highway project
- Segment: S1 (Rodovia)
- Budget: $75M
- Agents: 8 (1 vertical + 7 horizontal)
- Token budget: 300k

### Medium Project (3 segments, 12 agents, ~10 min)

```bash
./maestro.sh execute examples/workflow-medium-porto-energia-saneamento.yaml
```

**Scenario:** Porto + Energia + Saneamento
- Segments: S7 (Porto), S10 (Energia), S9 (Saneamento)
- Budget: $1.15B
- Agents: 12 (3 vertical + 9 horizontal)
- Token budget: 450k

### Complex Project (4 segments, 16 agents, ~15 min)

```bash
./maestro.sh execute examples/workflow-complex-multimodal.yaml
```

**Scenario:** Complexo Multimodal (Rodovia + OAE + Ferrovia + Metrô)
- Segments: S1–S4 (all infrastructure types)
- Budget: $2B+
- Agents: 16 (4 vertical + 12 horizontal)
- Token budget: 600k

## Architecture Overview

### 5-Layer Orchestration

```
┌─────────────────────────────────────┐
│  Detector (Phase A)                 │
│  - Analyze project description      │
│  - Select 8–16 agents dynamically   │
├─────────────────────────────────────┤
│  Fan-Out (Parallel Execution)       │
│  - Queue executor (max 8 concurrent)│
│  - Rate limiting (exponential back) │
├─────────────────────────────────────┤
│  Consensus Engine                   │
│  - 3/5 super-majority voting        │
│  - Confidence weighting             │
├─────────────────────────────────────┤
│  Aggregator                         │
│  - Consolidate outputs              │
│  - Generate artifacts (DOCX, JSON)  │
├─────────────────────────────────────┤
│  ML Inference (Phase B)             │
│  - Routing predictions              │
│  - Duration estimates               │
│  - Risk scores                      │
└─────────────────────────────────────┘
         + Engineering Analysis (Phase C)
         - Code execution sandbox
         - Norm parser (Lei 12.334, ICOLD)
         - What-if simulator
```

### Agent Pool (20 Total)

**Vertical Agents (9):** Segment specialists
- S1: Highways | S2: Bridges/OAE | S3: Railways | S4: Metro
- S6: Buildings | S7: Ports | S8: Airports | S9: Sanitation | S10: Energy
- S11: Dams

**Horizontal Agents (11):** Cross-cutting activities
- Maestro (routing) | Claims | Contracts | Budget | Schedule
- 3D Modeling | Financial Advisory | Business Dev | Presentations
- Specialized agents (as needed)

### Performance Targets

| Complexity | Segments | Agents | Duration | Token Budget |
|-----------|----------|--------|----------|--------------|
| Simple | 1 | 8 | < 8 min | 300k |
| Medium | 2–3 | 12 | < 10 min | 450k |
| Complex | 4+ | 16 | < 15 min | 600k |

## Configuration

### Environment Variables

```bash
export MAESTRO_TOKEN_BUDGET=600000      # Max tokens per workflow
export MAESTRO_MAX_WORKERS=8            # Concurrent agent workers
export MAESTRO_QUEUE_SIZE=16            # Task queue buffer
export MAESTRO_TIMEOUT_MIN=15           # Max execution time
```

### Settings File

Edit `settings.json` to customize:
- Agent tier selection (Haiku/Sonnet/Opus)
- RAG collections (bge-small-en-v1.5, 384-d)
- Supabase connection
- Logging level

## Troubleshooting

### Issue: "Models not trained"

**Cause:** ML models (routing, duration, risk) not yet trained.

**Solution:** Phase B will skip gracefully. Train models with:
```bash
python3 src/maestro/ml_trainer.py --train-all
```

### Issue: Consensus deadlock (tied vote)

**Cause:** Even split in voting (e.g., 2/4 agents).

**Solution:** Escalate to human review. The workflow will pause and create an escalation ticket.

### Issue: Rate limit (429 Throttle)

**Cause:** Too many concurrent API calls.

**Solution:** Maestro uses exponential backoff (2s → 4s → 8s → 16s). No action needed; it will retry.

### Issue: Healthcheck timeout

**Cause:** Slow file system or Python import delays.

**Solution:** Run manual check:
```bash
ls src/maestro/detector.py src/maestro/consensus.py
```

## Workflow Development

### Create Custom Workflow

1. Copy an example workflow:
   ```bash
   cp examples/workflow-simple-rodovia.yaml my-project.yaml
   ```

2. Edit the YAML file with your project details:
   ```yaml
   project:
     id: "proj-custom"
     name: "My Project"
     segments: ["S1", "S7"]
     complexity: "medium"
   ```

3. Execute:
   ```bash
   ./maestro.sh execute my-project.yaml
   ```

### Workflow YAML Structure

```yaml
project:
  id: "unique-id"
  name: "Project name"
  segments: ["S1", "S7", ...]          # Segments involved
  complexity: "simple|medium|complex"  # Auto-detected if omitted

phases:
  - phase_name: "fan_out"              # Phase A: Parallel execution
    agents: [...]
  
  - phase_name: "consensus"            # Consensus voting
    aspects:
      - aspect: "budget"
        voters: [...]
        threshold: 3
  
  - phase_name: "aggregate"            # Phase D: Consolidation
    outputs: [...]
```

## Documentation

- **API Reference:** `docs/MAESTRO-OS-v6-API.md`
- **Developer Guide:** `docs/MAESTRO-OS-v6-DEVELOPER.md`
- **Test Suite:** `tests/test_maestro_v6_smoke.py`, `test_maestro_v6_integration.py`

## Support

For issues or questions:

1. Run healthcheck: `./maestro.sh healthcheck`
2. Check logs: `tail -f logs/agent_runs.jsonl`
3. Review documentation: `./maestro.sh --help`
4. Open an issue on GitHub

---

**Maestro OS v6.0** — Built for parallel multi-agent infrastructure analysis.  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-07-26
