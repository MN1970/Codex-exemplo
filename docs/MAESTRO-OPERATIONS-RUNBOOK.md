# MAESTRO OS v6.0 — Operations Runbook

**Version:** 6.0.0  
**Last Updated:** 2026-07-26  
**Owner:** Site Reliability Engineering (SRE) Team  
**Escalation Contact:** oncall@maestro-ops.internal  
**Maintenance Window:** Sunday 02:00–04:00 UTC (30-min alert required)

---

## 1. SLA Definitions & Uptime Targets

| Tier | Availability | Max Downtime/Month | Response Time | Recovery Time |
|------|--------------|-------------------|----------------|----------------|
| P1 (Critical) | 99.99% | 4 min 23 sec | 15 min | 30 min |
| P2 (High) | 99.9% | 43 min 12 sec | 30 min | 1 hour |
| P3 (Standard) | 99.5% | 3 hours 36 min | 2 hours | 4 hours |

**Current Status Dashboard:** https://maestro-ops.internal/status  
**Incident Channel:** #maestro-incidents (Slack)

---

## 2. Daily Health Checks (Phased)

### Phase 1: First 4 Hours (Hourly Checks — 00:00, 01:00, 02:00, 03:00 UTC)

Run these every hour for the first 4 hours after deployment or after maintenance windows.

#### 2.1.1 Core Service Health

```bash
# Check all service endpoints
curl -s https://maestro-api.internal/health/status | jq '.status'
curl -s https://maestro-api.internal/health/readiness | jq '.ready'

# Expected output: "healthy", "ready": true

# Check detector service (consensus voting engine)
curl -s https://detector.maestro-internal/health | jq '.uptime_seconds'

# Check queue executor
curl -s https://queue-executor.maestro-internal/health | jq '.worker_pool_active'

# Verify all expected: detector, queue-executor, ml-inference, vector-db, cache
```

#### 2.1.2 Consensus Engine Health

```bash
# Check active consensus polls in-flight
curl -s https://maestro-api.internal/consensus/status | jq '.active_polls, .avg_poll_duration_ms'

# Expected: active_polls < 50, avg_poll_duration_ms < 2000

# Check voting quorum availability
curl -s https://maestro-api.internal/consensus/quorum | jq '.quorum_members[] | {name, status, latency_ms}'

# All members should be "healthy" with latency < 100ms
```

#### 2.1.3 Queue Executor Status

```bash
# Check task queue depth
curl -s https://queue-executor.maestro-internal/metrics | jq '.queue_depth, .in_flight_tasks'

# Expected: queue_depth < 1000, in_flight_tasks < 100

# Check worker availability
curl -s https://queue-executor.maestro-internal/workers | jq '.available, .total, .busy'

# Alert if available < total * 0.2 (less than 20% free capacity)
```

#### 2.1.4 Token Budget Status

```bash
# Check aggregate token burn rate
curl -s https://maestro-api.internal/tokens/status | jq '.burn_rate_tokens_per_sec, .daily_budget, .consumed_today'

# Expected: burn_rate < 50,000 tokens/sec (adjust per contract)
# consumed_today should be < daily_budget * 0.8 (not exceeding 80% by hour 4)
```

#### 2.1.5 Logs Ingestion & Streaming

```bash
# Verify log shipper is operational
curl -s https://logs.maestro-internal/health | jq '.last_write_timestamp, .pending_logs'

# pending_logs should be < 1000 (indicates log queue is draining)
```

### Phase 2: Standard Daily Checks (After Hour 4, then 2x Daily)

Run at **08:00 UTC** and **16:00 UTC** (morning and afternoon daily checks).

#### 2.2.1 Database Connection Pool

```bash
# Check PostgreSQL connection pool
curl -s https://maestro-api.internal/db/pool | jq '.connections_active, .connections_idle, .connections_max'

# Expected: connections_active < connections_max * 0.8

# Check pgvector (embedding DB) status
curl -s https://vectordb.maestro-internal/health | jq '.connection_pool_util'

# Alert if util > 85%
```

#### 2.2.2 Cache Layer Health (Redis)

