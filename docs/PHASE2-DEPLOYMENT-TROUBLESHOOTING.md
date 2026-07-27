# Phase 2 Deployment Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** 2026-07-27  
**Owner:** DevOps & Maestro Teams

---

## Quick Diagnosis Matrix

| Symptom | Component | Likely Cause | Solution |
|---------|-----------|--------------|----------|
| Search returns wrong results | RAG | Poor chunking or embeddings | Re-embed collection |
| Vector search slow (>1000ms) | RAG | Poor index configuration | Increase nprobes, rebuild index |
| Ingestion costs high (>$200) | RAG | Duplicate chunks, retries | Deduplicate, fix retry logic |
| SharePoint sync hangs | Sync | API token expired | Refresh Graph token |
| Feedback submissions stop | Feedback | Database issue | Check connection, restart service |
| API returning 5xx errors | System | Service outage | Check logs, restart component |

---

## Phase 2.4: RAG Ingestion Issues

### Problem: Vector Search Returns Irrelevant Results

**Symptoms:**
- Top-1 relevance score <70% (target ≥85%)
- Wrong collection being returned
- Semantic similarity doesn't match query meaning

**Root Causes:**
1. Poor document chunking (too large, too small, wrong boundaries)
2. Low-quality embeddings (model not suitable for domain)
3. Vector index not rebuilt after ingestion
4. Embedding dimensions mismatch

**Diagnosis Steps:**

```bash
# Step 1: Check embedding quality
python3 << 'EOPYTHON'
import sys
sys.path.append('/home/user/Codex-exemplo/scripts')
from test_embeddings import check_embedding_quality

quality_report = check_embedding_quality(
    test_queries=[
        "O que é CBUQ?",  # Should embed to saneamento
        "Transmissão LT",  # Should embed to energia
    ],
    top_k=5
)
print(json.dumps(quality_report, indent=2))
EOPYTHON
```

**Expected output:**
```json
{
  "saneamento_query": {
    "top_1_match": "saneamento",
    "confidence": 0.95
  },
  "energia_query": {
    "top_1_match": "energia",
    "confidence": 0.92
  }
}
```

**Step 2: Check vector index state:**
```bash
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT
  schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'rag%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
SQL
```

**Solution:**

If embeddings are poor:
```bash
# Option A: Use different model
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --embedding-model "text-embedding-004-new" \
  --force-re-embed
```

If index needs rebuilding:
```bash
# Option B: Rebuild vector index
python3 << 'EOPYTHON'
import psycopg2

conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()

# Recreate IVFFLAT index with better parameters
cur.execute("""
  DROP INDEX IF EXISTS idx_rag_embedding CASCADE;
  CREATE INDEX idx_rag_embedding ON rag_documents
    USING ivfflat (chunk_embedding vector_cosine_ops)
    WITH (lists = 100, probes = 20);
""")

conn.commit()
cur.close()
conn.close()
print("✓ Index rebuilt with parameters: lists=100, probes=20")
EOPYTHON
```

If chunks are poor:
```bash
# Option C: Rechunk documents
python3 scripts/chunk_documents.py \
  --input-dir docs/rag \
  --output-dir chunks-v2 \
  --chunk-size 400 \
  --overlap 150 \
  --strategy semantic  # Use semantic boundaries instead of sliding window
```

---

### Problem: Ingestion Stops or Fails

**Symptoms:**
```
[ERROR] Ingestion failed at 2,145 chunks
[ERROR] Status: FAILED
[ERROR] Last collection: saneamento
```

**Root Causes:**
1. Network timeout during embedding API call
2. Supabase connection lost
3. Invalid embedding response
4. Chunk size exceeds model limit

**Diagnosis:**

```bash
# Check logs
tail -100 /tmp/ingest_rag_documents.log | grep ERROR

# Expected error patterns:
# - "Connection timeout" → Network issue
# - "Invalid embedding" → Model issue
# - "Database error" → Supabase issue
```

**Solutions:**

**For network timeouts:**
```bash
# Increase timeout and reduce batch size
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --batch-size 25 \
  --timeout 60 \
  --max-retries 5 \
  --retry-backoff exponential
```

