/**
 * Exemplos de Integração — Notifications Service
 *
 * Mostra casos de uso reais:
 * - Notificações de PR (GitHub)
 * - Atualizações de agentes
 * - Falhas de teste
 * - Deployments
 */

import {
  getNotifier,
  NotificationEventType,
  NotificationPriority,
  NotificationEvent,
} from "../services/notifications";

/**
 * Exemplo 1: Pipeline de CI/CD com falhas de teste
 */
export async function exampleCIPipelineTestFailure(): Promise<void> {
  const notifier = getNotifier();
  const userId = "dev_team@mantaassociados.com";
  const buildNumber = "2024.07.31.001";

  console.log("\n=== Exemplo 1: CI Pipeline - Test Failure ===\n");

  // Configura preferências do time
  notifier.setUserPreferences(userId, {
    optin: true,
    channelPreferences: {
      email: true,
      webhook: true,
      inApp: true,
      slack: true,
    },
  });

  // Simula falha de testes individuais
  const testCases = [
    {
      name: "MaestroRouter.routing-saneamento",
      duration: 150,
      error: "Timeout after 100ms",
    },
    {
      name: "MaestroRouter.routing-energia",
      duration: 200,
      error: "AssertionError: expected high confidence",
    },
  ];

  for (const testCase of testCases) {
    const event: NotificationEvent = {
      id: `test_${buildNumber}_${testCase.name}`,
      type: NotificationEventType.TEST_FAILED,
      userId,
      timestamp: new Date(),
      priority: NotificationPriority.HIGH,
      data: {
        testName: testCase.name,
        suite: "src/services/__tests__",
        failureCount: 1,
        errorSummary: testCase.error,
        duration: testCase.duration,
        buildNumber,
      },
      groupKey: `test_build_${buildNumber}`, // Agrupa todas as falhas do build
      metadata: {
        source: "github-actions",
        tags: ["ci", "test", `build_${buildNumber}`],
      },
    };

    await notifier.addEvent(event);
    console.log(`  📨 Evento adicionado: ${testCase.name}`);
  }

  // Aguarda agrupamento
  console.log("\n  ⏳ Aguardando processamento agrupado...");
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Mostra estatísticas
  const stats = notifier.getDeliveryStats(userId);
  console.log("\n  📊 Estatísticas:");
  console.log(`     Total enviado: ${stats.totalSent}`);
  console.log(`     Entregue: ${stats.totalDelivered}`);
  console.log(`     Taxa de entrega: ${stats.deliveryRate.toFixed(1)}%`);
}

/**
 * Exemplo 2: Notificações de Pull Request (GitHub)
 */
export async function exampleGitHubPRNotifications(): Promise<void> {
  const notifier = getNotifier();
  const maintainerId = "mauricio@mantaassociados.com";

  console.log("\n=== Exemplo 2: GitHub - PR Notifications ===\n");

  // Configura preferências do maintainer
  notifier.setUserPreferences(maintainerId, {
    optin: true,
    channelPreferences: {
      email: false,
      webhook: true,
      inApp: true,
      slack: true,
    },
  });

  // Simula eventos de PR
  const prEvents: Array<{
    type: NotificationEventType;
    data: Record<string, unknown>;
  }> = [
    {
      type: NotificationEventType.PR_OPENED,
      data: {
        prNumber: 456,
        prTitle: "Add notifications service",
        author: "john_doe",
        repository: "codex-exemplo",
        branch: "feature/notifications",
      },
    },
    {
      type: NotificationEventType.PR_REVIEW_REQUESTED,
      data: {
        prNumber: 456,
        requester: "ci_bot",
        reviewers: [maintainerId],
      },
    },
    {
      type: NotificationEventType.PR_MERGED,
      data: {
        prNumber: 456,
        prTitle: "Add notifications service",
        targetBranch: "main",
        mergedBy: "jane_doe",
      },
    },
  ];

  for (const prEvent of prEvents) {
    const event: NotificationEvent = {
      id: `pr_456_${prEvent.type}`,
      type: prEvent.type,
      userId: maintainerId,
      timestamp: new Date(),
      priority:
        prEvent.type === NotificationEventType.PR_REVIEW_REQUESTED
          ? NotificationPriority.HIGH
          : NotificationPriority.MEDIUM,
      data: prEvent.data,
      groupKey: "pr_456_lifecycle", // Agrupa ciclo de vida do PR
      metadata: {
        source: "github",
        tags: ["pr", "456", "notifications"],
      },
    };

    await notifier.addEvent(event);
    console.log(
      `  📨 PR evento: ${prEvent.type.toUpperCase()}`
    );
  }

  console.log("\n  ⏳ Aguardando processamento...");
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Mostra histórico
  const history = notifier.getNotificationHistory(maintainerId);
  console.log("\n  📋 Histórico:");
  console.log(`     Total: ${history.summary.total}`);
  console.log(`     Entregue: ${history.summary.delivered}`);
  console.log(`     Aberta: ${history.summary.opened}`);
}

