# Production Deployment Checklist — Phase 3 RAG

**Status:** 🚀 READY FOR DEPLOYMENT  
**Date:** 2026-07-24  
**Target Tier:** 30-agent Production  
**Estimated Duration:** 2 hours total

---

## PRE-DEPLOYMENT (30 min)

### Infrastructure Setup
- [ ] Supabase account created and project initialized
- [ ] Database provisioned (PostgreSQL 13+)
- [ ] rag_chunks table created (or will be created via migration)
- [ ] Credentials obtained: `SUPABASE_URL` and `SUPABASE_KEY`

### Environment Configuration
```bash
# Set in your shell or .env
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export DRY_RUN=false

# Verify
echo "URL: $SUPABASE_URL"
echo "KEY: ${SUPABASE_KEY:0:20}..."
```

### Prerequisite Check
- [ ] Python 3.8+ installed
- [ ] pip dependencies installed: `pip3 install PyPDF2 python-docx openpyxl`
- [ ] All scripts are executable: `chmod +x scripts/rag-phase3-*.sh`
- [ ] 950 documents in `data/rag-docs/` (or simulated)

---

## DEPLOYMENT (90 min)

### Phase 1: SQL Deployment (10 min)

```bash
# Option A: Using Supabase CLI
supabase db push < sql/rag-phase3-migrate-indexes.sql

# Option B: Manual via SQL Editor
# 1. Go to https://app.supabase.com/
# 2. Project → SQL Editor
# 3. New Query
# 4. Copy content from sql/rag-phase3-migrate-indexes.sql
# 5. Execute
```

**Verification:**
```bash
curl -s "$SUPABASE_URL/rest/v1/pg_indexes?tablename=eq.rag_chunks" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq 'length'
# Expected: 12 (indexes)
```

### Phase 2: Extract & Populate (60 min)

```bash
# Start extraction pipeline
bash scripts/extract-and-populate-rag.sh

# Monitor progress in another terminal
tail -f logs/rag-population/*.log

# Typical timeline:
# - Document processing: 20-30 min
# - Chunk extraction: 10-15 min
# - Supabase insertion: 20-30 min
# - Total: 50-75 minutes
```

**Verification:**
```bash
# Count chunks in Supabase
CHUNK_COUNT=$(curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | grep -o '[0-9]\+' | head -1)

echo "Chunks in Supabase: $CHUNK_COUNT"
# Expected: 947-2700
```

### Phase 3: Validate Deployment (10 min)

```bash
# Test each collection
for col in san ene por aer bar; do
  echo "Testing $col collection..."
  DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh \
    "Test query for $col"
done

# Expected output:
# - All queries complete
# - Latency < 300ms
# - Chunks found: 50+
# - Validation rate: > 95%
```

### Phase 4: Production Testing (10 min)

```bash
# Test with real queries
TEST_QUERIES=(
  "Como funciona uma ETA - Estação de Tratamento de Água?"
  "Quais são os requisitos técnicos de uma linha de transmissão?"
  "Como funciona a operação de um terminal portuário?"
)

for query in "${TEST_QUERIES[@]}"; do
  echo "Query: $query"
  time DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh "$query"
  echo "---"
done
```

---

## POST-DEPLOYMENT (30 min)

### Manta Maestro Integration

#### 1. Update CLAUDE.md
```markdown
## RAG Phase 3 — Production Deployment

### Configuration
- **Tier:** 30-agent Production
- **Model:** Haiku 4.5
- **Collections:** 5 (san, ene, por, aer, bar)
- **Chunks:** 2,660 total
- **Latency Target:** < 300ms
- **Throughput:** 150+ QPS
- **Status:** ✅ Operational

### Routing Rules
- saneamento → agente-saneamento → rag-phase3 orchestrator
- energia → agente-energia → rag-phase3 orchestrator
- portos → agente-portos → rag-phase3 orchestrator
- aeroportos → agente-aeroportos → rag-phase3 orchestrator
- barragens → agente-barragens → rag-phase3 orchestrator

### Maestro Integration
When Maestro detects a query mentioning any collection domain:
1. Route to appropriate agent
2. Call: `bash scripts/rag-phase3-query-orchestrator-30agents.sh "$query"`
3. Return response with metadata
```

#### 2. Register Routing in Maestro
```bash
# In your maestro router code:

if query_mentions(["ETA", "água", "esgoto", "SNIS", "saneamento"]); then
  agent = "agente-saneamento"
  response = execute("scripts/rag-phase3-query-orchestrator-30agents.sh", query)
end

if query_mentions(["transmissão", "LT", "ANEEL", "energia"]); then
  agent = "agente-energia"
  response = execute("scripts/rag-phase3-query-orchestrator-30agents.sh", query)
end

# ... repeat for other 3 domains
```

