# Manta Maestro — Support Handbook v1.0

**For:** Support team, customer success, escalation engineers  
**Team Size:** 8 support agents  
**SLA:** P1 < 1h, P2 < 4h, P3 < 24h  
**Updated:** 2026-07-27

---

## Quick Incident Response

### P1 (Critical) — System Down / Data Loss

**Response Time:** < 15 minutes  
**Escalate to:** Incident Commander + CTO

**Customer message template:**
> "We're aware of the outage and our engineering team is actively working to restore service. We'll send you an update every 15 minutes. Thank you for your patience."

**Tracking:**
- Create incident in Jira: P1-[DATE]-[NUMBER]
- Notify customer via email + Slack #customer-alerts
- Post-incident report required within 24h

### P2 (High) — Degradation / Feature Broken

**Response Time:** < 1 hour  
**Escalate to:** Senior support engineer + DevOps

**Customer message:**
> "Thank you for reporting this. We're investigating and will get back to you within 1 hour."

### P3 (Medium) — Non-critical Bug

**Response Time:** < 4 hours  
**Assignment:** Support team (self-service resolution if possible)

### P4 (Low) — Enhancement / Documentation

**Response Time:** < 24 hours  
**Assignment:** Product team (may be backlog)

---

## Common Issues & Solutions

### Issue #1: Login Failed — "Invalid Credentials"

**Symptoms:**
- User can't log in
- Shows "Invalid email or password"
- User reset password but still failing

**Diagnosis**

```bash
# SSH to production and check user status
psql -h postgres-primary -d manta_db -U postgres

SELECT user_id, email, password_hash, mfa_enabled, is_active 
FROM users WHERE email = 'user@example.com';
```

**Solutions**

**Option A: Password reset (most common)**
1. Ask user to visit login page
2. Click "Forgot password?"
3. Enter email → check inbox for reset link
4. Create new password (min 12 chars, 1 upper, 1 number, 1 symbol)
5. Try logging in

**Option B: MFA disabled (if stuck in auth loop)**
```bash
# Support escalation: disable MFA temporarily
psql -h postgres-primary -d manta_db -U postgres

UPDATE users SET mfa_enabled = false WHERE email = 'user@example.com';
```
Then ask user to:
1. Log in (no MFA code needed now)
2. Go to Settings → Security → Re-enable MFA (will show new QR code)
3. Scan QR with authenticator app
4. Confirm

**Option C: Account locked after 5 failed attempts**
```bash
# Reset login attempts
UPDATE users SET login_attempts = 0 WHERE email = 'user@example.com';
```

---

### Issue #2: "Agent Execution Failed" — 503 Service Unavailable

**Symptoms:**
- Prompt submitted, getting error "Service temporarily unavailable"
- Other users report same issue
- Happens intermittently

**Diagnosis**

```bash
# Check FastAPI pod status
kubectl get pods -n manta-prod | grep fastapi

# Check logs
kubectl logs deployment/manta-fastapi -n manta-prod --tail=50
```

**Solutions**

**Option A: Pod is restarting (crashloop)**
```bash
# Describe pod to see why
kubectl describe pod [POD_NAME] -n manta-prod

# Common causes: OOM, missing dependency
# Fix: Restart deployment
kubectl rollout restart deployment/manta-fastapi -n manta-prod
```

**Option B: Database connection pool exhausted**
```bash
# Check active connections
psql -h postgres-primary -d manta_db -c "SELECT count(*) FROM pg_stat_activity;"

# If > 45/50: scale API pods to spread load
kubectl scale deployment/manta-fastapi --replicas=6 -n manta-prod
```

**Option C: Claude API timeout**
```bash
# Temporary issue with Anthropic API
# Solution: User should retry in 5-10 minutes
# If persists, escalate to Anthropic support
```

**Customer message:**
> "The service is experiencing temporary issues. Please try again in a few minutes. We're monitoring the situation closely."

