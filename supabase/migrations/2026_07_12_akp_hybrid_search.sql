-- Academic Knowledge Pipeline (WF-AKP-001) — Hybrid Search (BM25 + Vector RRF)
-- Ticket: WF-AKP-001 backlog item #6
--
-- Motivação:
--   `match_academic_knowledge()` (v4.3 original) usa APENAS cosine sobre
--   embeddings. Termos raros ou normativos ("NBR 12211", "RBAC 154 §5.3",
--   "ANEEL REN 970") sub-detectam porque o embedding os trata como termos
--   genéricos.
--
-- Solução:
--   1. Adiciona tsvector column p/ full-text search (config 'portuguese')
--   2. Trigger mantém tsvector sincronizado com titulo + chunk
--   3. Nova função `match_academic_knowledge_hybrid(query_text, query_embedding, ...)`
--      que faz FTS + vector search e funde os resultados via RRF (k=60)
--
-- A função original `match_academic_knowledge()` continua funcionando (não
-- foi tocada) — coexistência para permitir A/B testing.
--
-- MIGRAÇÃO CANDIDATA, aditiva sobre `2026_07_12_akp_stages_4_6.sql`.
-- Idempotente via IF NOT EXISTS / OR REPLACE.

BEGIN;

-- =====================================================================
-- 1. Coluna tsvector + índice GIN
-- =====================================================================

ALTER TABLE academic_knowledge_elements
  ADD COLUMN IF NOT EXISTS search_tsv tsvector;

-- Config 'portuguese' cobre stemming PT (dragagem→drag, aeroportuário→aeroport).
-- Peso A no título (mais relevante), B no chunk.
CREATE OR REPLACE FUNCTION ake_update_tsv() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_tsv :=
    setweight(to_tsvector('portuguese', COALESCE(NEW.titulo, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.chunk,  '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ake_tsv ON academic_knowledge_elements;
CREATE TRIGGER trg_ake_tsv
  BEFORE INSERT OR UPDATE OF titulo, chunk
  ON academic_knowledge_elements
  FOR EACH ROW EXECUTE FUNCTION ake_update_tsv();

-- Backfill p/ linhas existentes (idempotente — só re-computa)
UPDATE academic_knowledge_elements
   SET search_tsv =
       setweight(to_tsvector('portuguese', COALESCE(titulo, '')), 'A') ||
       setweight(to_tsvector('portuguese', COALESCE(chunk,  '')), 'B')
 WHERE search_tsv IS NULL;

CREATE INDEX IF NOT EXISTS idx_ake_search_tsv
  ON academic_knowledge_elements USING GIN(search_tsv);

-- =====================================================================
-- 2. Função híbrida — FTS + Vector com Reciprocal Rank Fusion
-- =====================================================================

-- RRF (Reciprocal Rank Fusion) — método clássico da literatura de IR
-- (Cormack et al. 2009). Cada resultado ganha score 1/(k + rank), onde
-- k=60 é o hyperparameter padrão. Fundir dois rankings vira soma dos
-- 1/(k+rank) de cada fonte. Robusto e SEM tuning por segmento.

CREATE OR REPLACE FUNCTION match_academic_knowledge_hybrid(
  query_text       TEXT,
  query_embedding  vector(1536),
  match_count      INTEGER DEFAULT 5,
  filter_segmento  TEXT    DEFAULT NULL,
  filter_tipo      TEXT    DEFAULT NULL,
  filter_agente    TEXT    DEFAULT NULL,
  rrf_k            INTEGER DEFAULT 60,
  vector_pool      INTEGER DEFAULT 30,  -- top-N do vector para fundir
  fts_pool         INTEGER DEFAULT 30   -- top-N do FTS para fundir
)
RETURNS TABLE (
  id             TEXT,
  tese_id        TEXT,
  titulo         TEXT,
  chunk          TEXT,
  tipo           TEXT,
  segmento       TEXT,
  citacao_bibtex TEXT,
  similarity     FLOAT,   -- cosine similarity (0-1, NULL se só FTS matcheou)
  fts_rank       FLOAT,   -- ts_rank (0-1, NULL se só vector matcheou)
  rrf_score      FLOAT,   -- soma dos 1/(k+rank) das duas fontes
  sources        TEXT[]   -- ARRAY['vector','fts'] indicando origem
)
LANGUAGE sql STABLE AS $$
  WITH
    -- 1) Top-N do vector search (cosine)
    vec AS (
      SELECT
        ake.id,
        1 - (ake.embedding <=> query_embedding) AS similarity,
        ROW_NUMBER() OVER (ORDER BY ake.embedding <=> query_embedding ASC) AS rnk
      FROM academic_knowledge_elements ake
      WHERE ake.embedding IS NOT NULL
        AND (filter_segmento IS NULL OR ake.segmento = filter_segmento)
        AND (filter_tipo     IS NULL OR ake.tipo     = filter_tipo)
        AND (filter_agente   IS NULL OR filter_agente = ANY(ake.agentes_alvo))
      ORDER BY ake.embedding <=> query_embedding ASC
      LIMIT vector_pool
    ),
    -- 2) Top-N do FTS (BM25-like via ts_rank_cd)
    fts AS (
      SELECT
        ake.id,
        ts_rank_cd(ake.search_tsv, plainto_tsquery('portuguese', query_text)) AS fts_rank,
        ROW_NUMBER() OVER (
          ORDER BY ts_rank_cd(ake.search_tsv, plainto_tsquery('portuguese', query_text)) DESC
        ) AS rnk
      FROM academic_knowledge_elements ake
      WHERE ake.search_tsv @@ plainto_tsquery('portuguese', query_text)
        AND (filter_segmento IS NULL OR ake.segmento = filter_segmento)
        AND (filter_tipo     IS NULL OR ake.tipo     = filter_tipo)
        AND (filter_agente   IS NULL OR filter_agente = ANY(ake.agentes_alvo))
      ORDER BY fts_rank DESC
      LIMIT fts_pool
    ),
    -- 3) União dos IDs + RRF score
    fused AS (
      SELECT
        COALESCE(vec.id, fts.id) AS id,
        vec.similarity,
        fts.fts_rank,
        (
          COALESCE(1.0 / (rrf_k + vec.rnk), 0) +
          COALESCE(1.0 / (rrf_k + fts.rnk), 0)
        ) AS rrf_score,
        ARRAY_REMOVE(
          ARRAY[
            CASE WHEN vec.id IS NOT NULL THEN 'vector' END,
            CASE WHEN fts.id IS NOT NULL THEN 'fts'    END
          ], NULL
        ) AS sources
      FROM vec
      FULL OUTER JOIN fts USING (id)
    )
  SELECT
    ake.id,
    ake.tese_id,
    ake.titulo,
    ake.chunk,
    ake.tipo,
    ake.segmento,
    ake.citacao_bibtex,
    fused.similarity,
    fused.fts_rank,
    fused.rrf_score,
    fused.sources
  FROM fused
  JOIN academic_knowledge_elements ake ON ake.id = fused.id
  ORDER BY fused.rrf_score DESC
  LIMIT match_count;
