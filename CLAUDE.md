# CLAUDE.md — Manta Maestro v5 (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.0** (2026-07-20) — RAG híbrido + 30 agentes dinâmicos (matriz S1–S5 × E01–E06) +
workflow engine com detecção de projeto + MCP fallback + orchestração paralela.

---

## MAPA COMPLETO DE AGENTES — 30 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |

### Eixo 2 — Verticais por segmento (5 segmentos × 6 especialistas)

**Matriz dinâmica: 30 agentes**

| Segmento | E01 (Estudo) | E02 (Básico) | E03 (Executivo) | E04 (Obra) | E05 (Operação) | E06 (Encerramento) |
|----------|---|---|---|---|---|---|
| **S1** Rodovias | S1.E01 ✅ | S1.E02 ✅ | S1.E03 ✅ | S1.E04 ✅ | S1.E05 ✅ | S1.E06 🆕 |
| **S2** OAE (pontes) | S2.E01 ✅ | S2.E02 ✅ | S2.E03 ✅ | S2.E04 ✅ | S2.E05 ✅ | S2.E06 🆕 |
| **S3** Ferrovia | S3.E01 ✅ | S3.E02 ✅ | S3.E03 ✅ | S3.E04 ✅ | S3.E05 ✅ | S3.E06 🆕 |
| **S4** Metrô/VLT | S4.E01 ✅ | S4.E02 ✅ | S4.E03 ✅ | S4.E04 ✅ | S4.E05 ✅ | S4.E06 🆕 |
| **S5** Saneamento | S5.E01 🆕 | S5.E02 🆕 | S5.E03 🆕 | S5.E04 🆕 | S5.E05 🆕 | S5.E06 🆕 |

**Status:**
- ✅ Operacional (S1–S4 existentes, reusando lógica por fase)
- 🆕 Criado v5.0 (S5 Saneamento; E06 Encerramento p/ todos; refatoração para dinâmica)

### Eixo 3 — Ciclo de vida (6 fases de especialização)

Matriz dinâmica: cada agente é especialista em UMA fase × UM segmento.

1. **E01** — Estudo prévio / EVTE
2. **E02** — Projeto básico (traçado/layout)
3. **E03** — Projeto executivo (PAP, quantitativo)
4. **E04** — Obra em execução (cronograma, serviços)
5. **E05** — Operação & manutenção (AAD, tarifação, O&M)
6. **E06** — Encerramento / Concessão / Descomissionamento

---

## RAG HÍBRIDO — Maestro v5

Arquitetura tripartite (SQLite local + Redis cache + MCP fallback):

| Camada | Tecnologia | Atualização | Latência | Custo |
|--------|---|---|---|---|
| 1. Cache local | SQLite FTS5 + embeddings | 2x/dia (batch) | <100ms | ~0 |
| 2. Hot reindex | Voyage AI embeddings | 2x/dia (12h apart) | <200ms | $0.01/1M tokens |
| 3. MCP fallback | SharePoint M365 query | On-demand | <2s | JWT bearer |

**Fluxo de retrieval:**
```
Query + Segmento + Fase
  ↓
SQLite FTS5 (keywords) + Redis cache hit?
  ├─ HIT → rerank (Sonnet) → top-2
  └─ MISS → MCP M365 sharepoint_search → INSERT SQLite → rerank
    → top-2 chunks injetados em system prompt do agente S#.E##
```

---

## WORKFLOW ENGINE — Maestro (Manta 00)

Pipeline determinístico: Input → Detect Type → Route → Execute Parallel → Synthesize

1. **Detect Project Type** (metadata .mtp.json)
   - Extrai: segment (S1–S5), phase (E01–E06), estado, projeto_id
