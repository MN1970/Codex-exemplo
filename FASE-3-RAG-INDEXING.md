# FASE 3 — RAG Indexing & Parallel Agent Orchestration
## Otimização de Busca com 16 Agentes em Paralelo

**Data:** 2026-07-22  
**Status:** Fase 3 Planning (após Fase 2 completa)  
**Objetivo:** Indexar 947 chunks + orquestrar 16 agentes para busca distribuída

---

## 🎯 O que é Fase 3

**Fase 2:** Coleta documentos → Extrai chunks → Insere em Supabase (RAG básico)  
**Fase 3:** Indexa chunks → Busca distribuída → 16 agentes em paralelo → Responses rápidas

---

## 📊 Arquitetura: 16 Agentes em Paralelo

### 3 Camadas de Agentes

```
┌─────────────────────────────────────────────────────────────┐
│  Maestro Router (Manta 00)                                  │
│  Roteia queries para agentes especializados                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────┐  ┌──────▼───┐  ┌──────▼──────┐
│  5 Agentes │  │ 8 Agentes│  │ 3 Agentes  │
│ Verticais  │  │ Indexação│  │ Validação  │
│ (S6-S10)   │  │ (Paralelo)   │ (Quality)  │
└─────┬──────┘  └──────┬───┘  └──────┬──────┘
      │                │             │
      ├─ Saneamento   ├─ Index-san  ├─ Verify-Confidence
      ├─ Energia      ├─ Index-ene  ├─ Verify-Metadata
      ├─ Portos       ├─ Index-por  └─ Verify-Ranking
      ├─ Aeroportos   ├─ Index-aer
      └─ Barragens    └─ Index-bar

      (S6-S10)       (Search)       (Quality)
```

### Detalhamento dos 16 Agentes

#### **Camada 1: Agentes Verticais (5 agentes)**
Especialistas em cada segmento, acessam RAG próprio:

| Agent | Segment | Acesso RAG | Função |
|-------|---------|-----------|--------|
| agente-saneamento | S8 | san: | Consultas em saneamento |
| agente-energia | S9 | ene: | Consultas em energia |
| agente-portos | S6 | por: | Consultas em portos |
| agente-aeroportos | S7 | aer: | Consultas em aeroportos |
| agente-barragens | S10 | bar: | Consultas em barragens |

#### **Camada 2: Indexadores em Paralelo (8 agentes)**
Criam índices distribuídos:

| Agent | Tipo Index | Responsabilidade |
|-------|-----------|------------------|
| indexer-san-fulltext | Full-Text Search | Text search em san: |
| indexer-ene-fulltext | Full-Text Search | Text search em ene: |
| indexer-por-fulltext | Full-Text Search | Text search em por: |
| indexer-aer-fulltext | Full-Text Search | Text search em aer: |
| indexer-bar-fulltext | Full-Text Search | Text search em bar: |
| indexer-vectors-1 | Vector Embeddings | Chunks 1-200 (similarity) |
| indexer-vectors-2 | Vector Embeddings | Chunks 200-400 |
| indexer-vectors-3 | Vector Embeddings | Chunks 400-600 |

#### **Camada 3: Validadores de Qualidade (3 agentes)**
Verificam e ranqueiam resultados:

| Agent | Função | Valida |
|-------|--------|--------|
| validator-confidence | Score de confiança | confidence_score >= 0.85 |
| validator-metadata | Metadados completos | source_url, document_id, segment |
| validator-ranking | Ranking de relevância | Ordena por relevância para query |

---

## 🔍 Tipos de Indexação

### 1. Full-Text Search (Supabase tsvector)

**O que faz:** Busca textual rápida  
**Usado para:** "Lei 14.026", "saneamento", "esgoto"  
**Performance:** ~50ms para 947 chunks  

```sql
-- Criar índice full-text em rag_chunks
CREATE INDEX idx_rag_chunks_content_fts ON rag_chunks
  USING GIN(to_tsvector('portuguese', content));

-- Query de busca
SELECT * FROM rag_chunks 
WHERE to_tsvector('portuguese', content) @@ 
      plainto_tsquery('portuguese', 'saneamento básico')
LIMIT 10;
```

