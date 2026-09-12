-- Manta Maestro — D4 (retenção de logs): routing_events retention
-- Ticket: ADR D1-D4 (docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md),
-- seção "Correção de diagnóstico — 2026-09-13", D4.
--
-- CONTEXTO
-- ---------------------------------------------------------------------
-- `supabase/migrations/2026_08_02_routing_observability.sql` criou
-- `routing_events` (1 linha por decisão de roteamento do Maestro) e
-- `routing_feedback` (1 linha por feedback do bandit), mas nenhuma das
-- duas tem coluna de retenção/TTL — achado original do ADR D4.
--
-- A tabela de retenção do ADR (seção D4, "Proposta") define: "Routing
-- (Maestro → agente, scores) → 90 dias, sem valor regulatório". Isso
-- mapeia diretamente para `routing_events` (chosen_agent_id +
-- chosen_confidence = o "score" citado).
--
-- `routing_feedback` já tem `ON DELETE CASCADE` para `routing_events`
-- (routing_id REFERENCES routing_events(routing_id) ON DELETE CASCADE)
-- — arquivar/purgar `routing_events` já resolve o feedback associado
-- automaticamente, sem precisar de uma segunda coluna de retenção.
--
-- Segue o MESMO padrão de `2026_07_25_observability_maestro_runs.sql`
-- (`maestro_runs` → `maestro_runs_archive` + `archive_old_maestro_runs()`):
-- tabela archive espelho (sem FKs) + função que arquiva e depois purga
-- as linhas expiradas da tabela quente.
--
-- Esta é uma MIGRAÇÃO CANDIDATA — gate humano MN antes de aplicar em
-- produção real (mesma ressalva de todas as migrações candidatas deste
-- repositório).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_13_d4_routing_retention.sql

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Coluna de retenção em routing_events (90 dias, D4)
-- ---------------------------------------------------------------------

ALTER TABLE routing_events
  ADD COLUMN IF NOT EXISTS retention_until TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days');

COMMENT ON COLUMN routing_events.retention_until IS
  'D4 (ADR-D1-D4): retenção de 90 dias para logs de routing (sem valor '
  'regulatório) — linhas com retention_until < NOW() são elegíveis para '
  'archive_old_routing_events(). routing_feedback não precisa de coluna '
  'própria: ON DELETE CASCADE em routing_id já a acompanha.';

-- Backfill: o DEFAULT acima é avaliado uma única vez (no momento do
-- ALTER TABLE) para as linhas já existentes, então todas herdariam o
-- MESMO retention_until baseado em "agora", não no created_at real de
-- cada uma. Recalcula explicitamente a partir de created_at para que
-- linhas antigas expirem quando deveriam (created_at + 90 dias), não
-- 90 dias a partir da data desta migração.
UPDATE routing_events
SET retention_until = created_at + INTERVAL '90 days';

-- ---------------------------------------------------------------------
-- 2. routing_events_archive — mesma estrutura, sem FKs (padrão maestro_runs_archive)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS routing_events_archive (
  id                BIGINT PRIMARY KEY,
  routing_id        TEXT NOT NULL,
  query_hash        TEXT,
  query_preview     TEXT,
  top_candidates    JSONB NOT NULL DEFAULT '[]'::jsonb,
  chosen_agent_id   TEXT NOT NULL,
  chosen_confidence NUMERIC NOT NULL,
  samples           JSONB NOT NULL DEFAULT '{}'::jsonb,
  latency_ms        INT,
  tokens_used       INT,
  created_at        TIMESTAMPTZ NOT NULL,
  retention_until   TIMESTAMPTZ,
  archived_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routing_events_archive_created
  ON routing_events_archive (created_at DESC);

COMMENT ON TABLE routing_events_archive IS
  'Arquivo de routing_events com retention_until < NOW() (D4, 90 dias). '
  'Populado e esvaziado da tabela quente por archive_old_routing_events().';

-- ---------------------------------------------------------------------
-- 3. archive_old_routing_events() — mesmo estilo de archive_old_maestro_runs()
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION archive_old_routing_events()
RETURNS TABLE(archived_count INT) AS $$
DECLARE
  _archived_count INT;
BEGIN
  -- Copia para o archive as linhas expiradas (retention_until < NOW()).
  INSERT INTO routing_events_archive (
    id, routing_id, query_hash, query_preview, top_candidates,
    chosen_agent_id, chosen_confidence, samples, latency_ms, tokens_used,
    created_at, retention_until, archived_at
  )
  SELECT
    id, routing_id, query_hash, query_preview, top_candidates,
    chosen_agent_id, chosen_confidence, samples, latency_ms, tokens_used,
    created_at, retention_until, NOW()
  FROM routing_events
  WHERE retention_until < NOW()
  ON CONFLICT (id) DO NOTHING;

  GET DIAGNOSTICS _archived_count = ROW_COUNT;

  -- Purga da tabela quente (sem valor regulatório — D4 não exige
  -- retenção indefinida para routing, ao contrário de claim/contratual/
  -- advisory). routing_feedback associado é removido em cascata.
  DELETE FROM routing_events
  WHERE retention_until < NOW();

  RETURN QUERY SELECT _archived_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archive_old_routing_events() IS
  'D4: arquiva (routing_events_archive) e depois purga de routing_events '
  'as linhas com retention_until < NOW() (política de 90 dias). Chamar '
  'via job agendado (cron/APScheduler), nunca via decisão do LLM em '
  'tempo real — mesmo anti-padrão evitado em archive_old_maestro_runs().';

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP FUNCTION IF EXISTS archive_old_routing_events();
-- DROP TABLE IF EXISTS routing_events_archive;
-- ALTER TABLE routing_events DROP COLUMN IF EXISTS retention_until;
--
-- COMMIT;
