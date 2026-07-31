/**
 * Monitoring & Observability Service
 * Versão: 1.0.0
 *
 * Recursos:
 * - Prometheus metrics (latency, success_rate, queue_depth)
 * - Structured logging com Pino + JSON
 * - Distributed tracing ready (OpenTelemetry)
 * - Alert manager (Slack): high error rate, timeout, stale sync
 * - Dashboard queries e metricas exportáveis
 */

import pino, { Logger } from "pino";
import { v4 as uuidv4 } from "uuid";

/**
 * Tipos de métricas
 */
export enum MetricType {
  COUNTER = "counter",
  GAUGE = "gauge",
  HISTOGRAM = "histogram",
  SUMMARY = "summary",
}

/**
 * Níveis de severidade para alertas
 */
export enum AlertSeverity {
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  CRITICAL = "critical",
}

/**
 * Interface para uma métrica individual
 */
export interface Metric {
  name: string;
  type: MetricType;
  value: number;
  timestamp: Date;
  labels?: Record<string, string>;
  unit?: string;
}

/**
 * Interface para agregações de métricas
 */
export interface MetricAggregation {
  name: string;
  count: number;
  sum: number;
  min: number;
  max: number;
  mean: number;
  p50: number;
  p95: number;
  p99: number;
  timestamp: Date;
}

/**
 * Interface para um alerta
 */
export interface Alert {
  id: string;
  name: string;
  severity: AlertSeverity;
  message: string;
  metricName: string;
  threshold: number;
  currentValue: number;
  timestamp: Date;
  resolved?: boolean;
  resolvedAt?: Date;
}

/**
 * Interface para contexto de rastreamento distribuído
 */
export interface TraceContext {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  flags: number;
}

/**
 * Interface para eventos estruturados
 */
export interface StructuredEvent {
  id: string;
  name: string;
  level: "debug" | "info" | "warn" | "error";
  timestamp: Date;
  duration?: number;
  metadata: Record<string, unknown>;
  traceContext?: TraceContext;
  tags?: string[];
}

/**
 * Configurable alert rules
 */
export interface AlertRule {
  id: string;
  name: string;
  metricName: string;
  operator: ">" | "<" | "==" | "!=" | ">=" | "<=";
  threshold: number;
  severity: AlertSeverity;
  window?: number; // milliseconds
  enabled: boolean;
  slackWebhook?: string;
  channels?: string[]; // slack channels
}

/**
 * Classe para coleta e gerenciamento de métricas Prometheus-style
 */
export class MetricsCollector {
  private metrics: Map<string, Metric[]> = new Map();
  private aggregations: Map<string, MetricAggregation> = new Map();
  private counters: Map<string, number> = new Map();
  private gauges: Map<string, number> = new Map();
  private histograms: Map<string, number[]> = new Map();
  private readonly maxMetricsPerName = 10000;
  private logger: Logger;

  constructor(logger: Logger) {
    this.logger = logger;
  }

  /**
   * Incrementa um contador
   */
  incrementCounter(
    name: string,
    value: number = 1,
    labels?: Record<string, string>
  ): void {
    const key = this.buildKey(name, labels);
    const current = this.counters.get(key) || 0;
    this.counters.set(key, current + value);

    this.recordMetric({
      name,
      type: MetricType.COUNTER,
      value: current + value,
      timestamp: new Date(),
      labels,
    });
  }

  /**
   * Define um gauge
   */
  setGauge(
    name: string,
    value: number,
    labels?: Record<string, string>
  ): void {
    const key = this.buildKey(name, labels);
    this.gauges.set(key, value);

    this.recordMetric({
      name,
      type: MetricType.GAUGE,
      value,
      timestamp: new Date(),
      labels,
    });
  }

  /**
   * Registra uma observação de histograma (ex: latência)
   */
  recordHistogram(
    name: string,
    value: number,
    labels?: Record<string, string>
  ): void {
    const key = this.buildKey(name, labels);
    const histogram = this.histograms.get(key) || [];

    histogram.push(value);
    if (histogram.length > 10000) {
      histogram.shift();
    }
    this.histograms.set(key, histogram);

    this.recordMetric({
      name,
      type: MetricType.HISTOGRAM,
      value,
      timestamp: new Date(),
      labels,
      unit: "ms",
    });
  }

