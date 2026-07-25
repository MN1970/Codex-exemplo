# Manta Maestro v5.0.0 — Master Roadmap
## Expansão de 20 para 60 Agentes + RAG + Orchestração em Paralelo

**Projeto:** MN1970/Codex-exemplo  
**Branch:** claude/sharepoint-manta-maestro-5-tahryk  
**Timeline Total:** 2-3 semanas  
**Status:** Phase 1 ✅ Complete — Phase 2-5 ⏳ Planned  

---

## 🎯 Visão Geral do Projeto

Manta Maestro é um sistema distribuído de **60 agentes IA especializados** para otimizar projetos de infraestrutura em 9 segmentos setoriais (rodovia, OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens).

### Arquitetura de 3 Eixos

```
┌─────────────────────────────────────────────────────────┐
│              MAESTRO ROUTER (Manta 00)                  │
│         Intake + Roteamento Semântico Inteligente      │
└─────────────┬───────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │                                                   │
              ▼                                                   ▼
    ┌──────────────────────┐                    ┌──────────────────────┐
    │  11 AGENTES HORIZ.   │                    │  9 AGENTES VERTICAIS │
    │  (Transversais)      │                    │  (Por Segmento)      │
    ├──────────────────────┤                    ├──────────────────────┤
    │ • maestro (00)       │                    │ • S1: Rodovia        │
    │ • claims (01)        │                    │ • S2: OAE            │
    │ • contratual (02)    │                    │ • S3: Ferrovia       │
    │ • imobiliário (04)   │                    │ • S4: Metrô          │
    │ • orçamento (05)     │                    │ • S6: Portos 🆕      │
    │ • modelagem (06)     │                    │ • S7: Aeroportos 🆕  │
    │ • cronograma (07)    │                    │ • S8: Saneamento 🆕  │
    │ • bd (13)            │                    │ • S9: Energia 🆕     │
    │ • apresentações (14) │                    │ • S10: Barragens 🆕  │
    │ • advisory (15)      │                    │                      │
    │ • arquiteto-ia (16)  │                    │    +40 SUB-AGENTES   │
    └──────────────────────┘                    │  (8 por segmento × 5)│
                                                 │  Especializados em   │
                                                 │  8 fases do ciclo    │
                                                 └──────────────────────┘
                │                                         │
                └─────────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼────────────┐
                    │  5 RAG COLLECTIONS      │
                    │  (950+ Documentos)      │
                    ├─────────────────────────┤
                    │ • san: Saneamento (200) │
                    │ • ene: Energia (300)    │
                    │ • por: Portos (150)     │
                    │ • aer: Aeroportos (120) │
                    │ • bar: Barragens (180)  │
                    └─────────────────────────┘
```

---

## 📅 Fases do Projeto

### FASE 1: ✅ COMPLETA — Arquitetura de 60 Agentes
**Timeline:** Semana 1  
**Status:** Merged PR #17, iniciado PR #18

#### Deliverables
- [x] agents-config-60.json — Definição de 60 agentes com tiers, RAG access, pesos
- [x] Schema Supabase (001_create_rag_and_agents_schema.sql)
  - rag_chunks, agent_knowledge_mapping, agent_execution_log
  - sharepoint_sync_log, rag_collection_status
  - Triggers, índices, dados iniciais
- [x] maestro-parallel.sh — Executor paralelo (max 20 agentes simultâneos)
- [x] webhook-sp-to-supabase.sh — Sincronizador SharePoint → Supabase
- [x] Documentação completa
  - README-60-AGENTS.md
  - FASE-1-DEPLOYMENT-CHECKLIST.md

#### Checklist
- [x] 11 Agentes Horizontais definidos
- [x] 9 Agentes Verticais definidos
- [x] 40 Sub-agentes especializados (8 por segmento × 5)
- [x] Schema Supabase com 5 tabelas principais
- [x] Executor paralelo com weighted round-robin
- [x] Webhook com validação aluci-guard
- [x] Commits e push para branch
- [x] PR #18 criado e em review

---

### FASE 2: ⏳ PRÓXIMA — População RAG (950+ Documentos)
**Timeline:** Semana 2  
**Status:** Planejado

