/**
 * Configurações para SyncQueueManager
 * Pré-configurações para diferentes cenários de uso
 */

import { SyncQueueManager, QueuePriority, type RetryPolicy } from "../services/sync-queue";

/**
 * Presets de configuração
 */
export const SyncQueuePresets = {
  /**
   * Development: Baixa latência, low throughput
   * Bom para testes locais
   */
  development: {
    maxBatchSize: 5,
    processingIntervalMs: 1000,
    retryPolicy: {
      maxRetries: 2,
      initialDelayMs: 500,
      maxDelayMs: 5000,
      backoffMultiplier: 2,
    } as RetryPolicy,
  },

  /**
   * Production: Alto throughput, confiabilidade
   * Para sincronização crítica
   */
  production: {
    maxBatchSize: 50,
    processingIntervalMs: 5000,
    retryPolicy: {
      maxRetries: 5,
      initialDelayMs: 1000,
      maxDelayMs: 60000,
      backoffMultiplier: 2,
    } as RetryPolicy,
  },

  /**
   * HighThroughput: Máxima performance
   * Para grande volume de items
   */
  highThroughput: {
    maxBatchSize: 100,
    processingIntervalMs: 2000,
    retryPolicy: {
      maxRetries: 3,
      initialDelayMs: 500,
      maxDelayMs: 30000,
      backoffMultiplier: 1.5,
    } as RetryPolicy,
  },

  /**
   * LowLatency: Mínima latência
   * Para processamento em tempo real
   */
  lowLatency: {
    maxBatchSize: 5,
    processingIntervalMs: 100,
    retryPolicy: {
      maxRetries: 2,
      initialDelayMs: 100,
      maxDelayMs: 2000,
      backoffMultiplier: 2,
    } as RetryPolicy,
  },

  /**
   * Reliable: Máxima confiabilidade
   * Para dados críticos
   */
  reliable: {
    maxBatchSize: 10,
    processingIntervalMs: 10000,
    retryPolicy: {
      maxRetries: 10,
      initialDelayMs: 2000,
      maxDelayMs: 120000,
      backoffMultiplier: 2,
    } as RetryPolicy,
  },
};

/**
 * Tipo de preset disponível
 */
export type SyncQueuePreset = keyof typeof SyncQueuePresets;

/**
 * Factory para criar SyncQueueManager com preset
 */
export function createSyncQueueManager<T>(
  preset: SyncQueuePreset = "development"
): SyncQueueManager<T> {
  const config = SyncQueuePresets[preset];

  console.log(
    `✅ Creating SyncQueueManager with preset: ${preset}`
  );
  console.log(`   Batch size: ${config.maxBatchSize}`);
  console.log(`   Processing interval: ${config.processingIntervalMs}ms`);
  console.log(`   Max retries: ${config.retryPolicy.maxRetries}`);

  return new SyncQueueManager<T>(config);
}

/**
 * Configuração padrão para ambiente
 */
export function getDefaultPreset(): SyncQueuePreset {
  const env = process.env.NODE_ENV || "development";

  switch (env) {
    case "production":
      return "production";
    case "staging":
      return "reliable";
    default:
      return "development";
  }
}

/**
 * Configurações padrão para Supabase
 */
export const SupabaseQueueConfig = {
  development: {
    supabaseUrl: process.env.SUPABASE_URL || "http://localhost:54321",
    supabaseKey: process.env.SUPABASE_ANON_KEY || "eyJhbGc...",
    tableName: "sync_queue_dev",
    deadLetterTableName: "sync_queue_dead_letter_dev",
  },

  production: {
    supabaseUrl: process.env.SUPABASE_URL || "",
    supabaseKey: process.env.SUPABASE_ANON_KEY || "",
    tableName: "sync_queue",
    deadLetterTableName: "sync_queue_dead_letter",
  },
};

/**
 * Configurações de monitoramento
 */
export const MonitoringConfig = {
  /**
   * Prometheus endpoint
   */
  prometheusEndpoint: process.env.PROMETHEUS_PUSHGATEWAY || "http://localhost:9091",

  /**
   * Intervalo de push para Prometheus
   */
  prometheusPushIntervalMs: 30000, // 30 segundos

  /**
   * Alertas
   */
  alerts: {
    deadLetterQueueThreshold: 50, // Alertar se DLQ > 50 items
    failureRateThreshold: 0.1, // Alertar se taxa de falha > 10%
    latencyThreshold: 5000, // Alertar se latência > 5s
    queueSizeThreshold: 1000, // Alertar se fila > 1000 items
  },

  /**
   * Logging
   */
  logging: {
    verbose: process.env.DEBUG === "true",
    logMetricsInterval: 60000, // 60 segundos
  },
};

/**
 * Exemplo de uso
 */
export function exampleUsage(): void {
  // Criar manager com preset padrão
  const manager = createSyncQueueManager<{ id: string; data: string }>(
    getDefaultPreset()
  );

  // Ou criar com preset específico
  const devManager = createSyncQueueManager<{ id: string; data: string }>(
    "development"
  );

  const prodManager = createSyncQueueManager<{ id: string; data: string }>(
    "production"
  );

  console.log("Managers criados com sucesso!");

  // Cleanup
  manager.destroy();
  devManager.destroy();
  prodManager.destroy();
}

/**
 * Configurações por ambiente
 */
export const EnvironmentConfig = {
  development: {
    queuePreset: "development" as SyncQueuePreset,
    enableMetrics: true,
    metricsVerbose: true,
    persistenceEnabled: false, // Em desenvolvimento, sem Supabase
  },

  staging: {
    queuePreset: "reliable" as SyncQueuePreset,
    enableMetrics: true,
    metricsVerbose: false,
    persistenceEnabled: true, // Staging com persistência
  },

  production: {
    queuePreset: "production" as SyncQueuePreset,
    enableMetrics: true,
    metricsVerbose: false,
    persistenceEnabled: true, // Produção sempre com persistência
  },
};

/**
 * Obter configuração do ambiente atual
 */
export function getEnvironmentConfig() {
  const env = (process.env.NODE_ENV || "development") as keyof typeof EnvironmentConfig;
  return EnvironmentConfig[env] || EnvironmentConfig.development;
}
