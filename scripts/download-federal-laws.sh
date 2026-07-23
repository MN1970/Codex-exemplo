#!/bin/bash
# Download 5 Federal Laws — Phase 2 Day 1
# Lei 14.026 (Saneamento), Lei 9.074 (Energia), Lei 12.815 (Portos)
# Lei 13.182 (Aeroportos), Lei 12.334 (Barragens)

set -e

BASE_DIR="data/rag-docs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/rag-population/phase2-laws-download-${TIMESTAMP}.log"

# Ensure directories exist
mkdir -p "$BASE_DIR"/{san,ene,por,aer,bar}
mkdir -p logs/rag-population

echo "============================================"
echo "FASE 2 — Downloading 5 Federal Laws"
echo "============================================"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo ""

# Function to download with error handling
download_law() {
    local name=$1
    local url=$2
    local collection=$3
    local filename=$4

    echo "→ Downloading: $name..."

    if curl -s -f -L "$url" -o "$BASE_DIR/$collection/$filename" 2>/dev/null; then
        local size=$(du -h "$BASE_DIR/$collection/$filename" | cut -f1)
        echo "  ✓ Downloaded: $filename ($size)" | tee -a "$LOG_FILE"
        return 0
    else
        echo "  ✗ Failed: $name (URL may be restricted)" | tee -a "$LOG_FILE"
        # Create placeholder document
        cat > "$BASE_DIR/$collection/$filename" <<EOF
# $name
## Lei Federal Brasileira

**Título:** $name
**Data:** $(date +%Y-%m-%d)
**Fonte:** planalto.gov.br
**Status:** Download falhou - acesso restrito ao servidor

Este é um documento de referência. Para o conteúdo completo:
1. Visite: $url
2. Salve como PDF
3. Coloque em: $BASE_DIR/$collection/

### Instruções de Download Manual
- Abra o link no navegador
- Use "Salvar página como..." (Ctrl+S no Chrome/Firefox)
- Formato: PDF ou Documento Word
- Salve em: $BASE_DIR/$collection/
EOF
        local size=$(du -h "$BASE_DIR/$collection/$filename" | cut -f1)
        echo "  ⚠ Criado placeholder: $filename ($size)" | tee -a "$LOG_FILE"
        return 1
    fi
}

echo "[1/5] Lei 14.026/2020 — Saneamento Básico"
download_law "Lei 14.026/2020" \
    "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm" \
    "san" "Lei-14026-2020-Saneamento.pdf"

echo ""
echo "[2/5] Lei 9.074/1995 — Energia Elétrica"
download_law "Lei 9.074/1995" \
    "https://www.planalto.gov.br/ccivil_03/leis/l9074.htm" \
    "ene" "Lei-9074-1995-Energia.pdf"

echo ""
echo "[3/5] Lei 12.815/2013 — Portos"
download_law "Lei 12.815/2013" \
    "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12815.htm" \
    "por" "Lei-12815-2013-Portos.pdf"

echo ""
echo "[4/5] Lei 13.182/2015 — Aeroportos"
download_law "Lei 13.182/2015" \
    "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13182.htm" \
    "aer" "Lei-13182-2015-Aeroportos.pdf"

echo ""
echo "[5/5] Lei 12.334/2010 — Barragens"
download_law "Lei 12.334/2010" \
    "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12334.htm" \
    "bar" "Lei-12334-2010-Barragens.pdf"

echo ""
echo "============================================"
echo "Summary:"
echo "============================================"

for col in san ene por aer bar; do
    count=$(find "$BASE_DIR/$col" -type f | wc -l)
    case $col in
        san) target="200 (Saneamento)" ;;
        ene) target="300 (Energia)" ;;
        por) target="150 (Portos)" ;;
        aer) target="120 (Aeroportos)" ;;
        bar) target="180 (Barragens)" ;;
    esac
    printf "  %-3s: %2d docs / %-30s\n" "$col" "$count" "$target" | tee -a "$LOG_FILE"
done

total=$(find "$BASE_DIR" -type f | wc -l)
echo ""
echo "  TOTAL: $total / 950 docs ($(( total * 100 / 950 ))%)" | tee -a "$LOG_FILE"

echo ""
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo ""
echo "✅ Next: Download BNDES + SNIS documents"
echo "   Veja: FASE2-EXECUCAO-AGORA.md (seção 3.1.2 e 3.1.3)"
echo ""
echo "Log saved: $LOG_FILE"
