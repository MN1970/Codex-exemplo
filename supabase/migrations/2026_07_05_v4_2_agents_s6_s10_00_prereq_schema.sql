-- Manta Maestro v4.2 — PRÉ-REQUISITO de schema para a migração S6-S10
-- Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
--
-- MIGRAÇÃO CANDIDATA — NÃO APLICAR SEM APROVAÇÃO MN.
--
-- MOTIVO DESTE ARQUIVO
-- --------------------
-- A migração 2026_07_05_v4_2_agents_s6_s10.sql assume a existência de
-- três tabelas (rag_collections, sp_agent_routing,
-- maestro_routing_keywords). Verificação ao vivo no projeto Supabase
-- "manta-maestro" (project_id ogxxgvgtulrbbppshjie, ACTIVE_HEALTHY) em
-- 2026-07-26 confirmou que NENHUMA das três existe:
--
--   SELECT table_name FROM information_schema.tables
--   WHERE table_schema='public'
--     AND table_name IN ('rag_collections','sp_agent_routing',
--                         'maestro_routing_keywords');
--   -> 0 linhas
--
-- O schema real do projeto usa outra convenção de nomes (prefixo
-- manta_*: manta_rag_documents, manta_rag_chunks,
-- manta_agent_capabilities, manta_trace, manta_projects, ...). As três
-- tabelas abaixo são NOVAS relações a criar, não "adaptação de nomes
-- de coluna" como o comentário original do .sql sugeria.
--
-- Este arquivo cria as três tabelas com CREATE TABLE IF NOT EXISTS,
-- casando exatamente com as colunas assumidas pela migração de dados
-- (2026_07_05_v4_2_agents_s6_s10.sql), para que ela possa rodar sem
-- alteração. NÃO renomeia para o padrão manta_* — decisão de
-- convenção de nomes deve ser tomada pelo arquiteto (manta-15-arq)
-- e pelo MN, não unilateralmente aqui.
--
-- ORDEM DE APLICAÇÃO (ver runbook):
--   1. Este arquivo (00_prereq_schema.sql)   <- cria as tabelas
--   2. 2026_07_05_v4_2_agents_s6_s10.sql     <- popula os dados (INSERT ... ON CONFLICT DO NOTHING)
--   3. 2026_07_05_v4_2_agents_s6_s10_validate.sql <- confirma o resultado
--
-- Rollback correspondente: 2026_07_05_v4_2_agents_s6_s10_rollback.sql
-- (dropa apenas as linhas inseridas por padrão; DROP TABLE é opcional
-- e comentado, ver seção final).

BEGIN;

-- ---------------------------------------------------------------------
-- 1. rag_collections — registro de coleções RAG (Supabase pgvector)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rag_collections (
  slug            TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  storage_prefix  TEXT NOT NULL,
  initial_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE rag_collections IS
  'Registro mestre das coleções RAG do Manta Maestro (uma por segmento/eixo horizontal). Populado via migração de dados v4.2 (S6-S10) e correspondentes futuras.';

-- ---------------------------------------------------------------------
-- 2. sp_agent_routing — regras de roteamento SharePoint por agente
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sp_agent_routing (
  agent_slug     TEXT PRIMARY KEY,
  sp_folder      TEXT NOT NULL,
  file_patterns  TEXT[] NOT NULL,
  priority       INTEGER NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sp_agent_routing IS
  'Mapeia agent_slug -> pasta SharePoint + padrões de arquivo para ingestão automática. Um agente por linha.';

-- ---------------------------------------------------------------------
-- 3. maestro_routing_keywords — palavras-chave de roteamento do Maestro
-- ---------------------------------------------------------------------
-- Ver comentário no arquivo de dados: esta tabela só é necessária se o
-- Maestro (Manta 00) carregar as regras de roteamento do banco em vez
-- de parsear o bloco ROUTING do CLAUDE.md master em tempo de execução.
-- Confirmar com o arquiteto (manta-15-arq / manta-arquiteto-ia) antes
-- de aplicar esta seção — se o parsing direto do CLAUDE.md for o
-- padrão adotado, comentar/pular este CREATE TABLE e a correspondente
-- seção 3 da migração de dados.

CREATE TABLE IF NOT EXISTS maestro_routing_keywords (
  agent_slug  TEXT NOT NULL,
  keyword     TEXT NOT NULL,
  priority    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (agent_slug, keyword)
);

COMMENT ON TABLE maestro_routing_keywords IS
  'Palavras-chave de roteamento do Maestro (Q1 do intake), usadas apenas se o Manta 00 não parsear o CLAUDE.md diretamente.';

-- Índices de apoio (consultas mais comuns: lookup por agente, lookup
-- por keyword em ILIKE de prompt do usuário).
CREATE INDEX IF NOT EXISTS idx_sp_agent_routing_priority
  ON sp_agent_routing (priority DESC);

CREATE INDEX IF NOT EXISTS idx_maestro_routing_keywords_keyword
  ON maestro_routing_keywords (keyword);

COMMIT;

-- =====================================================================
-- ROLLBACK deste arquivo (executar manualmente, só se as tabelas foram
-- criadas por ESTE arquivo e estiverem vazias/seguras para remover)
-- =====================================================================
-- BEGIN;
-- DROP TABLE IF EXISTS maestro_routing_keywords;
-- DROP TABLE IF EXISTS sp_agent_routing;
-- DROP TABLE IF EXISTS rag_collections;
-- COMMIT;
