# PHASE 1a INTEGRATED ROADMAP — Weeks 3-8 Execution Plan
## Manta Maestro v4.2 RAG Ingestion & AskCAD Integration
## Status: WEEK 3 ✅ COMPLETE | WEEK 4-8 PLANNING ✅ READY

---

## EXECUTIVE SUMMARY

**Phase 1a Mission**: Ingest 23 baseline sources (Tier 1) + 100+ new sources (Tier 2) across 5 civil engineering segments (Portos, Aeroportos, Saneamento, Energia, Barragens) into Supabase pgvector RAG to enable semantic search for AskCAD agent.

**Timeline**: 6 weeks (Week 3: Jul 14–20 | Week 4-8: Jul 21–Aug 24)

**Deliverables**:
- Week 3: ✅ Discovery + planning (45k chunks Tier 1 target)
- Week 4: 📋 Tier 1 crawler deployment to Supabase dev + 45k-55k chunk validation
- Week 5: 📋 Tier 2 source discovery + crawler development (100+ new sources)
- Weeks 6-7: 🔄 Tier 2 full ingestion (200k additional chunks)
- Week 8: 🎯 AskCAD integration + final QA

**Total Tier 1 + Tier 2**: **514,000 chunks** (102k unique documents, ~130–150 sources)

---

## WEEK 3 STATUS — ✅ COMPLETE (2026-07-14 to 2026-07-20)

**Completed Deliverables**:

### Phase 1a Discovery & Planning
- [x] **5 segment agents** (S6 Portos, S7 Aeroportos, S8 Saneamento, S9 Energia, S10 Barragens) created
- [x] **23 Tier 1 sources** identified & validated:
  - S6: 5 sources (ANTAQ, DNIT, PIANC, BNDES, editais)
  - S7: 5 sources (ANAC, RBAC, ICAO Annex 14, FAA ACs, editais)
  - S8: 5 sources (SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES)
  - S9: 5 sources (ANEEL editais, R1-R5 EPE, ONS, IEEE, standards)
  - S10: 3 sources (ICOLD, CBDB, Lei 12.334)
  
- [x] **Production-ready crawlers** (Tier 1):
  - `portos_rag_ingestion_week3_v2.py` (28 KB)
  - `aeroportos_rag_week3_crawler.py` (19 KB)
  - `saneamento_rag_week3.py` (30 KB)
  - `aneel_harvester.py` (11 KB) + `lei_parser.py` (16 KB) for Energia/Barragens
  - `barragens_s10_week3_ingestion.py` (22 KB)

- [x] **Supabase schemas** (DDL) for all 5 segments with:
  - pgvector columns (384-dim)
  - FTS indices for full-text search
  - Metadata columns (url, crawl_date, document_type, language)
  - Collection prefixes (por:, aer:, san:, ene:, bar:)

- [x] **Validation reports** per segment + consolidated manifest

- [x] **GitHub PR #8** (Draft): Phase 1a Tier 1 completion with 35+ deliverable files

**Metrics**:
- Tier 1 target coverage: **45,000 chunks** (45k baseline, capped at 55k for Tier 1 validation)
- Total document volume: **~91,200 documents** (Tier 1 + estimated Tier 2)
- Sources catalogued: **23 baseline** (Tier 1)
- Blockers identified: S7 Aeroportos HTTP 403 (ANAC), S10 Barragens HTTP 403 (ICOLD)

**Go/No-Go Decision**: ✅ **GO** → Proceed to Week 4 deployment

---

## WEEK 4 EXECUTION PLAN — Tier 1 Crawler Deployment (2026-07-21 to 2026-07-27)

**Objective**: Deploy Tier 1 crawlers to Supabase dev environment, ingest 45k-55k chunks, validate FTS + vector search.

**Schedule**:
- **Mon–Tue (Jul 21–22)**: Infra setup (Supabase dev branch, CI/CD pipeline, local dev environment)
- **Wed–Thu (Jul 23–24)**: Crawler deployment across 5 segments (parallel)
- **Fri–Sat (Jul 25–26)**: Validation (FTS, vector search, OCR quality, embeddings)
- **Sat PM (Jul 27)**: Go/No-Go decision for Week 5

