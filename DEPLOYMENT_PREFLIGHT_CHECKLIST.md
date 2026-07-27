# 📋 DEPLOYMENT PRE-FLIGHT CHECKLIST

**Project:** Manta Maestro Production Deployment  
**Date:** 2026-07-27  
**Approval:** mneves@mantaassociados.com  
**Duration:** 2-3 hours  

---

## ✅ REQUIREMENT VERIFICATION

### Infrastructure Access

- [ ] **Kubernetes Cluster Access**
  - [ ] kubectl configured and working
  - [ ] Context set to production cluster: `kubectl config current-context`
  - [ ] At least 5GB disk space available on nodes
  - [ ] Network connectivity from this machine to cluster

- [ ] **Database Access**
  - [ ] PostgreSQL 15+ running and accessible
  - [ ] pgvector extension installed: `SELECT * FROM pg_extension WHERE extname = 'vector'`
  - [ ] Database user credentials available: `$DB_USER` / `$DB_PASSWORD`
  - [ ] Can connect: `PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d manta -c "SELECT 1"`

- [ ] **Redis Access**
  - [ ] Redis cluster running and accessible
  - [ ] Can connect: `redis-cli -h $REDIS_HOST -p $REDIS_PORT ping`
  - [ ] Returns `PONG`
  - [ ] Port 6379 accessible from Kubernetes cluster

- [ ] **Container Registry**
  - [ ] Docker/Container registry credentials configured
  - [ ] Latest image pulled: `manta-backend:latest`
  - [ ] Image tag matches deployment config

### Tools & Dependencies

- [ ] **kubectl** (v1.24+)
  ```bash
  kubectl version --client
  ```

- [ ] **Helm** (v3.12+)
  ```bash
  helm version --short
  ```

- [ ] **alembic** (for database migrations)
  ```bash
  cd manta-backend && alembic current
  ```

- [ ] **psql** (PostgreSQL client, optional but recommended)
  ```bash
  psql --version
  ```

- [ ] **redis-cli** (Redis client, optional but recommended)
  ```bash
  redis-cli --version
  ```

- [ ] **curl** (for smoke tests)
  ```bash
  curl --version
  ```

### Environment Variables

Create a `.env.production` file with these variables:

```bash
# Kubernetes
KUBE_NAMESPACE=default
HELM_RELEASE=manta

# Database
DB_HOST=your-postgres-host
DB_USER=manta
DB_PASSWORD=your-secure-password
DB_PORT=5432

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379

# Service URLs
API_URL=https://api.manta.example.com
GRAFANA_URL=https://grafana.manta.example.com
GRAFANA_API_TOKEN=your-grafana-api-token

# Helm
HELM_CHART=./manta-helm
```

**Validation:**
```bash
source .env.production
echo "Database: $DB_HOST"
echo "Redis: $REDIS_HOST"
echo "API: $API_URL"
```

- [ ] All environment variables set
- [ ] Can access all hostnames via ping/curl
- [ ] Credentials tested and working

### Slack & Monitoring

- [ ] **Slack Webhook** (optional, for alerts)
  - [ ] Create incoming webhook: https://api.slack.com/messaging/webhooks
  - [ ] URL available as `$SLACK_WEBHOOK_URL`
  - [ ] Test webhook: `curl -X POST $SLACK_WEBHOOK_URL -d '{...}'`

- [ ] **Grafana API Token**
  - [ ] Login to Grafana at `$GRAFANA_URL`
  - [ ] Create API token: Admin → API Keys → New API Key
  - [ ] Token saved as `GRAFANA_API_TOKEN`
  - [ ] Token has Editor role

- [ ] **PagerDuty** (optional, for critical alerts)
  - [ ] Integration key available if using PagerDuty
  - [ ] Configured in alertmanager config

### Kubernetes Cluster Pre-Checks

- [ ] **Node Status**
  ```bash
  kubectl get nodes
  # All nodes should be Ready
  ```

- [ ] **Current Deployments**
  ```bash
  kubectl get deployments
  # Review any existing deployments
  ```

- [ ] **Available Storage**
  ```bash
  kubectl get pvc
  # Ensure persistent volumes available for PostgreSQL StatefulSet
  ```

- [ ] **Helm Repos Updated**
  ```bash
  helm repo update
  # Should complete without errors
  ```

- [ ] **RBAC & Permissions**
  - [ ] User can create deployments: `kubectl auth can-i create deployments`
  - [ ] User can create services: `kubectl auth can-i create services`
  - [ ] User can create statefulsets: `kubectl auth can-i create statefulsets`

### Database Pre-Checks

- [ ] **Backup Existing Data**
  ```bash
  # Create backup
  PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d manta > manta_backup_$(date +%Y%m%d_%H%M%S).sql
  
  # Verify backup size
  ls -lh manta_backup_*.sql
  ```

- [ ] **Check Existing Data**
  ```bash
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d manta << 'EOF'
  SELECT tablename FROM pg_tables WHERE schemaname='public';
  EOF
  ```

- [ ] **Verify Alembic History**
  ```bash
  cd manta-backend
  alembic current
  # Should show current migration version
  ```

### Network & Firewall

- [ ] **Ingress/LoadBalancer**
  - [ ] DNS configured (if using DNS names)
  - [ ] Firewall rules allow traffic to K8s services
  - [ ] SSL/TLS certificates ready (if using HTTPS)

- [ ] **Cluster Network**
  - [ ] Cluster-to-cluster communication working
  - [ ] DNS resolution within cluster
  - [ ] External egress enabled for package downloads

