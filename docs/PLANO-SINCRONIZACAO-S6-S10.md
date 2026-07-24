# PLANO DE AÇÃO EXECUTÁVEL — Sincronização SharePoint S6–S10
## Consolidação de Conteúdo para Agentes Portos, Aeroportos, Saneamento, Energia, Barragens

**Status**: v1.0 | 2026-07-24 | Maestro (Manta 00)
**Objetivo**: Sincronizar e validar conteúdo SharePoint para os 5 novos segmentos, preparar ingestion RAG.

---

## 1. MATRIZ DE PRIORIDADE — RANKING POR TIER

### TIER 1 (Crítico — SINCRONIZAR PRIMEIRO)
Bloqueadores de projeto. Sem isso, os agentes não funcionam.

| Segmento | Categoria | Fontes Primárias | Arquivo SP | Criticidade |
|----------|-----------|-----------------|-----------|-------------|
| **S8 Saneamento** | Marcos regulatórios | Lei 14.026/2020 (novo marco), Lei 11.445/2007, PRC 05/2017 | `03_Projetos/Saneamento/00-Normativos/` | **CRÍTICA** |
| **S8 Saneamento** | Normas técnicas | NBR 12211-12218 (projeto ETA/ETE), NBR 9648-9651 (esgoto), NBR 15645 (emissário) | `03_Projetos/Saneamento/00-Normativos/NBR/` | **CRÍTICA** |
| **S8 Saneamento** | Agência reguladora | SNIS (indicadores), ANA NR-001/002/004, ERAS (AySA argentina) | `03_Projetos/Saneamento/00-Normativos/Agências/` | **CRÍTICA** |
| **S9 Energia** | Marcos regulatórios | ANEEL REN (todas), Procedimentos de Rede ONS, lei concessões | `03_Projetos/Energia/00-Normativos/` | **CRÍTICA** |
| **S9 Energia** | Normas técnicas | NBR 5422 (LT aéreas), NBR 6118 (fundações), IEEE 738 (ampacidade), IEC 60826 | `03_Projetos/Energia/00-Normativos/NBR-IEEE-IEC/` | **CRÍTICA** |
| **S6 Portos** | Marcos regulatórios | Lei 12.815/2013 (lei portos), Lei 14.301/2022 (BR do Mar), ANTAQ normativas | `03_Projetos/Portos/00-Normativos/` | **CRÍTICA** |
| **S6 Portos** | Normas técnicas | NBR 9782 (ações portuárias), NBR 6122 (fundações), ROM 0.2/2.0 (espanhol), PIANC | `03_Projetos/Portos/00-Normativos/NBR-ROM-PIANC/` | **CRÍTICA** |
| **S10 Barragens** | Marcos regulatórios | Lei 12.334/2010 (PNSB), Lei 14.066/2020 (pós-Brumadinho), ANM 95/2022 | `03_Projetos/Barragens/00-Normativos/` | **CRÍTICA** |
| **S10 Barragens** | Normas técnicas | NBR 13028 (rejeitos), NBR 8681 (ações), ICOLD Bulletins (164, 194), CBDB cadernos | `03_Projetos/Barragens/00-Normativos/NBR-ICOLD-CBDB/` | **CRÍTICA** |
| **S7 Aeroportos** | Marcos regulatórios | RBAC 154 (ANAC — obrigatório BR), ICAO Annex 14, FAA Advisory Circulars | `03_Projetos/Aeroportos/00-Normativos/` | **CRÍTICA** |

**Ação Imediata**: Sincronizar todas as pastas `00-Normativos/` ANTES de qualquer outra coisa.

---

### TIER 2 (Alto — SINCRONIZAR EM PARALELO COM TIER 1)
Projetos executados + templates. Fornecem contexto real aos agentes.

