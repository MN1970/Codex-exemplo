# Troubleshooting Guide: 10 Common Issues & Runbooks

Diagnostic procedures and remediation steps for Manta Maestro Observability stack issues.

---

## Issue 1: Jaeger Not Ingesting Spans

**Symptoms:** Jaeger UI shows no services or traces, despite applications sending data

**Diagnosis:**

```bash
# Check Jaeger pod status
kubectl get pods -n observability -l app=jaeger -o wide
kubectl logs -n observability deployment/jaeger | tail -50

# Check OTLP port exposure
kubectl get svc -n observability jaeger -o yaml | grep -A 10 "ports:"

# Verify connectivity from application
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -v telnet://jaeger:4317 2>&1 | grep -i connect

# Check resource limits
kubectl top pods -n observability -l app=jaeger
kubectl describe pod -n observability deployment/jaeger | grep -A 5 "Limits"
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Jaeger pod crashed** | `kubectl restart -n observability deployment/jaeger` |
| **OTLP port blocked** | Edit `k8s/jaeger/jaeger-service.yaml`, verify port 4317 is exposed |
| **Application not exporting** | Check app logs: `service_name` not set or exporter not initialized |
| **Network policy blocking** | List: `kubectl get networkpolicies -n observability`; Allow OTLP traffic |
| **Resource limit hit (OOM)** | Increase memory in `jaeger-deployment.yaml` (currently 1Gi) |

**Resolution Steps:**

```bash
# 1. Restart Jaeger
kubectl rollout restart -n observability deployment/jaeger
kubectl wait --for=condition=ready pod -l app=jaeger -n observability --timeout=60s

# 2. Verify logs
kubectl logs -n observability deployment/jaeger | grep -i "error\|warn"

# 3. Check OTLP connectivity
kubectl port-forward -n observability svc/jaeger 4317:4317 &
curl -I http://localhost:4317

# 4. If still broken, inspect YAML
kubectl get configmap -n observability jaeger-config -o yaml

# 5. Restart with new config
kubectl rollout restart -n observability deployment/jaeger
```

---

## Issue 2: ClickHouse Query Timeout

**Symptoms:** ` Timeout waiting for ClickHouse response, trace queries slow, query execution > 5 seconds

**Diagnosis:**

```bash
# Check ClickHouse pod status
kubectl get pods -n observability -l app=clickhouse -o wide
kubectl logs -n observability deployment/clickhouse | tail -20

# Check resource usage
kubectl top pods -n observability -l app=clickhouse

# Test direct connectivity
kubectl port-forward -n observability svc/clickhouse 9000:9000 &
clickhouse-client --host localhost --port 9000 --query "SELECT 1"

# Check table sizes
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "SELECT table, formatReadableSize(sum(bytes)) \
    FROM system.parts WHERE database='otel_traces' GROUP BY table"

# Check slow queries log
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "SELECT query_duration_ms, query \
    FROM system.query_log ORDER BY query_start_time DESC LIMIT 10"
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **High query complexity** | Use time-range filter: `timestamp > now() - INTERVAL 1 DAY` |
| **Disk I/O bottleneck** | Scale ClickHouse PVC (PVC must be on fast storage) |
| **Memory pressure** | Increase `memory_limit` in ClickHouse config (~2Gi) |
| **Slow table scans** | Add indexes on `(timestamp, trace_id)` |
| **Expired trace data** | TTL cleanup too aggressive; extend to 45d |

**Resolution Steps:**

```bash
# 1. Increase memory limit
kubectl set env -n observability deployment/clickhouse \
  MAX_MEMORY_USAGE=2000000000

# 2. Optimize query: use time-based filtering
# FROM otel_traces.otel_traces WHERE timestamp > now() - INTERVAL 1 DAY

# 3. Check disk space
kubectl exec -it -n observability deployment/clickhouse -- \
  df -h /var/lib/clickhouse

# 4. If disk full, scale PVC
kubectl patch pvc -n observability clickhouse-data \
  -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 5. Restart ClickHouse