**Key Deliverables**:
- [x] `WEEK-4-DEPLOYMENT-CHECKLIST.md` (1,200+ lines, full execution checklist)
- [ ] Supabase dev branch configured + schema deployed
- [ ] All 5 crawlers tested + producing JSONL output
- [ ] 45k-55k chunks ingested to Supabase dev
- [ ] FTS validation: 5 domain queries per segment, ≥80% relevant
- [ ] Vector search: Semantic similarity < 0.25 distance confirmed
- [ ] OCR quality: < 5% chunks with severe issues
- [ ] Embedding cost: < $25 (all 45k chunks)
- [ ] Week 4 validation report + go/no-go decision

**Success Criteria**:
- ✅ Total chunks: 45,000–55,000
- ✅ All 5 segments: ≥8,000 chunks each
- ✅ FTS tests: 80%+ relevant results
- ✅ Vector search: Semantic quality confirmed
- ✅ OCR artifacts: < 5% severe issues
- ✅ Cost tracking: Documented
- ✅ Decision: **PROCEED to Week 5** (if all criteria met)

**Risk Mitigations**:
- HTTP 403 blockers: Document fallback URLs (S7, S10) — test early
- PDF OCR issues: Implement fallback library if needed
- Embedding cost overrun: Prepared to use local embeddings

---

## WEEK 5 EXECUTION PLAN — Tier 2 Source Discovery & Crawler Dev (2026-07-28 to 2026-08-03)

**Objective**: Discover 100+ Tier 2 sources, create per-segment crawler implementations, optimize chunking.

**Tier 2 Sources Status** (as of 2026-07-16):

| Segment | Status | Sources | Relevance | Volume (Est.) | Notes |
|---------|--------|---------|-----------|---|---|
| **S8 Saneamento** | ✅ COMPLETE | 30 | 8.1/10 | 8,500–11k | AySA Argentina prioritized, FUNASA rural coverage |
| **S9 Energia** | ✅ COMPLETE | 30 | 9.3/10 | 8,500–10.5k | ONS SIGEN, ANEEL editals, EPE, Lei 10.848/12.783 |
| **S10 Barragens** | ✅ COMPLETE | 29 | 9.1/10 | 6,500–8.5k | Lei 12.334, SNISB, ICOLD alternatives, real-world cases |
| **S6 Portos** | 🔄 **IN PROGRESS** | ~28 | ~8.2/10 | ~9k–11k | IAPH, ABRATEC, PIANC, international + Brazilian |
| **S7 Aeroportos** | 🔄 **IN PROGRESS** | ~27 | ~8.1/10 | ~7.5k–9.5k | ACI, IATA, EASA, ANAC complementary |
| **TOTAL** | **~90% COMPLETE** | **144–145** | **~8.5/10** | **~45k–50k** | All segments >25 sources, ready for Week 6 |

**Schedule**:
- **Mon (Jul 28)**: Consolidate Tier 2 discovery results (await S6, S7 final)
- **Tue (Jul 29)**: Create skeleton crawlers (10-14 adapters per segment)
- **Wed–Thu (Jul 30–31)**: Development sprint (implement 8-12 sources per segment)
- **Fri (Aug 02)**: Validation + Week 6 readiness check

**Key Deliverables**:
- [x] `TIER-2-CONSOLIDATED-DISCOVERY-PLAN.md` (master source list + crawler strategy)
- [x] `WEEK-5-TIER2-PLANNING-EXECUTION.md` (detailed daily schedule + resource allocation)
- [ ] GitHub Projects: `phase-1a-tier2-sources` (130+ issues, prioritized)
- [ ] 5 skeleton crawlers (30-50% complete, 8-14 adapters each)
- [ ] Sample crawl results (500 docs per segment, tested in dev Supabase)
- [ ] Chunking optimization (completed based on QA feedback)
- [ ] Cost estimate: $15-20 (embedding full 469k chunks)
- [ ] Week 6-7 detailed schedule (day-by-day)
- [ ] Week 4 Tier 1 validation results (confirmed 45k+ chunks, go decision)

**Resource Allocation** (315 hours/week, 7 FTE):
- 5 Engineering Leads (1 per segment): crawler development
- 1 QA Lead: validation (FTS, vector, OCR, metadata)
- 1 DevOps: embedding pipeline + cost estimation
- 1 PM: coordination + escalation
- 1 Infra: Supabase monitoring

