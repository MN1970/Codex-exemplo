# Setup Checklist — SICRO Similaridade Database

Passo-a-passo para inicializar o banco de dados Supabase para produção.

## ✅ Pré-requisitos

- [ ] Supabase project criado (https://app.supabase.com)
- [ ] CLI instalado: `npm install -g supabase`
- [ ] Python 3.10+ instalado
- [ ] Acesso à conexão Supabase (host, user, password)
- [ ] pgvector extension habilitado

## 🚀 Execução (15-20 minutos)

### 1. Preparar Ambiente (2 min)

```bash
cd supabase/

# Copiar template de env vars
cp .env.example .env

# Editar .env com credenciais Supabase
# SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.supabase.co:5432/postgres
nano .env
```

**Check:** Testar conexão
```bash
psql $SUPABASE_DB_URL -c "SELECT VERSION();"
```

---

### 2. Criar Tabelas (2 min)

```bash
# Executar migrations
psql $SUPABASE_DB_URL < migrations/001_sicro_similaridade_tables.sql
```

**Check:** Verificar tabelas criadas
```bash
psql $SUPABASE_DB_URL -c "\dt sicro_*"
# Deve retornar: 7 tabelas (sicro_insumos, price_history, migration_map, etc)
```

---

### 3. Carregar Dados de Teste (1 min)

```bash
# Inserir 25 itens SICRO + histórico + normas
psql $SUPABASE_DB_URL < seed/001_sicro_seed.sql
```

**Check:** Verificar dados
```bash
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM sicro_insumos;"
# Deve retornar: 25
```

---

### 4. Gerar Embeddings (5-10 min)

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Gerar embeddings (384-dim, BAAI/bge-small-en-v1.5)
python scripts/generate_embeddings.py
```

**Output esperado:**
```
INFO: Carregando modelo BAAI/bge-small-en-v1.5...
INFO: Conectando ao Supabase...
INFO: Processando 25 itens...
INFO: Batch 1: Gerando embeddings para 25 itens...
INFO: Batch salvo: 25 embeddings
✅ Embeddings gerados e armazenados com sucesso!
```

**Check:** Verificar embeddings
```bash
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM sicro_insumos WHERE embedding IS NOT NULL;"
# Deve retornar: 25
```

---

### 5. Testar Busca Vetorial (2 min)

```bash
# Teste de busca (cosine similarity)
psql $SUPABASE_DB_URL -c "
  SELECT codigo, descricao, 
         (embedding <=> '[0.1,0.2,0.3,...]'::vector) as distance
  FROM sicro_insumos
  ORDER BY distance
  LIMIT 3;
"
```

**Check:** Deve retornar 3 itens mais similares

---

### 6. Configurar MCP + Claude Code (2 min)

```bash
# Adicionar ao .claude/settings.json
cat >> .claude/settings.json <<'EOF'
{
  "mcp_servers": {
    "supabase": {
      "enabled": true,
      "project_id": "ogxxgvgtulrbbppshjie",
      "api_url": "https://ogxxgvgtulrbbppshjie.supabase.co",
      "api_key": "eyJ..."
    }
  }
}
EOF
```

---

### 7. Validação Final (2 min)

```bash
# Testar skill sicro-similaridade
/sicro-similaridade

# Selecionar planilha de teste
# → Deve retornar JSON com matches e scores

# Validar com aluci-guard
/aluci-guard
# → Deve confirmar que não há referências fabricadas
```

---

## 📊 Métricas de Sucesso

| Métrica | Target | Verificar |
|---------|--------|-----------|
| Tabelas criadas | 7 | `\dt sicro_*` → 7 tables |
| Itens SICRO | 25 | `SELECT COUNT(*)` → 25 |
| Embeddings | 25 | `WHERE embedding IS NOT NULL` → 25 |
| Latência query | < 50ms | `EXPLAIN ANALYZE` |
| Índice IVFFlat | ✅ | `\di idx_sicro_embedding` |

---

## ⚠️ Troubleshooting

### Erro: "pgvector extension not found"
```bash
psql $SUPABASE_DB_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Erro: "Connection refused"
- Verificar host/port em `SUPABASE_DB_URL`
- Verificar se IP está whitelisted
- Teste: `psql -h db.supabase.co -U postgres -c "SELECT VERSION();"`

### Erro: "Embeddings generation timeout"
- Aumentar timeout em `generate_embeddings.py`
- Reduzir `BATCH_SIZE` de 50 para 25

### Query lenta após embeddings
```sql
-- Recriar índice com mais lists
DROP INDEX idx_sicro_embedding;
CREATE INDEX idx_sicro_embedding ON sicro_insumos 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
VACUUM ANALYZE;
```

---

## 📝 Cleanup (se necessário)

```bash
# Dropar todas as tabelas SICRO
psql $SUPABASE_DB_URL -c "
  DROP TABLE IF EXISTS sicro_auditoria_busca CASCADE;
  DROP TABLE IF EXISTS sicro_normas CASCADE;
  DROP TABLE IF EXISTS sicro_sinapi_equivalence CASCADE;
  DROP TABLE IF EXISTS manta_sicro_usage CASCADE;
  DROP TABLE IF EXISTS sicro_migration_map CASCADE;
  DROP TABLE IF EXISTS sicro_price_history CASCADE;
  DROP TABLE IF EXISTS sicro_insumos CASCADE;
"

# Remover extensão pgvector (se não usar em outro lugar)
psql $SUPABASE_DB_URL -c "DROP EXTENSION IF NOT EXISTS vector;"
```

---

## 🎉 Pronto!

Se todos os checks passaram, o banco de dados está pronto para:
1. ✅ Skill `sicro-similaridade` operacional
2. ✅ Integração com agentes Manta
3. ✅ Consultas de busca em tempo real

**Próximo passo:** Integração com `manta-orcamento` (Manta 05)
