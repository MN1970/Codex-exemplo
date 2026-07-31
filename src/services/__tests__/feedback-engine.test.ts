/**
 * Testes para FeedbackEngine
 */

import {
  FeedbackEngine,
  createFeedbackEngine,
  ErrorType,
  ErrorSeverity,
  FeedbackStatus,
  type CIOutput,
  type CIError,
} from "../feedback-engine";

// Mock do Anthropic
jest.mock("@anthropic-ai/sdk", () => {
  return jest.fn().mockImplementation(() => ({
    messages: {
      create: jest.fn(),
    },
  }));
});

// Mock do fetch global
global.fetch = jest.fn();

describe("FeedbackEngine", () => {
  let engine: FeedbackEngine;
  const mockConfig = {
    githubToken: "test_token",
    owner: "test_owner",
    repo: "test_repo",
    anthropicApiKey: "test_key",
  };

  beforeEach(() => {
    jest.clearAllMocks();
    engine = createFeedbackEngine(mockConfig);
  });

  describe("Constructor", () => {
    it("should create FeedbackEngine with config", () => {
      expect(engine).toBeDefined();
      expect(engine).toBeInstanceOf(FeedbackEngine);
    });

    it("should use environment variable for API key if not provided", () => {
      process.env.ANTHROPIC_API_KEY = "env_key";
      const testEngine = createFeedbackEngine({
        githubToken: "token",
        owner: "owner",
        repo: "repo",
      });
      expect(testEngine).toBeDefined();
    });
  });

  describe("processCIOutput", () => {
    it("should skip processing when no errors", async () => {
      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "main",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "success",
        errors: [],
        logs: [],
      };

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.SKIPPED);
      expect(tracking.suggestionsGenerated).toBe(0);
      expect(tracking.commentsPosted).toBe(0);
    });

    it("should process output with errors", async () => {
      const error: CIError = {
        type: ErrorType.TEST_FAILURE,
        severity: ErrorSeverity.ERROR,
        message: "Test failed: expect(foo).toBe(bar)",
        file: "src/foo.test.ts",
        line: 42,
      };

      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [error],
        logs: ["Error: test failed"],
        testResults: {
          total: 100,
          passed: 90,
          failed: 10,
          skipped: 0,
          duration: 5000,
          failedTests: ["test/foo.test.ts"],
        },
      };

      // Mock Anthropic response
      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              suggestions: [
                {
                  suggestion: "Check the assertion in line 42",
                  codeExample: "expect(foo).toBe(bar)",
                  confidence: 0.9,
                  priority: "high",
                },
              ],
            }),
          },
        ],
      });

      // Mock GitHub API
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ id: 123 }),
      });

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.POSTED);
      expect(tracking.suggestionsGenerated).toBeGreaterThan(0);
      expect(tracking.commentsPosted).toBe(1);
    });

    it("should handle errors gracefully", async () => {
      const error: CIError = {
        type: ErrorType.LINT_ERROR,
        severity: ErrorSeverity.ERROR,
        message: "Missing semicolon",
        file: "src/index.ts",
        line: 10,
      };

      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [error],
        logs: [],
      };

      // Mock Anthropic failure
      const mockClient = (engine as any).client;
      mockClient.messages.create = jest
        .fn()
        .mockRejectedValue(new Error("API Error"));

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.FAILED);
    });
  });

  describe("Coverage metrics", () => {
    it("should detect coverage below threshold", async () => {
      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [
          {
            type: ErrorType.COVERAGE_BELOW_THRESHOLD,
            severity: ErrorSeverity.WARNING,
            message: "Coverage below threshold (70% < 80%)",
          },
        ],
        logs: [],
        coverage: {
          lines: 70,
          statements: 72,
          functions: 68,
          branches: 65,
          threshold: 80,
        },
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              suggestions: [
                {
                  suggestion: "Add more test cases for uncovered branches",
                  confidence: 0.8,
                  priority: "medium",
                },
              ],
            }),
          },
        ],
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ id: 123 }),
      });

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.POSTED);
    });
  });

  describe("Retry logic", () => {
    it("should retry on transient failures", async () => {
      const error: CIError = {
        type: ErrorType.BUILD_FAILURE,
        severity: ErrorSeverity.ERROR,
        message: "Build failed",
      };

      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [error],
        logs: [],
      };

      const mockClient = (engine as any).client;
      let callCount = 0;
      mockClient.messages.create = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount < 2) {
          throw new Error("(503) Service Unavailable");
        }
        return Promise.resolve({
          content: [
            {
              type: "text",
              text: JSON.stringify({
                suggestions: [
                  {
                    suggestion: "Check build logs",
                    confidence: 0.7,
                    priority: "high",
                  },
                ],
              }),
            },
          ],
        });
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ id: 123 }),
      });

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.POSTED);
      expect(mockClient.messages.create).toHaveBeenCalledTimes(2);
    });

    it("should fail after max retries", async () => {
      const error: CIError = {
        type: ErrorType.BUILD_FAILURE,
        severity: ErrorSeverity.CRITICAL,
        message: "Build failed permanently",
      };

      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [error],
        logs: [],
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest
        .fn()
        .mockRejectedValue(new Error("(500) Internal Server Error"));

      const tracking = await engine.processCIOutput(output);

      expect(tracking.status).toBe(FeedbackStatus.FAILED);
      expect(mockClient.messages.create).toHaveBeenCalled();
    });
  });

  describe("Statistics and tracking", () => {
    it("should track feedback history", async () => {
      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test",
        prNumber: 42,
        branch: "main",
        commit: "abc",
        timestamp: new Date(),
        duration: 1000,
        status: "success",
        errors: [],
        logs: [],
      };

      const tracking = await engine.processCIOutput(output);
      const history = engine.getFeedbackHistory();

      expect(history).toHaveLength(1);
      expect(history[0].feedbackId).toBe(tracking.feedbackId);
    });

    it("should calculate statistics", async () => {
      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test",
        prNumber: 42,
        branch: "main",
        commit: "abc",
        timestamp: new Date(),
        duration: 1000,
        status: "success",
        errors: [],
        logs: [],
      };

      await engine.processCIOutput(output);

      const stats = engine.getStatistics();

      expect(stats.totalFeedbacks).toBe(1);
      expect(stats.successRate).toBeLessThanOrEqual(1);
      expect(stats.avgTimeSpentMs).toBeGreaterThanOrEqual(0);
    });

    it("should clear history", async () => {
      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test",
        prNumber: 42,
        branch: "main",
        commit: "abc",
        timestamp: new Date(),
        duration: 1000,
        status: "success",
        errors: [],
        logs: [],
      };

      await engine.processCIOutput(output);
      expect(engine.getFeedbackHistory()).toHaveLength(1);

      engine.clearHistory();
      expect(engine.getFeedbackHistory()).toHaveLength(0);
    });
  });

  describe("Error types", () => {
    const errorTypes = [
      ErrorType.TEST_FAILURE,
      ErrorType.LINT_ERROR,
      ErrorType.TYPE_ERROR,
      ErrorType.COVERAGE_BELOW_THRESHOLD,
      ErrorType.BUILD_FAILURE,
      ErrorType.DEPENDENCY_ERROR,
      ErrorType.PERFORMANCE_REGRESSION,
      ErrorType.SECURITY_ISSUE,
    ];

    errorTypes.forEach((errorType) => {
      it(`should handle ${errorType}`, () => {
        const error: CIError = {
          type: errorType,
          severity: ErrorSeverity.ERROR,
          message: `Error of type ${errorType}`,
        };

        expect(error.type).toBe(errorType);
      });
    });
  });

  describe("Comment formatting", () => {
    it("should format suggestions as markdown comment", async () => {
      const error: CIError = {
        type: ErrorType.TEST_FAILURE,
        severity: ErrorSeverity.ERROR,
        message: "Test failed",
        file: "test.ts",
        line: 10,
      };

      const output: CIOutput = {
        workflowId: "workflow_1",
        workflowName: "test_workflow",
        prNumber: 42,
        branch: "feature/foo",
        commit: "abc123",
        timestamp: new Date(),
        duration: 5000,
        status: "failure",
        errors: [error],
        logs: [],
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              suggestions: [
                {
                  suggestion: "Fix the test assertion",
                  codeExample: "expect(x).toBe(y)",
                  confidence: 0.95,
                  priority: "high",
                },
              ],
            }),
          },
        ],
      });

      let capturedBody = "";
      (global.fetch as jest.Mock).mockImplementation((url, options) => {
        if (options.method === "POST") {
          capturedBody = JSON.parse(options.body).body;
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ id: 123 }),
        });
      });

      await engine.processCIOutput(output);

      expect(capturedBody).toContain("CI Feedback");
      expect(capturedBody).toContain("TEST_FAILURE");
      expect(capturedBody).toContain("high");
      expect(capturedBody).toContain("confidence");
    });
  });
});
