# Agent Memory Tiering — Quick Start Guide

**TL;DR:** Deploy R10 (memory tiering) in 3 steps: (1) run migration, (2) test scripts, (3) schedule APScheduler triggers.

---

## 1. Deploy Migration (5 min)

```bash
cd /home/user/Codex-exemplo

# Via Supabase CLI
supabase db push

# OR via psql
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql

# Verify
psql "$SUPABASE_DB_URL" -c "\dt agent_memory_*"
# Should show: agent_memory_archive, agent_memory_tier_log, agent_memory_quota
```

---

## 2. Test Scripts (Dry-Run Mode)

### A. Test Tiering

```bash
# Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-service-role-key"

# Run in dry-run mode (no changes)
python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run \
  --verbose

# Expected output:
# ✓ Promoted XX entries HOT→WARM
# ✓ Archived XX entries WARM→COLD
# ✓ Purged XX entries COLD→DELETE
# ✓ LRU evicted XX entries
```

### B. Test Cleanup

```bash
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \
  --rule-priority=3 \
  --dry-run

# Expected output:
# CLEANUP OPERATIONS:
#   Expired entries: XX deleted, X.X MB freed
#   Low-rating archived: XX deleted, X.X MB freed
#   LRU eviction: XX deleted, X.X MB freed
# 
# R9 FEEDBACK LOOP:
#   High-rating candidates: XX
```

### C. Test Monitoring

```bash
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-json=monitoring-report.json

cat monitoring-report.json | jq .

# Expected: stats for all agents, quota alerts (if any), anomalies (if any)
```

---

## 3. Schedule APScheduler Triggers

Use Claude Code's trigger system (or your own scheduler):

```python
# In Claude Code interactive mode or script
from mcp__bf7c680d-5fdc-5ef4-b4a0-abadb619bf0a__create_trigger import create_trigger

# Daily cleanup (00:00 UTC)
create_trigger(
    name="agent-memory-cleanup-daily",
    cron="0 0 * * *",
    prompt="""
Execute agent memory cleanup for all agents.

Run: python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=$AGENT_ID \
  --rule-priority=3 \
  --slack-webhook=$SLACK_WEBHOOK

Expected: Delete expired + low-rating + LRU evict if quota > 80%
Extract high-rating candidates for R9 retraining.
    """,
    notifications={"email": True}
)

# Daily tiering (02:00 UTC)
create_trigger(
    name="agent-memory-tiering-daily",
    cron="0 2 * * *",
    prompt="""
Execute full agent memory tiering cycle:
  1. HOT → WARM (30 min inactivity)
  2. WARM → COLD (480 min + rating < 2)
  3. COLD → DELETE (90 days)
  4. LRU evict if quota > 80%

Run: python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-json=tiering-results.json

Expected: Move entries between tiers, free memory, log to audit trail.
    """,
    notifications={"email": True}
)

# Hourly monitoring (every hour)
create_trigger(
    name="agent-memory-monitoring-hourly",
    cron="0 * * * *",
    prompt="""
Execute agent memory monitoring cycle.

Run: python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --slack-webhook=$SLACK_WEBHOOK \
  --output-json=monitoring-report.json

Check:
  - Quota violations (60%, 80%, 90%, 100%)
  - Anomalies (rapid growth, abnormal access, low ratings)
  - Send Slack alerts if thresholds exceeded
    """,
    notifications={"email": False}
)
```

---

## 4. Verify Deployment

```bash
# Check tables exist
psql "$SUPABASE_DB_URL" -c "
  SELECT tablename FROM pg_tables 
  WHERE tablename LIKE 'agent_memory%' 
  ORDER BY tablename;"

# Check triggers active
psql "$SUPABASE_DB_URL" -c "
  SELECT tgname, tgtable FROM pg_trigger 
  WHERE tgname LIKE 'trg_%';"

# Check sample quota
psql "$SUPABASE_DB_URL" -c "
  SELECT agent_id, current_memory_mb, max_memory_mb, 
         (current_memory_mb / max_memory_mb * 100)::NUMERIC(5,1) as quota_pct
  FROM agent_memory_quota 
  LIMIT 5;"
```

---

## Common Operations

### Manual Tiering Cycle

```bash
# Full cycle with all steps
python scripts/agent_memory_tiering.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-json=tiering-results.json

# Check results
cat tiering-results.json | jq .metrics
```

### Cleanup for Specific Agent

```bash
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s8 \
  --rule-priority=3 \
  --slack-webhook=$SLACK_WEBHOOK
```

### Check Agent Quota Status

```python
from scripts.agent_memory_monitoring import MemoryMonitoringDB

db = MemoryMonitoringDB(SUPABASE_URL, SUPABASE_KEY)
stats = db.get_memory_stats('manta-03-s1')

print(f"Agent: {stats.agent_id}")
print(f"Total: {stats.total_mb:.2f} MB ({stats.quota_pct:.1f}% quota)")
print(f"  HOT: {stats.hot_mb:.2f} MB")
print(f"  WARM: {stats.warm_mb:.2f} MB")
print(f"  COLD: {stats.cold_mb:.2f} MB")
print(f"Chunks: {stats.chunk_count}")
```

### Extract High-Rating Entries for R9

```bash
python scripts/agent_memory_cleanup.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \
  --rule-priority=0 \
  --output-json=r9-candidates.json

# R9 retraining job reads r9-candidates.json
# Updates embedding model
# Next tiering cycle uses new embeddings
```

### Monitor for Anomalies