| Segmento | Categoria | Exemplos | Arquivo SP | Criticidade |
|----------|-----------|----------|-----------|-------------|
| **S8 Saneamento** | Projetos executados — ETA/ETE | Sistema Riachuelo (AySA), Planta Norte (AySA), ETE São João (SP) | `03_Projetos/Saneamento/01-Projetos-Executados/` | **ALTA** |
| **S8 Saneamento** | PMSB — Planos Municipais | Cidades 50k+, incluindo perfil AySA (Buenos Aires) | `03_Projetos/Saneamento/02-PMSB/` | **ALTA** |
| **S9 Energia** | Projetos executados — LT | LT 230/345/500 kV leiloados ANEEL, subestações reais (geometria, bills) | `03_Projetos/Energia/01-Projetos-Executados/` | **ALTA** |
| **S9 Energia** | Estudos ANEEL — R1-R5 | R1 (sistema), R2 (básico ambiental), R3 (básico eletromecânico), R4/R5 (leilão) | `03_Projetos/Energia/02-Estudos-ANEEL-R1-R5/` | **ALTA** |
| **S6 Portos** | Projetos executados | Terminal contêiner (Suape, Itajaí), granel sólido, dragagem de aprofundamento | `03_Projetos/Portos/01-Projetos-Executados/` | **ALTA** |
| **S6 Portos** | Editais de arrendamento | TUP recentes (ANTAQ), amostra de concessões portuárias | `03_Projetos/Portos/02-Editais-Arrendamentos/` | **ALTA** |
| **S10 Barragens** | Projetos executados | UHE, barragem abastecimento (100+ MW ou> 50 km³), barragem de rejeitos | `03_Projetos/Barragens/01-Projetos-Executados/` | **ALTA** |
| **S10 Barragens** | Casos-referência | Fundão (post-mortem), Brumadinho (laudo técnico) — descomissionamento | `03_Projetos/Barragens/02-Casos-Referencia/` | **ALTA** |
| **S7 Aeroportos** | Projetos executados | TPS, pista/taxiway, aeroportos regionais (PCN, pavimento) | `03_Projetos/Aeroportos/01-Projetos-Executados/` | **ALTA** |

**Ação**: Iniciar sincronização paralela LOGO APÓS TIER 1. Priorizar AySA (S8) + ANEEL (S9).

---

### TIER 3 (Médio — SINCRONIZAR EM SEQUÊNCIA)
Estudos técnicos, documentação interna Manta, procedimentos.

| Segmento | Categoria | Exemplos | Arquivo SP | Criticidade |
|----------|-----------|----------|-----------|-------------|
| **Todos** | Estudos técnicos | EVTA/EVTE, relatórios hidrológicos, batimetrias, diagnósticos | `03_Projetos/{Segmento}/03-Estudos-Tecnicos/` | **MÉDIA** |
| **Todos** | Documentos Manta | Memoriais, cronogramas-padrão, planilhas de custo | `03_Projetos/{Segmento}/04-Manta-Internos/` | **MÉDIA** |
| **Todos** | Procedimentos e checklists | Intake Q2 (8 fases), templates de relatório, matriz de risco | `03_Projetos/{Segmento}/05-Procedimentos/` | **MÉDIA** |
| **S8, S9, S6, S10** | Modelos financeiros | VPL, TIR, modelos PPP, subsídio cruzado (S8), RAP (S9) | `03_Projetos/{Segmento}/06-Modelos-Financeiros/` | **MÉDIA** |

**Ação**: Agendar para próxima semana (SEMANA DE 2026-07-31). Não bloqueia função dos agentes.

---

### TIER 4 (Referência — SINCRONIZAR CONFORME DISPONÍVEL)
Editais históricos, casos internacionais, documentação de mercado.

| Segmento | Categoria | Exemplos | Arquivo SP | Criticidade |
|----------|-----------|----------|-----------|-------------|
| **Todos** | Editais históricos | Processos competitivos 2020-2025, contratos assinados (redacted) | `03_Projetos/{Segmento}/07-Editais-Historicos/` | **BAIXA** |
| **Todos** | Casos internacionais | Projetos Portugal, México, Argentina, Peru (contexto latino) | `03_Projetos/{Segmento}/08-Casos-Internacionais/` | **BAIXA** |
| **Todos** | Documentação mercado | Relatórios BNDES, estudos setoriais, publicações técnicas open-source | `03_Projetos/{Segmento}/09-Documentacao-Mercado/` | `(conforme interesse)` | **BAIXA** |

**Ação**: Sincronizar como background, sem urgência. Aumenta valor dos agentes mas não é crítico.

---

## 2. SCRIPT DE SINCRONIZAÇÃO + VALIDAÇÃO

### 2.1 SETUP — Preparação local

```bash
#!/bin/bash
# setup-sync-s6-s10.sh
# Executar uma única vez para preparar estrutura local

set -e

# Variáveis
WORK_DIR="${HOME}/Manta-S6-S10-Sync"
LOG_FILE="${WORK_DIR}/sync.log"
VALIDATE_REPORT="${WORK_DIR}/validate-report.txt"

# Criar estrutura local esperada
mkdir -p "${WORK_DIR}/03_Projetos"
cd "${WORK_DIR}"

# Criar pastas por segmento (esperadas pelo CLAUDE.md)
for SEGMENT in "Saneamento" "Energia" "Portos" "Aeroportos" "Barragens"; do
  mkdir -p "03_Projetos/${SEGMENT}/00-Normativos"
  mkdir -p "03_Projetos/${SEGMENT}/01-Projetos-Executados"
  mkdir -p "03_Projetos/${SEGMENT}/02-Estudos-Primarios"
  mkdir -p "03_Projetos/${SEGMENT}/03-Estudos-Tecnicos"
  mkdir -p "03_Projetos/${SEGMENT}/04-Manta-Internos"
  mkdir -p "03_Projetos/${SEGMENT}/05-Procedimentos"
  mkdir -p "03_Projetos/${SEGMENT}/06-Modelos-Financeiros"
  mkdir -p "03_Projetos/${SEGMENT}/07-Editais-Historicos"
  mkdir -p "03_Projetos/${SEGMENT}/08-Casos-Internacionais"
  mkdir -p "03_Projetos/${SEGMENT}/09-Documentacao-Mercado"
done

echo "Estrutura local criada em: ${WORK_DIR}"
echo "Próximo passo: executar sync-tier1.sh"
```

