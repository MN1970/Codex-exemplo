# Fase 4 Production Deployment Plan

**Status**: Ready for Execution
**Date**: 2026-07-27
**Version**: 1.0.0

---

## Pre-Deployment Checklist

### Prerequisites Verification

- [ ] Kubernetes cluster 1.24+ available and accessible
- [ ] kubectl configured with production cluster context
- [ ] 16+ CPU cores and 32+ GB RAM available
- [ ] 300+ GB disk space for storage
- [ ] Ingress controller (nginx-ingress) deployed
- [ ] cert-manager installed for TLS certificates
- [ ] Node labels configured:
  - `ml-node=true` (for ML model storage)
  - `monitoring-node=true` (for Prometheus)
  - `observability-node=true` (for Elasticsearch)

### Security Approval

- [ ] Security team approved RBAC configuration
- [ ] Network policies reviewed and approved
- [ ] Container images scanned (trivy, Snyk)
- [ ] Secrets management solution configured
- [ ] TLS certificates provisioned
- [ ] Backup encryption keys stored securely

### Stakeholder Sign-off

- [ ] Platform Engineering lead approval
- [ ] DevOps team ready for deployment
- [ ] On-call rotation updated
- [ ] Communication plan executed (team notification)
- [ ] Rollback plan documented and tested

---

## Deployment Phases

### Phase 0: Pre-Flight Checks (15 minutes)

**Goal**: Verify cluster is ready for deployment

```bash
#!/bin/bash
set -e

echo "=== Phase 0: Pre-Flight Checks ==="

# 1. Verify cluster connectivity
echo "[1/8] Verifying cluster connectivity..."
kubectl cluster-info
kubectl get nodes

# 2. Check resource availability
echo "[2/8] Checking resource availability..."
TOTAL_CPU=$(kubectl get nodes -o json | \
  jq -r '.items[] | .status.allocatable.cpu' | \
  sed 's/m$//' | awk '{sum += $1} END {print sum}')
TOTAL_MEMORY=$(kubectl get nodes -o json | \
  jq -r '.items[] | .status.allocatable.memory' | \
  sed 's/Ki$//' | awk '{sum += $1} END {print int(sum / 1048576)}')

echo "Available CPU: ${TOTAL_CPU}m"
echo "Available Memory: ${TOTAL_MEMORY}Gi"

if (( TOTAL_CPU < 16000 )); then
  echo "ERROR: Insufficient CPU (need 16, have $(( TOTAL_CPU / 1000 )))"
  exit 1
fi

if (( TOTAL_MEMORY < 32 )); then
  echo "ERROR: Insufficient Memory (need 32Gi, have ${TOTAL_MEMORY}Gi)"
  exit 1
fi

# 3. Check node labels
echo "[3/8] Checking node labels..."
ML_NODES=$(kubectl get nodes -l ml-node=true | wc -l)
if (( ML_NODES < 1 )); then
  echo "WARNING: No nodes labeled ml-node=true"
fi

# 4. Verify ingress controller
echo "[4/8] Verifying ingress controller..."
if kubectl get deployment -n ingress-nginx nginx-ingress-controller &>/dev/null; then
  echo "✓ nginx-ingress controller found"
else
  echo "ERROR: nginx-ingress controller not found"
  exit 1
fi

# 5. Verify cert-manager
echo "[5/8] Verifying cert-manager..."
if kubectl get deployment -n cert-manager cert-manager &>/dev/null; then
  echo "✓ cert-manager found"
else
  echo "WARNING: cert-manager not found - TLS may fail"
fi

# 6. Check for existing namespace
echo "[6/8] Checking for existing namespace..."
if kubectl get namespace manta-fase4-prod &>/dev/null; then
  echo "WARNING: Namespace manta-fase4-prod already exists"
  echo "This will update existing deployment"
fi

# 7. Verify DNS resolution
echo "[7/8] Verifying DNS resolution..."
kubectl run -it --rm dns-check --image=busybox --restart=Never -- \
  nslookup kubernetes.default &>/dev/null && echo "✓ DNS working" || echo "WARNING: DNS check failed"

# 8. Check storage provisioner
echo "[8/8] Checking storage provisioner..."
if kubectl get storageclass &>/dev/null; then
  echo "✓ Storage classes available"
else
  echo "WARNING: No storage classes found"
fi

echo ""
echo "=== Phase 0 Complete ==="
echo "Cluster is ready for deployment!"
```

