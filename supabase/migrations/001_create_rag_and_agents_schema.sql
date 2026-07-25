-- Manta Maestro v5.0.0 - RAG e Agent Knowledge Schema
-- Criado: 2026-07-22
-- Propósito: Suporte para 60 agentes com RAG em paralelo

-- ============================================================================
-- 1. TABELA RAG_CHUNKS — Armazenamento de conhecimento por coleção
-- ============================================================================

CREATE TABLE rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_prefix TEXT NOT NULL,
  segment TEXT NOT NULL,
  document_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  source_url TEXT,
  source_type TEXT,
  metadata JSONB DEFAULT '{}',

  -- Validação de conteúdo
  confidence_score NUMERIC(3,2) DEFAULT 0.85,
  validation_status TEXT DEFAULT 'pending',
  validated_by TEXT,
  validated_at TIMESTAMP,

  -- Auditoria
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_updated TIMESTAMP DEFAULT NOW(),

  -- Tags para busca
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],

  CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
  CONSTRAINT valid_validation_status CHECK (validation_status IN ('pending', 'validated', 'rejected')),
  CONSTRAINT valid_collection_prefix CHECK (collection_prefix IN ('san:', 'ene:', 'por:', 'aer:', 'bar:', 'rod:', 'oae:', 'fer:', 'met:'))
);

CREATE INDEX idx_rag_chunks_collection ON rag_chunks(collection_prefix);
CREATE INDEX idx_rag_chunks_segment ON rag_chunks(segment);
CREATE INDEX idx_rag_chunks_document ON rag_chunks(document_id);
CREATE INDEX idx_rag_chunks_validation ON rag_chunks(validation_status);
CREATE INDEX idx_rag_chunks_tags ON rag_chunks USING GIN(tags);

-- ============================================================================
-- 2. TABELA AGENT_KNOWLEDGE_MAPPING — Mapeamento de Acesso RAG por Agente
-- ============================================================================

CREATE TABLE agent_knowledge_mapping (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL UNIQUE,
  agent_name TEXT NOT NULL,
  agent_tier TEXT,
  segment TEXT,
  collection_prefixes TEXT[] DEFAULT ARRAY[]::TEXT[],
  access_level TEXT DEFAULT 'read',

  -- Sincronização
  last_synced TIMESTAMP,
  last_knowledge_update TIMESTAMP,
  knowledge_version TEXT,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT valid_access_level CHECK (access_level IN ('read', 'read_write', 'admin'))
);

CREATE INDEX idx_agent_mapping_agent_id ON agent_knowledge_mapping(agent_id);
CREATE INDEX idx_agent_mapping_segment ON agent_knowledge_mapping(segment);
CREATE INDEX idx_agent_mapping_active ON agent_knowledge_mapping(is_active);

-- ============================================================================
-- 3. TABELA AGENT_EXECUTION_LOG — Rastreamento de Execução em Paralelo
-- ============================================================================

CREATE TABLE agent_execution_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  execution_id TEXT UNIQUE DEFAULT gen_random_uuid()::TEXT,

  -- Status de execução
  status TEXT DEFAULT 'queued',
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_ms INTEGER,

  -- Metadata
  input_prompt TEXT,
  output_summary TEXT,
  error_message TEXT,

  -- Parallelização
  concurrency_batch INTEGER,
  concurrency_weight INTEGER,

  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT valid_status CHECK (status IN ('queued', 'running', 'completed', 'failed', 'timeout'))
);

CREATE INDEX idx_execution_log_agent ON agent_execution_log(agent_id);
CREATE INDEX idx_execution_log_status ON agent_execution_log(status);
CREATE INDEX idx_execution_log_created ON agent_execution_log(created_at);

-- ============================================================================
-- 4. TABELA SHAREPOINT_SYNC_LOG — Rastreamento de Sincronização SP → Supabase
-- ============================================================================