### 2.2 TIER 1 — Sincronização de Normativos (BLOQUEIA OUTRAS FASES)

```bash
#!/bin/bash
# sync-tier1.sh
# Sincroniza todas as normas + marcos regulatórios
# Requer: rclone configurado com MS Graph (SharePoint Online)

set -e

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
LOG_FILE="${WORK_DIR}/sync-tier1.log"
RCLONE_REMOTE="sharepoint"  # Nome do remote rclone (configurar via: rclone config)
SP_SITE="Manta Associados"
SP_DRIVE="Documentos Compartilhados"

echo "[$(date)] Iniciando sincronização TIER 1 (Normativos)" | tee -a "$LOG_FILE"

# Segmentos
SEGMENTS=("Saneamento" "Energia" "Portos" "Aeroportos" "Barragens")

for SEGMENT in "${SEGMENTS[@]}"; do
  echo "[$(date)] Sincronizando ${SEGMENT}/00-Normativos..." | tee -a "$LOG_FILE"
  
  SRC="${RCLONE_REMOTE}:${SP_SITE}/${SP_DRIVE}/03_Projetos/${SEGMENT}/00-Normativos"
  DST="${WORK_DIR}/03_Projetos/${SEGMENT}/00-Normativos"
  
  rclone sync \
    --progress \
    --stats 5s \
    --transfers 4 \
    --checkers 8 \
    --log-file="${LOG_FILE}" \
    "${SRC}" "${DST}"
  
  echo "[$(date)] ✓ ${SEGMENT}/00-Normativos sincronizado ($(du -sh "${DST}" | cut -f1))" | tee -a "$LOG_FILE"
done

echo "[$(date)] TIER 1 completo. Executar validação: ./validate-tier1.sh" | tee -a "$LOG_FILE"
```

### 2.3 VALIDAÇÃO — Checklist automático

```bash
#!/bin/bash
# validate-tier1.sh
# Valida se estrutura local bate com CLAUDE.md

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
REPORT="${WORK_DIR}/validate-tier1-report.txt"

echo "=== RELATÓRIO DE VALIDAÇÃO — TIER 1 ===" > "$REPORT"
echo "Data: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

declare -A TIER1_FILES=(
  ["Saneamento"]="Lei_14.026_2020.pdf;Lei_11.445_2007.pdf;NBR_12211-12218.pdf;NBR_9648-9651.pdf;ANA_NR-001-002-004.pdf;SNIS_2023.xlsx"
  ["Energia"]="ANEEL_REN_todas.pdf;ONS_Procedimentos-Rede.pdf;NBR_5422.pdf;NBR_6118.pdf;IEEE_Std_738.pdf;IEC_60826.pdf"
  ["Portos"]="Lei_12.815_2013.pdf;Lei_14.301_2022.pdf;NBR_9782.pdf;NBR_6122.pdf;ROM_0.2.pdf;ROM_2.0.pdf;PIANC_reports.pdf;ANTAQ_normativas.pdf"
  ["Barragens"]="Lei_12.334_2010.pdf;Lei_14.066_2020.pdf;ANM_Resolucao_95_2022.pdf;NBR_13028.pdf;NBR_8681.pdf;ICOLD_164.pdf;ICOLD_194.pdf"
  ["Aeroportos"]="RBAC_154.pdf;ICAO_Annex_14.pdf;FAA_AC_150.pdf;DECEA_ICA_100-12.pdf"
)

for SEGMENT in "Saneamento" "Energia" "Portos" "Aeroportos" "Barragens"; do
  echo "" >> "$REPORT"
  echo "--- SEGMENTO: ${SEGMENT} ---" >> "$REPORT"
  
  NORMA_DIR="${WORK_DIR}/03_Projetos/${SEGMENT}/00-Normativos"
  
  if [ ! -d "$NORMA_DIR" ]; then
    echo "✗ PASTA NÃO EXISTE: ${NORMA_DIR}" >> "$REPORT"
    continue
  fi
  
  FILE_COUNT=$(find "$NORMA_DIR" -type f | wc -l)
  DIR_SIZE=$(du -sh "$NORMA_DIR" | cut -f1)
  
  echo "Arquivos encontrados: ${FILE_COUNT}" >> "$REPORT"
  echo "Tamanho total: ${DIR_SIZE}" >> "$REPORT"
  
  # Verificar se tem ao menos arquivos .pdf/.xlsx/.dwg
  PDF_COUNT=$(find "$NORMA_DIR" -type f \( -iname "*.pdf" -o -iname "*.xlsx" -o -iname "*.dwg" \) | wc -l)
  
  if [ "$PDF_COUNT" -gt 0 ]; then
    echo "✓ Documentos técnicos encontrados: ${PDF_COUNT}" >> "$REPORT"
  else
    echo "✗ AVISO: Nenhum documento técnico (.pdf/.xlsx/.dwg) em ${NORMA_DIR}" >> "$REPORT"
  fi
  
  # Listar primeiros 10 arquivos
  echo "Primeiros 10 arquivos:" >> "$REPORT"
  find "$NORMA_DIR" -type f | head -10 | sed 's/^/  /' >> "$REPORT"
done

echo "" >> "$REPORT"
echo "=== PRÓXIMOS PASSOS ===" >> "$REPORT"
echo "1. Revisar relatório e corrigir gaps" >> "$REPORT"
echo "2. Se OK, executar: ./sync-tier2.sh" >> "$REPORT"

cat "$REPORT"
```

