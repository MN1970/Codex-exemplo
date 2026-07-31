# Auto-Merge Controller — Automação inteligente de merge de PRs

Versão: **1.0.0**

## Visão Geral

O `AutoMergeController` automatiza o processo de merge de pull requests, verificando pré-requisitos essenciais antes de fazer o merge:

- ✅ **CI passed** — Verifica se o pipeline de CI/CD passou
- ✅ **Approvals** — Valida número de approvals necessários
- ✅ **Conflicts** — Detecta e bloqueia em caso de conflitos de merge
- ✅ **Status checks** — Verifica checks obrigatórios do branch protection
- ✅ **Draft prevention** — Impede merge de PRs em modo draft
- ✅ **Branch cleanup** — Deleta feature branch após merge bem-sucedido

## Features

### Verificação de Pré-requisitos

```typescript
const controller = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  requireCIPassed: true,
  requiredApprovals: 2,
});

const result = await controller.mergePR(42);
```

### Audit Trail Completo

Todos os eventos são registrados em um audit trail que pode ser persistido em Supabase:

```typescript
const controller = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  auditTableUrl: "https://xxx.supabase.co/rest/v1/audit_log",
  auditApiKey: "sbp_xxx",
});

const result = await controller.mergePR(42);
console.log(result.auditEvents);
// [
//   { action: "AUTO_MERGE_STARTED", ... },
//   { action: "PREREQUISITES_CHECK_PASSED", ... },
//   { action: "MERGE_COMPLETED", ... },
//   { action: "BRANCH_DELETED", ... }
// ]
```

### Notificação de Bloqueios

Quando uma PR é bloqueada, o sistema pode notificar via Slack ou log:

```typescript
const controller = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  notifyOnBlock: true,
  slackWebhook: "https://hooks.slack.com/services/...",
});

const result = await controller.mergePR(42);

if (result.status === MergeStatus.BLOCKED) {
  // Slack foi notificado automaticamente
  console.log("Bloqueado por:", result.blockedBy);
}
```

### Estratégias de Merge

Suporte para diferentes estratégias:

```typescript
// Merge commit (default)
const controller1 = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  mergeMethod: "merge",
});

// Squash and merge
const controller2 = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  mergeMethod: "squash",
  commitMessage: "Squashed PR: feature implementation",
});

// Rebase and merge
const controller3 = new AutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  mergeMethod: "rebase",
});
```

## Tipos

### MergeStatus

Estados possíveis do processo de merge:

```typescript
enum MergeStatus {
  PENDING = "pending",                          // Aguardando inicio
  CHECKING_PREREQUISITES = "checking_prerequisites", // Verificando pré-requisitos
  READY_TO_MERGE = "ready_to_merge",           // Pronto para merge
  MERGING = "merging",                         // Em processo de merge
  MERGED = "merged",                           // Merge completado
  FAILED = "failed",                           // Falha no processo
  BLOCKED = "blocked",                         // Bloqueado por pré-requisitos
  REQUIRES_HUMAN_REVIEW = "requires_human_review", // Requer revisão humana
}
```

### BlockReason

Razões pelas quais um merge pode ser bloqueado:

```typescript
enum BlockReason {
  CI_FAILED = "ci_failed",                    // Pipeline de CI falhou
  MISSING_APPROVALS = "missing_approvals",    // Faltam approvals
  MERGE_CONFLICTS = "merge_conflicts",        // Conflitos de merge
  BRANCH_OUTDATED = "branch_outdated",        // Branch desatualizada
  REQUIRED_STATUS_CHECK_FAILED = "required_status_check_failed",
  DRAFT_PR = "draft_pr",                      // PR está em draft
  NETWORK_ERROR = "network_error",            // Erro de rede
  PERMISSION_DENIED = "permission_denied",    // Permissão negada
  UNKNOWN = "unknown",                        // Erro desconhecido
}
```

### MergeResult

Resultado detalhado da operação de merge:

```typescript
interface MergeResult {
  success: boolean;
  prNumber: number;
  owner: string;
  repo: string;
  status: MergeStatus;
  sha?: string;
  mergeCommitSha?: string;
  blockedBy?: BlockReason[];
  prerequisitesCheck?: PrerequisiteCheckResult;
  branchDeleted?: boolean;
  auditEvents: AuditEvent[];
  timestamp: Date;
  duration?: number; // milliseconds
  error?: string;
}
```

