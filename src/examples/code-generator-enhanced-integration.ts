/**
 * Code Generator Enhanced — Integration Examples
 *
 * Demonstrates practical usage of CodeGeneratorPR for:
 * - PR analysis and automation
 * - GitHub Actions integration
 * - Quality reporting
 * - Batch code improvements
 */

import {
  CodeGeneratorPR,
  createCodeGeneratorPR,
  type PRContext,
  type PRAnalysisResult,
} from "@/services/code-generator-enhanced";
import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

// ============================================================================
// EXAMPLE 1: Basic PR Analysis
// ============================================================================

/**
 * Analyze a single PR and print summary
 */
export async function exampleBasicPRAnalysis() {
  console.log("\n=== Example 1: Basic PR Analysis ===\n");

  const generator = createCodeGeneratorPR();

  const prContext: PRContext = {
    title: "Add user authentication with JWT",
    description: "Implements JWT-based authentication system",
    branch: "feature/jwt-auth",
    author: "dev@example.com",
    changedFiles: {
      "src/auth/jwt.ts": `
export class JWTAuthenticator {
  constructor(private secret: string) {}

  generateToken(userId: string): string {
    // Token generation logic
    return "token";
  }

  verifyToken(token: string): boolean {
    // Token verification
    return true;
  }
}
      `,
      "src/auth/middleware.ts": `
export function authMiddleware(req, res, next) {
  const token = req.headers.authorization;
  // Missing error handling!
  const user = verifyToken(token);
  req.user = user;
  next();
}
      `,
    },
  };

  const result = await generator.analyzePR(prContext);

  console.log("PR Analysis Result:");
  console.log("==================");
  console.log(`Status: ${result.status}`);
  console.log(`Processing time: ${result.processingTimeMs}ms`);
  console.log("\nSummary:");
  console.log(`  Total issues found: ${result.summary.totalIssuesFound}`);
  console.log(`  Critical issues: ${result.summary.criticalIssues}`);
  console.log(`  High issues: ${result.summary.highIssues}`);
  console.log(
    `  Estimated test coverage: ${result.summary.estimatedTestCoverage}%`
  );
  console.log(
    `  Estimated refactoring time: ${result.summary.estimatedRefactoringTime}`
  );
  console.log(`  Overall risk level: ${result.summary.overallRiskLevel}`);

  if (result.fixes.length > 0) {
    console.log("\nFixes suggested:");
    result.fixes.forEach((fix) => {
      console.log(`  - [${fix.severity.toUpperCase()}] ${fix.description}`);
      console.log(
        `    Issue: ${fix.issueType} | Confidence: ${fix.confidence}%`
      );
    });
  }

  if (result.refactorings.length > 0) {
    console.log("\nRefactorings suggested:");
    result.refactorings.forEach((ref) => {
      console.log(
        `  - ${ref.type}: ${ref.description} (impact: ${ref.impact}/10)`
      );
    });
  }

  if (result.improvements.length > 0) {
    console.log("\nImprovements suggested:");
    result.improvements.forEach((imp) => {
      console.log(`  - [${imp.category}] ${imp.description}`);
    });
  }

  return result;
}

// ============================================================================
// EXAMPLE 2: GitHub Actions Integration
// ============================================================================

/**
 * Integration for GitHub Actions workflow
 * Analyzes PR and creates detailed review comment
 */
export async function exampleGitHubActionsIntegration(prContext: PRContext) {
  console.log("\n=== Example 2: GitHub Actions Integration ===\n");

  const generator = createCodeGeneratorPR();
  const result = await generator.analyzePR(prContext);

  // Format as GitHub comment
  const comment = formatGitHubReviewComment(result);

  console.log("Generated GitHub Review Comment:");
  console.log("================================");
  console.log(comment);

  // In real GitHub Actions, would use:
  // await github.rest.issues.createComment({
  //   owner, repo, issue_number,
  //   body: comment
  // });

  return comment;
}

/**
 * Formats analysis result as GitHub review comment
 */
