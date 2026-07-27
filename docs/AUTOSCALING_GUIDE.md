# Kubernetes Auto-Scaling Guide - Manta Maestro

## Overview

This guide covers the Horizontal Pod Autoscaler (HPA) and custom metrics setup for Manta Maestro's Kubernetes deployment. The auto-scaling system automatically adjusts the number of pod replicas based on real-time metrics (CPU, memory, and custom metrics) to handle varying load while optimizing costs.

**Table of Contents**
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Load Testing](#load-testing)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Prerequisites

### Kubernetes Cluster Requirements

- **Kubernetes 1.23+** (1.28+ recommended for autoscaling/v2)
- **Metrics Server** installed in `kube-system` namespace
- **Prometheus** for metric collection
- **Prometheus Adapter** for custom metrics
- **Grafana** for dashboard visualization (optional but recommended)

### Required Helm Charts/Components

```bash
# Verify metrics-server is installed
kubectl get deployment metrics-server -n kube-system

# If not present, install:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify installation
kubectl top nodes
kubectl top pods -n manta
```

### CLI Tools

- `kubectl` (1.23+)
- `helm` (3.10+)
- `locust` (for load testing)

---

## Architecture

### HPA Controllers

Manta Maestro deploys three HPA controllers:

| Component | Min Replicas | Max Replicas | CPU Target | Memory Target | Status |
|-----------|-------------|--------------|-----------|---------------|--------|
| **FastAPI** | 2 | 10 | 70% | 80% | Primary target |
| **React SPA** | 1 | 5 | 75% | N/A | Frontend |
| **PostgreSQL** | 1 | 3 | 80% | 85% | Conservative scaling |

### Scaling Policies

Each HPA has different scaling behavior to prevent thrashing:

**FastAPI (Scale-Up)**
- Stabilization: 0 seconds (aggressive)
- Policy 1: +100% of current replicas every 30s
- Policy 2: +2 pods every 30s
- Selects the maximum change (Max strategy)

**FastAPI (Scale-Down)**
- Stabilization: 300 seconds (5 minutes)
- Policy: -50% of current replicas every 60s

**React (Scale-Up)**
- Stabilization: 30 seconds
- Policy: +100% of current replicas every 30s

**React (Scale-Down)**
- Stabilization: 300 seconds
- Policy: -50% of current replicas every 60s

**PostgreSQL (Conservative)**
- Scale-Up: Stabilization 60s, +50% every 60s, max 1 pod per scale
- Scale-Down: Stabilization 300s, -25% every 120s

---

## Installation & Setup

### 1. Verify Metrics Server

```bash
# Check if metrics-server is running
kubectl get deployment metrics-server -n kube-system -o wide

# Check metrics collection
kubectl top nodes
kubectl top pods -n manta

# Expected output:
# NAME                       CPU(cores)   MEMORY(Mi)
# manta-fastapi-abc12-xyz    450m         512Mi
```

If metrics are not available, install metrics-server:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n kube-system
```

### 2. Deploy Prometheus Adapter (for Custom Metrics)

Create a namespace for monitoring:

```bash
kubectl create namespace monitoring
```

Install Prometheus and Prometheus Adapter:

```bash
# Using Helm (recommended)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus Stack
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set prometheus.prometheusSpec.retention=7d

# Install Prometheus Adapter
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  -n monitoring \
  -f monitoring/prometheus-adapter-values.yaml
```

### 3. Deploy Manta Helm Chart with HPA Enabled

```bash
# Update Helm chart values
helm repo add manta https://charts.manta.example.com
helm repo update

# Deploy with autoscaling enabled
helm install manta-maestro manta/manta-helm \
  --namespace manta \
  --create-namespace \
  -f manta-helm/values-production.yaml \
  --set autoscaling.fastapi.enabled=true \
  --set autoscaling.react.enabled=true \
  --set autoscaling.postgres.enabled=true

# Verify HPA resources created
kubectl get hpa -n manta
kubectl get pdb -n manta  # Pod Disruption Budgets
```

### 4. Verify HPA Status

```bash
# Check HPA status
kubectl get hpa -n manta -o wide

# Watch HPA in real-time
kubectl get hpa -n manta -w

# Get detailed HPA status
kubectl describe hpa manta-maestro-fastapi -n manta
```

Expected output:

```
NAME                       REFERENCE                            TARGETS                       MINPODS   MAXPODS   REPLICAS   AGE
manta-maestro-fastapi      Deployment/manta-maestro-fastapi     72%/70%                       2         10        2          5m
manta-maestro-react        Deployment/manta-maestro-react       45%/75%                       1         5         1          5m
manta-maestro-postgres     StatefulSet/manta-maestro-postgres   82%/80%, 78%/85%              1         3         1          5m
```

---

## Configuration

### Helm Values Configuration

#### FastAPI HPA Settings

```yaml
autoscaling:
  fastapi:
    enabled: true
    minReplicas: 2          # Always keep 2 FastAPI pods
    maxReplicas: 10         # Max 10 replicas (adjust based on cluster capacity)
    targetCPUUtilizationPercentage: 70     # Scale up if CPU > 70%
    targetMemoryUtilizationPercentage: 80  # Scale up if memory > 80%
```

#### React HPA Settings

```yaml
autoscaling:
  react:
    enabled: true
    minReplicas: 1          # Min 1 frontend pod
    maxReplicas: 5          # Frontend rarely needs more
    targetCPUUtilizationPercentage: 75
```

#### PostgreSQL HPA Settings

```yaml
autoscaling:
  postgres:
    enabled: true
    minReplicas: 1
    maxReplicas: 3          # Conservative - database scaling is complex
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 85
    customMetrics:
      - name: "db_active_connections"
        targetType: "AverageValue"
        targetValue: "80"   # Scale if > 80 active connections
```

### Custom Metrics Configuration

Edit `manta-helm/templates/prometheus-adapter-configmap.yaml`:

```yaml
customMetrics:
  prometheusAdapter:
    enabled: true
    configMapName: manta-prometheus-adapter
    # Rules map Prometheus metrics to K8s custom metrics
    rules:
      - seriesQuery: 'manta_api_requests_per_second'
        resources:
          overrides:
            namespace: {resource: "namespace"}
            pod: {resource: "pod"}
        name:
          matches: "requests_per_second"
```

### Adjusting Thresholds

To change scaling thresholds without redeploying:

```bash
# Edit HPA directly
kubectl edit hpa manta-maestro-fastapi -n manta

# Change targetCPUUtilizationPercentage from 70 to 75
# Save and exit

# Verify changes applied
kubectl get hpa manta-maestro-fastapi -n manta -o yaml | grep target
```

### Pod Disruption Budgets

Pod Disruption Budgets (PDBs) ensure minimum availability during cluster operations:

```yaml
# FastAPI PDB requires minimum 1 pod always available
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: manta-fastapi
```

View PDBs:

```bash
kubectl get pdb -n manta
kubectl describe pdb manta-maestro-fastapi -n manta
```

---

## Monitoring

### HPA Status Monitoring

Check current HPA status:

```bash
# Get HPA metrics
kubectl get hpa -n manta --watch

# Get detailed info
kubectl describe hpa manta-maestro-fastapi -n manta

# Get HPA events
kubectl get events -n manta --field-selector involvedObject.kind=HorizontalPodAutoscaler
```

### Prometheus Queries

Monitor scaling events with Prometheus:

```promql
# Current replicas for FastAPI
kube_hpa_status_current_replicas{hpa="manta-maestro-fastapi", namespace="manta"}

# Desired vs current replicas
kube_hpa_status_desired_replicas{namespace="manta"}

# HPA scaling rate
rate(kube_hpa_status_current_replicas[10m]) > 0  # Scale-up events
rate(kube_hpa_status_current_replicas[10m]) < 0  # Scale-down events

# CPU utilization by pod
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="manta"}[1m]))

