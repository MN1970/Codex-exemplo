# Health Dashboard — Sistema de Monitoramento de Sync

**Versão:** 1.0.0  
**Arquivo:** `src/services/health-dashboard.ts`

## Visão Geral

O `HealthDashboard` é um serviço completo de monitoramento e telemetria para sistemas de sincronização distribuídos. Fornece visibilidade em tempo real sobre a saúde do sync, detectando problemas antes que impactem usuários finais.

## Recursos Principais

### 1. **Monitoramento de Latência de Sync**
- Rastreia latência de cada operação de sync
- Alvo: < 5 minutos (300.000 ms)
- Calcula: latência atual, média, pico
- Alertas automáticos quando excede alvo

```typescript
dashboard.recordSyncLatency(250000); // 250 segundos
const metrics = dashboard.getMetrics();
console.log(metrics.syncLatency.withinTarget); // true/false
```

### 2. **Rastreamento de Conflitos**
- Monitora conflitos resolvidos vs pendentes
- Detecta acúmulo de conflitos não resolvidos
- Permite resolução individual ou em lote

```typescript
// Registra novo conflito
dashboard.recordConflictPending();

// Resolve um conflito
dashboard.resolveConflict();

// Resolve todos os conflitos
dashboard.resolveAllConflicts();
```

### 3. **Cálculo de Uptime**
- Rastreia outages com timestamps
- Calcula percentage de uptime
- Alvo: > 99%
- Mantém histórico de outages

```typescript
// Registra outage
dashboard.recordOutage('Database disconnected');

// Após a recuperação
dashboard.endOutage();

const metrics = dashboard.getMetrics();
console.log(metrics.uptime.percentage); // 99.5
```

### 4. **Monitoramento de Webhooks**
- Rastreia tentativas de entrega
- Status: SUCCESS, FAILED, PENDING, RETRYING
- Calcula taxa de sucesso e tempo médio de entrega
- Detecta padrões de falha

```typescript
dashboard.recordWebhookDeliveryAttempt(
  'webhook-id',
  WebhookDeliveryStatus.SUCCESS,
  75 // tempo em ms
);

const metrics = dashboard.getMetrics();
console.log(metrics.webhooks.successRate); // 95.5%
```

### 5. **Monitoramento de Profundidade de Fila**
- Rastreia crescimento/diminuição da fila
- Monitora items críticos
- Estima tempo de drenagem
- Calcula taxa de processamento

```typescript
dashboard.recordQueueDepth(
  50,    // profundidade atual
  100,   // máxima
  5      // items críticos
);

const metrics = dashboard.getMetrics();
console.log(metrics.queue.estimatedDrainTimeMin); // Tempo estimado
```

## API Reference

### Classe HealthDashboard

#### Métodos de Registro

| Método | Descrição | Exemplo |
|--------|-----------|---------|
| `recordSyncLatency(ms)` | Registra latência de sync | `dashboard.recordSyncLatency(150000)` |
| `recordConflictPending()` | Registra novo conflito | `dashboard.recordConflictPending()` |
| `recordConflictResolved()` | Incrementa conflitos resolvidos | `dashboard.recordConflictResolved()` |
| `resolveConflict()` | Move um conflito de pendente para resolvido | `dashboard.resolveConflict()` |
| `resolveAllConflicts()` | Resolve todos os pendentes | `dashboard.resolveAllConflicts()` |
| `recordOutage(reason?)` | Registra início de outage | `dashboard.recordOutage('DB down')` |
| `endOutage()` | Encerra outage atual | `dashboard.endOutage()` |
| `recordWebhookDeliveryAttempt(id, status, ms)` | Registra tentativa de webhook | `dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 75)` |
| `recordQueueDepth(depth, maxDepth, criticalCount?)` | Registra profundidade da fila | `dashboard.recordQueueDepth(50, 100, 3)` |

#### Métodos de Consulta

| Método | Retorna | Descrição |
|--------|---------|-----------|
| `getStatus()` | `DashboardStatus` | Status simplificado do dashboard |
| `getMetrics()` | `HealthMetrics` | Métricas detalhadas completas |

#### Métodos de Gerenciamento

