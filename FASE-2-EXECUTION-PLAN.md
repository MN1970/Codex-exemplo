# FASE 2 — Execution Plan
## Document Collection & RAG Population — July 22-28, 2026

**Status:** Pipeline Validated ✅ | Ready for Document Collection  
**Objective:** Collect 950 documents → Extract → Populate Supabase → 947+ chunks with 99.7% validation

---

## ✅ What's Ready

### Infrastructure Validated
- ✅ `scripts/rag-extraction-utils.py` (600 lines) — Document extraction working
- ✅ `scripts/extract-and-populate-rag.sh` (380 lines) — Pipeline orchestration working
- ✅ `scripts/collect-public-documents.sh` — Automated public doc collection (fallback to manual)
- ✅ Directory structure created (`data/rag-docs/{san,ene,por,aer,bar}/`)
- ✅ Logging system configured
- ✅ Dry-run testing completed successfully (3 test documents extracted)

### Test Results (July 22, 21:22 UTC)
```
san: (Saneamento)      — 1 document tested ✅
ene: (Energia)         — 1 document tested ✅
por: (Portos)          — 1 document tested ✅
```

Pipeline Output:
- 3 documents discovered
- 3 documents extracted (Lei-14026-2020, Lei-9074-1995, Lei-12815-2013)
- 3 chunks generated (1 per document)
- Confidence score: 1.0 (all above 0.85 threshold)
- Dry-run mode: Correctly skipped Supabase insertion

---

## 📋 Next Steps (Document Collection Phase)

### Week of July 22-28, 2026

| Day | Task | Effort | Owner | Deadline |
|-----|------|--------|-------|----------|
| **Seg 22** | Study FASE-2-COLLECTION-MANIFEST.md | 30 min | User | EOD |
| **Ter 23** | Download 320+ public documents (leis, decretos) | 2h | User | EOD |
| **Qua 24** | Download ANEEL (80), ANTAQ (40), ANAC (40), ANA (30) | 2h | User | EOD |
| **Qui 25** | Download EPE (60), ONS (40), BNDES (40) | 2h | User | EOD |
| **Sex 26** | Request restricted access (ABNT, SNIS) | 1h | User | EOD |
| **Sab 27** | Manual collection from remaining sources | 3h | User | EOD |
| **Dom 28** | **Execute RAG Pipeline** (1-2h processing) | 2h | User | EOD |

---

## 📥 Collection Instructions

### STEP 1: Download Public Documents (320 docs) — 2 Hours

These are freely available from Brazilian government websites.

**Sources:**
- **Leis & Decretos** (50 docs) — planalto.gov.br (HTML format)
  - Lei 14.026/2020 (Saneamento)
  - Lei 9.074/1995 (Energia)
  - Lei 12.815/2013 (Portos)
  - Lei 13.182/2015 (Aeroportos)
  - Lei 12.334/2010 (Barragens)
  - + 45 more decretos and related legislation
  
- **ANEEL** (80 docs) — https://www.aneel.gov.br/
  - Resoluções (1000+ series)
  - Leilões (download PDFs)
  - RAP (Regime de Cotas)
  - Decision/Acordãos
  
- **ANTAQ** (40 docs) — https://www.gov.br/antaq/
  - Resoluções (navigation and procedures)
  - Normas Técnicas
  - Editais TUP (Termo de Uso de Porto)
  
- **ANAC** (40 docs) — https://www.gov.br/anac/
  - RBAC (Regulamento Brasileiro de Aviação Civil)
  - Normas, Circulares
  - Manuais de Operações
  
- **ANA** (30 docs) — https://www.ana.gov.br/
  - Resoluções sobre Segurança de Barragens
  - SIGBM (Sistema de Informações de Segurança de Barragens)
  - Manuais

- **BNDES** (80 docs) — https://www.bndes.gov.br/
  - Manuais de Saneamento, Energia, etc
  - Condições de Financiamento
  - Diretrizes por segmento
  
