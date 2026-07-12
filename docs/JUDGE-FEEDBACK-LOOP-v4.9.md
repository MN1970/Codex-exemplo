# Judge Feedback Loop — v4.9

Loop end-to-end que transforma cada resposta ruim do agente em ticket de
curadoria automaticamente, dispensa triagem manual dos flags e feeda o
processo de refinamento de prompt / tier promotion.

**Status:** candidato v4.9 (migration `2026_07_13_judge_feedback_loop_v4_9.sql`).
Nao executar em producao sem gate MN.

---

## Motivacao

v4.6 instalou o juiz LLM (Sonnet 4.6) — cada resposta amostrada recebe um
`judge_score` 0-5. Score < 3 vira um `agent_response_flags` automaticamente,
via trigger. **Ate v4.8 o loop parava ai:** flags acumulavam num backlog
paralelo que ninguem lia rotineiramente. Nao havia priorizacao, nao havia
deteccao de padroes cronicos, e mudancas de prompt nao entravam de volta no
tier de escolha de modelo do Maestro.

**v4.9 fecha:** flag warn/error -> ticket em `akp_curation_backlog` com
`ticket_type='judge_flag'`; padroes recorrentes (>=3 flags/agente/30d) viram
`ticket_type='judge_pattern'`; MN despacha a partir do mesmo painel de
curadoria que ja usa para gaps academicos.

---

## Diagrama do loop

```
    +-----------------------+     score < 3     +---------------------------+
    |  agent_query_log      |------------------>|  agent_response_flags     |
    |  (judge_score, notes) | trigger v4.6      |  (flag_reason, status)    |
    +-----------+-----------+                   +---------------+-----------+
                ^                                               |
                |                                     AFTER INSERT (v4.9)
                |                                               v
                |                                   severity in (warn, error)?
                |                                               |
                |                     +-------------------------+---------+
                |                     |                                   |
                |                    NAO                                 SIM
                |                     |                                   |
                |                  ignora                     +-----------v----------+
                |                                             | akp_curation_backlog |
                |                                             | ticket_type=         |
                |                                             |  'judge_flag'        |
                |                                             +-----------+----------+
                |                                                         |
                |                cron diario 08:00 UTC                    |
                |          (promote_gaps_to_backlog v4.9)                 |
                |                        |                                |
                |                        v                                |
                |         >=3 flags warn+ / 30d / agente?                 |
                |                        |                                |
                |                       SIM                               |
                |                        |                                |
                |          +-------------v-------------+                  |
                |          | ticket_type='judge_pattern' |                |
                |          +-------------+-------------+                  |
                |                        |                                |
                |                        +----------+---------------------+
                |                                   |
                |                                   v
                |                       +-------------------------+
                |                       |  MN painel de curadoria |
                |                       |  (in_review / accepted) |
                |                       +-------------+-----------+
                |                                     |
                |                                     v
                |                   +---------------------------------+
                |                   | prompt refinement / novo KE /    |
                |                   | ajuste routing / tier promote-   |
                |                   | demote                           |
                |                   +---------------+-----------------+
                |                                   |
                +-----------------------------------+
                             (proximo ciclo)
```

---

## Componentes v4.9

### Trigger `trg_judge_flag_to_backlog`

- **Onde:** `agent_response_flags` AFTER INSERT.
- **O que faz:** puxa `judge_score` + `judge_notes` + `agent_slug` do
  `agent_query_log` referenciado; deriva `severity` (0-1 => error, 2 =>
  warn); se warn/error, insere em `akp_curation_backlog` com
  `ticket_type='judge_flag'`, `priority=1|3`, evidence completa em JSONB.
- **Idempotencia:** indice unico parcial em `evidence->>'flag_id'` para
  `ticket_type='judge_flag'`. Re-inserts sao no-op.

### Extensao de `promote_gaps_to_backlog()`

Alem do comportamento historico v4.5 (consumo de `v_akp_gap_candidates`),
agora tambem detecta **padroes cronicos**:

- Janela: 30 dias.
- Gatilho: `n_flags_warn + n_flags_error >= 3` para o mesmo agente.
- Acao: cria ou atualiza ticket `AKP-JP-*` com evidence agregada
  (`n_flags_warn`, `n_flags_error`, `top_flags`).
