# Background Agents Integration Guide (v5.0)

**Status:** Complete Framework Implementation  
**Date:** 2026-07-25  
**Segments:** S5 (Túneis) + Horizontais (Claims, Advisory, etc.)

---

## Overview

Background agents enable long-running tasks (> 30 seconds) without blocking the user. This integration connects:

1. **Framework Layer**: `background_agent_framework.py` — Job spawning, status tracking
2. **State Layer**: `agent_state_manager.py` — Memory persistence, embeddings
3. **Queue Layer**: `agent_job_queue.py` — APScheduler integration, retry logic
4. **Storage Layer**: 3 SQL migrations + 10+ tables/functions in Supabase

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ User Input: "Analise geotécnica de túnel de 5 km" + CAD (1.5MB) │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                     ┌────────▼────────┐
                     │ Agent Skill (S5)│
                     └─────────┬────────┘
                              │
                   ┌──────────▼──────────┐
                   │ should_background? │ > 30s?
                   └──────────┬──────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │ YES (background)   │ NO (sync)          │
         ▼                    ▼
   ┌──────────────┐    ┌──────────────┐
   │background_   │    │ Process      │
   │spawn()       │    │ inline       │
   └──────┬───────┘    └──────────────┘
          │
          │ Returns job_id immediately
          ▼
   ┌──────────────────────┐
   │ Supabase: agent_jobs │
   │ status = "pending"   │
   └──────┬───────────────┘
          │
    ┌─────▼──────────────────────────┐
    │ JobQueue (APScheduler)         │
    │ Polls every 1 second           │
    │ Spawns worker threads (max 5)  │
    └─────┬──────────────────────────┘
          │
          ▼
    ┌──────────────────────┐
    │ Worker processes     │
    │ agent_id prompt      │
    │ with timeout 300s    │
    └─────┬────────────────┘
          │
          ├─ Success ──────┐
          │                │
          │ Retry (max 2x) ├─────────┐
          │                │         │
          └─ Timeout ──────┘         │
                                     ▼
                          ┌────────────────────┐
                          │ hook: SubagentStop │
                          └──────────┬─────────┘
                                     │
                          ┌──────────▼─────────┐
                          │ store_result()     │
                          │ 1. Update agent_jobs
                          │ 2. Store in agent_memory
                          │ 3. Update agent_state
                          │ 4. Cache embedding
                          │ 5. Invoke callback
                          └────────────────────┘
