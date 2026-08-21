# Supabase Setup — SICRO Similaridade Integration

Guia de inicialização do banco de dados PostgreSQL com pgvector para SICRO Similaridade v1.0.

## Pre-requisitos

- [Supabase CLI](https://supabase.com/docs/guides/cli/getting-started)
- PostgreSQL 14+ com extensão pgvector
- Python 3.10+
- Acesso à chave de API Supabase

## 1. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais Supabase
```

Variáveis obrigatórias:
```
SUPABASE_DB_URL=postgresql://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_URL=https://....supabase.co
```

## 2. Criar Tabelas (Migrations)

Via Supabase CLI:

```bash
supabase migration up
```

Ou manualmente via psql:

```bash
psql $SUPABASE_DB_URL < migrations/001_sicro_similaridade_tables.sql
```

Isso criará:
- `sicro_insumos` (índice principal com embeddings)
- `sicro_price_history` (série temporal)
- `sicro_migration_map` (obsolescência)
- `manta_sicro_usage` (priors históricos)
- `sicro_sinapi_equivalence` (benchmarking)
- `sicro_normas` (metadados de normas técnicas)
- `sicro_auditoria_busca` (auditoria para aluci-guard)
- Índices (BM25, IVFFlat para embeddings)
- Views (preços atuais, histórico)

**Verificar criação:**

```bash
psql $SUPABASE_DB_URL -c "\dt sicro_*"
psql $SUPABASE_DB_URL -c "\dv sicro_*"
```

## 3. Carregar Dados Iniciais (Seed)

```bash
psql $SUPABASE_DB_URL < seed/001_sicro_seed.sql
```

Isso carrega:
- 25 itens SICRO de exemplo
- Histórico de preços (últimos 3 meses)
- Itens obsoletos e mapeamento de migração
- Histórico de uso Manta (priors)
- Equivalências SICRO ↔ SINAPI
- Normas técnicas associadas

**Verificar dados:**

```bash
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM sicro_insumos;"
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM sicro_price_history;"
```

## 4. Gerar Embeddings Vetoriais

Instalar dependências:

```bash
pip install -r requirements.txt
```

Executar script:

```bash
python scripts/generate_embeddings.py
```

Isso irá:
1. Carregar modelo BAAI/bge-small-en-v1.5
2. Gerar embeddings (384-dim) para cada item SICRO
3. Armazenar em Supabase (coluna `embedding`)
4. Indexar com IVFFlat para buscas rápidas

**Tempo estimado:** 5-10 minutos (50 itens)

**Verificar:**

```bash
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM sicro_insumos WHERE embedding IS NOT NULL;"
```

Deve retornar o número total de itens.

## 5. Testar Integração

Smoke test da busca:

```bash
psql $SUPABASE_DB_URL -c "
  SELECT codigo, descricao, 
         cosine_similarity(embedding, '[0.1, 0.2, ...]'::vector) as similarity
  FROM sicro_insumos
  ORDER BY similarity DESC
  LIMIT 5;
"
```

## 6. Configurar MCP Server (Claude Code)

Adicionar à `.claude/settings.json`:

```json
{
  "mcp_servers": {
    "supabase": {
      "enabled": true,
      "project_id": "ogxxgvgtulrbbppshjie",
      "api_url": "https://ogxxgvgtulrbbppshjie.supabase.co",
      "api_key": "$SUPABASE_ANON_KEY"
    }
  }
}
```

## 7. Validar com Aluci-Guard

Executar auditoria:

```bash
/aluci-guard
# Validar que não há referências fabricadas em normas/URLs
```

## Troubleshooting

### "pgvector extension not found"
```bash
psql $SUPABASE_DB_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### "Connection refused"
Verificar `SUPABASE_DB_URL` e conectividade:
```bash
psql $SUPABASE_DB_URL -c "SELECT VERSION();"
```

### "Embeddings took too long"
Aumentar `BATCH_SIZE` em `generate_embeddings.py`:
```python
BATCH_SIZE = 100  # aumentar de 50 para 100
```

### "Índice IVFFlat lento"
Recriar com parâmetro `lists`:
```sql
DROP INDEX idx_sicro_embedding;
CREATE INDEX idx_sicro_embedding ON sicro_insumos 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
```

## Estrutura de Arquivos

```
supabase/
├── migrations/
│   └── 001_sicro_similaridade_tables.sql  (DDL + índices)
├── seed/
│   └── 001_sicro_seed.sql                 (dados de teste)
├── scripts/
│   └── generate_embeddings.py             (gerador de embeddings)
├── .env.example                           (template de env vars)
├── requirements.txt                       (dependências Python)
└── README.md                              (este arquivo)
```

## Próximos Passos

1. ✅ Criar tabelas (migrations)
2. ✅ Carregar dados iniciais (seed)
3. ✅ Gerar embeddings
4. ⏳ Integrar skill `sicro-similaridade` com agentes operacionais
5. ⏳ Configurar RAG (Retrieval-Augmented Generation)
6. ⏳ Deploy em produção

## Referências

- [Supabase pgvector Docs](https://supabase.com/docs/guides/database/extensions/pgvector)
- [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [SICRO Official](https://sicrweb.caixa.gov.br/)
