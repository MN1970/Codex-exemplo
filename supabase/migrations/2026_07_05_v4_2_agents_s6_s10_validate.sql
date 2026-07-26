-- Manta Maestro v4.2 — Queries de validação pós-deploy
-- Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
--
-- Rodar após aplicar (1) 00_prereq_schema.sql e (2)
-- 2026_07_05_v4_2_agents_s6_s10.sql. Todas as queries devem retornar
-- exatamente as contagens indicadas em "Esperado". Qualquer desvio
-- interrompe o runbook antes da etapa 3 (SharePoint).

-- ---------------------------------------------------------------------
-- V1. Pré-checagem de schema (rodar ANTES do deploy, não depois)
-- ---------------------------------------------------------------------
-- Esperado antes do prereq: 0 linhas. Esperado depois do prereq: 3 linhas.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('rag_collections', 'sp_agent_routing', 'maestro_routing_keywords')
ORDER BY table_name;

-- ---------------------------------------------------------------------
-- V2. Coleções RAG — 5 linhas, uma por segmento novo
-- ---------------------------------------------------------------------
-- Esperado: 5 linhas, storage_prefix único, sources >= 1 cada.
SELECT slug, storage_prefix, jsonb_array_length(initial_sources) AS n_sources
FROM rag_collections
WHERE slug IN ('saneamento', 'energia', 'portos', 'aeroportos', 'barragens')
ORDER BY slug;

-- V2b. Nenhum slug duplicado / nenhum storage_prefix colidindo com
-- coleções pré-existentes (S1-S4, horizontais).
SELECT storage_prefix, COUNT(*) AS n
FROM rag_collections
GROUP BY storage_prefix
HAVING COUNT(*) > 1;
-- Esperado: 0 linhas.

-- ---------------------------------------------------------------------
-- V3. Routing SharePoint — 5 linhas, uma por agente novo
-- ---------------------------------------------------------------------
SELECT agent_slug, sp_folder, priority, array_length(file_patterns, 1) AS n_patterns
FROM sp_agent_routing
WHERE agent_slug IN (
  'agente-saneamento', 'agente-energia', 'agente-portos',
  'agente-aeroportos', 'agente-barragens'
)
ORDER BY agent_slug;
-- Esperado: 5 linhas, priority = 100, n_patterns = 3 em cada.

-- ---------------------------------------------------------------------
-- V4. Palavras-chave de roteamento — 41 linhas no total
-- ---------------------------------------------------------------------
-- Contagem por agente (valores esperados entre parênteses):
--   agente-saneamento  -> 8
--   agente-energia     -> 8
--   agente-portos      -> 9
--   agente-aeroportos  -> 7
--   agente-barragens   -> 9
--   TOTAL              -> 41
SELECT agent_slug, COUNT(*) AS n_keywords
FROM maestro_routing_keywords
WHERE agent_slug IN (
  'agente-saneamento', 'agente-energia', 'agente-portos',
  'agente-aeroportos', 'agente-barragens'
)
GROUP BY agent_slug
ORDER BY agent_slug;

-- V4b. Nenhuma keyword duplicada para o mesmo agente (o PK composto já
-- garante isso, mas confirmar explicitamente após o deploy).
SELECT agent_slug, keyword, COUNT(*)
FROM maestro_routing_keywords
GROUP BY agent_slug, keyword
HAVING COUNT(*) > 1;
-- Esperado: 0 linhas.

-- V4c. Nenhuma keyword nova colide com keyword de agente já existente
-- (S1-S4 / horizontais) — checagem de ambiguidade de routing.
SELECT keyword, array_agg(agent_slug ORDER BY agent_slug) AS agentes
FROM maestro_routing_keywords
GROUP BY keyword
HAVING COUNT(DISTINCT agent_slug) > 1;
-- Não é necessariamente um erro (ex.: "CCR" pode ser usado por mais de
-- um segmento), mas toda linha aqui deve ser revisada manualmente
-- contra os "casos ambíguos" citados em docs/DEPLOY-v4.2.md secao 5.

-- ---------------------------------------------------------------------
-- V5. Nenhum agente novo ausente de nenhuma das 3 tabelas
-- (checagem cruzada de completude)
-- ---------------------------------------------------------------------
WITH esperados(agent_slug) AS (
  VALUES ('agente-saneamento'), ('agente-energia'), ('agente-portos'),
         ('agente-aeroportos'), ('agente-barragens')
)
SELECT e.agent_slug,
       EXISTS (SELECT 1 FROM sp_agent_routing r WHERE r.agent_slug = e.agent_slug) AS tem_routing,
       EXISTS (SELECT 1 FROM maestro_routing_keywords k WHERE k.agent_slug = e.agent_slug) AS tem_keywords
FROM esperados e
ORDER BY e.agent_slug;
-- Esperado: tem_routing = true e tem_keywords = true em todas as 5 linhas.
