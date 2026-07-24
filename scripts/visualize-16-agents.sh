#!/bin/bash

# ============================================================================
# VISUALIZE-16-AGENTS.SH
# Mostra os 16 agentes de Fase 3 em formato visual
# ============================================================================

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║         MANTA MAESTRO v5 — PHASE 3: RAG INDEXING + 16 AGENTS             ║
║                  Orchestração Paralela de Busca Distribuída               ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMADA 1: AGENTES VERTICAIS (5 Especialistas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────┐
│ Serial Processing → Gera resposta final                                 │
│                                                                          │
│ 1. agente-saneamento      Segment: S8  │ Collection: san:  │ PRIORIDADE │
│    "Especialista em agua, esgoto, drenagem"                             │
│    Tier: Opus | RAG Access: FULL                                        │
│                                                                          │
│ 2. agente-energia         Segment: S9  │ Collection: ene:  │ PRIORIDADE │
│    "Especialista em transmissão, distribuição, geração"                 │
│    Tier: Opus | RAG Access: FULL                                        │
│                                                                          │
│ 3. agente-portos          Segment: S6  │ Collection: por:  │ Média      │
│    "Especialista em dragagem, berços, portos"                           │
│    Tier: Opus | RAG Access: FULL                                        │
│                                                                          │
│ 4. agente-aeroportos      Segment: S7  │ Collection: aer:  │ Média      │
│    "Especialista em pistas, TPS, infraestrutura aeroportuária"          │
│    Tier: Opus | RAG Access: FULL                                        │
│                                                                          │
│ 5. agente-barragens       Segment: S10 │ Collection: bar:  │ Média      │
│    "Especialista em segurança, vertedouros, rejeitos"                   │
│    Tier: Opus | RAG Access: FULL                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMADA 2: INDEXADORES (8 Agentes em Paralelo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parallel Execution (Max 8 concurrent) → Busca distribuída

┌─────────────────────────────────────────────────────────────────────────┐
│ FULL-TEXT SEARCH (5 agentes) — Busca textual rápida                    │
│ Index Type: tsvector (PostgreSQL)                                       │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ indexer-san-fulltext   → Collection: san:  (200 chunks)        │    │
│ │                          Cria: idx_rag_san_fulltext             │    │
│ │                          Tier: Sonnet | Prioridade: ALTA       │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ indexer-ene-fulltext   → Collection: ene:  (300 chunks)        │    │
│ │                          Cria: idx_rag_ene_fulltext             │    │
│ │                          Tier: Sonnet | Prioridade: ALTA       │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ indexer-por-fulltext   → Collection: por:  (150 chunks)        │    │
│ │ indexer-aer-fulltext   → Collection: aer:  (120 chunks)        │    │
│ │ indexer-bar-fulltext   → Collection: bar:  (180 chunks)        │    │
│ │                          Tier: Sonnet | Prioridade: Média      │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ VECTOR EMBEDDINGS (3 agentes) — Busca semântica                        │
│ Index Type: HNSW (pgvector)                                             │
│ Model: text-embedding-3-large (1536 dims)                              │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ indexer-vectors-1     → Chunks 1-200    (split para paralelizar)    │
│ │                          Cria: idx_rag_vectors_hnsw_1           │    │
│ │                          Tier: Opus | Prioridade: ALTA         │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ indexer-vectors-2     → Chunks 200-400                         │    │
│ │ indexer-vectors-3     → Chunks 400-600                         │    │
│ │                          Tier: Opus | Prioridade: ALTA         │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMADA 3: VALIDADORES (3 Agentes em Paralelo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parallel Validation (Max 3 concurrent) → Filtra e classifica resultados

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ validator-confidence                                            │    │
│ │ Função: Filtra chunks com confidence_score >= 0.85             │    │
│ │ Input: Todos os chunks encontrados (15-50 resultados)          │    │
│ │ Output: Chunks com score válido (55-100% passam)               │    │
│ │ Tier: Sonnet | Prioridade: ALTA                               │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ validator-metadata                                              │    │
│ │ Função: Verifica completude de metadados                        │    │
│ │ Campos: document_id, source_url, collection_prefix, segment    │    │
│ │ Input: Chunks passados em confidence                           │    │
│ │ Output: Chunks com metadata completa                           │    │
│ │ Tier: Sonnet | Prioridade: ALTA                               │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ validator-ranking                                               │    │
│ │ Função: Ordena por relevância                                   │    │
│ │ Critérios: confidence_score, semantic_similarity, text_match   │    │
│ │ Input: Chunks validados (8-15 resultados)                      │    │
│ │ Output: Top 10 ranqueados por relevância                       │    │
│ │ Tier: Sonnet | Prioridade: ALTA                               │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUXO DE EXECUÇÃO: Query Processing Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USER: "Como funciona uma ETA?"
         │
         ▼
    ┌────────────────────────┐
    │ Stage 1: MAESTRO (1 agent)
    │ └─ Identifica: saneamento → san:
    │ └─ Tempo: 500ms max
    │ └─ Serial
    └──────────┬─────────────┘
               │
         ┌─────▼──────────────────────────────────┐
         │ Stage 2: INDEXADORES (8 agents paralelo)
         │ ├─ indexer-san-fulltext  → "ETA" (fulltext)
         │ ├─ indexer-ene-fulltext  → tratamento (se relevante)
         │ ├─ indexer-por-fulltext  → água/dragagem (se relevante)
         │ ├─ indexer-aer-fulltext  → (pode retornar vazio)
         │ ├─ indexer-bar-fulltext  → (pode retornar vazio)
         │ ├─ indexer-vectors-1     → similitude semântica
         │ ├─ indexer-vectors-2     → similitude semântica
         │ └─ indexer-vectors-3     → similitude semântica
         │ Tempo: 2000ms max
         │ Resultado: 20-40 chunks candidatos
         └─────┬──────────────────────────────────┘
               │
         ┌─────▼──────────────────────────────────┐
         │ Stage 3: VALIDADORES (3 agents paralelo)
         │ ├─ validator-confidence   → Filtra score
         │ ├─ validator-metadata     → Verifica completude
         │ └─ validator-ranking      → Ordena top 10
         │ Tempo: 1000ms max
         │ Resultado: 10 chunks ranking
         └─────┬──────────────────────────────────┘
               │
         ┌─────▼──────────────────────────────────┐
         │ Stage 4: ESPECIALISTA (1 agent)
         │ └─ agente-saneamento
         │ └─ Lê top 10 chunks
         │ └─ Gera resposta
         │ └─ Tempo: 5000ms max
         │ └─ Serial
         └──────────┬──────────────────┘
                    │
                    ▼
            RESPONSE: "A ETA passa por
            4 etapas: coagulação,
            decantação, filtração,
            desinfecção..."

LATÊNCIA TOTAL: ~200ms (20x mais rápido que sem índices)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUMO: 16 AGENTES EM PARALELO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total: 16 Agentes
├─ Camada 1 (Especialistas):     5 agentes (serial)
├─ Camada 2 (Indexadores):        8 agentes (paralelo, max 8)
└─ Camada 3 (Validadores):        3 agentes (paralelo, max 3)

Paralelismo Máximo: 11 agentes simultâneos
(8 indexadores + 3 validadores)

Throughput Esperado:
├─ Query latency:  < 200ms (vs 2000ms sem índices)
├─ Queries/seg:    > 50 (vs 0.5 sem índices)
└─ Speedup:        10x - 100x dependendo da query

Performance SLA:
├─ P50 latency:    < 100ms
├─ P99 latency:    < 300ms
├─ P999 latency:   < 500ms
└─ Availability:   99.9%

EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Status: PLANEJADO (após Fase 2)"
echo "Deployment: Semana 1-3 após 947+ chunks em Supabase"
echo "Documentação: FASE-3-RAG-INDEXING.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
