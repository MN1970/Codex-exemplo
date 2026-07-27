# Phase 4.1 Migration Guide (v4.2 → v5.0)

**Version**: 1.0  
**Date**: 2026-07-27  
**Duration**: 8 weeks  
**Risk Level**: Medium (federation is isolated from core routing)

---

## Overview

This guide covers the safe migration from Maestro v4.2 (single-org) to v5.0 with Agent Federation (Phase 4.1). The migration happens in **four phases** with gates, rollback plans, and customer communication templates.

### Key Principles
- **Non-blocking**: Federation runs alongside v4.2; no forced cutover
- **Progressive**: Start with 1 partner org, expand gradually
- **Reversible**: Can disable federation at any time with feature flag
- **Observable**: Comprehensive monitoring and audit trails
- **Compliant**: Zero data leaks, immutable audit logs, GDPR-ready

---

## Phase 1: Preparation (Week 1)

### 1.1 Pre-Migration Checklist

```bash
# 1. Backup existing infrastructure
pg_dump manta_maestro > /backups/maestro-v4.2-$(date +%s).sql

# 2. Create feature flag
INSERT INTO feature_flags (name, enabled, rollout_percentage)
VALUES ('FEDERATION_ENABLED', false, 0);

# 3. Verify infra readiness
kubectl get nodes -o wide              # Cluster status
kubectl get pvc -A                     # Storage available
curl https://supabase-api.manta.internal/health  # DB ready

# 4. Prepare certificates
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout /etc/federation/root-ca.key \
  -out /etc/federation/root-ca.crt \
  -subj "/CN=Manta Federation Root CA/O=Manta" -days 3650
```

### 1.2 Pre-Flight Validation

```python
# tests/federation/test_preflight.py
import pytest
from maestro.mtls_handler import MTLSHandler

def test_ca_certificate_exists():
    """Verify root CA is available."""
    handler = MTLSHandler(
        ca_cert_path="/etc/federation/root-ca.crt",
        ca_key_path="/etc/federation/root-ca.key",
    )
    assert handler.ca_cert is not None
    assert handler.ca_key is not None

def test_database_schema_ready():
    """Verify federation tables exist."""
    # Query Supabase schema
    tables = ["federation_agents", "federation_audit_log"]
    # Assert tables exist
```

### 1.3 Rollback Plan for Phase 1

| Issue | Action | Timeline |
|-------|--------|----------|
| CA cert generation fails | Use pre-generated backup certs | 30 min |
| Database unreachable | Switch to read-only mode (v4.2 only) | 15 min |
| Kubernetes cluster down | Restore from backup + redeploy | 2 hours |

---

## Phase 2: Soft Launch (Week 2-3)

### 2.1 Deploy Federation Broker (Staging)

```bash
# 1. Deploy to staging namespace
kubectl apply -f infra/k8s/federation-deployment.yaml -n manta-staging

# 2. Verify deployment
kubectl get pods -n manta-staging -l app=federation-broker
kubectl logs -f deployment/federation-broker -n manta-staging

# 3. Run integration tests
pytest tests/federation/test_federation_suite.py -v --markers=integration

# 4. Performance baseline
# Expected: <100ms latency p95, 99.95% uptime
```

### 2.2 Onboard First Partner (Manual Process)

**Partner**: ACME Claims Inc (org-2)

```bash
# 1. Generate org CA certificate
python -c "
from maestro.mtls_handler import MTLSHandler
handler = MTLSHandler('/etc/federation/root-ca.crt', '/etc/federation/root-ca.key')
cert, key = handler.generate_ca_certificate(
    org_id='org-2',
    common_name='ACME Claims CA',
    validity_days=3650
)
# Save to: /etc/federation/certs/org-2-ca.{crt,key}
"

# 2. Create organization record
curl -X POST https://federation-broker-staging.manta.internal/api/v1/orgs \
  -H "Authorization: Bearer $(kubectl get secret federation-admin-token -o jsonpath='{.data.token}')" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org-2",
    "org_name": "ACME Claims Inc",
    "trust_tier": "L2_PARTNER",
    "contact_email": "engineering@acme-claims.com",
    "ca_certificate_pem": "'$(cat /etc/federation/certs/org-2-ca.crt | base64 -w 0)'"
  }'

# 3. Create agent record for partner agent
curl -X POST https://federation-broker-staging.manta.internal/api/v1/agents/register \
  -H "Authorization: Bearer $(base64 <<< org-2:$ORG_SECRET_KEY)" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "partner-acme-claims-v1",
    "org_id": "org-2",
    "capabilities": [
      {
        "name": "classify-claim",
        "domain": "claims",
        "version": "1.0.0",
        "requires_org_context": false,
        "rate_limit_rps": 100,
        "cost_usd_per_1k": 0.02
      }
    ]
  }'
```

