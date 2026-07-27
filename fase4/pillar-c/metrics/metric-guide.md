# Manta Maestro Prometheus Metrics Guide

Complete reference for 50+ metrics across Git, ML, Infrastructure, Business, and Anomaly domains.

## Overview

Total Metrics: **50+** organized in 6 categories:
- Git/GitOps: 8 metrics
- ML/AI: 10 metrics
- Infrastructure: 8 metrics
- Business/Cost: 6 metrics
- Anomaly Detection: 10 metrics
- Canary/Performance: 12 metrics

---

## Git/GitOps Metrics (8)

### 1. manta_git_merge_success_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Labels:** branch, author
- **Description:** Cumulative count of successful PR merges
- **Alert threshold:** none (baseline)
- **Query example:** `increase(manta_git_merge_success_total[1h])`

### 2. manta_git_merge_failure_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Labels:** branch, reason (conflict, ci_failure, review_rejected)
- **Description:** Cumulative count of failed PR merges
- **Alert threshold:** > 5 failures per hour
- **Query example:** `increase(manta_git_merge_failure_total{reason="conflict"}[1h])`

### 3. manta_git_merge_success_rate
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Real-time PR merge success rate
- **Alert threshold:** < 0.85 for 5m
- **Calculation:** success_count / (success_count + failure_count)
- **Query example:** `rate(manta_git_merge_success_total[1h]) / (rate(manta_git_merge_success_total[1h]) + rate(manta_git_merge_failure_total[1h]))`

### 4. manta_git_pr_review_time_seconds
- **Type:** Histogram
- **Unit:** seconds
- **Buckets:** 60s, 5m, 15m, 30m, 1h, 2h
- **Description:** Time from PR creation to merge (includes review, CI, rework)
- **Alert threshold:** p95 > 3600s (1 hour)
- **Query examples:**
  - `histogram_quantile(0.95, manta_git_pr_review_time_seconds_bucket)` → p95 review time
  - `histogram_quantile(0.5, manta_git_pr_review_time_seconds_bucket)` → median review time

### 5. manta_git_conflict_resolution_time_seconds
- **Type:** Histogram
- **Unit:** seconds
- **Buckets:** 60s, 5m, 15m, 30m, 1h, 2h
- **Description:** Time spent resolving merge conflicts per PR
- **Alert threshold:** > 7200s (2 hours) for any single conflict
- **Labels:** conflict_type (simple, complex, data)

### 6. manta_git_commit_size_lines
- **Type:** Histogram
- **Unit:** lines of code
- **Buckets:** 10, 50, 100, 500, 1000, 5000
- **Description:** Size of each commit (lines changed: added + removed)
- **Alert threshold:** none (informational; track as quality metric)
- **Query example:** `histogram_quantile(0.95, manta_git_commit_size_lines_bucket)` → p95 commit size

### 7. manta_git_ci_duration_seconds
- **Type:** Histogram
- **Unit:** seconds
- **Buckets:** 30s, 1m, 2m, 5m, 10m, 20m
- **Description:** End-to-end CI/CD pipeline execution time
- **Alert threshold:** p99 > 1200s (20 minutes)
- **Labels:** pipeline_stage (build, test, deploy, validation)

### 8. manta_git_author_commits_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Labels:** author, repository
- **Description:** Commits authored by each developer
- **Alert threshold:** none (used for productivity analytics)
- **Query example:** `topk(10, increase(manta_git_author_commits_total[7d]))` → top 10 contributors

---

## ML/AI Metrics (10)

### 9. manta_ml_model_accuracy
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Current ML model accuracy on validation set
- **Alert threshold:** < 0.88 (5% drift from 92.4% baseline)
- **Update frequency:** Every training cycle (weekly)

### 10. manta_ml_model_accuracy_baseline
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Baseline accuracy for drift detection (92.4%)
- **Purpose:** Detect model degradation
- **Labels:** model_name, version

