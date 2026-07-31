/**
 * Tests for Health Dashboard Service
 */

import {
  HealthDashboard,
  HealthStatus,
  WebhookDeliveryStatus,
  getHealthDashboard,
  createHealthDashboard,
} from '../health-dashboard';

describe('HealthDashboard', () => {
  let dashboard: HealthDashboard;

  beforeEach(() => {
    dashboard = createHealthDashboard();
  });

  describe('Sync Latency Tracking', () => {
    it('should record sync latency and calculate metrics', () => {
      dashboard.recordSyncLatency(100000); // 100 sec
      dashboard.recordSyncLatency(150000); // 150 sec
      dashboard.recordSyncLatency(200000); // 200 sec

      const metrics = dashboard.getMetrics();
      expect(metrics.syncLatency.current).toBe(200000);
      expect(metrics.syncLatency.peak).toBe(200000);
      expect(metrics.syncLatency.average).toBeGreaterThan(0);
    });

    it('should determine if sync latency is within target (5 min = 300000ms)', () => {
      dashboard.recordSyncLatency(250000); // Below target
      let status = dashboard.getStatus();
      expect(status.summary.syncOnTarget).toBe(true);

      dashboard.recordSyncLatency(350000); // Above target
      status = dashboard.getStatus();
      expect(status.summary.syncOnTarget).toBe(false);
    });

    it('should create alert when latency exceeds target', () => {
      dashboard.recordSyncLatency(400000); // Exceeds target
      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.length).toBeGreaterThan(0);
      expect(metrics.alerts.some(a => a.category === 'sync_latency')).toBe(true);
    });

    it('should track latency history', () => {
      for (let i = 1; i <= 100; i++) {
        dashboard.recordSyncLatency(i * 1000);
      }

      const metrics = dashboard.getMetrics();
      expect(metrics.syncLatency.peak).toBe(100000);
    });
  });

  describe('Conflict Tracking', () => {
    it('should track resolved conflicts', () => {
      dashboard.recordConflictResolved();
      dashboard.recordConflictResolved();

      const metrics = dashboard.getMetrics();
      expect(metrics.conflicts.resolved).toBe(2);
    });

    it('should track pending conflicts', () => {
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();

      const status = dashboard.getStatus();
      expect(status.summary.conflictsPending).toBe(3);
    });

    it('should resolve pending conflicts', () => {
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();

      dashboard.resolveConflict();
      dashboard.resolveConflict();

      const metrics = dashboard.getMetrics();
      expect(metrics.conflicts.pending).toBe(1);
      expect(metrics.conflicts.resolved).toBe(2);
    });

    it('should resolve all conflicts at once', () => {
      for (let i = 0; i < 5; i++) {
        dashboard.recordConflictPending();
      }

      dashboard.resolveAllConflicts();

      const metrics = dashboard.getMetrics();
      expect(metrics.conflicts.pending).toBe(0);
      expect(metrics.conflicts.resolved).toBe(5);
    });

    it('should create alert for too many pending conflicts', () => {
      for (let i = 0; i < 15; i++) {
        dashboard.recordConflictPending();
      }

      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.some(a => a.category === 'conflicts')).toBe(true);
    });

    it('should clear conflict history', () => {
      dashboard.recordConflictResolved();
      dashboard.recordConflictPending();

      dashboard.clearConflictHistory();

      const metrics = dashboard.getMetrics();
      expect(metrics.conflicts.resolved).toBe(0);
      expect(metrics.conflicts.totalSinceLastClear).toBe(0);
      expect(metrics.conflicts.pending).toBe(1); // mantém pendentes
    });
  });

  describe('Uptime Tracking', () => {
    it('should calculate uptime percentage', () => {
      const metrics = dashboard.getMetrics();
      expect(metrics.uptime.percentage).toBeGreaterThanOrEqual(0);
      expect(metrics.uptime.percentage).toBeLessThanOrEqual(100);
    });

    it('should record outages', () => {
      dashboard.recordOutage('Database disconnected');

      // Simula que outage durou 100ms
      setTimeout(() => {
        dashboard.endOutage();
      }, 100);

      // Aguarda o setTimeout
      return new Promise((resolve) => {
        setTimeout(() => {
          const metrics = dashboard.getMetrics();
          expect(metrics.uptime.outages.length).toBeGreaterThan(0);
          expect(metrics.uptime.totalDowntime).toBeGreaterThanOrEqual(0);
          resolve(undefined);
        }, 150);
      });
    });

    it('should track multiple outages', () => {
      dashboard.recordOutage('Outage 1');
      dashboard.endOutage();

      dashboard.recordOutage('Outage 2');
      dashboard.endOutage();

      const metrics = dashboard.getMetrics();
      expect(metrics.uptime.outages.length).toBe(2);
    });

    it('should create alert when recording outage', () => {
      dashboard.recordOutage('Critical failure');

      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.some(a => a.severity === 'critical')).toBe(true);
      expect(metrics.alerts.some(a => a.category === 'uptime')).toBe(true);
    });

    it('should have high uptime when no outages occur', () => {
      const metrics = dashboard.getMetrics();
      expect(metrics.uptime.percentage).toBeGreaterThan(99);
    });
  });

  describe('Webhook Delivery Tracking', () => {
    it('should record successful webhook deliveries', () => {
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-2', WebhookDeliveryStatus.SUCCESS, 150);

      const metrics = dashboard.getMetrics();
      expect(metrics.webhooks.successfulDeliveries).toBe(2);
      expect(metrics.webhooks.totalAttempts).toBe(2);
    });

    it('should record failed webhook deliveries', () => {
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.FAILED, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-2', WebhookDeliveryStatus.SUCCESS, 50);

      const metrics = dashboard.getMetrics();
      expect(metrics.webhooks.failedDeliveries).toBe(1);
      expect(metrics.webhooks.successRate).toBe(50);
    });

    it('should track pending and retrying deliveries', () => {
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.PENDING, 0);
      dashboard.recordWebhookDeliveryAttempt('webhook-2', WebhookDeliveryStatus.RETRYING, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-3', WebhookDeliveryStatus.SUCCESS, 50);

      const metrics = dashboard.getMetrics();
      expect(metrics.webhooks.pendingDeliveries).toBe(1);
      expect(metrics.webhooks.retryingDeliveries).toBe(1);
    });

    it('should calculate webhook success rate', () => {
      // 3 successes, 2 failures = 60%
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-2', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-3', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-4', WebhookDeliveryStatus.FAILED, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-5', WebhookDeliveryStatus.FAILED, 100);

      const metrics = dashboard.getMetrics();
      expect(metrics.webhooks.successRate).toBe(60);
    });

    it('should calculate average delivery time', () => {
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('webhook-2', WebhookDeliveryStatus.SUCCESS, 200);
      dashboard.recordWebhookDeliveryAttempt('webhook-3', WebhookDeliveryStatus.SUCCESS, 300);

      const metrics = dashboard.getMetrics();
      expect(metrics.webhooks.averageDeliveryTimeMs).toBe(200);
    });

    it('should create alert when webhook delivery fails', () => {
      dashboard.recordWebhookDeliveryAttempt('webhook-1', WebhookDeliveryStatus.FAILED, 100);

      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.some(a => a.category === 'webhooks')).toBe(true);
    });
  });

  describe('Queue Depth Monitoring', () => {
    it('should record queue depth', () => {
      dashboard.recordQueueDepth(50, 100);
      dashboard.recordQueueDepth(75, 100);
      dashboard.recordQueueDepth(25, 100);

      const metrics = dashboard.getMetrics();
      expect(metrics.queue.currentDepth).toBe(25);
      expect(metrics.queue.maxDepth).toBe(100);
    });

    it('should calculate average queue depth', () => {
      dashboard.recordQueueDepth(20, 100);
      dashboard.recordQueueDepth(40, 100);
      dashboard.recordQueueDepth(60, 100);

      const metrics = dashboard.getMetrics();
      expect(metrics.queue.averageDepth).toBe(40);
    });

    it('should track critical items in queue', () => {
      dashboard.recordQueueDepth(50, 100, 5);
      dashboard.recordQueueDepth(60, 100, 3);

      const metrics = dashboard.getMetrics();
      expect(metrics.queue.highestPriority).toBe(3);
    });

    it('should create alert when queue depth is high', () => {
      dashboard.recordQueueDepth(85, 100); // 85% utilization

      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.some(a => a.category === 'queue')).toBe(true);
    });

    it('should create critical alert when too many critical items', () => {
      dashboard.recordQueueDepth(50, 100, 10);

      const metrics = dashboard.getMetrics();
      expect(metrics.alerts.some(a => a.severity === 'critical')).toBe(true);
    });

    it('should estimate queue drain time', () => {
      // Registra crescimento da fila
      for (let i = 0; i < 10; i++) {
        dashboard.recordQueueDepth(10 + i * 5, 100);
      }

      const metrics = dashboard.getMetrics();
      // Com dados de taxa de processamento, estima tempo
      expect(metrics.queue.estimatedDrainTimeMin).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Overall Health Status', () => {
    it('should be HEALTHY when all metrics are good', () => {
      dashboard.recordSyncLatency(100000); // Bem abaixo do alvo
      dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 50);
      dashboard.recordQueueDepth(30, 100); // 30% utilization

      const status = dashboard.getStatus();
      expect(status.status).toBe(HealthStatus.HEALTHY);
    });

    it('should be DEGRADED when multiple warning conditions exist', () => {
      dashboard.recordSyncLatency(280000); // Perto do alvo (80% of target)
      dashboard.recordSyncLatency(290000);
      dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 50);
      dashboard.recordWebhookDeliveryAttempt('wh-2', WebhookDeliveryStatus.FAILED, 50);
      dashboard.recordWebhookDeliveryAttempt('wh-3', WebhookDeliveryStatus.FAILED, 50); // Abaixa taxa de sucesso
      dashboard.recordQueueDepth(75, 100); // 75% utilization

      const status = dashboard.getStatus();
      // Tem múltiplas warning conditions, deveria ser DEGRADED
      expect([HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]).toContain(status.status);
    });

    it('should be UNHEALTHY when critical conditions exist', () => {
      dashboard.recordSyncLatency(350000); // Acima do alvo
      dashboard.recordOutage('Critical failure');

      const status = dashboard.getStatus();
      expect(status.status).toBe(HealthStatus.UNHEALTHY);
    });
  });

  describe('Alert Management', () => {
    it('should resolve alerts', () => {
      dashboard.recordSyncLatency(400000); // Cria alerta
      const metrics1 = dashboard.getMetrics();
      expect(metrics1.alerts.length).toBeGreaterThan(0);
      const alertId = metrics1.alerts[0].id;

      dashboard.resolveAlert(alertId);

      const metrics2 = dashboard.getMetrics();
      // Após resolver, o alerta não deve aparecer na lista de alertas ativos
      const unresolvedAlert = metrics2.alerts.find(a => a.id === alertId);
      expect(unresolvedAlert).toBeUndefined();
    });

    it('should clear resolved alerts', () => {
      dashboard.recordSyncLatency(400000);
      const metrics1 = dashboard.getMetrics();
      const alertId = metrics1.alerts[0].id;

      dashboard.resolveAlert(alertId);
      dashboard.clearResolvedAlerts();

      const metrics2 = dashboard.getMetrics();
      expect(metrics2.alerts.find(a => a.id === alertId)).toBeUndefined();
    });

    it('should include alerts in status', () => {
      dashboard.recordSyncLatency(400000);
      const status = dashboard.getStatus();
      expect(status.alerts.length).toBeGreaterThan(0);
    });
  });

  describe('Data Export and Reset', () => {
    it('should export report as JSON', () => {
      dashboard.recordSyncLatency(100000);
      dashboard.recordConflictResolved();
      dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 50);

      const report = dashboard.exportReport();
      expect(typeof report).toBe('string');

      const parsed = JSON.parse(report);
      expect(parsed.syncLatency).toBeDefined();
      expect(parsed.conflicts).toBeDefined();
      expect(parsed.webhooks).toBeDefined();
    });

    it('should reset all metrics', () => {
      dashboard.recordSyncLatency(100000);
      dashboard.recordConflictResolved();
      dashboard.recordConflictResolved();
      dashboard.recordQueueDepth(50, 100);

      dashboard.reset();

      const metrics = dashboard.getMetrics();
      expect(metrics.syncLatency.current).toBe(0);
      expect(metrics.conflicts.resolved).toBe(0);
      expect(metrics.queue.currentDepth).toBe(0);
    });
  });

  describe('Singleton Pattern', () => {
    it('should return same instance from getHealthDashboard', () => {
      const instance1 = getHealthDashboard();
      const instance2 = getHealthDashboard();
      expect(instance1).toBe(instance2);
    });

    it('should create new instances with createHealthDashboard', () => {
      const instance1 = createHealthDashboard();
      const instance2 = createHealthDashboard();
      expect(instance1).not.toBe(instance2);
    });
  });

  describe('Integration Scenarios', () => {
    it('should handle complete sync lifecycle with conflicts and recovery', () => {
      // Inicia sync
      dashboard.recordSyncLatency(150000);

      // Alguns conflitos
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();
      dashboard.recordConflictPending();

      // Resolve conflitos
      dashboard.resolveConflict();
      dashboard.resolveConflict();

      // Webhooks disparam
      dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 100);
      dashboard.recordWebhookDeliveryAttempt('wh-2', WebhookDeliveryStatus.SUCCESS, 120);

      const status = dashboard.getStatus();
      expect(status.summary.syncLatencyMs).toBe(150000);
      expect(status.summary.conflictsPending).toBe(1);
      expect(status.summary.webhookSuccessRate).toBe(100);
    });

    it('should track multiple sync cycles', () => {
      for (let cycle = 0; cycle < 5; cycle++) {
        dashboard.recordSyncLatency(100000 + cycle * 10000);
        dashboard.recordQueueDepth(20 + cycle * 5, 100);
      }

      const metrics = dashboard.getMetrics();
      expect(metrics.syncLatency.peak).toBe(140000);
    });

    it('should provide useful dashboard summary for monitoring', () => {
      // Simula atividade normal
      dashboard.recordSyncLatency(250000);
      dashboard.recordConflictResolved();
      dashboard.recordConflictPending();
      dashboard.recordWebhookDeliveryAttempt('wh-1', WebhookDeliveryStatus.SUCCESS, 75);
      dashboard.recordQueueDepth(35, 100, 2);

      const status = dashboard.getStatus();

      expect(status.lastUpdate).toBeDefined();
      expect(status.summary.syncLatencyMs).toBeGreaterThan(0);
      expect(status.summary.queueDepth).toBe(35);
      expect(status.status).toBeDefined();
    });
  });
});
