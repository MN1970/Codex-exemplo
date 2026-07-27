# HPA Operations Runbook

Quick reference guide for diagnosing and resolving HPA issues in Manta Maestro.

## Quick Diagnostics

### Check HPA Status (1 minute)

```bash
# Get all HPAs
kubectl get hpa -n manta -o wide

# Expected output:
# NAME                    REFERENCE             TARGETS           MINPODS MAXPODS REPLICAS AGE
# manta-maestro-fastapi   Deployment/...fastapi 72%/70%           2       10      4        5m
# manta-maestro-react     Deployment/...react   45%/75%           1       5       1        5m
```

### Check Current Metrics (2 minutes)

```bash
# Get top pods
kubectl top pods -n manta -l app=manta-fastapi --containers

# Expected: Low utilization (< 50%) at idle, high during load

# Get detailed HPA metrics
kubectl get hpa manta-maestro-fastapi -n manta -o yaml | grep -A 20 "currentMetrics:"
```

### Check Pod Status (1 minute)

```bash
# Get all pods in manta namespace
kubectl get pods -n manta

# Check any pending pods
kubectl get pods -n manta --field-selector=status.phase=Pending
```

---

## Common Issues & Quick Fixes

### Issue: HPA Not Scaling (Replicas Stuck at Min)

**Symptoms:**
- CPU/Memory high (> 70%) but replicas not increasing
- `kubectl get hpa` shows same replicas for hours

**Quick Fix (5 min):**

```bash
# 1. Check metrics are available
kubectl top pods -n manta -l app=manta-fastapi
# If empty, metrics-server is down

# 2. Check metrics-server
kubectl get deployment metrics-server -n kube-system
kubectl logs deployment/metrics-server -n kube-system --tail=20

# 3. Verify resource requests are set
kubectl get deployment manta-maestro-fastapi -n manta -o yaml | grep -A 5 "requests:"

# 4. Check HPA status
kubectl describe hpa manta-maestro-fastapi -n manta | grep -A 10 "Status:"

# 5. Restart metrics-server if needed
kubectl rollout restart deployment/metrics-server -n kube-system
```

**Root Cause:**
- Metrics Server not running
- Pods missing resource requests
- HPA condition not met (metric below threshold)

---

### Issue: HPA Thrashing (Rapid Scaling Up/Down)

**Symptoms:**
- Replicas: 2 → 8 → 3 → 7 → 4 (wild fluctuation)
- CPU metric unstable (jumps from 65% to 80% rapidly)

**Quick Fix (3 min):**

```bash
# 1. Check HPA scaling events
kubectl get events -n manta --field-selector involvedObject.kind=HorizontalPodAutoscaler

# 2. Increase stabilization window (prevents thrashing)
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/behavior/scaleDown/stabilizationWindowSeconds", "value": 600}]'

# 3. Adjust thresholds higher
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/metrics/0/resource/target/averageUtilization", "value": 80}]'

# 4. Watch to verify stabilization
kubectl get hpa manta-maestro-fastapi -n manta -w
```

**Root Cause:**
- Workload with spiky metrics
- Stabilization window too short
- Threshold too close to current utilization

**Prevention:**
- Set `scaleDown.stabilizationWindowSeconds: 300-600`
- Use higher thresholds (75-80% instead of 70%)
- Monitor metric variance

---

### Issue: Pods Pending After Scale-Up

**Symptoms:**
- HPA scales to 8 replicas
- Only 3-4 pods are running
- Others in Pending state

**Quick Fix (5 min):**

```bash
# 1. Get pending pods
kubectl get pods -n manta --field-selector=status.phase=Pending

# 2. Check why pending
kubectl describe pod <pending-pod> -n manta
# Look for "Insufficient cpu", "Insufficient memory", "failed to provision"

# 3. Check node capacity
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources"

# 4. Options:
#    Option A: Add more nodes (depends on cloud provider)
#    kubectl scale nodes --replicas=5  # Example for GKE
#
#    Option B: Lower HPA maxReplicas
helm upgrade manta-maestro ./manta-helm \
  --set autoscaling.fastapi.maxReplicas=5 \
  -n manta
#
#    Option C: Lower pod resource requests (if safe)
```

**Root Cause:**
- Insufficient cluster capacity
- Node resource exhaustion
- Storage provisioning timeout

---

### Issue: HPA Reaches Max Replicas, Still High Load

**Symptoms:**
- HPA shows 10/10 replicas (at max)
- CPU still > 80%
- Error rate increasing

**Quick Fix (10 min):**

```bash
# 1. Confirm at max
kubectl get hpa manta-maestro-fastapi -n manta
# Shows REPLICAS=10, MAXPODS=10

# 2. Add more nodes (example: GKE)
gcloud container clusters resize manta-cluster --num-nodes=5

# 3. OR: Increase maxReplicas temporarily
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 15}]'

# 4. Monitor scaling
kubectl get hpa manta-maestro-fastapi -n manta -w

# 5. Check if load continues
kubectl top pods -n manta --containers | grep manta-fastapi
```

**Root Cause:**
- Cluster under-provisioned for peak load
- Need to scale infrastructure, not just replicas

---

### Issue: Scale-Down Too Slow (Replicas Stuck at High)

**Symptoms:**
- Load drops but replicas stay at 8
- 10+ minutes pass, still at 8
- Wasting resources

**Quick Fix (2 min):**

