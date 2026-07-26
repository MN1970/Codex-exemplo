-- Manta Maestro v4.3 — Agent Pool Configuration
-- Ticket: MNT-2026-MAESTRO-PARALELO-8-SONNET
-- Date: 2026-07-26

BEGIN;

-- Table: maestro_agent_pool
-- Stores configuration for 8-agent parallel execution pool
CREATE TABLE IF NOT EXISTS maestro_agent_pool (
  agent_code TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
  agent_type TEXT DEFAULT 'sonnet',
  model_tier TEXT DEFAULT 'sonnet' CHECK (model_tier IN ('haiku', 'sonnet', 'opus')),
  max_concurrent INT DEFAULT 1 CHECK (max_concurrent >= 1),
  timeout_sec INT DEFAULT 120 CHECK (timeout_sec >= 30),
  priority INT DEFAULT 0 CHECK (priority >= 0 AND priority <= 200),
  pool_group TEXT DEFAULT 'parallel-8-sonnet',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comment
COMMENT ON TABLE maestro_agent_pool IS 'Configuration for Maestro parallel execution pool (8 Sonnet agents)';

-- Insert 8-agent pool configuration
INSERT INTO maestro_agent_pool (agent_code, agent_name, model_tier, priority, pool_group) VALUES
  -- Horizontal agents (6)
  ('Manta-02', 'contratual', 'sonnet', 90, 'parallel-8-sonnet'),
  ('Manta-04', 'imobiliario', 'sonnet', 50, 'parallel-8-sonnet'),
  ('Manta-05', 'orcamento', 'sonnet', 100, 'parallel-8-sonnet'),
  ('Manta-07', 'cronograma', 'sonnet', 100, 'parallel-8-sonnet'),
  ('Manta-13', 'bd', 'sonnet', 70, 'parallel-8-sonnet'),
  ('Manta-14', 'apresentacoes', 'sonnet', 50, 'parallel-8-sonnet'),
  -- Vertical agents (2) — HIGH PRIORITY
  ('Manta-03-S8', 'agente-saneamento', 'sonnet', 200, 'parallel-8-sonnet'),
  ('Manta-03-S9', 'agente-energia', 'sonnet', 200, 'parallel-8-sonnet')
ON CONFLICT (agent_code) DO UPDATE SET
  agent_name = EXCLUDED.agent_name,
  model_tier = EXCLUDED.model_tier,
  priority = EXCLUDED.priority,
  updated_at = NOW();

-- Table: maestro_execution_logs
-- Track parallel execution metrics
CREATE TABLE IF NOT EXISTS maestro_execution_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id TEXT NOT NULL,
  agent_code TEXT NOT NULL REFERENCES maestro_agent_pool(agent_code),
  start_time TIMESTAMPTZ DEFAULT NOW(),
  end_time TIMESTAMPTZ,
  duration_ms INT,
  status TEXT CHECK (status IN ('pending', 'running', 'success', 'timeout', 'error')),
  result_tokens INT,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (agent_code) REFERENCES maestro_agent_pool(agent_code)
);

CREATE INDEX IF NOT EXISTS idx_maestro_logs_request_id ON maestro_execution_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_maestro_logs_agent_code ON maestro_execution_logs(agent_code);
CREATE INDEX IF NOT EXISTS idx_maestro_logs_status ON maestro_execution_logs(status);

COMMIT;

-- ===================================================================
-- ROLLBACK (executar se necessário)
-- ===================================================================
-- BEGIN;
--   DROP TABLE IF EXISTS maestro_execution_logs;
--   DROP TABLE IF EXISTS maestro_agent_pool;
-- COMMIT;
