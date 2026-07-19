# v4.9 Judge Feedback Loop — Adapted Runbook

**Status:** Decision brief + apply plan. Supersedes the original v4.9 SQL for the
prod-schema reality. Gate humano MN antes de aplicar em prod.
**Owner:** MN. **Date:** 2026-07-19.
**Artifact SQL:** `supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql`

---

## 1. Context

The original v4.9 migration (`docs/JUDGE-FEEDBACK-LOOP-v4.9.md`) is **blocked**:
it assumes the v4.6 llm-judge migration (`agent_response_flags`, `agent_query_log`)
was applied in prod — it was not. Recon (workflow 16 agentes, 2026-07-19)
confirms:

- Prod uses `public.manta_rag_queries` directly with judge columns inline:
  `query_id` (bigint PK), `timestamp`, `tipo`, `query_text`, `filtros` (jsonb),
  `hits_count`, `trace_id`, `judge_score` (smallint), `judge_scored_at`,
  `judge_model`, `judge_notes` (jsonb).
- `agent_response_flags` NÃO existe.
- `agent_query_log` NÃO existe (renamed a manta_rag_queries).
- `v_akp_gap_candidates` NÃO existe (obsoleta na v4.5 quando `promote_gaps_to_backlog`
  passou a ler manta_rag_queries diretamente).
- `promote_gaps_to_backlog(INTEGER)` já existe e lê manta_rag_queries direto.

Running the original SQL would fail on missing tables and break the working
judge path already in prod.

## 2. Recommended adaptation — **D1' (D1 com todos os patches do verdict)**

The 16-agent workflow refuted the initial D1 draft on **three concrete points**
(schema assumption, MAX+1 race, backward-compat break of `promote_gaps_to_backlog`).
The synth-migration-sql agent addressed **all three**:

- **Schema assumption →** DO $$ pre-flight guard (linhas 49-82 do SQL) que
  `RAISE EXCEPTION` se qualquer coluna requerida em manta_rag_queries estiver
  ausente. Aborta cedo, sem estragar nada.
- **MAX+1 race →** três `SEQUENCE`s dedicadas (`akp_judge_flag_seq`,
  `akp_judge_pattern_seq`, `akp_gap_candidate_seq`) com `setval()` alinhado ao
  MAX(ticket_id) existente para idempotência em reruns e compat com backlog v4.5.
  Nunca usa MAX+1.
- **Backward-compat →** `DROP FUNCTION` explícito das 4 variantes possíveis
  antes de recriar `promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER)`. O cron
  daily continua funcionando (é executado sem args nomeados, os defaults
  cobrem o call site atual).

Além disso, o synth folded in dois extras que estavam no verdict D4:

- **Idempotência de judge_flag →** `UNIQUE INDEX` parcial em
  `(evidence->>'query_id')` WHERE `ticket_type='judge_flag'`. Garante 1 ticket
  por query mesmo sob concorrência de INSERT+UPDATE simultâneos.
- **Idempotência de judge_pattern →** `UNIQUE INDEX` parcial em
  `(COALESCE(agent_slug,'unknown-agent'), segmento)` WHERE
  `ticket_type='judge_pattern' AND status NOT IN ('closed','rejected')`.
  Garante 1 agregado aberto por par (agente, segmento).

Design contemplado e descartado:

- **D2 (restore `v_akp_gap_candidates`)** — CONFIRMED skip. View sem consumer.
- **D3 (v4.6 learned router)** — SKIP: `manta_learned_router.py` grava direto em
  `manta_rag_ml_predictions` (que já existe em prod como store genérica). Não
  precisa restaurar `maestro_routing_predictions` para v4.9 funcionar.
- **D4 (batch-only minimal)** — não escolhido: perde real-time flagging,
  ganhando apenas 3 objetos a menos no rollback. Como o synth-migration-sql
  já resolveu as 3 objeções do verdict D1, D1' fica com features mais completas
  ao mesmo custo operacional.

## 3. O que o migration entrega (5 seções)

### 3.1 Section 1 — Backlog estendido

`ALTER TABLE public.akp_curation_backlog ADD COLUMN IF NOT EXISTS`:

