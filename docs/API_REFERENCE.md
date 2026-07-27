# Manta Maestro — API Reference v1.0

**Base URL:** `https://api.manta.example.com`  
**OpenAPI Docs:** `https://api.manta.example.com/docs`  
**Auth:** JWT (Bearer token in Authorization header)  

---

## Authentication

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "organization_name": "Manta Associados",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "user_id": "usr_abc123",
  "email": "user@example.com",
  "organization_id": "org_xyz789",
  "token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 3600
}
```

**Errors:**
- 400: Invalid email format, weak password, org name too short
- 409: Email already registered

---

### POST /auth/login

Authenticate and receive JWT access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "mfa_code": "123456"  // Optional if MFA enabled
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "roles": ["user", "admin"],
    "organization_id": "org_xyz789"
  }
}
```

**Errors:**
- 401: Invalid credentials
- 403: MFA code required or invalid

---

### POST /auth/refresh

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "expires_in": 3600
}
```

**Errors:**
- 401: Refresh token expired or invalid

---

### GET /auth/profile

Get authenticated user profile.

**Headers:**
```
Authorization: Bearer eyJhbGc...
```

**Response (200):**
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization_id": "org_xyz789",
  "roles": ["user"],
  "mfa_enabled": true,
  "created_at": "2026-07-01T10:00:00Z",
  "last_login": "2026-07-27T14:30:00Z"
}
```

---

## Agents

### GET /agents

List all available agents (with filtering by segment).

**Query Parameters:**
- `segment`: S1, S2, S3, S4, S6, S7, S8, S9, S10 (optional)
- `tag`: "horizontal", "vertical" (optional)
- `limit`: 10-100 (default: 20)
- `offset`: pagination offset

**Response (200):**
```json
{
  "agents": [
    {
      "id": "agent_s1_rodovia",
      "name": "Infraestrutura — Rodovias",
      "segment": "S1",
      "description": "Agente especializado em projetos rodoviários",
      "tier": "sonnet",
      "endpoint": "/agents/agent_s1_rodovia/execute",
      "capabilities": ["project-analysis", "cost-estimation", "schedule-planning"]
    },
    {
      "id": "agent_portos",
      "name": "Infraestrutura — Portos",
      "segment": "S6",
      "description": "Especialista em projetos portuários",
      "tier": "opus",
      "endpoint": "/agents/agent_portos/execute",
      "capabilities": ["maritime-engineering", "regulatory-compliance"]
    }
  ],
  "total": 20,
  "limit": 20,
  "offset": 0
}
```

---

### POST /agents/{agent_id}/execute

Execute a prompt against a specific agent.

**Path Parameters:**
- `agent_id`: Agent ID (e.g., `agent_s1_rodovia`)

