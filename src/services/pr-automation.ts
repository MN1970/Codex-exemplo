/**
 * PR Automation Engine — Sistema inteligente de automação de PRs
 * Versão: 1.0.0
 *
 * Recursos:
 * - Auto-detecção de mudanças em PRs
 * - Parse de intent de commit messages
 * - Geração de sugestões de melhoria baseadas em padrões de código
 * - Trigger automático de CI/CD
 * - Monitoramento de build status e resultados de testes
 * - Integração com Supabase para persistência
 * - Análise de qualidade de código
 */

import { IntentParser, type ParsedIntent } from "./intent-parser";
import {
  CIOrchestratorService,
  type OrchestrationResult,
  type BuildOutput,
} from "./ci-orchestrator";

/**
 * Tipos de padrões de código detectados
 */
export type CodePatternType =
  | "complexity"
  | "duplication"
  | "missing-types"
  | "missing-tests"
  | "performance"
  | "security"
  | "accessibility"
  | "documentation";

/**
 * Severidade da sugestão
 */
export type SuggestionSeverity = "info" | "warning" | "critical";

/**
 * Status de análise de PR
 */
export enum PRAnalysisStatus {
  PENDING = "pending",
  ANALYZING = "analyzing",
  ANALYZED = "analyzed",
  TRIGGERING_CI = "triggering_ci",
  MONITORING_BUILD = "monitoring_build",
  COMPLETED = "completed",
  FAILED = "failed",
}

/**
 * Resultado da análise de PR
 */
export interface PRAnalysis {
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  description?: string;
  author: string;
  branch: string;
  baseBranch: string;
  status: PRAnalysisStatus;

  // Análise de código
  filesChanged: number;
  additions: number;
  deletions: number;
  changedFiles: Array<{
    filename: string;
    patch?: string;
    additions: number;
    deletions: number;
  }>;

  // Intent parsing
  commitIntent?: ParsedIntent;
  commitMessages: string[];

  // Padrões detectados
  codePatterns: DetectedPattern[];

  // Sugestões
  suggestions: Suggestion[];

  // CI/CD
  ciTriggered: boolean;
  workflowRunId?: number;
  buildStatus?: BuildStatus;

  // Metadados
  analyzedAt: Date;
  completedAt?: Date;
  duration?: number; // ms
  error?: string;
}

/**
 * Padrão de código detectado
 */
export interface DetectedPattern {
  type: CodePatternType;
  severity: SuggestionSeverity;
  file: string;
  line?: number;
  description: string;
  confidence: number; // 0.0-1.0
}

/**
 * Sugestão de melhoria
 */
export interface Suggestion {
  id: string;
  type: CodePatternType;
  severity: SuggestionSeverity;
  file?: string;
  title: string;
  description: string;
  recommendation: string;
  examples?: string[];
  confidence: number; // 0.0-1.0
}

/**
 * Status do build
 */
export interface BuildStatus {
  workflowRunId: number;
  status: "queued" | "in_progress" | "completed" | "failed" | "timed_out";
  conclusion?: string;
  passed: boolean;
  testsPassed?: number;
  testsFailed?: number;
  coverage?: number; // %
  duration?: number; // ms
  completedAt?: Date;
}

/**
 * Resultado de CI/CD
 */
export interface CIResult {
  success: boolean;
  workflowRunId: number;
  status: string;
  buildOutput: BuildOutput;
  duration: number;
  timestamp: Date;
  error?: string;
}

/**
 * Contexto para geração de sugestões
 */
export interface CodeContext {
  fileName: string;
  language: string;
  code: string;
  metrics?: {
    complexity: number;
    linesOfCode: number;
    functionsCount: number;
    averageFunctionLength: number;
  };
}

/**
 * Configuração do PR Automation Engine
 */
export interface PRAutomationConfig {
  githubToken: string;
  owner: string;
  repo: string;
  workflowId?: string | number;
  ciPollingInterval?: number;
  maxCIWait?: number;

  // Supabase
  supabaseUrl?: string;
  supabaseKey?: string;

  // LLM
  anthropicApiKey?: string;
  model?: string;

  // Thresholds
  minConfidenceThreshold?: number;
  autoTriggerCI?: boolean;
  autoCommentOnPR?: boolean;
}

/**
 * Classe principal do PR Automation Engine
 */
