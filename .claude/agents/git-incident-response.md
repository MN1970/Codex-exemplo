# SKILL.md — git-incident-response

**Automated Security Incident Response for Git Repositories**

Version: **v1.0** (2026-07-26)

---

## Overview

`git-incident-response` is an automated security incident detection and remediation skill for Git repositories. It monitors commits, pull requests, and dependencies for security threats—leaked credentials, vulnerable packages, and suspicious activity—and executes a playbook to contain, log, escalate, and remediate incidents in real time.

**Tier:** Sonnet  
**Invocation:** `/git-incident-response [--scan-repo|--monitor-pr|--check-deps] [--dry-run]`  
**Model:** claude-3-5-sonnet-20241022

---

## Purpose & Use Cases

- **Incident detection:** Catch hardcoded secrets, AWS credentials, API keys, JWT tokens, database passwords before they land in production
- **Dependency scanning:** Flag vulnerable packages in `package.json`, `requirements.txt`, `go.mod`, `Gemfile`
- **Anomaly detection:** Alert on suspicious commit patterns (high churn, mass deletions, unusual authorship)
- **Automated triage & escalation:** Route incidents by severity (CRITICAL → C-suite, HIGH → team lead, MEDIUM → log-only)
- **Audit trail:** Immutable log of every detection, decision, and remediation action
- **Compliance:** Meet PCI-DSS, SOC 2, HIPAA requirements for incident response

---

## Detection Triggers

### 1. Hardcoded Secrets (Regex-based + entropy analysis)

| Pattern | Example | Severity |
|---------|---------|----------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | CRITICAL |
| AWS Secret Key | `aws_secret_access_key = [A-Za-z0-9/+=]{40}` | CRITICAL |
| GitHub Token | `ghp_[A-Za-z0-9_]{36,255}` | CRITICAL |
| Slack Token | `xox[baprs]-[0-9]{10,13}-[A-Za-z0-9]{24,26}` | CRITICAL |
| API Key (generic) | `api[_-]?key\s*[:=]\s*['"]?[A-Za-z0-9]{32,}['"]?` | HIGH |
| Database password | `password\s*[:=]\s*['"]?[^\s'"\n]{8,}['"]?` | HIGH |
| JWT Token | `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.` | HIGH |
| Private key | `-----BEGIN (RSA|DSA|EC|PGP) PRIVATE KEY-----` | CRITICAL |
| Stripe key | `sk_live_[A-Za-z0-9]{20,}` | CRITICAL |

### 2. Vulnerable Dependencies

**Severity** = CVE CVSS score + reachability analysis

- `npm audit` / `yarn audit` (Node.js)
- `pip install safety` (Python)
- `go list -json -m all` + GHSA feed (Go)
- `bundle audit` (Ruby)
- **Threshold:** CVSS ≥ 7.0 → HIGH; ≥ 9.0 → CRITICAL

### 3. Suspicious Activity

| Pattern | Threshold | Severity |
|---------|-----------|----------|
| High commit churn | >50 files/commit × 5 commits/hour | MEDIUM |
| Mass file deletion | >100 files deleted in single commit | HIGH |
| Unusual author | Commit from unknown email after lockdown | HIGH |
| Forced push to main | Any `git push -f` to protected branch | CRITICAL |

---

## Auto-Remediation Playbook

```
INCIDENT DETECTED
  ↓
[1] CONTAIN
  • Pause CI/CD pipeline (if CRITICAL)
  • Comment on PR: "Security hold: incident #12345 detected"
  • Revoke leaked token immediately (GitHub API)
  ↓
[2] ANALYZE
  • Grep commit history for token patterns (past 90 days)
  • Check if secret was used to access resources
  • Map affected systems (prod, staging, dev)
  ↓
[3] REMEDIATE
  • CRITICAL: Rotate secret → revoke old key → issue new key
  • HIGH: Create ticket + notify team lead
  • MEDIUM: Log incident, no action if not in protected branch
  ↓
[4] ESCALATE
  • CRITICAL: Slack #security-incidents + email CTO/CISO
  • HIGH: Slack @team-lead + create Jira ticket
  • MEDIUM: Log to incident database, no alert
  ↓
[5] AUDIT & CLOSE
  • Write immutable incident report (JSON)
  • Store in secure S3 bucket (encrypted)
  • Close PR or merge after remediation
  • Tag commit for forensics
```

---

## Incident Types & Scenarios

### Scenario 1: Hardcoded API Key in PR

**Trigger:** PR #423 adds `config.json` with `"api_key": "sk_live_51abc...xyz"`