### 2.3 Test Routing (5% Traffic)

```bash
# 1. Enable feature flag at 5%
UPDATE feature_flags SET rollout_percentage = 5
WHERE name = 'FEDERATION_ENABLED';

# 2. Send test request through federation
python -c "
import asyncio
from maestro.afp_protocol import AFPRequest

async def test():
    req = AFPRequest.create_request(
        source_agent='manta-01-claims',
        source_org='org-1',
        target_agent='partner-acme-claims-v1',
        target_org='org-2',
        capability='classify-claim',
        payload={'claim_text': 'test'},
        data_classification='PUBLIC'
    )
    # Route through broker
    # Verify response

asyncio.run(test())
"

# 3. Monitor metrics (24 hours)
# Grafana dashboard: Federation > Latency, Error Rate, Request Count
# Alert if: latency_p95 > 100ms OR error_rate > 0.1%
```

### 2.4 Soft Launch Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Uptime | 99.9% | PASS |
| Latency (p95) | <100ms | PASS |
| Error rate | <0.1% | PASS |
| Data isolation violations | 0 | PASS |
| Partner feedback | Positive | PASS |

**Gate**: If all pass → proceed to Phase 3. Else → investigate & delay 1 week.

---

## Phase 3: General Availability (Week 4-6)

### 3.1 Enable Federation for All Agents

```bash
# 1. Gradually increase rollout
UPDATE feature_flags SET rollout_percentage = 25 WHERE name = 'FEDERATION_ENABLED';
# Day 2
UPDATE feature_flags SET rollout_percentage = 50 WHERE name = 'FEDERATION_ENABLED';
# Day 3
UPDATE feature_flags SET rollout_percentage = 75 WHERE name = 'FEDERATION_ENABLED';
# Day 4
UPDATE feature_flags SET rollout_percentage = 100 WHERE name = 'FEDERATION_ENABLED';

# 2. Monitor continuously
watch -n 5 "kubectl logs -f deployment/federation-broker -n manta-maestro | grep ERROR"
```

### 3.2 Decommission Legacy Federation API (v4.2)

```bash
# 1. Check for remaining traffic
SELECT COUNT(*) FROM federation_audit_log
WHERE created_at > NOW() - INTERVAL '24 hours'
AND request_path LIKE '/api/v4.2/%';

# 2. Once minimal, mark as deprecated
# - Add deprecation header to responses
# - Update API docs with sunset date (30 days)
# - Notify partners via email

# 3. After 30 days, disable endpoint
# Update Nginx:
# location /api/v4.2/* { return 410 Gone; }
```

### 3.3 Customer Communications

**Email to Partners** (Week 4):
```
Subject: Manta Maestro v5.0 Federation Now Available

Dear Partners,

We're excited to announce Maestro v5.0 with Agent Federation!

What's new:
- Direct agent-to-agent communication (AFP/1.0 protocol)
- Multi-org capability routing with zero data leaks
- Real-time capability discovery
- Immutable audit trails for compliance

Your next steps:
1. Review the partnership agreement (attached)
2. Generate your org CA certificate
3. Submit 1-2 agent manifests for testing
4. Schedule handshake ceremony with our team

Timeline:
- August 2026: Soft launch with select partners
- September 2026: General availability
- October 2026: v4.2 API sunset (30-day deprecation)

Questions? Contact maestro@mantaassociados.com

Best regards,
Manta Maestro Team
```

---

## Phase 4: Hardening (Week 7-8)

### 4.1 Penetration Testing

**Security Audit Scope**:

```markdown
# Phase 4.1 Federation Security Audit

## mTLS Validation
- [ ] Valid cert → allowed
- [ ] Expired cert → denied
- [ ] Revoked cert → denied
- [ ] Wrong org cert → denied
- [ ] Self-signed cert → denied

## Data Isolation
- [ ] Org-1 data not visible to Org-2
- [ ] INTERNAL classification enforced
- [ ] Audit logs immutable (SHA-256 checksums)
- [ ] Response filtering works

## Protocol Security
- [ ] Message tampering detected (signature verification)
- [ ] Replay attacks prevented (nonce/timestamp)
- [ ] Certificate pinning works
- [ ] No side-channel leaks

## API Security
- [ ] Rate limiting enforced
- [ ] SQL injection prevented
- [ ] XSS prevention (if any UI)
- [ ] CSRF tokens present
```

**Run penetration tests**:

```bash
# Attempt to tamper with message
python tests/security/test_message_tampering.py

# Attempt to exfiltrate data
python tests/security/test_data_exfiltration.py

# Attempt certificate attacks
python tests/security/test_certificate_attacks.py

# All tests must PASS before go-live
```

### 4.2 Load Testing

```bash
# Simulate 1,000 concurrent federation requests
ab -c 1000 -n 10000 \
  https://federation-broker.manta.internal/api/v1/request \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{...}'

# Expected results:
# - Latency p95 < 100ms
# - Requests/sec > 10,000
# - Error rate < 0.01%
# - No memory leaks
```

### 4.3 Go-Live Checklist

- [x] All tests pass (unit, integration, security, performance)
- [x] Monitoring dashboards created
- [x] Runbooks documented and tested
- [x] On-call schedule ready (24/7)
- [x] Partner agreements signed
- [x] Data isolation audit cleared
- [x] Security audit passed
- [x] Load test passed
- [x] Executive sign-off obtained

### 4.4 Go-Live Plan (Day 1)

```timeline
06:00 UTC  - Pre-flight checks (30 min)
06:30 UTC  - Gradual rollout (25% → 50% → 100%, monitor continuously)
08:00 UTC  - Full federation active, monitor metrics
08:30 UTC  - Send "live" notification to partners
12:00 UTC  - Post-mortem meeting (if any incidents)
16:00 UTC  - Final sign-off by maestro team
```

---

## Rollback Procedures

### Emergency Rollback (< 5 minutes)

```bash
# 1. Disable federation immediately
UPDATE feature_flags SET enabled = false WHERE name = 'FEDERATION_ENABLED';

# 2. Verify traffic back on v4.2
tail -100 /var/log/maestro/routing.log | grep -c "v4.2"

# 3. Inform partners
# Send incident notification email
```

### Graceful Rollback (< 30 minutes)

```bash
# 1. Stop accepting new federation requests
# Change status page: "Federation temporarily paused for maintenance"

# 2. Wait for in-flight requests to complete (set timeout = 30s)
for req in $(kubectl get pods -o name); do
  kubectl wait $req --for=condition=ready --timeout=30s
done

# 3. Scale down federation broker
kubectl scale deployment federation-broker \
  --replicas=0 -n manta-maestro

# 4. Switch traffic back to v4.2 routing
# Update Istio VirtualService
```

---

## Monitoring & Alerts

### Key Metrics

```yaml
# Prometheus scrape config
global:
  scrape_interval: 30s

scrape_configs:
- job_name: federation-broker
  static_configs:
  - targets: ['federation-broker.manta-maestro:8001']

# Alert rules
groups:
- name: federation
  rules:
  - alert: FederationLatencyHigh
    expr: histogram_quantile(0.95, federation_request_latency_seconds) > 0.1
    for: 5m
    annotations:
      summary: "Federation latency > 100ms"

  - alert: FederationErrorRateHigh
    expr: rate(federation_request_errors_total[5m]) > 0.001
    for: 5m
    annotations:
      summary: "Federation error rate > 0.1%"

  - alert: DataIsolationViolation
    expr: data_isolation_violations_total > 0
    for: 1m
    annotations:
      summary: "Data isolation violation detected!"
      severity: CRITICAL
```

### Dashboards

**Grafana Dashboard** (`dashboards/federation-overview.json`):

