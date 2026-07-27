# 🚀 PRODUCTION DEPLOYMENT HANDOFF
## Manta Maestro Optimization Package v1.0

**Approval Date:** 2026-07-27  
**Approved By:** mneves@mantaassociados.com  
**Deployment Target:** Production (Kubernetes cluster)  
**Expected Downtime:** 0 minutes (blue-green deployment)  

---

## 📦 EXECUTIVE SUMMARY

4 production-ready initiatives approved for deployment:

1. **Fine-Tuning Contínuo** — Saneamento (AySA priority)
2. **Feedback Analytics** — Weekly aggregation + auto-retraining triggers
3. **Performance Tuning** — Redis cache, pgvector HNSW, smart model selection
4. **Kubernetes Auto-Scaling** — HPA with custom metrics

**Total:** 38 files, 11,000+ lines of code, 6 Grafana dashboards, 25+ Prometheus alerts

---

## 🏃 QUICKSTART DEPLOYMENT (2-3 hours)

### Prerequisites
```bash
# Verify kubectl context
kubectl config current-context  # should be: production-cluster

# Verify Helm is installed
helm version  # v3.12+

# Verify PostgreSQL 15+ with pgvector
psql -h $DB_HOST -U $DB_USER -d manta -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Verify Redis is running
redis-cli -h $REDIS_HOST ping  # should return: PONG
```

### Step 1: Deploy Infrastructure (30 min)

```bash
cd /home/user/Codex-exemplo

# 1a. Apply database migrations
alembic upgrade head

# Output should include:
# - pgvector extension enabled
# - 6 new tables: rag_chunks (with embedding), fine_tune_jobs, feedback_alerts, etc.
# - HNSW index created on rag_chunks(embedding)
# - RLS policies applied for multi-tenant isolation

# 1b. Install/Upgrade Prometheus Adapter
kubectl apply -f manta-helm/templates/prometheus-adapter-configmap.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  -f monitoring/prometheus-adapter-values.yaml \
  -n monitoring --create-namespace

# 1c. Deploy HPA templates
helm upgrade manta manta-helm/ \
  --values manta-helm/values.yaml \
  --values manta-helm/values-production.yaml \
  --wait \
  --timeout 10m

# Output should include:
# - FastAPI HPA created (min:2, max:10, 70% CPU)
# - React HPA created (min:1, max:5, 75% CPU)
# - PostgreSQL HPA created (min:1, max:3)
# - Ingress updated with health checks

# 1d. Deploy fine-tuning infrastructure
kubectl set image deployment/fastapi \
  fastapi=manta-backend:latest \
  --record

# 1e. Restart FastAPI to pick up new endpoints
kubectl rollout restart deployment/fastapi
kubectl rollout status deployment/fastapi --timeout=5m
```

### Step 2: Validate Infrastructure (20 min)

```bash
# 2a. Verify Metrics Server is ready
kubectl get deployment metrics-server -n kube-system
# Expected: READY 1/1

# 2b. Verify HPA status
kubectl get hpa -o wide
# Expected output:
# NAME          REFERENCE                     TARGETS       MINPODS MAXPODS REPLICAS
# fastapi       Deployment/fastapi            70%/70%       2       10      3
# react         Deployment/react              75%/75%       1       5       1
# postgres      StatefulSet/postgres          80%/80%       1       3       1

# 2c. Verify custom metrics are available
kubectl get --all-namespaces --all \
  | grep "custom.metrics.k8s.io"
# Expected: custom.metrics.k8s.io/v1beta1

# 2d. Verify database HNSW index
psql -h $DB_HOST -U $DB_USER -d manta << 'EOF'
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE indexname LIKE '%hnsw%';
EOF
# Expected: Index on rag_chunks(embedding) with algorithm=hnsw

# 2e. Verify Redis connectivity
redis-cli -h $REDIS_HOST --latency
# Expected: latency < 5ms
```

### Step 3: Import Grafana Dashboards (15 min)

```bash
# Login to Grafana UI at http://grafana.manta.example.com

# 3a. Import Performance Overview
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @manta-backend/monitoring/grafana/dashboards/performance-overview.json

# 3b. Import Cache Analytics
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @manta-backend/monitoring/grafana/dashboards/cache-analytics.json

# 3c. Import PostgreSQL Performance
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @manta-backend/monitoring/grafana/dashboards/postgresql-performance.json

# 3d. Import Model Cost Analysis
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @manta-backend/monitoring/grafana/dashboards/model-cost-analysis.json

# 3e. Import HPA Scaling Dashboard
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @monitoring/grafana-hpa-dashboard.json

# 3f. Import Feedback Analytics Dashboard
curl -X POST http://grafana.manta.example.com/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -d @monitoring/grafana-feedback-dashboard.json
```

### Step 4: Enable Features (10 min)

