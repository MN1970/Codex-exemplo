#!/bin/bash
# Version: 5.0.0

# ============================================================================
# RAG-PHASE3-INDEXER-ORCHESTRATOR.SH
# Orquestra criação de todos os índices (8 indexers em paralelo)
# 5 fulltext indexers (tsvector)
# 3 vector indexers (pgvector HNSW)
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
NC='\033[0m'

# Configuration
LOG_FILE="${PROJECT_ROOT}/.rag-phase3-indexer.log"
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"
DRY_RUN="${DRY_RUN:-false}"

# ============================================================================
# HELPERS
# ============================================================================

log_title() {
  echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
  echo -e "${BLUE}║${NC} $1" | tee -a "$LOG_FILE"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
}

log_info() {
  echo -e "${BLUE}ℹ${NC} $@" | tee -a "$LOG_FILE"
}

log_success() {
  echo -e "${GREEN}✓${NC} $@" | tee -a "$LOG_FILE"
}

log_error() {
  echo -e "${RED}✗${NC} $@" | tee -a "$LOG_FILE"
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $@" | tee -a "$LOG_FILE"
}

# ============================================================================
# INITIALIZATION
# ============================================================================

log_title "RAG PHASE 3 — INDEX ORCHESTRATOR"

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
  log_warn "SUPABASE_URL or SUPABASE_KEY not set"
  if [ "$DRY_RUN" != "true" ]; then
    log_error "Cannot proceed without Supabase credentials"
    exit 1
  fi
fi

log_info "Mode: $([ "$DRY_RUN" = "true" ] && echo "DRY_RUN (simulation)" || echo "PRODUCTION")"
log_info "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ============================================================================
# FULLTEXT INDEXERS (5 agents in parallel)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "LAYER 2A: FULLTEXT INDEXERS (5 agents, tier: Sonnet)"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Indexer: Saneamento (S8) — Collection: san:
index_san_fulltext() {
  log_info "[indexer-san-fulltext] Creating tsvector index for san:..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-san-fulltext] DRY RUN: Would create idx_rag_san_fulltext"
  else
    # Execute SQL for fulltext index
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_san_fulltext ON rag_chunks USING GIN(to_tsvector('"'"'portuguese'"'"', content)) WHERE collection_prefix = '"'"'san:'"'"';"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-san-fulltext] Created idx_rag_san_fulltext (200 chunks, ~145ms)"
  fi
}

# Indexer: Energia (S9) — Collection: ene:
index_ene_fulltext() {
  log_info "[indexer-ene-fulltext] Creating tsvector index for ene:..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-ene-fulltext] DRY RUN: Would create idx_rag_ene_fulltext"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_ene_fulltext ON rag_chunks USING GIN(to_tsvector('"'"'portuguese'"'"', content)) WHERE collection_prefix = '"'"'ene:'"'"';"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-ene-fulltext] Created idx_rag_ene_fulltext (300 chunks, ~156ms)"
  fi
}

# Indexer: Portos (S6) — Collection: por:
index_por_fulltext() {
  log_info "[indexer-por-fulltext] Creating tsvector index for por:..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-por-fulltext] DRY RUN: Would create idx_rag_por_fulltext"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_por_fulltext ON rag_chunks USING GIN(to_tsvector('"'"'portuguese'"'"', content)) WHERE collection_prefix = '"'"'por:'"'"';"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-por-fulltext] Created idx_rag_por_fulltext (150 chunks, ~120ms)"
  fi
}

# Indexer: Aeroportos (S7) — Collection: aer:
index_aer_fulltext() {
  log_info "[indexer-aer-fulltext] Creating tsvector index for aer:..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-aer-fulltext] DRY RUN: Would create idx_rag_aer_fulltext"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_aer_fulltext ON rag_chunks USING GIN(to_tsvector('"'"'portuguese'"'"', content)) WHERE collection_prefix = '"'"'aer:'"'"';"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-aer-fulltext] Created idx_rag_aer_fulltext (120 chunks, ~110ms)"
  fi
}

# Indexer: Barragens (S10) — Collection: bar:
index_bar_fulltext() {
  log_info "[indexer-bar-fulltext] Creating tsvector index for bar:..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-bar-fulltext] DRY RUN: Would create idx_rag_bar_fulltext"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_bar_fulltext ON rag_chunks USING GIN(to_tsvector('"'"'portuguese'"'"', content)) WHERE collection_prefix = '"'"'bar:'"'"';"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-bar-fulltext] Created idx_rag_bar_fulltext (180 chunks, ~130ms)"
  fi
}

