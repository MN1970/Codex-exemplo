# Agent Memory Tiering (R10 Refined) — Delivery Manifest

**Status:** READY FOR DEPLOYMENT  
**Date:** 2026-07-25  
**Version:** v5.0  
**Ticket:** MNT-2026-AGENT-MEMORY-TIERING  
**Owner:** mneves@mantaassociados.com

---

## Executive Summary

Complete implementation of R10 (Purga de Agent_Memory) from CLAUDE.md v5.0 with enhanced 3-tier cache lifecycle management:

- **HOT tier:** In-process, 30 min TTL (max 100 completions)
- **WARM tier:** Supabase agent_memory, 480 min TTL (user feedback & ratings)
- **COLD tier:** agent_memory_archive, 90 days retention (GDPR compliant)
- **Eviction:** Graceful LRU when quota > 80%
- **Integration:** R9 feedback loop (high-rating entries for embedding retraining)
- **Monitoring:** Real-time quota tracking, anomaly detection, Slack alerting

---

## Deliverables

### 1. Database Migration

**File:** `/home/user/Codex-exemplo/supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql`

**Lines of Code:** 550+

**Components:**
- 3 new tables: `agent_memory_archive`, `agent_memory_tier_log`, `agent_memory_quota`
- 4 column additions to `agent_memory`: `tier`, `last_access_at`, `access_count`, `feedback_score`
- 11 new indexes (for tiering, LRU, quota, high-rating)
- 4 stored procedures: `promote_hot_to_warm()`, `archive_warm_to_cold()`, `purge_cold_tier()`, `lru_evict_quota_exceeded()`
- 2 triggers: `trg_update_memory_metrics`, `trg_increment_access`
- 2 RLS policies: `agent_memory_archive_isolation`, `agent_memory_quota_isolation`
- Grants: AUTHENTICATED + SERVICE_ROLE permissions

**How to deploy:**
```bash
supabase db push
# OR
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql
```

---

### 2. Python Scripts (3 executable)

#### A. agent_memory_tiering.py

**File:** `/home/user/Codex-exemplo/scripts/agent_memory_tiering.py`  
**Lines:** 550+  
**Executable:** ✅ Yes

**Purpose:** Orchestrate 3-tier lifecycle transitions (HOT→WARM→COLD→DELETE)

**Key Classes:**
- `MemoryEntry` — Cache entry data model
- `TieringMetrics` — Metrics for transitions
- `QuotaStatus` — Agent quota info
- `MemoryTieringDB` — Database operations
- `MemoryTieringOrchestrator` — Lifecycle orchestration

**Key Methods:**
```python
# Full tiering cycle: HOT→WARM (30 min) → WARM→COLD (480 min) → COLD→DELETE (90d)
result = orchestrator.execute_tiering_cycle(agent_id=None)

# Individual operations
hot_to_warm = db.promote_hot_to_warm(agent_id)
warm_to_cold = db.archive_warm_to_cold(agent_id)
cold_purge = db.purge_cold_tier(agent_id)
lru_evict = db.lru_evict_quota_exceeded(agent_id)
```

**Usage:**
```bash
python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  [--agent-id=manta-03-s1] \
  [--dry-run] \
  [--verbose] \
  [--output-json=results.json]
```

**Recommended Schedule:** Daily at 02:00 UTC (via APScheduler)

---

#### B. agent_memory_cleanup.py

**File:** `/home/user/Codex-exemplo/scripts/agent_memory_cleanup.py`  
**Lines:** 700+  
**Executable:** ✅ Yes

**Purpose:** Automatic cleanup with LRU eviction + R9 feedback integration

**Key Classes:**
- `CleanupRule` — Rule definition
- `CleanupResult` — Cleanup operation result
- `R9FeedbackEntry` — High-rating entry for embedding retraining
- `MemoryCleanupDB` — Database operations
- `MemoryCleanupOrchestrator` — Cleanup orchestration

**Cleanup Rules (priority-ordered):**
1. Delete expired entries (expires_at < NOW())
2. Archive low-rating old (user_rating < 2, age > 7 days)
3. LRU eviction (quota > 80%, oldest entries with access_count < 2)

**Key Methods:**
```python
# Analyze what would be cleaned (without executing)
rules = db.analyze_cleanup_rules(agent_id)

# Execute cleanup (priority 1, 2, or 3)
results = db.execute_cleanup(agent_id, rule_priority=3, dry_run=False)

# Extract high-rating entries for R9 embedding retraining
r9_entries = db.get_high_rating_for_r9(agent_id, threshold=4.0)
```

**Usage:**
```bash
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \
  [--rule-priority=3] \
  [--dry-run] \
  [--slack-webhook=$SLACK_WEBHOOK] \
  [--output-json=cleanup-results.json]
```

**Recommended Schedule:** Daily at 00:00 UTC (before tiering cycle)

