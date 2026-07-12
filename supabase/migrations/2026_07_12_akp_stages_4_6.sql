-- Academic Knowledge Pipeline (WF-AKP-001) — Stages 4-6
-- Ticket: WF-AKP-001 (Stages 4-6 pending in Claude Code)
--
-- Contexto:
--   Stages 1-3 (concluídas fora deste repo) produziram:
--     - 36 teses acadêmicas curadas (ver academic_theses)
--     - 52 Knowledge Elements (chunks + metadata prontos p/ embedding)
--
--   Esta migração cobre:
--     Stage 4 — pgvector ingestion (schema + índice HNSW)
--     Stage 5 — SharePoint indexing (rag_collections + sp_agent_routing)
--     Stage 6 — agent activation (maestro_routing_keywords transversais)
--
-- MIGRAÇÃO CANDIDATA. Não aplicar em produção sem aprovação MN.
-- Alguns pressupostos de schema podem divergir do Supabase real; ajustar
-- conforme necessidade (colunas marcadas com -- ADAPT).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_12_akp_stages_4_6.sql
--
-- ROLLBACK: ver bloco DOWN no fim deste arquivo. As inserções são
-- idempotentes via ON CONFLICT DO NOTHING; os CREATE são IF NOT EXISTS.

BEGIN;

-- =====================================================================
-- STAGE 4 — pgvector ingestion
-- =====================================================================

