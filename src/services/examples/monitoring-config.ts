/**
 * Configuração de Monitoring & Observability
 *
 * Define:
 * - Alert rules
 * - Slack webhooks
 * - Thresholds customizados
 * - Preferências de ambiente
 */

import { AlertRule, AlertSeverity, ObservabilityManager } from "../monitoring";
import { v4 as uuidv4 } from "uuid";

/**
 * Interface para configuração de ambiente
 */
export interface MonitoringConfig {
  serviceName: string;
  environment: "development" | "staging" | "production";
  slack?: {
    webhookUrl: string;
    channels: {
      alerts: string;
      critical: string;
      warnings: string;
    };
  };
  alertRules: AlertRule[];
  metricsRetentionMs?: number;
  alertsRetentionMs?: number;
  tracesRetentionMs?: number;
}

/**
 * Configuração padrão para desenvolvimento
 */
export const developmentConfig: MonitoringConfig = {
  serviceName: "sync-service",
  environment: "development",
  metricsRetentionMs: 1800000, // 30 minutos
  alertsRetentionMs: 3600000, // 1 hora
  tracesRetentionMs: 900000, // 15 minutos
  alertRules: [
    {
      id: uuidv4(),
      name: "High Latency (Dev)",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 10000, // 10s em dev
      severity: AlertSeverity.WARNING,
      enabled: true,
    },
    {
      id: uuidv4(),
      name: "Queue Depth (Dev)",
      metricName: "queue_depth",
      operator: ">",
      threshold: 50, // 50 items em dev
      severity: AlertSeverity.WARNING,
      enabled: true,
    },
  ],
};

/**
 * Configuração para staging
 */
export const stagingConfig: MonitoringConfig = {
  serviceName: "sync-service-staging",
  environment: "staging",
  slack: {
    webhookUrl: process.env.SLACK_WEBHOOK_STAGING || "",
    channels: {
      alerts: "#staging-alerts",
      critical: "#critical-alerts",
      warnings: "#warnings",
    },
  },
  metricsRetentionMs: 3600000, // 1 hora
  alertsRetentionMs: 86400000, // 24 horas
  tracesRetentionMs: 3600000, // 1 hora
  alertRules: [
    {
      id: uuidv4(),
      name: "High Request Latency",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 5000, // 5s
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_STAGING,
      channels: ["#staging-alerts"],
    },
    {
      id: uuidv4(),
      name: "Timeout Detected",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 30000, // 30s
      severity: AlertSeverity.ERROR,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_STAGING,
      channels: ["#critical-alerts"],
    },
    {
      id: uuidv4(),
      name: "High Error Rate",
      metricName: "error_rate_percent",
      operator: ">",
      threshold: 5, // > 5%
      severity: AlertSeverity.ERROR,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_STAGING,
      channels: ["#staging-alerts"],
    },
    {
      id: uuidv4(),
      name: "Queue Stale",
      metricName: "queue_depth",
      operator: ">",
      threshold: 100,
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_STAGING,
      channels: ["#staging-alerts"],
    },
    {
      id: uuidv4(),
      name: "High CPU Usage",
      metricName: "cpu_usage_percent",
      operator: ">",
      threshold: 80, // > 80%
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_STAGING,
      channels: ["#warnings"],
    },
  ],
};

/**
 * Configuração para produção
 */
