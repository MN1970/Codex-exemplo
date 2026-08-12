# CI Integration Guide — Agent Audit & Remediation v5.0

**Document Version:** 1.0  
**Last Updated:** 2026-07-25  
**Scope:** Integration of `audit_agents.py` v2 + `regenerate_skill.py` into CI/CD pipelines

---

## Overview

This guide shows how to integrate drift detection and auto-remediation into your CI pipeline:

1. **Audit Phase** (`audit_agents.py`) — Detects divergences
2. **Remediation Phase** (`regenerate_skill.py`) — Auto-fixes if needed
3. **Report Generation** — JSON (machine-readable), HTML (human-readable), CSV (data)
4. **Slack Alerts** — Notify team on drift

**Key principle:** Fail CI if drift detected, unless explicitly whitelisted.

---

## Quick Start

### 1. Run Audit

```bash
cd /home/user/Codex-exemplo

python scripts/audit_agents.py \
  --agents-dir .claude/agents \
  --claude-md CLAUDE.md \
  --versions-json VERSIONS.json \
  --settings-json .claude/settings.json \
  --output-format json \
  --output-dir rag_evals \
  --divergence-threshold 0 \
  --verbose
```

**Output files:**
- `rag_evals/audit_agents.json` — Full audit results
- `rag_evals/divergence_report.json` — Drift details + remediation commands
- `audit.log` — Execution log

### 2. Check Exit Code

```bash
python scripts/audit_agents.py --divergence-threshold 0
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "PASS: All agents synced"
else
  echo "FAIL: Drift detected"
  cat rag_evals/divergence_report.json
  exit 1
fi
```

### 3. Auto-Remediate (Optional)

```bash
# Dry-run first
python scripts/regenerate_skill.py --all --dry-run

# Apply changes
python scripts/regenerate_skill.py --all
```

---

## GitHub Actions Workflow

### Example: `.github/workflows/audit-agents.yml`

```yaml
name: Agent Audit & Drift Detection

on:
  pull_request:
    paths:
      - '.claude/agents/**'
      - 'CLAUDE.md'
      - 'VERSIONS.json'
      - '.claude/settings.json'
  schedule:
    # Daily audit at 02:00 UTC
    - cron: '0 2 * * *'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Agent Audit
        id: audit
        run: |
          python scripts/audit_agents.py \
            --agents-dir .claude/agents \
            --claude-md CLAUDE.md \
            --versions-json VERSIONS.json \
            --settings-json .claude/settings.json \
            --output-format json \
            --output-dir rag_evals \
            --divergence-threshold 0 \
            --verbose

      - name: Upload audit reports
        uses: actions/upload-artifact@v3
        with:
          name: audit-reports
          path: rag_evals/
          retention-days: 30

      - name: Check audit result
        run: |
          DIVERGENCES=$(jq '.divergence_summary | (.drift + .not_in_registry + .missing_version)' rag_evals/audit_agents.json)
          echo "Total divergences: $DIVERGENCES"
          
          if [ "$DIVERGENCES" -gt 0 ]; then
            echo "::error::Agent drift detected. Review divergence_report.json"
            cat rag_evals/divergence_report.json
            exit 1
          fi

      - name: Notify Slack (on failure)
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Agent audit failed on ${{ github.ref }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Agent Audit Failed*\nRepo: ${{ github.repository }}\nBranch: ${{ github.ref }}\nCommit: ${{ github.sha }}"
                  }
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Review divergence report: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_AGENT_OPS }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

---

## GitLab CI/CD Pipeline

### Example: `.gitlab-ci.yml`

```yaml
stages:
  - audit
  - remediate
  - report

variables:
  AGENTS_DIR: ".claude/agents"
  CLAUDE_MD: "CLAUDE.md"
  VERSIONS_JSON: "VERSIONS.json"
  SETTINGS_JSON: ".claude/settings.json"

audit_agents:
  stage: audit
  image: python:3.11
  script:
    - mkdir -p rag_evals
    - python scripts/audit_agents.py \
        --agents-dir $AGENTS_DIR \
        --claude-md $CLAUDE_MD \
        --versions-json $VERSIONS_JSON \
        --settings-json $SETTINGS_JSON \
        --output-format json \
        --output-dir rag_evals \
        --divergence-threshold 0 \
        --verbose
    
    # Check divergences
    - |
      DIVERGENCES=$(jq '.divergence_summary | (.drift + .not_in_registry + .missing_version)' rag_evals/audit_agents.json)
      echo "Total divergences: $DIVERGENCES"
      [ "$DIVERGENCES" -eq 0 ] || exit 1
  
  artifacts:
    paths:
      - rag_evals/
      - audit.log
    reports:
      junit: rag_evals/audit_agents.json
    expire_in: 30 days
  allow_failure: false

