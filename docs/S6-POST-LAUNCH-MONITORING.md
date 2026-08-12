# S6 Post-Launch Monitoring — Alerts, Metrics & Daily Reports
**Version: v5.0 | Agent: Manta 03-S6 (Portos) | Timeline: T+1h through T+30d**

Production monitoring framework with Grafana dashboards, Slack alerts, and daily report template.

---

## MONITORING WINDOWS

| Window | Duration | Check Interval | Owner | Escalation |
|--------|----------|---|-------|-----------|
| **Phase 1: Immediate** | T+0 to T+1h | Every 5 min | On-Call Eng | MN (if alert) |
| **Phase 2: Ramp-up** | T+1h to T+6h | Every 15 min | On-Call Eng | Tech Lead |
| **Phase 3: Stabilization** | T+6h to T+24h | Every 30 min | On-Call Eng | Tech Lead |
| **Phase 4: Observation** | T+24h to T+7d | Every 2h | DevOps | MN (daily report) |
| **Phase 5: Normal** | T+7d to T+30d | 2x daily (morning, evening) | DevOps | MN (weekly report) |

---

## GRAFANA DASHBOARD — S6 OVERVIEW

**URL:** `http://grafana.manta.local/d/s6-portos-overview`

### Panel 1: Routing Accuracy (Real-time)
```
Query: agent_runs WHERE agent_id = 'manta-03-s6' AND created_at > now()-15m
Metric: (count of correct route) / (total queries) × 100%
Target: >= 75%
Alert: RED if < 70% for 5 min
```

**Visual:** Bar chart, color-coded (green 75+%, yellow 60-75%, red <60%)

### Panel 2: Error Rate (Real-time)
```
Query: agent_runs WHERE status = 'error' AND created_at > now()-15m
Metric: error_count / total_count × 100%
Target: <= 1%
Alert: YELLOW if 1-5%, RED if > 5% for 10 min
```

**Visual:** Line chart with warning band

### Panel 3: Latency Percentiles (Real-time)
```
Query: PERCENTILE_CONT(0.50, 0.95, 0.99) OF latency_ms
      WHERE agent_id = 'manta-03-s6' AND created_at > now()-15m
Target: p50 < 5s, p95 < 8s, p99 < 12s
Alert: YELLOW if p95 > 10s, RED if > 15s for 5 min
```

**Visual:** Multi-series line chart (3 lines: p50, p95, p99)

### Panel 4: Model Tier Distribution (Last 1h)
```
Query: SELECT model_tier, COUNT(*) FROM agent_runs
       WHERE agent_id = 'manta-03-s6' AND created_at > now()-60m
       GROUP BY model_tier
Expected: Haiku 40%, Sonnet 50%, Opus 10%
```

**Visual:** Pie chart or stacked bar chart

### Panel 5: Cost Trend (Last 24h)
```
Query: SELECT DATE_TRUNC('hour', created_at) AS hour,
              SUM(cost_usd) FROM agent_runs
       WHERE agent_id = 'manta-03-s6'
       GROUP BY hour
Target: Trend stable, no sudden spikes > 2x baseline
```

**Visual:** Area chart with baseline band

### Panel 6: Feedback Score Distribution
```
Query: agent_feedback WHERE run_id IN (agent_runs for S6)
       COUNT() by score (0–5 stars)
Target: Avg score >= 3.5
Alert: YELLOW if avg < 3.0, RED if avg < 2.5
```

**Visual:** Histogram (score 0-5, count on Y-axis)

### Panel 7: System Health
```
Panels: Scheduler status (up/down), DB connectivity (ok/err),
        Elasticsearch status, Slack alert status
```

**Visual:** Status indicator (green=ok, red=problem)

---

## SLACK ALERTS CONFIGURATION

### Alert Channel: `#agent-ops`

#### Alert Rules (Prometheus/Grafana)

| Alert | Condition | Severity | Auto-Escalate | Message |
|-------|-----------|----------|---|---------|
| **Routing Accuracy Low** | < 70% for 5 min | 🔴 CRITICAL | MN at 10 min | "S6 routing accuracy: 58%. Possible keyword rule issue. Investigation started." |
| **Error Rate High** | > 5% for 10 min | 🔴 CRITICAL | MN at 5 min | "S6 error rate: 8%. Check error_message distribution. Fallback active?" |
| **Latency Spike** | p95 > 15s for 5 min | 🟡 HIGH | Tech Lead | "S6 latency spike: p95 = 18s. Reranker slow? Check Elasticsearch." |
| **Cost Anomaly** | > 3x baseline/run | 🟡 HIGH | MN (async) | "S6 average cost: $1.20/run (baseline $0.30). Over-tiering detected?" |
| **Scheduler Down** | Status != running | 🔴 CRITICAL | MN at 2 min | "manta-scheduler down. System background tasks paused." |
| **DB Connection Fail** | Heartbeat timeout | 🔴 CRITICAL | DBA + MN | "Supabase connection timeout. Can't write agent_runs. CRITICAL." |
| **RAG Collection Empty** | Count < 100 | 🔴 CRITICAL | DBA at 1 min | "RAG collection por:v5.0:chunks count dropped to 0. Data loss?" |
| **Feedback Score Low** | Avg < 2.5 | 🟡 HIGH | Tech Lead | "S6 feedback score: 2.1. Users unhappy. Quality issue?" |

