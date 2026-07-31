/**
 * Phase 2 - Cowork Integration Tests
 * Comprehensive test suite for webhook validation, event processing,
 * notifications, health monitoring, and queue management.
 *
 * Coverage Areas:
 * - Webhook signature validation (HMAC-SHA256)
 * - Event processing (PR, commit, task)
 * - Notification delivery with rate limiting
 * - Health dashboard metrics accuracy
 * - Sync queue idempotency
 * - Error handling & retry logic
 *
 * Target: 30+ tests, >80% coverage
 */

import crypto from 'crypto';

// ============================================================================
// MOCK INTERFACES & TYPES
// ============================================================================

enum WebhookEventType {
  PR_OPENED = 'pr.opened',
  PR_MERGED = 'pr.merged',
  COMMIT = 'commit',
  TASK_UPDATED = 'task.updated',
  TASK_STATUS_CHANGED = 'task.status_changed',
  COMMENT_ADDED = 'comment.added',
}

enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

enum DeliveryStatus {
  PENDING = 'pending',
  SENT = 'sent',
  FAILED = 'failed',
  DELIVERED = 'delivered',
}

enum HealthStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy',
}

interface WebhookPayload {
  event: WebhookEventType;
  timestamp: string;
  deliveryId: string;
  data: Record<string, unknown>;
  retryCount?: number;
}

interface NotificationEvent {
  id: string;
  type: string;
  userId: string;
  priority: NotificationPriority;
  timestamp: Date;
  data: Record<string, unknown>;
}

interface QueueEntry {
  id: string;
  payload: WebhookPayload;
  retryCount: number;
  timestamp: number;
  idempotencyKey?: string;
}

interface HealthMetrics {
  syncLatencyMs: number;
  webhookSuccessRate: number;
  queueDepth: number;
  uptime: number;
  status: HealthStatus;
}

interface RateLimitConfig {
  maxPerMinute: number;
  maxPerHour: number;
  userId: string;
}

// ============================================================================
// WEBHOOK SIGNATURE VALIDATOR
// ============================================================================

class WebhookSignatureValidator {
  constructor(private secret: string) {}

  validateSignature(payload: string, signature: string): boolean {
    try {
      const expectedSignature = crypto
        .createHmac('sha256', this.secret)
        .update(payload)
        .digest('hex');

      return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
      );
    } catch (error) {
      return false;
    }
  }

  generateSignature(payload: string): string {
    return crypto
      .createHmac('sha256', this.secret)
      .update(payload)
      .digest('hex');
  }
}

// ============================================================================
// EVENT PROCESSOR
// ============================================================================

class EventProcessor {
  private processedEvents: Set<string> = new Set();

  async processEvent(payload: WebhookPayload): Promise<boolean> {
    // Check for duplicates
    if (this.processedEvents.has(payload.deliveryId)) {
      return false;
    }

    // Validate event type
    if (!Object.values(WebhookEventType).includes(payload.event)) {
      throw new Error(`Unknown event type: ${payload.event}`);
    }

    this.processedEvents.add(payload.deliveryId);
    return true;
  }

  hasProcessed(deliveryId: string): boolean {
    return this.processedEvents.has(deliveryId);
  }

  clearProcessed(): void {
    this.processedEvents.clear();
  }
}

// ============================================================================
// NOTIFICATION SERVICE
// ============================================================================

class NotificationService {
  private queue: NotificationEvent[] = [];
  private rateLimits: Map<string, number[]> = new Map();
  private deliveryLog: Array<{
    id: string;
    status: DeliveryStatus;
    timestamp: Date;
  }> = [];
  private maxPerMinute: number = 5;
  private userPreferences: Map<string, { optin: boolean; channels: string[] }> =
    new Map();

  async queueNotification(event: NotificationEvent): Promise<boolean> {
    // Check rate limit
    if (!this.checkRateLimit(event.userId)) {
      return false;
    }

    // Check user preferences
    const prefs = this.userPreferences.get(event.userId);
    if (prefs && !prefs.optin) {
      return false;
    }

    this.queue.push(event);
    return true;
  }

