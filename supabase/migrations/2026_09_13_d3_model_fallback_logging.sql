-- Manta Maestro — D3 Model Fallback Logging
-- ADR: docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md (correção 2026-09-13)
-- Ticket: MNT-2026-ADR-D1-D4
--
-- `maestro_runs.model_tier` (2026_07_25_observability_maestro_runs.sql)
-- já registra o tier FINAL usado numa run. Esta migração complementa
-- com o tier ORIGINALMENTE solicitado e o motivo de eventual fallback
-- (ver src/maestro/model_fallback.py — ModelTierPolicy), para permitir
-- auditoria de degradação Haiku<->Sonnet e de casos "awaiting_human_decision"
-- em agentes Opus-obrigatórios (agente-claims, agente-advisory,
-- agente-arquiteto-ia) sem alterar o schema já existente.
--
-- Não-destrutivo: apenas ADD COLUMN IF NOT EXISTS com defaults seguros.

BEGIN;

ALTER TABLE maestro_runs
  ADD COLUMN IF NOT EXISTS tier_requested TEXT,
  ADD COLUMN IF NOT EXISTS fallback_reason TEXT,
  ADD COLUMN IF NOT EXISTS escalation_notified_human BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN maestro_runs.tier_requested IS
  'D3: tier originalmente solicitado pelo agente/workflow (haiku|sonnet|opus), antes de qualquer fallback. Complementa model_tier (tier final efetivamente usado).';
COMMENT ON COLUMN maestro_runs.fallback_reason IS
  'D3: motivo do fallback de tier, quando tier_requested != model_tier (ex.: rate limit, overload, retries esgotados). NULL quando não houve fallback.';
COMMENT ON COLUMN maestro_runs.escalation_notified_human IS
  'D3: TRUE quando um caso de Opus indisponível (agente sem fallback automático) foi notificado a um humano em vez de degradar silenciosamente. Default FALSE.';

COMMIT;

-- =====================================================================
-- VERSÃO: 2026-09-13 (D3 — fallback de modelo)
-- STATUS: proposta aprovada por MN, implementação corrigida contra o
--         código real (ver ADR-D1-D4, "Correção de diagnóstico 2026-09-13")
-- =====================================================================
