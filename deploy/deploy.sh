#!/bin/bash
# Maestro APScheduler v5.0 — Deployment Helper Script
# Usage: ./deploy/deploy.sh [systemd|docker|kubernetes] [staging|production]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_MODE="${1:-docker}"
ENVIRONMENT="${2:-staging}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/maestro-deploy-${TIMESTAMP}.log"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"
}

# Print header
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║      Maestro APScheduler v5.0 — Deployment Helper         ║"
    echo "║             Mode: $DEPLOY_MODE | Environment: $ENVIRONMENT"
    echo "║                     $(date '+%Y-%m-%d %H:%M:%S')"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Validation function
validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi
    log_success "Python $(python3 --version | cut -d' ' -f2) found"

    # Check VERSIONS.json
    if [ ! -f "$REPO_ROOT/VERSIONS.json" ]; then
        log_error "VERSIONS.json not found at $REPO_ROOT"
        exit 1
    fi
    log_success "VERSIONS.json valid"

    # Check CLAUDE.md
    if ! grep -q "v5.0" "$REPO_ROOT/CLAUDE.md"; then
        log_error "CLAUDE.md missing v5.0 marker"
        exit 1
    fi
    log_success "CLAUDE.md v5.0 found"

    # Check environment file
    if [ ! -f "$REPO_ROOT/.env" ]; then
        if [ -f "$REPO_ROOT/.env.example" ]; then
            log_warning ".env not found, creating from .env.example"
            cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
            log_warning "Please update .env with your actual credentials"
            exit 1
        else
            log_error ".env file not found"
            exit 1
        fi
    fi
    log_success ".env file found"
}

