# RAG Embedding A/B Test — P4 Specification

**Version:** v5.0  
**Date:** 2026-07-25  
**Author:** Evaluation Framework (Manta Maestro)  
**Status:** Ready for Execution

---

## Objetivo

Escolher melhor embedding model para P4 (RAG Híbrido: BM25 + Embedding + Reranker) da arquitetura Manta v5.0.

Dois candidatos:
1. **bge-small-en-v1.5** (384d, rápido, English-focused)
2. **intfloat/multilingual-e5-large-instruct** (1024d, multilíngue, Portuguese-native)

**Critério de vitória:** Winner deve ter Recall@5 > 10% melhor que competidor.

---

## Metodologia

### Dataset

**Golden Set:** 50 QA pairs (rag_evals/golden_set_v1.csv)

Distribuição por segmento:
- **Saneamento (S8):** 10 QAs (AySA focus) — PRIORIDADE
- **Energia (S9):** 10 QAs (ANEEL focus)
- **Portos (S6):** 10 QAs
- **Aeroportos (S7):** 10 QAs
- **Barragens (S10):** 10 QAs

Dificuldades:
- Easy (7 pairs): Conceitos básicos, regulação
- Medium (25 pairs): Cálculos, design, dimensionamento
- Hard (18 pairs): Técnicas avançadas, análise complexa

### Processo de Avaliação

Para cada QA pair (questão + resposta esperada):

1. **Geração de Mock Chunks**
   - Golden chunk: resposta esperada (chunk_golden)
   - 9 distrator chunks: baixa relevância semântica
   - Total: 10 chunks por QA (simula retrieval size típico)

2. **Embedding**
   - Questão: `q_emb = embed_model(question)`
   - Chunks: `chunk_embs = [embed_model(c) for c in chunks]`
   - Ambos modelos processam mesma entrada

3. **Ranking**
   - Similaridade cosine: `sim(q, c_i) = 1 - cosine_distance(q_emb, c_emb_i)`
   - Ranking descendente (top-1 = melhor match)
   - Avaliar posição do golden chunk

4. **Métricas por QA**

   **Recall@5:** Binária (1 se golden em top-5, 0 caso contrário)
   ```
   Recall@5(qa) = 1 if rank(golden_chunk) <= 5 else 0
   ```

   **RRR (Reciprocal Rank):** Posição do golden chunk
   ```
   RRR(qa) = 1 / rank if rank <= 5 else 0
   ```

   **NDCG@5 (Normalized Discounted Cumulative Gain)**
   ```
   DCG@5 = Σ(i=1 to 5) [1 / log₂(i+1)] × rel(i)
   rel(i) = 1 if rank_i == golden_chunk else 0
   IDCG = 1 / log₂(2) = 1.0 (ideal: golden em posição 1)
   NDCG@5 = DCG@5 / IDCG
   ```

### Agregação de Métricas

Para ambos os modelos:

1. **Recall@5 (macro)**
   ```
   Recall@5 = (n_qa_with_golden_in_top5) / n_total_qa
   Escala: 0.0 — 1.0
   ```

2. **MRR (Mean Reciprocal Rank)**
   ```
   MRR = avg([RRR(qa_1), RRR(qa_2), ..., RRR(qa_50)])
   Escala: 0.0 — 1.0
   ```

3. **NDCG@5 (macro)**
   ```
   NDCG@5 = avg([NDCG@5(qa_1), ..., NDCG@5(qa_50)])
   Escala: 0.0 — 1.0
   ```

4. **Latência (ms)**
   ```
   latency_ms = avg([embedding_time(q_i + chunks_i) for all QAs])
   Captura tempo real de embedding
   ```

### Decisão de Vitória

**Condição primária:** Recall@5 improvement > 10%
```
improvement_recall = (Recall@5_winner - Recall@5_loser) / Recall@5_loser × 100%

IF improvement_recall > 10%:
   winner = model com maior Recall@5
ELIF improvement_mrr > 5% AND improvement_ndcg > 5%:
   winner = model com maior MRR (e NDCG como tiebreaker)
ELSE:
   winner = model com maior Recall@5 (tiebreaker)
```

**Confidence Score:**
```
IF improvement_recall > 10%:
   confidence = min(0.95, 0.50 + improvement_recall / 100)
ELIF improvement_recall > 5%:
   confidence = 0.65
ELSE:
   confidence = 0.55
```

---

## Execução

### Ambiente

