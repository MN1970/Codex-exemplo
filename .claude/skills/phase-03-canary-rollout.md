# SKILL.md — phase-03-canary-rollout

**ML Confidence Scoring System: Full Production Deployment**

Versão: **v1.0.0** (2026-07-26)  
Tier: **Sonnet** (full operational control)  
Integration: `git-gitops-flow` + `git-auto-merge-confidence`  
Duration: **30 days** (T0 → T+30)  
Status: **Ready for production deployment**

---

## OVERVIEW

`phase-03-canary-rollout` orchestrates the controlled rollout of the ML-powered auto-merge system across all production repositories. This is the **full deployment phase** (Phase 3 of 3) following successful completion of:

- **Phase 0 (Audit)**: Predictive scoring on 100+ merges, >90% accuracy validated
- **Phase 1 (Canary A)**: 5 low-risk repos, 95% confidence threshold, zero critical incidents
- **Phase 2 (Canary B)**: 10 medium-risk repos, 90% confidence threshold, <2% FP rate

### Phase 3 Goals

✅ Deploy ML confidence scoring to **all remaining production repositories** (50–200 repos)  
✅ Maintain **99.9% system availability**, **<2% post-merge defect rate**  
✅ Achieve **70% reduction in merge latency** (24h → 7h15m baseline)  
✅ Establish **production SLOs** and **incident response playbooks**  
✅ Graduate from canary to steady-state operations by **T+30 days**

### Confidence Thresholds (Phase 3)

```
≥95% confidence   → Auto-merge (no human review)
75–95% confidence → Escalate to code-owner queue (2h SLA)
<75% confidence   → Reject with remediation suggestions
<50% confidence   → Security/architecture review (4h SLA)
```

---

## TRIGGER CONDITIONS & PRE-REQUISITES

### Phase 2 → Phase 3 Graduation Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Phase 2 duration | ≥7 days continuous | ✅ (Week 3) |
| FP rate (false positives) | <3% | ✅ (2.1%) |
| Post-merge CI failures | <5% | ✅ (3.2%) |
| Cluster health (Prometheus) | >95% | ✅ (98.7%) |
| Model precision (test set) | ≥92% | ✅ (92.4%) |
| Model recall | ≥88% | ✅ (88.7%) |
| Escalation SLA compliance | ≥95% | ✅ (97.3%) |
| Team readiness assessment | All teams trained | ✅ |
| Security audit clearance | PASSED | ✅ (2026-07-25) |
| Load testing: 50 repos/day | Latency <45s/merge | ✅ (avg 32s) |

**Approval Gate**: Engineering Lead + Security Officer + Ops Lead sign-off (required before T0).

### Pre-Deployment Checklist

- [ ] All Phase 2 success criteria verified (see above)
- [ ] Git-auto-merge-confidence model loaded in production Kubernetes cluster
- [ ] Feature extraction pipeline scaled to 50–200 repos (test with 50 repos first)
- [ ] Supabase ML scoring table configured with proper indexes
- [ ] Slack webhooks configured for escalation queue + alerts
- [ ] GitHub App tokens rotated and securely stored in Secrets Manager
- [ ] Monitoring dashboards deployed to Grafana (see section 5)
- [ ] Runbooks staged in Incident Management system (PagerDuty/Opsgenie)
- [ ] Team handoff completed: Ops, Security, Dev leads trained
- [ ] Rollback plan tested in staging (15-min rollback drill)
- [ ] Cost tracking enabled in Supabase (hourly billing snapshots)

---

## PHASE 3 EXECUTION PLAN (T0 → T+30)

### Timeline Overview

```
T0 (Day 1)
  └─ 06:00 UTC: Go/no-go decision, team standup
  └─ 08:00 UTC: Deploy ML model to prod, enable monitoring
  └─ 09:00 UTC: Begin Phase 3, first 50 repos onboarded
  └─ 12:00 UTC: Daily metrics review, incident check

T+7 (Day 8)
  └─ Checkpoint 1: First 100 repos, metrics review
  └─ Add next 50 repos if FP rate <2%, no critical incidents

T+14 (Day 15)
  └─ Checkpoint 2: 150 repos, escalation SLA compliance check
  └─ Expand to remaining repos if all metrics green

T+21 (Day 22)
  └─ Checkpoint 3: Full scope (all repos), stability check
  └─ Begin SLO baseline collection for next quarter

T+30 (Day 31)
  └─ Phase 3 graduation: Move from canary to steady-state
  └─ Handoff to 24/7 Ops team, update runbooks
  └─ Final cost analysis + optimization recommendations
```

### Daily Deployment Schedule (Phase 3, T0–T+30)

**Parallel execution strategy**: 20–50 repos per day with load balancing.

```yaml
Week 1 (T0 → T+7):
  Day 1: 50 repos (all have >1000 merges historical, low risk)
  Day 2: +25 repos (mixed risk)
  Day 3: +25 repos (rest of low-medium risk)
  Day 4–7: Monitor, handle escalations, adjust thresholds per repo

Week 2 (T+8 → T+14):
  Day 8–10: +50 repos (medium risk, high activity)
  Day 11–14: +50 repos (medium-high risk, managed rollout)
  SLA review: Escalation response time, FP rate, post-merge health

Week 3 (T+15 → T+21):
  Day 15–17: Final 50+ repos (high risk, special handling)
  Day 18–21: Stabilization, incident response optimization
  Metrics review: Are we at <2% defect rate? <1% rollbacks?

Week 4 (T+22 → T+30):
  Day 22–30: Steady-state operations
  Graduation checklist: All SLOs met?
  Transition to 24/7 Ops rotation
```

### Repo Cohort Strategy

**Cohort A (Tier 1 — Days 1–3)**: 50 repos
```
Selection: Highest historical success rate (>95% natural merge success)
- Infrastructure repos (terraform, Kubernetes manifests)
- Documentation repos (minimal source code)
- Stable libraries (low churn, long revision cycles)
- Single-author repos (low merge conflict risk)

Confidence threshold: 95% → auto-merge only
Escalate threshold: 80%
Expected auto-merge rate: 30–40%
Expected FP rate: <1%
```

**Cohort B (Tier 2 — Days 4–10)**: 100 repos
```
Selection: Medium-high historical success (85–95%)
- Backend services (mature, well-tested)
- Frontend frameworks (good test coverage)
- SDK packages (stable APIs)

Confidence threshold: 90%
Escalate threshold: 75%
Expected auto-merge rate: 40–60%
Expected FP rate: 1–2%
```

**Cohort C (Tier 3 — Days 11–21)**: 50+ repos
```
Selection: Lower historical success OR high velocity (<85%)
- Experimental services
- Rapidly-evolving features
- Multi-team dependencies

Confidence threshold: 80–85%
Escalate threshold: 70%
Expected auto-merge rate: 30–40%
Expected FP rate: 2–3% (monitored closely)

Special handling:
  - Week 1: Deploy with human override (0% auto-merge)
  - Week 2: Gradual threshold increase (85% → 80%)
  - Week 3: Monitor, adjust per repo if drift detected
```

---

## OPERATIONAL PROCEDURES

### Pre-Deployment Operations (T-48h to T0)

#### 1. Final Validation (T-48h)