### 11. manta_ml_model_precision
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** False positive rate metric
- **Target:** ≥ 0.92 (92% of positive predictions correct)

### 12. manta_ml_model_recall
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** False negative rate metric
- **Target:** ≥ 0.88 (88% of true positives detected)

### 13. manta_ml_model_f1_score
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Harmonic mean of precision and recall
- **Formula:** 2 * (precision * recall) / (precision + recall)
- **Target:** ≥ 0.90

### 14. manta_ml_inference_latency_ms
- **Type:** Histogram
- **Unit:** milliseconds
- **Buckets:** 10ms, 50ms, 100ms, 500ms, 1s, 2s
- **Description:** Real-time inference latency per request
- **Alert threshold:** p99 > 2000ms
- **Labels:** model_id, input_size_bytes

### 15. manta_ml_training_duration_hours
- **Type:** Histogram
- **Unit:** hours
- **Buckets:** 0.5h, 1h, 2h, 4h, 8h, 24h
- **Description:** Time required to train or retrain model
- **Update frequency:** Weekly
- **Labels:** training_type (initial, retraining, tuning)

### 16. manta_ml_feature_importance
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Top 10 feature importance scores from XGBoost
- **Labels:** feature_name, feature_rank (1-10)
- **Query example:** `topk(10, manta_ml_feature_importance)` → top features

### 17. manta_ml_predictions_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Labels:** model_id, prediction_class
- **Description:** Cumulative predictions made by models
- **Query example:** `rate(manta_ml_predictions_total[1h])` → prediction throughput

### 18. manta_ml_training_loss
- **Type:** Gauge
- **Unit:** 0-1+ (varies by loss function)
- **Description:** Training loss during model training
- **Update frequency:** Per training epoch
- **Labels:** epoch, dataset_type (train, validation)

---

## Infrastructure Metrics (8)

### 19. manta_infrastructure_cpu_usage_percent
- **Type:** Gauge
- **Unit:** % (0-100)
- **Description:** CPU utilization of pods
- **Alert threshold:** > 80% sustained for 5m
- **Labels:** namespace, pod_name, container_name

### 20. manta_infrastructure_memory_usage_mb
- **Type:** Gauge
- **Unit:** MB
- **Description:** Memory consumption (RSS)
- **Alert threshold:** > 90% of limit

### 21. manta_infrastructure_memory_limit_mb
- **Type:** Gauge
- **Unit:** MB
- **Description:** Kubernetes memory request/limit
- **Labels:** namespace, pod_name

### 22. manta_infrastructure_disk_io_operations_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Description:** Total disk I/O operations (reads + writes)
- **Labels:** node, device, operation_type (read, write)

### 23. manta_infrastructure_disk_io_latency_ms
- **Type:** Histogram
- **Unit:** ms
- **Buckets:** 1ms, 5ms, 10ms, 50ms, 100ms
- **Description:** Disk I/O operation latency
- **Alert threshold:** p99 > 50ms

### 24. manta_infrastructure_network_throughput_mbps
- **Type:** Gauge
- **Unit:** Mbps
- **Description:** Network bandwidth utilization
- **Alert threshold:** > 80% of capacity
- **Labels:** interface, direction (ingress, egress)

### 25. manta_infrastructure_pod_restarts_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Description:** Total pod restart events
- **Alert threshold:** > 3 restarts per 24h
- **Labels:** namespace, pod_name, reason (OOMKilled, CrashLoop, Evicted)

### 26. manta_infrastructure_container_build_duration_seconds
- **Type:** Histogram
- **Unit:** s
- **Buckets:** 30s, 1m, 2m, 5m, 10m
- **Description:** Docker/container image build time
- **Alert threshold:** p95 > 600s (10 min)

---

## Business/Cost Metrics (6)

### 27. manta_cost_per_merge_dollars
- **Type:** Gauge
- **Unit:** $ (USD)
- **Description:** Infrastructure cost divided by successful merges
- **Calculation:** (hourly_infra_cost / merges_this_hour) for each hour
- **Target:** < $50 per merge

