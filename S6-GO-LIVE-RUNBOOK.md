# S6 Go-Live Runbook — Decision Tree & Troubleshooting
**Version: v5.0 | Agent: Manta 03-S6 (Portos) | Owner: mneves@mantaassociados.com**

Real-time decision tree for launch day (T-6h through T+24h) with diagnostic commands.

---

## LAUNCH DAY TIMELINE

```
T-6h    Pre-deployment validation (PHASE 1 of checklist)
T-5h    Sign-off gate (PHASE 2)
T-4h    Database migrations (PHASE 3)
T-3h    APScheduler setup (PHASE 4)
T-2h    Skill deployment (PHASE 5)
T-1h30m Maestro routing rules (PHASE 6)
T-1h    Tiering & fallback setup (PHASE 7)
T-30m   Pre-launch testing (PHASE 8)
T-15m   Final approval gate (PHASE 9)
T+0     GO-LIVE (PHASE 10)
T+1h    Immediate monitoring (PHASE 11)
T+6h    Short-term checks (PHASE 12)
T+24h   Daily report (PHASE 13)
```

---

## DECISION TREE (Interactive)

### BEFORE LAUNCH (T-6h to T+0)

```
START: Launch day begins (T-6h)
│
├─ Q1: All pre-deployment tests passing?
│  ├─ YES → Continue to Q2
│  └─ NO  → [ACTION 1: Fix failing tests, re-run, then continue]
│
├─ Q2: MN approval received?
│  ├─ YES (email/Slack) → Continue to Q3
│  └─ NO  → [ACTION 2: Chase MN for approval (phone call), max 30min wait]
│          └─ If no response after 30min: DELAY launch 24h, document decision
│
├─ Q3: Database migrations completed without errors?
│  ├─ YES (all tables exist, indexes created) → Continue to Q4
│  └─ NO  → [ACTION 3: Check migration logs, fix schema issues, retry migrations]
│          └─ If migration fails 2x: ROLLBACK to previous schema version
│
├─ Q4: APScheduler running and all 3 jobs registered?
│  ├─ YES (systemctl status = active) → Continue to Q5
│  └─ NO  → [ACTION 4: Check systemd logs, restart service, verify 3 jobs]
│          └─ If jobs still missing: Check scheduler_jobs.py for syntax errors
│
├─ Q5: Skill v5.0 checksum matches VERSIONS.json?
│  ├─ YES → Continue to Q6
│  └─ NO  → [ACTION 5: Recalculate checksum, update VERSIONS.json, re-validate]
│
├─ Q6: Maestro routing tests passing (>=8/10)?
│  ├─ YES → Continue to Q7
│  └─ NO  → [ACTION 6: Run routing audit, check BM25 index, validate embedding]
│          └─ If < 8/10 still failing: DELAY launch, debug keyword rules
│
├─ Q7: RAG `por:v5.0:chunks` has >= 2000 chunks with valid embeddings?
│  ├─ YES → Continue to Q8
│  └─ NO  → [ACTION 7: Check rag_chunks count, verify embeddings, re-ingest if needed]
│          └─ If < 2000 chunks: DELAY launch until ingestion complete
│
├─ Q8: Tiering formula validates on test cases (Haiku/Sonnet/Opus routes)?
│  ├─ YES → Continue to Q9
│  └─ NO  → [ACTION 8: Review complexity score formula, validate weights]
│          └─ If formula still wrong: DELAY, fix tiering logic
│
├─ Q9: Fallback cascade tested (Haiku timeout → Sonnet → Opus)?
│  ├─ YES → Continue to Q10
│  └─ NO  → [ACTION 9: Run fallback test, verify timeout triggers fallback]
│
├─ Q10: All 11 E2E tests passing?
│  ├─ YES → Continue to GO-LIVE READINESS
│  └─ NO  → [ACTION 10: Identify failing test, debug, re-run]
│           └─ If 2+ tests still failing: DELAY 24h for investigation
│
READINESS GATE: All conditions met → PROCEED TO T+0
```

