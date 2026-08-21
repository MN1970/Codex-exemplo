-- =====================================================================
-- Portal Manta (Portal IA) — schema candidato do backend
-- Artefato: MNT-2026-ARQ-0001 (anexo A)  ·  v1.0  ·  2026-08-20
--
-- ESTE ARQUIVO NÃO É UMA MIGRAÇÃO DE PRODUÇÃO.
-- É o desenho de referência que acompanha docs/PORTAL-BACKEND-PLANO.md.
-- Antes de virar migração:
--   1) confirmar convivência com o schema atual do RAG
--      (ke_embeddings, manta_rag_chunks, knowledge_extractions);
--   2) gate humano MN;
--   3) quebrar em migrações versionadas por fase (F0..F5).
--
-- Projeto alvo: manta-maestro-v5 (ogxxgvgtulrbbppshjie, sa-east-1)
-- =====================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector (já presente)
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- busca textual/fuzzy

CREATE SCHEMA IF NOT EXISTS portal_core;
CREATE SCHEMA IF NOT EXISTS portal_docs;
CREATE SCHEMA IF NOT EXISTS portal_ai;
CREATE SCHEMA IF NOT EXISTS portal_ops;

-- ---------------------------------------------------------------------
-- Tipos
-- ---------------------------------------------------------------------
CREATE TYPE portal_core.member_role AS ENUM
  ('owner','admin','manager','analyst','viewer','agent');

CREATE TYPE portal_core.project_phase AS ENUM
  ('estudo_previo','projeto_basico','projeto_executivo','obra',
   'operacao_manutencao','licitacao','due_diligence','encerramento');

CREATE TYPE portal_core.link_type AS ENUM ('FS','SS','FF','SF');

CREATE TYPE portal_ops.job_status AS ENUM
  ('queued','running','succeeded','failed','dead');

CREATE TYPE portal_ai.run_status AS ENUM
  ('queued','running','succeeded','failed','flagged','cancelled');

-- =====================================================================
-- portal_core — tenancy, pessoas, projetos
-- =====================================================================

CREATE TABLE portal_core.tenants (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug           text UNIQUE NOT NULL,
  display_name   text NOT NULL,
  is_internal    boolean NOT NULL DEFAULT false,  -- true apenas p/ tenant zero
  token_budget   bigint,                          -- teto mensal; NULL = sem teto
  status         text NOT NULL DEFAULT 'active',
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.profiles (
  user_id      uuid PRIMARY KEY,                  -- = auth.users.id
  full_name    text,
  job_title    text,
  avatar_url   text,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.memberships (
  tenant_id  uuid NOT NULL REFERENCES portal_core.tenants(id) ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES portal_core.profiles(user_id) ON DELETE CASCADE,
  role       portal_core.member_role NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, user_id)
);

-- Catálogo de segmentos (S1..S13) e atividades (A1..A10).
-- Tabela, não constante em código: a reconciliação da taxonomia
-- (risco R-01 do plano) muda dado, não deploy.
CREATE TABLE portal_core.taxonomy (
  code        text PRIMARY KEY,          -- 'S1', 'A1', 'F-portal-ia'
                                         -- numeração legada do CLAUDE.md deste repo
  kind        text NOT NULL,             -- 'segmento' | 'atividade' | 'funcional'
  name        text NOT NULL,
  legacy_code text,                      -- '03-S1', '02-C' ...
  rag_prefix  text,                      -- 'rod:', 'san:' ...
  active      boolean NOT NULL DEFAULT true
);

CREATE TABLE portal_core.projects (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL REFERENCES portal_core.tenants(id) ON DELETE CASCADE,
  code           text NOT NULL,                 -- código interno do projeto
  name           text NOT NULL,
  segment_code   text REFERENCES portal_core.taxonomy(code),
  phase          portal_core.project_phase,
  location       text,
  starts_on      date,
  ends_on        date,
  status         text NOT NULL DEFAULT 'active',
  metadata       jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_by     uuid,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),
  deleted_at     timestamptz,
  UNIQUE (tenant_id, code)
);

CREATE TABLE portal_core.project_members (
  project_id uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES portal_core.profiles(user_id) ON DELETE CASCADE,
  tenant_id  uuid NOT NULL,
  role       portal_core.member_role NOT NULL,
  PRIMARY KEY (project_id, user_id)
);

