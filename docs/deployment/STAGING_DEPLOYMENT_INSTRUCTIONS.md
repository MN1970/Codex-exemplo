# Staging Deployment Instructions
**Date:** 2026-07-26  
**Environment:** Supabase Staging  
**Status:** Ready for execution

---

## Quick Start (5 minutes)

```bash
# 1. Get your Supabase staging credentials
# From: https://app.supabase.com → Select project → Settings → Database

# 2. Make script executable
chmod +x scripts/deploy_staging.sh

# 3. Run deployment
./scripts/deploy_staging.sh <SUPABASE_HOST> <ADMIN_PASSWORD>

# Example:
./scripts/deploy_staging.sh db.abcdef123456.supabase.co "your_admin_password"
```

---

## What This Does

### WS1: SQL Migration Deployment
```bash
✅ [1/6] Verify PostgreSQL client installed
✅ [2/6] Test Supabase connection
✅ [3/6] Create pre-deployment backup
✅ [4/6] Execute SQL migration (58 chunks)
✅ [5/6] Validate 58 chunks inserted
✅ [6/6] Generate deployment report
```

### Expected Output
```
WS1 + WS4 Staging Deployment — Phase 3 RAG Optimization
╔════════════════════════════════════════════════════════════════╗
║  ✅ STAGING DEPLOYMENT COMPLETE                               ║
╚════════════════════════════════════════════════════════════════╝

Deployment Summary:
  • Chunks inserted: 58/58 ✅
  • Minimum words: 170 (≥150) ✅
  • Deployment time: ~2-3s ✅
  • Backup: backups/staging_YYYYMMDD_HHMMSS.sql ✅

Next: Run 39-query benchmark to validate Phase 3 results
```

---

## Prerequisites

### Required
- [ ] PostgreSQL client (`psql`) installed
  ```bash
  # macOS
  brew install postgresql@15
  
  # Ubuntu/Debian
  sudo apt-get install postgresql-client
  
  # Windows
  # Download from: https://www.postgresql.org/download/windows/
  ```

- [ ] Supabase project created with staging database
- [ ] Admin password available (from Supabase Settings → Database)

### Optional (Recommended)
- [ ] Backup existing data (script does this automatically)
- [ ] Test connection to Supabase first:
  ```bash
  psql -h db.XXXX.supabase.co -U postgres -d postgres
  # Password: <your_admin_password>
  # \q to exit
  ```

---

## Detailed Execution Steps

### Step 1: Gather Supabase Credentials

1. Go to: https://app.supabase.com
2. Select your project
3. Click "Settings" → "Database"
4. Copy:
   - **Host:** `db.XXXX.supabase.co` (Connection string section)
   - **Password:** Your admin password (you set this during project creation)
   - **Port:** Usually `5432` (default)

### Step 2: Prepare Script

```bash
# Navigate to repo root
cd /path/to/Codex-exemplo

# Make script executable
chmod +x scripts/deploy_staging.sh

# Verify SQL migration file exists
ls -la supabase/migrations/2026_07_26_rag_phase3_corrected.sql
# Should show: 534 lines
```

### Step 3: Execute Deployment

```bash
# Run with your Supabase credentials
./scripts/deploy_staging.sh db.XXXX.supabase.co "YourAdminPassword"

# If password contains special characters, quote it:
./scripts/deploy_staging.sh db.XXXX.supabase.co "P@ssw0rd!#123"
```

### Step 4: Monitor Execution

Script output will show progress:
```
[1/6] Verifying Prerequisites... ✅
[2/6] Testing Supabase Connection... ✅
[3/6] Creating Pre-Deployment Backup... ✅
[4/6] Deploying SQL Migration (58 chunks)... ✅
[5/6] Validating Chunk Insertion... ✅
[6/6] Generating Deployment Report... ✅
```

### Step 5: Verify Deployment

Check the deployment log:
```bash
cat docs/deployment/STAGING_DEPLOYMENT_LOG.txt
```

