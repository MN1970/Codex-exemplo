# Phase 3.5: Advanced Routing (LLM Tie-Breaker) — Implementation Guide

**Version**: v1.0  
**Date**: 2026-07-27  
**Status**: Ready for Implementation  
**Team**: Maestro, Data, DevOps  
**Timeline**: Q3 2027 (Month 19-20, Phase 3)

---

## Executive Summary

Phase 3.5 implements **LLM-powered tie-breaker routing** to disambiguate close routing decisions using Claude Sonnet. When multiple agents score within a confidence threshold, the Manta 16 (Arquiteto-IA) agent provides semantic reasoning to select the best-fit agent.

**Key Metrics**:
- **Latency**: <500ms p95 (includes tie-breaker invocation)
- **Approval rate**: ≥85% (users approve tie-breaker decision)
- **Deployment**: FastAPI service + Cowork integration
- **Cost per tie-breaker**: <$0.05 (Sonnet @ ~400 tokens)
- **Success criterion**: 85%+ approval rate within 30 days of launch

---

## Architecture Overview

### High-Level Flow

```
Query Input
    ↓
Standard Multi-Agent Routing (Keyword + Vector Search)
    ↓
Score Results: Agent1=0.92, Agent2=0.88, Agent3=0.75
    ↓
Gap Detection: (0.92 - 0.88) = 0.04 < threshold (0.10)
    ↓
YES: Invoke Tie-Breaker
    ├─ Manta 16 (Sonnet) semantic analysis
    ├─ Reason-based score adjustment
    ├─ Confidence boosting
    ↓
Return Tie-Breaker Decision
    ↓
User Feedback (Cowork button)
    ↓
Feedback Loop: Adjust scores, boost/penalize tie-breaker
    ↓
Weekly Analysis: Statistical significance, model updates
```

### Components

1. **Tie-Breaker Service** (`maestro/tiebreaker.py`)
   - Score gap detection algorithm
   - Manta 16 (Sonnet) invocation wrapper
   - Reasoning-based score adjustment
   - Confidence boosting heuristics

2. **Feedback Integration** (`maestro/feedback_integration.py`)
   - Track user corrections
   - Boost/penalize tie-breaker decisions
   - Feedback loop SQL analysis
   - Weekly recommendation job

3. **A/B Testing Framework** (`maestro/ab_testing.py`)
   - Control group: standard routing
   - Variant group: tie-breaker routing
   - Metrics collection & analysis
   - Statistical significance testing

4. **Monitoring & Metrics** (`maestro/monitoring.py`)
   - Tie-breaker invocation tracking
   - Success rate monitoring
   - Latency percentiles (p50, p95, p99)
   - Cost per call tracking

5. **Test Suite** (`tests/phase_3_5/test_tiebreaker.py`)
   - Ambiguous query scenarios (50+ test cases)
   - Tie-breaker accuracy validation
   - Performance benchmarks
   - Edge case handling

---

## Implementation Details

### 1. Tie-Breaker Service

**File**: `maestro/tiebreaker.py` (~320 lines)

#### Key Classes

```python
class ScoreGapDetector:
    """Detects when routing scores are within tie-breaker threshold."""
    
    def should_trigger_tiebreaker(
        scores: Dict[str, float],
        gap_threshold: float = 0.10,
        min_score: float = 0.70
    ) -> Tuple[bool, Dict]:
        """
        Returns (should_trigger, metadata).
        
        Triggers if:
        - Top 2 scores gap < gap_threshold
        - Top score >= min_score
        - Not a clear winner
        """

class TieBreakerInvoker:
    """Invokes Manta 16 (Sonnet) for disambiguation."""
    
    async def invoke_manta16(
        query: str,
        candidates: List[Agent],
        context: RoutingContext
    ) -> TieBreakerResult:
        """
        Calls Manta 16 with:
        - Original query
        - Candidate agents + current scores
        - Project context (if available)
        - RAG context snippets
        
        Returns reasoning + adjusted scores.
        """

class ScoreAdjuster:
    """Adjusts scores based on tie-breaker reasoning."""
    
    def adjust_scores(
        original_scores: Dict[str, float],
        tiebreaker_reasoning: str,
        confidence: float
    ) -> Dict[str, float]:
        """
        Applies multiplicative adjustment based on:
        - Confidence level (0.0-1.0)
        - Reasoning specificity
        - Domain keyword matches in reasoning
        
        Preserves original scores when confidence < 0.60.
        """

class ConfidenceBooster:
    """Boosts scores based on feedback history."""
    
    def boost_from_history(
        agent_id: str,
        user_approval_rate: float,
        recent_feedback: List[Feedback]
    ) -> float:
        """
        Multiplier range: 0.95 - 1.05
        - Recent wins (past 7 days): +0.02
        - High approval rate (>85%): +0.03
        - Penalty for recent losses: -0.03
        """
```

