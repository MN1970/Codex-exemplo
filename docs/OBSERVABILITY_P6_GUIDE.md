# Manta Maestro v5.0 — Observabilidade (P6)

**Versão:** 2026-07-25  
**Ticket:** MNT-2026-MAESTRO-OBSERVABILITY-P6  
**Status:** Production-ready

## Visão Geral

Este documento especifica o **Pilar P6 (Observabilidade)** da arquitetura Maestro v5.0:

- **Tabela imutável `maestro_runs`** — Log append-only de todas as execuções
- **Retenção automática** — 90 dias hot (Postgres), 365 dias warm (archive)
- **RLS policies** — Privacidade por user_id
- **Vistas analíticas** — Para Grafana dashboards
- **Integração SubagentStop** — Hook para gravação automática de runs
- **APScheduler jobs** — Archive diário, feedback loop, health checks

---

## 1. SCHEMA E ESTRUTURA

### 1.1 Tabelas Principais

#### `maestro_runs` (append-only, imutável)

```sql
CREATE TABLE maestro_runs (
  run_id UUID PRIMARY KEY,                -- UUID único
  user_id UUID NOT NULL,                  -- FK auth.users
  session_id TEXT NOT NULL,               -- Claude Code session
  created_at TIMESTAMPTZ NOT NULL,        -- Timestamp da execução
  
  -- Roteamento (R1)
  agent_id TEXT NOT NULL,                 -- e.g., "manta-03-s8"
  skill_id TEXT NOT NULL,                 -- e.g., "agente-saneamento.v5.0"
  
  -- Modelo & Custos
  model_tier TEXT NOT NULL,               -- haiku-4-5|sonnet-5|opus-5
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cost_usd NUMERIC(10, 6) NOT NULL,      -- Calculado via calculate_run_cost()
  
  -- Performance
  latency_ms INTEGER NOT NULL,            -- Tempo total em ms
  
  -- Status & Erros
  status TEXT NOT NULL,                   -- success|timeout|error
  error_message TEXT,
  
  -- Contexto
  phase TEXT,                             -- estudo-previo|projeto-basico|...
  feedback_score INTEGER,                 -- 0-5, opcional, pós-run
  feedback_timestamp TIMESTAMPTZ,
  
  -- Observabilidade
  routing_confidence NUMERIC(3, 2),       -- 0.0-1.0
  rag_collection TEXT,                    -- e.g., "san:v5.0:chunks"
  rag_reranker_score NUMERIC(3, 2),
  metadata JSONB,                         -- complexity_score, fallback_cascade, etc.
  
  -- Auditoria
  is_archived BOOLEAN DEFAULT FALSE,
  created_at_utc TIMESTAMPTZ GENERATED ALWAYS AS (created_at AT TIME ZONE 'UTC')
);
```

#### `maestro_runs_archive` (warm storage)

- Mesma estrutura que `maestro_runs`, mas sem FKs (dados já transferidos)
- Preenchida automaticamente via `archive_old_maestro_runs()` quando runs ultrapassam 90 dias
- Compactada com índices menos agressivos
- Retenção: 365 dias (conforme GDPR/auditoria)

#### `maestro_feedback` (opcional, para feedback loop R9)

```sql
CREATE TABLE maestro_feedback (
  feedback_id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES maestro_runs(run_id),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 5),
  comment TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. RETENÇÃO & ARCHIVE

### 2.1 Política de Retenção

| Camada | Tabela | Período | Tipo | SLA Latência |
|--------|--------|---------|------|-------------|
| Hot | maestro_runs | 90 dias | SSD Postgres | < 10ms |
| Warm | maestro_runs_archive | 365 dias | Postgres + backup | < 100ms |
| Cold | External backup | Indefinido | Cloud storage (S3/GCS) | Manual restore |

### 2.2 Função de Archive Automático

```sql
-- Chamada diariamente às 02:00 UTC via APScheduler
SELECT archived_count FROM archive_old_maestro_runs();
```

**O que faz:**
1. Copia runs com `created_at < NOW() - INTERVAL '90 days'` para `maestro_runs_archive`
2. Marca `is_archived = TRUE` na tabela hot (soft delete, não remove dados)
3. Valida via ON CONFLICT para idempotência (seguro re-executar)
4. Log: `{archived_count, error_count}` para APScheduler

**Segurança:**
- Dados nunca são deletados (auditoria)
- Soft delete permite rollback se necessário
- Archive table tem dados imutáveis (constraint NOT NULL em todas as colunas)

### 2.3 Cálculo de Retenção

```
Supabase Postgres: ~$0.07 / GB / mês
Estimativa:
  - 1000 runs/dia × 365 dias = 365k runs/ano
  - ~2KB por run (média) = 730 MB/ano
  - Hot (90d): ~180MB = ~$0.01/mês
  - Warm (270d): ~540MB = ~$0.04/mês
  - Total: ~$0.05/mês (negligível)

