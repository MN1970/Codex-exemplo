# Contrato de API — Portal Manta `/v1`

- **ID do artefato**: MNT-2026-ARQ-0001 (anexo B)
- **Versão**: 1.0 · **Data**: 2026-08-20
- **Status**: proposta (gate MN) — anexo de `docs/PORTAL-BACKEND-PLANO.md`

Base: `https://portal-api.mantaassociados.com/v1`
Autenticação: `Authorization: Bearer <JWT do Supabase Auth>`

---

## 1. Convenções

### 1.1. Divisão de responsabilidade

| Operação | Caminho |
| --- | --- |
| Leitura simples, filtro, paginação, realtime | **PostgREST/Supabase JS** direto, protegido por RLS |
| Escrita de negócio, jobs, IA, exportação, integrações | **`/v1` no FastAPI** |

O frontend nunca escreve direto nas tabelas de negócio: validação,
auditoria e guardrails vivem na API.

### 1.2. Paginação

Cursor opaco. `GET /v1/...?limit=50&cursor=eyJ...`

```json
{ "data": [ ... ], "next_cursor": "eyJpZCI6..." , "has_more": true }
```

`limit` máximo 200. Ordenação padrão: `created_at DESC, id DESC`.

### 1.3. Erros — RFC 9457 (`application/problem+json`)

```json
{
  "type": "https://portal.mantaassociados.com/errors/validation",
  "title": "Payload inválido",
  "status": 422,
  "detail": "cost_items[3].unit_price deve ser >= 0",
  "instance": "/v1/budgets/9f1.../items:bulk",
  "request_id": "01JB8Q7K3M..."
}
```

| Código | Uso |
| --- | --- |
| 400 | Requisição malformada |
| 401 | Sem token / token inválido |
| 403 | Sem permissão no tenant ou projeto |
| 404 | Recurso inexistente **ou fora do tenant** (nunca 403, para não vazar existência) |
| 409 | Conflito de versão (`If-Match` falhou) |
| 422 | Validação semântica |
| 429 | Rate limit ou teto de tokens — `Retry-After` |
| 502/504 | Falha em dependência (Anthropic, Graph) |

### 1.4. Idempotência e concorrência

- Todo `POST` que cria recurso aceita `Idempotency-Key` (UUID); repetição
  em 24 h devolve a resposta original.
- `PATCH`/`PUT` exigem `If-Match: <etag>`; sem isso, `428`.

### 1.5. Cabeçalhos padrão de resposta

`X-Request-Id`, `ETag` (read models), `RateLimit-Remaining`,
`X-Tenant-Id` (eco, para depuração).

---

## 2. Projetos e ficha

```http
GET  /v1/projects?segment=S8&phase=obra&limit=50
GET  /v1/projects/{project_id}
POST /v1/projects
PATCH /v1/projects/{project_id}
GET  /v1/projects/{project_id}/ficha
GET  /v1/projects/{project_id}/dashboard?from=2026-01-01&to=2026-08-31
```

`GET /v1/projects/{id}/ficha` (módulo 8) — read model consolidado,
cacheável por `ETag`:

```json
{
  "project": { "id": "...", "code": "OBRA-2026-014", "name": "...",
               "segment_code": "S8", "phase": "obra" },
  "contract": { "number": "...", "original_amount": 128500000.00,
                "currency": "BRL", "reference_date": "2026-01-15",
                "source_ref": "Contrato assinado, cláusula 5.1",
                "amendments_count": 3, "current_amount": 141200000.00 },
  "schedule": { "baseline_finish": "2028-04-30", "current_finish": "2028-11-12",
                "delay_days": 196, "critical_activities": 42 },
  "cost":     { "budget_total": 141200000.00, "measured_total": 61340000.00,
                "physical_pct": 43.2, "financial_pct": 43.4 },
  "claims":   { "open": 4, "claimed_amount": 18700000.00, "currency": "BRL" },
  "missing":  { "physical_pct_by_discipline": "sem medição aprovada no período" }
}
```

O campo `missing` materializa **R2**: o que não existe aparece como
motivo, nunca como zero ou estimativa.

---

## 3. Contratos (módulo 2)

```http
GET   /v1/projects/{project_id}/contracts
POST  /v1/projects/{project_id}/contracts
GET   /v1/contracts/{id}
POST  /v1/contracts/{id}/amendments
GET   /v1/contracts/{id}/clauses?q=reequil%C3%ADbrio&limit=20
GET   /v1/contracts/{id}/milestones
```

Busca de cláusula usa full-text em português (`search_tsv`) com
destaque (`headline`) e devolve o `document_version` de origem para
rastreabilidade.

---

## 4. Cronograma (módulo 3)

```http
POST /v1/projects/{project_id}/schedules/import      # multipart XER/MPP/XML
     → 202 { "job_id": "...", "schedule_id": "..." }
GET  /v1/schedules/{id}/versions
GET  /v1/schedules/{id}/activities?version_id=&critical=true&cursor=
GET  /v1/schedules/{id}/critical-path?version_id=
GET  /v1/schedules/{id}/s-curve?version_id=&granularity=month
POST /v1/schedules/{id}/compare                      # baseline × revisão
     { "base_version_id": "...", "target_version_id": "..." }
GET  /v1/schedules/{id}/health                       # DCMA 14-point
```

Import é sempre assíncrono (arquivos P6 grandes). O cliente acompanha
por `GET /v1/jobs/{job_id}` ou por Realtime em `portal_ops.job_events`.

---

## 5. Claims (módulo 4)

