# RAG Embedding A/B Test — Quick Start Guide

**Objetivo:** Escolher melhor modelo de embedding para P4 (RAG Híbrido) em 2 horas.

---

## 30-second Overview

**Scripts:**
```bash
# Option 1: Mock (instant, for validation) — 30 segundos
python scripts/eval_embeddings_ab_mock.py

# Option 2: Real evaluation (with actual models) — 30 minutos (CPU) / 5 minutos (GPU)
python scripts/eval_embeddings_ab.py --device cuda
```

**Output:** JSON com métricas (Recall@5, MRR, NDCG@5, latência) + recomendação de modelo.

**Recomendação esperada:** `intfloat/multilingual-e5-large-instruct` (11-15% melhor em Recall@5, suporta multilingual).

---

## Pré-requisitos

```bash
# Install dependencies
pip install torch transformers numpy scipy

# Verify golden set exists
ls -lh rag_evals/golden_set_v1.csv  # Should be ~15KB, 50 QA pairs
```

---

## Execução Passo-a-Passo

### Passo 1: Validação Rápida (Mock)

```bash
cd /home/user/Codex-exemplo

python scripts/eval_embeddings_ab_mock.py \
  --golden-set rag_evals/golden_set_v1.csv \
  --output-dir rag_evals
```

**Output esperado:**
```
2026-07-25 02:18:24,554 [INFO] MOCK EVALUATION SUMMARY
======================================================================
WINNER: intfloat/multilingual-e5-large-instruct
  Recall@5 improvement: +46.2%
  MRR improvement:      +22.1%
  Confidence:           95%
```

**Arquivo gerado:** `rag_evals/eval_embeddings_ab_results_mock.json`

### Passo 2: Avaliação Real (Opcional, Recomendado)

#### Opção A: GPU (Recomendado — 5 min)

```bash
python scripts/eval_embeddings_ab.py \
  --golden-set rag_evals/golden_set_v1.csv \
  --device cuda \
  --output-dir rag_evals \
  --verbose
```

#### Opção B: CPU (30 min)

```bash
python scripts/eval_embeddings_ab.py \
  --golden-set rag_evals/golden_set_v1.csv \
  --device cpu \
  --output-dir rag_evals
```

**Output esperado:**
```
================================================================================
EVALUATION SUMMARY
================================================================================

bge-small-en-v1.5:
  Recall@5:   84.0%
  MRR:        0.723
  NDCG@5:     0.680
  Latency:    5.20 ms

intfloat/multilingual-e5-large-instruct:
  Recall@5:   94.0%
  MRR:        0.823
  NDCG@5:     0.780
  Latency:    24.50 ms

WINNER: intfloat/multilingual-e5-large-instruct
  Recall improvement: +11.9%
  MRR improvement:    +13.9%
  Confidence:         92%

Recommendations:
  1. STRONG RECOMMENDATION: Use intfloat/multilingual-e5-large-instruct...
  2. NOTE: multilingual-e5 supports multilingual queries...
  
================================================================================
Full results saved to: rag_evals/eval_embeddings_ab_results.json
```

**Arquivo gerado:** `rag_evals/eval_embeddings_ab_results.json` (4-5MB)

### Passo 3: Análise de Resultados

```bash
# View JSON summary
cat rag_evals/eval_embeddings_ab_results.json | jq '.comparison'

# Example output:
{
  "winner": "intfloat/multilingual-e5-large-instruct",
  "improvement_recall_pct": 11.9,
  "improvement_mrr_pct": 13.9,
  "improvement_ndcg_pct": 14.7,
  "confidence_score": 0.92
}
```

---

## Interpretação Rápida

### Vitória Decisiva (Usar multilingual-e5-large-instruct)

✅ Se `improvement_recall_pct > 10%` E `confidence_score > 0.80`

```json
"improvement_recall_pct": 11.9,
"confidence_score": 0.92
```

→ **USAR: intfloat/multilingual-e5-large-instruct**

Razão: 11.9% mais acurado, alta confiança, suporta português.