CREATE TABLE sharepoint_sync_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_prefix TEXT NOT NULL,
  segment TEXT NOT NULL,

  -- Arquivo do SharePoint
  sp_file_name TEXT NOT NULL,
  sp_file_path TEXT NOT NULL,
  sp_file_id TEXT UNIQUE,
  sp_last_modified TIMESTAMP,

  -- Sincronização
  sync_status TEXT DEFAULT 'pending',
  synced_at TIMESTAMP,
  chunks_created INTEGER DEFAULT 0,
  chunks_validated INTEGER DEFAULT 0,

  -- Validação
  validation_status TEXT DEFAULT 'pending',
  validation_errors TEXT[],

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT valid_sync_status CHECK (sync_status IN ('pending', 'in_progress', 'completed', 'failed')),
  CONSTRAINT valid_validation_status CHECK (validation_status IN ('pending', 'passed', 'failed'))
);

CREATE INDEX idx_sync_log_collection ON sharepoint_sync_log(collection_prefix);
CREATE INDEX idx_sync_log_status ON sharepoint_sync_log(sync_status);
CREATE INDEX idx_sync_log_created ON sharepoint_sync_log(created_at);

-- ============================================================================
-- 5. TABELA RAG_COLLECTION_STATUS — Status Geral das Coleções
-- ============================================================================

CREATE TABLE rag_collection_status (
  collection_prefix TEXT PRIMARY KEY,
  collection_name TEXT NOT NULL,
  segment TEXT NOT NULL,

  -- Contadores
  total_documents INTEGER DEFAULT 0,
  total_chunks INTEGER DEFAULT 0,
  validated_chunks INTEGER DEFAULT 0,
  pending_chunks INTEGER DEFAULT 0,

  -- Qualidade
  avg_confidence_score NUMERIC(3,2) DEFAULT 0.0,

  -- Atualização
  last_update TIMESTAMP,
  update_frequency TEXT,
  priority TEXT,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 6. TRIGGERS E FUNÇÕES
-- ============================================================================

-- Atualizar timestamp updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_rag_chunks_updated_at
  BEFORE UPDATE ON rag_chunks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_agent_mapping_updated_at
  BEFORE UPDATE ON agent_knowledge_mapping
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_sync_log_updated_at
  BEFORE UPDATE ON sharepoint_sync_log
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_collection_status_updated_at
  BEFORE UPDATE ON rag_collection_status
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. INITIAL DATA — Configuração das Coleções RAG
-- ============================================================================

INSERT INTO rag_collection_status (collection_prefix, collection_name, segment, update_frequency, priority)
VALUES
  ('san:', 'Saneamento', 'S8', 'Mensal', '🔴 ALTA (AYSÁ)'),
  ('ene:', 'Energia', 'S9', 'Semanal', '🔴 ALTA (ANEEL)'),
  ('por:', 'Portos', 'S6', 'Semestral', '🟡 Média'),
  ('aer:', 'Aeroportos', 'S7', 'Semestral', '🟡 Média'),
  ('bar:', 'Barragens', 'S10', 'Trimestral', '🟡 Média');

-- Inicializar mapeamento de agentes horizontais
INSERT INTO agent_knowledge_mapping (agent_id, agent_name, agent_tier, collection_prefixes, access_level)
VALUES
  ('manta-00', 'maestro', 'Haiku→Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'admin'),
  ('manta-01', 'claims', 'Opus', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-02', 'contratual', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-04', 'imobiliario', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-05', 'orcamento', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-06', 'modelagem', 'Sonnet/Opus', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-07', 'cronograma', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-13', 'bd', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-14', 'apresentacoes', 'Sonnet', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-15', 'advisory', 'Sonnet/Opus', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'read'),
  ('manta-16', 'arquiteto-ia', 'Opus', ARRAY['san:', 'ene:', 'por:', 'aer:', 'bar:'], 'admin');

-- Inicializar mapeamento de agentes verticais principais
INSERT INTO agent_knowledge_mapping (agent_id, agent_name, agent_tier, segment, collection_prefixes, access_level)
VALUES
  ('manta-03-s6', 'agente-portos', 'Sonnet', 'S6', ARRAY['por:'], 'read'),
  ('manta-03-s7', 'agente-aeroportos', 'Sonnet', 'S7', ARRAY['aer:'], 'read'),
  ('manta-03-s8', 'agente-saneamento', 'Sonnet', 'S8', ARRAY['san:'], 'read_write'),
  ('manta-03-s9', 'agente-energia', 'Sonnet', 'S9', ARRAY['ene:'], 'read_write'),
  ('manta-03-s10', 'agente-barragens', 'Sonnet', 'S10', ARRAY['bar:'], 'read_write');
