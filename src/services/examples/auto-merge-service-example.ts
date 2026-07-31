/**
 * Exemplos práticos de uso do AutoMerge Service
 * Phase 4: Automação avançada de merge com locking distribuído
 */

import { createAutoMerge, AutoMerge } from "../auto-merge-service";
import type {
  AutoMergeServiceConfig,
  MergeResult,
  Requirement,
  Conflict,
  ScheduleResult,
  MergeMetrics,
} from "../auto-merge-service";

// ============================================================================
// EXEMPLO 1: Merge Básico com Verificações
// ============================================================================

export async function example1_basicMerge() {
  console.log("\n=== EXEMPLO 1: Merge Básico ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
    requireCIPassed: true,
    requiredApprovals: 1,
    defaultStrategy: "squash",
  });

  const prNumber = 123;

  // 1. Verificar se pode fazer merge
  console.log("1. Verificando se PR pode ser mergido...");
  const canMerge = await autoMerge.canMerge({ number: prNumber });
  console.log(`   Resultado: ${canMerge ? "SIM" : "NÃO"}\n`);

  if (!canMerge) {
    console.log("2. Analisando motivo do bloqueio...");
    const requirements = await autoMerge.checkRequirements({ number: prNumber });
    const unmet = requirements.filter((r) => !r.met);

    unmet.forEach((req) => {
      console.log(`   ✗ ${req.type}`);
      console.log(`     ${req.description}`);
      if (req.currentValue) {
        console.log(`     Atual: ${req.currentValue}`);
      }
    });
    return;
  }

  // 2. Realizar merge
  console.log("2. Realizando merge...");
  const result = await autoMerge.merge(prNumber, "squash");

  if (result.success) {
    console.log(`   ✓ Merge realizado com sucesso!`);
    console.log(`     Commit: ${result.mergeCommitSha}`);
    console.log(`     Duração: ${result.duration}ms`);
  } else {
    console.log(`   ✗ Merge falhou`);
    console.log(`     Código: ${result.error?.code}`);
    console.log(`     Mensagem: ${result.error?.message}`);
    console.log(`     Recuperável: ${result.error?.recoverable}`);
  }
}

// ============================================================================
// EXEMPLO 2: Análise Completa de Requisitos
// ============================================================================

export async function example2_requirementsAnalysis() {
  console.log("\n=== EXEMPLO 2: Análise de Requisitos ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
  });

  const prNumber = 456;

  console.log("Verificando todos os requisitos de merge...\n");

  const requirements = await autoMerge.checkRequirements({ number: prNumber });

  // Agrupar por status
  const met = requirements.filter((r) => r.met);
  const unmet = requirements.filter((r) => !r.met);

  console.log(`✓ Requisitos Atendidos (${met.length}):`);
  met.forEach((req) => {
    console.log(`  ✓ ${req.type}`);
    console.log(`    ${req.description}`);
  });

  if (unmet.length > 0) {
    console.log(`\n✗ Requisitos Não Atendidos (${unmet.length}):`);
    unmet.forEach((req) => {
      console.log(`  ✗ ${req.type}`);
      console.log(`    ${req.description}`);
      if (req.currentValue && req.requiredValue) {
        console.log(`    Atual: ${req.currentValue} | Requerido: ${req.requiredValue}`);
      }
      if (req.checkDetails) {
        console.log(`    Detalhes: ${JSON.stringify(req.checkDetails)}`);
      }
    });
  }

  console.log(`\nResumo: ${met.length}/${requirements.length} requisitos atendidos`);
}

// ============================================================================
// EXEMPLO 3: Detecção e Análise de Conflitos
// ============================================================================

export async function example3_conflictDetection() {
  console.log("\n=== EXEMPLO 3: Detecção de Conflitos ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
  });

  const prNumber = 789;

  console.log("Procurando por conflitos de merge...\n");

  const conflicts = await autoMerge.getConflicts({ number: prNumber });

  if (conflicts.length === 0) {
    console.log("✓ Nenhum conflito detectado! PR está pronto para merge.\n");
    return;
  }

  console.log(`✗ ${conflicts.length} conflito(s) detectado(s):\n`);

  // Agrupar por severidade
  const bySeverity = conflicts.reduce(
    (acc, c) => {
      if (!acc[c.severity]) acc[c.severity] = [];
      acc[c.severity].push(c);
      return acc;
    },
    {} as Record<string, Conflict[]>
  );

  ["high", "medium", "low"].forEach((severity) => {
    const list = bySeverity[severity];
    if (!list) return;

    console.log(`${severity.toUpperCase()} SEVERITY (${list.length}):`);
    list.forEach((conflict) => {
      console.log(`\n  Arquivo: ${conflict.file}`);
      console.log(`  Tipo: ${conflict.type}`);
      console.log(`  Descrição: ${conflict.description}`);
      console.log(`  Resolvível: ${conflict.resolvable ? "SIM" : "NÃO"}`);

      if (conflict.suggestedResolution) {
        console.log(`  Sugestão: ${conflict.suggestedResolution}`);
      }

      if (conflict.lineRange) {
        console.log(`  Linhas: ${conflict.lineRange.start}-${conflict.lineRange.end}`);
      }
    });
  });
}

