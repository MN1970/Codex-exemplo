# SKILL.md — git-code-pattern-detection

**Detect SQL injection, XSS, hardcoded secrets, deprecated APIs, TODOs across git repositories. Fase 1 MVP (10 OWASP) → Fase 2 (50+ CWE + AST + Semgrep + ML filtering).**

Version: **2.0.0** | Tier: **Sonnet/Opus** | MCPs: **GitHub search_code + Bash grep + Semgrep CLI** | Output: **JSON + HTML dashboard + Remediation playbook**

---

## Overview

Automated security and code-quality scanning skill that identifies anti-patterns across a git repository using:
- GitHub MCP `search_code` for distributed pattern matching
- Bash `grep` for local deep scans
- Regex library with 10+ detectors
- JSON findings export (file:line:pattern:severity:fix)
- Interactive HTML security dashboard with severity breakdown, trend charts, and remediation guidance

---

## Fase 1 → Fase 2 Evolution

**Fase 1 (MVP)**: 10 OWASP patterns, GitHub + Bash scanning, JSON + HTML dashboard  
**Fase 2 (Current)**: 50+ CWE Top 25 patterns, AST analysis, Semgrep SAST integration, ML-based severity filtering, detailed remediation playbooks for Python/JavaScript/Go

### What's New in Fase 2

| Feature | Fase 1 | Fase 2 | Status |
|---------|--------|--------|--------|
| Pattern count | 10 OWASP | 50+ CWE Top 25 | ✅ Implemented |
| Code analysis | Regex matching | Regex + AST semantic analysis | ✅ Implemented |
| SAST tool | None | Semgrep integration | ✅ Implemented |
| False positive reduction | Manual review | ML-based severity filter | ✅ Implemented |
| Remediation guidance | Suggestion snippets | Full playbooks + fixes | ✅ Implemented |
| Language support | JS/TS/Python/PHP | Python/JavaScript/Go/Java + others | ✅ Implemented |
| Configuration as code | Manual patterns | Semgrep YAML configs | ✅ Implemented |
| Severity prediction | Fixed labels | ML confidence scoring | ✅ Implemented |

---

## Capability Matrix (Fase 2: 50+ Patterns)

**Fase 1 Core (10 patterns)**:

| Pattern Class | Detection | Auto-fix | Dashboard | CWE |
|---|---|---|---|---|
| SQL injection | ✅ Dynamic queries, unescaped params | ⚠ Manual review | ✅ Critical | CWE-89 |
| XSS (DOM/innerHTML) | ✅ Unsafe HTML insertion | ⚠ Manual review | ✅ Critical | CWE-79 |
| Hardcoded secrets | ✅ API keys, passwords, tokens | ❌ Detect only | ✅ Critical | CWE-798 |
| Deprecated APIs | ✅ Older frameworks, removed methods | ✅ Version mapping | ✅ Medium | CWE-1104 |
| TODOs / FIXMEs | ✅ Unresolved code comments | ❌ Detect only | ✅ Low | N/A |
| Promise anti-patterns | ✅ Uncaught rejections, `await` missing | ⚠ Suggest pattern | ✅ Medium | CWE-391 |
| Command injection | ✅ `shell=True`, `eval()`, `exec()` | ⚠ Suggest subprocess | ✅ Critical | CWE-78 |
| Insecure random | ✅ `Math.random()`, `rand()`, `random.randint()` | ✅ Suggest crypto | ✅ Medium | CWE-338 |
| Path traversal | ✅ `os.path.join()` + user input | ⚠ Suggest pathlib | ✅ High | CWE-22 |
| Hardcoded IPs/URLs | ✅ Dev/staging endpoints in prod code | ⚠ Suggest env vars | ✅ Medium | CWE-798 |

**Fase 2 Additions (40+ new CWE patterns)**:

| CWE | Pattern Class | Detection | Severity | Languages |
|---|---|---|---|---|
| CWE-352 | CSRF (Cross-Site Request Forgery) | ✅ Missing CSRF tokens | HIGH | JS, Python, Java |
| CWE-434 | Unrestricted file upload | ✅ No file type validation | HIGH | PHP, Python, JS |
| CWE-943 | Improper neutralization | ✅ Unvalidated input in context | HIGH | Python, JS, Go |
| CWE-20 | Improper input validation | ✅ Missing input bounds checks | HIGH | All |
| CWE-200 | Exposure of sensitive information | ✅ Logs containing secrets | HIGH | All |
| CWE-203 | Observable discrepancy | ✅ Timing attacks in auth | MEDIUM | Python, Go, Java |
| CWE-208 | Observable timing discrepancy | ✅ Constant-time comparison | MEDIUM | Go, Python, C |
| CWE-215 | Information exposure in debug data | ✅ Debug mode in production | HIGH | All |
| CWE-248 | Uncaught exception handler | ✅ Empty catch blocks | MEDIUM | Java, C#, Python |
| CWE-250 | Execution with unnecessary privilege | ✅ setuid/sudo patterns | MEDIUM | C, Go, Bash |
| CWE-276 | Incorrect default permissions | ✅ File/dir permissions | MEDIUM | Python, Go, Bash |
| CWE-287 | Improper authentication | ✅ Missing auth checks | CRITICAL | All |
| CWE-295 | Improper certificate validation | ✅ SSL/TLS bypass | CRITICAL | Python, Go, Java |
| CWE-306 | Missing authentication for critical function | ✅ Unprotected API endpoints | CRITICAL | All |
| CWE-307 | Improper restriction of rendered UI layers | ✅ Clickjacking vectors | HIGH | JS, HTML |
| CWE-311 | Missing encryption | ✅ Plaintext data transmission | CRITICAL | All |
| CWE-312 | Cleartext storage of sensitive information | ✅ Unencrypted database fields | CRITICAL | All |
| CWE-327 | Use of broken/risky cryptographic algorithm | ✅ MD5, DES, RC4 usage | CRITICAL | All |
| CWE-328 | Reversible one-way hash | ✅ Base64 encoding as "encryption" | HIGH | Python, JS |
| CWE-330 | Use of insufficiently random values | ✅ Weak RNG for tokens | HIGH | All |
| CWE-338 | Use of cryptographically weak PRNG | ✅ Math.random() for security | MEDIUM | JS, Python |
| CWE-340 | Generation of predictable numbers/identifiers | ✅ Sequential IDs, predictable UUIDs | MEDIUM | All |
| CWE-345 | Insufficient verification of data authenticity | ✅ Missing MAC/signature validation | HIGH | All |
| CWE-346 | Origin validation error | ✅ Missing origin checks in headers | MEDIUM | JS, Python |
| CWE-347 | Improper verification of cryptographic signature | ✅ Missing signature verification | CRITICAL | Python, Go, Java |
| CWE-350 | Reliance on reverse DNS resolution | ✅ Hostname-based auth | MEDIUM | All |
| CWE-352 | CSRF | ✅ No CSRF token validation | HIGH | All |
| CWE-359 | Exposure of private personal information to an unauthorized actor | ✅ PII in logs/responses | CRITICAL | All |
| CWE-366 | Race condition in check-use-of-file | ✅ TOCTOU vulnerability | MEDIUM | Python, Go, C |
| CWE-367 | Time-of-check time-of-use race condition | ✅ TOCTOU in auth | HIGH | All |
| CWE-377 | Insecure temporary file | ✅ `/tmp` with predictable name | HIGH | Python, Go, C, Bash |
| CWE-379 | Creation of temporary file in directory with insecure permissions | ✅ World-readable temp files | HIGH | All |
| CWE-400 | Uncontrolled resource consumption | ✅ No rate limiting/resource bounds | MEDIUM | All |
| CWE-401 | Missing release of memory after effective lifetime | ✅ Memory leak patterns | MEDIUM | C, Go, Java |
| CWE-404 | Improper resource validation | ✅ No resource size checks | MEDIUM | All |
| CWE-406 | Insufficient log data | ✅ Missing audit logs | MEDIUM | All |
| CWE-427 | Uncontrolled search path element | ✅ Unsafe library loading | HIGH | Python, C, Go |
| CWE-434 | Unrestricted upload of dangerous file type | ✅ No file type validation | HIGH | All |
| CWE-440 | Expected behavior violation | ✅ Documented behavior not met | LOW | All |
| CWE-476 | Null pointer dereference | ✅ Missing null checks | MEDIUM | Java, C, Go |
| CWE-502 | Deserialization of untrusted data | ✅ Unsafe pickle/JSON parsing | CRITICAL | Python, Java, JavaScript |
| CWE-598 | Use of GET request with sensitive query strings | ✅ Sensitive params in query string | HIGH | All |
| CWE-601 | URL redirection to untrusted site | ✅ Open redirect vulnerability | MEDIUM | All |
| CWE-611 | Improper restriction of XML external entity reference | ✅ XXE vulnerability | CRITICAL | Java, Python, Go |
| CWE-614 | Sensitive cookie without secure flag | ✅ Missing HttpOnly/Secure flags | HIGH | All |
| CWE-620 | Unverified password change | ✅ No email verification for password reset | HIGH | All |
| CWE-640 | Weak password recovery mechanism | ✅ Predictable recovery tokens | HIGH | All |
| CWE-656 | Reliance on security through obscurity | ✅ Hardcoded "secret" values | MEDIUM | All |
| CWE-662 | Improper synchronization | ✅ Race conditions in shared state | MEDIUM | Python, Go, Java, C |
| CWE-706 | Use of incorrectly-resolved name | ✅ Namespace collision | MEDIUM | Python, Go |
| CWE-776 | Improper restriction of recursive entity references in DTDs | ✅ Billion laughs/DTD bomb | HIGH | Java, Python |
| CWE-943 | Improper neutralization of special elements in data query logic | ✅ LDAP injection, NoSQL injection | HIGH | All |

---

## Fase 2: AST Analysis & Semantic Code Analysis

**Abstract Syntax Tree (AST) Analysis** moves beyond regex pattern matching to understand code semantics and control flow. This enables detection of logic-level vulnerabilities, not just string patterns.

### AST Analysis Features

| Feature | What it detects | Example |
|---------|-----------------|---------|
| **Data flow tracking** | User input → dangerous sink (e.g., SQL query, file path) | `user_input = request.args['id']` → `db.query(f"SELECT * WHERE id={user_input}")` |
| **Control flow analysis** | Unreachable code, missing validation branches | Code after `return` statement; missing error handlers in all paths |
| **Type inference** | Variable type mismatches, type confusion | String passed to function expecting int; type coercion in comparisons |
| **Call graph analysis** | Function call chains leading to vulnerability | `process_user_input()` → `validate_email()` → but no SQL escaping before `execute_query()` |
| **Constant propagation** | Hardcoded secrets, sensitive values in vars | `API_KEY="sk_live_1234"` detected as constant, flagged even if assigned to var |
| **Taint tracking** | How untrusted data flows through program | Request params → stored in session → rendered in HTML (XSS chain) |

### Implementation via Semgrep

**Semgrep** is a fast SAST (Static Application Security Testing) tool that uses pattern-based rules written in YAML for semantic analysis:

```yaml
# Example: SQL injection via Semgrep rule
rules:
  - id: sql-injection-f-string
    patterns:
      - pattern-either:
          - patterns:
              - pattern: |
                  $QUERY = f"...{$VAR}..."
                  $DB.execute($QUERY)
              - pattern-not: |
                  $QUERY = f"...{$VAR!r}..."  # repr() escapes
              - pattern-not: |
                  $QUERY = "SELECT ... WHERE id = ?"
                  $DB.execute($QUERY, [$VAR])
    message: "Potential SQL injection: Use parameterized queries"
    severity: HIGH
    languages: [python]
```

### AST Example: Data Flow Detection

**Python Code**:
```python
# File: app.py, Line 42
@app.route('/search')
def search():
    user_input = request.args.get('query')  # UNTRUSTED SOURCE
    
    # Missing validation here!
    
    db_query = f"SELECT * FROM products WHERE name LIKE '%{user_input}%'"  # SINK
    results = db.execute(db_query)
    
    return render_template('results.html', data=results)  # XSS SINK
```

**AST Taint Analysis**:
```
user_input (source: request.args) 
  ↓ (no sanitization)
db_query (contains untrusted data)
  ↓ (flows to SQL execute)
CRITICAL: SQL injection @ line 48
```

**Detection Output**:
```json
{
  "finding_id": "FND-ast-001",
  "type": "SQL_INJECTION_VIA_TAINT",
  "severity": "CRITICAL",
  "source": "request.args.get('query')",
  "sink": "db.execute(db_query)",
  "taint_chain": [
    {"line": 42, "type": "source", "description": "user input from request"},
    {"line": 47, "type": "no_validation", "description": "no sanitization applied"},
    {"line": 48, "type": "sink", "description": "flows to SQL execute"}
  ],
  "fix": "Use parameterized query: db.execute('SELECT ... WHERE name LIKE ?', [f'%{user_input}%'])"
}
```

### AST Detection Rules (Built into Semgrep rules)

1. **Taint-based SQL injection**: Track request params → SQL execute
2. **Taint-based XSS**: Track request params → HTML render without escaping
3. **Authentication bypass**: Detect missing auth checks on critical endpoints
4. **Deserialization attacks**: Track untrusted data → pickle.loads() / JSON.parse()
5. **Path traversal chains**: Track user input → file operations without normalization
6. **Cryptographic misuse**: Track crypto function calls with weak algorithms
7. **Missing null checks**: Detect dereferences without null validation
8. **Race conditions**: Detect check-then-use patterns on shared resources

---

## Semgrep SAST Integration

### Installation & Setup

```bash
# Install Semgrep (via package manager or pip)
pip install semgrep
# or: brew install semgrep (macOS)
# or: https://semgrep.dev/docs/getting-started/

# Verify installation
semgrep --version
# Output: semgrep 1.50.0
```

### Semgrep Rulesets

**Official Manta Rulesets** (stored in Supabase or GitHub):

1. **p/owasp-top-ten** (built-in): Maps to CWE Top 25
2. **p/security-audit** (custom): Manta-specific rules for infrastructure projects
3. **p/cwe-top-25** (built-in): All CWE Top 25 patterns
4. **p/python-security** (built-in): Python-specific rules
5. **p/javascript-security** (built-in): JavaScript/TypeScript rules
6. **p/golang-security** (built-in): Go-specific rules

### Semgrep CLI Usage

```bash
# Scan a single file
semgrep -c p/owasp-top-ten src/app.py

# Scan entire directory
semgrep -c p/security-audit . --json > findings.json

# Scan with multiple rulesets
semgrep -c p/cwe-top-25 -c p/python-security . --json

# Target specific language
semgrep --include="*.py" -c p/python-security .

# Exclude test directories
semgrep -c p/security-audit . --exclude="tests,node_modules"

# Output in different formats
semgrep . --json              # JSON for parsing
semgrep . --sarif             # SARIF for GitHub Advanced Security
semgrep . --csv               # CSV for spreadsheets
semgrep . --text              # Human-readable text
```

### Sample Semgrep Rules (YAML format)

**Rule 1: SQL Injection (Python f-strings)**
```yaml
rules:
  - id: cwe-89-sql-inject-fstring-python
    pattern-either:
      - patterns:
          - pattern: |
              $QUERY = f"...{...}..."
              $DB_OBJ.$METHOD($QUERY, ...)
          - metavariable-regex:
              metavariable: $DB_OBJ
              regex: (db|database|conn|cursor)
          - metavariable-regex:
              metavariable: $METHOD
              regex: (execute|query|run)
    message: SQL injection via f-string. Use parameterized queries.
    severity: CRITICAL
    languages: [python]
```

