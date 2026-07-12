-- Manta Maestro v4.4 — expansão de verticais S5 + S11 + S12 + S13
-- Ticket: MNT-2026-UPGRADE-VERTICALS-S5-S11-S12-S13
--
-- Adiciona 4 novos agentes verticais em cima dos 5 da v4.2 e do
-- academic-knowledge da v4.3:
--   - agente-tuneis (S5, prefixo tun:)          — antes ⚡ parcial, agora ✅
--   - agente-mineracao (S11, prefixo min:)      — adjacente S10
--   - agente-oleo-gas (S12, prefixo ogs:)       — downstream/midstream
--   - agente-edificacoes (S13, prefixo edi:)    — vertical + galpão
--
-- MIGRAÇÃO CANDIDATA. Aditiva sobre v4.2 (stages S6-S10),
-- v4.3 stages 4-6 (AKP + hybrid + telemetry). Idempotente via ON CONFLICT.
--
-- Executar:
--   supabase db push
--   -- ou --
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_12_verticals_v4_4.sql
--
-- ROLLBACK: bloco DOWN no fim.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Novas coleções RAG (transparente ao motor v4.2)
-- ---------------------------------------------------------------------
INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('tuneis', 'Túneis', 'tun:', jsonb_build_array(
     'ITA/AITES guidelines',
     'PIARC C4 (túneis rodoviários)',
     'NFPA 502 (fire in transportation tunnels)',
     'NBR 15220 (segurança em túneis rodoviários)',
     'DNIT IPR-742',
     'DER-SP Instrução de Serviço para túneis',
     'FHWA Tunnel Manual'
   )),
  ('mineracao', 'Mineração', 'min:', jsonb_build_array(
     'ANM NRM-01..NRM-22',
     'NR-22 MTE (Segurança em Mineração)',
     'Código de Mineração (Decreto-Lei 227/1967)',
     'SME Mining Engineering Handbook',
     'CIM Estimation of Mineral Resources',
     'JORC 2012 + NI 43-101 + PERC + SEC K-1300',
     'Read & Stacey Guidelines for Open Pit Slope Design',
     'Wills Mineral Processing Technology'
   )),
  ('oleo-gas', 'Óleo e Gás', 'ogs:', jsonb_build_array(
     'ANP Resoluções (6/2011, 41/2017, 807/2020, 858/2022)',
     'Lei 9.478/1997 (marco regulatório)',
     'API 650, API 653, API 5L, API RP 14C/500/580/581',
     'ANSI B31.3, B31.4, B31.8',
     'NFPA 30 (líquidos inflamáveis), NFPA 59A (LNG)',
     'IEC 60079 (áreas classificadas), IEC 61511 (SIL)',
     'OSHA 1910.119 (PSM)'
   )),
  ('edificacoes', 'Edificações', 'edi:', jsonb_build_array(
     'NBR 6118 (concreto), NBR 8800 (aço), NBR 6120 (cargas)',
     'NBR 6122 (fundações), NBR 15421 (sísmica)',
     'NBR 15575 (desempenho — MCMV)',
     'NBR 9077 (saídas), NBR 14432 (fogo)',
     'IT-CBMESP + Selo Casa Azul CAIXA',
     'LEED v4.1, AQUA-HQE, EDGE, ISO 19650, IFC 4.3',
     'Decreto 10.306/2020 (BIM BR)'
   ))
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. SharePoint routing p/ os 4 novos verticais
-- ---------------------------------------------------------------------
INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('agente-tuneis',      '03_Projetos/Tuneis/*',      ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-mineracao',   '03_Projetos/Mineracao/*',   ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-oleo-gas',    '03_Projetos/OleoGas/*',     ARRAY['*.pdf','*.dwg','*.xlsx'], 100),
  ('agente-edificacoes', '03_Projetos/Edificacoes/*', ARRAY['*.pdf','*.dwg','*.xlsx'], 100)
ON CONFLICT (agent_slug) DO NOTHING;

-- ---------------------------------------------------------------------
-- 3. Palavras-chave do Maestro (opcional — depende do schema real)
-- ---------------------------------------------------------------------
INSERT INTO maestro_routing_keywords (agent_slug, keyword, priority) VALUES
  -- Túneis (S5)
  ('agente-tuneis', 'túnel',                100),
  ('agente-tuneis', 'tunel',                100),
  ('agente-tuneis', 'NATM',                 100),
  ('agente-tuneis', 'TBM',                  100),
  ('agente-tuneis', 'EPB',                   90),
  ('agente-tuneis', 'shotcrete',             90),
  ('agente-tuneis', 'dovela',                95),
  ('agente-tuneis', 'cut and cover',         90),
  ('agente-tuneis', 'imerso',                85),
  ('agente-tuneis', 'convergência',          85),
  ('agente-tuneis', 'PIARC',                 90),
  ('agente-tuneis', 'ITA',                   80),
  ('agente-tuneis', 'NFPA 502',              95),
  ('agente-tuneis', 'Marcello Alencar',      80),
  ('agente-tuneis', 'Linha 4',               75),
  ('agente-tuneis', 'Linha 6',               75),
  ('agente-tuneis', 'Rodoanel túnel',        80),
  -- Mineração (S11)
  ('agente-mineracao', 'mineração',         100),
  ('agente-mineracao', 'mineracao',         100),
  ('agente-mineracao', 'mina',               95),
  ('agente-mineracao', 'minério',            95),
  ('agente-mineracao', 'minerio',            95),
  ('agente-mineracao', 'ANM',               100),
  ('agente-mineracao', 'DNPM',               90),
  ('agente-mineracao', 'NI 43-101',         100),
  ('agente-mineracao', 'JORC',              100),
  ('agente-mineracao', 'PERC',               95),
  ('agente-mineracao', 'cava',               85),
  ('agente-mineracao', 'open pit',           90),
  ('agente-mineracao', 'moagem SAG',         90),
  ('agente-mineracao', 'flotação',           85),
  ('agente-mineracao', 'flotacao',           85),
  ('agente-mineracao', 'heap leach',         90),
  ('agente-mineracao', 'CIL',                80),
  ('agente-mineracao', 'LOM',                85),
  ('agente-mineracao', 'block caving',       90),
  ('agente-mineracao', 'Vale',               75),
  ('agente-mineracao', 'Carajás',            85),
  ('agente-mineracao', 'Salobo',             80),
  ('agente-mineracao', 'Anglo American',     75),
  ('agente-mineracao', 'Minas Rio',          80),
  -- Óleo & Gás (S12)
  ('agente-oleo-gas', 'petróleo',           100),
  ('agente-oleo-gas', 'petroleo',           100),
  ('agente-oleo-gas', 'gás natural',        100),
  ('agente-oleo-gas', 'gas natural',        100),
  ('agente-oleo-gas', 'óleo e gás',         100),
  ('agente-oleo-gas', 'oleo gas',           100),
  ('agente-oleo-gas', 'o&g',                 95),
  ('agente-oleo-gas', 'ANP',                100),
  ('agente-oleo-gas', 'GASBOL',              95),
  ('agente-oleo-gas', 'gasoduto',           100),
  ('agente-oleo-gas', 'oleoduto',           100),
  ('agente-oleo-gas', 'poliduto',            95),
  ('agente-oleo-gas', 'refino',              95),
  ('agente-oleo-gas', 'refinaria',           95),
  ('agente-oleo-gas', 'Comperj',             90),
  ('agente-oleo-gas', 'Rnest',               85),
  ('agente-oleo-gas', 'Replan',              85),
  ('agente-oleo-gas', 'Reduc',               85),
  ('agente-oleo-gas', 'Rlam',                85),
  ('agente-oleo-gas', 'API 650',             95),
  ('agente-oleo-gas', 'API 5L',              90),
  ('agente-oleo-gas', 'API 653',             90),
  ('agente-oleo-gas', 'ANSI B31',            90),
  ('agente-oleo-gas', 'NFPA 30',             90),
  ('agente-oleo-gas', 'LNG',                 90),
  ('agente-oleo-gas', 'HAZOP',               95),
  ('agente-oleo-gas', 'HDD',                 85),
  ('agente-oleo-gas', 'city gate',           85),
  ('agente-oleo-gas', 'UPGN',                85),
  ('agente-oleo-gas', 'monoboia',            80),
  -- Edificações (S13)
  ('agente-edificacoes', 'edificação',      100),
  ('agente-edificacoes', 'edificacao',      100),
  ('agente-edificacoes', 'predial',          90),
  ('agente-edificacoes', 'torre',            90),
  ('agente-edificacoes', 'galpão',           95),
  ('agente-edificacoes', 'galpao',           95),
  ('agente-edificacoes', 'warehouse',        90),
  ('agente-edificacoes', 'cross-dock',       85),
  ('agente-edificacoes', 'data center',      90),
  ('agente-edificacoes', 'hospital',         85),
  ('agente-edificacoes', 'universidade',     80),
  ('agente-edificacoes', 'MCMV',            100),
  ('agente-edificacoes', 'NBR 15575',       105),
  ('agente-edificacoes', 'NBR 6118',         85),
  ('agente-edificacoes', 'NBR 8800',         85),
  ('agente-edificacoes', 'MRV',              80),
  ('agente-edificacoes', 'Cyrela',           80),
  ('agente-edificacoes', 'Even',             75),
  ('agente-edificacoes', 'LEED',             95),
  ('agente-edificacoes', 'AQUA',             85),
  ('agente-edificacoes', 'Selo Casa Azul',   90),
  ('agente-edificacoes', 'curtain wall',     85),
  ('agente-edificacoes', 'alvenaria estrutural', 85),
  ('agente-edificacoes', 'laje protendida',  80),
  ('agente-edificacoes', 'hélice contínua',  75),
  ('agente-edificacoes', 'BIM',              85),
  ('agente-edificacoes', 'Revit',            75),
  ('agente-edificacoes', 'CBMESP',           90),
  ('agente-edificacoes', 'sprinkler',        80)
ON CONFLICT (agent_slug, keyword) DO NOTHING;

-- ---------------------------------------------------------------------
-- 4. Bindings à coleção academic-knowledge (herda comportamento v4.3)
-- ---------------------------------------------------------------------
-- Só executa se v4.3 já foi aplicada (tabela agent_rag_bindings existe).
-- Pulamos silenciosamente se não existir para não quebrar o rollout ordenado.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
     WHERE table_schema='public' AND table_name='agent_rag_bindings'
  ) THEN
    INSERT INTO agent_rag_bindings (agent_slug, collection_slug, role, priority) VALUES
      ('agente-tuneis',      'academic-knowledge', 'auxiliary', 100),
      ('agente-mineracao',   'academic-knowledge', 'auxiliary', 100),
      ('agente-oleo-gas',    'academic-knowledge', 'auxiliary', 100),
      ('agente-edificacoes', 'academic-knowledge', 'auxiliary', 100)
    ON CONFLICT (agent_slug, collection_slug) DO NOTHING;
  END IF;
END $$;

COMMIT;

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM agent_rag_bindings WHERE agent_slug IN
--   ('agente-tuneis','agente-mineracao','agente-oleo-gas','agente-edificacoes');
--
-- DELETE FROM maestro_routing_keywords WHERE agent_slug IN
--   ('agente-tuneis','agente-mineracao','agente-oleo-gas','agente-edificacoes');
--
-- DELETE FROM sp_agent_routing WHERE agent_slug IN
--   ('agente-tuneis','agente-mineracao','agente-oleo-gas','agente-edificacoes');
--
-- DELETE FROM rag_collections WHERE slug IN
--   ('tuneis','mineracao','oleo-gas','edificacoes');
--
-- COMMIT;
