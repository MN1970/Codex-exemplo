-- Manta Maestro — endurecimento de RLS (acesso indevido / vazamento)
-- Ticket: MNT-2026-SEC-RLS-01
--
-- MIGRAÇÃO CANDIDATA. Não aplicar em produção sem aprovação MN.
-- Ver docs/SEGURANCA-ARTEFATOS.md (seção "Achados Supabase 2026-09-26").
--
-- Problema: projeto `manta-maestro` expõe ~85 mil linhas de dados
-- comerciais (r2j_* — preços, receita, EVTEA, parâmetros de edital;
-- RAG; composições) via políticas `USING (true)` para o papel `anon`.
-- A chave anon fica embutida nos portais HTML, então qualquer pessoa
-- que abra o código-fonte de um portal lê essas tabelas pela REST API.
-- Além disso, `authenticated USING (true)` libera qualquer conta criada
-- no Supabase Auth, não só a equipe Manta.
--
-- O que esta migração faz:
--   1. Cria `private.is_manta_member()` (fora do schema exposto pela API):
--      verdadeiro só para JWT com e-mail @mantaassociados.com.
--   2. Remove as políticas de leitura `anon`/`authenticated` com
--      `USING (true)` nas tabelas sensíveis e cria `manta_member_read`.
--   3. Troca o INSERT anônimo de pk_queries/pk_feedback por INSERT de
--      membro (evita spam / envenenamento do feedback do RAG).
--   4. Revoga os GRANTs de tabela do papel `anon` nessas tabelas
--      (defesa em profundidade caso alguém recrie uma política aberta).
--
-- NÃO altera: políticas de service_role e maestro_core; a função
-- `get_projeto_status_publico` (exceção pública intencional — só
-- devolve snapshots aprovados e publicados).
--
-- IMPACTO: portais que hoje leem essas tabelas só com a chave anon
-- passam a receber lista vazia. Antes de aplicar, migrar cada portal
-- para login Supabase Auth (Azure/Entra ID ou magic link restrito ao
-- domínio) ou para uma edge function com service_role no servidor.
-- Também DESATIVAR cadastro aberto em Auth > Providers (signups).
--
-- ROLLBACK: bloco DOWN no fim do arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Função de pertencimento (schema não exposto pela API REST)
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS private;
REVOKE ALL ON SCHEMA private FROM PUBLIC, anon;
GRANT USAGE ON SCHEMA private TO authenticated;

CREATE OR REPLACE FUNCTION private.is_manta_member()
RETURNS boolean
LANGUAGE sql
STABLE
SET search_path = ''
AS $$
  -- Depende de cadastro aberto DESATIVADO e confirmação de e-mail ativa
  -- no Supabase Auth; senão qualquer um cria conta com esse domínio.
  SELECT coalesce(lower(auth.jwt() ->> 'email') LIKE '%@mantaassociados.com', false);
$$;

REVOKE ALL ON FUNCTION private.is_manta_member() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION private.is_manta_member() TO authenticated;

-- ---------------------------------------------------------------------
-- 2. Leitura restrita a membros nas tabelas sensíveis
-- ---------------------------------------------------------------------
DO $$
DECLARE
  t   text;
  pol record;
  sensitive text[] := ARRAY[
    -- Rota 2 de Julho (dados comerciais do cliente)
    'r2j_composicao_insumos','r2j_composicoes','r2j_cronograma_obra',
    'r2j_dispositivos','r2j_eap','r2j_evtea','r2j_inventario_linear',
    'r2j_oae','r2j_obra_servicos','r2j_obras','r2j_opex_arvore',
    'r2j_opex_itens','r2j_parametros_edital','r2j_pavimento','r2j_per',
    'r2j_precos_base','r2j_precos_unitarios','r2j_receita',
    'r2j_trechos_homogeneos',
    -- RAG / conhecimento
    'manta_rag_chunks','manta_rag_documents','manta_rag_cases',
    'manta_rag_ml_predictions','manta_rag_queries','rag_chunks',
    'knowledge_extractions','ke_embeddings','teses_academicas',
    -- Portal PK / composições
    'pk_associations','pk_composition_inputs','pk_compositions',
    'pk_sicro_items','pk_queries','pk_feedback','servicos',
    -- Rastreabilidade e inventário de artefatos
    'manta_trace','manta_artefatos','sp258_drenagem_mapa',
    -- Metadados de routing (baixa sensibilidade, mas revelam estrutura)
    'rag_collections','sp_agent_routing',
    'maestro_routing_keywords','maestro_routing_keywords_v6'
  ];
BEGIN
  FOREACH t IN ARRAY sensitive LOOP
    IF to_regclass(format('public.%I', t)) IS NULL THEN
      RAISE NOTICE 'tabela % não existe — ignorada', t;
      CONTINUE;
    END IF;

    -- Remove políticas abertas (USING true) para anon/authenticated/public.
    FOR pol IN
      SELECT policyname
        FROM pg_policies
       WHERE schemaname = 'public'
         AND tablename  = t
         AND roles && ARRAY['anon','authenticated','public']::name[]
         AND coalesce(qual, 'true') = 'true'
         AND coalesce(with_check, 'true') = 'true'
    LOOP
      EXECUTE format('DROP POLICY %I ON public.%I', pol.policyname, t);
    END LOOP;

    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);

    EXECUTE format('DROP POLICY IF EXISTS manta_member_read ON public.%I', t);
    EXECUTE format(
      'CREATE POLICY manta_member_read ON public.%I
         FOR SELECT TO authenticated
         USING ((SELECT private.is_manta_member()))', t);

    EXECUTE format('REVOKE ALL ON public.%I FROM anon', t);
  END LOOP;
END $$;

-- ---------------------------------------------------------------------
-- 3. Registro de consultas/feedback do Portal PK: só membros inserem
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS manta_member_insert ON public.pk_queries;
CREATE POLICY manta_member_insert ON public.pk_queries
  FOR INSERT TO authenticated
  WITH CHECK ((SELECT private.is_manta_member()));

DROP POLICY IF EXISTS manta_member_insert ON public.pk_feedback;
CREATE POLICY manta_member_insert ON public.pk_feedback
  FOR INSERT TO authenticated
  WITH CHECK ((SELECT private.is_manta_member()));

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário — reabre o acesso anon)
-- =====================================================================
-- BEGIN;
-- DO $$
-- DECLARE t text;
-- BEGIN
--   FOR t IN SELECT tablename FROM pg_policies
--             WHERE schemaname='public' AND policyname='manta_member_read'
--   LOOP
--     EXECUTE format('DROP POLICY manta_member_read ON public.%I', t);
--     EXECUTE format('GRANT SELECT ON public.%I TO anon', t);
--     EXECUTE format('CREATE POLICY read_only_anon_authenticated ON public.%I
--                       FOR SELECT TO anon, authenticated USING (true)', t);
--   END LOOP;
-- END $$;
-- DROP POLICY IF EXISTS manta_member_insert ON public.pk_queries;
-- DROP POLICY IF EXISTS manta_member_insert ON public.pk_feedback;
-- GRANT INSERT ON public.pk_queries, public.pk_feedback TO anon;
-- CREATE POLICY pk_queries_anon_insert  ON public.pk_queries  FOR INSERT TO anon WITH CHECK (true);
-- CREATE POLICY pk_feedback_anon_insert ON public.pk_feedback FOR INSERT TO anon WITH CHECK (true);
-- COMMIT;
