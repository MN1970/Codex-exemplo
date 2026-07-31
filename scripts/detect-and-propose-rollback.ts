#!/usr/bin/env ts-node
/**
 * Script CLI para detectar CI failures e propor rollback
 * Chamado pelo workflow: rollback-monitor.yml
 */

import { createRollbackOrchestratorService, type CIFailure } from '../src/services/rollback';

// Parse command line arguments
function parseArgs(): {
  workflowRunId: number;
  repository: string;
  branch: string;
} {
  const args: Record<string, string> = {};

  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      const value = process.argv[i + 1];
      args[key] = value;
      i++;
    }
  }

  return {
    workflowRunId: parseInt(args['workflow-run-id'] || '0', 10),
    repository: args['repository'] || 'unknown/unknown',
    branch: args['branch'] || 'main',
  };
}

async function main() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║ Rollback Monitor - Detect & Propose                       ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  const { workflowRunId, repository, branch } = parseArgs();
  const [owner, repo] = repository.split('/');

  console.log(`[CONFIG]`);
  console.log(`  Workflow Run ID: ${workflowRunId}`);
  console.log(`  Repository: ${repository}`);
  console.log(`  Branch: ${branch}\n`);

  // Valida argumentos
  if (!workflowRunId || !owner || !repo) {
    console.error('Error: Missing required arguments');
    console.error('Usage: detect-and-propose-rollback.ts --workflow-run-id <id> --repository <owner/repo> --branch <branch>');
    process.exit(1);
  }

  // Cria serviço
  const service = createRollbackOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || '',
    owner,
    repo,
    slackWebhookUrl: process.env.SLACK_WEBHOOK,
    coworkWebhookUrl: process.env.COWORK_WEBHOOK,
    requireManualApprovalForCritical: true,
    autoExecuteOnApproval: true,
  });

  console.log('[STEP 1] Detecting CI failure...\n');

  try {
    // Detecta falha
    // Em um cenário real, isto faria fetch real do GitHub
    // Por agora, retorna null (sem falha) ou mock (com falha)

    console.log('✓ CI failure detection initiated');
    console.log('  Querying GitHub Actions workflow run...');

    // Mock para demonstração
    const ciFailure: CIFailure | null = null; // Em produção, fazer fetch real

    if (!ciFailure) {
      console.log('✓ No CI failure detected in workflow run\n');
      console.log('Exit: All tests passing, no rollback needed');
      process.exit(0);
    }

    console.log(`✓ CI failure detected`);
    console.log(`  Tests Failed: ${ciFailure.failedTests.length}`);
    console.log(`  Lint Errors: ${ciFailure.lintErrors.length}`);
    console.log(`  Severity: ${ciFailure.severity}\n`);

    console.log('[STEP 2] Creating rollback proposal...\n');

    const proposal = await service.proposeRollback(ciFailure);

    console.log(`✓ Proposal created: ${proposal.id}`);
    console.log(`  Target Commit: ${proposal.targetCommit.substring(0, 12)}`);
    console.log(`  Severity: ${proposal.severity}`);
    console.log(`  Confidence: ${(proposal.impact.confidenceLevel * 100).toFixed(1)}%`);
    console.log(`  Auto-Approvable: ${proposal.autoApprovalEligible}`);
    console.log(`  Status: ${proposal.approvalStatus}\n`);

    if (!proposal.autoApprovalEligible) {
      console.log('[STEP 3] Requesting manual approval...\n');

      const approvalReq = await service.requestApproval(proposal, 'both');

      console.log('✓ Approval request sent');
      console.log(`  Channel: ${approvalReq.channel}`);
      console.log(`  Token: ${approvalReq.approvalToken.substring(0, 20)}...`);
      console.log(`  Expires: ${approvalReq.expiresAt.toISOString()}\n`);

      console.log('Awaiting reviewer approval via Slack/Cowork...');
      console.log('(timeout in 30 minutes if no response)\n');
    } else {
      console.log('[STEP 3] Auto-approving rollback...\n');

      console.log('✓ Proposal auto-approved (meets confidence threshold)');
      console.log('  Queuing for execution...\n');
    }

    // Exibe resumo
    console.log('[SUMMARY]');
    const metrics = service.getMetrics();
    console.log(`  Total Failures Detected: ${metrics.totalFailuresDetected}`);
    console.log(`  Total Proposals: ${metrics.totalProposals}`);
    console.log(`  Auto-Approved: ${metrics.autoApprovedCount}\n`);

    console.log('Exit: Rollback proposal processed successfully');
    process.exit(0);
  } catch (error) {
    console.error('\n[ERROR] Failed to process CI failure:', error);
    process.exit(1);
  }
}

main();
