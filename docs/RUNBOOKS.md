# Manta Maestro — Operational Runbooks v1.0

**Audience:** DevOps, On-Call Engineers  
**Updated:** 2026-07-27  
**Escalation Contact:** [INCIDENT_COMMANDER_PHONE]

---

## ALERT: High Latency (p95 > 5s)

### Severity: CRITICAL 🔴

**Symptoms:**
- Prometheus alert: `manta_api_latency_p95_seconds > 5`
- Grafana dashboard shows red
- User complaints about slow responses

**Potential Causes:**
1. Database connection pool exhausted
2. Slow queries blocking other requests
3. High CPU/memory utilization
4. Network latency to upstream service (Claude API, MCP gateway)
5. Pod memory leak causing garbage collection pauses

### Investigation Steps

**1. Check pod logs (first 3 minutes)**

```bash
# Get recent errors from FastAPI pods
kubectl logs -n manta-prod deployment/manta-fastapi --tail=100 | grep -i error

# Check for OOM kill events
kubectl describe node | grep -i memory

# Watch real-time metrics
kubectl top pods -n manta-prod --sort-by memory
```

**2. Inspect database metrics**

```bash
# Connect to PostgreSQL
psql -h postgres-primary.manta-prod.svc.cluster.local -U manta_user -d manta_db

-- Check connection count
SELECT count(*) FROM pg_stat_activity;

-- Find slow queries (> 5s)
SELECT query, total_time, calls FROM pg_stat_statements 
WHERE total_time > 5000 ORDER BY total_time DESC LIMIT 10;

-- Check connection pool state
SELECT * FROM pg_stat_activity WHERE state != 'idle';
```

**3. Check Redis cache**

```bash
# Connect to Redis
redis-cli -h redis-cache.manta-prod.svc.cluster.local

# Monitor commands in real-time
MONITOR

# Check memory usage
INFO memory

# Check for expired keys
DBSIZE
```

**4. View Jaeger traces**

- Go to: `https://jaeger.manta.example.com`
- Filter by service: `manta-fastapi`
- Look for spans with duration > 5s
- Identify bottleneck: Database? Claude API? Serialization?

### Remediation

**Option A: Database Connection Pool (most common)**

```bash
# Increase pool size temporarily (requires deployment restart)
kubectl set env deployment/manta-fastapi \
  DB_POOL_MIN=10 DB_POOL_MAX=100 -n manta-prod

# Monitor effect
kubectl logs -f deployment/manta-fastapi | grep "pool"
```

**Option B: Restart affected pod**

```bash
# Kill a single pod to force restart (K8s will reschedule)
kubectl delete pod -l app=manta-fastapi -n manta-prod

# Watch for recovery
kubectl get pods -n manta-prod -w
```

**Option C: Rollback recent deployment**

```bash
# Check deployment history
kubectl rollout history deployment/manta-fastapi -n manta-prod

# Rollback to previous version
kubectl rollout undo deployment/manta-fastapi -n manta-prod

# Verify
kubectl get deployment -n manta-prod -o wide
```

**Option D: Scale up (if load is high)**

```bash
kubectl scale deployment/manta-fastapi --replicas=6 -n manta-prod
```

### Validation

✅ Check if p95 latency returns below 5s within 5 minutes  
✅ Verify error rate < 0.1%  
✅ Confirm user-facing tests pass  

### Postmortem

- Root cause: ________________
- Why was it missed: ________________
- Prevention: ________________

---

## ALERT: Low Routing Accuracy (< 90%)

### Severity: HIGH 🟠

**Symptoms:**
- Prometheus alert: `manta_routing_accuracy < 0.9`
- Wrong agents being selected for user prompts
- Support tickets about "wrong team got assigned"

**Potential Causes:**
1. Feedback loop indicates model drift
2. New segment (S6-S10) not trained on latest patterns
3. Recent deployment of new routing model regression
4. Training data distribution shift

### Investigation Steps

**1. Check feedback data**

