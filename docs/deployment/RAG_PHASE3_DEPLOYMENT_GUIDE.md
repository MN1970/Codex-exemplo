# RAG Phase 3 Deployment Guide
**Date:** 2026-07-26  
**Status:** Comprehensive execution guide for parallel deployment  
**Target Audience:** DevOps, RAG Engineering, QA, Operations

---

## Quick Start (Parallel Execution)

Execute **4 parallel workstreams** simultaneously:

```bash
# Workstream 1: Fix & Deploy SQL Migration (4-6 hours)
→ Fix word count validation in rag_insert.sql
→ Deploy to Supabase staging
→ Verify 58 chunks inserted

# Workstream 2: Collect S10 Corpus (18-24 hours)
→ Gather ICOLD + CBDB + Lei 12.334 + Manta projects
→ Assemble 400-500 document corpus
→ Prepare training data (Day 2)

# Workstream 3: Update PR #32 with Deployment Docs
→ Add SQL migration guide
→ Add S10 fine-tuning roadmap
→ Add production checklist

# Workstream 4: Prepare Staging Environment (2-3 hours)
→ Create Supabase staging DB
→ Configure embedding services (text-embedding-3-large + E5-large)
→ Set up monitoring dashboards
```

---

## Workstream 1: SQL Migration Fixes

### Current Status
- ❌ All 58 chunks failed validation
- ❌ Word count mismatches (avg -5 to -30 words)
- ❌ 23 chunks < 150 words (required minimum)
- ❌ 8 chunks have placeholder markers

### Fix Process (4-6 hours)

**Step 1: Identify Problem Chunks** (30 min)
```bash
# Review rag_insertion_report.json for all failures
# Categorize by error type:
# - WORD_COUNT_MISMATCH (58/58)
# - INVALID_SIZE (23/58)
# - PLACEHOLDER_DETECTED (8/58)
```

**Step 2: Expand Chunks** (3-4 hours)
For each of 58 chunks:
1. Add 20-50 words to reach 150-350 minimum
2. Expand technical content (add norms, examples, context)
3. Remove placeholder markers
4. Recount words accurately

Example expansion:
```
BEFORE (121 words):
"Controle de terraplenagem em rodovia é executado pela fiscalização..."

AFTER (165 words):
"Controle de terraplenagem em rodovia é executado pela fiscalização de obra segundo procedimentos DNIT (Departamento Nacional de Infraestrutura de Transportes). A cada 100 metros lineares de terraplenagem concluída, realiza-se ensaio de densidade de areia (método cálice de areia, NBR 9813) para verificar se a compactação atingiu 95% do Proctor normal determinado em laboratório. Se falhar, a camada é escarificada (revolvida com grade de discos), reúmidecida até umidade ótima e recompactada com rolo compressor de pneus ou rolo liso vibratório..."
```

**Step 3: Validate Metadata** (30 min)
```json
{
  "chunk_id": "syn_ter_rod_004",
  "word_count": 165,  // ← UPDATE
  "declared_count": 160,  // match or update
  "title": "Terraplenagem em rodovia: controle geotécnico e relatórios",
  "normas_citadas": ["DNIT 2006", "NBR 9813", "NBR 7182"],
  "chunk_length_status": "VALID"  // 150-350 range
}
```

**Step 4: Re-generate SQL** (1 hour)
```bash
# Re-run chunk generation with corrected metadata
# Output: rag_insert_v2.sql (corrected)
# Validation: ensure all chunks pass pre-flight checks
```

**Step 5: Test in Staging** (30 min)
```sql
-- In Supabase staging
BEGIN TRANSACTION;
  EXECUTE rag_insert_v2.sql;
  SELECT COUNT(*) FROM rag_chunks WHERE source_type = 'synthetic_disambiguator';
  -- Expected: 58
COMMIT;
```

### Expected Output
- ✅ `rag_insert_v2.sql` (corrected, all chunks valid)
- ✅ Validation report (0 failures)
- ✅ Staging test results (58/58 inserted)

---

## Workstream 2: S10 Corpus Collection (See Separate Doc)

