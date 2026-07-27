# Manta Maestro — Kubernetes Deployment Guide

Complete step-by-step guide for deploying Manta Maestro to production and staging Kubernetes clusters.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Cluster Setup](#cluster-setup)
4. [Secrets Management](#secrets-management)
5. [Deployment Steps](#deployment-steps)
6. [Verification](#verification)
7. [Post-Deployment](#post-deployment)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **kubectl** (v1.24+): Kubernetes CLI
  ```bash
  kubectl version --client
  ```

- **Helm** (v3.8+): Kubernetes package manager
  ```bash
  helm version
  ```

- **kubeseal** (v0.24.0+): Sealed Secrets CLI (for secret encryption)
  ```bash
  wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz
  tar xfz kubeseal-0.24.0-linux-amd64.tar.gz -C /usr/local/bin/
  ```

- **Docker** (optional): For building/pushing images

### Access & Permissions

- kubeconfig configured for target cluster
- Cluster admin role (for initial setup)
- Access to image registry (e.g., Docker Hub, ECR, GCR)

### Kubernetes Cluster Requirements

- Version: 1.24+ (for rbac.authorization.k8s.io/v1)
- Nodes: 3+ (for HA)
- Total resources: 4+ CPU cores, 8GB+ RAM (minimum)
- Storage: PersistentVolume provisioner available

---

## Pre-Deployment Checklist

### Infrastructure

- [ ] Kubernetes cluster is running and accessible
- [ ] StorageClass is available for PostgreSQL persistence
  ```bash
  kubectl get storageclass
  ```
- [ ] DNS is configured for domain names
- [ ] Firewall rules allow inbound HTTPS (443)
- [ ] Load balancer provisioning is enabled

### Domain & TLS

- [ ] DNS A record points to Ingress IP
  ```bash
  nslookup api.manta.example.com
  ```
- [ ] Certificate authority (Let's Encrypt) is accessible
- [ ] Email for cert notifications is configured

### Docker Images

- [ ] FastAPI image is available in registry
  ```bash
  docker pull docker.io/mantaassociados/manta-fastapi:1.0.0
  ```
- [ ] React image is available
  ```bash
  docker pull docker.io/mantaassociados/manta-react:1.0.0
  ```
- [ ] Alembic migration image is available
  ```bash
  docker pull docker.io/mantaassociados/manta-alembic:1.0.0
  ```

### Secrets & Credentials

- [ ] Claude API key obtained from Anthropic
- [ ] MCP server credentials (if applicable)
- [ ] Database password generated and stored securely
- [ ] JWT secret generated

---

## Cluster Setup

### 1. Install Ingress Controller (nginx)

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.metrics.enabled=true \
  --wait
```

Verify:
```bash
kubectl get service -n ingress-nginx
kubectl get pods -n ingress-nginx
```

### 2. Install Cert-Manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true \
  --set global.leaderElection.namespace=cert-manager \
  --wait
```

Verify:
```bash
kubectl get pods -n cert-manager
kubectl api-resources | grep certmanager
```

### 3. Create ClusterIssuer for Let's Encrypt

```bash
kubectl apply -f - <<'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: devops@mantaassociados.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx

---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: devops@mantaassociados.com
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

Verify:
```bash
kubectl get clusterissuer
kubectl describe clusterissuer letsencrypt-prod
```

### 4. Install Sealed Secrets

```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

Verify:
```bash
kubectl get deployment -n kube-system sealed-secrets-controller
kubectl get pods -n kube-system -l app.kubernetes.io/name=sealed-secrets
```

### 5. Create StorageClass (if not available)

```bash
# Example: SSD StorageClass for production
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/gce-pd  # GCP example; adjust per cloud provider
parameters:
  type: pd-ssd
  replication-type: regional-pd
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF

# Verify
kubectl get storageclass
```

---

## Secrets Management

### Step 1: Prepare Sealed Secrets

#### Generate Database Password Secret

```bash
# Create namespace first (if not exists)
kubectl create namespace manta
# or
kubectl create namespace manta-staging

# Generate and seal database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "PostgreSQL Password: $DB_PASSWORD"

echo -n "$DB_PASSWORD" | \
  kubectl create secret generic manta-db-secret \
    --dry-run=client \
    --from-file=postgres-password=/dev/stdin \
    -o yaml | \
  kubeseal -n manta -f - -w /tmp/db-secret-sealed.yaml

cat /tmp/db-secret-sealed.yaml
# Copy the encryptedData value to templates/secret-sealed.yaml
```

#### Generate API Secrets

```bash
# Store your actual Claude API key (from Anthropic)
CLAUDE_API_KEY="sk-ant-your-actual-key-here"
JWT_SECRET=$(openssl rand -base64 64)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Create temporary secret manifest
cat > /tmp/api-secrets.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: manta-api-secrets
type: Opaque
stringData:
  claude-api-key: "$CLAUDE_API_KEY"
  jwt-secret: "$JWT_SECRET"
  redis-password: "$REDIS_PASSWORD"
  mcp-server-key: "placeholder-if-needed"
EOF

# Seal it
kubeseal -n manta -f /tmp/api-secrets.yaml -w /tmp/api-secret-sealed.yaml

cat /tmp/api-secret-sealed.yaml
# Copy the encryptedData value to templates/secret-sealed.yaml
```

#### Update templates/secret-sealed.yaml

Replace placeholder values in `templates/secret-sealed.yaml` with the actual sealed values:

```yaml
spec:
  encryptedData:
    postgres-password: AgBvB3F8K2xL9m... # From db-secret-sealed.yaml
    claude-api-key: AgBvB3F8K2xL9m...   # From api-secret-sealed.yaml
    jwt-secret: AgBvB3F8K2xL9m...
    redis-password: AgBvB3F8K2xL9m...
```

### Step 2: Verify Sealed Secrets

```bash
# Deploy and verify unsealing works
kubectl apply -f templates/secret-sealed.yaml -n manta

# Wait for secrets to be created
kubectl get secrets -n manta

# Verify content (should be readable)
kubectl get secret manta-db-secret -n manta -o yaml
```

---

## Deployment Steps

### Step 1: Update values.yaml

Edit configuration for your environment:

```bash
# Copy appropriate values file
cp values-production.yaml values-prod.yaml

# Edit with your configuration
nano values-prod.yaml
```

Key updates:

```yaml
global:
  domain: manta.example.com

fastapi:
  image:
    tag: "1.0.0"  # Your release tag
  env:
    DATABASE_URL: "postgresql://manta:manta@postgres.manta.svc.cluster.local:5432/manta"

react:
  image:
    tag: "1.0.0"
  env:
    REACT_APP_API_URL: "https://api.manta.example.com"

postgres:
  persistence:
    storageClass: "fast-ssd"  # Your StorageClass
    size: "100Gi"
```

### Step 2: Helm Lint

Validate chart syntax:

```bash
helm lint .
```

Expected output:
```
==> Linting .
[INFO] Chart.yaml: icon is missing
1 chart(s) linted, 0 error(s)
```

### Step 3: Dry-Run Deployment

Preview what will be deployed:

```bash
helm upgrade --install manta . \
  -f values-prod.yaml \
  -n manta \
  --dry-run \
  --debug
```

Review output for any issues.

### Step 4: Deploy to Cluster

```bash
helm upgrade --install manta . \
  -f values-prod.yaml \
  -n manta \
  --create-namespace \
  --wait \
  --timeout 5m
```

Expected output:
```
Release "manta" does not exist. Installing it now.
NAME: manta
LAST DEPLOYED: 2026-07-26 12:00:00 UTC
NAMESPACE: manta
STATUS: deployed
...
```

### Step 5: Monitor Deployment Progress

```bash
# Watch deployments
kubectl rollout status deployment/manta-fastapi -n manta
kubectl rollout status deployment/manta-react -n manta
kubectl rollout status statefulset/manta-postgres -n manta

# Or watch all pods
kubectl get pods -n manta -w
```

Expected progression:
1. Database pod starts (PostgreSQL)
2. Init container runs (DB migration)
3. FastAPI pods start (after DB is ready)
4. React pod starts

---

## Verification

### Step 1: Verify Pods Are Running

```bash
kubectl get pods -n manta

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# manta-fastapi-xxxxx              1/1     Running   0          2m
# manta-fastapi-xxxxx              1/1     Running   0          2m
# manta-react-xxxxx                1/1     Running   0          2m
# manta-postgres-0                 1/1     Running   0          3m
```

### Step 2: Check Service Endpoints

```bash
kubectl get svc -n manta
kubectl get endpoints -n manta

# Verify services are bound to pods
kubectl describe svc manta-fastapi -n manta
```

### Step 3: Verify Ingress & TLS

```bash
kubectl get ingress -n manta

# Wait for TLS certificate to be issued (may take 1-2 minutes)
kubectl get certificate -n manta

# Check ingress IP
INGRESS_IP=$(kubectl get ingress manta-api -n manta -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"

# Update DNS if needed (or test with IP)
curl -kv https://$INGRESS_IP/health  # For IP-based access
curl https://api.manta.example.com/health  # For DNS-based access
```

### Step 4: Verify Database Connectivity

```bash
# Port-forward to PostgreSQL
kubectl port-forward svc/manta-postgres-client 5432:5432 -n manta &

# Connect using psql
psql -h localhost -U manta -d manta

# Inside psql, verify schema
\dt  # List tables
\dx  # List extensions (should include pgvector)
```

### Step 5: Test FastAPI Health

```bash
# Port-forward to FastAPI
kubectl port-forward svc/manta-fastapi 8000:8000 -n manta &

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready

# View API documentation
open http://localhost:8000/docs

# Check metrics
curl http://localhost:8000/metrics
```

### Step 6: Test React Frontend

```bash
# Port-forward to React
kubectl port-forward svc/manta-react 3000:80 -n manta &

# Open in browser
open http://localhost:3000

# Should see React app served successfully
```

### Step 7: Verify RBAC Permissions

```bash
# Check ServiceAccounts exist
kubectl get serviceaccount -n manta

# Verify Roles and RoleBindings
kubectl get role -n manta
kubectl get rolebinding -n manta

# Test RBAC (should fail - non-root user)
kubectl auth can-i get pods --as=system:serviceaccount:manta:manta-fastapi -n manta
```

### Step 8: Verify NetworkPolicies

```bash
# Check policies are in place
kubectl get networkpolicy -n manta

# Test connectivity:
# Pod to PostgreSQL should work
kubectl exec -it deployment/manta-fastapi -n manta -- \
  nc -zv postgres.manta.svc.cluster.local 5432

# Pod to external (should work)
kubectl exec -it deployment/manta-fastapi -n manta -- \
  curl https://api.anthropic.com/health
```

### Step 9: Verify HPA Status

```bash
kubectl get hpa -n manta

# Check current metrics
kubectl get hpa manta-fastapi -n manta --watch

# Trigger load test (optional)
kubectl run -it --rm debug --image=loadimpact/k6 --restart=Never -- \
  run /dev/stdin <<'EOF'
import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  http.get('http://manta-fastapi.manta.svc.cluster.local:8000/health');
  sleep(1);
}
EOF
```

---

## Post-Deployment

### Step 1: Enable Monitoring (Optional)

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Install Grafana
helm install grafana prometheus-community/grafana \
  -n monitoring

# Port-forward to Grafana
kubectl port-forward svc/grafana 3000:80 -n monitoring &
# Visit http://localhost:3000 (default: admin/prom-operator)
```

### Step 2: Enable Logging Aggregation (Optional)

```bash
# Install ELK Stack (Elasticsearch, Logstash, Kibana)
# Or use cloud providers' logging (CloudWatch, Stackdriver, etc.)

# Example: Google Cloud Logging
kubectl apply -f - <<'EOF'
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-gcp
  namespace: kube-system
spec:
  # ... Fluentd configuration
EOF
```

### Step 3: Configure Backup

```bash
# PostgreSQL backup script
cat > /usr/local/bin/backup-manta-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/backups/manta"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

kubectl exec -n manta manta-postgres-0 -- \
  pg_dump -U manta manta \
  > "$BACKUP_DIR/manta_$TIMESTAMP.sql"

# Compress
gzip "$BACKUP_DIR/manta_$TIMESTAMP.sql"

# Upload to cloud storage (example: S3)
aws s3 cp "$BACKUP_DIR/manta_$TIMESTAMP.sql.gz" s3://backup-bucket/manta/

echo "Backup completed: manta_$TIMESTAMP.sql.gz"
EOF

chmod +x /usr/local/bin/backup-manta-db.sh

# Schedule daily backup
echo "0 2 * * * /usr/local/bin/backup-manta-db.sh" | crontab -
```

### Step 4: Document Runbooks

Create operational runbooks:

- Scaling procedures
- Incident response
- Backup/restore
- Log analysis
- Performance tuning

---

## Rollback Procedures

### Rollback Last Helm Release

```bash
# Check release history
helm history manta -n manta

# Rollback to previous version
helm rollback manta -n manta

# Or rollback to specific revision
helm rollback manta 1 -n manta

# Verify
kubectl rollout status deployment/manta-fastapi -n manta
```

### Rollback PostgreSQL (Restore from Backup)

```bash
# Stop FastAPI pods to prevent writes
kubectl scale deployment manta-fastapi --replicas=0 -n manta

# Restore from backup
BACKUP_FILE="/backups/manta/manta_20260726_120000.sql.gz"
gunzip < $BACKUP_FILE | \
  kubectl exec -i manta-postgres-0 -n manta -- \
  psql -U manta manta

# Resume FastAPI
kubectl scale deployment manta-fastapi --replicas=3 -n manta

# Verify
kubectl rollout status deployment/manta-fastapi -n manta
```

---

## Troubleshooting

### Pods stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n manta

# Common causes:
# 1. PVC pending (storage not provisioned)
kubectl get pvc -n manta

# 2. Insufficient resources
kubectl top nodes

# 3. Node selector not matching
kubectl get nodes --show-labels

# Fix:
kubectl describe pvc manta-postgres-postgresql-data-manta-postgres-0 -n manta
```

### Database migration failures

```bash
# Check init container logs
kubectl logs manta-fastapi-xxxxx -c db-migrate -n manta

# Common issues:
# - Network connectivity to DB
kubectl exec -it manta-fastapi-xxxxx -n manta -- \
  nc -zv postgres.manta.svc.cluster.local 5432

# - Schema already exists
kubectl exec -it manta-postgres-0 -n manta -- \
  psql -U manta -d manta -c "SELECT version();"

# Fix: Check alembic migration files
ls -la alembic/versions/
```

### API returns 502 Bad Gateway

```bash
# Check FastAPI pod logs
kubectl logs deployment/manta-fastapi -n manta

# Check if FastAPI is listening
kubectl exec -it deployment/manta-fastapi -n manta -- \
  netstat -tulpn | grep 8000

# Check database connectivity from pod
kubectl exec -it deployment/manta-fastapi -n manta -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### Certificate not issued

```bash
# Check certificate status
kubectl get certificate -n manta
kubectl describe certificate manta-api-tls -n manta

# Check cert-manager logs
kubectl logs -f deployment/cert-manager -n cert-manager

# Force renewal
kubectl delete certificate manta-api-tls -n manta
kubectl apply -f template for Ingress
```

### High memory/CPU usage

```bash
# Check resource usage
kubectl top pods -n manta
kubectl top nodes

# If pods exceed limits:
kubectl describe pod <pod-name> -n manta | grep -A 10 "Limits"

# Adjust limits in values.yaml and redeploy
helm upgrade manta . -f values-prod.yaml -n manta
```

---

## Support

For issues or questions:
- Check logs: `kubectl logs -f <pod> -n manta`
- Check events: `kubectl describe <resource> -n manta`
- Review CLAUDE.md for agent routing rules
- Check GitHub issues: https://github.com/mantaassociados/manta-maestro

---

**Last Updated**: 2026-07-26  
**Chart Version**: 1.0.0  
**Status**: Production-Ready