**Headers:**
```
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

**Request:**
```json
{
  "prompt": "Qual é o orçamento estimado para terraplenagem em rodovia de 50km?",
  "context": {
    "project_type": "highway",
    "region": "south",
    "LoRA_adapter": "org_xyz789-adapter-001"  // Optional
  },
  "temperature": 0.7,
  "max_tokens": 2000,
  "include_citations": true
}
```

**Response (200):**
```json
{
  "request_id": "req_xyz123",
  "agent_id": "agent_s1_rodovia",
  "response": "O orçamento estimado para terraplenagem em rodovia de 50km, considerando...",
  "citations": [
    {
      "source": "SICRO-2024-Terraplenagem",
      "chunk_id": "chunk_456",
      "relevance_score": 0.92,
      "text": "Preços unitários para terraplenagem..."
    }
  ],
  "metadata": {
    "model_used": "claude-3-5-sonnet-20241022",
    "tokens_used": { "input": 1523, "output": 487 },
    "latency_ms": 1245,
    "routing_confidence": 0.94
  }
}
```

**Errors:**
- 400: Invalid prompt, missing required context
- 401: Unauthorized (missing/invalid token)
- 429: Rate limit exceeded (100 req/min per user)
- 503: Agent service unavailable

---

### GET /agents/{agent_id}/history

Get execution history for an agent.

**Query Parameters:**
- `limit`: 10-100 (default: 20)
- `offset`: pagination
- `start_date`: ISO 8601 timestamp (optional)
- `end_date`: ISO 8601 timestamp (optional)

**Response (200):**
```json
{
  "history": [
    {
      "request_id": "req_xyz123",
      "agent_id": "agent_s1_rodovia",
      "prompt": "Qual é o orçamento estimado...",
      "status": "completed",
      "created_at": "2026-07-27T14:30:00Z",
      "tokens_used": { "input": 1523, "output": 487 },
      "latency_ms": 1245
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

---

## RAG (Knowledge Hub)

### POST /rag/search

Semantic search across knowledge base.

**Headers:**
```
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

**Request:**
```json
{
  "query": "Escoramento em obras viárias",
  "collection": "rodovias",  // Optional: filter by segment
  "k": 5,  // Top-k results (1-20, default: 5)
  "similarity_threshold": 0.6,
  "include_metadata": true
}
```

**Response (200):**
```json
{
  "results": [
    {
      "chunk_id": "chunk_001",
      "document_id": "doc_abc123",
      "source": "NBR-9050-2020.pdf",
      "similarity_score": 0.92,
      "text": "Escoramento em obras viárias deve seguir as diretrizes de segurança...",
      "metadata": {
        "document_type": "norm",
        "section": "3.2",
        "page": 15
      }
    }
  ],
  "total_results": 5,
  "query_embedding_tokens": 8
}
```

**Errors:**
- 400: Invalid query, k > 20
- 401: Unauthorized

---

### POST /rag/upload

Upload documents to knowledge hub.

**Headers:**
```
Authorization: Bearer eyJhbGc...
Content-Type: multipart/form-data
```

**Request:**
```
POST /rag/upload
Authorization: Bearer eyJhbGc...

Form data:
- files: [document.pdf, standard.docx, ...]  (max 50MB per file)
- collection: "rodovias"
- metadata: {"project_id": "proj_123", "segment": "S1"}
```

**Response (202):**
```json
{
  "upload_id": "upload_xyz789",
  "files_received": 3,
  "status": "processing",
  "estimated_completion": "2026-07-27T15:30:00Z",
  "webhook_url": "https://your-domain.com/webhooks/rag_upload"
}
```

**Webhook (when complete):**
```json
{
  "upload_id": "upload_xyz789",
  "status": "completed",
  "documents_processed": 3,
  "chunks_created": 145,
  "errors": []
}
```

**Errors:**
- 400: File too large, unsupported format
- 401: Unauthorized
- 413: Request entity too large

---

### GET /rag/documents

List uploaded documents in knowledge hub.

**Query Parameters:**
- `collection`: Filter by segment (optional)
- `search`: Text search in document names
- `limit`: 10-100 (default: 20)

**Response (200):**
```json
{
  "documents": [
    {
      "document_id": "doc_abc123",
      "name": "NBR-9050-2020.pdf",
      "collection": "rodovias",
      "size_bytes": 5242880,
      "chunk_count": 145,
      "uploaded_at": "2026-07-15T10:00:00Z",
      "status": "indexed"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

### DELETE /rag/documents/{document_id}

Delete a document from knowledge hub.

**Response (204):** No content

**Errors:**
- 404: Document not found
- 401: Unauthorized

---

## Routing

### POST /routing/classify

Classify user input to determine appropriate agent.

**Headers:**
```
Authorization: Bearer eyJhbGc...
```

**Request:**
```json
{
  "input": "Escoramento em obras viárias: quais normas aplicáveis?",
  "context": {
    "organization_id": "org_xyz789",
    "previous_agent": "agent_s1_rodovia"  // Optional
  }
}
```

**Response (200):**
```json
{
  "predicted_agent_id": "agent_s1_rodovia",
  "confidence": 0.94,
  "alternatives": [
    {
      "agent_id": "agent_s2_oae",
      "confidence": 0.04
    },
    {
      "agent_id": "agent_06_modelagem",
      "confidence": 0.02
    }
  ],
  "model_version": "routing-classifier-v2.3",
  "latency_ms": 245
}
```

---

### POST /routing/retrain

Trigger retraining of routing classifier.

**Headers:**
```
Authorization: Bearer eyJhbGc...
X-Admin-Token: admin_secret_xyz
```

**Request:**
```json
{
  "lookback_days": 30,
  "test_split": 0.2,
  "hyperparams": {
    "learning_rate": 1e-4,
    "epochs": 10,
    "batch_size": 32
  }
}
```

**Response (202):**
```json
{
  "job_id": "job_xyz789",
  "status": "queued",
  "estimated_duration_seconds": 3600,
  "callback_url": "https://api.manta.example.com/routing/retrain/job_xyz789"
}
```

---

## Feedback

### POST /feedback/submit

Submit feedback on agent response.

**Headers:**
```
Authorization: Bearer eyJhbGc...
```

**Request:**
```json
{
  "request_id": "req_xyz123",
  "rating": 5,  // 1-5 stars
  "comment": "Excellent analysis, very detailed.",
  "helpful": true,
  "tags": ["accurate", "detailed", "cite-sources"]
}
```

**Response (201):**
```json
{
  "feedback_id": "fb_abc123",
  "request_id": "req_xyz123",
  "status": "received",
  "created_at": "2026-07-27T14:30:00Z"
}
```

---

### GET /feedback/analytics

Get feedback analytics (admin-only).

**Headers:**
```
Authorization: Bearer eyJhbGc...
X-Admin-Token: admin_secret_xyz
```

**Query Parameters:**
- `agent_id`: Filter by agent (optional)
- `start_date`: ISO 8601 (optional)
- `end_date`: ISO 8601 (optional)

**Response (200):**
```json
{
  "period": { "start": "2026-07-01", "end": "2026-07-27" },
  "total_feedback": 1523,
  "average_rating": 4.2,
  "rating_distribution": {
    "5": 890,
    "4": 456,
    "3": 145,
    "2": 28,
    "1": 4
  },
  "top_tags": ["accurate", "detailed", "cite-sources"],
  "agents": {
    "agent_s1_rodovia": {
      "feedback_count": 234,
      "avg_rating": 4.5,
      "improvement_trends": "↑ +0.3 vs previous month"
    }
  }
}
```

---

## Fine-Tuning (ML)

### POST /ml/finetune

Submit a fine-tuning job.

**Headers:**
```
Authorization: Bearer eyJhbGc...
```

**Request:**
```json
{
  "dataset_uri": "s3://org-bucket/finetune-data.jsonl",
  "dataset_size": 512,  // Number of examples
  "model_base": "claude-3-5-sonnet-20241022",
  "adapter_name": "org_xyz789-rodovia-v1",
  "hyperparams": {
    "learning_rate": 2e-4,
    "epochs": 3,
    "batch_size": 8,
    "lora_rank": 16
  },
  "validation_split": 0.2
}
```

**Response (202):**
```json
{
  "job_id": "job_ft_xyz789",
  "status": "queued",
  "organization_id": "org_xyz789",
  "adapter_name": "org_xyz789-rodovia-v1",
  "estimated_duration_seconds": 7200,
  "webhook_url": "https://your-domain.com/webhooks/finetune"
}
```

**Webhook (when complete):**
```json
{
  "job_id": "job_ft_xyz789",
  "status": "completed",
  "model_adapter_id": "adapter_abc123",
  "metrics": {
    "train_loss": 0.42,
    "val_loss": 0.51,
    "val_accuracy": 0.96
  },
  "artifact_uri": "s3://artifacts/org_xyz789-rodovia-v1.tar.gz"
}
```

---

### GET /ml/finetune/{job_id}

Get status of a fine-tuning job.

**Response (200):**
```json
{
  "job_id": "job_ft_xyz789",
  "status": "completed",
  "progress": {
    "current_epoch": 3,
    "total_epochs": 3,
    "percent": 100
  },
  "metrics": {
    "train_loss": 0.42,
    "val_loss": 0.51,
    "val_accuracy": 0.96
  },
  "model_adapter_id": "adapter_abc123",
  "created_at": "2026-07-25T10:00:00Z",
  "completed_at": "2026-07-25T12:15:00Z"
}
```

---

### GET /ml/models

List fine-tuned models.

**Query Parameters:**
- `organization_id`: Filter by org (default: current org)
- `status`: active, archived, experimental

**Response (200):**
```json
{
  "models": [
    {
      "id": "adapter_abc123",
      "name": "org_xyz789-rodovia-v1",
      "base_model": "claude-3-5-sonnet-20241022",
      "status": "active",
      "created_at": "2026-07-25T12:15:00Z",
      "metrics": {
        "val_accuracy": 0.96,
        "improvement_vs_baseline": "+2.3%"
      },
      "usage_count": 145
    }
  ],
  "total": 3
}
```

---

### POST /ml/models/{model_id}/deploy

Deploy a fine-tuned model to production (A/B test).

**Request:**
```json
{
  "split_percent": 50,  // % of traffic to new model
  "agents": ["agent_s1_rodovia", "agent_s2_oae"],
  "monitoring_metrics": ["accuracy", "latency"],
  "rollback_threshold": 0.02  // If perf drops > 2%
}
```

**Response (202):**
```json
{
  "deployment_id": "deploy_xyz789",
  "model_id": "adapter_abc123",
  "status": "deploying",
  "split_percent": 50,
  "agents": ["agent_s1_rodovia", "agent_s2_oae"]
}
```

---

## Workflows

### POST /workflows

Create a new workflow.

**Request:**
```json
{
  "name": "Análise de Rodovia — Escopo Completo",
  "description": "Workflow que analisa projeto de rodovia de forma integrada",
  "steps": [
    {
      "agent_id": "agent_s1_rodovia",
      "prompt_template": "Analise o projeto técnico: {project_file}",
      "output_variable": "technical_analysis"
    },
    {
      "agent_id": "agent_05_orcamento",
      "prompt_template": "Estime o orçamento baseado em: {technical_analysis}",
      "output_variable": "budget_estimate"
    },
    {
      "agent_id": "agent_07_cronograma",
      "prompt_template": "Crie cronograma para: {budget_estimate}",
      "output_variable": "schedule"
    }
  ],
  "variables": {
    "project_file": { "type": "file", "required": true }
  }
}
```

**Response (201):**
```json
{
  "workflow_id": "wf_abc123",
  "name": "Análise de Rodovia — Escopo Completo",
  "created_at": "2026-07-27T14:30:00Z",
  "status": "active",
  "version": 1
}
```

---

### POST /workflows/{workflow_id}/execute

Execute a workflow.

**Request:**
```json
{
  "variables": {
    "project_file": "s3://bucket/project-2024.pdf"
  },
  "priority": "high"
}
```

**Response (202):**
```json
{
  "execution_id": "exec_xyz789",
  "workflow_id": "wf_abc123",
  "status": "running",
  "steps_total": 3,
  "steps_completed": 1
}
```

---

### GET /workflows/{workflow_id}/executions/{execution_id}

Get workflow execution result.

**Response (200):**
```json
{
  "execution_id": "exec_xyz789",
  "workflow_id": "wf_abc123",
  "status": "completed",
  "started_at": "2026-07-27T14:30:00Z",
  "completed_at": "2026-07-27T14:45:30Z",
  "outputs": {
    "technical_analysis": "Análise detalhada...",
    "budget_estimate": "R$ 2.5M",
    "schedule": "24 meses"
  }
}
```

---

## Admin

### GET /health

Health check (no auth required).

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-07-27T14:30:00Z",
  "uptime_seconds": 3600,
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "mcp_gateway": "healthy",
    "anthropic_api": "healthy"
  }
}
```

---

### GET /admin/deployment-status

Pre-launch deployment verification (admin-only).

**Headers:**
```
Authorization: Bearer eyJhbGc...
X-Admin-Token: admin_secret_xyz
```

**Response (200):**
```json
{
  "deployment": {
    "version": "1.0.0",
    "environment": "production",
    "deployed_at": "2026-07-27T10:00:00Z"
  },
  "tests": {
    "unit_coverage": 0.95,
    "integration_status": "passing",
    "e2e_scenarios": 8,
    "e2e_passing": 8
  },
  "infrastructure": {
    "kubernetes_nodes": 3,
    "pod_replicas": { "frontend": 2, "backend": 3, "database": 1 },
    "storage_available_gb": 50
  },
  "security": {
    "tls_certificate_valid": true,
    "secrets_encrypted": true,
    "penetration_test_passed": true
  },
  "monitoring": {
    "prometheus_targets": 18,
    "alerts_configured": 24,
    "dashboards_ready": 12
  },
  "checklist_complete": true
}
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid JSON, missing required field |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | Insufficient permissions (RBAC) |
| 404 | Not Found | Agent/document/workflow not found |
| 409 | Conflict | Email already registered |
| 429 | Too Many Requests | Rate limit exceeded (100 req/min) |
| 500 | Internal Server Error | Unhandled exception |
| 503 | Service Unavailable | Dependency (DB/API) down |

---

## Rate Limiting

**Global limit:** 100 requests/minute per user  
**Per-endpoint limits:**
- Agent execution: 50 req/min
- RAG search: 100 req/min
- Feedback submit: 200 req/min
- Fine-tuning: 10 jobs/day per org

**Headers returned:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1627401600
```

---

## Webhooks

Manta sends webhooks for long-running operations (document uploads, fine-tuning):

**Security:**
- Signed with HMAC-SHA256 (header: `X-Manta-Signature`)
- Retry logic: Exponential backoff, up to 5 attempts over 24h
- Expected HTTP 2xx response; anything else is considered failure

**Example webhook:**
```json
{
  "event": "finetune.completed",
  "timestamp": "2026-07-25T12:15:00Z",
  "data": {
    "job_id": "job_ft_xyz789",
    "status": "completed",
    "model_adapter_id": "adapter_abc123"
  }
}
```

---

**API Version:** 1.0  
**Last Updated:** 2026-07-27  
**Status:** Production Ready