---

### Issue #3: Slow Response — "Waiting 30+ seconds"

**Symptoms:**
- Prompts taking > 10 seconds to complete
- User frustrated with latency
- Not consistently slow (sometimes fast, sometimes slow)

**Diagnosis**

```bash
# Check p95 latency
kubectl port-forward -n manta-prod svc/prometheus 9090:9090

# Query: histogram_quantile(0.95, rate(manta_api_latency_seconds_bucket[5m]))
# Expected < 5s
```

**Solutions**

**Option A: High CPU/memory utilization**
- Wait 5-10 minutes for auto-scaling
- Or manually scale: `kubectl scale deployment/manta-fastapi --replicas=6`
- Message: "We're experiencing higher-than-normal load. Performance should improve shortly."

**Option B: Slow query in database**
- Pass to DevOps/DBA for investigation
- Escalate: "Internal: DB slow query, investigating"

**Option C: Network latency to Claude API**
- Not user's fault, temporary issue
- Message: "External API latency is higher than normal. Responses will take longer than usual. We're monitoring."

---

### Issue #4: Upload Failed — "File too large" or "Unsupported format"

**Symptoms:**
- User trying to upload to Knowledge Hub
- Getting error: File size > 50MB or format not supported

**Solution**

**Option A: File too large**
- Max file size is 50MB
- Ask user to:
  1. Compress PDF (save as PDF Lite in Adobe)
  2. Split into multiple files
  3. Try again

**Option B: Unsupported format**
- Supported: PDF, DOCX, XLSX
- Ask user to convert:
  - PPT → PDF (File → Export as PDF)
  - JPG/PNG → PDF (online converter or Print to PDF)
  - PSD/CAD → Export as PDF

**Option C: Corrupted file**
- Ask user to:
  1. Re-download from source
  2. Verify file opens on their computer
  3. Try upload again

---

### Issue #5: Wrong Agent Selected — Routing Error

**Symptoms:**
- User asks about Saneamento
- Maestro selects Rodovia agent instead
- Response doesn't match user's intent

**Solution**

1. Acknowledge: "I understand the wrong agent was selected for your question"
2. Explain: "Our routing model is trained on 20 agents and sometimes makes mistakes on niche topics"
3. Workaround:
   - Manual selection: Browse agent list, click correct agent
   - Feedback: Rate the mistake (helps retrain routing model)
4. Message: "Thanks for catching that! We're using your feedback to improve agent selection. This should happen less frequently after our next update (2026-08-15)."

---

### Issue #6: Low Citation Accuracy — "Source is incorrect"

**Symptoms:**
- Agent response includes a citation
- User verifies the source — text doesn't match the cited document
- Trust issues ("why should I trust this?")

**Solution**

1. Retrieve the citation details from user
2. Manually verify:
```bash
# Search the knowledge base
curl -X POST https://api.manta.example.com/rag/search \
  -H "Authorization: Bearer $SUPPORT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "[DOC_ID_FROM_USER]",
    "chunk_id": "[CHUNK_ID_FROM_USER]"
  }'
```

3. If citation is wrong:
   - Apologize: "This is a citation error. Thank you for catching it."
   - Note the issue: Create bug ticket "RAG Citation Mismatch"
   - Escalate to engineering for investigation
   - Suggest: "Please verify citations by clicking the source link before relying on the information"

4. If citation is correct but user misunderstood:
   - Clarify the context
   - Point to specific sentence/section
   - Message: "This citation is accurate. Here's the specific section that applies to your question..."

---

### Issue #7: API Key Not Working — 401 Unauthorized

**Symptoms:**
- Developer trying to use API
- Getting: `{"detail": "Invalid authentication credentials"}`

**Solution**

1. Verify they have an API key:
   ```bash
   # SSH to DB
   psql -h postgres-primary -d manta_db
   
   SELECT * FROM api_keys WHERE user_id = 'usr_xyz';
   ```