kubectl rollout restart -n observability deployment/clickhouse
```

---

## Issue 3: Prometheus High Memory Usage

**Symptoms:** Prometheus memory climbing over time, pod approaching OOM limit, scrapes slowing down

**Diagnosis:**

```bash
# Check memory trend
kubectl top pods -n observability -l app=prometheus

# Check target count
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Check database size
kubectl exec -it -n observability deployment/prometheus -- du -sh /prometheus

# Check cardinality (series count)
curl -s 'http://localhost:9090/api/v1/query?query=count(up)' | jq '.data.result'

# Check wal directory
kubectl exec -it -n observability deployment/prometheus -- du -sh /prometheus/wal/
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **High metric cardinality** | Remove high-cardinality labels; use relabel_configs to drop labels |
| **Long retention time** | Reduce `--storage.tsdb.retention.time` (default 30d) |
| **Too many scrape targets** | Filter targets with `relabel_configs` in prometheus.yml |
| **Memory leak in Prometheus** | Restart pod weekly via cronjob |
| **WAL (write-ahead log) too large** | Increase `--storage.tsdb.max-block-duration` |

**Resolution Steps:**

```bash
# 1. Check high-cardinality metrics
curl -s 'http://localhost:9090/api/v1/label/__name__/values' | \
  jq '.data[] | select(length > 20)' | head

# 2. Remove problematic high-cardinality metric
# Edit prometheus-configmap.yaml, add metric_relabel_configs to drop

# 3. Restart Prometheus
kubectl rollout restart -n observability deployment/prometheus

# 4. Reduce retention (if needed)
kubectl patch deployment -n observability prometheus --type json -p \
  '[{"op":"replace","path":"/spec/template/spec/containers/0/args/2","value":"--storage.tsdb.retention.time=7d"}]'

# 5. Monitor new memory usage
kubectl top pods -n observability -l app=prometheus -w
```

---

## Issue 4: Grafana Dashboards Not Loading

**Symptoms:** 404 errors when accessing dashboards, panels show "No data", datasource connection refused

**Diagnosis:**

```bash
# Check Grafana pod
kubectl logs -n observability deployment/grafana | grep -i error

# Verify datasource connectivity
kubectl exec -it -n observability deployment/grafana -- \
  curl -s http://prometheus:9090/-/healthy

# Check datasource configuration
curl -s 'http://localhost:3000/api/datasources' | jq '.[] | {name, url}'

# List dashboards
curl -s 'http://localhost:3000/api/search?query=&starred=false' | jq '.[] | {id, title, uid}'

# Check dashboard JSON for errors
curl -s 'http://localhost:3000/api/dashboards/db/git-analytics' | jq '.dashboard | {title, uid}'
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Datasource unreachable** | Verify Prometheus/Jaeger services are running |
| **Wrong datasource URL** | Use service DNS: `http://prometheus:9090` (not localhost) |
| **Dashboard UID conflict** | Remove conflicting dashboard, re-import with new UID |
| **Expired auth token** | Logout and re-login, generate new API token |
| **PVC disk full** | Check Grafana storage: `kubectl exec -it -n observability deployment/grafana -- du -sh /var/lib/grafana` |

**Resolution Steps:**

```bash
# 1. Verify datasources
curl -H "Authorization: Bearer $(cat /run/secrets/grafana-token)" \
  'http://localhost:3000/api/datasources' | jq '.[] | {name, .url, status}'

# 2. Fix datasource URL if needed
curl -X PUT -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"url":"http://prometheus:9090"}' \
  'http://localhost:3000/api/datasources/1'

# 3. Re-import dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d @grafana-dashboards/git-analytics.json

# 4. Clear Grafana cache
kubectl exec -it -n observability deployment/grafana -- \
  rm -rf /var/lib/grafana/cache/*

# 5. Restart Grafana
kubectl rollout restart -n observability deployment/grafana
```

---

## Issue 5: Alerts Not Firing (Alert Rules Misconfigured)

**Symptoms:** Expected alerts don't fire, Prometheus shows alert rule errors, no webhook notifications