function formatGitHubReviewComment(result: PRAnalysisResult): string {
  const riskEmoji = {
    low: "🟢",
    medium: "🟡",
    high: "🔴",
    critical: "🚨",
  };

  let comment = `# Code Analysis Report

${riskEmoji[result.summary.overallRiskLevel]} **Overall Risk Level**: ${result.summary.overallRiskLevel.toUpperCase()}

## Summary
- **Total Issues Found**: ${result.summary.totalIssuesFound}
- **Critical Issues**: ${result.summary.criticalIssues}
- **High Issues**: ${result.summary.highIssues}
- **Estimated Test Coverage**: ${result.summary.estimatedTestCoverage}%
- **Estimated Refactoring Time**: ${result.summary.estimatedRefactoringTime}

`;

  if (result.summary.criticalIssues > 0) {
    comment += `## 🚨 Critical Issues (${result.summary.criticalIssues})\n\n`;
    result.fixes
      .filter((f) => f.severity === "critical")
      .forEach((fix) => {
        comment += `### ${fix.description}\n`;
        comment += `- **Type**: ${fix.issueType}\n`;
        comment += `- **Location**: ${fix.location || "N/A"}\n`;
        comment += `- **Explanation**: ${fix.explanation}\n`;
        comment += `- **Suggested Fix**: \`\`\`${fix.suggestedCode}\`\`\`\n\n`;
      });
  }

  if (result.fixes.filter((f) => f.severity === "high").length > 0) {
    comment += `## ⚠️ High Priority Issues\n\n`;
    result.fixes
      .filter((f) => f.severity === "high")
      .forEach((fix) => {
        comment += `- **${fix.description}**: ${fix.explanation}\n`;
      });
    comment += "\n";
  }

  if (result.refactorings.length > 0) {
    comment += `## 📝 Refactoring Suggestions (${result.refactorings.length})\n\n`;
    result.refactorings
      .sort((a, b) => b.impact - a.impact)
      .slice(0, 5) // Top 5
      .forEach((ref) => {
        comment += `- **${ref.type}**: ${ref.description} (Impact: ${ref.impact}/10)\n`;
      });
    if (result.refactorings.length > 5) {
      comment += `- ... and ${result.refactorings.length - 5} more\n`;
    }
    comment += "\n";
  }

  if (result.testSuite) {
    comment += `## ✅ Test Generation\n`;
    comment += `- **Framework**: ${result.testSuite.testFramework}\n`;
    comment += `- **Test Cases**: ${result.testSuite.testCaseCount}\n`;
    comment += `- **Expected Coverage**: ${result.testSuite.expectedCoverage}%\n`;
    comment += `- **Suggested File**: \`${result.testSuite.suggestedFileName}\`\n\n`;
  }

  if (result.errors.length > 0) {
    comment += `## ❌ Analysis Errors\n`;
    result.errors.forEach((error) => {
      comment += `- ${error}\n`;
    });
  }

  comment += `\n---\n`;
  comment += `Generated by Code Generator Enhanced (Phase 3)\n`;
  comment += `Processed in ${result.processingTimeMs}ms`;

  return comment;
}

// ============================================================================
// EXAMPLE 3: Quality Report Generation
// ============================================================================

/**
 * Generate comprehensive quality report for multiple files
 */
