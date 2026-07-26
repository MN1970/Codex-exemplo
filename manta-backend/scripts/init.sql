-- init.sql — bootstrap do banco local (docker-compose) para o Manta Backend.
-- Espelha as 5 coleções RAG e as tabelas usadas pelos routers.

CREATE EXTENSION IF NOT EXISTS vector;

-- rag_documents precisa existir ANTES de rag_chunks porque
-- rag_chunks.document_id referencia rag_documents(id).
CREATE TABLE IF NOT EXISTS rag_documents (
    id           UUID PRIMARY KEY,
    collection   TEXT NOT NULL,
    title        TEXT NOT NULL,
    filename     TEXT NOT NULL,
    file_type    TEXT NOT NULL DEFAULT '',
    source       TEXT NOT NULL DEFAULT 'upload',
    size_bytes   BIGINT NOT NULL DEFAULT 0,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_documents_collection ON rag_documents (collection);
CREATE INDEX IF NOT EXISTS idx_rag_documents_created_at ON rag_documents (created_at);

CREATE TABLE IF NOT EXISTS rag_chunks (
    id          BIGSERIAL PRIMARY KEY,
    collection  TEXT NOT NULL,       -- saneamento | energia | portos | aeroportos | barragens
    prefix      TEXT NOT NULL,       -- san: | ene: | por: | aer: | bar:
    content     TEXT NOT NULL,
    embedding   vector(1536),
    document_id UUID REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection ON rag_chunks (collection);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_document_id ON rag_chunks (document_id);

CREATE TABLE IF NOT EXISTS agent_feedback (
    id          UUID PRIMARY KEY,
    agent_code  TEXT NOT NULL,
    rating      SMALLINT NOT NULL CHECK (rating BETWEEN -1 AND 1),
    comment     TEXT,
    user_email  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sp_agent_routing (
    id          BIGSERIAL PRIMARY KEY,
    agent_code  TEXT NOT NULL,
    sp_folder   TEXT NOT NULL,
    pattern     TEXT NOT NULL
);

-- Sessões de invocação do Canvas (POST /agents/{slug}/invoke): uma linha
-- por prompt+resposta completa, gravada quando o streaming SSE termina.
CREATE TABLE IF NOT EXISTS agent_sessions (
    id          UUID PRIMARY KEY,
    agent_code  TEXT NOT NULL,
    agent_slug  TEXT NOT NULL,
    prompt      TEXT NOT NULL,
    response    TEXT NOT NULL,
    user_email  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_sessions_slug ON agent_sessions (agent_slug);
