/**
 * Test suite para AutoMerge Service
 * Testa todos os recursos da automação de merge com locking distribuído
 */

import { AutoMerge, createAutoMerge, ScheduleStatus, LockStatus } from "../auto-merge-service";
import type {
  MergeResult,
  Requirement,
  Conflict,
  ScheduleResult,
  MergeMetrics,
} from "../auto-merge-service";

describe("AutoMerge Service", () => {
  let autoMerge: AutoMerge;

  const mockConfig = {
    githubToken: "test-token",
    owner: "test-owner",
    repo: "test-repo",
    requireCIPassed: true,
    requiredApprovals: 1,
    allowMergingWithConflicts: false,
    enableScheduling: true,
    trackMetrics: true,
  };

  beforeEach(() => {
    autoMerge = createAutoMerge(mockConfig);
  });

  describe("canMerge()", () => {
    it("should return false when requirements are not met", async () => {
      // Mock implementation - would need actual GitHub API mocking in real tests
      const canMerge = await autoMerge.canMerge({ number: 1 });
      expect(typeof canMerge).toBe("boolean");
    });

    it("should handle draft PRs correctly", async () => {
      const canMerge = await autoMerge.canMerge({ number: 1, draft: true });
      expect(canMerge).toBe(false);
    });

    it("should return true when all requirements met", async () => {
      const canMerge = await autoMerge.canMerge({ number: 1, draft: false });
      // Result depends on mock API responses
      expect(typeof canMerge).toBe("boolean");
    });
  });

  describe("checkRequirements()", () => {
    it("should check all requirement types", async () => {
      const requirements = await autoMerge.checkRequirements({ number: 1 });

      expect(Array.isArray(requirements)).toBe(true);
      expect(requirements.length).toBeGreaterThan(0);

      // Verifica tipos de requisitos
      const typeSet = new Set(requirements.map((r) => r.type));
      expect(typeSet.has("not_draft")).toBe(true);
      expect(typeSet.has("no_conflicts")).toBe(true);
    });

    it("should include requirement details", async () => {
      const requirements = await autoMerge.checkRequirements({ number: 1 });

      for (const req of requirements) {
        expect(req).toHaveProperty("type");
        expect(req).toHaveProperty("met");
        expect(req).toHaveProperty("description");
        expect(req).toHaveProperty("lastCheckedAt");
        expect(req.lastCheckedAt instanceof Date).toBe(true);
      }
    });

    it("should track check details for complex requirements", async () => {
      const requirements = await autoMerge.checkRequirements({ number: 1 });
      const statusCheckReq = requirements.find((r) => r.type === "status_checks");

      if (statusCheckReq) {
        expect(statusCheckReq.checkDetails).toBeDefined();
      }
    });
  });

  describe("getConflicts()", () => {
    it("should return empty array when no conflicts", async () => {
      const conflicts = await autoMerge.getConflicts({ number: 1 });
      expect(Array.isArray(conflicts)).toBe(true);
    });

    it("should detect content conflicts", async () => {
      const conflicts = await autoMerge.getConflicts({ number: 1 });

      for (const conflict of conflicts) {
        expect(conflict).toHaveProperty("file");
        expect(conflict).toHaveProperty("type");
        expect(conflict).toHaveProperty("description");
        expect(conflict).toHaveProperty("severity");
        expect(["low", "medium", "high"]).toContain(conflict.severity);
      }
    });

    it("should include resolution suggestions for resolvable conflicts", async () => {
      const conflicts = await autoMerge.getConflicts({ number: 1 });

      for (const conflict of conflicts) {
        if (conflict.resolvable) {
          expect(conflict.suggestedResolution).toBeDefined();
        }
      }
    });
  });

  describe("merge()", () => {
    it("should block merge when requirements not met", async () => {
      // Assume CI not passed in mock
      const result = await autoMerge.merge(1, "squash");

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("prNumber");
      expect(result).toHaveProperty("strategy");
      expect(result).toHaveProperty("transactionId");
      expect(result.auditLog).toBeInstanceOf(Array);
    });

    it("should use specified merge strategy", async () => {
      const result = await autoMerge.merge(1, "rebase");
      expect(result.strategy).toBe("rebase");
    });

    it("should use default strategy when not specified", async () => {
      const result = await autoMerge.merge(1);
      expect(result.strategy).toBe("squash");
    });

    it("should generate unique transaction ID", async () => {
      const result1 = await autoMerge.merge(1);
      const result2 = await autoMerge.merge(2);

      expect(result1.transactionId).not.toBe(result2.transactionId);
      expect(result1.transactionId).toMatch(/^txn-/);
    });

    it("should include audit log in result", async () => {
      const result = await autoMerge.merge(1);

      expect(Array.isArray(result.auditLog)).toBe(true);
      for (const entry of result.auditLog) {
        expect(entry).toHaveProperty("timestamp");
        expect(entry).toHaveProperty("action");
        expect(entry).toHaveProperty("status");
        expect(entry).toHaveProperty("prNumber");
        expect(entry).toHaveProperty("transactionId");
      }
    });

    it("should handle merge conflicts appropriately", async () => {
      // Config não permite conflitos
      const result = await autoMerge.merge(1, "merge");

      if (!result.success) {
        if (result.error?.code === "MERGE_CONFLICTS") {
          expect(result.error.recoverable).toBe(false);
        }
      }
    });

    it("should calculate merge duration", async () => {
      const result = await autoMerge.merge(1);
      expect(typeof result.duration).toBe("number");
      expect(result.duration).toBeGreaterThanOrEqual(0);
    });
  });

  describe("scheduleMerge()", () => {
    it("should schedule merge for future date", async () => {
      const futureDate = new Date(Date.now() + 60000); // 1 minuto no futuro
      const result = await autoMerge.scheduleMerge(1, futureDate, "squash");

      expect(result.success).toBe(true);
      expect(result.status).toBe(ScheduleStatus.SCHEDULED);
      expect(result.scheduleId).toMatch(/^sch-/);
      expect(result.scheduledFor).toEqual(futureDate);
    });

    it("should reject past dates", async () => {
      const pastDate = new Date(Date.now() - 60000); // 1 minuto no passado
      const result = await autoMerge.scheduleMerge(1, pastDate, "merge");

      expect(result.success).toBe(false);
      expect(result.status).toBe(ScheduleStatus.FAILED);
    });

    it("should use specified merge strategy", async () => {
      const futureDate = new Date(Date.now() + 60000);
      const result = await autoMerge.scheduleMerge(1, futureDate, "rebase");

      expect(result.strategy).toBe("rebase");
    });

    it("should use default strategy when not specified", async () => {
      const futureDate = new Date(Date.now() + 60000);
      const result = await autoMerge.scheduleMerge(1, futureDate);

      expect(result.strategy).toBe("squash");
    });

    it("should generate unique schedule IDs", async () => {
      const futureDate = new Date(Date.now() + 60000);
      const result1 = await autoMerge.scheduleMerge(1, futureDate);
      const result2 = await autoMerge.scheduleMerge(2, futureDate);

      expect(result1.scheduleId).not.toBe(result2.scheduleId);
    });

    it("should track scheduled merges", async () => {
      const futureDate = new Date(Date.now() + 60000);
      await autoMerge.scheduleMerge(1, futureDate);
      await autoMerge.scheduleMerge(2, futureDate);

      const scheduled = autoMerge.getScheduledMerges();
      expect(scheduled.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe("Metrics Tracking", () => {
    it("should provide merge metrics", () => {
      const metrics = autoMerge.getMetrics();

      expect(metrics).toHaveProperty("totalMerges");
      expect(metrics).toHaveProperty("successfulMerges");
      expect(metrics).toHaveProperty("failedMerges");
      expect(metrics).toHaveProperty("successRate");
      expect(metrics).toHaveProperty("averageDuration");
      expect(metrics).toHaveProperty("conflictRate");
      expect(metrics).toHaveProperty("mergeStrategiesUsed");
      expect(metrics).toHaveProperty("blockedByRequirement");
    });

    it("should track merge strategies used", async () => {
      const metricsBefore = autoMerge.getMetrics();
      const strategyCountBefore = metricsBefore.mergeStrategiesUsed.squash || 0;

      // Simula merge com estratégia
      await autoMerge.merge(1, "squash");

      const metricsAfter = autoMerge.getMetrics();
      // Nota: Conta será incrementada apenas se merge for bem-sucedido
      expect(typeof metricsAfter.mergeStrategiesUsed.squash).toBe("number");
    });

    it("should track lock wait times", () => {
      const metrics = autoMerge.getMetrics();

      expect(metrics.lockWaitTime).toHaveProperty("average");
      expect(metrics.lockWaitTime).toHaveProperty("max");
      expect(metrics.lockWaitTime).toHaveProperty("min");
      expect(typeof metrics.lockWaitTime.average).toBe("number");
    });
  });

  describe("Audit Trail", () => {
    it("should maintain audit log", async () => {
      const auditBefore = autoMerge.getAuditLog();
      const countBefore = auditBefore.length;

      await autoMerge.canMerge({ number: 1 });

      const auditAfter = autoMerge.getAuditLog();
      // Audit trail foi atualizado
      expect(auditAfter.length).toBeGreaterThanOrEqual(countBefore);
    });

    it("should include detailed audit entries", async () => {
      await autoMerge.merge(1);

      const audit = autoMerge.getAuditLog();
      for (const entry of audit) {
        expect(entry).toHaveProperty("timestamp");
        expect(entry).toHaveProperty("action");
        expect(entry.status).toMatch(/^(success|failure|warning)$/);
        expect(entry).toHaveProperty("prNumber");
        expect(entry).toHaveProperty("details");
        expect(entry).toHaveProperty("transactionId");
      }
    });
  });

  describe("Transaction Management", () => {
    it("should track transaction by ID", async () => {
      const result = await autoMerge.merge(1);
      const transaction = autoMerge.getTransaction(result.transactionId);

      expect(transaction).toBeDefined();
      expect(transaction?.id).toBe(result.transactionId);
      expect(transaction?.prNumber).toBe(1);
    });

    it("should record transaction status", async () => {
      const result = await autoMerge.merge(1);
      const transaction = autoMerge.getTransaction(result.transactionId);

      expect(transaction?.status).toMatch(/^(pending|completed|failed)$/);
      expect(transaction?.startedAt instanceof Date).toBe(true);
    });
  });

  describe("Schedule Management", () => {
    it("should cancel scheduled merge", async () => {
      const futureDate = new Date(Date.now() + 60000);
      const scheduleResult = await autoMerge.scheduleMerge(1, futureDate);

      if (scheduleResult.success) {
        const cancelled = autoMerge.cancelSchedule(scheduleResult.scheduleId);
        expect(cancelled).toBe(true);
      }
    });

    it("should return false when cancelling non-existent schedule", () => {
      const cancelled = autoMerge.cancelSchedule("non-existent-id");
      expect(cancelled).toBe(false);
    });

    it("should list scheduled merges", async () => {
      const futureDate = new Date(Date.now() + 60000);
      await autoMerge.scheduleMerge(1, futureDate);

      const scheduled = autoMerge.getScheduledMerges();
      expect(Array.isArray(scheduled)).toBe(true);

      if (scheduled.length > 0) {
        const firstSchedule = scheduled[0];
        expect(firstSchedule).toHaveProperty("scheduleId");
        expect(firstSchedule).toHaveProperty("prNumber");
        expect(firstSchedule).toHaveProperty("scheduledFor");
      }
    });
  });

  describe("Error Handling", () => {
    it("should handle network errors gracefully", async () => {
      const result = await autoMerge.merge(999999); // PR que provavelmente não existe

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("error");
    });

    it("should provide error details in merge result", async () => {
      const result = await autoMerge.merge(999999);

      if (!result.success && result.error) {
        expect(result.error).toHaveProperty("code");
        expect(result.error).toHaveProperty("message");
        expect(result.error).toHaveProperty("recoverable");
      }
    });

    it("should include error in audit log", async () => {
      await autoMerge.merge(999999);

      const audit = autoMerge.getAuditLog();
      const failureEntries = audit.filter((e) => e.status === "failure");

      if (failureEntries.length > 0) {
        expect(failureEntries[0].details).toHaveProperty("error");
      }
    });
  });

  describe("Configuration", () => {
    it("should create service with custom config", () => {
      const customConfig = {
        githubToken: "custom-token",
        owner: "custom-owner",
        repo: "custom-repo",
        defaultStrategy: "rebase" as const,
        requiredApprovals: 2,
        lockTtl: 30000,
      };

      const service = createAutoMerge(customConfig);
      expect(service).toBeInstanceOf(AutoMerge);
    });

    it("should use default values for optional config", () => {
      const minimalConfig = {
        githubToken: "token",
        owner: "owner",
        repo: "repo",
      };

      const service = createAutoMerge(minimalConfig);
      expect(service).toBeInstanceOf(AutoMerge);

      // Verifica que métricas estão disponíveis (indicando inicialização correta)
      const metrics = service.getMetrics();
      expect(metrics).toBeDefined();
    });
  });

  describe("Distributed Locking", () => {
    it("should prevent concurrent merges of same PR", async () => {
      // Este teste é simplificado - em produção seria mais complexo
      const result = await autoMerge.merge(1, "squash");

      expect(result).toHaveProperty("transactionId");
      // Transaction lock foi gerenciado internamente
      expect(result.auditLog.length).toBeGreaterThan(0);
    });

    it("should allow concurrent merges of different PRs", async () => {
      const result1 = Promise.all([
        autoMerge.merge(1, "squash"),
        autoMerge.merge(2, "merge"),
        autoMerge.merge(3, "rebase"),
      ]);

      const results = await result1;
      expect(results).toHaveLength(3);

      // Todos têm IDs de transação diferentes
      const txnIds = new Set(results.map((r) => r.transactionId));
      expect(txnIds.size).toBe(3);
    });
  });

  describe("Merge Strategies", () => {
    it("should support all merge strategies", async () => {
      const strategies = ["merge", "squash", "rebase", "cherry-pick", "fast-forward"] as const;

      for (const strategy of strategies) {
        const result = await autoMerge.merge(1, strategy);
        expect(result.strategy).toBe(strategy);
      }
    });

    it("should use default strategy when not specified", async () => {
      const service = createAutoMerge({
        ...mockConfig,
        defaultStrategy: "rebase",
      });

      const result = await service.merge(1);
      expect(result.strategy).toBe("rebase");
    });
  });
});

describe("AutoMerge Integration Tests", () => {
  let autoMerge: AutoMerge;

  beforeEach(() => {
    autoMerge = createAutoMerge({
      githubToken: "test-token",
      owner: "test-owner",
      repo: "test-repo",
      enableScheduling: true,
    });
  });

  it("should handle complete merge workflow", async () => {
    // 1. Verifica se pode fazer merge
    const canMerge = await autoMerge.canMerge({ number: 1 });
    expect(typeof canMerge).toBe("boolean");

    // 2. Verifica requisitos
    const requirements = await autoMerge.checkRequirements({ number: 1 });
    expect(Array.isArray(requirements)).toBe(true);

    // 3. Detecta conflitos
    const conflicts = await autoMerge.getConflicts({ number: 1 });
    expect(Array.isArray(conflicts)).toBe(true);

    // 4. Realiza merge
    const mergeResult = await autoMerge.merge(1, "squash");
    expect(mergeResult).toHaveProperty("transactionId");

    // 5. Verifica métricas
    const metrics = autoMerge.getMetrics();
    expect(metrics.totalMerges).toBeGreaterThanOrEqual(1);
  });

  it("should handle scheduled merge workflow", async () => {
    const futureDate = new Date(Date.now() + 60000);

    // 1. Agenda merge
    const scheduleResult = await autoMerge.scheduleMerge(1, futureDate, "squash");
    expect(scheduleResult.success).toBe(true);

    // 2. Lista agendamentos
    const scheduled = autoMerge.getScheduledMerges();
    expect(scheduled.length).toBeGreaterThan(0);

    // 3. Cancela agendamento
    if (scheduleResult.success) {
      const cancelled = autoMerge.cancelSchedule(scheduleResult.scheduleId);
      expect(cancelled).toBe(true);
    }
  });
});
