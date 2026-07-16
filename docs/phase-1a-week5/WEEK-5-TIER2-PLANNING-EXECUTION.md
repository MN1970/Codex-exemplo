# WEEK 5 EXECUTION PLAN — Tier 2 Source Discovery & Crawler Development
## 2026-07-28 to 2026-08-03
## Parallel: Week 4 Validation Complete, Week 5 Tier 2 Implementation Begins

---

## WEEK 5 OBJECTIVES

| Objective | Owner | Success Criteria | Blocker Risk |
|-----------|-------|------------------|--------------|
| **Finalize Tier 2 source manifest** | Segment leads | All 5 segments deliver 25-30 sources each (130-150 total) | Medium: agents may find < 25 sources |
| **Create per-segment crawler implementations** | Engineering | 5 GitHub projects (1 per segment) with 30+ crawler tasks | Low: crawler architecture already proven |
| **Design embedding pipeline for 469k chunks** | DevOps | Cost estimate $25-30, latency plan, batch sizing | Low: OpenAI API proven, cost negligible |
| **Resolve HTTP 403 blockers from Tier 1** | S7, S10 teams | Document alternative URL strategies, test fallbacks | Medium: ANAC, ICOLD may have limited alt access |
| **Create Week 6-7 detailed schedule** | PM | Day-by-day crawler deployment + validation plan | Low: Phase 1a schedule already established |
| **Conduct Tier 2 source prioritization** | Leadership | Rank all sources by relevance + public access; start with top 60 | Low: prioritization framework simple |

---

## DAILY BREAKDOWN

### MONDAY 2026-07-28 — Tier 2 Discovery Consolidation

**Morning (8:00–12:00)**:
- [ ] Await final Tier 2 discovery results (S6, S7, S10 if not already complete)
- [ ] Consolidate all 5 segment results into master spreadsheet:
  ```
  | Segment | Source # | URL | Type | Est. Docs | Relevance | Public? | Category | Notes |
  | S6 Portos | 1 | ... | ... | ... | 9.2/10 | 100% | associations | IAPH guidelines |
  | ... |
  ```
- [ ] Compute aggregate stats:
  - Total sources: 130–150
  - Total documents: 45k–50k
  - Total chunks (after dedup): ~469k (goal)
  - Public access %: 55–65%
- [ ] Flag any segment with < 25 sources → escalate for additional discovery
- [ ] Create GitHub Project `phase-1a-tier2-sources` with all sources as issues + labels by segment/category

**Afternoon (12:00–18:00)**:
- [ ] **S6 Portos**: Review 30 Tier 2 sources, categorize (associations, standards, academia, tech, legislation, public repos)
- [ ] **S7 Aeroportos**: Identify & document HTTP 403 patterns from Tier 1; design fallback crawlers
- [ ] **S9 Energia**: Confirm ONS SIGEN access + EPE/ANEEL data availability; design incremental crawlers
- [ ] **S10 Barragens**: Escalate ICOLD database 403; identify public mirror (Web Archive, ResearchGate)
- [ ] **S8 Saneamento**: Finalize AySA OAuth2 authentication + SNIS municipal recursion design

**Deliverables (EOD Mon)**:
- [ ] Master Tier 2 source spreadsheet (5 segments × 25-30 sources = 130-150 rows)
- [ ] GitHub Project `phase-1a-tier2-sources` with prioritized issues
- [ ] Per-segment notes on implementation complexity + blockers

---

### TUESDAY 2026-07-29 — Crawler Architecture & Skeleton Implementation

