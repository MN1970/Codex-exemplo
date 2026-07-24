# CAG Shadow Mode — Deployment & Operations Guide

## Executive Summary

**Shadow Mode** launches CAG in parallel with v4.2 RAG for 30 days (Jul 22 - Aug 21, 2026) to safely validate CAG's readiness before pilot launch.

- **User Impact**: None — all results return from v4.2 RAG
- **Risk Level**: Minimal — CAG runs non-blocking in background
- **Success Metric**: CAG accuracy ≥90%, latency within 10% of RAG
- **Decision Date**: Aug 22, 2026

---

## Pre-Deployment Checklist

- [ ] **Code Review**
  - [ ] ShadowModeOrchestrator reviewed & approved
  - [ ] ShadowModeAnalyzer reviewed & approved
  - [ ] Test coverage ≥90% (test_shadow_mode.py)

- [ ] **Infrastructure**
  - [ ] Supabase project ready (staging or production)
  - [ ] Migration 2026_07_22_v1_0_shadow_mode.sql applied
  - [ ] Tables: cag_shadow_logs, cag_shadow_daily_stats, cag_shadow_config created
  - [ ] Indices created without errors
  - [ ] Function fn_compute_shadow_daily_stats created

- [ ] **Configuration**
  - [ ] CAG_SHADOW_ENABLED=true in environment
  - [ ] Buffer size = 100 (default acceptable)
  - [ ] Debug logging disabled in production
  - [ ] Supabase connection string validated

- [ ] **Monitoring**
  - [ ] Dashboards created in Supabase UI / Metabase / Grafana
  - [ ] Alert rules configured (error spike, latency regression)
  - [ ] Daily stats SQL query tested
  - [ ] Mismatch analysis query tested

- [ ] **Runbooks**
  - [ ] Escalation contacts defined
  - [ ] Rollback procedure documented & tested
  - [ ] Support team briefed on shadow mode operation

---

## Deployment Steps

### Step 1: Apply Supabase Migration

**Timing**: Before maestro.py deployment (same deployment window)

```bash
# Stage environment
cd /path/to/Codex-exemplo
supabase db push --no-verify supabase/migrations/2026_07_22_v1_0_shadow_mode.sql

# Verify success
supabase db execute "
  SELECT COUNT(*) as table_count FROM information_schema.tables
  WHERE table_schema = 'public' AND table_name LIKE 'cag_shadow_%';
"
# Expected output: table_count = 3
```

**Expected output:**
```
Applied migration 2026_07_22_v1_0_shadow_mode.sql
Created 3 tables, 4 indices, 1 function
Verification complete: all objects created successfully
```

### Step 2: Deploy CAG Shadow Mode Code

**Timing**: Same deployment window as migration

```bash
# Build/test
pytest cag/tests/test_shadow_mode.py -v

# Expected: all tests pass
# test_shadow_run_success PASSED
# test_agent_match_detection PASSED
# test_latency_comparison PASSED
# ... (11 more tests)

# Deploy
git push -u origin claude/manta-maestro-cag-ml-8wdrg4
# (or merge PR #16 to main, then deploy)
```

### Step 3: Configure Maestro Entrypoint

**File**: `maestro.py` (or equivalent main router)

```python
# Add imports
from cag.shadow_mode import ShadowModeOrchestrator
from cag.orchestrator.cag_orchestrator import CAGOrchestrator

# Initialize (in main setup function)
def setup_shadow_mode():
    """Configure shadow mode orchestration"""
    cag_orchestrator = CAGOrchestrator(debug=False)
    shadow_orchestrator = ShadowModeOrchestrator(
        rag_handler=existing_rag_handler_v42,
        cag_orchestrator=cag_orchestrator,
        debug=os.getenv('CAG_SHADOW_DEBUG', 'false').lower() == 'true'
    )
    return shadow_orchestrator

# In query handler
@app.post("/query")
@app.post("/q")
async def handle_query(
    query: str,
    session_id: Optional[str] = None,
    context: Optional[Dict] = None
):
    """Route query through shadow mode (CAG + RAG parallel)"""
    if not session_id:
        session_id = generate_session_id()

    # Run shadow mode (CAG runs in background)
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(
        query=query,
        session_id=session_id,
        rag_context=context or {}
    )

    # Return RAG result to user (no change)
    return {
        'status': 'success',
        'query': query,
        'session_id': session_id,
        'result': rag_result,
        'timestamp': datetime.utcnow().isoformat()
    }

# Graceful shutdown
@app.on_event("shutdown")
async def shutdown():
    """Flush any remaining shadow logs on shutdown"""
    await shadow_orchestrator.flush_buffer()
```

