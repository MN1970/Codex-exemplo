#!/usr/bin/env bash

################################################################################
# Manta Maestro — Automated Development Environment Setup
################################################################################
# Usage: ./scripts/setup-dev.sh [OPTIONS]
#
# Options:
#   --skip-build       Skip Docker image build (use existing images)
#   --skip-db          Skip database initialization (assume already initialized)
#   --skip-seed        Skip test data seeding
#   --reset-db         Drop and recreate database (destructive!)
#   --help             Show this help message
#
# This script performs the following:
#   1. Validates Docker & Docker Compose installation
#   2. Validates project structure
#   3. Copies .env.example to .env (if not exists)
#   4. Builds Docker images
#   5. Starts services (up -d)
#   6. Runs database migrations (alembic upgrade head)
#   7. Seeds test data (optional)
#   8. Waits for all services to be healthy
#   9. Prints access URLs and next steps
#
# Exit codes:
#   0  = Success
#   1  = Required tool missing (Docker, Docker Compose)
#   2  = Invalid project structure
#   3  = Docker command failed
#   4  = Database initialization failed
#   5  = Service health check timeout

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
readonly ENV_FILE="${PROJECT_ROOT}/.env"
readonly ENV_EXAMPLE="${PROJECT_ROOT}/.env.example"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration defaults
SKIP_BUILD=false
SKIP_DB=false
SKIP_SEED=false
RESET_DB=false
QUIET=false

# Service parameters
readonly HEALTHCHECK_TIMEOUT=180  # seconds
readonly HEALTHCHECK_INTERVAL=5   # seconds
readonly DATABASE_WAIT_TIMEOUT=60 # seconds

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

die() {
    local exit_code=$1
    shift
    log_error "$@"
    exit "$exit_code"
}

show_help() {
    sed -n '/^# Usage:/,/^[^#]/p' "$0" | grep '^#' | cut -c3- | head -n -1
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

check_docker() {
    log_info "Checking Docker installation..."

    if ! command -v docker &> /dev/null; then
        die 1 "Docker not found. Please install Docker: https://docs.docker.com/get-docker/"
    fi

    log_success "Docker found: $(docker --version)"
}

check_docker_compose() {
    log_info "Checking Docker Compose installation..."

    if ! command -v docker-compose &> /dev/null; then
        die 1 "Docker Compose not found. Please install it: https://docs.docker.com/compose/install/"
    fi

    log_success "Docker Compose found: $(docker-compose --version)"
}

check_project_structure() {
    log_info "Validating project structure..."

    local required_files=(
        "docker-compose.yml"
        "manta-backend/Dockerfile"
        "manta-backend/requirements.txt"
        "manta-backend/alembic.ini"
        "manta-frontend/package.json"
        "manta-frontend/Dockerfile.dev"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "${PROJECT_ROOT}/${file}" ]]; then
            die 2 "Missing required file: ${file}"
        fi
    done

    log_success "Project structure is valid"
}

# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

setup_env_file() {
    log_info "Setting up environment file..."

    if [[ -f "$ENV_FILE" ]]; then
        log_warning ".env already exists, skipping copy"
        return 0
    fi

    if [[ ! -f "$ENV_EXAMPLE" ]]; then
        die 2 ".env.example not found at ${ENV_EXAMPLE}"
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"
    log_success "Copied .env.example → .env"
    log_warning "Please review and customize ${ENV_FILE} before proceeding"
}

build_images() {
    if [[ "$SKIP_BUILD" == true ]]; then
        log_warning "Skipping Docker image build (--skip-build flag set)"
        return 0
    fi

    log_info "Building Docker images..."

    cd "$PROJECT_ROOT"

    if ! docker-compose build --no-cache 2>&1 | tee /tmp/docker-build.log; then
        die 3 "Docker build failed. Check /tmp/docker-build.log"
    fi

    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services with docker-compose..."

    cd "$PROJECT_ROOT"

    if ! docker-compose up -d 2>&1 | tee /tmp/docker-up.log; then
        die 3 "docker-compose up failed. Check /tmp/docker-up.log"
    fi

    log_success "Services started (detached mode)"
    sleep 5  # Give services time to initialize
}

wait_for_database() {
    if [[ "$SKIP_DB" == true ]]; then
        log_warning "Skipping database wait (--skip-db flag set)"
        return 0
    fi

    log_info "Waiting for PostgreSQL to be ready (timeout: ${DATABASE_WAIT_TIMEOUT}s)..."

    local elapsed=0
    local interval=2

    while [[ $elapsed -lt $DATABASE_WAIT_TIMEOUT ]]; do
        if docker-compose exec -T db pg_isready -U manta -d manta &> /dev/null; then
            log_success "PostgreSQL is ready"
            return 0
        fi
        sleep "$interval"
        elapsed=$((elapsed + interval))
        echo -n "." >&2
    done

    die 4 "PostgreSQL did not become ready within ${DATABASE_WAIT_TIMEOUT}s"
}

run_migrations() {
    if [[ "$SKIP_DB" == true ]]; then
        log_warning "Skipping database migrations (--skip-db flag set)"
        return 0
    fi

    log_info "Running database migrations..."

    if [[ "$RESET_DB" == true ]]; then
        log_warning "Dropping and recreating database (--reset-db flag set)..."
        docker-compose exec -T db psql -U manta -d postgres -c "DROP DATABASE IF EXISTS manta WITH (FORCE);"
        docker-compose exec -T db psql -U manta -d postgres -c "CREATE DATABASE manta;"
    fi

    # Run Alembic migrations
    if ! docker-compose exec -T backend sh -c "cd /app && alembic upgrade head" 2>&1 | tee /tmp/alembic.log; then
        die 4 "Alembic migrations failed. Check /tmp/alembic.log"
    fi

    log_success "Database migrations completed"
}