**Morning (8:00–12:00)**:
- [ ] Create skeleton crawlers for all 5 segments in parallel branches:
  ```
  backends/
    portos/crawlers/portos_rag_tier2_SKELETON.py        (700 lines, 10 source adapters)
    aeroportos/crawlers/aeroportos_rag_tier2_SKELETON.py (650 lines, 8 adapters)
    saneamento/crawlers/saneamento_rag_tier2_SKELETON.py (750 lines, 12 adapters)
    energia/crawlers/energia_rag_tier2_SKELETON.py        (800 lines, 14 adapters)
    barragens/crawlers/barragens_rag_tier2_SKELETON.py    (700 lines, 12 adapters)
  ```
  Each includes:
  - Base `Crawler` class with retries, rate limiting, session management
  - 10-14 source adapters (one per major Tier 2 source category)
  - Configuration for API keys, fallback URLs, auth methods (OAuth2, basic, etc.)
  - Chunking strategy per source (PDFs, HTML, JSON, structured data)
  - Error handling + logging

- [ ] Test skeleton crawlers on dev against 10% sample per segment (50-100 docs each)

**Afternoon (12:00–18:00)**:
- [ ] Review test results from morning; identify early blockers:
  - Which sources require auth (OAuth2, API keys)?
  - Which sources have rate limits?
  - Which sources fail on >10% of documents?
- [ ] **Special focus on Tier 1 blocker resolution**:
  - S7 Aeroportos: Test alternative ANAC URLs (ICAO portal, FAA archive, Brazil aviation school libraries)
  - S10 Barragens: Test ICOLD Web Archive mirror, CBDB open access, Zenodo repository
- [ ] Create implementation roadmap for Wednesday-Friday (source priority order)

**Deliverables (EOD Tue)**:
- [ ] 5 skeleton crawlers (30-50% complete, skeleton + adapters)
- [ ] GitHub branches: `feature/tier2-crawlers-s6`, `feature/tier2-crawlers-s7`, etc.
- [ ] Early blocker log + mitigation strategies documented

---

### WEDNESDAY 2026-07-30 — Tier 2 Crawler Development Sprint 1

**Parallel across 5 teams (Morning + Afternoon, 8:00–18:00)**:

#### S6 Portos
- **Crawl targets** (top 8 priority sources by relevance):
  1. IAPH (International Association of Port Authorities) — standards + case studies
  2. AAPA (American Association of Port Authorities) — design guidelines, white papers
  3. PIANC (Permanent International Association of Navigation Congresses) — technical publications
  4. Port of Rotterdam / Singapore design docs — case studies
  5. Brazilian ports API (Antares, SISDOC) — operational data
  6. Lloyd's List Intelligence — market data, port operations
  7. Port Technology International (journal) — research + case studies
  8. Brazilian port operator websites (TCIPSA, Portonave, etc.) — technical specs
- **Implementation**: Create 8 source adapters; test on 500 docs total; deploy to dev
- **Expected chunks**: 1,200–1,500 from these 8 sources

#### S7 Aeroportos
- **Crawl targets** (top 8):
  1. ACI (Airports Council International) — airport standards, best practices
  2. ACRP (Airport Cooperative Research Program) — research reports
  3. ALPA (Air Line Pilots Association) — operational procedures, safety
  4. EASA (European Union Aviation Safety Agency) — regulations, certifications
  5. Civil Aviation Authority of Brazil (ANAC) supplementary regulations
  6. OpenSky Network — flight data, traffic analysis
  7. Brazilian airport operator websites (Infraero, Viracopos, etc.) — operational specs
  8. NOTAM database (FAA) — procedure updates, restrictions
- **HTTP 403 mitigation**: Test 2-3 alternative URL strategies per source
- **Implementation**: 8 adapters; test on 500 docs; deploy to dev
- **Expected chunks**: 1,000–1,200 from these 8 sources

#### S8 Saneamento
- **Crawl targets** (top 10):
  1. AySA (Agua y Saneamientos Argentinos) — design + operational manuals (OAuth2)
  2. SNIS (Sistema Nacional de Informações sobre Saneamento) — municipal data (PMSB recursive crawl)
  3. ABCON (Associação Brasileira de Concessionárias) — industry reports
  4. FUNASA (Fundação Nacional de Saúde) — rural saneamento guidelines
  5. SABESP (São Paulo water utility) — technical documentation
  6. IWA (International Water Association) — water supply + wastewater standards (40% open)
  7. ANA (Agência Nacional de Águas) — water resources, PMSB databases
  8. IBGE (Saneamento census) — structured data
  9. DataSUS — epidemiological waterborne disease data
  10. PMSBs (5,570 municipalities) — locally-specific saneamento plans
