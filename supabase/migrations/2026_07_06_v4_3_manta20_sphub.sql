-- Manta Maestro v4.3 — Manta 20 (SP Hub v2.0)
-- Ticket: MANTA-SPHUB-20260706-001
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN. Cria as duas tabelas de suporte à alimentação proativa
-- do SP Hub (Parte B5 da spec) e semeia 24 routing rules iniciais
-- (Parte B3).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_06_v4_3_manta20_sphub.sql
--
-- ROLLBACK: bloco DOWN no fim do arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. sp_agent_feed — fila de docs por agente (notificação proativa)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sp_agent_feed (
  id            UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_code    TEXT        NOT NULL,               -- 'M1', 'M2', ...
  doc_id        TEXT        NOT NULL,               -- SP item ID
  doc_path      TEXT        NOT NULL,               -- caminho completo SP
  doc_name      TEXT        NOT NULL,
  doc_type      TEXT,                               -- contrato/projeto/medicao/...
  file_ext      TEXT,                               -- pdf/dwg/xer/...
  priority      TEXT        DEFAULT 'media',        -- alta/media/baixa
  status        TEXT        DEFAULT 'pending',      -- pending/delivered/ingested
  detected_at   TIMESTAMPTZ DEFAULT NOW(),
  delivered_at  TIMESTAMPTZ,
  metadata      JSONB       DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_agent_feed_agent
  ON sp_agent_feed (agent_code, status);

CREATE INDEX IF NOT EXISTS idx_agent_feed_priority
  ON sp_agent_feed (priority, status);

-- Evita dedup na re-detecção do mesmo doc para o mesmo agente enquanto
-- ainda estiver pending (histórico de delivered/ingested permanece).
CREATE UNIQUE INDEX IF NOT EXISTS uniq_agent_feed_pending
  ON sp_agent_feed (agent_code, doc_id)
  WHERE status = 'pending';

-- ---------------------------------------------------------------------
-- 2. sp_routing_rules — regras configuráveis
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sp_routing_rules (
  id                SERIAL      PRIMARY KEY,
  rule_name         TEXT        NOT NULL UNIQUE,
  path_pattern      TEXT,                            -- regex/glob no path SP
  file_ext_pattern  TEXT,                            -- '.xer,.mpp' ou '*'
  name_pattern      TEXT,                            -- regex no nome
  target_agents     TEXT[]      NOT NULL,            -- ARRAY['M1','M2']
  doc_type          TEXT        NOT NULL,            -- tipo resultante
  priority          TEXT        DEFAULT 'media',     -- alta/media/baixa
  active            BOOLEAN     DEFAULT TRUE,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routing_rules_active
  ON sp_routing_rules (active, priority);

-- ---------------------------------------------------------------------
-- 3. Seed — 24 routing rules iniciais (PARTE B3 da spec)
-- ---------------------------------------------------------------------
--
-- Ordem de avaliação sugerida pelo Manta 20 no delta_sync:
--   1) regras por extensão (mais específicas)
--   2) regras por nome (SICRO, RDO, BM, ...)
--   3) regras por pasta (mais gerais)
-- Todas as regras `active=TRUE` que casam disparam — routing é 1-N.

INSERT INTO sp_routing_rules
  (rule_name, path_pattern, file_ext_pattern, name_pattern, target_agents, doc_type, priority)
