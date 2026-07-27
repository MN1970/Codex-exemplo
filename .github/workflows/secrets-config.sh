#!/bin/bash
#
# Phase 2 GitHub Actions Secrets Configuration Script
# Configures all required secrets for Phase 2 deployment (RAG ingestion, orchestrator, etc.)
# Usage: ./secrets-config.sh [--interactive|--verify|--help]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/tmp/secrets-config_${TIMESTAMP}.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Logging and Output Utilities
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
# Phase 2 Secrets Definition
# ============================================================================

declare -A PHASE2_SECRETS=(
    # Anthropic Configuration
    ["ANTHROPIC_API_KEY"]="Anthropic API key (from console.anthropic.com/account/keys)"
    ["ANTHROPIC_MODEL_MAESTRO"]="Model for routing (usually claude-3-5-sonnet-20241022)"
    ["ANTHROPIC_MODEL_ORCHESTRATOR"]="Model for orchestration (usually claude-3-5-sonnet-20241022)"

    # Supabase Configuration
    ["SUPABASE_PROJECT_ID"]="Project ID from supabase.com/project/[ID]/settings/general"
    ["SUPABASE_PROJECT_URL"]="Full project URL (https://[PROJECT_ID].supabase.co)"
    ["SUPABASE_ANON_KEY"]="Anon public key from API settings"
    ["SUPABASE_SERVICE_ROLE_KEY"]="Service role key (for migrations and admin tasks)"
    ["SUPABASE_DB_PASSWORD"]="Postgres password for direct migrations (optional, use service role when possible)"

    # GCP Configuration
    ["GCP_PROJECT_ID"]="Google Cloud project ID"
    ["GCP_REGION"]="Default GCP region (us-central1 or us-east1 recommended)"
    ["GCP_VERTEX_AI_EMBEDDINGS_MODEL"]="Embeddings model (text-embedding-004)"
    ["GCP_SERVICE_ACCOUNT_JSON"]="Service account JSON key (base64 encoded for GitHub Actions)"

    # Microsoft Graph Configuration (SharePoint Sync)
    ["MICROSOFT_TENANT_ID"]="Azure AD tenant ID"
    ["MICROSOFT_CLIENT_ID"]="Azure AD app registration client ID"
    ["MICROSOFT_CLIENT_SECRET"]="Azure AD app registration client secret"
    ["SHAREPOINT_SITE_URL"]="SharePoint site URL (e.g., https://mantaassociados.sharepoint.com/sites/maestro)"
    ["SHAREPOINT_DRIVE_ID"]="SharePoint document library drive ID"

    # GitHub Configuration
    ["GITHUB_PAT"]="Personal Access Token with repo, workflow, and read:org scopes"
    ["GITHUB_ORGANIZATION"]="Organization name (MN1970)"
    ["GITHUB_REPOSITORY"]="Repository name (Codex-exemplo)"

    # Monitoring & Alerting
    ["CLOUDWATCH_ROLE_ARN"]="CloudWatch IAM role ARN for logging"
    ["CLOUDWATCH_LOG_GROUP"]="CloudWatch log group name (/maestro/phase2)"
    ["SLACK_WEBHOOK_URL"]="Slack incoming webhook for deployment notifications (optional)"

    # Phase 2 Specific
    ["FEEDBACK_DB_URL"]="Supabase PostgreSQL URL for feedback collection"
    ["VECTORSTORE_COLLECTION_NAME"]="Supabase vector collection name (pgvector)"
    ["ORCHESTRATOR_AGENT_ID"]="Manta 17 orchestrator agent ID"
    ["CLASSIFIER_AGENT_ID"]="Document classifier agent ID"
)

# ============================================================================
# Usage and Help
# ============================================================================