### AuditEvent

Evento registrado no audit trail:

```typescript
interface AuditEvent {
  timestamp: Date;
  action: string;
  status: string;
  prNumber: number;
  owner: string;
  repo: string;
  details?: Record<string, any>;
  error?: string;
  userId?: string;
}
```

## Configuração (AutoMergeConfig)

```typescript
interface AutoMergeConfig {
  // Obrigatórios
  githubToken: string;      // Token GitHub
  owner: string;            // Dono do repositório
  repo: string;             // Nome do repositório

  // Pré-requisitos
  requireCIPassed?: boolean;        // Exigir CI passou (default: true)
  requiredApprovals?: number;       // Número de approvals (default: 1)
  allowMergingWithConflicts?: boolean; // Permitir conflitos (default: false)

  // Estratégia de merge
  mergeMethod?: "merge" | "squash" | "rebase"; // (default: "merge")
  commitMessage?: string;           // Mensagem do commit
  commitDescription?: string;       // Descrição do commit
  deleteBranchAfterMerge?: boolean; // Deletar branch (default: true)

  // Audit
  auditTableUrl?: string;    // URL da tabela Supabase para audit
  auditApiKey?: string;      // API Key do Supabase

  // Notificações
  notifyOnBlock?: boolean;           // Notificar quando bloqueado (default: true)
  slackWebhook?: string;             // Webhook do Slack

  // Thresholds
  maxWaitForCI?: number;     // Tempo máximo para CI (ms)
  checkInterval?: number;    // Intervalo entre verificações (ms)
}
```

## Exemplos

### Exemplo 1: Merge Automático Básico

```typescript
import { createAutoMergeController } from "./services";

async function autoMergePR() {
  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: "my-org",
    repo: "my-repo",
  });

  const result = await controller.mergePR(123);

  if (result.success) {
    console.log(`✅ PR #${result.prNumber} merged successfully`);
    console.log(`   Commit: ${result.mergeCommitSha}`);
    console.log(`   Branch deleted: ${result.branchDeleted}`);
  } else {
    console.log(`❌ Merge failed: ${result.error}`);
    console.log(`   Blocked by: ${result.blockedBy?.join(", ")}`);
  }
}
```

### Exemplo 2: Integração com CI/CD Pipeline

```typescript
import { createAutoMergeController, MergeStatus } from "./services";

async function ciIntegration() {
  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: "my-org",
    repo: "my-repo",
    requireCIPassed: true,
    requiredApprovals: 2,
    mergeMethod: "squash",
  });

  // Fila de PRs para merge
  const prNumbers = [42, 43, 44];

  for (const prNumber of prNumbers) {
    console.log(`Processing PR #${prNumber}...`);
    
    const result = await controller.mergePR(prNumber);

    switch (result.status) {
      case MergeStatus.MERGED:
        console.log(`✅ Successfully merged PR #${prNumber}`);
        break;
      case MergeStatus.BLOCKED:
        console.log(`⚠️ PR #${prNumber} blocked: ${result.blockedBy?.join(", ")}`);
        break;
      case MergeStatus.FAILED:
        console.log(`❌ Failed to merge PR #${prNumber}: ${result.error}`);
        break;
    }
  }
}
```

### Exemplo 3: Audit Trail Completo

```typescript
import { createAutoMergeController } from "./services";

async function auditExample() {
  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: "my-org",
    repo: "my-repo",
    auditTableUrl: process.env.SUPABASE_AUDIT_URL!,
    auditApiKey: process.env.SUPABASE_API_KEY!,
  });

  const result = await controller.mergePR(123);

  // Audit trail é persistido automaticamente
  console.log("Audit Trail Events:");
  result.auditEvents.forEach((event) => {
    console.log(
      `  [${event.timestamp.toISOString()}] ${event.action} - ${event.status}`
    );
    if (event.details) {
      console.log(`    Details:`, event.details);
    }
  });
}
```

### Exemplo 4: Notificações via Slack

```typescript
import { createAutoMergeController, BlockReason } from "./services";

