# Docker Development Setup Guide

Complete guide for setting up and managing the Manta Maestro development environment using Docker Compose.

## Quick Start

### One-Command Setup

```bash
# Clone/navigate to project root and run:
./scripts/setup-dev.sh
```

This single command will:
1. Validate Docker installation
2. Copy `.env.example` → `.env`
3. Build all Docker images
4. Start services (`docker-compose up -d`)
5. Initialize PostgreSQL database
6. Run Alembic migrations
7. Seed test data (10 agents, 100 RAG chunks)
8. Wait for all services to be healthy
9. Print access URLs

**Estimated time:** 2-5 minutes (first run may be slower due to image building)

### Post-Setup Access

Once setup completes, access your environment at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend (React)** | http://localhost:5173 | Main UI (Vite dev server, hot-reload) |
| **Backend API** | http://localhost:8000 | FastAPI with OpenAPI docs |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API documentation |
| **Health Check** | http://localhost:8000/admin/health | Backend health status |
| **PostgreSQL** | localhost:5432 | Database (user: `manta`, password: `mantadev`) |
| **Redis** | localhost:6379 | Cache & sessions |

---

## Services Overview

### Stack Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Frontend   │  │   Backend    │  │   Redis      │      │
│  │  (React/    │  │  (FastAPI)   │  │  (Cache)     │      │
│  │  Vite)      │  │  :8000       │  │  :6379       │      │
│  │  :5173      │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                            │                                 │
│                    ┌───────▼──────────┐                     │
│                    │   PostgreSQL     │                     │
│                    │   (pgvector)     │                     │
│                    │   :5432          │                     │
│                    └──────────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
        docker network: manta-network (172.28.0.0/16)
```

### Service Details

#### Frontend (React + Vite)

**Container:** `manta-frontend`  
**Port:** 5173  
**Type:** Node.js development server  
**Hot-Reload:** Yes (HMR enabled)

Features:
- Vite dev server with instant HMR (Hot Module Replacement)
- Mounted source code for live editing
- Excluded `node_modules` for performance
- Resource limits: 1 CPU, 512 MB RAM

**Configuration:**
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_AUTH_ENABLED=true
```

#### Backend (FastAPI)

**Container:** `manta-backend`  
**Port:** 8000  
**Type:** Python async (uvicorn)  
**Hot-Reload:** Yes (uvicorn --reload)

Features:
- Uvicorn ASGI server with auto-reload on code changes
- 2 worker processes (configurable via `API_WORKERS`)
- Health check endpoint (`/admin/health`)
- OpenAPI documentation (`/docs`, `/redoc`)
- SQLAlchemy ORM with Alembic migrations
- pgvector integration for RAG embeddings
- MCP integration (GitHub, Supabase, Microsoft 365)
- Claude API integration for agent execution

**Configuration:**
```env
DATABASE_URL=postgresql://manta:mantadev@db:5432/manta
CLAUDE_API_KEY=sk-...  # Required for agent features
JWT_ALGORITHM=RS256
```

**Resource Limits:** 1.5 CPU, 1 GB RAM

#### PostgreSQL 15 + pgvector

**Container:** `manta-postgres`  
**Port:** 5432  
**Type:** Relational database with vector extension

Features:
- pgvector extension pre-installed
- Automatic schema initialization via `init.sql`
- Data persistence via Docker volume (`manta-db-data`)
- Health check enabled
- Query logging (statements > 1 second logged)

**Credentials:**
```
User:     manta
Password: mantadev (dev only; change in production!)
Database: manta
```

**Resource Limits:** 2 CPU, 2 GB RAM (suitable for development)

**Persistence:** Data is stored in `manta-db-data` Docker volume (survives container restarts)

#### Redis

**Container:** `manta-redis`  
**Port:** 6379  
**Type:** In-memory cache/session store

Features:
- LRU eviction policy (256 MB max)
- Persistence enabled (RDB snapshots)
- Used for:
  - Session storage (TTL: 24 hours)
  - Caching (TTL: 1 hour)
  - Rate limiting
  - Job queue (future)

**Resource Limits:** 0.5 CPU, 512 MB RAM

---

## Common Tasks

### View Logs

View all service logs in real-time:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f frontend
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100

# Since specific time
docker-compose logs --since=30m
```

### Rebuild Images

Rebuild one or all images:

```bash
# Rebuild all images
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

### Reset Database

**Warning:** This will delete all data in PostgreSQL.

```bash
# Full reset (drop DB, recreate, run migrations, seed)
./scripts/setup-dev.sh --reset-db

# Manual reset
docker-compose exec db psql -U manta -d postgres -c "DROP DATABASE manta WITH (FORCE);"
docker-compose exec db psql -U manta -d postgres -c "CREATE DATABASE manta;"
docker-compose exec backend alembic upgrade head
```

