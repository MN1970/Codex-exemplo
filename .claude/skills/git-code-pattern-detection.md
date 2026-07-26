# SKILL.md — git-code-pattern-detection

**Detect SQL injection, XSS, hardcoded secrets, deprecated APIs, TODOs across git repositories.**

Version: **1.0.0** | Tier: **Sonnet** | MCPs: **GitHub search_code + Bash grep** | Output: **JSON + HTML dashboard**

---

## Overview

Automated security and code-quality scanning skill that identifies anti-patterns across a git repository using:
- GitHub MCP `search_code` for distributed pattern matching
- Bash `grep` for local deep scans
- Regex library with 10+ detectors
- JSON findings export (file:line:pattern:severity:fix)
- Interactive HTML security dashboard with severity breakdown, trend charts, and remediation guidance

---

## Capability Matrix

| Pattern Class | Detection | Auto-fix | Dashboard |
|---|---|---|---|
| SQL injection | ✅ Dynamic queries, unescaped params | ⚠ Manual review | ✅ High-severity flag |
| XSS (DOM/innerHTML) | ✅ Unsafe HTML insertion | ⚠ Manual review | ✅ High-severity flag |
| Hardcoded secrets | ✅ API keys, passwords, tokens | ❌ Detect only | ✅ Critical flag + alert |
| Deprecated APIs | ✅ Older frameworks, removed methods | ✅ Version mapping | ✅ Medium-severity flag |
| TODOs / FIXMEs | ✅ Unresolved code comments | ❌ Detect only | ✅ Low-severity flag |
| Promise anti-patterns | ✅ Uncaught rejections, `await` missing | ⚠ Suggest pattern | ✅ Medium-severity flag |
| Command injection | ✅ `shell=True`, `eval()`, `exec()` | ⚠ Suggest subprocess | ✅ High-severity flag |
| Insecure random | ✅ `Math.random()`, `rand()`, `random.randint()` | ✅ Suggest crypto | ✅ Medium-severity flag |
| Path traversal | ✅ `os.path.join()` + user input | ⚠ Suggest pathlib | ✅ High-severity flag |
| Hardcoded IPs/URLs | ✅ Dev/staging endpoints in prod code | ⚠ Suggest env vars | ✅ Medium-severity flag |

---

## Pattern Library (v1.0)

### 1. SQL Injection — Dynamic Query Construction

**Pattern ID**: `SEC-001-SQL-INJECT`

