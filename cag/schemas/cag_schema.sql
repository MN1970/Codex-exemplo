-- CAG (Custom Agent Group) — Schema Supabase
-- Ticket: MNT-2026-CAG-ML
-- Data: 2026-07-22

BEGIN;

-- ========================================================================
-- 1. INTENT CLASSIFICATION MODEL
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_intent_models (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL UNIQUE,
    version INT NOT NULL DEFAULT 1,
    model_type VARCHAR(50) NOT NULL, -- 'distilbert', 'claude-embeddings', 'custom'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'training', -- 'training', 'active', 'archived'
    metadata JSONB DEFAULT '{}' -- hyperparams, training_date, accuracy_train, accuracy_val
);

-- ========================================================================
-- 2. AGENT SCORING MATRIX (histórico de hits/misses)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_agent_scores (
    id BIGSERIAL PRIMARY KEY,
    agent_slug VARCHAR(255) NOT NULL, -- ex: 'agente-saneamento'
    query_intent VARCHAR(255) NOT NULL, -- ex: 'saneamento', 'energia', 'ambíguo'
    selected BOOLEAN NOT NULL, -- foi selecionado ou não?
    user_rated BOOLEAN DEFAULT FALSE, -- usuário gave feedback?
    user_rating NUMERIC(3,2) DEFAULT NULL, -- 0-1.0: útil?
    hit BOOLEAN DEFAULT NULL, -- true=correto, false=erro, NULL=desconhecido
    confidence_score NUMERIC(5,3) DEFAULT NULL, -- 0-1.0
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(agent_slug, query_intent)
);

-- ========================================================================
-- 3. FEEDBACK LOG (usuário sinaliza se resposta foi útil)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_feedback_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- rastrear conversação
    query_text TEXT NOT NULL,
    query_intent VARCHAR(255) NOT NULL,
    selected_agents VARCHAR(255)[] NOT NULL, -- agentes que responderam
    ranked_order VARCHAR(255)[] NOT NULL, -- ordem do ranker
    user_rating NUMERIC(3,2) NOT NULL, -- 0-1.0: quanto ajudou?
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================================================
-- 4. ROUTING METRICS (dashboard de acurácia)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_routing_metrics (
    id BIGSERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    total_queries INT DEFAULT 0,
    correct_selections INT DEFAULT 0, -- quantas vezes foi selecionado CERTO
    incorrect_selections INT DEFAULT 0, -- quantas vezes foi selecionado ERRADO
    avg_confidence NUMERIC(5,3) DEFAULT 0.0,
    avg_user_rating NUMERIC(3,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date_bucket, agent_slug)
);