```

---

## Files Delivered

### Python Scripts (3)

#### 1. `scripts/background_agent_framework.py`
- **Classes**: `BackgroundAgentFramework`, `JobStatus`, `BackgroundJobResult`
- **Public API**:
  - `background_spawn(agent_id, prompt, timeout_seconds, metadata, callback_url)` → job_id
  - `background_status(job_id)` → Dict with status + result
  - `background_list(agent_id, status)` → List[Dict]
- **Responsibilities**:
  - Create jobs in `agent_jobs` table
  - Fetch job status
  - List jobs with filtering
  - Cleanup expired jobs (> 7 days)

#### 2. `scripts/agent_state_manager.py`
- **Classes**: `AgentStateManager`, `StateEntry`
- **Public API**:
  - `store_result(agent_id, session_id, result_text, prompt, rating, ttl)` → bool
  - `store_memory(agent_id, session_id, memory_key, value, prompt, rating, ttl)` → memory_id
  - `get_memories(agent_id, session_id, memory_key, limit)` → List[Dict]
  - `purge_expired_memories(agent_id)` → count
  - `embed_text(text)` → [1536 floats]
  - `cache_embedding(agent_id, query_text, embedding)` → bool
  - `get_agent_stats(agent_id)` → Dict with metrics
- **Responsibilities**:
  - Store results in `agent_memory` (TTL 480 min)
  - Update `agent_state` with embeddings + ratings
  - Deduplication via MD5 checksum
  - TTL cleanup (R10 policy)
  - Embedding generation + caching (R9 feedback loop)

#### 3. `scripts/agent_job_queue.py`
- **Classes**: `BackgroundJobQueue`, `BackgroundJobWorker`
- **Public API**:
  - `start_queue()` → bool
  - `stop_queue()` → bool
  - `queue_status()` → Dict with active_jobs, is_running, etc.
- **Responsibilities**:
  - Poll `agent_jobs` table for PENDING status (1s interval)
  - Spawn worker threads (max 5 concurrent)
  - Execute agent with 300s timeout
  - Handle timeout → retry logic (2x max)
  - Update job status (pending → running → completed/failed/timeout)
  - Invoke callback webhooks
  - APScheduler integration for background execution

### SQL Migration (1)

#### `supabase/migrations/2026_07_25_agent_background_jobs.sql`
- **Tables**:
  - `agent_jobs` — Job queue (id, status, prompt, result, retry_count, etc.)
  - `agent_job_logs` — Audit trail (append-only, status transitions)
  - `agent_job_metrics` — Aggregations (total_jobs, success_rate, avg_duration)
- **Indexes** (7):
  - `idx_agent_jobs_status` — Query pending jobs fast
  - `idx_agent_jobs_agent_id` — Filter by agent
  - `idx_agent_jobs_created_at` — Chronological
  - `idx_agent_jobs_cleanup` — Cleanup old jobs
- **Functions** (3):
  - `log_job_status_change()` — Audit logging
  - `refresh_agent_job_metrics()` — Auto aggregation
  - `cleanup_old_agent_jobs(days)` — TTL purge
- **Triggers** (3):
  - `trg_agent_jobs_log_status` — Log transitions
  - `trg_agent_jobs_refresh_metrics` — Update metrics
  - `trg_agent_jobs_update_timestamp` — Auto timestamp
- **RLS Policies** (2):
  - `agent_jobs_isolation` — Per-agent access
  - `agent_job_logs_insert/read` — Audit trail

### Skill Example (1)

#### `.claude/agents/example_background_agent_skill.md`
- Runnable example: S5 (Túneis) geotechnical analysis
- Shows:
  - How to estimate processing time
  - When to trigger background (> 30s)
  - How to call `background_spawn()`
  - How to provide status endpoint
  - Integration with hook `SubagentStop`
  - CLI for monitoring jobs
  - Full user workflow

---

## Integration Steps

### Step 1: Deploy SQL Schema

```bash
# Apply migration to Supabase
supabase db push

# Or manually:
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_agent_background_jobs.sql
```

**Verifies:**
- ✅ 3 tables created (agent_jobs, agent_job_logs, agent_job_metrics)
- ✅ 4 indexes created
- ✅ 3 functions created
- ✅ 3 triggers enabled
- ✅ RLS policies enabled

### Step 2: Update settings.json (Add Hook)

In `.claude/settings.json`, add `subagent_stop` hook:

```json
{
  "hooks": {
    "subagent_stop": {
      "enabled": true,
      "label": "BackgroundJobCompletion v5.0",
      "steps": [
        {
          "step": 1,
          "name": "store_background_result",
          "description": "Store job result in agent_memory + agent_state",
          "script": "scripts/background_job_completion_handler.py",
          "parameters": {
            "job_id": "$JOB_ID",
            "agent_id": "$AGENT_ID",
            "result": "$AGENT_OUTPUT",
            "user_rating": "$USER_FEEDBACK_SCORE"
          },
          "on_error": "warn"
        }
      ]
    }
  }
}
```

### Step 3: Start Job Queue Processor

**Option A: Manual (Development)**

```bash
# Terminal 1: Start processor (blocks, press Ctrl+C to stop)
$ python scripts/agent_job_queue.py start

# Terminal 2: Monitor
$ watch python scripts/agent_job_queue.py status
```

**Option B: Systemd Service (Production)**

```ini
# /etc/systemd/system/manta-job-queue.service
[Unit]
Description=Manta Background Job Queue Processor
After=network.target

[Service]
Type=simple
User=manta
WorkingDirectory=/home/manta/Codex-exemplo
ExecStart=/usr/bin/python3 scripts/agent_job_queue.py start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable manta-job-queue
sudo systemctl start manta-job-queue
sudo systemctl status manta-job-queue
```

**Option C: Docker (Containerized)**

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY scripts scripts/
CMD ["python", "scripts/agent_job_queue.py", "start"]
```

```bash
docker build -t manta-job-queue .
docker run -d --name manta-job-queue \
  -e SUPABASE_URL="$SUPABASE_URL" \
  -e SUPABASE_KEY="$SUPABASE_KEY" \
  manta-job-queue
```

