# Agent Memory Cache — Implementation Guide (R10)

Manta Maestro v5.0 — Agent memory cache ephemeral + persistent state with automatic purge (R10 policy).

## Overview

This package implements the agent memory cache layer for S1 (Rodovias) and all vertical agents (S1-S10).

**Key components:**
- `agent_memory` — ephemeral cache (TTL 480 min)
- `agent_state` — persistent state (embeddings, feedback aggregation)
- `agent_memory_metrics` — observability (size, chunk count, purge stats)
- `agent_memory_purge_log` — audit log (append-only)

**Policy enforcement (R10):**
- DELETE rows with `expires_at <= NOW()` (TTL-based)
- DELETE rows with `user_rating < 2 AND age > 7 days`
- Keep latest 1000 completions per agent
- Keep embedding vectors from frequent queries
- Alert if memory > 100 MB per agent or > 10 GB total freed

## Files

### DDL & Migrations

**`supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql`**
- Complete schema definition (4 tables, 7 indexes, 3 functions, 1 trigger)
- RLS policies (row-level security per agent_id)
- Stored procedures: `purge_expired_agent_memory()`, `refresh_agent_memory_metrics()`, `insert_agent_memory_dedup()`
- Status: **READY FOR PRODUCTION**
- Execute via: `supabase db push` or `psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql`

### Python Scripts

**`scripts/agent_memory_init.py`**
- Validates SQL syntax, indexes, RLS policies, functions
- Generates initialization report
- Usage:
  ```bash
  python scripts/agent_memory_init.py \
    --supabase-url=$SUPABASE_URL \
    --supabase-key=$SUPABASE_KEY \
    --dry-run  # Validate only, don't apply
  ```
- Exit codes: 0 (success), 1 (critical error), 2 (validation failed)

**`scripts/agent_memory_purge.py`**
- Executes scheduled purge (R10 policy)
- Deletes expired/low-rating entries, records metrics
- Sends Slack alerts if threshold exceeded
- Usage:
  ```bash
  python scripts/agent_memory_purge.py \
    --supabase-url=$SUPABASE_URL \
    --supabase-key=$SUPABASE_KEY \
    --agent-id=manta-03-s1 \  # Specific agent (optional)
    --dry-run \  # Simulate without deleting
    --slack-webhook=$SLACK_WEBHOOK_URL
  ```
- Exit codes: 0 (success), 1 (error), 2 (no purge needed)

### Configuration

**`scripts/agent_memory_policy.json`**
- Defines cache TTL, purge rules, memory thresholds, RLS policy
- Documents observability metrics (Grafana dashboard)
- Lists all 9 agents (S1-S10, excl. S5)
- APScheduler trigger template for daily purge (cron: `0 3 * * *`)
- Deployment notes & rollback procedure

## Architecture

### Tables

```
agent_memory (ephemeral)
  ├─ id (UUID, PK)
  ├─ agent_id (TEXT)
  ├─ session_id (TEXT)
  ├─ memory_key (TEXT)
  ├─ memory_value (JSONB)
  ├─ expires_at (TIMESTAMPTZ) ← TTL enforcement
  ├─ user_rating (SMALLINT 0-5) ← Feedback signal
  ├─ checksum (MD5) ← Dedup
  └─ created_at (TIMESTAMPTZ)
  
  Indexes:
    • (agent_id, expires_at DESC) — fast purge lookup
    • (agent_id, user_rating) — low-rating filter
    • (agent_id, checksum) — dedup check

agent_state (persistent)
  ├─ id (UUID, PK)
  ├─ agent_id (TEXT)
  ├─ embedding_vector (vector[1536]) ← Multilingual-E5-Large
  ├─ user_intent_score (FLOAT 0.0-1.0)
  ├─ feedback_count (INT)
  ├─ avg_user_rating (FLOAT 0.0-5.0)
  ├─ total_memory_size_bytes (BIGINT)
  ├─ chunk_count (INT)
  └─ last_updated (TIMESTAMPTZ)
  
  Indexes:
    • (agent_id) — lookup
    • ivfflat on embedding_vector — semantic search
    • (agent_id, last_updated DESC) — recent queries

agent_memory_metrics (observability)
  ├─ id (UUID, PK)
  ├─ agent_id (TEXT)
  ├─ metric_type (TEXT: "purge"|"size"|"chunk_count")
  ├─ metric_value (FLOAT)
  ├─ memory_size_mb (FLOAT)
  ├─ chunk_count (INT)
  ├─ deleted_count (INT)
  ├─ purge_reason (TEXT)
  └─ recorded_at (TIMESTAMPTZ)
  
  Index: (agent_id, recorded_at DESC)

agent_memory_purge_log (audit-only, append-only)
  ├─ id (UUID, PK)
  ├─ agent_id (TEXT)
  ├─ purge_timestamp (TIMESTAMPTZ)
  ├─ policy_applied (TEXT: "ttl_expired"|"rating_low")
  ├─ total_rows_deleted (INT)
  ├─ total_bytes_freed (BIGINT)
  ├─ memory_size_before_mb (FLOAT)
  ├─ memory_size_after_mb (FLOAT)
  ├─ purge_duration_ms (INT)
  ├─ executed_by (TEXT: "system" or user_id)
  └─ notes (JSONB)
  
  Index: (agent_id, purge_timestamp DESC)
```