2. If no key exists, ask them to:
   - Log in to Manta Maestro
   - Profile → API Keys → Generate Key
   - Copy the key (shown once!)

3. If key exists but still failing:
   - Check if key is **active** (not revoked)
   - Check if key is **valid** (not expired)
   - Check HTTP header format: `Authorization: Bearer YOUR_KEY`

4. If still failing:
   ```bash
   # Check logs for auth errors
   kubectl logs deployment/manta-fastapi | grep "auth\|401"
   ```
   - May be rate limiting or JWT issue
   - Ask them to try again in 5 minutes

---

### Issue #8: Storage Limit Exceeded — "Knowledge Hub full"

**Symptoms:**
- Upload fails: "Storage quota exceeded"
- User has uploaded many documents

**Solution**

1. Check their usage:
   ```bash
   psql -h postgres-primary -d manta_db
   
   SELECT org_id, 
     ROUND(SUM(pg_total_relation_size(schemaname||'.'||tablename)) / 1024 / 1024) AS size_mb
   FROM pg_tables
   WHERE org_id = 'org_xyz'
   GROUP BY org_id;
   ```

2. Options:
   - **Upgrade plan:** Professional tier includes more storage
   - **Delete old documents:** Ask user to remove unused documents from Knowledge Hub
   - **Archive to S3:** Contact support for custom archival solution

3. Message: "Your Knowledge Hub is at capacity. You can either upgrade to Professional tier or remove unused documents. Would you like help with either?"

---

### Issue #9: Feedback Not Submitted — "Rating disappeared"

**Symptoms:**
- User rates response (1-5 stars)
- Refreshes page → rating is gone
- Not recorded in system

**Solution**