### AT LAUNCH (T+0)

```
GO-LIVE WINDOW (T+0 to T+30min)
│
├─ T+0min: Merge to main, activate routing
│  └─ [ACTION: git push, set s6_enabled = true]
│
├─ T+5min: Warmup queries (3 requests)
│  ├─ All succeed → Continue monitoring
│  └─ Any fail → [ACTION 11: Check logs, diagnosis below]
│
├─ T+15min: METRICS CHECK #1
│  ├─ Q: Routing accuracy >= 75%? (spot check 10 queries)
│  │  ├─ YES → Continue
│  │  └─ NO  → [ACTION 12 in tree below]
│  │
│  ├─ Q: Error rate <= 1%?
│  │  ├─ YES → Continue
│  │  └─ NO  → [ACTION 13 in tree below]
│  │
│  ├─ Q: Latency p50 < 5s, p95 < 8s?
│  │  ├─ YES → Continue
│  │  └─ NO  → [ACTION 14 in tree below]
│
├─ T+30min: METRICS CHECK #2 (repeat)
│  └─ All metrics OK → LAUNCH CONFIRMED
```

---

## POST-LAUNCH DECISIONS (T+1h to T+24h)

```
MONITORING LOOP (every 10 min for first hour, then 30 min, then 2h)
│
├─ CHECK: Routing accuracy still >= 75%?
│  ├─ YES  → OK, continue monitoring
│  └─ NO   → 
│     ├─ First time: [ACTION 12A: Audit 20 failed queries, identify pattern]
│     ├─ Second time: [ACTION 12B: Disable reranker R6, re-test]
│     └─ Third time: TRIGGER ROLLBACK (see S6-ROLLBACK-PLAN.md)
│
├─ CHECK: Error rate < 5% and stable?
│  ├─ YES  → OK
│  └─ NO   →
│     ├─ First time: [ACTION 13A: Check error_message distribution]
│     ├─ Pattern = timeout: [ACTION 13B: Increase timeout_sec in fallback config]
│     ├─ Pattern = OOM: [ACTION 13C: Scale up container memory or reduce context window]
│     └─ Persistent > 5%: TRIGGER ROLLBACK
│
├─ CHECK: Latency p95 < 10s (allow 2x initial SLA first hour)?
│  ├─ YES  → OK
│  └─ NO   →
│     ├─ Is reranker R6 taking > 100ms? [ACTION 14A: Disable R6, use BM25 only]
│     ├─ Is Elasticsearch slow? [ACTION 14B: Check ES CPU/memory, restart if needed]
│     └─ If p95 still > 12s after 1h: TRIGGER ROLLBACK
│
├─ CHECK: No data corruption or missing chunks?
│  ├─ YES  → OK
│  └─ NO   → IMMEDIATE: [ACTION 15: Stop all writes, restore from backup, ROLLBACK]
│
├─ T+6h CHECK:
│  ├─ Cost per run reasonable (estimate vs baseline)?
│  │  ├─ YES (< 2x expected) → OK
│  │  └─ NO  → [ACTION 16: Check tiering distribution, may need re-tune]
│  │
│  ├─ Feedback score trend (any runs rated < 2)?
│  │  ├─ NO  → Great!
│  │  └─ YES → [ACTION 17: Investigate low-rated queries, identify issue]
│
└─ T+24h: Daily report (see POST-LAUNCH-MONITORING.md)
```

---

## ACTION ITEMS (Detailed Diagnostics & Fixes)

### ACTION 1: Fix Failing Tests

```bash
# Identify failing test
pytest tests/ -v | grep FAIL

# Re-run specific test with detailed output
pytest tests/routing/test_s6_portos.py::test_name -vvs

# Common fixes:
# - Routing test: validate keyword rules in maestro.v5.0.md
# - RAG test: check collection exists, has embeddings
# - Tiering test: validate formula in tiering.py matches CLAUDE.md

# After fix:
pytest tests/ -v  # Verify all pass
```

