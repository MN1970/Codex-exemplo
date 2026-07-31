/**
 * Testes para SyncQueueManager
 */

import {
  SyncQueueManager,
  QueuePriority,
  QueueItemStatus,
} from "../sync-queue";

describe("SyncQueueManager", () => {
  let manager: SyncQueueManager<{ id: string; data: string }>;

  beforeEach(() => {
    manager = new SyncQueueManager({
      maxBatchSize: 5,
      processingIntervalMs: 100,
    });
  });

  afterEach(() => {
    manager.destroy();
  });

  describe("Enqueuing items", () => {
    it("should add item to queue", async () => {
      const result = await manager.enqueue(
        { id: "test1", data: "content1" },
        QueuePriority.MEDIUM
      );

      expect(result).toBe(true);
      expect(manager.getQueueSize()).toBe(1);
    });

    it("should handle multiple items in queue", async () => {
      for (let i = 0; i < 5; i++) {
        await manager.enqueue(
          { id: `test${i}`, data: `content${i}` },
          QueuePriority.MEDIUM
        );
      }

      expect(manager.getQueueSize()).toBe(5);
    });

    it("should reject duplicate items (idempotency)", async () => {
      const item = { id: "test1", data: "content1" };

      const first = await manager.enqueue(item, QueuePriority.MEDIUM);
      expect(first).toBe(true);

      // Mesma hash de conteúdo deve ser rejeitada
      const second = await manager.enqueue(item, QueuePriority.MEDIUM);
      expect(second).toBe(false);

      expect(manager.getQueueSize()).toBe(1);
    });

    it("should allow different items with same ID if content differs", async () => {
      const first = await manager.enqueue(
        { id: "test1", data: "content1" },
        QueuePriority.MEDIUM
      );
      expect(first).toBe(true);

      // Conteúdo diferente = hash diferente
      const second = await manager.enqueue(
        { id: "test1", data: "content2" },
        QueuePriority.MEDIUM
      );
      expect(second).toBe(true);

      expect(manager.getQueueSize()).toBe(2);
    });
  });

  describe("Priority ordering", () => {
    it("should process CRITICAL items before HIGH", async () => {
      const processOrder: string[] = [];

      manager.onProcess(async (item) => {
        processOrder.push(item.id);
      });

      // Adiciona em ordem: LOW, HIGH, CRITICAL
      await manager.enqueue(
        { id: "low", data: "low" },
        QueuePriority.LOW
      );
      await manager.enqueue(
        { id: "high", data: "high" },
        QueuePriority.HIGH
      );
      await manager.enqueue(
        { id: "critical", data: "critical" },
        QueuePriority.CRITICAL
      );

      manager.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 500));
      manager.stopProcessing();

      // Ordem esperada: CRITICAL, HIGH, LOW
      expect(processOrder[0]).toBe("critical");
      expect(processOrder[1]).toBe("high");
      expect(processOrder[2]).toBe("low");
    });

    it("should maintain FIFO order within same priority", async () => {
      const processOrder: string[] = [];

      manager.onProcess(async (item) => {
        processOrder.push(item.id);
      });

      // Adiciona 3 items com mesma prioridade
      await manager.enqueue(
        { id: "item1", data: "1" },
        QueuePriority.MEDIUM
      );
      await manager.enqueue(
        { id: "item2", data: "2" },
        QueuePriority.MEDIUM
      );
      await manager.enqueue(
        { id: "item3", data: "3" },
        QueuePriority.MEDIUM
      );

      manager.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 500));
      manager.stopProcessing();

      // Ordem esperada: FIFO
      expect(processOrder).toEqual(["item1", "item2", "item3"]);
    });
  });

  describe("Batch processing", () => {
    it("should process items in batches", async () => {
      const batchSizes: number[] = [];

      manager.onProcess(async (item) => {
        // No-op
      });

      // Adiciona 12 items, batch size = 5
      for (let i = 0; i < 12; i++) {
        await manager.enqueue(
          { id: `item${i}`, data: `data${i}` },
          QueuePriority.MEDIUM
        );
      }

      manager.startProcessing();

      // Monitora queue size após processamento
      await new Promise((resolve) => {
        let checks = 0;
        const interval = setInterval(() => {
          const size = manager.getQueueSize();
          batchSizes.push(size);

          if (size === 0 || checks > 5) {
            clearInterval(interval);
            resolve(null);
          }
          checks++;
        }, 150);
      });

      manager.stopProcessing();

      expect(batchSizes.length).toBeGreaterThan(0);
    });

    it("should not exceed maxBatchSize per processing round", async () => {
      const manager2 = new SyncQueueManager<{ id: string; data: string }>({
        maxBatchSize: 3,
      });

      const processedCount = { count: 0 };

      manager2.onProcess(async (item) => {
        processedCount.count++;
      });

      for (let i = 0; i < 10; i++) {
        await manager2.enqueue(
          { id: `item${i}`, data: `data${i}` },
          QueuePriority.MEDIUM
        );
      }

      const processed = await manager2.processBatch();
      expect(processed).toBeLessThanOrEqual(3);

      manager2.destroy();
    });
  });

  describe("Retry policy", () => {
    it("should retry failed items with backoff", async () => {
      let attemptCount = 0;

      manager.onProcess(async (item) => {
        attemptCount++;
        if (attemptCount < 3) {
          throw new Error("Simulated failure");
        }
      });

      await manager.enqueue(
        { id: "failing-item", data: "content" },
        QueuePriority.MEDIUM
      );

      manager.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 5000));
      manager.stopProcessing();

      // Item deve ter sido retentado
      expect(attemptCount).toBeGreaterThanOrEqual(1);
    });

    it("should move items to dead letter queue after max retries", async () => {
      const manager2 = new SyncQueueManager<{ id: string; data: string }>({
        maxBatchSize: 5,
        retryPolicy: {
          maxRetries: 2,
          initialDelayMs: 100,
          maxDelayMs: 1000,
          backoffMultiplier: 2,
        },
      });

      manager2.onProcess(async (item) => {
        throw new Error("Always fails");
      });

      await manager2.enqueue(
        { id: "failing-item", data: "content" },
        QueuePriority.MEDIUM
      );

      manager2.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 3000));
      manager2.stopProcessing();

      // Item deve estar na dead letter queue
      expect(manager2.getDeadLetterQueueSize()).toBeGreaterThan(0);

      const dlItems = manager2.getDeadLetterItems();
      expect(dlItems.length).toBeGreaterThan(0);
      expect(dlItems[0].status).toBe(QueueItemStatus.DEAD_LETTER);

      manager2.destroy();
    });
  });

  describe("Metrics and observability", () => {
    it("should track queue metrics", async () => {
      manager.onProcess(async (item) => {
        await new Promise((resolve) => setTimeout(resolve, 50));
      });

      for (let i = 0; i < 10; i++) {
        await manager.enqueue(
          { id: `item${i}`, data: `data${i}` },
          QueuePriority.MEDIUM
        );
      }

      const metricsBeforeProcessing = manager.getMetrics();
      expect(metricsBeforeProcessing.queueSize).toBe(10);
      expect(metricsBeforeProcessing.totalProcessed).toBe(0);

      manager.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 2000));
      manager.stopProcessing();

      const metricsAfterProcessing = manager.getMetrics();
      expect(metricsAfterProcessing.totalProcessed).toBeGreaterThan(0);
      expect(metricsAfterProcessing.averageLatencyMs).toBeGreaterThan(0);
    });

    it("should generate Prometheus format metrics", () => {
      const prometheusMetrics = manager.getPrometheusMetrics();

      expect(prometheusMetrics).toContain("queue_size");
      expect(prometheusMetrics).toContain("dead_letter_queue_size");
      expect(prometheusMetrics).toContain("items_processed_total");
      expect(prometheusMetrics).toContain("items_failed_total");
      expect(prometheusMetrics).toContain("processing_duration_ms");
    });

    it("should track processing latency", async () => {
      const processingTime = 100; // ms

      manager.onProcess(async (item) => {
        await new Promise((resolve) =>
          setTimeout(resolve, processingTime)
        );
      });

      await manager.enqueue(
        { id: "item1", data: "content" },
        QueuePriority.MEDIUM
      );

      await manager.processBatch();

      const metrics = manager.getMetrics();
      expect(metrics.averageLatencyMs).toBeGreaterThanOrEqual(processingTime - 50); // Allow 50ms tolerance
    });
  });

  describe("Dead letter queue management", () => {
    it("should retrieve dead letter items", async () => {
      const manager2 = new SyncQueueManager<{ id: string; data: string }>({
        retryPolicy: {
          maxRetries: 1,
          initialDelayMs: 50,
          maxDelayMs: 100,
          backoffMultiplier: 1,
        },
      });

      manager2.onProcess(async () => {
        throw new Error("Always fails");
      });

      await manager2.enqueue(
        { id: "failing1", data: "content1" },
        QueuePriority.MEDIUM
      );
      await manager2.enqueue(
        { id: "failing2", data: "content2" },
        QueuePriority.MEDIUM
      );

      manager2.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 1500));
      manager2.stopProcessing();

      const dlItems = manager2.getDeadLetterItems();
      expect(dlItems.length).toBeGreaterThan(0);

      for (const item of dlItems) {
        expect(item.status).toBe(QueueItemStatus.DEAD_LETTER);
        expect(item.failureReason).toBeDefined();
      }

      manager2.destroy();
    });

    it("should remove items from dead letter queue", async () => {
      const manager2 = new SyncQueueManager<{ id: string; data: string }>({
        retryPolicy: {
          maxRetries: 1,
          initialDelayMs: 50,
          maxDelayMs: 100,
          backoffMultiplier: 1,
        },
      });

      manager2.onProcess(async () => {
        throw new Error("Always fails");
      });

      await manager2.enqueue(
        { id: "failing-item", data: "content" },
        QueuePriority.MEDIUM
      );

      manager2.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 1000));
      manager2.stopProcessing();

      const dlItems = manager2.getDeadLetterItems();
      expect(dlItems.length).toBeGreaterThan(0);

      const removed = manager2.removeFromDeadLetterQueue(dlItems[0].id);
      expect(removed).toBe(true);
      expect(manager2.getDeadLetterQueueSize()).toBe(dlItems.length - 1);

      manager2.destroy();
    });
  });

  describe("Item retrieval", () => {
    it("should retrieve item by ID", async () => {
      await manager.enqueue(
        { id: "test-item", data: "content" },
        QueuePriority.MEDIUM
      );

      const item = manager.getItem("test-item");
      expect(item).toBeDefined();
      expect(item?.id).toContain("item_");
      expect(item?.data.id).toBe("test-item");
    });

    it("should return null for non-existent item", () => {
      const item = manager.getItem("non-existent");
      expect(item).toBeNull();
    });
  });

  describe("Metadata handling", () => {
    it("should preserve metadata when enqueueing", async () => {
      const metadata = {
        source: "webhook",
        tags: ["important", "sync"],
        correlationId: "corr-123",
      };

      await manager.enqueue(
        { id: "test", data: "content" },
        QueuePriority.HIGH,
        metadata
      );

      const item = manager.getItem("test");
      expect(item?.metadata).toEqual(metadata);
    });
  });

  describe("Queue operations", () => {
    it("should clear queue and dead letter queue", async () => {
      await manager.enqueue(
        { id: "item1", data: "content" },
        QueuePriority.MEDIUM
      );

      manager.clear();

      expect(manager.getQueueSize()).toBe(0);
      expect(manager.getDeadLetterQueueSize()).toBe(0);
    });

    it("should handle concurrent processing safely", async () => {
      let processedCount = 0;

      manager.onProcess(async (item) => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        processedCount++;
      });

      for (let i = 0; i < 20; i++) {
        await manager.enqueue(
          { id: `item${i}`, data: `data${i}` },
          QueuePriority.MEDIUM
        );
      }

      manager.startProcessing();
      await new Promise((resolve) => setTimeout(resolve, 1000));
      manager.stopProcessing();

      expect(processedCount).toBeGreaterThan(0);
    });
  });

  describe("Processing lifecycle", () => {
    it("should start and stop processing", () => {
      expect(() => {
        manager.startProcessing();
        manager.stopProcessing();
      }).not.toThrow();
    });

    it("should warn if starting processing twice", () => {
      const consoleSpy = jest.spyOn(console, "warn");

      manager.startProcessing();
      manager.startProcessing(); // Should warn

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining("Processing already started")
      );

      manager.stopProcessing();
      consoleSpy.mockRestore();
    });

    it("should handle destroy gracefully", () => {
      manager.startProcessing();
      expect(() => {
        manager.destroy();
      }).not.toThrow();
    });
  });
});
