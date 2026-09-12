# Parallel KE Embeddings Indexer — Manta Maestro

> Infraestrutura para indexação paralela de Knowledge Extractions com embeddings `BAAI/bge-small-en-v1.5` (384d).

**Status da base (2026-07-27):**  
✅ 86 KEs totais, 86 com embeddings, 0 pendentes.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Discovery (sequencial, Supabase MCP)        │
│ → SQL: LEFT JOIN ke_embeddings para achar NULL      │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ Step 2: Sharding (Python, local)                    │
│ → Divide list de KEs em N shards (15-20 cada)       │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ Step 3: Subagent Dispatch (N workers em paralelo)   │
│ → Cada subagent processa 1 shard via SentenceXmer   │
│ → Insere embeddings no Supabase MCP (ogxxgv...)     │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ Step 4: Verification (sequencial, Supabase MCP)     │
│ → Count total vs com_embedding vs sem_embedding     │
└─────────────────────────────────────────────────────┘
```

---

## Uso

### 1. Descobrir KEs sem embedding (manual via Supabase MCP)

```sql
SELECT ke.ke_codigo, ke.descricao
FROM public.knowledge_extractions ke
LEFT JOIN public.ke_embeddings emb ON emb.ke_codigo = ke.ke_codigo
WHERE emb.ke_codigo IS NULL
ORDER BY ke.ke_codigo;
```

Se retornar vazio → **nada a fazer, base está 100% indexada.**

Se retornar N linhas → copie o resultado como JSON e prossiga para o Step 2.

### 2. Gerar shards e prompts de subagent (Python local)

```bash
cd /home/user/Codex-exemplo

python3 scripts/parallel_ke_embeddings_indexer.py
```

Output:
```
╔════════════════════════════════════════════╗
║ Parallel KE Embeddings Indexer Summary     ║
╠════════════════════════════════════════════╣
║ Total KEs pending:      20                 ║
║ Shards created:         2                  ║
║ Total items in shards:  20                 ║
║ ...
```

Copie os prompts de subagent gerados.

### 3. Disparar subagents em paralelo (Claude Code)

**Em uma MESMA mensagem**, faça múltiplas chamadas de Task (ou Agent):

```
[Você envia para Claude Code]

Aqui estão os 2 shards para indexação paralela de KEs. Rode ambos em paralelo:

SHARD 1:
[prompt do shard 1]

SHARD 2:
[prompt do shard 2]
```

Claude Code dispara ambos em paralelo. Cada subagent:
1. Instala `sentence-transformers`
2. Carrega `BAAI/bge-small-en-v1.5`
3. Gera embeddings com `normalize_embeddings=True`
4. Monta INSERT SQL
5. Executa via Supabase MCP (project_id: `ogxxgvgtulrbbppshjie`)
6. Verifica e reporta sucesso/falhas

### 4. Verificação final (Supabase MCP, sequencial)

```sql
SELECT COUNT(*) AS total_kes,
       COUNT(emb.ke_codigo) AS com_embedding,
       COUNT(*) - COUNT(emb.ke_codigo) AS sem_embedding
FROM public.knowledge_extractions ke
LEFT JOIN public.ke_embeddings emb ON emb.ke_codigo = ke.ke_codigo;
```

Esperado: `sem_embedding = 0`.

---

## Regras críticas

1. **Modelo imutável:**  
   Sempre `BAAI/bge-small-en-v1.5` (384 dims, L2-normalized).  
   A coluna `embedding` em `ke_embeddings` é 384-dimensional.

2. **Normalização obrigatória:**  
   ```python
   embeddings = model.encode(texts, normalize_embeddings=True)
   ```
   A coluna usa `cosine` similarity (via `<=>` operator), que assume vetores normalizados.

3. **ON CONFLICT DO NOTHING:**  
   Nunca sobrescrever um embedding existente silenciosamente.  
   Para re-embedar um KE já indexado: `DELETE` explícito, depois `INSERT` novo.

4. **Integridade de texto:**  
   `chunk_text` em `ke_embeddings` = texto completo de `descricao` usado para gerar o embedding.  
   Nunca truncar.

5. **Model field obrigatório:**  
   `model` coluna = sempre a string exata `'BAAI/bge-small-en-v1.5'`.  
   Permite auditoria e migração futura (ex.: se passar para `bge-m3`, inserir em coluna separada).

---

## Troubleshooting

### "API_KEY_MISSING_OR_INVALID" no Supabase MCP

O servidor Supabase MCP não foi configurado com a chave de projeto.

```bash
# Verificar:
echo $SUPABASE_API_KEY

# Se vazio, configurar em Claude Code settings:
# update-config → add env var SUPABASE_API_KEY=<seu-token>
```

### "tensor size mismatch" na verificação

Alguns KEs têm embeddings de outra dimensão (ex.: 1024 de um modelo antigo).

```sql
SELECT ke_codigo, array_length(embedding, 1) AS dims
FROM public.ke_embeddings
WHERE array_length(embedding, 1) != 384;
```

Se encontrar, deletar e re-embedar:
```sql
DELETE FROM public.ke_embeddings WHERE array_length(embedding, 1) != 384;
```

### Timeout no download do modelo

Primeira execução: `sentence-transformers` baixa ~120 MB do HuggingFace Hub.  
Depois fica em cache local (`~/.cache/huggingface/`).

Se timeout → rodar em máquina com conexão melhor ou usar cache local pré-aquecido.

---

## Arquivos

```
/home/user/Codex-exemplo/
├── PARALLEL_KE_EMBEDDINGS.md          # este arquivo
└── scripts/
    └── parallel_ke_embeddings_indexer.py
        └── class KeIndexerOrchestrator
            ├── discover(kes_result) → int
            ├── shard(shard_size=15) → int
            ├── gen_subagent_prompts() → List[(num, prompt)]
            └── summary() → str
```

---

## Histórico

- **2026-07-27:** Infraestrutura implementada. Base em estado ideal (86/86 indexados). Pronto para rodar on-demand quando novos KEs chegarem.

---

## Próximos passos

1. Quando novos KEs forem criados em `public.knowledge_extractions` **sem passar pelo indexador:**
   - Rodar discovery query
   - Gerar shards via orchestrator
   - Disparar subagents em paralelo
   - Verificar e reportar

2. **Integração futura:** script cron ou webhook que roda discovery automático 1x/dia ou após cada bulk insert.

3. **Migração de modelo (futura):** Se passar para `bge-m3` (1024d):
   - Criar coluna `embedding_m3` em `ke_embeddings`
   - Inserir lá (nunca sobrescrever `embedding` existente)
   - Atualizar `match_kes_hybrid` para usar coluna correta
