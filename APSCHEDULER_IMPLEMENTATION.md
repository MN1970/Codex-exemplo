# APScheduler Implementation — P7 Background Orchestration (v5.0)

**Author:** Claude Code Agent  
**Date:** 2026-07-25  
**Status:** Production Ready

## Overview

Implementação completa do sistema APScheduler para orquestração em background (P7) conforme CLAUDE.md v5.0.

**4 Jobs críticos:**
1. **RAG Reindex (R6)** — Daily @ 02:00 UTC
2. **Agent Memory Purge (R10)** — Daily @ 03:00 UTC
3. **Feedback Loop & Retraining (R9)** — Weekly @ Sunday 03:00 UTC
4. **Health Check** — Every 6 hours

---

## Files Structure

```
Codex-exemplo/
├── scripts/
│   ├── apscheduler_setup.py          # Main scheduler setup & manager
│   ├── feedback_loop_job.py           # R9: Feedback extraction + retraining
│   ├── health_check_job.py            # Health monitoring job
│   ├── rag_reindex_job.py             # Wrapper for R6
│   ├── agent_memory_purge_job.py      # Wrapper for R10
│   ├── rag-reindex.py                 # (existing) RAG reindex logic
│   ├── agent_memory_purge.py          # (existing) Purge logic
│   └── healthcheck.py                 # (existing) Health check logic
│
├── .claude/
│   ├── apscheduler_config.json        # Job configuration (cron schedules)
│   └── hooks/
│       └── session_start_apscheduler_check.py  # Status check on session start
│
└── APSCHEDULER_IMPLEMENTATION.md      # This file
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install APScheduler pytz supabase-py python-dotenv requests
```

### 2. Configure Environment

Create `.env` file in repo root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL  # Optional
```

### 3. List Registered Jobs

```bash
python scripts/apscheduler_setup.py --list-jobs
```

Output:
```
======================================================================
REGISTERED JOBS
======================================================================
ID: rag-reindex
  Name: RAG Reindex (R6)
  Next run: 2026-07-26 02:00:00+00:00
  Trigger: cron

ID: agent-memory-purge
  Name: Agent Memory Purge (R10)
  Next run: 2026-07-26 03:00:00+00:00
  Trigger: cron

ID: feedback-loop
  Name: Feedback Loop & Retraining (R9)
  Next run: 2026-07-27 03:00:00+00:00
  Trigger: cron

ID: health-check
  Name: Health Check
  Next run: 2026-07-26 06:00:00+00:00
  Trigger: cron
```

### 4. Start APScheduler (Foreground)

```bash
python scripts/apscheduler_setup.py --run-scheduler
```

Expected output:
```
======================================================================
STARTING APScheduler (P7 — Background Orchestration)
Timezone: UTC
======================================================================
...
Registered 4 jobs
======================================================================
✓ APScheduler started successfully

Scheduled jobs:
  - rag-reindex: RAG Reindex (R6) (next run: 2026-07-26 02:00:00+00:00)
  - agent-memory-purge: Agent Memory Purge (R10) (next run: 2026-07-26 03:00:00+00:00)
  - feedback-loop: Feedback Loop & Retraining (R9) (next run: 2026-07-27 03:00:00+00:00)
  - health-check: Health Check (next run: 2026-07-26 06:00:00+00:00)