### 28. manta_roi_per_feature
- **Type:** Gauge
- **Unit:** 1+ (unitless ratio)
- **Description:** Revenue impact per shipped feature
- **Calculation:** (business_value_achieved / feature_cost)
- **Target:** > 1.5 ROI (50% return)

### 29. manta_velocity_merges_per_day
- **Type:** Gauge
- **Unit:** 1 (count)
- **Description:** Daily merge throughput
- **Calculation:** count of merges in past 24h
- **Baseline:** 20 merges/day (historical)
- **Alert threshold:** < 10 merges/day (50% drop)

### 30. manta_cost_monthly
- **Type:** Gauge
- **Unit:** $ (USD)
- **Description:** Total monthly infrastructure cost
- **Update frequency:** Daily
- **Labels:** cost_category (compute, storage, network, services)

### 31. manta_cost_per_service_dollars
- **Type:** Gauge
- **Unit:** $ (USD)
- **Description:** Monthly cost breakdown per microservice
- **Labels:** service_name (jaeger, prometheus, grafana, clickhouse, etc)
- **Query example:** `sum by (service_name) (manta_cost_per_service_dollars)` → total cost

### 32. manta_feature_deployment_time_days
- **Type:** Histogram
- **Unit:** days
- **Buckets:** 0.5d, 1d, 3d, 7d, 14d, 30d
- **Description:** Time from feature branch creation to production merge
- **Alert threshold:** p95 > 14 days (2 weeks)

---

## Anomaly Detection Metrics (10)

### 33. manta_anomaly_detection_latency_ms
- **Type:** Histogram
- **Unit:** ms
- **Buckets:** 10ms, 50ms, 100ms, 500ms, 1s
- **Description:** Latency of anomaly detection inference (Isolation Forest + DBSCAN)
- **Target:** p99 < 1000ms
- **Labels:** model_type (isolation_forest, dbscan)

### 34. manta_anomaly_score
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Isolation Forest anomaly score per metric
- **Interpretation:**
  - 0.0-0.2: Normal
  - 0.2-0.5: Mild anomaly
  - 0.5-0.8: Moderate anomaly
  - 0.8-1.0: Severe anomaly
- **Labels:** metric_name

### 35. manta_pattern_quality_score
- **Type:** Gauge
- **Unit:** 0-100
- **Description:** Quality score of detected patterns after feedback loop
- **Update frequency:** Weekly (after pattern retraining)
- **Labels:** pattern_id, pattern_type (latency_spike, gradual_drift, etc)

### 36. manta_canary_rollout_progress_percent
- **Type:** Gauge
- **Unit:** % (0-100)
- **Description:** Canary deployment progress
- **Values:**
  - 0-25: Phase 0 (Audit)
  - 25-50: Phase 1 (5 low-risk at 95%)
  - 50-75: Phase 2 (10 medium at 90%)
  - 75-100: Phase 3 (full at 75%)

### 37. manta_anomaly_detection_unresolved_count
- **Type:** Gauge
- **Unit:** 1 (count)
- **Description:** Number of anomalies awaiting resolution
- **Alert threshold:** > 5 unresolved for 1h
- **Update frequency:** Real-time

### 38. manta_anomaly_dbscan_cluster_size
- **Type:** Gauge
- **Unit:** 1 (count)
- **Description:** Size of largest DBSCAN cluster (drift indicator)
- **Interpretation:**
  - < 10: Normal clustering
  - 10-50: Moderate drift
  - 50-100: Significant drift
  - > 100: CRITICAL drift detected
- **Alert threshold:** > 100 (immediate escalation)

### 39. manta_canary_rollout_last_phase_change_timestamp
- **Type:** Gauge
- **Unit:** Unix seconds
- **Description:** When the canary last progressed to next phase
- **Alert threshold:** if (now - value) > 1800s (30 min stuck)
- **Query:** `time() - manta_canary_rollout_last_phase_change_timestamp > 1800`

