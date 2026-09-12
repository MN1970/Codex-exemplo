-- Maestro OS v6.0 Schema Migration
-- Date: 2026-07-26
-- Purpose: Projects, Decisions, Agent Pool, Consensus tracking

-- ============================================
-- 1. PROJECTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Metadata
  project_name VARCHAR(255) NOT NULL,
  project_type VARCHAR(50) NOT NULL, -- 'porto', 'barragem', 'energia', 'multi_segment'
  location VARCHAR(255),
  budget_range VARCHAR(50), -- '0-50M', '50-250M', '250M+'

  -- Segments & Complexity
  segments TEXT[], -- Array of S codes: ['S6', 'S10', 'S9']
  num_segments INT NOT NULL,
  complexity_level VARCHAR(20), -- 'simple', 'medium', 'complex'

  -- Agent Pool
  agents_detected INT, -- Calculated: N_segments + base_horizontals
  agents_pool TEXT[], -- Array of agent names: ['agente-portos', 'manta-05', ...]
  agents_assigned INT DEFAULT 0,

  -- Execution State
  status VARCHAR(50) DEFAULT 'created', -- 'created', 'fan_out_started', 'consensus_in_progress', 'consolidated', 'error'
  execution_start_at TIMESTAMPTZ,
  execution_end_at TIMESTAMPTZ,
  execution_duration_secs INT,

  -- Token Budget
  token_budget INT, -- Dynamic: 300k–600k based on N_agents
  token_used INT DEFAULT 0,

  -- Audit Trail
  created_by VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Metadata
  input_description TEXT, -- Original user input/project brief
  notes TEXT
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_segments ON projects(segments);
CREATE INDEX idx_projects_complexity ON projects(complexity_level);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- ============================================
-- 2. DECISIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Link to Project
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

  -- Decision Metadata
  aspect VARCHAR(50) NOT NULL, -- 'orçamento', 'cronograma', 'risco', 'contratual'
  dimension VARCHAR(100), -- 'cost_realism', 'critical_path', 'schedule_risk'

  -- Candidates (Agent Proposals)
  candidates JSONB NOT NULL, -- Array: [{agent: 'S6', value: 500M, confidence: 0.85}, ...]

  -- Voting
  voting_rule VARCHAR(50) DEFAULT 'super_majority', -- 'super_majority' (3/5), 'majority' (2/3), 'consensus'
  voters TEXT[], -- Array of agents that voted on this aspect
  num_voters INT,
  threshold_required INT DEFAULT 3, -- Votes needed to pass

  -- Consensus Result
  consensus_result JSONB, -- {value: 'R$ 1.15B', confidence: 0.88, winning_proposal: 'S6'}
  consensus_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'voted', 'decided', 'escalated'
  consensus_confidence FLOAT, -- 0..1

  -- Escalation (if consensus fails)
  escalation_needed BOOLEAN DEFAULT FALSE,
  escalation_to VARCHAR(255), -- Email of person to escalate to
  escalation_reason TEXT,

  -- Audit Trail
  created_at TIMESTAMPTZ DEFAULT NOW(),
  trace_json JSONB, -- Full audit trail of voting process

  CONSTRAINT valid_voters CHECK (array_length(voters, 1) >= 2)
);

CREATE INDEX idx_decisions_project_id ON decisions(project_id);
CREATE INDEX idx_decisions_aspect ON decisions(aspect);
CREATE INDEX idx_decisions_consensus_status ON decisions(consensus_status);
CREATE INDEX idx_decisions_escalation_needed ON decisions(escalation_needed);