```bash
# Check Redis memory usage and eviction
curl -s https://cache.maestro-internal/info | jq '.memory_used_mb, .memory_max_mb, .evictions_total'

# Alert if memory_used > memory_max * 0.90

# Check cache hit ratio
curl -s https://cache.maestro-internal/metrics | jq '.hit_rate_percent, .miss_rate_percent'

# Expected: hit_rate > 70% for consensus cache, > 85% for agent response cache
```

#### 2.2.3 ML Inference Pipeline

```bash
# Check model load status
curl -s https://ml-inference.maestro-internal/models | jq '.loaded_models[] | {name, latency_p99_ms, cache_hit_rate}'

# Expected: latency_p99 < 500ms, cache_hit_rate > 70%

# Check GPU/TPU utilization
curl -s https://ml-inference.maestro-internal/hardware | jq '.gpu_util_percent, .memory_util_percent, .queue_depth'

# Alert if queue_depth > 100 (indicating inference backlog)
```

#### 2.2.4 Consensus Voting Metrics

```bash
# Check consensus poll outcomes (healthy == high agreement)
curl -s https://maestro-api.internal/consensus/metrics | jq '.agreement_rate_percent, .escalation_rate_percent'

# Expected: agreement_rate > 85%, escalation_rate < 5%

# Check consensus deadlock detector
curl -s https://maestro-api.internal/consensus/deadlocks | jq '.total_deadlocks_24h, .last_deadlock_timestamp'

# Alert if total_deadlocks_24h > 2
```

#### 2.2.5 Workflow Execution Health

```bash
# Check active workflows
curl -s https://maestro-api.internal/workflows/active | jq '.total, .stuck_workflows, .avg_duration_seconds'

# Expected: stuck_workflows == 0, avg_duration < SLA definition

# Check workflow state transitions
curl -s https://maestro-api.internal/workflows/metrics | jq '.created_24h, .completed_24h, .failed_24h'

# Alert if failed_24h > completed_24h * 0.05 (>5% failure rate)
```

#### 2.2.6 Agent Execution Metrics

```bash
# Check per-agent success rates
curl -s https://maestro-api.internal/agents/metrics | jq '.agents[] | {agent_id, success_rate, avg_latency_ms, error_count_24h}'

# Expected: success_rate > 95% for each agent, error_count_24h < 10

# Check for agent crashes
curl -s https://maestro-api.internal/agents/crashes | jq '.recent_crashes[] | {agent_id, timestamp, error_type}'
```

#### 2.2.7 Rate Limiting & Backoff State

```bash
# Check external API rate limit headroom
curl -s https://maestro-api.internal/rate-limits | jq '.limits[] | {api, requests_used, limit, remaining_percent}'

# Expected: remaining_percent > 20% for all APIs

# Check backoff queue (exponential backoff for rate-limited requests)
curl -s https://queue-executor.maestro-internal/backoff-queue | jq '.queued_tasks, .oldest_retry_timestamp'

# Alert if queued_tasks > 500
```

---

## 3. Workflow Monitoring & Issue Detection

### 3.1 Detecting Stuck Workflows

Workflows are considered "stuck" if they remain in the same state for > 2x expected duration.

#### 3.1.1 Automated Detection

```bash
# List workflows stuck > 10 minutes (adjust threshold per workflow type)
curl -s https://maestro-api.internal/workflows/stuck?threshold_minutes=10 | jq '.workflows[] | {id, state, duration_seconds, created_at}'

# Example output:
# {
#   "id": "wf_abc123",
#   "state": "consensus_pending",
#   "duration_seconds": 1200,
#   "created_at": "2026-07-26T10:30:00Z"
# }
```

#### 3.1.2 Root Cause Diagnosis

```bash
# Check workflow logs for the specific workflow
curl -s https://maestro-api.internal/workflows/abc123/logs | jq '.logs[] | {timestamp, level, message}' | head -50

# Common stuck patterns:
# - "consensus_pending": Check if consensus engine is responsive
# - "awaiting_agent_response": Check agent logs for errors
# - "queue_executor_blocked": Check queue executor worker pool
```

#### 3.1.3 Manual Intervention