| Coluna       | Tipo     | Default            | Racional                                                  |
|--------------|----------|--------------------|-----------------------------------------------------------|
| `ticket_type`| TEXT     | `'gap_candidate'`  | Discrimina 3 tipos: gap_candidate, judge_flag, judge_pattern |
| `agent_slug` | TEXT     | NULL               | Agente Manta (derivado de `filtros->>'filter_agente'`)    |
| `evidence`   | JSONB    | `'{}'`             | Payload livre (query_id, trace_id, notes, thresholds…)    |
| `priority`   | SMALLINT | 3                  | 1 crítico → 5 baixo. Escala com judge_score               |

CHECK constraints (`NOT VALID` + `VALIDATE` para não fazer full scan em backlog
grande):

- `ticket_type IN ('gap_candidate','judge_flag','judge_pattern')`
- `priority BETWEEN 1 AND 5`
- `status IN ('triage','open','in_review','accepted','rejected','in_curation','ke_created','closed')`
  (reconstrói o CHECK anterior para incluir open/in_review v4.9)

Índices:

- `uq_akp_backlog_judge_flag_query` UNIQUE `(evidence->>'query_id')` WHERE
  ticket_type='judge_flag' — idempotência
- `uq_akp_backlog_judge_pattern_open` UNIQUE
  `(COALESCE(agent_slug,'unknown-agent'), segmento)` WHERE
  ticket_type='judge_pattern' AND status NOT IN ('closed','rejected') — dedup
- `idx_akp_backlog_ticket_type` — filtro comum
- `idx_akp_backlog_agent` — filtro por agente
- `idx_akp_backlog_status_priority` — triage queries

### 3.2 Section 2 — Trigger real-time

`judge_flag_to_backlog()` PLPGSQL SECURITY DEFINER + `SET search_path = public,
extensions` (regra Supabase). Trigger:

```sql
CREATE TRIGGER trg_judge_flag_to_backlog
  AFTER INSERT OR UPDATE OF judge_score ON public.manta_rag_queries
  FOR EACH ROW
  WHEN (
    NEW.judge_score IS NOT NULL
    AND NEW.judge_score < 3
    AND (TG_OP = 'INSERT' OR OLD.judge_score IS DISTINCT FROM NEW.judge_score)
  )
  EXECUTE FUNCTION public.judge_flag_to_backlog();
```

Coverage:
- INSERT com judge_score < 3 (batch judge, replay)
- UPDATE OF judge_score (caminho normal: juiz roda depois da query)

Cobertura de corrida:
- Short-circuit `EXISTS(...)` antes de INSERT
- `EXCEPTION WHEN unique_violation` no dedup (uq_akp_backlog_judge_flag_query),
  silencia apenas essa colisão específica

### 3.3 Section 3 — `promote_gaps_to_backlog()` estendido

Nova assinatura:
```sql
promote_gaps_to_backlog(
  min_occurrences INTEGER DEFAULT 3,
  max_avg_hits    FLOAT   DEFAULT 3.0,
  min_judge_flags INTEGER DEFAULT 3
) RETURNS TABLE (ticket_id_out TEXT, action_out TEXT, ticket_type_out TEXT,
                 segmento_out TEXT, query_out TEXT)
```

Duas partes:
1. **gap_candidate** (v4.5 preservada) — ≥ min_occurrences buscas/30d por
   (segmento, query_text) com AVG(hits_count) < max_avg_hits.
2. **judge_pattern** (novo) — agrega ≥ min_judge_flags respostas judge_score<3
   em 30d por (agent_slug, segmento) em UM ticket. Preserva o insight de padrão
   crônico separado dos judge_flag individuais.

Both partes leem `manta_rag_queries` diretamente. Cron atual (08:00 UTC daily)
continua funcionando sem alteração no GH Action.

### 3.4 Section 4 — View `v_judge_feedback_health`

`WITH (security_invoker = true)` — a view respeita a RLS da tabela base.
Agrega 30d por (agent_slug, segmento):
- `n_queries_30d` (total), `n_judged_30d` (com score)
- `n_low_scores` (< 3), `n_zeros`, `n_ones`, `n_twos`
- `avg_judge_score`, `min_judge_score`, `p50_judge_score`
- `low_score_pct` = 100 * n_low_scores / NULLIF(n_judged_30d, 0)
- `avg_hits_when_low` — se agente tem baixo score, também está tendo poucos hits?
- `judge_models_used` (jsonb array)
- `health_status`: `critical` (low_pct ≥ 30 OR n_zeros ≥ 3), `warn` (≥ 15%),
  `ok` (< 15%), `healthy` (0 low). Alimenta dashboards + Reflexion Loop +
  tier promotion (Haiku→Sonnet→Opus) + SkillForge.

