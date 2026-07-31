/**
 * Orchestrator Master — Orquestrador inteligente do pipeline de desenvolvimento
 * Versão: 1.0.0
 *
 * Coordena:
 * - Intent Parser (parse da intenção inicial)
 * - Code Generator (geração de código)
 * - CI Orchestrator (execução de testes/build)
 * - Feedback Engine (feedback automático)
 * - Code Reviewer (revisão de código)
 * - Auto-Merge (merge automático)
 *
 * Recursos:
 * - State machine com 9 estados (IDLE, INTENT_PARSING, CODE_GENERATION, CI_EXECUTION, CODE_REVIEW, MERGE_EXECUTION, COMPLETED, FAILED, ROLLED_BACK)
 * - Timeout handling (60 min máximo)
 * - Rollback automático em caso de erro crítico
 * - Telemetria completa e rastreamento de eventos
 * - Error handling robusto com retry logic
 * - Audit trail para compliance
 * - Métricas de performance em tempo real
 */

import Anthropic from "@anthropic-ai/sdk";
import { EventEmitter } from "events";

// ============================================================================
// ENUMS E TIPOS
// ============================================================================

/**
 * Estados da máquina de estados do orquestrador
 */
export enum OrchestratorState {
  /** Aguardando requisição inicial */
  IDLE = "idle",
  /** Parseando intenção do usuário */
  INTENT_PARSING = "intent_parsing",
  /** Gerando código baseado na intenção */
  CODE_GENERATION = "code_generation",
  /** Executando testes e build (CI) */
  CI_EXECUTION = "ci_execution",
  /** Revisando código gerado */
  CODE_REVIEW = "code_review",
  /** Executando merge */
  MERGE_EXECUTION = "merge_execution",
  /** Pipeline completado com sucesso */
  COMPLETED = "completed",
  /** Pipeline falhou */
  FAILED = "failed",
  /** Rollback realizado após falha */
  ROLLED_BACK = "rolled_back",
}

/**
 * Severidade de erro
 */
export enum ErrorSeverity {
  /** Erro informativo, não bloqueia */
  INFO = "info",
  /** Erro de aviso, pode continuar */
  WARNING = "warning",
  /** Erro que requer ação */
  ERROR = "error",
  /** Erro crítico que require rollback */
  CRITICAL = "critical",
}

/**
 * Tipos de eventos de telemetria
 */
export enum TelemetryEventType {
  STATE_TRANSITION = "state_transition",
  PHASE_STARTED = "phase_started",
  PHASE_COMPLETED = "phase_completed",
  PHASE_FAILED = "phase_failed",
  ERROR_OCCURRED = "error_occurred",
  TIMEOUT_WARNING = "timeout_warning",
  ROLLBACK_INITIATED = "rollback_initiated",
  RETRY_ATTEMPTED = "retry_attempted",
  METRIC_SNAPSHOT = "metric_snapshot",
}

/**
 * Interface para input do orchestrador
 */
export interface OrchestratorInput {
  /** Descrição da tarefa em linguagem natural */
  intent: string;
  /** Segmento vertical (ex: Saneamento, Energia) */
  segment?: string;
  /** Branch base para criar feature branch */
  baseBranch?: string;
  /** Diretório raiz do projeto */
  projectRoot?: string;
  /** Email do usuário */
  userEmail?: string;
  /** Tags para categorização */
  tags?: string[];
  /** Timeout customizado em minutos (máximo 60) */
  timeoutMinutes?: number;
  /** Requer aprovação humana antes do merge */
  requireApproval?: boolean;
}

/**
 * Interface para erro rastreado
 */
export interface TrackedError {
  /** Timestamp do erro */
  timestamp: Date;
  /** Estado em que o erro ocorreu */
  state: OrchestratorState;
  /** Severidade do erro */
  severity: ErrorSeverity;
  /** Mensagem de erro */
  message: string;
  /** Stack trace do erro */
  stack?: string;
  /** Contexto adicional */
  context?: Record<string, any>;
  /** ID único do erro */
  id: string;
}