```bash
# 4a. Enable fine-tuning (via environment variable)
kubectl set env deployment/fastapi \
  FINETUNING_ENABLED=true \
  FINETUNING_STORAGE=s3  # or local for dev
  
# 4b. Enable feedback analytics
kubectl set env deployment/fastapi \
  FEEDBACK_ANALYTICS_ENABLED=true \
  FEEDBACK_ALERT_THRESHOLD=3.5 \
  FEEDBACK_RETRAINING_THRESHOLD=3.0

# 4c. Enable cache layer
kubectl set env deployment/fastapi \
  CACHE_ENABLED=true \
  REDIS_HOST=$REDIS_HOST \
  REDIS_PORT=6379 \
  CACHE_TTL_SECONDS=300

# 4d. Enable smart model selection
kubectl set env deployment/fastapi \
  SMART_MODEL_SELECTION=true \
  MODEL_HAIKU_MAX_CHARS=500 \
  MODEL_SONNET_MAX_CHARS=2000

# 4e. Restart to apply all changes
kubectl rollout restart deployment/fastapi
kubectl rollout status deployment/fastapi --timeout=5m
```

### Step 5: Run Smoke Tests (10 min)

```bash
cd /home/user/Codex-exemplo

# 5a. Test fine-tuning endpoint
curl -X POST http://api.manta.example.com/ml/finetune \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "segment": "saneamento",
    "epochs": 1,
    "demo_mode": true
  }'
# Expected: 202 Accepted with job_id

# 5b. Test feedback analytics endpoint
curl -X GET "http://api.manta.example.com/feedback/analytics/by-agent?limit=10" \
  -H "Authorization: Bearer ${API_TOKEN}"
# Expected: 200 OK with agent ratings

# 5c. Test cache endpoint
curl -X GET "http://api.manta.example.com/monitoring/cache-stats" \
  -H "Authorization: Bearer ${API_TOKEN}"
# Expected: 200 OK with hit_rate, evictions, etc.

# 5d. Test semantic search (cache should kick in)
curl -X GET "http://api.manta.example.com/search?q=ETA%20tratamento&limit=5" \
  -H "Authorization: Bearer ${API_TOKEN}"
# Expected: 200 OK with results + X-Cache-Hit header

# 5e. Test HPA is scaling
kubectl get hpa fastapi -w  # watch for scaling events
# Expected: TARGETS fluctuates around 70%
```

### Step 6: Monitor Live (Continuous)

```bash
# Watch HPA scaling in real-time
watch -n 2 'kubectl get hpa'

# Watch pod replica changes
watch -n 2 'kubectl get pods -l app=fastapi'

# Tail FastAPI logs
kubectl logs -f deployment/fastapi --all-containers=true

# Check Grafana dashboards (every 5 min for first hour):
# - Performance Overview: p99 latency < 2s?
# - Cache Analytics: hit_rate > 70%?
# - HPA Dashboard: scaling events occurring?
# - Feedback Analytics: data flowing in?

# Check AlertManager for any firing alerts
kubectl logs -f deployment/alertmanager
```

---

## 🔄 DEPLOYMENT PHASES

### Phase 1: Infrastructure (Hour 0-1)
- [ ] Database migrations applied
- [ ] Prometheus Adapter installed
- [ ] HPA templates deployed
- [ ] FastAPI restarted with new code
- **Owner:** DevOps / Database Team

### Phase 2: Validation (Hour 1-2)
- [ ] Metrics Server ready
- [ ] HPA status verified
- [ ] Database indexes confirmed
- [ ] Redis connectivity tested
- **Owner:** Platform Engineering

### Phase 3: Monitoring (Hour 2-2.5)
- [ ] 6 Grafana dashboards imported
- [ ] Slack alerts configured
- [ ] PagerDuty escalation ready
- **Owner:** SRE / Monitoring Team

### Phase 4: Go-Live (Hour 2.5-3)
- [ ] Fine-tuning feature flag enabled
- [ ] Feedback analytics enabled
- [ ] Cache layer enabled
- [ ] Smart model selection enabled
- [ ] All systems restarted
- **Owner:** Engineering Lead

### Phase 5: Post-Launch Monitoring (Hour 3+, first 24h)
- [ ] Continuous dashboard monitoring
- [ ] Real-time alert evaluation
- [ ] Performance metric validation
- [ ] Rollback plan on standby
- **Owner:** On-Call Engineer + SRE

---

## 🚨 ROLLBACK PROCEDURES

### Quick Rollback (< 5 minutes)
```bash
# 1. Disable all new features
kubectl set env deployment/fastapi \
  FINETUNING_ENABLED=false \
  FEEDBACK_ANALYTICS_ENABLED=false \
  CACHE_ENABLED=false \
  SMART_MODEL_SELECTION=false

# 2. Restart with old configuration
kubectl rollout restart deployment/fastapi

# 3. Delete HPA (goes back to manual replicas)
kubectl delete hpa --all

# 4. Scale back to pre-deployment replicas
kubectl scale deployment fastapi --replicas=2
kubectl scale deployment react --replicas=1

# 5. Verify
kubectl get pods -l app=fastapi
```