**Rule 2: Hardcoded API Keys**
```yaml
rules:
  - id: cwe-798-hardcoded-api-keys
    patterns:
      - pattern-either:
          - pattern: |
              api_key = "sk_live_..."
          - pattern: |
              API_KEY = "...{20,}..."
          - pattern-regex: |
              (api_?key|secret|password)\s*=\s*["`][A-Za-z0-9_]{20,}["`]
    message: Hardcoded API key detected. Use environment variables.
    severity: CRITICAL
    languages: [python, javascript, java]
```

**Rule 3: Unsafe deserialization (Python pickle)**
```yaml
rules:
  - id: cwe-502-unsafe-pickle
    patterns:
      - pattern-either:
          - pattern: pickle.loads(...)
          - pattern: pickle.load(...)
    pattern-not: |
      pickle.loads(BASE64_ENCODED_CONSTANT)
    message: Unsafe deserialization with pickle. Attacker can execute arbitrary code.
    severity: CRITICAL
    languages: [python]
```

**Rule 4: Missing CSRF token validation**
```yaml
rules:
  - id: cwe-352-missing-csrf-token
    patterns:
      - pattern-either:
          - patterns:
              - pattern: |
                  @app.route($ROUTE, methods=["POST"])
                  def $FUNC(...):
              - pattern-not: |
                  csrf_token.validate()
              - pattern-not: |
                  @csrf.protect
              - pattern-not: |
                  check_csrf_token($...)
    message: Missing CSRF token validation on POST endpoint.
    severity: HIGH
    languages: [python, javascript]
```

---

## Pattern Library (v2.0 — 50+ CWE patterns)

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

## New Fase 2 Patterns (Expanded)

### 11. CSRF — Cross-Site Request Forgery

**Pattern ID**: `CWE-352-CSRF`

```regex
# Missing CSRF token validation in POST/PUT/DELETE endpoints
@(app|router)\.(post|put|delete)\(
  (?!.*csrf|.*token|.*verify)
  
# CSRF token not validated before state change
def (update|delete|create)\s*\(.*request.*\):
  (?!.*csrf_token\.validate|.*check_csrf)

# Missing SameSite cookie attribute
Set-Cookie:.*(?!.*SameSite)
```

**Severity**: HIGH  
**Examples**:

**Python (Flask) - Vulnerable**:
```python
@app.route('/transfer', methods=['POST'])
def transfer_funds():
    amount = request.form.get('amount')
    to_account = request.form.get('to')
    # No CSRF token check!
    db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", 
               [amount, current_user.id])
    return "Transfer successful"
```

**Python (Flask) - Fixed**:
```python
from flask_wtf.csrf import csrf_protect

@app.route('/transfer', methods=['POST'])
@csrf_protect  # Validate CSRF token automatically
def transfer_funds():
    amount = request.form.get('amount')
    to_account = request.form.get('to')
    db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", 
               [amount, current_user.id])
    return "Transfer successful"
```

**JavaScript (Express) - Vulnerable**:
```javascript
app.post('/api/transfer', (req, res) => {
  const { amount, toAccount } = req.body;
  // No CSRF token validation
  db.query('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', 
           [amount, req.user.id]);
  res.json({ success: true });
});
```

**JavaScript (Express) - Fixed**:
```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

app.use(cookieParser());
app.use(csrf({ cookie: true }));

app.post('/api/transfer', (req, res) => {
  const { amount, toAccount } = req.body;
  // CSRF token automatically validated by middleware
  db.query('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', 
           [amount, req.user.id]);
  res.json({ success: true });
});
```

**Go - Vulnerable**:
```go
http.HandleFunc("/api/transfer", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != "POST" {
        return
    }
    amount := r.PostFormValue("amount")
    // No CSRF token check
    db.Exec("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", 
            amount, userID)
})
```

**Go - Fixed**:
```go
import "github.com/gorilla/csrf"

http.HandleFunc("/api/transfer", csrf.Protect([]byte("32-byte-key"))(
    http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.Method != "POST" {
            return
        }
        amount := r.PostFormValue("amount")
        // CSRF middleware validates token
        db.Exec("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", 
                amount, userID)
    })))
```

---

### 12. Unrestricted File Upload

**Pattern ID**: `CWE-434-UNRESTRICTED-UPLOAD`

```regex
# No file type validation
request\.files\[.*\]
multer\(\)
@app\.route.*upload.*methods.*POST

# Missing MIME type check
filename = .*\.filename
(?!.*\.split\(.*\)\[-1\].*in.*|.*mimetype.*|.*magic\.from_buffer)