```bash
# Query recent feedback to see patterns
psql -h postgres-primary -d manta_db

SELECT agent_id, COUNT(*) as count, AVG(rating) as avg_rating
FROM feedback
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY agent_id
ORDER BY count DESC;

-- Check false positives
SELECT input_text, predicted_agent, correct_agent, confidence
FROM routing_feedback
WHERE predicted_agent != correct_agent
LIMIT 20;
```

**2. Check model version**

```bash
# Get current routing model version
kubectl get configmap manta-config -o jsonpath='{.data.ROUTING_MODEL_VERSION}'

# Expected: routing-classifier-v2.3
# If older, may be stale training
```

**3. Analyze test set performance**

```bash
# Run evaluation on recent data
python3 ml/evaluate_routing.py \
  --model-version routing-classifier-v2.3 \
  --test-days 7 \
  --output metrics.json

# Expected accuracy >= 0.92
```

### Remediation

**Option A: Retrain routing classifier**

```bash
# Submit retraining job
curl -X POST https://api.manta.example.com/routing/retrain \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lookback_days": 30,
    "test_split": 0.2,
    "hyperparams": {
      "learning_rate": 1e-4,
      "epochs": 15,
      "batch_size": 32
    }
  }'

# Monitor job status
curl -X GET https://api.manta.example.com/routing/retrain/job_xyz789 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Option B: Rollback to previous model**

```bash
# Get model history
kubectl get configmap manta-models -o yaml

# Revert to previous version
kubectl patch configmap manta-config --type merge \
  -p '{"data":{"ROUTING_MODEL_VERSION":"routing-classifier-v2.2"}}'

# Restart FastAPI pods to pick up new config
kubectl rollout restart deployment/manta-fastapi -n manta-prod
```

**Option C: Add human feedback loop**

```bash
# Tag recent misclassifications for manual review
psql -h postgres-primary -d manta_db

UPDATE routing_feedback
SET human_verified = true, corrected_agent = 'agent_s8_saneamento'
WHERE predicted_agent != correct_agent AND created_at > NOW() - INTERVAL '24 hours';

-- Retrain with human corrections
```

### Validation

✅ Confirm accuracy >= 0.90 on fresh test set  
✅ Verify specific segment (S1-S10) accuracies individually  
✅ A/B test new model on 10% traffic first  

---

## ALERT: Out of Storage

### Severity: CRITICAL 🔴

**Symptoms:**
- Alert: `manta_storage_available_percent < 10`
- Pod failures: `DiskPressure`
- New document uploads failing

**Investigation Steps**

```bash
# Check disk usage
kubectl describe nodes | grep -A 5 "Allocated resources"

# Find large files
kubectl exec -it pod/postgres-primary-0 -- df -h /data

# Check which tables consume space
psql -h postgres-primary -d manta_db

SELECT schemaname, tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### Remediation

**Option A: Clean old sessions**

```bash
# Delete sessions older than 90 days
psql -h postgres-primary -d manta_db

DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '90 days';
VACUUM FULL;

-- Expected space freed: 10-30GB
```

**Option B: Archive logs to S3**

```bash
# Move Loki logs to cold storage
kubectl exec -it pod/loki-0 -- bash

# Manually archive old log chunks
aws s3 sync /loki/chunks s3://manta-backups/loki-archive/$(date +%Y%m%d)/ \
  --storage-class GLACIER

# Remove local copies after confirmation
rm -rf /loki/chunks/2026-06-*
```

**Option C: Expand PersistentVolume**

```bash
# Scale up the PV (requires downtime or snapshot restore)
kubectl patch pvc postgres-data -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# Restart PostgreSQL to apply
kubectl delete pod postgres-primary-0
# K8s will reschedule with larger volume

# Verify
kubectl get pvc postgres-data -o wide
```

**Option D: Prune old documents from RAG**

```bash
psql -h postgres-primary -d manta_db

-- Delete documents older than 1 year
DELETE FROM rag_documents 
WHERE created_at < NOW() - INTERVAL '365 days'
AND project_id NOT IN (SELECT id FROM active_projects);

-- Reclaim space
VACUUM FULL rag_chunks;

-- Expected space freed: 5-20GB
```

### Validation