#### Configuration

```yaml
# config/phase_3_5.yaml
tiebreaker:
  enabled: true
  gap_threshold: 0.10              # Score gap triggering tie-breaker
  min_score: 0.70                  # Minimum score to consider routing
  max_latency_ms: 400              # Strict latency budget
  
  manta16:
    model: "claude-3-5-sonnet-20241022"
    timeout_ms: 350
    max_tokens: 500
    temperature: 0.3               # Low temp for consistency
    
  scoring:
    confidence_weight: 0.8         # How much to adjust based on confidence
    feedback_boost_max: 0.05       # Max boost from feedback
    
  fallback:
    timeout_strategy: "original"   # Fall back to top-1 on timeout
    error_strategy: "standard"     # Fall back on API errors
```

### 2. Feedback Integration

**File**: `maestro/feedback_integration.py` (~160 lines)

#### Database Schema Extension

```sql
-- Extends routing_feedback table (Phase 2.1)
ALTER TABLE routing_feedback ADD COLUMN (
    tiebreaker_invoked BOOLEAN DEFAULT false,
    tiebreaker_decision TEXT,          -- Agent ID selected by tie-breaker
    user_approved BOOLEAN,              -- User confirmed/overrode decision
    correction_agent_id TEXT,           -- Agent user actually chose
    correction_confidence FLOAT,        -- Confidence in correction
    adjusted_scores JSONB               -- Final scores after adjustment
);

-- New table: tiebreaker_metrics
CREATE TABLE tiebreaker_metrics (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    invocation_count INTEGER,
    success_count INTEGER,            -- User approved
    failure_count INTEGER,            -- User corrected
    avg_latency_ms FLOAT,
    cost_usd FLOAT,
    gap_threshold_used FLOAT,
    week_number INTEGER,
    UNIQUE(week_number)
);
```

#### Key Classes

```python
class FeedbackAnalyzer:
    """Analyzes user corrections and feedback."""
    
    async def record_feedback(
        routing_id: str,
        user_approved: bool,
        actual_agent: str,
        context: Dict
    ) -> None:
        """
        Records user decision.
        If approved: boosts tie-breaker decision score.
        If corrected: penalizes tie-breaker, learns from correction.
        """
    
    async def calculate_approval_rate(
        agent_id: str,
        window_days: int = 7
    ) -> Dict[str, float]:
        """
        Returns:
        {
            'approval_rate': 0.87,
            'correction_rate': 0.13,
            'total_decisions': 150,
            'trend': 'up'  # week-over-week
        }
        """

class ScoreBoosting:
    """Boosts scores based on feedback history."""
    
    async def get_feedback_boost(
        agent_id: str,
        recent_window_days: int = 7
    ) -> float:
        """
        Returns multiplier (0.95 - 1.05):
        - High approval: +0.03
        - Recent wins: +0.02
        - Penalties: -0.03 to -0.05
        """

class WeeklyRecommendationJob:
    """Runs every Monday 08:00 UTC."""
    
    async def analyze_week(week_number: int) -> Recommendations:
        """
        Generates:
        - Gap threshold adjustment (if approval < 80%)
        - Agent score recalibration
        - Confidence penalty/boost recommendations
        - Statistical significance tests
        
        Outputs to:
        - tiebreaker_metrics table
        - Slack notification to #maestro-data
        - GitHub issue if action required
        """
```

### 3. A/B Testing Framework

**File**: `maestro/ab_testing.py` (~210 lines)

#### Design

```
User Population: 10,000 routed queries/week

Control Group (50%):   5,000 queries
├─ Standard routing (keyword + vector search)
├─ No tie-breaker invocation
├─ Baseline approval rate tracking

Variant Group (50%):   5,000 queries
├─ Standard routing + tie-breaker for gaps < 0.10
├─ Manta 16 invocation when score gap detected
├─ Tie-breaker approval rate tracking

Metrics:
- Approval rate (primary metric)
- Latency (p95)
- Cost per routing (delta cost for tie-breaker)
- User satisfaction (CSAT via Cowork)
- Agent specialist alignment
```

#### Key Classes

