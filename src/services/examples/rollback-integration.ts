/**
 * Integração do Rollback Orchestrator com GitHub Actions e Slack
 * Demonstra uso em environment real: webhooks, aprovação, execução
 */

import { createRollbackOrchestratorService, type CIFailure } from '../rollback';

/**
 * Express middleware para processar webhook de CI failure do GitHub
 */
export function createCIFailureWebhookHandler(service: ReturnType<typeof createRollbackOrchestratorService>) {
  return async (req: any, res: any) => {
    const { action, workflow_run, repository } = req.body;

    console.log(
      `[WEBHOOK] CI failure detected: ${repository.full_name}#${workflow_run.id}`
    );

    try {
      // 1. Detecta falha
      const ciFailure = await service.detectCIFailure(workflow_run.id);

      if (!ciFailure) {
        return res.json({ message: 'No CI failure detected' });
      }

      // 2. Propõe rollback
      const proposal = await service.proposeRollback(ciFailure);

      console.log(`[PROPOSAL] Created: ${proposal.id} (auto-approvable: ${proposal.autoApprovalEligible})`);

      // 3. Se não for auto-approvable, requer aprovação
      if (!proposal.autoApprovalEligible) {
        await service.requestApproval(proposal, 'both');
        console.log(`[APPROVAL] Requested for proposal ${proposal.id}`);

        return res.json({
          proposalId: proposal.id,
          requiresApproval: true,
          message: 'Rollback proposal created and sent for approval',
        });
      }

      // 4. Se for auto-approvable, executa imediatamente
      console.log(
        `[AUTO-APPROVE] Automatically approving proposal ${proposal.id}`
      );

      return res.json({
        proposalId: proposal.id,
        requiresApproval: false,
        message: 'Rollback proposal auto-approved and queued for execution',
      });
    } catch (error) {
      console.error('[ERROR]', error);
      return res.status(500).json({ error: String(error) });
    }
  };
}

/**
 * Slack action handler para botões de aprovação/rejeição
 */
export function createSlackActionHandler(service: ReturnType<typeof createRollbackOrchestratorService>) {
  return async (req: any, res: any) => {
    const payload = JSON.parse(req.body.payload);
    const { action_id, value, user } = payload;

    console.log(`[SLACK] ${user.username} clicked ${action_id}`);

    try {
      if (action_id.startsWith('approve_rollback_')) {
        const proposalId = value;
        const proposal = service.getProposal(proposalId);

        if (!proposal) {
          return res.status(404).json({ error: 'Proposal not found' });
        }

        // Aprova com token fake (em produção, validar token)
        const approvalRequest = (service as any).approvalRequests?.get(proposalId);
        if (!approvalRequest) {
          return res.status(400).json({ error: 'Approval request not found' });
        }

        const approved = await service.approveRollback(
          proposalId,
          approvalRequest.approvalToken,
          user.username
        );

        console.log(
          `[APPROVED] ${user.username} approved rollback ${proposalId}`
        );

        return res.json({
          text: `Rollback approved by ${user.username}. Executing revert...`,
        });
      } else if (action_id.startsWith('reject_rollback_')) {
        const proposalId = value;

        const rejected = await service.rejectRollback(
          proposalId,
          'Rejected via Slack',
          user.username
        );

        console.log(
          `[REJECTED] ${user.username} rejected rollback ${proposalId}`
        );

        return res.json({
          text: `Rollback rejected by ${user.username}.`,
        });
      }

      return res.status(400).json({ error: 'Unknown action' });
    } catch (error) {
      console.error('[SLACK_ERROR]', error);
      return res.status(500).json({ error: String(error) });
    }
  };
}

/**
 * GET endpoint para status e métricas
 */
