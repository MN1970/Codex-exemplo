/**
 * Code Generator Enhanced — Serviço de geração de código baseado em contexto de PR
 * Versão: 2.0.0 (Phase 3 - PR-Specific Enhancement)
 *
 * Responsabilidades:
 * - Estende CodeGenerator com análise específica de PRs
 * - Analisa diffs de PR para gerar fixes de issues comuns
 * - Sugere refatorações baseadas em código novo
 * - Gera casos de teste para novo código
 * - Sugere melhorias de performance e segurança
 * - Implementa cache e logging de auditoria
 *
 * Features:
 * 1. Fix generation — detecção e correção de bugs comuns
 * 2. Refactoring suggestions — oportunidades de melhoria de código
 * 3. Test generation — cobertura de testes automática
 * 4. Improvement analysis — sugestões de performance, segurança, tipos
 * 5. Caching — evita re-análise do mesmo código
 * 6. Audit logging — rastreamento completo das operações
 */

import Anthropic from "@anthropic-ai/sdk";
import { createHash } from "crypto";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { join } from "path";

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

/**
 * Contexto de PR para análise
 */
export interface PRContext {
  /** Título do PR */
  title: string;

  /** Descrição do PR */
  description?: string;

  /** Branch do PR */
  branch?: string;

  /** Autor do PR */
  author?: string;

  /** Diff das mudanças (formato git diff ou raw content) */
  diff?: string;

  /** Arquivos alterados com seu conteúdo */
  changedFiles?: Record<string, string>;

  /** Arquivos deletados (nomes) */
  deletedFiles?: string[];

  /** Labels do PR */
  labels?: string[];

  /** Se é WIP (Work in Progress) */
  isWIP?: boolean;

  /** Relacionado a issues */
  relatedIssueNumbers?: number[];
}

/**
 * Código que precisa de correção
 */
export interface CodeFix {
  /** ID único do fix */
  id: string;

  /** Tipo de problema detectado */
  issueType:
    | "null-check"
    | "type-error"
    | "performance"
    | "security"
    | "memory-leak"
    | "error-handling"
    | "logic-error"
    | "style"
    | "other";

  /** Severidade (low, medium, high, critical) */
  severity: "low" | "medium" | "high" | "critical";

  /** Descrição do problema */
  description: string;

  /** Localização (arquivo:linha:coluna) */
  location?: string;

  /** Código problemático */
  problematicCode?: string;

  /** Código corrigido proposto */
  suggestedCode: string;

  /** Explicação da correção */
  explanation: string;

  /** Confiança na sugestão (0-100) */
  confidence: number;

  /** Tags para categorização */
  tags: string[];

  /** Se foi validado/testado */
  validated: boolean;
}

/**
 * Sugestão de refatoração
 */
export interface Refactoring {
  /** ID único */
  id: string;

  /** Tipo de refatoração */
  type:
    | "extract-function"
    | "extract-constant"
    | "extract-interface"
    | "merge-duplicates"
    | "simplify-logic"
    | "improve-naming"
    | "reduce-complexity"
    | "improve-types"
    | "other";

  /** Descrição */
  description: string;

  /** Impacto estimado (1-10, onde 10 é melhoramento máximo) */
  impact: number;

  /** Dificuldade de implementação (1-10, onde 10 é muito difícil) */
  difficulty: number;

  /** Código atual */
  currentCode: string;

  /** Código refatorado proposto */
  refactoredCode: string;

  /** Benefícios da refatoração */
  benefits: string[];

  /** Riscos potenciais */
  risks: string[];

  /** Priority (high/medium/low) */
  priority: "high" | "medium" | "low";

  /** Se foi validado */
  validated: boolean;
}

/**
 * Suite de testes gerada
 */
export interface TestSuite {
  /** ID único */
  id: string;

  /** Framework de testes usado */
  testFramework: "jest" | "vitest" | "mocha" | "other";

  /** Cobertura esperada (0-100%) */
  expectedCoverage: number;

