/**
 * Exemplos de uso do Master Orchestrator
 * Demonstra casos de uso reais e padrões de integração
 */

import {
  createMasterOrchestrator,
  OrchestratorState,
  TelemetryEventType,
  type OrchestratorResult,
  type OrchestratorInput,
} from "../orchestrator";

// ============================================================================
// EXEMPLO 1: Pipeline Básico Simples
// ============================================================================

export async function basicPipelineExample() {
  console.log("\n=== Exemplo 1: Pipeline Básico ===\n");

  const orchestrator = createMasterOrchestrator({
    timeoutMinutes: 30,
    verbose: true,
  });

  const input: OrchestratorInput = {
    intent:
      "Criar novo agente para análise automática de documentos de saneamento",
    segment: "Saneamento",
    userEmail: "developer@manta.com",
    tags: ["priority-high", "feature-new"],
  };

  try {
    const result = await orchestrator.orchestrate(input);

    console.log("\n📊 Resultado Final:");
    console.log(`  Status: ${result.success ? "✓ Sucesso" : "✗ Falha"}`);
    console.log(`  Estado Final: ${result.finalState}`);
    console.log(`  Duração Total: ${result.metrics.totalDurationMs}ms`);

    if (result.artifacts?.pullRequest) {
      console.log(
        `  PR criada: ${result.artifacts.pullRequest.url}`
      );
    }
  } catch (error) {
    console.error("Erro no pipeline:", error);
  }
}

// ============================================================================
// EXEMPLO 2: Com Listeners de Estado
// ============================================================================

export async function stateChangeListenerExample() {
  console.log("\n=== Exemplo 2: Rastreamento de Transições de Estado ===\n");

  const orchestrator = createMasterOrchestrator({
    verbose: false,
  });

  // Rastrear mudanças de estado
  orchestrator.on("stateChange", (data) => {
    const duration = new Date().getTime();
    console.log(
      `⏱️  [${duration}] ${data.previousState} → ${data.newState}`
    );
  });

  const input: OrchestratorInput = {
    intent: "Criar novo agente para análise de energia elétrica",
    segment: "Energia",
  };

  const result = await orchestrator.orchestrate(input);

  console.log(
    `\n✓ Pipeline concluído em estado: ${result.finalState}`
  );
}

// ============================================================================
// EXEMPLO 3: Telemetria e Métricas
// ============================================================================

export async function telemetryExample() {
  console.log("\n=== Exemplo 3: Coleta de Telemetria ===\n");

  const orchestrator = createMasterOrchestrator({
    telemetryEnabled: true,
    verbose: false,
  });

  const phaseMetrics: Record<string, number> = {};

  // Coletar eventos de telemetria
  orchestrator.on("telemetry", (event) => {
    if (event.type === TelemetryEventType.PHASE_COMPLETED) {
      phaseMetrics[event.state] = event.phaseDuration || 0;
      console.log(
        `📈 ${event.state}: ${event.phaseDuration}ms`
      );
    }
  });

  const input: OrchestratorInput = {
    intent: "Gerar código para novo módulo de análise",
  };

  const result = await orchestrator.orchestrate(input);

  console.log("\n📊 Resumo de Métricas:");
  console.log(`  Duração Total: ${result.metrics.totalDurationMs}ms`);
  console.log(`  Erros: ${result.metrics.errorCount}`);
  console.log(`  Retries: ${result.metrics.retryCount}`);
  console.log(`  Taxa de Sucesso: ${(result.metrics.successRate * 100).toFixed(0)}%`);

  // Mostrar duração por fase
  console.log("\n⏱️  Duração por Fase:");
  Object.entries(phaseMetrics).forEach(([phase, duration]) => {
    if (duration > 0) {
      console.log(`  ${phase}: ${duration}ms`);
    }
  });
}

// ============================================================================
// EXEMPLO 4: Callbacks Customizados
// ============================================================================

