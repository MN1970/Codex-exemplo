# Manta Maestro Alert Rules Guide

Complete reference for 8 critical alert rules with escalation paths.

## Alert Rules Summary

| # | Alert Name | Severity | Threshold | Duration | Component |
|---|------------|----------|-----------|----------|-----------|
| 1 | PRMergeSuccessRateLow | CRITICAL | < 85% | 5m | Git/GitOps |
| 2 | MLInferenceLatencyHigh | CRITICAL | p99 > 2000ms | 5m | ML/AI |
| 3 | AnomaliesUnresolvedCritical | CRITICAL | > 5 count | 60m | Anomaly |
| 4 | CostSpikeCritical | CRITICAL | > 20% MoM | 5m | Business |
| 5 | MLModelAccuracyDrift | WARNING | > 5% drift | 10m | ML/AI |
| 6 | DBSCANMassiveDriftDetected | CRITICAL | > 100 size | 5m | Anomaly |
| 7 | CanaryRolloutStuck | WARNING | > 30 min | 5m | Deployment |
| 8 | JaegerSpanErrorRateHigh | CRITICAL | > 2% | 5m | Tracing |

---

## Alert Details

### ALERT 1: PRMergeSuccessRateLow

**Metric:** `manta_git_merge_success_rate < 0.85`

**Trigger Conditions:**
- Success rate drops below 85%
- Sustained for at least 5 minutes

**Root Causes:**
- Increased merge conflicts (code divergence)
- CI/CD pipeline failures (flaky tests, broken builds)
- Code review rejections (quality gates, security issues)
- Broken builds or dependency conflicts

**Response Steps:**
1. **Immediate (0-5 min):** Check recent commits in Grafana Git Analytics dashboard
2. **Investigation (5-30 min):**
   ```promql
   # Get failure reasons
   rate(manta_git_merge_failure_total{reason!=""}[1h])
   
   # Get success rate trend
   rate(manta_git_merge_success_total[1h]) / 
   (rate(manta_git_merge_success_total[1h]) + rate(manta_git_merge_failure_total[1h]))
   ```
3. **Remediation (30-60 min):**
   - If CI failures: Review recent CI pipeline changes, re-run failed tests
   - If conflicts: Implement stricter branching strategy or increase rebase frequency
   - If review rejections: Clarify code review standards with team

**Escalation Path:**
```
Alert fires (t=0)
  ↓
PagerDuty notification (t=1 min)
  ↓
On-call engineer assigned (t=5-15 min)
  ↓
Team Slack #manta-alerts notified (t=1 min)
  ↓
Engineering VP email (if unresolved > 30 min)
```

**SLA:** 15 min response, 1 hour resolution

---

### ALERT 2: MLInferenceLatencyHigh

**Metric:** `histogram_quantile(0.99, rate(manta_ml_inference_latency_ms_bucket[5m])) > 2000`

**Trigger Conditions:**
- 99th percentile latency exceeds 2 seconds
- Sustained for 5 minutes

**Root Causes:**
- Model size increased without optimization
- Resource contention (GPU/CPU exhaustion)
- Input feature complexity explosion
- Inference batch size too large
- Memory pressure causing GC pauses

**Response Steps:**
1. **Immediate (0-5 min):** Check Grafana ML Health dashboard
   ```promql
   # Check current latency percentiles
   histogram_quantile(0.50, rate(manta_ml_inference_latency_ms_bucket[1m]))
   histogram_quantile(0.95, rate(manta_ml_inference_latency_ms_bucket[1m]))
   histogram_quantile(0.99, rate(manta_ml_inference_latency_ms_bucket[1m]))
   ```

2. **Investigation (5-30 min):**
   - Check infrastructure metrics (CPU, memory, GPU)
   - Review recent model deployments
   - Check feature engineering overhead
   - Monitor request queue depth

3. **Quick Wins (5-15 min):**
   - Scale ML pod replicas 2x
   - Reduce batch size
   - Enable model quantization (fp32 → fp16)

