# MAESTRO OS v6.0 — Team Training & Certification

**Version:** 6.0.0  
**Target Audience:** SRE, DevOps, Platform Engineers  
**Duration:** 8 hours (recommended spread over 2 days)  
**Certification:** 12-topic competency checklist  
**Last Updated:** 2026-07-26

---

## Part 1: Architecture Overview

### 1.1 5-Layer Maestro Architecture (for Operations)

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: WORKFLOW ORCHESTRATION                                 │
│ (Stateful workflow engine, SLA timers, state machines)          │
│ Entry point for all multi-step tasks                            │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ Layer 4: CONSENSUS VOTING ENGINE                                │
│ (5-node voting pool, agreement detection, escalation handler)   │
│ Ensures agreement before committing multi-agent decisions       │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ Layer 3: AGENT EXECUTION & ORCHESTRATION                        │
│ (20 agents S1-S11, model versioning, response caching)          │
│ Routes tasks to appropriate agent, manages response aggregation │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ Layer 2: QUEUE EXECUTOR (Worker Pool)                           │
│ (10 workers, task scheduling, backoff queue, rate limiting)     │
│ Manages task queue, worker assignment, exponential backoff      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ Layer 1: ML INFERENCE PIPELINE                                  │
│ (Model cache, embedding server, token counter, batch processor) │
│ Low-level inference, embeddings, token accounting               │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow (Example: Workflow Creation):**
1. User submits workflow → Layer 5 accepts and creates state machine
2. Workflow needs decision → Layer 5 calls Layer 4 (consensus)
3. Consensus queries agents (Layer 3) in parallel
4. Layer 3 queues tasks → Layer 2 assigns to workers
5. Workers invoke models → Layer 1 does inference, returns embeddings/tokens
6. Responses flow back up: Layer 1 → Layer 2 → Layer 3 → Layer 4
7. Consensus aggregates, Layer 5 applies decision to workflow

### 1.2 Key Components

| Component | Layer | Role | Health Check |
|-----------|-------|------|--------------|
| **Detector** | 4 | Watches voting patterns, detects deadlock | `GET /consensus/status` |
| **Consensus Voting Pool** | 4 | 5 voters aggregate outputs | `GET /consensus/quorum` |
| **Agent Router** | 3 | Routes tasks to S1-S11 agents | `GET /agents/status` |
| **Queue Executor** | 2 | 10 workers, task scheduling | `GET /queue-executor/workers` |
| **ML Inference Engine** | 1 | Models, embeddings, batching | `GET /ml-inference/models` |
| **Vector DB (pgvector)** | 1 | Embedding storage & retrieval | `GET /vectordb/health` |
| **Cache (Redis)** | 2–3 | Consensus results, agent responses | `GET /cache.maestro/info` |

### 1.3 Data Flow: "Happy Path" (Workflow → Decision)

```
Time | Component | Action
-----|-----------|-------
t0   | User      | POST /workflows → {type: "procurement_analysis", context: {...}}
t1   | Layer 5   | Create workflow WF_001, state=initial, enqueue task
t2   | Layer 2   | Assign task to Worker #3
t3   | Layer 3   | Agent Router calls S5 (imobiliario), S1 (rodovia) agents in parallel
t4   | Layer 4   | Consensus enqueues 5 voting tasks: Agent_1, Agent_2, Agent_3, Agent_4, Agent_5
t5   | Layer 2   | Queue executor assigns votes to workers #4-#8
t6   | Layer 1   | Each worker invokes model inference, generates response vector
t7   | Layer 4   | Consensus Detector sees 4/5 votes match → 80% agreement
t8   | Layer 4   | Agreement > 75% threshold → COMMIT decision
t9   | Layer 5   | Update WF_001 state=completed, store result
t10  | User      | GET /workflows/WF_001 → {status: "completed", result: {...}}
```

**Timeline:** t0 → t10 = ~2–5 seconds (SLA target)

---

## Part 2: Key Concepts for Operations

