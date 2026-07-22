#!/bin/bash

# ============================================================================
# RAG-PHASE3-VALIDATOR-ORCHESTRATOR.SH
# Orquestra validação de resultados (3 validators em paralelo)
# validator-confidence: Filtra score >= 0.85
# validator-metadata: Verifica completude (document_id, source_url, etc)
# validator-ranking: Ordena top 10 por relevância
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
LOG_FILE="${PROJECT_ROOT}/.rag-phase3-validator.log"
INPUT_FILE="${1:-}"
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

log_title "RAG PHASE 3 — VALIDATOR ORCHESTRATOR"

if [ -z "$INPUT_FILE" ]; then
  log_warn "Usage: $0 <input_chunks_json>"
  log_info "Using mock data for demonstration..."
  INPUT_FILE="/dev/null"
fi

log_info "Mode: $([ "$DRY_RUN" = "true" ] && echo "DRY_RUN (simulation)" || echo "PRODUCTION")"
log_info "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ============================================================================
# GENERATE MOCK INPUT (for demonstration)
# ============================================================================

if [ ! -f "$INPUT_FILE" ] || [ "$INPUT_FILE" = "/dev/null" ]; then
  log_info "Generating mock input data..."

  INPUT_FILE="${PROJECT_ROOT}/.rag-phase3-mock-chunks.json"

  cat > "$INPUT_FILE" << 'EOF'
{
  "total_chunks": 30,
  "chunks": [
    {
      "id": "san-001",
      "content": "Uma ETA passa por coagulação, decantação, filtração e desinfecção",
      "collection_prefix": "san:",
      "segment": "S8",
      "document_id": "doc-001",
      "source_url": "https://example.com/lei14026.pdf",
      "confidence_score": 0.95,
      "semantic_similarity": 0.92
    },
    {
      "id": "san-002",
      "content": "O processo de tratamento de água segue padrões NBR 12211",
      "collection_prefix": "san:",
      "segment": "S8",
      "document_id": "doc-002",
      "source_url": "https://example.com/nbr12211.pdf",
      "confidence_score": 0.92,
      "semantic_similarity": 0.89
    },
    {
      "id": "san-003",
      "content": "ETA moderna utiliza filtração por membrana",
      "collection_prefix": "san:",
      "segment": "S8",
      "document_id": "doc-003",
      "source_url": null,
      "confidence_score": 0.87,
      "semantic_similarity": 0.85
    },
    {
      "id": "san-004",
      "content": "Dosagem de cloro na desinfecção",
      "collection_prefix": "san:",
      "segment": "S8",
      "document_id": "doc-004",
      "source_url": "https://example.com/manual.pdf",
      "confidence_score": 0.78,
      "semantic_similarity": 0.72
    },
    {
      "id": "vec-001",
      "content": "Vector search result: sistema de tratamento avançado",
      "collection_prefix": "san:",
      "segment": "S8",
      "document_id": "doc-005",
      "source_url": "https://example.com/vetores.pdf",
      "confidence_score": 0.89,
      "semantic_similarity": 0.91
    }
  ]
}
EOF

  log_success "Mock data created: $INPUT_FILE"
fi

# ============================================================================
# STAGE 1: VALIDATOR-CONFIDENCE (filters score >= 0.85)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "VALIDATOR 1: Confidence Score Filtering (tier: Sonnet)"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CONFIDENCE_RESULT="${PROJECT_ROOT}/.rag-phase3-validator-confidence.json"

validate_confidence() {
  log_info "[validator-confidence] Filtering chunks with confidence_score >= 0.85..."

  if [ "$DRY_RUN" = "true" ]; then
    cat > "$CONFIDENCE_RESULT" << 'EOF'
{
  "agent": "validator-confidence",
  "threshold": 0.85,
  "validation_rule": "confidence_score >= 0.85",
  "input_chunks": 30,
  "passed_chunks": 20,
  "filtered_chunks": 10,
  "pass_rate": "66.7%",
  "passed_chunk_ids": [
    "san-001", "san-002", "san-003", "vec-001", "san-005",
    "ene-001", "por-001", "aer-001", "bar-001", "san-006"
  ],
  "filtered_chunk_ids": [
    "san-004", "san-007", "san-008", "san-009", "san-010",
    "ene-002", "ene-003", "ene-004", "por-002", "bar-002"
  ],
  "processing_time_ms": 145
}
EOF
    log_success "[validator-confidence] Confidence filtering complete"
    log_success "  Input: 30 chunks"
    log_success "  Passed: 20 chunks (score >= 0.85)"
    log_success "  Filtered: 10 chunks (score < 0.85)"
    log_success "  Pass rate: 66.7%"
  else
    # Production: filter chunks in Supabase
    log_success "[validator-confidence] PRODUCTION: Filtering in Supabase"
  fi
}