```python
class ABTestManager:
    """Manages A/B test lifecycle."""
    
    def assign_group(user_id: str, query_id: str) -> str:
        """
        Deterministic assignment using SHA256(user_id + seed).
        Returns 'control' or 'variant'.
        """
    
    async def record_test_event(
        query_id: str,
        group: str,
        event: str,  # 'routed', 'feedback', 'approved', 'corrected'
        metadata: Dict
    ) -> None:
        """Logs all test events to ClickHouse (analytics DB)."""
    
    async def get_test_metrics(
        start_date: date,
        end_date: date
    ) -> TestResults:
        """
        Returns:
        {
            'control': {
                'approval_rate': 0.82,
                'latency_p95_ms': 180,
                'cost_per_query': 0.008,
                'sample_size': 5000
            },
            'variant': {
                'approval_rate': 0.87,
                'latency_p95_ms': 420,
                'cost_per_query': 0.053,
                'sample_size': 5000
            },
            'statistical_significance': {
                'approval_rate_p_value': 0.003,  # Significant
                'confidence_interval': [0.01, 0.08],
                'power': 0.95
            }
        }
        """

class StatisticalAnalysis:
    """Performs significance testing."""
    
    def two_proportion_ztest(
        control_successes: int,
        control_n: int,
        variant_successes: int,
        variant_n: int
    ) -> Dict:
        """
        Returns p-value, confidence interval, power.
        Threshold: p < 0.05 for significance.
        """
    
    def minimum_sample_size(
        baseline_rate: float = 0.82,
        expected_lift: float = 0.05,  # 5% relative lift
        alpha: float = 0.05,
        power: float = 0.90
    ) -> int:
        """
        Returns samples per group needed.
        Typical: 2,500-5,000 per group.
        """
```

#### Database

```sql
CREATE TABLE ab_test_events (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    query_id UUID,
    user_id TEXT,
    test_group TEXT,  -- 'control' or 'variant'
    event_type TEXT,  -- 'routed', 'feedback', 'approved', 'corrected'
    routing_result JSONB,
    metadata JSONB,
    INDEX (timestamp, test_group, event_type)
);
```

### 4. Monitoring & Metrics

**File**: `maestro/monitoring.py` (~110 lines)

#### Metrics Collected

```
# Prometheus metrics (exposed on /metrics)

maestro_tiebreaker_invocations_total
    Labels: status (success|timeout|error|fallback)
    
maestro_tiebreaker_success_rate
    Labels: agent_id
    Range: [0.0, 1.0]
    
maestro_tiebreaker_latency_seconds
    Labels: quantile (0.5, 0.95, 0.99)
    
maestro_tiebreaker_cost_usd_total
    Labels: none
    
maestro_tiebreaker_confidence_distribution
    Labels: confidence_bucket (0.0-0.2, 0.2-0.4, ..., 0.8-1.0)
    
maestro_tiebreaker_gap_distribution
    Labels: gap_bucket (0.0-0.05, 0.05-0.10, 0.10+)
    
maestro_feedback_approval_rate
    Labels: agent_id, window_days
    Range: [0.0, 1.0]
```

#### Key Classes

```python
class TieBreakerMetrics:
    """Collects and exports tie-breaker metrics."""
    
    def __init__(self):
        self.invocations = Counter(
            'maestro_tiebreaker_invocations_total',
            'Total tie-breaker invocations',
            ['status']
        )
        self.latency = Histogram(
            'maestro_tiebreaker_latency_seconds',
            'Tie-breaker latency',
            buckets=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
        )
        # ... more metrics
    
    async def record_invocation(
        duration_ms: float,
        success: bool,
        confidence: float,
        cost_usd: float
    ) -> None:
        """Records one tie-breaker invocation."""
    
    async def get_realtime_dashboard(self) -> Dict:
        """
        Returns current state for Grafana:
        - Invocation rate (queries/min)
        - Success rate (%)
        - Latency p95 (ms)
        - Cost per call (USD)
        - Approval rate by agent (%)
        """

class DashboardGenerator:
    """Generates Grafana dashboard JSON."""
    
    def generate_phase_3_5_dashboard(self) -> str:
        """Returns Grafana dashboard JSON with 8 panels."""
```

#### Grafana Panels

```
Panel 1: Tie-Breaker Invocation Rate (requests/min)
Panel 2: Success Rate by Agent (%)
Panel 3: Latency Distribution (p50, p95, p99)
Panel 4: Cost Per Tie-Breaker Call (USD)
Panel 5: Approval Rate Trend (7-day rolling)
Panel 6: Score Gap Distribution (histogram)
Panel 7: A/B Test Metrics (control vs variant)
Panel 8: Error Rate & Fallback Rate (%)
```

