-- Manta Cases Pipeline (WF-MCP-001) — v4.6 Stages 4-6
-- Ticket: WF-MCP-001 (Manta Cases Pipeline)
--
-- Contexto:
--   Stages 1-3 (concluídas fora deste repo por MN + equipe) produzem, a
--   partir dos memoriais reais no SharePoint (DDs, EVTEs, projetos
--   executivos, laudos técnicos, pareceres), pares (pergunta técnica
--   implícita → resposta especializada Manta) curados como Case Elements.
--
--   Esta migração cobre:
--     Stage 4 — pgvector ingestion (schema + índice HNSW + hybrid FTS)
--     Stage 5 — SharePoint indexing (rag_collections + sp_agent_routing)
--     Stage 6 — agent activation (agent_rag_bindings prioridade 120)
--
--   PRIORIDADE 120 (> 100 da academic-knowledge): memoriais REAIS Manta
--   valem mais que tese acadêmica em qualquer resolução de contexto.
--
--   NDA compliance: cada projeto/KE carrega `nda_level` explícito
--   (publico|interno|confidencial|restrito). A função de busca aceita
--   `filter_nda_level` que representa o teto autorizado do consumidor
--   e SÓ retorna KEs com nda_level ≤ teto (ordem lexicográfica de
--   sensibilidade).
--
-- MIGRAÇÃO CANDIDATA. Não aplicar em produção sem aprovação MN.
-- Aditiva sobre v4.5. Idempotente via IF NOT EXISTS / ON CONFLICT.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_12_manta_cases_v4_6.sql
--
-- ROLLBACK: ver bloco DOWN no fim deste arquivo.

BEGIN;

-- =====================================================================
-- STAGE 4 — pgvector ingestion
-- =====================================================================

