#!/bin/bash

# Manta Maestro Kubernetes Auto-Scaling Setup Script
# Sets up Metrics Server, HPA, and Prometheus Adapter for auto-scaling
#
# Usage: ./scripts/setup-autoscaling.sh [command]
# Commands:
#   install    - Install metrics-server and prometheus-adapter
#   validate   - Verify auto-scaling setup
#   upgrade    - Upgrade existing setup
#   monitor    - Watch HPA scaling in real-time

set -e

NAMESPACE="manta"
KUBE_SYSTEM_NS="kube-system"
MONITORING_NS="monitoring"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    log_info "kubectl version: $(kubectl version --client --short)"
}

# Check cluster connectivity
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    log_info "Connected to cluster: $(kubectl config current-context)"
}

# Install Metrics Server
install_metrics_server() {
    log_info "Checking Metrics Server..."

    if kubectl get deployment metrics-server -n $KUBE_SYSTEM_NS &> /dev/null; then
        log_warn "Metrics Server is already installed"
        return
    fi

    log_info "Installing Metrics Server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

    log_info "Waiting for Metrics Server to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n $KUBE_SYSTEM_NS

    log_info "✓ Metrics Server installed successfully"
}

# Install Prometheus and Prometheus Adapter
install_prometheus_adapter() {
    log_info "Checking Prometheus Adapter..."

    # Create monitoring namespace
    if ! kubectl get namespace $MONITORING_NS &> /dev/null; then
        log_info "Creating namespace: $MONITORING_NS"
        kubectl create namespace $MONITORING_NS
    fi

    # Check if Helm is available
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install Helm 3+ first."
        exit 1
    fi

    log_info "Adding Prometheus Helm repository..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

    # Check if Prometheus Stack is already installed
    if helm list -n $MONITORING_NS | grep -q kube-prometheus-stack; then
        log_warn "Prometheus Stack is already installed"
    else
        log_info "Installing Prometheus Stack..."
        helm install kube-prometheus-stack \
            prometheus-community/kube-prometheus-stack \
            -n $MONITORING_NS \
            --set prometheus.prometheusSpec.retention=7d \
            --set grafana.adminPassword=admin
        log_info "✓ Prometheus Stack installed"
    fi

    # Check if Prometheus Adapter is already installed
    if helm list -n $MONITORING_NS | grep -q prometheus-adapter; then
        log_warn "Prometheus Adapter is already installed"
    else
        log_info "Installing Prometheus Adapter..."
        helm install prometheus-adapter \
            prometheus-community/prometheus-adapter \
            -n $MONITORING_NS \
            --set prometheus.url=http://kube-prometheus-stack-prometheus.monitoring:9090 \
            --set prometheus.port=9090
        log_info "✓ Prometheus Adapter installed"
    fi

    log_info "Waiting for Prometheus Adapter to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus-adapter -n $MONITORING_NS || true
}

# Deploy Manta Helm Chart with HPA enabled
deploy_manta_hpa() {
    log_info "Deploying Manta Maestro with HPA enabled..."

    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace $NAMESPACE
    fi

    log_info "Deploying Helm chart..."
    helm upgrade --install manta-maestro ./manta-helm \
        --namespace $NAMESPACE \
        --create-namespace \
        -f manta-helm/values.yaml \
        --set autoscaling.fastapi.enabled=true \
        --set autoscaling.react.enabled=true \
        --set autoscaling.postgres.enabled=true

    log_info "✓ Manta Maestro deployed with HPA"
}

