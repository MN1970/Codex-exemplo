# Shadow Mode Deployment Checklist — Jul 22, 2026

**Phase**: Pre-deployment verification for 30-day CAG vs RAG comparison  
**Window**: Jul 22 – Aug 21, 2026  
**Owner**: DevOps / Platform Engineering  
**Status**: Ready for execution

---

## ✅ PRE-DEPLOYMENT (Jul 21 EOD)

### Code & Tests
- [x] All 91 tests passing (test_cag_e2e, test_cag_edge_cases, test_parallel_processor, test_shadow_mode)
- [x] Intent classifier confidence fixed (0.65+ base, position/word bonuses)
- [x] Agent selector thresholds adjusted (min_confidence: 0.3)
- [x] ResponseRanker tests mocked for CI
- [x] PR #16 approved and merged
- [x] Branch `claude/manta-maestro-cag-ml-8wdrg4` on main

### Database
- [ ] Supabase migration `2026_07_22_v1_0_shadow_mode.sql` applied
  ```sql
  -- Tables created:
  - cag_shadow_logs (per-query comparison)
  - cag_shadow_daily_stats (daily aggregates)
  - cag_shadow_config (feature flags)
  - fn_compute_shadow_daily_stats() (aggregation function)
  ```
- [ ] Verify indexes created (session, timestamp, rag_agent, agent_match)
- [ ] Verify config table populated with thresholds
- [ ] Test daily stats function with sample data

### Infrastructure
- [ ] Docker image built and tested
  - Base: Python 3.11-slim
  - CMD: `python -m pytest cag/tests/` (health check)
- [ ] requirements.txt validated (all dependencies installable)
- [ ] Environment variables configured
  - `ANTHROPIC_API_KEY` (for Claude ranking)
  - `SUPABASE_URL` / `SUPABASE_KEY`
  - `SHADOW_MODE_ENABLED=true`
  - `DEBUG=false`

### Configuration
- [ ] Supabase config table values reviewed
  ```
  enabled: true
  start_date: 2026-07-22
  end_date: 2026-08-21
  buffer_size: 100
  agent_match_threshold: 0.85
  latency_threshold_pct: 10.0
  error_threshold: 0.001
  comparison_mode: parallel
  debug_logging: false
  ```

---

## 🚀 DEPLOYMENT (Jul 22 00:00 UTC)

### Step 1: Database Migration
```bash
# Apply migration to production Supabase
supabase db push --remote

# Verify tables exist
SELECT tablename FROM pg_tables 
WHERE tablename LIKE 'cag_shadow_%' 
ORDER BY tablename;

# Expected: 3 tables + 1 function
```
**Owner**: DBA | **Time**: 5 min | **Rollback**: See rollback script in migration file

### Step 2: Deploy Shadow Mode Service
```bash
# Build image
docker build -t manta/cag-shadow-mode:v1.0 .

# Push to registry
docker push manta/cag-shadow-mode:v1.0

# Deploy to staging first (canary)
kubectl set image deployment/shadow-mode-canary \
  shadow-mode=manta/cag-shadow-mode:v1.0

# Wait 30 min, verify logs
kubectl logs -f deployment/shadow-mode-canary
```
**Owner**: DevOps | **Time**: 15 min | **Smoke Test**: Check logs for no errors

### Step 3: Enable Shadow Mode Flag
```bash
# Update Supabase config
UPDATE cag_shadow_config 
SET value = 'true' 
WHERE key = 'enabled' 
AND value = 'false';

# Verify
SELECT * FROM cag_shadow_config WHERE key = 'enabled';
```
**Owner**: Platform | **Time**: 2 min | **Effect**: Immediate (no restart needed)

### Step 4: Verify First Queries
- [ ] Monitor logs for new entries in `cag_shadow_logs`
- [ ] Check first 10 rows for valid comparison data
  ```sql
  SELECT session_id, timestamp, rag_agent, cag_selected_agents, 
         agent_match, confidence_delta, latency_delta_ms 
  FROM cag_shadow_logs 
  ORDER BY timestamp DESC 
  LIMIT 10;
  ```
