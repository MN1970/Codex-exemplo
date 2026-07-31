/**
 * Exemplo de uso do Rollback Orchestrator
 * Demonstra: detecção de CI failure, proposta, aprovação e execução de rollback
 */

import {
  createRollbackOrchestratorService,
  FailureSeverity,
  type CIFailure,
  type MergedPR,
} from "../rollback";

/**
 * Cenário 1: Detecção automática de falha e proposta de rollback
 */
async function scenario1_AutomaticDetectionAndProposal() {
  console.log("=== Scenario 1: Automatic Detection and Proposal ===\n");

  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-hub",
    slackWebhookUrl: process.env.SLACK_WEBHOOK || "https://hooks.slack.com/test",
    coworkWebhookUrl: process.env.COWORK_WEBHOOK,
    approvalTimeoutMinutes: 30,
    maxAutomaticRollbacksPerDay: 5,
    requireManualApprovalForCritical: true,
  });

  // Simula CI failure detectada em main
  const ciFailure: CIFailure = {
    commitSha: "f3a4c2b8d9e1f6a0b2c3d4e5f6a7b8c9",
    commitMessage: "Add async operation handler (closes #234)",
    author: "dev.silva@manta.com",
    committedAt: new Date(Date.now() - 15 * 60000), // 15 min atrás
    workflowRunId: 987654321,
    failedTests: [
      {
        name: "should handle timeout correctly",
        suite: "async-handler.test.ts",
        message:
          "Expected timeout after 5000ms but got 3000ms. Error: Promise not rejected",
        duration: 5100,
      },
      {
        name: "should retry on transient error",
        suite: "async-handler.test.ts",
        message: "RetryPolicy not applied. Expected 3 retries but got 0",
        duration: 2500,
      },
      {
        name: "integration: end-to-end operation",
        suite: "integration.test.ts",
        message: "Operation timed out. No response from handler within 10000ms",
        duration: 10200,
      },
    ],
    lintErrors: [
      {
        file: "src/async-handler.ts",
        line: 42,
        column: 12,
        rule: "no-async-without-await",
        message: "Async function declared but async/await not properly used",
        severity: "error",
      },
      {
        file: "src/async-handler.ts",
        line: 89,
        column: 5,
        rule: "prefer-const",
        message: "Variable should be const instead of let",
        severity: "warning",
      },
    ],
    severity: FailureSeverity.HIGH,
    affectedFiles: [
      "src/async-handler.ts",
      "src/retry-policy.ts",
      "tests/async-handler.test.ts",
    ],
    buildDuration: 125000,
  };

  // PR que foi merged
  const mergedPR: MergedPR = {
    number: 234,
    title: "Add async operation handler with retry logic",
    description: "Implements robust async operation handling with exponential backoff",
    author: "dev.silva@manta.com",
    mergeCommit: "f3a4c2b8d9e1f6a0b2c3d4e5f6a7b8c9",
    mergedAt: new Date(Date.now() - 20 * 60000), // 20 min atrás
    headBranch: "feature/async-handler",
    baseCommit: "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  };

  // 1. Propõe rollback
  console.log("[1] Proposing rollback...");
  const proposal = await service.proposeRollback(ciFailure, mergedPR);

  console.log(`✓ Proposal ID: ${proposal.id}`);
  console.log(`  Target Commit: ${proposal.targetCommit.substring(0, 12)}`);
  console.log(`  Severity: ${proposal.severity}`);
  console.log(`  Tests Failed: ${proposal.ciFailure.failedTests.length}`);
  console.log(`  Auto-Approvable: ${proposal.autoApprovalEligible}`);
  console.log(`  Approval Status: ${proposal.approvalStatus}\n`);

  // 2. Se não for auto-approvable, requer aprovação
  if (!proposal.autoApprovalEligible) {
    console.log("[2] Requesting manual approval via Slack & Cowork...");
    const approvalRequest = await service.requestApproval(proposal, "both");

    console.log(`✓ Approval request sent`);
    console.log(`  Channel: ${approvalRequest.channel}`);
    console.log(`  Expires in: ${approvalRequest.expiresAt.getTime() - Date.now()}ms`);
    console.log(`  Token: ${approvalRequest.approvalToken.substring(0, 20)}...\n`);

    // Simula aprovação
    console.log("[3] Simulating approval from reviewer...");
    const approvedProposal = await service.approveRollback(
      proposal.id,
      approvalRequest.approvalToken,
      "reviewer.costa@manta.com"
    );

    console.log(`✓ Rollback approved`);
    console.log(`  Approved by: ${approvedProposal.approvedBy}`);
    console.log(`  Approved at: ${approvedProposal.approvedAt}\n`);
  }

  // 3. Exibe métricas
  const metrics = service.getMetrics();
  console.log("[4] Metrics:");
  console.log(`  Total Failures Detected: ${metrics.totalFailuresDetected}`);
  console.log(`  Total Proposals: ${metrics.totalProposals}`);
  console.log(`  Total Approved: ${metrics.totalApproved}`);
  console.log(`  Auto-Approved: ${metrics.autoApprovedCount}\n`);

  // 4. Exibe audit trail
  console.log("[5] Audit Trail (latest 3 entries):");
  const auditTrail = service.getAuditTrail();
  auditTrail
    .slice(-3)
    .forEach((entry) => {
      console.log(`  [${entry.timestamp.toISOString()}] ${entry.action} (${entry.status})`);
      if (entry.error) console.log(`    Error: ${entry.error}`);
    });
}

