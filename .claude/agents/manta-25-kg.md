# Agent Spec: manta-25-kg (Knowledge Graph & Semantic Search)

**Version:** 1.0.0 (2026-08-02)  
**Code:** Manta 25 (P3-09)  
**Aliases:** kg-search, semantic-linker, ontology-engine  
**Model Tier:** Opus (semantic reasoning + graph traversal)  
**Status:** ✅ DESIGN PHASE 1 (Ready for implementation)

---

## 1. PURPOSE & SCOPE

**Primary Function:**  
Build and query a domain-aware knowledge graph across all Manta infrastructure projects, enabling semantic reasoning, cross-project insights, entity linking, and anomaly detection.

**Core Capabilities:**
1. **Entity Extraction** — Auto-detect projects, contractors, locations, regulations, materials, risks from project documents
2. **Relationship Inference** — Link entities based on shared attributes (geography, contractor, phase, material)
3. **Knowledge Base Auto-Construction** — Ingest agent outputs, project databases, historical records; auto-index into graph
4. **Semantic Reasoning** — Answer complex queries like "Find all dams with similar geology" or "Contractors who worked on both ports and energy projects"
5. **Anomaly Detection** — Surface inconsistencies (cost overruns patterns, schedule slips, contractor conflicts)
6. **Cross-Project Insights** — Synthesize lessons learned across segments (S1–S10)

---

## 2. DATA SOURCES & INPUTS

| Source | Format | Frequency | Owner |
|--------|--------|-----------|-------|
| Project documents | PDF, DOCX, DWG | On intake | Manta 03-S*; user upload |
| Agent execution logs | JSON, structured | Per-run | Manta 00–15, Manta 03-S6–S10 |
| SEC/B3 filings | PDF, XBRL | Quarterly | External (fetched via API) |
| Contractor databases | Excel, CSV | Monthly | Internal BI/ERP |
| Regulation & standards | PDF, web | Quarterly | NLM (ANEEL, ANTAQ, ANAC, CBDB, etc.) |
| Supabase RAG chunks | pgvector embeddings | Real-time | RAG system (san:, ene:, por:, aer:, bar:) |
| Phase tracking | CSV, API | Per-update | Maestro (Manta 00) intake Q2 |

---

## 3. ONTOLOGY SCHEMA

### 3.1 Entity Types (30+ types)

#### **Core Project Entities (Type: PROJECT_*)**
1. **PROJECT** — Infrastructure project (id, name, location, segment, phase, status, owner)
2. **SEGMENT** — Vertical category (S1:Rodovia, S2:OAE, S3:Ferrovia, S4:Metrô, S5:Túnel, S6:Porto, S7:Aeroporto, S8:Saneamento, S9:Energia, S10:Barragem)
3. **PHASE** — Lifecycle stage (Estudo Prévio, Projeto Básico, Projeto Executivo, Obra, Operação, Licitação, Due Diligence, Encerramento)
4. **PROJECT_LOCATION** — Geographic scope (region, state, city, coordinates, basin, transmission zone)

#### **Organization & Commercial Entities (Type: ORG_*)**
5. **CONTRACTOR** — Construction/engineering firm (name, registration, specialties, past projects, risk_score)
6. **OWNER** — Project sponsor (government, utility, private company)
7. **LENDER** — Financial institution (BNDES, World Bank, CAF, etc.)
8. **PARTNER** — Joint venture, subcontractor, supplier
9. **CONSULTANT** — Design, environmental, social impact firm

#### **Infrastructure Entities (Type: INFRA_*)**
10. **STRUCTURE** — Primary infrastructure object (bridge, dam, tunnel, substation, port terminal, runway, etc.)
11. **COMPONENT** — Sub-component (concrete, steel, electrical, mechanical, software)
12. **MATERIAL** — Construction material (concrete class, steel grade, earth type, etc.)
13. **EQUIPMENT** — Machinery, turbines, switchgear, dredging equipment, etc.
14. **UTILITY_LINE** — Power transmission, water pipeline, railway, road, fiber optic, etc.