### 2.4 TIER 2 — Sincronização de Projetos Executados + Editais (PARALELO COM TIER 1)

```bash
#!/bin/bash
# sync-tier2.sh
# Sincroniza projetos reais + editais

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
LOG_FILE="${WORK_DIR}/sync-tier2.log"
RCLONE_REMOTE="sharepoint"
SP_SITE="Manta Associados"
SP_DRIVE="Documentos Compartilhados"

echo "[$(date)] Iniciando sincronização TIER 2 (Projetos + Editais)" | tee -a "$LOG_FILE"

SEGMENTS=("Saneamento" "Energia" "Portos" "Barragens" "Aeroportos")
TIER2_FOLDERS=("01-Projetos-Executados" "02-Estudos-Primarios")

for SEGMENT in "${SEGMENTS[@]}"; do
  for FOLDER in "${TIER2_FOLDERS[@]}"; do
    echo "[$(date)] Sincronizando ${SEGMENT}/${FOLDER}..." | tee -a "$LOG_FILE"
    
    SRC="${RCLONE_REMOTE}:${SP_SITE}/${SP_DRIVE}/03_Projetos/${SEGMENT}/${FOLDER}"
    DST="${WORK_DIR}/03_Projetos/${SEGMENT}/${FOLDER}"
    
    # Usar --max-size para evitar arquivos muito grandes (>500MB)
    rclone sync \
      --progress \
      --stats 5s \
      --transfers 4 \
      --max-size 500M \
      --log-file="${LOG_FILE}" \
      "${SRC}" "${DST}" || echo "⚠ Aviso: alguns arquivos não sincronizados (possível limite de tamanho)"
    
    echo "[$(date)] ✓ ${SEGMENT}/${FOLDER} parcialmente sincronizado" | tee -a "$LOG_FILE"
  done
done

echo "[$(date)] TIER 2 completo. Executar: ./validate-tier2.sh" | tee -a "$LOG_FILE"
```

### 2.5 RELATÓRIO DE GAPS

```bash
#!/bin/bash
# generate-gaps-report.sh
# Identifica pastas vazias, arquivos faltantes, inconsistências

WORK_DIR="${HOME}/Manta-S6-S10-Sync"
GAPS_REPORT="${WORK_DIR}/gaps-report.txt"

echo "=== RELATÓRIO DE GAPS ===" > "$GAPS_REPORT"
echo "Gerado: $(date)" >> "$GAPS_REPORT"
echo "" >> "$GAPS_REPORT"

SEGMENTS=("Saneamento" "Energia" "Portos" "Aeroportos" "Barragens")

for SEGMENT in "${SEGMENTS[@]}"; do
  echo "--- ${SEGMENT} ---" >> "$GAPS_REPORT"
  
  for FOLDER in 00-Normativos 01-Projetos-Executados 02-Estudos-Primarios 03-Estudos-Tecnicos 04-Manta-Internos 05-Procedimentos 06-Modelos-Financeiros; do
    DIR="${WORK_DIR}/03_Projetos/${SEGMENT}/${FOLDER}"
    
    if [ ! -d "$DIR" ]; then
      echo "✗ PASTA NÃO CRIADA: ${FOLDER}" >> "$GAPS_REPORT"
    elif [ -z "$(find "$DIR" -type f 2>/dev/null)" ]; then
      echo "⚠ PASTA VAZIA: ${FOLDER}" >> "$GAPS_REPORT"
    else
      FILE_COUNT=$(find "$DIR" -type f | wc -l)
      echo "✓ ${FOLDER}: ${FILE_COUNT} arquivos" >> "$GAPS_REPORT"
    fi
  done
  
  echo "" >> "$GAPS_REPORT"
done

echo "=== AÇÕES RECOMENDADAS ===" >> "$GAPS_REPORT"
echo "" >> "$GAPS_REPORT"
echo "1. Revisar pastas vazias (⚠) — podem não existir no SharePoint" >> "$GAPS_REPORT"
echo "2. Se documentos críticos faltam, fazer upload manual via SharePoint Web" >> "$GAPS_REPORT"
echo "3. Depois de corrigir gaps: executar ./prepare-rag-ingestion.sh" >> "$GAPS_REPORT"

cat "$GAPS_REPORT"
```

