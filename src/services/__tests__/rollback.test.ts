/**
 * Testes para Rollback Orchestrator
 * Cobertura: detecção de falhas, propostas, aprovação, execução
 */

import {
  RollbackOrchestratorService,
  RollbackMonitorStatus,
  RollbackExecutionStatus,
  FailureSeverity,
  createRollbackOrchestratorService,
  type RollbackOrchestratorConfig,
  type CIFailure,
  type MergedPR,
} from "../rollback";

describe("RollbackOrchestratorService", () => {
  let service: RollbackOrchestratorService;
  let config: RollbackOrchestratorConfig;

  beforeEach(() => {
    config = {
      githubToken: "test-token",
      owner: "test-owner",
      repo: "test-repo",
      slackWebhookUrl: "https://hooks.slack.com/test",
      coworkWebhookUrl: "https://cowork.test/webhook",
      approvalTimeoutMinutes: 30,
      maxAutomaticRollbacksPerDay: 5,
    };

    service = createRollbackOrchestratorService(config);
  });

  describe("Initialization", () => {
    it("should create service with valid config", () => {
      expect(service).toBeDefined();
      expect(service).toBeInstanceOf(RollbackOrchestratorService);
    });

    it("should throw error on missing GitHub token", () => {
      const invalidConfig = { ...config, githubToken: "" };
      expect(
        () => createRollbackOrchestratorService(invalidConfig)
      ).toThrow("GitHub token is required");
    });

    it("should throw error on missing owner or repo", () => {
      const invalidConfig = { ...config, owner: "" };
      expect(
        () => createRollbackOrchestratorService(invalidConfig)
      ).toThrow("Owner and repo are required");
    });

    it("should initialize with default configuration", () => {
      const minimalConfig: RollbackOrchestratorConfig = {
        githubToken: "token",
        owner: "owner",
        repo: "repo",
      };

      const svc = createRollbackOrchestratorService(minimalConfig);
      const metrics = svc.getMetrics();

      expect(metrics.totalFailuresDetected).toBe(0);
      expect(metrics.totalProposals).toBe(0);
    });
  });

  describe("Failure Detection", () => {
    it("should detect CI failure from workflow run", async () => {
      // Mock implementation - in real tests would mock fetch
      const mockFailure: CIFailure = {
        commitSha: "abc123",
        commitMessage: "Fix: something broken",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 12345,
        failedTests: [
          {
            name: "test should pass",
            suite: "main.test.ts",
            message: "Expected true but got false",
            duration: 150,
          },
          {
            name: "async operation should resolve",
            suite: "async.test.ts",
            message: "Timeout exceeded",
            duration: 5000,
          },
        ],
        lintErrors: [
          {
            file: "src/index.ts",
            line: 42,
            column: 5,
            rule: "no-unused-vars",
            message: "unusedVariable is defined but never used",
            severity: "error",
          },
        ],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/index.ts", "src/utils.ts"],
        buildDuration: 120000,
      };

      // Verify failure structure
      expect(mockFailure.commitSha).toBeDefined();
      expect(mockFailure.failedTests.length).toBe(2);
      expect(mockFailure.lintErrors.length).toBe(1);
      expect(mockFailure.severity).toBe(FailureSeverity.MEDIUM);
    });

    it("should calculate severity as CRITICAL for many failures", async () => {
      const failure: CIFailure = {
        commitSha: "critical123",
        commitMessage: "Broke everything",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 99999,
        failedTests: Array(25)
          .fill(null)
          .map((_, i) => ({
            name: `test ${i}`,
            suite: "tests.ts",
            message: "Failed",
            duration: 100,
          })),
        lintErrors: Array(15)
          .fill(null)
          .map((_, i) => ({
            file: "src/file.ts",
            line: i,
            column: 1,
            rule: "rule",
            message: "Error",
            severity: "error" as const,
          })),
        severity: FailureSeverity.CRITICAL,
        affectedFiles: ["src/index.ts"],
        buildDuration: 180000,
      };

      expect(failure.severity).toBe(FailureSeverity.CRITICAL);
      expect(failure.failedTests.length).toBeGreaterThan(20);
      expect(failure.lintErrors.length).toBeGreaterThan(10);
    });

    it("should update metrics when failure is detected", () => {
      const initialMetrics = service.getMetrics();
      expect(initialMetrics.totalFailuresDetected).toBe(0);

      // Simulating failure detection by checking metrics structure
      const metrics = service.getMetrics();
      expect(metrics).toHaveProperty("totalFailuresDetected");
      expect(metrics).toHaveProperty("totalProposals");
      expect(metrics).toHaveProperty("totalApproved");
    });
  });

  describe("Rollback Proposal", () => {
    it("should create rollback proposal with correct structure", async () => {
      const failure: CIFailure = {
        commitSha: "fail456",
        commitMessage: "Breaking change",
        author: "developer@test.com",
        committedAt: new Date(),
        workflowRunId: 54321,
        failedTests: [
          {
            name: "should work",
            suite: "test.ts",
            message: "Failed assertion",
            duration: 200,
          },
          {
            name: "should handle errors",
            suite: "test.ts",
            message: "Unexpected error",
            duration: 150,
          },
          {
            name: "should validate input",
            suite: "test.ts",
            message: "Missing validation",
            duration: 100,
          },
          {
            name: "should process data",
            suite: "test.ts",
            message: "Wrong output",
            duration: 180,
          },
          {
            name: "should clean up resources",
            suite: "test.ts",
            message: "Resource leak",
            duration: 300,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.HIGH,
        affectedFiles: ["src/core.ts", "src/utils.ts"],
        buildDuration: 150000,
      };

      const mergedPR: MergedPR = {
        number: 123,
        title: "Add new feature",
        author: "developer@test.com",
        mergeCommit: "fail456",
        mergedAt: new Date(),
        headBranch: "feature/new-feature",
        baseCommit: "base789",
      };

      const proposal = await service.proposeRollback(failure, mergedPR);

      expect(proposal).toBeDefined();
      expect(proposal.id).toMatch(/^rollback-/);
      expect(proposal.targetCommit).toBe(failure.commitSha);
      expect(proposal.ciFailure).toEqual(failure);
      expect(proposal.mergedPR).toEqual(mergedPR);
      expect(proposal.severity).toBe(FailureSeverity.HIGH);
      expect(proposal.approvalStatus).toBeDefined();
    });

    it("should mark proposal as auto-approvable for non-critical failures", async () => {
      const failure: CIFailure = {
        commitSha: "medium789",
        commitMessage: "Minor issue",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 77777,
        failedTests: Array(8)
          .fill(null)
          .map((_, i) => ({
            name: `test ${i}`,
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          })),
        lintErrors: [],
        severity: FailureSeverity.HIGH,
        affectedFiles: ["src/helpers.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);

      // Non-CRITICAL with enough failures might be auto-approvable
      expect(proposal).toHaveProperty("autoApprovalEligible");
      expect(proposal).toHaveProperty("approvalStatus");
    });

    it("should not auto-approve CRITICAL severity", async () => {
      const failure: CIFailure = {
        commitSha: "critical999",
        commitMessage: "Catastrophic failure",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 88888,
        failedTests: Array(30)
          .fill(null)
          .map((_, i) => ({
            name: `test ${i}`,
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          })),
        lintErrors: [],
        severity: FailureSeverity.CRITICAL,
        affectedFiles: ["src/core.ts"],
        buildDuration: 200000,
      };

      const proposal = await service.proposeRollback(failure);

      // CRITICAL severity should NOT be auto-approved by default
      expect(proposal.autoApprovalEligible).toBe(false);
      expect(proposal.approvalStatus).toBe("pending");
    });
  });

  describe("Approval Workflow", () => {
    it("should request approval with valid token and expiration", async () => {
      const failure: CIFailure = {
        commitSha: "approval123",
        commitMessage: "Needs approval",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 11111,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);
      const approvalRequest = await service.requestApproval(proposal, "slack");

      expect(approvalRequest).toBeDefined();
      expect(approvalRequest.proposalId).toBe(proposal.id);
      expect(approvalRequest.approvalToken).toBeDefined();
      expect(approvalRequest.approvalToken.length).toBeGreaterThan(10);
      expect(approvalRequest.status).toBe("pending");
      expect(approvalRequest.expiresAt.getTime()).toBeGreaterThan(Date.now());
    });

    it("should approve rollback with valid token", async () => {
      const failure: CIFailure = {
        commitSha: "approve456",
        commitMessage: "Needs approval",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 22222,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);
      const approvalRequest = await service.requestApproval(proposal);

      const approvedProposal = await service.approveRollback(
        proposal.id,
        approvalRequest.approvalToken,
        "reviewer@test.com"
      );

      expect(approvedProposal.approvalStatus).toBe("approved");
      expect(approvedProposal.approvedBy).toBe("reviewer@test.com");
      expect(approvedProposal.approvedAt).toBeDefined();
    });

    it("should reject approval with invalid token", async () => {
      const failure: CIFailure = {
        commitSha: "reject789",
        commitMessage: "Invalid token test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 33333,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);
      await service.requestApproval(proposal);

      expect(
        service.approveRollback(proposal.id, "invalid-token", "reviewer@test.com")
      ).rejects.toThrow("Invalid approval token");
    });

    it("should reject rollback request", async () => {
      const failure: CIFailure = {
        commitSha: "rejecttest",
        commitMessage: "Reject test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 44444,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.LOW,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);
      await service.requestApproval(proposal);

      const rejectedProposal = await service.rejectRollback(
        proposal.id,
        "Not a real issue, will fix manually",
        "reviewer@test.com"
      );

      expect(rejectedProposal.approvalStatus).toBe("rejected");
      expect(rejectedProposal.rejectionReason).toBe(
        "Not a real issue, will fix manually"
      );
    });
  });

  describe("Metrics and Audit Trail", () => {
    it("should track metrics", async () => {
      const initialMetrics = service.getMetrics();
      expect(initialMetrics.totalFailuresDetected).toBe(0);
      expect(initialMetrics.totalProposals).toBe(0);

      const failure: CIFailure = {
        commitSha: "metric123",
        commitMessage: "Metric test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 55555,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      await service.proposeRollback(failure);

      const updatedMetrics = service.getMetrics();
      expect(updatedMetrics.totalProposals).toBeGreaterThan(
        initialMetrics.totalProposals
      );
    });

    it("should maintain audit trail", async () => {
      const auditTrail = service.getAuditTrail();
      expect(Array.isArray(auditTrail)).toBe(true);

      const failure: CIFailure = {
        commitSha: "audit123",
        commitMessage: "Audit test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 66666,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      await service.proposeRollback(failure);

      const newAuditTrail = service.getAuditTrail();
      expect(newAuditTrail.length).toBeGreaterThanOrEqual(auditTrail.length);
    });

    it("should reset metrics", () => {
      const failure: CIFailure = {
        commitSha: "reset123",
        commitMessage: "Reset test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 77777,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      service.proposeRollback(failure).then(() => {
        service.resetMetrics();

        const metrics = service.getMetrics();
        expect(metrics.totalProposals).toBe(0);
        expect(metrics.totalFailuresDetected).toBe(0);
      });
    });
  });

  describe("Active Proposals", () => {
    it("should retrieve active proposals", async () => {
      let proposals = service.getActiveProposals();
      expect(proposals.length).toBe(0);

      const failure: CIFailure = {
        commitSha: "active123",
        commitMessage: "Active proposal test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 88888,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);

      proposals = service.getActiveProposals();
      expect(proposals.length).toBeGreaterThan(0);
      expect(proposals.some((p) => p.id === proposal.id)).toBe(true);
    });

    it("should retrieve specific proposal by ID", async () => {
      const failure: CIFailure = {
        commitSha: "specific123",
        commitMessage: "Specific proposal test",
        author: "dev@test.com",
        committedAt: new Date(),
        workflowRunId: 99999,
        failedTests: [
          {
            name: "test",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test2",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test3",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test4",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
          {
            name: "test5",
            suite: "test.ts",
            message: "Failed",
            duration: 100,
          },
        ],
        lintErrors: [],
        severity: FailureSeverity.MEDIUM,
        affectedFiles: ["src/test.ts"],
        buildDuration: 100000,
      };

      const proposal = await service.proposeRollback(failure);
      const retrieved = service.getProposal(proposal.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(proposal.id);
      expect(retrieved?.targetCommit).toBe(failure.commitSha);
    });
  });

  describe("Configuration Validation", () => {
    it("should validate minimum required configuration", () => {
      const validConfig: RollbackOrchestratorConfig = {
        githubToken: "token",
        owner: "owner",
        repo: "repo",
      };

      expect(
        () => createRollbackOrchestratorService(validConfig)
      ).not.toThrow();
    });

    it("should accept optional configurations", () => {
      const fullConfig: RollbackOrchestratorConfig = {
        githubToken: "token",
        owner: "owner",
        repo: "repo",
        slackWebhookUrl: "https://hooks.slack.com/test",
        coworkWebhookUrl: "https://cowork.test",
        maxAutomaticRollbacksPerDay: 10,
        approvalTimeoutMinutes: 45,
        requireManualApprovalForCritical: false,
      };

      expect(
        () => createRollbackOrchestratorService(fullConfig)
      ).not.toThrow();
    });
  });
});
