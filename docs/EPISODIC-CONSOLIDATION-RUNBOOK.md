# Runbook — Consolidacao da memoria episodica (v4.7)

Referencia: roadmap `MNT-IA-20260712-001` §4.5 (Upgrade C — memoria
episodica) e migration
`supabase/migrations/2026_07_13_maestro_v4_7_reflexion_episodic_cost.sql`.

Cron agendado: `.github/workflows/episodes-consolidation-daily.yml`
(diario 03:00 UTC + `workflow_dispatch`).

---

## 1. Quando consolidar (policy de retention)

A funcao `public.consolidate_old_episodes()` implementa a decay policy
canonica de `agent_episodes`:

| Janela                | Ação                                                                 |
| --------------------- | -------------------------------------------------------------------- |
| **0..30 dias**        | Mantidos crus. Sao a memoria "quente" lida pelo `get_relevant_episodes`. |
| **30..90 dias**       | Destilados: um episodio-resumo por `(agent_id, task_type)` com >=3 ocorrencias; `task_type` prefixado com `destilled_`; top-3 `lessons_learned` mais frequentes. Originais deletados. |
| **> 90 dias**         | Purgados. Os destilados ja cobrem o historico.                       |

Retorno: `INTEGER` = `n_destilados + n_deletados`. Idempotente — grupos
`destilled_%` sao ignorados nas duas passagens.

**Regra pratica:** rodar o cron **1x/dia, ~03:00 UTC** (janela fria do
banco e antes do `akp-daily-cron` das 08:00 UTC). Rodar mais que 1x/dia
nao ganha nada — a janela é ancorada em `NOW() - INTERVAL`, entao runs
extras retornam 0.

---

## 2. Como tunar `p_older_than_days`

A funcao **hoje nao tem parametro** — as janelas 30d/90d estao
hardcoded no SQL. Se precisar afrouxar/apertar a retention:

1. Editar a migration (ou criar migration aditiva `..._episodic_retention.sql`)
   trocando `INTERVAL '30 days'` / `INTERVAL '90 days'` pelos novos
   valores; opcionalmente promovendo `p_older_than_days INTEGER`
   (destilacao) e `p_purge_days INTEGER` (purga) a argumentos com
   defaults.
2. `CREATE OR REPLACE FUNCTION public.consolidate_old_episodes(...)` —
   Postgres aceita adicionar args com default sem quebrar chamadas
   existentes.
3. Se assinatura mudar, ajustar o body do POST no workflow:
   `-d '{"p_older_than_days": 45, "p_purge_days": 120}'`.
4. Aplicar via `supabase db push` e disparar 1 `workflow_dispatch`
   manual para validar antes do proximo run automatico.

**Cuidado:** afrouxar a janela de destilacao (>90d) sem afrouxar a
purga vai perder episodios sem destilar. Sempre `p_purge_days >=
p_older_than_days`.

---

## 3. Como reverter uma consolidacao errada

Consolidacao é destrutiva por design (deleta os originais). Recovery
depende do backup do Supabase:

1. **PITR (Point-in-Time Recovery)** do projeto Supabase — restaura o
   estado imediatamente ANTES do run problematico. Requer plano Pro+.
   Passo-a-passo em https://supabase.com/docs/guides/platform/backups
   (aba Point in time recovery).
2. **Snapshot logico** — se houver dump `pg_dump` recente, restaurar
   apenas a tabela: `pg_restore -t agent_episodes ...`.
3. **Desfazer parcial (destilados sem restore):** deletar linhas
   destiladas criadas pelo run ruim (`WHERE model_used = 'consolidator'
   AND created_at >= '<run_ts>'::timestamptz`) — nao recupera os
   originais mas remove o resumo enganoso.

Antes de mexer, sempre `SELECT COUNT(*) FROM public.agent_episodes
WHERE task_type LIKE 'destilled_%';` para ter baseline. Anexar ao
ticket de incidente.

---

## 4. KPIs — view `v_episodes_health`

