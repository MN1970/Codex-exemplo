-- Manta Maestro — D1 (multi-tenancy): tenant_id + RLS
-- Ticket: ADR D1-D4 (docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md)
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA (mesma política das demais
-- migrações deste diretório: revisar contra o schema real antes de
-- aplicar em produção; gate humano MN — aprovado para implementação
-- em 2026-09-13, ver ADR seção "Correção de diagnóstico — 2026-09-13").
--
-- ATENÇÃO — 2 avisos importantes antes de aplicar isto em qualquer
-- banco real:
--
-- (a) `rag_chunks` tem HOJE 2 definições de CREATE TABLE conflitantes
--     neste repositório: `2026_07_27_barragens_rag_chunks.sql` (mais
--     antiga) e `2026_08_02_rag_hierarchy_v5.sql` (mais nova, schema
--     hierárquico com segment_codes/lifecycle_phases/embedding 384d).
--     Esta migração assume a definição de `2026_08_02_rag_hierarchy_v5.sql`
--     como canônica (é a mais recente e a que o ADR/CLAUDE.md tratam
--     como "v5"). Se essa premissa estiver errada — se
--     `2026_07_27_barragens_rag_chunks.sql` for na verdade a vigente —
--     avisar antes de aplicar; os dois arquivos nunca foram
--     reconciliados entre si.
--
-- (b) A produção real (fora deste repositório, auditada via MCP
--     Supabase) usa os nomes `manta_rag_chunks` / `manta_rag_documents`,
--     não `rag_chunks` — os nomes usados nas migrações deste repo podem
--     não bater com o schema real. Por isso, todo ALTER abaixo usa
--     `IF EXISTS` / `IF NOT EXISTS`: se o nome não bater, o ALTER vira
--     no-op em vez de falhar — mas também não tem efeito nenhum sobre a
--     tabela real até alguém reconciliar os nomes (ver
--     docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md).
--
-- O que esta migração faz:
--   1. Adiciona `tenant_id TEXT NOT NULL DEFAULT 'manta-interno'` em
--      `rag_chunks`, `rag_collections` e `sp_agent_routing` (as 2
--      últimas via ALTER TABLE IF EXISTS, pois nunca são criadas neste
--      repo — só populadas via INSERT assumindo schema pré-existente,
--      ver `2026_08_31_baseline_pre_existing_collections.sql` linhas
--      ~29-33).
--   2. Habilita RLS nessas 3 tabelas com uma policy de tenant que
--      COMPÕE com o padrão já usado no repo
--      (`current_setting('app.current_tenant_id', true)` — mesmo estilo
--      de `current_setting('app.current_agent_id', true)` usado em
--      `2026_07_25_agent_background_jobs.sql`). NÃO toca nas 13
--      policies já existentes de agent_id/user_id em outras tabelas
--      (`2026_07_25_agent_background_jobs.sql`,
--      `2026_07_25_v5_0_agent_memory_cache.sql`,
--      `2026_07_25_v5_0_agent_memory_tiering.sql`,
--      `2026_07_25_observability_maestro_runs.sql`,
--      `db/migrations/001_maestro_os_v6_schema.sql`) — apenas as 3
--      tabelas-alvo acima recebem policy nova.
--   3. Cria tabela `tenants` (não existia neste repositório) com os 3
--      tenants propostos no ADR. `aysa` e `regis-dd` são PROPOSTOS,
--      pendentes de confirmação MN (ver ADR, Gate humano D1) — não
--      tratar como uso confirmado em produção.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_09_13_d1_multi_tenancy.sql
--
-- ROLLBACK: ver bloco DOWN comentado no fim do arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Tabela de referência de tenants (não existia no repositório)
-- ---------------------------------------------------------------------
-- `aysa` e `regis-dd` são PROPOSTOS pelo ADR D1, pendentes de
-- confirmação MN — ver docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md,
-- seção D1 "Gate humano". Não é evidência de uso real desses tenants
-- em produção; é só o registro do que foi proposto.

