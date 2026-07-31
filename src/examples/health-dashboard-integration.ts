/**
 * Examples: Health Dashboard Integration
 * Demonstra como usar o HealthDashboard para monitoramento de sync
 */

import {
  HealthDashboard,
  HealthStatus,
  WebhookDeliveryStatus,
  createHealthDashboard,
} from '../services/health-dashboard';

/**
 * Exemplo 1: Monitoramento básico de sync
 */
export async function exampleBasicSyncMonitoring(): Promise<void> {
  console.log('\n=== Exemplo 1: Monitoramento Básico de Sync ===\n');

  const dashboard = createHealthDashboard();

  // Simula latências de sync
  console.log('Registrando latências de sync...');
  dashboard.recordSyncLatency(100000); // 100 seg
  dashboard.recordSyncLatency(150000); // 150 seg
  dashboard.recordSyncLatency(180000); // 180 seg

  const status = dashboard.getStatus();
  console.log('Status do Dashboard:', {
    status: status.status,
    latencyMs: status.summary.syncLatencyMs,
    onTarget: status.summary.syncOnTarget,
  });
}

/**
 * Exemplo 2: Rastreamento de conflitos
 */
export async function exampleConflictTracking(): Promise<void> {
  console.log('\n=== Exemplo 2: Rastreamento de Conflitos ===\n');

  const dashboard = createHealthDashboard();

  console.log('Simulando ciclo de conflitos...');

  // Conflitos são detectados
  for (let i = 0; i < 5; i++) {
    dashboard.recordConflictPending();
    console.log(`Conflito ${i + 1} registrado (pendente)`);
  }

  let metrics = dashboard.getMetrics();
  console.log(`Total de conflitos pendentes: ${metrics.conflicts.pending}`);

  // Conflitos são resolvidos
  console.log('\nResolvendo conflitos...');
  dashboard.resolveConflict();
  dashboard.resolveConflict();

  metrics = dashboard.getMetrics();
  console.log({
    pending: metrics.conflicts.pending,
    resolved: metrics.conflicts.resolved,
  });
}

/**
 * Exemplo 3: Monitoramento de uptime e outages
 */
export async function exampleUptimeTracking(): Promise<void> {
  console.log('\n=== Exemplo 3: Monitoramento de Uptime e Outages ===\n');

  const dashboard = createHealthDashboard();

  console.log('Sistema operacional...');

  // Simula um outage
  console.log('Registrando outage...');
  dashboard.recordOutage('Database connection lost');

  // Após 100ms, outage é encerrado
  await new Promise(resolve => setTimeout(resolve, 100));
  dashboard.endOutage();
  console.log('Outage encerrado');

  const metrics = dashboard.getMetrics();
  console.log({
    uptimePercentage: metrics.uptime.percentage,
    totalOutages: metrics.uptime.outages.length,
  });
}

/**
 * Exemplo 4: Rastreamento de entrega de webhooks
 */
export async function exampleWebhookTracking(): Promise<void> {
  console.log('\n=== Exemplo 4: Rastreamento de Webhooks ===\n');

  const dashboard = createHealthDashboard();

  const webhooks = [
    { id: 'webhook-1', status: WebhookDeliveryStatus.SUCCESS, time: 50 },
    { id: 'webhook-2', status: WebhookDeliveryStatus.SUCCESS, time: 75 },
    { id: 'webhook-3', status: WebhookDeliveryStatus.FAILED, time: 100 },
    { id: 'webhook-4', status: WebhookDeliveryStatus.SUCCESS, time: 60 },
    { id: 'webhook-5', status: WebhookDeliveryStatus.RETRYING, time: 0 },
  ];

  console.log('Registrando entregas de webhooks...');
  webhooks.forEach(wh => {
    dashboard.recordWebhookDeliveryAttempt(wh.id, wh.status, wh.time);
    console.log(`${wh.id}: ${wh.status}`);
  });

  const metrics = dashboard.getMetrics();
  console.log('\nMétricas de Webhook:', {
    totalAttempts: metrics.webhooks.totalAttempts,
    successful: metrics.webhooks.successfulDeliveries,
    failed: metrics.webhooks.failedDeliveries,
    successRate: `${metrics.webhooks.successRate}%`,
    avgDeliveryTime: `${metrics.webhooks.averageDeliveryTimeMs}ms`,
  });
}

/**
 * Exemplo 5: Monitoramento de fila
 */
export async function exampleQueueMonitoring(): Promise<void> {
  console.log('\n=== Exemplo 5: Monitoramento de Fila ===\n');

  const dashboard = createHealthDashboard();

  console.log('Simulando fila de processamento...');

  // Simula crescimento da fila
  for (let i = 1; i <= 5; i++) {
    const depth = i * 15;
    const critical = i > 3 ? i : 0;
    dashboard.recordQueueDepth(depth, 100, critical);
    console.log(`Iteração ${i}: profundidade=${depth}, críticos=${critical}`);

    await new Promise(resolve => setTimeout(resolve, 100));
  }

  const metrics = dashboard.getMetrics();
  console.log('\nMétricas de Fila:', {
    currentDepth: metrics.queue.currentDepth,
    maxDepth: metrics.queue.maxDepth,
    averageDepth: metrics.queue.averageDepth,
    criticalItems: metrics.queue.highestPriority,
    processingRate: `${metrics.queue.processingRate} items/min`,
  });
}

