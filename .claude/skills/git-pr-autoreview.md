---
name: git-pr-autoreview
manta_code: "Util-GIT-01"
aliases: ["pr-review", "code-review-auto", "pr-autoreview", "github-review", "owasp-scan"]
version: 1.0.0
updated: 2026-07-26
author: Manta Associados
template_origem: utility-skill-v1.0.0
tier: Sonnet
description: >
  Skill de análise automatizada de Pull Requests com verificação de estilo de
  código (ESLint/Prettier/Black/Go fmt), varredura de segurança OWASP (injection,
  auth, crypto, SSRF, XXE, etc.), e sugestões de correção sem aplicação automática.
  Estrutura em 5 vertentes: V1 Análise de Estilo & Formatação, V2 Varredura de
  Segurança (OWASP Top 10 + CWE), V3 Análise de Complexidade Ciclomática &
  Manutenibilidade, V4 Document Intelligence (docstrings/comments/tests), V5
  Geração de Comentários Estruturados + Draft de Review. Saída: JSON estruturado
  (file:line:severity:message:category:suggested_fix) + preview HTML de review.
  MCP: GitHub search_code + pull_request_review_write. Requer aprovação humana
  antes de qualquer commit; NÃO aplica correções automaticamente. Use SEMPRE que
  mencionar revisão PR, code review automático, análise de segurança, verificação
  de estilo, OWASP scan, linting PR, security audit código.
---

# GIT-PR-AUTOREVIEW — Util-GIT-01

## 1. PERGUNTA OBRIGATÓRIA INICIAL

Antes de qualquer ação:

```
┌──────────────────────────────────────────────────┐
│  GIT-PR-AUTOREVIEW — INTAKE                      │
│                                                  │
│  Q1: Qual é a URL/identificador da PR?           │
│      (ex: https://github.com/owner/repo/pull/42) │
│      ou: owner/repo#42                           │
│                                                  │
│  Q2: Qual é o escopo da análise?                 │
│      (a) Estilo & formatação apenas              │
│      (b) Segurança (OWASP) apenas                │
│      (c) Complexidade & manutenibilidade         │
│      (d) Documentação & testes                   │
│      (e) COMPLETO (todas acima)                  │
│                                                  │
│  Q3: Linguagens no PR?                           │
│      (js) JavaScript/TypeScript                  │
│      (py) Python                                 │
│      (go) Go                                     │
│      (java) Java                                 │
│      (m) Múltiplas                               │
│      (o) Outra                                   │
│                                                  │
│  Q4: Gerar review no GitHub ou apenas JSON?      │
│      (gh) Publicar como draft review no GitHub   │
│      (json) Salvar JSON estruturado localmente   │
│      (both) Ambos                                │
│                                                  │
│  Q5: Severidade mínima a reportar?               │
│      (all) Todas (info, warning, error, critical)│
│      (warn) Warning+ (warning, error, critical)  │
│      (err) Error+ (error, critical)              │
│      (crit) Critical apenas                      │
│                                                  │
│  Q6: Adicionar sugestões de correção automáticas?│
│      (y) Sim, incluir suggested fixes nos inline │
│      (n) Não, apenas reportar issues             │
│      (safe) Apenas fixes "seguros" (fmt, rename) │
│                                                  │
│  Q7: Contexto humano (para memo do review):      │
│      Ex: "API refactor", "Security hardening",   │
│      "Database migration", etc.                  │
└──────────────────────────────────────────────────┘
```

## 2. ARQUITETURA — 5 VERTENTES

```
   ┌──────────────────────────────────────────────────────┐
   │  V1 Análise de Estilo & Formatação                  │
   │  V2 Varredura de Segurança (OWASP Top 10 + CWE)     │
   │  V3 Complexidade Ciclomática & Manutenibilidade     │
   │  V4 Document Intelligence (docstrings/testes)       │
   │  V5 Geração de Review & JSON Estruturado            │
   └──────────────────────────────────────────────────────┘
```

## 3. MÓDULOS POR VERTENTE