-- ---------------------------------------------------------------------
-- 4.1 Extensão pgvector (idempotente; já presente em v4.3, aqui por
-- garantia se esta migração rodar isolada)
-- ---------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------
-- 4.2 Tabela manta_projects — metadata dos projetos-fonte
-- ---------------------------------------------------------------------
-- 1 linha / projeto Manta que originou casos. Referência interna
-- (não vaza para output do agente sem NDA compliance).
CREATE TABLE IF NOT EXISTS manta_projects (
  id             TEXT PRIMARY KEY,             -- slug estável (ex.: 'epr-br365')
  nome           TEXT NOT NULL,                -- ex.: 'EPR BR-365 Duplicação Uberlândia–Patrocínio'
  cliente        TEXT,                          -- ex.: 'EPR Concessionária'
  segmento       TEXT,                          -- rodovias|oae|ferrovia|metro|tuneis|portos|aeroportos|saneamento|energia|barragens|mineracao|oleo_gas|edificacoes|transversal
  ano_inicio     INTEGER,
  ano_conclusao  INTEGER,
  escopo_resumo  TEXT,                          -- resumo executivo do projeto
  sp_path        TEXT,                          -- caminho no SharePoint (03_Projetos/... ou 08_Casos_Manta/...)
  nda_level      TEXT NOT NULL DEFAULT 'interno' CHECK (nda_level IN (
                    'publico',        -- pode ser citado sem restrição
                    'interno',        -- só dentro da Manta + parceiros com NDA
                    'confidencial',   -- só equipe do projeto + owners
                    'restrito'        -- só MN + tech lead
                  )),
  disciplinas    TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ex.: ['terraplenagem','pavimentação','OAE','drenagem']
  equipe_manta   TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ex.: ['MN','Vinícius','Bruno']
  status         TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo','arquivado','em_revisao','encerrado')),
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_manta_projects_segmento    ON manta_projects(segmento);
CREATE INDEX IF NOT EXISTS idx_manta_projects_nda         ON manta_projects(nda_level);
CREATE INDEX IF NOT EXISTS idx_manta_projects_disciplinas ON manta_projects USING GIN(disciplinas);
CREATE INDEX IF NOT EXISTS idx_manta_projects_ano_conc    ON manta_projects(ano_conclusao DESC);

-- ---------------------------------------------------------------------
-- 4.3 Tabela manta_cases_elements — Knowledge Elements dos memoriais
-- ---------------------------------------------------------------------
-- Espelha o schema de academic_knowledge_elements (v4.3) mas com semântica
-- Manta: tipos são categorias de caso (lição aprendida, decisão de projeto,
-- memória de cálculo, pleito de claim, etc.), citação é INTERNA (referência
-- ao memorial no SharePoint), e cada KE herda o nda_level do projeto (com
-- possibilidade de restringir mais, nunca afrouxar).
CREATE TABLE IF NOT EXISTS manta_cases_elements (
  id                   TEXT PRIMARY KEY,             -- ex.: 'MCS-00042'
  projeto_id           TEXT NOT NULL REFERENCES manta_projects(id) ON DELETE CASCADE,
  ordem                INTEGER NOT NULL,             -- posição no memorial (p/ replay)
  tipo                 TEXT NOT NULL CHECK (tipo IN (
                          'lição_aprendida',    -- retro / post-mortem
                          'decisão_projeto',    -- rationale registrado (por que fizemos X)
                          'memória_calculo',    -- passo-a-passo de cálculo reutilizável
                          'pleito_claim',       -- argumentação de reequilíbrio / claim contratual
                          'risco_mitigado',     -- risco identificado + tratamento aplicado
                          'padrão_aplicado',    -- template / padrão consolidado no projeto
                          'contra_exemplo',     -- o que NÃO deu certo (aprendizado negativo)
                          'recomendação'        -- recomendação genérica derivada do caso
                        )),
  titulo               TEXT NOT NULL,                -- resumo curto (≤120 chars)
  chunk                TEXT NOT NULL,                -- texto original preservado (300-800 tokens típico)
  chunk_tokens         INTEGER,                       -- contagem cache (cl100k_base)
  segmento             TEXT NOT NULL,                -- redundância p/ filtragem barata
  disciplinas          TEXT[] DEFAULT ARRAY[]::TEXT[],
  agentes_alvo         TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ex.: ARRAY['agente-portos','agente-barragens']
  fase_ciclo_vida      TEXT[] DEFAULT ARRAY[]::TEXT[],  -- 'estudo_previo','projeto_basico','executivo','obra','o_m','licitacao','dd','descomissionamento'
  nda_level            TEXT NOT NULL DEFAULT 'interno' CHECK (nda_level IN (
                          'publico','interno','confidencial','restrito'
                        )),
  citacao_interna      TEXT,                          -- ex.: '[MN 2024, memorial-EPR-BR365-DD, §4.2]'
  provenance           JSONB DEFAULT '{}'::jsonb,     -- {stage_1:{...},stage_2:{...},stage_3:{...}} audit trail
  embedding            vector(1536),                  -- text-embedding-3-small default
  embedding_model      TEXT,                          -- 'text-embedding-3-small' | ...
  embedding_created_at TIMESTAMPTZ,
  search_tsv           TSVECTOR,                      -- FTS híbrido (v4.3 pattern)
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- Índices funcionais
CREATE INDEX IF NOT EXISTS idx_mcs_projeto_id     ON manta_cases_elements(projeto_id);
CREATE INDEX IF NOT EXISTS idx_mcs_tipo           ON manta_cases_elements(tipo);
CREATE INDEX IF NOT EXISTS idx_mcs_segmento       ON manta_cases_elements(segmento);
CREATE INDEX IF NOT EXISTS idx_mcs_agentes_alvo   ON manta_cases_elements USING GIN(agentes_alvo);
CREATE INDEX IF NOT EXISTS idx_mcs_disciplinas    ON manta_cases_elements USING GIN(disciplinas);
CREATE INDEX IF NOT EXISTS idx_mcs_fase           ON manta_cases_elements USING GIN(fase_ciclo_vida);
CREATE INDEX IF NOT EXISTS idx_mcs_nda_level      ON manta_cases_elements(nda_level);

-- Índice HNSW p/ vector search (cosine). Mesma configuração da AKP.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='public' AND indexname='idx_mcs_embedding_hnsw'
  ) THEN
    CREATE INDEX idx_mcs_embedding_hnsw
      ON manta_cases_elements
      USING hnsw (embedding vector_cosine_ops)
      WITH (m = 16, ef_construction = 64);
  END IF;
END $$;

-- Índice GIN p/ FTS (backfill logo abaixo cuida do search_tsv)
CREATE INDEX IF NOT EXISTS idx_mcs_search_tsv
  ON manta_cases_elements USING GIN(search_tsv);

-- ---------------------------------------------------------------------
-- 4.4 Triggers: updated_at + search_tsv
-- ---------------------------------------------------------------------
-- Reusa touch_updated_at() se já existir (v4.3); senão cria.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'touch_updated_at') THEN
    EXECUTE $F$
      CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $B$
      BEGIN
        NEW.updated_at := NOW();
        RETURN NEW;
      END;
      $B$ LANGUAGE plpgsql;
    $F$;
  END IF;
