# Runbook: Phase 2.4 RAG Ingestion Deployment

**Status**: 🟢 PRODUCTION READY  
**Owner**: DevOps + Data team  
**Audience**: Engineers executing deployment  
**Duration**: 2-3 hours (initial setup)

---

## Pre-Deployment Checklist

- [ ] Supabase project created + migration applied
- [ ] GitHub repository has write access to secrets
- [ ] RAG source PDFs organized in `/docs/rag-sources/`
- [ ] Anthropic API key validated
- [ ] Python 3.9+ available locally
- [ ] `supabase-cli` installed (`brew install supabase`)
- [ ] GitHub CLI (`gh`) installed and authenticated

---

## STEP 1: Configure GitHub Secrets (5 min)

### 1.1 Gather Secrets

Get these values ready:

```bash
# Anthropic API
ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.anthropic/config.txt 2>/dev/null || echo "sk-ant-xxx")

# Supabase
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="eyJhbGc..."  # From Supabase Settings → API

# Optional: Slack webhook for notifications
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx"
```

### 1.2 Add to GitHub Secrets

```bash
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"
gh secret set SUPABASE_URL --body "$SUPABASE_URL"
gh secret set SUPABASE_ANON_KEY --body "$SUPABASE_ANON_KEY"
gh secret set SLACK_WEBHOOK_URL --body "$SLACK_WEBHOOK_URL"  # optional

# Verify
gh secret list
```

**Expected output:**
```
ANTHROPIC_API_KEY    Updated 2026-07-25
SUPABASE_URL         Updated 2026-07-25
SUPABASE_ANON_KEY    Updated 2026-07-25
SLACK_WEBHOOK_URL    Updated 2026-07-25
```

---

## STEP 2: Prepare Supabase (10 min)

### 2.1 Apply Phase 1 Migrations (if not done)

```bash
# Check current migration status
supabase migration list

# Apply Phase 1 migrations (in order)
supabase db push supabase/migrations/2026_07_25_add_pgvector_to_rag.sql
supabase db push supabase/migrations/2026_07_25_add_maestro_monitoring.sql
supabase db push supabase/migrations/2026_07_26_add_feedback_tables.sql

# Verify tables exist
supabase db columns rag_chunks
supabase db columns maestro_rag_ingestion_log
```

### 2.2 Verify RAG Chunks Table

```sql
-- Login to Supabase dashboard → SQL Editor
SELECT 
  table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'rag%';

-- Should see:
-- rag_chunks
-- maestro_rag_ingestion_log

-- Check columns
\d rag_chunks
```

**Expected schema:**
```
id | collection_slug | content | source_file | page_num | embedding | metadata | created_at
```

---

## STEP 3: Organize RAG Source Files (15 min)

### 3.1 Create Directory Structure

```bash
mkdir -p docs/rag-sources/{saneamento,energia,portos,aeroportos,barragens}

# Add tier subdirectories
for segment in saneamento energia portos aeroportos barragens; do
  mkdir -p docs/rag-sources/$segment/{T1-normas,T2-projetos,T3-estudos,T4-templates}
done
```

### 3.2 Populate with PDFs

Download from SharePoint `02_Conhecimento/` and organize:

```
docs/rag-sources/
├── saneamento/
│   ├── T1-normas/          # SNIS, Lei 14.026, NBR 12211-12218
│   │   ├── SNIS-2023.pdf
│   │   ├── Lei_14026.pdf
│   │   └── NBR_12211.pdf
│   ├── T2-projetos/        # ETA/ETE designs
│   │   └── ETA_Brasilia_design.pdf
│   ├── T3-estudos/         # PMSB, feasibility
│   │   └── PMSB_Sao_Paulo.pdf
│   └── T4-templates/       # RFP templates
│       └── ETA_RFP_template.pdf
├── energia/
│   ├── T1-normas/          # ANEEL R1-R5, EPE
│   ├── T2-projetos/        # LT/subestação designs
│   ├── T3-estudos/         # PDE, EPE studies
│   └── T4-templates/       # Leilão editais
# ... portos, aeroportos, barragens
```

