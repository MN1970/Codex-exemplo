# Shadow Mode Operations Guide — Daily & Weekly

**Effective**: Jul 22, 2026  
**Duration**: 30-day window (Jul 22 – Aug 21)  
**Runbook for**: Platform engineers, on-call devops, data team

---

## 🌅 Daily Standup (UTC 08:00)

### 1. Check Latest Daily Stats (2 min)
```sql
-- Connect to Supabase prod
SELECT 
  date_bucket,
  total_queries,
  agent_match_rate,
  latency_delta_pct_avg,
  error_rate,
  go_ready
FROM cag_shadow_daily_stats
ORDER BY date_bucket DESC
LIMIT 3;
```

**What to look for**:
- `total_queries` > 10: healthy traffic
- `agent_match_rate` trending toward 0.85+
- `latency_delta_pct_avg` within ±10%
- `error_rate` < 0.001 (< 0.1%)
- `go_ready` = TRUE: metrics passing thresholds

### 2. Sample Recent Logs (3 min)
```sql
-- Last 20 queries
SELECT 
  session_id,
  timestamp,
  rag_agent,
  cag_selected_agents[1] as cag_primary_agent,
  agent_match,
  confidence_delta,
  latency_delta_ms,
  CASE 
    WHEN rag_response_text LIKE '%error%' THEN 'RAG_ERROR'
    WHEN cag_final_response LIKE '%error%' THEN 'CAG_ERROR'
    ELSE 'OK'
  END as status
FROM cag_shadow_logs
WHERE timestamp > NOW() - INTERVAL '6 hours'
ORDER BY timestamp DESC
LIMIT 20;
```

**What to look for**:
- No ERROR status rows (or < 1%)
- agent_match trending TRUE (primary agent aligned)
- confidence_delta small (RAG vs CAG aligned)
- latency_delta_ms reasonable (not 10x slower)

### 3. Check Alerts & Logs (2 min)
```bash
# Application logs
kubectl logs -f deployment/shadow-mode --tail=50 | grep -i error

# Supabase function logs (if available)
# Check error rates in Supabase dashboard
```

**What to look for**:
- No repeated "API rate limit" errors
- No "connection timeout" patterns
- No "invalid JSON" parsing errors

### 4. Escalate if Needed
| Metric | Threshold | Action |
|--------|-----------|--------|
| error_rate | > 0.01 (1%) | Page DevOps oncall immediately |
| agent_match_rate | < 0.75 | Schedule tuning session |
| latency_delta_pct | > 20% | Profile classifier performance |
| total_queries (6h) | 0 | Check RAG handler, maestro logs |

---

## 🔍 Deep Dive Investigation

### If Agent Match Rate Low (< 80%)

**Symptom**: `cag_shadow_logs` shows agent_match = FALSE for >20% of queries

**Root Cause Analysis**:
```sql
-- Which intents have low match?
SELECT 
  rag_agent,
  COUNT(*) as total,
  SUM(CASE WHEN agent_match THEN 1 ELSE 0 END) as matched,
  ROUND(SUM(CASE WHEN agent_match THEN 1 ELSE 0 END)::numeric / COUNT(*), 2) as match_rate
FROM cag_shadow_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY rag_agent
ORDER BY match_rate ASC;

-- Sample mismatches
SELECT session_id, query, rag_agent, cag_selected_agents, confidence_delta
FROM cag_shadow_logs
WHERE agent_match = FALSE
AND timestamp > NOW() - INTERVAL '6 hours'
LIMIT 10;
```

**Fix Options**:
1. **Keyword tuning** (fast): Add more keywords to intent classes in CLAUDE.md
2. **Confidence thresholds** (medium): Adjust keyword confidence base (currently 0.65)
3. **ML retraining** (slow): Fine-tune intent classifier with mismatches

### If Latency Degrading (> 15% slower)

**Symptom**: CAG taking 15-20% longer than RAG