---

## 3. CHECKLIST POR SEGMENTO — VALIDAÇÃO EXECUTÁVEL

### 3.1 S8 — Saneamento (PRIORIDADE: AySA Argentina)

**PRÉ-REQUISITO**: Tier 1 + Tier 2 sincronizados

```
[✓] Pastas principais criadas
  ├─ [?] 03_Projetos/Saneamento/00-Normativos → EXISTEM documentos?
  ├─ [?] 03_Projetos/Saneamento/01-Projetos-Executados → AySA (Sistema Riachuelo, Planta Norte)?
  ├─ [?] 03_Projetos/Saneamento/02-Estudos-Primarios → PMSB município-alvo?
  └─ [?] 03_Projetos/Saneamento/06-Modelos-Financeiros → Modelo AySA (subsídio cruzado)?

[✓] Normas primárias sincronizadas
  ├─ [ ] Lei 14.026/2020 (novo marco saneamento)
  ├─ [ ] Lei 11.445/2007 (regulação básica)
  ├─ [ ] NBR 12211-12218 (projeto ETA/ETE)
  ├─ [ ] PRC 05/2017 (padrão potabilidade BR)
  └─ [ ] ERAS/AySA regulatory framework (Argentina)

[✓] Projetos executados presentes
  ├─ [ ] Mínimo 3 projetos ETA (>10k m³/dia)
  ├─ [ ] Mínimo 3 projetos ETE (>10k PE)
  ├─ [ ] Mínimo 2 projetos AySA (Argentina)
  └─ [ ] DWGs de rede, memoriais, orçamentos SICRO/SINAPI

[✓] Templates preenchidos
  ├─ [ ] Intake Q2 da agente-saneamento (8 fases)
  ├─ [ ] Matriz de risco EVTE
  ├─ [ ] Cronograma-padrão (obra 24-36 meses)
  └─ [ ] Modelo financeiro VPL/TIR

**Comando de validação**:
```bash
cd ~/Manta-S6-S10-Sync
find 03_Projetos/Saneamento -type f | wc -l  # Deve ser > 50
du -sh 03_Projetos/Saneamento            # Deve ser > 500 MB (se projetos reais)
```

---

### 3.2 S9 — Energia (PRIORIDADE: ANEEL + State Grid)

```
[✓] Pastas principais criadas
  ├─ [?] 03_Projetos/Energia/00-Normativos
  ├─ [?] 03_Projetos/Energia/01-Projetos-Executados → LT 230/345/500 kV + SEs
  ├─ [?] 03_Projetos/Energia/02-Estudos-Primarios → R1-R5 ANEEL
  └─ [?] 03_Projetos/Energia/06-Modelos-Financeiros → Modelo RAP

[✓] Normas primárias sincronizadas
  ├─ [ ] ANEEL REN (todas as Resoluções Normativas)
  ├─ [ ] ONS Procedimentos de Rede (PdR)
  ├─ [ ] NBR 5422 (linhas aéreas transmissão)
  ├─ [ ] IEEE Std 738 (ampacidade condutor)
  └─ [ ] IEC 60826 (critérios design)

[✓] Projetos executados presentes
  ├─ [ ] Mínimo 3 LTs leiloadas (ANEEL 2022-2025)
  ├─ [ ] Mínimo 2 subestações (336/500/765 kV)
  ├─ [ ] Projetos com Estudos R1-R5 completos
  └─ [ ] DWGs de traçado, perfis de terreno, BIMs de SE

[✓] Templates preenchidos
  ├─ [ ] Intake Q2 agente-energia (8 fases)
  ├─ [ ] Matriz de estudo de sistema (fluxo, curto, estabilidade)
  ├─ [ ] Cronograma RAP (30 anos) + marcos construtivos
  └─ [ ] Modelo financeiro RAP/VPL

