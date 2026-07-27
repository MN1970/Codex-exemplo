# SKILL.md — git-observability-stack

**Git Operations Observability Stack (OpenTelemetry)**

Version: **1.0.0** | Tier: **Sonnet** | Status: 🆕 **Fase 4** | Last updated: **2026-07-27**

MCPs: **Supabase (git_traces, git_metrics, git_logs), Alertmanager (alert_routes), Grafana (dashboard_api), GitHub (list_commits, pull_request_read)** | Output: **100% distributed traces + 50+ metrics + structured logs + 4 Grafana dashboards + 8 alert rules**

---

## Overview

**git-observability-stack** instruments Git Evolution Suite (Fase 3–4) with production-grade observability using **OpenTelemetry**. Provides 100% tracing of merge operations, 50+ Prometheus metrics, structured JSON logging, and anomaly detection via Isolation Forest + DBSCAN. Integrates Jaeger (distributed traces), ClickHouse (time-series metrics), Grafana (visualization), and Alertmanager (incident response).

**Core goal**: Transform black-box Git automation into fully observable, auditable, and resilient operations with sub-second anomaly detection and immutable compliance logs.

### Purpose

- **Trace every merge operation** — 100% sampling for audit trail (W3C TraceContext)
- **Monitor ML model health** — inference latency, confidence drift, false positive tracking
- **Track resource utilization** — CPU, memory, disk I/O, network per merge operation
- **Cost attribution** — per-repo, per-author, per-merge granularity
- **Detect anomalies** — latency spikes, model drift, SLO breaches in real-time
- **Incident response** — end-to-end trace correlation for post-mortem analysis
- **Compliance & audit** — immutable event log with context propagation (SOC 2 ready)

### Observability Pillars (3 Signal Types)

1. **Traces** — Distributed tracing of merge workflows (100% sampling, immutable)
2. **Metrics** — 50+ Prometheus metrics (latency, throughput, errors, cost, ML health)
3. **Logs** — Structured JSON logs with W3C TraceContext correlation

---

## When to Use

**Trigger 1: Operational visibility during Fase 4 rollout**  
"I need end-to-end tracing of ML-based merge decisions, including ML inference timing, feature importance, and post-merge CI outcomes."

**Trigger 2: Cost attribution for GitOps infrastructure**  
"Which repos and authors are driving compute costs? Show me per-merge breakdown and monthly trends."

**Trigger 3: Incident response and debugging**  
"A merge failed in production. Trace the entire operation (ML scoring → merge → CI → rollback) with all dependencies and resource consumption."

**Trigger 4: ML model health monitoring**  
"Is the ML model's accuracy drifting? Are inference latencies increasing? Alert me if confidence distribution changes significantly."

**Trigger 5: SLO compliance and capacity planning**  
"I need dashboards showing merge success rates, latency percentiles (p50/p95/p99), and false positive rates to meet SLAs."

---

## Architecture & Components

### 1. OpenTelemetry Instrumentation Stack

```
┌──────────────────────────────────────────────────────────────────┐
│ Git Evolution Suite (git-gitops-flow, git-multi-repo-workflows,  │
│ git-auto-merge-confidence, git-chaos-engineering)                │
├──────────────────────────────────────────────────────────────────┤
│                   OpenTelemetry SDK Layer                        │
│  ┌─ Tracing (auto-instrumentation + custom spans)               │
│  ├─ Metrics (in-memory aggregation + periodic export)            │
│  └─ Logging (structured JSON + context propagation)              │
├──────────────────────────────────────────────────────────────────┤
│              OTEL Collector (batch processor)                    │
│  ┌─ Trace exporter → Jaeger (gRPC, port 14250)                  │
│  ├─ Metrics exporter → ClickHouse (HTTP, port 8123)             │
│  └─ Logs exporter → Supabase PostgreSQL (OTLP protocol)         │
├──────────────────────────────────────────────────────────────────┤
│                  Backend Data Layer                              │
│  ┌─ Jaeger: distributed traces (24h retention, sampling audit)  │
│  ├─ ClickHouse: time-series metrics (90d retention, TTL)        │
│  ├─ Supabase: structured logs + audit trail + anomaly feedback  │
│  └─ Prometheus: metrics scrape target (via OTLP remoting)       │
├──────────────────────────────────────────────────────────────────┤
│              Observability & Response Layer                      │
│  ┌─ Grafana: 4 dashboards (Git Analytics, ML Health, Cost, Anom)
│  ├─ Alertmanager: 8 alert rules + escalation policies           │
│  ├─ Anomaly detector: Isolation Forest (latency), DBSCAN (drift)│
│  └─ Incident response: trace correlation + runbook links        │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Data Flow & Event Correlation

```
git-gitops-flow (merge_started) 
  → span: merge_preparation (900ms avg)
    → span: ml_scoring (450ms avg, model_version=v2.4, confidence=0.94)
    → span: conflict_detection (50ms avg, conflicts=0)
  → span: git_merge (150ms avg, merge_algorithm=recursive)
  → span: post_merge_ci (3200ms avg, ci_status=passed)
  → span: verification (200ms avg, verification_ok=true)
  → span: notification (100ms avg, channels=["slack", "github"])

All spans tagged with:
  trace_id = "a4fb4a318d7d4a408afc0e8f80b14891"
  span_id = "1131e6c302f8d381"
  parent_span_id = "05e3f0c8d696e28f"
  deployment_id = "prod-merge-2026-07-27-14:32:18"
  repo = "anthropics/claude-code"
  author = "alice@example.com"
  merge_confidence = "0.94" (dimension)
  ml_model_version = "v2.4" (dimension)

Exported to:
  Jaeger (trace replay, latency analysis, dependency graph)
  ClickHouse (metrics: merge_duration_sec, ml_scoring_latency_ms, cost_cents)
  Supabase (raw logs + feedback: false_positive=0, cost_estimate=0.012)
```

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `enable_tracing` | boolean | No | Enable 100% distributed tracing (default: `true`). |
| `trace_sampling_rate` | float | No | Trace sampling: 0.0–1.0 (default: 1.0 = 100% sampling for audit). |
| `metrics_export_interval` | integer | No | Metrics export frequency (seconds, default: 10). |
| `jaeger_endpoint` | string | No | Jaeger collector gRPC endpoint (default: `localhost:14250`). |
| `clickhouse_endpoint` | string | No | ClickHouse HTTP endpoint (default: `localhost:8123`). |
| `supabase_url` | string | No | Supabase API endpoint for audit logs (default: env `SUPABASE_URL`). |
| `alertmanager_endpoint` | string | No | Alertmanager webhook URL for alerts (default: env `ALERTMANAGER_WEBHOOK`). |
| `anomaly_detection_enabled` | boolean | No | Enable real-time anomaly detection (default: `true`). |
| `alert_rules_config` | file | No | Custom Alertmanager YAML rules (default: built-in 8 rules). |
| `dashboard_export_format` | enum | No | Export dashboards: `grafana_json`, `prometheus_rules`, `otel_config` (default: all). |

---

## Outputs

### 1. Traces (Jaeger)

**Immutable audit trail** of all merge operations. Each trace contains:
- 5–12 nested spans (merge_started → merge_completed)
- Full context: repo, author, ML confidence, feature importance, resource utilization
- Latency breakdown per operation (merge_preparation, ml_scoring, conflict_detection, git_merge, ci)
- Error events (conflict_detected, post_merge_ci_failed, rollback_triggered)

**Storage**: Jaeger backend (24h retention, immutable for audit). Example trace JSON:

```json
{
  "traceID": "a4fb4a318d7d4a408afc0e8f80b14891",
  "processID": "p1",
  "process": { "serviceName": "git-evolution-suite", "tags": {} },
  "spans": [
    {
      "traceID": "a4fb4a318d7d4a408afc0e8f80b14891",
      "spanID": "1131e6c302f8d381",
      "parentSpanID": "05e3f0c8d696e28f",
      "operationName": "merge_operation",
      "references": [],
      "startTime": 1690446738000000,
      "duration": 4700000,
      "tags": {
        "git.repo": "anthropics/claude-code",
        "git.author": "alice@example.com",
        "git.merge_confidence": 0.94,
        "ml.model_version": "v2.4",
        "http.status_code": 200,
        "span.kind": "INTERNAL"
      },
      "logs": [
        {
          "timestamp": 1690446738100000,
          "fields": [{ "key": "event", "value": "merge_started" }]
        },
        {
          "timestamp": 1690446739050000,
          "fields": [{ "key": "event", "value": "ml_scoring_complete" }, { "key": "confidence", "value": "0.94" }]
        }
      ],
      "processID": "p1",
      "warnings": []
    }
  ]
}
```

### 2. Metrics (50+ Prometheus PromQL)

**Real-time time-series metrics** exported to ClickHouse and scraped by Prometheus/Grafana.

#### Deployment Metrics (latency, throughput, errors)

```yaml
# Merge operation duration (histogram, seconds)
git_merge_duration_seconds_bucket{repo="anthropics/claude-code",le="0.1"}
git_merge_duration_seconds_bucket{repo="anthropics/claude-code",le="0.5"}
git_merge_duration_seconds_bucket{repo="anthropics/claude-code",le="1.0"}
git_merge_duration_seconds_bucket{repo="anthropics/claude-code",le="5.0"}
git_merge_duration_seconds_bucket{repo="anthropics/claude-code",le="+Inf"}
git_merge_duration_seconds_count{repo="anthropics/claude-code"}
git_merge_duration_seconds_sum{repo="anthropics/claude-code"}