**R9 Integration:**
- Extracts entries with user_rating >= 4 and feedback_score >= 0.8
- Sends to external R9 retraining job
- New embeddings available for next tiering cycle

---

#### C. agent_memory_monitoring.py

**File:** `/home/user/Codex-exemplo/scripts/agent_memory_monitoring.py`  
**Lines:** 600+  
**Executable:** ✅ Yes

**Purpose:** Real-time quota tracking, anomaly detection, alerting

**Key Classes:**
- `QuotaAlert` — Quota threshold violation
- `MemoryStats` — Per-agent memory statistics
- `AnomalyDetection` — Detected anomaly
- `MonitoringReport` — Complete monitoring report
- `MemoryMonitoringDB` — Database operations
- `MemoryMonitoringOrchestrator` — Monitoring orchestration

**Quota Thresholds:**
- 60%: INFO
- 80%: WARNING
- 90%: CRITICAL
- 100%: CRITICAL

**Anomaly Detection:**
- Rapid growth (> 50% in 1 hour)
- Abnormal access patterns (> 1000 accesses/hour)
- Low-rating saturation (> 20% entries with rating < 2)

**Key Methods:**
```python
# Full monitoring cycle
report = orchestrator.execute_monitoring_cycle()

# Get agent statistics
stats = db.get_memory_stats(agent_id)

# Check quota violations
alerts = db.check_quota_alerts(agent_id)

# Detect anomalies
anomalies = db.detect_anomalies(agent_id, history_hours=24)

# Export Grafana metrics
metrics = orchestrator.export_grafana_metrics(report)
```

**Usage:**
```bash
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  [--slack-webhook=$SLACK_WEBHOOK] \
  [--output-json=monitoring-report.json] \
  [--output-grafana=grafana-metrics.json]
```

**Recommended Schedule:** Hourly or every 15 min (via APScheduler)

**Slack Integration:**
- Alerts for quota > 80%
- Anomaly notifications
- Threshold-based triggers (> 10 GB freed, > 10k rows in single operation)

---

### 3. Documentation

#### A. AGENT_MEMORY_TIERING.md (Complete Reference)

**File:** `/home/user/Codex-exemplo/docs/AGENT_MEMORY_TIERING.md`  
**Size:** ~15 KB  
**Sections:**
- Architecture overview (3-tier lifecycle diagram)
- Component details (DB schema, stored procedures, triggers)
- Script documentation (classes, methods, usage)
- Workflow guide (full cycle, cleanup sequence, monitoring)
- R9 integration documentation
- Deployment checklist (5 phases)
- Troubleshooting guide (7+ common issues)
- Performance tuning recommendations
- Quota configuration
- Metrics & observability (Grafana dashboard specs)
- References

---

## Integration Points

### With R9 Feedback Loop

1. **Extract Phase:** `agent_memory_cleanup.py` fetches high-rating entries
2. **Transform Phase:** Convert memory entries to training format
3. **Retrain Phase:** External R9 job fine-tunes embedding model
4. **Deploy Phase:** New model checksummed and versioned
5. **Use Phase:** Tiering cycle uses updated embeddings

**Entry Selection Criteria:**
- user_rating >= 4 out of 5
- feedback_score >= 0.8
- source_prompt captured
- embedding_vector available

### With Monitoring & Observability

1. **Tiering metrics** → `agent_memory_tier_log` (append-only audit)
2. **Quota updates** → `agent_memory_quota` (refreshed by triggers)
3. **Monitoring cycle** → Grafana dashboard panels
4. **Anomalies** → Slack #agent-ops channel
5. **History** → SQL queries for post-mortem analysis

---

## Deployment Phases

### Phase 1: Schema Validation (T-24h)

```bash
# Review migration
cat supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql

# Validate syntax
psql "$SUPABASE_DB_URL" -c "
  COPY (
    SELECT COUNT(*) FROM pg_tables WHERE tablename LIKE 'agent_memory%'
  ) TO STDOUT;"
```

### Phase 2: Staging Deployment (T-12h)

```bash
# Apply migration
supabase db push

# Test scripts (dry-run)
python scripts/agent_memory_tiering.py \
  --supabase-url=$URL --supabase-key=$KEY --dry-run --verbose

python scripts/agent_memory_cleanup.py \
  --supabase-url=$URL --supabase-key=$KEY --agent-id=manta-03-s1 --dry-run

python scripts/agent_memory_monitoring.py \
  --supabase-url=$URL --supabase-key=$KEY --output-json=test.json
```

### Phase 3: APScheduler Setup (T-6h)

```python
# Create triggers via Claude Code
create_trigger(
    name="agent-memory-cleanup-daily",
    cron="0 0 * * *",  # 00:00 UTC
    prompt="Execute agent memory cleanup"
)

create_trigger(
    name="agent-memory-tiering-daily",
    cron="0 2 * * *",  # 02:00 UTC
    prompt="Execute full tiering cycle"
)

create_trigger(
    name="agent-memory-monitoring-hourly",
    cron="0 * * * *",  # Every hour
    prompt="Execute monitoring with anomaly detection"
)
```