show_help() {
    cat << EOF
${BLUE}Phase 2 GitHub Actions Secrets Configuration${NC}

${BLUE}Usage:${NC}
  $0 [COMMAND]

${BLUE}Commands:${NC}
  --interactive    Run interactive setup wizard
  --verify         Verify all required secrets are configured
  --list           List all required secrets (with descriptions)
  --template       Generate secrets template for manual entry
  --export         Export secrets to .env file (use with caution!)
  --help           Show this help message

${BLUE}Examples:${NC}
  # Interactive wizard
  $0 --interactive

  # Verify existing secrets
  $0 --verify

  # List all required secrets
  $0 --list

  # Generate template
  $0 --template > secrets.env.template

${BLUE}Requirements:${NC}
  - GitHub CLI (gh) installed and authenticated
  - Permissions to configure repository secrets
  - Access to all services (Anthropic, Supabase, GCP, Microsoft)

${BLUE}Phase 2 Deployment Phases:${NC}
  Phase 2.1: Feedback Loop (database, analytics)
  Phase 2.2: Multi-Agent Orchestration (Manta 17, routing)
  Phase 2.3: Document Auto-Classification (MCP listener)
  Phase 2.4: RAG Batch Ingestion (embeddings, pgvector)
  Phase 2.5: SharePoint Sync Automation (Graph API, agent .md → SKILL.md)

${BLUE}Documentation:${NC}
  - Full setup guide: docs/PHASE2-DEPLOYMENT-RUNBOOK.md
  - Troubleshooting: docs/PHASE2-DEPLOYMENT-TROUBLESHOOTING.md
  - Log file: $LOG_FILE

EOF
}

# ============================================================================
# Interactive Setup Wizard
# ============================================================================