### 2.1 Consensus Voting Explained

**What it is:** Multiple agents vote on the same question; decision requires agreement.

**Why:** Reduces hallucination risk, increases confidence in multi-agent decisions.

**Process:**

```
POLL CREATED: "Should we approve procurement for supplier X?"

VOTER 1 (Agent S5): "Yes, price 15% below market, quality excellent"
         confidence: 0.92

VOTER 2 (Agent S1): "Yes, references check out, delivery SLA acceptable"
         confidence: 0.88

VOTER 3 (Agent S2): "No, logistics risk to Rio variant"
         confidence: 0.61

VOTER 4 (Agent S3): "Yes, terms within standard parameters"
         confidence: 0.95

VOTER 5 (Agent S4): "Yes, matches procurement policy"
         confidence: 0.85

AGGREGATION:
  Yes votes: 4/5 (80%)
  Confidence average: 0.84
  → AGREEMENT REACHED (threshold: 3/5 = 60%)
  → Decision: COMMIT "Yes"
```

**Confidence Scores:** 0.0–1.0 scale
- 0.9+: High confidence (agent has strong evidence)
- 0.7–0.9: Moderate confidence (agent reasonably sure)
- 0.5–0.7: Low confidence (agent has doubts)
- <0.5: Very low confidence (should trigger escalation)

**Escalation:** If agreement < 60% OR timeout after 15 min → weighted voting by confidence.

### 2.2 Token Budget Tracking

Every agent response consumes tokens from shared budget.

**Monthly Budget:** 100M tokens (example; varies by contract)

**Allocation:**
```
Total Budget: 100M tokens/month (2026-08)

Consumption by layer (target):
  Layer 1 (inference): 35M tokens (context embeddings, LLM calls)
  Layer 3 (agents):    40M tokens (multi-turn conversations, reasoning)
  Layer 4 (consensus): 20M tokens (voting context, agreement polling)
  Buffer (unused):      5M tokens

Daily budget: 100M / 30 days = 3.33M tokens/day
Hourly budget: 3.33M / 24 = 139K tokens/hour (alert if > 200K/hour)
```

**Burn Rate Monitoring:**

```bash
# Check current day consumption
curl -s https://maestro-api.internal/tokens/status | jq '{
  burn_rate_tokens_per_sec,
  consumed_today,
  daily_budget,
  percent_used: (.consumed_today / .daily_budget * 100)
}'

# Output:
# {
#   "burn_rate_tokens_per_sec": 18500,
#   "consumed_today": 1500000,
#   "daily_budget": 3330000,
#   "percent_used": 45
# }
```

**Optimization Strategies:**
1. **Batch queries:** Combine 5 small requests → 1 batch request (save 60% tokens)
2. **Context summarization:** Reduce context window for retries (save 30% tokens)
3. **Cache hits:** Reuse previous consensus decisions (save 100% tokens if cached)
4. **Early termination:** Stop voting early if unanimous (save 40% tokens)

### 2.3 Rate Limiting & Backoff Strategy

External APIs have rate limits (e.g., Anthropic API: 10,000 req/min).

**Backoff Strategy (Exponential):**

```
Attempt 1: Immediate
Attempt 2: Wait 5 seconds (if rate limited)
Attempt 3: Wait 25 seconds (5 * 5)
Attempt 4: Wait 125 seconds (25 * 5)
Attempt 5: Wait 625 seconds (2 min)
Max backoff: 300 seconds (5 min)
```

**Queue Executor Behavior:**

```
REQUEST: POST /api/agent/query
↓
HTTP 429 (Rate Limited)
↓
Enqueue to BACKOFF_QUEUE
  task_id: task_xyz
  retry_at: now() + 5 sec
  attempt: 2
  backoff_multiplier: 5
↓
[Wait 5 seconds]
↓
RETRY: POST /api/agent/query (attempt 2)
↓
If success: Remove from backoff queue, mark complete
If 429 again: Re-enqueue with new backoff (25 sec this time)
```

