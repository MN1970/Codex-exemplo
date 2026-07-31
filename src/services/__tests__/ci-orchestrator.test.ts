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

    it(
      "should timeout after maxWaitMs",
      async () => {
        // This test verifies that monitoring times out after maxWaitMs
        // We set a very short timeout to test the timeout logic
        const shortTimeoutOrchestrator = new CIOrchestratorService({
          githubToken: mockConfig.githubToken,
          owner: mockConfig.owner,
          repo: mockConfig.repo,
          pollingIntervalMs: 5000, // Minimum adjusted value
          maxWaitMs: 5500, // Just slightly more than polling (test will timeout quickly)
        });

        // Always returns in_progress
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

        const result = await shortTimeoutOrchestrator.monitorWorkflowRun(
          12345,
          "ci.yml"
        );

        // Should timeout due to short maxWaitMs
        expect(result.status).toBe("failure");
        expect(result.workflowStatus).toBe(WorkflowRunStatus.TIMED_OUT);
      },
      15000 // 15s jest timeout for this test (accounts for polling delay)
    );

    it("should handle API errors during monitoring", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: "Not Found",
        status: 404,
      });

      const result = await orchestrator.monitorWorkflowRun(88888);

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
Coverage Report:
Lines: 87.25% | Statements: 86.90% | Functions: 92.10% | Branches: 81.50%
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 99999,
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

      const result = await orchestrator.monitorWorkflowRun(99999);

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
ESLint output:
src/index.ts:42:10: error - Unexpected var statement (no-var)
src/utils.ts:15:5: warning - Unused variable 'x' (no-unused-vars)
      `;

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 77777,
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

      const result = await orchestrator.monitorWorkflowRun(77777);

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
      const executeOrchestrator = createCIOrchestratorService({
        githubToken: "test-token",
        owner: "test-owner",
        repo: "test-repo",
        workflowId: "ci.yml",
        pollingIntervalMs: 100,
        maxWaitMs: 5000,
      });

      // Track call sequence
      let callSequence = 0;
      (global.fetch as jest.Mock).mockImplementation(async (url: string) => {
        callSequence++;

        // Dispatch trigger
        if (url.includes("/dispatches")) {
          return { status: 204, ok: true };
        }

        // Get latest workflow runs
        if (url.includes("/runs") && url.includes("per_page=1")) {
          return {
            ok: true,
            json: async () => ({
              workflow_runs: [{ id: 55555 }],
            }),
          };
        }

        // Get workflow status
        if (url.includes("/runs/55555") && !url.includes("/jobs")) {
          return {
            ok: true,
            json: async () => ({
              id: 55555,
              name: "CI",
              head_branch: "main",
              status: "completed",
              conclusion: "success",
              created_at: "2025-07-31T10:00:00Z",
              updated_at: "2025-07-31T10:00:00Z",
            }),
          };
        }

        // Get jobs
        if (url.includes("/jobs")) {
          return {
            ok: true,
            json: async () => ({
              jobs: [{ id: 1, name: "test" }],
            }),
          };
        }

        // Get logs
        if (url.includes("/jobs/1")) {
          return {
            ok: true,
            text: async () => "Tests: 100 passed, 0 failed",
          };
        }

        return { ok: false, status: 404 };
      });

      const result = await executeOrchestrator.executeWorkflow("ci.yml", "main", {
        debug: "true",
      });

      expect(result.status).toBe("success");
      expect(result.workflowRunId).toBe(55555);
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
      (global.fetch as jest.Mock).mockImplementation(async (url: string) => {
        // Get workflow status
        if (url.includes("/runs/66666") && !url.includes("/jobs")) {
          return {
            ok: true,
            json: async () => ({
              id: 66666,
              name: "CI",
              head_branch: "main",
              status: "completed",
              conclusion: "success",
              created_at: "2025-07-31T10:00:00Z",
              updated_at: "2025-07-31T10:00:00Z",
            }),
          };
        }

        // Get jobs
        if (url.includes("/jobs") && !url.includes("/logs")) {
          return {
            ok: true,
            json: async () => ({
              jobs: [{ id: 1, name: "test" }],
            }),
          };
        }

        // Get logs - return 410 Gone
        if (url.includes("/logs")) {
          return {
            ok: false,
            status: 410,
            statusText: "Gone",
            text: async () => "", // Even though not used, provide it
          };
        }

        return { ok: false, status: 404 };
      });

      const result = await orchestrator.monitorWorkflowRun(66666, "ci.yml");

      expect(result.buildOutput.logs).toContain("[Logs expired]");
    });
  });
});
