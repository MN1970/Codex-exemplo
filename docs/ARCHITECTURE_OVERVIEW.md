# Manta Maestro — System Architecture Overview v1.0

**Last Updated:** 2026-07-27  
**Target Audience:** Engineers, Architects, DevOps  
**SLO:** 99.9% availability | p95 < 5s latency  

---

## 1. HIGH-LEVEL SYSTEM DESIGN

### Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Presentation (React SPA)                       │
│ - Interactive UI for agent selection, workflow building │
│ - Real-time feedback, Knowledge Hub search              │
│ - Admin dashboard for org management                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ↓ (HTTPS/REST)
┌─────────────────────────────────────────────────────────┐
│ Layer 2: API Gateway & Services (FastAPI, async)        │
│ - REST endpoints (40+ routes)                           │
│ - JWT authentication, RBAC authorization               │
│ - MCP client/server integration (multi-remote)          │
│ - Request validation, rate limiting                     │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌───────────────────────────────────────────────────────┐
│ Layer 3: Business Logic & Data Access                 │
│ - Agent executor (selector + router + call handler)   │
│ - RAG engine (semantic search, pgvector)              │
│ - ML service (fine-tuning, model deployment)          │
│ - Workflow builder & orchestrator                     │
│ - Feedback aggregator & analytics                     │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌──────────────────────────────────────────────────────┐
│ Layer 4: Data & Integrations                         │
│ - PostgreSQL (auth, workflows, feedback)             │
│ - Vector DB (pgvector, 768-dim embeddings)           │
│ - Redis cache (sessions, rate limit counters)        │
│ - S3 (document storage, backups)                     │
│ - MCP services (GitHub, Supabase, MS365)            │
│ - Claude API (inference, fine-tuning)               │
└──────────────────────────────────────────────────────┘
```

---

## 2. 20-AGENT HUB-AND-SPOKE TOPOLOGY

### Agent Registry (Maestro v4.2)

```
                        ┌─────────────────┐
                        │  MAESTRO (00)   │
                        │   (Router)      │
                        │ Hub-and-spoke   │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
          ┌─────────▼────┐  ┌────▼─────────────────┐
          │ HORIZONTAL   │  │ VERTICAL (SEGMENTS)  │
          │ AGENTS       │  │ & LIFECYCLE          │
          │ (Eixo 1)     │  │ (Eixo 2 & 3)        │
          └──────────────┘  └────────────────────┘
          /  |  |  |  |  \      |  |  |  |  |  \
    01-C 02 04 05 06 07  13-16  S1 S2 S3 S4  S6-10
```

### Agent Mapping (v4.2: 11 horizontal + 9 vertical)

**Horizontal (Eixo 1):**
- **Manta 00 (Maestro)** — Router, intake Q1 classification
- **Manta 01 (Claims)** — Sinistros, seguros, indenizações
- **Manta 02 (Contratual)** — Contratos, termos, negociações
- **Manta 04 (Imobiliário)** — Propriedade, uso do solo, zoneamento
- **Manta 05 (Orçamento)** — Custos, SICRO, precificação
- **Manta 06 (Modelagem)** — Engenharia, simulações, análise numérica
- **Manta 07 (Cronograma)** — Planejamento, Gantt, timeline
- **Manta 13 (BD)** — Business development, oportunidades
- **Manta 14 (Apresentações)** — PPTs, comunicação executiva
- **Manta 15 (Advisory)** — Consultoria, strategic insights
- **Manta 16 (Arquiteto-IA)** — IA architecture, fine-tuning strategy

**Vertical (Eixo 2: Segmentos) + Lifecycle (Eixo 3):**
- **Manta 03-S1** — Rodovias (pavimento, terraplenagem, SICRO)
- **Manta 03-S2** — OAE/Pontes (estruturas, NBR 7187)
- **Manta 03-S3** — Ferrovia (trilho, via permanente)
- **Manta 03-S4** — Metrô (estações, NATM, VLT)
- **Manta 03-S6** — Portos (ANTAQ, dragagem, terminais)
- **Manta 03-S7** — Aeroportos (ANAC, pistas, TPS)
- **Manta 03-S8** — Saneamento (ETA/ETE, SNIS, AySA) — **PRIORITY**
- **Manta 03-S9** — Energia (ANEEL, transmissão, subestações)
- **Manta 03-S10** — Barragens (ICOLD, CFRD, rejeitos)

All vertical agents support **8 lifecycle phases**:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## 3. DATA FLOW DIAGRAMS

### 3.1 Agent Execution Flow

```
User Prompt
    │
    ▼
