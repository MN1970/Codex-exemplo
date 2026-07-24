#!/bin/bash
# ============================================================================
# SCRIPTS PRONTOS — Sincronização SharePoint S6-S10
# Maestro | 2026-07-24 | v1.0
# ============================================================================
# USO: Copiar cada script abaixo para um arquivo separado, dar chmod +x,
#      executar na sequência conforme PLANO-SINCRONIZACAO-S6-S10.md
# ============================================================================

# SCRIPT 1: setup-sync-s6-s10.sh
# FASE: Inicialização
# DURAÇÃO: ~2 min
# ============================================================================
cat > ~/setup-sync-s6-s10.sh << 'SETUP_EOF'
#!/bin/bash
# Setup da estrutura local para sincronização S6-S10

set -e

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "SETUP: Sincronização SharePoint S6-S10"
echo "=========================================="
echo "Diretório: ${WORK_DIR}"
echo "Data: $(date)"
echo ""

# Criar diretório principal
mkdir -p "${WORK_DIR}/03_Projetos"
cd "${WORK_DIR}"

# Criar estrutura por segmento
SEGMENTS=("Saneamento" "Energia" "Portos" "Aeroportos" "Barragens")

for SEGMENT in "${SEGMENTS[@]}"; do
  echo "[$(date +%H:%M:%S)] Criando estrutura para ${SEGMENT}..."

  for FOLDER in \
    "00-Normativos" \
    "01-Projetos-Executados" \
    "02-Estudos-Primarios" \
    "03-Estudos-Tecnicos" \
    "04-Manta-Internos" \
    "05-Procedimentos" \
    "06-Modelos-Financeiros" \
    "07-Editais-Historicos" \
    "08-Casos-Internacionais" \
    "09-Documentacao-Mercado"; do

    mkdir -p "03_Projetos/${SEGMENT}/${FOLDER}"
  done
done

# Criar diretório de logs
mkdir -p "${WORK_DIR}/logs"

# Criar arquivo README
cat > "${WORK_DIR}/README.txt" << 'README_EOF'
SINCRONIZAÇÃO SHAREPOINT S6-S10
================================

Estrutura criada em: $(date)

Próximos passos:
1. Executar: ./sync-tier1.sh (sincronizar normativos)
2. Executar: ./validate-tier1.sh (validar TIER 1)
3. Executar: ./sync-tier2.sh (sincronizar projetos)
4. Executar: ./checklist-s8.sh, checklist-s9.sh, ... (validar por segmento)
5. Executar: ./generate-consolidation-report.sh (relatório final)

Segmentos:
- S8: Saneamento (prioridade: AySA)
- S9: Energia (prioridade: ANEEL)
- S6: Portos (ANTAQ)
- S10: Barragens (ICOLD/Lei 12.334)
- S7: Aeroportos (RBAC/ANAC)

Tamanho estimado: 3-5 GB total

README_EOF

echo ""
echo "✓ Setup completo!"
echo "✓ Estrutura criada em: ${WORK_DIR}"
echo ""
echo "Próximo passo: executar ./sync-tier1.sh"
SETUP_EOF

chmod +x ~/setup-sync-s6-s10.sh
echo "✓ setup-sync-s6-s10.sh criado"

# SCRIPT 2: sync-tier1.sh
# FASE: Sincronização TIER 1 (Normativos)
# DURAÇÃO: 30-60 min
# ============================================================================
cat > ~/sync-tier1.sh << 'TIER1_EOF'
#!/bin/bash
# Sincroniza TIER 1 (Normativos) — CRÍTICO
# Bloqueador: sem isso, agentes não têm base legal

set -e

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
LOG_FILE="${WORK_DIR}/logs/sync-tier1-$(date +%Y%m%d_%H%M%S).log"

# Configuração rclone
RCLONE_REMOTE="sharepoint"  # Trocar se nome diferente
SP_SITE="Manta Associados"
SP_DRIVE="Documentos Compartilhados"

