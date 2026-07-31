/**
 * Code Reviewer Integration Example
 *
 * Demonstrates how to integrate CodeReviewer with other Manta services:
 * - PR Automation Engine
 * - Feedback Engine
 * - CI/CD Orchestrator
 * - LLM Judge
 */

import { CodeReviewer } from "../code-reviewer";
import type { Review, SecurityIssue } from "../code-reviewer";

// ============================================================================
// INTEGRATION 1: CodeReviewer + PR Automation
// ============================================================================

export class PRReviewIntegration {
  private codeReviewer: CodeReviewer;

  constructor() {
    this.codeReviewer = new CodeReviewer({
      useDeepAnalysis: true,
    });
  }

  /**
   * Analyzes PR code and determines merge strategy
   */
  async analyzePullRequest(input: {
    prNumber: number;
    title: string;
    code: string;
    filepath: string;
    ciPassed: boolean;
  }) {
    const review = await this.codeReviewer.reviewCode(input.code, {
      filepath: input.filepath,
      language: "typescript",
    });

    return this.determineMergeStrategy(review, input);
  }

  /**
   * Determines whether to auto-merge, request changes, or comment
   */
  private determineMergeStrategy(
    review: Review,
    prInfo: { prNumber: number; ciPassed: boolean }
  ) {
    const criticalSecurity = review.securityIssues.filter(
      (i) => i.severity === "critical"
    );
    const errors = review.securityIssues.filter(
      (i) => i.severity === "error"
    );

    // Decision matrix
    if (criticalSecurity.length > 0) {
      return {
        decision: "REQUEST_CHANGES",
        reason: `${criticalSecurity.length} critical security issue(s) must be fixed`,
        issues: criticalSecurity,
        action: "BLOCK_MERGE",
      };
    }

    if (errors.length > 0 && !prInfo.ciPassed) {
      return {
        decision: "REQUEST_CHANGES",
        reason: "Security or quality errors + CI failures",
        issues: errors,
        action: "REQUEST_CHANGES",
      };
    }

    if (errors.length > 0 && prInfo.ciPassed) {
      return {
        decision: "CONDITIONAL_MERGE",
        reason: "Issues present but CI passed",
        issues: errors,
        action: "COMMENT",
      };
    }

    if (review.overallScore >= 85) {
      return {
        decision: "AUTO_MERGE",
        reason: `Excellent code quality (${review.overallScore}/100)`,
        action: "APPROVE",
      };
    }

    return {
      decision: "COMMENT",
      reason: review.summary,
      recommendations: review.recommendations,
      action: "COMMENT",
    };
  }
}

// ============================================================================
// INTEGRATION 2: CodeReviewer + Quality Metrics
// ============================================================================

export class CodeQualityMetrics {
  private codeReviewer: CodeReviewer;
  private metrics: Map<string, Review[]> = new Map();

  constructor() {
    this.codeReviewer = new CodeReviewer();
  }

  /**
   * Tracks code quality over time
   */
  async trackCodeQuality(
    code: string,
    filepath: string,
    timestamp: Date = new Date()
  ) {
    const review = await this.codeReviewer.reviewCode(code, {
      filepath,
      language: "typescript",
    });

    // Store review for analysis
    if (!this.metrics.has(filepath)) {
      this.metrics.set(filepath, []);
    }
    this.metrics.get(filepath)!.push(review);

    return review;
  }

  /**
   * Generates quality report for a file
   */
  generateQualityReport(filepath: string) {
    const reviews = this.metrics.get(filepath) || [];

    if (reviews.length === 0) {
      return null;
    }

    const latestReview = reviews[reviews.length - 1];
    const avgScore =
      reviews.reduce((sum, r) => sum + r.overallScore, 0) / reviews.length;
    const trend = this.calculateTrend(reviews);

    return {
      filepath,
      currentScore: latestReview.overallScore,
      averageScore: Math.round(avgScore),
      trend,
      reviewCount: reviews.length,
      criticalIssues: latestReview.securityIssues.filter(
        (i) => i.severity === "critical"
      ).length,
      errorIssues: latestReview.securityIssues.filter((i) => i.severity === "error").length,
      improvements: latestReview.improvements,
    };
  }

  /**
   * Calculates score trend (improving, stable, declining)
   */
  private calculateTrend(reviews: Review[]): "improving" | "stable" | "declining" {
    if (reviews.length < 2) return "stable";

    const recent = reviews.slice(-3);
    const older = reviews.slice(-6, -3);

    const recentAvg =
      recent.reduce((sum, r) => sum + r.overallScore, 0) / recent.length;
    const olderAvg =
      older.length > 0
        ? older.reduce((sum, r) => sum + r.overallScore, 0) / older.length
        : recentAvg;

    if (recentAvg > olderAvg + 5) return "improving";
    if (recentAvg < olderAvg - 5) return "declining";
    return "stable";
  }
}

// ============================================================================
// INTEGRATION 3: CodeReviewer + Issue Tracking
// ============================================================================

export class CodeIssueTracker {
  private codeReviewer: CodeReviewer;
  private issueRegistry: Map<string, SecurityIssue[]> = new Map();

