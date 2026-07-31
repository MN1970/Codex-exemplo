/**
 * Code Reviewer Agent — Análise profunda de PRs e agentes novos
 * Versão: 1.0.0
 *
 * Análise de:
 * - Correctness: lógica, edge cases, validações
 * - Security: injeção, exposição de secrets, acessos
 * - Performance: complexidade, loops, alocações
 * - Style: padrões, type safety, documentação
 *
 * Usa Claude Opus para análise estruturada e retorna findings.
 */

import Anthropic from "@anthropic-ai/sdk";

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

/**
 * Dimensões de análise
 */
export type AnalysisDimension = "correctness" | "security" | "performance" | "style";

/**
 * Severidade do finding
 */
export type FindingSeverity = "info" | "warning" | "error" | "critical";

/**
 * Finding individual
 */
export interface CodeFinding {
  /** Arquivo afetado (caminho relativo) */
  file: string;

  /** Número de linha (1-indexed) */
  line: number;

  /** Fim da linha (se span multi-line) */
  endLine?: number;

  /** Dimensão de análise */
  dimension: AnalysisDimension;

  /** Severidade */
  severity: FindingSeverity;

  /** Título curto do problema */
  title: string;

  /** Descrição detalhada */
  description: string;

  /** Sugestão de fix */
  suggestion?: string;

  /** Snippet de código problemático */
  code?: string;
}

/**
 * Input para o reviewer
 */
export interface CodeReviewInput {
  /** Diff da PR (formato unified diff) */
  prDiff: string;

  /** Conteúdo do novo agente ou serviço */
  newAgentCode: string;

  /** Caminho do novo agente (ex: src/agents/code-reviewer.ts) */
  agentPath: string;

  /** Contexto do PR (título, descrição) */
  prContext?: {
    title?: string;
    description?: string;
    author?: string;
  };

  /** Dimensões a analisar (default: todas) */
  dimensions?: AnalysisDimension[];
}

/**
 * Output da análise
 */
export interface CodeReviewOutput {
  /** Status da análise */
  status: "success" | "failed";

  /** Findings encontrados */
  findings: CodeFinding[];

  /** Sumarização (max 50 linhas) */
  summary: string;

  /** Contagem de findings por dimensão */
  dimensionStats: Record<AnalysisDimension, number>;

  /** Contagem de findings por severidade */
  severityStats: Record<FindingSeverity, number>;

  /** Score geral (0-100) */
  overallScore: number;

  /** Tempo de análise (ms) */
  analysisTimeMs: number;

  /** Erros durante análise */
  errors?: string[];
}

/**
 * Contexto interno de análise
 */
interface ReviewContext {
  input: CodeReviewInput;
  findings: CodeFinding[];
  startTime: number;
  analysisPrompt: string;
}

// ============================================================================
// CODE REVIEWER AGENT
// ============================================================================

export class CodeReviewerAgent {
  private client: Anthropic;
  private model = "claude-opus-4-1-20250805";

  /**
   * Inicializa o revisor de código
   */
  constructor(apiKey?: string) {
    this.client = new Anthropic({
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY,
    });
  }

  /**
   * Executa análise profunda de PR
   */
  async reviewCode(input: CodeReviewInput): Promise<CodeReviewOutput> {
    const startTime = Date.now();
    const context: ReviewContext = {
      input,
      findings: [],
      startTime,
      analysisPrompt: "",
    };

    try {
      // Prepara prompt de análise
      context.analysisPrompt = this.buildAnalysisPrompt(input);

      // Chama Opus para análise profunda
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 4096,
        messages: [
          {
            role: "user",
            content: context.analysisPrompt,
          },
        ],
      });

      // Extrai findings do response
      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";
      context.findings = this.parseFindings(responseText, input.agentPath);

      // Valida findings
      this.validateFindings(context.findings);

      // Gera sumarização
      const summary = this.generateSummary(context.findings);

