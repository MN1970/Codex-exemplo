# Parallel KE Embeddings Indexing — Quick Start

> Infraestrutura implementada para indexação paralela de Knowledge Extractions no Manta Maestro.
>
> **Status:** ✅ Base 100% indexada (86/86 KEs). Infraestrutura pronta para rodar on-demand.

---

## Visão Geral

A infraestrutura permite descobrir, shardear e indexar em paralelo Knowledge Extractions que não têm embeddings ainda.

```
KEs sem embedding → Discover → Shard → Parallel indexing → Verify
     (lista)      (SQL)    (Python)  (N subagents)       (SQL)
```

Cada subagent processa um shard independentemente, gerando embeddings localmente via `SentenceTransformer` e inserindo no Supabase MCP.

---

## Quick Start

### 1️⃣ Demo (sem dados reais)

```bash
cd /home/user/Codex-exemplo

# Demo rápido (sem download de modelo)
python3 scripts/run_ke_indexing_demo.py --no-embeddings

# Demo completo (com embeddings reais, ~60s na primeira execução)
python3 scripts/run_ke_indexing_demo.py
```

Isso mostra:
- Discovery de 5 KEs fictícias
- Sharding em 2 shards
- Geração de prompts prontos para subagents
- Geração de SQL INSERT (com embeddings reais se rodar sem flag)
- Verification query

### 2️⃣ Test de geração de SQL

```bash
python3 scripts/test_sql_generation.py
```

Mostra exatamente como fica o SQL INSERT que vai pro Supabase MCP.

### 3️⃣ Em produção (quando novos KEs chegarem)

1. **Discovery via Supabase MCP:**
   ```sql
   SELECT ke.ke_codigo, ke.descricao
   FROM public.knowledge_extractions ke
   LEFT JOIN public.ke_embeddings emb USING(ke_codigo)
   WHERE emb.ke_codigo IS NULL
   ORDER BY ke.ke_codigo;
   ```

2. **Se houver resultados, colar em Claude Code:**
   ```
   Tenho N KEs sem embeddings:
   [resultado JSON aqui]
   
   Quero rodar indexação paralela. Dispara os shards?
   ```

3. **Claude dispara subagents em paralelo**  
   Cada subagent:
   - Instala `sentence-transformers`
   - Carrega `BAAI/bge-small-en-v1.5`
   - Gera embeddings (384 dims, L2-normalized)
   - Monta SQL INSERT
   - Executa via Supabase MCP
   - Reporta sucesso/falhas

4. **Verification via Supabase MCP:**
   ```sql
   SELECT COUNT(*) AS total_kes,
          COUNT(emb.ke_codigo) AS com_embedding,
          COUNT(*) - COUNT(emb.ke_codigo) AS sem_embedding
   FROM public.knowledge_extractions ke
   LEFT JOIN public.ke_embeddings emb USING(ke_codigo);
   ```
   Esperado: `sem_embedding = 0`

---

## Arquivos

```
scripts/
├── parallel_ke_embeddings_indexer.py  ← Orchestrator (núcleo)
├── run_ke_indexing_demo.py            ← Demo end-to-end
└── test_sql_generation.py             ← Test de SQL

PARALLEL_KE_EMBEDDINGS.md              ← Runbook completo
README_KE_INDEXING.md                  ← Este arquivo (quick start)
```

---

## Regras críticas

- **Modelo imutável:** sempre `BAAI/bge-small-en-v1.5` (384 dims)
- **Normalização:** sempre `normalize_embeddings=True`
- **Conflito:** `ON CONFLICT DO NOTHING` (nunca sobrescrever)
- **Chunk text:** sempre o texto completo usado para gerar embedding

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Download lento do modelo | Primeira execução (~120 MB). Depois fica em cache. |
| "API_KEY_MISSING_OR_INVALID" | Configurar `SUPABASE_API_KEY` em settings.json do Claude Code |
| Tensor mismatch | Alguns KEs têm embeddings de outra dimensão. Deletar e re-indexar. |

---

## Próximos passos

- [ ] Integração com webhook/cron para rodar discovery automático 1x/dia
- [ ] Dashboard de status de indexação (quantos KEs indexados por dia)
- [ ] Suporte para migração de modelo futuro (ex.: `bge-m3` em coluna separada)

---

## Links

- [PARALLEL_KE_EMBEDDINGS.md](./PARALLEL_KE_EMBEDDINGS.md) — Runbook completo (discovery, sharding, dispatch, verify, troubleshooting)
- [Manta Maestro CLAUDE.md](./CLAUDE.md) — Arquitetura de agentes
