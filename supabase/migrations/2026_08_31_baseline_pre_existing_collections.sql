-- Manta Maestro — baseline das 4 coleções RAG pré-existentes
-- (rodovias, oae, ferrovia, metro)
--
-- Estas 4 coleções antecedem a convenção de migração deste
-- repositório (introduzida em 2026_07_05_v4_2_agents_s6_s10.sql) — já
-- estavam operacionais em produção antes da v4.2, conforme a tabela
-- "RAG — Coleções em Supabase" do CLAUDE.md master (marcadas
-- "✅ Operacional (pré-existente)"). Este arquivo é a migração
-- retroativa/documental que faltava: registra o estado já aplicado em
-- produção, não uma mudança nova.
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA/DOCUMENTAL. Não aplica em
-- produção sem confirmação MN de que o INSERT é de fato idempotente
-- contra o schema real (`rag_collections`) — se as linhas já existirem
-- com um `slug` diferente do usado aqui, ajustar antes de rodar.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_31_baseline_pre_existing_collections.sql
--
-- ROLLBACK: inserções idempotentes via `ON CONFLICT DO NOTHING`; para
-- desfazer, ver bloco DOWN no fim deste arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- Registro das 4 coleções RAG pré-existentes
-- ---------------------------------------------------------------------
-- Assumes existing table `rag_collections(slug TEXT PRIMARY KEY,
--   name TEXT, storage_prefix TEXT, initial_sources JSONB, created_at
--   TIMESTAMPTZ DEFAULT NOW())` — mesmo schema assumido em
--   2026_07_05_v4_2_agents_s6_s10.sql.

INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('rodovias', 'Rodovias', 'rod:', jsonb_build_array(
     'DNIT normas e manuais',
     'SICRO (tabelas de custo referencial)',
     'NBR-DNIT'
   )),
  ('oae',      'OAE (pontes, viadutos)', 'oae:', jsonb_build_array(
     'NBR 7187 — Projeto de Pontes de Concreto Armado e Protendido',
     'NBR 6118 — Projeto de Estruturas de Concreto',
     'NBR 6122 — Projeto e Execução de Fundações',
     'PRL/RioSP (manuais de projeto de OAE)'
   )),
  ('ferrovia', 'Ferrovia', 'fer:', jsonb_build_array(
     'AREMA (American Railway Engineering Association)',
     'DNIT ferroviário',
     'Manuais de concessionárias ferroviárias'
   )),
  ('metro',    'Metrô', 'mtr:', jsonb_build_array(
     'ABNT NBR-NM',
     'ARTESP (normas de concessão metroferroviária)',
     'Manual STM (Sistema de Transporte Metroviário)'
   ))
ON CONFLICT (slug) DO NOTHING;

COMMIT;

-- ---------------------------------------------------------------------
-- DOWN (rollback manual, se necessário)
-- ---------------------------------------------------------------------
-- BEGIN;
-- DELETE FROM rag_collections WHERE slug IN ('rodovias', 'oae', 'ferrovia', 'metro');
-- COMMIT;
