/**
 * Health Dashboard — Sistema de monitoramento de saúde do sync
 * Versão: 1.0.0
 *
 * Recursos:
 * - Latência de sync (alvo < 5 min)
 * - Rastreamento de conflitos (resolvidos vs pendentes)
 * - Percentage de uptime (alvo > 99%)
 * - Status de entrega de webhooks
 * - Monitoramento de profundidade de fila
 */

/**
 * Status de saúde do sistema
 */
export enum HealthStatus {
  HEALTHY = "healthy",
  DEGRADED = "degraded",
  UNHEALTHY = "unhealthy",
}

/**
 * Status de entrega de webhook
 */
export enum WebhookDeliveryStatus {
  SUCCESS = "success",
  FAILED = "failed",
  PENDING = "pending",
  RETRYING = "retrying",
}

/**
 * Métrica de conflito
 */
export interface ConflictMetric {
  resolved: number;
  pending: number;
  totalSinceLastClear: number;
  lastResolvedAt?: Date;
  lastPendingAt?: Date;
}

/**
 * Métrica de latência de sync
 */
export interface SyncLatencyMetric {
  current: number; // em milissegundos
  average: number;
  peak: number;
  targetMs: number; // 5 min = 300000ms
  withinTarget: boolean;
  lastSyncAt?: Date;
}

/**
 * Métrica de uptime
 */
export interface UptimeMetric {
  percentage: number;
  targetPercentage: number;
  totalUptime: number; // em milissegundos
  totalDowntime: number;
  lastUptimeCheckAt?: Date;
  outages: UptimeOutage[];
}

/**
 * Registro de outage
 */
export interface UptimeOutage {
  startAt: Date;
  endAt?: Date;
  durationMs: number;
  reason?: string;
}

/**
 * Métrica de webhook
 */
export interface WebhookMetric {
  totalAttempts: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  successRate: number;
  pendingDeliveries: number;
  retryingDeliveries: number;
  lastDeliveryAt?: Date;
  averageDeliveryTimeMs: number;
}

/**
 * Métrica de fila
 */
export interface QueueMetric {
  currentDepth: number;
  maxDepth: number;
  averageDepth: number;
  highestPriority: number; // count de items críticos
  processingRate: number; // items/min
  estimatedDrainTimeMin: number;
}

/**
 * Snapshot completo de métricas
 */
export interface HealthMetrics {
  timestamp: Date;
  overallStatus: HealthStatus;
  syncLatency: SyncLatencyMetric;
  conflicts: ConflictMetric;
  uptime: UptimeMetric;
  webhooks: WebhookMetric;
  queue: QueueMetric;
  alerts: HealthAlert[];
}

/**
 * Alerta de saúde
 */
export interface HealthAlert {
  id: string;
  severity: "info" | "warning" | "critical";
  category: string;
  message: string;
  timestamp: Date;
  resolved?: boolean;
  resolvedAt?: Date;
}

/**
 * Status simplificado do dashboard
 */
export interface DashboardStatus {
  status: HealthStatus;
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

/**
 * HealthDashboard — Classe principal de monitoramento
 */
export class HealthDashboard {
  private syncLatencies: number[] = [];
  private conflicts: ConflictMetric;
  private outages: UptimeOutage[] = [];
  private webhookHistory: WebhookDeliveryEvent[] = [];
  private queueMetrics: QueueMetricsHistory[] = [];
  private alerts: Map<string, HealthAlert> = new Map();
  private lastHealthCheck: Date;
  private startTime: Date;
  private readonly maxHistorySize = 10000;
  private readonly syncLatencyTargetMs = 300000; // 5 minutos
  private readonly uptimeTarget = 99.0; // 99%

  constructor() {
    this.conflicts = {
      resolved: 0,
      pending: 0,
      totalSinceLastClear: 0,
    };
    this.startTime = new Date();
    this.lastHealthCheck = new Date();
  }

  /**
   * Registra uma latência de sync
   */
  public recordSyncLatency(latencyMs: number): void {
    this.syncLatencies.push(latencyMs);
    if (this.syncLatencies.length > this.maxHistorySize) {
      this.syncLatencies.shift();
    }

    // Verifica se latência excede alvo
    if (latencyMs > this.syncLatencyTargetMs) {
      this.addAlert(
        `sync_latency_high_${Date.now()}`,
        "warning",
        "sync_latency",
        `Latência de sync ${latencyMs}ms excede alvo de ${this.syncLatencyTargetMs}ms`
      );
    }
  }

  /**
   * Registra um conflito resolvido
   */
  public recordConflictResolved(): void {
    this.conflicts.resolved++;
    this.conflicts.totalSinceLastClear++;
    this.conflicts.lastResolvedAt = new Date();
  }