END $$;

DROP TRIGGER IF EXISTS trg_manta_projects_updated ON manta_projects;
CREATE TRIGGER trg_manta_projects_updated
  BEFORE UPDATE ON manta_projects
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_mcs_updated ON manta_cases_elements;
CREATE TRIGGER trg_mcs_updated
  BEFORE UPDATE ON manta_cases_elements
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- Trigger search_tsv (portuguese, peso A no título, peso B no chunk)
CREATE OR REPLACE FUNCTION mcs_update_tsv() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_tsv :=
    setweight(to_tsvector('portuguese', COALESCE(NEW.titulo, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.chunk,  '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_mcs_tsv ON manta_cases_elements;
CREATE TRIGGER trg_mcs_tsv
  BEFORE INSERT OR UPDATE OF titulo, chunk
  ON manta_cases_elements
  FOR EACH ROW EXECUTE FUNCTION mcs_update_tsv();

-- Backfill p/ linhas existentes (idempotente)
UPDATE manta_cases_elements
   SET search_tsv =
       setweight(to_tsvector('portuguese', COALESCE(titulo, '')), 'A') ||
       setweight(to_tsvector('portuguese', COALESCE(chunk,  '')), 'B')
 WHERE search_tsv IS NULL;

-- ---------------------------------------------------------------------
-- 4.5 Função de busca híbrida com filtro de NDA
-- ---------------------------------------------------------------------
-- Ordem lexicográfica de sensibilidade — usada no filtro NDA:
--   publico(0) < interno(1) < confidencial(2) < restrito(3)
-- O consumidor passa `filter_nda_level` = seu TETO autorizado.
-- Retorna KEs cujo nda_level ≤ teto (nível numérico).
CREATE OR REPLACE FUNCTION _nda_rank(level TEXT) RETURNS INTEGER
LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE level
    WHEN 'publico'      THEN 0
    WHEN 'interno'      THEN 1
    WHEN 'confidencial' THEN 2
    WHEN 'restrito'     THEN 3
    ELSE 99
  END;
$$;

-- Função híbrida FTS + Vector via Reciprocal Rank Fusion (k=60 default).
-- Mesmo desenho de match_academic_knowledge_hybrid (v4.3), acrescentando
-- filter_nda_level.
CREATE OR REPLACE FUNCTION match_manta_cases_hybrid(
  query_text       TEXT,
  query_embedding  vector(1536),
  match_count      INTEGER DEFAULT 5,
  filter_segmento  TEXT    DEFAULT NULL,
  filter_agente    TEXT    DEFAULT NULL,
  filter_nda_level TEXT    DEFAULT 'interno',  -- teto autorizado do consumidor
  rrf_k            INTEGER DEFAULT 60,
  vector_pool      INTEGER DEFAULT 30,
  fts_pool         INTEGER DEFAULT 30
)
RETURNS TABLE (
  id              TEXT,
  projeto_id      TEXT,
  titulo          TEXT,
  chunk           TEXT,
  tipo            TEXT,
  segmento        TEXT,
  nda_level       TEXT,
  citacao_interna TEXT,
  similarity      FLOAT,
  fts_rank        FLOAT,
  rrf_score       FLOAT,
  sources         TEXT[]
)
LANGUAGE sql STABLE AS $$
  WITH
    nda_ceiling AS (SELECT _nda_rank(filter_nda_level) AS ceiling),
    -- 1) Vector search top-N
    vec AS (
      SELECT
        mcs.id,
        1 - (mcs.embedding <=> query_embedding) AS similarity,
        ROW_NUMBER() OVER (ORDER BY mcs.embedding <=> query_embedding ASC) AS rnk
      FROM manta_cases_elements mcs, nda_ceiling
      WHERE mcs.embedding IS NOT NULL
        AND _nda_rank(mcs.nda_level) <= nda_ceiling.ceiling
        AND (filter_segmento IS NULL OR mcs.segmento = filter_segmento)
        AND (filter_agente   IS NULL OR filter_agente = ANY(mcs.agentes_alvo))
      ORDER BY mcs.embedding <=> query_embedding ASC
      LIMIT vector_pool
    ),
    -- 2) FTS top-N (portuguese)
    fts AS (
      SELECT
        mcs.id,
        ts_rank_cd(mcs.search_tsv, plainto_tsquery('portuguese', query_text)) AS fts_rank,
        ROW_NUMBER() OVER (
          ORDER BY ts_rank_cd(mcs.search_tsv, plainto_tsquery('portuguese', query_text)) DESC
        ) AS rnk
      FROM manta_cases_elements mcs, nda_ceiling
      WHERE mcs.search_tsv @@ plainto_tsquery('portuguese', query_text)
        AND _nda_rank(mcs.nda_level) <= nda_ceiling.ceiling
        AND (filter_segmento IS NULL OR mcs.segmento = filter_segmento)
        AND (filter_agente   IS NULL OR filter_agente = ANY(mcs.agentes_alvo))
      ORDER BY fts_rank DESC
      LIMIT fts_pool
    ),
    -- 3) RRF fusion
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
    mcs.id,
    mcs.projeto_id,
    mcs.titulo,
    mcs.chunk,
    mcs.tipo,
    mcs.segmento,
    mcs.nda_level,
    mcs.citacao_interna,
    fused.similarity,
    fused.fts_rank,
    fused.rrf_score,
    fused.sources
  FROM fused
  JOIN manta_cases_elements mcs ON mcs.id = fused.id
  ORDER BY fused.rrf_score DESC
  LIMIT match_count;
