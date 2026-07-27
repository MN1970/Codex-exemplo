# MAESTRO OS v6.0 — Troubleshooting Procedures

**Version:** 6.0.0  
**Target Audience:** SRE, On-Call Engineers  
**Purpose:** Rapid diagnosis and resolution of production issues  
**Last Updated:** 2026-07-26

---

## Part 1: Symptoms → Root Causes Matrix

| Symptom | Likely Root Cause | Confidence | Quick Check | Runbook Section |
|---------|-------------------|------------|-------------|-----------------|
| Workflows timeout (>5 sec SLA) | Queue executor backlog | High | `queue_depth > 1000` | Issue #3 |
| Consensus polls timeout (>15 min) | Voter offline or dead | High | `GET /consensus/quorum` | Issue #2 |
| All agents failing | Agent router down | Critical | `GET /agents/status` | Issue #5 |
| "Rate limit exceeded" errors | External API throttling | High | `GET /rate-limits` | Issue #4 |
| Workflows silently stuck | Database deadlock | High | `GET /db/queries?running=true` | Issue #2 |
| Cache hit rate plummet (70% → 40%) | Cache eviction or memory pressure | Medium | `GET /cache/info` | Issue #1 |
| Token burn spike (20K → 100K/sec) | Consensus retry loop | High | `GET /tokens/breakdown` | Issue #1 |
| 30%+ of workers unhealthy | Worker code crash | High | `GET /workers?status=dead` | Issue #5 |
| "Consensus deadlock" warnings | Voter divergence / conflicting data | Medium | Check poll votes | Section 2 |
| Database connection pool exhausted | Connection leak or long queries | Medium | `GET /db/pool` | Issue #5 |

---

## Part 2: Step-by-Step Diagnostics

### Diagnostic 1: Workflow Timeout (>5 sec)

**Time to Execute:** 2 minutes  
**Expected Resolution:** Queue optimization or worker scaling

```bash
# Step 1: Confirm timeout
curl -s https://maestro-api.internal/workflows/recent?limit=10 | \
  jq '.workflows[] | select(.duration_seconds > 5) | {id, duration_seconds}'

# Step 2: Identify bottleneck phase
curl -s https://maestro-api.internal/workflows/{workflow_id}/timeline | \
  jq '.phases[] | {phase, duration_ms}' | sort -k2 -rn | head -1

# Example output: "queue_execution": 5600 ms (slowest)

# Step 3: Check queue depth
QUEUE_DEPTH=$(curl -s https://queue-executor.maestro-internal/metrics | jq '.queue_depth')
if [ $QUEUE_DEPTH -gt 1000 ]; then
  echo "QUEUE DEPTH HIGH: $QUEUE_DEPTH tasks queued"
  # → Increase worker count
  curl -X PATCH https://queue-executor.maestro-internal/control \
    -d '{"worker_count": 15}'
fi

# Step 4: Check worker pool
curl -s https://queue-executor.maestro-internal/workers | \
  jq '{total: .total, busy: .busy, available: .available}'

# Step 5: Monitor recovery
watch -n 2 'curl -s https://queue-executor.maestro-internal/metrics | jq ".queue_depth"'
# Wait for queue_depth to drop to < 500

# Resolve: Once queue_depth < 500 and avg latency < 3 sec, return workers to original count
curl -X PATCH https://queue-executor.maestro-internal/control \
  -d '{"worker_count": 10}'
```

---

## Part 3: Data Integrity Checks

Run these to detect corruption or stale data.

### Check 3.1: Workflow State Consistency

```bash
# Verify workflow state matches queue executor state
curl -s https://maestro-api.internal/workflows | jq '.workflows[] | {id, state}' > workflows.json

curl -s https://queue-executor.maestro-internal/tasks | jq '.tasks[] | {workflow_id, state}' > queue_tasks.json

# Compare
jq -r '.[] | .id' workflows.json | while read WF; do
  WF_STATE=$(jq -r ".[] | select(.id==\"$WF\") | .state" workflows.json)
  TASK_STATE=$(jq -r ".[] | select(.workflow_id==\"$WF\") | .state" queue_tasks.json)
  if [ "$WF_STATE" != "$TASK_STATE" ]; then
    echo "MISMATCH: $WF state=$WF_STATE but task state=$TASK_STATE"
  fi
done

# Expected: No mismatches. If found → Contact DBA for investigation.
```

### Check 3.2: Cache Validity vs Database

```bash
# Sample cache entries and verify against database
curl -s https://cache.maestro-internal/entries?sample=10 | jq '.entries[]' | while read ENTRY; do
  KEY=$(echo $ENTRY | jq -r '.key')
  CACHED_VAL=$(echo $ENTRY | jq -r '.value')
  DB_VAL=$(psql maestro_db -t -c "SELECT value FROM cache_source WHERE key='$KEY'" 2>/dev/null)
  
  if [ "$CACHED_VAL" != "$DB_VAL" ]; then
    echo "STALE CACHE: $KEY (cache: $CACHED_VAL, db: $DB_VAL)"
  fi
done

# Expected: All match. If > 10% mismatch → Flush cache (see Diagnostic 6)
```

### Check 3.3: Consensus Poll Input Integrity

```bash
# Verify recent consensus polls have consistent input data
curl -s https://maestro-api.internal/consensus/polls?status=completed&hours=6 | \
  jq '.polls[] | {id, input_hash, data_integrity_check}' | \
  jq -s 'group_by(.input_hash) | map({hash: .[0].input_hash, count: length}) | .[] | select(.count > 1)'

# Expected: Each poll has unique input_hash (no duplicates unless intended)
# If same input reused: Verify voters responding consistently
```

---

## Part 4: Log Rotation & Retention Policies

### Log Retention Schedule