**Profiling**:
```sql
-- Latency percentiles
SELECT 
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rag_latency_ms) as rag_p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY rag_latency_ms) as rag_p95,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cag_latency_ms) as cag_p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cag_latency_ms) as cag_p95,
  AVG(latency_delta_pct) as avg_delta_pct
FROM cag_shadow_logs
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

**Bottleneck Identification**:
- RAG p50 = 500ms, CAG p50 = 600ms (+20%) → Classifier overhead
- RAG p95 = 3000ms, CAG p95 = 3200ms (+6%) → Outliers, not average

**Solutions**:
1. **Classifier caching**: Cache embeddings for repeated queries
2. **Parallel execution**: Ensure N agents run in parallel (not sequential)
3. **Reduce token count**: Shorten prompts in response ranker

### If Error Rate Spike (> 0.5%)

**Symptom**: Errors in cag_final_response or rag_response_text

**Diagnosis**:
```sql
-- Error breakdown
SELECT 
  CASE 
    WHEN rag_response_text LIKE '%error%' THEN 'RAG_ERROR'
    WHEN cag_final_response LIKE '%error%' THEN 'CAG_ERROR'
    ELSE 'UNKNOWN'
  END as error_type,
  COUNT(*) as count,
  MAX(timestamp) as latest
FROM cag_shadow_logs
WHERE (rag_response_text LIKE '%error%' OR cag_final_response LIKE '%error%')
AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY error_type
ORDER BY count DESC;

-- Sample errors
SELECT session_id, timestamp, rag_response_text, cag_final_response
FROM cag_shadow_logs
WHERE cag_final_response LIKE '%error%'
AND timestamp > NOW() - INTERVAL '6 hours'
LIMIT 5;
```

**Common Issues**:
1. **Supabase rate limit**: Flush buffer slower (increase batch size)
2. **Claude API quota**: Check API usage in Anthropic dashboard
3. **Intent classifier timeout**: Increase timeout in config
4. **Network transient**: Usually resolves within 15 min

---

## 📈 Weekly Review (Friday 17:00 UTC)

### Prepare 7-Day Report

```sql
-- Weekly summary
SELECT 
  date_bucket,
  total_queries,
  queries_with_errors,
  ROUND(error_rate * 100, 2) as error_pct,
  ROUND(agent_match_rate * 100, 2) as match_pct,
  ROUND(rag_p50_ms) as rag_p50,
  ROUND(cag_p50_ms) as cag_p50,
  ROUND(latency_delta_pct_avg, 2) as latency_delta,
  go_ready
FROM cag_shadow_daily_stats
WHERE date_bucket >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date_bucket;
```

### Compile Metrics Table

| Date | Queries | Errors | Match % | Latency Δ | GO? |
|------|---------|--------|---------|-----------|-----|
| Jul 22 | 450 | 2 | 87% | +5% | ✅ |
| Jul 23 | 520 | 1 | 89% | +3% | ✅ |
| Jul 24 | 610 | 3 | 88% | +4% | ✅ |
| Jul 25 | 680 | 4 | 87% | +6% | ✅ |
| Jul 26 | 720 | 2 | 88% | +4% | ✅ |
| Jul 27 | 790 | 5 | 86% | +8% | ✅ |
| Jul 28 | 850 | 3 | 89% | +5% | ✅ |

### GO/NO-GO Assessment

**Passing Criteria** (all must be true):
- ✅ Agent match rate ≥ 85% (daily)
- ✅ Latency within 10% (on average)
- ✅ Error rate < 0.1%
- ✅ No cascading failures

**Recommendation**: ✅ **CONTINUE** to week 2

### Stakeholder Update

**Format**: Slack message to #maestro-cag + email to MN

```
📊 Shadow Mode Week 1 Summary (Jul 22–28)

✅ Metrics: All green
- Total queries: 4,620
- Agent match: 87.8% (threshold: 85%)
- Latency delta: +5.3% (threshold: ≤10%)
- Error rate: 0.06% (threshold: ≤0.1%)

📈 Trending: Stable
- Match rate stable 86-89%
- Latency improving (started +8%, now +4%)
- Errors trending down (4.4 → 2.8 per day avg)

🎯 Decision: CONTINUE to week 2
- No tuning needed
- Proceed as planned
- Next review: Aug 4