### 2. Vector Embeddings (Similarity Search)

**O que faz:** Busca semântica baseada em significado  
**Usado para:** Conceitual, contexto, relacionamentos  
**Performance:** ~100ms com pgvector  

```sql
-- Instalar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Adicionar coluna de embeddings
ALTER TABLE rag_chunks ADD COLUMN embedding vector(1536);

-- Criar índice HNSW para busca rápida
CREATE INDEX ON rag_chunks 
USING hnsw (embedding vector_cosine_ops);

-- Query semântica
SELECT * FROM rag_chunks 
ORDER BY embedding <-> 
  '[0.1, 0.2, ..., 0.9]'::vector
LIMIT 10;
```

### 3. Índices Compostos (Segment + Collection)

**O que faz:** Filtra por segmento ou coleção  
**Usado para:** Rotas para agentes especializados  
**Performance:** ~10ms (index lookup)  

```sql
CREATE INDEX idx_rag_collection_segment 
ON rag_chunks(collection_prefix, segment);
```

---

## 🚀 Orchestração com 16 Agentes em Paralelo

### Workflow de Query com Paralelo

```
USER QUERY: "Como tratar água em uma ETA?"
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 1. MAESTRO ROUTER                                   │
│    - Identifica: Saneamento (san:, S8)             │
│    - Distribui para 16 agentes em paralelo         │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌───────────────────────────────────────────────────┐
│ CAMADA 2: INDEXADORES (8 agentes paralelo)       │
│                                                    │
│ ┌──────────────────┐  ┌──────────────────┐       │
│ │ fulltext-san     │  │ vectors-1        │       │
│ │ Busca: "ETA"     │  │ Embed + Sim Search│     │
│ └────────┬─────────┘  └────────┬─────────┘       │
│ ┌──────────────────┐  ┌──────────────────┐       │
│ │ metadata-san     │  │ vectors-2        │       │
│ │ Filter collection│  │ Continua embedding       │
│ └────────┬─────────┘  └────────┬─────────┘       │
│                       ... (vectors-3)            │
└────────────┬──────────────────────────────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌───────────────────────────────────────────────────┐
│ CAMADA 3: VALIDADORES (3 agentes paralelo)       │
│                                                    │
│ ┌─────────────────┐  ┌─────────────────┐        │
│ │ confidence      │  │ metadata        │        │
│ │ Filter score>=  │  │ Check completude        │
│ │ 0.85            │  │                │        │
│ └────────┬────────┘  └────────┬────────┘        │
│ ┌─────────────────────────────────────┐         │
│ │ ranking                             │         │
│ │ Ordena por relevância               │         │
│ └────────┬────────────────────────────┘         │
└─────────┬────────────────────────────────────────┘
          │
    ┌─────▼─────┐
    ▼
┌──────────────────────────────────────┐
│ CAMADA 1: AGENTE ESPECIALIZADO       │
│ agente-saneamento (S8)               │
│                                       │
│ ✅ Top 10 chunks validados           │
│ ✅ Ranqueados por relevância         │
│ ✅ Confiança: 0.92 média             │
│                                       │
│ "A ETA passa por 4 etapas..."        │
└──────────────────────────────────────┘
```

### Paralelização: Max 16 Agentes

```bash
# Configuração de slot pool
MAX_PARALLEL_AGENTS=16
DISTRIBUTED_ACROSS={
  "indexers": 8,      # Indexação distribuída
  "validators": 3,    # Validação paralela
  "specialists": 5    # Agentes verticais (podem ser serial)
}

# Load balancing
LOAD_BALANCE_STRATEGY="round-robin"
AGENT_TIMEOUT=5000  # 5 segundos por agente
RETRY_POLICY="exponential-backoff"
```

---

## 📋 Implementação: 3 Scripts

### Script 1: `rag-indexer-parallel.sh`
Cria índices usando 8 agentes em paralelo