- **Special**: Implement SNIS municipal recursion (5k+ municipalities); deduplicate down to representative 500
- **Implementation**: 12 adapters (SNIS gets 3 sub-adapters); test on 1,500 docs; deploy to dev
- **Expected chunks**: 1,800–2,200 from these 12 sources (highest volume Tier 2)

#### S9 Energia
- **Crawl targets** (top 10):
  1. ONS (Operador Nacional do Sistema) — SIGEN (GeoJSON), boletins, despacho
  2. ANEEL (Agência Nacional de Energia Elétrica) — concessões, resoluções, editais
  3. EPE (Empresa de Pesquisa Energética) — PDE (10-year expansion plan), relatórios
  4. CCEE (Câmara de Comercialização de Energia Elétrica) — market data (partial API)
  5. Lei 10.848/2004 + Lei 12.783/2013 — regulatory foundation
  6. ABNT NBR standards (5460, 14039, 6021, 15847) — technical norms (partial paywall)
  7. CIGRÉ Brasil — technical papers, working groups
  8. IEEE Xplore — transmission + power system research (paywall)
  9. Fabricante WEG — Brazilian equipment documentation
  10. Siemens + ABB whitepapers — substation + LT technology
- **Implementation**: 12 adapters; ANEEL CEDOC API + ONS SIGEN GeoJSON + PDF crawling; test on 1,200 docs
- **Expected chunks**: 1,500–1,800 from these 12 sources

#### S10 Barragens
- **Crawl targets** (top 10):
  1. Lei 12.334/2010 — regulatory foundation + PDF text
  2. CBDB (Committee on Dams and Embankments) — technical standards, case studies
  3. SNISB (Sistema Nacional de Informações sobre Segurança de Barragens) — Brazilian dam registry
  4. SIGBM (Sistema de Informações de Geotecnia e Barragens) — geotechnical data
  5. ICOLD (International Commission on Large Dams) — dam safety guidelines (partial access)
  6. Web Archive / ResearchGate — ICOLD mirrors + academic papers
  7. ANA (Agência Nacional de Águas) — water resources, dam safety
  8. ANM (Agência Nacional de Mineração) — mining dam safety + design guidelines
  9. Brazilian dam operator sites (Eletrobras, Furnas, Duke Energy) — technical reports
  10. DNPM/ANM resoluções — mining + dam regulation updates
- **Blockers**: ICOLD 403 expected; use Web Archive + ResearchGate + Zenodo mirrors
- **Implementation**: 12 adapters; SNISB + SIGBM APIs if available; test on 1,000 docs
- **Expected chunks**: 1,200–1,500 from these 12 sources

**Deliverables (EOD Wed)**:
- [ ] 5 teams complete development of 8-14 adapters per segment
- [ ] All crawlers tested on 500-1,500 docs per segment (success rate >= 85%)
- [ ] Chunks staged in Supabase dev (validation only, not ingested to production yet)
- [ ] Blockers logged + mitigations tested (especially S7, S10)

---

### THURSDAY 2026-07-31 — Tier 2 Crawler Validation & Optimization

**Morning (8:00–12:00)**:
- [ ] All 5 teams run full Tier 2 crawls against all ~30 sources per segment (NOT full-crawl, just discovery mode)
  - S6: 8 sources × 50 docs each = 400 docs
  - S7: 8 sources × 50 docs = 400 docs
  - S8: 12 sources × 100 docs = 1,200 docs
  - S9: 12 sources × 80 docs = 960 docs
  - S10: 12 sources × 50 docs = 600 docs
  - **Total**: ~3,500 test documents

