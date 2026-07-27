# Fase 4 - Git Evolution Suite Kubernetes Deployment

## Overview

This directory contains production-ready Kubernetes manifests for deploying the Fase 4 Git Evolution Suite on Kubernetes. The suite consists of 4 integrated pillars:

- **Pillar A**: Multi-platform Router (Platform Abstraction Layer)
- **Pillar B**: AST-based Code Refactoring Engine (55 detection rules)
- **Pillar C**: OpenTelemetry Observability Stack (Jaeger, Prometheus, Grafana, Alertmanager)
- **Pillar D**: Advanced ML v2.0 (50-feature ensemble, 93.65% accuracy)

## Files Structure

```
k8s-production/
├── README.md                          # This file
├── namespace.yaml                     # Namespace, RBAC, network policies, resource quotas
├── storage.yaml                       # PersistentVolumes, PersistentVolumeClaims, StorageClasses
├── pillar-a-router.yaml               # Platform router deployment, service, HPA
├── pillar-b-refactor.yaml             # Code refactoring engine deployment, configmaps
├── pillar-c-observability.yaml        # Jaeger, Prometheus, Grafana, Alertmanager deployments
├── pillar-d-ml-model.yaml             # ML inference service, daily scoring CronJob
├── monitoring-configs.yaml            # Prometheus scrape configs, alerts, Grafana datasources
├── ingress-and-networking.yaml        # Ingress, NetworkPolicies, PodDisruptionBudgets
├── secrets-template.yaml              # Secrets template for credentials
└── deployment-script.sh               # Automated deployment script
```

## Prerequisites

### Cluster Requirements
- Kubernetes 1.24+
- 16+ CPU cores
- 32+ GB RAM
- 300+ GB disk space
- Ingress controller (nginx-ingress recommended)
- cert-manager for TLS certificate management
- Dynamic persistent volume provisioning

### Software Requirements
- kubectl 1.24+
- Helm 3.10+ (optional, for package management)
- kustomize (optional, for template management)

### Kubernetes Nodes
Label your nodes appropriately for scheduling:

```bash
# For ML model storage (ReadOnlyMany)
kubectl label nodes <node-name> ml-node=true

# For monitoring (Prometheus, etc.)
kubectl label nodes <node-name> monitoring-node=true

# For observability stack
kubectl label nodes <node-name> observability-node=true
```

## Pre-Deployment Setup

### 1. Namespace and RBAC
```bash
kubectl apply -f namespace.yaml
```

This creates:
- Namespace: `manta-fase4-prod`
- ServiceAccount: `manta-fase4-sa`
- Role with minimal permissions (read-only for most resources)
- RoleBinding connecting role to service account
- ResourceQuota: 32 CPU requests, 64Gi memory requests
- LimitRange: Container max 4 CPU/8Gi, Pod max 8 CPU/16Gi
- NetworkPolicy: Ingress/Egress rules for security

### 2. Storage
```bash
kubectl apply -f storage.yaml
```

This creates:
- PersistentVolumes for ML models (100Gi, ReadOnlyMany)
- PersistentVolumes for Prometheus (50Gi, ReadWriteOnce)
- PersistentVolumes for Elasticsearch (100Gi, ReadWriteOnce)
- StorageClasses for fast (SSD) and standard storage

### 3. Configure Secrets
Copy and customize the secrets template:

```bash
cp secrets-template.yaml secrets.yaml
# Edit secrets.yaml and replace all REPLACE_WITH_* values
# Do NOT commit secrets.yaml to git - use a secure secrets management solution
kubectl apply -f secrets.yaml
```

**Important**: Never commit actual secrets to version control. Use:
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- External Secrets Operator
- Sealed Secrets (for git-friendly encryption)

## Deployment

### Option 1: Automated Deployment (Recommended)
```bash
./deployment-script.sh
```

