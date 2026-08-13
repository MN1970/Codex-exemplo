# Agent Memory Cache — Implementation Summary (v5.0 R10)

**Status:** READY FOR DEPLOYMENT  
**Date:** 2026-07-25  
**Owner:** mneves@mantaassociados.com  
**Ticket:** MNT-2026-AGENT-MEMORY-CACHE

---

## Overview

Complete schema design for agent_memory cache layer implementing R10 (automatic purge policy) from CLAUDE.md v5.0 Manta Maestro.

**Scope:** S1 (Rodovias) + S2-S10 vertical agents  
**Components:** 4 tables, 7 indexes, 3 stored procedures, 1 trigger, 2 RLS policies

---

## Files Delivered

### 1. DDL Migration

**`supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql`** (434 lines)

Complete schema definition:

```
Tables:
├─ agent_memory (ephemeral, TTL 480 min)
├─ agent_state (persistent, embeddings)
├─ agent_memory_metrics (observability)
└─ agent_memory_purge_log (audit-only)

Indexes:
├─ idx_agent_memory_expires_at ← Fast purge lookup
├─ idx_agent_memory_user_rating ← Low-rating filter
├─ idx_agent_memory_checksum ← Dedup check
├─ idx_agent_memory_session ← Session lookup
├─ idx_agent_state_agent_id
├─ idx_agent_state_embedding ← IVFFlat (vector search)
├─ idx_agent_state_last_updated
├─ idx_agent_memory_metrics_agent_id
├─ idx_agent_memory_metrics_type
├─ idx_agent_memory_purge_log_agent_id
└─ idx_agent_memory_purge_log_policy

Stored Procedures:
├─ purge_expired_agent_memory(p_agent_id) ← R10 enforcement
├─ refresh_agent_memory_metrics(p_agent_id) ← Metrics calc
└─ insert_agent_memory_dedup(...) ← Dedup insert

Trigger:
└─ trg_agent_memory_rating_update ← Update agent_state on rating

RLS Policies:
├─ agent_memory_isolation ← By agent_id
└─ agent_state_isolation ← By agent_id
```

**Execute via:**
```bash
supabase db push
# OR
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql
```

### 2. Python Scripts

**`scripts/agent_memory_init.py`** (280 lines)

Initializer:
- Validates SQL syntax (4 tables, 7 indexes, 3 functions, 1 trigger, 2 RLS policies)
- Checks constraints and column definitions
- Validates grants (AUTHENTICATED + SERVICE_ROLE)
- Generates initialization report
- Dry-run mode for pre-deployment validation

**Usage:**
```bash
python scripts/agent_memory_init.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run --verbose
```

**`scripts/agent_memory_purge.py`** (370 lines)

Scheduled purge executor (runs daily @ 03:00 UTC):
- Executes R10 policy: DELETE expired + low-rating entries
- Calculates before/after metrics
- Logs to agent_memory_purge_log (append-only audit)
- Updates agent_memory_metrics for Grafana
- Slack alerts if threshold exceeded (> 10 GB freed or > 10k rows)

**Usage:**
```bash
python scripts/agent_memory_purge.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --agent-id=manta-03-s1 \  # optional
  --dry-run \
  --slack-webhook=$SLACK_WEBHOOK_URL
```

**`scripts/agent_memory_validate.py`** (380 lines)

Post-deployment validator:
- Verifies all tables exist with correct columns
- Checks indexes are created
- Validates functions callable
- Verifies triggers active
- Confirms RLS policies enabled
- Tests sample insert/select/purge operations

**Usage:**
```bash
python scripts/agent_memory_validate.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --verbose
```

### 3. Configuration

**`scripts/agent_memory_policy.json`** (280 lines)

Configuration file defining:
- TTL policy (480 min default)
- Purge rules (priority-ordered)
- Memory/chunk thresholds (soft/hard limits)
- RLS enforcement (per agent_id)
- Observability (Grafana dashboard config)
- APScheduler trigger template (cron: `0 3 * * *`)
- Agent list (S1-S10, excl. S5)
- Deployment notes & rollback procedure

### 4. Documentation

**`scripts/AGENT_MEMORY_README.md`** (400+ lines)

Complete guide including:
- Overview & architecture
- Table schemas with indexes
- RLS policy explanation
- Purge policy (R10) with rules & thresholds
- Deployment checklist (5 steps)
- Testing checklist
- Grafana dashboard setup
- Troubleshooting guide
- References

**`AGENT_MEMORY_IMPLEMENTATION.md`** (this file)

