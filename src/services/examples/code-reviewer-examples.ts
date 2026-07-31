/**
 * Code Reviewer Service — Usage Examples
 *
 * Demonstrates all major capabilities of the CodeReviewer service:
 * - Full code reviews
 * - Security analysis
 * - Performance analysis
 * - Refactoring suggestions
 * - Comment generation
 */

import {
  CodeReviewer,
  reviewCodeFast,
  reviewCodeDeep,
  analyzeSecurity,
  analyzePerformance,
  suggestRefactors,
} from "../code-reviewer";

// ============================================================================
// EXAMPLE 1: Quick Security Scan
// ============================================================================

async function example1_QuickSecurityScan() {
  console.log("\n🔍 Example 1: Quick Security Scan\n");

  const code = `
// Database access without parameterized queries
async function getUserById(userId) {
  const sql = \`SELECT * FROM users WHERE id = \${userId}\`;
  return db.query(sql);
}

// Exposed API key in code
const API_KEY = "sk_live_1234567890abcdef";

// Weak password validation
function validatePassword(password) {
  return password.length > 3;
}
`;

  const issues = await analyzeSecurity(code, {
    filepath: "src/services/user.ts",
    language: "typescript",
  });

  console.log(`Found ${issues.length} security issues:\n`);

  for (const issue of issues) {
    console.log(`[${issue.severity.toUpperCase()}] ${issue.type}`);
    console.log(`  Line: ${issue.line}`);
    console.log(`  Description: ${issue.description}`);
    console.log(`  Impact: ${issue.impact}`);
    console.log(`  Remediation: ${issue.remediation}`);

    if (issue.cweId) {
      console.log(`  CWE: ${issue.cweId}`);
    }

    if (issue.secureExample) {
      console.log(`  Secure Example: ${issue.secureExample}`);
    }

    console.log();
  }
}

// ============================================================================
// EXAMPLE 2: Performance Analysis
// ============================================================================

async function example2_PerformanceAnalysis() {
  console.log("\n⚡ Example 2: Performance Analysis\n");

  const code = `
// N+1 query problem
async function getUsersWithPosts() {
  const users = await db.query("SELECT * FROM users");

  for (const user of users) {
    const posts = await db.query(
      \`SELECT * FROM posts WHERE user_id = \${user.id}\`
    );
    user.posts = posts;
  }

  return users;
}

// Inefficient nested loops
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// Missing cache
function expensiveCalculation(input) {
  // No memoization or caching
  return complexMath(input);
}
`;

  const issues = await analyzePerformance(code, {
    filepath: "src/services/data-loader.ts",
    language: "typescript",
  });

  console.log(`Found ${issues.length} performance issues:\n`);

  for (const issue of issues) {
    console.log(`[${issue.severity.toUpperCase()}] ${issue.type}`);
    console.log(`  Description: ${issue.description}`);

    if (issue.estimatedImpact.timeMs) {
      console.log(`  ⏱️  Time Impact: ~${issue.estimatedImpact.timeMs}ms`);
    }

    if (issue.estimatedImpact.memoryMb) {
      console.log(
        `  💾 Memory Impact: ~${issue.estimatedImpact.memoryMb}MB`
      );
    }

    if (issue.estimatedImpact.degradationPercent) {
      console.log(
        `  📊 Degradation: ~${issue.estimatedImpact.degradationPercent}%`
      );
    }

    console.log(`  Optimization: ${issue.optimization}`);

    if (issue.optimizedExample) {
      console.log(`  Example: ${issue.optimizedExample.substring(0, 80)}...`);
    }

    console.log();
  }
}

// ============================================================================
// EXAMPLE 3: Refactoring Suggestions
// ============================================================================

async function example3_RefactoringSuggestions() {
  console.log("\n🔧 Example 3: Refactoring Suggestions\n");

  const code = `
// Deeply nested conditions
function processOrder(order) {
  if (order) {
    if (order.items) {
      if (order.items.length > 0) {
        if (order.total > 0) {
          if (order.customer) {
            if (order.customer.verified) {
              return processValidOrder(order);
            }
          }
        }
      }
    }
  }
  return null;
}

// Duplicated code
function calculateTaxUS(amount) {
  const rate = 0.07;
  return amount * rate;
}

function calculateTaxCA(amount) {
  const rate = 0.07;
  return amount * rate;
}

function calculateTaxMX(amount) {
  const rate = 0.16;
  return amount * rate;
}

// Magic numbers
function validateUser(user) {
  return user.age >= 18 && user.credits > 100;
}
`;

  const refactorings = await suggestRefactors(code, {
    filepath: "src/services/order.ts",
    language: "typescript",
  });

  console.log(`Found ${refactorings.length} refactoring suggestions:\n`);

  // Sort by priority (highest first)
  const sorted = refactorings.sort((a, b) => b.priority - a.priority);

  for (const ref of sorted) {
    console.log(`[Priority ${ref.priority}] ${ref.type}`);
    console.log(`  Description: ${ref.description}`);
    console.log(`  Benefit: ${ref.benefit}`);
    console.log(`  Rationale: ${ref.rationale}`);

    if (ref.complexity) {
      console.log(
        `  Complexity: ${ref.complexity.before} → ${ref.complexity.after}`
      );
    }

    console.log();
  }
}