```bash
#!/bin/bash
# Orquestra 8 indexadores
# - 5 para full-text (san, ene, por, aer, bar)
# - 3 para vector embeddings (chunks 1-600)

# Execução:
./scripts/rag-indexer-parallel.sh \
  --chunks-count 947 \
  --vector-dim 1536 \
  --max-parallel 8

# Output:
# ✓ Index san: created (fulltext)
# ✓ Index ene: created (fulltext)
# ... (aer, bar, por)
# ✓ Vector index 1-200 created
# ✓ Vector index 200-400 created
# ✓ Vector index 400-600 created
# ✓ All 8 indexes ready in parallel
```

### Script 2: `rag-query-orchestrator.sh`
Executa queries com 16 agentes em paralelo

```bash
#!/bin/bash
# Orquestra 16 agentes para uma query
# - 8 indexadores (busca)
# - 3 validadores (qualidade)
# - 5 especialistas (resposta)

# Execução:
./scripts/rag-query-orchestrator.sh \
  --query "Como funciona uma ETA?" \
  --collection "san:" \
  --max-parallel 16 \
  --timeout 5s

# Workflow:
# 1. Distribuir query aos 8 indexadores (paralelo)
# 2. Coletar resultados
# 3. Passar aos 3 validadores (paralelo)
# 4. Passar ao agente especializado (serial)
# 5. Retornar resposta

# Output:
# [00:00.000] Maestro: Routing query to san:
# [00:00.050] Indexer-fulltext: Found 15 chunks
# [00:00.080] Indexer-vectors: Found 12 similar chunks
# [00:00.100] Validator-confidence: 15/27 passed (55%)
# [00:00.120] Validator-metadata: 15/15 complete
# [00:00.150] Validator-ranking: Top 10 selected
# [00:00.200] agente-saneamento: Generated response
# RESPONSE: "A ETA passa por..."
```

### Script 3: `agents-rag-indexer-config.json`
Configuração dos 16 agentes

```json
{
  "version": "3.0.0",
  "agents": [
    {
      "id": "indexer-san-fulltext",
      "name": "Indexador Full-Text Saneamento",
      "type": "indexer",
      "tier": "Sonnet",
      "parallelSlot": true,
      "maxParallel": 8,
      "collection": "san:",
      "indexType": "fulltext",
      "priority": "high"
    },
    {
      "id": "indexer-vectors-1",
      "name": "Indexador Vector Embeddings (chunks 1-200)",
      "type": "indexer",
      "tier": "Opus",
      "parallelSlot": true,
      "maxParallel": 8,
      "chunkRange": [1, 200],
      "indexType": "vector",
      "embedding": {
        "model": "text-embedding-3-large",
        "dimension": 1536
      }
    },
    {
      "id": "validator-confidence",
      "name": "Validador Confidence Score",
      "type": "validator",
      "tier": "Sonnet",
      "parallelSlot": true,
      "maxParallel": 3,
      "validatesField": "confidence_score",
      "threshold": 0.85
    },
    {
      "id": "agente-saneamento",
      "name": "Agente Especializado Saneamento",
      "type": "specialist",
      "tier": "Opus",
      "collection": "san:",
      "segment": "S8",
      "ragAccess": "full"
    }
  ],
  "orchestration": {
    "maxParallel": 16,
    "strategy": "round-robin",
    "loadBalancing": {
      "indexers": 8,
      "validators": 3,
      "specialists": 5
    },
    "timeouts": {
      "indexer": "2s",
      "validator": "1s",
      "specialist": "5s"
    }
  }
}
```

---

## 📈 Performance Esperada

### Antes (Sem Índices)

```
Query: "Como funciona uma ETA?"
Tempo: 2000ms
- Scan full table: 1800ms
- Filter: 100ms
- Validate: 100ms
```

### Depois (Com 16 Agentes + Índices)

```
Query: "Como funciona uma ETA?"
Tempo: 200ms
- Indexer fulltext (paralelo): 50ms
- Indexer vectors (paralelo): 50ms
- Validator confidence (paralelo): 25ms
- Validator metadata (paralelo): 25ms
- Validator ranking (paralelo): 25ms
- agente-saneamento: 25ms

Total: ~10x mais rápido
```

