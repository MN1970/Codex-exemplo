-- Migration: User Feedback and Learning Loop for Maestro Routing
-- Purpose: Track user approvals and enable continuous improvement of routing keywords
-- Date: 2026-07-26

BEGIN;

-- 1. User feedback table (user approves/rejects routing decision)
CREATE TABLE IF NOT EXISTS maestro_user_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamp DEFAULT now(),

  -- Reference to routing trace
  routing_trace_id uuid UNIQUE REFERENCES maestro_routing_trace(id) ON DELETE CASCADE,

  -- The feedback signal
  approved boolean NOT NULL,  -- user approved agent selection
  confidence int DEFAULT NULL, -- 1-5 scale: how confident was the approval
  notes text DEFAULT NULL,    -- optional user comment

  -- Context
  session_id text NULL,
  user_id text NULL,
  user_agent text DEFAULT NULL,

  -- Action taken
  was_actioned boolean DEFAULT false,
  action_type text DEFAULT NULL, -- 'keyword_adjustment', 'agent_escalation', 'none'
  action_description text DEFAULT NULL,

  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_maestro_user_feedback_routing
  ON maestro_user_feedback(routing_trace_id);

CREATE INDEX IF NOT EXISTS idx_maestro_user_feedback_timestamp
  ON maestro_user_feedback(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_user_feedback_approved
  ON maestro_user_feedback(approved, timestamp DESC);

-- 2. Routing keywords (dynamic, updates based on feedback)
CREATE TABLE IF NOT EXISTS maestro_routing_keywords (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  agent_slug text NOT NULL,
  keyword text NOT NULL,

  -- Scoring
  confidence float DEFAULT 0.5, -- 0-1: how confident this keyword → agent
  frequency int DEFAULT 0,      -- how many times has user approved this route
  last_approved timestamp DEFAULT NULL,

  -- Source
  source text DEFAULT 'manual', -- 'manual' or 'feedback_learning'
  feedback_count int DEFAULT 0, -- how many positive feedback signals

  -- Lifecycle
  active boolean DEFAULT true,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_maestro_routing_keywords_unique
  ON maestro_routing_keywords(agent_slug, keyword);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_keywords_agent
  ON maestro_routing_keywords(agent_slug, confidence DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_keywords_active
  ON maestro_routing_keywords(active)
  WHERE active = true;

-- 3. Feedback analysis (aggregate metrics)
CREATE TABLE IF NOT EXISTS maestro_feedback_analysis (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_date date NOT NULL,

  -- Per agent
  agent_slug text NOT NULL,

  -- Approval metrics
  total_feedback int DEFAULT 0,
  approved_count int DEFAULT 0,
  approval_rate float DEFAULT 0.0, -- 0-1

  -- Confidence signals
  high_confidence_approvals int DEFAULT 0, -- score 4-5
  avg_confidence float DEFAULT 0.0,

  -- Improvement signals
  rejected_count int DEFAULT 0,
  most_rejected_keyword text DEFAULT NULL,
  common_wrong_agents text[] DEFAULT NULL,

  -- Recommended actions
  recommend_keyword_boost text DEFAULT NULL,
  recommend_keyword_demotion text DEFAULT NULL,
  recommend_fallback_agent text DEFAULT NULL,

  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_maestro_feedback_analysis_unique
  ON maestro_feedback_analysis(analysis_date, agent_slug);

-- 4. A/B Testing infrastructure (for routing improvements)
CREATE TABLE IF NOT EXISTS maestro_routing_ab_tests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Test metadata
  test_name text NOT NULL,
  test_slug text UNIQUE NOT NULL,
  description text DEFAULT NULL,

  -- Configuration
  variant_a_prompt text NOT NULL, -- original keywords
  variant_b_prompt text NOT NULL, -- new/optimized keywords

  control_rate float DEFAULT 0.9, -- 90% on variant A
  treatment_rate float DEFAULT 0.1, -- 10% on variant B

  -- Status
  status text DEFAULT 'draft', -- draft, active, paused, completed
  started_at timestamp DEFAULT NULL,
  ended_at timestamp DEFAULT NULL,

  -- Metrics collection
  variant_a_samples int DEFAULT 0,
  variant_a_approval_rate float DEFAULT 0.0,
  variant_b_samples int DEFAULT 0,
  variant_b_approval_rate float DEFAULT 0.0,

  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_ab_tests_status
  ON maestro_routing_ab_tests(status, started_at DESC);

-- 5. Function to process feedback and update keywords
CREATE OR REPLACE FUNCTION process_routing_feedback(
  p_routing_trace_id uuid,
  p_approved boolean,
  p_confidence int DEFAULT 3
)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_trace maestro_routing_trace;
  v_feedback_id uuid;
  v_keyword text;
BEGIN
  -- Get the routing trace
  SELECT * INTO v_trace FROM maestro_routing_trace WHERE id = p_routing_trace_id;

  IF v_trace.id IS NULL THEN
    RAISE EXCEPTION 'Routing trace not found';
  END IF;

  -- Insert feedback record
  INSERT INTO maestro_user_feedback (
    routing_trace_id,
    approved,
    confidence
  ) VALUES (
    p_routing_trace_id,
    p_approved,
    p_confidence
  ) RETURNING id INTO v_feedback_id;

  -- Update routing trace with feedback
  UPDATE maestro_routing_trace
  SET user_approved = p_approved
  WHERE id = p_routing_trace_id;

  -- If approved, boost confidence of matching keywords
  IF p_approved THEN
    -- Extract keywords from prompt and boost agent's confidence
    UPDATE maestro_routing_keywords
    SET
      confidence = LEAST(1.0, confidence + 0.05),
      frequency = frequency + 1,
      last_approved = now(),
      feedback_count = feedback_count + 1,
      updated_at = now()
    WHERE agent_slug = v_trace.primary_agent
      AND active = true
      AND keyword <> ANY(string_to_array(lower(v_trace.prompt), ' '));
  ELSE
    -- If rejected, reduce confidence for this agent on these keywords
    UPDATE maestro_routing_keywords
    SET
      confidence = GREATEST(0.1, confidence - 0.10),
      updated_at = now()
    WHERE agent_slug = v_trace.primary_agent
      AND active = true;
  END IF;

  RETURN v_feedback_id;
END;
$$;

-- 6. Function to recommend keyword adjustments (runs weekly)
CREATE OR REPLACE FUNCTION analyze_feedback_and_recommend(
  p_analysis_date date DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  agent_slug text,
  recommendation text,
  priority text,
  affected_feedback_count int
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH feedback_stats AS (
    SELECT
      rt.primary_agent,
      uf.approved,
      COUNT(*) as count,
      ARRAY_AGG(DISTINCT rt.primary_agent) as alt_agents
    FROM maestro_user_feedback uf
    JOIN maestro_routing_trace rt ON uf.routing_trace_id = rt.id
    WHERE DATE(uf.timestamp) = p_analysis_date
    GROUP BY rt.primary_agent, uf.approved
  )
  SELECT
    fs.primary_agent::text,
    (CASE
      WHEN fs.approved = false AND fs.count > 5 THEN
        'Review and demote keywords for ' || fs.primary_agent ||
        ' (rejected ' || fs.count || 'x today)'
      WHEN fs.approved = true AND fs.count > 20 THEN
        'Boost keywords for ' || fs.primary_agent ||
        ' (approved ' || fs.count || 'x with high confidence)'
      ELSE NULL
    END)::text,
    (CASE
      WHEN fs.approved = false AND fs.count > 10 THEN 'HIGH'
      WHEN fs.approved = true AND fs.count > 20 THEN 'MEDIUM'
      ELSE 'LOW'
    END)::text,
    fs.count::int
  FROM feedback_stats fs
  WHERE (fs.approved = false AND fs.count >= 3) OR (fs.approved = true AND fs.count >= 15)
  ORDER BY fs.count DESC;
END;
$$;

COMMIT;

-- Note: After applying this migration:
-- 1. Seed maestro_routing_keywords from CLAUDE.md routing rules
-- 2. Integrate insert_maestro_feedback() calls in Cowork feedback button
-- 3. Schedule weekly: SELECT * FROM analyze_feedback_and_recommend(CURRENT_DATE - interval '1 day')
-- 4. Create GitHub issues from recommendations
