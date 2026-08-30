-- Manta Maestro v5.3 — backfill de registro das 4 coleções RAG pré-existentes
-- (rodovias, oae, ferrovia, metro), anteriores à convenção de migração
-- candidata usada a partir de v4.2.
--
-- Contexto: CLAUDE.md ("RAG — Coleções em Supabase") sempre listou estas 4
-- coleções como "✅ Operacional (pré-existente)" — elas já existem em
-- produção desde antes deste repositório versionar migrações candidatas.
-- `tests/rag/test_rag_collections.py::test_no_orphan_collections_in_claude_md`
-- e `test_collection_present_in_a_migration_file` exigem que toda coleção
-- documentada no CLAUDE.md tenha uma migração correspondente — este arquivo
-- fecha essa lacuna para as 4 coleções legadas, sem alterar nada em produção
-- (idempotente via `ON CONFLICT DO NOTHING`, como as demais migrações
-- candidatas deste diretório).
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA / DE DOCUMENTAÇÃO. Não precisa ser
-- aplicada em produção (as coleções já existem lá) — serve para o
-- repositório ter, em código, o registro das 4 coleções que faltavam.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_23_v5_3_legacy_collections_backfill.sql
--
-- ROLLBACK: inserções idempotentes via `ON CONFLICT DO NOTHING`; para
-- desfazer, ver bloco DOWN no fim deste arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- Registro das 4 coleções RAG pré-existentes (rodovias, oae, ferrovia, metro)
-- ---------------------------------------------------------------------
-- Assumes existing table `rag_collections(slug TEXT PRIMARY KEY,
--   name TEXT, storage_prefix TEXT, initial_sources JSONB, created_at
--   TIMESTAMPTZ DEFAULT NOW())` — mesmo schema assumido em
--   2026_07_05_v4_2_agents_s6_s10.sql.

INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources)
VALUES
  ('rodovias', 'Rodovias', 'rod:', jsonb_build_array(
     'DNIT',
     'SICRO',
     'NBR-DNIT'
   )),
  ('oae', 'OAE (pontes, viadutos)', 'oae:', jsonb_build_array(
     'NBR 7187',
     'NBR 6118',
     'NBR 6122',
     'PRL/RioSP'
   )),
  ('ferrovia', 'Ferrovia', 'fer:', jsonb_build_array(
     'AREMA',
     'DNIT ferroviário',
     'Concessionárias'
   )),
  ('metro', 'Metrô', 'mtr:', jsonb_build_array(
     'ABNT NBR-NM',
     'ARTESP',
     'Manual STM'
   ))
ON CONFLICT (slug) DO NOTHING;

COMMIT;

-- ---------------------------------------------------------------------
-- DOWN (rollback manual, se necessário)
-- ---------------------------------------------------------------------
-- BEGIN;
-- DELETE FROM rag_collections WHERE slug IN ('rodovias', 'oae', 'ferrovia', 'metro');
-- COMMIT;