# Percentile queries (p50, p95, p99)
histogram_quantile(0.50, rate(git_merge_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(git_merge_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(git_merge_duration_seconds_bucket[5m]))

# Merge success rate (counter-based)
git_merge_success_total{repo,author,result}
git_merge_total{repo,author}
rate(git_merge_success_total[5m]) / rate(git_merge_total[5m])

# False positive rate (auto-merged but should have escalated)
git_false_positive_total{repo,author,severity}
rate(git_false_positive_total[1h]) / rate(git_merge_auto_total[1h])

# Merge conflicts (counter)
git_merge_conflicts_total{repo,file_type,resolution_strategy}

# CI post-merge failures (counter)
git_postmerge_ci_failures_total{repo,stage,failure_reason}

# Auto-merge acceptance rate
git_merge_auto_total{repo,outcome} # auto_merged, escalated, rejected
rate(git_merge_auto_total{outcome="auto_merged"}[5m])

# Rollback rate
git_rollback_total{repo,reason}
rate(git_rollback_total[1h])

# Merge throughput (ops/min)
rate(git_merge_total[1m])
```

#### ML Model Metrics

```yaml
# Model inference latency (ms)
git_ml_inference_latency_milliseconds{model_version="v2.4",op="scoring"}
git_ml_inference_latency_milliseconds{model_version="v2.4",op="feature_extraction"}

# Confidence score distribution (histogram)
git_ml_confidence_score_bucket{repo,le="0.50"}
git_ml_confidence_score_bucket{repo,le="0.75"}
git_ml_confidence_score_bucket{repo,le="0.95"}
git_ml_confidence_score_bucket{repo,le="1.00"}
git_ml_confidence_score_count{repo}
git_ml_confidence_score_sum{repo}

# Model accuracy (precision, recall, F1)
git_ml_accuracy_precision{model_version}
git_ml_accuracy_recall{model_version}
git_ml_accuracy_f1{model_version}

# Feature importance (top 5 features)
git_ml_feature_importance{feature_name,rank}

# Model drift detection (Wasserstein distance)
git_ml_drift_wasserstein_distance{metric="confidence_distribution"}
git_ml_drift_population_stability_index{metric="confidence"}

# Prediction correctness feedback
git_ml_prediction_feedback{outcome,was_correct} # true/false
```

#### Resource Metrics

```yaml
# CPU usage per merge (millicores)
git_cpu_usage_millicores{repo,component="ml_inference"}
git_cpu_usage_millicores{repo,component="git_merge"}
git_cpu_usage_millicores{repo,component="ci_orchestration"}

# Memory usage per merge (bytes)
git_memory_usage_bytes{repo,component}

# Disk I/O per merge (bytes read/written)
git_disk_io_bytes_total{repo,operation="read"}
git_disk_io_bytes_total{repo,operation="write"}

# Network bandwidth per merge (bytes)
git_network_bandwidth_bytes_total{repo,direction="ingress"}
git_network_bandwidth_bytes_total{repo,direction="egress"}

# Concurrent merge operations (gauge)
git_concurrent_merges_active{repo}
```

#### Cost Metrics

```yaml
# Per-merge cost (USD cents)
git_merge_cost_cents{repo,author,ml_model_version}

# Cost breakdown by component (cents)
git_cost_breakdown_cents{repo,component="ml_inference"}
git_cost_breakdown_cents{repo,component="compute"}
git_cost_breakdown_cents{repo,component="storage"}

# Cumulative monthly cost (USD)
git_monthly_cost_usd{repo,month}

# Cost per author (USD)
git_cost_per_author_usd{author,month}

# Budget utilization (%)
git_budget_utilization_percent{month}

# Cost anomalies (USD)
git_cost_anomaly_usd{repo,anomaly_type}
```

#### SLO & Compliance Metrics

```yaml
# SLO: merge latency p99 < 5 seconds
git_slo_merge_latency_p99_met{repo} # 0 = missed, 1 = met

# SLO: merge success rate > 99%
git_slo_success_rate_met{repo} # 0 = missed, 1 = met

# SLO: false positive rate < 3%
git_slo_fp_rate_met{repo} # 0 = missed, 1 = met

# SLO: post-merge CI success > 98%
git_slo_ci_success_rate_met{repo} # 0 = missed, 1 = met

# Audit log entries (immutable event count)
git_audit_log_entries_total{event_type,severity}
```

### 3. Structured Logs (JSON, Supabase)

**Queryable, context-correlated audit logs** stored in PostgreSQL (Supabase).

```json
{
  "timestamp": "2026-07-27T14:32:18.342Z",
  "trace_id": "a4fb4a318d7d4a408afc0e8f80b14891",
  "span_id": "1131e6c302f8d381",
  "service": "git-gitops-flow",
  "level": "INFO",
  "event": "merge_completed",
  "repo": "anthropics/claude-code",
  "author": "alice@example.com",
  "pr_number": 2847,
  "merge_status": "success",
  "merge_strategy": "recursive",
  "ml_confidence": 0.94,
  "ml_model_version": "v2.4",
  "feature_importance": {
    "test_pass_rate": 0.32,
    "security_scan_critical_count": 0.18,
    "file_change_pattern": 0.15,
    "author_history": 0.12,
    "commit_message_quality": 0.10,
    "time_of_day": 0.08,
    "repo_fan_out": 0.05
  },
  "merge_duration_ms": 4700,
  "conflict_count": 0,
  "postmerge_ci_status": "passed",
  "postmerge_ci_duration_ms": 3200,
  "resource_utilization": {
    "cpu_millicores": 450,
    "memory_bytes": 256000000,
    "disk_io_bytes": 2500000
  },
  "cost_estimate_cents": 1.2,
  "deployment_id": "prod-merge-2026-07-27-14:32:18",
  "audit_trail": {
    "action": "auto_merged",
    "approved_by": null,
    "approval_time_ms": 0,
    "escalation_reason": null
  },
  "error": null,
  "tags": {
    "environment": "prod",
    "phase": "fase_4",
    "criticality": "medium"
  }
}
```

### 4. Grafana Dashboards (4 custom dashboards)

#### Dashboard 1: Git Analytics

**Merge trends, author patterns, repo health**

Panels:
- **Merge Success Rate (gauges)**: per-repo, 24h moving average
- **Merge Duration Heatmap**: time-of-day × day-of-week, p50/p95/p99
- **Author Contribution Stacked Area**: commits/day per top 5 authors
- **Repo Health Scorecard**: success rate, avg latency, cost/merge, false positive rate
- **Merge Conflicts Timeline**: stacked bar by resolution strategy
- **CI Post-Merge Failures**: pie chart by stage (build, test, deploy, rollback)

**Query example**:
```promql
sum by (repo) (rate(git_merge_success_total[5m])) / sum by (repo) (rate(git_merge_total[5m]))
```

#### Dashboard 2: ML Health

**Model accuracy, confidence distribution, feature importance, drift**

Panels:
- **Confidence Score Distribution**: histogram (bars for bins: <0.5, 0.5–0.75, 0.75–0.95, 0.95–1.0)
- **Model Accuracy Metrics**: precision, recall, F1 (line charts, weekly trend)
- **Inference Latency (p50/p95/p99)**: time-series line chart
- **Feature Importance Ranking**: bar chart, top 10 features (refreshed weekly)
- **Model Drift (Wasserstein + PSI)**: dual-axis line chart with thresholds
- **False Positive Rate Trend**: line chart with SLO threshold (3%)
- **Model Version Timeline**: annotation for version changes
- **Prediction Feedback Loop**: pie chart (correct / incorrect predictions)

**Query example**:
```promql
histogram_quantile(0.95, rate(git_ml_confidence_score_bucket[1h]))
```

#### Dashboard 3: Cost Attribution

**Per-repo, per-author, per-merge granularity**

Panels:
- **Cost per Repo (bar chart)**: monthly cumulative, sortable
- **Cost per Author (scatter plot)**: x=commits/month, y=cost/month, bubble size=merge count
- **Cost Breakdown by Component**: pie chart (ML inference, compute, storage, network)
- **Hourly Cost Trend**: stacked area (ML inference vs. compute vs. storage)
- **Cost per Merge (histogram)**: distribution of individual merge costs
- **Budget Utilization (gauge)**: % of monthly budget used
- **Cost Anomalies Timeline**: vertical lines on cost trend chart
- **ROI Table**: repos ranked by cost-to-benefit ratio

**Query example**:
```promql
sum by (repo) (git_merge_cost_cents) / 100 as cost_usd
```

#### Dashboard 4: Anomalies & Incidents

**Detected anomalies, SLO breaches, incident timeline**

Panels:
- **Active Anomalies (table)**: timestamp, type (latency, drift, cost), severity, affected repos
- **Latency Spikes (heatmap)**: time × repo, color intensity = spike severity
- **Model Drift Score (gauge + history)**: current Wasserstein distance + threshold line
- **SLO Status (4 gauges)**: Merge latency p99, success rate, FP rate, CI success rate
- **Incident Timeline (annotations)**: merge failures, rollbacks, alerts triggered
- **Correlation Graph (force-directed)**: nodes=repos, edges=shared anomalies
- **Anomaly Distribution (pie)**: latency spikes, drift, cost overruns, ci failures
- **Top Affected Repos (table)**: anomaly count, avg severity, incident frequency

**Query example**:
```promql
git_slo_merge_latency_p99_met{repo}
```

---

## Tracing Instrumentation

### Span Structure & Events

All merge operations are traced with this span hierarchy:

```
Span: merge_operation (root)
  ├─ Span: merge_preparation
  │   ├─ Span: repo_access (event: repo_accessed)
  │   ├─ Span: ml_scoring
  │   │   ├─ Event: feature_extraction_started
  │   │   ├─ Event: model_inference (confidence=0.94, latency_ms=450)
  │   │   └─ Event: feature_importance_computed
  │   └─ Span: conflict_detection (event: conflict_detected, count=0)
  ├─ Span: git_merge
  │   └─ Event: merge_completed (strategy=recursive, status=success)
  ├─ Span: post_merge_ci
  │   ├─ Event: ci_job_submitted
  │   ├─ Event: ci_job_completed (status=passed, duration_ms=3200)
  │   └─ Event: ci_artifacts_stored
  ├─ Span: verification
  │   └─ Event: verification_ok
  └─ Span: notification
      ├─ Event: slack_notification_sent
      └─ Event: github_comment_posted
```

### Tag & Dimension Schema

**Standard tags on all spans**:

```
Trace-level tags:
  trace_id: "a4fb4a318d7d4a408afc0e8f80b14891" (W3C TraceContext)
  deployment_id: "prod-merge-2026-07-27-14:32:18" (unique merge operation ID)
  environment: "prod" or "staging"
  phase: "fase_4"
  version: "v1.0.0"

Span-level tags:
  span.kind: INTERNAL | SERVER | CLIENT
  span.name: "merge_operation" | "ml_scoring" | "git_merge" | ...
  
Git context:
  git.repo: "anthropics/claude-code"
  git.author: "alice@example.com"
  git.pr_number: 2847
  git.branch: "develop" or "main"
  git.merge_strategy: "recursive" | "ours" | "theirs"
  
ML context:
  ml.model_version: "v2.4"
  ml.confidence: 0.94
  ml.recommendation: "AUTO_MERGE" | "ESCALATE" | "REJECT"
  ml.inference_latency_ms: 450
  
Business context:
  repo.risk_level: "low" | "medium" | "high"
  merge.complexity: "simple" | "moderate" | "complex"
  merge.conflict_count: 0
  merge.cost_cents: 1.2
  
Operational context:
  http.status_code: 200 | 409 | 500
  error.type: "null" | "conflict" | "ci_failure" | "timeout"
  resource.cpu_millicores: 450
  resource.memory_bytes: 256000000
```

### Context Propagation (W3C TraceContext)

All spans propagate W3C TraceContext headers for correlation across services:

```http
traceparent: 00-a4fb4a318d7d4a408afc0e8f80b14891-1131e6c302f8d381-01
tracestate: vendor=value
```

---

## Anomaly Detection

### 1. Isolation Forest (Latency Spikes)

Detects unusual latency patterns using unsupervised learning:

```python
from sklearn.ensemble import IsolationForest
import numpy as np

# Training features (7-day window)
X = np.array([
    [merge_duration_ms, concurrent_merges, ci_duration_ms, 
     file_change_count, conflict_count, repo_fan_out, time_of_day_hour],
    # ... more observations
])

# Fit model (100 trees, 256 samples/tree)
iso_forest = IsolationForest(
    n_estimators=100,
    max_samples=256,
    contamination=0.02,  # expect 2% anomalies
    random_state=42
)
iso_forest.fit(X)

# Detect anomalies (prediction: -1 = anomaly, 1 = normal)
predictions = iso_forest.predict(X_test)
anomaly_scores = iso_forest.score_samples(X_test)  # [-1.0 to 0.5]

# Alert threshold: anomaly_score < -0.3
for merge in recent_merges:
    if merge.anomaly_score < -0.3:
        alert(f"Latency spike detected: {merge.duration_ms}ms (z-score: {merge.anomaly_score:.2f})")
```

**Trigger**: Latency p99 > 5 seconds (SLO threshold)  
**Action**: Create alert, add to Anomalies dashboard, store feedback in Supabase

### 2. DBSCAN (ML Model Drift)

Detects distribution shifts in confidence scores and feature importance:

```python
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist, squareform
import numpy as np

# Time-windowed confidence scores (last 7 days)
confidence_baseline = np.array([0.89, 0.91, 0.92, 0.90, 0.89, ...])  # 1000 merges
confidence_recent = np.array([0.78, 0.75, 0.81, 0.72, 0.80, ...])   # 50 merges

# Wasserstein distance (optimal transport)
from scipy.stats import wasserstein_distance
w_distance = wasserstein_distance(confidence_baseline, confidence_recent)

# Alert if drift > 0.05 (5% distributional change)
if w_distance > 0.05:
    alert(f"Model drift detected: Wasserstein={w_distance:.3f}")

# Population Stability Index (PSI) for discrete distributions
psi = sum((recent_pct - baseline_pct) * np.log(recent_pct / baseline_pct))
# PSI > 0.1 indicates shift, PSI > 0.25 indicates major shift
if psi > 0.1:
    alert(f"Model PSI drift: {psi:.3f}")
```

**Trigger**: Model confidence distribution shifts >2%  
**Action**: Trigger model retraining, flag merges for manual review, store feedback

### 3. Threshold-Based Alerts (SLO Breaches)

Simple threshold-based detection for known SLO targets:

```yaml
# SLO: Merge latency p99 < 5 seconds
if histogram_quantile(0.99, rate(git_merge_duration_seconds_bucket[5m])) > 5.0:
  alert("CRITICAL: Merge latency p99 exceeded 5s")

# SLO: Merge success rate > 99%
if rate(git_merge_success_total[1h]) / rate(git_merge_total[1h]) < 0.99:
  alert("WARNING: Merge success rate below 99%")

# SLO: False positive rate < 3%
if rate(git_false_positive_total[1h]) / rate(git_merge_auto_total[1h]) > 0.03:
  alert("CRITICAL: False positive rate > 3%")

# SLO: Post-merge CI success > 98%
if rate(git_postmerge_ci_failures_total[1h]) / rate(git_merge_total[1h]) > 0.02:
  alert("WARNING: Post-merge CI success < 98%")
```

---

## Alerting Integration

### 8 Critical Alerts

| Alert | Condition | Severity | Escalation | Action |
|-------|-----------|----------|------------|--------|
| **ModelDriftDetected** | Wasserstein dist > 0.05 or PSI > 0.1 | CRITICAL | On-call ML engineer (PagerDuty) | Pause auto-merge, trigger retraining, manual review queue |
| **MergeFalsePositiveRateHigh** | FP rate > 3% | CRITICAL | Security + ML team | Block auto-merge, escalate all PRs, incident review |
| **MergeLatencySpike** | p99 > 5s (Isolation Forest anomaly) | WARNING | DevOps on-call | Check OTEL traces, resource utilization, Jaeger trace replay |
| **MergeSuccessRateLow** | Success rate < 99% (1h window) | WARNING | DevOps on-call | Review recent failures, check CI/CD logs, trigger incident response |
| **PostMergeCIFailure** | CI success < 98% or >5 failures in 30min | CRITICAL | Build + Ops teams | Investigate CI root cause, rollback if cascading |
| **DataLossDetected** | Audit log gaps or trace drops > 0.1% | CRITICAL | Security + DB ops | Page on-call immediately, verify trace exports, Jaeger retention |
| **CostOverrun** | Monthly cost > 110% of budget or >$1000/day anomaly | WARNING | Finance + Ops | Review expensive repos/authors, optimize or rebalance |
| **IncidentResponseFailure** | Incident runbook execution fails or manual escalation timeout >24h | CRITICAL | On-call incident commander | Page escalation team, manual investigation required |

### Alertmanager Configuration

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

route:
  receiver: default
  group_by: [alertname, repo]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  routes:
    # CRITICAL alerts → immediate PagerDuty + Slack
    - match:
        severity: CRITICAL
      receiver: pagerduty_oncall
      continue: true
      repeat_interval: 5m
    
    # WARNING alerts → Slack only, 30min repeat
    - match:
        severity: WARNING
      receiver: slack_alerts
      repeat_interval: 30m
    
    # Model drift → ML team channel + PagerDuty
    - match_re:
        alertname: "ModelDriftDetected|MergeFalsePositiveRateHigh"
      receiver: ml_team_pagerduty
      group_wait: 1m
      repeat_interval: 10m

receivers:
  - name: default
    slack_configs:
      - channel: "#git-evolution-alerts"
        title: "{{ .GroupLabels.alertname }}"
        text: "{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}"

  - name: pagerduty_oncall
    slack_configs:
      - channel: "#incident-response"
    pagerduty_configs:
      - service_key: "{{ .Alerts.0.Labels.pagerduty_service_key }}"
        description: "{{ .GroupLabels.alertname }}: {{ .Alerts.0.Annotations.summary }}"

  - name: ml_team_pagerduty
    slack_configs:
      - channel: "#ml-platform"
    pagerduty_configs:
      - service_key: "{{ .Alerts.0.Labels.ml_pagerduty_key }}"

inhibit_rules:
  # Inhibit low-severity if high-severity is already firing
  - source_match:
      severity: CRITICAL
    target_match:
      severity: WARNING
    equal: [repo, alertname]
```

---

## Worked Examples

### Example 1: Trace a Merge Operation (End-to-End)

**Scenario**: Alice merges PR #2847 in `anthropics/claude-code`. ML confidence = 0.94 → auto-merged. Goal: View full trace in Jaeger.

**Steps**:

1. **In Grafana Git Analytics dashboard**, click "Merge Success Rate" gauge for repo `anthropics/claude-code`
2. **Drill into time-series** → filter by author=alice → find merge at 2026-07-27T14:32:18
3. **Click trace ID** (`a4fb4a318d7d4a408afc0e8f80b14891`) → redirects to Jaeger UI
4. **In Jaeger**, view trace with 8 spans:
   - `merge_operation` (root, 4700ms total)
   - `merge_preparation` (900ms)
     - `repo_access` (50ms)
     - `ml_scoring` (450ms, confidence=0.94, model=v2.4)
     - `conflict_detection` (0 conflicts)
   - `git_merge` (150ms, strategy=recursive)
   - `post_merge_ci` (3200ms, status=passed)
   - `verification` (200ms, ok=true)
   - `notification` (100ms, slack + github)

**Key metrics from trace**:
```
Total duration: 4700ms
ML inference latency: 450ms (within SLO <500ms)
Cost: 1.2 cents
Resource utilization: 450 mCPU, 256 MB RAM
Feature importance: test_pass_rate=32%, security_scan=18%, file_pattern=15%
Post-merge CI: PASSED (3200ms)
```

**Export**: Click "Export Trace as JSON" → download for incident review or compliance audit

---

### Example 2: Detect Latency Spike Anomaly

**Scenario**: On 2026-07-27 at 16:45, monitoring system detects a latency spike.

**Automatic detection**:
1. **Isolation Forest** runs every 5 minutes on last 1000 merges
2. **Detects**:
   - Merge duration: 12.5s (usual: ~4.7s)
   - Anomaly score: -0.52 (threshold: < -0.3)
   - Root cause candidates: high concurrent merges (12), large file changeset (450 files)

3. **Alert triggered**:
```json
{
  "alertname": "MergeLatencySpike",
  "severity": "WARNING",
  "repo": "anthropics/claude-code",
  "anomaly_score": -0.52,
  "merge_duration_ms": 12500,
  "concurrent_merges": 12,
  "file_change_count": 450,
  "timestamp": "2026-07-27T16:45:30Z"
}
```

4. **Slack notification**:
   ```
   :warning: Merge latency spike detected
   Repo: anthropics/claude-code
   Duration: 12.5s (p99 SLO: 5s)
   Anomaly score: -0.52
   Concurrent merges: 12 (correlating factor)
   
   [View trace] [View dashboard] [Runbook]
   ```

5. **DevOps on-call**:
   - Clicks "View trace" → Jaeger shows bottleneck in `post_merge_ci` (9.5s, CI queue backlog)
   - Checks resource utilization dashboard → CPU at 95%, memory at 87%
   - Scales CI workers from 8 to 12
   - Latency normalizes in 10 minutes

6. **Feedback loop**:
   - Incident marked as `resolved=true` in Supabase
   - Isolation Forest retrains with this example
   - Anomaly detector refines threshold for concurrent merge detection

---

### Example 3: Cost Attribution Dashboard

**Scenario**: Finance team wants to understand Q3 GitOps costs by author and repo.

**Dashboard query**:
```promql
# Top 10 repos by cost
sum by (repo) (git_merge_cost_cents) / 100 > 0
order by value desc
limit 10
```

**Results**:
```
anthropics/claude-code:        $342.15 (156 merges, avg $2.19/merge)
anthropics/anthropic-sdk-py:   $187.42 (98 merges, avg $1.91/merge)
anthropics/anthropic-sdk-js:   $124.80 (67 merges, avg $1.86/merge)
...
```

**Top authors by cost**:
```promql
sum by (author) (git_merge_cost_cents) / 100
order by value desc
limit 5
```

**Results**:
```
alice@example.com:   $287.30 (142 merges, avg $2.02/merge)
bob@example.com:     $195.15 (119 merges, avg $1.64/merge)
carol@example.com:   $121.45 (93 merges, avg $1.30/merge)
david@example.com:    $89.60 (54 merges, avg $1.66/merge)
eve@example.com:      $61.87 (42 merges, avg $1.47/merge)
```

**Cost breakdown by component**:
```
ML inference: $198.40 (43%)
Compute (runner): $142.30 (31%)
Storage & logging: $67.20 (15%)
Network: $38.15 (8%)
Other: $18.35 (3%)
```

**Insights**:
- Alice's merges are 23% more expensive than average (2.02 vs. 1.64) → complex PRs with many files
- `anthropics/claude-code` is most expensive → high merge frequency + large changesets
- ML inference dominates cost → consider model optimization (quantization, inference caching)

**Action**: Recommend Alice's team to break large PRs into smaller changesets for cost optimization

---

### Example 4: Incident Response Using Trace Data

**Scenario**: Post-merge CI failed for merge ID `prod-merge-2026-07-27-15:22:45`. Finance system integration broke. Goal: Root cause analysis.

**Steps**:

1. **Find trace in Grafana**:
   - Filter anomalies dashboard for event=`postmerge_ci_failures_total`
   - Click incident → trace_id = `b7c3a5d2f8e1a4c9`

2. **Open in Jaeger**:
   - Trace shows 8 spans
   - **Bottleneck found**: `post_merge_ci` span shows:
     ```json
     {
       "operationName": "post_merge_ci",
       "duration": 8200,  // 8.2 seconds
       "spans": [
         {
           "operationName": "ci_job_submitted",
           "duration": 100,
           "tags": { "job_id": "ci-run-5842" }
         },
         {
           "operationName": "ci_job_running",
           "duration": 7950,
           "logs": [
             { "timestamp": ..., "message": "Test finance_integration.ts FAILED" },
             { "timestamp": ..., "message": "Error: timeout connecting to database" }
           ]
         }
       ]
     }
   ```

3. **Correlate with logs** (Supabase query):
   ```sql
   SELECT timestamp, event, repo, error FROM git_audit_logs 
   WHERE trace_id = 'b7c3a5d2f8e1a4c9' 
   ORDER BY timestamp;
   ```
   Result:
   ```
   14:22:18  repo_accessed       anthropics/finance-lib
   14:22:20  ml_scoring_complete confidence=0.88
   14:22:21  git_merge           success
   14:22:22  ci_job_submitted    job_id=ci-run-5842
   14:22:30  ci_job_failed       error=timeout, database_url=prod-db-replica-3
   ```

4. **Database team investigates**:
   - Prod DB replica 3 was throttled due to high IO
   - Finance integration tests timed out after 30 seconds
   - Root cause: unoptimized query in migration 0142_financial_sync.sql

5. **Automated rollback**:
   - Merge is rolled back (new PR created, merge reverted)
   - All downstream syncs in fan-out are also reverted (transactional safety)
   - Finance team deploys fix, CI passes, re-merge approved

6. **Post-mortem**:
   - Alert rule updated: `ci_test_timeout` → escalate if database latency > 100ms
   - Query review process added to Finance team's deployment SOP
   - Trace saved to incident archive for compliance

---

## Integration & Deployment

### OpenTelemetry SDK Installation

**Python (FastAPI/async Git automation)**:
```python
from opentelemetry import trace, metrics, logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Jaeger trace exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Prometheus metrics reader
prometheus_reader = PrometheusMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[prometheus_reader]))

# Auto-instrumentation
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument(engine)

# Custom span creation
tracer = trace.get_tracer(__name__)

@app.post("/merge")
async def merge_pr(pr_id: int):
    with tracer.start_as_current_span("merge_operation") as span:
        span.set_attribute("git.pr_number", pr_id)
        span.set_attribute("git.repo", "anthropics/claude-code")
        span.set_attribute("git.author", "alice@example.com")
        
        with tracer.start_as_current_span("ml_scoring"):
            confidence = await score_merge(pr_id)
            span.set_attribute("ml.confidence", confidence)
        
        with tracer.start_as_current_span("git_merge"):
            result = await git_merge(pr_id)
        
        span.set_attribute("merge.status", result.status)
        return result
```

**Go (CLI Git tool)**:
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/jaeger/rpc"
    "go.opentelemetry.io/otel/sdk/trace"
)

// Initialize Jaeger exporter
jaegerExporter, _ := rpc.New(
    rpc.WithEndpoint("http://localhost:14250"),
)
defer jaegerExporter.Shutdown(ctx)

// Set global tracer provider
otel.SetTracerProvider(
    trace.NewTracerProvider(
        trace.WithBatcher(jaegerExporter),
    ),
)

tracer := otel.Tracer("git-evolution-suite")

func mergeRepository(ctx context.Context, prID int) error {
    ctx, span := tracer.Start(ctx, "merge_operation")
    defer span.End()
    
    span.SetAttributes(
        attribute.String("git.pr_number", fmt.Sprintf("%d", prID)),
        attribute.String("git.repo", "anthropics/claude-code"),
    )
    
    // Nested spans
    _, mlSpan := tracer.Start(ctx, "ml_scoring")
    confidence := scoreMerge(ctx, prID)
    mlSpan.SetAttribute("ml.confidence", confidence)
    mlSpan.End()
    
    return gitMerge(ctx, prID)
}
```

### Local Development Mode

For local development without full Jaeger/ClickHouse setup:

```python
# Use console exporters (stdout)
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

if ENV == "development":
    # Console exporter (print to stdout)
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )
    
    # In-memory storage for local inspection
    in_memory_exporter = InMemorySpanExporter()
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(in_memory_exporter)
    )
    
    # Run `export OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost` to connect to Jaeger