### V1 — Análise de Estilo & Formatação
- `pr-style-linter.md` — regras ESLint/Prettier (JS), Black (Py), gofmt (Go)
- `pr-style-naming.md` — convenções camelCase, snake_case, PascalCase
- `pr-style-imports.md` — organização imports, unused imports, circular deps
- `pr-style-comments.md` — comentários obsoletos, TODOs órfãos, console.log
- `pr-style-whitespace.md` — trailing spaces, indentação, line length

### V2 — Varredura de Segurança (OWASP)
- `pr-security-scanner.md` — orquestrador OWASP Top 10 + CWE
- `pr-sec-a01-injection.md` — SQL injection, LDAP, OS command, template injection
- `pr-sec-a02-auth.md` — weak auth, hardcoded creds, missing MFA, JWT expiry
- `pr-sec-a03-data-exposure.md` — logging PII, plaintext passwords, unencrypted comms
- `pr-sec-a04-xxe.md` — XML External Entity, XXE parsing, unsafe deserialization
- `pr-sec-a05-broken-access.md` — IDOR, privilege escalation, missing authz checks
- `pr-sec-a06-config.md` — hardcoded secrets, default creds, debug mode, CORS *
- `pr-sec-a07-ssrf.md` — Server-Side Request Forgery, open redirects, webhook abuse
- `pr-sec-a08-crypto.md` — weak hashing, MD5/SHA1, hardcoded keys, poor randomness
- `pr-sec-a09-logging.md` — insufficient logging, error disclosure, missing audit trails
- `pr-sec-a10-deps.md` — known CVEs in dependencies, outdated libs (Dependabot)

### V3 — Complexidade Ciclomática & Manutenibilidade
- `pr-complexity-cyclomatic.md` — CC > 10? função muito longa? nested conditions?
- `pr-complexity-nesting.md` — callback hell, pyramid of doom, arrow nesting
- `pr-complexity-duplication.md` — código duplicado (DRY), oportunidades de refactor
- `pr-complexity-cohesion.md` — responsabilidade única? função faz uma coisa bem?

### V4 — Document Intelligence
- `pr-docs-docstrings.md` — funções sem docstring/JSDoc/GoDoc? parâmetros documentados?
- `pr-docs-tests.md` — função nova sem testes? cobertura diminuiu? edge cases?
- `pr-docs-comments.md` — comentários claros sobre PORQUÊ (não o quê)?
- `pr-docs-changelog.md` — entry em CHANGELOG/release notes? API docs updated?

### V5 — Geração de Review & JSON
- `pr-review-generator.md` — orquestrador, agregação de todas as vertentes
- `pr-json-schema.md` — schema JSON estruturado (file:line:severity:message:fix)
- `pr-review-draft.md` — template HTML+Markdown para draft review GitHub
- `pr-summary-metrics.md` — dashboard: style score, security score, complexity, coverage delta

## 4. ESTRUTURA DE SAÍDA — JSON SCHEMA

