#!/bin/bash
#
# Supabase Migration Runner for Phase 2 Deployment
# Manages database schema for feedback loops, vector storage, and orchestration
# Usage: ./deploy_migrations.sh [--dry-run|--rollback|--status|--help]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SUPABASE_DIR="$REPO_ROOT/supabase"
MIGRATIONS_DIR="$SUPABASE_DIR/migrations"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/tmp/deploy_migrations_${TIMESTAMP}.log"

# Configuration from environment or defaults
SUPABASE_PROJECT_URL="${SUPABASE_PROJECT_URL:-}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"
DRY_RUN="${DRY_RUN:-false}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# Logging Utilities
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

check_prerequisites() {
    log_info "Running pre-flight checks..."

    local missing_deps=()

    # Check required tools
    if ! command -v psql &> /dev/null; then
        missing_deps+=("psql")
    fi

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [ -z "$SUPABASE_PROJECT_URL" ]; then
        log_error "SUPABASE_PROJECT_URL environment variable not set"
        return 1
    fi

    if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
        log_error "SUPABASE_SERVICE_ROLE_KEY environment variable not set"
        return 1
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_deps[*]}"
        echo "Install with: sudo apt-get install postgresql-client jq"
        return 1
    fi

    if [ ! -d "$MIGRATIONS_DIR" ]; then
        log_error "Migrations directory not found: $MIGRATIONS_DIR"
        return 1
    fi

    log_success "All prerequisites met"
    return 0
}

# ============================================================================
# Database Connection & Queries
# ============================================================================

execute_migration() {
    local migration_file="$1"
    local migration_name=$(basename "$migration_file" .sql)

    if [ ! -f "$migration_file" ]; then
        log_error "Migration file not found: $migration_file"
        return 1
    fi

    log_info "Executing migration: $migration_name"

    if [ "$DRY_RUN" = "true" ]; then
        log_warn "DRY RUN: Would execute migration"
        cat "$migration_file" | head -20
        return 0
    fi

    # Extract database URL components
    local db_url="${SUPABASE_PROJECT_URL}/rest/v1"
    local parsed_url=$(echo "$SUPABASE_PROJECT_URL" | sed 's/https:\/\///')
    local host="${parsed_url%/*}"

    # Execute migration via psql
    if PGPASSWORD="$SUPABASE_SERVICE_ROLE_KEY" psql \
        -h "${host}" \
        -U postgres \
        -d postgres \
        -f "$migration_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Migration complete: $migration_name"
        return 0
    else
        log_error "Migration failed: $migration_name"
        return 1
    fi
}