#### Slack Webhook Integration

```bash
# Create Slack webhook URL in Slack workspace
# Manta Workspace > Apps > Incoming Webhooks > Add New

# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "✅ Slack webhook test — S6 monitoring active",
    "blocks": [{
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*S6 Post-Launch Monitoring*\nWebhook: ✓ Online"}
    }]
  }'

# Export webhook URL as env var
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
```

#### Custom Alert Message Templates

**Low Routing Accuracy:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "🚨 S6 Routing Accuracy Alert"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Metric:*\nRouting Accuracy"},
        {"type": "mrkdwn", "text": "*Current:*\n68% (target: 75%)"},
        {"type": "mrkdwn", "text": "*Duration:*\n5 minutes"},
        {"type": "mrkdwn", "text": "*Status:*\n🔴 CRITICAL"}
      ]
    },
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*Possible Causes:*\n• Keyword rules incomplete\n• Embedding model outdated\n• BM25 index stale"}
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "View Dashboard"}, "url": "http://grafana.manta.local/d/s6-portos-overview"},
        {"type": "button", "text": {"type": "plain_text", "text": "Run Diagnostics"}, "url": "..."},
        {"type": "button", "text": {"type": "plain_text", "text": "Start Rollback"}, "url": "..."}
      ]
    },
    {
      "type": "context",
      "elements": [{"type": "mrkdwn", "text": "_Alert triggered at 2026-07-25T14:30:00Z by Grafana_"}
    ]
  ]
}
```

**High Error Rate:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "🚨 S6 Error Rate Alert"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Error Rate:*\n8.2% (target: <1%)"},
        {"type": "mrkdwn", "text": "*Failed Runs:*\n45 out of 550"},
        {"type": "mrkdwn", "text": "*Top Error:*\n'timeout' (28 runs)"}
      ]
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "View Error Logs"}, "url": "..."},
        {"type": "button", "text": {"type": "plain_text", "text": "Increase Timeout"}, "url": "..."}
      ]
    }
  ]
}
```

---

## DAILY REPORT TEMPLATE (T+1d, T+8d, T+15d, T+30d)

**Created:** Every day at 09:00 UTC (morning meeting)  
**Posted to:** Slack #agent-ops and email @mantaassociados.com

### Template

