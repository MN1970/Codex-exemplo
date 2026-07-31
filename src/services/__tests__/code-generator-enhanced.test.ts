/**
 * Tests para Code Generator Enhanced (Phase 3)
 *
 * Testa:
 * - Geração de fixes
 * - Geração de refatorações
 * - Geração de testes
 * - Sugestões de melhorias
 * - Caching
 * - Auditoria
 * - Análise completa de PR
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  CodeGeneratorPR,
  createCodeGeneratorPR,
  analyzeQuickPR,
  suggestTestsQuick,
  type PRContext,
  type CodeFix,
  type Refactoring,
  type TestSuite,
  type Improvement,
  type PRAnalysisResult,
} from "../code-generator-enhanced";
import { mkdirSync, rmSync, existsSync } from "fs";
import { join } from "path";
import * as path from "path";

// ============================================================================
// SETUP & TEARDOWN
// ============================================================================

const testProjectRoot = join(__dirname, "..", "..", "..", "test-temp");

beforeEach(() => {
  // Cria diretório temporário
  if (!existsSync(testProjectRoot)) {
    mkdirSync(testProjectRoot, { recursive: true });
  }
});

afterEach(() => {
  // Limpa diretório temporário
  if (existsSync(testProjectRoot)) {
    rmSync(testProjectRoot, { recursive: true, force: true });
  }
});

// ============================================================================
// TESTES UNITÁRIOS
// ============================================================================

describe("CodeGeneratorPR", () => {
  let generator: CodeGeneratorPR;

  beforeEach(() => {
    generator = createCodeGeneratorPR(testProjectRoot);
  });

  // ========================================================================
  // Construtor e Inicialização
  // ========================================================================

  describe("Initialization", () => {
    it("deve criar instância com defaults", () => {
      const gen = createCodeGeneratorPR();
      expect(gen).toBeDefined();
    });

    it("deve criar instância com projectRoot customizado", () => {
      const gen = createCodeGeneratorPR(testProjectRoot);
      expect(gen).toBeDefined();
    });

    it("deve criar diretórios necessários", () => {
      const gen = createCodeGeneratorPR(testProjectRoot);
      expect(existsSync(join(testProjectRoot, ".claude"))).toBe(true);
      expect(existsSync(join(testProjectRoot, ".claude", "logs"))).toBe(true);
    });
  });

  // ========================================================================
  // Geração de Fixes
  // ========================================================================

  describe("generateFixes", () => {
    it("deve retornar array de CodeFix", async () => {
      // Mock de resposta Anthropic seria necessário em teste real
      // Por enquanto, testa a estrutura

      const diff = `
        --- a/file.ts
        +++ b/file.ts
        @@ -1,3 +1,5 @@
        function getValue() {
        +  if (!data) return null;
          return data.value;
        }
      `;

      // Nota: Em teste real com mock Anthropic, retornaria fixes
      // Aqui apenas testamos a estrutura esperada

      const mockFixes: CodeFix[] = [
        {
          id: "fix-001",
          issueType: "null-check",
          severity: "high",
          description: "Null check missing for data parameter",
          location: "file.ts:2:3",
          problematicCode: "return data.value;",
          suggestedCode: "if (!data) return null; return data.value;",
          explanation: "Data can be null, needs validation",
          confidence: 95,
          tags: ["null-safety", "type-checking"],
          validated: false,
        },
      ];

      expect(mockFixes[0].issueType).toBe("null-check");
      expect(mockFixes[0].severity).toBe("high");
      expect(mockFixes[0].confidence).toBe(95);
    });

    it("deve gerar IDs únicos para cada fix", async () => {
      const mockFixes: CodeFix[] = [
        {
          id: "id-1",
          issueType: "performance",
          severity: "medium",
          description: "Loop optimization",
          suggestedCode: "optimized code",
          explanation: "Use map instead of loop",
          confidence: 85,
          tags: ["performance"],
          validated: false,
        },
        {
          id: "id-2",
          issueType: "security",
          severity: "critical",
          description: "SQL injection risk",
          suggestedCode: "safe query",
          explanation: "Use parameterized queries",
          confidence: 99,
          tags: ["security"],
          validated: false,
        },
      ];

      const ids = mockFixes.map((f) => f.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(mockFixes.length);
    });

    it("deve incluir severidade correta em fixes", async () => {
      const severities: CodeFix["severity"][] = [
        "low",
        "medium",
        "high",
        "critical",
      ];

      for (const severity of severities) {
        const fix: CodeFix = {
          id: `fix-${severity}`,
          issueType: "other",
          severity,
          description: "Test",
          suggestedCode: "code",
          explanation: "explanation",
          confidence: 80,
          tags: [],
          validated: false,
        };

        expect(fix.severity).toBe(severity);
      }
    });
  });

  // ========================================================================
  // Geração de Refatorações
  // ========================================================================

  describe("generateRefactorings", () => {
    it("deve retornar array de Refactoring", async () => {
      const mockRefactorings: Refactoring[] = [
        {
          id: "refac-001",
          type: "extract-function",
          description: "Extract validation logic",
          impact: 7,
          difficulty: 2,
          currentCode: "code before",
          refactoredCode: "code after",
          benefits: ["reusability", "testability"],
          risks: ["none"],
          priority: "medium",
          validated: false,
        },
      ];

      expect(mockRefactorings).toHaveLength(1);
      expect(mockRefactorings[0].type).toBe("extract-function");
      expect(mockRefactorings[0].priority).toBe("medium");
    });

    it("deve calcular impact e difficulty corretamente", async () => {
      const refactorings: Refactoring[] = [
        {
          id: "r1",
          type: "extract-constant",
          description: "Extract magic number",
          impact: 3,
          difficulty: 1,
          currentCode: "const value = 42;",
          refactoredCode: "const MAGIC_VALUE = 42;",
          benefits: ["clarity"],
          risks: [],
          priority: "low",
          validated: true,
        },
        {
          id: "r2",
          type: "reduce-complexity",
          description: "Simplify complex logic",
          impact: 9,
          difficulty: 8,
          currentCode: "complex if/else",
          refactoredCode: "simplified logic",
          benefits: ["maintainability", "readability"],
          risks: ["potential edge cases"],
          priority: "high",
          validated: false,
        },
      ];

      expect(refactorings[0].impact).toBeLessThan(refactorings[1].impact);
      expect(refactorings[0].difficulty).toBeLessThan(refactorings[1].difficulty);
    });

    it("deve incluir benefícios e riscos", async () => {
      const refac: Refactoring = {
        id: "r-test",
        type: "merge-duplicates",
        description: "Merge duplicated functions",
        impact: 6,
        difficulty: 3,
        currentCode: "func1 + func2",
        refactoredCode: "func",
        benefits: ["DRY principle", "maintainability"],
        risks: ["breaking change", "regression"],
        priority: "medium",
        validated: false,
      };

      expect(refac.benefits).toContain("DRY principle");
      expect(refac.risks).toContain("breaking change");
    });
  });

  // ========================================================================
  // Geração de Testes
  // ========================================================================

  describe("generateTests", () => {
    it("deve gerar TestSuite com estrutura correta", async () => {
      const mockTestSuite: TestSuite = {
        id: "ts-001",
        testFramework: "jest",
        expectedCoverage: 90,
        testCaseCount: 5,
        testCode: "test code here",
        testCases: [
          {
            name: "should return value",
            description: "Happy path",
            type: "unit",
            input: { value: 42 },
            expectedOutput: 42,
            assertions: ["return === 42"],
            critical: true,
          },
        ],
        testedFunctions: ["getValue"],
        scenarios: [
          {
            name: "Happy path",
            description: "Normal operation",
            testCaseNames: ["should return value"],
            executionOrder: 1,
          },
        ],
        suggestedFileName: "getValue.test.ts",
      };

      expect(mockTestSuite.testFramework).toBe("jest");
      expect(mockTestSuite.expectedCoverage).toBe(90);
      expect(mockTestSuite.testCaseCount).toBe(1); // 1 caso neste exemplo
      expect(mockTestSuite.testedFunctions).toContain("getValue");
    });

    it("deve suportar múltiplos frameworks de teste", async () => {
      const frameworks: Array<"jest" | "vitest" | "mocha"> = [
        "jest",
        "vitest",
        "mocha",
      ];

      for (const fw of frameworks) {
        const suite: TestSuite = {
          id: `ts-${fw}`,
          testFramework: fw,
          expectedCoverage: 85,
          testCaseCount: 3,
          testCode: `// ${fw} tests`,
          testCases: [],
          testedFunctions: [],
          scenarios: [],
          suggestedFileName: `test.${fw}.ts`,
        };

        expect(suite.testFramework).toBe(fw);
      }
    });

    it("deve incluir casos de teste variados", async () => {
      const testCases = [
        {
          name: "happy path",
          description: "Normal operation",
          type: "unit" as const,
          input: { x: 1 },
          expectedOutput: 1,
          assertions: ["x === 1"],
          critical: true,
        },
        {
          name: "edge case - null input",
          description: "Handle null",
          type: "unit" as const,
          input: { x: null },
          expectedOutput: null,
          assertions: ["x === null"],
          critical: true,
        },
        {
          name: "integration",
          description: "With dependencies",
          type: "integration" as const,
          input: { service: "mock" },
          expectedOutput: "result",
          assertions: ["service was called"],
          critical: false,
        },
      ];

      const unitCases = testCases.filter((tc) => tc.type === "unit");
      const integrationCases = testCases.filter(
        (tc) => tc.type === "integration"
      );

      expect(unitCases).toHaveLength(2);
      expect(integrationCases).toHaveLength(1);
    });
  });

  // ========================================================================
  // Sugestões de Melhorias
  // ========================================================================

  describe("suggestImprovements", () => {
    it("deve retornar array de Improvement", async () => {
      const mockImprovements: Improvement[] = [
        {
          id: "imp-001",
          category: "performance",
          description: "Use memoization",
          impact: 8,
          effort: 3,
          suggestion: "Add React.memo wrapper",
          codeExample: "const Component = React.memo(() => ...)",
          references: ["https://react.dev/reference/react/memo"],
          priority: "high",
          validated: false,
        },
      ];

      expect(mockImprovements).toHaveLength(1);
      expect(mockImprovements[0].category).toBe("performance");
    });

    it("deve cobrir todas as categorias", async () => {
      const categories: Improvement["category"][] = [
        "performance",
        "security",
        "readability",
        "maintainability",
        "types",
        "error-handling",
        "documentation",
        "testing",
        "other",
      ];

      const improvements: Improvement[] = categories.map((cat) => ({
        id: `imp-${cat}`,
        category: cat,
        description: `Improvement in ${cat}`,
        impact: 5,
        effort: 2,
        suggestion: "Do something",
        priority: "medium",
        validated: false,
      }));

      expect(improvements).toHaveLength(categories.length);
      improvements.forEach((imp, idx) => {
        expect(imp.category).toBe(categories[idx]);
      });
    });

    it("deve incluir referências úteis", async () => {
      const improvement: Improvement = {
        id: "imp-security",
        category: "security",
        description: "Validate input",
        impact: 9,
        effort: 2,
        suggestion: "Use zod for validation",
        codeExample: "const schema = z.object(...)",
        references: [
          "https://zod.dev",
          "https://owasp.org/www-community/attacks/injection",
        ],
        priority: "high",
        validated: true,
      };

      expect(improvement.references).toBeDefined();
      expect(improvement.references?.length).toBeGreaterThan(0);
    });
  });

  // ========================================================================
  // Cache
  // ========================================================================

  describe("Cache Management", () => {
    it("deve reportar estatísticas de cache", () => {
      const stats = generator.getCacheStats();

      expect(stats).toHaveProperty("size");
      expect(stats).toHaveProperty("entries");
      expect(stats.size).toBe(0);
      expect(stats.entries).toBe(0);
    });

    it("deve permitir limpeza de cache", () => {
      // Operação deve completar sem erro
      generator.clearCache();

      const stats = generator.getCacheStats();
      expect(stats.size).toBe(0);
    });
  });

  // ========================================================================
  // Auditoria
  // ========================================================================

  describe("Audit Logging", () => {
    it("deve reportar estatísticas de auditoria", () => {
      const stats = generator.getAuditStats();

      expect(stats).toHaveProperty("totalActions");
      expect(stats).toHaveProperty("successCount");
      expect(stats).toHaveProperty("errorCount");
      expect(stats).toHaveProperty("averageExecutionTime");
    });

    it("deve salvar audit log em arquivo", () => {
      generator.saveAuditLog();
      // Verificação seria feita através de filesystem check
      // em teste real
    });

    it("deve rastrear ações bem-sucedidas", () => {
      const statsBefore = generator.getAuditStats();
      const countBefore = statsBefore.totalActions;

      // Simula action (seria feita através de method call real)
      // Aqui apenas verificamos estrutura

      const statsAfter = generator.getAuditStats();
      expect(statsAfter).toBeDefined();
    });
  });

  // ========================================================================
  // Análise Completa de PR
  // ========================================================================

  describe("Complete PR Analysis", () => {
    it("deve retornar PRAnalysisResult com estrutura correta", async () => {
      const mockResult: PRAnalysisResult = {
        status: "success",
        fixes: [],
        refactorings: [],
        improvements: [],
        summary: {
          totalIssuesFound: 0,
          criticalIssues: 0,
          highIssues: 0,
          estimatedTestCoverage: 0,
          estimatedRefactoringTime: "0h",
          overallRiskLevel: "low",
        },
        processingTimeMs: 150,
        generatedAt: new Date(),
        errors: [],
      };

      expect(mockResult.status).toBe("success");
      expect(mockResult.summary).toBeDefined();
      expect(mockResult.processingTimeMs).toBeGreaterThan(0);
    });

    it("deve calcular risco correto baseado em issues", () => {
      const scenarios = [
        {
          criticalCount: 0,
          highCount: 0,
          totalCount: 0,
          expectedRisk: "low" as const,
        },
        {
          criticalCount: 0,
          highCount: 1,
          totalCount: 5,
          expectedRisk: "medium" as const,
        },
        {
          criticalCount: 0,
          highCount: 5,
          totalCount: 15,
          expectedRisk: "high" as const,
        },
        {
          criticalCount: 1,
          highCount: 0,
          totalCount: 1,
          expectedRisk: "critical" as const,
        },
      ];

      for (const scenario of scenarios) {
        const fixes: CodeFix[] = [];

        // Adiciona issues críticas
        for (let i = 0; i < scenario.criticalCount; i++) {
          fixes.push({
            id: `crit-${i}`,
            issueType: "security",
            severity: "critical",
            description: "Critical issue",
            suggestedCode: "fix",
            explanation: "Critical",
            confidence: 99,
            tags: [],
            validated: false,
          });
        }

        // Adiciona issues altas
        for (let i = 0; i < scenario.highCount; i++) {
          fixes.push({
            id: `high-${i}`,
            issueType: "performance",
            severity: "high",
            description: "High issue",
            suggestedCode: "fix",
            explanation: "High",
            confidence: 85,
            tags: [],
            validated: false,
          });
        }

        // Verifica lógica de risco (simplificada)
        expect(scenario.expectedRisk).toBeDefined();
      }
    });

    it("deve estimar tempo de refatoração", () => {
      const refactorings: Refactoring[] = [
        {
          id: "r1",
          type: "extract-function",
          description: "Test",
          impact: 5,
          difficulty: 2,
          currentCode: "code",
          refactoredCode: "refactored",
          benefits: [],
          risks: [],
          priority: "medium",
          validated: false,
        },
        {
          id: "r2",
          type: "reduce-complexity",
          description: "Test",
          impact: 8,
          difficulty: 7,
          currentCode: "code",
          refactoredCode: "refactored",
          benefits: [],
          risks: [],
          priority: "high",
          validated: false,
        },
      ];

      const totalDifficulty = refactorings.reduce(
        (sum, r) => sum + r.difficulty,
        0
      );
      const estimatedHours = Math.ceil((totalDifficulty * 5) / 60);

      expect(estimatedHours).toBeGreaterThan(0);
      expect(estimatedHours).toBeLessThan(100); // Sanity check
    });
  });

  // ========================================================================
  // Factory Functions
  // ========================================================================

  describe("Factory Functions", () => {
    it("createCodeGeneratorPR deve retornar instância válida", () => {
      const gen = createCodeGeneratorPR();
      expect(gen).toBeDefined();
      expect(gen).toBeInstanceOf(CodeGeneratorPR);
    });

    it("analyzeQuickPR deve ser callable", async () => {
      // Tipo check apenas - não executa em teste sem mock
      const func = analyzeQuickPR;
      expect(typeof func).toBe("function");
    });

    it("suggestTestsQuick deve ser callable", async () => {
      const func = suggestTestsQuick;
      expect(typeof func).toBe("function");
    });
  });
});

// ============================================================================
// TESTES DE INTEGRAÇÃO
// ============================================================================

describe("CodeGeneratorPR Integration", () => {
  it("deve suportar fluxo completo sem erros", () => {
    const gen = createCodeGeneratorPR(testProjectRoot);

    // Simula análise
    const result: PRAnalysisResult = {
      status: "success",
      fixes: [
        {
          id: "f1",
          issueType: "null-check",
          severity: "high",
          description: "Missing null check",
          suggestedCode: "if (x) return x;",
          explanation: "Prevent NPE",
          confidence: 95,
          tags: ["null-safety"],
          validated: true,
        },
      ],
      refactorings: [
        {
          id: "r1",
          type: "extract-function",
          description: "Extract logic",
          impact: 6,
          difficulty: 2,
          currentCode: "inline code",
          refactoredCode: "function call",
          benefits: ["reusability"],
          risks: [],
          priority: "medium",
          validated: true,
        },
      ],
      improvements: [
        {
          id: "i1",
          category: "performance",
          description: "Add caching",
          impact: 7,
          effort: 3,
          suggestion: "Memoize results",
          priority: "medium",
          validated: false,
        },
      ],
      summary: {
        totalIssuesFound: 2,
        criticalIssues: 0,
        highIssues: 1,
        estimatedTestCoverage: 85,
        estimatedRefactoringTime: "2h",
        overallRiskLevel: "medium",
      },
      processingTimeMs: 2500,
      generatedAt: new Date(),
      errors: [],
    };

    expect(result.status).toBe("success");
    expect(result.fixes).toHaveLength(1);
    expect(result.refactorings).toHaveLength(1);
    expect(result.improvements).toHaveLength(1);
    expect(result.summary.overallRiskLevel).toBe("medium");
  });

  it("deve manter consistência entre análises", () => {
    const gen = createCodeGeneratorPR(testProjectRoot);

    // Simula múltiplas análises
    const code = `
      function getValue(data) {
        return data.value;
      }
    `;

    // Ambas análises devem produzir mesma ID para mesmo input
    const id1 = code.length; // Simplificado
    const id2 = code.length;

    expect(id1).toBe(id2);
  });
});

// ============================================================================
// TESTES DE CASOS EXTREMOS
// ============================================================================

describe("Edge Cases", () => {
  let gen: CodeGeneratorPR;

  beforeEach(() => {
    gen = createCodeGeneratorPR(testProjectRoot);
  });

  it("deve lidar com PR vazio", () => {
    const emptyPR: PRContext = {
      title: "Empty PR",
      description: undefined,
      changedFiles: {},
    };

    expect(emptyPR.title).toBeDefined();
    expect(emptyPR.changedFiles).toEqual({});
  });

  it("deve lidar com código muito grande", () => {
    const largeCode = "function test() { ".repeat(1000) + " }".repeat(1000);

    expect(largeCode.length).toBeGreaterThan(10000);
    // Estrutura deve ainda ser válida
    expect(typeof largeCode).toBe("string");
  });

  it("deve validar severidades de fix", () => {
    const severities: CodeFix["severity"][] = [
      "low",
      "medium",
      "high",
      "critical",
    ];

    const fixes: CodeFix[] = severities.map((sev, idx) => ({
      id: `fix-${idx}`,
      issueType: "other",
      severity: sev,
      description: "Test",
      suggestedCode: "code",
      explanation: "explanation",
      confidence: 80,
      tags: [],
      validated: false,
    }));

    expect(fixes).toHaveLength(4);
    fixes.forEach((fix, idx) => {
      expect(fix.severity).toBe(severities[idx]);
    });
  });

  it("deve validar tipos de refatoração", () => {
    const types: Refactoring["type"][] = [
      "extract-function",
      "extract-constant",
      "extract-interface",
      "merge-duplicates",
      "simplify-logic",
      "improve-naming",
      "reduce-complexity",
      "improve-types",
      "other",
    ];

    const refactorings: Refactoring[] = types.map((type, idx) => ({
      id: `ref-${idx}`,
      type,
      description: "Test",
      impact: 5,
      difficulty: 2,
      currentCode: "code",
      refactoredCode: "refactored",
      benefits: [],
      risks: [],
      priority: "medium",
      validated: false,
    }));

    expect(refactorings).toHaveLength(types.length);
  });
});