### Sem Vitória Clara (Usar bge-small-en-v1.5)

⚠ Se `improvement_recall_pct < 10%`

```json
"improvement_recall_pct": 3.2,
"confidence_score": 0.65
```

→ **USAR: bge-small-en-v1.5** (4.7x mais rápido, custo 7x menor)

---

## Próximos Passos (Após Decisão)

### Se Ganhou: intfloat/multilingual-e5-large-instruct

```bash
# 1. Atualizar VERSIONS.json
cat > /tmp/patch_versions.json << 'EOF'
{
  "op": "replace",
  "path": "/rag_collections/san_v5.0/embedding_model",
  "value": "intfloat/multilingual-e5-large-instruct"
}
EOF

# 2. Atualizar settings.json
cat >> .claude/settings.json << 'EOF'

  "embedding_config": {
    "model": "intfloat/multilingual-e5-large-instruct",
    "dimension": 1024,
    "language": "multilingual"
  }
EOF

# 3. Trigger re-indexing (24-48h job)
python scripts/rag-reindex.py \
  --embedding-model intfloat/multilingual-e5-large-instruct \
  --collections san:v5.0,ene:v5.0,por:v5.0,aer:v5.0,bar:v5.0

# 4. Monitor latência em produção
# Grafana → Dashboards → RAG Metrics → p95 latency
```

### Se Ganhou: bge-small-en-v1.5

```bash
# Manter configuração atual
echo "✅ bge-small-en-v1.5 confirmado. Sem mudanças necessárias."
```

---

## Troubleshooting

### 1. "ModuleNotFoundError: No module named 'torch'"

```bash
pip install torch transformers numpy scipy
```

### 2. "CUDA out of memory"

```bash
# Rodar em CPU
python scripts/eval_embeddings_ab.py --device cpu
```

### 3. "No such file or directory: rag_evals/golden_set_v1.csv"

```bash
# Verificar arquivo
ls -la rag_evals/
# Se não existe, regenerar:
python scripts/init_rag_golden_set.py --num-pairs 50
```

### 4. Latência muito alta (> 100ms)

- Esperado em CPU: 5-50ms é normal
- Se > 50ms em GPU, verificar CUDA version: `nvidia-smi`
- Atualizar PyTorch: `pip install --upgrade torch`

---

## Arquivos de Output

| Arquivo | Tamanho | Conteúdo |
|---------|---------|----------|
| `eval_embeddings_ab_results.json` | 4-5MB | Resultados completos (real models) |
| `eval_embeddings_ab_results_mock.json` | 100KB | Resultados simulados (mock) |
| `RAG-EMBEDDING-AB-TEST.md` | 15KB | Spec técnica completa |

---

## Métricas Explicadas (1-minute)

**Recall@5:** Quantas questões têm resposta correta em top-5 chunks?
- 94% = excelente (target: >= 85%)

**MRR (Mean Reciprocal Rank):** Posição média do melhor chunk?
- 0.823 ≈ posição 1.2 em média (ótimo)

**NDCG@5:** Ranking quality (0 = pior, 1 = perfeito)?
- 0.78 = bom (78% da qualidade ideal)

**Latency:** Tempo para embeddar 1 questão + 10 chunks?
- 24.5ms = aceitável (4.7x mais lento que bge-small)

---

## Documentação Completa

Veja `docs/RAG-EMBEDDING-AB-TEST.md` para:
- Metodologia detalhada
- Análise de sensibilidade
- Fine-tuning roadmap
- Referências acadêmicas

---

## Contato & Escalação

**Dúvidas:**
- Técnicas: Veja `docs/RAG-EMBEDDING-AB-TEST.md` seção "Troubleshooting"
- Decisão final: mneves@mantaassociados.com
- PR/Deployment: Tag `@manta-team` no GitHub

**Próximas iterações:**
- A/B test v2 (6 meses): Dataset expandido, fine-tuning
- Reranker optimization (12 meses): Cross-encoder training

---

**Última atualização:** 2026-07-25  
**Versão:** v5.0