```markdown
# S6 Daily Report — [DATE]

**Report Period:** [START_TIME] to [END_TIME] (24h)
**Status:** ✅ HEALTHY / 🟡 WATCH / 🔴 INCIDENT

---

## Executive Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Routing Accuracy | 87.3% | >= 75% | ✅ |
| Error Rate | 0.8% | < 1% | ✅ |
| Latency (p95) | 4.2s | < 8s | ✅ |
| Avg Feedback | 4.1/5 | >= 3.5 | ✅ |
| Cost/Run | $0.32 | < $0.50 | ✅ |
| Uptime | 99.8% | > 99.5% | ✅ |

---

## Detailed Metrics (24h window)

### Traffic & Volume
- **Total Runs:** 1,247
- **Successful Runs:** 1,237 (99.2%)
- **Failed Runs:** 10 (0.8%)
  - Timeout: 6 (60%)
  - Error: 3 (30%)
  - Other: 1 (10%)

### Routing Performance
- **Routing Accuracy:** 87.3% (1,087 correct, 160 misrouted)
  - Correct → S6: 1,087
  - Misrouted to S1: 85
  - Misrouted to other: 75
- **Confidence Score Distribution:**
  - High (>0.9): 921 runs (74%)
  - Medium (0.7-0.9): 267 runs (21%)
  - Low (<0.7): 59 runs (5%)

### Latency Analysis
- **p50:** 2.1s (target: <5s) ✅
- **p95:** 4.2s (target: <8s) ✅
- **p99:** 7.8s (target: <12s) ✅
- **Max:** 18.3s (1 outlier, S3 file processing)

### Model Tiering Distribution
| Model | Count | % | Avg Cost | Total Cost |
|-------|-------|---|----------|-----------|
| Haiku | 487 | 39% | $0.15 | $73 |
| Sonnet | 636 | 51% | $0.42 | $267 |
| Opus | 124 | 10% | $1.20 | $149 |
| **TOTAL** | **1,247** | **100%** | **$0.32** | **$489** |

### Cost Analysis
- **Daily Cost:** $489 (24-hour period)
- **Projected Monthly:** $14,670 (at current rate)
- **Cost Trend:** Stable (no anomalies)
- **Cost per correct route:** $0.45 (vs $0.32 avg = 40% for misroutes)

### Feedback & Quality
- **Total Feedback Submitted:** 287 (23% response rate)
- **Average Score:** 4.1/5 stars ✅
- **Score Distribution:**
  - 5 stars: 172 (60%)
  - 4 stars: 82 (28%)
  - 3 stars: 24 (8%)
  - 2 stars: 6 (2%)
  - 1 star: 3 (1%)

- **Top Feedback Themes:**
  - Positive: "Accurate results" (89 mentions), "Fast response" (67), "Relevant sources" (45)
  - Negative: "Missing context" (4), "Wrong format" (2), "Slow" (1)

### Incidents & Issues
| Time | Severity | Issue | Duration | Resolution |
|------|----------|-------|----------|-----------|
| 14:30 | 🟡 | Latency spike (p95 8.9s) | 15 min | Reranker temporarily disabled |
| 22:15 | 🟡 | Routing accuracy drop (71%) | 20 min | Keyword rule adjusted |
| — | — | No 🔴 CRITICAL incidents | — | — |

---

## RAG Collection Health

| Collection | Chunks | Embeddings | Avg Score | Status |
|------------|--------|-----------|-----------|--------|
| por:v5.0:chunks | 2,147 | 2,147 (100%) | 0.82 | ✅ |
| (1 week old) | — | — | — | Good quality |

- **Ingestion Status:** No new ingestions today
- **Cache Hit Rate:** 34% (333 of 1,000 queries from rag_cache)
- **Embedding Freshness:** < 7 days old ✅

---

## System Health

| Component | Status | Uptime | Notes |
|-----------|--------|--------|-------|
| manta-scheduler | ✅ Running | 100% | All 3 jobs executed |
| Supabase DB | ✅ Connected | 99.9% | 1 brief connection hiccup at 11:22 UTC |
| Elasticsearch (BM25) | ✅ Running | 100% | Healthy, disk 62% |
| Embedding Service | ✅ Running | 99.8% | 1 brief restart at 03:15 UTC |
| Grafana Dashboard | ✅ Online | 100% | All panels rendering |
| Slack Integration | ✅ Connected | 100% | Webhooks functional |

---

## Comparison to Baseline (Pre-S6 v4.9)

| Metric | S6 v5.0 | v4.9 Baseline | Delta | Status |
|--------|---------|---------------|-------|--------|
| Routing Accuracy | 87.3% | 82% | +5.3% | ✅ Better |
| Latency (p95) | 4.2s | 3.8s | +0.4s | ⚠️ Slight increase |
| Error Rate | 0.8% | 0.5% | +0.3% | ⚠️ Slight increase |
| Feedback Score | 4.1/5 | 3.9/5 | +0.2 | ✅ Better |
| Cost/Run | $0.32 | $0.20 | +60% | ⚠️ Expected (Sonnet vs Haiku) |

---

## Recommendations & Actions

### Immediate (Today)
- [ ] Monitor latency after reranker re-enable (scheduled for 16:00 UTC)
- [ ] Review 6 low-rated feedback (2-star and below)
- [ ] Confirm keyword rule fix for S1 misroutes effective

### Short-term (Next 3 days)
- [ ] Analyze why cost is 60% higher than v4.9
  - **Possible cause:** Tiering weights favor Sonnet too much?
  - **Action:** Review complexity score (R7) formula, consider Haiku threshold adjustment
- [ ] Investigate latency p99 spike (7.8s → 18.3s at one point)
  - **Action:** Check if large file processing (S3) was involved

### Medium-term (Next week)
- [ ] Collect 7 days of feedback to train embedding reranker (R9 feedback loop)
- [ ] Run A/B test: Current tiering vs adjusted tiering (reduce Opus, increase Haiku)
- [ ] Performance tune RAG queries if cache hit rate drops below 30%

---

## Team Notes

**MN Comment:** [To be filled during review call]

**Tech Lead Notes:** [To be filled]

**On-Call Engineer Notes:** [To be filled]

---

## Sign-Off

**Report Generated by:** Automated reporting system  
**Report Date:** 2026-07-26T09:00:00Z  
**Reviewed by:** _____________________ (Tech Lead)  
**Approved by:** _____________________ (MN)  

**Next Report Due:** 2026-07-27T09:00:00Z

---

**End of Daily Report**
```