```json
{
  "pr": {
    "owner": "string",
    "repo": "string",
    "pull_number": "integer",
    "head_sha": "string",
    "base_ref": "string",
    "title": "string",
    "changed_files_count": "integer",
    "additions": "integer",
    "deletions": "integer"
  },
  "analysis": {
    "timestamp": "ISO8601",
    "scopes_analyzed": ["style", "security", "complexity", "docs"],
    "languages_detected": ["JavaScript", "Python"],
    "total_findings": "integer"
  },
  "findings": [
    {
      "id": "pr-sec-a02-001",
      "file_path": "src/auth.js",
      "line_start": 42,
      "line_end": 45,
      "severity": "critical",
      "category": "security",
      "subcategory": "a02_broken_authentication",
      "title": "Hardcoded API key in source code",
      "message": "Plaintext API key detected in line 43. This credential MUST be moved to environment variables or a secrets manager (AWS Secrets Manager, HashiCorp Vault).",
      "code_snippet": "const API_KEY = 'sk_live_abc123...'",
      "cwe": ["CWE-798"],
      "owasp": ["A02:2021 – Cryptographic Failures"],
      "suggested_fix": "const API_KEY = process.env.API_KEY || '';",
      "fix_level": "safe",
      "references": [
        "https://owasp.org/www-project-top-ten/",
        "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"
      ]
    },
    {
      "id": "pr-style-001",
      "file_path": "src/utils.js",
      "line_start": 100,
      "line_end": 100,
      "severity": "warning",
      "category": "style",
      "subcategory": "formatting",
      "title": "Trailing whitespace",
      "message": "Line 100 has 3 trailing spaces.",
      "code_snippet": "  return result;   ",
      "suggested_fix": "  return result;",
      "fix_level": "safe",
      "tool": "ESLint (no-trailing-spaces)"
    },
    {
      "id": "pr-complexity-002",
      "file_path": "src/business.js",
      "line_start": 50,
      "line_end": 120,
      "severity": "warning",
      "category": "complexity",
      "subcategory": "cyclomatic_complexity",
      "title": "High cyclomatic complexity (CC=14)",
      "message": "Function 'processOrder' has CC=14 (threshold: 10). Consider breaking into smaller functions.",
      "suggested_fix": "Extract validateOrder(), calculateDiscount(), applyTax() as separate functions.",
      "fix_level": "moderate"
    }
  ],
  "summary": {
    "critical_count": 1,
    "error_count": 2,
    "warning_count": 5,
    "info_count": 3,
    "style_issues": 8,
    "security_issues": 3,
    "complexity_issues": 2,
    "docs_issues": 4,
    "overall_score": 72,
    "recommendation": "CHANGES_REQUESTED"
  },
  "review_draft": {
    "status": "PENDING",
    "title": "Auto-Review: 3 critical/error findings",
    "body": "## Summary\n\n**Overall Score: 72/100**\n\n- **Critical**: 1 finding (hardcoded secrets)\n- **Errors**: 2 findings\n- **Warnings**: 5 findings\n\n...",
    "can_approve": false,
    "requires_human_review": true
  }
}
```

## 5. ARTEFATOS DE SAÍDA

1. **JSON Estruturado** (`findings.json`)
   - Completo, estruturado, pronto para integração CI/CD
   - Schemas validados

2. **Draft PR Review** (GitHub comment, via `pull_request_review_write`)
   - Conversível para HTML render
   - Markdown com inline code suggestions
   - Status: PENDING (nunca APPROVED/COMMENTED sem aprovação humana)

3. **Dashboard HTML** (opcional, artefato React)
   - Visualização das findings
   - Gráficos de distribuição (style vs security vs complexity)
   - Links diretos para código no GitHub

4. **Relatório de Impacto** (Markdown)
   - Delta de segurança em relação à base branch
   - Mudanças em cobertura de testes
   - Potencial technical debt introduzido

## 6. REGRAS FUNDAMENTAIS

1. **NUNCA aplicar correções automaticamente.** Apenas SUGERIR.
2. **Sempre exigir aprovação humana antes de qualquer escrita no GitHub.**
3. **JSON estruturado é a fonte da verdade;** review draft é apenas visualização.
4. **Severidade CRITICAL ou ERROR = bloqueia merge** (marcado no summary).
5. **Findings devem ter linha:coluna exata** (não ranges vagas).
6. **Incluir CWE/OWASP references em segurança.**
7. **Para security: incluir "fix_level"** (safe, moderate, high_risk).
8. **Linguagens com regras diferentes** (JS ESLint ≠ Python Black).
9. **Se detectar secrets (API key, token, password), severidade = CRITICAL.**
10. **Não reportar false positives** (e.g., "password" em comentário ≠ secret).

## 7. WORKFLOW DE INTEGRAÇÃO

```
User input (Q1-Q7)
    ↓
fetch PR diff via GitHub (search_code + PR metadata)
    ↓
Parse altered lines (linha exata por arquivo)
    ↓
V1: Estilo & Formatação (linter rules)
    ↓
V2: Segurança (OWASP scan)
    ↓
V3: Complexidade (CC analyzer)
    ↓
V4: Documentação & Testes (AST parser)
    ↓
V5: Agregação & Geração
    ├→ JSON findings
    ├→ Review draft (Markdown)
    └→ Summary (score, recommendation)
    ↓
[HUMAN APPROVAL GATE]
    ↓
IF aprovado:
  publicar via pull_request_review_write (PENDING)
  gerar HTML dashboard
ELSE:
  salvar JSON localmente, aguardar feedback
```

## 8. INTEGRAÇÕES MANTA

