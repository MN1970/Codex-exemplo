-- Manta Maestro v5.0.2 — RAG Infrastructure Setup
-- Ticket: MNT-2026-INFRASTRUCTURE-RAG-PGVECTOR
-- Date: 2026-08-08
--
-- This migration creates the foundation for RAG (Retrieval-Augmented Generation)
-- with pgvector embeddings for 5 new segments (S6-S10).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_08_v5_0_2_rag_infrastructure.sql

BEGIN;

-- Enable pgvector extension (required for embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================================
-- 1. RAG Collections Table (if not exists)
-- =====================================================================
-- Stores metadata about each RAG collection (saneamento, energia, etc.)
CREATE TABLE IF NOT EXISTS rag_collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL, -- e.g., 'saneamento', 'energia', 'portos', 'aeroportos', 'barragens'
  name TEXT NOT NULL, -- e.g., 'Saneamento & Água'
  storage_prefix TEXT NOT NULL, -- e.g., 'san:', 'ene:', 'por:', 'aer:', 'bar:'
  description TEXT, -- detailed description of collection scope
  initial_sources JSONB, -- array of source documents/URLs
  embedding_model TEXT DEFAULT 'BAAI/bge-small-en-v1.5', -- default embeddings model
  embedding_dimension INTEGER DEFAULT 384, -- vector size for this collection
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookup by slug
CREATE UNIQUE INDEX IF NOT EXISTS idx_rag_collections_slug ON rag_collections(slug);

-- =====================================================================
-- 2. RAG Chunks Table (main vector storage)
-- =====================================================================
-- Stores document chunks with embeddings for semantic search
CREATE TABLE IF NOT EXISTS rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collection_id UUID NOT NULL REFERENCES rag_collections(id) ON DELETE CASCADE,
  collection_slug TEXT NOT NULL, -- denormalized for query speed
  prefix TEXT, -- e.g., 'san:001', 'ene:045'
  document_title TEXT NOT NULL, -- e.g., 'Lei 14.026/2020', 'ICAO Annex 14'
  document_url TEXT, -- URL to source (if available)
  chunk_index INTEGER, -- sequential chunk number within document (0, 1, 2, ...)
  chunk_text TEXT NOT NULL, -- the actual text to embed and search
  chunk_length INTEGER, -- character count of chunk_text
  embedding vector(384), -- pgvector: 384-dimensional embedding from BAAI/bge-small-en-v1.5
  metadata JSONB, -- flexible metadata: {source_type, language, regulatory_status, keywords, tags, section_number, page_number, etc.}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection_slug ON rag_chunks(collection_slug);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_document_title ON rag_chunks(document_title);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_metadata_keywords ON rag_chunks USING GIN(metadata -> 'keywords');
-- Vector index for similarity search (IVFFlat is most performant for <1M rows)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =====================================================================
-- 3. RAG Learning Log Table
-- =====================================================================
-- Tracks query performance and learning metrics for autoscaling optimization
CREATE TABLE IF NOT EXISTS rag_learning_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  query_text TEXT, -- the user's question
  query_tokens INTEGER, -- token count of query
  collection_slug TEXT, -- which collection was queried (e.g., 'saneamento')
  chunks_retrieved INTEGER, -- how many chunks returned
  top_k_similarity FLOAT[], -- top similarity scores (for relevance tracking)
  response_model TEXT, -- which agent model was used (Haiku, Sonnet, Opus)
  response_tokens INTEGER, -- token count of response
  wall_clock_seconds NUMERIC(8, 2), -- actual wall-clock time
  status TEXT, -- 'success', 'partial', 'failed'
  user_feedback TEXT, -- 0–5 stars or comment (future: human feedback loop)
  metadata JSONB -- flexible: {volume_band, complexity, pattern, cost_usd, etc.}
);

-- Index for analytics (query by collection + status)
CREATE INDEX IF NOT EXISTS idx_rag_learning_log_collection ON rag_learning_log(collection_slug);
CREATE INDEX IF NOT EXISTS idx_rag_learning_log_timestamp ON rag_learning_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_rag_learning_log_status ON rag_learning_log(status);