interactive_setup() {
    log_info "Starting Phase 2 secrets configuration wizard..."
    log_info "You will be prompted for each secret. Press Ctrl+C to cancel."

    local configured_count=0
    local failed_count=0

    # Section 1: Anthropic
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 1: Anthropic Configuration"
    log_info "═══════════════════════════════════════════════════════════════"

    read -sp "Enter ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
    echo ""
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        set_github_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY" && ((configured_count++)) || ((failed_count++))
    fi

    read -p "Enter ANTHROPIC_MODEL_MAESTRO (default: claude-3-5-sonnet-20241022): " model_maestro
    model_maestro="${model_maestro:-claude-3-5-sonnet-20241022}"
    set_github_secret "ANTHROPIC_MODEL_MAESTRO" "$model_maestro" && ((configured_count++)) || ((failed_count++))

    read -p "Enter ANTHROPIC_MODEL_ORCHESTRATOR (default: claude-3-5-sonnet-20241022): " model_orch
    model_orch="${model_orch:-claude-3-5-sonnet-20241022}"
    set_github_secret "ANTHROPIC_MODEL_ORCHESTRATOR" "$model_orch" && ((configured_count++)) || ((failed_count++))

    # Section 2: Supabase
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 2: Supabase Configuration"
    log_info "═══════════════════════════════════════════════════════════════"

    read -p "Enter SUPABASE_PROJECT_ID: " SUPABASE_PROJECT_ID
    set_github_secret "SUPABASE_PROJECT_ID" "$SUPABASE_PROJECT_ID" && ((configured_count++)) || ((failed_count++))

    read -p "Enter SUPABASE_PROJECT_URL (https://[ID].supabase.co): " SUPABASE_PROJECT_URL
    set_github_secret "SUPABASE_PROJECT_URL" "$SUPABASE_PROJECT_URL" && ((configured_count++)) || ((failed_count++))

    read -sp "Enter SUPABASE_ANON_KEY: " SUPABASE_ANON_KEY
    echo ""
    set_github_secret "SUPABASE_ANON_KEY" "$SUPABASE_ANON_KEY" && ((configured_count++)) || ((failed_count++))

    read -sp "Enter SUPABASE_SERVICE_ROLE_KEY: " SUPABASE_SERVICE_ROLE_KEY
    echo ""
    set_github_secret "SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_SERVICE_ROLE_KEY" && ((configured_count++)) || ((failed_count++))

    # Section 3: GCP
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 3: GCP Configuration"
    log_info "═══════════════════════════════════════════════════════════════"

    read -p "Enter GCP_PROJECT_ID: " GCP_PROJECT_ID
    set_github_secret "GCP_PROJECT_ID" "$GCP_PROJECT_ID" && ((configured_count++)) || ((failed_count++))

    read -p "Enter GCP_REGION (default: us-central1): " GCP_REGION
    GCP_REGION="${GCP_REGION:-us-central1}"
    set_github_secret "GCP_REGION" "$GCP_REGION" && ((configured_count++)) || ((failed_count++))

    read -p "Enter GCP service account JSON path (will be base64 encoded): " gcp_json_path
    if [ -f "$gcp_json_path" ]; then
        gcp_json_b64=$(base64 -w0 < "$gcp_json_path")
        set_github_secret "GCP_SERVICE_ACCOUNT_JSON" "$gcp_json_b64" && ((configured_count++)) || ((failed_count++))
        log_success "Service account JSON encoded and stored"
    else
        log_warn "File not found: $gcp_json_path (skipping)"
        ((failed_count++))
    fi

    # Section 4: Microsoft Graph
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 4: Microsoft Graph Configuration (SharePoint Sync)"
    log_info "═══════════════════════════════════════════════════════════════"

    read -p "Enter MICROSOFT_TENANT_ID: " MICROSOFT_TENANT_ID
    set_github_secret "MICROSOFT_TENANT_ID" "$MICROSOFT_TENANT_ID" && ((configured_count++)) || ((failed_count++))

    read -p "Enter MICROSOFT_CLIENT_ID: " MICROSOFT_CLIENT_ID
    set_github_secret "MICROSOFT_CLIENT_ID" "$MICROSOFT_CLIENT_ID" && ((configured_count++)) || ((failed_count++))

    read -sp "Enter MICROSOFT_CLIENT_SECRET: " MICROSOFT_CLIENT_SECRET
    echo ""
    set_github_secret "MICROSOFT_CLIENT_SECRET" "$MICROSOFT_CLIENT_SECRET" && ((configured_count++)) || ((failed_count++))

    read -p "Enter SHAREPOINT_SITE_URL: " SHAREPOINT_SITE_URL
    set_github_secret "SHAREPOINT_SITE_URL" "$SHAREPOINT_SITE_URL" && ((configured_count++)) || ((failed_count++))

    read -p "Enter SHAREPOINT_DRIVE_ID: " SHAREPOINT_DRIVE_ID
    set_github_secret "SHAREPOINT_DRIVE_ID" "$SHAREPOINT_DRIVE_ID" && ((configured_count++)) || ((failed_count++))

    # Section 5: GitHub
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 5: GitHub Configuration"
    log_info "═══════════════════════════════════════════════════════════════"

    read -sp "Enter GITHUB_PAT (Personal Access Token): " GITHUB_PAT
    echo ""
    set_github_secret "GITHUB_PAT" "$GITHUB_PAT" && ((configured_count++)) || ((failed_count++))

    # Section 6: Monitoring
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "SECTION 6: Monitoring & Alerting (Optional)"
    log_info "═══════════════════════════════════════════════════════════════"

    read -p "Enter CLOUDWATCH_LOG_GROUP (default: /maestro/phase2): " CLOUDWATCH_LOG_GROUP
    CLOUDWATCH_LOG_GROUP="${CLOUDWATCH_LOG_GROUP:-/maestro/phase2}"
    set_github_secret "CLOUDWATCH_LOG_GROUP" "$CLOUDWATCH_LOG_GROUP" && ((configured_count++)) || ((failed_count++))

    read -p "Enter SLACK_WEBHOOK_URL (optional, press Enter to skip): " SLACK_WEBHOOK_URL
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        set_github_secret "SLACK_WEBHOOK_URL" "$SLACK_WEBHOOK_URL" && ((configured_count++)) || ((failed_count++))
    fi

    # Summary
    echo ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_success "Configuration Complete!"
    log_info "═══════════════════════════════════════════════════════════════"
    echo "Configured: $configured_count | Failed: $failed_count"
    log_info "Log file: $LOG_FILE"
}

# ============================================================================
# GitHub Secret Management
# ============================================================================