seed_test_data() {
    if [[ "$SKIP_SEED" == true ]]; then
        log_warning "Skipping test data seeding (--skip-seed flag set)"
        return 0
    fi

    log_info "Seeding test data..."

    # Create a simple SQL script to seed data
    local seed_script="
    -- Insert test agents (10 agents with different statuses)
    INSERT INTO agents (id, name, status, created_at)
    SELECT
        'agent-' || i,
        'Test Agent ' || i,
        CASE WHEN i % 3 = 0 THEN 'active' WHEN i % 3 = 1 THEN 'inactive' ELSE 'archived' END,
        NOW() - INTERVAL '1 day' * i
    FROM generate_series(1, 10) AS i
    ON CONFLICT DO NOTHING;

    -- Insert test RAG chunks (100 chunks with embeddings)
    INSERT INTO rag_chunks (id, content, metadata, created_at)
    SELECT
        'chunk-' || i,
        'Test RAG chunk ' || i || ': Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        jsonb_build_object('source', 'test_data', 'index', i),
        NOW() - INTERVAL '1 hour'
    FROM generate_series(1, 100) AS i
    ON CONFLICT DO NOTHING;
    "

    if ! docker-compose exec -T db psql -U manta -d manta <<< "$seed_script" 2>&1 | tee /tmp/seed.log; then
        log_warning "Test data seeding had issues (non-fatal). Check /tmp/seed.log"
        # Don't die, as test data is optional
    else
        log_success "Test data seeded successfully (10 agents, 100 RAG chunks)"
    fi
}

wait_for_services() {
    log_info "Waiting for all services to be healthy (timeout: ${HEALTHCHECK_TIMEOUT}s)..."

    local elapsed=0
    local services=("backend" "db" "redis" "frontend")

    while [[ $elapsed -lt $HEALTHCHECK_TIMEOUT ]]; do
        local all_healthy=true

        for service in "${services[@]}"; do
            local state=$(docker-compose ps --services --filter "status=running" | grep -x "$service" || true)

            if [[ -z "$state" ]]; then
                all_healthy=false
                echo -n "." >&2
                break
            fi
        done

        if [[ "$all_healthy" == true ]]; then
            log_success "All services are running"
            return 0
        fi

        sleep "$HEALTHCHECK_INTERVAL"
        elapsed=$((elapsed + HEALTHCHECK_INTERVAL))
    done

    log_warning "Some services may not be fully healthy yet, but they are starting"
}

print_summary() {
    log_info "Printing service URLs and connection details..."

    cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}
${GREEN}║         Manta Maestro Development Environment Ready!              ║${NC}
${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}

${BLUE}Service URLs:${NC}
  • Backend API:        ${GREEN}http://localhost:8000${NC}
    - OpenAPI Docs:    ${GREEN}http://localhost:8000/docs${NC}
    - ReDoc:           ${GREEN}http://localhost:8000/redoc${NC}
    - Health Check:    ${GREEN}http://localhost:8000/admin/health${NC}

  • Frontend (React):   ${GREEN}http://localhost:5173${NC}

  • PostgreSQL:         ${BLUE}localhost:5432${NC}
    - User:            ${BLUE}manta${NC}
    - Password:        ${BLUE}mantadev${NC}
    - Database:        ${BLUE}manta${NC}

  • Redis:              ${BLUE}localhost:6379${NC}
    - Database:        ${BLUE}0${NC}

${BLUE}Common Tasks:${NC}
  • View logs:          docker-compose logs -f [service]
  • Rebuild images:     docker-compose build --no-cache [service]
  • Reset database:     ./scripts/setup-dev.sh --reset-db
  • Run shell:          docker-compose exec backend bash
  • Stop services:      docker-compose down

${BLUE}Development Tips:${NC}
  • Backend auto-reloads on file changes (uvicorn --reload)
  • Frontend has hot module replacement (HMR) at port 5173
  • Database changes: run migrations in /manta-backend/alembic/versions/
  • Tests: docker-compose exec backend pytest tests/
  • Lint: docker-compose exec frontend npm run lint
  • API testing: curl -X GET http://localhost:8000/admin/health

${BLUE}Environment File:${NC}
  ${YELLOW}${ENV_FILE}${NC}
  Customize as needed for your environment.

${BLUE}Documentation:${NC}
  See docs/DOCKER_SETUP.md for detailed troubleshooting and tuning.

${GREEN}✓ Setup complete! Start coding.${NC}

EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-build)  SKIP_BUILD=true; shift ;;
            --skip-db)     SKIP_DB=true; shift ;;
            --skip-seed)   SKIP_SEED=true; shift ;;
            --reset-db)    RESET_DB=true; shift ;;
            --quiet)       QUIET=true; shift ;;
            --help|-h)     show_help; exit 0 ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "Manta Maestro Development Environment Setup"
    log_info "Project root: ${PROJECT_ROOT}"
    log_info ""

    # Pre-flight checks
    check_docker
    check_docker_compose
    check_project_structure

    log_info ""
    log_info "Starting setup process..."
    log_info ""

    # Setup steps
    setup_env_file
    build_images
    start_services
    wait_for_database
    run_migrations
    seed_test_data
    wait_for_services

    log_info ""
    print_summary

    log_success "Development environment is ready!"
    exit 0
}

# Run main
main "$@"