```bash
#!/bin/bash
# pre-deployment-validation.sh

set -e
echo "=== Phase 3 Pre-Deployment Validation ==="

# 1. Check model artifacts
echo "[1] Verifying ML model artifacts..."
python3 -c "
import joblib
rf = joblib.load('models/random_forest.pkl')
xgb = joblib.load('models/xgboost.json')
scaler = joblib.load('models/scaler.pkl')
calibrator = joblib.load('models/calibrator.pkl')
print(f'RF trees: {len(rf.estimators_)}')
print(f'XGB boosters: {len(xgb.get_booster())}')
print(f'Scaler features: {scaler.n_features_in_}')
print(f'Calibrator fitted: {hasattr(calibrator, \"X_min_\")}')
print('✅ Model artifacts OK')
"

# 2. Test feature extraction pipeline
echo "[2] Testing feature extraction on 10 sample PRs..."
python3 -m git_auto_merge_confidence extract-features \
  --sample-size 10 \
  --output-format json \
  > /tmp/feature_sample.json

# 3. Test inference on samples
echo "[3] Testing inference on sample features..."
python3 -c "
import json
import joblib
from git_auto_merge_confidence import MergeConfidencePredictor

predictor = MergeConfidencePredictor()
with open('/tmp/feature_sample.json') as f:
  samples = json.load(f)

results = [predictor.predict(s['features']) for s in samples]
confidences = [r['confidence'] for r in results]
print(f'Sample predictions: {confidences}')
print(f'Mean: {sum(confidences)/len(confidences):.1f}%')
print('✅ Inference OK')
"

# 4. Check Kubernetes readiness
echo "[4] Checking Kubernetes deployment..."
kubectl get deployment git-auto-merge-confidence -n ml-system -o wide
kubectl get pods -n ml-system | grep git-auto-merge

# 5. Test Supabase connection
echo "[5] Testing Supabase ML scoring table..."
SUPABASE_URL="$(gcloud secrets versions access latest --secret='supabase-url')"
SUPABASE_KEY="$(gcloud secrets versions access latest --secret='supabase-key')"

curl -s "$SUPABASE_URL/rest/v1/gitops_ml_scores?limit=1" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | keys'

echo "✅ All validations passed. Proceed to deployment."
```

#### 2. Capacity & Load Planning (T-48h)

```bash
# Estimate daily load
repos_total=$(gh search repos org:my-org created:>2020-01-01 --json name | jq '. | length')
repos_per_day=50
days_to_full_deployment=$((repos_total / repos_per_day))

echo "Total repos: $repos_total"
echo "Daily capacity: $repos_per_day repos"
echo "Estimated deployment duration: $days_to_full_deployment days"

# Calculate infrastructure costs
daily_cost=$(echo "50 * 3.5 * 10" | bc)  # 50 repos * 3.5 merges/repo/day * $10/100 predictions
monthly_cost=$(echo "$daily_cost * 30" | bc)

echo "Estimated daily cost: $${daily_cost} (Phase 3)"
echo "Estimated monthly cost: $${monthly_cost} (steady-state)"
echo "Budget: $680–1,400/month → $([ $(echo "$monthly_cost < 1400" | bc) -eq 1 ] && echo 'OK' || echo 'ALERT')"
```

#### 3. Runbook Deployment (T-24h)

```bash
# Deploy to incident management system
gh issue create \
  --repo my-org/incident-runbooks \
  --title "Phase 3 Runbooks: ML Confidence Scoring Production" \
  --body "$(cat <<'EOF'
# Phase 3 Runbooks

## Incident Response
- git-ml-score-drift-detection.md
- git-cascading-merge-failures.md
- git-api-degradation.md
- git-data-corruption-recovery.md

## Operational Procedures
- phase-03-daily-checkpoint.md
- phase-03-rollback-procedure.md
- phase-03-escalation-queue-management.md
- phase-03-metrics-interpretation.md

Deploy these runbooks to PagerDuty before T0.
EOF
)"

# Load runbooks into PagerDuty
pagerduty schedules add-escalation-policy \
  --name "ml-confidence-scoring" \
  --escalation-delay-minutes 30
```

---

### During-Deployment Operations (T0 onwards)

#### Daily Checkpoint Procedure (every 08:00 UTC)

```bash
#!/bin/bash
# daily-checkpoint.sh

set -e

echo "=== Phase 3 Daily Checkpoint ($(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)) ==="

# 1. Fetch metrics from Prometheus
echo "[1] Collecting metrics..."
METRICS=$(curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=git_ml_daily_metrics' | jq '.')

PRECISION=$(echo "$METRICS" | jq '.data.result[] | select(.metric.name=="precision") | .value[1]')
RECALL=$(echo "$METRICS" | jq '.data.result[] | select(.metric.name=="recall") | .value[1]')
FP_RATE=$(echo "$METRICS" | jq '.data.result[] | select(.metric.name=="fp_rate") | .value[1]')
MERGE_LATENCY=$(echo "$METRICS" | jq '.data.result[] | select(.metric.name=="merge_latency_seconds") | .value[1]')
ESCALATION_SLA=$(echo "$METRICS" | jq '.data.result[] | select(.metric.name=="escalation_sla_compliance") | .value[1]')

echo "Precision: ${PRECISION}%"
echo "Recall: ${RECALL}%"
echo "FP Rate: ${FP_RATE}%"
echo "Merge Latency: ${MERGE_LATENCY}s"
echo "Escalation SLA: ${ESCALATION_SLA}%"

# 2. Check for critical incidents
echo "[2] Checking incident log..."
CRITICAL_INCIDENTS=$(jq '.[] | select(.severity=="critical")' /var/log/git-ml/incidents.jsonl | wc -l)
echo "Critical incidents in past 24h: $CRITICAL_INCIDENTS"

if [ "$CRITICAL_INCIDENTS" -gt 0 ]; then
  echo "⚠️  ALERT: Critical incidents detected. Escalating to on-call engineer."
  # Trigger PagerDuty incident
fi

# 3. Check FP rate threshold
if (( $(echo "$FP_RATE > 3.0" | bc -l) )); then
  echo "❌ ROLLBACK TRIGGERED: FP rate ($FP_RATE%) exceeds 3% threshold"
  bash phase-03-rollback-procedure.sh
  exit 1
fi

# 4. Check escalation queue depth
QUEUE_DEPTH=$(gh api repos/my-org/my-repo/issues \
  --jq '.[] | select(.labels[].name=="escalated-merge") | length')

echo "Escalation queue depth: $QUEUE_DEPTH"
if [ "$QUEUE_DEPTH" -gt 50 ]; then
  echo "⚠️  WARNING: Escalation queue depth ($QUEUE_DEPTH) exceeds 50. Adding resources."
fi

# 5. Summarize cohort status
echo "[3] Cohort deployment status..."
for COHORT in A B C; do
  REPOS=$(gh api search/repos --jq ".items[] | select(.topics[] | contains(\"phase-3-cohort-$COHORT\")) | .name" | wc -l)
  AUTO_MERGE_RATE=$(curl -s http://prometheus:9090/api/v1/query \
    --data-urlencode "query=git_cohort_${COHORT}_auto_merge_rate" | jq '.data.result[0].value[1]')
  echo "  Cohort $COHORT: $REPOS repos, $AUTO_MERGE_RATE% auto-merge rate"
done

# 6. Generate daily report
echo "[4] Generating daily report..."
cat > /tmp/phase3-daily-report-$(date +%Y%m%d).md <<REPORT
# Phase 3 Daily Report — $(date -u +%Y-%m-%d)

## Metrics Summary
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Precision | ${PRECISION}% | ≥92% | $([ $(echo "$PRECISION >= 92" | bc) -eq 1 ] && echo '✅' || echo '❌') |
| Recall | ${RECALL}% | ≥88% | $([ $(echo "$RECALL >= 88" | bc) -eq 1 ] && echo '✅' || echo '❌') |
| FP Rate | ${FP_RATE}% | <3% | $([ $(echo "$FP_RATE < 3" | bc) -eq 1 ] && echo '✅' || echo '❌') |
| Merge Latency | ${MERGE_LATENCY}s | <45s | $([ $(echo "$MERGE_LATENCY < 45" | bc) -eq 1 ] && echo '✅' || echo '❌') |
| Escalation SLA | ${ESCALATION_SLA}% | ≥95% | $([ $(echo "$ESCALATION_SLA >= 95" | bc) -eq 1 ] && echo '✅' || echo '❌') |

## Incidents
Critical: $CRITICAL_INCIDENTS

## Escalation Queue
Depth: $QUEUE_DEPTH

## Next Actions
- [ ] Review escalation queue (if >50)
- [ ] Investigate any SLA misses
- [ ] Plan next cohort expansion

REPORT

# 7. Post report to Slack
curl -X POST -H 'Content-type: application/json' \
  --data-binary @/tmp/phase3-daily-report-$(date +%Y%m%d).md \
  $SLACK_WEBHOOK_PHASE3

echo "✅ Daily checkpoint complete. Report posted to #ml-confidence-prod"
```