```bash
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --slack-webhook=$SLACK_WEBHOOK \
  --output-json=full-report.json

# Check for alerts
cat full-report.json | jq '.quota_alerts[]'
cat full-report.json | jq '.anomalies[]'
```

---

## Troubleshooting Quick Fixes

### "Table agent_memory_archive does not exist"

```bash
# Rerun migration
supabase db push

# Or check for errors
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql
```

### "Function promote_hot_to_warm() does not exist"

```bash
# Stored procedure not created; rerun migration
psql "$SUPABASE_DB_URL" -c "
  \df promote_hot_to_warm"
# Should list the function
```

### "Quota alerts not triggering"

```bash
# Force quota recalculation
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-json=debug.json

cat debug.json | jq '.stats | keys'
# Check if agents are listed
```

### "No metrics in Grafana"

```bash
# Export metrics to Grafana format
python scripts/agent_memory_monitoring.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --output-grafana=grafana-metrics.json

# Send to Grafana API or datasource
cat grafana-metrics.json | jq .
```

---

## Configuration

### Change Quota Per Agent

```sql
-- Increase AySA project to 150 MB
UPDATE agent_memory_quota
SET max_memory_mb = 150.0
WHERE agent_id = 'manta-03-s8';

-- Verify
SELECT agent_id, max_memory_mb, current_memory_mb,
       (current_memory_mb / max_memory_mb * 100)::NUMERIC(5,1) as quota_pct
FROM agent_memory_quota
WHERE agent_id = 'manta-03-s8';
```

### Adjust TTLs (in migration before deployment)

```sql
-- In promote_hot_to_warm(): change INTERVAL '30 minutes'
-- In archive_warm_to_cold(): change INTERVAL '480 minutes' (8 hours)
-- In purge_cold_tier(): change retention_until logic
```

### Change LRU Threshold

In `agent_memory_cleanup.py`, line ~350:
```python
# Current: evict if quota > 80%
if quota_pct > 80.0:
    # Target: free 20%

# Change to:
if quota_pct > 90.0:  # More aggressive
    # Target: free 10%
```

---

## Environment Setup

```bash
# 1. Set Supabase credentials
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-service-role-key"  # NOT anon key!

# 2. Install Python dependencies (if needed)
pip install psycopg2-binary requests

# 3. Create .env file for credentials (optional)
cat > /home/user/Codex-exemplo/.env << EOF
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_KEY
SLACK_WEBHOOK=$SLACK_WEBHOOK
EOF

# 4. Source in scripts (if using .env)
source /home/user/Codex-exemplo/.env
```

---

## Performance Tuning

### If tiering cycle takes > 60 seconds

```bash
# 1. Check which step is slow
python scripts/agent_memory_tiering.py \
  --supabase-url=$URL --supabase-key=$KEY --verbose 2>&1 | grep -E "Step|duration"

# 2. Check index usage
psql "$SUPABASE_DB_URL" -c "
  SELECT schemaname, tablename, indexname, idx_scan
  FROM pg_stat_user_indexes
  WHERE tablename LIKE 'agent_memory%'
  ORDER BY idx_scan DESC;"

# 3. Run ANALYZE to refresh stats
psql "$SUPABASE_DB_URL" -c "
  ANALYZE agent_memory;
  ANALYZE agent_memory_archive;
  ANALYZE agent_memory_quota;"
```

### If cleanup is deleting too much

```bash
# 1. Run with lower priority
python scripts/agent_memory_cleanup.py \
  --supabase-url=$URL --supabase-key=$KEY \
  --agent-id=manta-03-s1 \
  --rule-priority=1  # Only delete expired (not low-rating)

# 2. Check what's being deleted
python scripts/agent_memory_cleanup.py \
  --supabase-url=$URL --supabase-key=$KEY \
  --agent-id=manta-03-s1 \
  --dry-run --verbose
```

---

## Dashboard Setup (Grafana)

### Create New Dashboard

1. Go to Grafana (https://grafana.manta-internal.com)
2. **Create** → **Dashboard**
3. Add panels:

```json
{
  "panels": [
    {
      "title": "Memory by Tier",
      "targets": [
        {
          "expr": "agent_memory_hot_mb + agent_memory_warm_mb + agent_memory_cold_mb"
        }
      ],
      "type": "graph"
    },
    {
      "title": "Quota % by Agent",
      "targets": [
        {
          "expr": "(agent_memory_current_mb / agent_memory_max_mb) * 100"
        }
      ],
      "type": "graph"
    },
    {
      "title": "Tiering Events",
      "targets": [
        {
          "expr": "increase(agent_memory_tier_transitions[1h])"
        }
      ],
      "type": "counter"
    }
  ]
}
```

---

## Testing Checklist

- [ ] Migration applies without errors
- [ ] Tables/indexes created successfully
- [ ] Tiering script runs (dry-run)
- [ ] Cleanup script runs (dry-run)
- [ ] Monitoring script runs
- [ ] APScheduler triggers configured
- [ ] First cleanup cycle executes (logs checked)
- [ ] First tiering cycle executes (metrics updated)
- [ ] First monitoring cycle executes (Slack alerts if any)
- [ ] Grafana dashboard displays metrics
- [ ] R9 extraction working (high-rating candidates)

---

## Support

- **Full Documentation:** `/home/user/Codex-exemplo/docs/AGENT_MEMORY_TIERING.md`
- **Troubleshooting:** See docs → Troubleshooting section
- **Slack:** #agent-ops
- **Owner:** mneves@mantaassociados.com

---

**Status: ✅ READY TO DEPLOY**  
**Last Updated: 2026-07-25**