  constructor() {
    this.codeReviewer = new CodeReviewer();
  }

  /**
   * Scans code and registers new issues
   */
  async scanForIssues(code: string, filepath: string) {
    const issues = await this.codeReviewer.analyzeSecurityIssues(code, {
      filepath,
      language: "typescript",
    });

    // Register high-severity issues
    const tracked = issues.filter((i) =>
      ["error", "critical"].includes(i.severity)
    );

    if (tracked.length > 0) {
      this.issueRegistry.set(filepath, tracked);
    }

    return {
      filepath,
      issueCount: tracked.length,
      issues: tracked,
    };
  }

  /**
   * Gets all critical issues across codebase
   */
  getCriticalIssues() {
    const critical: Array<{ file: string; issues: SecurityIssue[] }> = [];

    for (const [filepath, issues] of this.issueRegistry.entries()) {
      const criticalInFile = issues.filter((i) => i.severity === "critical");
      if (criticalInFile.length > 0) {
        critical.push({ file: filepath, issues: criticalInFile });
      }
    }

    return critical.sort((a, b) => b.issues.length - a.issues.length);
  }

  /**
   * Generates issue summary
   */
  generateIssueSummary() {
    let totalCritical = 0;
    let totalError = 0;

    for (const issues of this.issueRegistry.values()) {
      totalCritical += issues.filter((i) => i.severity === "critical").length;
      totalError += issues.filter((i) => i.severity === "error").length;
    }

    return {
      totalFiles: this.issueRegistry.size,
      totalCritical,
      totalError,
      issuesPerFile: Array.from(this.issueRegistry.entries()).map(
        ([file, issues]) => ({
          file,
          count: issues.length,
        })
      ),
    };
  }
}

// ============================================================================
// INTEGRATION 4: CodeReviewer + Education/Coaching
// ============================================================================

export class CodeReviewCoach {
  private codeReviewer: CodeReviewer;

  constructor() {
    this.codeReviewer = new CodeReviewer({
      includeExamples: true,
      useDeepAnalysis: false,
    });
  }

  /**
   * Provides personalized coaching based on code review
   */
  async coachDeveloper(
    code: string,
    developerLevel: "junior" | "mid" | "senior"
  ) {
    const review = await this.codeReviewer.reviewCode(code, {
      language: "typescript",
    });

    return this.generateCoachingPlan(review, developerLevel);
  }

  /**
   * Generates personalized coaching plan
   */
  private generateCoachingPlan(
    review: Review,
    level: "junior" | "mid" | "senior"
  ) {
    const learningPriorities: Record<typeof level, string[]> = {
      junior: [
        "security",
        "basic-patterns",
        "testing",
        "documentation",
        "performance",
      ],
      mid: [
        "advanced-patterns",
        "performance",
        "security",
        "scalability",
        "maintainability",
      ],
      senior: [
        "architecture",
        "system-design",
        "mentoring",
        "code-standards",
        "innovation",
      ],
    };

    const priorities = learningPriorities[level];

    return {
      developerLevel: level,
      coachingFocus: priorities,
      currentWeaknesses: [
        ...review.securityIssues.slice(0, 2),
        ...review.performanceIssues.slice(0, 2),
      ].map((issue) => ({
        area: issue.type,
        description: issue.description,
        resource: this.getLearningResource(issue.type, level),
      })),
      strengths: this.identifyStrengths(review),
      recommendedNextSteps: this.getNextSteps(review, level),
    };
  }

  /**
   * Identifies code strengths
   */
  private identifyStrengths(review: Review) {
    const strengths: string[] = [];

    if (review.improvements.security > 80) strengths.push("Security awareness");
    if (review.improvements.performance > 80) strengths.push("Performance optimization");
    if (review.improvements.codeQuality > 80) strengths.push("Code quality");
    if (review.improvements.testability > 80) strengths.push("Test coverage");

    return strengths;
  }

  /**
   * Gets learning resources
   */
  private getLearningResource(topic: string, level: "junior" | "mid" | "senior") {
    const resources: Record<string, Record<string, string>> = {
      "sql-injection": {
        junior:
          "https://owasp.org/www-community/attacks/SQL_Injection",
        mid: "https://owasp.org/www-project-top-ten/",
        senior:
          "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
      },
      "exposed-secret": {
        junior:
          "https://docs.github.com/en/code-security/secret-scanning",
        mid: "https://www.securecoding.cert.org/",
        senior:
          "https://www.cloudflare.com/learning/security/secrets-management/",
      },
    };

    return resources[topic] || {};
  }

  /**
   * Recommends next steps
   */
  private getNextSteps(
    review: Review,
    level: "junior" | "mid" | "senior"
  ) {
    if (level === "junior") {
      return [
        "Read security best practices documentation",
        "Review code examples from senior developers",
        "Practice writing parameterized queries",
        "Attend security training",
      ];
    } else if (level === "mid") {
      return [
        "Lead a code review session",
        "Propose security standards for the team",
        "Mentor a junior developer",
        "Contribute to architecture decisions",
      ];
    } else {
      return [
        "Define company-wide code standards",
        "Build internal security tooling",
        "Mentor other senior engineers",
        "Review architectural decisions",
      ];
    }
  }
}

