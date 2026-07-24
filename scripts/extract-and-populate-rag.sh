#!/bin/bash
# Version: 5.0.0

# ============================================================================
# EXTRACT-AND-POPULATE-RAG.SH
# Pipeline Completo: Extração → Limpeza → Chunkarização → Validação → Supabase
# Versão: 5.0.0
# Data: 2026-07-22
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Supabase
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"

# Diretórios
DOCS_DIR="${DOCS_DIR:-${PROJECT_ROOT}/data/rag-docs}"
STAGING_DIR="${STAGING_DIR:-${PROJECT_ROOT}/.rag-staging}"
LOG_DIR="${PROJECT_ROOT}/logs/rag-population"

# Configuração
CHUNK_SIZE=1000
CONFIDENCE_THRESHOLD=0.85
DRY_RUN="${DRY_RUN:-false}"

# Coleções e segmentos
declare -A COLLECTION_SEGMENTS=(
  [san:]=S8
  [ene:]=S9
  [por:]=S6
  [aer:]=S7
  [bar:]=S10
)

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

init_logging() {
  mkdir -p "$LOG_DIR"
  LOG_FILE="${LOG_DIR}/rag-population-$(date +%Y-%m-%d-%H%M%S).log"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] RAG Population Started" | tee "$LOG_FILE"
}

log_info() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${BLUE}ℹ${NC} $@" | tee -a "$LOG_FILE" >&2
}

log_success() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${GREEN}✓${NC} $@" | tee -a "$LOG_FILE" >&2
}

log_warn() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${YELLOW}⚠${NC} $@" | tee -a "$LOG_FILE" >&2
}

log_error() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}✗${NC} $@" | tee -a "$LOG_FILE" >&2
}

# Validar pré-requisitos
check_prerequisites() {
  log_info "Validando pré-requisitos..."

  # Verificar Python
  if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado. Instale com: apt-get install -y python3"
    exit 1
  fi

  # Verificar módulos Python
  for module in PyPDF2 docx openpyxl; do
    if ! python3 -c "import ${module}" 2>/dev/null; then
      log_warn "Módulo Python não encontrado: $module"
      log_info "Instale com: pip install ${module}"
    fi
  done

  # Verificar curl e jq
  for cmd in curl jq; do
    if ! command -v "$cmd" &> /dev/null; then
      log_error "Comando não encontrado: $cmd"
      exit 1
    fi
  done

  # Verificar Supabase
  if [[ -z "$SUPABASE_URL" ]] || [[ -z "$SUPABASE_KEY" ]]; then
    log_error "SUPABASE_URL ou SUPABASE_KEY não definidos"
    exit 1
  fi

  # Verificar rag-extraction-utils.py
  if [[ ! -f "${SCRIPT_DIR}/rag-extraction-utils.py" ]]; then
    log_error "Arquivo não encontrado: ${SCRIPT_DIR}/rag-extraction-utils.py"
    exit 1
  fi

  log_success "Pré-requisitos validados"
}

# Descobrir documentos por coleção
discover_documents() {
  local collection=$1
  local collection_dir="${DOCS_DIR}/${collection}"

  if [[ ! -d "$collection_dir" ]]; then
    log_warn "Diretório não encontrado: $collection_dir"
    return 0
  fi

  # Encontrar todos os arquivos suportados
  find "$collection_dir" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" -o -name "*.txt" \) | sort
}

# Processar um documento
process_single_document() {
  local filepath=$1
  local collection=$2
  local segment=$3

  local filename=$(basename "$filepath")
  local staging_file="${STAGING_DIR}/${collection}-${filename}.json"

  log_info "Processando: $filename (Coleção: $collection, Segmento: $segment)"

  # Criar diretório staging
  mkdir -p "$STAGING_DIR"

  # Executar extração com Python
  if python3 "${SCRIPT_DIR}/rag-extraction-utils.py" "$filepath" "$collection" "$segment" > "$staging_file" 2>&1; then
    log_success "Extraído: $filename"
    echo "$staging_file"
  else
    log_error "Falha ao extrair: $filename"
    cat "$staging_file" >> "$LOG_FILE"
    return 1
  fi
}

# Filtrar chunks por confidence
filter_chunks_by_confidence() {
  local staging_file=$1
  local threshold=${CONFIDENCE_THRESHOLD}

  # Usar jq para filtrar chunks com confidence >= threshold
  jq --arg threshold "$threshold" \
    '.chunks |= map(select(.confidence_score >= ($threshold | tonumber)))' \
    "$staging_file" > "${staging_file}.filtered"

  mv "${staging_file}.filtered" "$staging_file"

  local filtered_count=$(jq '.chunks | length' "$staging_file")
  log_info "Chunks após filtro de confiança: $filtered_count"
}

