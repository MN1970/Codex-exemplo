/**
 * Code Reviewer Service — Análise estruturada de código (Fase 4)
 * Versão: 1.0.0
 *
 * Responsabilidades:
 * - Análise profunda de código para múltiplas dimensões
 * - Detecção de problemas de segurança, performance e estilo
 * - Sugestões de refatoração com exemplos
 * - Geração de comentários de review estruturados
 * - Avaliação contra best practices
 *
 * Dimensões de análise:
 * 1. Security: injeção, exposição de secrets, autenticação, validação
 * 2. Performance: complexidade, loops, alocações, cache opportunities
 * 3. Style: convenções, documentação, type safety, readability
 * 4. Testing: cobertura, edge cases, mocks, assertions
 * 5. Best Practices: padrões, anti-patterns, design patterns
 *
 * Modelo: Claude Haiku para análise rápida em lote, Opus para análise profunda
 */

import Anthropic from "@anthropic-ai/sdk";

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

/**
 * Severidade de um issue
 */
export type IssueSeverity = "info" | "warning" | "error" | "critical";

/**
 * Categoria de um issue
 */
export type IssueCategory =
  | "security"
  | "performance"
  | "style"
  | "testing"
  | "best-practice";

/**
 * Issue de segurança detectado
 */
export interface SecurityIssue {
  /** Identificador único */
  id: string;

  /** Tipo de vulnerabilidade */
  type:
    | "injection"
    | "exposed-secret"
    | "weak-validation"
    | "insecure-deserialization"
    | "access-control"
    | "cryptography"
    | "external-dependency"
    | "injection-vulnerability"
    | "other";

  /** Severidade (critical > error > warning > info) */
  severity: IssueSeverity;

  /** Descrição do problema */
  description: string;

  /** Localização no código (linha) */
  line: number;

  /** Fim da linha (se multi-linha) */
  endLine?: number;

  /** Snippet de código afetado */
  codeSnippet: string;

  /** Impacto potencial */
  impact: string;

  /** Passos para remediar */
  remediation: string;

  /** Exemplo de código seguro */
  secureExample?: string;

  /** CWE (Common Weakness Enumeration) se aplicável */
  cweId?: string;

  /** Confiança na detecção (0.0-1.0) */
  confidence: number;
}

/**
 * Issue de performance detectado
 */
export interface PerformanceIssue {
  /** Identificador único */
  id: string;

  /** Tipo de problema */
  type:
    | "n-plus-one"
    | "inefficient-loop"
    | "memory-leak"
    | "unnecessary-allocation"
    | "missing-cache"
    | "large-payload"
    | "blocking-operation"
    | "other";

  /** Severidade */
  severity: IssueSeverity;

  /** Descrição */
  description: string;

  /** Linha afetada */
  line: number;

  /** Fim da linha (se multi-linha) */
  endLine?: number;

  /** Snippet de código */
  codeSnippet: string;

  /** Impacto estimado */
  estimatedImpact: {
    /** Tempo adicional (ms) */
    timeMs?: number;

    /** Memória adicional (MB) */
    memoryMb?: number;

    /** Taxa de degradação (%) */
    degradationPercent?: number;
  };

  /** Sugestão de otimização */
  optimization: string;

  /** Exemplo otimizado */
  optimizedExample?: string;

  /** Confiança */
  confidence: number;
}

/**
 * Sugestão de refatoração
 */
export interface Refactoring {
  /** Identificador único */
  id: string;

  /** Tipo de refatoração */
  type:
    | "extract-method"
    | "extract-constant"
    | "simplify-condition"
    | "remove-duplication"
    | "improve-naming"
    | "reduce-complexity"
    | "split-class"
    | "other";

  /** Descrição */
  description: string;

  /** Benefício esperado */
  benefit: string;

  /** Linha afetada */
  line: number;

  /** Fim da linha */
  endLine?: number;

  /** Snippet original */
  beforeCode: string;