Backup automático Supabase:
  - 7-day backup retention (included)
  - Archive table compactada via VACUUM (weekly)
```

---

## 3. ROW-LEVEL SECURITY (RLS)

### 3.1 Políticas

| Policy | Tabela | Operação | Regra | Quem pode |
|--------|--------|----------|-------|-----------|
| maestro_runs_select_own | maestro_runs | SELECT | `auth.uid() = user_id` | Usuário autenticado (seus dados) |
| maestro_runs_no_update | maestro_runs | UPDATE | `FALSE` | Ninguém (imutável) |
| maestro_runs_no_delete | maestro_runs | DELETE | `FALSE` | Ninguém (imutável) |
| maestro_runs_insert_service | maestro_runs | INSERT | `TRUE` | Service role / backend app |
| maestro_feedback_select_own | maestro_feedback | SELECT | `auth.uid() = user_id` | Usuário autenticado |
| maestro_feedback_insert_own | maestro_feedback | INSERT | `auth.uid() = user_id` | Usuário autenticado |

### 3.2 Validação RLS

```bash
# Verificar que RLS está ativado
psql $SUPABASE_DB_URL -c "
  SELECT relname, rowsecurity 
  FROM pg_class 
  WHERE relname IN ('maestro_runs', 'maestro_feedback');
"

# Listar policies
psql $SUPABASE_DB_URL -c "
  SELECT policyname, tablename, cmd 
  FROM pg_policies 
  WHERE tablename LIKE 'maestro_%';
"
```

---

## 4. INDEXES

### 4.1 Estratégia de Indexação

| Index | Colunas | Uso |
|-------|---------|-----|
| idx_maestro_runs_agent_created | (agent_id, created_at DESC) | Dashboard: custo/agente/dia |
| idx_maestro_runs_status_created | (status, created_at DESC) | Dashboard: taxa de erro |
| idx_maestro_runs_cost_usd | (cost_usd DESC) | Top-N runs por custo |
| idx_maestro_runs_user_created | (user_id, created_at DESC) | Auditoria por usuário |
| idx_maestro_runs_model_created | (model_tier, created_at DESC) | Análise de tiering (R7) |
| idx_maestro_runs_phase_created | (phase, created_at DESC) | Queries por ciclo de vida |
| idx_maestro_runs_skill_created | (skill_id, created_at DESC) | Skill utilization |
| idx_maestro_runs_agent_status_created | (agent_id, status, created_at DESC) | Composite para queries complexas |

### 4.2 Tamanho Estimado

```
1000 runs/dia × 90 dias hot = 90k runs
Per-run: 200 bytes de dados + 100 bytes por index (média 4 indexes)
Total: 90k × 200 = 18 MB hot + ~36 MB indexes = ~54 MB hot
Warm (270 dias): ~162 MB dados + ~162 MB indexes = ~324 MB total

Supabase incluye até 8GB de storage, portanto sem problemas.
```

---

## 5. VISTAS ANALÍTICAS (PARA GRAFANA)

### 5.1 Vistas Disponíveis

#### `vw_cost_by_agent_daily`

```sql
SELECT date, agent_id, run_count, total_cost_usd, avg_cost_usd, 
       error_count, timeout_count, success_rate_pct
FROM vw_cost_by_agent_daily
WHERE date >= NOW() - INTERVAL '30 days'
ORDER BY date DESC, total_cost_usd DESC;
```

Uso: **Painel de Custo por Agente**

#### `vw_latency_by_agent`

```sql
SELECT agent_id, run_count, p50_ms, p95_ms, p99_ms, avg_ms
FROM vw_latency_by_agent
ORDER BY avg_ms DESC;
```

Uso: **Painel de Performance (p50, p95, p99)**

#### `vw_error_rate_by_agent`

```sql
SELECT agent_id, total_runs, error_count, timeout_count, 
       error_rate_pct, timeout_rate_pct, success_rate_pct