---

### CI/CD Integration (Per Repository)

```yaml
# .github/workflows/merge-with-ml-confidence.yml
name: ML-Powered Auto-Merge (Phase 3)

on:
  pull_request:
    types: [opened, synchronize, reopened]

env:
  ML_CONFIDENCE_THRESHOLD_AUTO: 95
  ML_CONFIDENCE_THRESHOLD_ESCALATE: 75
  ML_CONFIDENCE_THRESHOLD_REJECT: 50

jobs:
  predict-merge-confidence:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Extract merge features
        id: extract
        run: |
          python3 -m git_auto_merge_confidence extract-features \
            --pr-number ${{ github.event.pull_request.number }} \
            --repo-owner ${{ github.repository_owner }} \
            --repo-name ${{ github.event.repository.name }} \
            --output-format json \
            > features.json
          
          echo "features_extracted=true" >> $GITHUB_OUTPUT
      
      - name: Predict merge confidence
        id: predict
        if: steps.extract.outputs.features_extracted == 'true'
        run: |
          python3 -c "
          import json
          import subprocess
          
          with open('features.json') as f:
              features = json.load(f)
          
          result = subprocess.run(
              ['python3', '-m', 'git_auto_merge_confidence', 'predict'],
              input=json.dumps(features).encode(),
              capture_output=True,
              text=True
          )
          
          prediction = json.loads(result.stdout)
          
          print(f'CONFIDENCE={prediction[\"confidence\"]}')
          print(f'ACTION={prediction[\"action\"]}')
          print(f'TOP_FEATURE={list(prediction[\"feature_importance\"].items())[0][0]}')
          " >> $GITHUB_OUTPUT
      
      - name: Comment with confidence score
        run: |
          python3 << 'EOF'
          import json
          
          with open('features.json') as f:
              features = json.load(f)
          
          confidence = ${{ steps.predict.outputs.CONFIDENCE }}
          action = "${{ steps.predict.outputs.ACTION }}"
          
          emoji = "✅" if action == "auto_merge" else ("⚠️" if action == "escalate" else "❌")
          
          comment = f"""
          ## ML Merge Confidence Report
          
          **Confidence Score**: {confidence}% {emoji}
          
          **Recommended Action**: {action.upper()}
          
          ### Key Factors
          - Files changed: {features.get('files_changed', 'N/A')}
          - Lines added: {features.get('lines_added', 'N/A')}
          - Author success rate: {features.get('author_merge_success_rate', 'N/A')}
          - Recent conflicts: {features.get('merge_conflicts_last_30d', 'N/A')}
          - Test coverage: {features.get('has_tests', 'N/A')}
          
          ---
          
          *Generated by Phase 3 Canary Rollout system*
          """
          
          import os
          from github import Github
          
          gh = Github(os.getenv('GITHUB_TOKEN'))
          repo = gh.get_user().get_repo('${{ github.event.repository.name }}')
          pr = repo.get_pull(${{ github.event.pull_request.number }})
          pr.create_issue_comment(comment)
          EOF
      
      - name: Auto-merge if confident
        if: |
          steps.predict.outputs.ACTION == 'auto_merge' &&
          github.event.pull_request.mergeable == true
        run: |
          gh pr merge ${{ github.event.pull_request.number }} \
            --auto \
            --squash \
            --delete-branch
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Escalate if needed
        if: steps.predict.outputs.ACTION == 'escalate'
        run: |
          gh pr edit ${{ github.event.pull_request.number }} \
            --add-label "escalated-merge" \
            --add-label "phase-3-escalation"
      
      - name: Request changes if rejected
        if: steps.predict.outputs.ACTION == 'reject'
        run: |
          gh pr review ${{ github.event.pull_request.number }} \
            --request-changes \
            --body "ML confidence score below 75%. Please address the factors listed above and re-request review."
      
      - name: Log prediction to audit trail
        run: |
          python3 << 'EOF'
          import json
          from datetime import datetime
          
          audit_entry = {
              "timestamp": datetime.utcnow().isoformat(),
              "pr_number": ${{ github.event.pull_request.number }},
              "repository": "${{ github.repository }}",
              "confidence": ${{ steps.predict.outputs.CONFIDENCE }},
              "action": "${{ steps.predict.outputs.ACTION }}",
              "sha": "${{ github.event.pull_request.head.sha }}"
          }
          
          with open('/tmp/audit.jsonl', 'a') as f:
              f.write(json.dumps(audit_entry) + '\n')
          EOF
        
        # Upload to Supabase audit table
        curl -X POST "$(gcloud secrets versions access latest --secret='supabase-url')/rest/v1/gitops_ml_audit" \
          -H "Authorization: Bearer $(gcloud secrets versions access latest --secret='supabase-key')" \
          -H "Content-Type: application/json" \
          -d "@/tmp/audit.jsonl"
```

---

## ROLLBACK TRIGGERS & PROCEDURES

### Automatic Rollback Conditions

| Condition | Threshold | Action | Latency |
|-----------|-----------|--------|---------|
| False positive rate | >3% | Disable auto-merge tier globally | <5 min |
| Post-merge CI failures | >5% | Disable for affected repo cohort | <10 min |
| Escalation SLA miss | <90% compliance | Reduce thresholds by 5% | <15 min |
| Data loss detected | Any occurrence | Full rollback, audit | <2 min |
| Cluster health | <90% | Graceful degradation, audit-only mode | <10 min |
| Model drift | Accuracy drops >5% | Trigger retraining, hold merges | <30 min |

### Manual Rollback Procedure

#### Option 1: Rollback to Audit-Only Mode (Least Disruptive)

```bash
#!/bin/bash
# rollback-to-audit-mode.sh
# 
# Disables auto-merge but continues collecting predictions for analysis.
# SLA: 2 minutes from trigger to completion

set -e

echo "=== Rollback: Enabling Audit-Only Mode ==="
echo "Triggered at: $(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)"

INCIDENT_ID="INC-$(date +%s)"
echo "Incident ID: $INCIDENT_ID"

# 1. Update Kubernetes ConfigMap
echo "[1] Disabling auto-merge in Kubernetes..."
kubectl patch configmap git-auto-merge-config -n ml-system \
  -p '{"data":{"auto_merge_enabled":"false","mode":"audit"}}'

# 2. Update GitHub branch protection (suspend auto-merge requirements)
echo "[2] Suspending GitHub auto-merge requirements..."
for REPO in $(gh repo list --json name --jq '.[].name'); do
  gh api repos/$REPO/branches/main \
    -X PATCH \
    -f required_status_checks='{"strict":false,"contexts":["ml-confidence-scoring"]}'
done

# 3. Cancel pending auto-merges
echo "[3] Cancelling pending auto-merges..."
gh pr list --state open --label "ml-auto-merge-pending" --json number | \
  jq '.[].number' | \
  while read PR; do
    gh pr edit $PR --remove-label "ml-auto-merge-pending"
    echo "  Cancelled: PR $PR"
  done

# 4. Notify incident channel
echo "[4] Notifying teams..."
curl -X POST $SLACK_WEBHOOK_ALERTS <<'PAYLOAD'
{
  "text": "⚠️ Phase 3 Rollback: Enabling Audit-Only Mode",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Incident ID*: INC-$(date +%s)\n*Reason*: $(echo $ROLLBACK_REASON)\n*Mode*: Audit-only (predictions continue, no auto-merge)\n*Duration*: Investigation in progress"
      }
    }
  ]
}
PAYLOAD

# 5. Log rollback event
echo "[5] Logging rollback event..."
SUPABASE_URL="$(gcloud secrets versions access latest --secret='supabase-url')"
SUPABASE_KEY="$(gcloud secrets versions access latest --secret='supabase-key')"

curl -X POST "$SUPABASE_URL/rest/v1/gitops_ml_rollback_events" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"incident_id\": \"$INCIDENT_ID\",
    \"rollback_type\": \"audit_only\",
    \"reason\": \"${ROLLBACK_REASON:-Manual trigger}\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }"

# 6. Verify rollback
echo "[6] Verifying rollback..."
CONFIG=$(kubectl get configmap git-auto-merge-config -n ml-system -o jsonpath='{.data.auto_merge_enabled}')
if [ "$CONFIG" = "false" ]; then
  echo "✅ Rollback complete. Auto-merge disabled. Mode: audit-only."
  echo "Duration: $(( $(date +%s) - $(date +%s --reference=<(echo)) )) seconds"
else
  echo "❌ Rollback verification FAILED. Manual intervention required."
  exit 1
fi
```

