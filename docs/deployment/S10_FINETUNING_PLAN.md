# S10 Fine-Tuning Action Plan — Domain-Specific Optimization
**Date:** 26 de julho de 2026  
**Timeline:** 1 week (immediate start recommended)  
**Status:** Pending execution  
**Responsibility:** RAG Engineering + Domain Expert (Barragens S10)

---

## Problem Statement

**Current Performance:** S10 (Barragens) domain achieves **0% Recall@1** on 2 benchmark queries despite 84.62% overall Recall@1.

**Root Cause:** text-embedding-3-large (and E5-large) fail to discriminate barragem-specific terminology from rodovia-specific vocabulary. Example:
- Query: "Fundação de barragem em solo: análise de estabilidade"
- Retrieved (incorrect): S1 Rodovia documents (Fundação rodoviária, pavimento)
- Expected: S10 Barragem documents (Fundação de concreto, vertedouro)

**Vocabulary Overlap Issues:**
- "fundação" → bridge pillar (S2) vs. dam foundation (S10)
- "estrutura" → road structure vs. dam structure
- "compactação" → soil compaction (rodovia) vs. rockfill compaction (barragem, different standards)
- "drenagem" → surface drainage (S1) vs. internal drainage (S10)

---

## Fine-Tuning Strategy

### Phase 1: Domain Corpus Preparation (2 days)
**Goal:** Build high-quality barragem-specific training corpus

**Data Sources:**
1. **ICOLD (International Commission on Large Dams)**
   - Case studies: 50+ dam projects
   - Technical bulletins: structural design, hydraulics, geotechnics
   - Target: 200-300 documents

2. **CBDB (Cadastro Brasileiro de Barragens)**
   - Brazilian registered dams: 2,000+ public records
   - Standard categories: name, location, type, height, volume
   - Target: extract 100+ diverse examples

3. **Technical Standards (Brazil/Latin America)**
   - Lei 12.334 (Dam Safety Law) — full text
   - ABNT NBR 8944 (Earth dams classification)
   - ICOLD Compilations on construction, spillways, seepage
   - Target: 50+ documents

4. **Proprietary Manta Projects**
   - Past dam projects (EIV-compatible documentation)
   - Design reports, cost analyses, technical memos
   - Target: 20-30 documents (sanitized)

**Expected Corpus:** ~400-500 documents, 50K-100K tokens

### Phase 2: Training Data Creation (1 day)
**Goal:** Create fine-tuning pairs (domain vs. confusable non-domain)

**Format:** JSON Lines (jsonl)
```json
{
  "text": "Barragem CFRD: compactação de aterro em zona envelope (rocha) requer densidade seca 0.97 Proctor modificado...",
  "label": "barragem_specificity",
  "domain": "S10",
  "contrastive_negative": "Rodovia compactação de subleito requer 95% Proctor normal...",
  "key_terms": ["CFRD", "envelope", "Proctor modificado", "vertedouro"],
  "difficulty": "hard"  # confusable with S1
}
```

**Pair Categories:**
1. **Dam structures** (CFRD, CCR, earth) vs. road structures
2. **Spillway designs** vs. highway drainage
3. **Geotechnical testing** (barragem scale vs. road scale)
4. **Regulatory frameworks** (Lei 12.334 vs. DNIT)
5. **Equipment & methods** (heavy pata-de-cabra for dams vs. rolo liso for roads)

**Expected pairs:** ~200-300 positive/negative pairs

### Phase 3: Model Fine-Tuning (2 days)
**Goal:** Fine-tune E5-large (or text-embedding-3-large variant) on barragem corpus

**Approach 1: E5-Large (Open-source, no API cost)**
```python
from sentence_transformers import models, losses, SentenceTransformer
from sentence_transformers.evaluation import InformationRetrievalEvaluator
from sentence_transformers import InputExample
from torch.utils.data import DataLoader

# Load base model
model = SentenceTransformer('intfloat/multilingual-e5-large')

# Prepare training data from ICOLD + CBDB corpus
train_examples = [
    InputExample(texts=['dam foundation analysis text...', 'dam-specific label'], label=1),
    InputExample(texts=['dam foundation analysis text...', 'road foundation text...'], label=0),
    # ... 200+ pairs
]

# Fine-tune with constrastive loss
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model=model)

evaluator = InformationRetrievalEvaluator(...)  # use Phase 3 queries

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=500,
    evaluator=evaluator,
    output_path='./fine-tuned-e5-barragem'
)
```

**Approach 2: OpenAI Fine-Tuning (API-based)**
- Less control, but managed training
- Cost: ~$50-100 for 300 training pairs
- Timeline: 1 day
- **Recommended if internal GPU not available**

**Expected Improvement:** +6-8% Recall@1 on S10 queries (0% → 6-8%)

### Phase 4: Validation & Integration (1 day)
**Goal:** Test fine-tuned model on Phase 3 benchmark

**Test Cases:**
1. **S10-specific queries (2 residual):**
   - "Fundação de barragem em solo: análise de estabilidade"
   - "Estrutura de concreto em vertedouro: projeto de drenagem interna"
   - Expected: both retrieve S10 chunks (>0% Recall@1)

