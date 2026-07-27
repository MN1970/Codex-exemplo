# Setup Guide: OpenTelemetry Observability Stack

Complete step-by-step installation and configuration guide for Manta Maestro Observability (Fase 4, Pillar C).

## Prerequisites

- **Kubernetes 1.24+** with kubectl configured
- **Helm 3.12+** installed
- **8+ CPU cores, 16GB RAM** minimum for observability stack
- **100GB persistent volume** for trace/metrics storage
- **Docker** for building custom images (optional)
- **Python 3.9+, Go 1.21+** for SDK examples

### Verify Prerequisites
```bash
# Kubernetes
kubectl version --short
kubectl get nodes
kubectl describe nodes | grep -E "Name:|cpu:|memory:"

# Helm
helm version

# Available resources
kubectl top nodes
kubectl describe pvc
```

---

## Installation Steps

### Step 1: Create Namespace and Base Resources

```bash
# Navigate to project
cd /home/user/Codex-exemplo/fase4/pillar-c

# Apply namespace (with resource quotas)
kubectl apply -f k8s/namespace.yaml

# Verify namespace
kubectl get ns -L pod-security.kubernetes.io/enforce
kubectl describe quota -n observability
```

### Step 2: Deploy Jaeger + ClickHouse (Tracing Backend)

```bash
# Apply ClickHouse manifests (15-30 seconds)
kubectl apply -f k8s/clickhouse/

# Verify ClickHouse is running
kubectl get pods -n observability -l app=clickhouse -w

# Test ClickHouse connectivity
kubectl port-forward -n observability svc/clickhouse 9000:9000 &
clickhouse-client --host localhost --port 9000 --query "SELECT version()"

# Create trace tables
kubectl exec -it -n observability deployment/clickhouse -- \
  clickhouse-client << 'EOF'
CREATE DATABASE IF NOT EXISTS otel_traces;

CREATE TABLE IF NOT EXISTS otel_traces.otel_traces (
  timestamp DateTime,
  trace_id String,
  span_id String,
  parent_span_id String,
  service_name String,
  operation_name String,
  status_code String,
  duration_nano Int64
) ENGINE = MergeTree()
ORDER BY (timestamp, trace_id)
TTL timestamp + INTERVAL 30 DAY;
EOF

# Apply Jaeger manifests (30-60 seconds)
kubectl apply -f k8s/jaeger/

# Verify Jaeger is running
kubectl get pods -n observability -l app=jaeger -w

# Test Jaeger API
kubectl port-forward -n observability svc/jaeger 16686:16686 &
curl http://localhost:16686/api/services
```

### Step 3: Deploy Prometheus + Node Exporter

```bash
# Apply Prometheus manifests
kubectl apply -f k8s/prometheus/

# Verify Prometheus is running
kubectl get pods -n observability -l app=prometheus -w

# Test Prometheus API
kubectl port-forward -n observability svc/prometheus 9090:9090 &
curl http://localhost:9090/api/v1/query?query=up
```

### Step 4: Deploy Grafana

```bash
# Apply Grafana manifests
kubectl apply -f k8s/grafana/

# Verify Grafana is running
kubectl get pods -n observability -l app=grafana -w

# Access Grafana
kubectl port-forward -n observability svc/grafana 3000:3000 &

# Login
# URL: http://localhost:3000
# Username: admin
# Password: Grafana@2026SecurePass

# Change password on first login (recommended)
```

### Step 5: Deploy Alertmanager

```bash
# Apply Alertmanager manifests
kubectl apply -f k8s/alertmanager/

# Verify Alertmanager is running
kubectl get pods -n observability -l app=alertmanager -w

# Configure webhooks (edit secret)
kubectl edit secret -n observability slack-webhooks
kubectl edit secret -n observability pagerduty-api-key

# Test Alertmanager
kubectl port-forward -n observability svc/alertmanager 9093:9093 &
curl http://localhost:9093/api/v1/alerts
```

### Step 6: Deploy OTEL SDKs (Applications)

