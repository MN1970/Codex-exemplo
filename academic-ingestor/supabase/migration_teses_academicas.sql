-- WF-AKP-001 — M13 migration (schema alinhado com HANDOFF + pgvector 768d)
--
-- Aplicada em produção (Supabase manta-maestro, ogxxgvgtulrbbppshjie) em 2026-07-05
-- via MCP apply_migration:
--   * wf_akp_001_academic_ingestor            (tabelas + índices + RLS)
--   * wf_akp_001_align_with_handoff_schema    (colunas grader_score/aluci_status/conhecimentos)
--
-- Este arquivo é a versão consolidada e re-aplicável dessas duas migrations.
-- Idempotente: usa create table if not exists, add column if not exists, drop policy if exists.

-- ── Extensões ────────────────────────────────────────────────
-- `vector` já vem instalado no projeto manta-maestro (v0.8.0, schema public).
-- create extension if not exists vector;

-- ── teses_academicas: fonte catalogada ───────────────────────
create table if not exists public.teses_academicas (
  id              uuid primary key default extensions.uuid_generate_v4(),
  codigo          text unique not null,
  titulo          text not null,
  autor           text,
  orientador      text,
  instituicao     text,
  programa        text,
  grau            text,
  ano             int,
  bloco_busca     text,
  url_original    text,
  url_pdf         text,
  doi             text,
  idioma          text default 'pt-BR',
  palavras_chave  text[] default '{}'::text[],
  agentes_destino text[] default '{}'::text[],
  hash_sha256     text,
  status          text default 'catalogado',
  metadata        jsonb default '{}'::jsonb,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

alter table public.teses_academicas
  add column if not exists grader_score  numeric,
  add column if not exists aluci_status  text,
  add column if not exists conhecimentos jsonb default '[]'::jsonb;

comment on table  public.teses_academicas is 'WF-AKP-001 fonte: teses/artigos catalogados por bloco B1-B8. status: catalogado|graded|approved|rejected|ingested.';
comment on column public.teses_academicas.agentes_destino is 'Slugs dos agentes Manta que consomem esta fonte (ex: 03-S1, 07).';
comment on column public.teses_academicas.conhecimentos   is 'Cópia denormalizada dos KEs em jsonb (HANDOFF format). knowledge_extractions é a versão normalizada com embeddings.';

-- ── knowledge_extractions: KEs normalizadas (uma linha por KE) ─
create table if not exists public.knowledge_extractions (
  id                uuid primary key default extensions.uuid_generate_v4(),
  ke_codigo         text unique not null,
  tese_codigo       text not null references public.teses_academicas(codigo) on delete cascade,
  tipo              text,
  descricao         text not null,
  agentes_destino   text[] default '{}'::text[],
  grader_score      numeric,
  grader_breakdown  jsonb,
  aluci_status      text,
  aluci_flags       jsonb,
  approved_by       text,
  approved_at       timestamptz,
  metadata          jsonb default '{}'::jsonb,
  created_at        timestamptz default now(),
  updated_at        timestamptz default now()
);

comment on table  public.knowledge_extractions is 'WF-AKP-001 KEs (Knowledge Extractions). Um KE por peça de conhecimento reutilizável. aluci_status: pass|warn|fail.';
comment on column public.knowledge_extractions.tipo is 'metodo|parametro|formula|benchmark|case_study|referencia_catalogada|norma';

-- ── ke_embeddings: pgvector 768d (mpnet paraphrase-multilingual) ─
create table if not exists public.ke_embeddings (
  id           uuid primary key default extensions.uuid_generate_v4(),
  ke_codigo    text not null references public.knowledge_extractions(ke_codigo) on delete cascade,
  embedding    vector(768),
  model        text default 'paraphrase-multilingual-mpnet-base-v2',
  chunk_text   text,
  created_at   timestamptz default now()
);

comment on table public.ke_embeddings is 'WF-AKP-001 pgvector store — 768d HNSW, alinhado com manta_rag_chunks.';

-- ── Índices ──────────────────────────────────────────────────
create index if not exists idx_teses_agentes     on public.teses_academicas      using gin(agentes_destino);
create index if not exists idx_teses_bloco       on public.teses_academicas      (bloco_busca);
create index if not exists idx_teses_status      on public.teses_academicas      (status);
create index if not exists idx_teses_grader      on public.teses_academicas      (grader_score);
create index if not exists idx_teses_aluci       on public.teses_academicas      (aluci_status);
create index if not exists idx_teses_conhec_gin  on public.teses_academicas      using gin(conhecimentos);
create index if not exists idx_ke_agentes        on public.knowledge_extractions using gin(agentes_destino);
create index if not exists idx_ke_tese           on public.knowledge_extractions (tese_codigo);
create index if not exists idx_ke_aluci          on public.knowledge_extractions (aluci_status);
create index if not exists idx_ke_score          on public.knowledge_extractions (grader_score);
create index if not exists idx_ke_emb_hnsw       on public.ke_embeddings         using hnsw (embedding vector_cosine_ops);

-- ── Trigger updated_at ───────────────────────────────────────
create or replace function public.wf_akp_touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists trg_teses_academicas_updated on public.teses_academicas;
create trigger trg_teses_academicas_updated
before update on public.teses_academicas
for each row execute function public.wf_akp_touch_updated_at();

drop trigger if exists trg_ke_updated on public.knowledge_extractions;
create trigger trg_ke_updated
before update on public.knowledge_extractions
for each row execute function public.wf_akp_touch_updated_at();

-- ── RLS ──────────────────────────────────────────────────────
alter table public.teses_academicas       enable row level security;
alter table public.knowledge_extractions   enable row level security;
alter table public.ke_embeddings           enable row level security;

drop policy if exists teses_service_all on public.teses_academicas;
create policy teses_service_all      on public.teses_academicas      for all    to service_role using (true) with check (true);
drop policy if exists teses_auth_read  on public.teses_academicas;
create policy teses_auth_read        on public.teses_academicas      for select to authenticated using (true);

drop policy if exists ke_service_all   on public.knowledge_extractions;
create policy ke_service_all         on public.knowledge_extractions for all    to service_role using (true) with check (true);
drop policy if exists ke_auth_read    on public.knowledge_extractions;
create policy ke_auth_read           on public.knowledge_extractions for select to authenticated using (true);

drop policy if exists emb_service_all on public.ke_embeddings;
create policy emb_service_all        on public.ke_embeddings         for all    to service_role using (true) with check (true);
drop policy if exists emb_auth_read   on public.ke_embeddings;
create policy emb_auth_read          on public.ke_embeddings         for select to authenticated using (true);
