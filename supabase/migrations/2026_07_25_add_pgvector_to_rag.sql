-- Migration: Add pgvector support for semantic search in RAG chunks
-- Purpose: Enable vector similarity search for improved RAG relevance
-- Date: 2026-07-25

BEGIN;

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- 2. Add embedding column to rag_chunks table
-- Column will store 1536-dimensional embeddings (Anthropic embedding model)
ALTER TABLE rag_chunks
  ADD COLUMN embedding vector(1536) NULL,
  ADD COLUMN embedding_model text DEFAULT 'claude-embed-3',
  ADD COLUMN embedding_created_at timestamp DEFAULT NULL;

-- 3. Create index on embedding column for fast similarity search
-- Using ivfflat index for ~1M vectors, or hnsw for larger scales
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding
  ON rag_chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- 4. Add function for vector similarity search
CREATE OR REPLACE FUNCTION search_rag_by_similarity(
  query_embedding vector(1536),
  collection_filter text DEFAULT NULL,
  limit_results int DEFAULT 10,
  similarity_threshold float DEFAULT 0.5
)
RETURNS TABLE (
  chunk_id uuid,
  collection_slug text,
  content text,
  source_file text,
  similarity_score float,
  page_num int
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    rc.id,
    rc.collection_slug,
    rc.content,
    rc.source_file,
    (1 - (rc.embedding <=> query_embedding)) as similarity_score,
    rc.page_num
  FROM rag_chunks rc
  WHERE
    (collection_filter IS NULL OR rc.collection_slug = collection_filter)
    AND rc.embedding IS NOT NULL
    AND (1 - (rc.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY rc.embedding <=> query_embedding
  LIMIT limit_results;
$$;

-- 5. Add function for hybrid search (keyword + vector)
CREATE OR REPLACE FUNCTION search_rag_hybrid(
  query_text text,
  query_embedding vector(1536),
  collection_filter text DEFAULT NULL,
  limit_results int DEFAULT 10,
  keyword_weight float DEFAULT 0.3,
  vector_weight float DEFAULT 0.7
)
RETURNS TABLE (
  chunk_id uuid,
  collection_slug text,
  content text,
  source_file text,
  score float,
  search_type text
)
LANGUAGE SQL STABLE
AS $$
  WITH keyword_results AS (
    SELECT
      rc.id,
      rc.collection_slug,
      rc.content,
      rc.source_file,
      ts_rank(
        setweight(to_tsvector('portuguese', rc.content), 'A') ||
        setweight(to_tsvector('portuguese', coalesce(rc.source_file, '')), 'B'),
        plainto_tsquery('portuguese', query_text)
      ) as score,
      'keyword' as search_type,
      row_number() OVER (ORDER BY ts_rank(...) DESC) as rn
    FROM rag_chunks rc
    WHERE
      (collection_filter IS NULL OR rc.collection_slug = collection_filter)
      AND setweight(to_tsvector('portuguese', rc.content), 'A') ||
          setweight(to_tsvector('portuguese', coalesce(rc.source_file, '')), 'B')
          @@ plainto_tsquery('portuguese', query_text)
  ),
  vector_results AS (
    SELECT
      rc.id,
      rc.collection_slug,
      rc.content,
      rc.source_file,
      (1 - (rc.embedding <=> query_embedding)) as score,
      'semantic' as search_type,
      row_number() OVER (ORDER BY rc.embedding <=> query_embedding) as rn
    FROM rag_chunks rc
    WHERE
      (collection_filter IS NULL OR rc.collection_slug = collection_filter)
      AND rc.embedding IS NOT NULL
  )
  SELECT
    COALESCE(k.id, v.id),
    COALESCE(k.collection_slug, v.collection_slug),
    COALESCE(k.content, v.content),
    COALESCE(k.source_file, v.source_file),
    COALESCE(k.score, 0) * keyword_weight + COALESCE(v.score, 0) * vector_weight as score,
    CASE
      WHEN k.id IS NOT NULL AND v.id IS NOT NULL THEN 'hybrid'
      WHEN k.id IS NOT NULL THEN 'keyword'
      ELSE 'semantic'
    END as search_type
  FROM keyword_results k
  FULL OUTER JOIN vector_results v ON k.id = v.id
  ORDER BY score DESC
  LIMIT limit_results;
$$;

-- 6. Create table for tracking embedding sync state
CREATE TABLE IF NOT EXISTS rag_embedding_sync (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chunk_id uuid UNIQUE NOT NULL REFERENCES rag_chunks(id) ON DELETE CASCADE,
  embedding_status text DEFAULT 'pending', -- pending, processing, completed, failed
  embedding_error text NULL,
  embedded_at timestamp DEFAULT NULL,
  embedding_model text DEFAULT 'claude-embed-3',
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_embedding_sync_status
  ON rag_embedding_sync(embedding_status);

CREATE INDEX IF NOT EXISTS idx_rag_embedding_sync_created
  ON rag_embedding_sync(created_at DESC);

-- 7. Create trigger to track updates
CREATE OR REPLACE FUNCTION update_rag_embedding_sync_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rag_embedding_sync_timestamp
  BEFORE UPDATE ON rag_embedding_sync
  FOR EACH ROW
  EXECUTE FUNCTION update_rag_embedding_sync_timestamp();

-- 8. Add full-text search index to rag_chunks for keyword search
ALTER TABLE rag_chunks
  ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('portuguese', coalesce(content, '')), 'A') ||
    setweight(to_tsvector('portuguese', coalesce(source_file, '')), 'B')
  ) STORED;

CREATE INDEX IF NOT EXISTS idx_rag_chunks_search
  ON rag_chunks
  USING GIN (search_vector);

COMMIT;

-- Note: After applying this migration:
-- 1. Run `supabase/embeddings_sync.py` to generate embeddings for existing chunks
-- 2. Schedule `embeddings_sync.py` as daily cron job to process new chunks
-- 3. Update RAG query functions to use hybrid search: search_rag_hybrid()