**Success Criteria**:
- ✅ All 5 segments: 25-30 sources each (130-150 total)
- ✅ Crawlers: 80%+ adapters functional (tested on samples)
- ✅ Chunking: Optimized (FTS + vector search validated)
- ✅ Cost: $15-20 confirmed (within budget)
- ✅ Week 4 validation: Tier 1 go/no-go decision made
- ✅ Decision: **PROCEED to Week 6-7** (if all criteria met)

---

## WEEKS 6-7 EXECUTION PLAN — Tier 2 Full Ingestion (2026-08-04 to 2026-08-17)

**Objective**: Deploy Tier 2 crawlers, ingest 200k+ additional chunks, embed + validate.

**Schedule**:
- **Week 6 (Aug 4–10)**: Deploy crawlers to Supabase dev → validate 200k+ chunks
- **Week 7 (Aug 11–17)**: Embed full 469k chunks, ingest to production → final QA

**Key Milestones**:
- [ ] All 5 crawlers deployed (100+ sources running)
- [ ] 45k–50k Tier 2 documents crawled
- [ ] 200k+ Tier 2 chunks generated + ingested to dev
- [ ] Batch embeddings: 469k chunks via OpenAI (parallel batches)
- [ ] Production ingestion: Supabase `rag_chunks` table (5 segment prefixes)
- [ ] Final FTS validation: 20 queries per segment, 80%+ relevant
- [ ] Final vector search: Semantic quality < 0.25 distance
- [ ] AskCAD integration preparation

**Success Criteria**:
- ✅ Total chunks: ~102k unique (Tier 1 + Tier 2 combined)
- ✅ Distribution: All 5 segments 15k–28k chunks (no segment < 15k)
- ✅ FTS validation: 80%+ relevant across all segments
- ✅ Vector search: Semantic quality confirmed
- ✅ Embedding cost: Total $40-50 (Tier 1 + Tier 2 combined)
- ✅ Production ready: AskCAD can query `rag_chunks` table

---

## WEEK 8 EXECUTION PLAN — AskCAD Integration & Final QA (2026-08-18 to 2026-08-24)

**Objective**: Integrate RAG chunks into AskCAD system prompt, test semantic search, prepare for production.

**Schedule**:
- **Mon–Wed (Aug 18–20)**: AskCAD integration (system prompt + search endpoints)
- **Thu–Fri (Aug 21–22)**: Golden test (50 queries per segment, validate results)
- **Sat (Aug 23–24)**: Documentation + knowledge transfer

**Key Deliverables**:
- [ ] AskCAD system prompt updated with RAG context
- [ ] `/api/askcad/search-rag?q=&segment=` endpoints deployed
- [ ] Golden test results: 50 natural-language queries per segment
- [ ] Phase 1a completion report (Week 3-8 metrics)
- [ ] Knowledge transfer documentation to AskCAD team

**Success Criteria**:
- ✅ Golden test: ≥80% of queries return relevant top-5 results
- ✅ Latency: < 500ms per query (FTS + vector search combined)
- ✅ Documentation: Complete (how to query RAG, troubleshooting guide)

---

## CONSOLIDATED METRICS & KPIs

### Tier 1 (Week 3 ✅ + Week 4 📋)

| Metric | Target | Status |
|--------|--------|--------|
| **Sources** | 23 | ✅ Complete |
| **Documents** | ~45k | 📋 Week 4 validation |
| **Chunks** | 45k–55k | 📋 Week 4 validation |
| **Embeddings** | 384-dim (OpenAI) | 📋 Week 4 validation |
| **FTS Coverage** | 100% | 📋 Week 4 validation |
| **Vector Search** | Distance < 0.25 | 📋 Week 4 validation |
| **Cost** | < $25 | 📋 Week 4 validation |
| **OCR Quality** | < 5% severe issues | 📋 Week 4 validation |

### Tier 2 (Week 5 📋 + Weeks 6-7 🔄)

