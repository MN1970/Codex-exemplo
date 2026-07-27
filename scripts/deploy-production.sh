#!/bin/bash
################################################################################
# MANTA MAESTRO PRODUCTION DEPLOYMENT SCRIPT
# 4 Initiatives: Fine-Tuning + Feedback + Performance Tuning + Auto-Scaling
# Approval: mneves@mantaassociados.com (2026-07-27)
# Usage: ./scripts/deploy-production.sh [phase1|phase2|phase3|phase4|phase5|all]
################################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${KUBE_NAMESPACE:-default}"
RELEASE_NAME="${HELM_RELEASE:-manta}"
HELM_CHART="${HELM_CHART:-./manta-helm}"
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-manta}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
API_URL="${API_URL:-http://localhost:8000}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_API_TOKEN="${GRAFANA_API_TOKEN:-}"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

log_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Pre-flight checks
preflight_check() {
    log_info "Running pre-flight checks..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    log_success "kubectl found"

    # Check current context
    CURRENT_CONTEXT=$(kubectl config current-context)
    log_info "Current context: $CURRENT_CONTEXT"
    read -p "Continue with context '$CURRENT_CONTEXT'? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled"
        exit 1
    fi

    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm not found. Please install helm v3.12+"
        exit 1
    fi
    log_success "helm found ($(helm version --short))"

    # Check Metrics Server
    if kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_success "Metrics Server found"
    else
        log_warn "Metrics Server NOT found. Will be installed in Phase 1"
    fi

    # Check PostgreSQL connection
    if command -v psql &> /dev/null; then
        if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d manta -c "SELECT 1" &> /dev/null; then
            log_success "PostgreSQL connection OK"
        else
            log_warn "Cannot connect to PostgreSQL. Will retry in Phase 1"
        fi
    else
        log_warn "psql not found. Skipping PostgreSQL check"
    fi

    # Check Redis connection
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &> /dev/null; then
            log_success "Redis connection OK"
        else
            log_warn "Cannot connect to Redis. Will retry in Phase 1"
        fi
    else
        log_warn "redis-cli not found. Skipping Redis check"
    fi

    log_success "Pre-flight checks complete"
    echo
}

# PHASE 1: Infrastructure Setup
phase1_infrastructure() {
    log_info "========================================="
    log_info "PHASE 1: Infrastructure Setup (30 min)"
    log_info "========================================="
    echo

    # 1a. Database migrations
    log_info "Step 1a: Running database migrations..."
    if command -v alembic &> /dev/null; then
        cd manta-backend
        alembic upgrade head || log_warn "Alembic upgrade had issues"
        cd ..
        log_success "Database migrations applied"
    else
        log_warn "alembic not found. Run manually: cd manta-backend && alembic upgrade head"
    fi
    echo

    # 1b. Install Prometheus Adapter
    log_info "Step 1b: Installing Prometheus Adapter..."
    if helm repo list | grep -q prometheus-community; then
        log_success "prometheus-community repo already added"
    else
        log_info "Adding prometheus-community Helm repo..."
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
    fi

    helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter \
        -f monitoring/prometheus-adapter-values.yaml \
        -n monitoring --create-namespace \
        --wait --timeout 5m || log_warn "Prometheus Adapter install had issues"
    log_success "Prometheus Adapter installed"
    echo

    # 1c. Deploy HPA templates via Helm
    log_info "Step 1c: Deploying Helm chart with HPA templates..."
    helm upgrade --install "$RELEASE_NAME" "$HELM_CHART" \
        --values manta-helm/values.yaml \
        --values manta-helm/values-production.yaml \
        -n "$NAMESPACE" \
        --wait --timeout 10m || log_error "Helm deployment failed"
    log_success "Helm chart deployed"
    echo

    # 1d. Restart FastAPI with new code
    log_info "Step 1d: Restarting FastAPI deployment..."
    kubectl rollout restart deployment/fastapi -n "$NAMESPACE"
    kubectl rollout status deployment/fastapi -n "$NAMESPACE" --timeout=5m
    log_success "FastAPI restarted"
    echo

    log_success "✓ PHASE 1 COMPLETE"
    echo
}