- `padrao-manta`, `consist-guard` — validações estruturais
- `agente-contratual` — análise de compliance em PRs (legal review)
- `agente-06` — análise de modelos/dados em alterações
- **CI/CD pipelines** — integração webhook (GitHub Actions, GitLab CI)
- **Slack/Teams** — notificações (opcional, via SendMessage)

## 9. HANDOFF PARA OUTROS AGENTES

| Quando aparecer | Handoff para |
|---|---|
| Violação de compliance/legal em código | `agente-contratual` |
| Bug em lógica de negócio identificado | `agente-advisory` (segunda opinião) |
| Dados de modelo alterados sem testes | `agente-06` (modelagem) |
| Falha de performance detectada | `agente-06` (otimização) |
| Integração com infra/deploy | Skill `cd-infrastructure` ou `devops` |

## 10. O QUE ESTE SKILL NÃO FAZ

- Não substitui testes automatizados (apenas valida alterações).
- Não faz merge automático (requer aprovação humana explícita).
- Não executa código (apenas análise estática).
- Não fornece code coverage report (referencia dados de CI se disponível).
- Não substitui security audit profissional para código crítico.

## 11. DEPENDÊNCIAS MCP & TIER

**MCP Tools Necessários:**
- `github__search_code` — procurar padrões nas alterações
- `github__pull_request_review_write` — criar/atualizar draft review

**Tier:** Sonnet (capacity para análise complexa de múltiplas linhas)

**Timeout:** 30s por arquivo alterado (max 5 min por PR)

## 12. EXEMPLOS DE SAÍDA

### Exemplo 1: Security Finding (CRITICAL)
```json
{
  "id": "pr-sec-a02-hardcoded-key",
  "file_path": "config/secrets.js",
  "line_start": 5,
  "severity": "critical",
  "category": "security",
  "title": "Hardcoded database password",
  "message": "Database password found in plaintext. Must be moved to environment variables.",
  "code_snippet": "const dbPass = 'MyS3cur3P@ss';",
  "cwe": ["CWE-798"],
  "suggested_fix": "const dbPass = process.env.DB_PASSWORD;"
}
```

### Exemplo 2: Style Finding (WARNING)
```json
{
  "id": "pr-style-eslint-001",
  "file_path": "src/api.js",
  "line_start": 42,
  "severity": "warning",
  "category": "style",
  "title": "Unused variable 'config'",
  "suggested_fix": "Remove 'const config = {}; on line 42 or use it.",
  "tool": "ESLint (no-unused-vars)"
}
```

### Exemplo 3: Complexity Finding (WARNING)
```json
{
  "id": "pr-complexity-cc-high",
  "file_path": "src/processor.js",
  "line_start": 30,
  "line_end": 110,
  "severity": "warning",
  "category": "complexity",
  "title": "Cyclomatic Complexity too high (CC=16)",
  "message": "Function 'validateAndProcess' exceeds threshold of 10.",
  "suggested_fix": "Extract conditional logic into separate functions: validateUser(), validateData(), processTransaction()."
}
```

## 13. METADADOS

```
Skill: git-pr-autoreview
Versão: 1.0.0
Criada: 2026-07-26
Categoria: Utility / DevOps / Code Quality
Propósito: Análise automatizada de PRs (estilo, segurança, complexidade)
MCP Tools: GitHub (search_code, pull_request_review_write)
Tier: Sonnet
Timeout: 5min max/PR
Entrada: PR URL ou owner/repo#number
Saída: JSON + Draft Review GitHub + HTML Dashboard
Requer Aprovação: SIM (human gate antes de publish)
Auto-Apply Fixes: NÃO (sugestões apenas)
Linguagens Suportadas: JavaScript, TypeScript, Python, Go, Java, (extensível)
OWASP Coverage: Top 10 + CWE
Classificação: Interno — Manta Associados
```

---

## INSTRUÇÕES DE ATIVAÇÃO

Para usar este skill, invoque com:

```
/git-pr-autoreview <PR_URL_or_owner/repo#number>
```

Sistema fará as perguntas Q1-Q7 e entregará análise estruturada dentro de 5 min.

**Sempre aprove antes de publicar no GitHub.**