  /**
   * Registra um conflito pendente
   */
  public recordConflictPending(): void {
    this.conflicts.pending++;
    this.conflicts.totalSinceLastClear++;
    this.conflicts.lastPendingAt = new Date();

    // Alerta se há muitos conflitos pendentes
    if (this.conflicts.pending > 10) {
      this.addAlert(
        `conflicts_pending_high_${Date.now()}`,
        "warning",
        "conflicts",
        `${this.conflicts.pending} conflitos pendentes de resolução`
      );
    }
  }

  /**
   * Marca um conflito como resolvido
   */
  public resolveConflict(): void {
    if (this.conflicts.pending > 0) {
      this.conflicts.pending--;
      this.conflicts.resolved++;
      this.conflicts.lastResolvedAt = new Date();
    }
  }

  /**
   * Registra um outage
   */
  public recordOutage(reason?: string): void {
    const outage: UptimeOutage = {
      startAt: new Date(),
      durationMs: 0,
      reason,
    };
    this.outages.push(outage);

    this.addAlert(
      `outage_${Date.now()}`,
      "critical",
      "uptime",
      `Outage registrado: ${reason || "Motivo desconhecido"}`
    );
  }

  /**
   * Encerra o outage mais recente
   */
  public endOutage(): void {
    if (this.outages.length > 0) {
      const lastOutage = this.outages[this.outages.length - 1];
      if (!lastOutage.endAt) {
        lastOutage.endAt = new Date();
        lastOutage.durationMs = lastOutage.endAt.getTime() - lastOutage.startAt.getTime();
      }
    }
  }

  /**
   * Registra uma tentativa de entrega de webhook
   */
  public recordWebhookDeliveryAttempt(
    webhookId: string,
    status: WebhookDeliveryStatus,
    deliveryTimeMs: number
  ): void {
    const event: WebhookDeliveryEvent = {
      id: webhookId,
      status,
      deliveryTimeMs,
      timestamp: new Date(),
    };
    this.webhookHistory.push(event);

    if (this.webhookHistory.length > this.maxHistorySize) {
      this.webhookHistory.shift();
    }

    if (status === WebhookDeliveryStatus.FAILED) {
      this.addAlert(
        `webhook_failed_${webhookId}_${Date.now()}`,
        "warning",
        "webhooks",
        `Falha na entrega de webhook ${webhookId}`
      );
    }
  }

  /**
   * Registra profundidade da fila
   */
  public recordQueueDepth(
    depth: number,
    maxDepth: number,
    criticalCount: number = 0
  ): void {
    const metric: QueueMetricsHistory = {
      depth,
      maxDepth,
      criticalCount,
      timestamp: new Date(),
    };
    this.queueMetrics.push(metric);

    if (this.queueMetrics.length > this.maxHistorySize) {
      this.queueMetrics.shift();
    }

    // Alerta se fila está crescendo demais
    if (depth > maxDepth * 0.8) {
      this.addAlert(
        `queue_depth_high_${Date.now()}`,
        "warning",
        "queue",
        `Profundidade de fila alta: ${depth}/${maxDepth}`
      );
    }

    // Alerta se há items críticos acumulando
    if (criticalCount > 5) {
      this.addAlert(
        `queue_critical_items_${Date.now()}`,
        "critical",
        "queue",
        `${criticalCount} items críticos na fila aguardando processamento`
      );
    }
  }

  /**
   * Limpa conflitos (reset de contador)
   */
  public clearConflictHistory(): void {
    this.conflicts = {
      resolved: 0,
      pending: this.conflicts.pending, // mantém os pendentes
      totalSinceLastClear: 0,
    };
  }

  /**
   * Resolve todos os conflitos pendentes
   */
  public resolveAllConflicts(): void {
    if (this.conflicts.pending > 0) {
      this.conflicts.resolved += this.conflicts.pending;
      this.conflicts.pending = 0;
      this.conflicts.lastResolvedAt = new Date();
    }
  }

  /**
   * Obtém status simplificado do dashboard
   */
  public getStatus(): DashboardStatus {
    const now = new Date();
    this.lastHealthCheck = now;

    const syncLatencyMetric = this.calculateSyncLatency();
    const uptimeMetric = this.calculateUptime();
    const webhookMetric = this.calculateWebhookMetrics();
    const queueMetric = this.calculateQueueMetrics();

    // Determina status geral
    const overallStatus = this.determineOverallStatus(
      syncLatencyMetric,
      uptimeMetric,
      webhookMetric,
      queueMetric
    );

    // Filtra alertas não resolvidos
    const activeAlerts = Array.from(this.alerts.values()).filter(a => !a.resolved);

    return {
      status: overallStatus,
      summary: {
        syncLatencyMs: syncLatencyMetric.current,
        syncOnTarget: syncLatencyMetric.withinTarget,
        conflictsPending: this.conflicts.pending,
        uptimePercentage: uptimeMetric.percentage,
        webhookSuccessRate: webhookMetric.successRate,
        queueDepth: queueMetric.currentDepth,
      },
      alerts: activeAlerts,
      lastUpdate: now,
    };
  }