// ============================================================================
// EXEMPLO 4: Merge com Estratégias Diferentes
// ============================================================================

export async function example4_mergeStrategies() {
  console.log("\n=== EXEMPLO 4: Diferentes Estratégias de Merge ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
  });

  const strategies = ["merge", "squash", "rebase", "cherry-pick", "fast-forward"] as const;
  const prNumber = 999;

  console.log(`Testando diferentes estratégias para PR #${prNumber}\n`);

  for (const strategy of strategies) {
    console.log(`Tentando merge com estratégia: ${strategy.toUpperCase()}`);

    const result = await autoMerge.merge(prNumber, strategy);

    if (result.success) {
      console.log(`  ✓ Sucesso`);
      console.log(`    Commit: ${result.mergeCommitSha?.substring(0, 7)}`);
      console.log(`    Duração: ${result.duration}ms`);
    } else {
      console.log(`  ✗ Falhou: ${result.error?.code}`);
      if (result.error?.recoverable) {
        console.log(`    (Erro recuperável)`);
      }
    }

    console.log();
  }
}

// ============================================================================
// EXEMPLO 5: Agendamento de Merge
// ============================================================================

export async function example5_scheduleMerge() {
  console.log("\n=== EXEMPLO 5: Agendamento de Merge ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
    enableScheduling: true,
  });

  const prNumber = 111;

  // Agenda para diferentes horários
  const times = [
    { label: "5 minutos", offset: 5 * 60 * 1000 },
    { label: "1 hora", offset: 60 * 60 * 1000 },
    { label: "8 horas", offset: 8 * 60 * 60 * 1000 },
    { label: "1 dia", offset: 24 * 60 * 60 * 1000 },
  ];

  console.log(`Agendando merges para PR #${prNumber}\n`);

  const scheduleIds: string[] = [];

  for (const { label, offset } of times) {
    const scheduledFor = new Date(Date.now() + offset);

    const result = await autoMerge.scheduleMerge(
      prNumber,
      scheduledFor,
      "squash"
    );

    if (result.success) {
      console.log(`✓ Agendado para ${label}`);
      console.log(`  ID: ${result.scheduleId}`);
      console.log(`  Hora: ${scheduledFor.toISOString()}`);
      scheduleIds.push(result.scheduleId);
    } else {
      console.log(`✗ Falha ao agendar para ${label}: ${result.message}`);
    }
  }

  // Listar agendamentos
  console.log("\nAgendamentos ativos:");
  const scheduled = autoMerge.getScheduledMerges();
  scheduled.forEach((merge) => {
    console.log(`  PR #${merge.prNumber}`);
    console.log(`    Status: ${merge.status}`);
    console.log(`    Estratégia: ${merge.strategy}`);
    console.log(`    Horário: ${new Date(merge.scheduledFor).toISOString()}`);
  });

  // Cancelar alguns agendamentos
  console.log("\nCancelando alguns agendamentos...");
  for (let i = 0; i < Math.min(2, scheduleIds.length); i++) {
    const success = autoMerge.cancelSchedule(scheduleIds[i]);
    console.log(`  ${success ? "✓" : "✗"} Cancelado: ${scheduleIds[i]}`);
  }
}

// ============================================================================
// EXEMPLO 6: Rastreamento de Métricas
// ============================================================================

