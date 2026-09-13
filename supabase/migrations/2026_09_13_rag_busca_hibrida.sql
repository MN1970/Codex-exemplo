-- Manta Maestro v4.3 — RAG: busca híbrida + metadado de versão
-- Ver análise completa em docs/RAG-EMBEDDING-HIBRIDO.md
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN e sem confirmar o schema real de `rag_chunks` (este
-- repositório não tem acesso ao Supabase de produção — assume um
-- schema aproximado, documentado abaixo, com base no que o CLAUDE.md
-- v4.2 registra: 5 coleções já inseridas em `rag_collections`, chunks
-- em `rag_chunks`).
--
-- NÃO inclui a troca do modelo de embedding (bge-small-en-v1.5 →
-- multilíngue) — essa etapa exige re-embedding completo de todo o
-- conteúdo já indexado e é tratada como projeto separado (ver seção
-- 2.1 do documento de análise). Este arquivo cobre só busca híbrida
-- (2.2) e metadado de versão/vigência (2.3), que não dependem de
-- re-embedding e têm ganho imediato.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_13_rag_busca_hibrida.sql
--
-- PRÉ-REQUISITO: confirmar que `rag_chunks` existe com pelo menos
-- `(id, collection_slug TEXT, content TEXT, embedding vector(384))`.
-- Se os nomes de coluna reais divergirem, ajustar este arquivo antes
-- de rodar — tudo está em BEGIN…COMMIT, então qualquer erro reverte.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Metadado de versão/vigência por chunk
-- ---------------------------------------------------------------------

ALTER TABLE rag_chunks
  ADD COLUMN IF NOT EXISTS documento_revisao TEXT,
  ADD COLUMN IF NOT EXISTS documento_data     DATE,
  ADD COLUMN IF NOT EXISTS status_vigencia    TEXT NOT NULL DEFAULT 'vigente'
    CHECK (status_vigencia IN ('vigente', 'superado', 'rascunho'));

CREATE INDEX IF NOT EXISTS idx_rag_chunks_vigencia
  ON rag_chunks (collection_slug, status_vigencia);

COMMENT ON COLUMN rag_chunks.documento_revisao IS
  'Identificador de revisão do documento-fonte (ex.: "_C", "REV_02"). '
  'Existe para evitar o tipo de inconsistência registrada no CLAUDE.md '
  '(MNT-2026-COM-1183_D citado sem confirmação — só _C localizada).';
COMMENT ON COLUMN rag_chunks.status_vigencia IS
  'vigente = usar na busca por padrão; superado = manter para '
  'auditoria/histórico, mas excluir da busca a menos que solicitado '
  'explicitamente; rascunho = ainda não aprovado, nunca citar sem aviso.';

-- ---------------------------------------------------------------------
-- 2. Coluna de busca textual (tsvector) + índice GIN
-- ---------------------------------------------------------------------

ALTER TABLE rag_chunks
  ADD COLUMN IF NOT EXISTS content_tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('portuguese', coalesce(content, ''))) STORED;

CREATE INDEX IF NOT EXISTS idx_rag_chunks_tsv
  ON rag_chunks USING GIN (content_tsv);

-- ---------------------------------------------------------------------
-- 3. Função de busca híbrida (vetorial + textual, Reciprocal Rank Fusion)
-- ---------------------------------------------------------------------
-- k = constante do RRF (60 é o valor padrão usado na literatura).
-- Exclui chunks 'superado' por padrão via p_incluir_superados.

CREATE OR REPLACE FUNCTION rag_busca_hibrida(
    query_embedding     vector,
    query_texto         TEXT,
    p_collection_slug   TEXT,
    p_incluir_superados BOOLEAN DEFAULT FALSE,
    match_count         INT DEFAULT 8,
    rrf_k               INT DEFAULT 60
)
RETURNS TABLE (
    id                 BIGINT,
    content            TEXT,
    documento_revisao  TEXT,
    documento_data     DATE,
    status_vigencia    TEXT,
    sim_vetorial       FLOAT,
    rank_textual       FLOAT,
    score_hibrido      FLOAT
)
LANGUAGE SQL AS $$
    WITH vetorial AS (
        SELECT rc.id,
               1 - (rc.embedding <=> query_embedding) AS sim_vetorial,
               ROW_NUMBER() OVER (ORDER BY rc.embedding <=> query_embedding) AS rank_v
        FROM rag_chunks rc
        WHERE rc.collection_slug = p_collection_slug
          AND (p_incluir_superados OR rc.status_vigencia = 'vigente')
          AND rc.embedding IS NOT NULL
        ORDER BY rc.embedding <=> query_embedding
        LIMIT GREATEST(match_count * 4, 40)
    ),
    textual AS (
        SELECT rc.id,
               ts_rank(rc.content_tsv, plainto_tsquery('portuguese', query_texto)) AS rank_textual,
               ROW_NUMBER() OVER (
                 ORDER BY ts_rank(rc.content_tsv, plainto_tsquery('portuguese', query_texto)) DESC
               ) AS rank_t
        FROM rag_chunks rc
        WHERE rc.collection_slug = p_collection_slug
          AND (p_incluir_superados OR rc.status_vigencia = 'vigente')
          AND rc.content_tsv @@ plainto_tsquery('portuguese', query_texto)
        ORDER BY rank_textual DESC
        LIMIT GREATEST(match_count * 4, 40)
    ),
    combinado AS (
        SELECT COALESCE(v.id, t.id) AS id,
               COALESCE(v.sim_vetorial, 0) AS sim_vetorial,
               COALESCE(t.rank_textual, 0) AS rank_textual,
               (1.0 / (rrf_k + COALESCE(v.rank_v, 100000))) +
               (1.0 / (rrf_k + COALESCE(t.rank_t, 100000))) AS score_hibrido
        FROM vetorial v
        FULL OUTER JOIN textual t ON v.id = t.id
    )
    SELECT rc.id, rc.content, rc.documento_revisao, rc.documento_data,
           rc.status_vigencia, c.sim_vetorial, c.rank_textual, c.score_hibrido
    FROM combinado c
    JOIN rag_chunks rc ON rc.id = c.id
    ORDER BY c.score_hibrido DESC
    LIMIT match_count;
$$;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP FUNCTION IF EXISTS rag_busca_hibrida(vector, TEXT, TEXT, BOOLEAN, INT, INT);
-- DROP INDEX IF EXISTS idx_rag_chunks_tsv;
-- ALTER TABLE rag_chunks DROP COLUMN IF EXISTS content_tsv;
-- DROP INDEX IF EXISTS idx_rag_chunks_vigencia;
-- ALTER TABLE rag_chunks
--   DROP COLUMN IF EXISTS documento_revisao,
--   DROP COLUMN IF EXISTS documento_data,
--   DROP COLUMN IF EXISTS status_vigencia;
--
-- COMMIT;