export const productionConfig: MonitoringConfig = {
  serviceName: "sync-service",
  environment: "production",
  slack: {
    webhookUrl: process.env.SLACK_WEBHOOK_PROD || "",
    channels: {
      alerts: "#alerts",
      critical: "#critical",
      warnings: "#ops-warnings",
    },
  },
  metricsRetentionMs: 86400000, // 24 horas
  alertsRetentionMs: 604800000, // 7 dias
  tracesRetentionMs: 3600000, // 1 hora
  alertRules: [
    // Latência
    {
      id: uuidv4(),
      name: "P95 Latency Warning",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 3000, // 3s
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#ops-warnings"],
    },
    {
      id: uuidv4(),
      name: "Request Timeout",
      metricName: "sync_latency_ms",
      operator: ">",
      threshold: 30000, // 30s
      severity: AlertSeverity.CRITICAL,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#critical", "#alerts"],
    },

    // Taxa de erro
    {
      id: uuidv4(),
      name: "High Error Rate (>5%)",
      metricName: "error_rate_percent",
      operator: ">",
      threshold: 5,
      severity: AlertSeverity.ERROR,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#alerts"],
    },
    {
      id: uuidv4(),
      name: "Critical Error Rate (>10%)",
      metricName: "error_rate_percent",
      operator: ">",
      threshold: 10,
      severity: AlertSeverity.CRITICAL,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#critical"],
    },

    // Fila
    {
      id: uuidv4(),
      name: "Queue Backing Up",
      metricName: "queue_depth",
      operator: ">",
      threshold: 100,
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#alerts"],
    },
    {
      id: uuidv4(),
      name: "Queue Severely Backed Up",
      metricName: "queue_depth",
      operator: ">",
      threshold: 500,
      severity: AlertSeverity.CRITICAL,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#critical"],
    },

    // CPU e Recursos
    {
      id: uuidv4(),
      name: "High CPU Usage Warning",
      metricName: "cpu_usage_percent",
      operator: ">",
      threshold: 75,
      severity: AlertSeverity.WARNING,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#ops-warnings"],
    },
    {
      id: uuidv4(),
      name: "Critical CPU Usage",
      metricName: "cpu_usage_percent",
      operator: ">",
      threshold: 90,
      severity: AlertSeverity.CRITICAL,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#critical"],
    },

    // Database Pool
    {
      id: uuidv4(),
      name: "DB Pool Nearly Exhausted",
      metricName: "db_pool_connections",
      operator: ">=",
      threshold: 90,
      severity: AlertSeverity.ERROR,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#alerts"],
    },
    {
      id: uuidv4(),
      name: "DB Pool Exhausted",
      metricName: "db_pool_connections",
      operator: "==",
      threshold: 100,
      severity: AlertSeverity.CRITICAL,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#critical"],
    },

    // SLA Compliance
    {
      id: uuidv4(),
      name: "Success Rate Below SLA",
      metricName: "success_rate_percent",
      operator: "<",
      threshold: 99, // < 99%
      severity: AlertSeverity.ERROR,
      enabled: true,
      slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      channels: ["#alerts"],
    },
  ],
};

/**
 * Factory para selecionar configuração por environment
 */
export function getConfig(env?: string): MonitoringConfig {
  const environment = env || process.env.NODE_ENV || "development";

  switch (environment) {
    case "production":
      return productionConfig;
    case "staging":
      return stagingConfig;
    default:
      return developmentConfig;
  }
}

/**
 * Aplicar configuração ao ObservabilityManager
 */
export function applyConfig(
  observability: ObservabilityManager,
  config: MonitoringConfig
): void {
  // Registrar todas as regras de alerta
  for (const rule of config.alertRules) {
    observability.alerts.registerRule(rule);
  }

  observability.logger.info(
    {
      environment: config.environment,
      ruleCount: config.alertRules.length,
    },
    "Monitoring configuration applied"
  );
}

/**
 * Exemplo de uso
 */
export function exampleUsage() {
  // Get config para environment atual
  const config = getConfig();

  // Criar observability manager
  const observability = new ObservabilityManager(
    config.serviceName,
    config.environment
  );

  // Aplicar configuração
  applyConfig(observability, config);

  // Usar observability manager
  observability.metrics.recordHistogram("sync_latency_ms", 2500);

  // Avaliar alertas
  observability.alerts.evaluateRules("sync_latency_ms", 2500);

  // Obter status
  const status = observability.getSystemStatus();
  console.log("System Status:", status);

  // Cleanup
  observability.shutdown();
}

/**
 * Configuração por segmento de aplicação
 */
export interface SegmentConfig {
  name: string;
  config: MonitoringConfig;
}

/**
 * Configs para diferentes segmentos
 */
export const segmentConfigs: Record<string, MonitoringConfig> = {
  "github-sync": {
    serviceName: "github-sync-service",
    environment: "production",
    alertRules: [
      {
        id: uuidv4(),
        name: "GitHub API Rate Limit Low",
        metricName: "github_api_remaining",
        operator: "<",
        threshold: 100,
        severity: AlertSeverity.WARNING,
        enabled: true,
        slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      },
    ],
  },

  "code-review": {
    serviceName: "code-review-service",
    environment: "production",
    alertRules: [
      {
        id: uuidv4(),
        name: "Review Queue Too Deep",
        metricName: "review_queue_depth",
        operator: ">",
        threshold: 200,
        severity: AlertSeverity.WARNING,
        enabled: true,
        slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      },
      {
        id: uuidv4(),
        name: "Model Inference Timeout",
        metricName: "inference_latency_ms",
        operator: ">",
        threshold: 60000,
        severity: AlertSeverity.ERROR,
        enabled: true,
        slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      },
    ],
  },

  "data-sync": {
    serviceName: "data-sync-service",
    environment: "production",
    alertRules: [
      {
        id: uuidv4(),
        name: "Sync Lag Too High",
        metricName: "sync_lag_seconds",
        operator: ">",
        threshold: 3600, // 1 hour
        severity: AlertSeverity.ERROR,
        enabled: true,
        slackWebhook: process.env.SLACK_WEBHOOK_PROD,
      },
    ],
  },
};

/**
 * Get config for specific segment
 */
export function getSegmentConfig(segment: string): MonitoringConfig {
  return segmentConfigs[segment] || getConfig();
}