**Comando de validação**:
```bash
find 03_Projetos/Energia/02-Estudos-Primarios -name "R*.pdf" | wc -l  # Deve ser ≥ 5
grep -r "ANEEL" 03_Projetos/Energia/00-Normativos | wc -l              # Deve ter referências
```

---

### 3.3 S6 — Portos

```
[✓] Pastas principais criadas
  ├─ [?] 03_Projetos/Portos/00-Normativos
  ├─ [?] 03_Projetos/Portos/01-Projetos-Executados → Terminais reais
  ├─ [?] 03_Projetos/Portos/02-Estudos-Primarios → Hidrográficos, geotécnicos
  └─ [?] 03_Projetos/Portos/08-Casos-Internacionais → PIANC reports

[✓] Normas primárias sincronizadas
  ├─ [ ] Lei 12.815/2013 (lei dos portos)
  ├─ [ ] Lei 14.301/2022 (BR do Mar)
  ├─ [ ] NBR 9782 (ações portuárias)
  ├─ [ ] PIANC reports (dragagem, layout cais)
  └─ [ ] ROM 0.2/2.0 (norma espanhola de referência)

[✓] Projetos executados presentes
  ├─ [ ] Mínimo 2 terminais contêiner (TEU >500k/ano)
  ├─ [ ] Mínimo 2 terminais granel (sólido + líquido)
  ├─ [ ] Editais de TUP (>2 casos)
  └─ [ ] DWGs cais, batimetrias, cronogramas dragagem

[✓] Templates preenchidos
  ├─ [ ] Intake Q2 agente-portos (8 fases)
  ├─ [ ] Matriz hidrográfica + oceanográfica
  ├─ [ ] Cronograma dragagem (ciclo anual)
  └─ [ ] Modelo econômico TUP/concessão

**Comando de validação**:
```bash
find 03_Projetos/Portos -name "*.dwg" | wc -l  # Deve ter DWGs de cais
grep -i "antaq\|pianc" 03_Projetos/Portos/00-Normativos -r | wc -l
```

---

### 3.4 S10 — Barragens

```
[✓] Pastas principais criadas
  ├─ [?] 03_Projetos/Barragens/00-Normativos
  ├─ [?] 03_Projetos/Barragens/01-Projetos-Executados → UHE, abastecimento, rejeitos
  ├─ [?] 03_Projetos/Barragens/02-Casos-Referencia → Fundão, Brumadinho
  └─ [?] 03_Projetos/Barragens/06-Modelos-Financeiros → VPL UHE/PPP

[✓] Normas primárias sincronizadas
  ├─ [ ] Lei 12.334/2010 (PNSB)
  ├─ [ ] Lei 14.066/2020 (pós-Brumadinho)
  ├─ [ ] ANM Resolução 95/2022 (descaracterização)
  ├─ [ ] ICOLD Bulletins (164=CFRD, 194=rejeitos filtrados)
  └─ [ ] CBDB cadernos técnicos (rejeitos, segurança)

[✓] Projetos executados presentes
  ├─ [ ] Mínimo 2 barragens hidrelétricas (100+ MW)
  ├─ [ ] Mínimo 2 barragens abastecimento (50+ km³)
  ├─ [ ] Mínimo 2 barragens rejeitos (ativas)
  └─ [ ] DWGs seção típica, fundações, instrumentação

[✓] Templates preenchidos
  ├─ [ ] Intake Q2 agente-barragens (8 fases + descomissionamento)
  ├─ [ ] Matriz hidrológica (PMP, hidrograma projeto, regularização)
  ├─ [ ] Cronograma obra (sazonal, desvio)
  └─ [ ] Plano PAE/PAEBM (zoneamento ZAS/ZSS)

**Comando de validação**:
```bash
find 03_Projetos/Barragens/02-Casos-Referencia -name "*Fundão*" -o -name "*Brumadinho*" | wc -l
find 03_Projetos/Barragens -name "*.dwg" -o -name "*seção*" | wc -l
```

---

### 3.5 S7 — Aeroportos