---

### ACTION 2: Chase MN for Approval

```bash
# Slack message template:
# @MN: S6 launch approval needed (T-5h window). 
# All pre-deployment tests passing. 
# Reply ✓ to approve, or reason if blocking.

# If no response after 15min:
# Phone call to MN: "Hi MN, are we good to proceed with S6 launch in 30 min?"

# Document decision in DEPLOYMENT-APPROVALS.md:
echo "[APPROVAL-DECISION] 2026-07-25T10:00:00Z — MN approved via Slack" >> .github/DEPLOYMENT-APPROVALS.md
```

---

### ACTION 3: Fix Migration Failures

```bash
# Check migration status
supabase migration list
# or check directly in Supabase UI

# If migration failed:
# Option A: Fix SQL and re-run
supabase migration up

# Option B: Manual SQL fix
psql -h $SUPABASE_HOST -U postgres << 'SQL'
-- Re-create failed table
CREATE TABLE IF NOT EXISTS agent_runs (...);
-- Check constraints
SELECT * FROM information_schema.tables WHERE table_name = 'agent_runs';
SQL

# Verify tables exist:
psql -h $SUPABASE_HOST -U postgres -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
# Expected: agent_feedback, agent_runs, agent_triggers, rag_cache, rag_chunks, rag_metadata
```

---

### ACTION 4: Fix APScheduler Issues

```bash
# Check service status
systemctl status manta-scheduler -l

# View logs
journalctl -u manta-scheduler -f

# Restart service
systemctl restart manta-scheduler
sleep 5
systemctl status manta-scheduler

# Verify jobs registered (check logs or monitoring):
# Should see: "rag_reindex_daily" "embedding_retrain_weekly" "memory_purge_daily"

# If jobs missing, check scripts/scheduler_jobs.py for syntax errors:
python3 -c "from scripts.scheduler_jobs import *; print('✓ Jobs module OK')"

# If still broken, can launch manually (not ideal for prod):
python3 -c "
from scripts.start_scheduler import scheduler
import time
time.sleep(10)  # Let it run briefly
print('Jobs:', [job.name for job in scheduler.get_jobs()])
"
```

---

### ACTION 5: Fix Checksum Mismatch

```bash
# Recalculate actual checksum
actual=$(md5sum .claude/agents/agente-portos.v5.0.md | awk '{print $1}')
echo "Actual: $actual"

# Get expected from VERSIONS.json
expected=$(jq '.agente-portos.v5.0.checksum' VERSIONS.json | tr -d '"')
echo "Expected: $expected"

# If mismatch:
# Option A: File changed, update VERSIONS.json
jq '.agente-portos.v5.0.checksum = "'$actual'"' VERSIONS.json > VERSIONS.json.tmp
mv VERSIONS.json.tmp VERSIONS.json

# Option B: File corrupted, restore from git
git checkout HEAD .claude/agents/agente-portos.v5.0.md

# Re-verify
md5sum .claude/agents/agente-portos.v5.0.md | awk '{print $1}'
jq '.agente-portos.v5.0.checksum' VERSIONS.json
# Should match
```

---

### ACTION 6: Debug Routing Accuracy Low

