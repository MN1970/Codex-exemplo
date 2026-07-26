-- Manta Maestro v4.2 — ROLLBACK da migração S6-S10
-- Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
--
-- Reverte apenas as LINHAS inseridas pela migração de dados
-- (2026_07_05_v4_2_agents_s6_s10.sql). NÃO dropa as tabelas criadas
-- pelo prereq (00_prereq_schema.sql) — isso é opcional e está
-- comentado no fim deste arquivo, pois outras coleções/rotas podem já
-- ter sido adicionadas às mesmas tabelas depois do deploy inicial.
--
-- Uso:
--   psql "$SUPABASE_DB_URL" -f 2026_07_05_v4_2_agents_s6_s10_rollback.sql
--
-- Seguro para rodar mesmo se a migração nunca tiver sido aplicada
-- (DELETE de 0 linhas não é erro).

BEGIN;

-- Checagem prévia: quantas linhas serão afetadas (log informativo).
-- Não falha a transação; serve apenas de registro no output do psql.
SELECT 'maestro_routing_keywords' AS tabela, COUNT(*) AS linhas_a_remover
FROM maestro_routing_keywords
WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens')
UNION ALL
SELECT 'sp_agent_routing', COUNT(*)
FROM sp_agent_routing
WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens')
UNION ALL
SELECT 'rag_collections', COUNT(*)
FROM rag_collections
WHERE slug IN ('saneamento', 'energia', 'portos', 'aeroportos', 'barragens');

DELETE FROM maestro_routing_keywords WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens');

DELETE FROM sp_agent_routing WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens');

DELETE FROM rag_collections WHERE slug IN
  ('saneamento', 'energia', 'portos', 'aeroportos', 'barragens');

-- Checagem pós-delete: deve retornar 0 em todas as 3 linhas.
SELECT 'maestro_routing_keywords' AS tabela, COUNT(*) AS linhas_restantes
FROM maestro_routing_keywords
WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens')
UNION ALL
SELECT 'sp_agent_routing', COUNT(*)
FROM sp_agent_routing
WHERE agent_slug IN
  ('agente-saneamento', 'agente-energia', 'agente-portos',
   'agente-aeroportos', 'agente-barragens')
UNION ALL
SELECT 'rag_collections', COUNT(*)
FROM rag_collections
WHERE slug IN ('saneamento', 'energia', 'portos', 'aeroportos', 'barragens');

COMMIT;

-- =====================================================================
-- OPCIONAL — dropar as tabelas inteiras (só se foram criadas
-- exclusivamente para esta feature e nada mais as usa; CONFIRMAR
-- com list_tables antes de descomentar e rodar isoladamente).
-- =====================================================================
-- BEGIN;
-- DROP TABLE IF EXISTS maestro_routing_keywords;
-- DROP TABLE IF EXISTS sp_agent_routing;
-- DROP TABLE IF EXISTS rag_collections;
-- COMMIT;