-- ---------------------------------------------------------------------
-- Contratos (módulo 2)
-- ---------------------------------------------------------------------
CREATE TABLE portal_core.contracts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL,
  project_id      uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  number          text NOT NULL,
  object          text,
  signed_on       date,
  original_amount numeric(18,2),
  currency        char(3) NOT NULL DEFAULT 'BRL',
  reference_date  date,                       -- R5: valor @data
  source_ref      text,                       -- R5: fonte do valor
  term_days       integer,
  created_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, number)
);

CREATE TABLE portal_core.contract_amendments (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  contract_id    uuid NOT NULL REFERENCES portal_core.contracts(id) ON DELETE CASCADE,
  number         text NOT NULL,
  kind           text,                        -- prazo | valor | escopo | misto
  signed_on      date,
  delta_amount   numeric(18,2),
  delta_days     integer,
  currency       char(3) DEFAULT 'BRL',
  reference_date date,
  summary        text,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.contract_clauses (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  contract_id uuid NOT NULL REFERENCES portal_core.contracts(id) ON DELETE CASCADE,
  number      text,
  title       text,
  body        text NOT NULL,
  tags        text[] NOT NULL DEFAULT '{}',
  search_tsv  tsvector GENERATED ALWAYS AS (to_tsvector('portuguese'::regconfig, coalesce(body,''))) STORED
);
CREATE INDEX ON portal_core.contract_clauses USING gin (search_tsv);

-- ---------------------------------------------------------------------
-- Cronograma (módulo 3)
-- ---------------------------------------------------------------------
CREATE TABLE portal_core.schedules (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  name       text NOT NULL,
  source     text NOT NULL,                  -- xer | mspdi | manual
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.schedule_versions (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  schedule_id  uuid NOT NULL REFERENCES portal_core.schedules(id) ON DELETE CASCADE,
  label        text NOT NULL,                -- 'Baseline 0', 'Rev 12'
  is_baseline  boolean NOT NULL DEFAULT false,
  data_date    date,
  imported_from uuid,                        -- document_versions.id do XER/MPP
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.activities (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL,
  version_id    uuid NOT NULL REFERENCES portal_core.schedule_versions(id) ON DELETE CASCADE,
  external_id   text NOT NULL,               -- Activity ID do P6/MSP
  wbs_path      text,
  name          text NOT NULL,
  early_start   date, early_finish  date,
  late_start    date, late_finish   date,
  actual_start  date, actual_finish date,
  duration_days numeric(10,2),
  total_float   numeric(10,2),
  pct_complete  numeric(5,2),
  is_critical   boolean NOT NULL DEFAULT false,
  UNIQUE (version_id, external_id)
);
CREATE INDEX ON portal_core.activities (version_id, is_critical);

CREATE TABLE portal_core.activity_links (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL,
  version_id    uuid NOT NULL REFERENCES portal_core.schedule_versions(id) ON DELETE CASCADE,
  predecessor_id uuid NOT NULL REFERENCES portal_core.activities(id) ON DELETE CASCADE,
  successor_id   uuid NOT NULL REFERENCES portal_core.activities(id) ON DELETE CASCADE,
  link_type      portal_core.link_type NOT NULL,
  lag_days       numeric(10,2) NOT NULL DEFAULT 0
);

CREATE TABLE portal_core.progress_snapshots (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  version_id   uuid NOT NULL REFERENCES portal_core.schedule_versions(id) ON DELETE CASCADE,
  period_end   date NOT NULL,
  planned_pct  numeric(5,2),
  actual_pct   numeric(5,2),
  UNIQUE (version_id, period_end)
);

-- ---------------------------------------------------------------------
-- Custos (módulo 5)
-- ---------------------------------------------------------------------
CREATE TABLE portal_core.budgets (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  name       text NOT NULL,
  base_table text,                            -- SICRO | SINAPI | próprio
  bdi_pct    numeric(6,3),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.budget_versions (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  budget_id  uuid NOT NULL REFERENCES portal_core.budgets(id) ON DELETE CASCADE,
  label      text NOT NULL,
  reference_date date NOT NULL,               -- R5: data-base da tabela
  source_ref text,                            -- R5: ex. 'SICRO SP 04/2026'
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.cost_items (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  version_id     uuid NOT NULL REFERENCES portal_core.budget_versions(id) ON DELETE CASCADE,
  wbs_path       text,
  ref_code       text,                        -- código SICRO/SINAPI
  description    text NOT NULL,
  unit           text NOT NULL,
  quantity       numeric(18,4) NOT NULL,
  unit_price     numeric(18,2) NOT NULL,
  currency       char(3) NOT NULL DEFAULT 'BRL',
  reference_date date NOT NULL,
  source_ref     text,
  missing_reason text,                        -- R2: por que um dado está nulo
  total_price    numeric(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);
CREATE INDEX ON portal_core.cost_items (version_id, ref_code);

CREATE TABLE portal_core.measurements (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  project_id   uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  number       integer NOT NULL,
  period_start date NOT NULL,
  period_end   date NOT NULL,
  status       text NOT NULL DEFAULT 'draft', -- draft|submitted|approved
  approved_by  uuid,                          -- gate humano
  approved_at  timestamptz,
  UNIQUE (project_id, number)
);

CREATE TABLE portal_core.measurement_lines (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  measurement_id uuid NOT NULL REFERENCES portal_core.measurements(id) ON DELETE CASCADE,
  cost_item_id   uuid REFERENCES portal_core.cost_items(id),
  quantity       numeric(18,4) NOT NULL,
  amount         numeric(18,2) NOT NULL,
  currency       char(3) NOT NULL DEFAULT 'BRL',
  reference_date date NOT NULL
);

CREATE TABLE portal_core.cashflow_entries (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  project_id     uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  period_end     date NOT NULL,
  planned_amount numeric(18,2),
  actual_amount  numeric(18,2),
  currency       char(3) NOT NULL DEFAULT 'BRL',
  reference_date date NOT NULL,
  UNIQUE (project_id, period_end)
);

-- ---------------------------------------------------------------------
-- Claims (módulo 4)
-- ---------------------------------------------------------------------
CREATE TABLE portal_core.claims (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  project_id     uuid NOT NULL REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  manta_id       text,                        -- R4: MNT-YYYY-CLM-NNNN
  number         text,
  title          text NOT NULL,
  status         text NOT NULL DEFAULT 'draft',
  claimed_amount numeric(18,2),
  currency       char(3) NOT NULL DEFAULT 'BRL',
  reference_date date,
  source_ref     text,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_core.claim_windows (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  claim_id   uuid NOT NULL REFERENCES portal_core.claims(id) ON DELETE CASCADE,
  code       text NOT NULL,                   -- 'GR-04', '2026-T1'
  starts_on  date NOT NULL,
  ends_on    date NOT NULL,
  narrative  text,
  UNIQUE (claim_id, code)
);

CREATE TABLE portal_core.claim_events (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL,
  claim_id      uuid NOT NULL REFERENCES portal_core.claims(id) ON DELETE CASCADE,
  window_id     uuid REFERENCES portal_core.claim_windows(id) ON DELETE SET NULL,
  occurred_on   date NOT NULL,
  category      text,                         -- NC, interferência, projeto, clima
  description   text NOT NULL,
  responsibility text,                        -- contratante | contratada | terceiro
  evidence_ref  uuid                          -- document_versions.id
);

CREATE TABLE portal_core.claim_impacts (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  event_id    uuid NOT NULL REFERENCES portal_core.claim_events(id) ON DELETE CASCADE,
  activity_id uuid REFERENCES portal_core.activities(id) ON DELETE SET NULL,
  delay_days  numeric(10,2),
  cost_amount numeric(18,2),
  currency    char(3) DEFAULT 'BRL',
  reference_date date,
  method      text                            -- AACE MIP 3.x, SCL, etc.
);

CREATE TABLE portal_core.quantum_lines (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  claim_id       uuid NOT NULL REFERENCES portal_core.claims(id) ON DELETE CASCADE,
  window_id      uuid REFERENCES portal_core.claim_windows(id) ON DELETE SET NULL,
  description    text NOT NULL,
  basis          text,                        -- memória de cálculo resumida
  amount         numeric(18,2) NOT NULL,
  currency       char(3) NOT NULL DEFAULT 'BRL',
  reference_date date NOT NULL,
  source_ref     text NOT NULL,               -- R5: fonte obrigatória
  missing_reason text
);

-- =====================================================================
-- portal_docs — documentos (módulo 7)
-- =====================================================================
CREATE TABLE portal_docs.documents (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  project_id   uuid REFERENCES portal_core.projects(id) ON DELETE CASCADE,
  manta_id     text,                          -- R4
  title        text NOT NULL,
  doc_type     text,                          -- contrato|projeto|laudo|edital...
  discipline   text,
  sp_item_id   text,                          -- id do item no SharePoint
  sp_path      text,
  status       text NOT NULL DEFAULT 'active',-- active|parse_failed|archived
  status_reason text,                         -- R2
  created_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, sp_item_id)
);

CREATE TABLE portal_docs.document_versions (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  document_id  uuid NOT NULL REFERENCES portal_docs.documents(id) ON DELETE CASCADE,
  version      integer NOT NULL,
  storage_key  text NOT NULL,                 -- bucket/tenant/…
  mime_type    text,
  size_bytes   bigint,
  sha256       text NOT NULL,
  indexed_at   timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, version)
);
-- Deduplicação por conteúdo: consulta por (tenant_id, sha256) antes de
-- gravar. Não é UNIQUE de propósito — o mesmo arquivo pode ser anexado
-- legitimamente a dois projetos do mesmo tenant.
CREATE INDEX ON portal_docs.document_versions (tenant_id, sha256);

CREATE TABLE portal_docs.document_links (
  document_id uuid NOT NULL REFERENCES portal_docs.documents(id) ON DELETE CASCADE,
  tenant_id   uuid NOT NULL,
  target_kind text NOT NULL,                  -- claim|activity|clause|measurement
  target_id   uuid NOT NULL,
  PRIMARY KEY (document_id, target_kind, target_id)
);

CREATE TABLE portal_docs.sp_sync_state (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  sp_folder   text NOT NULL,                  -- 03_Projetos/Saneamento/*
  delta_token text,
  last_run_at timestamptz,
  last_error  text,
  UNIQUE (tenant_id, sp_folder)
);

CREATE TABLE portal_docs.extraction_results (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  version_id  uuid NOT NULL REFERENCES portal_docs.document_versions(id) ON DELETE CASCADE,
  extractor   text NOT NULL,                  -- evtea-extractor, cad-reader...
  schema_name text NOT NULL,
  payload     jsonb NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- =====================================================================
-- portal_ai — execuções de agente (módulo 6)
-- =====================================================================
CREATE TABLE portal_ai.agent_config (
  agent_code  text PRIMARY KEY REFERENCES portal_core.taxonomy(code),
  model       text NOT NULL,                  -- claude-sonnet-5 etc.
  max_tokens  integer NOT NULL DEFAULT 8192,
  rag_collections text[] NOT NULL DEFAULT '{}',
  enabled     boolean NOT NULL DEFAULT true
);

CREATE TABLE portal_ai.agent_runs (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  project_id   uuid REFERENCES portal_core.projects(id) ON DELETE SET NULL,
  user_id      uuid,
  agent_code   text REFERENCES portal_core.taxonomy(code),
  routed_by    text,                          -- 'router' | 'user'
  route_score  numeric(6,2),
  status       portal_ai.run_status NOT NULL DEFAULT 'queued',
  error        text,
  started_at   timestamptz,
  finished_at  timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON portal_ai.agent_runs (tenant_id, created_at DESC);

CREATE TABLE portal_ai.agent_messages (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  run_id     uuid NOT NULL REFERENCES portal_ai.agent_runs(id) ON DELETE CASCADE,
  seq        integer NOT NULL,
  role       text NOT NULL,                   -- user|assistant|tool
  content    text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (run_id, seq)
);

CREATE TABLE portal_ai.agent_tool_calls (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  run_id      uuid NOT NULL REFERENCES portal_ai.agent_runs(id) ON DELETE CASCADE,
  tool_name   text NOT NULL,
  arguments   jsonb,
  result_summary text,
  duration_ms integer,
  succeeded   boolean
);

CREATE TABLE portal_ai.rag_queries (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL,
  run_id      uuid REFERENCES portal_ai.agent_runs(id) ON DELETE CASCADE,
  query_text  text NOT NULL,
  collection  text,
  top_k       integer NOT NULL DEFAULT 5,
  threshold   numeric(4,3) NOT NULL DEFAULT 0.700,
  hits        jsonb,                          -- [{chunk_id, score}]
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_ai.citations (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  run_id       uuid NOT NULL REFERENCES portal_ai.agent_runs(id) ON DELETE CASCADE,
  version_id   uuid REFERENCES portal_docs.document_versions(id) ON DELETE SET NULL,
  locator      text,                          -- página, seção, célula
  quoted_text  text
);

CREATE TABLE portal_ai.guardrail_findings (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  run_id     uuid NOT NULL REFERENCES portal_ai.agent_runs(id) ON DELETE CASCADE,
  guard      text NOT NULL,                   -- aluci-guard | consist-guard | R1
  severity   text NOT NULL,                   -- info | warn | block
  reference  text,                            -- norma/lei/URL/SICRO suspeito
  detail     text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_ai.token_usage (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL,
  run_id         uuid REFERENCES portal_ai.agent_runs(id) ON DELETE SET NULL,
  model          text NOT NULL,
  input_tokens   integer NOT NULL DEFAULT 0,
  output_tokens  integer NOT NULL DEFAULT 0,
  cache_read_tokens  integer NOT NULL DEFAULT 0,
  cache_write_tokens integer NOT NULL DEFAULT 0,
  cost_amount    numeric(18,6),               -- NULL enquanto não medido (R2)
  currency       char(3) DEFAULT 'USD',
  occurred_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON portal_ai.token_usage (tenant_id, occurred_at DESC);

-- =====================================================================
-- portal_ops — jobs, auditoria, notificações
-- =====================================================================
CREATE TABLE portal_ops.jobs (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    uuid NOT NULL,
  kind         text NOT NULL,                 -- document.ingest, schedule.import…
  payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
  status       portal_ops.job_status NOT NULL DEFAULT 'queued',
  attempts     integer NOT NULL DEFAULT 0,
  max_attempts integer NOT NULL DEFAULT 3,
  last_error   text,
  scheduled_at timestamptz NOT NULL DEFAULT now(),
  started_at   timestamptz,
  finished_at  timestamptz,
  created_by   uuid
);
CREATE INDEX ON portal_ops.jobs (status, scheduled_at);

CREATE TABLE portal_ops.job_events (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  job_id     uuid NOT NULL REFERENCES portal_ops.jobs(id) ON DELETE CASCADE,
  at         timestamptz NOT NULL DEFAULT now(),
  level      text NOT NULL DEFAULT 'info',
  message    text NOT NULL,
  progress   numeric(5,2)
);

CREATE TABLE portal_ops.audit_log (
  id          bigserial PRIMARY KEY,
  tenant_id   uuid NOT NULL,
  actor_id    uuid,
  action      text NOT NULL,                  -- create|update|delete|export|approve
  resource    text NOT NULL,                  -- 'portal_core.claims'
  resource_id uuid,
  diff        jsonb,
  request_id  text,
  at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON portal_ops.audit_log (tenant_id, at DESC);

CREATE TABLE portal_ops.notifications (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  uuid NOT NULL,
  user_id    uuid,
  kind       text NOT NULL,
  title      text NOT NULL,
  body       text,
  link       text,
  read_at    timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE portal_ops.feature_flags (
  tenant_id uuid NOT NULL,
  flag      text NOT NULL,
  enabled   boolean NOT NULL DEFAULT false,
  PRIMARY KEY (tenant_id, flag)
);

-- =====================================================================
-- RLS — padrão aplicado a todas as tabelas com tenant_id
-- =====================================================================
-- Exemplo canônico; no repositório de migrações isto vira um DO-block
-- que itera sobre as tabelas dos schemas portal_*.

ALTER TABLE portal_core.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_select ON portal_core.projects
  FOR SELECT USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

CREATE POLICY tenant_isolation_write ON portal_core.projects
  FOR ALL USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid)
          WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Camada 2 — escopo por projeto (para tabelas com project_id):
-- USING (project_id IN (SELECT project_id FROM portal_core.project_members
--                       WHERE user_id = auth.uid()))

-- =====================================================================
-- PENDÊNCIA BLOQUEANTE (risco R-02 do plano)
-- =====================================================================
-- As tabelas de RAG em produção não têm tenant_id. Antes de qualquer
-- tenant externo, aplicar:
--
--   ALTER TABLE public.manta_rag_chunks ADD COLUMN tenant_id uuid;
--   ALTER TABLE public.ke_embeddings    ADD COLUMN tenant_id uuid;
--   -- backfill: conteúdo interno → tenant zero; normas públicas → NULL
--   CREATE INDEX ON public.manta_rag_chunks (tenant_id);
--   -- e o filtro precisa entrar DENTRO da RPC de busca, não no app.
--
-- Sem isso, RAG cross-tenant é vazamento de dados de cliente.

COMMIT;

-- =====================================================================
-- DOWN (manual)
-- =====================================================================
-- BEGIN;
--   DROP SCHEMA portal_ops  CASCADE;
--   DROP SCHEMA portal_ai   CASCADE;
--   DROP SCHEMA portal_docs CASCADE;
--   DROP SCHEMA portal_core CASCADE;
-- COMMIT;
