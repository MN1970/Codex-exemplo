# SKILL.md — git-chaos-engineering

**Resilience Testing for Git Operations & CI/CD Pipelines**

Versão: **v1.0.0** (2026-07-26)
Tier: **Sonnet**
Execution: **Automated (staging, weekly) + on-demand**
Status: **Available**

---

## Visão Geral

`git-chaos-engineering` simula cenários de falha críticos em operações Git,
pipelines de merge, e integrações com GitHub, para validar resiliência,
recuperabilidade e completude de trilhas de auditoria.

Destina-se a:
- Validação de automation scripts (CI/CD)
- Verificação de procedimentos de rollback
- Testes de recuperação após falhas de rede/API
- Auditoria de integridade de dados pós-merge
- Simulação de cenários de catástrofe operacional

---

## 5 Cenários de Chaos

### Cenário 1: Timeout de Rede (Merge Hang)

**Trigger**: `git merge` inicia mas a comunicação com remote cai a 50% do caminho.

**Simulação**:
```bash
# Executa merge em pano de fundo
git merge feature/X &
MERGE_PID=$!

# Após 3s, simula timeout (reduz largura de banda a 1kb/s)
sleep 3
tc qdisc add dev eth0 root tbf rate=1kbit burst=32kbit latency=400ms

# Aguarda timeout do timeout (geralmente 30s no Git)
wait $MERGE_PID 2>/dev/null
MERGE_EXIT=$?

# Remove limitação
tc qdisc del dev eth0 root

# Verifica estado: merge.conflictResolution ou rebase.autostash?
```

**Falha esperada**:
```
error: unable to resolve reference HEAD
fatal: merge operation timed out
repository in MERGING state
```

**Recuperação**:
```bash
git merge --abort                    # restaura HEAD
git reset --hard HEAD               # limpa working tree
git status                          # verifica limpeza
```

**Métricas coletadas**:
- Tempo até timeout: ±30s (variável)
- Estado do repo: `MERGING`
- Completude de logs: 100% (Git logs os frames parciais)

---

### Cenário 2: Rate Limit Exceeded na GitHub API

**Trigger**: Fluxo de merge (push + PR check + API calls para release notes) atinge
rate limit (60 req/hr sem auth, 5000 req/hr com auth).

**Simulação**:
```bash
#!/bin/bash
# Consome rate limit com requests sucessivos antes da operação crítica

for i in {1..100}; do
  curl -s -H "Authorization: token ${GH_TOKEN}" \
    https://api.github.com/repos/owner/repo/issues \
    > /dev/null &
done

# Aguarda até a maioria falhar com 403
wait

# Tenta merge neste estado
git push origin feature/X:main 2>&1 | tee push.log

# Verifica para: "API rate limit exceeded"
```

**Falha esperada**:
```
remote: GitHub API error (403): API rate limit exceeded for user ID 12345.
remote: Please retry your request in 3600 seconds.
fatal: unable to access repository: 403 Forbidden
```

**Recuperação**:
```bash
# Estratégia 1: Aguardar rate limit window (1h)
sleep 3600
git push origin feature/X:main

# Estratégia 2: Fallback para token elevado (se disponível)
GH_TOKEN=${ELEVATED_GH_TOKEN} git push origin feature/X:main

# Estratégia 3: Escalata manual
echo "Rate limit hit. Trigger manual review: ESCALATION-001"
```

**Métricas coletadas**:
- Tempo até falha: 0-5s (API rejeita imediatamente)
- Retry behavior: exponencial backoff (2^n segundos, máx 3600s)
- Token fallback disponível: S/N
- Trilha de auditoria: log do 403 com timestamp

---

### Cenário 3: Merge Conflict em Arquivo Crítico

**Trigger**: Merge automático falha porque arquivo crítico (deployment config,
package.json, database migration) tem conflitos não-triviais.

**Simulação**:
```bash
# Cria branch de base com versão v1 de arquivo crítico
git checkout -b base-v1
echo "version: 1.0.0" > package.json
git add package.json
git commit -m "base: v1"

# Cria branch paralelo com versão v2
git checkout -b feature/upgrade-v2
echo "version: 2.0.0" > package.json
git add package.json
git commit -m "feature: upgrade to v2"

# Volta para base, simula mudança diferente (v1.5)
git checkout base-v1
echo "version: 1.5.0" > package.json
git commit -am "hotfix: bump to v1.5"

# Tenta merge
git merge feature/upgrade-v2
# >>> CONFLICT <<<
```