---

## WEEKLY SUMMARY (T+7d)

**Posted:** Every Friday to #agent-ops + email

```markdown
# S6 Weekly Summary — Week 1 (2026-07-25 to 2026-07-31)

**Status:** ✅ HEALTHY

### Key Metrics (7 days)
- **Total Runs:** 8,647
- **Routing Accuracy:** 86.2% (avg)
- **Avg Latency (p95):** 4.5s
- **Avg Error Rate:** 0.9%
- **Avg Feedback:** 4.0/5
- **Total Cost:** $3,456 (avg $494/day)

### Incidents This Week
- None 🔴 CRITICAL
- 2 🟡 HIGH (latency spike Wed, routing dip Thu) — both resolved < 30min

### Recommendations for Week 2
1. Continue monitoring cost trend (currently 60% above v4.9)
2. Schedule embedding retrain (R9) after 7d feedback collection
3. Plan canary test: 10% queries to experimental tiering weights

---
```

---

## MONITORING CHECKLIST (Daily)

**Every morning at 09:00 UTC:**

```bash
# 1. Check Grafana dashboard
curl -s http://grafana.manta.local/api/health | jq .
# Expected: {"database":"ok","status":"ok"}

# 2. Verify metrics from DB
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT 
  COUNT(*) as total_runs,
  COUNT(CASE WHEN status = 'success' THEN 1 END) as success,
  ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / COUNT(*), 2) as success_rate,
  ROUND(AVG(cost_usd), 4) as avg_cost,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency
FROM agent_runs
WHERE agent_id = 'manta-03-s6' AND created_at > NOW() - INTERVAL '24 hours';
SQL

# 3. Check feedback
psql -h $SUPABASE_HOST -U postgres << 'SQL'
SELECT 
  ROUND(AVG(score), 2) as avg_score,
  COUNT(*) as feedback_count
FROM agent_feedback
WHERE run_id IN (SELECT run_id FROM agent_runs WHERE agent_id = 'manta-03-s6' AND created_at > NOW() - INTERVAL '24 hours');
SQL

# 4. Check for errors in logs
grep "ERROR\|CRITICAL" logs/*.log | tail -20

# 5. Verify scheduler is running
systemctl status manta-scheduler | grep -i active

# 6. Generate daily report (auto or manual)
python3 scripts/generate_daily_report.py --agent s6 --format markdown > reports/s6_report_$(date +%Y-%m-%d).md

# 7. Post to Slack
curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' \
  -d "$(cat reports/s6_report_$(date +%Y-%m-%d).md | jq -R -s -c '{text:.}')"
```

---

## COST TRACKING

### Cost Model

```
Total Cost = Σ (input_tokens × $input_rate + output_tokens × $output_rate) per run

Model Rates (as of 2026-07-25):
- Haiku:  $0.80 per 1M input, $2.40 per 1M output
- Sonnet: $3.00 per 1M input, $15.00 per 1M output
- Opus:   $15.00 per 1M input, $75.00 per 1M output

Example:
  Input: 1,500 tokens × ($3.00 / 1M) = $0.0045
  Output: 500 tokens × ($15.00 / 1M) = $0.0075
  Total per run: $0.012 (Sonnet 2K input)
```

### Cost Alerts

```
Daily threshold: > $600 → YELLOW alert (22% over baseline $489)
Daily threshold: > $800 → RED alert (63% over baseline)

Weekly average > $550/day → Escalate to MN, review tiering
```

---

## GO/NO-GO DECISION GATES

### T+24h Gate (Daily Report)
**Decision:** Continue in production or rollback?

**Go if:** All metrics within 10% of target (routing >= 68%, error <= 2%, latency p95 < 10s)  
**No-Go if:** Any metric fails 2 consecutive hours

### T+7d Gate (Weekly Report)
**Decision:** Keep S6 in prod, continue optimization, or promote to GA?

**Metrics for GA promotion:**
- Routing accuracy > 85% for 7 days ✅
- Feedback score > 3.8 for 7 days ✅
- No 🔴 CRITICAL incidents ✅
- Cost stable or downward trend ✅

---

## SIGN-OFF

**Monitoring Plan Prepared by:** Claude AI (Codex-exemplo Agent)  
**Date:** 2026-07-25  
**Approved by:** _____________________ (Tech Lead)  
**Approved by:** _____________________ (MN)

---

**End of Post-Launch Monitoring Guide**
