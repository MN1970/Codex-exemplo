# Observabilidade P6 — Maestro v5.0

**Status:** Production-ready  
**Versão:** 2026-07-25  
**Ticket:** MNT-2026-MAESTRO-OBSERVABILITY-P6

---

## Sumário Executivo

O **Pilar P6 (Observabilidade)** implementa logging imutável, append-only, de todas as execuções do Maestro para análise, auditoria e otimização de custos.

### O que foi entregue?

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
| **Schema SQL** | `supabase/migrations/2026_07_25_observability_maestro_runs.sql` | Tabelas: `maestro_runs` (hot), `maestro_runs_archive` (warm), `maestro_feedback` + 6 vistas analíticas |
| **Setup Script** | `scripts/setup_maestro_runs.py` | Inicialização, validação, health checks, archive automático |
| **Hook Integration** | `.claude/hooks/subagentstop_maestro_observability.py` | Grava runs automaticamente via SubagentStop event |
| **Grafana Dashboard** | `docs/grafana_maestro_dashboard.json` | 8 painéis: custo, latência, erro rate, feedback, tiering, top-runs |
| **Documentação** | `docs/OBSERVABILITY_P6_GUIDE.md` | Especificação completa (schema, RLS, retenção, integração) |
| **Deployment** | `docs/DEPLOYMENT_P6_CHECKLIST.md` | Checklist 10-phase, 2-4 horas de setup |
| **Config Example** | `.claude/settings_example.json` | Settings.json com todos os hooks + config |

### Métodos-chave

- **Imutável:** Nenhuma modificação ou deleção (constraints)
- **Append-only:** Apenas INSERT permitido (via RLS)
- **Auditável:** Todas as runs e feedback logged (para GDPR, compliance)
- **Escalável:** Indexes otimizados, retenção automática, archive warm
- **Observável:** 6 vistas analíticas + Grafana dashboard + APScheduler jobs

---

## Arquitetura de Retenção

```
┌──────────────────────────────────────────────────────────┐
│ maestro_runs (HOT — Postgres SSD)                        │
│ 90 dias | 365k runs/ano ≈ 730 MB | < 10ms latência     │
└────────────────────┬─────────────────────────────────────┘
                     │ (daily, 02:00 UTC)
                     ↓
┌──────────────────────────────────────────────────────────┐
│ maestro_runs_archive (WARM — Postgres + backup)          │
│ 365 dias | ≈ 1.4 GB compactado | < 100ms latência      │
└──────────────────────────────────────────────────────────┘
                     │ (audit/compliance)
                     ↓
┌──────────────────────────────────────────────────────────┐
│ Cloud Storage (COLD — S3/GCS backup)                     │
│ Indefinido | Manual restore only                         │
└──────────────────────────────────────────────────────────┘
```

---

## Tabelas

### `maestro_runs` (append-only, imutável)

```sql
CREATE TABLE maestro_runs (
  run_id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  session_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  
  -- Roteamento
  agent_id TEXT NOT NULL,          -- "manta-03-s8"
  skill_id TEXT NOT NULL,          -- "agente-saneamento.v5.0"
  
  -- Modelo & Custo
  model_tier TEXT NOT NULL,        -- haiku-4-5|sonnet-5|opus-5
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cost_usd NUMERIC(10, 6),
  
  -- Performance
  latency_ms INTEGER NOT NULL,
  
  -- Status
  status TEXT NOT NULL,            -- success|timeout|error
  error_message TEXT,
  
  -- Contexto
  phase TEXT,                      -- ciclo de vida (8 fases)
  feedback_score INTEGER,          -- 0-5, optional
  routing_confidence NUMERIC,      -- 0-1
  rag_collection TEXT,
  rag_reranker_score NUMERIC,
  metadata JSONB,
  
  is_archived BOOLEAN DEFAULT FALSE
);
```

### `maestro_feedback` (opcional, para R9)

