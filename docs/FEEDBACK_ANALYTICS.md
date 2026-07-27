# FEEDBACK_ANALYTICS.md — Documentação da Iniciativa 3

**Iniciativa 3: Feedback Analytics — Análise de Ratings + Triggers**

Versão: **1.0.0** (2026-07-27)

---

## 1. Visão Geral

Implementação completa de analytics de feedback para monitorar a saúde dos agentes Manta em produção, detectar problemas de desempenho e disparar ações automáticas (alertas Slack, fine-tuning automático).

**Objetivos:**
- Agregação semanal de ratings e feedbacks por agente
- Detecção de tendências (up/down/stable)
- Alertas automáticos quando avg_rating < 3.5 por 2 semanas
- Retraining automático se avg_rating < 3.0 por 2 semanas
- Dashboard Grafana com 7 panels de visualização
- Dashboard React integrado no frontend

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend                                                    │
├─────────────────────────────────────────────────────────────┤
│ FeedbackAnalyticsDashboard.tsx (React + Recharts)          │
│   ├─ GET /feedback/analytics/by-agent (weekly stats)       │
│   └─ GET /feedback/analytics/alerts (alert list)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Backend (FastAPI)                                           │
├─────────────────────────────────────────────────────────────┤
│ routers/feedback.py                                         │
│   ├─ POST /feedback (existing)                             │
│   ├─ GET /feedback (existing)                              │
│   ├─ GET /feedback/analytics/by-agent (NEW)                │
│   └─ GET /feedback/analytics/alerts (NEW)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tasks (Background Jobs)                                     │
├─────────────────────────────────────────────────────────────┤
│ tasks/feedback_analytics.py                                 │
│   └─ run_feedback_analytics_pipeline() [scheduled weekly]   │
│       ├─ compute_agent_stats() → SQL aggregation           │
│       ├─ detect_trend() → compara com semana anterior      │
│       ├─ trigger_retraining_job() → submete LoRA job      │
│       └─ send_slack_alert() → notifica #agent-performance │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Database (PostgreSQL)                                       │
├─────────────────────────────────────────────────────────────┤
│ Tables (ORM via database.py):                               │
│   ├─ feedback (Feedback model) — logs de feedback           │
│   └─ feedback_alerts (FeedbackAlert model) — alertas        │
│                                                             │
│ Migrations (Alembic):                                       │
│   └─ 0006_feedback_alerts.py — cria tabela feedback_alerts │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes

### 3.1 Models (database.py)

#### `Feedback` (existente, melhorado)
```python
class Feedback(Base):
    __tablename__ = "feedback"
    
    id: str                 # UUID
    org_id: str            # FK organizations
    session_id: str | None  # FK sessions (opcional)
    agent_id: str | None   # FK agents (opcional)
    user_id: str | None    # FK users (opcional)
    rating: int            # -1 (ruim) | 0 (neutro) | 1 (bom)
    comment: str | None
    created_at: datetime
```

#### `FeedbackAlert` (novo)
```python
class FeedbackAlert(Base):
    __tablename__ = "feedback_alerts"
    
    id: str                           # UUID
    org_id: str                       # FK organizations
    agent_id: str | None              # FK agents
    agent_slug: str                   # "agente-saneamento", "agente-energia", etc.
    avg_rating: float                 # p.ex. 3.2
    feedback_count: int               # total de feedback no período
    trend: str                        # "up" | "down" | "stable"
    threshold: float                  # 3.5 (padrão)
    action_taken: str                 # "slack_notified" | "retraining_job_submitted" | ...
    metadata: dict[str, Any]          # contexto extra (weeks_below, retraining job id, etc.)
    triggered_at: datetime
```

### 3.2 Endpoints (routers/feedback.py)

#### `POST /feedback` (existente)
Registra um feedback sobre um agente.

**Request:**
```json
{
  "agent_code": "Manta 03-S8",
  "rating": -1,
  "comment": "Lento demais",
  "user_email": "user@company.com"
}
```

**Response:** `FeedbackRecord`