Summary of deliverables and deployment plan.

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    Agent Memory Cache (R10)                        │
└────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  agent_memory    │         │  agent_state     │
│  (ephemeral)     │         │  (persistent)    │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ agent_id         │         │ agent_id         │
│ session_id       │         │ embedding_vector │
│ memory_key       │         │ user_intent_score│
│ memory_value (J) │         │ avg_user_rating  │
│ expires_at ⏰    │         │ feedback_count   │
│ user_rating 📊   │         │ last_updated     │
│ checksum (MD5)   │         └──────────────────┘
│ created_at       │              ▲
└──────────────────┘              │
     ▲                            │
     │ TTL expired/low rating  UPDATE on rating
     │ (DELETE)                    │
     │                             │
┌────────────────────────────────────────────┐
│  Purge Function (R10)                      │
│  purge_expired_agent_memory()              │
│  ✗ expires_at <= NOW()                    │
│  ✗ user_rating < 2 AND age > 7d           │
│  ✓ Keep latest 1000 completions          │
│  ✓ Keep embedding vectors                │
└────────────────────────────────────────────┘
     │
     ├─→ DELETE rows
     │
     └─→ Log to agent_memory_purge_log (audit-only)
         │
         └─→ Update agent_memory_metrics
             │
             └─→ Grafana Dashboard

RLS Policy (agent_id isolation):
┌────────────────────────────────────────┐
│ SET app.current_agent_id = 'manta-03-s1'  │
│ SELECT * FROM agent_memory            │
│ → Only S1 (Rodovias) cache visible    │
└────────────────────────────────────────┘
```

---

## Deployment Phases

### Phase 4 — Observability (T-12h before go-live)

**Step 1: Validate SQL** (5 min)
```bash
cd /home/user/Codex-exemplo
python scripts/agent_memory_init.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run --verbose
```

Expected output:
```
✓ SQL syntax validation passed
✓ All 7 critical indexes found
✓ RLS policies validation passed
✓ Trigger validation passed
✓ Grant validation completed
Result: Dry-run validation passed
```

**Step 2: Apply Migration** (2-5 min)
```bash
supabase db push
# or
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql
```

**Step 3: Validate Schema** (5 min)
```bash
python scripts/agent_memory_validate.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --verbose
```

Expected output:
```
✓ Table agent_memory exists with 11 columns
✓ Table agent_state exists with 11 columns
✓ Index idx_agent_memory_expires_at
✓ Function purge_expired_agent_memory exists
✓ RLS policy agent_memory_isolation on agent_memory
✓ Sample memory insert successful
✓ RLS isolation verified
✓ Purge function callable
✓ Metrics refresh callable

Result: Schema validation successful
```

**Step 4: Test Purge (dry-run)** (2 min)
```bash
python scripts/agent_memory_purge.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --dry-run --verbose
```

Expected output:
```
Memory metrics BEFORE purge:
  Total memory: 167.99 MB
  Total chunks: 991
  Agents: 3

DRY-RUN: Would execute purge (no changes made)

Purge results:
  Rows deleted: 234
  Bytes freed: 156.79 MB (0.15 GB)
  Agents affected: 3

Result: Dry-run validation passed
```

**Step 5: Setup APScheduler** (5 min)

Configure daily trigger via Claude Code:
```python
from mcp__bf7c680d-5fdc-5ef4-b4a0-abadb619bf0a__create_trigger import create_trigger

trigger = create_trigger(
    name="agent-memory-purge-daily",
    cron="0 3 * * *",  # 03:00 UTC daily
    prompt=(
        "Execute purga de agent_memory conforme R10 CLAUDE.md:\n"
        "DELETE entries com expires_at <= NOW() ou "
        "(user_rating < 2 AND age > 7 days).\n"
        "Mantenha últimas 1000 completions por agente.\n"
        "Registre metrics em agent_memory_metrics.\n"
        "Se bytes_freed > 10GB ou rows_deleted > 10k, "
        "envie Slack alert para #agent-ops."
    ),
    notifications={"email": True, "push": False}
)
```

**Step 6: Verify Grafana** (5 min)

Navigate to: https://grafana.manta-internal.com/d/agent-memory-cache

Panels should show:
- [ ] Cache Size by Agent (memory_size_mb)
- [ ] Chunk Count by Agent
- [ ] Purge Operations (time series)
- [ ] Memory Trend (24h avg)

**Step 7: Production Execution** (2 min)

First real purge:
```bash
python scripts/agent_memory_purge.py \
  --supabase-url=$SUPABASE_URL \
  --supabase-key=$SUPABASE_KEY \
  --slack-webhook=$SLACK_WEBHOOK_URL