export class PRAutomationEngine {
  private config: PRAutomationConfig;
  private intentParser: IntentParser;
  private ciOrchestrator: CIOrchestratorService;
  private apiBaseUrl = "https://api.github.com";
  private supabaseUrl?: string;
  private supabaseKey?: string;

  constructor(config: PRAutomationConfig) {
    this.config = {
      minConfidenceThreshold: 0.6,
      autoTriggerCI: true,
      autoCommentOnPR: false,
      ...config,
    };

    // Inicializa o intent parser
    this.intentParser = new IntentParser({
      apiKey: config.anthropicApiKey || process.env.ANTHROPIC_API_KEY,
      model: config.model || "claude-3-5-sonnet-20241022",
    });

    // Inicializa o CI orchestrator
    this.ciOrchestrator = new CIOrchestratorService({
      githubToken: config.githubToken,
      owner: config.owner,
      repo: config.repo,
      workflowId: config.workflowId,
      pollingIntervalMs: config.ciPollingInterval || 30000,
      maxWaitMs: config.maxCIWait || 300000,
    });

    // Configura Supabase se disponível
    this.supabaseUrl = config.supabaseUrl || process.env.SUPABASE_URL;
    this.supabaseKey = config.supabaseKey || process.env.SUPABASE_ANON_KEY;
  }

  /**
   * Analisa um PR completo
   */
  async analyzePR(
    prNumber: number,
    owner?: string,
    repo?: string
  ): Promise<PRAnalysis> {
    const finalOwner = owner || this.config.owner;
    const finalRepo = repo || this.config.repo;
    const startTime = Date.now();

    const analysis: PRAnalysis = {
      prNumber,
      owner: finalOwner,
      repo: finalRepo,
      title: "",
      author: "",
      branch: "",
      baseBranch: "main",
      status: PRAnalysisStatus.ANALYZING,
      filesChanged: 0,
      additions: 0,
      deletions: 0,
      changedFiles: [],
      commitMessages: [],
      codePatterns: [],
      suggestions: [],
      ciTriggered: false,
      analyzedAt: new Date(),
    };

    try {
      // 1. Busca dados do PR
      const prData = await this.fetchPRData(prNumber, finalOwner, finalRepo);
      Object.assign(analysis, {
        title: prData.title,
        author: prData.user.login,
        branch: prData.head.ref,
        baseBranch: prData.base.ref,
        description: prData.body,
      });

      // 2. Busca arquivos alterados
      const files = await this.fetchPRFiles(prNumber, finalOwner, finalRepo);
      analysis.changedFiles = files;
      analysis.filesChanged = files.length;
      analysis.additions = files.reduce((sum, f) => sum + f.additions, 0);
      analysis.deletions = files.reduce((sum, f) => sum + f.deletions, 0);

      // 3. Busca commits
      const commits = await this.fetchPRCommits(prNumber, finalOwner, finalRepo);
      analysis.commitMessages = commits.map((c) => c.commit.message);

      // 4. Parse de intent do primeiro commit
      if (commits.length > 0) {
        const mainCommitMsg = commits[0].commit.message.split("\n")[0];
        analysis.commitIntent = await this.intentParser.parse(mainCommitMsg);
      }

      // 5. Análise de padrões de código
      const patterns = await this.detectCodePatterns(files);
      analysis.codePatterns = patterns;

      // 6. Gera sugestões
      const suggestions = await this.generateSuggestions(files, patterns);
      analysis.suggestions = suggestions;

      // 7. Trigger de CI/CD se configurado
      if (this.config.autoTriggerCI) {
        try {
          analysis.status = PRAnalysisStatus.TRIGGERING_CI;
          const ciResult = await this.triggerCI(prNumber, finalOwner, finalRepo);
          analysis.ciTriggered = true;
          analysis.workflowRunId = ciResult.workflowRunId;

          // 8. Monitora build
          analysis.status = PRAnalysisStatus.MONITORING_BUILD;
          const buildStatus = await this.monitorBuild(ciResult.workflowRunId);
          analysis.buildStatus = buildStatus;
        } catch (error) {
          console.warn("CI trigger failed:", error);
          // Continua mesmo se CI falhar
        }
      }

      // 9. Persiste no Supabase se configurado
      if (this.supabaseUrl && this.supabaseKey) {
        await this.persistAnalysis(analysis);
      }

      analysis.status = PRAnalysisStatus.COMPLETED;
      analysis.completedAt = new Date();
      analysis.duration = Date.now() - startTime;

      return analysis;
    } catch (error) {
      analysis.status = PRAnalysisStatus.FAILED;
      analysis.error = error instanceof Error ? error.message : String(error);
      analysis.completedAt = new Date();
      analysis.duration = Date.now() - startTime;

      return analysis;
    }
  }