**For Supabase connection issues:**
```bash
# Test connection
python3 << 'EOPYTHON'
import psycopg2
import os

try:
    conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
    print("✓ Connection successful")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("Database:", cur.fetchone())
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOPYTHON
```

**For chunk size issues:**
```bash
# Verify chunk sizes
wc -w chunks/*.jsonl | awk '{print $1}' | sort -n | tail -20

# If chunks exceed 1000 tokens, rechunk:
python3 scripts/chunk_documents.py \
  --input-dir docs/rag \
  --output-dir chunks-fixed \
  --chunk-size 400 \
  --max-chunk-size 800
```

**Resume failed ingestion:**
```bash
# Ingest only failed collections
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --skip-collections saneamento,energia \
  --only-collections portos,aeroportos,barragens
```

---

### Problem: High Embedding Costs

**Symptoms:**
```
Total embeddings cost: $450 (expected <$100)
Cost per token: $0.00025 (expected $0.00002)
```

**Root Causes:**
1. Duplicate chunks being re-embedded
2. Incorrect retry logic (retrying successfully embedded chunks)
3. Test queries using API instead of cached embeddings
4. Wrong pricing model selected

**Diagnosis:**

```bash
# Check for duplicates
python3 << 'EOPYTHON'
import json
from collections import Counter

chunk_hashes = []
with open("chunks/embeddings_manifest.jsonl") as f:
    for line in f:
        data = json.loads(line)
        chunk_hashes.append(data['hash'])

duplicates = [h for h, count in Counter(chunk_hashes).items() if count > 1]
print(f"Duplicate chunks found: {len(duplicates)}")

# Show which are duplicated
for dup_hash in duplicates[:5]:
    count = chunk_hashes.count(dup_hash)
    print(f"  Hash {dup_hash}: embedded {count} times")
EOPYTHON
```

**Solutions:**

**Remove duplicates:**
```bash
python3 scripts/deduplicate_chunks.py \
  --input-dir chunks/ \
  --output-dir chunks-dedup/ \
  --hash-algorithm sha256
```

**Fix retry logic:**
```bash
# Modify retry strategy to skip already-embedded chunks
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks-dedup/ \
  --skip-existing \
  --batch-size 100
```

**Check actual cost:**
```bash
# Query Supabase for embedding usage
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT
  COUNT(*) as total_embeddings,
  SUM(token_count) as total_tokens,
  ROUND(SUM(token_count) * 0.00002, 2) as estimated_cost_usd
FROM rag_documents
WHERE chunk_embedding IS NOT NULL;
SQL
```

---

### Problem: Vector Search Slow (>500ms)

**Symptoms:**
```
Latency p95: 1,200ms (target: <500ms)
Query: "What is CBUQ?" → 1,145ms response time
```

**Root Causes:**
1. IVFFLAT index parameters suboptimal (nprobes too low)
2. Too many similar chunks (high recall at cost of latency)
3. Network latency to database
4. Index fragmentation

**Diagnosis:**

```bash
# Check index statistics
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename LIKE 'rag%'
ORDER BY idx_scan DESC;
SQL
```

**Solutions:**

**Increase nprobes for faster search:**
```bash
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
DROP INDEX IF EXISTS idx_rag_embedding CASCADE;

CREATE INDEX idx_rag_embedding ON rag_documents
  USING ivfflat (chunk_embedding vector_cosine_ops)
  WITH (lists = 50, probes = 5);
-- Start with fewer probes, increase if needed

ANALYZE rag_documents;
SQL
```

**Test with various probe counts:**
```python
# Test latency with different nprobes
import time

for nprobes in [5, 10, 20, 50]:
    # Rebuild index
    # Run test queries
    # Measure latency
    # Report results
```

---

## Phase 2.5: SharePoint Sync Issues

### Problem: Sync Hangs or Times Out

**Symptoms:**
```
[2026-07-28 14:15:12] Fetching agents from GitHub...
[2026-07-28 14:45:30] TIMEOUT - No activity for 30 minutes
```

**Root Causes:**
1. Microsoft Graph API token expired
2. GitHub API rate limit exceeded
3. SharePoint site unavailable or slow
4. Network connectivity issue