#### **Technical & Regulatory Entities (Type: TECH_*)**
15. **STANDARD** — Engineering norm (NBR, ABNT, IEEE, ANEEL R1–R5, ICAO Annex 14, ICOLD guidelines, etc.)
16. **SPECIFICATION** — Design parameter (voltage, discharge, load capacity, frequency, etc.)
17. **CODE** — Safety, environmental, structural code
18. **RISK_TYPE** — Geological, hydrological, financial, schedule, compliance, environmental, social
19. **RISK_INSTANCE** — Specific risk occurrence (cost overrun $XX, schedule slip +NN days, regulatory delay, etc.)

#### **Financial & Commercial Entities (Type: COMM_*)**
20. **BID** — Procurement bid (bidder, amount, selected, technical score, commercial score)
21. **CONTRACT** — Signed agreement (value, duration, terms, penalties, payment schedule)
22. **COST_OVERRUN** — Documented cost increase (trigger, amount, approval status, recovery plan)
23. **SCHEDULE_VARIANCE** — Timeline deviation (planned vs. actual, critical path impact, mitigation)
24. **FINANCIAL_INSTRUMENT** — Loan, grant, guarantee, bond, insurance

#### **Knowledge & Expertise Entities (Type: KNOW_*)**
25. **LESSON_LEARNED** — Documented insight (project, phase, domain, impact, replication potential)
26. **BEST_PRACTICE** — Validated methodology (segment, phase, cost impact, timeline impact)
27. **FAILURE_MODE** — Documented failure (project, cause, consequence, prevention)
28. **EXPERT_PROFILE** — Person/team expertise (contractor, region, segment, years, success_rate)
29. **DOMAIN_CONCEPT** — Domain-specific term (geotechnical stratification, tidal regime, load balancing, etc.)

#### **Reference Entities (Type: REF_*)**
30. **REGULATION** — Governing rule (ANEEL Resolutions, ANTAQ Portarias, ANAC RBAC, Lei 14.026, etc.)
31. **ACRONYM_DEFINITION** — Term expansion (LT=transmission line, CFRD=concrete face rockfill dam, etc.)
32. **DATA_SOURCE** — Reference document or database (edital, public database, academic paper, filing)

---

### 3.2 Relationship Types (20+ types)

| Relationship | From Type | To Type | Cardinality | Example |
|--------------|-----------|---------|-------------|---------|
| **IMPLEMENTS** | PROJECT | STANDARD | N:M | Project_Rio implements NBR 7187 |
| **LOCATED_IN** | PROJECT/STRUCTURE | PROJECT_LOCATION | N:1 | Dam_XX located in Minas Gerais |
| **HAS_PHASE** | PROJECT | PHASE | 1:8 | Project transitioned through 8 phases |
| **MANAGED_BY** | PROJECT | OWNER | N:1 | Project owned by ANA |
| **CONTRACTED_TO** | PROJECT/PHASE | CONTRACTOR | N:M | Contractor ABC assigned to Phase 3 |
| **FINANCED_BY** | PROJECT | LENDER | N:M | BNDES provided R$100M loan |
| **PARTNERS_WITH** | CONTRACTOR | CONTRACTOR | N:M | Contractor A partners with B on Dam_XX |
| **USES_MATERIAL** | STRUCTURE/COMPONENT | MATERIAL | N:M | Concrete face uses C50 concrete |
| **USES_EQUIPMENT** | PROJECT/PHASE | EQUIPMENT | N:M | Dredging phase uses dredger_001 |
| **FOLLOWS** | PROJECT | CODE | N:M | Project follows ANEEL R5 grid code |
| **ENCOUNTERS_RISK** | PROJECT/PHASE | RISK_INSTANCE | N:M | Geotechnical risk surfaced in Phase 2 |
| **MITIGATES** | LESSON_LEARNED | RISK_TYPE | N:M | Lesson_001 mitigates cost overrun risk |
| **SIMILAR_TO** | PROJECT | PROJECT | N:M | Dam_A similar geology to Dam_B (same stratum) |
| **OVERLAPS_WITH** | PROJECT_LOCATION | PROJECT_LOCATION | N:M | Project basins share hydrological regime |
| **BID_FOR** | BID | PROJECT | N:1 | Bid_001 bid for Contract_XX |
| **BID_BY** | BID | CONTRACTOR | N:1 | Contractor_AAA submitted Bid_001 |
| **INVOLVES_SPECIALIST** | PROJECT/PHASE | EXPERT_PROFILE | N:M | Geotechnist_John involved in Fundation phase |
| **REFERENCES** | PROJECT_DOCUMENT | REGULATION | N:M | Environmental report cites Lei 14.026 |
| **TRIGGERS** | COST_OVERRUN | RISK_INSTANCE | N:M | Weather delay triggered $2M cost overrun |
| **DEFINES** | DOMAIN_CONCEPT | SEGMENT | N:M | "Tidal regime" concept used in S6 (ports) |