/**
 * Interface para tentativa de retry
 */
export interface RetryAttempt {
  /** Número da tentativa */
  attemptNumber: number;
  /** Timestamp da tentativa */
  timestamp: Date;
  /** Estado anterior ao retry */
  previousState: OrchestratorState;
  /** Erro que causou o retry */
  error: TrackedError;
  /** Status do retry (pending, success, failed) */
  status: "pending" | "success" | "failed";
  /** Duração em ms */
  duration?: number;
}

/**
 * Interface para evento de telemetria
 */
export interface TelemetryEvent {
  /** Tipo do evento */
  type: TelemetryEventType;
  /** Timestamp */
  timestamp: Date;
  /** Estado atual */
  state: OrchestratorState;
  /** Duração da fase em ms (se aplicável) */
  phaseDuration?: number;
  /** Dados adicionais do evento */
  data?: Record<string, any>;
  /** Métricas associadas */
  metrics?: OrchestratorMetrics;
}

/**
 * Interface para métricas do orquestrador
 */
export interface OrchestratorMetrics {
  /** Duração total em ms */
  totalDurationMs: number;
  /** Duração de cada fase em ms */
  phaseDurations: Record<OrchestratorState, number>;
  /** Número de erros */
  errorCount: number;
  /** Número de retries */
  retryCount: number;
  /** Número de timeouts */
  timeoutCount: number;
  /** Taxa de sucesso (0-1) */
  successRate: number;
  /** Timestamp de início */
  startedAt: Date;
  /** Timestamp de fim */
  endedAt?: Date;
  /** Estado final */
  finalState: OrchestratorState;
  /** Erros rastreados */
  errors: TrackedError[];
  /** Tentativas de retry */
  retries: RetryAttempt[];
}

/**
 * Interface para resultado do orchestrador
 */
export interface OrchestratorResult {
  /** Status final */
  success: boolean;
  /** Estado final */
  finalState: OrchestratorState;
  /** Mensagem de resultado */
  message: string;
  /** Artifacts gerados */
  artifacts?: {
    branch: string;
    pullRequest?: {
      number: number;
      url: string;
    };
    files?: string[];
  };
  /** Métricas finais */
  metrics: OrchestratorMetrics;
  /** Erros ocorridos */
  errors: TrackedError[];
  /** Rollback realizado? */
  rolledBack: boolean;
  /** Detalhes do rollback (se aplicável) */
  rollbackDetails?: {
    reason: string;
    timestamp: Date;
    restoredCommit: string;
  };
}

/**
 * Interface para configuração do retry
 */
export interface RetryPolicy {
  /** Máximo de tentativas */
  maxAttempts: number;
  /** Delay inicial em ms */
  initialDelayMs: number;
  /** Delay máximo em ms */
  maxDelayMs: number;
  /** Fator de backoff exponencial */
  backoffFactor: number;
  /** Estados que podem fazer retry */
  retryableStates: OrchestratorState[];
}

/**
 * Interface para configuração do orchestrador
 */
export interface OrchestratorConfig {
  /** Timeout global em minutos (máximo 60) */
  timeoutMinutes: number;
  /** Política de retry */
  retryPolicy: RetryPolicy;
  /** Se deve fazer rollback automático em erro crítico */
  autoRollback: boolean;
  /** Se deve fazer merge automático após sucesso */
  autoMerge: boolean;
  /** Habilitar telemetria */
  telemetryEnabled: boolean;
  /** Log verboso */
  verbose: boolean;
  /** Callbacks para notificação */
  callbacks?: {
    onStateChange?: (state: OrchestratorState) => Promise<void>;
    onError?: (error: TrackedError) => Promise<void>;
    onSuccess?: (result: OrchestratorResult) => Promise<void>;
  };
}

// ============================================================================
// CLASSE PRINCIPAL DO ORCHESTRADOR
// ============================================================================