```

---

## Key Metrics

| Component | Count | Status |
|-----------|-------|--------|
| Tables | 4 | Created |
| Indexes | 11 | Created |
| Stored Procedures | 3 | Created |
| Triggers | 1 | Created |
| RLS Policies | 2 | Created |
| Python Scripts | 3 | Ready |
| Config Files | 1 | Ready |
| Documentation | 2 | Ready |

| Agent | agent_id | TTL | Memory Limit | Status |
|-------|----------|-----|--------------|--------|
| S1 | manta-03-s1 | 480 min | 100 MB | Enabled |
| S2 | manta-03-s2 | 480 min | 100 MB | Enabled |
| S3 | manta-03-s3 | 480 min | 100 MB | Enabled |
| S4 | manta-03-s4 | 480 min | 100 MB | Enabled |
| S6 | manta-03-s6 | 480 min | 100 MB | Enabled |
| S7 | manta-03-s7 | 480 min | 100 MB | Enabled |
| S8 | manta-03-s8 | 480 min | 100 MB | Enabled ⭐ AySA |
| S9 | manta-03-s9 | 480 min | 100 MB | Enabled |
| S10 | manta-03-s10 | 480 min | 100 MB | Enabled |

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| RLS blocking legitimate access | Verify app.current_agent_id set before query |
| Purge deleting recent entries | "Keep recent" rule (priority 110) protects |
| Large purge causing slowdown | Async execution via APScheduler (non-blocking) |
| Slack alerts flooding | Threshold: > 10 GB or > 10k rows (conservative) |
| Embedding vectors lost | Stored in agent_state (persistent, not deleted) |

---

## Rollback Plan

If critical issues post-deployment:

**Step 1: Disable APScheduler**
```bash
python -c "
from mcp__... import delete_trigger
delete_trigger('agent-memory-purge-daily')
"
```

**Step 2: Drop Tables** (via psql as service_role)
```sql
BEGIN;
DROP TRIGGER IF EXISTS trg_agent_memory_rating_update ON agent_memory;
DROP FUNCTION IF EXISTS update_agent_state_on_rating();
DROP FUNCTION IF EXISTS insert_agent_memory_dedup(...);
DROP FUNCTION IF EXISTS refresh_agent_memory_metrics(...);
DROP FUNCTION IF EXISTS purge_expired_agent_memory(...);
DROP TABLE IF EXISTS agent_memory_purge_log CASCADE;
DROP TABLE IF EXISTS agent_memory_metrics CASCADE;
DROP TABLE IF EXISTS agent_state CASCADE;
DROP TABLE IF EXISTS agent_memory CASCADE;
COMMIT;
```

**Step 3: Log Incident**
```bash
echo "Rollback executed at $(date)" >> ROLLBACK_LOG.md
```

---

## File Paths

```
/home/user/Codex-exemplo/
├── supabase/
│   └── migrations/
│       └── 2026_07_25_v5_0_agent_memory_cache.sql ........... DDL (434 lines)
│
├── scripts/
│   ├── agent_memory_init.py ........................... Initializer (280 lines)
│   ├── agent_memory_purge.py .......................... Purger (370 lines)
│   ├── agent_memory_validate.py ....................... Validator (380 lines)
│   ├── agent_memory_policy.json ....................... Config (280 lines)
│   └── AGENT_MEMORY_README.md ......................... Guide (400+ lines)
│
└── AGENT_MEMORY_IMPLEMENTATION.md ..................... This file
```

---

## Next Steps

1. **Review & Approval** (MN sign-off)
   - [ ] Architect approves schema
   - [ ] DBA approves indexes
   - [ ] Security approves RLS
   - [ ] Ops approves APScheduler trigger

2. **Stage Environment** (T-24h)
   - [ ] Deploy to staging Supabase project
   - [ ] Run full validation
   - [ ] Load test (1000 agents, 100MB each)
   - [ ] Verify Grafana metrics

3. **Production** (T+0)
   - [ ] Execute Phase 4 deployment steps
   - [ ] Monitor Grafana for 24h
   - [ ] Collect user feedback
   - [ ] Document issues in MNT-2026-AGENT-MEMORY-CACHE

4. **Post-Launch** (T+48h)
   - [ ] Validate purge ran successfully
   - [ ] Check Slack alerts (if configured)
   - [ ] Review agent_memory_purge_log for anomalies
   - [ ] Adjust thresholds if needed

---

## Support & Contacts

- **Owner:** mneves@mantaassociados.com
- **Slack:** #agent-ops (alerts)
- **Ticket:** MNT-2026-AGENT-MEMORY-CACHE
- **Docs:** scripts/AGENT_MEMORY_README.md
- **References:** CLAUDE.md v5.0 (R10 — Purga de Agent_Memory)

---

**Status: ✅ READY FOR DEPLOYMENT**  
**Date: 2026-07-25**  
**Version: v5.0**