```sql
CREATE TABLE maestro_feedback (
  feedback_id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES maestro_runs,
  user_id UUID NOT NULL REFERENCES auth.users,
  score INTEGER CHECK (score >= 0 AND score <= 5),
  comment TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Vistas Analíticas (para Grafana)

| Vista | Métrica | Granularidade | Uso |
|-------|---------|---------------|-----|
| `vw_cost_by_agent_daily` | total_cost_usd, run_count, success_rate | Diário/Agent | Custo |
| `vw_latency_by_agent` | p50/p95/p99 ms, avg_ms, min_ms, max_ms | Agent | Performance |
| `vw_error_rate_by_agent` | error%, timeout%, success% | Agent | Confiabilidade |
| `vw_model_tier_distribution` | haiku/sonnet/opus %, total_cost | Diário | Tiering (R7) |
| `vw_feedback_distribution` | 0-5 stars count, % | Agregado | Satisfação |
| `vw_top_cost_runs` | run_id, cost_usd, agent_id, model_tier | Run-level | Debug |

---

## RLS Policies (Privacidade)

| Policy | Operação | Regra | Acesso |
|--------|----------|-------|--------|
| maestro_runs_select_own | SELECT | auth.uid() = user_id | Usuário vê seus dados |
| maestro_runs_no_update | UPDATE | FALSE | Ninguém (imutável) |
| maestro_runs_no_delete | DELETE | FALSE | Ninguém (auditável) |
| maestro_runs_insert_service | INSERT | TRUE | Service role / backend |

---

## Hook SubagentStop Integration

Quando um subagente termina:

```python
# Event dispara hook:
{
  'agent_id': 'manta-03-s8',
  'skill_id': 'agente-saneamento.v5.0',
  'model_tier': 'sonnet-5',
  'input_tokens': 1200,
  'output_tokens': 450,
  'latency_ms': 2500,
  'status': 'success',
  'context': {
    'phase': 'projeto-executivo',
    'routing_confidence': 0.92,
    'rag_collection': 'san:v5.0:chunks',
    'rag_reranker_score': 0.88,
    'complexity_score': 2.5
  }
}

# Hook calcula custo:
cost_usd = calculate_run_cost('sonnet-5', 1200, 450)
# = (1200 × 3.0/1M) + (450 × 15.0/1M) = 0.00360 + 0.00675 = $0.01035

# Hook grava em maestro_runs (async, não-blocking)
```

**Handler:** `.claude/hooks/subagentstop_maestro_observability.py`

**Config:** `.claude/settings.json`:
```json
{
  "hooks": {
    "SubagentStop": {
      "enabled": true,
      "handler": "./.claude/hooks/subagentstop_maestro_observability.py",
      "async": true,
      "timeout_ms": 5000
    }
  }
}
```

---

## APScheduler Jobs (Background)

### Job 1: Archive Diário (02:00 UTC)
```
Move runs 90d+ para maestro_runs_archive (soft delete)
Executa: SELECT archive_old_maestro_runs()
SLA: < 100ms para ~100 runs
```

### Job 2: Health Check Horário (a cada 6h)
```
Valida schema, indexes, RLS, mock inserts
Alerta Slack se falhas
```

### Job 3: Feedback Loop Semanal (domingo 03:00 UTC) — R9
```
Processa feedback_score >= 4
Fine-tunes embedding model (opcional)
Atualiza VERSIONS.json checksums
```

---

## Grafana Dashboard

**Import:** `docs/grafana_maestro_dashboard.json`

### Painéis

1. **Custo por Agente (últimos 30d)** — line chart
2. **Taxa de Erro** — tabela com error%, timeout%, success%
3. **Latência (p50/p95/p99)** — bar chart
4. **Feedback Distribution** — pie chart
5. **Model Tier Distribution** — donut chart
6. **Model Tier Trend (30d)** — stacked line chart
7. **Top 10 Runs por Custo** — tabela
8. **Run Count & Cost Trend** — dual axis

**Refresh:** 30s (em tempo real)

---

## Setup (2-4 horas)

### Quick Start

```bash
# 1. Aplicar migration
supabase db push

# 2. Health check
python scripts/setup_maestro_runs.py --health-check
# ✓ Schema, Indexes, RLS Policies, Mock Insert — PASS

# 3. Configurar Grafana
# Data source: PostgreSQL (Supabase)
# Import: grafana_maestro_dashboard.json

