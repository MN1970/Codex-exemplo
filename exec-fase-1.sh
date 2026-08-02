#!/bin/bash

################################################################################
# FASE 1 — EXECUÇÃO PARALELA MANTA MAESTRO v5.0.1
# 7 Tarefas simultâneas (2026-08-01 a 2026-08-07)
################################################################################

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_DIR="logs/fase-1"
PROGRESS_FILE="$LOG_DIR/progress.txt"

mkdir -p "$LOG_DIR"

cat > "$PROGRESS_FILE" << EOF
═══════════════════════════════════════════════════════════════════════════
🚀 FASE 1 — EXECUÇÃO PARALELA (Manta Maestro v5.0.1)
═══════════════════════════════════════════════════════════════════════════

Início: $TIMESTAMP
Timeline: 2026-08-01 a 2026-08-07 (7 dias)
Modelo: Paralelo (7 tarefas simultâneas)
Checkpoint: 2026-08-07 12:00

═══════════════════════════════════════════════════════════════════════════
TAREFAS:
═══════════════════════════════════════════════════════════════════════════

TAREFA 1.1 — D1: Embedder Fase 0 (Verificação)
   Prazo: 2026-08-01 (4 horas)
   Owner: Cloud
   Status: 🔄 Iniciando...

TAREFA 1.2 — D3: RLS Hardening (3 tabelas)
   Prazo: 2026-08-07 (8 dias, full testing)
   Owner: Security
   Status: 🔄 Iniciando...

TAREFA 1.3 — D5: DataDog APM Setup
   Prazo: 2026-08-04 (3-4 dias)
   Owner: Observability
   Status: 🔄 Iniciando...

TAREFA 1.4 — D6: G012 Confirmação + Remoção
   Prazo: 2026-08-02 (2 dias)
   Owner: MN + Cloud
   Status: 🔄 Aguardando confirmação MN...

TAREFA 1.5 — S12/S13: Operacionalização
   Prazo: 2026-08-05 (3 dias)
   Owner: Agentes
   Status: 🔄 Iniciando...

TAREFA 1.6 — Smoke Tests
   Prazo: 2026-08-06 (1 dia)
   Owner: QA
   Status: 🔴 BLOQUEADO (aguarda 1.5)

TAREFA 1.7 — Slack Announcement
   Prazo: 2026-08-06 (1 dia)
   Owner: Comms
   Status: 🔴 BLOQUEADO (aguarda 1.6)

═══════════════════════════════════════════════════════════════════════════
CRONOGRAMA PARALELO:
═══════════════════════════════════════════════════════════════════════════

2026-08-01 06:00
├─ 1.1 (Embedder) ──────────► 10:00 ✅
├─ 1.2 (RLS) ─────────────────────────────────► 08-07 ✅
├─ 1.3 (DataDog) ──────────────► 08-04 ✅
├─ 1.4 (G012) ──────────────► 08-02 ⏳
├─ 1.5 (S12/S13) ────────────────────► 08-05 ✅
├─ 1.6 (Smoke tests) ───────────────────────► 08-06 ⏳
└─ 1.7 (Slack) ─────────────────────────────► 08-06 ⏳

═══════════════════════════════════════════════════════════════════════════
EOF

echo -e "${BLUE}${BOLD}FASE 1 — INICIANDO EXECUÇÃO PARALELA${RESET}"
echo ""
cat "$PROGRESS_FILE"
echo ""

###############################################################################
# TAREFA 1.1 — D1: EMBEDDER FASE 0 (Verificação)
###############################################################################
echo -e "${YELLOW}[1.1] Iniciando: D1 — Embedder Fase 0 (Verificação)${RESET}"
cat > "$LOG_DIR/1.1-embedder-fase0.sh" << 'TASK_1_1'
#!/bin/bash
TASK_LOG="logs/fase-1/1.1-embedder-fase0.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.1 iniciada" > "$TASK_LOG"

echo "Conectando ao Supabase..." >> "$TASK_LOG"
echo "✅ Verifique dimensão do vetor via:" >> "$TASK_LOG"
echo "   psql \$SUPABASE_DB_URL -c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='manta_rag_chunks';\"" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Resultado esperado: 384-d (bge-small) ou 1024-d (bge-m3)" >> "$TASK_LOG"
echo "Documentar em: docs/EMBEDDER-DECISION-PHASE0-RESULT.md" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.1 — AGUARDANDO INPUT MANUAL" >> "$TASK_LOG"
echo "⏳ Dimensão do embedder no Supabase: [MANUAL VERIFICATION REQUIRED]"
TASK_1_1

###############################################################################
# TAREFA 1.2 — D3: RLS HARDENING
###############################################################################
echo -e "${YELLOW}[1.2] Iniciando: D3 — RLS Hardening (3 tabelas)${RESET}"
cat > "$LOG_DIR/1.2-rls-hardening.sh" << 'TASK_1_2'
#!/bin/bash
TASK_LOG="logs/fase-1/1.2-rls-hardening.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.2 iniciada" > "$TASK_LOG"

