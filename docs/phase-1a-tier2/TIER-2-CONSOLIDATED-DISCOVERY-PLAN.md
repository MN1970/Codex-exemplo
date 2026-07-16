# TIER 2 CONSOLIDATED DISCOVERY PLAN
## Phase 1a Weeks 6-7 Source Mapping & Crawler Strategy
## Status: S8 Complete | S6, S7, S9, S10 In Progress

---

## EXECUTIVE SUMMARY

**Tier 2 Mission**: Discover and integrate 100+ new sources (beyond Phase 1a Tier 1's 23 baseline sources) to expand RAG coverage from 45k to 514k total chunks across Weeks 6-7.

**Timeline**: 
- Week 5 (Jul 28–Aug 3): Finalize Tier 2 source discovery + create per-segment crawler implementations
- Week 6 (Aug 4–Aug 10): Deploy Tier 2 crawlers to Supabase → 200k+ additional chunks
- Week 7 (Aug 11–Aug 17): Validate, optimize embeddings, prepare AskCAD integration

**Total Tier 1 + Tier 2**: 514,000 chunks (469k Tier 2 distributed across 5 segments)

---

## DISCOVERY RESULTS & SEGMENT SUMMARIES

### S8 SANEAMENTO — ✅ TIER 2 COMPLETE

**Status**: Discovery finished 2026-07-16 PM  
**Sources Found**: 30 Tier 2 sources  
**Relevance Score**: 8.1/10 average  
**Estimated Volume**: 8,000–12,000 documents (8.5k–11k chunks after dedup)

#### Tier 2 Breakdown by Category

| Category | Count | Examples | Public Access | Est. Docs |
|----------|-------|----------|---|---|
| **Associações** | 3 | ABCON, ASSEMAE, ENOHSA Argentina | 100% | 500 |
| **AySA Argentina** (PRIORIDADE) | 3 | AySA SP, ENOHSA manuais, Ley 26.221 | 100% | 800 |
| **Repositórios Públicos** | 5 | SNIS, ANA PMSB, IBGE-PNAD, DataSUS, Tesouro | 100% | 3,000 |
| **Normas & Standards** | 7 | IWA, AWWA, ASCE, WHO, NBR 12211-12213, BS EN | 40% open | 1,500 |
| **Legislação Brasil** | 4 | Portaria MS 888/2021, Lei 14.026, CONAMA 357/405/430, PMSBs | 100% | 800 |
| **Publicações Acadêmicas** | 6 | Revista DAE, ABRH, USP, UFRGS, UFBA, Journal AQUA-IWA | 60% open | 1,200 |
| **Operadores Brasileiros** | 3 | SABESP, COPASA, CAESB relatórios | 50% open | 600 |
| **Saneamento Rural** | 1 | FUNASA (< 50k hab) | 100% | 400 |
| **Saúde Pública** | 1 | SINAN/DataSUS doenças hídricas | 100% | 300 |
| **Financeiro/Investimentos** | 1 | PAC/BNDES saneamento | 100% | 200 |
| **TOTAL** | **30** | | **66% public** | **~9,200** |

#### Top 5 Tier 2 Sources (S8 by relevance)

1. **AySA Manuales de Diseño & Operación** (9.5/10)
   - URL: `aisa.com.ar/empresa/biblioteca/` (partial access)
   - Volume: 2,000 pages (design standards, operational manuals)
   - Type: Technical documentation (Spanish + Portuguese translations available)
   - Relevance: Design standards for utilities serving 10M people; directly applicable to Brazil

2. **SNIS 2024 Complementary Data (ANA PMSB)** (9.3/10)
   - URL: `ana.gov.br/pmsb/` (100% public)
   - Volume: 3,500 documents (municipal PMSB plans, 5,570 municipalities)
   - Type: Structured data + PDFs
   - Relevance: Complements Tier 1 SNIS aggregates with municipal-level detail

3. **Associação Brasileira de Concessionárias de Água e Esgoto (ABCON)** (9.1/10)
   - URL: `abcon.com.br/publicacoes/` (100% public)
   - Volume: 800 documents (best practices, case studies, economic analysis)
   - Type: Industry reports, white papers
   - Relevance: Operator perspective on efficiency, costs, technology adoption

4. **FUNASA Saneamento Rural (MS)** (8.9/10)
   - URL: `funasa.saude.gov.br/` (100% public)
   - Volume: 600 documents (design guidelines, training materials for < 50k municipalities)
   - Type: Technical guidelines + PDFs
   - Relevance: Covers underrepresented rural segment (critical for comprehensive coverage)

5. **IWA Water Supply & Wastewater Standards** (8.7/10)
   - URL: `iwawaterwiki.org/` (40% open, 60% paywall)
   - Volume: 1,200 pages (best practices, benchmarking, innovation)
   - Type: International standards + case studies
   - Relevance: Cross-reference to global practices; validates Brazilian standards alignment

#### S8 Tier 2 Crawler Implementation Plan (Weeks 6-7)

**Week 6 Tasks**:
1. Enhance `saneamento_rag_week3.py` with 10 new crawlers (1 per Tier 2 category bulk + AySA + FUNASA specialized)
2. Add AYSa authentication (OAuth2) + Spanish/Portuguese PDF parsing
3. Implement SNIS municipal PMSB recursive crawl (5,570 municipalities)
4. Create fallback strategies for paywalled sources (IWA, AWWA archives)
5. Deploy to Supabase dev → validate chunking on 1k sample docs
6. **Target**: 8,500–11,000 new chunks by end Week 6

**Week 7 Tasks**:
1. Run full Tier 2 crawl (all 30 sources) → 8,500–11,000 chunks
2. Embed + ingest to Supabase production `san:` prefix
3. QA: Validate AySA content searchable (Portuguese translation verified), PMSB municipal rollup works
4. **Target**: All 30 sources fully indexed by end Week 7

---

### S6 PORTOS — 🔄 IN PROGRESS

**Status**: Discovery agent running (agent ID: a2f964b5f5cf01513)  
**Expected completion**: ~30 min (by 2026-07-16 PM)  
**Preliminary target**: 25–30 Tier 2 sources  
**Estimated volume**: 9,000–11,000 chunks

**Scope** (inferred from briefing):
- Port associations (AAPA, IAPH, Latin American port networks)
- Technical standards (ISO, IALA, PIANC design guidelines)
- Academic/case studies (port engineering, automation, Brazilian regional ports)
- Technologies (dredging equipment, cranes, automation)
- Complementary legislation (environmental, labor, infrastructure)
- Public repositories (government data, port statistics)

**Placeholder awaiting agent completion**...

---

### S7 AEROPORTOS — 🔄 IN PROGRESS

**Status**: Discovery agent running (agent ID: a9811039336b09291)  
**Expected completion**: ~30 min  
**Preliminary target**: 25–30 Tier 2 sources  
**Estimated volume**: 7,500–9,500 chunks

**Scope** (inferred):
- Airport associations (IATA, ACI, regional networks)
- Design/operations standards (ISO, ICAO beyond Annex 14)
- Academic research (aviation, regional airports, Brazil-focused)
- Technology documentation (ILS, NAVAID, ATC systems)
- Complementary legislation (safety, environmental, infrastructure)
- Public datasets (flight data, airport statistics, operational metrics)

**Placeholder awaiting agent completion**...

---

### S9 ENERGIA — 🔄 IN PROGRESS

**Status**: Discovery agent running (agent ID: a46c89218ddea8817)  
**Expected completion**: ~30 min  
**Preliminary target**: 25–30 Tier 2 sources  
**Estimated volume**: 8,500–10,500 chunks

**Scope** (inferred):
- Energy associations (ABRADEE, ABRACE, transmission operators)
- Technical standards (ABNT, IEEE, IEC)
- Academic research (grid stability, transmission design, Brazilian context)
- Equipment documentation (WEG, transformers, breakers)
- Complementary legislation (concessions, market mechanisms, planning)
- Public data (ONS operations, EPE forecasts, CCEE markets)

**Placeholder awaiting agent completion**...

---

### S10 BARRAGENS — 🔄 IN PROGRESS

**Status**: Discovery agent running (agent ID: a6aa0d36aac7705c0)  
**Expected completion**: ~30 min  
**Preliminary target**: 25–30 Tier 2 sources  
**Estimated volume**: 6,500–8,500 chunks

**Scope** (inferred):
- Dam associations (ICOLD, CBDB, Brazilian operators)
- Design/safety standards (ABNT, ICOLD guidelines)
- Academic research (dam engineering, safety, Brazilian case studies)
- Real-world cases (Fundão, Brumadinho, monitoring, lessons learned)
- Complementary legislation (Lei 12.334, ANM, environmental)
- Public repositories (SNISB, SIGBM, government data)

**Placeholder awaiting agent completion**...

---

## TIER 2 SOURCE CONSOLIDATION MATRIX

**Once all agents complete, this matrix will be populated**:

| Segment | Tier 2 Sources | Est. Docs | Est. Chunks | Public Access % | High-Priority Category |
|---------|---|---|---|---|---|
| **S6 Portos** | [PENDING] | [PENDING] | [PENDING] | [PENDING] | Ports associations, Latin American networks |
| **S7 Aeroportos** | [PENDING] | [PENDING] | [PENDING] | [PENDING] | Airport associations, regional airports |
| **S8 Saneamento** | ✅ 30 | 9,200 | 10,400 | 66% | AySA Argentina, FUNASA rural, SNIS PMSB |
| **S9 Energia** | [PENDING] | [PENDING] | [PENDING] | [PENDING] | ANEEL/EPE/ONS market data, State Grid docs |
| **S10 Barragens** | [PENDING] | [PENDING] | [PENDING] | [PENDING] | Lei 12.334, CBDB case studies, real-world safety |
| **TOTAL** | **~130–150** | **~45,000–50,000** | **~469,000** | **~60%** | Across all priorities |

---

## TIER 2 CRAWLER DEVELOPMENT STRATEGY (Weeks 6-7)

### Week 6: Crawler Implementation & Dev Validation

**Daily Schedule:**
- **Mon 2026-08-04**: Create skeleton crawlers for all 5 segments + run Tier 2 discovery on subset (10% sample per segment)
- **Tue–Wed 2026-08-05–06**: Implement API/web scraping for 25 Tier 2 sources (5 per segment)
- **Thu 2026-08-07**: Deploy to Supabase dev, validate chunking on 1k sample docs per segment
- **Fri 2026-08-08**: Optimize chunking params (token targets, overlap); prepare production deployment list

**Parallel Work Stream**:
- Handle HTTP 403 blockers identified in Tier 1 (S7 Aeroportos, S10 Barragens) — test alternative URLs
- Create specialized crawlers for unique sources (AySA OAuth2, SNIS municipal recursion, ANEEL CKAN pagination)
- Prepare embeddings pipeline for 469k total chunks (cost estimation: $18–22)

**Success Criteria Week 6**:
- [ ] All 5 segments have functional Tier 2 crawlers (at least 80% of sources tested)
- [ ] 10k sample chunks validated in Supabase dev (correct schema, no missing fields)
- [ ] OCR quality verified on PDF-heavy sources (S9 EPE, S8 SNIS, S10 ICOLD)
- [ ] Embedding pipeline tested on 1k chunks (latency, cost, quality)

### Week 7: Full Tier 2 Ingestion & Production Deployment

**Daily Schedule:**
- **Mon 2026-08-11**: Run full Tier 2 crawl (all sources) → 45k–50k documents
- **Tue 2026-08-12**: Chunk + validate output (target: 469k chunks across 5 segments)
- **Wed–Thu 2026-08-13–14**: Batch embed all 469k chunks via OpenAI (parallel, 100 req/min)
- **Fri 2026-08-15**: Ingest to Supabase production → validate FTS + vector search
- **Sat 2026-08-16**: Final QA + AskCAD integration prep

**Success Criteria Week 7**:
- [ ] 469k Tier 1 + Tier 2 chunks in Supabase production
- [ ] All 5 segments pass FTS (20 domain queries per segment, 80%+ relevant)
- [ ] All 5 segments pass vector search (semantic relevance < 0.25 distance)
- [ ] Embedding cost tracked (budget $25–30)
- [ ] AskCAD ready to ingest `rag_chunks` table

---

## CHUNKING & EMBEDDING SCALING (469k total)

### Volume Breakdown

| Segment | Tier 1 | Tier 2 | Combined | Est. Chunks |
|---------|---|---|---|---|
| S6 Portos | 10k | 9k | 19k | 21k |
| S7 Aeroportos | 7.5k | 8k | 15.5k | 17k |
| S8 Saneamento | 16k | 9.2k | 25.2k | 28k |
| S9 Energia | 8.5k | 9k | 17.5k | 20k |
| S10 Barragens | 6.5k | 7.5k | 14k | 16k |
| **TOTAL** | **48.5k** | **42.7k** | **91.2k** | **102k** |

**Note**: This represents aggregate documents. After deduplication (est. 20–30% overlap within + across segments), final chunk count is expected **~102k chunks** (accounting for overlap). If additional Tier 2 sources discovered during Week 5, scale adjusts linearly.

### Embedding Cost & Timeline

**OpenAI text-embedding-3-small @ $0.02 per 1M input tokens**:
- Avg chunk: 350 tokens
- 102k chunks × 350 tokens = **35.7M input tokens**
- Cost: 35.7M × $0.00000002 = **$0.71 (surprisingly low!)**
- Alternative: If using local `sentence-transformers/multilingual-e5-small` (no API cost): **$0.00** but ~200 min compute time

**Recommended approach**: Use OpenAI for production (cost negligible, quality proven), parallelize embedding batches (10 concurrent batches × 100 req/min = 1k req/min max, total time ~10 min for 102k chunks + retries).

**Timeline**: Week 7 Wed–Thu, ~2–3 hours wall-clock time.

---

## INTEGRATION DEPENDENCIES

### Phase 1a → Phase 2 Handoff

**By EOD Week 7 (2026-08-17)**, Tier 1 + Tier 2 ingestion complete:
- ✅ 102k chunks in Supabase `rag_chunks` table (across 5 segments)
- ✅ FTS indices ready (tested 5+ queries per segment)
- ✅ pgvector ready (384d embeddings, normalized)
- ✅ Metadata complete (url, crawl_date, document_type, language)

**Week 8 Prep** (2026-08-18–24):
- AskCAD integration: Populate the service-specific `rag_chunks` RAG context in AskCAD system prompt
- Create search endpoints: `/api/askcad/search-rag?q=&segment=` for each service
- Golden test: 50 natural-language queries per segment, verify top-5 results relevant

---

## RISK REGISTER (Tier 2)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| HTTP 403 on paywalled sources (IWA, AWWA, ICOLD) | Medium (40%) | Low | Use open mirrors (Web Archive, ResearchGate); supplement with free alternatives |
| SNIS municipal PMSB crawl timeout (5,570 municipalities) | Medium (35%) | Medium | Implement parallel crawl (10 workers); cache results; skip municipalities > 500MB |
| PDF OCR quality on Spanish documents (AySA) | Low (15%) | Medium | Test OCR on sample AySA docs Week 5; use specialized Spanish OCR if needed |
| Duplicate content across Tier 1 + Tier 2 (>30%) | Medium (30%) | Medium | Implement fuzzy dedup (80% similarity threshold) before embedding |
| Embedding API rate limit (OpenAI) | Low (10%) | Low | Use exponential backoff; batch smaller if needed; switch to local embeddings if necessary |

---

## SUCCESS CRITERIA (Phase 1a Tier 1 + Tier 2)

**By EOD Week 7 (2026-08-17)**:

1. ✅ **Coverage**: 102k chunks ingested (Tier 1 + Tier 2 combined)
2. ✅ **Distribution**: All 5 segments have 15k–28k chunks (no segment < 15k)
3. ✅ **Quality**: FTS test 80%+ relevant per segment; vector search < 0.25 distance
4. ✅ **Deduplication**: < 30% duplicate content across sources
5. ✅ **Cost**: Total embeddings < $50 (including Tier 1 + Tier 2)
6. ✅ **Documentation**: All sources catalogued + crawler code committed
7. ✅ **Ready for Phase 2**: AskCAD integration can proceed Week 8

---

## NEXT STEPS

**Immediate (Today 2026-07-16 PM)**:
- [ ] Await completion of S6, S7, S9, S10 discovery agents (~30 min remaining)
- [ ] Consolidate 5 segment results into final Tier 2 source manifest
- [ ] Create **TIER-2-CRAWLER-IMPLEMENTATION-ROADMAP.md** (detailed per-segment Week 6-7 plan)

**Tomorrow (2026-07-17)**:
- [ ] Review + approve Tier 2 source list (stakeholder sign-off)
- [ ] Prioritize sources by relevance + public access (start with 60%+ public access tier)
- [ ] Create per-segment crawler stubs (GitHub issues for Week 6 implementation)

**Week 5 (2026-07-28–08-03)**:
- [ ] Implement Tier 2 crawlers (5 teams, 1 per segment)
- [ ] Week 4 retrospective: OCR issues from Tier 1 → apply fixes to Tier 2 PDF parsing
- [ ] Finalize Week 6-7 detailed schedule with resource allocation

---

## OWNERSHIP & ACCOUNTABILITY

| Segment | Week 5 Owner | Week 6 Owner | Week 7 Owner |
|---------|---|---|---|
| **S6 Portos** | S6 Tech Lead | S6 Engineering | S6 QA |
| **S7 Aeroportos** | S7 Tech Lead | S7 Engineering | S7 QA |
| **S8 Saneamento** | S8 Tech Lead | S8 Engineering | S8 QA |
| **S9 Energia** | S9 Tech Lead | S9 Engineering | S9 QA |
| **S10 Barragens** | S10 Tech Lead | S10 Engineering | S10 QA |
| **Cross-Segment** | Infra Lead | DevOps | QA Lead |

---

**Status**: Phase 1a Tier 2 Discovery **UNDERWAY** (S8 ✅, S6/S7/S9/S10 🔄)  
**Next Update**: 2026-07-16 EOD (consolidated 5-segment plan)  
**Last Modified**: 2026-07-16 14:32 UTC  
**Owner**: Phase 1a Program Manager