CREATE TABLE IF NOT EXISTS tenants (
  id          TEXT PRIMARY KEY,
  name        TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tenants IS
  'Registro de tenants para isolamento multi-tenant (D1). manta-interno '
  'é o default operacional real; aysa e regis-dd são PROPOSTOS pelo ADR '
  'D1-D4, pendentes de confirmação MN antes de uso em produção.';

INSERT INTO tenants (id, name)
VALUES
  ('manta-interno', 'Manta Associados (interno, default)'),
  ('aysa',          'AySA — saneamento Argentina (PROPOSTO, pendente confirmação MN)'),
  ('regis-dd',      'Régis Bittencourt — due diligence M&A (PROPOSTO, pendente confirmação MN)')
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. tenant_id nas 3 tabelas-alvo
-- ---------------------------------------------------------------------

-- rag_chunks: assume a definição canônica de 2026_08_02_rag_hierarchy_v5.sql
-- (ver aviso (a) no topo do arquivo). IF EXISTS evita falha caso o nome
-- real em produção seja manta_rag_chunks (ver aviso (b)).
ALTER TABLE IF EXISTS rag_chunks
  ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'manta-interno';

-- rag_collections: nunca criada neste repo (só populada via INSERT em
-- 2026_08_31_baseline_pre_existing_collections.sql, assumindo schema
-- pré-existente) — por isso ALTER TABLE IF EXISTS.
ALTER TABLE IF EXISTS rag_collections
  ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'manta-interno';

-- sp_agent_routing: idem — nunca criada neste repo.
ALTER TABLE IF EXISTS sp_agent_routing
  ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'manta-interno';

-- ---------------------------------------------------------------------
-- 3. RLS — policy de tenant, composta com o padrão já usado no repo
-- ---------------------------------------------------------------------
-- Mesmo estilo de current_setting('app.current_agent_id', true) usado
-- em 2026_07_25_agent_background_jobs.sql, agora para tenant. Esta
-- migração NÃO altera nenhuma policy existente de agent_id/user_id —
-- só adiciona policy nova de tenant_id nestas 3 tabelas, que não tinham
-- nenhuma policy de tenant antes (e, no caso de rag_chunks, nenhuma
-- policy de tipo algum antes desta migração).

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'rag_chunks') THEN
    ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS rag_chunks_tenant_isolation ON rag_chunks;
    CREATE POLICY rag_chunks_tenant_isolation ON rag_chunks
      USING (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      )
      WITH CHECK (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      );
  END IF;
END;
$$;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'rag_collections') THEN
    ALTER TABLE rag_collections ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS rag_collections_tenant_isolation ON rag_collections;
    CREATE POLICY rag_collections_tenant_isolation ON rag_collections
      USING (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      )
      WITH CHECK (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      );
  END IF;
END;
$$;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'sp_agent_routing') THEN
    ALTER TABLE sp_agent_routing ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS sp_agent_routing_tenant_isolation ON sp_agent_routing;
    CREATE POLICY sp_agent_routing_tenant_isolation ON sp_agent_routing
      USING (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      )
      WITH CHECK (
        tenant_id = CURRENT_SETTING('app.current_tenant_id', true)
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true
      );
  END IF;
END;
$$;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP POLICY IF EXISTS sp_agent_routing_tenant_isolation ON sp_agent_routing;
-- DROP POLICY IF EXISTS rag_collections_tenant_isolation ON rag_collections;
-- DROP POLICY IF EXISTS rag_chunks_tenant_isolation ON rag_chunks;
--
-- ALTER TABLE IF EXISTS sp_agent_routing DROP COLUMN IF EXISTS tenant_id;
-- ALTER TABLE IF EXISTS rag_collections DROP COLUMN IF EXISTS tenant_id;
-- ALTER TABLE IF EXISTS rag_chunks DROP COLUMN IF EXISTS tenant_id;
--
-- DROP TABLE IF EXISTS tenants;
--
-- COMMIT;