**Falha esperada**:
```
Auto-merging package.json
CONFLICT (content): Merge conflict in package.json
Automatic merge failed; fix conflicts and then commit the result.
```

**Cenários comuns em produção**:
1. **Migração de dados** (`migrations/001_add_users_table.sql`)
   - Ambas branches adicionam coluna diferente
   - Impossível reconciliar sem perda de semântica

2. **Deployment config** (`terraform/main.tf` ou `docker-compose.yml`)
   - Duas equipes modificam networking
   - Conflito não-resolvível automaticamente

3. **Versionamento** (`VERSION`, `setup.py`, `Cargo.toml`)
   - SemVer colide
   - Requer decisão humana sobre qual versão prevalece

**Recuperação**:
```bash
# Opção 1: Aceitar NOSSA versão (feature branch)
git checkout --ours package.json
git add package.json

# Opção 2: Aceitar DELES (main branch)
git checkout --theirs package.json
git add package.json

# Opção 3: Resolução manual + validação
# (arquivo precisa ser parseável/válido antes de commit)
vim package.json
npm install --dry-run  # valida semântica
git add package.json

# Completa merge
git commit -m "merge feature/upgrade-v2: resolve package.json conflict"
```

**Métricas coletadas**:
- Número de arquivos com conflito
- Linhas afetadas (LOC)
- Resolvibilidade automática: S/N
- Tempo até resolução manual
- Teste de validação pós-merge (npm install, terraform validate, etc)

---

### Cenário 4: Teste Pós-Merge Falha (Post-Merge CI)

**Trigger**: Merge completa, push é feito, mas CI/CD pipeline falha em testes
automatizados, deixando main branch em estado quebrado.

**Simulação**:
```bash
# Setup: main tem teste que passa
git checkout main
npm test  # ✅ passa

# Feature branch modifica código de forma que teste falha
git checkout -b feature/refactor
# ... modificações que quebram teste unitário ...
echo "console.log('missing return statement')" >> src/utils.js
# sem return statement → teste falha

# Merge completa localmente (sem rodar testes)
git merge feature/refactor
git push origin main

# Webhook GitHub dispara CI
# CI/CD pipeline (GitHub Actions, Jenkins, etc) executa:
npm test
# >>> FALHA <<<
# npm ERR! Test suite failed
# npm ERR! FAIL src/utils.test.js
```

**Falha esperada**:
```
FAIL src/utils.test.js
  ● should return valid object
    expect(utils.transform()).toBeDefined()
    Received: undefined

Tests:       1 passed, 1 failed, 2 total
Coverage:    78% (was 92%)
```

**Cascata de falhas**:
```
1. npm test fails
2. CI marks commit as FAILED
3. Deployment to staging blocked
4. Dependent PRs blocked (status check)
5. Dev team discovers main is broken
6. Requires manual rollback + fix
```

**Recuperação**:
```bash
# Opção 1: Rollback rápido (revert commit de merge)
git revert -m 1 <merge-commit-hash>
git push origin main

# Opção 2: Fix forward (corrige erro no mesmo branch)
# Assumindo que estamos localmente na feature ainda
git checkout feature/refactor
# ... corrige código ...
git add src/utils.js
git commit -m "fix: add missing return statement"
git push origin feature/refactor

# Re-teste
npm test  # ✅ passa
# Re-merge para main
git checkout main
git merge feature/refactor
git push origin main
# CI dispara novamente ✅

# Opção 3: Hotfix branch (se main já está merged)
git checkout main
git pull origin main
git checkout -b hotfix/utils-return
# ... corrige ...
git commit -am "hotfix: restore utils.js return"
git push origin hotfix/utils-return
# Abre PR rápida, merge com status check
```

**Métricas coletadas**:
- Tempo até CI falhar: 30-120s (depende de suite)
- Testes falhando: contagem
- Coverage impactada: %-point
- MTTR (Mean Time To Recovery): tempo até rollback/fix
- Commits impactados: quantos dependem de main quebrada

---

### Cenário 5: Cascata de Rollback Quebrada (Cascading Rollback Chain Breaks)

**Trigger**: Revert de um revert, ou rollback de rollback, deixa Git em estado
incerto onde a história refere-se a commits que foram "desfeitos" e refazidos.

