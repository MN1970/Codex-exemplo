# APScheduler Deployment Guide — P7 Background Orchestration

**Quick Reference for Deployment & Operations**

---

## Pre-requisites

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
# Or manually:
pip install APScheduler==3.10.4 pytz supabase-py python-dotenv requests
```

### 2. Configure Environment Variables

Create `.env` file:

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional but recommended
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Verify VERSIONS.json

APScheduler needs `VERSIONS.json` for skill checksums:

```bash
# Check if VERSIONS.json exists and is valid
python3 -c "import json; json.load(open('VERSIONS.json'))" && echo "✓ VERSIONS.json valid"
```

---

## Deployment Methods

### Method 1: Docker (Recommended for Production)

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy repo
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run APScheduler
ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/apscheduler_setup.py", "--run-scheduler"]
```

#### Build and Run

```bash
# Build image
docker build -t manta-apscheduler:v5.0 .

# Run container
docker run -d \
  --name apscheduler-manta \
  --env-file .env \
  -v $(pwd)/logs:/tmp \
  --restart unless-stopped \
  manta-apscheduler:v5.0

# Check logs
docker logs -f apscheduler-manta
```

---

### Method 2: Systemd Service (Linux)

#### Create Service File

```bash
sudo tee /etc/systemd/system/apscheduler-manta.service > /dev/null << 'EOL'
[Unit]
Description=Manta APScheduler — P7 Background Orchestration
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=manta
Group=manta
WorkingDirectory=/home/manta/Codex-exemplo
EnvironmentFile=/home/manta/Codex-exemplo/.env
ExecStart=/home/manta/.venv/bin/python scripts/apscheduler_setup.py --run-scheduler
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL
```

#### Enable and Start

```bash
# Enable on boot
sudo systemctl enable apscheduler-manta.service

# Start service
sudo systemctl start apscheduler-manta.service

# Check status
sudo systemctl status apscheduler-manta.service

# View logs
sudo journalctl -u apscheduler-manta.service -f

# Stop service
sudo systemctl stop apscheduler-manta.service
```

---

### Method 3: Supervisor

#### Create Config

```bash
sudo tee /etc/supervisor/conf.d/apscheduler-manta.conf > /dev/null << 'EOL'
[program:apscheduler-manta]
directory=/home/manta/Codex-exemplo
command=/home/manta/.venv/bin/python scripts/apscheduler_setup.py --run-scheduler
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/apscheduler-manta.log
stopsignal=INT
stopasgroup=true
environment=SUPABASE_URL="...",SUPABASE_KEY="..."
EOL
```

#### Enable

```bash
sudo supervisorctl reread
sudo supervisorctl update apscheduler-manta
sudo supervisorctl start apscheduler-manta
sudo supervisorctl tail -f apscheduler-manta
```

---

### Method 4: Local Development

#### Foreground Execution

```bash
cd /home/user/Codex-exemplo
python scripts/apscheduler_setup.py --run-scheduler
```

#### Background Execution (nohup)

```bash
nohup python scripts/apscheduler_setup.py --run-scheduler > /tmp/apscheduler.log 2>&1 &
echo $! > /tmp/apscheduler.pid
```

---

## Post-Deployment Checks

### 1. Verify Service is Running

```bash
# Check process
ps aux | grep apscheduler_setup.py

# Check port (if health check endpoint exposed)
curl http://localhost:8080/health
```

### 2. List Scheduled Jobs

```bash
python scripts/apscheduler_setup.py --list-jobs
```

Expected output shows 4 jobs with next run times.

### 3. Test Each Job

```bash
# Test RAG reindex
python scripts/apscheduler_setup.py --test-job rag-reindex

# Test agent memory purge
python scripts/apscheduler_setup.py --test-job agent-memory-purge

# Test feedback loop
python scripts/apscheduler_setup.py --test-job feedback-loop

# Test health check
python scripts/apscheduler_setup.py --test-job health-check
```

### 4. Check Logs

```bash
# All logs
tail -f /tmp/apscheduler.log

# Specific job
grep "RAG Reindex" /tmp/apscheduler.log
```

---

## Job Schedule Summary