### Métrica: Queries/Segundo

| Cenário | QPS | Latência Avg | P99 |
|---------|-----|--------------|-----|
| Sem índices | 0.5 | 2000ms | 5000ms |
| Índices apenas | 5 | 200ms | 500ms |
| 16 agentes paralelo | 50+ | 20ms | 100ms |

---

## 🔄 Integração com Maestro (Manta 00)

Maestro Router já sabe rotear queries:

```
Query menção saneamento → agente-saneamento (S8, san:)
Query menção energia → agente-energia (S9, ene:)
Query menção porto → agente-portos (S6, por:)
Query menção aeroporto → agente-aeroportos (S7, aer:)
Query menção barragem → agente-barragens (S10, bar:)
```

Com Fase 3, Maestro também **orquestra 16 agentes em paralelo**:

```
┌─────────────────────────────────────┐
│ Manta 00 — Maestro Router           │
├─────────────────────────────────────┤
│ Fase 1: Routing                     │
│ └─ Identifica segmento (S6-S10)     │
│                                     │
│ Fase 2: Indexação (16 agentes)      │
│ ├─ 8 Indexadores (paralelo)         │
│ ├─ 3 Validadores (paralelo)         │
│ └─ 5 Especialistas (serial → resposta)│
│                                     │
│ Fase 3: Orquestração Avançada       │
│ ├─ Load balancing                   │
│ ├─ Caching distribuído              │
│ ├─ Métricas em tempo real           │
│ └─ Sincronização com SharePoint     │
└─────────────────────────────────────┘
```

---

## 📊 Checkpoint: Quando Implementar

### Timeline Recomendada

| Fase | Quando | O que | Agentes |
|------|--------|-------|---------|
| **Fase 2** | Semana 1 | Coleta + RAG básico | 0 (manual) |
| **Fase 2** | Semana 2 | Validação em Supabase | 5 (especialistas) |
| **Fase 3** | Semana 3 | Indexação | 8 (indexadores) |
| **Fase 3** | Semana 4 | Validação paralela | 3 (validators) |
| **Fase 3** | Semana 5 | Full orchestration | 16 (todos) |
| **Fase 4** | Semana 6 | SharePoint sync | +2 (sync agents) |

---

## 🎯 Checklist de Implementação

Fase 3 — Quando estiver pronto:

### Semana 1 (Indexação)
- [ ] Criar script `rag-indexer-parallel.sh`
- [ ] Implementar 8 indexadores
  - [ ] 5 full-text (san, ene, por, aer, bar)
  - [ ] 3 vector embeddings (1-200, 200-400, 400-600)
- [ ] Testar criação de índices
- [ ] Documentar índices em Supabase

### Semana 2 (Validadores)
- [ ] Criar 3 validadores em paralelo
  - [ ] validator-confidence (score >= 0.85)
  - [ ] validator-metadata (completude)
  - [ ] validator-ranking (relevância)
- [ ] Integrar com maestro
- [ ] Testar pipeline

### Semana 3 (Orchestração)
- [ ] Criar `rag-query-orchestrator.sh`
- [ ] Implementar round-robin load balancing
- [ ] Testar com 16 agentes simultâneos
- [ ] Validar latência < 200ms
- [ ] Métricas: QPS > 50

---

## 📚 Documentos Relacionados

- **STATUS-FASE-1-E-2.md** — O que foi feito em Fases 1-2
- **FASE-2-EXECUTION-PLAN.md** — Como executar Fase 2
- **FASE-2-RAG-TESTING.md** — Testes (vale para Fase 3 também)
- **MASTER-ROADMAP.md** — Visão geral Fases 1-5

---

## 🚀 Status

**Fase 2:** ✅ Em execução (coleta de docs)  
**Fase 3:** ⏳ Planejado (após Fase 2 com 947 chunks)  
**Implementação:** Começar após validação de 947+ chunks em Supabase

---

**Data:** 2026-07-22  
**Status:** Planejamento Fase 3 (Indexação + 16 Agentes em Paralelo)  
**Próximo:** Executar Fase 2 (coleta documentos até 2026-07-28)
