# Agent Management Backend Implementation

## Overview

This document describes the complete Agent management backend implementation for the Manta Maestro (Agent Registry) v4.2.

## Files Created

### 1. Core Database Setup
- **`app/core/database.py`** - SQLAlchemy engine configuration and session management
  - SQLite support with foreign key constraints
  - SessionLocal for database sessions
  - `get_db()` dependency for FastAPI routes
  - `init_db()` for table initialization

### 2. ORM Model
- **`app/models/agent.py`** - SQLAlchemy Agent model
  - Fields: id, name, code, aliases (JSON), tier, status, eixo, description, service_url, routing_keywords
  - Enums: `AgentStatus`, `AgentTier`, `AgentEixo`
  - Indexes for common queries (eixo, status, tier)
  - `to_dict()` method for serialization

### 3. Pydantic Schemas
- **`app/schemas/agent.py`** - Request/response validation
  - `AgentCreate` - for POST requests
  - `AgentUpdate` - for PATCH requests (partial updates)
  - `AgentResponse` - for successful responses
  - `AgentListResponse` - for paginated list responses
  - `AgentDetailResponse` - for single agent detail
  - `ErrorResponse` - for error responses

### 4. Database Operations
- **`app/db/agent.py`** - CRUD and query functions
  - `get_agent_by_id()` - Retrieve agent by ID
  - `get_agent_by_code()` - Retrieve agent by code
  - `get_agents()` - List with filtering and pagination
  - `create_agent()` - Create new agent with validation
  - `update_agent()` - Partial updates
  - `delete_agent()` - Soft delete (archive)
  - `hard_delete_agent()` - Permanent deletion
  - `list_agents_by_eixo()` - Filter by eixo
  - `list_agents_by_status()` - Filter by status
  - `search_agents()` - Full-text search by name/code
  - `get_agent_count()` - Total agent count

### 5. FastAPI Router
- **`app/routers/agents.py`** - REST API endpoints
  - `GET /api/agents` - List all agents with filters and pagination
  - `GET /api/agents/{agent_id}` - Get single agent
  - `POST /api/agents` - Create new agent
  - `PATCH /api/agents/{agent_id}` - Update agent
  - `DELETE /api/agents/{agent_id}` - Archive agent
  - `GET /api/agents/search/by-eixo/{eixo}` - Filter by eixo
  - `GET /api/agents/search/by-status/{status}` - Filter by status

### 6. Database Migrations
- **`alembic.ini`** - Alembic configuration
- **`migrations/env.py`** - Alembic environment setup
- **`migrations/script.py.mako`** - Migration template
- **`migrations/versions/001_initial_create_agents_table.py`** - Initial migration for agents table

### 7. Seed Script
- **`scripts/seed_agents.py`** - Load 20 agents from CLAUDE.md v4.2
  - All Manta 00 horizontal agents
  - All Manta 03-S1 to S10 vertical agents
  - Usage: `python scripts/seed_agents.py` or `python scripts/seed_agents.py --reset`

### 8. Unit Tests
- **`tests/test_agents_router.py`** - 35+ test cases covering:
  - List endpoint (empty, with data, pagination, filtering)
  - Detail endpoint (success, not found)
  - Create endpoint (success, duplicates, validation)
  - Update endpoint (success, partial, not found)
  - Delete endpoint (success, not found)
  - Search endpoints (by eixo, by status)

## API Endpoints

### List Agents
```bash
GET /api/agents?limit=100&offset=0&eixo=Horizontal&status=Operacional&tier=Sonnet&search=maestro
```

Query Parameters:
- `limit`: Pagination limit (1-500, default: 100)
- `offset`: Pagination offset (default: 0)
- `eixo`: Filter by eixo (Horizontal, Vertical, Lifecycle)
- `status`: Filter by status (Operacional, Beta, Parcial, Inativo, Descontinuado)
- `tier`: Filter by tier (Haiku, Sonnet, Opus, Haiku→Sonnet, Sonnet/Opus)
- `search`: Search by name or code

Response:
```json
{
  "agents": [
    {
      "id": "manta-00",
      "name": "maestro (router)",
      "code": "Manta 00",
      "aliases": ["maestro", "manta-router"],
      "description": "Roteador central...",
      "eixo": "Horizontal",
      "tier": "Haiku→Sonnet",
      "status": "Operacional",
      "service_url": null,
      "routing_keywords": [],
      "created_at": "2026-07-16T...",
      "updated_at": "2026-07-16T...",
      "created_by": "seed-script",
      "updated_by": null
    }
  ],
  "total": 20,
  "limit": 100,
  "offset": 0,
  "filters": {...}
}
```

### Get Single Agent
```bash
GET /api/agents/manta-00
```

### Create Agent
```bash
POST /api/agents
Content-Type: application/json

{
  "id": "manta-new",
  "name": "New Agent",
  "code": "Manta NEW",
  "aliases": ["new", "agent"],
  "description": "A new agent",
  "eixo": "Horizontal",
  "tier": "Sonnet",
  "status": "Operacional",
  "service_url": "http://localhost:8001",
  "routing_keywords": ["new", "test"],
  "created_by": "user@example.com"
}
```