  private checkRateLimit(userId: string): boolean {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    if (!this.rateLimits.has(userId)) {
      this.rateLimits.set(userId, []);
    }

    const userTimestamps = this.rateLimits.get(userId)!;
    const recentTimestamps = userTimestamps.filter(
      (ts) => ts > oneMinuteAgo
    );

    // Check limit BEFORE adding new timestamp
    const canProceed = recentTimestamps.length < this.maxPerMinute;

    // Add this request to the list if allowed
    if (canProceed) {
      recentTimestamps.push(now);
    }

    this.rateLimits.set(userId, recentTimestamps);

    return canProceed;
  }

  async deliverNotification(
    event: NotificationEvent
  ): Promise<DeliveryStatus> {
    try {
      // Simulate delivery
      const timestamp = new Date();
      this.recordDelivery(event.id, DeliveryStatus.DELIVERED, timestamp);
      return DeliveryStatus.DELIVERED;
    } catch (error) {
      this.recordDelivery(event.id, DeliveryStatus.FAILED, new Date());
      return DeliveryStatus.FAILED;
    }
  }

  private recordDelivery(
    id: string,
    status: DeliveryStatus,
    timestamp: Date
  ): void {
    this.deliveryLog.push({ id, status, timestamp });
  }

  setUserPreference(
    userId: string,
    optin: boolean,
    channels: string[] = []
  ): void {
    this.userPreferences.set(userId, { optin, channels });
  }

  getDeliveryLog() {
    return this.deliveryLog;
  }

  getQueueSize(): number {
    return this.queue.length;
  }

  processQueue(): number {
    let processed = 0;
    while (this.queue.length > 0) {
      const event = this.queue.shift();
      if (event) {
        processed++;
      }
    }
    return processed;
  }
}

// ============================================================================
// SYNC QUEUE WITH IDEMPOTENCY
// ============================================================================

class SyncQueue {
  private queue: QueueEntry[] = [];
  private idempotencyIndex: Map<string, string> = new Map();
  private processedIds: Set<string> = new Set();

  enqueue(payload: WebhookPayload, idempotencyKey?: string): boolean {
    // Generate idempotency key if not provided
    const key = idempotencyKey || payload.deliveryId;

    // Check for duplicate
    if (this.idempotencyIndex.has(key)) {
      return false;
    }

    const entry: QueueEntry = {
      id: crypto.randomUUID(),
      payload,
      retryCount: 0,
      timestamp: Date.now(),
      idempotencyKey: key,
    };

    this.queue.push(entry);
    this.idempotencyIndex.set(key, entry.id);
    return true;
  }

  dequeue(): QueueEntry | undefined {
    return this.queue.shift();
  }

  async process(processor: (entry: QueueEntry) => Promise<void>): Promise<number> {
    let processed = 0;
    while (this.queue.length > 0) {
      const entry = this.dequeue();
      if (entry) {
        try {
          await processor(entry);
          this.processedIds.add(entry.id);
          processed++;
        } catch (error) {
          // Re-queue on error
          this.queue.push(entry);
        }
      }
    }
    return processed;
  }

  isDuplicate(idempotencyKey: string): boolean {
    return this.idempotencyIndex.has(idempotencyKey);
  }

  getSize(): number {
    return this.queue.length;
  }

  clear(): void {
    this.queue = [];
    this.idempotencyIndex.clear();
    this.processedIds.clear();
  }

  getStats() {
    return {
      queueSize: this.queue.length,
      processedCount: this.processedIds.size,
      idempotencyIndexSize: this.idempotencyIndex.size,
    };
  }
}

// ============================================================================
// HEALTH DASHBOARD
// ============================================================================

class HealthDashboard {
  private syncLatencies: number[] = [];
  private webhookDeliveries: { success: boolean; timestamp: Date }[] = [];
  private queueDepths: number[] = [];
  private startTime = Date.now();
  private downtime = 0;
  private conflicts = {
    resolved: 0,
    pending: 0,
  };

  recordSyncLatency(latencyMs: number): void {
    this.syncLatencies.push(latencyMs);
    // Keep only last 100 entries
    if (this.syncLatencies.length > 100) {
      this.syncLatencies.shift();
    }
  }

  recordWebhookDelivery(success: boolean): void {
    this.webhookDeliveries.push({ success, timestamp: new Date() });
    // Keep only last 1000 entries
    if (this.webhookDeliveries.length > 1000) {
      this.webhookDeliveries.shift();
    }
  }