  /** Snippet refatorado */
  afterCode: string;

  /** Razão da refatoração */
  rationale: string;

  /** Complexidade ciclomática antes/depois */
  complexity?: {
    before: number;
    after: number;
  };

  /** Prioridade (1=baixa, 5=alta) */
  priority: 1 | 2 | 3 | 4 | 5;
}

/**
 * Comentário estruturado de review
 */
export interface ReviewComment {
  /** Identificador único */
  id: string;

  /** Linha do código */
  line: number;

  /** Fim da linha */
  endLine?: number;

  /** Tipo de comentário */
  type: "suggestion" | "question" | "observation" | "praise" | "issue";

  /** Severidade */
  severity: IssueSeverity;

  /** Título breve */
  title: string;

  /** Corpo do comentário (markdown) */
  body: string;

  /** Tag (ex: @performance, @security) */
  tag?: string;

  /** Código sugerido */
  suggestedCode?: string;

  /** Discussão anterior (context) */
  context?: string;

  /** Se é um issue bloqueante */
  isBlocking: boolean;
}

/**
 * Resultado completo de review de código
 */
export interface Review {
  /** Status geral */
  status: "success" | "failed";

  /** Issues de segurança encontrados */
  securityIssues: SecurityIssue[];

  /** Issues de performance encontrados */
  performanceIssues: PerformanceIssue[];

  /** Sugestões de refatoração */
  refactorings: Refactoring[];

  /** Comentários estruturados */
  comments: ReviewComment[];

  /** Score geral (0-100) */
  overallScore: number;

  /** Análise de melhorias sugeridas */
  improvements: {
    /** Segurança (0-100) */
    security: number;

    /** Performance (0-100) */
    performance: number;

    /** Qualidade de código (0-100) */
    codeQuality: number;

    /** Testabilidade (0-100) */
    testability: number;

    /** Manutenibilidade (0-100) */
    maintainability: number;
  };

  /** Resumo de achados */
  summary: string;

  /** Recomendações principais */
  recommendations: string[];

  /** Tempo de análise (ms) */
  analysisTimeMs: number;

  /** Erros durante análise */
  errors?: string[];
}

/**
 * Contexto de análise
 */
export interface ReviewContext {
  /** Caminho do arquivo */
  filepath: string;

  /** Linguagem de programação */
  language?: "typescript" | "javascript" | "python" | "go" | "rust" | "other";

  /** Contexto adicional (ex: qual framework usa) */
  framework?: string;

  /** Versão do framework/linguagem */
  version?: string;

  /** Padrões/standards a seguir */
  standards?: string[];

  /** Arquivo com dependências (package.json, etc) */
  dependencies?: Record<string, string>;
}

/**
 * Configuração do CodeReviewer
 */
export interface CodeReviewerConfig {
  /** API key do Anthropic */
  apiKey?: string;

  /** Modelo para análise rápida */
  fastModel?: string; // Default: claude-3-5-haiku-20241022

  /** Modelo para análise profunda */
  deepModel?: string; // Default: claude-opus-4-1-20250805

  /** Tokens máximos por request */
  maxTokens?: number; // Default: 4096

  /** Usar análise profunda por padrão */
  useDeepAnalysis?: boolean; // Default: false

  /** Incluir exemplos de código */
  includeExamples?: boolean; // Default: true

  /** Threshold mínimo de confiança */
  confidenceThreshold?: number; // Default: 0.7

  /** URL da API do Anthropic */
  anthropicApiUrl?: string;
}

/**
 * Estatísticas de review
 */
export interface ReviewStats {
  /** Total de issues */
  totalIssues: number;

  /** Issues por severidade */
  bySeverity: Record<IssueSeverity, number>;

  /** Issues por categoria */
  byCategory: Record<IssueCategory, number>;

  /** Score ponderado */
  weightedScore: number;

  /** Tempo de análise */
  analysisTimeMs: number;
}

// ============================================================================
// CODE REVIEWER CLASS
// ============================================================================