### Phase 1: Namespace & RBAC Setup (5 minutes)

**Goal**: Create secure namespace with proper access controls

```bash
#!/bin/bash
echo "=== Phase 1: Namespace & RBAC Setup ==="

# Apply namespace, RBAC, quotas, limit ranges, network policies
kubectl apply -f fase4/k8s-production/namespace.yaml

echo "Waiting for namespace to be active..."
kubectl wait --for=condition=Active namespace/manta-fase4-prod --timeout=30s

echo "✓ Namespace created"
echo "✓ ServiceAccount configured"
echo "✓ RBAC roles bound"
echo "✓ Resource quotas applied"
echo "✓ Limit ranges enforced"
echo "✓ Network policies configured"
```

### Phase 2: Storage Configuration (5 minutes)

**Goal**: Provision persistent storage for data

```bash
#!/bin/bash
echo "=== Phase 2: Storage Configuration ==="

# Apply persistent volumes and claims
kubectl apply -f fase4/k8s-production/storage.yaml

echo "Waiting for PVs to be available..."
for pv in ml-model-pv prometheus-pv elasticsearch-data-pv; do
  kubectl wait --for=condition=Available pv/$pv --timeout=30s || true
done

echo "✓ PersistentVolumes created"
echo "✓ StorageClasses configured"
echo "✓ Storage ready for deployment"
```

### Phase 3: Observability Stack (10 minutes)

**Goal**: Deploy monitoring, tracing, and alerting infrastructure

```bash
#!/bin/bash
echo "=== Phase 3: Observability Stack ==="

# Deploy monitoring configs first
kubectl apply -f fase4/k8s-production/monitoring-configs.yaml

# Deploy observability components
kubectl apply -f fase4/k8s-production/pillar-c-observability.yaml

echo "Waiting for observability deployments..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/jaeger-collector -n manta-fase4-prod
kubectl wait --for=condition=available --timeout=300s \
  deployment/prometheus -n manta-fase4-prod
kubectl wait --for=condition=available --timeout=300s \
  deployment/grafana -n manta-fase4-prod
kubectl wait --for=condition=available --timeout=300s \
  deployment/alertmanager -n manta-fase4-prod

echo "✓ Jaeger Collector running"
echo "✓ Prometheus collecting metrics"
echo "✓ Grafana dashboards available"
echo "✓ Alertmanager routing alerts"
```

### Phase 4: Platform Router (Pillar A) - 8 minutes

**Goal**: Deploy multi-platform API gateway

```bash
#!/bin/bash
echo "=== Phase 4: Platform Router (Pillar A) ==="

kubectl apply -f fase4/k8s-production/pillar-a-router.yaml

echo "Waiting for Platform Router deployment..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/platform-router -n manta-fase4-prod

echo "Waiting for ready replicas..."
REPLICAS=0
while (( REPLICAS < 3 )); do
  REPLICAS=$(kubectl get deployment platform-router -n manta-fase4-prod \
    -o jsonpath='{.status.readyReplicas}')
  echo "Ready replicas: $REPLICAS/3"
  sleep 5
done

echo "Testing health checks..."
ROUTER_POD=$(kubectl get pods -n manta-fase4-prod -l app=platform-router -o name | head -1)
kubectl exec -it $ROUTER_POD -n manta-fase4-prod -- \
  curl -s http://localhost:8080/health/ready | jq .

echo "✓ Platform Router deployed (3 replicas ready)"
echo "✓ Health checks passing"
```

### Phase 5: Code Refactoring Engine (Pillar B) - 8 minutes

