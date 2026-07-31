# Agent Memory Tiering (R10 Refined)

## Overview

**Status:** READY FOR DEPLOYMENT  
**Date:** 2026-07-25  
**Version:** v5.0  
**Owner:** mneves@mantaassociados.com  
**Ticket:** MNT-2026-AGENT-MEMORY-TIERING

Complete implementation of R10 (Purga de Agent_Memory) from CLAUDE.md v5.0 with enhanced 3-tier cache lifecycle management, automatic cleanup policies, graceful LRU eviction, and R9 feedback loop integration.

---

## Architecture Overview

### 3-Tier Memory Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Agent Memory Tiering (R10)                       │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐
│ HOT TIER (In-Process)            │
├──────────────────────────────────┤
│ Last 100 completions             │ ← Created by agent
│ 30 min TTL                       │
│ High access frequency (> 2/hr)   │
│ Stored in: memory (process)      │
└──────────────────────────────────┘
        ↓ (30 min inactivity)
┌──────────────────────────────────┐
│ WARM TIER (Supabase)             │
├──────────────────────────────────┤
│ agent_memory table               │ ← Persisted to Supabase
│ 480 min TTL (8 hours)            │
│ Medium access (0-2/hr)           │
│ With user_rating feedback        │
└──────────────────────────────────┘
        ↓ (480 min + rating < 2)
┌──────────────────────────────────┐
│ COLD TIER (Archive)              │
├──────────────────────────────────┤
│ agent_memory_archive table       │ ← Long-term retention
│ 90 days retention (GDPR)         │
│ Audit trail & lineage            │
│ Low-rating or aged entries       │
└──────────────────────────────────┘
        ↓ (90 days)
        DELETE (GDPR compliance)
```

### Lifecycle Transitions

| From | To | Trigger | Condition | Tier Rank |
|------|----|---------|-----------|----|
| HOT | WARM | Inactivity | last_access_at > 30 min | 1 |
| WARM | COLD | TTL + Rating | expires_at + (user_rating < 2) OR age > 480 min | 2 |
| COLD | DELETE | Retention | retention_until < NOW() (90 days) | 3 |
| WARM/HOT | DELETE | LRU Eviction | quota > 80% + access_count < 2 OR user_rating < 2 | Emergency |

---

## Components

### 1. Database Schema (New Migration)

**File:** `supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql` (500+ lines)

#### New Tables

**agent_memory_archive** (Cold tier)
```sql
CREATE TABLE agent_memory_archive (
    id UUID PRIMARY KEY,
    agent_id TEXT NOT NULL,              -- Multi-tenant isolation
    memory_key TEXT NOT NULL,
    memory_value JSONB NOT NULL,
    tier VARCHAR(10) = 'COLD',
    created_at TIMESTAMPTZ NOT NULL,     -- Original creation
    last_access_at TIMESTAMPTZ NOT NULL, -- Last access before archive
    access_count INT,                    -- Total accesses
    archived_at TIMESTAMPTZ DEFAULT NOW(),
    archive_reason VARCHAR(100),         -- Why it was archived
    retention_until TIMESTAMPTZ NOT NULL, -- Delete after this
    archived_by TEXT DEFAULT 'system'
);

-- Indexes for efficient queries
CREATE INDEX idx_agent_memory_archive_expires
    ON agent_memory_archive (agent_id, retention_until ASC)
    WHERE archived_at < (NOW() - INTERVAL '90 days');

CREATE INDEX idx_agent_memory_archive_reason
    ON agent_memory_archive (agent_id, archive_reason)
    WHERE archived_at > (NOW() - INTERVAL '7 days');
```

**agent_memory_tier_log** (Audit trail - append-only)
```sql
CREATE TABLE agent_memory_tier_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    memory_id UUID NOT NULL,
    from_tier VARCHAR(10) NOT NULL,      -- 'HOT', 'WARM', 'COLD'
    to_tier VARCHAR(10) NOT NULL,        -- 'HOT', 'WARM', 'COLD', 'DELETED'
    reason VARCHAR(100) NOT NULL,        -- Transition reason
    memory_size_bytes BIGINT,
    user_rating SMALLINT,
    feedback_score FLOAT8,
    transitioned_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for audit queries
CREATE INDEX idx_agent_memory_tier_log_agent
    ON agent_memory_tier_log (agent_id, transitioned_at DESC);
