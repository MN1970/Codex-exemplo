# Fase 4 Staging Kubernetes Environment

## Overview

Staging environment for Fase 4 - Git Evolution Suite. Provides a production-like setup for integration testing, performance validation, and pre-production verification before production deployment.

## Differences from Production

| Aspect | Production | Staging |
|--------|-----------|---------|
| Namespace | `manta-fase4-prod` | `manta-fase4-staging` |
| Router Replicas | 3 | 2 |
| Refactor Replicas | 2 | 1 |
| ML Inference Replicas | 3 | 2 |
| CPU Requests | 32 | 16 |
| Memory Requests | 64Gi | 32Gi |
| CPU Limits | 64 | 32 |
| Memory Limits | 128Gi | 64Gi |
| Pod Limit | 100 | 50 |
| Image Tags | `1.0.0` | `1.0.0-staging` |
| Log Level | info | debug |
| Data Retention | 30 days | 7 days |
| HPA Min/Max | 3/10 | 2/5 |

## Deployment

### Prerequisites
Same as production, but with lower resource requirements:
- 8+ CPU cores (vs 16+ for production)
- 16+ GB RAM (vs 32+ for production)
- 150+ GB disk space (vs 300+ for production)

### Deploy Staging
```bash
# Using Kustomize overlay
kubectl apply -k fase4/k8s-staging/

# Or manually
kubectl apply -f fase4/k8s-production/namespace.yaml -n manta-fase4-staging
kubectl apply -f fase4/k8s-production/storage.yaml
kubectl apply -f fase4/k8s-production/pillar-a-router.yaml -n manta-fase4-staging
kubectl apply -f fase4/k8s-production/pillar-b-refactor.yaml -n manta-fase4-staging
kubectl apply -f fase4/k8s-production/pillar-c-observability.yaml -n manta-fase4-staging
kubectl apply -f fase4/k8s-production/pillar-d-ml-model.yaml -n manta-fase4-staging
```

### Validate Staging
```bash
bash fase4/k8s-production/validate-deployment.sh
# Edit script to use NAMESPACE="manta-fase4-staging"
```

## Testing Scenarios

### 1. Integration Testing
Test all 4 pillars working together:
```bash
# Test Platform Router → Code Refactor Engine
kubectl exec -it <router-pod> -n manta-fase4-staging -- \
  curl http://code-refactor-engine:8081/health/ready

# Test Router → ML Inference
kubectl exec -it <router-pod> -n manta-fase4-staging -- \
  curl http://ml-inference:8082/health/ready
```

### 2. Load Testing
Simulate production traffic with reduced scale:
```bash
# Use k6 or Apache JMeter
k6 run --vus 50 --duration 5m loadtest.js
```

### 3. Canary Testing
Validate canary deployment strategy:
- Deploy new Router version to 1 replica first
- Monitor metrics and error rates
- Gradually roll out to remaining replicas

### 4. Chaos Engineering
Test resilience without impacting production:
```bash
# Test pod failure recovery
kubectl delete pod <router-pod> -n manta-fase4-staging

# Test network disruption
kubectl set env deployment/platform-router \
  SIMULATE_NETWORK_LATENCY=5000 \
  -n manta-fase4-staging
```

### 5. Security Testing
Validate RBAC and network policies:
```bash
# Attempt unauthorized API access (should fail)
kubectl exec -it <pod> -n manta-fase4-staging -- \
  curl -H "Authorization: Bearer invalid-token" http://api/secret

# Test network isolation (should fail)
kubectl exec -it <pod> -n manta-fase4-staging -- \
  curl http://pod-in-different-namespace:8080
```

## Performance Testing

### Baseline Metrics (Expected)
- P50 Latency: <200ms
- P95 Latency: <500ms
- P99 Latency: <2s
- Error Rate: <0.1%
- Throughput: 100+ req/sec per replica

### Load Test Procedure
1. Start staging deployment
2. Wait for all pods ready (5-10 min)
3. Run load test (50-100 concurrent users, 5-10 min)
4. Collect metrics from Prometheus
5. Compare with baselines
6. Archive results for reference

### Monitoring During Tests
```bash
# Watch Prometheus metrics
kubectl port-forward svc/prometheus 9090:9090 -n manta-fase4-staging
# Access http://localhost:9090
# Query: rate(http_requests_total[5m])
#        histogram_quantile(0.95, http_request_duration_seconds)
```