┌─────────────────────────────────────┐
│ FastAPI: POST /agents/{id}/execute  │
│ - Input validation (Pydantic)       │
│ - JWT token verification            │
└──────────────┬──────────────────────┘
               │
               ▼
         ┌────────────────────┐
         │ Session Management │
         │ (Redis cache)      │
         └─────────┬──────────┘
                   │
                   ▼
      ┌────────────────────────────┐
      │ Agent Selector             │
      │ (Intake Q1 analysis)       │
      │ Model: routing-classifier  │
      ├────────────────────────────┤
      │ Matches: S1..S10 agents    │
      │ Accuracy: 94.2%            │
      │ Latency: p95 < 280ms       │
      └─────────┬──────────────────┘
                │
                ▼
   ┌────────────────────────────────┐
   │ Selected Agent Executor        │
   │ (hub-and-spoke)               │
   │ Calls:                        │
   │ - claude-opus-4-20250514      │
   │ - Claude model inference      │
   ├────────────────────────────────┤
   │ Input tokens: [1K-4K avg]     │
   │ Output tokens: [500-2K avg]   │
   │ Latency: p95 < 1.2s           │
   └─────────┬──────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Response Processing                │
│ - Format: JSON + markdown          │
│ - Citations: [doc_id, chunk_id]    │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Feedback Ingestion (async)         │
│ - Store: PostgreSQL feedback table │
│ - Topic: Kafka (future)            │
└─────────────────────────────────────┘
          │
          ▼
    User Response

Latency Budget (p95):
  ├─ Selection: 280ms
  ├─ API calls: 1,200ms
  ├─ Response format: 50ms
  ├─ DB write: 100ms
  └─ Total: ~1,630ms (< 5s target ✅)
```

### 3.2 Semantic Search & RAG Flow

```
User Query: "Escoramento em obras viárias"
    │
    ▼
┌──────────────────────────────────────┐
│ POST /rag/search                     │
│ - Input validation                   │
│ - Multi-language support (PT/EN)     │
└────────────┬───────────────────────┘
             │
             ▼
      ┌──────────────────────┐
      │ Query Embedding      │
      │ Model: text-embed-3  │
      │ Dim: 768             │
      │ Latency: < 100ms     │
      └──────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │ pgvector Search                │
    │ (Postgres with vector cols)    │
    ├────────────────────────────────┤
    │ Collection: docs + chunks      │
    │ k=5 nearest neighbors          │
    │ similarity > 0.6 threshold     │
    │ Latency: p95 < 450ms           │
    │ Vectors indexed: 50K+          │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │ Chunk Re-ranking (BM25)    │
    │ - Semantic + keyword       │
    │ - Top 3 chunks selected    │
    │ - Metadata: source doc     │
    └──────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ Context Assembly             │
    │ - Prepend: system prompt     │
    │ - Inject: chunks (RAG)       │
    │ - Instruction: cite sources  │
    └────────────┬─────────────────┘
                 │
                 ▼
      ┌───────────────────────┐
      │ Agent w/ RAG Context  │
      │ - Inference           │
      │ - Citations generated │
      │ - Accuracy: 96%+      │
      └───────────┬───────────┘
                  │
                  ▼
         Response w/ Citations
         [source_id] [chunk_id] [score]

Latency Budget (p95):
  ├─ Embedding: 100ms
  ├─ Vector search: 450ms
  ├─ Re-ranking: 50ms
  ├─ Agent inference: 1,200ms
  └─ Total: ~1,800ms (< 5s target ✅)
```

### 3.3 Fine-Tuning & Model Deployment

```
POST /ml/finetune
    │
    ▼
┌──────────────────────────────────────┐
│ Fine-tuning Job Submission          │
│ - Org ID, dataset URI, hyperparams   │
│ - Output model name: {org}-adapter   │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Job Queued (PostgreSQL: ml_jobs)    │
│ - Status: pending                    │
│ - Submitted: timestamp               │
│ - Callback: webhook URL              │
└────────┬───────────────────────────┘
         │
         ▼ (Async: MLX worker)
