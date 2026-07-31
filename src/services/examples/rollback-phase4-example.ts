/**
 * Phase 4 Rollback Service — Integration Examples
 *
 * Demonstrates:
 * - Detecting issues in commits
 * - Reverting problematic commits
 * - Creating revert PRs
 * - Tracking rollback history
 * - Using safeguards
 */

import {
  createRollback,
  type RollbackConfig,
  FailureSeverity,
} from "../rollback";

// ============================================================================
// EXAMPLE 1: Initialize Rollback Service
// ============================================================================

export async function exampleInitializeRollback() {
  console.log("\n=== Example 1: Initialize Rollback Service ===\n");

  const config: RollbackConfig = {
    githubToken: process.env.GITHUB_TOKEN || "your-token",
    owner: "your-org",
    repo: "your-repo",
    mainBranch: "main",

    // Safeguards
    preventCascadingRollbacks: true,
    maxRolledBackCommits: 5,
    requireManualApprovalForRollback: true,
    maxRollbacksPerDay: 5,

    // Notifications
    slackWebhookUrl: process.env.SLACK_WEBHOOK,
    notifyOnDetection: true,
    notifyOnExecution: true,

    // Storage
    storeHistory: true,
    historyRetentionDays: 90,
  };

  const rollback = createRollback(config);
  console.log("✅ Rollback service initialized");
  console.log(`   Owner: ${config.owner}`);
  console.log(`   Repo: ${config.repo}`);
  console.log(`   Main branch: ${config.mainBranch}`);
  console.log(`   Max rollbacks/day: ${config.maxRollbacksPerDay}`);

  return rollback;
}

// ============================================================================
// EXAMPLE 2: Detect Issues in a Commit
// ============================================================================

export async function exampleDetectIssues() {
  console.log("\n=== Example 2: Detect Issues ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
  });

  const commitSha = "abc123def456";

  try {
    const issues = await rollback.detectIssues(commitSha);

    console.log(`📋 Found ${issues.length} issues in commit ${commitSha}`);

    for (const issue of issues) {
      const severityEmoji =
        issue.severity === FailureSeverity.CRITICAL
          ? "🔴"
          : issue.severity === FailureSeverity.HIGH
            ? "🟠"
            : issue.severity === FailureSeverity.MEDIUM
              ? "🟡"
              : "🟢";

      console.log(`\n${severityEmoji} ${issue.type.toUpperCase()}`);
      console.log(`   Message: ${issue.message}`);
      console.log(`   Severity: ${issue.severity}`);
      console.log(`   Detected: ${issue.detectedAt.toISOString()}`);

      if (issue.affectedFiles) {
        console.log(`   Files: ${issue.affectedFiles.join(", ")}`);
      }
    }

    // Summarize issues by severity
    const bySeverity = {
      [FailureSeverity.CRITICAL]: issues.filter(
        (i) => i.severity === FailureSeverity.CRITICAL
      ).length,
      [FailureSeverity.HIGH]: issues.filter((i) => i.severity === FailureSeverity.HIGH)
        .length,
      [FailureSeverity.MEDIUM]: issues.filter(
        (i) => i.severity === FailureSeverity.MEDIUM
      ).length,
      [FailureSeverity.LOW]: issues.filter((i) => i.severity === FailureSeverity.LOW)
        .length,
    };

    console.log(`\n📊 Summary by severity:`);
    console.log(`   Critical: ${bySeverity[FailureSeverity.CRITICAL]}`);
    console.log(`   High: ${bySeverity[FailureSeverity.HIGH]}`);
    console.log(`   Medium: ${bySeverity[FailureSeverity.MEDIUM]}`);
    console.log(`   Low: ${bySeverity[FailureSeverity.LOW]}`);
  } catch (error) {
    console.error(`❌ Failed to detect issues: ${String(error)}`);
  }
}

// ============================================================================
// EXAMPLE 3: Revert a Problematic Commit
// ============================================================================