/**
 * Exemplo 3: Atualizações de Agentes (Sistema interno)
 */
export async function exampleAgentUpdates(): Promise<void> {
  const notifier = getNotifier();
  const userId = "mneves@mantaassociados.com";

  console.log("\n=== Exemplo 3: Agent Updates ===\n");

  // Configura preferências
  notifier.setUserPreferences(userId, {
    optin: true,
    channelPreferences: {
      email: true,
      webhook: false,
      inApp: true,
      slack: true,
    },
  });

  // Simula atualizações de agentes
  const agentUpdates = [
    {
      agentName: "agente-saneamento",
      agentCode: "Manta 03-S8",
      updateSummary: "Atualizado: keywords de SNIS, Lei 14.026",
      environment: "staging",
    },
    {
      agentName: "agente-energia",
      agentCode: "Manta 03-S9",
      updateSummary: "Corrigido: scoring de transmissão",
      environment: "production",
    },
  ];

  for (const update of agentUpdates) {
    // Evento de atualização
    const updateEvent: NotificationEvent = {
      id: `agent_update_${update.agentCode}`,
      type: NotificationEventType.AGENT_UPDATED,
      userId,
      timestamp: new Date(),
      priority: NotificationPriority.MEDIUM,
      data: {
        agentName: update.agentName,
        agentCode: update.agentCode,
        updateSummary: update.updateSummary,
        timestamp: new Date().toISOString(),
      },
      groupKey: "agent_updates_batch",
      metadata: {
        source: "system",
        tags: ["agent", update.agentCode.split(" ")[2].toLowerCase()],
      },
    };

    // Evento de deployment (se em production)
    if (update.environment === "production") {
      const deployEvent: NotificationEvent = {
        id: `agent_deploy_${update.agentCode}`,
        type: NotificationEventType.AGENT_DEPLOYED,
        userId,
        timestamp: new Date(Date.now() + 100), // 100ms depois
        priority: NotificationPriority.HIGH,
        data: {
          agentName: update.agentName,
          agentCode: update.agentCode,
          environment: update.environment,
          deploymentTime: new Date().toISOString(),
          version: "4.2.0",
        },
        groupKey: "agent_updates_batch",
        metadata: {
          source: "system",
          tags: ["agent", "deploy"],
        },
      };

      await notifier.addEvent(deployEvent);
      console.log(
        `  🚀 Deployment: ${update.agentName} → ${update.environment}`
      );
    }

    await notifier.addEvent(updateEvent);
    console.log(`  🔄 Update: ${update.agentName} - ${update.updateSummary}`);
  }

  console.log("\n  ⏳ Aguardando processamento...");
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Mostra rate limit
  const rateLimit = notifier.getRateLimitMetrics(userId);
  console.log("\n  ⏱️ Rate Limit:");
  console.log(`     Eventos/minuto: ${rateLimit.eventsLastMinute}`);
  console.log(`     Throttled: ${rateLimit.throttled ? "Sim" : "Não"}`);
}

/**
 * Exemplo 4: Deployment Pipeline
 */
export async function exampleDeploymentPipeline(): Promise<void> {
  const notifier = getNotifier();
  const opsTeam = "ops@mantaassociados.com";

  console.log("\n=== Exemplo 4: Deployment Pipeline ===\n");

  // Configura preferências da ops
  notifier.setUserPreferences(opsTeam, {
    optin: true,
    channelPreferences: {
      email: false,
      webhook: true,
      inApp: true,
      slack: true,
    },
  });

  const deploymentId = `deploy_${Date.now()}`;
  const stages = [
    { name: "Staging", status: "started" },
    { name: "Health check", status: "started" },
    { name: "Production", status: "started" },
  ];

  // Eventos de deployment
  for (const stage of stages) {
    if (stage.status === "started") {
      const event: NotificationEvent = {
        id: `${deploymentId}_${stage.name}`,
        type: NotificationEventType.DEPLOYMENT_STARTED,
        userId: opsTeam,
        timestamp: new Date(),
        priority: NotificationPriority.HIGH,
        data: {
          environment: stage.name.toLowerCase(),
          version: "1.2.3",
          deploymentId,
          stage: stage.name,
        },
        groupKey: `deployment_${deploymentId}`,
        metadata: {
          source: "deployment-system",
          tags: ["deployment", "production"],
        },
      };

      await notifier.addEvent(event);
      console.log(`  🚀 Iniciado: ${stage.name}`);
    }

    // Simula tempo de deployment
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Completion event
    const completionEvent: NotificationEvent = {
      id: `${deploymentId}_${stage.name}_complete`,
      type: NotificationEventType.DEPLOYMENT_COMPLETED,
      userId: opsTeam,
      timestamp: new Date(),
      priority: NotificationPriority.HIGH,
      data: {
        environment: stage.name.toLowerCase(),
        version: "1.2.3",
        deploymentId,
        stage: stage.name,
        duration: "2m 34s",
      },
      groupKey: `deployment_${deploymentId}`,
      metadata: {
        source: "deployment-system",
        tags: ["deployment", "complete"],
      },
    };

    await notifier.addEvent(completionEvent);
    console.log(`  ✅ Completado: ${stage.name}`);
  }

  console.log("\n  ⏳ Aguardando processamento...");
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Mostra analytics completo
  const stats = notifier.getDeliveryStats(opsTeam);
  console.log("\n  📊 Analytics:");
  console.log(`     Total: ${stats.totalSent}`);
  console.log(`     Taxa de entrega: ${stats.deliveryRate.toFixed(1)}%`);
  console.log(
    `     Tempo médio: ${stats.averageDeliveryTimeMs.toFixed(0)}ms`
  );

  console.log("\n  📡 Por Canal:");
  for (const [channel, data] of Object.entries(stats.byChannel)) {
    console.log(`     ${channel}: ${data.sent} enviado, ${data.delivered} entregue`);
  }
}