Expected output:
```
Status: ✅ SUCCESSFUL
Chunks inserted: 58/58 ✅
Minimum word count: 170 (target: ≥150) ✅
```

---

## Validation After Deployment

### Manual Verification (Optional)

Connect to staging database and run:

```bash
# Connect to Supabase staging
psql -h db.XXXX.supabase.co -U postgres -d postgres -p 5432

# Count inserted chunks
SELECT COUNT(*) FROM rag_chunks 
WHERE source_type = 'synthetic_disambiguator';
# Expected: 58

# Check word count stats
SELECT 
  MIN(CAST(metadata->>'word_count' AS INTEGER)) as min_words,
  MAX(CAST(metadata->>'word_count' AS INTEGER)) as max_words,
  AVG(CAST(metadata->>'word_count' AS INTEGER)) as avg_words
FROM rag_chunks 
WHERE source_type = 'synthetic_disambiguator';
# Expected: min ≥ 150, max ≤ 350, avg ≈ 170

# List all chunk IDs (verification)
SELECT metadata->>'chunk_id' FROM rag_chunks 
WHERE source_type = 'synthetic_disambiguator'
ORDER BY metadata->>'chunk_id'
LIMIT 5;
```

---

## Rollback Procedure

If deployment fails, automatic rollback is included in the script. However, you can also rollback manually:

```bash
# Restore from backup created before deployment
psql -h db.XXXX.supabase.co -U postgres -d postgres -p 5432 \
  -f backups/staging_YYYYMMDD_HHMMSS.sql

# Verify rollback
SELECT COUNT(*) FROM rag_chunks 
WHERE source_type = 'synthetic_disambiguator';
# Should be back to pre-deployment state
```

---

## Troubleshooting

### Error: "psql not found"
**Solution:** Install PostgreSQL client
```bash
brew install postgresql@15  # macOS
sudo apt-get install postgresql-client  # Linux
```

### Error: "FATAL: password authentication failed"
**Solution:** Check admin password
- Verify you're using the correct admin password (not database password)
- Try connecting manually first:
  ```bash
  psql -h db.XXXX.supabase.co -U postgres
  ```

### Error: "relation 'rag_chunks' does not exist"
**Solution:** Table may not exist yet
- The script will create it automatically on first run
- Or manually create schema:
  ```bash
  psql -h db.XXXX.supabase.co -U postgres -d postgres \
    -c "CREATE TABLE IF NOT EXISTS rag_chunks (
      id SERIAL PRIMARY KEY,
      source_type TEXT,
      context_tag TEXT,
      chunk_text TEXT,
      source_reference TEXT,
      domain_tag TEXT,
      embedding_weight FLOAT,
      metadata_json JSONB,
      created_at TIMESTAMP DEFAULT NOW()
    );"
  ```

### Error: "connection timeout"
**Solution:** Check network connectivity
- Verify Supabase host is correct
- Check if you're on a network that allows PostgreSQL (port 5432)
- Try from different network or VPN

---

## Next Steps After Deployment

### Immediate (Day 1)
1. ✅ SQL migration deployed
2. 📋 Run 39-query benchmark on staging
3. 📋 Verify Recall@1 ≥ 84.62%
4. 📋 Verify contamination = 0%

### Short-term (Week 1)
1. 📋 Set up embedding services (WS4)
2. 📋 Configure monitoring (WS4)
3. 📋 Load testing (up to 50 QPS)
4. 📋 UAT with domain experts

### Medium-term (Week 2-3)
1. 📋 S10 fine-tuning (WS2)
2. 📋 Production sign-offs
3. 📋 Go-live preparation
4. 📋 Production deployment 2026-08-15

---

## Support

**Issues or questions?**
- Check deployment log: `docs/deployment/STAGING_DEPLOYMENT_LOG.txt`
- Review SQL migration: `supabase/migrations/2026_07_26_rag_phase3_corrected.sql`
- Contact: RAG Engineering Lead

---

**Prepared by:** Agente RAG Benchmark  
**Status:** Ready for team execution  
**Timeline:** Execution any time (2026-07-27 onwards)
