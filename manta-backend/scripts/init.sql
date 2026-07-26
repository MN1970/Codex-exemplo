-- init.sql — bootstrap do banco local (docker-compose) para o Manta Backend.
-- Espelha as 5 coleções RAG e as tabelas usadas pelos routers.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_chunks (
    id          BIGSERIAL PRIMARY KEY,
    collection  TEXT NOT NULL,       -- saneamento | energia | portos | aeroportos | barragens
    prefix      TEXT NOT NULL,       -- san: | ene: | por: | aer: | bar:
    content     TEXT NOT NULL,
    embedding   vector(1536),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection ON rag_chunks (collection);

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
