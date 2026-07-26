#!/usr/bin/env bash
#
# Manta Maestro v4.2 — executor de deploy Supabase (S6-S10)
# Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
#
# Aplica, nesta ordem, os três arquivos em supabase/migrations/:
#   1. 2026_07_05_v4_2_agents_s6_s10_00_prereq_schema.sql  (DDL — cria tabelas se não existirem)
#   2. 2026_07_05_v4_2_agents_s6_s10.sql                   (DML — popula dados, idempotente)
#   3. 2026_07_05_v4_2_agents_s6_s10_validate.sql          (SELECT — valida o resultado)
#
# GATES DE SEGURANÇA (não contornar):
#   - Requer SUPABASE_DB_URL no ambiente.
#   - Requer MN_APPROVAL=yes no ambiente — reflete o item pendente
#     "Gate humano: aprovação MN antes de merge" do checklist v4.2 em
#     CLAUDE.md. Este script RECUSA rodar sem ele.
#   - Roda sempre em --dry-run (SELECT-only / psql -1 com ROLLBACK)
#     a menos que --apply seja passado explicitamente.
#   - Pré-checagem de schema: se as 3 tabelas já existirem só serão
#     alteradas nada (CREATE TABLE IF NOT EXISTS é no-op); se não
#     existirem, o prereq as cria — isso é logado, não é silencioso.
#
# Uso:
#   MN_APPROVAL=yes SUPABASE_DB_URL="postgresql://..." \
#     ./scripts/deploy_supabase_v4_2_s6_s10.sh --dry-run   # padrão, seguro
#
#   MN_APPROVAL=yes SUPABASE_DB_URL="postgresql://..." \
#     ./scripts/deploy_supabase_v4_2_s6_s10.sh --apply     # aplica de fato
#
#   ./scripts/deploy_supabase_v4_2_s6_s10.sh --rollback    # reverte (também requer MN_APPROVAL)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="$SCRIPT_DIR/../supabase/migrations"

PREREQ_FILE="$MIGRATIONS_DIR/2026_07_05_v4_2_agents_s6_s10_00_prereq_schema.sql"
DATA_FILE="$MIGRATIONS_DIR/2026_07_05_v4_2_agents_s6_s10.sql"
VALIDATE_FILE="$MIGRATIONS_DIR/2026_07_05_v4_2_agents_s6_s10_validate.sql"
ROLLBACK_FILE="$MIGRATIONS_DIR/2026_07_05_v4_2_agents_s6_s10_rollback.sql"

MODE="dry-run"
for arg in "$@"; do
  case "$arg" in
    --apply)    MODE="apply" ;;
    --dry-run)  MODE="dry-run" ;;
    --rollback) MODE="rollback" ;;
    --validate-only) MODE="validate-only" ;;
    *) echo "Argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

echo "=== Manta Maestro v4.2 — deploy Supabase (S6-S10) — modo: $MODE ==="

# ---------------------------------------------------------------------
# Gate 1 — aprovação humana MN (checklist CLAUDE.md)
# ---------------------------------------------------------------------
if [[ "${MN_APPROVAL:-}" != "yes" ]]; then
  cat >&2 <<'EOF'
BLOQUEADO: variável de ambiente MN_APPROVAL=yes não definida.

O CLAUDE.md master (v4.2, seção "DEPLOY CHECKLIST") lista
"Gate humano: aprovação MN antes de merge" como item NÃO CONCLUÍDO
([ ]). O próprio arquivo de migração também declara:
  "Não aplica em produção sem aprovação MN."

Este script se recusa a prosseguir sem confirmação explícita de que
esse gate foi cumprido. Se MN já aprovou, rode novamente com:
  MN_APPROVAL=yes ...
EOF
  exit 1
fi

if [[ "$MODE" != "rollback" && "$MODE" != "validate-only" ]]; then
  if [[ -z "${SUPABASE_DB_URL:-}" ]]; then
    echo "BLOQUEADO: SUPABASE_DB_URL não definida." >&2
    exit 1
  fi
fi