### RLS Policy

All tables use **row-level security** with isolation by `agent_id`:

```sql
-- Example: agent_memory_isolation
CREATE POLICY agent_memory_isolation ON agent_memory
    USING (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true)
```

**Setting agent_id at connection time:**
```sql
-- On each client connection:
SET app.current_agent_id = 'manta-03-s1';
SET app.is_admin = false;
```

This ensures:
- Agent S1 (Rodovias) cannot see S8 (Saneamento) cache
- Only admin can bypass RLS for auditing
- Multi-tenant isolation by design

### Purge Policy (R10)

Runs **daily at 03:00 UTC** (APScheduler):

```python
trigger = create_trigger(
    name="agent-memory-purge-daily",
    cron="0 3 * * *",
    prompt="Execute purga de agent_memory conforme R10..."
)
```

**Rules applied (in order):**

1. **TTL Expiration** (Priority 100)
   ```sql
   DELETE FROM agent_memory
   WHERE agent_id = $agent_id
   AND expires_at <= NOW()
   ```

2. **Low Rating + Age** (Priority 90)
   ```sql
   DELETE FROM agent_memory
   WHERE agent_id = $agent_id
   AND user_rating < 2
   AND created_at < NOW() - INTERVAL '7 days'
   ```

3. **Keep Recent** (Priority 110)
   - Protect last 1000 completions per agent
   - Even if `user_rating < 2`, keep recent entries

**Thresholds:**
- Soft limit: 80 MB/agent → warn
- Hard limit: 100 MB/agent → force purge
- Chunk limit: 10,000 chunks/agent → warn

**Alerts (via Slack if enabled):**
- Total bytes freed > 10 GB
- Total rows deleted > 10,000
- Duration > 5 minutes

## Deployment

### Phase 4 — Observability (T-12h before go-live)

**Prerequisites:**
- [ ] Supabase project active
- [ ] pgvector extension installed
- [ ] APScheduler ready (Temporal/Celery backend)
- [ ] Slack webhook configured (optional)

**Steps:**

1. **Validate SQL**
   ```bash
   python scripts/agent_memory_init.py \
     --supabase-url=$SUPABASE_URL \
     --supabase-key=$SUPABASE_KEY \
     --dry-run --verbose
   ```

2. **Apply Migration**
   ```bash
   cd /path/to/repo
   supabase db push  # or: psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql
   ```

3. **Test Purge (dry-run)**
   ```bash
   python scripts/agent_memory_purge.py \
     --supabase-url=$SUPABASE_URL \
     --supabase-key=$SUPABASE_KEY \
     --dry-run --verbose
   ```

4. **Setup APScheduler Trigger**
   ```python
   # In your background job orchestrator:
   from mcp__bf7c680d-5fdc-5ef4-b4a0-abadb619bf0a__create_trigger import create_trigger
   
   trigger = create_trigger(
       name="agent-memory-purge-daily",
       cron="0 3 * * *",
       prompt="Execute purga de agent_memory conforme R10...",
       notifications={
           "push": False,
           "email": True
       }
   )
   ```

5. **Validate in Grafana**
   - Navigate to: https://grafana.manta-internal.com/d/agent-memory-cache
   - Panels: Cache Size, Chunk Count, Purge Operations, Memory Trend
   - Verify all agents reporting metrics

### Testing Checklist