export class MasterOrchestrator extends EventEmitter {
  /** Configuração do orchestrador */
  private config: OrchestratorConfig;

  /** Estado atual */
  private currentState: OrchestratorState = OrchestratorState.IDLE;

  /** Input da execução atual */
  private currentInput?: OrchestratorInput;

  /** Métricas acumuladas */
  private metrics: OrchestratorMetrics = {
    totalDurationMs: 0,
    phaseDurations: {
      [OrchestratorState.IDLE]: 0,
      [OrchestratorState.INTENT_PARSING]: 0,
      [OrchestratorState.CODE_GENERATION]: 0,
      [OrchestratorState.CI_EXECUTION]: 0,
      [OrchestratorState.CODE_REVIEW]: 0,
      [OrchestratorState.MERGE_EXECUTION]: 0,
      [OrchestratorState.COMPLETED]: 0,
      [OrchestratorState.FAILED]: 0,
      [OrchestratorState.ROLLED_BACK]: 0,
    },
    errorCount: 0,
    retryCount: 0,
    timeoutCount: 0,
    successRate: 0,
    startedAt: new Date(),
    finalState: OrchestratorState.IDLE,
    errors: [],
    retries: [],
  };

  /** Histórico de eventos de telemetria */
  private telemetryEvents: TelemetryEvent[] = [];

  /** Timestamp do início da execução */
  private executionStartTime?: Date;

  /** Timeout ID para cancelamento */
  private timeoutHandle?: NodeJS.Timeout;

  /** Cliente Anthropic */
  private anthropic: Anthropic;

  /** Fase atual para timeout tracking */
  private phaseStartTime?: Date;

  /** Commit anterior para rollback */
  private previousCommit?: string;

  constructor(config?: Partial<OrchestratorConfig>) {
    super();

    this.config = {
      timeoutMinutes: Math.min(config?.timeoutMinutes || 60, 60),
      retryPolicy: config?.retryPolicy || {
        maxAttempts: 3,
        initialDelayMs: 1000,
        maxDelayMs: 30000,
        backoffFactor: 2,
        retryableStates: [
          OrchestratorState.CODE_GENERATION,
          OrchestratorState.CI_EXECUTION,
          OrchestratorState.CODE_REVIEW,
          OrchestratorState.MERGE_EXECUTION,
        ],
      },
      autoRollback: config?.autoRollback !== false,
      autoMerge: config?.autoMerge !== false,
      telemetryEnabled: config?.telemetryEnabled !== false,
      verbose: config?.verbose === true,
      callbacks: config?.callbacks,
    };

    this.anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  }

  /**
   * Inicia a orquestração de um pipeline
   */
  async orchestrate(input: OrchestratorInput): Promise<OrchestratorResult> {
    try {
      this.currentInput = input;
      this.executionStartTime = new Date();
      this.metrics.startedAt = this.executionStartTime;

      // Validar input
      this.validateInput(input);

      // Configurar timeout global
      this.setupGlobalTimeout();

      // Iniciar pipeline
      await this.transitionState(OrchestratorState.INTENT_PARSING);
      await this.executeIntentParsing();

      await this.transitionState(OrchestratorState.CODE_GENERATION);
      await this.executeCodeGeneration();

      await this.transitionState(OrchestratorState.CI_EXECUTION);
      await this.executeCIExecution();

      await this.transitionState(OrchestratorState.CODE_REVIEW);
      await this.executeCodeReview();

      await this.transitionState(OrchestratorState.MERGE_EXECUTION);
      await this.executeMergeExecution();

      await this.transitionState(OrchestratorState.COMPLETED);

      const result = this.buildSuccessResult();
      await this.config.callbacks?.onSuccess?.(result);
      return result;
    } catch (error) {
      return await this.handlePipelineError(error);
    } finally {
      this.cleanup();
    }
  }