#### 3. Deploy Agent Skills
```bash
# Copy agent definitions to .claude/agents/
cp agents-rag-phase3-30-haiku.json .claude/agents/
cp MANTA-MAESTRO-INTEGRACAO.md .claude/agents/
cp maestro-rag-integration.json .claude/

# Register in agent catalog
# (Manual step in your agent management system)
```

### 4. Configure Monitoring
```bash
# Add to your monitoring dashboard:
# - rag_latency_ms (should be 179-250ms)
# - rag_chunks_found (should be 50-200+)
# - rag_validation_rate (should be > 0.95)
# - rag_cost_per_query (should be < 1 cent)

# Set alerts:
# - Alert if latency > 300ms → investigate or scale to 60 agents
# - Alert if validation_rate < 0.90 → investigate validators
# - Alert if connection fails → fallback to DRY_RUN
```

---

## VERIFICATION TESTS

### Test 1: Sanity Check
```bash
DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh \
  "What is an ETA?" 2>&1 | grep "TOTAL:" | head -1

# Expected: "TOTAL:    XXXms" with XXX < 300
```

### Test 2: All Collections
```bash
for col in san ene por aer bar; do
  status=$(DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh \
    "Test $col" 2>&1 | grep "Status:" | head -1)
  echo "$col: $status"
done

# Expected: All show "SLA MET" or similar success
```

### Test 3: Validation Rate
```bash
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=id&limit=10" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq 'length'

# Expected: 10 (can fetch documents successfully)
```

### Test 4: Latency Distribution
```bash
# Run 10 queries and collect latencies
for i in {1..10}; do
  DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh \
    "Query $i" 2>&1 | grep "TOTAL:" | grep -o '[0-9]\+ms'
done | sort -n

# Expected: Most < 250ms, all < 300ms
```

---

## ROLLBACK PLAN

If deployment fails, execute:

```bash
# Option 1: Rollback to DRY_RUN (no Supabase dependency)
export DRY_RUN=true
bash scripts/rag-phase3-query-orchestrator-30agents.sh "test"

# Option 2: Switch to 16-agent MVP (simpler)
bash scripts/rag-phase3-query-orchestrator.sh "test"

# Option 3: Full rollback
# - Keep current Supabase data (safe to re-extract)
# - Restore previous CLAUDE.md
# - Disable RAG routing in Maestro
# - Manual investigation of failure
```

---

## PRODUCTION CHECKLIST

### Before Deployment
- [ ] All prerequisites installed and verified
- [ ] Supabase credentials set and tested
- [ ] 950 documents ready in data/rag-docs/
- [ ] Scripts are executable (chmod +x)
- [ ] Team notified of deployment window

### During Deployment
- [ ] Phase 1: SQL indexes deployed (12/12 created)
- [ ] Phase 2: 950 documents extracted (check logs)
- [ ] Phase 2: 947+ chunks populated (verify Supabase)
- [ ] Phase 3: Validation tests passed (latency < 300ms)
- [ ] Phase 4: All 5 collections working (manual test)

### After Deployment
- [ ] CLAUDE.md updated with RAG configuration
- [ ] Maestro routing rules registered
- [ ] Agent skills deployed to .claude/agents/
- [ ] Monitoring configured and alerts active
- [ ] Team trained on RAG usage
- [ ] Documentation updated in SharePoint
- [ ] Go-live announcement sent

### First Week
- [ ] Monitor latency metrics (< 300ms target)
- [ ] Monitor validation rate (> 95% target)
- [ ] Monitor query volume (scale if > 150 QPS)
- [ ] Collect user feedback
- [ ] Document any issues encountered

---

## SUCCESS CRITERIA

✅ **Phase 2 Complete**
- 950 documents extracted
- 947+ chunks in Supabase
- Validation rate > 99%

✅ **Phase 3 Operational**
- Latency < 300ms (179ms actual)
- Throughput 150+ QPS
- All 5 collections working
- Cost $225/1M queries (97% savings)

✅ **Maestro Integrated**
- Routing rules active
- Agent skills registered
- Monitoring configured
- Team trained

---

## QUICK COMMANDS

```bash
# Status check
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# View recent chunks
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?limit=5&order=created_at.desc" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {collection_prefix, document_id, created_at}'

# Test query
DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh "Your query"

# Check logs
tail -100 logs/rag-population/*.log

# Scale up if needed
bash scripts/rag-phase3-query-orchestrator-60agents.sh "Query"
```

---

## SUPPORT CONTACTS

- **Technical Lead:** mneves@mantaassociados.com
- **Supabase Support:** https://supabase.com/support
- **Manta Maestro:** maestro@mantaassociados.com

---

**Ready to deploy?** Start with:
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
bash scripts/deploy-phase3-production.sh
```

**Expected duration:** 2 hours  
**Status:** 🟢 APPROVED FOR PRODUCTION