A migration cria `public.v_episodes_health` (nao `v_episodic_health` —
atencao ao nome). Rollup de 30d por `agent_id`:

| Coluna                | O que observar                                             |
| --------------------- | ---------------------------------------------------------- |
| `n_episodes`          | Volume — queda abrupta sinaliza cron rodando em excesso.   |
| `avg_iterations`      | Media de iteracoes Reflexion. Alvo `<= 1.5`.               |
| `avg_quality_score`   | Alvo `>= 0.75`. Queda >0.10 semana-a-semana investigar.    |
| `pct_escalated`       | Escalation p/ humano. Alerta se `> 10 %` em 7d rolling.    |
| `n_aluci_fail`        | Falhas do aluci-guard — deveria tender a zero.             |
| `n_consist_fail`      | Falhas do consist-guard — idem.                            |
| `n_star3/2/1`         | Distribuicao de `output_tier`.                             |
| `last_episode_at`     | Se `> 24h`, telemetria pode ter parado.                    |

Query padrao pos-run:

```sql
SELECT agent_id, n_episodes, avg_quality_score, pct_escalated
FROM public.v_episodes_health
ORDER BY avg_quality_score ASC NULLS LAST
LIMIT 10;
```

Complementar com `SELECT task_type, COUNT(*) FROM public.agent_episodes
WHERE task_type LIKE 'destilled_%' GROUP BY 1 ORDER BY 2 DESC;` para
ver quais grupos concentram destilacao (bom indicador de tarefas
repetitivas — candidatas a SkillForge/Upgrade F).

---

## 5. Alerta Slack — spike de consolidacao

**Threshold:** se um run destilar + purgar `> 5 %` do total de
episodios ativos, disparar ping `#manta-maestro-ops` para MN.

Racional: em regime estacionario o run diario mexe em <1 % da tabela
(so entra na janela 30..90d que o run anterior nao pegou). Um pico
`> 5 %` significa (a) o cron ficou dias sem rodar e entrou muita
massa de uma so vez, ou (b) alguem alterou os intervalos sem calibrar.

Query de deteccao (pos-run, dentro do proprio workflow ou no
`akp-daily-cron` como watchdog):

```sql
WITH tot AS (
  SELECT COUNT(*) AS n_total FROM public.agent_episodes
),
recent_destilled AS (
  SELECT COUNT(*) AS n_new
  FROM public.agent_episodes
  WHERE model_used = 'consolidator'
    AND created_at >= NOW() - INTERVAL '1 hour'
)
SELECT
  n_total,
  n_new,
  ROUND(100.0 * n_new / NULLIF(n_total, 0), 2) AS pct_new_destilled
FROM tot, recent_destilled;
```

Se `pct_new_destilled > 5.0`, o step deve marcar `::warning::` e
opcionalmente postar no webhook Slack (secret `SLACK_WEBHOOK_OPS`).
Enquanto o webhook nao esta configurado, o operador MN checa o
resultado do run manualmente via `::notice::` do workflow.

---

## 6. Playbook rapido de troubleshooting

| Sintoma                                              | Diagnostico                                                                                       |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Workflow falha com `"code":"42883"`                  | Funcao nao existe — migration nao aplicada. Rodar `supabase db push`.                             |
| Workflow falha com `"code":"42501"`                  | Service role sem `EXECUTE` — `GRANT EXECUTE ON FUNCTION public.consolidate_old_episodes() TO service_role;`. |
| Retorno = `0` por varios dias                        | Ou nao ha episodios na janela 30..90d, ou o cron rodou N vezes no mesmo dia. Checar `v_episodes_health.n_episodes`. |
| `avg_quality_score` despenca apos consolidacao       | Destilados herdam `AVG(quality_score)` do grupo — normal se o cluster de tarefas era de baixa qualidade. Investigar `task_type` origem. |
| Timeout HTTP no curl                                 | `agent_episodes` cresceu muito. Aumentar timeout do step (`curl --max-time 300`) e considerar rodar `VACUUM ANALYZE`. |
