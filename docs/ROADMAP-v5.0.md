## Resumo

Draft de ROADMAP v5.0 escrito em `/home/user/Codex-exemplo/docs/ROADMAP-v5.0.md` (192 linhas).

**8 vetores ordenados por prioridade:**

1. **Aplicar v4.6 formal em produção** (P0) — learned_router + llm_judge + manta_cases, migrations candidatas prontas, gate humano MN
2. **Reflexion Loop v4.7 Fase 3** (P0) — maestro_reflexion.py + retry policy + gating star2/star3 + alerta Slack
3. **SkillForge v4.7 Fase 6** (P1) — sharepoint/03-skills-forjadas + pipeline automático GH Action daily
4. **Cost governance v4.7** (P1) — cost_log em agent_episodes, dashboard /admin/cost-per-agent, alertas tier
5. **Backfill retroativo promote_gaps** (P2) — WF-AKP-002 histórico, script idempotente, timestamp guard
6. **Deprecação v_akp_judge_health** (P2) — drop view, substituir por agent_response_flags, zero breaking changes
7. **Multi-tenant (v5.0)** (P2) — tenant_id em tabelas chave, RLS Supabase, JWT tenant extraction
8. **Versionamento de agentes + A/B test prompts** (P3) — agent_versions + prompt_experiments, métricas Bayesianas

**Prazos:** vetores 1–2 semana 1–3, vetores 3–6 semana 4–6, vetor 7 semana 7–8, vetor 8 pós v5.0 formal.

**Gate:** MN valida cada stage pós-implementação via feat/ branches + PR → main