### 40. manta_jaeger_span_error_rate
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Percentage of spans with error status
- **Alert threshold:** > 0.02 (2%)
- **Calculation:** error_spans / total_spans

### 41. manta_anomaly_isolation_forest_detections_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Description:** Cumulative anomalies detected by Isolation Forest
- **Labels:** metric_name, severity (low, medium, high)

### 42. manta_anomaly_dbscan_drift_detections_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Description:** Cumulative drift events detected by DBSCAN
- **Labels:** drift_type, magnitude

---

## Canary/Deployment Metrics (8)

### 43-46. manta_canary_phase_X_success_rate
- **Type:** Gauge
- **Unit:** 0-1 (fraction)
- **Description:** Success rate per canary phase
- **Phases:**
  - Phase 0: Audit (100% success required)
  - Phase 1: 5 low-risk services at 95% threshold
  - Phase 2: 10 medium-risk at 90% threshold
  - Phase 3: Full deployment at 75% threshold

### 47. manta_canary_rollback_count_total
- **Type:** Counter
- **Unit:** 1 (count)
- **Description:** Total number of canary rollbacks
- **Labels:** phase, reason (success_threshold_miss, timeout, manual_trigger)

### 48. manta_span_processing_latency_ms
- **Type:** Histogram
- **Unit:** ms
- **Buckets:** 1ms, 5ms, 10ms, 50ms, 100ms, 500ms
- **Description:** Jaeger span ingestion and processing latency
- **Target:** p99 < 100ms

### 49. manta_span_ingestion_rate_per_second
- **Type:** Gauge
- **Unit:** spans/sec
- **Description:** Real-time span ingestion rate into Jaeger
- **Baseline:** 1000-2000 spans/sec

### 50. manta_alert_firing_count
- **Type:** Gauge
- **Unit:** 1 (count)
- **Description:** Number of currently active/firing alerts
- **Alert threshold:** > 3 firing simultaneously
- **Labels:** severity (info, warning, critical)

---

## Query Examples & Dashboards

### Key Performance Indicators (KPIs)

```promql
# Merge velocity
rate(manta_git_merge_success_total[1h])

# ML model health
manta_ml_model_accuracy / manta_ml_model_accuracy_baseline

# Cost efficiency
manta_cost_per_merge_dollars

# Anomaly health (low is good)
avg(manta_anomaly_score)

# Deployment success
manta_canary_phase_3_success_rate
```

### SLO Compliance

```promql
# 99.5% of merges succeed
(sum(rate(manta_git_merge_success_total[30d])) /
 (sum(rate(manta_git_merge_success_total[30d])) +
  sum(rate(manta_git_merge_failure_total[30d])))) > 0.995

# 95% of inferences < 500ms
histogram_quantile(0.95, rate(manta_ml_inference_latency_ms_bucket[5m])) < 500

# Anomalies resolved within 1 hour
avg(manta_anomaly_detection_unresolved_count) < 3
```

---

## Units & Naming Conventions

- **Counters:** `_total` suffix (always increasing)
- **Gauges:** No suffix (can go up/down)
- **Histograms:** `_bucket`, `_count`, `_sum` suffixes (auto-generated)
- **Time:** Always seconds in base unit (`_seconds`), ms where specified (`_ms`)
- **Money:** Always dollars (`_dollars`)
- **Rates:** Per second (`_per_second`) or per day (`_per_day`)

---

## Integration with Alertmanager

All metrics feed into Prometheus AlertManager with thresholds defined in `/pillar-c/k8s/prometheus/prometheus-rules.yaml`.

Critical alerts (severity: critical):
- PR merge success rate < 85%
- ML inference latency p99 > 2000ms
- DBSCAN cluster size > 100 (massive drift)
- Unresolved anomalies > 5 for 1h

Warning alerts (severity: warning):
- PR review time p95 > 1h
- Cost spike > 20% month-over-month
- Canary phase stuck > 30m
- Jaeger error rate > 2%