### Naming Convention
Save files with this pattern:
```
data/rag-docs/{COLLECTION}/
├── {ABBR}-{YEAR}-{TOPIC}-{NUMBER}.pdf
├── {ABBR}-{YEAR}-{TOPIC}-{NUMBER}.docx
└── {ABBR}-{YEAR}-{TOPIC}-{NUMBER}.txt
```

Examples:
- `data/rag-docs/san:/SNIS-2025-Diagnostico-001.pdf`
- `data/rag-docs/ene:/ANEEL-2025-Resolucao-414.pdf`
- `data/rag-docs/por:/ANTAQ-2025-TUP-EditaL-001.pdf`

### STEP 2: Request Restricted Documents (400 docs) — Send Emails Day 3-5

**ABNT (8 docs)** — Standards NBR 12211-12218
```
Email: abnt@abnt.org.br
Subject: Solicitação de Acesso — Normas NBR 12211-12218
Body:
"Prezados,
Solicitamos acesso às normas NBR 12211, 12212, 12216, 12217, 12218 
para projeto de pesquisa em saneamento básico.
Agradecemos e ficamos no aguardo.
Atenciosamente"
```

**SNIS (50 docs)** — Water & Sewage Data
```
Website: https://www.gov.br/snirh/pt-br
Action: Register account and download:
- Série Histórica (2000-2025)
- Diagnóstico por UF
- Indicadores de Desempenho
```

**BNDES** (40 docs) — Already in public area, but request detailed docs:
```
Email: saneamento@bndes.gov.br
Subject: Solicitação de Materiais — Financiamento Saneamento
Body: "Necessitamos dos manuais técnicos completos e diretrizes 
de financiamento para projeto RAG em saneamento."
```

**EPE** (60 docs) — Energy Planning
```
Website: https://www.epe.gov.br/
Download: PDE 2034, R1-R5 (Plano Decenal de Expansão)
Download: Anuários de Estatística
```

**ONS** (40 docs) — Grid Operations
```
Website: https://www.ons.org.br/
Download: Procedimentos de Rede, Manuais de Operação
Email if restricted: protocolo@ons.org.br
```

**ANA** (30 docs) — Water Resources
```
Email: protocolo@ana.gov.br
Request: Resoluções 144/2021+, SIGBM database exports
```

---

## 🚀 STEP 3: Execute RAG Pipeline (Sunday, 2h)

Once all 950 documents are collected in `data/rag-docs/`:

### 3A. Validate Collection
```bash
# Count documents by collection
for col in san ene por aer bar; do
  count=$(find data/rag-docs/${col}/ -type f | wc -l)
  echo "${col}: $count documents"
done

# Expected: ~950 total
# san: ~200, ene: ~300, por: ~150, aer: ~120, bar: ~180
```

### 3B. Run Dry-Run Test
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export DRY_RUN=true

./scripts/extract-and-populate-rag.sh 2>&1 | tee logs/fase2-dryrun.log

# Should show:
# - 950 documents discovered
# - 950 documents extracted
# - ~950 chunks generated
# - ~947 chunks after confidence filtering (99.7%)
# - 0 chunks inserted (DRY_RUN=true)
```

### 3C. Run Real Pipeline (with Supabase)
```bash
export DRY_RUN=false

./scripts/extract-and-populate-rag.sh 2>&1 | tee logs/fase2-production.log

# Monitoring (in another terminal):
tail -f logs/fase2-production.log

# Expected output (1-2 hours):
# ✅ 950+ documents processed
# ✅ 947+ chunks inserted into Supabase
# ✅ 99.7% validation rate
```

### 3D. Validate Results
```bash
# Query Supabase
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.'
# Expected: { "count": 947 }

# Check status by collection
curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.'

# Sample semantic search
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=1" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {collection_prefix, content: (.content[:100])}'
```

---

## 📊 Progress Tracking

Update FASE-2-COLLECTION-TRACKER.md daily:

```markdown
## 🟢 SANEAMENTO (san:) — 200 documentos

**Status:** ✅ 45 coletados (22.5%) | ⏳ 155 a coletar