```

---

## Performance Impact Analysis

**Overhead of 100% tracing, metrics, structured logging**:

| Component | Overhead | Mitigation |
|-----------|----------|-----------|
| **Trace span creation** | +15–20ms per merge | Batch processing, async export |
| **ML inference tagging** | +5–8ms | In-band (minimal) |
| **Metrics aggregation** | +10–15ms | Periodic (every 10s) export |
| **Structured logging (JSON)** | +8–12ms | Async buffering, batch flush |
| **Network export (Jaeger + ClickHouse)** | +30–50ms | Async batch processor (no blocking) |
| **Total overhead** | **~70–115ms per merge** | **<5% of typical 4.7s merge duration** |

**Mitigation strategies**:
1. **Async export**: OTEL batch processor batches 512 spans, exports every 5 seconds (non-blocking)
2. **Sampling in dev**: Local development uses 10% sampling (reduce overhead to <11ms)
3. **Metric aggregation**: Prometheus scrape interval 10s, not per-merge (no spike)
4. **Log buffering**: JSON logs buffered in memory, flushed every 100 entries or 5 seconds

**Result**: Observable overhead <5% relative to merge operations. No user-facing impact.

---

## SLA & SLO Definitions

### SLOs for Git Evolution Suite (Fase 4)

| SLO | Target | Measurement | Alert Threshold |
|-----|--------|-------------|-----------------|
| **Merge Latency p99** | <5 seconds | `histogram_quantile(0.99, rate(git_merge_duration_seconds_bucket[5m]))` | >5.0s triggers WARNING |
| **Merge Success Rate** | ≥99% | `rate(git_merge_success_total[1h]) / rate(git_merge_total[1h])` | <0.99 triggers WARNING |
| **False Positive Rate** | <3% | `rate(git_false_positive_total[1h]) / rate(git_merge_auto_total[1h])` | >0.03 triggers CRITICAL |
| **Post-Merge CI Success** | ≥98% | `1 - rate(git_postmerge_ci_failures_total[1h]) / rate(git_merge_total[1h])` | <0.98 triggers WARNING |
| **Trace Export Latency** | <30s | Time from span completion to Grafana visibility | >30s triggers INFO |
| **Jaeger Availability** | ≥99.9% | Query latency <500ms, 5xx errors <0.1% | Breach triggers CRITICAL |
| **ML Model Latency p95** | <500ms | `histogram_quantile(0.95, rate(git_ml_inference_latency_milliseconds_bucket[5m]))` | >500ms triggers WARNING |
| **Cost Forecast Accuracy** | ±10% | `|actual_cost - predicted_cost| / actual_cost` | >10% drift triggers INFO |

### Error Budgets (Monthly)

```
Merge Success Rate 99% → 7.2 hours downtime per month
Post-Merge CI 98% → 14.4 hours of CI failures per month
Trace Latency <30s → 43 minutes of slow traces per month
ML Inference <500ms p95 → 43 minutes of slow inference per month
```

---

## Deployment Guide (Step-by-Step)

### Phase 1: Infrastructure Setup (1–2 days)

1. **Deploy Jaeger backend** (all-in-one or distributed):
   ```bash
   docker run -d --name jaeger \
     -p 6831:6831/udp \
     -p 16686:16686 \
     jaegertracing/all-in-one:latest
   ```

2. **Deploy ClickHouse** (time-series database):
   ```bash
   docker run -d --name clickhouse \
     -p 8123:8123 \
     -v clickhouse_data:/var/lib/clickhouse \
     clickhouse/clickhouse-server:latest
   ```

3. **Create ClickHouse tables** (git_traces, git_metrics, git_logs):
   ```sql
   CREATE TABLE git_metrics (
     timestamp DateTime,
     trace_id String,
     metric_name String,
     metric_value Float64,
     labels Map(String, String),
     INDEX idx_timestamp_trace (timestamp, trace_id) TYPE minmax GRANULARITY 1
   ) ENGINE = MergeTree()
   ORDER BY (timestamp, metric_name)
   TTL timestamp + INTERVAL 90 DAY;
   ```

4. **Deploy Prometheus** (metrics scrape target):
   ```bash
   docker run -d --name prometheus \
     -v prometheus.yml:/etc/prometheus/prometheus.yml \
     -p 9090:9090 \
     prom/prometheus:latest
   ```

5. **Deploy Grafana** (visualization):
   ```bash
   docker run -d --name grafana \
     -p 3000:3000 \
     grafana/grafana:latest
   ```

### Phase 2: Instrumentation (2–3 days)

1. **Install OTEL SDKs** in git-gitops-flow, git-auto-merge-confidence, git-multi-repo-workflows:
   ```bash
   pip install opentelemetry-api opentelemetry-sdk \
     opentelemetry-exporter-jaeger opentelemetry-exporter-prometheus
   ```

2. **Add auto-instrumentation** (FastAPI, SQLAlchemy, requests):
   ```python
   from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
   from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
   
   FastAPIInstrumentor.instrument_app(app)
   SQLAlchemyInstrumentor().instrument(engine)
   ```

3. **Add custom spans** in merge operation flow (merge_preparation, ml_scoring, git_merge, post_merge_ci, verification, notification)

4. **Add custom metrics** (50+ metrics across deployment, ML, resource, cost)

### Phase 3: Dashboard Creation (1 day)

1. **Create 4 Grafana dashboards** from JSON specs (Dashboard 1–4)
2. **Configure data sources** (Prometheus for metrics, Jaeger for traces)
3. **Add dashboard variables** for repo filtering, time-range selection, author filtering
4. **Test dashboard queries** with mock data

### Phase 4: Alerting Setup (1 day)

1. **Deploy Alertmanager** (if not already running):
   ```bash
   docker run -d --name alertmanager \
     -v alertmanager.yml:/etc/alertmanager/alertmanager.yml \
     -p 9093:9093 \
     prom/alertmanager:latest
   ```

2. **Configure 8 alert rules** (ModelDriftDetected, MergeFalsePositiveRateHigh, etc.)

3. **Set up webhooks** (Slack, PagerDuty, email)

4. **Test alerts** with mock data

### Phase 5: Validation & Tuning (2 days)

1. **Run 10–20 test merges** through full pipeline
2. **Verify traces appear in Jaeger** (<30s latency)
3. **Verify metrics appear in Grafana** (within 10s)
4. **Verify alerts trigger correctly** (no false positives)
5. **Tune anomaly detection** thresholds (Isolation Forest contamination rate, DBSCAN eps)
6. **Load test** with 50 concurrent merges

### Phase 6: Production Rollout (1 day)

1. **Enable on staging** for 1 week (canary)
2. **Monitor** alert false positive rate, overhead metrics
3. **Roll out to production** with 100% sampling
4. **Monitor SLOs** for 1 week
5. **Adjust retention policies** based on storage usage

---

## Capacity Planning & Scaling

### Storage Requirements

```
Trace storage (Jaeger):
  - 1 trace ≈ 5 KB (8 spans, average tags/logs)
  - 50 merges/day × 30 days = 1,500 traces/month
  - 1,500 × 5 KB = 7.5 MB/month (24h retention = 7.5 MB)
  - For 90d retention: 7.5 MB × 3 = 22.5 MB (on-disk backend)

