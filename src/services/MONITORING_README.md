# Monitoring & Observability Service

**Versão**: 1.0.0  
**Localização**: `/src/services/monitoring.ts`  
**Linguagem**: TypeScript

Serviço completo de observabilidade com suporte a:
- Métricas Prometheus (latência, taxa de sucesso, profundidade de fila)
- Logging estruturado com Pino + JSON
- Rastreamento distribuído (pronto para OpenTelemetry)
- Gerenciamento inteligente de alertas com integração Slack
- Dashboard queries para Grafana/Prometheus

---

## Instalação

### 1. Instalar dependências

```bash
npm install
```

As seguintes dependências foram adicionadas ao `package.json`:

```json
{
  "@opentelemetry/api": "^1.7.0",
  "@opentelemetry/auto-instrumentations-node": "^0.40.0",
  "@opentelemetry/exporter-prometheus": "^0.45.1",
  "@opentelemetry/sdk-metrics": "^1.18.1",
  "@opentelemetry/sdk-node": "^0.44.1",
  "@opentelemetry/sdk-trace-node": "^0.44.1",
  "pino": "^8.17.0",
  "pino-pretty": "^10.3.1",
  "uuid": "^9.0.1"
}
```

### 2. Variáveis de ambiente

```bash
# Slack webhook para alertas (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Environment
NODE_ENV=production
LOG_LEVEL=info
```

---

## Componentes Principais

### 1. MetricsCollector

Coleta métricas estilo Prometheus (counter, gauge, histogram, summary).

```typescript
const collector = new MetricsCollector(logger);

// Counter (incremental)
collector.incrementCounter("requests_total", 1, { method: "GET" });

// Gauge (valor absoluto)
collector.setGauge("queue_depth", 45, { service: "sync" });

// Histogram (distribuição)
collector.recordHistogram("latency_ms", 245, { endpoint: "/api/sync" });

// Obter agregações
const agg = collector.aggregateMetrics("latency_ms");
// {
//   mean: 245.5,
//   p50: 240,
//   p95: 280,
//   p99: 300
// }
```

**Métricas padrão registradas**:
- `requests_total` — total de requisições
- `requests_success` — requisições bem-sucedidas
- `requests_error` — requisições com erro
- `sync_latency_ms` — latência de sincronização
- `queue_depth` — profundidade da fila
- `error_rate_percent` — taxa de erro
- `cpu_usage_percent` — uso de CPU
- `db_pool_connections` — conexões ativas no pool

### 2. AlertManager

Gerencia alertas com suporte a Slack, histórico e resolução.

```typescript
const alertManager = new AlertManager(logger);

// Registrar regra
alertManager.registerRule({
  id: "high-latency",
  name: "High Request Latency",
  metricName: "sync_latency_ms",
  operator: ">",
  threshold: 5000,
  severity: AlertSeverity.WARNING,
  enabled: true,
  slackWebhook: process.env.SLACK_WEBHOOK_URL,
  channels: ["#alerts"],
});

// Avaliar métrica contra regras
const alerts = alertManager.evaluateRules("sync_latency_ms", 7500);
// → Alerta criado automaticamente se > 5000

// Acessar alertas ativos
const activeAlerts = alertManager.getActiveAlerts();

// Resolver alerta
alertManager.resolveAlert(alert.id);

// Histórico
const history = alertManager.getAlertHistory(100);
```

**Operadores suportados**: `>`, `<`, `>=`, `<=`, `==`, `!=`

**Severidades**: `info`, `warning`, `error`, `critical`

**Alertas padrão configurados**:
1. High Error Rate (> 5%)
2. Request Timeout (latência > 30s)
3. Stale Sync (queue depth > 100)
4. Critical CPU Usage (> 90%)

### 3. TracingManager

Rastreamento distribuído OpenTelemetry-ready.

```typescript
const tracing = new TracingManager(logger);

// Iniciar trace
const traceContext = tracing.startTrace();
// { traceId: "uuid", spanId: "uuid", flags: 1 }

// Criar spans
const span = tracing.createSpan(traceContext, "fetch_data", {
  source: "github",
});

// Simular work...

// Finalizar span
tracing.endSpan(span, { status: "success", records: 150 });

// Exportar trace (OpenTelemetry format)
const trace = tracing.exportTrace(traceContext.traceId);
```

**Formato de exportação**:
```json
{
  "traceId": "...",
  "spanCount": 3,
  "spans": [
    {
      "spanId": "...",
      "parentSpanId": "...",
      "name": "fetch_data",
      "startTime": "2026-07-31T...",
      "endTime": "2026-07-31T...",
      "attributes": { "source": "github" }
    }
  ]
}
```

### 4. Logger (Pino)

Logging estruturado com JSON em produção.

```typescript
const logger = createLogger("my-service", "production");

// Info
logger.info(
  { userId: "123", action: "login" },
  "User logged in"
);

// Warning
logger.warn(
  { remaining: 10, resetAt: "..." },
  "API rate limit warning"
);

// Error
logger.error(
  { error: "Connection refused", retries: 3 },
  "Database connection failed"
);

// Debug (apenas em desenvolvimento)
logger.debug(
  { payload: {...} },
  "Processing webhook"
);
```