remediate_on_drift:
  stage: remediate
  image: python:3.11
  script:
    - python scripts/regenerate_skill.py --all --verbose
  only:
    - merge_requests
  when: on_failure

publish_report:
  stage: report
  image: python:3.11
  script:
    - python scripts/audit_agents.py \
        --agents-dir $AGENTS_DIR \
        --output-format html \
        --output-dir rag_evals
  artifacts:
    paths:
      - rag_evals/audit_agents.html
    expire_in: 90 days
  only:
    - main
```

---

## Jenkins Pipeline

### Example: `Jenkinsfile`

```groovy
pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Audit') {
            steps {
                script {
                    sh '''
                        echo "Running Agent Audit v5.0..."
                        mkdir -p rag_evals
                        
                        python scripts/audit_agents.py \
                            --agents-dir .claude/agents \
                            --claude-md CLAUDE.md \
                            --versions-json VERSIONS.json \
                            --settings-json .claude/settings.json \
                            --output-format json \
                            --output-dir rag_evals \
                            --divergence-threshold 0 \
                            --verbose
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'rag_evals/**', allowEmptyArchive: false
                    publishHTML([
                        reportDir: 'rag_evals',
                        reportFiles: 'audit_agents.html',
                        reportName: 'Agent Audit Report'
                    ])
                }
                failure {
                    script {
                        def divergenceReport = readJSON file: 'rag_evals/divergence_report.json'
                        def divergences = divergenceReport.summary.total_divergences
                        
                        echo "Detected ${divergences} divergence(s)"
                        echo "Agents to fix: ${divergenceReport.remediation.agents_to_fix}"
                        
                        // Send Slack alert
                        slackSend(
                            color: 'danger',
                            message: """Agent Audit Failed
                            Job: ${env.JOB_NAME}
                            Build: ${env.BUILD_NUMBER}
                            Divergences: ${divergences}
                            """,
                            webhookUrl: env.SLACK_WEBHOOK
                        )
                    }
                }
            }
        }

        stage('Remediate') {
            when {
                expression { currentBuild.result == 'FAILURE' }
            }
            steps {
                script {
                    sh '''
                        echo "Auto-remediating drift..."
                        python scripts/regenerate_skill.py --all --verbose
                    '''
                }
            }
        }

        stage('Commit & Push') {
            when {
                expression { currentBuild.result != 'SUCCESS' }
            }
            steps {
                script {
                    sh '''
                        git config user.email "audit@manta.internal"
                        git config user.name "Manta Maestro CI"
                        
                        git add .claude/agents/**
                        git add VERSIONS.json
                        git add .claude/settings.json
                        
                        git commit -m "chore: auto-sync agents to v5.0 canonical spec"
                        git push origin ${env.GIT_BRANCH}
                    '''
                }
            }
        }
    }

    post {
        always {
            junit 'rag_evals/audit_agents.json'
            cleanWs()
        }
    }
}
```

---

## Pre-commit Hook

### Example: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "Running agent audit pre-commit hook..."

STAGED_FILES=$(git diff --cached --name-only)

# Check if any agent/config files are staged
if echo "$STAGED_FILES" | grep -qE '(\.claude/agents/|CLAUDE\.md|VERSIONS\.json|settings\.json)'; then
    echo "Agent files detected. Running audit..."
    
    python scripts/audit_agents.py \
        --agents-dir .claude/agents \
        --claude-md CLAUDE.md \
        --versions-json VERSIONS.json \
        --settings-json .claude/settings.json \
        --divergence-threshold 0 \
        --verbose
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Agent audit failed. Commit blocked."
        echo "Run: python scripts/regenerate_skill.py --all"
        exit 1
    fi
fi

exit 0
```

Install:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Drift Handling Strategy

### Strategy 1: Fail on Any Drift (Strictest)

```bash
python scripts/audit_agents.py --divergence-threshold 0
```

**Use case:** Production deployments, compliance-sensitive projects.

### Strategy 2: Fail on Critical Drift Only

```bash
python scripts/audit_agents.py \
  --divergence-threshold 1 \
  # Allows 1 minor divergence (e.g., missing RAG collection)
```

**Use case:** Development, feature branches.

### Strategy 3: Warn & Auto-Remediate

```bash
python scripts/audit_agents.py --divergence-threshold 0 || {
    echo "Drift detected. Auto-remediating..."
    python scripts/regenerate_skill.py --all
    exit 1  # Still fail to require review
}
```

**Use case:** Automated maintenance pipelines.

---

## Interpreting `divergence_report.json`

### Structure

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-07-25T14:32:00Z",
  "summary": {
    "total_agents_scanned": 5,
    "agents_with_drift": 1,
    "total_divergences": 2
  },
  "divergences": [
    {
      "agent_id": "agente-energia",
      "status": "drift",
      "divergence_reasons": [
        "CHECKSUM_MISMATCH",
        "SKILL_PIN_MISMATCH"
      ],
      "checksum_actual": "d1a4f3c2b5e6a7d8e9f1a2b3c4d5e6f7",
      "checksum_expected": "e2b5c3a1d6f4e7c8b9a1d2e3f4a5b6c7",
      "remediation_command": "python scripts/regenerate_skill.py --agent agente-energia"
    }
  ],
  "remediation": {
    "auto_sync_command": "python scripts/regenerate_skill.py --all --dry-run",
    "agents_to_fix": [
      {
        "agent_id": "agente-energia",
        "command": "python scripts/regenerate_skill.py --agent agente-energia"
      }
    ]
  }
}
```

### Divergence Types

| Code | Meaning | Severity | Auto-fixable? |
|------|---------|----------|---------------|
| `CHECKSUM_MISMATCH` | File content differs from canonical | HIGH | Yes |
| `SKILL_PIN_MISMATCH` | settings.json version wrong | MEDIUM | Yes |
| `MODEL_MISMATCH` | Model tier not matching spec | MEDIUM | Yes |
| `NOT_IN_CANONICAL_20` | Agent not in v5.0 spec | CRITICAL | No |
| `NO_V5_SPEC_IN_VERSIONS_JSON` | Missing v5.0 entry | HIGH | No |
| `MISSING_RAG_COLLECTION_SPEC` | RAG not defined (verticals) | LOW | No |

---

## Monitoring & Alerts

### Slack Integration

```bash
python scripts/audit_agents.py \
  --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  --verbose
```

### Grafana Dashboard

Create a Grafana dashboard from `rag_evals/audit_agents.json`:

```json
{
  "title": "Agent Audit Metrics",
  "panels": [
    {
      "title": "Agents Synced",
      "targets": [
        {
          "expr": "divergence_summary.synced"
        }
      ]
    },
    {
      "title": "Drift Detected",
      "targets": [
        {
          "expr": "divergence_summary.drift"
        }
      ]
    }
  ]
}
```

---

## Troubleshooting

### Issue: `FileNotFoundError: VERSIONS.json`

**Solution:**
```bash
# Ensure VERSIONS.json exists in repo root
ls -la VERSIONS.json

# If missing, restore from git history
git checkout HEAD -- VERSIONS.json
```

### Issue: `Divergence detected but script shows passing`

**Solution:** Check divergence threshold:
```bash
python scripts/audit_agents.py --divergence-threshold 0 --verbose
```

### Issue: `regenerate_skill.py fails with write permission error`

**Solution:** Check directory permissions:
```bash
chmod -R 755 .claude/agents/
chmod 755 VERSIONS.json .claude/settings.json
```

### Issue: Checksum mismatch after fix

**Solution:** Regenerate and re-check:
```bash
python scripts/regenerate_skill.py --agent agente-saneamento
python scripts/audit_agents.py --verbose
```

---

## Best Practices

1. **Run audit on every commit** — Use pre-commit hook or CI
2. **Fail on drift in main branch** — `--divergence-threshold 0`
3. **Allow grace period in dev** — `--divergence-threshold 5` for feature branches
4. **Pin versions explicitly** — Always set `skill_version_pin` in settings.json
5. **Review drift before auto-fix** — Use `--dry-run` first
6. **Maintain VERSIONS.json** — Update checksums when intentionally modifying agents
7. **Archive old versions** — Keep v4.9 in VERSIONS.json for 30 days after deprecation

---

## Related Documentation

- [CLAUDE.md v5.0](../CLAUDE.md) — Agent registry specification
- [VERSIONS.json](../VERSIONS.json) — Version & checksum tracking
- [scripts/README.md](./README.md) — Script documentation

---

**Contact:** mneves@mantaassociados.com  
**Last Updated:** 2026-07-25