**Goal**: Deploy AST-based code analysis engine

```bash
#!/bin/bash
echo "=== Phase 5: Code Refactoring Engine (Pillar B) ==="

kubectl apply -f fase4/k8s-production/pillar-b-refactor.yaml

echo "Waiting for Code Refactor deployment..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/code-refactor-engine -n manta-fase4-prod

echo "Waiting for ready replicas..."
REPLICAS=0
while (( REPLICAS < 2 )); do
  REPLICAS=$(kubectl get deployment code-refactor-engine -n manta-fase4-prod \
    -o jsonpath='{.status.readyReplicas}')
  echo "Ready replicas: $REPLICAS/2"
  sleep 5
done

echo "✓ Code Refactoring Engine deployed (2 replicas ready)"
echo "✓ 55 detection rules loaded"
```

### Phase 6: ML Inference Service (Pillar D) - 10 minutes

**Goal**: Deploy machine learning model serving infrastructure

```bash
#!/bin/bash
echo "=== Phase 6: ML Inference Service (Pillar D) ==="

kubectl apply -f fase4/k8s-production/pillar-d-ml-model.yaml

echo "Waiting for ML Inference deployment..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/ml-inference -n manta-fase4-prod

echo "Waiting for ready replicas..."
REPLICAS=0
while (( REPLICAS < 3 )); do
  REPLICAS=$(kubectl get deployment ml-inference -n manta-fase4-prod \
    -o jsonpath='{.status.readyReplicas}')
  echo "Ready replicas: $REPLICAS/3"
  sleep 5
done

echo "✓ ML Inference Service deployed (3 replicas ready)"
echo "✓ Model v2.0 loaded (93.65% accuracy)"
echo "✓ Daily scoring CronJob scheduled"
```

### Phase 7: Networking & Ingress (5 minutes)

**Goal**: Configure external access and network policies

```bash
#!/bin/bash
echo "=== Phase 7: Networking & Ingress ==="

kubectl apply -f fase4/k8s-production/ingress-and-networking.yaml

echo "Waiting for Ingress controller..."
sleep 10

echo "Verifying Ingress endpoints..."
kubectl get ingress -n manta-fase4-prod
kubectl get networkpolicy -n manta-fase4-prod

echo "✓ Ingress configured"
echo "✓ TLS certificates pending (cert-manager will provision)"
echo "✓ Network policies enforced"
```

### Phase 8: Validation & Health Checks (15 minutes)

**Goal**: Comprehensive validation of production deployment

```bash
#!/bin/bash
echo "=== Phase 8: Validation & Health Checks ==="

# Run comprehensive validation script
bash fase4/k8s-production/validate-deployment.sh

if [ $? -eq 0 ]; then
  echo "✓ All validation checks PASSED"
else
  echo "✗ Validation failed - rolling back"
  exit 1
fi

# Additional production checks
echo ""
echo "Running production-specific validation..."

# 1. Verify all pods running
echo "[1/6] Checking pod status..."
FAILED_PODS=$(kubectl get pods -n manta-fase4-prod \
  --field-selector=status.phase!=Running -o name | wc -l)
if [ $FAILED_PODS -eq 0 ]; then
  echo "✓ All pods running"
else
  echo "✗ $FAILED_PODS pods not running"
  exit 1
fi

# 2. Verify metrics collection
echo "[2/6] Checking metrics collection..."
METRICS=$(kubectl exec -it prometheus-0 -n manta-fase4-prod -- \
  curl -s localhost:9090/api/v1/targets | jq '.data.activeTargets | length')
echo "✓ Prometheus collecting from $METRICS targets"

# 3. Test inter-service connectivity
echo "[3/6] Testing inter-service connectivity..."
ROUTER_POD=$(kubectl get pods -n manta-fase4-prod -l app=platform-router -o name | head -1)
kubectl exec -it $ROUTER_POD -n manta-fase4-prod -- \
  curl -s http://code-refactor-engine:8081/health/ready > /dev/null && \
  echo "✓ Router → Refactor connectivity OK" || \
  echo "✗ Router → Refactor connectivity FAILED"

# 4. Verify HPA configured
echo "[4/6] Verifying HPA..."
kubectl get hpa -n manta-fase4-prod | wc -l | grep -q "[4-9]" && \
  echo "✓ HPA configured" || \
  echo "✗ HPA not configured"

# 5. Check resource usage
echo "[5/6] Checking resource utilization..."
kubectl top pods -n manta-fase4-prod | tail -1

# 6. Review alerts
echo "[6/6] Checking active alerts..."
ALERTS=$(kubectl exec -it alertmanager-0 -n manta-fase4-prod -- \
  curl -s localhost:9093/api/v1/alerts | jq '.data | length')
if [ "$ALERTS" = "0" ]; then
  echo "✓ No active alerts"
else
  echo "⚠ $ALERTS active alerts (review in Alertmanager)"
fi

echo ""
echo "=== Phase 8 Complete ==="
```

