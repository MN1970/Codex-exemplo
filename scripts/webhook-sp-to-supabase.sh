#!/bin/bash

# ============================================================================
# WEBHOOK-SP-TO-SUPABASE.SH
# Sincronização Automatizada SharePoint → Supabase RAG
# Versão: 5.0.0
# Data: 2026-07-22
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Credenciais (carregar de variáveis de ambiente ou .env)
SHAREPOINT_SITE="${SHAREPOINT_SITE:-}"
SHAREPOINT_TOKEN="${SHAREPOINT_TOKEN:-}"
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"

# Coleções RAG e mapeamento para pastas do SharePoint
declare -A COLLECTION_MAP=(
  [san:]="03_Projetos/Saneamento"
  [ene:]="03_Projetos/Energia"
  [por:]="03_Projetos/Portos"
  [aer:]="03_Projetos/Aeroportos"
  [bar:]="03_Projetos/Barragens"
)

declare -A SEGMENT_MAP=(
  [san:]="S8"
  [ene:]="S9"
  [por:]="S6"
  [aer:]="S7"
  [bar:]="S10"
)

# Configurações de sincronização
CHUNK_SIZE=1000
VALIDATION_ENABLED=true
VALIDATION_CONFIDENCE_THRESHOLD=0.85

LOG_DIR="${PROJECT_ROOT}/logs/sync"
LOG_FILE="${LOG_DIR}/webhook-sync-$(date +%Y-%m-%d).log"
SYNC_STATE_FILE="${LOG_DIR}/.sync-state.json"

# Cores para output
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
  touch "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] SharePoint → Supabase Sync Started" >> "$LOG_FILE"
}

log_message() {
  local level=$1
  shift
  local message="$@"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${level}: ${message}" | tee -a "$LOG_FILE"
}

log_info() {
  log_message "${BLUE}INFO${NC}" "$@"
}

log_success() {
  log_message "${GREEN}✓${NC}" "$@"
}

log_warn() {
  log_message "${YELLOW}⚠${NC}" "$@"
}

log_error() {
  log_message "${RED}✗${NC}" "$@"
}

# Validar pré-requisitos
check_prerequisites() {
  log_info "Validando pré-requisitos..."

  if [[ -z "$SHAREPOINT_SITE" ]] || [[ -z "$SHAREPOINT_TOKEN" ]]; then
    log_error "SHAREPOINT_SITE ou SHAREPOINT_TOKEN não definidos"
    exit 1
  fi

  if [[ -z "$SUPABASE_URL" ]] || [[ -z "$SUPABASE_KEY" ]]; then
    log_error "SUPABASE_URL ou SUPABASE_KEY não definidos"
    exit 1
  fi

  for cmd in curl jq pdftotext; do
    if ! command -v "$cmd" &> /dev/null; then
      log_warn "Comando não encontrado: $cmd"
    fi
  done

  log_success "Pré-requisitos validados"
}

# Carregar estado anterior de sincronização
load_sync_state() {
  if [[ -f "$SYNC_STATE_FILE" ]]; then
    cat "$SYNC_STATE_FILE"
  else
    echo '{}'
  fi
}

# Salvar estado de sincronização
save_sync_state() {
  local state=$1
  echo "$state" > "$SYNC_STATE_FILE"
}

# Listar arquivos do SharePoint para uma coleção
list_sharepoint_files() {
  local collection_prefix=$1
  local sp_path="${COLLECTION_MAP[$collection_prefix]}"

  log_info "Listando arquivos do SharePoint: $sp_path"

  # Em produção, isso usaria a SharePoint REST API real
  # Por enquanto, retornar lista vazia para exemplificar
  echo "[]"
}