FROM vw_error_rate_by_agent
ORDER BY error_rate_pct DESC;
```

Uso: **Painel de Confiabilidade**

#### `vw_model_tier_distribution`

```sql
SELECT date, model_tier, run_count, pct_of_day, total_cost_usd
FROM vw_model_tier_distribution
WHERE date >= NOW() - INTERVAL '30 days'
ORDER BY date DESC;
```

Uso: **Painel de Tiering (R7 efficiency)**

#### `vw_feedback_distribution`

```sql
SELECT feedback_score, count, pct
FROM vw_feedback_distribution
ORDER BY feedback_score DESC;
```

Uso: **Painel de Satisfação (stars 0-5)**

#### `vw_top_cost_runs`

```sql
SELECT run_id, date, agent_id, model_tier, cost_usd, status
FROM vw_top_cost_runs
LIMIT 10;
```

Uso: **Debug: Top-10 runs mais caras**

---

## 6. INTEGRAÇÃO COM HOOK SubagentStop

### 6.1 Fluxo SubagentStop → maestro_runs

O hook `SubagentStop` (disparado quando um subagente termina) deve:

1. **Coletar dados da execução:**
   - run_id (gerado ou recebido)
   - user_id (contexto do session)
   - agent_id (qual agente rodou)
   - skill_id (qual skill versionada)
   - input_tokens, output_tokens (do response)
   - model_tier (qual modelo foi usado)
   - latency_ms (agora - start_time)
   - status (success|timeout|error)
   - error_message (se aplicável)

2. **Calcular custo:**
   ```python
   cost_usd = calculate_run_cost(model_tier, input_tokens, output_tokens)
   ```

3. **Injetar contexto:**
   - phase (do metadata da sessão)
   - routing_confidence (do R1 routing)
   - rag_collection, rag_reranker_score (do RAG context)

4. **Gravar em maestro_runs:**
   ```python
   supabase.table('maestro_runs').insert({
       'run_id': run_id,
       'user_id': user_id,
       'session_id': session_id,
       'agent_id': agent_id,
       'skill_id': skill_id,
       'model_tier': model_tier,
       'input_tokens': input_tokens,
       'output_tokens': output_tokens,
       'cost_usd': cost_usd,
       'latency_ms': latency_ms,
       'status': status,
       'error_message': error_message,
       'phase': phase,
       'routing_confidence': routing_confidence,
       'rag_collection': rag_collection,
       'rag_reranker_score': rag_reranker_score,
       'metadata': {
           'complexity_score': complexity_score,
           'fallback_cascade': fallback_model or None,
           'keywords_matched': len(keywords),
           'rag_hit': rag_reranker_score is not None
       }
   }).execute()
   ```

### 6.2 Implementação do Hook (Pseudocódigo)

**Arquivo esperado:** `.claude/hooks/subagentstop.py` (ou em settings.json)

```python
# hook: SubagentStop
# trigger: quando um agente/subagente termina execução

def on_subagent_stop(event):
    """
    Grava run em maestro_runs quando subagente termina.
    
    Args:
        event: {
            'agent_id': str,
            'session_id': str,
            'user_id': str,
            'model_tier': str,
            'input_tokens': int,
            'output_tokens': int,
            'latency_ms': int,
            'status': str,
            'error_message': str | None,
            'context': {
                'phase': str | None,
                'routing_confidence': float,
                'rag_collection': str | None,
                'rag_reranker_score': float | None,
                'complexity_score': float
            }
        }
    """
    from supabase import create_client
    from datetime import datetime
    
    # Cliente Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Calcular custo
    cost_usd = calculate_run_cost(
        event['model_tier'],
        event['input_tokens'],
        event['output_tokens']
    )
    
    # Preparar payload
    run_record = {
        'user_id': event['user_id'],
        'session_id': event['session_id'],
        'agent_id': event['agent_id'],
        'skill_id': event.get('skill_id', 'unknown'),
        'model_tier': event['model_tier'],
        'input_tokens': event['input_tokens'],
        'output_tokens': event['output_tokens'],
        'cost_usd': cost_usd,
        'latency_ms': event['latency_ms'],
        'status': event['status'],
        'error_message': event.get('error_message'),
        'phase': event['context'].get('phase'),
        'routing_confidence': event['context']['routing_confidence'],
        'rag_collection': event['context'].get('rag_collection'),
        'rag_reranker_score': event['context'].get('rag_reranker_score'),
        'metadata': {
            'complexity_score': event['context']['complexity_score'],
            'fallback_cascade': event.get('fallback_model'),
            'keywords_matched': event['context'].get('keywords_matched', 0)
        }
    }
    
    # Inserir em maestro_runs
    try:
        result = supabase.table('maestro_runs').insert(run_record).execute()
        logger.info(f"[P6] Run gravada: {run_record['run_id']}")
    except Exception as e:
        logger.error(f"[P6] Erro ao gravar run: {e}")
        # Não falha a execução se observabilidade falhar
        pass