**Monitoring Backoff Queue:**

```bash
# Check how many tasks are in exponential backoff
curl -s https://queue-executor.maestro-internal/backoff-queue | jq '{
  queued_tasks,
  oldest_retry_timestamp,
  avg_retry_delay_seconds
}'

# If queued_tasks > 500 for > 10 min: investigate rate limit issue
```

---

## Part 3: Dashboard Interpretation

### 3.1 Main Status Dashboard (maestro-ops.internal/status)

```
┌─ Maestro OS Status ────────────────────────────────────────────┐
│                                                                  │
│ System Health:     🟢 OPERATIONAL                               │
│ Uptime:            99.97% (last 30 days)                        │
│ Incidents (24h):   1 P3 (resolved), 0 P1/P2                     │
│                                                                  │
├─ Core Services ───────────────────────────────────────────────┤
│ API Gateway:       🟢 Healthy (latency: 45ms p99)               │
│ Consensus Engine:  🟢 Healthy (agreement: 86%)                 │
│ Agent Router:      🟢 Healthy (20 agents active)                │
│ Queue Executor:    🟢 Healthy (queue depth: 234)                │
│ ML Inference:      🟢 Healthy (p99 latency: 380ms)              │
│                                                                  │
├─ Resource Utilization ───────────────────────────────────────┤
│ Token Burn:        18.5K tokens/sec (target: <50K)              │
│ Daily Budget:      1.5M / 3.33M (45% used, good)                │
│ Worker Pool:       8/10 busy (80% utilized)                     │
│ Database Conn:     12/25 (48% util)                             │
│ Cache Hit Rate:    78% (consensus cache)                        │
│                                                                  │
├─ Workflow Metrics (Last Hour) ────────────────────────────────┤
│ Created:           234                                           │
│ Completed:         227 (97% success rate)                       │
│ Failed:            5 (2% failure rate)                           │
│ Stuck:             2 (in consensus >15min)                       │
│ Avg Duration:      3.2 sec (SLA: <5 sec)                        │
│                                                                  │
├─ Alerts ─────────────────────────────────────────────────────┤
│ 🟡 WARNING: Cache miss rate 22% (expect <20%)                   │
│ 🟢 OK: Token burn rate nominal                                  │
│ 🟢 OK: All workers healthy                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**How to Read:**
- 🟢 Green = Normal, no action needed
- 🟡 Yellow = Degraded but functioning, monitor closely
- 🔴 Red = Critical issue, page on-call immediately

### 3.2 Consensus Engine Dashboard

**Key Metrics:**
- **Agreement Rate:** % of polls reaching consensus (target: >85%)
- **Escalation Rate:** % of polls escalated to weighted voting (target: <5%)
- **Voter Divergence:** How much agents disagree (target: low)
- **Poll Duration:** Time to consensus (target: <2 sec)

**Interpretation:**

| Agreement | Escalation | Voter Divergence | Status | Action |
|-----------|-----------|-----------------|--------|--------|
| >85% | <5% | Low | Healthy | None |
| 70–85% | 5–10% | Medium | Caution | Monitor next hour |
| 50–70% | 10–20% | High | Degraded | Investigate voter divergence |
| <50% | >20% | Very High | Critical | Escalate to P1 |

### 3.3 Token Budget Dashboard

```
Monthly Budget: 100M tokens (2026-08)
Daily Average:   3.33M tokens
Current Date:    2026-07-26 (15:30 UTC)
Days Remaining:  5 days

Consumption Graph (tokens/hour):
  Hour 00–04: [████░░░░░░░░░░░░░░] 150K (within range)
  Hour 04–08: [███████░░░░░░░░░░░░] 210K (approaching limit)
  Hour 08–12: [██████░░░░░░░░░░░░░] 180K (OK)
  Hour 12–16: [████░░░░░░░░░░░░░░░] 140K (OK)

Current rate: 18.5K tokens/sec
Trend: Stable (no spike detected)
Forecast: On track to use 3.1M today (92% of budget)

