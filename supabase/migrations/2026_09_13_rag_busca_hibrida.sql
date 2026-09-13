-- Manta Maestro v5.4.7 — RAG: busca híbrida + metadado de versão (gap G016)
-- Ver análise completa em docs/RAG-EMBEDDING-HIBRIDO.md
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN e sem confirmar o schema real de `manta_rag_chunks`
-- (este repositório não tem acesso de escrita ao Supabase de produção
-- — assume um schema aproximado, documentado abaixo, com base no que
-- `docs/SUPABASE-PROJECT-AUDIT.md` e `docs/EMBEDDER-DECISION.md`
-- documentam sobre essa tabela: 204 chunks, ligada a `manta_rag_documents`,
-- busca via RPC dedicada).
--
-- NÃO mexe no embedder nem na coluna de embedding (tipo/dimensão
-- inalterados) — a troca de embedder (bge-small-en-v1.5 → multilíngue)
-- foi avaliada e formalmente REJEITADA em 26/07/2026 (gap G010, ver
-- docs/EMBEDDER-DECISION.md); este arquivo não reabre essa decisão.
-- Cobre só busca híbrida e metadado de versão/vigência (gap G016), que
-- não dependem do embedder e não exigem re-embedding.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_13_rag_busca_hibrida.sql
--
-- PRÉ-REQUISITO: confirmar que `manta_rag_chunks` existe com pelo menos
-- `(id, collection_slug TEXT, content TEXT, embedding vector(?))` —
-- a dimensão real do vetor não é alterada por este arquivo, então não
-- precisa ser conhecida para aplicar esta migração. Se os nomes de
-- coluna reais divergirem, ajustar este arquivo antes de rodar — tudo
-- está em BEGIN…COMMIT, então qualquer erro reverte.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Metadado de versão/vigência por chunk
-- ---------------------------------------------------------------------

ALTER TABLE manta_rag_chunks
  ADD COLUMN IF NOT EXISTS documento_revisao TEXT,
  ADD COLUMN IF NOT EXISTS documento_data     DATE,
  ADD COLUMN IF NOT EXISTS status_vigencia    TEXT NOT NULL DEFAULT 'vigente'
    CHECK (status_vigencia IN ('vigente', 'superado', 'rascunho'));

CREATE INDEX IF NOT EXISTS idx_manta_rag_chunks_vigencia
  ON manta_rag_chunks (collection_slug, status_vigencia);

COMMENT ON COLUMN manta_rag_chunks.documento_revisao IS
  'Identificador de revisão do documento-fonte (ex.: "_C", "REV_02"). '
  'Existe para dar ao RAG uma forma de nao amplificar uma citacao de '
  'revisao inexistente ou desatualizada de um documento — ver o caso '
  'MNT-2026-COM-1183_D (revisao fabricada, nunca existiu — so _C e '
  'real) registrado na secao "Modelo Mestre de Proposta" do CLAUDE.md. '
  'Nao substitui o aluci-guard: a fabricacao em si e problema de '
  'geracao de conteudo, nao de indexacao.';
COMMENT ON COLUMN manta_rag_chunks.status_vigencia IS
  'vigente = usar na busca por padrão; superado = manter para '
  'auditoria/histórico, mas excluir da busca a menos que solicitado '
  'explicitamente; rascunho = ainda não aprovado, nunca citar sem aviso.';

-- ---------------------------------------------------------------------
-- 2. Coluna de busca textual (tsvector) + índice GIN
-- ---------------------------------------------------------------------

ALTER TABLE manta_rag_chunks
  ADD COLUMN IF NOT EXISTS content_tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('portuguese', coalesce(content, ''))) STORED;

CREATE INDEX IF NOT EXISTS idx_manta_rag_chunks_tsv
  ON manta_rag_chunks USING GIN (content_tsv);

-- ---------------------------------------------------------------------
-- 3. Função de busca híbrida (vetorial + textual, Reciprocal Rank Fusion)
-- ---------------------------------------------------------------------
-- k = constante do RRF (60 é o valor padrão usado na literatura).
-- Exclui chunks 'superado' por padrão via p_incluir_superados.
-- Não substitui a RPC vetorial já existente em produção (citada em
-- docs/EMBEDDER-DECISION.md) — é uma função nova, adicional.

CREATE OR REPLACE FUNCTION manta_rag_busca_hibrida(
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
        FROM manta_rag_chunks rc
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
        FROM manta_rag_chunks rc
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
    JOIN manta_rag_chunks rc ON rc.id = c.id
    ORDER BY c.score_hibrido DESC
    LIMIT match_count;
$$;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP FUNCTION IF EXISTS manta_rag_busca_hibrida(vector, TEXT, TEXT, BOOLEAN, INT, INT);
-- DROP INDEX IF EXISTS idx_manta_rag_chunks_tsv;
-- ALTER TABLE manta_rag_chunks DROP COLUMN IF EXISTS content_tsv;
-- DROP INDEX IF EXISTS idx_manta_rag_chunks_vigencia;
-- ALTER TABLE manta_rag_chunks
--   DROP COLUMN IF EXISTS documento_revisao,
--   DROP COLUMN IF EXISTS documento_data,
--   DROP COLUMN IF EXISTS status_vigencia;
--
-- COMMIT;
