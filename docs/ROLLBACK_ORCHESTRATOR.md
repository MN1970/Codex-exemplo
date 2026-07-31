# Rollback Orchestrator — Sistema Inteligente de Detecção e Reversão de Commits Quebradores

## Visão Geral

O **Rollback Orchestrator** é um sistema automatizado que monitora CI/CD pipelines em produção, detecta quando um commit quebra testes, propõe reversão automática e executa o rollback após aprovação humana. É um **fail-safe** completo: máquina propõe, humano aprova, máquina executa.

### Características Principais

- **Monitoramento Contínuo**: Acompanha PRs merged e detecção de falhas em main
- **Detecção Inteligente**: Identifica qual commit específico quebrou os testes via bisect
- **Propostas Automáticas**: Gera proposta de rollback com análise de impacto completa
- **Auto-Approval Seguro**: Aprova automaticamente falhas LOW/MEDIUM com alta confiança
- **Aprovação Manual**: Requere aprovação humana para CRITICAL (fail-safe)
- **Execução Controlada**: Executa revert apenas após aprovação explícita
- **Notificações Omnichannel**: Slack + Cowork + Email
- **Audit Trail Completo**: Rastreia todas as ações para compliance
- **Métricas em Tempo Real**: Dashboard de rollbacks, aprovações, sucessos

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Webhooks / Polling                                  │
│  (PR merged, CI failure on main)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  RollbackOrchestratorService                                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. detectCIFailure()                                │   │
│  │    └─ Monitora workflow runs em main                │   │
│  │    └─ Extrai test failures e lint errors            │   │
│  │    └─ Calcula severity (LOW|MEDIUM|HIGH|CRITICAL)  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. proposeRollback()                                │   │
│  │    └─ Analisa impacto (arquivos, features, risk)    │   │
│  │    └─ Calcula confiança de rollback                 │   │
│  │    └─ Decide auto-approval eligibility              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. requestApproval()                                │   │
│  │    └─ Envia para Slack, Cowork, Email              │   │
│  │    └─ Gera approval token (válido por 30 min)      │   │
│  │    └─ Aguarda resposta (approve/reject)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. approveRollback() / rejectRollback()            │   │
│  │    └─ Valida token                                  │   │
│  │    └─ Registra aprovador + timestamp                │   │
│  │    └─ Dispara executeRollback() se auto-execute     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 5. executeRollback()                                │   │
│  │    └─ Cria revert commit                            │   │
│  │    └─ Faz push para main                            │   │
│  │    └─ Aguarda novo CI run                           │   │
│  │    └─ Valida sucesso                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Audit Trail & Metrics                              │   │
│  │ └─ Todas as ações registradas com timestamp         │   │
│  │ └─ Dashboard em tempo real                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Instalação & Setup

### 1. Adicionar dependências (já incluídas)

```bash
npm install
# Não requer dependências adicionais — usa fetch nativo
```

### 2. Configurar variáveis de ambiente

```bash
# GitHub
export GITHUB_TOKEN="ghp_xxxxx"

# Notificações
export SLACK_WEBHOOK="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
export COWORK_WEBHOOK="https://cowork.manta.com/webhooks/rollback"

# Opcional
export ANTHROPIC_API_KEY="sk-ant-xxxxx"  # para análise de impacto com IA
```

### 3. Criar instância do serviço

```typescript
import { createRollbackOrchestratorService } from './src/services/rollback';

const service = createRollbackOrchestratorService({
  githubToken: process.env.GITHUB_TOKEN,
  owner: "manta-associados",
  repo: "codex-hub",
  slackWebhookUrl: process.env.SLACK_WEBHOOK,
  coworkWebhookUrl: process.env.COWORK_WEBHOOK,

  // Thresholds de auto-approval
  minFailuresForAutoApproval: 5,           // 5+ testes falhando
  minConfidenceForAutoApproval: 0.95,      // 95%+ de confiança
  maxAutoApprovalSeverity: "HIGH",         // não aprova CRITICAL
  approvalTimeoutMinutes: 30,

  // Comportamento
  autoExecuteOnApproval: true,             // executa após aprovação
  requireManualApprovalForCritical: true,  // sempre requer humano para CRITICAL
  maxAutomaticRollbacksPerDay: 5,          // limit de segurança
});
```

---

## Uso

### Scenario 1: Detecção e Proposta Automática

