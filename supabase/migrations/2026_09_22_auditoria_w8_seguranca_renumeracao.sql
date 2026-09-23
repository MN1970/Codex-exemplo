-- =====================================================================
-- Auditoria do sistema Manta Maestro — onda W8 (Supabase)
-- Plano: docs/PLANO-AUDITORIA-v1.md · Relatório: docs/auditoria/RELATORIO-AUDITORIA-2026-09-22.md
-- Projeto: manta-maestro (ogxxgvgtulrbbppshjie) · Aplicada em 2026-09-22
--
-- Parte A — segurança (advisors do Supabase, nível ERROR/WARN)
-- Parte B — renumeração de segmentos em manta_agent_capabilities para a
--           numeração canônica do SharePoint (decisão D2 de MN, 2026-09-22)
-- Parte C — registro da decisão nos change requests pendentes
--
-- Reversão: ver bloco "ROLLBACK" no fim do arquivo.
-- =====================================================================

-- ---------------------------------------------------------------------
-- A1. manta_artefatos: RLS estava desabilitado e anon/authenticated
--     tinham INSERT/UPDATE/DELETE/TRUNCATE. Passa a leitura pública
--     somente (mesmo padrão de rag_collections / sp_agent_routing).
--     Escritas continuam possíveis via service_role.
-- ---------------------------------------------------------------------
ALTER TABLE public.manta_artefatos ENABLE ROW LEVEL SECURITY;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, TRIGGER, REFERENCES
  ON public.manta_artefatos FROM anon, authenticated;
DROP POLICY IF EXISTS read_only_anon_authenticated ON public.manta_artefatos;
CREATE POLICY read_only_anon_authenticated ON public.manta_artefatos
  FOR SELECT TO anon, authenticated USING (true);

-- ---------------------------------------------------------------------
-- A2. Views de uso por usuário (maestro_cost_log): eram SECURITY DEFINER
--     e expunham custo/uso por usuário a anon. A tabela de origem só
--     permite maestro_core e service_role — as views passam a respeitar
--     isso (security_invoker).
-- ---------------------------------------------------------------------
ALTER VIEW public.v_top_users           SET (security_invoker = true);
ALTER VIEW public.v_usage_by_user_agent SET (security_invoker = true);

-- ---------------------------------------------------------------------
-- A3. Views r2j_*: eram SECURITY DEFINER. As tabelas de origem já têm
--     policy de leitura para anon ("leitura_anon"); acrescenta a mesma
--     leitura para authenticated (hoje authenticated só lia via view
--     definer) e passa as views a security_invoker — sem mudança de
--     resultado para anon.
-- ---------------------------------------------------------------------
DO $$
DECLARE t text;
BEGIN
  FOR t IN
    SELECT tablename FROM pg_policies
    WHERE schemaname = 'public' AND tablename LIKE 'r2j\_%' AND policyname = 'leitura_anon'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS leitura_authenticated ON public.%I', t);
    EXECUTE format('CREATE POLICY leitura_authenticated ON public.%I FOR SELECT TO authenticated USING (true)', t);
  END LOOP;
END $$;

ALTER VIEW public.v_r2j_servicos              SET (security_invoker = true);
ALTER VIEW public.v_r2j_quant_por_rodovia     SET (security_invoker = true);
ALTER VIEW public.v_r2j_quant_por_frente      SET (security_invoker = true);
ALTER VIEW public.v_r2j_capex_anual           SET (security_invoker = true);
ALTER VIEW public.v_r2j_opex_anual            SET (security_invoker = true);
ALTER VIEW public.v_r2j_opex_rubrica          SET (security_invoker = true);
ALTER VIEW public.v_r2j_quant_capex_servico   SET (security_invoker = true);
ALTER VIEW public.v_r2j_obras_geo             SET (security_invoker = true);
ALTER VIEW public.v_r2j_retigrafico           SET (security_invoker = true);
ALTER VIEW public.v_r2j_inventario_por_classe SET (security_invoker = true);
ALTER VIEW public.v_r2j_oae_resumo            SET (security_invoker = true);

-- A4. search_path fixo (lint function_search_path_mutable). A função só
--     usa builtins (lower/btrim/coalesce).
ALTER FUNCTION public.r2j_un_norm(text) SET search_path = '';