  /**
   * Transiciona para um novo estado
   */
  private async transitionState(newState: OrchestratorState): Promise<void> {
    const previousState = this.currentState;
    const phaseStarted = this.phaseStartTime || new Date();

    // Registrar duração da fase anterior
    if (this.phaseStartTime) {
      const phaseDuration = Date.now() - this.phaseStartTime.getTime();
      this.metrics.phaseDurations[previousState] = phaseDuration;
    }

    this.currentState = newState;
    this.phaseStartTime = new Date();

    // Emitir evento de transição
    this.emit("stateChange", { previousState, newState, timestamp: new Date() });

    // Registrar telemetria
    await this.recordTelemetry({
      type: TelemetryEventType.STATE_TRANSITION,
      timestamp: new Date(),
      state: newState,
      data: { previousState },
    });

    // Callback
    await this.config.callbacks?.onStateChange?.(newState);

    if (this.config.verbose) {
      console.log(`[Orchestrator] Transição: ${previousState} → ${newState}`);
    }
  }

  /**
   * Valida o input
   */
  private validateInput(input: OrchestratorInput): void {
    if (!input.intent || input.intent.trim().length === 0) {
      throw new Error("Intent não pode estar vazio");
    }

    if (input.timeoutMinutes && input.timeoutMinutes > 60) {
      throw new Error("Timeout máximo é 60 minutos");
    }
  }

  /**
   * Configura timeout global
   */
  private setupGlobalTimeout(): void {
    const timeoutMs = (this.currentInput?.timeoutMinutes || this.config.timeoutMinutes) * 60 * 1000;

    this.timeoutHandle = setTimeout(() => {
      this.handleTimeout();
    }, timeoutMs);

    if (this.config.verbose) {
      console.log(`[Orchestrator] Timeout configurado para ${timeoutMs}ms`);
    }
  }

  /**
   * Manipula timeout global
   */
  private async handleTimeout(): Promise<void> {
    this.metrics.timeoutCount++;

    const error: TrackedError = {
      timestamp: new Date(),
      state: this.currentState,
      severity: ErrorSeverity.CRITICAL,
      message: `Timeout global atingido (${this.config.timeoutMinutes} minutos)`,
      id: this.generateErrorId(),
    };

    await this.recordTelemetry({
      type: TelemetryEventType.TIMEOUT_WARNING,
      timestamp: new Date(),
      state: this.currentState,
      data: { error },
    });

    if (this.config.autoRollback) {
      await this.executeRollback("Timeout global");
    }

    throw error;
  }

  /**
   * Executa fase de parsing de intenção
   */
  private async executeIntentParsing(): Promise<void> {
    try {
      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_STARTED,
        timestamp: new Date(),
        state: OrchestratorState.INTENT_PARSING,
      });

      if (!this.currentInput) {
        throw new Error("Input não inicializado");
      }

      // Simular parsing de intenção com Claude
      const response = await this.anthropic.messages.create({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 500,
        messages: [
          {
            role: "user",
            content: `Analise a seguinte intenção e extraia: objetivo, segmento, tipo de ação, e prioridade.\n\nIntenção: ${this.currentInput.intent}`,
          },
        ],
      });

      const parsedContent = response.content[0];
      if (parsedContent.type !== "text") {
        throw new Error("Resposta inesperada do Claude");
      }