# Health check function
health_check() {
    local url="$1"
    local max_retries=30
    local retry_count=0

    log_info "Waiting for service to be healthy ($url)..."

    while [ $retry_count -lt $max_retries ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "Service is healthy"
            return 0
        fi

        retry_count=$((retry_count + 1))
        sleep 2
    done

    log_error "Service failed to become healthy after $((max_retries * 2))s"
    return 1
}

# Deploy function for Systemd
deploy_systemd() {
    log_info "Deploying with Systemd..."

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "Systemd deployment requires root privileges"
        exit 1
    fi

    # Create maestro user
    if ! id "maestro" &>/dev/null; then
        log_info "Creating maestro user..."
        useradd -r -s /bin/bash -d /opt/maestro maestro
        log_success "maestro user created"
    fi

    # Create directories
    mkdir -p /opt/maestro
    mkdir -p /var/log/maestro
    mkdir -p /etc/maestro

    log_info "Copying application files..."
    cp -r "$REPO_ROOT"/* /opt/maestro/
    chown -R maestro:maestro /opt/maestro /var/log/maestro /etc/maestro
    chmod 755 /opt/maestro /var/log/maestro

    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip3 install --upgrade pip
    pip3 install schedule requests prometheus-client python-dotenv pydantic

    # Copy .env to /etc/maestro
    log_info "Setting up environment..."
    cp "$REPO_ROOT/.env" /etc/maestro/.env
    chmod 600 /etc/maestro/.env
    chown maestro:maestro /etc/maestro/.env

    # Install systemd service
    log_info "Installing systemd service..."
    cp "$REPO_ROOT/deploy/maestro-apscheduler.service" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable maestro-apscheduler

    # Start service
    log_info "Starting maestro-apscheduler service..."
    systemctl start maestro-apscheduler

    # Health check
    sleep 3
    if systemctl is-active --quiet maestro-apscheduler; then
        log_success "maestro-apscheduler service started successfully"
    else
        log_error "Failed to start maestro-apscheduler service"
        journalctl -u maestro-apscheduler -n 20
        exit 1
    fi

    # Test health endpoint
    if health_check "http://localhost:8080/health"; then
        log_success "Systemd deployment completed successfully"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Deploy function for Docker Compose
deploy_docker() {
    log_info "Deploying with Docker Compose..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found"
        exit 1
    fi
    log_success "Docker $(docker --version | cut -d' ' -f3) found"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found"
        exit 1
    fi
    log_success "Docker Compose $(docker-compose --version | cut -d' ' -f3) found"

    # Build image
    log_info "Building Docker image..."
    docker build \
        -f "$REPO_ROOT/deploy/Dockerfile" \
        -t maestro-scheduler:latest \
        -t "maestro-scheduler:$ENVIRONMENT-$TIMESTAMP" \
        "$REPO_ROOT"

    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi

    # Start services
    log_info "Starting Docker Compose services..."
    cd "$REPO_ROOT/deploy" || exit 1
    docker-compose up -d

    if [ $? -eq 0 ]; then
        log_success "Docker services started"
    else
        log_error "Docker Compose failed"
        exit 1
    fi

    # Wait for startup
    sleep 5

    # Health check
    if health_check "http://localhost:8080/health"; then
        log_success "Docker deployment completed successfully"
        echo ""
        echo "Services:"
        echo "  - Maestro Scheduler: http://localhost:8080"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000"
        echo "  - AlertManager: http://localhost:9093"
    else
        log_error "Health check failed"
        docker-compose logs maestro-scheduler
        exit 1
    fi
}

# Deploy function for Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found"
        exit 1
    fi
    log_success "kubectl $(kubectl version --client=true 2>/dev/null | grep 'Client' | cut -d' ' -f3) found"

    # Create namespace
    log_info "Creating maestro namespace..."
    kubectl create namespace maestro --dry-run=client -o yaml | kubectl apply -f -

    # Create secrets
    log_info "Creating Kubernetes secrets..."
    if [ -f "$REPO_ROOT/.env" ]; then
        source "$REPO_ROOT/.env"
        kubectl create secret generic maestro-secrets \
            --from-literal=database-url="$DATABASE_URL" \
            --from-literal=slack-webhook="$SLACK_WEBHOOK_URL" \
            -n maestro \
            --dry-run=client -o yaml | kubectl apply -f -
        log_success "Secrets created"
    else
        log_error ".env file not found for secrets"
        exit 1
    fi

    # Apply manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f "$REPO_ROOT/deploy/k8s/maestro-scheduler-statefulset.yaml"

    # Wait for rollout
    log_info "Waiting for deployment to be ready..."
    kubectl rollout status statefulset/maestro-scheduler -n maestro --timeout=5m

    if [ $? -eq 0 ]; then
        log_success "Kubernetes deployment completed successfully"
        echo ""
        echo "Check service status:"
        echo "  kubectl get pods -n maestro"
        echo "  kubectl logs maestro-scheduler-0 -n maestro"
    else
        log_error "Kubernetes deployment failed"
        exit 1
    fi
}

# Run healthcheck
run_healthcheck() {
    log_info "Running healthchecks..."

    # Validate VERSIONS.json
    python3 "$REPO_ROOT/scripts/healthcheck.py"

    # Validate scheduler
    python3 -c "
from pathlib import Path
from scripts.apscheduler_setup import MaestroScheduler
scheduler = MaestroScheduler(Path('$REPO_ROOT'))
print(f'✓ Scheduler initialized with {len(scheduler.jobs)} jobs')
for name in scheduler.jobs:
    print(f'  - {name}')
"

    log_success "All healthchecks passed"
}

# Cleanup
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Deployment failed. Check logs at: $LOG_FILE"
    fi
}

trap cleanup EXIT

# Main execution
main() {
    print_header
    validate_prerequisites

    case "$DEPLOY_MODE" in
        systemd)
            deploy_systemd
            ;;
        docker)
            deploy_docker
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        *)
            log_error "Unknown deploy mode: $DEPLOY_MODE"
            echo "Usage: $0 [systemd|docker|kubernetes] [staging|production]"
            exit 1
            ;;
    esac

    run_healthcheck
    log_success "Deployment completed successfully!"
    echo ""
    echo "Logs: $LOG_FILE"
}

main "$@"
