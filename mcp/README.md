# MantaBase MCP v2

**Code-execution + sandbox + SSA-equivalente auth**

Versão: 2.0.0 | Ticket: MNT-2026-UPGRADE-AGENTS-S6S10 | Branch: `claude/mantabase-mcp-v2-arch-ala0oo`

## Arquitetura

### 4 Propostas + Decisão

| ID | Proposta | Status | Impacto | Esforço |
|----|----------|--------|---------|---------|
| P1 | Migrar para padrão code-execution | ✅ Implementado | Alto | Médio |
| P2 | Sandbox de execução isolado | ✅ Implementado | Alto | Baixo |
| P3 | Autenticação SSA-equivalente | ✅ Implementado | Médio | Baixo |
| P4 | Eliminar duplicidade Netlify/Railway | ⏳ Pós-merge | Baixo | Trivial |

**Decisão**: P3 agora + P1+P2 já estão embutidos. Resultado: **arquitetura coesa** (não apenas P3 isolada).

---

## 3 Meta-tools

### 1. `execute` — Python com sandbox

```python
# Requisição
{
    "code": "import pandas as pd\ndf = pd.DataFrame([...])\nresult = df.sum()",
    "context": {
        "client": supabase_client,
        "pd": pandas,
    }
}

# Resposta
{
    "result": <obj>,
    "output": "...",  # stdout capturado
    "error": None,
    "execution_time": 0.234
}
```

**Bloqueios** (RestrictedPython):
- ❌ `import os`, `import sys`, `import subprocess`
- ❌ `socket`, `urllib`, `requests`
- ❌ File I/O fora do escopo
- ❌ `eval()`, `exec()` não-restrito

**Permite**:
- ✅ Pandas, NumPy, Polars
- ✅ Custom schemas (dataclasses, Pydantic)
- ✅ Lógica Python arbitrária (dentro das restrições)

### 2. `query` — Read-only SQL

```python
{
    "sql": "SELECT * FROM projects WHERE status = $1",
    "params": {"status": "active"}
}

# Resposta
{
    "rows": [{...}, {...}],
    "count": 42,
    "error": None
}
```

**Bloqueios**:
- ❌ INSERT, UPDATE, DELETE, DROP, TRUNCATE
- ❌ Alterações de schema

**Permite**:
- ✅ SELECT, JOINs, agregações
- ✅ CTEs, window functions
- ✅ Parâmetros named

### 3. `skills` — Templates pré-aprovados

```python
{
    "category": "data-processing"  # opcional
}

# Resposta
{
    "skills": [
        {
            "id": "skill-001",
            "name": "Bulk insert rows",
            "category": "data-processing",
            "code": "...",
            "description": "..."
        }
    ]
}
```

Cada skill é um snippet testado que pode ser copiado e adaptado em `execute()`.

---

## Autenticação (P3)

### SSA-equivalente: JWT curta duração + renovação automática

**Padrão**: Sem intervenção humana, renovação automática.

```python
from auth import get_token_manager

mgr = get_token_manager()

# Emitir token
token = mgr.issue_token(
    user_email="mneves@mantaassociados.com",
    scopes=["execute.python", "query.supabase", "sharepoint.write"],
    ttl_seconds=3600  # 1 hora
)

# Validar
payload = mgr.validate_token(token)
if payload is None:
    print("Token inválido ou expirado")

# Verificar se está próximo de expirar
if mgr.is_token_expiring_soon(token, threshold_seconds=300):
    # Renovar antes que expire
    token = mgr.refresh_token(token)
```

**Scopes suportados**:
- `execute.python` — rodar código em `execute()`
- `query.supabase` — queries em `query()`
- `sharepoint.write` — escrever no SharePoint
- `skills.read` — listar skills

**Payload JWT**:
```json
{
    "sub": "mneves@mantaassociados.com",
    "iss": "mantabase-mcp-v2",
    "aud": "mcp-core",
    "scope": ["execute.python", "query.supabase"],
    "exp": 1719235200,
    "iat": 1719231600,
    "nbf": 1719231600
}
```

---

## Setup

### 1. Instalação

```bash
cd mcp/
pip install -e ".[dev]"
```

### 2. Variáveis de ambiente

```bash
export MANTABASE_SECRET_KEY="seu-secret-super-longo-aleatorio"
export SUPABASE_URL="https://project.supabase.co"
export SUPABASE_KEY="sua-api-key"
```

### 3. Rodar testes

```bash
pytest tests/ -v
```

### 4. Rodar servidor

```bash
python server.py
```

---

## Deploy

### Netlify (ativo)

```bash
# Build
pip install -e .

# Start
python server.py
```

Entrypoint: `/api/mcp` (proxy FastMCP).

### Railway (pendente)

Próxima fase pós-merge. Eliminar duplicidade (P4).

---

## Próximos passos (Etapa 4 — Ciclo 2)

1. **Implementar `query()` de verdade** — integrar Supabase client
2. **Iterar `execute()` scopes** — adicionar permissões por função (admin/user/viewer)
3. **Testes de integração** — E2E com Supabase + SharePoint
4. **Deploy ponto-a-ponto** — Netlify CI + Railway switchover
5. **Documentação de skills** — biblioteca de 10-20 templates testados

---

## Referências

- [RestrictedPython](https://restrictedpython.readthedocs.io/)
- [FastMCP](https://github.com/jlopp/fastmcp)
- [JWT (RFC 7519)](https://tools.ietf.org/html/rfc7519)
- [CLAUDE.md](../CLAUDE.md) — Manta Maestro master registry