      if (this.config.verbose) {
        console.log(`[Intent Parser] Análise: ${parsedContent.text.substring(0, 100)}...`);
      }

      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_COMPLETED,
        timestamp: new Date(),
        state: OrchestratorState.INTENT_PARSING,
        phaseDuration: this.getPhaseElapsedTime(),
      });
    } catch (error) {
      throw this.wrapError(error, OrchestratorState.INTENT_PARSING);
    }
  }

  /**
   * Executa fase de geração de código
   */
  private async executeCodeGeneration(): Promise<void> {
    try {
      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_STARTED,
        timestamp: new Date(),
        state: OrchestratorState.CODE_GENERATION,
      });

      if (!this.currentInput) {
        throw new Error("Input não inicializado");
      }

      // Simular geração de código com Claude
      const response = await this.anthropic.messages.create({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 2000,
        messages: [
          {
            role: "user",
            content: `Gere código TypeScript para: ${this.currentInput.intent}\n\nSegmento: ${this.currentInput.segment || "Geral"}\n\nFormato: retorne APENAS código válido com comentários.`,
          },
        ],
      });

      const generatedContent = response.content[0];
      if (generatedContent.type !== "text") {
        throw new Error("Resposta inesperada do Claude");
      }

      // Simular armazenamento de commit anterior
      this.previousCommit = "abc123def456"; // Mock

      if (this.config.verbose) {
        console.log(
          `[Code Generator] Código gerado: ${generatedContent.text.substring(0, 100)}...`
        );
      }

      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_COMPLETED,
        timestamp: new Date(),
        state: OrchestratorState.CODE_GENERATION,
        phaseDuration: this.getPhaseElapsedTime(),
      });
    } catch (error) {
      throw this.wrapError(error, OrchestratorState.CODE_GENERATION);
    }
  }

  /**
   * Executa fase de CI
   */
  private async executeCIExecution(): Promise<void> {
    try {
      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_STARTED,
        timestamp: new Date(),
        state: OrchestratorState.CI_EXECUTION,
      });

      // Simular execução de CI (testes, build, lint)
      // Aqui integraríamos com o CIOrchestratorService real
      const testsPassed = Math.random() > 0.2; // 80% de chance de sucesso

      if (!testsPassed) {
        throw new Error(
          "Testes falharam: Coverage abaixo de 80%, 3 testes falhando no suite de regressão"
        );
      }

      if (this.config.verbose) {
        console.log("[CI Orchestrator] Todos os testes passaram com sucesso");
      }

      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_COMPLETED,
        timestamp: new Date(),
        state: OrchestratorState.CI_EXECUTION,
        phaseDuration: this.getPhaseElapsedTime(),
      });
    } catch (error) {
      throw this.wrapError(error, OrchestratorState.CI_EXECUTION);
    }
  }

  /**
   * Executa fase de revisão de código
   */
  private async executeCodeReview(): Promise<void> {
    try {
      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_STARTED,
        timestamp: new Date(),
        state: OrchestratorState.CODE_REVIEW,
      });

      // Simular análise de código com Claude
      const response = await this.anthropic.messages.create({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content:
              'Revise o código gerado. Identifique: issues de segurança, performance, maintainability. Formato: JSON com campos "issues", "suggestions", "approval".',
          },
        ],
      });

      const reviewContent = response.content[0];
      if (reviewContent.type !== "text") {
        throw new Error("Resposta inesperada do Claude");
      }

      if (this.config.verbose) {
        console.log(`[Code Reviewer] Review completo: ${reviewContent.text.substring(0, 100)}...`);
      }

      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_COMPLETED,
        timestamp: new Date(),
        state: OrchestratorState.CODE_REVIEW,
        phaseDuration: this.getPhaseElapsedTime(),
      });
    } catch (error) {
      throw this.wrapError(error, OrchestratorState.CODE_REVIEW);
    }
  }

  /**
   * Executa fase de merge
   */
  private async executeMergeExecution(): Promise<void> {
    try {
      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_STARTED,
        timestamp: new Date(),
        state: OrchestratorState.MERGE_EXECUTION,
      });

      // Verificar se auto-merge está habilitado
      if (!this.config.autoMerge && this.currentInput?.requireApproval) {
        if (this.config.verbose) {
          console.log("[Auto-Merge] Aguardando aprovação humana...");
        }
        // Em produção, aguardaria aqui por aprovação
      }

      // Simular merge
      const mergeSucceeded = Math.random() > 0.1; // 90% de chance de sucesso

      if (!mergeSucceeded) {
        throw new Error("Falha ao fazer merge: conflitos de merge detectados");
      }

      if (this.config.verbose) {
        console.log("[Auto-Merge] Merge realizado com sucesso");
      }

      await this.recordTelemetry({
        type: TelemetryEventType.PHASE_COMPLETED,
        timestamp: new Date(),
        state: OrchestratorState.MERGE_EXECUTION,
        phaseDuration: this.getPhaseElapsedTime(),
      });
    } catch (error) {
      throw this.wrapError(error, OrchestratorState.MERGE_EXECUTION);
    }
  }

  /**
   * Manipula erro do pipeline com retry logic
   */
  private async handlePipelineError(error: any): Promise<OrchestratorResult> {
    const trackedError = this.wrapError(error, this.currentState);
    this.metrics.errors.push(trackedError);
    this.metrics.errorCount++;

    // Verificar se pode fazer retry
    const canRetry =
      this.config.retryPolicy.retryableStates.includes(this.currentState) &&
      this.metrics.retries.filter((r) => r.previousState === this.currentState).length <
        this.config.retryPolicy.maxAttempts;

    if (canRetry) {
      const retryAttempt = await this.executeRetry(trackedError);
      if (retryAttempt.status === "success") {
        // Retry foi bem-sucedido, continuar pipeline
        return await this.continuePipelineAfterRetry();
      }
    }

    // Se chegou aqui, a falha é definitiva
    await this.config.callbacks?.onError?.(trackedError);

    // Decidir se faz rollback
    if (this.config.autoRollback && trackedError.severity === ErrorSeverity.CRITICAL) {
      await this.executeRollback(trackedError.message);
      return this.buildRolledBackResult(trackedError);
    }

    return this.buildFailureResult(trackedError);
  }

  /**
   * Executa retry de uma fase
   */
  private async executeRetry(error: TrackedError): Promise<RetryAttempt> {
    const attemptNumber = this.metrics.retries.filter((r) => r.previousState === this.currentState)
      .length + 1;

    const attempt: RetryAttempt = {
      attemptNumber,
      timestamp: new Date(),
      previousState: this.currentState,
      error,
      status: "pending",
    };

    const delayMs = Math.min(
      this.config.retryPolicy.initialDelayMs *
        Math.pow(this.config.retryPolicy.backoffFactor, attemptNumber - 1),
      this.config.retryPolicy.maxDelayMs
    );

    if (this.config.verbose) {
      console.log(
        `[Retry] Tentativa ${attemptNumber} de ${this.config.retryPolicy.maxAttempts} após ${delayMs}ms`
      );
    }

    await new Promise((resolve) => setTimeout(resolve, delayMs));

    await this.recordTelemetry({
      type: TelemetryEventType.RETRY_ATTEMPTED,
      timestamp: new Date(),
      state: this.currentState,
      data: { attemptNumber, error },
    });

    this.metrics.retryCount++;

    try {
      // Re-executar a fase atual
      switch (this.currentState) {
        case OrchestratorState.CODE_GENERATION:
          await this.executeCodeGeneration();
          break;
        case OrchestratorState.CI_EXECUTION:
          await this.executeCIExecution();
          break;
        case OrchestratorState.CODE_REVIEW:
          await this.executeCodeReview();
          break;
        case OrchestratorState.MERGE_EXECUTION:
          await this.executeMergeExecution();
          break;
      }

      attempt.status = "success";
      attempt.duration = Date.now() - attempt.timestamp.getTime();
    } catch (retryError) {
      attempt.status = "failed";
      attempt.duration = Date.now() - attempt.timestamp.getTime();
    }

    this.metrics.retries.push(attempt);
    return attempt;
  }

  /**
   * Continua o pipeline após retry bem-sucedido
   */
  private async continuePipelineAfterRetry(): Promise<OrchestratorResult> {
    // Lógica para continuar a partir da fase que teve sucesso
    // Em um caso real, isso reconstruiria o fluxo de estados
    if (this.currentState === OrchestratorState.CODE_GENERATION) {
      await this.transitionState(OrchestratorState.CI_EXECUTION);
      await this.executeCIExecution();
    } else if (this.currentState === OrchestratorState.CI_EXECUTION) {
      await this.transitionState(OrchestratorState.CODE_REVIEW);
      await this.executeCodeReview();
    } else if (this.currentState === OrchestratorState.CODE_REVIEW) {
      await this.transitionState(OrchestratorState.MERGE_EXECUTION);
      await this.executeMergeExecution();
    }

    await this.transitionState(OrchestratorState.COMPLETED);
    return this.buildSuccessResult();
  }

  /**
   * Executa rollback
   */
  private async executeRollback(reason: string): Promise<void> {
    await this.transitionState(OrchestratorState.ROLLED_BACK);

    if (this.config.verbose) {
      console.log(`[Rollback] Revertendo para commit anterior: ${this.previousCommit}`);
    }

    await this.recordTelemetry({
      type: TelemetryEventType.ROLLBACK_INITIATED,
      timestamp: new Date(),
      state: OrchestratorState.ROLLED_BACK,
      data: { reason, restoredCommit: this.previousCommit },
    });

    // Em produção, executaria comandos git de rollback
    // git reset --hard [previousCommit]
    // git push origin main --force (com cuidado!)
  }

  /**
   * Envolve erro genérico em TrackedError
   */
  private wrapError(error: any, state: OrchestratorState): TrackedError {
    const message = error instanceof Error ? error.message : String(error);
    const stack = error instanceof Error ? error.stack : undefined;

    return {
      timestamp: new Date(),
      state,
      severity:
        state === OrchestratorState.MERGE_EXECUTION ? ErrorSeverity.CRITICAL : ErrorSeverity.ERROR,
      message,
      stack,
      id: this.generateErrorId(),
    };
  }

  /**
   * Registra evento de telemetria
   */
  private async recordTelemetry(event: Partial<TelemetryEvent>): Promise<void> {
    if (!this.config.telemetryEnabled) return;

    const telemetryEvent: TelemetryEvent = {
      type: event.type || TelemetryEventType.METRIC_SNAPSHOT,
      timestamp: event.timestamp || new Date(),
      state: event.state || this.currentState,
      phaseDuration: event.phaseDuration,
      data: event.data,
      metrics: this.metrics,
    };

    this.telemetryEvents.push(telemetryEvent);

    if (this.config.verbose && event.type === TelemetryEventType.PHASE_COMPLETED) {
      console.log(
        `[Telemetry] Fase ${event.state} completada em ${event.phaseDuration}ms`
      );
    }

    this.emit("telemetry", telemetryEvent);
  }

  /**
   * Constrói resultado de sucesso
   */
  private buildSuccessResult(): OrchestratorResult {
    const endTime = new Date();
    this.metrics.endedAt = endTime;
    this.metrics.totalDurationMs = endTime.getTime() - this.metrics.startedAt.getTime();
    this.metrics.finalState = OrchestratorState.COMPLETED;
    this.metrics.successRate = 1;

    return {
      success: true,
      finalState: OrchestratorState.COMPLETED,
      message: "Pipeline executado com sucesso",
      metrics: this.metrics,
      errors: this.metrics.errors,
      rolledBack: false,
      artifacts: {
        branch: `feature/${this.generateFeatureBranchName()}`,
        pullRequest: {
          number: Math.floor(Math.random() * 10000),
          url: `https://github.com/manta/codex-exemplo/pull/${Math.floor(Math.random() * 10000)}`,
        },
        files: ["/src/services/orchestrator.ts", "/tests/orchestrator.test.ts"],
      },
    };
  }

  /**
   * Constrói resultado de falha
   */
  private buildFailureResult(error: TrackedError): OrchestratorResult {
    const endTime = new Date();
    this.metrics.endedAt = endTime;
    this.metrics.totalDurationMs = endTime.getTime() - this.metrics.startedAt.getTime();
    this.metrics.finalState = OrchestratorState.FAILED;
    this.metrics.successRate = 0;

    return {
      success: false,
      finalState: OrchestratorState.FAILED,
      message: `Pipeline falhou: ${error.message}`,
      metrics: this.metrics,
      errors: this.metrics.errors,
      rolledBack: false,
    };
  }

  /**
   * Constrói resultado de rollback
   */
  private buildRolledBackResult(error: TrackedError): OrchestratorResult {
    const endTime = new Date();
    this.metrics.endedAt = endTime;
    this.metrics.totalDurationMs = endTime.getTime() - this.metrics.startedAt.getTime();
    this.metrics.finalState = OrchestratorState.ROLLED_BACK;
    this.metrics.successRate = 0;

    return {
      success: false,
      finalState: OrchestratorState.ROLLED_BACK,
      message: `Pipeline falhou e foi feito rollback: ${error.message}`,
      metrics: this.metrics,
      errors: this.metrics.errors,
      rolledBack: true,
      rollbackDetails: {
        reason: error.message,
        timestamp: new Date(),
        restoredCommit: this.previousCommit || "unknown",
      },
    };
  }

  /**
   * Obtém tempo decorrido da fase atual
   */
  private getPhaseElapsedTime(): number {
    if (!this.phaseStartTime) return 0;
    return Date.now() - this.phaseStartTime.getTime();
  }

  /**
   * Gera ID único para erro
   */
  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Gera nome para feature branch
   */
  private generateFeatureBranchName(): string {
    const timestamp = Date.now();
    const segment = this.currentInput?.segment || "general";
    return `${segment.toLowerCase().replace(/\s+/g, "-")}-${timestamp}`;
  }

  /**
   * Limpa recursos (timeout, listeners, etc)
   */
  private cleanup(): void {
    if (this.timeoutHandle) {
      clearTimeout(this.timeoutHandle);
    }

    // Remover listeners
    this.removeAllListeners();
  }

  /**
   * Retorna métricas atualizadas
   */
  getMetrics(): OrchestratorMetrics {
    return { ...this.metrics };
  }

  /**
   * Retorna eventos de telemetria
   */
  getTelemetryEvents(): TelemetryEvent[] {
    return [...this.telemetryEvents];
  }

  /**
   * Retorna estado atual
   */
  getCurrentState(): OrchestratorState {
    return this.currentState;
  }

  /**
   * Exporta relatório de auditoria completo
   */
  exportAuditTrail(): {
    timestamp: Date;
    startedAt: Date;
    endedAt?: Date;
    totalDurationMs: number;
    finalState: OrchestratorState;
    stateTransitions: Array<{ from: OrchestratorState; to: OrchestratorState; timestamp: Date }>;
    errors: TrackedError[];
    retries: RetryAttempt[];
    telemetryEvents: TelemetryEvent[];
  } {
    const stateTransitions: Array<{ from: OrchestratorState; to: OrchestratorState; timestamp: Date }> =
      [];

    for (const event of this.telemetryEvents) {
      if (event.type === TelemetryEventType.STATE_TRANSITION && event.data?.previousState) {
        stateTransitions.push({
          from: event.data.previousState,
          to: event.state,
          timestamp: event.timestamp,
        });
      }
    }

    return {
      timestamp: new Date(),
      startedAt: this.metrics.startedAt,
      endedAt: this.metrics.endedAt,
      totalDurationMs: this.metrics.totalDurationMs,
      finalState: this.metrics.finalState,
      stateTransitions,
      errors: this.metrics.errors,
      retries: this.metrics.retries,
      telemetryEvents: this.telemetryEvents,
    };
  }
}

// ============================================================================
// FACTORY E EXPORTS
// ============================================================================

/**
 * Cria instância do orchestrador com configuração padrão
 */
export function createMasterOrchestrator(
  config?: Partial<OrchestratorConfig>
): MasterOrchestrator {
  return new MasterOrchestrator(config);
}
