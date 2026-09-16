# Deployment Approvals — S6 Go-Live v5.0
**Version: v5.0 | Date: 2026-07-25 | Agent: Manta 03-S6 (Portos)**

Sign-off record for deployment phases. **All phases must be approved before proceeding to next phase.**

---

## PRE-LAUNCH APPROVALS

### Phase 0 — Pre-Flight (24h before launch)
**Approval Required:** MN (mneves@mantaassociados.com)

- [ ] **APPROVED** by _____________________ (name)
  - **Timestamp:** _____________________
  - **Channel:** (Slack / Email / Phone)
  - **Notes:** 

---

### Phase 1 — Pre-Deployment Validation (T-6h)
**Approval Required:** Tech Lead

- [ ] **Code validation:** CLAUDE.md, VERSIONS.json, settings.json syntax OK
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Database schema:** All tables exist, indexes created, RLS enabled
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **RAG collection:** `por:v5.0:chunks` has >= 2000 chunks with embeddings
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Tests passing:** All unit + integration tests >= 95% pass rate
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Backup confirmed:** v4.9 RAG, CLAUDE.md v4.2, skills v4.9 backed up
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

---

### Phase 2 — Pre-Deployment Sign-Off (T-5h)
**Approval Required:** MN

- [ ] **All Phase 1 items complete**
  - [ ] Approved by: _____________________ (name — MN)
  - [ ] Timestamp: _____________________
  - [ ] Approval method: (Email / Slack / Phone)
  - [ ] Email subject or Slack thread link: 

---

### Phase 3 — Database Migrations (T-4h)
**Approval Required:** DBA / Database Ops

- [ ] **Migrations executed successfully**
  - [ ] Migration ID: _____________________
  - [ ] Executed by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Schema integrity validated**
  - [ ] All 6 tables exist: ✓ agent_runs ✓ agent_feedback ✓ agent_triggers ✓ rag_chunks ✓ rag_metadata ✓ rag_cache
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Indexes created & performance baseline established**
  - [ ] Verified by: _____________________ (name)
  - [ ] Baseline query time (sample): _____________________ ms

---

### Phase 4 — Background Tasks Setup (T-3h)
**Approval Required:** DevOps / SRE

- [ ] **APScheduler configured & running**
  - [ ] Service: manta-scheduler (systemd / Docker)
  - [ ] Status: active (running) ✓
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **All 3 scheduled jobs registered**
  - [ ] Job 1: rag_reindex_daily (cron: 02:00 UTC)
  - [ ] Job 2: embedding_retrain_weekly (cron: Sun 03:00 UTC)
  - [ ] Job 3: memory_purge_daily (cron: 03:30 UTC)
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

---

### Phase 5 — Skill Deployment (T-2h)
**Approval Required:** Tech Lead

- [ ] **Skill file verified**
  - [ ] File: `.claude/agents/agente-portos.v5.0.md`
  - [ ] Size: >= 10KB ✓
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Checksum validated**
  - [ ] Actual MD5: _____________________
  - [ ] Expected (VERSIONS.json): _____________________
  - [ ] Match: ✓ YES ✓ NO
  - [ ] Verified by: _____________________ (name)

- [ ] **Settings.json pinning confirmed**
  - [ ] Skill pin: agente-portos = v5.0 ✓
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

---

### Phase 6 — Maestro Routing (T-1h 30m)
**Approval Required:** Tech Lead (AI/ML)

- [ ] **Keyword rules in place**
  - [ ] S6 keywords defined: {porto|terminal|ANTAQ|dragagem|molhe|...}
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Embedding model functional**
  - [ ] Model: intfloat/multilingual-e5-large-instruct ✓
  - [ ] Embedding dimension: 384 ✓
  - [ ] Test query similarity (S6 vs other agents): > 0.80 ✓
  - [ ] Verified by: _____________________ (name)

- [ ] **BM25 index operational**
  - [ ] Elasticsearch index: `por_v5.0` ✓
  - [ ] Document count: >= 2000 ✓
  - [ ] Sample query latency: _____________________ ms (target < 50ms)
  - [ ] Verified by: _____________________ (name)

---

### Phase 7 — Tiering & Fallback (T-1h)
**Approval Required:** Tech Lead (Infra)

- [ ] **Complexity score formula validated**
  - [ ] Test case 1 (Haiku route): ✓ PASS
  - [ ] Test case 2 (Sonnet route): ✓ PASS
  - [ ] Test case 3 (Opus route): ✓ PASS
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Fallback cascade tested**
  - [ ] Haiku timeout → Sonnet fallback: ✓ Works
  - [ ] Sonnet timeout → Opus fallback: ✓ Works
  - [ ] Verified by: _____________________ (name)

---

### Phase 8 — Pre-Launch Testing (T-30m)
**Approval Required:** QA Lead / Tech Lead