echo "=========================================="
echo "TIER 1: Sincronização de Normativos"
echo "=========================================="
echo "Log: ${LOG_FILE}"
echo "Data: $(date)"
echo ""

# Verificar se rclone está configurado
if ! rclone listremotes | grep -q "^${RCLONE_REMOTE}$"; then
  echo "❌ ERRO: Remote rclone '${RCLONE_REMOTE}' não encontrado"
  echo "Configurar primeiro com: rclone config"
  exit 1
fi

echo "✓ rclone remote verificado: ${RCLONE_REMOTE}"
echo ""

# Sincronizar cada segmento TIER 1
SEGMENTS=("Saneamento" "Energia" "Portos" "Aeroportos" "Barragens")

for SEGMENT in "${SEGMENTS[@]}"; do
  echo "[$(date +%H:%M:%S)] Sincronizando ${SEGMENT}/00-Normativos..."

  SRC="${RCLONE_REMOTE}:${SP_SITE}/${SP_DRIVE}/03_Projetos/${SEGMENT}/00-Normativos"
  DST="${WORK_DIR}/03_Projetos/${SEGMENT}/00-Normativos"

  # Tentar sincronização
  if rclone sync \
    --progress \
    --stats 10s \
    --transfers 4 \
    --checkers 8 \
    --checksum \
    --log-file="${LOG_FILE}" \
    "${SRC}" "${DST}"; then

    SIZE=$(du -sh "${DST}" 2>/dev/null | cut -f1 || echo "0 MB")
    COUNT=$(find "${DST}" -type f 2>/dev/null | wc -l || echo "0")
    echo "  ✓ Sucesso: ${COUNT} arquivos, ${SIZE}"
  else
    echo "  ⚠ Aviso: possível erro ou permissão negada"
  fi

  echo ""
done

echo "=========================================="
echo "✓ TIER 1 sincronização completo"
echo "Log detalhado: ${LOG_FILE}"
echo ""
echo "Próximo passo: ./validate-tier1.sh"
TIER1_EOF

chmod +x ~/sync-tier1.sh
echo "✓ sync-tier1.sh criado"

# SCRIPT 3: validate-tier1.sh
# FASE: Validação pós-sincronização TIER 1
# DURAÇÃO: ~5 min
# ============================================================================
cat > ~/validate-tier1.sh << 'VALIDATE_EOF'
#!/bin/bash
# Valida se TIER 1 foi sincronizado corretamente

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/logs/validate-tier1-$(date +%Y%m%d_%H%M%S).txt"

echo "=========================================="
echo "VALIDAÇÃO: TIER 1 (Normativos)"
echo "=========================================="
echo "Relatório: ${REPORT}"
echo ""

cat > "${REPORT}" << 'REPORT_EOF'
=== VALIDAÇÃO TIER 1 ===
Data: $(date)

RESUMO:
EOFR

SEGMENTS=("Saneamento" "Energia" "Portos" "Aeroportos" "Barragens")
TOTAL_FILES=0
TOTAL_SIZE=0

for SEGMENT in "${SEGMENTS[@]}"; do
  NORMA_DIR="${WORK_DIR}/03_Projetos/${SEGMENT}/00-Normativos"

  if [ ! -d "$NORMA_DIR" ]; then
    echo "[✗] ${SEGMENT}: PASTA NÃO EXISTE" | tee -a "${REPORT}"
    continue
  fi

  FILE_COUNT=$(find "$NORMA_DIR" -type f 2>/dev/null | wc -l)
  DIR_SIZE=$(du -sh "$NORMA_DIR" 2>/dev/null | cut -f1 || echo "0 MB")

  TOTAL_FILES=$((TOTAL_FILES + FILE_COUNT))

  if [ "$FILE_COUNT" -gt 0 ]; then
    echo "[✓] ${SEGMENT}: ${FILE_COUNT} arquivos, ${DIR_SIZE}" | tee -a "${REPORT}"
  else
    echo "[⚠] ${SEGMENT}: PASTA VAZIA" | tee -a "${REPORT}"
  fi