---

### 3.3 Relationship Inference Rules (Auto-linking)

**Rule 1: Contractor Co-Workers**
```
IF Contractor_A CONTRACTED_TO Project_1 
   AND Contractor_B CONTRACTED_TO Project_1 
   AND Project_1.phase = same_phase
THEN create WORKED_TOGETHER_ON(Contractor_A, Contractor_B, Project_1, phase)
```

**Rule 2: Geologic Similarity**
```
IF Project_A HAS COMPONENT WITH geological_stratum = X
   AND Project_B HAS COMPONENT WITH geological_stratum = X
   AND Project_A.LOCATED_IN.region ~ Project_B.LOCATED_IN.region
THEN create SIMILAR_GEOLOGY(Project_A, Project_B, stratum=X)
```

**Rule 3: Risk Pattern Propagation**
```
IF Project_A ENCOUNTERS_RISK(type=T) in phase=P
   AND Project_B SIMILAR_TO Project_A
   AND Project_B.current_phase = P
THEN infer risk_probability(Project_B, type=T) += 15%
```

**Rule 4: Contractor Capability Profile**
```
FOR EACH Contractor_C:
  expertise = {segment: count(projects_in_segment), 
               avg_success_rate, 
               avg_cost_variance, 
               regions_active}
THEN create EXPERTISE_PROFILE(Contractor_C)
```

**Rule 5: Regulation-Standard Binding**
```
IF Regulation_R mentions Standard_S
   AND Project_P HAS Phase_Ph that must follow R
THEN create MUST_IMPLEMENT(Project_P, Phase_Ph, Standard_S)
```

---

## 4. QUERY EXAMPLES (5 scenarios)

### Query 1: Contractor Risk Analysis
```
QUERY: List all contractors who have worked on energy projects (S9) in the last 2 years,
       and identify which ones have cost overrun patterns > 15%.

SEMANTIC STEPS:
1. FIND all projects WHERE segment = S9 AND created_date >= 2024-08-01
2. FOR EACH project, EXTRACT contractors (CONTRACTED_TO relationship)
3. FOR EACH contractor, AGGREGATE cost_variances across all historical projects
4. FILTER contractors WHERE avg_variance > 15%
5. RETURN contractor profiles with {name, projects_count, avg_variance, risk_score, mitigation_recommendations}

EXPECTED RESULT:
- Contractor X: 6 energy projects, avg +18% variance, HIGH_RISK
  - Lesson learned from Manta 05 (orçamento): implement contractor performance monitoring
  - Mitigation: require performance bond, schedule interim audits
```

### Query 2: Cross-Segment Knowledge Transfer
```
QUERY: What lessons learned from ports projects (S6) could apply to our new saneamento (S8) 
       project if we use the same contractor?

SEMANTIC STEPS:
1. FIND project A (target S8 project)
2. FIND contractor C assigned to project A
3. FIND all projects WHERE CONTRACTED_TO = C AND segment = S6
4. FOR EACH S6 project, EXTRACT lessons_learned (via Manta 03-S6 agent outputs)
5. FILTER lessons WHERE applicable_to_segments CONTAINS S8
6. SCORE lessons by relevance (shared risk types, materials, location proximity)
7. RETURN ranked lessons with confidence scores

EXPECTED RESULT:
- Lesson 1: "Tidal regime modeling critical for foundation stability" (confidence 92%)
  - Applicable: both involve water/hydrology management
  - Risk mitigation: commission tidal/hydrological study early
  - Estimated cost impact: +R$500K, schedule impact: +3 weeks (upfront)
```