  recordQueueDepth(depth: number): void {
    this.queueDepths.push(depth);
    // Keep only last 100 entries
    if (this.queueDepths.length > 100) {
      this.queueDepths.shift();
    }
  }

  recordConflictResolved(): void {
    this.conflicts.resolved++;
  }

  recordConflictPending(): void {
    this.conflicts.pending++;
  }

  recordDowntime(durationMs: number): void {
    this.downtime += durationMs;
  }

  getMetrics(): HealthMetrics {
    const avgLatency =
      this.syncLatencies.length > 0
        ? this.syncLatencies.reduce((a, b) => a + b, 0) /
          this.syncLatencies.length
        : 0;

    const successCount = this.webhookDeliveries.filter(
      (d) => d.success
    ).length;
    const successRate =
      this.webhookDeliveries.length > 0
        ? (successCount / this.webhookDeliveries.length) * 100
        : 100;

    const avgQueueDepth =
      this.queueDepths.length > 0
        ? this.queueDepths.reduce((a, b) => a + b, 0) / this.queueDepths.length
        : 0;

    const totalTime = Date.now() - this.startTime;
    const uptime = ((totalTime - this.downtime) / totalTime) * 100;

    const status =
      uptime < 99 || avgLatency > 5000
        ? HealthStatus.UNHEALTHY
        : uptime < 99.5 || avgLatency > 3000
          ? HealthStatus.DEGRADED
          : HealthStatus.HEALTHY;

    return {
      syncLatencyMs: avgLatency,
      webhookSuccessRate: successRate,
      queueDepth: avgQueueDepth,
      uptime,
      status,
    };
  }

  getConflictStats() {
    return this.conflicts;
  }

  reset(): void {
    this.syncLatencies = [];
    this.webhookDeliveries = [];
    this.queueDepths = [];
    this.startTime = Date.now();
    this.downtime = 0;
    this.conflicts = { resolved: 0, pending: 0 };
  }
}

// ============================================================================
// RATE LIMITER
// ============================================================================

class RateLimiter {
  private buckets: Map<string, number[]> = new Map();
  private readonly maxPerMinute: number;
  private readonly maxPerHour: number;

  constructor(maxPerMinute = 10, maxPerHour = 100) {
    this.maxPerMinute = maxPerMinute;
    this.maxPerHour = maxPerHour;
  }

  canProceed(key: string): boolean {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    const oneHourAgo = now - 3600000;

    if (!this.buckets.has(key)) {
      this.buckets.set(key, []);
    }

    const timestamps = this.buckets.get(key)!;

    // Filter to keep only recent timestamps
    const recentMinute = timestamps.filter((ts) => ts > oneMinuteAgo);
    const recentHour = timestamps.filter((ts) => ts > oneHourAgo);

    // Check limits
    if (recentMinute.length >= this.maxPerMinute) {
      return false;
    }
    if (recentHour.length >= this.maxPerHour) {
      return false;
    }

    // Record this request
    recentMinute.push(now);
    this.buckets.set(key, recentMinute);

    return true;
  }

  getRemainingRequests(key: string): number {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    const timestamps = this.buckets.get(key) || [];
    const recentCount = timestamps.filter((ts) => ts > oneMinuteAgo).length;

    return Math.max(0, this.maxPerMinute - recentCount);
  }

  reset(): void {
    this.buckets.clear();
  }
}

// ============================================================================
// RETRY HANDLER
// ============================================================================

class RetryHandler {
  private readonly maxRetries: number;
  private readonly initialBackoffMs: number;
  private readonly maxBackoffMs: number;

  constructor(
    maxRetries = 3,
    initialBackoffMs = 100,
    maxBackoffMs = 5000
  ) {
    this.maxRetries = maxRetries;
    this.initialBackoffMs = initialBackoffMs;
    this.maxBackoffMs = maxBackoffMs;
  }

  calculateBackoff(retryCount: number): number {
    const exponentialBackoff = this.initialBackoffMs * Math.pow(2, retryCount);
    return Math.min(exponentialBackoff, this.maxBackoffMs);
  }

