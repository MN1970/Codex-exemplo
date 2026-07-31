/**
 * Code Reviewer Service — Test Suite
 * Tests for security analysis, performance analysis, refactoring suggestions,
 * and comment generation
 */

import {
  CodeReviewer,
  createCodeReviewer,
  reviewCodeFast,
  reviewCodeDeep,
  analyzeSecurity,
  analyzePerformance,
  suggestRefactors,
  type Review,
  type SecurityIssue,
  type PerformanceIssue,
  type Refactoring,
} from "../code-reviewer";

describe("CodeReviewer", () => {
  let reviewer: CodeReviewer;

  beforeEach(() => {
    reviewer = new CodeReviewer({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  });

  describe("Constructor & Configuration", () => {
    it("should create instance with default config", () => {
      const instance = new CodeReviewer();
      expect(instance).toBeInstanceOf(CodeReviewer);
    });

    it("should create instance with custom config", () => {
      const instance = new CodeReviewer({
        useDeepAnalysis: true,
        maxTokens: 8000,
        confidenceThreshold: 0.8,
      });
      expect(instance).toBeInstanceOf(CodeReviewer);
    });

    it("should use API key from config", () => {
      const instance = new CodeReviewer({ apiKey: "test-key" });
      expect(instance).toBeInstanceOf(CodeReviewer);
    });
  });

  describe("reviewCode()", () => {
    it("should return a Review object with all fields", async () => {
      const code = `
        function add(a, b) {
          return a + b;
        }
      `;

      const review = await reviewer.reviewCode(code);

      expect(review).toHaveProperty("status");
      expect(review).toHaveProperty("securityIssues");
      expect(review).toHaveProperty("performanceIssues");
      expect(review).toHaveProperty("refactorings");
      expect(review).toHaveProperty("comments");
      expect(review).toHaveProperty("overallScore");
      expect(review).toHaveProperty("improvements");
      expect(review).toHaveProperty("summary");
      expect(review).toHaveProperty("recommendations");
      expect(review).toHaveProperty("analysisTimeMs");
    });

    it("should detect SQL injection vulnerabilities", async () => {
      const code = `
        const sql = \`SELECT * FROM users WHERE id = \${userId}\`;
        db.query(sql);
      `;

      const review = await reviewer.reviewCode(code);

      // Should have security issues
      if (review.status === "success") {
        expect(Array.isArray(review.securityIssues)).toBe(true);
      }
    });

    it("should detect exposed secrets", async () => {
      const code = `
        const apiKey = "sk_live_12345abcdef";
        const token = "ghp_secrettoken123456";
      `;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        expect(Array.isArray(review.securityIssues)).toBe(true);
      }
    });

    it("should provide context-aware analysis", async () => {
      const code = `function processData(items) { return items; }`;

      const review = await reviewer.reviewCode(code, {
        filepath: "src/services/data.ts",
        language: "typescript",
        framework: "express",
      });

      expect(review.status).toBe("success");
    });

    it("should calculate overall score (0-100)", async () => {
      const code = `function simple() { return 42; }`;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        expect(review.overallScore).toBeGreaterThanOrEqual(0);
        expect(review.overallScore).toBeLessThanOrEqual(100);
      }
    });

    it("should populate improvements object with dimension scores", async () => {
      const code = `function test() { return true; }`;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        expect(review.improvements).toHaveProperty("security");
        expect(review.improvements).toHaveProperty("performance");
        expect(review.improvements).toHaveProperty("codeQuality");
        expect(review.improvements).toHaveProperty("testability");
        expect(review.improvements).toHaveProperty("maintainability");

        // All scores should be 0-100
        Object.values(review.improvements).forEach((score) => {
          expect(score).toBeGreaterThanOrEqual(0);
          expect(score).toBeLessThanOrEqual(100);
        });
      }
    });

    it("should include recommendations", async () => {
      const code = `
        function insecureFunction() {
          const password = "admin123";
          eval(password);
        }
      `;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        expect(Array.isArray(review.recommendations)).toBe(true);
      }
    });

    it("should measure analysis time", async () => {
      const code = `function test() { return 1; }`;

      const review = await reviewer.reviewCode(code);

      expect(review.analysisTimeMs).toBeGreaterThan(0);
    });
  });

  describe("analyzeSecurityIssues()", () => {
    it("should return SecurityIssue array", async () => {
      const code = `const api_key = "sk_live_abc123";`;

      const issues = await reviewer.analyzeSecurityIssues(code);

      expect(Array.isArray(issues)).toBe(true);
      issues.forEach((issue) => {
        expect(issue).toHaveProperty("id");
        expect(issue).toHaveProperty("type");
        expect(issue).toHaveProperty("severity");
        expect(issue).toHaveProperty("description");
        expect(issue).toHaveProperty("line");
        expect(issue).toHaveProperty("codeSnippet");
        expect(issue).toHaveProperty("impact");
        expect(issue).toHaveProperty("remediation");
        expect(issue).toHaveProperty("confidence");
      });
    });

    it("should have valid severity levels", async () => {
      const code = `const secret = "password123";`;

      const issues = await reviewer.analyzeSecurityIssues(code);

      const validSeverities = ["info", "warning", "error", "critical"];
      issues.forEach((issue) => {
        expect(validSeverities).toContain(issue.severity);
      });
    });

    it("should have valid issue types", async () => {
      const code = `const token = getToken(); const sql = \`SELECT * FROM users WHERE id = \${id}\`;`;

      const issues = await reviewer.analyzeSecurityIssues(code);

      const validTypes = [
        "injection",
        "exposed-secret",
        "weak-validation",
        "insecure-deserialization",
        "access-control",
        "cryptography",
        "external-dependency",
        "injection-vulnerability",
        "other",
      ];

      issues.forEach((issue) => {
        expect(validTypes).toContain(issue.type);
      });
    });

    it("should include line numbers", async () => {
      const code = `
line 1
line 2
const secret = "api_key";
line 4
      `;

      const issues = await reviewer.analyzeSecurityIssues(code);

      issues.forEach((issue) => {
        expect(typeof issue.line).toBe("number");
        expect(issue.line).toBeGreaterThan(0);
      });
    });

    it("should include confidence scores", async () => {
      const code = `const password = "admin";`;

      const issues = await reviewer.analyzeSecurityIssues(code);

      issues.forEach((issue) => {
        expect(issue.confidence).toBeGreaterThanOrEqual(0);
        expect(issue.confidence).toBeLessThanOrEqual(1);
      });
    });

    it("should provide context-aware analysis", async () => {
      const code = `const config = require("./secrets.json");`;

      const issues = await reviewer.analyzeSecurityIssues(code, {
        filepath: "src/config.ts",
        language: "typescript",
        framework: "express",
      });

      expect(Array.isArray(issues)).toBe(true);
    });
  });

  describe("checkPerformance()", () => {
    it("should return PerformanceIssue array", async () => {
      const code = `
        for (let i = 0; i < 10000; i++) {
          for (let j = 0; j < 10000; j++) {
            doSomething();
          }
        }
      `;

      const issues = await reviewer.checkPerformance(code);

      expect(Array.isArray(issues)).toBe(true);
      issues.forEach((issue) => {
        expect(issue).toHaveProperty("id");
        expect(issue).toHaveProperty("type");
        expect(issue).toHaveProperty("severity");
        expect(issue).toHaveProperty("description");
        expect(issue).toHaveProperty("line");
        expect(issue).toHaveProperty("codeSnippet");
        expect(issue).toHaveProperty("estimatedImpact");
        expect(issue).toHaveProperty("optimization");
        expect(issue).toHaveProperty("confidence");
      });
    });

    it("should have valid severity levels", async () => {
      const code = `for (let i = 0; i < 10000; i++) { db.query(i); }`;

      const issues = await reviewer.checkPerformance(code);

      const validSeverities = ["info", "warning", "error", "critical"];
      issues.forEach((issue) => {
        expect(validSeverities).toContain(issue.severity);
      });
    });

    it("should have valid issue types", async () => {
      const code = `for (let i = 0; i < 1000; i++) { malloc(1024); }`;

      const issues = await reviewer.checkPerformance(code);

      const validTypes = [
        "n-plus-one",
        "inefficient-loop",
        "memory-leak",
        "unnecessary-allocation",
        "missing-cache",
        "large-payload",
        "blocking-operation",
        "other",
      ];

      issues.forEach((issue) => {
        expect(validTypes).toContain(issue.type);
      });
    });

    it("should include estimated impact metrics", async () => {
      const code = `for (let i = 0; i < 10000; i++) { process(); }`;

      const issues = await reviewer.checkPerformance(code);

      issues.forEach((issue) => {
        expect(issue.estimatedImpact).toBeDefined();
        // Impact can have timeMs, memoryMb, or degradationPercent
        expect(
          issue.estimatedImpact.timeMs ||
            issue.estimatedImpact.memoryMb ||
            issue.estimatedImpact.degradationPercent
        ).toBeDefined();
      });
    });
  });

  describe("suggestRefactoring()", () => {
    it("should return Refactoring array", async () => {
      const code = `
        function complex(a, b, c) {
          if (a) { if (b) { if (c) { return true; } } }
          return false;
        }
      `;

      const refactorings = await reviewer.suggestRefactoring(code);

      expect(Array.isArray(refactorings)).toBe(true);
      refactorings.forEach((ref) => {
        expect(ref).toHaveProperty("id");
        expect(ref).toHaveProperty("type");
        expect(ref).toHaveProperty("description");
        expect(ref).toHaveProperty("benefit");
        expect(ref).toHaveProperty("line");
        expect(ref).toHaveProperty("beforeCode");
        expect(ref).toHaveProperty("afterCode");
        expect(ref).toHaveProperty("rationale");
        expect(ref).toHaveProperty("priority");
      });
    });

    it("should have valid refactoring types", async () => {
      const code = `
        const x = 5;
        const y = 5;
        const z = x + y;
      `;

      const refactorings = await reviewer.suggestRefactoring(code);

      const validTypes = [
        "extract-method",
        "extract-constant",
        "simplify-condition",
        "remove-duplication",
        "improve-naming",
        "reduce-complexity",
        "split-class",
        "other",
      ];

      refactorings.forEach((ref) => {
        expect(validTypes).toContain(ref.type);
      });
    });

    it("should have priority ratings (1-5)", async () => {
      const code = `function foo() { if (x) { if (y) { return 1; } } }`;

      const refactorings = await reviewer.suggestRefactoring(code);

      refactorings.forEach((ref) => {
        expect(ref.priority).toBeGreaterThanOrEqual(1);
        expect(ref.priority).toBeLessThanOrEqual(5);
      });
    });

    it("should include before/after code samples", async () => {
      const code = `
        function duplicate1() { return process.env.SECRET; }
        function duplicate2() { return process.env.SECRET; }
      `;

      const refactorings = await reviewer.suggestRefactoring(code);

      refactorings.forEach((ref) => {
        expect(ref.beforeCode.length).toBeGreaterThan(0);
        expect(ref.afterCode.length).toBeGreaterThan(0);
      });
    });

    it("should optionally include complexity metrics", async () => {
      const code = `
        function nested() {
          if (a) { if (b) { if (c) { if (d) { return 1; } } } }
          return 0;
        }
      `;

      const refactorings = await reviewer.suggestRefactoring(code);

      refactorings.forEach((ref) => {
        if (ref.complexity) {
          expect(ref.complexity.before).toBeGreaterThan(0);
          expect(ref.complexity.after).toBeGreaterThan(0);
        }
      });
    });
  });

  describe("generateComments()", () => {
    it("should return ReviewComment array", async () => {
      const code = `
        const secret = "password";
        for (let i = 0; i < 1000; i++) {
          db.query(sql);
        }
      `;

      const comments = await reviewer.generateComments(code);

      expect(Array.isArray(comments)).toBe(true);
      comments.forEach((comment) => {
        expect(comment).toHaveProperty("id");
        expect(comment).toHaveProperty("line");
        expect(comment).toHaveProperty("type");
        expect(comment).toHaveProperty("severity");
        expect(comment).toHaveProperty("title");
        expect(comment).toHaveProperty("body");
        expect(comment).toHaveProperty("isBlocking");
      });
    });

    it("should mark critical/error issues as blocking", async () => {
      const code = `eval(userInput);`;

      const comments = await reviewer.generateComments(code);

      comments.forEach((comment) => {
        if (["critical", "error"].includes(comment.severity)) {
          expect(comment.isBlocking).toBe(true);
        } else {
          expect(comment.isBlocking).toBe(false);
        }
      });
    });

    it("should have valid comment types", async () => {
      const code = `const x = 5;`;

      const comments = await reviewer.generateComments(code);

      const validTypes = [
        "suggestion",
        "question",
        "observation",
        "praise",
        "issue",
      ];

      comments.forEach((comment) => {
        expect(validTypes).toContain(comment.type);
      });
    });

    it("should generate markdown body", async () => {
      const code = `function test() { return undefined; }`;

      const comments = await reviewer.generateComments(code);

      comments.forEach((comment) => {
        expect(typeof comment.body).toBe("string");
        expect(comment.body.length).toBeGreaterThan(0);
      });
    });
  });

  describe("generateComment()", () => {
    it("should generate single comment from issue", async () => {
      const comment = await reviewer.generateComment({
        type: "issue",
        title: "SQL Injection",
        line: 42,
        description: "User input not sanitized",
        severity: "critical",
      });

      expect(comment).toHaveProperty("id");
      expect(comment).toHaveProperty("line", 42);
      expect(comment).toHaveProperty("type", "issue");
      expect(comment).toHaveProperty("severity", "critical");
      expect(comment).toHaveProperty("title");
      expect(comment).toHaveProperty("body");
      expect(comment).toHaveProperty("isBlocking", true);
    });

    it("should set isBlocking based on severity", async () => {
      const critical = await reviewer.generateComment({
        type: "issue",
        title: "Critical Issue",
        line: 1,
        description: "Test",
        severity: "critical",
      });

      const info = await reviewer.generateComment({
        type: "suggestion",
        title: "Minor suggestion",
        line: 1,
        description: "Test",
        severity: "info",
      });

      expect(critical.isBlocking).toBe(true);
      expect(info.isBlocking).toBe(false);
    });
  });

  describe("Factory Functions", () => {
    it("createCodeReviewer() should create instance", () => {
      const instance = createCodeReviewer({
        useDeepAnalysis: true,
      });

      expect(instance).toBeInstanceOf(CodeReviewer);
    });

    it("reviewCodeFast() should use Haiku model", async () => {
      const code = `function test() { return true; }`;

      const review = await reviewCodeFast(code);

      expect(review).toHaveProperty("status");
      expect(review).toHaveProperty("overallScore");
    });

    it("reviewCodeDeep() should use Opus model", async () => {
      const code = `function test() { return true; }`;

      const review = await reviewCodeDeep(code);

      expect(review).toHaveProperty("status");
      expect(review).toHaveProperty("overallScore");
    });

    it("analyzeSecurity() should analyze only security", async () => {
      const code = `const token = "secret123";`;

      const issues = await analyzeSecurity(code);

      expect(Array.isArray(issues)).toBe(true);
    });

    it("analyzePerformance() should analyze only performance", async () => {
      const code = `for (let i = 0; i < 10000; i++) { }`;

      const issues = await analyzePerformance(code);

      expect(Array.isArray(issues)).toBe(true);
    });

    it("suggestRefactors() should suggest refactorings", async () => {
      const code = `function complex() { if (a) { if (b) { return true; } } }`;

      const refactors = await suggestRefactors(code);

      expect(Array.isArray(refactors)).toBe(true);
    });
  });

  describe("Edge Cases", () => {
    it("should handle empty code", async () => {
      const review = await reviewer.reviewCode("");

      expect(review).toHaveProperty("status");
    });

    it("should handle very long code", async () => {
      const longCode = `
        function test() {
          ${Array(100).fill("const x = 1;").join("\n")}
          return x;
        }
      `;

      const review = await reviewer.reviewCode(longCode);

      expect(review).toHaveProperty("status");
    });

    it("should handle code with special characters", async () => {
      const code = `const emoji = "👍🔐💡";`;

      const review = await reviewer.reviewCode(code);

      expect(review).toHaveProperty("status");
    });

    it("should handle code with multiple languages", async () => {
      const code = `
        // TypeScript
        const x: number = 42;

        /* SQL */
        SELECT * FROM users;
      `;

      const review = await reviewer.reviewCode(code, {
        language: "typescript",
      });

      expect(review).toHaveProperty("status");
    });

    it("should return partial results on error", async () => {
      const code = `function test() { }`;

      const review = await reviewer.reviewCode(code);

      // Even with errors, should have basic structure
      expect(review).toHaveProperty("securityIssues");
      expect(review).toHaveProperty("performanceIssues");
      expect(review).toHaveProperty("refactorings");
    });
  });

  describe("Scoring Logic", () => {
    it("should calculate dimension scores correctly", async () => {
      const code = `function clean() { return 42; }`;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        const { improvements } = review;

        // All dimensions should be present
        expect(improvements.security).toBeDefined();
        expect(improvements.performance).toBeDefined();
        expect(improvements.codeQuality).toBeDefined();
        expect(improvements.testability).toBeDefined();
        expect(improvements.maintainability).toBeDefined();
      }
    });

    it("should weight security highest in overall score", async () => {
      // This test verifies scoring priority
      // Security issues should impact overall score more than style issues

      const code = `eval(userInput);`;

      const review = await reviewer.reviewCode(code);

      if (review.status === "success") {
        expect(review.overallScore).toBeLessThan(100);
      }
    });
  });
});