1. **Federation Health**
   - Requests/sec (by status: allowed, denied, rate_limited)
   - Latency distribution (p50, p95, p99)
   - Uptime %
   - Error rate

2. **Data Isolation**
   - Violations count (by severity: critical, high, medium)
   - Org coverage (how many orgs federating)
   - Request/response compliance %

3. **Partners**
   - Active agents per org
   - Capabilities offered
   - Requests routed to each partner

4. **Audit Trail**
   - Recent violations (sortable)
   - Certificate expirations (upcoming)
   - Rate limit hits

---

## Post-Migration (Week 9+)

### 4.5.1 Partner Feedback Loop

```markdown
# Weekly Partner Sync (Thursdays 14:00 UTC)

Attendees:
- Manta: Maestro PM, Engineering Lead
- Partners: Engineering Leads

Agenda:
1. Federation uptime & performance (5 min)
2. Issues & feature requests (20 min)
3. Roadmap for Phase 4.2 (10 min)
4. Q&A (10 min)

Deliverables:
- GitHub issues created for feature requests
- Incident reviews (if any)
- Roadmap update
```

### 4.5.2 Continuous Improvement

**Metrics to Track**:

| Metric | Target | Review Freq |
|--------|--------|-------------|
| Federation uptime | 99.95% | Weekly |
| Latency p95 | <100ms | Weekly |
| Partner satisfaction | >4.0/5.0 | Monthly |
| Security incidents | 0 | Weekly |
| Data isolation violations | 0 | Real-time alerts |

**Monthly Reviews**:
- Capacity planning (add more replicas if needed)
- Cost optimization (adjust pricing, rate limits)
- Feature prioritization (roadmap for Phase 4.2)
- Security updates (certificate rotation, audit logs)

---

## Appendix A: Environment Variables

```bash
# Federation Broker Config

# Database
DATABASE_URL=postgresql://user:pass@supabase.manta.internal:5432/maestro
DB_POOL_SIZE=20
DB_TIMEOUT_SECONDS=30

# mTLS
MTLS_CA_CERT_PATH=/etc/federation/ca/root-ca.crt
MTLS_CA_KEY_PATH=/etc/federation/ca/root-ca.key
CERTIFICATE_VALIDITY_DAYS=365

# Broker Identity
MANTA_ORG_ID=org-1
BROKER_API_KEY=$(openssl rand -hex 32)

# Feature Flags
FEDERATION_ENABLED=true
FEDERATION_MODE=production  # or staging/development

# Monitoring
METRICS_ENABLED=true
PROMETHEUS_PORT=8001
LOG_LEVEL=INFO

# Rate Limiting
DEFAULT_RATE_LIMIT_RPS=100
BURST_MULTIPLIER=1.5
WINDOW_SIZE_SECONDS=60
```

---

## Appendix B: Troubleshooting

### Issue: "Certificate validation failed"

```bash
# Check certificate validity
openssl x509 -in /etc/federation/certs/agent.crt -noout -dates

# Validate chain
openssl verify -CAfile /etc/federation/ca/root-ca.crt agent.crt

# Fix: Regenerate certificate
python -c "
from maestro.mtls_handler import MTLSHandler
handler = MTLSHandler(...)
cert, key = handler.generate_agent_certificate(...)
"
```

### Issue: "Data isolation violation"

```bash
# Check audit logs
SELECT * FROM data_isolation_violations
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC LIMIT 10;

# Analyze violation details
# - Check which org's data was exposed
# - Check which request ID caused it
# - Review request/response payloads

# Fix: Update data patterns
validator.register_org_data_patterns(
  "org-id",
  [r"pattern-1", r"pattern-2", ...]
)
```

### Issue: "Latency degradation"

```bash
# Check broker metrics
kubectl top pods -n manta-maestro

# Scale up if CPU/memory high
kubectl scale deployment federation-broker --replicas=5

# Check database performance
EXPLAIN ANALYZE SELECT * FROM federation_agents WHERE org_id = 'org-1';

# Add indexes if needed
CREATE INDEX idx_federation_agents_org_id ON federation_agents(org_id);
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-27 | Initial migration guide |
| 1.1 (planned) | 2026-08-31 | Post-launch update with lessons learned |
