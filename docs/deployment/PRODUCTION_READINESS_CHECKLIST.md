# Production Readiness Checklist — Phase 3 RAG Deployment
**Date:** 26 de julho de 2026  
**Status:** In Progress  
**Target:** Production deployment 2026-08-15 (3 weeks)

---

## Pre-Deployment Phase (This week)

### Code & Configuration
- [ ] **Phase 3 Commits Verified**
  - Commit 70ff798: Hybrid embedding + semantic layer ✅
  - All 4 files committed to claude/rag-benchmark-greide-optimization-o6wrat ✅
  - PR #32 created (draft, clean merge state) ✅

- [ ] **SQL Migration Ready**
  - rag_insert.sql created (531 lines)
  - ⚠️ **TODO:** Fix word count validation errors (58 chunks rejected)
  - Anti-term table (31 pairs) prepared
  - Domain thresholds configured (8 domains)
  - Rollback plan documented

- [ ] **Configuration Files**
  - [ ] Domain threshold config (S1-S10 similarity thresholds)
  - [ ] Embedding model config (text-embedding-3-large primary, E5-large fallback)
  - [ ] Search function parameters (ensemble weights, contamination penalty)
  - [ ] Monitoring thresholds (S10 Recall@1 ≥ 50%, overall contamination ≤ 1%)

### Testing
- [ ] **Unit Tests**
  - [ ] Anti-term filtering logic (31 pairs × 2 directions = 62 test cases)
  - [ ] Domain threshold application (8 domains × 2 thresholds = 16 test cases)
  - [ ] Embedding ensemble ranking (dual model fusion, top-k selection)
  - [ ] Search function latency (p99 < 500ms target)

- [ ] **Integration Tests**
  - [ ] SQL migration execution (full INSERT of 58 chunks)
  - [ ] Search on synthetic chunks (retrieve all 4 ambiguous terms)
  - [ ] Cross-domain contamination (verify 0 S10 contamination in other domains)
  - [ ] Benchmark re-run (39 queries, confirm 84.62% Recall@1)

- [ ] **Performance Tests**
  - [ ] Throughput: 100 queries/sec (or document peak capacity)
  - [ ] Latency: p50 < 200ms, p95 < 400ms, p99 < 500ms
  - [ ] Memory: embedding cache footprint < 2GB
  - [ ] CPU: sustained load < 60% during peak queries

- [ ] **Regression Tests**
  - [ ] All Phase 1+2 achievements maintained (0% contamination)
  - [ ] No performance degradation vs. Phase 2 (latency +0-50ms acceptable)
  - [ ] No new cross-domain errors (verify against baseline)
  - [ ] Fallback to E5-large functional if primary unavailable

### Documentation
- [ ] **Deployment Guide**
  - [ ] Step-by-step execution instructions
  - [ ] Prerequisites (Supabase credentials, API keys, env vars)
  - [ ] Verification checklist (post-deployment validation)
  - [ ] Rollback procedure (with timeline estimate)

- [ ] **Operations Handbook**
  - [ ] Monitoring dashboard setup
  - [ ] Alert thresholds (S10 Recall@1, contamination rate, latency)
  - [ ] Incident response (degraded performance, contamination spike)
  - [ ] On-call escalation (24/7 support model)

- [ ] **Architecture Decision Records (ADRs)**
  - [ ] Why text-embedding-3-large (vs. E5-large, ada-002)
  - [ ] Why dynamic thresholds per domain (vs. single global threshold)
  - [ ] Why ensemble ranking (vs. single model)
  - [ ] Why S10 fine-tuning as Phase 3.5 (vs. blocking deployment)

---

## Staging Deployment (Week 2)

### Infrastructure
- [ ] **Supabase Staging Environment**
  - [ ] Backup main database (full snapshot)
  - [ ] Apply SQL migration to staging (rag_insert.sql)
  - [ ] Verify 58 chunks inserted successfully
  - [ ] Verify 31 anti-term pairs created
  - [ ] Verify 8 domain configs applied

- [ ] **Embedding Service Staging**
  - [ ] Spin up text-embedding-3-large (OpenAI API or local)
  - [ ] Configure E5-large fallback (HuggingFace or local)
  - [ ] Test ensemble ranking (dual model fusion)
  - [ ] Load balancing (distribute queries across models)

- [ ] **Search Function Staging**
  - [ ] Deploy contamination filter (anti-term lookup)
  - [ ] Deploy dynamic threshold logic (per-domain similarity)
  - [ ] Deploy query expansion (5 Phase 3 residual queries)
  - [ ] Test end-to-end search pipeline