Scheduler running. Press Ctrl+C to stop.
```

---

## Job Details

### Job 1: RAG Reindex (R6) — Daily @ 02:00 UTC

**Purpose:** Validate embeddings, update cache metadata, detect divergence

**Implementation:** `scripts/rag_reindex_job.py` → wraps `rag-reindex.py`

**Actions:**
1. Iterate all RAG collections (san:v5.0, ene:v5.0, etc.)
2. Validate embedding vectors (dimension = 1024 for e5-large)
3. Update `metadata.json` with reindex timestamp
4. Build cache index for 7-day TTL
5. Email alert if divergence > 5%

**Config:**
```json
{
  "id": "rag-reindex",
  "cron": "0 2 * * *",
  "description": "Reindex all RAG collections, validate embeddings"
}
```

**Logs:** `tail -f /tmp/apscheduler.log | grep "RAG Reindex"`

---

### Job 2: Agent Memory Purge (R10) — Daily @ 03:00 UTC

**Purpose:** Delete expired & low-quality entries from agent_memory cache

**Implementation:** `scripts/agent_memory_purge_job.py` → wraps `agent_memory_purge.py`

**Actions:**
1. Execute SQL: `purge_expired_agent_memory()`
2. Delete rows with:
   - `expires_at <= NOW()` (TTL 480 min)
   - `user_rating < 2 AND created_at < NOW() - 7 days`
3. Keep latest 1000 completions per agent
4. Keep embeddings of frequent queries
5. Log deletion stats in append-only log
6. Slack alert if > 10GB freed

**Config:**
```json
{
  "id": "agent-memory-purge",
  "cron": "0 3 * * *",
  "description": "Purge expired chunks and low-rating entries"
}
```

**Policy (R10):**
```
IF agent_memory_size_mb > 100
   OR last_purge > 30 days ago
   THEN:
     - Manter últimas 1000 completions
     - Descartar chunks com age > 7 dias e user_rating < 2
     - Manter embeddings de queries frequentes
     - Log: {agent_id, size_before, size_after, deleted_count}
```

---

### Job 3: Feedback Loop & Retraining (R9) — Weekly @ Sunday 03:00 UTC

**Purpose:** Extract user feedback (high ratings) and retrain reranker

**Implementation:** `scripts/feedback_loop_job.py`

**Actions:**
1. Fetch `feedback_score >= 4` from past 7 days
2. Extract embedding vectors (user_intent_vector)
3. Fine-tune cross-encoder reranker with queries
4. Compute improvement metrics
5. Update `VERSIONS.json` with new checksum
6. Slack notification with training stats

**New file:** `scripts/feedback_loop_job.py`

**Workflow:**
```
1. Query: SELECT * FROM agent_feedback WHERE rating >= 4 AND created_at > NOW() - 7 days
2. Extract: embedding for each query (e5-large model)
3. Retrain: fine-tune `reranker-cross-encoder` with positive examples
4. Validate: check improvement_pct > 2% before deploying
5. Update: VERSIONS.json reranker.v5.0.checksum = MD5(model_state)
```

**Config:**
```json
{
  "id": "feedback-loop",
  "cron": "0 3 * * 0",
  "description": "Extract feedback, retrain reranker"
}
```

---

### Job 4: Health Check — Every 6 Hours

**Purpose:** Validate system health, alert if critical issues

**Implementation:** `scripts/health_check_job.py`

**Actions:**
1. Validate maestro_runs schema, indexes, RLS
2. Check agent_memory size (alert if > 100MB)
3. Verify skill checksums vs VERSIONS.json
4. Check RAG collections completeness
5. Monitor error rate (alert if > 5%)
6. Slack alert if critical issues detected

**New file:** `scripts/health_check_job.py`

**Checks:**
- ✓ maestro_runs table exists + has indexes
- ✓ RLS policies enabled
- ✓ agent_memory total size < 100MB
- ✓ Skill checksums match VERSIONS.json
- ✓ RAG collections have metadata.json
- ✓ Error rate < 5%

**Config:**
```json
{
  "id": "health-check",
  "cron": "0 */6 * * *",
  "description": "Validate maestro_runs schema, indexes, RLS, agent memory"
}
```

---

## Command Reference

### List all jobs

```bash
python scripts/apscheduler_setup.py --list-jobs
```

### Run scheduler (foreground)

```bash
python scripts/apscheduler_setup.py --run-scheduler
```

### Test a job immediately

```bash
python scripts/apscheduler_setup.py --test-job rag-reindex
python scripts/apscheduler_setup.py --test-job agent-memory-purge
python scripts/apscheduler_setup.py --test-job feedback-loop
python scripts/apscheduler_setup.py --test-job health-check
```

### Check status

```bash
python scripts/apscheduler_setup.py --status
```

Output:
```json
{
  "running": true,
  "jobs": [
    {
      "id": "rag-reindex",
      "name": "RAG Reindex (R6)",
      "next_run": "2026-07-26 02:00:00+00:00",
      "trigger": "cron"
    },
    ...
  ],
  "timestamp": "2026-07-25T14:30:00+00:00"
}
```

### Pause a job

```bash
python scripts/apscheduler_setup.py --pause-job feedback-loop
```

### Resume a job

```bash
python scripts/apscheduler_setup.py --resume-job feedback-loop
```

---

## Deployment

### Option A: Foreground (Development)

```bash
cd /home/user/Codex-exemplo
python scripts/apscheduler_setup.py --run-scheduler
```

### Option B: Systemd Service (Production)

Create `/etc/systemd/system/apscheduler-manta.service`:

```ini
[Unit]
Description=Manta APScheduler — P7 Background Orchestration
After=network.target