**Diagnosis:**

```bash
# Test Graph API
python3 << 'EOPYTHON'
import requests
import os

token_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(
    os.getenv("MICROSOFT_TENANT_ID")
)

data = {
    "grant_type": "client_credentials",
    "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
    "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
    "scope": "https://graph.microsoft.com/.default"
}

response = requests.post(token_url, data=data)
if response.status_code == 200:
    print("✓ Graph API token acquired")
else:
    print(f"✗ Token failed: {response.status_code}")
    print(response.json())
EOPYTHON
```

**Test SharePoint connectivity:**
```bash
# Test site access
curl -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/mantaassociados.sharepoint.com:/sites/maestro"
```

**Solutions:**

**Refresh API token:**
```bash
python3 scripts/refresh_graph_token.py
```

**Check rate limits:**
```bash
# GitHub rate limit
curl -H "Authorization: token $GITHUB_PAT" \
  https://api.github.com/rate_limit | jq '.rate_limit'
```

**Increase timeouts:**
```bash
# In sync config
{
  "sync": {
    "graph_api_timeout": 60,      // Increase from 30
    "github_api_timeout": 60,      // Increase from 30
    "sharepoint_request_timeout": 120
  }
}
```

---

### Problem: Sync Conflicts

**Symptoms:**
```
[ERROR] Conflict detected: agente-saneamento.md
[ERROR] Modified in both GitHub and SharePoint
[ERROR] Cannot auto-resolve
```

**Root Causes:**
1. Simultaneous edits in GitHub and SharePoint
2. Network delay causing race condition
3. Version mismatch

**Diagnosis:**

```bash
# Check version history in GitHub
git log --oneline -- .claude/agents/agente-saneamento.md | head -5

# Check version in SharePoint
curl -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drive/items/{ITEM_ID}/versions"
```

**Solutions:**

**Resolve with GitHub priority:**
```bash
python3 << 'EOPYTHON'
from sharepoint_sync.conflict_resolver import resolve_conflict

conflict_file = ".claude/agents/agente-saneamento.md"
resolution = resolve_conflict(
    file=conflict_file,
    strategy="github_priority",
    verbose=True
)
print(f"Resolved: {resolution}")
EOPYTHON
```

**Resolve with SharePoint priority:**
```bash
# Copy SharePoint version to GitHub
# Then sync
python3 scripts/sharepoint_sync_engine.py \
  --config configs/sharepoint_sync_config.json \
  --conflict-strategy sharepoint_priority
```

**Manual resolution:**
```bash
# 1. Check both versions
git show HEAD:.claude/agents/agente-saneamento.md > /tmp/github_version.md
curl -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drive/items/{ITEM_ID}/content" \
  > /tmp/sharepoint_version.md

# 2. Review and merge manually
diff /tmp/github_version.md /tmp/sharepoint_version.md

# 3. Create merged version
# (edit /tmp/github_version.md with content from both)

# 4. Push to GitHub
cp /tmp/github_version.md .claude/agents/agente-saneamento.md
git add .claude/agents/agente-saneamento.md
git commit -m "Resolve SharePoint sync conflict: manual merge"
git push origin main
```

---

### Problem: Files Not Syncing

**Symptoms:**
```
Expected files in SharePoint: 15
Actual files found: 12
Missing: agente-portos.md, agente-aeroportos.md, agente-barragens.md
```

**Root Causes:**
1. Sync service not running
2. File permissions issue
3. SharePoint folder path incorrect
4. Files not tracked in GitHub

**Diagnosis:**

```bash
# Check if sync service is running
ps aux | grep sharepoint_sync

# Check logs
tail -50 /var/log/maestro/sharepoint_sync.log | grep -i error

# Verify files exist in GitHub
git ls-files | grep ".claude/agents"
```

**Solutions:**

**Restart sync service:**
```bash
systemctl restart maestro-sharepoint-sync
sleep 5
systemctl status maestro-sharepoint-sync
```

**Check file permissions:**
```bash
# In SharePoint, verify folder permissions
# User must have "Edit" or "Contribute" on the folder
```

