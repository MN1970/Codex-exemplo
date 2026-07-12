# LEARNED-ROUTER-UNBLOCK — v4.9

**Ticket:** MAESTRO-V4.9-LEARNED-ROUTING-UNBLOCK
**Autor:** Maestro (draft) — revisar com MN antes de mergear
**Status:** aberto (migração v4.6 ainda não aplicada em `manta-maestro`)

## 1. Diagnóstico (2026-07-12)

Consulta ao projeto Supabase `manta-maestro` (`ogxxgvgtulrbbppshjie`,
região `sa-east-1`, ACTIVE_HEALTHY):

```sql
-- Tentativa direta:
SELECT COUNT(*) FROM public.maestro_routing_predictions;
-- ↳ ERRO / vazio: tabela NÃO existe em produção.

-- Introspecção:
SELECT column_name FROM information_schema.columns
  WHERE table_name='maestro_routing_predictions';
-- ↳ 0 linhas.

-- Único primo em `public` hoje:
SELECT table_name FROM information_schema.tables
  WHERE table_schema='public' AND table_name ILIKE '%maestro%';
-- ↳ maestro_cost_log (v4.7, model tiering)
```

Diagnóstico canônico: **`real_rows = 0` porque a migração v4.6
(`2026_07_12_maestro_learned_router_v4_6.sql`) ainda não foi aplicada.**
O CLAUDE.md master confirma no DEPLOY CHECKLIST v4.6: *"Aplicar as 4
migrações v4.6 no Supabase … ordem: learned_router → llm_judge →
manta_cases"* segue **não marcado**.

Enquanto isso, o `manta-hub/scripts/maestro_learned_router.py` opera em
modo **mock data** (documentado no header). Todo `train` treinou sobre
sintéticos, portanto NENHUM modelo em `data/maestro_router_model.pt` é
apto para produção.

## 2. Ordem de trabalho para desbloquear

### 2.1. Onde no Maestro inserir a telemetria (a)

Hoje o Manta 00 executa apenas o keyword-router legado (§ ROUTING do
CLAUDE.md). Nenhuma decisão de routing é persistida. **A cada dispatch,
o Maestro precisa gravar uma row em `maestro_routing_predictions`.**
Ponto de instrumentação canônico:

- Arquivo: `manta_shared/maestro/dispatcher.py` (função `route(query)`
  — hoje pura, sem side-effect).
- Após decidir `agent_slug`, chamar `log_prediction(...)` (novo helper
  em `manta_shared/maestro/telemetry.py`) — enfileirado em thread
  daemon para não bloquear o turno.
- Quando o subagente termina (fim do DAG), preencher `actual_agent`
  via `UPDATE ... WHERE id = predicted_id` (feedback loop).

Enquanto o pré-router ML não existir em produção, todas as linhas
sairão com `is_override=TRUE, model_version=NULL, predicted_agent=<slug
do keyword-router>` — o keyword-router VIRA a ground truth inicial do
dataset. Isso é intencional: dá bootstrap sem gastar rótulo humano.

### 2.2. Modelo da row (b)

```python
Row(
  query_text       = original user query,        # TEXT
  query_embedding  = e5_small(query),            # vector(384) — mesmo modelo do AskCAD KB
  predicted_agent  = "agente-portos",            # TEXT (ver mapa CLAUDE.md §MAPA COMPLETO)
  confidence       = 1.0,                         # keyword-router é determinístico
  actual_agent     = NULL,                        # atualizado no fim do turno
  is_override      = TRUE,                        # até o MLP estar treinado
  model_version    = "keyword-v4.6",             # sentinela do modo bootstrap
  feedback_source  = "production",               # {production, smoke_test, manual, training}
  session_id       = <maestro session uuid>,
)
```

Contexto extra que ajuda re-treino direcionado (mas ainda NÃO tem
coluna — abrir MAESTRO-V4.9-EXTEND-SCHEMA se virar bloqueador):
`intake_q1` (segmento), `intake_q2` (fase do ciclo de vida 1-8),
`tier_default` (haiku/sonnet/opus).

### 2.3. Trigger de re-treino (c)

`retrain-incremental` no script já suporta cutoff temporal. Regra:

