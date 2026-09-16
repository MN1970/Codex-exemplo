-- Manta Maestro — D4 (retenção de logs): novas tabelas de retenção
-- Ticket: ADR D1-D4 (docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md),
-- seção "Correção de diagnóstico — 2026-09-13", D4.
--
-- CONTEXTO
-- ---------------------------------------------------------------------
-- O diagnóstico corrigido do D4 confirmou que, hoje, NÃO existe nenhuma
-- tabela real para: (a) decisão de claim/contratual/advisory (retenção
-- indefinida, sem purga automática — mesma lógica de laudo técnico);
-- (b) revisão de artefato (Etapa 4 da skill manta-arquiteto-ia: 30 dias
-- reversível, depois arquivado indefinidamente, nunca deletado); (c)
-- logs Cowork/task-run (30 dias, operacional, sem valor de auditoria
-- após execução confirmada).
--
-- As 3 tabelas abaixo são novas, simples e determinísticas — nenhuma
-- delas colide com tabelas já existentes (`maestro_runs`, `routing_events`,
-- `agent_memory`) e nenhuma tem trigger de purga automática embutido:
--   - `agent_decision_log` e `artifact_review_log` são, por definição,
--     de retenção indefinida/reversível — não devem ser apagadas por um
--     job automático.
--   - `cowork_task_log` tem TTL de 30 dias, mas o job real que executa
--     `DELETE WHERE retention_until < NOW()` fica FORA do escopo desta
--     migração (ver comentário na tabela) — não criar aqui um job que
--     ninguém aciona ainda, para não repetir o padrão mockado que este
--     mesmo ADR corrigiu em `scripts/agent_memory_purge.py`.
--
-- Esta é uma MIGRAÇÃO CANDIDATA — gate humano MN antes de aplicar em
-- produção real.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_13_d4_decision_retention_tables.sql

BEGIN;

-- ---------------------------------------------------------------------
-- 1. agent_decision_log — claim/contratual/advisory (Manta 01/02/15)
-- ---------------------------------------------------------------------
-- Retenção INDEFINIDA por design — rastreabilidade jurídica, mesma
-- lógica de laudo técnico: nunca se apaga sozinho. SEM coluna de
-- expiração de propósito (não é um esquecimento, é a decisão do D4).

CREATE TABLE IF NOT EXISTS agent_decision_log (
  id                BIGSERIAL PRIMARY KEY,
  agent_slug        TEXT NOT NULL,
  decision_summary  TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  retention_policy  TEXT NOT NULL DEFAULT 'indefinite'
    CHECK (retention_policy = 'indefinite')
);

CREATE INDEX IF NOT EXISTS idx_agent_decision_log_agent_created
  ON agent_decision_log (agent_slug, created_at DESC);

COMMENT ON TABLE agent_decision_log IS
  'D4: log de decisões de claim/contratual/advisory (Manta 01/02/15). '
  'RETENÇÃO INDEFINIDA — nunca purgada automaticamente. Não adicionar '
  'coluna de expiração/DELETE automático sem nova decisão MN (mesma '
  'lógica de laudo técnico: rastreabilidade jurídica).';
COMMENT ON COLUMN agent_decision_log.retention_policy IS
  'Sempre "indefinite" (CHECK constraint) — documenta a intenção no '
  'próprio dado, não só em comentário de schema.';

-- ---------------------------------------------------------------------
-- 2. artifact_review_log — revisão de artefato (Etapa 4, manta-arquiteto-ia)
-- ---------------------------------------------------------------------
-- 30 dias reversível (reversible_until), depois arquivado indefinidamente
-- (archived_at marcado, linha NUNCA deletada — "arquivado", não "purgado").

CREATE TABLE IF NOT EXISTS artifact_review_log (
  id                BIGSERIAL PRIMARY KEY,
  artifact_ref      TEXT NOT NULL,
  reviewed_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  reversible_until  TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 days'),
  archived_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_artifact_review_log_artifact
  ON artifact_review_log (artifact_ref, reviewed_at DESC);
CREATE INDEX IF NOT EXISTS idx_artifact_review_log_reversible_until
  ON artifact_review_log (reversible_until)
  WHERE archived_at IS NULL;

COMMENT ON TABLE artifact_review_log IS
  'D4: log de revisão de artefato (Etapa 4 da skill manta-arquiteto-ia). '
  '30 dias reversível (reversible_until); depois disso, marcar '
  'archived_at (arquivado indefinidamente) — NUNCA fazer DELETE. Um job '
  'de arquivamento real (fora do escopo desta migração) faria: '
  'UPDATE artifact_review_log SET archived_at = NOW() '
  'WHERE reversible_until < NOW() AND archived_at IS NULL.';
COMMENT ON COLUMN artifact_review_log.reversible_until IS
  'Janela de 30 dias em que a revisão ainda pode ser desfeita.';
COMMENT ON COLUMN artifact_review_log.archived_at IS
  'NULL enquanto reversível; timestamp de arquivamento depois disso. '
  'A linha permanece na tabela indefinidamente — arquivar != deletar.';

-- ---------------------------------------------------------------------
-- 3. cowork_task_log — logs Cowork / task-run
-- ---------------------------------------------------------------------
-- 30 dias, operacional, sem valor de auditoria após execução confirmada.
-- Ao contrário das duas tabelas acima, esta é candidata a purga real —
-- mas a função/job que executa o DELETE fica fora do escopo desta
-- migração (evitar repetir o padrão mockado corrigido em
-- scripts/agent_memory_purge.py: não criar aqui uma função "de mentira"
-- que nada aciona).

CREATE TABLE IF NOT EXISTS cowork_task_log (
  id                BIGSERIAL PRIMARY KEY,
  task_ref          TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  retention_until   TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX IF NOT EXISTS idx_cowork_task_log_retention_until
  ON cowork_task_log (retention_until);
CREATE INDEX IF NOT EXISTS idx_cowork_task_log_task_created
  ON cowork_task_log (task_ref, created_at DESC);

COMMENT ON TABLE cowork_task_log IS
  'D4: log de tasks/execuções Cowork. Retenção de 30 dias, operacional, '
  'sem valor de auditoria após execução confirmada. IMPORTANTE: esta '
  'migração só cria a tabela e a coluna de expiração — o job/função real '
  'de purga (DELETE FROM cowork_task_log WHERE retention_until < NOW()) '
  'fica fora de escopo aqui e deve ser implementado e agendado '
  '(cron/APScheduler) separadamente, seguindo o mesmo padrão real (não '
  'mockado) de scripts/agent_memory_cleanup.py — nunca deixar este '
  'comentário como a única coisa que "executa" a purga.';
COMMENT ON COLUMN cowork_task_log.retention_until IS
  'Quando < NOW(), a linha é candidata a DELETE por um job real ainda '
  'não implementado (ver comentário da tabela).';

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP TABLE IF EXISTS cowork_task_log;
-- DROP TABLE IF EXISTS artifact_review_log;
-- DROP TABLE IF EXISTS agent_decision_log;
--
-- COMMIT;