- [ ] Verify RAG results still returned to users (shadow doesn't block)
- [ ] Confirm CAG results logged (no API errors)

**Expected**: Data flowing within 5 min of deployment

---

## 📊 FIRST 24 HOURS (Jul 22–23)

### Hourly Checks
- [ ] Query count: 50+ queries logged (non-zero traffic)
- [ ] Agent match rate: sample trending toward ≥85%
- [ ] Latency delta: CAG within ±20% of RAG (not regressing fast)
- [ ] Error rate: <1% (allowing startup glitches)

### Daily Aggregation
```sql
-- Manual trigger on Jul 22 EOD
SELECT fn_compute_shadow_daily_stats('2026-07-22'::DATE);

-- Review results
SELECT date_bucket, total_queries, agent_match_rate, 
       rag_p50_ms, cag_p50_ms, latency_delta_pct_avg, 
       go_ready 
FROM cag_shadow_daily_stats 
WHERE date_bucket >= '2026-07-22' 
ORDER BY date_bucket DESC;
```

### Alerts to Trigger
- [ ] **Error Rate Spike** (>2%): Page on-call
- [ ] **No Queries for 30 min**: Check maestro logs, RAG handler
- [ ] **CAG Latency >2x RAG** (>20%): Investigate classifier performance

---

## 🔧 DAILY OPERATIONS (Jul 23–Aug 21)

### Morning Standup (UTC 08:00)
1. Review previous day's `cag_shadow_daily_stats` row
2. Check `go_ready` flag (0 = NO-GO, 1 = GO)
3. Identify blockers:
   - Agent match < 85%? → Tune keyword thresholds
   - Latency > 10% slower? → Profile classifier + ranker
   - Errors > 0.1%? → Check API rate limits, network
4. Update stakeholders (MN, team)

### Data Collection (Automated)
- ShadowModeLogProcessor flushes every 100 queries (batching)
- Daily stats computed at 23:59 UTC via cron job
- Parallel analysis engine runs 5 dimensions (accuracy, latency, errors, trends, agents)

### Weekly Review (Friday EOD)
- Pull 7-day summary from `cag_shadow_daily_stats`
- Calculate trending metrics
- Prepare GO/NO-GO recommendation for week 2

---

## ✋ MANUAL GATES (Weeks 1, 2, 3)

### After Week 1 (Jul 29 EOD)
**Decision**: Continue shadow mode or escalate?

**GO Criteria Met?**
- [ ] Agent match rate ≥85% across 7 days
- [ ] CAG latency within 10% of RAG (not slower)
- [ ] Error rate <0.1%
- [ ] No data loss (all queries logged)

**Action**:
- **GO**: Proceed to week 2, no changes
- **NO-GO**: 
  - Stop accepting new intent classes for CAG (lock to saneamento, energia, etc.)
  - Tuning window: Jul 29–31
  - Re-evaluate Aug 1

### After Week 2 (Aug 5 EOD)
**Decision**: Ready for pilot phase or extend shadow?

**Criteria**:
- 14 days of clean data
- Trending stable (no degradation)
- Historical precedent from week 1 validated

**Action**:
- **GO**: Schedule pilot phase (start date Aug 8)
- **EXTEND**: Continue shadow 1 more week, re-eval Aug 12

### Before Week 3 Cutoff (Aug 15)
**Decision**: Prepare for end-of-window synthesis

- Compile 30-day report
- Final GO/NO-GO recommendation
- Prepare pilot rollout or fallback plan

---

## 🛑 ROLLBACK PROCEDURE (If Needed)

### Immediate (< 5 min)
```bash
# Disable shadow mode flag
UPDATE cag_shadow_config 
SET value = 'false' 
WHERE key = 'enabled';

# Users see RAG responses, CAG logging stops
# No data loss (cag_shadow_logs preserved)
```

### Full Revert (if data corruption suspected)
```sql
-- See rollback script at bottom of migration file
DROP FUNCTION fn_compute_shadow_daily_stats(DATE);
DROP TABLE cag_shadow_logs CASCADE;
DROP TABLE cag_shadow_daily_stats CASCADE;
DROP TABLE cag_shadow_config CASCADE;
```

**Note**: Keep enabled=false for 48h before full drop (recovery window)

---

## 📋 SIGN-OFF

| Role | Name | Date | Status |
|------|------|------|--------|
| DevOps Lead | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_ | [ ] Ready |
| DBA | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_ | [ ] Ready |
| Platform Lead | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_ | [ ] Ready |
| MN (Decision) | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_ | [ ] Approved |

---

## 📞 CONTACTS & ESCALATION

| On-Call | Timezone | Slack | Phone |
|---------|----------|-------|-------|
| DevOps | UTC | #platform-oncall | +55 11 XXXX-XXXX |
| DBA | UTC | #data-oncall | +55 11 XXXX-XXXX |
| MN (Decision) | UTC | @MN | +55 11 XXXX-XXXX |

**Escalation Path**:
1. Error rate spike → DevOps oncall
2. Data anomaly → DBA oncall
3. GO/NO-GO decision → MN
4. Crisis (complete outage) → VP Engineering

---

## 📚 Related Docs

- [Shadow Mode Architecture](./SHADOW_MODE_DEPLOYMENT.md)
- [Parallel Operations Guide](./SHADOW_MODE_PARALLEL_OPERATIONS.md)
- [CAG ML Migration Notes](./CLAUDE.md) — v5.0 prototipagem section
- [Test Suite Results](../cag/tests/) — 91/91 passing

---

**Last Updated**: 2026-07-20  
**Prepared By**: Claude Code  
**Approved By**: [MN signature required]