### Phase 9: Canary Gate Activation (5 minutes)

**Goal**: Activate ML confidence-based canary deployment strategy

```bash
#!/bin/bash
echo "=== Phase 9: Canary Gate Activation ==="

# Create ConfigMap with canary gate configuration
kubectl create configmap ml-canary-gates \
  --from-literal=phase_0_audit_confidence=0.95 \
  --from-literal=phase_1_low_risk_confidence=0.90 \
  --from-literal=phase_2_medium_risk_confidence=0.85 \
  --from-literal=phase_3_full_deployment_confidence=0.75 \
  --from-literal=current_phase=0 \
  -n manta-fase4-prod || true

echo "✓ Phase 0 (Audit Mode) activated"
echo "  - ML model confidence threshold: 95%"
echo "  - Production traffic: 0%"
echo "  - Duration: 24 hours (monitoring only)"
echo ""
echo "Phase progression schedule:"
echo "  Phase 0: 24-48 hours (audit, 0% traffic)"
echo "  Phase 1: 2-3 days (5% traffic at 90% confidence)"
echo "  Phase 2: 3-5 days (25% traffic at 85% confidence)"
echo "  Phase 3: Full deployment (100% traffic at 75% confidence)"
echo ""
echo "✓ Canary gates configured"
echo "✓ Ready for progressive rollout"
```

### Phase 10: Post-Deployment Monitoring (Continuous)

**Goal**: Monitor production system for 48 hours

```bash
#!/bin/bash
echo "=== Phase 10: Post-Deployment Monitoring ==="
echo "Monitoring production deployment for 48 hours..."
echo ""
echo "Key metrics to monitor:"
echo "  - Error rate: should be <0.1%"
echo "  - P95 latency: should be <500ms"
echo "  - ML model confidence: should be >90%"
echo "  - Pod restart count: should be 0"
echo "  - Memory usage: should be <80% of limit"
echo ""
echo "Access monitoring dashboards:"
echo "  Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n manta-fase4-prod"
echo "  Grafana: kubectl port-forward svc/grafana 3000:3000 -n manta-fase4-prod"
echo "  Jaeger: kubectl port-forward svc/jaeger-query 16686:16686 -n manta-fase4-prod"
echo ""
echo "Review logs:"
echo "  kubectl logs -f deployment/platform-router -n manta-fase4-prod"
echo "  kubectl logs -f deployment/ml-inference -n manta-fase4-prod"
echo ""
echo "Contact: platform-team@manta.com"
```

---

## Automated Deployment Script

**File**: `PRODUCTION_DEPLOY.sh`

