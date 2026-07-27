#!/bin/bash

set -e

NAMESPACE="manta-fase4-prod"
TIMEOUT=300
POLL_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Fase 4 Kubernetes Deployment Validation"
echo "================================================"
echo

# Function to print colored output
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
echo "1. Checking Prerequisites..."
echo "---"

if ! command -v kubectl &> /dev/null; then
    error "kubectl not found. Please install kubectl."
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    error "Cannot connect to Kubernetes cluster. Please configure kubeconfig."
    exit 1
fi

info "kubectl is available"
info "Kubernetes cluster is accessible"

# Check namespace exists
if kubectl get namespace $NAMESPACE &> /dev/null; then
    info "Namespace $NAMESPACE exists"
else
    error "Namespace $NAMESPACE does not exist"
    exit 1
fi

echo
echo "2. Checking Resource Quotas..."
echo "---"

if kubectl get resourcequota manta-fase4-quota -n $NAMESPACE &> /dev/null; then
    info "ResourceQuota is configured"
    kubectl describe resourcequota manta-fase4-quota -n $NAMESPACE
else
    error "ResourceQuota not found"
    exit 1
fi

echo
echo "3. Checking RBAC Configuration..."
echo "---"

if kubectl get serviceaccount manta-fase4-sa -n $NAMESPACE &> /dev/null; then
    info "ServiceAccount is configured"
else
    error "ServiceAccount not found"
    exit 1
fi

if kubectl get role manta-fase4-role -n $NAMESPACE &> /dev/null; then
    info "Role is configured"
else
    error "Role not found"
    exit 1
fi

if kubectl get rolebinding manta-fase4-rolebinding -n $NAMESPACE &> /dev/null; then
    info "RoleBinding is configured"
else
    error "RoleBinding not found"
    exit 1
fi

echo
echo "4. Checking Persistent Volumes..."
echo "---"

PVS=(ml-model-pv prometheus-pv elasticsearch-data-pv)
for pv in "${PVS[@]}"; do
    if kubectl get pv $pv &> /dev/null; then
        info "PersistentVolume $pv exists"
    else
        warn "PersistentVolume $pv not found"
    fi
done

echo
echo "5. Checking Deployments..."
echo "---"

DEPLOYMENTS=(
    "platform-router:3"
    "code-refactor-engine:2"
    "jaeger-collector:2"
    "ml-inference:3"
    "prometheus:1"
    "grafana:1"
    "alertmanager:1"
    "jaeger-query:1"
)

for deployment_info in "${DEPLOYMENTS[@]}"; do
    IFS=':' read -r deployment expected_replicas <<< "$deployment_info"

    if kubectl get deployment $deployment -n $NAMESPACE &> /dev/null; then
        actual_replicas=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.replicas}')
        ready_replicas=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')

        if [ "$ready_replicas" == "$expected_replicas" ]; then
            info "Deployment $deployment: $ready_replicas/$expected_replicas replicas ready"
        else
            warn "Deployment $deployment: $ready_replicas/$expected_replicas replicas ready (waiting...)"
        fi
    else
        error "Deployment $deployment not found"
    fi
done

echo
echo "6. Waiting for Deployments to be Ready..."
echo "---"

READY_DEPLOYMENTS=0
TOTAL_DEPLOYMENTS=${#DEPLOYMENTS[@]}
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    READY_DEPLOYMENTS=0

    for deployment_info in "${DEPLOYMENTS[@]}"; do
        IFS=':' read -r deployment expected_replicas <<< "$deployment_info"

        if kubectl get deployment $deployment -n $NAMESPACE &> /dev/null; then
            ready=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')

            if [ "$ready" == "$expected_replicas" ]; then
                ((READY_DEPLOYMENTS++))
            fi
        fi
    done

    if [ $READY_DEPLOYMENTS -eq $TOTAL_DEPLOYMENTS ]; then
        info "All deployments are ready!"
        break
    fi

    echo "Progress: $READY_DEPLOYMENTS/$TOTAL_DEPLOYMENTS deployments ready (waited ${ELAPSED}s)"
    sleep $POLL_INTERVAL
    ((ELAPSED += POLL_INTERVAL))
done

if [ $READY_DEPLOYMENTS -ne $TOTAL_DEPLOYMENTS ]; then
    error "Timeout waiting for deployments. Only $READY_DEPLOYMENTS/$TOTAL_DEPLOYMENTS are ready."
    exit 1
fi

echo
echo "7. Checking Pod Health..."
echo "---"

UNHEALTHY_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running,status.phase!=Succeeded -o name | wc -l)

if [ $UNHEALTHY_PODS -eq 0 ]; then
    info "All pods are running or succeeded"
else
    warn "$UNHEALTHY_PODS pods are not in Running/Succeeded state"
    kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running,status.phase!=Succeeded
