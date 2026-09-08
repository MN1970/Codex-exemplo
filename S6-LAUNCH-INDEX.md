# S6 Launch Documentation Index
**Version: v5.0 | Agent: Manta 03-S6 (Portos) | Launch Date: 2026-07-25**

Complete guide to all S6 go-live and post-launch documentation. **Start here.**

---

## QUICK START (READ IN THIS ORDER)

### Before Launch (T-24h to T+0)

1. **[S6-GO-LIVE-CHECKLIST.md](./S6-GO-LIVE-CHECKLIST.md)** ⭐ PRIMARY
   - **What:** 127-item checklist across 20 deployment phases
   - **When:** T-24h through T+0 (4–6 hours total)
   - **Who:** Tech Lead, DevOps, QA, MN
   - **Key sections:** Phase 0 (pre-flight) → Phase 10 (go-live)
   - **Output:** Green checkmarks on all phases before launch
   - **Time to read:** 30 min (skim before, refer during launch)

2. **[S6-GO-LIVE-RUNBOOK.md](./S6-GO-LIVE-RUNBOOK.md)** ⭐ DURING LAUNCH
   - **What:** Interactive decision tree + troubleshooting commands
   - **When:** T-6h to T+24h (have open during entire window)
   - **Who:** On-Call Engineer, Tech Lead
   - **Key sections:** Decision tree, 17 ACTION items with code
   - **Use case:** "What do I do if routing accuracy drops?" → Look up ACTION 12A
   - **Time to read:** 20 min (reference, not cover-to-cover)

3. **[S6-ROLLBACK-PLAN.md](./S6-ROLLBACK-PLAN.md)** 🚨 EMERGENCY ONLY
   - **What:** Step-by-step rollback procedure, < 60 min RTO
   - **When:** Only if critical incident triggered
   - **Who:** MN, Tech Lead, DBA
   - **Key sections:** 8 rollback steps, contingency approvals
   - **RTO:** < 60 minutes guaranteed
   - **Time to read:** 15 min (skim before, execute if needed)

### Administration & Approvals

4. **[.github/DEPLOYMENT-APPROVALS.md](./.github/DEPLOYMENT-APPROVALS.md)** 📋 SIGN-OFF
   - **What:** Sign-off template for all 13 phases
   - **When:** Fill during deployment (each phase needs approval)
   - **Who:** Phase leads (MN, Tech Lead, DBA, DevOps)
   - **Key sections:** Pre-launch, launch, post-launch approval gates
   - **Output:** Completed sign-offs for audit trail
   - **Time to read:** 5 min (reference for sign-offs)

### After Launch (T+1h through T+30d)

5. **[docs/S6-POST-LAUNCH-MONITORING.md](./docs/S6-POST-LAUNCH-MONITORING.md)** 📊 DAILY REFERENCE
   - **What:** Grafana alerts, Slack integration, daily report template
   - **When:** T+1h through T+30d (post-launch monitoring)
   - **Who:** DevOps, Tech Lead, MN (for daily reports)
   - **Key sections:** 7 Grafana panels, 8 alert rules, daily report template
   - **Frequency:** Daily (09:00 UTC) + weekly summaries
   - **Time to read:** 20 min (understand structure, then refer daily)

### Infrastructure Setup

6. **[SLACK-CHANNEL-SETUP.md](./SLACK-CHANNEL-SETUP.md)** 💬 INFRASTRUCTURE
   - **What:** Setup Slack channels, webhooks, alerts
   - **When:** T-24h (before launch)
   - **Who:** DevOps/SRE, Communications
   - **Key sections:** 10-step setup (channels, webhooks, alerts, schedules)
   - **Output:** 3 Slack channels live, alerts firing
   - **Time to read:** 15 min (execute step-by-step)

---

## DOCUMENT MAP (Full Index)

```
S6 Launch Documentation/
│
├── 🚀 GO-LIVE (Launch Day T-6h to T+0)
│   ├── S6-GO-LIVE-CHECKLIST.md        [127 items, 20 phases]
│   ├── S6-GO-LIVE-RUNBOOK.md          [Decision tree + actions]
│   └── S6-ROLLBACK-PLAN.md            [Emergency procedures]
│
├── 📋 APPROVALS & GOVERNANCE
│   ├── .github/DEPLOYMENT-APPROVALS.md [Sign-offs per phase]
│   └── CLAUDE.md                       [Architecture v5.0 reference]
│
├── 📊 POST-LAUNCH (T+1h through T+30d)
│   ├── docs/S6-POST-LAUNCH-MONITORING.md [Alerts, reports, dashboards]
│   └── docs/S6-DAILY-REPORT-TEMPLATE.md  [Auto-generated daily]
│
├── 💬 INFRASTRUCTURE
│   ├── SLACK-CHANNEL-SETUP.md         [Channels, webhooks, alerts]
│   └── S6-LAUNCH-INDEX.md             [THIS FILE]
│
└── 📚 REFERENCE
    ├── VERSIONS.json                  [Skill checksums]
    ├── .claude/agents/agente-portos.v5.0.md
    └── .claude/agents/maestro.v5.0.md
```