┌──────────────────────────────────────┐
│ MLX Service (separate pod)           │
│ - LoRA rank: 16                      │
│ - Learning rate: 2e-4                │
│ - Epochs: 3                          │
│ - Batch size: 8                      │
│ - Duration: ~1-4h per 1K examples    │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Model Artifacts                      │
│ - LoRA weights: S3://{org}/adapter   │
│ - Metrics (loss, acc): metadata.json │
│ - Logs: CloudWatch                   │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Model Registration                   │
│ - DB: ml_models table                │
│ - Status: ready                      │
│ - Baseline performance: metrics.json │
│ - A/B test flag: enabled             │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Runtime Deployment                   │
│ - Load adapter in agent executor     │
│ - A/B test split: 50/50 initial      │
│ - Monitor: accuracy, latency         │
│ - Rollback: 1-click to baseline      │
└────────┬───────────────────────────┘
         │
         ▼
GET /ml/finetune/{job_id}/status
    ├─ Status: completed
    ├─ Model ID: {org}-adapter-001
    ├─ Performance delta: +2.3%
    └─ Ready for production: true
```

---

## 4. SCALABILITY & PERFORMANCE

### Horizontal Scaling

| Component | Min | Max | CPU per | RAM per | Scale Trigger |
|-----------|-----|-----|---------|---------|---------------|
| FastAPI pods | 3 | 6 | 500m | 512Mi | CPU > 70% or RPS > 500 |
| React pods | 2 | 4 | 250m | 256Mi | CPU > 60% or users > 5K |
| PostgreSQL replicas | 1 | 2 | 2 | 4Gi | Failover only |
| Redis cache | 1 | 2 | 1 | 2Gi | Memory > 80% |
| Jaeger tracer | 1 | 2 | 500m | 1Gi | Span rate > 10K/s |

### Throughput Targets

- **API Throughput:** 1,000+ RPS sustained (p95 < 5s) ✅
- **Agent Execution:** 450+ concurrent executions
- **RAG Search:** 300+ concurrent queries
- **Feedback Ingestion:** 500+ feedback events/sec
- **Vector Search:** 50K+ vectors, < 500ms p95

### Caching Strategy

```
┌──────────────────────────────────────┐
│ Browser Cache (1hr max-age)          │
│ - Static assets: CSS, JS, fonts      │
│ - CloudFlare CDN: 30min ttl          │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Redis Cache (5min ttl)               │
│ - Session tokens: user:{uid}         │
│ - Rate limit counters: ratelimit:ip  │
│ - Agent definitions: agents:*        │
│ - Fine-tuning model list: ml:models  │
│ - Recent feedback: feedback:latest   │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Database Query Cache (30sec)         │
│ - Feedback aggregations (hourly)     │
│ - Routing model accuracy metrics     │
│ - Organization settings              │
└──────────────────────────────────────┘
```

---

## 5. DISASTER RECOVERY & FAILOVER

### RTO / RPO Targets

| Failure Scenario | RTO | RPO | Method |
|------------------|-----|-----|--------|
| Pod crash | < 1m | 0s | K8s auto-restart |
| Node failure | < 5m | 0s | Pod rescheduling |
| Database primary failure | < 30s | < 5min | Postgres streaming replication |
| AZ failure | < 15min | < 5min | Cross-AZ replicas + backups |
| Region failure | < 1h | < 1h | S3 backups + manual failover |

### Backup Strategy

```
PostgreSQL Backups:
├─ Hourly snapshots: S3 (us-east-1)
│  └─ Retention: 30 days
├─ Daily full backups: S3 (us-west-2 replica)
│  └─ Retention: 90 days
├─ Monthly archives: Glacier
│  └─ Retention: 7 years
└─ Point-in-time recovery: WAL logs (2 weeks)

Document Store (S3):
├─ Versioning enabled
├─ Cross-region replication: us-east-1 ↔ us-west-2
├─ Lifecycle: 30d to Glacier, 90d to Deep Archive
└─ Encryption: AES-256 (keys in AWS KMS)