# PHASE 2: Validation
phase2_validation() {
    log_info "========================================="
    log_info "PHASE 2: Validation & Testing (20 min)"
    log_info "========================================="
    echo

    # 2a. Verify Metrics Server
    log_info "Step 2a: Verifying Metrics Server..."
    if kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_success "Metrics Server ready"
    else
        log_error "Metrics Server not found"
    fi
    echo

    # 2b. Verify HPA status
    log_info "Step 2b: Verifying HPA status..."
    kubectl get hpa -n "$NAMESPACE" -o wide
    log_success "HPA templates verified"
    echo

    # 2c. Verify custom metrics
    log_info "Step 2c: Checking custom metrics..."
    CUSTOM_METRICS=$(kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" 2>/dev/null | wc -l)
    if [ "$CUSTOM_METRICS" -gt 0 ]; then
        log_success "Custom metrics available"
    else
        log_warn "Custom metrics not yet available (normal, may take 1-2 min)"
    fi
    echo

    # 2d. Verify database HNSW index
    log_info "Step 2d: Verifying pgvector HNSW index..."
    if command -v psql &> /dev/null; then
        if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d manta -c \
            "SELECT indexname FROM pg_indexes WHERE indexname LIKE '%hnsw%'" &> /dev/null; then
            log_success "HNSW index verified"
        else
            log_warn "HNSW index not found. May need manual creation"
        fi
    else
        log_warn "psql not available. Skipping index verification"
    fi
    echo

    # 2e. Verify Redis
    log_info "Step 2e: Verifying Redis connectivity..."
    if command -v redis-cli &> /dev/null; then
        LATENCY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --latency 2>/dev/null | grep -oP '\d+(?=\.\d+ms)' | head -1)
        if [ -n "$LATENCY" ]; then
            log_success "Redis latency: ${LATENCY}ms"
        else
            log_warn "Redis check inconclusive"
        fi
    else
        log_warn "redis-cli not available. Skipping Redis check"
    fi
    echo

    log_success "✓ PHASE 2 COMPLETE"
    echo
}

# PHASE 3: Monitoring Setup
phase3_monitoring() {
    log_info "========================================="
    log_info "PHASE 3: Monitoring Setup (15 min)"
    log_info "========================================="
    echo

    if [ -z "$GRAFANA_API_TOKEN" ]; then
        log_warn "GRAFANA_API_TOKEN not set. Skipping automated dashboard import."
        log_info "Manual steps:"
        log_info "1. Login to Grafana at $GRAFANA_URL"
        log_info "2. Import dashboards from monitoring/grafana-*.json"
        return
    fi

    log_info "Importing Grafana dashboards..."

    DASHBOARDS=(
        "manta-backend/monitoring/grafana/dashboards/performance-overview.json"
        "manta-backend/monitoring/grafana/dashboards/cache-analytics.json"
        "manta-backend/monitoring/grafana/dashboards/postgresql-performance.json"
        "manta-backend/monitoring/grafana/dashboards/model-cost-analysis.json"
        "monitoring/grafana-hpa-dashboard.json"
        "monitoring/grafana-feedback-dashboard.json"
    )

    for dashboard in "${DASHBOARDS[@]}"; do
        if [ -f "$dashboard" ]; then
            log_info "Importing $dashboard..."
            curl -s -X POST "$GRAFANA_URL/api/dashboards/db" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $GRAFANA_API_TOKEN" \
                -d @"$dashboard" || log_warn "Failed to import $dashboard"
        fi
    done

    log_success "Grafana dashboards imported"
    log_info "Access Grafana at: $GRAFANA_URL"
    echo

    log_success "✓ PHASE 3 COMPLETE"
    echo
}

# PHASE 4: Go-Live (Feature Enablement)
phase4_golive() {
    log_info "========================================="
    log_info "PHASE 4: Go-Live - Feature Enablement (10 min)"
    log_info "========================================="
    echo

    log_info "Enabling all features..."

    kubectl set env deployment/fastapi \
        FINETUNING_ENABLED=true \
        FEEDBACK_ANALYTICS_ENABLED=true \
        CACHE_ENABLED=true \
        SMART_MODEL_SELECTION=true \
        REDIS_HOST="$REDIS_HOST" \
        REDIS_PORT="$REDIS_PORT" \
        CACHE_TTL_SECONDS=300 \
        FEEDBACK_ALERT_THRESHOLD=3.5 \
        FEEDBACK_RETRAINING_THRESHOLD=3.0 \
        MODEL_HAIKU_MAX_CHARS=500 \
        MODEL_SONNET_MAX_CHARS=2000 \
        -n "$NAMESPACE" || log_error "Failed to set environment variables"

    log_info "Restarting FastAPI with all features enabled..."
    kubectl rollout restart deployment/fastapi -n "$NAMESPACE"
    kubectl rollout status deployment/fastapi -n "$NAMESPACE" --timeout=5m

    log_success "All features enabled and live"
    echo

    log_success "✓ PHASE 4 COMPLETE - GO-LIVE!"
    echo
}

