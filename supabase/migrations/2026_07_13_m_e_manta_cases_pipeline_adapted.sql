-- M-E — WF-MCP-001 Manta Cases Pipeline ADAPTADO
-- Substitui: supabase/migrations/2026_07_12_manta_cases_v4_6.sql
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 2 M-E
--
-- Coexiste com public.manta_rag_cases (feedback learner) — este arquivo
-- adiciona uma segunda tabela dedicada a KEs curados a partir de memoriais
-- Manta, com semântica de "referência técnica" (não "feedback").

BEGIN;

-- ============================================================
-- 1. Projetos Manta (origem dos casos)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.manta_projects (
  id                TEXT PRIMARY KEY,
  nome              TEXT NOT NULL,
  cliente           TEXT,
  segmento          TEXT,           -- rodovias, portos, ..., edificacoes
  ano_inicio        INT,
  ano_conclusao     INT,
  escopo_resumo     TEXT,
  sp_path           TEXT,           -- caminho SharePoint
  nda_level         TEXT DEFAULT 'interno' CHECK (nda_level IN (
                     'publico','interno','confidencial','restrito'
                    )),
  disciplinas       TEXT[] DEFAULT '{}',
  equipe_manta      TEXT[] DEFAULT '{}',
  status            TEXT DEFAULT 'ativo' CHECK (status IN ('ativo','arquivado','em_revisao')),
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.manta_projects ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_manta_projects_segmento
  ON public.manta_projects(segmento);
CREATE INDEX IF NOT EXISTS idx_manta_projects_nda
  ON public.manta_projects(nda_level);

-- ============================================================
-- 2. Case Elements — KEs extraídos de memoriais Manta
-- ============================================================
CREATE TABLE IF NOT EXISTS public.manta_case_elements (
  id                UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
  mce_codigo        TEXT UNIQUE NOT NULL,   -- MCE-00042
  projeto_id        TEXT NOT NULL REFERENCES public.manta_projects(id) ON DELETE CASCADE,
  ordem             INTEGER NOT NULL,
  tipo              TEXT NOT NULL CHECK (tipo IN (
                     'licao_aprendida','decisao_projeto','memoria_calculo',
                     'pleito_claim','risco_mitigado','padrao_aplicado',
                     'contra_exemplo','recomendacao'
                    )),
  titulo            TEXT NOT NULL,
  descricao         TEXT NOT NULL,
  segmento          TEXT NOT NULL,
  disciplinas       TEXT[] DEFAULT '{}',
  agentes_destino   TEXT[] DEFAULT '{}',
  fase_ciclo_vida   TEXT[] DEFAULT '{}',
  nda_level         TEXT NOT NULL DEFAULT 'interno' CHECK (nda_level IN (
                     'publico','interno','confidencial','restrito'
                    )),
  citacao_interna   TEXT,
  metadata          JSONB DEFAULT '{}'::jsonb,
  search_tsv        tsvector,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.manta_case_elements ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_mce_projeto      ON public.manta_case_elements(projeto_id);
CREATE INDEX IF NOT EXISTS idx_mce_tipo         ON public.manta_case_elements(tipo);
CREATE INDEX IF NOT EXISTS idx_mce_segmento     ON public.manta_case_elements(segmento);
CREATE INDEX IF NOT EXISTS idx_mce_agentes      ON public.manta_case_elements USING GIN(agentes_destino);
CREATE INDEX IF NOT EXISTS idx_mce_disciplinas  ON public.manta_case_elements USING GIN(disciplinas);
CREATE INDEX IF NOT EXISTS idx_mce_nda          ON public.manta_case_elements(nda_level);
CREATE INDEX IF NOT EXISTS idx_mce_search_tsv   ON public.manta_case_elements USING GIN(search_tsv);

CREATE OR REPLACE FUNCTION public.mce_update_tsv()
RETURNS TRIGGER LANGUAGE plpgsql SET search_path = public, extensions AS $$
BEGIN
  NEW.search_tsv :=
    setweight(to_tsvector('portuguese', COALESCE(NEW.titulo, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.descricao, '')), 'B');
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_mce_tsv ON public.manta_case_elements;
CREATE TRIGGER trg_mce_tsv
  BEFORE INSERT OR UPDATE OF titulo, descricao
  ON public.manta_case_elements
  FOR EACH ROW EXECUTE FUNCTION public.mce_update_tsv();

-- ============================================================
-- 3. Embeddings dos case elements (paralelo ke_embeddings)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.mce_embeddings (
  id            UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
  mce_codigo    TEXT NOT NULL REFERENCES public.manta_case_elements(mce_codigo) ON DELETE CASCADE,
  embedding     vector(1024),                   -- bge-m3 canonical
  model         TEXT DEFAULT 'bge-m3',
  chunk_text    TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.mce_embeddings ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_mce_emb_codigo ON public.mce_embeddings(mce_codigo);

-- HNSW cosine index (mesmo padrão de ke_embeddings)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes
                  WHERE schemaname='public' AND indexname='idx_mce_emb_hnsw') THEN
    CREATE INDEX idx_mce_emb_hnsw
      ON public.mce_embeddings
      USING hnsw (embedding vector_cosine_ops)
      WITH (m = 16, ef_construction = 64);
  END IF;
END $$;

-- ============================================================
-- 4. Helper NDA ranking + Função hybrid retrieval de casos Manta
-- ============================================================
CREATE OR REPLACE FUNCTION public._nda_rank(level TEXT)
RETURNS INTEGER LANGUAGE sql IMMUTABLE SET search_path = public AS $$
  SELECT CASE level
    WHEN 'publico'      THEN 1
    WHEN 'interno'      THEN 2
    WHEN 'confidencial' THEN 3
    WHEN 'restrito'     THEN 4
    ELSE 99
  END;
$$;

CREATE OR REPLACE FUNCTION public.match_manta_cases_hybrid(
  query_text       TEXT,
  query_embedding  vector(1024),
  match_count      INTEGER DEFAULT 5,
  filter_segmento  TEXT    DEFAULT NULL,
  filter_agente    TEXT    DEFAULT NULL,
  filter_nda_level TEXT    DEFAULT 'interno',   -- teto do consumidor
  rrf_k            INTEGER DEFAULT 60
)
RETURNS TABLE (
  mce_codigo    TEXT,
  projeto_id    TEXT,
  titulo        TEXT,
  descricao     TEXT,
  tipo          TEXT,
  segmento      TEXT,
  nda_level     TEXT,
  similarity    FLOAT,
  fts_rank      FLOAT,
  rrf_score     FLOAT
)
LANGUAGE sql STABLE SET search_path = public, extensions AS $$
  WITH
    nda_ceiling AS (SELECT public._nda_rank(filter_nda_level) AS r),
    vec AS (
      SELECT mce.mce_codigo,
             1 - (emb.embedding <=> query_embedding) AS similarity,
             ROW_NUMBER() OVER (ORDER BY emb.embedding <=> query_embedding ASC) AS rnk
      FROM public.manta_case_elements mce
      JOIN public.mce_embeddings emb ON emb.mce_codigo = mce.mce_codigo
      WHERE emb.embedding IS NOT NULL
        AND public._nda_rank(mce.nda_level) <= (SELECT r FROM nda_ceiling)
        AND (filter_segmento IS NULL OR mce.segmento = filter_segmento)
        AND (filter_agente   IS NULL OR filter_agente = ANY(mce.agentes_destino))
      ORDER BY emb.embedding <=> query_embedding ASC
      LIMIT 30
    ),
    fts AS (
      SELECT mce.mce_codigo,
             ts_rank_cd(mce.search_tsv, plainto_tsquery('portuguese', query_text)) AS fts_rank,
             ROW_NUMBER() OVER (
               ORDER BY ts_rank_cd(mce.search_tsv, plainto_tsquery('portuguese', query_text)) DESC
             ) AS rnk
      FROM public.manta_case_elements mce
      WHERE mce.search_tsv @@ plainto_tsquery('portuguese', query_text)
        AND public._nda_rank(mce.nda_level) <= (SELECT r FROM nda_ceiling)
        AND (filter_segmento IS NULL OR mce.segmento = filter_segmento)
        AND (filter_agente   IS NULL OR filter_agente = ANY(mce.agentes_destino))
      ORDER BY fts_rank DESC
      LIMIT 30
    ),
    fused AS (
      SELECT COALESCE(vec.mce_codigo, fts.mce_codigo) AS mce_codigo,
             vec.similarity, fts.fts_rank,
             (COALESCE(1.0/(rrf_k+vec.rnk), 0) + COALESCE(1.0/(rrf_k+fts.rnk), 0)) AS rrf_score
      FROM vec FULL OUTER JOIN fts USING (mce_codigo)
    )
  SELECT mce.mce_codigo, mce.projeto_id, mce.titulo, mce.descricao,
         mce.tipo, mce.segmento, mce.nda_level,
         f.similarity, f.fts_rank, f.rrf_score
    FROM fused f
    JOIN public.manta_case_elements mce ON mce.mce_codigo = f.mce_codigo
   ORDER BY f.rrf_score DESC
   LIMIT match_count;
$$;

COMMENT ON FUNCTION public.match_manta_cases_hybrid IS
  'Retrieval híbrido para KEs de memoriais Manta. Aplica filtro NDA como teto (retorna só NDA <= filter_nda_level). RRF k=60 sobre FTS + vector 1024d.';

COMMIT;

-- ============================================================
-- ROLLBACK
-- ============================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS public.match_manta_cases_hybrid(TEXT,vector,INTEGER,TEXT,TEXT,TEXT,INTEGER);
-- DROP FUNCTION IF EXISTS public._nda_rank(TEXT);
-- DROP INDEX    IF EXISTS idx_mce_emb_hnsw;
-- DROP TABLE    IF EXISTS public.mce_embeddings;
-- DROP TRIGGER  IF EXISTS trg_mce_tsv ON public.manta_case_elements;
-- DROP FUNCTION IF EXISTS public.mce_update_tsv();
-- DROP TABLE    IF EXISTS public.manta_case_elements;
-- DROP TABLE    IF EXISTS public.manta_projects;
-- COMMIT;