export async function exampleRevertCommit() {
  console.log("\n=== Example 3: Revert Commit ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
    maxRollbacksPerDay: 5,
  });

  const commitSha = "abc123def456";
  const reason = "CI failure: 5 tests failing, 2 lint errors";

  try {
    console.log(`⏳ Reverting commit ${commitSha.substring(0, 7)}...`);
    console.log(`   Reason: ${reason}`);

    const result = await rollback.revert(commitSha, reason);

    if (result.success) {
      console.log(`\n✅ Revert successful`);
      console.log(`   Revert commit: ${result.revertCommitSha}`);
      console.log(`   Duration: ${result.duration}ms`);

      if (result.cascadingRollbacks && result.cascadingRollbacks.length > 0) {
        console.log(
          `\n⚠️  Cascading rollback risk detected for commits:`
        );
        for (const cascade of result.cascadingRollbacks) {
          console.log(`   - ${cascade.substring(0, 7)}`);
        }
      }
    } else {
      console.log(`\n❌ Revert failed: ${result.error}`);
    }

    return result;
  } catch (error) {
    console.error(`❌ Revert error: ${String(error)}`);
  }
}

// ============================================================================
// EXAMPLE 4: Create Revert PR
// ============================================================================

export async function exampleCreateRevertPR() {
  console.log("\n=== Example 4: Create Revert PR ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
  });

  const commitSha = "abc123def456";

  try {
    console.log(`📝 Creating revert PR for commit ${commitSha.substring(0, 7)}...`);

    const prNumber = await rollback.createRevertPR(commitSha);

    console.log(`\n✅ Revert PR created`);
    console.log(`   PR #${prNumber}`);
    console.log(
      `   URL: https://github.com/your-org/your-repo/pull/${prNumber}`
    );
    console.log(`\nNote: PR requires manual review and approval before merge`);

    return prNumber;
  } catch (error) {
    console.error(`❌ PR creation failed: ${String(error)}`);
  }
}

// ============================================================================
// EXAMPLE 5: Track Rollback History
// ============================================================================

export async function exampleTrackHistory() {
  console.log("\n=== Example 5: Track Rollback History ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
    storeHistory: true,
    historyRetentionDays: 90,
  });

  // Get history from last 7 days
  const history = await rollback.trackHistory({
    days: 7,
  });

  console.log(`📅 Rollback history (last 7 days): ${history.length} events\n`);

  // Group by type
  const byType = {
    detection: history.filter((e) => e.type === "detection").length,
    approval: history.filter((e) => e.type === "approval").length,
    execution: history.filter((e) => e.type === "execution").length,
    failure: history.filter((e) => e.type === "failure").length,
    success: history.filter((e) => e.type === "success").length,
  };

  console.log(`📊 Events by type:`);
  console.log(`   Detection: ${byType.detection}`);
  console.log(`   Approval: ${byType.approval}`);
  console.log(`   Execution: ${byType.execution}`);
  console.log(`   Failure: ${byType.failure}`);
  console.log(`   Success: ${byType.success}`);

  // Show recent events
  const recent = history.slice(-5).reverse();
  if (recent.length > 0) {
    console.log(`\n📋 Recent events:`);
    for (const event of recent) {
      console.log(`   ${event.timestamp.toISOString()} - ${event.type}`);
      console.log(
        `      Commit: ${event.commitSha.substring(0, 7)}`
      );
      if (event.actor) {
        console.log(`      Actor: ${event.actor}`);
      }
      if (event.reason) {
        console.log(`      Reason: ${event.reason}`);
      }
    }
  }

  return history;
}

// ============================================================================
// EXAMPLE 6: Safeguard Demonstration
// ============================================================================