  /** Número de casos de teste */
  testCaseCount: number;

  /** Código dos testes */
  testCode: string;

  /** Casos de teste individuais */
  testCases: TestCase[];

  /** Tipos testados */
  testedFunctions: string[];

  /** Cenários de teste */
  scenarios: TestScenario[];

  /** Arquivo sugerido */
  suggestedFileName: string;
}

/**
 * Caso de teste individual
 */
export interface TestCase {
  /** Nome do teste */
  name: string;

  /** Descrição */
  description: string;

  /** Tipo de teste (unit/integration/e2e) */
  type: "unit" | "integration" | "e2e";

  /** Dados de entrada (setup) */
  input: Record<string, unknown>;

  /** Output esperado */
  expectedOutput: unknown;

  /** Assertions */
  assertions: string[];

  /** Se é crítico */
  critical: boolean;
}

/**
 * Cenário de teste (agrupamento de casos)
 */
export interface TestScenario {
  /** Nome do cenário */
  name: string;

  /** Descrição */
  description: string;

  /** Casos de teste inclusos */
  testCaseNames: string[];

  /** Ordem de execução */
  executionOrder: number;
}

/**
 * Sugestão de melhoria
 */
export interface Improvement {
  /** ID único */
  id: string;

  /** Categoria */
  category:
    | "performance"
    | "security"
    | "readability"
    | "maintainability"
    | "types"
    | "error-handling"
    | "documentation"
    | "testing"
    | "other";

  /** Descrição */
  description: string;

  /** Impacto (1-10) */
  impact: number;

  /** Esforço (1-10) */
  effort: number;

  /** Sugestão proposta */
  suggestion: string;

  /** Exemplos de código */
  codeExample?: string;

  /** Referências/links úteis */
  references?: string[];

  /** Priority */
  priority: "high" | "medium" | "low";

  /** Se foi validado */
  validated: boolean;
}

/**
 * Resultado da análise de PR
 */
export interface PRAnalysisResult {
  /** Status */
  status: "success" | "partial" | "failed";

  /** Fixes encontrados e sugeridos */
  fixes: CodeFix[];

  /** Refatorações sugeridas */
  refactorings: Refactoring[];

  /** Suite de testes gerada */
  testSuite?: TestSuite;

  /** Melhorias sugeridas */
  improvements: Improvement[];

  /** Sumário executivo */
  summary: {
    totalIssuesFound: number;
    criticalIssues: number;
    highIssues: number;
    estimatedTestCoverage: number;
    estimatedRefactoringTime: string;
    overallRiskLevel: "low" | "medium" | "high" | "critical";
  };

  /** Tempo de processamento (ms) */
  processingTimeMs: number;

  /** Timestamp de geração */
  generatedAt: Date;

  /** Erros encontrados durante análise */
  errors: string[];
}

/**
 * Entrada de cache
 */
interface CacheEntry {
  /** Hash do conteúdo original */
  contentHash: string;

  /** Resultado em cache */
  result: PRAnalysisResult;

  /** Timestamp da entrada */
  timestamp: Date;

  /** TTL em ms (default: 24h) */
  ttl: number;
}

/**
 * Entrada de auditoria
 */
interface AuditLogEntry {
  /** Timestamp */
  timestamp: Date;

  /** Ação realizada */
  action: string;

  /** Detalhes */
  details: Record<string, unknown>;

  /** Usuário (se disponível) */
  user?: string;

  /** Status (success/error) */
  status: "success" | "error";

  /** Tempo de execução (ms) */
  executionTimeMs: number;

  /** Erro (se houver) */
  error?: string;
}

// ============================================================================
// CODE GENERATOR PR SERVICE
// ============================================================================

export class CodeGeneratorPR {
  private client: Anthropic;
  private projectRoot: string;
  private cache: Map<string, CacheEntry>;
  private auditLog: AuditLogEntry[];
  private auditLogPath: string;
  private cacheDir: string;