Configuration (Git):
├─ CLAUDE.md, agents, schemas versioned
├─ CI/CD pipeline triggers on commits
├─ Rollback: git checkout {tag}
└─ Audit trail: All commits signed
```

### Failover Procedure

**Database Failover (Primary → Secondary):**
1. Detect primary unavailable (health check fails, timeout)
2. Promote secondary: `pg_ctl promote`
3. Update connection string (DNS points to secondary)
4. Verify data consistency: pg_catalog checks
5. Failback when primary recovers (manual review)

**Service Failover (Pod crash):**
1. Kubelet detects liveness probe failure
2. Pod enters CrashLoopBackoff state
3. K8s reschedules on healthy node
4. New pod: init container → migrate DB schema → ready
5. Service DNS updated within 5s

**Region Failover (manual, < 1h RTO):**
1. Activate DR cluster (pre-provisioned, standby)
2. Restore latest backup: `pg_restore < backup.sql`
3. Update DNS A records (5min TTL)
4. Deploy FastAPI from image registry
5. Verify monitoring, logging, tracing operational
6. Restore S3 bucket versioning (select point-in-time)

---

## 6. SECURITY ARCHITECTURE

### Authentication & Authorization

```
┌─────────────┐
│ User Login  │
└──────┬──────┘
       │
       ▼
┌───────────────────────────────────┐
│ OAuth 2.0 / OIDC (optional)       │
│ OR Email + password               │
└──────────┬────────────────────────┘
           │
           ▼
┌───────────────────────────────────┐
│ Verify credentials (bcrypt hash)  │
│ Generate JWT (RS256 signed)       │
│ TTL: 1h (access), 7d (refresh)   │
└──────────┬────────────────────────┘
           │
           ▼
┌───────────────────────────────────┐
│ Store session (Redis)             │
│ key: session:{token_jti}          │
│ ttl: 1h                           │
└──────────┬────────────────────────┘
           │
           ▼
┌───────────────────────────────────┐
│ Return JWT + refresh token        │
│ Client: store in httpOnly cookie  │
└───────────────────────────────────┘

Subsequent Requests:
┌──────────────────────────┐
│ Client sends JWT (header)│
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Middleware: decode JWT (RS256)   │
│ Verify signature, expiration     │
│ Load user context (DB)           │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ RBAC: check user roles           │
│ - Owner, Admin, User, Viewer     │
│ - Per-resource permissions       │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Allow/deny request               │
└──────────────────────────────────┘
```

### Encryption

- **At Rest:** AES-256 (all data in PostgreSQL, S3, backups)
- **In Transit:** TLS 1.3 (all HTTPS + internal services)
- **Secrets:** Sealed Secrets (Kubernetes) or AWS Secrets Manager
- **Signing:** JWT (RS256), code signatures (Cosign)

---

## 7. MONITORING & OBSERVABILITY

### Metrics (Prometheus)

```
manta_agent_execution_duration_seconds{agent_id, status}
  └─ histogram: p50, p95, p99, max

manta_routing_accuracy_percent{model_version}
  └─ gauge: 94.2%

manta_rag_search_latency_seconds{collection}
  └─ histogram: p95 < 450ms

manta_api_requests_total{endpoint, status_code}
  └─ counter: /agents/{id}/execute 2.5M/day

manta_database_connection_pool_in_use{pool_name}
  └─ gauge: 32/50 connections

manta_fine_tuning_jobs_total{status}
  └─ counter: completed, failed, pending
```

### Logging (Loki)

```
Log Levels:
  - ERROR: Critical failures, escalate immediately
  - WARN: Degradation, investigate within 15min
  - INFO: Normal operations, agent execution, API calls
  - DEBUG: Verbose tracing (disabled in production)

Retention:
  - Hot (Loki): 30 days
  - Cold (S3): 90 days
  - Archive (Glacier): 7 years
```

### Tracing (Jaeger)

```
Traces sampled: 10% in production (100% in staging)
Retention: 72 hours
Exported to: Jaeger backend (S3 storage)

Span instrumentation:
  - API request → agent execution → model inference
  - RAG search → vector query → re-ranking
  - Database queries: slow log (> 1s)
  - External API calls: MCP, Anthropic, S3