4. **Long-term (if not resolved):**
   - Profile model inference
   - Optimize feature engineering
   - Consider model distillation

**Escalation Path:**
```
Alert fires (t=0)
  ↓
PagerDuty (ML on-call) (t=1 min)
  ↓
Auto-remediation: Scale pods 2x (t=2 min)
  ↓
If not resolved in 5 min → Slack #manta-ml + email
  ↓
Incident escalation if > 30 min unresolved
```

**SLA:** 15 min response, 30 min resolution target

---

### ALERT 3: AnomaliesUnresolvedCritical

**Metric:** `manta_anomaly_detection_unresolved_count > 5` for 60m

**Trigger Conditions:**
- More than 5 anomalies detected and unresolved
- Sustained for 1 hour (indicates systematic issue)

**Root Causes:**
- Actual production incident (latency spike, errors, resource exhaustion)
- Anomaly detection model overfitting (false positives)
- System configuration change causing metric distribution shift
- Cascade failure across multiple services

**Response Steps:**
1. **Immediate (0-10 min):** Check Grafana Anomalies dashboard
   ```promql
   # Get unresolved count by metric
   group by (metric_name) (manta_anomaly_detection_unresolved_count)
   
   # Get raw anomaly scores
   max(manta_anomaly_score)
   ```

2. **Assessment (10-20 min):**
   - Are anomalies true positives or false positives?
   - Check application logs for actual errors
   - Review recent deployments
   - Check infrastructure health

3. **Resolution:**
   - **If real issue:** Mitigate root cause (scale pods, fix bug, rollback deploy)
   - **If false positives:** Update anomaly detection thresholds or retrain model

**Escalation Path:**
```
Anomalies fire (t=0)
  ↓
Wait 60 minutes for self-resolution
  ↓
If still unresolved at t=60 min:
  ├→ PagerDuty (critical)
  ├→ Slack #manta-incident + @channel
  └→ Email to VP Engineering + team leads
```

**SLA:** Auto-resolution preferred within 60m, manual response required if not

---

### ALERT 4: CostSpikeCritical

**Metric:** `(manta_cost_monthly - (manta_cost_monthly offset 30d)) / (manta_cost_monthly offset 30d) > 0.2`

**Trigger Conditions:**
- Monthly cost increases > 20% month-over-month
- Sustained for 5 minutes

**Root Causes:**
- New deployments without cost optimization
- Runaway resource consumption (memory leak, infinite loop)
- Increased traffic beyond capacity
- Test environments accidentally left running
- Non-optimized Kubernetes resource requests

**Response Steps:**
1. **Immediate (0-5 min):** Review Grafana Cost Attribution dashboard
   ```promql
   # Cost by service
   sum by (service_name) (manta_cost_per_service_dollars)
   
   # Cost trend (daily)
   rate(manta_cost_monthly[1d])
   ```

2. **Investigation (5-30 min):**
   - Which service caused the spike?
   - When did it start?
   - Was there a deployment or config change?

3. **Remediation:**
   - Kill unnecessary resources
   - Right-size compute resources
   - Enable cost optimization (spot instances, reserved capacity)
   - Rollback problematic deployment

**Escalation Path:**
```
Alert fires (t=0)
  ↓
Slack #manta-finance + Finance team (t=1 min)
  ↓
PagerDuty (DevOps on-call) (t=2 min)
  ↓
Email to CFO if > 30% spike (t=1 min)
  ↓
Cost review meeting if > 50% spike
```

**SLA:** 15 min response, 2 hour resolution target

---

### ALERT 5: MLModelAccuracyDrift

**Metric:** `abs(manta_ml_model_accuracy - manta_ml_model_accuracy_baseline) > 0.05`

**Trigger Conditions:**
- Model accuracy drifts > 5% from 92.4% baseline
- Sustained for 10 minutes

