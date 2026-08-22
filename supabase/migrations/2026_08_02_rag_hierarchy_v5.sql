-- =====================================================================
-- Manta Maestro v5.0 — RAG Hierarchy: rag_chunks table
-- Ticket: MNT-2026-RAG-HIERARCHY-V5
--
-- Implements RAG metadata schema for 5 collections:
-- - saneamento (SNIS, NBR, Lei 14.026, BNDES)
-- - energia (ANEEL, EPE, ONS, IEEE)
-- - portos (ANTAQ, PIANC, BNDES)
-- - barragens (ICOLD, CBDB, Lei 12.334)
-- - editais (cross-segmento: licitações templates, tenders)
--
-- Features:
-- - pgvector embeddings (384d: BAAI/bge-small-en-v1.5)
-- - Multi-factor metadata (confidence, citation_count, recency, domain_tags)
-- - Full-text search (Portuguese) + HNSW semantic search
-- - BRIN index for append-only ingested_at timeline
-- =====================================================================

BEGIN;

-- Create pgvector extension if not already present
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================================
-- Main RAG chunks table
-- =====================================================================

CREATE TABLE IF NOT EXISTS rag_chunks (
  -- Primary identifiers
  chunk_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id       TEXT NOT NULL,
  source_collection TEXT NOT NULL,

  -- Validate source_collection against 5 allowed values
  CONSTRAINT chk_source_collection CHECK (
    source_collection IN ('saneamento', 'energia', 'portos', 'barragens', 'editais')
  ),

  -- Content & semantic embeddings
  text              TEXT NOT NULL,
  embedding         vector(384),          -- BAAI/bge-small-en-v1.5 (384 dims)
  embedding_model   TEXT DEFAULT 'BAAI/bge-small-en-v1.5',

  -- Provenance: source document metadata
  source_document_title       TEXT NOT NULL,
  source_document_type        TEXT NOT NULL,
  source_url                  TEXT,
  source_organization         TEXT,

  -- Validate source_document_type
  CONSTRAINT chk_source_document_type CHECK (
    source_document_type IN ('regulation', 'tender', 'edital', 'standard', 'guide', 'case_study')
  ),

  -- Domain tagging: topic keywords (multi-valued)
  domain_tags       TEXT[] NOT NULL DEFAULT '{}',

  -- Segment codes: which infrastructure segments this chunk applies to
  -- S6: Portos, S7: Aeroportos, S8: Saneamento, S9: Energia, S10: Barragens
  segment_codes     TEXT[] NOT NULL DEFAULT '{}',
  CONSTRAINT chk_segment_codes CHECK (
    segment_codes <@ ARRAY['S6','S7','S8','S9','S10']::TEXT[]
  ),

  -- Lifecycle phases: which project phases this chunk applies to (1-8)
  -- 1=estudo prévio, 2=projeto básico, 3=projeto executivo, 4=obra em execução,
  -- 5=operação & manutenção, 6=licitação, 7=due diligence, 8=encerramento
  lifecycle_phases  SMALLINT[] NOT NULL DEFAULT ARRAY[1,2,3,4,5,6,7,8]::SMALLINT[],
  CONSTRAINT chk_lifecycle_phases CHECK (
    lifecycle_phases <@ ARRAY[1,2,3,4,5,6,7,8]::SMALLINT[]
  ),

  -- Recency signals: when is this chunk fresh/current?
  published_date    DATE,                 -- Original publication date
  ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now(),  -- When added to RAG
  last_updated_at   TIMESTAMPTZ,          -- When chunk last refreshed
  currency_status   TEXT NOT NULL DEFAULT 'current',
  CONSTRAINT chk_currency_status CHECK (
    currency_status IN ('current', 'draft', 'superseded', 'historical')
  ),

  -- Reliability & confidence signals
  confidence        NUMERIC(3,2) NOT NULL DEFAULT 0.5,
  CONSTRAINT chk_confidence CHECK (confidence BETWEEN 0 AND 1),

  citation_count    INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT chk_citation_count CHECK (citation_count >= 0),

  relevance_feedback_score NUMERIC(3,2),
  CONSTRAINT chk_relevance_feedback CHECK (
    relevance_feedback_score IS NULL OR relevance_feedback_score BETWEEN -1 AND 1
  ),

  -- Operational: position in source document (for coherence/context)
  chunk_order       INTEGER,
  window_size       INTEGER,

  -- Audit timestamps
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- Indexes: optimized for RAG query patterns
-- =====================================================================

-- Collection-based filtering
CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection
  ON rag_chunks (source_collection);

-- Currency filtering (only 'current' documents in most queries)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_currency
  ON rag_chunks (currency_status)
  WHERE currency_status = 'current';

-- Domain tag filtering (multi-valued)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_domain_tags
  ON rag_chunks USING GIN (domain_tags);

-- Segment code filtering
CREATE INDEX IF NOT EXISTS idx_rag_chunks_segment_codes
  ON rag_chunks USING GIN (segment_codes);

-- Organization filtering (SNIS, ANEEL, ANTAQ, ICOLD, etc.)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_source_org
  ON rag_chunks (source_organization);

-- Semantic search: HNSW index on embeddings
-- Uses vector_cosine_ops (cosine distance); supports k-NN queries
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding
  ON rag_chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE embedding IS NOT NULL;

-- Recency index: BRIN (append-only, time-ordered)
-- Supports fast filtering by ingested_at window
CREATE INDEX IF NOT EXISTS idx_rag_chunks_ingested_brin
  ON rag_chunks USING BRIN (ingested_at)
  WITH (pages_per_range = 128);

-- Full-text search: Portuguese language
-- Generated column for tsvector; auto-updated on INSERT/UPDATE
ALTER TABLE rag_chunks
  ADD COLUMN IF NOT EXISTS text_fts tsvector
    GENERATED ALWAYS AS (
      to_tsvector('portuguese', text)
    ) STORED;

CREATE INDEX IF NOT EXISTS idx_rag_chunks_text_fts
  ON rag_chunks USING GIN (text_fts);

-- Combined index for multi-collection summary queries
CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection_currency
  ON rag_chunks (source_collection, currency_status);

-- =====================================================================
-- View: summary statistics per collection (for monitoring)
-- =====================================================================

CREATE OR REPLACE VIEW rag_chunks_stats AS
SELECT
  source_collection,
  COUNT(*) as total_chunks,
  COUNT(*) FILTER (WHERE currency_status = 'current') as current_chunks,
  COUNT(*) FILTER (WHERE currency_status = 'superseded') as superseded_chunks,
  COUNT(*) FILTER (WHERE embedding IS NOT NULL) as chunks_with_embedding,
  COUNT(DISTINCT document_id) as unique_documents,
  COUNT(DISTINCT source_organization) as unique_sources,
  ROUND(AVG(confidence)::NUMERIC, 3) as avg_confidence,
  MAX(citation_count) as max_citations,
  MAX(ingested_at) as last_ingested_at
FROM rag_chunks
GROUP BY source_collection;

COMMENT ON VIEW rag_chunks_stats IS
  'Summary statistics per RAG collection: useful for monitoring indexing progress and quality metrics.';

-- =====================================================================
-- Function: refresh chunk relevance feedback (Bayesian learning)
-- =====================================================================

CREATE OR REPLACE FUNCTION update_chunk_feedback(
  p_chunk_id UUID,
  p_feedback_score NUMERIC
)
RETURNS void AS $$
BEGIN
  -- Update feedback score with exponential moving average (EMA)
  -- Weights: 70% old score, 30% new feedback
  UPDATE rag_chunks
  SET
    relevance_feedback_score =
      COALESCE(relevance_feedback_score, 0) * 0.7 + p_feedback_score * 0.3,
    updated_at = now()
  WHERE chunk_id = p_chunk_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- Trigger: auto-update timestamp on chunk modification
-- =====================================================================

CREATE OR REPLACE FUNCTION rag_chunks_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_rag_chunks_timestamp ON rag_chunks;
CREATE TRIGGER trigger_rag_chunks_timestamp
  BEFORE UPDATE ON rag_chunks
  FOR EACH ROW
  EXECUTE FUNCTION rag_chunks_update_timestamp();

-- =====================================================================
-- Grant permissions (adjust for your Supabase setup)
-- =====================================================================

GRANT SELECT ON rag_chunks TO authenticated;
GRANT INSERT, UPDATE ON rag_chunks TO service_role;
GRANT SELECT ON rag_chunks_stats TO authenticated;

-- =====================================================================
-- Seed data: example chunks for testing (optional)
-- Uncomment to populate with sample data
-- =====================================================================

/*
INSERT INTO rag_chunks (
  document_id, source_collection, text, source_document_title,
  source_document_type, source_organization, domain_tags,
  segment_codes, confidence, citation_count, currency_status
) VALUES
  (
    'snis-nbr-12211-excerpt-001',
    'saneamento',
    'NBR 12211:2018 defines the design criteria for water supply systems with adduction distances up to 100 km.
     For adduction > 100 km, use BEB (Bombas de Êmbolo Betonadas) or investigate pressure vessel design per NBR 8883.',
    'NBR 12211:2018 — Projeto de adutoras de água para abastecimento público',
    'standard',
    'ABNT',
    ARRAY['adução', 'dimensionamento', 'abastecimento', 'NBR-12211'],
    ARRAY['S8'],
    0.95,
    12,
    'current'
  ),
  (
    'aneel-edital-2024-lt-765kv',
    'energia',
    'ANEEL 2024 transmission licititation process: LT 765 kV requires joint authority from ANEEL + EPE.
     Initial authorization → 24 months for EIS + basic project → public hearing → 36 months for executive project.
     Total timeline: 5-7 years before energization.',
    'ANEEL Edital de Licitação: LT 765 kV Região Sudeste 2024',
    'edital',
    'ANEEL',
    ARRAY['transmissão', 'licitação', 'LT', 'ANEEL', 'planejamento'],
    ARRAY['S9'],
    0.92,
    8,
    'current'
  ),
  (
    'antaq-porto-capacidade-berco',
    'portos',
    'ANTAQ regulation: berço (dock position) capacity for container terminal calculated as:
     Capacity (TEU/year) = (Berth length in m) × (Ship turnaround time in days) × (Avg ship size in TEU) × 0.85.
     Typical berth: 400m length, 28-day turnaround → 450k-600k TEU/year for Panamax vessels.',
    'ANTAQ Guia: Planejamento de Capacidade em Terminais de Contêineres',
    'guide',
    'ANTAQ',
    ARRAY['porto', 'contêiner', 'capacidade', 'berço', 'planejamento'],
    ARRAY['S6'],
    0.88,
    5,
    'current'
  ),
  (
    'icold-barragem-altura-concreto',
    'barragens',
    'ICOLD Guidelines on concrete dams: maximum height depends on foundation conditions and internal drainage design.
     With adequate internal drainage + grouting: up to 260m height documented. Without internal drainage: 180m max.
     Safety factor on stress: minimum 1.5 (static load), 1.2 (seismic).',
    'ICOLD Bulletin: Concrete Dam Design and Construction',
    'standard',
    'ICOLD',
    ARRAY['barragem', 'concreto', 'altura', 'drenagem', 'segurança'],
    ARRAY['S10'],
    0.91,
    15,
    'current'
  ),
  (
    'bndes-edital-saneamento-prazos-2024',
    'editais',
    'BNDES 2024 sanitation tender: submission period open until 30-Jun-2024 for basic project stage.
     Evaluation: 120 days. Award announcement: 60 days after evaluation.
     Financial close: 180 days after award. Total: 360-day cycle from opening to first disbursement.',
    'BNDES Seleção Pública: Saneamento Integrado AySA 2024',
    'edital',
    'BNDES',
    ARRAY['licitação', 'saneamento', 'prazos', 'AySA', 'BNDES'],
    ARRAY['S8'],
    0.94,
    6,
    'current'
  );
*/

COMMIT;

-- =====================================================================
-- ROLLBACK (if needed)
-- =====================================================================

/*
BEGIN;

DROP VIEW IF EXISTS rag_chunks_stats;
DROP TRIGGER IF EXISTS trigger_rag_chunks_timestamp ON rag_chunks;
DROP FUNCTION IF EXISTS rag_chunks_update_timestamp();
DROP FUNCTION IF EXISTS update_chunk_feedback(UUID, NUMERIC);
DROP INDEX IF EXISTS idx_rag_chunks_text_fts;
DROP INDEX IF EXISTS idx_rag_chunks_collection_currency;
DROP INDEX IF EXISTS idx_rag_chunks_ingested_brin;
DROP INDEX IF EXISTS idx_rag_chunks_embedding;
DROP INDEX IF EXISTS idx_rag_chunks_source_org;
DROP INDEX IF EXISTS idx_rag_chunks_segment_codes;
DROP INDEX IF EXISTS idx_rag_chunks_domain_tags;
DROP INDEX IF EXISTS idx_rag_chunks_currency;
DROP INDEX IF EXISTS idx_rag_chunks_collection;
DROP TABLE IF EXISTS rag_chunks;

COMMIT;
*/
