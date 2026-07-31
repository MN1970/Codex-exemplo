/**
 * Testes para CIOrchestratorService
 */

import {
  CIOrchestratorService,
  createCIOrchestratorService,
  WorkflowRunStatus,
  WorkflowConclusion,
} from "../ci-orchestrator";

// Mock do fetch global
global.fetch = jest.fn();

describe("CIOrchestratorService", () => {
  let orchestrator: CIOrchestratorService;
  const mockConfig = {
    githubToken: "test-token-xyz",
    owner: "manta-associados",
    repo: "codex-exemplo",
    workflowId: "ci.yml",
    pollingIntervalMs: 100, // Reduzido para testes
    maxWaitMs: 5000, // Reduzido para testes
  };

  beforeEach(() => {
    orchestrator = new CIOrchestratorService(mockConfig);
    jest.clearAllMocks();
  });

  describe("Initialization", () => {
    it("should create orchestrator with valid config", () => {
      expect(orchestrator).toBeDefined();
    });

    it("should adjust polling interval if too short", () => {
      expect(() => {
        new CIOrchestratorService({
          ...mockConfig,
          pollingIntervalMs: 2000, // Too short
        });
      }).not.toThrow();
    });

    it("should throw if maxWaitMs < pollingIntervalMs", () => {
      expect(() => {
        new CIOrchestratorService({
          ...mockConfig,
          pollingIntervalMs: 10000,
          maxWaitMs: 5000,
        });
      }).toThrow("maxWaitMs must be >= pollingIntervalMs");
    });

    it("should create via factory function", () => {
      const instance = createCIOrchestratorService(mockConfig);
      expect(instance).toBeInstanceOf(CIOrchestratorService);
    });
  });

  describe("Trigger Workflow", () => {
    it("should trigger workflow successfully", async () => {
      // Mock do dispatch endpoint retornando 204
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 204,
        ok: true,
      });

      // Mock do getLatestWorkflowRunId
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          workflow_runs: [{ id: 12345 }],
        }),
      });

      const runId = await orchestrator.triggerWorkflow("ci.yml", "main");

      expect(runId).toBe(12345);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/dispatches"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "token test-token-xyz",
          }),
        })
      );
    });

    it("should handle workflow not found", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 422,
        statusText: "Unprocessable Entity",
        ok: false,
      });

      await expect(
        orchestrator.triggerWorkflow("nonexistent.yml")
      ).rejects.toThrow("Workflow not found or invalid branch");
    });

    it("should handle API errors", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 500,
        statusText: "Internal Server Error",
        ok: false,
        json: async () => ({ message: "Server error" }),
      });

      await expect(
        orchestrator.triggerWorkflow("ci.yml")
      ).rejects.toThrow("Failed to trigger workflow");
    });

    it("should pass workflow inputs", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 204,
        ok: true,
      });

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          workflow_runs: [{ id: 12345 }],
        }),
      });

      const inputs = { debug: "true", ref: "develop" };
      await orchestrator.triggerWorkflow("ci.yml", "main", inputs);

      const callBody = JSON.parse(
        (global.fetch as jest.Mock).mock.calls[0][1].body
      );
      expect(callBody.inputs).toEqual(inputs);
    });
  });

  describe("Monitor Workflow Run", () => {
    it("should complete successfully when workflow passes", async () => {
      const mockLogs = `
Tests: 42 passed, 0 failed, 2 skipped
Lines: 85.5% | Statements: 85.0% | Functions: 90.2% | Branches: 80.1%
      `;

      // Simula polling: completado imediatamente para testes
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 12345,
            name: "CI",
            head_branch: "main",
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:60Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 67890, name: "build-test" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => mockLogs,
        });

      const result = await orchestrator.monitorWorkflowRun(12345, "ci.yml");

      expect(result.status).toBe("success");
      expect(result.conclusion).toBe(WorkflowConclusion.SUCCESS);
      expect(result.workflowStatus).toBe(WorkflowRunStatus.COMPLETED);
      expect(result.buildOutput.testResults?.passed).toBe(42);
      expect(result.buildOutput.testResults?.failed).toBe(0);
      expect(result.buildOutput.coverage?.lines).toBe(85.5);
    });

    it("should handle workflow failure", async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 12345,
            status: "completed",
            conclusion: "failure",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:01:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 67890, name: "build-test" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => "Build failed: test suite error",
        });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.status).toBe("failure");
      expect(result.conclusion).toBe(WorkflowConclusion.FAILURE);
    });

    it("should timeout after maxWaitMs", async () => {
      // Sempre retorna in_progress
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          id: 12345,
          status: "in_progress",
          conclusion: null,
          created_at: "2025-07-31T10:00:00Z",
          updated_at: "2025-07-31T10:00:00Z",
        }),
      });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.status).toBe("failure");
      expect(result.workflowStatus).toBe(WorkflowRunStatus.TIMED_OUT);
      expect(result.error).toContain("timed out");
    });

    it("should handle API errors during monitoring", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: "Not Found",
      });

      const result = await orchestrator.monitorWorkflowRun(99999);

      expect(result.status).toBe("failure");
      expect(result.error).toBeDefined();
    });
  });

  describe("Parse Test Results", () => {
    it("should parse basic test results", async () => {
      const logs = `
        > jest
        PASS  src/__tests__/service.test.ts
        Tests: 42 passed, 0 failed, 2 skipped
        Test Suites: 5 passed, 5 total
        Duration: 2.345s
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "test" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => logs,
        });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.buildOutput.testResults).toBeDefined();
      expect(result.buildOutput.testResults?.passed).toBe(42);
      expect(result.buildOutput.testResults?.failed).toBe(0);
      expect(result.buildOutput.testResults?.skipped).toBe(2);
    });

    it("should handle alternative test format", async () => {
      const logs = `
Test Results:
{
  "numPassedTests": 38,
  "numFailedTests": 2,
  "numTotalTests": 40
}
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 54321,
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "test" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => logs,
        });

      const result = await orchestrator.monitorWorkflowRun(54321);

      expect(result.buildOutput.testResults?.passed).toBe(38);
      expect(result.buildOutput.testResults?.failed).toBe(2);
    });
  });

  describe("Parse Coverage", () => {
    it("should parse coverage metrics", async () => {
      const logs = `
        Coverage:
        Lines: 87.25% | Statements: 86.90% | Functions: 92.10% | Branches: 81.50%
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "coverage" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => logs,
        });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.buildOutput.coverage).toBeDefined();
      expect(result.buildOutput.coverage?.lines).toBeCloseTo(87.25, 1);
      expect(result.buildOutput.coverage?.statements).toBeCloseTo(86.9, 1);
      expect(result.buildOutput.coverage?.functions).toBeCloseTo(92.1, 1);
      expect(result.buildOutput.coverage?.branches).toBeCloseTo(81.5, 1);
    });
  });

  describe("Parse Lint Errors", () => {
    it("should parse ESLint errors", async () => {
      const logs = `
        src/index.ts:42:10: error - Unexpected var statement (no-var)
        src/utils.ts:15:5: warning - Unused variable 'x' (no-unused-vars)
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            status: "completed",
            conclusion: "failure",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "lint" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => logs,
        });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.buildOutput.lintErrors).toBeDefined();
      expect(result.buildOutput.lintErrors?.length).toBeGreaterThan(0);

      const firstError = result.buildOutput.lintErrors?.[0];
      expect(firstError?.file).toBe("src/index.ts");
      expect(firstError?.line).toBe(42);
      expect(firstError?.column).toBe(10);
      expect(firstError?.severity).toBe("error");
      expect(firstError?.rule).toBe("no-var");
    });
  });

  describe("Execute Workflow", () => {
    it("should execute complete workflow flow", async () => {
      // Mock trigger
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 204,
        ok: true,
      });

      // Mock getLatestWorkflowRunId
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          workflow_runs: [{ id: 12345 }],
        }),
      });

      // Mock monitor - status progression
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "test" }],
          }),
        })
        // Job logs
        .mockResolvedValueOnce({
          ok: true,
          text: async () => "Tests: 100 passed, 0 failed",
        });

      const result = await orchestrator.executeWorkflow("ci.yml", "main", {
        debug: "true",
      });

      expect(result.status).toBe("success");
      expect(result.workflowRunId).toBe(12345);
    });
  });

  describe("Metrics", () => {
    it("should track metrics correctly", async () => {
      const initialMetrics = orchestrator.getMetrics();

      expect(initialMetrics.totalWorkflowsTriggered).toBe(0);
      expect(initialMetrics.successCount).toBe(0);
      expect(initialMetrics.failureCount).toBe(0);
    });

    it("should reset metrics", () => {
      orchestrator.resetMetrics();
      const metrics = orchestrator.getMetrics();

      expect(metrics.totalWorkflowsTriggered).toBe(0);
      expect(metrics.successCount).toBe(0);
      expect(metrics.failureCount).toBe(0);
      expect(metrics.timeoutCount).toBe(0);
    });
  });

  describe("Error Handling", () => {
    it("should handle network errors", async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error("Network error")
      );

      await expect(
        orchestrator.triggerWorkflow("ci.yml")
      ).rejects.toThrow("Error triggering workflow");
    });

    it("should handle expired logs gracefully", async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            status: "completed",
            conclusion: "success",
            created_at: "2025-07-31T10:00:00Z",
            updated_at: "2025-07-31T10:00:00Z",
          }),
        })
        // Jobs
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            jobs: [{ id: 1, name: "test" }],
          }),
        })
        // Job logs - 410 Gone
        .mockResolvedValueOnce({
          ok: false,
          status: 410,
          statusText: "Gone",
        });

      const result = await orchestrator.monitorWorkflowRun(12345);

      expect(result.buildOutput.logs).toContain("[Logs expired]");
    });
  });
});