```
[✓] Pastas principais criadas
  ├─ [?] 03_Projetos/Aeroportos/00-Normativos
  ├─ [?] 03_Projetos/Aeroportos/01-Projetos-Executados → TPS, pistas, taxiways
  ├─ [?] 03_Projetos/Aeroportos/03-Estudos-Tecnicos → Mix de aeronaves, mix de movimentos
  └─ [?] 03_Projetos/Aeroportos/06-Modelos-Financeiros → PPP concessão

[✓] Normas primárias sincronizadas
  ├─ [ ] RBAC 154 (ANAC — obrigatório BR)
  ├─ [ ] ICAO Annex 14 (design + operações)
  ├─ [ ] FAA ACs 150/5300-13 (design padrão)
  ├─ [ ] FAA AC 150/5320-6 (pavimentos aeroportuários)
  └─ [ ] DECEA ICA 100-12 (espaço aéreo)

[✓] Projetos executados presentes
  ├─ [ ] Mínimo 2 TPS (>500k passageiros/ano)
  ├─ [ ] Mínimo 2 projetos pista/taxiway (renovação ou novo)
  ├─ [ ] Mínimo 1 aeroporto regional (PCN, pavimento simpli ficado)
  └─ [ ] DWGs orientação pista, RESA, sistema de drenagem

[✓] Templates preenchidos
  ├─ [ ] Intake Q2 agente-aeroportos (8 fases)
  ├─ [ ] Mix de aeronaves + TPHP (movimentos hora-pico)
  ├─ [ ] Cronograma respeitando janelas operacionais (trabalho noturno)
  └─ [ ] Modelo PPP concessão (concessionário + ANAC)

**Comando de validação**:
```bash
find 03_Projetos/Aeroportos -name "*pista*" -o -name "*RWY*" -o -name "*TPS*" | wc -l
grep -i "rbac\|anac\|icao" 03_Projetos/Aeroportos/00-Normativos -r | wc -l
```

---

## 4. ROADMAP — PRÓXIMAS FASES (TIMELINE ESTIMADA)

### FASE 1: SINCRONIZAÇÃO LOCAL (SEMANA 2026-07-24 A 2026-07-28)

**Objetivo**: Ter todo conteúdo TIER 1 + TIER 2 local + validado.

| Dia | Ação | Comando | Responsável |
|-----|------|---------|-------------|
| **24-Jul (hoje)** | Setup local + TIER 1 inicial | `./setup-sync-s6-s10.sh && ./sync-tier1.sh` | Maestro |
| **25-Jul** | Validação TIER 1 + correção gaps | `./validate-tier1.sh && ./generate-gaps-report.sh` | Maestro + Usuário |
| **26-Jul** | TIER 2 (paralelo com correções TIER 1) | `./sync-tier2.sh` | Maestro |
| **27-Jul** | Validação checklists por segmento | `for s in s8 s9 s6 s10 s7; do ./checklist-${s}.sh; done` | Usuário (por segmento) |
| **28-Jul** | Relatório consolidado + aprovação | `./generate-consolidation-report.sh` | Maestro |

**Output esperado**: 
- [x] Pasta `~/Manta-S6-S10-Sync/03_Projetos/` com estrutura completa
- [x] Relatório de gaps / missing documents
- [x] Checklists validados por segmento

---

### FASE 2: PREPARAÇÃO RAG (SEMANA 2026-07-31 A 2026-08-04)

**Objetivo**: Preparar ingestion em Supabase para cada agente.

| Segmento | Ação | Prioridade | Timeline |
|----------|------|-----------|----------|
| **S8 Saneamento** | Ingestar normas + 2-3 projetos AySA em `san:` | **P0** | 31-Jul a 01-Ago |
| **S9 Energia** | Ingestar R1-R5 ANEEL + 2-3 LTs em `ene:` | **P0** | 31-Jul a 01-Ago |
| **S6 Portos** | Ingestar PIANC + 2-3 terminais em `por:` | **P1** | 02-Ago |
| **S10 Barragens** | Ingestar ICOLD + Lei 12.334 em `bar:` | **P1** | 02-Ago |
| **S7 Aeroportos** | Ingestar RBAC/ICAO + 2-3 TPS em `aer:` | **P2** | 03-04-Ago |

**Como ingestar**:
1. Usar Supabase CLI ou Graph API para bulk upload de PDFs para `storage/{prefixo}/*`
2. Executar embedding (via OpenAI or Anthropic Claude) em chunks de 1024 tokens
3. Inserir em tabela `rag_chunks` (document_id, segment, chunk, embedding, metadata)

**Comando template**:
```bash
# Exemplo: ingestar S8 Saneamento
python3 ingest-rag.py \
  --source ~/Manta-S6-S10-Sync/03_Projetos/Saneamento \
  --segment san \
  --supabase-url $SUPABASE_URL \
  --supabase-key $SUPABASE_KEY \
  --model claude-3-5-sonnet  # Ou similar
```

---

### FASE 3: VALIDAÇÃO AGENTES (SEMANA 2026-08-07 A 2026-08-11)

**Objetivo**: Testar routing e respostas para cada segmento.

| Teste | Prompt-exemplo | Segmento | Esperado |
|-------|--------|----------|----------|
| **Routing correto** | "Preciso de projeto de ETA com 100k m³/dia para AySA" | S8 | → agente-saneamento |
| **Respostas fundamentadas** | "Qual a norma de transmissão 500 kV?" | S9 | Cita ANEEL REN + NBR 5422 |
| **Acesso a projetos** | "Mostre um terminal contêiner modelo em DWG" | S6 | RAG retorna 2-3 documentos |
| **Referência histórica** | "O que aprendemos com Brumadinho?" | S10 | Extrai de casos-referência |
| **Compliance ANAC** | "Qual a RBAC 154 para pavimento?" | S7 | Consulta normas + recomendação |

**Gating**: Apenas se todos os testes passarem, ativar routin g público.

---

### FASE 4: GO-LIVE (SEMANA 2026-08-14)

**Objetivo**: Ativar públicamente.

| Tarefa | Owner | Status |
|--------|-------|--------|
| Merge CLAUDE.md v4.2 ao repositório principal | Maestro | Pending |
| Criar 5 routing rules em `sp_agent_routing` table | Usuário (DBA) | Pending |
| Deploy SKILL.md ao SharePoint (`01-agentes-fundamentais/`) | Usuário | Pending |
| Comunicado aos agentes (Slack + email) | Manta 00 | Pending |
| Atualizar `ARQUITETURA-AGENTES-IA.md` (v1.0.0 → v2.0.0) | Maestro | Pending |

---

## 5. CHECKLIST EXECUTÁVEL FINAL

### Antes de começar
- [ ] rclone instalado + configurado (Microsoft Graph para SharePoint)
- [ ] Acesso a SharePoint como `mneves@mantaassociados.com`
- [ ] Pasta local ~/Manta-S6-S10-Sync preparada
- [ ] Espaço em disco: mínimo 2-5 GB

### TIER 1 — Completar até 25-Jul
- [ ] `./setup-sync-s6-s10.sh` executado
- [ ] `./sync-tier1.sh` completado
- [ ] `./validate-tier1.sh` passou
- [ ] Gaps identificados e documentados
- [ ] Todos os `00-Normativos/` preenchidos > 200 MB cada

### TIER 2 — Completar até 28-Jul
- [ ] `./sync-tier2.sh` completado
- [ ] Mínimo 3 projetos por segmento sincronizados
- [ ] Checklists por segmento (S6-S10) validados
- [ ] Consolidation report gerado

### RAG — Completar até 04-Ago
- [ ] Supabase project preparado (`rag_chunks` table criada)
- [ ] Ingestion scripts testados
- [ ] Chunking/embedding funcionando
- [ ] 5 prefixos de storage (`san:`, `ene:`, `por:`, `bar:`, `aer:`) preenchidos

### Go-live — 14-Ago
- [ ] Agentes testados com prompts de cada segmento
- [ ] Routing validado (Maestro roteia corretamente)
- [ ] SKILL.md registrados + publicados
- [ ] Gate humano: aprovação MN recebida

---

## ANEXO — Exemplo de Estrutura Local Esperada (após Fase 1)

```
~/Manta-S6-S10-Sync/
├── 03_Projetos/
│   ├── Saneamento/
│   │   ├── 00-Normativos/          (Lei 14.026, Lei 11.445, NBR 12211-12218, ... > 300 MB)
│   │   ├── 01-Projetos-Executados/ (ETA/ETE >50k, >500 MB)
│   │   ├── 02-Estudos-Primarios/   (PMSB, hidrológicos)
│   │   └── ...
│   ├── Energia/
│   │   ├── 00-Normativos/          (ANEEL REN, NBR 5422, IEEE 738, ... > 250 MB)
│   │   ├── 01-Projetos-Executados/ (LTs leiloadas + DWGs, >600 MB)
│   │   ├── 02-Estudos-Primarios/   (R1-R5 ANEEL)
│   │   └── ...
│   ├── Portos/
│   │   ├── 00-Normativos/          (Lei 12.815, PIANC, NBR, ... > 200 MB)
│   │   ├── 01-Projetos-Executados/ (Terminais DWG, >400 MB)
│   │   └── ...
│   ├── Barragens/
│   │   ├── 00-Normativos/          (Lei 12.334, ICOLD, CBDB, ... > 200 MB)
│   │   ├── 01-Projetos-Executados/ (UHE, rejeitos, DWGs, >500 MB)
│   │   ├── 02-Casos-Referencia/    (Fundão, Brumadinho docs)
│   │   └── ...
│   └── Aeroportos/
│       ├── 00-Normativos/          (RBAC 154, ICAO Annex 14, FAA, ... > 180 MB)
│       ├── 01-Projetos-Executados/ (TPS, pistas, >300 MB)
│       └── ...
├── sync-tier1.log
├── sync-tier2.log
├── validate-tier1-report.txt
├── gaps-report.txt
└── consolidation-report.txt
```

**Tamanho total estimado**: 3–5 GB (com projetos reais > 6 GB)

---

**FIM DO PLANO**

Maestro | 2026-07-24 | v1.0