- [ ] Chunk & embed sample (OpenAI):
  - Sample 500 chunks (100 per segment)
  - Batch embed via API (cost: ~$0.01)
  - Measure: latency per chunk, error rate, embedding quality

- [ ] QA validation:
  - FTS test: 3 domain queries per segment on sample chunks
  - Vector search: 3 semantic similarity tests per segment
  - Metadata completeness: 100% of fields populated
  - OCR quality: Manual inspection of 20 PDF-sourced chunks per segment

**Afternoon (12:00–18:00)**:
- [ ] Optimize chunking parameters based on QA feedback:
  - Adjust target chunk size (350-450 tokens) if too short/long
  - Adjust overlap (50 tokens) if creating duplicates
  - Fix PDF extraction issues (if OCR > 5% severe)
  - Update metadata templates per source

- [ ] Cost estimation for full Tier 2 ingestion (469k chunks):
  - Document chunking: ~2-3 hours (parallel batch)
  - Embedding: ~15-20 minutes (OpenAI batch, 100 req/min)
  - Ingestion: ~30-40 minutes (Supabase throughput)
  - Total incremental cost: $15-20 (embeddings only)

- [ ] Create **Week 6-7 detailed schedule** (day-by-day crawler runs, chunk targets, ingest order)

**Deliverables (EOD Thu)**:
- [ ] QA validation report (FTS/vector/OCR pass/fail per segment)
- [ ] Chunking optimization applied to all crawlers
- [ ] Cost estimate + timeline for full Tier 2 (confirmed budget)
- [ ] Week 6-7 detailed schedule (daily crawler runs + targets)

---

### FRIDAY 2026-08-02 — Week 5 Retrospective & Week 6 Kickoff Planning

**Morning (8:00–12:00)**:
- [ ] **Retrospective on Tier 2 discovery + crawler development**:
  - How many sources discovered per segment? (Target: 25-30, accept >25)
  - Crawler completion rate per segment? (Target: 80%+ of sources having working adapters by EOD Thu)
  - Major blockers encountered + mitigations applied
  - Cost + timeline estimates accuracy check

- [ ] **Week 4 validation results review** (from Tier 1 completion):
  - Total Tier 1 chunks ingested: 45k–55k ✓?
  - FTS validation results per segment ✓?
  - Vector search quality confirmed ✓?
  - OCR issues < 5% ✓?
  - Go/No-Go decision: PROCEED to Week 6 ✓?

- [ ] **Decide: Proceed with Week 6-7 Tier 2 or extend Week 5 blockers**
  - If Go: Finalize crawlers + prepare for Monday Week 6 kickoff
  - If No-Go: Escalate blockers + adjust schedule

**Afternoon (12:00–18:00)**:
- [ ] **Week 6 preparation**:
  - [ ] Finalize GitHub Projects for all 5 segments (ready for Monday standup)
  - [ ] Create crawlers README (installation, configuration, runtime instructions)
  - [ ] Prepare CI/CD pipeline for Week 6 parallel deployment
  - [ ] Allocate engineering resources (1 engineer per segment minimum)
  - [ ] Schedule daily standups (Mon–Fri 9:00 UTC for 5 teams)

- [ ] **Tier 2 risk mitigation planning**:
  - [ ] Document HTTP 403 fallback URLs (S7, S10)
  - [ ] Prepare alternative data sources if primary fails (5-10% fallback per segment)
  - [ ] Plan escalation contacts (data providers, government APIs, research repositories)

- [ ] **Create communication plan**:
  - [ ] Weekly summary to leadership: "Week 5 Tier 2 discovery + crawler dev complete; Week 6 ingestion ready"
  - [ ] Segment-specific updates to stakeholders (portos associations, ANAC, ANEEL, etc.)