# Validate auto-scaling setup
validate_autoscaling() {
    log_info "Validating auto-scaling setup..."

    # Check Metrics Server
    log_info "Checking Metrics Server..."
    if kubectl get deployment metrics-server -n $KUBE_SYSTEM_NS &> /dev/null; then
        STATUS=$(kubectl get deployment metrics-server -n $KUBE_SYSTEM_NS -o jsonpath='{.status.conditions[?(@.type=="Available")].status}')
        if [ "$STATUS" = "True" ]; then
            log_info "✓ Metrics Server is running"
        else
            log_warn "Metrics Server is not ready"
        fi
    else
        log_error "✗ Metrics Server is not installed"
    fi

    # Check metrics are available
    log_info "Checking metrics availability..."
    if kubectl top nodes &> /dev/null; then
        log_info "✓ Node metrics available"
        kubectl top nodes
    else
        log_error "✗ Node metrics not available"
    fi

    if kubectl top pods -n $NAMESPACE &> /dev/null; then
        log_info "✓ Pod metrics available"
        kubectl top pods -n $NAMESPACE
    else
        log_warn "Pod metrics not available yet (may take a few minutes)"
    fi

    # Check HPA resources
    log_info "Checking HPA resources..."
    if kubectl get hpa -n $NAMESPACE &> /dev/null; then
        log_info "✓ HPA resources found:"
        kubectl get hpa -n $NAMESPACE -o wide
    else
        log_error "✗ No HPA resources found in namespace $NAMESPACE"
    fi

    # Check Pod Disruption Budgets
    log_info "Checking Pod Disruption Budgets..."
    if kubectl get pdb -n $NAMESPACE &> /dev/null; then
        log_info "✓ Pod Disruption Budgets found:"
        kubectl get pdb -n $NAMESPACE
    else
        log_warn "No PDBs found (optional)"
    fi

    # Check Prometheus Adapter
    log_info "Checking Prometheus Adapter..."
    if kubectl get deployment prometheus-adapter -n $MONITORING_NS &> /dev/null; then
        STATUS=$(kubectl get deployment prometheus-adapter -n $MONITORING_NS -o jsonpath='{.status.conditions[?(@.type=="Available")].status}')
        if [ "$STATUS" = "True" ]; then
            log_info "✓ Prometheus Adapter is running"
        else
            log_warn "Prometheus Adapter is not ready"
        fi
    else
        log_warn "Prometheus Adapter is not installed (optional for custom metrics)"
    fi

    # Summary
    log_info "✓ Validation complete!"
}

# Watch HPA scaling in real-time
monitor_hpa() {
    log_info "Monitoring HPA scaling in real-time..."
    log_info "Press Ctrl+C to stop monitoring"
    log_info ""

    echo "=== HPA Status ==="
    kubectl get hpa -n $NAMESPACE -w

    log_info ""
    log_info "=== Pod Status ==="
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=api -w
}

# Show HPA detailed status
show_hpa_status() {
    log_info "HPA Status Overview"
    log_info ""
    kubectl get hpa -n $NAMESPACE -o wide
    log_info ""
    log_info "Detailed Status (First HPA):"
    kubectl describe hpa -n $NAMESPACE | head -50
}

# Clean up (optional)
cleanup() {
    log_warn "Removing HPA configuration from Helm values..."
    helm upgrade manta-maestro ./manta-helm \
        --namespace $NAMESPACE \
        --set autoscaling.fastapi.enabled=false \
        --set autoscaling.react.enabled=false \
        --set autoscaling.postgres.enabled=false

    log_info "HPA has been disabled"
}

# Main command dispatcher
main() {
    command=${1:-validate}

    check_kubectl
    check_cluster

    case "$command" in
        install)
            log_info "Installing auto-scaling components..."
            install_metrics_server
            install_prometheus_adapter
            deploy_manta_hpa
            log_info "✓ Auto-scaling installation complete!"
            ;;
        validate)
            validate_autoscaling
            ;;
        upgrade)
            log_info "Upgrading auto-scaling setup..."
            install_metrics_server
            install_prometheus_adapter
            deploy_manta_hpa
            validate_autoscaling
            ;;
        monitor)
            monitor_hpa
            ;;
        status)
            show_hpa_status
            ;;
        cleanup)
            cleanup
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Available commands:"
            echo "  install   - Install metrics-server and prometheus-adapter"
            echo "  validate  - Verify auto-scaling setup"
            echo "  upgrade   - Upgrade existing setup"
            echo "  monitor   - Watch HPA scaling in real-time"
            echo "  status    - Show detailed HPA status"
            echo "  cleanup   - Disable HPA configuration"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