/**
 * Exemplo 5: Preferências de Usuário e Opt-in/Opt-out
 */
export async function exampleUserPreferences(): Promise<void> {
  const notifier = getNotifier();
  const userId = "user_preferences_demo";

  console.log("\n=== Exemplo 5: User Preferences ===\n");

  // Estado inicial
  console.log("  Estado inicial:");
  const initialPrefs = notifier.getUserPreferences(userId);
  console.log(`    Optin: ${initialPrefs.optin}`);
  console.log(`    Email: ${initialPrefs.channelPreferences.email}`);
  console.log(`    Slack: ${initialPrefs.channelPreferences.slack}`);

  // Usuário desabilita email
  console.log("\n  Usuário desabilita notificações por email...");
  notifier.setUserPreferences(userId, {
    channelPreferences: {
      email: false,
      webhook: true,
      inApp: true,
      slack: true,
    },
  });

  // Usuário desabilita um tipo de evento
  console.log("  Usuário desabilita TEST_PASSED...");
  notifier.setEventTypePreference(
    userId,
    NotificationEventType.TEST_PASSED,
    false
  );

  // Mostra preferências atualizadas
  console.log("\n  Preferências atualizadas:");
  const updatedPrefs = notifier.getUserPreferences(userId);
  console.log(`    Email: ${updatedPrefs.channelPreferences.email}`);
  console.log(`    TEST_PASSED: ${updatedPrefs.eventTypePreferences.get(NotificationEventType.TEST_PASSED)}`);

  // Tenta adicionar TEST_PASSED (será descartado)
  console.log("\n  Adicionando TEST_PASSED (será descartado)...");
  const testPassedEvent: NotificationEvent = {
    id: "evt_test_passed_123",
    type: NotificationEventType.TEST_PASSED,
    userId,
    timestamp: new Date(),
    priority: NotificationPriority.LOW,
    data: {
      suite: "test_suite",
      totalTests: 100,
    },
    groupKey: "test_group",
  };

  await notifier.addEvent(testPassedEvent);
  console.log("  ✅ Evento descartado (type desabilitado)");

  // Usuário faz opt-out completo
  console.log("\n  Usuário faz opt-out total...");
  notifier.setUserPreferences(userId, { optin: false });

  // Tenta adicionar evento (será descartado)
  const prEvent: NotificationEvent = {
    id: "evt_pr_optout",
    type: NotificationEventType.PR_OPENED,
    userId,
    timestamp: new Date(),
    priority: NotificationPriority.MEDIUM,
    data: { prNumber: 999 },
    groupKey: "pr_optout",
  };

  await notifier.addEvent(prEvent);
  console.log("  ✅ Evento descartado (user opted out)");
}

/**
 * Executar todos os exemplos
 */
export async function runAllExamples(): Promise<void> {
  console.log("╔════════════════════════════════════════════════════════════════╗");
  console.log("║         NOTIFICATIONS SERVICE - INTEGRATION EXAMPLES           ║");
  console.log("╚════════════════════════════════════════════════════════════════╝");

  try {
    await exampleCIPipelineTestFailure();
    await exampleGitHubPRNotifications();
    await exampleAgentUpdates();
    await exampleDeploymentPipeline();
    await exampleUserPreferences();

    console.log(
      "\n╔════════════════════════════════════════════════════════════════╗"
    );
    console.log("║                    ALL EXAMPLES COMPLETED                       ║");
    console.log(
      "╚════════════════════════════════════════════════════════════════╝\n"
    );
  } catch (error) {
    console.error("\n❌ Error in examples:", error);
  }
}

// Se executado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllExamples().catch(console.error);
}