**Document:** `S10_CORPUS_COLLECTION_TASKS.md`

**Timeline:** 2026-07-27 to 2026-07-28 (48 hours, parallel tasks)

**Deliverable:** `barragem_corpus_v1.zip` (400-500 docs, 50-100K tokens)

---

## Workstream 3: Update PR #32 with Deployment Artifacts

### Current PR Status
- ✅ Created (2026-07-26, 13:28 UTC)
- ✅ Draft status (review ready)
- ✅ Clean merge state
- 📋 Missing: deployment documentation links

### PR Update Tasks (1-2 hours)

**Task 1: Add Deployment Guide Section to PR Description**

Insert after "Files Changed":

```markdown
## Deployment & Operations

### Phase 1: SQL Migration (This Week)
See `docs/deployment/SQL_MIGRATION_PHASE3.md`
- Status: 🔧 In progress (word count fixes)
- Timeline: 2026-07-27 to 2026-07-31
- Deliverable: rag_insert_v2.sql

### Phase 2: S10 Fine-tuning (Week 2)
See `docs/deployment/S10_FINETUNING_PLAN.md`
- Status: 📋 Ready to start (corpus collection)
- Timeline: 2026-07-27 to 2026-08-01
- Success: S10 Recall@1 0% → 50-70%

### Phase 3: Production Readiness (Week 3)
See `docs/deployment/PRODUCTION_READINESS_CHECKLIST.md`
- Status: 📋 Prepared (awaiting Phase 1+2 completion)
- Go-live: 2026-08-15, 02:00 UTC
- Success criteria: All 4 documented

### Supporting Docs
- `SQL_MIGRATION_PHASE3.md` — Supabase deployment guide
- `S10_FINETUNING_PLAN.md` — Barragens domain optimization
- `S10_CORPUS_COLLECTION_TASKS.md` — Corpus gathering checklist
- `PRODUCTION_READINESS_CHECKLIST.md` — Operations handbook
- `RAG_PHASE3_DEPLOYMENT_GUIDE.md` — This document
```

**Task 2: Add Parallel Workstreams Diagram**

```markdown
## Parallel Execution Timeline

```
┌─ Workstream 1: SQL Migration Fix ────────────┐
│ 2026-07-27 → 2026-07-31 (4-6 hours per day) │
│ Fix word counts → Deploy staging → Validate  │
└─────────────────────────────────────────────┘
          ↓
┌─ Workstream 2: S10 Corpus Collection ────────┐
│ 2026-07-27 → 2026-07-28 (48 hours parallel) │
│ ICOLD + CBDB + Lei + Manta → Corpus → Train  │
└─────────────────────────────────────────────┘
          ↓
┌─ Workstream 3: PR Documentation ────────────┐
│ 2026-07-26 → 2026-07-27 (1-2 hours)        │
│ Link deployment guides → Update PR body     │
└─────────────────────────────────────────────┘
          ↓
┌─ Workstream 4: Staging Environment ────────┐
│ 2026-07-27 → 2026-07-31 (continuous)       │
│ DB setup → Config → Monitoring → UAT       │
└─────────────────────────────────────────────┘
          ↓
       Go-live 2026-08-15
```

**Task 3: Update Status Badges**

Current:
```markdown
**Status:** Ready for review and deployment (subject to S10 fine-tuning action item)
```

Update to:
```markdown
**Status:** Phase 3 complete ✅ | Deployment in progress 🚀
- SQL Migration: 🔧 Fixing validation errors
- S10 Fine-tuning: 📋 Corpus collection starts 2026-07-27
- Production Ready: 📋 3-week rollout plan documented
```

---

## Workstream 4: Staging Environment Setup

### Prerequisites
- [ ] Supabase account with project created
- [ ] PostgreSQL admin credentials
- [ ] OpenAI API key (text-embedding-3-large access)
- [ ] HuggingFace token (E5-large model access, optional)
- [ ] Monitoring tools (DataDog, Prometheus, or built-in)

### Setup Steps (2-3 hours)

**Step 1: Create Staging Database** (30 min)
```bash
# In Supabase console or via CLI
supabase projects create \
  --name "rag-phase3-staging" \
  --region us-east-1

