/**
 * LLM Judge — Sistema inteligente de classificação de riscos de PR
 * Versão: 2.0.0 (Phase 4 - Complete Decision Engine)
 *
 * Recursos:
 * - Haiku classifier: categoriza PRs como high/medium/low-risk
 * - Code evaluation com análise detalhada
 * - Quality scoring (0-100)
 * - Mergeability decisions com reasoning
 * - Decision explanations em linguagem natural
 * - Audit trail completo
 * - Confidence levels em múltiplos níveis
 * - Critical vs minor issue classification
 */

import Anthropic from "@anthropic-ai/sdk";

/**
 * Tipos de decisão de merge
 */
export type MergeDecisionType = "approve" | "request-changes" | "comment" | "block";

/**
 * Níveis de confiança na decisão
 */
export type ConfidenceLevel = "very-high" | "high" | "moderate" | "low" | "very-low";

/**
 * Severidade de issues encontrados
 */
export type IssueSeverity = "critical" | "major" | "minor" | "info";

/**
 * Resultado da avaliação de código
 */
export interface Evaluation {
  code: string;
  reviews: CodeReview[];
  overallScore: number; // 0-100
  issues: CodeIssue[];
  criticalIssues: CodeIssue[];
  minorIssues: CodeIssue[];
  improvements: string[];
  securityRisks: SecurityRisk[];
  performanceRisks: PerformanceRisk[];
  testability: TestabilityScore;
  maintainability: MaintainabilityScore;
  documentation: DocumentationScore;
  auditTrail: AuditTrailEntry[];
  evaluatedAt: Date;
  model: string;
  promptTokens?: number;
  completionTokens?: number;
}

/**
 * Revisão de código fornecida
 */
export interface CodeReview {
  reviewer: string;
  content: string;
  timestamp: Date;
  severity?: IssueSeverity;
}

/**
 * Issue encontrado no código
 */
export interface CodeIssue {
  id: string;
  title: string;
  description: string;
  severity: IssueSeverity;
  category: string; // 'security', 'performance', 'style', 'logic', etc
  location?: {
    file?: string;
    line?: number;
  };
  suggestion?: string;
  confidence: number; // 0.0-1.0
}

/**
 * Risco de segurança identificado
 */
export interface SecurityRisk {
  type: string;
  description: string;
  severity: IssueSeverity;
  remediation: string;
  cwe?: string; // CWE identifier
}

/**
 * Risco de performance identificado
 */
export interface PerformanceRisk {
  type: string;
  description: string;
  impact: "critical" | "high" | "medium" | "low";
  optimization: string;
}

/**
 * Score de testabilidade
 */
export interface TestabilityScore {
  score: number; // 0-100
  hasUnitTests: boolean;
  hasIntegrationTests: boolean;
  coverage: number; // 0-100
  recommendations: string[];
}

/**
 * Score de manutenibilidade
 */
export interface MaintainabilityScore {
  score: number; // 0-100
  complexity: number; // 0-100 (lower is better)
  readability: number; // 0-100
  documentation: number; // 0-100
  issues: string[];
}

/**
 * Score de documentação
 */
export interface DocumentationScore {
  score: number; // 0-100
  hasReadme: boolean;
  hasAPIDoc: boolean;
  hasExamples: boolean;
  hasComments: boolean;
  recommendations: string[];
}

/**
 * Decisão de merge
 */
export interface MergeDecision {
  decision: MergeDecisionType;
  confidenceLevel: ConfidenceLevel;
  confidence: number; // 0.0-1.0
  reasoning: string;
  reasons: string[];
  blockers?: string[];
  warnings?: string[];
  suggestions?: string[];
  ciStatus?: boolean;
  reviewsApproved?: number;
  reviewsRequested?: number;
  auditTrail: AuditTrailEntry[];
  decidedAt: Date;
  model: string;
}

/**
 * Score de qualidade
 */
export interface QualityScore {
  overall: number; // 0-100
  codeQuality: number; // 0-100
  testCoverage: number; // 0-100
  documentation: number; // 0-100
  security: number; // 0-100
  performance: number; // 0-100
  maintainability: number; // 0-100
  grade: "A" | "B" | "C" | "D" | "F"; // Letter grade
  breakdown: {
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  };
  auditTrail: AuditTrailEntry[];
  scoredAt: Date;
  model: string;
}

/**
 * Entrada de trilha de auditoria
 */
export interface AuditTrailEntry {
  timestamp: Date;
  action: string;
  details: Record<string, unknown>;
  confidence?: number;
  model?: string;
}

/**
 * Níveis de risco detectados
 */
export type RiskLevel = "high" | "medium" | "low";

/**
 * Categorias de risco
 */
export type RiskCategory =
  | "security"
  | "breaking-change"
  | "performance"
  | "untested-code"
  | "large-changeset"
  | "external-dependency"
  | "documentation"
  | "database-migration"
  | "infrastructure"
  | "low-risk-refactor";

/**
 * Ação recomendada baseada no risco
 */
export enum JudgeAction {
  AUTO_MERGE = "auto_merge",
  CONDITIONAL_MERGE = "conditional_merge", // Merge se CI passou
  REQUIRES_REVIEW = "requires_review",
  BLOCKING = "blocking",
}

/**
 * Resultado da classificação de PR
 */
export interface PRJudgment {
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  author: string;