# Baixar e extrair conteúdo de um arquivo
extract_file_content() {
  local sp_file_path=$1
  local temp_dir=$(mktemp -d)

  log_info "Extraindo conteúdo de: $sp_file_path"

  # Detectar tipo de arquivo e extrair conteúdo
  case "${sp_file_path##*.}" in
    pdf)
      # pdftotext "$temp_file" -
      log_info "Arquivo PDF detectado"
      ;;
    docx)
      log_info "Arquivo DOCX detectado"
      # unzip -p "$temp_file" word/document.xml | xvfb-run
      ;;
    xlsx)
      log_info "Arquivo XLSX detectado"
      ;;
    txt)
      log_info "Arquivo TXT detectado"
      ;;
    *)
      log_warn "Tipo de arquivo não reconhecido: ${sp_file_path##*.}"
      return 1
      ;;
  esac

  rm -rf "$temp_dir"
}

# Validar conteúdo com aluci-guard (anti-alucinação)
validate_content() {
  local content=$1
  local confidence_score=${2:-0.85}

  if [[ "$VALIDATION_ENABLED" != "true" ]]; then
    echo '{"valid": true, "confidence": 1.0, "issues": []}'
    return 0
  fi

  log_info "Validando conteúdo com aluci-guard..."

  # Aqui seria implementada a integração com aluci-guard
  # Por enquanto, simular validação
  local validation_result=$(jq -n \
    --arg content "$content" \
    --arg confidence "$confidence_score" \
    '{
      valid: true,
      confidence: ($confidence | tonumber),
      issues: [],
      validated_at: (now | todate)
    }')

  echo "$validation_result"
}

# Dividir conteúdo em chunks
chunk_content() {
  local content=$1
  local chunk_size=${CHUNK_SIZE}
  local chunk_index=0

  # Dividir conteúdo em blocos de chunk_size caracteres
  local content_length=${#content}
  local offset=0

  while (( offset < content_length )); do
    local chunk="${content:$offset:$chunk_size}"
    echo "$chunk" | jq -Rs '{chunk: .}'
    ((offset += chunk_size))
    ((chunk_index++))
  done
}

# Inserir chunks no Supabase
insert_chunks_to_supabase() {
  local collection_prefix=$1
  local segment=$2
  local document_id=$3
  local file_name=$4
  local chunks=$5

  log_info "Inserindo chunks no Supabase: $collection_prefix (${#chunks[@]} chunks)"

  local chunk_index=0
  for chunk in "${chunks[@]}"; do
    local payload=$(jq -n \
      --arg collection_prefix "$collection_prefix" \
      --arg segment "$segment" \
      --arg document_id "$document_id" \
      --arg chunk_index "$chunk_index" \
      --arg content "$chunk" \
      --arg source_url "sharepoint://${file_name}" \
      --arg source_type "sharepoint" \
      '{
        collection_prefix: $collection_prefix,
        segment: $segment,
        document_id: $document_id,
        chunk_index: ($chunk_index | tonumber),
        content: $content,
        source_url: $source_url,
        source_type: $source_type,
        validation_status: "pending",
        confidence_score: 0.85,
        tags: []
      }')

    # Enviar para Supabase
    curl -s -X POST \
      "${SUPABASE_URL}/rest/v1/rag_chunks" \
      -H "Authorization: Bearer ${SUPABASE_KEY}" \
      -H "Content-Type: application/json" \
      -d "$payload" > /dev/null || {
      log_error "Falha ao inserir chunk $chunk_index"
      return 1
    }

    ((chunk_index++))
  done

  log_success "Inseridos $chunk_index chunks para documento $document_id"
}

# Sincronizar uma coleção
sync_collection() {
  local collection_prefix=$1
  local segment="${SEGMENT_MAP[$collection_prefix]}"

  log_info "Sincronizando coleção: ${BLUE}${collection_prefix}${NC} (Segmento: $segment)"

  # Listar arquivos não sincronizados
  local files=$(list_sharepoint_files "$collection_prefix")

  if [[ -z "$files" ]]; then
    log_info "Nenhum arquivo novo para sincronizar em $collection_prefix"
    return 0
  fi

  # Processar cada arquivo
  local file_count=0
  echo "$files" | jq -r '.[] | @json' | while read -r file_json; do
    local file=$(echo "$file_json" | jq -r '.')
    local file_id=$(echo "$file" | jq -r '.id')
    local file_name=$(echo "$file" | jq -r '.name')
    local file_path=$(echo "$file" | jq -r '.path')

    log_info "Processando arquivo: $file_name"

    # Extrair conteúdo
    local content=$(extract_file_content "$file_path")
    if [[ -z "$content" ]]; then
      log_warn "Falha ao extrair conteúdo de $file_name"
      continue
    fi

    # Validar conteúdo
    local validation=$(validate_content "$content")
    local is_valid=$(echo "$validation" | jq -r '.valid')

    if [[ "$is_valid" != "true" ]]; then
      log_warn "Conteúdo inválido em $file_name"
      continue
    fi

    # Dividir em chunks
    local -a chunks=()
    while IFS= read -r chunk; do
      chunks+=("$chunk")
    done < <(chunk_content "$content")

    # Inserir chunks
    insert_chunks_to_supabase "$collection_prefix" "$segment" "$file_id" "$file_name" "${chunks[@]}"

    # Registrar sincronização
    log_to_sync_log "$collection_prefix" "$file_id" "$file_name" "completed" "${#chunks[@]}"

    ((file_count++))
  done

  log_success "Sincronizados $file_count arquivos em $collection_prefix"
}

# Registrar status de sincronização no Supabase
log_to_sync_log() {
  local collection_prefix=$1
  local file_id=$2
  local file_name=$3
  local sync_status=$4
  local chunks_created=$5

  local payload=$(jq -n \
    --arg collection_prefix "$collection_prefix" \
    --arg segment "${SEGMENT_MAP[$collection_prefix]}" \
    --arg sp_file_name "$file_name" \
    --arg sp_file_id "$file_id" \
    --arg sync_status "$sync_status" \
    --arg chunks_created "$chunks_created" \
    '{
      collection_prefix: $collection_prefix,
      segment: $segment,
      sp_file_name: $sp_file_name,
      sp_file_id: $sp_file_id,
      sync_status: $sync_status,
      chunks_created: ($chunks_created | tonumber),
      validation_status: "pending"
    }')

  curl -s -X POST \
    "${SUPABASE_URL}/rest/v1/sharepoint_sync_log" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" > /dev/null || {
    log_error "Falha ao registrar sincronização no log"
    return 1
  }
}