  /**
   * Inicializa o gerador de código com suporte a PR
   */
  constructor(
    apiKey?: string,
    projectRoot?: string,
    auditLogPath?: string
  ) {
    this.client = new Anthropic({
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY,
    });
    this.projectRoot = projectRoot || process.cwd();
    this.cache = new Map();
    this.auditLog = [];
    this.auditLogPath =
      auditLogPath ||
      join(this.projectRoot, ".claude", "logs", "code-gen-audit.jsonl");
    this.cacheDir = join(this.projectRoot, ".claude", "cache", "code-gen");

    // Cria diretórios se não existirem
    this.ensureDirectories();
    this.loadAuditLog();
  }

  /**
   * Gera fixes baseado no diff do PR
   *
   * @param prDiff - Diff do PR
   * @returns Array de fixes sugeridos
   */
  async generateFixes(prDiff: string): Promise<CodeFix[]> {
    const startTime = Date.now();
    const action = "generateFixes";

    try {
      // Verifica cache
      const cached = this.checkCache(prDiff, "fixes");
      if (cached && cached.fixes.length > 0) {
        this.logAudit(action, { source: "cache" }, startTime, "success");
        return cached.fixes;
      }

      const systemPrompt = `Tu es um especialista em análise de código e segurança.
Analisarás um diff de PR e identificarás problemas:
1. Null/undefined checks faltando
2. Type errors potenciais
3. Issues de performance
4. Vulnerabilidades de segurança
5. Memory leaks
6. Error handling inadequado
7. Logic errors
8. Style issues

Para cada problema, retorna:
- Tipo do problema
- Severidade
- Localização
- Código problemático
- Código corrigido
- Explicação

Retorna JSON estruturado.`;

      const userPrompt = `Analisa este diff e sugere fixes:

\`\`\`diff
${prDiff}
\`\`\`

Retorna um array JSON de fixes com estrutura:
{
  "fixes": [
    {
      "issueType": "null-check|type-error|performance|security|memory-leak|error-handling|logic-error|style|other",
      "severity": "low|medium|high|critical",
      "description": "...",
      "location": "file:line:col",
      "problematicCode": "...",
      "suggestedCode": "...",
      "explanation": "...",
      "confidence": 85,
      "tags": ["tag1", "tag2"]
    }
  ]
}`;

      const response = await this.client.messages.create({
        model: "claude-opus-4-1-20250805",
        max_tokens: 4000,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      });

      const assistantMessage =
        response.content[0].type === "text" ? response.content[0].text : "{}";

      // Parse resposta
      const fixes = this.parseFixes(assistantMessage);

      // Adiciona IDs únicos
      const enrichedFixes = fixes.map((fix) => ({
        ...fix,
        id: this.generateId(fix),
        validated: false,
      }));

      this.logAudit(
        action,
        { fixesCount: enrichedFixes.length },
        startTime,
        "success"
      );

      return enrichedFixes;
    } catch (error) {
      this.logAudit(
        action,
        { error: String(error) },
        startTime,
        "error",
        error instanceof Error ? error.message : String(error)
      );
      throw error;
    }
  }