| Método | Descrição |
|--------|-----------|
| `clearConflictHistory()` | Reseta contadores de conflitos |
| `resolveAlert(alertId)` | Marca alerta como resolvido |
| `clearResolvedAlerts()` | Remove alertas resolvidos |
| `exportReport()` | Exporta métricas em JSON |
| `reset()` | Reseta todas as métricas |

### Tipos de Retorno

#### DashboardStatus

```typescript
interface DashboardStatus {
  status: HealthStatus;  // HEALTHY | DEGRADED | UNHEALTHY
  summary: {
    syncLatencyMs: number;
    syncOnTarget: boolean;
    conflictsPending: number;
    uptimePercentage: number;
    webhookSuccessRate: number;
    queueDepth: number;
  };
  alerts: HealthAlert[];
  lastUpdate: Date;
}
```

#### HealthMetrics

```typescript
interface HealthMetrics {
  timestamp: Date;
  overallStatus: HealthStatus;
  syncLatency: SyncLatencyMetric;
  conflicts: ConflictMetric;
  uptime: UptimeMetric;
  webhooks: WebhookMetric;
  queue: QueueMetric;
  alerts: HealthAlert[];
}
```

### Enums

#### HealthStatus
- `HEALTHY` — Todos os sistemas operacionais normalmente
- `DEGRADED` — Múltiplos problemas, mas sistema funcional
- `UNHEALTHY` — Problemas críticos detectados

#### WebhookDeliveryStatus
- `SUCCESS` — Entrega bem-sucedida
- `FAILED` — Falha na entrega
- `PENDING` — Aguardando entrega
- `RETRYING` — Em retry

## Uso Prático

### Exemplo 1: Integração Básica

```typescript
import { createHealthDashboard, WebhookDeliveryStatus } from './services/health-dashboard';

const dashboard = createHealthDashboard();

// Durante operações de sync
async function syncData() {
  const startTime = Date.now();

  try {
    // ... operação de sync ...
    const elapsed = Date.now() - startTime;
    dashboard.recordSyncLatency(elapsed);
  } catch (error) {
    dashboard.recordOutage(error.message);
  }
}

// Monitorar webhooks
async function sendWebhook(webhookId: string) {
  const startTime = Date.now();

  try {
    // ... enviar webhook ...
    const elapsed = Date.now() - startTime;
    dashboard.recordWebhookDeliveryAttempt(
      webhookId,
      WebhookDeliveryStatus.SUCCESS,
      elapsed
    );
  } catch (error) {
    dashboard.recordWebhookDeliveryAttempt(
      webhookId,
      WebhookDeliveryStatus.FAILED,
      0
    );
  }
}

// Verificar saúde
const status = dashboard.getStatus();
if (status.status === 'unhealthy') {
  console.error('System is unhealthy!', status.alerts);
}
```

### Exemplo 2: Monitoramento de Conflitos

```typescript
function detectConflicts(changes) {
  for (const change of changes) {
    if (hasConflict(change)) {
      dashboard.recordConflictPending();

      try {
        const resolution = await resolveConflict(change);
        if (resolution.success) {
          dashboard.resolveConflict();
        }
      } catch (error) {
        // Conflito continua pendente
      }
    }
  }
}
```

### Exemplo 3: Dashboard Express

```typescript
import express from 'express';
import { getHealthDashboard } from './services/health-dashboard';

const app = express();
const dashboard = getHealthDashboard();

// Endpoint de saúde
app.get('/health', (req, res) => {
  const status = dashboard.getStatus();
  const statusCode = status.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(status);
});

// Endpoint de métricas detalhadas
app.get('/metrics', (req, res) => {
  const metrics = dashboard.getMetrics();
  res.json(metrics);
});

// Endpoint de alertas
app.get('/alerts', (req, res) => {
  const metrics = dashboard.getMetrics();
  res.json({
    count: metrics.alerts.length,
    alerts: metrics.alerts,
  });
});
```

## Limiares e Alertas

### Limiares de Alerta Automáticos

| Métrica | Alerta | Nível |
|---------|--------|-------|
| Latência de sync | > 300.000 ms (5 min) | WARNING |
| Conflitos pendentes | > 10 | WARNING |
| Taxa de sucesso de webhooks | < 90% | WARNING |
| Taxa de sucesso de webhooks | < 80% | CRITICAL |
| Profundidade de fila | > 80% da máxima | WARNING |
| Profundidade de fila | > 90% da máxima | CRITICAL |
| Uptime | < 99% | WARNING |
| Uptime | < 95% | CRITICAL |