-- ---------------------------------------------------------------------
-- B. Renumeração de segmentos (D2): manta_agent_capabilities usava a
--    numeração antiga ("Convenção A"). A numeração canônica é a do
--    SharePoint (01-segmentos/ e INDICE-CANONICAL.md):
--      antigo 03-S5  túneis      → 03-S12
--      antigo 03-S6  portos      → 03-S7
--      antigo 03-S7  aeroportos  → 03-S8
--      antigo 03-S8  saneamento  → 03-S9
--      antigo 03-S9  energia     → 03-S10
--      antigo 03-S10 barragens   → 03-S11
--      antigo 03-S11 mineração   → 03-S13
--      antigo 03-S12 óleo e gás  → 03-S14
--      antigo 03-S13 edificações → 03-S6
--    S1–S4 não mudam. Chave é (agent_id, capability) — mapeamento pela
--    capability evita colisão durante o UPDATE. Nenhuma FK referencia a
--    tabela. Logs históricos (manta_trace, manta_agent_messages) não são
--    reescritos: registram o código vigente na época.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_2026_09_22_renumeracao (
  capability   text PRIMARY KEY,
  agent_id_old text NOT NULL,
  agent_id_new text NOT NULL,
  applied_at   timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.audit_2026_09_22_renumeracao ENABLE ROW LEVEL SECURITY;

INSERT INTO public.audit_2026_09_22_renumeracao (capability, agent_id_old, agent_id_new) VALUES
  ('especialista-tuneis',      '03-S5',  '03-S12'),
  ('especialista-portos',      '03-S6',  '03-S7'),
  ('especialista-aeroportos',  '03-S7',  '03-S8'),
  ('especialista-saneamento',  '03-S8',  '03-S9'),
  ('especialista-energia',     '03-S9',  '03-S10'),
  ('especialista-barragens',   '03-S10', '03-S11'),
  ('especialista-mineracao',   '03-S11', '03-S13'),
  ('especialista-oleo-gas',    '03-S12', '03-S14'),
  ('especialista-edificacoes', '03-S13', '03-S6')
ON CONFLICT (capability) DO NOTHING;

UPDATE public.manta_agent_capabilities c
   SET agent_id = r.agent_id_new, updated_at = now()
  FROM public.audit_2026_09_22_renumeracao r
 WHERE c.capability = r.capability
   AND c.agent_id = r.agent_id_old;

-- ---------------------------------------------------------------------
-- C. Change requests pendentes da rodada noturna (2026-09-20)
-- ---------------------------------------------------------------------
UPDATE public.agent_change_requests
   SET status = 'rejected'
 WHERE request_id = 'CR-2026-09-20-TAXONOMY-01' AND status = 'pending';
-- Motivo: MN decidiu em 2026-09-22 (D2) adotar a numeração do
-- SharePoint (S6=Edificações … S11=Barragens), o oposto do proposto.

UPDATE public.agent_change_requests
   SET status = 'applied', applied_at = now(),
       applied_migration = '2026_09_22_auditoria_w8_seguranca_renumeracao'
 WHERE request_id = 'CR-2026-09-20-SEGMENTS-01' AND status = 'pending';
-- Motivo: Mineração e Óleo&Gás já são segmentos oficiais no SharePoint
-- (S13 e S14, INDICE-CANONICAL.md v1.1); renumerados acima. A parte 2
-- (fonte _C vs _D) já foi resolvida na skill A1-proposta v3.3.7.

-- =====================================================================
-- ROLLBACK (manual, se necessário)
-- UPDATE public.manta_agent_capabilities c SET agent_id = r.agent_id_old
--   FROM public.audit_2026_09_22_renumeracao r
--  WHERE c.capability = r.capability AND c.agent_id = r.agent_id_new;
-- ALTER VIEW public.v_top_users SET (security_invoker = false);  -- etc.
-- ALTER TABLE public.manta_artefatos DISABLE ROW LEVEL SECURITY;
-- UPDATE public.agent_change_requests SET status='pending', applied_at=NULL, applied_migration=NULL
--  WHERE request_id IN ('CR-2026-09-20-TAXONOMY-01','CR-2026-09-20-SEGMENTS-01');
-- =====================================================================