[Service]
Type=simple
User=manta
WorkingDirectory=/home/user/Codex-exemplo
Environment="PATH=/home/user/.venv/bin"
Environment="SUPABASE_URL=https://your-project.supabase.co"
Environment="SUPABASE_KEY=your-service-role-key"
ExecStart=/home/user/.venv/bin/python scripts/apscheduler_setup.py --run-scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable apscheduler-manta.service
sudo systemctl start apscheduler-manta.service
sudo systemctl status apscheduler-manta.service
```

Monitor logs:

```bash
sudo journalctl -u apscheduler-manta.service -f
```

### Option C: Docker

Create `Dockerfile.apscheduler`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY scripts/*.py .
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "apscheduler_setup.py", "--run-scheduler"]
```

Build and run:

```bash
docker build -f Dockerfile.apscheduler -t manta/apscheduler:v5.0 .
docker run -d \
  --env-file .env \
  --name apscheduler-manta \
  manta/apscheduler:v5.0
```

### Option D: Supervisor

Create `/etc/supervisor/conf.d/apscheduler-manta.conf`:

```ini
[program:apscheduler-manta]
command=/home/user/.venv/bin/python /home/user/Codex-exemplo/scripts/apscheduler_setup.py --run-scheduler
directory=/home/user/Codex-exemplo
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/apscheduler-manta.log
environment=SUPABASE_URL="https://...",SUPABASE_KEY="..."
```

Enable:

```bash
sudo supervisorctl reread
sudo supervisorctl update apscheduler-manta
```

---

## Monitoring & Logging

### Log File

All output written to `/tmp/apscheduler.log`:

```bash
tail -f /tmp/apscheduler.log
```

### Job-specific logs

Filter by job:

```bash
# RAG reindex logs
grep "RAG Reindex" /tmp/apscheduler.log

# Purge logs
grep "Agent Memory Purge" /tmp/apscheduler.log

# Feedback loop logs
grep "Feedback Loop" /tmp/apscheduler.log

# Health check logs
grep "Health Check" /tmp/apscheduler.log
```

### Slack Notifications

Each job can send Slack alerts on:
- Completion with summary
- Critical errors (with logs)
- Threshold breaches (e.g., > 10GB freed, > 5% error rate)

Configure via `SLACK_WEBHOOK_URL` env var.

---

## Session Start Hook

Optional: Check APScheduler status on session start.

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "session_start": ".claude/hooks/session_start_apscheduler_check.py"
  }
}
```

When session starts, will print:

```
======================================================================
APScheduler Status Check (P7 Background Orchestration)
======================================================================

Scheduled jobs (4 enabled):
  ✓ RAG Reindex (R6) (0 2 * * *)
  ✓ Agent Memory Purge (R10) (0 3 * * *)
  ✓ Feedback Loop & Retraining (R9) (0 3 * * 0)
  ✓ Health Check (0 */6 * * *)