## Padrões de Uso

### Padrão 1: Singleton Global

```typescript
import { getHealthDashboard } from './services/health-dashboard';

// Sempre retorna a mesma instância
const dashboard1 = getHealthDashboard();
const dashboard2 = getHealthDashboard();
// dashboard1 === dashboard2
```

### Padrão 2: Instância Local

```typescript
import { createHealthDashboard } from './services/health-dashboard';

// Cria novas instâncias
const dashboard1 = createHealthDashboard();
const dashboard2 = createHealthDashboard();
// dashboard1 !== dashboard2
```

### Padrão 3: Integração com Logger

```typescript
const dashboard = getHealthDashboard();
const logger = createLogger();

// Log automático de alertas
const metrics = dashboard.getMetrics();
metrics.alerts.forEach(alert => {
  if (alert.severity === 'critical') {
    logger.error(`CRITICAL: ${alert.message}`);
  } else if (alert.severity === 'warning') {
    logger.warn(`WARNING: ${alert.message}`);
  }
});
```

## Testes

O serviço inclui testes abrangentes em `src/services/__tests__/health-dashboard.test.ts`:

```bash
npm test -- src/services/__tests__/health-dashboard.test.ts
```

### Cobertura de Testes

- ✅ Rastreamento de latência de sync
- ✅ Rastreamento de conflitos
- ✅ Cálculo de uptime
- ✅ Monitoramento de webhooks
- ✅ Monitoramento de fila
- ✅ Determinação de status geral
- ✅ Gerenciamento de alertas
- ✅ Exportação e reset
- ✅ Padrão singleton
- ✅ Cenários integrados

## Exemplos Completos

Ver `src/examples/health-dashboard-integration.ts` para 8 exemplos completos:

1. Monitoramento básico de sync
2. Rastreamento de conflitos
3. Monitoramento de uptime
4. Rastreamento de webhooks
5. Monitoramento de fila
6. Cenário de sync degradado
7. Dashboard em tempo real
8. Exportação de relatório

## Melhores Práticas

### 1. **Inicializar Cedo**
```typescript
// Na inicialização da aplicação
const dashboard = getHealthDashboard();
```

### 2. **Registrar Eventos Significativos**
```typescript
// Registre latências reais, não estimadas
const startTime = Date.now();
// ... operação ...
const elapsed = Date.now() - startTime;
dashboard.recordSyncLatency(elapsed);
```

### 3. **Monitorar Periodicamente**
```typescript
setInterval(() => {
  const status = dashboard.getStatus();
  if (status.status !== 'healthy') {
    notifyOps(status);
  }
}, 60000); // A cada minuto
```

### 4. **Limpar Alertas Resolvidos**
```typescript
// Limpe alertas antigos periodicamente
dashboard.clearResolvedAlerts();
```

### 5. **Exportar Relatórios**
```typescript
// Para auditoria ou análise
const report = dashboard.exportReport();
saveToDatabase(report);
```

## Performance

- Histórico interno limitado a 10.000 eventos (evita memory leaks)
- Operações O(1) para registro de eventos
- Cálculos agregados O(n) apenas quando consultados
- Seguro para uso em hot paths

## Troubleshooting

### Status sempre UNHEALTHY

1. Verifique se há latências acima de 300.000 ms
2. Verifique se uptime está abaixo de 95%
3. Verifique taxa de sucesso de webhooks

### Alertas não aparecendo

1. Confirme que eventos estão sendo registrados
2. Chame `getMetrics()` ou `getStatus()` para gerar alertas
3. Verifique se alertas foram resolvidos com `resolveAlert()`

### Memory crescendo

1. Chame `clearResolvedAlerts()` periodicamente
2. Considere chamar `reset()` em intervalos longos
3. Verifique se há vazamentos no seu código de integração

## Roadmap

- [ ] Persistência de métricas em banco de dados
- [ ] Integração com Prometheus/Grafana
- [ ] Alertas via webhook/email
- [ ] Análise de tendências
- [ ] Predição de problemas via ML
- [ ] Dashboard web interativo

## Licença

Parte do projeto Manta Associados — Health Monitoring System