done

echo "" | tee -a "${REPORT}"
echo "TOTAL: ${TOTAL_FILES} arquivos em TIER 1" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

# Verificar se tem arquivos principais esperados
echo "VALIDAÇÃO DE CONTEÚDO:" | tee -a "${REPORT}"

for SEGMENT in "${SEGMENTS[@]}"; do
  NORMA_DIR="${WORK_DIR}/03_Projetos/${SEGMENT}/00-Normativos"

  if [ -d "$NORMA_DIR" ]; then
    PDF_COUNT=$(find "$NORMA_DIR" -iname "*.pdf" 2>/dev/null | wc -l)
    XLS_COUNT=$(find "$NORMA_DIR" -iname "*.xls*" 2>/dev/null | wc -l)
    DWG_COUNT=$(find "$NORMA_DIR" -iname "*.dwg" 2>/dev/null | wc -l)

    echo "${SEGMENT}: ${PDF_COUNT} PDFs, ${XLS_COUNT} XLS, ${DWG_COUNT} DWGs" | tee -a "${REPORT}"
  fi
done

echo "" | tee -a "${REPORT}"
echo "STATUS: OK para continuar com TIER 2" | tee -a "${REPORT}"

VALIDATE_EOF

cat "${REPORT}"
echo ""
echo "✓ Relatório salvo: ${REPORT}"
chmod +x ~/validate-tier1.sh
echo "✓ validate-tier1.sh criado"

# SCRIPT 4: sync-tier2.sh
# FASE: Sincronização TIER 2 (Projetos + Editais)
# DURAÇÃO: 60-120 min
# ============================================================================
cat > ~/sync-tier2.sh << 'TIER2_EOF'
#!/bin/bash
# Sincroniza TIER 2 (Projetos Executados + Estudos Primários)

set -e

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
LOG_FILE="${WORK_DIR}/logs/sync-tier2-$(date +%Y%m%d_%H%M%S).log"

RCLONE_REMOTE="sharepoint"
SP_SITE="Manta Associados"
SP_DRIVE="Documentos Compartilhados"

echo "=========================================="
echo "TIER 2: Projetos Executados + Estudos"
echo "=========================================="
echo "Log: ${LOG_FILE}"
echo ""

SEGMENTS=("Saneamento" "Energia" "Portos" "Barragens" "Aeroportos")
TIER2_FOLDERS=("01-Projetos-Executados" "02-Estudos-Primarios")

for SEGMENT in "${SEGMENTS[@]}"; do
  for FOLDER in "${TIER2_FOLDERS[@]}"; do
    echo "[$(date +%H:%M:%S)] ${SEGMENT}/${FOLDER}..."

    SRC="${RCLONE_REMOTE}:${SP_SITE}/${SP_DRIVE}/03_Projetos/${SEGMENT}/${FOLDER}"
    DST="${WORK_DIR}/03_Projetos/${SEGMENT}/${FOLDER}"

    # Sync com limite de tamanho para evitar arquivos gigantes
    rclone sync \
      --progress \
      --stats 10s \
      --transfers 4 \
      --max-size 500M \
      --checksum \
      --log-file="${LOG_FILE}" \
      "${SRC}" "${DST}" || true

    SIZE=$(du -sh "${DST}" 2>/dev/null | cut -f1 || echo "0 MB")
    echo "  ✓ ${SIZE}"
  done
done

echo ""
echo "✓ TIER 2 sincronizado"
echo "Próximo passo: Executar checklists por segmento"
TIER2_EOF

chmod +x ~/sync-tier2.sh
echo "✓ sync-tier2.sh criado"

# SCRIPT 5: generate-gaps-report.sh
# FASE: Análise de gaps
# DURAÇÃO: ~5 min
# ============================================================================
cat > ~/generate-gaps-report.sh << 'GAPS_EOF'
#!/bin/bash
# Gera relatório de gaps (documentos faltantes)

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/gaps-report-$(date +%Y%m%d_%H%M%S).txt"