// ============================================================================
// EXAMPLE 4: Complete Code Review (Fast)
// ============================================================================

async function example4_CompleteCodeReviewFast() {
  console.log("\n📋 Example 4: Complete Code Review (Fast - Haiku)\n");

  const code = `
import { Router } from 'express';

const router = Router();

router.get('/user/:id', (req, res) => {
  // SQL Injection vulnerability
  const query = \`SELECT * FROM users WHERE id = \${req.params.id}\`;

  db.query(query, (err, results) => {
    if (err) {
      res.status(500).send('Database error');
    } else {
      res.json(results);
    }
  });
});

// Exposed API key (UNSAFE - should use env vars)
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY || "sk_test_placeholder";

export default router;
`;

  const review = await reviewCodeFast(code, {
    filepath: "src/routes/user-routes.ts",
    language: "typescript",
    framework: "express",
  });

  console.log(`Review Status: ${review.status}`);
  console.log(`Overall Score: ${review.overallScore}/100`);
  console.log(`Analysis Time: ${review.analysisTimeMs}ms\n`);

  console.log("📊 Dimension Scores:");
  console.log(`  Security: ${review.improvements.security}/100`);
  console.log(`  Performance: ${review.improvements.performance}/100`);
  console.log(`  Code Quality: ${review.improvements.codeQuality}/100`);
  console.log(`  Testability: ${review.improvements.testability}/100`);
  console.log(`  Maintainability: ${review.improvements.maintainability}/100\n`);

  console.log(`📌 Summary: ${review.summary}\n`);

  console.log("🎯 Recommendations:");
  review.recommendations.forEach((rec) => {
    console.log(`  • ${rec}`);
  });

  console.log(
    `\n🔒 Security Issues (${review.securityIssues.length}):`
  );
  review.securityIssues.forEach((issue) => {
    console.log(
      `  [${issue.severity}] Line ${issue.line}: ${issue.description}`
    );
  });

  console.log(
    `\n⚡ Performance Issues (${review.performanceIssues.length}):`
  );
  review.performanceIssues.forEach((issue) => {
    console.log(
      `  [${issue.severity}] Line ${issue.line}: ${issue.description}`
    );
  });

  console.log(
    `\n💡 Refactoring Suggestions (${review.refactorings.length}):`
  );
  review.refactorings.forEach((ref) => {
    console.log(
      `  [Priority ${ref.priority}] ${ref.type}: ${ref.description}`
    );
  });
}

// ============================================================================
// EXAMPLE 5: Deep Code Review (Opus)
// ============================================================================

async function example5_DeepCodeReviewOpus() {
  console.log("\n🔬 Example 5: Deep Code Review (Opus)\n");

  const code = `
class UserService {
  constructor(db, cache) {
    this.db = db;
    this.cache = cache;
  }

  async getUserById(userId) {
    // Check cache first
    const cached = await this.cache.get(\`user:\${userId}\`);
    if (cached) return cached;

    // Query database
    const user = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [userId]
    );

    if (user) {
      await this.cache.set(\`user:\${userId}\`, user, 3600);
    }

    return user;
  }

  async getUsersByRole(role) {
    // Validate input
    const validRoles = ['admin', 'user', 'guest'];
    if (!validRoles.includes(role)) {
      throw new Error(\`Invalid role: \${role}\`);
    }

    // Use parameterized query
    return this.db.query(
      'SELECT * FROM users WHERE role = $1',
      [role]
    );
  }
}
`;

  const startTime = Date.now();
  const review = await reviewCodeDeep(code, {
    filepath: "src/services/user-service.ts",
    language: "typescript",
    framework: "express",
    dependencies: {
      express: "^4.18.0",
      redis: "^4.0.0",
      pg: "^8.0.0",
    },
  });
  const elapsed = Date.now() - startTime;

  console.log(`Review Status: ${review.status}`);
  console.log(`Overall Score: ${review.overallScore}/100`);
  console.log(`Analysis Time: ${elapsed}ms (LLM: ${review.analysisTimeMs}ms)\n`);

  console.log("📊 Detailed Analysis:");
  console.log(`Security:        ${review.improvements.security}/100`);
  console.log(`Performance:     ${review.improvements.performance}/100`);
  console.log(`Code Quality:    ${review.improvements.codeQuality}/100`);
  console.log(`Testability:     ${review.improvements.testability}/100`);
  console.log(`Maintainability: ${review.improvements.maintainability}/100\n`);

  console.log(`📌 Summary:\n${review.summary}\n`);

  console.log("🎯 Key Recommendations:");
  review.recommendations.slice(0, 3).forEach((rec) => {
    console.log(`  • ${rec}`);
  });

  if (review.securityIssues.length > 0) {
    console.log(`\n🔒 Security Issues (${review.securityIssues.length}):`);
    review.securityIssues.forEach((issue) => {
      console.log(
        `  [${issue.severity}] ${issue.type} at line ${issue.line}`
      );
    });
  }

  if (review.performanceIssues.length > 0) {
    console.log(
      `\n⚡ Performance Issues (${review.performanceIssues.length}):`
    );
    review.performanceIssues.forEach((issue) => {
      console.log(
        `  [${issue.severity}] ${issue.type} at line ${issue.line}`
      );
    });
  }

  console.log(`\n💡 High-Priority Refactorings:`);
  review.refactorings
    .filter((r) => r.priority >= 4)
    .forEach((ref) => {
      console.log(`  [${ref.type}] ${ref.description}`);
    });
}