```bash
# 1. Check scale-down policy
kubectl get hpa manta-maestro-fastapi -n manta -o yaml | grep -A 10 "scaleDown:"

# 2. Reduce stabilization window
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/behavior/scaleDown/stabilizationWindowSeconds", "value": 300}]'

# 3. Increase scale-down rate
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/behavior/scaleDown/policies/0/value", "value": 75}]'

# 4. Verify scaling down
kubectl get hpa manta-maestro-fastapi -n manta -w
```

**Root Cause:**
- Conservative scale-down settings
- Stabilization window waiting before scale-down

---

## Monitoring & Alerts

### Key Metrics to Watch

```bash
# HPA scaling events
kubectl get events -n manta --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler

# Pod resource utilization
kubectl top pods -n manta

# HPA current status
kubectl get hpa -n manta
```

### Prometheus Queries

```promql
# HPA current replicas
kube_hpa_status_current_replicas{namespace="manta"}

# How often HPA scales
rate(kube_hpa_status_current_replicas[10m]) != 0

# Metric vs threshold
container_cpu_usage_seconds_total{namespace="manta"} / kube_pod_container_resource_limits
```

### Alert Thresholds

| Alert | Condition | Action |
|-------|-----------|--------|
| `HPAReachedMaxReplicas` | Replicas >= Max-1 for 5m | **Escalate**: add nodes or raise max |
| `HPAThrashing` | Scale 3+ times in 10m | **Investigate**: check metric stability |
| `HPAScalingFailed` | Failures detected | **Check**: cluster resources, PDB |

---

## Configuration Changes

### Increase Max Replicas

```bash
# Via kubectl patch
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 15}]'

# Via helm upgrade
helm upgrade manta-maestro ./manta-helm \
  --set autoscaling.fastapi.maxReplicas=15 \
  -n manta
```

### Change CPU Threshold

```bash
# Via kubectl patch
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/metrics/0/resource/target/averageUtilization", "value": 75}]'

# Via helm upgrade
helm upgrade manta-maestro ./manta-helm \
  --set autoscaling.fastapi.targetCPUUtilizationPercentage=75 \
  -n manta
```

### Disable HPA

```bash
# Temporarily disable while troubleshooting
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' \
  -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 2}]'

# Reset manually to fixed replicas
kubectl scale deployment manta-maestro-fastapi -n manta --replicas=3
```

---

## Performance Tuning

### For Stability (Prevent Thrashing)

```yaml
# Use these settings
autoscaling:
  fastapi:
    targetCPUUtilizationPercentage: 75     # Not 70
    behavior:
      scaleUp:
        stabilizationWindowSeconds: 60
      scaleDown:
        stabilizationWindowSeconds: 600    # 10 minutes
```

### For Responsiveness (Quick Scale-Up)

```yaml
autoscaling:
  fastapi:
    targetCPUUtilizationPercentage: 70
    behavior:
      scaleUp:
        stabilizationWindowSeconds: 0      # Immediate
        policies:
          - type: Percent
            value: 100
            periodSeconds: 30
```

### For Cost Efficiency (Conservative Scaling)

```yaml
autoscaling:
  fastapi:
    minReplicas: 1                         # Lower minimum
    targetCPUUtilizationPercentage: 80     # Higher threshold
    behavior:
      scaleDown:
        stabilizationWindowSeconds: 900    # 15 minutes
        policies:
          - type: Percent
            value: 25                      # Reduce by 25%
```

---

## Emergency Procedures

### Disable HPA Immediately

```bash
# Scale to fixed replicas
kubectl scale deployment manta-maestro-fastapi -n manta --replicas=3

# Disable HPA
kubectl delete hpa manta-maestro-fastapi -n manta
```

### Restore from Values

```bash
# Re-enable HPA from Helm
helm upgrade manta-maestro ./manta-helm \
  --set autoscaling.fastapi.enabled=true \
  -n manta
```

### Check All HPA Events

```bash
# Last 1 hour of HPA events
kubectl get events -n manta \
  --field-selector involvedObject.kind=HorizontalPodAutoscaler \
  --sort-by='.metadata.creationTimestamp'
```

---

## Useful Commands Summary

```bash
# Status check
kubectl get hpa -n manta -o wide

# Watch scaling
kubectl get hpa -n manta -w

# Detailed status
kubectl describe hpa manta-maestro-fastapi -n manta

# Events
kubectl get events -n manta --field-selector involvedObject.kind=HorizontalPodAutoscaler

# Metrics
kubectl top pods -n manta -l app=manta-fastapi
kubectl top nodes

# Patch HPA
kubectl patch hpa manta-maestro-fastapi -n manta --type='json' -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 15}]'

# Manual scale
kubectl scale deployment manta-maestro-fastapi -n manta --replicas=5

# Restart metrics-server
kubectl rollout restart deployment/metrics-server -n kube-system

# Get HPA YAML
kubectl get hpa manta-maestro-fastapi -n manta -o yaml
```

---

## Resources

- [AUTOSCALING_GUIDE.md](./AUTOSCALING_GUIDE.md) - Full auto-scaling guide
- [LOAD_TESTING_GUIDE.md](../tests/LOAD_TESTING_GUIDE.md) - Load testing procedures
- [Kubernetes HPA Docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

---

**Last Updated:** 2026-07-27
**Urgency Level:** High - Use for incident response