  /**
   * Gera sugestões de refatoração
   *
   * @param code - Código a refatorar
   * @returns Array de sugestões de refatoração
   */
  async generateRefactorings(code: string): Promise<Refactoring[]> {
    const startTime = Date.now();
    const action = "generateRefactorings";

    try {
      // Verifica cache
      const cached = this.checkCache(code, "refactorings");
      if (cached && cached.refactorings.length > 0) {
        this.logAudit(action, { source: "cache" }, startTime, "success");
        return cached.refactorings;
      }

      const systemPrompt = `Tu es um especialista em refatoração de código.
Analisarás código e sugerirás refatorações para:
1. Extrair funções/constantes/interfaces
2. Mesclar duplicatas
3. Simplificar lógica
4. Melhorar nomes
5. Reduzir complexidade ciclomática
6. Melhorar tipagem

Para cada refatoração, fornece:
- Tipo
- Descrição
- Código atual
- Código refatorado
- Benefícios e riscos
- Impact e difficulty scores

Retorna JSON estruturado.`;

      const userPrompt = `Analisa este código e sugere refatorações:

\`\`\`typescript
${code}
\`\`\`

Retorna um array JSON:
{
  "refactorings": [
    {
      "type": "extract-function|extract-constant|extract-interface|merge-duplicates|simplify-logic|improve-naming|reduce-complexity|improve-types|other",
      "description": "...",
      "impact": 8,
      "difficulty": 3,
      "currentCode": "...",
      "refactoredCode": "...",
      "benefits": ["benefit1", "benefit2"],
      "risks": ["risk1"],
      "priority": "high|medium|low"
    }
  ]
}`;

      const response = await this.client.messages.create({
        model: "claude-opus-4-1-20250805",
        max_tokens: 4000,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      });

      const assistantMessage =
        response.content[0].type === "text" ? response.content[0].text : "{}";

      const refactorings = this.parseRefactorings(assistantMessage);

      const enrichedRefactorings = refactorings.map((ref) => ({
        ...ref,
        id: this.generateId(ref),
        validated: false,
      }));

      this.logAudit(
        action,
        { refactoringsCount: enrichedRefactorings.length },
        startTime,
        "success"
      );

      return enrichedRefactorings;
    } catch (error) {
      this.logAudit(
        action,
        { error: String(error) },
        startTime,
        "error",
        error instanceof Error ? error.message : String(error)
      );
      throw error;
    }
  }

  /**
   * Gera casos de teste para código novo
   *
   * @param code - Código para o qual gerar testes
   * @param testFramework - Framework de testes (jest, vitest, mocha)
   * @returns Suite de testes gerada
   */
  async generateTests(
    code: string,
    testFramework: "jest" | "vitest" | "mocha" = "jest"
  ): Promise<TestSuite> {
    const startTime = Date.now();
    const action = "generateTests";

    try {
      // Verifica cache
      const cacheKey = `${code}-${testFramework}`;
      const cached = this.checkCache(cacheKey, "testSuite");
      if (cached && cached.testSuite) {
        this.logAudit(action, { source: "cache" }, startTime, "success");
        return cached.testSuite;
      }

      const systemPrompt = `Tu es um especialista em testes de software.
Gerarás uma suite completa de testes para código TypeScript/JavaScript.
Usa ${testFramework} como framework.

Coverage:
- Happy path (casos de sucesso)
- Edge cases
- Error cases
- Integration scenarios

Retorna:
- Código dos testes
- Casos individuais com setup/assertion
- Cenários de teste
- Cobertura estimada`;

      const userPrompt = `Gera testes completos para este código usando ${testFramework}:

\`\`\`typescript
${code}
\`\`\`

Retorna JSON:
{
  "testFramework": "${testFramework}",
  "expectedCoverage": 90,
  "testCaseCount": 5,
  "testCode": "// código completo dos testes",
  "testCases": [
    {
      "name": "test name",
      "description": "...",
      "type": "unit|integration|e2e",
      "input": { },
      "expectedOutput": null,
      "assertions": ["assertion1"],
      "critical": true
    }
  ],
  "testedFunctions": ["funcName"],
  "scenarios": [
    {
      "name": "scenario",
      "description": "...",
      "testCaseNames": ["test1"],
      "executionOrder": 1
    }
  ],
  "suggestedFileName": "module.test.ts"
}`;

      const response = await this.client.messages.create({
        model: "claude-opus-4-1-20250805",
        max_tokens: 5000,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      });

      const assistantMessage =
        response.content[0].type === "text" ? response.content[0].text : "{}";

      const testSuite = this.parseTestSuite(assistantMessage);

      this.logAudit(
        action,
        {
          testCaseCount: testSuite.testCaseCount,
          expectedCoverage: testSuite.expectedCoverage,
        },
        startTime,
        "success"
      );

      return testSuite;
    } catch (error) {
      this.logAudit(
        action,
        { error: String(error) },
        startTime,
        "error",
        error instanceof Error ? error.message : String(error)
      );
      throw error;
    }
  }

