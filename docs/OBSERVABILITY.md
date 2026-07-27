# Manta Maestro Production Observability Guide

Complete guide to monitoring, logging, tracing, and alerting for the Manta Maestro platform.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Accessing the Observability Stack](#accessing-the-observability-stack)
4. [Key Dashboards](#key-dashboards)
5. [Alert Configuration](#alert-configuration)
6. [SLO Definitions](#slo-definitions)
7. [Troubleshooting](#troubleshooting)
8. [Integration Setup](#integration-setup)
9. [Best Practices](#best-practices)

---

## Quick Start

### Start the Monitoring Stack

```bash
# Set required environment variables
export ENVIRONMENT=production
export POSTGRES_USER=manta
export POSTGRES_PASSWORD=<secure-password>
export GRAFANA_PASSWORD=<secure-admin-password>
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
export PAGERDUTY_SERVICE_KEY=<your-pagerduty-key>

# Start all services
docker-compose -f docker-compose-monitoring.yml up -d

# Verify services are healthy
docker-compose -f docker-compose-monitoring.yml ps
```

### Access the Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / `$GRAFANA_PASSWORD` |
| Prometheus | http://localhost:9090 | None (internal) |
| AlertManager | http://localhost:9093 | None (internal) |
| Jaeger UI | http://localhost:16686 | None |
| API Health | http://localhost:8000/health | None |
| API Metrics | http://localhost:8000/metrics | None |

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│           Manta Maestro Backend (FastAPI)           │
│  ┌──────────────────────────────────────────────┐  │
│  │  OpenTelemetry Instrumentation              │  │
│  │  - Structured JSON Logging                  │  │
│  │  - Distributed Tracing (OTLP)              │  │
│  │  - Prometheus Metrics (/metrics endpoint)  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         │                    │                   │
         ├──► Jaeger         ├──► Prometheus     └──► Logs/Files
         │   (Tracing)        │   (Metrics)
         │                    │
         └────────┬───────────┘
                  │
         ┌────────▼──────────┐
         │  AlertManager     │  ◄─── Alert Rules
         │  (Routing)        │
         └────────┬──────────┘
                  │
    ┌─────────────┼──────────────┐
    │             │              │
    ▼             ▼              ▼
  Slack        PagerDuty       Email
(#alerts)     (on-call)      (digest)
```

### Data Flow

1. **Instrumentation** (manta-backend/instrumentation.py)
   - FastAPI middleware captures HTTP requests
   - OpenTelemetry auto-instrumentation for libraries
   - Structured JSON logs with trace context
   - Custom metrics for routing & model performance

2. **Collection**
   - Prometheus scrapes /metrics endpoint every 10s
   - PostgreSQL exporter collects DB metrics
   - Node exporter collects system metrics
   - Jaeger collects distributed traces via OTLP

3. **Storage**
   - Prometheus: 30-day retention in `/prometheus`
   - Grafana: dashboard configurations
   - Jaeger: in-memory trace storage (configurable)

4. **Visualization**
   - Grafana dashboards query Prometheus
   - Jaeger UI for distributed trace inspection
   - Prometheus UI for metric exploration

5. **Alerting**
   - Prometheus evaluates alert rules every 30s
   - AlertManager deduplicates and routes to Slack/PagerDuty
   - Slack for warnings, PagerDuty for critical alerts

---

## Accessing the Observability Stack

### Grafana Access

**First Login (IMPORTANT: Change Password)**

1. Navigate to http://localhost:3000
2. Login with admin / `$GRAFANA_PASSWORD`
3. **Change admin password immediately**:
   - Click admin icon (top right)
   - Select "Change Password"
   - Use a strong, unique password

**Organization & Team Setup**

```
Settings → Preferences → Set default organization
Settings → Teams → Create team "Platform Engineering"
Settings → Users → Add team members
```

### Prometheus Access

Access the Prometheus UI at http://localhost:9090/graph

**Key Query Examples:**

```promql
# Current request latency (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Routing accuracy by agent
routing_accuracy

# Error rate (%)
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Database connection pool utilization
database_connection_pool_size{status="active"} / 50

# CPU usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Jaeger Tracing

Access the Jaeger UI at http://localhost:16686

**Navigate traces:**

1. Select "manta-maestro-api" from Service dropdown
2. Filter by operation or tags
3. Click trace to see span waterfall
4. Hover over spans to see attributes

**Key attributes in traces:**

- `http.method`: GET, POST, etc.
- `http.status_code`: HTTP response code
- `manta.agent`: Routing agent (maestro, infrastructure, claims, etc.)
- `user.id`: Authenticated user
- `trace_id` / `span_id`: Unique identifiers

---

## Key Dashboards

### 1. API Health Dashboard

**Panels:**

| Panel | Metric | Alert Threshold |
|-------|--------|-----------------|
| Request Latency (p50/p95/p99) | `histogram_quantile(...)` | p95 > 5s |
| Request Rate | `sum(rate(http_requests_total[1m]))` by endpoint | — |
| Error Rate | `sum(rate(http_requests_total{status=~"5.."}[5m]))` | > 5% |
| Status Codes | `http_requests_total` by status | — |

**How to interpret:**

- **p95 Latency > 5s**: Indicates degraded performance; check load, database, or model latency
- **Error Rate > 5%**: Check logs for stack traces; may indicate service dependency failure
- **Error Spike**: Sudden increase; usually transient; escalate if sustained

---

### 2. Routing Accuracy Dashboard

**Panels:**

| Panel | Metric | Target | Alert |
|-------|--------|--------|-------|
| Accuracy by Agent | `routing_accuracy` | > 90% | < 90% |
| Routing Decisions | `routing_decisions_total` | — | — |
| Mispredictions | `routing_decisions_total{decision="incorrect"}` | < 10% | — |

**How to interpret:**

- **Accuracy < 90%**: Check agent model for degradation
  - Retrain agent model if accuracy has drifted
  - Check for recent input distribution changes
  - Review mispredicted examples in logs

- **Specific agent low**: May indicate:
  - Model performance regression
  - Change in input domain (new client, new agent type)
  - Feature preprocessing issue

**Action:** When accuracy drops below 90%, investigate most recent mispredictions using:

```bash
# Find mispredictions in logs
grep 'decision="incorrect"' logs/manta-maestro.log | tail -20
```

---

### 3. Model Inference Dashboard

**Panels:**

| Panel | Metric | P95 Threshold | P99 Threshold |
|-------|--------|---------------|---------------|
| Inference Latency | `model_inference_duration_seconds` | 5s | 10s |
| Tokens Used | `model_tokens_total` | — | — |
| Cache Hit Rate | `cache_hits_total / (hits + misses)` | > 80% | — |

**How to interpret:**

- **Latency p95 > 5s**: Model is slow; may indicate:
  - High token count (check prompt length)
  - Overloaded model server
  - Network/IO delays
  - Model complexity growth

- **Cache Hit Rate < 80%**: Consider:
  - Increasing cache size
  - Adjusting cache TTL
  - Analyzing cache key patterns

---

### 4. Database Performance Dashboard

**Panels:**

| Panel | Metric | Alert Threshold |
|-------|--------|-----------------|
| Query Latency (p95) | `database_query_duration_seconds` | > 1s |
| Connection Pool | `database_connection_pool_size` | > 40/50 active |
| Slow Queries | `pg_stat_statements_mean_time` | > 1000ms |

**How to interpret:**

- **Query Latency p95 > 1s**: Likely cause:
  - Missing indexes (check query plans)
  - N+1 queries (enable query logging)
  - Table bloat (run VACUUM)
  - Concurrent lock contention

- **Connection Pool Near Exhaustion**: 
  - Check for long-running transactions
  - Verify connection cleanup in app code
  - Consider increasing pool size if legitimate growth

**Action: Debug Slow Queries**

```sql
-- Connect to PostgreSQL
psql postgresql://manta:password@localhost/manta

-- Top slow queries
SELECT mean_time, calls, query 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Connection count
SELECT datname, count(*) 
FROM pg_stat_activity 
GROUP BY datname;
```

---

### 5. System Infrastructure Dashboard

**Panels:**

| Panel | Metric | Warning | Critical |
|-------|--------|---------|----------|
| CPU Usage | `100 - avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100` | 85% | 95% |
| Memory Usage | `(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)` | 85% | 95% |
| Disk Space | `node_filesystem_avail_bytes / node_filesystem_size_bytes` | 15% | 5% |
| Network I/O | `rate(node_network_transmit_bytes_total[5m])` | — | — |

---

## Alert Configuration

### Alert Severity Levels

| Severity | Response Time | Escalation | Channel |
|----------|---------------|-----------|---------|
| Critical | < 5 minutes | Page on-call | PagerDuty + Slack |
| Warning | < 30 minutes | Slack notification | #engineering-alerts |
| Info | < 1 hour | No escalation | #general |

### Alert Rules Location

```
monitoring/alert-rules.yaml
```

**Key Alerts:**

#### 1. High API Latency (Critical)

```yaml
HighAPILatencyP95:
  expr: histogram_quantile(0.95, ...) > 5s
  for: 5m
  threshold: 5 seconds
  why: SLO target is p95 < 5s
  action: Investigate model latency, DB queries, or load balancer issues
```

**Debugging Steps:**

1. Check Jaeger for slow traces
2. Query Prometheus for slow databases:
   ```promql
   database_query_duration_seconds{quantile="0.95"}
   ```
3. Check model latency:
   ```promql
   model_inference_duration_seconds{quantile="0.95"}
   ```
4. If sustained, check logs for errors:
   ```bash
   tail -100 logs/manta-maestro.log | grep ERROR
   ```

#### 2. Low Routing Accuracy (Warning)

```yaml
LowRoutingAccuracy:
  expr: routing_accuracy < 0.90
  for: 10m
  threshold: 90%
  why: Target accuracy is 90% for production
  action: Inspect mispredictions, retrain if needed
```

**Debugging Steps:**

1. Check affected agent in dashboard
2. Export recent mispredictions:
   ```bash
   grep 'agent="x-agent" decision="incorrect"' logs/manta-maestro.log > mispredictions.jsonl
   ```
3. Analyze patterns:
   - Which input types fail most?
   - Did distribution change recently?
   - Check agent model version

#### 3. Database Connection Pool Exhaustion (Critical)

```yaml
DatabaseConnectionPoolExhausted:
  expr: active_connections / total > 0.90
  for: 5m
  threshold: 90% utilization
  why: Indicates connection leak or overload
  action: Restart service, check for stuck connections
```

**Debugging Steps:**

1. Check active connections:
   ```bash
   psql -h localhost -U manta manta -c \
     "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
   ```
2. Kill idle transactions:
   ```sql
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'idle' AND state_change < now() - interval '1 hour';
   ```
3. Check app logs for unclosed connections

#### 4. High Error Rate (Critical)

```yaml
HighErrorRate:
  expr: 5xx_errors / total_requests > 0.05
  for: 5m
  threshold: 5% error rate
  why: Indicates service degradation
  action: Check logs, restart service if needed
```

---

## SLO Definitions

### Service Level Objectives

**Availability SLO: 99.9%** (43 minutes downtime/month)

```promql
# Monthly availability
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
>= 0.999
```

**Latency SLO: p95 < 5s** (for 95% of requests)

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[30d]))
< 5
```

**Routing Accuracy SLO: > 90%**

```promql
(correct_routings / total_routings)
>= 0.90
```

**Error Budget** (for 30-day period)

- Total requests: 2,592,000 (30 requests/sec avg)
- Budget: 2,592 errors (0.1%)
- Current consumption: Check dashboard "SLO Burn Rate"

---

## Troubleshooting

### Common Issues & Solutions

#### 1. High API Latency

**Symptoms:** p95 latency > 5s, requests slow

**Diagnosis:**

1. Check if it's a specific endpoint:
   ```promql
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) by (endpoint)
   ```

2. Check if database is slow:
   ```promql
   database_query_duration_seconds{quantile="0.95"}
   ```

3. Check if model is slow:
   ```promql
   model_inference_duration_seconds{quantile="0.95"}
   ```

**Solutions:**

- **Endpoint slow:** Optimize code, add caching
- **DB slow:** Add indexes, run ANALYZE, kill slow queries
- **Model slow:** Reduce prompt size, batch requests, increase GPU allocation

#### 2. Low Routing Accuracy

**Symptoms:** `routing_accuracy < 0.90`, mispredictions increasing

**Diagnosis:**

1. Check if accuracy dropped suddenly or gradually
2. Identify which agents are affected
3. Export recent mispredictions

**Solutions:**

- **Recent drop:** Check for input distribution change (new client, API change)
- **Gradual drift:** Retrain model with fresh data
- **Specific agent:** Review agent model, check for feature changes

#### 3. Database Connection Pool Exhausted

**Symptoms:** Connections > 45/50, requests start timing out

**Diagnosis:**

```sql
-- Check connections by state
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Check connection age
SELECT pid, datname, state, query_start, backend_start
FROM pg_stat_activity 
WHERE state != 'active'
ORDER BY backend_start DESC;
```

**Solutions:**

- **Idle connections:** Reduce `pool_recycle` timeout in SQLAlchemy config
- **Stuck transactions:** Increase transaction timeout, add deadlock handling
- **Legitimate growth:** Increase pool size in docker-compose config

#### 4. Out of Disk Space

**Symptoms:** Alerts for < 5% disk available

**Diagnosis:**

```bash
df -h                                # Check disk usage
du -sh logs/                         # Check log size
du -sh /prometheus/wal               # Check Prometheus WAL
```

**Solutions:**

- **Logs filling disk:** Rotate and archive logs
  ```bash
  docker exec manta-api logrotate /etc/logrotate.d/manta
  ```
- **Prometheus WAL:** Reduce retention or increase disk
  ```yaml
  # In prometheus.yaml
  --storage.tsdb.retention.time=15d  # Reduce from 30d
  ```

#### 5. Service Crashed/Restarting

**Diagnosis:**

```bash
# Check container logs
docker logs manta-api --tail 50

# Check restart count
docker inspect manta-api | grep -A 5 RestartCount
```

**Common causes:**

- Out of memory: Increase container memory limit
- Database unavailable: Check postgres container status
- Invalid environment variables: Verify .env file

---

## Integration Setup

### Slack Integration

**1. Create Slack Webhook**

1. Go to https://api.slack.com/apps
2. Create new app → "From scratch"
3. Name: "Manta Maestro Alerts"
4. Incoming Webhooks → "Add New Webhook to Workspace"
5. Select channel: #alerts
6. Copy webhook URL

**2. Configure AlertManager**

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
docker-compose -f docker-compose-monitoring.yml up -d alertmanager
```

**3. Test Webhook**

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert from Manta"}' \
  $SLACK_WEBHOOK_URL
```

### PagerDuty Integration

**1. Create PagerDuty Service**

1. Go to PagerDuty dashboard
2. Services → New Service
3. Name: "Manta Maestro"
4. Escalation Policy: "Default"
5. Add Integration: Prometheus
6. Copy integration key

**2. Configure AlertManager**

```bash
export PAGERDUTY_SERVICE_KEY="<your-integration-key>"
docker-compose -f docker-compose-monitoring.yml up -d alertmanager
```

**3. Test Alert**

In AlertManager UI (http://localhost:9093), manually fire a test alert to verify routing.

---

## Best Practices

### 1. Metric Naming Conventions

```
# Follow Prometheus conventions
<namespace>_<subsystem>_<name>_<unit>

Examples:
- http_request_duration_seconds
- model_inference_duration_seconds
- database_connection_pool_size
- routing_accuracy
```

### 2. Alert Tuning

**When to adjust thresholds:**

- **p95 latency threshold:** Increase only if legitimate business reason (e.g., batch jobs)
- **Accuracy threshold:** Never decrease; instead, investigate root cause
- **Error rate threshold:** Should be < 1% normally; 5% indicates serious issue

**Golden signals to monitor:**

1. **Latency** (p50, p95, p99)
2. **Traffic** (requests/sec, throughput)
3. **Errors** (error rate, error budget burn)
4. **Saturation** (resource usage, queue depth)

### 3. Cardinality Management

⚠️ **High-cardinality metrics cause storage explosion!**

Avoid using as metric labels:
- ❌ Request IDs
- ❌ Trace IDs
- ❌ User IDs (except in trace context)
- ❌ Token counts
- ✅ Agent names (fixed set)
- ✅ HTTP methods (GET, POST, etc.)
- ✅ Endpoints
- ✅ Status codes

### 4. Log Retention

**Retention policy:**

- **Application logs:** 30 days (compressed after 7 days)
- **Prometheus metrics:** 30 days
- **Jaeger traces:** 7 days (in-memory; adjust via `MEMORY_MAX_TRACES`)

```bash
# Archive old logs
tar czf logs-2026-07-$(date +%d).tar.gz logs/manta-maestro.log.*
rm logs/manta-maestro.log.*
```

### 5. On-Call Runbook Template

When creating alerts, always include a runbook URL:

```yaml
annotations:
  summary: "Brief description"
  description: "Detailed description with context"
  runbook_url: "https://wiki.manta.local/runbooks/alert-name"
```

**Runbook contents:**

1. **What is this alert?** (description)
2. **Why did it trigger?** (common causes)
3. **How to diagnose?** (step-by-step)
4. **How to fix?** (remediation steps)
5. **Who to escalate to?** (team, on-call)

---

## Metrics Export & Reporting

### Generate SLO Report

```bash
# Query Prometheus for availability
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=avg(http_requests_total{status!~"5.."}[30d]) / avg(http_requests_total[30d])' \
  | jq '.data.result[0].value[1]'
```

### Grafana Report Export

1. Open dashboard
2. Share → Export as PDF
3. Schedule via Grafana alerts (premium feature)

---

## Disaster Recovery

### Prometheus Data Recovery

If Prometheus data corrupts:

```bash
# Stop Prometheus
docker-compose -f docker-compose-monitoring.yml stop prometheus

# Backup current data
cp -r prometheus_data prometheus_data.backup

# Rebuild TSDB
docker-compose -f docker-compose-monitoring.yml run prometheus \
  --storage.tsdb.path=/prometheus \
  --storage.tsdb.retention.time=30d

# Restart
docker-compose -f docker-compose-monitoring.yml up -d prometheus
```

### Grafana Dashboard Recovery

Dashboards are version-controlled in `grafana-dashboard.json`:

```bash
# Restore from source
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana-dashboard.json
```

---

## Contacts & Escalation

| Role | Contact | Page Criteria |
|------|---------|---------------|
| On-Call Engineer | #on-call in Slack | Critical alerts (p95 > 5s, errors > 5%) |
| Database Admin | <dba@manta.local> | DB connection pool exhausted |
| Platform Team | <platform@manta.local> | Infrastructure alerts (CPU, disk, memory) |
| Escalation Manager | <escalation@manta.local> | Multiple simultaneous critical alerts |

---

**Last Updated:** 2026-07-26  
**Owner:** Platform Engineering  
**Version:** 1.0.0