**Simulação**:
```bash
# Histórico linear:
# A (initial) → B (feature) → C (revert B) → D (revert C) → ???

# Setup
git log --oneline
# d3e4f5a (HEAD → main) Revert "Revert 'feature X'"
# c2b1a0d Revert "feature X"
# b1a2c3d feature X
# a0b1c2d initial commit

# Problema: commit B está em estado "ghost"
# Se alguém fizer cherry-pick de B ou fizer merge de branch que contém B:
git checkout -b feature/uses-b
# ... código que depende de lógica introduzida em B ...
git commit -am "extend feature B"

# Tenta merge para main
git merge feature/uses-b
# ??? Conflicts ou comportamento indefinido porque B foi revertido e então desfeito

# Git não sabe se B "conta" ou não
```

**Cascata de fallout**:
```
1. Rollback de hotfix introduz revert commit
2. Dev não percebe que feature foi revertida
3. Dev faz novo commit que depende de lógica revertida
4. Merge gera conflitos estranhos ou merges "silenciosamente" com bugs
5. Testes passam porque não cobrem a combinação revert+merge
6. Deploy vai para prod
7. Apenas em prod, sob carga real, a lógica quebrada manifesta
8. Rollback em prod necessário
9. Mas rollback de prod = mais reverts = torna histórico ainda mais confuso
```

**Simulação de cenário real**:
```bash
#!/bin/bash

# Simulação de ciclo completo
git log --oneline | head -20

# Detectar "undo of undo":
# Se git log contiver "Revert 'Revert" → padrão suspeito

# Algoritmo de detecção:
git log --oneline | grep -E "Revert.*Revert" && \
  echo "WARNING: Cascading revert pattern detected"

# Validar integridade da árvore:
# Para cada commit merged para main após um revert de revert:
# - Rodar tests com aquele commit específico isolado
# - Verificar se comportamento é consistente com pre-revert state

for commit in $(git log --oneline main | cut -d' ' -f1); do
  git checkout $commit
  npm test > /tmp/test_${commit}.log 2>&1
  if [ $? -ne 0 ]; then
    echo "BROKEN COMMIT: $commit"
    echo "Diff from main:"
    git diff main..HEAD --stat
  fi
done
```

**Falhas esperadas**:
```
- Merge resolvido "limpo" mas testes falham
- Comportamento em prod diverge de staging
- Audit trail confuso (não claro qual versão prevalece)
- Revert de revert não é idempotente
```

**Recuperação**:
```bash
# Opção 1: Rewind to stable commit (antes do ciclo de revert)
# Identifica último commit estável antes dos reverts
STABLE=$(git log --oneline | grep -v "Revert" | head -1 | cut -d' ' -f1)
git reset --hard $STABLE
git push --force-with-lease origin main  # cuidado: reescreve história

# Opção 2: Squash + amend (if não-published)
# Reescreve últimas N commits em uma sequência linear clara
git rebase -i HEAD~5
# Interativamente squash commits de revert-cycle

# Opção 3: Audit trail reconstruction
# Reconstrói o que realmente aconteceu vs. história de commits
git log --all --graph --decorate --oneline > audit_before.txt
git fsck --full > integrity_check.txt
# Anexa como post-mortem ao incidente

# Opção 4: Branch limpo (cherry-pick apenas commits bons)
git checkout -b main-restored
git cherry-pick A B D  # pula os reverts, mantém lógica desejada
git push origin main-restored
# Code review + merge via PR
```

**Métricas coletadas**:
- Profundidade de revert chain (quantos níveis)
- Commits "fantasma" (revertidos + refeitos)
- Divergência de teste (testes passam em uma versão, falham em outra)
- Detecção de ciclo (algoritmo de busca em grafo)

---

## Saídas (Outputs)

### 1. Chaos Report (JSON)