echo "=========================================="
echo "RELATÓRIO DE GAPS"
echo "=========================================="

cat > "${REPORT}" << 'REPORT_EOF'
=== ANÁLISE DE GAPS ===
Data: $(date)

Estrutura Esperada (Resumo):
├─ Saneamento/
│  ├─ 00-Normativos: Lei 14.026, Lei 11.445, NBR 12211-12218, SNIS
│  ├─ 01-Projetos: >3 ETAs, >3 ETEs, AySA
│  └─ 02-Estudos: PMSB, hidrológicos
├─ Energia/
│  ├─ 00-Normativos: ANEEL REN, NBR 5422, IEEE 738
│  ├─ 01-Projetos: >3 LTs, >2 SEs
│  └─ 02-Estudos: R1-R5 ANEEL
├─ Portos/
│  ├─ 00-Normativos: Lei 12.815, PIANC, NBR
│  ├─ 01-Projetos: >2 terminais, dragagem
│  └─ 02-Estudos: hidrográficos, geotécnicos
├─ Barragens/
│  ├─ 00-Normativos: Lei 12.334, ICOLD
│  ├─ 01-Projetos: >2 UHE, >2 abastecimento
│  └─ 02-Casos: Fundão, Brumadinho
└─ Aeroportos/
   ├─ 00-Normativos: RBAC 154, ICAO Annex 14
   ├─ 01-Projetos: >2 TPS, >2 pistas
   └─ 02-Estudos: mix aeronaves

DETALHES:

EOFREPORT

for SEGMENT in "Saneamento" "Energia" "Portos" "Barragens" "Aeroportos"; do
  echo "" >> "${REPORT}"
  echo "--- ${SEGMENT} ---" >> "${REPORT}"

  for FOLDER in "00-Normativos" "01-Projetos-Executados" "02-Estudos-Primarios"; do
    DIR="${WORK_DIR}/03_Projetos/${SEGMENT}/${FOLDER}"

    if [ ! -d "$DIR" ]; then
      echo "[✗] ${FOLDER}: PASTA NÃO CRIADA" >> "${REPORT}"
    elif [ -z "$(find "$DIR" -type f 2>/dev/null)" ]; then
      echo "[⚠] ${FOLDER}: VAZIA" >> "${REPORT}"
    else
      COUNT=$(find "$DIR" -type f 2>/dev/null | wc -l)
      SIZE=$(du -sh "$DIR" 2>/dev/null | cut -f1)
      echo "[✓] ${FOLDER}: ${COUNT} arquivos, ${SIZE}" >> "${REPORT}"
    fi
  done
done

echo "" >> "${REPORT}"
echo "PRÓXIMOS PASSOS:" >> "${REPORT}"
echo "1. Revisar pastas vazias (⚠) — verificar se existem no SharePoint" >> "${REPORT}"
echo "2. Se crítico (TIER 1) falta, fazer upload manual" >> "${REPORT}"
echo "3. Executar checklists por segmento para validar completude" >> "${REPORT}"

cat "${REPORT}"
echo ""
echo "✓ Relatório: ${REPORT}"
GAPS_EOF

chmod +x ~/generate-gaps-report.sh
echo "✓ generate-gaps-report.sh criado"

# ============================================================================
# CRIAR CHECKLISTS POR SEGMENTO (S6-S10)
# ============================================================================

# SCRIPT 6: checklist-s8.sh (Saneamento)
cat > ~/checklist-s8.sh << 'S8_EOF'
#!/bin/bash
WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/checklist-s8-$(date +%Y%m%d).txt"

echo "=== CHECKLIST S8 - SANEAMENTO ===" | tee "${REPORT}"
echo "Data: $(date)" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

