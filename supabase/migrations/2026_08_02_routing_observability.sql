-- Manta Maestro — Routing observability (routing_events / routing_feedback)
-- Ticket: MNT-2026-ECOSYSTEM-UPGRADE-V5 (Fase 2.1 "Feedback loop" persistence
-- + Fase 4.2 "Quarterly reviews")
--
-- CONTEXTO / POR QUE ESTA MIGRAÇÃO EXISTE
-- ---------------------------------------------------------------------
-- `feedback_loop.py` (raiz do repo) já implementa o loop de feedback
-- (Thompson Sampling) com um `SQLiteFeedbackStore` totalmente funcional,
-- e deixa um `SupabaseFeedbackStore` como *stub não implementado* —
-- ou seja, em produção (Supabase) as tabelas `routing_events` e
-- `routing_feedback` **ainda não existem em lugar nenhum**. Sem elas,
-- nenhuma query de `supabase/analytics/quarterly_review_kpis.sql` roda.
--
-- Esta migração cria, em Postgres, o equivalente exato do schema já
-- validado em `SQLiteFeedbackStore._init_schema()` (mesmos nomes de
-- coluna, para que `SupabaseFeedbackStore` seja um port 1:1, não um
-- redesign) — e ACRESCENTA apenas 2 colunas nullable (`latency_ms`,
-- `tokens_used`) que o schema mais rico do
-- `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §4.1 previa, mas que o
-- runtime ainda não loga. Ver "PENDÊNCIAS DE INSTRUMENTAÇÃO" abaixo.
--
-- O que **não** está aqui, de propósito: `outcome`, `is_composed`,
-- `composed_agents`, `composition_strategy`, `outcome_agent_id` (do
-- §4.1). Esses campos descrevem fallback (Fase 2.3) e composição
-- multi-agente (Fase 2.2) — nenhuma das duas está implementada no
-- Maestro hoje (só o feedback loop / Fase 2.1 está). Adicionar essas
-- colunas antes de existir o código que as popula deixaria o schema
-- "mentindo" sobre capacidades que não existem. Criar em migração
-- separada quando Fase 2.2/2.3 forem implementadas.
--
-- ATENÇÃO — CONFLITO DE SCHEMA JÁ EXISTENTE (não corrigido aqui):
-- há DUAS definições de `agent_health` no repo hoje, incompatíveis
-- entre si:
--   1. `services/heartbeat/heartbeat-service.js` (DDL embutido) +
--      `supabase/migrations/2026_08_02_agent_health_heartbeat.sql`:
--      1 linha por agente (`agent_id TEXT PRIMARY KEY`), estado atual.
--      **Esta é a versão que o serviço em produção realmente usa.**
--   2. `supabase/migrations/2026_08_02_agent_auto_registration.sql`:
--      série temporal (`id BIGSERIAL`, `recorded_at`), 1 linha por
--      amostra — copia do schema aspiracional do §4.1.
-- Como ambas usam `CREATE TABLE IF NOT EXISTS agent_health`, a que
-- rodar primeiro "vence" silenciosamente e a segunda vira no-op (sem
-- erro, sem colunas adicionadas). Isso quebra a query 4.5 de
-- `quarterly_review_kpis.sql` (uptime histórico) se a versão vencedora
-- for a #1 (estado único, sem histórico). Resolver antes da 1ª
-- quarterly review real: escolher uma das duas, migrar a outra, e
-- deixar 1 única fonte de verdade. Não resolvido nesta migração porque
-- foge do escopo de "observabilidade de routing".
--
-- PENDÊNCIAS DE INSTRUMENTAÇÃO (para o Maestro popular os dados):
--   - `latency_ms`: tempo de handling do agente escolhido. Hoje nem
--     `feedback_loop.py` nem os serviços em `infra/agent-registry/`
--     medem isso no caminho de routing (existe `latencyMs` em
--     `infra/agent-registry/auto-registration-service.js`, mas é do
--     self-test de registro, não do tráfego real).
--   - `tokens_used`: soma de tokens (input+output) da chamada Claude
--     para aquele agente — necessário para o KPI "cost/request" da
--     quarterly review. Precisa ser lido de `usage.input_tokens` +
--     `usage.output_tokens` da resposta da API e passado para
--     `log_routing_event(...)` (ou gravado num UPDATE logo após).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_02_routing_observability.sql
--
-- Esta é uma MIGRAÇÃO CANDIDATA — gate humano MN antes de aplicar.
-- ROLLBACK: ver bloco DOWN no fim do arquivo.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. routing_events — 1 linha por chamada a getNextAgent()
-- ---------------------------------------------------------------------
-- Espelha SQLiteFeedbackStore._init_schema() (feedback_loop.py) coluna
-- a coluna, para que SupabaseFeedbackStore seja um port direto.

CREATE TABLE IF NOT EXISTS routing_events (
  id                BIGSERIAL PRIMARY KEY,
  routing_id        TEXT UNIQUE NOT NULL,     -- uuid4, gerado por getNextAgent()
  query_hash        TEXT,                     -- sha256(query) — feedback_loop.py sempre preenche
  query_preview     TEXT,                     -- query[:200] — só para debug/QA humano, não PII-safe por padrão
  top_candidates    JSONB NOT NULL DEFAULT '[]'::jsonb,  -- lista de agent_id candidatos (shortlist)
  chosen_agent_id   TEXT NOT NULL REFERENCES agents(id),
  chosen_confidence NUMERIC NOT NULL,         -- theta_hat amostrado (Thompson Sampling), 0..1
  samples           JSONB NOT NULL DEFAULT '{}'::jsonb,  -- {agent_id: theta_hat} de todos os candidatos

  -- Extensões pendentes de instrumentação (ver comentário acima) —
  -- NULL até o Maestro passar a medir/logar estes valores.
  latency_ms        INT,
  tokens_used        INT,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_routing_events_created  ON routing_events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_events_agent     ON routing_events (chosen_agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_events_confidence ON routing_events (chosen_confidence);

COMMENT ON TABLE routing_events IS
  'Uma linha por decisão de roteamento do Maestro (getNextAgent() em feedback_loop.py). '
  'latency_ms e tokens_used ficam NULL até o runtime do Maestro passar a registrá-los — '
  'ver cabeçalho desta migração para os pontos de instrumentação pendentes.';

-- ---------------------------------------------------------------------
-- 2. routing_feedback — 1 linha por chamada a acceptFeedback()
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS routing_feedback (
  id           BIGSERIAL PRIMARY KEY,
  routing_id   TEXT NOT NULL REFERENCES routing_events(routing_id) ON DELETE CASCADE,
  agent_id     TEXT NOT NULL REFERENCES agents(id),
  feedback     TEXT NOT NULL CHECK (feedback IN ('correct', 'wrong', 'slow', 'incomplete')),
  reward       NUMERIC NOT NULL CHECK (reward >= 0 AND reward <= 1),  -- ver DEFAULT_REWARD_MAP em feedback_loop.py
  comment      TEXT,                          -- comentário livre opcional (não usado pelo bandit)
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_routing_feedback_agent   ON routing_feedback (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_feedback_routing ON routing_feedback (routing_id);

COMMENT ON TABLE routing_feedback IS
  'Uma linha por acceptFeedback() do bandit (feedback_loop.py). feedback/reward alimentam '
  'a atualização Beta(alpha,beta) em agent_posteriors e as métricas de accuracy da quarterly review.';

-- ---------------------------------------------------------------------
-- 3. agent_posteriors — estado atual da crença Beta(alpha,beta) por agente
-- ---------------------------------------------------------------------
-- Opcional para as queries de KPI, mas necessário se `SupabaseFeedbackStore`
-- for implementado de fato (hoje é um stub) — mantém o estado do bandit
-- persistente entre reinícios do processo Maestro.

CREATE TABLE IF NOT EXISTS agent_posteriors (
  agent_id     TEXT PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
  alpha        NUMERIC NOT NULL DEFAULT 1.0,
  beta         NUMERIC NOT NULL DEFAULT 1.0,
  n_updates    INT NOT NULL DEFAULT 0,
  updated_at   TIMESTAMPTZ
);

COMMENT ON TABLE agent_posteriors IS
  'Beta(alpha,beta) posterior por agente (Thompson Sampling, feedback_loop.py). '
  'mean = alpha/(alpha+beta) é a estimativa atual de "taxa de acerto" do agente.';

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP TABLE IF EXISTS agent_posteriors;
-- DROP TABLE IF EXISTS routing_feedback;
-- DROP TABLE IF EXISTS routing_events;
--
-- COMMIT;