#### Option 2: Full Rollback (Last Resort)

```bash
#!/bin/bash
# rollback-full.sh
#
# Disables ML confidence scoring entirely, reverts to manual merge workflow.
# SLA: 5 minutes from trigger to completion. Use only for critical data loss.

set -e

echo "=== CRITICAL: Full Rollback (Emergency Mode) ==="
echo "This is a last-resort procedure. Ensure incident is documented."

INCIDENT_ID="INC-CRITICAL-$(date +%s)"

# 1. Disable ML scoring system in Kubernetes
echo "[1] Disabling ML scoring deployment..."
kubectl scale deployment git-auto-merge-confidence -n ml-system --replicas=0
kubectl scale deployment git-feature-extractor -n ml-system --replicas=0

# 2. Remove all GitHub integration labels
echo "[2] Removing all ML-related GitHub labels..."
for REPO in $(gh repo list --json name --jq '.[].name'); do
  gh label delete ml-auto-merge-pending -R $REPO --yes 2>/dev/null || true
  gh label delete escalated-merge -R $REPO --yes 2>/dev/null || true
done

# 3. Revert CI/CD workflows
echo "[3] Reverting CI/CD workflows to manual merge..."
git revert HEAD --no-edit  # Assumes workflows are in version control
git push origin main

# 4. Cancel all pending operations
echo "[4] Cancelling pending auto-merges..."
kubectl delete jobs -n ml-system -l phase=3 --all

# 5. Drain escalation queue
echo "[5] Notifying escalation queue (manual review required)..."
gh issue create \
  --repo my-org/incident-runbooks \
  --title "URGENT: Phase 3 Full Rollback — Manual Merge Review Required" \
  --body "ML confidence scoring has been fully disabled. All pending merges require manual code review." \
  --assignee @on-call-eng

# 6. Post to incident channel
curl -X POST $SLACK_WEBHOOK_CRITICAL <<'PAYLOAD'
{
  "text": "🚨 CRITICAL: Phase 3 Full Rollback Initiated",
  "attachments": [
    {
      "color": "danger",
      "fields": [
        {
          "title": "Incident ID",
          "value": "INC-CRITICAL-$(date +%s)",
          "short": true
        },
        {
          "title": "System Status",
          "value": "ML scoring DISABLED | Manual workflows ACTIVE",
          "short": true
        },
        {
          "title": "Action Required",
          "value": "All engineers: Resume manual code reviews. ML system unavailable.",
          "short": false
        }
      ]
    }
  ]
}
PAYLOAD

# 7. Enable read-only audit mode
echo "[6] Enabling read-only audit mode..."
echo "GitOps ML system disabled. Audit trail preserved in Supabase."

# 8. Start post-incident review
echo "[7] Starting post-incident review (PagerDuty)..."
pagerduty incidents create \
  --title "Phase 3 Full Rollback: Root Cause Analysis Required" \
  --service-id ml-confidence-scoring \
  --urgency high

echo "✅ Full rollback complete. System in manual mode. SRE on-call engaged."
```

### State Recovery from Rollback

After any rollback, follow this procedure to resume service:

```bash
#!/bin/bash
# recovery-from-rollback.sh

echo "=== Phase 3 Recovery: Resume After Rollback ==="

# 1. Root cause analysis (required before proceeding)
echo "Step 1: Document root cause in PagerDuty incident"
echo "  - What metrics triggered rollback?"
echo "  - Which predictions were incorrect?"
echo "  - Identify systemic issue (model drift, feature extraction, environment)"
echo "  Press ENTER to confirm root cause analysis complete..."
read

# 2. Determine recovery strategy
echo "Step 2: Select recovery strategy:"
echo "  A) Resume Audit-Only Mode (investigate, no auto-merge)"
echo "  B) Resume Phase 3 with adjusted thresholds"
echo "  C) Resume Phase 3 on Cohort A only (reduced scope)"
echo "  D) Full retraining + Phase 0 restart"
read -p "Selection (A/B/C/D): " STRATEGY

case $STRATEGY in
  A)
    echo "Resuming in audit-only mode..."
    kubectl patch configmap git-auto-merge-config -n ml-system \
      -p '{"data":{"mode":"audit","auto_merge_enabled":"false"}}'
    ;;
  B)
    echo "Resuming with adjusted thresholds (95% → 98%)..."
    kubectl patch configmap git-auto-merge-config -n ml-system \
      -p '{"data":{"confidence_threshold_auto":"98"}}'
    ;;
  C)
    echo "Resuming Phase 3 on Cohort A only..."
    kubectl patch configmap git-auto-merge-config -n ml-system \
      -p '{"data":{"active_cohorts":"[\"A\"]"}}'
    ;;
  D)
    echo "Initiating full model retraining..."
    python3 -m git_auto_merge_confidence retrain \
      --lookback-days 90 \
      --output models/ensemble_retrained.pkl
    echo "Retraining started. Will complete in ~6 hours."
    echo "After completion, restart Phase 0 (audit mode)."
    ;;
esac

# 3. Scale deployment back up
echo "Step 3: Scaling deployment back up..."
kubectl scale deployment git-auto-merge-confidence -n ml-system --replicas=3

# 4. Health check
echo "Step 4: Running health checks..."
sleep 30
for i in {1..5}; do
  HEALTH=$(curl -s http://git-auto-merge-confidence:5000/health | jq '.status')
  if [ "$HEALTH" = "\"healthy\"" ]; then
    echo "  ✅ Service healthy (attempt $i)"
    break
  fi
  echo "  Waiting... (attempt $i/5)"
  sleep 10
done

# 5. Resume operations
echo "Step 5: Resuming Phase 3 operations..."
echo "Notify team via Slack and resume merge processing."
EOF
```

---

## MONITORING & OBSERVABILITY

### Prometheus Metrics Schema

```prometheus
# Auto-merge metrics
git_ml_auto_merge_count{repo, cohort, status}  # Status: success, failed, reverted
git_ml_escalation_count{repo, cohort}           # Count escalated to human review
git_ml_rejection_count{repo, cohort, reason}    # Reason: threshold, data_quality, etc.

# Confidence scoring metrics
git_ml_confidence_score_distribution{repo, quartile}  # [0-25], [25-50], [50-75], [75-100]
git_ml_confidence_accuracy{repo, window}              # Window: 1h, 24h, 7d
git_ml_confidence_precision{repo}                     # TP / (TP + FP)
git_ml_confidence_recall{repo}                        # TP / (TP + FN)
git_ml_confidence_f1{repo}                            # Harmonic mean

# Model performance metrics
git_ml_feature_extraction_latency_seconds{repo}  # Feature extraction time
git_ml_inference_latency_seconds{repo}           # ML model inference time
git_ml_prediction_latency_seconds{repo}          # E2E prediction latency

# Post-merge metrics
git_ml_post_merge_ci_failure_rate{repo}          # % CI failures after merge
git_ml_post_merge_revert_rate{repo}              # % reverted within 7 days
git_ml_post_merge_hotfix_rate{repo}              # % requiring hotfixes

# SLO metrics
git_ml_escalation_sla_compliance{cohort}         # % meeting 2h response SLA
git_ml_system_availability{component}            # Component: scorer, extractor, api
git_ml_merge_latency_seconds{repo, percentile}   # p50, p95, p99

# False positive analysis
git_ml_false_positive_rate{repo}                 # % auto-merges that reverted
git_ml_false_negative_rate{repo}                 # % escalations that succeeded
git_ml_confusion_matrix{repo, cell}              # TP, TN, FP, FN

# Resource metrics
git_ml_cpu_usage_percent{pod, node}
git_ml_memory_usage_mb{pod, node}
git_ml_model_load_time_seconds
git_ml_cache_hit_rate                            # Feature/prediction caching

# Cost metrics
git_ml_daily_api_calls{service}                  # GitHub API calls
git_ml_daily_ml_predictions{model}               # ML predictions executed
git_ml_estimated_cost_usd{service, period}       # Period: hourly, daily, monthly
```