Optimization Opportunities:
  - Cache hit rate 78% (could improve to 85%)
  - Context summarization enabled for 40% of retries
  - Batch size: 8 (could increase to 12)
```

---

## Part 4: Debugging Multi-Agent Execution

### 4.1 "Why Did My Workflow Fail?" Diagnostic Tree

```
WORKFLOW FAILED
│
├─ Check consensus status
│  ├─ Consensus reached? 
│  │  ├─ Yes → Check agent votes (see 4.2)
│  │  └─ No → Check for deadlock (see 4.3)
│  └─ Poll duration > 15 min?
│     ├─ Yes → Escalated → Check escalation result
│     └─ No → Timeout occurred → See 4.4
│
├─ Check queue executor
│  ├─ Task in backoff queue? → Check retry logic (5–10 sec backoff)
│  ├─ Worker crash? → Check worker logs for panic
│  └─ Rate limit? → Check HTTP 429 responses
│
├─ Check individual agent
│  ├─ Agent response missing? → Check agent logs
│  ├─ Agent confidence < 0.5? → Check agent uncertainty
│  └─ Agent hallucinating? → Check RAG retrieval
│
└─ Check data integrity
   ├─ Input context corrupted? → Compare input_hash
   ├─ Stale cache hit? → Validate cache timestamp
   └─ Database transaction failed? → Check DB logs
```

### 4.2 Reading Agent Confidence Scores

**High Confidence (0.85–1.0):**
```
Agent S5 recommends: "Approve procurement"
Confidence: 0.94
Reasoning: "Supplier comparison complete (3 vendors evaluated), 
price 18% below market, financial stability verified, 
delivery terms standard, past performance excellent."
```
→ Trust this recommendation; low chance of hallucination.

**Medium Confidence (0.65–0.85):**
```
Agent S1 recommends: "Request additional geological survey"
Confidence: 0.72
Reasoning: "Standard practice for this soil type (clay, 5m depth), 
but recent survey available from 2 km away (extrapolation 
uncertainty ±15%)."
```
→ Recommendation likely valid but less certain; consider additional validation.

**Low Confidence (<0.65):**
```
Agent S3 recommends: "Delay project timeline"
Confidence: 0.48
Reasoning: "Historical data for similar rail gauge limited in database 
(only 2 precedents), contractor experience with new signaling system uncertain."
```
→ High uncertainty; likely to trigger escalation; may recommend human review.

### 4.3 Detecting Consensus Deadlock

**Symptoms:**
- Workflow stuck in "consensus_pending" state > 15 min
- Agreement rate < 50%
- Escalation unresolved > 20 min

**Debugging:**

```bash
# Step 1: Get workflow and find stuck consensus poll
curl -s https://maestro-api.internal/workflows/WF_001 | jq '.current_state, .consensus_poll_id'

# Output: state="consensus_pending", poll_id="poll_abc123"

# Step 2: Inspect consensus poll details
curl -s https://maestro-api.internal/consensus/polls/poll_abc123 | jq '.votes[] | {voter, decision, confidence}'

# Output:
# { "voter": "Agent_S1", "decision": "yes", "confidence": 0.92 }
# { "voter": "Agent_S2", "decision": "yes", "confidence": 0.88 }
# { "voter": "Agent_S3", "decision": "no", "confidence": 0.61 }  ← Outlier!
# { "voter": "Agent_S4", "decision": "yes", "confidence": 0.95 }
# { "voter": "Agent_S5", "decision": "yes", "confidence": 0.85 }

# Step 3: Check Agent_S3 reasoning
curl -s https://maestro-api.internal/consensus/polls/poll_abc123/voter-logs/Agent_S3 | jq '.'

# Step 4: Decide: COMMIT (ignore S3, proceed) or ROLLBACK (rerun with clarified context)

curl -X POST https://maestro-api.internal/consensus/polls/poll_abc123/escalate \
  -d '{"decision": "commit", "reason": "4/5 agreement sufficient, S3 outlier likely data gap"}'