| Job | Schedule | UTC Time | Frequency |
|-----|----------|----------|-----------|
| rag-reindex | `0 2 * * *` | 02:00 | Daily |
| agent-memory-purge | `0 3 * * *` | 03:00 | Daily |
| feedback-loop | `0 3 * * 0` | 03:00 Sun | Weekly |
| health-check | `0 */6 * * *` | Every 6h | 4x daily |

---

## Monitoring & Alerting

### Slack Notifications

Jobs send alerts when:
- **rag-reindex:** Divergence > 5% or embedding validation fails
- **agent-memory-purge:** > 10GB freed or > 10000 rows deleted
- **feedback-loop:** Training completed with improvement metrics
- **health-check:** Critical issues detected (schema, checksums, etc.)

Configure via `SLACK_WEBHOOK_URL` env var.

### Metrics

Access via `.claude/apscheduler_config.json` or Grafana:

```bash
# View APScheduler status
python scripts/apscheduler_setup.py --status
```

### Alerts

Subscribe to job failures:
1. Check `/tmp/apscheduler.log` for errors
2. Configure Slack webhook for notifications
3. Setup CloudWatch/Grafana for metrics

---

## Troubleshooting

### Scheduler Not Starting

```bash
# Check Python installation
python --version

# Check APScheduler install
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✓ APScheduler installed')"

# Check env vars
env | grep SUPABASE
```

### Job Execution Failures

```bash
# View logs
tail -100 /tmp/apscheduler.log

# Test specific job
python scripts/apscheduler_setup.py --test-job rag-reindex

# Enable verbose logging
LOGLEVEL=DEBUG python scripts/apscheduler_setup.py --run-scheduler
```

### High Memory Usage

```bash
# Monitor memory
watch 'ps aux | grep apscheduler_setup.py'

# Pause non-critical jobs
python scripts/apscheduler_setup.py --pause-job feedback-loop

# Check for stuck processes
lsof -p $(pgrep -f apscheduler_setup.py)
```

### Supabase Connection Issues

```bash
# Test connection
python -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
c = create_client(url, key)
r = c.table('maestro_runs').select('count(*)').execute()
print(f'Connected! Records: {r.count}')
"
```

---

## Operational Tasks

### Pause All Jobs

```bash
python scripts/apscheduler_setup.py --pause-job rag-reindex
python scripts/apscheduler_setup.py --pause-job agent-memory-purge
python scripts/apscheduler_setup.py --pause-job feedback-loop
python scripts/apscheduler_setup.py --pause-job health-check
```

### Resume All Jobs

```bash
python scripts/apscheduler_setup.py --resume-job rag-reindex
python scripts/apscheduler_setup.py --resume-job agent-memory-purge
python scripts/apscheduler_setup.py --resume-job feedback-loop
python scripts/apscheduler_setup.py --resume-job health-check
```

### Restart Service

```bash
# Systemd
sudo systemctl restart apscheduler-manta.service

# Supervisor
sudo supervisorctl restart apscheduler-manta

# Manual
pkill -f apscheduler_setup.py
python scripts/apscheduler_setup.py --run-scheduler &
```

### View Job Configuration

```bash
cat .claude/apscheduler_config.json | python -m json.tool
```

### Modify Job Schedule

Edit `.claude/apscheduler_config.json`:

```json
{
  "id": "rag-reindex",
  "cron": "0 4 * * *"  // Change from 02:00 to 04:00
}
```

Then restart scheduler.

---

## Scaling Considerations

### Multiple APScheduler Instances

For high-availability, deploy multiple instances with distributed locking:

```python
# Use PostgreSQL-backed scheduler store
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql://...')
}

scheduler = BackgroundScheduler(jobstores=jobstores)
```

### Resource Limits

Expected resource usage per job:

| Job | CPU | Memory | Disk I/O |
|-----|-----|--------|----------|
| rag-reindex | 10% | 200MB | High |
| agent-memory-purge | 5% | 100MB | High |
| feedback-loop | 15% | 300MB | Medium |
| health-check | 5% | 50MB | Low |

---

## Support

For issues:

1. Check `/tmp/apscheduler.log`
2. Run: `python scripts/apscheduler_setup.py --test-job <job-id>`
3. Review: `APSCHEDULER_IMPLEMENTATION.md`
4. Contact: DevOps team

---

**Version:** v5.0  
**Last Updated:** 2026-07-25