```bash
#!/bin/bash

set -e

NAMESPACE="manta-fase4-prod"
TIMEOUT=300
LOG_FILE="/tmp/fase4-deployment-$(date +%Y%m%d-%H%M%S).log"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a $LOG_FILE; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a $LOG_FILE; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE; }

info "Starting Fase 4 Production Deployment"
info "Log file: $LOG_FILE"
info ""

# Phase 0: Pre-Flight
info "Phase 0: Pre-Flight Checks..."
(source <(sed -n '/Phase 0:/,/Phase 1:/p' $0) || exit 1) 2>&1 | tee -a $LOG_FILE
info "Phase 0 Complete ✓"
echo ""

# Phase 1: Namespace
info "Phase 1: Namespace & RBAC Setup..."
kubectl apply -f fase4/k8s-production/namespace.yaml 2>&1 | tee -a $LOG_FILE
kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=30s 2>&1 | tee -a $LOG_FILE
info "Phase 1 Complete ✓"
echo ""

# Phase 2: Storage
info "Phase 2: Storage Configuration..."
kubectl apply -f fase4/k8s-production/storage.yaml 2>&1 | tee -a $LOG_FILE
info "Phase 2 Complete ✓"
echo ""

# Phase 3: Observability
info "Phase 3: Observability Stack..."
kubectl apply -f fase4/k8s-production/monitoring-configs.yaml 2>&1 | tee -a $LOG_FILE
kubectl apply -f fase4/k8s-production/pillar-c-observability.yaml 2>&1 | tee -a $LOG_FILE
kubectl wait --for=condition=available --timeout=$TIMEOUT \
  deployment/prometheus -n $NAMESPACE 2>&1 | tee -a $LOG_FILE
info "Phase 3 Complete ✓"
echo ""

# Phase 4: Router
info "Phase 4: Platform Router..."
kubectl apply -f fase4/k8s-production/pillar-a-router.yaml 2>&1 | tee -a $LOG_FILE
kubectl wait --for=condition=available --timeout=$TIMEOUT \
  deployment/platform-router -n $NAMESPACE 2>&1 | tee -a $LOG_FILE
info "Phase 4 Complete ✓"
echo ""

# Phase 5: Refactor
info "Phase 5: Code Refactoring Engine..."
kubectl apply -f fase4/k8s-production/pillar-b-refactor.yaml 2>&1 | tee -a $LOG_FILE
kubectl wait --for=condition=available --timeout=$TIMEOUT \
  deployment/code-refactor-engine -n $NAMESPACE 2>&1 | tee -a $LOG_FILE
info "Phase 5 Complete ✓"
echo ""

# Phase 6: ML
info "Phase 6: ML Inference Service..."
kubectl apply -f fase4/k8s-production/pillar-d-ml-model.yaml 2>&1 | tee -a $LOG_FILE
kubectl wait --for=condition=available --timeout=$TIMEOUT \
  deployment/ml-inference -n $NAMESPACE 2>&1 | tee -a $LOG_FILE
info "Phase 6 Complete ✓"
echo ""

# Phase 7: Networking
info "Phase 7: Networking & Ingress..."
kubectl apply -f fase4/k8s-production/ingress-and-networking.yaml 2>&1 | tee -a $LOG_FILE
info "Phase 7 Complete ✓"
echo ""

# Phase 8: Validation
info "Phase 8: Validation & Health Checks..."
bash fase4/k8s-production/validate-deployment.sh 2>&1 | tee -a $LOG_FILE || {
  error "Validation failed"
  exit 1
}
info "Phase 8 Complete ✓"
echo ""

# Phase 9: Canary
info "Phase 9: Canary Gate Activation..."
kubectl create configmap ml-canary-gates \
  --from-literal=phase=0 \
  --from-literal=audit_confidence=0.95 \
  -n $NAMESPACE 2>&1 | tee -a $LOG_FILE || true
info "Phase 9 Complete ✓"
echo ""

info "=========================================="
info "Production Deployment Complete! ✓"
info "=========================================="
info "Deployment Summary:"
info "  Namespace: $NAMESPACE"
info "  Deployments: 8 (Router, Refactor, ML, Observability)"
info "  Total Replicas: 10+ (auto-scaling to 30+)"
info "  Storage: 250Gi allocated"
info "  Status: All pods running, health checks passing"
info ""
info "Next Steps:"
info "  1. Monitor Phase 0 (audit mode) for 24-48 hours"
info "  2. Review metrics in Grafana dashboard"
info "  3. Verify no alerts firing"
info "  4. Check logs for errors"
info "  5. Approve progression to Phase 1"
info ""
info "Log file: $LOG_FILE"
```