```regex
# JavaScript/TypeScript
query\s*=\s*["`].*\$\{.*\}.*["`]
\.query\(["`]SELECT.*WHERE.*\$\{.*\}["`]

# Python
sql\s*=\s*f["`]SELECT.*WHERE.*{.*}["`]
cursor\.execute\(\s*f["`].*{.*}["`]

# PHP
\$query\s*=\s*["`]SELECT.*WHERE.*\$[a-zA-Z_]["`]
mysqli_query\(\s*\$conn,\s*["`].*\$[a-zA-Z_]
```

**Severity**: HIGH  
**Fix suggestion**: Use parameterized queries (prepared statements).  
**Example fix**:
```javascript
// Before (vulnerable)
const query = `SELECT * FROM users WHERE id = ${userId}`;

// After (safe)
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

---

### 2. XSS — Unsafe HTML Insertion

**Pattern ID**: `SEC-002-XSS-DOM`

```regex
# JavaScript/TypeScript
\.innerHTML\s*=\s*[variables]
\.outerHTML\s*=\s*[variables]
\$\(["`].*["`]\)\.html\([variables]\)
dangerouslySetInnerHTML=

# Handlebars/EJS
\{\{\{.*\}\}\}
<%=\s*[variables].*%>  (without -s)

# Vue.js
v-html=
\.html\(
```

**Severity**: HIGH  
**Fix suggestion**: Use text content properties or sanitize HTML libraries (DOMPurify).  
**Example fix**:
```javascript
// Before (vulnerable)
element.innerHTML = userInput;

// After (safe)
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

---

### 3. Hardcoded Secrets

**Pattern ID**: `SEC-003-SECRETS`

```regex
# API Keys
(api_key|apiKey|api-key)\s*[=:]\s*["`][a-zA-Z0-9]{20,}["`]
(secret|password|pwd)\s*[=:]\s*["`][^\s"]{8,}["`]

# AWS / GCP / Azure patterns
aws_access_key_id\s*[=:]\s*AKIA[A-Z0-9]{16}
mongodb\+srv://[a-zA-Z0-9]+:[a-zA-Z0-9]+@
Bearer\s+[A-Za-z0-9._-]{20,}

# Private keys
-----BEGIN\s+(RSA|EC|OPENSSH)\s+PRIVATE\s+KEY
-----BEGIN\s+PRIVATE\s+KEY
```

**Severity**: CRITICAL  
**Fix suggestion**: Move to environment variables or secrets manager (AWS Secrets Manager, HashiCorp Vault, GitHub Secrets).  
**Example fix**:
```javascript
// Before (vulnerable)
const API_KEY = "sk-1234567890abcdefghij";

// After (safe)
const API_KEY = process.env.API_KEY;
```

---

### 4. Deprecated APIs

**Pattern ID**: `SEC-004-DEPRECATED`

```regex
# Node.js
require\(\s*["`]crypto["`]\)  # vs crypto.webcrypto (v15.7+)
String\.prototype\.substr\(
Buffer\(["`].*["`],\s*["`]utf8["`]\)  # use Buffer.from()

# JavaScript (browser)
XMLHttpRequest  # vs fetch()
\.createTextNode\(
Array\.prototype\.length = 0  # use .splice()

# Python (common)
\.has_key\(
StringIO\.StringIO\(  # use io.StringIO()
collections\.Sequence  # use collections.abc.Sequence (py3.3+)

# jQuery (if still in use)
\$\.ajax\(  # deprecated in 3.6+, use fetch
\.live\(  # use .on() or .delegate()
```

**Severity**: MEDIUM  
**Fix suggestion**: Update to modern alternatives with version-specific guidance.  
**Example fix**:
```javascript
// Before (deprecated)
var xhr = new XMLHttpRequest();

// After (modern)
fetch('/api/data')
  .then(r => r.json())
  .then(data => console.log(data));
```

---

### 5. TODOs / FIXMEs

**Pattern ID**: `SEC-005-TODO`

```regex
//\s*(TODO|FIXME|BUG|HACK|XXX|KLUDGE)\s*[:]*\s*(.*)
#\s*(TODO|FIXME|BUG|HACK|XXX)\s*[:]*\s*(.*)
/\*\s*(TODO|FIXME|BUG)\s*(.*)?\*/
```

**Severity**: LOW  
**Fix suggestion**: Create GitHub issue and link in comment.  
**Comment format**:
```javascript
// TODO: Refactor auth logic — see GH-1234
// FIXME: Performance issue on large datasets (v2.1 backlog)
```

---

### 6. Promise Anti-patterns

**Pattern ID**: `SEC-006-PROMISE`

```regex
# Missing await
(async\s+function|=>\s*\{).*Promise\s+\(.*\)(?!\s*await)

# Uncaught rejections
\.catch\(\s*\)  # empty catch
Promise\.all\(.*\)(?!\s*\.catch)
\.then\(.*,.*\)(?=.*throw)  # error handler before rejection
```

**Severity**: MEDIUM  
**Fix suggestion**: Add `.catch()` or `try/catch` in async functions.  
**Example fix**:
```javascript
// Before (unsafe)
promise.then(data => doSomething(data));

// After (safe)
promise
  .then(data => doSomething(data))
  .catch(err => logger.error(err));
```

---

### 7. Command Injection

**Pattern ID**: `SEC-007-CMD-INJECT`

```regex
# Python
subprocess\.(call|run|Popen)\(["`].*\$\{.*\}.*["`],\s*shell\s*=\s*True
os\.system\(
eval\(
exec\(

# Node.js
require\(["`]child_process["`]\)\.exec\(["`].*\$\{.*\}["`]
shell\s*:\s*true

# PHP
shell_exec\(
passthru\(
system\(
exec\(
```

**Severity**: HIGH  
**Fix suggestion**: Use parameterized subprocess calls (list args, not shell strings).  
**Example fix**:
```python
# Before (vulnerable)
os.system(f"rm {user_file}")

# After (safe)
import subprocess
subprocess.run(['rm', user_file], check=True)
```

---

### 8. Insecure Random

**Pattern ID**: `SEC-008-INSECURE-RANDOM`

```regex
# JavaScript
Math\.random\(\)  # for security, use crypto.getRandomValues()

# Python
random\.randint\(
random\.choice\(
import random  (if used for security tokens)

# PHP
rand\(
mt_rand\(
```

**Severity**: MEDIUM  
**Fix suggestion**: Use cryptographic RNG (crypto.getRandomValues, secrets, os.urandom).  
**Example fix**:
```javascript
// Before (weak)
const token = Math.random().toString(36).substr(2);

// After (cryptographically secure)
import crypto from 'crypto';
const token = crypto.randomBytes(32).toString('hex');
```

---

### 9. Path Traversal

**Pattern ID**: `SEC-009-PATH-TRAVERSAL`

```regex
# Python
os\.path\.join\(["`].*["`],\s*[variable]\)  # unsanitized
open\(.*\+\s*[variable].*\)

# Node.js
path\.join\(__dirname,\s*[variable]\)  # risky if variable unvalidated
fs\.readFile\([variable],\s*\(err

# PHP
file_get_contents\(\s*\$[variable]
include\(\s*\$[variable]
```

**Severity**: HIGH  
**Fix suggestion**: Validate and sanitize path inputs; use pathlib.Path restrictions.  
**Example fix**:
```python
# Before (vulnerable)
file_path = os.path.join('/uploads', user_input)
with open(file_path) as f:
    data = f.read()

# After (safe)
from pathlib import Path
base = Path('/uploads')
requested = (base / user_input).resolve()
if not str(requested).startswith(str(base)):
    raise ValueError("Path traversal attempt")
with open(requested) as f:
    data = f.read()
```

---

### 10. Hardcoded IPs/URLs

**Pattern ID**: `SEC-010-HARDCODED-CONFIG`

```regex
# Dev/staging endpoints
https?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}
(localhost|127\.0\.0\.1|dev\.|staging\.|test\.).*:[0-9]{2,5}
(http|https)://.*\.example\.com

# Hardcoded service URLs in production code
const.*=\s*["`]http[s]?://[a-z]+\.[a-z]+\.com["`]
DATABASE_URL\s*=\s*postgres://.*:.*@.*:[0-9]+
```

**Severity**: MEDIUM  
**Fix suggestion**: Move to environment variables (.env, Secrets Manager).  
**Example fix**:
```javascript
// Before (hardcoded)
const API_URL = "https://api.dev.example.com";

// After (configurable)
const API_URL = process.env.API_URL || 'https://api.example.com';
```

---

## Invocation

### Via GitHub MCP

```bash
# Search entire repository for SQL injection patterns
gh search_code --repo owner/repo "query.*\$\{" --extension js --extension ts

# Combine with grep for local deep scans
gh search_code --repo owner/repo "dangerouslySetInnerHTML" --language jsx
```

### Via Bash Grep (Local Repo)

```bash
# Scan all JavaScript/TypeScript files
grep -rn "\.innerHTML\s*=" . --include="*.js" --include="*.ts" --include="*.jsx"

# Find hardcoded secrets
grep -rn "api[_-]?key\|password\|secret" . --include="*.json" --include="*.js" --include="*.env*"

# Locate TODOs
grep -rn "TODO\|FIXME" . --include="*.js" --include="*.py" --include="*.java"
```

---

## Output Formats

### JSON Findings Schema

```json
{
  "scan_id": "scan-20260726-a1b2c3",
  "timestamp": "2026-07-26T10:30:00Z",
  "repository": "owner/repo",
  "branch": "main",
  "findings": [
    {
      "id": "FND-001",
      "file": "src/api/users.js",
      "line": 42,
      "pattern_id": "SEC-001-SQL-INJECT",
      "pattern_name": "SQL Injection — Dynamic Query",
      "severity": "HIGH",
      "matched_text": "const query = `SELECT * FROM users WHERE id = ${userId}`;",
      "message": "Unescaped parameter in SQL query. Use parameterized queries.",
      "fix_suggestion": "Use prepared statements: db.query('SELECT * FROM users WHERE id = ?', [userId])",
      "tags": ["security", "sql", "injection"]
    },
    {
      "id": "FND-002",
      "file": "src/components/Profile.jsx",
      "line": 18,
      "pattern_id": "SEC-002-XSS-DOM",
      "pattern_name": "XSS — Unsafe HTML Insertion",
      "severity": "HIGH",
      "matched_text": "dangerouslySetInnerHTML={{ __html: userBio }}",
      "message": "User-controlled HTML insertion. Sanitize input.",
      "fix_suggestion": "Use DOMPurify: innerHTML = DOMPurify.sanitize(userBio)",
      "tags": ["security", "xss", "dom"]
    },
    {
      "id": "FND-003",
      "file": ".env.local",
      "line": 5,
      "pattern_id": "SEC-003-SECRETS",
      "pattern_name": "Hardcoded Secrets",
      "severity": "CRITICAL",
      "matched_text": "REACT_APP_API_KEY=sk_live_abc123def456",
      "message": "API key exposed in source. Rotate immediately.",
      "fix_suggestion": "Move to GitHub Secrets or environment variable manager; rotate key.",
      "tags": ["security", "secrets", "critical"]
    },
    {
      "id": "FND-004",
      "file": "src/utils/legacy.js",
      "line": 12,
      "pattern_id": "SEC-004-DEPRECATED",
      "pattern_name": "Deprecated API — XMLHttpRequest",
      "severity": "MEDIUM",
      "matched_text": "var xhr = new XMLHttpRequest();",
      "message": "XMLHttpRequest deprecated. Use fetch() or axios.",
      "fix_suggestion": "Replace with fetch: fetch(url).then(r => r.json())",
      "tags": ["deprecated", "modernization"]
    },
    {
      "id": "FND-005",
      "file": "src/auth/session.ts",
      "line": 87,
      "pattern_id": "SEC-005-TODO",
      "pattern_name": "Unresolved TODO",
      "severity": "LOW",
      "matched_text": "// TODO: Fix session timeout — see issue #1234",
      "message": "Unresolved TODO comment. Create/link GitHub issue.",
      "fix_suggestion": "Link to issue: // TODO(GH-1234): Fix session timeout",
      "tags": ["code-quality", "todo"]
    }
  ],
  "summary": {
    "total_findings": 5,
    "by_severity": {
      "CRITICAL": 1,
      "HIGH": 2,
      "MEDIUM": 1,
      "LOW": 1
    },
    "by_pattern": {
      "SEC-001-SQL-INJECT": 1,
      "SEC-002-XSS-DOM": 1,
      "SEC-003-SECRETS": 1,
      "SEC-004-DEPRECATED": 1,
      "SEC-005-TODO": 1
    },
    "files_scanned": 47,
    "patterns_run": 10
  }
}
```

### HTML Security Dashboard

**Features**:
- **Severity breakdown** (CRITICAL / HIGH / MEDIUM / LOW pie chart)
- **Pattern distribution** (bar chart by pattern type)
- **File hotspots** (files with most findings)
- **Trend** (findings over time if historical scans provided)
- **Actionable remediation** (one-click links to pattern library fixes)
- **Dark/light theme** support
- **Export CSV** button

**Generated at**: `findings-dashboard-{scan_id}.html`

Sample dashboard sections:
```
┌─────────────────────────────────────────────────────┐
│  Security Scan Results                              │
│  Scan ID: scan-20260726-a1b2c3                      │
│  Repository: owner/repo                             │
│  Date: 2026-07-26                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  CRITICAL    HIGH    MEDIUM    LOW                  │
│    [1]      [2]       [1]      [1]                 │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Pattern Distribution:                              │
│  ████████ SQL Injection (1)                        │
│  ████████ XSS (1)                                  │
│  ████████ Secrets (1)                              │
│  ████████ Deprecated (1)                           │
│  ████████ TODO (1)                                 │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Top Files:                                         │
│  1. src/api/users.js (1 finding)                   │
│  2. src/components/Profile.jsx (1 finding)         │
│  3. .env.local (1 finding)                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Integration with Manta Maestro

**Tier**: Sonnet (can be escalated to Opus for large repos 1000+ files)

**Routing in Maestro (Manta 00)**:

```
IF user asks "scan repository", "security audit", "find vulnerabilities"
   → git-code-pattern-detection (skill)
   OR escalate to Manta 15 (advisory) if broader security assessment needed
```

**Chains with**:
- **Manta 01 (Claims)**: If security finding is contractual liability
- **Manta 15 (Advisory)**: If findings suggest architectural changes
- **Manta 16 (Arquitecto-IA)**: If patterns suggest refactor/redesign

---

## Performance Notes

| Repo Size | Scan Time | Output |
|-----------|-----------|--------|
| Small (< 100 files) | 30s–1m | JSON + HTML |
| Medium (100–1000 files) | 2–5m | JSON + HTML |
| Large (1000+ files) | 10–30m | JSON + HTML (Opus tier) |

**Optimization**: Use GitHub search_code for distributed scanning + local grep for validation.

---

## Known Limitations

1. **False positives**: Comments, example code, strings with pattern substrings may trigger. Manual review recommended for MEDIUM/LOW.
2. **False negatives**: Encrypted secrets, obfuscated SQL, or domain-specific patterns may not detect. Use in combination with dedicated tools (git-secrets, TruffleHog).
3. **No auto-fix**: AUTO-FIX for HIGH/CRITICAL issues requires human approval; tool provides suggestions only.
4. **Language scope**: Primary support: JavaScript/TypeScript, Python, PHP, Java. Others via regex heuristics.

---

## Usage Examples

### Example 1: Security Audit

```
Scan repository 'anthropics/claude-code' for SQL injection and XSS patterns.
→ Runs patterns SEC-001, SEC-002
→ Outputs JSON with 3 HIGH findings
→ Generates dashboard with remediation links
```

### Example 2: Pre-commit Hook

```
Before pushing to main:
- Scan staged files for SEC-003-SECRETS and SEC-007-CMD-INJECT
- Block commit if CRITICAL findings
- Warn if HIGH findings detected
```

### Example 3: Continuous Scanning

```
Weekly scan (Monday 9am UTC):
- Full repository scan with all 10 patterns
- Compare against baseline from previous week
- Generate trend report and alert on new CRITICAL/HIGH
```

---

## Changelog

- **v1.0.0** (2026-07-26) — Initial release. 10 patterns: SQL, XSS, secrets, deprecated, TODO, promises, command injection, insecure random, path traversal, hardcoded config. GitHub MCP + Bash grep integration. JSON + HTML outputs.

---

## Support & Escalation

- **Minor questions**: Consult pattern library above
- **False positives**: Create issue with matched text and context
- **New patterns**: Submit PR to pattern library with regex + test cases
- **Escalation**: Contact Manta 16 (Arquitecto-IA) for custom pattern development

**Maintainer**: Manta Maestro (Advisory, Manta 15)  
**Repository**: `Codex-exemplo/.claude/skills/`  
**Last updated**: 2026-07-26