Questions? Slack @DevOps or ping MN.
```

---

## 🛠️ Configuration Adjustments

### If You Need to Adjust Thresholds

```sql
-- Example: Increase latency tolerance from 10% to 12%
UPDATE cag_shadow_config
SET value = '12.0'
WHERE key = 'latency_threshold_pct';

-- Verify change
SELECT key, value FROM cag_shadow_config 
WHERE key LIKE '%threshold%' OR key = 'latency_threshold_pct';
```

**When to adjust**:
- CAG consistently 11-12% slower → Raise to 15% (give more time for improvement)
- CAG consistently 6-8% slower → Lower to 8% (stricter target)
- Agent match at 83% consistently → Lower threshold to 80% temporarily

### Enabling Debug Logging

```sql
-- Temporarily enable verbose logs
UPDATE cag_shadow_config
SET value = 'true'
WHERE key = 'debug_logging';

-- Check logs
kubectl logs -f deployment/shadow-mode --tail=200

-- Disable when done
UPDATE cag_shadow_config
SET value = 'false'
WHERE key = 'debug_logging';
```

---

## 📋 Manual Tasks Checklist

### Every Morning (08:00 UTC)
- [ ] Review daily stats (1 min)
- [ ] Spot-check logs (2 min)
- [ ] Check alerts (1 min)
- [ ] Update status in Slack thread

### Every Friday (17:00 UTC)
- [ ] Generate 7-day report (10 min)
- [ ] Assess GO/NO-GO (5 min)
- [ ] Send stakeholder update (5 min)
- [ ] Escalate any blockers (if any)

### On Weekends (On-Call)
- [ ] Monitor error rate (alerting enabled)
- [ ] If error_rate > 1%: Page DevOps lead
- [ ] If queries = 0 for 1h: Page DevOps lead
- [ ] Do NOT make config changes (wait for Mon standup)

---

## 🚨 Critical Alerts

### Real-Time Monitoring (Recommended Setup)

```sql
-- Create alert for error spike (in your monitoring tool)
SELECT COUNT(*) 
FROM cag_shadow_logs 
WHERE timestamp > NOW() - INTERVAL '5 minutes'
AND (rag_response_text LIKE '%error%' OR cag_final_response LIKE '%error%')
HAVING COUNT(*) > 5;  -- Threshold: more than 5 errors in 5 min

-- Create alert for no traffic
SELECT COUNT(*) 
FROM cag_shadow_logs 
WHERE timestamp > NOW() - INTERVAL '30 minutes';
-- Threshold: 0 queries = alert
```

### Manual Checks (Fallback)

```bash
# Every 30 min during business hours
# From cron or manual run:

psql $SUPABASE_DB -c "
  SELECT COUNT(*) as recent_queries,
         SUM(CASE WHEN rag_response_text LIKE '%error%' OR cag_final_response LIKE '%error%' THEN 1 ELSE 0 END) as errors
  FROM cag_shadow_logs
  WHERE timestamp > NOW() - INTERVAL '30 minutes';
" | grep -q "recent_queries|0" && echo "ALERT: No queries in 30 min!"
```

---

## 📞 Escalation & Contacts

| Severity | Condition | Action | Owner |
|----------|-----------|--------|-------|
| P1 | Error rate > 2% | Page oncall NOW | DevOps |
| P1 | 0 queries for 1h | Page oncall NOW | DevOps |
| P2 | Agent match < 70% | Schedule urgent tuning | MN + ML team |
| P2 | Latency > 20% | Profile & investigate | Performance team |
| P3 | Config drift detected | Verify & align | Platform |

---

## 📚 Reference

- [Deployment Checklist](./DEPLOYMENT_CHECKLIST_JUL22.md) — Pre-launch tasks
- [Shadow Mode Architecture](./SHADOW_MODE_DEPLOYMENT.md) — Technical deep dive
- [Parallel Operations](./SHADOW_MODE_PARALLEL_OPERATIONS.md) — Batch processing & scaling
- [CLAUDE.md](../CLAUDE.md) — Agent registry & CAG specs

---

**Last Updated**: 2026-07-20  
**Document Owner**: Platform Engineering  
**Review Frequency**: Weekly (before Friday standup)