```bash
# If consensus poll is stuck (>15 min in consensus_pending):
# 1. Check active consensus polls
curl -s https://maestro-api.internal/consensus/polls?status=active | jq '.polls[]'

# 2. Identify problematic poll
# 3. Escalate consensus poll (force resolution by weighted voting)
curl -X POST https://maestro-api.internal/consensus/polls/{poll_id}/escalate \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "timeout_10min", "force_resolution": true}'

# 4. Update workflow state
curl -X PATCH https://maestro-api.internal/workflows/{workflow_id} \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"state": "recovery_escalated"}'
```

### 3.2 Consensus Escalation Procedures

When consensus voting fails to reach agreement within timeout, escalation rules apply.

#### 3.2.1 Escalation Decision Tree

```
START: Consensus Poll (5 voters, 3+ agree = majority)
├─ Timeout (15 min)? → ESCALATE
├─ Unanimous (5/5 agree)? → COMMIT immediately
├─ Strong majority (4/5 agree)? → COMMIT after 5-sec final check
├─ Simple majority (3/5 agree)? → WAIT 30 sec for late votes, then COMMIT
├─ Weak plurality (2/5 agree)? → ESCALATE to weighted voting
└─ Deadlock (1/5 agree)? → ESCALATE to human review (P1 incident)

ESCALATE → Weighted Voting (high-confidence agents get 2x vote weight)
  ├─ Weighted majority (60%+)? → COMMIT
  └─ Still deadlocked? → ROLLBACK and human review
```

#### 3.2.2 Checking Escalation Status

```bash
# Get all escalations in last 24 hours
curl -s https://maestro-api.internal/consensus/escalations?hours=24 | jq '.escalations[] | {id, poll_id, reason, resolution, resolved_at}'

# Check ongoing escalations (unresolved)
curl -s https://maestro-api.internal/consensus/escalations?status=ongoing | jq '.escalations[]'

# Expected: ongoing escalations == 0 (all should be resolved within 30 min)
```

#### 3.2.3 Resolving Escalation Manually

```bash
# Get escalation details
curl -s https://maestro-api.internal/consensus/escalations/{escalation_id} | jq '.'

# Review votes and agent confidence scores
# Decision: COMMIT (force resolution) or ROLLBACK (retry workflow)

# Force resolution (weighted vote winner)
curl -X POST https://maestro-api.internal/consensus/escalations/{escalation_id}/resolve \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"decision": "commit", "human_review_notes": "Agent X confidence 0.92 > threshold 0.80"}'

# If rollback needed
curl -X POST https://maestro-api.internal/consensus/escalations/{escalation_id}/resolve \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"decision": "rollback", "human_review_notes": "Deadlock; requeuing workflow"}'
```

---

## 4. Queue Executor Troubleshooting

The queue executor manages task scheduling and worker pool allocation.

### 4.1 Detecting Stuck Tasks

```bash
# Find tasks stuck in queue or execution > 5 minutes
curl -s https://queue-executor.maestro-internal/tasks?status=stuck&threshold_minutes=5 | jq '.tasks[] | {id, state, enqueued_at, started_at, worker_id}'

# Expected: 0 stuck tasks

# Get queue depth (queued but not yet assigned)
curl -s https://queue-executor.maestro-internal/metrics | jq '.queue_depth, .queue_depth_percentile_p95'
```

### 4.2 Worker Pool Health

```bash
# Check worker availability
curl -s https://queue-executor.maestro-internal/workers | jq '.workers[] | {id, status, tasks_completed_24h, uptime_seconds, last_heartbeat}'

# Expected: all workers "healthy", last_heartbeat < 30 sec ago

# Check for dead workers (no heartbeat > 2 min)
curl -s https://queue-executor.maestro-internal/workers?status=dead | jq '.dead_workers[]'

# If dead workers exist, they will be auto-replaced within 1 min; alert if > 2 dead simultaneously
```

### 4.3 Clearing Stuck Tasks

```bash
# Option 1: Retry stuck task
curl -X POST https://queue-executor.maestro-internal/tasks/{task_id}/retry \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"attempt": 2, "backoff_seconds": 30}'

# Option 2: Reassign to different worker
curl -X PATCH https://queue-executor.maestro-internal/tasks/{task_id} \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"worker_id": "worker_xyz", "state": "queued"}'

# Option 3: Cancel task (use only if task is unrecoverable)
curl -X DELETE https://queue-executor.maestro-internal/tasks/{task_id} \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"reason": "unrecoverable_error", "notify_workflow": true}'
```