VALUES
  -- Pastas 02_CLIENTE/*
  ('cliente_contrato',        '02_CLIENTE/*/01_CONTRATO/*',        '*', NULL,
   ARRAY['M1','M2'], 'contrato',        'alta'),
  ('cliente_rec',             '02_CLIENTE/*/02_REC/*',             '*', NULL,
   ARRAY['M8'],       'edital',          'alta'),
  ('cliente_proposta',        '02_CLIENTE/*/03_PROPOSTA/*',        '*', NULL,
   ARRAY['M8','M7'],  'proposta',        'alta'),
  ('cliente_projeto',         '02_CLIENTE/*/04_PROJETO/*',         '*', NULL,
   ARRAY['M3','M4'],  'projeto',         'alta'),
  ('cliente_medicao',         '02_CLIENTE/*/05_MEDICAO/*',         '*', NULL,
   ARRAY['M7','M1'],  'medicao',         'media'),
  ('cliente_correspondencia', '02_CLIENTE/*/06_CORRESPONDENCIA/*', '*', NULL,
   ARRAY['M2'],       'correspondencia', 'media'),
  ('cliente_cronograma',      '02_CLIENTE/*/07_CRONOGRAMA/*',      '*', NULL,
   ARRAY['M1'],       'cronograma',      'alta'),

  -- Pastas 04_IA
  ('ia_maestro',              '04_IA/Manta-Maestro/*',             '*', NULL,
   ARRAY['M19'],      'skill',           'baixa'),
  ('ia_rag',                  '04_IA/RAG/*',                       '*', NULL,
   ARRAY['M18'],      'rag_chunk',       'baixa'),

  -- Biblioteca / normas
  ('biblioteca',              '03_BIBLIOTECA/*',                   '*', NULL,
   ARRAY['M16'],      'norma_paper',     'media'),

  -- Extensões — cross-folder
  ('ext_xer_mpp',             NULL, '.xer,.mpp',                        NULL,
   ARRAY['M1','M3'],  'cronograma_p6',   'alta'),
  ('ext_dwg_dxf',             NULL, '.dwg,.dxf',                        NULL,
   ARRAY['M3','M4'],  'projeto_cad',     'alta'),
  ('ext_ifc',                 NULL, '.ifc,.ifczip,.ifcxml',             NULL,
   ARRAY['M4','M6'],  'modelo_bim',      'alta'),
  ('ext_landxml',             NULL, '.xml,.landxml',                    NULL,
   ARRAY['M3'],       'landxml',         'media'),
  ('ext_pdf_generico',        NULL, '.pdf',                             NULL,
   ARRAY['M18'],      'pdf_generico',    'baixa'),

  -- Nome / conteúdo
  ('name_sicro',              NULL, '*', '.*SICRO.*',
   ARRAY['M7'],       'composicao_custo','alta'),
  ('name_rdo',                NULL, '*', '.*RDO.*',
   ARRAY['M1','M7'],  'diario_obra',     'media'),
  ('name_bm',                 NULL, '*', '.*(BM|Boletim.?Medi).*',
   ARRAY['M7','M1'],  'boletim_medicao', 'alta'),
  ('name_tac',                NULL, '*', '.*(TAC|Termo.?Aditivo).*',
   ARRAY['M1','M2'],  'aditivo_contrato','alta'),
  ('name_per',                NULL, '*', '.*(PER|Projeto.?Executivo.?Refer).*',
   ARRAY['M8','M3'],  'per',             'alta'),
  ('name_sondagem',           NULL, '*', '.*(sondagem|SPT|CPT).*',
   ARRAY['M4','M10'], 'sondagem',        'media'),
  ('name_batimetria',         NULL, '*', '.*batimetri.*',
   ARRAY['M3-S6'],    'batimetria',      'media'),
  ('name_barragem',           NULL, '*', '.*(barragem|dam|vertedouro).*',
   ARRAY['M3-S10'],   'barragem',        'media'),
  ('name_licitacao',          NULL, '*', '.*(edital|licitacao|preg[aã]o).*',
   ARRAY['M8'],       'edital',          'alta')
ON CONFLICT (rule_name) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP INDEX IF EXISTS uniq_agent_feed_pending;
-- DROP INDEX IF EXISTS idx_agent_feed_priority;
-- DROP INDEX IF EXISTS idx_agent_feed_agent;
-- DROP TABLE IF EXISTS sp_agent_feed;
--
-- DROP INDEX IF EXISTS idx_routing_rules_active;
-- DROP TABLE IF EXISTS sp_routing_rules;
--
-- COMMIT;