### Validation
- [ ] **Smoke Tests (Staging)**
  - [ ] 39 benchmark queries → 33+ correct at Recall@1 (84.62%+)
  - [ ] 0% cross-domain contamination confirmed
  - [ ] S10 performance: 0/2 queries (expected until fine-tuning)
  - [ ] Latency: p99 < 500ms
  - [ ] No errors or exceptions in logs

- [ ] **Load Testing (Staging)**
  - [ ] Ramp up to 10 QPS → verify latency stays < 500ms p99
  - [ ] Ramp up to 50 QPS → verify no timeouts
  - [ ] Sustained 20 QPS for 1 hour → memory stable
  - [ ] Concurrent 100 clients × 100 queries → no crashes

- [ ] **Failover Testing (Staging)**
  - [ ] Primary embedding model (text-embedding-3-large) fails
  - [ ] System falls back to E5-large automatically
  - [ ] Latency increases by ~30% (acceptable)
  - [ ] Recall@1 degrades by 2-5% (acceptable)

- [ ] **UAT (User Acceptance Testing)**
  - [ ] Domain experts test S1-S4 queries (rodovia, OAE, ferrovia, metrô)
  - [ ] Domain experts test S6, S8, S9 queries (portos, saneamento, energia)
  - [ ] Verify results match expectations
  - [ ] Collect feedback on relevance, latency, usability

---

## Production Deployment (Week 3)

### Go-Live Preparation
- [ ] **Sign-offs**
  - [ ] RAG Engineering sign-off (technical readiness)
  - [ ] QA sign-off (testing complete)
  - [ ] Operations sign-off (monitoring configured)
  - [ ] MN approval (business readiness)

- [ ] **Communication**
  - [ ] Notify all stakeholders (deployment window, expected latency)
  - [ ] Prepare rollback communication (if needed)
  - [ ] Schedule post-deployment review (1 week later)

- [ ] **Backup & Recovery**
  - [ ] Supabase automated backup enabled
  - [ ] Backup verified (test restore, ensure < 1 hour RTO)
  - [ ] Rollback SQL prepared (DELETE synthetic chunks, restore old search function)
  - [ ] Rollback tested (dry-run in staging)

### Deployment Execution
- [ ] **Timing**
  - [ ] Schedule: 2026-08-15, 02:00 UTC (off-peak window)
  - [ ] Estimated duration: 30-60 minutes
  - [ ] Maintenance window announced: 30 min before → 15 min after

- [ ] **Steps**
  1. [ ] Create Supabase backup
  2. [ ] Execute rag_insert.sql (58 chunks, 31 anti-terms, 8 domain configs)
  3. [ ] Deploy search function update (contamination filter + dynamic thresholds)
  4. [ ] Deploy embedding ensemble (text-embedding-3-large + E5-large)
  5. [ ] Verify: 58 chunks inserted, 0 SQL errors, search function active
  6. [ ] Enable monitoring (S10 Recall@1, contamination, latency)
  7. [ ] Open incident ticket (MNT-2026-RAG-PHASE3-DEPLOY)
  8. [ ] Run smoke tests on production (39 queries, verify 84.62% Recall@1)
  9. [ ] Notify stakeholders (deployment successful)

### Post-Deployment Verification
- [ ] **Real-World Validation (Day 1)**
  - [ ] Monitor S10 Recall@1 (should be 0%, flagged for fine-tuning)
  - [ ] Monitor contamination rate (should be 0.00%)
  - [ ] Monitor search latency (should be < 500ms p99)
  - [ ] Monitor error rate (should be < 0.1%)
  - [ ] No customer complaints or escalations

- [ ] **Extended Monitoring (Days 2-7)**
  - [ ] Daily dashboard review (metrics + alerts)
  - [ ] Weekly performance report
  - [ ] Customer feedback collected
  - [ ] Incident ticket closed (if no issues, close after 7 days)

- [ ] **Fine-Tuning Launch (Week 4)**
  - [ ] Execute S10 fine-tuning plan (parallel effort)
  - [ ] Re-run benchmark with fine-tuned model
  - [ ] Deploy S10-optimized embeddings (hot update, no downtime)
  - [ ] Verify S10 Recall@1 improved (0% → 50-70%)

---

## Continuous Monitoring & Operations

