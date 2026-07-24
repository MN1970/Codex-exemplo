# Supabase Setup Guide — MantaBase MCP v2

**Status**: required para query() funcional | **Arquivo**: `supabase_migrations.sql`

---

## 1. Criar projeto Supabase

1. Ir para [supabase.com](https://supabase.com)
2. New project
3. Database password (salvar em segurança)
4. Aguardar setup (~2 min)

## 2. Copiar credenciais

**Supabase Dashboard** → Settings → API

```bash
export SUPABASE_URL="https://xxxxxx.supabase.co"
export SUPABASE_KEY="eyJhbGc..."  # public API key
export SUPABASE_DB_PASSWORD="sua-senha"  # para migrations
```

## 3. Aplicar migrations

### Opção A: via Supabase Dashboard (simples)

1. Dashboard → SQL Editor
2. New query
3. Copiar conteúdo de `supabase_migrations.sql`
4. Run

### Opção B: via CLI (recomendado)

```bash
# Instalar Supabase CLI
npm install -g supabase

# Login
supabase login

# Aplicar migration
psql postgresql://postgres:$SUPABASE_DB_PASSWORD@db.xxxxxx.supabase.co:5432/postgres \
  -f mcp/supabase_migrations.sql
```

### Opção C: via MCP Supabase tool (futuro)

```python
from mcp_supabase import apply_migration
apply_migration("supabase_migrations.sql")
```

---

## 4. Verificar migration

```sql
-- Verificar função RPC criada
SELECT routine_name FROM information_schema.routines 
WHERE routine_name = 'execute_select_query';

-- Verificar tabela de auditoria
SELECT * FROM mcp_query_audit LIMIT 1;

-- Verificar tabela de exemplo (projects)
SELECT COUNT(*) FROM projects;
```

---

## 5. Testar query() funcional

```bash
cd mcp/

# Setup env
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="..."

# Rodar testes
pytest tests/test_supabase_query.py -v -k "execute_query"

# Ou manualmente
python -c "
from supabase_client import SupabaseQueryClient
client = SupabaseQueryClient()
result = client.execute_query('SELECT * FROM projects LIMIT 1')
print(result)
"
```

---

## 6. Estrutura de dados (exemplo)

### Tabela: projects

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT ('active', 'inactive', 'archived'),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### RPC: execute_select_query

```sql
SELECT * FROM rpc('execute_select_query', {
    'p_sql': 'SELECT * FROM projects WHERE status = $1',
    'p_params': '{"status": "active"}'
})
```

---

## 7. Auditoria (logging de queries)

Todas as queries executadas via MCP são logadas em `mcp_query_audit`:

```sql
SELECT user_email, query_hash, duration_ms, row_count 
FROM mcp_query_audit 
WHERE user_email = 'user@example.com'
ORDER BY executed_at DESC 
LIMIT 10;
```

---

## 8. Row Level Security (RLS)

### Projetos públicos (read-only)

```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Todos podem ler
CREATE POLICY "Projects are viewable by anyone" ON projects
    FOR SELECT USING (true);

-- Apenas admin pode escrever (fora do MCP, via API)
CREATE POLICY "Only admin can insert" ON projects
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

---

## 9. Performance tuning

### Índices recomendados

```sql
-- Status queries
CREATE INDEX idx_projects_status ON projects(status);

-- Time-based queries
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- Full-text search (futuro)
CREATE INDEX idx_projects_search ON projects USING gin(to_tsvector('english', name || ' ' || description));
```

### Query profiling

```sql
-- Explicar plan
EXPLAIN ANALYZE
SELECT * FROM projects 
WHERE status = 'active' 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## 10. Troubleshooting

### Erro: "RPC function not found"

→ Verificar se migration foi aplicada:
```sql
SELECT * FROM pg_proc WHERE proname = 'execute_select_query';
```

### Erro: "Mutation queries are not allowed"

→ SQL contém INSERT/UPDATE/DELETE — bloqueado por design.

### Erro: "Connection refused"

→ SUPABASE_URL ou SUPABASE_KEY inválidos.

### Query lenta (>1s)

→ Verificar índices:
```sql
EXPLAIN ANALYZE SELECT ...;
```

---

## 11. Próximas fases

- [ ] Implementar `mcp_query_audit` logging automático
- [ ] Cache de queries (Redis/Upstash)
- [ ] Query rate limiting (max 100/min por user)
- [ ] Full-text search via RPC
- [ ] Realtime subscriptions (WebSocket)

---

## Referências

- [Supabase Docs](https://supabase.com/docs)
- [PostgREST API](https://postgrest.org/)
- [RPC Functions](https://supabase.com/docs/guides/database/functions)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

---

**Última atualização**: 2026-07-24 | **Ticket**: MNT-2026-UPGRADE-AGENTS-S6S10