```json
{
  "run_id": "chaos-2026-07-26T14:32:00Z",
  "environment": "staging",
  "scenarios_executed": 5,
  "timestamp": "2026-07-26T14:32:00Z",
  "duration_seconds": 245,
  "scenarios": [
    {
      "scenario_id": 1,
      "name": "Network Timeout (Merge Hang)",
      "status": "FAILED (as expected)",
      "trigger_time_ms": 3200,
      "failure_time_ms": 33400,
      "recovery_time_ms": 1200,
      "error": "fatal: merge operation timed out",
      "git_state_before": "on-branch=main commits_ahead=0",
      "git_state_after": "MERGING (abort successful)",
      "data_integrity": "100% (all commits preserved)",
      "audit_trail": "merge.log contains 47 frames",
      "metrics": {
        "timeout_triggered": true,
        "automatic_recovery": false,
        "manual_recovery_steps": 2,
        "files_corrupted": 0
      }
    },
    {
      "scenario_id": 2,
      "name": "GitHub API Rate Limit Exceeded",
      "status": "FAILED (as expected)",
      "trigger_time_ms": 0,
      "failure_time_ms": 4100,
      "recovery_time_ms": 3600000,
      "error": "GitHub API error (403): API rate limit exceeded",
      "mitigation": "Token fallback used (ELEVATED_GH_TOKEN)",
      "retry_strategy": "exponential backoff: 2^5 = 32 seconds",
      "automatic_recovery": true,
      "metrics": {
        "requests_before_limit": 87,
        "rate_limit_window_seconds": 3600,
        "token_fallback_available": true,
        "fallback_tokens_tested": 2
      }
    },
    {
      "scenario_id": 3,
      "name": "Merge Conflict (Critical File)",
      "status": "FAILED (as expected)",
      "conflict_file": "package.json",
      "conflict_lines": 3,
      "conflict_type": "version incompatibility",
      "auto_resolvable": false,
      "manual_resolution_time_ms": 45000,
      "post_merge_validation": "npm install --dry-run PASSED",
      "metrics": {
        "files_with_conflict": 1,
        "total_conflicts": 3,
        "resolution_strategy_used": "accept_ours + manual edit",
        "validation_passed": true,
        "data_loss_risk": "high (if auto-resolved with wrong strategy)"
      }
    },
    {
      "scenario_id": 4,
      "name": "Post-Merge Test Failure (CI)",
      "status": "FAILED (as expected)",
      "test_suite": "npm test",
      "failed_tests": 1,
      "total_tests": 42,
      "coverage_drop_percent": 14,
      "ci_detection_time_ms": 42000,
      "recovery_strategy": "revert --no-edit",
      "recovery_time_ms": 8400,
      "post_recovery_validation": "PASSED",
      "metrics": {
        "mttr_seconds": 8,
        "commits_impacted": 3,
        "branches_blocked": 5,
        "production_risk": "CRITICAL (if merged without CI gate)"
      }
    },
    {
      "scenario_id": 5,
      "name": "Cascading Rollback Chain Breaks",
      "status": "FAILED (as expected)",
      "revert_chain_depth": 3,
      "ghost_commits_detected": 2,
      "audit_trail_integrity": 87,
      "recovery_strategy": "reset --hard to stable commit",
      "recovery_time_ms": 2100,
      "history_rewrite": true,
      "git_fsck_errors": 0,
      "metrics": {
        "idempotence_test_passed": false,
        "squash_rebase_successful": true,
        "post_recovery_tests": "PASSED"
      }
    }
  ],
  "summary": {
    "total_scenarios": 5,
    "total_failures": 5,
    "expected_failures": 5,
    "unexpected_failures": 0,
    "average_recovery_time_ms": 803140,
    "data_integrity_score": 99.5,
    "audit_trail_completeness": 95
  }
}
```

### 2. Resilience Score (0-100)

