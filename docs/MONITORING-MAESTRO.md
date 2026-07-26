# Maestro Monitoring & Observability

**Phase 1.4** — Runtime metrics, dashboards, and alerting for Maestro v4.2+

## Overview

This document covers the monitoring infrastructure for tracking Maestro (Manta 00) performance across all 20 agents and 9 segments.

### Metrics Captured

| Metric | Table | Frequency | Purpose |
|--------|-------|-----------|---------|
| Latency (p50/p95/p99) | maestro_runtime_metrics | Per request | Performance tracking |
| Token usage | maestro_runtime_metrics | Per request | Cost optimization |
| Model tier distribution | maestro_runtime_metrics | Per request | Tier strategy audit |
| Fallback rate | maestro_runtime_metrics | Per request | System health |
| Routing accuracy | maestro_routing_trace | Per routing decision | Quality gates |
| Ambiguous cases | maestro_routing_trace | Per routing decision | Improvement opportunities |
| User feedback | maestro_routing_trace | On approval | Learning signals |

---

## 1. Database Setup

### Apply Migrations

```bash
# Apply monitoring tables + views + functions
supabase db push --migration 2026_07_25_add_maestro_monitoring.sql

# Verify tables created
supabase db query "SELECT * FROM maestro_runtime_metrics LIMIT 1;"
```

### Schema Overview

**maestro_runtime_metrics** (per request):
- `timestamp, agent_slug, latency_ms, prompt_tokens, response_tokens`
- `model_tier, fallback_count, routing_confidence`
- Indexed on: `timestamp, agent_slug, model_tier, session_id`

**maestro_routing_trace** (per routing):
- `prompt, primary_agent, primary_score, alternate_agents`
- `is_ambiguous, score_gap, user_approved`
- Indexed on: `timestamp, primary_agent, is_ambiguous`

**maestro_metrics_daily** (aggregated):
- Materialized nightly via `compute_daily_metrics()`
- Enables fast dashboard queries without scanning millions of rows

**Views** (real-time):
- `maestro_metrics_current_hour` — last 60 minutes by agent
- `maestro_routing_quality` — 30-day routing accuracy + user feedback

---

## 2. Integration with Maestro Router

### Insert Metric After Dispatch

```python
# In manta-hub/maestro/router.py (pseudocode)

from supabase import create_client

def dispatch(prompt: str) -> Response:
    start_time = time.perf_counter()

    # ... routing logic ...
    agent, confidence = route_prompt(prompt)

    # ... execute agent ...
    response = agent.invoke(prompt)

    # Track metric
    latency_ms = (time.perf_counter() - start_time) * 1000
    insert_maestro_metric(
        agent_slug=agent.slug,
        prompt_tokens=count_tokens(prompt),
        response_tokens=count_tokens(response),
        latency_ms=latency_ms,
        model_tier=agent.tier,  # 'haiku', 'sonnet', 'opus'
        model_name=agent.model_id,
        routing_confidence=confidence,
        session_id=session_id,
        user_id=user_id,
    )

    return response
```

### Python Helper (supabase/metrics_client.py)

```python
from supabase import create_client

class MaestroMetricsClient:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)

    def insert_metric(
        self,
        agent_slug: str,
        prompt_tokens: int,
        response_tokens: int,
        latency_ms: float,
        model_tier: str,
        model_name: str,
        **kwargs
    ) -> str:
        """Insert a runtime metric. Returns metric ID."""
        response = self.supabase.rpc(
            'insert_maestro_metric',
            {
                'p_agent_slug': agent_slug,
                'p_prompt_tokens': prompt_tokens,
                'p_response_tokens': response_tokens,
                'p_latency_ms': latency_ms,
                'p_model_tier': model_tier,
                'p_model_name': model_name,
                **{f'p_{k}': v for k, v in kwargs.items()}
            }
        ).execute()
        return response.data[0]

    def insert_routing_trace(
        self,
        prompt: str,
        primary_agent: str,
        primary_score: float,
        alternate_agents: list = None,
        session_id: str = None,
    ) -> str:
        """Insert a routing trace. Returns trace ID."""
        import hashlib
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        response = self.supabase.table('maestro_routing_trace').insert({
            'prompt': prompt,
            'prompt_hash': prompt_hash,
            'primary_agent': primary_agent,
            'primary_score': primary_score,
            'alternate_agents': alternate_agents or [],
            'session_id': session_id,
        }).execute()
        return response.data[0]['id']
```

---

## 3. Dashboard Queries

### Current Status (Last Hour)

```sql
SELECT * FROM maestro_metrics_current_hour
ORDER BY request_count DESC;

-- Result:
-- agent_slug        | request_count | avg_latency | p95_latency | haiku_calls | sonnet_calls | opus_calls
-- agente-saneamento | 42            | 245ms       | 380ms       | 30          | 12           | 0
-- agente-energia    | 38            | 312ms       | 520ms       | 0           | 25           | 13
-- ...
```

### Routing Quality (Last 7 Days)