**Flow:**
1. **Detect:** Regex match + entropy check (>4.0 bits/char)
2. **Contain:** Comment on PR: "Security hold: Stripe secret detected (token: sk_live_51abc...xyz)"
3. **Revoke:** Call Stripe API to revoke `sk_live_51abc...xyz`
4. **Issue new key:** Generate new Stripe token, push to secure vault
5. **Escalate:** Slack #security-incidents + email security-eng@company.com
6. **Output:** Incident report (see [Outputs](#outputs))

```json
{
  "incident_id": "INC-2026-07-26-001",
  "type": "HARDCODED_SECRET",
  "severity": "CRITICAL",
  "pattern": "stripe_key",
  "detected_at": "2026-07-26T14:32:18Z",
  "pr_number": 423,
  "commit": "abc1234567...",
  "action": "revoked",
  "remediation_time_seconds": 45,
  "escalated_to": ["security-eng@company.com", "#security-incidents"]
}
```

### Scenario 2: Vulnerable Dependency in PR

**Trigger:** PR #511 bumps `lodash` to 4.17.19 (CVE-2021-23337, CVSS 9.1)

**Flow:**
1. **Detect:** `npm audit` flags lodash 4.17.19 as CRITICAL
2. **Contain:** Comment on PR: "CVE-2021-23337 in lodash 4.17.19 (CVSS 9.1)"
3. **Recommend:** Suggest upgrade to 4.17.21+ (patched version)
4. **Block:** Set PR status to "error" until dependency resolved
5. **Escalate:** Slack team lead + assign Jira ticket (P1)
6. **Output:** Incident report with remediation steps

```json
{
  "incident_id": "INC-2026-07-26-002",
  "type": "VULNERABLE_DEPENDENCY",
  "severity": "CRITICAL",
  "package": "lodash",
  "current_version": "4.17.19",
  "vulnerable_cve": "CVE-2021-23337",
  "cvss_score": 9.1,
  "recommended_version": "4.17.21",
  "pr_number": 511,
  "action": "blocked",
  "escalated_to": ["@team-lead", "jira:PROJ-1234"]
}
```

### Scenario 3: Suspicious Commit Churn

**Trigger:** User `bot@legacy-system` pushes 12 commits to `main` in 6 minutes, each touching >60 files

**Flow:**
1. **Detect:** Anomaly in commit velocity + author reputation
2. **Contain:** Block push immediately (pre-receive hook)
3. **Investigate:** Check if account was compromised (IP, timestamp, auth logs)
4. **Escalate:** Slack #security-incidents + page on-call security engineer
5. **Action:** Force password reset for `bot@legacy-system`; review all commits in 24-hour window
6. **Output:** Incident report with timeline

```json
{
  "incident_id": "INC-2026-07-26-003",
  "type": "SUSPICIOUS_ACTIVITY",
  "severity": "HIGH",
  "anomaly": "high_commit_churn",
  "author": "bot@legacy-system",
  "timeframe": "2026-07-26T14:00:00Z to 2026-07-26T14:06:00Z",
  "commits": 12,
  "files_per_commit": 67,
  "branch": "main",
  "action": "push_blocked",
  "investigation": "account_compromise_suspected",
  "escalated_to": ["#security-incidents", "on-call-security"]
}
```

---

## Outputs

### Incident Report (JSON)

Stored in `s3://security-incidents-audit/incidents/{YYYY-MM-DD}/INC-{incident_id}.json` (encrypted at rest)

```json
{
  "incident_id": "INC-2026-07-26-001",
  "type": "HARDCODED_SECRET|VULNERABLE_DEPENDENCY|SUSPICIOUS_ACTIVITY",
  "severity": "CRITICAL|HIGH|MEDIUM",
  "status": "detected|contained|remediated|closed",
  "detected_at": "2026-07-26T14:32:18Z",
  "contained_at": "2026-07-26T14:32:45Z",
  "remediated_at": "2026-07-26T14:33:10Z",
  "closed_at": null,
  "repository": "github.com/company/repo",
  "branch": "feature/payment-integration",
  "commit": "abc123def456...",
  "pr_number": 423,
  "author": "dev@company.com",
  "pattern_matched": "stripe_key|aws_secret|cve_identifier",
  "details": {
    "secret_type": "stripe_live_key",
    "exposure_window_seconds": 342,
    "accessed_endpoints": ["GET /billing", "POST /charges"],
    "compromised_resources": ["prod-db", "stripe-account-id-12345"]
  },
  "remediation": {
    "action": "revoked",
    "old_secret": "sk_live_51abc...xyz",
    "new_secret": "sk_live_99xyz...abc",
    "token_rotated_at": "2026-07-26T14:33:10Z",
    "time_to_remediate_seconds": 38
  },
  "escalation": {
    "level": "CRITICAL",
    "notified": [
      "security-eng@company.com",
      "#security-incidents",
      "cto@company.com"
    ],
    "jira_ticket": "SEC-9876",
    "pagerduty_incident": "INC-5432"
  },
  "audit_trail": [
    {
      "timestamp": "2026-07-26T14:32:18Z",
      "action": "detection",
      "tool": "regex_entropy_scan",
      "result": "HARDCODED_SECRET_DETECTED"
    },
    {
      "timestamp": "2026-07-26T14:32:45Z",
      "action": "containment",
      "tool": "github_api",
      "result": "PR_COMMENTED"
    },
    {
      "timestamp": "2026-07-26T14:33:10Z",
      "action": "remediation",
      "tool": "stripe_api",
      "result": "TOKEN_REVOKED"
    }
  ]
}
```

### Remediation Status (Slack message)

```
🔴 CRITICAL INCIDENT: Stripe API Key Leaked in PR #423

Repository: company/payment-service
Branch: feature/payment-integration
Detected: 2026-07-26 14:32:18 UTC

🛡️ REMEDIATION TIMELINE:
[14:32:18] Detected: sk_live_51abc...xyz
[14:32:45] Contained: PR commented, CI blocked
[14:33:10] Revoked: Old token invalidated
[14:33:12] Issued: New token created (sk_live_99xyz...abc)

📊 EXPOSURE WINDOW: 342 seconds (5 min 42 sec)

✅ STATUS: REMEDIATED
  Jira: SEC-9876
  Follow-up: CTO notified, audit trail locked

Questions? DM @security-eng
```

### Audit Trail (immutable log)

Every incident action is logged to:
- **CloudWatch Logs:** `git-incident-response/audit/{YYYY-MM-DD}`
- **S3 (encrypted):** `s3://security-incidents-audit/incidents/{incident_id}.json`
- **Splunk:** Indexed under `sourcetype=git_security`

---

## Escalation Matrix

| Severity | Triggered By | Actions | Notified | SLA |
|----------|--------------|---------|----------|-----|
| **CRITICAL** | Hardcoded AWS key, private key, forced push to main | Immediate revoke + pipeline pause + page on-call | CTO, CISO, security-eng, #security-incidents | 5 min |
| **HIGH** | API key, DB password, CVSS ≥ 9.0 CVE, mass deletion | Contained + team lead notified + P1 Jira ticket | team-lead, #security-incidents, assignee | 1 hour |
| **MEDIUM** | High commit churn on non-main, CVSS 7–8 CVE | Logged + optional Slack notification | @author, log database | 24 hours |
| **LOW** | Informational alerts (e.g., deprecated dependency) | Logged only | — | — |

---

## Rate Limiting & Anti-Spam

To prevent alert fatigue and runaway remediation loops:

```
MAX 10 INCIDENTS / HOUR per repository
  • If threshold exceeded: Buffer additional incidents → digest email 1/hour
  • If same secret detected 3× in 24h: Escalate to "account compromise"
  • If false positives > 15% (weekly): Auto-tune regex thresholds
```

---

## Tools & Dependencies

| Tool | Purpose | Provider |
|------|---------|----------|
| `Bash grep + ripgrep` | Local secret pattern matching | OS |
| `GitHub search_code` | Commit history scanning | GitHub API |
| `npm audit / pip safety / cargo audit` | Dependency vulnerability scanning | Package managers |
| `Stripe API` / `AWS IAM` | Secret rotation & revocation | External APIs |
| `Slack MCP` | Incident notifications | Slack API |
| `Jira API` | Ticket creation | Jira |
| `PagerDuty API` | On-call escalation | PagerDuty |
| `AWS S3 + KMS` | Incident storage (encrypted) | AWS |
| `CloudWatch Logs / Splunk` | Audit trail | Observability |

---

## Invocation Examples

### Scan entire repository for secrets

```bash
/git-incident-response --scan-repo --repository github.com/company/api
```

**Output:**
```
Scanning repository: github.com/company/api
Found 3 incidents:
  [INC-2026-07-26-001] CRITICAL: AWS secret key in config/prod.env (commit abc123)
  [INC-2026-07-26-002] HIGH: Lodash 4.17.19 (CVE-2021-23337) in package.json
  [INC-2026-07-26-003] MEDIUM: High commit churn detected (12 commits/6 min)

Remediation initiated. Check S3 for incident reports.
```

### Monitor incoming PR for secrets

```bash
/git-incident-response --monitor-pr --pr-number 423 --repository github.com/company/payment
```

**Output:**
```
Monitoring PR #423 in github.com/company/payment
[14:32:18] Regex scan: HARDCODED_SECRET detected (stripe_key)
[14:32:45] Contained: PR commented, CI blocked
[14:33:10] Remediated: Token revoked + escalated to #security-incidents

Incident Report: INC-2026-07-26-001
Download: s3://security-incidents-audit/incidents/2026-07-26/INC-2026-07-26-001.json
```

### Check dependencies for CVEs

```bash
/git-incident-response --check-deps --repository github.com/company/frontend
```

**Output:**
```
Dependency Audit: github.com/company/frontend
Scanning: package.json, package-lock.json

CRITICAL (1):
  ✗ lodash 4.17.19 → CVE-2021-23337 (CVSS 9.1)
    Recommend: 4.17.21+
    Jira: SEC-9876 (P1)

HIGH (2):
  ✗ express 4.17.0 → CVE-2022-123456 (CVSS 8.2)
  ✗ axios 0.21.1 → CVE-2021-987654 (CVSS 7.5)

Jira tickets created for all CRITICAL + HIGH issues.
```

### Dry-run (no remediation)

```bash
/git-incident-response --scan-repo --dry-run --repository github.com/company/api
```

**Output:**
```
DRY-RUN MODE (no actions taken)
Scanning: github.com/company/api

Would detect:
  - 1 CRITICAL incident
  - 2 HIGH incidents
  - 1 MEDIUM incident

Would escalate to:
  - #security-incidents (Slack)
  - security-eng@company.com (email)
  - CTO (for CRITICAL items)

Use without --dry-run to execute remediation.
```

---

## Configuration & Customization

### File: `.claude/git-incident-response.config.json`

```json
{
  "detection": {
    "enabled_patterns": [
      "aws_access_key",
      "aws_secret_key",
      "github_token",
      "slack_token",
      "api_key_generic",
      "database_password",
      "jwt_token",
      "private_key",
      "stripe_key"
    ],
    "entropy_threshold": 4.0,
    "git_history_depth_days": 90
  },
  "remediation": {
    "auto_revoke_secrets": true,
    "pause_ci_on_critical": true,
    "create_jira_tickets": true
  },
  "escalation": {
    "critical_recipients": [
      "cto@company.com",
      "security-eng@company.com",
      "#security-incidents"
    ],
    "high_recipients": ["team-lead@company.com"],
    "medium_recipients": []
  },
  "rate_limit": {
    "max_incidents_per_hour": 10,
    "digest_mode_enabled": true
  },
  "storage": {
    "s3_bucket": "security-incidents-audit",
    "kms_key_id": "arn:aws:kms:us-east-1:123456789:key/abc123",
    "retention_days": 2555
  }
}
```

---

## FAQ & Troubleshooting

**Q: Can I whitelist false positives?**  
A: Yes. Add pattern + repository to `.claude/git-incident-response.whitelist.json`:
```json
{
  "whitelisted_patterns": [
    {
      "repository": "github.com/company/test-fixtures",
      "pattern": "aws_secret_key",
      "reason": "mock credentials for unit tests"
    }
  ]
}
```

**Q: What if my API key is accidentally leaked but never used?**  
A: The skill still revokes it (safe over sorry). Exposure window is logged; if no access detected, severity may be downgraded to HIGH.

**Q: How do I test this without real incidents?**  
A: Use `--dry-run` mode. Add a test secret to a feature branch, run the skill, and watch the detection without executing remediation.

**Q: What if remediation fails (e.g., Stripe API timeout)?**  
A: Incident status → "remediation_failed", escalated to on-call security. Retry logic: exponential backoff (max 3 attempts over 10 minutes).

---

## References

- [OWASP Secret Management](https://owasp.org/www-community/Sensitive_Data_Exposure)
- [CWE-798: Hardcoded Credentials](https://cwe.mitre.org/data/definitions/798.html)
- [PCI-DSS Requirement 2.4: Configure Services Securely](https://www.pcisecuritystandards.org/)
- [SOC 2 Trust Service Criteria: Security Incident Response](https://www.aicpa.org/interestareas/informationmanagement/sodp-security-audit)

---

**Last Updated:** 2026-07-26  
**Maintained By:** Security Engineering Team  
**License:** Internal Use Only