export async function exampleQualityReportGeneration() {
  console.log("\n=== Example 3: Quality Report Generation ===\n");

  const projectRoot = process.cwd();
  const generator = createCodeGeneratorPR(projectRoot);

  // Sample files to analyze
  const files = [
    {
      name: "services/auth.ts",
      content: `
export function authenticate(token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return payload;
}
      `,
    },
    {
      name: "utils/database.ts",
      content: `
export async function queryUsers(id) {
  return await db.query("SELECT * FROM users WHERE id = " + id);
}
      `,
    },
  ];

  const report = {
    timestamp: new Date().toISOString(),
    projectPath: projectRoot,
    files: [] as any[],
    summary: {
      totalFiles: files.length,
      totalIssues: 0,
      totalRefactorings: 0,
      averageRiskLevel: "medium" as const,
    },
  };

  for (const file of files) {
    console.log(`Analyzing ${file.name}...`);

    const fixes = await generator.generateFixes(file.content);
    const refactorings = await generator.generateRefactorings(file.content);
    const improvements = await generator.suggestImprovements(file.content);

    const fileReport = {
      name: file.name,
      issues: fixes.length,
      refactorings: refactorings.length,
      improvements: improvements.length,
      criticalIssues: fixes.filter((f) => f.severity === "critical").length,
      highIssues: fixes.filter((f) => f.severity === "high").length,
    };

    report.files.push(fileReport);
    report.summary.totalIssues += fixes.length;
    report.summary.totalRefactorings += refactorings.length;

    console.log(`  Issues: ${fixes.length}, Refactorings: ${refactorings.length}`);
  }

  console.log("\n=== Quality Report ===");
  console.log(JSON.stringify(report, null, 2));

  // In real scenario, would save to file:
  // writeFileSync('quality-report.json', JSON.stringify(report, null, 2));

  return report;
}

// ============================================================================
// EXAMPLE 4: Test Generation and Output
// ============================================================================

/**
 * Generate test suite and save to file
 */
export async function exampleTestGeneration() {
  console.log("\n=== Example 4: Test Generation ===\n");

  const generator = createCodeGeneratorPR();

  const sourceCode = `
export function calculatePrice(basePrice: number, taxRate: number): number {
  return basePrice * (1 + taxRate);
}

export function applyDiscount(price: number, discountPercent: number): number {
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error("Invalid discount");
  }
  return price * (1 - discountPercent / 100);
}

export function formatPrice(price: number, currency: string = "USD"): string {
  return \`\${currency} \${price.toFixed(2)}\`;
}
  `;

  // Generate test suite
  const testSuite = await generator.generateTests(sourceCode, "jest");

  console.log("Generated Test Suite:");
  console.log("====================");
  console.log(`Framework: ${testSuite.testFramework}`);
  console.log(`Expected Coverage: ${testSuite.expectedCoverage}%`);
  console.log(`Test Cases: ${testSuite.testCaseCount}`);
  console.log(`Functions Tested: ${testSuite.testedFunctions.join(", ")}`);
  console.log("\nTest Scenarios:");
  testSuite.scenarios.forEach((scenario) => {
    console.log(`  - ${scenario.name}: ${scenario.description}`);
    console.log(`    Tests: ${scenario.testCaseNames.join(", ")}`);
  });

  console.log("\nFirst 500 chars of test code:");
  console.log("----------------------------");
  console.log(testSuite.testCode.substring(0, 500) + "...");

  // In real scenario, would save:
  // writeFileSync(
  //   `src/${testSuite.suggestedFileName}`,
  //   testSuite.testCode
  // );

  return testSuite;
}

// ============================================================================
// EXAMPLE 5: Fix-and-Commit Workflow
// ============================================================================

/**
 * Analyze diff, fix issues, and prepare commit
 */
export async function exampleFixAndCommitWorkflow() {
  console.log("\n=== Example 5: Fix-and-Commit Workflow ===\n");

  const generator = createCodeGeneratorPR();

  // Sample diff
  const diff = `
--- a/src/utils.ts
+++ b/src/utils.ts
@@ -1,5 +1,10 @@
+export function getUser(id: string) {
+  const users = { '1': { name: 'Alice' } };
+  return users[id].name;  // Missing null check!
+}

export function calculateTotal(items) {
   return items.reduce((sum, item) => sum + item.price, 0);
}
  `;

  const fixes = await generator.generateFixes(diff);

  console.log("Issues Found in Diff:");
  console.log("====================");
  fixes.forEach((fix) => {
    console.log(`\n[${fix.severity.toUpperCase()}] ${fix.description}`);
    console.log(`Issue: ${fix.issueType}`);
    console.log(`Location: ${fix.location}`);
    console.log(`\nCurrent:\n  ${fix.problematicCode}`);
    console.log(`\nProposed Fix:\n  ${fix.suggestedCode}`);
    console.log(`\nExplanation: ${fix.explanation}`);
    console.log(`Confidence: ${fix.confidence}%`);
  });

  // Prepare commit message
  const commitMessage = generateCommitMessage(fixes);
  console.log("\n\nGenerated Commit Message:");
  console.log("========================");
  console.log(commitMessage);

  return { fixes, commitMessage };
}