```sql
SELECT
  date,
  primary_agent,
  total_cases,
  ambiguous_cases,
  ROUND(100.0 * ambiguous_cases / total_cases, 2) as ambiguity_rate,
  ROUND(100.0 * approved_cases / total_cases, 2) as approval_rate,
  median_gap
FROM maestro_routing_quality
WHERE date >= CURRENT_DATE - interval '7 days'
ORDER BY date DESC, total_cases DESC;
```

### Token Efficiency (Daily)

```sql
SELECT
  date,
  agent_slug,
  total_requests,
  ROUND(total_tokens::numeric / total_requests, 0) as avg_tokens_per_request,
  haiku_count as cheap_tier,
  sonnet_count as mid_tier,
  opus_count as expensive_tier
FROM maestro_metrics_daily
WHERE date >= CURRENT_DATE - interval '30 days'
ORDER BY date DESC, total_tokens DESC;
```

### Latency SLO Tracking

```sql
SELECT
  date,
  agent_slug,
  total_requests,
  ROUND(latency_p50::numeric) as p50_ms,
  ROUND(latency_p95::numeric) as p95_ms,
  ROUND(latency_p99::numeric) as p99_ms,
  CASE
    WHEN latency_p95 < 300 THEN '✅ OK'
    WHEN latency_p95 < 500 THEN '⚠️  WARNING'
    ELSE '❌ SLA_BREACH'
  END as slo_status
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
ORDER BY latency_p99 DESC;
```

---

## 4. Alerts & Thresholds

### Alert Rules

```sql
-- Alert: High fallback rate
SELECT
  agent_slug,
  fallback_rate,
  COUNT(*) as fallback_cases
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
  AND fallback_rate > 0.05  -- > 5%
GROUP BY agent_slug, fallback_rate
ORDER BY fallback_rate DESC;

-- Alert: Latency SLA breach
SELECT
  agent_slug,
  latency_p95,
  latency_p99
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
  AND latency_p95 > 500;  -- > 500ms target

-- Alert: Routing ambiguity spike
SELECT
  date,
  primary_agent,
  ambiguous_cases,
  ROUND(100.0 * ambiguous_cases / total_cases, 2) as ambiguity_pct
FROM maestro_routing_quality
WHERE date = CURRENT_DATE - interval '1 day'
  AND ambiguous_cases > 10;
```

### Recommended Alert Configuration

| Alert | Threshold | Action |
|-------|-----------|--------|
| **Latency P95 > 500ms** | Per agent | Slack notification, investigate tier strategy |
| **Fallback Rate > 5%** | Per agent | Page on-call, check for routing issues |
| **Token Usage Spike** | Per day | Log for cost review, may trigger caching |
| **Ambiguous Cases > 10/day** | Per agent | Create GitHub issue for routing improvement |
| **Opus Usage > 30%** | Daily | Trigger cost review, evaluate Sonnet capability |

---

## 5. Scheduled Jobs

### Nightly Aggregation (11 PM UTC)

```sql
-- Run daily: SELECT compute_daily_metrics(CURRENT_DATE - interval '1 day');
-- Via Supabase Edge Function:

import { serve } from "https://deno.land/std@0.136.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL"),
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")
  );

  const result = await supabase.rpc("compute_daily_metrics", {
    p_date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  });

  return new Response(JSON.stringify(result), { status: 200 });
});
```

---

## 6. Cowork Dashboard Integration

### Custom Dashboard

```markdown
# Maestro Health Dashboard

## Current Hour Status

\`\`\`sql
SELECT * FROM maestro_metrics_current_hour LIMIT 5;
\`\`\`

## Routing Quality (Last 7D)

\`\`\`sql
SELECT date, primary_agent, total_cases, approved_cases,
       ROUND(100.0 * approved_cases / total_cases) as approval_rate
FROM maestro_routing_quality
WHERE date >= CURRENT_DATE - interval '7 days'
ORDER BY date DESC, approval_rate DESC;
\`\`\`

## SLA Status

\`\`\`sql
SELECT agent_slug, latency_p95, latency_p99,
       CASE WHEN latency_p95 < 300 THEN '✅' ELSE '❌' END as status
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
ORDER BY latency_p99 DESC;
\`\`\`
```

---

## 7. Deployment Checklist

- [ ] Apply migration: `2026_07_25_add_maestro_monitoring.sql`
- [ ] Create metrics client: `supabase/metrics_client.py`
- [ ] Integrate metrics calls in Maestro router
- [ ] Setup nightly cron job for `compute_daily_metrics()`
- [ ] Configure Slack alerts for thresholds
- [ ] Create Cowork custom connector for dashboards
- [ ] Test: Verify metrics inserted after first dispatch
- [ ] Baseline: Capture 7 days of data before alerting

---

## 8. Next Steps (Phase 2)

- **Feedback Loop**: Track user approvals → improve routing keywords
- **Cost Optimization**: Analyze token distribution → optimize tier strategy
- **Anomaly Detection**: ML-based detection of unusual patterns
- **Predictive Scaling**: Forecast traffic patterns → pre-warm resources