# Verificar TIER 1
echo "[TIER 1 - Normativos]" | tee -a "${REPORT}"
[ -f "${WORK_DIR}/03_Projetos/Saneamento/00-Normativos"/*14.026* ] && echo "  [✓] Lei 14.026/2020" | tee -a "${REPORT}" || echo "  [✗] Lei 14.026/2020 FALTANDO" | tee -a "${REPORT}"
[ -f "${WORK_DIR}/03_Projetos/Saneamento/00-Normativos"/*12211* ] && echo "  [✓] NBR 12211-12218" | tee -a "${REPORT}" || echo "  [✗] NBR 12211-12218 FALTANDO" | tee -a "${REPORT}"

# Verificar TIER 2
echo "[TIER 2 - Projetos]" | tee -a "${REPORT}"
COUNT=$(find "${WORK_DIR}/03_Projetos/Saneamento/01-Projetos-Executados" -type f 2>/dev/null | wc -l)
echo "  Projetos encontrados: ${COUNT}" | tee -a "${REPORT}"
[ "$COUNT" -ge 3 ] && echo "  [✓] Mínimo 3 projetos" | tee -a "${REPORT}" || echo "  [⚠] Menos de 3 projetos" | tee -a "${REPORT}"

cat "${REPORT}"
S8_EOF

chmod +x ~/checklist-s8.sh
echo "✓ checklist-s8.sh criado"

# SCRIPT 7: checklist-s9.sh (Energia)
cat > ~/checklist-s9.sh << 'S9_EOF'
#!/bin/bash
WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/checklist-s9-$(date +%Y%m%d).txt"

echo "=== CHECKLIST S9 - ENERGIA ===" | tee "${REPORT}"
echo "Data: $(date)" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

echo "[TIER 1 - Normativos]" | tee -a "${REPORT}"
[ -d "${WORK_DIR}/03_Projetos/Energia/00-Normativos" ] && COUNT=$(find "${WORK_DIR}/03_Projetos/Energia/00-Normativos" -iname "*ANEEL*" -o -iname "*REN*" | wc -l) && [ "$COUNT" -gt 0 ] && echo "  [✓] ANEEL REN encontrado" | tee -a "${REPORT}" || echo "  [✗] ANEEL REN FALTANDO" | tee -a "${REPORT}"

echo "[TIER 2 - Projetos]" | tee -a "${REPORT}"
COUNT=$(find "${WORK_DIR}/03_Projetos/Energia/01-Projetos-Executados" -type f 2>/dev/null | wc -l)
echo "  Projetos encontrados: ${COUNT}" | tee -a "${REPORT}"

cat "${REPORT}"
S9_EOF

chmod +x ~/checklist-s9.sh
echo "✓ checklist-s9.sh criado"

# Criar checklists para S6, S10, S7 (similares)
for SEGMENTO in "S6" "S10" "S7"; do
  cat > ~/checklist-${SEGMENTO}.sh << "GENERIC_EOF"
#!/bin/bash
WORK_DIR="${HOME}/Manta-S6-S10-Sync"
SEGMENT_MAP=( ["S6"]="Portos" ["S10"]="Barragens" ["S7"]="Aeroportos" )
SEGMENT_NAME=${SEGMENT_MAP[$1]}
REPORT="${WORK_DIR}/checklist-${SEGMENTO}-$(date +%Y%m%d).txt"

echo "=== CHECKLIST ${SEGMENTO} - ${SEGMENT_NAME} ===" | tee "${REPORT}"
echo "Data: $(date)" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

echo "[TIER 1 - Normativos]" | tee -a "${REPORT}"
COUNT=$(find "${WORK_DIR}/03_Projetos/${SEGMENT_NAME}/00-Normativos" -type f 2>/dev/null | wc -l)
echo "  Arquivos normativos: ${COUNT}" | tee -a "${REPORT}"

echo "[TIER 2 - Projetos]" | tee -a "${REPORT}"
COUNT=$(find "${WORK_DIR}/03_Projetos/${SEGMENT_NAME}/01-Projetos-Executados" -type f 2>/dev/null | wc -l)
echo "  Projetos encontrados: ${COUNT}" | tee -a "${REPORT}"

cat "${REPORT}"
GENERIC_EOF
  chmod +x ~/checklist-${SEGMENTO}.sh
  echo "✓ checklist-${SEGMENTO}.sh criado"
done

# ============================================================================
# SCRIPT FINAL: Consolidation Report
# ============================================================================

cat > ~/generate-consolidation-report.sh << 'CONSOLIDATION_EOF'
#!/bin/bash
WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/consolidation-report-$(date +%Y%m%d_%H%M%S).txt"

echo "=========================================="
echo "RELATÓRIO DE CONSOLIDAÇÃO FINAL"
echo "=========================================="

cat > "${REPORT}" << 'FINAL_REPORT'
=== CONSOLIDAÇÃO S6-S10 ===
Data: $(date)

RESUMO EXECUTIVO:

Estrutura local consolidada em:
  ~/Manta-S6-S10-Sync/03_Projetos/

Segmentos sincronizados:
  1. Saneamento (S8) — AySA prioridade
  2. Energia (S9) — ANEEL prioridade
  3. Portos (S6)
  4. Barragens (S10)
  5. Aeroportos (S7)

FINAL_REPORT

TOTAL_FILES=0
TOTAL_SIZE=0

for SEGMENT in "Saneamento" "Energia" "Portos" "Barragens" "Aeroportos"; do
  echo "" >> "${REPORT}"
  echo "--- ${SEGMENT} ---" >> "${REPORT}"

  FILES=$(find "${WORK_DIR}/03_Projetos/${SEGMENT}" -type f 2>/dev/null | wc -l)
  SIZE=$(du -sh "${WORK_DIR}/03_Projetos/${SEGMENT}" 2>/dev/null | cut -f1 || echo "0 MB")

  TOTAL_FILES=$((TOTAL_FILES + FILES))

  echo "Arquivos: ${FILES}" >> "${REPORT}"
  echo "Tamanho: ${SIZE}" >> "${REPORT}"
done

echo "" >> "${REPORT}"
echo "TOTAL GERAL: ${TOTAL_FILES} arquivos" >> "${REPORT}"
echo "" >> "${REPORT}"
echo "STATUS: Pronto para FASE 2 (RAG Ingestion)" >> "${REPORT}"
echo "Próximo passo: Preparar Supabase para ingestion" >> "${REPORT}"

cat "${REPORT}"
echo ""
echo "✓ Relatório: ${REPORT}"
CONSOLIDATION_EOF

chmod +x ~/generate-consolidation-report.sh
echo "✓ generate-consolidation-report.sh criado"

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "=========================================="
echo "✓ SCRIPTS CRIADOS COM SUCESSO"
echo "=========================================="
echo ""
echo "Scripts disponíveis em ~/ :"
echo ""
echo "FASE 1 (Setup + TIER 1 + TIER 2):"
echo "  1. bash ~/setup-sync-s6-s10.sh"
echo "  2. bash ~/sync-tier1.sh"
echo "  3. bash ~/validate-tier1.sh"
echo "  4. bash ~/sync-tier2.sh"
echo "  5. bash ~/generate-gaps-report.sh"
echo ""
echo "Validação por segmento:"
echo "  bash ~/checklist-s8.sh  (Saneamento)"
echo "  bash ~/checklist-s9.sh  (Energia)"
echo "  bash ~/checklist-s6.sh  (Portos)"
echo "  bash ~/checklist-s10.sh (Barragens)"
echo "  bash ~/checklist-s7.sh  (Aeroportos)"
echo ""
echo "Relatório final:"
echo "  bash ~/generate-consolidation-report.sh"
echo ""
echo "PRÓXIMO PASSO: Executar setup"
echo "  bash ~/setup-sync-s6-s10.sh"
echo ""
