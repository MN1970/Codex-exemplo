/**
 * Notifications Service — Sistema inteligente de notificações com agrupamento
 * Versão: 1.0.0
 *
 * Recursos:
 * - InteligentNotifier: agrupa eventos por relevância
 * - Templates de notificação (PR, agent updates, test failures)
 * - Rate limiting: max 5 notificações/minuto por usuário
 * - Preferências do usuário: optin/optout por tipo
 * - Analytics: delivery tracking e métricas
 */

/**
 * Tipos de eventos suportados
 */
export enum NotificationEventType {
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

/**
 * Nível de prioridade de notificação
 */
export enum NotificationPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

/**
 * Status de entrega da notificação
 */
export enum DeliveryStatus {
  PENDING = "pending",
  SENT = "sent",
  FAILED = "failed",
  DELIVERED = "delivered",
  OPENED = "opened",
  CLICKED = "clicked",
}

/**
 * Interface para um evento de notificação
 */
export interface NotificationEvent {
  id: string;
  type: NotificationEventType;
  userId: string;
  timestamp: Date;
  priority: NotificationPriority;
  data: Record<string, unknown>;
  groupKey: string; // Chave para agrupamento de eventos relacionados
  metadata?: {
    source?: string; // "github", "system", "agent", etc
    tags?: string[];
    relatedEvents?: string[]; // IDs de eventos relacionados
  };
}

/**
 * Interface para uma notificação gerada
 */
export interface Notification {
  id: string;
  userId: string;
  eventIds: string[]; // Eventos agrupados nesta notificação
  type: NotificationEventType;
  title: string;
  message: string;
  priority: NotificationPriority;
  createdAt: Date;
  sentAt?: Date;
  deliveryStatus: DeliveryStatus;
  channel: "email" | "webhook" | "in-app" | "slack";
  metadata?: {
    actionUrl?: string;
    actionLabel?: string;
    groupCount?: number; // Quantos eventos foram agrupados
    aggregatedData?: Record<string, unknown>;
  };
}

/**
 * Interface para preferências do usuário
 */
export interface UserNotificationPreferences {
  userId: string;
  optin: boolean; // Master switch
  eventTypePreferences: Map<NotificationEventType, boolean>;
  channelPreferences: {
    email: boolean;
    webhook: boolean;
    inApp: boolean;
    slack: boolean;
  };
  rateLimit: {
    maxPerMinute: number;
    maxPerHour: number;
    quiet: boolean; // Modo silencioso
  };
  groupingEnabled: boolean;
  groupingWindowMs: number; // Janela de agrupamento em ms
  updatedAt: Date;
}

/**
 * Interface para analytics de delivery
 */
export interface DeliveryAnalytics {
  notificationId: string;
  userId: string;
  eventType: NotificationEventType;
  channel: "email" | "webhook" | "in-app" | "slack";
  deliveryStatus: DeliveryStatus;
  deliveryTimeMs?: number;
  attemptCount: number;
  lastAttemptAt?: Date;
  openedAt?: Date;
  clickedAt?: Date;
  errorMessage?: string;
}

/**
 * Templates de notificação por tipo de evento
 */
const NOTIFICATION_TEMPLATES: Record<
  NotificationEventType,
  (data: Record<string, unknown>) => { title: string; message: string }
> = {
  [NotificationEventType.PR_OPENED]: (data) => ({
    title: `New PR: ${data.prTitle || "Untitled"}`,
    message: `${data.author || "A developer"} opened PR #${data.prNumber} in ${data.repository || "repository"}`,
  }),
  [NotificationEventType.PR_MERGED]: (data) => ({
    title: `PR Merged: ${data.prTitle || "Untitled"}`,
    message: `PR #${data.prNumber} was merged into ${data.targetBranch || "main"} by ${data.mergedBy || "someone"}`,
  }),
  [NotificationEventType.PR_REVIEW_REQUESTED]: (data) => ({
    title: `Review Requested: ${data.prTitle || "Untitled"}`,
    message: `${data.requester || "Someone"} requested your review on PR #${data.prNumber}`,
  }),
  [NotificationEventType.AGENT_UPDATED]: (data) => ({
    title: `Agent Updated: ${data.agentName || "Unknown"}`,
    message: `${data.agentName || "Agent"} (${data.agentCode || "N/A"}) was updated: ${data.updateSummary || "No details"}`,
  }),
  [NotificationEventType.AGENT_DEPLOYED]: (data) => ({
    title: `Agent Deployed: ${data.agentName || "Unknown"}`,
    message: `${data.agentName || "Agent"} deployed to ${data.environment || "production"} at ${data.deploymentTime || "now"}`,
  }),
  [NotificationEventType.TEST_FAILED]: (data) => ({
    title: `Test Failed: ${data.testName || "Unknown test"}`,
    message: `${data.failureCount || 1} test(s) failed in ${data.suite || "test suite"}. ${data.errorSummary || ""}`,
  }),
  [NotificationEventType.TEST_PASSED]: (data) => ({
    title: `Tests Passed: ${data.suite || "Test suite"}`,
    message: `All ${data.totalTests || 0} tests passed successfully`,
  }),
  [NotificationEventType.BUILD_FAILED]: (data) => ({
    title: `Build Failed`,
    message: `Build failed: ${data.errorSummary || "See logs for details"}`,
  }),
  [NotificationEventType.BUILD_SUCCESS]: (data) => ({
    title: `Build Successful`,
    message: `Build completed successfully in ${data.buildTimeMs || "unknown"}ms`,
  }),
  [NotificationEventType.DEPLOYMENT_STARTED]: (data) => ({
    title: `Deployment Started`,
    message: `Deployment to ${data.environment || "environment"} started for ${data.version || "version"}`,
  }),
  [NotificationEventType.DEPLOYMENT_COMPLETED]: (data) => ({
    title: `Deployment Completed`,
    message: `Successfully deployed to ${data.environment || "environment"}. Version: ${data.version || "unknown"}`,
  }),
  [NotificationEventType.SKILL_ADDED]: (data) => ({
    title: `Skill Added: ${data.skillName || "Unknown"}`,
    message: `New skill "${data.skillName || "Unknown"}" is now available`,
  }),
  [NotificationEventType.SKILL_DEPRECATED]: (data) => ({
    title: `Skill Deprecated: ${data.skillName || "Unknown"}`,
    message: `Skill "${data.skillName || "Unknown"}" will be deprecated on ${data.deprecationDate || "TBD"}`,
  }),
};

/**
 * Calcula a prioridade baseada no tipo de evento
 */
function getPriorityForEventType(eventType: NotificationEventType): NotificationPriority {
  const priorityMap: Record<NotificationEventType, NotificationPriority> = {
    [NotificationEventType.PR_OPENED]: NotificationPriority.MEDIUM,
    [NotificationEventType.PR_MERGED]: NotificationPriority.MEDIUM,
    [NotificationEventType.PR_REVIEW_REQUESTED]: NotificationPriority.HIGH,
    [NotificationEventType.AGENT_UPDATED]: NotificationPriority.MEDIUM,
    [NotificationEventType.AGENT_DEPLOYED]: NotificationPriority.HIGH,
    [NotificationEventType.TEST_FAILED]: NotificationPriority.HIGH,
    [NotificationEventType.TEST_PASSED]: NotificationPriority.LOW,
    [NotificationEventType.BUILD_FAILED]: NotificationPriority.CRITICAL,
    [NotificationEventType.BUILD_SUCCESS]: NotificationPriority.LOW,
    [NotificationEventType.DEPLOYMENT_STARTED]: NotificationPriority.HIGH,
    [NotificationEventType.DEPLOYMENT_COMPLETED]: NotificationPriority.HIGH,
    [NotificationEventType.SKILL_ADDED]: NotificationPriority.MEDIUM,
    [NotificationEventType.SKILL_DEPRECATED]: NotificationPriority.HIGH,
  };
  return priorityMap[eventType] || NotificationPriority.MEDIUM;
}

/**
 * Monitor de Rate Limiting por usuário
 */
class RateLimitMonitor {
  private userEventTimestamps: Map<string, Date[]> = new Map();
  private maxPerMinute: number = 5;

