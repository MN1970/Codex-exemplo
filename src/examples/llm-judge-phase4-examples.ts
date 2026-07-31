/**
 * LLM Judge Phase 4 - Decision Engine Examples
 *
 * Demonstrates all new Phase 4 methods:
 * - evaluateCode: Detailed code evaluation
 * - decideMergeability: Intelligent merge decisions
 * - scoreQuality: Comprehensive quality scoring
 * - explainDecision: Natural language explanations
 */

import {
  createLLMJudge,
  translateMergeDecision,
  translateConfidenceLevel,
  translateIssueSeverity,
  type PRData,
  type CodeReview,
} from "../services/llm-judge";

/**
 * Example 1: Evaluate code with reviews
 */
async function example1_EvaluateCode() {
  console.log("\n" + "=".repeat(70));
  console.log("Example 1: Code Evaluation with Detailed Analysis");
  console.log("=".repeat(70));

  const judge = createLLMJudge();

  const code = `
// Authentication module
export class AuthService {
  private users = new Map<string, User>();

  async authenticateUser(email: string, password: string): Promise<boolean> {
    // Simple lookup - NO INPUT VALIDATION!
    const user = this.users.get(email);
    if (!user) return false;

    // Direct password comparison - SECURITY ISSUE
    return user.password === password;
  }

  async registerUser(email: string, password: string): Promise<void> {
    // Duplicate email check missing
    this.users.set(email, { email, password });
  }

  getUserList(): User[] {
    // Returns all users including passwords - PRIVACY ISSUE
    return Array.from(this.users.values());
  }
}

interface User {
  email: string;
  password: string;
}`;

  const reviews: CodeReview[] = [
    {
      reviewer: "alice.johnson",
      content: "This code has several security issues. Passwords should be hashed, not stored in plain text.",
      timestamp: new Date(),
      severity: "critical",
    },
    {
      reviewer: "bob.smith",
      content: "Missing input validation on email and password parameters.",
      timestamp: new Date(),
      severity: "major",
    },
  ];

  console.log("\n📝 Analyzing code...\n");
  const evaluation = await judge.evaluateCode(code, reviews);

  console.log(`Overall Score: ${evaluation.overallScore}/100`);
  console.log(`Critical Issues: ${evaluation.criticalIssues.length}`);
  console.log(`Minor Issues: ${evaluation.minorIssues.length}`);
  console.log(`\nTestability: ${evaluation.testability.score}/100`);
  console.log(`Maintainability: ${evaluation.maintainability.score}/100`);
  console.log(`Documentation: ${evaluation.documentation.score}/100`);

  if (evaluation.securityRisks.length > 0) {
    console.log(`\n🔒 Security Risks:`);
    evaluation.securityRisks.forEach((risk) => {
      console.log(`  - [${translateIssueSeverity(risk.severity)}] ${risk.type}: ${risk.description}`);
    });
  }

  console.log(`\n📋 Audit Trail (${evaluation.auditTrail.length} entries):`);
  evaluation.auditTrail.forEach((entry) => {
    console.log(`  - ${entry.action} @ ${entry.timestamp.toISOString()}`);
  });

  return evaluation;
}

/**
 * Example 2: Decide mergeability with confidence levels
 */
async function example2_DecideMergeability() {
  console.log("\n" + "=".repeat(70));
  console.log("Example 2: Merge Decision with Confidence Levels");
  console.log("=".repeat(70));

  const judge = createLLMJudge();

  const prData: PRData = {
    prNumber: 505,
    owner: "acmecorp",
    repo: "platform",
    title: "refactor: migrate from MongoDB to PostgreSQL",
    description: `
This PR migrates the entire database layer from MongoDB to PostgreSQL.

Key changes:
- New Postgres schema
- Updated ORM models
- Database migration scripts
- Updated queries

Testing: Full integration tests pass. Performance benchmarks included.`,
    author: "carol.white",
    branch: "feat/postgres-migration",
    baseBranch: "main",
    filesChanged: 45,
    additions: 3200,
    deletions: 2800,
    changedFiles: [
      {
        filename: "src/db/schema.ts",
        additions: 400,
        deletions: 0,
      },
      {
        filename: "src/db/migrations/001_initial.ts",
        additions: 200,
        deletions: 0,
      },
      {
        filename: "src/models/User.ts",
        additions: 150,
        deletions: 100,
      },
      {
        filename: "src/db/queries.test.ts",
        additions: 300,
        deletions: 200,
      },
    ],
    commits: [
      {
        message: "feat: add PostgreSQL schema and migrations",
        author: "carol.white",
      },
      {
        message: "refactor: update models for PostgreSQL",
        author: "carol.white",
      },
      {
        message: "test: comprehensive database tests",
        author: "carol.white",
      },
    ],
    ciPassed: true,
    testsPassed: 150,
    testsFailed: 0,
    coverage: 92,
  };

  console.log("\n🔍 Analyzing mergeability...\n");
  const decision = await judge.decideMergeability(prData);

  console.log(`Decision: ${translateMergeDecision(decision.decision).toUpperCase()}`);
  console.log(`Confidence: ${translateConfidenceLevel(decision.confidenceLevel)}`);
  console.log(`Score: ${(decision.confidence * 100).toFixed(1)}%`);
  console.log(`\nReasoning: ${decision.reasoning}`);

  if (decision.reasons.length > 0) {
    console.log(`\nReasons:`);
    decision.reasons.forEach((reason) => {
      console.log(`  • ${reason}`);
    });
  }

  if (decision.blockers && decision.blockers.length > 0) {
    console.log(`\n🛑 Blockers:`);
    decision.blockers.forEach((blocker) => {
      console.log(`  • ${blocker}`);
    });
  }

  if (decision.warnings && decision.warnings.length > 0) {
    console.log(`\n⚠️ Warnings:`);
    decision.warnings.forEach((warning) => {
      console.log(`  • ${warning}`);
    });
  }

  if (decision.suggestions && decision.suggestions.length > 0) {
    console.log(`\n💡 Suggestions:`);
    decision.suggestions.forEach((suggestion) => {
      console.log(`  • ${suggestion}`);
    });
  }

  console.log(`\n📋 Audit Trail (${decision.auditTrail.length} entries):`);
  decision.auditTrail.forEach((entry) => {
    console.log(`  - ${entry.action} @ ${entry.timestamp.toISOString()}`);
  });

  return decision;
}