export async function callbacksExample() {
  console.log("\n=== Exemplo 4: Callbacks Customizados ===\n");

  const orchestrator = createMasterOrchestrator({
    callbacks: {
      onStateChange: async (state) => {
        console.log(`🔄 Transição para estado: ${state}`);

        // Aqui você poderia enviar notificação, atualizar UI, etc
        await simulateNotification(
          `Estado alterado para ${state}`
        );
      },

      onError: async (error) => {
        console.error(`❌ Erro em ${error.state}:`);
        console.error(`   ${error.message}`);
        console.error(`   Severidade: ${error.severity}`);
        console.error(`   ID: ${error.id}`);

        // Aqui você poderia registrar em serviço de erro, enviar alerta, etc
        await simulateErrorTracking({
          errorId: error.id,
          state: error.state,
          message: error.message,
          severity: error.severity,
        });
      },

      onSuccess: async (result) => {
        console.log(`✅ Pipeline completado com sucesso!`);
        console.log(
          `   Duração: ${result.metrics.totalDurationMs}ms`
        );

        if (result.artifacts?.pullRequest) {
          console.log(
            `   PR: ${result.artifacts.pullRequest.url}`
          );
          await simulateSlackNotification(
            `✅ PR criada: ${result.artifacts.pullRequest.url}`
          );
        }
      },
    },
  });

  const input: OrchestratorInput = {
    intent: "Implementar nova funcionalidade de análise",
  };

  await orchestrator.orchestrate(input);
}

// ============================================================================
// EXEMPLO 5: Retry Policy Customizado
// ============================================================================

export async function retryPolicyExample() {
  console.log("\n=== Exemplo 5: Retry Policy Customizado ===\n");

  const orchestrator = createMasterOrchestrator({
    retryPolicy: {
      maxAttempts: 5,           // Permitir até 5 tentativas
      initialDelayMs: 500,      // Começar com 500ms
      maxDelayMs: 60000,        // Máximo 60 segundos
      backoffFactor: 1.5,       // 50% de aumento a cada tentativa
      retryableStates: [
        OrchestratorState.CODE_GENERATION,
        OrchestratorState.CI_EXECUTION,
      ],
    },
    verbose: true,
  });

  const input: OrchestratorInput = {
    intent: "Gerar código com retry agressivo para testes",
    timeoutMinutes: 10,
  };

  const result = await orchestrator.orchestrate(input);

  console.log("\n📊 Estatísticas de Retry:");
  console.log(`  Total de Retries: ${result.metrics.retryCount}`);
  console.log(`  Total de Erros: ${result.metrics.errorCount}`);

  // Listar detalhes de cada retry
  if (result.metrics.retries.length > 0) {
    console.log("\n  Detalhes de Retries:");
    result.metrics.retries.forEach((retry, index) => {
      console.log(`    ${index + 1}. Tentativa ${retry.attemptNumber}`);
      console.log(`       Estado: ${retry.previousState}`);
      console.log(
        `       Resultado: ${retry.status}`
      );
      console.log(`       Duração: ${retry.duration}ms`);
    });
  }
}

// ============================================================================
// EXEMPLO 6: Timeout Handling
// ============================================================================

export async function timeoutHandlingExample() {
  console.log("\n=== Exemplo 6: Timeout Handling ===\n");

  const orchestrator = createMasterOrchestrator({
    timeoutMinutes: 2,  // 2 minutos de timeout
    autoRollback: true,
    verbose: true,
  });

  // Monitorar progresso
  let monitorInterval = setInterval(() => {
    console.log(
      `  Estado atual: ${orchestrator.getCurrentState()}`
    );
  }, 500);

  try {
    const input: OrchestratorInput = {
      intent: "Testar com timeout curto",
      timeoutMinutes: 1,  // Override com 1 minuto
    };

    const result = await orchestrator.orchestrate(input);

    console.log(
      `\n✓ Pipeline concluído: ${result.finalState}`
    );
    console.log(
      `  Duração: ${result.metrics.totalDurationMs}ms`
    );

    if (result.metrics.timeoutCount > 0) {
      console.log(
        `  Timeouts detectados: ${result.metrics.timeoutCount}`
      );
    }
  } finally {
    clearInterval(monitorInterval);
  }
}