fi

echo
echo "8. Checking Services..."
echo "---"

SERVICES=(
    "platform-router"
    "code-refactor-engine"
    "ml-inference"
    "jaeger-collector"
    "jaeger-query"
    "prometheus"
    "grafana"
    "alertmanager"
)

for service in "${SERVICES[@]}"; do
    if kubectl get service $service -n $NAMESPACE &> /dev/null; then
        cluster_ip=$(kubectl get service $service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
        info "Service $service: $cluster_ip"
    else
        error "Service $service not found"
    fi
done

echo
echo "9. Testing Pod Connectivity..."
echo "---"

# Test connectivity from platform-router to other services
echo "Testing platform-router connectivity..."
ROUTER_POD=$(kubectl get pods -n $NAMESPACE -l app=platform-router -o name | head -1)

if [ -n "$ROUTER_POD" ]; then
    # Test health endpoint
    if kubectl exec -it $ROUTER_POD -n $NAMESPACE -- curl -s http://localhost:8080/health/ready &> /dev/null; then
        info "platform-router health endpoint is responding"
    else
        warn "platform-router health endpoint is not responding"
    fi

    # Test connectivity to code-refactor-engine
    if kubectl exec -it $ROUTER_POD -n $NAMESPACE -- curl -s http://code-refactor-engine:8081/health/ready &> /dev/null; then
        info "platform-router can reach code-refactor-engine"
    else
        warn "platform-router cannot reach code-refactor-engine"
    fi
else
    warn "No platform-router pods found"
fi

echo
echo "10. Checking Network Policies..."
echo "---"

NETPOLS=$(kubectl get networkpolicy -n $NAMESPACE -o name | wc -l)
info "Found $NETPOLS network policies"

echo
echo "11. Checking HPA Configuration..."
echo "---"

HPAS=$(kubectl get hpa -n $NAMESPACE -o name)
if [ -n "$HPAS" ]; then
    info "Horizontal Pod Autoscalers configured:"
    kubectl get hpa -n $NAMESPACE
else
    warn "No HPA resources found"
fi

echo
echo "12. Checking Node Resources..."
echo "---"

NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
info "Cluster has $NODE_COUNT nodes"

TOTAL_CPU=$(kubectl get nodes -o json | jq -r '.items[] | .status.allocatable.cpu' | sed 's/m$//' | awk '{sum += $1} END {print sum}')
TOTAL_MEMORY=$(kubectl get nodes -o json | jq -r '.items[] | .status.allocatable.memory' | sed 's/Ki$//' | awk '{sum += $1} END {print int(sum / 1048576)}')

info "Total allocatable CPU: ${TOTAL_CPU}m ($(echo "scale=2; $TOTAL_CPU / 1000" | bc))"
info "Total allocatable memory: ${TOTAL_MEMORY}Gi"

echo
echo "13. Checking Monitoring Stack..."
echo "---"

# Check Prometheus targets
PROM_POD=$(kubectl get pods -n $NAMESPACE -l app=prometheus -o name | head -1)
if [ -n "$PROM_POD" ]; then
    info "Prometheus is running"
    # Get number of active targets
    TARGETS=$(kubectl exec -it $PROM_POD -n $NAMESPACE -- curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length' 2>/dev/null || echo "unknown")
    info "Active Prometheus targets: $TARGETS"
else
    warn "Prometheus pod not found"
fi

# Check Grafana
GRAFANA_POD=$(kubectl get pods -n $NAMESPACE -l app=grafana -o name | head -1)
if [ -n "$GRAFANA_POD" ]; then
    if kubectl exec -it $GRAFANA_POD -n $NAMESPACE -- curl -s http://localhost:3000/api/health &> /dev/null; then
        info "Grafana is responding to health checks"
    else
        warn "Grafana health check failed"
    fi
else
    warn "Grafana pod not found"
fi

# Check Jaeger
JAEGER_POD=$(kubectl get pods -n $NAMESPACE -l app=jaeger-collector -o name | head -1)
if [ -n "$JAEGER_POD" ]; then
    if kubectl exec -it $JAEGER_POD -n $NAMESPACE -- curl -s http://localhost:14269 &> /dev/null; then
        info "Jaeger Collector is responding"
    else
        warn "Jaeger Collector health check failed"
    fi
else
    warn "Jaeger Collector pod not found"
fi

echo
echo "================================================"
echo "Validation Summary"
echo "================================================"

if [ $READY_DEPLOYMENTS -eq $TOTAL_DEPLOYMENTS ] && [ $UNHEALTHY_PODS -eq 0 ]; then
    info "All validation checks PASSED!"
    info "Fase 4 deployment is ready for use"
    exit 0
else
    error "Some validation checks FAILED"
    error "Please review the output above and fix any issues"
    exit 1
fi