```bash
# Run routing audit (20 test queries)
python3 << 'EOF'
from maestro import route

test_prompts = [
    "Porto de Santos dragagem",
    "ANTAQ terminal contêineres",
    "Projeto molhe quebra-mar PIANC",
    "Calado canal de acesso",
    "Berço atracação navios",
    # ... 15 more portuário keywords
]

correct = 0
for prompt in test_prompts:
    result = route(prompt)
    is_correct = result['agent_id'] == 'manta-03-s6'
    correct += is_correct
    print(f"{'✓' if is_correct else '✗'} {prompt} → {result['agent_id']}")

accuracy = correct / len(test_prompts)
print(f"\nAccuracy: {accuracy:.0%}")

if accuracy < 0.75:
    print("\n⚠️ Accuracy low. Check:")
    print("1. BM25 index: SELECT COUNT(*) FROM rag_chunks WHERE collection LIKE 'por:v5.0%'")
    print("2. Embedding: Is embedding model loaded?")
    print("3. Keyword rules: Are S6 keywords in maestro.v5.0.md?")
    print("4. RAG collection name: Correct? (por:v5.0:*)")
EOF

# Check BM25 index
curl -s http://localhost:9200/por_v5.0/_count | jq .count

# Check embedding service
curl -s http://localhost:8000/embed \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"porto"}' | jq '.embeddings | length'
# Expected: 384 (embedding dimension)

# Validate keyword rules in maestro
grep -A 20 "# S6 — PORTOS" .claude/agents/maestro.v5.0.md
# Should list: {porto|terminal|ANTAQ|dragagem|molhe|berço|...}
```

---

### ACTION 7: Fix RAG Collection Issues

```bash
# Check chunk count
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT COUNT(*) as chunks, COUNT(DISTINCT embedding IS NULL) as with_embedding
  FROM rag_chunks WHERE collection LIKE 'por:v5.0%';
SQL
# Expected: >= 2000 chunks, all with embeddings (is_null = 0)

# If < 2000 chunks:
echo "Need to re-ingest RAG collection"

# Check if source docs available
ls -lh .claude/rag/por_v5.0/sources/ 2>/dev/null || echo "No sources, need to upload"

# Re-ingest:
python3 scripts/rag_ingest.py --collection por --version v5.0 --source-dir sources/portos/

# Verify ingestion
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT COUNT(*) FROM rag_chunks WHERE collection LIKE 'por:v5.0%' AND embedding IS NOT NULL;
SQL
# Should now be >= 2000

# If embeddings missing:
python3 scripts/compute_embeddings.py --collection por:v5.0:chunks

# Validate sample queries:
python3 << 'EOF'
from rag import query_bm25, query_embedding

q = "dragagem PIANC"
bm25 = query_bm25(q, "por:v5.0:chunks")
emb = query_embedding(q, "por:v5.0:chunks")
print(f"BM25 results: {len(bm25)}")
print(f"Embedding results: {len(emb)}")
assert len(bm25) > 0 and len(emb) > 0
EOF
```

---

### ACTION 12A: Audit Failed Routing Queries

```bash
# Get S6 runs from last 15 min
psql -h $SUPABASE_HOST -U postgres << 'SQL' > failed_queries.csv
SELECT run_id, prompt, agent_id, status, error_message
  FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '15 min'
  ORDER BY created_at DESC;
SQL

# Analyze failures
python3 << 'EOF'
import pandas as pd
failed = pd.read_csv('failed_queries.csv')
print(f"Total runs: {len(failed)}")
print(f"Routed to S6: {(failed['agent_id'] == 'manta-03-s6').sum()}")
print(f"Failed: {(failed['status'] == 'error').sum()}")

# Show failing prompts
failing = failed[failed['agent_id'] != 'manta-03-s6']
print("\nNon-S6 routed (should be S6):")
for _, row in failing.head(10).iterrows():
    print(f"  {row['prompt'][:60]}... → {row['agent_id']}")
EOF

# If pattern identified (e.g., "ANTAQ" keyword missing):
# Fix maestro.v5.0.md keyword rules, re-test
grep -i "ANTAQ\|dragagem" .claude/agents/maestro.v5.0.md | head -3
# If not present, add to S6 keyword block
```

---

### ACTION 12B: Disable Reranker (R6)