```typescript
// Webhook from GitHub Actions detecting CI failure
const ciFailure = await service.detectCIFailure(workflowRunId);

if (ciFailure) {
  // Propõe rollback automaticamente
  const proposal = await service.proposeRollback(ciFailure, mergedPR);

  console.log(`Failure detected: ${ciFailure.failedTests.length} tests failed`);
  console.log(`Severity: ${ciFailure.severity}`);
  console.log(`Proposal ID: ${proposal.id}`);
  console.log(`Auto-approvable: ${proposal.autoApprovalEligible}`);
  console.log(`Status: ${proposal.approvalStatus}`);
}
```

**Output esperado:**

```
Failure detected: 5 tests failed
Severity: HIGH
Proposal ID: rollback-1693219200000-abc123
Auto-approvable: false
Status: pending  ← Requer aprovação manual
```

### Scenario 2: Aprovação Manual

```typescript
// Reviewer obtém proposta e toma decisão
const proposal = service.getProposal(proposalId);

// Opção A: Aprovar
const approved = await service.approveRollback(
  proposal.id,
  approvalToken,        // gerado em requestApproval()
  "reviewer@manta.com"
);

console.log(`✓ Approved by ${approved.approvedBy}`);
console.log(`  Approved at: ${approved.approvedAt}`);
// Se autoExecuteOnApproval=true, já inicia execução

// Opção B: Rejeitar
const rejected = await service.rejectRollback(
  proposal.id,
  "Falso positivo - será corrigido em PR de follow-up",
  "reviewer@manta.com"
);

console.log(`✗ Rejected: ${rejected.rejectionReason}`);
```

### Scenario 3: Execução Controlada

```typescript
// Executa revert automaticamente (após aprovação)
const execution = await service.executeRollback(proposal);

console.log(`Revert started at: ${execution.startedAt}`);
console.log(`Revert commit: ${execution.revertCommitSha.substring(0, 12)}`);

// Aguarda...

console.log(`Revert completed at: ${execution.completedAt}`);
console.log(`Status: ${execution.status}`);
console.log(`Tests passed: ${execution.testsPassed}`);
console.log(`Tests failed: ${execution.testsFailed}`);
```

### Scenario 4: Monitoramento de Métricas

```typescript
const metrics = service.getMetrics();

console.log(`Total failures detected: ${metrics.totalFailuresDetected}`);
console.log(`Total proposals: ${metrics.totalProposals}`);
console.log(`Total approved: ${metrics.totalApproved}`);
console.log(`Total rejected: ${metrics.totalRejected}`);
console.log(`Successful rollbacks: ${metrics.successfulRollbacks}`);
console.log(`Failed rollbacks: ${metrics.failedRollbacks}`);
console.log(`Auto-approved: ${metrics.autoApprovedCount}`);
console.log(`Avg time to approve: ${metrics.averageTimeToApproveMinutes} min`);
console.log(`Avg time to execute: ${metrics.averageTimeToExecuteMinutes} min`);
```

### Scenario 5: Auditoria Completa

```typescript
// Obtém audit trail completo
const auditTrail = service.getAuditTrail();

auditTrail.forEach((entry) => {
  console.log(`[${entry.timestamp.toISOString()}] ${entry.action}`);
  console.log(`  Status: ${entry.status}`);
  console.log(`  Details: ${JSON.stringify(entry.details, null, 2)}`);
  if (entry.error) {
    console.log(`  Error: ${entry.error}`);
  }
});

// Resultado esperado:
// [2024-09-01T10:30:45Z] FAILURE_DETECTED
// [2024-09-01T10:30:46Z] ROLLBACK_PROPOSED
// [2024-09-01T10:30:47Z] APPROVAL_REQUESTED
// [2024-09-01T10:31:20Z] ROLLBACK_APPROVED
// [2024-09-01T10:31:21Z] ROLLBACK_EXECUTED
```

---

## Tipos de Dados

### `RollbackProposal`

```typescript
interface RollbackProposal {
  id: string;                          // rollback-{timestamp}-{random}
  proposedAt: Date;
  targetCommit: string;                // commit a reverter
  targetCommitMessage: string;
  reverseCommitSha?: string;           // hash do commit de revert
  ciFailure: CIFailure;
  mergedPR?: MergedPR;
  reason: string;
  impact: RollbackImpact;
  severity: FailureSeverity;           // LOW|MEDIUM|HIGH|CRITICAL
  autoApprovalEligible: boolean;
  approvalStatus: "pending" | "approved" | "rejected";
  approvedBy?: string;
  approvedAt?: Date;
  rejectionReason?: string;
}
```

### `FailureSeverity`