```

### 4.4 Timeout Diagnosis

**If workflow timeout (>5 sec SLA):**

```bash
# Get workflow timeline
curl -s https://maestro-api.internal/workflows/WF_001/timeline | jq '.phases[] | {phase, start_at, end_at, duration_ms}'

# Output:
# { "phase": "init", "start_at": "2026-07-26T15:30:00Z", "end_at": "2026-07-26T15:30:00.1Z", "duration_ms": 100 }
# { "phase": "consensus_voting", "start_at": "2026-07-26T15:30:00.1Z", "end_at": "2026-07-26T15:30:03.5Z", "duration_ms": 3400 }  ← 3.4 sec (OK)
# { "phase": "agent_exec", "start_at": "2026-07-26T15:30:03.5Z", "end_at": "2026-07-26T15:30:08.2Z", "duration_ms": 4700 }  ← 4.7 sec (OK)
# { "phase": "queue_exec", "start_at": "2026-07-26T15:30:08.2Z", "end_at": "2026-07-26T15:30:13.8Z", "duration_ms": 5600 }  ← 5.6 sec (SLOW!)

# → Queue executor is slow (5.6 sec). Check queue depth.
curl -s https://queue-executor.maestro-internal/metrics | jq '.queue_depth'
# Output: 2340 (high backlog!)

# Solution: Increase workers or wait for queue to drain
curl -X PATCH https://queue-executor.maestro-internal/control \
  -d '{"worker_count": 15}'  # Increase from 10 to 15
```

---

## Part 5: Consensus Escalation Resolution

### 5.1 What Happens When Voting Deadlocks

**Scenario:** 3 agents say "yes" (confidence 0.88, 0.85, 0.82), 2 agents say "no" (confidence 0.72, 0.68).

**Why it's a problem:**
- Yes: 3/5 (60%) = Simple majority
- But average yes confidence: 0.85
- Average no confidence: 0.70
- Despite simple majority, "yes" voters are MORE confident

**Escalation Process:**

```
1. Detect: Agreement < 75% threshold
2. Trigger: Weighted voting (confidence-weighted)
   Weighted Yes: (0.88 + 0.85 + 0.82) = 2.55
   Weighted No:  (0.72 + 0.68) = 1.40
   Total: 3.95
   Yes ratio: 2.55 / 3.95 = 64.6%

3. Decision: Weighted majority (64.6% > 60% threshold)
   → COMMIT "yes"

4. Log: Escalation resolved at weighted voting (no human intervention needed)
```

**What if still deadlocked at weighted voting?**

```
4b. Human Review Flag:
    - Send escalation to #maestro-incidents (Slack)
    - Include: context, both agent reasonings, confidence scores
    - Wait for human decision (SLA: 10 min)
    - Human approves or rejects

5. Human Decision:
   - Approve: Accept majority decision
   - Reject: Rollback and requeue with clarified context
   - Block: Mark workflow as requiring manual intervention
```

### 5.2 When to Escalate (Manual Decision)

**Automatic escalation occurs if:**
- Confidence spread > 0.30 (e.g., 0.90 vs 0.60)
- Vote split 3–2 with lower confidence on majority side
- Timeout after 15 min without reaching 75% agreement

**Human escalation examples:**

```
CASE 1: Procurement Decision (procurement: $5M+)
  Votes: S5 (yes, 0.88), S1 (yes, 0.82), S2 (yes, 0.79), S3 (no, 0.85), S4 (no, 0.81)
  Issue: "No" voters have higher confidence (0.85, 0.81 vs 0.88, 0.82, 0.79)
  → Escalate to human: "High confidence objection detected"

CASE 2: Risk Assessment (geotechnical hazard)
  Votes: S2 (yes risk, 0.92), others say "no" (avg 0.65)
  Issue: One agent highly confident in risk, others uncertain
  → Escalate to human: "Risk variance detected; recommend site inspection"