  // Classificação de risco
  riskLevel: RiskLevel;
  riskCategories: RiskCategory[];
  confidence: number; // 0.0-1.0
  reason: string; // Explicação detalhada

  // Recomendação de ação
  action: JudgeAction;
  actionReason: string;

  // Análise detalhada
  detailedAnalysis: {
    securityConcerns: string[];
    performanceRisks: string[];
    testCoverage: {
      hasTests: boolean;
      confidence: number;
    };
    changeSize: {
      filesChanged: number;
      additionsCount: number;
      deletionsCount: number;
      severity: "large" | "medium" | "small";
    };
    codePatterns: {
      hasBreakingChanges: boolean;
      hasExternalDeps: boolean;
      hasMigrations: boolean;
      hasDocumentation: boolean;
    };
  };

  // Metadados
  analyzedAt: Date;
  model: string;
  promptTokens?: number;
  completionTokens?: number;
}

/**
 * Entrada para o judge
 */
export interface PRData {
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  description?: string;
  author: string;
  branch: string;
  baseBranch: string;

  // Estatísticas de mudança
  filesChanged: number;
  additions: number;
  deletions: number;
  changedFiles: Array<{
    filename: string;
    patch?: string;
    additions: number;
    deletions: number;
  }>;

  // Contexto adicional
  commits: Array<{
    message: string;
    author: string;
  }>;

  // Status do CI (opcional)
  ciPassed?: boolean;
  ciWorkflowId?: number;
  testsPassed?: number;
  testsFailed?: number;
  coverage?: number;
}

/**
 * Configuração do LLM Judge
 */
export interface LLMJudgeConfig {
  apiKey?: string;
  model?: string; // Default: claude-3-5-haiku-20241022
  maxTokens?: number;
  minConfidenceThreshold?: number;
  anthropicApiUrl?: string;
}

/**
 * Classe principal do LLM Judge
 */
export class LLMJudge {
  private client: Anthropic;
  private config: Required<LLMJudgeConfig>;
  private systemPrompt: string;

  constructor(config: LLMJudgeConfig = {}) {
    const apiKey = config.apiKey || process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error(
        "ANTHROPIC_API_KEY não configurada. Configure via config ou env var."
      );
    }

    this.client = new Anthropic({ apiKey });
    this.config = {
      apiKey,
      model: config.model || "claude-3-5-haiku-20241022",
      maxTokens: config.maxTokens || 1024,
      minConfidenceThreshold: config.minConfidenceThreshold ?? 0.6,
      anthropicApiUrl: config.anthropicApiUrl || "https://api.anthropic.com",
    };