  setMaxPerMinute(max: number): void {
    this.maxPerMinute = max;
  }

  /**
   * Verifica se o usuário excedeu o rate limit
   * Retorna true se evento pode ser processado, false se excede limite
   */
  checkRateLimit(userId: string): boolean {
    const now = new Date();
    const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);

    if (!this.userEventTimestamps.has(userId)) {
      this.userEventTimestamps.set(userId, []);
    }

    const timestamps = this.userEventTimestamps.get(userId)!;

    // Remove timestamps antigos (> 1 minuto)
    const recentTimestamps = timestamps.filter((ts) => ts > oneMinuteAgo);
    this.userEventTimestamps.set(userId, recentTimestamps);

    // Verifica se pode adicionar novo evento
    if (recentTimestamps.length < this.maxPerMinute) {
      recentTimestamps.push(now);
      return true;
    }

    return false;
  }

  /**
   * Retorna métrica de events/min do usuário
   */
  getMetrics(userId: string): { eventsLastMinute: number; throttled: boolean } {
    const now = new Date();
    const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);

    const timestamps = this.userEventTimestamps.get(userId) || [];
    const recentTimestamps = timestamps.filter((ts) => ts > oneMinuteAgo);

    return {
      eventsLastMinute: recentTimestamps.length,
      throttled: recentTimestamps.length >= this.maxPerMinute,
    };
  }
}