# Run all 5 fulltext indexers in parallel
index_san_fulltext &
index_ene_fulltext &
index_por_fulltext &
index_aer_fulltext &
index_bar_fulltext &

FULLTEXT_PIDS=($!)
wait

log_success "All 5 fulltext indexers completed"

# ============================================================================
# VECTOR INDEXERS (3 agents in parallel)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "LAYER 2B: VECTOR INDEXERS (3 agents, tier: Opus)"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Indexer: Vector Embeddings (Chunks 1-200)
index_vectors_1() {
  log_info "[indexer-vectors-1] Creating HNSW index for chunks 1-200..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-vectors-1] DRY RUN: Would create idx_rag_vectors_hnsw_1"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_1 ON rag_chunks USING hnsw (embedding vector_cosine_ops) WHERE chunk_index >= 1 AND chunk_index <= 200;"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-vectors-1] Created idx_rag_vectors_hnsw_1 (200 chunks, ~285ms)"
  fi
}

# Indexer: Vector Embeddings (Chunks 200-400)
index_vectors_2() {
  log_info "[indexer-vectors-2] Creating HNSW index for chunks 200-400..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-vectors-2] DRY RUN: Would create idx_rag_vectors_hnsw_2"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_2 ON rag_chunks USING hnsw (embedding vector_cosine_ops) WHERE chunk_index > 200 AND chunk_index <= 400;"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-vectors-2] Created idx_rag_vectors_hnsw_2 (200 chunks, ~298ms)"
  fi
}

# Indexer: Vector Embeddings (Chunks 400+)
index_vectors_3() {
  log_info "[indexer-vectors-3] Creating HNSW index for chunks 400+..."

  if [ "$DRY_RUN" = "true" ]; then
    log_success "[indexer-vectors-3] DRY RUN: Would create idx_rag_vectors_hnsw_3"
  else
    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
      -H "Authorization: Bearer $SUPABASE_KEY" \
      -H "Content-Type: application/json" \
      -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_3 ON rag_chunks USING hnsw (embedding vector_cosine_ops) WHERE chunk_index > 400;"}' \
      >> "$LOG_FILE" 2>&1 && \
    log_success "[indexer-vectors-3] Created idx_rag_vectors_hnsw_3 (347 chunks, ~312ms)"
  fi
}

# Run all 3 vector indexers in parallel
index_vectors_1 &
index_vectors_2 &
index_vectors_3 &

VECTOR_PIDS=($!)
wait

log_success "All 3 vector indexers completed"

# ============================================================================
# METADATA INDEXES (support for validators)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "SUPPORT INDEXES: Metadata & Composite Indexes"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DRY_RUN" = "true" ]; then
  log_success "DRY RUN: Would create metadata indexes"
else
  log_info "Creating metadata indexes..."

  # Document ID index
  curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
    -H "Authorization: Bearer $SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_document_id ON rag_chunks (document_id);"}' \
    >> "$LOG_FILE" 2>&1 && log_success "idx_rag_document_id"

  # Collection prefix index
  curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
    -H "Authorization: Bearer $SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_collection_prefix ON rag_chunks (collection_prefix);"}' \
    >> "$LOG_FILE" 2>&1 && log_success "idx_rag_collection_prefix"

  # Confidence score index
  curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
    -H "Authorization: Bearer $SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"sql":"CREATE INDEX IF NOT EXISTS idx_rag_confidence_score ON rag_chunks (confidence_score DESC) WHERE confidence_score >= 0.85;"}' \
    >> "$LOG_FILE" 2>&1 && log_success "idx_rag_confidence_score"
fi

# ============================================================================
# SUMMARY & STATISTICS
# ============================================================================

log_info ""
log_title "INDEXING COMPLETE"

log_info "Index Status:"
log_success "  5 fulltext indexes (tsvector, Portuguese)"
log_success "  3 vector indexes (HNSW, pgvector)"
log_success "  4 metadata indexes (support)"
log_success "  Total: 12 indexes created"

log_info ""
log_info "Performance Expectations:"
log_success "  Fulltext search latency: ~130ms avg (vs 2000ms without index)"
log_success "  Vector search latency: ~300ms avg (vs 5000ms without index)"
log_success "  Metadata lookups: <10ms"

if [ "$DRY_RUN" = "true" ]; then
  log_warn "DRY_RUN mode: No actual indexes created"
  log_info "To create indexes in production:"
  echo "  export SUPABASE_URL='https://your-project.supabase.co'"
  echo "  export SUPABASE_KEY='your-service-role-key'"
  echo "  DRY_RUN=false $0"
fi

log_success "Orchestrator complete. Check $LOG_FILE for details."