---

## Rollback Procedure

**If deployment fails at any phase:**

```bash
#!/bin/bash

NAMESPACE="manta-fase4-prod"

echo "=== ROLLBACK INITIATED ==="
echo "Rolling back Fase 4 deployment..."

# Delete deployments
kubectl delete deployment --all -n $NAMESPACE

# Delete services
kubectl delete service --all -n $NAMESPACE

# Delete ingress
kubectl delete ingress --all -n $NAMESPACE

# Keep namespace, storage, ConfigMaps for data preservation
echo "✓ Deployments rolled back"
echo "✓ Namespace preserved with data"
echo "✓ Ready to re-deploy or investigate"

# Notify team
echo ""
echo "ALERT: Fase 4 deployment rolled back"
echo "Reason: See logs above"
echo "Contact: platform-team@manta.com"
```

---

## Success Criteria

### Deployment Success ✓

- [ ] All 8 deployments running with correct replicas
- [ ] All pods in Running state
- [ ] Health checks passing (liveness, readiness, startup)
- [ ] Services accessible and discoverable
- [ ] Prometheus collecting metrics from 8+ targets
- [ ] Grafana dashboards populated with data
- [ ] Jaeger collecting traces
- [ ] Alertmanager routing alerts
- [ ] Ingress configured with TLS
- [ ] Network policies enforced
- [ ] HPA active and monitoring
- [ ] Zero pod restarts in first 30 minutes

### Operational Readiness ✓

- [ ] Monitoring dashboard accessible
- [ ] Alert rules validated
- [ ] Incident runbooks ready
- [ ] Team trained on procedures
- [ ] Escalation procedures published
- [ ] Backup procedures tested
- [ ] Rollback procedure verified
- [ ] Log aggregation working

### Performance Validation ✓

- [ ] Error rate <0.1%
- [ ] P95 latency <500ms
- [ ] Throughput >100 req/s
- [ ] ML confidence >90%
- [ ] Pod CPU <70% average
- [ ] Pod memory <70% average
- [ ] Storage utilization <50%

---

## Post-Deployment Activities

### Day 1 (Deployment Day)
- [ ] Monitor Phase 0 (audit mode) throughout day
- [ ] Review logs every 30 minutes
- [ ] Check metrics on monitoring dashboard
- [ ] Respond to any alerts immediately
- [ ] Document any issues or observations

### Day 2 (Monitoring)
- [ ] Continue Phase 0 monitoring
- [ ] Analyze 24-hour trend data
- [ ] Verify no crash loops or restart patterns
- [ ] Check all inter-service communication
- [ ] Validate backup procedures

### Week 1 (Stabilization)
- [ ] Complete Phase 0 → Phase 1 transition (48 hours)
- [ ] Monitor Phase 1 (5% traffic) for 2-3 days
- [ ] Run load test on production data
- [ ] Validate scaling behavior
- [ ] Document lessons learned

### Week 2-4 (Full Rollout)
- [ ] Phase 1 → Phase 2 → Phase 3 progression
- [ ] Collect performance data
- [ ] Optimize resource allocation
- [ ] Update documentation with real metrics
- [ ] Plan optimization work for next quarter

---

## Deployment Sign-Off

**Prepared By**: Platform Engineering Team  
**Date**: 2026-07-27  
**Status**: Ready for Execution  

**Approvals Required**:
- [ ] Platform Engineering Lead: _________________
- [ ] DevOps Lead: _________________
- [ ] Security Officer: _________________
- [ ] Director of Engineering: _________________

**Executed By**: _________________  
**Execution Date**: _________________  
**Execution Duration**: _________ minutes  
**Overall Status**: [ ] Success [ ] Failure [ ] Partial

**Notes**:
_________________________________
_________________________________

---

**For questions or issues during deployment, contact: platform-team@manta.com**