---

## TIMELINE & DOCUMENT USAGE

```
T-24h (Day before)
├─ READ: S6-GO-LIVE-CHECKLIST.md (30 min, understand phases)
├─ READ: SLACK-CHANNEL-SETUP.md (15 min, execute setup)
├─ EXECUTE: Create Slack channels, webhooks
└─ OUTPUT: .github/DEPLOYMENT-APPROVALS.md Phase 0 signed off

T-6h (Morning of launch)
├─ READ: S6-GO-LIVE-RUNBOOK.md (20 min, understand decision tree)
├─ EXECUTE: S6-GO-LIVE-CHECKLIST.md Phases 1–9
├─ REFERENCE: S6-GO-LIVE-RUNBOOK.md for troubleshooting
└─ OUTPUT: .github/DEPLOYMENT-APPROVALS.md Phases 1–9 signed off

T+0 (Launch!)
├─ EXECUTE: S6-GO-LIVE-CHECKLIST.md Phase 10 (deployment)
├─ REFERENCE: S6-GO-LIVE-RUNBOOK.md (have open, watch for issues)
├─ SLACK: Post status updates to #s6-launch (auto or manual)
└─ OUTPUT: Phase 10 signed off, deployment complete

T+1h to T+6h (Ramp-up)
├─ MONITOR: Grafana dashboard (8 panels, real-time metrics)
├─ WATCH: Slack alerts in #agent-ops (automated)
├─ REFERENCE: S6-GO-LIVE-RUNBOOK.md if action needed
└─ DECISION: If critical issue → trigger S6-ROLLBACK-PLAN.md

T+6h to T+24h (Stabilization)
├─ MONITOR: Continued Grafana + Slack
├─ PREPARE: Daily report (using template from docs/S6-POST-LAUNCH-MONITORING.md)
├─ DECIDE: T+24h go/no-go gate
└─ OUTPUT: First daily report sent to @mantaassociados.com

T+1d to T+7d (Observation)
├─ EXECUTE: Daily report generation (09:00 UTC)
├─ REVIEW: Metrics vs targets
├─ DECIDE: T+7d go/no-go gate (promote to GA or continue monitoring)
└─ OUTPUT: Weekly summary report

T+7d onwards (Normal Operations)
├─ MONITOR: 2x daily check (morning + evening)
├─ REPORT: Weekly summaries
└─ MAINTAIN: Post-launch optimization (tiering tuning, etc.)
```

---

## WHO SHOULD READ WHAT

### MN (Decision Maker)
- ✅ S6-GO-LIVE-CHECKLIST.md (phases 0, 2, 9 only)
- ✅ S6-GO-LIVE-RUNBOOK.md (skim decision tree)
- ✅ .github/DEPLOYMENT-APPROVALS.md (sign-offs)
- ✅ S6-ROLLBACK-PLAN.md (once before launch, in case)
- ✅ docs/S6-POST-LAUNCH-MONITORING.md (daily reports)

### Tech Lead
- ✅ S6-GO-LIVE-CHECKLIST.md (full read, then reference)
- ✅ S6-GO-LIVE-RUNBOOK.md (full read, open during launch)
- ✅ .github/DEPLOYMENT-APPROVALS.md (sign-offs for phases they lead)
- ✅ docs/S6-POST-LAUNCH-MONITORING.md (oversee alerts, approve reports)
- ✅ S6-ROLLBACK-PLAN.md (emergency, read before launch)

### DevOps/SRE
- ✅ S6-GO-LIVE-CHECKLIST.md (phases 3–7, full details)
- ✅ S6-GO-LIVE-RUNBOOK.md (open during launch for troubleshooting)
- ✅ SLACK-CHANNEL-SETUP.md (execute all 10 steps)
- ✅ docs/S6-POST-LAUNCH-MONITORING.md (manage dashboards, alerts)
- ✅ S6-ROLLBACK-PLAN.md (own execution if triggered)

### QA/Test Lead
- ✅ S6-GO-LIVE-CHECKLIST.md (phases 8, focus on tests)
- ✅ S6-GO-LIVE-RUNBOOK.md (skim for context)
- ✅ .github/DEPLOYMENT-APPROVALS.md (phase 8 sign-offs)

### On-Call Engineer (Launch Day)
- ✅ S6-GO-LIVE-RUNBOOK.md (full read, keep open all day)
- ✅ S6-GO-LIVE-CHECKLIST.md (reference during execution)
- ✅ S6-ROLLBACK-PLAN.md (emergency procedure)
- ✅ SLACK-CHANNEL-SETUP.md (understand channels)
- 📱 Have MN phone number ready