#### Python FastAPI Example
```bash
cd otel-sdk/python

# Create Docker image (optional)
docker build -t manta/otel-fastapi:1.0 .

# Or run directly
pip install -r requirements.txt

# Set environment variables
export SERVICE_NAME=manta-gitops
export JAEGER_HOST=jaeger.observability.svc.cluster.local
export JAEGER_PORT=4317
export PROMETHEUS_PORT=8000

# Run application
python otel_fastapi_app.py

# Test endpoints
curl -X POST http://localhost:8080/merge \
  -H "Content-Type: application/json" \
  -d '{"pr_id":"PR-001","branch":"feature/test","conflict_resolution_time_seconds":30}'

# View traces in Jaeger
# http://localhost:16686 → Search for service "manta-gitops"
```

#### Go HTTP Server Example
```bash
cd otel-sdk/go

# Build binary
go build -o server .

# Set environment variables
export SERVICE_NAME=manta-ml-inference
export JAEGER_HOST=jaeger.observability.svc.cluster.local
export JAEGER_PORT=4317
export PROMETHEUS_PORT=8001

# Run server
./server

# Test endpoints
curl http://localhost:8080/health

# View metrics
curl http://localhost:8001/metrics
```

### Step 7: Deploy Anomaly Detection Models

```bash
cd ml-anomaly

# Install dependencies
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Train models
python isolation_forest_model.py
python dbscan_model.py

# Verify models created
ls -lh models/
# isolation_forest.pkl ~5-10MB
# dbscan_drift.pkl ~5-10MB

# Start anomaly scorer
export PROMETHEUS_URL=http://prometheus:9090
export PROMETHEUS_PORT=8001
python anomaly_scorer.py

# Verify metrics exported
curl http://localhost:8001/metrics | grep manta_anomaly
```

---

## Configuration & Customization

### Custom Jaeger Configuration

Edit `k8s/jaeger/jaeger-configmap.yaml`:

```yaml
sampling.json:
  default_strategy:
    type: probabilistic
    param: 0.1  # Sample 10% of traces (reduce cost)
  service_strategies:
    - service: "manta-gitops"
      type: probabilistic
      param: 0.5  # Sample 50% of critical service
```

### Custom Prometheus Retention

Edit `k8s/prometheus/prometheus-deployment.yaml`:

```yaml
args:
  - --storage.tsdb.retention.time=7d  # Default 30d
  - --storage.tsdb.max-block-duration=2h  # Adjust block size
```

### Custom Grafana Dashboards

Import dashboards via API:

```bash
# Export existing dashboard
curl -H "Authorization: Bearer $(cat /run/secrets/grafana-token)" \
  http://localhost:3000/api/dashboards/db/git-analytics > git-analytics-backup.json

# Import new dashboard
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat /run/secrets/grafana-token)" \
  -d @custom-dashboard.json \
  http://localhost:3000/api/dashboards/db
```

### Custom Alert Rules

Edit `k8s/prometheus/prometheus-rules.yaml`:

```yaml
- alert: CustomAlert
  expr: your_metric > 100
  for: 5m
  annotations:
    summary: "Custom alert"
    runbook_url: "https://..."
```

---

## Verification Checklist

### Health Checks

```bash
# All pods running
kubectl get pods -n observability

# All services accessible
kubectl get svc -n observability

# Jaeger ingesting spans
curl -s http://localhost:16686/api/services | jq '.data | length'

# Prometheus scraping targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Grafana dashboard health
curl -s http://localhost:3000/api/datasources | jq '.[] | .name'

# Alertmanager receiving alerts
curl -s http://localhost:9093/api/v1/alerts | jq '.data | length'
```

### Data Flow Verification

```bash
# 1. Create a test application span
curl -X POST http://localhost:8080/merge \
  -H "Content-Type: application/json" \
  -d '{"pr_id":"TEST-123","branch":"main"}'

# 2. Check trace appears in Jaeger
curl -s 'http://localhost:16686/api/traces?service=manta-gitops&limit=1' | jq '.data.traces[0].traceID'

# 3. Check metrics in Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=manta_git_merge_success_total' | jq '.data.result'

# 4. Check dashboard loads in Grafana
curl -s 'http://localhost:3000/api/dashboards/db/git-analytics' | jq '.dashboard.title'
```