/**
 * Example 3: Score code quality comprehensively
 */
async function example3_ScoreQuality() {
  console.log("\n" + "=".repeat(70));
  console.log("Example 3: Comprehensive Quality Scoring");
  console.log("=".repeat(70));

  const judge = createLLMJudge();

  const code = `
import { Injectable } from '@nestjs/common';
import { UserRepository } from './user.repository';
import * as bcrypt from 'bcrypt';
import { ValidationError } from 'class-validator';

/**
 * User Service
 *
 * Manages user authentication and profile operations.
 * Includes password hashing, validation, and error handling.
 */
@Injectable()
export class UserService {
  constructor(private userRepository: UserRepository) {}

  /**
   * Register a new user
   * @param email - User email (validated)
   * @param password - User password (will be hashed)
   * @returns Created user object (without password)
   */
  async register(email: string, password: string) {
    // Validate email format
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new ValidationError({ email: 'Invalid email format' });
    }

    // Check if user exists
    const existing = await this.userRepository.findByEmail(email);
    if (existing) {
      throw new Error('User already exists');
    }

    // Hash password with salt rounds
    const hashedPassword = await bcrypt.hash(password, 10);

    // Save user
    const user = await this.userRepository.create({
      email,
      password: hashedPassword,
    });

    // Return user without password
    const { password: _, ...safeUser } = user;
    return safeUser;
  }

  /**
   * Authenticate user
   * @param email - User email
   * @param password - Plain text password
   * @returns Authenticated user or null
   */
  async authenticate(email: string, password: string) {
    const user = await this.userRepository.findByEmail(email);
    if (!user) {
      return null;
    }

    const passwordMatch = await bcrypt.compare(password, user.password);
    if (!passwordMatch) {
      return null;
    }

    const { password: _, ...safeUser } = user;
    return safeUser;
  }
}
`;

  console.log("\n📊 Calculating quality scores...\n");
  const qualityScore = await judge.scoreQuality(code);

  console.log(`Overall Grade: ${qualityScore.grade}`);
  console.log(`Overall Score: ${qualityScore.overall}/100`);
  console.log(`\nBreakdown:`);
  console.log(`  Code Quality:     ${qualityScore.codeQuality}/100`);
  console.log(`  Test Coverage:    ${qualityScore.testCoverage}/100`);
  console.log(`  Documentation:    ${qualityScore.documentation}/100`);
  console.log(`  Security:         ${qualityScore.security}/100`);
  console.log(`  Performance:      ${qualityScore.performance}/100`);
  console.log(`  Maintainability:  ${qualityScore.maintainability}/100`);

  if (qualityScore.breakdown.strengths.length > 0) {
    console.log(`\n✅ Strengths:`);
    qualityScore.breakdown.strengths.forEach((strength) => {
      console.log(`  • ${strength}`);
    });
  }

  if (qualityScore.breakdown.weaknesses.length > 0) {
    console.log(`\n⚠️ Weaknesses:`);
    qualityScore.breakdown.weaknesses.forEach((weakness) => {
      console.log(`  • ${weakness}`);
    });
  }

  if (qualityScore.breakdown.recommendations.length > 0) {
    console.log(`\n💡 Recommendations:`);
    qualityScore.breakdown.recommendations.forEach((rec) => {
      console.log(`  • ${rec}`);
    });
  }

  console.log(`\n📋 Audit Trail (${qualityScore.auditTrail.length} entries):`);
  qualityScore.auditTrail.forEach((entry) => {
    console.log(`  - ${entry.action} @ ${entry.timestamp.toISOString()}`);
  });

  return qualityScore;
}

