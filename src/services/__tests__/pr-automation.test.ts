/**
 * Testes para PR Automation Engine
 */

import { PRAutomationEngine, PRAnalysisStatus } from "../pr-automation";
import { IntentParser } from "../intent-parser";
import { CIOrchestratorService } from "../ci-orchestrator";

// Mock dos módulos
jest.mock("../intent-parser");
jest.mock("../ci-orchestrator");

describe("PRAutomationEngine", () => {
  let prEngine: PRAutomationEngine;
  let mockIntentParser: jest.Mocked<IntentParser>;
  let mockCIOrchestrator: jest.Mocked<CIOrchestratorService>;

  const mockConfig = {
    githubToken: "test-token",
    owner: "test-owner",
    repo: "test-repo",
    workflowId: "test-workflow.yml",
    autoTriggerCI: true,
    minConfidenceThreshold: 0.6,
  };

  const mockPRData = {
    number: 42,
    title: "Add new feature",
    body: "This PR adds a new feature",
    user: {
      login: "testuser",
    },
    head: {
      ref: "feature/new-feature",
    },
    base: {
      ref: "main",
    },
  };

  const mockFiles = [
    {
      filename: "src/services/new-feature.ts",
      patch: "+export function newFeature() {\n+  return 'hello';\n+}",
      additions: 3,
      deletions: 0,
    },
    {
      filename: "src/services/__tests__/new-feature.test.ts",
      patch: "+describe('newFeature', () => {\n+  it('works', () => {});\n+});",
      additions: 3,
      deletions: 0,
    },
  ];

  const mockCommits = [
    {
      commit: {
        message: "feat: add new feature for PR handling",
        author: {
          name: "Test User",
          email: "test@example.com",
        },
      },
      sha: "abc123",
    },
  ];

  beforeEach(() => {
    // Limpa todos os mocks
    jest.clearAllMocks();

    // Configura mocks
    mockIntentParser = IntentParser as jest.Mocked<typeof IntentParser>;
    mockCIOrchestrator = CIOrchestratorService as jest.Mocked<
      typeof CIOrchestratorService
    >;

    // Cria instância
    prEngine = new PRAutomationEngine(mockConfig);
  });

  describe("analyzePR", () => {
    it("should analyze a PR successfully", async () => {
      // Configura fetch mock
      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/42") && !url.includes("/files")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockPRData),
          } as any);
        }
        if (url.includes("/pulls/42/files")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockFiles),
          } as any);
        }
        if (url.includes("/pulls/42/commits")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockCommits),
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      const analysis = await prEngine.analyzePR(42);

      expect(analysis).toBeDefined();
      expect(analysis.prNumber).toBe(42);
      expect(analysis.title).toBe("Add new feature");
      expect(analysis.author).toBe("testuser");
      expect(analysis.filesChanged).toBe(2);
      expect(analysis.additions).toBe(6);
      expect(analysis.deletions).toBe(0);
      expect(analysis.status).toBe(PRAnalysisStatus.COMPLETED);
      expect(analysis.completedAt).toBeDefined();
      expect(analysis.duration).toBeGreaterThan(0);
    });

    it("should detect code patterns", async () => {
      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/42")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                ...mockPRData,
                number: 42,
              }),
          } as any);
        }
        if (url.includes("/files")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve([
                {
                  filename: "src/services/complex-feature.ts",
                  patch: "+".repeat(150), // Muitas linhas adicionadas
                  additions: 150,
                  deletions: 0,
                },
              ]),
          } as any);
        }
        if (url.includes("/commits")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockCommits),
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      const analysis = await prEngine.analyzePR(42);

      expect(analysis.codePatterns.length).toBeGreaterThan(0);
      expect(analysis.codePatterns[0].type).toBeDefined();
      expect(analysis.codePatterns[0].severity).toBeDefined();
    });

    it("should generate suggestions", async () => {
      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/42")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                ...mockPRData,
                number: 42,
              }),
          } as any);
        }
        if (url.includes("/files")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve([
                {
                  filename: "src/services/feature.ts",
                  patch: "+".repeat(600), // Grande demais
                  additions: 600,
                  deletions: 0,
                },
              ]),
          } as any);
        }
        if (url.includes("/commits")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockCommits),
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      const analysis = await prEngine.analyzePR(42);

      expect(analysis.suggestions.length).toBeGreaterThan(0);
      expect(analysis.suggestions[0]).toHaveProperty("id");
      expect(analysis.suggestions[0]).toHaveProperty("title");
      expect(analysis.suggestions[0]).toHaveProperty("recommendation");
    });

    it("should handle fetch errors gracefully", async () => {
      global.fetch = jest.fn(() =>
        Promise.reject(new Error("Network error"))
      );

      const analysis = await prEngine.analyzePR(42);

      expect(analysis.status).toBe(PRAnalysisStatus.FAILED);
      expect(analysis.error).toBeDefined();
    });

    it("should handle missing PR", async () => {
      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/999")) {
          return Promise.resolve({
            ok: false,
            statusText: "Not Found",
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      const analysis = await prEngine.analyzePR(999);

      expect(analysis.status).toBe(PRAnalysisStatus.FAILED);
      expect(analysis.error).toContain("Failed to fetch PR data");
    });
  });

  describe("generateSuggestions", () => {
    it("should suggest adding tests for missing test files", async () => {
      const files = [
        {
          filename: "src/feature.ts",
          additions: 50,
          deletions: 0,
        },
      ];

      const suggestions = await prEngine.generateSuggestions(files, []);

      const testSuggestion = suggestions.find((s) => s.type === "missing-tests");
      expect(testSuggestion).toBeDefined();
      expect(testSuggestion?.severity).toBe("warning");
    });

    it("should suggest splitting large PRs", async () => {
      const files = [
        {
          filename: "src/feature.ts",
          additions: 600,
          deletions: 0,
        },
      ];

      const suggestions = await prEngine.generateSuggestions(files, []);

      const sizeSuggestion = suggestions.find((s) => s.title.includes("grande"));
      expect(sizeSuggestion).toBeDefined();
      expect(sizeSuggestion?.severity).toBe("warning");
    });

    it("should not suggest tests if test files are included", async () => {
      const files = [
        {
          filename: "src/feature.ts",
          additions: 50,
          deletions: 0,
        },
        {
          filename: "src/feature.test.ts",
          additions: 50,
          deletions: 0,
        },
      ];

      const suggestions = await prEngine.generateSuggestions(files, []);

      const testSuggestion = suggestions.find((s) => s.type === "missing-tests");
      expect(testSuggestion).toBeUndefined();
    });
  });

  describe("triggerCI", () => {
    it("should trigger CI pipeline", async () => {
      const mockRunId = 12345;

      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/42") && !url.includes("/files")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                ...mockPRData,
                number: 42,
              }),
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      // Mock do CI Orchestrator
      const mockOrchestrator = {
        triggerWorkflow: jest.fn().mockResolvedValue(mockRunId),
        monitorWorkflowRun: jest.fn().mockResolvedValue({
          status: "success",
          workflowRunId: mockRunId,
          buildOutput: { logs: [], duration: 5000 },
          duration: 5000,
          timestamp: new Date(),
        }),
      };

      // Substitui o orchestrator
      (prEngine as any).ciOrchestrator = mockOrchestrator;

      const result = await prEngine.triggerCI(42);

      expect(result.success).toBe(true);
      expect(result.workflowRunId).toBe(mockRunId);
      expect(mockOrchestrator.triggerWorkflow).toHaveBeenCalled();
    });

    it("should handle CI trigger failure", async () => {
      global.fetch = jest.fn((url: string) => {
        if (url.includes("/pulls/42")) {
          return Promise.resolve({
            ok: false,
            statusText: "Not Found",
          } as any);
        }
        return Promise.reject(new Error("Unexpected URL"));
      });

      await expect(prEngine.triggerCI(42)).rejects.toThrow();
    });
  });

  describe("monitorBuild", () => {
    it("should monitor build status", async () => {
      const mockOrchestrator = {
        monitorWorkflowRun: jest.fn().mockResolvedValue({
          status: "success",
          workflowStatus: "completed",
          conclusion: "success",
          buildOutput: {
            logs: ["test log"],
            testResults: {
              passed: 10,
              failed: 0,
              skipped: 2,
              duration: 5000,
            },
            coverage: {
              lines: 85,
              statements: 85,
              functions: 90,
              branches: 80,
            },
            duration: 5000,
          },
          duration: 5000,
          timestamp: new Date(),
        }),
      };

      (prEngine as any).ciOrchestrator = mockOrchestrator;

      const buildStatus = await prEngine.monitorBuild(12345);

      expect(buildStatus.passed).toBe(true);
      expect(buildStatus.testsPassed).toBe(10);
      expect(buildStatus.testsFailed).toBe(0);
      expect(buildStatus.coverage).toBe(85);
    });

    it("should handle monitor build timeout", async () => {
      const mockOrchestrator = {
        monitorWorkflowRun: jest.fn().mockRejectedValue(new Error("Timeout")),
      };

      (prEngine as any).ciOrchestrator = mockOrchestrator;

      await expect(prEngine.monitorBuild(12345)).rejects.toThrow();
    });
  });
});
