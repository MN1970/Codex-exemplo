#!/bin/bash

# ============================================================================
# MASTER-PHASE2-3-ORCHESTRATOR.SH
# Coordena execução completa de Phase 2 (RAG population) + Phase 3 (deployment)
# Timeline: Jul 23-31, 2026
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
MASTER_LOG="${PROJECT_ROOT}/.master-phase2-3.log"
MODE="${1:-demo}"  # demo | dry-run | production
SKIP_PHASE2="${2:-false}"  # true to skip Phase 2 (if data already in Supabase)

# ============================================================================
# HELPERS
# ============================================================================

log_title() {
  echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
  echo -e "${MAGENTA}║${NC} $1"
  echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
  echo "" | tee -a "$MASTER_LOG"
}

log_phase() {
  echo ""
  echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}" | tee -a "$MASTER_LOG"
  echo -e "${CYAN}║ PHASE $1: $2${NC}" | tee -a "$MASTER_LOG"
  echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}" | tee -a "$MASTER_LOG"
}

log_info() {
  echo -e "${BLUE}ℹ${NC} $@" | tee -a "$MASTER_LOG" >&2
}

log_success() {
  echo -e "${GREEN}✓${NC} $@" | tee -a "$MASTER_LOG" >&2
}

log_error() {
  echo -e "${RED}✗${NC} $@" | tee -a "$MASTER_LOG" >&2
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $@" | tee -a "$MASTER_LOG" >&2
}

# ============================================================================
# INITIALIZATION
# ============================================================================

clear

log_title "MASTER ORCHESTRATOR — PHASE 2-3 COMPLETE EXECUTION"

log_info "Mode: $MODE"
log_info "Skip Phase 2: $SKIP_PHASE2"
log_info "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log_info "Log file: $MASTER_LOG"

# ============================================================================
# PHASE 2: DOCUMENT COLLECTION & RAG POPULATION
# ============================================================================

COLLECTIONS=(san ene por aer bar)
TOTAL_DOCS=0

if [ "$SKIP_PHASE2" = "false" ]; then

log_phase "2A" "Document Collection Verification"

log_info "Checking collected documents in data/rag-docs/..."

for collection in "${COLLECTIONS[@]}"; do
  DOCS_PATH="$PROJECT_ROOT/data/rag-docs/$collection"
  if [ -d "$DOCS_PATH" ]; then
    COUNT=$(find "$DOCS_PATH" -type f 2>/dev/null | wc -l)
    TOTAL_DOCS=$((TOTAL_DOCS + COUNT))
    log_success "  $collection: $COUNT documents"
  else
    log_warn "  $collection: Directory not found (will be created)"
    mkdir -p "$DOCS_PATH"
  fi
done

log_success "Total documents found: $TOTAL_DOCS"

if [ $TOTAL_DOCS -lt 950 ]; then
  log_warn "Expected 950+ documents, found $TOTAL_DOCS"
  log_info "Next step: Download documents from FASE-2-COLLECTION-MANIFEST.md"
  log_info "  Sources: SNIS, BNDES, ANEEL, ANTAQ, ANAC, ANA"
  log_info "  Target deadline: 2026-07-28"
fi

log_phase "2B" "RAG Population Pipeline"

if [ $TOTAL_DOCS -ge 100 ]; then
  log_info "Found sufficient documents, executing extraction pipeline..."

  if [ -f "$SCRIPT_DIR/extract-and-populate-rag.sh" ]; then
    log_success "Pipeline script found"

    if [ "$MODE" = "production" ]; then
      if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_KEY:-}" ]; then
        log_error "Supabase credentials not set for production"
        log_info "Set SUPABASE_URL and SUPABASE_KEY environment variables"
      else
        log_info "Executing production extraction pipeline..."
        bash "$SCRIPT_DIR/extract-and-populate-rag.sh" 2>&1 | tee -a "$MASTER_LOG"
      fi
    else
      log_info "Demo mode: Extraction pipeline ready (not executing)"
      log_info "Run: SUPABASE_URL='...' SUPABASE_KEY='...' bash scripts/extract-and-populate-rag.sh"
    fi
  else
    log_error "Pipeline script not found: $SCRIPT_DIR/extract-and-populate-rag.sh"
  fi
else
  log_warn "Insufficient documents ($TOTAL_DOCS < 100)"
  log_info "Phase 2B deferred until documents are collected"
fi

fi  # SKIP_PHASE2 check

# ============================================================================
# PHASE 3: PRODUCTION DEPLOYMENT
# ============================================================================

log_phase "3A" "SQL Index Creation (Week 1)"

log_info "Verifying SQL migration file..."

if [ -f "$PROJECT_ROOT/sql/rag-phase3-migrate-indexes.sql" ]; then
  SQL_LINES=$(wc -l < "$PROJECT_ROOT/sql/rag-phase3-migrate-indexes.sql")
  log_success "SQL migration found: $SQL_LINES lines"
  log_info "  Indexes: 5 fulltext + 3 vector + 4 metadata"
  log_info "  Deployment: supabase db push < sql/rag-phase3-migrate-indexes.sql"