/**
 * Example 4: Explain decisions in natural language
 */
async function example4_ExplainDecision() {
  console.log("\n" + "=".repeat(70));
  console.log("Example 4: Natural Language Decision Explanations");
  console.log("=".repeat(70));

  const judge = createLLMJudge();

  // First, get an evaluation
  const code = `
export function calculateTotal(items: any[]) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total = total + items[i].price * items[i].quantity;
  }
  return total;
}`;

  console.log("\n📝 Evaluating code...");
  const evaluation = await judge.evaluateCode(code, []);

  console.log(`\n📚 Generating explanation...\n`);
  const explanation = await judge.explainDecision(evaluation);

  console.log("Explanation:");
  console.log("-".repeat(70));
  console.log(explanation);
  console.log("-".repeat(70));

  return explanation;
}

/**
 * Example 5: Complete workflow - from code to decision
 */
async function example5_CompleteWorkflow() {
  console.log("\n" + "=".repeat(70));
  console.log("Example 5: Complete Workflow - Code to Decision");
  console.log("=".repeat(70));

  const judge = createLLMJudge();

  // Step 1: Evaluate code quality
  console.log("\n📝 Step 1: Evaluating code quality...");
  const code = `
export class PaymentProcessor {
  process(amount: number, cardToken: string): boolean {
    // SECURITY ISSUE: Storing token in logs
    console.log(\`Processing \${amount} with token \${cardToken}\`);

    // ISSUE: No input validation
    const result = this.callPaymentGateway(amount, cardToken);

    // ISSUE: No error handling
    return result;
  }
}`;

  const evaluation = await judge.evaluateCode(code);
  console.log(`   Score: ${evaluation.overallScore}/100`);
  console.log(`   Critical Issues: ${evaluation.criticalIssues.length}`);

  // Step 2: Score quality
  console.log("\n📊 Step 2: Scoring overall quality...");
  const qualityScore = await judge.scoreQuality(code);
  console.log(`   Grade: ${qualityScore.grade}`);
  console.log(`   Overall: ${qualityScore.overall}/100`);

  // Step 3: Explain issues
  console.log("\n📚 Step 3: Generating detailed explanation...");
  const explanation = await judge.explainDecision(evaluation);
  console.log(`   Explanation generated (${explanation.length} chars)`);

  // Step 4: Decide mergeability
  console.log("\n🔍 Step 4: Deciding mergeability...");
  const prData: PRData = {
    prNumber: 506,
    owner: "company",
    repo: "api",
    title: "feat: add payment processing",
    author: "developer",
    branch: "feat/payments",
    baseBranch: "main",
    filesChanged: 2,
    additions: 50,
    deletions: 0,
    changedFiles: [
      { filename: "src/payment.ts", additions: 50, deletions: 0 },
      { filename: "src/payment.test.ts", additions: 30, deletions: 0 },
    ],
    commits: [{ message: "feat: add payment processing", author: "developer" }],
    ciPassed: true,
  };

  const decision = await judge.decideMergeability(prData);
  console.log(`   Decision: ${translateMergeDecision(decision.decision)}`);
  console.log(`   Confidence: ${(decision.confidence * 100).toFixed(1)}%`);

  // Summary
  console.log("\n" + "=".repeat(70));
  console.log("WORKFLOW SUMMARY");
  console.log("=".repeat(70));
  console.log(`Code Quality Score: ${evaluation.overallScore}/100`);
  console.log(`Quality Grade: ${qualityScore.grade}`);
  console.log(`Merge Decision: ${translateMergeDecision(decision.decision)}`);
  console.log(`Confidence Level: ${translateConfidenceLevel(decision.confidenceLevel)}`);
  console.log("=".repeat(70));
}

/**
 * Run all examples
 */
async function runAllPhase4Examples() {
  console.log("\n╔════════════════════════════════════════════════════════════════╗");
  console.log("║         LLM Judge Phase 4 - Decision Engine Examples           ║");
  console.log("╚════════════════════════════════════════════════════════════════╝");

  try {
    await example1_EvaluateCode();
    await example2_DecideMergeability();
    await example3_ScoreQuality();
    await example4_ExplainDecision();
    await example5_CompleteWorkflow();

    console.log("\n" + "=".repeat(70));
    console.log("✅ All Phase 4 examples completed successfully!");
    console.log("=".repeat(70) + "\n");
  } catch (error) {
    console.error("\n❌ Error running examples:", error);
    process.exit(1);
  }
}

// Exports
export {
  example1_EvaluateCode,
  example2_DecideMergeability,
  example3_ScoreQuality,
  example4_ExplainDecision,
  example5_CompleteWorkflow,
  runAllPhase4Examples,
};

// Run if executed directly
if (require.main === module) {
  runAllPhase4Examples().catch(console.error);
}