### 5. Test Suite

**File**: `tests/phase_3_5/test_tiebreaker.py` (~280 lines)

#### Test Categories

```
1. Ambiguous Queries (25 test cases)
   ├─ Infrastructure domain (rodovias, pontes, túneis)
   ├─ Saneamento domain
   ├─ Energia domain
   ├─ Portos/Aeroportos domain
   └─ Multi-domain queries

2. Tie-Breaker Accuracy (15 test cases)
   ├─ Correct disambiguation
   ├─ Confidence threshold validation
   ├─ Score adjustment verification
   └─ Fallback behavior on timeout

3. Performance Benchmarks (10 test cases)
   ├─ Latency <500ms p95
   ├─ Cost <$0.05 per call
   ├─ Throughput 100+ queries/sec
   └─ Concurrent invocation handling

4. Edge Cases (20 test cases)
   ├─ All scores equal
   ├─ Single candidate after filtering
   ├─ No candidates above min_score
   ├─ Malformed agent metadata
   ├─ Network timeout handling
   └─ Invalid routing context
```

#### Key Test Functions

```python
class TestTieBreakerService:
    
    @pytest.mark.asyncio
    async def test_ambiguous_saneamento_query(self):
        """Test tie-breaker on ambiguous saneamento query."""
        query = "ETA com lagoas de tratamento e submersas"
        scores = {
            'agente-saneamento': 0.92,
            'agente-infraestrutura-s1': 0.88,
            'agente-energia': 0.65
        }
        
        result = await tiebreaker.invoke_manta16(
            query, scores, context
        )
        
        assert result.selected_agent == 'agente-saneamento'
        assert result.confidence > 0.80
        assert result.reasoning is not None
    
    @pytest.mark.asyncio
    async def test_latency_under_500ms(self):
        """Verify tie-breaker latency is under 500ms p95."""
        latencies = []
        for _ in range(100):
            start = time.time()
            await tiebreaker.invoke_manta16(query, scores, context)
            latencies.append((time.time() - start) * 1000)
        
        p95 = np.percentile(latencies, 95)
        assert p95 < 500, f"p95 latency {p95}ms exceeds 500ms budget"
    
    @pytest.mark.asyncio
    async def test_cost_under_005_usd(self):
        """Verify cost per tie-breaker call < $0.05."""
        # Mock Anthropic API usage tracking
        result = await tiebreaker.invoke_manta16(
            query, scores, context
        )
        
        cost = result.cost_usd
        assert cost < 0.05, f"Cost ${cost} exceeds $0.05 budget"
```

---

## Deployment Checklist

### Pre-Deployment (Week 1-2)

- [ ] Code review (Security, Data, Maestro teams)
- [ ] Database migrations applied (tiebreaker_metrics table)
- [ ] Environment variables configured
  - [ ] `MANTA_16_ENDPOINT` (Manta 16 service URL)
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `SUPABASE_URL`, `SUPABASE_KEY`
- [ ] Test suite passes (100% of 280 tests)
- [ ] Load testing: 1,000 req/sec mock traffic
- [ ] Fallback mechanisms validated (timeout, error handling)

### Deployment (Week 3)

- [ ] Deploy tiebreaker service to staging (Cloud Run)
- [ ] Integrate with maestro-router (Phase 1 baseline)
- [ ] Wire Cowork feedback button to feedback_integration
- [ ] Enable A/B test (50/50 split)
- [ ] Verify metrics flowing to Grafana
- [ ] Smoke tests on production traffic (1% of queries)

### Post-Deployment (Week 4+)

- [ ] Monitor approval rate daily (target: ≥85%)
- [ ] Monitor latency p95 (target: <500ms)
- [ ] Run statistical significance test on day 7 (p < 0.05)
- [ ] Weekly recommendation job executes (Monday 08:00 UTC)
- [ ] Cost tracking: <$0.05 per call
- [ ] Team training: Maestro + Data teams on monitoring dashboard

---

## Success Criteria (Monitoring Gates)

| Metric | Target | SLA | Action if Missing |
|--------|--------|-----|-------------------|
| Tie-breaker approval rate | ≥85% | 30 days | Recalibrate gap threshold |
| Latency p95 | <500ms | Always | Roll back (fallback to Phase 2) |
| Cost per call | <$0.05 | Always | Optimize prompt or reduce scope |
| A/B test p-value | <0.05 | Day 7 | Declare statistical significance |
| Error rate | <1% | Always | Debug API integration |
| User satisfaction (CSAT) | ≥4.0/5 | Day 14 | Improve reasoning clarity |