/**
 * Cenário 2: Auto-approval para HIGH severity com múltiplas falhas
 */
async function scenario2_HighSeverityAutoApproval() {
  console.log("\n=== Scenario 2: High Severity with Auto-Approval ===\n");

  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-hub",
    minFailuresForAutoApproval: 5,
    minConfidenceForAutoApproval: 0.90,
    maxAutoApprovalSeverity: FailureSeverity.HIGH,
    autoExecuteOnApproval: true, // Auto-execute após aprovação
  });

  // Simula alta gravidade com muitas falhas
  const ciFailure: CIFailure = {
    commitSha: "7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    commitMessage: "Refactor core validation logic",
    author: "dev.santos@manta.com",
    committedAt: new Date(Date.now() - 10 * 60000),
    workflowRunId: 123456789,
    failedTests: Array.from({ length: 12 }, (_, i) => ({
      name: `validation test ${i + 1}`,
      suite: "validation.test.ts",
      message: `Failed assertion on test case ${i + 1}`,
      duration: 150 + i * 50,
    })),
    lintErrors: Array.from({ length: 3 }, (_, i) => ({
      file: "src/validation.ts",
      line: 20 + i * 10,
      column: 5,
      rule: "invalid-pattern",
      message: `Pattern violation at line ${20 + i * 10}`,
      severity: "error" as const,
    })),
    severity: FailureSeverity.HIGH,
    affectedFiles: ["src/validation.ts", "src/index.ts"],
    buildDuration: 180000,
  };

  console.log("[1] Detecting CI failure (HIGH severity, 12 failed tests)...");
  const proposal = await service.proposeRollback(ciFailure);

  console.log(`✓ Proposal created with auto-approval: ${proposal.autoApprovalEligible}`);
  console.log(`  Approval Status: ${proposal.approvalStatus}`);

  if (proposal.autoApprovalEligible) {
    console.log("✓ Auto-approved by system (meets confidence threshold)\n");
  }

  // Exibe info de impact analysis
  console.log("[2] Impact Analysis:");
  console.log(`  Files Affected: ${proposal.impact.filesAffected.length}`);
  console.log(`  Tests Fixed: ${proposal.impact.testsFixed}`);
  console.log(`  Confidence: ${(proposal.impact.confidenceLevel * 100).toFixed(1)}%`);
  console.log(`  Estimated Downtime: ${proposal.impact.estimatedDowntime}ms\n`);
}

/**
 * Cenário 3: Rejeição de rollback por reviewer
 */
async function scenario3_ManualRejection() {
  console.log("\n=== Scenario 3: Manual Rejection by Reviewer ===\n");

  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-hub",
    requireManualApprovalForCritical: true,
  });

  const ciFailure: CIFailure = {
    commitSha: "abcdef0123456789abcdef0123456789",
    commitMessage: "Temporary debugging code accidentally committed",
    author: "dev.junior@manta.com",
    committedAt: new Date(),
    workflowRunId: 555555555,
    failedTests: [
      {
        name: "should return correct value",
        suite: "utils.test.ts",
        message: "Expected 42 but got 100 (debug value)",
        duration: 200,
      },
    ],
    lintErrors: [],
    severity: FailureSeverity.LOW,
    affectedFiles: ["src/utils.ts"],
    buildDuration: 90000,
  };

  console.log("[1] Proposing rollback for LOW severity failure...");
  const proposal = await service.proposeRollback(ciFailure);

  console.log("[2] Requesting approval...");
  const approvalRequest = await service.requestApproval(proposal);

  console.log("[3] Reviewer analysis: False alarm");
  console.log("   This is just temporary debug code that developer will fix...\n");

  console.log("[4] Rejecting rollback...");
  const rejectedProposal = await service.rejectRollback(
    proposal.id,
    "False alarm: temporary debug code. Developer fixing in follow-up commit.",
    "reviewer.ana@manta.com"
  );

  console.log(`✓ Rollback rejected`);
  console.log(`  Reason: ${rejectedProposal.rejectionReason}`);
}

