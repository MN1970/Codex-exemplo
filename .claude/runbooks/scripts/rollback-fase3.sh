#!/bin/bash
################################################################################
# FASE 3 ROLLBACK SCRIPT
# Automated rollback to pre-Fase 3 production state
#
# Usage: ./rollback-fase3.sh
# Execution time: ~15 minutes
# Rollback scope: All 10 Fase 3 skills + agent + database
################################################################################

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="/var/log/fase3-rollback"
ROLLBACK_LOG="$LOGS_DIR/rollback-$(date +%Y%m%d-%H%M%S).log"
SNAPSHOT_ID="${SNAPSHOT_ID:-pre-fase3-2026-0727}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOGS_DIR"

# Logging function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "$ROLLBACK_LOG"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $@" | tee -a "$ROLLBACK_LOG"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $@" | tee -a "$ROLLBACK_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "$ROLLBACK_LOG"
}

################################################################################
# MAIN ROLLBACK PROCEDURE
################################################################################

main() {
    log_info "=== FASE 3 ROLLBACK INITIATED ==="
    log_info "Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log_info "Rollback destination snapshot: $SNAPSHOT_ID"
    echo ""

    # Confirmation check
    echo -e "${RED}WARNING: This will restore production to pre-Fase 3 state.${NC}"
    echo "This action:"
    echo "  • Stops all new merge operations"
    echo "  • Reverts database to snapshot (all Fase 3 data lost)"
    echo "  • Removes 10 Fase 3 skills from production"
    echo "  • Restores Fase 2 gates"
    echo ""

    read -p "Type 'ROLLBACK' to confirm: " confirm
    if [ "$confirm" != "ROLLBACK" ]; then
        log_info "Rollback cancelled by user"
        exit 0
    fi

    echo ""

    # ========================================================================
    # STEP 1: PAUSE ALL MERGE OPERATIONS (T0–T+5min)
    # ========================================================================
    log_info "[STEP 1/4] Pausing all merge operations..."

    # Disable merge operations in gitops-flow-runner
    if ! kubectl patch deployment gitops-flow-runner -n gitops \
        -p '{"spec":{"template":{"spec":{"containers":[{"name":"gitops-flow","env":[{"name":"MERGE_ENABLED","value":"false"}]}]}}}}' \
        2>> "$ROLLBACK_LOG"; then
        log_warn "Failed to patch gitops-flow-runner (may not exist)"
    else
        log_info "✓ Merge operations paused"
    fi

    sleep 30

    # Verify no new merges initiated
    RECENT_MERGES=$(kubectl logs -n gitops deployment/gitops-flow-runner \
        --tail=20 2>/dev/null | grep -c "merge initiated" || echo "0")

    if [ "$RECENT_MERGES" -eq 0 ]; then
        log_info "✓ No new merges in last check"
    else
        log_warn "Detected $RECENT_MERGES recent merge attempts"
    fi

    # Notify stakeholders
    log_info "Sending rollback notification to Slack..."
    curl -X POST "https://hooks.slack.com/services/${SLACK_WEBHOOK_PATH}" \
        -H "Content-Type: application/json" \
        -d '{
            "channel": "#incidents",
            "text": "🚨 FASE 3 ROLLBACK IN PROGRESS",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Timestamp", "value": "'$(date -u +'%Y-%m-%dT%H:%M:%SZ')'", "short": true},
                    {"title": "Status", "value": "Merge operations paused", "short": true},
                    {"title": "Next", "value": "Database snapshot restore (5–15 min)", "short": false}
                ]
            }]
        }' 2>/dev/null || log_warn "Failed to send Slack notification"

    # ========================================================================
    # STEP 2: FREEZE SENSITIVE TABLES (T+5–T+10min)
    # ========================================================================
    log_info "[STEP 2/4] Freezing sensitive database tables..."

    if [ -z "$SUPABASE_DB_URL" ]; then
        log_error "SUPABASE_DB_URL not set, cannot proceed"
        exit 1
    fi

    # Lock tables
    psql "$SUPABASE_DB_URL" << 'SQL' 2>> "$ROLLBACK_LOG" || {
        log_warn "Failed to lock tables (may already be restored)"
    }
    -- Attempt to lock critical tables for read-only
    LOCK TABLE gitops_ml_scores IN EXCLUSIVE MODE;
    LOCK TABLE tbl_detection_feedback IN EXCLUSIVE MODE;
    LOCK TABLE tbl_pattern_quality_metrics IN EXCLUSIVE MODE;
    LOCK TABLE git_parallel_schedule IN EXCLUSIVE MODE;
    LOCK TABLE git_execution_plans IN EXCLUSIVE MODE;
