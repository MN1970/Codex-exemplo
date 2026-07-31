# ARCHITECTURE.md — Codex Exemplo

**Version:** 1.0.0  
**Last Updated:** 2026-07-31  
**Status:** Reference Implementation  

---

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Data Flows](#data-flows)
4. [State Management](#state-management)
5. [Tools & Resources](#tools--resources)
6. [Deployment Architecture](#deployment-architecture)
7. [Integration Patterns](#integration-patterns)

---

## Overview

Codex Exemplo is a distributed MCP (Model Context Protocol) agent system designed to support multi-tenant document processing, workflow orchestration, and collaborative knowledge management. The architecture follows a layered design with explicit separation of concerns:

- **MCP Server Layer** → Protocol handling, agent lifecycle
- **Adapter Layer** → Transport abstraction (HTTP, gRPC, local IPC)
- **State Manager** → CRDT-based distributed state
- **Resource Layer** → Typed tools and resources (URIs)
- **Deployment Layer** → Local, staging, and production environments

### Key Principles

- **Stateless agents** + **centralized state** = resilience
- **Event-driven flows** reduce latency and coupling
- **CRDT light** enables eventual consistency without consensus
- **9 canonical URIs** organize all resources
- **16 typed tools** with explicit contracts

---

## Components

### 1. MCP Server (Agent Host)

**Responsibility:** Protocol handling, agent instantiation, lifecycle management

```
┌─────────────────────────────────────────────────────┐
│             MCP Server (Agent Host)                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Protocol Handler (Claude API ↔ Agent Logic) │  │
│  │ • Request/response serialization             │  │
│  │ • Error handling & retries                   │  │
│  │ • Session context propagation                │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Agent Lifecycle Manager                      │  │
│  │ • Bootstrap (load CLAUDE.md, skills)         │  │
│  │ • Turn execution (prompt → tool calls)       │  │
│  │ • Graceful shutdown & cleanup                │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Context Manager                              │  │
│  │ • Session storage (RAM + disk)               │  │
│  │ • Conversation history pruning               │  │
│  │ • Token budgeting & overflow handling        │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Key Operations:**

- `bootstrap()` → load agent config, initialize context
- `executeTurn(prompt)` → run single LLM turn, handle tool calls
- `publishContext()` → push session state to State Manager
- `shutdown(graceful=true)` → flush buffers, close connections

---

### 2. Adapter Layer (Transport Abstraction)

**Responsibility:** Translate between MCP Server and external systems

```
┌────────────────────────────────────────────────────────┐
│              Adapter Layer                             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ HTTP Adapter │  │ gRPC Adapter │  │  IPC Link  │  │
│  │ (REST API)   │  │  (low-lat.)  │  │ (local)    │  │
│  │              │  │              │  │            │  │
│  │ • POST /turn │  │ AgentSvc.    │  │ Unix socket│  │
│  │ • GET /ctx   │  │ ExecuteTurn  │  │ or named   │  │
│  │ • WebSocket  │  │ ListTools    │  │ pipe       │  │
│  │   /stream    │  │              │  │            │  │
│  └──────────────┘  └──────────────┘  └────────────┘  │
│        ▲                  ▲                  ▲        │
│        │ JSON             │ Protobuf         │        │
│        │ (content-agnostic)                 │        │
└────────────────────────────────────────────────────────┘
         ▼              ▼              ▼
    HTTP Clients   Integrations  Local Workers
    (Claude API,   (Supabase,    (Claude Code
    Apps)          GitHub)       local dev)
```

**Adapters:**

| Adapter | Transport | Latency | Throughput | Use Case |
|---------|-----------|---------|------------|----------|
| HTTP | REST/WebSocket | ~100ms | Med | External clients, SaaS integrations |
| gRPC | HTTP/2 | ~10ms | High | Inter-service, low-latency flows |
| IPC | Unix socket | <1ms | Very high | Local development, same-host agents |

---

### 3. State Manager (CRDT Light)

**Responsibility:** Distributed state replication, conflict resolution

```
┌──────────────────────────────────────────────────────────┐
│           State Manager (CRDT Light)                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Supabase Realtime (Primary Store)                  │ │
│  │ • tables: sessions, turns, artifacts, context      │ │
│  │ • RLS policies per agent / user                    │ │
│  │ • logical clocks (lamport timestamps)              │ │
│  │ • presence: active_agents (live cursors)           │ │
│  └────────────────────────────────────────────────────┘ │
│                 ▲                           │           │
│                 │ (replication)             │           │
│  ┌──────────────┴───────┬──────────────────┴──────────┐ │
│  │                      │                             │ │
│  ▼                      ▼                             ▼ │
│ ┌────────────┐   ┌────────────┐   ┌──────────────┐   │
│ │Local Cache │   │   Staging  │   │Prod Fallback │   │
│ │(Redis)     │   │  (Supabase │   │(S3, Archive) │   │
│ │            │   │  backup)   │   │              │   │
│ └────────────┘   └────────────┘   └──────────────┘   │
│                                                       │
└──────────────────────────────────────────────────────────┘
```

**CRDT Light Strategy:**

- **Vectors clocks** per agent turn (lamport timestamp + agent ID)
- **Last-write-wins** for primitive fields (timestamps break ties)
- **Append-only logs** for events (immutable, ordered)
- **Snapshot tables** for computed state (sessions, contexts)
- **Conflict resolution** via `merge_policy` in schema

---

## Data Flows

Five canonical data flows organize all agent interactions:

### Flow 1: READ (Context Acquisition)

```
Agent                   State Manager              Resource Layer
  │                          │                           │
  ├─ queryContext()──────────┼──> [lookup session]       │
  │                          │    [fetch artifacts]      │
  │  <─ [context blob]───────┤                           │
  │                          │                           │
  ├─────────────────────────────────────────> readTool()─┤
  │                                           [s3://, db://]
  │  <─────────────────────────────────────── [result]   │
  │
  └─ Execution begins
```

**Sequence:**

1. Agent calls `publishContext()` (previous turn)
2. Agent requests `queryContext()` at turn start
3. State Manager fetches from Supabase + local cache
4. Agent loads resources via Tool URIs (9 prefixes)
5. Context delivered to LLM tokenizer

**Latency SLA:** <100ms (cached), <500ms (cold)

---

### Flow 2: WRITE (State Persistence)

```
Agent                   State Manager              Storage
  │                          │                       │
  ├─ emit(turnResult)────────┤                       │
  │  ├─ artifact_id          │                       │
  │  ├─ turn_count           │ [validate schema]     │
  │  ├─ tool_calls[]         │ [check RLS]           │
  │  └─ exit_reason          │                       │
  │                          ├─ insert/update───────>│
  │                          │  [turns table]        │
  │                          │                       │
  │                          ├─ upsert───────────────>│
  │                          │  [contexts table]     │
  │                          │                       │
  │  <─ write_ack────────────┤                       │
  │                          │  <─ [tx_id]──────────┤
  │
  └─ Proceed to next turn (or shutdown)
```

**Sequence:**

1. Agent collects `turnResult` (all artifacts, state changes)
2. Calls `emit(turnResult)` with schema validation
3. State Manager opens transaction (`Supabase.tx()`)
4. RLS policies checked for agent + user
5. Inserts/updates in `turns`, `artifacts`, `contexts`
6. Returns `tx_id` for idempotency
7. Async replication to staging/prod backups

**Latency SLA:** <200ms (local), <1s (prod)

---

### Flow 3: NOTIFY (Event Propagation)

```
Agent                   State Manager         WebSocket / Pub/Sub
  │                          │                           │
  ├─ onArtifactChange()──────┤                           │
  │  ├─ artifact_id: "art_"   │ [broadcast payload]─────>│ [subscription]
  │  ├─ change_type: "update" │                          │ client_id=foo
  │  ├─ delta: {...}          │                          │
  │  └─ timestamp              │ [presence update]──────>│ active_agents[]
  │                          │                          │
  │  <─ (async ack)───────────┤ <─ [event_id]──────────┤
  │                          │
  └─ Continue execution
```

**Sequence:**

1. Agent detects artifact change (tool output, LLM response)
2. Calls `onArtifactChange(artifact_id, delta)` (fire-and-forget)
3. State Manager serializes event (JSON)
4. Broadcast to Supabase Realtime subscribers
5. All listening clients receive update instantly
6. Update presence (active agents, who edited what)

**Latency SLA:** <50ms (same datacenter), <200ms (geo)

---

### Flow 4: SYNC (Multi-Agent Coordination)

```
Agent A              State Manager        Agent B
  │                        │                 │
  ├─ requestLock(res_x)────┼────────────────>│
  │                        │   [lock granted]│
  │                        │                 │
  ├─ executeOnResource(x)──┼────────────────>│
  │                        │   [queued]      │
  │                        │                 │
  │  <─ [polling] ─────────┤                 │
  │     lock_status?       │   [waiting]     │
  │                        │                 │
  │  <─ [lock_released]────┼────────────────>│ [now A done]
  │                        │   [execute]     │
  │                        │                 │
  │                        │   [write]──────>│
  │                        │   [unlock]──────┤
  │                        │   [notify A]←───┤
  │  <─ [completion]───────┼────────────────┘
  │
  └─ Resume local execution
```

**Sequence:**

1. Agent A acquires distributed lock (Supabase `pg_advisory_lock`)
2. Agent B waits (polls or listens on Realtime channel)
3. Agent A completes operation, releases lock
4. State Manager notifies waiting agents
5. Agent B acquires lock, executes
6. Both emit completion events (Flow 3)

**Latency SLA:** <500ms (3 agents), scales O(n)

---

### Flow 5: CONTEXT (Session State Propagation)

```
User Input       MCP Server         State Manager        Resource Layer
  │                 │                      │                    │
  ├─ [prompt] ─────>│                      │                    │
  │                 │                      │                    │
  │                 ├─ loadContext() ──────┼───> [fetch sessions]│
  │                 │                      │    [fetch artifacts]
  │                 │  <──── [merged context] ──────────────────┤
  │                 │                      │                    │
  │                 ├─ [prompt + context]──────────────────────>│
  │                 │   [to LLM]           │                    │
  │                 │                      │                    │
  │                 │  <─ [LLM response]───────────────────────┤
  │                 │                      │                    │
  │                 ├─ emit(turn_result)──>│                    │
  │                 │                      ├─ [persist]────────>│
  │                 │                      │                    │
  │  <─ [response] ──┤                      │                    │
  │                 │  <─ [ack]────────────┤                    │
  │                 │
  └─ Turn complete
```

**Sequence:**

1. User sends prompt
2. MCP Server calls `loadContext()` (pulls from State Manager)
3. Context merged with prompt (token budget applied)
4. Sent to LLM with full tool manifest
5. LLM generates response + tool calls
6. Agent emits `turnResult` (Flow 2)
7. State Manager persists, returns ack
8. Response delivered to user

**Latency SLA:** <500ms total (user → response)

---

## State Management

### CRDT Light Model

Codex uses a **simplified CRDT** approach tailored to agent workloads:

#### 1. Data Model

```yaml
# Session (MV-register: last-write-wins)
sessions:
  id: "ses_"
  agent_id: "manta_00" | "manta_03_s1" | ...
  user_id: "user_"
  created_at: <timestamp>
  context: <json> # merged snapshot
  state: "active" | "paused" | "closed"
  lamport_clock: <int> # vector clock per agent
  
# Turns (append-only log)
turns:
  id: "turn_"
  session_id: "ses_"
  turn_num: <int>
  prompt: <string>
  response: <string>
  tool_calls: <json[]>
  artifacts_touched: <uri[]>
  timestamp: <int> # lamport clock
  agent_id: "manta_"
  tx_id: <uuid> # for idempotency
  
# Artifacts (MV-register with delta)
artifacts:
  id: "art_"
  session_id: "ses_"
  uri: "doc://", "dag://", etc.
  content_type: "markdown" | "json" | "binary"
  body: <blob>
  version: <int>
  lamport_clock: <int>
  merge_policy: "last-write-wins" | "append-log" | "custom"
  
# Contexts (computed snapshot)
contexts:
  id: "ctx_"
  session_id: "ses_"
  agents_active: <set> # presence
  artifacts_in_scope: <uri[]>
  latest_turn: <int>
  token_count: <int>
  merged_at: <timestamp>
```

#### 2. Conflict Resolution

| Field | Strategy | Tiebreaker |
|-------|----------|-----------|
| `context.*` (primitives) | Last-write-wins | Lamport timestamp |
| `artifacts.body` | Last-write-wins | Lamport + agent_id |
| `turns[]` | Append-only | Turn number |
| `artifacts.tags[]` | Union-based | all tags preserved |

**Example:** Agent A and Agent B update `session.state` simultaneously:
```
A: state="paused"  @ lamport=42, agent_id="manta_00"
B: state="active"  @ lamport=42, agent_id="manta_03_s1"

Winner: B (agent_id > lexicographically)
```

#### 3. Consistency Guarantees

- **Read-after-write:** Agent A's write propagates to cache <10ms
- **Causal consistency:** Lamport clocks ensure event ordering per agent
- **Eventual consistency:** All replicas converge within RTO (5s prod)
- **Conflict-free:** LWW + append-only = no manual resolution needed

---

### Storage Topology

```
┌─────────────────────────────────────────────────────────┐
│ Supabase (Primary State)                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│ │ sessions     │  │ turns        │  │ artifacts    │  │
│ │ RLS: agent   │  │ RLS: agent   │  │ RLS: user    │  │
│ │              │  │              │  │              │  │
│ │ id PK        │  │ id PK        │  │ id PK        │  │
│ │ agent_id FK  │  │ session_id FK│  │ session_id FK│  │
│ │ (idx)        │  │ (idx)        │  │ (idx)        │  │
│ └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│ Realtime triggers:                                      │
│ • on_artifact_change → broadcast                       │
│ • on_lock_release → notify waiters                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲                      │
         │                      │
    [warm cache]          [replication job]
         │                      │
    ┌────┴─────────┬────────────┴─────────┐
    ▼              ▼                       ▼
┌─────────┐  ┌──────────┐  ┌──────────────────┐
│ Redis   │  │ Staging  │  │ S3 Archive       │
│ (1-hr   │  │ (Supabase│  │ (Glacier, 30d)  │
│ TTL)    │  │ backup)  │  │                  │
└─────────┘  └──────────┘  └──────────────────┘
   LOCAL       STAGING         PRODUCTION
```

---

## Tools & Resources

### 9 Canonical URIs

All resources are addressed by **9 URI prefixes**, enabling routing and caching:

| Prefix | Scheme | Storage | Latency | Use Case |
|--------|--------|---------|---------|----------|
| `doc://` | Document | Supabase (blob) + S3 | ~100ms | Markdown, PDFs, text artifacts |
| `dag://` | DAG (artifact) | Supabase (JSON) + Redis | ~10ms | Multi-version document graphs |
| `db://` | Database | Supabase (table) | ~50ms | Structured data (RAG, schemas) |
| `api://` | External API | HTTP adapter | ~100ms | Supabase, GitHub, SharePoint |
| `cache://` | In-process cache | RAM | <1ms | Session context, computed fields |
| `file://` | File system | Local disk | ~5ms | Temp artifacts, logs (dev only) |
| `sp://` | SharePoint | SP adapter | ~200ms | Enterprise content, O365 |
| `ai://` | Agent result | Supabase | ~50ms | Previous agent outputs, chains |
| `config://` | Configuration | CLAUDE.md, env | ~1ms | Agent routing, skill registry |

#### URI Examples

```
doc://manta-00/context-2026-07-31.md
dag://manta-03-s1/architecture#v4
db://san:editais/bndes-2024
api://github/repos/anthropic/claude-code/pulls/42
cache://session-ses_abc123/artifacts
file:///tmp/claude-0/...scratchpad.../report.pdf
sp://sites/manta/lists/proyectos/items/1
ai://manta-06/output-2026-07-31T14:32:00Z
config://CLAUDE.md#routing-rules
```

---

### 16 Core Tools

Tools are organized into 4 families:

#### Family A: Context Management (4 tools)

| Tool | Input | Output | Flow |
|------|-------|--------|------|
| `readContext` | `session_id`, `scope` | `{agents, artifacts, turns}` | READ |
| `writeContext` | `session_id`, `delta` | `{tx_id, version}` | WRITE |
| `queryArtifacts` | `session_id`, `uri_prefix`, `filter` | `artifact[]` | READ |
| `subscribeContext` | `session_id`, `channels[]` | `{subscribe_id}` | NOTIFY |

#### Family B: Artifact Management (4 tools)

| Tool | Input | Output | Flow |
|------|-------|--------|------|
| `createArtifact` | `type`, `body`, `metadata` | `{uri, id, version}` | WRITE |
| `updateArtifact` | `uri`, `delta`, `merge_policy` | `{version, conflicts?}` | WRITE |
| `readArtifact` | `uri`, `version?` | `{body, metadata, history}` | READ |
| `deleteArtifact` | `uri`, `reason` | `{archived_id}` | WRITE |

#### Family C: Synchronization (4 tools)

| Tool | Input | Output | Flow |
|------|-------|--------|------|
| `acquireLock` | `resource_uri`, `timeout_ms`, `agent_id` | `{lock_id, until}` | SYNC |
| `releaseLock` | `lock_id` | `{released}` | SYNC |
| `broadcastEvent` | `channel`, `payload`, `ttl` | `{event_id}` | NOTIFY |
| `waitForEvent` | `channel`, `timeout_ms` | `{event, timestamp}` | SYNC |

#### Family D: Resource Access (4 tools)

| Tool | Input | Output | Flow |
|------|-------|--------|------|
| `readResource` | `uri`, `format?` | `{body, metadata, etag}` | READ |
| `writeResource` | `uri`, `body`, `format` | `{uri, etag, size}` | WRITE |
| `listResources` | `uri_prefix`, `limit`, `offset` | `{items[], has_more}` | READ |
| `resolveUri` | `uri_pattern`, `context` | `{uri, candidates[]}` | READ |

---

## Deployment Architecture

### Three-Tier Topology

```
┌──────────────────────────────────────────────────────────────┐
│                         Production                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ MCP Server (Kubernetes, 3 replicas)                    │ │
│  │ • Load balancer (round-robin)                          │ │
│  │ • Session affinity for agent continuity               │ │
│  │ • Auto-scaling (CPU, turns/sec)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┴─────────────────────────────┐   │
│  │ Supabase (Prod): Primary state, RLS strict          │   │
│  │ • Read replicas: 2 (geo-distributed)                │   │
│  │ • Connection pooling (PgBouncer, 100 conns)         │   │
│  │ • Backups: hourly → S3 Glacier                       │   │
│  │ • Failover: automated (5min RTO)                     │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────┴─────────────────────────────┐   │
│  │ Redis (Prod): Warm cache, locks, presence            │   │
│  │ • Redis Cluster: 6 nodes                             │   │
│  │ • Replication: 2:1 (master:slave)                    │   │
│  │ • TTL: 1hr (session context)                         │   │
│  │ • Sentinel: auto-failover                            │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────┴─────────────────────────────┐   │
│  │ S3 Archive (Prod): Long-term storage                  │   │
│  │ • Glacier Deep Archive (7yr retention)               │   │
│  │ • Versioning + lifecycle policies                    │   │
│  │ • Encryption at rest (KMS)                           │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                         Staging                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ MCP Server (1-2)     │  │ Supabase (Staging)           │ │
│  │ • Manual scaling     │  │ • Backup from prod           │ │
│  │ • Debug logging      │  │ • Purge weekly               │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ Redis (local)        │  │ S3 (staging bucket)          │ │
│  │ • Single node        │  │ • Versioning only            │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                         Local (Dev)                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ MCP Server (Docker)  │  │ Supabase (Local stack)       │ │
│  │ • Host process       │  │ • PostgreSQL 15 (docker)     │ │
│  │ • Single agent       │  │ • pgAdmin on 5050             │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ Redis (docker)       │  │ File system                  │ │
│  │ • Single instance    │  │ • /tmp/claude-0/.../         │ │
│  │ • Persistent vol     │  │ • Local artifacts + logs     │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Deployment Profiles

#### Local (Development)

```yaml
# .claude/config/local.env
CODEX_ENV=local
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<local-stub>
REDIS_URL=redis://localhost:6379
S3_ENDPOINT=http://localhost:9000  # MinIO
ADAPTER=ipc                        # Unix socket
LOG_LEVEL=debug
```

**Startup:**
```bash
supabase start
docker run -d redis:latest
npm run dev:mcp-server
```

---

#### Staging (QA / Integration)

```yaml
# .claude/config/staging.env
CODEX_ENV=staging
SUPABASE_URL=https://staging-db.supabase.co
SUPABASE_ANON_KEY=<staging-key>
REDIS_URL=redis://staging-redis.internal:6379
S3_ENDPOINT=https://s3-staging.amazonaws.com
S3_BUCKET=codex-staging
ADAPTER=http                     # REST API
LOG_LEVEL=info
RATE_LIMIT=100req/min            # per agent
```

**Deployment:**
```bash
git push origin staging
# → GitHub Actions CI/CD
# → Deploy to k8s staging cluster
# → Smoke tests (5min)
```

---

#### Production

```yaml
# .claude/config/production.env
CODEX_ENV=production
SUPABASE_URL=https://prod-db.supabase.co
SUPABASE_ANON_KEY=<prod-key>
REDIS_URL=redis-cluster.internal:6379  # Cluster
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=codex-prod
ADAPTER=grpc                     # Low-latency
LOG_LEVEL=warn
RATE_LIMIT=1000req/min           # per agent
TLS_CERT=/etc/secrets/tls.crt
TLS_KEY=/etc/secrets/tls.key
```

**Deployment:**
```bash
# Manual gate required
git tag v1.x.y
git push origin v1.x.y
# → GitHub Actions: build + push ECR
# → Manual approval in ArgoCD
# → Blue-green deploy (k8s, 10min)
# → Canary (5% traffic) → 50% → 100%
```

---

### HA & Failover

#### Failure Scenarios

| Scenario | RTO | Recovery |
|----------|-----|----------|
| Single MCP Server | <10s | Load balancer → healthy replica |
| Supabase primary | 5min | Automatic failover to replica |
| Redis master | <30s | Sentinel → new master election |
| Network partition | 30s | Circuit breaker → cached state |
| Data corruption | 1hr | S3 restore from backup |

#### Health Checks

```
MCP Server (every 5s):
  GET /health
  → {status, uptime, turns_count, memory_mb}
  
State Manager (every 10s):
  SELECT 1 FROM pg_stat_database
  → {connections, xact_commit, latency}
  
Cache (every 3s):
  PING
  → {latency_ms, memory_usage}
```

---

## Integration Patterns

### Pattern 1: Agent-to-Supabase (RLS)

**Use:** Secure multi-tenant reads/writes

```javascript
// MCP Server
const { data, error } = await supabase
  .from('artifacts')
  .select('*')
  .eq('session_id', sessionId)
  .eq('agent_id', agentId)
  // RLS policy: (auth.uid() = user_id) AND (agent_id IN user_agents)
  
// → Supabase RLS enforces policy before returning rows
// → No manual permission checks needed
```

---

### Pattern 2: Broadcast-Subscribe (Realtime)

**Use:** Multi-agent coordination, live updates

```javascript
// Agent A (Publisher)
const channel = supabase
  .channel(`artifact:${artifactId}`)
  .on('broadcast', { event: 'update' },
    payload => { /* ... */ })
  .subscribe();

// Emit change
channel.send({
  type: 'broadcast',
  event: 'update',
  payload: { delta: {...}, version: 42 }
});

// Agent B (Subscriber) receives instantly
```

---

### Pattern 3: Distributed Lock (Pg Advisory)

**Use:** Exclusive resource access

```sql
-- MCP Server
BEGIN TRANSACTION;
SELECT pg_advisory_lock(hashtext('resource_uri'));
-- critical section
UPDATE artifacts SET body = ... WHERE id = ...;
SELECT pg_advisory_unlock(hashtext('resource_uri'));
COMMIT;
```

---

### Pattern 4: CRDT Merge (Last-Write-Wins)

**Use:** Conflict-free concurrent updates

```javascript
// Agent A @ t=100, lamport=10
{ state: 'active', version: 1, lamport: 10, agent_id: 'manta_00' }

// Agent B @ t=101, lamport=10
{ state: 'paused', version: 1, lamport: 10, agent_id: 'manta_03' }

// Merge logic (Supabase trigger)
IF NEW.lamport > OLD.lamport THEN
  RETURN NEW;  -- A's update
ELSIF NEW.lamport = OLD.lamport AND NEW.agent_id > OLD.agent_id THEN
  RETURN NEW;  -- B wins (lex order)
ELSE
  RETURN OLD;
END IF;
```

---

### Pattern 5: Context Versioning (DAG)

**Use:** Restore previous agent states

```yaml
# Artifact with versioning DAG
dag://manta-00/context

v3 (current)
├─ v2 (parent)
│  ├─ v1 (parent)
│  └─ v1_alt (sibling fork)
└─ v3_experimental (branch)

# Read specific version
readArtifact('dag://manta-00/context#v2')
```

---

## Configuration & Policies

### CLAUDE.md Integration

```markdown
# CLAUDE.md

agents:
  - id: manta-00
    tier: Haiku → Sonnet
    max_turns: 50
    context_window: 100k
    skills:
      - maestro
      - manta-context
      - manta-maestro
```

**Routing via maestro:**
- Reads `CLAUDE.md#routing-rules`
- Matches user prompt against regexes
- Routes to correct agent (S1–S10)
- Passes context via Flow 5

### Rate Limiting & Quotas

```
Per-agent (production):
  turns/min: 100
  context_tokens/hr: 1M
  artifact_writes/day: 10k
  
Per-user:
  concurrent_sessions: 3
  artifacts_total: 1000
  
Per-turn:
  max_tool_calls: 20
  max_context_size: 200k tokens
```

---

## Monitoring & Observability

### Metrics (Prometheus)

```
codex_turn_duration_ms          # histogram
codex_state_write_latency_ms    # gauge
codex_context_merge_time_ms     # histogram
codex_artifact_count_total      # counter
codex_lock_wait_time_ms         # gauge
codex_cache_hit_ratio           # gauge
```

### Logs (JSON, sent to CloudWatch)

```json
{
  "timestamp": "2026-07-31T14:30:45Z",
  "level": "INFO",
  "agent_id": "manta_03_s1",
  "session_id": "ses_abc123",
  "event": "turn_complete",
  "turn_num": 5,
  "tool_calls": 3,
  "duration_ms": 234,
  "artifacts_touched": ["dag://...", "doc://..."],
  "trace_id": "12345"
}
```

### Alarms

| Condition | Threshold | Action |
|-----------|-----------|--------|
| P99 latency (turn) | >5s | PagerDuty |
| Cache miss ratio | >20% | Warning |
| Lock contention | >10 waiters | Auto-scale |
| Artifact count | >10M | Archive to S3 |
| Supabase CPU | >80% | Scale replicas |

---

## References

- **MCP Spec:** https://modelcontextprotocol.io
- **Supabase Realtime:** https://supabase.com/docs/guides/realtime
- **CRDT Papers:** Shapiro et al. "A comprehensive study of CRDT" (2011)
- **Lamport Clocks:** Lamport, L. "Time, Clocks, and the Ordering of Events in a Distributed System" (1978)
- **Eventual Consistency:** Vogels, W. "Eventually Consistent" (2008)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-31 | Initial release: 5 flows, CRDT light, 16 tools, 3-tier deployment |

---

**Document Owner:** Codex Architecture Board  
**Last Reviewed:** 2026-07-31  
**Next Review:** 2026-10-31