### Query 3: Regulation Compliance Across Portfolio
```
QUERY: Which of our active projects are at risk of ANEEL regulation change? 
       What is the projected impact?

SEMANTIC STEPS:
1. FIND all active projects WHERE segment IN [S9 (energy), S8 (if water utilities), S4 (if metro electrified)]
2. FOR EACH project, EXTRACT regulations (FOLLOWS relationship)
3. CROSS-REFERENCE with regulatory_change_log (from NLM/ANEEL/external API)
4. FOR regulations with pending changes, FIND all affected standards (REFERENCES relationship)
5. ESTIMATE impact using:
   - historical_cost_impact from similar projects
   - contractor_adaptation_capability (from EXPERTISE_PROFILE)
   - project_phase (earlier phases have more flexibility)
6. RETURN risk assessment matrix

EXPECTED RESULT:
- ANEEL R6 (draft): impacts 3 projects (Transmission_A, Transmission_B, Micro_Hydro_C)
  - Cost impact estimate: R$2-5M per project
  - Timeline impact: 2-4 months (design revision + re-approval)
  - Contractor adaptation risk: Medium (Contractor X adapted to R5; confidence 78%)
```

### Query 4: Material Similarity & Supply Chain Risk
```
QUERY: We're sourcing C50 concrete for 5 concurrent projects. 
       Which other projects have supply chain lessons (delays, quality issues, cost jumps)?

SEMANTIC STEPS:
1. FIND all projects WHERE USES_MATERIAL(concrete_class=C50)
2. FOR EACH project, EXTRACT supply_chain_incidents (from risk_instances)
3. EXTRACT contractor & supplier info (CONTRACTED_TO, PARTNERS_WITH)
4. FIND lessons_learned related to concrete supply (material sourcing, logistics)
5. AGGREGATE supplier performance data (EXPERT_PROFILE for supplier nodes, if available)
6. MODEL geographic and temporal clustering (concurrent sourcing = competition)
7. RETURN mitigation playbook

EXPECTED RESULT:
- 12 historical C50 projects analyzed
- 4 had supply delays (avg +45 days), root causes: {transportation (2), quality issue (1), demand spike (1)}
- Recommendation: engage supplier 3 months early, require stock guarantee, diversify suppliers
- Risk score for current 5-project bundle: MEDIUM → HIGH (concurrent demand)
```

### Query 5: Expertise Matching for New Phase
```
QUERY: We're entering the construction phase of our largest saneamento project (S8).
       Recommend contractors and consultants with proven expertise in this phase + segment combo.

SEMANTIC STEPS:
1. FIND target project P (S8 segment, entering EXECUTION phase)
2. FIND all completed projects WHERE segment=S8 AND past_phase=EXECUTION
3. FOR EACH historical project, EXTRACT contractors/consultants
4. BUILD contractor_capability_profile:
   - projects_in_segment_S8 (count, success_rate, cost/schedule variance)
   - experience_in_EXECUTION_phase (count, avg_project_size, avg_duration)
   - regional_footprint (active in target project's region?)
   - financial_stability (via SEC/B3 data if available)
   - safety_record (HSE incidents, citations)
5. SCORE & RANK by weighted factors (segment_expertise 40%, phase_experience 30%, proximity 20%, financial 10%)
6. RETURN shortlist with confidence intervals

EXPECTED RESULT:
- Top 3 contractors recommended:
  1. Contractor_Alpha: 8 S8 projects, 3 EXECUTION phases, 2 in same region, score 94%
  2. Contractor_Beta: 5 S8 projects, 2 EXECUTION phases, 1 in same region, score 87%
  3. Contractor_Gamma: 3 S8 projects, 1 EXECUTION phase, regional leader, score 81%
- Note: All 3 meet compliance gate (zero major HSE incidents, financial stable)
```