      return {
        status: "success",
        findings: context.findings,
        summary,
        dimensionStats: this.calculateDimensionStats(context.findings),
        severityStats: this.calculateSeverityStats(context.findings),
        overallScore: this.calculateScore(context.findings),
        analysisTimeMs: Date.now() - startTime,
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      return {
        status: "failed",
        findings: context.findings,
        summary: `Análise falhou: ${errorMsg}`,
        dimensionStats: { correctness: 0, security: 0, performance: 0, style: 0 },
        severityStats: { info: 0, warning: 0, error: 0, critical: 0 },
        overallScore: 0,
        analysisTimeMs: Date.now() - startTime,
        errors: [errorMsg],
      };
    }
  }

  /**
   * Constrói prompt de análise estruturado
   */
  private buildAnalysisPrompt(input: CodeReviewInput): string {
    const dimensions = input.dimensions || [
      "correctness",
      "security",
      "performance",
      "style",
    ];
    const dimensionText = dimensions.join(", ");

    return `Você é um revisor de código expert. Analise o seguinte PR e novo agente:

**Contexto do PR:**
${input.prContext?.title ? `- Título: ${input.prContext.title}` : ""}
${input.prContext?.description ? `- Descrição: ${input.prContext.description}` : ""}
${input.prContext?.author ? `- Autor: ${input.prContext.author}` : ""}

**Diff da PR:**
\`\`\`diff
${input.prDiff}
\`\`\`

**Novo Agente/Código:**
\`\`\`typescript
${input.newAgentCode}
\`\`\`

**Dimensões a revisar:** ${dimensionText}

Forneça findings em formato JSON com esta estrutura:
\`\`\`json
{
  "findings": [
    {
      "file": "caminho/relativo.ts",
      "line": 42,
      "endLine": 45,
      "dimension": "correctness|security|performance|style",
      "severity": "info|warning|error|critical",
      "title": "Título curto",
      "description": "Descrição detalhada do problema",
      "suggestion": "Como corrigir",
      "code": "snippet do código problemático"
    }
  ]
}
\`\`\`

Siga estas regras:
1. Seja específico: cite linha, dimensão, severidade
2. Evite false positives: apenas problemas reais
3. Priorize critical > error > warning > info
4. Foque em PR diff antes que código inteiro
5. Retorne SEMPRE um JSON válido`;
  }

  /**
   * Extrai findings do response do Opus
   */
  private parseFindings(responseText: string, agentPath: string): CodeFinding[] {
    const findings: CodeFinding[] = [];

    try {
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return findings;

      const parsed = JSON.parse(jsonMatch[0]);
      if (!Array.isArray(parsed.findings)) return findings;

      for (const f of parsed.findings) {
        if (
          f.file &&
          typeof f.line === "number" &&
          f.dimension &&
          f.severity &&
          f.title
        ) {
          findings.push({
            file: f.file,
            line: f.line,
            endLine: f.endLine,
            dimension: f.dimension,
            severity: f.severity,
            title: f.title,
            description: f.description || "",
            suggestion: f.suggestion,
            code: f.code,
          });
        }
      }
    } catch {
      // Se JSON inválido, retorna array vazio
    }

    return findings;
  }

  /**
   * Valida integridade dos findings
   */
  private validateFindings(findings: CodeFinding[]): void {
    const validDimensions: AnalysisDimension[] = [
      "correctness",
      "security",
      "performance",
      "style",
    ];
    const validSeverities: FindingSeverity[] = [
      "info",
      "warning",
      "error",
      "critical",
    ];

    for (const f of findings) {
      if (!validDimensions.includes(f.dimension)) {
        f.dimension = "style";
      }
      if (!validSeverities.includes(f.severity)) {
        f.severity = "warning";
      }
      if (f.line < 1) f.line = 1;
      if (f.endLine && f.endLine < f.line) f.endLine = undefined;
    }
  }

  /**
   * Calcula estatísticas por dimensão
   */
  private calculateDimensionStats(
    findings: CodeFinding[]
  ): Record<AnalysisDimension, number> {
    const stats: Record<AnalysisDimension, number> = {
      correctness: 0,
      security: 0,
      performance: 0,
      style: 0,
    };

    for (const f of findings) {
      stats[f.dimension]++;
    }

    return stats;
  }

  /**
   * Calcula estatísticas por severidade
   */
  private calculateSeverityStats(
    findings: CodeFinding[]
  ): Record<FindingSeverity, number> {
    const stats: Record<FindingSeverity, number> = {
      info: 0,
      warning: 0,
      error: 0,
      critical: 0,
    };

    for (const f of findings) {
      stats[f.severity]++;
    }

    return stats;
  }

  /**
   * Calcula score geral (0-100)
   * Penalidades: critical -30, error -15, warning -5, info -1
   */
  private calculateScore(findings: CodeFinding[]): number {
    let score = 100;

    for (const f of findings) {
      switch (f.severity) {
        case "critical":
          score -= 30;
          break;
        case "error":
          score -= 15;
          break;
        case "warning":
          score -= 5;
          break;
        case "info":
          score -= 1;
          break;
      }
    }

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Gera sumarização dos findings (max 50 linhas)
   */
  private generateSummary(findings: CodeFinding[]): string {
    if (findings.length === 0) {
      return "✅ Nenhum finding detectado. Código está limpo!";
    }

    const grouped = this.groupByDimension(findings);
    const lines: string[] = [];

    lines.push(`📊 Análise de Código — ${findings.length} findings\n`);

    for (const [dimension, dimensionFindings] of Object.entries(grouped)) {
      if (dimensionFindings.length === 0) continue;

      const severityCount = this.countBySeverity(dimensionFindings);
      const criticals = dimensionFindings.filter((f) => f.severity === "critical");
      const errors = dimensionFindings.filter((f) => f.severity === "error");

      lines.push(`## ${dimension.toUpperCase()}`);
      lines.push(
        `   ${severityCount.map((s) => `${s.count}x ${s.severity}`).join(" | ")}`
      );

      if (criticals.length > 0) {
        for (const f of criticals.slice(0, 2)) {
          lines.push(`   🔴 [L${f.line}] ${f.title}`);
        }
        if (criticals.length > 2) {
          lines.push(`   ... +${criticals.length - 2} critical(s)`);
        }
      }

      if (errors.length > 0) {
        for (const f of errors.slice(0, 2)) {
          lines.push(`   🟠 [L${f.line}] ${f.title}`);
        }
        if (errors.length > 2) {
          lines.push(`   ... +${errors.length - 2} error(s)`);
        }
      }

      lines.push("");
    }

    return lines.slice(0, 50).join("\n");
  }

  /**
   * Agrupa findings por dimensão
   */
  private groupByDimension(
    findings: CodeFinding[]
  ): Record<AnalysisDimension, CodeFinding[]> {
    const grouped: Record<AnalysisDimension, CodeFinding[]> = {
      correctness: [],
      security: [],
      performance: [],
      style: [],
    };

    for (const f of findings) {
      grouped[f.dimension].push(f);
    }

    return grouped;
  }

  /**
   * Conta findings por severidade
   */
  private countBySeverity(
    findings: CodeFinding[]
  ): Array<{ severity: FindingSeverity; count: number }> {
    const counts: Record<FindingSeverity, number> = {
      info: 0,
      warning: 0,
      error: 0,
      critical: 0,
    };

    for (const f of findings) {
      counts[f.severity]++;
    }

    return Object.entries(counts)
      .filter(([_, count]) => count > 0)
      .map(([severity, count]) => ({
        severity: severity as FindingSeverity,
        count,
      }));
  }
}

// ============================================================================
// EXPORTAÇÕES
// ============================================================================

export default CodeReviewerAgent;