-- ============================================
-- 3. AGENT POOL TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS agent_pool (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Agent Definition
  agent_code VARCHAR(50) NOT NULL UNIQUE, -- 'S6', 'S10', 'S9', 'A5', 'A7', 'manta-05'
  agent_name VARCHAR(255) NOT NULL,
  agent_category VARCHAR(20), -- 'vertical' (S1-S11) or 'horizontal' (A1-A10)

  -- Classification
  segment_code VARCHAR(10), -- For verticals: 'S6', 'S10', 'S9', etc.
  activity_code VARCHAR(10), -- For horizontals: 'A5', 'A7', 'A15', etc.

  -- Execution Config
  model_tier VARCHAR(20) DEFAULT 'sonnet', -- 'haiku', 'sonnet', 'opus'
  tool_access TEXT[], -- ['Read', 'Grep', 'Bash', 'WebSearch', ...]
  rag_prefix VARCHAR(10), -- 'por:', 'ene:', 'san:', 'bar:' for verticals

  -- Status
  is_available BOOLEAN DEFAULT TRUE,
  is_deprecated BOOLEAN DEFAULT FALSE,

  -- Metadata
  description TEXT,
  skill_url VARCHAR(255), -- Link to SKILL.md in SharePoint
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_pool_code ON agent_pool(agent_code);
CREATE INDEX idx_agent_pool_category ON agent_pool(agent_category);
CREATE INDEX idx_agent_pool_segment ON agent_pool(segment_code);

-- ============================================
-- 4. CONSENSUS TRACE TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS consensus_trace (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Link
  decision_id UUID NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,

  -- Individual Vote
  agent_name VARCHAR(255) NOT NULL,
  vote_value JSONB, -- Agent's proposal
  vote_confidence FLOAT,
  vote_reasoning TEXT,

  -- Timing
  voted_at TIMESTAMPTZ DEFAULT NOW(),

  -- Trace
  agent_session_id VARCHAR(255), -- Link to agent session for debugging
  trace JSONB -- Full context of agent's reasoning
);

CREATE INDEX idx_consensus_trace_decision_id ON consensus_trace(decision_id);
CREATE INDEX idx_consensus_trace_agent ON consensus_trace(agent_name);

-- ============================================
-- 5. MAESTRO EXECUTION LOG
-- ============================================

CREATE TABLE IF NOT EXISTS maestro_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Workflow Execution
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  workflow_id VARCHAR(255), -- Unique workflow run ID

  -- Phases
  phase_1_fan_out_start TIMESTAMPTZ,
  phase_1_fan_out_end TIMESTAMPTZ,
  phase_1_duration_secs INT,

  phase_2_consensus_start TIMESTAMPTZ,
  phase_2_consensus_end TIMESTAMPTZ,
  phase_2_duration_secs INT,

  phase_3_aggregate_start TIMESTAMPTZ,
  phase_3_aggregate_end TIMESTAMPTZ,
  phase_3_duration_secs INT,

  total_execution_secs INT,

  -- Results
  num_agents_spawned INT,
  num_decisions_made INT,
  num_decisions_auto_resolved INT,
  num_decisions_escalated INT,

  consensus_rate FLOAT, -- (auto_resolved / total) %

  -- Artifacts
  output_docx_path VARCHAR(255),
  output_json_path VARCHAR(255),
  output_matrix_path VARCHAR(255),

  -- Status
  status VARCHAR(50), -- 'success', 'partial', 'error'
  error_message TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_maestro_executions_project_id ON maestro_executions(project_id);
CREATE INDEX idx_maestro_executions_status ON maestro_executions(status);

-- ============================================
-- 6. HELPER FUNCTIONS
-- ============================================

-- Calculate agent pool size based on segments + complexity
CREATE OR REPLACE FUNCTION calculate_agent_pool_size(
  p_num_segments INT,
  p_complexity_level VARCHAR
) RETURNS INT AS $$
DECLARE
  v_base_agents INT := 4; -- A1, A5, A7, A15 minimum
  v_segment_multiplier INT;
BEGIN
  -- Simple: 1 segment → 4 agents
  -- Medium: 2-3 segments → 9 agents
  -- Complex: 4+ segments → all 11 horizontals

  CASE p_complexity_level
    WHEN 'simple' THEN
      v_segment_multiplier := 1;
    WHEN 'medium' THEN
      v_segment_multiplier := 3;
    WHEN 'complex' THEN
      v_segment_multiplier := 5;
    ELSE
      v_segment_multiplier := 0;
  END CASE;

  RETURN p_num_segments + v_segment_multiplier + v_base_agents;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Calculate token budget dynamically
CREATE OR REPLACE FUNCTION calculate_token_budget(
  p_num_agents INT
) RETURNS INT AS $$
BEGIN
  -- 8 agents: 300k
  -- 12 agents: 450k
  -- 16 agents: 600k
  -- Linear scale: 37.5k per agent
  RETURN (p_num_agents * 37500) + 0;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- 7. SEED DATA — Agent Pool
-- ============================================

INSERT INTO agent_pool (
  agent_code, agent_name, agent_category, segment_code,
  model_tier, rag_prefix, description
) VALUES
-- Vertical Agents (S1-S11)
('S1', 'agente-infraestrutura-rodovias', 'vertical', 'S1', 'sonnet', NULL, 'Rodovias: pavimentação, DNIT, SICRO'),
('S2', 'agente-infraestrutura-oae', 'vertical', 'S2', 'sonnet', NULL, 'OAE: pontes, viadutos, NBR 7187'),
('S3', 'agente-infraestrutura-ferrovia', 'vertical', 'S3', 'sonnet', NULL, 'Ferrovia: via permanente, AMV'),
('S4', 'agente-infraestrutura-metro', 'vertical', 'S4', 'sonnet', NULL, 'Metrô: estações, NATM, PSD'),
('S6', 'agente-edificacoes', 'vertical', 'S6', 'sonnet', NULL, 'Edificações: arquitetura, MEP'),
('S7', 'agente-portos', 'vertical', 'S7', 'sonnet', 'por:', 'Portos: ANTAQ, dragagem, terminais'),
('S8', 'agente-aeroportos', 'vertical', 'S8', 'sonnet', 'aer:', 'Aeroportos: ANAC, ICAO, TPS'),
('S9', 'agente-saneamento', 'vertical', 'S9', 'sonnet', 'san:', 'Saneamento: ETA, ETE, Lei 14.026, AySA'),
('S10', 'agente-energia', 'vertical', 'S10', 'sonnet', 'ene:', 'Energia: ANEEL, LT, subestações'),
('S11', 'agente-barragens', 'vertical', 'S11', 'sonnet', 'bar:', 'Barragens: ICOLD, PNSB, rejeitos'),

-- Horizontal Agents (A1-A10)
('A1', 'manta-01-claims', 'horizontal', NULL, 'sonnet', NULL, 'Claims: pleitos, atrasos, imprevistos'),
('A2', 'manta-02-contratual', 'horizontal', NULL, 'sonnet', NULL, 'Contratual: termos, compliance, procurement'),
('A5', 'manta-05-orcamento', 'horizontal', NULL, 'sonnet', NULL, 'Orçamento: composições SICRO, BDI, custos'),
('A6', 'manta-06-modelagem', 'horizontal', NULL, 'sonnet', NULL, 'Modelagem: BIM 3D, FEA, PLAXIS'),
('A7', 'manta-07-cronograma', 'horizontal', NULL, 'sonnet', NULL, 'Cronograma: planning, rota crítica, marcos'),
('A13', 'manta-13-bd', 'horizontal', NULL, 'sonnet', NULL, 'Business Development: parcerias, financiamento'),
('A14', 'manta-14-apresentacoes', 'horizontal', NULL, 'sonnet', NULL, 'Apresentações: PPTX, stakeholders'),
('A15', 'manta-15-advisory', 'horizontal', NULL, 'sonnet', NULL, 'Advisory: modelo financeiro, viabilidade'),
('M00', 'maestro-router', 'horizontal', NULL, 'sonnet', NULL, 'Maestro: roteamento, orquestração, consenso')
ON CONFLICT (agent_code) DO NOTHING;

-- ============================================
-- 8. GRANTS (if using Supabase auth)
-- ============================================

-- Grant access to authenticated users
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE maestro_executions ENABLE ROW LEVEL SECURITY;

-- Allow read all, write own
CREATE POLICY "Projects: select all" ON projects FOR SELECT USING (true);
CREATE POLICY "Projects: insert own" ON projects FOR INSERT WITH CHECK (created_by = current_user_email());
CREATE POLICY "Projects: update own" ON projects FOR UPDATE USING (created_by = current_user_email());

CREATE POLICY "Decisions: select all" ON decisions FOR SELECT USING (true);
CREATE POLICY "Decisions: insert via project" ON decisions FOR INSERT WITH CHECK (
  EXISTS (SELECT 1 FROM projects WHERE id = project_id AND created_by = current_user_email())
);

COMMIT;