| Log Type | Retention | Archive Location | Searchable Until |
|----------|-----------|------------------|------------------|
| Application (INFO+) | 7 days | S3: maestro-logs/archive/ | 90 days |
| Error logs (ERROR+) | 14 days | S3: maestro-logs/errors/ | 1 year |
| Audit logs (all) | 30 days | S3: maestro-logs/audit/ | 1 year (legal hold) |
| Debug logs (DEBUG+) | 3 days | Local: /var/log/maestro/debug/ | Not archived |

### Log Rotation Commands

```bash
# Manual log rotation (if automated fails)
kubectl exec -n maestro-system $(kubectl get pod -n maestro-system -l app=maestro-api -o jsonpath='{.items[0].metadata.name}') \
  -- sh -c 'logrotate -f /etc/logrotate.d/maestro'

# Verify rotation
ls -lh /var/log/maestro/maestro-api.log*

# Archive old logs to S3
find /var/log/maestro -name "*.log.*" -mtime +7 -exec \
  aws s3 cp {} s3://maestro-logs/archive/{} \; && \
  find /var/log/maestro -name "*.log.*" -mtime +7 -delete
```

---

## Part 5: Metrics & Performance Profiling

### Profile 5.1: Slow Consensus Polls

```bash
# Find consensus polls that took > 2 seconds
curl -s https://maestro-api.internal/consensus/polls?status=completed | \
  jq '.polls[] | select(.duration_seconds > 2) | {id, duration_seconds, voter_count, agreement_rate}' | \
  sort_by(.duration_seconds) | reverse | head -20

# Analyze pattern (more voters = longer?)
# If duration correlates with voter count: Expected behavior
# If duration inconsistent: Check for network latency or voter responsiveness issues
```

### Profile 5.2: Agent Latency Distribution

```bash
# Get latency percentiles for each agent
curl -s https://maestro-api.internal/agents/metrics | \
  jq '.agents[] | {agent_id, latency_p50_ms, latency_p99_ms, latency_p999_ms}' | \
  column -t

# Expected: p99 < 500ms, p999 < 1000ms
# If p999 > 1000ms: Investigate tail latency (GC pause? Resource contention?)
```

### Profile 5.3: Token Consumption by Workflow Type

```bash
# Break down tokens by workflow type (last 24 hours)
curl -s https://maestro-api.internal/tokens/by-workflow-type?hours=24 | \
  jq '.workflows[] | {type, count, tokens_per_workflow_avg}' | \
  sort_by(.tokens_per_workflow_avg) | reverse

# Identify expensive workflow types, optimize context window or enable batching
```

---

## Part 6: Database Query Recipes

### Query 6.1: Find Workflows in "Stuck" States

```sql
-- PostgreSQL query to find workflows stuck > 20 minutes in same state
SELECT id, state, created_at, EXTRACT(EPOCH FROM (NOW() - created_at)) as age_seconds
FROM workflows
WHERE created_at > NOW() - INTERVAL '1 day'
  AND EXTRACT(EPOCH FROM (NOW() - updated_at)) > 1200  -- 20 minutes
ORDER BY age_seconds DESC
LIMIT 20;

-- Result: Shows stuck workflow IDs and how long they've been stuck
```

### Query 6.2: Consensus Poll Agreement Rates (Last 24h)

```sql
-- Find consensus polls and their agreement rates
SELECT 
  id, 
  vote_count, 
  ROUND(agreement_percent::numeric, 2) as agreement_rate,
  EXTRACT(EPOCH FROM (resolved_at - created_at)) as duration_seconds
FROM consensus_polls
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND status = 'resolved'
ORDER BY created_at DESC
LIMIT 50;

-- Expected: Most polls have agreement > 75%
-- If many < 60%: Investigate voter divergence
```

### Query 6.3: Agent Response Cache Hit Rate

```sql
-- Measure cache effectiveness for agent responses
SELECT 
  COUNT(*) FILTER (WHERE cache_hit=true) as cache_hits,
  COUNT(*) as total_requests,
  ROUND(100.0 * COUNT(*) FILTER (WHERE cache_hit=true) / COUNT(*), 2) as hit_rate_percent
FROM agent_execution_log
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY agent_id
ORDER BY hit_rate_percent DESC;

-- Expected: hit_rate > 70% (good caching)
-- If < 50%: Cache is not effective, investigate query patterns
```

### Query 6.4: Daily Token Burn Trend

```sql
-- Trend token consumption over last 7 days
SELECT 
  DATE(created_at) as day,
  SUM(tokens_consumed) as daily_total,
  ROUND(AVG(tokens_consumed), 0) as avg_per_workflow,
  COUNT(*) as workflow_count
FROM token_log
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY day DESC;

-- Spot trends: Is burn rate increasing day-over-day?
```

---

## Part 7: Quick Reference — Common Fixes

| Problem | Symptom | Quick Fix (< 2 min) | If Fails |
|---------|---------|-------------------|----------|
| Queue stuck | queue_depth > 5000 | `POST /queue-executor/control/drain` | Restart workers |
| Cache stale | hit_rate 40% | `POST /cache/flush` (graceful) | Full rebuild |
| Agent offline | agent not responding | `GET /agents/{id}/health` then restart | Check logs for error |
| Consensus timeout | poll > 15 min | `POST /consensus/polls/{id}/escalate` | Force weighted voting |
| Rate limit | HTTP 429 | Enable `enable_adaptive_backoff` | Contact API provider |
| Worker dead | status="dead" | Restart pod or worker pool | Check crash logs |
| DB connection pool | util > 85% | `POST /db/pool/cleanup` | Optimize slow queries |

---

**Document Version:** 6.0.0  
**Last Updated:** 2026-07-26  
**Owner:** SRE Team  
**Next Review:** 2026-08-26