### Step 4: Enable Shadow Mode in Config

**In Supabase:**

```sql
-- Verify config table populated
SELECT * FROM cag_shadow_config ORDER BY key;

-- Output should show:
-- enabled: 'true'
-- start_date: '2026-07-22'
-- end_date: '2026-08-21'
-- ... (9 more config rows)

-- If not present, insert defaults
INSERT INTO cag_shadow_config (key, value, description) VALUES
    ('enabled', 'true', 'Enable/disable shadow mode'),
    ('start_date', '2026-07-22', 'Shadow mode start date'),
    ('end_date', '2026-08-21', '30-day window end date'),
    ('buffer_size', '100', 'Number of results before flushing to Supabase'),
    ('agent_match_threshold', '0.85', 'Minimum agent match rate for GO decision'),
    ('latency_threshold_pct', '10.0', 'Maximum acceptable latency increase (%)'),
    ('error_threshold', '0.001', 'Maximum acceptable error rate'),
    ('comparison_mode', 'parallel', 'Run CAG and RAG in parallel'),
    ('debug_logging', 'false', 'Enable verbose debug output')
ON CONFLICT DO NOTHING;
```

### Step 5: Deploy & Smoke Test

**Timing**: Jul 22, 2026

```bash
# Deploy maestro.py changes
git push origin claude/manta-maestro-cag-ml-8wdrg4
# → CI/CD pipeline runs (cag_tests.yml)

# Post-deployment verification
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Qual é a norma para ETA?","session_id":"smoke-test-001"}'

# Expected response:
# {
#   "status": "success",
#   "query": "Qual é a norma para ETA?",
#   "session_id": "smoke-test-001",
#   "result": { RAG result },
#   "timestamp": "2026-07-22T14:30:00.123456"
# }

# Verify shadow log creation
supabase db execute "
  SELECT COUNT(*) as count FROM cag_shadow_logs WHERE created_at > NOW() - INTERVAL '5 minutes';
"
# Expected: count > 0 (indicates CAG ran in background)
```

---

## Operations (Jul 22 - Aug 21)

### Daily Tasks

**Every morning (9 AM PT):**

```sql
-- Compute previous day's stats
SELECT fn_compute_shadow_daily_stats(CURRENT_DATE - INTERVAL '1 day');

-- View results
SELECT date_bucket, total_queries, agent_match_rate, error_rate, go_ready
FROM cag_shadow_daily_stats
WHERE date_bucket = CURRENT_DATE - INTERVAL '1 day';
```

**Weekly review (every Friday 4 PM PT):**

```sql
-- Last 7 days summary
SELECT
    date_bucket,
    total_queries,
    agent_match_rate,
    latency_delta_pct_avg,
    error_rate,
    go_ready
FROM cag_shadow_daily_stats
WHERE date_bucket >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date_bucket DESC;

-- Agent mismatch patterns
SELECT
    rag_agent,
    cag_selected_agents[1] as cag_agent,
    COUNT(*) as mismatch_count,
    AVG(ABS(confidence_delta)) as avg_confidence_delta
FROM cag_shadow_logs
WHERE date_bucket = CURRENT_DATE - INTERVAL '7 days'
  AND agent_match = FALSE
GROUP BY rag_agent, cag_selected_agents[1]
ORDER BY mismatch_count DESC
LIMIT 10;
```