✅ Disk usage < 80%  
✅ No more DiskPressure on nodes  
✅ New uploads succeed  

---

## ALERT: Database Failover (Primary → Standby)

### Severity: CRITICAL 🔴

**Symptoms:**
- PostgreSQL primary pod not responding
- Alert: `manta_postgres_replication_lag_seconds > 10`
- Connection errors from FastAPI

### Manual Failover Procedure

**Step 1: Verify primary is unavailable**

```bash
# Try to connect
psql -h postgres-primary.manta-prod.svc.cluster.local -c "SELECT 1"

# If timeout, primary is down
```

**Step 2: Promote standby to primary**

```bash
# Connect to standby via kubectl
kubectl exec -it pod/postgres-standby-0 -- psql -U postgres

-- Promote to primary
SELECT pg_promote();

-- Verify it's now primary
SELECT pg_is_in_recovery();  -- Should return 'f' (false)

-- Check replicated WAL
SELECT * FROM pg_stat_replication;
```

**Step 3: Update connection string**

```bash
# Update DNS or connection pool to point to new primary
kubectl patch service postgres-primary \
  -p '{"spec":{"selector":{"statefulset.kubernetes.io/pod-name":"postgres-standby-0"}}}'

# Verify from FastAPI
kubectl logs deployment/manta-fastapi | grep "connected to"
```

**Step 4: Restart FastAPI pods**

```bash
# Force reconnection to new primary
kubectl rollout restart deployment/manta-fastapi

# Verify
kubectl get pods -l app=manta-fastapi
```

**Step 5: Bring up new standby (when primary recovers)**

```bash
# Restore primary as a standby replica
kubectl exec -it pod/postgres-primary-0 -- bash

# Reset the cluster to be a replica
rm -rf /data/recovery.signal
pg_ctl start

# It should auto-connect as standby (configured in recovery.conf)
SELECT pg_is_in_recovery();  -- Should return 't' (true)
```

### Validation

✅ All connections successful  
✅ Replication lag < 100ms  
✅ Backup jobs running normally  

---

## ALERT: API Error Rate > 1%

### Severity: HIGH 🟠

**Symptoms:**
- Alert: `manta_api_errors_total / manta_api_requests_total > 0.01`
- 5xx errors spiking

**Investigation**

```bash
# Check error logs
kubectl logs deployment/manta-fastapi --tail=200 | grep "ERROR\|Exception"

# Count by endpoint
kubectl logs deployment/manta-fastapi --tail=1000 | \
  grep "ERROR" | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
```

**Remediation**

```bash
# Option 1: Restart affected pods
kubectl rollout restart deployment/manta-fastapi

# Option 2: Check for recent deployment issues
kubectl rollout history deployment/manta-fastapi
kubectl describe deployment manta-fastapi

# Option 3: Scale up if load is high
kubectl scale deployment/manta-fastapi --replicas=6
```

---

## ALERT: Memory Pressure (> 85%)

### Severity: HIGH 🟠

**Investigation**

```bash
kubectl top nodes
kubectl top pods -n manta-prod --sort-by memory

# Check for memory leaks
kubectl logs deployment/manta-fastapi --since=1h | grep -i "memory\|gc"
```

**Remediation**

```bash
# Restart pod to free memory
kubectl delete pod -l app=manta-fastapi

# Or scale up to distribute load
kubectl scale deployment/manta-fastapi --replicas=6
```

---

## ALERT: Kubernetes Node NotReady

### Severity: CRITICAL 🔴

**Investigation**

```bash
# Check node status
kubectl describe node node-name

# Look at events
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -20
```

**Remediation**

```bash
# Cordon node (prevent new pods)
kubectl cordon node-name

# Drain pods gracefully
kubectl drain node-name --ignore-daemonsets --delete-emptydir-data

# Reboot node
ssh admin@node-ip sudo reboot

# Uncordon after reboot
kubectl uncordon node-name

# Verify
kubectl get nodes
```

---

## ALERT: Certificate Expiration < 7 days

### Severity: MEDIUM 🟡

**Investigation**