  /**
   * Gera sugestões de melhoria baseadas em padrões de código
   */
  async generateSuggestions(
    files: Array<{ filename: string; patch?: string }>,
    patterns: DetectedPattern[]
  ): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    // Mapeia padrões para sugestões
    for (const pattern of patterns) {
      const suggestion: Suggestion = {
        id: `${pattern.type}-${pattern.file}-${Date.now()}`,
        type: pattern.type,
        severity: pattern.severity,
        file: pattern.file,
        title: this.getTitleForPattern(pattern.type),
        description: pattern.description,
        recommendation: this.getRecommendationForPattern(
          pattern.type,
          pattern.file
        ),
        confidence: pattern.confidence,
        examples: this.getExamplesForPattern(pattern.type),
      };

      suggestions.push(suggestion);
    }

    // Adiciona sugestões gerais baseadas em estatísticas
    const totalAdditions = files.reduce((sum, f) => sum + f.additions, 0);
    const totalDeletions = files.reduce((sum, f) => sum + f.deletions, 0);

    if (totalAdditions > 500) {
      suggestions.push({
        id: `large-pr-${Date.now()}`,
        type: "complexity",
        severity: "warning",
        title: "Considerado um PR grande",
        description: `Este PR tem ${totalAdditions} linhas adicionadas, o que pode dificultar a revisão`,
        recommendation:
          "Considere dividir em PRs menores para melhor revisão e testabilidade",
        confidence: 0.9,
      });
    }

    if (!files.some((f) => f.filename.includes(".test.") || f.filename.includes(".spec."))) {
      suggestions.push({
        id: `missing-tests-${Date.now()}`,
        type: "missing-tests",
        severity: "warning",
        title: "Sem testes detectados",
        description:
          "Nenhum arquivo de teste foi modificado neste PR",
        recommendation:
          "Adicione testes para as mudanças implementadas",
        confidence: 0.7,
        examples: [
          "jest/vitest for unit tests",
          "Cypress/Playwright for e2e tests",
          "RTL for component tests",
        ],
      });
    }