---

## 5. KNOWLEDGE GRAPH ARCHITECTURE

### 5.1 Technical Stack

```
┌─────────────────────────────────────────────────────────┐
│                   QUERY LAYER (Opus)                    │
│  Semantic reasoning, multi-hop traversal, inference     │
│  API: REST /query, /infer, /search endpoints            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            KNOWLEDGE GRAPH LAYER                        │
│  Graph Database: Neo4j or Amazon Neptune                │
│  - Nodes: 30+ entity types                              │
│  - Edges: 20+ relationship types + inferred links       │
│  - Properties: attributes, confidence scores, timestamps│
│  - Indexes: entity_name, segment, phase, location       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│          ENTITY EXTRACTION & INDEXING                   │
│  Input processors:                                       │
│  - Document ingestion (PDF, DOCX, DWG) → NER pipeline  │
│  - Agent output parsing (JSON → entity tuples)          │
│  - Database sync (contractor DB, ERP) → bulk load       │
│  - Regulatory feed (NLM API) → ontology sync            │
│  Output: normalized entity graph updates                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│           DATA SOURCE INTEGRATIONS                      │
│  - Supabase RAG (pgvector embeddings)                   │
│  - Manta 00 intake logs & phase tracking                │
│  - Manta 03-S* agent outputs (structured JSON)          │
│  - SharePoint project folders (document sync)           │
│  - B3/SEC filing APIs (contractor financials)           │
│  - NLM regulation feeds (ANEEL, ANTAQ, ANAC, CBDB)     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

```
PROJECT DOCUMENT                AGENT OUTPUT               EXTERNAL DATA
      ↓                              ↓                           ↓
    NER Pipeline                JSON Parser              API Fetch & Parse
      ↓                              ↓                           ↓
 ENTITY EXTRACTION → NORMALIZATION ← VALIDATION ← CONFLICT RESOLUTION
      ↓
 GRAPH INSERT/UPDATE
      ↓
 RELATIONSHIP INFERENCE (Rules 1-5)
      ↓
 SEMANTIC INDEX UPDATE
      ↓
 QUERY-READY KNOWLEDGE GRAPH