### 4.4 Worker Pool Reset

Use only if multiple workers are unresponsive and auto-healing is failing.

```bash
# Graceful shutdown of all workers (drain queue first)
curl -X POST https://queue-executor.maestro-internal/control/drain \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"drain_timeout_seconds": 300, "cancel_unfinished": false}'

# Wait for queue to drain (monitor queue_depth)
watch -n 5 'curl -s https://queue-executor.maestro-internal/metrics | jq ".queue_depth"'

# Once queue_depth == 0, restart worker pool
curl -X POST https://queue-executor.maestro-internal/control/restart-workers \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"worker_count": 10, "ramp_up_seconds": 60}'

# Verify workers are healthy
curl -s https://queue-executor.maestro-internal/workers | jq '.workers[] | {id, status}'
```

---

## 5. Common Issues & Resolutions

### Issue 1: High Token Burn Rate

**Symptom:** Token burn rate exceeds SLA (>50K tokens/sec)

**Root Causes:**
- Consensus polls retrying with full context (context window explosion)
- ML inference using large embedding batches
- Agent responses including full conversation history

**Resolution:**

```bash
# Check token distribution
curl -s https://maestro-api.internal/tokens/breakdown | jq '.by_component[] | {component, tokens_24h, percent}'

# If consensus is > 50%:
# 1. Enable context summarization for stalled polls
curl -X PATCH https://maestro-api.internal/consensus/config \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"enable_context_summarization": true, "summary_compression_ratio": 0.3}'

# 2. Reduce retry max attempts
curl -X PATCH https://maestro-api.internal/consensus/config \
  -d '{"max_poll_retries": 2}'

# If ML inference is > 50%:
# Check batch size and model input length
curl -s https://ml-inference.maestro-internal/config | jq '.batch_size, .max_input_tokens'

# Reduce batch size if under token pressure
curl -X PATCH https://ml-inference.maestro-internal/config \
  -d '{"batch_size": 8}'

# Monitor token burn rate recovery
watch -n 10 'curl -s https://maestro-api.internal/tokens/status | jq ".burn_rate_tokens_per_sec"'
```

### Issue 2: Consensus Deadlock (Voting Divergence)

**Symptom:** Consensus escalations > 5% of polls, agreement_rate < 70%

**Root Causes:**
- Agent outputs diverging due to different model versions
- Agent configuration skew (inconsistent parameters)
- Data integrity issues in input state

**Resolution:**

```bash
# 1. Check agent versions
curl -s https://maestro-api.internal/agents | jq '.agents[] | {id, version, model, config_hash}'

# If versions differ, trigger config sync
curl -X POST https://maestro-api.internal/agents/sync-config \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"target_version": "6.0.0"}'

# 2. Check consensus voter confidence distribution
curl -s https://maestro-api.internal/consensus/metrics | jq '.voter_confidence_distribution[]'

# If some agents consistently low confidence (< 0.5), investigate agent logs
curl -s https://maestro-api.internal/agents/{low_confidence_agent}/logs | jq '.logs[] | {timestamp, level, message}' | head -30

# 3. Verify input data integrity for recent polls
curl -s https://maestro-api.internal/consensus/polls?status=completed&hours=1 | jq '.polls[] | {id, input_hash, data_integrity_check}'

# If integrity check fails, rerun poll with validated input
curl -X POST https://maestro-api.internal/consensus/polls/{poll_id}/rerun \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"validate_input": true, "regenerate_context": true}'
```

### Issue 3: Workflow Timeout

**Symptom:** Workflows not completing within expected SLA

**Root Causes:**
- Consensus polls taking >15 min (consensus engine backlog)
- Agent response latency spike
- Queue executor task assignment delays

**Resolution:**

```bash
# Identify bottleneck
curl -s https://maestro-api.internal/workflows/{workflow_id}/timeline | jq '.phases[] | {phase, duration_seconds, percent_of_total}'

# If consensus phase > 50% of total:
# → Check consensus engine health (see section 3.2.2)
# → Consider escalating consensus polls to 10-minute timeout (vs 15 min default)

# If agent_execution phase > 50%:
# → Check agent latency metrics
curl -s https://maestro-api.internal/agents/metrics | jq '.agents[] | {id, latency_p99_ms, error_rate}'

# If queue_execution phase > 50%:
# → Check queue executor queue depth
curl -s https://queue-executor.maestro-internal/metrics | jq '.queue_depth, .avg_wait_time_seconds'

# Temporary: Increase worker pool
curl -X PATCH https://queue-executor.maestro-internal/control \
  -d '{"worker_count": 15, "ramp_up_seconds": 30}'
```