$$;

COMMENT ON FUNCTION match_academic_knowledge_hybrid IS
  'Hybrid retrieval combining BM25-like FTS (portuguese) and pgvector cosine, fused via RRF (k=60 default). Robust to normative/rare-term queries where vector-only underperforms.';

COMMIT;

-- =====================================================================
-- Uso esperado
-- =====================================================================
--
-- Query em linguagem natural (comportamento igual ao match_academic_knowledge):
--   SELECT * FROM match_academic_knowledge_hybrid(
--     query_text := 'dragagem em terminal graneleiro',
--     query_embedding := '[...]'::vector(1536),
--     match_count := 5,
--     filter_segmento := 'portos'
--   );
--
-- Query normativa (hybrid brilha):
--   SELECT * FROM match_academic_knowledge_hybrid(
--     query_text := 'NBR 12211 concepção ETA',
--     query_embedding := '[...]'::vector(1536),
--     match_count := 5,
--     filter_segmento := 'saneamento'
--   );
--
-- Fallback (só FTS, quando embedding não estiver disponível):
--   SELECT * FROM match_academic_knowledge_hybrid(
--     query_text := 'CFRD flexão laje',
--     query_embedding := ARRAY_FILL(0, ARRAY[1536])::vector(1536),  -- zero vector
--     vector_pool := 0,  -- desabilita canal vector
--     match_count := 5
--   );
--
-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS match_academic_knowledge_hybrid(TEXT, vector, INTEGER, TEXT, TEXT, TEXT, INTEGER, INTEGER, INTEGER);
-- DROP TRIGGER IF EXISTS trg_ake_tsv ON academic_knowledge_elements;
-- DROP FUNCTION IF EXISTS ake_update_tsv();
-- DROP INDEX  IF EXISTS idx_ake_search_tsv;
-- ALTER TABLE academic_knowledge_elements DROP COLUMN IF EXISTS search_tsv;
-- COMMIT;