run_psql() {
  local file="$1"
  psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$file"
}

# ---------------------------------------------------------------------
# Gate 2 — pré-checagem de schema (idempotente, só relatório em dry-run)
# ---------------------------------------------------------------------
preflight_check() {
  echo "--- Preflight: verificando existência das tabelas alvo ---"
  psql "$SUPABASE_DB_URL" -t -A -c "
    SELECT table_name FROM information_schema.tables
    WHERE table_schema='public'
      AND table_name IN ('rag_collections','sp_agent_routing','maestro_routing_keywords')
    ORDER BY table_name;" | tee /tmp/_preflight_tables.txt

  local n_found
  n_found=$(wc -l < /tmp/_preflight_tables.txt | tr -d ' ')
  echo "Tabelas encontradas: $n_found / 3"

  if [[ "$n_found" -lt 3 ]]; then
    echo "AVISO: nem todas as 3 tabelas existem ainda. O prereq" \
         "(00_prereq_schema.sql) será aplicado antes da migração de dados."
  fi
}

# Roda um arquivo de migração como dry-run de verdade: os arquivos já
# têm BEGIN;...COMMIT; próprios, então NÃO adianta envolver com
# --single-transaction e anexar ROLLBACK — o COMMIT interno do arquivo
# fecha a transação antes disso, e as mudanças ficam persistidas (bug
# encontrado e corrigido durante a validação deste script). A forma
# segura é substituir a linha final "COMMIT;" por "ROLLBACK;" em uma
# cópia temporária, preservando toda a lógica DDL/DML para inspeção.
dry_run_file() {
  local file="$1"
  local tmp
  tmp="$(mktemp)"
  sed 's/^COMMIT;$/ROLLBACK;/' "$file" > "$tmp"
  psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$tmp"
  rm -f "$tmp"
}

case "$MODE" in
  dry-run)
    echo "Modo dry-run: nenhuma alteração será persistida (COMMIT trocado por ROLLBACK)."
    preflight_check
    echo "--- Simulando prereq (DDL) ---"
    dry_run_file "$PREREQ_FILE"
    echo "--- Simulando migração de dados (DML) ---"
    echo "NOTA: se as tabelas ainda não existirem de verdade (preflight < 3/3)," \
         "esta etapa falhará com 'relation does not exist' — isso é esperado:" \
         "o prereq precisa ser de fato aplicado (--apply) antes da migração de" \
         "dados poder ser simulada ou aplicada."
    dry_run_file "$DATA_FILE" || echo "(falha acima é esperada se o prereq real ainda não rodou)"
    echo "Dry-run concluído. Revise a saída acima. Para aplicar de fato, use --apply."
    ;;

  apply)
    preflight_check
    echo "--- Aplicando prereq (DDL, idempotente via IF NOT EXISTS) ---"
    run_psql "$PREREQ_FILE"
    echo "--- Aplicando migração de dados (DML, idempotente via ON CONFLICT DO NOTHING) ---"
    run_psql "$DATA_FILE"
    echo "--- Rodando validação pós-deploy ---"
    run_psql "$VALIDATE_FILE"
    echo "Deploy concluído. Confira manualmente os resultados de V2-V5 acima"\
         "contra os valores 'Esperado' documentados em"\
         "$VALIDATE_FILE."
    echo "Próximo passo: seguir docs/DEPLOY-v4.2.md seções 3-5 (SharePoint + testes de routing)."
    ;;

  validate-only)
    run_psql "$VALIDATE_FILE"
    ;;

  rollback)
    if [[ -z "${SUPABASE_DB_URL:-}" ]]; then
      echo "BLOQUEADO: SUPABASE_DB_URL não definida." >&2
      exit 1
    fi
    echo "--- Executando rollback (remove apenas as linhas S6-S10) ---"
    run_psql "$ROLLBACK_FILE"
    echo "Rollback concluído. Tabelas permanecem no schema (DROP TABLE é opcional,"\
         "ver bloco comentado no fim de $ROLLBACK_FILE)."
    ;;
esac