```bash
# If reranker causing issues (slow/errors), disable temporarily
cat > .claude/reranker-config.json << 'EOF'
{
  "enabled": false,
  "reason": "temporary_disable_due_to_accuracy_issue",
  "timestamp": "2026-07-25T14:30:00Z"
}
EOF

# Update maestro to skip reranker:
python3 << 'EOF'
import json
with open('.claude/settings.json') as f:
    config = json.load(f)
config['reranker_enabled'] = False
with open('.claude/settings.json', 'w') as f:
    json.dump(config, f, indent=2)
print("Reranker disabled, using BM25 + embedding only")
EOF

# Re-test routing
python3 << 'EOF'
from maestro import route
result = route("Porto dragagem ANTAQ")
print(f"Agent: {result['agent_id']}")
print(f"Confidence: {result['routing_confidence']:.2%}")
EOF
```

---

### ACTION 13B: Increase Timeout for Fallback

```bash
# If timeouts causing errors, increase threshold
cat > .claude/fallback-config.json << 'EOF'
{
  "haiku": {
    "timeout_sec": 90,
    "fallback_to": "sonnet"
  },
  "sonnet": {
    "timeout_sec": 150,
    "fallback_to": "opus"
  },
  "opus": {
    "timeout_sec": 240,
    "fallback_to": null
  }
}
EOF

# Reload config in running service
systemctl restart manta-scheduler
sleep 5

# Monitor for timeouts:
watch -n 5 "psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT status, COUNT(*) FROM agent_runs 
  WHERE created_at > NOW() - INTERVAL '5 min'
  GROUP BY status;
SQL
"
```

---

### ACTION 14A: Disable Reranker (if slow)

```bash
# Same as ACTION 12B — reranker can add 100ms latency
# Disable if latency is critical issue

# Check reranker latency:
grep "rerank" logs/maestro.log | tail -20
# Look for "rerank_time_ms" metrics

# If > 100ms consistently, disable:
echo "reranker_enabled: false" >> .claude/settings.json
systemctl restart manta-scheduler
```

---

### ACTION 15: Data Corruption Recovery

```bash
# IMMEDIATE: Stop all writes
systemctl stop manta-scheduler
# Set s6_enabled = false
python3 -c "
import json
with open('.claude/settings.json') as f:
    config = json.load(f)
config['s6_enabled'] = False
with open('.claude/settings.json', 'w') as f:
    json.dump(config, f, indent=2)
"

# Restore from backup (see ROLLBACK-PLAN.md STEP 4)
gunzip < backups/rag_v4.9_pre_s6_XXXXX.sql.gz | psql -h $SUPABASE_HOST -U postgres -d postgres

# Verify integrity
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT COUNT(*) FROM rag_chunks;
SELECT COUNT(*) FROM rag_metadata;
SELECT COUNT(*) FROM agent_runs;
SQL

# Restart
systemctl start manta-scheduler

# TRIGGER ROLLBACK (cannot fix data corruption quickly)
```

---

### ACTION 16: Cost Anomaly Investigation

```bash
# Analyze cost per run
psql -h $SUPABASE_HOST -U postgres << 'SQL' > s6_costs.csv
SELECT model_tier, COUNT(*) as runs, 
       ROUND(AVG(cost_usd), 6) as avg_cost,
       ROUND(SUM(cost_usd), 2) as total_cost
  FROM agent_runs
  WHERE agent_id = 'manta-03-s6' AND created_at > NOW() - INTERVAL '6 hours'
  GROUP BY model_tier;
SQL

python3 << 'EOF'
import pandas as pd
costs = pd.read_csv('s6_costs.csv')
print(costs)

# Check if too many Opus runs
if (costs[costs['model_tier'] == 'opus']['runs'].sum() / costs['runs'].sum()) > 0.2:
    print("⚠️ Over 20% Opus runs. Check complexity score (R7) formula")
    print("May need to reduce max_tokens or complexity weights")
EOF

# Review tiering distribution
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT model_tier, COUNT(*) as runs FROM agent_runs 
  WHERE agent_id = 'manta-03-s6'
  GROUP BY model_tier;
SQL
# Expected: majority Sonnet, some Haiku, few Opus

# If too many Opus:
# Option A: Reduce max_tokens
sed -i 's/max_tokens.*=.*2048/max_tokens = 1500/' .claude/agents/agente-portos.v5.0.md

# Option B: Adjust complexity weights
python3 << 'EOF'
# In tiering.py, reduce weights:
# keywords_matched: 1.0 → 0.8
# rag_reranker: 2.0 → 1.5
# files: 1.5 → 1.2
EOF
```

