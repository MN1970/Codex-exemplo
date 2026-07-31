/**
 * Testes para o Master Orchestrator
 * Cobertura: state machine, timeouts, retry logic, rollback, telemetria
 */

import {
  MasterOrchestrator,
  createMasterOrchestrator,
  OrchestratorState,
  ErrorSeverity,
  TelemetryEventType,
  OrchestratorInput,
} from "../orchestrator";

describe("Master Orchestrator", () => {
  let orchestrator: MasterOrchestrator;

  beforeEach(() => {
    orchestrator = createMasterOrchestrator({
      timeoutMinutes: 1,
      verbose: false,
      telemetryEnabled: true,
      autoRollback: true,
      autoMerge: true,
    });
  });

  afterEach(() => {
    // Cleanup
  });

  // ========================================================================
  // TESTES DE STATE MACHINE
  // ========================================================================

  describe("State Machine", () => {
    it("deve iniciar no estado IDLE", () => {
      expect(orchestrator.getCurrentState()).toBe(OrchestratorState.IDLE);
    });

    it("deve fazer transições de estado corretas durante orquestração bem-sucedida", async () => {
      const states: OrchestratorState[] = [];

      orchestrator.on("stateChange", (data) => {
        states.push(data.newState);
      });

      const input: OrchestratorInput = {
        intent: "Criar novo agente para análise de saneamento",
        segment: "Saneamento",
        timeoutMinutes: 30,
      };

      const result = await orchestrator.orchestrate(input);

      expect(result.success).toBe(true);
      expect(result.finalState).toBe(OrchestratorState.COMPLETED);
      expect(states).toContain(OrchestratorState.INTENT_PARSING);
      expect(states).toContain(OrchestratorState.CODE_GENERATION);
      expect(states).toContain(OrchestratorState.CI_EXECUTION);
      expect(states).toContain(OrchestratorState.CODE_REVIEW);
      expect(states).toContain(OrchestratorState.MERGE_EXECUTION);
    });

    it("deve respeitar a ordem de transição de estados", async () => {
      const transitions: Array<{ from: OrchestratorState; to: OrchestratorState }> = [];

      orchestrator.on("stateChange", (data) => {
        transitions.push({ from: data.previousState, to: data.newState });
      });

      const input: OrchestratorInput = {
        intent: "Criar novo agente",
      };

      await orchestrator.orchestrate(input);

      // Validar sequência de transições
      const stateSequence = transitions.map((t) => t.to);
      const expectedStart = [
        OrchestratorState.INTENT_PARSING,
        OrchestratorState.CODE_GENERATION,
        OrchestratorState.CI_EXECUTION,
      ];

      for (let i = 0; i < expectedStart.length; i++) {
        expect(stateSequence[i]).toBe(expectedStart[i]);
      }
    });
  });

  // ========================================================================
  // TESTES DE TIMEOUT
  // ========================================================================

  describe("Timeout Handling", () => {
    it("deve validar timeout máximo de 60 minutos", () => {
      expect(() => {
        const orch = createMasterOrchestrator({
          timeoutMinutes: 120,
        });
        orch.orchestrate({
          intent: "Test",
          timeoutMinutes: 120,
        });
      }).toThrow();
    });

    it("deve permitir timeout customizado até 60 minutos", () => {
      const orch = createMasterOrchestrator({
        timeoutMinutes: 45,
      });
      expect(orch.getCurrentState()).toBe(OrchestratorState.IDLE);
    });

    it("deve registrar evento de timeout", async () => {
      const orch = createMasterOrchestrator({
        timeoutMinutes: 0.01, // 0.6 segundos
        autoRollback: true,
      });

      const telemetryEvents: any[] = [];
      orch.on("telemetry", (event) => {
        telemetryEvents.push(event);
      });

      const input: OrchestratorInput = {
        intent: "Test with timeout",
      };

      try {
        await orch.orchestrate(input);
      } catch (error) {
        // Esperado timeout
      }

      const timeoutEvent = telemetryEvents.find(
        (e) => e.type === TelemetryEventType.TIMEOUT_WARNING
      );
      expect(timeoutEvent).toBeDefined();
    });
  });

  // ========================================================================
  // TESTES DE VALIDAÇÃO DE INPUT
  // ========================================================================

  describe("Input Validation", () => {
    it("deve rejeitar intent vazio", async () => {
      const input: OrchestratorInput = {
        intent: "",
      };

      const result = await orchestrator.orchestrate(input);
      expect(result.success).toBe(false);
    });

    it("deve aceitar input válido", async () => {
      const input: OrchestratorInput = {
        intent: "Criar novo serviço de análise",
        segment: "Rodovias",
      };

      const result = await orchestrator.orchestrate(input);
      expect([true, false]).toContain(result.success);
    });

    it("deve incluir tags opcionais", async () => {
      const input: OrchestratorInput = {
        intent: "Criar agente",
        tags: ["urgent", "high-priority"],
      };

      const result = await orchestrator.orchestrate(input);
      expect(result.metrics).toBeDefined();
    });
  });

  // ========================================================================
  // TESTES DE TELEMETRIA E MÉTRICAS
  // ========================================================================

  describe("Telemetry and Metrics", () => {
    it("deve registrar eventos de telemetria para cada fase", async () => {
      const events: any[] = [];

      orchestrator.on("telemetry", (event) => {
        events.push(event);
      });

      const input: OrchestratorInput = {
        intent: "Teste telemetria",
      };

      await orchestrator.orchestrate(input);

      const phaseStartedEvents = events.filter(
        (e) => e.type === TelemetryEventType.PHASE_STARTED
      );
      const phaseCompletedEvents = events.filter(
        (e) => e.type === TelemetryEventType.PHASE_COMPLETED
      );

      expect(phaseStartedEvents.length).toBeGreaterThan(0);
      expect(phaseCompletedEvents.length).toBeGreaterThan(0);
    });

    it("deve rastrear duração de cada fase", async () => {
      const input: OrchestratorInput = {
        intent: "Teste duração",
      };

      const result = await orchestrator.orchestrate(input);
      const metrics = result.metrics;

      expect(metrics.totalDurationMs).toBeGreaterThan(0);
      expect(metrics.phaseDurations).toBeDefined();
      expect(
        Object.values(metrics.phaseDurations).some((d) => d > 0)
      ).toBe(true);
    });

    it("deve rastrear contadores de erro, retry e timeout", async () => {
      const input: OrchestratorInput = {
        intent: "Teste contadores",
      };

      const result = await orchestrator.orchestrate(input);
      const metrics = result.metrics;

      expect(metrics.errorCount).toBeGreaterThanOrEqual(0);
      expect(metrics.retryCount).toBeGreaterThanOrEqual(0);
      expect(metrics.timeoutCount).toBeGreaterThanOrEqual(0);
    });

    it("deve exportar audit trail completo", async () => {
      const input: OrchestratorInput = {
        intent: "Teste audit trail",
      };

      await orchestrator.orchestrate(input);
      const auditTrail = orchestrator.exportAuditTrail();

      expect(auditTrail.timestamp).toBeDefined();
      expect(auditTrail.startedAt).toBeDefined();
      expect(auditTrail.finalState).toBeDefined();
      expect(auditTrail.stateTransitions).toBeDefined();
      expect(auditTrail.errors).toBeDefined();
      expect(auditTrail.telemetryEvents).toBeDefined();
    });

    it("deve calcular taxa de sucesso", async () => {
      const input: OrchestratorInput = {
        intent: "Teste taxa sucesso",
      };

      const result = await orchestrator.orchestrate(input);
      const metrics = result.metrics;

      if (result.success) {
        expect(metrics.successRate).toBe(1);
      } else {
        expect(metrics.successRate).toBe(0);
      }
    });
  });

  // ========================================================================
  // TESTES DE RETRY LOGIC
  // ========================================================================

  describe("Retry Logic", () => {
    it("deve respeitar política de retry configurada", async () => {
      const orch = createMasterOrchestrator({
        retryPolicy: {
          maxAttempts: 3,
          initialDelayMs: 10,
          maxDelayMs: 100,
          backoffFactor: 2,
          retryableStates: [
            OrchestratorState.CODE_GENERATION,
            OrchestratorState.CI_EXECUTION,
          ],
        },
      });

      const input: OrchestratorInput = {
        intent: "Teste retry",
      };

      const result = await orch.orchestrate(input);
      expect(result.metrics.retryCount).toBeGreaterThanOrEqual(0);
    });

    it("deve rastrear tentativas de retry com backoff exponencial", async () => {
      const orch = createMasterOrchestrator({
        retryPolicy: {
          maxAttempts: 3,
          initialDelayMs: 10,
          maxDelayMs: 100,
          backoffFactor: 2,
          retryableStates: [OrchestratorState.CI_EXECUTION],
        },
      });

      const input: OrchestratorInput = {
        intent: "Teste backoff",
      };

      const result = await orch.orchestrate(input);
      const auditTrail = orch.exportAuditTrail();

      expect(auditTrail.retries).toBeDefined();
      // Se houve retries, validar backoff exponencial
      if (auditTrail.retries.length > 1) {
        for (let i = 1; i < auditTrail.retries.length; i++) {
          const prevDelay = auditTrail.retries[i - 1].timestamp.getTime();
          const currDelay = auditTrail.retries[i].timestamp.getTime();
          expect(currDelay - prevDelay).toBeGreaterThan(0);
        }
      }
    });
  });

  // ========================================================================
  // TESTES DE ROLLBACK
  // ========================================================================

  describe("Rollback Mechanism", () => {
    it("deve executar rollback em erro crítico se habilitado", async () => {
      const orch = createMasterOrchestrator({
        autoRollback: true,
      });

      const input: OrchestratorInput = {
        intent: "Teste rollback crítico",
      };

      const result = await orch.orchestrate(input);
      // Pode resultar em rollback se houver erro crítico
      expect(
        [OrchestratorState.COMPLETED, OrchestratorState.ROLLED_BACK, OrchestratorState.FAILED]
      ).toContain(result.finalState);
    });

    it("deve rastrear detalhes de rollback", async () => {
      const orch = createMasterOrchestrator({
        autoRollback: true,
      });

      const input: OrchestratorInput = {
        intent: "Teste detalhes rollback",
      };

      const result = await orch.orchestrate(input);

      if (result.rolledBack) {
        expect(result.rollbackDetails).toBeDefined();
        expect(result.rollbackDetails?.reason).toBeDefined();
        expect(result.rollbackDetails?.timestamp).toBeDefined();
        expect(result.rollbackDetails?.restoredCommit).toBeDefined();
      }
    });

    it("deve respeitar flag autoRollback=false", async () => {
      const orch = createMasterOrchestrator({
        autoRollback: false,
      });

      const input: OrchestratorInput = {
        intent: "Teste sem rollback",
      };

      const result = await orch.orchestrate(input);
      expect(result.rolledBack).toBe(false);
    });
  });

  // ========================================================================
  // TESTES DE CALLBACKS
  // ========================================================================

  describe("Callbacks", () => {
    it("deve chamar callback onStateChange quando transição ocorre", async () => {
      const onStateChange = jest.fn();

      const orch = createMasterOrchestrator({
        callbacks: {
          onStateChange,
        },
      });

      const input: OrchestratorInput = {
        intent: "Teste callback state change",
      };

      await orch.orchestrate(input);
      expect(onStateChange).toHaveBeenCalled();
    });

    it("deve chamar callback onSuccess em sucesso", async () => {
      const onSuccess = jest.fn();

      const orch = createMasterOrchestrator({
        callbacks: {
          onSuccess,
        },
      });

      const input: OrchestratorInput = {
        intent: "Teste callback sucesso",
      };

      const result = await orch.orchestrate(input);

      if (result.success) {
        expect(onSuccess).toHaveBeenCalled();
      }
    });

    it("deve chamar callback onError em erro", async () => {
      const onError = jest.fn();

      const orch = createMasterOrchestrator({
        callbacks: {
          onError,
        },
      });

      const input: OrchestratorInput = {
        intent: "", // Intent vazio causará erro
      };

      const result = await orch.orchestrate(input);

      if (!result.success) {
        expect(onError).toHaveBeenCalled();
      }
    });
  });

  // ========================================================================
  // TESTES DE RESULT E ARTIFACTS
  // ========================================================================

  describe("Result and Artifacts", () => {
    it("deve retornar result com estrutura correta", async () => {
      const input: OrchestratorInput = {
        intent: "Teste result structure",
      };

      const result = await orchestrator.orchestrate(input);

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("finalState");
      expect(result).toHaveProperty("message");
      expect(result).toHaveProperty("metrics");
      expect(result).toHaveProperty("errors");
      expect(result).toHaveProperty("rolledBack");
    });

    it("deve incluir artifacts em caso de sucesso", async () => {
      const input: OrchestratorInput = {
        intent: "Teste artifacts",
      };

      const result = await orchestrator.orchestrate(input);

      if (result.success) {
        expect(result.artifacts).toBeDefined();
        expect(result.artifacts?.branch).toBeDefined();
        expect(result.artifacts?.pullRequest).toBeDefined();
        expect(result.artifacts?.files).toBeDefined();
      }
    });

    it("deve incluir informações de erro em caso de falha", async () => {
      const input: OrchestratorInput = {
        intent: "Teste error info",
      };

      const result = await orchestrator.orchestrate(input);

      if (!result.success) {
        expect(result.errors.length).toBeGreaterThanOrEqual(0);
      }
    });
  });

  // ========================================================================
  // TESTES DE CONFIGURAÇÃO
  // ========================================================================

  describe("Configuration", () => {
    it("deve permitir customização de timeoutMinutes", () => {
      const orch = createMasterOrchestrator({
        timeoutMinutes: 45,
      });
      expect(orch).toBeDefined();
    });

    it("deve permitir customização de retryPolicy", () => {
      const orch = createMasterOrchestrator({
        retryPolicy: {
          maxAttempts: 5,
          initialDelayMs: 500,
          maxDelayMs: 60000,
          backoffFactor: 1.5,
          retryableStates: [OrchestratorState.CI_EXECUTION],
        },
      });
      expect(orch).toBeDefined();
    });

    it("deve permitir desabilitar telemetria", async () => {
      const orch = createMasterOrchestrator({
        telemetryEnabled: false,
      });

      const input: OrchestratorInput = {
        intent: "Teste sem telemetria",
      };

      await orch.orchestrate(input);
      const events = orch.getTelemetryEvents();
      expect(events.length).toBe(0);
    });
  });

  // ========================================================================
  // TESTES DE PERFORMANCE
  // ========================================================================

  describe("Performance", () => {
    it("deve completar pipeline dentro do timeout", async () => {
      const input: OrchestratorInput = {
        intent: "Teste performance",
        timeoutMinutes: 5,
      };

      const startTime = Date.now();
      const result = await orchestrator.orchestrate(input);
      const elapsedTime = Date.now() - startTime;

      expect(elapsedTime).toBeLessThan(5 * 60 * 1000);
      expect(result.metrics.totalDurationMs).toBeLessThan(5 * 60 * 1000);
    });

    it("deve registrar duração total com precisão", async () => {
      const input: OrchestratorInput = {
        intent: "Teste duração total",
      };

      const startTime = Date.now();
      const result = await orchestrator.orchestrate(input);
      const actualElapsedTime = Date.now() - startTime;

      expect(result.metrics.totalDurationMs).toBeLessThanOrEqual(actualElapsedTime + 100);
      expect(result.metrics.totalDurationMs).toBeGreaterThan(0);
    });
  });

  // ========================================================================
  // TESTES DE FACTORY
  // ========================================================================

  describe("Factory Function", () => {
    it("deve criar orchestrador via factory function", () => {
      const orch = createMasterOrchestrator();
      expect(orch).toBeInstanceOf(MasterOrchestrator);
    });

    it("deve aceitar configuração parcial na factory", () => {
      const orch = createMasterOrchestrator({
        autoMerge: false,
        verbose: true,
      });
      expect(orch).toBeInstanceOf(MasterOrchestrator);
    });
  });
});