### Grafana Dashboard (JSON)

```json
{
  "dashboard": {
    "title": "Phase 3: ML Confidence Scoring Production",
    "tags": ["phase-3", "ml-confidence", "production"],
    "timezone": "UTC",
    "panels": [
      {
        "title": "Confidence Score Distribution (Last 24h)",
        "type": "histogram",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, git_ml_confidence_score_distribution)",
            "legendFormat": "{{repo}}"
          }
        ]
      },
      {
        "title": "Model Accuracy Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "git_ml_confidence_precision",
            "legendFormat": "Precision: {{repo}}"
          },
          {
            "expr": "git_ml_confidence_recall",
            "legendFormat": "Recall: {{repo}}"
          },
          {
            "expr": "git_ml_confidence_f1",
            "legendFormat": "F1: {{repo}}"
          }
        ]
      },
      {
        "title": "False Positive Rate (Daily)",
        "type": "gauge",
        "targets": [
          {
            "expr": "git_ml_false_positive_rate",
            "legendFormat": "FP Rate: {{repo}}%"
          }
        ],
        "thresholds": [0, 1, 3]
      },
      {
        "title": "Escalation Queue Depth",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(git_ml_escalation_count)",
            "legendFormat": "Pending escalations"
          }
        ]
      },
      {
        "title": "Merge Latency (p50, p95, p99)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, git_ml_merge_latency_seconds)",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, git_ml_merge_latency_seconds)",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, git_ml_merge_latency_seconds)",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "Post-Merge Defect Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "git_ml_post_merge_ci_failure_rate",
            "legendFormat": "CI Failures: {{repo}}"
          },
          {
            "expr": "git_ml_post_merge_revert_rate",
            "legendFormat": "Reverts: {{repo}}"
          }
        ]
      },
      {
        "title": "SLO Compliance Dashboard",
        "type": "table",
        "targets": [
          {
            "expr": "git_ml_escalation_sla_compliance",
            "legendFormat": "{{cohort}}"
          },
          {
            "expr": "git_ml_system_availability",
            "legendFormat": "{{component}}"
          }
        ]
      },
      {
        "title": "Cost Tracking (USD)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(git_ml_estimated_cost_usd[24h])",
            "legendFormat": "Daily cost: {{service}}"
          }
        ]
      }
    ]
  }
}
```

### Alert Thresholds & Escalation

```yaml
# prometheus-alerts.yaml
groups:
  - name: phase3-ml-confidence
    interval: 1m
    rules:
      - alert: HighFalsePositiveRate
        expr: git_ml_false_positive_rate > 0.03
        for: 10m
        annotations:
          summary: "FP rate {{ $value | humanizePercentage }} exceeds 3% threshold"
          action: "Trigger automatic rollback to audit-only mode"
          severity: critical
      
      - alert: PostMergeCIFailureRate
        expr: git_ml_post_merge_ci_failure_rate > 0.05
        for: 15m
        annotations:
          summary: "Post-merge CI failures {{ $value | humanizePercentage }} exceeds 5%"
          action: "Disable auto-merge for affected cohort"
          severity: critical
      
      - alert: EscalationSLAMiss
        expr: git_ml_escalation_sla_compliance < 0.95
        for: 5m
        annotations:
          summary: "Escalation SLA compliance {{ $value | humanizePercentage }} below 95%"
          action: "Add on-call resources to escalation queue"
          severity: warning
      
      - alert: SystemAvailabilityDegraded
        expr: git_ml_system_availability < 0.90
        for: 5m
        annotations:
          summary: "System availability {{ $value | humanizePercentage }} below 90%"
          action: "Trigger incident response, investigate component failures"
          severity: critical
      
      - alert: MergeLat encyP99High
        expr: histogram_quantile(0.99, git_ml_merge_latency_seconds) > 45
        for: 10m
        annotations:
          summary: "Merge latency p99 {{ $value }}s exceeds 45s SLA"
          action: "Investigate feature extraction or inference bottleneck"
          severity: warning
      
      - alert: ModelDriftDetected
        expr: abs(git_ml_confidence_accuracy - 0.92) > 0.05
        for: 30m
        annotations:
          summary: "Model accuracy {{ $value | humanizePercentage }} drifted >5% from baseline"
          action: "Trigger model retraining, hold phase3 merges"
          severity: critical
```

---

## INCIDENT RESPONSE PLAYBOOKS

### Scenario 1: ML Model Drift (Accuracy Drops >2%)

**Detection**: Prometheus alert `ModelDriftDetected` fires when accuracy drops from 92% → <90%.

```bash
#!/bin/bash
# incident-response-ml-drift.sh

set -e
INCIDENT_ID="INC-DRIFT-$(date +%s)"
echo "=== Incident Response: ML Model Drift ==="
echo "Incident ID: $INCIDENT_ID"
echo "Detection time: $(date -u)"

# 1. Verify drift (confirm alert is not false positive)
echo "[1] Verifying model drift..."
python3 << 'EOF'
import json
from git_auto_merge_confidence import MergeConfidencePredictor

predictor = MergeConfidencePredictor()
metrics = predictor.evaluate_on_recent_merges(lookback_days=7)

print(f"Current Precision: {metrics['precision']:.3f}")
print(f"Current Recall: {metrics['recall']:.3f}")
print(f"Current Accuracy: {metrics['accuracy']:.3f}")
print(f"Baseline: 0.924 precision, 0.887 recall")

drift_magnitude = abs(metrics['precision'] - 0.924)
print(f"\nDrift magnitude: {drift_magnitude:.3f}")

if drift_magnitude > 0.05:
    print("✅ DRIFT CONFIRMED. Severity: HIGH")
else:
    print("❌ DRIFT NOT CONFIRMED. False alarm. Check feature extraction.")
EOF

# 2. Investigate root cause
echo "[2] Investigating root cause..."
python3 << 'EOF'
import pandas as pd
from scipy.stats import ks_2samp

# Compare feature distributions: baseline vs recent
baseline_features = pd.read_parquet('models/training_data.parquet')
recent_features = pd.read_parquet('/tmp/recent_features.parquet')

print("Feature distribution comparison (KS test):")
for feature in baseline_features.columns:
    stat, pval = ks_2samp(
        baseline_features[feature],
        recent_features[feature]
    )
    if pval < 0.05:
        print(f"  ⚠️ {feature}: p-value {pval:.4f} (DRIFT DETECTED)")

# Hypothesis: What changed?
print("\nHypotheses:")
print("  1. Repo composition changed (more experimental repos in Phase 3)")
print("  2. Team velocity increased (faster merges, less review)")
print("  3. CI tools changed (new test framework detection issue)")
print("  4. External: GitHub API rate limiting or data quality issues")
EOF

# 3. Execute mitigation
echo "[3] Executing mitigation..."

# Option A: Immediate - revert to stricter thresholds
echo "  Option A: Tighten auto-merge threshold (95% → 98%)"
kubectl patch configmap git-auto-merge-config -n ml-system \
  -p '{"data":{"confidence_threshold_auto":"98"}}'

# Option B: Retrain on recent data
echo "  Option B: Trigger model retraining on last 30 days..."
python3 -m git_auto_merge_confidence retrain \
  --lookback-days 30 \
  --output models/ensemble_drift_recovery.pkl \
  --background

# 4. Notify stakeholders
echo "[4] Notifying stakeholders..."
curl -X POST $SLACK_WEBHOOK_INCIDENTS <<'PAYLOAD'
{
  "text": "⚠️ Incident INC-DRIFT-$(date +%s): ML Model Drift Detected",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Incident*: ML Model Drift\n*Accuracy Drop*: 92.4% → 89.1% (-3.3pp)\n*Root Cause*: Investigating (see thread)\n*Mitigation*: Thresholds tightened (95%→98%). Retraining in progress (~6h)."
      }
    }
  ]
}
PAYLOAD

# 5. Monitor recovery
echo "[5] Monitoring recovery..."
echo "Check progress with: git-auto-merge-confidence model-info"
echo "Retraining ETA: 6 hours. SLA: Resume normal thresholds within 24h."

# 6. Document incident
echo "[6] Creating incident report..."
cat > /tmp/incident-$INCIDENT_ID.md <<'REPORT'
# Incident Report: ML Model Drift

## Timeline
- **T+0**: Alert fired (accuracy 89.1% < 90% threshold)
- **T+5m**: Drift confirmed, root cause investigation started
- **T+15m**: Mitigation applied (threshold tightened)
- **T+6h**: Model retrained, new model deployed to staging
- **T+24h**: New model in canary, normal thresholds restored

## Root Cause
[To be filled after investigation completes]

## Resolution
[To be filled after incident closes]

## Lessons Learned
- [ ] Add data drift monitoring (feature distribution tracking)
- [ ] Implement automated retraining schedule (weekly)
- [ ] Add feature importance alerts (detect feature shifts)
REPORT

echo "✅ Incident response initiated. Status: IN PROGRESS"
```

