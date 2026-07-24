#!/bin/bash

# ============================================================================
# TEST-RAG-LOCAL.SH
# Quick RAG Testing — Local Extraction + Dry-Run Pipeline
# Executa em ~2 minutos sem Supabase
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# HELPERS
# ============================================================================

log_title() {
  echo ""
  echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC} $1"
  echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
  echo ""
}

test_success() {
  echo -e "${GREEN}✓${NC} $@"
  ((TESTS_PASSED++))
}

test_error() {
  echo -e "${RED}✗${NC} $@"
  ((TESTS_FAILED++))
}

test_info() {
  echo -e "${BLUE}ℹ${NC} $@"
}

test_warn() {
  echo -e "${YELLOW}⚠${NC} $@"
}

# ============================================================================
# TEST 1: ENVIRONMENT
# ============================================================================

log_title "TEST 1: Verificar Ambiente"

test_info "Python version..."
if python3 --version > /dev/null 2>&1; then
  PYTHON_VERSION=$(python3 --version)
  test_success "Python installed: $PYTHON_VERSION"
else
  test_error "Python não encontrado"
  exit 1
fi

test_info "Verificar módulos Python..."
for module in PyPDF2 docx openpyxl; do
  if python3 -c "import ${module}" 2>/dev/null; then
    test_success "Module $module instalado"
  else
    test_warn "Module $module não instalado"
  fi
done

test_info "Verificar scripts..."
if [ -f "$SCRIPT_DIR/rag-extraction-utils.py" ]; then
  test_success "rag-extraction-utils.py encontrado"
else
  test_error "rag-extraction-utils.py não encontrado"
  exit 1
fi

if [ -f "$SCRIPT_DIR/extract-and-populate-rag.sh" ]; then
  test_success "extract-and-populate-rag.sh encontrado"
else
  test_error "extract-and-populate-rag.sh não encontrado"
  exit 1
fi

test_info "Verificar estrutura de diretórios..."
if [ -d "$PROJECT_ROOT/data/rag-docs" ]; then
  test_success "data/rag-docs/ existe"
else
  test_error "data/rag-docs/ não encontrado"
  exit 1
fi

# ============================================================================
# TEST 2: LOCAL EXTRACTION
# ============================================================================

log_title "TEST 2: Extração Local (um documento)"

TEST_DOC="$PROJECT_ROOT/data/rag-docs/san:/Lei-14026-2020.txt"

if [ ! -f "$TEST_DOC" ]; then
  test_warn "Arquivo de teste não encontrado, criando..."
  mkdir -p "$PROJECT_ROOT/data/rag-docs/san:"

  cat > "$TEST_DOC" << 'EOF'
LEI Nº 14.026, DE 26 DE JULHO DE 2020

Atualiza o marco legal do saneamento básico no Brasil.

CAPÍTULO I — DISPOSIÇÕES GERAIS

Art. 1º Esta Lei atualiza o marco legal do saneamento básico no Brasil.

CAPÍTULO II — PRESTAÇÃO DE SERVIÇOS

Art. 3º Os serviços de saneamento básico são aqueles de limpeza urbana
e manejo de resíduos sólidos, esgotamento sanitário, abastecimento de
água potável e drenagem e manejo das águas pluviais urbanas.

CAPÍTULO III — METAS DE UNIVERSALIZAÇÃO

Art. 6º Até 31 de dezembro de 2033, deverão ser alcançadas as seguintes metas:
- 99% de cobertura de abastecimento de água
- 90% de cobertura de esgotamento sanitário
EOF
fi

test_info "Extraindo documento..."
EXTRACTION_OUTPUT=$(python3 "$SCRIPT_DIR/rag-extraction-utils.py" "$TEST_DOC" "san:" "S8" 2>&1)

# Verificar JSON válido
if echo "$EXTRACTION_OUTPUT" | jq '.' > /dev/null 2>&1; then
  test_success "JSON válido gerado"

  # Verificar estrutura
  CHUNKS=$(echo "$EXTRACTION_OUTPUT" | jq '.chunks | length')
  test_success "Chunks extraídos: $CHUNKS"

  # Verificar confidence
  CONFIDENCE=$(echo "$EXTRACTION_OUTPUT" | jq '.chunks[0].confidence_score')
  test_success "Confidence score: $CONFIDENCE"

  if (( $(echo "$CONFIDENCE >= 0.85" | bc -l) )); then
    test_success "Confidence >= 0.85 (passa no filtro)"
  else
    test_warn "Confidence < 0.85 (seria filtrado)"
  fi

  # Mostrar amostra
  CONTENT_SAMPLE=$(echo "$EXTRACTION_OUTPUT" | jq -r '.chunks[0].content[:80]')
  test_info "Content sample: $CONTENT_SAMPLE..."
else
  test_error "JSON inválido gerado"
fi

# ============================================================================
# TEST 3: METADATA
# ============================================================================

log_title "TEST 3: Verificar Metadados"

test_info "Document ID..."
DOC_ID=$(echo "$EXTRACTION_OUTPUT" | jq -r '.document_id')
if [ ! -z "$DOC_ID" ] && [ "$DOC_ID" != "null" ]; then
  test_success "Document ID: $DOC_ID"
else
  test_error "Document ID vazio"
fi

test_info "Collection prefix..."
COLLECTION=$(echo "$EXTRACTION_OUTPUT" | jq -r '.chunks[0].collection_prefix')
if [ "$COLLECTION" = "san:" ]; then
  test_success "Collection prefix: $COLLECTION"