  /**
   * Sugere melhorias gerais no código
   *
   * @param code - Código a analisar
   * @returns Array de sugestões de melhoria
   */
  async suggestImprovements(code: string): Promise<Improvement[]> {
    const startTime = Date.now();
    const action = "suggestImprovements";

    try {
      // Verifica cache
      const cached = this.checkCache(code, "improvements");
      if (cached && cached.improvements.length > 0) {
        this.logAudit(action, { source: "cache" }, startTime, "success");
        return cached.improvements;
      }

      const systemPrompt = `Tu es um especialista em qualidade de código.
Analisarás código e sugerirás melhorias em:
1. Performance (otimizações, caching, algoritmos)
2. Security (vulnerabilidades, validação de input)
3. Readability (clareza, documentação)
4. Maintainability (modularidade, testes)
5. Types (type safety, generics)
6. Error handling
7. Documentation
8. Testing

Para cada melhoria, fornece:
- Categoria
- Descrição
- Impacto (1-10)
- Esforço (1-10)
- Sugestão com exemplo
- Prioridade

Retorna JSON estruturado.`;

      const userPrompt = `Analisa este código e sugere melhorias:

\`\`\`typescript
${code}
\`\`\`

Retorna um array JSON:
{
  "improvements": [
    {
      "category": "performance|security|readability|maintainability|types|error-handling|documentation|testing|other",
      "description": "...",
      "impact": 7,
      "effort": 2,
      "suggestion": "...",
      "codeExample": "...",
      "references": ["link1"],
      "priority": "high|medium|low"
    }
  ]
}`;

      const response = await this.client.messages.create({
        model: "claude-opus-4-1-20250805",
        max_tokens: 4000,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      });

      const assistantMessage =
        response.content[0].type === "text" ? response.content[0].text : "{}";

      const improvements = this.parseImprovements(assistantMessage);

      const enrichedImprovements = improvements.map((imp) => ({
        ...imp,
        id: this.generateId(imp),
        validated: false,
      }));

      this.logAudit(
        action,
        { improvementsCount: enrichedImprovements.length },
        startTime,
        "success"
      );

      return enrichedImprovements;
    } catch (error) {
      this.logAudit(
        action,
        { error: String(error) },
        startTime,
        "error",
        error instanceof Error ? error.message : String(error)
      );
      throw error;
    }
  }

  /**
   * Análise completa de PR
   *
   * @param prContext - Contexto do PR
   * @returns Resultado completo da análise
   */
  async analyzePR(prContext: PRContext): Promise<PRAnalysisResult> {
    const startTime = Date.now();
    const action = "analyzePR";

    try {
      const results: PRAnalysisResult = {
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
        processingTimeMs: 0,
        generatedAt: new Date(),
        errors: [],
      };

      // Analisa diffs
      if (prContext.diff) {
        results.fixes = await this.generateFixes(prContext.diff);
      }

      // Analisa arquivos alterados
      if (prContext.changedFiles) {
        for (const [fileName, content] of Object.entries(
          prContext.changedFiles
        )) {
          if (fileName.endsWith(".ts") || fileName.endsWith(".tsx")) {
            const refactorings = await this.generateRefactorings(content);
            results.refactorings.push(...refactorings);

            const testSuite = await this.generateTests(content);
            if (!results.testSuite) {
              results.testSuite = testSuite;
            }

            const improvements = await this.suggestImprovements(content);
            results.improvements.push(...improvements);
          }
        }
      }

      // Calcula sumário
      results.summary = this.calculateSummary(results);
      results.processingTimeMs = Date.now() - startTime;

      this.logAudit(
        action,
        {
          pr: prContext.title,
          fixesCount: results.fixes.length,
          refactoringsCount: results.refactorings.length,
          improvementsCount: results.improvements.length,
        },
        startTime,
        "success"
      );

      return results;
    } catch (error) {
      const result: PRAnalysisResult = {
        status: "failed",
        fixes: [],
        refactorings: [],
        improvements: [],
        summary: {
          totalIssuesFound: 0,
          criticalIssues: 0,
          highIssues: 0,
          estimatedTestCoverage: 0,
          estimatedRefactoringTime: "0h",
          overallRiskLevel: "critical",
        },
        processingTimeMs: Date.now() - startTime,
        generatedAt: new Date(),
        errors: [
          error instanceof Error ? error.message : String(error),
        ],
      };

      this.logAudit(
        action,
        { error: String(error) },
        startTime,
        "error",
        error instanceof Error ? error.message : String(error)
      );

      return result;
    }
  }