### Issue 4: Rate Limit Exceeded on External API

**Symptom:** Agent requests rejected with 429 HTTP status

**Root Causes:**
- Burst traffic exceeding API limits
- Backoff queue not properly implemented
- Rate limit headers not honored by client

**Resolution:**

```bash
# Check current rate limit status
curl -s https://maestro-api.internal/rate-limits | jq '.limits[] | {api, remaining, reset_at}'

# Enable adaptive backoff
curl -X PATCH https://maestro-api.internal/rate-limiting/config \
  -d '{"enable_adaptive_backoff": true, "min_backoff_seconds": 5, "max_backoff_seconds": 300}'

# Clear backoff queue to retry requests
curl -X POST https://queue-executor.maestro-internal/backoff-queue/flush \
  -H "Authorization: Bearer $MAESTRO_TOKEN" \
  -d '{"api": "anthropic", "drain_seconds": 60}'

# If limit persistently exceeded, contact API provider or upgrade plan
```

### Issue 5: Database Connection Pool Exhaustion

**Symptom:** Connection pool util > 85%, new queries timeout

**Root Causes:**
- Stale connections not being reaped
- Long-running queries holding connections
- Connection leak in application code

**Resolution:**

```bash
# Check connection pool state
curl -s https://maestro-api.internal/db/pool | jq '.'

# Kill idle connections older than 10 minutes
curl -X POST https://maestro-api.internal/db/pool/cleanup \
  -d '{"idle_timeout_seconds": 600}'

# Identify long-running queries
curl -s https://maestro-api.internal/db/queries?running=true | jq '.queries[] | {id, duration_seconds, query}'

# If any query > 5 minutes, investigate or cancel
curl -X POST https://maestro-api.internal/db/queries/{query_id}/cancel \
  -d '{"reason": "long_running", "notify_app": true}'

# Reduce connection pool max if sustainable (less total connections needed)
curl -X PATCH https://maestro-api.internal/db/config \
  -d '{"pool_max": 20}'
```

---

## 6. Escalation Matrix

| Severity | SLA Response | SLA Resolution | Actions | Escalation |
|----------|--------------|----------------|---------|------------|
| P1 (Critical) | 15 min | 30 min | Page on-call immediately, skip daily standup | VP Engineering + CEO notification after 10 min |
| P2 (High) | 30 min | 1 hour | Create incident thread, assign on-call, daily sync | VP Engineering after 20 min |
| P3 (Standard) | 2 hours | 4 hours | Create ticket, assign to team | Triage in next standup |

### P1 Incident Examples
- All consensus engine voters offline
- Queue executor all workers dead (unrecoverable)
- Database completely unavailable
- Data loss / corruption detected
- Unauthorized API access detected

### P2 Incident Examples
- Single consensus voter offline
- 30%+ of workers unhealthy
- Token burn rate > 2x SLA
- Consensus deadlock (ongoing >10 min)

### P3 Incident Examples
- Single workflow stuck
- Cache hit rate degraded but system stable
- Non-critical service delayed response

---

## 7. Team On-Call Procedures

### 7.1 On-Call Handoff (Weekly, Monday 08:00 UTC)

**Outgoing on-call:**
```bash
# 1. Review all open incidents in last 7 days
curl -s https://maestro-ops.internal/incidents?days=7 | jq '.incidents[] | {id, severity, created_at, closed_at, owner}'

# 2. Document context for incoming on-call
# 3. Run health check (see section 2.1)
# 4. Review changes deployed in last week
git log --oneline --since="7 days ago" maestro-ops.internal/deployments

# 5. Post handoff summary to #maestro-incidents
# Example: "No P1/P2 incidents. 1 P3 (workflow timeout) resolved. All systems nominal. 3 consensus escalations (normal). Token burn 18K/sec (normal)."
```