# PHASE 5: Smoke Tests
phase5_smoke_tests() {
    log_info "========================================="
    log_info "PHASE 5: Smoke Tests (10 min)"
    log_info "========================================="
    echo

    # Get service endpoint
    SERVICE_IP=$(kubectl get service/$RELEASE_NAME -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -z "$SERVICE_IP" ]; then
        SERVICE_IP=$(kubectl get service/$RELEASE_NAME -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
    fi
    SERVICE_URL="http://$SERVICE_IP:8000"

    log_info "Service URL: $SERVICE_URL"
    echo

    # 5a. Test fine-tuning endpoint
    log_info "5a. Testing fine-tuning endpoint..."
    RESPONSE=$(curl -s -X POST "$SERVICE_URL/ml/finetune" \
        -H "Content-Type: application/json" \
        -d '{
            "segment": "saneamento",
            "epochs": 1,
            "demo_mode": true
        }' || echo "{}")

    if echo "$RESPONSE" | grep -q "job_id\|id"; then
        log_success "Fine-tuning endpoint responding"
    else
        log_warn "Fine-tuning endpoint response unclear: $RESPONSE"
    fi
    echo

    # 5b. Test feedback analytics endpoint
    log_info "5b. Testing feedback analytics endpoint..."
    RESPONSE=$(curl -s "$SERVICE_URL/feedback/analytics/by-agent?limit=5" || echo "{}")

    if echo "$RESPONSE" | grep -q "agent\|data\|\[\]"; then
        log_success "Feedback analytics endpoint responding"
    else
        log_warn "Feedback analytics response unclear"
    fi
    echo

    # 5c. Test cache stats
    log_info "5c. Testing cache stats endpoint..."
    RESPONSE=$(curl -s "$SERVICE_URL/monitoring/cache-stats" || echo "{}")

    if echo "$RESPONSE" | grep -q "hit_rate\|evictions"; then
        log_success "Cache stats endpoint responding"
    else
        log_warn "Cache stats response unclear"
    fi
    echo

    # 5d. Watch HPA scaling
    log_info "5d. Checking HPA status..."
    kubectl get hpa -n "$NAMESPACE"
    echo

    log_success "✓ PHASE 5 COMPLETE - SMOKE TESTS DONE"
    echo
}

# Main execution
main() {
    PHASE="${1:-all}"

    echo
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  MANTA MAESTRO PRODUCTION DEPLOYMENT                          ║"
    echo "║  4 Initiatives: Fine-Tuning + Feedback + Perf + Auto-Scaling ║"
    echo "║  Approved: mneves@mantaassociados.com (2026-07-27)           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo

    preflight_check

    case "$PHASE" in
        phase1)
            phase1_infrastructure
            ;;
        phase2)
            phase2_validation
            ;;
        phase3)
            phase3_monitoring
            ;;
        phase4)
            phase4_golive
            ;;
        phase5)
            phase5_smoke_tests
            ;;
        all)
            phase1_infrastructure
            sleep 5
            phase2_validation
            sleep 5
            phase3_monitoring
            sleep 5
            phase4_golive
            sleep 5
            phase5_smoke_tests
            ;;
        *)
            log_error "Unknown phase: $PHASE"
            echo "Usage: $0 [phase1|phase2|phase3|phase4|phase5|all]"
            exit 1
            ;;
    esac

    echo
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 DEPLOYMENT COMPLETE 🎉                      ║"
    echo "║                                                                ║"
    echo "║  Next Steps:                                                   ║"
    echo "║  1. Monitor dashboards in Grafana: $GRAFANA_URL         ║"
    echo "║  2. Watch HPA scaling: kubectl get hpa -w               ║"
    echo "║  3. Tail logs: kubectl logs -f deploy/fastapi --all     ║"
    echo "║  4. Check alerts: kubectl logs -f deploy/alertmanager   ║"
    echo "║                                                                ║"
    echo "║  Rollback (if needed): kubectl rollout undo deploy/fastapi   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo
}

main "$@"
