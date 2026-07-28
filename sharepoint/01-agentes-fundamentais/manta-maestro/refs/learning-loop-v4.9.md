# refs/learning-loop-v4.9.md — manta-maestro

**Ref canônico do Learning Loop Fechado (v4.9).** Documenta o pipeline
`judge_score → akp_curation_backlog` aplicado em prod 2026-07-19.

---

## 1. Pipeline em uma tela

```
manta_rag_queries.judge_score < 3
  ── trigger trg_judge_flag_to_backlog ──▶
    akp_curation_backlog (ticket_type='judge_flag', 1 por query_id)

promote_gaps_to_backlog(3, 3.0, 3)  [cron diário 08:00 UTC]
  ── ≥3 flags/30d por (agent_slug, segmento) ──▶
    akp_curation_backlog (ticket_type='judge_pattern', agregado)

v_judge_feedback_health
  ── alimenta prompt refinement, tier promotion (Haiku→Sonnet→Opus),
     Reflexion Loop, SkillForge, dashboard M19.
```

## 2. Objetos criados em prod (project `ogxxgvgtulrbbppshjie`)

**Colunas em `akp_curation_backlog`** (4 aditivas, `ADD COLUMN IF NOT EXISTS`):

| Coluna       | Tipo     | Default            | Uso                                      |
|--------------|----------|--------------------|------------------------------------------|
| `ticket_type`| TEXT     | `'gap_candidate'`  | 3 valores: gap_candidate, judge_flag, judge_pattern |
| `agent_slug` | TEXT     | NULL               | Agente Manta (`filtros->>'filter_agente'`) |
| `evidence`   | JSONB    | `'{}'`             | query_id, trace_id, judge_notes, scores  |
| `priority`   | SMALLINT | 3                  | 1 crítico → 5 baixo. Escala com score    |

**CHECK constraints** (todas `NOT VALID` + `VALIDATE`):
- `ticket_type IN ('gap_candidate','judge_flag','judge_pattern')`
- `priority BETWEEN 1 AND 5`
- `status IN (…, 'open', 'in_review', …)` — expandido v4.9

**3 sequences race-safe** (nunca MAX+1):
- `akp_judge_flag_seq` — tickets `AKP-JF-NNNNN`
- `akp_judge_pattern_seq` — tickets `AKP-JP-NNNNN`
- `akp_gap_candidate_seq` — tickets `AKP-002-NNNNN`

**5 indexes** (2 UNIQUE parciais + 3 regulares):
- `uq_akp_backlog_judge_flag_query` — dedup por query_id
- `uq_akp_backlog_judge_pattern_open` — 1 pattern aberto por (agent_slug, segmento)
- `idx_akp_backlog_ticket_type`, `idx_akp_backlog_agent`,
  `idx_akp_backlog_status_priority` — query paths comuns

**Trigger + função** (SECURITY DEFINER, `SET search_path = public, extensions`):
```sql
CREATE TRIGGER trg_judge_flag_to_backlog
  AFTER INSERT OR UPDATE OF judge_score ON public.manta_rag_queries
  FOR EACH ROW
  WHEN (NEW.judge_score IS NOT NULL AND NEW.judge_score < 3)
  EXECUTE FUNCTION public.judge_flag_to_backlog();
```

**Function** `promote_gaps_to_backlog(INT, FLOAT, INT)` — 2 partes:
1. `gap_candidate` (v4.5 preservada) — ≥N buscas/30d com AVG(hits_count) < X.
2. `judge_pattern` (novo v4.9) — ≥N flags/30d por agente/segmento em UM ticket.

**View** `v_judge_feedback_health` (`security_invoker=true`) — 30d, 8 métricas
+ `health_status` ∈ {critical, warn, ok, healthy}.

## 3. Priority scaling (escala com severity)

| judge_score | priority | interpretação |
|-------------|----------|----------------|
| 0           | 1        | crítico — resposta totalmente errada |
| 1           | 2        | severo — desvio grande do esperado |
| 2           | 3        | moderado — melhorável mas passável |
| 3+          | —        | não gera ticket (só < 3 dispara trigger) |