  /**
   * Obtém métricas detalhadas
   */
  public getMetrics(): HealthMetrics {
    const now = new Date();

    return {
      timestamp: now,
      overallStatus: this.determineOverallStatus(
        this.calculateSyncLatency(),
        this.calculateUptime(),
        this.calculateWebhookMetrics(),
        this.calculateQueueMetrics()
      ),
      syncLatency: this.calculateSyncLatency(),
      conflicts: { ...this.conflicts },
      uptime: this.calculateUptime(),
      webhooks: this.calculateWebhookMetrics(),
      queue: this.calculateQueueMetrics(),
      alerts: Array.from(this.alerts.values()).filter(a => !a.resolved),
    };
  }

  /**
   * Calcula métrica de latência de sync
   */
  private calculateSyncLatency(): SyncLatencyMetric {
    const current = this.syncLatencies.length > 0 ? this.syncLatencies[this.syncLatencies.length - 1] : 0;
    const average = this.syncLatencies.length > 0
      ? this.syncLatencies.reduce((a, b) => a + b, 0) / this.syncLatencies.length
      : 0;
    const peak = this.syncLatencies.length > 0 ? Math.max(...this.syncLatencies) : 0;

    return {
      current,
      average: Math.round(average),
      peak,
      targetMs: this.syncLatencyTargetMs,
      withinTarget: current <= this.syncLatencyTargetMs,
      lastSyncAt: this.syncLatencies.length > 0 ? new Date() : undefined,
    };
  }

  /**
   * Calcula métrica de uptime
   */
  private calculateUptime(): UptimeMetric {
    const totalDuration = new Date().getTime() - this.startTime.getTime();
    const totalDowntime = this.outages.reduce((sum, outage) => sum + outage.durationMs, 0);
    const totalUptime = totalDuration - totalDowntime;

    // Evita divisão por zero
    let percentage = 100;
    if (totalDuration > 0) {
      percentage = (totalUptime / totalDuration) * 100;
    }

    return {
      percentage: Math.max(0, Math.min(Math.round(percentage * 100) / 100, 100)),
      targetPercentage: this.uptimeTarget,
      totalUptime: Math.max(0, totalUptime),
      totalDowntime,
      lastUptimeCheckAt: new Date(),
      outages: this.outages,
    };
  }

  /**
   * Calcula métrica de webhooks
   */
  private calculateWebhookMetrics(): WebhookMetric {
    const successful = this.webhookHistory.filter(
      e => e.status === WebhookDeliveryStatus.SUCCESS
    ).length;
    const failed = this.webhookHistory.filter(
      e => e.status === WebhookDeliveryStatus.FAILED
    ).length;
    const pending = this.webhookHistory.filter(
      e => e.status === WebhookDeliveryStatus.PENDING
    ).length;
    const retrying = this.webhookHistory.filter(
      e => e.status === WebhookDeliveryStatus.RETRYING
    ).length;

    const total = this.webhookHistory.length;
    const successRate = total > 0 ? (successful / total) * 100 : 0;
    const avgDeliveryTime = total > 0
      ? this.webhookHistory.reduce((sum, e) => sum + e.deliveryTimeMs, 0) / total
      : 0;

    return {
      totalAttempts: total,
      successfulDeliveries: successful,
      failedDeliveries: failed,
      successRate: Math.round(successRate * 100) / 100,
      pendingDeliveries: pending,
      retryingDeliveries: retrying,
      lastDeliveryAt: this.webhookHistory.length > 0 ? this.webhookHistory[this.webhookHistory.length - 1].timestamp : undefined,
      averageDeliveryTimeMs: Math.round(avgDeliveryTime),
    };
  }