### Dashboards
- [ ] **Real-Time Metrics Dashboard**
  - Metric: Recall@1 per domain (S1-S10)
  - Metric: Contamination rate (global + per-domain)
  - Metric: Search latency (p50, p95, p99)
  - Metric: Error rate (SQL, embedding, search)
  - Metric: Embedding cache hit rate
  - Metric: Query throughput (QPS)

- [ ] **SLA Dashboard**
  - Target: Recall@1 ≥ 80% (current: 84.62%)
  - Target: Contamination ≤ 1% (current: 0%)
  - Target: Latency p99 < 500ms
  - Target: Uptime ≥ 99.5%

- [ ] **S10 Fine-Tuning Progress Dashboard** (Post-Phase 3)
  - Target: S10 Recall@1 ≥ 50%
  - Tracking: training data collection, fine-tuning status, validation results

### Alerting
- [ ] **Critical Alerts**
  - [ ] Recall@1 < 70% (block production queries, page on-call)
  - [ ] Contamination > 5% (investigate within 1 hour)
  - [ ] Latency p99 > 1000ms (degrade to fallback model)
  - [ ] Error rate > 1% (page on-call)

- [ ] **Warning Alerts**
  - [ ] Recall@1 < 80% (investigate within 4 hours)
  - [ ] Contamination > 2% (log for trend analysis)
  - [ ] Latency p99 > 500ms (check model load)
  - [ ] S10 Recall@1 < 30% (track fine-tuning progress)

### Incident Response
- [ ] **Degradation Procedure**
  1. If Recall@1 drops below 70%:
     - Switch to E5-large fallback (single model)
     - Disable dynamic thresholds (use global 0.70 threshold)
     - Disable query expansion (use base query only)
     - Expected: Recall@1 ~75% (acceptable), resolve within 4 hours

  2. If Contamination spikes > 5%:
     - Investigate which queries are misrouted
     - Check if new domain queries added without anti-terms
     - Rollback search function if needed
     - Expected: restore within 2 hours

  3. If Latency exceeds 1000ms p99:
     - Check API quota (text-embedding-3-large)
     - Reduce batch size for embedding requests
     - Enable read-only mode (serve from cache)
     - Scale embedding service horizontally

- [ ] **Rollback Procedure**
  1. If all else fails, execute complete rollback:
     - DELETE synthetic chunks from rag_chunks
     - Revert search function to Phase 2 baseline
     - Redeploy E5-large single model
     - Expected: restore within 15 minutes

---

## Success Criteria for Production Release

✅ **Recall@1 ≥ 80%** (current: 84.62%, maintain above 80%)  
✅ **Contamination ≤ 1%** (current: 0%, alert if > 1%)  
✅ **Latency p99 < 500ms** (measure in production, baseline ~250ms)  
✅ **Uptime ≥ 99.5%** (acceptable: 1 outage per month < 1 hour)  
✅ **Zero critical incidents in first 7 days**  
✅ **S10 fine-tuning launched within 2 weeks** (Phase 3.5)

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| RAG Engineering Lead | TBD | — | 📋 Pending |
| QA Manager | TBD | — | 📋 Pending |
| Operations Lead | TBD | — | 📋 Pending |
| MN Approval | mneves@mantaassociados.com | — | 📋 Pending |

---

## Appendix: Rollout Timeline

```
Today (2026-07-26):
  - Phase 3 completed: 84.62% Recall@1, 0% contamination ✅
  - PR #32 created (draft) ✅
  - SQL migration prepared (validation fixes needed)
  - S10 fine-tuning plan documented
  - Production checklist this doc ✅

This Week (2026-07-27 to 2026-07-31):
  - Fix SQL migration word count issues
  - Execute SQL in Supabase staging
  - Run 39-query benchmark on staging
  - Load testing (up to 50 QPS)
  - UAT with domain experts

Next Week (2026-08-01 to 2026-08-07):
  - Finalize sign-offs (Eng, QA, Ops, MN)
  - Prepare communications & runbooks
  - Test rollback procedure
  - Schedule production deployment window

Week 3 (2026-08-08 to 2026-08-14):
  - Production deployment (2026-08-15, 02:00 UTC)
  - Post-deployment verification (24-48 hours)
  - Close deployment ticket
  - Launch S10 fine-tuning (parallel effort)

Week 4+ (2026-08-15+):
  - S10 fine-tuning execution (in progress)
  - Daily monitoring & incident response
  - Post-launch review (1 week later)
  - Production optimization (long-term)
```

---

**Prepared by:** Agente RAG Benchmark (Phase 3)  
**Document Status:** Ready for sign-off  
**Last Updated:** 2026-07-26
