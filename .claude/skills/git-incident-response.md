# Git Incident Response

**Version:** 1.0.0  
**Tier:** Sonnet  
**Manta Code:** Sec-INC-01  
**Updated:** 2026-07-26

## Overview

Automated detection and remediation of security incidents in Git repositories. Detects hardcoded secrets, vulnerable dependencies, and suspicious activity. Executes remediation playbooks with escalation and audit logging.

**When to Use:**
- "Scan for leaked secrets"
- "Check vulnerable dependencies"
- "Analyze suspicious commit activity"
- "Emergency rollback on breach"
- "Incident response automation"

## Detection Triggers (9 Secret Patterns)

### API Keys & Tokens
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- GitHub personal access tokens
- Stripe API keys (sk_live, sk_test)
- Slack API tokens
- JWT tokens with secrets

### Credentials
- Database passwords (mongodb://, postgresql://)
- Private SSH keys (.pem, .key)
- Certificates (.crt)
- API credentials (Basic Auth)

### Additional Patterns
- Hardcoded IP addresses (127.0.0.1, 10.0.0.0/8 in code)
- Environment secrets (.env files)
- Cloud credentials (GCP, Azure)

## Auto-Remediation Playbook

### 5-Step Flow: Contain → Analyze → Remediate → Escalate → Audit

1. **CONTAIN** (0-5 min)
   - Pause CI/CD pipeline
   - Create draft PR to revert
   - Notify on-call security engineer

2. **ANALYZE** (5-15 min)
   - Determine secret scope (API key, database password, etc.)
   - Check git history for usage (how long exposed?)
   - Identify affected systems/services

3. **REMEDIATE** (15-45 min)
   - Revoke/rotate the exposed secret
   - Update all references in code/config
   - Deploy updated code to production

4. **ESCALATE** (ongoing)
   - CRITICAL: CTO + CISO + security-eng → 5 min SLA
   - HIGH: Team lead → 1 hour SLA
   - MEDIUM: Log only → 24 hour SLA

5. **AUDIT** (48 hours)
   - Document incident (RCA, timeline, remediation)
   - Update playbooks based on learnings
   - Compliance reporting (SOC2, HIPAA, PCI-DSS)

## Incident Scenarios

### Scenario 1: Hardcoded Stripe API Key
```json
{
  "incident_id": "INC-2026-07-26-001",
  "severity": "CRITICAL",
  "type": "hardcoded_api_key",
  "detected_at": "2026-07-26T12:00:00Z",
  "secret_type": "Stripe API key (sk_live_xxxxx)",
  "exposed_duration": "14 days (since commit abc1234)",
  "affected_services": ["payment-service"],
  "remediation_steps": [
    "Revoke key in Stripe dashboard",
    "Generate new API key",
    "Update production config",
    "Deploy new code with secret removal"
  ],
  "status": "CONTAINED",
  "escalation": "CTO, CISO notified"
}
```

### Scenario 2: Vulnerable Dependency
```json
{
  "incident_id": "INC-2026-07-26-002",
  "severity": "CRITICAL",
  "type": "vulnerable_dependency",
  "package": "lodash",
  "version": "4.17.20",
  "cve": "CVE-2021-23337",
  "cvss_score": 9.1,
  "remediation": "Update to lodash@4.17.21+"
}
```

### Scenario 3: Suspicious Commit Churn
```json
{
  "incident_id": "INC-2026-07-26-003",
  "severity": "HIGH",
  "type": "suspicious_activity",
  "commits_in_1h": 47,
  "files_modified": 1200,
  "suspicious_patterns": ["mass deletion", "bulk chmod", "credential addition"],
  "suspected_compromise": "Author account may be compromised",
  "action": "Suspend account + rotate credentials"
}
```

## Escalation Matrix

| Severity | Alert | SLA | Contacts |
|----------|-------|-----|----------|
| **CRITICAL** | 🚨 Slack #security-incidents | 5 min | CTO, CISO, security-eng |
| **HIGH** | ⚠️ Slack + Jira P1 | 1 hour | Team lead, security-eng |
| **MEDIUM** | 📋 Log only | 24 hours | Security team digest |
| **LOW** | 🔔 Weekly digest | — | Team notification |

## Configuration

```json
{
  "secret_patterns": {
    "aws_keys": true,
    "github_tokens": true,
    "stripe_keys": true,
    "private_keys": true,
    "entropy_threshold": 4.5
  },
  "dependency_scanning": {
    "enabled": true,
    "cvss_threshold": 7.0,
    "check_transitive": true
  },
  "anomaly_detection": {
    "enabled": true,
    "commit_churn_threshold": 50,
    "mass_deletion_threshold": 1000
  },
  "rate_limit": {
    "max_incidents_per_hour": 10,
    "digest_mode": true
  },
  "notifications": {
    "slack": "#security-incidents",
    "pagerduty": true,
    "jira": true
  }
}
```

## Tools Required

- GitHub API (`search_code`, `get_commit`, `list_commits`)
- Bash/ripgrep (local scanning)
- npm audit, pip safety, cargo audit (dependency scanning)
- Slack MCP (notifications)
- Jira API (incident tracking)
- AWS S3 + KMS (secure secret storage)

## Related Skills

- `git-threat-modeling` — Identify architecture-level risks
- `git-code-pattern-detection` — Scan for code anti-patterns
- `git-pr-autoreview` — Prevent secrets in PRs

## Limitations

⚠️ **Detection is Pattern-Based**
- Entropy analysis may miss sophisticated obfuscation
- Custom secret formats may not be detected
- Transitive dependencies require external scanning
- Compromised SSH keys require manual verification

**Requires Manual Verification:**
- Actual secret validity (test exposure)
- Business impact assessment
- Severity determination
- Remediation approval