### DBA
- ✅ S6-GO-LIVE-CHECKLIST.md (phases 3–4, database focus)
- ✅ S6-ROLLBACK-PLAN.md (STEP 4: database restore)
- ✅ docs/S6-POST-LAUNCH-MONITORING.md (DB health checks)

---

## KEY ARTIFACTS GENERATED DURING DEPLOYMENT

| Phase | Document | Owner | Output |
|-------|----------|-------|--------|
| Phase 0 | .github/DEPLOYMENT-APPROVALS.md | MN | ✓ Pre-flight approved |
| Phase 1–9 | .github/DEPLOYMENT-APPROVALS.md | Tech Lead | ✓ All phases signed |
| Phase 10 | .github/DEPLOYMENT-APPROVALS.md | On-Call | ✓ Deployment complete |
| T+1d | S6 Daily Report | DevOps | ✓ Report → email + Slack |
| T+7d | S6 Weekly Summary | MN | ✓ Summary → decision gate |
| If rollback | ROLLBACK_LOG.md | Tech Lead | ✓ Post-mortem + timeline |

---

## CRITICAL DECISION GATES (Go/No-Go)

### T+0 (Launch Authorization)
**Decision:** Approve deployment  
**Decision Maker:** MN  
**Reference:** .github/DEPLOYMENT-APPROVALS.md PHASE 9  
**Condition:** All phases 1–8 complete and signed off

### T+24h (Continue or Monitor Longer)
**Decision:** Keep in production or investigate further  
**Decision Maker:** MN + Tech Lead  
**Reference:** docs/S6-POST-LAUNCH-MONITORING.md (Daily Report)  
**Go if:** Routing >= 75%, Error <= 2%, Latency p95 < 10s  
**No-Go if:** Any metric fails 2x consecutive hours

### T+7d (GA Promotion or Rollback)
**Decision:** Promote to GA, continue monitoring, or rollback  
**Decision Maker:** MN  
**Reference:** docs/S6-POST-LAUNCH-MONITORING.md (Weekly Summary)  
**Go if:** 7-day avg routing >= 85%, feedback >= 3.8/5, no 🔴 CRITICAL incidents  
**No-Go if:** Any metric consistently below threshold

### Emergency (Anytime)
**Decision:** Immediate rollback  
**Decision Maker:** MN or on-call if MN unavailable  
**Reference:** S6-ROLLBACK-PLAN.md  
**Trigger:** Routing < 60%, Error > 10%, DB unavailable, security breach  
**RTO:** < 60 minutes

---

## QUICK REFERENCE CARDS

### Pre-Launch Checklist (T-6h to T+0)
```
☐ Phase 1: Pre-deployment validation (code, DB, RAG, tests)
☐ Phase 2: Pre-deployment sign-off (MN approval)
☐ Phase 3: Database migrations (6 tables, indexes, RLS)
☐ Phase 4: APScheduler setup (3 jobs registered)
☐ Phase 5: Skill deployment (checksum validated)
☐ Phase 6: Maestro routing (keyword rules, embedding, BM25)
☐ Phase 7: Tiering & fallback (formula tested, cascade works)
☐ Phase 8: Pre-launch testing (11 E2E tests passing)
☐ Phase 9: Final approval gate (MN sign-off)
☐ Phase 10: Go-live (merge, deploy, warmup, validate)
```

### Launch Day Actions (T+0)
```
1. Start monitoring: Open Grafana dashboard in browser
2. Open runbook: S6-GO-LIVE-RUNBOOK.md (decision tree)
3. Slack ready: Join #s6-launch and #agent-ops channels
4. Decision tree: Follow T+0 branch (warmup, validation, confirmation)
5. Reports: Post status updates to Slack every 30 min for first 6h
6. Escalate: Any CRITICAL condition → phone MN immediately
```

### Troubleshooting Quick Links
```
Routing accuracy low?      → ACTION 12A (S6-GO-LIVE-RUNBOOK.md)
Error rate high?           → ACTION 13A/13B (runbook)
Latency spike?             → ACTION 14A (runbook, disable reranker)
Cost anomaly?              → ACTION 16 (runbook)
Low user feedback?         → ACTION 17 (runbook)
Database issue?            → ROLLBACK-PLAN.md STEP 4
Scheduler down?            → ACTION 4 (runbook)
Need to rollback?          → S6-ROLLBACK-PLAN.md (8 steps, < 60 min)
```

---

## DOCUMENT STATS