## 4. Hardening pós-apply (2026-07-19)

- `REVOKE ALL ON v_judge_feedback_health FROM anon, authenticated`;
  `GRANT SELECT` para `authenticated` e `service_role` apenas.
- `REVOKE EXECUTE ON judge_flag_to_backlog() FROM anon, authenticated, PUBLIC`
  — só `postgres` (owner) e `service_role` executam.
- `COMMENT ON VIEW v_akp_judge_health` (v4.6, keep-with-comment):
  "superseded by v_judge_feedback_health em v4.9. Deprecar em v5.0 se 90d
  sem consumer."

## 5. Smoke test (evidência AKP-JF-00001)

```sql
-- INSERT sintético com score baixo:
INSERT INTO public.manta_rag_queries
  (tipo, query_text, judge_score, judge_scored_at, judge_model, filtros, hits_count, timestamp)
VALUES
  ('smoke-test-v4.9', 'smoke', 1, NOW(), 'sonnet-4-6',
   '{"filter_agente":"smoke-agent"}'::jsonb, 0, NOW());

-- Trigger disparou → ticket criado:
-- ticket_id=AKP-JF-00001, ticket_type=judge_flag, agent_slug=smoke-agent,
-- segmento=smoke-test-v4.9, priority=2 (score=1), evidence com query_id + trigger_op

-- 2º UPDATE não cria 2º ticket (dedup via UNIQUE INDEX parcial):
UPDATE public.manta_rag_queries SET judge_score = 0 WHERE tipo = 'smoke-test-v4.9';
-- SELECT: apenas 1 ticket AKP-JF-00001 permanece. Idempotência OK.
```

## 6. Backfill de histórico

Ver `docs/V4.9-BACKFILL-RUNBOOK.md` — 3 passos: (1) preview count de queries
com score<3 sem ticket, (2) `UPDATE no-op` para forçar trigger em rows
existentes, (3) `SELECT promote_gaps_to_backlog(3, 3.0, 3)` para criar
`judge_pattern` retroativos. Rodar UMA VEZ após ativar o juiz LLM na app.

## 7. Rollback (bounded)

Ver bloco comentado no fim de
`supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql`.
1 trigger + 3 funções/views + 5 indexes + 3 constraints + 4 colunas +
3 sequences. Preserva tickets órfãos (`ticket_type=NULL`) — não migra
dados para outra tabela.

## 8. Como o Maestro consome esta camada

- **F6 Guardrails** — ao final de cada resposta star2/star3, se o juiz
  LLM (Sonnet 4.6) retornar `judge_score < 3`, a trigger cria ticket
  automaticamente. Reflexion Loop lê `agent_episodes.last_flags` na
  próxima execução do mesmo agente e ativa autocrítica.
- **F1.c Learned Router** — se `v_judge_feedback_health.health_status =
  'critical'` para um segmento, o dispatcher promove tier de Haiku →
  Sonnet automaticamente.
- **SkillForge** — se >5 tickets `judge_pattern` abertos por 30d para
  o mesmo agente, aciona `skillforge_pipeline.py` para gerar sub-skill
  específica do padrão (gate humano MN via `skillforge_pending_review`).

## 9. Refs cruzados

- `docs/JUDGE-FEEDBACK-LOOP-v4.9-ADAPTED-RUNBOOK.md` — apply + rollback + risks
- `docs/V4.9-BACKFILL-RUNBOOK.md` — promover histórico
- `docs/SPRINT-RETROSPECTIVE-v4.9.md` — pós-mortem
- `docs/ROADMAP-v5.0.md` — próximos 8 vetores
- `refs/reflexion-loop-guide.md` — consumo em Reflexion (v4.7)
- `refs/episodic-memory-schema.md` — episódios que alimentam este pipeline

---

**Migration em prod:** `supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql`
**Gate humano MN:** completado 2026-07-19.
**Autor:** Manta Associados. **Versão:** 4.9.0.