  /**
   * Registra uma métrica
   */
  private recordMetric(metric: Metric): void {
    const name = metric.name;
    const metricsArray = this.metrics.get(name) || [];

    metricsArray.push(metric);
    if (metricsArray.length > this.maxMetricsPerName) {
      metricsArray.shift();
    }

    this.metrics.set(name, metricsArray);
  }

  /**
   * Computa agregações para um nome de métrica
   */
  aggregateMetrics(name: string): MetricAggregation | null {
    const metricsArray = this.metrics.get(name);
    if (!metricsArray || metricsArray.length === 0) {
      return null;
    }

    const values = metricsArray.map((m) => m.value).sort((a, b) => a - b);
    const count = values.length;
    const sum = values.reduce((a, b) => a + b, 0);
    const mean = sum / count;

    const aggregation: MetricAggregation = {
      name,
      count,
      sum,
      min: values[0],
      max: values[count - 1],
      mean,
      p50: this.percentile(values, 50),
      p95: this.percentile(values, 95),
      p99: this.percentile(values, 99),
      timestamp: new Date(),
    };

    this.aggregations.set(name, aggregation);
    return aggregation;
  }

  /**
   * Calcula percentil
   */
  private percentile(values: number[], p: number): number {
    const index = Math.ceil((p / 100) * values.length) - 1;
    return values[Math.max(0, index)];
  }

  /**
   * Retorna todas as métricas em formato Prometheus
   */
  getPrometheusMetrics(): string {
    let output = "";

    // TYPE declarations
    for (const [name, metricsArray] of this.metrics.entries()) {
      if (metricsArray.length === 0) continue;
      const type = metricsArray[0].type;
      output += `# TYPE ${this.sanitizeMetricName(name)} ${type}\n`;
    }

    // Metrics
    for (const [name, metricsArray] of this.metrics.entries()) {
      for (const metric of metricsArray) {
        const sanitized = this.sanitizeMetricName(name);
        const labels = metric.labels
          ? "{" + this.formatLabels(metric.labels) + "}"
          : "";
        output += `${sanitized}${labels} ${metric.value} ${metric.timestamp.getTime()}\n`;
      }
    }

    return output;
  }

  /**
   * Limpa métricas antigas (older than threshold)
   */
  pruneMetrics(thresholdMs: number = 3600000): void {
    const now = Date.now();
    for (const [name, metricsArray] of this.metrics.entries()) {
      const filtered = metricsArray.filter(
        (m) => now - m.timestamp.getTime() < thresholdMs
      );
      this.metrics.set(name, filtered);
    }
    this.logger.debug(
      { action: "pruneMetrics", thresholdMs },
      "Metrics pruned"
    );
  }

  /**
   * Retorna dashboard data pronto para Grafana/Prometheus
   */
  getDashboardData(): Record<string, unknown> {
    const dashboardData: Record<string, unknown> = {};

    // Agregar todas as métricas
    for (const name of this.metrics.keys()) {
      const agg = this.aggregateMetrics(name);
      if (agg) {
        dashboardData[name] = agg;
      }
    }

    return {
      timestamp: new Date().toISOString(),
      metrics: dashboardData,
      counters: Object.fromEntries(this.counters),
      gauges: Object.fromEntries(this.gauges),
    };
  }