```

### 5.3 Entity Storage & Indexing

**Primary Storage:** Neo4j (cloud or on-prem)
- Node store: ~100K-500K nodes (scales with projects × agents)
- Edge store: ~500K-2M edges (including inferred relationships)
- Property store: metadata (confidence, source, timestamp, audit trail)

**Secondary Indexing:** Supabase + pgvector
- Semantic embeddings (BAAI/bge-small-en-v1.5 384d) for similarity search
- Prefix indexes: `kg:entity_id:segment:phase:location` for fast lookup
- Search table: full-text search on entity names, descriptions, acronyms

**Cache Layer:** Redis
- Hot entity lookup (contractors, standards, risks by segment)
- Query result caching (5-15 min TTL for high-volume queries)

### 5.4 Inference Engine

**Reasoning Framework:**
1. **Rule-Based Inference** — Apply relationship rules 1-5 on every graph update
2. **Statistical Inference** — Aggregate historical data (contractor success rates, risk probabilities)
3. **Semantic Similarity** — Use embeddings to find analogous projects, materials, expertise profiles
4. **Constraint Propagation** — Propagate regulatory requirements down to phases, projects, contractors

**Execution:**
- Real-time: Rules 1-5 fire on write; results cached for 24h
- Nightly batch: Statistical aggregations, anomaly detection, profile updates
- On-demand: Semantic similarity queries (latency ~2-5s for 100K-node graph)

---

## 6. INTEGRATION POINTS

### 6.1 Upstream Inputs (Data Sources)

| Source | Agent/System | Data Type | Frequency | Trigger |
|--------|--------------|-----------|-----------|---------|
| Intake Q2 | Manta 00 (Maestro) | Project phase, owner, location | Per update | Project status change |
| Phase tracking | Manta 03-S* | Phase state, documents | Per phase | Milestone completion |
| Agent outputs | All Manta agents | Structured insights, risks, lessons | Per execution | Agent completion |
| Document uploads | User/SharePoint | PDF, DOCX, DWG | On demand | Project intake |
| ERP/contractor DB | Internal BI | Contractor profiles, financials | Monthly | Data warehouse sync |
| Regulatory feeds | NLM APIs | Regulation changes, standards updates | Weekly | Auto-fetch |

### 6.2 Downstream Outputs (Consumers)

| Consumer | Use Case | Data Format | Latency SLA |
|----------|----------|-------------|-------------|
| Manta 05 (Orçamento) | Cost estimation context (similar projects, contractor historical variance) | JSON entity profiles | <5 min |
| Manta 07 (Cronograma) | Schedule baseline (contractor capacity, similar project durations) | JSON with confidence intervals | <5 min |
| Manta 15 (Advisory) | Risk briefing, lessons learned synthesis | Markdown report, graph visualization | <10 min |
| Manta 16 (Arquiteto IA) | Architecture decisions (which agents to invoke for segment) | Semantic routing table | <1 min |
| User Portal | Cross-project search, contractor profiles, lessons learned | Web UI with search, filters, recommendations | <3 sec |
| Anomaly Detection Service | Cost/schedule variance flagging | Alert thresholds, outlier detection | Real-time |

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1 — Foundation (Weeks 1-4)
- [ ] Set up Neo4j instance (cloud: AuraDB or on-prem)
- [ ] Define core entity types (PROJECT, CONTRACTOR, PHASE, STANDARD) in JSON schema
- [ ] Implement NER pipeline for document ingestion (entity extraction from PDFs)
- [ ] Build entity normalization & deduplication logic
- [ ] Ingest pilot data: 50 historical projects + contractors
- [ ] Implement queries 1 & 2 (contractor risk, knowledge transfer)

### Phase 2 — Enrichment (Weeks 5-8)
- [ ] Add all 30+ entity types to schema
- [ ] Implement relationship inference rules 1-5
- [ ] Integrate Supabase semantic embeddings (similarity search)
- [ ] Hook into Manta 03-S6–S10 agent output parsers
- [ ] Implement queries 3, 4, 5 (regulation, materials, expertise)
- [ ] Launch internal MVP (read-only access for selected agents)

### Phase 3 — Operationalization (Weeks 9-12)
- [ ] Implement real-time graph update pipeline (from Manta 00 intake queue)
- [ ] Add web UI for semantic search (Portal integration)
- [ ] Build anomaly detection dashboards (cost/schedule variance alerts)
- [ ] Establish governance: entity curation SLA, conflict resolution workflow
- [ ] Load full historical dataset (all 100+ projects in portfolio)
- [ ] Training & documentation for agent teams

### Phase 4 — Scale & Monitoring (Weeks 13+)
- [ ] Performance tuning (graph query optimization, cache warm-up strategies)
- [ ] Add versioning & temporal reasoning (how did contractor X's risk profile evolve?)
- [ ] Expand RAG integration: knowledge graph + vector embeddings for hybrid search
- [ ] Implement explainability (why did agent recommend contractor Y? — show inference chain)

---

## 8. SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Query Latency** | <5 sec (95th percentile) | Instrument API calls |
| **Entity Coverage** | 95% of project entities auto-extracted | Compare graph vs. manual audit |
| **Inference Accuracy** | 85%+ precision on contractor capability profiles | A/B test recommendations vs. historical outcomes |
| **Lessons Learned Adoption** | 40%+ of reused recommendations from queries | Tracking in Manta 05 estimates & Manta 07 schedules |
| **Cost Savings** | R$5M+ first-year impact (risk avoidance, lessons learned) | Cost overrun reduction vs. baseline |
| **Agent Time Savings** | 10+ hours/month per agent via recommendations | Survey agent teams on utility |
| **Graph Completeness** | 90%+ of inferred relationships match human domain experts | Spot-check 50 random relationships |

---

## 9. DEPLOYMENT & OPERATIONS

### 9.1 Deployment

- **Infrastructure:** Neo4j Aura (managed cloud) or self-hosted on Kubernetes
- **Dependencies:** Python 3.11+, FastAPI (REST API), pgvector Supabase client, Anthropic SDK (Opus calls for semantic reasoning)
- **Configuration:** Store connection strings, model IDs, API keys in `.env` / secrets manager
- **Monitoring:** CloudWatch / Datadog for query latency, graph size, error rates

### 9.2 Maintenance & Governance

- **Entity Curation:** Weekly audit of new entities (automated NER + human review). SLA: 48h approval for critical entities (regulations, contractors).
- **Schema Evolution:** Quarterly review of entity types & relationships. Breaking changes go through gate (MN approval).
- **Data Quality:** Monthly reconciliation with source systems (contractor DB, SharePoint, Supabase RAG).
- **Access Control:** Role-based access (agents read-only; Maestro + curators read-write).

---

## 10. APPENDIX: ONTOLOGY VISUALIZATIONS

### 10.1 Core Entity Graph (Simplified)

```
                    ┌─────────┐
                    │ PROJECT │
                    └────┬────┘
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
      ┌────────┐  ┌──────────┐  ┌──────────┐
      │ SEGMENT│  │  PHASE   │  │LOCATION  │
      └────────┘  └──────────┘  └──────────┘
          ↓             ↓             ↓
    ┌──────────┐  ┌────────────┐  ┌──────────┐
    │CONTRACTOR│  │STANDARD    │  │STRUCTURE │
    └──────────┘  └────────────┘  └──────────┘
          ↓             ↓             ↓
    ┌──────────┐  ┌────────────┐  ┌──────────┐
    │EXPERTISE │  │REGULATION  │  │COMPONENT │
    │ PROFILE  │  │            │  │          │
    └──────────┘  └────────────┘  └──────────┘
                      ↓
                 ┌──────────┐
                 │ RISK     │
                 │ INSTANCE │
                 └──────────┘