Metrics storage (ClickHouse):
  - 50+ metrics × 50 merges/day × 30 days = 75,000 data points/month
  - With cardinality (10 repos × 5 authors × 5 dimensions) = 750,000 points/month
  - At ~100 bytes/point: 75 MB/month
  - For 90d retention: 75 MB × 3 = 225 MB

Logs storage (Supabase):
  - 1 merge ≈ 1 KB JSON log
  - 50 merges/day × 30 days = 1,500 logs/month = 1.5 MB
  - For 90d retention: 1.5 MB × 3 = 4.5 MB

Total: ~250 MB for 90 days (very manageable)
```

### Scalability Limits (Fase 4)

| Metric | Limit | Mitigation |
|--------|-------|-----------|
| **Merges per day** | 1,000+ | Batch processor handles up to 2K merges/min |
| **Concurrent spans** | 10,000+ | Async export (non-blocking) |
| **Cardinality** | 100K+ dimensions | Partition ClickHouse tables, use LowCardinality columns |
| **Trace latency** | <30s | Batch processor every 5s |
| **Query latency** | <1s | Index on timestamp, repo, trace_id |

---

## Troubleshooting Guide

### Symptom: Traces not appearing in Jaeger

**Causes & fixes**:
1. **OTEL exporter not configured**: Verify `jaeger_endpoint` is reachable
   ```bash
   telnet localhost 14250
   ```

2. **Jaeger collector not running**: Check logs
   ```bash
   docker logs jaeger | grep "listening"
   ```

3. **Sampling rate = 0**: Verify `trace_sampling_rate` > 0
   ```python
   assert sdk_config.trace_sampling_rate > 0, "Sampling rate must be > 0"
   ```

### Symptom: High false positive rate in alerts

**Causes & fixes**:
1. **Isolation Forest contamination rate too high**: Tune from 0.02 to 0.01
2. **Threshold-based alerts too sensitive**: Increase SLO thresholds (e.g., latency p99 from 5s to 6s)
3. **Seasonal patterns not accounted for**: Use STL decomposition to remove trend/seasonality before anomaly detection

### Symptom: ClickHouse out of disk space

**Causes & fixes**:
1. **TTL not enabled**: Verify TTL policy on tables
   ```sql
   ALTER TABLE git_metrics MODIFY TTL timestamp + INTERVAL 90 DAY;
   ```

2. **High cardinality metrics**: Use LowCardinality columns for repo, author, component
   ```sql
   ALTER TABLE git_metrics MODIFY COLUMN repo LowCardinality(String);
   ```

---

## Advanced: Custom Anomaly Detection Tuning

### Isolation Forest Parameters

```python
from sklearn.ensemble import IsolationForest

