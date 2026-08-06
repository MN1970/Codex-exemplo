-- =====================================================================
-- VALIDATION CHECKS para migração v4.2 Agentes S6-S10
-- =====================================================================
-- Execute ANTES de aplicar a migração em PROD

-- 1. VERIFICAR SCHEMA (execute em qualquer banco Supabase)
-- =====================================================================

-- Confirmar que as 3 tabelas existem
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('rag_collections', 'sp_agent_routing', 'maestro_routing_keywords')
ORDER BY table_name;

-- Detalhar schema de rag_collections
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'rag_collections'
ORDER BY ordinal_position;

-- Detalhar schema de sp_agent_routing
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'sp_agent_routing'
ORDER BY ordinal_position;

-- Detalhar schema de maestro_routing_keywords
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'maestro_routing_keywords'
ORDER BY ordinal_position;

-- 2. VERIFICAR CONSTRAINTS
-- =====================================================================

-- Listar PRIMARY KEYs
SELECT table_name, constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name IN ('rag_collections', 'sp_agent_routing', 'maestro_routing_keywords')
  AND constraint_type = 'PRIMARY KEY'
ORDER BY table_name;

-- Listar FKs (se houver)
SELECT constraint_name, table_name, column_name
FROM information_schema.key_column_usage
WHERE table_name IN ('rag_collections', 'sp_agent_routing', 'maestro_routing_keywords')
  AND referenced_table_name IS NOT NULL
ORDER BY table_name, column_name;

-- 3. VERIFICAR DADOS ANTES (contagens)
-- =====================================================================

SELECT
  (SELECT COUNT(*) FROM rag_collections) as rag_collections_count,
  (SELECT COUNT(*) FROM sp_agent_routing) as sp_routing_count,
  (SELECT COUNT(*) FROM maestro_routing_keywords) as maestro_keywords_count;

-- 4. EXECUTAR MIGRAÇÃO
-- =====================================================================
-- Copiar/executar o arquivo supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql

-- 5. VERIFICAR DADOS DEPOIS (validar)
-- =====================================================================

-- Contagem esperada: +5 RAG collections
SELECT COUNT(*) as expected_5 FROM rag_collections
WHERE slug IN ('saneamento','energia','portos','aeroportos','barragens');

-- Contagem esperada: +5 SP routing rules
SELECT COUNT(*) as expected_5 FROM sp_agent_routing
WHERE agent_slug IN ('agente-saneamento','agente-energia','agente-portos',
                      'agente-aeroportos','agente-barragens');

-- Contagem esperada: +41 maestro keywords
SELECT COUNT(*) as expected_41 FROM maestro_routing_keywords
WHERE agent_slug IN ('agente-saneamento','agente-energia','agente-portos',
                      'agente-aeroportos','agente-barragens');

-- Detalhe: RAG collections
SELECT slug, name, storage_prefix, created_at
FROM rag_collections
WHERE slug IN ('saneamento','energia','portos','aeroportos','barragens')
ORDER BY slug;

-- Detalhe: SP routing rules
SELECT agent_slug, sp_folder, priority, created_at
FROM sp_agent_routing
WHERE agent_slug IN ('agente-saneamento','agente-energia','agente-portos',
                      'agente-aeroportos','agente-barragens')
ORDER BY agent_slug;

-- Detalhe: Maestro keywords por agente
SELECT agent_slug, COUNT(*) as keyword_count, MIN(priority) as min_prio, MAX(priority) as max_prio
FROM maestro_routing_keywords
WHERE agent_slug IN ('agente-saneamento','agente-energia','agente-portos',
                      'agente-aeroportos','agente-barragens')
GROUP BY agent_slug
ORDER BY agent_slug;

-- 6. TESTAR ROLLBACK (APENAS EM DEV)
-- =====================================================================
-- Executar em uma transação separada após confirmar INSERT:

BEGIN;

DELETE FROM maestro_routing_keywords WHERE agent_slug IN
  ('agente-saneamento','agente-energia','agente-portos',
   'agente-aeroportos','agente-barragens');

DELETE FROM sp_agent_routing WHERE agent_slug IN
  ('agente-saneamento','agente-energia','agente-portos',
   'agente-aeroportos','agente-barragens');

DELETE FROM rag_collections WHERE slug IN
  ('saneamento','energia','portos','aeroportos','barragens');

COMMIT;

-- Verificar que tudo foi deletado
SELECT COUNT(*) as should_be_0 FROM rag_collections
WHERE slug IN ('saneamento','energia','portos','aeroportos','barragens');