**Root Causes:**
- Data distribution shift (new patterns in production data)
- Model overfitting
- Training/serving feature mismatch
- Regression in feature engineering
- Need for model retraining

**Response Steps:**
1. **Assessment (0-10 min):**
   ```promql
   # Check accuracy components
   manta_ml_model_precision
   manta_ml_model_recall
   manta_ml_model_f1_score
   ```

2. **Investigation (10-30 min):**
   - Which class is degrading (precision or recall)?
   - Check training logs for recent changes
   - Review feature importance changes
   - Analyze prediction distribution shift

3. **Remediation:**
   - If minor drift (94-93%): Monitor closely
   - If major drift (< 88%): Schedule model retraining
   - Consider rolling back to previous model version

**Escalation Path:**
```
Alert fires (t=0)
  ↓
Slack #manta-ml (warning level) (t=1 min)
  ↓
ML Engineering team email (t=1 min)
  ↓
If unresolved > 24h: Schedule retraining
```

**SLA:** Investigation within business hours, retraining within 24h

---

### ALERT 6: DBSCANMassiveDriftDetected

**Metric:** `manta_anomaly_dbscan_cluster_size > 100`

**Trigger Conditions:**
- Largest DBSCAN cluster exceeds 100 samples
- Indicates massive distribution shift in metrics
- Triggered immediately (< 1m)

**Root Causes:**
- Systemic failure affecting many services
- Major deployment with unexpected side effects
- Cascading failure across dependent services
- Sudden traffic surge or pattern change

**Response Steps:**
1. **IMMEDIATE (< 2 min):** This is an emergency signal
   - Page entire on-call team
   - Check Status page for customer-facing impact
   - Review recent deployments
   - Prepare rollback plan

2. **Investigation (2-10 min):**
   ```promql
   # Check all anomalies
   manta_anomaly_score
   
   # Check error rates
   manta_jaeger_span_error_rate
   
   # Check infrastructure
   manta_infrastructure_cpu_usage_percent
   ```

3. **Mitigation (10-30 min):**
   - Scale down or rollback problematic deployments
   - Increase resource capacity
   - Engage incident commander

**Escalation Path (IMMEDIATE):**
```
Alert fires (t=0)
  ↓
PagerDuty CRITICAL (all on-call) (t=0.5 min)
  ↓
Slack #manta-incident + @channel (t=0.5 min)
  ↓
Email VP Engineering + CTO (t=1 min)
  ↓
War room/incident bridge (t=5 min)
  ↓
Post-mortem (within 24h)
```

**SLA:** 5 min response, 15 min mitigation required

---

### ALERT 7: CanaryRolloutStuck

**Metric:** `time() - manta_canary_rollout_last_phase_change_timestamp > 1800`

**Trigger Conditions:**
- No phase progression for > 30 minutes
- Indicates deployment may be blocked

**Root Causes:**
- Phase success threshold not met
- Automated checks failing
- Waiting for manual approval
- Resource constraints preventing progression

**Response Steps:**
1. **Check Status (0-5 min):**
   ```promql
   # Check phase success rates
   manta_canary_phase_1_success_rate
   manta_canary_phase_2_success_rate
   manta_canary_phase_3_success_rate
   
   # Check phase duration
   manta_canary_phase_0_duration_minutes
   ```

2. **Assessment (5-15 min):**
   - Why is phase not progressing?
   - Are success criteria realistic?
   - Check logs for blocking errors

3. **Remediation:**
   - Manually approve phase progression if safe
   - Adjust success thresholds if too strict
   - Rollback if issues detected

**Escalation Path:**
```
Alert fires (t=0)
  ↓
Slack #manta-deployments (warning) (t=1 min)
  ↓
Email to DevOps team (t=1 min)
  ↓
Manual intervention (5-30 min)
  ↓
Post-deployment review (if rolled back)
```

**SLA:** 30 min investigation, 1 hour resolution

---

### ALERT 8: JaegerSpanErrorRateHigh

