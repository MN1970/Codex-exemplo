# Notifications Service Documentation

Sistema inteligente de notificações com agrupamento de eventos, rate limiting, preferências de usuário e analytics de delivery.

## Visão Geral

O **Notifications Service** (`src/services/notifications.ts`) fornece:

- **InteligentNotifier**: Classe principal que gerencia eventos e notificações
- **Agrupamento inteligente**: Agrupa eventos relacionados por janela de tempo configurável
- **Rate limiting**: Máximo 5 notificações por minuto por usuário (configurável)
- **Preferências do usuário**: Optin/optout global e por tipo de evento
- **Analytics completo**: Rastreamento de entrega, abertura e cliques
- **Templates**: Mensagens pré-formatadas para cada tipo de evento

## Tipos de Eventos Suportados

```typescript
enum NotificationEventType {
  PR_OPENED = "pr_opened",
  PR_MERGED = "pr_merged",
  PR_REVIEW_REQUESTED = "pr_review_requested",
  AGENT_UPDATED = "agent_updated",
  AGENT_DEPLOYED = "agent_deployed",
  TEST_FAILED = "test_failed",
  TEST_PASSED = "test_passed",
  BUILD_FAILED = "build_failed",
  BUILD_SUCCESS = "build_success",
  DEPLOYMENT_STARTED = "deployment_started",
  DEPLOYMENT_COMPLETED = "deployment_completed",
  SKILL_ADDED = "skill_added",
  SKILL_DEPRECATED = "skill_deprecated",
}
```

## Níveis de Prioridade

```typescript
enum NotificationPriority {
  LOW = "low",           // Informação geral
  MEDIUM = "medium",     // Alterações normais
  HIGH = "high",         // Ação recomendada
  CRITICAL = "critical", // Requer ação imediata
}
```

## Canais de Entrega

- **Email**: Via provedor de email (SendGrid, AWS SES, etc)
- **Webhook**: Endpoint HTTP configurado
- **Slack**: Mensagens diretas ou canais
- **In-app**: Armazenado no banco de dados

## Arquitetura

### Fluxo de Processamento

```
1. Evento adicionado → addEvent()
   ↓
2. Verifica rate limit → RateLimitMonitor
   ↓
3. Verifica preferências do usuário
   ↓
4. Enfileira evento por groupKey
   ↓
5. Agenda processamento (janela de agrupamento)
   ↓
6. Processa grupo → createGroupNotification()
   ↓
7. Entrega via canal → deliverNotification()
   ↓
8. Registra analytics → DeliveryAnalytics
```

### Classes Principais

#### InteligentNotifier

A classe principal que gerencia todo o ciclo de vida das notificações.

```typescript
class InteligentNotifier {
  // Adicionar evento
  addEvent(event: NotificationEvent): Promise<void>

  // Gerenciar preferências
  getUserPreferences(userId: string): UserNotificationPreferences
  setUserPreferences(userId: string, preferences: Partial<...>): void
  setEventTypePreference(userId: string, eventType: NotificationEventType, enabled: boolean): void

  // Analytics
  getDeliveryAnalytics(userId: string): DeliveryAnalytics[]
  getDeliveryStats(userId: string): DeliveryStats
  getRateLimitMetrics(userId: string): RateLimitMetrics
  getNotificationHistory(userId: string, limit?: number): NotificationHistory

  // Marcar como aberta/clicada
  markAsOpened(notificationId: string, userId: string): void
  markAsClicked(notificationId: string, userId: string): void

  // Cleanup
  destroy(): void
}
```

## Uso Básico

### 1. Criar um Notifier

```typescript
import { getNotifier, NotificationEventType, NotificationPriority } from "./services/notifications";

const notifier = getNotifier();
```

### 2. Adicionar um Evento

```typescript
const event = {
  id: "evt_pr_123",
  type: NotificationEventType.PR_OPENED,
  userId: "user_456",
  timestamp: new Date(),
  priority: NotificationPriority.MEDIUM,
  data: {
    prNumber: 123,
    prTitle: "Add notifications service",
    author: "john_doe",
    repository: "codex-exemplo",
  },
  groupKey: "pr_group_123", // Agrupa eventos relacionados
  metadata: {
    source: "github",
    tags: ["feature", "notifications"],
  },
};

await notifier.addEvent(event);
```

### 3. Configurar Preferências do Usuário

```typescript
notifier.setUserPreferences("user_456", {
  optin: true,
  channelPreferences: {
    email: true,
    webhook: false,
    inApp: true,
    slack: true,
  },
  rateLimit: {
    maxPerMinute: 5,
    maxPerHour: 30,
  },
  groupingWindowMs: 300000, // 5 minutos
});
```

### 4. Desabilitar Tipos de Eventos

```typescript
// Desabilita notificações para testes passando
notifier.setEventTypePreference(
  "user_456",
  NotificationEventType.TEST_PASSED,
  false
);
```