#### Objetivos
- [ ] Coletar 950+ documentos de fontes autorizadas
- [ ] Extrair conteúdo (PDFs, DOCXs, etc)
- [ ] Chunkarizar em segmentos de 1000 caracteres
- [ ] Validar com aluci-guard (confidence ≥ 0.85)
- [ ] Inserir em 5 coleções Supabase
- [ ] Testar busca semântica

#### Distribuição de Documentos

| Coleção | Docs | Prioridade | Atualização | Fontes |
|---------|------|-----------|------------|--------|
| san: | 200 | 🔴 ALTA (AYSÁ) | Mensal | SNIS, IWA, NBR, Lei 14.026 |
| ene: | 300 | 🔴 ALTA (ANEEL) | Semanal | ANEEL, EPE R1-R5, ONS, IEEE |
| por: | 150 | 🟡 Média | Semestral | ANTAQ, PIANC, BNDES |
| aer: | 120 | 🟡 Média | Semestral | ANAC, ICAO, FAA |
| bar: | 180 | 🟡 Média | Trimestral | ICOLD, CBDB, SIGBM, Lei 12.334 |

#### Deliverables
- [ ] FASE-2-RAG-POPULATION-PLAN.md (CRIADO)
- [ ] scripts/extract-and-populate-rag.sh
- [ ] 950+ chunks inseridos em Supabase
- [ ] Validação: 95%+ chunks com validation_status = "validated"
- [ ] Testes de busca semântica por coleção
- [ ] Relatório de qualidade (avg confidence_score ≥ 0.88)

---

### FASE 3: ⏳ CONCURRENT — Orchestração Avançada
**Timeline:** Semana 2-3  
**Status:** Planejado (concurrent com Fase 2)

#### Objetivos
- [ ] Load balancing por segmento setorial
- [ ] Fila de prioridades (ALTA > Média > Baixa)
- [ ] Caching distribuído (Redis/Memcached)
- [ ] Métricas em tempo real
- [ ] Failover automático

#### Arquitetura
```
Load Balancing por Segmento:
├─ ALTA (S8, S9): 10 slots (50%)
├─ Média (S6, S7, S10): 8 slots (40%)
└─ Baixa (S1-S4): 2 slots (10%)

Cache Strategy:
├─ Redis key pattern: "{collection}:{query_hash}"
├─ TTL: 1 hora
├─ Max size: 500MB
└─ Expected hit rate: 75-85%

Metrics Collection:
├─ agent_metrics table (executions/min, avg time, success rate)
├─ cache_hit_rate tracking
├─ rag_response_time (p50, p95, p99)
└─ Real-time dashboards
```

#### Deliverables
- [ ] maestro-advanced-orchestration.sh
- [ ] maestro-cache-manager.sh
- [ ] agent_metrics table em Supabase
- [ ] Real-time metrics dashboard (prototipo)
- [ ] Validação: 20 agentes simultâneos com fairness

---

### FASE 4: ⏳ CONCURRENT — Sincronização Automática
**Timeline:** Semana 3  
**Status:** Planejado (concurrent com Fases 2-3)

#### Objetivos
- [ ] Webhooks de change events do SharePoint
- [ ] Cron jobs para sincronização periódica
- [ ] Detecção incremental de mudanças
- [ ] Sincronização bidirecional (SP ↔ Supabase)
- [ ] Rollback automático em caso de erro

#### Arquitetura
```
Webhooks SharePoint:
├─ Endpoint: POST /webhook/sharepoint
├─ Verify signature (HMAC-SHA256)
├─ Extract & validate content (aluci-guard)
├─ Upsert to rag_chunks
└─ Log in sharepoint_sync_log

Cron Schedule:
├─ san: (AYSÁ) — 1º dia cada mês, 00:00 UTC
├─ ene: (ANEEL) — Todo Segunda, 00:00 UTC
├─ por:, aer: — 1º dia a cada 6 meses, 00:00 UTC
└─ bar: — 1º dia a cada 3 meses, 00:00 UTC

Bidirectional Sync:
├─ SP → Supabase: via webhooks + cron
├─ Supabase → SP: via triggers on chunk_updated
└─ Audit trail: quem, quando, o quê, por quê
```