---

#### `GET /feedback/analytics/by-agent` (novo)
Retorna estatísticas agregadas por agente.

**Query params:**
- `org_id` (optional): filtrar por organização
- `weeks_back` (int, default=1): quantas semanas atrás?

**Response:**
```json
{
  "timestamp": "2026-07-27T10:00:00Z",
  "stats": [
    {
      "agent_slug": "agente-saneamento",
      "agent_code": "Manta 03-S8",
      "avg_rating": 3.2,
      "feedback_count": 45,
      "std_dev": 0.85,
      "trend": "down",
      "rating_distribution": {"-1": 12, "0": 8, "1": 25},
      "negative_comment_tags": ["lento", "impreciso", "resposta incompleta"]
    },
    ...
  ],
  "summary": {
    "total_agents_analyzed": 20,
    "agents_with_feedback": 15,
    "total_feedback_entries": 342,
    "avg_rating_all_agents": 3.45
  }
}
```

---

#### `GET /feedback/analytics/alerts` (novo)
Retorna alertas disparados (agentes com baixo desempenho).

**Query params:**
- `org_id` (optional): filtrar por organização
- `limit` (int, default=50): máximo de alertas

**Response:**
```json
[
  {
    "id": "alert-uuid-1",
    "agent_slug": "agente-saneamento",
    "agent_code": "Manta 03-S8",
    "avg_rating": 3.2,
    "feedback_count": 45,
    "trend": "down",
    "threshold": 3.5,
    "action_taken": "slack_notified",
    "triggered_at": "2026-07-27T08:00:00Z",
    "metadata": {
      "weeks_below_threshold": 2,
      "prev_rating": 3.5
    }
  },
  ...
]
```

---

### 3.3 Background Task (tasks/feedback_analytics.py)

#### `run_feedback_analytics_pipeline(org_id: str | None = None)`
Entry point principal. Executa semanalmente (sugere-se segunda-feira 09:00 UTC).

**Fluxo:**

1. **Agregação semanal** (`compute_agent_stats`):
   - Query: `SELECT AVG(rating), STDDEV(rating), COUNT(*) FROM feedback WHERE agent_id = ? AND created_at >= cutoff`
   - Calcula: avg_rating, std_dev, feedback_count

2. **Trend Detection** (`detect_trend`):
   - Compara avg_rating desta semana com semana anterior
   - Classifica: "up" (delta > 0.2), "down" (delta < -0.2), "stable"

3. **Alertas** (se avg_rating < 3.5 por 2+ semanas):
   - Insere `FeedbackAlert` com `action_taken = "slack_notified"`
   - Envia notificação Slack para #agent-performance

4. **Retraining Trigger** (se avg_rating < 3.0 por 2+ semanas):
   - Submete `FineTuneJob` automático
   - Atualiza `FeedbackAlert` com `action_taken = "retraining_job_submitted"`
   - Metadata: `{"retraining": {"job_id": "...", "segment": "saneamento", "status": "queued"}}`

**Exemplo de uso:**
```python
# Roda para TODAS as organizações
result = await run_feedback_analytics_pipeline()
print(result)
# {
#   "timestamp": "2026-07-27T09:00:00Z",
#   "agents_analyzed": 20,
#   "alerts_triggered": 3,
#   "alerts": [
#     {"agent_slug": "agente-saneamento", "avg_rating": 3.2, "action": "retraining_job_submitted"}
#   ]
# }

# Ou para organização específica
result = await run_feedback_analytics_pipeline(org_id="org-uuid")
```

---

### 3.4 Frontend Dashboard (FeedbackAnalyticsDashboard.tsx)

Componente React integrado que exibe:

1. **Summary Cards:**
   - Agentes analisados (total)
   - Com feedback (count)
   - Total feedback entries (última semana)
   - Avg rating geral

2. **Trend Chart:**
   - Line chart: evolução da media semanal nos últimos 30 dias

3. **Low-Rated Agents Table:**
   - Apenas agentes com avg_rating < 3.5
   - Highlight em vermelho
   - Clicável para detalhe