# Memory utilization by pod
sum by (pod) (container_memory_working_set_bytes{namespace="manta"})

# Request rate
sum(rate(http_requests_total{namespace="manta"}[1m]))

# Error rate
sum(rate(http_requests_total{namespace="manta", status=~"5.."}[1m]))
```

### Grafana Dashboard

Import the HPA dashboard:

```bash
# The dashboard is pre-configured in monitoring/grafana-hpa-dashboard.json
# Import via Grafana UI: Dashboards > Import > Upload JSON

# Or deploy via Helm:
kubectl create configmap grafana-hpa-dashboard \
  --from-file=monitoring/grafana-hpa-dashboard.json \
  -n monitoring

# Dashboard shows:
# - HPA Current vs Desired Replicas (timeline)
# - Resource Utilization vs Thresholds
# - Scaling Events (scale-up/down frequency)
# - Request Rate and Error Rate
# - Per-pod metrics
```

### Alerts

Critical alerts configured in `monitoring/alert-rules.yaml`:

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| **HPAReachedMaxReplicas** | Current >= Max-1 for 5m | Critical | Scale cluster, raise max replicas |
| **HPAThrashing** | 3+ scale events in 10m | Warning | Review HPA thresholds, check metrics stability |
| **HPAScalingFailed** | > 0 failures in 5m | Critical | Check cluster resources, HPA config |
| **HighMetricValue** | p95 latency > 5s | Warning | Monitor, may trigger HPA soon |
| **ClusterNodeCapacity** | < 3 nodes | Warning | Add nodes if HPA maxReplicas reached |

---

## Load Testing

### Prerequisites

```bash
pip install locust
```

### Running Load Tests

#### Baseline Test (100 concurrent users)

```bash
locust -f tests/load_test.py \
  -u 100 \
  --spawn-rate 10 \
  -H http://localhost:8000 \
  --run-time 5m \
  --csv=results/baseline_100