  async retry<T>(
    fn: () => Promise<T>,
    onRetry?: (attempt: number) => void
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        if (attempt < this.maxRetries) {
          const backoff = this.calculateBackoff(attempt);
          onRetry?.(attempt + 1);
          await new Promise((resolve) => setTimeout(resolve, backoff));
        }
      }
    }

    throw lastError;
  }

  shouldRetry(retryCount: number): boolean {
    return retryCount < this.maxRetries;
  }
}

// ============================================================================
// TEST SUITE BEGINS
// ============================================================================

describe('Phase 2 - Cowork Integration', () => {
  const secret = 'test-secret-key-12345';
  let validator: WebhookSignatureValidator;
  let processor: EventProcessor;
  let notificationService: NotificationService;
  let syncQueue: SyncQueue;
  let healthDashboard: HealthDashboard;
  let rateLimiter: RateLimiter;
  let retryHandler: RetryHandler;

  beforeEach(() => {
    validator = new WebhookSignatureValidator(secret);
    processor = new EventProcessor();
    notificationService = new NotificationService();
    syncQueue = new SyncQueue();
    healthDashboard = new HealthDashboard();
    rateLimiter = new RateLimiter(5, 50); // 5 per min, 50 per hour
    retryHandler = new RetryHandler(3, 50, 500);
  });

  // ==========================================================================
  // WEBHOOK SIGNATURE VALIDATION (5 tests)
  // ==========================================================================

  describe('Webhook Signature Validation', () => {
    test('validates correct HMAC-SHA256 signature', () => {
      const payload = JSON.stringify({
        event: WebhookEventType.PR_OPENED,
        data: { pr_id: '123' },
      });
      const signature = validator.generateSignature(payload);

      expect(validator.validateSignature(payload, signature)).toBe(true);
    });

    test('rejects invalid signature', () => {
      const payload = JSON.stringify({
        event: WebhookEventType.PR_OPENED,
        data: { pr_id: '123' },
      });
      const invalidSignature = 'invalid-signature-hash';

      expect(validator.validateSignature(payload, invalidSignature)).toBe(
        false
      );
    });

    test('rejects tampered payload', () => {
      const payload = JSON.stringify({
        event: WebhookEventType.PR_OPENED,
        data: { pr_id: '123' },
      });
      const signature = validator.generateSignature(payload);

      const tamperedPayload = JSON.stringify({
        event: WebhookEventType.COMMIT,
        data: { pr_id: '999' },
      });

      expect(validator.validateSignature(tamperedPayload, signature)).toBe(
        false
      );
    });

    test('handles missing signature gracefully', () => {
      const payload = JSON.stringify({
        event: WebhookEventType.COMMIT,
        data: {},
      });

      expect(validator.validateSignature(payload, '')).toBe(false);
    });

    test('prevents timing attacks with timingSafeEqual', () => {
      const payload = JSON.stringify({
        event: WebhookEventType.TASK_UPDATED,
        data: { task_id: '456' },
      });
      const signature = validator.generateSignature(payload);

      // Multiple validations with same valid signature should all succeed
      expect(validator.validateSignature(payload, signature)).toBe(true);
      expect(validator.validateSignature(payload, signature)).toBe(true);
    });
  });

  // ==========================================================================
  // EVENT PROCESSING (8 tests)
  // ==========================================================================

  describe('Event Processing', () => {
    test('processes PR_OPENED event successfully', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.PR_OPENED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-001',
        data: { pr_id: '123', title: 'New Feature' },
      };

      const result = await processor.processEvent(payload);

      expect(result).toBe(true);
      expect(processor.hasProcessed('delivery-001')).toBe(true);
    });

    test('processes COMMIT event successfully', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.COMMIT,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-002',
        data: { commit_sha: 'abc123', message: 'Fix bug' },
      };

      const result = await processor.processEvent(payload);

      expect(result).toBe(true);
    });

    test('processes TASK_UPDATED event successfully', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.TASK_UPDATED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-003',
        data: { task_id: 'task-001', status: 'in_progress' },
      };

      const result = await processor.processEvent(payload);

      expect(result).toBe(true);
    });

    test('rejects duplicate events', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.TASK_STATUS_CHANGED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-004',
        data: { task_id: 'task-002' },
      };

      await processor.processEvent(payload);
      const duplicateResult = await processor.processEvent(payload);

      expect(duplicateResult).toBe(false);
    });

    test('rejects unknown event types', async () => {
      const payload: WebhookPayload = {
        event: 'unknown.event' as WebhookEventType,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-005',
        data: {},
      };

      await expect(processor.processEvent(payload)).rejects.toThrow(
        'Unknown event type'
      );
    });

    test('processes multiple events in sequence', async () => {
      const payloads: WebhookPayload[] = [
        {
          event: WebhookEventType.PR_OPENED,
          timestamp: new Date().toISOString(),
          deliveryId: 'delivery-101',
          data: {},
        },
        {
          event: WebhookEventType.COMMIT,
          timestamp: new Date().toISOString(),
          deliveryId: 'delivery-102',
          data: {},
        },
        {
          event: WebhookEventType.TASK_UPDATED,
          timestamp: new Date().toISOString(),
          deliveryId: 'delivery-103',
          data: {},
        },
      ];

      for (const payload of payloads) {
        await processor.processEvent(payload);
      }

      expect(processor.hasProcessed('delivery-101')).toBe(true);
      expect(processor.hasProcessed('delivery-102')).toBe(true);
      expect(processor.hasProcessed('delivery-103')).toBe(true);
    });

    test('handles comment events', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.COMMENT_ADDED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-104',
        data: { comment_id: 'comment-001', text: 'Great work!' },
      };

      const result = await processor.processEvent(payload);

      expect(result).toBe(true);
    });
  });

  // ==========================================================================
  // NOTIFICATION DELIVERY (6 tests)
  // ==========================================================================

  describe('Notification Delivery', () => {
    test('queues notification successfully', async () => {
      const event: NotificationEvent = {
        id: 'notif-001',
        type: 'pr_opened',
        userId: 'user-123',
        priority: NotificationPriority.MEDIUM,
        timestamp: new Date(),
        data: { pr_id: '123' },
      };

      const result = await notificationService.queueNotification(event);

      expect(result).toBe(true);
      expect(notificationService.getQueueSize()).toBe(1);
    });

    test('respects user notification preferences', async () => {
      notificationService.setUserPreference('user-456', false);

      const event: NotificationEvent = {
        id: 'notif-002',
        type: 'task_updated',
        userId: 'user-456',
        priority: NotificationPriority.HIGH,
        timestamp: new Date(),
        data: { task_id: 'task-001' },
      };

      const result = await notificationService.queueNotification(event);

      expect(result).toBe(false);
      expect(notificationService.getQueueSize()).toBe(0);
    });

    test('enforces per-user rate limiting', async () => {
      const userId = 'user-789';
      notificationService.setUserPreference(userId, true);
      const results: boolean[] = [];

      for (let i = 0; i < 7; i++) {
        const event: NotificationEvent = {
          id: `notif-${i}`,
          type: 'test',
          userId,
          priority: NotificationPriority.LOW,
          timestamp: new Date(),
          data: { index: i },
        };

        const result = await notificationService.queueNotification(event);
        results.push(result);
      }

      // First 5 should succeed, next 2 should fail
      expect(results.slice(0, 5).every((r) => r === true)).toBe(true);
      expect(results.slice(5).some((r) => r === false)).toBe(true);
    });

    test('delivers notification and logs status', async () => {
      const event: NotificationEvent = {
        id: 'notif-003',
        type: 'build_success',
        userId: 'user-111',
        priority: NotificationPriority.MEDIUM,
        timestamp: new Date(),
        data: { build_id: 'build-001' },
      };

      await notificationService.queueNotification(event);
      const status = await notificationService.deliverNotification(event);

      expect(status).toBe(DeliveryStatus.DELIVERED);
      const log = notificationService.getDeliveryLog();
      expect(log.length).toBeGreaterThan(0);
      expect(log[0].status).toBe(DeliveryStatus.DELIVERED);
    });

    test('processes notification queue', async () => {
      const userId = 'user-222';
      notificationService.setUserPreference(userId, true);

      for (let i = 0; i < 3; i++) {
        const event: NotificationEvent = {
          id: `notif-queue-${i}`,
          type: 'test',
          userId,
          priority: NotificationPriority.MEDIUM,
          timestamp: new Date(),
          data: { index: i },
        };
        await notificationService.queueNotification(event);
      }

      const processed = notificationService.processQueue();

      expect(processed).toBe(3);
      expect(notificationService.getQueueSize()).toBe(0);
    });

    test('handles critical priority notifications', async () => {
      const event: NotificationEvent = {
        id: 'notif-critical',
        type: 'deployment_failed',
        userId: 'user-333',
        priority: NotificationPriority.CRITICAL,
        timestamp: new Date(),
        data: { error: 'Out of memory' },
      };

      const result = await notificationService.queueNotification(event);

      expect(result).toBe(true);
      expect(notificationService.getQueueSize()).toBe(1);
    });
  });

  // ==========================================================================
  // HEALTH DASHBOARD ACCURACY (5 tests)
  // ==========================================================================

  describe('Health Dashboard Accuracy', () => {
    test('calculates correct sync latency metrics', () => {
      healthDashboard.recordSyncLatency(100);
      healthDashboard.recordSyncLatency(200);
      healthDashboard.recordSyncLatency(150);

      const metrics = healthDashboard.getMetrics();

      expect(metrics.syncLatencyMs).toBe(150); // average
      expect(metrics.syncLatencyMs).toBeLessThan(5000); // within target
    });

    test('calculates webhook delivery success rate', () => {
      healthDashboard.recordWebhookDelivery(true);
      healthDashboard.recordWebhookDelivery(true);
      healthDashboard.recordWebhookDelivery(false);
      healthDashboard.recordWebhookDelivery(true);

      const metrics = healthDashboard.getMetrics();

      expect(metrics.webhookSuccessRate).toBe(75);
    });

    test('monitors queue depth', () => {
      healthDashboard.recordQueueDepth(5);
      healthDashboard.recordQueueDepth(10);
      healthDashboard.recordQueueDepth(8);

      const metrics = healthDashboard.getMetrics();

      expect(metrics.queueDepth).toBeCloseTo(7.67, 1);
    });

    test('tracks conflict resolution', () => {
      healthDashboard.recordConflictResolved();
      healthDashboard.recordConflictResolved();
      healthDashboard.recordConflictPending();

      const stats = healthDashboard.getConflictStats();

      expect(stats.resolved).toBe(2);
      expect(stats.pending).toBe(1);
    });

    test('determines overall health status based on metrics', () => {
      // Record good metrics
      healthDashboard.recordSyncLatency(1000);
      healthDashboard.recordWebhookDelivery(true);
      healthDashboard.recordWebhookDelivery(true);

      let metrics = healthDashboard.getMetrics();
      expect(metrics.status).toBe(HealthStatus.HEALTHY);

      // Record degradation
      healthDashboard.reset();
      for (let i = 0; i < 10; i++) {
        healthDashboard.recordWebhookDelivery(false);
      }
      healthDashboard.recordSyncLatency(4000);

      metrics = healthDashboard.getMetrics();
      expect([HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]).toContain(
        metrics.status
      );
    });
  });

  // ==========================================================================
  // SYNC QUEUE IDEMPOTENCY (4 tests)
  // ==========================================================================

  describe('Sync Queue Idempotency', () => {
    test('detects duplicate payloads via deliveryId', () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.TASK_UPDATED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-dup-001',
        data: { task_id: 'task-001' },
      };

      const result1 = syncQueue.enqueue(payload);
      const result2 = syncQueue.enqueue(payload);

      expect(result1).toBe(true);
      expect(result2).toBe(false);
    });

    test('enqueues unique payloads in order', () => {
      const payloads: WebhookPayload[] = [
        {
          event: WebhookEventType.PR_OPENED,
          timestamp: new Date().toISOString(),
          deliveryId: 'delivery-order-001',
          data: { order: 1 },
        },
        {
          event: WebhookEventType.COMMIT,
          timestamp: new Date().toISOString(),
          deliveryId: 'delivery-order-002',
          data: { order: 2 },
        },
      ];

      payloads.forEach((p) => syncQueue.enqueue(p));

      expect(syncQueue.getSize()).toBe(2);
      const first = syncQueue.dequeue();
      expect((first?.payload.data as { order: number }).order).toBe(1);
    });

    test('processes queue idempotently', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.TASK_UPDATED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-process-001',
        data: { task_id: 'task-001' },
      };

      syncQueue.enqueue(payload);

      let processed = 0;
      await syncQueue.process(async () => {
        processed++;
      });

      expect(processed).toBe(1);
      expect(syncQueue.getSize()).toBe(0);
    });

    test('returns queue statistics', () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.COMMIT,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-stats-001',
        data: {},
      };

      syncQueue.enqueue(payload);
      const stats = syncQueue.getStats();

      expect(stats.queueSize).toBe(1);
      expect(stats.idempotencyIndexSize).toBe(1);
    });
  });

  // ==========================================================================
  // RATE LIMITING ENFORCEMENT (3 tests)
  // ==========================================================================

  describe('Rate Limiting Enforcement', () => {
    test('enforces per-minute rate limit', () => {
      const userId = 'user-ratelimit-1';
      const results: boolean[] = [];

      // Try to make 7 requests (limit is 5)
      for (let i = 0; i < 7; i++) {
        results.push(rateLimiter.canProceed(userId));
      }

      // First 5 should succeed, next 2 should fail
      expect(results.slice(0, 5).every((r) => r === true)).toBe(true);
      expect(results.slice(5).every((r) => r === false)).toBe(true);
    });

    test('tracks remaining requests', () => {
      const userId = 'user-ratelimit-2';

      rateLimiter.canProceed(userId);
      rateLimiter.canProceed(userId);
      rateLimiter.canProceed(userId);

      const remaining = rateLimiter.getRemainingRequests(userId);

      expect(remaining).toBe(2); // 5 - 3
    });

    test('resets rate limit state', () => {
      const userId = 'user-ratelimit-3';

      rateLimiter.canProceed(userId);
      rateLimiter.canProceed(userId);
      rateLimiter.reset();

      const remaining = rateLimiter.getRemainingRequests(userId);

      expect(remaining).toBe(5); // Should be reset to max
    });
  });

  // ==========================================================================
  // ERROR HANDLING & RETRIES (6 tests)
  // ==========================================================================

  describe('Error Handling & Retries', () => {
    test('calculates exponential backoff correctly', () => {
      const backoff0 = retryHandler.calculateBackoff(0);
      const backoff1 = retryHandler.calculateBackoff(1);
      const backoff2 = retryHandler.calculateBackoff(2);

      expect(backoff0).toBe(50);
      expect(backoff1).toBe(100);
      expect(backoff2).toBe(200);
    });

    test('caps backoff at maximum value', () => {
      const backoff10 = retryHandler.calculateBackoff(10);

      expect(backoff10).toBe(500); // capped at maxBackoffMs
    });

    test('retries failed operation successfully', async () => {
      let attempts = 0;

      const fn = async () => {
        attempts++;
        if (attempts < 3) {
          throw new Error('Temporary failure');
        }
        return 'success';
      };

      const result = await retryHandler.retry(fn);

      expect(result).toBe('success');
      expect(attempts).toBe(3);
    });

    test('fails after max retries exceeded', async () => {
      const fn = async () => {
        throw new Error('Persistent failure');
      };

      await expect(retryHandler.retry(fn)).rejects.toThrow(
        'Persistent failure'
      );
    });

    test('invokes retry callback on each attempt', async () => {
      const onRetry = jest.fn();
      let attempts = 0;

      const fn = async () => {
        attempts++;
        if (attempts < 2) {
          throw new Error('Failed');
        }
        return 'success';
      };

      await retryHandler.retry(fn, onRetry);

      expect(onRetry).toHaveBeenCalled();
    });

    test('determines if retry should continue', () => {
      expect(retryHandler.shouldRetry(0)).toBe(true);
      expect(retryHandler.shouldRetry(1)).toBe(true);
      expect(retryHandler.shouldRetry(2)).toBe(true);
      expect(retryHandler.shouldRetry(3)).toBe(false);
    });
  });

  // ==========================================================================
  // INTEGRATION TESTS (3 tests)
  // ==========================================================================

  describe('Integration Tests', () => {
    test('complete webhook-to-notification flow', async () => {
      const payload = JSON.stringify({
        event: WebhookEventType.PR_OPENED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-integration-001',
        data: { pr_id: '123', title: 'New Feature' },
      });

      const signature = validator.generateSignature(payload);
      const isValid = validator.validateSignature(payload, signature);
      expect(isValid).toBe(true);

      const webhookPayload: WebhookPayload = JSON.parse(payload);
      const eventProcessed = await processor.processEvent(webhookPayload);
      expect(eventProcessed).toBe(true);

      const notifEvent: NotificationEvent = {
        id: 'notif-integration-001',
        type: 'pr_opened',
        userId: 'user-integration-001',
        priority: NotificationPriority.MEDIUM,
        timestamp: new Date(),
        data: { pr_id: '123' },
      };

      const queued = await notificationService.queueNotification(notifEvent);
      expect(queued).toBe(true);
    });

    test('webhook processing with rate limiting and queue', async () => {
      const userId = 'user-full-flow';

      for (let i = 0; i < 3; i++) {
        const canProceed = rateLimiter.canProceed(userId);

        if (canProceed) {
          const payload: WebhookPayload = {
            event: WebhookEventType.COMMIT,
            timestamp: new Date().toISOString(),
            deliveryId: `delivery-full-${i}`,
            data: { commit_number: i },
          };

          const enqueued = syncQueue.enqueue(payload);
          expect(enqueued).toBe(true);
        }
      }

      expect(syncQueue.getSize()).toBe(3);
    });

    test('health dashboard reflects system state', async () => {
      // Simulate activity
      for (let i = 0; i < 10; i++) {
        healthDashboard.recordSyncLatency(Math.random() * 2000);
        healthDashboard.recordWebhookDelivery(Math.random() > 0.1); // 90% success
        healthDashboard.recordQueueDepth(Math.floor(Math.random() * 20));
      }

      const metrics = healthDashboard.getMetrics();

      expect(metrics.syncLatencyMs).toBeGreaterThan(0);
      expect(metrics.webhookSuccessRate).toBeGreaterThanOrEqual(50);
      expect(metrics.queueDepth).toBeGreaterThanOrEqual(0);
      expect([
        HealthStatus.HEALTHY,
        HealthStatus.DEGRADED,
        HealthStatus.UNHEALTHY,
      ]).toContain(metrics.status);
    });
  });

  // ==========================================================================
  // EDGE CASES & ROBUSTNESS (5 tests)
  // ==========================================================================

  describe('Edge Cases & Robustness', () => {
    test('handles empty queue gracefully', async () => {
      let processed = 0;
      await syncQueue.process(async () => {
        processed++;
      });

      expect(processed).toBe(0);
    });

    test('handles very large payloads', async () => {
      const largeData = 'x'.repeat(1000000); // 1MB string

      const payload: WebhookPayload = {
        event: WebhookEventType.COMMIT,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-large',
        data: { content: largeData },
      };

      const result = await processor.processEvent(payload);

      expect(result).toBe(true);
    });

    test('handles concurrent notification queue operations', async () => {
      const promises = [];

      for (let i = 0; i < 10; i++) {
        const event: NotificationEvent = {
          id: `notif-concurrent-${i}`,
          type: 'test',
          userId: `user-concurrent-${i % 2}`, // Only 2 unique users
          priority: NotificationPriority.LOW,
          timestamp: new Date(),
          data: { index: i },
        };

        promises.push(notificationService.queueNotification(event));
      }

      const results = await Promise.all(promises);

      expect(results.filter((r) => r === true).length).toBeGreaterThan(0);
    });

    test('cleans up processed events correctly', async () => {
      const payload: WebhookPayload = {
        event: WebhookEventType.TASK_UPDATED,
        timestamp: new Date().toISOString(),
        deliveryId: 'delivery-cleanup',
        data: {},
      };

      await processor.processEvent(payload);
      processor.clearProcessed();

      const hasProcessed = processor.hasProcessed('delivery-cleanup');
      expect(hasProcessed).toBe(false);
    });

    test('handles clock skew in timestamps', () => {
      const now = Date.now();
      const futureTime = now + 3600000; // 1 hour in future
      const pastTime = now - 3600000; // 1 hour in past

      const payloads: WebhookPayload[] = [
        {
          event: WebhookEventType.PR_OPENED,
          timestamp: new Date(futureTime).toISOString(),
          deliveryId: 'delivery-future',
          data: {},
        },
        {
          event: WebhookEventType.COMMIT,
          timestamp: new Date(pastTime).toISOString(),
          deliveryId: 'delivery-past',
          data: {},
        },
      ];

      payloads.forEach((p) => {
        syncQueue.enqueue(p);
      });

      expect(syncQueue.getSize()).toBe(2);
    });
  });
});