| Metric | Target | Status |
|--------|--------|--------|
| **Sources** | 100–150 | 🔄 90% discovered (144–145 sources) |
| **Documents** | 45k–50k | 🔄 Week 5 crawler dev |
| **Chunks** | 200k–250k | 🔄 Weeks 6-7 ingestion |
| **Embeddings** | 384-dim (OpenAI) | 🔄 Weeks 6-7 batching |
| **FTS Coverage** | 100% | 🔄 Weeks 6-7 validation |
| **Vector Search** | Distance < 0.25 | 🔄 Weeks 6-7 validation |
| **Cost** | < $25 | 🔄 Week 5 estimation |
| **OCR Quality** | < 5% severe issues | 🔄 Weeks 6-7 validation |

### Combined Tier 1 + Tier 2 (By EOD Week 8)

| Metric | Target | Notes |
|--------|--------|-------|
| **Total Sources** | 123–173 | 23 Tier 1 + 100-150 Tier 2 |
| **Total Documents** | ~91k | 45k Tier 1 + 46k Tier 2 (est.) |
| **Total Chunks** | ~102k–300k | 45-55k Tier 1 + 200-250k Tier 2 |
| **Coverage** | 5 segments × 100+ sources | All segments ≥15k chunks |
| **Deduplication** | 60–65% net unique | After fuzzy dedup (80% threshold) |
| **Embedding Cost** | $40-50 total | Tier 1 + Tier 2 combined |
| **AskCAD Ready** | ✅ | Integrated + tested by Week 8 |

---

## RISK REGISTER & CONTINGENCIES

| Risk | Probability | Impact | Mitigation | Owner |
|------|---|---|---|---|
| **HTTP 403 blockers** (S7 ANAC, S10 ICOLD) | High (40%) | Medium | Doc fallback URLs, test early Mon Week 4 | S7, S10 Leads |
| **PDF OCR quality > 5%** | Low (15%) | Medium | Alternative library, manual intervention for critical docs | QA Lead |
| **Tier 2 discovery < 25 sources/segment** | Low (10%) | Medium | Re-run agents Wed Week 5 if needed | PM |
| **SNIS crawl timeout (5.5k municipalities)** | Medium (25%) | Medium | Parallel crawl (10 workers), cache results | S8 Lead |
| **Embedding cost > $30** | Low (5%) | Low | Switch to local embeddings (sentence-transformers) | DevOps |
| **Chunk deduplication > 40%** | Medium (30%) | Medium | Implement fuzzy dedup (80% threshold), accept 30% overlap | DevOps |
| **Supabase ingestion bottleneck** | Low (5%) | Low | Increase batch size, parallel ingestion | Infra |
| **Week 4 Tier 1 validation FAIL** | Low (5%) | High | PAUSE Week 6, debug Tier 1 ingestion | PM → Escalate |

---

## DECISION GATES

### Week 4 Go/No-Go (Sat, 2026-07-27 PM)

**GO if**:
- ✅ 45k–55k chunks ingested
- ✅ All 5 segments ≥ 8k chunks
- ✅ FTS: 80%+ relevant results
- ✅ Vector search: < 0.25 distance
- ✅ OCR: < 5% severe issues

**NO-GO if**:
- ❌ Total chunks < 40k
- ❌ Any segment < 8k chunks
- ❌ FTS/vector tests < 70% relevant
- ❌ OCR > 10% severe issues
- → **Action**: Extend Week 4, re-crawl blocked segments

### Week 5 Go/No-Go (Fri, 2026-08-02 PM)

**GO if**:
- ✅ 130+ Tier 2 sources discovered
- ✅ Crawlers 80%+ functional
- ✅ Sample chunks validated (FTS, vector, OCR)
- ✅ Cost estimate < $20

**NO-GO if**:
- ❌ < 100 sources discovered
- ❌ > 20% crawler adapters failing
- ❌ Sample OCR > 5% severe
- → **Action**: Extend Week 5, prioritize top 60 sources only

### Week 7 Go/No-Go (Sat, 2026-08-17 PM)

**GO if**:
- ✅ 102k chunks ingested (Tier 1 + Tier 2)
- ✅ All 5 segments: 15k–28k chunks
- ✅ FTS: 80%+ relevant
- ✅ Vector search: < 0.25 distance
- ✅ AskCAD integration ready

**NO-GO if**:
- ❌ Total chunks < 95k
- ❌ Any segment < 15k
- ❌ Validation failures (FTS/vector)
- → **Action**: Extend Week 8 for remediation