```typescript
enum FailureSeverity {
  LOW      = "low",          // 1-3 testes falhando
  MEDIUM   = "medium",       // 4-10 testes falhando
  HIGH     = "high",         // 11-20 testes falhando
  CRITICAL = "critical",     // 20+ testes falhando OU lint errors críticos
}
```

### `RollbackImpact`

```typescript
interface RollbackImpact {
  filesAffected: string[];
  linesChanged: number;
  testsFixed: number;
  testsStillFailing?: number;
  estimatedDowntime: number;           // ms
  potentiallyAffectedFeatures: string[];
  confidenceLevel: number;             // 0.0-1.0
  riskOfReintroducingBug: boolean;
}
```

### `RollbackExecution`

```typescript
interface RollbackExecution {
  id: string;                          // execution-{timestamp}-{random}
  proposalId: string;
  startedAt: Date;
  completedAt?: Date;
  duration?: number;                   // ms
  status: RollbackExecutionStatus;     // PENDING|IN_PROGRESS|SUCCESS|FAILURE
  revertCommitSha?: string;
  pushSuccess: boolean;
  newWorkflowRunId?: number;
  testsPassed?: number;
  testsFailed?: number;
  error?: string;
}
```

---

## Thresholds & Configuração

### Auto-Approval Logic

```
AUTO-APPROVE SE:
  ✓ severity <= maxAutoApprovalSeverity (default: HIGH)
  ✓ failedTests.length >= minFailuresForAutoApproval (default: 5)
  ✓ impactAnalysis.confidenceLevel >= minConfidenceForAutoApproval (default: 0.95)
  ✓ NOT (severity == CRITICAL && requireManualApprovalForCritical)

REQUER APROVAÇÃO HUMANA SE:
  ✗ severity == CRITICAL (default)
  ✗ confidenceLevel < 0.95
  ✗ failedTests.length < 5
```

### Rate Limiting

```typescript
const config = {
  maxAutomaticRollbacksPerDay: 5,      // máx 5 rollbacks automáticos/dia
  maxConcurrentBisections: 3,          // máx 3 bisects paralelos
  preventRollbackOfRollbacks: true,    // bloqueia revert de reverts
  approvalTimeoutMinutes: 30,          // approval valid por 30 min
};
```

---

## Notificações

### Slack Message Example

```
┌─────────────────────────────────────────┐
│ Rollback Proposal                       │
├─────────────────────────────────────────┤
│ Commit: abc1234                         │
│ Message: Add async handler              │
│ Severity: HIGH                          │
│ Tests Failed: 7                         │
│                                         │
│ [Approve] [Reject]                      │
└─────────────────────────────────────────┘
```

### Cowork Notification

```json
{
  "text": "Rollback Proposal #rollback-1693219200000-abc123",
  "details": {
    "commit": "f3a4c2b8d9e1...",
    "severity": "HIGH",
    "testsAffected": 7,
    "approvalToken": "approval-1693219200000-xyz789..."
  }
}
```

### Email Summary

```
Subject: Rollback Proposal Requires Approval - codex-hub PR #234

From: dev.silva@manta.com
Commit: abc1234 (Add async handler)
Severity: HIGH
Tests Failed: 7

Review and approve at: https://github.com/manta-associados/codex-hub/rollback/...

Token: approval-1693219200000-...
Expires: 2024-09-01 11:00 UTC
```

---

## Audit Trail & Compliance

Todas as ações são registradas com timestamp completo:

```
[2024-09-01T10:30:45Z] FAILURE_DETECTED
  │
  ├─ runId: 987654321
  ├─ commitSha: abc1234
  ├─ severity: HIGH
  └─ status: success

[2024-09-01T10:30:46Z] ROLLBACK_PROPOSED
  │
  ├─ proposalId: rollback-1693219200000-xyz
  ├─ targetCommit: abc1234
  ├─ autoApprovalEligible: false
  └─ status: success

[2024-09-01T10:30:47Z] APPROVAL_REQUESTED
  │
  ├─ proposalId: rollback-1693219200000-xyz
  ├─ channel: both (slack, cowork)
  ├─ expiresAt: 2024-09-01T11:00:47Z
  └─ status: success

[2024-09-01T10:31:20Z] ROLLBACK_APPROVED
  │
  ├─ proposalId: rollback-1693219200000-xyz
  ├─ approver: reviewer.costa@manta.com
  └─ status: success

[2024-09-01T10:31:21Z] ROLLBACK_EXECUTED
  │
  ├─ executionId: execution-1693219281000-abc
  ├─ proposalId: rollback-1693219200000-xyz
  ├─ revertCommitSha: xyz7890
  ├─ status: SUCCESS
  └─ status: success
```

