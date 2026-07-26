# FASE 3 PRODUCTION DEPLOYMENT RUNBOOK
**Complete deployment, monitoring, and incident response documentation**

Version: 1.0.0  
Status: Ready for deployment  
Created: 2026-07-26  
Target Deployment: 2026-07-27, 02:00–06:00 UTC  

---

## 📖 DOCUMENT STRUCTURE

```
.claude/runbooks/
├── README.md (this file)
├── FASE3-PRODUCTION-DEPLOYMENT.md       ← MAIN RUNBOOK (1,500+ lines)
├── INCIDENT-RESPONSE-WORKED-EXAMPLES.md ← 3 real scenario walkthroughs
├── scripts/
│   ├── preflight-checks.sh              ← Pre-flight validation (T-48h)
│   └── rollback-fase3.sh                ← Emergency rollback automation
└── templates/
    ├── grafana-dashboard-fase3.json     ← 10-panel monitoring dashboard
    └── slack-notifications.json         ← Pre-built notification templates
```

---

## 🚀 QUICK START

### For Deployment Day (T-48h to T+240min)

**1. Read the main runbook (FASE3-PRODUCTION-DEPLOYMENT.md):**
   - Section 1: Executive Summary (overview)
   - Section 2: Pre-Deployment Checklist (48 hours before)
   - Section 3: Deployment Procedure (T0–T+4h timeline)

**2. Prepare infrastructure (T-48h):**
   ```bash
   # Run pre-flight checks
   ./runbooks/scripts/preflight-checks.sh
   ```

**3. Monitor deployment (T0–T+240min):**
   - Watch Grafana dashboard (import `templates/grafana-dashboard-fase3.json`)
   - Use Slack notifications (templates in `templates/slack-notifications.json`)

**4. If incident occurs:**
   - Consult `INCIDENT-RESPONSE-WORKED-EXAMPLES.md` for scenario-based guidance
   - Each scenario shows timeline, actions, and expected outcomes

### For 24-Hour Post-Deployment Monitoring (T0 → T+24h)

**Section 5: 24-Hour Post-Deployment Monitoring**
- Hourly metrics (ML precision, FP rate, escalations)
- 4-hour system metrics (latency, throughput, errors)
- 8-hour financial metrics (cost tracking)
- Alert thresholds and escalation criteria

### For Phase Transitions (T+24h, T+72h, T+7d)

**Section 6: Phase Transition Gates**
- Phase 0 → Phase 1 (T+24h gate)
- Phase 1 → Phase 2 (T+72h gate)
- Phase 2 → Phase 3 (T+7d gate)
- Approval criteria and deployment procedures for each phase

### If Rollback Needed

**Section 4: Rollback Procedure**
- Automatic rollback triggers (FP rate >3%, cascading failures >5, data loss)
- Manual rollback: `./scripts/rollback-fase3.sh`
- Expected rollback time: <15 minutes

---

## 📋 CHECKLIST MATRIX

### Pre-Deployment (48 hours before)

| Task | Owner | Status |
|------|-------|--------|
| Infrastructure snapshot | DevOps | [ ] |
| Database backups verified | DBA | [ ] |
| ML model weights exported | ML Eng | [ ] |
| Incident response team briefed | DevOps | [ ] |
| Rollback script tested | DevOps | [ ] |
| Monitoring alerts configured | DevOps | [ ] |
| Pre-flight checks passed | DevOps | [ ] |
| All sign-offs collected | PM | [ ] |

### Deployment Day (T0–T+240min)

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| T0–T+15min | Pre-flight checks | Network, DB, ML health | [ ] |
| T+15–T+45min | Core infrastructure | ML scoring engine | [ ] |
| T+45–T+120min | v3.0 skills (3) | 3 expanded skills deployed | [ ] |
| T+120–T+180min | Agent + monitoring | agente-gitops v3.0 + Grafana | [ ] |
| T+180–T+240min | Validation | Phase 0 complete, zero defects | [ ] |

### Post-Deployment (24 hours)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| ML Precision | ≥92% | ___% | [ ] |
| FP Rate | <3% | ___% | [ ] |
| Post-merge defects | <5% | ___% | [ ] |
| Data loss | 0 records | ___ | [ ] |
| Latency p99 | <5s | ___s | [ ] |
| Phase 0 complete | 60 min audit | ___min | [ ] |

