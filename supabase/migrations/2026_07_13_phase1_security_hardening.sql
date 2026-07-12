-- Fase 1 — Fixes de segurança em produção
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 1
--
-- Status: APLICADA em produção 2026-07-12 via MCP apply_migration
-- (nome interno da migração: phase1_security_hardening_v4_6_audit).
-- Este arquivo existe para rastreabilidade no repo.
--
-- Resolveu 2 ERROR + 5 WARN dos advisors. Restaram 10 INFO (RLS sem policy
-- em 10 tabelas) e 1 WARN (vector extension em public — legado, requer
-- rebuild de HNSW para mover para extensions).

-- 1. SECURITY DEFINER → INVOKER nas 2 views identificadas pelos advisors
ALTER VIEW public.v_manta_l05_overview SET (security_invoker = on);
ALTER VIEW public.v_ke_por_agente     SET (security_invoker = on);

-- 2. search_path imutável em 6 funções (evita function injection)
ALTER FUNCTION public.manta_rag_search(vector, integer, text, text[], text, date, date, boolean)
  SET search_path = public, extensions;
ALTER FUNCTION public.manta_rag_fts(text, integer, text, text[])
  SET search_path = public, extensions;
ALTER FUNCTION public.rag_search(vector, integer, rag_collection, rag_agent, text, smallint)
  SET search_path = public, extensions;
ALTER FUNCTION public.wf_akp_touch_updated_at()
  SET search_path = public, extensions;
ALTER FUNCTION public.manta_agent_rag(text, vector, integer)
  SET search_path = public, extensions;
ALTER FUNCTION public.manta_rag_agent_search(vector, text, integer)
  SET search_path = public, extensions;
