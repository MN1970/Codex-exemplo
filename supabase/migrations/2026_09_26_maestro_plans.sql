-- ============================================================================
-- v5.5.0 — Registro plano × executado do planejador do Maestro (N0)
-- ============================================================================
-- Status: CANDIDATA — NÃO aplicada. Requer gate humano MN antes de rodar
-- no projeto `manta-maestro` (ogxxgvgtulrbbppshjie).
--
-- Cada execução do Maestro grava o plano gerado por src/maestro/planner.py
-- e o que de fato rodou. Serve para:
--   1. medir se o planejador acerta (agentes fora do plano = sinal de ajuste);
--   2. calibrar os tetos de tokens por nível (N0–N3) com dados reais;
--   3. ver custo por plano, sem depender de agent_episodes.
--
-- Só cria objetos novos (IF NOT EXISTS). Não altera tabelas existentes.
-- Rollback no fim do arquivo.
-- ============================================================================

CREATE TABLE IF NOT EXISTS maestro_plans (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at          timestamptz NOT NULL DEFAULT now(),
  pedido              text NOT NULL,
  metodo              text NOT NULL CHECK (metodo IN ('palavras-chave', 'llm')),
  agentes_planejados  text[] NOT NULL DEFAULT '{}',
  agentes_executados  text[] NOT NULL DEFAULT '{}',
  guardioes           text[] NOT NULL DEFAULT '{}',
  teto_tokens         integer NOT NULL,
  tokens_consumidos   integer,
  custo_usd           numeric(10, 4),
  requer_aprovacao    boolean NOT NULL DEFAULT false,
  aprovado            boolean,
  plano               jsonb NOT NULL
);

CREATE INDEX IF NOT EXISTS maestro_plans_created_at_idx
  ON maestro_plans (created_at DESC);

-- RLS habilitada desde a criação (achado AI-6: não repetir tabelas públicas
-- sem RLS). Escrita/leitura só pelo service role do Maestro.
ALTER TABLE maestro_plans ENABLE ROW LEVEL SECURITY;

-- Aderência ao plano: execuções que chamaram agentes fora do plano ou
-- estouraram o teto de tokens.
CREATE OR REPLACE VIEW v_maestro_plan_aderencia
WITH (security_invoker = true) AS
SELECT
  date_trunc('day', created_at)                                    AS dia,
  count(*)                                                         AS execucoes,
  count(*) FILTER (WHERE NOT (agentes_executados <@ agentes_planejados))
                                                                   AS fora_do_plano,
  count(*) FILTER (WHERE tokens_consumidos > teto_tokens)          AS estourou_teto,
  round(avg(cardinality(agentes_executados)), 2)                   AS media_agentes,
  round(avg(tokens_consumidos))                                    AS media_tokens,
  sum(custo_usd)                                                   AS custo_usd
FROM maestro_plans
GROUP BY 1
ORDER BY 1 DESC;

-- Rollback:
-- DROP VIEW IF EXISTS v_maestro_plan_aderencia;
-- DROP TABLE IF EXISTS maestro_plans;