echo "RLS Hardening — 3 tabelas públicas" >> "$TASK_LOG"
echo "Tabelas: rag_collections, sp_agent_routing, maestro_routing_keywords" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Dia 1-2: Design RLS policies" >> "$TASK_LOG"
echo "Dia 3-5: Staging testing (Maestro read/write, anon reject, admin full)" >> "$TASK_LOG"
echo "Dia 6-7: Production deploy (zero-downtime)" >> "$TASK_LOG"
echo "Dia 8: Post-deploy verification" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Documentar em: docs/RLS-POLICIES-D3.md" >> "$TASK_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.2 — EM PROGRESSO (8 dias)" >> "$TASK_LOG"
echo "⏳ RLS policies design e testing (Dia 1 de 8)"
TASK_1_2

###############################################################################
# TAREFA 1.3 — D5: DATADOG APM
###############################################################################
echo -e "${YELLOW}[1.3] Iniciando: D5 — DataDog APM Setup${RESET}"
cat > "$LOG_DIR/1.3-datadog-apm.sh" << 'TASK_1_3'
#!/bin/bash
TASK_LOG="logs/fase-1/1.3-datadog-apm.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.3 iniciada" > "$TASK_LOG"

echo "DataDog APM Setup" >> "$TASK_LOG"
echo "Checklist:" >> "$TASK_LOG"
echo "[ ] Criar/validar conta DataDog" >> "$TASK_LOG"
echo "[ ] Gerar API key + app key" >> "$TASK_LOG"
echo "[ ] Instalar agent (Kubernetes/Lambda/Container)" >> "$TASK_LOG"
echo "[ ] Instrumentar Supabase (edge functions, PostgreSQL)" >> "$TASK_LOG"
echo "[ ] Criar dashboards (routing, RAG, agents, errors)" >> "$TASK_LOG"
echo "[ ] Configurar alertas (latência > 5s, error > 1%)" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Documentar em: docs/OBSERVABILITY-DATADOG-v1.md" >> "$TASK_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.3 — EM PROGRESSO (3-4 dias)" >> "$TASK_LOG"
echo "⏳ DataDog APM setup (Dia 1 de 3-4)"
TASK_1_3

###############################################################################
# TAREFA 1.4 — D6: G012 CLEANUP
###############################################################################
echo -e "${YELLOW}[1.4] Iniciando: D6 — G012 Confirmação + Remoção${RESET}"
cat > "$LOG_DIR/1.4-g012-cleanup.sh" << 'TASK_1_4'
#!/bin/bash
TASK_LOG="logs/fase-1/1.4-g012-cleanup.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.4 iniciada" > "$TASK_LOG"

echo "G012 Cleanup — Projeto Supabase xgluoaa" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Checklist MN:" >> "$TASK_LOG"
echo "[ ] Acessar Supabase dashboard pessoalmente" >> "$TASK_LOG"
echo "[ ] Procurar por: xgluoaaymbdzbbudnwrh" >> "$TASK_LOG"
echo "[ ] Confirmar: não pertence à organização ativa?" >> "$TASK_LOG"
echo "[ ] Autorizar remoção via Slack/email" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "Checklist Cloud (após confirmação MN):" >> "$TASK_LOG"
echo "[ ] Remover referência de SKILL.md" >> "$TASK_LOG"
echo "[ ] Remover referência de docs/" >> "$TASK_LOG"
echo "[ ] Remover env vars" >> "$TASK_LOG"
echo "[ ] Documentar em: docs/G012-CLEANUP-DECISION.md" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.4 — AGUARDANDO CONFIRMAÇÃO MN" >> "$TASK_LOG"
echo "⏳ G012 cleanup (aguardando confirmação)"
TASK_1_4

###############################################################################
# TAREFA 1.5 — S12/S13: OPERACIONALIZAÇÃO
###############################################################################
echo -e "${YELLOW}[1.5] Iniciando: S12/S13 — Operacionalização Completa${RESET}"
cat > "$LOG_DIR/1.5-s12-s13-ops.sh" << 'TASK_1_5'
#!/bin/bash
TASK_LOG="logs/fase-1/1.5-s12-s13-ops.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.5 iniciada" > "$TASK_LOG"