// ============================================================================
// EXEMPLO 7: Audit Trail Completo
// ============================================================================

export async function auditTrailExample() {
  console.log("\n=== Exemplo 7: Exportar Audit Trail ===\n");

  const orchestrator = createMasterOrchestrator({
    telemetryEnabled: true,
  });

  const input: OrchestratorInput = {
    intent: "Execução para auditoria completa",
    tags: ["audit", "compliance"],
  };

  const result = await orchestrator.orchestrate(input);

  // Exportar audit trail
  const auditTrail = orchestrator.exportAuditTrail();

  console.log("📋 Audit Trail:");
  console.log(`  Iniciado em: ${auditTrail.startedAt.toISOString()}`);
  console.log(
    `  Finalizado em: ${auditTrail.endedAt?.toISOString() || "Em progresso"}`
  );
  console.log(
    `  Duração Total: ${auditTrail.totalDurationMs}ms`
  );
  console.log(
    `  Estado Final: ${auditTrail.finalState}`
  );

  console.log("\n🔄 Transições de Estado:");
  auditTrail.stateTransitions.forEach((transition, index) => {
    console.log(`  ${index + 1}. ${transition.from} → ${transition.to}`);
  });

  if (auditTrail.errors.length > 0) {
    console.log("\n❌ Erros Ocorridos:");
    auditTrail.errors.forEach((error, index) => {
      console.log(`  ${index + 1}. ${error.message}`);
      console.log(`     Estado: ${error.state}`);
      console.log(`     Severidade: ${error.severity}`);
      console.log(`     ID: ${error.id}`);
    });
  }

  if (auditTrail.retries.length > 0) {
    console.log("\n🔁 Retries Executados:");
    auditTrail.retries.forEach((retry, index) => {
      console.log(`  ${index + 1}. Tentativa ${retry.attemptNumber}`);
      console.log(`     Status: ${retry.status}`);
      console.log(`     Duração: ${retry.duration}ms`);
    });
  }

  console.log(
    `\n📊 Total de Eventos de Telemetria: ${auditTrail.telemetryEvents.length}`
  );
}

// ============================================================================
// EXEMPLO 8: Cenário de Produção
// ============================================================================