### Weekly Checklist

| Task | Owner | Due | Status |
|------|-------|-----|--------|
| Review daily stats | CAG Team Lead | Fri 4 PM | ☐ |
| Check error spikes | DevOps | Fri 4 PM | ☐ |
| Verify buffer flushes | Backend | Fri 5 PM | ☐ |
| Team huddle & metrics | PM | Fri 5:30 PM | ☐ |
| Update stakeholders | PM | Fri 6 PM | ☐ |

### Mid-Test Validation (Aug 4)

Manual accuracy check required:

```python
from cag.shadow_mode import ShadowModeAnalyzer

# Load 50 random shadow results
results = query_supabase("""
    SELECT * FROM cag_shadow_logs
    WHERE date_bucket >= '2026-07-22' AND date_bucket < '2026-08-04'
    ORDER BY RANDOM() LIMIT 50
""")

# Manual review: Does CAG's intent classification match the query?
# Expected accuracy: ≥90%

# Document findings:
# - Misclassifications: [list queries where CAG got it wrong]
# - Confidence distribution: [histogram of CAG confidence scores]
# - Intent coverage: [which intents did CAG encounter?]
```

### Final Analysis (Aug 18-21)

```python
from cag.shadow_mode import ShadowModeAnalyzer

# Load all 30-day results
all_results = query_supabase("""
    SELECT * FROM cag_shadow_logs
    WHERE date_bucket >= '2026-07-22' AND date_bucket <= '2026-08-21'
""")

# Analyze
analyzer = ShadowModeAnalyzer(debug=True)
report = analyzer.analyze_results(all_results, duration_days=30)

# Output:
# {
#   'total_queries': 18_734,
#   'accuracy_metrics': {'agent_match_rate': 0.882, 'avg_confidence_delta': 0.031},
#   'latency_metrics': {...},
#   'error_rate': 0.0004,
#   'go_decision': True,
#   'blockers': [],
#   'recommendations': ['Proceed to Pilot Phase (Aug 26)'],
#   'next_phase': 'PILOT'
# }

# Generate report & present to MN
```

---

## Monitoring & Alerting

### Key Metrics to Watch

| Metric | Target | Alert Threshold | Dashboard Query |
|--------|--------|-----------------|-----------------|
| Agent Match Rate | ≥ 85% | < 80% | `SELECT agent_match_rate FROM cag_shadow_daily_stats ORDER BY date_bucket DESC LIMIT 1` |
| Latency p95 | RAG × 1.10 | > RAG × 1.15 | `SELECT rag_p95_ms, cag_p95_ms FROM cag_shadow_daily_stats ORDER BY date_bucket DESC LIMIT 1` |
| Error Rate | < 0.1% | > 0.5% | `SELECT error_rate FROM cag_shadow_daily_stats ORDER BY date_bucket DESC LIMIT 1` |
| Query Volume | N/A | > 5K/day indicates usage surge | `SELECT total_queries FROM cag_shadow_daily_stats ORDER BY date_bucket DESC LIMIT 1` |
| Buffer Flush Rate | 1x per 100 queries | < 0 indicates blocked flush | Check logs: `CAG [SHADOW] Flushing...` |

### Alerting Rules (Supabase Webhooks / Custom)

```sql
-- Alert: Agent match rate drops below 80%
CREATE ALERT agent_match_drop
  ON cag_shadow_daily_stats
  WHERE agent_match_rate < 0.80
  AND date_bucket = CURRENT_DATE
  THEN send_slack("#cag-alerts", "🚨 Agent match rate dropped to {agent_match_rate}%");

-- Alert: Latency regression > 15%
CREATE ALERT latency_regression
  ON cag_shadow_daily_stats
  WHERE (cag_p95_ms / rag_p95_ms) > 1.15
  AND date_bucket = CURRENT_DATE
  THEN send_slack("#cag-alerts", "⚠️ CAG latency regressed to {cag_p95_ms}ms (RAG: {rag_p95_ms}ms)");

-- Alert: Error rate spike
CREATE ALERT error_rate_spike
  ON cag_shadow_daily_stats
  WHERE error_rate > 0.005
  AND date_bucket = CURRENT_DATE
  THEN send_slack("#cag-alerts", "🔴 Error rate spiked to {error_rate}%");
```