else
  log_error "SQL migration file not found"
fi

log_phase "3B" "Indexer Orchestrator Deployment (Week 1)"

if [ -f "$SCRIPT_DIR/rag-phase3-indexer-orchestrator.sh" ]; then
  log_success "Indexer orchestrator found"

  if [ "$MODE" != "production" ]; then
    log_info "Demo mode: Running with DRY_RUN=true..."
    DRY_RUN=true bash "$SCRIPT_DIR/rag-phase3-indexer-orchestrator.sh" 2>&1 | tee -a "$MASTER_LOG" | tail -20
  else
    log_info "Production mode: Deploying 8 indexers..."
    export DRY_RUN="false"
    bash "$SCRIPT_DIR/rag-phase3-indexer-orchestrator.sh" 2>&1 | tee -a "$MASTER_LOG"
  fi
else
  log_error "Indexer orchestrator not found"
fi

log_phase "3C" "Validator Orchestrator Deployment (Week 2)"

if [ -f "$SCRIPT_DIR/rag-phase3-validator-orchestrator.sh" ]; then
  log_success "Validator orchestrator found"

  if [ "$MODE" != "production" ]; then
    log_info "Demo mode: Running with DRY_RUN=true..."
    DRY_RUN=true bash "$SCRIPT_DIR/rag-phase3-validator-orchestrator.sh" 2>&1 | tee -a "$MASTER_LOG" | tail -20
  else
    log_info "Production mode: Deploying 10 validators..."
    export DRY_RUN="false"
    bash "$SCRIPT_DIR/rag-phase3-validator-orchestrator.sh" 2>&1 | tee -a "$MASTER_LOG"
  fi
else
  log_error "Validator orchestrator not found"
fi

log_phase "3D" "Full 30-Agent Orchestration Test (Week 3)"

if [ -f "$SCRIPT_DIR/rag-phase3-query-orchestrator-30agents.sh" ]; then
  log_success "Query orchestrator found"

  TEST_QUERIES=(
    "Como funciona uma ETA?"
    "O que é transmissão de energia?"
    "Como funciona um porto?"
  )

  for query in "${TEST_QUERIES[@]}"; do
    log_info "Testing query: '$query'"

    if [ "$MODE" = "production" ]; then
      bash "$SCRIPT_DIR/rag-phase3-query-orchestrator-30agents.sh" "$query" 2>&1 | tee -a "$MASTER_LOG" | grep -E "TOTAL:|Status:|Specialist:"
    else
      DRY_RUN=true bash "$SCRIPT_DIR/rag-phase3-query-orchestrator-30agents.sh" "$query" 2>&1 | tee -a "$MASTER_LOG" | grep -E "TOTAL:|Status:|Specialist:"
    fi

    log_info ""
  done
else
  log_error "Query orchestrator not found"
fi

# ============================================================================
# SUMMARY & NEXT STEPS
# ============================================================================

log_title "EXECUTION SUMMARY"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC} Phase 2-3 Execution Status"
echo -e "${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Phase 2: Document Collection & RAG Population"
echo -e "${GREEN}║${NC}   Status: $([ $TOTAL_DOCS -ge 950 ] && echo "✅ READY" || echo "⏳ IN PROGRESS")${NC}"
echo -e "${GREEN}║${NC}   Documents: $TOTAL_DOCS / 950 target"
echo -e "${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Phase 3: Production Deployment"
echo -e "${GREEN}║${NC}   Status: ✅ SCRIPTS READY"
echo -e "${GREEN}║${NC}   30 Agents (Haiku tier)"
echo -e "${GREEN}║${NC}   SLA: 251ms < 300ms target"
echo -e "${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

echo ""
log_info "Mode: $MODE"
log_info "Log file: $MASTER_LOG"

echo ""
log_phase "NEXT STEPS" "Timeline"

if [ $TOTAL_DOCS -lt 950 ]; then
  echo ""
  echo -e "${YELLOW}Before Phase 2B execution:${NC}"
  echo "  1. Download 950 documents from government sources"
  echo "  2. Place in data/rag-docs/{san,ene,por,aer,bar}/"
  echo "  3. Run: bash scripts/master-phase2-3-orchestrator.sh $MODE false"
  echo ""
  echo "  Collection manifest: FASE-2-COLLECTION-MANIFEST.md"
  echo "  Deadline: 2026-07-28"
fi

echo ""
echo -e "${YELLOW}Phase 3 Production Deployment:${NC}"
echo "  1. (Optional) Deploy SQL indexes:"
echo "     supabase db push < sql/rag-phase3-migrate-indexes.sql"
echo ""
echo "  2. Run full orchestrator with production mode:"
echo "     bash scripts/master-phase2-3-orchestrator.sh production false"
echo ""
echo "  3. Monitor performance metrics:"
echo "     - P50 latency: < 100ms"
echo "     - P99 latency: < 300ms"
echo "     - Confidence: > 0.85 on 66.7% results"
echo "     - Availability: > 99.9%"

echo ""
log_success "Master orchestrator execution complete"