export async function productionScenarioExample() {
  console.log("\n=== Exemplo 8: Cenário de Produção ===\n");

  const orchestrator = createMasterOrchestrator({
    timeoutMinutes: 45,  // 45 minutos
    autoRollback: true,
    autoMerge: false,    // Requer aprovação em produção
    telemetryEnabled: true,
    verbose: false,

    retryPolicy: {
      maxAttempts: 3,
      initialDelayMs: 2000,
      maxDelayMs: 30000,
      backoffFactor: 2,
      retryableStates: [
        OrchestratorState.CI_EXECUTION,
        OrchestratorState.CODE_GENERATION,
      ],
    },

    callbacks: {
      onStateChange: async (state) => {
        // Enviar métrica para Prometheus
        await recordMetric("orchestrator.state.change", {
          state,
        });
      },

      onError: async (error) => {
        // Logar erro estruturado
        console.error({
          type: "ORCHESTRATOR_ERROR",
          errorId: error.id,
          state: error.state,
          message: error.message,
          severity: error.severity,
          timestamp: error.timestamp,
        });

        // Enviar para serviço de erro (Sentry, etc)
        await reportError({
          errorId: error.id,
          state: error.state,
          message: error.message,
          stack: error.stack,
        });
      },

      onSuccess: async (result) => {
        // Logar sucesso
        console.log({
          type: "ORCHESTRATOR_SUCCESS",
          duration: result.metrics.totalDurationMs,
          finalState: result.finalState,
          artifacts: result.artifacts,
        });

        // Enviar notificação
        if (result.artifacts?.pullRequest) {
          await sendSlackMessage({
            channel: "#deployments",
            text: `✅ Nova PR criada: ${result.artifacts.pullRequest.url}`,
            metadata: {
              branch: result.artifacts.branch,
              prNumber: result.artifacts.pullRequest.number,
            },
          });
        }
      },
    },
  });

  const input: OrchestratorInput = {
    intent:
      "Implementar nova funcionalidade de análise com confiança",
    segment: "Saneamento",
    userEmail: "ops@manta.com",
    tags: ["prod", "feature", "high-priority"],
    timeoutMinutes: 40,
    requireApproval: true,  // Requer aprovação
  };

  try {
    console.log("🚀 Iniciando pipeline de produção...\n");

    const result = await orchestrator.orchestrate(input);

    if (result.success) {
      console.log("✅ Pipeline concluído com sucesso!");
      console.log(`   Duração: ${result.metrics.totalDurationMs}ms`);
      console.log(
        `   PR: ${result.artifacts?.pullRequest?.url}`
      );
      console.log("   Aguardando aprovação para merge...");
    } else if (result.rolledBack) {
      console.log("🔄 Pipeline falhou e foi feito rollback");
      console.log(`   Razão: ${result.rollbackDetails?.reason}`);
    } else {
      console.log("❌ Pipeline falhou");
      console.log(`   Mensagem: ${result.message}`);
      console.log(`   Erros: ${result.errors.length}`);
    }

    // Salvar audit trail para conformidade
    const auditTrail = orchestrator.exportAuditTrail();
    await saveAuditTrailToDatabase(auditTrail);
  } catch (error) {
    console.error("Erro fatal no pipeline:", error);
  }
}

// ============================================================================
// Funções Auxiliares (Simuladas)
// ============================================================================

async function simulateNotification(message: string): Promise<void> {
  // Simulação de notificação
  console.log(`  📬 Notificação: ${message}`);
}

async function simulateErrorTracking(
  errorData: any
): Promise<void> {
  // Simulação de rastreamento de erro
  console.log(`  🔍 Erro rastreado: ${errorData.errorId}`);
}

async function simulateSlackNotification(
  message: string
): Promise<void> {
  // Simulação de envio para Slack
  console.log(`  💬 Slack: ${message}`);
}

async function recordMetric(
  metricName: string,
  _data: any
): Promise<void> {
  // Simulação de gravação de métrica
  // console.log(`  📊 Métrica: ${metricName}`);
}

async function reportError(_errorData: any): Promise<void> {
  // Simulação de reporte de erro
  // console.log(`  📨 Erro reportado`);
}

async function sendSlackMessage(
  _message: any
): Promise<void> {
  // Simulação de envio para Slack
  // console.log(`  💬 Mensagem Slack enviada`);
}

async function saveAuditTrailToDatabase(
  _auditTrail: any
): Promise<void> {
  // Simulação de salvamento em banco de dados
  // console.log(`  💾 Audit trail salvo`);
}

// ============================================================================
// Função para executar todos os exemplos
// ============================================================================

export async function runAllExamples() {
  console.log("╔════════════════════════════════════════════════════════╗");
  console.log("║   Master Orchestrator - Exemplos de Uso                 ║");
  console.log("╚════════════════════════════════════════════════════════╝");

  try {
    // Descomente o exemplo que deseja executar
    await basicPipelineExample();
    // await stateChangeListenerExample();
    // await telemetryExample();
    // await callbacksExample();
    // await retryPolicyExample();
    // await timeoutHandlingExample();
    // await auditTrailExample();
    // await productionScenarioExample();
  } catch (error) {
    console.error("Erro ao executar exemplos:", error);
  }
}

// Executar se este arquivo for o entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllExamples().catch(console.error);
}
