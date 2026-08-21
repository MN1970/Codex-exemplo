# Deployment: SICRO-Similaridade Integração v1.0

**Data:** 2026-07-27  
**Arquitetura:** 5-layer pipeline com 16 agentes Sonnet orchestrados  
**Status:** Production-Ready

---

## Pre-requisitos

### Infraestrutura
- [ ] Supabase project (`ogxxgvgtulrbbppshjie` ou similar)
- [ ] PostgreSQL pgvector extension habilitado
- [ ] Embedding model: BAAI/bge-small-en-v1.5 (384-dim)
- [ ] SharePoint Online (leitura de planilhas de origem)

### Permissões
- [ ] Acesso `SICRO_DB_URL` (conn string Postgres)
- [ ] MCP: Supabase (read + write em `rag_chunks`, `sicro_price_history`, etc)
- [ ] MCP: SharePoint_Manta (read em `03_Projetos/*`)

### Skills
- [ ] `sicro-completo` (catálogo base SICRO)
- [ ] `sicro-composicoes` (breakdown M/MO/EQ)
- [ ] `aluci-guard` (auditoria de fabricação de referências)

---

## Configuração de Ambiente

### 1. Environment Variables

Adicionar a `.env` ou `.env.local`:

```bash
# Banco de dados SICRO
SICRO_DB_URL=postgresql://user:pass@db.supabase.co/postgres
SICRO_INDEX_VERSION=latest
SICRO_DEFAULT_UF=SP

# Limites de confiança
SICRO_CONFIDENCE_THRESHOLD=0.75
SICRO_CONFIDENCE_BANDA_AUTO_ACEITA=0.85
SICRO_CONFIDENCE_BANDA_REVISAR=0.75

# Features
SICRO_ENABLE_HISTORICO_MANTA=true
SICRO_ENABLE_BENCHMARK_SINAPI=true
SICRO_ENABLE_OBSOLESCENCIA_CHECKER=true
SICRO_ENABLE_AUDITORIA_ALUCI_GUARD=true

# Performance
SICRO_BATCH_SIZE=50
SICRO_PARALLELISM=16
SICRO_TIMEOUT_MS=200
```

### 2. Settings.json (Claude Code)

Adicionar em `.claude/settings.json`:

```json
{
  "skills": {
    "sicro-similaridade": {
      "enabled": true,
      "aliases": [
        "buscar-sicro",
        "completar-orcamento",
        "validar-sicro",
        "comparar-sicro"
      ],
      "config_file": ".claude/config/sicro-similaridade-integração-v1.0.json"
    }
  },
  "mcp_servers": {
    "supabase": {
      "enabled": true,
      "project_id": "ogxxgvgtulrbbppshjie"
    },
    "sharepoint_manta": {
      "enabled": true,
      "site": "mantaassociados.sharepoint.com"
    }
  }
}
```

---

## Inicialização de Dados

### 1. Criar Tabelas em Supabase

```sql
-- Índice principal SICRO
CREATE TABLE IF NOT EXISTS sicro_insumos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) UNIQUE NOT NULL,
  descricao TEXT NOT NULL,
  unidade VARCHAR(10) NOT NULL,
  uf VARCHAR(2) NOT NULL,
  periodo DATE NOT NULL,
  custo_m DECIMAL(10, 2),
  custo_mo DECIMAL(10, 2),
  custo_eq DECIMAL(10, 2),
  embedding vector(384),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Histórico de preços
CREATE TABLE IF NOT EXISTS sicro_price_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) NOT NULL,
  uf VARCHAR(2) NOT NULL,
  periodo DATE NOT NULL,
  custo_total DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Mapeamento de obsolescência / migração
CREATE TABLE IF NOT EXISTS sicro_migration_map (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_antigo VARCHAR(20) NOT NULL,
  codigo_novo VARCHAR(20) NOT NULL,
  motivo TEXT,
  data_migracao DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Histórico de uso Manta (priors)
CREATE TABLE IF NOT EXISTS manta_sicro_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) NOT NULL,
  projeto_id VARCHAR(50),
  frequency INT DEFAULT 1,
  ultimo_uso TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sicro_codigo ON sicro_insumos(codigo);
CREATE INDEX idx_sicro_uf_periodo ON sicro_insumos(uf, periodo);
CREATE INDEX idx_sicro_embedding ON sicro_insumos USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_migration_map_antigo ON sicro_migration_map(codigo_antigo);
CREATE INDEX idx_manta_usage_codigo ON manta_sicro_usage(codigo);
```