CASE 3: Timeline Acceleration
  Votes: S7 (yes, 0.58), S3 (yes, 0.61), others say "no" (0.90+)
  Issue: Low confidence on majority side
  → Escalate to human: "Majority low confidence; maintain conservative timeline"
```

---

## Part 6: What-If Simulation Interpretation

Simulations predict outcomes of hypothetical scenarios.

### 6.1 Running a Simulation

```bash
# Scenario: "What if we increase worker pool to 20?"
curl -X POST https://maestro-ops.internal/simulations \
  -d '{
    "scenario_name": "worker_pool_20",
    "changes": {
      "queue_executor.worker_count": 20  # ← hypothetical change
    },
    "forecast_hours": 24
  }'

# Response:
{
  "simulation_id": "sim_xyz789",
  "scenario": "worker_pool_20",
  "forecast": {
    "avg_queue_depth": 150,          # ← down from 400 now
    "avg_task_latency_ms": 250,      # ← down from 450 now
    "token_burn_rate_change": "+5%", # ← slight increase (more parallelism)
    "cost_impact": "$150/month"      # ← 20 vs 10 workers
  },
  "confidence": 0.82
}
```

### 6.2 Interpreting Simulation Results

| Metric | Good | Concerning | Action |
|--------|------|-------------|--------|
| Queue Depth Reduction | >30% | <10% | Small improvement only |
| Latency Improvement | >20% | <5% | Not worth the change |
| Token Burn Increase | <10% | >20% | Trade-off may not justify |
| Cost Impact | <$100/mo | >$500/mo | Economically unfavorable |
| Confidence | >0.85 | <0.70 | Prediction unreliable |

### 6.3 Example Simulation Scenarios

**Scenario 1: "Is more cache better?"**
```
Hypothesis: Increase Redis cache from 4GB to 8GB
Expected outcome: Cache hit rate 78% → 88% (higher = better)
Simulation result: Hit rate → 87%, latency -80ms, cost +$60/mo
Recommendation: ✅ IMPLEMENT (clear benefit)
```

**Scenario 2: "Reduce consensus poll timeout?"**
```
Hypothesis: Reduce consensus poll timeout from 15 min to 10 min
Expected outcome: Faster decisions, more escalations (tradeoff)
Simulation result: Escalations +8%, agreement rate -5%, deadline met 92% vs 99%
Recommendation: ❌ SKIP (escalations not worth deadline improvement)
```

---

## Part 7: Team Certification Checklist

Complete all 12 topics to certify as Maestro Operations Engineer.

### Topic 1: Architecture Layers
- [ ] I can name the 5 layers of Maestro (Workflow, Consensus, Agent, Queue, Inference)
- [ ] I can explain the data flow from workflow creation to decision
- [ ] I can identify which layer owns each component (detector, router, executor, etc.)
- [ ] I can draw the architecture diagram from memory

**Verification:** Whiteboard diagram + Q&A with team lead

---

### Topic 2: Consensus Voting Mechanics
- [ ] I understand the 5-voter quorum and majority rule (3/5)
- [ ] I can explain confidence scores (0.0–1.0 scale) and what drives them
- [ ] I can identify a consensus deadlock and explain weighted voting escalation
- [ ] I can determine when to escalate vs when to commit

**Verification:** Analyze 3 sample polls (high agreement, deadlock, timeout)

---

### Topic 3: Daily Health Checks
- [ ] I can run all Phase 1 checks (hourly for first 4 hours) and interpret results
- [ ] I can run all Phase 2 checks (daily at 08:00 and 16:00 UTC) and diagnose issues
- [ ] I can explain what each metric means (queue depth, worker utilization, hit rate, etc.)
- [ ] I can identify when to escalate based on health check results

**Verification:** Execute complete health check on test environment

---

### Topic 4: Workflow Monitoring & Stuck Detection
- [ ] I can identify a stuck workflow and determine its state
- [ ] I can check consensus poll details for a specific workflow
- [ ] I can manually escalate a consensus poll and update workflow state
- [ ] I can distinguish between "stuck in consensus" vs "stuck in queue" vs "agent timeout"

**Verification:** Debug 2 simulated stuck workflows

---

### Topic 5: Queue Executor Troubleshooting
- [ ] I can check worker pool health and identify dead workers
- [ ] I understand task retry logic and exponential backoff (5, 25, 125 sec, etc.)
- [ ] I can clear stuck tasks by reassigning, retrying, or canceling
- [ ] I can perform a graceful worker pool reset

**Verification:** Diagnose and fix 3 queue executor scenarios

---

### Topic 6: Token Budget Optimization
- [ ] I can read the token budget dashboard and calculate consumption rate
- [ ] I understand the monthly/daily/hourly budget breakdown
- [ ] I can identify 3 ways to reduce token burn (batching, context summarization, caching)
- [ ] I can forecast token exhaustion and recommend optimizations

**Verification:** Propose token optimization plan for test scenario

---

### Topic 7: Rate Limiting & Backoff Strategy
- [ ] I understand exponential backoff (5, 25, 125, 625 sec, max 300)
- [ ] I can identify rate-limited requests (HTTP 429) in logs
- [ ] I can check backoff queue depth and assess if it's draining properly
- [ ] I can decide whether to retry, wait, or escalate based on retry count

**Verification:** Analyze rate limit incident, trace 5 retries

---

### Topic 8: Metrics Dashboard Interpretation
- [ ] I can read the main status dashboard and identify critical vs minor issues
- [ ] I can interpret consensus metrics (agreement rate, escalation rate, divergence)
- [ ] I can interpret token budget metrics and predict daily consumption
- [ ] I can explain what normal values are for each metric

**Verification:** Dashboard walkthrough + interpret 5 metric anomalies

---

### Topic 9: Multi-Agent Debugging
- [ ] I can use the diagnostic tree to narrow down failure causes
- [ ] I can read agent confidence scores and identify outliers
- [ ] I can access agent logs and understand error messages
- [ ] I can determine whether failure is agent, consensus, queue, or data-related

**Verification:** Debug 3 workflow failures from logs alone

---

### Topic 10: Escalation Procedures & Human Review
- [ ] I can check active escalations and their status
- [ ] I can manually resolve an escalation (commit vs rollback)
- [ ] I understand when to escalate to human vs auto-resolve
- [ ] I can document escalation decisions in incident log

**Verification:** Simulate escalation resolution process

---

### Topic 11: Rollback & Emergency Procedures
- [ ] I can perform a quick rollback to previous deployment (< 5 min)
- [ ] I can flush and rebuild cache safely
- [ ] I understand database rollback risks and when to use it
- [ ] I can coordinate with team during critical incidents

**Verification:** Rapid rollback drill (test environment)

---

### Topic 12: On-Call Readiness
- [ ] I have access to all dashboards, logs, and alerting systems
- [ ] I understand escalation timers (P1: 15 min, P2: 30 min, P3: 2 hours)
- [ ] I can respond to a simulated P1 page within 15 minutes
- [ ] I can post incident updates and RCA summary

**Verification:** Simulated P1 incident response (30 min duration)

---

## Certification Sign-Off

**Candidate Name:** ________________  
**Date Completed:** ________________  
**Team Lead Signature:** ________________  

All 12 topics must be checked and verified by team lead before certification.

**Certification Valid Until:** [Date + 1 year]

---

## Additional Resources

- **Runbook:** `/docs/MAESTRO-OPERATIONS-RUNBOOK.md`
- **Troubleshooting:** `/docs/MAESTRO-TROUBLESHOOTING-PROCEDURES.md`
- **API Reference:** `https://maestro-api.internal/docs`
- **Slack Channel:** `#maestro-incidents` (incidents), `#maestro-engineering` (updates)

**Next Steps:** Schedule team lead review and on-call transition.

---

**Last Reviewed:** 2026-07-26  
**Next Review:** 2026-08-26  
**Owner:** SRE Team (Maestro Operations)
