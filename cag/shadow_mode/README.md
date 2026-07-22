# CAG Shadow Mode — 30-Day A/B Testing Framework

## Overview

**Shadow Mode** runs CAG (v5.0) and v4.2 RAG in parallel for 30 days without affecting user-facing results. All queries return RAG results, but CAG runs silently in the background for comparison.

This enables safe, data-driven evaluation of CAG's readiness before pilot launch.

---

## Timeline

| Phase | Dates | Status |
|-------|-------|--------|
| Shadow Mode (A/B test) | Jul 22 - Aug 21, 2026 | 🔄 Active |
| Analysis & GO/NO-GO | Aug 22 - Aug 25, 2026 | ⏳ Pending |
| Pilot Launch (if GO) | Aug 26, 2026 | ⏳ Pending |

---

## Success Criteria (GO Decision)

CAG is ready for Pilot if ALL criteria are met:

| Metric | Threshold | Measurement | Status |
|--------|-----------|-------------|--------|
| **Agent Match Rate** | ≥ 85% | % queries where CAG selects same primary agent as RAG | 🔄 Monitoring |
| **Latency** | ≤ RAG × 1.10 | CAG p95 within 10% of RAG p95 | 🔄 Monitoring |
| **Error Rate** | < 0.1% | % queries with CAG errors | 🔄 Monitoring |
| **Confidence Accuracy** | ≥ 90% | Intent classification accuracy (manual sample) | 🔄 TBD @day 15 |

If any criterion fails → **NO-GO** → Tuning phase required before retry.

---

## Architecture

### Shadow Flow

```
User Query
    ↓
[Maestro Routing]
    ├─→ [RAG Handler] → Response to User ✓
    └─→ [CAG Orchestrator] (async, non-blocking)
            ├─→ Intent Classifier
            ├─→ Agent Selector
            ├─→ Response Ranker
            ├─→ Response Synthesizer
            └─→ [Supabase: cag_shadow_logs] (background)
```

### Key Properties

- **Non-blocking**: CAG errors don't affect user experience
- **Parallel**: Both systems run simultaneously
- **Logged**: Every result pair stored for analysis
- **Fire-and-forget**: CAG result flushed to Supabase asynchronously
- **No feedback loop**: Shadow mode doesn't train classifier (yet)

---

## Implementation Steps

### 1. Deploy Shadow Mode Schema to Supabase

```bash
# Apply migration
supabase db push --no-verify supabase/migrations/2026_07_22_v1_0_shadow_mode.sql

# Verify tables created
supabase db execute "SELECT tablename FROM pg_tables WHERE tablename LIKE 'cag_shadow_%';"
```

Creates:
- `cag_shadow_logs` — detailed per-query comparisons
- `cag_shadow_daily_stats` — aggregated daily metrics
- `cag_shadow_config` — feature flags

### 2. Configure Maestro Entrypoint

In `maestro.py` (or equivalent router):

```python
from cag.shadow_mode import ShadowModeOrchestrator
from cag.orchestrator.cag_orchestrator import CAGOrchestrator

# Initialize shadow orchestrator
cag_orch = CAGOrchestrator(debug=False)
shadow_orch = ShadowModeOrchestrator(
    rag_handler=existing_rag_handler,
    cag_orchestrator=cag_orch,
    debug=True  # Set to False in production
)

@app.post("/query")
async def handle_query(query: str, session_id: str):
    # Run shadow mode
    rag_result, shadow_result = await shadow_orch.shadow_run(
        query=query,
        session_id=session_id,
        rag_context={...}
    )

    # Return RAG result (no change to user)
    return rag_result
```

### 3. Enable Shadow Mode in Supabase Config

```sql
UPDATE cag_shadow_config
SET value = 'true'
WHERE key = 'enabled';
```

### 4. Start Monitoring Dashboard

Create a Supabase dashboard with these queries:

**Daily Summary:**
```sql
SELECT date_bucket, total_queries, agent_match_rate, latency_delta_pct_avg, error_rate, go_ready
FROM cag_shadow_daily_stats
ORDER BY date_bucket DESC;
```

**Last 100 Queries:**
```sql
SELECT session_id, timestamp, rag_agent, cag_selected_agents[1], agent_match, latency_delta_ms, latency_delta_pct
FROM cag_shadow_logs
ORDER BY timestamp DESC
LIMIT 100;
```