```

#### Scaling Test (500 concurrent users - triggers HPA)

```bash
locust -f tests/load_test.py \
  -u 500 \
  --spawn-rate 25 \
  -H https://api.manta.example.com \
  --run-time 15m \
  --csv=results/scaling_500
```

Watch HPA scaling in parallel:

```bash
# Terminal 2: Monitor HPA scaling
kubectl get hpa manta-maestro-fastapi -n manta -w

# Terminal 3: Monitor pods
kubectl get pods -n manta -l app=manta-fastapi -w

# Terminal 4: Watch metrics
kubectl top pods -n manta -l app=manta-fastapi --containers -w
```

### Expected Behavior

**Phase 1 (0-1 min):** Spawn 25 users/sec
- 2 FastAPI replicas running
- CPU/memory increasing

**Phase 2 (1-3 min):** Reach 500 concurrent users
- CPU > 70% threshold
- HPA scales to 4 replicas (100% increase)
- Load distributes across 4 pods

**Phase 3 (3-10 min):** Sustained load
- Continue scaling: 4 → 6 → 8 replicas
- Latency maintained < 5s p95
- Error rate < 1%

**Phase 4 (10-15 min):** Wind down
- Spawn rate decreases
- HPA begins scale-down after 300s stabilization
- Replicas reduce back to 2-3

### Load Test Metrics

Expected results (500 concurrent users):

```
Response Time:
- Min: 50ms
- Mean: 800ms
- Max: 3500ms
- p95: < 3s
- p99: < 5s

Requests:
- Total: ~15,000
- RPS: ~100-150/sec at peak
- Success: > 99%
- Error rate: < 1%

Scaling:
- Initial replicas: 2
- Peak replicas: 8-10
- Scale-up time: 2-3 minutes
- Minimum scale latency per pod: 30 seconds
```

---

## Troubleshooting

### HPA Not Scaling

**Symptoms:** Metrics show high CPU/memory but HPA isn't scaling

**Diagnosis:**

```bash
# 1. Check HPA status
kubectl describe hpa manta-maestro-fastapi -n manta

# Look for "Current Metrics" and error messages

# 2. Check metrics are available
kubectl top pods -n manta -l app=manta-fastapi

# If empty, metrics-server is not working
# 3. Check HPA events
kubectl get events -n manta --field-selector involvedObject.name=manta-maestro-fastapi

# 4. Check resource requests are set
kubectl get deployment manta-maestro-fastapi -n manta -o yaml | grep -A 5 "requests:"
```

**Solutions:**

1. **Metrics Server not running:**
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. **Metrics not available (pods need resource requests):**
   ```yaml
   resources:
     requests:
       cpu: 500m
       memory: 512Mi
   ```

3. **HPA misconfigured:**
   ```bash
   kubectl edit hpa manta-maestro-fastapi -n manta
   # Verify minReplicas < maxReplicas
   # Verify resource metrics are set
   ```

### HPA Thrashing (Rapid Scaling)

**Symptoms:** Replicas rapidly increase and decrease (2→10→3→8...)

**Causes:**
- Thresholds too close to current utilization
- Unstable workload metrics
- Stabilization window too short

**Solutions:**

1. **Increase stabilization window:**
   ```bash
   kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
     -p='[{"op": "replace", "path": "/spec/behavior/scaleDown/stabilizationWindowSeconds", "value": 600}]'
   ```

2. **Adjust thresholds:**
   - Increase target CPU from 70% to 75-80%
   - Reduce aggressive scale-up (100% → 50%)

3. **Monitor metric stability:**
   ```promql
   # Check CPU metric variance
   stddev_over_time(container_cpu_usage_seconds_total[5m])
   ```

### Pods Pending After Scale-Up

**Symptoms:** HPA scales to 8 replicas but only 3-4 are running

**Causes:**
- Insufficient cluster resources
- Node resource quotas exceeded
- Storage provisioning delays

**Solutions:**

```bash
# Check pending pods
kubectl get pods -n manta --field-selector=status.phase=Pending