- Roda no cron diario existente (08:00 UTC, GH Action `akp-daily-cron.yml`).

### View `v_judge_feedback_health`

Painel operacional MN, por agente, janela 30d:

| Coluna              | Semantica                                          |
|---------------------|----------------------------------------------------|
| `agent_slug`        | agente                                             |
| `n_flags_warn`      | flags com score = 2                                |
| `n_flags_error`     | flags com score 0..1                               |
| `n_tickets_open`    | judge_flag + judge_pattern em status ativo         |
| `mean_judge_score`  | media do score dos flags                           |
| `last_ticket_at`    | ultimo ticket judge_* criado                       |

Consulta: `SELECT * FROM v_judge_feedback_health;`.

---

## Playbook MN (revisao e refino)

1. **Diaria (5 min):**
   `SELECT * FROM v_judge_feedback_health WHERE n_flags_error > 0;`
   -> pings vermelhos primeiro.

2. **Triagem de judge_flag:**
   ```sql
   SELECT ticket_id, agent_slug, priority, evidence->>'flag_reason'
     FROM akp_curation_backlog
    WHERE ticket_type='judge_flag' AND status='open'
    ORDER BY priority, first_detected_at DESC;
   ```
   Cada ticket = uma resposta ruim especifica. MN abre a query original
   (`evidence->>'query_log_id'`) e decide:
   - **falso positivo** do juiz -> `status='rejected'`, `notes='FP: <razao>'`
   - **problema real, isolado** -> `status='accepted'`, planeja fix
   - **problema real, sistemico** -> escala para revisao do SKILL.md

3. **Triagem de judge_pattern:**
   Ticket agregado = agente com problema cronico. Sinal forte para:
   - refinar `system_prompt_fragment` do agente
   - promover tier (Haiku -> Sonnet, Sonnet -> Opus)
   - adicionar/atualizar KE que cobre o gap

4. **Merge + tier promotion/demotion:**
   Mudanca no SKILL.md vai por `agent_change_request` (v4.5 governance —
   >=2 approvals). Ao aplicar, `applied_migration` linka de volta ao PR.
   Tickets do backlog que motivaram a mudanca sao fechados
   (`status='closed'`, `linked_ke_ids` ou `notes` referenciando o PR).

---

## Runbook de verificacao

Depois de aplicar a migration no Supabase (via `apply_manta_migrations.py`
ou dashboard):

```bash
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python manta-hub/scripts/verify_judge_feedback_v4_9.py
```

Script:
1. Insere um `agent_query_log` sintetico com `judge_score=2`.
2. Insere um `agent_response_flags` sintetico apontando pra ele.
3. Espera 1s.
4. Verifica que exatamente 1 ticket `judge_flag` aparece em
   `akp_curation_backlog`.
5. Limpa tudo (DELETE em ticket + flag + log).
6. Exit 0 se OK, 1 se falhar.

CI-friendly: pode entrar como job pos-deploy no workflow
`.github/workflows/akp-daily-cron.yml`.

---

## Ligacao com o resto do Maestro v4.7+

- **P2 Prompt Contract (Upgrade B):** quando MN refina prompt em resposta
  a um judge_pattern, o novo P2 vira parte da evidencia (`evidence.p2_v_before`,
  `evidence.p2_v_after` no ticket).
- **Reflexion Loop (Upgrade A):** um flag error pode disparar re-execucao
  reflexiva na proxima ocorrencia do padrao — o Reflexion consulta o backlog
  antes de responder.
- **SkillForge (Upgrade F):** tickets `judge_pattern` sao input direto do
  pipeline de forjamento de skills (padrao repetido = candidato a skill).
- **Model tiering (Upgrade E):** `v_judge_feedback_health.mean_judge_score`
  entra na decisao de tier — agente com score medio < 3.5 em 30d = candidato
  a promocao de tier.

---

## Rollback

Ver bloco comentado no fim da migration
`supabase/migrations/2026_07_13_judge_feedback_loop_v4_9.sql`. Atencao: as
colunas novas em `akp_curation_backlog` NAO devem ser derrubadas se ja
existem rows `judge_flag`/`judge_pattern` — marcar como `closed` e manter.