# 4. Habilitar hook
# Edit .claude/settings.json → hooks.SubagentStop.enabled = true

# 5. Iniciar scheduler
python scripts/setup_maestro_runs.py --schedule-jobs &

# 6. Monitorar
# Grafana → Maestro Observability dashboard
# 💚 Tudo funciona?
```

**Detalhado:** `docs/DEPLOYMENT_P6_CHECKLIST.md`

---

## Troubleshooting

### "Hook não está gravando runs"

```bash
# Verificar que hook está ativado
grep -A5 "SubagentStop" .claude/settings.json

# Testar hook manualmente
python .claude/hooks/subagentstop_maestro_observability.py
# ✓ Run gravada com sucesso: [UUID]

# Verificar logs
tail -f /tmp/maestro_scheduler.log
```

### "Grafana dashboard está vazio"

```bash
# Validar data source
# Grafana → Configuration → Data Sources → Supabase Maestro → Test

# Verificar se há dados
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM maestro_runs;"

# Se vazio, inserir mock:
python scripts/setup_maestro_runs.py --health-check
# Isso faz insert de teste
```

### "Archive não está funcionando"

```bash
# Verificar que scheduler está rodando
ps aux | grep setup_maestro_runs.py

# Testar manualmente
python scripts/setup_maestro_runs.py --archive --days-threshold 90

# Validar função PL/pgSQL
psql $SUPABASE_DB_URL -c "SELECT * FROM pg_proc WHERE proname = 'archive_old_maestro_runs';"
```

---

## Queries Úteis

### Custo total por agente hoje
```sql
SELECT agent_id, COUNT(*) as run_count, SUM(cost_usd) as total_cost
FROM maestro_runs
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY agent_id
ORDER BY total_cost DESC;
```

### Erros da última hora
```sql
SELECT run_id, agent_id, status, error_message, latency_ms
FROM maestro_runs
WHERE created_at > NOW() - INTERVAL '1 hour'
  AND status IN ('error', 'timeout')
ORDER BY created_at DESC;
```

### Taxa de erro por agente
```sql
SELECT * FROM vw_error_rate_by_agent ORDER BY error_rate_pct DESC;
```

### Latência p50/p95/p99
```sql
SELECT * FROM vw_latency_by_agent ORDER BY p99_ms DESC;
```

### Runs mais caras
```sql
SELECT * FROM vw_top_cost_runs LIMIT 20;
```

---

## Métricas-Chave (OKR)

| Métrica | Target | Período | Owner |
|---------|--------|---------|-------|
| Error Rate | < 1% | Por agente/dia | Maestro |
| Timeout Rate | < 0.5% | Por agente/dia | Maestro |
| Latência p99 | < 10s | Por agente | Maestro |
| Custo médio/run | < $0.01 | Por agente (via R7) | Product |
| Feedback Score | ≥ 4.0 | Agregado | Product |
| Archive SLA | < 1 dia | Daily | DevOps |

---

## Roadmap Pós-Launch

- **v5.1:** Fine-tuning automático de reranker (R9)
- **v5.2:** BI integrado (Metabase + dashboards por segmento)
- **v5.3:** LLM-as-judge para auto-categorização de erros
- **v5.4:** Cost optimizer advisor

---

## Suporte & Contato

**Proprietário:** mneves@mantaassociados.com  
**Ticket:** MNT-2026-MAESTRO-OBSERVABILITY-P6  
**Slack:** #agent-ops

**Documentação:**
- [P6 Guide](./OBSERVABILITY_P6_GUIDE.md) — Especificação técnica completa
- [Deployment](./DEPLOYMENT_P6_CHECKLIST.md) — Checklist passo-a-passo
- [Schema SQL](../supabase/migrations/2026_07_25_observability_maestro_runs.sql) — DDL
- [Setup Script](../scripts/setup_maestro_runs.py) — Automatização
- [Hook Code](./../.claude/hooks/subagentstop_maestro_observability.py) — Integração

---

**Versão:** 2026-07-25 | **Status:** Production-ready | **Aprovação:** Pendente (MN)