1. Likely a **race condition** in frontend
2. Ask them to:
   - Clear browser cache (Cmd+Shift+Delete)
   - Try again on different browser (to verify it's not browser-specific)

3. If persists:
   - May be JavaScript error
   - Ask them to open **Developer Console** (F12)
   - Check for red errors
   - Screenshot and send to support

4. Escalate to engineering if needed: "Frontend feedback submission failing on Chrome, user affected since [DATE]"

---

### Issue #10: MFA Code Not Working — "Code expired"

**Symptoms:**
- User enters MFA code
- Getting: "Invalid or expired code"
- Code wasn't accepted within 30 seconds

**Solution**

1. TOTP codes expire every 30 seconds
   - Ask user to get **new code** from authenticator app
   - Enter quickly (within 30 sec)
   - If using phone, check **time is correct** on phone (clock skew causes failures)

2. If repeatedly failing:
   - Clock may be out of sync
   - **Solution:** User should sync time on phone
     - iPhone: Settings → General → Date & Time → turn off Auto-Set (then back on)
     - Android: Settings → Date & Time → turn off Automatic date & time (then back on)

3. If still failing after sync:
   - Authenticator app may be corrupted
   - **Solution:** Disable MFA (requires escalation)
   ```bash
   # Support escalation: verify user identity first!
   # Then:
   UPDATE users SET mfa_enabled = false WHERE user_id = 'usr_xyz';
   ```
   - Ask user to re-enable MFA (will provide new QR code)

---

### Issue #11: Workflow Execution Stuck — "Still running after 1 hour"

**Symptoms:**
- User started multi-step workflow
- Status shows "running" for > 1 hour
- No progress visible

**Solution**

1. Check workflow status:
   ```bash
   curl -X GET https://api.manta.example.com/workflows/wf_xyz/executions/exec_abc \
     -H "Authorization: Bearer $SUPPORT_TOKEN"
   ```

2. If status is "stuck":
   - Check which step is stuck:
     - Database error? (check pod logs)
     - Claude API timeout? (retry will be automatic)
     - MCP service down? (check status.manta.example.com)

3. Solutions:
   - **If < 30 min stuck:** "Still processing. Complex workflows can take 10-30 minutes. We'll notify you when complete."
   - **If > 30 min stuck:** Stop workflow and restart
   ```bash
   # Kill the workflow job
   kubectl delete job workflow-exec-abc
   ```
   - Message: "The previous workflow had an issue and was cancelled. Please restart it and we'll investigate."

4. Escalate to engineering for root cause

---

### Issue #12: Citation Sources Missing — "No citations in response"

**Symptoms:**
- User had "Include citations" enabled
- Response came back with NO citations
- Looks like hallucination

**Solution**

1. Check if Knowledge Hub is **empty/not configured**:
   - Ask: "Do you have documents uploaded to Knowledge Hub?"
   - If no: explain RAG requires documents
   - Guide them: Knowledge Hub → Upload → Add documents

2. If documents exist but citations missing:
   - Check if query matched any documents:
   ```bash
   curl -X POST https://api.manta.example.com/rag/search \
     -H "Authorization: Bearer $SUPPORT_TOKEN" \
     -d '{"query": "[USER_QUERY]"}'
   ```
   - If no results: documents may not match query
   - Message: "Your documents don't seem to cover this topic. Consider uploading relevant standards/contracts."

3. If search results exist but not cited:
   - May be agent preference (model chose to use generic knowledge instead)
   - Ask agent directly: "Please include citations from Knowledge Hub"
   - Escalate: "Agent not citing available sources"

---

## Decision Tree: How to Escalate

```
┌─ Is the system DOWN? ──→ P1: Escalate immediately
│
├─ Is it USER EDUCATION? ──→ Self-service: link to USER_GUIDE.md
│
├─ Is it a KNOWN ISSUE? ──→ Check issue DB, provide workaround + ETA
│
├─ Can I reproduce it? ──→ Yes: Create bug ticket, assign to engineering
│                    └─→ No: Ask for more info (screenshot, steps to repro)
│
├─ Does it affect many users? ──→ Yes: Page reliability team, communicate status
│                             └─→ No: Route to support queue
│
└─ Does it need code change? ──→ Yes: Create GitHub issue (with severity label)
                          └─→ No: Resolve and close ticket
```

---

## Communication Templates

### Template 1: Initial Response (First Contact)

> "Thanks for contacting Manta Maestro support! I've received your issue: [SUMMARY]. 
> 
> I'm investigating and will follow up with next steps within 1 hour. 
> 
> In the meantime, [QUICK_WORKAROUND if applicable].
> 
> Looking forward to getting this resolved for you!
> 
> Best,  
> [SUPPORT_AGENT_NAME]"

### Template 2: Status Update (If investigating > 30 min)

> "Quick update: We're still looking into your issue. 
> 
> So far we've checked:
> - [CHECK_1]: [RESULT]
> - [CHECK_2]: [RESULT]
> 
> Next steps:
> - [ACTION_1]
> - [ACTION_2]
> 
> We'll follow up within [TIME]."

### Template 3: Bug Confirmation

> "Thank you for reporting this! I've confirmed this is a bug in [COMPONENT].
> 
> **Workaround:** [WORKAROUND if applicable]
> 
> **Permanent fix:** Our team is working on a fix, targeted for [DATE].
> 
> I'll let you know as soon as it's deployed. Sorry for the inconvenience!"

### Template 4: Not a Bug (User Education)

> "Thanks for your question! This is actually working as designed.
> 
> Here's what's happening: [EXPLANATION]
> 
> **To accomplish your goal:**
> 1. [STEP_1]
> 2. [STEP_2]
> 
> Let me know if this helps!"

### Template 5: Resolution / Ticket Close

> "Your issue has been resolved! 
> 
> **What we did:** [SUMMARY]
> 
> **Your action:** [ANY_ACTION_NEEDED if applicable]
> 
> **For future reference:** [DOCUMENTATION_LINK]
> 
> Feel free to reach out if you have more questions. Thanks for your patience!"

---

## Escalation Matrix

| Issue | Who | When | How |
|-------|-----|------|-----|
| System outage | Incident Commander | Immediately | Page PagerDuty |
| Data loss | CTO | Immediately | Call + email |
| Security issue | Security lead | < 15 min | Slack + call |
| API bug | Backend engineering | Next available | GitHub issue P1 |
| UI bug | Frontend engineering | Same day | GitHub issue P2 |
| Routing error | ML team | Within 24h | Feedback data tagged |
| Customer complaint | Product manager | Within 24h | Email summary |
| Feature request | Product team | Within 7d | GitHub discussion |

---

## FAQ (Frequently Asked Questions)

**Q1: How long does document upload take?**  
A: 1-5 minutes per file. Complex PDFs may take longer. We send notification when done.

**Q2: Can I share my account with a teammate?**  
A: No, each person needs their own account. But you can share workflows within the organization.

**Q3: What happens if I delete a document from Knowledge Hub?**  
A: It's moved to trash (recoverable for 30 days). After 30 days, permanently deleted.

**Q4: Can I export my workflow results?**  
A: Yes! Click "Download" on completed workflow (PDF, Word, or JSON format).

**Q5: Is my data encrypted?**  
A: Yes, AES-256 encryption at rest and TLS 1.3 in transit.

**Q6: How do I change my organization name?**  
A: Admin settings (requires org owner role). Contact support if you don't have access.

**Q7: Can I use Manta Maestro offline?**  
A: No, it requires internet connection. Offline support planned for Q4 2026.

**Q8: What's the refund policy?**  
A: 14-day money-back guarantee. Contact support with reason.

**Q9: Can I cancel my subscription anytime?**  
A: Yes, no lock-in. Cancels at end of billing cycle.

**Q10: How do I report a security issue?**  
A: Email security@mantaassociados.com (not in public issues).

**Q11: What payment methods do you accept?**  
A: Credit card (all major), bank transfer (Brazil), PIX.

**Q12: Is there an SLA for API uptime?**  
A: Yes, 99.9% uptime SLA with 10% credits for violations (Enterprise plan).

**Q13: Can I use fine-tuned models in production?**  
A: Yes, they're auto-deployed to your organization's agents (A/B test by default).

**Q14: How do I prevent other team members from deleting workflows?**  
A: Assign read-only permissions in Admin → Access Control.

**Q15: What languages does Manta support?**  
A: Portuguese (Brazil) and English. Other languages coming soon.

---

## Support Tools & Access

**Slack channels:**
- `#manta-support` — Internal support team chat
- `#customer-alerts` — Broadcast alerts to customers
- `#escalations` — Escalate to engineering

**Ticketing system:**
- Jira: https://jira.mantaassociados.com
- Create tickets: [PROJECT]-[NUMBER] (e.g., SUPPORT-1234)

**Knowledge base:**
- Confluence: https://wiki.mantaassociados.com/support
- Update with common issues as you discover them

**Access:**
- PostgreSQL: `psql -h postgres-primary -U support_user`
- Kubernetes: `kubectl config use-context manta-prod`
- Logs: `kubectl logs -f deployment/manta-fastapi -n manta-prod`

---

## Metrics & KPIs

**Track these weekly:**

- **Response time (First response):** Target < 1h for P1, < 4h for P2
- **Resolution time (Ticket close):** Target < 8h for P1, < 24h for P2
- **Customer satisfaction (CSAT):** Target > 4.5/5
- **Escalation rate:** Track % tickets escalated to engineering
- **Repeat issues:** If same issue reported 3+ times, escalate as bug

---

**Last Updated:** 2026-07-27  
**On-Call Phone:** [SUPPORT_LEAD_PHONE]  
**Slack:** @support-lead  
**Email:** support@mantaassociados.com