### 3.5 Section 5 — RLS + GRANTs

- `ENABLE ROW LEVEL SECURITY` (idempotente via DO block).
- Policy service_role: full access via `WITH CHECK` + `USING (auth.role() =
  'service_role')`.
- GRANT SELECT em `v_judge_feedback_health` para `authenticated` (para admin UI)
  e `service_role`.

## 4. Apply steps (Supabase MCP)

```bash
# Step 1 — pre-flight (opcional, o migration mesmo aborta se falhar)
mcp__Supabase__execute_sql --query "SELECT column_name FROM information_schema.columns
  WHERE table_schema='public' AND table_name='manta_rag_queries'
    AND column_name IN ('query_id','timestamp','tipo','query_text','filtros',
                        'hits_count','judge_score','judge_scored_at','judge_model',
                        'judge_notes','trace_id')
  ORDER BY column_name;"
# Esperado: 11 linhas retornadas

# Step 2 — apply the adapted migration
mcp__Supabase__apply_migration \
  --name "2026_07_19_judge_feedback_loop_v4_9_adapted" \
  --query "$(cat supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql)"

# Step 3 — smoke test do trigger (INSERT sintético com score baixo)
mcp__Supabase__execute_sql --query "INSERT INTO public.manta_rag_queries
  (tipo, query_text, judge_score, judge_scored_at, judge_model, filtros)
  VALUES ('smoke-test','v4.9 trigger smoke test',1,NOW(),'sonnet-4-6',
          '{\"filter_agente\":\"smoke\"}'::jsonb)
  RETURNING query_id;"

mcp__Supabase__execute_sql --query "SELECT ticket_id, ticket_type, agent_slug,
  segmento, priority, evidence->>'query_id' AS qid
  FROM public.akp_curation_backlog
  WHERE ticket_type = 'judge_flag' AND agent_slug = 'smoke'
  ORDER BY id DESC LIMIT 1;"
# Esperado: 1 ticket AKP-JF-NNNNN com priority=2

# Step 4 — cleanup do smoke test
mcp__Supabase__execute_sql --query "DELETE FROM public.akp_curation_backlog
  WHERE agent_slug='smoke' AND ticket_type='judge_flag';
  DELETE FROM public.manta_rag_queries
  WHERE tipo='smoke-test';"
```

## 5. Verification queries

```sql
-- V1: 4 colunas presentes, defaults corretos
SELECT column_name, data_type, column_default, is_nullable
  FROM information_schema.columns
 WHERE table_schema='public' AND table_name='akp_curation_backlog'
   AND column_name IN ('ticket_type','agent_slug','evidence','priority')
 ORDER BY column_name;

-- V2: trigger existe e cobre INSERT+UPDATE
SELECT tgname, tgtype, pg_get_triggerdef(oid) AS def
  FROM pg_trigger
 WHERE tgname = 'trg_judge_flag_to_backlog';

-- V3: 3 sequences alinhadas
SELECT sequence_name, last_value
  FROM information_schema.sequences seq
  JOIN pg_sequences pgs ON pgs.sequencename = seq.sequence_name
 WHERE seq.sequence_schema='public'
   AND seq.sequence_name IN ('akp_judge_flag_seq','akp_judge_pattern_seq',
                             'akp_gap_candidate_seq');

-- V4: função nova reads manta_rag_queries e faz judge_pattern
SELECT pg_get_functiondef(oid)::text ILIKE '%manta_rag_queries%' AS reads_prod_table,
       pg_get_functiondef(oid)::text ILIKE '%judge_pattern%'    AS has_pattern_branch,
       pg_get_functiondef(oid)::text ILIKE '%v_akp_gap_candidates%' AS reads_deprecated_view
  FROM pg_proc
 WHERE proname='promote_gaps_to_backlog' AND pronamespace='public'::regnamespace;
-- Esperado: reads_prod_table=t, has_pattern_branch=t, reads_deprecated_view=f

-- V5: view retorna linhas (pode estar vazia se ninguém foi julgado ainda)
SELECT agent_slug, segmento, n_judged_30d, low_score_pct, health_status
  FROM public.v_judge_feedback_health
 ORDER BY n_judged_30d DESC NULLS LAST
 LIMIT 10;

-- V6: unique indexes ativos
SELECT indexname, indexdef
  FROM pg_indexes
 WHERE schemaname='public'
   AND tablename='akp_curation_backlog'
   AND indexname IN ('uq_akp_backlog_judge_flag_query',
                     'uq_akp_backlog_judge_pattern_open')
 ORDER BY indexname;
```