-- =====================================================================
-- 4. SharePoint Agent Routing Table (if not exists)
-- =====================================================================
-- Maps agents to SharePoint folders for automatic document discovery
CREATE TABLE IF NOT EXISTS sp_agent_routing (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug TEXT UNIQUE NOT NULL, -- e.g., 'agente-saneamento', 'agente-energia'
  sp_folder TEXT NOT NULL, -- SharePoint path, e.g., '03_Projetos/Saneamento/*'
  file_patterns TEXT[] NOT NULL, -- glob patterns, e.g., ARRAY['*.pdf', '*.dwg', '*.xlsx']
  priority INTEGER DEFAULT 100, -- higher = processes first
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sp_agent_routing_slug ON sp_agent_routing(agent_slug);
CREATE INDEX IF NOT EXISTS idx_sp_agent_routing_priority ON sp_agent_routing(priority DESC);

-- =====================================================================
-- 5. Maestro Routing Keywords Table (optional)
-- =====================================================================
-- Stores routing keywords for the Maestro (Manta 00) router
-- Can be loaded from CLAUDE.md or stored here for fast lookup
CREATE TABLE IF NOT EXISTS maestro_routing_keywords (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug TEXT NOT NULL, -- e.g., 'agente-saneamento'
  keyword TEXT NOT NULL, -- e.g., 'saneamento', 'ETA', 'SNIS'
  priority INTEGER DEFAULT 100, -- higher = stronger signal for routing
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(agent_slug, keyword)
);

CREATE INDEX IF NOT EXISTS idx_maestro_keywords_agent ON maestro_routing_keywords(agent_slug);
CREATE INDEX IF NOT EXISTS idx_maestro_keywords_keyword ON maestro_routing_keywords(keyword);

-- =====================================================================
-- 6. Embeddings Cache Table (optional optimization)
-- =====================================================================
-- For frequently queried chunks, cache embeddings to avoid recomputation
CREATE TABLE IF NOT EXISTS embeddings_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  text_hash TEXT UNIQUE NOT NULL, -- SHA256 of text (to detect duplicates)
  embedding vector(384), -- cached embedding
  model TEXT DEFAULT 'BAAI/bge-small-en-v1.5',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_cache_hash ON embeddings_cache(text_hash);

-- =====================================================================
-- 7. Insert RAG Collections (5 new segments: S6-S10)
-- =====================================================================
INSERT INTO rag_collections (slug, name, storage_prefix, description, initial_sources, embedding_model, embedding_dimension)
VALUES
  ('saneamento', 'Saneamento & Água', 'san:',
   'Water supply, wastewater treatment, urban drainage. Regulatory: Lei 14.026/2020, SNIS, NBR 12211-12218.',
   jsonb_build_array(
     'Lei 14.026/2020', 'Lei 11.445/2007', 'SNIS Database (2000-2024)',
     'PNSB (Plano Nacional Saneamento Básico)', 'ANA Resoluções', 'BNDES Editais',
     'NBR 12211', 'NBR 12212', 'NBR 12217', 'CONAMA 357/2005', 'IWA Standards'
   ),
   'BAAI/bge-small-en-v1.5', 384),

  ('energia', 'Energia Elétrica (Transmissão)', 'ene:',
   'High-voltage transmission lines (LT ≥69 kV), substations. Regulatory: ANEEL, Lei 10.433/2002, Decreto 5.163/2004.',
   jsonb_build_array(
     'Lei 10.433/2002', 'Decreto 5.163/2004', 'Resolução ANEEL 963/2023',
     'EPE Planos R1-R5', 'ONS Relatórios', 'NBR 5422', 'NBR 6979',
     'IEC 60826', 'IEEE Std 738', 'CIGRÉ Technical Brochures'
   ),
   'BAAI/bge-small-en-v1.5', 384),

  ('portos', 'Terminais Portuários', 'por:',
   'Port infrastructure (quays, channels, dredging) and terminal operations. Regulatory: ANTAQ, Lei 12.815/2013.',
   jsonb_build_array(
     'Lei 12.815/2013', 'Lei 13.886/2019', 'Resolução ANTAQ 1/2003',
     'ANTAQ Database', 'NBR 9782', 'NBR 6122', 'ROM 0.2', 'ROM 2.0',
     'PIANC Guidelines', 'ANTAQ Tarifas', 'Portos Referência (Santos, Paranaguá)'
   ),
   'BAAI/bge-small-en-v1.5', 384),

  ('aeroportos', 'Infraestrutura Aeroportuária', 'aer:',
   'Airport runways, terminals, navigation systems. Regulatory: ANAC, Lei 11.182/2005, ICAO Annex 14.',
   jsonb_build_array(
     'Lei 11.182/2005', 'Lei 13.319/2016', 'Resolução ANAC 1/2008',
     'ICAO Annex 14', 'ICAO Doc 9157', 'FAA AC 150/5300-13',
     'FAA AC 150/5320-5', 'NBR 14001', 'RBAC (Partes 121, 139)',
     'Aeroportos Referência (GRU, GIG, SBMG)'
   ),
   'BAAI/bge-small-en-v1.5', 384),

  ('barragens', 'Barragens & Segurança', 'bar:',
   'Dams (hydropower, water supply, tailings). Regulatory: Lei 12.334/2010, Lei 14.066/2020, ANM, ANA.',
   jsonb_build_array(
     'Lei 12.334/2010', 'Lei 14.066/2020', 'Resolução ANA 886/2017',
     'Resolução ANM 04/2020', 'NBR 13028', 'NBR 8681',
     'SIGBM Database (ANM)', 'SNISB Database (ANA)', 'ICOLD Bulletins',
     'CBDB Cadernos Técnicos', 'Usinas ANEEL', 'Estudos de Caso Internacionais'
   ),
   'BAAI/bge-small-en-v1.5', 384)
ON CONFLICT (slug) DO NOTHING;

-- =====================================================================
-- 8. Insert SharePoint Routing Rules (5 new segments)
-- =====================================================================
INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('agente-saneamento',  '03_Projetos/Saneamento/*',  ARRAY['*.pdf','*.dwg','*.xlsx','*.docx'], 100),
  ('agente-energia',     '03_Projetos/Energia/*',     ARRAY['*.pdf','*.dwg','*.xlsx','*.docx'], 100),
  ('agente-portos',      '03_Projetos/Portos/*',      ARRAY['*.pdf','*.dwg','*.xlsx','*.docx'], 100),
  ('agente-aeroportos',  '03_Projetos/Aeroportos/*',  ARRAY['*.pdf','*.dwg','*.xlsx','*.docx'], 100),
  ('agente-barragens',   '03_Projetos/Barragens/*',   ARRAY['*.pdf','*.dwg','*.xlsx','*.docx'], 100)
ON CONFLICT (agent_slug) DO NOTHING;

-- =====================================================================
-- 9. Insert Maestro Routing Keywords (5 new segments)
-- =====================================================================
INSERT INTO maestro_routing_keywords (agent_slug, keyword, priority) VALUES
  -- Saneamento (S8)
  ('agente-saneamento', 'saneamento',        100),
  ('agente-saneamento', 'ETA',               100),
  ('agente-saneamento', 'ETE',               100),
  ('agente-saneamento', 'adutora',           100),
  ('agente-saneamento', 'esgoto',            100),
  ('agente-saneamento', 'AySA',              120),
  ('agente-saneamento', 'drenagem urbana',    95),
  ('agente-saneamento', 'SNIS',              100),
  -- Energia (S9)
  ('agente-energia',    'transmissão',       100),
  ('agente-energia',    'LT',                 90),
  ('agente-energia',    'subestação',        100),
  ('agente-energia',    'ANEEL',             100),
  ('agente-energia',    'RAP',                90),
  ('agente-energia',    'leilão transmissão', 95),
  ('agente-energia',    'ONS',                90),
  ('agente-energia',    'EPE',                90),
  -- Portos (S6)
  ('agente-portos',     'porto',              80),
  ('agente-portos',     'terminal',           70),
  ('agente-portos',     'ANTAQ',             100),
  ('agente-portos',     'dragagem',          100),
  ('agente-portos',     'molhe',             100),
  ('agente-portos',     'berço',              90),
  ('agente-portos',     'calado',             90),
  ('agente-portos',     'contêiner',          80),
  ('agente-portos',     'granel',             80),
  -- Aeroportos (S7)
  ('agente-aeroportos', 'aeroporto',         100),
  ('agente-aeroportos', 'pista pouso',       100),
  ('agente-aeroportos', 'ANAC',              100),
  ('agente-aeroportos', 'ICAO',              100),
  ('agente-aeroportos', 'TPS',                90),
  ('agente-aeroportos', 'TECA',               90),
  ('agente-aeroportos', 'balizamento',       100),
  -- Barragens (S10)
  ('agente-barragens',  'barragem',          100),
  ('agente-barragens',  'vertedouro',        100),
  ('agente-barragens',  'CFRD',              100),
  ('agente-barragens',  'CCR',                80),
  ('agente-barragens',  'rejeitos',          110),
  ('agente-barragens',  'PNSB',              100),
  ('agente-barragens',  'ICOLD',             100),
  ('agente-barragens',  'CBDB',              100),
  ('agente-barragens',  'TSF',               100)
ON CONFLICT (agent_slug, keyword) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (if needed, execute manually)
-- =====================================================================
-- BEGIN;
--
-- DROP TABLE IF EXISTS maestro_routing_keywords;
-- DROP TABLE IF EXISTS sp_agent_routing;
-- DROP TABLE IF EXISTS embeddings_cache;
-- DROP TABLE IF EXISTS rag_learning_log;
-- DROP TABLE IF EXISTS rag_chunks;
-- DROP TABLE IF EXISTS rag_collections;
-- DROP EXTENSION IF EXISTS vector;
--
-- COMMIT;