// ============================================================================
// EXAMPLE 6: PR Review Automation
// ============================================================================

async function example6_PRReviewAutomation() {
  console.log("\n🤖 Example 6: PR Review Automation\n");

  const reviewer = new CodeReviewer({
    useDeepAnalysis: true,
  });

  // Simulating a PR with problematic code
  const prCode = `
// Feature: Add user authentication
import crypto from 'crypto';

export async function authenticateUser(username, password) {
  // TODO: This is a temporary hardcoded password
  const correctPassword = "admin123";

  if (password === correctPassword) {
    return {
      token: crypto.randomBytes(32).toString('hex'),
      user: username
    };
  }

  return null;
}

export function validateToken(token) {
  // Simple token validation (not secure!)
  return token && token.length === 64;
}
`;

  const review = await reviewer.reviewCode(prCode, {
    filepath: "src/auth.ts",
    language: "typescript",
  });

  // Determine PR action based on review
  let action: "APPROVE" | "REQUEST_CHANGES" | "COMMENT" = "APPROVE";
  let reason = "Code review passed";

  if (review.securityIssues.some((i) => i.severity === "critical")) {
    action = "REQUEST_CHANGES";
    reason = "Critical security issues must be fixed";
  } else if (
    review.securityIssues.some((i) => i.severity === "error") ||
    review.overallScore < 60
  ) {
    action = "COMMENT";
    reason = "Security or quality concerns require attention";
  }

  console.log("🔄 PR Review Automation Decision:\n");
  console.log(`Action: ${action}`);
  console.log(`Reason: ${reason}`);
  console.log(`Overall Score: ${review.overallScore}/100\n`);

  if (action === "REQUEST_CHANGES") {
    console.log("❌ Changes Requested:\n");
    review.securityIssues
      .filter((i) => i.severity === "critical")
      .forEach((issue) => {
        console.log(`- [CRITICAL] ${issue.type}: ${issue.description}`);
        console.log(`  Fix: ${issue.remediation}`);
      });
  } else if (action === "COMMENT") {
    console.log("💬 Review Comments:\n");
    review.comments.slice(0, 3).forEach((comment) => {
      console.log(`Line ${comment.line}: ${comment.title}`);
      console.log(`  ${comment.body.substring(0, 100)}...`);
    });
  } else {
    console.log("✅ Approved!\n");
    console.log(`Code quality is excellent (${review.overallScore}/100)`);
  }
}

// ============================================================================
// MAIN: Run All Examples
// ============================================================================

async function main() {
  console.log("═══════════════════════════════════════════════════════════");
  console.log("Code Reviewer Service — Usage Examples");
  console.log("═══════════════════════════════════════════════════════════");

  try {
    // Note: These examples require ANTHROPIC_API_KEY to be set
    if (!process.env.ANTHROPIC_API_KEY) {
      console.error("\n❌ ANTHROPIC_API_KEY environment variable not set");
      console.error("Set it before running: export ANTHROPIC_API_KEY=sk_...");
      process.exit(1);
    }

    // Run examples sequentially to avoid rate limiting
    await example1_QuickSecurityScan();
    await example2_PerformanceAnalysis();
    await example3_RefactoringSuggestions();
    await example4_CompleteCodeReviewFast();
    await example5_DeepCodeReviewOpus();
    await example6_PRReviewAutomation();

    console.log(
      "\n═══════════════════════════════════════════════════════════"
    );
    console.log("✅ All examples completed successfully!");
    console.log(
      "═══════════════════════════════════════════════════════════\n"
    );
  } catch (error) {
    console.error("\n❌ Error running examples:");
    console.error(error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export {
  example1_QuickSecurityScan,
  example2_PerformanceAnalysis,
  example3_RefactoringSuggestions,
  example4_CompleteCodeReviewFast,
  example5_DeepCodeReviewOpus,
  example6_PRReviewAutomation,
};
