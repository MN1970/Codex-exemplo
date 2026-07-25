#!/bin/bash

# ============================================================================
# MAESTRO-PARALLEL.SH
# Orchestrador de Execução Paralela para 60 Agentes da Manta Maestro
# Versão: 5.0.0
# Data: 2026-07-22
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${PROJECT_ROOT}/agents-config-60.json"

MAX_CONCURRENT_AGENTS=20
TIMEOUT_PER_AGENT=30
RETRY_MAX_ATTEMPTS=4
RETRY_BACKOFF=(2 4 8 16)

SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"

LOG_DIR="${PROJECT_ROOT}/logs/maestro"
EXECUTION_ID="$(date +%s)-$(openssl rand -hex 4)"
LOG_FILE="${LOG_DIR}/maestro-${EXECUTION_ID}.log"

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
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Maestro Execution Started: $EXECUTION_ID" | tee "$LOG_FILE"
}

log_message() {
  local level=$1
  shift
  local message="$@"
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${level}: ${message}" | tee -a "$LOG_FILE"
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

  if ! command -v jq &> /dev/null; then
    log_error "jq não encontrado. Instale com: apt-get install -y jq"
    exit 1
  fi

  if ! command -v curl &> /dev/null; then
    log_error "curl não encontrado. Instale com: apt-get install -y curl"
    exit 1
  fi

  if [[ ! -f "$CONFIG_FILE" ]]; then
    log_error "Arquivo de configuração não encontrado: $CONFIG_FILE"
    exit 1
  fi

  if [[ -z "$SUPABASE_URL" ]] || [[ -z "$SUPABASE_KEY" ]]; then
    log_warn "SUPABASE_URL ou SUPABASE_KEY não definidos. Logging será apenas local."
  fi

  log_success "Pré-requisitos validados"
}

# Extrair lista de agentes do config
get_all_agents() {
  jq -r '
    [
      (.eixo_1_horizontais.agents[] | .id),
      (.eixo_2_verticais_por_segmento.agents[] | .id),
      (.eixo_3_especializados_por_fase.segments_with_subagents[] | .subagents[] | .id)
    ] | .[]
  ' "$CONFIG_FILE"
}