### 5. Consultar Analytics

```typescript
// Estatísticas de entrega
const stats = notifier.getDeliveryStats("user_456");
console.log(stats);
// {
//   totalSent: 10,
//   totalDelivered: 9,
//   totalFailed: 1,
//   deliveryRate: 90,
//   averageDeliveryTimeMs: 145.5,
//   byChannel: {
//     email: { sent: 5, delivered: 5 },
//     inApp: { sent: 5, delivered: 4 },
//     ...
//   }
// }

// Histórico de notificações
const history = notifier.getNotificationHistory("user_456", 50);
console.log(history.summary);
// {
//   total: 10,
//   delivered: 9,
//   failed: 1,
//   opened: 7,
//   clicked: 3
// }

// Rate limiting
const rateLimit = notifier.getRateLimitMetrics("user_456");
console.log(rateLimit);
// { eventsLastMinute: 3, throttled: false }
```

### 6. Marcar Notificações como Abertas/Clicadas

```typescript
// Quando usuário abre uma notificação
notifier.markAsOpened("notif_123", "user_456");

// Quando usuário clica em ação
notifier.markAsClicked("notif_123", "user_456");
```

## Agrupamento de Eventos

O serviço agrupa eventos relacionados por `groupKey` dentro de uma janela de tempo configurável (padrão: 5 minutos).

### Exemplo de Agrupamento

Três eventos com mesmo `groupKey`:

```
[09:00:00] PR #123 aberto → type: PR_OPENED
[09:00:15] Revisão solicitada em #123 → type: PR_REVIEW_REQUESTED
[09:00:30] Alguém comentou em #123 → type: PR_OPENED (novo comment)

↓ (após janela de 5 minutos)

Uma notificação agrupada:
"3 notificações sobre PR #123"
```

## Rate Limiting

O sistema limita notificações por usuário:

- **Padrão**: 5 eventos/minuto
- **Configurável**: Via `setUserPreferences()`
- **Monitorado**: Rastreado por `RateLimitMonitor`

```typescript
// Verificar se usuário está throttled
const metrics = notifier.getRateLimitMetrics("user_456");
if (metrics.throttled) {
  console.log("Usuário atingiu rate limit");
}
```

Quando evento excede rate limit:
- É descartado silenciosamente
- Um warning é registrado
- Analytics não é atualizado

## Preferências do Usuário

### Estrutura de Preferências

```typescript
interface UserNotificationPreferences {
  userId: string;
  optin: boolean;                    // Master switch
  eventTypePreferences: Map<...>;    // Por tipo de evento
  channelPreferences: {              // Por canal
    email: boolean;
    webhook: boolean;
    inApp: boolean;
    slack: boolean;
  };
  rateLimit: {
    maxPerMinute: number;
    maxPerHour: number;
    quiet: boolean;                  // Modo silencioso
  };
  groupingEnabled: boolean;
  groupingWindowMs: number;
  updatedAt: Date;
}
```

### Padrões

```typescript
// Padrão global
optin: true
rateLimit.maxPerMinute: 5
rateLimit.maxPerHour: 30
groupingWindowMs: 300000 // 5 minutos

// Canais habilitados por padrão
email: true
inApp: true

// Canais desabilitados por padrão
webhook: false
slack: false

// Todos os event types habilitados por padrão
TEST_PASSED: true
TEST_FAILED: true
// etc...
```

## Analytics de Delivery

O sistema rastreia cada notificação entregue.

### Estrutura de Analytics

```typescript
interface DeliveryAnalytics {
  notificationId: string;
  userId: string;
  eventType: NotificationEventType;
  channel: "email" | "webhook" | "in-app" | "slack";
  deliveryStatus: DeliveryStatus;      // pending, sent, delivered, opened, clicked
  deliveryTimeMs?: number;              // Tempo de entrega em ms
  attemptCount: number;                 // Tentativas de entrega
  lastAttemptAt?: Date;
  openedAt?: Date;                      // Quando usuário abriu
  clickedAt?: Date;                     // Quando usuário clicou
  errorMessage?: string;
}
```

### Métricas Disponíveis

```typescript
// Por usuário
const stats = notifier.getDeliveryStats("user_456");
// {
//   totalSent: number,
//   totalDelivered: number,
//   totalFailed: number,
//   deliveryRate: number,              // Percentual
//   averageDeliveryTimeMs: number,
//   byChannel: {
//     email: { sent, delivered },
//     webhook: { sent, delivered },
//     ...
//   }
// }

// Histórico completo
const history = notifier.getNotificationHistory("user_456", 50);
// {
//   analytics: DeliveryAnalytics[],
//   summary: {
//     total: number,
//     delivered: number,
//     failed: number,
//     opened: number,
//     clicked: number
//   }
// }
```

## Templates de Notificação

Cada tipo de evento tem um template pré-definido:

```typescript
// PR_OPENED
{
  title: "New PR: <prTitle>",
  message: "<author> opened PR #<prNumber> in <repository>"
}

// AGENT_UPDATED
{
  title: "Agent Updated: <agentName>",
  message: "<agentName> (<agentCode>) was updated: <updateSummary>"
}

// TEST_FAILED
{
  title: "Test Failed: <testName>",
  message: "<failureCount> test(s) failed in <suite>. <errorSummary>"
}

// BUILD_FAILED
{
  title: "Build Failed",
  message: "Build failed: <errorSummary>"
}

// DEPLOYMENT_COMPLETED
{
  title: "Deployment Completed",
  message: "Successfully deployed to <environment>. Version: <version>"
}
```

## Integração com GitHub

### Exemplo: Processar eventos do GitHub

```typescript
import { Octokit } from "@octokit/rest";
import { InteligentNotifier, NotificationEventType } from "./services/notifications";

const notifier = getNotifier();
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

// Webhook handler
app.post("/webhooks/github", async (req, res) => {
  const { action, pull_request, repository } = req.body;

  if (action === "opened") {
    const event = {
      id: `github_pr_${pull_request.id}`,
      type: NotificationEventType.PR_OPENED,
      userId: process.env.USER_ID,
      timestamp: new Date(),
      priority: NotificationPriority.MEDIUM,
      data: {
        prNumber: pull_request.number,
        prTitle: pull_request.title,
        author: pull_request.user.login,
        repository: repository.name,
      },
      groupKey: `pr_${pull_request.number}`,
      metadata: {
        source: "github",
        tags: ["pr", repository.name],
      },
    };

    await notifier.addEvent(event);
  }

  res.sendStatus(200);
});
```

## Integração com Sistema de CI/CD

### Exemplo: Notificar falhas de teste

```typescript
// No seu pipeline CI/CD
const event = {
  id: `ci_test_${Date.now()}`,
  type: NotificationEventType.TEST_FAILED,
  userId: process.env.DEVELOPER_EMAIL,
  timestamp: new Date(),
  priority: NotificationPriority.HIGH,
  data: {
    testName: "MaestroRouter.test",
    suite: "src/services/__tests__",
    failureCount: 2,
    errorSummary: "Timeout in keyword matching",
  },
  groupKey: `test_suite_${buildNumber}`,
  metadata: {
    source: "ci",
    tags: ["test", "failed", `build_${buildNumber}`],
  },
};

await notifier.addEvent(event);
```

## Testes

Executar suite de testes:

```bash
npm test -- src/services/__tests__/notifications.test.ts
```

Executar exemplo:

```bash
npm run dev
# No arquivo do seu projeto:
import { runNotificationExamples } from "./services/notifications";
await runNotificationExamples();
```

## Performance

- **Busca de eventos**: O(1) por usuário
- **Agrupamento**: O(n) onde n = eventos em janela
- **Rate limiting**: O(1) com limpeza lazy
- **Analytics**: O(1) append, O(n) para histórico

## Considerações de Deployment

### Variáveis de Ambiente

```bash
# Email
SENDGRID_API_KEY=...
NOTIFICATION_EMAIL_FROM=notifications@mantaassociados.com

# Slack
SLACK_BOT_TOKEN=...
SLACK_WEBHOOK_URL=...

# Webhook
WEBHOOK_BASE_URL=https://example.com

# Rate limiting
NOTIF_RATE_LIMIT_PER_MINUTE=5
NOTIF_RATE_LIMIT_PER_HOUR=30

# Grouping
NOTIF_GROUPING_WINDOW_MS=300000  # 5 minutos
```

### Cleanup

Sempre chamar `destroy()` ao encerrar:

```typescript
const notifier = getNotifier();

// ... usar notifier ...

// Ao desligar
notifier.destroy();
```

## Roadmap

- [ ] Persistência em banco de dados
- [ ] Retry automático com backoff exponencial
- [ ] Padrões de notificação avançados (digest, coalescing)
- [ ] Integração com mais canais (Teams, Discord, SMS)
- [ ] Dashboard de analytics
- [ ] A/B testing de mensagens
- [ ] ML para otimizar timing de entrega

## Troubleshooting

### Notificações não estão sendo entregues

1. Verificar se usuário tem `optin: true`
2. Verificar se event type está habilitado
3. Verificar rate limit: `getRateLimitMetrics()`
4. Verificar preferences de canal

### Eventos sendo descartados

1. Verificar `getDeliveryAnalytics()` para erros
2. Verificar logs do sistema
3. Verificar configuração de preferências

### Agrupamento não funcionando

1. Verificar se `groupingEnabled: true`
2. Verificar se `groupKey` é consistente
3. Aguardar janela de agrupamento (padrão: 5 min)

## Referências

- [src/services/notifications.ts](../src/services/notifications.ts)
- [src/services/__tests__/notifications.test.ts](../src/services/__tests__/notifications.test.ts)