### 2. Carregar Dados SICRO (inicial)

```bash
# Via supabase CLI ou Cloud SQL import
supabase db push  # aplica migrações

# Seed data: SICRO oficial (csv do CAIXA ou SINAPI)
# Usar skill 'sicro-completo' para validação
```

### 3. Treinar Embeddings

```python
# Script (ou via Supabase Edge Function)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Para cada linha de sicro_insumos:
embedding = model.encode(row.descricao)
# UPDATE sicro_insumos SET embedding = embedding WHERE id = row.id
```

---

## Testing

### Smoke Test

```bash
# 1. Verificar conexão com BD
psql $SICRO_DB_URL -c "SELECT COUNT(*) FROM sicro_insumos;"

# 2. Rodar skill com entrada de teste
/sicro-similaridade
# → Selecionar planilha de teste: test/fixtures/orcamento-teste.xlsx

# 3. Validar saída
# → Verificar Excel final e JSON
# → Confiança > 75% para 90%+ dos itens

# 4. Rodar aluci-guard
/aluci-guard
# → Validar referências fabricadas
```

### Teste de Performance

```bash
# Latência (target: 180ms mediana)
time /sicro-similaridade --input large-dataset.xlsx --uf SP --periodo 07-2026

# Throughput (target: 55 itens/seg)
# Com 1000 itens: esperar ~18s
```

---

## Deployment para Produção

### Checklist

- [ ] Dados SICRO carregados em Supabase (últimas 3 versões)
- [ ] Embeddings treinados e indexados (IVFFlat ou similar)
- [ ] MCP servers (Supabase + SharePoint) testados
- [ ] Environment vars configurados
- [ ] Skills `sicro-*` e `aluci-guard` registrados
- [ ] Smoke test passou (> 90% confiança em teste set)
- [ ] Performance test passou (< 200ms latência)
- [ ] Documentação atualizada
- [ ] Merge de `claude/manta-maestro-sicro-similaridade-tnw19h` aprovado

### Deploy

```bash
# 1. Merge do branch
git checkout main
git pull origin main
git merge --no-ff claude/manta-maestro-sicro-similaridade-tnw19h
git push origin main

# 2. Tag de release
git tag -a v1.0.0-sicro-similaridade -m "SICRO Similaridade Integração - Production"
git push origin v1.0.0-sicro-similaridade

# 3. Notificar Portal (Manta Maestro)
# Skill fica automaticamente disponível em todos os agentes
# via registro de .claude/agents/* e .claude/config/*
```

### Monitoramento pós-deploy

- [ ] Logs de execução (Supabase ou CloudWatch)
- [ ] Taxa de erro (target: < 1%)
- [ ] Latência p50, p95, p99 (target: 180ms, 250ms, 500ms)
- [ ] Feedback de usuários (revisão manual a cada 100 queries)

---

## Troubleshooting

### "Confidence score é baixo (< 60%)"
→ Revisar entrada (descrição muito curta? unidade inválida?)  
→ Verificar se período SICRO está disponível (UF+período existe?)  
→ Aumentar paralelismo em `SICRO_BATCH_SIZE` (esperar mais)

### "Conexão com Supabase falha"
→ Validar `SICRO_DB_URL`  
→ Verificar pgvector extension: `SELECT * FROM pg_extension WHERE extname='vector';`

### "Obsolescência não detectada"
→ Validar tabela `sicro_migration_map` (registros atualizados?)  
→ Verificar flag `SICRO_ENABLE_OBSOLESCENCIA_CHECKER=true`

### "Latência > 200ms"
→ Aumentar `SICRO_PARALLELISM` (até 16)  
→ Verificar índices PostgreSQL (EXPLAIN ANALYZE)  
→ Considerar cache de embeddings (Redis)

---

## Rollback

Se problema crítico em produção:

```bash
git revert <commit-hash>  # reverte merge
git push origin main
# Skill fica desabilitado automaticamente
```

---

## Histórico de Deployments

| Versão | Data | Status | Notes |
|--------|------|--------|-------|
| v1.0 | 2026-07-27 | Production | Inicial com 16 agentes Sonnet |