async function slackNotificationExample() {
  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: "my-org",
    repo: "my-repo",
    notifyOnBlock: true,
    slackWebhook: process.env.SLACK_WEBHOOK_URL!,
  });

  const result = await controller.mergePR(123);

  if (result.blockedBy?.includes(BlockReason.CI_FAILED)) {
    // Slack é notificado automaticamente
    console.log("🔔 Team has been notified on Slack");
  }
}
```

## API Reference

### `mergePR(prNumber: number): Promise<MergeResult>`

Executa o processo de auto-merge para um PR.

**Parâmetros:**
- `prNumber` — Número do PR no GitHub

**Retorna:** Resultado detalhado da operação

**Exemplo:**
```typescript
const result = await controller.mergePR(42);
```

### `getAuditLog(): AuditEvent[]`

Retorna o log de audit em memória.

**Retorna:** Array de eventos de audit

**Exemplo:**
```typescript
const events = controller.getAuditLog();
events.forEach(e => console.log(e.action));
```

### `clearAuditLog(): void`

Limpa o log de audit em memória.

**Exemplo:**
```typescript
controller.clearAuditLog();
```

## Fluxo de Processamento

```
┌─────────────────────────┐
│   mergePR(prNumber)     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Fetch PR Data (GitHub API)      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ checkPrerequisites()            │
├─────────────────────────────────┤
│ • Check Draft status            │
│ • Check Merge conflicts         │
│ • Check CI passed               │
│ • Check Approvals               │
│ • Check Branch outdated         │
│ • Check Status checks           │
└────────────┬────────────────────┘
             │
        ┌────┴─────┐
        │           │
   BLOCKED      PASSED
        │           │
    ┌───▼─┐    ┌────▼─────────────┐
    │ 🔔  │    │ performMerge()   │
    │ Notify   │ (GitHub API)     │
    └──────┘   └────┬────────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ deleteBranch()   │
            │ (if configured)  │
            └────┬─────────────┘
                 │
                 ▼
            ┌──────────────────┐
            │ persistAuditLog()│
            │ (if configured)  │
            └────┬─────────────┘
                 │
                 ▼
            ┌──────────────────┐
            │ Return Result    │
            └──────────────────┘
```

## Tratamento de Erros

O controller implementa fallback robusto:

1. **Erro de rede:** Notifica humano, registra em audit trail
2. **Pré-requisitos não atendidos:** Bloqueia, notifica (Slack/log), retorna detalhes
3. **Falha de merge:** Registra erro, não tenta deletar branch, retorna detalhe
4. **Falha de deleção de branch:** Continua mesmo assim (merge foi bem-sucedido)

## Integração com Supabase

Para persistir audit trail em Supabase:

```typescript
const controller = createAutoMergeController({
  githubToken: "ghp_xxx",
  owner: "my-org",
  repo: "my-repo",
  auditTableUrl: `${SUPABASE_URL}/rest/v1/auto_merge_audit`,
  auditApiKey: SUPABASE_KEY,
});

// Tabela esperada:
// auto_merge_audit (
//   id: bigint,
//   timestamp: timestamp,
//   action: text,
//   status: text,
//   pr_number: integer,
//   owner: text,
//   repo: text,
//   details: jsonb,
//   error: text
// )
```

## Integração com GitHub Actions

Para usar em um workflow GitHub Actions:

```yaml
name: Auto-Merge

on:
  pull_request:
    types: [opened, reopened, synchronize]

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Auto-Merge PR
        uses: ./
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          owner: ${{ github.repository_owner }}
          repo: ${{ github.event.repository.name }}
          pr-number: ${{ github.event.number }}
          slack-webhook: ${{ secrets.SLACK_WEBHOOK }}
```

## Performance

- **Verificação de pré-requisitos:** ~500ms (3-4 chamadas de API)
- **Merge:** ~1-2s (1 chamada de API PUT)
- **Deleção de branch:** ~500ms (1 chamada de API DELETE)
- **Total típico:** ~2-3 segundos

## Limitações

1. **Rate limiting:** Respeita rate limits do GitHub (60 req/min público, 5000 autenticado)
2. **Status mergeable null:** Se GitHub não conseguir calcular, assume true
3. **Conflicts em merge base:** Detecta apenas conflitos conhecidos
4. **Permissões:** Requer permissão `pull` ou superior no repo

## Changelog

### v1.0.0 (2024-07-31)
- Initial release
- Verificação de pré-requisitos completa
- Merge automático com múltiplas estratégias
- Deleção de branch pós-merge
- Audit trail completo
- Notificações via Slack
- Integração com Supabase