/**
 * Intelligent Notifier — Agrupa eventos relacionados por relevância
 */
export class InteligentNotifier {
  private eventQueue: Map<string, NotificationEvent[]> = new Map();
  private userPreferences: Map<string, UserNotificationPreferences> = new Map();
  private deliveryAnalytics: Map<string, DeliveryAnalytics[]> = new Map();
  private rateLimitMonitor = new RateLimitMonitor();
  private groupingWindowMs: number = 300000; // 5 minutos
  private groupingTimeouts: Map<string, NodeJS.Timeout> = new Map();

  constructor() {
    this.initializeDefaultPreferences();
  }

  /**
   * Inicializa preferências padrão para novo usuário
   */
  private initializeDefaultPreferences(): void {
    // Será preenchido conforme usuários são criados
  }

  /**
   * Registra um novo evento no sistema
   */
  public async addEvent(event: NotificationEvent): Promise<void> {
    // Verifica rate limit
    if (!this.rateLimitMonitor.checkRateLimit(event.userId)) {
      console.warn(
        `⚠️ Rate limit exceeded for user ${event.userId}. Event ${event.id} throttled.`
      );
      return;
    }

    // Obtém preferências do usuário
    const preferences = this.getUserPreferences(event.userId);

    // Verifica se usuário tem optin
    if (!preferences.optin) {
      console.log(
        `📵 User ${event.userId} has opted out. Event ${event.id} dropped.`
      );
      return;
    }

    // Verifica se evento type está habilitado
    const eventEnabled = preferences.eventTypePreferences.get(event.type) ?? true;
    if (!eventEnabled) {
      console.log(
        `📵 Event type ${event.type} is disabled for user ${event.userId}`
      );
      return;
    }

    // Adiciona evento à fila
    if (!this.eventQueue.has(event.userId)) {
      this.eventQueue.set(event.userId, []);
    }
    this.eventQueue.get(event.userId)!.push(event);

    console.log(
      `✅ Event ${event.id} (${event.type}) added for user ${event.userId}`
    );

    // Agenda processamento do grupo se não existir timeout ativo
    if (!this.groupingTimeouts.has(event.userId)) {
      this.scheduleGroupProcessing(event.userId);
    }
  }

  /**
   * Agenda o processamento agrupado de eventos
   */
  private scheduleGroupProcessing(userId: string): void {
    const timeout = setTimeout(async () => {
      const notifications = await this.processUserEventGroup(userId);
      console.log(
        `📨 Processed ${notifications.length} notification(s) for user ${userId}`
      );
      this.groupingTimeouts.delete(userId);
    }, this.groupingWindowMs);

    this.groupingTimeouts.set(userId, timeout);
  }

