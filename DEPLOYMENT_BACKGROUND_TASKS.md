# Maestro APScheduler v5.0 — Deployment Guide

**Background Tasks Orchestration for Manta Associados**

**Version:** 5.0  
**Updated:** 2026-07-25  
**Maintainer:** mneves@mantaassociados.com  
**Status:** Production-ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pre-Deployment](#pre-deployment)
4. [Installation](#installation)
   - [Linux Systemd](#linux-systemd)
   - [Docker Compose](#docker-compose)
   - [Kubernetes (Advanced)](#kubernetes-advanced)
5. [Configuration](#configuration)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [Rollback](#rollback)

---

## Overview

**Maestro APScheduler** is a production-grade background task orchestrator for Manta Associados' v5.0 agent architecture. It manages four critical jobs:

| Job | Schedule | Purpose | Timeout |
|-----|----------|---------|---------|
| **RAG Reindex** | Daily 02:00 UTC | Refresh embeddings, validate collections | 10 min |
| **Agent Memory Purge** | Daily 03:00 UTC | Clean agent state, archive old runs | 5 min |
| **Embedding Retrain** | Weekly Sun 03:00 UTC | Fine-tune reranker model | 30 min |
| **Tiering Audit** | Daily 04:00 UTC | Validate model selection rules | 5 min |

**Key Features:**
- Prometheus metrics export (port 8080)
- Slack alerts on job failures
- Automatic retry logic (configurable)
- Health check endpoint (`/health`, `/metrics`)
- Docker & Systemd support
- Zero-downtime deployment
- Comprehensive logging & audit trails

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│ Maestro APScheduler (Python 3.11)                           │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐    │
│ │ APScheduler Core (background thread)                 │    │
│ │  - CronTrigger: 02:00, 03:00, 04:00, weekly         │    │
│ │  - Coalesce: Skip missed jobs if behind             │    │
│ │  - Max instances: 1 (no concurrent runs)            │    │
│ └──────────────────────────────────────────────────────┘    │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ Job Runners (subprocess wrappers)                    │    │
│ │  - rag-reindex.py                                    │    │
│ │  - agent_memory_purge.py                             │    │
│ │  - eval_embeddings_ab.py                             │    │
│ │  - tiering-audit.py                                  │    │
│ └──────────────────────────────────────────────────────┘    │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ Prometheus Metrics Export (port 8080)                │    │
│ │  - maestro_job_count (gauge)                         │    │
│ │  - maestro_job_success_total (counter)               │    │
│ │  - maestro_job_failure_total (counter)               │    │
│ │  - maestro_job_duration_ms (histogram)               │    │
│ │  - maestro_last_job_duration_ms (gauge)              │    │
│ └──────────────────────────────────────────────────────┘    │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ Health Endpoint (Flask)                              │    │
│ │  - GET /health → JSON status                         │    │
│ │  - GET /metrics → Prometheus format                  │    │
│ └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓
    [PostgreSQL]  [Prometheus]  [AlertManager]
      (state)       (9090)        (Slack hooks)
```

### Deployment Options

| Option | Best For | Complexity | HA Support |
|--------|----------|-----------|-----------|
| **Systemd** | Single VM, production | Low | No (requires HAProxy/keepalived) |
| **Docker Compose** | Dev, staging, small prod | Medium | No |
| **Kubernetes** | Multi-region, high-scale | High | Yes (StatefulSet + CronJob) |

---

## Pre-Deployment

### Requirements

**System:**
- Linux (Ubuntu 20.04+, RHEL 8+, or equivalent)
- Python 3.11+
- 512 MB RAM minimum, 1 GB recommended
- 10 GB disk (logs + cache)
- Network access to: PostgreSQL, Slack, Docker Hub (if containerized)

**Credentials Required:**
```bash
# .env file (do NOT commit)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DATABASE_URL=postgresql://user:password@localhost:5432/maestro_v5
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_access_token
```

**Repository Structure:**
```
Codex-exemplo/
├── scripts/
│   ├── apscheduler_setup.py          # Main orchestrator
│   ├── rag-reindex.py
│   ├── agent_memory_purge.py
│   ├── eval_embeddings_ab.py
│   └── tiering-audit.py
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── maestro-apscheduler.service
│   └── docker/
│       ├── prometheus-maestro.yml
│       ├── alertmanager-maestro.yml
│       └── init-db.sql
├── .claude/
│   ├── agents/                       # Skill files
│   ├── rag/                          # RAG collections
│   └── settings.json
├── VERSIONS.json                     # Skill checksums
└── CLAUDE.md                         # v5.0 spec
```

### Pre-Flight Checks

```bash
# 1. Validate Python version
python3 --version  # Should be 3.11+

# 2. Check required dependencies
pip list | grep -E "schedule|requests|prometheus-client"

# 3. Validate VERSIONS.json
python3 scripts/healthcheck.py

# 4. Test CLAUDE.md (v5.0 sections present)
grep -E "v5.0|R1|R6|R7|R8|R9|R10" CLAUDE.md

# 5. Validate scheduler config (dry-run)
python3 -c "from pathlib import Path; from scripts.apscheduler_setup import MaestroScheduler; s = MaestroScheduler(Path.cwd()); print(f'Jobs: {list(s.jobs.keys())}')"
```

---

## Installation

### Option 1: Linux Systemd (Single Server)

#### 1.1 Create maestro user & directories

```bash
# As root
useradd -r -s /bin/bash -d /opt/maestro maestro

mkdir -p /opt/maestro
mkdir -p /var/log/maestro
mkdir -p /etc/maestro

# Copy application files
cp -r Codex-exemplo/* /opt/maestro/

# Set permissions
chown -R maestro:maestro /opt/maestro /var/log/maestro /etc/maestro
chmod 755 /opt/maestro
chmod 755 /var/log/maestro
chmod 644 /opt/maestro/scripts/*.py
chmod 755 /opt/maestro/scripts/apscheduler_setup.py
```

#### 1.2 Install Python dependencies

```bash
# As maestro user
cd /opt/maestro
pip3 install --user --upgrade pip
pip3 install --user -r requirements.txt
```

**requirements.txt:**
```
schedule==1.2.0
requests==2.31.0
prometheus-client==0.19.0
python-dotenv==1.0.0
pydantic==2.5.0
psycopg2-binary==2.9.9
```

#### 1.3 Create .env file (secrets)

```bash
sudo tee /etc/maestro/.env > /dev/null <<EOF
PYTHONUNBUFFERED=1
MAESTRO_ENV=production
MAESTRO_LOG_LEVEL=INFO
DATABASE_URL=postgresql://maestro:${DB_PASSWORD}@localhost:5432/maestro_v5
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK}
EOF

sudo chmod 600 /etc/maestro/.env
sudo chown maestro:maestro /etc/maestro/.env
```

#### 1.4 Install systemd service

```bash
# As root
cp deploy/maestro-apscheduler.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable maestro-apscheduler
systemctl start maestro-apscheduler

# Verify
systemctl status maestro-apscheduler
journalctl -u maestro-apscheduler -n 50 -f  # Follow logs
```

#### 1.5 Validate health

```bash
# Check service is running
systemctl is-active maestro-apscheduler  # Should output 'active'

# Test health endpoint (local port forwarding if needed)
curl http://localhost:8080/health | jq .

# Check metrics
curl http://localhost:8080/metrics | grep maestro_job_count
```

---

### Option 2: Docker Compose (Dev/Staging)

#### 2.1 Build Docker image

```bash
cd Codex-exemplo

# Build locally
docker build -f deploy/Dockerfile -t maestro-scheduler:latest .

# Or push to Docker Hub
docker build -f deploy/Dockerfile -t ${DOCKER_USERNAME}/maestro-scheduler:v5.0 .
docker push ${DOCKER_USERNAME}/maestro-scheduler:v5.0
```

#### 2.2 Create docker-compose environment

```bash
# Copy files
cp deploy/docker-compose.yml /path/to/deployment/
cp -r deploy/docker /path/to/deployment/

# Create .env in deployment directory
cat > .env <<EOF
COMPOSE_PROJECT_NAME=maestro
POSTGRES_USER=maestro
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://maestro:secure_password_here@postgres:5432/maestro_v5
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
GRAFANA_PASSWORD=grafana_secure_password
EOF

chmod 600 .env
```

#### 2.3 Start services

```bash
# Start all services
docker-compose up -d

# Verify all services are healthy
docker-compose ps

# Follow logs
docker-compose logs -f maestro-scheduler

# Check health endpoint
curl http://localhost:8080/health | jq .
```

#### 2.4 Access services

| Service | URL | Credentials |
|---------|-----|-------------|
| Maestro Health | http://localhost:8080/health | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / (from .env) |
| AlertManager | http://localhost:9093 | — |

---

### Option 3: Kubernetes (Advanced)

#### 3.1 Create StatefulSet manifest

```yaml
# manifests/maestro-scheduler-statefulset.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: maestro-scheduler-config
  namespace: maestro
data:
  scheduler-config.json: |
    {
      "enabled": true,
      "timezone": "UTC",
      "jobs": [
        {
          "id": "rag-reindex",
          "name": "RAG Reindex",
          "enabled": true,
          "cron": "0 2 * * *"
        }
      ]
    }

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: maestro-scheduler
  namespace: maestro
spec:
  serviceName: maestro-scheduler
  replicas: 1
  selector:
    matchLabels:
      app: maestro-scheduler
  template:
    metadata:
      labels:
        app: maestro-scheduler
    spec:
      serviceAccountName: maestro-scheduler
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: scheduler
        image: docker.io/mantaassociados/maestro-scheduler:v5.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: metrics
          containerPort: 8080
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: database-url
        - name: SLACK_WEBHOOK_URL
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: slack-webhook
        - name: MAESTRO_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
        volumeMounts:
        - name: config
          mountPath: /opt/maestro/.claude
          readOnly: true
        - name: logs
          mountPath: /var/log/maestro
      volumes:
      - name: config
        configMap:
          name: maestro-scheduler-config
      - name: logs
        emptyDir: {}
  volumeClaimTemplates:
  - metadata:
      name: logs
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi

---
apiVersion: v1
kind: Service
metadata:
  name: maestro-scheduler
  namespace: maestro
spec:
  clusterIP: None  # Headless service for StatefulSet
  selector:
    app: maestro-scheduler
  ports:
  - name: metrics
    port: 8080
    targetPort: 8080

---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: maestro-scheduler
  namespace: maestro
spec:
  selector:
    matchLabels:
      app: maestro-scheduler
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### 3.2 Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace maestro

# Create secrets
kubectl create secret generic maestro-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=slack-webhook=$SLACK_WEBHOOK_URL \
  -n maestro

# Apply manifests
kubectl apply -f manifests/maestro-scheduler-statefulset.yaml

# Verify
kubectl get pods -n maestro
kubectl logs maestro-scheduler-0 -n maestro -f
```

---

## Configuration

### Scheduler Config File

Location: `.claude/scheduler-config.json`

```json
{
  "enabled": true,
  "timezone": "UTC",
  "jobs": [
    {
      "id": "rag-reindex",
      "name": "RAG Reindex (R6)",
      "enabled": true,
      "trigger": "cron",
      "cron": "02:00",
      "timeout_seconds": 600,
      "retry_count": 1
    },
    {
      "id": "agent-memory-purge",
      "name": "Agent Memory Purge (R10)",
      "enabled": true,
      "trigger": "cron",
      "cron": "03:00",
      "timeout_seconds": 300,
      "retry_count": 1
    },
    {
      "id": "embedding-retrain",
      "name": "Embedding Retrain (R9)",
      "enabled": true,
      "trigger": "cron",
      "cron": "weekly:0:03:00",
      "timeout_seconds": 1800,
      "retry_count": 2
    },
    {
      "id": "tiering-audit",
      "name": "Tiering Audit (R7)",
      "enabled": true,
      "trigger": "cron",
      "cron": "04:00",
      "timeout_seconds": 300,
      "retry_count": 1
    }
  ]
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAESTRO_ENV` | production | Environment (dev/staging/production) |
| `MAESTRO_LOG_LEVEL` | INFO | Log level (DEBUG/INFO/WARNING/ERROR) |
| `DATABASE_URL` | — | PostgreSQL connection string |
| `SLACK_WEBHOOK_URL` | — | Slack webhook for alerts |
| `PYTHONUNBUFFERED` | 1 | Disable Python output buffering |

---

## Monitoring & Alerts

### Prometheus Metrics

**Scheduler-specific metrics:**

```prometheus
# Gauge: Total scheduled jobs
maestro_job_count{} 4

# Counter: Successful job executions
maestro_job_success_total{job_name="rag-reindex"} 128
maestro_job_success_total{job_name="agent-memory-purge"} 256

# Counter: Failed job executions
maestro_job_failure_total{job_name="rag-reindex"} 2

# Histogram: Job execution duration (milliseconds)
maestro_job_duration_ms_bucket{job_name="rag-reindex",le="100"} 0
maestro_job_duration_ms_bucket{job_name="rag-reindex",le="500"} 45
maestro_job_duration_ms_bucket{job_name="rag-reindex",le="1000"} 120
maestro_job_duration_ms_bucket{job_name="rag-reindex",le="5000"} 128

# Gauge: Last job execution duration
maestro_last_job_duration_ms{job_name="rag-reindex"} 3427
```

### Alert Rules

File: `deploy/docker/prometheus-alert-rules.yml`

```yaml
groups:
- name: maestro_scheduler
  interval: 30s
  rules:
  - alert: MaestroJobFailure
    expr: increase(maestro_job_failure_total[5m]) > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Job {{ $labels.job_name }} failed"
      description: "{{ $value }} failures in last 5 minutes"

  - alert: MaestroJobTimeout
    expr: maestro_last_job_duration_ms{job_name="rag-reindex"} > 600000
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "RAG Reindex timeout detected"

  - alert: MaestroSchedulerDown
    expr: up{job="maestro-scheduler"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Maestro scheduler is down"
```

### Slack Alerts

Configure AlertManager to send failures to Slack:

```bash
# In .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Channels (in alertmanager-maestro.yml)
#maestro-alerts - warnings and info
#maestro-critical - critical issues
#maestro-jobs - job failures
```

Example alert:
```
[CRITICAL] Job Failure: rag-reindex
Collection: san:v5.0:chunks
Error: Database connection timeout
Last run: 2026-07-25T02:15:00Z
```

---

## Testing & Validation

### Unit Tests

```bash
# Test scheduler initialization
python3 -c "
from pathlib import Path
from scripts.apscheduler_setup import MaestroScheduler

scheduler = MaestroScheduler(Path.cwd())
assert len(scheduler.jobs) == 4, 'Should have 4 jobs'
print('✓ Scheduler initialized')
"

# Test health endpoint (in background)
python3 scripts/apscheduler_setup.py &
sleep 3
curl http://localhost:8080/health | jq .
pkill -f apscheduler_setup.py
```

### Integration Tests

```bash
# 1. Test RAG reindex job
python3 scripts/rag-reindex.py

# 2. Test agent memory purge
python3 scripts/agent_memory_purge.py

# 3. Test tiering audit
python3 scripts/tiering-audit.py

# 4. Check logs
tail -50 /var/log/maestro/maestro-apscheduler.log
```

### Smoke Tests

```bash
#!/bin/bash
# tests/smoke-test.sh

echo "Testing Maestro APScheduler..."

# 1. Health endpoint
echo "1. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8080/health)
if echo "$HEALTH" | jq . > /dev/null 2>&1; then
  echo "✓ Health endpoint OK"
else
  echo "✗ Health endpoint failed"
  exit 1
fi

# 2. Metrics endpoint
echo "2. Testing metrics endpoint..."
METRICS=$(curl -s http://localhost:8080/metrics | grep maestro_job_count)
if [ -n "$METRICS" ]; then
  echo "✓ Metrics endpoint OK"
  echo "  $METRICS"
else
  echo "✗ Metrics endpoint failed"
  exit 1
fi

# 3. Job counts
echo "3. Checking scheduled jobs..."
JOBS=$(echo "$HEALTH" | jq '.jobs | length')
if [ "$JOBS" -eq 4 ]; then
  echo "✓ All 4 jobs scheduled"
else
  echo "⚠ Expected 4 jobs, got $JOBS"
fi

echo "✓ All smoke tests passed"
```

---

## Troubleshooting

### Service won't start

**Symptom:** `systemctl start maestro-apscheduler` fails

**Solution:**
```bash
# 1. Check logs
journalctl -u maestro-apscheduler -n 100

# 2. Verify Python dependencies
pip3 list | grep -E "schedule|prometheus|requests"

# 3. Check file permissions
ls -la /opt/maestro/scripts/apscheduler_setup.py

# 4. Test manually
cd /opt/maestro
python3 scripts/apscheduler_setup.py --test-config
```

### Jobs not running on schedule

**Symptom:** Jobs marked "success" but no actual work done

**Solution:**
```bash
# 1. Check scheduler is actually running
ps aux | grep apscheduler_setup

# 2. Verify cron expressions
python3 -c "
import json
from pathlib import Path
config = json.load(open('.claude/scheduler-config.json'))
for job in config['jobs']:
  print(f'{job[\"id\"]}: {job[\"cron\"]}')
"

# 3. Check job script permissions
chmod +x scripts/rag-reindex.py
chmod +x scripts/agent_memory_purge.py

# 4. Test job manually
python3 scripts/rag-reindex.py --dry-run
```

### High memory usage

**Symptom:** `maestro-scheduler` using > 512 MB RAM

**Solution:**
```bash
# 1. Check memory metrics
curl http://localhost:8080/metrics | grep maestro_agent_memory_mb

# 2. Reduce job concurrency
# In .claude/scheduler-config.json, add:
"max_concurrent_jobs": 1

# 3. Increase memory limit (systemd)
# Edit /etc/systemd/system/maestro-apscheduler.service
MemoryLimit=1024M

# 4. Restart
systemctl daemon-reload
systemctl restart maestro-apscheduler
```

### Database connection errors

**Symptom:** `ERROR: could not connect to server` in logs

**Solution:**
```bash
# 1. Check DATABASE_URL
echo $DATABASE_URL

# 2. Test connection
psql $DATABASE_URL -c "SELECT 1"

# 3. Verify credentials
grep DATABASE_URL /etc/maestro/.env

# 4. Check PostgreSQL is running
systemctl status postgresql
```

### Prometheus alerts not firing

**Symptom:** AlertManager not receiving alerts

**Solution:**
```bash
# 1. Verify Prometheus config
curl http://localhost:9090/api/v1/rules | jq .

# 2. Check AlertManager connectivity
curl http://localhost:9090/api/v1/alerts

# 3. Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL

# 4. Check AlertManager logs
docker logs maestro-alertmanager
```

---

## Rollback

### Systemd Rollback

```bash
# 1. Stop current service
systemctl stop maestro-apscheduler

# 2. Restore previous version
cp /opt/maestro/scripts/apscheduler_setup.py.bak /opt/maestro/scripts/apscheduler_setup.py

# 3. Restart
systemctl start maestro-apscheduler

# 4. Verify
systemctl status maestro-apscheduler
curl http://localhost:8080/health
```

### Docker Rollback

```bash
# 1. Stop current container
docker-compose down

# 2. Switch to previous image
sed -i 's/:v5.0/:v4.9/g' docker-compose.yml

# 3. Restart
docker-compose up -d

# 4. Verify
docker-compose ps
curl http://localhost:8080/health
```

### Kubernetes Rollback

```bash
# 1. Check rollout history
kubectl rollout history statefulset/maestro-scheduler -n maestro

# 2. Rollback to previous revision
kubectl rollout undo statefulset/maestro-scheduler -n maestro

# 3. Verify
kubectl rollout status statefulset/maestro-scheduler -n maestro
```

---

## Support & Contact

**Issues:** mneves@mantaassociados.com  
**Slack:** #maestro-ops  
**Documentation:** https://manta.wiki/maestro-v5  
**Source:** https://github.com/mantaassociados/Codex-exemplo

---

**Version History**

| Version | Date | Changes |
|---------|------|---------|
| 5.0 | 2026-07-25 | Initial release with Docker, systemd, Kubernetes support |
| 4.9 | 2026-07-05 | Pre-release, background task foundation |

---

**End of Deployment Guide**