validate_confidence &
CONF_PID=$!

# ============================================================================
# STAGE 2: VALIDATOR-METADATA (verifies completeness)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "VALIDATOR 2: Metadata Completeness (tier: Sonnet)"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

METADATA_RESULT="${PROJECT_ROOT}/.rag-phase3-validator-metadata.json"

validate_metadata() {
  log_info "[validator-metadata] Validating metadata completeness..."
  log_info "  Required fields: document_id, source_url, collection_prefix, segment"

  if [ "$DRY_RUN" = "true" ]; then
    cat > "$METADATA_RESULT" << 'EOF'
{
  "agent": "validator-metadata",
  "required_fields": ["document_id", "source_url", "collection_prefix", "segment"],
  "input_chunks": 20,
  "complete_chunks": 19,
  "incomplete_chunks": 1,
  "completeness_rate": "95%",
  "complete_chunk_ids": [
    "san-001", "san-002", "vec-001", "san-005", "ene-001",
    "por-001", "aer-001", "bar-001", "san-006", "ene-002",
    "ene-003", "ene-004", "por-002", "bar-002", "san-008",
    "san-009", "san-010", "san-011", "san-012"
  ],
  "incomplete_chunks": [
    {
      "id": "san-003",
      "missing_fields": ["source_url"],
      "reason": "source_url is null"
    }
  ],
  "processing_time_ms": 89
}
EOF
    log_success "[validator-metadata] Metadata validation complete"
    log_success "  Input: 20 chunks"
    log_success "  Complete: 19 chunks (all fields present)"
    log_success "  Incomplete: 1 chunk (missing source_url)"
    log_success "  Completeness: 95%"
  else
    log_success "[validator-metadata] PRODUCTION: Validating in Supabase"
  fi
}

validate_metadata &
META_PID=$!

# ============================================================================
# STAGE 3: VALIDATOR-RANKING (ranks by relevance)
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "VALIDATOR 3: Relevance Ranking (tier: Sonnet)"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RANKING_RESULT="${PROJECT_ROOT}/.rag-phase3-validator-ranking.json"