export function createMetricsEndpoint(service: ReturnType<typeof createRollbackOrchestratorService>) {
  return async (req: any, res: any) => {
    const metrics = service.getMetrics();
    const proposals = service.getActiveProposals();
    const auditTrail = service.getAuditTrail().slice(-20); // últimas 20 ações

    return res.json({
      metrics: {
        totalFailuresDetected: metrics.totalFailuresDetected,
        totalProposals: metrics.totalProposals,
        totalApproved: metrics.totalApproved,
        totalRejected: metrics.totalRejected,
        totalExecuted: metrics.totalExecuted,
        successfulRollbacks: metrics.successfulRollbacks,
        failedRollbacks: metrics.failedRollbacks,
        autoApprovedCount: metrics.autoApprovedCount,
        averageTimeToApproveMinutes: metrics.averageTimeToApproveMinutes,
      },
      activeProposals: proposals.map((p) => ({
        id: p.id,
        targetCommit: p.targetCommit.substring(0, 12),
        severity: p.severity,
        status: p.approvalStatus,
        proposedAt: p.proposedAt,
      })),
      recentActivity: auditTrail.map((entry) => ({
        timestamp: entry.timestamp,
        action: entry.action,
        status: entry.status,
      })),
    });
  };
}

/**
 * Health check endpoint
 */
export function createHealthCheckEndpoint(service: ReturnType<typeof createRollbackOrchestratorService>) {
  return async (req: any, res: any) => {
    const metrics = service.getMetrics();
    const failureRate =
      metrics.totalExecuted > 0
        ? (metrics.failedRollbacks / metrics.totalExecuted) * 100
        : 0;

    const health = {
      status: failureRate < 10 ? 'healthy' : 'degraded',
      failureRate: failureRate.toFixed(1),
      metrics,
      timestamp: new Date(),
    };

    return res.json(health);
  };
}

/**
 * Exemplo: Setup de Express server com Rollback Orchestrator
 */