**Incoming on-call:**
```bash
# 1. Read handoff summary
# 2. Verify access to all dashboards and tooling
curl -s https://maestro-ops.internal/status  # Main dashboard
curl -s https://maestro-ops.internal/logs    # Log aggregator
curl -s https://maestro-ops.internal/alerts  # Alert manager

# 3. Set phone/Slack presence to "on-call"
# 4. Test escalation (send test page to verify alerting works)
# 5. Review SLA timers and escalation procedures
```

### 7.2 Incident Response Checklist

Upon P1 incident page:

```
[ ] Acknowledge page within 5 minutes
[ ] Join #maestro-incidents channel
[ ] Run "Status Check" script (section 2.1)
[ ] Identify affected service(s)
[ ] Check recent deployments/changes
[ ] Post initial status: "Investigating [issue]"
[ ] Get logs/metrics for past 30 min
[ ] Contact previous on-call if unclear
[ ] Start incident timer (45 min target resolution)
[ ] Update status every 5 min
[ ] At 30 min, escalate to VP Engineering if not resolved
[ ] Post RCA within 2 hours of resolution
```

### 7.3 Communication Template

```
@channel Incident Started: 2026-07-26T15:30:00Z
Severity: P1 (Consensus engine offline)
Affected: Workflows currently in consensus phase (est. 5 active)
Impact: ~50 users unable to start new workflows
Status: Investigating root cause
ETA: 15:55 UTC (investigating service logs)
Updates: Every 5 minutes
Contact: @oncall-ops
```

---

## 8. Log Analysis Recipes

### 8.1 Finding Consensus Deadlocks

```bash
# Extract all escalations in last 6 hours
kubectl logs -n maestro-consensus -l app=consensus-engine \
  --since=6h | grep "escalation" > consensus_escalations.log

# Parse escalation rate per minute
grep "escalation" consensus_escalations.log | \
  awk '{print substr($1, 1, 16)}' | \
  sort | uniq -c | sort -rn | \
  awk '{print $2, $1}'

# Expected: < 1 escalation per minute average
```

### 8.2 Finding Slow Agent Responses

```bash
# Extract agent latencies from logs
jq -r '.[] | select(.component=="agent_executor") | 
  "\(.timestamp) \(.agent_id) \(.latency_ms)"' maestro-logs.jsonl | \
  awk '$3 > 5000 {print $1, $2, $3 "ms"}' | \
  sort -k3 -rn | head -20

# Identifies agents with latency > 5 sec
```

### 8.3 Finding Token Spikes

```bash
# Extract token consumption by component per minute
jq -r '.[] | select(.component=="token_counter") | 
  "\(.timestamp) \(.component_name) \(.tokens_consumed)"' maestro-logs.jsonl | \
  awk -F'[ :.]' '{minute=$1":"$2":"$3; tokens[$4][minute]+=$5} 
    END {for (comp in tokens) for (m in tokens[comp]) 
      print m, comp, tokens[comp][m]}' | \
  sort -k3 -rn | head -30

# Shows tokens/minute by component, sorted descending
```

### 8.4 Finding Workflow Errors

```bash
# Extract all workflow errors with context
jq -r '.[] | select(.level=="error" and .component=="workflow") | 
  "\(.timestamp) \(.workflow_id) \(.error_message)"' maestro-logs.jsonl | \
  head -50

# Get error distribution
jq -r '.[] | select(.level=="error" and .component=="workflow") | 
  .error_message' maestro-logs.jsonl | \
  sort | uniq -c | sort -rn
```

### 8.5 Finding Queue Executor Stuck Tasks

```bash
# Extract all task state transitions
jq -r '.[] | select(.component=="queue_executor") | 
  "\(.timestamp) \(.task_id) \(.state_from) → \(.state_to)"' maestro-logs.jsonl | \
  grep -E "(queued|in_progress)" | \
  awk '{print $3}' | sort | uniq -c | sort -rn | \
  head -20

# Finds task IDs with many state transitions (possible loops)
```

### 8.6 Finding Rate Limit Violations

```bash
# Extract rate limit responses
jq -r '.[] | select(.http_status==429) | 
  "\(.timestamp) \(.api_name) remaining_requests=\(.rate_limit_remaining)"' maestro-logs.jsonl | \
  head -30

# Count by API
jq -r '.[] | select(.http_status==429) | .api_name' maestro-logs.jsonl | \
  sort | uniq -c | sort -rn
```