### Step 4: Update Agent Skills (Example)

In any agent skill (S5, Claims, etc.), add background detection:

```python
from scripts.background_agent_framework import background_spawn

def estimate_time(file_mb, complexity):
    """Heuristic: 30s base + 20s per MB + complexity factor"""
    return int(30 + file_mb * 20 + {
        "basico": 0,
        "executivo": 30,
        "risco-completo": 60
    }.get(complexity, 0))

def main():
    file_mb = 1.5
    complexity = "risco-completo"
    
    if estimate_time(file_mb, complexity) > 30:
        # BACKGROUND PATH
        job_id = background_spawn(
            agent_id="manta-03-s5",
            prompt="Analise geotécnica de túnel de 5 km",
            timeout_seconds=300
        )
        print(f"Análise iniciada. Job ID: {job_id}")
        print(f"Status: /api/jobs/{job_id}/status")
    else:
        # SYNC PATH
        result = process_inline()
        print(result)
```

### Step 5: Create Status Endpoint (API)

```python
# api/jobs.py (FastAPI example)
from fastapi import FastAPI, HTTPException
from scripts.background_agent_framework import background_status

app = FastAPI()

@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Check background job status."""
    result = background_status(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": result["status"],  # pending|running|completed|failed|timeout
        "result": result.get("result"),
        "error": result.get("error"),
        "started_at": result.get("started_at"),
        "completed_at": result.get("completed_at"),
    }

@app.post("/api/jobs/{job_id}/rate")
async def rate_job(job_id: str, rating: int):
    """User rates the job result (0-5)."""
    # Update agent_memory with user_rating
    # Aggregated in agent_state for R9 feedback loop
    pass
```

---

## Usage Examples

### CLI: Spawn Job

```bash
$ python scripts/background_agent_framework.py spawn \
  --agent-id manta-03-s5 \
  --prompt "Analise viabilidade de túnel" \
  --timeout 300

# Output:
# Job spawned: 550e8400-e29b-41d4-a716-446655440000
```

### CLI: Check Status

```bash
$ python scripts/background_agent_framework.py status 550e8400-e29b-41d4-a716-446655440000

# Output:
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "agent_id": "manta-03-s5",
#   "status": "running",
#   "created_at": "2026-07-25T14:32:00Z",
#   "started_at": "2026-07-25T14:32:05Z",
#   "retry_count": 0
# }
```

### CLI: List Jobs

```bash
$ python scripts/background_agent_framework.py list \
  --agent-id manta-03-s5 \
  --status pending

# Output:
# [
#   { "id": "550e8400-...", "status": "pending", ... },
#   { "id": "550e8401-...", "status": "pending", ... }
# ]
```

### CLI: Cleanup Expired

```bash
$ python scripts/background_agent_framework.py cleanup --days 7

# Output:
# Deleted 15 expired jobs
```

### Python: In Agent Skill

```python
from scripts.background_agent_framework import background_spawn, background_status

# Spawn
job_id = background_spawn("manta-03-s5", "Analyze tunnel", timeout_seconds=300)
print(f"Job: {job_id}")

# Check status (e.g., in polling loop)
status = background_status(job_id)
print(status["status"])  # "pending"|"running"|"completed"|"failed"|"timeout"
```

### Python: Store State

```python
from scripts.agent_state_manager import store_result

# Store result after agent completes
store_result(
    agent_id="manta-03-s5",
    session_id="sess_abc123",
    result_text="Análise geotécnica: Viável com ressalvas...",
    source_prompt="Analise viabilidade de túnel",
    user_rating=5,  # User liked it
    ttl_minutes=480  # Keep for 8 hours
)
```

---

## Monitoring & Observability

### Table: `agent_job_metrics`

Auto-populated by triggers. Query for insights:

```sql
-- Jobs per agent (last 7 days)
SELECT agent_id, total_jobs, success_rate, avg_duration_seconds
FROM agent_job_metrics
WHERE updated_at > NOW() - INTERVAL '7 days'
ORDER BY total_jobs DESC;

-- Slowest agents
SELECT agent_id, avg_duration_seconds
FROM agent_job_metrics
WHERE avg_duration_seconds > 120
ORDER BY avg_duration_seconds DESC;
```

### Table: `agent_job_logs`

Audit trail. Example queries:

```sql
-- Timeout history for S5
SELECT COUNT(*) as timeouts, agent_id
FROM agent_job_logs
WHERE new_status = 'timeout' AND agent_id LIKE 'manta-03-s5%'
GROUP BY agent_id;

-- Retry patterns
SELECT job_id, COUNT(*) as transitions
FROM agent_job_logs
GROUP BY job_id
HAVING COUNT(*) > 3  -- Jobs that transitioned > 3 times
ORDER BY COUNT(*) DESC
LIMIT 10;
```

### Grafana Dashboard (Optional)

```json
{
  "dashboard": {
    "title": "Background Job Queue",
    "panels": [
      {
        "title": "Active Jobs",
        "targets": [
          {
            "expr": "SELECT COUNT(*) FROM agent_jobs WHERE status = 'running'"
          }
        ]
      },
      {
        "title": "Success Rate by Agent",
        "targets": [
          {
            "expr": "SELECT agent_id, success_rate FROM agent_job_metrics"
          }
        ]
      },
      {
        "title": "Avg Duration (seconds)",
        "targets": [
          {
            "expr": "SELECT agent_id, avg_duration_seconds FROM agent_job_metrics"
          }
        ]
      }
    ]
  }
}
```

---

## Troubleshooting

### Problem: Jobs stuck in "pending"

**Diagnosis:**

```bash
$ python scripts/agent_job_queue.py status

# If not running, start it
$ python scripts/agent_job_queue.py start &
```

**Solution:**
- Check if processor is running
- Check logs for errors
- Verify Supabase connectivity (env vars)

### Problem: Jobs timeout repeatedly

**Diagnosis:**

```sql
SELECT id, agent_id, retry_count, timeout_seconds
FROM agent_jobs
WHERE status = 'timeout'
ORDER BY created_at DESC
LIMIT 10;
```

**Solution:**
- Increase `timeout_seconds` parameter
- Optimize agent code
- Check if agent is hanging (not returning)

### Problem: Memory grows unbounded

**Diagnosis:**

```sql
SELECT COUNT(*) as expired_entries
FROM agent_memory
WHERE expires_at < NOW();
```

**Solution:**
- Trigger purge: `python scripts/agent_state_manager.py purge --agent-id manta-03-s5`
- Or schedule daily via APScheduler

### Problem: "Supabase not available" warning

**Diagnosis:**

```bash
$ echo $SUPABASE_URL $SUPABASE_KEY | grep -v "^$"
```

**Solution:**
- Set env vars in `.env.local` (dev) or Key Vault (prod)
- See credentials section in settings.json

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Job spawn latency | < 100ms | Synchronous INSERT |
| Poll latency (per job) | 1s interval | Configurable |
| Worker startup | < 500ms | Thread spawn + agent init |
| Job completion store | < 500ms | 3x INSERT (jobs, memory, state) |
| Callback webhook | < 10s timeout | Fire-and-forget |
| Max concurrent jobs | 5 | Configurable per instance |
| Job result TTL | 30 days | After `completed_at` |
| Memory TTL | 8 hours | 480 min, configurable |

---

## Rollback Procedure

If issues arise:

```bash
# 1. Stop job queue
python scripts/agent_job_queue.py stop

# 2. Rollback SQL (in Supabase)
-- See bottom of: supabase/migrations/2026_07_25_agent_background_jobs.sql
-- Uncomment and run DROP statements

# 3. Remove scripts
rm scripts/background_agent_framework.py
rm scripts/agent_state_manager.py
rm scripts/agent_job_queue.py

# 4. Remove hook from settings.json
# Delete the "subagent_stop" section
```

---

## Next Steps

1. **Deployment**: Apply SQL schema to staging Supabase
2. **Testing**: Start job queue processor, spawn test job
3. **Integration**: Update 2-3 agent skills (S5, Claims, Advisory)
4. **Monitoring**: Set up Grafana dashboard
5. **Rollout**: Gradual rollout to production
6. **Feedback**: Collect metrics from real usage, optimize

---

## References

- `CLAUDE.md` — P7 (Orquestração em Background)
- `scripts/background_agent_framework.py` — API reference
- `scripts/agent_state_manager.py` — State persistence
- `scripts/agent_job_queue.py` — Queue processor
- `.claude/agents/example_background_agent_skill.md` — Full walkthrough