export async function setupRollbackOrchestrationServer() {
  // Simula Express (em produção, usar Express real)
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║ Rollback Orchestrator Integration Server                  ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || 'test-token',
    owner: 'manta-associados',
    repo: 'codex-hub',
    slackWebhookUrl: process.env.SLACK_WEBHOOK,
    coworkWebhookUrl: process.env.COWORK_WEBHOOK,
    autoExecuteOnApproval: true,
    requireManualApprovalForCritical: true,
  });

  console.log('[SERVER] Rollback Orchestrator initialized\n');

  // Endpoints
  console.log('[ENDPOINTS]');
  console.log('  POST   /webhooks/ci-failure    ← GitHub Actions CI failure');
  console.log('  POST   /webhooks/slack/action  ← Slack button clicks');
  console.log('  GET    /metrics                ← Dashboard metrics');
  console.log('  GET    /health                 ← Health check\n');

  // Simula webhook: CI failure detected
  console.log('[SIMULATION 1] GitHub Actions detects CI failure');
  console.log('─────────────────────────────────────────────────────────\n');

  const mockWebhookPayload = {
    action: 'completed',
    workflow_run: {
      id: 987654321,
      status: 'completed',
      conclusion: 'failure',
      head_sha: 'f3a4c2b8d9e1f6a0b2c3d4e5f6a7b8c9',
    },
    repository: {
      full_name: 'manta-associados/codex-hub',
    },
  };

  // Simula detecção (em produção seria via fetch real)
  console.log('Processing webhook payload...');
  console.log(`  Workflow Run ID: ${mockWebhookPayload.workflow_run.id}`);
  console.log(`  Conclusion: ${mockWebhookPayload.workflow_run.conclusion}`);
  console.log(`  Commit SHA: ${mockWebhookPayload.workflow_run.head_sha.substring(0, 12)}\n`);

  // Cria failure simulada
  const mockFailure: CIFailure = {
    commitSha: mockWebhookPayload.workflow_run.head_sha,
    commitMessage: 'Add async operation handler',
    author: 'dev.silva@manta.com',
    committedAt: new Date(Date.now() - 10 * 60000),
    workflowRunId: mockWebhookPayload.workflow_run.id,
    failedTests: [
      {
        name: 'should handle timeout',
        suite: 'async.test.ts',
        message: 'Expected timeout after 5000ms',
        duration: 5100,
      },
      {
        name: 'should retry on error',
        suite: 'async.test.ts',
        message: 'Retry policy not applied',
        duration: 2500,
      },
      {
        name: 'integration: e2e operation',
        suite: 'integration.test.ts',
        message: 'Operation timed out',
        duration: 10200,
      },
      {
        name: 'should validate input',
        suite: 'async.test.ts',
        message: 'Validation missing',
        duration: 1800,
      },
      {
        name: 'should cleanup resources',
        suite: 'async.test.ts',
        message: 'Resource leak detected',
        duration: 3200,
      },
    ],
    lintErrors: [
      {
        file: 'src/async-handler.ts',
        line: 42,
        column: 12,
        rule: 'no-async-without-await',
        message: 'Async function without proper await',
        severity: 'error',
      },
    ],
    severity: 'HIGH' as const,
    affectedFiles: ['src/async-handler.ts', 'src/retry-policy.ts'],
    buildDuration: 125000,
  };

  console.log('[DETECT] Creating rollback proposal...\n');

  const proposal = await service.proposeRollback(mockFailure);

  console.log(`✓ Proposal created: ${proposal.id}`);
  console.log(`  Severity: ${proposal.severity}`);
  console.log(`  Tests failed: ${proposal.ciFailure.failedTests.length}`);
  console.log(`  Confidence: ${(proposal.impact.confidenceLevel * 100).toFixed(1)}%`);
  console.log(`  Auto-approvable: ${proposal.autoApprovalEligible}`);
  console.log(`  Status: ${proposal.approvalStatus}\n`);

  // Simula approval request
  if (!proposal.autoApprovalEligible) {
    console.log('[REQUEST] Sending approval request to Slack...\n');

    const approvalReq = await service.requestApproval(proposal, 'slack');

    console.log(`✓ Approval request sent`);
    console.log(`  Token: ${approvalReq.approvalToken.substring(0, 30)}...`);
    console.log(`  Expires: ${approvalReq.expiresAt.toISOString()}\n`);

    // Simula Slack action: approve
    console.log('[SIMULATION 2] Reviewer clicks "Approve" button in Slack');
    console.log('─────────────────────────────────────────────────────────\n');

    const mockSlackPayload = {
      action_id: `approve_rollback_${proposal.id}`,
      value: proposal.id,
      user: {
        username: 'reviewer.costa',
      },
    };

    console.log(`Processing Slack action: ${mockSlackPayload.action_id}`);
    console.log(`  User: ${mockSlackPayload.user.username}`);
    console.log(`  Proposal: ${mockSlackPayload.value}\n`);

    try {
      const approved = await service.approveRollback(
        proposal.id,
        approvalReq.approvalToken,
        mockSlackPayload.user.username
      );

      console.log('✓ Rollback approved');
      console.log(`  Approved by: ${approved.approvedBy}`);
      console.log(`  Approved at: ${approved.approvedAt}\n`);
    } catch (error) {
      console.error(`✗ Approval failed: ${error}`);
    }
  } else {
    console.log('[AUTO-APPROVE] Proposal is auto-approvable, skipping manual approval\n');
  }

  // Exibe métricas
  console.log('[SIMULATION 3] Dashboard Metrics');
  console.log('─────────────────────────────────────────────────────────\n');

  const metrics = service.getMetrics();

  console.log('Rollback Statistics:');
  console.log(`  Total Failures Detected: ${metrics.totalFailuresDetected}`);
  console.log(`  Total Proposals: ${metrics.totalProposals}`);
  console.log(`  Approved: ${metrics.totalApproved}`);
  console.log(`  Rejected: ${metrics.totalRejected}`);
  console.log(`  Auto-Approved: ${metrics.autoApprovedCount}`);
  console.log(`  Successful Rollbacks: ${metrics.successfulRollbacks}`);
  console.log(`  Failed Rollbacks: ${metrics.failedRollbacks}\n`);

  // Audit trail
  console.log('[SIMULATION 4] Audit Trail');
  console.log('─────────────────────────────────────────────────────────\n');

  const auditTrail = service.getAuditTrail();

  console.log('Recent Actions:');
  auditTrail
    .slice(-5)
    .forEach((entry) => {
      console.log(
        `  [${entry.timestamp.toISOString()}] ${entry.action} (${entry.status})`
      );
    });

  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║ Integration demo completed successfully!                 ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');
}

// Executa se for chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
  setupRollbackOrchestrationServer().catch(console.error);
}

export { setupRollbackOrchestrationServer };