**Metric:** `manta_jaeger_span_error_rate > 0.02`

**Trigger Conditions:**
- More than 2% of spans have error status
- Sustained for 5 minutes

**Root Causes:**
- Application errors (unhandled exceptions, bugs)
- Downstream service failures
- Resource exhaustion
- Configuration errors
- Network/connectivity issues

**Response Steps:**
1. **Immediate (0-5 min):** Check Jaeger dashboard
   ```promql
   # Error rate by service
   manta_jaeger_span_error_rate
   
   # Error details
   jaeger_spans_total{span_status="error"}
   ```

2. **Investigation (5-15 min):**
   - Which services are erroring?
   - Error type and stack traces?
   - Recent code changes?
   - Check application logs

3. **Remediation:**
   - Deploy fix for error-causing code
   - Restart pods if transient error
   - Scale resources if capacity issue
   - Implement circuit breaker if downstream failure

**Escalation Path:**
```
Alert fires (t=0)
  ↓
PagerDuty (on-call engineer) (t=1 min)
  ↓
Slack #manta-observability (t=1 min)
  ↓
Application team email (t=2 min)
  ↓
If affecting customers: Incident commander
```

**SLA:** 15 min response, 1 hour resolution

---

## Alert Management Workflows

### Silence an Alert (Planned Maintenance)

```bash
# Via Alertmanager API
curl -X POST http://alertmanager:9093/api/v1/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "MLInferenceLatencyHigh"}],
    "startsAt": "2026-01-15T14:00:00Z",
    "endsAt": "2026-01-15T16:00:00Z",
    "createdBy": "devops-team",
    "comment": "Deploying ML model optimization"
  }'
```

### Create Incident from Alert

Each CRITICAL alert automatically creates a Jira incident:
- Title: Alert name
- Description: Alert annotations
- Assignee: On-call team
- Priority: P1 (critical)
- Links: Runbook, Dashboard

### Post-Mortem Template

After any CRITICAL alert:
1. **Timeline:** When did alert fire? When resolved?
2. **Impact:** How many users/services affected?
3. **Root Cause:** Why did it happen?
4. **Detection:** How quickly was it detected?
5. **Response:** What actions were taken?
6. **Resolution:** How was it fixed?
7. **Prevention:** What prevents recurrence?

---

## Testing Alerts

### Simulate Alert Conditions

```python
# Test MLInferenceLatencyHigh
from prometheus_client import Gauge, Histogram

latency = Histogram('manta_ml_inference_latency_ms', 'test')
for i in range(100):
    # Push value above 2000ms threshold
    latency.observe(2100)

# Test PRMergeSuccessRateLow
success = Counter('manta_git_merge_success_total', 'test')
failure = Counter('manta_git_merge_failure_total', 'test')
for i in range(20):
    failure.inc()  # 20 failures, 0 successes = 0% success rate
```

### Alert Silence Testing

```bash
# Create 1-hour silence for testing
curl -X POST http://alertmanager:9093/api/v1/silences \
  -d '{"matchers":[{"name":"alertname","value":"MLInferenceLatencyHigh"}],"endsAt":"2026-01-15T13:00:00Z"}'
```

---

## Integration Points

### PagerDuty
- Service: Manta-Maestro-Critical
- API Key: Stored in Secret `pagerduty-api-key`
- Routing: Escalation policies defined in PagerDuty console

### Slack
- Webhook: #manta-alerts channel
- Webhook: #manta-incident channel
- Webhook URLs in Secret `slack-webhooks`

### Email
- SMTP: smtp.gmail.com:587
- Credentials: Secret `smtp-credentials`
- Recipients: defined in AlertManager config

---

## Metrics for Alert Quality

Track alert effectiveness:
```promql
# Alert firing frequency
rate(manta_alert_firing_count[7d])

# Mean time to resolution (MTTR)
avg(manta_anomaly_resolution_time_minutes)

# False positive rate
(false_positive_alerts / total_alerts)
```