```plaintext
╔═══════════════════════════════════════════════════════════════╗
║                    RESILIENCE SCORECARD                       ║
╚═══════════════════════════════════════════════════════════════╝

[████████░░] SCENARIO DETECTION:        88/100
  ├─ Timeout detection          ✅ 20/20
  ├─ Rate limit detection       ✅ 20/20
  ├─ Conflict detection         ✅ 20/20
  ├─ CI failure detection       ✅ 18/20  (delayed by 12s)
  └─ Revert chain detection     ✅ 10/20  (requires manual inspection)

[██████░░░░] AUTOMATIC RECOVERY:       60/100
  ├─ Network timeout            ✅ 12/20  (manual abort needed)
  ├─ Rate limit                 ✅ 20/20  (token fallback works)
  ├─ Merge conflict             ✗  0/20  (requires human decision)
  ├─ CI failure                 ✅ 18/20  (revert automatic)
  └─ Revert chain               ✅ 10/20  (detection only)

[████████░░] DATA INTEGRITY:           84/100
  ├─ No data loss               ✅ 20/20
  ├─ Audit trail preserved      ✅ 18/20  (gap in scenario 5)
  ├─ Commit shas stable         ✅ 16/20  (force-push risk)
  └─ Test consistency           ✅ 30/30  (all validations passed)

[██████████] RECOVERY TIME:            100/100
  ├─ Timeout MTTR               ✅ 20/20  (< 1 min)
  ├─ Rate limit MTTR            ✅ 20/20  (auto-retry works)
  ├─ Conflict MTTR              ✅ 18/20  (manual slow)
  ├─ CI failure MTTR            ✅ 20/20  (< 10 sec revert)
  └─ Revert chain MTTR          ✅ 22/20  (bonus: fsck clean)

[██████████] PROCESS MATURITY:         92/100
  ├─ Runbook quality            ✅ 20/20
  ├─ Documentation              ✅ 18/20  (one scenario underdoc'd)
  ├─ Automation coverage        ✅ 20/20
  ├─ Monitoring integration     ✅ 18/20  (Scenario 5 needs alert)
  └─ Training materials         ✅ 16/20

┌───────────────────────────────────────────────────────────────┐
│  OVERALL RESILIENCE SCORE:  84/100  ⚠ GOOD (needs improvement) │
│                                                               │
│  Risk Level:  MEDIUM                                         │
│  Recommendation: Address data-loss risks in Scenario 3 & 5   │
└───────────────────────────────────────────────────────────────┘

Comparison to industry baseline (CNCF resilience studies):
  Your score:  84
  Industry avg: 71
  Top tier:    95+

TREND: ↗ +4 points since last quarter
```

### 3. Resilience Scoring Formula

```
SCORE = (D + A + I + R + P) / 5

Where:
  D = Detection capability (0-100)
      = (scenarios_detected / total_scenarios) * 100
      + detection_latency_penalty
      + false_positive_penalty

  A = Automatic recovery rate (0-100)
      = (scenarios_auto_recovered / total_scenarios) * 100
      - manual_intervention_penalty
      - escalation_count_penalty

  I = Data integrity (0-100)
      = 100 - (data_loss_incidents * 20)
           - (audit_gaps_percent * 0.5)
           - (sha_mutation_count * 5)

  R = Recovery time (0-100)
      = min(100, (target_mttr / actual_mttr) * 100)
      where target_mttr = 5 minutes (300 seconds)
      Scenarios:
        - Timeout: target 60 sec
        - API rate: target 3600 sec (explicit window)
        - Conflict: target 300 sec
        - CI failure: target 30 sec
        - Revert chain: target 120 sec

  P = Process maturity (0-100)
      = (runbook_completeness * 0.3)
      + (automation_coverage * 0.25)
      + (monitoring_integration * 0.25)
      + (training_materials * 0.2)

Penalties Applied:
  - Each undetected scenario:      -20 points
  - False positive per 10:          -5 points
  - Manual escalation per item:     -10 points
  - Data loss incident:             -25 points
  - MTTR exceeds target by 50%:     -10 points
  - Incomplete runbook:             -15 points
  - No monitoring alert:            -12 points

Final score interpretation:
  90-100: EXCELLENT (enterprise-ready)
  80-89:  GOOD (production-ready, needs improvement)
  70-79:  FAIR (requires immediate action)
  <70:    POOR (not recommended for critical systems)
```

---

## Mitigação e Playbooks

### Playbook A: Network Timeout (Scenario 1)

**Detection**:
```bash
# Monitorar em tempo real
git --version  # estabelece baseline
timeout 35s git merge origin/feature/X || {
  EXIT=$?
  if [ $EXIT -eq 124 ]; then
    echo "ALERT: Merge timeout detected"
    CHAOS_LOG="merge_timeout_$(date +%s).log"
  fi
}
```

**Mitigation**:
1. **Prevenção**:
   - Usar `GIT_TRACE=true GIT_TRACE_PERFORMANCE=true` para diagnosticar lentidão
   - Configurar `git config core.preloadIndex true` para repositórios grandes
   - Usar shallow clones (`git clone --depth 1`) para CI/CD

2. **Detecção**:
   - Monitoring script: alertar se merge > 30s
   - Log de performance: registrar `GIT_TRACE_PERFORMANCE`

3. **Resposta**:
   ```bash
   git merge --abort
   git reset --hard HEAD
   # Retry com melhor conexão ou menor escopo
   ```