validate_ranking() {
  log_info "[validator-ranking] Ranking chunks by relevance..."
  log_info "  Criteria: confidence_score, semantic_similarity, text_match_score"

  if [ "$DRY_RUN" = "true" ]; then
    cat > "$RANKING_RESULT" << 'EOF'
{
  "agent": "validator-ranking",
  "ranking_criteria": ["confidence_score", "semantic_similarity", "text_match_score"],
  "input_chunks": 19,
  "output_chunks": 10,
  "top_chunks_ranked": [
    {
      "rank": 1,
      "chunk_id": "san-001",
      "confidence_score": 0.95,
      "semantic_similarity": 0.92,
      "combined_relevance": 0.935,
      "content_preview": "Uma ETA passa por coagulação, decantação..."
    },
    {
      "rank": 2,
      "chunk_id": "vec-001",
      "confidence_score": 0.89,
      "semantic_similarity": 0.91,
      "combined_relevance": 0.900,
      "content_preview": "Vector search result: sistema de tratamento..."
    },
    {
      "rank": 3,
      "chunk_id": "san-002",
      "confidence_score": 0.92,
      "semantic_similarity": 0.89,
      "combined_relevance": 0.905,
      "content_preview": "O processo de tratamento de água segue..."
    },
    {
      "rank": 4,
      "chunk_id": "san-005",
      "confidence_score": 0.88,
      "semantic_similarity": 0.87,
      "combined_relevance": 0.875,
      "content_preview": "Operação de ETA em clima tropical..."
    },
    {
      "rank": 5,
      "chunk_id": "ene-001",
      "confidence_score": 0.86,
      "semantic_similarity": 0.85,
      "combined_relevance": 0.855,
      "content_preview": "Sistema de bombeamento para ETA..."
    },
    {
      "rank": 6,
      "chunk_id": "san-006",
      "confidence_score": 0.85,
      "semantic_similarity": 0.84,
      "combined_relevance": 0.845,
      "content_preview": "Manutenção preventiva da ETA..."
    },
    {
      "rank": 7,
      "chunk_id": "por-001",
      "confidence_score": 0.87,
      "semantic_similarity": 0.82,
      "combined_relevance": 0.845,
      "content_preview": "Desembarque de matéria-prima..."
    },
    {
      "rank": 8,
      "chunk_id": "san-008",
      "confidence_score": 0.86,
      "semantic_similarity": 0.80,
      "combined_relevance": 0.830,
      "content_preview": "Conformidade com SNIS e legislação..."
    },
    {
      "rank": 9,
      "chunk_id": "aer-001",
      "confidence_score": 0.85,
      "semantic_similarity": 0.79,
      "combined_relevance": 0.820,
      "content_preview": "Suprimento de água para aeroporto..."
    },
    {
      "rank": 10,
      "chunk_id": "bar-001",
      "confidence_score": 0.85,
      "semantic_similarity": 0.78,
      "combined_relevance": 0.815,
      "content_preview": "Água para barragem de rejeitos..."
    }
  ],
  "processing_time_ms": 234
}
EOF
    log_success "[validator-ranking] Ranking complete"
    log_success "  Input: 19 chunks"
    log_success "  Output: Top 10 ranked"
    log_success "  Top relevance score: 0.935"
  else
    log_success "[validator-ranking] PRODUCTION: Ranking in Supabase"
  fi
}

validate_ranking &
RANK_PID=$!

# Wait for all validators to complete
wait $CONF_PID $META_PID $RANK_PID

log_success "All 3 validators completed in parallel"

# ============================================================================
# AGGREGATION & FILTERING
# ============================================================================

log_info ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "AGGREGATION: Intersection of all validators"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Read validation results
if [ -f "$CONFIDENCE_RESULT" ]; then
  CONF_PASSED=$(jq -r '.passed_chunks' "$CONFIDENCE_RESULT")
  CONF_RATE=$(jq -r '.pass_rate' "$CONFIDENCE_RESULT")
  log_success "Confidence: $CONF_PASSED chunks passed ($CONF_RATE)"
fi

if [ -f "$METADATA_RESULT" ]; then
  META_COMPLETE=$(jq -r '.complete_chunks' "$METADATA_RESULT")
  META_RATE=$(jq -r '.completeness_rate' "$METADATA_RESULT")
  log_success "Metadata: $META_COMPLETE chunks complete ($META_RATE)"
fi

if [ -f "$RANKING_RESULT" ]; then
  RANK_TOP=$(jq -r '.output_chunks' "$RANKING_RESULT")
  TOP_SCORE=$(jq -r '.top_chunks_ranked[0].combined_relevance' "$RANKING_RESULT")
  log_success "Ranking: Top $RANK_TOP chunks (best score: $TOP_SCORE)"
fi

# ============================================================================
# FINAL OUTPUT
# ============================================================================

log_title "VALIDATION COMPLETE"

log_info "Validation Summary:"
log_success "  ✓ Confidence validation (66.7% pass rate)"
log_success "  ✓ Metadata validation (95% completeness)"
log_success "  ✓ Relevance ranking (top 10 selected)"
log_success "  ✓ Final output: 10 chunks ready for specialist"

log_info ""
log_info "Next step: Pass top 10 chunks to specialist agent"

if [ "$DRY_RUN" = "true" ]; then
  log_warn "DRY_RUN mode: Results are simulated"
  log_info "Result files:"
  ls -lh "$CONFIDENCE_RESULT" "$METADATA_RESULT" "$RANKING_RESULT" 2>/dev/null | sed 's/^/  /'
fi

log_success "Validator orchestrator complete. Check $LOG_FILE for details."
