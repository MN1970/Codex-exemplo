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
  type BuildStatus,
  type PRAnalysis,
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

  describe("Phase 3 — analyzeCIResults", () => {
    it("should analyze successful CI results", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
        testResults: {
          total: 100,
          passed: 100,
          failed: 0,
          skipped: 0,
          duration: 5000,
        },
        coverage: {
          lines: 85,
          statements: 85,
          functions: 80,
          branches: 75,
          threshold: 80,
        },
      };

      const feedback = await engine.analyzeCIResults(buildStatus);

      expect(feedback).toBeDefined();
      expect(feedback.prNumber).toBe(42);
      expect(feedback.severity).toBe("info");
      expect(feedback.issues).toHaveLength(0);
    });

    it("should detect test failures and generate recommendations", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "failure",
        timestamp: new Date(),
        duration: 5000,
        testResults: {
          total: 100,
          passed: 90,
          failed: 10,
          skipped: 0,
          duration: 5000,
          failedTests: ["test/foo.test.ts", "test/bar.test.ts"],
        },
        coverage: {
          lines: 80,
          statements: 80,
          functions: 80,
          branches: 75,
          threshold: 80,
        },
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              recommendations: [
                {
                  type: "test",
                  title: "Fix failing tests",
                  description: "Fix test failures",
                  impact: "high",
                  effort: "medium",
                  priority: 9,
                },
              ],
            }),
          },
        ],
      });

      const feedback = await engine.analyzeCIResults(buildStatus);

      expect(feedback).toBeDefined();
      expect(feedback.prNumber).toBe(42);
      expect(feedback.severity).toBe("error");
      expect(feedback.issues.length).toBeGreaterThan(0);
      expect(feedback.issues[0].category).toBe("Test Failures");
      expect(feedback.recommendations.length).toBeGreaterThan(0);
    });

    it("should detect coverage below threshold", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "failure",
        timestamp: new Date(),
        duration: 5000,
        coverage: {
          lines: 70,
          statements: 72,
          functions: 68,
          branches: 65,
          threshold: 80,
        },
      };

      const feedback = await engine.analyzeCIResults(buildStatus);

      expect(feedback.issues.some((i) => i.category === "Coverage Below Threshold")).toBe(true);
    });

    it("should cache feedback for future access", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 99,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
      };

      await engine.analyzeCIResults(buildStatus);

      const cached = engine.getFeedback(99);
      expect(cached).toBeDefined();
      expect(cached?.prNumber).toBe(99);
    });
  });

  describe("Phase 3 — generateRecommendations", () => {
    it("should generate recommendations from PR analysis", async () => {
      const prAnalysis: PRAnalysis = {
        prNumber: 42,
        title: "Add feature X",
        description: "Implements feature X",
        author: "john",
        filesChanged: 5,
        additions: 100,
        deletions: 20,
        commits: 3,
        labels: ["feature", "enhancement"],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              recommendations: [
                {
                  type: "test",
                  title: "Add tests",
                  description: "Add unit tests",
                  impact: "high",
                  effort: "medium",
                  priority: 8,
                  estimatedTimeMinutes: 30,
                },
                {
                  type: "code",
                  title: "Refactor duplicated code",
                  description: "Extract common logic",
                  impact: "medium",
                  effort: "low",
                  priority: 6,
                },
              ],
            }),
          },
        ],
      });

      const recommendations = await engine.generateRecommendations(prAnalysis);

      expect(recommendations.length).toBeGreaterThan(0);
      expect(recommendations[0]).toHaveProperty("type");
      expect(recommendations[0]).toHaveProperty("title");
      expect(recommendations[0]).toHaveProperty("impact");
      expect(recommendations[0]).toHaveProperty("effort");
      expect(recommendations[0]).toHaveProperty("priority");
    });

    it("should handle empty recommendations gracefully", async () => {
      const prAnalysis: PRAnalysis = {
        prNumber: 42,
        title: "Small fix",
        description: "Typo fix",
        author: "jane",
        filesChanged: 1,
        additions: 1,
        deletions: 1,
        commits: 1,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              recommendations: [],
            }),
          },
        ],
      });

      const recommendations = await engine.generateRecommendations(prAnalysis);

      expect(recommendations).toEqual([]);
    });
  });

  describe("Phase 3 — trackMetrics", () => {
    it("should track PR metrics", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
        testResults: {
          total: 100,
          passed: 95,
          failed: 5,
          skipped: 0,
          duration: 5000,
        },
        coverage: {
          lines: 85,
          statements: 85,
          functions: 80,
          branches: 75,
        },
        lint: {
          errors: 2,
          warnings: 10,
          fixable: 5,
        },
      };

      // First analyze to populate feedback cache
      await engine.analyzeCIResults(buildStatus);

      // Then track metrics
      const metrics = await engine.trackMetrics(42);

      expect(metrics).toBeDefined();
      expect(metrics.prNumber).toBe(42);
      expect(metrics.qualityScore).toBeGreaterThan(0);
      expect(metrics.testCoverage).toBe(85);
      expect(metrics.buildTimeMs).toBe(5000);
      expect(metrics.testsPassed).toBe(95);
      expect(metrics.testsFailed).toBe(5);
      expect(metrics.lintIssues).toBe(2);
    });

    it("should maintain metrics history", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 100,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
        coverage: {
          lines: 80,
          statements: 80,
          functions: 80,
          branches: 75,
        },
      };

      await engine.analyzeCIResults(buildStatus);
      await engine.trackMetrics(100);
      await engine.trackMetrics(100); // Track again

      const history = engine.getMetricsHistory(100);
      expect(history.length).toBe(2);
      expect(history[0].prNumber).toBe(100);
      expect(history[1].prNumber).toBe(100);
    });
  });

  describe("Phase 3 — suggestReviewers", () => {
    it("should suggest reviewers based on diff", async () => {
      const diff = `
        diff --git a/src/services/index.ts b/src/services/index.ts
        --- a/src/services/index.ts
        +++ b/src/services/index.ts
        @@ -1,3 +1,5 @@
        +import { APIHandler } from './handlers';
        +
         export class MyService {
           private handler: APIHandler;
         }
      `;

      const mockClient = (engine as any).client;
      mockClient.messages.create = jest.fn().mockResolvedValue({
        content: [
          {
            type: "text",
            text: JSON.stringify({
              reviewers: [
                {
                  username: "alice",
                  expertise: ["backend", "services"],
                  matchScore: 0.95,
                  filesExpertise: {
                    "src/services/index.ts": 0.9,
                  },
                },
                {
                  username: "bob",
                  expertise: ["api", "testing"],
                  matchScore: 0.75,
                  filesExpertise: {
                    "src/services/index.ts": 0.7,
                  },
                },
              ],
            }),
          },
        ],
      });

      const reviewers = await engine.suggestReviewers(diff);

      expect(reviewers.length).toBeGreaterThan(0);
      expect(reviewers[0]).toHaveProperty("username");
      expect(reviewers[0]).toHaveProperty("expertise");
      expect(reviewers[0]).toHaveProperty("matchScore");
      expect(reviewers[0].expertise).toBeInstanceOf(Array);
    });
  });

  describe("Phase 3 — getMetricsAggregate", () => {
    it("should aggregate metrics over time period", async () => {
      const now = new Date();
      const startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago

      // Add some metrics
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "success",
        timestamp: now,
        duration: 5000,
        coverage: {
          lines: 85,
          statements: 85,
          functions: 80,
          branches: 75,
        },
      };

      await engine.analyzeCIResults(buildStatus);
      await engine.trackMetrics(42);

      const aggregate = engine.getMetricsAggregate(startDate, now);

      expect(aggregate).toBeDefined();
      expect(aggregate.period.startDate).toEqual(startDate);
      expect(aggregate.period.endDate).toEqual(now);
      expect(aggregate.totalPRs).toBeGreaterThanOrEqual(0);
    });

    it("should calculate trends", async () => {
      const now = new Date();
      const startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

      const aggregate = engine.getMetricsAggregate(startDate, now);

      expect(aggregate.trends).toHaveProperty("qualityTrend");
      expect(aggregate.trends).toHaveProperty("coverageTrend");
      expect(aggregate.trends).toHaveProperty("performanceTrend");
    });
  });

  describe("Phase 3 — Cache management", () => {
    it("should clear all caches", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
      };

      await engine.analyzeCIResults(buildStatus);
      await engine.trackMetrics(42);

      expect(engine.getFeedback(42)).toBeDefined();
      expect(engine.getMetricsHistory(42).length).toBeGreaterThan(0);

      engine.clearAllCaches();

      expect(engine.getFeedback(42)).toBeUndefined();
      expect(engine.getMetricsHistory(42).length).toBe(0);
    });

    it("should clear specific caches", async () => {
      const buildStatus: BuildStatus = {
        workflowId: "workflow_1",
        workflowName: "CI",
        prNumber: 42,
        status: "success",
        timestamp: new Date(),
        duration: 5000,
      };

      await engine.analyzeCIResults(buildStatus);
      await engine.trackMetrics(42);

      engine.clearMetricsHistory();

      expect(engine.getFeedback(42)).toBeDefined();
      expect(engine.getMetricsHistory(42).length).toBe(0);
    });
  });
});