4. **Pós-Incidente**:
   - Analisar `GIT_TRACE_PERFORMANCE` logs
   - Verificar se rede tinha latência alta
   - Considerar split do merge em múltiplos PRs menores

---

### Playbook B: Rate Limit Exceeded (Scenario 2)

**Detection**:
```bash
# Check rate limit before operations
gh api rate_limit --jq '.rate.remaining'

# Se < 10: aguardar ou usar token elevado
REMAINING=$(gh api rate_limit --jq '.rate.remaining')
if [ $REMAINING -lt 10 ]; then
  echo "Rate limit critical. Using elevated token."
  export GH_TOKEN=${ELEVATED_GH_TOKEN}
fi
```

**Mitigation**:
1. **Prevenção**:
   - Usar GraphQL em vez de REST (mais eficiente)
   - Batcher: agrupar múltiplas requests
   - Cache de respostas por 5 min

2. **Escalas de contingência**:
   ```bash
   # Tier 1: Token regular (5000 req/hr)
   if rate_limit_critical; then
     # Tier 2: Elevated token (10000 req/hr)
     export GH_TOKEN=${ELEVATED_TOKEN}
   fi
   if still_critical; then
     # Tier 3: Manual escalation + wait window
     echo "Escalating to on-call engineer"
     PagerDuty incident created
     sleep 3600  # Aguarda reset do window
   fi
   ```

3. **Resposta**:
   - Retry com exponential backoff
   - Após esgotamento: human escalation

4. **Pós-Incidente**:
   - Analisar qual tool consumiu rate limit
   - Otimizar queries subsequentes

---

### Playbook C: Merge Conflict (Scenario 3)

**Detection**:
```bash
git merge origin/feature/X 2>&1 | tee merge.log
if grep -q "CONFLICT" merge.log; then
  echo "Merge conflict detected in:"
  git status | grep "both modified"
fi
```

**Mitigation**:
1. **Prevenção**:
   - Code review obrigatório antes de merge (não merge without review)
   - Semantic versioning: evita conflitos em VERSION files
   - CI gate: rodar testes em merge commit (antes de push)

2. **Resolução automática (onde possível)**:
   ```bash
   # Git pode auto-resolver algumas versões de conflito
   git config merge.conflictStyle diff3
   # Requer decisão humana de qualquer forma para package.json
   ```

3. **Resolução manual com validação**:
   ```bash
   # Editor interativo
   git mergetool --tool=vimdiff
   
   # Validação pós-resolução
   npm install --dry-run  # testa se valid JSON
   terraform validate      # testa se valid HCL
   
   # Se falhar: resolver novamente
   git add <arquivo>
   git commit -m "merge: resolve <arquivo> (validated)"
   ```

4. **Fallback se irresolvível**:
   ```bash
   git merge --abort
   # Abrir issue para discussão síncrona
   # Escalate para tech lead
   ```

---

### Playbook D: Post-Merge CI Failure (Scenario 4)

**Detection**:
```bash
# GitHub Actions (ou CI system) automático detecta
# Se suite falha: status check torna-se RED

# Local detection (pré-merge):
git merge --no-commit --no-ff origin/feature/X
npm test  # Rodar testes ANTES de finalizar merge
if [ $? -ne 0 ]; then
  git merge --abort
  echo "Tests would fail. Aborting merge."
fi
```

**Mitigation**:
1. **Prevenção**:
   - Obrigatório: rodar `npm test` localmente antes de push
   - Pre-commit hook: impedir commit se testes falham
   - Require status checks: GitHub bloqueia merge se CI falha

2. **Detecção automática**:
   - GitHub Actions / CI pipeline automático
   - Webhook notifica Slack / PagerDuty

3. **Resposta automática**:
   ```bash
   # Script de resposta automática no CI
   if npm test FAILED; then
     # Opção 1: Revert e notificar
     git revert -m 1 HEAD
     git push origin main
     
     # Notificar autor
     gh pr comment <pr> -b "@author CI failed. Reverted."
   fi
   ```

4. **Recovery**:
   - Author deve criar novo commit que corrige erro
   - Resubmeter PR
   - CI passa novamente

---

### Playbook E: Cascading Rollback Chain (Scenario 5)

**Detection**:
```bash
# Procurar padrão suspeito na história
git log --oneline | head -20

# Algoritmo: detectar "Revert of Revert"
if git log --oneline | grep -q "Revert.*Revert"; then
  echo "ALERT: Cascading revert pattern detected"
  # Investigar commits envolvidos
  git log -S "Revert" --oneline | head -10
fi

# Validação de integridade
git fsck --full
if [ $? -ne 0 ]; then
  echo "WARNING: Repository integrity issues found"
fi
```

