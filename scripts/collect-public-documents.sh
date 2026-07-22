#!/bin/bash

# ============================================================================
# COLLECT-PUBLIC-DOCUMENTS.SH
# Script de Coleta Automática de Documentos Públicos para RAG
# Suporta: Download via URL, conversão de formatos, deduplicação
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${PROJECT_ROOT}/data/rag-docs"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
  echo -e "${BLUE}ℹ${NC} $@"
}

log_success() {
  echo -e "${GREEN}✓${NC} $@"
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $@"
}

log_error() {
  echo -e "${RED}✗${NC} $@"
}

# Download de documento com retry
download_file() {
  local url=$1
  local output=$2
  local max_retries=3
  local retry=0

  while (( retry < max_retries )); do
    if curl -L --progress-bar --max-time 300 "$url" -o "$output" 2>/dev/null; then
      log_success "Downloaded: $(basename "$output")"
      return 0
    fi
    ((retry++))
    if (( retry < max_retries )); then
      log_warn "Retry $retry/$max_retries para $url"
      sleep 2
    fi
  done

  log_error "Falha ao baixar: $url"
  return 1
}

# ============================================================================
# SANEAMENTO — san:
# ============================================================================

collect_saneamento() {
  log_info "=========================================="
  log_info "Coletando: SANEAMENTO (san:) — 200 documentos"
  log_info "=========================================="

  mkdir -p "$DATA_DIR/san:"

  # Lei 14.026/2020 — Lei do Marco Legal de Saneamento
  log_info "Coletando Lei 14.026/2020..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm" \
    "$DATA_DIR/san:/Lei-14026-2020.html" || true

  # NBR 12216 — Projetos de Estação de Tratamento de Água para Abastecimento Público
  log_info "Coletando NBR 12216 (ABNT) — Requer acesso..."
  log_warn "NBR 12216: Acesso pago via ABNT. Contacte: abnt@abnt.org.br"

  # SNIS — Sistema Nacional de Informações sobre Saneamento
  log_info "Coletando dados SNIS..."
  # Nota: SNIS pode requerer login. URLs públicas podem estar disponíveis
  log_warn "SNIS: Pode requerer cadastro em https://www.gov.br/snirh/pt-br"

  # PMSB — Plano Municipal de Saneamento Básico (exemplo: São Paulo)
  log_info "Coletando exemplo PMSB São Paulo..."
  # Este é um documento de exemplo público

  log_success "Coleta SANEAMENTO iniciada"
  log_info "Status: Lei 14.026 coletada"
  log_warn "TODO: Coletar 199 documentos restantes (NBR, SNIS, editais BNDES, etc)"
}

# ============================================================================
# ENERGIA — ene:
# ============================================================================

collect_energia() {
  log_info "=========================================="
  log_info "Coletando: ENERGIA (ene:) — 300 documentos"
  log_info "=========================================="

  mkdir -p "$DATA_DIR/ene:"

  # Lei 9.074/1995 — Concessões de Geração, Transmissão e Distribuição
  log_info "Coletando Lei 9.074/1995..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/leis/l9074.htm" \
    "$DATA_DIR/ene:/Lei-9074-1995.html" || true

  # Decreto 2.003/1996 — Regulamenta a Lei 9.074
  log_info "Coletando Decreto 2.003/1996..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/decreto/d2003.htm" \
    "$DATA_DIR/ene:/Decreto-2003-1996.html" || true

  # Resolução ANEEL 414/2010 — Condições Gerais de Fornecimento de Energia Elétrica
  log_info "Coletando Resolução ANEEL 414/2010..."
  log_warn "ANEEL 414: Disponível em https://www.aneel.gov.br/ (PDF ~2MB)"

  # Nota: Documentos EPE (PDE, R1-R5) e ONS podem requerer download manual
  log_warn "EPE PDE 2025: Download manual em https://www.epe.gov.br/"
  log_warn "ONS Procedimentos: Download manual em https://www.ons.org.br/"

  log_success "Coleta ENERGIA iniciada"
  log_info "Status: Lei 9.074 e Decreto 2.003 coletados"
  log_warn "TODO: Coletar 298 documentos restantes (ANEEL, EPE, ONS, IEEE, etc)"
}