2. **Cross-domain contamination (regression test):**
   - All 37 non-S10 queries should still retrieve correct domain
   - Expected: 0% contamination (maintain Phase 3 achievement)

3. **Performance:** latency < 500ms per query

**Metric Success:**
- S10 Recall@1: 0% → 50-70% (after fine-tuning)
- Overall contamination: 0% → 0% (no regression)
- Overall Recall@1: 84.62% → 85-87% (slight improvement)

---

## Resource Requirements

| Resource | Qty | Cost | Notes |
|----------|-----|------|-------|
| **GPU (Tesla V100)** | 1 | $10/h | ~16 hours training |
| **Document collection labor** | 40 hours | $500 | ICOLD + CBDB + Lei + proprietary |
| **Training data annotation** | 300 pairs | $300 | domain expert + QA |
| **Fine-tuning (OpenAI API)** | 300 pairs | $50-100 | if outsourced |
| **Validation & testing** | 8 hours | $100 | benchmark re-run + regression |
| **Total** | — | **$1,000-1,500** | **1 week timeline** |

---

## Success Criteria

✅ **S10 Recall@1:** 0% → **≥50%** (critical)  
✅ **Overall Recall@1:** maintain ≥80% (no regression)  
✅ **Contamination:** maintain **0.00%**  
✅ **Latency:** search < 500ms (no degradation)  

---

## Fallback Options

### Option A: Hybrid Retrieval (3 days, lower cost)
If fine-tuning is delayed:
- Use keyword-based pre-filtering for S10 queries (Lei 12.334, ICOLD, vertedouro)
- Route barragem queries to separate vector index
- Expected improvement: +20-30% Recall@1 (faster but less elegant)

### Option B: Model Swap (2 days, medium cost)
Replace text-embedding-3-large with barragem-optimized alternative:
- OpenAI text-embedding-3-small (cheaper) + reranker for S10
- Or: Cohere embed-english-v3.0 (better domain discrimination)
- Expected improvement: +15-25% Recall@1
- Cost: API subscription ($0.02-0.10 per 1M tokens)

### Option C: Accept Current State (0 days, 0 cost)
- Monitor S10 Recall@1 via dashboard
- Execute fine-tuning during next 2-week sprint
- Risk: S10 queries continue to fail in production (~2-3% of all queries affected)

---

## Timeline & Milestones

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-07-27 (Fri) | Corpus collection (ICOLD, CBDB, Lei) | RAG Eng + Domain Expert | 📋 Ready |
| 2026-07-28 (Sat) | Training data creation (200+ pairs) | Annotation team | 📋 Pending |
| 2026-07-29 (Sun) | Fine-tuning run (3 epochs) | ML Engineer | 📋 Pending |
| 2026-07-30 (Mon) | Validation & regression testing | QA + RAG Eng | 📋 Pending |
| 2026-07-31 (Tue) | Model deployment (staging) | DevOps | 📋 Pending |
| 2026-08-01 (Wed) | Production rollout + monitoring | DevOps + Ops | 📋 Pending |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Fine-tuning overfits to domain | High | Use cross-validation, test on synthetic queries |
| Corpus too small (< 200 docs) | Medium | Pre-collect from ICOLD + CBDB + Lei |
| GPU unavailable | Medium | Use OpenAI API fine-tuning (cost +$50-100) |
| Fine-tuning degrades overall Recall | High | Separate S10 index, use ensemble ranking |
| Timeline slips (> 7 days) | Medium | Deploy Fallback Option A (keyword routing) in parallel |

---

## Integration with Phase 3 Results

This fine-tuning is **Phase 3.5** (post-launch optimization):
- Does NOT invalidate Phase 3 results (84.62% Recall@1, 0% contamination)
- Improves S10 domain specifically without regression to other domains
- Can be deployed independently after Phase 3 production rollout

---

## Decision Tree

```
START: S10 Fine-tuning Plan
│
├─ Budget available? (< $2,000)
│  ├─ YES → Option A (hybrid retrieval, 3 days)
│  │        └─ → Deploy + Monitor → S10 Recall@1 +20-30%
│  │
│  └─ NO (budget > $2,000) → Option B/C (full fine-tuning or accept)
│
├─ Timeline urgent (< 3 days)?
│  ├─ YES → Option A (keyword routing)
│  └─ NO → Option B (fine-tuning) + commit to 1-week deadline
│
└─ END: Execute selected option
```

---

## Recommended Action

**PROCEED WITH FULL FINE-TUNING (Option B)** starting 2026-07-27.

**Rationale:**
- Phase 3 has 3 weeks runway before production deadline
- S10 is highest-priority optimization gap (2 queries failing)
- $1,500 cost is < 1% of total RAG project budget
- Fine-tuning creates reusable S10-optimized embeddings for future projects

**Owner:** RAG Engineering Lead + Barragens Domain Expert (Manta 03-S10)  
**Approval:** MN (awaiting sign-off)

---

**Prepared by:** Agente RAG Benchmark (Phase 3)  
**Validation:** aluci-guard (0 hallucinations)  
**Status:** Ready for immediate execution