#### Deliverables
- [ ] webhook-sp-change-events.js (Node.js)
- [ ] sync-collection.sh (cron job script)
- [ ] Triggers em Supabase para sync reverso
- [ ] Audit logging completo
- [ ] Validação: <2s latência para webhooks

---

### FASE 5: ⏳ FINAL — Dashboard e Go-live
**Timeline:** Semana 3-4  
**Status:** Planejado

#### Objetivos
- [ ] Dashboard em tempo real (React/Vue)
- [ ] Visualização de 60 agentes
- [ ] Métricas de RAG (hit rate, response time, validation %)
- [ ] Alertas automáticos (Slack)
- [ ] Relatórios de execução (diário/semanal/mensal)
- [ ] Go-live operacional completo

#### Dashboard Components
```
1. Agent Status Grid (20×3)
   └─ Real-time execution status de 60 agentes

2. RAG Collection Status
   └─ Documentos, chunks, validação, cache hit rate

3. Performance Metrics (Last 24 Hours)
   ├─ Executions/hour
   ├─ Avg response time
   ├─ Success rate
   ├─ Cache hit rate
   └─ RAG latency (p99)

4. Alert Panel
   └─ Active alerts com ações recomendadas

5. Reports
   ├─ Daily execution summary
   ├─ Weekly RAG quality report
   └─ Monthly agent performance
```

#### Deliverables
- [ ] Frontend dashboard (React/TypeScript)
- [ ] Backend API (/api/dashboard/snapshot, etc)
- [ ] Slack integration for alerts
- [ ] Report generation templates
- [ ] Monitoring playbook (runbooks)
- [ ] 24/7 operational readiness

---

## 📂 Estrutura de Repositório

```
Codex-exemplo/
├── MASTER-ROADMAP.md                        # Este arquivo
├── README-60-AGENTS.md                      # Visão geral da arquitetura
├── CLAUDE.md                                # Master agent registry
│
├── FASE-1-DEPLOYMENT-CHECKLIST.md           # ✅ COMPLETO
├── FASE-2-RAG-POPULATION-PLAN.md            # ⏳ PLANEJADO
├── FASE-3-4-5-ROADMAP.md                    # ⏳ PLANEJADO
│
├── agents-config-60.json                    # Definição de 60 agentes
│
├── supabase/
│   ├── migrations/
│   │   └── 001_create_rag_and_agents_schema.sql  # Schema v5.0.0
│   └── seed.sql                             # (future) dados iniciais
│
├── scripts/
│   ├── maestro-parallel.sh                  # ✅ Executor paralelo
│   ├── webhook-sp-to-supabase.sh            # ✅ Webhook de sync
│   ├── maestro-advanced-orchestration.sh    # ⏳ Load balancing
│   ├── maestro-cache-manager.sh             # ⏳ Caching distribuído
│   ├── webhook-sp-change-events.js          # ⏳ Webhooks Node.js
│   └── sync-collection.sh                   # ⏳ Cron jobs
│
├── dashboard/                               # ⏳ React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├─ AgentStatusGrid.tsx
│   │   │   ├─ RAGCollectionStatus.tsx
│   │   │   ├─ PerformanceMetrics.tsx
│   │   │   └─ AlertPanel.tsx
│   │   └── pages/
│   │       └─ Dashboard.tsx
│   └── package.json
│
├── backend/                                 # ⏳ API backend
│   ├── src/
│   │   ├── routes/
│   │   │   └─ dashboard.js
│   │   └── controllers/
│   │       └─ metricsController.js
│   └── server.js
│
├── .github/
│   ├── workflows/
│   │   ├─ deploy-schema.yml                 # ⏳ Deploy Supabase
│   │   ├─ test-maestro.yml                  # ⏳ Test executor
│   │   └─ populate-rag.yml                  # ⏳ Batch RAG population
│   └── pull_request_template.md
│
└── logs/
    ├── maestro/                             # Logs do executor paralelo
    └── sync/                                # Logs de sincronização
```

---

## 🚀 Como Usar Este Roadmap