**Diagnosis:**

```bash
# Check Prometheus alert status
curl -s 'http://localhost:9090/api/v1/rules' | jq '.data.groups[].rules[] | {name: .alert, state: .state}'

# Look for rule errors
curl -s 'http://localhost:9090/api/v1/rules' | jq '.data.groups[].rules[] | select(.health != "ok") | {name: .alert, health: .health, lastError: .lastError}'

# Validate rule YAML syntax
promtool check rules k8s/prometheus/prometheus-rules.yaml

# Check Alertmanager status
curl -s 'http://localhost:9093/api/v1/alerts' | jq '.data'

# Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts -d '[{
  "labels":{"alertname":"TestAlert","severity":"critical"},
  "annotations":{"summary":"Test"},
  "generatorURL":"http://prometheus:9090"
}]'
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Invalid PromQL expression** | Validate with `promtool check rules` or Prometheus UI |
| **Metric name typo** | Check metric exists: `curl http://prometheus:9090/api/v1/query?query=manta_metric_name` |
| **Alertmanager misconfigured** | Check config: `kubectl get configmap -n observability alertmanager-config -o yaml` |
| **Webhook URL invalid** | Test Slack/PagerDuty webhooks manually |
| **Rule eval interval too long** | Edit rule `interval` (default 30s) |

**Resolution Steps:**

```bash
# 1. Validate rule syntax
promtool check rules k8s/prometheus/prometheus-rules.yaml

# 2. Fix any syntax errors in rules
kubectl edit configmap -n observability prometheus-rules

# 3. Reload Prometheus (uses web API)
curl -X POST http://localhost:9090/-/reload

# 4. Verify rule loaded
curl -s 'http://localhost:9090/api/v1/rules?type=alert' | \
  jq '.data.groups[] | {name, rules: (.rules | map(.alert))}'

# 5. Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"PRMergeSuccessRateLow"},"generatorURL":"test"}]'

# 6. Restart Alertmanager if config changed
kubectl rollout restart -n observability deployment/alertmanager
```

---

## Issue 6: Anomaly Detector Models Not Trained / Failing

**Symptoms:** Anomaly scorer crashes, models not found, `FileNotFoundError: models/isolation_forest.pkl`

**Diagnosis:**