# Tuning for merge latency spikes
iso_forest = IsolationForest(
    n_estimators=150,           # More trees for stability
    max_samples=min(256, len(X)),  # Subsample for scalability
    max_features=0.8,           # Use 80% of features per tree
    contamination=0.01,         # Expect 1% anomalies (tune down if too many alerts)
    random_state=42,
    n_jobs=-1                   # Parallel processing
)

# Cross-validate on holdout set
from sklearn.model_selection import cross_validate
scores = cross_validate(iso_forest, X_train, scoring='roc_auc', cv=5)
print(f"Cross-validation AUC: {scores['test_score'].mean():.3f}")
```

### DBSCAN Parameters for Model Drift

```python
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist

# Tuning for confidence score distribution drift
# Use Wasserstein distance as metric
distances = pdist(confidence_scores.reshape(-1, 1), metric='euclidean')

# Find "knee" point (elbow curve)
distances_sorted = np.sort(distances)
k_distance_graph = distances_sorted[::-1]  # reverse sort

# DBSCAN with data-driven eps
eps = 0.05  # threshold for Wasserstein distance
dbscan = DBSCAN(eps=eps, min_samples=5)
clusters = dbscan.fit_predict(confidence_scores.reshape(-1, 1))

# Clusters: -1 = noise (anomaly), others = normal distribution clusters
n_anomalies = sum(clusters == -1)
print(f"Detected {n_anomalies} anomalies ({n_anomalies/len(clusters)*100:.1f}%)")
```

---

## Limitations & Future Roadmap

### Current Limitations (v1.0)

1. **Jaeger retention**: 24h default (consider on-disk backend for 90d compliance)
2. **ClickHouse cardinality**: High-cardinality tags (trace_id, span_id) may require partitioning for large-scale
3. **Model drift**: DBSCAN requires manual retraining; future: online learning
4. **Cost model**: Linear cost estimation; future: non-linear ML cost predictor
5. **Correlation latency**: Trace data appears in Grafana with ~30s delay (batch export window)
6. **Manual threshold tuning**: Isolation Forest contamination rate requires per-metric tuning

### Future (v1.1–v2.0)

- [ ] **Trace sampling strategy**: Move from 100% to intelligent sampling (high-risk merges always sampled, low-risk sampled at 5%)
- [ ] **Custom spans in ML model**: Export feature vectors, embeddings, decision tree paths to Jaeger for explainability
- [ ] **Live streaming**: WebSocket-based live trace tail for real-time incident response
- [ ] **Cost optimization engine**: ML-based cost predictor (non-linear feature interactions)
- [ ] **Chaos testing integration**: Automatically generate anomaly scenarios from prod traces
- [ ] **Multi-tenancy**: Support cost attribution across multiple organizations/teams
- [ ] **Automated threshold tuning**: Self-adjusting anomaly thresholds (online learning)
- [ ] **Time-series forecasting**: Prophet-based cost/latency forecasts for capacity planning

---

## Advanced Topics

### Trace Context Propagation Across Services

For multi-service Git automation (merge → ML scoring → CI orchestration), traces must propagate context:

```python
# git-gitops-flow service
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextPropagator

