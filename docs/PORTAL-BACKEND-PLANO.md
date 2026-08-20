# Plano de Backend — Portal Manta (Portal IA)

- **ID do artefato**: MNT-2026-ARQ-0001
- **Versão**: 1.0
- **Data**: 2026-08-20
- **Autor**: Manta Maestro (Manta 00) → F-portal-ia + F-arquiteto-ia
- **Status**: Proposta para gate humano (MN)
- **Substitui**: — (primeiro documento de arquitetura do backend do Portal)

Documentos relacionados:
`sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` (v2.0.0),
`docs/COWORK-INTEGRATION.md`, `docs/DEPLOY-v4.2.md`,
`docs/portal-backend/schema-draft.sql`, `docs/portal-backend/api-contract.md`.

---

## Sumário

1. [Escopo, premissas e não-escopo](#1-escopo-premissas-e-não-escopo)
2. [Decisões de arquitetura (ADR resumidos)](#2-decisões-de-arquitetura-adr-resumidos)
3. [Visão de componentes](#3-visão-de-componentes)
4. [Modelo de dados](#4-modelo-de-dados)
5. [Multi-tenancy, autenticação e autorização](#5-multi-tenancy-autenticação-e-autorização)
6. [Contrato de API](#6-contrato-de-api)
7. [Camada de IA — orquestração, RAG e guardrails](#7-camada-de-ia--orquestração-rag-e-guardrails)
8. [Ingestão documental (SharePoint → Portal → RAG)](#8-ingestão-documental-sharepoint--portal--rag)
9. [Jobs assíncronos e importadores](#9-jobs-assíncronos-e-importadores)
10. [Segurança, LGPD e regras invioláveis R1–R5](#10-segurança-lgpd-e-regras-invioláveis-r1r5)
11. [Observabilidade, SLO e custos](#11-observabilidade-slo-e-custos)
12. [Ambientes, CI/CD e deploy](#12-ambientes-cicd-e-deploy)
13. [Estratégia de testes](#13-estratégia-de-testes)
14. [Roadmap por fases](#14-roadmap-por-fases)
15. [Riscos e decisões pendentes](#15-riscos-e-decisões-pendentes)

---

## 1. Escopo, premissas e não-escopo

### 1.1. O que este backend serve

O **Portal IA** é produto vendido a cliente (implantação + mensalidade —
ver §11.3) e, simultaneamente, a camada operacional interna da Manta.
O frontend é o scaffold React de **8 módulos**:

| # | Módulo | Necessidade de backend |
|---|--------|------------------------|
| 1 | Dashboard | Agregações de prazo, custo, claims, alertas |
| 2 | Contratos | Contratos, aditivos, cláusulas, prazos-gatilho |
| 3 | Cronograma | Import XER/MSP, baselines, CPM, curva S, atrasos |
| 4 | Claims | Janelas, eventos, nexo causal, quantum, anexos |
| 5 | Custos | Orçamento, SICRO, medições, fluxo de caixa, BDI |
| 6 | Assistente IA | Chat com os 20 agentes, streaming, RAG, citações |
| 7 | Docs | Repositório, versões, sync SharePoint, busca |
| 8 | Ficha | Ficha técnica consolidada do projeto (read model) |

### 1.2. Premissa central (assumida, confirmar em §15)

> O backend é **multi-tenant desde o dia 1**, com a Manta como
> `tenant` interno (tenant zero) e cada cliente como tenant isolado
> por RLS. Isso evita reescrita quando o segundo cliente entrar e
> permite que o uso interno valide o produto antes da venda.

Alternativa descartada: dois backends (interno + produto). Custo de
manutenção dobrado, divergência de schema garantida em 6 meses.

### 1.3. Premissas de plataforma

- Supabase permanece o plano de dados (projeto `manta-maestro-v5`,
  `ogxxgvgtulrbbppshjie`, região `sa-east-1`).
- Embeddings: `BAAI/bge-small-en-v1.5`, 384d, pgvector HNSW
  (cosine, m=16, ef=64) — mesma configuração de produção.
- O hub existente (`manta-hub`, FastAPI + MCP em
  `hub.mantaassociados.com`) é reaproveitado como *runtime* de
  aplicação; o Portal ganha um serviço irmão, não um stack novo.
- SharePoint (`sites/Engenharia`, library `Documentos`) continua
  **sistema de registro** dos documentos internos. O Portal indexa e
  referencia; não substitui.
- Frontend em Netlify (team `mneves`), backend na VPS.

### 1.4. Não-escopo desta fase

- Reescrita do AskCAD ou dos MCP tools já entregues na Fase A.
- Motor de cálculo de engenharia dentro do backend (fica nas skills /
  agentes; o backend orquestra e persiste resultados).
- App mobile nativo.
- Faturamento/cobrança automatizada (o contrato é fechado fora do
  Portal; o Portal só mede consumo — §11.3).

---

## 2. Decisões de arquitetura (ADR resumidos)

### ADR-01 — Supabase como plano de dados, FastAPI como plano de aplicação

**Decisão**: híbrido. Postgres/Auth/Storage/Realtime do Supabase para
dados, sessão e arquivos; um serviço **FastAPI (Python 3.12)** para
tudo que envolve orquestração de agentes, parsers pesados (XER, MSP,
DWG, PDF), regras de negócio e chamadas à Anthropic API.

**Por quê**: o frontend fala direto com o Postgres via PostgREST para
leituras simples (paginação, filtros, realtime) — economia grande de
código CRUD. O que Edge Functions fazem mal (jobs longos, bibliotecas
Python de engenharia, streaming com controle fino de tokens) fica no
FastAPI, onde as skills e o parser P6 já vivem.

**Descartado**: (a) *Supabase puro com Edge Functions* — limite de
tempo de execução e ecossistema Deno incompatível com o parque Python
das skills; (b) *FastAPI puro com Postgres gerenciado* — perde Auth,
Storage, RLS, Realtime e obriga a reimplementar tudo isso.

### ADR-02 — Um cluster, schemas separados; split por projeto só quando exigido

**Decisão**: v1 usa o cluster existente com schemas `portal_core`,
`portal_docs`, `portal_ai`, `portal_ops`, convivendo com o schema
público do RAG (`ke_embeddings`, `manta_rag_chunks`).

**Gatilho de split**: primeiro contrato que exija isolamento físico de
dados ou residência específica → projeto Supabase dedicado
`manta-portal-<cliente>` com o mesmo schema, provisionado por
migração versionada. O modelo multi-tenant por RLS já torna esse
split mecânico.

### ADR-03 — Fila no próprio Postgres (PGMQ), não Redis/Celery

**Decisão**: `pgmq` (extensão Supabase) + worker Python dedicado.
Uma dependência a menos para operar, transacionalidade com o dado de
negócio (enfileirar job e gravar estado no mesmo commit), visibilidade
via SQL.

**Gatilho de revisão**: > ~50 jobs/min sustentados ou necessidade de
fan-out massivo → migrar para `arq` + Redis. O contrato do worker
(§9) é agnóstico à fila para tornar essa troca barata.

### ADR-04 — Anthropic API direta, não gateway próprio

Chamadas ao modelo saem do FastAPI com `model tiering` por agente
(Haiku para roteamento, Sonnet para produção, Opus para claims e
arquitetura), *prompt caching* nos blocos estáveis (SKILL.md, contexto
do projeto) e contabilização de tokens por tenant (§11.3).

### ADR-05 — Contrato de API versionado e estável (`/v1`)

O frontend do Portal é entregue a cliente; quebra de contrato é
incidente. Versionamento no path, erros em `application/problem+json`
(RFC 9457), paginação por cursor, `Idempotency-Key` em toda escrita
não-idempotente. Detalhe em `docs/portal-backend/api-contract.md`.

---

## 3. Visão de componentes

```
┌──────────────────────────────────────────────────────────────────┐
│ Frontend — Portal React (Netlify)                                │
│ 8 módulos · Supabase JS (leitura/realtime) · fetch /v1 (escrita) │
└───────────────┬──────────────────────────────┬───────────────────┘
                │ JWT (Supabase Auth)          │ JWT
                ▼                              ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│ Supabase (sa-east-1)      │   │ portal-api — FastAPI (VPS)       │
│ · Postgres 15 + pgvector  │◄──┤ · /v1 REST + /v1/…/stream (SSE)  │
│ · Auth (OIDC Entra ID)    │   │ · orquestração dos 20 agentes    │
│ · Storage (buckets/tenant)│   │ · parsers XER/MSP/PDF/DWG        │
│ · Realtime (job status)   │   │ · guardrails R1–R5 · aluci-guard │
│ · RLS por tenant_id       │   └───────┬──────────────┬───────────┘
│ · pgmq (fila de jobs)     │           │              │
└─────┬─────────────────────┘           │              │
      │                                 ▼              ▼
      │                    ┌───────────────────┐ ┌─────────────────┐
      │                    │ Anthropic API     │ │ manta-hub /mcp  │
      │                    │ opus-5/sonnet-5/  │ │ (tools Maestro, │
      │                    │ haiku-4-5         │ │  AskCAD, SICRO) │
      │                    └───────────────────┘ └─────────────────┘
      ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│ portal-worker (VPS)       │──►│ Microsoft Graph / SharePoint     │
│ · consome pgmq            │   │ 04_IA/…, 03_Projetos/<Segmento>/ │
│ · ingestão SP → RAG       │   └──────────────────────────────────┘
│ · import cronograma/custo │
│ · embeddings bge-small    │
└───────────────────────────┘
```

Três processos de aplicação, todos versionados no mesmo repositório
(`manta-hub`, diretório `backends/portal/`):

| Processo | systemd unit | Responsabilidade |
|---|---|---|
| `portal-api` | `portal-api.service` | HTTP síncrono + SSE |
| `portal-worker` | `portal-worker.service` | Jobs de fila (pgmq) |
| `portal-scheduler` | `portal-scheduler.timer` | Cron: sync SP, snapshots, alertas |

---

## 4. Modelo de dados

DDL completo e comentado em **`docs/portal-backend/schema-draft.sql`**
(migração candidata — não aplicar sem aprovação MN). Resumo por
domínio:

### 4.1. `portal_core` — tenancy e projetos

| Tabela | Papel |
|---|---|
| `tenants` | Cliente/organização. Tenant zero = Manta |
| `profiles` | Espelho de `auth.users` + nome, cargo, avatar |
| `memberships` | `(tenant_id, user_id, role)` — RBAC |
| `projects` | Obra/contrato-objeto. FK `segment_code` (S1–S11) |
| `project_members` | ACL por projeto (leitura/edição/aprovação) |
| `contracts` | Contrato principal por projeto |
| `contract_amendments` | Aditivos (prazo, valor, escopo) |
| `contract_clauses` | Cláusulas indexadas (nº, título, texto, tags) |
| `milestones` | Marcos contratuais e gatilhos de prazo |

### 4.2. `portal_core` — cronograma e custos

| Tabela | Papel |
|---|---|
| `schedules` | Cronograma importado (origem XER/MSP/manual) |
| `schedule_versions` | Baseline e revisões (`is_baseline`, `data_date`) |
| `activities` | Atividades com WBS, datas, folgas, `is_critical` |
| `activity_links` | Precedências (FS/SS/FF/SF, lag) |
| `progress_snapshots` | Avanço físico por período (curva S) |
| `budgets` / `budget_versions` | Orçamento e revisões |
| `cost_items` | Itens com código SICRO/SINAPI, qtd, preço unit., BDI |
| `measurements` | Medições (boletins) por período |
| `cashflow_entries` | Fluxo previsto × realizado |

### 4.3. `portal_core` — claims

| Tabela | Papel |
|---|---|
| `claims` | Pleito/reequilíbrio (nº, objeto, status, valor) |
| `claim_windows` | Janelas de análise (GR-xx, trimestre) |
| `claim_events` | Eventos com data, causa, responsabilidade, evidência |
| `claim_impacts` | Nexo evento → atividade → prazo/custo |
| `quantum_lines` | Composição do quantum (linha, base, valor, fonte) |

### 4.4. `portal_docs`

| Tabela | Papel |
|---|---|
| `documents` | Documento lógico (título, tipo, disciplina, projeto) |
| `document_versions` | Versões com hash SHA-256, tamanho, storage key |
| `document_links` | Vínculo documento ↔ claim/atividade/cláusula |
| `sp_sync_state` | Cursor de sincronização por pasta SharePoint |
| `extraction_results` | Saída estruturada de parsers (JSONB + schema) |

### 4.5. `portal_ai`

| Tabela | Papel |
|---|---|
| `agent_runs` | Execução de agente: prompt, agente, projeto, status |
| `agent_messages` | Turnos da conversa (role, conteúdo, tokens) |
| `agent_tool_calls` | Ferramentas invocadas + resultado resumido |
| `rag_queries` | Query, coleção, top-k, scores, chunks retornados |
| `citations` | Citação ↔ `document_version` ↔ trecho (rastreabilidade R2) |
| `guardrail_findings` | Achados de `aluci-guard`/`consist-guard` por run |
| `token_usage` | Tokens in/out/cache por run, tenant, modelo, custo |

RAG continua nas tabelas de produção (`ke_embeddings`,
`manta_rag_chunks`); o Portal adiciona apenas **`tenant_id` e
`project_id` como colunas de filtro** para não vazar contexto entre
tenants (item bloqueante — §15).

### 4.6. `portal_ops`

| Tabela | Papel |
|---|---|
| `jobs` | Estado do job (tipo, payload, tentativas, erro) |
| `job_events` | Timeline por job (para UI de progresso) |
| `audit_log` | Quem fez o quê, quando, em qual recurso (append-only) |
| `notifications` | Alertas ao usuário (prazo, CI, aprovação) |
| `integrations` | Credenciais/config por tenant (referência ao cofre) |
| `feature_flags` | Liberação de módulo por tenant |

### 4.7. Convenções

- PK `uuid` (`gen_random_uuid()`); `created_at`/`updated_at timestamptz`;
  `created_by uuid`.
- **Toda** tabela de negócio carrega `tenant_id uuid NOT NULL` — sem
  exceção, é o que torna a política RLS uniforme.
- Soft delete via `deleted_at` nas entidades que aparecem em relatório.
- Valores monetários: `numeric(18,2)` + `currency char(3)` +
  `reference_date date` (R5 — nunca um `float` solto).
- Quantidades de engenharia: `numeric(18,4)` + `unit text`.
- Nomenclatura de artefato gerado: `MNT-YYYY-TIPO-SEQ` em
  `documents.manta_id` (R4).

---

## 5. Multi-tenancy, autenticação e autorização

### 5.1. Identidade

- **Equipe Manta**: OIDC com Microsoft Entra ID (mesma conta do M365 /
  SharePoint) — evita segundo diretório e herda MFA corporativo.
- **Usuários do cliente**: e-mail + senha com política forte, ou OIDC
  do cliente quando existir (configurável por tenant).
- **Serviços** (worker, scheduler, integrações): `service_role` restrito
  por rede, nunca exposto ao browser.

### 5.2. Claims no JWT

Auth Hook do Supabase injeta no token: `tenant_id`, `role`,
`project_ids` (quando ≤ 50; acima disso, resolução por tabela).

### 5.3. RLS — padrão único

```sql
-- aplicado a toda tabela com tenant_id
CREATE POLICY tenant_isolation ON <tabela>
  USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- camada 2: acesso por projeto
CREATE POLICY project_scope ON <tabela_com_project_id>
  USING (project_id IN (SELECT project_id FROM portal_core.project_members
                        WHERE user_id = auth.uid()));
```

Teste de regressão obrigatório: suíte que, para **cada** tabela,
autentica como tenant A e verifica que `SELECT` sobre dado do tenant B
retorna zero linhas (§13).

### 5.4. Papéis (RBAC)

| Papel | Escopo | Pode |
|---|---|---|
| `owner` | tenant | Tudo, inclusive faturamento e usuários |
| `admin` | tenant | Usuários, projetos, integrações |
| `manager` | projeto | Editar dados do projeto, aprovar artefatos |
| `analyst` | projeto | Criar/editar; não aprova |
| `viewer` | projeto | Somente leitura + exportação |
| `agent` | serviço | Escrita restrita nas tabelas `portal_ai` |

Aprovação (gate humano) é papel `manager`+: nenhum artefato gerado por
IA sai do Portal como oficial sem `approved_by` preenchido.

---

## 6. Contrato de API

Detalhe completo em **`docs/portal-backend/api-contract.md`**. Resumo:

```
POST   /v1/auth/session                  troca de código OIDC
GET    /v1/projects                      lista (cursor, filtros)
GET    /v1/projects/{id}/ficha           read model consolidado (mód. 8)
GET    /v1/projects/{id}/dashboard       agregações (mód. 1)

GET    /v1/projects/{id}/contracts       (mód. 2)
POST   /v1/contracts/{id}/amendments
GET    /v1/contracts/{id}/clauses?q=

POST   /v1/projects/{id}/schedules/import   upload XER/MSP → job (mód. 3)
GET    /v1/schedules/{id}/activities
GET    /v1/schedules/{id}/critical-path
GET    /v1/schedules/{id}/s-curve

GET    /v1/projects/{id}/claims             (mód. 4)
POST   /v1/claims/{id}/windows
POST   /v1/claims/{id}/quantum:recalculate  → job

GET    /v1/projects/{id}/budgets            (mód. 5)
POST   /v1/budgets/{id}/items:bulk
GET    /v1/projects/{id}/cashflow

POST   /v1/ai/runs                          inicia execução de agente (mód. 6)
GET    /v1/ai/runs/{id}/stream              SSE: tokens, tool calls, citações
POST   /v1/ai/route                         router Maestro (determinístico)
GET    /v1/ai/agents                        catálogo A1–A10 / S1–S11
POST   /v1/ai/rag/query                     busca semântica com filtro de tenant

GET    /v1/projects/{id}/documents          (mód. 7)
POST   /v1/documents:upload                 URL assinada + registro
POST   /v1/documents/{id}/reindex           → job
GET    /v1/search?q=                        híbrido (texto + vetor)

GET    /v1/jobs/{id}                        estado + eventos
GET    /v1/usage?from=&to=                  consumo de tokens/custo
```

Convenções: cursor (`?cursor=&limit=`), `ETag`/`If-None-Match` em read
models, `Idempotency-Key` em POST, `problem+json` em erro, `429` com
`Retry-After` em rate limit por tenant.

---

## 7. Camada de IA — orquestração, RAG e guardrails

### 7.1. Fluxo de uma execução (`POST /v1/ai/runs`)

```
1. Valida JWT → tenant_id, project_id, permissão no projeto
2. Router determinístico (keyword match, zero token) → agente A*/S*/F*
   · confiança < 70% → devolve 200 com `needs_disambiguation` + opções
3. Cria `agent_runs` (status=queued) e devolve 202 + run_id
4. Worker/handler monta o contexto:
   · SKILL.md do agente (bloco cacheado)
   · ficha do projeto (bloco cacheado por projeto)
   · RAG top-5 filtrado por tenant_id + coleção do agente
   · histórico truncado por janela
5. Chama Anthropic com o tier do agente (haiku/sonnet/opus)
6. Tool calls → MCP do hub (SICRO, AskCAD, cronograma) ou funções locais
7. Streaming para o cliente via SSE; persistência incremental
8. Pós-processamento obrigatório:
   · aluci-guard (normas, leis, SICRO, URLs, DOIs) → guardrail_findings
   · R1 (anonimização de nomes de empresa em artefato)
   · citações resolvidas para document_version (R2)
9. Grava token_usage e fecha o run (status=succeeded|failed|flagged)
```

Run com achado **bloqueante** do `aluci-guard` termina como `flagged`:
o conteúdo é entregue marcado, nunca publicado como artefato oficial.

### 7.2. Model tiering

| Uso | Modelo | Racional |
|---|---|---|
| Roteamento, classificação, extração simples | `claude-haiku-4-5` | Volume alto, tarefa fechada |
| Agentes de produção (S1–S11, A2–A8) | `claude-sonnet-5` | Padrão |
| A1-claims, A10-risco, F-arquiteto-ia | `claude-opus-5` | Raciocínio longo, risco alto |

Tier é config por agente em tabela (`portal_ai.agent_config`), não
constante em código — permite ajuste sem deploy.

### 7.3. RAG

- Coleções: `propostas`, `contratos`, `normas`, `composicoes`,
  `projetos` + prefixos por segmento (`rod:`, `oae:`, … `bar:`).
- Query: embedding 384d → HNSW cosine → `threshold > 0.7`, top-5 →
  injeção como `[FONTE N]`.
- **Filtro de tenant é obrigatório na RPC**, não no código de aplicação
  (defesa em profundidade).
- Coleções públicas (normas, SICRO) são compartilhadas via
  `tenant_id IS NULL`; conteúdo de projeto nunca é.

### 7.4. Controle de custo

Teto de tokens por tenant/mês em `tenants.token_budget`; ao atingir
80% → notificação; 100% → runs novos rejeitados com `402`/`429`
configurável. Sem isso o produto tem custo variável sem limite.

---

## 8. Ingestão documental (SharePoint → Portal → RAG)

```
scheduler (a cada 30 min)
  └─ para cada linha de sp_sync_state (pasta × tenant):
       Graph delta query → lista mudanças desde o cursor
       └─ enfileira job `document.ingest` por arquivo
            ├─ baixa para Storage (bucket do tenant)
            ├─ hash SHA-256 → deduplicação (rag_index_log)
            ├─ parser por tipo: PDF (texto+OCR), XLSX, DOCX, DWG/DXF
            ├─ chunking 800/100
            ├─ embedding bge-small-en-v1.5 (384d)
            └─ upsert em manta_rag_chunks + documents/document_versions
```

Pontos de atenção:

- O MCP M365 hoje é **read-only**; escrita no SP depende do
  `sharepoint-write-mcp-server` (pendência aberta — §15). A ingestão
  descrita só precisa de leitura, então **não é bloqueada** por isso.
- Idempotência por hash: reprocessar a mesma versão é no-op.
- Falha de parser não derruba o job da pasta: registra
  `documents.status='parse_failed'` + motivo (R2), segue.

---

## 9. Jobs assíncronos e importadores

| Tipo de job | Origem | Duração típica | Saída |
|---|---|---|---|
| `document.ingest` | scheduler/upload | s–min | chunks + embeddings |
| `schedule.import` | upload XER/MSP | s–min | `activities`, `links`, versão |
| `schedule.analyze` | usuário | s | CPM, DCMA-14, curva S |
| `budget.import` | upload XLSX | s | `cost_items` + validação SICRO |
| `claim.quantum` | usuário | min | `quantum_lines` + memória |
| `ai.run` | API | s–min | `agent_messages`, citações |
| `report.export` | usuário | s–min | DOCX/XLSX/PPTX no Storage |

Contrato do worker: `handler(payload) -> Result`, com *retry* exponencial
(3 tentativas), *dead letter* em `jobs.status='dead'`, e todo evento
relevante escrito em `job_events` para a UI de progresso (Realtime).

Importadores reaproveitam as skills existentes (`cronograma-toolkit`,
`xer-p6-analytics`, `sicro-composicoes`, `evtea-extractor`) como
bibliotecas Python — sem reimplementar parser.

---

## 10. Segurança, LGPD e regras invioláveis R1–R5

### 10.1. Controles

| Controle | Implementação |
|---|---|
| Isolamento | RLS em todas as tabelas + filtro de tenant na RPC do RAG |
| Segredos | Cofre da VPS (systemd `LoadCredential` ou Doppler/1Password); nada em `.env` versionado |
| Storage | Buckets por tenant, URLs assinadas com TTL ≤ 15 min |
| Transporte | TLS 1.2+ obrigatório; HSTS |
| Auditoria | `audit_log` append-only, retenção 24 meses |
| Rate limit | Por tenant e por rota (nginx + contador no Postgres) |
| Uploads | Verificação de tipo real (magic bytes), limite de tamanho, antivírus opcional |
| Dependências | `pip-audit` + Dependabot no CI |
| Revisão | `security-review` antes de cada release de produção |

### 10.2. LGPD

Dados pessoais no Portal são de **usuários corporativos** (nome,
e-mail, cargo) — base legal: execução de contrato. Documentos de obra
podem conter dados de terceiros: tratados como confidenciais do tenant,
sem uso para treinamento, sem compartilhamento entre tenants.
Retenção e exclusão definidas em contrato; `DELETE` de tenant remove
dados e objetos de Storage em cascata (job `tenant.purge`).

### 10.3. Aderência às regras R1–R5

| Regra | Onde é imposta no backend |
|---|---|
| **R1** — nunca exibir nomes de empresa em artefato | Filtro de anonimização na etapa 8 do §7.1, aplicado a todo export |
| **R2** — dado ausente = `null` + motivo | Colunas anuláveis + `*_missing_reason text`; API nunca devolve valor inventado |
| **R3** — output técnico passa por `aluci-guard` | Etapa obrigatória do pipeline; run sem guardrail não pode ser exportado |
| **R4** — todo artefato tem ID/versão/data | `documents.manta_id`, `version`, `created_at` obrigatórios em export |
| **R5** — valores em BRL @data + fonte | Trio `amount`/`currency`/`reference_date` + `source_ref` em toda tabela monetária |

---

## 11. Observabilidade, SLO e custos

### 11.1. Telemetria

- **Logs** estruturados JSON (`structlog`) com `request_id`, `tenant_id`,
  `run_id`; envio para Loki ou arquivo rotacionado na VPS.
- **Métricas** Prometheus: latência por rota, fila (profundidade, idade
  da mensagem mais antiga), tokens/min, erros 5xx, custo/dia.
- **Traços** OpenTelemetry cobrindo API → worker → Anthropic.
- **Health**: `/healthz` (liveness), `/readyz` (Postgres + fila + Graph).

### 11.2. SLO propostos

| Indicador | Alvo |
|---|---|
| Disponibilidade da API | 99,5%/mês |
| p95 de leitura CRUD | < 400 ms |
| Primeiro token no chat | < 2,5 s |
| Import de cronograma (≤ 5k atividades) | < 90 s |
| RPO / RTO | 24 h (PITR 7 dias) / 4 h |

### 11.3. Custos

| Item | Valor | Data | Fonte |
|---|---|---|---|
| Preço do Portal IA ao cliente | R$ 50.000 implantação + R$ 25.000/mês | 2026-07-27 | skill `manta-maestro` v5.0.1 §9 |
| Supabase (plano atual) | `null` — a confirmar no console | — | conta `manta-maestro-v5` |
| VPS (api + worker) | `null` — a confirmar na fatura | — | provedor atual do hub |
| Anthropic API | `null` — depende de volume; instrumentar por `token_usage` antes de precificar | — | medição do piloto |

Custo de LLM não é estimado aqui de propósito (R2): a medição do
piloto em `token_usage` dá o número real por projeto/mês, e é ele que
deve entrar na margem do produto.

---

## 12. Ambientes, CI/CD e deploy

| Ambiente | Dados | Deploy |
|---|---|---|
| `local` | Supabase CLI (docker) + seeds | `make dev` |
| `staging` | Branch Supabase (`create_branch`) | push em `main` do backend |
| `prod` | `manta-maestro-v5` | tag `portal-vX.Y.Z` + aprovação MN |

Pipeline (GitHub Actions):

```
lint (ruff, black --check) → typecheck (mypy) → testes (pytest)
  → testes de RLS → migração dry-run (supabase db diff)
  → build de imagem → deploy staging → smoke E2E
  → [gate humano MN] → deploy prod → smoke + rollback automático
```

Migrações: uma pasta por versão, `up` sempre transacional, `down`
documentado no arquivo (padrão já adotado em
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`).

---

## 13. Estratégia de testes

| Camada | O que cobre | Meta |
|---|---|---|
| Unitário | Regras de negócio, parsers, router determinístico | ≥ 80% nas regras |
| **RLS** | Tenant A não lê/escreve dado de tenant B — **por tabela** | 100% das tabelas |
| Contrato | Schema OpenAPI × respostas reais (`schemathesis`) | 100% das rotas |
| Integração | Fluxos com Postgres real (testcontainers) | Fluxos críticos |
| Roteamento IA | `tests/routing/prompts.md` — ≥ 90% no agente esperado | 90% |
| Guardrail | Casos-semente de norma/lei/SICRO falsos são pegos | 100% dos casos |
| Carga | 50 usuários simultâneos, 10 runs de IA em paralelo | SLO §11.2 |

A suíte de RLS é o teste que não pode faltar: é a diferença entre um
produto multi-tenant e um vazamento de dados de cliente.

---

## 14. Roadmap por fases

Estimativa para **1 dev backend sênior + 0,5 dev** (ajustar conforme
alocação real).

| Fase | Entrega | Semanas |
|---|---|---|
| **F0 — Fundação** | Repo `backends/portal/`, schemas `portal_*`, RLS, Auth (Entra ID), CI, staging, `/healthz` | 2 |
| **F1 — Docs + RAG** | Ingestão SP, Storage, parsers PDF/XLSX, `/v1/documents`, `/v1/search`, filtro de tenant no RAG | 3 |
| **F2 — Assistente IA** | `/v1/ai/*`, streaming SSE, tool calls via MCP do hub, `aluci-guard`, `token_usage`, teto de custo | 3 |
| **F3 — Cronograma + Custos** | Import XER/MSP, CPM, curva S, orçamento, SICRO, medições, fluxo de caixa | 3 |
| **F4 — Claims + Contratos** | Janelas, eventos, nexo, quantum, contratos e aditivos, exportações | 2 |
| **F5 — Dashboard/Ficha + hardening** | Read models, alertas, observabilidade, carga, `security-review`, piloto com 1 cliente | 2 |
| | **Total** | **15** |

Marcos de valor antecipado: ao fim de **F2** o Portal já é demonstrável
para cliente (docs + assistente com citações). F3–F4 é o que o
diferencia de um chat genérico.

---

## 15. Riscos e decisões pendentes

### 15.1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-01 | Taxonomia divergente entre canônico v5.0 (`A*/S*`) e produção (`03-S*`, `M*`) | Alto — routing e RAG inconsistentes | Reconciliar **antes** de F2; o Portal lê a taxonomia de uma tabela única, não de constantes |
| R-02 | RAG sem `tenant_id` hoje | Crítico — vazamento entre clientes | Migração de coluna + backfill é pré-requisito de F1; sem isso, nenhum tenant externo entra |
| R-03 | Custo de LLM sem teto | Médio-alto | Teto por tenant + medição desde o dia 1 (§7.4) |
| R-04 | `sharepoint-write-mcp-server` não implantado | Baixo para o backend | Ingestão só precisa de leitura; escrita fica em backlog |
| R-05 | KE-068 (barragens) com erro factual confirmado | Médio | Excluir da recuperação por flag até correção |
| R-06 | Um único dev com contexto do stack | Alto | ADRs neste documento + testes de contrato como documentação executável |
| R-07 | Single point of failure na VPS | Médio | Health checks + restart automático; avaliar segundo nó quando houver cliente externo em produção |

### 15.2. Decisões que dependem de MN

1. **Multi-tenant desde o dia 1** (§1.2) — confirmar. Se a decisão for
   "só uso interno por 12 meses", F0 encolhe ~1 semana, mas o retrabalho
   depois é maior.
2. **Cluster compartilhado × projeto Supabase dedicado por cliente**
   (ADR-02) — confirmar se algum contrato em negociação exige
   isolamento físico.
3. **Repositório**: `backends/portal/` dentro de `manta-hub` (proposto)
   ou repo novo `manta-portal-api`.
4. **Prioridade dos módulos**: o roadmap assume Docs+IA antes de
   Cronograma/Custos. Se o piloto for um cliente de claims, inverter
   F3/F4.
5. **Escopo do piloto**: qual projeto/segmento entra primeiro (define
   quais parsers priorizar).

---

## Changelog

- **v1.0** (2026-08-20) — versão inicial. Arquitetura, modelo de dados,
  contrato de API, pipeline de IA, segurança, roadmap 15 semanas.