**Mitigation**:
1. **Prevenção**:
   - Policy: máximo 1 nível de revert (não revert de revert sem discussão)
   - Squash rebase: manter história linear
   - Enforce: `git log --oneline` não deve conter palavra "Revert" >2 vezes na última semana

2. **Se ocorrer**:
   - **Opção A**: Reset para commit estável (antes dos reverts)
     ```bash
     STABLE=$(git log --oneline | grep -v "Revert" | head -1 | cut -d' ' -f1)
     git reset --hard $STABLE
     git push --force-with-lease origin main
     ```
   - **Opção B**: Squash rebase
     ```bash
     git rebase -i HEAD~5
     # Interativamente squash commits de revert-cycle em 1 commit
     ```
   - **Opção C**: Cherry-pick apenas commits bons
     ```bash
     git checkout -b main-restored $(git merge-base main develop)
     git cherry-pick A B D  # skip reverts
     git push origin main-restored
     # PR + merge
     ```

3. **Validação pós-recovery**:
   ```bash
   # Rodar testes em cada commit isolado
   git log --oneline | while read sha msg; do
     git checkout $sha
     npm test || echo "BROKEN: $sha"
   done
   
   # Verificar idempotência
   git checkout main
   npm test && npm test && npm test  # 3x rodar testes
   ```

---

## Métricas de Resiliência

| Métrica | Target | Como medir | Alerta |
|---------|--------|-----------|--------|
| **MTTD** (Mean Time To Detect) | < 30s | Tempo entre erro e log/alert | > 60s |
| **MTTR** (Mean Time To Recover) | < 5 min | Tempo entre falha e sistema saudável | > 10 min |
| **Data loss** | 0 | Verificar `git fsck --full` | > 0 bytes |
| **Audit trail gaps** | 0 | Revisar logs de operação | > 1 gap |
| **Test consistency** | 100% | Tests passam em todas versões | < 95% |
| **False positives** | < 5% | Detecções que não são reais falhas | > 10% |
| **Scenarios detected** | 100% | 5/5 cenários identificáveis | < 80% |
| **Automatic recovery** | > 60% | 3+ de 5 recuperações sem intervenção | < 50% |

---

## Execução Automatizada

### Agendamento (Semanal)

```yaml
# .github/workflows/chaos-engineering.yml
name: Git Chaos Engineering (Weekly)

on:
  schedule:
    - cron: '0 2 * * 1'  # Toda segunda-feira, 2h (UTC)

jobs:
  chaos-test:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history

      - name: Run Chaos Scenarios
        run: |
          bash ./scripts/chaos-scenarios.sh 2>&1 | tee chaos-report.log
        env:
          GH_TOKEN: ${{ secrets.ELEVATED_GH_TOKEN }}
          CHAOS_ENV: staging
          CHAOS_DRY_RUN: false

      - name: Generate Report (JSON)
        run: |
          python3 ./scripts/chaos-report-generator.py \
            --input chaos-report.log \
            --output chaos-report.json \
            --resilience-score

      - name: Upload Report Artifact
        uses: actions/upload-artifact@v4
        with:
          name: chaos-report-${{ github.run_id }}
          path: chaos-report.json

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_RESILIENCE }}
          payload: |
            {
              "text": "Chaos Engineering Report",
              "attachments": [{
                "color": "${{ job.status == 'success' && '#36a64f' || '#ff0000' }}",
                "text": "Resilience Score: ${{ env.RESILIENCE_SCORE }}/100",
                "actions": [{
                  "type": "button",
                  "text": "View Report",
                  "url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                }]
              }]
            }
```

### On-Demand Execution

```bash
# Rodar chaos tests manually (staging)
./scripts/chaos-scenarios.sh --environment staging --scenarios all

# Rodar apenas cenário 3 (conflict detection)
./scripts/chaos-scenarios.sh --scenario 3

# Dry-run (não fazer push real)
./scripts/chaos-scenarios.sh --dry-run
```

---

## Template de Post-Incident Review