set_github_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [ -z "$secret_value" ]; then
        log_warn "Skipping empty secret: $secret_name"
        return 1
    fi

    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) not found. Install from https://cli.github.com"
        return 1
    fi

    # Use gh to set the secret
    if echo "$secret_value" | gh secret set "$secret_name" 2>&1; then
        log_success "Set secret: $secret_name"
        return 0
    else
        log_error "Failed to set secret: $secret_name"
        return 1
    fi
}

verify_secrets() {
    log_info "Verifying GitHub Actions secrets..."

    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) not found"
        return 1
    fi

    local missing=()
    local found=()

    for secret in "${!PHASE2_SECRETS[@]}"; do
        if gh secret list 2>/dev/null | grep -q "^${secret}[[:space:]]"; then
            found+=("$secret")
            log_success "Found: $secret"
        else
            missing+=("$secret")
            log_warn "Missing: $secret"
        fi
    done

    echo ""
    log_info "Summary: ${#found[@]} found, ${#missing[@]} missing"

    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        log_warn "Missing secrets:"
        for secret in "${missing[@]}"; do
            echo "  - $secret"
        done
        return 1
    fi

    return 0
}

list_secrets() {
    log_info "Required Phase 2 Secrets:"
    echo ""

    for secret in "${!PHASE2_SECRETS[@]}"; do
        printf "  ${BLUE}%-35s${NC} %s\n" "$secret" "${PHASE2_SECRETS[$secret]}"
    done

    echo ""
    log_info "Total: ${#PHASE2_SECRETS[@]} secrets required"
}

generate_template() {
    cat << 'EOF'
# Phase 2 Secrets Template
# Copy this file, fill in values, and run: gh secret set from .env
# WARNING: This file contains sensitive data. Never commit it to version control.

# Anthropic Configuration
ANTHROPIC_API_KEY=<your_api_key_here>
ANTHROPIC_MODEL_MAESTRO=claude-3-5-sonnet-20241022
ANTHROPIC_MODEL_ORCHESTRATOR=claude-3-5-sonnet-20241022

# Supabase Configuration
SUPABASE_PROJECT_ID=<your_project_id>
SUPABASE_PROJECT_URL=https://<project_id>.supabase.co
SUPABASE_ANON_KEY=<your_anon_key>
SUPABASE_SERVICE_ROLE_KEY=<your_service_role_key>

# GCP Configuration
GCP_PROJECT_ID=<your_gcp_project>
GCP_REGION=us-central1
GCP_SERVICE_ACCOUNT_JSON=<base64_encoded_service_account_json>

# Microsoft Graph Configuration
MICROSOFT_TENANT_ID=<your_tenant_id>
MICROSOFT_CLIENT_ID=<your_app_registration_id>
MICROSOFT_CLIENT_SECRET=<your_client_secret>
SHAREPOINT_SITE_URL=https://mantaassociados.sharepoint.com/sites/maestro
SHAREPOINT_DRIVE_ID=<your_drive_id>

# GitHub Configuration
GITHUB_PAT=<your_personal_access_token>
GITHUB_ORGANIZATION=MN1970
GITHUB_REPOSITORY=Codex-exemplo

# Monitoring & Alerting
CLOUDWATCH_LOG_GROUP=/maestro/phase2
SLACK_WEBHOOK_URL=<optional_slack_webhook>

# Phase 2 Specific
FEEDBACK_DB_URL=postgresql://<user>:<password>@<host>/feedback
VECTORSTORE_COLLECTION_NAME=maestro-phase2-vectors
ORCHESTRATOR_AGENT_ID=manta-17-orchestrator
CLASSIFIER_AGENT_ID=manta-classifier

EOF
}

# ============================================================================
# Main
# ============================================================================

main() {
    log_info "Phase 2 GitHub Actions Secrets Configuration"
    log_info "Timestamp: $(date)"
    log_info "Repository: $REPO_ROOT"

    case "${1:-}" in
        --interactive)
            interactive_setup
            ;;
        --verify)
            verify_secrets
            ;;
        --list)
            list_secrets
            ;;
        --template)
            generate_template
            ;;
        --help|"")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
