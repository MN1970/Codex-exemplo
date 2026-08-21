-- Manta Maestro — Agent Heartbeat / Health Registry
-- Companion schema for services/heartbeat/heartbeat-service.js
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN. O serviço também cria esta tabela automaticamente na
-- inicialização (CREATE TABLE IF NOT EXISTS) caso a migração ainda
-- não tenha sido aplicada — este arquivo serve para deixá-la
-- versionada e revisável junto do restante do schema do Maestro.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_02_agent_health_heartbeat.sql
--
-- ROLLBACK: ver bloco DOWN no fim deste arquivo.

BEGIN;

CREATE TABLE IF NOT EXISTS agent_health (
  agent_id           TEXT PRIMARY KEY,             -- e.g. 'agente-saneamento', 'manta-05'
  status             TEXT NOT NULL CHECK (status IN ('healthy','degraded','unhealthy')),
  queue_depth        INTEGER NOT NULL DEFAULT 0,
  error_rate_5m      NUMERIC NOT NULL DEFAULT 0 CHECK (error_rate_5m >= 0 AND error_rate_5m <= 1),
  last_heartbeat_at  TIMESTAMPTZ NOT NULL,
  unhealthy_since    TIMESTAMPTZ,                   -- NULL unless currently unhealthy
  routable           BOOLEAN NOT NULL DEFAULT TRUE, -- FALSE once unhealthy > 10 min (grace window)
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_health_status ON agent_health (status);
CREATE INDEX IF NOT EXISTS idx_agent_health_routable ON agent_health (routable);

COMMENT ON TABLE agent_health IS
  'Última posição conhecida de cada agente Manta, atualizada a cada heartbeat (~5 min). '
  'O Maestro consulta routable=TRUE antes de rotear; agentes unhealthy por mais de '
  '10 min (ver HEARTBEAT_UNHEALTHY_GRACE_MS) ficam routable=FALSE.';

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
-- DROP TABLE IF EXISTS agent_health;
-- COMMIT;