---

## Helm Deployment (Alternative)

For production, use Helm charts:

```bash
# Create values file
cat > helm-values.yaml << EOF
prometheus:
  retention: 30d
  scrapeInterval: 15s
  
grafana:
  adminPassword: SecurePass123!
  
jaeger:
  sampling: 0.1
  
clickhouse:
  storage: 100Gi
EOF

# Deploy observability-core
helm install manta-observability ./helm/observability-core/ \
  -n observability \
  -f helm-values.yaml

# Deploy tracing-backend
helm install manta-tracing ./helm/tracing-backend/ \
  -n observability

# Deploy anomaly-detection
helm install manta-anomaly ./helm/anomaly-detection/ \
  -n observability

# Verify
helm list -n observability
```

---

## Post-Installation Configuration

### 1. Configure Alertmanager Webhooks

```bash
# Create Slack webhook secret
kubectl create secret generic slack-webhooks \
  --from-literal=alerts-channel=https://hooks.slack.com/services/YOUR/WEBHOOK \
  -n observability --dry-run=client -o yaml | kubectl apply -f -

# Create PagerDuty API key secret
kubectl create secret generic pagerduty-api-key \
  --from-literal=api-key=YOUR_PAGERDUTY_KEY \
  -n observability --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Import Grafana Dashboards

```bash
# Get Grafana admin token
ADMIN_TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"Grafana@2026SecurePass"}' | jq -r '.token')

# Import dashboards
for dashboard in grafana-dashboards/*.json; do
  curl -X POST http://localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d @$dashboard
done
```

### 3. Enable Persistent Storage

```bash
# Create StorageClass
kubectl apply -f - << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: observability-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
EOF

# Update PVCs to use new StorageClass
kubectl patch pvc -n observability clickhouse-data \
  -p '{"spec":{"storageClassName":"observability-storage"}}'
```

### 4. Configure TLS/HTTPS

```bash
# Create TLS certificate secret
kubectl create secret tls observability-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n observability

# Create Ingress
kubectl apply -f - << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: observability-ingress
  namespace: observability
spec:
  tls:
  - hosts:
    - grafana.manta.local
    - prometheus.manta.local
    - jaeger.manta.local
    secretName: observability-tls
  rules:
  - host: grafana.manta.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
EOF
```

---

## Troubleshooting Installation Issues

### Issue: Pods in CrashLoopBackOff

```bash
# Check logs
kubectl logs -n observability deployment/jaeger

# Check resource limits
kubectl describe pod -n observability deployment/prometheus

# Solution: Increase resource requests/limits in manifest
kubectl edit deployment -n observability prometheus
```

### Issue: PVC not binding

```bash
# Check available storage
kubectl get pv

# Check StorageClass
kubectl get sc

# Solution: Create StorageClass or increase available space
```

### Issue: Jaeger not receiving spans

```bash
# Verify OTLP port is open
kubectl get svc -n observability jaeger -o wide

# Check network policies
kubectl get networkpolicies -n observability

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl -- \
  curl http://jaeger:4317 --version
```

---

## Cleanup

To remove the observability stack:

```bash
# Delete all resources
kubectl delete namespace observability

# Delete PersistentVolumes
kubectl delete pv -l app.kubernetes.io/instance=manta-observability

# Verify cleanup
kubectl get ns | grep observability
kubectl get pv | grep observability
```

---

## Next Steps

1. **[Dashboards](./DASHBOARDS.md):** Import and customize dashboards
2. **[API Integration](./API.md):** Integrate OTEL SDKs into applications
3. **[Alerts](../alerts/alerts-guide.md):** Configure alert rules and escalation
4. **[Troubleshooting](./TROUBLESHOOTING.md):** Common issues and solutions

---

**Estimated Setup Time:** 20-30 minutes  
**Support:** #manta-observability Slack channel