  /**
   * Retorna métricas chave para relatórios
   */
  getKeyMetrics(): Record<string, unknown> {
    const latency = this.aggregateMetrics("sync_latency_ms");
    const successRate = this.calculateSuccessRate();
    const queueDepth = this.gauges.get("queue_depth") || 0;
    const errorRate = this.calculateErrorRate();

    return {
      latency: latency
        ? {
            mean: latency.mean,
            p95: latency.p95,
            p99: latency.p99,
          }
        : null,
      successRate,
      queueDepth,
      errorRate,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Calcula taxa de sucesso (%)
   */
  private calculateSuccessRate(): number {
    const total = this.counters.get("requests_total") || 0;
    const success = this.counters.get("requests_success") || 0;
    return total > 0 ? (success / total) * 100 : 0;
  }

  /**
   * Calcula taxa de erro (%)
   */
  private calculateErrorRate(): number {
    const total = this.counters.get("requests_total") || 0;
    const errors = this.counters.get("requests_error") || 0;
    return total > 0 ? (errors / total) * 100 : 0;
  }

  /**
   * Reseta todas as métricas (útil para testes)
   */
  reset(): void {
    this.metrics.clear();
    this.aggregations.clear();
    this.counters.clear();
    this.gauges.clear();
    this.histograms.clear();
  }

  private buildKey(
    name: string,
    labels?: Record<string, string>
  ): string {
    if (!labels || Object.keys(labels).length === 0) {
      return name;
    }
    return name + JSON.stringify(labels);
  }

  private sanitizeMetricName(name: string): string {
    return name.replace(/[^a-zA-Z0-9_]/g, "_");
  }

  private formatLabels(labels: Record<string, string>): string {
    return Object.entries(labels)
      .map(([k, v]) => `${k}="${v}"`)
      .join(",");
  }
}

/**
 * Gerenciador de alertas com integração Slack
 */
export class AlertManager {
  private alerts: Map<string, Alert> = new Map();
  private rules: Map<string, AlertRule> = new Map();
  private logger: Logger;
  private readonly alertHistorySize = 1000;
  private alertHistory: Alert[] = [];

  constructor(logger: Logger) {
    this.logger = logger;
  }

  /**
   * Registra uma regra de alerta
   */
  registerRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
    this.logger.info({ rule }, "Alert rule registered");
  }

  /**
   * Avalia um valor contra as regras e cria alertas se necessário
   */
  evaluateRules(metricName: string, currentValue: number): Alert[] {
    const triggeredAlerts: Alert[] = [];

    for (const rule of this.rules.values()) {
      if (!rule.enabled || rule.metricName !== metricName) {
        continue;
      }

      if (this.evaluateCondition(rule.operator, currentValue, rule.threshold)) {
        const alert = this.createAlert(rule, currentValue);
        triggeredAlerts.push(alert);
        this.alerts.set(alert.id, alert);
        this.addToHistory(alert);

        this.logger.warn({ alert }, "Alert triggered");

        // Enviar para Slack se configurado
        if (rule.slackWebhook) {
          this.sendSlackAlert(alert, rule).catch((err) =>
            this.logger.error({ err, alert }, "Failed to send Slack alert")
          );
        }
      }
    }

    return triggeredAlerts;
  }

  /**
   * Resolve um alerta
   */
  resolveAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = new Date();
      this.logger.info({ alert }, "Alert resolved");
    }
  }

  /**
   * Retorna alertas ativos
   */
  getActiveAlerts(): Alert[] {
    return Array.from(this.alerts.values()).filter((a) => !a.resolved);
  }

  /**
   * Retorna histórico de alertas
   */
  getAlertHistory(limit: number = 100): Alert[] {
    return this.alertHistory.slice(-limit);
  }

  /**
   * Limpa alertas antigos (resolvidos)
   */
  pruneAlerts(thresholdMs: number = 86400000): void {
    // 24h
    const now = Date.now();
    for (const [id, alert] of this.alerts.entries()) {
      if (
        alert.resolved &&
        now - alert.resolvedAt!.getTime() > thresholdMs
      ) {
        this.alerts.delete(id);
      }
    }
  }

  private evaluateCondition(
    operator: string,
    current: number,
    threshold: number
  ): boolean {
    switch (operator) {
      case ">":
        return current > threshold;
      case "<":
        return current < threshold;
      case ">=":
        return current >= threshold;
      case "<=":
        return current <= threshold;
      case "==":
        return current === threshold;
      case "!=":
        return current !== threshold;
      default:
        return false;
    }
  }

  private createAlert(rule: AlertRule, currentValue: number): Alert {
    return {
      id: uuidv4(),
      name: rule.name,
      severity: rule.severity,
      message: `${rule.name}: ${currentValue} ${rule.operator} ${rule.threshold}`,
      metricName: rule.metricName,
      threshold: rule.threshold,
      currentValue,
      timestamp: new Date(),
    };
  }

  private addToHistory(alert: Alert): void {
    this.alertHistory.push(alert);
    if (this.alertHistory.length > this.alertHistorySize) {
      this.alertHistory.shift();
    }
  }

  private async sendSlackAlert(alert: Alert, rule: AlertRule): Promise<void> {
    if (!rule.slackWebhook) {
      return;
    }

    const color =
      alert.severity === AlertSeverity.CRITICAL
        ? "ff0000"
        : alert.severity === AlertSeverity.ERROR
          ? "ff6600"
          : alert.severity === AlertSeverity.WARNING
            ? "ffcc00"
            : "36a64b";

    const payload = {
      attachments: [
        {
          fallback: alert.message,
          color,
          title: `[${alert.severity.toUpperCase()}] ${alert.name}`,
          text: alert.message,
          fields: [
            {
              title: "Current Value",
              value: alert.currentValue.toString(),
              short: true,
            },
            {
              title: "Threshold",
              value: alert.threshold.toString(),
              short: true,
            },
            {
              title: "Metric",
              value: alert.metricName,
              short: true,
            },
            {
              title: "Time",
              value: alert.timestamp.toISOString(),
              short: true,
            },
          ],
        },
      ],
    };

    try {
      const response = await fetch(rule.slackWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Slack API returned ${response.status}`);
      }
    } catch (error) {
      this.logger.error(
        { error, webhook: rule.slackWebhook },
        "Failed to send Slack alert"
      );
      throw error;
    }
  }
}

/**
 * Gerenciador de rastreamento distribuído (OpenTelemetry ready)
 */
export class TracingManager {
  private traces: Map<string, TraceContext> = new Map();
  private spans: Map<string, StructuredEvent[]> = new Map();
  private logger: Logger;

  constructor(logger: Logger) {
    this.logger = logger;
  }

  /**
   * Inicia um novo rastreamento
   */
  startTrace(): TraceContext {
    const traceId = uuidv4();
    const context: TraceContext = {
      traceId,
      spanId: uuidv4(),
      flags: 1,
    };

    this.traces.set(traceId, context);
    return context;
  }

  /**
   * Cria um novo span dentro de um rastreamento
   */
  createSpan(
    traceContext: TraceContext,
    name: string,
    metadata: Record<string, unknown> = {}
  ): StructuredEvent {
    const event: StructuredEvent = {
      id: uuidv4(),
      name,
      level: "info",
      timestamp: new Date(),
      metadata,
      traceContext: {
        ...traceContext,
        parentSpanId: traceContext.spanId,
        spanId: uuidv4(),
      },
    };

    const spanArray = this.spans.get(traceContext.traceId) || [];
    spanArray.push(event);
    this.spans.set(traceContext.traceId, spanArray);

    return event;
  }

  /**
   * Finaliza um span (registra duração)
   */
  endSpan(event: StructuredEvent, metadata?: Record<string, unknown>): void {
    event.duration = Date.now() - event.timestamp.getTime();
    if (metadata) {
      event.metadata = { ...event.metadata, ...metadata };
    }

    this.logger.info(
      {
        span: event.name,
        duration: event.duration,
        traceId: event.traceContext?.traceId,
        spanId: event.traceContext?.spanId,
        metadata: event.metadata,
      },
      "Span completed"
    );
  }

  /**
   * Retorna todos os spans de um rastreamento
   */
  getTrace(traceId: string): StructuredEvent[] {
    return this.spans.get(traceId) || [];
  }

  /**
   * Exporta rastreamento em formato OpenTelemetry-compatível
   */
  exportTrace(traceId: string): Record<string, unknown> {
    const events = this.getTrace(traceId);
    return {
      traceId,
      spanCount: events.length,
      startTime: events[0]?.timestamp,
      endTime: events[events.length - 1]?.timestamp,
      spans: events.map((e) => ({
        spanId: e.traceContext?.spanId,
        parentSpanId: e.traceContext?.parentSpanId,
        name: e.name,
        startTime: e.timestamp.toISOString(),
        endTime: e.duration
          ? new Date(e.timestamp.getTime() + e.duration).toISOString()
          : null,
        attributes: e.metadata,
      })),
    };
  }

  /**
   * Limpa rastreamentos antigos
   */
  pruneTraces(thresholdMs: number = 3600000): void {
    // 1h
    const now = Date.now();
    for (const traceId of this.spans.keys()) {
      const events = this.spans.get(traceId) || [];
      if (
        events.length > 0 &&
        now - events[0].timestamp.getTime() > thresholdMs
      ) {
        this.spans.delete(traceId);
        this.traces.delete(traceId);
      }
    }
  }
}

/**
 * Logger factory com configuração estruturada
 */
export function createLogger(
  serviceName: string,
  environment: string = "development"
): Logger {
  const isDev = environment === "development";

  return pino(
    {
      level: isDev ? "debug" : "info",
      timestamp: pino.stdTimeFunctions.isoTime,
      base: {
        service: serviceName,
        environment,
        version: "1.0.0",
      },
      formatters: {
        level: (label) => {
          return { level: label };
        },
      },
    },
    isDev
      ? pino.transport({
          target: "pino-pretty",
          options: {
            colorize: true,
            singleLine: false,
            translateTime: "SYS:standard",
            ignore: "pid,hostname",
          },
        })
      : undefined
  );
}

/**
 * Classe principal que integra tudo
 */
export class ObservabilityManager {
  public metrics: MetricsCollector;
  public alerts: AlertManager;
  public tracing: TracingManager;
  public logger: Logger;
  private cleanupInterval: NodeJS.Timer | null = null;

  constructor(serviceName: string, environment: string = "development") {
    this.logger = createLogger(serviceName, environment);
    this.metrics = new MetricsCollector(this.logger);
    this.alerts = new AlertManager(this.logger);
    this.tracing = new TracingManager(this.logger);

    this.setupDefaultAlerts();
    this.startCleanupTimer();
  }

  /**
   * Configura alertas padrão
   */
  private setupDefaultAlerts(): void {
    // High error rate (> 5%)
    this.alerts.registerRule({
      id: uuidv4(),
      name: "High Error Rate",
      metricName: "error_rate_percent",
      operator: ">",
      threshold: 5,
      severity: AlertSeverity.ERROR,
      enabled: true,
    });

    // Timeout detected (> 30s latency)
    this.alerts.registerRule({
      id: uuidv4(),
      name: "Request Timeout",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 30000,
      severity: AlertSeverity.WARNING,
      enabled: true,
    });

    // Stale sync (queue depth > 100)
    this.alerts.registerRule({
      id: uuidv4(),
      name: "Stale Sync - Queue Depth",
      metricName: "queue_depth",
      operator: ">",
      threshold: 100,
      severity: AlertSeverity.WARNING,
      enabled: true,
    });

    // Critical CPU usage (> 90%)
    this.alerts.registerRule({
      id: uuidv4(),
      name: "High CPU Usage",
      metricName: "cpu_usage_percent",
      operator: ">",
      threshold: 90,
      severity: AlertSeverity.CRITICAL,
      enabled: true,
    });

    this.logger.info(
      { ruleCount: 4 },
      "Default alert rules registered"
    );
  }

  /**
   * Inicia timer de limpeza periódica
   */
  private startCleanupTimer(): void {
    this.cleanupInterval = setInterval(
      () => {
        this.metrics.pruneMetrics(3600000); // 1h
        this.alerts.pruneAlerts(86400000); // 24h
        this.tracing.pruneTraces(3600000); // 1h
      },
      600000
    ); // 10 min
  }

  /**
   * Obtém status geral do sistema
   */
  getSystemStatus(): Record<string, unknown> {
    const keyMetrics = this.metrics.getKeyMetrics();
    const activeAlerts = this.alerts.getActiveAlerts();
    const dashboardData = this.metrics.getDashboardData();

    return {
      timestamp: new Date().toISOString(),
      health: {
        metrics: keyMetrics,
        alerts: {
          active: activeAlerts.length,
          list: activeAlerts,
        },
      },
      dashboard: dashboardData,
    };
  }

  /**
   * Retorna métricas em formato Prometheus
   */
  getPrometheusMetrics(): string {
    return this.metrics.getPrometheusMetrics();
  }

  /**
   * Limpa recursos
   */
  shutdown(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.logger.info("ObservabilityManager shutdown");
  }
}

/**
 * Criador de middleware para Express (exemplo de uso)
 */
export function createObservabilityMiddleware(
  observability: ObservabilityManager
) {
  return (req: any, res: any, next: any) => {
    const startTime = Date.now();
    const traceContext = observability.tracing.startTrace();

    // Adiciona contexto de rastreamento aos headers
    res.set("X-Trace-ID", traceContext.traceId);
    res.set("X-Span-ID", traceContext.spanId);

    // Intercepta response para registrar métricas
    const originalSend = res.send;
    res.send = function (data: any) {
      const duration = Date.now() - startTime;
      const statusCode = res.statusCode;

      // Registra latência
      observability.metrics.recordHistogram("http_request_latency_ms", duration, {
        method: req.method,
        path: req.path,
        status: statusCode.toString(),
      });

      // Registra sucesso/erro
      if (statusCode >= 400) {
        observability.metrics.incrementCounter("requests_error", 1, {
          status: statusCode.toString(),
        });
      } else {
        observability.metrics.incrementCounter("requests_success", 1);
      }

      observability.metrics.incrementCounter("requests_total", 1);

      // Log estruturado
      observability.logger.info(
        {
          traceId: traceContext.traceId,
          method: req.method,
          path: req.path,
          statusCode,
          duration,
        },
        "Request completed"
      );

      return originalSend.call(this, data);
    };

    next();
  };
}
