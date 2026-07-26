-- Migration: Maestro Runtime Metrics and Monitoring
-- Purpose: Track Maestro performance, model usage, and system health
-- Date: 2026-07-25

BEGIN;

-- 1. Table for runtime metrics (every dispatch)
CREATE TABLE IF NOT EXISTS maestro_runtime_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamp DEFAULT now(),
  agent_slug text NOT NULL,

  -- Input metrics
  prompt_tokens int NOT NULL,
  response_tokens int NOT NULL,
  total_tokens int GENERATED ALWAYS AS (prompt_tokens + response_tokens) STORED,

  -- Performance metrics
  latency_ms float NOT NULL,

  -- Model and tier selection
  model_tier text NOT NULL, -- 'haiku', 'sonnet', 'opus'
  model_name text NOT NULL,

  -- Fallback tracking
  fallback_count int DEFAULT 0,
  fallback_reason text NULL, -- 'latency', 'cost', 'error', 'none'

  -- Routing context
  routing_confidence float DEFAULT 0.0, -- 0-1
  routing_keywords text[] DEFAULT NULL,

  -- Request context
  session_id text NULL,
  user_id text NULL,
  request_id text NULL,

  -- Tags for analytics
  tags jsonb DEFAULT '{}',

  created_at timestamp DEFAULT now()
);