| `real_rows` acumulado | Ação                                                     |
|-----------------------|----------------------------------------------------------|
| < 100                 | Bootstrap; classificar via keyword-router; NÃO treinar.  |
| ≥ 100                 | 1º treino full (`--mode train`); rodar `evaluate`.       |
| ≥ 500                 | Retreino incremental semanal (cron domingo 04:00 UTC).   |
| ≥ 5000                | Retreino noturno (cron diário 04:00 UTC) + versionamento.|

Só marcar `is_override=FALSE` (i.e. adotar predição do MLP) quando
`v_router_accuracy.accuracy_pct ≥ 85 %` na janela de 7 dias E
`disagreement_rate ≤ 10 %` contra o keyword-router (`v_router_disagreements`).

### 2.4. SLO de coleta (d)

Baseline observado no Maestro operacional SP v3.0+: **~10 turnos/dia**
(Manta 00 + 12 verticais + 8 horizontais, ~2 turnos por usuário útil,
5 usuários ativos).

- **Meta:** 100 rows em ≤ 30 dias corridos.
- **Alarme (Slack #maestro-ops via GH Action diária 09:00 UTC):**
  disparar se `last_7d < 21` (i.e. < 3 rows/dia) por 14 dias
  consecutivos. Consulta:

  ```sql
  SELECT COUNT(*) AS last_7d
    FROM maestro_routing_predictions
   WHERE created_at > NOW() - INTERVAL '7 days'
     AND feedback_source = 'production';
  ```

- **Emergency stop:** se ao fim de 45 dias `real_rows < 100`, abandonar
  Plano A e escalar Plano B (§ 2.5).

### 2.5. Plano B — bootstrap sintético (e)

Se a produção não gera volume suficiente, gerar dataset a partir de
conversas históricas do Slack MANTA usando Sonnet 4.6 como extrator:

1. **Fonte:** exportar #manta-projetos, #ia, #obras dos últimos 12
   meses (via Slack Web API ou dump JSON local).
2. **Prompt de extração:** para cada mensagem-turno, classificar em
   `{agente-portos, agente-aeroportos, agente-saneamento, agente-energia,
   agente-barragens, agente-tuneis, agente-mineracao, agente-oleo-gas,
   agente-edificacoes, agente-infraestrutura-{S1..S4}, horizontal-*, none}`
   com justificativa em 1 linha; descartar rótulo `none` ou low-confidence.
3. **Alvo:** 50 exemplos por vertical ativo (13 verticais × 50 = 650
   rows); horizontal-* opcional. Custo estimado ≈ 650 × US$0,02 ≈ US$13
   (Sonnet 4.6 batch).
4. **Persistência:** inserir com `feedback_source='training'`,
   `session_id='synthetic-bootstrap-v4.9'`, `is_override=TRUE`,
   `model_version=NULL`. Estas rows contam para o thresold de 100 mas
   ficam segregadas em `WHERE feedback_source='training'` na view de
   acurácia (para não inflar métrica de produção).
5. **Guarda:** rodar `evaluate` cross-validado 5-fold antes de considerar
   o modelo prod-ready — sintético sozinho não desbloqueia produção,
   apenas o primeiro treino.

## 3. Runbook resumido

```
# 1. Aplicar a migração
supabase db push --project ogxxgvgtulrbbppshjie \
  supabase/migrations/2026_07_12_maestro_learned_router_v4_6.sql

# 2. Instrumentar Maestro (novo PR — manta-hub)
#    → dispatcher.py chama log_prediction() após route()
#    → fechar loop com update_actual_agent() no end-of-DAG

# 3. Deploy → coleta orgânica (30d SLO)

# 4. Ao cruzar 100 rows reais:
python /home/user/manta-hub/scripts/maestro_learned_router.py \
  --mode train --since-days 30
python /home/user/manta-hub/scripts/maestro_learned_router.py \
  --mode evaluate
```

## 4. Métricas alvo (para quando o modelo treinar)

- Top-1 accuracy ≥ 85 % (holdout 20 %)
- ROC-AUC macro (one-vs-rest) ≥ 0,92
- Disagreement rate com keyword-router ≤ 10 % (`v_router_disagreements`)
- P95 latência de inferência ≤ 50 ms (embedding + MLP forward em CPU)

Reavaliar thresholds após 500 rows reais.