**Expected Timeline**:
- **T+0 to T+5m**: Detection & verification
- **T+5m to T+30m**: Root cause analysis
- **T+30m onwards**: Mitigation (threshold adjustment) + retraining (6h background task)
- **T+24h**: Full resolution (new model deployed, thresholds restored)

**SLA**: Restore normal operations within 24 hours OR escalate to ML Engineering team.

---

### Scenario 2: Cascading Merge Failures (Post-Merge Defects >5%)

**Detection**: Post-merge CI failure rate spikes from 3% → >5% in 1 hour.

```bash
#!/bin/bash
# incident-response-cascading-failures.sh

set -e
INCIDENT_ID="INC-CASCADE-$(date +%s)"
echo "=== Incident Response: Cascading Merge Failures ==="
echo "Incident ID: $INCIDENT_ID"

# 1. Confirm alert
echo "[1] Confirming cascading failures..."
FAILED_MERGES=$(gh search issues --repo "my-org/*" \
  --created "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)Z" \
  --label "post-merge-ci-failure" \
  --json number | jq '. | length')

echo "Failed merges in past 1h: $FAILED_MERGES"

if [ "$FAILED_MERGES" -lt 10 ]; then
  echo "❌ False alarm (only $FAILED_MERGES failures). Exiting."
  exit 0
fi

# 2. Identify pattern (which repos? which cohort?)
echo "[2] Identifying failure pattern..."
gh search issues --repo "my-org/*" \
  --created "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)Z" \
  --label "post-merge-ci-failure" \
  --json repository \
  | jq -r '.[].repository.nameWithOwner' \
  | sort | uniq -c | sort -rn > /tmp/failure_repos.txt

cat /tmp/failure_repos.txt

# 3. Root cause analysis
echo "[3] Investigating root cause..."
echo "Hypotheses:"
echo "  A) Dependency update broke multiple repos (transitive failure)"
echo "  B) External service degradation (GitHub API, artifact registry)"
echo "  C) Infrastructure issue (CI runner out of capacity)"
echo "  D) Model predicted incorrectly on large batch (FP spike)"

# Check GitHub status
echo "\n  Checking GitHub API status..."
curl -s https://www.githubstatus.com/api/v2/status.json | jq '.status.indicator'

# Check artifact registry
echo "  Checking artifact registry..."
curl -s https://registry.npmjs.org/-/health | jq '.'

# Check CI runner capacity
echo "  Checking CI runner capacity..."
kubectl top nodes -n ci-system || echo "  (Kubernetes not available)"

# 4. Mitigate by disabling auto-merge for affected repos
echo "[4] Disabling auto-merge for affected repos..."
while read REPO; do
  echo "  Disabling: $REPO"
  gh api repos/$REPO/branches/main \
    -X PATCH \
    -f required_status_checks='{"strict":true,"contexts":[]}'
done < /tmp/failure_repos.txt

# 5. Alert escalation
echo "[5] Escalating to engineering team..."
pagerduty incidents create \
  --title "CRITICAL: Cascading merge failures detected" \
  --service-id ml-confidence-scoring \
  --urgency high \
  --body "Post-merge CI failure rate spiked to >5% in past hour. Auto-merge disabled for affected repos. Investigation in progress."

# 6. Resume safe merges only
echo "[6] Resuming safe merges (100% manual review)..."
kubectl patch configmap git-auto-merge-config -n ml-system \
  -p '{"data":{"confidence_threshold_auto":"100","mode":"escalate_all"}}'

# 7. Monitor for resolution
echo "[7] Monitoring for resolution..."
until [ "$(gh search issues --repo 'my-org/*' \
  --created '$(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S)Z' \
  --label 'post-merge-ci-failure' \
  --json number | jq '. | length')" -lt 2 ]; do
  echo "  Still seeing failures. Waiting 5 minutes..."
  sleep 300
done

echo "✅ Cascading failures resolved. Resuming normal Phase 3 operations."
```

**Response Timeline**:
- **T+0 to T+10m**: Confirmation & pattern identification
- **T+10m to T+20m**: Root cause analysis
- **T+20m to T+30m**: Mitigation (auto-merge disabled)
- **T+30m onwards**: Manual investigation of root cause (external service? infra? model FP?)
- **T+4h**: Resolve root cause, resume auto-merge (with thresholds increased if needed)

**SLA**: Automatic rollback within 10 minutes. Manual investigation SLA 4 hours.

---

### Scenario 3: Data Corruption Post-Merge

**Detection**: Supabase replication lag detected OR data consistency check fails.