### Para Gerente de Projeto
1. Acompanhar progresso via checklist em cada FASE-X.md
2. Monitorar PRs #18 (Fase 1) e subsequentes
3. Alocar recursos para sprint planning (2-3 semanas)
4. Comunicar status para stakeholders semanalmente

### Para Engenheiro
1. Ler MASTER-ROADMAP.md (este arquivo) para contexto
2. Consultar FASE-X específica para detalhes técnicos
3. Executar scripts de Fase 1 e validar
4. Clonar branch: `git checkout claude/sharepoint-manta-maestro-5-tahryk`
5. Implementar Fases 2-5 seguindo planos detalhados

### Para DevOps
1. Deploy Supabase schema (Fase 1): `supabase db push`
2. Configurar variáveis de ambiente (SUPABASE_URL, SUPABASE_KEY, etc)
3. Testar maestro-parallel.sh com simulação
4. Preparar infraestrutura para Fases 3-5 (Redis, webhooks, etc)
5. Setup CI/CD workflows (GitHub Actions)

---

## 📊 Métricas de Sucesso

### Fase 1 ✅
- [x] 60 agentes definidos e configurados
- [x] Schema Supabase com 5 tabelas principais
- [x] Executor paralelo com 20 slots simultâneos
- [x] Webhook com validação anti-alucinação
- [x] Documentação completa

### Fase 2 ⏳
- [ ] 950+ documentos coletados e inseridos
- [ ] 99.7%+ chunks validados (947/950)
- [ ] Avg confidence_score ≥ 0.88 por coleção
- [ ] Busca semântica funcional
- [ ] Performance: <500ms por query

### Fase 3 ⏳
- [ ] 20 agentes simultâneos com fairness
- [ ] Cache hit rate ≥ 75%
- [ ] Load balancing respeitando prioridades
- [ ] Métricas coletadas e visualizadas
- [ ] Failover automático testado

### Fase 4 ⏳
- [ ] Webhooks processam < 2s
- [ ] Sync incremental de documentos
- [ ] Sincronização bidirecional funcional
- [ ] Rollback automático em erro
- [ ] Audit trail completo

### Fase 5 ⏳
- [ ] Dashboard com real-time updates
- [ ] Alertas automáticos (Slack)
- [ ] Relatórios de execução gerados
- [ ] 99.5%+ uptime
- [ ] Zero intervenção manual 24/7

---

## 🔗 Referências Rápidas

| Documento | Propósito | Status |
|-----------|----------|--------|
| [README-60-AGENTS.md](README-60-AGENTS.md) | Visão geral arquitetura | ✅ |
| [FASE-1-DEPLOYMENT-CHECKLIST.md](FASE-1-DEPLOYMENT-CHECKLIST.md) | Validação Fase 1 | ✅ |
| [FASE-2-RAG-POPULATION-PLAN.md](FASE-2-RAG-POPULATION-PLAN.md) | Plano de população RAG | ⏳ |
| [FASE-3-4-5-ROADMAP.md](FASE-3-4-5-ROADMAP.md) | Detalhes Fases 3-5 | ⏳ |
| [agents-config-60.json](agents-config-60.json) | Config de 60 agentes | ✅ |
| [CLAUDE.md](CLAUDE.md) | Master agent registry | ✅ |

---

## 👥 Stakeholders

- **Responsável Técnico:** mneves@mantaassociados.com
- **Sponsors:** AYSÁ (Saneamento), ANEEL (Energia)
- **Equipe:** Pesquisa (coleta docs), DevOps (infra), Eng (implementação)

---

## 📝 Histórico de Versões

- **v5.0.0** (2026-07-22) — Fase 1 completa, Fases 2-5 planejadas
- **v4.2** (2026-07-05) — Expansão S6-S10, 5 agentes verticais adicionados
- **v4.1** (anterior) — 15 agentes (11 horizontais + 4 verticais S1-S4)

---

**Status Atual:** Phase 1 ✅ Complete, PR #18 em review  
**Próximo Marco:** Fase 2 (população RAG) — Semana 2  
**Timeline Total:** 2-3 semanas para go-live completo