### Complete Rollback (if critical issue)
```bash
# Rollback to previous image tag
kubectl set image deployment/fastapi \
  fastapi=manta-backend:v4.2-stable \
  --record

kubectl rollout status deployment/fastapi --timeout=5m

# Rollback database (if schema issue)
alembic downgrade -1
```

**Rollback triggers:**
- Error rate > 5% for 5 minutes
- Latency p99 > 10s for 10 minutes
- Any unhandled exception in fine-tuning/feedback/cache critical path
- HPA thrashing (scale up/down > 5x in 10 minutes)

---

## 📞 SUPPORT & ESCALATION

### On-Call Contacts
| Tier | Owner | Slack | Response Time |
|------|-------|-------|----------------|
| 🔴 Critical | @devops-lead | #manta-incidents | 5 min |
| 🟡 High | @ml-engineer | #manta-alerts | 15 min |
| 🟠 Medium | @sre-team | #manta-platform | 1 hour |
| 🟢 Low | @support-team | #manta-feedback | 4 hours |

### Common Issues & Fixes

#### Issue: HPA not scaling
```bash
# Check metrics
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/*/cpu_usage

# Check Prometheus Adapter logs
kubectl logs -n monitoring deployment/prometheus-adapter

# Solution: Restart metrics-server
kubectl rollout restart deployment/metrics-server -n kube-system
```

#### Issue: Cache hit rate low (< 60%)
```bash
# Check Redis connectivity
redis-cli -h $REDIS_HOST ping

# Check cache stats
curl http://api.manta.example.com/monitoring/cache-stats

# Solution: Flush stale cache
redis-cli -h $REDIS_HOST FLUSHDB

# Or: Increase TTL
kubectl set env deployment/fastapi CACHE_TTL_SECONDS=600
```

#### Issue: Semantic search latency high (> 2s p95)
```bash
# Check pgvector index
psql -h $DB_HOST -U $DB_USER -d manta << 'EOF'
EXPLAIN (ANALYZE, BUFFERS)
SELECT embedding <-> ARRAY[0.1,0.2,...]::vector
FROM rag_chunks LIMIT 10;
EOF

# Solution: Reindex if needed
REINDEX INDEX CONCURRENTLY rag_chunks_embedding_idx;
```

#### Issue: Fine-tuning jobs stuck
```bash
# Check job status
curl http://api.manta.example.com/ml/finetune?status=running

# Check logs
kubectl logs -f deployment/fastapi --tail=100 | grep finetune

# Kill stuck job (admin only)
curl -X DELETE http://api.manta.example.com/ml/finetune/{job_id} \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

---

## 📊 SUCCESS CRITERIA (Post-Deployment)

**Must have (within 1 hour):**
- ✅ All pods healthy (no restarts)
- ✅ Zero critical alerts
- ✅ API responding (p50 < 500ms)
- ✅ Error rate < 0.5%

**Should have (within 4 hours):**
- ✅ Cache hit rate > 60% (target 70%)
- ✅ HPA scaling observed (at least 1 scale event)
- ✅ Semantic search p95 < 1s
- ✅ Feedback data flowing in

**Nice to have (within 24 hours):**
- ✅ Cache hit rate > 70%
- ✅ Model cost savings validated (30% reduction)
- ✅ Auto-retraining trigger tested
- ✅ All dashboards populated with data

---

## 📝 SIGN-OFF

```
DEPLOYMENT APPROVED: ✅ YES
APPROVAL DATE: 2026-07-27
APPROVAL AUTHORITY: mneves@mantaassociados.com

DEPLOYMENT OWNER: [DevOps Lead Name]
SCHEDULED START: [Date/Time]
EXPECTED COMPLETION: [Date/Time +3 hours]

PREPARED BY: Claude Code (AI)
REVIEWED BY: [Engineering Lead Name]
AUTHORIZED BY: [CTO/Ops Director Name]

STATUS: READY FOR PRODUCTION DEPLOYMENT
```

---

## 📚 REFERENCE DOCUMENTATION

- Fine-Tuning Guide: `docs/FINETUNING_GUIDE.md`
- Feedback Analytics: `docs/FEEDBACK_ANALYTICS.md`
- Performance Tuning: `docs/PERFORMANCE_TUNING.md`
- Auto-Scaling Guide: `docs/AUTOSCALING_GUIDE.md`
- HPA Runbook: `docs/HPA_RUNBOOK.md`
- API Reference: `docs/API_REFERENCE.md`
- Troubleshooting: `docs/RUNBOOKS.md`

**Last Updated:** 2026-07-27  
**Version:** 1.0  
**Status:** PRODUCTION APPROVED ✅