export async function example6_metrics() {
  console.log("\n=== EXEMPLO 6: Rastreamento de Métricas ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
    trackMetrics: true,
  });

  // Simular alguns merges
  console.log("Simulando operações de merge...\n");

  for (let i = 1; i <= 3; i++) {
    await autoMerge.merge(100 + i, i % 2 === 0 ? "squash" : "rebase");
  }

  // Obter métricas
  const metrics = autoMerge.getMetrics();

  console.log("=== MÉTRICAS GERAIS ===\n");
  console.log(`Total de Merges: ${metrics.totalMerges}`);
  console.log(`Merges bem-sucedidos: ${metrics.successfulMerges}`);
  console.log(`Merges falhados: ${metrics.failedMerges}`);
  console.log(`Taxa de sucesso: ${metrics.successRate.toFixed(2)}%`);
  console.log(`Duração média: ${metrics.averageDuration.toFixed(0)}ms`);
  console.log(`Taxa de conflito: ${metrics.conflictRate.toFixed(2)}%\n`);

  console.log("=== ESTRATÉGIAS UTILIZADAS ===\n");
  Object.entries(metrics.mergeStrategiesUsed).forEach(([strategy, count]) => {
    if (count > 0) {
      const percentage = ((count / metrics.totalMerges) * 100).toFixed(1);
      console.log(`${strategy}: ${count} (${percentage}%)`);
    }
  });

  console.log("\n=== BLOQUEIOS POR REQUISITO ===\n");
  const blockedMerges = Object.entries(metrics.blockedByRequirement).filter(
    ([, count]) => count > 0
  );

  if (blockedMerges.length === 0) {
    console.log("Nenhum bloqueio registrado");
  } else {
    blockedMerges.forEach(([requirement, count]) => {
      console.log(`${requirement}: ${count}`);
    });
  }

  console.log("\n=== TEMPO DE ESPERA DE LOCK ===\n");
  console.log(
    `Média: ${metrics.lockWaitTime.average.toFixed(0)}ms`
  );
  console.log(`Máximo: ${metrics.lockWaitTime.max.toFixed(0)}ms`);
  console.log(`Mínimo: ${metrics.lockWaitTime.min.toFixed(0)}ms`);

  if (metrics.lastMergeAt) {
    console.log(
      `\nÚltimo merge: ${metrics.lastMergeAt.toISOString()}`
    );
  }
}

// ============================================================================
// EXEMPLO 7: Audit Trail e Transações
// ============================================================================

export async function example7_auditTrail() {
  console.log("\n=== EXEMPLO 7: Auditoria e Transações ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
  });

  // Realizar algumas operações
  console.log("Realizando operações e registrando auditoria...\n");

  const mergeResult = await autoMerge.merge(222, "squash");
  const txnId = mergeResult.transactionId;

  console.log(`Transação: ${txnId}\n`);

  // Obter informações da transação
  const transaction = autoMerge.getTransaction(txnId);

  if (transaction) {
    console.log("=== INFORMAÇÕES DA TRANSAÇÃO ===\n");
    console.log(`ID: ${transaction.id}`);
    console.log(`PR: #${transaction.prNumber}`);
    console.log(`Estratégia: ${transaction.strategy}`);
    console.log(`Status: ${transaction.status}`);
    console.log(`Iniciada: ${transaction.startedAt.toISOString()}`);

    if (transaction.completedAt) {
      const duration =
        transaction.completedAt.getTime() - transaction.startedAt.getTime();
      console.log(`Completada: ${transaction.completedAt.toISOString()}`);
      console.log(`Duração: ${duration}ms`);
    }

    if (transaction.error) {
      console.log(`Erro: ${transaction.error}`);
    }
  }

  // Audit trail completo
  console.log("\n=== AUDIT TRAIL ===\n");

  const auditLog = autoMerge.getAuditLog();
  const transactionLog = auditLog.filter((e) => e.transactionId === txnId);

  transactionLog.forEach((entry) => {
    console.log(
      `[${entry.timestamp.toISOString().split("T")[1]}] ${entry.action}`
    );
    console.log(`  Status: ${entry.status}`);
    console.log(`  PR: #${entry.prNumber}`);

    if (Object.keys(entry.details).length > 0) {
      console.log(`  Detalhes: ${JSON.stringify(entry.details, null, 2)}`);
    }
  });
}

// ============================================================================
// EXEMPLO 8: Tratamento de Erros
// ============================================================================