-- 2. Indices for common queries
CREATE INDEX IF NOT EXISTS idx_maestro_metrics_timestamp
  ON maestro_runtime_metrics(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_metrics_agent
  ON maestro_runtime_metrics(agent_slug, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_metrics_model
  ON maestro_runtime_metrics(model_tier, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_metrics_session
  ON maestro_runtime_metrics(session_id)
  WHERE session_id IS NOT NULL;

-- 3. Table for routing decisions (trace-level)
CREATE TABLE IF NOT EXISTS maestro_routing_trace (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamp DEFAULT now(),

  prompt text NOT NULL,
  prompt_hash text NOT NULL UNIQUE, -- hash for dedup

  -- Routing scoring
  primary_agent text NOT NULL,
  primary_score float NOT NULL,
  alternate_agents jsonb DEFAULT '[]', -- [{agent, score}, ...]

  -- Confidence metrics
  score_gap float DEFAULT NULL, -- primary_score - runner_up_score
  is_ambiguous boolean DEFAULT false, -- gap < 10 points

  -- Execution
  executed_agent text NULL, -- which agent actually handled it
  user_approved boolean DEFAULT NULL, -- feedback

  session_id text NULL,
  created_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_trace_timestamp
  ON maestro_routing_trace(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_trace_primary
  ON maestro_routing_trace(primary_agent, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_trace_ambiguous
  ON maestro_routing_trace(is_ambiguous, timestamp DESC)
  WHERE is_ambiguous = true;

-- 4. Table for aggregated daily metrics (materialized view support)
CREATE TABLE IF NOT EXISTS maestro_metrics_daily (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  agent_slug text NOT NULL,

  -- Throughput
  total_requests int DEFAULT 0,
  total_tokens bigint DEFAULT 0,

  -- Latency percentiles
  latency_p50 float DEFAULT 0,
  latency_p95 float DEFAULT 0,
  latency_p99 float DEFAULT 0,
  latency_max float DEFAULT 0,

  -- Model distribution
  haiku_count int DEFAULT 0,
  sonnet_count int DEFAULT 0,
  opus_count int DEFAULT 0,

  -- Fallback tracking
  fallback_count int DEFAULT 0,
  fallback_rate float DEFAULT 0.0,

  -- Routing quality
  ambiguous_cases int DEFAULT 0,
  average_confidence float DEFAULT 0.0,

  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_maestro_metrics_daily_unique
  ON maestro_metrics_daily(date, agent_slug);

CREATE INDEX IF NOT EXISTS idx_maestro_metrics_daily_date
  ON maestro_metrics_daily(date DESC);

-- 5. Function to insert metric (called by Maestro router)
CREATE OR REPLACE FUNCTION insert_maestro_metric(
  p_agent_slug text,
  p_prompt_tokens int,
  p_response_tokens int,
  p_latency_ms float,
  p_model_tier text,
  p_model_name text,
  p_fallback_count int DEFAULT 0,
  p_routing_confidence float DEFAULT 0.0,
  p_session_id text DEFAULT NULL,
  p_user_id text DEFAULT NULL,
  p_tags jsonb DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_metric_id uuid;
BEGIN
  INSERT INTO maestro_runtime_metrics (
    agent_slug,
    prompt_tokens,
    response_tokens,
    latency_ms,
    model_tier,
    model_name,
    fallback_count,
    routing_confidence,
    session_id,
    user_id,
    tags
  ) VALUES (
    p_agent_slug,
    p_prompt_tokens,
    p_response_tokens,
    p_latency_ms,
    p_model_tier,
    p_model_name,
    p_fallback_count,
    p_routing_confidence,
    p_session_id,
    p_user_id,
    COALESCE(p_tags, '{}')
  ) RETURNING id INTO v_metric_id;

  RETURN v_metric_id;
END;
$$;

-- 6. Function to compute daily metrics (called nightly)
CREATE OR REPLACE FUNCTION compute_daily_metrics(p_date date DEFAULT CURRENT_DATE)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_agent text;
BEGIN
  -- Clear existing metrics for the day
  DELETE FROM maestro_metrics_daily WHERE date = p_date;

  -- Compute metrics per agent
  FOR v_agent IN
    SELECT DISTINCT agent_slug FROM maestro_runtime_metrics
    WHERE DATE(timestamp) = p_date
  LOOP
    INSERT INTO maestro_metrics_daily (
      date,
      agent_slug,
      total_requests,
      total_tokens,
      latency_p50,
      latency_p95,
      latency_p99,
      latency_max,
      haiku_count,
      sonnet_count,
      opus_count,
      fallback_count,
      fallback_rate,
      average_confidence
    )
    SELECT
      p_date,
      v_agent,
      COUNT(*),
      SUM(total_tokens),
      percentile_cont(0.50) WITHIN GROUP (ORDER BY latency_ms),
      percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms),
      percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms),
      MAX(latency_ms),
      COUNT(*) FILTER (WHERE model_tier = 'haiku'),
      COUNT(*) FILTER (WHERE model_tier = 'sonnet'),
      COUNT(*) FILTER (WHERE model_tier = 'opus'),
      SUM(fallback_count),
      AVG(CASE WHEN fallback_count > 0 THEN 1.0 ELSE 0.0 END),
      AVG(routing_confidence)
    FROM maestro_runtime_metrics
    WHERE agent_slug = v_agent AND DATE(timestamp) = p_date
    GROUP BY v_agent;
  END LOOP;
END;
$$;

-- 7. Create view for current hour metrics
CREATE OR REPLACE VIEW maestro_metrics_current_hour AS
SELECT
  agent_slug,
  COUNT(*) as request_count,
  AVG(latency_ms) as avg_latency,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
  SUM(prompt_tokens) as total_prompt_tokens,
  SUM(response_tokens) as total_response_tokens,
  COUNT(*) FILTER (WHERE model_tier = 'haiku') as haiku_calls,
  COUNT(*) FILTER (WHERE model_tier = 'sonnet') as sonnet_calls,
  COUNT(*) FILTER (WHERE model_tier = 'opus') as opus_calls,
  COUNT(*) FILTER (WHERE fallback_count > 0) as fallback_cases
FROM maestro_runtime_metrics
WHERE timestamp > now() - interval '1 hour'
GROUP BY agent_slug
ORDER BY request_count DESC;

-- 8. Create view for routing quality
CREATE OR REPLACE VIEW maestro_routing_quality AS
SELECT
  DATE(timestamp) as date,
  primary_agent,
  COUNT(*) as total_cases,
  SUM(CASE WHEN is_ambiguous THEN 1 ELSE 0 END) as ambiguous_cases,
  SUM(CASE WHEN user_approved = true THEN 1 ELSE 0 END) as approved_cases,
  SUM(CASE WHEN user_approved = false THEN 1 ELSE 0 END) as rejected_cases,
  AVG(score_gap) as avg_score_gap,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score_gap) as median_gap
FROM maestro_routing_trace
WHERE timestamp > now() - interval '30 days'
GROUP BY DATE(timestamp), primary_agent
ORDER BY date DESC, total_cases DESC;

COMMIT;

-- Note: After applying this migration:
-- 1. Update Maestro router to call insert_maestro_metric() after each dispatch
-- 2. Schedule nightly cron job: SELECT compute_daily_metrics(CURRENT_DATE - interval '1 day')
-- 3. Monitor with views: maestro_metrics_current_hour, maestro_routing_quality
-- 4. Setup alerts on fallback_rate > 5% and latency_p95 > 1000ms