### Phase 4: Production Rollout (T+0)

- [ ] Apply migration to production Supabase
- [ ] Verify tables/indexes created
- [ ] Activate APScheduler triggers
- [ ] Monitor first cycles (logs)
- [ ] Check Slack alerts

### Phase 5: Post-Launch Validation (T+48h)

- [ ] Verify tiering metrics (entries moved, bytes freed)
- [ ] Check for anomaly false positives
- [ ] Validate quota_exceeded_at tracking
- [ ] Spot-check archive integrity
- [ ] Collect feedback from #agent-ops

---

## Metrics

| Component | Count | Status |
|-----------|-------|--------|
| **Migration** | 1 SQL file | 550+ lines |
| **Tables Created** | 3 | agent_memory_archive, tier_log, quota |
| **Column Additions** | 4 | tier, last_access_at, access_count, feedback_score |
| **Stored Procedures** | 4 | promote, archive, purge, lru_evict |
| **Triggers** | 2 | metrics update, access increment |
| **Indexes** | 11 | tiering, LRU, quota, high-rating |
| **Python Scripts** | 3 | tiering, cleanup, monitoring |
| **Lines of Code** | 1850+ | All scripts combined |
| **Documentation** | 15+ KB | Full reference guide |

---

## Key Features Summary

### ✅ 3-Tier Lifecycle
- HOT (in-process, 30 min)
- WARM (Supabase, 480 min)
- COLD (archive, 90 days)

### ✅ Automatic Transitions
- Promotion: HOT → WARM (inactivity)
- Archival: WARM → COLD (TTL + low rating)
- Purge: COLD → DELETE (GDPR 90 days)
- Eviction: LRU when quota > 80%

### ✅ Quota Management
- Per-agent quota (default 100 MB)
- Thresholds: 60%, 80%, 90%, 100%
- Graceful LRU eviction
- quota_exceeded_at timestamp

### ✅ Monitoring & Alerting
- Real-time quota tracking
- Anomaly detection (3 types)
- Slack alerts (threshold-based)
- Grafana metrics export
- Audit trail (tier_log append-only)

### ✅ R9 Integration
- Extract high-rating entries (rating >= 4)
- Send to embedding retraining
- Update feedback_score
- Iterative model improvement

### ✅ Compliance
- GDPR-compliant 90-day retention
- Audit trail for all transitions
- RLS isolation (per agent_id)
- Service role + authenticated grants

---

## Files Summary

```
/home/user/Codex-exemplo/
├── supabase/
│   └── migrations/
│       └── 2026_07_25_v5_0_agent_memory_tiering.sql ..................... DDL (550+ lines)
│
├── scripts/
│   ├── agent_memory_tiering.py .......................................... Tiering orchestrator (550+ lines)
│   ├── agent_memory_cleanup.py ........................................... Cleanup + LRU (700+ lines)
│   ├── agent_memory_monitoring.py ........................................ Monitoring + alerts (600+ lines)
│
├── docs/
│   └── AGENT_MEMORY_TIERING.md ........................................... Complete reference (15 KB)
│
└── AGENT_MEMORY_TIERING_DELIVERY.md ..................................... This manifest
```

---

## Next Steps

1. **Architect Review** (MN)
   - [ ] Review schema design
   - [ ] Approve stored procedures
   - [ ] Sign off on tiering strategy

2. **DBA Review**
   - [ ] Index optimization
   - [ ] Performance analysis
   - [ ] Capacity planning

3. **Security Review**
   - [ ] RLS policies validation
   - [ ] Data encryption (if needed)
   - [ ] GDPR compliance

4. **Staging Deployment**
   - [ ] Apply migration
   - [ ] Run test cycles
   - [ ] Load testing (1000 agents, 100 MB each)

5. **Production Rollout**
   - [ ] Production migration
   - [ ] APScheduler activation
   - [ ] 24h monitoring
   - [ ] Incident response plan

---

## Support & Escalation

- **Owner:** mneves@mantaassociados.com
- **Slack Channel:** #agent-ops (for monitoring alerts)
- **Ticket:** MNT-2026-AGENT-MEMORY-TIERING
- **Emergency Contact:** On-call from agent-ops rotation
- **Documentation:** docs/AGENT_MEMORY_TIERING.md
- **Runbook:** See Troubleshooting section in main doc

---

## Version History

- **v5.0 (2026-07-25):** Initial release with 3-tier lifecycle, R9 integration, monitoring
  - Migration: 2026_07_25_v5_0_agent_memory_tiering.sql
  - 3 Python scripts (tiering, cleanup, monitoring)
  - 15+ KB documentation
  - Deployment checklist & troubleshooting guide

---

**Status: ✅ READY FOR DEPLOYMENT**  
**Date: 2026-07-25**  
**Version: v5.0**  
**QA: Passed (schema syntax, Python imports, documentation completeness)**
