# Portal Master Database Documentation

## Overview

Portal Master uses SQLAlchemy as the ORM (Object-Relational Mapping) layer and Alembic for database migrations. The database stores agent metadata, tool service information, synchronization events, and knowledge base documents.

## Database Architecture

### Configuration

- **Database**: SQLite (development) or PostgreSQL (production)
- **Location**: `./data/portal.db` (SQLite)
- **Configuration**: `alembic.ini` and `app/core/database.py`
- **Environment Variable**: `DATABASE_URL`

### Example Environment Setup

```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./data/portal.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/portal_master
```

## Tables and Models

### 1. **agents** — Agent Registry
Stores metadata for all 20 agents in the Manta Maestro system.

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key (e.g., "manta-00", "manta-03-s8") |
| name | String(255) | Display name |
| code | String(50) | Code identifier (e.g., "Manta 00") — UNIQUE |
| aliases | JSON | Alternative names |
| description | String(1000) | Description |
| eixo | Enum | Classification: Horizontal, Vertical, Lifecycle |
| tier | Enum | Model tier: Haiku, Sonnet, Opus, Haiku→Sonnet, Sonnet/Opus |
| status | Enum | Status: Operacional, Beta, Parcial, Inativo, Descontinuado |
| service_url | String(500) | URL to agent service |
| routing_keywords | JSON | Keywords for automatic routing |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| created_by | String(255) | User who created |
| updated_by | String(255) | User who last updated |

**Indexes**: code, status, eixo+status, eixo+tier, tier, name

### 2. **tool_services** — Tool Service Registry
Stores metadata for the 14 backend tool services.

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key (e.g., "balanço", "askcad") |
| name | String(255) | Service name |
| description | String(1000) | Description |
| version | String(50) | Service version |
| port | Integer | Service port — UNIQUE |
| base_url | String(500) | Service base URL |
| health_check_url | String(500) | Health check endpoint |
| status | Enum | Status: Healthy, Degraded, Offline, Maintenance, Unknown |
| last_health_check | DateTime | Last health check timestamp |
| health_check_interval_seconds | Integer | Health check interval |
| endpoints_json | JSON | Supported endpoints documentation |
| config_json | JSON | Service configuration |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| created_by | String(255) | Creator |
| updated_by | String(255) | Last updater |

**Indexes**: status, port, name

### 3. **sync_events** — Synchronization Event Log
Tracks all synchronization events between Portal Master and Manta Hub.

| Column | Type | Description |
|--------|------|-------------|
| id | String(100) | Primary key |
| event_type | Enum | Event type (AgentRegistered, ToolStatusChanged, etc.) |
| direction | Enum | Direction: Pull, Push, Bidirectional |
| status | Enum | Status: Pending, InProgress, Success, PartialSuccess, Failed |
| source | String(255) | Source system (e.g., "manta-hub") |
| source_system_id | String(255) | ID in source system |
| items_synced | Integer | Count of items synced |
| items_failed | Integer | Count of items failed |
| items_skipped | Integer | Count of items skipped |
| payload_json | JSON | The data that was synced |
| metadata_json | JSON | Additional context |
| error_message | Text | Error details if failed |
| result_json | JSON | Result details |
| timestamp | DateTime | Event timestamp |
| started_at | DateTime | When sync started |
| completed_at | DateTime | When sync completed |
| duration_seconds | Integer | Total duration |
| triggered_by | String(255) | User or system that triggered sync |
| correlation_id | String(100) | For tracking related syncs |
| created_at | DateTime | Record creation time |
| updated_at | DateTime | Record update time |

**Indexes**: timestamp, status, event_type, direction, source, correlation_id

### 4. **knowledge_documents** — Knowledge Base Documents
Stores documents for the RAG (Retrieval-Augmented Generation) system.

| Column | Type | Description |
|--------|------|-------------|
| id | String(100) | Primary key |
| title | String(500) | Document title |
| content | Text | Full document content |
| summary | String(1000) | Brief summary |
| category | Enum | Category: Agent Profile, Routing Rule, Documentation, etc. |
| eixo_tags | JSON | Associated eixos |
| agent_ids | JSON | Associated agent IDs |
| tags | JSON | Custom tags |
| source_url | String(1000) | Original source URL |
| source_repo | String(500) | Source repository |
| source_path | String(500) | Path in source repo |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |
| created_by | String(255) | Creator |
| updated_by | String(255) | Last updater |

**Relationships**: 
- One-to-Many with `knowledge_chunks` (cascade delete)
- One-to-Many with `external_sources` (cascade delete)

**Indexes**: category, created_at, source_url, title

### 5. **knowledge_chunks** — Document Chunks for Search
Chunked content from knowledge documents for efficient RAG retrieval.

| Column | Type | Description |
|--------|------|-------------|
| id | String(150) | Primary key (doc_id:chunk_index) |
| doc_id | String(100) | Foreign key to knowledge_documents |
| chunk_text | Text | Chunk content |
| chunk_index | Integer | Order in document |
| section_title | String(500) | Section or heading |
| embedding_vector | String(5000) | Placeholder for embedding |
| token_count | Integer | Token count in chunk |
| created_at | DateTime | Creation timestamp |