export async function example8_errorHandling() {
  console.log("\n=== EXEMPLO 8: Tratamento de Erros ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
    allowMergingWithConflicts: false,
  });

  const prNumber = 333;

  console.log(`Tentando merge de PR #${prNumber}\n`);

  const result = await autoMerge.merge(prNumber);

  if (!result.success) {
    console.log("✗ Merge falhou\n");

    if (result.error) {
      console.log("=== INFORMAÇÕES DO ERRO ===\n");
      console.log(`Código: ${result.error.code}`);
      console.log(`Mensagem: ${result.error.message}`);
      console.log(`Recuperável: ${result.error.recoverable}\n`);

      // Tratamento baseado em tipo de erro
      switch (result.error.code) {
        case "REQUIREMENTS_NOT_MET":
          console.log("Ação sugerida: Verificar requisitos com checkRequirements()");
          break;

        case "MERGE_CONFLICTS":
          console.log("Ação sugerida: Revisar conflitos com getConflicts()");
          break;

        case "MERGE_FAILED":
          if (result.error.recoverable) {
            console.log("Ação sugerida: Tentar novamente após alguns segundos");
          } else {
            console.log("Ação sugerida: Investigar erro com suporte");
          }
          break;
      }
    }

    // Análise do que bloqueou
    console.log("\n=== ANÁLISE DO BLOQUEIO ===\n");

    const requirements = await autoMerge.checkRequirements({ number: prNumber });
    const unmet = requirements.filter((r) => !r.met);

    if (unmet.length > 0) {
      console.log(`${unmet.length} requisito(s) não atendido(s):`);
      unmet.forEach((req) => {
        console.log(`  - ${req.type}`);
      });
    }

    const conflicts = await autoMerge.getConflicts({ number: prNumber });

    if (conflicts.length > 0) {
      console.log(`${conflicts.length} conflito(s) detectado(s):`);
      conflicts.forEach((c) => {
        console.log(`  - ${c.file} (${c.severity})`);
      });
    }
  } else {
    console.log("✓ Merge realizado com sucesso!");
  }
}

// ============================================================================
// EXEMPLO 9: Monitoramento e Relatório
// ============================================================================

export async function example9_monitoring() {
  console.log("\n=== EXEMPLO 9: Monitoramento e Relatório ===\n");

  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "anthropics",
    repo: "claude-code",
  });

  // Simular múltiplas operações
  console.log("Coletando dados de monitoramento...\n");

  for (let i = 0; i < 5; i++) {
    await autoMerge.canMerge({ number: 400 + i });
    await autoMerge.checkRequirements({ number: 400 + i });
  }

  // Gerar relatório
  console.log("=== RELATÓRIO DE MONITORAMENTO ===\n");

  const metrics = autoMerge.getMetrics();
  const auditLog = autoMerge.getAuditLog();
  const scheduled = autoMerge.getScheduledMerges();

  console.log("RESUMO EXECUTIVO:");
  console.log(`  Período: Últimas 24 horas`);
  console.log(`  Operações totais: ${auditLog.length}`);
  console.log(`  Merges realizados: ${metrics.totalMerges}`);
  console.log(`  Taxa de sucesso: ${metrics.successRate.toFixed(2)}%`);
  console.log(`  Agendamentos pendentes: ${scheduled.length}\n`);

  console.log("PERFORMANCE:");
  console.log(`  Tempo médio de merge: ${metrics.averageDuration.toFixed(0)}ms`);
  console.log(`  Tempo de lock (médio): ${metrics.lockWaitTime.average.toFixed(0)}ms`);
  console.log(`  Taxa de conflito: ${metrics.conflictRate.toFixed(2)}%\n`);

  console.log("ATIVIDADES RECENTES:");
  const recent = auditLog.slice(-10);

  recent.forEach((entry) => {
    const timestamp = entry.timestamp.toISOString().split("T")[1];
    const status = entry.status === "success" ? "✓" : "✗";
    console.log(`  ${timestamp} ${status} ${entry.action} (PR #${entry.prNumber})`);
  });
}

// ============================================================================
// MAIN - Executar exemplos
// ============================================================================

export async function runAllExamples() {
  console.log("\n╔════════════════════════════════════════════════════════════╗");
  console.log("║         AutoMerge Service - Exemplos Práticos             ║");
  console.log("╚════════════════════════════════════════════════════════════╝");

  try {
    await example1_basicMerge();
    await example2_requirementsAnalysis();
    await example3_conflictDetection();
    await example4_mergeStrategies();
    await example5_scheduleMerge();
    await example6_metrics();
    await example7_auditTrail();
    await example8_errorHandling();
    await example9_monitoring();

    console.log("\n╔════════════════════════════════════════════════════════════╗");
    console.log("║              Exemplos Completados com Sucesso!             ║");
    console.log("╚════════════════════════════════════════════════════════════╝\n");
  } catch (error) {
    console.error("\n✗ Erro ao executar exemplos:");
    console.error(error);
  }
}

// Executar se arquivo for rodado diretamente
if (require.main === module) {
  runAllExamples().catch(console.error);
}