```

### 6.3 Integração em settings.json

```json
{
  "hooks": {
    "SubagentStop": {
      "enabled": true,
      "service": "maestro_observability",
      "handler": "on_subagent_stop",
      "async": true,
      "timeout_ms": 5000,
      "retry": {
        "max_attempts": 2,
        "backoff_ms": 1000
      }
    }
  }
}
```

---

## 7. APSCHEDULER JOBS (BACKGROUND)

### 7.1 Jobs Configurados

#### Job 1: Archive Diário (02:00 UTC)

```python
scheduler.add_job(
    archive_old_maestro_runs,
    'cron',
    hour=2, minute=0,
    id='maestro_archive_daily',
    coalesce=True,
    max_instances=1
)
```

**O que faz:**
- Move runs com idade > 90 dias para `maestro_runs_archive`
- Marca `is_archived = TRUE` na tabela hot
- Log: `{archived_count, error_count}`

#### Job 2: Health Check Horário (a cada 6 horas)

```python
scheduler.add_job(
    validate_schema_and_indexes,
    'cron',
    hour='*/6', minute=0,
    id='maestro_health_check_6h'
)
```

**O que faz:**
- Valida índices e vistas
- Verifica RLS policies
- Executa teste de insert mock
- Alert se falhas detectadas

#### Job 3: Feedback Loop Semanal (domingo 03:00 UTC)

```python
scheduler.add_job(
    process_feedback_loop,
    'cron',
    day_of_week=6, hour=3, minute=0,
    id='maestro_feedback_loop_weekly'
)
```

**O que faz (R9 feedback loop):**
- Coleta feedback_score ≥ 4
- Extrai embeddings de prompts relacionados
- Fine-tunes reranker cross-encoder (opcional)
- Atualiza checksum em VERSIONS.json

### 7.2 Setup do APScheduler

```bash
# Instalar
pip install APScheduler pytz

# Iniciar scheduler em background
python scripts/setup_maestro_runs.py --schedule-jobs

# Ou, em produção (systemd):
# [Service]
# ExecStart=/usr/bin/python3 /app/scripts/setup_maestro_runs.py --schedule-jobs
# Restart=always
# RestartSec=10
```

---

## 8. GRAFANA DASHBOARD

### 8.1 Setup Grafana

```bash
# 1. Adicionar data source Supabase
# Grafana → Configuration → Data Sources → New
# Type: PostgreSQL
# Host: [SUPABASE_HOST]
# Database: postgres
# User: postgres
# Password: [SUPABASE_PASSWORD]
# SSL Mode: require

# 2. Importar dashboard
# Grafana → Dashboards → Import
# Upload: docs/grafana_maestro_dashboard.json

# 3. Configurar refresh
# Dashboard → Settings → Refresh interval: 30s
```

### 8.2 Painéis Inclusos

| Painel | Métrica | Granularidade | Período |
|--------|---------|---------------|---------|
| Custo por Agente | total_cost_usd | Diário | Últimos 30 dias |
| Taxa de Erro | error_rate_pct, timeout_rate_pct | Por agente | Último período completo |
| Latência (p50/p95/p99) | Percentis | Por agente | Último período |
| Feedback Distribution | 0-5 stars | Agregado | Último período |
| Model Tier Distribution | haiku|sonnet|opus | Diário | Últimos 30 dias |
| Top 10 Runs por Custo | cost_usd | Run-level | Último período |

### 8.3 Alertas Sugeridos

```yaml
# Alert 1: Error Rate > 5%
- alert: MaestroHighErrorRate
  expr: error_rate_pct{agent_id=~"manta-.*"} > 5
  for: 15m
  annotations:
    summary: "{{ $labels.agent_id }} error rate {{ $value }}%"
    action: "Check maestro_runs for details"

