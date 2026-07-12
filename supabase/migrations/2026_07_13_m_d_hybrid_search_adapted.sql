-- M-D — Hybrid search ADAPTADO ao schema real
-- Substitui: supabase/migrations/2026_07_12_akp_hybrid_search.sql
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 2 M-D
--
-- Opera sobre knowledge_extractions + ke_embeddings (schema real).
-- Adiciona tsvector para FTS 'portuguese' + função hybrid RRF k=60.

BEGIN;

-- ============================================================
-- 1. tsvector column + GIN index sobre knowledge_extractions
-- ============================================================
ALTER TABLE public.knowledge_extractions
  ADD COLUMN IF NOT EXISTS search_tsv tsvector;

CREATE OR REPLACE FUNCTION public.ke_update_tsv()
RETURNS TRIGGER LANGUAGE plpgsql SET search_path = public, extensions AS $$
BEGIN
  NEW.search_tsv :=
    setweight(to_tsvector('portuguese', COALESCE(NEW.tipo, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.descricao, '')), 'B');
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ke_tsv ON public.knowledge_extractions;
CREATE TRIGGER trg_ke_tsv
  BEFORE INSERT OR UPDATE OF tipo, descricao
  ON public.knowledge_extractions
  FOR EACH ROW EXECUTE FUNCTION public.ke_update_tsv();

-- Backfill existente
UPDATE public.knowledge_extractions
   SET search_tsv =
       setweight(to_tsvector('portuguese', COALESCE(tipo, '')), 'A') ||
       setweight(to_tsvector('portuguese', COALESCE(descricao, '')), 'B')
 WHERE search_tsv IS NULL;

CREATE INDEX IF NOT EXISTS idx_ke_search_tsv
  ON public.knowledge_extractions USING GIN(search_tsv);

-- ============================================================
-- 2. Função hybrid — BM25 (via ts_rank_cd) + vector (via cosine) fundida via RRF k=60
-- ============================================================
-- Assume vector(1024) (bge-m3). Ver ke_embeddings.embedding.

CREATE OR REPLACE FUNCTION public.match_kes_hybrid(
  query_text       TEXT,
  query_embedding  vector(1024),
  match_count      INTEGER DEFAULT 5,
  filter_agente    TEXT    DEFAULT NULL,
  filter_tipo      TEXT    DEFAULT NULL,
  rrf_k            INTEGER DEFAULT 60,
  vector_pool      INTEGER DEFAULT 30,
  fts_pool         INTEGER DEFAULT 30
)
RETURNS TABLE (
  ke_codigo       TEXT,
  tese_codigo     TEXT,
  descricao       TEXT,
  tipo            TEXT,
  agentes_destino TEXT[],
  grader_score    NUMERIC,
  similarity      FLOAT,
  fts_rank        FLOAT,
  rrf_score       FLOAT,
  sources         TEXT[]
)
LANGUAGE sql STABLE SET search_path = public, extensions AS $$
  WITH
    vec AS (
      SELECT
        ke.ke_codigo,
        1 - (emb.embedding <=> query_embedding) AS similarity,
        ROW_NUMBER() OVER (ORDER BY emb.embedding <=> query_embedding ASC) AS rnk
      FROM public.knowledge_extractions ke
      JOIN public.ke_embeddings emb ON emb.ke_codigo = ke.ke_codigo
      WHERE emb.embedding IS NOT NULL
        AND (filter_agente IS NULL OR filter_agente = ANY(ke.agentes_destino))
        AND (filter_tipo   IS NULL OR ke.tipo = filter_tipo)
      ORDER BY emb.embedding <=> query_embedding ASC
      LIMIT vector_pool
    ),
    fts AS (
      SELECT
        ke.ke_codigo,
        ts_rank_cd(ke.search_tsv, plainto_tsquery('portuguese', query_text)) AS fts_rank,
        ROW_NUMBER() OVER (
          ORDER BY ts_rank_cd(ke.search_tsv, plainto_tsquery('portuguese', query_text)) DESC
        ) AS rnk
      FROM public.knowledge_extractions ke
      WHERE ke.search_tsv @@ plainto_tsquery('portuguese', query_text)
        AND (filter_agente IS NULL OR filter_agente = ANY(ke.agentes_destino))
        AND (filter_tipo   IS NULL OR ke.tipo = filter_tipo)
      ORDER BY fts_rank DESC
      LIMIT fts_pool
    ),
    fused AS (
      SELECT
        COALESCE(vec.ke_codigo, fts.ke_codigo) AS ke_codigo,
        vec.similarity,
        fts.fts_rank,
        (COALESCE(1.0 / (rrf_k + vec.rnk), 0) +
         COALESCE(1.0 / (rrf_k + fts.rnk), 0)) AS rrf_score,
        ARRAY_REMOVE(ARRAY[
          CASE WHEN vec.ke_codigo IS NOT NULL THEN 'vector' END,
          CASE WHEN fts.ke_codigo IS NOT NULL THEN 'fts'    END
        ], NULL) AS sources
      FROM vec
      FULL OUTER JOIN fts USING (ke_codigo)
    )
  SELECT
    ke.ke_codigo, ke.tese_codigo, ke.descricao, ke.tipo,
    ke.agentes_destino, ke.grader_score,
    f.similarity, f.fts_rank, f.rrf_score, f.sources
  FROM fused f
  JOIN public.knowledge_extractions ke ON ke.ke_codigo = f.ke_codigo
  ORDER BY f.rrf_score DESC
  LIMIT match_count;
$$;

COMMENT ON FUNCTION public.match_kes_hybrid IS
  'Hybrid retrieval BM25 portuguese + pgvector 1024d cosine, fundido via RRF k=60. Adaptado ao schema real (knowledge_extractions + ke_embeddings).';

COMMIT;

-- ============================================================
-- ROLLBACK
-- ============================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS public.match_kes_hybrid(TEXT, vector, INTEGER, TEXT, TEXT, INTEGER, INTEGER, INTEGER);
-- DROP TRIGGER IF EXISTS trg_ke_tsv ON public.knowledge_extractions;
-- DROP FUNCTION IF EXISTS public.ke_update_tsv();
-- DROP INDEX IF EXISTS idx_ke_search_tsv;
-- ALTER TABLE public.knowledge_extractions DROP COLUMN IF EXISTS search_tsv;
-- COMMIT;