## Troubleshooting

### Pod Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n manta-fase4-staging

# Check logs
kubectl logs <pod-name> -n manta-fase4-staging --previous

# Check resource limits
kubectl top pod <pod-name> -n manta-fase4-staging
```

### High Memory Usage
```bash
# Scale down replicas
kubectl scale deployment/platform-router --replicas=1 -n manta-fase4-staging

# Increase resource limits in kustomization.yaml
```

### Network Connectivity Issues
```bash
# Test DNS resolution
kubectl exec -it <pod> -n manta-fase4-staging -- nslookup code-refactor-engine

# Test TCP connectivity
kubectl exec -it <pod> -n manta-fase4-staging -- \
  curl -v telnet://code-refactor-engine:8081
```

## Data Management

### Persistent Data
Staging uses separate PVs from production:
- ML models: `/mnt/ml-models-staging`
- Prometheus: `/mnt/prometheus-staging`
- Elasticsearch: `/mnt/elasticsearch-staging`

### Data Retention
```bash
# Prometheus: 7 days (vs 30 days production)
# Jaeger: 48 hours (vs 7 days production)
# Elasticsearch: 24 hours (vs 30 days production)
```

### Reset Staging
```bash
# Clear all data
kubectl delete pvc --all -n manta-fase4-staging

# Redeploy fresh
kubectl apply -k fase4/k8s-staging/
```

## CI/CD Integration

### Automated Testing Pipeline
```yaml
# GitLab CI or GitHub Actions
stages:
  - deploy-staging
  - integration-tests
  - load-tests
  - security-tests
  - promote-to-prod

deploy_staging:
  script:
    - kubectl apply -k fase4/k8s-staging/
    - bash fase4/k8s-production/validate-deployment.sh

integration_tests:
  script:
    - pytest tests/integration/
    - newman run tests/postman_collection.json

load_tests:
  script:
    - k6 run tests/load/load-test.js
    - curl prometheus:9090/api/v1/query?query=...

security_tests:
  script:
    - kube-bench run --targets node,policies
    - trivy image manta-fase4/platform-router:1.0.0
```

## Promotion to Production

### Pre-Production Checklist
- [ ] All integration tests passing
- [ ] Load tests show acceptable performance
- [ ] Security tests passing (no vulnerabilities)
- [ ] Manual testing completed
- [ ] Documentation reviewed and updated
- [ ] Team approval obtained
- [ ] Rollback plan documented

### Promotion Process
```bash
# 1. Tag images as production-ready
docker tag manta-fase4/platform-router:1.0.0-staging \
           manta-fase4/platform-router:1.0.0

# 2. Deploy to production
kubectl apply -k fase4/k8s-production/

# 3. Monitor production deployment
kubectl logs -f deployment/platform-router -n manta-fase4-prod

# 4. Activate canary gates (Phase 0: audit mode)
# Phase 0 (audit): 95% confidence, 0% traffic
# Phase 1: 90% confidence, 5% traffic
# Phase 2: 85% confidence, 25% traffic
# Phase 3: 75% confidence, 100% traffic
```

## Maintenance

### Regular Tasks
- Daily: Review logs for errors
- Weekly: Run full integration test suite
- Weekly: Check resource utilization
- Bi-weekly: Update base images from production
- Monthly: Full staging reset and redeploy

### Updating Staging
```bash
# Update base kustomization
git pull origin main

# Redeploy with new configuration
kubectl apply -k fase4/k8s-staging/

# Validate deployment
bash fase4/k8s-production/validate-deployment.sh
```

## Cost Optimization

### Staging Sizing
- 2 Router replicas (vs 3 production)
- 1 Refactor replica (vs 2 production)
- 2 ML replicas (vs 3 production)
- ~30% lower resource cost than production

### Off-Hours Shutdown
```bash
# Scale down all replicas at end of business
kubectl scale deployment --all --replicas=1 -n manta-fase4-staging

# Scale back up next morning
kubectl scale deployment --all --replicas=2 -n manta-fase4-staging
```

## Documentation

- **Architecture**: See production README.md
- **Integration Tests**: See INTEGRATION_TESTS.md
- **Deployment Scripts**: See deployment-script.sh
- **Performance Baselines**: See FASE4_COMPLETE_SUMMARY.md

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs with `kubectl logs -f`
3. Check Prometheus metrics for performance issues
4. Consult with Platform Engineering team