```bash
# Check TLS certificate expiry
kubectl get secret tls-secret -o jsonpath='{.data.tls\.crt}' | base64 --decode | openssl x509 -noout -dates
```

**Remediation**

```bash
# Renew certificate (Let's Encrypt auto-renewal should handle this)
# If manual renewal needed:

curl -X POST https://api.example.com/admin/renew-tls \
  -H "X-Admin-Token: $ADMIN_TOKEN"

# Monitor renewal
kubectl logs -f deployment/cert-manager
```

---

## INCIDENT: Service Restart Loop

### Severity: CRITICAL 🔴

**Symptoms:**
- Pod in `CrashLoopBackOff` state
- Restart count keeps incrementing

**Remediation**

```bash
# Get pod logs to find root cause
kubectl logs pod-name --previous

# Common causes:
# 1. Dependency not available (DB, Redis)
kubectl get service postgres-primary
kubectl get service redis-cache

# 2. Config error
kubectl describe configmap manta-config

# 3. Resource limit exceeded
kubectl describe pod pod-name | grep -A 10 "Limits"

# Fix: Increase resource limits
kubectl set resources deployment/manta-fastapi \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1024Mi
```

---

## INCIDENT: MCP Gateway Unavailable

### Severity: HIGH 🟠

**Investigation**

```bash
# Test connectivity to MCP gateway
curl -v https://mcp-gateway.example.com/health

# Check pod status
kubectl get pods -n mcp-system
kubectl logs deployment/mcp-gateway -n mcp-system

# Check network policy
kubectl get networkpolicy -n manta-prod
```

**Remediation**

```bash
# If network issue, check service
kubectl describe service mcp-gateway

# Restart MCP gateway
kubectl rollout restart deployment/mcp-gateway -n mcp-system

# Check if auth credentials expired
kubectl get secret mcp-credentials -o yaml
# If expired, update with new token

# Verify
curl https://mcp-gateway.example.com/health
```

---

## ROLLBACK PROCEDURES

### Code Rollback (Fast Path)

```bash
# Get deployment history
kubectl rollout history deployment/manta-fastapi

# Rollback to previous revision (1 step back)
kubectl rollout undo deployment/manta-fastapi --to-revision=15

# Verify rollback
kubectl rollout status deployment/manta-fastapi

# If multiple revisions back needed
kubectl rollout undo deployment/manta-fastapi --to-revision=10
```

### Database Schema Rollback

```bash
# Get current schema version
psql -h postgres-primary -d manta_db -c "SELECT version FROM alembic_version;"

# Downgrade schema
alembic downgrade base

# Or to specific version
alembic downgrade ae1028ead8ac

# Verify
psql -h postgres-primary -d manta_db -c "SELECT version FROM alembic_version;"
```

### Model Adapter Rollback

```bash
# Disable new model deployment
kubectl patch deployment manta-fastapi -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"fastapi","env":[{"name":"ENABLE_ADAPTER","value":"false"}]}]}}}}'

# Restart to apply
kubectl rollout restart deployment/manta-fastapi

# Verify baseline model is used
curl https://api.manta.example.com/ml/status | grep model_name
```

---

## ESCALATION

### Severity Levels

| Severity | Escalate to | Response SLA | Example |
|----------|------------|------------|---------|
| 🔴 CRITICAL | Incident Commander + CTO | < 15 min | Outage, data loss |
| 🟠 HIGH | On-Call DevOps + Product | < 1 hour | Degradation, error spike |
| 🟡 MEDIUM | On-Call Ops | < 4 hours | Minor issues |
| 🟢 LOW | Ticket system | < 24 hours | Cosmetic issues |

### Escalation Chain

1. **On-Call Engineer** → Triage & initial investigation (0-15 min)
2. **Incident Commander** (if critical) → Coordinate response
3. **CTO/VP Eng** (if > 1h outage) → Business decision
4. **Customer Success** (if customer-facing) → Communication

---

**Last Updated:** 2026-07-27  
**On-Call Schedule:** https://pagerduty.example.com  
**War Room:** [SLACK_CHANNEL] or Zoom link in PagerDuty incident