| Document | Size | Pages | Items | Read Time |
|----------|------|-------|-------|-----------|
| S6-GO-LIVE-CHECKLIST.md | 42 KB | 20 | 127 | 30 min |
| S6-GO-LIVE-RUNBOOK.md | 22 KB | 15 | 17 actions | 20 min |
| S6-ROLLBACK-PLAN.md | 16 KB | 10 | 8 steps | 15 min |
| .github/DEPLOYMENT-APPROVALS.md | 12 KB | 8 | 13 phases | 5 min |
| docs/S6-POST-LAUNCH-MONITORING.md | 28 KB | 18 | 6 dashboards | 20 min |
| SLACK-CHANNEL-SETUP.md | 18 KB | 12 | 10 steps | 15 min |
| **TOTAL** | **138 KB** | **83** | **~180** | **~105 min** |

---

## FILE LOCATIONS (Copy URLs from here)

```bash
# In repo root:
S6-GO-LIVE-CHECKLIST.md
S6-GO-LIVE-RUNBOOK.md
S6-ROLLBACK-PLAN.md
SLACK-CHANNEL-SETUP.md
S6-LAUNCH-INDEX.md

# In .github/:
.github/DEPLOYMENT-APPROVALS.md

# In docs/:
docs/S6-POST-LAUNCH-MONITORING.md

# Reference files (already in repo):
CLAUDE.md
VERSIONS.json
.claude/agents/agente-portos.v5.0.md
.claude/agents/maestro.v5.0.md
```

---

## COMMUNICATION DISTRIBUTION

### Email Notifications (T-24h, T-6h, T+0, T+24h)

**Recipients:** @mantaassociados.com (core team)

**Subject lines:**
```
T-24h: "[GO-LIVE] Manta 03-S6 Agente-Portos v5.0 — Launch in 24 hours"
T-6h:  "[GO-LIVE] S6 Launch TODAY at 08:00 UTC"
T+0:   "[LIVE] Manta 03-S6 Agente-Portos v5.0 is now in production"
T+24h: "[REPORT] S6 Daily Status — All systems nominal"
```

### Slack Channels
```
#agent-ops        ← Real-time alerts, incidents
#s6-launch        ← Launch day updates, status
#s6-monitoring    ← Daily reports, long-term health
```

### Internal Wiki / Shared Drive
```
Link to this index (S6-LAUNCH-INDEX.md)
Link to all 6 documents (in order)
Updated daily with latest report link
```

---

## SUCCESS CRITERIA (By Phase)

| Phase | Success = | Evidence |
|-------|-----------|----------|
| Pre-launch | All 127 checklist items ✓ | Signed checklist |
| Launch | Deployment complete, metrics normal | Git commit + Slack confirmation |
| T+24h | Routing >= 75%, Error < 2%, Latency < 10s | Daily report metrics |
| T+7d | Routing >= 85%, Feedback >= 3.8/5 | Weekly report + go/no-go decision |
| T+30d | Stable production, no 🔴 incidents | Monthly summary ready for GA promotion |

---

## SUPPORT & ESCALATION

**In case of questions before launch:**
- Email: mneves@mantaassociados.com
- Slack: @mneves (DM)
- Phone: [Fill in from emergency contacts in SLACK-CHANNEL-SETUP.md]

**During launch (T+0 to T+6h):**
- On-Call Engineer: Check S6-GO-LIVE-RUNBOOK.md
- Tech Lead: Oversee runbook execution
- MN: Available for critical decisions (phone on)

**Post-launch (T+1d onwards):**
- Daily reports → email to MN
- Weekly decisions → recorded in DEPLOYMENT-APPROVALS.md
- Issues → track in ROLLBACK_LOG.md (if applicable)

---

## NEXT STEPS (After Launch)

1. **T+1d:** Review first daily report, confirm metrics OK
2. **T+7d:** Weekly go/no-go decision (continue or promote to GA)
3. **T+30d:** Consider full GA promotion
4. **Ongoing:** Monitor cost, optimize tiering weights (R7), retrain embedding (R9)

---

## SIGN-OFF

**Documentation Prepared:** Claude AI (Codex-exemplo Agent)  
**Date:** 2026-07-25  
**Reviewed by:** _____________________ (Tech Lead)  
**Approved by:** _____________________ (MN)  

**All documentation ready for launch:** ✅ YES

---

**End of S6 Launch Documentation Index**

---

## HOW TO USE THIS INDEX

1. **Bookmark this page** (S6-LAUNCH-INDEX.md)
2. **Print or save the Timeline section** (for quick reference)
3. **Read documents in the "QUICK START" order** (before T-6h)
4. **Have these 3 open on launch day:**
   - S6-GO-LIVE-CHECKLIST.md (checklist progress)
   - S6-GO-LIVE-RUNBOOK.md (decision tree)
   - Slack #s6-launch channel (status updates)
5. **Post-launch:** Use S6-POST-LAUNCH-MONITORING.md for daily reports

**Estimated total read time (all docs): 105 minutes**  
**Recommended distribution: 30 min before (checklist), 20 min day-of (runbook), 15 min async (others)**