### Update Agent
```bash
PATCH /api/agents/manta-00
Content-Type: application/json

{
  "name": "Updated maestro",
  "status": "Beta",
  "updated_by": "user@example.com"
}
```

### Delete Agent (Soft Delete)
```bash
DELETE /api/agents/manta-00
```

### Search by Eixo
```bash
GET /api/agents/search/by-eixo/horizontal
```

### Search by Status
```bash
GET /api/agents/search/by-status/operacional
```

## Data Model

### Agent Fields
- **id** (string, PK): Unique identifier (e.g., "manta-00")
- **name** (string): Human-readable name
- **code** (string, UNIQUE): Agent code (e.g., "Manta 00")
- **aliases** (JSON array): Alternative names
- **description** (string, optional): Agent description
- **eixo** (enum): Classification (Horizontal, Vertical, Lifecycle)
- **tier** (enum): Model tier (Haiku, Sonnet, Opus, etc.)
- **status** (enum): Status (Operacional, Beta, Parcial, Inativo, Descontinuado)
- **service_url** (string, optional): URL to service/documentation
- **routing_keywords** (JSON array): Keywords for automatic routing
- **created_at** (datetime): Creation timestamp
- **updated_at** (datetime): Last update timestamp
- **created_by** (string, optional): Creator username
- **updated_by** (string, optional): Last updater username

### Enums

**AgentStatus:**
- Operacional (✅)
- Beta
- Parcial (⚡)
- Inativo
- Descontinuado

**AgentTier:**
- Haiku
- Sonnet
- Opus
- Haiku→Sonnet
- Sonnet/Opus

**AgentEixo:**
- Horizontal (transversal agents)
- Vertical (segment-specific agents)
- Lifecycle (phase-specific agents)

## Database Schema

```sql
CREATE TABLE agents (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) NOT NULL UNIQUE,
  aliases JSON DEFAULT '[]',
  description VARCHAR(1000),
  eixo VARCHAR(50) NOT NULL,
  tier VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'Operacional',
  service_url VARCHAR(500),
  routing_keywords JSON DEFAULT '[]',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(255),
  updated_by VARCHAR(255)
);

CREATE INDEX idx_agent_eixo_status ON agents(eixo, status);
CREATE INDEX idx_agent_eixo_tier ON agents(eixo, tier);
CREATE INDEX idx_agent_status ON agents(status);
CREATE INDEX idx_agent_tier ON agents(tier);
```

## Usage

### Installation
```bash
cd portal/backend
pip install -r requirements.txt
```

### Initialize Database
```bash
python scripts/seed_agents.py
```

### Reset and Reseed
```bash
python scripts/seed_agents.py --reset
```

### Run Tests
```bash
pytest tests/test_agents_router.py -v
```

### Run Server
```bash
cd portal/backend
python -m uvicorn app.main:app --reload --port 8000
```

### Access API
- Health check: http://localhost:8000/api/health
- Agents list: http://localhost:8000/api/agents
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Initial 20 Agents (from CLAUDE.md v4.2)

### Eixo 1 - Horizontais (11 agents)
1. Manta 00 - maestro (router)
2. Manta 01 - claims
3. Manta 02 - contratual
4. Manta 04 - imobiliario
5. Manta 05 - orcamento
6. Manta 06 - modelagem
7. Manta 07 - cronograma
8. Manta 13 - bd (business-dev)
9. Manta 14 - apresentacoes
10. Manta 15 - advisory
11. Manta 16 - arquiteto-ia

### Eixo 2 - Verticais por Segmento (9 agents)
1. Manta 03-S1 - agente-infraestrutura (Rodovias)
2. Manta 03-S2 - agente-infraestrutura (OAE)
3. Manta 03-S3 - agente-infraestrutura (Ferrovia)
4. Manta 03-S4 - agente-infraestrutura (Metrô)
5. Manta 03-S6 - agente-portos
6. Manta 03-S7 - agente-aeroportos
7. Manta 03-S8 - agente-saneamento (PRIORIDADE AySA)
8. Manta 03-S9 - agente-energia (ANEEL/State Grid)
9. Manta 03-S10 - agente-barragens

## Error Codes

- **200 OK** - Successful GET
- **201 Created** - Successful POST
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Invalid request format
- **404 Not Found** - Agent not found
- **409 Conflict** - Duplicate ID or code
- **422 Unprocessable Entity** - Validation error (invalid enum value, etc.)
- **500 Internal Server Error** - Server error

## Integration Notes

1. The agent router is automatically included in `app.main:app`
2. Database is initialized on startup via `init_db()` in main.py
3. All endpoints use dependency injection for database sessions
4. All timestamps are automatically managed (created_at, updated_at)
5. Soft deletes are used by default (status set to INATIVO)
6. Search is case-insensitive (using SQL ILIKE)
7. Pagination is unlimited by default but max 500 items per request

## Future Enhancements

1. Add service health checks for service_url
2. Implement agent availability/uptime tracking
3. Add agent performance metrics
4. Implement agent versioning
5. Add audit logging for all changes
6. Implement agent tagging/categorization
7. Add API key authentication for service calls
8. Implement role-based access control (RBAC)
9. Add webhook notifications for agent changes
10. Implement agent dependency graph