**Agent Mismatch Analysis:**
```sql
SELECT rag_agent, cag_selected_agents[1] as cag_agent, COUNT(*) as count
FROM cag_shadow_logs
WHERE agent_match = FALSE
GROUP BY rag_agent, cag_selected_agents[1]
ORDER BY count DESC
LIMIT 20;
```

---

## Daily Operations (Jul 22 - Aug 21)

### Weekly Checklist

**Every Friday:**
1. [ ] Review daily_stats for that week
2. [ ] Check for error spikes
3. [ ] Verify agent_match_rate trend
4. [ ] Document anomalies in `cag_shadow_config.notes`
5. [ ] Share metrics snapshot with team

**Mid-test (Aug 4):**
6. [ ] Manual accuracy check: sample 50 queries, verify CAG classifications
7. [ ] Check embedding cache hit rate
8. [ ] Review latency distribution (p50, p95, p99)
9. [ ] Adjust thresholds if needed

**Final week (Aug 18-21):**
10. [ ] Finalize accuracy measurements
11. [ ] Run ShadowModeAnalyzer.analyze_results()
12. [ ] Generate GO/NO-GO report
13. [ ] Present findings to MN

---

## Failure Scenarios & Mitigations

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| CAG latency > RAG×1.10 | Daily stats | Optimize classifier, disable semantic scoring |
| Agent match rate < 85% | Daily stats + anomaly review | Retrain classifier with RAG decisions |
| High error rate (>0.1%) | Daily stats | Check for missing intent classes, debug selector |
| Embedding service down | Exception handling | Fallback to keyword-only classification |

---

## Data Retention

All shadow logs are retained for 90 days post-shadow for retrospective analysis:
- Use for classifier fine-tuning
- A/B test paper / postmortem
- Historical baseline for Pilot comparison

---

## Disabling Shadow Mode

If critical issues emerge:

```sql
UPDATE cag_shadow_config
SET value = 'false'
WHERE key = 'enabled';

-- Stop CAG execution in maestro.py
```

Logs remain in Supabase for analysis.

---

## Expected Outputs (Aug 22)

**Go Report** (if all criteria ✅):
```
CAG SHADOW MODE — GO DECISION
==============================
Duration: 31 days (Jul 22 - Aug 21)
Total Queries: X,XXX
Agent Match Rate: 88.2% ✅ (threshold: ≥85%)
Latency p95: 2,450ms vs RAG 2,380ms ✅ (within 10%)
Error Rate: 0.04% ✅ (threshold: <0.1%)

RECOMMENDATION: Proceed to Pilot Phase (Aug 26)
Pilot agents: agente-saneamento, agente-energia, agente-portos
```

**NO-GO Report** (if any criterion ❌):
```
CAG SHADOW MODE — NO-GO DECISION
==================================
Blocker: Agent Match Rate 78.5% < 85% threshold
  → Likely cause: Classifier confidence too high
  → Action: Retrain with RAG decision labels

Recommendation: 2-week tuning window, retry shadow mode
Next shadow: Sep 1 - Sep 15, 2026
```

---

## Metrics Schema

### cag_shadow_logs (per query)
- `session_id`, `query`, `timestamp`
- RAG: `rag_agent`, `rag_latency_ms`, `rag_confidence`, `rag_response_text`
- CAG: `cag_selected_agents[]`, `cag_latency_ms`, `cag_avg_confidence`, `cag_final_response`
- Comparison: `agent_match`, `confidence_delta`, `latency_delta_ms`, `latency_delta_pct`

### cag_shadow_daily_stats (per day)
- Volume: `total_queries`, `queries_with_errors`, `error_rate`
- Agent Match: `agent_match_rate`
- Latency: RAG `p50/p95/p99`, CAG `p50/p95/p99`
- Deltas: `latency_delta_pct_avg`, `confidence_delta_avg`
- Decision: `go_ready` (boolean)

---

## References

- CAG Orchestrator: `cag/orchestrator/cag_orchestrator.py`
- Shadow Orchestrator: `cag/shadow_mode/shadow_orchestrator.py`
- Supabase Migration: `supabase/migrations/2026_07_22_v1_0_shadow_mode.sql`
- Phase 1.1 Monitoring: `supabase/migrations/2026_10_15_v1_1_monitoring.sql` (Phase 2, Oct)
