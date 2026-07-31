/**
 * Testes unitários para Auto-Merge Controller
 */

import {
  AutoMergeController,
  createAutoMergeController,
  MergeStatus,
  BlockReason,
  type AutoMergeConfig,
  type MergeResult,
  type PrerequisiteCheckResult,
  type AuditEvent,
} from "../auto-merge";

describe("AutoMergeController", () => {
  let controller: AutoMergeController;
  const mockConfig: AutoMergeConfig = {
    githubToken: "test-token",
    owner: "test-org",
    repo: "test-repo",
    requireCIPassed: true,
    requiredApprovals: 1,
    allowMergingWithConflicts: false,
    mergeMethod: "merge",
    deleteBranchAfterMerge: true,
    notifyOnBlock: true,
  };

  beforeEach(() => {
    controller = createAutoMergeController(mockConfig);
  });

  describe("Initialization", () => {
    test("should create AutoMergeController with default config", () => {
      expect(controller).toBeDefined();
      expect(controller instanceof AutoMergeController).toBe(true);
    });

    test("should initialize with custom config values", () => {
      const customConfig: AutoMergeConfig = {
        ...mockConfig,
        requiredApprovals: 2,
        mergeMethod: "squash",
        deleteBranchAfterMerge: false,
      };

      const customController = createAutoMergeController(customConfig);
      expect(customController).toBeDefined();
    });

    test("should have empty audit log on initialization", () => {
      const auditLog = controller.getAuditLog();
      expect(Array.isArray(auditLog)).toBe(true);
      expect(auditLog.length).toBe(0);
    });
  });

  describe("Audit Trail", () => {
    test("should maintain audit log", () => {
      const initialLog = controller.getAuditLog();
      expect(initialLog.length).toBe(0);

      controller.clearAuditLog();
      const clearedLog = controller.getAuditLog();
      expect(clearedLog.length).toBe(0);
    });

    test("should clear audit log", () => {
      controller.clearAuditLog();
      const auditLog = controller.getAuditLog();
      expect(auditLog.length).toBe(0);
    });
  });

  describe("Type definitions", () => {
    test("should have correct MergeStatus enum values", () => {
      expect(MergeStatus.PENDING).toBe("pending");
      expect(MergeStatus.CHECKING_PREREQUISITES).toBe("checking_prerequisites");
      expect(MergeStatus.READY_TO_MERGE).toBe("ready_to_merge");
      expect(MergeStatus.MERGING).toBe("merging");
      expect(MergeStatus.MERGED).toBe("merged");
      expect(MergeStatus.FAILED).toBe("failed");
      expect(MergeStatus.BLOCKED).toBe("blocked");
      expect(MergeStatus.REQUIRES_HUMAN_REVIEW).toBe("requires_human_review");
    });

    test("should have correct BlockReason enum values", () => {
      expect(BlockReason.CI_FAILED).toBe("ci_failed");
      expect(BlockReason.MISSING_APPROVALS).toBe("missing_approvals");
      expect(BlockReason.MERGE_CONFLICTS).toBe("merge_conflicts");
      expect(BlockReason.BRANCH_OUTDATED).toBe("branch_outdated");
      expect(BlockReason.REQUIRED_STATUS_CHECK_FAILED).toBe(
        "required_status_check_failed"
      );
      expect(BlockReason.DRAFT_PR).toBe("draft_pr");
      expect(BlockReason.NETWORK_ERROR).toBe("network_error");
      expect(BlockReason.PERMISSION_DENIED).toBe("permission_denied");
    });
  });

  describe("AuditEvent interface", () => {
    test("should create valid AuditEvent", () => {
      const auditEvent: AuditEvent = {
        timestamp: new Date(),
        action: "TEST_ACTION",
        status: "success",
        prNumber: 123,
        owner: "test-org",
        repo: "test-repo",
        details: { key: "value" },
      };

      expect(auditEvent.timestamp).toBeInstanceOf(Date);
      expect(auditEvent.action).toBe("TEST_ACTION");
      expect(auditEvent.status).toBe("success");
      expect(auditEvent.prNumber).toBe(123);
      expect(auditEvent.owner).toBe("test-org");
      expect(auditEvent.repo).toBe("test-repo");
      expect(auditEvent.details).toEqual({ key: "value" });
    });
  });

  describe("PrerequisiteCheckResult interface", () => {
    test("should create valid PrerequisiteCheckResult", () => {
      const prerequisitesCheck: PrerequisiteCheckResult = {
        passed: true,
        checks: {
          ciPassed: true,
          approvalsOk: true,
          noConflicts: true,
          notDraft: true,
          branchProtectionOk: true,
        },
        blockedBy: [],
        details: "All checks passed",
      };

      expect(prerequisitesCheck.passed).toBe(true);
      expect(prerequisitesCheck.checks.ciPassed).toBe(true);
      expect(prerequisitesCheck.checks.approvalsOk).toBe(true);
      expect(prerequisitesCheck.blockedBy).toEqual([]);
    });

    test("should create blocked PrerequisiteCheckResult", () => {
      const prerequisitesCheck: PrerequisiteCheckResult = {
        passed: false,
        checks: {
          ciPassed: false,
          approvalsOk: true,
          noConflicts: true,
          notDraft: true,
          branchProtectionOk: true,
        },
        blockedBy: [BlockReason.CI_FAILED],
        details: "CI pipeline failed",
      };

      expect(prerequisitesCheck.passed).toBe(false);
      expect(prerequisitesCheck.checks.ciPassed).toBe(false);
      expect(prerequisitesCheck.blockedBy).toEqual([BlockReason.CI_FAILED]);
    });
  });

  describe("MergeResult interface", () => {
    test("should create valid successful MergeResult", () => {
      const mergeResult: MergeResult = {
        success: true,
        prNumber: 42,
        owner: "test-org",
        repo: "test-repo",
        status: MergeStatus.MERGED,
        sha: "abc123",
        mergeCommitSha: "def456",
        branchDeleted: true,
        auditEvents: [],
        timestamp: new Date(),
        duration: 1500,
      };

      expect(mergeResult.success).toBe(true);
      expect(mergeResult.status).toBe(MergeStatus.MERGED);
      expect(mergeResult.mergeCommitSha).toBe("def456");
      expect(mergeResult.branchDeleted).toBe(true);
    });

    test("should create valid failed MergeResult", () => {
      const mergeResult: MergeResult = {
        success: false,
        prNumber: 42,
        owner: "test-org",
        repo: "test-repo",
        status: MergeStatus.BLOCKED,
        blockedBy: [BlockReason.CI_FAILED, BlockReason.MISSING_APPROVALS],
        auditEvents: [],
        timestamp: new Date(),
        error: "PR requirements not met",
      };

      expect(mergeResult.success).toBe(false);
      expect(mergeResult.status).toBe(MergeStatus.BLOCKED);
      expect(mergeResult.blockedBy).toContain(BlockReason.CI_FAILED);
      expect(mergeResult.error).toBeDefined();
    });
  });

  describe("AutoMergeConfig interface", () => {
    test("should create valid AutoMergeConfig with all options", () => {
      const config: AutoMergeConfig = {
        githubToken: "token",
        owner: "org",
        repo: "repo",
        requireCIPassed: true,
        requiredApprovals: 2,
        allowMergingWithConflicts: false,
        mergeMethod: "squash",
        commitMessage: "Custom merge message",
        commitDescription: "Custom description",
        deleteBranchAfterMerge: true,
        auditTableUrl: "https://api.supabase.com/rest/v1/audit",
        auditApiKey: "api-key",
        notifyOnBlock: true,
        slackWebhook: "https://hooks.slack.com/...",
        maxWaitForCI: 600000,
        checkInterval: 5000,
      };

      expect(config.githubToken).toBe("token");
      expect(config.requiredApprovals).toBe(2);
      expect(config.mergeMethod).toBe("squash");
      expect(config.commitMessage).toBe("Custom merge message");
      expect(config.slackWebhook).toBeDefined();
    });

    test("should create minimal AutoMergeConfig", () => {
      const minimalConfig: AutoMergeConfig = {
        githubToken: "token",
        owner: "org",
        repo: "repo",
      };

      expect(minimalConfig.githubToken).toBe("token");
      expect(minimalConfig.owner).toBe("org");
      expect(minimalConfig.repo).toBe("repo");
    });
  });

  describe("Factory function", () => {
    test("createAutoMergeController should return valid instance", () => {
      const instance = createAutoMergeController(mockConfig);
      expect(instance).toBeInstanceOf(AutoMergeController);
    });

    test("should allow chaining with factory function", () => {
      const instance = createAutoMergeController({
        githubToken: "token",
        owner: "org",
        repo: "repo",
        requiredApprovals: 3,
      });

      expect(instance.getAuditLog()).toEqual([]);
    });
  });
});
