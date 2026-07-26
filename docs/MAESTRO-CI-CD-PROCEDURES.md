# Maestro CI/CD Procedures & Operations Manual

**Version:** 6.0.1  
**Last Updated:** 2026-07-26  
**Maintainer:** DevOps Team (devops@mantaassociados.com)

---

## Quick Links

- **CI Pipeline:** `.github/workflows/maestro-ci.yml`
- **Deployment Pipeline:** `.github/workflows/maestro-deploy.yml`  
- **Nightly Health Check:** `.github/workflows/maestro-nightly.yml`
- **Monitoring Setup:** `docs/MAESTRO-MONITORING-SETUP.md`
- **Troubleshooting:** `docs/MAESTRO-TROUBLESHOOTING-PROCEDURES.md`

---

## Overview

The Maestro v6.0 CI/CD system comprises three primary workflows:

- **maestro-ci.yml**: Continuous integration on push/PR (30-60 min)
- **maestro-deploy.yml**: Release deployment with blue-green strategy (45-90 min)
- **maestro-nightly.yml**: Automated health checks (6 AM UTC daily)

### Key Principles

1. **No direct production pushes** - all changes via release tags (v6.0.*)
2. **Blue-green deployments** - zero-downtime strategy with rollback capability
3. **Staged validation** - staging verification before production approval gate
4. **Comprehensive testing** - smoke, unit, integration, security, type, and performance checks
5. **Audit trail** - all deployments logged with actor, timestamp, and image tag

---

## CI Pipeline (`maestro-ci.yml`)

### Triggers

- Push to `main` or `develop` branch
- Pull requests to `main` or `develop`
- Manual dispatch via GitHub Actions UI

### Jobs (Execution Order)

1. **Parallel (t=0-15 min):**
   - code-quality (flake8, pylint, isort, black)
   - type-checking (mypy)
   - security-scanning (bandit, safety)

2. **Sequential (t=15-30 min):**
   - unit-tests (pytest, coverage)
   - needs: code-quality, type-checking

3. **Sequential (t=30-45 min):**
   - integration-tests (PostgreSQL, Redis)
   - needs: code-quality, type-checking, unit-tests

4. **Parallel (t=45-60 min):**
   - documentation-validation (markdown links, markup)
   - smoke-tests
   - needs: unit-tests, integration-tests

5. **Sequential (t=60-75 min):**
   - docker-build (only on main branch)
   - trivy security scan
   - needs: all quality jobs

6. **Final (t=75-90 min):**
   - results (summary check)

---

## Deployment Pipeline (`maestro-deploy.yml`)

### Triggers

- Tag push matching `v6.0.*` (automatic to staging)
- Manual dispatch with environment selection

### Flow

```
v6.0.X tag pushed OR manual dispatch
    ↓
[pre-deployment-checks] → Validate checklist, verify configs
    ↓
[build-and-push-image] → Docker build + push to registry
    ↓
[deploy-to-staging] → Kubernetes rollout to staging
    ↓
[smoke-tests-staging] → Health checks, routing verification
    ↓
[approval-gate] → Manual approval (24 hour timeout)
    ↓
[deploy-to-production] → Blue-green rollout
    ↓
[post-deployment-validation] → Production smoke tests
    ↓
[rollback-safety-check] → Verify rollback capability
    ↓
[deployment-notification] → Slack notification
```

---

## Manual Deployment

### To Staging Only

```bash
gh workflow run maestro-deploy.yml \
  -f deployment_environment=staging \
  -f image_tag=v6.0.1
```

### To Production

Release tag automatically triggers full pipeline:

```bash
git tag v6.0.1 main
git push origin v6.0.1

# Then approve the deployment in GitHub Actions UI
```

---

## Monitoring Deployments

```bash
# List recent workflow runs
gh run list --repo manta-associados/maestro-os --workflow maestro-deploy.yml --limit 10

# View specific deployment
gh run view <RUN_ID> --log

# Download logs
gh run download <RUN_ID> --dir ./deployment-logs
```

---

## Emergency Rollback

If production deployment fails:

```bash
# Option 1: Via CI/CD (Recommended)
gh workflow run maestro-deploy.yml \
  -f deployment_environment=production \
  -f image_tag=v6.0.0  # Previous stable version

# Option 2: Manual Kubernetes (If CI/CD unavailable)
kubectl patch service maestro \
  -n maestro-prod \
  -p '{"spec":{"selector":{"deployment":"maestro-green"}}}'
```

---

## Common Issues & Solutions

### CI Failure: Code Quality

```bash
# Run locally to debug
flake8 maestro/ --show-source
mypy maestro/
black maestro/ --check
isort maestro/ --check-only
```

### CI Failure: Test Coverage

```bash
# Run tests locally
pytest tests/unit/ -v --cov=maestro
pytest tests/integration/ -v

# Check coverage report
coverage report
```

### Deployment: Kubernetes Timeout

```bash
# Check pod events
kubectl describe pod -n maestro-prod -l deployment=maestro-blue | tail -20

# Check resource availability
kubectl top nodes
kubectl top pods -n maestro-prod

# Scale up if needed
kubectl scale deployment maestro-blue -n maestro-prod --replicas=5
```

---

## Support & Escalation

- **DevOps Team:** devops@mantaassociados.com
- **On-Call:** PagerDuty (maestro-v6-oncall escalation policy)
- **Status Page:** https://status.maestro.manta-associados.com
- **Slack:** #maestro-devops

---

**Document Version:** 6.0.1  
**Last Reviewed:** 2026-07-26  
**Next Review:** 2026-08-26