```

**agent_memory_quota** (Quota tracking)
```sql
CREATE TABLE agent_memory_quota (
    agent_id TEXT PRIMARY KEY,
    max_memory_mb NUMERIC(10,2) DEFAULT 100.00,  -- Default 100 MB/agent
    current_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    hot_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    warm_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    cold_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    chunk_count INT DEFAULT 0,
    quota_exceeded_at TIMESTAMPTZ,               -- When > 80%
    last_checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert index: quota > 80%
CREATE INDEX idx_agent_memory_quota_exceeded
    ON agent_memory_quota (agent_id)
    WHERE (current_memory_mb / max_memory_mb) > 0.8;
```

#### Column Additions to agent_memory

```sql
ALTER TABLE agent_memory
    ADD COLUMN tier VARCHAR(10) DEFAULT 'WARM'
        CHECK (tier IN ('HOT', 'WARM', 'COLD')),
    ADD COLUMN last_access_at TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN access_count INT DEFAULT 0,
    ADD COLUMN feedback_score FLOAT8 DEFAULT NULL;
```

#### Stored Procedures

1. **promote_hot_to_warm()** — HOT → WARM transition after 30 min
2. **archive_warm_to_cold()** — WARM → COLD transition after 480 min + low rating
3. **purge_cold_tier()** — COLD → DELETE after 90 days (GDPR)
4. **lru_evict_quota_exceeded()** — Graceful LRU eviction when quota > 80%
5. **update_memory_metrics_on_tier_change()** — Trigger to update quotas

#### Triggers

- **trg_update_memory_metrics** — Update agent_memory_quota on tier changes
- **trg_increment_access** — Increment access_count on SELECT

---

### 2. Python Scripts

#### A. agent_memory_tiering.py (550 lines)

**Purpose:** Orchestrate 3-tier lifecycle transitions

**Classes:**
- `MemoryEntry` — Data model for cache entries
- `TieringMetrics` — Metrics for each transition
- `MemoryTieringDB` — DB operations
- `MemoryTieringOrchestrator` — Lifecycle orchestration

**Key Methods:**
```python
# Execute full tiering cycle
orchestrator.execute_tiering_cycle(agent_id=None)
  ├─ promote_hot_to_warm()      # Step 1: HOT → WARM (30 min)
  ├─ archive_warm_to_cold()     # Step 2: WARM → COLD (480 min)
  ├─ purge_cold_tier()          # Step 3: COLD → DELETE (90 days)
  └─ lru_evict_quota_exceeded() # Step 4: LRU if quota > 80%
```

**Usage:**
```bash
python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run \
  --verbose \
  --output-json=tiering-results.json
```

**Output Example:**
```json
{
  "status": "success",
  "metrics": [
    {
      "agent_id": "manta-03-s1",
      "from_tier": "HOT",
      "to_tier": "WARM",
      "moved_count": 45,
      "freed_mb": 12.3,
      "reason": "INACTIVITY"
    }
  ],
  "statistics": {
    "HOT": { "count": 10, "total_mb": 2.1 },
    "WARM": { "count": 1200, "total_mb": 45.6 },
    "COLD": { "count": 5000, "total_mb": 120.3 }
  }
}
```

#### B. agent_memory_cleanup.py (700 lines)

**Purpose:** Automatic cleanup with LRU eviction + R9 integration

**Classes:**
- `CleanupRule` — Rule definition
- `CleanupResult` — Cleanup operation result
- `R9FeedbackEntry` — High-rating entry for embedding retraining
- `MemoryCleanupDB` — DB operations
- `MemoryCleanupOrchestrator` — Cleanup orchestration

**Cleanup Rules (priority order):**
1. **Priority 1:** Delete expired entries (expires_at < NOW())
2. **Priority 2:** Archive low-rating old (user_rating < 2, age > 7 days)
3. **Priority 3:** LRU eviction if quota > 80%

**Key Methods:**
```python
# Analyze what would be cleaned
orchestrator.analyze_cleanup_rules(agent_id)
  → [CleanupRule(priority=1, ...), ...]

# Execute cleanup
orchestrator.execute_cleanup(agent_id, rule_priority=3, dry_run=False)
  → [CleanupResult(...), ...]

# Get high-rating entries for R9
orchestrator.get_high_rating_for_r9(agent_id, threshold=4.0)
  → [R9FeedbackEntry(...), ...]
```

**Usage:**
```bash
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \
  --rule-priority=3 \
  --dry-run \
  --slack-webhook=$SLACK_WEBHOOK
```

**Output Example:**
```
CLEANUP OPERATIONS:
  manta-03-s1 - Expired entries
    Deleted: 234 entries
    Freed: 15.6 MB
    Quota: 75.2% → 62.1%

  manta-03-s1 - Low-rating archived (>7d)
    Deleted: 89 entries
    Freed: 8.3 MB
    Quota: 62.1% → 54.8%

TOTALS:
  Entries deleted: 323
  Total freed: 23.9 MB

R9 FEEDBACK LOOP:
  High-rating candidates for embedding retraining: 52
```

#### C. agent_memory_monitoring.py (600 lines)

**Purpose:** Real-time quota tracking, anomaly detection, alerting

**Classes:**
- `QuotaAlert` — Quota threshold violation
- `MemoryStats` — Per-agent memory statistics
- `AnomalyDetection` — Detected anomaly
- `MonitoringReport` — Complete monitoring report
- `MemoryMonitoringDB` — DB operations
- `MemoryMonitoringOrchestrator` — Monitoring orchestration

**Key Features:**
- **Quota Thresholds:** 60% (INFO), 80% (WARNING), 90% (CRITICAL), 100% (CRITICAL)
- **Anomaly Detection:**
  - Rapid growth (> 50% in 1 hour)
  - Abnormal access patterns (> 1000 accesses/hour)
  - Low-rating saturation (> 20% entries with rating < 2)
- **Metrics Export:** Grafana-compatible JSON

**Key Methods:**
```python
# Execute monitoring cycle
report = orchestrator.execute_monitoring_cycle()

# Get statistics
stats = db.get_memory_stats(agent_id)
  → MemoryStats(total_mb=45.6, quota_pct=45.6%, ...)

# Check for quota violations
alerts = db.check_quota_alerts(agent_id)
  → [QuotaAlert(severity='WARNING', ...), ...]

# Detect anomalies
anomalies = db.detect_anomalies(agent_id, history_hours=24)
  → [AnomalyDetection(anomaly_type='RAPID_GROWTH', ...), ...]
```

**Usage:**
```bash
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --slack-webhook=$SLACK_WEBHOOK \
  --output-json=monitoring-report.json \
  --output-grafana=grafana-metrics.json
```

**Output Example:**
```
MEMORY STATISTICS:
  manta-03-s1
    Total: 45.62 MB (45.6% quota)
    HOT: 2.12 MB (4.6%)
    WARM: 35.45 MB (77.7%)
    COLD: 8.05 MB (17.6%)
    Chunks: 1245
    Access rate: 345/hour

QUOTA ALERTS:
  [WARNING] Agent manta-03-s2 quota 82.3% (threshold: 80%)

ANOMALIES DETECTED:
  [RAPID_GROWTH] manta-03-s3
    Rapid growth detected: 65% in 1 hour
    Action: Check for memory leak or unusual agent behavior
```

---

## Workflow

### Full Tiering Cycle (Recommended: Daily at 02:00 UTC)

```python
from scripts.agent_memory_tiering import MemoryTieringOrchestrator, MemoryTieringDB

db = MemoryTieringDB(supabase_url, supabase_key)
orch = MemoryTieringOrchestrator(db, dry_run=False)

result = orch.execute_tiering_cycle(agent_id=None)  # All agents
```

**Timeline:**
1. **00:00 UTC** — Cleanup (cleanup script)
2. **02:00 UTC** — Tiering cycle (this script)
   - HOT → WARM (30 min inactivity)
   - WARM → COLD (480 min + rating < 2)
   - COLD → DELETE (90 days)
   - LRU eviction (quota > 80%)
3. **03:00 UTC** — Monitoring (monitoring script)
4. **04:00 UTC** — R9 Feedback retraining (async)

### Cleanup Sequence (Daily at 00:00 UTC)

```python
from scripts.agent_memory_cleanup import MemoryCleanupOrchestrator, MemoryCleanupDB

db = MemoryCleanupDB(supabase_url, supabase_key)
orch = MemoryCleanupOrchestrator(db, dry_run=False, slack_webhook=webhook_url)

result = orch.execute_cleanup_for_agent(
    agent_id='manta-03-s1',
    rule_priority=3  # Execute rules 1-3
)
```

### Monitoring Cycle (Hourly)

```python
from scripts.agent_memory_monitoring import MemoryMonitoringOrchestrator, MemoryMonitoringDB

db = MemoryMonitoringDB(supabase_url, supabase_key)
orch = MemoryMonitoringOrchestrator(db, slack_webhook=webhook_url)

report = orch.execute_monitoring_cycle()
print(orch.get_report(report))
```

---

## Integration with R9 Feedback Loop

The tiering system integrates with R9 (Feedback Loop) for embedding model retraining:

1. **High-Rating Preservation:** Entries with user_rating >= 4 are preserved (not archived)
2. **Extraction:** `agent_memory_cleanup.py` extracts high-rating entries
3. **Retraining:** External R9 process uses these entries to fine-tune embedding model
4. **Feedback Score:** Embeddings receive feedback_score (0.0-1.0) for ranking

**Workflow:**
```
agent_memory (high rating) 
  ↓ (daily)
cleanup script extraction → [source_prompt, embedding, feedback_score]
  ↓
R9 retraining job
  ↓
embedding model version ++
  ↓
next tiering cycle uses new embeddings
```

---

## Deployment Checklist

### Phase 1: Schema Validation (T-24h)

- [ ] Review `supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql`
- [ ] Validate SQL syntax (no parse errors)
- [ ] Check table definitions vs. existing schema
- [ ] Verify index strategy (no conflicts)
- [ ] Confirm trigger logic (audit trail + metrics)

### Phase 2: Staging Deployment (T-12h)

```bash
# 1. Apply migration
supabase db push
# OR
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql

# 2. Validate schema
python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run --verbose

# 3. Test cleanup
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \
  --dry-run

# 4. Test monitoring
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-json=test-report.json
```

### Phase 3: APScheduler Setup (T-6h)

Configure triggers via Claude Code:

```python
from mcp__bf7c680d-5fdc-5ef4-b4a0-abadb619bf0a__create_trigger import create_trigger

# Daily cleanup at 00:00 UTC
create_trigger(
    name="agent-memory-cleanup-daily",
    cron="0 0 * * *",
    prompt="Execute agent memory cleanup (rule priority 3, LRU enabled)"
)

# Daily tiering at 02:00 UTC
create_trigger(
    name="agent-memory-tiering-daily",
    cron="0 2 * * *",
    prompt="Execute full tiering cycle (HOT→WARM→COLD→DELETE)"
)

# Hourly monitoring
create_trigger(
    name="agent-memory-monitoring-hourly",
    cron="0 * * * *",
    prompt="Execute memory monitoring cycle with anomaly detection"
)
```

### Phase 4: Production Rollout (T+0)

- [ ] Execute schema migration in production
- [ ] Verify all tables/indexes created
- [ ] Activate APScheduler triggers
- [ ] Monitor first tiering cycle (log verification)
- [ ] Check Slack alerts for 24h
- [ ] Validate Grafana metrics dashboard

### Phase 5: Post-Launch (T+48h)

- [ ] Review tiering metrics (entries moved, bytes freed)
- [ ] Check anomaly detections (false positives?)
- [ ] Validate quota_exceeded_at timestamps
- [ ] Spot-check archive integrity (90-day retention OK?)
- [ ] Collect user feedback (#agent-ops channel)

---

## Troubleshooting

### Issue: LRU Eviction Too Aggressive

**Symptom:** Legitimate entries deleted when quota > 80%

**Root Cause:** access_count/last_access_at not being tracked accurately

**Solution:**
```sql
-- Verify triggers are active
SELECT * FROM pg_trigger WHERE tgname LIKE 'trg_%';

-- Check access_count distribution
SELECT agent_id, MIN(access_count), MAX(access_count), AVG(access_count)
FROM agent_memory
GROUP BY agent_id;

-- Adjust LRU threshold in cleanup script:
# Change: WHERE access_count < 2
# To: WHERE access_count < 5 AND last_access_at < (NOW() - INTERVAL '1 hour')
```

### Issue: Quota Alerts Not Triggering

**Symptom:** Agent > 80% quota but no Slack alert

**Root Cause:** agent_memory_quota not being updated by triggers

**Solution:**
```sql
-- Force recalculation
SELECT refresh_agent_memory_metrics(agent_id) 
FROM (SELECT DISTINCT agent_id FROM agent_memory) t;

-- Or run monitoring cycle with verbose
python scripts/agent_memory_monitoring.py \
  --supabase-url=$URL --supabase-key=$KEY \
  --output-json=debug.json
# Check debug.json for quota calculations
```

### Issue: COLD Tier Not Purging After 90 Days

**Symptom:** agent_memory_archive keeps growing

**Root Cause:** purge_cold_tier() not being scheduled or failing silently

**Solution:**
```bash
# Manual purge (dry-run first)
python scripts/agent_memory_tiering.py \
  --supabase-url=$URL --supabase-key=$KEY \
  --dry-run

# Check purge_cold_tier() directly
psql "$SUPABASE_DB_URL" -c "SELECT purge_cold_tier('manta-03-s1');"

# Verify retention_until is set correctly
SELECT COUNT(*), MIN(retention_until), MAX(retention_until)
FROM agent_memory_archive;
```

---

## Performance Tuning

### Index Strategy

**Hot Indexes** (used every cycle):
- `idx_agent_memory_tier_hot` — HOT → WARM promotion
- `idx_agent_memory_tier_warm_archive` — WARM → COLD archival
- `idx_agent_memory_quota_exceeded` — Quota monitoring

**Warm Indexes** (used in cleanup):
- `idx_agent_memory_lru` — LRU eviction
- `idx_agent_memory_high_rating` — R9 extraction

**Analysis:**
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename LIKE 'agent_memory%'
ORDER BY idx_scan DESC;

-- Identify missing indexes
EXPLAIN ANALYZE
SELECT * FROM agent_memory
WHERE agent_id = 'manta-03-s1' AND tier = 'HOT'
ORDER BY last_access_at DESC;
```

### Query Optimization

**Tiering Cycle Duration:** Target < 60 seconds for all agents

```bash
# Measure tiering cycle
time python scripts/agent_memory_tiering.py \
  --supabase-url=$URL --supabase-key=$KEY \
  --dry-run

# If > 60s:
#   1. Disable one tier at a time to identify bottleneck
#   2. Check index effectiveness (EXPLAIN ANALYZE)
#   3. Consider batching instead of per-agent
```

---

## Quota Configuration

### Per-Agent Quota Override

Default quota is 100 MB per agent. To customize:

```sql
UPDATE agent_memory_quota
SET max_memory_mb = 150.0
WHERE agent_id = 'manta-03-s8';  -- AySA project (high-volume)
```

### Quota Scaling by Agent Tier

**Recommended:**
- **S1–S4 (existing):** 100 MB (default)
- **S6–S10 (new):** 100 MB (default)
- **Special:** S8 (AySA) → 150 MB, S9 (ANEEL) → 120 MB

---

## Metrics & Observability

### Grafana Dashboard Panels

1. **Total Memory by Tier** (stacked area chart)
   - X-axis: time
   - Y-axis: memory_mb
   - Series: hot_mb, warm_mb, cold_mb

2. **Quota % by Agent** (bar chart)
   - X-axis: agent_id
   - Y-axis: quota_pct (0-100%)
   - Color: green (< 60%), yellow (60-80%), red (> 80%)

3. **Tiering Events** (time series)
   - Counter: transitions per hour
   - Breakdown: HOT→WARM, WARM→COLD, COLD→DELETE, LRU_EVICT

4. **Anomalies Detected** (table)
   - Columns: agent_id, anomaly_type, severity, timestamp

### Key Metrics to Track

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Tiering cycle duration | < 60s | > 90s | > 120s |
| Entries moved/hour | 0-1000 | > 2000 | > 5000 |
| Bytes freed/hour | 0-500 MB | > 1 GB | > 2 GB |
| Quota exceeded agents | 0 | > 1 | > 3 |
| Anomaly detections | 0 | > 2 | > 5 |
| LRU evictions/day | 0-10 | > 20 | > 50 |

---

## References

- **CLAUDE.md:** v5.0, Section "R10 — PURGA DE AGENT_MEMORY"
- **Agent Memory Implementation:** `/home/user/Codex-exemplo/AGENT_MEMORY_IMPLEMENTATION.md`
- **Database Migrations:** `supabase/migrations/`
- **Python Scripts:** `scripts/agent_memory_*.py`

---

## Support

- **Owner:** mneves@mantaassociados.com
- **Slack:** #agent-ops (monitoring alerts)
- **Ticket:** MNT-2026-AGENT-MEMORY-TIERING
- **Emergency Runbook:** See Troubleshooting section above

---

**Status: ✅ READY FOR DEPLOYMENT**  
**Last Updated: 2026-07-25**  
**Version: v5.0**