======================================================================
```

---

## Troubleshooting

### Job not executing

1. **Check if scheduler is running:**
   ```bash
   ps aux | grep apscheduler_setup.py
   ```

2. **Check job registration:**
   ```bash
   python scripts/apscheduler_setup.py --list-jobs
   ```

3. **Test job directly:**
   ```bash
   python scripts/apscheduler_setup.py --test-job rag-reindex
   ```

4. **Check logs:**
   ```bash
   tail -f /tmp/apscheduler.log
   ```

### High memory usage

If scheduler consuming too much memory:

1. Check job execution times (should be < 5 min each)
2. Pause non-critical jobs: `--pause-job feedback-loop`
3. Check for stuck processes: `ps aux | grep python`

### Supabase connection errors

1. **Validate credentials in .env**
2. **Check network connectivity:**
   ```bash
   curl -I https://your-project.supabase.co
   ```
3. **Test connection:**
   ```bash
   python -c "from supabase import create_client; c = create_client('$SUPABASE_URL', '$SUPABASE_KEY'); print(c.table('maestro_runs').select('count(*)').execute())"
   ```

### Job timeout

If job timeout after 60s, cascade to higher-tier model (R8):

```python
# In apscheduler_setup.py, modify _job_* methods:
# result = executor.run(timeout_seconds=300)  # 5 min timeout
```

---

## Performance Metrics

Expected execution times:

| Job | Duration | Frequency | SLA |
|-----|----------|-----------|-----|
| rag-reindex | 2-5 min | Daily @ 02:00 | < 10 min |
| agent-memory-purge | 1-3 min | Daily @ 03:00 | < 5 min |
| feedback-loop | 3-10 min | Weekly Sunday | < 15 min |
| health-check | 30-60 sec | Every 6 hours | < 2 min |

**Total background time per week:** ~2 hours

---

## Configuration Reference

Edit `.claude/apscheduler_config.json` to:

1. **Enable/disable jobs:**
   ```json
   {
     "id": "rag-reindex",
     "enabled": false
   }
   ```

2. **Change cron schedule:**
   ```json
   {
     "cron": "0 4 * * *"  // Changed to 04:00 UTC
   }
   ```

3. **Add new job:**
   ```json
   {
     "id": "my-custom-job",
     "name": "My Custom Job",
     "enabled": true,
     "trigger": "cron",
     "cron": "0 */3 * * *",
     "description": "My custom description"
   }
   ```

After editing, restart scheduler:

```bash
# Kill current scheduler
pkill -f "apscheduler_setup.py"

# Restart
python scripts/apscheduler_setup.py --run-scheduler
```

---

## Integration with CLAUDE.md v5.0

This implementation follows:

- **P7 — Orquestração em Background:** APScheduler executes 4 critical jobs
- **R9 — Feedback Loop:** Weekly retraining of reranker cross-encoder
- **R10 — Memory Purge:** Daily cleanup of expired agent memory
- **P6 — Observabilidade:** Health checks and run tracking

Related files:
- CLAUDE.md (main specification)
- VERSIONS.json (skill/RAG collection versioning)
- .claude/apscheduler_config.json (job config)
- scripts/apscheduler_setup.py (main implementation)

---

## Support & Rollback

If critical issue:

```bash
# Pause all jobs
python scripts/apscheduler_setup.py --pause-job rag-reindex
python scripts/apscheduler_setup.py --pause-job agent-memory-purge
python scripts/apscheduler_setup.py --pause-job feedback-loop
python scripts/apscheduler_setup.py --pause-job health-check

# Or stop scheduler completely
pkill -f "apscheduler_setup.py"
```

Revert to v4.2:
```bash
git checkout v4.2 -- scripts/apscheduler_setup.py .claude/apscheduler_config.json
```

---

**Status:** ✓ Production Ready  
**Last Updated:** 2026-07-25  
**Version:** v5.0