## 6. Rollback

```sql
BEGIN;
DROP TRIGGER IF EXISTS trg_judge_flag_to_backlog ON public.manta_rag_queries;
DROP FUNCTION IF EXISTS public.judge_flag_to_backlog();
DROP VIEW  IF EXISTS public.v_judge_feedback_health;
DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER);

-- Recria a assinatura antiga v4.5 (INTEGER) para não quebrar o cron
-- (o corpo v4.5 original vive em supabase/migrations/2026_07_12_akp_governance_v4_5.sql)
-- Se precisar, aplique aquele arquivo de novo com --idempotent.

DROP INDEX IF EXISTS public.uq_akp_backlog_judge_flag_query;
DROP INDEX IF EXISTS public.uq_akp_backlog_judge_pattern_open;
DROP INDEX IF EXISTS public.idx_akp_backlog_ticket_type;
DROP INDEX IF EXISTS public.idx_akp_backlog_agent;
DROP INDEX IF EXISTS public.idx_akp_backlog_status_priority;

ALTER TABLE public.akp_curation_backlog
  DROP CONSTRAINT IF EXISTS akp_curation_backlog_ticket_type_chk,
  DROP CONSTRAINT IF EXISTS akp_curation_backlog_priority_range,
  DROP CONSTRAINT IF EXISTS akp_curation_backlog_status_chk;

ALTER TABLE public.akp_curation_backlog
  DROP COLUMN IF EXISTS ticket_type,
  DROP COLUMN IF EXISTS agent_slug,
  DROP COLUMN IF EXISTS evidence,
  DROP COLUMN IF EXISTS priority;

DROP SEQUENCE IF EXISTS public.akp_judge_flag_seq;
DROP SEQUENCE IF EXISTS public.akp_judge_pattern_seq;
DROP SEQUENCE IF EXISTS public.akp_gap_candidate_seq;
COMMIT;
```

Rollback bounded: 1 trigger + 3 functions/views + 5 indexes + 3 constraints +
4 columns + 3 sequences. Nenhum dado migrado para outra tabela — todos os
tickets ficariam órfãos com `ticket_type=NULL` após o rollback (é o preço de
manter o backlog vivo).

## 7. Risks

- **Column-name drift on `manta_rag_queries`** — mitigado pelo pre-flight guard
  do próprio migration (linhas 49-82). Aborta cedo se qualquer coluna estiver
  ausente.
- **Race no ticket_id** — mitigado pelas 3 sequences dedicadas (nunca MAX+1).
- **Race no dedup** — mitigado pelos 2 UNIQUE INDEXes parciais + EXCEPTION
  handling silencioso.
- **Backward-compat do cron `akp-daily-cron.yml`** — o cron chama
  `promote_gaps_to_backlog()` sem args nomeados; os defaults novos (min_judge_flags=3)
  cobrem o call site. Se o cron passasse args nomeados velhos, quebraria — mas
  não passa. Validar após apply rodando o cron manualmente no GH Actions.
- **Volume de tickets** — se prod já acumulou muitas queries com judge_score<3,
  o INSERT trigger não dispara em rows pre-existentes (só INSERT novo ou UPDATE
  OF judge_score). Para promover histórico, rodar
  `SELECT promote_gaps_to_backlog(3, 3.0, 3);` uma vez após o apply — a Part 2
  do function cria os judge_pattern retroativos.

---

**Summary:** D1' (D1 with all 5 verdict patches folded in — pre-flight guard,
3 sequences, DROP old signatures, UNIQUE INDEXes parciais para dedup) é a
adaptação recomendada. Real-time via trigger + agregação via cron.
Aditivo sobre v4.5. Rollback é 1 script. D3 (learned router) SKIP porque
`manta_rag_ml_predictions` já cobre. D2 (`v_akp_gap_candidates`) SKIP porque
sem consumer. Apply via Supabase MCP em 4 steps (pre-flight → apply migration
→ smoke test trigger → cleanup). Verificação = 6 SQL queries. Gate humano
MN antes de aplicar em prod (convenção CLAUDE.md).
