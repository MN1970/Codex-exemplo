#!/bin/bash

# ============================================================================
# COLLECT-PUBLIC-DOCUMENTS.SH
# Automate collection of publicly available Brazilian government documents
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOC_DIR="${PROJECT_ROOT}/data/rag-docs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $@"; }
log_success() { echo -e "${GREEN}✓${NC} $@"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $@"; }

# ============================================================================
# DOWNLOAD HELPERS
# ============================================================================

download_file() {
    local url="$1"
    local output="$2"

    if curl -s -L -o "$output" "$url" 2>/dev/null; then
        return 0
    fi

    if wget -q -O "$output" "$url" 2>/dev/null; then
        return 0
    fi

    return 1
}

# ============================================================================
# CREATE SAMPLE DOCUMENTS FOR TESTING
# ============================================================================

create_sample_documents() {
    log_info "Creating sample documents for RAG testing..."

    local samples=(
        "san:sample-eta-design.txt:ETA (Estação de Tratamento de Água)"
        "ene:sample-transmissao.txt:Linhas de Transmissão de Energia"
        "por:sample-terminal.txt:Operação de Terminais Portuários"
        "aer:sample-pista.txt:Projeto de Pista de Pouso"
        "bar:sample-barragem.txt:Segurança de Barragens"
    )

    local count=0
    for sample in "${samples[@]}"; do
        IFS=':' read -r col filename title <<< "$sample"
        filepath="${DOC_DIR}/${col}/${filename}"

        cat > "$filepath" <<EOF
# $title

## Introdução
Este é um documento de amostra para teste do pipeline RAG (Retrieval-Augmented Generation).

## Contexto
Collection: $col
Data: $(date +"%Y-%m-%d")

## Conteúdo Técnico

### Seção 1: Fundamentos
Os princípios fundamentais da engenharia neste domínio incluem conformidade com normas brasileiras,
requisitos de segurança, e procedimentos operacionais estabelecidos por agências regulatórias.

### Seção 2: Especificações
- Padrão técnico: Conforme NBR aplicável
- Requisitos de segurança: Conforme legislação federal
- Procedimentos operacionais: Conforme manual de operação

### Seção 3: Implementação
A implementação deve seguir rigorosamente os procedimentos técnicos estabelecidos.
Todos os requisitos de qualidade devem ser atendidos.

### Seção 4: Validação
Os critérios de validação incluem testes de conformidade, inspeção visual,
e documentação completa de todas as etapas.

## Conclusão
Este documento serve como referência técnica para os procedimentos associados.
EOF

        log_success "Criado: $filename"
        ((count++))
    done

    echo "$count"
}

# ============================================================================
# VERIFY COLLECTION
# ============================================================================

verify_collection() {
    log_info "Verificando coleção de documentos..."

    echo ""
    echo "Contagem de documentos por coleção:"

    local total=0
    for col in san ene por aer bar; do
        count=$(find "${DOC_DIR}/${col}" -type f 2>/dev/null | wc -l)
        printf "  %-10s: %3d documentos\n" "$col:" "$count"
        total=$((total + count))
    done

    echo ""
    echo "TOTAL: $total documentos"
    
    if [ "$total" -ge 5 ]; then
        log_success "Amostra criada com sucesso!"
    fi
}

# ============================================================================
# MAIN
# ============================================================================

mkdir -p "${DOC_DIR}"/{san,ene,por,aer,bar}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║ COLETA DE DOCUMENTOS PÚBLICOS — Iniciando              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log_info "Criando documentos de amostra para teste..."
samples_count=$(create_sample_documents)

log_info "Verificando coleção..."
verify_collection

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║ PRÓXIMOS PASSOS                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "1. TESTE DO PIPELINE (com amostra)"
echo "   export DRY_RUN=true"
echo "   bash scripts/extract-and-populate-rag.sh"
echo ""
echo "2. COLETA MANUAL DE DOCUMENTOS (950 documentos totais)"
echo "   Sources:"
echo "     - ANEEL: https://www.aneel.gov.br/"
echo "     - ANTAQ: https://www.gov.br/antaq/"
echo "     - ANAC: https://www.gov.br/anac/"
echo "     - ANA: https://www.ana.gov.br/"
echo "     - EPE: https://www.epe.gov.br/"
echo "     - ONS: https://www.ons.org.br/"
echo ""
echo "3. PRODUÇÃO RAG (após coletar 950+ documentos)"
echo "   export DRY_RUN=false"
echo "   export SUPABASE_URL='...'"
echo "   export SUPABASE_KEY='...'"
echo "   bash scripts/extract-and-populate-rag.sh"
echo ""