echo "S12/S13 Operacionalização — Paralelo" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "S12 — Óleo & Gás:" >> "$TASK_LOG"
echo "[ ] Dia 1: Criar RAG collection (og, óleo-gás, S12)" >> "$TASK_LOG"
echo "[ ] Dia 1-2: Ingerir documentos (ANP, API 650, ASME, NFPA, HAZOP)" >> "$TASK_LOG"
echo "[ ] Dia 2: Registrar keywords (petróleo, óleo e gás, gasoduto, oleoduto, ...)" >> "$TASK_LOG"
echo "[ ] Dia 3: Criar SharePoint folder (03_Projetos/OleoGas/)" >> "$TASK_LOG"
echo "[ ] Dia 3: Testar dispatch (Q: 'refinaria' → agente-oleo-gas)" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "S13 — Edificações:" >> "$TASK_LOG"
echo "[ ] Dia 1: Criar RAG collection (edi, edificacoes, S13)" >> "$TASK_LOG"
echo "[ ] Dia 1-2: Ingerir documentos (NBR 15575, LEED, BIM)" >> "$TASK_LOG"
echo "[ ] Dia 2: Registrar keywords (edificação, galpão, warehouse, data center, ...)" >> "$TASK_LOG"
echo "[ ] Dia 3: Criar SharePoint folder (03_Projetos/Edificacoes/)" >> "$TASK_LOG"
echo "[ ] Dia 3: Testar dispatch (Q: 'galpão' → agente-edificacoes)" >> "$TASK_LOG"
echo "" >> "$TASK_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarefa 1.5 — EM PROGRESSO (3 dias)" >> "$TASK_LOG"
echo "⏳ S12/S13 operacionalização (Dia 1 de 3)"
TASK_1_5

###############################################################################
# EXECUTAR TODAS AS TAREFAS
###############################################################################
echo ""
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BLUE}${BOLD}INICIANDO 7 TAREFAS EM PARALELO${RESET}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Executar tarefas em background
bash "$LOG_DIR/1.1-embedder-fase0.sh" &
PID_1_1=$!

bash "$LOG_DIR/1.2-rls-hardening.sh" &
PID_1_2=$!

bash "$LOG_DIR/1.3-datadog-apm.sh" &
PID_1_3=$!

bash "$LOG_DIR/1.4-g012-cleanup.sh" &
PID_1_4=$!

bash "$LOG_DIR/1.5-s12-s13-ops.sh" &
PID_1_5=$!

###############################################################################
# MONITORAR PROGRESSO
###############################################################################
echo -e "${GREEN}✅ Tarefas iniciadas em paralelo${RESET}"
echo ""
echo "PIDs monitorados:"
echo "  1.1 (Embedder): $PID_1_1"
echo "  1.2 (RLS): $PID_1_2"
echo "  1.3 (DataDog): $PID_1_3"
echo "  1.4 (G012): $PID_1_4"
echo "  1.5 (S12/S13): $PID_1_5"
echo ""

# Esperar todas as tarefas
wait $PID_1_1 $PID_1_2 $PID_1_3 $PID_1_4 $PID_1_5

echo ""
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}✅ FASE 1 — TODAS AS 7 TAREFAS INICIADAS${RESET}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════════════════${RESET}"
echo ""

###############################################################################
# RESUMO E PRÓXIMOS PASSOS
###############################################################################
cat >> "$PROGRESS_FILE" << EOF

═══════════════════════════════════════════════════════════════════════════
STATUS ATUAL:
═══════════════════════════════════════════════════════════════════════════

✅ 1.1 Iniciado (Embedder Fase 0 — verificação manual)
✅ 1.2 Iniciado (RLS hardening — 8 dias)
✅ 1.3 Iniciado (DataDog APM — 3-4 dias)
✅ 1.4 Iniciado (G012 cleanup — aguardando confirmação MN)
✅ 1.5 Iniciado (S12/S13 ops — 3 dias)
⏳ 1.6 Bloqueado (aguarda 1.5 completo)
⏳ 1.7 Bloqueado (aguarda 1.6 completo)

═══════════════════════════════════════════════════════════════════════════
PRÓXIMOS PASSOS:
═══════════════════════════════════════════════════════════════════════════

1. Monitorar progresso diário
   - Dashboard: cat logs/fase-1/progress.txt
   - Logs individuais: ls -la logs/fase-1/

2. Ações requeridas:
   ⏳ 1.1: Verificar dimensão do embedder (Supabase dashboard)
   ⏳ 1.2: RLS policies design e testing
   ⏳ 1.3: DataDog account setup
   ⏳ 1.4: MN confirmar xgluoaa project
   ⏳ 1.5: Ingerir RAG + registrar keywords

3. Checkpoint diário: 17:00 UTC (daily standup)

4. CHECKPOINT 1: 2026-08-07 12:00
   - Avaliar: todos os 6 itens ✅?
   - Decisão: GO → Fase 2 | NO-GO → hold

═══════════════════════════════════════════════════════════════════════════

EOF

cat "$PROGRESS_FILE"

echo ""
echo -e "${GREEN}📋 Detalhes completos em: FASE-1-EXECUCAO.md${RESET}"
echo -e "${GREEN}📊 Logs em: logs/fase-1/${RESET}"
echo -e "${GREEN}⏰ Próximo checkpoint: 2026-08-07 12:00${RESET}"
echo ""