---

## 9. Rollback Procedures

### 9.1 Quick Rollback (< 5 minutes)

Use this if current deployment is causing P1 issues and fix is > 30 min away.

```bash
# 1. Identify last stable deployment
kubectl rollout history deployment/maestro-api -n maestro-system | head -5

# 2. Trigger rollback
kubectl rollout undo deployment/maestro-api -n maestro-system --to-revision=4

# 3. Wait for rollback to complete
kubectl rollout status deployment/maestro-api -n maestro-system

# 4. Verify service recovered
curl -s https://maestro-api.internal/health/status | jq '.status'

# 5. Post to incident channel
# "@channel Rolled back to revision 4. Services recovering. ETA 5 min for full recovery."

# 6. Drain backlog of queued requests
curl -X POST https://queue-executor.maestro-internal/control/drain \
  -d '{"drain_timeout_seconds": 120}'

# 7. Monitor metrics for 10 minutes to ensure stability
watch -n 10 'curl -s https://maestro-api.internal/health/status | jq ".status"'
```

### 9.2 Database Rollback (Careful!)

Use only if data corruption detected in latest deployment.

```bash
# 1. STOP all writes to database
kubectl scale deployment maestro-api --replicas=0 -n maestro-system

# 2. Check backup catalog
aws s3 ls s3://maestro-backups/hourly/ | tail -5

# 3. Restore from backup (choose appropriate recovery point)
aws s3 cp s3://maestro-backups/hourly/db-2026-07-26-1400.sql.gz - | gunzip | psql maestro_db

# 4. Verify data integrity
psql maestro_db -c "SELECT COUNT(*) FROM workflows; SELECT COUNT(*) FROM consensus_polls;"

# 5. Restart application
kubectl scale deployment maestro-api --replicas=3 -n maestro-system

# 6. Monitor for any stale data issues
curl -s https://maestro-api.internal/data/integrity-check | jq '.status'
```

### 9.3 Cache Flush (Data Mismatch)

If cache is stale and causing incorrect decisions:

```bash
# 1. Gracefully flush cache (drain subscribers)
curl -X POST https://cache.maestro-internal/flush \
  -d '{"mode": "graceful", "timeout_seconds": 60}'

# 2. Rebuild cache from source of truth (PostgreSQL)
curl -X POST https://cache.maestro-internal/rebuild \
  -d '{"async": true}'

# 3. Monitor cache rebuild progress
watch -n 5 'curl -s https://cache.maestro-internal/metrics | jq ".cache_entries, .rebuild_progress_percent"'

# 4. Once rebuild complete, resume normal operations
curl -s https://cache.maestro-internal/health | jq '.ready'
```

---

## 10. Maintenance Mode

For scheduled maintenance windows (Sunday 02:00–04:00 UTC).

```bash
# 1. Announce maintenance (1 day before)
# 2. Enable maintenance mode
curl -X POST https://maestro-api.internal/maintenance/enable \
  -d '{"duration_minutes": 120, "message": "Scheduled maintenance: DB migration"}'

# 3. Gracefully drain workflows
curl -X POST https://queue-executor.maestro-internal/control/drain \
  -d '{"cancel_unfinished": false}'

# 4. Perform maintenance (DB migration, config update, etc.)

# 5. Disable maintenance mode
curl -X POST https://maestro-api.internal/maintenance/disable

# 6. Verify all systems operational
# Run full health check (section 2.1)

# 7. Post completion to #maestro-incidents
```

---

## 11. Contact & Escalation

**Primary On-Call:** Check #maestro-incidents topic  
**SRE Lead:** sre-lead@maestro-ops.internal  
**VP Engineering:** vp-eng@maestro-ops.internal  
**Emergency Pager:** +1-XXX-MAESTRO-911 (internal)

**Incident Severity Hotline:**
- P1: Immediate (< 15 min response)
- P2: Urgent (< 30 min response)
- P3: Standard (next business day)

---

**Last Reviewed:** 2026-07-26  
**Next Review:** 2026-08-26  
**Owner:** SRE Team (Maestro Operations)