  /**
   * Processa e agrupa eventos de um usuário
   */
  private async processUserEventGroup(userId: string): Promise<Notification[]> {
    const events = this.eventQueue.get(userId) || [];
    if (events.length === 0) {
      return [];
    }

    const notifications: Notification[] = [];
    const preferences = this.getUserPreferences(userId);

    // Agrupa eventos por groupKey
    const groupedEvents = new Map<string, NotificationEvent[]>();
    for (const event of events) {
      if (!groupedEvents.has(event.groupKey)) {
        groupedEvents.set(event.groupKey, []);
      }
      groupedEvents.get(event.groupKey)!.push(event);
    }

    // Cria notificação para cada grupo
    for (const [groupKey, groupEvents] of groupedEvents) {
      const notification = this.createGroupNotification(groupEvents, userId);
      if (notification) {
        notifications.push(notification);

        // Envia notificação através de canais habilitados
        await this.deliverNotification(notification, preferences);
      }
    }

    // Limpa fila do usuário
    this.eventQueue.delete(userId);

    return notifications;
  }

  /**
   * Cria uma notificação agregada para um grupo de eventos
   */
  private createGroupNotification(
    events: NotificationEvent[],
    userId: string
  ): Notification | null {
    if (events.length === 0) return null;

    // Ordena por prioridade e timestamp
    const sorted = [...events].sort((a, b) => {
      const priorityOrder = {
        [NotificationPriority.CRITICAL]: 0,
        [NotificationPriority.HIGH]: 1,
        [NotificationPriority.MEDIUM]: 2,
        [NotificationPriority.LOW]: 3,
      };
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      return priorityDiff !== 0
        ? priorityDiff
        : b.timestamp.getTime() - a.timestamp.getTime();
    });

    const primaryEvent = sorted[0];
    const template = NOTIFICATION_TEMPLATES[primaryEvent.type];
    const { title, message } = template(primaryEvent.data);

    const notification: Notification = {
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId,
      eventIds: events.map((e) => e.id),
      type: primaryEvent.type,
      title,
      message:
        events.length > 1 ? `${message} (+${events.length - 1} more)` : message,
      priority: primaryEvent.priority,
      createdAt: new Date(),
      deliveryStatus: DeliveryStatus.PENDING,
      channel: this.selectChannel(userId),
      metadata: {
        groupCount: events.length,
        aggregatedData: {
          eventTypes: [...new Set(events.map((e) => e.type))],
          tags: [
            ...new Set(events.flatMap((e) => e.metadata?.tags || [])),
          ],
        },
      },
    };

    return notification;
  }

  /**
   * Seleciona o melhor canal para entrega
   */
  private selectChannel(
    userId: string
  ): "email" | "webhook" | "in-app" | "slack" {
    const preferences = this.getUserPreferences(userId);

    if (preferences.channelPreferences.slack) return "slack";
    if (preferences.channelPreferences.email) return "email";
    if (preferences.channelPreferences.webhook) return "webhook";
    return "in-app";
  }

  /**
   * Entrega a notificação através do canal configurado
   */
  private async deliverNotification(
    notification: Notification,
    preferences: UserNotificationPreferences
  ): Promise<void> {
    const analytics: DeliveryAnalytics = {
      notificationId: notification.id,
      userId: notification.userId,
      eventType: notification.type,
      channel: notification.channel,
      deliveryStatus: DeliveryStatus.PENDING,
      attemptCount: 0,
    };

    try {
      const startTime = Date.now();

      switch (notification.channel) {
        case "email":
          await this.deliverViaEmail(notification);
          break;
        case "webhook":
          await this.deliverViaWebhook(notification);
          break;
        case "slack":
          await this.deliverViaSlack(notification);
          break;
        case "in-app":
          await this.deliverInApp(notification);
          break;
      }

      analytics.deliveryStatus = DeliveryStatus.DELIVERED;
      analytics.deliveryTimeMs = Date.now() - startTime;
      analytics.lastAttemptAt = new Date();
      analytics.attemptCount = 1;

      notification.sentAt = new Date();
      notification.deliveryStatus = DeliveryStatus.DELIVERED;

      console.log(
        `✅ Notification ${notification.id} delivered via ${notification.channel}`
      );
    } catch (error) {
      analytics.deliveryStatus = DeliveryStatus.FAILED;
      analytics.errorMessage = String(error);
      analytics.lastAttemptAt = new Date();
      analytics.attemptCount = 1;
      notification.deliveryStatus = DeliveryStatus.FAILED;

      console.error(
        `❌ Failed to deliver notification ${notification.id}:`,
        error
      );
    }

    // Registra analytics
    if (!this.deliveryAnalytics.has(notification.userId)) {
      this.deliveryAnalytics.set(notification.userId, []);
    }
    this.deliveryAnalytics.get(notification.userId)!.push(analytics);
  }