$$;

COMMENT ON FUNCTION match_manta_cases_hybrid IS
  'Busca híbrida (BM25-like FTS pt + pgvector cosine, fused via RRF k=60) sobre manta_cases_elements. '
  'filter_nda_level = teto autorizado do consumidor (publico<interno<confidencial<restrito). '
  'Retorna apenas KEs com nda_level ≤ teto.';

-- =====================================================================
-- STAGE 5 — SharePoint indexing
-- =====================================================================

-- ---------------------------------------------------------------------
-- 5.1 Registrar coleção RAG 'manta-cases'
-- ---------------------------------------------------------------------
-- Transversal (todos os agentes verticais podem consumir). Prefixo 'mcs:'
-- evita conflito com san:/ene:/por:/aer:/bar:/ake:/tun:/min:/ogs:/edi:.
INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('manta-cases', 'Casos Manta (WF-MCP-001)', 'mcs:', jsonb_build_array(
     'Memoriais de DD/EVTE',
     'Projetos executivos',
     'Pleitos técnicos',
     'Laudos periciais',
     'Auditorias',
     'Pipeline WF-MCP-001 stages 1-3'
   ))
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 5.2 Routing SharePoint — pasta 08_Casos_Manta
-- ---------------------------------------------------------------------
-- Não é um agente próprio (não roteia); é coleção RAG consumida pelos
-- verticais. Registramos assim mesmo para o indexer SharePoint saber
-- onde varrer os memoriais.
INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('rag-manta-cases', '08_Casos_Manta/*', ARRAY['*.pdf','*.docx','*.md','*.json'], 220)
ON CONFLICT (agent_slug) DO NOTHING;

-- =====================================================================
-- STAGE 6 — Agent activation
-- =====================================================================

-- ---------------------------------------------------------------------
-- 6.1 Keywords transversais p/ o Maestro reforçar recall
-- ---------------------------------------------------------------------
-- Estas keywords NÃO roteiam para um agente específico. Elas são
-- flags para o Maestro ativar a coleção 'manta-cases' EM CIMA do
-- roteamento vertical normal (segmento primário continua ganhando).
-- Prioridade > que academic-knowledge para casos onde o usuário
-- fala explicitamente de projetos/memoriais da Manta.
INSERT INTO maestro_rag_hints (collection_slug, keyword, priority) VALUES
  ('manta-cases', 'memorial',              95),
  ('manta-cases', 'DD',                     90),
  ('manta-cases', 'due diligence',          95),
  ('manta-cases', 'EVTE',                   90),
  ('manta-cases', 'projeto executivo Manta',95),
  ('manta-cases', 'caso Manta',             98),
  ('manta-cases', 'caso real',              95),
  ('manta-cases', 'lição aprendida',        95),
  ('manta-cases', 'pleito',                 90),
  ('manta-cases', 'reequilíbrio',           85),
  ('manta-cases', 'claim contratual',       85),
  ('manta-cases', 'contra-exemplo',         85),
  ('manta-cases', 'já fizemos',             95),
  ('manta-cases', 'referência interna',     90),
  ('manta-cases', 'MN',                     60),   -- Manoel Neves
  ('manta-cases', 'benchmark Manta',        98)
ON CONFLICT (collection_slug, keyword) DO NOTHING;