# Inserir chunks no Supabase
insert_chunks_to_supabase() {
  local staging_file=$1

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY RUN] Pulando inserção no Supabase"
    return 0
  fi

  log_info "Inserindo chunks no Supabase..."

  local chunks=$(jq '.chunks' "$staging_file")
  local chunk_count=$(echo "$chunks" | jq 'length')

  if [[ "$chunk_count" -eq 0 ]]; then
    log_warn "Nenhum chunk para inserir"
    return 0
  fi

  # Inserir cada chunk
  local inserted=0
  echo "$chunks" | jq -c '.[]' | while read -r chunk; do
    # Extrair collection_prefix e segment
    local collection=$(echo "$chunk" | jq -r '.collection_prefix')
    local segment=$(echo "$chunk" | jq -r '.segment')

    # Preparar payload para Supabase
    local payload=$(echo "$chunk" | jq '{
      collection_prefix: .collection_prefix,
      segment: .segment,
      document_id: .document_id,
      chunk_index: .chunk_index,
      content: .content,
      source_url: .source_url,
      source_type: "file",
      confidence_score: .confidence_score,
      validation_status: .validation_status,
      tags: []
    }')

    # Inserir
    if curl -s -X POST \
      "${SUPABASE_URL}/rest/v1/rag_chunks" \
      -H "Authorization: Bearer ${SUPABASE_KEY}" \
      -H "Content-Type: application/json" \
      -d "$payload" > /dev/null 2>&1; then
      ((inserted++))
    else
      log_error "Falha ao inserir chunk"
    fi
  done

  log_success "Inseridos $inserted chunks no Supabase"
}

# Atualizar status de coleção
update_collection_status() {
  local collection=$1

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY RUN] Pulando atualização de status"
    return 0
  fi

  log_info "Atualizando status da coleção: $collection"

  # Contar chunks validados e total
  local validated_count=$(curl -s \
    "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection}&validation_status=eq.validated&select=count=exact" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" | jq '.count // 0')

  local total_count=$(curl -s \
    "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection}&select=count=exact" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" | jq '.count // 0')

  # Calcular avg confidence
  local avg_confidence=$(curl -s \
    "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection}&select=confidence_score" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" | jq "add / length" 2>/dev/null || echo "0")

  # Atualizar status
  local payload=$(jq -n \
    --arg collection "$collection" \
    --arg validated "$validated_count" \
    --arg total "$total_count" \
    --arg avg_conf "$avg_confidence" \
    '{
      collection_prefix: $collection,
      validated_chunks: ($validated | tonumber),
      total_chunks: ($total | tonumber),
      avg_confidence_score: ($avg_conf | tonumber),
      last_update: now | todate
    }')

  curl -s -X PATCH \
    "${SUPABASE_URL}/rest/v1/rag_collection_status?collection_prefix=eq.${collection}" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" > /dev/null || log_warn "Falha ao atualizar status"

  log_success "Status atualizado: $collection (Total: $total_count, Validados: $validated_count, Avg Conf: $avg_confidence)"
}

# Processar uma coleção completa
process_collection() {
  local collection=$1
  local segment="${COLLECTION_SEGMENTS[$collection]}"

  log_info "=========================================="
  log_info "Processando Coleção: ${BLUE}${collection}${NC} (Segmento: $segment)"
  log_info "=========================================="

  local documents=($(discover_documents "$collection"))

  if [[ ${#documents[@]} -eq 0 ]]; then
    log_warn "Nenhum documento encontrado para coleção: $collection"
    return 0
  fi

  log_info "Documentos encontrados: ${#documents[@]}"

  # Processar cada documento
  local processed=0
  for doc in "${documents[@]}"; do
    if staging_file=$(process_single_document "$doc" "$collection" "$segment"); then
      filter_chunks_by_confidence "$staging_file"
      insert_chunks_to_supabase "$staging_file"
      ((processed++))
    fi
  done

  # Atualizar status da coleção
  update_collection_status "$collection"

  log_success "Processados $processed documentos para $collection"
}

# Gerar relatório final
generate_report() {
  log_info "=========================================="
  log_info "Gerando Relatório Final"
  log_info "=========================================="

  local report_file="${LOG_DIR}/rag-population-report-$(date +%Y-%m-%d-%H%M%S).json"

  local total_chunks=0
  local validated_chunks=0
  local collections_data=()

  for collection in "${!COLLECTION_SEGMENTS[@]}"; do
    local total=$(curl -s \
      "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection}&select=count=exact" \
      -H "Authorization: Bearer ${SUPABASE_KEY}" | jq '.count // 0')

    local validated=$(curl -s \
      "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection}&validation_status=eq.validated&select=count=exact" \
      -H "Authorization: Bearer ${SUPABASE_KEY}" | jq '.count // 0')

    total_chunks=$((total_chunks + total))
    validated_chunks=$((validated_chunks + validated))

    collections_data+=($(jq -n \
      --arg collection "$collection" \
      --arg total "$total" \
      --arg validated "$validated" \
      '{collection: $collection, total: ($total | tonumber), validated: ($validated | tonumber)}'))
  done

  local report=$(jq -n \
    --arg timestamp "$(date -Iseconds)" \
    --arg total_chunks "$total_chunks" \
    --arg validated_chunks "$validated_chunks" \
    --argjson collections "$(jq -s '.' <<< "$(printf '%s\n' "${collections_data[@]}")")" \
    '{
      timestamp: $timestamp,
      total_chunks: ($total_chunks | tonumber),
      validated_chunks: ($validated_chunks | tonumber),
      validation_percentage: (($validated_chunks / $total_chunks * 100) | floor),
      collections: $collections
    }')

  echo "$report" | jq . > "$report_file"

  log_success "Relatório gerado: $report_file"
  jq . "$report_file"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  init_logging
  check_prerequisites

  log_info "Iniciando população RAG"
  log_info "Dry run: $DRY_RUN"

  # Processar cada coleção
  for collection in "${!COLLECTION_SEGMENTS[@]}"; do
    process_collection "$collection" || log_error "Erro ao processar coleção: $collection"
  done

  # Gerar relatório final
  if [[ "$DRY_RUN" != "true" ]]; then
    generate_report
  fi

  log_success "População RAG concluída"
}

# Executar main
main "$@"