# Obter peso de concorrência de um agente
get_agent_concurrency_weight() {
  local agent_id=$1
  jq -r "
    (
      (.eixo_1_horizontais.agents[] | select(.id == \"$agent_id\") | .concurrency_weight),
      (.eixo_2_verticais_por_segmento.agents[] | select(.id == \"$agent_id\") | .concurrency_weight),
      (.eixo_3_especializados_por_fase.segments_with_subagents[] | .subagents[] | select(.id == \"$agent_id\") | .concurrency_weight)
    ) | first
  " "$CONFIG_FILE"
}

# Obter nome do agente
get_agent_name() {
  local agent_id=$1
  jq -r "
    (
      (.eixo_1_horizontais.agents[] | select(.id == \"$agent_id\") | .name),
      (.eixo_2_verticais_por_segmento.agents[] | select(.id == \"$agent_id\") | .name),
      (.eixo_3_especializados_por_fase.segments_with_subagents[] | .subagents[] | select(.id == \"$agent_id\") | .name)
    ) | first
  " "$CONFIG_FILE"
}

# Atualizar log de execução no Supabase
log_to_supabase() {
  local agent_id=$1
  local status=$2
  local duration_ms=$3
  local output_summary=${4:-""}

  if [[ -z "$SUPABASE_URL" ]] || [[ -z "$SUPABASE_KEY" ]]; then
    return 0
  fi

  local payload=$(jq -n \
    --arg agent_id "$agent_id" \
    --arg status "$status" \
    --arg duration_ms "$duration_ms" \
    --arg output_summary "$output_summary" \
    --arg execution_id "$EXECUTION_ID" \
    '{
      agent_id: $agent_id,
      status: $status,
      duration_ms: ($duration_ms | tonumber),
      output_summary: $output_summary,
      execution_id: $execution_id
    }')

  curl -s -X POST \
    "${SUPABASE_URL}/rest/v1/agent_execution_log" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" > /dev/null 2>&1 || true
}

# Executar um agente com retry
execute_agent() {
  local agent_id=$1
  local agent_name=$2
  local weight=$3

  local attempt=1
  local start_time=$(date +%s%N)

  while (( attempt <= RETRY_MAX_ATTEMPTS )); do
    log_info "Executando agente: ${BLUE}${agent_name}${NC} (ID: ${agent_id}) [Tentativa ${attempt}/${RETRY_MAX_ATTEMPTS}]"

    # Simular execução do agente
    # Em produção, isso chamaria a API do Claude ou executaria o agente real
    if timeout "$TIMEOUT_PER_AGENT" bash -c "
      # Placeholder para execução real do agente
      sleep $((RANDOM % 5 + 1))
      exit 0
    "; then
      local end_time=$(date +%s%N)
      local duration_ms=$(( (end_time - start_time) / 1000000 ))

      log_success "Agente ${agent_name} completado (${duration_ms}ms)"
      log_to_supabase "$agent_id" "completed" "$duration_ms" "Execução bem-sucedida"

      return 0
    else
      local exit_code=$?
      if (( exit_code == 124 )); then
        log_warn "Agente ${agent_name} timeout"
        if (( attempt < RETRY_MAX_ATTEMPTS )); then
          local backoff=${RETRY_BACKOFF[$((attempt - 1))]}
          log_info "Aguardando ${backoff}s antes de retry..."
          sleep "$backoff"
        fi
      else
        log_error "Agente ${agent_name} falhou com código $exit_code"
        log_to_supabase "$agent_id" "failed" "0" "Falha na execução (código: $exit_code)"
        return 1
      fi
    fi

    ((attempt++))
  done

  log_error "Agente ${agent_name} falhou após ${RETRY_MAX_ATTEMPTS} tentativas"
  log_to_supabase "$agent_id" "failed" "0" "Falha permanente após retries"
  return 1
}

# Gerenciar fila de execução paralela
execute_parallel() {
  local -a agents=("$@")
  local -a running_pids=()
  local -a running_agents=()
  local current_weight=0
  local batch_num=1

  log_info "Iniciando execução paralela com máximo de ${MAX_CONCURRENT_AGENTS} agentes simultâneos"
  log_info "Total de agentes a executar: ${#agents[@]}"

  local agent_idx=0
  while (( agent_idx < ${#agents[@]} )) || (( ${#running_pids[@]} > 0 )); do
    # Limpar pids completados
    local cleaned_pids=()
    for pid in "${running_pids[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        cleaned_pids+=("$pid")
      fi
    done
    running_pids=("${cleaned_pids[@]}")
    running_agents=("${running_agents[@]:0:${#running_pids[@]}}")

    # Adicionar novos agentes até atingir limite
    while (( agent_idx < ${#agents[@]} )) && (( ${#running_pids[@]} < MAX_CONCURRENT_AGENTS )); do
      local agent_id="${agents[$agent_idx]}"
      local agent_name=$(get_agent_name "$agent_id")
      local weight=$(get_agent_concurrency_weight "$agent_id")

      execute_agent "$agent_id" "$agent_name" "$weight" &
      local pid=$!

      running_pids+=("$pid")
      running_agents+=("${agent_name}")

      log_info "Agente enfileirado: ${agent_name} (PID: ${pid}) [${#running_pids[@]}/${MAX_CONCURRENT_AGENTS}]"

      ((agent_idx++))
    done

    # Aguardar um pouco antes de verificar status
    sleep 1
  done

  log_success "Execução paralela completa. ${#agents[@]} agentes processados."
}

# Gerar relatório de execução
generate_report() {
  log_info "Gerando relatório de execução..."

  local report_file="${LOG_DIR}/maestro-report-${EXECUTION_ID}.json"

  jq -n \
    --arg execution_id "$EXECUTION_ID" \
    --arg start_time "$(date -Iseconds)" \
    --arg log_file "$LOG_FILE" \
    '{
      execution_id: $execution_id,
      timestamp: $start_time,
      log_file: $log_file,
      max_concurrent_agents: '${MAX_CONCURRENT_AGENTS}',
      total_agents_configured: 60,
      status: "completed"
    }' > "$report_file"

  log_success "Relatório gerado: $report_file"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  init_logging
  check_prerequisites

  local all_agents=($(get_all_agents))

  if (( ${#all_agents[@]} == 0 )); then
    log_error "Nenhum agente encontrado no arquivo de configuração"
    exit 1
  fi

  log_info "Carregados ${#all_agents[@]} agentes da configuração"

  execute_parallel "${all_agents[@]}"
  generate_report

  log_info "Maestro execution completed: $EXECUTION_ID"
}

# Executar main
main "$@"