export class CodeReviewer {
  private client: Anthropic;
  private config: Required<CodeReviewerConfig>;

  /**
   * Inicializa o revisor de código
   */
  constructor(config: CodeReviewerConfig = {}) {
    this.client = new Anthropic({
      apiKey: config.apiKey || process.env.ANTHROPIC_API_KEY,
      baseURL: config.anthropicApiUrl,
    });

    this.config = {
      apiKey: config.apiKey || process.env.ANTHROPIC_API_KEY || "",
      fastModel: config.fastModel || "claude-3-5-haiku-20241022",
      deepModel: config.deepModel || "claude-opus-4-1-20250805",
      maxTokens: config.maxTokens || 4096,
      useDeepAnalysis: config.useDeepAnalysis || false,
      includeExamples: config.includeExamples !== false,
      confidenceThreshold: config.confidenceThreshold || 0.7,
      anthropicApiUrl: config.anthropicApiUrl || "",
    };
  }

  /**
   * Executa review completo de código
   */
  async reviewCode(
    code: string,
    context?: ReviewContext
  ): Promise<Review> {
    const startTime = Date.now();
    const errors: string[] = [];

    try {
      // Executa análises em paralelo
      const [
        securityIssues,
        performanceIssues,
        refactorings,
        comments,
      ] = await Promise.all([
        this.analyzeSecurityIssues(code, context).catch((e) => {
          errors.push(`Security analysis failed: ${e.message}`);
          return [];
        }),
        this.checkPerformance(code, context).catch((e) => {
          errors.push(`Performance analysis failed: ${e.message}`);
          return [];
        }),
        this.suggestRefactoring(code, context).catch((e) => {
          errors.push(`Refactoring analysis failed: ${e.message}`);
          return [];
        }),
        this.generateComments(code, context).catch((e) => {
          errors.push(`Comment generation failed: ${e.message}`);
          return [];
        }),
      ]);

      // Calcula scores
      const improvements = this.calculateImprovements(
        securityIssues,
        performanceIssues,
        refactorings,
        comments
      );

      const overallScore = this.calculateOverallScore(improvements);

      // Gera resumo
      const summary = this.generateSummary(
        securityIssues,
        performanceIssues,
        refactorings
      );

      // Gera recomendações
      const recommendations = this.generateRecommendations(
        securityIssues,
        performanceIssues,
        refactorings
      );

      return {
        status: "success",
        securityIssues,
        performanceIssues,
        refactorings,
        comments,
        overallScore,
        improvements,
        summary,
        recommendations,
        analysisTimeMs: Date.now() - startTime,
        errors: errors.length > 0 ? errors : undefined,
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      return {
        status: "failed",
        securityIssues: [],
        performanceIssues: [],
        refactorings: [],
        comments: [],
        overallScore: 0,
        improvements: {
          security: 0,
          performance: 0,
          codeQuality: 0,
          testability: 0,
          maintainability: 0,
        },
        summary: `Review failed: ${errorMsg}`,
        recommendations: [],
        analysisTimeMs: Date.now() - startTime,
        errors: [errorMsg],
      };
    }
  }

  /**
   * Analisa problemas de segurança
   */
  async analyzeSecurityIssues(
    code: string,
    context?: ReviewContext
  ): Promise<SecurityIssue[]> {
    const model = this.config.useDeepAnalysis
      ? this.config.deepModel
      : this.config.fastModel;

    const prompt = this.buildSecurityAnalysisPrompt(code, context);

    try {
      const response = await this.client.messages.create({
        model,
        max_tokens: this.config.maxTokens,
        messages: [{ role: "user", content: prompt }],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";
      return this.parseSecurityIssues(responseText);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error("Security analysis error:", errorMsg);
      return [];
    }
  }

  /**
   * Verifica problemas de performance
   */
  async checkPerformance(
    code: string,
    context?: ReviewContext
  ): Promise<PerformanceIssue[]> {
    const model = this.config.useDeepAnalysis
      ? this.config.deepModel
      : this.config.fastModel;

    const prompt = this.buildPerformanceAnalysisPrompt(code, context);

    try {
      const response = await this.client.messages.create({
        model,
        max_tokens: this.config.maxTokens,
        messages: [{ role: "user", content: prompt }],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";
      return this.parsePerformanceIssues(responseText);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error("Performance analysis error:", errorMsg);
      return [];
    }
  }

  /**
   * Sugere refatorações
   */
  async suggestRefactoring(
    code: string,
    context?: ReviewContext
  ): Promise<Refactoring[]> {
    const model = this.config.useDeepAnalysis
      ? this.config.deepModel
      : this.config.fastModel;

    const prompt = this.buildRefactoringPrompt(code, context);

    try {
      const response = await this.client.messages.create({
        model,
        max_tokens: this.config.maxTokens,
        messages: [{ role: "user", content: prompt }],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";
      return this.parseRefactorings(responseText);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error("Refactoring analysis error:", errorMsg);
      return [];
    }
  }

  /**
   * Gera comentários de review estruturados
   */
  async generateComments(
    code: string,
    context?: ReviewContext
  ): Promise<ReviewComment[]> {
    // Primeiro, analisa o código para gerar issues
    const [
      securityIssues,
      performanceIssues,
    ] = await Promise.all([
      this.analyzeSecurityIssues(code, context),
      this.checkPerformance(code, context),
    ]);

    // Gera comentários para cada issue
    const comments: ReviewComment[] = [];

    for (const issue of [...securityIssues]) {
      const comment = await this.generateComment({
        type: "issue",
        title: issue.type,
        line: issue.line,
        description: issue.description,
        severity: issue.severity,
      });
      comments.push(comment);
    }

    for (const issue of [...performanceIssues]) {
      const comment = await this.generateComment({
        type: "suggestion",
        title: issue.type,
        line: issue.line,
        description: issue.description,
        severity: issue.severity,
      });
      comments.push(comment);
    }

    return comments;
  }

  /**
   * Gera um comentário individual estruturado
   */
  async generateComment(issue: {
    type: ReviewComment["type"];
    title: string;
    line: number;
    description: string;
    severity: IssueSeverity;
  }): Promise<ReviewComment> {
    const prompt = `
Gere um comentário de review estruturado para o seguinte issue:

Tipo: ${issue.type}
Título: ${issue.title}
Linha: ${issue.line}
Descrição: ${issue.description}
Severidade: ${issue.severity}

O comentário deve:
1. Ser conciso mas claro (2-3 sentças)
2. Incluir exemplos de como melhorar
3. Ter tom profissional e construtivo
4. Começar com o problema e terminar com a solução

Retorne APENAS o texto do comentário, sem formatação markdown adicional.
`;

    try {
      const response = await this.client.messages.create({
        model: this.config.fastModel,
        max_tokens: 500,
        messages: [{ role: "user", content: prompt }],
      });

      const body =
        response.content[0].type === "text" ? response.content[0].text : "";

      return {
        id: `comment-${Date.now()}-${Math.random()}`,
        line: issue.line,
        type: issue.type,
        severity: issue.severity,
        title: issue.title,
        body,
        isBlocking: ["critical", "error"].includes(issue.severity),
      };
    } catch (error) {
      return {
        id: `comment-${Date.now()}-${Math.random()}`,
        line: issue.line,
        type: issue.type,
        severity: issue.severity,
        title: issue.title,
        body: issue.description,
        isBlocking: ["critical", "error"].includes(issue.severity),
      };
    }
  }

  // =========================================================================
  // MÉTODOS PRIVADOS
  // =========================================================================

  /**
   * Constrói prompt de análise de segurança
   */
  private buildSecurityAnalysisPrompt(
    code: string,
    context?: ReviewContext
  ): string {
    return `Você é um especialista em segurança de código. Analise o seguinte código para encontrar vulnerabilidades e problemas de segurança:

${context?.filepath ? `Arquivo: ${context.filepath}` : ""}
${context?.language ? `Linguagem: ${context.language}` : ""}

\`\`\`
${code}
\`\`\`

Procure por:
1. Injeção (SQL, XSS, command injection)
2. Exposição de secrets (chaves, tokens, senhas)
3. Validação fraca ou ausente
4. Desserialização insegura
5. Controle de acesso inadequado
6. Criptografia fraca
7. Dependências externas inseguras

Retorne APENAS um JSON válido com a estrutura:
\`\`\`json
{
  "issues": [
    {
      "type": "injection|exposed-secret|weak-validation|insecure-deserialization|access-control|cryptography|external-dependency|other",
      "severity": "info|warning|error|critical",
      "description": "descrição do problema",
      "line": 42,
      "codeSnippet": "trecho do código",
      "impact": "impacto potencial",
      "remediation": "como corrigir",
      "secureExample": "exemplo seguro",
      "cweId": "CWE-123",
      "confidence": 0.95
    }
  ]
}
\`\`\``;
  }

  /**
   * Constrói prompt de análise de performance
   */
  private buildPerformanceAnalysisPrompt(
    code: string,
    context?: ReviewContext
  ): string {
    return `Você é um especialista em otimização de performance. Analise o seguinte código para encontrar gargalos e oportunidades de otimização:

${context?.filepath ? `Arquivo: ${context.filepath}` : ""}
${context?.language ? `Linguagem: ${context.language}` : ""}

\`\`\`
${code}
\`\`\`

Procure por:
1. N+1 queries ou chamadas redundantes
2. Loops ineficientes
3. Vazamento de memória
4. Alocações desnecessárias
5. Oportunidades de cache
6. Payloads grandes
7. Operações bloqueantes

Retorne APENAS um JSON válido:
\`\`\`json
{
  "issues": [
    {
      "type": "n-plus-one|inefficient-loop|memory-leak|unnecessary-allocation|missing-cache|large-payload|blocking-operation|other",
      "severity": "info|warning|error|critical",
      "description": "descrição do gargalo",
      "line": 42,
      "codeSnippet": "trecho do código",
      "estimatedImpact": {
        "timeMs": 100,
        "memoryMb": 50,
        "degradationPercent": 10
      },
      "optimization": "como otimizar",
      "optimizedExample": "código otimizado",
      "confidence": 0.85
    }
  ]
}
\`\`\``;
  }

  /**
   * Constrói prompt de sugestão de refatoração
   */
  private buildRefactoringPrompt(
    code: string,
    context?: ReviewContext
  ): string {
    return `Você é um especialista em design de software e code quality. Sugira refatorações para melhorar o código:

${context?.filepath ? `Arquivo: ${context.filepath}` : ""}
${context?.language ? `Linguagem: ${context.language}` : ""}

\`\`\`
${code}
\`\`\`

Procure por oportunidades de:
1. Extrair métodos
2. Extrair constantes
3. Simplificar condicionais
4. Remover duplicação
5. Melhorar nomes
6. Reduzir complexidade ciclomática
7. Dividir classes grandes

Retorne APENAS um JSON válido:
\`\`\`json
{
  "refactorings": [
    {
      "type": "extract-method|extract-constant|simplify-condition|remove-duplication|improve-naming|reduce-complexity|split-class|other",
      "description": "o que refatorar",
      "benefit": "benefício esperado",
      "line": 42,
      "beforeCode": "código original",
      "afterCode": "código refatorado",
      "rationale": "por que refatorar",
      "complexity": {
        "before": 8,
        "after": 3
      },
      "priority": 3
    }
  ]
}
\`\`\``;
  }

  /**
   * Parse issues de segurança do response
   */
  private parseSecurityIssues(responseText: string): SecurityIssue[] {
    try {
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      if (!Array.isArray(parsed.issues)) return [];

      return parsed.issues.map((issue: any, idx: number) => ({
        id: `sec-${idx}`,
        type: issue.type || "other",
        severity: issue.severity || "warning",
        description: issue.description || "",
        line: issue.line || 0,
        endLine: issue.endLine,
        codeSnippet: issue.codeSnippet || "",
        impact: issue.impact || "",
        remediation: issue.remediation || "",
        secureExample: issue.secureExample,
        cweId: issue.cweId,
        confidence: issue.confidence || 0.5,
      }));
    } catch {
      return [];
    }
  }

  /**
   * Parse issues de performance do response
   */
  private parsePerformanceIssues(responseText: string): PerformanceIssue[] {
    try {
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      if (!Array.isArray(parsed.issues)) return [];

      return parsed.issues.map((issue: any, idx: number) => ({
        id: `perf-${idx}`,
        type: issue.type || "other",
        severity: issue.severity || "warning",
        description: issue.description || "",
        line: issue.line || 0,
        endLine: issue.endLine,
        codeSnippet: issue.codeSnippet || "",
        estimatedImpact: issue.estimatedImpact || {},
        optimization: issue.optimization || "",
        optimizedExample: issue.optimizedExample,
        confidence: issue.confidence || 0.5,
      }));
    } catch {
      return [];
    }
  }

  /**
   * Parse refatorações do response
   */
  private parseRefactorings(responseText: string): Refactoring[] {
    try {
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      if (!Array.isArray(parsed.refactorings)) return [];

      return parsed.refactorings.map((ref: any, idx: number) => ({
        id: `refactor-${idx}`,
        type: ref.type || "other",
        description: ref.description || "",
        benefit: ref.benefit || "",
        line: ref.line || 0,
        endLine: ref.endLine,
        beforeCode: ref.beforeCode || "",
        afterCode: ref.afterCode || "",
        rationale: ref.rationale || "",
        complexity: ref.complexity,
        priority: ref.priority || 3,
      }));
    } catch {
      return [];
    }
  }

  /**
   * Calcula scores de melhoria
   */
  private calculateImprovements(
    security: SecurityIssue[],
    performance: PerformanceIssue[],
    refactorings: Refactoring[],
    comments: ReviewComment[]
  ) {
    const securityScore = this.calculateDimensionScore(security, "security");
    const performanceScore = this.calculateDimensionScore(
      performance,
      "performance"
    );
    const codeQualityScore =
      80 - (refactorings.length > 0 ? Math.min(refactorings.length * 5, 30) : 0);
    const testabilityScore = comments.filter((c) => c.tag === "@testing")
      .length > 0 ? 60 : 80;
    const maintainabilityScore =
      85 - (comments.filter((c) => c.tag === "@naming").length > 0 ? 10 : 0);

    return {
      security: Math.max(0, Math.min(100, securityScore)),
      performance: Math.max(0, Math.min(100, performanceScore)),
      codeQuality: Math.max(0, Math.min(100, codeQualityScore)),
      testability: Math.max(0, Math.min(100, testabilityScore)),
      maintainability: Math.max(0, Math.min(100, maintainabilityScore)),
    };
  }

  /**
   * Calcula score por dimensão
   */
  private calculateDimensionScore(
    issues: SecurityIssue[] | PerformanceIssue[],
    dimension: string
  ): number {
    if (issues.length === 0) return 100;

    const criticalCount = issues.filter((i) => i.severity === "critical")
      .length;
    const errorCount = issues.filter((i) => i.severity === "error").length;
    const warningCount = issues.filter((i) => i.severity === "warning").length;

    const score =
      100 -
      (criticalCount * 30 + errorCount * 15 + warningCount * 5);

    return Math.max(0, score);
  }

  /**
   * Calcula score geral
   */
  private calculateOverallScore(improvements: {
    security: number;
    performance: number;
    codeQuality: number;
    testability: number;
    maintainability: number;
  }): number {
    const weights = {
      security: 0.3,
      performance: 0.25,
      codeQuality: 0.25,
      testability: 0.1,
      maintainability: 0.1,
    };

    const score =
      (improvements.security * weights.security +
        improvements.performance * weights.performance +
        improvements.codeQuality * weights.codeQuality +
        improvements.testability * weights.testability +
        improvements.maintainability * weights.maintainability) /
      Object.values(weights).reduce((a, b) => a + b);

    return Math.round(score);
  }

  /**
   * Gera resumo de achados
   */
  private generateSummary(
    security: SecurityIssue[],
    performance: PerformanceIssue[],
    refactorings: Refactoring[]
  ): string {
    const criticalSecurity = security.filter((i) => i.severity === "critical");
    const errorPerformance = performance.filter((i) => i.severity === "error");

    const parts: string[] = [];

    if (criticalSecurity.length > 0) {
      parts.push(
        `🔴 ${criticalSecurity.length} critical security issue(s) found`
      );
    }

    if (errorPerformance.length > 0) {
      parts.push(
        `⚠️  ${errorPerformance.length} performance issue(s) found`
      );
    }

    if (refactorings.length > 0) {
      parts.push(
        `💡 ${refactorings.length} refactoring opportunity(ies) identified`
      );
    }

    if (parts.length === 0) {
      return "✅ Code review completed successfully with no critical issues found.";
    }

    return parts.join(". ") + ".";
  }

  /**
   * Gera recomendações
   */
  private generateRecommendations(
    security: SecurityIssue[],
    performance: PerformanceIssue[],
    refactorings: Refactoring[]
  ): string[] {
    const recommendations: string[] = [];

    if (security.filter((i) => i.severity === "critical").length > 0) {
      recommendations.push(
        "Fix all critical security vulnerabilities before merging"
      );
    }

    if (performance.filter((i) => i.severity === "error").length > 0) {
      recommendations.push("Address performance bottlenecks");
    }

    const highPriorityRefactors = refactorings.filter((r) => r.priority >= 4);
    if (highPriorityRefactors.length > 0) {
      recommendations.push(`Apply high-priority refactorings: ${highPriorityRefactors.map((r) => r.type).join(", ")}`);
    }

    if (recommendations.length === 0) {
      recommendations.push("Code quality is good, proceed with review");
    }

    return recommendations;
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Factory para criar uma instância do CodeReviewer
 */
export function createCodeReviewer(
  config?: CodeReviewerConfig
): CodeReviewer {
  return new CodeReviewer(config);
}

/**
 * Executa review rápido de código (Haiku)
 */
export async function reviewCodeFast(
  code: string,
  context?: ReviewContext
): Promise<Review> {
  const reviewer = new CodeReviewer({
    fastModel: "claude-3-5-haiku-20241022",
    useDeepAnalysis: false,
  });
  return reviewer.reviewCode(code, context);
}

/**
 * Executa review profundo de código (Opus)
 */
export async function reviewCodeDeep(
  code: string,
  context?: ReviewContext
): Promise<Review> {
  const reviewer = new CodeReviewer({
    deepModel: "claude-opus-4-1-20250805",
    useDeepAnalysis: true,
  });
  return reviewer.reviewCode(code, context);
}

/**
 * Analisa apenas segurança
 */
export async function analyzeSecurity(
  code: string,
  context?: ReviewContext
): Promise<SecurityIssue[]> {
  const reviewer = new CodeReviewer();
  return reviewer.analyzeSecurityIssues(code, context);
}

/**
 * Analisa apenas performance
 */
export async function analyzePerformance(
  code: string,
  context?: ReviewContext
): Promise<PerformanceIssue[]> {
  const reviewer = new CodeReviewer();
  return reviewer.checkPerformance(code, context);
}

/**
 * Sugere refactorações
 */
export async function suggestRefactors(
  code: string,
  context?: ReviewContext
): Promise<Refactoring[]> {
  const reviewer = new CodeReviewer();
  return reviewer.suggestRefactoring(code, context);
}