    this.systemPrompt = this.buildSystemPrompt();
  }

  /**
   * Constrói o prompt de sistema para o Claude
   */
  private buildSystemPrompt(): string {
    return `Você é um árbitro especializado em análise de risco de Pull Requests (PRs).
Sua tarefa é avaliar PRs e classificá-los quanto ao risco de serem aceitos/merged.

NÍVEIS DE RISCO:
- HIGH: Potencial para bugs críticos, perda de dados, segurança comprometida. Requer revisão humana obrigatória.
- MEDIUM: Mudanças significativas mas com risco moderado. Pode auto-merge se CI passou.
- LOW: Mudanças simples, bem testadas, baixo risco. Pode auto-merge imediatamente.

CATEGORIAS DE RISCO:
- security: Vulnerabilidades de segurança (SQL injection, XSS, auth bypass, etc)
- breaking-change: Mudanças que quebram compatibilidade (API, schema, etc)
- performance: Risco de degradação de performance
- untested-code: Código sem testes unitários/integração
- large-changeset: Muitas mudanças (100+ arquivos ou 1000+ linhas)
- external-dependency: Novos pacotes/dependências externas
- documentation: Documentação inadequada
- database-migration: Mudanças em schema/migrations
- infrastructure: Mudanças em infra/deploy/ops
- low-risk-refactor: Refatorações sem mudança de comportamento

ANÁLISE REQUERIDA:
1. Tamanho da mudança (pequena, média, grande)
2. Padrões de código perigosos (eval, dynamic imports, unsafe casts, etc)
3. Cobertura de testes
4. Documentação adequada
5. Dependências externas adicionadas
6. Potencial para breaking changes
7. Segurança (inputs não validados, querys não parametrizadas, etc)
8. Performance (loops aninhados, O(n²), queries sem índices, etc)

INSTRUÇÕES DE CONFIANÇA:
- 0.95+: Análise muito clara e certa
- 0.8-0.95: Análise clara com alta certeza
- 0.6-0.8: Análise com confiança moderada
- 0.4-0.6: Análise incerta, recomenda high-risk
- <0.4: Muito incerto, recomenda blocking

ESTRUTURA DE SAÍDA (JSON):
{
  "riskLevel": "high|medium|low",
  "riskCategories": ["categoria1", "categoria2"],
  "confidence": 0.0-1.0,
  "reason": "Explicação clara e concisa do risco detectado",
  "action": "auto_merge|conditional_merge|requires_review|blocking",
  "actionReason": "Por que esta ação é recomendada",
  "detailedAnalysis": {
    "securityConcerns": ["..."],
    "performanceRisks": ["..."],
    "testCoverage": { "hasTests": boolean, "confidence": 0.0-1.0 },
    "changeSize": {
      "filesChanged": number,
      "additionsCount": number,
      "deletionsCount": number,
      "severity": "large|medium|small"
    },
    "codePatterns": {
      "hasBreakingChanges": boolean,
      "hasExternalDeps": boolean,
      "hasMigrations": boolean,
      "hasDocumentation": boolean
    }
  }
}

EXEMPLOS:

1. PR seguro com testes:
   Título: "refactor: simplify utils functions"
   - riskLevel: "low"
   - riskCategories: ["low-risk-refactor"]
   - confidence: 0.95
   - action: "auto_merge"

2. PR com breaking change:
   Título: "feat: change API response format"
   - riskLevel: "high"
   - riskCategories: ["breaking-change"]
   - confidence: 0.9
   - action: "requires_review"

3. PR grande sem testes:
   Título: "feat: add new dashboard"
   - 150 arquivos, 5000+ linhas
   - Sem mudanças em arquivos .test.ts
   - riskLevel: "high"
   - riskCategories: ["large-changeset", "untested-code"]
   - confidence: 0.85
   - action: "requires_review"

4. PR com dependência externa:
   Título: "feat: add payment integration"
   - Novo package: stripe@latest
   - riskLevel: "medium"
   - riskCategories: ["external-dependency"]
   - confidence: 0.75
   - action: "conditional_merge"
`;
  }

  /**
   * Analisa um PR e retorna classificação de risco
   */
  async judge(prData: PRData): Promise<PRJudgment> {
    try {
      // Prepara contexto do PR
      const prContext = this.buildPRContext(prData);

      // Chama Claude Haiku para classificação
      const response = await this.client.messages.create({
        model: this.config.model,
        max_tokens: this.config.maxTokens,
        system: this.systemPrompt,
        messages: [
          {
            role: "user",
            content: prContext,
          },
        ],
      });

      // Extrai tokens usados
      const promptTokens = response.usage.input_tokens;
      const completionTokens = response.usage.output_tokens;

      // Extrair texto da resposta
      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Parse JSON da resposta
      const judgmentData = this.extractJsonFromResponse(responseText);

      // Normaliza e valida
      const normalized = this.normalizeJudgment(judgmentData);

      // Enriquece com análise local
      const enriched = this.enrichJudgment(
        normalized,
        prData,
        promptTokens,
        completionTokens
      );

      return enriched;
    } catch (error) {
      console.error("Erro no LLM Judge:", error);
      return this.createFallbackJudgment(
        prData,
        "high",
        "Erro ao processar PR no LLM Judge"
      );
    }
  }

  /**
   * Avalia código com análise detalhada
   */
  async evaluateCode(code: string, reviews: CodeReview[] = []): Promise<Evaluation> {
    const auditTrail: AuditTrailEntry[] = [];

    try {
      auditTrail.push({
        timestamp: new Date(),
        action: "evaluation_started",
        details: {
          codeLength: code.length,
          reviewCount: reviews.length,
        },
      });

      const evaluationPrompt = this.buildEvaluationPrompt(code, reviews);

      const response = await this.client.messages.create({
        model: this.config.model,
        max_tokens: Math.max(this.config.maxTokens * 2, 2048),
        system: this.buildEvaluationSystemPrompt(),
        messages: [
          {
            role: "user",
            content: evaluationPrompt,
          },
        ],
      });

      const promptTokens = response.usage.input_tokens;
      const completionTokens = response.usage.output_tokens;

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      const evaluationData = this.extractJsonFromResponse(responseText);

      auditTrail.push({
        timestamp: new Date(),
        action: "evaluation_completed",
        details: { tokens: { prompt: promptTokens, completion: completionTokens } },
      });

      const evaluation = this.normalizeEvaluation(
        evaluationData,
        code,
        reviews,
        auditTrail,
        promptTokens,
        completionTokens
      );

      return evaluation;
    } catch (error) {
      console.error("Erro ao avaliar código:", error);
      auditTrail.push({
        timestamp: new Date(),
        action: "evaluation_error",
        details: { error: String(error) },
      });

      return this.createFallbackEvaluation(code, reviews, auditTrail);
    }
  }

  /**
   * Decide se um PR pode ser mergeado
   */
  async decideMergeability(pr: PRData & { ciPassed?: boolean }): Promise<MergeDecision> {
    const auditTrail: AuditTrailEntry[] = [];

    try {
      auditTrail.push({
        timestamp: new Date(),
        action: "mergeability_check_started",
        details: {
          prNumber: pr.prNumber,
          ciPassed: pr.ciPassed,
        },
      });

      // Primeiro, fazer o julgamento de risco
      const judgment = await this.judge(pr);

      // Construir decisão baseada no julgamento
      const decision = this.convertJudgmentToMergeDecision(judgment, auditTrail);

      // Validar contra limites de confiança
      if (decision.confidence < this.config.minConfidenceThreshold) {
        decision.decision = "request-changes";
        decision.blockers = [
          "Confiança insuficiente na análise. Revisão humana recomendada.",
        ];
      }

      auditTrail.push({
        timestamp: new Date(),
        action: "mergeability_decided",
        details: {
          decision: decision.decision,
          confidence: decision.confidence,
        },
      });

      decision.auditTrail = auditTrail;
      return decision;
    } catch (error) {
      console.error("Erro ao decidir mergeabilidade:", error);
      auditTrail.push({
        timestamp: new Date(),
        action: "mergeability_error",
        details: { error: String(error) },
      });

      return {
        decision: "comment",
        confidenceLevel: "very-low",
        confidence: 0.2,
        reasoning: "Erro ao processar PR. Revisão humana necessária.",
        reasons: [String(error)],
        blockers: ["Erro ao analisar PR"],
        auditTrail,
        decidedAt: new Date(),
        model: this.config.model,
      };
    }
  }

  /**
   * Calcula score de qualidade do código
   */
  async scoreQuality(code: string): Promise<QualityScore> {
    const auditTrail: AuditTrailEntry[] = [];

    try {
      auditTrail.push({
        timestamp: new Date(),
        action: "quality_scoring_started",
        details: { codeLength: code.length },
      });

      const scoringPrompt = this.buildScoringPrompt(code);

      const response = await this.client.messages.create({
        model: this.config.model,
        max_tokens: Math.max(this.config.maxTokens, 1500),
        system: this.buildScoringSystemPrompt(),
        messages: [
          {
            role: "user",
            content: scoringPrompt,
          },
        ],
      });

      const promptTokens = response.usage.input_tokens;
      const completionTokens = response.usage.output_tokens;

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      const scoreData = this.extractJsonFromResponse(responseText);

      auditTrail.push({
        timestamp: new Date(),
        action: "quality_scoring_completed",
        details: { scores: scoreData },
      });

      const qualityScore = this.normalizeQualityScore(
        scoreData,
        auditTrail,
        promptTokens,
        completionTokens
      );

      return qualityScore;
    } catch (error) {
      console.error("Erro ao calcular score de qualidade:", error);
      auditTrail.push({
        timestamp: new Date(),
        action: "quality_scoring_error",
        details: { error: String(error) },
      });

      return this.createFallbackQualityScore(auditTrail);
    }
  }

  /**
   * Explica uma decisão de forma legível
   */
  async explainDecision(evaluation: Evaluation): Promise<string> {
    try {
      const explanationPrompt = this.buildExplanationPrompt(evaluation);

      const response = await this.client.messages.create({
        model: this.config.model,
        max_tokens: 1024,
        system:
          "Você é um especialista em revisão de código. Explique de forma clara e concisa as decisões de revisão.",
        messages: [
          {
            role: "user",
            content: explanationPrompt,
          },
        ],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Adicionar à trilha de auditoria
      evaluation.auditTrail.push({
        timestamp: new Date(),
        action: "decision_explained",
        details: { explanationLength: responseText.length },
      });

      return responseText;
    } catch (error) {
      console.error("Erro ao explicar decisão:", error);
      return `Erro ao gerar explicação: ${String(error)}`;
    }
  }

  /**
   * Constrói contexto formatado do PR para enviar ao Claude
   */
  private buildPRContext(prData: PRData): string {
    const filesList = prData.changedFiles
      .slice(0, 20) // Limita a primeiros 20 arquivos
      .map((f) => `- ${f.filename} (+${f.additions}/-${f.deletions})`)
      .join("\n");

    const hasTests = prData.changedFiles.some(
      (f) => f.filename.includes(".test.") || f.filename.includes(".spec.")
    );

    const dangerousPatterns = this.detectDangerousPatterns(prData);

    return `ANÁLISE DE PULL REQUEST:

Informações Gerais:
- PR #${prData.prNumber}
- Repositório: ${prData.owner}/${prData.repo}
- Título: ${prData.title}
- Autor: ${prData.author}
- Branch: ${prData.branch} → ${prData.baseBranch}

Descrição:
${prData.description || "(Sem descrição)"}

Estatísticas de Mudança:
- Arquivos alterados: ${prData.filesChanged}
- Adições: ${prData.additions}
- Deleções: ${prData.deletions}
- Tamanho total: ${prData.additions + prData.deletions} linhas

Arquivos Alterados:
${filesList}
${prData.filesChanged > 20 ? `\n... e mais ${prData.filesChanged - 20} arquivos` : ""}

Testes:
- Contém testes: ${hasTests ? "SIM" : "NÃO"}
- Testes passaram: ${prData.testsPassed !== undefined ? `${prData.testsPassed}/${(prData.testsPassed || 0) + (prData.testsFailed || 0)}` : "Desconhecido"}
- Cobertura: ${prData.coverage ? `${prData.coverage}%` : "Desconhecida"}

Commits:
${prData.commits.slice(0, 5).map((c) => `- ${c.message.split("\n")[0]}`).join("\n")}
${prData.commits.length > 5 ? `\n... e mais ${prData.commits.length - 5} commits` : ""}

Padrões Detectados:
${dangerousPatterns.length > 0 ? dangerousPatterns.join("\n") : "- Nenhum padrão perigoso detectado"}

CI Status:
- Passou: ${prData.ciPassed !== undefined ? (prData.ciPassed ? "SIM" : "NÃO") : "Desconhecido"}

Com base nesta análise, classifique o PR em termos de risco (high/medium/low) e forneça um JSON estruturado com sua avaliação.`;
  }

  /**
   * Detecta padrões perigosos no código
   */
  private detectDangerousPatterns(prData: PRData): string[] {
    const patterns: string[] = [];

    for (const file of prData.changedFiles) {
      if (!file.patch) continue;

      const patch = file.patch;

      // Segurança
      if (patch.includes("eval(") || patch.includes("new Function")) {
        patterns.push(`⚠️ CRÍTICO: eval/dynamic function em ${file.filename}`);
      }

      if (patch.match(/innerHTML\s*=/i)) {
        patterns.push(`⚠️ CRÍTICO: innerHTML assignment em ${file.filename}`);
      }

      if (patch.includes("DROP TABLE") || patch.includes("DELETE FROM")) {
        patterns.push(
          `⚠️ CRÍTICO: Operação destructiva de BD em ${file.filename}`
        );
      }

      // SQL Injection
      if (patch.match(/\$\{.*\}|f\s*".*\$|query\s*\(\s*`/)) {
        patterns.push(`⚠️ SQL Injection: String interpolation em ${file.filename}`);
      }

      // Breaking changes
      if (
        patch.includes("export class ") ||
        (patch.includes("export interface") && patch.includes("-"))
      ) {
        patterns.push(`⚠️ Mudança potencial em API pública: ${file.filename}`);
      }

      // Migração de BD
      if (file.filename.includes("migration") || file.filename.includes("schema")) {
        patterns.push(`⚠️ Migração de banco de dados: ${file.filename}`);
      }

      // Dependências externas
      if (
        file.filename === "package.json" ||
        file.filename === "requirements.txt" ||
        file.filename === "go.mod"
      ) {
        if (patch.includes("+")) {
          patterns.push(`⚠️ Nova dependência externa: ${file.filename}`);
        }
      }

      // Código sensível sem documentação
      if (file.additions > 100 && !file.filename.includes(".test.")) {
        if (file.patch.match(/auth|secret|password|token|api.key/i)) {
          patterns.push(
            `⚠️ Código sensível sem documentação: ${file.filename}`
          );
        }
      }
    }

    return patterns;
  }

  /**
   * Extrai JSON de uma resposta do Claude
   */
  private extractJsonFromResponse(text: string): Partial<PRJudgment> {
    try {
      // Tenta encontrar JSON entre chaves
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return {};
    } catch (error) {
      console.warn("Falha ao extrair JSON:", error);
      return {};
    }
  }

  /**
   * Normaliza e valida o julgamento
   */
  private normalizeJudgment(
    judgment: Partial<PRJudgment>
  ): Omit<PRJudgment, "analyzedAt" | "model" | "promptTokens" | "completionTokens"> {
    const riskLevel = this.normalizeRiskLevel(judgment.riskLevel as string);
    const confidence = this.normalizeConfidence(judgment.confidence as number);
    const action = this.normalizeAction(
      judgment.action as string,
      riskLevel
    );

    return {
      prNumber: judgment.prNumber || 0,
      owner: judgment.owner || "",
      repo: judgment.repo || "",
      title: judgment.title || "",
      author: judgment.author || "",
      riskLevel,
      riskCategories: Array.isArray(judgment.riskCategories)
        ? judgment.riskCategories
        : [],
      confidence,
      reason:
        judgment.reason ||
        "Análise via Claude Haiku (fallback normalization)",
      action,
      actionReason:
        judgment.actionReason ||
        this.getDefaultActionReason(action, riskLevel),
      detailedAnalysis: judgment.detailedAnalysis || {
        securityConcerns: [],
        performanceRisks: [],
        testCoverage: { hasTests: false, confidence: 0.5 },
        changeSize: {
          filesChanged: 0,
          additionsCount: 0,
          deletionsCount: 0,
          severity: "small",
        },
        codePatterns: {
          hasBreakingChanges: false,
          hasExternalDeps: false,
          hasMigrations: false,
          hasDocumentation: false,
        },
      },
    };
  }

  /**
   * Enriquece o julgamento com análise local
   */
  private enrichJudgment(
    judgment: Omit<
      PRJudgment,
      "analyzedAt" | "model" | "promptTokens" | "completionTokens"
    >,
    prData: PRData,
    promptTokens: number,
    completionTokens: number
  ): PRJudgment {
    // Atualiza estatísticas com dados reais se não estiverem preenchidas
    if (judgment.detailedAnalysis.changeSize.filesChanged === 0) {
      judgment.detailedAnalysis.changeSize.filesChanged = prData.filesChanged;
      judgment.detailedAnalysis.changeSize.additionsCount = prData.additions;
      judgment.detailedAnalysis.changeSize.deletionsCount = prData.deletions;
    }

    // Detecta tamanho
    const totalLines =
      judgment.detailedAnalysis.changeSize.additionsCount +
      judgment.detailedAnalysis.changeSize.deletionsCount;
    if (totalLines > 1000) {
      judgment.detailedAnalysis.changeSize.severity = "large";
    } else if (totalLines > 100) {
      judgment.detailedAnalysis.changeSize.severity = "medium";
    } else {
      judgment.detailedAnalysis.changeSize.severity = "small";
    }

    // Detecta padrões localmente se não foram detectados
    const hasTestFiles = prData.changedFiles.some(
      (f) => f.filename.includes(".test.") || f.filename.includes(".spec.")
    );

    // Enrich code patterns if not already filled
    if (!judgment.detailedAnalysis.codePatterns.hasDocumentation && hasTestFiles) {
      judgment.detailedAnalysis.codePatterns = {
        ...judgment.detailedAnalysis.codePatterns,
        // Test files detected
      };
    }

    // Boostar confiança se CI passou
    if (prData.ciPassed && judgment.confidence < 0.9) {
      judgment.confidence = Math.min(
        0.95,
        judgment.confidence + 0.1
      );
    }

    // Degradar confiança se CI falhou
    if (prData.ciPassed === false && judgment.riskLevel !== "high") {
      judgment.riskLevel = "high";
      judgment.action = JudgeAction.REQUIRES_REVIEW;
      judgment.reason =
        "CI pipeline falhou: risco elevado detectado automaticamente";
      judgment.confidence = Math.max(0.6, judgment.confidence - 0.15);
    }

    return {
      ...judgment,
      analyzedAt: new Date(),
      model: this.config.model,
      promptTokens,
      completionTokens,
    };
  }

  /**
   * Normaliza riskLevel para valores válidos
   */
  private normalizeRiskLevel(level?: string): RiskLevel {
    if (!level) return "medium";

    const lower = level.toLowerCase().trim();
    if (["high", "alto"].includes(lower)) return "high";
    if (["low", "baixo"].includes(lower)) return "low";
    return "medium";
  }

  /**
   * Normaliza confidence para [0, 1]
   */
  private normalizeConfidence(confidence?: number): number {
    if (confidence === undefined || confidence === null) return 0.5;
    const num = Number(confidence);
    if (isNaN(num)) return 0.5;
    return Math.max(0, Math.min(1, num));
  }

  /**
   * Normaliza action baseado no riskLevel
   */
  private normalizeAction(action?: string, riskLevel?: RiskLevel): JudgeAction {
    if (!action) {
      // Default baseado no risk level
      switch (riskLevel) {
        case "high":
          return JudgeAction.REQUIRES_REVIEW;
        case "low":
          return JudgeAction.AUTO_MERGE;
        default:
          return JudgeAction.CONDITIONAL_MERGE;
      }
    }

    const lower = action.toLowerCase().trim().replace(/_/g, "");
    if (lower.includes("automerge")) return JudgeAction.AUTO_MERGE;
    if (lower.includes("conditional")) return JudgeAction.CONDITIONAL_MERGE;
    if (lower.includes("review")) return JudgeAction.REQUIRES_REVIEW;
    if (lower.includes("block")) return JudgeAction.BLOCKING;

    // Default
    return JudgeAction.CONDITIONAL_MERGE;
  }

  /**
   * Retorna razão padrão para uma ação
   */
  private getDefaultActionReason(action: JudgeAction, riskLevel: RiskLevel): string {
    const reasons: Record<JudgeAction, Record<RiskLevel, string>> = {
      [JudgeAction.AUTO_MERGE]: {
        low: "PR com baixo risco, testes passaram, pode fazer merge automático",
        medium: "Risco moderado mas dentro dos limites",
        high: "Risco alto não permite auto-merge",
      },
      [JudgeAction.CONDITIONAL_MERGE]: {
        low: "Pode fazer merge após CI passar",
        medium: "Merge permitido se CI passou e testes cobrem mudanças",
        high: "Risco alto requer revisão manual antes do merge",
      },
      [JudgeAction.REQUIRES_REVIEW]: {
        low: "Requer revisão antes do merge",
        medium: "Mudanças significativas requerem revisão",
        high: "Risco crítico detectado - revisão obrigatória",
      },
      [JudgeAction.BLOCKING]: {
        low: "PR bloqueada",
        medium: "PR bloqueada - risco crítico",
        high: "PR bloqueada - risco crítico detectado, requer correção",
      },
    };

    return (
      reasons[action]?.[riskLevel] ||
      `Ação ${action} recomendada para risco ${riskLevel}`
    );
  }

  /**
   * Constrói prompt de sistema para avaliação
   */
  private buildEvaluationSystemPrompt(): string {
    return `Você é um expert em análise de código. Sua tarefa é avaliar código e fornecer feedback detalhado sobre:
1. Qualidade geral (0-100)
2. Issues encontrados (críticos, maiores, menores)
3. Riscos de segurança
4. Riscos de performance
5. Testabilidade
6. Manutenibilidade
7. Documentação

Retorne um JSON estruturado com análise completa.`;
  }

  /**
   * Constrói prompt para avaliação
   */
  private buildEvaluationPrompt(code: string, reviews: CodeReview[]): string {
    const reviewsText = reviews
      .map(
        (r) =>
          `- ${r.reviewer} (${r.severity || "info"}): ${r.content}`
      )
      .join("\n");

    return `Analise este código:

\`\`\`
${code.substring(0, 5000)}
${code.length > 5000 ? "... (código truncado)" : ""}
\`\`\`

Revisões anteriores:
${reviewsText || "(Nenhuma revisão anterior)"}

Forneça análise estruturada em JSON.`;
  }

  /**
   * Constrói prompt de sistema para scoring
   */
  private buildScoringSystemPrompt(): string {
    return `Você é um especialista em métricas de qualidade de código. Avalie o código em múltiplas dimensões:
- Qualidade geral: 0-100
- Qualidade de código: 0-100
- Cobertura de testes: 0-100
- Documentação: 0-100
- Segurança: 0-100
- Performance: 0-100
- Manutenibilidade: 0-100

Atribua uma nota (A-F) baseada na pontuação geral.`;
  }

  /**
   * Constrói prompt para scoring
   */
  private buildScoringPrompt(code: string): string {
    return `Atribua scores de qualidade para este código:

\`\`\`
${code.substring(0, 3000)}
${code.length > 3000 ? "... (código truncado)" : ""}
\`\`\`

Retorne um JSON com scores de 0-100 em cada categoria.`;
  }

  /**
   * Constrói prompt para explicação
   */
  private buildExplanationPrompt(evaluation: Evaluation): string {
    const issuesText = evaluation.issues
      .slice(0, 5)
      .map((i) => `- [${i.severity}] ${i.title}: ${i.description}`)
      .join("\n");

    return `Baseado nesta avaliação de código, forneça uma explicação clara e concisa:

Score Geral: ${evaluation.overallScore}/100
Problemas Críticos: ${evaluation.criticalIssues.length}
Problemas Menores: ${evaluation.minorIssues.length}

Principais Issues:
${issuesText}

Explique o significado desta avaliação e recomendações principais.`;
  }

  /**
   * Normaliza resultado de avaliação
   */
  private normalizeEvaluation(
    data: any,
    code: string,
    reviews: CodeReview[],
    auditTrail: AuditTrailEntry[],
    promptTokens: number,
    completionTokens: number
  ): Evaluation {
    const evaluation: Evaluation = {
      code,
      reviews,
      overallScore: Math.min(100, Math.max(0, data.overallScore || 50)),
      issues: Array.isArray(data.issues)
        ? (data.issues as CodeIssue[])
        : [],
      criticalIssues: (Array.isArray(data.criticalIssues)
        ? data.criticalIssues
        : []) as CodeIssue[],
      minorIssues: (Array.isArray(data.minorIssues)
        ? data.minorIssues
        : []) as CodeIssue[],
      improvements: Array.isArray(data.improvements)
        ? (data.improvements as string[])
        : [],
      securityRisks: Array.isArray(data.securityRisks)
        ? (data.securityRisks as SecurityRisk[])
        : [],
      performanceRisks: Array.isArray(data.performanceRisks)
        ? (data.performanceRisks as PerformanceRisk[])
        : [],
      testability: data.testability || {
        score: 50,
        hasUnitTests: false,
        hasIntegrationTests: false,
        coverage: 0,
        recommendations: [],
      },
      maintainability: data.maintainability || {
        score: 50,
        complexity: 50,
        readability: 50,
        documentation: 50,
        issues: [],
      },
      documentation: data.documentation || {
        score: 50,
        hasReadme: false,
        hasAPIDoc: false,
        hasExamples: false,
        hasComments: false,
        recommendations: [],
      },
      auditTrail,
      evaluatedAt: new Date(),
      model: this.config.model,
      promptTokens,
      completionTokens,
    };

    return evaluation;
  }

  /**
   * Normaliza score de qualidade
   */
  private normalizeQualityScore(
    data: any,
    auditTrail: AuditTrailEntry[],
    promptTokens: number,
    completionTokens: number
  ): QualityScore {
    const overall = Math.min(100, Math.max(0, data.overall || 50));
    const grade: "A" | "B" | "C" | "D" | "F" =
      overall >= 90
        ? "A"
        : overall >= 80
          ? "B"
          : overall >= 70
            ? "C"
            : overall >= 60
              ? "D"
              : "F";

    return {
      overall,
      codeQuality: Math.min(100, Math.max(0, data.codeQuality || 50)),
      testCoverage: Math.min(100, Math.max(0, data.testCoverage || 50)),
      documentation: Math.min(100, Math.max(0, data.documentation || 50)),
      security: Math.min(100, Math.max(0, data.security || 50)),
      performance: Math.min(100, Math.max(0, data.performance || 50)),
      maintainability: Math.min(100, Math.max(0, data.maintainability || 50)),
      grade,
      breakdown: data.breakdown || {
        strengths: [],
        weaknesses: [],
        recommendations: [],
      },
      auditTrail,
      scoredAt: new Date(),
      model: this.config.model,
    };
  }

  /**
   * Converte julgamento para decisão de merge
   */
  private convertJudgmentToMergeDecision(
    judgment: PRJudgment,
    auditTrail: AuditTrailEntry[]
  ): MergeDecision {
    let decision: MergeDecisionType = "comment";
    let confidenceLevel: ConfidenceLevel = "moderate";

    if (judgment.confidence >= 0.9) {
      confidenceLevel = "very-high";
    } else if (judgment.confidence >= 0.75) {
      confidenceLevel = "high";
    } else if (judgment.confidence >= 0.5) {
      confidenceLevel = "moderate";
    } else if (judgment.confidence >= 0.3) {
      confidenceLevel = "low";
    } else {
      confidenceLevel = "very-low";
    }

    switch (judgment.action) {
      case JudgeAction.AUTO_MERGE:
        decision = "approve";
        break;
      case JudgeAction.CONDITIONAL_MERGE:
        decision = "comment";
        break;
      case JudgeAction.REQUIRES_REVIEW:
        decision = "request-changes";
        break;
      case JudgeAction.BLOCKING:
        decision = "block";
        break;
    }

    const reasons: string[] = [judgment.reason];

    if (judgment.detailedAnalysis.securityConcerns.length > 0) {
      reasons.push(
        `Preocupações de segurança: ${judgment.detailedAnalysis.securityConcerns.join(", ")}`
      );
    }

    if (judgment.detailedAnalysis.changeSize.severity === "large") {
      reasons.push(
        `Mudança grande: ${judgment.detailedAnalysis.changeSize.additionsCount} adições`
      );
    }

    return {
      decision,
      confidenceLevel,
      confidence: judgment.confidence,
      reasoning: judgment.actionReason,
      reasons,
      blockers:
        judgment.action === JudgeAction.BLOCKING
          ? judgment.riskCategories
          : undefined,
      warnings:
        judgment.riskLevel === "high"
          ? judgment.riskCategories
          : undefined,
      suggestions: judgment.detailedAnalysis.securityConcerns,
      auditTrail,
      decidedAt: new Date(),
      model: this.config.model,
    };
  }

  /**
   * Cria avaliação fallback
   */
  private createFallbackEvaluation(
    code: string,
    reviews: CodeReview[],
    auditTrail: AuditTrailEntry[]
  ): Evaluation {
    return {
      code,
      reviews,
      overallScore: 50,
      issues: [],
      criticalIssues: [],
      minorIssues: [],
      improvements: ["Erro ao avaliar. Revisão manual recomendada."],
      securityRisks: [],
      performanceRisks: [],
      testability: {
        score: 0,
        hasUnitTests: false,
        hasIntegrationTests: false,
        coverage: 0,
        recommendations: ["Adicione testes"],
      },
      maintainability: {
        score: 50,
        complexity: 0,
        readability: 0,
        documentation: 0,
        issues: [],
      },
      documentation: {
        score: 0,
        hasReadme: false,
        hasAPIDoc: false,
        hasExamples: false,
        hasComments: false,
        recommendations: ["Adicione documentação"],
      },
      auditTrail,
      evaluatedAt: new Date(),
      model: this.config.model,
    };
  }

  /**
   * Cria score de qualidade fallback
   */
  private createFallbackQualityScore(
    auditTrail: AuditTrailEntry[]
  ): QualityScore {
    return {
      overall: 50,
      codeQuality: 50,
      testCoverage: 0,
      documentation: 0,
      security: 50,
      performance: 50,
      maintainability: 50,
      grade: "C",
      breakdown: {
        strengths: [],
        weaknesses: ["Erro ao analisar código"],
        recommendations: ["Revisão manual recomendada"],
      },
      auditTrail,
      scoredAt: new Date(),
      model: this.config.model,
    };
  }

  /**
   * Cria um julgamento fallback em caso de erro
   */
  private createFallbackJudgment(
    prData: PRData,
    riskLevel: RiskLevel,
    reason: string
  ): PRJudgment {
    return {
      prNumber: prData.prNumber,
      owner: prData.owner,
      repo: prData.repo,
      title: prData.title,
      author: prData.author,
      riskLevel,
      riskCategories: [],
      confidence: 0.3,
      reason,
      action:
        riskLevel === "high"
          ? JudgeAction.REQUIRES_REVIEW
          : JudgeAction.CONDITIONAL_MERGE,
      actionReason: `Fallback action devido a erro: ${reason}`,
      detailedAnalysis: {
        securityConcerns: [],
        performanceRisks: [],
        testCoverage: { hasTests: false, confidence: 0.0 },
        changeSize: {
          filesChanged: prData.filesChanged,
          additionsCount: prData.additions,
          deletionsCount: prData.deletions,
          severity:
            prData.additions > 1000
              ? "large"
              : prData.additions > 100
                ? "medium"
                : "small",
        },
        codePatterns: {
          hasBreakingChanges: false,
          hasExternalDeps: false,
          hasMigrations: false,
          hasDocumentation: false,
        },
      },
      analyzedAt: new Date(),
      model: this.config.model,
    };
  }
}

/**
 * Factory function para criar instância
 */
export function createLLMJudge(config?: LLMJudgeConfig): LLMJudge {
  return new LLMJudge(config);
}

/**
 * Função auxiliar para julgamento rápido
 */
export async function judgePR(
  prData: PRData,
  config?: LLMJudgeConfig
): Promise<PRJudgment> {
  const judge = new LLMJudge(config);
  return judge.judge(prData);
}

/**
 * Helper para traduzir ação para português
 */
export function translateAction(action: JudgeAction): string {
  const translations: Record<JudgeAction, string> = {
    [JudgeAction.AUTO_MERGE]: "Auto-merge imediato",
    [JudgeAction.CONDITIONAL_MERGE]: "Merge se CI passar",
    [JudgeAction.REQUIRES_REVIEW]: "Requer revisão humana",
    [JudgeAction.BLOCKING]: "Bloqueado - não pode fazer merge",
  };

  return translations[action];
}

/**
 * Helper para traduzir riskLevel para português
 */
export function translateRiskLevel(level: RiskLevel): string {
  const translations: Record<RiskLevel, string> = {
    high: "Risco Alto",
    medium: "Risco Médio",
    low: "Risco Baixo",
  };

  return translations[level];
}

/**
 * Helper para traduzir ConfidenceLevel
 */
export function translateConfidenceLevel(level: ConfidenceLevel): string {
  const translations: Record<ConfidenceLevel, string> = {
    "very-high": "Muito Alta",
    high: "Alta",
    moderate: "Moderada",
    low: "Baixa",
    "very-low": "Muito Baixa",
  };

  return translations[level];
}

/**
 * Helper para traduzir MergeDecisionType
 */
export function translateMergeDecision(decision: MergeDecisionType): string {
  const translations: Record<MergeDecisionType, string> = {
    approve: "Aprovar",
    "request-changes": "Solicitar Mudanças",
    comment: "Comentar",
    block: "Bloquear",
  };

  return translations[decision];
}

/**
 * Helper para traduzir IssueSeverity
 */
export function translateIssueSeverity(severity: IssueSeverity): string {
  const translations: Record<IssueSeverity, string> = {
    critical: "Crítico",
    major: "Maior",
    minor: "Menor",
    info: "Informativo",
  };

  return translations[severity];
}