-- ---------------------------------------------------------------------
-- 6.2 Ativar consumo em todos os verticais S1-S13 + horizontais
-- ---------------------------------------------------------------------
-- PRIORIDADE 120 > 100 (academic-knowledge). Memoriais reais Manta
-- valem MAIS que tese externa em qualquer resolução de contexto.
-- Advisory/arquiteto-ia ganham a mesma prioridade que verticais porque
-- são consumidores estratégicos (respostas para MN/board).
INSERT INTO agent_rag_bindings (agent_slug, collection_slug, role, priority) VALUES
  -- S1-S4 (existentes)
  ('agente-infraestrutura-s1', 'manta-cases', 'auxiliary', 120),
  ('agente-infraestrutura-s2', 'manta-cases', 'auxiliary', 120),
  ('agente-infraestrutura-s3', 'manta-cases', 'auxiliary', 120),
  ('agente-infraestrutura-s4', 'manta-cases', 'auxiliary', 120),
  -- S5-S13 (v4.2 + v4.4)
  ('agente-tuneis',       'manta-cases', 'auxiliary', 120),
  ('agente-portos',       'manta-cases', 'auxiliary', 120),
  ('agente-aeroportos',   'manta-cases', 'auxiliary', 120),
  ('agente-saneamento',   'manta-cases', 'auxiliary', 120),
  ('agente-energia',      'manta-cases', 'auxiliary', 120),
  ('agente-barragens',    'manta-cases', 'auxiliary', 120),
  ('agente-mineracao',    'manta-cases', 'auxiliary', 120),
  ('agente-oleo-gas',     'manta-cases', 'auxiliary', 120),
  ('agente-edificacoes',  'manta-cases', 'auxiliary', 120),
  -- Horizontais estratégicos
  ('agente-advisory',     'manta-cases', 'auxiliary', 120),
  ('agente-arquiteto-ia', 'manta-cases', 'auxiliary', 110)
ON CONFLICT (agent_slug, collection_slug) DO NOTHING;

COMMIT;

-- =====================================================================
-- INGESTÃO DOS CASOS
-- =====================================================================
--
-- Os INSERTS dos manta_projects + manta_cases_elements NÃO estão neste
-- arquivo. O payload das stages 1-3 (JSON com chunk + provenance) vive
-- fora do repo (SharePoint 08_Casos_Manta/03_exports/).
--
-- Rodar o extrator (produz JSON a partir de memoriais PDF/DOCX):
--   cd manta-hub
--   python scripts/manta_cases_extract.py \
--     --input '/path/to/memoriais/*.pdf' \
--     --project-meta project_meta.json \
--     --output cases.json
--
-- Um `manta_cases_ingest.py` (TODO — fora do escopo desta migração)
-- vai espelhar `akp_ingest.py`, consumindo `cases.json` + `projects.csv`
-- e fazendo UPSERT em manta_projects + manta_cases_elements com
-- embeddings via OpenAI (text-embedding-3-small).
--
-- Ver `Codex-exemplo/sharepoint/03-manta-cases/runbook.md` para o
-- runbook completo das stages 4-6.
--
-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM agent_rag_bindings WHERE collection_slug = 'manta-cases';
-- DELETE FROM maestro_rag_hints  WHERE collection_slug = 'manta-cases';
-- DELETE FROM sp_agent_routing   WHERE agent_slug      = 'rag-manta-cases';
-- DELETE FROM rag_collections    WHERE slug            = 'manta-cases';
--
-- DROP FUNCTION IF EXISTS match_manta_cases_hybrid(TEXT, vector, INTEGER, TEXT, TEXT, TEXT, INTEGER, INTEGER, INTEGER);
-- DROP FUNCTION IF EXISTS _nda_rank(TEXT);
-- DROP TRIGGER  IF EXISTS trg_mcs_tsv ON manta_cases_elements;
-- DROP TRIGGER  IF EXISTS trg_mcs_updated ON manta_cases_elements;
-- DROP TRIGGER  IF EXISTS trg_manta_projects_updated ON manta_projects;
-- DROP FUNCTION IF EXISTS mcs_update_tsv();
-- DROP TABLE    IF EXISTS manta_cases_elements;
-- DROP TABLE    IF EXISTS manta_projects;
--
-- -- Não dropar touch_updated_at() nem tabelas auxiliares
-- -- (agent_rag_bindings, maestro_rag_hints, rag_collections) — outras
-- -- coleções dependem delas.
--
-- COMMIT;