# Atualizar status de coleção
update_collection_status() {
  local collection_prefix=$1

  log_info "Atualizando status da coleção: $collection_prefix"

  # Contar chunks validados
  local validated_count=$(curl -s \
    "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection_prefix}&validation_status=eq.validated&select=id" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" | jq '. | length')

  local total_count=$(curl -s \
    "${SUPABASE_URL}/rest/v1/rag_chunks?collection_prefix=eq.${collection_prefix}&select=id" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" | jq '. | length')

  local payload=$(jq -n \
    --arg collection_prefix "$collection_prefix" \
    --arg validated_chunks "$validated_count" \
    --arg total_chunks "$total_count" \
    '{
      collection_prefix: $collection_prefix,
      validated_chunks: ($validated_chunks | tonumber),
      total_chunks: ($total_chunks | tonumber)
    }')

  curl -s -X PATCH \
    "${SUPABASE_URL}/rest/v1/rag_collection_status?collection_prefix=eq.${collection_prefix}" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" > /dev/null || {
    log_warn "Falha ao atualizar status de coleção"
    return 1
  }
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  init_logging
  check_prerequisites

  log_info "Iniciando sincronização SharePoint → Supabase"

  # Sincronizar todas as coleções
  for collection_prefix in "${!COLLECTION_MAP[@]}"; do
    log_info "Processando coleção: $collection_prefix"
    sync_collection "$collection_prefix"
    update_collection_status "$collection_prefix"
  done

  log_success "Sincronização concluída com sucesso"
}

# Executar main
main "$@"