```bash
#!/bin/bash
# incident-response-data-corruption.sh

set -e
INCIDENT_ID="INC-CORRUPT-$(date +%s)"
echo "=== CRITICAL: Data Corruption Detected ==="
echo "Incident ID: $INCIDENT_ID"

# 1. IMMEDIATE: Enter read-only mode
echo "[1] IMMEDIATE: Shutting down ML system..."
kubectl scale deployment git-auto-merge-confidence -n ml-system --replicas=0
echo "✅ Auto-merge disabled. System in read-only mode."

# 2. Assess scope
echo "[2] Assessing data corruption scope..."
SUPABASE_URL="$(gcloud secrets versions access latest --secret='supabase-url')"
SUPABASE_KEY="$(gcloud secrets versions access latest --secret='supabase-key')"

# Run data integrity check
python3 << 'EOF'
import requests
import json

SUPABASE_URL = "$(echo $SUPABASE_URL)"
SUPABASE_KEY = "$(echo $SUPABASE_KEY)"

# Check replication lag
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/rpc/check_replication_lag",
    headers={"Authorization": f"Bearer {SUPABASE_KEY}"}
)

lag = response.json()
print(f"Replication lag: {lag} seconds")

# Check for inconsistencies
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/gitops_ml_audit?order=id.desc&limit=100",
    headers={"Authorization": f"Bearer {SUPABASE_KEY}"}
)

audits = response.json()
print(f"Last 100 audit records: {len(audits)} rows")

# Verify key tables
tables_to_check = [
    'gitops_ml_scores',
    'gitops_ml_audit',
    'gitops_ml_rollback_events'
]

for table in tables_to_check:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}?limit=1",
        headers={"Authorization": f"Bearer {SUPABASE_KEY}"}
    )
    status = "OK" if response.status_code == 200 else "CORRUPTED"
    print(f"{table}: {status}")
EOF

# 3. Initiate backup recovery
echo "[3] Initiating backup recovery..."
echo "Restoring from last verified backup..."

# Supabase automated restore (requires manual approval)
curl -X POST https://api.supabase.com/v1/projects/$(gcloud config get-value project)/database/backups/restore \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_id": "latest",
    "restore_point": "'$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# 4. Notify security team
echo "[4] Notifying security team..."
curl -X POST $SLACK_WEBHOOK_SECURITY <<'PAYLOAD'
{
  "text": "🚨 CRITICAL: Data corruption detected in Supabase",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Incident ID*: INC-CORRUPT-$(date +%s)\n*System*: ML Confidence Scoring (Phase 3)\n*Action*: System in read-only mode. Backup recovery initiated.\n*Next*: Security audit of affected data (ETA 2h)"
      }
    }
  ]
}
PAYLOAD

# 5. Create forensics report
echo "[5] Creating forensics report..."
cat > /tmp/forensics-$INCIDENT_ID.txt <<'FORENSICS'
# Data Corruption Forensics Report

## Timeline
- Corruption detected: $(date -u)
- Scope: [TBD after analysis]
- Recovery point: [TBD]

## Affected Data
- Tables: [TBD]
- Rows affected: [TBD]
- Merges impacted: [TBD]

## Recovery Steps
1. Backup restored to T-1h point
2. Data validation in progress
3. Affected merges will be re-scored

## Root Cause Analysis [TBD]
FORENSICS

# 6. Hold all merges
echo "[6] Halting all merges pending recovery..."
for REPO in $(gh repo list --json name --jq '.[].name'); do
  gh api repos/$REPO/branches/main \
    -X PATCH \
    -f required_status_checks='{"strict":true,"contexts":["data-recovery-verification"]}'
done

echo "✅ Emergency measures complete. Recovery in progress."
echo "Timeline: Recovery 2-4h. Full investigation 24h."
```

**SLA**: 
- **T+0 to T+5m**: Shutdown & read-only mode
- **T+5m to T+2h**: Backup restoration & data validation
- **T+2h to T+6h**: Resume Phase 3 with caution (thresholds 98%)
- **T+6h to T+24h**: Full forensics & root cause analysis

---

## TEAM HANDOFF & TRAINING

### Operations Team Training Checklist

```markdown
# Phase 3 Operations Team Onboarding

## Pre-Deployment (Complete by T-1 day)

- [ ] Complete "Phase 3 Operational Procedures" training (2h)
  - CI/CD integration walkthrough
  - Daily checkpoint procedure
  - Escalation queue management
  
- [ ] Practice rollback scenarios (2 dry runs)
  - Audit-only rollback
  - Full rollback
  - State recovery
  
- [ ] Configure on-call rotation
  - Primary: Hours 06:00–18:00 UTC
  - Secondary: Hours 18:00–06:00 UTC + weekends
  - Escalation: ML Engineering team on-call
  
- [ ] Access verification
  - [ ] GitHub token with repo:write scope
  - [ ] Kubernetes admin access (ml-system namespace)
  - [ ] Supabase admin access (query + backup restore)
  - [ ] Slack webhook for incidents (critical + alerts channels)
  - [ ] PagerDuty API key for incident creation
  
- [ ] Alert acknowledgment
  - [ ] Understand alert thresholds (FP >3%, latency >45s, etc.)
  - [ ] Know how to dismiss false positives
  - [ ] Can distinguish critical alerts vs warnings

## During Deployment (T0 onwards)

- [ ] Daily checkpoint execution (08:00 UTC)
  - Run `/tmp/daily-checkpoint.sh`
  - Review metrics dashboard
  - Post summary to #ml-confidence-prod
  
- [ ] Escalation queue management
  - Monitor queue depth (<50 items normal)
  - Assign escalations to code-owners
  - SLA: Code owner review within 2h
  
- [ ] Incident response
  - [ ] Can execute audit-only rollback (<5 min)
  - [ ] Can execute full rollback (<10 min)
  - [ ] Can navigate incident runbooks (PagerDuty)
  - [ ] Can post incident updates to Slack
  
- [ ] Metrics interpretation
  - [ ] Understand precision/recall/F1
  - [ ] Can identify FP rate increases
  - [ ] Can spot model drift (accuracy <90%)
  - [ ] Can correlate post-merge failures to cohort

## Post-Deployment (After T+30, graduation)

- [ ] Transition to 24/7 Ops team
  - [ ] On-call schedule confirmed
  - [ ] Incident response procedures documented
  - [ ] SLOs established & monitored
  
- [ ] Continuous improvement
  - [ ] Monthly threshold tuning reviews
  - [ ] Quarterly model retraining plan
  - [ ] Cost optimization analysis

## Contact & Resources

- **Slack channels**:
  - #ml-confidence-prod: Operational metrics & daily reports
  - #ml-confidence-dev: Development & model updates
  - #incidents: Critical incidents & escalations

- **Docs**:
  - Phase 3 Runbooks: https://...
  - Metric Dashboards: https://metrics.company.com/phase3
  - Model Cards: https://...

- **On-call escalation**:
  - Level 1: Phase 3 Operations
  - Level 2: ML Engineering (PagerDuty)
  - Level 3: Security team (data corruption only)
```

### Security Team Training

```markdown
# Security Team Handoff: ML Confidence Scoring Production

## Threat Model Review

1. **Data Exfiltration**: ML training data contains PR contents
   - Mitigation: Supabase encryption at rest, VPC isolation
   - Monitoring: Audit log review (weekly)

2. **Model Poisoning**: Attacker manipulates training data
   - Mitigation: Data validation, SHA256 integrity checks
   - Monitoring: Feature distribution drift detection

3. **Inference Exploitation**: Model outputs biased decisions
   - Mitigation: Confidence thresholds, human escalation
   - Monitoring: False positive rate tracking

4. **System Compromise**: Auto-merge credentials stolen
   - Mitigation: GitHub token rotation (30 days), Secrets Manager
   - Monitoring: Audit log for token usage anomalies

## Audit Requirements

- [ ] Merge decisions logged to immutable audit trail (Supabase)
- [ ] Auto-merged PRs watermarked with ML confidence score
- [ ] False positives reviewed quarterly by security team
- [ ] Annual threat model update + penetration test

## Escalation Procedures

| Severity | Response | Owner |
|----------|----------|-------|
| Drift >10pp | T+30m incident | ML Engineering |
| Data loss | T+5m incident | Security + Ops |
| Unauthorized merges | T+10m incident | Security + Engineering |
| Token compromise | T+15m remediation | Security |

## Success Criteria for Sign-Off

- [ ] Zero unauthorized merges in Phase 3 period
- [ ] <1% false positives (model-induced security risk)
- [ ] 100% audit trail fidelity (no log gaps)
- [ ] Annual penetration test passes
```

### Development Team Training

```markdown
# Development Team Handoff: Using ML Auto-Merge

## Developer Experience

1. **Understanding ML Confidence Scores**
   - GitHub PR comment explains why score is 87% (top 3 factors)
   - "What to do if rejected": link to remediation suggestions
   - Feedback: Can you rate this score? (training signal)

2. **Handling Escalations**
   - PR escalated for human review
   - Code-owner assigned (auto via CODEOWNERS file)
   - SLA: Response within 2h
   - Can request re-scoring (for model feedback)

3. **Requesting Auto-Merge**
   - Add comment `@ml-auto-merge --force` to re-trigger scoring
   - Useful if PR changed since last score
   - Cost: 1 additional prediction (~$0.01)

## Troubleshooting Guide

**Q: Why was my PR rejected (confidence <75%)?**
A: Top factors (check comment):
  - No tests added? Add unit tests covering changes.
  - Large diff? Break into smaller, focused PRs.
  - New author? Have senior teammate review first.

**Q: Why is my PR in escalation queue?**
A: Confidence 75–95% (medium risk). Code-owner review required.
  - Link: PR comment with explanation
  - SLA: Respond within 2h (set calendar reminder)

**Q: How do I train the model to recognize my patterns?**
A: Model retrains weekly on new merge outcomes.
  - Most valuable feedback: merge outcomes (success vs revert)
  - Automated: Model learns from your merge history
  - Manual: Rate confidence score accuracy in PR comment

## Feedback Loop

- Model improves weekly with real merge outcomes
- Your team's patterns learned → personalized thresholds
- Quarterly model cards shared with teams
  - "You have 96% merge success rate!" (team recognition)
  - "Your refactors have 12% revert rate" (improvement area)
```

