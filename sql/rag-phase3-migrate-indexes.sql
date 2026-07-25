-- ============================================================================
-- RAG PHASE 3 — INDEX MIGRATIONS
-- Cria índices fulltext e vector para otimizar buscas
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================================================
-- FULLTEXT INDEXES (5 collections)
-- ============================================================================

-- Saneamento (S8) — Collection: san:
CREATE INDEX IF NOT EXISTS idx_rag_san_fulltext
ON rag_chunks USING GIN(to_tsvector('portuguese', content))
WHERE collection_prefix = 'san:';

-- Energia (S9) — Collection: ene:
CREATE INDEX IF NOT EXISTS idx_rag_ene_fulltext
ON rag_chunks USING GIN(to_tsvector('portuguese', content))
WHERE collection_prefix = 'ene:';

-- Portos (S6) — Collection: por:
CREATE INDEX IF NOT EXISTS idx_rag_por_fulltext
ON rag_chunks USING GIN(to_tsvector('portuguese', content))
WHERE collection_prefix = 'por:';

-- Aeroportos (S7) — Collection: aer:
CREATE INDEX IF NOT EXISTS idx_rag_aer_fulltext
ON rag_chunks USING GIN(to_tsvector('portuguese', content))
WHERE collection_prefix = 'aer:';

-- Barragens (S10) — Collection: bar:
CREATE INDEX IF NOT EXISTS idx_rag_bar_fulltext
ON rag_chunks USING GIN(to_tsvector('portuguese', content))
WHERE collection_prefix = 'bar:';

-- ============================================================================
-- VECTOR EMBEDDING COLUMN (if not exists)
-- ============================================================================

DO $$
BEGIN
  IF NOT EXISTS(
    SELECT 1 FROM information_schema.columns
    WHERE table_name='rag_chunks' AND column_name='embedding'
  ) THEN
    ALTER TABLE rag_chunks ADD COLUMN embedding vector(1536);
  END IF;
END
$$;

-- ============================================================================
-- VECTOR INDEXES (3 partitions for parallel indexing)
-- ============================================================================

-- Vector Index 1: Chunks 1-200
CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_1
ON rag_chunks USING hnsw (embedding vector_cosine_ops)
WHERE chunk_index >= 1 AND chunk_index <= 200;

-- Vector Index 2: Chunks 200-400
CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_2
ON rag_chunks USING hnsw (embedding vector_cosine_ops)
WHERE chunk_index > 200 AND chunk_index <= 400;

-- Vector Index 3: Chunks 400+
CREATE INDEX IF NOT EXISTS idx_rag_vectors_hnsw_3
ON rag_chunks USING hnsw (embedding vector_cosine_ops)
WHERE chunk_index > 400;

-- ============================================================================
-- METADATA INDEXES (for validation layer)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_rag_document_id
ON rag_chunks (document_id);

CREATE INDEX IF NOT EXISTS idx_rag_collection_prefix
ON rag_chunks (collection_prefix);

CREATE INDEX IF NOT EXISTS idx_rag_segment
ON rag_chunks (segment);

CREATE INDEX IF NOT EXISTS idx_rag_confidence_score
ON rag_chunks (confidence_score DESC)
WHERE confidence_score >= 0.85;

-- ============================================================================
-- COMPOSITE INDEXES (for common query patterns)
-- ============================================================================

-- Quick lookups by collection and confidence
CREATE INDEX IF NOT EXISTS idx_rag_collection_confidence
ON rag_chunks (collection_prefix, confidence_score DESC);

-- Metadata completeness checks
CREATE INDEX IF NOT EXISTS idx_rag_metadata_complete
ON rag_chunks (document_id, source_url, collection_prefix, segment)
WHERE document_id IS NOT NULL
  AND source_url IS NOT NULL
  AND collection_prefix IS NOT NULL
  AND segment IS NOT NULL;

-- ============================================================================
-- STATISTICS & ANALYSIS
-- ============================================================================

-- Force ANALYZE after index creation
ANALYZE rag_chunks;

-- Log index creation (if logging table exists)
DO $$
BEGIN
  IF EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='rag_index_log') THEN
    INSERT INTO rag_index_log (index_name, status, created_at)
    VALUES
      ('idx_rag_san_fulltext', 'created', NOW()),
      ('idx_rag_ene_fulltext', 'created', NOW()),
      ('idx_rag_por_fulltext', 'created', NOW()),
      ('idx_rag_aer_fulltext', 'created', NOW()),
      ('idx_rag_bar_fulltext', 'created', NOW()),
      ('idx_rag_vectors_hnsw_1', 'created', NOW()),
      ('idx_rag_vectors_hnsw_2', 'created', NOW()),
      ('idx_rag_vectors_hnsw_3', 'created', NOW());
  END IF;
END
$$;