---

### ACTION 17: Low-Rated Queries Investigation

```bash
# Get low-rated runs (score < 2)
psql -h $SUPABASE_HOST -U postgres << 'SQL' > low_rated.csv
SELECT r.run_id, r.prompt, r.agent_id, f.score, f.comment
  FROM agent_runs r
  LEFT JOIN agent_feedback f ON r.run_id = f.run_id
  WHERE f.score < 2 AND r.created_at > NOW() - INTERVAL '24 hours'
  ORDER BY f.score ASC;
SQL

python3 << 'EOF'
import pandas as pd
low = pd.read_csv('low_rated.csv')
print(f"Low-rated runs: {len(low)}")
print("\nTop issues by comment:")
print(low['comment'].value_counts().head(5))

# Patterns:
# - "Results irrelevant" → RAG collection poor quality
# - "Wrong agent" → Routing rules need fix
# - "Slow response" → Latency issue, tiering/reranker
# - "Incomplete answer" → Context window too small
EOF

# Fix based on pattern:
# - If RAG poor: Re-ingest collection, validate sources
# - If routing wrong: Check keyword rules in maestro
# - If slow: Disable reranker, increase timeout
# - If incomplete: Increase max_tokens in skill
```

---

## MONITORING COMMANDS (Quick Reference)

```bash
# Health check
python3 scripts/healthcheck.py --quick

# View last 10 errors
grep ERROR logs/maestro.log | tail -10

# Routing accuracy (last 1 hour)
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT agent_id, COUNT(*) FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '1 hour'
  GROUP BY agent_id;
SQL

# Latency stats
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT 
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM agent_runs WHERE created_at > NOW() - INTERVAL '1 hour';
SQL

# Cost so far today
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT SUM(cost_usd) FROM agent_runs 
  WHERE agent_id = 'manta-03-s6'
  AND created_at > DATE_TRUNC('day', NOW());
SQL

# Systemd status
systemctl status manta-scheduler

# Recent logs
journalctl -u manta-scheduler -n 50

# Elasticsearch index size
curl -s http://localhost:9200/por_v5.0/_stats | jq '.indices.por_v5.0.primaries.store.size_in_bytes'
```

---

## ESCALATION FLOWCHART

```
Issue detected
    ↓
Is it ACTION 1–10? (Pre-launch)
    ├─ YES → Execute action, re-test
    │        If still broken after 2 attempts → DELAY launch 24h
    └─ NO  → Continue
    ↓
Is it ACTION 11–17? (Post-launch)
    ├─ First occurrence → Execute action, monitor for 15min
    │                      If issue resolved → Continue monitoring
    │                      If issue persists → Execute next escalation
    └─ Second occurrence of SAME issue → CONSIDER ROLLBACK
    ↓
Any 🔴 CRITICAL condition?
    ├─ YES → Immediate ROLLBACK (see S6-ROLLBACK-PLAN.md)
    │        Phone MN: "Initiating rollback due to [REASON]"
    └─ NO  → Continue monitoring, escalate to tech lead if unsure
```

---

## SIGN-OFF

**Prepared by:** Claude AI (Codex-exemplo Agent)  
**Date:** 2026-07-25  
**Reviewed by:** _____________________ (Tech Lead)  
**Distribution:** #agent-ops Slack, on-call team

**In case of emergency:** Call MN immediately (contact in ROLLBACK-PLAN.md)

---

**End of S6 Go-Live Runbook**