tracer = trace.get_tracer(__name__)
propagator = TraceContextPropagator()

@app.post("/merge")
async def merge_pr(pr_id: int):
    ctx = trace.set_span_in_context(tracer.start_span("merge_operation"))
    
    # Extract trace context into headers
    carrier = {}
    propagator.inject(ctx, carrier)
    
    # Call ML scoring service with trace context
    ml_response = await http_client.post(
        "http://ml-service/score",
        headers=carrier,  # Propagate traceparent + tracestate
        json={"pr_id": pr_id}
    )
    
    return ml_response

# ml-scoring-service (receives trace context)
@app.post("/score")
async def score_merge(request):
    # Extract trace context from headers
    ctx = propagator.extract(request.headers)
    
    with trace.use_span(trace.set_span_in_context(
        tracer.start_span("ml_scoring", context=ctx)
    )):
        # ML inference in child span of merged operation
        confidence = await score_model(request.pr_data)
        return {"confidence": confidence}
```

### Metrics Export to Custom Systems

Export metrics to external monitoring systems (DataDog, New Relic, etc.):

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Export to any OTLP-compatible backend
otlp_exporter = OTLPMetricExporter(
    endpoint="https://otlp.datadog.com:443/v1/metrics",
    headers={
        "DD-API-KEY": os.getenv("DATADOG_API_KEY"),
        "DD-SERVICE": "git-evolution-suite",
        "DD-ENV": "prod"
    }
)

metrics.set_meter_provider(
    MeterProvider(metric_readers=[PeriodicExportingMetricReader(otlp_exporter)])
)
```