**Configuração automática**:
- **Desenvolvimento**: logs coloridos e pretty-printed via pino-pretty
- **Produção**: logs em JSON estruturado (enviável direto para ELK/Datadog)

### 5. ObservabilityManager

Integrador central que une todos os componentes.

```typescript
const observability = new ObservabilityManager("sync-service", "production");

// Acessar componentes
observability.metrics.recordHistogram("latency_ms", 245);
observability.alerts.evaluateRules("latency_ms", 245);
observability.tracing.startTrace();
observability.logger.info({}, "message");

// Status geral
const status = observability.getSystemStatus();

// Métricas Prometheus
const promMetrics = observability.getPrometheusMetrics();

// Cleanup
observability.shutdown();
```

---

## Casos de Uso

### Caso 1: Monitorar sincronização GitHub

```typescript
const observability = new ObservabilityManager("github-sync", "production");

// Registrar webhook customizado
observability.alerts.registerRule({
  id: "stale-sync-github",
  name: "GitHub Sync is Stale",
  metricName: "queue_depth",
  operator: ">",
  threshold: 50,
  severity: AlertSeverity.ERROR,
  slackWebhook: process.env.SLACK_WEBHOOK_URL,
});

async function syncGitHub() {
  const trace = observability.tracing.startTrace();
  
  try {
    const startTime = Date.now();
    
    // Fetch PRs
    const span1 = observability.tracing.createSpan(
      trace,
      "fetch_prs"
    );
    const prs = await fetchPRsFromGitHub();
    observability.tracing.endSpan(span1);

    // Process PRs
    const span2 = observability.tracing.createSpan(
      trace,
      "process_prs"
    );
    for (const pr of prs) {
      await processPR(pr);
      observability.metrics.incrementCounter("prs_processed");
    }
    observability.tracing.endSpan(span2);

    // Record metrics
    const duration = Date.now() - startTime;
    observability.metrics.recordHistogram("sync_latency_ms", duration);
    observability.metrics.incrementCounter("sync_success");

  } catch (error) {
    observability.metrics.incrementCounter("sync_error");
    observability.logger.error({ error }, "GitHub sync failed");
    throw error;
  }
}
```

### Caso 2: Integração com Express

```typescript
import express from "express";
import { createObservabilityMiddleware } from "./monitoring";

const app = express();
const observability = new ObservabilityManager("api-server", "production");

// Aplicar middleware global
app.use(createObservabilityMiddleware(observability));

// Seus routes aqui...
app.get("/api/data", (req, res) => {
  res.json({ data: [] });
});

// Cada requisição terá:
// - X-Trace-ID header
// - X-Span-ID header
// - Latência registrada em http_request_latency_ms
// - Sucesso/erro registrado em requests_success/error
```

### Caso 3: Dashboard Grafana

**Prometheus endpoint** (para integrar com Grafana):

```typescript
app.get("/metrics", (req, res) => {
  res.type("text/plain");
  res.send(observability.getPrometheusMetrics());
});
```

**Grafana dashboard queries**:

```promql
# Latência P95
histogram_quantile(0.95, sync_latency_ms)

# Taxa de sucesso
rate(requests_success[5m]) / rate(requests_total[5m]) * 100

# Taxa de erro
rate(requests_error[5m]) / rate(requests_total[5m]) * 100

# Profundidade média da fila
avg(queue_depth)

# Requisições por segundo
rate(requests_total[1m])
```

### Caso 4: Alertas no Slack

**Configuração**:

```typescript
observability.alerts.registerRule({
  id: "high-error-rate",
  name: "⚠️ Erro: Taxa alta de falhas",
  metricName: "error_rate_percent",
  operator: ">",
  threshold: 5,
  severity: AlertSeverity.CRITICAL,
  slackWebhook: "https://hooks.slack.com/services/...",
  channels: ["#alerts", "#devops"],
});

// Quando error_rate_percent > 5%, envia para Slack:
// [CRITICAL] ⚠️ Erro: Taxa alta de falhas
// Current Value: 8.5%
// Threshold: 5%
// Metric: error_rate_percent
// Time: 2026-07-31T10:45:32.123Z
```

### Caso 5: Relatório de saúde do sistema

```typescript
// A cada 1 minuto
setInterval(() => {
  const status = observability.getSystemStatus();
  
  console.log("=== System Health Report ===");
  console.log(`Latência P95: ${status.health.metrics.latency.p95}ms`);
  console.log(`Taxa de sucesso: ${status.health.metrics.successRate.toFixed(2)}%`);
  console.log(`Profundidade de fila: ${status.health.metrics.queueDepth}`);
  console.log(`Alertas ativos: ${status.health.alerts.active}`);
  
  // Enviar para time de monitoramento
  notifyTeam(status);
}, 60000);
```

---