/**
 * Cenário 4: Multi-proposal tracking e métricas
 */
async function scenario4_MetricsAndTracking() {
  console.log("\n=== Scenario 4: Metrics and Audit Trail ===\n");

  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-hub",
  });

  // Simula 3 failures em sequência
  const failures = [
    {
      sha: "fail001",
      message: "First failure",
      testsFailed: 3,
      severity: FailureSeverity.MEDIUM,
    },
    {
      sha: "fail002",
      message: "Second failure",
      testsFailed: 7,
      severity: FailureSeverity.HIGH,
    },
    {
      sha: "fail003",
      message: "Third failure",
      testsFailed: 1,
      severity: FailureSeverity.LOW,
    },
  ];

  console.log("[1] Processing multiple CI failures...\n");

  for (const failure of failures) {
    const ciFailure: CIFailure = {
      commitSha: failure.sha,
      commitMessage: failure.message,
      author: "dev@manta.com",
      committedAt: new Date(),
      workflowRunId: Math.random() * 1000000,
      failedTests: Array.from({ length: failure.testsFailed }, (_, i) => ({
        name: `test ${i + 1}`,
        suite: "test.ts",
        message: "Failed",
        duration: 100,
      })),
      lintErrors: [],
      severity: failure.severity,
      affectedFiles: ["src/file.ts"],
      buildDuration: 100000,
    };

    const proposal = await service.proposeRollback(ciFailure);
    console.log(
      `✓ ${failure.message}: ${failure.testsFailed} tests failed (${failure.severity})`
    );
    console.log(
      `  Auto-approvable: ${proposal.autoApprovalEligible}, ID: ${proposal.id.substring(0, 20)}...`
    );
  }

  // Exibe métricas consolidadas
  console.log("\n[2] Consolidated Metrics:");
  const metrics = service.getMetrics();
  console.log(`  Total Failures Detected: ${metrics.totalFailuresDetected}`);
  console.log(`  Total Proposals: ${metrics.totalProposals}`);
  console.log(`  Avg Time to Detect: ${metrics.averageTimeToDetectMinutes} min`);
  console.log(`  Auto-Approved Count: ${metrics.autoApprovedCount}`);

  console.log("\n[3] Active Proposals:");
  const activeProposals = service.getActiveProposals();
  activeProposals.forEach((p) => {
    console.log(`  - ${p.id.substring(0, 20)}... (${p.severity})`);
  });

  console.log("\n[4] Audit Trail Summary:");
  const auditTrail = service.getAuditTrail();
  const actions = new Map<string, number>();
  auditTrail.forEach((entry) => {
    actions.set(entry.action, (actions.get(entry.action) || 0) + 1);
  });
  Array.from(actions.entries()).forEach(([action, count]) => {
    console.log(`  ${action}: ${count} occurrences`);
  });
}

/**
 * Executa todos os cenários
 */
async function runAllScenarios() {
  console.log("╔═══════════════════════════════════════════════════════════╗");
  console.log("║ Rollback Orchestrator - Usage Examples                   ║");
  console.log("╚═══════════════════════════════════════════════════════════╝\n");

  try {
    await scenario1_AutomaticDetectionAndProposal();
    await scenario2_HighSeverityAutoApproval();
    await scenario3_ManualRejection();
    await scenario4_MetricsAndTracking();

    console.log("\n╔═══════════════════════════════════════════════════════════╗");
    console.log("║ All scenarios completed successfully!                    ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");
  } catch (error) {
    console.error("Error running scenarios:", error);
    process.exit(1);
  }
}

// Executa se for chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllScenarios();
}

export { scenario1_AutomaticDetectionAndProposal, scenario2_HighSeverityAutoApproval, scenario3_ManualRejection, scenario4_MetricsAndTracking };