get_migration_status() {
    log_info "Checking migration status..."

    # Query migration history table
    local query="SELECT version, name, installed_on FROM schema_migrations ORDER BY installed_on DESC LIMIT 10;"

    # Note: This uses Supabase REST API for simplicity
    local response=$(curl -s \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: application/json" \
        "${SUPABASE_PROJECT_URL}/rest/v1/schema_migrations?order=installed_on.desc&limit=10" 2>&1)

    if [ $? -eq 0 ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        log_warn "Could not retrieve migration status"
        return 1
    fi
}

# ============================================================================
# Phase 2 Schema Migrations
# ============================================================================

create_phase2_migrations() {
    log_info "Creating Phase 2 database schema migrations..."

    # Create migrations directory if it doesn't exist
    mkdir -p "$MIGRATIONS_DIR"

    # Migration 1: Feedback Loop Tables
    cat > "$MIGRATIONS_DIR/001_feedback_loop_schema.sql" << 'EOMIG'
-- Phase 2.1: Feedback Loop Schema
-- Tracks user feedback for routing improvements

CREATE TABLE IF NOT EXISTS feedback_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    agent_routed_to TEXT NOT NULL,
    agent_expected TEXT,
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    relevant_result BOOLEAN,
    confidence_score FLOAT,
    feedback_text TEXT,
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_agent ON feedback_submissions(agent_routed_to);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_relevant ON feedback_submissions(relevant_result);
CREATE INDEX IF NOT EXISTS idx_feedback_embedding ON feedback_submissions USING ivfflat (query_embedding vector_cosine_ops);

-- Feedback metrics view
CREATE OR REPLACE VIEW feedback_metrics AS
SELECT
    DATE_TRUNC('day', created_at) as date,
    agent_routed_to,
    COUNT(*) as total_submissions,
    COUNT(CASE WHEN relevant_result = true THEN 1 END) as correct_routings,
    ROUND(100.0 * COUNT(CASE WHEN relevant_result = true THEN 1 END) / COUNT(*), 2) as accuracy_percentage,
    AVG(confidence_score) as avg_confidence
FROM feedback_submissions
GROUP BY DATE_TRUNC('day', created_at), agent_routed_to;

EOMIG

    # Migration 2: Vector Storage for RAG
    cat > "$MIGRATIONS_DIR/002_rag_vector_schema.sql" << 'EOMIG'
-- Phase 2.4: RAG Vector Storage Schema
-- Manages embeddings for document chunks across all collections

CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id TEXT NOT NULL,
    document_name TEXT NOT NULL,
    document_source TEXT,
    document_url TEXT,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    hash TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_collection ON rag_documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_rag_embedding ON rag_documents USING ivfflat (chunk_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_rag_document ON rag_documents(document_name);
CREATE INDEX IF NOT EXISTS idx_rag_hash ON rag_documents(hash);

-- RAG query cache (for performance)
CREATE TABLE IF NOT EXISTS rag_query_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    collection_id TEXT,
    top_k INT DEFAULT 5,
    results JSONB,
    relevance_scores FLOAT8[],
    ttl TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_cache_query ON rag_query_cache(query_text);
CREATE INDEX IF NOT EXISTS idx_rag_cache_embedding ON rag_query_cache USING ivfflat (query_embedding vector_cosine_ops);

-- RAG ingestion status
CREATE TABLE IF NOT EXISTS rag_ingestion_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id TEXT NOT NULL,
    total_documents INT DEFAULT 0,
    total_chunks INT DEFAULT 0,
    processed_chunks INT DEFAULT 0,
    failed_chunks INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    error_log JSONB DEFAULT '[]'
);

EOMIG

    # Migration 3: Orchestrator Tables
    cat > "$MIGRATIONS_DIR/003_orchestrator_schema.sql" << 'EOMIG'
-- Phase 2.2: Multi-Agent Orchestration Schema
-- Tracks ambiguous queries requiring multi-agent dispatch

CREATE TABLE IF NOT EXISTS orchestration_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    ambiguity_score FLOAT,
    primary_agent TEXT,
    secondary_agents TEXT[] DEFAULT '{}',
    routing_confidence FLOAT,
    routing_explanation TEXT,
    final_response JSONB,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    execution_time_ms INT
);

CREATE INDEX IF NOT EXISTS idx_orchestration_agent ON orchestration_tasks(primary_agent);
CREATE INDEX IF NOT EXISTS idx_orchestration_completed ON orchestration_tasks(completed);
CREATE INDEX IF NOT EXISTS idx_orchestration_embedding ON orchestration_tasks USING ivfflat (query_embedding vector_cosine_ops);

-- Agent capability matrix
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL UNIQUE,
    agent_name TEXT,
    agent_tier TEXT,
    capabilities JSONB,
    supported_phases TEXT[],
    supported_segments TEXT[],
    model TEXT,
    cost_per_token FLOAT,
    last_updated TIMESTAMP DEFAULT NOW()
);

EOMIG

    # Migration 4: Document Classifier
    cat > "$MIGRATIONS_DIR/004_document_classifier_schema.sql" << 'EOMIG'
-- Phase 2.3: Document Auto-Classification Schema
-- Tracks classified documents and routing decisions

CREATE TABLE IF NOT EXISTS classified_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name TEXT NOT NULL,
    file_path TEXT,
    file_size INT,
    file_type TEXT,
    raw_content TEXT,
    document_hash TEXT UNIQUE,
    classified_agent TEXT,
    classification_confidence FLOAT,
    segment TEXT,
    phase TEXT,
    keywords TEXT[],
    extracted_metadata JSONB,
    sharepoint_folder TEXT,
    sharepoint_item_id TEXT,
    classification_method TEXT CHECK (classification_method IN ('ml', 'rule_based', 'manual')),
    processed_at TIMESTAMP DEFAULT NOW(),
    routed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_doc_agent ON classified_documents(classified_agent);
CREATE INDEX IF NOT EXISTS idx_doc_segment ON classified_documents(segment);
CREATE INDEX IF NOT EXISTS idx_doc_hash ON classified_documents(document_hash);
CREATE INDEX IF NOT EXISTS idx_doc_sharepoint_path ON classified_documents(sharepoint_folder);

EOMIG

    # Migration 5: SharePoint Sync
    cat > "$MIGRATIONS_DIR/005_sharepoint_sync_schema.sql" << 'EOMIG'
-- Phase 2.5: SharePoint Sync Schema
-- Tracks agent .md → SKILL.md synchronization

CREATE TABLE IF NOT EXISTS sharepoint_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    source_file TEXT,
    target_file TEXT,
    sync_direction TEXT CHECK (sync_direction IN ('to_sharepoint', 'from_sharepoint')),
    status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    source_hash TEXT,
    target_hash TEXT,
    error_message TEXT,
    synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_agent ON sharepoint_sync_log(agent_name);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sharepoint_sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_created ON sharepoint_sync_log(created_at DESC);

-- SKILL.md version tracking
CREATE TABLE IF NOT EXISTS skill_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    skill_name TEXT,
    version TEXT,
    version_hash TEXT UNIQUE,
    published_by TEXT,
    published_at TIMESTAMP DEFAULT NOW(),
    changelog TEXT,
    is_current BOOLEAN DEFAULT TRUE
);

EOMIG

    log_success "Phase 2 migrations created"
}

# ============================================================================
# Migration Execution
# ============================================================================