4. **All Agents Table:**
   - Todas os agentes com feedback
   - Sortable, filterable
   - Drill-down por agente

5. **Alerts List:**
   - Últimos 20 alertas disparados
   - Status da ação (slack_notified, retraining_job_submitted)
   - Metadata do alerta

6. **Agent Detail (Modal):**
   - Ao clicar em um agente:
     - Cards: avg_rating, feedback_count, std_dev
     - Negative comment tags
     - Rating distribution (bar chart)

---

### 3.5 Grafana Dashboard (monitoring/grafana-feedback-dashboard.json)

7 panels pré-configurados:

1. **Avg Rating por Agente (bar chart)**
   - Últimos 7 dias
   - Color-coded: verde (>3.5), amarelo (3.0-3.5), vermelho (<3.0)

2. **Rating Distribution (pie chart)**
   - Proporção de -1/0/1 ratings

3. **Agentes com <3.5 Stars (table)**
   - Highlight vermelho
   - Colunas: agent_slug, avg_rating, feedback_count, trend

4. **Trend Semanal (line chart)**
   - Evolução da média geral (últimos 30 dias)

5. **Volume de Feedback por Dia (line chart)**
   - Últimos 30 dias

6. **Palavra frequentes em Feedback Negativo (word cloud ou tags)**
   - Tags extraídos de comentários com rating=-1

7. **Alert Status (table)**
   - Últimos 20 alertas
   - Colunas: agent_slug, avg_rating, action_taken, triggered_at

---

## 4. Agendamento

### Option A: APScheduler (Python sync)
```python
# No app.py startup:
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    run_feedback_analytics_pipeline,
    "cron",
    day_of_week="mon",
    hour=9,
    minute=0,
    timezone="UTC",
    id="feedback_analytics_weekly",
)
scheduler.start()
```

### Option B: Celery (Python async)
```python
# tasks/feedback_analytics.py
from celery import shared_task

@shared_task
def feedback_analytics_task(org_id: str | None = None):
    return asyncio.run(run_feedback_analytics_pipeline(org_id))

# celerybeat config:
# "feedback-analytics-weekly": {
#     "task": "tasks.feedback_analytics.feedback_analytics_task",
#     "schedule": crontab(day_of_week=0, hour=9, minute=0),
# }
```

### Option C: Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: manta-feedback-analytics
spec:
  schedule: "0 9 * * 1"  # Segunda 09:00 UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: analytics
            image: manta-backend:latest
            command:
            - python
            - -c
            - "import asyncio; from tasks.feedback_analytics import run_feedback_analytics_pipeline; asyncio.run(run_feedback_analytics_pipeline())"
```

---

## 5. Slack Integration

### Setup:
1. Criar webhook URL em Slack:
   - Workspace > Settings > Apps > Incoming Webhooks
   - Channel: #agent-performance
   - Copiar URL: `https://hooks.slack.com/services/T.../B.../X...`

2. Adicionar em `.env`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../X...
```

3. Implementar em `send_slack_alert()`:
```python
import os
import requests

async def send_slack_alert(agent_slug: str, avg_rating: float, action: str) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set, skipping Slack alert")
        return
    
    message = {
        "text": f":warning: Agent Alert: {agent_slug}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":warning: {agent_slug} — Baixo desempenho",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Agent:*\n{agent_slug}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Avg Rating:*\n{avg_rating:.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Action:*\n{action}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Timestamp:*\n{datetime.now(timezone.utc).isoformat()}"
                    }
                ]
            }
        ]
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code != 200:
        logger.error("Failed to send Slack alert: %s", response.text)