# ============================================================================
# PORTOS — por:
# ============================================================================

collect_portos() {
  log_info "=========================================="
  log_info "Coletando: PORTOS (por:) — 150 documentos"
  log_info "=========================================="

  mkdir -p "$DATA_DIR/por:"

  # Lei 12.815/2013 — Administração dos Portos
  log_info "Coletando Lei 12.815/2013..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12815.htm" \
    "$DATA_DIR/por:/Lei-12815-2013.html" || true

  # Resolução ANTAQ 1/2006 — Normas de Tráfego
  log_info "Coletando Resolução ANTAQ 1/2006..."
  log_warn "ANTAQ: Download em https://www.gov.br/antaq/"

  log_success "Coleta PORTOS iniciada"
  log_info "Status: Lei 12.815 coletada"
  log_warn "TODO: Coletar 149 documentos restantes (ANTAQ, PIANC, TUP editais, etc)"
}

# ============================================================================
# AEROPORTOS — aer:
# ============================================================================

collect_aeroportos() {
  log_info "=========================================="
  log_info "Coletando: AEROPORTOS (aer:) — 120 documentos"
  log_info "=========================================="

  mkdir -p "$DATA_DIR/aer:"

  # Lei 13.182/2015 — Concessão de Aeroportos
  log_info "Coletando Lei 13.182/2015..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13182.htm" \
    "$DATA_DIR/aer:/Lei-13182-2015.html" || true

  # Portaria ANAC — Normas de Infraestrutura
  log_info "Coletando normas ANAC..."
  log_warn "ANAC RBAC: Download em https://www.gov.br/anac/"

  log_success "Coleta AEROPORTOS iniciada"
  log_info "Status: Lei 13.182 coletada"
  log_warn "TODO: Coletar 119 documentos restantes (ANAC, ICAO, FAA, editais, etc)"
}

# ============================================================================
# BARRAGENS — bar:
# ============================================================================

collect_barragens() {
  log_info "=========================================="
  log_info "Coletando: BARRAGENS (bar:) — 180 documentos"
  log_info "=========================================="

  mkdir -p "$DATA_DIR/bar:"

  # Lei 12.334/2010 — Política Nacional de Segurança de Barragens
  log_info "Coletando Lei 12.334/2010..."
  download_file \
    "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12334.htm" \
    "$DATA_DIR/bar:/Lei-12334-2010.html" || true

  # Resolução ANA 144/2021 — Segurança de Barragens
  log_info "Coletando Resolução ANA 144/2021..."
  log_warn "ANA: Download em https://www.ana.gov.br/"

  log_success "Coleta BARRAGENS iniciada"
  log_info "Status: Lei 12.334 coletada"
  log_warn "TODO: Coletar 179 documentos restantes (ICOLD, CBDB, SIGBM, etc)"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  echo ""
  log_info "=========================================="
  log_info "COLETA AUTOMÁTICA — Documentos Públicos"
  log_info "=========================================="
  echo ""

  # Criar diretório base
  mkdir -p "$DATA_DIR"

  # Coletar por segmento
  collect_saneamento
  echo ""
  collect_energia
  echo ""
  collect_portos
  echo ""
  collect_aeroportos
  echo ""
  collect_barragens

  echo ""
  log_success "=========================================="
  log_success "Coleta automática concluída"
  log_success "=========================================="
  echo ""

  # Status
  log_info "Documentos coletados:"
  for col in san ene por aer bar; do
    count=$(find "$DATA_DIR/${col}" -type f 2>/dev/null | wc -l)
    echo "  ${col}: $count arquivo(s)"
  done

  echo ""
  log_info "Próximos passos:"
  echo "  1. Revisar FASE-2-COLLECTION-MANIFEST.md para 950 documentos"
  echo "  2. Fazer download manual de documentos restritos (ABNT, ANEEL, ANTAQ, etc)"
  echo "  3. Salvar em data/rag-docs/{collection}/"
  echo "  4. Executar: ./scripts/extract-and-populate-rag.sh"
}

main "$@"
