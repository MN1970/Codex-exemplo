# Slack Channel Setup — S6 Launch & Monitoring
**Version: v5.0 | Date: 2026-07-25 | Owner: mneves@mantaassociados.com**

Complete guide to configure Slack channels and integrations for S6 go-live launch day and post-launch monitoring.

---

## STEP 1 — CREATE SLACK CHANNELS (T-24h)

### Main Channels

#### 1.1 — #agent-ops (Existing or Create)
**Purpose:** Real-time operational alerts, go-live status, incident management  
**Visibility:** Private (invite core team only)  
**Members:** MN, Tech Lead, DevOps/SRE, DBA, On-Call Engineer, QA Lead

**Setup:**
```
1. Go to Slack Workspace > Channels
2. Create or select #agent-ops
3. Set description: "Manta Agent Ops — Real-time alerts, go-live status, incidents"
4. Set topic: "S6 Launch 2026-07-25 | Runbook: S6-GO-LIVE-RUNBOOK.md"
5. Make private: ☑ Private channel
6. Add members: (list above)
```

#### 1.2 — #s6-launch (Create)
**Purpose:** S6-specific launch coordination and updates  
**Visibility:** Private (same members as #agent-ops + stakeholders)  
**Members:** All above + Product Manager, Solution Architect

**Setup:**
```
1. Create new private channel: #s6-launch
2. Description: "Manta 03-S6 (Portos) Launch Coordination"
3. Topic: "Go-Live: 2026-07-25 08:00 UTC | Status: PENDING"
4. Pin key documents (see step below)
```

#### 1.3 — #s6-monitoring (Create, Optional)
**Purpose:** Post-launch metrics, daily reports, long-term health  
**Visibility:** Private or shared (if want broader visibility)  
**Members:** DevOps, Tech Lead, MN

**Setup:**
```
1. Create: #s6-monitoring
2. Description: "S6 Metrics, Daily Reports, Grafana Dashboards"
3. Enable threading to keep messages organized
```

---

## STEP 2 — PIN CRITICAL DOCUMENTS (T-12h)

### In #s6-launch (Pin these)

1. **Checklist Link**
   ```
   📋 S6-GO-LIVE-CHECKLIST.md
   GitHub link or internal wiki link
   ```

2. **Runbook Link**
   ```
   🚀 S6-GO-LIVE-RUNBOOK.md (Decision Tree)
   Quick reference for launch day decisions
   ```

3. **Rollback Plan Link**
   ```
   🔄 S6-ROLLBACK-PLAN.md (< 1h RTO)
   Only use if incident triggered
   ```

4. **Timeline**
   ```
   ⏱️ LAUNCH TIMELINE
   T-6h: Pre-deployment validation
   T-5h: MN sign-off
   T-4h: Database migrations
   ...
   T+0: GO-LIVE
   T+1h: Immediate monitoring
   T+24h: Daily report
   ```

5. **Emergency Contacts**
   ```
   🚨 INCIDENT RESPONSE
   MN: @mneves (SMS: +XX-XXXX-XXXX)
   Tech Lead: @[name]
   On-Call: @[current on-call engineer]
   ```

---

## STEP 3 — CONFIGURE INCOMING WEBHOOKS (T-12h)

### Slack Webhook Setup

**1. Get Webhook URL from Slack**
```
1. Go to Slack Workspace > Settings > App Management
2. Search "Incoming Webhooks"
3. Install or configure
4. Click "Add New Webhook to Workspace"
5. Select channel: #agent-ops
6. Copy the Webhook URL:
   https://hooks.slack.com/services/TXXX/BXXX/XXXX
```

**2. Configure in System**
```bash
# Add to .env file
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/TXXX/BXXX/XXXX"

# Or add to settings.json
jq '.slack_webhook_url = "https://hooks.slack.com/services/TXXX/BXXX/XXXX"' \
  .claude/settings.json > .claude/settings.json.tmp && mv .claude/settings.json.tmp .claude/settings.json

# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "✅ Slack webhook active — S6 monitoring ready",
    "blocks": [{
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*S6 Webhook Test*\nIntegration: ✓ OK"}
    }]
  }'
```

**3. Verify in Slack**
- Check #agent-ops for test message: "✅ Slack webhook active"
- If no message, check Webhook URL is correct

---

## STEP 4 — GRAFANA DASHBOARD LINK (T-8h)

**1. Create/Verify Grafana Dashboard**
```
1. Go to Grafana: http://grafana.manta.local
2. Create new dashboard: "S6 Portos Overview"
3. Add 7 panels (see POST-LAUNCH-MONITORING.md):
   - Routing Accuracy
   - Error Rate
   - Latency Percentiles
   - Model Tier Distribution
   - Cost Trend
   - Feedback Scores
   - System Health
```

**2. Share Dashboard Link in Slack**
```
Post in #s6-launch:

📊 **Grafana Dashboard Live**
URL: http://grafana.manta.local/d/s6-portos-overview
Refresh: Auto (30s)
Alerts: Configured (see #agent-ops for notifications)
```

---

## STEP 5 — SCHEDULED STATUS UPDATES (T-4h)

### Setup Slack Reminders (If Slack app installed)

**Launch Day (T+0 to T+6h) — Every 30 min status update**

```
1. Create scheduled message template:

📍 **S6 Status Update — [TIME]**

✅ Metrics:
  • Routing accuracy: [X]%
  • Error rate: [Y]%
  • Latency p95: [Z]s
  • Active runs: [N]

🔧 Actions taken: [summary]

⚠️ Issues: [if any]

Next update: [time + 30 min]

---

2. Post manually at T+0, T+30m, T+1h, T+1.5h, T+2h, T+2.5h, T+3h
   (or configure automated Grafana reports)
```

**Post-Launch (T+6h through T+24h) — Hourly**

```
Post to #s6-monitoring:
  • Metrics summary
  • Any alerts triggered
  • Actions taken
```

---

## STEP 6 — ALERT CONFIGURATION (T-8h)

### Grafana Alert Rules → Slack

**1. In Grafana, configure notification channel**
```
1. Admin > Channels > New Channel
2. Type: Slack
3. Name: manta-agent-ops
4. Webhook URL: [paste from STEP 3]
5. Channel: #agent-ops
6. Username: grafana-alerts
7. Icon: 🚨
8. Test: Send Test Alert
```

**2. Create Alert Rule for Each Metric**

**Alert: Routing Accuracy < 70%**
```
Name: S6 Routing Accuracy Low
Condition: agent_runs WHERE agent_id='manta-03-s6' 
           AND routing_accuracy < 0.70 for 5 minutes
Severity: CRITICAL 🔴
Notification: #agent-ops
Action: Auto-mention @mneves at 10 min
Message template:
"🚨 S6 Routing accuracy: 68% (target: 75%). Investigate keyword rules."
```

**Alert: Error Rate > 5%**
```
Name: S6 Error Rate High
Condition: error_count / total_count > 0.05 for 10 min
Severity: CRITICAL 🔴
Notification: #agent-ops
Auto-mention: @mneves at 5 min
```

**Alert: Latency p95 > 15s**
```
Name: S6 Latency Spike
Condition: PERCENTILE_CONT(0.95) OF latency_ms > 15000 for 5 min
Severity: HIGH 🟡
Notification: #agent-ops
Auto-mention: @tech-lead
```

**Alert: Cost Anomaly**
```
Name: S6 Cost Spike
Condition: AVG(cost_usd) > 3 × baseline for 1 hour
Severity: HIGH 🟡
Notification: #agent-ops
Async-mention: @mneves (not urgent)
```

**Alert: Scheduler Down**
```
Name: Scheduler Heartbeat Lost
Condition: Last heartbeat > 5 min ago
Severity: CRITICAL 🔴
Notification: #agent-ops
Auto-call: @mneves
```

---

## STEP 7 — SLACK COMMANDS (OPTIONAL, T-6h)

**If Slack Apps enabled, create custom commands for quick access:**

### Command: /s6-status
```
Returns: Last hour metrics
Output: Routing accuracy, error rate, latency, cost
```

### Command: /s6-rollback
```
Initiates rollback approval workflow
Requires: MN approval
Triggers: S6-ROLLBACK-PLAN.md
```

### Command: /s6-dashboard
```
Returns: Link to Grafana + recent alerts
```

---

## STEP 8 — LAUNCH DAY SLACK SEQUENCE (T+0)

### T-30 min (30 min before launch)
**Post in #s6-launch:**
```
🚀 **S6 LAUNCH IN 30 MINUTES**

📍 Timeline:
  • T-30m: Final health checks
  • T-15m: Team confirmation
  • T+0: Deployment
  • T+15m: Validation
  • T+30m: All-clear status

🔗 Resources:
  • Checklist: [link]
  • Runbook: [link]
  • Dashboard: [link]

👥 Team:
  • Lead: @[name]
  • MN on-call: @mneves
  • Incident escalation active ✓

React with ✓ to confirm readiness
```

### T+0 (Go-Live)
**Post in #s6-launch:**
```
🚀 **S6 IS LIVE**

⏱️ Deployment started: 2026-07-25T08:00:00Z
Status: 🟡 DEPLOYING

Next status update in 5 minutes...
```

### T+5 min
**Post in #s6-launch:**
```
✅ **Warmup queries successful**

Metrics (first 5 min):
  • Routing accuracy: 89%
  • Error rate: 0.2%
  • Latency p95: 3.8s

Next check: T+15 min
```

### T+15 min
**Post in #s6-launch:**
```
📊 **METRICS CHECK #1 (T+15m)**

✅ Routing accuracy: 87% (target >= 75%)
✅ Error rate: 0.6% (target < 1%)
✅ Latency p95: 4.1s (target < 8s)

Status: 🟢 NOMINAL
Next check: T+30 min
```

### T+30 min
**Post in #s6-launch:**
```
✅ **S6 LAUNCH CONFIRMED**

Launch window: COMPLETE ✓
Duration: 30 minutes
Status: 🟢 ALL SYSTEMS GO

Final metrics:
  • Routing: 86.5% accuracy
  • Error rate: 0.7%
  • Latency: p95 = 4.3s
  • Cost trend: On track

Next phase: Post-launch monitoring (see #s6-monitoring)
```

---

## STEP 9 — POST-LAUNCH DAILY REPORTS (T+1d)

**Schedule:** 09:00 UTC daily (auto-post or manual)

**Post to #s6-monitoring:**
```
📈 **S6 Daily Report — [DATE]**

[24-hour metrics summary]
• Routing accuracy: 86.2%
• Error rate: 0.8%
• Latency p95: 4.5s
• Feedback score: 4.0/5
• Cost: $489 (24h)
• Uptime: 99.8%

Status: ✅ HEALTHY

Incidents: None 🟢

Recommendations: [if any]

[Link to full report in Google Drive / Wiki]
```

---

## STEP 10 — WEEKLY SUMMARY (T+7d)

**Post to #s6-monitoring:**
```
📊 **S6 Weekly Summary — Week 1**

7-Day Metrics:
  • Avg routing accuracy: 86.2%
  • Avg error rate: 0.9%
  • Total runs: 8,647
  • Total cost: $3,456 ($494/day)
  • Avg feedback: 4.0/5

Status: ✅ HEALTHY

Incidents: 2 🟡 (both resolved < 30 min)

Go/No-Go Decision: ✅ CONTINUE IN PRODUCTION

Next week actions:
  1. Monitor cost trend (60% above v4.9)
  2. Schedule embedding retrain (R9)
  3. Plan tiering optimization test

[Full report link]
```

---

## CHECKLIST: SLACK SETUP COMPLETE

**T-24h:**
- [ ] #agent-ops channel exists, members invited
- [ ] #s6-launch channel created, members invited
- [ ] Key documents pinned in #s6-launch

**T-12h:**
- [ ] Slack Webhook URL obtained
- [ ] Webhook tested (message received in #agent-ops)
- [ ] .env or settings.json updated with webhook URL

**T-8h:**
- [ ] Grafana dashboard created & shared
- [ ] Alert rules configured in Grafana (5+ rules)
- [ ] Notification channel linked to #agent-ops

**T-6h:**
- [ ] Slack commands configured (optional but recommended)
- [ ] Emergency contacts pinned in #s6-launch
- [ ] Status update templates prepared

**T-4h:**
- [ ] Final Slack test: Post test alert
- [ ] Verify #agent-ops receives alert
- [ ] Team confirms Slack notifications working

**T+0:**
- [ ] Launch day message posted to #s6-launch
- [ ] Monitoring active, alerts firing correctly
- [ ] Daily report process tested

---

## EXAMPLE SLACK ALERT PAYLOADS

### Example 1: Routing Accuracy Low Alert
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "🚨 S6 Routing Accuracy Low"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Metric*\nRouting Accuracy"},
        {"type": "mrkdwn", "text": "*Current*\n68% (target: 75%)"},
        {"type": "mrkdwn", "text": "*Duration*\n5 minutes"},
        {"type": "mrkdwn", "text": "*Severity*\n🔴 CRITICAL"}
      ]
    },
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*Possible Causes:*\n• Keyword rules incomplete\n• Embedding model stale\n• BM25 index not updated\n\n*Action Required:*\nSee runbook ACTION 12A"}
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "View Dashboard"}, "url": "http://grafana.manta.local/d/s6-portos-overview", "style": "danger"},
        {"type": "button", "text": {"type": "plain_text", "text": "Run Diagnostics"}, "url": "..."},
        {"type": "button", "text": {"type": "plain_text", "text": "Runbook"}, "url": "..."}
      ]
    },
    {
      "type": "context",
      "elements": [{"type": "mrkdwn", "text": "_Alert at 2026-07-25T14:30:00Z | Will escalate to @mneves in 5 minutes if not resolved_"}]
    }
  ]
}
```

### Example 2: All-Clear Status
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "✅ S6 Launch Successful"}
    },
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "Manta 03-S6 (Portos) v5.0 is now in production.\n\n*Metrics (T+30m):*\n• Routing: 86.5% accuracy ✓\n• Error rate: 0.7% ✓\n• Latency: p95 = 4.3s ✓\n• Uptime: 100% ✓"}
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "View Live Dashboard"}, "url": "...", "style": "primary"}
      ]
    }
  ]
}
```

---

## SLACK BOT MESSAGE SCHEDULE (Optional Automation)

**If want fully automated daily posts, use Slack Workflow Builder:**

1. **Trigger:** Scheduled (Daily 09:00 UTC)
2. **Action:** Fetch metrics from database
3. **Action:** Format as Slack message
4. **Action:** Post to #s6-monitoring

**Or use third-party service (Zapier, IFTTT, Integromat) to:**
- Poll Grafana API every 30 min
- Post updates to Slack if metric threshold exceeded

---

## SIGN-OFF

**Slack Setup Completed by:** _____________________ (DevOps)  
**Date:** _____________________  
**Verified by:** _____________________ (Tech Lead)  

**All channels online & monitoring active:** ✅ YES / ❌ NO

---

**End of Slack Channel Setup Guide**