```bash
# Check if models exist
ls -lh /home/user/Codex-exemplo/fase4/pillar-c/ml-anomaly/models/

# Check model training logs
cat ml-anomaly/training.log

# Run anomaly scorer manually
cd ml-anomaly
python -c "from isolation_forest_model import train_and_save_model; train_and_save_model()"

# Check model size
du -sh ml-anomaly/models/*

# Verify model integrity
python -c "import pickle; m = pickle.load(open('ml-anomaly/models/isolation_forest.pkl', 'rb')); print(m.n_estimators)"
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Models not trained** | Run training script: `python isolation_forest_model.py` |
| **Corrupted pickle files** | Delete and retrain: `rm models/*.pkl && python isolation_forest_model.py` |
| **Dependencies missing** | Install: `pip install -r requirements.txt` |
| **Prometheus URL wrong** | Set env var: `export PROMETHEUS_URL=http://prometheus:9090` |
| **Insufficient training data** | Check Prometheus has metrics: `curl http://prometheus:9090/api/v1/targets` |

**Resolution Steps:**

```bash
# 1. Install dependencies
cd ml-anomaly
pip install -r requirements.txt

# 2. Train models
python isolation_forest_model.py
python dbscan_model.py

# 3. Verify models created
ls -lh models/

# 4. Test inference
python -c "
from isolation_forest_model import IsolationForestAnomalyDetector
from feature_engineering import AnomalyFeatureExtractor
import numpy as np

detector = IsolationForestAnomalyDetector(model_path='models/isolation_forest.pkl')
detector.load_model()
test_data = AnomalyFeatureExtractor.create_synthetic_normal_data(10)
test_data = AnomalyFeatureExtractor.normalize_features(test_data)
preds, scores = detector.predict(test_data)
print(f'Predictions: {preds}')
print(f'Scores: {scores}')
"

# 5. Start anomaly scorer
python anomaly_scorer.py
```

---

## Issue 7: High Cardinality Metrics Causing Prometheus Issues

**Symptoms:** Prometheus memory spike, slow queries, `metric_relabel_configs` not working

**Diagnosis:**

```bash
# Find high-cardinality metrics
curl -s 'http://localhost:9090/api/v1/query?query=topk(20, count by (__name__) ({{__name__=~".+"}}))' | \
  jq '.data.result[] | {metric: .metric.__name__, cardinality: .value[1]}'

# Check specific metric cardinality
curl -s 'http://localhost:9090/api/v1/label/pod_name/values' | jq '.data | length'

# List all label names
curl -s 'http://localhost:9090/api/v1/labels' | jq '.data[] | select(length > 3)'
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Pod/container labels with unique IDs** | Drop via `metric_relabel_configs` |
| **Timestamp labels** | Remove with relabel rules before scrape |
| **Dynamic labels from application** | Use `drop` action in scrape config |

**Resolution:**

```bash
# 1. Edit Prometheus config
kubectl edit configmap -n observability prometheus-config

# 2. Add metric_relabel_configs to drop high-cardinality labels
# Example:
metric_relabel_configs:
  - source_labels: [__name__]
    regex: "manta_custom_metric"
    action: drop

# 3. Reload Prometheus
curl -X POST http://localhost:9090/-/reload

# 4. Verify cardinality dropped
curl -s 'http://localhost:9090/api/v1/query?query=count(count by(__name__)({__name__=~".+"}))' | jq '.data.result[0].value[1]'
```

---

## Issue 8: Trace Storage Growing Too Fast (ClickHouse Disk Full)

**Symptoms:** ClickHouse PVC filling up, TTL cleanup not working, `out of disk space` errors

**Diagnosis:**

```bash
# Check disk usage
kubectl exec -it -n observability deployment/clickhouse -- df -h /var/lib/clickhouse

# Check table sizes
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "SELECT table, formatReadableSize(sum(bytes)) \
    FROM system.parts WHERE database='otel_traces' GROUP BY table"

# Check TTL status
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "SHOW CREATE TABLE otel_traces.otel_traces"

# Check retention policy
kubectl get configmap -n observability clickhouse-config -o yaml | grep -i ttl
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **TTL too long (30 days)** | Reduce to 14-21 days |
| **Trace volume too high** | Reduce Jaeger sampling rate (default 10%) |
| **PVC too small** | Scale storage (see Issue 2) |
| **TTL cleanup not running** | Restart ClickHouse: `kubectl restart -n observability deployment/clickhouse` |

**Resolution Steps:**

```bash
# 1. Check current TTL
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "SELECT * FROM system.tables WHERE name='otel_traces'"

# 2. Update TTL (reduce from 30d to 14d)
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "ALTER TABLE otel_traces.otel_traces \
    MODIFY TTL timestamp + INTERVAL 14 DAY"

# 3. Trigger manual cleanup
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client --query "OPTIMIZE TABLE otel_traces.otel_traces FINAL"

# 4. Reduce Jaeger sampling rate
kubectl edit configmap -n observability jaeger-config
# Change: param: 0.05  (5% instead of 10%)

# 5. Restart services
kubectl rollout restart -n observability deployment/jaeger
```

---

## Issue 9: Network Connectivity Problems (Services Can't Reach Each Other)

**Symptoms:** Connection refused errors, services timeout, `Unable to connect to Prometheus`

**Diagnosis:**

```bash
# Check service DNS resolution
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  nslookup prometheus.observability.svc.cluster.local

# Check network policies
kubectl get networkpolicies -n observability

# Test connectivity between pods
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  /bin/sh -c 'nc -zv prometheus.observability.svc.cluster.local 9090'

# Check service endpoints
kubectl get endpoints -n observability

# Check DNS in pod
kubectl exec -it -n observability deployment/grafana -- \
  cat /etc/resolv.conf
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Network policy blocking traffic** | Check: `kubectl get networkpolicies -n observability` |
| **Service not found (DNS issue)** | Verify service exists: `kubectl get svc -n observability` |
| **Pod IP not in endpoint** | Check pod status: `kubectl describe pod -n observability prometheus-xxx` |
| **Firewall rules** | Check node security groups / firewall rules |

**Resolution:**

```bash
# 1. Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -v http://prometheus.observability.svc.cluster.local:9090/api/v1/query?query=up

# 2. If blocked by network policy, remove temporarily
kubectl delete networkpolicies -n observability --all

# 3. Re-apply policies if needed
kubectl apply -f network-policies.yaml

# 4. Verify endpoints
kubectl get endpoints -n observability -o wide

# 5. Restart pods that failed to initialize
kubectl rollout restart -n observability deployment/grafana
```

---

## Issue 10: Slow Dashboard Performance / Query Timeout

**Symptoms:** Grafana dashboards slow to load (> 5s), panel queries timeout, CPU 100%

**Diagnosis:**

```bash
# Check Prometheus query performance
curl -s 'http://localhost:9090/api/v1/query_log' | \
  jq '.[] | select(.query_duration_ms > 5000) | {query, duration_ms: .query_duration_ms}' | head

# Check Prometheus CPU
kubectl top pods -n observability -l app=prometheus

# Analyze slow PromQL queries
curl -s 'http://localhost:9090/api/v1/tsdb/series' -d 'match[]=manta_git_pr_review_time_seconds_bucket' | \
  jq '.data | length'  # Series count for single metric

# Check time range of queries
# Look at Grafana dashboard requests in browser DevTools → Network tab
```

**Root Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| **Query scanning too much data** | Reduce time range in dashboard (e.g., 7d instead of 30d) |
| **Missing rate() function** | Use `rate()` for counters: `rate(metric_total[5m])` |
| **High-cardinality labels** | See Issue 7; drop unnecessary labels |
| **Joins across large series** | Use `group_left()` with filtering |
| **Prometheus resource-limited** | Scale resources: `kubectl set resources -n observability deployment/prometheus --limits=cpu=2,memory=4Gi` |

**Resolution:**

```bash
# 1. Optimize PromQL queries in dashboards
# Before: manta_git_merge_success_total
# After: rate(manta_git_merge_success_total[5m])

# 2. Edit Grafana dashboard
curl -X GET http://localhost:3000/api/dashboards/db/git-analytics | \
  jq '.dashboard.panels[].targets[].expr' | \
  head -5

# 3. Update slow panels to use better queries
# Use smaller time ranges: `[7d]` instead of `[30d]`

# 4. Scale Prometheus if needed
kubectl set resources -n observability deployment/prometheus \
  --limits=cpu=2,memory=4Gi \
  --requests=cpu=500m,memory=2Gi

# 5. Add dashboard variable for time range filter
# Example: `offset 24h` to limit lookback window
```

---

## General Troubleshooting Commands

```bash
# View all observability pods
kubectl get pods -n observability -o wide

# Restart all services
kubectl rollout restart -n observability deployment

# Get all events (errors)
kubectl get events -n observability --sort-by='.lastTimestamp'

# Check resource limits
kubectl describe nodes | grep -A 5 "Allocated resources"

# Export pod logs for debugging
kubectl logs -n observability deployment/prometheus > prometheus.log

# Access pod shell
kubectl exec -it -n observability deployment/prometheus -- /bin/bash

# Check PVC status
kubectl get pvc -n observability

# Describe specific resource
kubectl describe deployment -n observability prometheus
```

---

## Escalation Procedures

If issues persist after troubleshooting:

1. **Collect diagnostics:**
   ```bash
   kubectl get all -n observability > observability-state.txt
   kubectl logs -n observability --all-containers=true deployment > observability.log
   ```

2. **Contact support:** Share logs + observability-state.txt with #manta-observability team

3. **Emergency contact:** page on-call engineer if production impact

---

**Last Updated:** 2026-01-15  
**Version:** 1.0.0
