-- Manta Maestro v4.3 — agente-leitor-documental (Manta 08)
-- Ticket: MNT-2026-LEITOR-DOCUMENTAL
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA. Não aplica em produção sem
-- aprovação MN. Ajustar `assumes existing schema` conforme o schema
-- real do Supabase; nem toda coluna abaixo é obrigatória.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_14_v4_3_leitor_documental.sql
--
-- ROLLBACK: as inserções/criações são idempotentes (`IF NOT EXISTS` /
-- `ON CONFLICT DO NOTHING`); para desfazer, ver bloco DOWN no fim
-- deste arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Índice de controle de processamento (idempotência do leitor)
-- ---------------------------------------------------------------------
-- Novo — este agente não existia antes da v4.3. Guarda o hash de cada
-- arquivo já processado para não reprocessar o mesmo documento, e o
-- agente_dono resolvido (para auditoria de roteamento).

CREATE TABLE IF NOT EXISTS doc_processing_index (
  hash            TEXT PRIMARY KEY,
  nome_original   TEXT NOT NULL,
  formato_origem  TEXT NOT NULL,
  doc_type        TEXT,
  agente_dono     TEXT,
  fase_ciclo_vida TEXT,
  sp_folder       TEXT,
  status          TEXT NOT NULL DEFAULT 'processado'
                  CHECK (status IN ('processado', 'pendente_skill', 'erro')),
  processado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doc_processing_index_agente_dono
  ON doc_processing_index (agente_dono);

CREATE INDEX IF NOT EXISTS idx_doc_processing_index_status
  ON doc_processing_index (status);

-- ---------------------------------------------------------------------
-- 2. Tabela de despacho por formato (extensão → skill)
-- ---------------------------------------------------------------------
-- Espelha a tabela da seção 3 do SKILL.md. Mantida em banco (em vez de
-- só no Markdown) para permitir que o roteador do agente consulte sem
-- reparsing do SKILL.md a cada chamada.

CREATE TABLE IF NOT EXISTS doc_format_dispatch (
  extensao   TEXT NOT NULL,
  subtipo    TEXT NOT NULL DEFAULT 'generico',
  skill_alvo TEXT NOT NULL,
  prioridade INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (extensao, subtipo)
);

INSERT INTO doc_format_dispatch (extensao, subtipo, skill_alvo, prioridade) VALUES
  ('pdf',  'generico',           'pdf',                        10),
  ('pdf',  'edital',             'ler-edital',                 90),
  ('pdf',  'edital_aneel',       'ler-edital-aneel',           95),
  ('pdf',  'evtea_rodoviario',   'evtea-extractor',            90),
  ('pdf',  'planta_diagrama',    'leitura-diagrama-engenharia', 90),
  ('xlsx', 'generico',           'xlsx',                       10),
  ('xls',  'generico',           'xlsx',                       10),
  ('docx', 'generico',           'docx',                       10),
  ('dotx', 'generico',           'docx',                       10),
  ('pptx', 'generico',           'pptx',                       10),
  ('dwg',  'generico',           'autodesk-toolkit',           10),
  ('dxf',  'generico',           'autodesk-toolkit',           10),
  ('ifc',  'generico',           'autodesk-toolkit',           10),
  ('rvt',  'generico',           'autodesk-toolkit',           10),
  ('nwd',  'generico',           'autodesk-toolkit',           10),
  ('nwc',  'generico',           'autodesk-toolkit',           10),
  ('xer',  'generico',           'cronograma-toolkit',         10),
  ('mpp',  'generico',           'cronograma-toolkit',         10)
ON CONFLICT (extensao, subtipo) DO NOTHING;

-- ---------------------------------------------------------------------
-- 3. Registro do agente na tabela de routing SharePoint (opcional)
-- ---------------------------------------------------------------------
-- Assumes existing table `sp_agent_routing(agent_slug TEXT PRIMARY KEY,
--   sp_folder TEXT NOT NULL, file_patterns TEXT[] NOT NULL,
--   priority INTEGER DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW())`
-- (mesma usada pela migração v4.2).
--
-- O leitor-documental não é dono de uma pasta de segmento — ele
-- observa TODAS as pastas de projeto já mapeadas para os verticais
-- (S1-S10) e roda antes deles. Por isso não recebe uma linha própria
-- de `sp_folder`; a linha abaixo é só um marcador de prioridade mais
-- alta para garantir que ele rode primeiro no pipeline, caso o
-- Maestro use `priority` para decidir ordem de execução.

INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority)
VALUES
  ('agente-leitor-documental', '03_Projetos/*', ARRAY['*.pdf','*.xlsx','*.xls','*.docx','*.dotx','*.pptx','*.dwg','*.dxf','*.ifc','*.rvt','*.xer','*.mpp'], 200)
ON CONFLICT (agent_slug) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM sp_agent_routing WHERE agent_slug = 'agente-leitor-documental';
-- DROP TABLE IF EXISTS doc_format_dispatch;
-- DROP TABLE IF EXISTS doc_processing_index;
--
-- COMMIT;