**Requisitos:**
- Python 3.10+
- PyTorch (`torch >= 2.0`)
- Transformers (`transformers >= 4.30`)
- NumPy, SciPy
- ~6GB RAM (para carregamento simultâneo dos dois modelos)
- CUDA (opcional, mas recomendado para latência)

**Instalação:**
```bash
pip install torch transformers numpy scipy
```

### Opção 1: A/B Test Completo (Real Models)

Carrega ambos os embeddings e executa evaluation real (recomendado para decisão final):

```bash
# Rodas completos (CPU, ~30min)
python scripts/eval_embeddings_ab.py \
  --golden-set rag_evals/golden_set_v1.csv \
  --device cpu \
  --output-dir rag_evals

# Com CUDA (GPU, ~5min)
python scripts/eval_embeddings_ab.py \
  --device cuda \
  --output-dir rag_evals

# Verbose
python scripts/eval_embeddings_ab.py \
  --verbose \
  --output-dir rag_evals
```

**Output:**
- `rag_evals/eval_embeddings_ab_results.json` — Resultados completos (métricas + detalhes QA)

### Opção 2: Mock Test (Simulado)

Roda avaliação SEM carregar modelos reais (útil para CI/CD, validação rápida):

```bash
python scripts/eval_embeddings_ab_mock.py \
  --golden-set rag_evals/golden_set_v1.csv \
  --output-dir rag_evals
```

**Output:**
- `rag_evals/eval_embeddings_ab_results_mock.json` — Métricas simuladas (30s)

---

## Interpretação de Resultados

### Exemplo de Saída Real

```json
{
  "evaluation_metadata": {
    "timestamp": "2026-07-25T18:30:00Z",
    "golden_set_size": 50,
    "evaluation_type": "A/B test (P4 RAG embedding models)"
  },
  "models": {
    "bge_small": {
      "name": "bge-small-en-v1.5",
      "dimension": 384,
      "latency_ms": 5.2,
      "recall_at_5": 0.84,
      "mrr": 0.72,
      "ndcg_at_5": 0.68
    },
    "e5_large": {
      "name": "intfloat/multilingual-e5-large-instruct",
      "dimension": 1024,
      "latency_ms": 24.5,
      "recall_at_5": 0.94,
      "mrr": 0.82,
      "ndcg_at_5": 0.78
    }
  },
  "comparison": {
    "winner": "intfloat/multilingual-e5-large-instruct",
    "improvement_recall_pct": 11.9,
    "improvement_mrr_pct": 13.9,
    "improvement_ndcg_pct": 14.7,
    "confidence_score": 0.92
  },
  "qa_details": [
    {
      "qa_id": "qa_001",
      "question": "Qual método para calcular golpe de aríete...",
      "bge_small": {"rank": 2, "in_top5": true, "score": 0.87},
      "e5_large": {"rank": 1, "in_top5": true, "score": 0.94}
    }
    ...
  ],
  "recommendations": [
    "STRONG RECOMMENDATION: Use intfloat/multilingual-e5-large-instruct...",
    "NOTE: e5-large supports multilingual queries...",
    ...
  ]
}
```

### Interpretação por Métrica

**Recall@5 = 0.94**
- 94% das 50 questões têm resposta correta em top-5 chunks
- ✅ Excelente (target >= 85%)

**MRR = 0.82**
- Posição média do melhor chunk: 1 / 0.82 ≈ 1.22
- ✅ Muito bom (golden chunk está em ~1.2ª posição em média)

**NDCG@5 = 0.78**
- 78% da relevância ideal (máximo 1.0 é golden em posição 1)
- ✅ Bom ranking

**Latency = 24.5ms**
- Tempo para embeddar 1 questão + 10 chunks
- ⚠ Aceitável mas 4.7x mais lento que bge-small

**Confidence = 0.92**
- 92% certeza de que e5-large é melhor
- ✅ Alta confiança (threshold >= 0.70)

---

## Decisão & Próximos Passos

### Se multilingual-e5-large-instruct Vencer

**Razões:**
- Recall@5 11-15% melhor
- Suporta multilingual (português, espanhol)
- Melhor para queries em português natural

**Ações:**
1. ✅ Atualizar VERSIONS.json:
   ```json
   "rag_collections": {
     "san_v5.0": {
       "embedding_model": "intfloat/multilingual-e5-large-instruct",
       "dimension": 1024
     }
   }
   ```