- [ ] RLS isolation: User A cannot see User B's cache
- [ ] Purge execution: Test dry-run → actual run
- [ ] Metrics recording: Verify agent_memory_metrics table updated
- [ ] Slack alerts: Trigger large purge, verify notification
- [ ] Embedding refresh: Test R9 feedback loop
- [ ] Stress test: Fill cache to 100 MB, verify force purge
- [ ] Rollback: Apply ROLLBACK SQL, verify tables dropped

## Monitoring

### Grafana Dashboard

**URL:** https://grafana.manta-internal.com/d/agent-memory-cache

**Panels:**

1. **Cache Size by Agent** (bar chart)
   - Metric: `memory_size_mb` from `agent_memory_metrics`
   - Group by: `agent_id`
   - Alert: > 80 MB (warn), > 100 MB (critical)

2. **Chunk Count by Agent** (gauge)
   - Metric: `chunk_count` from `agent_memory_metrics`
   - Alert: > 5000 (warn), > 10000 (critical)

3. **Purge Operations** (time series)
   - Metric: `rows_deleted` from `agent_memory_purge_log`
   - Group by: `policy_applied`
   - Shows frequency & volume of purges

4. **Memory Trend** (line chart)
   - Metric: 24h avg of `memory_size_mb`
   - Helps identify growth patterns

### Alerting Rules

```
# Supabase Postgres Alerts

# Alert: Cache size growing
alert: AgentMemorySizeWarning
expr: agent_memory_metrics.memory_size_mb > 80
for: 30m
action: notify #agent-ops

# Alert: Purge running long
alert: PurgeDurationWarning
expr: agent_memory_purge_log.purge_duration_ms > 300000  # 5 min
for: 5m
action: notify #agent-ops

# Alert: Purge failed
alert: PurgeFailure
expr: purge_log.status == "error"
for: 1m
action: notify #agent-ops (urgent)
```

## Troubleshooting

### Purge not running

1. **Check APScheduler logs**
   ```bash
   journalctl -u apscheduler | grep agent-memory-purge-daily
   ```

2. **Verify trigger exists**
   ```bash
   python -c "from mcp__... import list_triggers; print(list_triggers(limit=10))"
   ```

3. **Test manual execution**
   ```bash
   python scripts/agent_memory_purge.py \
     --supabase-url=$SUPABASE_URL \
     --supabase-key=$SUPABASE_KEY \
     --agent-id=manta-03-s1 \
     --dry-run
   ```

### RLS blocking access

1. **Check current agent_id setting**
   ```sql
   SELECT CURRENT_SETTING('app.current_agent_id');
   ```

2. **Set agent_id before query**
   ```sql
   SET app.current_agent_id = 'manta-03-s1';
   SELECT * FROM agent_memory;  -- Should work
   ```

3. **Bypass RLS for admin query** (Supabase service_role key)
   ```sql
   SET app.is_admin = true;
   SELECT * FROM agent_memory;  -- All agents visible
   ```

### Cache size growing unbounded

1. **Check if purge ran**
   ```sql
   SELECT * FROM agent_memory_purge_log
   WHERE agent_id = 'manta-03-s1'
   ORDER BY purge_timestamp DESC
   LIMIT 5;
   ```

2. **Manual trigger**
   ```bash
   python scripts/agent_memory_purge.py \
     --supabase-url=$SUPABASE_URL \
     --supabase-key=$SUPABASE_KEY \
     --agent-id=manta-03-s1
   ```

3. **Check entries with high user_rating**
   ```sql
   SELECT COUNT(*), AVG(user_rating)
   FROM agent_memory
   WHERE agent_id = 'manta-03-s1';
   -- If avg_rating >= 4, entries are protected
   ```

### Embedding vector not updating

1. **Check agent_state**
   ```sql
   SELECT agent_id, embedding_vector IS NOT NULL as has_embedding,
          last_updated
   FROM agent_state
   WHERE agent_id = 'manta-03-s1';
   ```

2. **Manually trigger feedback loop (R9)**
   ```bash
   python -c "
   from mcp__... import fire_trigger
   fire_trigger('embedding-retraining-weekly')
   "
   ```

## References

- **CLAUDE.md v5.0** — R10 policy specification
- **DEPLOY-CHECKLIST.md** — Phase 4 (Observability)
- **Supabase Docs** — https://supabase.com/docs/guides/database
- **pgvector** — https://github.com/pgvector/pgvector

## Support

- **Slack**: #agent-ops
- **Issues**: MNT-2026-AGENT-MEMORY-CACHE
- **Owner**: mneves@mantaassociados.com