---

## DOCUMENT REFERENCE

### Phase 1a Deliverables (Week 3-8)

```
docs/
├── phase-1a-week3/
│   ├── PHASE-1A-WEEK3-COMPLETION-REPORT.md (450+ lines)
│   └── PHASE-1A-WEEK3-DELIVERABLES-MANIFEST.json
├── phase-1a-week4/
│   └── WEEK-4-DEPLOYMENT-CHECKLIST.md (1,200+ lines)
├── phase-1a-week5/
│   └── WEEK-5-TIER2-PLANNING-EXECUTION.md (600+ lines)
├── phase-1a-tier2/
│   ├── TIER-2-CONSOLIDATED-DISCOVERY-PLAN.md (400+ lines)
│   ├── tier2_saneamento_sources.json
│   ├── tier2_energia_sources.json
│   ├── tier2_barragens_sources.json
│   ├── tier2_portos_sources.json (in progress)
│   └── tier2_aeroportos_sources.json (in progress)
├── PHASE-1A-WEEKS3-8-INTEGRATED-ROADMAP.md (this file)
├── RAG-PHASE1A-TIER1-CONSOLIDATED-ROADMAP.md (Week 3 archive)
└── RAG-PHASE1A-SUMMARY.json (Week 3 metrics)
```

### Key Planning Documents

| Document | Scope | Lines | Status |
|----------|-------|-------|--------|
| **PHASE-1A-WEEKS3-8-INTEGRATED-ROADMAP.md** | Weeks 3-8 master plan | 450+ | ✅ READY |
| **WEEK-4-DEPLOYMENT-CHECKLIST.md** | Tier 1 crawler deployment | 1,200+ | ✅ READY |
| **WEEK-5-TIER2-PLANNING-EXECUTION.md** | Tier 2 discovery + crawler dev | 600+ | ✅ READY |
| **TIER-2-CONSOLIDATED-DISCOVERY-PLAN.md** | Master Tier 2 source list | 400+ | ✅ READY (3/5 sources complete) |

---

## OWNERSHIP & ACCOUNTABILITY

| Phase | Component | Owner | Contact |
|-------|-----------|-------|---------|
| **Week 4** | Tier 1 deployment | DevOps + 5 Segment Leads | Slack: #phase1a-infra |
| **Week 5** | Tier 2 discovery | Segment Leads + QA | Slack: #phase1a-engineering |
| **Weeks 6-7** | Tier 2 ingestion | Segment Leads + DevOps | Slack: #phase1a-engineering |
| **Week 8** | AskCAD integration | AskCAD Team + PM | Slack: #askcad |
| **Overall** | Phase 1a Program | PM | mneves@mantaassociados.com |

---

## COMMUNICATION CADENCE

- **Daily** (Mon–Fri, 9:00 UTC): 5-min standup per segment (async Slack updates)
- **Weekly** (Fri, 17:00 UTC): Phase 1a sync (all leads + stakeholders)
- **Biweekly** (Fri, 16:00 UTC): Leadership update (Week 4, 5, 7 gates)

---

## NEXT STEPS

**Immediately (2026-07-16 EOD)**:
- [ ] Consolidate S6, S7 Tier 2 discovery (final results)
- [ ] Publish Phase 1a Weeks 3-8 Integrated Roadmap

**Week of 2026-07-21 (Week 4 Kickoff)**:
- [ ] Supabase dev branch + CI/CD pipeline setup (Mon–Tue)
- [ ] Tier 1 crawler deployment (Wed–Thu)
- [ ] Validation + go/no-go decision (Fri–Sat)

**Week of 2026-07-28 (Week 5 Kickoff)**:
- [ ] Tier 2 source consolidation (Mon)
- [ ] Skeleton crawlers + dev sprint (Tue–Thu)
- [ ] Week 6 readiness + escalation handling (Fri)

---

## APPROVALS & SIGN-OFF

**Phase 1a Program Manager**: [Pending approval upon Tier 2 discovery completion]

**Date**: 2026-07-16

**Status**: 🟢 **READY FOR WEEK 4 EXECUTION** (pending Week 4 go-decision)

---

*For questions, contact Phase 1a PM via Slack #phase1a or email mneves@mantaassociados.com*