```

---

## 6. Retraining Workflow

Quando `avg_rating < 3.0` por 2+ semanas:

1. **Submit FineTuneJob**:
   - `segment`: extraído do agent_slug (ex: "saneamento")
   - `base_model`: "mistralai/Mistral-7B-v0.1" (padrão)
   - `epochs`: 3
   - `status`: "queued"

2. **Status tracking**:
   - Job é processado por `ml/finetuning.py::run_finetuning_pipeline()`
   - Status: queued → running → completed|failed
   - Metadata em `FeedbackAlert`: `{"retraining": {"job_id": "...", "status": "...", "loss": ...}}`

3. **Monitoring**:
   - GET `/ml/finetune/{job_id}` retorna status

---

## 7. Teste Local

### Setup:
```bash
# 1. Migrations
cd manta-backend
alembic upgrade head

# 2. Rodas analytics manualmente
python -c "
import asyncio
from tasks.feedback_analytics import run_feedback_analytics_pipeline
result = asyncio.run(run_feedback_analytics_pipeline())
print(result)
"

# 3. Verificar dados
psql $DATABASE_URL -c "SELECT * FROM feedback_alerts ORDER BY triggered_at DESC LIMIT 5;"
```

### Endpoints de teste:
```bash
# Analytics por agente
curl -s http://localhost:8000/api/feedback/analytics/by-agent?weeks_back=1 | jq .

# Alertas
curl -s http://localhost:8000/api/feedback/analytics/alerts?limit=10 | jq .

# Submeter feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"agent_code":"Manta 03-S8","rating":-1,"comment":"Lento"}'
```

---

## 8. Checklist de Deployment

- [ ] Migrations Alembic rodadas (`alembic upgrade head`)
- [ ] Tabela `feedback_alerts` criada e indexada
- [ ] Endpoints `/feedback/analytics/by-agent` e `//alerts` testados
- [ ] FeedbackAlert model integrado em `database.py`
- [ ] Agendamento configurado (APScheduler/Celery/CronJob)
- [ ] `SLACK_WEBHOOK_URL` definido em `.env`
- [ ] Grafana dashboard importado (`grafana-feedback-dashboard.json`)
- [ ] Frontend: `FeedbackAnalyticsDashboard.tsx` registrado em router
- [ ] Testes unitários: `tests/test_feedback_analytics.py`
- [ ] Documentação integrada em Wiki/SharePoint

---

## 9. Thresholds & Config

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `DEFAULT_ALERT_THRESHOLD` | 3.5 | Aviso se avg_rating cair abaixo |
| `RETRAINING_THRESHOLD` | 3.0 | Crítico, dispara retraining automático |
| `MIN_WEEKS_BELOW` | 2 | Mínimo de semanas abaixo para disparar alerta |
| `GRAFANA_LOOKBACK` | 30d | Período padrão no dashboard |
| `SLACK_ALERT_ENABLED` | True | Habilita Slack (toggleável) |

Todos mapeáveis para variáveis de ambiente se desejado.

---

## 10. Métricas & KPIs

### Observabilidade:
- Número de agentes com feedback (cobertura)
- Distribuição de ratings (qualidade)
- Agentes em watchlist (alertas ativos)
- Jobs de retraining iniciados (ações automáticas)
- Slack alerts enviados (engajamento)

### Exemplo de query para SLO:
```sql
-- Percentual de agentes com avg_rating >= 3.5 (SLO: 90%)
SELECT
  COUNT(CASE WHEN avg_rating >= 3.5 THEN 1 END)::float / COUNT(*) * 100 as pct_healthy
FROM (
  SELECT agent_id, AVG(rating) as avg_rating
  FROM feedback
  WHERE created_at >= now() - interval '7 days'
  GROUP BY agent_id
) t;
```

---

## 11. Referências

- **CLAUDE.md**: Manta Agent Registry master
- **database.py**: SQLAlchemy ORM models
- **routers/feedback.py**: API endpoints
- **tasks/feedback_analytics.py**: Background analytics task
- **alembic/versions/0006_feedback_alerts.py**: Database migration
- **FeedbackAnalyticsDashboard.tsx**: Frontend component
- **grafana-feedback-dashboard.json**: Grafana dashboard config

---

**Versão:** 1.0.0 (2026-07-27)  
**Status:** ✅ Completo — pronto para deployment  
**Owner:** Manta DevOps / Engineering Team