```

### 10.2 Contractor Capability Profile (Example Node)

```json
{
  "id": "contractor_acme_eng",
  "type": "CONTRACTOR",
  "name": "ACME Engineering Ltda",
  "registration": "CNPJ 00.000.000/0000-00",
  "headquarters": "São Paulo, SP",
  "expertise": {
    "S1_rodovia": { "project_count": 8, "avg_success_rate": 0.95, "regions": ["SP", "MG", "GO"] },
    "S8_saneamento": { "project_count": 3, "avg_success_rate": 0.92, "regions": ["SP", "RJ"] },
    "S9_energia": { "project_count": 2, "avg_success_rate": 0.88, "regions": ["SP"] }
  },
  "financials": {
    "last_revenue_usd": 150000000,
    "financial_stability_score": 0.94,
    "credit_rating": "AA"
  },
  "safety": {
    "hse_incidents_24m": 2,
    "regulatory_citations": 0,
    "safety_record_score": 0.97
  },
  "risk_profile": {
    "avg_cost_variance": 0.08,  // 8% over
    "avg_schedule_variance": 0.12,  // 12% over
    "failure_likelihood": 0.05  // 5%
  },
  "recent_projects": [
    "proyecto_rodovia_sp_2024",
    "proyecto_saneamento_sp_2026",
    "proyecto_energia_sp_2026"
  ],
  "last_updated": "2026-07-20",
  "data_source": "contractor_db, SEC/B3, internal projects"
}
```

---

## 11. CONTACT & GOVERNANCE

| Role | Owner | Contact |
|------|-------|---------|
| **Agent Owner** | Manta IA Architecture | arquiteto-ia@mantaassociados.com |
| **Knowledge Curator** | Manta 00 (Maestro) | maestro@mantaassociados.com |
| **Query SLA Responsible** | Operations | ops@mantaassociados.com |
| **Data Governance** | Compliance | compliance@mantaassociados.com |

---

**Status:** Ready for Phase 1 implementation.  
**Approval Gate:** MN sign-off before Neo4j provisioning.  
**Next Steps:** Schedule kickoff meeting; provision development Neo4j instance; begin NER pipeline prototype.