2. ✅ Atualizar .claude/settings.json:
   ```json
   {
     "embedding_strategy": "intfloat/multilingual-e5-large-instruct",
     "rag_p4_reranker": true
   }
   ```

3. ✅ Re-index RAG collections (24-48h):
   ```bash
   python scripts/rag-reindex.py \
     --embedding-model intfloat/multilingual-e5-large-instruct \
     --collections san:v5.0,ene:v5.0,por:v5.0,aer:v5.0,bar:v5.0
   ```

4. ✅ Monitorar latência em produção:
   - Grafana dashboard: `rag_p4_embedding_latency_p50/p95/p99`
   - Alert se latência > 100ms (16x overhead)

5. ✅ Coletar feedback de usuários (2 semanas):
   - Query satisfaction scores
   - Feedback loop (R9) treina embedding base em queries high-rating

### Se bge-small-en-v1.5 Vencer ou Empatar

**Razões:**
- 4.7x mais rápido
- Custo computacional 7x menor
- Suficiente para queries em inglês puro

**Ações:**
1. ✅ Manter bge-small como padrão
2. ✅ Considerar bge-small se latência crítica
3. ⚠ Reavaliar em 6 meses com dataset multilíngue expandido

---

## Análise de Sensibilidade

### Por Dificuldade

Executar análise pós-eval:

```bash
python -c "
import json
with open('rag_evals/eval_embeddings_ab_results.json') as f:
    results = json.load(f)['qa_details']
    
for difficulty in ['easy', 'medium', 'hard']:
    filtered = [r for r in results if r.get('difficulty') == difficulty]
    recall_v1 = sum(1 for r in filtered if r['bge_small']['in_top5']) / len(filtered) if filtered else 0
    recall_v2 = sum(1 for r in filtered if r['e5_large']['in_top5']) / len(filtered) if filtered else 0
    improvement = ((recall_v2 - recall_v1) / recall_v1 * 100) if recall_v1 > 0 else 0
    
    print(f'{difficulty:8} | bge: {recall_v1:.0%} | e5: {recall_v2:.0%} | improvement: {improvement:+.1f}%')
"
```

**Interpretação:**
- Se improvement maior em "hard", multilingual-e5 é melhor para problemas complexos
- Se improvement concentrado em "easy", pode ser artefato de dataset

### Por Segmento

Verificar performance por agent (S6-S10):

```bash
grep -A 5 '"agent_id"' rag_evals/eval_embeddings_ab_results.json | head -50
```

**Interpretação:**
- Se e5-large muito melhor em S8 (saneamento/AySA), recomenda-se usar nela
- Se performance uniforme, usar globalmente

---

## Troubleshooting

### GPU Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solução:**
```bash
# Rodar em CPU
python scripts/eval_embeddings_ab.py --device cpu

# Ou reduzir batch size (internal)
# Edit eval_embeddings_ab.py: EmbeddingModel.embed batch_size
```

### Models Não Baixam

```
EnvironmentError: [Errno 2] No such file or directory
```

**Solução:**
```bash
# Download manual
huggingface-cli download BAAI/bge-small-en-v1.5
huggingface-cli download intfloat/multilingual-e5-large-instruct

# Ou set cache dir
export HF_HOME=/path/to/huggingface_cache
```

### Latência Anormalmente Alta

> Latency 50ms+ em CPU é esperado

**Se > 100ms:**
- Verificar sistema (CPU load, memória disponível)
- Usar GPU
- Verificar versão PyTorch (update para 2.0+)

---

## Próximas Iterações

### A/B Test v2 (6 meses)

- Dataset expandido: 200+ QAs (segmentos + multilingual)
- Fine-tuning embedding em Manta queries
- Comparar cross-encoder reranker (R6)

### Fine-tuning Embedding (9 meses)

- Coletar high-rating queries (R9 feedback loop)
- Fine-tune multilingual-e5 em Manta domain
- Alcançar 96%+ Recall@5

### Reranker Optimization (12 meses)

- Treinar cross-encoder em labeled Manta queries
- Integrar R6 (reranker) com embedding
- Target: Recall@5 > 98%, MRR > 0.90

---

## Referências

- CLAUDE.md v5.0 — P4 RAG Híbrido
- BGE-small documentation: https://github.com/FlagOpen/FlagEmbedding
- Multilingual-e5: https://github.com/microsoft/unilm/tree/master/e5
- Evaluation metrics: https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)

---

**Manutenedor:** mneves@mantaassociados.com  
**Versão:** v5.0  
**Última atualização:** 2026-07-25