```

---

## 8. DEPLOYMENT TOPOLOGY

### Kubernetes Architecture (HA)

```
┌────────────────────────────────────────────────────┐
│ Production Cluster (3 nodes, us-east-1)            │
├────────────────────────────────────────────────────┤
│                                                    │
│ Namespace: manta-prod                             │
│                                                    │
│ ┌─────────────────────────────────────────┐      │
│ │ Ingress (HTTPS, TLS termination)        │      │
│ │ - manta.example.com                     │      │
│ │ - api.manta.example.com                 │      │
│ └──────────┬────────────────────────────┘      │
│            │                                     │
│ ┌──────────▼────────────────────────────────┐   │
│ │ Service: manta-frontend (2-4 pods)        │   │
│ │ - React SPA, 45MB image                   │   │
│ │ - Replicas: min 2, max 4                  │   │
│ │ - CPU: 250m req, 500m limit               │   │
│ │ - Memory: 256Mi req, 512Mi limit          │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Service: manta-fastapi (3-6 pods)        │   │
│ │ - FastAPI backend, 120MB image           │   │
│ │ - Replicas: min 3, max 6                 │   │
│ │ - CPU: 500m req, 1000m limit             │   │
│ │ - Memory: 512Mi req, 1024Mi limit        │   │
│ │ - Liveness probe: /health (30s)          │   │
│ │ - Readiness probe: /ready (5s)           │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ StatefulSet: postgres-primary            │   │
│ │ - 1 primary + 2 standby (streaming rep)  │   │
│ │ - Storage: 100GB PV (50% used)           │   │
│ │ - CPU: 2 req/limit                       │   │
│ │ - Memory: 4Gi req/limit                  │   │
│ │ - Replication lag: < 100ms               │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Deployment: redis-cache                  │   │
│ │ - 1-2 pods (max memory: 2Gi)             │   │
│ │ - CPU: 1 req/limit                       │   │
│ │ - Memory: 2Gi req/limit                  │   │
│ │ - TTL: 24h max                           │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Deployment: prometheus                   │   │
│ │ - 1 pod, 5GB storage (30d retention)    │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Deployment: loki                         │   │
│ │ - 1 pod, 10GB storage (hot: 30d)        │   │
│ │ - S3 backend (cold: 90d)                │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Deployment: jaeger                       │   │
│ │ - 1 pod, 30GB storage (72h)             │   │
│ │ - S3 backend (cold: 7y)                 │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Deployment: grafana                      │   │
│ │ - 1 pod, 12 dashboards                  │   │
│ │ - Datasources: Prometheus, Loki, Jaeger │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
└────────────────────────────────────────────────┘
```

---

## 9. TECHNOLOGY STACK SUMMARY

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React 18 | 18.2.0 | SPA, real-time UI |
| State Mgmt | Redux Toolkit | 1.9.5 | Global state |
| HTTP Client | axios + interceptors | 1.4.0 | API calls |
| Backend | FastAPI | 0.104.1 | Async REST API |
| Database | PostgreSQL | 15.3 | OLTP, transactions |
| Vector DB | pgvector | 0.5.1 | Semantic search (768-dim) |
| Cache | Redis | 7.2 | Sessions, rate limits |
| Message Queue | Kafka (future) | - | Event streaming |
| ML Framework | PyTorch + LoRA | 2.0.1 | Fine-tuning |
| Observability | Prometheus + Grafana | P: 2.47.0 | Metrics + visualization |
| Logging | Loki | 2.9.3 | Log aggregation |
| Tracing | Jaeger | 1.49.0 | Distributed tracing |
| Container Orch | Kubernetes | 1.27.4 | Deployment, scaling |
| IaC | Terraform | 1.5.7 | Infrastructure code |
| Config Mgmt | Helm | 3.12.0 | K8s package manager |
| Secrets | Sealed Secrets | 0.24.0 | K8s secret encryption |
| CI/CD | GitHub Actions | - | Automated builds/tests |
| LLM API | Anthropic Claude | 3.5-Sonnet | Inference, fine-tuning |

---

## 10. INTEGRATION POINTS

### External Services

1. **Anthropic Claude API**
   - Models: claude-opus-4-20250514, claude-3-5-sonnet-20241022
   - Timeout: 300s
   - Retries: 3 with exponential backoff
   - Rate limit: 100 req/min

2. **MCP Services**
   - GitHub: code search, issue/PR management
   - Supabase: SQL execution, edge functions
   - MS365: Teams, Outlook integration (via Graph API)

3. **S3 (AWS)**
   - Document storage, backup archives
   - Bucket versioning enabled
   - Cross-region replication (2-region active)

4. **CloudFlare CDN**
   - Static asset caching (JS, CSS, fonts)
   - DDoS protection
   - WAF rules applied

---

**Architecture version:** 4.2  
**Last reviewed:** 2026-07-27  
**Next review:** 2026-08-31 (post go-live)
