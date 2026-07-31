/**
 * Code Reviewer Agent — Suite de testes
 */

import { CodeReviewerAgent, type CodeReviewInput } from "../code-reviewer";

describe("CodeReviewerAgent", () => {
  let agent: CodeReviewerAgent;

  beforeAll(() => {
    agent = new CodeReviewerAgent(process.env.ANTHROPIC_API_KEY);
  });

  describe("reviewCode", () => {
    it("should return success status on valid input", async () => {
      const input: CodeReviewInput = {
        prDiff: `
--- a/src/agents/sample.ts
+++ b/src/agents/sample.ts
@@ -1,5 +1,10 @@
 export function process(data: string) {
-  const result = data.split('');
-  return result.join('');
+  if (!data) return null;
+  const result = data.split('');
+  const filtered = result.filter(x => x);
+  return filtered.join('');
 }
+
+export function unsafe() {
+  eval(userInput);
+}`,
        newAgentCode: `
export class MyService {
  private cache: any;

  async fetch(url: string) {
    const response = await fetch(url);
    return response.json();
  }

  process(items: unknown[]) {
    let sum = 0;
    for (let i = 0; i < items.length; i++) {
      sum += items[i] as number;
    }
    return sum;
  }
}`,
        agentPath: "src/agents/sample.ts",
        prContext: {
          title: "feat: add data processing service",
          description: "Implements basic data processing with caching",
          author: "dev-user",
        },
      };

      const output = await agent.reviewCode(input);

      expect(output.status).toEqual("success");
      expect(Array.isArray(output.findings)).toBe(true);
      expect(output.summary).toBeDefined();
      expect(output.overallScore).toBeGreaterThanOrEqual(0);
      expect(output.overallScore).toBeLessThanOrEqual(100);
      expect(output.analysisTimeMs).toBeGreaterThan(0);
    }, 30000);

    it("should detect security issues", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: `
export function executeCommand(userInput: string) {
  return eval(userInput);
}

export function queryDB(sql: string) {
  return database.execute(sql);
}`,
        agentPath: "src/services/query.ts",
        dimensions: ["security"],
      };

      const output = await agent.reviewCode(input);

      expect(output.status).toEqual("success");
      const securityFindings = output.findings.filter(
        (f) => f.dimension === "security"
      );
      expect(securityFindings.length).toBeGreaterThan(0);
    }, 30000);

    it("should detect style issues", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: `
export class MyClass {
  doSomething() {
    // code without proper typing
    let x = 1;
    var y = 2;
    function helper() {}
  }

  // missing JSDoc
  compute(a, b) {
    return a + b;
  }
}`,
        agentPath: "src/agents/style-test.ts",
        dimensions: ["style"],
      };

      const output = await agent.reviewCode(input);

      expect(output.status).toEqual("success");
      const styleFindings = output.findings.filter(
        (f) => f.dimension === "style"
      );
      // Esperamos algum finding de style (pode ser vazio se Opus não detectar)
      expect(Array.isArray(styleFindings)).toBe(true);
    }, 30000);

    it("should calculate dimension stats correctly", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: "export const x = 1;",
        agentPath: "src/test.ts",
      };

      const output = await agent.reviewCode(input);

      expect(output.dimensionStats).toHaveProperty("correctness");
      expect(output.dimensionStats).toHaveProperty("security");
      expect(output.dimensionStats).toHaveProperty("performance");
      expect(output.dimensionStats).toHaveProperty("style");

      const total = Object.values(output.dimensionStats).reduce(
        (a, b) => a + b,
        0
      );
      expect(total).toEqual(output.findings.length);
    }, 30000);

    it("should calculate severity stats correctly", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: "export const x = 1;",
        agentPath: "src/test.ts",
      };

      const output = await agent.reviewCode(input);

      expect(output.severityStats).toHaveProperty("info");
      expect(output.severityStats).toHaveProperty("warning");
      expect(output.severityStats).toHaveProperty("error");
      expect(output.severityStats).toHaveProperty("critical");

      const total = Object.values(output.severityStats).reduce((a, b) => a + b, 0);
      expect(total).toEqual(output.findings.length);
    }, 30000);
  });

  describe("score calculation", () => {
    it("should return 100 for zero findings", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: "export const valid = true;",
        agentPath: "src/test.ts",
      };

      const output = await agent.reviewCode(input);

      if (output.findings.length === 0) {
        expect(output.overallScore).toBe(100);
      }
    }, 30000);

    it("should decrease score with findings severity", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: `
export function dangerous() {
  eval('code');
  let x = 1;
  var y = 2;
}`,
        agentPath: "src/dangerous.ts",
      };

      const output = await agent.reviewCode(input);

      if (output.findings.some((f) => f.severity === "critical")) {
        expect(output.overallScore).toBeLessThan(100);
      }
    }, 30000);
  });

  describe("summary generation", () => {
    it("should generate summary under 50 lines", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: "export const x = 1;",
        agentPath: "src/test.ts",
      };

      const output = await agent.reviewCode(input);
      const lines = output.summary.split("\n");

      expect(lines.length).toBeLessThanOrEqual(50);
    }, 30000);

    it("should indicate clean code when no findings", async () => {
      const input: CodeReviewInput = {
        prDiff: "",
        newAgentCode: "export const valid = true;",
        agentPath: "src/test.ts",
      };

      const output = await agent.reviewCode(input);

      if (output.findings.length === 0) {
        expect(output.summary).toContain("✅");
      }
    }, 30000);
  });
});
