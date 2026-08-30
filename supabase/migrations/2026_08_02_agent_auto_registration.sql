-- Manta Maestro — Agent Registry core + auto-registration / A-B test support
-- Ticket: MNT-2026-AGENT-AUTOREG
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA (mesma política do
-- 2026_07_05_v4_2_agents_s6_s10.sql: revisar contra o schema real
-- antes de aplicar em produção; gate humano MN).
--
-- Cria a fundação descrita em
-- docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1 (tabela `agents` +
-- telemetria) que ainda não tinha migração própria, e adiciona as
-- colunas/tabelas necessárias para o fluxo de auto-registration
-- implementado em infra/agent-registry/:
--   1. novo agente vira linha em `agents` com lifecycle='alpha'
--   2. self-test grava 5 execuções em `agent_self_test_results`
--   3. se todas passarem, A/B test começa: traffic_percentage=5,
--      lifecycle='beta', ab_test_started_at=now, ab_test_ends_at=+7d
--   4. após 1 semana, `agent_promotion_events` registra a decisão
--      (promoted → traffic 100 / lifecycle prod, ou rejected/rollback)
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_02_agent_auto_registration.sql
--
-- ROLLBACK: ver bloco DOWN comentado no fim do arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Tabela mestre de agentes (schema §4.1 do doc de arquitetura v5.0)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agents (
  id                      TEXT PRIMARY KEY,          -- slug do frontmatter, ex. "agente-saneamento"
  name                    TEXT NOT NULL,
  description             TEXT,

  -- Expertise
  expertise_primary       TEXT[] DEFAULT '{}',
  expertise_secondary     TEXT[] DEFAULT '{}',
  keywords                TEXT[] DEFAULT '{}',

  -- Capabilities
  model                   TEXT CHECK (model IN ('haiku', 'sonnet', 'opus')),
  skills                  TEXT[] DEFAULT '{}',
  tools                   TEXT[] DEFAULT '{}',
  rag_collections         TEXT[] DEFAULT '{}',

  -- Metadata
  version                 TEXT,
  tier                    INT DEFAULT 3,
  handoffs_to             TEXT[] DEFAULT '{}',
  lifecycle               TEXT DEFAULT 'alpha'
                           CHECK (lifecycle IN ('alpha', 'beta', 'prod', 'rejected', 'deprecated')),
  cost_per_call           INT DEFAULT 1000,

  -- Auto-registration / A-B test tracking
  source_path             TEXT,                       -- ".claude/agents/agente-x.md"
  source_commit           TEXT,                        -- git sha that (re)registered this agent
  registered_at           TIMESTAMPTZ,
  traffic_percentage      INT DEFAULT 0 CHECK (traffic_percentage BETWEEN 0 AND 100),
  ab_test_started_at      TIMESTAMPTZ,
  ab_test_ends_at         TIMESTAMPTZ,
  promoted_at             TIMESTAMPTZ,
  promotion_status        TEXT DEFAULT 'pending'
                           CHECK (promotion_status IN ('pending', 'self_test_failed', 'ab_testing', 'promoted', 'rolled_back')),

  created_at              TIMESTAMPTZ DEFAULT now(),
  updated_at              TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agents_expertise  ON agents USING GIN (expertise_primary);
CREATE INDEX IF NOT EXISTS idx_agents_lifecycle  ON agents (lifecycle);
CREATE INDEX IF NOT EXISTS idx_agents_promotion  ON agents (promotion_status, ab_test_ends_at);

-- ---------------------------------------------------------------------
-- 2. Health / telemetria (usada pelo Maestro para nunca rotear p/ "down")
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_health (
  id                BIGSERIAL PRIMARY KEY,
  agent_id          TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  status            TEXT DEFAULT 'healthy' CHECK (status IN ('healthy', 'degraded', 'down')),
  queue_depth       INT DEFAULT 0,
  avg_latency_ms    FLOAT,
  error_rate_24h    FLOAT,
  success_count     INT DEFAULT 0,
  error_count       INT DEFAULT 0,
  recorded_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_health_agent ON agent_health (agent_id, recorded_at DESC);

-- ---------------------------------------------------------------------
-- 3. Resultados do self-test (5 sample queries, <30s latency gate)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_self_test_results (
  id                BIGSERIAL PRIMARY KEY,
  agent_id          TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  run_id            TEXT NOT NULL,          -- groups the 5 queries of one self-test run
  query             TEXT NOT NULL,
  passed            BOOLEAN NOT NULL,
  latency_ms        INT,
  latency_threshold_ms INT DEFAULT 30000,
  error             TEXT,
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_self_test_agent_run ON agent_self_test_results (agent_id, run_id);

-- ---------------------------------------------------------------------
-- 4. Log de eventos de promoção / rollback do A-B test
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_promotion_events (
  id                BIGSERIAL PRIMARY KEY,
  agent_id          TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  event             TEXT NOT NULL CHECK (event IN (
                       'registered', 'self_test_passed', 'self_test_failed',
                       'ab_test_started', 'promoted', 'rolled_back'
                     )),
  traffic_percentage_before INT,
  traffic_percentage_after  INT,
  reason            TEXT,
  metrics           JSONB,                  -- snapshot: success_rate, avg_latency_ms, error_rate
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_promotion_events_agent ON agent_promotion_events (agent_id, created_at DESC);

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP TABLE IF EXISTS agent_promotion_events;
-- DROP TABLE IF EXISTS agent_self_test_results;
-- DROP TABLE IF EXISTS agent_health;
-- DROP TABLE IF EXISTS agents;
--
-- COMMIT;