---

## Troubleshooting

### Symptoms & Remediation

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **Agent match rate < 85%** | Intent classifier confidence too high | Retrain classifier; adjust hybrid weights (70→60%) |
| **CAG latency > RAG × 1.20** | Slow embedding service or LLM calls | Disable semantic scoring; use keyword-only classifier |
| **Buffer flush fails** | Supabase connection issue | Check credentials; retry flush manually |
| **Missing shadow logs** | CAG not running or exception silenced | Check logs; enable debug_logging=true |
| **High error rate (>1%)** | Missing intent classes or agent pool issues | Add missing intents; validate agent pool config |

### Manual Diagnostics

```bash
# Check if shadow mode is enabled
supabase db execute "SELECT value FROM cag_shadow_config WHERE key = 'enabled';"
# Expected: true

# Check latest shadow log (verify CAG is running)
supabase db execute "
  SELECT timestamp, rag_agent, cag_selected_agents, agent_match
  FROM cag_shadow_logs
  ORDER BY timestamp DESC LIMIT 1;
"
# Expected: recent timestamp (within last 1 minute)

# Check daily stats for anomalies
supabase db execute "
  SELECT date_bucket, total_queries, error_rate, go_ready
  FROM cag_shadow_daily_stats
  ORDER BY date_bucket DESC LIMIT 7;
"

# Check maestro.py logs for CAG exceptions
tail -f /var/log/maestro.log | grep "CAG\|SHADOW\|ERROR"
```

---

## Disabling Shadow Mode (Emergency)

If critical issues require disabling:

```sql
-- Disable shadow mode immediately
UPDATE cag_shadow_config SET value = 'false' WHERE key = 'enabled';

-- In maestro.py, wrap shadow_run in try/except with graceful fallback:
try:
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(...)
except Exception as e:
    logger.warning(f"Shadow mode error: {e}. Falling back to RAG only.")
    rag_result = existing_rag_handler(query, session_id, context)

return rag_result  # Always return RAG result
```

**Post-incident:**
1. Document issue in Slack #cag-alerts
2. Enable CAG debug logging: `UPDATE cag_shadow_config SET value = 'true' WHERE key = 'debug_logging'`
3. Collect logs for analysis
4. Schedule postmortem within 24 hours

---

## Success & Transition to Pilot

**Aug 22, 2026: GO Decision**

If all criteria pass:
```
✅ Agent match rate: 88.2% (target: ≥85%)
✅ Latency p95: 2,450ms (target: ≤2,618ms = RAG 2,380 × 1.10)
✅ Error rate: 0.04% (target: <0.1%)
✅ Accuracy: 92% (manual sample, target: ≥90%)

DECISION: Proceed to PILOT PHASE (Aug 26)
```

**Pilot Phase Configuration (Aug 26):**

```python
# Switch 3 agents to CAG-only (no RAG fallback)
PILOT_AGENTS = [
    'agente-saneamento',  # Primary pilot
    'agente-energia',      # Secondary
    'agente-portos'        # Tertiary
]

# Other agents (5) remain on v4.2 RAG
```

---

## Reference Documentation

- CAG v5.0 Implementation: `cag/README.md`
- Shadow Mode Code: `cag/shadow_mode/shadow_orchestrator.py`
- Migration: `supabase/migrations/2026_07_22_v1_0_shadow_mode.sql`
- Test Suite: `cag/tests/test_shadow_mode.py`
- Supabase Evolution Roadmap: `docs/SUPABASE_EVOLUTION_ROADMAP.md`