  /**
   * Limpa cache (operação de manutenção)
   */
  clearCache(): void {
    const now = Date.now();
    let cleared = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp.getTime() > entry.ttl) {
        this.cache.delete(key);
        cleared++;
      }
    }

    this.logAudit("clearCache", { entriesCleared: cleared }, 0, "success");
  }

  /**
   * Exporta auditoria para arquivo
   */
  saveAuditLog(): void {
    try {
      const dir = this.auditLogPath.substring(
        0,
        this.auditLogPath.lastIndexOf("/")
      );

      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      const content = this.auditLog
        .map((entry) => JSON.stringify(entry))
        .join("\n");

      writeFileSync(this.auditLogPath, content, "utf-8");
    } catch (error) {
      console.error(
        "Erro ao salvar audit log:",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  /**
   * Retorna estatísticas de cache
   */
  getCacheStats(): { size: number; entries: number } {
    return {
      size: this.cache.size,
      entries: this.cache.size,
    };
  }

  /**
   * Retorna estatísticas de auditoria
   */
  getAuditStats(): {
    totalActions: number;
    successCount: number;
    errorCount: number;
    averageExecutionTime: number;
  } {
    const total = this.auditLog.length;
    const successes = this.auditLog.filter((e) => e.status === "success").length;
    const errors = total - successes;
    const avgTime =
      total === 0
        ? 0
        : this.auditLog.reduce((sum, e) => sum + e.executionTimeMs, 0) / total;

    return {
      totalActions: total,
      successCount: successes,
      errorCount: errors,
      averageExecutionTime: avgTime,
    };
  }

  // ========================================================================
  // MÉTODOS PRIVADOS
  // ========================================================================

  private checkCache(
    content: string,
    type: string
  ): { fixes: CodeFix[]; refactorings: Refactoring[]; improvements: Improvement[]; testSuite?: TestSuite } | null {
    const hash = this.hashContent(content);
    const key = `${type}:${hash}`;

    const entry = this.cache.get(key);
    if (!entry) return null;

    // Verifica TTL
    if (Date.now() - entry.timestamp.getTime() > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return {
      fixes: entry.result.fixes,
      refactorings: entry.result.refactorings,
      improvements: entry.result.improvements,
      testSuite: entry.result.testSuite,
    };
  }

  private hashContent(content: string): string {
    return createHash("sha256").update(content).digest("hex");
  }

  private generateId(obj: unknown): string {
    const hash = createHash("sha256")
      .update(JSON.stringify(obj))
      .digest("hex");
    return hash.substring(0, 12);
  }

  private parseFixes(response: string): Partial<CodeFix>[] {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      return parsed.fixes || [];
    } catch {
      return [];
    }
  }

  private parseRefactorings(response: string): Partial<Refactoring>[] {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      return parsed.refactorings || [];
    } catch {
      return [];
    }
  }

  private parseTestSuite(response: string): TestSuite {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error("No JSON found");

      const parsed = JSON.parse(jsonMatch[0]);
      return {
        id: this.generateId(parsed),
        testFramework: parsed.testFramework || "jest",
        expectedCoverage: parsed.expectedCoverage || 0,
        testCaseCount: parsed.testCaseCount || 0,
        testCode: parsed.testCode || "",
        testCases: parsed.testCases || [],
        testedFunctions: parsed.testedFunctions || [],
        scenarios: parsed.scenarios || [],
        suggestedFileName: parsed.suggestedFileName || "test.ts",
      };
    } catch {
      return {
        id: this.generateId({}),
        testFramework: "jest",
        expectedCoverage: 0,
        testCaseCount: 0,
        testCode: "",
        testCases: [],
        testedFunctions: [],
        scenarios: [],
        suggestedFileName: "test.ts",
      };
    }
  }

  private parseImprovements(response: string): Partial<Improvement>[] {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      return parsed.improvements || [];
    } catch {
      return [];
    }
  }

  private calculateSummary(result: PRAnalysisResult) {
    const criticalIssues = result.fixes.filter(
      (f) => f.severity === "critical"
    ).length;
    const highIssues = result.fixes.filter((f) => f.severity === "high").length;

    let riskLevel: "low" | "medium" | "high" | "critical" = "low";
    if (criticalIssues > 0) riskLevel = "critical";
    else if (highIssues > 2 || result.fixes.length > 10) riskLevel = "high";
    else if (result.fixes.length > 5) riskLevel = "medium";

    const estimatedTime = Math.ceil(
      result.refactorings.reduce((sum, r) => sum + r.difficulty * 5, 0) / 60
    );

    return {
      totalIssuesFound:
        result.fixes.length +
        result.refactorings.length +
        result.improvements.length,
      criticalIssues,
      highIssues,
      estimatedTestCoverage: result.testSuite?.expectedCoverage || 0,
      estimatedRefactoringTime: `${estimatedTime}h`,
      overallRiskLevel: riskLevel,
    };
  }

  private logAudit(
    action: string,
    details: Record<string, unknown>,
    startTime: number,
    status: "success" | "error",
    error?: string
  ): void {
    const executionTimeMs = startTime === 0 ? 0 : Date.now() - startTime;

    const entry: AuditLogEntry = {
      timestamp: new Date(),
      action,
      details,
      status,
      executionTimeMs,
      ...(error && { error }),
    };

    this.auditLog.push(entry);

    // Auto-save periodicamente (a cada 50 entradas)
    if (this.auditLog.length % 50 === 0) {
      this.saveAuditLog();
    }
  }

  private loadAuditLog(): void {
    try {
      if (!existsSync(this.auditLogPath)) {
        return;
      }

      const content = readFileSync(this.auditLogPath, "utf-8");
      const lines = content.trim().split("\n");

      for (const line of lines) {
        if (line) {
          try {
            const entry = JSON.parse(line) as AuditLogEntry;
            entry.timestamp = new Date(entry.timestamp);
            this.auditLog.push(entry);
          } catch {
            // Ignora linhas malformadas
          }
        }
      }
    } catch (error) {
      console.error(
        "Erro ao carregar audit log:",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  private ensureDirectories(): void {
    const dirs = [
      join(this.projectRoot, ".claude"),
      join(this.projectRoot, ".claude", "logs"),
      this.cacheDir,
    ];

    for (const dir of dirs) {
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }
    }
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Cria instância do gerador com suporte a PR
 */
export function createCodeGeneratorPR(
  projectRoot?: string,
  auditLogPath?: string
): CodeGeneratorPR {
  return new CodeGeneratorPR(undefined, projectRoot, auditLogPath);
}

/**
 * Função auxiliar para análise rápida de PR
 */
export async function analyzeQuickPR(
  diff: string,
  projectRoot?: string
): Promise<CodeFix[]> {
  const generator = createCodeGeneratorPR(projectRoot);
  return generator.generateFixes(diff);
}

/**
 * Função auxiliar para sugestões de teste
 */
export async function suggestTestsQuick(
  code: string,
  framework: "jest" | "vitest" | "mocha" = "jest"
): Promise<TestSuite> {
  const generator = createCodeGeneratorPR();
  return generator.generateTests(code, framework);
}
