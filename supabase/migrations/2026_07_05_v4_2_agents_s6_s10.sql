-- Manta Maestro v4.2 — expansão de agentes S6-S10
-- Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN. Ajustar `assumes existing schema` conforme o schema
-- real do Supabase; nem toda coluna abaixo é obrigatória.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql
--
-- ROLLBACK: as inserções são idempotentes via `ON CONFLICT DO NOTHING`;
-- para desfazer, ver bloco DOWN no fim deste arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Registro das 5 novas coleções RAG
-- ---------------------------------------------------------------------
-- Assumes existing table `rag_collections(slug TEXT PRIMARY KEY,
--   name TEXT, storage_prefix TEXT, initial_sources JSONB, created_at
--   TIMESTAMPTZ DEFAULT NOW())`. Se o schema for diferente
-- (por exemplo, coluna única `collection` em `rag_chunks`), adaptar.

INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('saneamento',  'Saneamento',  'san:', jsonb_build_array(
     'SNIS',
     'IWA',
     'NBR 12211 — Abastecimento de Água (Concepção)',
     'NBR 12212 — Poço Tubular',
     'NBR 12213 — Adução de Água',
     'NBR 12214 — Bombeamento de Água',
     'NBR 12215 — Adução e Distribuição de Água',
     'NBR 12216 — ETA (Estação de Tratamento de Água)',
     'NBR 12217 — Reservatório de Distribuição',
     'NBR 12218 — Rede de Distribuição de Água',
     'Lei 14.026/2020',
     'Editais BNDES saneamento',
     'ERAS/AySA (Argentina)'
   )),
  ('energia',     'Energia',     'ene:', jsonb_build_array(
     'ANEEL editais',
     'EPE (Empresa de Pesquisa Energética) — R1-R5 (Relatórios de Planejamento)',
     'ONS relatórios de operação',
     'IEEE standards (738, 80, 60826)',
     'NBR 5422'
   )),
  ('portos',      'Portos',      'por:', jsonb_build_array(
     'ANTAQ resoluções',
     'PIANC reports',
     'Editais BNDES/ANTAQ arrendamentos',
     'ROM 0.2, ROM 2.0',
     'NBR 9782, NBR 6122'
   )),
  ('aeroportos',  'Aeroportos',  'aer:', jsonb_build_array(
     'ANAC RBAC 154',
     'ICAO Annex 14',
     'FAA ACs (150/5300, 150/5320, 150/5340)',
     'ICAO Doc 9157',
     'DECEA ICA 100-12'
   )),
  ('barragens',   'Barragens',   'bar:', jsonb_build_array(
     'ICOLD bulletins',
     'CBDB cadernos técnicos',
     'SIGBM (ANM)',
     'SNISB (ANA)',
     'Lei 12.334/2010 + Lei 14.066/2020',
     'NBR 13028, NBR 8681'
   ))
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. Regras de routing SharePoint (sp_agent_routing)
-- ---------------------------------------------------------------------
-- Assumes existing table `sp_agent_routing(agent_slug TEXT PRIMARY KEY,
--   sp_folder TEXT NOT NULL, file_patterns TEXT[] NOT NULL,
--   priority INTEGER DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW())`.

INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('agente-saneamento',  '03_Projetos/Saneamento/*',  ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-energia',     '03_Projetos/Energia/*',     ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-portos',      '03_Projetos/Portos/*',      ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-aeroportos',  '03_Projetos/Aeroportos/*',  ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-barragens',   '03_Projetos/Barragens/*',   ARRAY['*.pdf','*.dwg','*.xlsx'], 100)
ON CONFLICT (agent_slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 3. Registro das palavras-chave de routing do Maestro (opcional)
-- ---------------------------------------------------------------------
-- Assumes existing table `maestro_routing_keywords(agent_slug TEXT,
--   keyword TEXT, priority INTEGER, PRIMARY KEY (agent_slug, keyword))`.
-- Comentar o bloco inteiro caso o Maestro carregue as keywords direto
-- do CLAUDE.md via parsing.

INSERT INTO maestro_routing_keywords (agent_slug, keyword, priority) VALUES
  -- Saneamento (S8)
  ('agente-saneamento', 'saneamento',        100),
  ('agente-saneamento', 'ETA',               100),
  ('agente-saneamento', 'ETE',               100),
  ('agente-saneamento', 'adutora',           100),
  ('agente-saneamento', 'esgoto',            100),
  ('agente-saneamento', 'AySA',              120),
  ('agente-saneamento', 'drenagem urbana',    95),
  ('agente-saneamento', 'SNIS',              100),
  -- Energia (S9)
  ('agente-energia',    'transmissão',       100),
  ('agente-energia',    'LT',                 90),
  ('agente-energia',    'subestação',        100),
  ('agente-energia',    'ANEEL',             100),
  ('agente-energia',    'RAP',                90),
  ('agente-energia',    'leilão transmissão', 95),
  ('agente-energia',    'ONS',                90),
  ('agente-energia',    'EPE',                90),
  -- Portos (S6)
  ('agente-portos',     'porto',              80),
  ('agente-portos',     'terminal',           70),
  ('agente-portos',     'ANTAQ',             100),
  ('agente-portos',     'dragagem',          100),
  ('agente-portos',     'molhe',             100),
  ('agente-portos',     'berço',              90),
  ('agente-portos',     'calado',             90),
  ('agente-portos',     'contêiner',          80),
  ('agente-portos',     'granel',             80),
  -- Aeroportos (S7)
  ('agente-aeroportos', 'aeroporto',         100),
  ('agente-aeroportos', 'pista pouso',       100),
  ('agente-aeroportos', 'ANAC',              100),
  ('agente-aeroportos', 'ICAO',              100),
  ('agente-aeroportos', 'TPS',                90),
  ('agente-aeroportos', 'TECA',               90),
  ('agente-aeroportos', 'balizamento',       100),
  -- Barragens (S10)
  ('agente-barragens',  'barragem',          100),
  ('agente-barragens',  'vertedouro',        100),
  ('agente-barragens',  'CFRD',              100),
  ('agente-barragens',  'CCR',                80),
  ('agente-barragens',  'rejeitos',          110),
  ('agente-barragens',  'PNSB',              100),
  ('agente-barragens',  'ICOLD',             100),
  ('agente-barragens',  'CBDB',              100),
  ('agente-barragens',  'TSF',               100)
ON CONFLICT (agent_slug, keyword) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM maestro_routing_keywords WHERE agent_slug IN
--   ('agente-saneamento','agente-energia','agente-portos',
--    'agente-aeroportos','agente-barragens');
--
-- DELETE FROM sp_agent_routing WHERE agent_slug IN
--   ('agente-saneamento','agente-energia','agente-portos',
--    'agente-aeroportos','agente-barragens');
--
-- DELETE FROM rag_collections WHERE slug IN
--   ('saneamento','energia','portos','aeroportos','barragens');
--
-- COMMIT;