# Initialize schema
psql postgresql://[CREDS]@db.[PROJECT].supabase.co:5432/postgres < schema.sql
```

**Step 2: Deploy Embedding Services** (1 hour)
```bash
# Option A: OpenAI API (no deployment needed)
export OPENAI_API_KEY="sk-..."

# Option B: Local E5-large fallback
docker pull huggingface/transformers-inference:latest
docker run -p 8000:80 \
  -e MODEL_ID=intfloat/multilingual-e5-large \
  huggingface/transformers-inference

# Test connectivity
curl http://localhost:8000/health
```

**Step 3: Configure Monitoring** (1 hour)
```bash
# Create dashboard in DataDog / Prometheus / built-in
# Metrics to track:
#   - rag_recall_at_1 (gauge, per domain)
#   - rag_contamination (gauge, global)
#   - search_latency_p99 (histogram)
#   - embedding_cache_hit_rate (gauge)
#   - query_throughput_qps (counter)
```

**Step 4: Deploy Search Function** (30 min)
```sql
-- In Supabase staging
CREATE OR REPLACE FUNCTION rag_search(
  query_text TEXT,
  domain_filter TEXT DEFAULT NULL,
  limit_results INT DEFAULT 3
) RETURNS TABLE(...) AS $$
BEGIN
  -- Implementation: ensemble ranking + anti-term filtering
  -- See SQL_MIGRATION_PHASE3.md for full function
END;
$$ LANGUAGE plpgsql;
```

**Step 5: Validate Setup** (30 min)
```bash
# Test search function
SELECT * FROM rag_search('Terraplenagem em rodovia', 'S1', 3);
# Expected: 3 rows, all S1 domain

# Test with contamination query
SELECT * FROM rag_search('Fundação de barragem', 'S1', 3);
# Expected: anti-term filter prevents S10 results
```

### Expected Output
- ✅ Staging Supabase database online
- ✅ Embedding services responding (< 500ms latency)
- ✅ Search function deployed & tested
- ✅ Monitoring dashboards active
- ✅ Ready for SQL migration + benchmark testing

---

## Timeline Overview

```
2026-07-26 (TODAY)
  ✅ Phase 3 complete
  ✅ PR #32 created
  ✅ Deployment docs written

2026-07-27 (FRIDAY) — All 4 Workstreams Start
  WS1: SQL fix begins (word count validation)
  WS2: Corpus collection begins (ICOLD, CBDB, Lei, Manta)
  WS3: PR documentation updates
  WS4: Staging DB creation

2026-07-28 (SATURDAY)
  WS1: SQL fix complete → deploy to staging
  WS2: Corpus assembly (400-500 docs ready)
  WS3: PR ready for team review
  WS4: Embedding services configured

2026-07-29 (SUNDAY)
  WS1: Benchmark re-run on staging (validate 84.62% maintained)
  WS2: Training data creation begins (200-300 pairs)
  WS4: Load testing (up to 50 QPS)

2026-07-30-31 (MON-TUE)
  WS1: Final staging validation complete
  WS2: Fine-tuning execution (Day 1-2 of 3)
  WS4: UAT with domain experts

2026-08-01 (WED)
  WS1: Staging → Production sign-off
  WS2: Fine-tuning complete → validation begins

2026-08-15 (WED)
  🚀 PRODUCTION DEPLOYMENT 02:00 UTC
```

---

## Success Criteria

✅ **All Workstreams Complete on Schedule**
- SQL migration: 0 validation errors
- S10 corpus: 400-500 documents, ready for training
- PR: documentation links all active
- Staging: 84.62% Recall@1 confirmed

✅ **Ready for Production Deployment**
- Sign-offs: Eng, QA, Ops, MN
- Risk mitigation: all contingencies documented
- Monitoring: live dashboards + alerts configured
- Rollback: tested and verified

---

**Prepared by:** Agente RAG Benchmark  
**Version:** 1.0  
**Status:** Ready for team execution
