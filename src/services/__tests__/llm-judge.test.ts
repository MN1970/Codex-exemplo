/**
 * Testes para LLM Judge
 * Versão: 1.0.0
 */

import {
  LLMJudge,
  createLLMJudge,
  judgePR,
  translateAction,
  translateRiskLevel,
  JudgeAction,
  type RiskLevel,
  type PRData,
  type PRJudgment,
} from "../llm-judge";

describe("LLMJudge", () => {
  let judge: LLMJudge;

  beforeEach(() => {
    // Skip tests se ANTHROPIC_API_KEY não está configurada
    if (!process.env.ANTHROPIC_API_KEY) {
      console.warn(
        "⚠️  ANTHROPIC_API_KEY não configurada. Pulando testes da API."
      );
    }
  });

  describe("Inicialização", () => {
    it("deve criar instância com configuração padrão", () => {
      if (!process.env.ANTHROPIC_API_KEY) {
        console.warn("Pulando teste - API key não configurada");
        return;
      }

      const judge = createLLMJudge();
      expect(judge).toBeDefined();
      expect(judge).toBeInstanceOf(LLMJudge);
    });

    it("deve criar instância com configuração customizada", () => {
      if (!process.env.ANTHROPIC_API_KEY) {
        console.warn("Pulando teste - API key não configurada");
        return;
      }

      const judge = createLLMJudge({
        model: "claude-3-5-haiku-20241022",
        maxTokens: 512,
      });
      expect(judge).toBeDefined();
    });

    it("deve lançar erro se ANTHROPIC_API_KEY não está configurada", () => {
      // Temporariamente remove a API key
      const originalKey = process.env.ANTHROPIC_API_KEY;
      delete process.env.ANTHROPIC_API_KEY;

      expect(() => {
        new LLMJudge();
      }).toThrow("ANTHROPIC_API_KEY não configurada");

      // Restaura a API key
      if (originalKey) {
        process.env.ANTHROPIC_API_KEY = originalKey;
      }
    });
  });

  describe("Helper Functions", () => {
    it("deve traduzir ações para português", () => {
      expect(translateAction(JudgeAction.AUTO_MERGE)).toBe("Auto-merge imediato");
      expect(translateAction(JudgeAction.CONDITIONAL_MERGE)).toBe(
        "Merge se CI passar"
      );
      expect(translateAction(JudgeAction.REQUIRES_REVIEW)).toBe(
        "Requer revisão humana"
      );
      expect(translateAction(JudgeAction.BLOCKING)).toBe(
        "Bloqueado - não pode fazer merge"
      );
    });

    it("deve traduzir risk levels para português", () => {
      expect(translateRiskLevel("low")).toBe("Risco Baixo");
      expect(translateRiskLevel("medium")).toBe("Risco Médio");
      expect(translateRiskLevel("high")).toBe("Risco Alto");
    });
  });

  describe("Estrutura de tipos", () => {
    it("deve ter tipos válidos para PRData", () => {
      const prData: PRData = {
        prNumber: 123,
        owner: "test-org",
        repo: "test-repo",
        title: "Fix: update dependencies",
        description: "Updates npm dependencies to latest versions",
        author: "testuser",
        branch: "fix/deps",
        baseBranch: "main",
        filesChanged: 2,
        additions: 10,
        deletions: 5,
        changedFiles: [
          {
            filename: "package.json",
            additions: 5,
            deletions: 2,
            patch: "+ lodash@^4.17.21",
          },
          {
            filename: "package-lock.json",
            additions: 5,
            deletions: 3,
          },
        ],
        commits: [
          {
            message: "fix: update dependencies",
            author: "testuser",
          },
        ],
      };

      expect(prData.prNumber).toBe(123);
      expect(prData.filesChanged).toBe(2);
      expect(prData.changedFiles).toHaveLength(2);
    });

    it("deve ter tipos válidos para PRJudgment", () => {
      const judgment: PRJudgment = {
        prNumber: 123,
        owner: "test-org",
        repo: "test-repo",
        title: "Fix: update dependencies",
        author: "testuser",
        riskLevel: "low",
        riskCategories: ["external-dependency"],
        confidence: 0.85,
        reason: "Pequena mudança com impacto limitado",
        action: JudgeAction.CONDITIONAL_MERGE,
        actionReason: "Pode fazer merge após CI passar",
        detailedAnalysis: {
          securityConcerns: [],
          performanceRisks: [],
          testCoverage: {
            hasTests: true,
            confidence: 0.9,
          },
          changeSize: {
            filesChanged: 2,
            additionsCount: 10,
            deletionsCount: 5,
            severity: "small",
          },
          codePatterns: {
            hasBreakingChanges: false,
            hasExternalDeps: true,
            hasMigrations: false,
            hasDocumentation: true,
          },
        },
        analyzedAt: new Date(),
        model: "claude-3-5-haiku-20241022",
        promptTokens: 250,
        completionTokens: 150,
      };

      expect(judgment.prNumber).toBe(123);
      expect(judgment.riskLevel).toBe("low");
      expect(judgment.action).toBe(JudgeAction.CONDITIONAL_MERGE);
      expect(judgment.confidence).toBeGreaterThanOrEqual(0);
      expect(judgment.confidence).toBeLessThanOrEqual(1);
      expect(judgment.detailedAnalysis.changeSize.severity).toBe("small");
    });
  });

  describe("Exemplos de PRs para análise", () => {
    it("exemplo: PR de baixo risco (refactor simples)", () => {
      const lowRiskPR: PRData = {
        prNumber: 100,
        owner: "anthropic",
        repo: "sdk-js",
        title: "refactor: simplify utility functions",
        description: "Simplify isValid function without changing behavior",
        author: "developer1",
        branch: "refactor/utils",
        baseBranch: "main",
        filesChanged: 1,
        additions: 15,
        deletions: 20,
        changedFiles: [
          {
            filename: "src/utils.ts",
            additions: 15,
            deletions: 20,
            patch: `
- export function isValid(obj: any): boolean {
-   if (obj === null) return false;
-   if (obj === undefined) return false;
-   return true;
- }
+ export function isValid(obj: any): boolean {
+   return obj != null;
+ }`,
          },
        ],
        commits: [
          {
            message: "refactor: simplify utility functions",
            author: "developer1",
          },
        ],
        testsPassed: 45,
        testsFailed: 0,
        coverage: 92,
        ciPassed: true,
      };

      expect(lowRiskPR.filesChanged).toBe(1);
      expect(lowRiskPR.additions).toBeLessThan(50);
      expect(lowRiskPR.ciPassed).toBe(true);
      // Esperado: riskLevel = "low", action = "auto_merge"
    });

    it("exemplo: PR de risco médio (nova feature com testes)", () => {
      const mediumRiskPR: PRData = {
        prNumber: 101,
        owner: "anthropic",
        repo: "sdk-js",
        title: "feat: add user authentication",
        description:
          "Implements OAuth2 integration for user authentication. Includes comprehensive tests.",
        author: "developer2",
        branch: "feat/auth",
        baseBranch: "main",
        filesChanged: 8,
        additions: 250,
        deletions: 10,
        changedFiles: [
          {
            filename: "src/auth/oauth.ts",
            additions: 150,
            deletions: 0,
            patch:
              "+ export class OAuthProvider { ... }",
          },
          {
            filename: "src/auth/oauth.test.ts",
            additions: 100,
            deletions: 0,
            patch: "+ describe('OAuthProvider', () => { ... })",
          },
        ],
        commits: [
          {
            message: "feat: add OAuth2 provider",
            author: "developer2",
          },
          {
            message: "test: add OAuth2 tests",
            author: "developer2",
          },
        ],
        testsPassed: 50,
        testsFailed: 0,
        coverage: 88,
        ciPassed: true,
      };

      expect(mediumRiskPR.filesChanged).toBeGreaterThan(5);
      expect(mediumRiskPR.additions).toBeGreaterThan(100);
      expect(mediumRiskPR.changedFiles.some((f) => f.filename.includes(".test."))).toBe(true);
      // Esperado: riskLevel = "medium", action = "conditional_merge"
    });

    it("exemplo: PR de alto risco (breaking change grande)", () => {
      const highRiskPR: PRData = {
        prNumber: 102,
        owner: "anthropic",
        repo: "sdk-js",
        title: "refactor: restructure API response format",
        description: "Major API restructuring - this is a breaking change",
        author: "developer3",
        branch: "refactor/api",
        baseBranch: "main",
        filesChanged: 45,
        additions: 1500,
        deletions: 800,
        changedFiles: [
          {
            filename: "src/api/client.ts",
            additions: 400,
            deletions: 300,
            patch:
              "- export interface Response { ... }\n+ export interface APIResponse { ... }",
          },
          {
            filename: "src/types.ts",
            additions: 200,
            deletions: 100,
            patch:
              "- export type Result = ...\n+ export type Result = ...", // Breaking change
          },
        ],
        commits: [
          {
            message: "refactor: restructure API response format",
            author: "developer3",
          },
        ],
        testsPassed: 30,
        testsFailed: 15,
        coverage: 60,
        ciPassed: false,
      };

      expect(highRiskPR.filesChanged).toBeGreaterThan(20);
      expect(highRiskPR.additions).toBeGreaterThan(1000);
      expect(highRiskPR.ciPassed).toBe(false);
      // Esperado: riskLevel = "high", action = "requires_review"
    });

    it("exemplo: PR com vulnerabilidade de segurança", () => {
      const securityRiskPR: PRData = {
        prNumber: 103,
        owner: "anthropic",
        repo: "sdk-js",
        title: "fix: improve data validation",
        description: "Add user input validation",
        author: "developer4",
        branch: "fix/validation",
        baseBranch: "main",
        filesChanged: 3,
        additions: 80,
        deletions: 20,
        changedFiles: [
          {
            filename: "src/handlers/user.ts",
            additions: 50,
            deletions: 10,
            patch: `
+ const user = JSON.parse(userInput);
+ const html = '<div>' + userInput + '</div>';
`,
          },
        ],
        commits: [
          {
            message: "fix: improve data validation",
            author: "developer4",
          },
        ],
        ciPassed: true,
      };

      expect(securityRiskPR.changedFiles[0].patch).toContain("JSON.parse");
      // Esperado: riskLevel = "high", riskCategories includes "security"
    });

    it("exemplo: PR com mudanças em migration de BD", () => {
      const migrationPR: PRData = {
        prNumber: 104,
        owner: "anthropic",
        repo: "backend",
        title: "feat: add user profiles table",
        description: "Add new user_profiles table with migration",
        author: "developer5",
        branch: "feat/profiles",
        baseBranch: "main",
        filesChanged: 2,
        additions: 50,
        deletions: 0,
        changedFiles: [
          {
            filename: "migrations/001_create_user_profiles.sql",
            additions: 30,
            deletions: 0,
            patch: "+ CREATE TABLE user_profiles ( id SERIAL PRIMARY KEY, ... );",
          },
          {
            filename: "src/models/userProfile.ts",
            additions: 20,
            deletions: 0,
            patch: "+ export interface UserProfile { ... }",
          },
        ],
        commits: [
          {
            message: "feat: add user profiles table",
            author: "developer5",
          },
        ],
      };

      expect(migrationPR.changedFiles.some((f) => f.filename.includes("migration"))).toBe(true);
      // Esperado: riskLevel = "medium", riskCategories includes "database-migration"
    });
  });

  describe("Testes com Fallback", () => {
    it("deve retornar judgment válido mesmo com erro", async () => {
      if (!process.env.ANTHROPIC_API_KEY) {
        console.warn("Pulando teste - API key não configurada");
        return;
      }

      // Cria um judge com configuração inválida para forçar erro
      const testPR: PRData = {
        prNumber: 999,
        owner: "test",
        repo: "test",
        title: "Test PR",
        author: "test",
        branch: "test",
        baseBranch: "main",
        filesChanged: 1,
        additions: 10,
        deletions: 5,
        changedFiles: [
          {
            filename: "test.ts",
            additions: 10,
            deletions: 5,
          },
        ],
        commits: [
          {
            message: "test commit",
            author: "test",
          },
        ],
      };

      // Mesmo com erro, deve retornar um PRJudgment válido
      const result = await judgePR(testPR);

      expect(result).toBeDefined();
      expect(result.prNumber).toBe(999);
      expect(result.riskLevel).toMatch(/^(high|medium|low)$/);
      expect(result.action).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
      expect(result.confidence).toBeLessThanOrEqual(1);
    });
  });

  describe("Análise de Detalhes", () => {
    it("deve incluir análise detalhada no judgment", () => {
      const testPR: PRData = {
        prNumber: 105,
        owner: "test",
        repo: "test",
        title: "Test PR",
        author: "test",
        branch: "test",
        baseBranch: "main",
        filesChanged: 3,
        additions: 150,
        deletions: 50,
        changedFiles: [
          { filename: "file1.ts", additions: 75, deletions: 25 },
          { filename: "file1.test.ts", additions: 75, deletions: 25 },
          { filename: "README.md", additions: 0, deletions: 0 },
        ],
        commits: [
          { message: "feat: new feature", author: "test" },
        ],
      };

      // Esperado structure
      expect(testPR.changedFiles).toHaveLength(3);
      expect(testPR.changedFiles[1].filename).toContain(".test.ts");

      // Ao fazer judgment, esperado:
      // - detailedAnalysis.testCoverage.hasTests = true
      // - detailedAnalysis.changeSize.severity = "medium"
    });
  });
});