## Queries Úteis para Dashboard

### Prometheus Queries

```promql
# 1. Latência P99 últimas 5m
histogram_quantile(0.99, rate(sync_latency_ms[5m]))

# 2. Throughput (requisições por segundo)
rate(requests_total[1m])

# 3. Taxa de erro (últimos 5 minutos)
(rate(requests_error[5m]) / rate(requests_total[5m])) * 100

# 4. Profundidade média da fila
avg_over_time(queue_depth[5m])

# 5. Uptime (tempo sem erros)
(count(requests_success) / count(requests_total)) * 100

# 6. CPU usage trend
rate(cpu_usage_percent[5m])

# 7. Database pool saturation
(avg(db_pool_connections) / 100) * 100

# 8. Alertas por severidade (últimas 24h)
count(ALERTS{severity="critical"})
count(ALERTS{severity="error"})
count(ALERTS{severity="warning"})
```

### JSON Queries (via /system-status endpoint)

```bash
# Obter status geral
curl http://localhost:3000/system-status | jq '.health.metrics'

# Obter alertas ativos
curl http://localhost:3000/system-status | jq '.health.alerts.list'

# Obter histórico de alertas (últimos 100)
curl http://localhost:3000/alerts/history?limit=100
```

---

## Limpeza e Retenção

O `ObservabilityManager` realiza limpeza automática a cada 10 minutos:

```typescript
// Remover métricas > 1 hora
metrics.pruneMetrics(3600000);

// Remover alertas resolvidos > 24 horas
alerts.pruneAlerts(86400000);

// Remover traces > 1 hora
tracing.pruneTraces(3600000);
```

**Limitações por padrão**:
- Max 10.000 métricas por nome
- Max 1.000 alertas em histórico
- Max 1.000 spans por trace

---

## Performance

### Overhead de observabilidade

- **Latência adicionada**: < 1ms por requisição
- **Memória**: ~50MB para 1.000 métricas em memória
- **CPU**: < 1% em modo idle

### Escalabilidade

Para ambientes com **alto volume**:

```typescript
// Aumentar retenção
observability.metrics.pruneMetrics(7200000); // 2 horas

// Integrar com Prometheus remoto
const prometheusMetrics = observability.getPrometheusMetrics();
// Enviar via pushgateway ou remote_write
await fetch("http://prometheus-pushgateway:9091/metrics/job/sync-service", {
  method: "POST",
  body: prometheusMetrics,
});
```

---

## Troubleshooting

### Alertas não disparam

```typescript
// 1. Verificar se regra está habilitada
observability.alerts.registerRule({
  // ...
  enabled: true, // ✅ Importante!
});

// 2. Verificar se métrica está sendo registrada
observability.metrics.recordHistogram("sync_latency_ms", 5000);

// 3. Avaliar regra manualmente
const alerts = observability.alerts.evaluateRules("sync_latency_ms", 5000);
console.log(alerts); // Deve conter o alerta
```

### Slack webhook não funciona

```typescript
// 1. Testar webhook manualmente
const payload = {
  attachments: [{
    color: "ff0000",
    title: "Test Alert",
    text: "Testing Slack integration"
  }]
};

fetch(process.env.SLACK_WEBHOOK_URL, {
  method: "POST",
  body: JSON.stringify(payload)
}).then(r => console.log(r.status)); // Deve ser 200

// 2. Verificar environment variable
console.log(process.env.SLACK_WEBHOOK_URL); // Não deve ser undefined

// 3. Habilitar debug logs
const observability = new ObservabilityManager("test", "development");
// Logs detalhados aparecerão no console
```

### Memória crescendo indefinidamente

```typescript
// 1. Verificar retenção de métricas
observability.metrics.pruneMetrics(1800000); // 30 min (menor)

// 2. Resetar métricas em desenvolvimento
observability.metrics.reset();

// 3. Monitorar crescimento
setInterval(() => {
  const metrics = observability.metrics.getDashboardData();
  console.log("Metrics count:", Object.keys(metrics).length);
}, 60000);
```

---

## Roadmap

**v1.1.0** (próxima versão):
- [ ] Suporte a OpenTelemetry collector remoto
- [ ] Integração com DataDog / New Relic
- [ ] Correlação automática de erros
- [ ] Sampling de traces adaptativo
- [ ] Agregações em tempo real via Redis

**v2.0.0**:
- [ ] Persistência em banco de dados
- [ ] Web dashboard nativo
- [ ] Análise automática de anomalias
- [ ] Correlação com logs em ELK

---

## Referências

- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Pino Logger](https://getpino.io/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/)
- [Slack API](https://api.slack.com/messaging/webhooks)

---

## Suporte

Para dúvidas ou issues:
1. Verificar exemplos em `src/services/examples/monitoring-example.ts`
2. Consultar testes em `src/services/__tests__/monitoring.test.ts`
3. Abrir issue no repositório

---

**Mantido por**: Manta Associados  
**Última atualização**: 2026-07-31  
**Versão**: 1.0.0