### Run Database Migrations

After creating new migration files in `manta-backend/alembic/versions/`:

```bash
# Apply pending migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new_column to users"
```

### Execute Shell Commands in Container

Run arbitrary commands inside a service:

```bash
# Backend shell
docker-compose exec backend bash
docker-compose exec backend python -c "import os; print(os.environ)"

# Database shell
docker-compose exec db psql -U manta -d manta
docker-compose exec db pg_dump -U manta manta > backup.sql

# Frontend shell (Node)
docker-compose exec frontend bash
docker-compose exec frontend npm list
docker-compose exec frontend node --version

# Redis CLI
docker-compose exec redis redis-cli
  > PING
  > KEYS *
  > FLUSHDB
```

### Run Tests

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v
docker-compose exec backend pytest tests/ -k "test_health" -v
docker-compose exec backend pytest tests/ --cov

# Frontend tests
docker-compose exec frontend npm test
docker-compose exec frontend npm run test:watch
docker-compose exec frontend npm run test:ui
```

### Run Linting & Formatting

```bash
# Backend
docker-compose exec backend python -m pylint app/ routers/
docker-compose exec backend python -m black . --check

# Frontend
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run lint:fix
docker-compose exec frontend npm run format
```

### Stop Services

```bash
# Stop all (containers continue to exist)
docker-compose stop

# Stop and remove containers (volumes are preserved)
docker-compose down

# Stop, remove containers AND remove volumes (⚠️ data loss!)
docker-compose down -v
```

### Clean Up Everything

```bash
# Remove stopped containers, dangling images, unused networks
docker system prune

# More aggressive (removes all unused images)
docker system prune -a

# With volumes (⚠️ data loss!)
docker system prune -a --volumes
```

---

## Troubleshooting

### Port Already in Use

If you see "Address already in use" errors:

```bash
# Find process using the port (e.g., 8000)
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
# Then rebuild: docker-compose build --no-cache
```

### Database Connection Timeout

If backend can't connect to PostgreSQL:

```bash
# Check if DB container is running
docker-compose ps db

# Check DB logs
docker-compose logs db

# Wait longer for DB startup
docker-compose restart db
sleep 10
docker-compose restart backend

# Test connection directly
docker-compose exec db pg_isready -U manta -d manta
```

### Frontend Not Updating on File Changes (HMR Issue)

If you edit React code but the browser doesn't hot-reload:

1. Check the browser console for WebSocket errors
2. Verify HMR configuration in `.env`:
   ```env
   VITE_HMR_HOST=localhost
   VITE_HMR_PORT=5173
   VITE_HMR_PROTOCOL=ws
   ```
3. Check the Vite dev server logs:
   ```bash
   docker-compose logs -f frontend | grep -i "hmr\|websocket"
   ```
4. Hard refresh the browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
5. Restart the frontend container:
   ```bash
   docker-compose restart frontend
   ```

### Backend Hot-Reload Not Working

If Python code changes don't trigger reload:

1. Verify `--reload` flag in docker-compose.yml:
   ```yaml
   command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload --reload-dirs /app
   ```
2. Check reload logs:
   ```bash
   docker-compose logs -f backend | grep -i "reload\|changes"
   ```
3. Rebuild from source:
   ```bash
   docker-compose build --no-cache backend
   docker-compose up -d backend
   ```
4. Manually restart:
   ```bash
   docker-compose restart backend
   ```

### Services Won't Start (Exit Code 1)

1. Check container logs:
   ```bash
   docker-compose logs backend
   docker-compose logs db
   ```

2. Common issues:
   - **Missing `.env` file:** Run `cp .env.example .env`
   - **Python dependency conflict:** `docker-compose build --no-cache backend`
   - **Node module issues:** `docker-compose exec frontend npm ci`
   - **Database locked:** `docker-compose down -v && docker-compose up -d`

3. Rebuild from scratch:
   ```bash
   docker-compose down -v
   ./scripts/setup-dev.sh
   ```

### Memory/CPU Errors

If containers are killed or slow:

1. Check Docker resource limits:
   ```bash
   docker stats
   ```

2. Increase Docker Desktop memory allocation:
   - Windows/Mac: Docker Desktop → Preferences → Resources
   - Linux: Check system memory: `free -h`

3. Reduce resource limits in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M  # Reduce from 1G
   ```

### Can't Connect to Localhost Services from Other Machines

Docker services are bound to `localhost` (127.0.0.1) by default:

```yaml
# In docker-compose.yml
ports:
  - "127.0.0.1:8000:8000"  # localhost only (default)
  - "8000:8000"              # all interfaces (accessible from network)
```