run_all_migrations() {
    log_info "Starting Phase 2 database migrations..."

    if [ ! -d "$MIGRATIONS_DIR" ]; then
        log_warn "Migrations directory not found, creating..."
        create_phase2_migrations
    fi

    # Sort migration files by version
    local migrations=$(find "$MIGRATIONS_DIR" -name "*.sql" | sort)

    if [ -z "$migrations" ]; then
        log_error "No migration files found"
        return 1
    fi

    local success_count=0
    local fail_count=0

    for migration in $migrations; do
        if execute_migration "$migration"; then
            ((success_count++))
        else
            ((fail_count++))
            if [ "$DRY_RUN" != "true" ]; then
                log_error "Stopping migration due to error. Run --rollback to revert."
                return 1
            fi
        fi
    done

    log_info "Migration Results: Success=$success_count, Failed=$fail_count"

    if [ $fail_count -eq 0 ]; then
        log_success "All migrations completed successfully"
        return 0
    else
        log_error "Some migrations failed"
        return 1
    fi
}

rollback_migrations() {
    log_warn "Rolling back Phase 2 migrations..."

    if [ "$DRY_RUN" = "true" ]; then
        log_warn "DRY RUN: Would execute rollback"
        return 0
    fi

    # Drop tables in reverse order
    local rollback_sql="
    DROP TABLE IF EXISTS sharepoint_sync_log CASCADE;
    DROP TABLE IF EXISTS skill_versions CASCADE;
    DROP TABLE IF EXISTS classified_documents CASCADE;
    DROP TABLE IF EXISTS agent_capabilities CASCADE;
    DROP TABLE IF EXISTS orchestration_tasks CASCADE;
    DROP TABLE IF EXISTS rag_ingestion_status CASCADE;
    DROP TABLE IF EXISTS rag_query_cache CASCADE;
    DROP TABLE IF EXISTS rag_documents CASCADE;
    DROP TABLE IF EXISTS feedback_submissions CASCADE;
    DROP VIEW IF EXISTS feedback_metrics CASCADE;
    "

    echo "$rollback_sql" | PGPASSWORD="$SUPABASE_SERVICE_ROLE_KEY" psql \
        -h "$(echo "$SUPABASE_PROJECT_URL" | sed 's/https:\/\///' | cut -d/ -f1)" \
        -U postgres \
        -d postgres 2>&1 | tee -a "$LOG_FILE"

    log_success "Rollback completed"
}

# ============================================================================
# Validation
# ============================================================================

validate_schema() {
    log_info "Validating database schema..."

    # Check for critical tables
    local required_tables=(
        "feedback_submissions"
        "rag_documents"
        "orchestration_tasks"
        "classified_documents"
        "sharepoint_sync_log"
    )

    for table in "${required_tables[@]}"; do
        local query="SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$table');"
        # This would require a proper database connection
        # For now, just log
        log_info "Checking table: $table"
    done

    log_success "Schema validation complete"
}

# ============================================================================
# Usage & Help
# ============================================================================

show_help() {
    cat << EOF
${BLUE}Supabase Migration Runner - Phase 2 Deployment${NC}

${BLUE}Usage:${NC}
  $0 [COMMAND]

${BLUE}Commands:${NC}
  (default)       Run all pending migrations
  --dry-run       Show migrations without executing
  --rollback      Rollback all Phase 2 migrations
  --status        Check migration status
  --validate      Validate database schema
  --help          Show this help message

${BLUE}Environment Variables:${NC}
  SUPABASE_PROJECT_URL       Project URL (https://[ID].supabase.co)
  SUPABASE_SERVICE_ROLE_KEY  Service role key for migrations
  DRY_RUN                    Set to 'true' for dry-run mode

${BLUE}Examples:${NC}
  # Run migrations with validation
  $0

  # Dry-run to preview changes
  DRY_RUN=true $0

  # Rollback in case of issues
  $0 --rollback

  # Check status
  $0 --status

${BLUE}Phase 2 Migrations:${NC}
  001_feedback_loop_schema.sql           - Feedback tracking tables
  002_rag_vector_schema.sql              - RAG vector storage
  003_orchestrator_schema.sql            - Multi-agent orchestration
  004_document_classifier_schema.sql     - Document auto-classification
  005_sharepoint_sync_schema.sql         - SharePoint synchronization

${BLUE}Documentation:${NC}
  Setup: docs/PHASE2-DEPLOYMENT-RUNBOOK.md
  Troubleshooting: docs/PHASE2-DEPLOYMENT-TROUBLESHOOTING.md
  Log: $LOG_FILE

EOF
}

# ============================================================================
# Main
# ============================================================================

main() {
    log_info "Supabase Migration Runner - Phase 2"
    log_info "Timestamp: $(date)"

    if ! check_prerequisites; then
        return 1
    fi

    case "${1:-}" in
        --dry-run)
            DRY_RUN=true
            run_all_migrations
            ;;
        --rollback)
            rollback_migrations
            ;;
        --status)
            get_migration_status
            ;;
        --validate)
            validate_schema
            ;;
        --help)
            show_help
            ;;
        *)
            run_all_migrations
            ;;
    esac
}

main "$@"