  /**
   * Entrega via email
   */
  private async deliverViaEmail(notification: Notification): Promise<void> {
    // Simulação de entrega via email
    console.log(`📧 Sending email to user ${notification.userId}...`);
    // TODO: Integrar com provedor de email real (SendGrid, AWS SES, etc)
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  /**
   * Entrega via Webhook
   */
  private async deliverViaWebhook(notification: Notification): Promise<void> {
    const preferences = this.getUserPreferences(notification.userId);
    const webhookUrl = preferences.channelPreferences.webhook
      ? `https://example.com/webhooks/notifications/${notification.userId}`
      : null;

    if (!webhookUrl) {
      throw new Error("Webhook URL not configured");
    }

    console.log(`🔗 Sending webhook to ${webhookUrl}...`);
    // TODO: Integrar com HTTP client real
    await new Promise((resolve) => setTimeout(resolve, 150));
  }

  /**
   * Entrega via Slack
   */
  private async deliverViaSlack(notification: Notification): Promise<void> {
    console.log(
      `💬 Sending Slack message to user ${notification.userId}...`
    );
    // TODO: Integrar com Slack API
    await new Promise((resolve) => setTimeout(resolve, 200));
  }

  /**
   * Entrega in-app (armazena no banco)
   */
  private async deliverInApp(notification: Notification): Promise<void> {
    console.log(
      `💾 Storing in-app notification for user ${notification.userId}...`
    );
    // TODO: Armazenar em banco de dados
    await new Promise((resolve) => setTimeout(resolve, 50));
  }

  /**
   * Obtém ou cria preferências do usuário
   */
  public getUserPreferences(
    userId: string
  ): UserNotificationPreferences {
    if (!this.userPreferences.has(userId)) {
      this.userPreferences.set(userId, {
        userId,
        optin: true,
        eventTypePreferences: new Map(
          Object.values(NotificationEventType).map((type) => [type, true])
        ),
        channelPreferences: {
          email: true,
          webhook: false,
          inApp: true,
          slack: false,
        },
        rateLimit: {
          maxPerMinute: 5,
          maxPerHour: 30,
          quiet: false,
        },
        groupingEnabled: true,
        groupingWindowMs: 300000, // 5 minutos
        updatedAt: new Date(),
      });
    }
    return this.userPreferences.get(userId)!;
  }

  /**
   * Atualiza preferências do usuário
   */
  public setUserPreferences(
    userId: string,
    preferences: Partial<UserNotificationPreferences>
  ): void {
    const current = this.getUserPreferences(userId);
    const updated = { ...current, ...preferences, updatedAt: new Date() };
    this.userPreferences.set(userId, updated);
    console.log(`✅ Preferences updated for user ${userId}`);
  }

  /**
   * Habilita/desabilita notificações para um tipo de evento
   */
  public setEventTypePreference(
    userId: string,
    eventType: NotificationEventType,
    enabled: boolean
  ): void {
    const preferences = this.getUserPreferences(userId);
    preferences.eventTypePreferences.set(eventType, enabled);
    console.log(
      `✅ Event type ${eventType} ${enabled ? "enabled" : "disabled"} for user ${userId}`
    );
  }

  /**
   * Retorna analytics de delivery para um usuário
   */
  public getDeliveryAnalytics(userId: string): DeliveryAnalytics[] {
    return this.deliveryAnalytics.get(userId) || [];
  }

  /**
   * Retorna estatísticas agregadas de delivery
   */
  public getDeliveryStats(userId: string): {
    totalSent: number;
    totalDelivered: number;
    totalFailed: number;
    deliveryRate: number;
    averageDeliveryTimeMs: number;
    byChannel: Record<string, { sent: number; delivered: number }>;
  } {
    const analytics = this.getDeliveryAnalytics(userId);

    const stats = {
      totalSent: analytics.length,
      totalDelivered: analytics.filter(
        (a) => a.deliveryStatus === DeliveryStatus.DELIVERED
      ).length,
      totalFailed: analytics.filter(
        (a) => a.deliveryStatus === DeliveryStatus.FAILED
      ).length,
      deliveryRate: 0,
      averageDeliveryTimeMs: 0,
      byChannel: {} as Record<string, { sent: number; delivered: number }>,
    };

    // Calcula taxa de entrega
    if (stats.totalSent > 0) {
      stats.deliveryRate = (stats.totalDelivered / stats.totalSent) * 100;
    }

    // Calcula tempo médio de entrega
    const deliveredWithTime = analytics.filter(
      (a) => a.deliveryStatus === DeliveryStatus.DELIVERED && a.deliveryTimeMs
    );
    if (deliveredWithTime.length > 0) {
      const totalTime = deliveredWithTime.reduce(
        (sum, a) => sum + (a.deliveryTimeMs || 0),
        0
      );
      stats.averageDeliveryTimeMs = totalTime / deliveredWithTime.length;
    }

    // Estatísticas por canal
    for (const channel of ["email", "webhook", "in-app", "slack"]) {
      const channelAnalytics = analytics.filter((a) => a.channel === channel);
      stats.byChannel[channel] = {
        sent: channelAnalytics.length,
        delivered: channelAnalytics.filter(
          (a) => a.deliveryStatus === DeliveryStatus.DELIVERED
        ).length,
      };
    }

    return stats;
  }

  /**
   * Retorna métricas de rate limiting
   */
  public getRateLimitMetrics(userId: string): {
    eventsLastMinute: number;
    throttled: boolean;
  } {
    return this.rateLimitMonitor.getMetrics(userId);
  }

  /**
   * Marca notificação como aberta
   */
  public markAsOpened(notificationId: string, userId: string): void {
    const analytics = this.deliveryAnalytics.get(userId) || [];
    const record = analytics.find((a) => a.notificationId === notificationId);
    if (record) {
      record.deliveryStatus = DeliveryStatus.OPENED;
      record.openedAt = new Date();
      console.log(
        `👁️ Notification ${notificationId} marked as opened for user ${userId}`
      );
    }
  }

  /**
   * Marca notificação como clicada
   */
  public markAsClicked(notificationId: string, userId: string): void {
    const analytics = this.deliveryAnalytics.get(userId) || [];
    const record = analytics.find((a) => a.notificationId === notificationId);
    if (record) {
      record.deliveryStatus = DeliveryStatus.CLICKED;
      record.clickedAt = new Date();
      console.log(
        `🖱️ Notification ${notificationId} marked as clicked for user ${userId}`
      );
    }
  }

  /**
   * Retorna histórico de notificações de um usuário
   */
  public getNotificationHistory(userId: string, limit: number = 50): {
    analytics: DeliveryAnalytics[];
    summary: {
      total: number;
      delivered: number;
      failed: number;
      opened: number;
      clicked: number;
    };
  } {
    const analytics = this.deliveryAnalytics
      .get(userId)
      ?.slice(-limit) || [];

    return {
      analytics,
      summary: {
        total: analytics.length,
        delivered: analytics.filter(
          (a) => a.deliveryStatus === DeliveryStatus.DELIVERED
        ).length,
        failed: analytics.filter(
          (a) => a.deliveryStatus === DeliveryStatus.FAILED
        ).length,
        opened: analytics.filter(
          (a) => a.deliveryStatus === DeliveryStatus.OPENED
        ).length,
        clicked: analytics.filter(
          (a) => a.deliveryStatus === DeliveryStatus.CLICKED
        ).length,
      },
    };
  }

  /**
   * Limpa timeouts pendentes
   */
  public destroy(): void {
    for (const timeout of this.groupingTimeouts.values()) {
      clearTimeout(timeout);
    }
    this.groupingTimeouts.clear();
    console.log("🧹 NotificationService destroyed");
  }
}

/**
 * Factory para criar instância singleton do notificador
 */
let notifierInstance: InteligentNotifier | null = null;

export function getNotifier(): InteligentNotifier {
  if (!notifierInstance) {
    notifierInstance = new InteligentNotifier();
  }
  return notifierInstance;
}

/**
 * Exemplo de uso e testes
 */
export async function runNotificationExamples(): Promise<void> {
  const notifier = getNotifier();

  const userId = "user_123";

  // Configura preferências do usuário
  notifier.setUserPreferences(userId, {
    optin: true,
    channelPreferences: {
      email: true,
      webhook: false,
      inApp: true,
      slack: true,
    },
  });

  console.log("\n=== NOTIFICATION SERVICE EXAMPLES ===\n");

  // Exemplo 1: PR aberto
  const prEvent: NotificationEvent = {
    id: `evt_${Date.now()}_1`,
    type: NotificationEventType.PR_OPENED,
    userId,
    timestamp: new Date(),
    priority: NotificationPriority.MEDIUM,
    data: {
      prNumber: 123,
      prTitle: "Add notifications service",
      author: "john_doe",
      repository: "codex-exemplo",
    },
    groupKey: "pr_group_123",
    metadata: {
      source: "github",
      tags: ["feature", "notifications"],
    },
  };

  // Exemplo 2: Agent atualizado
  const agentEvent: NotificationEvent = {
    id: `evt_${Date.now()}_2`,
    type: NotificationEventType.AGENT_UPDATED,
    userId,
    timestamp: new Date(),
    priority: NotificationPriority.MEDIUM,
    data: {
      agentName: "agente-saneamento",
      agentCode: "Manta 03-S8",
      updateSummary: "Updated keyword weights for better routing",
    },
    groupKey: "agent_group_s8",
    metadata: {
      source: "system",
      tags: ["agent", "update"],
    },
  };

  // Exemplo 3: Teste falhou
  const testEvent: NotificationEvent = {
    id: `evt_${Date.now()}_3`,
    type: NotificationEventType.TEST_FAILED,
    userId,
    timestamp: new Date(),
    priority: NotificationPriority.HIGH,
    data: {
      testName: "MaestroRouter.test",
      suite: "src/services/__tests__",
      failureCount: 2,
      errorSummary: "Timeout in keyword matching",
    },
    groupKey: "test_group_maestro",
    metadata: {
      source: "ci",
      tags: ["test", "failed"],
    },
  };

  console.log("📝 Adding events to notification system...\n");
  await notifier.addEvent(prEvent);
  await notifier.addEvent(agentEvent);
  await notifier.addEvent(testEvent);

  // Aguarda processamento
  console.log("⏳ Waiting for grouping window to process...\n");
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Mostra analytics
  const stats = notifier.getDeliveryStats(userId);
  console.log("\n📊 Delivery Statistics:");
  console.log(`   Total sent: ${stats.totalSent}`);
  console.log(`   Delivered: ${stats.totalDelivered}`);
  console.log(`   Failed: ${stats.totalFailed}`);
  console.log(`   Delivery rate: ${stats.deliveryRate.toFixed(1)}%`);
  console.log(
    `   Average delivery time: ${stats.averageDeliveryTimeMs.toFixed(0)}ms`
  );

  console.log("\n📈 By Channel:");
  for (const [channel, data] of Object.entries(stats.byChannel)) {
    console.log(`   ${channel}: ${data.sent} sent, ${data.delivered} delivered`);
  }

  // Mostra rate limit
  const rateLimitMetrics = notifier.getRateLimitMetrics(userId);
  console.log("\n⏱️ Rate Limiting:");
  console.log(
    `   Events last minute: ${rateLimitMetrics.eventsLastMinute}`
  );
  console.log(
    `   Throttled: ${rateLimitMetrics.throttled ? "Yes" : "No"}`
  );

  // Mostra histórico
  const history = notifier.getNotificationHistory(userId);
  console.log("\n📋 Notification History:");
  console.log(`   Total: ${history.summary.total}`);
  console.log(`   Delivered: ${history.summary.delivered}`);
  console.log(`   Opened: ${history.summary.opened}`);
  console.log(`   Clicked: ${history.summary.clicked}`);
}