The script performs:
1. Pre-flight checks (cluster connectivity, resource availability)
2. Namespace and RBAC setup
3. Storage configuration
4. Observability stack deployment (Jaeger, Prometheus, Grafana, Alertmanager)
5. Pillar A: Platform Router
6. Pillar B: Code Refactoring Engine
7. Pillar C: ML Inference Service
8. Health checks and validation
9. Monitoring dashboard setup
10. Canary gate activation

### Option 2: Manual Deployment
```bash
# 1. Create namespace and RBAC
kubectl apply -f namespace.yaml

# 2. Create storage
kubectl apply -f storage.yaml

# 3. Configure monitoring
kubectl apply -f monitoring-configs.yaml

# 4. Deploy observability stack
kubectl apply -f pillar-c-observability.yaml

# 5. Deploy pillar A (router)
kubectl apply -f pillar-a-router.yaml

# 6. Deploy pillar B (refactoring)
kubectl apply -f pillar-b-refactor.yaml

# 7. Deploy pillar D (ML)
kubectl apply -f pillar-d-ml-model.yaml

# 8. Configure networking
kubectl apply -f ingress-and-networking.yaml

# 9. Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=platform-router -n manta-fase4-prod --timeout=300s
```

## Post-Deployment Verification

### Check Pod Status
```bash
kubectl get pods -n manta-fase4-prod
kubectl get svc -n manta-fase4-prod
kubectl get ingress -n manta-fase4-prod
```

### Verify Health
```bash
# Platform Router
kubectl exec -it deployment/platform-router -n manta-fase4-prod -- curl localhost:8080/health/ready

# Code Refactor Engine
kubectl exec -it deployment/code-refactor-engine -n manta-fase4-prod -- curl localhost:8081/health/ready

# ML Inference
kubectl exec -it deployment/ml-inference -n manta-fase4-prod -- curl localhost:8082/health/ready
```

### Monitor Logs
```bash
# Follow logs for platform router
kubectl logs -f deployment/platform-router -n manta-fase4-prod

# Follow logs for all Fase 4 components
kubectl logs -f -l component=pillar-a,pillar-b,pillar-d -n manta-fase4-prod --all-containers=true
```

## Access Services

### Grafana Dashboard
```bash
# Port forward to access locally
kubectl port-forward svc/grafana 3000:3000 -n manta-fase4-prod
# Access at http://localhost:3000 (default: admin/changeme)
```

### Prometheus
```bash
kubectl port-forward svc/prometheus 9090:9090 -n manta-fase4-prod
# Access at http://localhost:9090
```

### Jaeger Tracing
```bash
kubectl port-forward svc/jaeger-query 16686:16686 -n manta-fase4-prod
# Access at http://localhost:16686
```

### Via Ingress (if configured)
- Router API: https://router.manta.local
- Refactor Engine: https://refactor.manta.local
- Observability: https://observability.manta.local
- ML Inference: https://ml.manta.local

## Scaling

### Horizontal Pod Autoscaling (HPA)
Services have HPA configured to automatically scale based on CPU and memory usage:

```bash
# Check HPA status
kubectl get hpa -n manta-fase4-prod

# View HPA details
kubectl describe hpa platform-router-hpa -n manta-fase4-prod
```

### Manual Scaling
```bash
# Scale platform router to 5 replicas
kubectl scale deployment/platform-router --replicas=5 -n manta-fase4-prod

# Scale ML inference to 8 replicas
kubectl scale deployment/ml-inference --replicas=8 -n manta-fase4-prod
```

## Monitoring & Alerting

### Metrics Exported
- **Request metrics**: rate, latency (p50, p95, p99), errors
- **System metrics**: CPU, memory, disk, network
- **ML metrics**: model confidence, drift detection, anomaly detection
- **Application metrics**: feature extraction time, inference latency, batch processing rate

### Alert Rules
Pre-configured alerts for:
- High error rate (>5%)
- High latency (P95 > 5s)
- ML model drift detected
- Anomaly detection triggered
- Pod crash looping
- Persistent volume filling up (>80%)

### Custom Metrics
Add custom Prometheus metrics via `prometheus-rules` ConfigMap:

```bash
kubectl edit configmap prometheus-config -n manta-fase4-prod
```

## Troubleshooting

### Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name> -n manta-fase4-prod --previous

# Describe pod for events
kubectl describe pod <pod-name> -n manta-fase4-prod
```

### Resource Quota Exceeded
```bash
# Check quota usage
kubectl describe resourcequota manta-fase4-quota -n manta-fase4-prod

# Increase quota if needed
kubectl edit resourcequota manta-fase4-quota -n manta-fase4-prod
```

### Network Issues
```bash
# Test connectivity between pods
kubectl run -it --rm debug --image=busybox --restart=Never -n manta-fase4-prod -- sh
# Inside pod: wget -O- http://platform-router/health/ready

# Check network policies
kubectl get networkpolicy -n manta-fase4-prod
kubectl describe networkpolicy <policy-name> -n manta-fase4-prod
```

### Storage Issues
```bash
# Check PVC status
kubectl get pvc -n manta-fase4-prod
kubectl describe pvc ml-model-pvc -n manta-fase4-prod

# Check PV status
kubectl get pv
kubectl describe pv ml-model-pv
```

## Upgrades

### Rolling Updates
Deployments use RollingUpdate strategy with 0 downtime:
- maxSurge: 1 (one extra pod during update)
- maxUnavailable: 0 (no pod downtime)

```bash
# Trigger rolling update of platform router
kubectl set image deployment/platform-router \
  router=manta-fase4/platform-router:1.1.0 \
  -n manta-fase4-prod
```

### Canary Deployments
ML model updates use canary approach (Phase 0-3):
- Phase 0: Audit mode (95% confidence)
- Phase 1: 5% production traffic
- Phase 2: 25% production traffic
- Phase 3: Full deployment

## Backup & Disaster Recovery

### Backup ConfigMaps
```bash
kubectl get configmap -n manta-fase4-prod -o yaml > configmaps-backup.yaml
```

### Backup Secrets (Encrypted)
```bash
kubectl get secret -n manta-fase4-prod -o yaml | \
  gpg --encrypt --recipient your-key-id > secrets-backup.yaml.gpg
```

### Backup Persistent Volumes
```bash
# Create snapshot of Prometheus volume
kubectl get pv prometheus-pv -o json | jq '.spec' > prometheus-pv-backup.json
```

## Security Best Practices

1. **RBAC**: ServiceAccount has minimal read-only permissions
2. **Network Policies**: Ingress/Egress rules restrict traffic between pods
3. **Pod Security**: Pods run as non-root with security contexts
4. **Secrets Management**: Use external secrets solution, never commit plaintext secrets
5. **Resource Limits**: All pods have CPU/memory requests and limits
6. **Health Checks**: Liveness, readiness, and startup probes configured
7. **Pod Disruption Budgets**: Ensure availability during cluster maintenance

## Performance Tuning

### Resource Requests/Limits
Adjust based on your workload:

```yaml
resources:
  requests:
    cpu: "1"           # Minimum guaranteed CPU
    memory: "1Gi"      # Minimum guaranteed memory
  limits:
    cpu: "4"           # Maximum allowed CPU
    memory: "4Gi"      # Maximum allowed memory
```

### Cache Tuning
Adjust cache sizes in environment variables:

```bash
kubectl set env deployment/platform-router \
  CACHE_SIZE_MB=1024 \
  -n manta-fase4-prod
```

### Parallelism
Adjust batch sizes and parallelism for better throughput:

```bash
kubectl set env deployment/ml-inference \
  BATCH_SIZE=64 \
  -n manta-fase4-prod
```

## Support & Documentation

- Architecture: See `FASE4_COMPLETE_SUMMARY.md`
- Integration Tests: See `INTEGRATION_TESTS.md`
- Deployment Roadmap: See `FASE4-IMPLEMENTATION-ROADMAP.md`
- Deployment Automation: See `deployment-script.sh`

## Version Information

- Kubernetes Version: 1.24+
- Jaeger: v1.38.0
- Prometheus: v2.40.0
- Grafana: v9.2.0
- Alertmanager: v0.24.0

## License

Manta Associados - 2026