-- ========================================================================
-- 5. AGENT POOL (registro de agentes participantes no CAG)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_agent_pool (
    id BIGSERIAL PRIMARY KEY,
    agent_slug VARCHAR(255) NOT NULL UNIQUE,
    agent_name VARCHAR(255) NOT NULL,
    segment VARCHAR(100) NOT NULL, -- 'rodovia', 'saneamento', 'energia', etc.
    rag_prefix VARCHAR(50) NOT NULL, -- 'rod:', 'san:', 'ene:', etc.
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================================================
-- 6. INTENT CLASSES (mapeamento de intenções)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_intent_classes (
    id BIGSERIAL PRIMARY KEY,
    intent_label VARCHAR(255) NOT NULL UNIQUE, -- 'saneamento', 'energia', etc.
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    primary_agents VARCHAR(255)[] NOT NULL, -- agentes que respondem bem
    secondary_agents VARCHAR(255)[] DEFAULT ARRAY[]::VARCHAR[], -- agentes complementares
    keywords TEXT[] NOT NULL, -- palavras que ativam essa classe
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================================================
-- 7. QUERY CACHE (evitar reprocessar mesma query)
-- ========================================================================

CREATE TABLE IF NOT EXISTS cag_query_cache (
    id BIGSERIAL PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL UNIQUE, -- SHA256(query text)
    query_text TEXT NOT NULL,
    intent_prediction JSONB NOT NULL, -- {intent: 'saneamento', confidence: 0.92, ...}
    selected_agents VARCHAR(255)[] NOT NULL,
    final_response TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

-- ========================================================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================================================

CREATE INDEX idx_cag_agent_scores_agent ON cag_agent_scores(agent_slug);
CREATE INDEX idx_cag_agent_scores_intent ON cag_agent_scores(query_intent);
CREATE INDEX idx_cag_feedback_session ON cag_feedback_logs(session_id);
CREATE INDEX idx_cag_feedback_created ON cag_feedback_logs(created_at);
CREATE INDEX idx_cag_metrics_date ON cag_routing_metrics(date_bucket);
CREATE INDEX idx_cag_intent_classes_intent ON cag_intent_classes(intent_label);
CREATE INDEX idx_cag_query_cache_hash ON cag_query_cache(query_hash);
CREATE INDEX idx_cag_query_cache_expires ON cag_query_cache(expires_at);

-- ========================================================================
-- INITIAL DATA: Intent Classes (padrão para Manta Maestro)
-- ========================================================================

INSERT INTO cag_intent_classes
  (intent_label, display_name, description, primary_agents, secondary_agents, keywords)
VALUES
  (
    'saneamento',
    'Saneamento Básico',
    'Água, esgoto, drenagem urbana, resíduos sólidos',
    ARRAY['agente-saneamento'],
    ARRAY['agente-energia', 'agente-contratual'],
    ARRAY['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto', 'drenagem', 'resíduos', 'AySA', 'SNIS']
  ),
  (
    'energia',
    'Energia',
    'Transmissão, distribuição, geração (hidro, eólica, solar, térmica)',
    ARRAY['agente-energia'],
    ARRAY['agente-barragens', 'agente-contratual'],
    ARRAY['transmissão', 'LT', 'subestação', 'ANEEL', 'geração', 'eólica', 'solar', 'hidráulica', 'UHE']
  ),
  (
    'portos',
    'Portos e Hidrovias',
    'Terminais marítimos, fluviais, dragagem, cais',
    ARRAY['agente-portos'],
    ARRAY['agente-energia', 'agente-contratual'],
    ARRAY['porto', 'terminal', 'ANTAQ', 'dragagem', 'molhe', 'berço', 'calado', 'contêiner', 'granel']
  ),
  (
    'aeroportos',
    'Aeroportos',
    'Pistas, taxiways, terminais, balizamento',
    ARRAY['agente-aeroportos'],
    ARRAY['agente-energia', 'agente-contratual'],
    ARRAY['aeroporto', 'pista', 'RWY', 'taxiway', 'TPS', 'TECA', 'ANAC', 'balizamento']
  ),
  (
    'barragens',
    'Barragens',
    'Concreto, terra, enrocamento, rejeitos',
    ARRAY['agente-barragens'],
    ARRAY['agente-energia', 'agente-contratual'],
    ARRAY['barragem', 'vertedouro', 'CFRD', 'CCR', 'rejeitos', 'TSF', 'PNSB', 'ICOLD']
  ),
  (
    'rodovias',
    'Rodovias',
    'Pavimento, pavimentação, terraplenagem',
    ARRAY['agente-infraestrutura'],
    ARRAY['agente-contratual', 'agente-orcamento'],
    ARRAY['rodovia', 'pavimento', 'CBUQ', 'BGS', 'terraplenagem', 'SICRO', 'DNIT']
  ),
  (
    'ambigu',
    'Ambíguo / Multi-domínio',
    'Consultas que envolvem múltiplos segmentos',
    ARRAY['agente-saneamento', 'agente-energia'],
    ARRAY['agente-contratual'],
    ARRAY[]
  );

-- ========================================================================
-- INITIAL DATA: Agent Pool
-- ========================================================================

INSERT INTO cag_agent_pool
  (agent_slug, agent_name, segment, rag_prefix, is_active)
VALUES
  ('agente-saneamento', 'Saneamento', 'saneamento', 'san:', TRUE),
  ('agente-energia', 'Energia', 'energia', 'ene:', TRUE),
  ('agente-portos', 'Portos', 'portos', 'por:', TRUE),
  ('agente-aeroportos', 'Aeroportos', 'aeroportos', 'aer:', TRUE),
  ('agente-barragens', 'Barragens', 'barragens', 'bar:', TRUE),
  ('agente-infraestrutura', 'Infraestrutura (Rodovias)', 'rodovias', 'rod:', TRUE),
  ('agente-contratual', 'Contratual', 'horizontal', NULL, TRUE),
  ('agente-orcamento', 'Orçamento', 'horizontal', NULL, TRUE);

COMMIT;

-- ========================================================================
-- ROLLBACK (se algo der errado)
-- ========================================================================
-- ROLLBACK;
--
-- DROP TABLE IF EXISTS cag_query_cache CASCADE;
-- DROP TABLE IF EXISTS cag_intent_classes CASCADE;
-- DROP TABLE IF EXISTS cag_agent_pool CASCADE;
-- DROP TABLE IF EXISTS cag_routing_metrics CASCADE;
-- DROP TABLE IF EXISTS cag_feedback_logs CASCADE;
-- DROP TABLE IF EXISTS cag_agent_scores CASCADE;
-- DROP TABLE IF EXISTS cag_intent_models CASCADE;
