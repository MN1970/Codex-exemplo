-- =====================================================================
-- Manta Maestro — Agent Registry: schema completo de produção
-- Ticket: MNT-2026-AGENT-REGISTRY-SCHEMA
--
-- Este arquivo é uma MIGRAÇÃO CANDIDATA (mesma política dos demais
-- arquivos em supabase/migrations/: revisar contra o schema real do
-- projeto Supabase antes de aplicar; gate humano MN antes de merge —
-- ver CLAUDE.md § DEPLOY CHECKLIST v4.2).
--
-- ESCOPO
--   Tabelas: agents, agent_expertise, agent_capabilities, agent_health,
--   agent_heartbeats, routing_feedback, routing_events — mais tabelas
--   de suporte (agent_registry_history, agent_registry_meta) e views/
--   funções de conveniência para o Maestro (Manta 00).
--
-- ⚠️ ACHADO IMPORTANTE (revisar com MN antes de aplicar) ⚠️
--   Este repositório já contém DUAS migrações de 2026-08-02 que criam
--   `agents` e `agent_health`:
--     - 2026_08_02_agent_auto_registration.sql
--     - 2026_08_02_agent_health_heartbeat.sql
--   As duas definem uma tabela `agent_health` com formatos
--   INCOMPATÍVEIS entre si (uma é série temporal com BIGSERIAL id +
--   múltiplas linhas por agente; a outra é uma linha única por agente
--   com PK em agent_id). Como ambas usam `CREATE TABLE IF NOT EXISTS`,
--   quem rodar primeiro "vence" e o outro serviço (heartbeat-service.js
--   ou ab-test-service.js) quebra em runtime por coluna inexistente.
--   Esta migração RESOLVE o conflito:
--     1. Mantém `agent_health` como série temporal (formato usado de
--        fato por infra/agent-registry/ab-test-service.js).
--     2. Cria uma tabela NOVA e distinta, `agent_heartbeats`, com o
--        formato "estado atual" que services/heartbeat/heartbeat-service.js
--        espera (agent_id TEXT PRIMARY KEY, routable, etc).
--   AÇÃO PENDENTE (fora do escopo deste arquivo SQL): atualizar
--   services/heartbeat/heartbeat-service.js para gravar em
--   `agent_heartbeats` em vez de `agent_health` (troca de 1 string no
--   SQL do serviço). Sem essa troca, o heartbeat service continuará
--   tentando usar `agent_health` no formato errado.
--
-- Todo o restante do arquivo usa CREATE TABLE IF NOT EXISTS + ALTER
-- TABLE ... ADD COLUMN IF NOT EXISTS de propósito: a migração é segura
-- de aplicar independente da ordem relativa às duas de 2026-08-02
-- (convergem para o mesmo schema final nos dois casos).
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_29_agent_registry_schema.sql
--
-- ROLLBACK: ver bloco DOWN comentado no fim do arquivo.
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 0. Extensões
-- ---------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector (embeddings + HNSW)

-- ---------------------------------------------------------------------
-- 1. agents — catálogo mestre (bootstrap idempotente)
-- ---------------------------------------------------------------------
-- Grão: UMA linha por implementação distinta de agente (não por linha
-- de routing). `agente-infraestrutura` cobre sozinho os segmentos
-- S1-S5 (Rodovias, OAE, Ferrovia, Metrô, Túneis-parcial) — o detalhe
-- por segmento vive em `agent_expertise.segment_code`, não em colunas
-- múltiplas aqui. Por isso este catálogo tem 17 linhas mesmo o CLAUDE.md
-- falando em "20 agentes" (20 = entradas de routing do MAPA COMPLETO,
-- contando S1-S4 e S6-S10 separadamente e excluindo S5 por ser parcial/
-- compartilhado — ver seed §8 mais abaixo para a nota completa).