# No file size limit
FileField\(
(?!.*FileAllowed|.*FileSize)
```

**Severity**: HIGH  
**Examples**:

**Python (Flask) - Vulnerable**:
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # No validation! User can upload .exe, .php, etc.
    file.save(os.path.join('uploads', file.filename))
    return "File uploaded"
```

**Python (Flask) - Fixed**:
```python
from werkzeug.utils import secure_filename
import magic

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'png', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    # Validate file extension
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return "Invalid file type", 400
    
    # Validate MIME type (magic bytes)
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime not in ['application/pdf', 'image/jpeg', 'image/png']:
        return "Invalid MIME type", 400
    
    # Validate file size
    file.seek(0, 2)
    if file.tell() > MAX_FILE_SIZE:
        return "File too large", 400
    file.seek(0)
    
    # Use secure filename
    filename = secure_filename(file.filename)
    file.save(os.path.join('uploads', filename))
    return "File uploaded successfully"
```

**JavaScript (Express) - Vulnerable**:
```javascript
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

app.post('/upload', upload.single('file'), (req, res) => {
  // No validation! User can upload anything
  res.json({ success: true, filename: req.file.filename });
});
```

**JavaScript (Express) - Fixed**:
```javascript
const multer = require('multer');
const FileType = require('file-type');
const fs = require('fs').promises;

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
const MAX_SIZE = 10 * 1024 * 1024;  // 10 MB

const upload = multer({
  dest: 'uploads/',
  fileFilter: async (req, file, cb) => {
    // Validate MIME type and extension
    const type = await FileType.fromBuffer(file.buffer);
    if (!ALLOWED_TYPES.includes(type?.mime || '')) {
      return cb(new Error('Invalid file type'));
    }
    cb(null, true);
  },
  limits: { fileSize: MAX_SIZE }
});

app.post('/upload', upload.single('file'), async (req, res) => {
  // Additional validation
  const ext = req.file.filename.split('.').pop().toLowerCase();
  if (!['jpg', 'png', 'pdf'].includes(ext)) {
    await fs.unlink(req.file.path);
    return res.status(400).json({ error: 'Invalid file type' });
  }
  res.json({ success: true, filename: req.file.filename });
});
```

**Go - Vulnerable**:
```go
http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
    file, handler, _ := r.FormFile("upload")
    defer file.Close()
    // No validation!
    dst, _ := os.Create(filepath.Join("uploads", handler.Filename))
    io.Copy(dst, file)
    defer dst.Close()
})
```

**Go - Fixed**:
```go
import (
    "io"
    "os"
    "path/filepath"
    "net/http"
)

const MAX_SIZE = 10 * 1024 * 1024  // 10 MB

var allowedExts = map[string]bool{
    ".jpg": true, ".jpeg": true, ".png": true, ".pdf": true,
}

http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
    file, handler, err := r.FormFile("upload")
    if err != nil {
        http.Error(w, "Upload error", http.StatusBadRequest)
        return
    }
    defer file.Close()
    
    // Validate file size
    if handler.Size > MAX_SIZE {
        http.Error(w, "File too large", http.StatusBadRequest)
        return
    }
    
    // Validate extension
    ext := filepath.Ext(handler.Filename)
    if !allowedExts[ext] {
        http.Error(w, "Invalid file type", http.StatusBadRequest)
        return
    }
    
    // Use secure filename (prevent directory traversal)
    safeFilename := filepath.Base(handler.Filename)
    dst, _ := os.Create(filepath.Join("uploads", safeFilename))
    io.Copy(dst, file)
    defer dst.Close()
    
    w.Header().Set("Content-Type", "application/json")
    fmt.Fprintf(w, `{"success": true}`)
})
```

---

### 13. XXE (XML External Entity) Injection

**Pattern ID**: `CWE-611-XXE`

```regex
# XML parsing without XXE protection
xml\.etree\.ElementTree\.parse\(
lxml\.etree\.parse\(
xml\.dom\.minidom\.parse\(
XMLParser\(
Document\.parseString\(
(?!.*DTD_FORBIDDEN|.*resolve_entities.*False|.*feature_external_ges.*False)
```

**Severity**: CRITICAL  
**Examples**:

**Python - Vulnerable**:
```python
import xml.etree.ElementTree as ET

def parse_xml(data):
    # Vulnerable: XXE attack possible
    tree = ET.fromstring(data)
    return tree
```

**Python - Fixed**:
```python
import xml.etree.ElementTree as ET

def parse_xml(data):
    # Disable external entities
    parser = ET.XMLParser()
    parser.resolve_entities = False
    tree = ET.fromstring(data, parser=parser)
    return tree

# Or use defusedxml (recommended)
from defusedxml import ElementTree as DefusedET

def parse_xml_safe(data):
    tree = DefusedET.fromstring(data)
    return tree
```

**JavaScript - Vulnerable**:
```javascript
const xml2js = require('xml2js');

let parser = new xml2js.Parser();
parser.parseString(userXml, (err, result) => {
  // Vulnerable: XXE possible
  console.log(result);
});
```

**JavaScript - Fixed**:
```javascript
const xml2js = require('xml2js');

let parser = new xml2js.Parser({
  strict: true,
  normalizeTags: true,
  // Disable external entity resolution
  doctype: null,
  DTD: null
});

parser.parseString(userXml, (err, result) => {
  console.log(result);
});
```

**Go - Vulnerable**:
```go
import "encoding/xml"

func parseXML(data string) {
    var doc interface{}
    xml.Unmarshal([]byte(data), &doc)  // XXE vulnerable
}
```

**Go - Fixed**:
```go
import (
    "encoding/xml"
    "strings"
)

func parseXML(data string) {
    decoder := xml.NewDecoder(strings.NewReader(data))
    decoder.Strict = true
    decoder.Entity = xml.HTMLEntity  // Only allow HTML entities
    
    var doc interface{}
    decoder.Decode(&doc)
}
```

---

### 14. Insecure Deserialization

**Pattern ID**: `CWE-502-UNSAFE-DESERIALIZATION`

```regex
# Python pickle (unsafe)
pickle\.loads\(.*\)
pickle\.load\(.*\)

# Java deserialization
ObjectInputStream\(
readObject\(\)

# JavaScript eval/Function
eval\(.*\)
Function\(.*\)
JSON\.parse.*untrusted
```

**Severity**: CRITICAL  
**Examples**:

**Python - Vulnerable**:
```python
import pickle

def load_user_session(data):
    # CRITICAL: Attacker can execute arbitrary code
    user_obj = pickle.loads(base64.b64decode(data))
    return user_obj
```

**Python - Fixed**:
```python
import json

def load_user_session(data):
    # Use JSON instead of pickle for untrusted data
    user_obj = json.loads(base64.b64decode(data))
    # Validate fields
    if not isinstance(user_obj.get('user_id'), int):
        raise ValueError("Invalid user_id")
    return user_obj
```

**JavaScript - Vulnerable**:
```javascript
// CRITICAL: eval() executes arbitrary code
const userData = eval(`(${receivedData})`);

// Also vulnerable: Function constructor
const fn = new Function('return ' + receivedData)();
```

**JavaScript - Fixed**:
```javascript
// Safe: JSON.parse only parses JSON
const userData = JSON.parse(receivedData);

// Validate structure
if (!userData.user_id || typeof userData.user_id !== 'number') {
    throw new Error('Invalid user_id');
}
```

**Go - Vulnerable**:
```go
import "encoding/gob"

func loadData(encodedData string) {
    decoder := gob.NewDecoder(strings.NewReader(encodedData))
    var data interface{}
    decoder.Decode(&data)  // gob can be exploited
}
```

**Go - Fixed**:
```go
import "encoding/json"

func loadData(encodedData string) {
    // Use JSON with strict types
    var data struct {
        UserID int    `json:"user_id"`
        Name   string `json:"name"`
    }
    json.Unmarshal([]byte(encodedData), &data)
    
    // Validate fields
    if data.UserID < 1 {
        return fmt.Errorf("invalid user_id")
    }
}
```

---

## ML-Based Severity Filtering (Fase 2 Innovation)

### Purpose

Reduce false positives by analyzing context and severity confidence. A regex match might be:
- **True positive**: Real vulnerability in exploitable code path
- **False positive**: Comment, test code, example, sanitized input

### ML Model Features

| Feature | Weight | Example |
|---------|--------|---------|
| **Pattern type** | 30% | SQL injection pattern is inherently high-risk |
| **Context analysis** | 25% | Is input validated before sink? Is code in test file? |
| **Exploitability** | 20% | Can attacker reach this code path? Is it reachable from network? |
| **Data flow** | 15% | Is untrusted data actually flowing to sink? |
| **Remediation history** | 10% | Has this been fixed before? How long unpatched? |

### Confidence Scoring

```
ML_CONFIDENCE = (pattern_weight × 0.30) + 
                (context_score × 0.25) + 
                (exploitability_score × 0.20) + 
                (dataflow_score × 0.15) +
                (remediation_score × 0.10)

If ML_CONFIDENCE < 0.4: Mark as LOW confidence (likely false positive)
If ML_CONFIDENCE 0.4–0.7: Mark as MEDIUM confidence (manual review recommended)
If ML_CONFIDENCE > 0.7: Mark as HIGH confidence (high-confidence finding)
```

### Example: False Positive Filtering

**Scenario 1: Real Vulnerability**
```python
# File: src/app.py (not in tests/)
user_id = request.args.get('id')
# No validation
db.query(f"SELECT * FROM users WHERE id={user_id}")  

ML Analysis:
- Pattern: SQL injection ✅ HIGH_WEIGHT
- Context: Production code (not test/example) ✅ HIGH
- Exploitability: Network reachable (route handler) ✅ HIGH
- Data flow: Untrusted input → SQL sink ✅ HIGH
→ ML_CONFIDENCE = 0.92 → CRITICAL (true positive)
```

**Scenario 2: False Positive (Comment)**
```python
# File: src/docs.py
"""
Example of VULNERABLE CODE (DO NOT USE):
db.query(f"SELECT * FROM users WHERE id={user_id}")
This is bad because...
"""

ML Analysis:
- Pattern: SQL injection ✅ HIGH_WEIGHT
- Context: Documentation/comment string ❌ LOW
- Exploitability: Inside docstring, not executed ❌ LOW
- Data flow: No actual data flow (string literal) ❌ LOW
→ ML_CONFIDENCE = 0.15 → FALSE POSITIVE (low confidence)
```

**Scenario 3: Mitigated (Parameterized Query)**
```python
user_id = request.args.get('id')
# Already using parameterized query!
db.query("SELECT * FROM users WHERE id=?", [user_id])

ML Analysis:
- Pattern: SQL injection detected ✅ HIGH_WEIGHT
- Context: But query is parameterized ✅ MEDIUM (mitigated)
- Exploitability: Input is parameter, not string ❌ LOW
- Data flow: Taint is neutralized by parameterization ✅ HIGH
→ ML_CONFIDENCE = 0.35 → LOW CONFIDENCE (mitigated, suppress)
```

### Output with ML Confidence Scores

```json
{
  "finding_id": "FND-042",
  "file": "src/api/users.py",
  "line": 45,
  "pattern": "CWE-89-SQL-INJECT",
  "matched_text": "db.query(f\"SELECT * FROM users WHERE id={user_id}\")",
  "base_severity": "CRITICAL",
  "ml_confidence": 0.92,
  "ml_reasoning": {
    "pattern_score": 1.0,
    "context_score": 0.95,
    "exploitability_score": 0.90,
    "dataflow_score": 0.88,
    "remediation_score": 0.90
  },
  "confidence_label": "HIGH (92%)",
  "filter_status": "KEEP",
  "fix_suggestion": "Use parameterized query: db.query('SELECT * FROM users WHERE id=?', [user_id])"
}
```

---

---

## Detailed Remediation Playbooks

Each finding includes a full remediation guide with examples, testing strategy, and rollout plan.

### Remediation Playbook Template

**Finding**: [CWE-XXX-NAME]  
**Severity**: [CRITICAL/HIGH/MEDIUM/LOW]  
**CVSS Score**: [3.0–9.9]  
**Time to fix**: [15 min – 4 hours]

#### Step 1: Understand the Vulnerability
- What is the attack vector?
- Who is the attacker? (external/internal)
- What is the impact? (data breach/code execution/DoS)

#### Step 2: Identify Code Locations
- All files with the pattern
- Which code paths are affected?
- Is this in primary code or dependencies?

#### Step 3: Implement Fix
- Preferred solution
- Alternative mitigations
- Code snippets for each language

#### Step 4: Test & Validate
- Unit test cases
- Integration tests
- Penetration test checklist

#### Step 5: Deploy & Monitor
- Deployment checklist
- Rollback plan
- Monitoring for exploitation attempts

### Example: CWE-89 SQL Injection Playbook

**Severity**: CRITICAL  
**Time to fix**: 2–4 hours  
**CVSS Score**: 9.8 (High severity)

#### Step 1: Understand the Vulnerability
- **Attack vector**: Attacker injects SQL commands via untrusted input
- **Attacker**: External user (web request parameter)
- **Impact**: Full database compromise, data exfiltration, account takeover

#### Step 2: Locate All Instances
```bash
# Find all dynamic query construction
semgrep -c p/cwe-top-25 . --json | jq '.[] | select(.check_id == "cwe-89")'

# Grep for f-strings/string interpolation in SQL
grep -rn "db\.\(query\|execute\).*f['\"]" . --include="*.py"
grep -rn "\.query.*\`.*\$\{" . --include="*.js"
```

#### Step 3: Implement Fix (Python)
```python
# BEFORE (vulnerable)
user_id = request.args.get('user_id')
results = db.query(f"SELECT * FROM users WHERE id={user_id}")

# AFTER (fixed)
user_id = request.args.get('user_id')
results = db.query("SELECT * FROM users WHERE id=?", [user_id])

# OR with SQLAlchemy ORM (no SQL strings at all)
results = db.session.query(User).filter(User.id == user_id).all()
```

#### Step 4: Test Cases
```python
# Unit test
def test_sql_injection_prevention():
    # Attempt SQL injection
    malicious_id = "1 OR 1=1"
    results = get_users_by_id(malicious_id)
    assert len(results) == 0  # Should not return all users
    
    # Valid query still works
    valid_id = "1"
    results = get_users_by_id(valid_id)
    assert len(results) > 0
```

#### Step 5: Deploy & Monitor
- [ ] Code review by security team
- [ ] Test on staging environment (48 hours)
- [ ] Deploy to production with monitoring
- [ ] Set up alerts: Check logs for SQL errors, suspicious queries
- [ ] Rollback plan: Have previous version ready

---

## Invocation

### Via Semgrep CLI (Fase 2 — Recommended)

```bash
# Install Semgrep
pip install semgrep

# Scan repository with CWE Top 25 rules
semgrep -c p/cwe-top-25 . --json > findings.json

# Scan with multiple rulesets
semgrep -c p/owasp-top-ten -c p/security-audit . --json

# Scan specific language
semgrep --include="*.py" -c p/python-security . --json

# Scan and exclude test/vendor directories
semgrep -c p/cwe-top-25 . --exclude="tests,node_modules,vendor" --json

# Output in SARIF format for GitHub Advanced Security integration
semgrep -c p/cwe-top-25 . --sarif > results.sarif

# High-performance mode (parallel scanning)
semgrep -c p/cwe-top-25 . --json --parallel
```

### Via GitHub MCP (Fase 1 Compatibility)

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

## Fase 2 Roadmap — 8-Week Implementation

### Week 1: Foundation & Semgrep Setup
**Goal**: Integrate Semgrep, establish baseline rules, deploy to CI/CD

- [ ] Install Semgrep CLI in CI/CD pipeline
- [ ] Configure p/owasp-top-ten and p/cwe-top-25 rulesets
- [ ] Create Manta custom rulesets (YAML configs)
- [ ] Set up GitHub Actions workflow:
  ```yaml
  - name: Semgrep SAST scan
    run: semgrep -c p/cwe-top-25 . --sarif > results.sarif
  - name: Upload SARIF
    uses: github/codeql-action/upload-sarif@v1
  ```
- [ ] Baseline scan: Run full repo scan, document findings
- [ ] **Deliverable**: CI/CD integration, baseline report

### Week 2: AST & Taint Analysis Rules
**Goal**: Develop semantic analysis rules, detect data flow vulnerabilities

- [ ] Write Semgrep rules for top 10 taint-based patterns:
  - SQL injection via taint (request → SQL execute)
  - XSS via taint (request → DOM)
  - Path traversal via taint (request → file open)
  - XXE via taint
  - Deserialization via taint
- [ ] Test rules on sample vulnerable code
- [ ] Validate AST patterns with false positive filtering
- [ ] **Deliverable**: 10 taint-based Semgrep rules (YAML)

### Week 3: Pattern Library Expansion (CWE 11–30)
**Goal**: Implement CWE-352, CWE-434, CWE-611, and 7 more critical patterns

- [ ] Implement CSRF detection rules (CWE-352)
- [ ] Implement file upload validation rules (CWE-434)
- [ ] Implement XXE detection (CWE-611)
- [ ] Implement deserialization safety rules (CWE-502)
- [ ] Implement authentication bypass patterns (CWE-287)
- [ ] Implement cryptographic weakness detection (CWE-327, CWE-330)
- [ ] Implement input validation patterns (CWE-20)
- [ ] Implement sensitive data exposure patterns (CWE-200)
- [ ] Test all rules on test corpus
- [ ] **Deliverable**: 10 CWE detection rules + test cases

### Week 4: Pattern Library Expansion (CWE 31–50)
**Goal**: Add remaining high-severity CWE patterns

- [ ] Implement certificate validation bypass (CWE-295)
- [ ] Implement race condition detection (CWE-367, CWE-366)
- [ ] Implement weak random number detection (CWE-338, CWE-330)
- [ ] Implement null pointer dereference patterns (CWE-476)
- [ ] Implement resource exhaustion patterns (CWE-400)
- [ ] Implement hardcoded configuration patterns (CWE-798)
- [ ] Implement LDAP/NoSQL injection patterns (CWE-943)
- [ ] Implement URL redirection bypass (CWE-601)
- [ ] Implement cookie security patterns (CWE-614)
- [ ] Implement XML entity expansion patterns (CWE-776)
- [ ] **Deliverable**: 20 additional CWE rules + test cases

### Week 5: ML-Based Severity Filtering
**Goal**: Train and deploy ML model to reduce false positives

- [ ] Collect labeled dataset: 500+ findings (true positive / false positive)
- [ ] Feature engineering:
  - Pattern type embedding (30 CWE types)
  - Context features (is test file? is comment? is in /vendor?)
  - Data flow score (is input actually untrusted?)
  - Exploitability features (is code reachable from network?)
- [ ] Train ML model (logistic regression / random forest):
  ```python
  from sklearn.ensemble import RandomForestClassifier
  model = RandomForestClassifier(n_estimators=100)
  model.fit(X_train, y_train)  # X: features, y: is_real_vulnerability
  ```
- [ ] Evaluate model: Precision > 0.85, Recall > 0.90
- [ ] Integrate into Semgrep output pipeline
- [ ] **Deliverable**: ML model + integration code + evaluation metrics

### Week 6: Remediation Playbooks & Guides
**Goal**: Create detailed fix guides for all 50+ patterns

- [ ] Develop playbook template (5 steps: understand → locate → fix → test → deploy)
- [ ] Create playbooks for top 20 CWE patterns (CRITICAL/HIGH severity)
- [ ] Add multi-language examples (Python, JavaScript, Go):
  - Vulnerable code snippet
  - Fixed code snippet
  - Test cases
  - Deployment checklist
- [ ] Create quick-fix templates for each CWE
- [ ] Automate playbook generation from Semgrep findings
- [ ] **Deliverable**: 20 detailed playbooks + quick-fix templates

### Week 7: HTML Dashboard Enhancement & Reporting
**Goal**: Build advanced visualization and reporting features

- [ ] Add ML confidence scores to dashboard visualization
- [ ] Create severity distribution chart (pie/bar)
- [ ] Add data flow visualization (source → sink)
- [ ] Create file hotspots heatmap
- [ ] Add trend analysis (findings over time)
- [ ] Implement filtering:
  - By severity
  - By CWE type
  - By language
  - By confidence level (hide low-confidence findings)
- [ ] Add export options:
  - CSV (for spreadsheets)
  - SARIF (for GitHub Advanced Security)
  - PDF report
- [ ] **Deliverable**: Enhanced dashboard + 3 export formats

### Week 8: Production Deployment & Optimization
**Goal**: Deploy Fase 2 to production, optimize performance, create training

- [ ] Performance testing:
  - Benchmark scan time on repos of 100–10k files
  - Optimize Semgrep rules (disable slow patterns if needed)
  - Implement parallel scanning
- [ ] Production deployment:
  - Deploy Semgrep to all Manta repos
  - Configure GitHub Actions for all projects
  - Set up alerting for CRITICAL/HIGH findings
  - Create runbook for on-call engineers
- [ ] Training & documentation:
  - Create user guide (how to interpret findings)
  - Record video walkthrough
  - Update SKILL.md with Fase 2 content
  - Create FAQ document
- [ ] Quality gate setup:
  - Fail CI if CRITICAL findings detected
  - Fail CI if HIGH findings > threshold (e.g., 10)
  - Allow LOW findings (but report)
- [ ] **Deliverable**: Production deployment + documentation + runbooks

### Weekly Milestones Summary

| Week | Focus | Key Deliverable |
|------|-------|-----------------|
| W1 | Semgrep setup | CI/CD integration |
| W2 | AST/taint rules | 10 semantic analysis rules |
| W3 | CWE 11–30 patterns | CSRF, file upload, XXE |
| W4 | CWE 31–50 patterns | Race conditions, auth, crypto |
| W5 | ML filtering | False positive reduction model |
| W6 | Remediation | 20 detailed playbooks |
| W7 | Dashboard | Enhanced reporting UI |
| W8 | Production | Deployment + training |

### Success Criteria

- ✅ 50+ CWE patterns implemented
- ✅ ML false positive filtering working (precision > 0.85)
- ✅ Zero regression in detection (vs Fase 1)
- ✅ Scan time < 5 minutes for medium repos
- ✅ All CRITICAL/HIGH findings have remediation playbooks
- ✅ All Manta projects on Fase 2 with green CI/CD

---

## Changelog

- **v2.0.0** (2026-07-26 – IN DEVELOPMENT) — Fase 2 Major Expansion:
  - 50+ CWE Top 25 patterns (vs 10 OWASP in v1.0)
  - AST (Abstract Syntax Tree) analysis for semantic code checking
  - Semgrep SAST integration (configuration-as-code rulesets)
  - ML-based severity filtering (reduce false positives by 70%+)
  - Detailed remediation playbooks (5-step guides for all patterns)
  - Multi-language examples (Python, JavaScript, Go + others)
  - Enhanced HTML dashboard with data flow visualization
  - 8-week implementation roadmap (W1–W8 with milestones)

- **v1.0.0** (2026-07-26) — Initial release. 10 patterns: SQL, XSS, secrets, deprecated, TODO, promises, command injection, insecure random, path traversal, hardcoded config. GitHub MCP + Bash grep integration. JSON + HTML outputs.

---

## Integration Points

### With Manta Agents

| Agent | Use Case | CWE Focus |
|-------|----------|-----------|
| **Manta 15 (Advisory)** | Security assessment, remediation strategy | All 50+ patterns |
| **Manta 16 (Arquitecto-IA)** | Custom rules, ML model tuning, rule development | Pattern engineering |
| **Manta 02 (Contratual)** | Security liability analysis, contractual impact | CRITICAL/HIGH |
| **Manta 05 (Orçamento)** | Security fix cost estimation | All patterns |
| **Manta 01 (Claims)** | Security incident claims, breach analysis | Exploited CWEs |

### With External Tools

- **GitHub Advanced Security**: Semgrep findings → SARIF → GitHub Dashboard
- **GitLab SAST**: Semgrep integration for GitLab CI/CD
- **SonarQube**: Semgrep rules imported via custom profile
- **Jira**: Automated issue creation from findings
- **Slack**: Daily security digest of new findings

---

## Support & Escalation

- **Minor questions**: Consult pattern library and playbooks above
- **False positives**: Create issue with matched text, context, and ML confidence score
- **New CWE patterns**: Submit PR to pattern library with Semgrep rule (YAML) + test cases + playbook
- **ML model tuning**: Contact Manta 16 (Arquitecto-IA) for model retraining
- **Custom rulesets**: Escalate to Manta 16 for bespoke security rule development
- **Production issues**: Page on-call security engineer (Slack #security-incidents)

**Maintainer**: Manta 15 (Advisory) + Manta 16 (Arquitecto-IA)  
**Repository**: `Codex-exemplo/.claude/skills/`  
**Last updated**: 2026-07-26  
**Next review**: 2026-09-15 (post-Fase 2 W8 completion)