---

## Performance Optimization Techniques

### 1. Span Batching & Async Export

Avoid blocking merge operations on trace export:

```python
# Batch processor (default: max_queue_size=2048, max_export_batch_size=512)
from opentelemetry.sdk.trace.export import BatchSpanProcessor

batch_processor = BatchSpanProcessor(
    jaeger_exporter,
    max_queue_size=2048,        # Max pending spans
    schedule_delay_millis=5000, # Export every 5 seconds
    max_export_batch_size=512,  # Max spans per export
    export_timeout_millis=30000 # 30s timeout before force-flush
)
trace.get_tracer_provider().add_span_processor(batch_processor)
```

### 2. Metrics Aggregation Intervals

Export metrics every 10–60 seconds (not per-operation):

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

metrics_reader = PeriodicExportingMetricReader(
    prometheus_exporter,
    interval_millis=10000  # 10s export interval
)
```

### 3. Sampling Strategies (Future v1.1+)

For high-throughput scenarios, intelligent sampling reduces overhead:

```python
from opentelemetry.sdk.trace.sampling import ProbabilitySampler, ParentBased

# Sample based on parent span + probability
sampler = ParentBased(
    root=ProbabilitySampler(0.1),  # 10% of root spans (low-risk merges)
)

# Override: always sample high-risk merges
class RiskAwareSampler(Sampler):
    def should_sample(self, trace_id, span_name, span_kind, attributes, links, trace_state):
        if attributes.get("merge.risk_level") == "high":
            return True  # 100% sampling for high-risk
        if attributes.get("merge.cost_estimate_cents", 0) > 10:
            return True  # 100% sampling for expensive operations
        return random.random() < 0.05  # 5% sampling for low-risk
```

---

## Model Validation & Testing

### Unit Tests for Anomaly Detectors

```python
import unittest
from sklearn.ensemble import IsolationForest
import numpy as np