---

## 🎯 SUCCESS CRITERIA

All of the following must be true to declare deployment successful:

- [x] **Functionality:** All 10 skills operational with <5min p99 latency
- [x] **ML Model:** Precision ≥92%, drift <2%, no false positives >3%
- [x] **Data Integrity:** Zero post-merge data loss, zero audit log gaps
- [x] **Cost:** Actual spend ≤ budget ($680–1,400/month)
- [x] **Monitoring:** Grafana dashboards active, alerts functioning
- [x] **Incident Response:** Playbooks ready, team trained
- [x] **Phase 0:** Complete 60-min audit mode with zero critical incidents
- [x] **Sign-offs:** DevOps lead, ML Engineering lead, Security officer approved

---

## 🚨 INCIDENT RESPONSE GUIDE

### If Alert Fires

**Step 1:** Identify scenario type in `INCIDENT-RESPONSE-WORKED-EXAMPLES.md`
- **Scenario A:** ML Model Drift (precision drops >2%)
- **Scenario B:** Cascading Merge Failures (>5 in 1h)
- **Scenario C:** Data Corruption (audit log gaps)

**Step 2:** Follow the worked example timeline for your scenario
- T0–T+5min: Detection & triage
- T+5–T+25min: Investigation
- T+25–T+45min: Remediation
- T+45–T+90min: Validation & recovery

**Step 3:** Use incident playbook from main runbook (Section 7)
- Actionable bash commands
- Expected outcomes
- Escalation paths

**Step 4:** If incident unresolved after MTTR target
- Consider rollback: `./scripts/rollback-fase3.sh`
- Schedule post-mortem within 4 hours

---

## 📊 MONITORING DASHBOARDS

### Grafana Dashboard Import

1. Go to Grafana → Dashboards → Import
2. Upload `templates/grafana-dashboard-fase3.json`
3. Select Prometheus datasource
4. View 10 panels:
   - ML Model Accuracy (Precision/Recall)
   - False Positive Rate
   - Post-Merge Defect Rate
   - Workflow Duration (p50/p95/p99)
   - Chaos Engineering Results
   - ML Inference Latency
   - Cost Tracking
   - Escalation Rate
   - ML Drift Detection
   - Phase Progress

---

## 💬 SLACK NOTIFICATIONS

### Pre-Built Templates

Use `templates/slack-notifications.json` for Slack messages:

- `deployment_start` — Sent at T0
- `midpoint_update` — Sent at T+2h
- `deployment_complete` — Sent at T+4h
- `incident_alert` — Sent when incident detected
- `rollback_initiated` — Sent if auto-rollback triggered
- `phase_1_gate_approval` — Sent at T+24h if approved
- `metrics_summary` — Sent at T+24h with full results

### Custom Integration

```bash
# Send notification
curl -X POST "https://hooks.slack.com/services/$SLACK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d @slack-notification.json
```

---

## 🔧 SUPPORT & ESCALATION

### On-Call Rotation
- **Primary:** DevOps lead (PagerDuty)
- **Secondary:** ML Engineering lead
- **Tertiary:** Database admin
- **Escalation:** CTO/Leadership

### Communication Channels
- **Real-time:** Slack #deployments, #incidents, #gitops
- **Dashboards:** Grafana (https://grafana.manta.internal/d/fase3-deployment)
- **Incident tracking:** PagerDuty
- **Post-incident:** GitHub issues + incident post-mortem

### Document References
- Main runbook: `FASE3-PRODUCTION-DEPLOYMENT.md`
- Incident scenarios: `INCIDENT-RESPONSE-WORKED-EXAMPLES.md`
- Scripts: `scripts/`
- Templates: `templates/`

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-26 | Initial runbook creation |

---

## 🏁 NEXT STEPS

1. **T-48h:** Run `./scripts/preflight-checks.sh`
2. **T-24h:** Conduct briefing for deployment team
3. **T0:** Begin deployment using main runbook section 3
4. **T+240min:** Start 24-hour monitoring period
5. **T+24h:** Gate review for Phase 1 approval
6. **T+72h:** Gate review for Phase 2 approval
7. **T+7d:** Gate review for Phase 3 (full deployment)

---

**Document owner:** DevOps team  
**Last updated:** 2026-07-26  
**Status:** Ready for deployment