### 3.3 Verify Organization

```bash
# Count files
find docs/rag-sources -name "*.pdf" | wc -l

# Should see at least 1 file per segment/tier
find docs/rag-sources -type d | sort
```

---

## STEP 4: Test Locally (20 min)

### 4.1 Install Dependencies

```bash
pip install --upgrade pip
pip install pypdf anthropic supabase python-dotenv

# Verify
python -c "import anthropic; print(anthropic.__version__)"
```

### 4.2 Create Local .env File

```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY="your-api-key-here"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"
EOF

# Do NOT commit .env to git
echo ".env" >> .gitignore
```

### 4.3 Run Dry-Run Test

```bash
# Test with a small subset
python scripts/ingest_rag_batch.py \
  --segment saneamento \
  --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --dry-run \
  --max-chunks 5

# Expected output:
# ✅ DRY RUN: Would ingest 5 chunks
# Segment: saneamento | Tier: T1
# Total tokens (estimated): ~2500
# Embedding model: text-embedding-3-large
# Target collection: san:br:
```

### 4.4 Test Actual Ingestion (small)

```bash
# Remove --dry-run to actually ingest
python scripts/ingest_rag_batch.py \
  --segment saneamento \
  --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --max-chunks 3  # Start small

# Wait 30 seconds for Supabase to confirm

# Verify in Supabase
supabase table select rag_chunks \
  --where 'collection_slug' eq 'san:br:' \
  --limit 5
```

**Expected output:**
```
id | collection_slug | content                        | tokens | created_at
1  | san:br:        | "Art. 1º - Este decreto..."   | 245    | 2026-07-25...
2  | san:br:        | "§ 1º - Aplicam-se as..."    | 198    | 2026-07-25...
3  | san:br:        | "§ 2º - As regras de..."     | 267    | 2026-07-25...
```

---

## STEP 5: Deploy CI/CD Workflow (10 min)

### 5.1 Verify Workflow File Exists

```bash
# Check workflow is in repo
cat .github/workflows/ingest-rag-monthly.yml | head -30

# Should show:
# name: RAG Ingestion (Monthly)
# on:
#   schedule:
#     - cron: '0 2 1 * *'  # 1st of month at 2 AM UTC
#   workflow_dispatch:
```

### 5.2 Enable Workflow

```bash
# List available workflows
gh workflow list

# Expected: ingest-rag-monthly.yml should be listed

# If disabled, enable it
gh workflow enable ingest-rag-monthly.yml
```

### 5.3 Test Manual Trigger

```bash
# Trigger workflow manually
gh workflow run ingest-rag-monthly.yml \
  -f segment=saneamento \
  -f tier=T1

# Expected output:
# ✓ Created workflow_dispatch event

# Watch execution
gh run list --workflow=ingest-rag-monthly.yml --limit=1
gh run view <run-id> --log  # Stream logs

# Wait for completion (2-5 minutes)
```

---

## STEP 6: Monitor First Run (30 min)

### 6.1 Check Workflow Progress

```bash
# List recent runs
gh run list --workflow=ingest-rag-monthly.yml --limit=5

# View detailed logs
gh run view <run-id> --log | tail -50

# Expected final status:
# ✅ All jobs succeeded
```

### 6.2 Verify Ingestion in Supabase

```bash
# Count new chunks
supabase db query << 'SQL'
SELECT 
  collection_slug,
  COUNT(*) as chunk_count,
  MAX(created_at) as latest
FROM rag_chunks
WHERE created_at > now() - interval '1 hour'
GROUP BY collection_slug;
SQL

# Expected:
# collection_slug | chunk_count | latest
# san:br:        | 245         | 2026-07-25 10:15:32
```

### 6.3 Check Ingestion Log

```bash
# View ingestion events
supabase db query << 'SQL'
SELECT 
  segment,
  tier,
  status,
  chunks_ingested,
  error_message,
  completed_at
FROM maestro_rag_ingestion_log
ORDER BY completed_at DESC
LIMIT 5;
SQL
```

### 6.4 Optional: Slack Notification

If SLACK_WEBHOOK_URL is set, check Slack for notification:

```
🤖 RAG Ingestion Complete
├─ Segment: saneamento
├─ Tier: T1
├─ Chunks: 245
├─ Tokens: ~125,000
├─ Duration: 2m 34s
└─ Status: ✅ Success
```

---

## STEP 7: Full Rollout (30 min)

### 7.1 Ingest All Segments (Sequential)

```bash
# Run for all 5 segments + 4 tiers
for segment in saneamento energia portos aeroportos barragens; do
  for tier in T1 T2 T3 T4; do
    echo "Starting: $segment / $tier"
    
    python scripts/ingest_rag_batch.py \
      --segment "$segment" \
      --tier "$tier" \
      --batch-size 10 \
      --max-chunks 100  # Limit to 100 per tier initially
    
    # Wait between segments to avoid rate limiting
    sleep 30
  done
done

# Monitor progress:
# Total expected: 5 segments × 4 tiers × 100 chunks = 2000 chunks
# Estimated time: ~30 minutes
```

### 7.2 Verify Complete Ingestion

```bash
# Query final counts by segment
supabase db query << 'SQL'
SELECT 
  collection_slug,
  COUNT(*) as total_chunks,
  COUNT(DISTINCT source_file) as unique_files,
  MIN(created_at) as first_ingested,
  MAX(created_at) as last_ingested
FROM rag_chunks
WHERE created_at > now() - interval '1 day'
GROUP BY collection_slug
ORDER BY collection_slug;
SQL

# Expected results:
# collection_slug | total_chunks | unique_files | first_ingested | last_ingested
# aer:br:        | 280          | 12           | 2026-07-25...  | 2026-07-25...
# bar:br:        | 245          | 8            | 2026-07-25...  | 2026-07-25...
# ene:br:        | 310          | 15           | 2026-07-25...  | 2026-07-25...
# por:br:        | 225          | 10           | 2026-07-25...  | 2026-07-25...
# san:br:        | 240          | 11           | 2026-07-25...  | 2026-07-25...
```

---

## STEP 8: Schedule Monthly Job (5 min)

### 8.1 Verify Monthly Schedule

The workflow is already scheduled at:
- **Time**: 1st of each month at 02:00 UTC
- **Cron**: `0 2 1 * *`

### 8.2 Test Scheduling Logic

```bash
# Check next scheduled run
gh workflow list --all | grep ingest-rag-monthly

# Should show next run date/time
```

### 8.3 Manual Override (if needed)

```bash
# To immediately run instead of waiting for 1st of month:
gh workflow run ingest-rag-monthly.yml \
  -f segment=saneamento \
  -f tier=T1 \
  -f force_reprocess=true
```

---

## STEP 9: Validation & Testing (15 min)

### 9.1 Vector Search Test

```bash
# Test semantic search on ingested chunks
cat > test_rag_search.py << 'EOF'
from anthropic import Anthropic
from supabase import create_client

client = Anthropic()
db = create_client("$SUPABASE_URL", "$SUPABASE_ANON_KEY")

# Generate embedding for test query
query = "Como dimensionar uma ETA para 100 mil habitantes?"
response = client.embeddings.create(
    model="text-embedding-3-large",
    input=query
)
query_embedding = response.data[0].embedding

# Search in Supabase (pgvector similarity)
result = db.rpc(
    'search_rag_chunks',
    {
        'query_embedding': query_embedding,
        'similarity_threshold': 0.7,
        'collection_slug': 'san:br:',
        'limit': 3
    }
).execute()

print(f"Found {len(result.data)} relevant chunks:")
for chunk in result.data:
    print(f"\n- Score: {chunk['similarity']:.2f}")
    print(f"  File: {chunk['source_file']}")
    print(f"  Excerpt: {chunk['content'][:100]}...")
EOF

python test_rag_search.py
```

### 9.2 Quality Metrics