2. **NLU Triagem** (Haiku 4.5)
   - Intent classification (orçamento, cronograma, geotecnia, etc.)
   - Agent candidates (1–3 agentes S#.E##)
3. **Route** (determinístico)
   - Segment × Phase → agente específico
   - Intent → fallback para múltiplos agentes (fan-out)
4. **Execute Parallel** (asyncio.gather)
   - 30 agentes max (concorrência adaptativa)
   - RAG inject + system prompt customizado
   - Timeout 60s por agente
5. **Synthesize** (Sonnet 4.6)
   - Merge respostas N agentes → JSON estruturado
   - Audit log em Postgres
   - Cache resultados 24h (Redis)

---

## ROUTING — Maestro v5 (Matriz dinâmica)

Regra de roteamento atualizada para v5 (metadata-driven):

```
# Matriz dinâmica: projeto_metadata.segment × projeto_metadata.phase → agente único

EXEMPLO: projeto BR-365.json contém {segment: "S1", phase: "E03"}
  → ROUTE → S1.E03 (Projeto Executivo de Rodovia)

# Intent-driven routing (quando phase é desconhecida ou agnóstica)

IF intent == "orçamento" E metadata.segment == "S1"
   → FAN-OUT [S1.E03, S1.E04, S1.E05]  # todas as fases que geram orçamento

IF intent == "cronograma" E metadata.segment == "*"
   → FAN-OUT [*.E04, *.E05]  # obra e operação têm cronogramas

IF intent == "geotecnia" E metadata.segment IN ["S2", "S4"]
   → FAN-OUT [S2.E01, S4.E01]  # estudos com geotecnia

# Fallback: unknown segment
IF metadata.segment NOT IN ["S1", "S2", "S3", "S4", "S5"]
   → MAESTRO_TRIAGEM (Haiku 4.5 classifica) → reroute
```

---

## DEPLOYMENT CHECKLIST v5.0 — Fase 1 (RAG Foundation)

### Codex-exemplo (este repo)
- [ ] Criar 30 skill files (`s#-e##.md`) em `.claude/agents/`
- [ ] Atualizar CLAUDE.md com schema v5.0 (✅ feito)
- [ ] Criar `.claude/rules/antipatterns.md`
- [ ] Validar lint de YAML frontmatter (30 agents)
- [ ] PR + merge para `claude/rag-sharepoint-dynamic-workflow-m2ar2b`

### manta-hub (backend)
**Fase 1A — RAG Service** (2–3 semanas)
- [ ] Schema SQLite local (`backends/maestro/data/maestro_rag.db`)
  - sp_documents (FTS5 index)
  - embeddings_cache (Voyage AI 1024d)
  - query_log (auditoria)
- [ ] `rag_service.py` (retrieve + sync + embed)
- [ ] `file_sync_daemon.py` (APScheduler batch sync 2x/dia)
- [ ] `project_detector.py` (metadata .mtp.json parser)
- [ ] Tests + fixtures (20 casobase)

**Fase 1B — Orchestrator** (2–3 semanas)
- [ ] `nlm_classifier.py` (Haiku 4.5 triagem)
- [ ] `workflow_engine.py` (fan-out + synthesize)
- [ ] `routers/query.py` (`POST /api/query`)
- [ ] `agent_invoker.py` (Claude API wrapper)
- [ ] Tests parallelismo (5 agentes concorrentes)

**Fase 1C — Infrastructure** (1 semana)
- [ ] `.env.example` com RAG_*, MCP_*, MAESTRO_*
- [ ] `deploy/maestro-api.service` (systemd)
- [ ] `deploy/nginx-maestro.conf` (reverse proxy)
- [ ] GitHub Actions CI/CD (lint + test)

### Supabase (seed RAG)
- [ ] Criar/verificar 5 coleções `rag_chunks`
- [ ] Upload 100 chunks por segmento (S1–S5)
- [ ] Testar retrieval + embedding similarity

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                                # este arquivo (v5.0)
├── .claude/
│   ├── agents/                              # 30 agentes × skills
│   │   ├── s1-e01-estudo.md
│   │   ├── s1-e02-basico.md
│   │   ├── s1-e03-executivo.md
│   │   ├── s1-e04-obra.md
│   │   ├── s1-e05-operacao.md
│   │   ├── s1-e06-encerramento.md
│   │   ├── s2-e01-estudo.md
│   │   # ... s2-e02 até s2-e06 (OAE)
│   │   # ... s3-e01 até s3-e06 (Ferrovia)
│   │   # ... s4-e01 até s4-e06 (Metrô)
│   │   # ... s5-e01 até s5-e06 (Saneamento)
│   │
│   ├── helpers/
│   │   ├── maestro-router.md               # Orchestrator triagem
│   │   ├── rag-retriever.md                # Embeddings helper
│   │   └── query-synthesizer.md            # Merge final
│   │
│   └── rules/
│       └── antipatterns.md
│
├── backend/ (em manta-hub)
│   └── maestro/
│       ├── rag_service.py               # SQLite + MCP fallback
│       ├── file_sync_daemon.py          # SP sync daemon (APScheduler)
│       ├── project_detector.py          # Metadata parser
│       ├── nlm_classifier.py            # NLU Haiku triagem
│       ├── workflow_engine.py           # Orchestração paralela
│       └── routers/
│           └── query.py                 # POST /api/query
```

Os agentes horizontais (Manta 00, 01, 02, etc.) vivem no repositório
operacional `manta-hub`. Este repositório (`Codex-exemplo`) serve como
referência canônica versionada dos agentes verticais (S#.E##) e do
mapa de routing matricial.

---

## Histórico de versões

- **v5.0** (2026-07-20) — Refatoração para matriz dinâmica (30 agentes:
  5 segmentos × 6 fases). RAG híbrido (SQLite + Redis + MCP). Workflow
  engine com detecção de projeto. Orchestração paralela de agentes.
  Ticket MNT-2026-UPGRADE-RAG-MAESTRO-V5.
- **v4.2** (2026-07-05) — Expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