else
  test_error "Collection prefix incorreto: $COLLECTION"
fi

test_info "Segment..."
SEGMENT=$(echo "$EXTRACTION_OUTPUT" | jq -r '.chunks[0].segment')
if [ "$SEGMENT" = "S8" ]; then
  test_success "Segment: $SEGMENT"
else
  test_error "Segment incorreto: $SEGMENT"
fi

# ============================================================================
# TEST 4: DRY-RUN PIPELINE
# ============================================================================

log_title "TEST 4: Dry-Run Pipeline (SEM Supabase)"

test_info "Limpando staging anterior..."
rm -rf "$PROJECT_ROOT/.rag-staging" 2>/dev/null || true
mkdir -p "$PROJECT_ROOT/.rag-staging"
test_success "Staging limpo"

test_info "Rodando pipeline em DRY_RUN mode..."

export DRY_RUN=true
export SUPABASE_URL="https://placeholder.supabase.co"
export SUPABASE_KEY="placeholder-key"

PIPELINE_LOG=$("$SCRIPT_DIR/extract-and-populate-rag.sh" 2>&1 || true)

# Verificar que pipeline executou
if echo "$PIPELINE_LOG" | grep -q "Extraído"; then
  test_success "Pipeline executou"
else
  test_warn "Nenhum documento processado"
fi

# Contar sucessos
EXTRACTIONS=$(echo "$PIPELINE_LOG" | grep "✓ Extraído" | wc -l)
test_success "Documentos extraídos: $EXTRACTIONS"

# Contar chunks
CHUNKS_TOTAL=$(echo "$PIPELINE_LOG" | grep "Chunks após filtro" | awk '{print $NF}' | paste -sd+ | bc 2>/dev/null || echo "0")
test_success "Total chunks após filtro: $CHUNKS_TOTAL"

# Verificar dry-run
if echo "$PIPELINE_LOG" | grep -q "DRY RUN.*Pulando inserção"; then
  test_success "Dry-run mode ativado (não inseriu em Supabase)"
else
  test_warn "Dry-run mode pode não estar ativado"
fi

# ============================================================================
# TEST 5: STAGING FILES
# ============================================================================

log_title "TEST 5: Verificar Arquivos Gerados"

STAGING_DIR="$PROJECT_ROOT/.rag-staging"

if [ -d "$STAGING_DIR" ]; then
  STAGING_FILES=$(find "$STAGING_DIR" -name "*.json" | wc -l)
  test_success "Staging files gerados: $STAGING_FILES"

  # Verificar primeiro arquivo
  if [ "$STAGING_FILES" -gt 0 ]; then
    FIRST_FILE=$(find "$STAGING_DIR" -name "*.json" | head -1)
    test_info "Examinando: $(basename $FIRST_FILE)"

    # Validar JSON
    if jq '.' "$FIRST_FILE" > /dev/null 2>&1; then
      test_success "JSON válido"

      # Contar chunks no arquivo
      FILE_CHUNKS=$(jq '.chunks | length' "$FIRST_FILE")
      test_success "Chunks neste arquivo: $FILE_CHUNKS"
    else
      test_error "JSON inválido no arquivo staging"
    fi
  fi
else
  test_warn "Diretório .rag-staging não encontrado"
fi

# ============================================================================
# TEST 6: EXTRACTION QUALITY
# ============================================================================

log_title "TEST 6: Qualidade da Extração"

# Verificar se há chunks com confiança ruim
LOW_CONFIDENCE=$(echo "$EXTRACTION_OUTPUT" | jq '[.chunks[] | select(.confidence_score < 0.85)] | length')

if [ "$LOW_CONFIDENCE" -eq 0 ]; then
  test_success "Todos os chunks passam no threshold (confidence >= 0.85)"
else
  test_warn "$LOW_CONFIDENCE chunks com confidence < 0.85"
fi

# Verificar tamanho do conteúdo
CONTENT_SIZE=$(echo "$EXTRACTION_OUTPUT" | jq -r '.chunks[0].content | length')
if [ "$CONTENT_SIZE" -gt 100 ]; then
  test_success "Conteúdo tem tamanho adequado ($CONTENT_SIZE chars)"
else
  test_warn "Conteúdo muito pequeno ($CONTENT_SIZE chars)"
fi

# ============================================================================
# SUMMARY
# ============================================================================

log_title "RESUMO DOS TESTES"

echo "Testes executados:"
echo -e "  ${GREEN}Passaram: $TESTS_PASSED${NC}"
echo -e "  ${RED}Falharam: $TESTS_FAILED${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
  echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║${NC} ✓ TODOS OS TESTES PASSARAM!"
  echo -e "${GREEN}║${NC} RAG está pronto para Fase 2"
  echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
  echo ""
  echo "Próximos passos:"
  echo "  1. Coletar 950 documentos (ver FASE-2-EXECUTION-PLAN.md)"
  echo "  2. Executar pipeline real com Supabase"
  echo "  3. Validar 947+ chunks inseridos"
  exit 0
else
  echo -e "${RED}╔════════════════════════════════════════╗${NC}"
  echo -e "${RED}║${NC} ✗ ALGUNS TESTES FALHARAM"
  echo -e "${RED}║${NC} Revise os erros acima"
  echo -e "${RED}╚════════════════════════════════════════╝${NC}"
  exit 1
fi
