# Fase 4 Operational Runbooks

Comprehensive operational procedures for running Fase 4 - Git Evolution Suite in production.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Scaling & Capacity Management](#scaling--capacity-management)
4. [Backup & Disaster Recovery](#backup--disaster-recovery)
5. [Upgrades & Maintenance](#upgrades--maintenance)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Security Operations](#security-operations)

---

## Daily Operations

### Morning Startup Checklist

**Frequency**: Once per shift start
**Expected Duration**: 5 minutes

```bash
# 1. Verify cluster connectivity
kubectl cluster-info
kubectl get nodes

# 2. Check all pods are running
kubectl get pods -n manta-fase4-prod
# Expected output: All pods in Running state

# 3. Check resource utilization
kubectl top nodes
kubectl top pods -n manta-fase4-prod

# 4. Verify services are accessible
kubectl get svc -n manta-fase4-prod
# Expected: All services have CLUSTER-IP assigned

# 5. Check Prometheus targets
kubectl exec -it prometheus-0 -n manta-fase4-prod -- \
  curl -s localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Expected: 8+ active targets

# 6. Check for alerts
kubectl exec -it alertmanager-0 -n manta-fase4-prod -- \
  curl -s localhost:9093/api/v1/alerts | jq '.data | length'
# Expected: 0 active alerts (if any, investigate)

# 7. Review logs for errors
kubectl logs -n manta-fase4-prod \
  -l app=platform-router \
  --tail=100 | grep -i error
```

**If any checks fail**: See [Incident Response](#incident-response) section.

### Hourly Health Monitoring

**Frequency**: Every hour during business hours
**Expected Duration**: 2 minutes

```bash
# 1. Check error rate (via Prometheus)
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m])' | \
  jq '.data.result[].value[1]'
# Expected: <0.05 (5%)

# 2. Check latency (P95)
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, http_request_duration_seconds)' | \
  jq '.data.result[].value[1]'
# Expected: <5 seconds

# 3. Check ML model confidence
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=avg(ml_model_confidence_score)' | \
  jq '.data.result[].value[1]'
# Expected: >0.90 (90%)

# 4. Check pod restarts
kubectl get pods -n manta-fase4-prod -o wide | grep -v "0/[0-9]"
# Expected: No pod restarts
```

**If metrics are outside expected ranges**: Escalate to on-call engineer.

---

## Incident Response

### Incident Severity Levels

| Severity | SLA | Response | Example |
|----------|-----|----------|---------|
| Critical | 15 min | Immediate investigation & remediation | All pods down, >50% error rate |
| High | 30 min | Urgent investigation | Single pod crashes, >10% error rate |
| Medium | 2 hours | Standard investigation | Degraded latency, <5% error rate |
| Low | Next business day | Scheduled investigation | Informational alerts, documentation needs |

### P1: Complete Service Outage

**Symptom**: All pods down, no service available
**SLA**: 15 minutes

**Step 1: Immediate Triage (0-2 min)**
```bash
# Check cluster status
kubectl get nodes

# Check namespace
kubectl get pods -n manta-fase4-prod

# Check events
kubectl describe namespace manta-fase4-prod
kubectl get events -n manta-fase4-prod --sort-by='.lastTimestamp'
```

**Step 2: Identify Root Cause (2-5 min)**
- Is the cluster accessible? (nodes ready?)
- Are resource quotas exceeded?
- Are persistent volumes available?
- Check pod descriptions for errors

```bash
# Check resource quotas
kubectl describe resourcequota manta-fase4-quota -n manta-fase4-prod

# Check PVC status
kubectl get pvc -n manta-fase4-prod

# Check pod status details
kubectl describe pod <pod-name> -n manta-fase4-prod
```

**Step 3: Remediation (5-15 min)**

*If resource quota exceeded:*
```bash
kubectl edit resourcequota manta-fase4-quota -n manta-fase4-prod
# Increase limits and save
```

*If PVC not bound:*
```bash
kubectl describe pvc <pvc-name> -n manta-fase4-prod
# Check PV availability
kubectl get pv

# If PV missing, create new storage
kubectl apply -f fase4/k8s-production/storage.yaml
```

*If pods failing to start:*
```bash
# Get pod logs
kubectl logs <pod-name> -n manta-fase4-prod --previous

# Check image availability
kubectl describe pod <pod-name> -n manta-fase4-prod

# Restart deployment
kubectl rollout restart deployment/<deployment> -n manta-fase4-prod
```

**Step 4: Verification (1-2 min)**
```bash
# Verify all pods running
kubectl get pods -n manta-fase4-prod

# Verify services accessible
kubectl get svc -n manta-fase4-prod

# Test connectivity
kubectl exec -it <router-pod> -n manta-fase4-prod -- \
  curl http://platform-router:80/health/ready
```

**Step 5: Post-Incident (after stability)**
- Document root cause
- File incident ticket (Jira/GitHub Issues)
- Schedule post-mortem
- Implement preventive measures

---

### P2: High Error Rate (>10%)

**Symptom**: Service returning 5xx errors, error rate spike
**SLA**: 30 minutes

**Step 1: Identify Affected Service**
```bash
# Get error rate by service
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m]) by (job)' | \
  jq '.data.result[]'

# Check specific service
kubectl logs deployment/<service> -n manta-fase4-prod --tail=50
```

**Step 2: Check Service Health**
```bash
# Get service pod status
kubectl get pods -l app=<service> -n manta-fase4-prod

# Check resource usage
kubectl top pod -l app=<service> -n manta-fase4-prod

# Check recent restarts
kubectl describe pod <pod> -n manta-fase4-prod
```

**Step 3: Determine Cause**

*If high CPU/Memory:*
```bash
# Restart pod to clear state
kubectl delete pod <pod-name> -n manta-fase4-prod

# Scale up if needed
kubectl scale deployment/<service> --replicas=5 -n manta-fase4-prod
```

*If application errors in logs:*
```bash
# Check for recent changes
git log --oneline -20

# Rollback to previous version
kubectl set image deployment/<service> \
  <service>=image:previous-tag \
  -n manta-fase4-prod
```

*If dependency issues:*
```bash
# Test connectivity to downstream services
kubectl exec <pod> -- curl http://dependency:port/health/ready

# Check dependency status
kubectl get pods -l app=dependency -n manta-fase4-prod
```

**Step 4: Verify Recovery**
```bash
# Monitor error rate for 5 minutes
watch -n 5 'curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode "query=rate(http_requests_total{status=~\"5..\"}[5m])" | \
  jq ".data.result[0].value[1]"'

# Error rate should drop below 1%
```

---

### P3: High Latency (P95 >5 sec)

**Symptom**: Slow responses, increased response time
**SLA**: 2 hours

**Step 1: Identify Latency Source**
```bash
# Check latency by service
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, http_request_duration_seconds) by (job)' | \
  jq '.data.result[]'

# Check request rate
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=rate(http_requests_total[5m]) by (job)' | \
  jq '.data.result[]'
```

**Step 2: Check Resource Availability**
```bash
# CPU and Memory utilization
kubectl top pods -n manta-fase4-prod

# Disk I/O (if applicable)
kubectl exec <pod> -- iostat -x 1

# Network metrics
kubectl exec <pod> -- netstat -i
```

**Step 3: Remediation**

*If resource constrained:*
```bash
# Scale up deployment
kubectl scale deployment/<service> --replicas=5 -n manta-fase4-prod

# Monitor latency decrease
watch -n 5 'curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode "query=histogram_quantile(0.95, http_request_duration_seconds)" | \
  jq ".data.result[0].value[1]"'
```

*If external dependency slow:*
```bash
# Increase timeout values
kubectl set env deployment/<service> \
  REQUEST_TIMEOUT_MS=60000 \
  -n manta-fase4-prod

# Check dependency health
curl <dependency-service>/health/ready
```

---

## Scaling & Capacity Management

### Horizontal Scaling (More Pods)

**When**: Error rate increasing, latency degrading
**Duration**: 2-3 minutes

```bash
# Check current replicas
kubectl get deployment -n manta-fase4-prod

# Scale up service
kubectl scale deployment/platform-router --replicas=5 -n manta-fase4-prod

# Monitor scaling progress
kubectl get deployment platform-router -n manta-fase4-prod -w

# Verify new pods healthy
kubectl get pods -l app=platform-router -n manta-fase4-prod
```

**Auto-Scaling is enabled**, so HPA will automatically scale based on CPU/memory.

### Vertical Scaling (More Resources)

**When**: Single pod reaching resource limits
**Duration**: 15-30 minutes (requires pod restart)

```bash
# Check current resource requests/limits
kubectl get pod <pod-name> -n manta-fase4-prod -o json | \
  jq '.spec.containers[].resources'

# Edit deployment to increase resources
kubectl edit deployment/platform-router -n manta-fase4-prod

# Change resources.requests.cpu and resources.requests.memory

# Deployment automatically rolls out with new resource limits
kubectl rollout status deployment/platform-router -n manta-fase4-prod
```

### Storage Capacity

**When**: PVC approaching 80% full
**Duration**: Variable

```bash
# Check PVC usage
kubectl exec prometheus-0 -n manta-fase4-prod -- df -h /prometheus

# If Prometheus storage full:
# 1. Reduce retention time
kubectl set env statefulset/prometheus \
  TSDB_RETENTION=7d \
  -n manta-fase4-prod

# 2. Or expand PVC
kubectl patch pvc prometheus-storage-prometheus-0 \
  -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}' \
  -n manta-fase4-prod
```

---

## Backup & Disaster Recovery

### Daily Backup Procedure

**Frequency**: Daily at 03:00 UTC
**Duration**: 5-10 minutes

```bash
#!/bin/bash
# Backup Prometheus data
kubectl exec -it prometheus-0 -n manta-fase4-prod -- \
  tar czf /prometheus/prometheus-backup-$(date +%Y%m%d).tar.gz \
  --exclude=wal /prometheus/

# Backup ConfigMaps
kubectl get configmap -n manta-fase4-prod -o yaml > \
  /backups/fase4-configmaps-$(date +%Y%m%d).yaml

# Backup Secrets (encrypted)
kubectl get secret -n manta-fase4-prod -o yaml | \
  gpg --encrypt --recipient YOUR_GPG_KEY > \
  /backups/fase4-secrets-$(date +%Y%m%d).yaml.gpg

# Upload to S3
aws s3 sync /backups/ s3://manta-backups/fase4/
```

### Restore from Backup

**Use Case**: Data corruption, accidental deletion
**Duration**: 15-30 minutes

```bash
# Restore Prometheus data
kubectl exec -it prometheus-0 -n manta-fase4-prod -- \
  tar xzf /prometheus/prometheus-backup-20260727.tar.gz \
  -C /prometheus/

# Restart Prometheus
kubectl delete pod prometheus-0 -n manta-fase4-prod

# Restore ConfigMaps
kubectl delete configmap --all -n manta-fase4-prod
kubectl apply -f fase4-configmaps-20260727.yaml

# Restore Secrets
gpg --decrypt fase4-secrets-20260727.yaml.gpg | kubectl apply -f -

# Verify restoration
kubectl get configmap -n manta-fase4-prod
kubectl get secret -n manta-fase4-prod
```

---

## Upgrades & Maintenance

### Rolling Update Procedure

**When**: New version deployment
**Downtime**: 0 (rolling update)
**Duration**: 5-15 minutes

```bash
# 1. Pull new image
docker pull manta-fase4/platform-router:1.1.0

# 2. Update deployment image
kubectl set image deployment/platform-router \
  platform-router=manta-fase4/platform-router:1.1.0 \
  -n manta-fase4-prod

# 3. Monitor rollout
kubectl rollout status deployment/platform-router \
  -n manta-fase4-prod -w

# 4. Verify health
kubectl get pods -l app=platform-router -n manta-fase4-prod

# 5. Check logs for errors
kubectl logs -f deployment/platform-router -n manta-fase4-prod
```

### Rollback Procedure

**When**: Update causes issues
**Duration**: 2-3 minutes

```bash
# View rollout history
kubectl rollout history deployment/platform-router -n manta-fase4-prod

# Rollback to previous version
kubectl rollout undo deployment/platform-router \
  -n manta-fase4-prod

# Monitor rollback
kubectl rollout status deployment/platform-router \
  -n manta-fase4-prod -w

# Verify health
kubectl get pods -l app=platform-router -n manta-fase4-prod
```

### Cluster Maintenance

**Frequency**: Monthly
**Duration**: 30-60 minutes
**Maintenance Window**: Off-business hours

```bash
# 1. Drain node (migrate pods)
kubectl drain <node-name> --ignore-daemonsets

# 2. Perform maintenance (OS updates, etc.)
ssh <node-name>
sudo apt-get update && sudo apt-get upgrade -y
sudo reboot

# 3. Wait for node to come back online
kubectl get nodes

# 4. Uncordon node (allow pod scheduling)
kubectl uncordon <node-name>

# 5. Verify pods rescheduled
kubectl get pods -n manta-fase4-prod
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

**Every 5 minutes:**
```bash
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Latency (P95)
histogram_quantile(0.95, http_request_duration_seconds)

# ML model confidence
avg(ml_model_confidence_score)
```

**Every 30 minutes:**
```bash
# Resource utilization (CPU, Memory)
container_cpu_usage_seconds_total
container_memory_usage_bytes

# Pod restart count
kube_pod_container_status_restarts_total

# PVC usage
kubelet_volume_stats_used_bytes
```

### Alert Response Guide

**Alert**: HighErrorRate (error rate >5%)
```
1. Check service logs: kubectl logs deployment/<service>
2. Check resource availability: kubectl top pods
3. Check dependencies: curl <dependency>/health/ready
4. Escalate if not resolved in 10 minutes
```

**Alert**: HighLatency (P95 >5 sec)
```
1. Check request rate: rate(http_requests_total[5m])
2. Check resource usage: kubectl top pods
3. Scale up if needed: kubectl scale deployment
4. Monitor for 5 minutes to verify resolution
```

**Alert**: MLModelDrift (drift score >0.3)
```
1. Review recent code changes
2. Check feature distribution changes
3. Run model retraining: kubectl exec ml-inference -- train_model.py
4. Deploy updated model: kubectl set image
```

**Alert**: PodCrashLooping
```
1. Get pod logs: kubectl logs <pod> --previous
2. Check resource limits: kubectl describe pod <pod>
3. Check startup probes: kubectl get events
4. If image issue, rollback: kubectl rollout undo deployment
```

---

## Security Operations

### RBAC Auditing

**Frequency**: Weekly
**Duration**: 5 minutes

```bash
# List all role bindings
kubectl get rolebinding -n manta-fase4-prod

# Audit service account permissions
kubectl auth can-i --list --as=system:serviceaccount:manta-fase4-prod:manta-fase4-sa -n manta-fase4-prod

# Check who can perform sensitive actions
kubectl auth can-i delete pod -n manta-fase4-prod --as=system:serviceaccount:manta-fase4-prod:manta-fase4-sa
```

### Secret Rotation

**Frequency**: Every 90 days
**Duration**: 15-30 minutes

```bash
# 1. Generate new secrets (outside cluster)
# Use LastPass/Vault/AWS Secrets Manager

# 2. Update Kubernetes secrets
kubectl delete secret github-credentials -n manta-fase4-prod
kubectl create secret generic github-credentials \
  --from-literal=github-token=<NEW_TOKEN> \
  -n manta-fase4-prod

# 3. Restart pods to pick up new secrets
kubectl rollout restart deployment/platform-router -n manta-fase4-prod

# 4. Verify pods running with new secrets
kubectl get pods -l app=platform-router -n manta-fase4-prod
```

### Network Policy Validation

**Frequency**: Monthly
**Duration**: 10 minutes

```bash
# Test allowed traffic
kubectl exec -it <router-pod> -n manta-fase4-prod -- \
  curl http://code-refactor-engine:8081/health/ready
# Expected: Success (200 OK)

# Test blocked traffic (should fail)
kubectl exec -it <router-pod> -n manta-fase4-prod -- \
  curl http://pod-in-different-namespace:8080
# Expected: Timeout or connection refused

# Review network policies
kubectl get networkpolicy -n manta-fase4-prod
kubectl describe networkpolicy platform-router-netpol -n manta-fase4-prod
```

### Container Image Scanning

**Frequency**: Before each deployment
**Duration**: 5-10 minutes

```bash
# Scan for vulnerabilities
trivy image manta-fase4/platform-router:1.0.0

# Check for critical vulnerabilities (CVSS >7.0)
trivy image --severity HIGH,CRITICAL manta-fase4/platform-router:1.0.0

# If vulnerabilities found:
# 1. Update dependencies
# 2. Rebuild image
# 3. Re-scan to verify
```

---

## Escalation Procedures

### When to Escalate

| Condition | Action |
|-----------|--------|
| Issue not resolved in 15 min (P1) | Page on-call engineer |
| Issue not resolved in 30 min (P2) | Alert engineering lead |
| Issue not resolved in 2 hours (P3) | Alert engineering director |
| Security issue detected | Alert security team immediately |
| Data loss/corruption | Alert CISO immediately |

### Contact Information

- **On-Call Engineer**: PagerDuty (rotation weekly)
- **Engineering Lead**: platform-lead@manta.local
- **Security Team**: security@manta.local
- **CISO**: ciso@manta.local

---

## Quick Reference

### Common Commands

```bash
# Pod management
kubectl get pods -n manta-fase4-prod
kubectl logs pod/<name> -n manta-fase4-prod
kubectl describe pod/<name> -n manta-fase4-prod
kubectl delete pod/<name> -n manta-fase4-prod
kubectl exec -it pod/<name> -n manta-fase4-prod -- /bin/bash

# Deployment management
kubectl get deployments -n manta-fase4-prod
kubectl scale deployment/<name> --replicas=5 -n manta-fase4-prod
kubectl rollout status deployment/<name> -n manta-fase4-prod
kubectl rollout undo deployment/<name> -n manta-fase4-prod

# Resource inspection
kubectl top nodes
kubectl top pods -n manta-fase4-prod
kubectl describe resourcequota manta-fase4-quota -n manta-fase4-prod
kubectl get events -n manta-fase4-prod --sort-by='.lastTimestamp'

# Monitoring access
kubectl port-forward svc/prometheus 9090:9090 -n manta-fase4-prod
kubectl port-forward svc/grafana 3000:3000 -n manta-fase4-prod
kubectl port-forward svc/jaeger-query 16686:16686 -n manta-fase4-prod
```

---

## Appendix: Runbook Updates

**Last Updated**: 2026-07-27
**Next Review**: 2026-08-27
**Owner**: Platform Engineering Team

To update this runbook: Submit PR with changes, get approval from engineering lead, merge to main.