- [ ] **All 11 E2E tests passing**
  - [ ] Test 1 (Basic S6 routing): ✓
  - [ ] Test 2 (Phase inference): ✓
  - [ ] Test 3 (Ambiguity fallback): ✓
  - [ ] Test 4 (BM25 query): ✓
  - [ ] Test 5 (Embedding query): ✓
  - [ ] Test 6 (Reranker): ✓
  - [ ] Test 7 (Tiering Haiku): ✓
  - [ ] Test 8 (Tiering Sonnet): ✓
  - [ ] Test 9 (Tiering Opus): ✓
  - [ ] Test 10 (E2E Maestro): ✓
  - [ ] Test 11 (E2E with file): ✓
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Performance baseline established**
  - [ ] Latency p50: _____________________ ms (target < 5s)
  - [ ] Latency p95: _____________________ ms (target < 8s)
  - [ ] Throughput (5 concurrent): _____________________ req/sec
  - [ ] Verified by: _____________________ (name)

- [ ] **Monitoring ready**
  - [ ] Slack webhook configured & tested ✓
  - [ ] Grafana dashboard accessible ✓
  - [ ] Alert thresholds set ✓
  - [ ] Verified by: _____________________ (name)

---

### Phase 9 — Final Approval Gate (T-15m)
**Approval Required:** MN (Final Sign-Off)

- [ ] **ALL PHASES 1–8 COMPLETE & APPROVED**

- [ ] **MN Final Approval**
  - [ ] Approved by: _____________________ (name — MUST be MN)
  - [ ] Timestamp: _____________________
  - [ ] Approval method: (Email / Slack / Phone)
  - [ ] Escalation contact confirmed (phone): _____________________
  - [ ] Incident response team on standby: ✓ YES

- [ ] **Go-Live Authorization:**
  - [ ] ✅ **AUTHORIZED TO PROCEED TO LAUNCH (T+0)**
  - [ ] ❌ **BLOCKED — Reason:** _________________________________

---

## LAUNCH & POST-LAUNCH APPROVALS

### Phase 10 — Go-Live (T+0)
**Decision Maker:** On-Call Engineer + MN

- [ ] **Pre-Flight Checks (5 min before)**
  - [ ] Health check: ✓ All green
  - [ ] Slack announcement posted: ✓ Yes
  - [ ] Background tasks paused: ✓ Yes
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **Deployment Executed (10 min)**
  - [ ] Git merge to main: ✓ Complete
  - [ ] Settings.json S6 enabled: ✓ Yes
  - [ ] Scheduler resumed: ✓ Running
  - [ ] Deployed by: _____________________ (name)
  - [ ] Timestamp: _____________________
  - [ ] Git commit SHA: _____________________

- [ ] **Warmup Queries (3 requests)**
  - [ ] Warmup 1: ✓ SUCCESS
  - [ ] Warmup 2: ✓ SUCCESS
  - [ ] Warmup 3: ✓ SUCCESS
  - [ ] Verified by: _____________________ (name)

- [ ] **Launch Confirmation (5 min)**
  - [ ] Routing accuracy >= 75%: ✓ YES
  - [ ] Error rate <= 1%: ✓ YES
  - [ ] Latency p95 < 8s: ✓ YES
  - [ ] Slack announcement (LIVE): ✓ Posted
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

---

### Phase 11–13 — Post-Launch Monitoring (T+1h to T+24h)

*(Recorded in POST-LAUNCH-MONITORING.md Daily Report)*

- [ ] **T+1h Check**
  - [ ] Metrics normal: ✓ YES
  - [ ] Verified by: _____________________ (name)
  - [ ] Timestamp: _____________________

- [ ] **T+6h Check**
  - [ ] Cost trend: On track ✓ / Over-budget ❌
  - [ ] Feedback scores: > 3.5 avg ✓ / Below ❌
  - [ ] Verified by: _____________________ (name)

- [ ] **T+24h Decision Gate**
  - [ ] Continue production: ✓ YES
  - [ ] Monitor longer: ❓ MONITOR
  - [ ] Rollback: ❌ NO (if yes, see ROLLBACK-PLAN.md)
  - [ ] Decided by: _____________________ (name — MN)
  - [ ] Timestamp: _____________________

---

## CONTINGENCY APPROVALS

### Rollback Decision (If Triggered)
**Approval Required:** MN (Immediate)

- [ ] **Rollback Initiated** (see S6-ROLLBACK-PLAN.md)
  - [ ] Reason: _________________________________
  - [ ] Decided by: _____________________ (name — MN)
  - [ ] Timestamp: _____________________
  - [ ] RTO start: _____________________

- [ ] **Rollback Complete**
  - [ ] RTO end: _____________________
  - [ ] Duration: _____________________ min (target < 60)
  - [ ] Verified by: _____________________ (name)
  - [ ] Status: ✓ Production restored

---

## ISSUE LOG

**Any issues found during deployment?**

| Issue | Severity | Resolution | Status |
|-------|----------|-----------|--------|
| [Fill if issues arise] | 🔴/🟡 | [How resolved] | ✓/❌ |
| | | | |

---

## SIGN-OFF

**Deployment Lead:** _____________________  
**Tech Lead:** _____________________  
**DBA/DevOps:** _____________________  
**MN (Final):** _____________________  

**Overall Status:**
- ✅ **APPROVED FOR PRODUCTION**
- 🔄 **PENDING APPROVALS** (phases: _______________)
- ❌ **BLOCKED** (reason: ______________)

**Date Completed:** _____________________  
**Time to Completion:** _____________________ hours

---

**End of Deployment Approvals**