---

## Configuration & Tuning

### Gap Threshold Tuning

Start with `gap_threshold=0.10` (10% gap).

- **If approval rate too low** (<80%): Increase to 0.12
- **If too many timeouts** (latency >500ms): Increase to 0.15
- **If approval rate high** (>90%): Decrease to 0.08 (invoke more)

### Confidence Weighting

Adjust `confidence_weight` (default 0.8):

- **Aggressive**: 0.9 (trust tie-breaker more)
- **Conservative**: 0.6 (blend with original scores)
- **Balanced**: 0.8 (recommended)

### Model Selection

Current: `claude-3-5-sonnet-20241022`

Alternatives:
- `claude-3-opus-20250219`: Higher quality, but slower + expensive
- `claude-3-haiku-20250307`: Faster, but lower reasoning quality

---

## Runbooks

### Runbook 1: Tie-Breaker Latency Exceeds 500ms

```
1. Check Manta 16 service health (health check endpoint)
2. If service down: Page on-call engineer (SRE)
3. If service slow: Check CloudTrace for slowness patterns
4. If tie-breaker code slow: Optimize prompt or reduce max_tokens
5. If API latency slow: Roll back to Phase 2 (no tie-breaker)
```

### Runbook 2: Approval Rate Falls Below 80%

```
1. Check gap_threshold setting (maybe too low, invoking too often)
2. Analyze confidence distribution (confidence metric panel)
3. Check Manta 16 output quality (reasoning field)
4. Run A/B test metrics to compare control vs variant
5. If issue confirmed: Increase gap_threshold by 0.02, monitor
```

### Runbook 3: Cost Exceeds $0.05 Per Call

```
1. Check model usage (Sonnet token counts)
2. Check prompt length (RAG context size)
3. Reduce max_tokens (default 500, try 300)
4. Reduce RAG context snippets (default 3, try 2)
5. Consider Haiku model for high-volume queries
```

---

## Timeline

### Phase 3.5 Execution (Q3 2027, 6 weeks)

**Week 1-2: Development**
- Implement tiebreaker.py (TieBreakerInvoker, ScoreAdjuster, ConfidenceBooster)
- Implement feedback_integration.py (FeedbackAnalyzer, WeeklyJob)
- Database migrations
- Unit tests (150+ tests)

**Week 3-4: Integration**
- Integrate with maestro-router (Phase 1)
- Wire Cowork feedback button
- Implement monitoring dashboard
- Implement A/B testing framework

**Week 5: Testing**
- Load testing (1,000 req/sec)
- Staging deployment & smoke tests
- Security review & API key audit
- Runbook validation

**Week 6+: Production**
- Canary deployment (1% of traffic)
- Monitor metrics (daily standup)
- Weekly statistical analysis
- Scale to 100% if successful

---

## Budget & Cost Analysis

### Infrastructure Cost

| Component | Monthly Cost |
|-----------|-------------|
| Manta 16 API calls (100K queries @ 400 tokens) | ~$50 |
| Supabase storage (feedback, metrics) | ~$10 |
| Cloud Run (tiebreaker service) | ~$20 |
| Grafana dashboard | ~$5 |
| **Total** | **~$85/month** |

### Savings from Improved Routing

- **Current approval rate**: 82% (Phase 1)
- **Target approval rate**: 87% (Phase 3.5)
- **5% lift × 10,000 weekly queries = 500 better routings/week**
- **Value**: 500 × $100 (avg project value) = $50K saved/week

**ROI**: 6,000:1 (monthly cost vs savings)

---

## References

- Phase 2.1: Feedback Loop (PHASE-2.1-FEEDBACK-INTEGRATION.md)
- Phase 3.0: Architecture (PHASE-3-PUBLIC-API.md)
- Manta 16 Spec (manta-16-arquiteto-ia.md)
- CLAUDE.md (v5.0, Maestro registry)

---

## Questions & Support

- **Architecture**: maestro@mantaassociados.com
- **Data/Analytics**: data@mantaassociados.com
- **DevOps/Deployment**: devops@mantaassociados.com
- **Slack channel**: #maestro-phase-3-5

---

**Document Version**: v1.0  
**Last Updated**: 2026-07-27  
**Next Review**: 2026-08-01 (after Phase 2 metrics baseline)