/**
 * Generate meaningful commit message from fixes
 */
function generateCommitMessage(fixes: any[]): string {
  const criticalCount = fixes.filter((f) => f.severity === "critical").length;
  const highCount = fixes.filter((f) => f.severity === "high").length;

  const types = fixes.reduce(
    (acc, fix) => {
      acc.add(fix.issueType);
      return acc;
    },
    new Set<string>()
  );

  const title = criticalCount > 0
    ? "fix: address critical issues"
    : highCount > 0
      ? `fix: resolve ${highCount} high-priority issues`
      : "refactor: improve code quality";

  const body =
    `
- Fixed ${fixes.length} issues found during code analysis
${fixes.map((f) => `  - ${f.description} (${f.severity})`).join("\n")}

Issues addressed:
${Array.from(types)
  .map((type) => `- ${type}`)
  .join("\n")}

Generated by Code Generator Enhanced v2.0.0
  `.trim();

  return `${title}\n\n${body}`;
}

// ============================================================================
// EXAMPLE 6: Audit Log Analysis
// ============================================================================

/**
 * Analyze audit log for insights
 */
export async function exampleAuditLogAnalysis() {
  console.log("\n=== Example 6: Audit Log Analysis ===\n");

  const generator = createCodeGeneratorPR();

  // Get statistics
  const stats = generator.getAuditStats();
  const cacheStats = generator.getCacheStats();

  console.log("Audit Statistics:");
  console.log("================");
  console.log(`Total Actions: ${stats.totalActions}`);
  console.log(
    `Success Rate: ${stats.totalActions === 0 ? "N/A" : ((stats.successCount / stats.totalActions) * 100).toFixed(2)}%`
  );
  console.log(`Success Count: ${stats.successCount}`);
  console.log(`Error Count: ${stats.errorCount}`);
  console.log(
    `Average Execution Time: ${stats.averageExecutionTime.toFixed(0)}ms`
  );

  console.log("\nCache Statistics:");
  console.log("================");
  console.log(`Cache Entries: ${cacheStats.entries}`);
  console.log(`Cache Size: ${cacheStats.size}`);

  // Save audit log
  generator.saveAuditLog();
  console.log("\nAudit log saved to: .claude/logs/code-gen-audit.jsonl");

  return { stats, cacheStats };
}

// ============================================================================
// MAIN RUNNER
// ============================================================================

/**
 * Run all examples
 */
export async function runAllExamples() {
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║   Code Generator Enhanced (Phase 3) — Integration Examples ║");
  console.log("╚════════════════════════════════════════════════════════════╝");

  try {
    // Run examples in sequence
    await exampleBasicPRAnalysis();
    await exampleGitHubActionsIntegration({
      title: "Refactor authentication module",
      description: "Improve code quality and security",
      changedFiles: {
        "src/auth.ts": "// sample code",
      },
    });
    await exampleQualityReportGeneration();
    await exampleTestGeneration();
    await exampleFixAndCommitWorkflow();
    await exampleAuditLogAnalysis();

    console.log("\n╔════════════════════════════════════════════════════════════╗");
    console.log("║                   All Examples Completed                    ║");
    console.log("╚════════════════════════════════════════════════════════════╝");
  } catch (error) {
    console.error("Error running examples:", error);
    throw error;
  }
}

// Export for use as module or CLI
if (require.main === module) {
  runAllExamples().catch(console.error);
}