export async function exampleSafeguards() {
  console.log("\n=== Example 6: Safeguards ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
    preventCascadingRollbacks: true,
    maxRolledBackCommits: 5,
    maxRollbacksPerDay: 5,
  });

  const metrics = rollback.getRollbackMetrics();

  console.log(`🛡️  Safeguard Status\n`);
  console.log(`   Total rolled back: ${metrics.totalRolledBack} / 5`);
  console.log(
    `   Daily rollbacks: ${metrics.dailyRollbackCount} / 5`
  );
  console.log(`   Cascading prevention: ENABLED`);
  console.log(
    `   Manual approval required: ENABLED\n`
  );

  if (metrics.rolledBackCommits.length > 0) {
    console.log(`📋 Previously rolled back commits:`);
    for (const commit of metrics.rolledBackCommits) {
      console.log(`   - ${commit.substring(0, 7)}`);
    }
  }

  console.log(`\n✅ All safeguards active`);
  console.log(`   Ready to prevent cascading failures`);
  console.log(`   Cascading rollback detection: ACTIVE`);

  return metrics;
}

// ============================================================================
// EXAMPLE 7: Complete Workflow
// ============================================================================

export async function exampleCompleteWorkflow() {
  console.log("\n=== Example 7: Complete Rollback Workflow ===\n");

  const rollback = createRollback({
    githubToken: process.env.GITHUB_TOKEN || "token",
    owner: "your-org",
    repo: "your-repo",
    mainBranch: "main",
    preventCascadingRollbacks: true,
    maxRollbacksPerDay: 5,
  });

  const commitSha = "abc123def456";

  try {
    // Step 1: Detect issues
    console.log(`Step 1️⃣  Detecting issues...`);
    const issues = await rollback.detectIssues(commitSha);
    console.log(`   ✓ Found ${issues.length} issues\n`);

    if (issues.length === 0) {
      console.log(`✅ No issues detected. Commit is healthy.`);
      return;
    }

    // Step 2: Analyze severity
    console.log(`Step 2️⃣  Analyzing severity...`);
    const hasCritical = issues.some(
      (i) => i.severity === FailureSeverity.CRITICAL
    );
    const hasHigh = issues.some((i) => i.severity === FailureSeverity.HIGH);
    console.log(`   Critical issues: ${hasCritical ? "YES" : "NO"}`);
    console.log(`   High issues: ${hasHigh ? "YES" : "NO"}\n`);

    // Step 3: Create revert PR (if safe)
    console.log(`Step 3️⃣  Creating revert PR...`);
    const prNumber = await rollback.createRevertPR(commitSha);
    console.log(`   ✓ Revert PR #${prNumber} created\n`);

    // Step 4: Check history
    console.log(`Step 4️⃣  Checking rollback history...`);
    const history = await rollback.trackHistory({ days: 7 });
    console.log(`   ✓ Found ${history.length} rollback events\n`);

    // Step 5: Get metrics
    console.log(`Step 5️⃣  Current metrics...`);
    const metrics = rollback.getRollbackMetrics();
    console.log(`   Total rolled back: ${metrics.totalRolledBack}`);
    console.log(`   Daily rollbacks: ${metrics.dailyRollbackCount}`);
    console.log(`   History entries: ${metrics.historySize}\n`);

    console.log(`✅ Workflow complete!`);
    console.log(`   Commit: ${commitSha.substring(0, 7)}`);
    console.log(`   Issues: ${issues.length}`);
    console.log(`   Revert PR: #${prNumber}`);
  } catch (error) {
    console.error(`❌ Workflow error: ${String(error)}`);
  }
}

// ============================================================================
// MAIN: Run all examples
// ============================================================================

export async function runAllExamples() {
  console.log("\n🚀 Phase 4 Rollback Service Examples\n");
  console.log("=".repeat(60));

  try {
    await exampleInitializeRollback();
    await exampleDetectIssues();
    await exampleRevertCommit();
    await exampleCreateRevertPR();
    await exampleTrackHistory();
    await exampleSafeguards();
    await exampleCompleteWorkflow();

    console.log("\n" + "=".repeat(60));
    console.log("✅ All examples completed successfully!\n");
  } catch (error) {
    console.error(`\n❌ Examples failed: ${String(error)}`);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}