-- ---------------------------------------------------------------------
-- 4.1 Extensão pgvector
-- ---------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------
-- 4.2 Tabela academic_theses — inventário das 36 teses
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS academic_theses (
  id             TEXT PRIMARY KEY,             -- slug estável (ex.: 'silva-2019-dragagem')
  titulo         TEXT NOT NULL,
  autor          TEXT NOT NULL,
  ano            INTEGER,
  instituicao    TEXT,                          -- USP, COPPE, UnB, ...
  programa       TEXT,                          -- POLI Engenharia Civil, ...
  orientador     TEXT,
  nivel          TEXT CHECK (nivel IN ('mestrado','doutorado','livre_docencia','pos_doc')),
  segmento       TEXT,                          -- portos|aeroportos|saneamento|energia|barragens|rodovias|oae|ferrovia|metro|tuneis|transversal
  doi            TEXT,
  url_publico    TEXT,                          -- link p/ repositório institucional
  sp_path        TEXT,                          -- caminho no SharePoint (07_Conhecimento_Academico/...)
  abstract       TEXT,
  palavras_chave TEXT[],
  citacoes       INTEGER DEFAULT 0,
  qualis         TEXT,                          -- A1..C se aplicável (revista de origem, quando artigo derivado)
  status         TEXT DEFAULT 'ativo' CHECK (status IN ('ativo','arquivado','em_revisao')),
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_academic_theses_segmento ON academic_theses(segmento);
CREATE INDEX IF NOT EXISTS idx_academic_theses_ano      ON academic_theses(ano DESC);
CREATE INDEX IF NOT EXISTS idx_academic_theses_palavras ON academic_theses USING GIN(palavras_chave);

-- ---------------------------------------------------------------------
-- 4.3 Tabela academic_knowledge_elements — 52 KEs prontos p/ embedding
-- ---------------------------------------------------------------------
-- Um KE = trecho autocontido de uma tese, curado por MN + equipe.
-- Metadata carrega o suficiente p/ um agente citar corretamente.
CREATE TABLE IF NOT EXISTS academic_knowledge_elements (
  id             TEXT PRIMARY KEY,             -- ex.: 'KE-052'
  tese_id        TEXT NOT NULL REFERENCES academic_theses(id) ON DELETE CASCADE,
  ordem          INTEGER NOT NULL,             -- posição dentro da tese (p/ replay)
  tipo           TEXT NOT NULL CHECK (tipo IN (
                    'conceito',       -- definição / framework teórico
                    'metodo',         -- metodologia / procedimento
                    'formula',        -- equação / modelo matemático
                    'caso',           -- estudo de caso empírico
                    'dado',           -- dado quantitativo / tabela
                    'critica',        -- crítica a norma / prática vigente
                    'recomendacao'    -- recomendação de projeto
                  )),
  titulo         TEXT NOT NULL,                -- resumo curto (≤120 chars)
  chunk          TEXT NOT NULL,                -- texto original preservado (300-800 tokens típico)
  chunk_tokens   INTEGER,                       -- contagem cache (openai tiktoken cl100k_base)
  paginas        INT4RANGE,                    -- páginas da tese (ex.: '[42,55)')
  segmento       TEXT NOT NULL,                -- redundância p/ filtragem barata
  aplicabilidade TEXT[],                       -- fases do ciclo de vida: 'estudo_previo','projeto_basico','executivo','obra','o_m','licitacao','dd','descomissionamento'
  agentes_alvo   TEXT[],                       -- lista explícita, ex.: ARRAY['agente-portos','agente-barragens']
  citacao_bibtex TEXT,                          -- referência formatada para citação
  provenance     JSONB DEFAULT '{}'::jsonb,    -- {stage_1:{...},stage_2:{...},stage_3:{...}} audit trail
  embedding      vector(1536),                  -- text-embedding-3-small default; ajustar se trocar modelo
  embedding_model TEXT,                         -- 'text-embedding-3-small' | 'text-embedding-3-large' | 'multilingual-e5-small'
  embedding_created_at TIMESTAMPTZ,
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ake_tese_id      ON academic_knowledge_elements(tese_id);
CREATE INDEX IF NOT EXISTS idx_ake_tipo         ON academic_knowledge_elements(tipo);
CREATE INDEX IF NOT EXISTS idx_ake_segmento     ON academic_knowledge_elements(segmento);
CREATE INDEX IF NOT EXISTS idx_ake_agentes_alvo ON academic_knowledge_elements USING GIN(agentes_alvo);
CREATE INDEX IF NOT EXISTS idx_ake_aplicabilid  ON academic_knowledge_elements USING GIN(aplicabilidade);

-- Índice HNSW p/ vector search (cosine). m=16, ef_construction=64 são
-- defaults conservadores; ajustar se cardinalidade crescer >>52.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='public' AND indexname='idx_ake_embedding_hnsw'
  ) THEN
    CREATE INDEX idx_ake_embedding_hnsw
      ON academic_knowledge_elements
      USING hnsw (embedding vector_cosine_ops)
      WITH (m = 16, ef_construction = 64);
  END IF;
END $$;

-- ---------------------------------------------------------------------
-- 4.4 Trigger updated_at
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_academic_theses_updated ON academic_theses;
CREATE TRIGGER trg_academic_theses_updated
  BEFORE UPDATE ON academic_theses
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_ake_updated ON academic_knowledge_elements;
CREATE TRIGGER trg_ake_updated
  BEFORE UPDATE ON academic_knowledge_elements
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ---------------------------------------------------------------------
-- 4.5 Função de busca vetorial com filtros
-- ---------------------------------------------------------------------
-- Interface estável p/ os agentes chamarem. Retorna top-N KEs por
-- similaridade cosine, com filtros opcionais por segmento, tipo, agente.
CREATE OR REPLACE FUNCTION match_academic_knowledge(
  query_embedding vector(1536),
  match_count     INTEGER DEFAULT 5,
  filter_segmento TEXT    DEFAULT NULL,
  filter_tipo     TEXT    DEFAULT NULL,
  filter_agente   TEXT    DEFAULT NULL,
  min_similarity  FLOAT   DEFAULT 0.20
)
RETURNS TABLE (
  id              TEXT,
  tese_id         TEXT,
  titulo          TEXT,
  chunk           TEXT,
  tipo            TEXT,
  segmento        TEXT,
  citacao_bibtex  TEXT,
  similarity      FLOAT
)
LANGUAGE sql STABLE AS $$
  SELECT
    ake.id,
    ake.tese_id,
    ake.titulo,
    ake.chunk,
    ake.tipo,
    ake.segmento,
    ake.citacao_bibtex,
    1 - (ake.embedding <=> query_embedding) AS similarity
  FROM academic_knowledge_elements ake
  WHERE ake.embedding IS NOT NULL
    AND (filter_segmento IS NULL OR ake.segmento = filter_segmento)
    AND (filter_tipo     IS NULL OR ake.tipo     = filter_tipo)
    AND (filter_agente   IS NULL OR filter_agente = ANY(ake.agentes_alvo))
    AND 1 - (ake.embedding <=> query_embedding) >= min_similarity
  ORDER BY ake.embedding <=> query_embedding ASC
  LIMIT match_count;
$$;

-- =====================================================================
-- STAGE 5 — SharePoint indexing
-- =====================================================================

-- ---------------------------------------------------------------------
-- 5.1 Registrar coleção RAG 'academic-knowledge'
-- ---------------------------------------------------------------------
-- Coleção TRANSVERSAL — não é vinculada a um segmento único; qualquer
-- agente vertical pode invocar. Prefixo 'ake:' evita conflito com as
-- coleções de segmento (san:, ene:, por:, aer:, bar:, ...).
INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('academic-knowledge', 'Conhecimento Acadêmico',  'ake:', jsonb_build_array(
     '36 teses curadas (mestrado + doutorado)',
     '52 Knowledge Elements (chunks + metadata)',
     'Pipeline WF-AKP-001 stages 1-3',
     'Instituições: USP, COPPE/UFRJ, UnB, UFPE, IST-Lisboa (parceria)',
     'Cobertura: portos, aeroportos, saneamento, energia, barragens + transversais'
   ))
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 5.2 Routing SharePoint — pasta 07_Conhecimento_Academico
-- ---------------------------------------------------------------------
-- Não é um agente próprio (não roteia); é uma coleção RAG consumida
-- pelos agentes verticais. Registramos assim mesmo para o indexer de
-- SharePoint saber onde varrer os PDFs das teses.
INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('rag-academic-knowledge', '07_Conhecimento_Academico/*', ARRAY['*.pdf','*.md','*.json'], 200)
ON CONFLICT (agent_slug) DO NOTHING;

-- =====================================================================
-- STAGE 6 — Agent activation
-- =====================================================================

-- ---------------------------------------------------------------------
-- 6.1 Keywords transversais p/ o Maestro reforçar recall
-- ---------------------------------------------------------------------
-- Estas keywords NÃO roteiam para um agente específico. Elas são
-- flags para o Maestro ativar a coleção 'academic-knowledge' EM CIMA
-- do roteamento vertical normal (segmento primário continua ganhando).
--
-- Assumes existing table `maestro_rag_hints(collection_slug TEXT,
--   keyword TEXT, priority INTEGER, PRIMARY KEY (collection_slug, keyword))`.
-- Se essa tabela não existir, comentar o bloco e implementar via
-- `SERVICE_PROMPT_FRAGMENTS` no Maestro.

CREATE TABLE IF NOT EXISTS maestro_rag_hints (
  collection_slug TEXT NOT NULL,
  keyword         TEXT NOT NULL,
  priority        INTEGER DEFAULT 50,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (collection_slug, keyword)
);

INSERT INTO maestro_rag_hints (collection_slug, keyword, priority) VALUES
  ('academic-knowledge', 'tese',                 90),
  ('academic-knowledge', 'dissertação',          90),
  ('academic-knowledge', 'artigo acadêmico',     85),
  ('academic-knowledge', 'estado da arte',       95),
  ('academic-knowledge', 'literatura',           80),
  ('academic-knowledge', 'referencial teórico',  90),
  ('academic-knowledge', 'benchmark acadêmico',  85),
  ('academic-knowledge', 'pesquisa científica',  80),
  ('academic-knowledge', 'metodologia',          70),
  ('academic-knowledge', 'critica à norma',      85),
  ('academic-knowledge', 'USP',                  60),
  ('academic-knowledge', 'COPPE',                70),
  ('academic-knowledge', 'UnB',                  60),
  ('academic-knowledge', 'orientador',           50)
ON CONFLICT (collection_slug, keyword) DO NOTHING;

-- ---------------------------------------------------------------------
-- 6.2 Ativar consumo em todos os verticais S1-S10
-- ---------------------------------------------------------------------
-- Tabela de opt-in: qual agente consulta qual coleção auxiliar.
-- Cada linha = 1 par (agente, coleção). Ordem = prioridade de fallback.
CREATE TABLE IF NOT EXISTS agent_rag_bindings (
  agent_slug      TEXT NOT NULL,
  collection_slug TEXT NOT NULL,
  role            TEXT NOT NULL DEFAULT 'auxiliary' CHECK (role IN ('primary','auxiliary')),
  priority        INTEGER DEFAULT 100,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (agent_slug, collection_slug)
);

INSERT INTO agent_rag_bindings (agent_slug, collection_slug, role, priority) VALUES
  -- S1-S4 (existentes)
  ('agente-infraestrutura-s1', 'academic-knowledge', 'auxiliary', 80),
  ('agente-infraestrutura-s2', 'academic-knowledge', 'auxiliary', 80),
  ('agente-infraestrutura-s3', 'academic-knowledge', 'auxiliary', 80),
  ('agente-infraestrutura-s4', 'academic-knowledge', 'auxiliary', 80),
  -- S6-S10 (novos v4.2 — prioridade maior, pipeline foi calibrado neles)
  ('agente-portos',      'academic-knowledge', 'auxiliary', 100),
  ('agente-aeroportos',  'academic-knowledge', 'auxiliary', 100),
  ('agente-saneamento',  'academic-knowledge', 'auxiliary', 100),
  ('agente-energia',     'academic-knowledge', 'auxiliary', 100),
  ('agente-barragens',   'academic-knowledge', 'auxiliary', 100),
  -- Horizontais estratégicos
  ('agente-advisory',    'academic-knowledge', 'auxiliary', 90),
  ('agente-arquiteto-ia','academic-knowledge', 'auxiliary', 70)
ON CONFLICT (agent_slug, collection_slug) DO NOTHING;

COMMIT;

-- =====================================================================
-- INGESTÃO DAS 52 KEs
-- =====================================================================
--
-- Os INSERTS reais das 36 teses + 52 KEs NÃO estão neste arquivo.
-- Motivo: o payload das stages 1-3 (JSON com chunk + provenance + qualis)
-- vive fora do repo (SharePoint 07_Conhecimento_Academico/exports/).
--
-- Rodar o ingestor:
--   cd manta-hub
--   python scripts/akp_ingest.py \
--     --input path/to/akp-ke-payload.json \
--     --supabase-url $SUPABASE_URL \
--     --supabase-key $SUPABASE_SERVICE_ROLE_KEY \
--     --embedding-model text-embedding-3-small
--
-- Ver `docs/AKP-INGESTION.md` no repositório manta-hub para o formato
-- esperado do JSON e o runbook completo.
--
-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM agent_rag_bindings WHERE collection_slug = 'academic-knowledge';
-- DELETE FROM maestro_rag_hints  WHERE collection_slug = 'academic-knowledge';
-- DELETE FROM sp_agent_routing   WHERE agent_slug      = 'rag-academic-knowledge';
-- DELETE FROM rag_collections    WHERE slug            = 'academic-knowledge';
--
-- DROP FUNCTION IF EXISTS match_academic_knowledge(vector, INTEGER, TEXT, TEXT, TEXT, FLOAT);
-- DROP TABLE    IF EXISTS academic_knowledge_elements;
-- DROP TABLE    IF EXISTS academic_theses;
--
-- -- Não dropar as tabelas auxiliares (agent_rag_bindings, maestro_rag_hints)
-- -- se outras coleções já dependerem delas. Verificar antes:
-- --   SELECT * FROM agent_rag_bindings WHERE collection_slug != 'academic-knowledge';
-- --   SELECT * FROM maestro_rag_hints  WHERE collection_slug != 'academic-knowledge';
--
-- COMMIT;
