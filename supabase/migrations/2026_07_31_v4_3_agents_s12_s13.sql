-- Manta Maestro v4.3 — formalização de S12 (Óleo & Gás) e S13 (Edificações)
-- Ticket: G014 (gap de documentação S12/S13)
-- Autor: Sonnet 12 — ver docs/SEGMENTOS-S12-S13-DECISION.md para o
-- racional completo desta migração.
--
-- CONTEXTO: os agent_id '03-S12' e '03-S13' JÁ EXISTEM e estão
-- `ativo = true` em `manta_agent_capabilities` (registrados em
-- 2026-07-12, confirmado por query direta nesta investigação). Este
-- arquivo NÃO cria os agentes — apenas fecha o gap de infraestrutura
-- de apoio (RAG collection, SharePoint routing, routing keywords) que
-- falta para que o Maestro consiga de fato despachar para eles.
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN (mesmo processo do
-- `2026_07_05_v4_2_agents_s6_s10.sql`).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql
--
-- ROLLBACK: inserções idempotentes via `ON CONFLICT DO NOTHING`; ver
-- bloco DOWN no fim deste arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Registro das 2 novas coleções RAG
-- ---------------------------------------------------------------------

INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('oleo-gas',    'Óleo & Gás', 'og:', jsonb_build_array(
     'ANP resoluções (distribuição, autorização de dutovias)',
     'API 650 / API 653 (tanques atmosféricos)',
     'ANSI/ASME B31.3, B31.4, B31.8 (tubulação e dutovias)',
     'NFPA 30, NFPA 15/16 (líquidos inflamáveis, proteção contra incêndio)',
     'NR-20, NR-13',
     'Metodologia HAZOP'
   )),
  ('edificacoes', 'Edificações', 'edi:', jsonb_build_array(
     'NBR 15575 (desempenho de edificações habitacionais / MCMV)',
     'NBR 6118, NBR 8800, NBR 6120',
     'LEED (USGBC/GBC Brasil)',
     'Decreto 10.306/2020 (BIM em licitação pública)',
     'NBR 9050 (acessibilidade)'
   ))
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. Regras de routing SharePoint (sp_agent_routing)
-- ---------------------------------------------------------------------

INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('agente-oleo-gas',    '03_Projetos/OleoGas/*',     ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-edificacoes', '03_Projetos/Edificacoes/*', ARRAY['*.pdf','*.dwg','*.xlsx'], 100)
ON CONFLICT (agent_slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 3. Palavras-chave de routing do Maestro
-- ---------------------------------------------------------------------

INSERT INTO maestro_routing_keywords (agent_slug, keyword, priority) VALUES
  -- Óleo & Gás (S12) — downstream + midstream apenas, NÃO upstream/E&P
  ('agente-oleo-gas',    'petróleo',         90),
  ('agente-oleo-gas',    'óleo e gás',      100),
  ('agente-oleo-gas',    'gasoduto',        100),
  ('agente-oleo-gas',    'oleoduto',        100),
  ('agente-oleo-gas',    'dutovia',          95),
  ('agente-oleo-gas',    'refinaria',       100),
  ('agente-oleo-gas',    'ANP',             100),
  ('agente-oleo-gas',    'API 650',         100),
  ('agente-oleo-gas',    'HAZOP',            90),
  -- Edificações (S13)
  ('agente-edificacoes', 'edificação',      100),
  ('agente-edificacoes', 'galpão',           90),
  ('agente-edificacoes', 'warehouse',        85),
  ('agente-edificacoes', 'data center',      85),
  ('agente-edificacoes', 'MCMV',            100),
  ('agente-edificacoes', 'NBR 15575',       100),
  ('agente-edificacoes', 'LEED',             90),
  ('agente-edificacoes', 'BIM de edificação', 80)
ON CONFLICT (agent_slug, keyword) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM maestro_routing_keywords WHERE agent_slug IN
--   ('agente-oleo-gas','agente-edificacoes');
--
-- DELETE FROM sp_agent_routing WHERE agent_slug IN
--   ('agente-oleo-gas','agente-edificacoes');
--
-- DELETE FROM rag_collections WHERE slug IN
--   ('oleo-gas','edificacoes');
--
-- COMMIT;