**Verify folder paths:**
```bash
# Check config
cat configs/sharepoint_sync_config.json | jq '.sharepoint'

# Should show:
# {
#   "site_url": "https://mantaassociados.sharepoint.com/sites/maestro",
#   "root_folder": "03_Projetos"
# }
```

**Force re-sync:**
```bash
# Run sync with force flag
python3 scripts/sharepoint_sync_engine.py \
  --config configs/sharepoint_sync_config.json \
  --force-all \
  --dry-run  # First check what will happen

# Then without dry-run
python3 scripts/sharepoint_sync_engine.py \
  --config configs/sharepoint_sync_config.json \
  --force-all
```

---

## System-Wide Issues

### Problem: Database Connection Pooling Exhausted

**Symptoms:**
```
[ERROR] FATAL: too many connections
[ERROR] remaining connection slots are reserved for non-replication superuser connections
```

**Root Causes:**
1. Ingestion pipeline creating too many connections
2. Stale connections not being closed
3. Connection pool misconfigured

**Solution:**

```bash
# Check current connections
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT count(*) as total_connections FROM pg_stat_activity;
SQL

# Kill idle connections
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes';
SQL

# Increase pool size in config
{
  "database": {
    "max_connections": 20,
    "connection_timeout": 10,
    "pool_size": 5,
    "max_overflow": 10
  }
}
```

---

### Problem: Out of Memory

**Symptoms:**
```
MemoryError: Unable to allocate 2.3 GB
Killed process: ingest_rag_documents.py
```

**Root Causes:**
1. Batch size too large
2. Loading entire file into memory
3. Embedding cache not cleared

**Solution:**

```bash
# Reduce batch size
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --batch-size 10  # Reduce from 100

# Enable streaming mode
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --streaming \
  --chunk-file-size 1000  # Process 1000 chunks at a time

# Clear embedding cache between batches
--cache-mode none
```

---

## Escalation & Support

### When to Escalate

| Issue Type | Level 1 | Level 2 | Level 3 | Level 4 |
|-----------|---------|---------|---------|---------|
| High latency (>500ms) | Check config | Performance tune | Architect review | Escalate to AWS |
| Sync conflicts (>3) | Manual merge | Review sync logic | Design review | Product decision |
| Cost overrun (>2x budget) | Check usage | Optimize model | Budget review | Executive decision |
| Downtime (>5 min) | Restart service | Check infra | Incident response | CEO notification |

### Support Contact

**On-Call Engineer:** maestro-on-call@mantaassociados.com  
**Slack:** #maestro-deployment  
**PagerDuty:** maestro-phase2-oncall  
**Escalation:** Contact team lead or CTO

---

## Appendix: Useful Commands

### Database Queries

```bash
# RAG status
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT 
  collection_id,
  COUNT(*) as chunks,
  COUNT(CASE WHEN chunk_embedding IS NOT NULL THEN 1 END) as embedded,
  MAX(updated_at) as last_updated
FROM rag_documents
GROUP BY collection_id;
SQL

# Feedback metrics
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT * FROM feedback_metrics LIMIT 10;
SQL

# SharePoint sync status
psql -h $SUPABASE_HOST -U postgres -d postgres << SQL
SELECT 
  agent_name,
  status,
  COUNT(*) as count,
  MAX(synced_at) as last_sync
FROM sharepoint_sync_log
GROUP BY agent_name, status
ORDER BY last_sync DESC;
SQL
```

### Monitoring

```bash
# Real-time log monitoring
tail -f /var/log/maestro/phase2.log | grep -E "ERROR|WARN"

# CloudWatch Insights query
aws logs start-query \
  --log-group-name "/maestro/phase2" \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @duration | stats avg(@duration) by bin(5m)'
```

### Cleanup & Maintenance

```bash
# Clear old logs (30+ days)
aws logs delete-log-group --log-group-name "/maestro/phase2/old"

# Archive to S3
aws s3 sync /var/log/maestro/ s3://maestro-logs/$(date +%Y-%m-%d)/

# Reset vector index statistics
ANALYZE rag_documents;
```

---

**Last Updated:** 2026-07-27  
**Maintainer:** DevOps & Maestro Teams