**Deliverables (EOD Fri)**:
- [ ] Week 5 retrospective memo (discovery results, crawler status, go/no-go decision)
- [ ] Week 4 Tier 1 validation results (confirmed 45k+ chunks, FTS/vector QA passed)
- [ ] Week 6-7 detailed schedule (day-by-day, hour-by-hour if needed)
- [ ] GitHub Projects ready for Monday kickoff
- [ ] Risk mitigation plan + escalation contacts documented

---

## RESOURCE ALLOCATION (Week 5)

| Role | Segment | Hours/Week | Responsibility |
|------|---------|-----------|---|
| **Engineering Lead (S6)** | Portos | 40 | Crawler dev (8 adapters), API integration, testing |
| **Engineering Lead (S7)** | Aeroportos | 40 | Crawler dev (8 adapters), 403 fallback design, testing |
| **Engineering Lead (S8)** | Saneamento | 40 | Crawler dev (12 adapters), AySA OAuth2, SNIS recursion, testing |
| **Engineering Lead (S9)** | Energia | 40 | Crawler dev (12 adapters), SIGEN/ANEEL API, testing |
| **Engineering Lead (S10)** | Barragens | 40 | Crawler dev (12 adapters), ICOLD fallback, SNISB/SIGBM APIs, testing |
| **QA Lead** | All | 40 | Validation (FTS, vector, OCR, metadata), optimization feedback |
| **DevOps** | All | 30 | Embedding pipeline design, cost estimation, CI/CD setup for Week 6 |
| **PM** | All | 30 | Schedule coordination, blocker escalation, stakeholder updates |
| **Infra** | All | 15 | Supabase config, monitoring, performance tuning |

**Total**: ~315 hours/week (7 FTE equivalent)

---

## SUCCESS CRITERIA (Week 5)

**By EOD Friday (2026-08-02)**:

1. ✅ **Tier 2 Discovery Complete**: All 5 segments have 25-30 sources each (130-150 total)
2. ✅ **Crawlers Functional**: 80%+ of Tier 2 sources have working adapters (tested on samples)
3. ✅ **Chunking Optimized**: Sample 500 chunks validated (FTS, vector search, OCR < 5%)
4. ✅ **Cost Estimated**: $15-20 for full Tier 2 embedding (confirmed with leadership)
5. ✅ **Week 4 Validation**: Tier 1 ingestion confirmed 45k-55k chunks, go/no-go decision made
6. ✅ **Go Decision**: Leadership approves proceeding with Week 6-7 Tier 2 ingestion
7. ✅ **Week 6 Ready**: Crawlers tested, CI/CD prepared, teams briefed on Monday schedule

---

## BLOCKERS & ESCALATION

| Blocker | Probability | Impact | Escalation |
|---------|---|---|---|
| Tier 2 discovery finds < 25 sources per segment | Low (10%) | Medium | Re-run discovery agents Wed if needed |
| Crawler development slips (adapters incomplete) | Medium (25%) | Medium | Prioritize top 8-10 sources per segment only |
| HTTP 403 blockers unresolved (S7, S10) | Medium (30%) | Medium | Escalate to data providers (ANAC, ICOLD) EOD Tue |
| Embedding cost exceeds budget ($30) | Low (5%) | Low | Switch to local embeddings (sentence-transformers) |
| Week 4 Tier 1 validation fails | Low (5%) | High | PAUSE Week 6; debug Tier 1 ingestion issues |

---

## NEXT STEPS

**Monday 2026-07-28 EOD**: 
- All 5 segments deliver Tier 2 source lists
- GitHub Project `phase-1a-tier2-sources` created with 130+ issues

**Friday 2026-08-02 EOD**:
- Week 5 retrospective + Week 6 readiness confirmed
- Go/No-Go decision communicated to leadership

**Monday 2026-08-04**:
- Week 6 Tier 2 full ingestion begins (45k-50k documents → 469k chunks)

---

**Owner**: Phase 1a Program Manager  
**Last Updated**: 2026-07-16  
**Status**: Ready for Week 5 execution (pending Tier 2 discovery completion)