```markdown
# Post-Incident Review — Git Chaos Test
**Date**: 2026-07-26  
**Incident Duration**: 3 minutes (scenario 4)  
**Severity**: MEDIUM (test environment only)  
**Author**: DevOps Team

## Executive Summary
Scenario 4 (Post-Merge CI Failure) exposed 3-minute delay in CI pipeline detection.
Normal recovery procedure (auto-revert) worked. Recommendation: tighten threshold.

## Timeline

| Time | Event |
|------|-------|
| 14:32:00 | Merge committed, pushed to main (staging) |
| 14:32:42 | CI pipeline triggered |
| 14:35:18 | CI failure detected (3m 18s latency) |
| 14:35:34 | Auto-revert initiated |
| 14:35:42 | Revert merged to main |
| 14:35:51 | Tests passing again |

## Root Cause Analysis

**Primary**: GitHub Actions queue delayed by 6 jobs ahead (unrelated workload).

**Contributing factors**:
1. No priority queue for critical CI checks
2. Test suite runtime = 45s (could be optimized)
3. No Slack alert for >2m CI latency

## Impact

- Main branch in failed state: 3m 18s
- Dependent PRs blocked: 2 PRs
- Developer experience: 3 devs notified of broken main

## Lessons Learned

| What went well | What could be better |
|---|---|
| Auto-revert worked immediately | Detection latency too high (3+ min) |
| No data loss | Test suite runtime > 45s |
| Audit trail complete | No priority queue for critical jobs |
| | Alert threshold not tight enough |

## Action Items

| ID | Action | Owner | Due | Priority |
|----|--------|-------|-----|----------|
| A1 | Optimize test suite (target: 30s) | QA Lead | 2026-08-09 | HIGH |
| A2 | Add priority queue to CI runner | DevOps | 2026-07-30 | HIGH |
| A3 | Lower alert threshold (2min → 90s) | DevOps | 2026-07-27 | MEDIUM |
| A4 | Update on-call runbook | SRE | 2026-07-28 | LOW |

## Metrics

```
Before fix:
  - MTTD: 3m 18s
  - MTTR: 8s (auto-revert)
  - Data loss: 0
  - Resilience score: 84/100

After fixes (projected):
  - MTTD: 90s (target)
  - MTTR: 8s (same)
  - Resilience score: 92/100 (projected)
```

## Appendix

### A. Logs
[Attach chaos-report.json]

### B. Related Issues
- GitHub Issue #1234: "CI latency tracking"
- GitHub Issue #1235: "Test optimization"
```

---

## Tools & Dependencies

| Tool | Propósito | Versão |
|------|-----------|--------|
| **git** | Core version control | ≥ 2.40 |
| **gh** | GitHub CLI | ≥ 2.30 |
| **GitHub MCP** | Machine-callable GitHub API | v2.0+ |
| **Bash** | Scenario scripting | ≥ 5.0 |
| **npm** (ou similar) | Test execution | ≥ 8.0 |
| **jq** | JSON parsing | ≥ 1.6 |
| **tc (iproute2)** | Network simulation | ≥ 5.0 |
| **Python 3** | Report generation | ≥ 3.9 |

---

## Como Invocar Esta Skill

```bash
# Sintaxe geral
claude skill:git-chaos-engineering \
  --scenarios all \
  --environment staging \
  --format json \
  --output-file chaos-report.json

# Exemplos

# 1. Rodar todos os 5 cenários (default)
claude skill:git-chaos-engineering

# 2. Rodar apenas cenário específico
claude skill:git-chaos-engineering --scenario 3

# 3. Dry-run (não fazer mudanças reais)
claude skill:git-chaos-engineering --dry-run

# 4. Gerar relatório com score
claude skill:git-chaos-engineering \
  --resilience-score \
  --format json \
  > chaos-report-$(date +%s).json

# 5. Enviar relatório para Slack
claude skill:git-chaos-engineering \
  --notify-slack=#resilience-tests \
  --webhook-url $SLACK_WEBHOOK
```

---

## Referências & Leitura Adicional

- **CNCF Resilience Research**: https://www.cncf.io/reports/
- **Git Internals**: https://git-scm.com/book/en/v2/Git-Internals
- **GitHub API Rate Limiting**: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- **Chaos Engineering Principles**: https://principlesofchaos.org/
- **SRE Book**: https://sre.google/books/
- **OWASP - Resilience Testing**: https://owasp.org/

---

## Histórico de Versões

- **v1.0.0** (2026-07-26) — Initial release com 5 cenários, playbooks, scoring formula