/**
 * Exemplo 6: Cenário de sync degradado
 */
export async function exampleDegradedSync(): Promise<void> {
  console.log('\n=== Exemplo 6: Cenário de Sync Degradado ===\n');

  const dashboard = createHealthDashboard();

  // Simula problemas progressivos
  console.log('Sync começando normalmente...');
  dashboard.recordSyncLatency(100000);
  dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 50);
  dashboard.recordQueueDepth(20, 100);

  let status = dashboard.getStatus();
  console.log('Status inicial:', status.status);

  console.log('\nSistema degrada...');
  // Latência aumenta
  dashboard.recordSyncLatency(280000);
  dashboard.recordSyncLatency(290000);

  // Webhooks começam a falhar
  dashboard.recordWebhookDeliveryAttempt('wh-2', WebhookDeliveryStatus.FAILED, 100);
  dashboard.recordWebhookDeliveryAttempt('wh-3', WebhookDeliveryStatus.FAILED, 100);

  // Fila cresce
  dashboard.recordQueueDepth(70, 100);
  dashboard.recordQueueDepth(80, 100, 5);

  status = dashboard.getStatus();
  console.log('Status degradado:', status.status);
  console.log('Alertas:', status.alerts.length);

  status.alerts.forEach(alert => {
    console.log(`  - [${alert.severity}] ${alert.message}`);
  });
}

/**
 * Exemplo 7: Dashboard de monitoramento em tempo real
 */
export async function exampleRealtimeDashboard(): Promise<void> {
  console.log('\n=== Exemplo 7: Dashboard em Tempo Real ===\n');

  const dashboard = createHealthDashboard();

  // Simula 5 ciclos de sync
  for (let cycle = 1; cycle <= 5; cycle++) {
    console.log(`\n--- Ciclo ${cycle} ---`);

    // Sync ocorre
    const latency = 100000 + Math.random() * 100000;
    dashboard.recordSyncLatency(latency);

    // Alguns conflitos
    if (Math.random() > 0.5) {
      dashboard.recordConflictPending();
      if (Math.random() > 0.3) {
        dashboard.resolveConflict();
      }
    }

    // Webhooks
    const webhookSuccess = Math.random() > 0.1;
    dashboard.recordWebhookDeliveryAttempt(
      `wh-${cycle}`,
      webhookSuccess ? WebhookDeliveryStatus.SUCCESS : WebhookDeliveryStatus.FAILED,
      Math.random() * 100
    );

    // Fila
    const queueDepth = Math.floor(Math.random() * 80);
    dashboard.recordQueueDepth(queueDepth, 100);

    // Mostra status
    const status = dashboard.getStatus();
    console.log('Status:', {
      health: status.status,
      latency: `${Math.round(status.summary.syncLatencyMs / 1000)}s`,
      conflicts: status.summary.conflictsPending,
      webhooks: `${status.summary.webhookSuccessRate}%`,
      queue: status.summary.queueDepth,
    });

    await new Promise(resolve => setTimeout(resolve, 500));
  }
}

/**
 * Exemplo 8: Exportando relatório
 */
export async function exampleExportReport(): Promise<void> {
  console.log('\n=== Exemplo 8: Exportando Relatório ===\n');

  const dashboard = createHealthDashboard();

  // Registra atividades variadas
  dashboard.recordSyncLatency(150000);
  dashboard.recordConflictResolved();
  dashboard.recordConflictPending();
  dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 75);
  dashboard.recordQueueDepth(30, 100);

  console.log('Exportando relatório em JSON...\n');
  const report = dashboard.exportReport();

  // Mostra apenas as métricas principais
  const parsed = JSON.parse(report);
  console.log('Métricas exportadas:', {
    timestamp: parsed.timestamp,
    overallStatus: parsed.overallStatus,
    syncLatency: {
      current: parsed.syncLatency.current,
      average: parsed.syncLatency.average,
      peak: parsed.syncLatency.peak,
    },
    conflicts: parsed.conflicts,
    webhooks: {
      totalAttempts: parsed.webhooks.totalAttempts,
      successRate: parsed.webhooks.successRate,
    },
    queue: {
      currentDepth: parsed.queue.currentDepth,
      averageDepth: parsed.queue.averageDepth,
    },
  });
}

/**
 * Executa todos os exemplos
 */
export async function runAllExamples(): Promise<void> {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║           Health Dashboard — Exemplos Completos             ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  await exampleBasicSyncMonitoring();
  await exampleConflictTracking();
  await exampleUptimeTracking();
  await exampleWebhookTracking();
  await exampleQueueMonitoring();
  await exampleDegradedSync();
  await exampleRealtimeDashboard();
  await exampleExportReport();

  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║                    Exemplos Concluídos!                     ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
}

// Executa se chamado diretamente
if (require.main === module) {
  runAllExamples().catch(console.error);
}