---

## 🚀 READY TO DEPLOY?

Run this final validation:

```bash
# Source environment
source .env.production

# Run deployment script pre-flight
./scripts/deploy-production.sh phase0_preflight  # (if implemented)

# Or manually verify
kubectl get nodes
kubectl get ns
psql -h $DB_HOST -U $DB_USER -d manta -c "SELECT version();"
redis-cli -h $REDIS_HOST -p $REDIS_PORT info
```

**Final Approval:**

- [ ] **Engineering Lead** — Code review & sign-off
- [ ] **DevOps Lead** — Infrastructure readiness
- [ ] **DBA** — Database backup & migration strategy
- [ ] **SRE** — Monitoring & alerting configured
- [ ] **Project Owner** — Business approval

---

## 📞 EMERGENCY CONTACTS

| Role | Name | Slack | Phone |
|------|------|-------|-------|
| Deployment Lead | [Name] | @name | XXX-XXX-XXXX |
| DevOps Lead | [Name] | @name | XXX-XXX-XXXX |
| DBA | [Name] | @name | XXX-XXX-XXXX |
| SRE | [Name] | @name | XXX-XXX-XXXX |

---

## 🔄 DEPLOYMENT SEQUENCE

```
PHASE 1: Infrastructure Setup (30 min)
├─ Database migrations
├─ Prometheus Adapter installation
├─ Helm chart deployment
└─ FastAPI restart

PHASE 2: Validation & Testing (20 min)
├─ Metrics Server verification
├─ HPA status check
├─ Custom metrics availability
├─ Database index verification
└─ Redis connectivity test

PHASE 3: Monitoring Setup (15 min)
├─ Grafana dashboard import
├─ Alert rules deployment
└─ Slack webhook configuration

PHASE 4: Go-Live - Feature Enablement (10 min)
├─ Fine-tuning feature enabled
├─ Feedback analytics enabled
├─ Cache layer enabled
├─ Smart model selection enabled
└─ FastAPI restart with all features

PHASE 5: Smoke Tests (10 min)
├─ Fine-tuning endpoint test
├─ Feedback analytics endpoint test
├─ Cache stats endpoint test
└─ HPA scaling validation
```

---

## ⏱️ TIMING EXPECTATIONS

| Phase | Duration | Owner | Can Fail-Over |
|-------|----------|-------|---------------|
| Pre-flight checks | 15 min | All | Yes (reschedule) |
| Phase 1 | 30 min | DevOps | No (critical) |
| Phase 2 | 20 min | Platform Eng | Yes (retry) |
| Phase 3 | 15 min | SRE | Yes (manual) |
| Phase 4 | 10 min | Engineering | No (critical) |
| Phase 5 | 10 min | QA | Yes (repeat) |
| **Total** | **2-3 hours** | **All** | **Depends** |

**Recommendation:** Schedule for off-peak hours (e.g., weekend morning or weekday after hours)

---

## 🛑 ABORT CRITERIA

Stop and rollback immediately if:

- ❌ Database migration fails
- ❌ Cannot connect to Kubernetes cluster
- ❌ Node becomes unavailable during deployment
- ❌ Pods fail to start (ImagePullBackOff, CrashLoopBackOff)
- ❌ Service endpoints not responding after Phase 4
- ❌ Error rate > 5% in smoke tests
- ❌ HPA not scaling after 5 minutes

**Rollback Command:**
```bash
./scripts/rollback-production.sh
# Or manually:
kubectl rollout undo deployment/fastapi
```

---

## ✨ SUCCESS CRITERIA

After deployment completes, verify:

| Criterion | Check | Success Metric |
|-----------|-------|-----------------|
| **Pods Running** | `kubectl get pods` | All pods Ready 1/1 |
| **Services Ready** | `kubectl get svc` | All services have EXTERNAL-IP or ClusterIP |
| **API Responding** | `curl $API_URL/health` | HTTP 200 in < 500ms |
| **Database Connected** | `curl $API_URL/db-check` | HTTP 200 |
| **HPA Active** | `kubectl get hpa -w` | Targets showing CPU% |
| **Grafana Dashboards** | `curl $GRAFANA_URL/api/dashboards` | 6+ dashboards listed |
| **Cache Working** | `curl $API_URL/monitoring/cache-stats` | hit_rate data returned |
| **Fine-tuning Ready** | `curl -X POST $API_URL/ml/finetune` | 202 Accepted response |
| **Error Rate** | Monitor for 5 min | < 0.1% errors |

---

## 📝 DEPLOYMENT LOG

Record deployment progress:

```
Start Time: __________
End Time: __________
Deployment Lead: __________

Phase 1 Status: [ ] In Progress  [ ] Complete  [ ] Failed
  Issues: _____________________________

Phase 2 Status: [ ] In Progress  [ ] Complete  [ ] Failed
  Issues: _____________________________

Phase 3 Status: [ ] In Progress  [ ] Complete  [ ] Failed
  Issues: _____________________________

Phase 4 Status: [ ] In Progress  [ ] Complete  [ ] Failed
  Issues: _____________________________

Phase 5 Status: [ ] In Progress  [ ] Complete  [ ] Failed
  Issues: _____________________________

OVERALL STATUS: [ ] SUCCESS  [ ] PARTIAL  [ ] ROLLBACK

Notes: ___________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

Sign-off:
Deployment Lead: ________________________  Date: __________
Engineering Manager: ____________________  Date: __________
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-27  
**Status:** READY FOR USE