```bash
# Gather quality metrics
supabase db query << 'SQL'
SELECT 
  COUNT(*) as total_chunks,
  COUNT(DISTINCT collection_slug) as segments,
  AVG(CHAR_LENGTH(content)) as avg_chunk_size,
  MIN(CHAR_LENGTH(content)) as min_chunk_size,
  MAX(CHAR_LENGTH(content)) as max_chunk_size
FROM rag_chunks
WHERE created_at > now() - interval '24 hours';
SQL

# Expected:
# total_chunks | segments | avg_chunk_size | min_chunk_size | max_chunk_size
# 1300         | 5        | 1850           | 245            | 4982
```

---

## STEP 10: Documentation & Handoff (10 min)

### 10.1 Create Team Runbook

```bash
# Update team documentation
cat > docs/RAG-INGESTION-RUNBOOK.md << 'EOF'
# RAG Ingestion Runbook (Team Copy)

## Monthly Ingestion Schedule
- **When**: 1st of each month at 2 AM UTC
- **Status**: Automatic (GitHub Actions)
- **Owner**: DevOps

## Manual Trigger
\`\`\`bash
gh workflow run ingest-rag-monthly.yml -f segment=saneamento
\`\`\`

## Monitoring
- Logs: GitHub Actions → ingest-rag-monthly.yml
- Metrics: Supabase → maestro_rag_ingestion_log table
- Slack: #maestro-alerts (if configured)

## Troubleshooting
See DEPLOYMENT-PHASE-2.md → Rollback section
EOF

git add docs/RAG-INGESTION-RUNBOOK.md
```

### 10.2 Notify Team

```bash
# Slack notification (if integrated)
echo "✅ RAG Ingestion (Phase 2.4) deployed successfully!
- 1,300+ chunks across 5 segments
- Monthly job scheduled (1st of month @ 2 AM UTC)
- Manual trigger available via: gh workflow run ingest-rag-monthly.yml
- Monitoring: https://supabase.co/project/[project]/editor" | \
  curl -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d @- << 'EOF'
{"text":"RAG Ingestion Phase 2.4 Deployed"}
EOF
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Verify secret is set
gh secret list | grep ANTHROPIC

# Re-add if missing
gh secret set ANTHROPIC_API_KEY --body "sk-ant-xxx"
```

### Issue: "Connection to Supabase failed"
```bash
# Test connection
python << 'EOF'
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

try:
    db = create_client(url, key)
    result = db.table("rag_chunks").select("COUNT(*)").execute()
    print(f"✅ Connected. Table has {len(result.data)} rows")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

### Issue: "Rate limit exceeded"
```bash
# Add exponential backoff between segments
# Already built into script with --batch-size parameter
# Default: 10 concurrent chunks per batch
# Increase if needed: --batch-size 20
```

### Issue: Workflow never triggers
```bash
# Check if workflow is enabled
gh workflow list | grep ingest-rag-monthly

# If disabled, enable it
gh workflow enable ingest-rag-monthly.yml

# Manually test
gh workflow run ingest-rag-monthly.yml --ref main
```

---

## Rollback Procedure

If something goes wrong during ingestion:

```bash
# 1. Stop the workflow (if still running)
gh run cancel <run-id>

# 2. Delete problematic chunks
supabase db query << 'SQL'
DELETE FROM rag_chunks
WHERE collection_slug = 'san:br:' AND created_at > '2026-07-25';
SQL

# 3. Fix the issue in scripts/ingest_rag_batch.py

# 4. Re-run with --dry-run
python scripts/ingest_rag_batch.py --segment saneamento --dry-run

# 5. Once verified, re-run without --dry-run
python scripts/ingest_rag_batch.py --segment saneamento
```

---

## Success Criteria

✅ **Deployment is successful when:**
- [ ] All GitHub secrets configured and verified
- [ ] Supabase migrations applied
- [ ] Local dry-run test passes
- [ ] 1,300+ chunks ingested across 5 segments
- [ ] Monthly CI/CD job scheduled and tested
- [ ] Team notified and runbook updated
- [ ] Monitoring dashboard showing ingestion metrics

**Estimated Total Time**: 2-3 hours (including PDF downloads)

---

**Status**: 🟢 READY TO EXECUTE  
**Last Updated**: 2026-07-25  
**Owner**: DevOps Team
