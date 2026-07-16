# Portal Knowledge — Manta Maestro v5.0

Central registry and knowledge base for the **ADK-5 Layer Architecture** — a unified platform for AI agent orchestration and domain expertise integration across 14 civil engineering tools and 20+ specialized agents.

## Quick Start

### Frontend (React 19 + Vite)
```bash
cd portal/frontend
npm install
npm run dev
# Serves at http://localhost:5173
```

### Backend (FastAPI)
```bash
cd portal/backend
python -m venv .venv
source .venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set JWT_SECRET, GITHUB_TOKEN, MANTA_HUB_API_URL
uvicorn app.main:app --reload --port 8000
# Serves at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Architecture

### ADK-5 Layer Model

**Layer 1: User Interface**
- React 19 SPA with Agent Registry, Tool Explorer, Sync Dashboard, Documentation

**Layer 2: Orchestration & Routing**
- Maestro router directing requests to appropriate agents
- Support for 20 specialized agents across 3 eixos (horizontal, vertical, lifecycle)

**Layer 3: Domain Expertise**
- Vertical agents (S1–S10): Infrastructure, Portos, Aeroportos, Saneamento, Energia, Barragens
- Each agent is a Claude specialized in a civil engineering domain

**Layer 4: Cross-Domain Services**
- Horizontal agents (Manta 00, 01, 02, 04–07, 13–16): Claims, Contracts, Budget, Schedule, Advisory, etc.

**Layer 5: Infrastructure**
- Portal Master (Codex-exemplo) — Master registry and API
- Manta Portal (:8016) — Integration layer with 14 tools and backend health checks
- Knowledge Base — SQLite with agent metadata, tool inventory, external source linkage

## File Structure

```
portal/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── styles/
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   ├── db/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── ADK5_ARCHITECTURE.md
│   ├── AGENT_ANATOMY.md
│   └── SYNC_PROTOCOL.md
└── scripts/
    ├── extract-maestro.py
    └── sync-metadata.py
```

## API Endpoints

### Health & Config
- `GET /api/health` — Service health status
- `GET /api/config` — Portal configuration and layer info

### Agents
- `GET /api/agents` — List all registered agents
- `GET /api/agents/{id}` — Get agent details
- `POST /api/agents` — Register new agent (admin only)

### Tools
- `GET /api/tools` — List all 14 manta-hub tools
- `GET /api/tools/{id}` — Get tool metadata
- `GET /api/tools/{id}/health` — Check tool health

### Synchronization
- `POST /api/sync/pull` — Pull agent metadata from Manta Hub
- `POST /api/sync/push` — Push portal metadata to Manta Hub

### Knowledge Base
- `GET /api/knowledge/agents` — Search agent knowledge
- `GET /api/knowledge/external-sources` — List external source linkage

## Key Features

✅ **Unified Agent Registry** — Single source of truth for all 20 agents  
✅ **5-Layer Visualization** — Interactive diagram of the architecture  
✅ **Tool Inventory** — Metadata for all 14 manta-hub tools  
✅ **External Source Linkage** — 3-layer fallback strategy (direct → snapshot → Wayback Machine)  
✅ **Real-Time Sync** — Bidirectional sync with Manta Hub backends  
✅ **Knowledge Base** — SQLite with full-text search and extraction history  

## Integration with Manta Hub

The Portal Master syncs bidirectionally with **Manta Hub** (:8016):

1. **Pull**: `POST /api/sync/pull` → fetches agent metadata from all 14 tools
2. **Push**: `POST /api/sync/push` → sends unified registry back to Manta Hub
3. **Health Checks**: Periodic polling of tool health endpoints
4. **Metadata Extraction**: Automatic discovery of tool capabilities, endpoints, and dependencies

## Development

### Testing
```bash
cd portal/backend
pytest tests/
```

### Database Migrations
```bash
cd portal/backend
alembic upgrade head
```

### Building for Production
```bash
cd portal/frontend
npm run build  # Creates dist/

cd portal/backend
pip install -r requirements.txt
```

## Documentation

- **ADK5_ARCHITECTURE.md** — Full specification of the 5-layer model
- **AGENT_ANATOMY.md** — Anatomy of an agent (system prompt, tools, capabilities)
- **SYNC_PROTOCOL.md** — Bidirectional sync protocol with Manta Hub
- **EXTERNAL_SOURCES.md** — Source linkage strategy and disclaimer

See `docs/` for detailed guides.

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd portal/backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd portal/frontend && npm run dev

# Browser
open http://localhost:5173
```

### Production
- **Frontend**: Deploy to Vercel or static hosting (Vite build)
- **Backend**: Deploy to Heroku, Railway, or Docker container
- **Database**: Use PostgreSQL or managed SQLite (Turso)

See `deploy/` for Docker and nginx configs.

## Support & Issues

- **Setup Issues**: See START_HERE.txt and SETUP_ADK5_ARCHITECTURE.md
- **Development Questions**: Open an issue in the GitHub repo
- **Blockers**: Slack channel #portal-adk5-blockers

## Timeline

- **MVP (v0.1.0)**: 3–5 days (frontend + backend stubs + basic sync)
- **Feature Complete (v0.2.0)**: +1 week (all endpoints, full search, real-time dashboard)
- **Production Ready (v1.0.0)**: +2 weeks (performance, security audit, DevOps)

## Release

- **v0.1.0-portal-adk5** → Initial MVP with 5-layer visualization and basic agent registry
- Target: End of week (2026-07-19)

---

**Built for Manta Associados | ADK-5 Layer Architecture | 2026**