# Check pod events
kubectl describe pod <pending-pod> -n manta

# Check node resources
kubectl top nodes
kubectl describe nodes

# Add more nodes if needed
# (Cloud provider specific)

# Set maxReplicas lower if cluster can't support
helm upgrade manta-maestro manta/manta-helm \
  --set autoscaling.fastapi.maxReplicas=6 \
  -n manta
```

### Database Scaling Issues

**Symptoms:** PostgreSQL HPA scaling causes replication lag

**Solutions:**

1. **Keep PostgreSQL minReplicas at 1:**
   - Database scaling is complex
   - Use connection pooling instead (PgBouncer)

2. **Monitor replication lag:**
   ```promql
   pg_replication_lag_bytes
   ```

3. **Conservative thresholds:**
   - CPU: 80% (not 70%)
   - Memory: 85% (not 80%)
   - Scale-down stabilization: 600s (not 300s)

---

## Best Practices

### 1. Resource Requests & Limits

Always set appropriate requests and limits:

```yaml
resources:
  requests:
    cpu: 500m          # Used by scheduler and HPA
    memory: 512Mi
  limits:
    cpu: 2000m         # Hard limit
    memory: 2Gi
```

**Why?**
- HPA uses requests to calculate utilization
- Requests ensure fair resource distribution
- Limits prevent pod from consuming cluster

### 2. Health Checks

Configure readiness and liveness probes:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 2

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

### 3. Graceful Shutdown

Set appropriate termination grace period:

```yaml
terminationGracePeriodSeconds: 30  # Allow 30s for in-flight requests
```

### 4. Pod Disruption Budgets

Ensure critical apps stay available during maintenance:

```yaml
spec:
  minAvailable: 1  # Always keep 1 FastAPI pod running
```

### 5. Monitoring & Alerting

- Monitor HPA scaling events daily
- Set alerts for thrashing and max replica events
- Review metrics monthly to tune thresholds
- Track scaling effectiveness (cost vs performance)

### 6. Scaling Testing

- Test load before production
- Measure scale-up/down times
- Verify error rates during scaling
- Document baseline performance

### 7. Cost Optimization

Balance auto-scaling with costs:

```bash
# Calculate cost of max replicas
Pod cost * maxReplicas * hourly_rate

# Example: 10 FastAPI pods @ $10/pod/month = $100/month
# Consider reserved capacity or spot instances for cost savings
```

### 8. Documentation

- Document custom HPA thresholds in runbooks
- Track scaling trigger conditions
- Maintain playbooks for scaling issues

---

## Commands Reference

### Viewing HPA Status

```bash
# List all HPAs
kubectl get hpa -n manta

# Watch HPA scaling in real-time
kubectl get hpa -n manta --watch

# Get detailed HPA info
kubectl describe hpa manta-maestro-fastapi -n manta

# Get HPA in YAML
kubectl get hpa manta-maestro-fastapi -n manta -o yaml
```

### Updating HPA

```bash
# Edit HPA
kubectl edit hpa manta-maestro-fastapi -n manta

# Patch specific field
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 15}]'

# Scale deployment manually
kubectl scale deployment manta-maestro-fastapi -n manta --replicas=5
```

### Monitoring Metrics

```bash
# Top nodes
kubectl top nodes

# Top pods
kubectl top pods -n manta

# Top pods with containers
kubectl top pods -n manta --containers

# Watch metrics
kubectl top pods -n manta -w

# Get metrics in JSON
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/manta/pods
```

### Debugging

```bash
# Get HPA events
kubectl get events -n manta --field-selector involvedObject.kind=HorizontalPodAutoscaler

# Check metrics availability
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/manta/pods

# Pod events
kubectl describe pod <pod-name> -n manta

# Pod logs
kubectl logs <pod-name> -n manta

# Previous logs (if pod crashed)
kubectl logs <pod-name> -n manta --previous
```

---

## Further Reading

- [Kubernetes HPA Official Docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
- [Pod Disruption Budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [Kubernetes Resource Metrics API](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-metrics-pipeline/)

---

**Last Updated:** 2026-07-27
**Maintainer:** Manta DevOps Team