// ============================================================================
// INTEGRATION 5: CodeReviewer + Team Dashboard
// ============================================================================

export class TeamCodeHealthDashboard {
  private codeReviewer: CodeReviewer;
  private teamStats: Map<string, Review[]> = new Map();

  constructor() {
    this.codeReviewer = new CodeReviewer();
  }

  /**
   * Tracks team code health
   */
  async trackTeamMember(
    code: string,
    teamMember: string,
    filepath: string
  ) {
    const review = await this.codeReviewer.reviewCode(code, {
      filepath,
      language: "typescript",
    });

    if (!this.teamStats.has(teamMember)) {
      this.teamStats.set(teamMember, []);
    }
    this.teamStats.get(teamMember)!.push(review);

    return review;
  }

  /**
   * Generates team dashboard
   */
  generateTeamDashboard() {
    const teamScores = Array.from(this.teamStats.entries()).map(
      ([member, reviews]) => ({
        member,
        averageScore:
          reviews.reduce((sum, r) => sum + r.overallScore, 0) / reviews.length,
        codeCount: reviews.length,
        securityScore:
          reviews.reduce((sum, r) => sum + r.improvements.security, 0) /
          reviews.length,
        performanceScore:
          reviews.reduce((sum, r) => sum + r.improvements.performance, 0) /
          reviews.length,
      })
    );

    return {
      timestamp: new Date(),
      teamMembers: teamScores.length,
      overallTeamScore:
        teamScores.reduce((sum, m) => sum + m.averageScore, 0) /
        teamScores.length,
      topPerformers: teamScores
        .sort((a, b) => b.averageScore - a.averageScore)
        .slice(0, 3),
      needsAttention: teamScores
        .sort((a, b) => a.averageScore - b.averageScore)
        .slice(0, 3),
      allMemberStats: teamScores,
    };
  }
}

// ============================================================================
// MAIN: Integration Examples
// ============================================================================

async function demonstrateIntegrations() {
  console.log("Code Reviewer Integration Examples\n");

  const sampleCode = `
    async function processPayment(userId, amount) {
      const sql = \`SELECT * FROM users WHERE id = \${userId}\`;
      const user = await db.query(sql);

      for (let i = 0; i < 10000; i++) {
        await api.call(\`/charge?user=\${user.id}&amount=\${amount}\`);
      }

      return true;
    }
  `;

  // Integration 1: PR Review
  console.log("📌 Integration 1: PR Automation\n");
  const prIntegration = new PRReviewIntegration();
  const prDecision = await prIntegration.analyzePullRequest({
    prNumber: 123,
    title: "Add payment processing",
    code: sampleCode,
    filepath: "src/services/payment.ts",
    ciPassed: false,
  });
  console.log(`Decision: ${prDecision.decision}`);
  console.log(`Reason: ${prDecision.reason}\n`);

  // Integration 2: Quality Metrics
  console.log("📊 Integration 2: Quality Metrics\n");
  const qualityMetrics = new CodeQualityMetrics();
  await qualityMetrics.trackCodeQuality(sampleCode, "src/payment.ts");
  const report = qualityMetrics.generateQualityReport("src/payment.ts");
  if (report) {
    console.log(`Score: ${report.currentScore}/100`);
    console.log(`Critical Issues: ${report.criticalIssues}\n`);
  }

  // Integration 3: Issue Tracking
  console.log("🔍 Integration 3: Issue Tracking\n");
  const issueTracker = new CodeIssueTracker();
  const scanResult = await issueTracker.scanForIssues(
    sampleCode,
    "src/payment.ts"
  );
  console.log(`Issues Found: ${scanResult.issueCount}\n`);

  // Integration 4: Coaching
  console.log("👨‍🏫 Integration 4: Developer Coaching\n");
  const coach = new CodeReviewCoach();
  const coachingPlan = await coach.coachDeveloper(sampleCode, "mid");
  console.log(`Level: ${coachingPlan.developerLevel}`);
  console.log(`Focus Areas: ${coachingPlan.coachingFocus.join(", ")}\n`);

  // Integration 5: Team Dashboard
  console.log("📈 Integration 5: Team Dashboard\n");
  const dashboard = new TeamCodeHealthDashboard();
  await dashboard.trackTeamMember(sampleCode, "alice@company.com", "payment.ts");
  await dashboard.trackTeamMember(sampleCode, "bob@company.com", "auth.ts");
  const teamDashboard = dashboard.generateTeamDashboard();
  console.log(`Team Members: ${teamDashboard.teamMembers}`);
  console.log(
    `Overall Team Score: ${teamDashboard.overallTeamScore.toFixed(1)}/100\n`
  );
}

export {
  PRReviewIntegration,
  CodeQualityMetrics,
  CodeIssueTracker,
  CodeReviewCoach,
  TeamCodeHealthDashboard,
};

// Run if executed directly
if (require.main === module) {
  demonstrateIntegrations().catch(console.error);
}