CREATE TABLE IF NOT EXISTS agents (
  id                      TEXT PRIMARY KEY,          -- slug do frontmatter, ex. "agente-saneamento"
  name                    TEXT NOT NULL,
  description             TEXT,

  -- Expertise (compat com infra/agent-registry/lib/parse-agent-md.js)
  expertise_primary       TEXT[] DEFAULT '{}',
  expertise_secondary     TEXT[] DEFAULT '{}',
  keywords                TEXT[] DEFAULT '{}',

  -- Capabilities (compat com o mesmo parser)
  model                   TEXT CHECK (model IN ('haiku', 'sonnet', 'opus')),
  skills                  TEXT[] DEFAULT '{}',
  tools                   TEXT[] DEFAULT '{}',
  rag_collections         TEXT[] DEFAULT '{}',

  -- Metadata
  version                 TEXT,
  tier                    INT DEFAULT 3,
  handoffs_to             TEXT[] DEFAULT '{}',
  lifecycle               TEXT DEFAULT 'alpha'
                           CHECK (lifecycle IN ('alpha', 'beta', 'prod', 'rejected', 'deprecated')),
  cost_per_call           INT DEFAULT 1000,

  -- Auto-registration / A-B test tracking (infra/agent-registry/*)
  source_path             TEXT,
  source_commit           TEXT,
  registered_at           TIMESTAMPTZ,
  traffic_percentage      INT DEFAULT 0 CHECK (traffic_percentage BETWEEN 0 AND 100),
  ab_test_started_at      TIMESTAMPTZ,
  ab_test_ends_at         TIMESTAMPTZ,
  promoted_at             TIMESTAMPTZ,
  promotion_status        TEXT DEFAULT 'pending'
                           CHECK (promotion_status IN ('pending', 'self_test_failed', 'ab_testing', 'promoted', 'rolled_back')),

  created_at              TIMESTAMPTZ DEFAULT now(),
  updated_at              TIMESTAMPTZ DEFAULT now()
);

-- Colunas novas desta migração (registro mestre CLAUDE.md v4.2: 3 eixos,
-- aliases, ciclo de vida de 8 fases, embeddings para busca semântica).
ALTER TABLE agents ADD COLUMN IF NOT EXISTS aliases                    TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE agents ADD COLUMN IF NOT EXISTS display_code               TEXT;                      -- ex. 'Manta 00', 'Manta 03-S6'
ALTER TABLE agents ADD COLUMN IF NOT EXISTS eixo                       SMALLINT;                  -- 1=horizontal, 2=vertical (segmento)
ALTER TABLE agents ADD COLUMN IF NOT EXISTS segment_codes              TEXT[] NOT NULL DEFAULT '{}'; -- ex. {S1,S2,S3,S4,S5}
ALTER TABLE agents ADD COLUMN IF NOT EXISTS segment_names              TEXT[] NOT NULL DEFAULT '{}'; -- paralelo a segment_codes
ALTER TABLE agents ADD COLUMN IF NOT EXISTS escalation_model           TEXT;                      -- 2º tier ex. haiku->sonnet, sonnet/opus
ALTER TABLE agents ADD COLUMN IF NOT EXISTS status_label               TEXT;                      -- espelha texto literal do CLAUDE.md
ALTER TABLE agents ADD COLUMN IF NOT EXISTS status_note                TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS lifecycle_phases_supported SMALLINT[] NOT NULL DEFAULT ARRAY[1,2,3,4,5,6,7,8]::SMALLINT[];
ALTER TABLE agents ADD COLUMN IF NOT EXISTS description_embedding      vector(384); -- BAAI/bge-small-en-v1.5 (RAG Supabase atual do Maestro)
ALTER TABLE agents ADD COLUMN IF NOT EXISTS registry_version           TEXT;        -- versão do CLAUDE.md que introduziu/tocou a linha
ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_active                  BOOLEAN NOT NULL DEFAULT true;

-- Constraints (idempotentes via DO $$ ... EXCEPTION WHEN duplicate_object)
DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT chk_agents_eixo CHECK (eixo IS NULL OR eixo IN (1, 2));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT chk_agents_eixo_segmentos CHECK (
    eixo IS NULL
    OR (eixo = 1 AND segment_codes = '{}')
    OR (eixo = 2 AND array_length(segment_codes, 1) > 0)
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT chk_agents_segment_codes_dominio CHECK (
    segment_codes <@ ARRAY['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11']::TEXT[]
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT chk_agents_escalation_model CHECK (
    escalation_model IS NULL
    OR (escalation_model IN ('haiku', 'sonnet', 'opus') AND escalation_model <> model)
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT chk_agents_lifecycle_phases CHECK (
    lifecycle_phases_supported <@ ARRAY[1,2,3,4,5,6,7,8]::SMALLINT[]
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

COMMENT ON TABLE agents IS
  'Catálogo mestre dos agentes IA da Manta Associados (CLAUDE.md master registry). '
  'Uma linha por implementação de agente; segmentos múltiplos de um mesmo agente '
  '(ex. agente-infraestrutura cobrindo S1-S5) ficam em segment_codes + agent_expertise.';
COMMENT ON COLUMN agents.eixo IS '1 = horizontal (transversal), 2 = vertical (segmento C3). O 3º eixo do CLAUDE.md (ciclo de vida) é lifecycle_phases_supported, não um valor de eixo.';
COMMENT ON COLUMN agents.description_embedding IS 'Embedding da description para routing semântico. Backfill via pipeline de ingestão (BAAI/bge-small-en-v1.5, 384d) — NULL até então.';

-- ---------------------------------------------------------------------
-- 2. agent_expertise — normaliza expertise_primary/secondary/keywords
-- ---------------------------------------------------------------------
-- Uma linha por (agente, segmento opcional, termo). segment_code é
-- NULL para expertise que vale para o agente inteiro, e 'S1'..'S10'
-- quando o termo é específico de um segmento coberto por um agente
-- multi-segmento (ex. agente-infraestrutura).

CREATE TABLE IF NOT EXISTS agent_expertise (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id        TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  segment_code    TEXT,
  expertise_type  TEXT NOT NULL CHECK (expertise_type IN ('primary', 'secondary', 'keyword', 'norm')),
  label           TEXT NOT NULL,
  weight          SMALLINT NOT NULL DEFAULT 100 CHECK (weight BETWEEN 0 AND 200),
  embedding       vector(384),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT chk_expertise_segment_dominio CHECK (
    segment_code IS NULL OR segment_code IN ('S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11')
  ),
  CONSTRAINT uq_expertise UNIQUE (agent_id, segment_code, expertise_type, label)
);

COMMENT ON TABLE agent_expertise IS
  'Termos de expertise/routing por agente (e opcionalmente por segmento), com peso '
  'para desempate no Maestro. Substitui/normaliza agents.expertise_primary|secondary|keywords.';

-- ---------------------------------------------------------------------
-- 3. agent_capabilities — normaliza skills/tools/rag_collections/handoffs
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_capabilities (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id          TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  capability_type   TEXT NOT NULL CHECK (capability_type IN ('tool', 'skill', 'rag_collection', 'handoff', 'sharepoint_folder', 'mcp')),
  capability_name   TEXT NOT NULL,
  config            JSONB NOT NULL DEFAULT '{}',
  is_enabled        BOOLEAN NOT NULL DEFAULT true,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT uq_capability UNIQUE (agent_id, capability_type, capability_name)
);

COMMENT ON TABLE agent_capabilities IS
  'Ferramentas, skills, coleções RAG, handoffs e pastas SharePoint de cada agente. '
  'config JSONB carrega detalhes por linha (ex. segment_code, file_patterns, storage_prefix).';

-- ---------------------------------------------------------------------
-- 4. agent_health — telemetria em série temporal (usada por
--    infra/agent-registry/ab-test-service.js para decidir promoção/rollback)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_health (
  id                BIGSERIAL PRIMARY KEY,
  agent_id          TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  status            TEXT DEFAULT 'healthy' CHECK (status IN ('healthy', 'degraded', 'down')),
  queue_depth       INT DEFAULT 0,
  avg_latency_ms    FLOAT,
  error_rate_24h    FLOAT,
  success_count     INT DEFAULT 0,
  error_count       INT DEFAULT 0,
  recorded_at       TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE agent_health ADD COLUMN IF NOT EXISTS p99_latency_ms FLOAT;
ALTER TABLE agent_health ADD COLUMN IF NOT EXISTS last_error     TEXT;

COMMENT ON TABLE agent_health IS
  'Série temporal de métricas de execução por agente (múltiplas linhas por agente ao '
  'longo do tempo). Consumida por ab-test-service.js (ORDER BY recorded_at DESC LIMIT 20) '
  'para decidir promoção/rollback do A-B test. NÃO confundir com agent_heartbeats (estado '
  'atual/liveness) — ver nota de conflito no topo do arquivo.';

-- ---------------------------------------------------------------------
-- 5. agent_heartbeats — estado atual (liveness) por agente
-- ---------------------------------------------------------------------
-- Formato exigido por services/heartbeat/heartbeat-service.js (upsert
-- via ON CONFLICT (agent_id)). Nome distinto de `agent_health` de
-- propósito — ver nota de conflito no topo do arquivo.

CREATE TABLE IF NOT EXISTS agent_heartbeats (
  agent_id            TEXT PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
  status              TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'unhealthy')),
  queue_depth         INTEGER NOT NULL DEFAULT 0,
  error_rate_5m       NUMERIC NOT NULL DEFAULT 0 CHECK (error_rate_5m >= 0 AND error_rate_5m <= 1),
  last_heartbeat_at   TIMESTAMPTZ NOT NULL,
  unhealthy_since     TIMESTAMPTZ,
  routable            BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE agent_heartbeats IS
  'Última posição conhecida de cada agente (~5 min), usada pelo Maestro antes de rotear '
  '(routable=TRUE). Equivalente ao agent_health de 2026_08_02_agent_health_heartbeat.sql, '
  'renomeado para não colidir com o agent_health de série temporal já em uso pelo A-B test.';

-- ---------------------------------------------------------------------
-- 6. routing_events — telemetria de decisões de routing do Maestro
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS routing_events (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  query                 TEXT NOT NULL,
  query_hash            TEXT NOT NULL,             -- sha256(query), para dedup/analytics sem PII em claro
  query_embedding       vector(384),
  lifecycle_phase       SMALLINT CHECK (lifecycle_phase BETWEEN 1 AND 8),  -- fase do Eixo 3 (Q2 intake)

  top_candidates        JSONB NOT NULL DEFAULT '[]', -- [{agent_id, score, segment_code}, ...]
  chosen_agent_id       TEXT REFERENCES agents(id),
  chosen_confidence      NUMERIC(5,4) CHECK (chosen_confidence BETWEEN 0 AND 1),

  is_composed           BOOLEAN NOT NULL DEFAULT false,
  composed_agents       TEXT[] NOT NULL DEFAULT '{}',
  composition_strategy  TEXT CHECK (composition_strategy IS NULL OR composition_strategy IN ('serial', 'parallel')),

  outcome               TEXT NOT NULL DEFAULT 'pending' CHECK (outcome IN ('success', 'fallback', 'error', 'pending')),
  outcome_agent_id      TEXT REFERENCES agents(id),

  latency_ms            INT,
  tokens_used            INT,

  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE routing_events IS
  'Uma linha por decisão de routing do Maestro (Manta 00): candidatos, escolha, confiança, '
  'composição multi-agente e resultado. Base para o dashboard de analytics (P99 latency, '
  'success rate, fallback %) e para o feedback loop bayesiano (feedback_loop.py).';

-- ---------------------------------------------------------------------
-- 7. routing_feedback — feedback humano sobre decisões de routing
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS routing_feedback (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  routing_event_id   UUID REFERENCES routing_events(id) ON DELETE SET NULL,
  agent_id           TEXT REFERENCES agents(id),
  query_hash         TEXT,

  feedback           TEXT NOT NULL CHECK (feedback IN ('correct', 'wrong', 'slow', 'incomplete', 'excellent')),
  rating             SMALLINT CHECK (rating BETWEEN 1 AND 5),
  comment            TEXT,
  user_email         TEXT,

  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE routing_feedback IS
  'Feedback humano (thumbs up/down / comentário) sobre uma decisão registrada em '
  'routing_events. Alimenta o feedback loop bayesiano (β-binomial) e QUARTERLY-REVIEW.';

-- ---------------------------------------------------------------------
-- 8. Suporte: versionamento e metadata do registry
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_registry_history (
  id            BIGSERIAL PRIMARY KEY,
  agent_id      TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  snapshot      JSONB NOT NULL,     -- linha anterior (sem updated_at/embedding, ver trigger)
  changed_by    TEXT,               -- role/usuário que fez o UPDATE, quando disponível
  changed_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE agent_registry_history IS
  'Auditoria/versionamento: snapshot da linha ANTERIOR de agents a cada UPDATE que altere '
  'campos de identidade/registro (ver trigger fn_agents_audit).';

CREATE TABLE IF NOT EXISTS agent_registry_meta (
  id               BOOLEAN PRIMARY KEY DEFAULT true CHECK (id),  -- singleton
  registry_version TEXT NOT NULL,
  source_document  TEXT,
  ticket           TEXT,
  released_at      DATE,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE agent_registry_meta IS
  'Versão vigente do registry (espelha o cabeçalho do CLAUDE.md master, ex. v4.2).';

COMMIT;

-- =====================================================================
-- 9. Índices otimizados (HNSW, GIN, BRIN, parciais)
-- =====================================================================
-- Fora da transação principal por clareza; CREATE INDEX aqui não usa
-- CONCURRENTLY porque as tabelas acabaram de ser criadas (sem lock
-- contention real em produção nova). Se aplicar contra uma tabela já
-- populada e concorrida, recriar estes blocos com CREATE INDEX
-- CONCURRENTLY fora de uma transação BEGIN/COMMIT.

BEGIN;

-- agents ---------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_agents_expertise        ON agents USING GIN (expertise_primary);
CREATE INDEX IF NOT EXISTS idx_agents_lifecycle        ON agents (lifecycle);
CREATE INDEX IF NOT EXISTS idx_agents_promotion        ON agents (promotion_status, ab_test_ends_at);
CREATE INDEX IF NOT EXISTS idx_agents_aliases          ON agents USING GIN (aliases);
CREATE INDEX IF NOT EXISTS idx_agents_segment_codes    ON agents USING GIN (segment_codes);
CREATE INDEX IF NOT EXISTS idx_agents_lifecycle_phases ON agents USING GIN (lifecycle_phases_supported);
CREATE INDEX IF NOT EXISTS idx_agents_eixo             ON agents (eixo);
CREATE INDEX IF NOT EXISTS idx_agents_active           ON agents (id) WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_agents_embedding        ON agents USING hnsw (description_embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE description_embedding IS NOT NULL;

-- agent_expertise --------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_expertise_agent      ON agent_expertise (agent_id);
CREATE INDEX IF NOT EXISTS idx_expertise_segment    ON agent_expertise (segment_code);
CREATE INDEX IF NOT EXISTS idx_expertise_label      ON agent_expertise (label);
CREATE INDEX IF NOT EXISTS idx_expertise_weight     ON agent_expertise (agent_id, weight DESC);
CREATE INDEX IF NOT EXISTS idx_expertise_embedding  ON agent_expertise USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE embedding IS NOT NULL;

-- agent_capabilities -------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_capabilities_agent      ON agent_capabilities (agent_id, capability_type);
CREATE INDEX IF NOT EXISTS idx_capabilities_type_name  ON agent_capabilities (capability_type, capability_name);
CREATE INDEX IF NOT EXISTS idx_capabilities_config     ON agent_capabilities USING GIN (config jsonb_path_ops);

-- agent_health (série temporal — BRIN por ser append-only e crescer muito) --
CREATE INDEX IF NOT EXISTS idx_health_agent         ON agent_health (agent_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_health_recorded_brin ON agent_health USING BRIN (recorded_at);

-- agent_heartbeats -----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_heartbeats_status   ON agent_heartbeats (status);
CREATE INDEX IF NOT EXISTS idx_heartbeats_routable ON agent_heartbeats (agent_id) WHERE NOT routable;

-- routing_events -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_routing_events_created    ON routing_events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_events_created_brin ON routing_events USING BRIN (created_at);
CREATE INDEX IF NOT EXISTS idx_routing_events_chosen      ON routing_events (chosen_agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_events_hash        ON routing_events (query_hash);
CREATE INDEX IF NOT EXISTS idx_routing_events_composed    ON routing_events USING GIN (composed_agents);
CREATE INDEX IF NOT EXISTS idx_routing_events_candidates  ON routing_events USING GIN (top_candidates jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_routing_events_embedding   ON routing_events USING hnsw (query_embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE query_embedding IS NOT NULL;

-- routing_feedback -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_feedback_agent   ON routing_feedback (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_event   ON routing_feedback (routing_event_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type    ON routing_feedback (feedback);

-- agent_registry_history --------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_registry_history_agent ON agent_registry_history (agent_id, changed_at DESC);

COMMIT;

-- =====================================================================
-- 10. Triggers (updated_at automático + versionamento/auditoria)
-- =====================================================================

BEGIN;

CREATE OR REPLACE FUNCTION fn_touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_expertise_updated_at ON agent_expertise;
CREATE TRIGGER trg_expertise_updated_at
  BEFORE UPDATE ON agent_expertise
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

DROP TRIGGER IF EXISTS trg_capabilities_updated_at ON agent_capabilities;
CREATE TRIGGER trg_capabilities_updated_at
  BEFORE UPDATE ON agent_capabilities
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

DROP TRIGGER IF EXISTS trg_heartbeats_updated_at ON agent_heartbeats;
CREATE TRIGGER trg_heartbeats_updated_at
  BEFORE UPDATE ON agent_heartbeats
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

DROP TRIGGER IF EXISTS trg_registry_meta_updated_at ON agent_registry_meta;
CREATE TRIGGER trg_registry_meta_updated_at
  BEFORE UPDATE ON agent_registry_meta
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

-- Versionamento: grava snapshot da linha anterior de `agents` sempre
-- que um UPDATE mudar algo além de updated_at/embedding, e mantém
-- updated_at sempre corrente (substitui o touch manual que os
-- serviços já fazem hoje — inofensivo mesmo quando eles também setam
-- updated_at explicitamente no payload).
CREATE OR REPLACE FUNCTION fn_agents_audit() RETURNS TRIGGER AS $$
DECLARE
  old_snapshot JSONB := to_jsonb(OLD) - 'updated_at' - 'description_embedding';
  new_snapshot JSONB := to_jsonb(NEW) - 'updated_at' - 'description_embedding';
BEGIN
  IF old_snapshot IS DISTINCT FROM new_snapshot THEN
    INSERT INTO agent_registry_history (agent_id, snapshot, changed_by)
    VALUES (OLD.id, old_snapshot, current_setting('request.jwt.claim.role', true));
  END IF;
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agents_audit ON agents;
CREATE TRIGGER trg_agents_audit
  BEFORE UPDATE ON agents
  FOR EACH ROW EXECUTE FUNCTION fn_agents_audit();

COMMIT;

-- =====================================================================
-- 11. Views e função de busca semântica (conveniência para o Maestro)
-- =====================================================================

BEGIN;

CREATE OR REPLACE VIEW v_agent_routing_keywords AS
SELECT
  e.agent_id,
  a.name              AS agent_name,
  a.lifecycle,
  a.is_active,
  e.segment_code,
  e.expertise_type,
  e.label,
  e.weight
FROM agent_expertise e
JOIN agents a ON a.id = e.agent_id
WHERE a.is_active
ORDER BY e.weight DESC;

COMMENT ON VIEW v_agent_routing_keywords IS
  'Keywords de routing ativas, join-adas com o agente, ordenadas por peso — '
  'consumo direto pelo Maestro (Manta 00) na etapa de triagem (Q1).';

CREATE OR REPLACE VIEW v_agent_health_latest AS
SELECT DISTINCT ON (agent_id)
  agent_id, status, queue_depth, avg_latency_ms, p99_latency_ms,
  error_rate_24h, success_count, error_count, last_error, recorded_at
FROM agent_health
ORDER BY agent_id, recorded_at DESC;

COMMENT ON VIEW v_agent_health_latest IS
  'Última amostra de telemetria (agent_health) por agente — complementa '
  'agent_heartbeats (liveness em tempo real) com as métricas de performance mais recentes.';

CREATE OR REPLACE FUNCTION fn_search_agents_by_embedding(
  query_embedding vector(384),
  match_count     INT DEFAULT 5,
  only_active     BOOLEAN DEFAULT true
) RETURNS TABLE (
  agent_id    TEXT,
  agent_name  TEXT,
  similarity  FLOAT,
  lifecycle   TEXT
) LANGUAGE sql STABLE AS $$
  SELECT
    a.id,
    a.name,
    1 - (a.description_embedding <=> query_embedding) AS similarity,
    a.lifecycle
  FROM agents a
  WHERE a.description_embedding IS NOT NULL
    AND (NOT only_active OR a.is_active)
  ORDER BY a.description_embedding <=> query_embedding
  LIMIT match_count;
$$;

COMMENT ON FUNCTION fn_search_agents_by_embedding IS
  'RPC de conveniência (supabase.rpc) para ranking semântico de agentes por '
  'similaridade de cosseno contra description_embedding (HNSW).';

COMMIT;

-- =====================================================================
-- 12. Row Level Security
-- =====================================================================
-- Todos os serviços hoje (infra/agent-registry/*, services/heartbeat/*)
-- usam SUPABASE_SERVICE_ROLE_KEY exclusivamente (bypassa RLS por
-- padrão) — ver infra/agent-registry/lib/supabase-client.js. Portanto é
-- seguro travar anon/authenticated aqui sem quebrar nada em produção.

BEGIN;

ALTER TABLE agents                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_expertise         ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_capabilities      ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_health            ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_heartbeats        ENABLE ROW LEVEL SECURITY;
ALTER TABLE routing_events          ENABLE ROW LEVEL SECURITY;
ALTER TABLE routing_feedback        ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_registry_history  ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_registry_meta     ENABLE ROW LEVEL SECURITY;

-- Leitura para usuários autenticados (ex. dashboard interno da Manta).
-- routing_events fica de fora de propósito (pode conter texto de query
-- sensível) — só service_role (bypassa RLS) lê essa tabela.
--
-- Os papéis `authenticated`/`anon`/`service_role` só existem em um
-- projeto Supabase de verdade (não em um Postgres genérico de dev/CI).
-- O bloco abaixo checa pg_roles antes de criar cada policy para que
-- esta migração rode sem erro em qualquer ambiente; em Supabase real
-- as policies são criadas normalmente.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
    BEGIN
      CREATE POLICY p_agents_select_authenticated ON agents
        FOR SELECT TO authenticated USING (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;

    BEGIN
      CREATE POLICY p_expertise_select_authenticated ON agent_expertise
        FOR SELECT TO authenticated USING (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;

    BEGIN
      CREATE POLICY p_capabilities_select_authenticated ON agent_capabilities
        FOR SELECT TO authenticated USING (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;

    BEGIN
      CREATE POLICY p_health_select_authenticated ON agent_health
        FOR SELECT TO authenticated USING (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;

    BEGIN
      CREATE POLICY p_heartbeats_select_authenticated ON agent_heartbeats
        FOR SELECT TO authenticated USING (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;

    -- Staff autenticado pode registrar feedback de routing (não pode ler
    -- o histórico de terceiros nem editar/apagar — só INSERT).
    BEGIN
      CREATE POLICY p_feedback_insert_authenticated ON routing_feedback
        FOR INSERT TO authenticated WITH CHECK (true);
    EXCEPTION WHEN duplicate_object THEN NULL; END;
  ELSE
    RAISE NOTICE 'Papel "authenticated" não existe neste banco (não é um projeto Supabase) — policies de leitura não criadas. agents/agent_expertise/agent_capabilities/agent_health/agent_heartbeats/routing_feedback ficam com RLS habilitado e SEM policy, ou seja, só o dono da tabela / roles com BYPASSRLS conseguem acessar até que as policies sejam criadas manualmente.';
  END IF;
END $$;

COMMIT;

-- =====================================================================
-- 13. Seed data — os 20/17 agentes v4.2 existentes (CLAUDE.md)
-- =====================================================================
-- Nota de contagem: o CLAUDE.md master fala em "20 agentes, 3 eixos".
-- O MAPA COMPLETO lista 11 linhas horizontais + 10 linhas verticais
-- (S1-S10) = 21 linhas de ROUTING, mas S5 (Túneis) é explicitamente
-- "⚡ Parcial (coberto por S2/S4)" — não é uma implementação própria.
-- Removendo S5 da contagem de agentes distintos: 11 + 9 (S1-S4 e
-- S6-S10) = 20, batendo com o cabeçalho do CLAUDE.md. Como TABELA
-- `agents` (grão = implementação), agente-infraestrutura aparece UMA
-- vez cobrindo S1-S5 (17 linhas no total). O detalhamento por
-- segmento (S1..S5 com seus próprios keywords/pastas SP) vive em
-- agent_expertise e agent_capabilities, preservando a granularidade de
-- routing sem duplicar a linha do agente.
--
-- lifecycle: 'prod' para os 12 agentes já "✅ Operacional" no CLAUDE.md;
-- 'beta' para os 5 novos S6-S10, que o próprio CLAUDE.md marca como
-- "🆕 Criado 2026-07-05" (não "✅ Operacional") e cujo DEPLOY CHECKLIST
-- v4.2 ainda tem a maioria dos itens pendentes (RAG, SharePoint, testes
-- de routing, gate humano MN).
--
-- promotion_status='promoted' / traffic_percentage=100 em todas as 17:
-- este seed é um backfill retroativo do registry v4.1/v4.2 que já
-- roteia 100% do tráfego hoje (antes da pipeline de auto-registration/
-- A-B test existir) — não confundir com um agente NOVO entrando pela
-- pipeline automática (que começa em lifecycle='alpha', traffic=0).
--
-- ON CONFLICT: atualiza apenas metadados descritivos/registry; nunca
-- sobrescreve estado de rollout (promotion_status, traffic_percentage,
-- ab_test_*, promoted_at, registered_at, source_path, source_commit)
-- caso a linha já exista (ex. já processada pela auto-registration
-- pipeline) — evita a migração "regredir" um agente em produção.

BEGIN;

INSERT INTO agents (
  id, name, description, aliases, display_code, eixo, segment_codes, segment_names,
  model, escalation_model, tier, lifecycle, status_label, status_note,
  registry_version, is_active, tools, rag_collections
) VALUES
  -- ---- Eixo 1 — Horizontais -----------------------------------------
  ('maestro', 'maestro (router)',
   'Manta 00 — Router/orquestrador. Faz a triagem inicial (Q1) e despacha para o agente vertical ou horizontal correto; escala de Haiku para Sonnet conforme complexidade.',
   ARRAY['maestro','manta-router'], 'Manta 00', 1, '{}', '{}',
   'haiku', 'sonnet', 3, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('claims', 'claims',
   'Manta 01 — Especialista em claims/reequilíbrio econômico-financeiro de contratos de infraestrutura.',
   ARRAY['02-C','manta-claims'], 'Manta 01', 1, '{}', '{}',
   'opus', NULL, 1, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('contratual', 'contratual',
   'Manta 02 — Especialista em análise contratual (FIDIC, licitações, aditivos).',
   ARRAY['manta-02','contratual'], 'Manta 02', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('imobiliario', 'imobiliario',
   'Manta 04 — Especialista em avaliação e desapropriação imobiliária.',
   ARRAY['manta-04'], 'Manta 04', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('orcamento', 'orcamento',
   'Manta 05 — Especialista em orçamento de obras (SICRO, SINAPI, composições).',
   ARRAY['manta-05'], 'Manta 05', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('modelagem', 'modelagem',
   'Manta 06 — Especialista em modelagem econômico-financeira de projetos de infraestrutura.',
   ARRAY['manta-06'], 'Manta 06', 1, '{}', '{}',
   'sonnet', 'opus', 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('cronograma', 'cronograma',
   'Manta 07 — Especialista em cronograma (Primavera P6, MS Project, análise de atraso).',
   ARRAY['manta-07'], 'Manta 07', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('bd', 'bd',
   'Manta 13 — Business development: prospecção, editais, radar de oportunidades.',
   ARRAY['manta-13','business-dev'], 'Manta 13', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('apresentacoes', 'apresentacoes',
   'Manta 14 — Geração de apresentações comerciais e técnicas (PPTX).',
   ARRAY['manta-14-pptx'], 'Manta 14', 1, '{}', '{}',
   'sonnet', NULL, 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('advisory', 'advisory',
   'Manta 15 — Advisory estratégico (M&A, due diligence, second opinion).',
   ARRAY['manta-15','advisory'], 'Manta 15', 1, '{}', '{}',
   'sonnet', 'opus', 2, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  ('arquiteto-ia', 'arquiteto-ia',
   'Manta 16 — Arquiteto de sistemas de IA (design de agentes, skills, pipelines Claude).',
   ARRAY['manta-15-arq'], 'Manta 16', 1, '{}', '{}',
   'opus', NULL, 1, 'prod', '✅ Operacional', NULL, 'v4.2', true, '{}', '{}'),

  -- ---- Eixo 2 — Verticais (segmentos C3) -----------------------------
  ('agente-infraestrutura', 'agente-infraestrutura',
   'Manta 03-S1..S5 — Especialista em infraestrutura de transportes: rodovias, OAE (pontes/viadutos), ferrovia, metrô e (parcialmente) túneis.',
   '{}', 'Manta 03 (S1-S5)', 2, ARRAY['S1','S2','S3','S4','S5'], ARRAY['Rodovias','OAE','Ferrovia','Metrô','Túneis'],
   'sonnet', 'opus', 2, 'prod', '✅ Operacional (S1-S4) / ⚡ Parcial (S5)',
   'S5 (Túneis) não tem implementação própria: roteia para este agente via regras de S2 (túnel rodoviário) ou S4 (túnel metroviário/NATM).',
   'v4.2', true, '{}', '{}'),

  ('agente-portos', 'agente-portos',
   'Manta 03-S6 — Especialista em projetos portuários e hidroviários.',
   '{}', 'Manta 03-S6', 2, ARRAY['S6'], ARRAY['Portos'],
   'sonnet', 'opus', 2, 'beta', '🆕 Criado 2026-07-05', NULL, 'v4.2', true,
   ARRAY['Read','Grep','Glob','Bash','WebSearch','WebFetch'], ARRAY['portos']),

  ('agente-aeroportos', 'agente-aeroportos',
   'Manta 03-S7 — Especialista em infraestrutura aeroportuária (lado ar + lado terra).',
   '{}', 'Manta 03-S7', 2, ARRAY['S7'], ARRAY['Aeroportos'],
   'sonnet', 'opus', 2, 'beta', '🆕 Criado 2026-07-05', NULL, 'v4.2', true,
   ARRAY['Read','Grep','Glob','Bash','WebSearch','WebFetch'], ARRAY['aeroportos']),

  ('agente-saneamento', 'agente-saneamento',
   'Manta 03-S8 — Especialista em saneamento básico (água, esgoto, drenagem urbana, resíduos). Prioridade AySA (Argentina).',
   '{}', 'Manta 03-S8', 2, ARRAY['S8'], ARRAY['Saneamento'],
   'sonnet', 'opus', 2, 'beta', '🆕 Criado 2026-07-05', 'PRIORIDADE AySA (projeto Argentina).', 'v4.2', true,
   ARRAY['Read','Grep','Glob','Bash','WebSearch','WebFetch'], ARRAY['saneamento']),

  ('agente-energia', 'agente-energia',
   'Manta 03-S9 — Especialista em setor elétrico (geração, transmissão, distribuição). Prioridade transmissão (ANEEL/State Grid).',
   '{}', 'Manta 03-S9', 2, ARRAY['S9'], ARRAY['Energia'],
   'sonnet', 'opus', 2, 'beta', '🆕 Criado 2026-07-05', 'ANEEL/State Grid.', 'v4.2', true,
   ARRAY['Read','Grep','Glob','Bash','WebSearch','WebFetch'], ARRAY['energia']),

  ('agente-barragens', 'agente-barragens',
   'Manta 03-S10 — Especialista em barragens (concreto, terra, enrocamento, rejeitos).',
   '{}', 'Manta 03-S10', 2, ARRAY['S10'], ARRAY['Barragens'],
   'sonnet', 'opus', 2, 'beta', '🆕 Criado 2026-07-05', NULL, 'v4.2', true,
   ARRAY['Read','Grep','Glob','Bash','WebSearch','WebFetch'], ARRAY['barragens'])

ON CONFLICT (id) DO UPDATE SET
  name                       = EXCLUDED.name,
  description                = EXCLUDED.description,
  aliases                    = EXCLUDED.aliases,
  display_code               = EXCLUDED.display_code,
  eixo                       = EXCLUDED.eixo,
  segment_codes              = EXCLUDED.segment_codes,
  segment_names              = EXCLUDED.segment_names,
  model                      = EXCLUDED.model,
  escalation_model           = EXCLUDED.escalation_model,
  tier                       = EXCLUDED.tier,
  status_label               = EXCLUDED.status_label,
  status_note                = EXCLUDED.status_note,
  registry_version           = EXCLUDED.registry_version,
  is_active                  = EXCLUDED.is_active,
  tools                      = CASE WHEN array_length(EXCLUDED.tools, 1) > 0 THEN EXCLUDED.tools ELSE agents.tools END,
  rag_collections            = CASE WHEN array_length(EXCLUDED.rag_collections, 1) > 0 THEN EXCLUDED.rag_collections ELSE agents.rag_collections END;
  -- (lifecycle e todo o bloco de promotion/traffic/ab_test/source_* NÃO
  -- entram no SET acima — ver nota "ON CONFLICT" no cabeçalho da seção)

-- lifecycle e rollout apenas no INSERT inicial (ON CONFLICT não toca
-- nestes campos); força o valor correto quando a linha é criada agora.
UPDATE agents SET
  lifecycle = CASE id
    WHEN 'agente-portos' THEN 'beta'
    WHEN 'agente-aeroportos' THEN 'beta'
    WHEN 'agente-saneamento' THEN 'beta'
    WHEN 'agente-energia' THEN 'beta'
    WHEN 'agente-barragens' THEN 'beta'
    ELSE 'prod'
  END,
  promotion_status = 'promoted',
  traffic_percentage = 100,
  promoted_at = COALESCE(promoted_at, CASE
    WHEN id IN ('agente-portos','agente-aeroportos','agente-saneamento','agente-energia','agente-barragens')
      THEN '2026-07-05'::TIMESTAMPTZ
    ELSE NULL
  END)
WHERE id IN (
  'maestro','claims','contratual','imobiliario','orcamento','modelagem','cronograma',
  'bd','apresentacoes','advisory','arquiteto-ia','agente-infraestrutura',
  'agente-portos','agente-aeroportos','agente-saneamento','agente-energia','agente-barragens'
)
AND promotion_status = 'pending'; -- só na primeira vez; não regride estado já avançado

INSERT INTO agent_registry_meta (id, registry_version, source_document, ticket, released_at)
VALUES (true, 'v4.2', 'CLAUDE.md', 'MNT-2026-UPGRADE-AGENTS-S6S10', '2026-07-05')
ON CONFLICT (id) DO UPDATE SET
  registry_version = EXCLUDED.registry_version,
  source_document  = EXCLUDED.source_document,
  ticket           = EXCLUDED.ticket,
  released_at      = EXCLUDED.released_at,
  updated_at       = now();

COMMIT;

-- ---------------------------------------------------------------------
-- 14. Seed — agent_expertise (keywords de routing, com pesos)
-- ---------------------------------------------------------------------
-- Fonte: seção ROUTING do CLAUDE.md master. Pesos de S6-S10 replicam
-- exatamente os já usados em maestro_routing_keywords (migração
-- 2026_07_05_v4_2_agents_s6_s10.sql) para não haver duas fontes de
-- verdade divergentes. S1-S4 não tinham peso explícito no CLAUDE.md —
-- usado peso uniforme 100. Horizontais não têm regra de routing por
-- keyword no CLAUDE.md (routing é por tipo de tarefa, não por Q1) —
-- não fabricado, propositalmente deixado sem linhas aqui.

BEGIN;

INSERT INTO agent_expertise (agent_id, segment_code, expertise_type, label, weight) VALUES
  -- S1 Rodovias
  ('agente-infraestrutura','S1','keyword','rodovia',100),
  ('agente-infraestrutura','S1','keyword','pavimento',100),
  ('agente-infraestrutura','S1','keyword','CBUQ',100),
  ('agente-infraestrutura','S1','keyword','BGS',100),
  ('agente-infraestrutura','S1','keyword','terraplenagem',100),
  ('agente-infraestrutura','S1','keyword','SICRO',100),
  ('agente-infraestrutura','S1','keyword','DNIT',100),
  -- S2 OAE
  ('agente-infraestrutura','S2','keyword','ponte',100),
  ('agente-infraestrutura','S2','keyword','viaduto',100),
  ('agente-infraestrutura','S2','keyword','OAE',100),
  ('agente-infraestrutura','S2','keyword','NBR 7187',100),
  ('agente-infraestrutura','S2','keyword','túnel rodoviário',100),
  -- S3 Ferrovia
  ('agente-infraestrutura','S3','keyword','ferrovia',100),
  ('agente-infraestrutura','S3','keyword','trilho',100),
  ('agente-infraestrutura','S3','keyword','AMV',100),
  ('agente-infraestrutura','S3','keyword','dormente',100),
  ('agente-infraestrutura','S3','keyword','via permanente',100),
  -- S4 Metrô
  ('agente-infraestrutura','S4','keyword','metrô',100),
  ('agente-infraestrutura','S4','keyword','estação',100),
  ('agente-infraestrutura','S4','keyword','NATM',100),
  ('agente-infraestrutura','S4','keyword','PSD',100),
  ('agente-infraestrutura','S4','keyword','linha 4',100),
  ('agente-infraestrutura','S4','keyword','linha 5',100),
  ('agente-infraestrutura','S4','keyword','VLT',100),
  -- S6 Portos (pesos = maestro_routing_keywords existente)
  ('agente-portos','S6','keyword','porto',80),
  ('agente-portos','S6','keyword','terminal',70),
  ('agente-portos','S6','keyword','ANTAQ',100),
  ('agente-portos','S6','keyword','dragagem',100),
  ('agente-portos','S6','keyword','molhe',100),
  ('agente-portos','S6','keyword','berço',90),
  ('agente-portos','S6','keyword','calado',90),
  ('agente-portos','S6','keyword','contêiner',80),
  ('agente-portos','S6','keyword','granel',80),
  -- S7 Aeroportos
  ('agente-aeroportos','S7','keyword','aeroporto',100),
  ('agente-aeroportos','S7','keyword','pista pouso',100),
  ('agente-aeroportos','S7','keyword','ANAC',100),
  ('agente-aeroportos','S7','keyword','ICAO',100),
  ('agente-aeroportos','S7','keyword','TPS',90),
  ('agente-aeroportos','S7','keyword','TECA',90),
  ('agente-aeroportos','S7','keyword','balizamento',100),
  -- S8 Saneamento
  ('agente-saneamento','S8','keyword','saneamento',100),
  ('agente-saneamento','S8','keyword','ETA',100),
  ('agente-saneamento','S8','keyword','ETE',100),
  ('agente-saneamento','S8','keyword','adutora',100),
  ('agente-saneamento','S8','keyword','esgoto',100),
  ('agente-saneamento','S8','keyword','AySA',120),
  ('agente-saneamento','S8','keyword','drenagem urbana',95),
  ('agente-saneamento','S8','keyword','SNIS',100),
  -- S9 Energia
  ('agente-energia','S9','keyword','transmissão',100),
  ('agente-energia','S9','keyword','LT',90),
  ('agente-energia','S9','keyword','subestação',100),
  ('agente-energia','S9','keyword','ANEEL',100),
  ('agente-energia','S9','keyword','RAP',90),
  ('agente-energia','S9','keyword','leilão transmissão',95),
  ('agente-energia','S9','keyword','ONS',90),
  ('agente-energia','S9','keyword','EPE',90),
  -- S10 Barragens
  ('agente-barragens','S10','keyword','barragem',100),
  ('agente-barragens','S10','keyword','vertedouro',100),
  ('agente-barragens','S10','keyword','CFRD',100),
  ('agente-barragens','S10','keyword','CCR',80),
  ('agente-barragens','S10','keyword','rejeitos',110),
  ('agente-barragens','S10','keyword','PNSB',100),
  ('agente-barragens','S10','keyword','ICOLD',100),
  ('agente-barragens','S10','keyword','CBDB',100),
  ('agente-barragens','S10','keyword','TSF',100)
ON CONFLICT (agent_id, segment_code, expertise_type, label) DO UPDATE SET weight = EXCLUDED.weight;

COMMIT;

-- ---------------------------------------------------------------------
-- 15. Seed — agent_capabilities (tools, RAG, SharePoint, handoff, skill)
-- ---------------------------------------------------------------------
-- Apenas capacidades com fonte explícita nos documentos do repositório
-- (frontmatter dos 5 agentes .claude/agents/*.md, migração
-- 2026_07_05_v4_2_agents_s6_s10.sql e ARQUITETURA-AGENTES-IA.md) — sem
-- inventar mapeamentos skill↔agente que não estão documentados.

BEGIN;

-- Tools confirmadas no frontmatter dos 5 novos agentes verticais
INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, config)
SELECT agent_id, 'tool', tool_name, '{}'::JSONB
FROM (VALUES
  ('agente-portos'), ('agente-aeroportos'), ('agente-saneamento'),
  ('agente-energia'), ('agente-barragens')
) AS a(agent_id)
CROSS JOIN (VALUES ('Read'), ('Grep'), ('Glob'), ('Bash'), ('WebSearch'), ('WebFetch')) AS t(tool_name)
ON CONFLICT (agent_id, capability_type, capability_name) DO NOTHING;

-- Coleções RAG (prefixo + fontes iniciais — migração 2026_07_05)
INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, config) VALUES
  ('agente-saneamento', 'rag_collection', 'saneamento', '{"storage_prefix":"san:","initial_sources":["SNIS","IWA","NBR 12211-12218","Lei 14.026","editais BNDES"]}'),
  ('agente-energia',    'rag_collection', 'energia',    '{"storage_prefix":"ene:","initial_sources":["ANEEL editais","R1-R5 EPE","ONS","IEEE"]}'),
  ('agente-portos',     'rag_collection', 'portos',     '{"storage_prefix":"por:","initial_sources":["ANTAQ","PIANC","editais BNDES/ANTAQ"]}'),
  ('agente-aeroportos', 'rag_collection', 'aeroportos', '{"storage_prefix":"aer:","initial_sources":["ANAC/RBAC","ICAO Annex 14","FAA ACs"]}'),
  ('agente-barragens',  'rag_collection', 'barragens',  '{"storage_prefix":"bar:","initial_sources":["ICOLD","CBDB","SIGBM","Lei 12.334"]}')
ON CONFLICT (agent_id, capability_type, capability_name) DO UPDATE SET config = EXCLUDED.config;

-- Pastas SharePoint sugeridas (CLAUDE.md + ARQUITETURA-AGENTES-IA.md)
INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, config) VALUES
  ('agente-infraestrutura', 'sharepoint_folder', '03_Projetos/Rodovias/*',    '{"segment_code":"S1","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-infraestrutura', 'sharepoint_folder', '03_Projetos/OAE/*',         '{"segment_code":"S2","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-infraestrutura', 'sharepoint_folder', '03_Projetos/Ferrovia/*',    '{"segment_code":"S3","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-infraestrutura', 'sharepoint_folder', '03_Projetos/Metro/*',       '{"segment_code":"S4","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-saneamento',     'sharepoint_folder', '03_Projetos/Saneamento/*',  '{"segment_code":"S8","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-energia',        'sharepoint_folder', '03_Projetos/Energia/*',    '{"segment_code":"S9","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-portos',         'sharepoint_folder', '03_Projetos/Portos/*',      '{"segment_code":"S6","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-aeroportos',     'sharepoint_folder', '03_Projetos/Aeroportos/*', '{"segment_code":"S7","file_patterns":["*.pdf","*.dwg","*.xlsx"]}'),
  ('agente-barragens',      'sharepoint_folder', '03_Projetos/Barragens/*',  '{"segment_code":"S10","file_patterns":["*.pdf","*.dwg","*.xlsx"]}')
ON CONFLICT (agent_id, capability_type, capability_name) DO NOTHING;

-- Handoff: maestro roteia para todos os demais 16 agentes do registry
INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, config)
SELECT 'maestro', 'handoff', id, '{}'::JSONB
FROM agents WHERE id <> 'maestro'
ON CONFLICT (agent_id, capability_type, capability_name) DO NOTHING;

-- Skills com mapeamento explícito na descrição/skill catalog
INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, config) VALUES
  ('agente-energia',        'skill', 'ler-edital-aneel',   '{"note":"editais ANEEL de transmissão + anexos técnicos + R1-R5"}'),
  ('agente-infraestrutura', 'skill', 'autodesk-toolkit',   '{"note":"camada CAD/BIM compartilhada — Rodovias/OAE/Ferrovia/Metrô"}'),
  ('imobiliario',           'skill', 'autodesk-toolkit',   '{"note":"camada CAD/BIM compartilhada — Imobiliário"}')
ON CONFLICT (agent_id, capability_type, capability_name) DO NOTHING;

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP FUNCTION IF EXISTS fn_search_agents_by_embedding(vector, INT, BOOLEAN);
-- DROP VIEW IF EXISTS v_agent_health_latest;
-- DROP VIEW IF EXISTS v_agent_routing_keywords;
--
-- DROP TRIGGER IF EXISTS trg_agents_audit ON agents;
-- DROP FUNCTION IF EXISTS fn_agents_audit();
-- DROP TRIGGER IF EXISTS trg_registry_meta_updated_at ON agent_registry_meta;
-- DROP TRIGGER IF EXISTS trg_heartbeats_updated_at ON agent_heartbeats;
-- DROP TRIGGER IF EXISTS trg_capabilities_updated_at ON agent_capabilities;
-- DROP TRIGGER IF EXISTS trg_expertise_updated_at ON agent_expertise;
-- DROP FUNCTION IF EXISTS fn_touch_updated_at();
--
-- DROP TABLE IF EXISTS agent_registry_meta;
-- DROP TABLE IF EXISTS agent_registry_history;
-- DROP TABLE IF EXISTS routing_feedback;
-- DROP TABLE IF EXISTS routing_events;
-- DROP TABLE IF EXISTS agent_heartbeats;
-- DROP TABLE IF EXISTS agent_capabilities;
-- DROP TABLE IF EXISTS agent_expertise;
--
-- -- agent_health e agents são compartilhados com as migrações de
-- -- 2026-08-02 — NÃO dropar aqui (dropar lá se for o caso). Este bloco
-- -- só reverte as colunas/constraints que ESTA migração adicionou:
-- ALTER TABLE agents
--   DROP COLUMN IF EXISTS is_active,
--   DROP COLUMN IF EXISTS registry_version,
--   DROP COLUMN IF EXISTS description_embedding,
--   DROP COLUMN IF EXISTS lifecycle_phases_supported,
--   DROP COLUMN IF EXISTS status_note,
--   DROP COLUMN IF EXISTS status_label,
--   DROP COLUMN IF EXISTS escalation_model,
--   DROP COLUMN IF EXISTS segment_names,
--   DROP COLUMN IF EXISTS segment_codes,
--   DROP COLUMN IF EXISTS eixo,
--   DROP COLUMN IF EXISTS display_code,
--   DROP COLUMN IF EXISTS aliases;
-- ALTER TABLE agent_health
--   DROP COLUMN IF EXISTS last_error,
--   DROP COLUMN IF EXISTS p99_latency_ms;
--
-- COMMIT;