```http
GET  /v1/projects/{project_id}/claims
POST /v1/projects/{project_id}/claims
GET  /v1/claims/{id}
POST /v1/claims/{id}/windows
POST /v1/claims/{id}/events
POST /v1/claims/{id}/events/{event_id}/impacts
POST /v1/claims/{id}/quantum:recalculate     → 202 job
GET  /v1/claims/{id}/quantum
POST /v1/claims/{id}/export                  → 202 job (DOCX/PDF/XLSX)
```

Toda linha de quantum exige `source_ref` (R5). A API rejeita com `422`
uma linha monetária sem `reference_date` + `source_ref`.

---

## 6. Custos (módulo 5)

```http
GET  /v1/projects/{project_id}/budgets
POST /v1/budgets/{id}/versions
POST /v1/budgets/{id}/items:bulk             # ≤ 5.000 linhas por chamada
GET  /v1/budget-versions/{id}/items?wbs=&ref_code=
POST /v1/projects/{project_id}/measurements
POST /v1/measurements/{id}:approve           # gate humano (role ≥ manager)
GET  /v1/projects/{project_id}/cashflow?granularity=month
GET  /v1/sicro/search?q=escava%C3%A7%C3%A3o&table=SICRO&uf=SP&ref=2026-04
```

`/v1/sicro/search` faz proxy para as tools SICRO já expostas no MCP do
hub — o Portal não replica a base de composições.

---

## 7. Assistente IA (módulo 6)

### 7.1. Roteamento determinístico

```http
POST /v1/ai/route
{ "prompt": "reabilitação da ETA norte, revisão do orçamento" }

200
{
  "primary": { "agent_code": "S8", "name": "saneamento", "score": 200 },
  "alternatives": [ { "agent_code": "A5", "name": "orcamento", "score": 100 } ],
  "confidence": 0.83
}
```

`confidence < 0.70` → `needs_disambiguation: true` e o frontend pergunta
ao usuário em vez de adivinhar.

### 7.2. Execução

```http
POST /v1/ai/runs
{
  "project_id": "…",              // opcional
  "agent_code": "S8",             // opcional; ausente → router decide
  "prompt": "…",
  "attachments": ["document_version_id", "…"],
  "options": { "rag": true, "top_k": 5 }
}

202 { "run_id": "…", "status": "queued", "agent_code": "S8" }
```

### 7.3. Streaming (SSE)

```http
GET /v1/ai/runs/{run_id}/stream
Accept: text/event-stream
```

```text
event: status      data: {"status":"running","agent_code":"S8"}
event: rag         data: {"chunks":[{"id":"…","score":0.82,"doc":"…"}]}
event: token       data: {"text":"A adutora "}
event: tool_call   data: {"name":"sicro_search","args":{…}}
event: citation    data: {"version_id":"…","locator":"p. 42"}
event: guardrail   data: {"guard":"aluci-guard","severity":"warn","reference":"NBR 12218"}
event: done        data: {"status":"succeeded","usage":{"input":18320,"output":1204}}
```

Reconexão com `Last-Event-ID`. Run que termina `flagged` (achado
bloqueante de guardrail) entrega o conteúdo marcado e **não** pode ser
exportado como artefato oficial.

### 7.4. Catálogo e RAG

```http
GET  /v1/ai/agents?kind=segmento          # A1–A10, S1–S13, F*
GET  /v1/ai/agents/{code}
POST /v1/ai/rag/query
     { "query": "…", "collection": "normas", "top_k": 5, "project_id": "…" }
GET  /v1/ai/runs?project_id=&status=&cursor=
POST /v1/ai/runs/{id}:cancel
```

O filtro de tenant na busca vetorial é aplicado **dentro da RPC**, não
no código de aplicação.

---

## 8. Documentos e busca (módulo 7)

```http
POST /v1/documents:upload-url                # devolve URL assinada (TTL 15 min)
     { "project_id": "…", "filename": "…", "mime_type": "…", "size_bytes": 0 }
POST /v1/documents                           # registra após o upload
GET  /v1/projects/{project_id}/documents?doc_type=&discipline=&cursor=
GET  /v1/documents/{id}/versions
GET  /v1/document-versions/{id}/download-url
POST /v1/documents/{id}/reindex              → 202 job
POST /v1/sharepoint/sync                     → 202 job (role ≥ admin)
GET  /v1/search?q=&mode=hybrid&project_id=&limit=20
```

`mode`: `text` (tsvector), `vector` (pgvector) ou `hybrid` (RRF entre
os dois — padrão).

---

## 9. Operação

```http
GET  /v1/jobs/{id}                 # status + eventos + progresso
GET  /v1/jobs?kind=&status=&cursor=
GET  /v1/usage?from=&to=&group_by=project   # tokens e custo por período
GET  /v1/notifications?unread=true
POST /v1/notifications/{id}:read
GET  /healthz                      # liveness (sem auth)
GET  /readyz                       # Postgres + fila + Graph (sem auth)
```

`GET /v1/usage` é o que fecha a conta do produto: consumo real por
projeto/tenant, base para a margem do contrato mensal.

---

## 10. Limites operacionais

| Limite | Valor inicial |
| --- | --- |
| Requisições por tenant | 600/min |
| Runs de IA simultâneos por tenant | 5 |
| Upload por arquivo | 250 MB |
| Linhas por `items:bulk` | 5.000 |
| TTL de URL assinada | 15 min |
| Retenção de SSE reconectável | 5 min |

Todos configuráveis por tenant em `portal_ops.feature_flags` /
`tenants` — os números acima são ponto de partida para o piloto, a
revisar com dados reais de uso.