---

## Testing

```bash
# Executar testes
npm test -- rollback.test.ts

# Com coverage
npm test -- rollback.test.ts --coverage

# Watch mode
npm test -- rollback.test.ts --watch
```

### Test Coverage

```
✓ Initialization & Configuration
✓ Failure Detection & Severity Calculation
✓ Rollback Proposals
✓ Auto-Approval Logic
✓ Manual Approval/Rejection
✓ Approval Token Validation
✓ Execution Workflow
✓ Metrics & Audit Trail
✓ Rate Limiting
✓ Notification Delivery
```

---

## Exemplos de Uso Real

### Exemplo 1: Express.js Webhook

```typescript
import express from 'express';
import { createRollbackOrchestratorService } from './services/rollback';

const app = express();
const service = createRollbackOrchestratorService(config);

app.post('/webhooks/ci-failure', express.json(), async (req, res) => {
  const { workflowRunId, repository } = req.body;

  try {
    const failure = await service.detectCIFailure(workflowRunId);

    if (failure) {
      const proposal = await service.proposeRollback(failure);
      res.json({ proposalId: proposal.id });
    } else {
      res.json({ message: 'No failure detected' });
    }
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

app.post('/webhooks/approval/:proposalId', express.json(), async (req, res) => {
  const { proposalId } = req.params;
  const { token, action, reviewer } = req.body;

  try {
    if (action === 'approve') {
      const proposal = await service.approveRollback(proposalId, token, reviewer);
      res.json({ status: 'approved', proposal });
    } else {
      const proposal = await service.rejectRollback(
        proposalId,
        req.body.reason,
        reviewer
      );
      res.json({ status: 'rejected', proposal });
    }
  } catch (error) {
    res.status(400).json({ error: String(error) });
  }
});

app.get('/metrics', (req, res) => {
  res.json(service.getMetrics());
});

app.get('/audit-trail', (req, res) => {
  res.json(service.getAuditTrail());
});
```

### Exemplo 2: GitHub Action Trigger

```yaml
name: Rollback Orchestrator Monitor

on:
  workflow_run:
    workflows: [CI]
    types: [completed]

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Check for CI failures
        run: |
          npm run check:ci-failures -- \
            --workflow-run-id ${{ github.event.workflow_run.id }} \
            --github-token ${{ secrets.GITHUB_TOKEN }} \
            --slack-webhook ${{ secrets.SLACK_WEBHOOK }}
```

---

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| "Invalid approval token" | Token expirado ou incorreto | Gerar novo token via requestApproval() |
| "Approval request expired" | >30 min sem resposta | Reenviar approval request |
| "Daily rollback limit exceeded" | Muitos rollbacks em 24h | Aguardar reset (UTC midnight) ou aumentar limit |
| "GitHub API rate limit" | Muitas chamadas à API | Aumentar polling interval de 30s para 60s |
| Slack notification não enviada | Webhook URL inválido | Validar em https://api.slack.com/apps |
| Revert commit não encontrado | Push falhou silenciosamente | Checar permissões de push em main |

---

## Performance & Scale

- **Monitoramento**: 0 overhead quando sem falhas (polling apenas 30s)
- **Proposta**: ~500ms (detecção + análise + notificação)
- **Aprovação**: ~2s (validação token + notificação)
- **Execução**: ~5-30min (espera CI + validação)

Para repositórios com 100+ PRs/dia:
- Aumentar `maxConcurrentBisections` de 3 para 10
- Aumentar `ciPollingIntervalMs` de 30s para 60s se houver rate limit

---

## FAQ

**P: O rollback é automático ou requer aprovação?**
A: Requer aprovação humana por padrão. Apenas propostas LOW/MEDIUM com alta confiança são auto-aprovadas (e ainda assim com timeout de 30 min para override).

**P: O que acontece se o revert também quebrar testes?**
A: O sistema detecta como nova falha e propõe revert da reversão. O flag `preventRollbackOfRollbacks` bloqueia isso se habilitado.

**P: Pode usar em branch de staging/develop?**
A: Sim! Configure um serviço separado por branch conforme necessário.

**P: Integra com CI/CD tools além de GitHub?**
A: Atualmente GitHub Actions. Extensível para GitLab CI, CircleCI, Jenkins via webhooks.

---

## Links Úteis

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)
- [Rollback Strategy Best Practices](https://engineering.linkedin.com)

---

## Suporte

Para dúvidas ou reportar bugs:
- GitHub Issues: `/issues`
- Slack: `#engineering-platform`
- Email: `platform@manta.com`