class TestAnomalyDetection(unittest.TestCase):
    def setUp(self):
        self.iso_forest = IsolationForest(contamination=0.02, random_state=42)
        # Normal latencies: ~4.7s ± 0.5s
        self.normal_data = np.random.normal(4700, 500, 1000).reshape(-1, 1)
        self.iso_forest.fit(self.normal_data)
    
    def test_normal_latency_not_anomaly(self):
        """Merges with ~4.7s latency should not be detected as anomaly"""
        normal_merge = np.array([[4800]])
        prediction = self.iso_forest.predict(normal_merge)
        self.assertEqual(prediction[0], 1)  # 1 = normal
    
    def test_spike_detected(self):
        """Merges with 12s latency should be detected as anomaly"""
        spike = np.array([[12000]])
        prediction = self.iso_forest.predict(spike)
        self.assertEqual(prediction[0], -1)  # -1 = anomaly
    
    def test_low_anomaly_score(self):
        """Anomaly scores should be in [-1.0, 0.5] range"""
        spike = np.array([[12000]])
        score = self.iso_forest.score_samples(spike)
        self.assertGreater(score[0], -1.0)
        self.assertLess(score[0], 0.5)

class TestMetricsExport(unittest.TestCase):
    def test_prometheus_metrics_queryable(self):
        """Prometheus scrape endpoint should return metrics"""
        response = requests.get("http://localhost:9090/api/v1/query", 
                              params={"query": "git_merge_success_total"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()["data"]["result"]), 0)
    
    def test_trace_in_jaeger(self):
        """New traces should appear in Jaeger within 30s"""
        # Trigger a merge
        merge_id = trigger_test_merge()
        
        # Poll Jaeger API
        time.sleep(5)  # Wait for batch export
        response = requests.get("http://localhost:16686/api/traces",
                              params={"service": "git-gitops-flow"})
        
        # Find trace by merge ID
        traces = response.json()["data"]
        found = any(merge_id in str(t) for t in traces)
        self.assertTrue(found, "Trace not found in Jaeger")
```

---

## Related Skills

- **git-gitops-flow** (v3.0): Use tracing in Phase 3 ML confidence scoring; ML inference tagged with latency
- **git-auto-merge-confidence** (v1.0): ML model outputs tagged with confidence, feature importance
- **git-multi-repo-workflows** (v3.0): Parallel execution spans correlate via trace_id
- **git-chaos-engineering** (v1.0): Chaos scenario outcomes correlated via traces
- **git-code-pattern-detection** (v3.0): Pattern feedback loops correlated with trace context
- **portal-gestao-manta**: Embed Cost Attribution dashboard (Dashboard 3) in project portal
- **manta-maestro**: Route observability questions to agente-gitops or DevOps team
- **context-guardian**: Use observability context for improved decision-making

---

## Invocation

From agente-gitops or any Manta agent:

```bash
/git-observability-stack --enable-tracing --anomaly-detection-enabled --export-format all
```

Or programmatically:

```python
result = skill("git-observability-stack", {
    "enable_tracing": True,
    "trace_sampling_rate": 1.0,
    "metrics_export_interval": 10,
    "jaeger_endpoint": "localhost:14250",
    "clickhouse_endpoint": "localhost:8123",
    "anomaly_detection_enabled": True,
    "alert_rules_config": "custom-alerts.yaml"
})

# Result contains:
# - Jaeger trace ID for latest merge
# - Grafana dashboard URLs (Git Analytics, ML Health, Cost, Anomalies)
# - Active alerts (8 rules, status of each)
# - Cost attribution (top repos, top authors, breakdown)
# - Anomaly detection status (Isolation Forest trained, DBSCAN calibrated)
# - SLO compliance report (merge latency p99, success rate, FP rate, CI success)
```

---

## Runbooks & Incident Response

### Runbook: High False Positive Rate Incident

**Trigger**: Alert `MergeFalsePositiveRateHigh` fires (FP rate > 3%)

**Steps**:

1. **Assess impact**:
   ```sql
   SELECT COUNT(*), AVG(ml.confidence) 
   FROM git_audit_logs 
   WHERE timestamp > now() - INTERVAL 1 hour 
   AND event = 'auto_merged' 
   AND false_positive = true;
   ```

2. **Root cause analysis**:
   - Check ML model version: `git logs --grep="model_version" | head -1`
   - Check recent training data: Wasserstein drift > 0.05?
   - Check feature importance: Which features changed most?

3. **Immediate action**:
   - Pause auto-merge: `git config --global merge.auto false`
   - Escalate all new PRs to human review
   - Notify ML team in Slack (#ml-platform)

4. **Investigation** (ML team):
   - Review false positives in last hour
   - Re-validate model on holdout test set
   - Check for data quality issues in recent merges

5. **Resolution**:
   - If model is stale: trigger retraining with latest data
   - If data is stale: pause feature collection, debug
   - Resume auto-merge only after FP rate < 2%

### Runbook: Post-Merge CI Failure Spike

**Trigger**: Alert `PostMergeCIFailure` fires (>5 failures in 30min)

**Steps**:

1. **Trace failed merges**:
   ```promql
   git_postmerge_ci_failures_total{stage="test"} 
   OFFSET 30m - git_postmerge_ci_failures_total{stage="test"}
   ```

2. **Identify common pattern**:
   - Same repo? → repo-specific CI config issue
   - Same file? → regression in specific module
   - Same author? → author's code quality issue
   - Different repos → infrastructure/flakiness issue

3. **Investigate via Jaeger**:
   - Find traces with `postmerge_ci_status="failed"`
   - Check span logs for error messages
   - Check resource utilization (CPU, memory) during failure

4. **Automatic actions**:
   - Rollback failed merges (transactional safety)
   - Alert infrastructure team if resource-constrained
   - Trigger chaos test to validate resilience

5. **Resolution**:
   - Fix root cause (CI config, code quality, infrastructure)
   - Re-run failed tests
   - Resume normal operations

---

## Support & Maintenance

**Questions / Issues:**
- Tag `@git-observability` in Slack (#git-evolution-suite channel)
- Create ticket: Jira project `MNT-OBSERVABILITY` (e.g., `MNT-OBS-47: Dashboard lag >1min`)
- Post-mortem templates: `RUNBOOK-INCIDENT-TRACE-ANALYSIS.md` (in SharePoint)

**Maintenance Schedule:**
- **Weekly**: Jaeger retention check (confirm <24h data available), alert false positive audit (should be <1% of alerts)
- **Monthly**: Model drift review (Wasserstein distance, PSI trends), cost anomaly analysis, SLO compliance report
- **Quarterly**: Trace sampling strategy review (consider 100% → 10% intelligent sampling), cardinality audit (check high-cardinality dimensions)
- **Semi-annual**: OTEL SDK upgrade (latest patch), ClickHouse schema optimization (TTL policy review, index rebuilds)

**Owned by**: Platform Engineering + Observability team (on-call rotation)  
**Last patch**: v1.0.0 (baseline, 2026-07-27)  
**Next review**: 2026-10-27 (quarterly)

**Contact**:
- Observability lead: @sarah-platform-eng (Slack)
- ML model owner: @mike-ml-team
- DevOps on-call: Pagerduty rotation (ml-observability-oncall)

---

**Version history:**
- **v1.0.0** (2026-07-27) — Initial release: 100% tracing with W3C TraceContext, 50+ metrics (deployment, ML, resource, cost), 4 Grafana dashboards, 8 alert rules with escalation policies, Isolation Forest + DBSCAN anomaly detection (70–115ms overhead, <5% relative), 24h Jaeger retention (expandable to 90d), deployment guide (6 phases), troubleshooting guide, unit tests, runbooks for high FP rate and CI failures. MCPs: Supabase (audit logs), Alertmanager (routing), Grafana (API), GitHub (enrichment). Tier: Sonnet.