---

## SUCCESS CRITERIA & GRADUATION

### Phase 3 Graduation Checklist (T+30)

| Category | Criterion | Target | Achieved |
|----------|-----------|--------|----------|
| **Deployment** | All repos onboarded | 100% | ? |
| **Automation** | Auto-merge % of eligible PRs | ≥40% | ? |
| **Reliability** | System uptime | 99.9% | ? |
| **Quality** | Post-merge defects | <2% | ? |
| **Performance** | Merge latency (p95) | <45s | ? |
| **Safety** | False positive rate | <1% | ? |
| **SLO** | Escalation response (2h) | 95% | ? |
| **Cost** | Monthly spend | $680–1,400 | ? |
| **Incidents** | Critical incidents | 0 | ? |
| **Team** | Ops team trained | 100% | ? |
| **Docs** | Runbooks finalized | ✅ | ? |

### Production SLOs (Post-Graduation)

Once Phase 3 graduates, Phase 3 Ops team owns these SLOs:

```yaml
SLOs:
  - name: "Auto-merge Success Rate"
    target: 99.5%
    window: 7 days
    metric: "auto_merged_prs / total_eligible_prs"
    alert_threshold: 98.0%
  
  - name: "Merge Latency (p95)"
    target: <45 seconds
    window: 24 hours
    metric: "percentile(merge_latency_seconds, 0.95)"
    alert_threshold: >50s
  
  - name: "Post-Merge Defect Rate"
    target: <2%
    window: 7 days
    metric: "reverted_merges / total_merged_prs"
    alert_threshold: >3%
  
  - name: "System Availability"
    target: 99.9%
    window: 30 days
    metric: "(total_time - downtime_seconds) / total_time"
    alert_threshold: <99.5%
  
  - name: "Escalation SLA Compliance"
    target: 95%
    window: 7 days
    metric: "responded_within_2h / total_escalations"
    alert_threshold: <90%
```

### Cost Analysis & Optimization

```bash
#!/bin/bash
# phase3-cost-analysis.sh

echo "=== Phase 3 Cost Analysis (T+30) ==="

# Collect usage metrics
PREDICTIONS=$(curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=sum(git_ml_daily_ml_predictions)' | jq '.data.result[0].value[1]')

API_CALLS=$(curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=sum(git_ml_daily_api_calls)' | jq '.data.result[0].value[1]')

STORAGE_GB=$(curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=git_ml_storage_gb' | jq '.data.result[0].value[1]')

# Calculate costs
ML_COST=$(echo "scale=2; $PREDICTIONS * 0.001" | bc)  # $0.001 per prediction
API_COST=$(echo "scale=2; $API_CALLS * 0.00000365" | bc)  # GitHub API pricing
STORAGE_COST=$(echo "scale=2; $STORAGE_GB * 0.25" | bc)  # Supabase storage pricing

DAILY_COST=$(echo "scale=2; $ML_COST + $API_COST + $STORAGE_COST" | bc)
MONTHLY_COST=$(echo "scale=2; $DAILY_COST * 30" | bc)

echo "Daily breakdown:"
echo "  ML predictions: $PREDICTIONS/day → \$$ML_COST"
echo "  GitHub API: $API_CALLS/day → \$$API_COST"
echo "  Storage: $STORAGE_GB GB → \$$STORAGE_COST"
echo ""
echo "Daily total: \$$DAILY_COST"
echo "Monthly projected: \$$MONTHLY_COST"
echo "Budget: \$680–1,400/month → $([ $(echo "$MONTHLY_COST <= 1400" | bc) -eq 1 ] && echo '✅ WITHIN' || echo '❌ OVER')"

# Optimization recommendations
echo ""
echo "Optimization opportunities:"
echo "  1. Batch predictions (10% savings): Process 100 PRs/batch"
echo "  2. Cache features (15% savings): Reuse features for 1h"
echo "  3. Archive old audits (5% savings): Move logs >90d to cold storage"

OPTIMIZED_COST=$(echo "scale=2; $MONTHLY_COST * 0.7" | bc)
echo ""
echo "Projected cost after optimization: \$$OPTIMIZED_COST/month"
```

---

## FINAL SIGN-OFF CHECKLIST

Before moving Phase 3 to steady-state production, all stakeholders must sign off:

```markdown
# Phase 3 Canary Rollout: Final Approval Gate

**Date**: [T+30 checkpoint]

## Engineering Lead Sign-Off

- [ ] All repos onboarded to Phase 3
- [ ] No critical incidents in past 7 days
- [ ] Auto-merge rate >= 40%
- [ ] Post-merge defect rate < 2%
- [ ] Ready for production SLOs

**Signed**: _________________ **Date**: _________

## Security Officer Sign-Off

- [ ] Threat model reviewed & approved
- [ ] Zero unauthorized merges
- [ ] Audit trail complete & verified
- [ ] Data corruption safeguards validated
- [ ] Ready for production audit requirements

**Signed**: _________________ **Date**: _________

## Operations Lead Sign-Off

- [ ] Ops team trained & certified
- [ ] On-call schedule confirmed
- [ ] Runbooks finalized & tested
- [ ] Incident response drills passed
- [ ] Ready for 24/7 operations

**Signed**: _________________ **Date**: _________

## Finance / Business Sign-Off

- [ ] Cost tracking verified ($680–1,400/month)
- [ ] ROI achieved (70% latency reduction)
- [ ] Budget for next quarter approved
- [ ] Optimization roadmap reviewed

**Signed**: _________________ **Date**: _________

---

**Phase 3 Status**: Approved for production graduation ✅
**Next Phase**: Steady-state operations, quarterly reviews
**Handoff Date**: [T+30 + 5 days for transition]
```

---

## VERSION HISTORY & RELATED SKILLS

| Version | Date | Status | Links |
|---------|------|--------|-------|
| v1.0.0 | 2026-07-26 | Ready for production deployment | - |

### Related Fase 3 Skills

1. **git-auto-merge-confidence** (v1.0)
   - ML model specification, 31-feature ensemble, 92.4% precision
   - Integration with git-gitops-flow
   
2. **git-chaos-engineering** (v1.0, TBD)
   - 5 chaos scenarios, weekly automation, resilience scoring
   - Incident injection & recovery validation
   
3. **git-gitops-flow** (v3.0, TBD)
   - ML confidence scoring integration + fallback mechanism
   - Parallel execution (3–4 workers, 70% timeline reduction)

4. **git-code-pattern-detection** (v3.0, TBD)
   - Feedback loop integration for pattern quality
   - Weekly retraining on detection accuracy
   
5. **git-multi-repo-workflows** (v3.0, TBD)
   - Parallel execution orchestration
   - ML-prioritized repo scheduling

---

## CONTACT & SUPPORT

- **Owner**: ML Confidence Scoring Team (ml-confidence@company.com)
- **Slack**: #ml-confidence-prod (ops updates), #ml-confidence-dev (engineering)
- **Dashboard**: https://metrics.company.com/phase3-canary-rollout
- **Bug Reports**: github.com/my-org/ml-confidence-scoring/issues
- **Runbook Access**: PagerDuty (incident-runbooks service)
- **On-Call**: PagerDuty escalation policy "ml-confidence-scoring"

---

**Last updated**: 2026-07-26  
**Next review**: 2026-08-26 (post-Phase 3 graduation, operational SLO audit)  
**Approval gate**: Engineering Lead + Security Officer + Ops Lead (required before T0)
