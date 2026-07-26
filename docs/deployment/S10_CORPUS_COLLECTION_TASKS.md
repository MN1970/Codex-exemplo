# S10 Fine-Tuning: Corpus Collection & Preparation
**Date:** 2026-07-26  
**Owner:** RAG Engineering + Barragens Domain Expert (Manta 03-S10)  
**Timeline:** 2026-07-27 to 2026-07-28 (2 days parallel)

---

## Task Breakdown

### Task 1: ICOLD Documentation Collection (6 hours)
**Owner:** RAG Researcher  
**Deadline:** 2026-07-27, 14:00 UTC

**Sources:**
- [ ] ICOLD Bulletins (1-40+): download from icold-cigb.org
  - Target: 30+ documents covering CFRD, CCR, earth dams
  - Focus: technical guidelines, case studies, design standards
  - Format: PDF → extract text
  
- [ ] ICOLD Case Studies Database
  - Target: 50+ dam projects (diverse geologies, heights, purposes)
  - Extract: project name, location, type (CFRD/CCR/earth), height, volume, foundation type
  - Format: CSV or JSON
  
- [ ] ICOLD Bibliography & Standards
  - Target: 10+ documents on seepage, spillway design, geotechnical testing
  - Format: PDF

**Deliverable:** `icold_corpus.zip` (50-100 MB, ~200 documents)

---

### Task 2: CBDB (Cadastro Brasileiro de Barragens) Extraction (4 hours)
**Owner:** Data Analyst  
**Deadline:** 2026-07-27, 18:00 UTC

**Sources:**
- [ ] ANA (Agência Nacional de Águas) CBDB portal
  - URL: cbdb.ana.gov.br or ana.gov.br/barragens
  - Data: registered Brazilian dams (2,000+ records)
  - Extract: name, location, state, type, height, volume, purpose, construction year
  
- [ ] Filter & Classify
  - Remove small dams (< 15m height)
  - Focus on: CFRD, CCR, earth dams, RCC
  - Target: 100+ diverse dams

**Deliverable:** `cbdb_dams.csv` (100+ rows, columns: nome, localização, tipo, altura, volume, fundação)

**SQL to extract:**
```sql
SELECT 
  nome_barragem, 
  estado, 
  tipo_barragem, 
  altura_m, 
  volume_m3, 
  finalidade,
  ano_construcao
FROM barragens_brasil
WHERE altura_m >= 15 
  AND tipo_barragem IN ('CFRD', 'CCR', 'TERRA', 'RCC')
ORDER BY altura_m DESC;
```

---

### Task 3: Lei 12.334 & Technical Standards (3 hours)
**Owner:** Legal/Domain Expert  
**Deadline:** 2026-07-27, 20:00 UTC

**Documents to Collect:**
- [ ] Lei 12.334/2010 (full text) — Brazilian Dam Safety Law
  - Focus sections: classificação (classification), requisitos técnicos (technical requirements), operação e manutenção (O&M)
  
- [ ] ABNT NBR 8944:2014 — Terra e enrocamento (earth and rockfill dams)
  - Sections: compactação (compaction), ensaios geotécnicos (geotechnical testing)
  
- [ ] ABNT NBR 9814:2014 — Barragens de concreto (concrete dams)
  - Sections: fundação (foundation), impermeabilização (waterproofing)
  
- [ ] ICOLD Technical Committees
  - Seepage Control (Committee 7)
  - Spillway Design (Committee 9)
  - Geotechnics (Committee 3)

**Deliverable:** `brazilian_standards.zip` (20-50 MB, ~50 documents)

---

### Task 4: Manta Proprietary Projects (2 hours)
**Owner:** Project Manager  
**Deadline:** 2026-07-27, 22:00 UTC

**Internal Sources:**
- [ ] Past dam feasibility studies (EVTE reports)
  - Filter: project confidentiality (sanitize company names, specific costs)
  - Extract: technical recommendations, geotechnical analysis, foundation design
  - Target: 5-10 reports
  
- [ ] Design & cost analysis documents
  - Focus: barragem-specific terminology, technical metrics
  - Format: PDF → extract relevant sections
  
- [ ] Regulatory submissions (ANA, DNPM)
  - Extract: technical justifications, design rationale
  - Target: 5+ documents

**Deliverable:** `manta_projects_sanitized.zip` (10-20 MB, ~20 documents)

**Security checklist:**
- [ ] Remove client names & confidential data
- [ ] Anonymize project locations (replace with "Project X")
- [ ] Remove cost breakdowns (keep only technical content)
- [ ] Get approval from project owners before inclusion

---

## Corpus Assembly (Task 5: 1 hour)

**Deadline:** 2026-07-28, 09:00 UTC

**Steps:**
1. Unzip all 4 deliverables into single corpus directory
2. Convert all PDFs to plaintext (using `pdfplumber` or similar)
3. Create manifest file: `corpus_manifest.json`
   ```json
   {
     "total_documents": 250,
     "sources": {
       "icold": 200,
       "cbdb": 50,
       "brazilian_standards": 50,
       "manta_projects": 20
     },
     "total_size_mb": 150,
     "languages": ["en", "pt"],
     "date_created": "2026-07-28T09:00:00Z"
   }
   ```
4. Generate word count report per source
5. Upload to shared storage (Google Drive, Manta SharePoint, or S3)

**Output:** `barragem_corpus_v1.zip` (150 MB, indexed)

---

## Quality Checklist

- [ ] All documents readable (no corrupted PDFs)
- [ ] No duplicate documents (deduplicate across sources)
- [ ] Minimum document size: 500 words (remove stubs)
- [ ] Language consistency (prioritize Portuguese + English)
- [ ] Metadata completeness (source, date, document type)
- [ ] No proprietary/confidential leakage (Manta projects sanitized)

---

## Dependencies & Timeline

```
2026-07-27 (Friday)
  06:00 — ICOLD collection starts (Task 1)
  12:00 — CBDB extraction starts (Task 2, parallel)
  14:00 — Lei + Standards collection starts (Task 3, parallel)
  18:00 — Manta projects sanitized (Task 4, parallel)
  
2026-07-28 (Saturday)
  09:00 — Corpus assembly & validation (Task 5)
  12:00 — Final corpus delivered (400-500 docs, 50K-100K tokens)
  
2026-07-28 (Saturday evening)
  18:00 — Training data creation begins (next phase)
```

---

## Success Criteria

✅ **Corpus Size:** 400-500 documents (minimum 50K tokens)  
✅ **Language:** Primarily Portuguese (pt-BR) with English supplement  
✅ **Diversity:** ICOLD + CBDB + Standards + Manta (4 distinct sources)  
✅ **Quality:** Zero duplicates, no corrupted PDFs, metadata complete  
✅ **Security:** Proprietary projects sanitized, no confidential leakage  
✅ **Accessibility:** Shared storage, indexed, searchable  

---

## Assigned Teams

| Task | Owner | Team | Contact |
|------|-------|------|---------|
| ICOLD Collection | RAG Researcher | Manta 03-S10 | — |
| CBDB Extraction | Data Analyst | Manta 03-S10 | — |
| Standards Collection | Legal/Domain Expert | Manta 03-S10 | — |
| Manta Projects | Project Manager | Manta 03-S10 | — |
| Corpus Assembly | RAG Engineering | Manta 03-S10 | — |

---

**Prepared by:** Agente RAG Benchmark  
**Status:** Ready for team assignment  
**Next Phase:** Training data creation (2026-07-28 onwards)