  /**
   * Calcula métrica de fila
   */
  private calculateQueueMetrics(): QueueMetric {
    const currentMetric = this.queueMetrics.length > 0
      ? this.queueMetrics[this.queueMetrics.length - 1]
      : { depth: 0, maxDepth: 0, criticalCount: 0, timestamp: new Date() };

    const avgDepth = this.queueMetrics.length > 0
      ? this.queueMetrics.reduce((sum, m) => sum + m.depth, 0) / this.queueMetrics.length
      : 0;

    // Calcula taxa de processamento (items/minuto)
    let processingRate = 0;
    if (this.queueMetrics.length > 1) {
      const recentMetrics = this.queueMetrics.slice(-60); // últimos 60 registros
      if (recentMetrics.length > 1) {
        const timeDiffMin = (recentMetrics[recentMetrics.length - 1].timestamp.getTime() -
          recentMetrics[0].timestamp.getTime()) / 60000;
        if (timeDiffMin > 0) {
          processingRate = (recentMetrics[0].depth - recentMetrics[recentMetrics.length - 1].depth) / timeDiffMin;
        }
      }
    }

    // Estima tempo de drenagem
    const estimatedDrainTimeMin = processingRate > 0
      ? Math.ceil(currentMetric.depth / processingRate)
      : -1;

    return {
      currentDepth: currentMetric.depth,
      maxDepth: currentMetric.maxDepth,
      averageDepth: Math.round(avgDepth),
      highestPriority: currentMetric.criticalCount,
      processingRate: Math.round(processingRate * 100) / 100,
      estimatedDrainTimeMin: estimatedDrainTimeMin >= 0 ? estimatedDrainTimeMin : 0,
    };
  }

  /**
   * Determina o status geral do sistema
   */
  private determineOverallStatus(
    syncLatency: SyncLatencyMetric,
    uptime: UptimeMetric,
    webhooks: WebhookMetric,
    queue: QueueMetric
  ): HealthStatus {
    const criticalConditions = [
      !syncLatency.withinTarget, // Latência acima do alvo
      uptime.percentage < 95, // Uptime muito baixo
      webhooks.successRate < 90, // Taxa de sucesso baixa
      queue.currentDepth > queue.maxDepth * 0.9, // Fila quase cheia
    ];

    const warningConditions = [
      syncLatency.current > this.syncLatencyTargetMs * 0.8, // Latência perto do alvo
      uptime.percentage < this.uptimeTarget, // Uptime abaixo do alvo
      webhooks.successRate < 95, // Taxa de sucesso abaixo do ideal
      queue.currentDepth > queue.maxDepth * 0.7, // Fila em nível de alerta
    ];

    const criticalCount = criticalConditions.filter(Boolean).length;
    const warningCount = warningConditions.filter(Boolean).length;

    if (criticalCount > 0) {
      return HealthStatus.UNHEALTHY;
    } else if (warningCount > 1) {
      return HealthStatus.DEGRADED;
    }
    return HealthStatus.HEALTHY;
  }

  /**
   * Adiciona um alerta
   */
  private addAlert(
    id: string,
    severity: "info" | "warning" | "critical",
    category: string,
    message: string
  ): void {
    if (!this.alerts.has(id)) {
      this.alerts.set(id, {
        id,
        severity,
        category,
        message,
        timestamp: new Date(),
      });
    }
  }

  /**
   * Marca um alerta como resolvido
   */
  public resolveAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = new Date();
    }
  }

  /**
   * Limpa alertas resolvidos
   */
  public clearResolvedAlerts(): void {
    Array.from(this.alerts.keys()).forEach(key => {
      const alert = this.alerts.get(key);
      if (alert?.resolved) {
        this.alerts.delete(key);
      }
    });
  }

  /**
   * Exporta relatório JSON
   */
  public exportReport(): string {
    const metrics = this.getMetrics();
    return JSON.stringify(metrics, null, 2);
  }

  /**
   * Reseta todas as métricas (uso com cuidado)
   */
  public reset(): void {
    this.syncLatencies = [];
    this.conflicts = { resolved: 0, pending: 0, totalSinceLastClear: 0 };
    this.outages = [];
    this.webhookHistory = [];
    this.queueMetrics = [];
    this.alerts.clear();
    this.startTime = new Date();
    this.lastHealthCheck = new Date();
  }
}

/**
 * Evento de entrega de webhook (interno)
 */
interface WebhookDeliveryEvent {
  id: string;
  status: WebhookDeliveryStatus;
  deliveryTimeMs: number;
  timestamp: Date;
}

/**
 * Registro histórico de métrica de fila (interno)
 */
interface QueueMetricsHistory {
  depth: number;
  maxDepth: number;
  criticalCount: number;
  timestamp: Date;
}

/**
 * Factory para criar instância singleton
 */
let healthDashboardInstance: HealthDashboard | null = null;

export function getHealthDashboard(): HealthDashboard {
  if (!healthDashboardInstance) {
    healthDashboardInstance = new HealthDashboard();
  }
  return healthDashboardInstance;
}

export function createHealthDashboard(): HealthDashboard {
  return new HealthDashboard();
}