# Alert 2: Timeout Rate > 2%
- alert: MaestroHighTimeoutRate
  expr: timeout_rate_pct{agent_id=~"manta-.*"} > 2
  for: 10m
  annotations:
    summary: "{{ $labels.agent_id }} timeout rate {{ $value }}%"

# Alert 3: Latency p99 > 30s
- alert: MaestroHighLatency
  expr: p99_ms > 30000
  for: 5m
  annotations:
    summary: "{{ $labels.agent_id }} p99 latency {{ $value }}ms"
```

---

## 9. DEPLOYMENT

### 9.1 Checklist de Deployment

- [ ] Executar migration: `supabase db push`
- [ ] Validar schema: `python scripts/setup_maestro_runs.py --init`
- [ ] Setup Grafana data source
- [ ] Importar dashboard JSON
- [ ] Configurar APScheduler jobs
- [ ] Integrar hook SubagentStop em settings.json
- [ ] Testar insert via hook (mock run)
- [ ] Monitorar Grafana por 24h
- [ ] Configurar alertas Slack (#agent-ops)

### 9.2 Rollback

```bash
# Se problemas:
psql $SUPABASE_DB_URL -f supabase/migrations/2026_07_25_observability_maestro_runs.sql --reverse
# (Nota: migration não possui bloco UP/DOWN reversível via Supabase CLI.
# Manual: DROP TABLE maestro_runs CASCADE; DROP TABLE maestro_feedback;)
```

---

## 10. DÚVIDAS & TROUBLESHOOTING

### Q: Por que RLS bloqueia INSERT do hook?

**R:** RLS policies devem permitir INSERT via `service_role` (credenciais de backend). Validar:

```sql
-- Hook roda como service_role:
GRANT INSERT, SELECT ON maestro_runs TO service_role;
```

### Q: Qual é o impacto de performance do archive?

**R:** Archive roda uma única vez por dia (02:00 UTC), típico < 100ms para 90-100 runs movidas. Seguro.

### Q: Como fazer queries manuais em maestro_runs?

**R:**
```sql
-- Custo de um agente hoje
SELECT agent_id, SUM(cost_usd) as total_cost
FROM maestro_runs
WHERE agent_id = 'manta-03-s8' 
  AND DATE(created_at) = CURRENT_DATE
GROUP BY agent_id;

-- Taxade erro última hora
SELECT status, COUNT(*) as count
FROM maestro_runs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY status;

-- Top runs por cost
SELECT run_id, agent_id, cost_usd, status
FROM maestro_runs
ORDER BY cost_usd DESC
LIMIT 10;
```

### Q: Como integrar com Slack alerts?

**R:**
```python
# scripts/slack_maestro_alerts.py
from slack_sdk import WebClient
from supabase import create_client

def alert_error_rate():
    errors = supabase.rpc('get_error_stats_last_hour').execute()
    if errors.data:
        msg = "🚨 Erros detectados na última hora:\n"
        for row in errors.data:
            msg += f"- {row['agent_id']}: {row['error_count']} erros\n"
        slack.chat_postMessage(channel='#agent-ops', text=msg)

# Schedule: a cada 5 minutos
scheduler.add_job(alert_error_rate, 'interval', minutes=5)
```

---

## 11. MÉTRICAS-CHAVE (OKR)

| Métrica | Target | Período | Responsável |
|---------|--------|---------|-------------|
| Error Rate | < 1% | Por agente/dia | Maestro team |
| Timeout Rate | < 0.5% | Por agente/dia | Maestro team |
| Latência p99 | < 10s | Por agente | Maestro team |
| Custo médio/run | < $0.01 | Por agente/dia (via tiering R7) | Maestro + Product |
| Feedback Score médio | ≥ 4.0 stars | Agregado | Product |
| Archive SLA | < 1 dia | Daily job | DevOps |

---

## 12. ROADMAP PÓS-LAUNCH

- [ ] **v5.1:** Fine-tuning automático de reranker (R9 feedback loop)
- [ ] **v5.2:** BI integrado (Metabase + dashboards customizados por segmento)
- [ ] **v5.3:** LLM-as-judge para auto-categorização de erros
- [ ] **v5.4:** Cost optimization advisor (recomendações de tiering)

---

**Fim do documento. Para suporte, contate: mneves@mantaassociados.com**