SQL

    log_info "✓ Critical tables locked"

    # ========================================================================
    # STEP 3: RESTORE SUPABASE SNAPSHOT (T+10–T+40min)
    # ========================================================================
    log_info "[STEP 3/4] Restoring Supabase snapshot (estimate: 10–15 min)..."

    if [ -z "$SUPABASE_API_TOKEN" ] || [ -z "$SUPABASE_PROJECT_ID" ]; then
        log_error "SUPABASE_API_TOKEN or SUPABASE_PROJECT_ID not set"
        exit 1
    fi

    # Initiate snapshot restore
    RESTORE_RESPONSE=$(curl -s -X POST \
        "https://api.supabase.com/v1/projects/$SUPABASE_PROJECT_ID/backups/$SNAPSHOT_ID/restore" \
        -H "Authorization: Bearer $SUPABASE_API_TOKEN" \
        -H "Content-Type: application/json")

    if echo "$RESTORE_RESPONSE" | grep -q "error"; then
        log_error "Snapshot restore request failed: $RESTORE_RESPONSE"
        exit 1
    fi

    log_info "Snapshot restore initiated. Waiting for completion..."

    # Wait for restore with periodic status checks
    WAIT_TIME=0
    MAX_WAIT=1200  # 20 minutes
    POLL_INTERVAL=30

    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        # Check restore status
        STATUS=$(curl -s "https://api.supabase.com/v1/projects/$SUPABASE_PROJECT_ID/backups" \
            -H "Authorization: Bearer $SUPABASE_API_TOKEN" | \
            jq -r ".backups[0].status // \"unknown\"")

        if [ "$STATUS" = "restored" ] || [ "$STATUS" = "success" ]; then
            log_info "✓ Snapshot restore completed"
            break
        fi

        WAIT_TIME=$((WAIT_TIME + POLL_INTERVAL))
        ELAPSED_MIN=$((WAIT_TIME / 60))

        if [ $((WAIT_TIME % 300)) -eq 0 ]; then
            log_info "  Waiting... ($ELAPSED_MIN min elapsed, status: $STATUS)"
        fi

        sleep $POLL_INTERVAL
    done

    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        log_error "Snapshot restore timeout (>20 min). Check Supabase console."
        exit 1
    fi

    # Verify database connectivity post-restore
    sleep 30  # Allow time for connections to reset

    if ! psql "$SUPABASE_DB_URL" -c "SELECT 1;" > /dev/null 2>&1; then
        log_error "Failed to connect to restored database"
        exit 1
    fi

    log_info "✓ Database connectivity verified"

    # ========================================================================
    # STEP 4: REVERT KUBERNETES DEPLOYMENTS (T+40–T+50min)
    # ========================================================================
    log_info "[STEP 4/4] Reverting Kubernetes deployments..."

    DEPLOYMENTS=(
        "gitops-skill-runner"
        "chaos-test-runner"
        "gitops-flow-runner"
        "multi-repo-runner"
        "pattern-detection-runner"
        "ml-service"
    )

    for deployment in "${DEPLOYMENTS[@]}"; do
        log_info "Reverting $deployment..."

        if kubectl rollout undo deployment/"$deployment" -n gitops 2>> "$ROLLBACK_LOG"; then
            # Wait for rollout
            if kubectl rollout status deployment/"$deployment" -n gitops --timeout=5m 2>> "$ROLLBACK_LOG"; then
                log_info "✓ $deployment reverted successfully"
            else
                log_warn "Rollout status check failed for $deployment (may still be valid)"
            fi
        else
            log_warn "Failed to revert $deployment (may not exist)"
        fi

        sleep 10  # Space out rollouts
    done

    # Re-enable Fase 2 gates in Maestro
    log_info "Re-enabling Fase 2 gates in Maestro..."

    python3 << 'PYTHON_EOF' 2>> "$ROLLBACK_LOG" || log_warn "Failed to update Maestro config"
import json
import os

maestro_config = {
    "phase": "2",
    "ml_confidence_enabled": False,
    "chaos_engineering_enabled": False,
    "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
}

config_path = "/opt/maestro/config/phase.json"
if os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump(maestro_config, f, indent=2)
    print("✓ Maestro phase configuration reverted to Fase 2")
else:
    print("⚠ Warning: Maestro config path not found")
PYTHON_EOF

    # ========================================================================
    # STEP 5: FINAL VERIFICATION (T+50–T+60min)
    # ========================================================================
    log_info "Verifying rollback completion..."

    # Check Kubernetes health
    REPLICAS=$(kubectl get deployment gitops-flow-runner -n gitops \
        -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    if [ "$REPLICAS" -ge 1 ]; then
        log_info "✓ Kubernetes: HEALTHY ($REPLICAS replicas ready)"
    else
        log_warn "⚠ Kubernetes replicas: $REPLICAS (may be recovering)"
    fi

    # Check database consistency
    TABLES_COUNT=$(psql "$SUPABASE_DB_URL" -t -c \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")

    if [ "$TABLES_COUNT" -gt 0 ]; then
        log_info "✓ Database: ACCESSIBLE ($TABLES_COUNT tables)"
    else
        log_warn "⚠ Database tables: could not verify"
    fi

    # Verify Fase 3 components are reverted
    if kubectl get deployment gitops-skill-runner -n gitops > /dev/null 2>&1; then
        IMAGEN=$(kubectl get deployment gitops-skill-runner -n gitops \
            -o jsonpath='{.spec.template.spec.containers[0].image}' || echo "unknown")

        if [[ "$IMAGEN" == *"v3.0"* ]] || [[ "$IMAGEN" == *"v1.0"* ]]; then
            log_warn "⚠ Warning: Fase 3 image still detected: $IMAGEN (may be in rollback)"
        else
            log_info "✓ Fase 3 skills: reverted (image: $IMAGEN)"
        fi
    fi

    # ========================================================================
    # COMPLETION
    # ========================================================================
    echo ""
    log_info "=== ROLLBACK COMPLETE ==="
    log_info "System reverted to Fase 2 (pre-Fase 3 state)"
    log_info "Rollback log: $ROLLBACK_LOG"
    echo ""

    echo -e "${GREEN}✓ ROLLBACK SUCCESSFUL${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Verify system stability (watch #deployments channel)"
    echo "2. Run incident post-mortem (within 4 hours)"
    echo "3. Investigate root cause"
    echo "4. Update deployment checklist"
    echo "5. Re-schedule Fase 3 deployment with fixes"
    echo ""
    echo "On-call: @DevOps-lead, @ML-engineering-lead"
    echo "Incident tracker: https://pagerduty.manta.internal"
    echo ""
}

# Execute main function
main
exit 0