**Relationships**: Many-to-One with `knowledge_documents`

**Indexes**: doc_id, chunk_index, doc_id+created_at

### 6. **external_sources** — External Resource Links
Links to external resources associated with knowledge documents.

| Column | Type | Description |
|--------|------|-------------|
| id | String(150) | Primary key (doc_id:source_index) |
| doc_id | String(100) | Foreign key to knowledge_documents |
| url | String(2000) | Resource URL |
| title | String(500) | Resource title |
| source_type | Enum | Type: direct, snapshot, wayback |
| status | Enum | Status: live, snapshot, archived, error |
| snapshot_url | String(2000) | Web.Archive snapshot URL |
| last_checked_at | DateTime | Last health check |
| last_status_code | Integer | HTTP status code |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |

**Relationships**: Many-to-One with `knowledge_documents`

**Indexes**: doc_id, status, last_checked_at, doc_id+status

## Database Migrations

Portal Master uses Alembic for version control of the database schema.

### Migration Files

- **001_initial_schema.py** — Creates all base tables with indexes
- **002_add_knowledge_indexes.py** — Adds optimization indexes for RAG queries

### Running Migrations

```bash
# Check migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 002

# Downgrade one revision
alembic downgrade -1

# Create new migration (autogenerate)
alembic revision --autogenerate -m "description"

# Create blank migration
alembic revision -m "description"
```

### Migration Environment

The Alembic environment (`migrations/env.py`) is configured to:
1. Read `DATABASE_URL` from environment variables
2. Auto-detect model changes (when using `--autogenerate`)
3. Support both offline and online migrations
4. Use StaticPool for SQLite (single connection)
5. Use connection pooling for PostgreSQL

## Database Initialization

The database is automatically initialized on application startup via the `lifespan` context manager in `app/main.py`.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("Starting up Portal Master...")
    init_db()  # Creates tables if they don't exist
    yield
    logger.info("Shutting down Portal Master")
```

## ORM Models

All models are defined in `app/models/` and inherit from `Base`:

```python
from app.models import (
    Agent,
    ToolService,
    SyncEvent,
    KnowledgeDocument,
    KnowledgeChunk,
    ExternalSource,
)
```

### Example: Creating an Agent

```python
from app.core.database import SessionLocal
from app.models import Agent, AgentEixo, AgentTier, AgentStatus

session = SessionLocal()
agent = Agent(
    id="manta-08",
    name="Test Agent",
    code="Manta 08",
    eixo=AgentEixo.HORIZONTAL,
    tier=AgentTier.SONNET,
    status=AgentStatus.OPERACIONAL,
)
session.add(agent)
session.commit()
session.close()
```

### Example: Querying Agents

```python
from app.core.database import SessionLocal
from app.models import Agent, AgentStatus

session = SessionLocal()

# Get all operational agents
agents = session.query(Agent).filter(
    Agent.status == AgentStatus.OPERACIONAL
).all()

# Get agents by eixo
horizontal_agents = session.query(Agent).filter(
    Agent.eixo == AgentEixo.HORIZONTAL
).all()

session.close()
```

## Database Session Management

FastAPI dependency for getting database sessions:

```python
from fastapi import Depends
from app.db import get_db

@app.get("/agents")
async def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()
```

## Performance Considerations

1. **Indexes**: All frequently-queried columns have indexes
2. **Foreign Keys**: Enabled for SQLite via `PRAGMA foreign_keys=ON`
3. **Cascade Delete**: Knowledge documents cascade to chunks and sources
4. **Connection Pooling**: StaticPool for SQLite, with pool recycling for PostgreSQL
5. **JSON Indexing**: JSON columns can be indexed in PostgreSQL for enhanced search

## Backup and Maintenance

### SQLite Backup

```bash
# Simple file copy
cp ./data/portal.db ./data/portal.db.backup

# Using SQLite CLI
sqlite3 ./data/portal.db ".backup backup.db"
```

### Database Cleanup

```python
# Delete old sync events (older than 30 days)
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models import SyncEvent

session = SessionLocal()
old_date = datetime.now() - timedelta(days=30)
session.query(SyncEvent).filter(SyncEvent.timestamp < old_date).delete()
session.commit()
session.close()
```

## Testing

Run database tests:

```bash
# All database tests
pytest tests/test_database.py -v

# Specific test class
pytest tests/test_database.py::TestAgentModel -v

# With coverage
pytest tests/test_database.py --cov=app --cov-report=html
```

## Troubleshooting

### "unable to open database file"

**Solution**: Create the `data/` directory:
```bash
mkdir -p ./data
```

### "UNIQUE constraint failed"

**Solution**: Check for duplicate values before inserting:
```python
existing = session.query(Agent).filter(Agent.code == "DUPLICATE").first()
if existing:
    # Handle duplicate
```

### "no such table"

**Solution**: Run migrations:
```bash
alembic upgrade head
```

## Related Documentation

- **Models**: `app/models/` — ORM model definitions
- **Database Configuration**: `app/core/database.py` — Connection setup
- **Migrations**: `migrations/` — Alembic configuration
- **API Routes**: `app/routers/` — FastAPI endpoints using database
- **Tests**: `tests/test_database.py` — Comprehensive test suite
