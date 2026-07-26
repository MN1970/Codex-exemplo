# Manta Maestro Helm Chart

Production-ready Kubernetes Helm chart for **Manta Maestro** — an AI agent orchestration platform for intelligent infrastructure and engineering consulting.

## Overview

This Helm chart deploys a complete Manta stack on Kubernetes:

- **FastAPI Backend** (2+ replicas) — Agent orchestration, API routing, LLM integration
- **React SPA Frontend** (1+ replica) — Web-based UI with reverse proxy to FastAPI
- **PostgreSQL Database** (1 StatefulSet) — Data persistence with pgvector extension for embeddings
- **RBAC & NetworkPolicies** — Fine-grained access control and network isolation
- **HPA (Horizontal Pod Autoscaling)** — Auto-scaling based on CPU/memory metrics
- **Ingress with TLS** — HTTPS termination via cert-manager (Let's Encrypt)
- **Sealed Secrets** — Encrypted secrets management (or HashiCorp Vault)

## Prerequisites

### Kubernetes Cluster

- Kubernetes 1.24+ (uses rbac.authorization.k8s.io/v1, networking.k8s.io/v1)
- kubectl configured to access your cluster
- Helm 3.8+ installed

### Required Components

1. **Ingress Controller** (nginx-ingress or similar)
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     -n ingress-nginx --create-namespace
   ```

2. **Cert-Manager** (for TLS certificate provisioning)
   ```bash
   helm repo add jetstack https://charts.jetstack.io
   helm install cert-manager jetstack/cert-manager \
     -n cert-manager --create-namespace \
     --set installCRDs=true
   ```

3. **Sealed Secrets Controller** (for secret encryption)
   ```bash
   kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
   ```

4. **StorageClass** (for PostgreSQL persistence)
   ```bash
   kubectl get storageclass  # Check available classes
   # Update values.postgres.persistence.storageClass if needed
   ```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mantaassociados/manta-maestro.git
cd manta-maestro/manta-helm
```

### 2. Create Sealed Secrets

#### Option A: Sealed Secrets (Recommended)

```bash
# Generate sealing key (already in cluster from controller installation)
kubeseal --fetch-cert > sealing-public-key.pem

# Create and seal database password
echo -n 'your-super-secure-postgres-password' | \
  kubectl create secret generic manta-db-secret \
    --dry-run=client \
    --from-file=postgres-password=/dev/stdin \
    -o yaml | \
  kubeseal -f - -w /tmp/db-secret-sealed.yaml

# Extract sealed value and update templates/secret-sealed.yaml
grep 'postgres-password:' /tmp/db-secret-sealed.yaml
# Copy the AgBvB3F8K2xL9m... value to templates/secret-sealed.yaml

# Repeat for API secrets
echo -n 'sk-ant-your-claude-api-key' | \
  kubectl create secret generic manta-api-secrets \
    --dry-run=client \
    --from-file=claude-api-key=/dev/stdin \
    -o yaml | \
  kubeseal -f - -w /tmp/api-secret-sealed.yaml
```

#### Option B: HashiCorp Vault

See [Secret Management](#secret-management) section below.

### 3. Update values.yaml

Edit `values.yaml` with your environment-specific values:

```yaml
# Domain names
global:
  domain: manta.example.com

# FastAPI configuration
fastapi:
  replicas: 2
  image:
    tag: "1.0.0"  # Your image tag
  env:
    DATABASE_URL: "postgresql://manta:manta@postgres.manta.svc.cluster.local:5432/manta"

# React configuration
react:
  replicas: 1
  image:
    tag: "1.0.0"  # Your image tag
  env:
    REACT_APP_API_URL: "https://api.manta.example.com"

# PostgreSQL
postgres:
  replicas: 1
  auth:
    database: "manta"
    username: "manta"
  persistence:
    storageClass: "standard"  # Or your StorageClass
    size: "20Gi"

# Autoscaling
autoscaling:
  fastapi:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
  react:
    enabled: true
    minReplicas: 1
    maxReplicas: 5
```

### 4. Deploy with Helm

```bash
# Add repository (if using Helm repo)
helm repo add manta https://charts.mantaassociados.com
helm repo update

# Install or upgrade
helm upgrade --install manta . \
  -f values.yaml \
  -n manta \
  --create-namespace

# Check status
kubectl rollout status deployment/manta-fastapi -n manta
kubectl rollout status deployment/manta-react -n manta
kubectl rollout status statefulset/manta-postgres -n manta
```

### 5. Verify Installation

```bash
# Check pods
kubectl get pods -n manta

# Check services
kubectl get svc -n manta

# Check ingress
kubectl get ingress -n manta

# View logs
kubectl logs -f deployment/manta-fastapi -n manta
kubectl logs -f deployment/manta-react -n manta

# Port-forward for testing
kubectl port-forward svc/manta-fastapi 8000:8000 -n manta
# Visit http://localhost:8000/docs for API Swagger UI
```

## Configuration

### Environment Variables

FastAPI environment variables are defined in `values.fastapi.env`:

- `LOG_LEVEL` — Logging level (INFO, DEBUG, WARNING)
- `DATABASE_URL` — PostgreSQL connection string
- `AGENT_ROUTING_CONFIG` — Path to agent routing YAML
- `API_WORKERS` — Number of Uvicorn workers
- `REDIS_URL` — Optional Redis for caching

### Secret Management

#### Sealed Secrets (Default)

Secrets in `templates/secret-sealed.yaml` are encrypted with the sealing key from the sealed-secrets controller.

To update secrets:

```bash
# Edit and reseal
echo -n 'new-password' | \
  kubectl create secret generic manta-db-secret \
    --dry-run=client \
    --from-file=postgres-password=/dev/stdin \
    -o yaml | \
  kubeseal -f - -w secret.yaml
```

#### HashiCorp Vault

Edit `values.yaml`:

```yaml
secrets:
  sealed:
    enabled: true
    sealer: "vault"  # Instead of "sealed-secrets"
    namespace: "vault"
```

Install External Secrets Operator and configure Vault access as described in `templates/secret-sealed.yaml`.

### Ingress Configuration

Update `values.yaml` for custom domain and TLS:

```yaml
fastapi:
  ingress:
    enabled: true
    hosts:
      - host: api.manta.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: manta-api-tls
        hosts:
          - api.manta.example.com

react:
  ingress:
    enabled: true
    hosts:
      - host: manta.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: manta-web-tls
        hosts:
          - manta.example.com
```

#### TLS Certificate Provisioning (Cert-Manager)

Ensure cert-manager is configured with a ClusterIssuer:

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@mantaassociados.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

## Architecture

### Deployment Strategy

- **Rolling Updates** — Zero-downtime deployments (maxSurge: 1, maxUnavailable: 0)
- **Health Checks** — Liveness and readiness probes on all containers
- **Pod Disruption Budgets** — Prevents cluster upgrades from disrupting service
- **Anti-Affinity** — Spreads pods across nodes for high availability

### Security

- **RBAC** — Service accounts with minimal permissions per component
- **NetworkPolicies** — Restrict traffic between pods (FastAPI↔DB, React↔FastAPI)
- **Pod Security** — Non-root users, read-only filesystems where possible
- **Sealed Secrets** — Encrypted credentials in etcd
- **Resource Limits** — CPU/memory requests and limits prevent resource exhaustion

### Scaling

#### Horizontal Pod Autoscaler (HPA)

Automatically scales based on CPU and memory utilization:

```yaml
autoscaling:
  fastapi:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

To monitor HPA status:

```bash
kubectl get hpa -n manta -w
```

#### Manual Scaling

```bash
kubectl scale deployment manta-fastapi --replicas=5 -n manta
```

## Monitoring & Logging

### Prometheus Metrics

FastAPI exposes metrics at `/metrics`:

```bash
kubectl port-forward svc/manta-fastapi 8000:8000 -n manta
curl http://localhost:8000/metrics
```

### Logs

```bash
# FastAPI logs
kubectl logs -f deployment/manta-fastapi -n manta --all-containers=true

# React logs
kubectl logs -f deployment/manta-react -n manta

# PostgreSQL logs
kubectl logs -f statefulset/manta-postgres -n manta

# View last 100 lines
kubectl logs deployment/manta-fastapi -n manta --tail=100
```

### ELK Stack Integration

Configure logging driver in `values.yaml`:

```yaml
monitoring:
  logging:
    enabled: true
    driver: "json-file"
```

## Upgrades & Maintenance

### Upgrading the Chart

```bash
# Update Helm repository
helm repo update

# Dry-run to preview changes
helm upgrade manta manta/manta \
  -f values.yaml \
  -n manta \
  --dry-run --debug

# Perform upgrade (rolling update for zero downtime)
helm upgrade manta manta/manta \
  -f values.yaml \
  -n manta
```

### Database Migrations

The FastAPI deployment includes an init container that runs `alembic upgrade head` before the app starts:

```yaml
initContainers:
  - name: db-migrate
    # Runs migration on every pod startup
```

Ensure your application includes migration files in `alembic/versions/`.

### PostgreSQL Backup

For production, configure regular backups:

```bash
# Create backup using pg_dump
kubectl exec -it manta-postgres-0 -n manta -- \
  pg_dump -U manta manta > backup.sql

# Restore from backup
kubectl cp backup.sql manta-postgres-0:/tmp/ -n manta
kubectl exec -it manta-postgres-0 -n manta -- \
  psql -U manta manta < /tmp/backup.sql
```

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n manta

# Check logs
kubectl logs <pod-name> -n manta --previous  # For crashed pods
```

### Database connection errors

```bash
# Test PostgreSQL connectivity
kubectl exec -it deployment/manta-fastapi -n manta -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://...')"

# Check PostgreSQL service DNS
kubectl exec -it deployment/manta-fastapi -n manta -- \
  nslookup postgres.manta.svc.cluster.local
```

### Ingress not working

```bash
# Check ingress status
kubectl describe ingress manta-api -n manta
kubectl get ingress -n manta -o yaml

# Check cert-manager certificate
kubectl get certificate -n manta
kubectl describe certificate manta-api-tls -n manta
```

### High memory usage

```bash
# Check resource usage
kubectl top pods -n manta

# Adjust resource limits in values.yaml
fastapi:
  resources:
    limits:
      memory: 4Gi  # Increase as needed
```

## Production Checklist

- [ ] Replace placeholder domain names (manta.example.com) with actual domains
- [ ] Update Docker image repositories and tags
- [ ] Create and encrypt secrets (DB password, API keys)
- [ ] Configure StorageClass for persistent volumes
- [ ] Set up cert-manager with production Let's Encrypt issuer
- [ ] Configure network policies for your environment
- [ ] Enable monitoring (Prometheus, Grafana)
- [ ] Set up log aggregation (ELK, CloudWatch)
- [ ] Configure alerts for pod crashes, resource usage
- [ ] Test backup and restore procedures
- [ ] Document runbooks for common operations
- [ ] Plan scaling strategy (initial replicas, HPA settings)
- [ ] Review and approve RBAC permissions
- [ ] Enable pod security standards/policies
- [ ] Configure resource quotas by namespace

## Support & Documentation

- **CLAUDE.md** — Agent registry and routing rules
- **GitHub Issues** — https://github.com/mantaassociados/manta-maestro/issues
- **Manta Documentation** — https://mantaassociados.com/docs

## License

© 2026 Manta Associados. All rights reserved.