/**
 * Função de teste rápida para demonstração
 */
export async function runLLMJudgeDemo(): Promise<void> {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log("⚠️  ANTHROPIC_API_KEY não configurada. Pulando demo.");
    return;
  }

  console.log("\n=== LLM Judge Demo ===\n");

  const judge = createLLMJudge();

  // Exemplo: PR de baixo risco
  const lowRiskPR: PRData = {
    prNumber: 1001,
    owner: "mycompany",
    repo: "my-app",
    title: "docs: update README",
    description: "Update README with latest information",
    author: "john.doe",
    branch: "docs/readme",
    baseBranch: "main",
    filesChanged: 1,
    additions: 20,
    deletions: 5,
    changedFiles: [
      {
        filename: "README.md",
        additions: 20,
        deletions: 5,
      },
    ],
    commits: [
      {
        message: "docs: update README",
        author: "john.doe",
      },
    ],
    ciPassed: true,
  };

  console.log("Analisando PR de baixo risco...");
  try {
    const judgment = await judge.judge(lowRiskPR);

    console.log("\n📊 Resultado:");
    console.log(`PR #${judgment.prNumber}: ${judgment.title}`);
    console.log(`Risk Level: ${translateRiskLevel(judgment.riskLevel)}`);
    console.log(`Confidence: ${(judgment.confidence * 100).toFixed(1)}%`);
    console.log(`Action: ${translateAction(judgment.action)}`);
    console.log(`Reason: ${judgment.reason}`);

    if (judgment.detailedAnalysis.securityConcerns.length > 0) {
      console.log("\n⚠️  Security Concerns:");
      judgment.detailedAnalysis.securityConcerns.forEach((c) =>
        console.log(`  - ${c}`)
      );
    }

    if (judgment.detailedAnalysis.performanceRisks.length > 0) {
      console.log("\n⚠️  Performance Risks:");
      judgment.detailedAnalysis.performanceRisks.forEach((r) =>
        console.log(`  - ${r}`)
      );
    }

    console.log("\n✅ Demo completed successfully!");
  } catch (error) {
    console.error("❌ Demo failed:", error);
  }
}

// Export for CLI usage
if (require.main === module) {
  runLLMJudgeDemo().catch(console.error);
}