    return suggestions;
  }

  /**
   * Dispara CI/CD pipeline
   */
  async triggerCI(prNumber: number, owner?: string, repo?: string): Promise<CIResult> {
    const finalOwner = owner || this.config.owner;
    const finalRepo = repo || this.config.repo;

    try {
      // Busca dados do PR para pegar a branch
      const prData = await this.fetchPRData(prNumber, finalOwner, finalRepo);
      const branch = prData.head.ref;

      // Trigger do workflow
      const workflowId = this.config.workflowId || "test.yml";
      const runId = await this.ciOrchestrator.triggerWorkflow(
        workflowId,
        branch,
        {
          pr_number: String(prNumber),
        }
      );

      // Monitora execução
      const orchestrationResult = await this.ciOrchestrator.monitorWorkflowRun(
        runId,
        workflowId
      );

      return {
        success: orchestrationResult.status === "success",
        workflowRunId: runId,
        status: orchestrationResult.workflowStatus,
        buildOutput: orchestrationResult.buildOutput,
        duration: orchestrationResult.duration,
        timestamp: orchestrationResult.timestamp,
        error: orchestrationResult.error,
      };
    } catch (error) {
      throw new Error(
        `Failed to trigger CI: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Monitora status do build
   */
  async monitorBuild(workflowId: number): Promise<BuildStatus> {
    try {
      // Aguarda um pouco para o workflow começar
      await this.delay(2000);

      // Monitora o workflow
      const result = await this.ciOrchestrator.monitorWorkflowRun(workflowId);

      // Extrai informações do build
      const buildStatus: BuildStatus = {
        workflowRunId: workflowId,
        status: result.workflowStatus,
        conclusion: result.conclusion || undefined,
        passed: result.status === "success",
        duration: result.duration,
        completedAt: result.timestamp,
      };

      // Tenta extrair dados de testes
      if (result.buildOutput.testResults) {
        buildStatus.testsPassed = result.buildOutput.testResults.passed;
        buildStatus.testsFailed = result.buildOutput.testResults.failed;
      }

      // Tenta extrair cobertura
      if (result.buildOutput.coverage) {
        buildStatus.coverage = Math.round(result.buildOutput.coverage.lines);
      }

      return buildStatus;
    } catch (error) {
      throw new Error(
        `Failed to monitor build: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Detecta padrões de código em arquivos alterados
   */
  private async detectCodePatterns(
    files: Array<{ filename: string; patch?: string; additions: number }>
  ): Promise<DetectedPattern[]> {
    const patterns: DetectedPattern[] = [];

    for (const file of files) {
      const language = this.detectLanguage(file.filename);

      // Detecção de TypeScript - tipos faltando
      if (language === "typescript" && file.patch) {
        if (
          (file.patch.includes("any") || file.patch.includes(": ")) &&
          !file.patch.includes(": unknown")
        ) {
          // Mais linhas de código podem indicar maior complexidade
          if (file.additions > 100) {
            patterns.push({
              type: "complexity",
              severity: "warning",
              file: file.filename,
              description: "Arquivo com grande número de adições",
              confidence: 0.7,
            });
          }
        }
      }

      // Detecção de código sem documentação
      if (file.additions > 50 && language !== "json" && language !== "yaml") {
        patterns.push({
          type: "documentation",
          severity: "info",
          file: file.filename,
          description: "Novo código sem documentação detectado",
          confidence: 0.6,
        });
      }

      // Detecção de possíveis problemas de segurança
      if (file.patch && file.patch.includes("eval(") && language === "typescript") {
        patterns.push({
          type: "security",
          severity: "critical",
          file: file.filename,
          description: "Uso potencial inseguro de eval() detectado",
          confidence: 0.95,
        });
      }

      // Detecção de problemas de performance
      if (
        file.patch &&
        (file.patch.includes("fetch") || file.patch.includes("query")) &&
        !file.patch.includes("async")
      ) {
        patterns.push({
          type: "performance",
          severity: "warning",
          file: file.filename,
          description: "Operação potencialmente síncrona detectada",
          confidence: 0.5,
        });
      }
    }

    return patterns;
  }

  /**
   * Busca dados do PR
   */
  private async fetchPRData(
    prNumber: number,
    owner: string,
    repo: string
  ): Promise<any> {
    const url = `${this.apiBaseUrl}/repos/${owner}/${repo}/pulls/${prNumber}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch PR data: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Busca arquivos alterados
   */
  private async fetchPRFiles(
    prNumber: number,
    owner: string,
    repo: string
  ): Promise<
    Array<{
      filename: string;
      patch?: string;
      additions: number;
      deletions: number;
    }>
  > {
    const url = `${this.apiBaseUrl}/repos/${owner}/${repo}/pulls/${prNumber}/files?per_page=100`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch PR files: ${response.statusText}`);
    }

    const data = (await response.json()) as Array<{
      filename: string;
      patch?: string;
      additions: number;
      deletions: number;
    }>;

    return data;
  }

  /**
   * Busca commits do PR
   */
  private async fetchPRCommits(
    prNumber: number,
    owner: string,
    repo: string
  ): Promise<any[]> {
    const url = `${this.apiBaseUrl}/repos/${owner}/${repo}/pulls/${prNumber}/commits?per_page=50`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch PR commits: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Persiste análise no Supabase
   */
  private async persistAnalysis(analysis: PRAnalysis): Promise<void> {
    if (!this.supabaseUrl || !this.supabaseKey) {
      return;
    }

    try {
      const url = `${this.supabaseUrl}/rest/v1/pr_analyses`;

      const payload = {
        pr_number: analysis.prNumber,
        owner: analysis.owner,
        repo: analysis.repo,
        title: analysis.title,
        author: analysis.author,
        branch: analysis.branch,
        status: analysis.status,
        files_changed: analysis.filesChanged,
        additions: analysis.additions,
        deletions: analysis.deletions,
        patterns_count: analysis.codePatterns.length,
        suggestions_count: analysis.suggestions.length,
        ci_triggered: analysis.ciTriggered,
        workflow_run_id: analysis.workflowRunId,
        analyzed_at: analysis.analyzedAt.toISOString(),
        completed_at: analysis.completedAt?.toISOString(),
        duration_ms: analysis.duration,
        error: analysis.error,
      };

      const response = await fetch(url, {
        method: "POST",
        headers: {
          apikey: this.supabaseKey,
          Authorization: `Bearer ${this.supabaseKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok && response.status !== 409) {
        console.warn(`Failed to persist analysis: ${response.statusText}`);
      }
    } catch (error) {
      console.warn("Error persisting analysis:", error);
      // Não falha a análise se a persistência falhar
    }
  }

  /**
   * Detecta linguagem de programação pelo nome do arquivo
   */
  private detectLanguage(filename: string): string {
    const ext = filename.split(".").pop()?.toLowerCase() || "";

    const languageMap: Record<string, string> = {
      ts: "typescript",
      tsx: "typescript",
      js: "javascript",
      jsx: "javascript",
      py: "python",
      java: "java",
      go: "go",
      rs: "rust",
      rb: "ruby",
      json: "json",
      yaml: "yaml",
      yml: "yaml",
      md: "markdown",
    };

    return languageMap[ext] || "unknown";
  }

  /**
   * Retorna título para um tipo de padrão
   */
  private getTitleForPattern(type: CodePatternType): string {
    const titles: Record<CodePatternType, string> = {
      complexity: "Complexidade de código elevada",
      duplication: "Código duplicado",
      "missing-types": "Tipos TypeScript faltando",
      "missing-tests": "Testes não encontrados",
      performance: "Possível problema de performance",
      security: "Preocupação de segurança",
      accessibility: "Acessibilidade",
      documentation: "Documentação faltando",
    };

    return titles[type] || "Padrão detectado";
  }

  /**
   * Retorna recomendação para um tipo de padrão
   */
  private getRecommendationForPattern(type: CodePatternType, file: string): string {
    const recommendations: Record<CodePatternType, string> = {
      complexity:
        "Refatore o código para reduzir complexidade ciclomática ou considere dividir funções",
      duplication: "Use composição ou herança para eliminar código duplicado",
      "missing-types": "Adicione tipos TypeScript explícitos para melhorar type safety",
      "missing-tests": "Escreva testes para cobrir a nova funcionalidade",
      performance: "Considere usar async/await e lazy loading para melhorar performance",
      security: "Revise o código para potenciais vulnerabilidades de segurança",
      accessibility:
        "Adicione labels, alt text e outras melhorias de acessibilidade",
      documentation: "Adicione comentários JSDoc e README para documentar o código",
    };

    return recommendations[type] || "Revise esta parte do código";
  }

  /**
   * Retorna exemplos para um tipo de padrão
   */
  private getExamplesForPattern(type: CodePatternType): string[] {
    const examples: Record<CodePatternType, string[]> = {
      complexity: [
        "Dividir funções grandes em funções menores",
        "Usar early returns para reduzir nesting",
        "Usar design patterns como Strategy ou Chain of Responsibility",
      ],
      duplication: [
        "Extrair código comum em funções reutilizáveis",
        "Usar herança ou composition",
        "Aplicar DRY (Don't Repeat Yourself)",
      ],
      "missing-types": [
        "interface User { name: string; email: string; }",
        "function fetchUser(id: string): Promise<User>",
        "Evitar uso de 'any' type",
      ],
      "missing-tests": [
        "describe('Component', () => { it('should render', () => { ... }) })",
        "Use testing-library para testes de componentes",
        "Use Jest para testes unitários",
      ],
      performance: [
        "Usar useMemo/useCallback em React",
        "Implementar pagination para listas grandes",
        "Usar índices em databases",
      ],
      security: [
        "Sanitizar inputs do usuário",
        "Usar prepared statements",
        "Implementar CORS corretamente",
      ],
      accessibility: [
        "Usar semantic HTML (button, nav, main, etc)",
        "Adicionar alt text em imagens",
        "Garantir contraste de cores adequado",
      ],
      documentation: [
        "Adicionar JSDoc comments para funções públicas",
        "Criar exemplos de uso",
        "Documentar comportamento de edge cases",
      ],
    };

    return examples[type] || [];
  }

  /**
   * Helper para delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Obtém métricas do CI orchestrator
   */
  getCIMetrics() {
    return this.ciOrchestrator.getMetrics();
  }
}

/**
 * Factory function para criar instância
 */
export function createPRAutomationEngine(
  config: PRAutomationConfig
): PRAutomationEngine {
  return new PRAutomationEngine(config);
}