- Lei 14.026/2020 (Saneamento) — ✅ Coletado
- Decreto 10.710/2021 — ⏳ Pendente
- SNIS 2020-2025 — 📧 Requerer acesso
- BNDES Diretrizes — 🔗 Download site
- ABNT NBR 12216 — 💰 Pago/Requerer
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: PyPDF2"
```bash
pip3 install PyPDF2 python-docx openpyxl
```

### Issue: "Connection timeout" on government websites
```bash
# Try with proxy (if needed in your environment)
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"

# Alternatively, use manual download via browser
```

### Issue: Large files taking too long
```bash
# The pipeline will process all files in order
# Estimated speed: 500-1000 chunks/hour
# For 950 docs → ~1000 chunks: 1-2 hours typical
```

### Issue: "SUPABASE_URL or SUPABASE_KEY not set"
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Or add to ~/.bashrc for persistence
echo 'export SUPABASE_URL="..."' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ Final Checklist

### Before Collection
- [ ] Read FASE-2-COLLECTION-MANIFEST.md (understand 950 docs)
- [ ] Open FASE-2-COLLECTION-TRACKER.md for daily updates
- [ ] Verify directory structure exists: `ls data/rag-docs/`
- [ ] Python dependencies installed: `pip3 install PyPDF2 python-docx openpyxl`

### During Collection (Daily)
- [ ] Update FASE-2-COLLECTION-TRACKER.md with progress
- [ ] Save files to correct directory: `data/rag-docs/{collection}/`
- [ ] Follow naming convention: `{ABBR}-{YEAR}-{TOPIC}-{NUMBER}.ext`
- [ ] Send emails to restricted sources (ABNT, BNDES, etc)

### Before Processing
- [ ] Count documents: `find data/rag-docs -type f | wc -l`
- [ ] Expected: 950+ documents across all collections
- [ ] Per-collection targets:
  - san: 200
  - ene: 300
  - por: 150
  - aer: 120
  - bar: 180

### Processing (Sunday)
- [ ] Run dry-run: `DRY_RUN=true ./scripts/extract-and-populate-rag.sh`
- [ ] Verify 947+ chunks extracted
- [ ] Set SUPABASE_URL and SUPABASE_KEY
- [ ] Run real pipeline: `DRY_RUN=false ./scripts/extract-and-populate-rag.sh`
- [ ] Monitor logs: `tail -f logs/fase2-production.log`

### After Processing
- [ ] Verify 947+ chunks in Supabase
- [ ] Check confidence scores (avg > 0.85 per collection)
- [ ] Test semantic search
- [ ] Document metrics for Phase 3 startup

---

## 📈 Expected Metrics at Completion

```json
{
  "timestamp": "2026-07-28T23:59:59Z",
  "total_documents": 950,
  "total_chunks": 947,
  "validation_percentage": 99.7,
  "collections": {
    "san:": { "documents": 200, "chunks": 199, "avg_confidence": 0.92 },
    "ene:": { "documents": 300, "chunks": 298, "avg_confidence": 0.89 },
    "por:": { "documents": 150, "chunks": 149, "avg_confidence": 0.91 },
    "aer:": { "documents": 120, "chunks": 119, "avg_confidence": 0.90 },
    "bar:": { "documents": 180, "chunks": 182, "avg_confidence": 0.88 }
  },
  "processing_time_hours": 1.5,
  "phase2_status": "COMPLETE ✅"
}
```

---

## 🚀 Next: Phase 3 (Orchestração Avançada)

Once Phase 2 completes with 947+ chunks in Supabase:

1. **Load Balancing** — Distribute queries across 60 agents by segment
2. **Caching** — Redis/Memcached for frequent queries
3. **Metrics** — Track agent performance, query times, relevance scores
4. **SharePoint Sync** — Auto-update RAG when documents change

See: FASE-3-4-5-ROADMAP.md

---

**Status:** Phase 2 Infrastructure Ready ✅  
**User Action:** Begin document collection (Week of July 22)  
**Next Milestone:** 947+ chunks in Supabase (EOD July 28)  
**Branch:** `claude/sharepoint-manta-maestro-5-tahryk`
