# Deployment Guide — Codex Hub MCP

Guia completo para deployment de desenvolvimento local a produção.

**Versão:** 1.0.0  
**Atualizado:** 2026-07-31  
**Mantainer:** Manta Associados Engineering Team

---

## Índice

1. [Prerequisites](#prerequisites)
2. [Local Setup (Docker Compose)](#local-setup-docker-compose)
3. [Staging Deployment (Railway)](#staging-deployment-railway)
4. [Production Deployment](#production-deployment)
5. [Rollback Procedure](#rollback-procedure)
6. [Troubleshooting](#troubleshooting)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Health Checks & Monitoring](#health-checks--monitoring)

---

## Prerequisites

### System Requirements

| Component | Requirement | Recommended |
|-----------|-------------|-------------|
| **Node.js** | >= 18.0.0 | 22.x (LTS) |
| **npm** | >= 9.0.0 | 10.x+ |
| **Docker** | >= 20.10 | Latest stable |
| **Docker Compose** | >= 1.29 | 2.20+ |
| **Git** | >= 2.30 | Latest |
| **Disk Space** | 2GB min | 5GB recommended |
| **RAM** | 2GB min | 8GB recommended |

### Node 22 Upgrade Path

Current state: **Node 20** (in Dockerfile)  
Target state: **Node 22** (future upgrade)

**To upgrade to Node 22:**

```bash
# Update Dockerfile
sed -i 's/FROM node:20-alpine/FROM node:22-alpine/g' Dockerfile

# Update package.json engines field
npm pkg set engines.node=">=22.0.0"

# Verify compatibility (run full test suite)
npm run test
npm run lint
```

### Required Credentials

Before starting, ensure you have:

- **GitHub**: Personal Access Token (PAT)
  ```
  Scopes: repo, workflow, read:org
  ```
- **Supabase**: Project URL & API Keys
  ```
  - SUPABASE_URL
  - SUPABASE_KEY (anon)
  - SUPABASE_SERVICE_ROLE (service role)
  ```
- **Anthropic**: API Key
  ```
  https://console.anthropic.com
  ```
- **Microsoft Graph**: Azure AD Token (optional for SharePoint)
  ```
  MS_TENANT_ID, MS_APP_ID, MS_APP_SECRET
  ```

### Installation Verification

```bash
# Check Node version (22.x or higher)
node --version
# v22.x.x

# Check npm version (10.x or higher)
npm --version
# 10.x.x

# Check Docker
docker --version
# Docker version 20.10+

# Check Docker Compose
docker compose version
# Docker Compose version 2.20+
```

---

## Local Setup (Docker Compose)

### Step 1: Clone Repository

```bash
git clone https://github.com/manta-associados/Codex-exemplo.git
cd Codex-exemplo
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Minimum required variables:**

```bash
# .env (development)
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug

ANTHROPIC_API_KEY=sk_your_key_here
CLAUDE_MODEL=claude-opus-4-1

SUPABASE_URL=https://your_project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE=your_service_role_key

GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=manta-associados
GITHUB_REPO=Codex-exemplo
GITHUB_DEFAULT_BRANCH=main
```

### Step 3: Verify Docker Setup

```bash
# Check docker-compose.yml exists
test -f docker-compose.yml && echo "✓ Found docker-compose.yml"

# Validate docker-compose configuration
docker compose config > /dev/null && echo "✓ Valid Docker Compose configuration"
```

### Step 4: Start Local Environment

```bash
# Start all services (app, PostgreSQL, Redis)
docker compose up -d

# Check service status
docker compose ps
# Expected output:
# NAME                STATUS              PORTS
# codex-app           Up 2 minutes        0.0.0.0:3000->3000/tcp
# codex-postgres      Up 2 minutes        0.0.0.0:5432->5432/tcp
# codex-redis         Up 2 minutes        0.0.0.0:6379->6379/tcp
```

### Step 5: Database Initialization

```bash
# Install dependencies
npm install

# Run migrations
npm run db:migrate

# (Optional) Seed test data
npm run db:seed

# Check database connection
npm run type-check
```

### Step 6: Verify Application

```bash
# Health check endpoint
curl http://localhost:3000/health
# Expected: {"status":"ok","timestamp":"2026-07-31T12:00:00Z"}

# View logs
docker compose logs -f codex-app

# Run tests
npm run test

# Run linter
npm run lint
```

### Local Development Workflow

```bash
# Watch mode (auto-rebuild on file changes)
npm run dev

# In another terminal, tail logs
docker compose logs -f codex-app

# Stop services when done
docker compose down

# Full cleanup (remove volumes)
docker compose down -v
```

### Accessing Local Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Application** | http://localhost:3000 | N/A |
| **Health Check** | http://localhost:3000/health | N/A |
| **PostgreSQL** | localhost:5432 | `postgres:postgres` |
| **Redis** | localhost:6379 | none |

---

## Staging Deployment (Railway)

### Prerequisites

- Railway account: https://railway.app
- GitHub repository connected to Railway
- Railway CLI installed: `npm install -g @railway/cli`

### Step 1: Connect Repository to Railway

```bash
# Login to Railway CLI
railway login

# Link project
railway link

# Select or create a new project named "codex-staging"
```

### Step 2: Create Environment Variables in Railway

```bash
# Via Railway Dashboard > Project > Variables
# Or via CLI:

railway variables set NODE_ENV=staging
railway variables set PORT=3000
railway variables set LOG_LEVEL=info

railway variables set ANTHROPIC_API_KEY=sk_your_key_here
railway variables set CLAUDE_MODEL=claude-sonnet-4

railway variables set SUPABASE_URL=https://staging.supabase.co
railway variables set SUPABASE_KEY=your_staging_key
railway variables set SUPABASE_SERVICE_ROLE=your_staging_role

railway variables set GITHUB_TOKEN=ghp_your_token_here
railway variables set GITHUB_OWNER=manta-associados
railway variables set GITHUB_REPO=Codex-exemplo
```

**Note:** Use **staging** credentials for Anthropic, Supabase, etc.

### Step 3: Configure Railway Services

Create `railway.json`:

```json
{
  "services": {
    "app": {
      "dockerfile": "Dockerfile",
      "variables": {
        "NODE_ENV": "staging",
        "LOG_LEVEL": "info"
      },
      "buildCommand": "npm install && npm run build",
      "startCommand": "npm run start"
    },
    "postgres": {
      "image": "postgres:15-alpine",
      "variables": {
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "RANDOM",
        "POSTGRES_DB": "codex_staging"
      }
    },
    "redis": {
      "image": "redis:7-alpine"
    }
  }
}
```

### Step 4: Deploy to Staging

```bash
# Push to staging branch (triggers auto-deploy)
git checkout -b staging origin/staging
git push origin staging

# Or manual deploy via CLI
railway up

# Monitor deployment
railway logs -f

# Expected output:
# [INFO] Deploying codex-hub-mcp v1.0.0
# [INFO] Building Docker image...
# [INFO] Build complete, pushing...
# [INFO] Deployment successful at https://codex-staging.up.railway.app
```

### Step 5: Verify Staging Deployment

```bash
# Health check
curl https://codex-staging.up.railway.app/health

# Check logs
railway logs

# Run smoke tests against staging
npm run test:staging
```

### Step 6: Database Migrations on Staging

```bash
# Run migrations in Railway environment
railway run npm run db:migrate

# Verify database state
railway run npm run db:verify
```

### Rollback Staging Deployment

```bash
# Revert to previous deployment
railway rollback

# Or redeploy specific commit
railway deploy --commit <commit-sha>
```

---

## Production Deployment

### Pre-Deployment Checklist

**Code Quality**
- [ ] All tests passing: `npm run test`
- [ ] Linter clean: `npm run lint`
- [ ] Type checking passes: `npm run type-check`
- [ ] Code reviewed by at least 2 team members
- [ ] All comments resolved on PR

**Security**
- [ ] No hardcoded secrets in code
- [ ] Dependencies audit clean: `npm audit`
- [ ] All `CRITICAL` and `HIGH` vulnerabilities fixed
- [ ] Security review completed (see `/security-review`)

**Documentation**
- [ ] CHANGELOG.md updated with version & changes
- [ ] README.md up-to-date
- [ ] API endpoints documented
- [ ] Deployment notes written
- [ ] Known issues / limitations listed

**Infrastructure**
- [ ] Staging deployment verified (24 hours min)
- [ ] Database migration tested on staging
- [ ] Load testing completed (if applicable)
- [ ] Monitoring & alerting configured
- [ ] Backup procedures verified

**Coordination**
- [ ] Maintenance window scheduled (if needed)
- [ ] Stakeholders notified
- [ ] On-call engineer assigned
- [ ] Rollback plan tested

### Step 1: Create Release Tag

```bash
# Determine version (semantic versioning)
# MAJOR.MINOR.PATCH (e.g., 1.2.3)
VERSION=1.2.3

# Create annotated tag
git tag -a v${VERSION} -m "Release v${VERSION}: Description of changes"

# Push tag
git push origin v${VERSION}
```

### Step 2: Build & Test

```bash
# Verify build succeeds
npm run build

# Run full test suite
npm run test

# Run coverage report
npm run test:coverage

# Lint code
npm run lint

# Type check
npm run type-check
```

### Step 3: Deploy to Production

#### Option A: Via Railway (Recommended)

```bash
# Merge to main branch (triggers auto-deploy)
git checkout main
git merge --no-ff staging -m "Merge v${VERSION} to production"
git push origin main

# Or manual production deploy
railway --environment production up

# Monitor deployment
railway --environment production logs -f

# Expected: https://codex-hub.mantaassociados.com live
```

#### Option B: Via Custom Script

```bash
# Run deployment script
npm run deploy:prod

# This executes:
# 1. npm run build
# 2. npm run test
# 3. npm run lint
# 4. Uploads to production server
# 5. Runs migrations
# 6. Verifies health check
```

#### Option C: Manual Docker Push

```bash
# Build image
docker build -t ghcr.io/manta-associados/codex-hub:${VERSION} .

# Push to registry
docker push ghcr.io/manta-associados/codex-hub:${VERSION}

# Deploy via Kubernetes / Docker Swarm / etc.
# (deployment manifest maintained separately)
```

### Step 4: Database Migrations

```bash
# Backup production database FIRST
npm run db:backup

# Run migrations in production (with confirmation)
# Only if schema changes present in this release
npm run db:migrate -- --environment production

# Verify migration success
npm run db:verify -- --environment production
```

### Step 5: Post-Deployment Verification

```bash
# Health check
curl https://api.mantaassociados.com/health
# Expected: {"status":"ok","version":"1.2.3","timestamp":"..."}

# Check critical endpoints
curl https://api.mantaassociados.com/agents/maestro/route
# Expected: {"status":"ok","message":"Maestro router online"}

# Monitor logs
# tail -f /var/log/codex-hub/app.log

# Check system resources
# CPU, Memory, Disk usage within expected bounds

# Verify external integrations
# - [ ] Supabase connected
# - [ ] GitHub API responding
# - [ ] Anthropic Claude API responding
# - [ ] Redis connection healthy
```

### Step 6: Announce Release

```bash
# Create release notes
gh release create v${VERSION} \
  --title "Release v${VERSION}" \
  --notes "See CHANGELOG.md for details"

# Notify team (via Slack / Teams / etc.)
# Message template:
# 🚀 Production deployment successful
# Version: v1.2.3
# Time: 2026-07-31 14:30 UTC
# Changes: See https://github.com/manta-associados/Codex-exemplo/releases/tag/v1.2.3
# Health: ✅ All systems operational
```

---

## Rollback Procedure

### Automatic Rollback (First 30 minutes)

If critical issues detected within 30 minutes of deployment:

```bash
# One-command rollback
npm run rollback:prod

# This will:
# 1. Identify previous stable version
# 2. Revert code to previous tag
# 3. Revert database (if applicable)
# 4. Restart services
# 5. Verify health checks
```

### Manual Rollback (Beyond 30 minutes)

If issues detected after 30 minutes, use manual rollback:

#### Step 1: Identify Previous Version

```bash
# List recent production deployments
git log --oneline -20 | grep "^v"
# or
railway deployment list --environment production

# Find the last known good version
# e.g., v1.2.2 (before v1.2.3)
```

#### Step 2: Backup Current State

```bash
# Backup current database
npm run db:backup -- --tag "backup-before-rollback-v1.2.3"

# Backup current logs
tar -czf /backups/logs-v1.2.3-$(date +%s).tar.gz /var/log/codex-hub/
```

#### Step 3: Revert Code

```bash
# Option A: Via Git (if no database migration)
git revert -m 1 <merge-commit-sha>
git push origin main

# Option B: Via Tag (if database migration involved)
git checkout v1.2.2
git tag production-rollback-timestamp
git push origin v1.2.2:main --force
# ⚠️ USE FORCE PUSH ONLY WITH EXPLICIT TEAM APPROVAL
```

#### Step 4: Revert Database (if applicable)

```bash
# Check if rollback migration exists
ls supabase/migrations/ | grep rollback

# Run rollback migration
npm run db:migrate -- --rollback

# Or manually execute rollback SQL
psql $SUPABASE_DB_URL -f supabase/migrations/ROLLBACK_v1.2.3.sql
```

#### Step 5: Redeploy

```bash
# Redeploy previous version
railway deploy --commit <v1.2.2-commit-sha> --environment production

# Monitor deployment
railway logs -f --environment production

# Verify health
curl https://api.mantaassociados.com/health
```

#### Step 6: Post-Rollback Actions

```bash
# Notify team
# "Rollback to v1.2.2 completed. Investigating root cause of v1.2.3 issue."

# Create incident ticket
# Document what went wrong, what was reverted, what's next

# Analyze logs
# tail -n 1000 /var/log/codex-hub/app.log | grep ERROR
```

### Database Rollback Specifics

**Scenario: Destructive Migration Deployed**

```bash
# If migration deleted data:

# 1. Restore from backup
pg_restore -h <host> -U postgres -d codex_prod \
  /backups/postgres-backup-v1.2.2.dump

# 2. Verify data integrity
SELECT COUNT(*) FROM critical_tables;

# 3. Re-run code at v1.2.2
npm run start -- --version
# Expected: v1.2.2
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Application Won't Start

**Symptom:**
```
Error: Cannot find module '@modelcontextprotocol/sdk'
```

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Rebuild TypeScript
npm run build

# Start again
npm run start
```

#### 2. Database Connection Failed

**Symptom:**
```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solution:**
```bash
# Check PostgreSQL service
docker compose ps | grep postgres

# Restart PostgreSQL
docker compose restart supabase

# Verify connection string
echo $DATABASE_URL
# Must be: postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

#### 3. Redis Connection Error

**Symptom:**
```
Error: connect ECONNREFUSED 127.0.0.1:6379
```

**Solution:**
```bash
# Check Redis service
docker compose ps | grep redis

# Restart Redis
docker compose restart redis

# Test connection
redis-cli ping
# Expected: PONG

# Check logs
docker compose logs redis
```

#### 4. Out of Memory (OOM)

**Symptom:**
```
JavaScript heap out of memory
Fatal error: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

**Solution:**
```bash
# Increase Node heap size
export NODE_OPTIONS="--max-old-space-size=4096"
npm run start

# Or in docker-compose.yml:
# environment:
#   - NODE_OPTIONS=--max-old-space-size=4096

# Check current memory usage
docker stats codex-app

# Optimize: Profile memory leaks
npm run test:memory-profile
```

#### 5. Docker Compose Port Conflicts

**Symptom:**
```
Error: listen EADDRINUSE :::3000
```

**Solution:**
```bash
# Find what's using port 3000
lsof -i :3000
# or
netstat -tlnp | grep 3000

# Kill process (if it's old)
kill -9 <PID>

# Or use different port
docker compose up -p codex-test

# Or modify docker-compose.yml
# ports:
#   - "3001:3000"  # Map to 3001 instead
```

#### 6. Supabase Connection Issues

**Symptom:**
```
Error: Failed to authenticate with Supabase
401 Unauthorized
```

**Solution:**
```bash
# Verify credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY
echo $SUPABASE_SERVICE_ROLE

# Test connection directly
curl -H "apikey: $SUPABASE_KEY" \
  "$SUPABASE_URL/rest/v1/" \
  -v

# Check if using staging/production correctly
# SUPABASE_URL should match environment (staging vs prod)

# Regenerate keys if compromised
# https://supabase.com/docs/guides/api/managing-api-keys
```

#### 7. Anthropic API Key Invalid

**Symptom:**
```
Error: 401 Unauthorized - Invalid API key
```

**Solution:**
```bash
# Verify API key format
# Must start with: sk_

echo $ANTHROPIC_API_KEY | head -c 5
# Expected: sk_

# Check key hasn't expired
# https://console.anthropic.com -> Account -> API Keys

# Test directly
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

#### 8. TypeScript Compilation Error

**Symptom:**
```
error TS2688: Cannot find type definition file for 'node'
```

**Solution:**
```bash
# Install type definitions
npm install --save-dev @types/node

# Rebuild TypeScript
npm run type-check

# Full rebuild
rm -rf dist
npm run build
```

#### 9. Tests Failing in CI/CD

**Symptom:**
```
FAIL src/__tests__/agents.test.ts
● Test Suites: 1 failed, 0 passed, 1 total
```

**Solution:**
```bash
# Run tests locally in watch mode
npm run test:watch

# Run specific test
npm run test -- agents.test.ts

# Check test environment
echo $NODE_ENV  # Should be: test

# Increase test timeout
# In jest.config.js: testTimeout: 30000

# View test coverage
npm run test:coverage
```

#### 10. SSL/TLS Certificate Error (Production)

**Symptom:**
```
Error: Error: self signed certificate in certificate chain
```

**Solution:**
```bash
# For development (UNSAFE - dev only):
export NODE_TLS_REJECT_UNAUTHORIZED=0
npm run start

# For production - get proper certificate:
# Via Let's Encrypt (Railway handles this)
# Or upload to: Railway Dashboard > Settings > Certificates

# Verify certificate
openssl s_client -connect api.mantaassociados.com:443
```

### Debug Mode

Enable verbose logging:

```bash
# Set debug environment variables
export LOG_LEVEL=debug
export DEBUG=codex:*
export NODE_DEBUG=http,tls

# Start application
npm run dev

# Check logs
docker compose logs -f codex-app | grep ERROR
```

### Health Check Diagnostics

```bash
# Quick health check
curl -s http://localhost:3000/health | jq .

# Check specific services
curl -s http://localhost:3000/health/postgres | jq .
curl -s http://localhost:3000/health/redis | jq .
curl -s http://localhost:3000/health/supabase | jq .
curl -s http://localhost:3000/health/anthropic | jq .
```

### Performance Profiling

```bash
# CPU profiling
node --prof dist/index.js
node --prof-process isolate-*.log > profile.txt

# Memory profiling
node --inspect dist/index.js
# Then open: chrome://inspect

# Check slow endpoints
npm run test:performance
```

### Log Analysis

```bash
# View real-time logs
docker compose logs -f codex-app

# Search logs for errors
docker compose logs codex-app | grep ERROR

# Export logs for analysis
docker compose logs codex-app > logs-$(date +%Y%m%d-%H%M%S).txt

# Check specific service logs
docker compose logs supabase
docker compose logs redis
```

---

## Environment Variables Reference

### Full Environment Variables List

See `.env.example` for complete reference. Key variables by category:

#### Application Core
```bash
NODE_ENV=development|staging|production
PORT=3000
LOG_LEVEL=error|warn|info|debug|trace
```

#### Anthropic API
```bash
ANTHROPIC_API_KEY=sk_...
CLAUDE_MODEL=claude-opus-4-1|claude-sonnet-4|claude-haiku-4-5-20251001
CLAUDE_API_TIMEOUT_MS=60000
CLAUDE_MAX_TOKENS=4096
```

#### Supabase
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_ROLE=eyJ...
SUPABASE_TIMEOUT_MS=15000
```

#### GitHub
```bash
GITHUB_TOKEN=ghp_...
GITHUB_OWNER=manta-associados
GITHUB_REPO=Codex-exemplo
GITHUB_DEFAULT_BRANCH=main
```

#### Database
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10
```

#### Redis
```bash
REDIS_URL=redis://localhost:6379
REDIS_TIMEOUT_MS=5000
```

#### Microsoft Graph (Optional)
```bash
MS_GRAPH_TOKEN=eyJ...
MS_TENANT_ID=12345678-...
MS_APP_ID=87654321-...
MS_APP_SECRET=...
MS_GRAPH_TIMEOUT_MS=30000
```

#### Cache & Sync
```bash
CACHE_TTL_SECONDS=3600
SYNC_QUEUE_ENABLED=true
SYNC_INTERVAL_MS=60000
```

---

## Health Checks & Monitoring

### Built-in Health Endpoints

```bash
# Application health
GET /health
Response: {"status":"ok","timestamp":"2026-07-31T12:00:00Z"}

# Service health
GET /health/postgres
GET /health/redis
GET /health/supabase
GET /health/anthropic
Response: {"service":"postgres","status":"healthy","latency_ms":15}
```

### Monitoring Setup

#### Prometheus Metrics

Application exports OpenTelemetry metrics on `/metrics`:

```bash
# View metrics
curl http://localhost:3000/metrics

# Key metrics:
# - http_requests_total (by method, route, status)
# - http_request_duration_seconds (by route)
# - db_query_duration_seconds
# - redis_operation_duration_seconds
# - anthropic_api_calls_total
```

#### Logging

Structured logging with Pino:

```json
{
  "level": "info",
  "time": "2026-07-31T12:00:00.000Z",
  "pid": 1234,
  "hostname": "codex-app",
  "req": {
    "method": "POST",
    "url": "/agents/maestro/route",
    "headers": {},
    "remoteAddress": "127.0.0.1"
  },
  "res": {
    "statusCode": 200,
    "responseTime": "145.32ms"
  },
  "msg": "request completed"
}
```

#### Alerting Rules

Configure alerts for:

- [ ] HTTP error rate > 5%
- [ ] Response time > 1000ms (p99)
- [ ] Database connection pool exhausted
- [ ] Redis connection failed
- [ ] Anthropic API quota exceeded
- [ ] Disk usage > 80%
- [ ] Memory usage > 85%
- [ ] Process restart > 3 times/hour

---

## Additional Resources

- **Architecture**: See `ARCHITECTURE.md`
- **Contributing**: See `CONTRIBUTING.md`
- **CI/CD**: See `.github/workflows/`
- **API Reference**: See `/docs/API.md`
- **Runbooks**: See `/docs/RUNBOOKS/`
- **Monitoring**: See `/docs/MONITORING.md`
- **Railway Docs**: https://docs.railway.app
- **Supabase Docs**: https://supabase.com/docs
- **Docker Docs**: https://docs.docker.com

---

## Support & Escalation

**Issues & Questions:**
- GitHub Issues: https://github.com/manta-associados/Codex-exemplo/issues
- Slack: #engineering-deployment
- Email: eng@mantaassociados.com

**On-Call Rotation:**
- See `/docs/RUNBOOKS/on-call.md`
- Escalation: engineer@mantaassociados.com

**Incident Response:**
- See `/docs/RUNBOOKS/incident-response.md`
- Postmortem template: `/docs/RUNBOOKS/postmortem.md`

---

**Last Updated:** 2026-07-31  
**Next Review:** 2026-10-31