To allow external access, edit `docker-compose.yml` and remove the `127.0.0.1:` prefix:
```yaml
ports:
  - "8000:8000"  # Now accessible from other machines
```

Then replace service hostnames:
```bash
# From other machine:
curl http://<YOUR_MACHINE_IP>:8000/admin/health
```

### Alembic Migration Conflicts

If you have conflicting migration files:

```bash
# View migration history
docker-compose exec backend alembic history

# Roll back to a specific revision
docker-compose exec backend alembic downgrade <revision>

# Resolve merge conflicts (if branches exist)
docker-compose exec backend alembic merge -m "merge head revisions"
docker-compose exec backend alembic upgrade head
```

---

## Performance Tuning

### Optimize Database Performance

```bash
# Analyze table sizes and indexes
docker-compose exec db psql -U manta -d manta -c "
  SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Vacuum and analyze
docker-compose exec db psql -U manta -d manta -c "VACUUM ANALYZE;"

# Check slow queries
docker-compose logs db | grep "duration:"
```

### Optimize RAM Usage

Edit `docker-compose.yml` resource limits:

```yaml
# Backend (default: 1G)
backend:
  deploy:
    resources:
      limits:
        memory: 512M  # Reduce for low-memory systems

# Database (default: 2G)
db:
  deploy:
    resources:
      limits:
        memory: 1G  # PostgreSQL works fine with 1G for dev

# Frontend (default: 512M)
frontend:
  deploy:
    resources:
      limits:
        memory: 256M
```

Then restart services:
```bash
docker-compose down
docker-compose up -d
```

### Enable Query Logging

See slow queries in PostgreSQL logs:

```bash
# Edit environment in docker-compose.yml
db:
  environment:
    POSTGRES_INITDB_ARGS: >
      -c log_statement=all
      -c log_min_duration_statement=500  # Log queries > 500ms
```

Then view logs:
```bash
docker-compose logs db | grep "duration:"
```

### Cache Redis Data

Configure Redis for better cache performance:

```bash
# Check Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Monitor cache hits/misses
docker-compose exec redis redis-cli INFO stats

# Clear cache if needed
docker-compose exec redis redis-cli FLUSHDB
```

### Disable Hot-Reload in Production Simulation

For testing production-like performance:

```bash
# Edit docker-compose.yml
backend:
  command: uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Without `--reload`, performance is closer to production.

---

## Environment Configuration

### Customize `.env` File

Key variables for local development:

```env
# Backend API
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
API_WORKERS=2

# Database
DATABASE_URL=postgresql://manta:mantadev@db:5432/manta

# Frontend
VITE_API_URL=http://localhost:8000
VITE_AUTH_ENABLED=true

# Optional: Claude API for agents
CLAUDE_API_KEY=sk-...

# Optional: GitHub MCP integration
GITHUB_MCP_TOKEN=ghp_...
```

After changing `.env`, restart affected services:

```bash
docker-compose up -d backend  # if backend variables changed
docker-compose up -d frontend # if frontend variables changed
```

---

## Advanced: Custom Docker Build Arguments

Build with custom arguments:

```bash
# Build with specific Python version
docker-compose build --build-arg PYTHON_VERSION=3.12 backend

# Build with build-time secrets (for private pip repos)
docker-compose build --secret github_token backend
```

Add to `docker-compose.yml`:
```yaml
backend:
  build:
    context: ./manta-backend
    secrets:
      - github_token
```

---

## Maintenance

### Regular Cleanup

```bash
# Weekly: Remove dangling images
docker image prune -f

# Monthly: Full system cleanup (be careful!)
docker system prune -a --volumes -f
```

### Backup Database

```bash
# Backup to file
docker-compose exec -T db pg_dump -U manta manta > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T db psql -U manta manta < backup_20260726.sql
```

### Monitor Resources

```bash
# Real-time stats
docker stats

# Historical stats (if you have a monitoring tool)
docker logs manta-backend --since 1h
```

---

## Getting Help

If you encounter issues:

1. **Check logs:** `docker-compose logs -f <service>`
2. **Search documentation:** See docs/ directory
3. **Review `.env`:** Ensure all required variables are set
4. **Restart services:** `docker-compose restart`
5. **Full reset:** `./scripts/setup-dev.sh --reset-db`

For persistent issues, provide:
```bash
# Save diagnostic info
docker-compose ps
docker-compose logs > diagnostic.log
docker version
docker-compose version
```

---

## Next Steps

1. **Customize `.env`:** Add your API keys (Claude, GitHub, etc.)
2. **Review services:** Visit http://localhost:8000/docs
3. **Start developing:** Edit files in `manta-backend/` or `manta-frontend/`
4. **Run tests:** `docker-compose exec backend pytest tests/`
5. **Read code:** See `manta-backend/README.md` and `manta-frontend/README.md`

Happy coding!
