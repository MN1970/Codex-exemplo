# SharePoint Consolidação — Manta Maestro v5.0.1 (Pós-Deployment)

**Data:** 2026-08-02  
**Status:** Consolidação operacional — 17 agentes em produção  
**Anteriormente:** v5.0.0 (2026-07-22, design) → v5.0.1 (2026-08-02, LIVE)

---

## 📋 Resumo Executivo

A v5.0.1 marca a transição de **design para produção operacional**. O deployment Phase 1+2 completou com sucesso em 2026-08-02, ativando **17 agentes ao vivo** (12 horizontais + 5 especializados Phase 2). Este documento:

1. **Mapeia a realidade de produção** ao estrutura SharePoint existente
2. **Identifica quais SKILL.md já estão prontos** para upload (saneamento, energia, portos, aeroportos, barragens) vs propostos (óleo-gás, edificações)
3. **Reconcilia documentação** (v5.0 design → v5.0.1 operacional)
4. **Define ações de atualização imediatas** para SP
5. **Registra decisões pendentes** que afetam routing e organização

---

## 1. ESTADO ATUAL — AGENTES MAPEADOS A SHAREPOINT

### 1.1 Agentes em Produção (12 + 5 Phase 2) — Operacionais Hoje

#### Horizontais (12 agentes)

| Código | Agente | Tier | SKILL.md em SP? | Status Produção |
|--------|--------|------|---|---|
| Manta 00 | maestro (router) | Haiku→Sonnet | ❌ (Router, não tem SKILL SP) | ✅ Live |
| Manta 01 | claims (02-C) | Opus | ❌ Pendente | ✅ Live |
| Manta 02 | contratual | Sonnet | ❌ Pendente | ✅ Live |
| Manta 04 | imobiliário | Sonnet | ❌ Pendente | ✅ Live |
| Manta 05 | orçamento | Sonnet | ❌ Pendente | ✅ Live |
| Manta 06 | modelagem | Sonnet/Opus | ❌ Pendente | ✅ Live |
| Manta 07 | cronograma | Sonnet | ❌ Pendente | ✅ Live |
| Manta 13 | bd (business-dev) | Sonnet | ❌ Pendente | ✅ Live |
| Manta 14 | apresentações | Sonnet | ❌ Pendente | ✅ Live |
| Manta 15 | advisory | Sonnet/Opus | ❌ Pendente | ✅ Live |
| Manta 16 | arquiteto-ia | Opus | ❌ Pendente | ✅ Live |

#### Phase 2 Especializados (5 agentes) — Novos 2026-08-02

| Código | Agente | Responsabilidade | SKILL.md em SP? | Status |
|--------|--------|---|---|---|
| Heartbeat Service | Saúde agentes | Monitor 5-min, graceful fallback | ❌ Serviço interno | ✅ Live |
| RAG Hierarchy | Seleção coleções | 5 coleções, BM25+semantic | ❌ Sistema | ✅ Live |
| Expert Finder | Ranking agentes | Blended scoring, Thompson Sampling | ❌ Sistema | ✅ Live |
| Composition Orchestrator | Orquestração multi-agente | 5 padrões, resource pooling | ❌ Sistema | ✅ Live |
| Observability | Métricas e tracing | OpenTelemetry+Jaeger, 13 métricas | ❌ Sistema | ✅ Live |

#### Verticais (9 agentes) — Operacionais

| Código | Segmento | Agente | SKILL.md em SP? | Pasta SP Destino | Status |
|--------|----------|--------|---|---|---|
| S1 | Rodovias | agente-infraestrutura (S1) | ❌ Pendente | `03_Projetos/Rodovias/` | ✅ Live |
| S2 | OAE | agente-infraestrutura (S2) | ❌ Pendente | `03_Projetos/OAE/` | ✅ Live |
| S3 | Ferrovia | agente-infraestrutura (S3) | ❌ Pendente | `03_Projetos/Ferrovia/` | ✅ Live |
| S4 | Metrô | agente-infraestrutura (S4) | ❌ Pendente | `03_Projetos/Metro/` | ✅ Live |
| S6 | Portos | agente-portos | ✅ **PRONTO** | `01-agentes-fundamentais/agente-portos/` | ✅ Live |
| S7 | Aeroportos | agente-aeroportos | ✅ **PRONTO** | `01-agentes-fundamentais/agente-aeroportos/` | ✅ Live |
| S8 | Saneamento | agente-saneamento | ✅ **PRONTO** ⭐ | `01-agentes-fundamentais/agente-saneamento/` | ✅ Live |
| S9 | Energia | agente-energia | ✅ **PRONTO** | `01-agentes-fundamentais/agente-energia/` | ✅ Live |
| S10 | Barragens | agente-barragens | ✅ **PRONTO** | `01-agentes-fundamentais/agente-barragens/` | ✅ Live |

---

## 2. AGENTES PROPOSTOS (Não Ativados Ainda)

| Código | Segmento | Agente | SKILL.md em repo? | Status | Gate Pendente |
|--------|----------|--------|---|---|---|
| S12 | Óleo & Gás | agente-oleo-gas | ✅ Criado 2026-07-31 | 🔲 Proposto | MN (RAG, routing keywords, SharePoint) |
| S13 | Edificações | agente-edificacoes | ✅ Criado 2026-07-31 | 🔲 Proposto | MN (RAG, routing keywords, SharePoint) |

**Nota:** S11 (Mineração) identificado em `manta_agent_capabilities` (prod), `ativo=true` desde 2026-07-12, mas sem agente `.md`, RAG ou rota SharePoint — formalização candidata para Phase 3 (gap G015).

---

## 3. AÇÕES IMEDIATAS — ATUALIZAR SHAREPOINT

### 3.1 SKILL.md Files Prontos para Upload (5 arquivos)

**Localização atual em repo:** `/sharepoint/01-agentes-fundamentais/agente-{portos,energia,saneamento,aeroportos,barragens}/SKILL.md`

**Ação:** Fazer upload direto para SharePoint usando a estrutura MCP SharePoint (ou via UI):

```
mnassociados.sharepoint.com/sites/Engenharia/
  └── Documentos Compartilhados/
      └── 04_IA/
          └── Manta-Maestro/
              └── 01-agentes-fundamentais/
                  ├── agente-portos/
                  │   └── SKILL.md ← Upload
                  ├── agente-aeroportos/
                  │   └── SKILL.md ← Upload
                  ├── agente-saneamento/
                  │   └── SKILL.md ← Upload ⭐ PRIORIDADE
                  ├── agente-energia/
                  │   └── SKILL.md ← Upload
                  └── agente-barragens/
                      └── SKILL.md ← Upload
```

**Arquivos complementares** (já em pastas de suporte):
- `refs/README.md` (referências e fontes por agente)
- `prompts/starters.md` (exemplos de perguntas iniciais)

**Prioridade:**
1. ⭐ **agente-saneamento** (PRIORIDADE AYSÁ, mais consultas esperadas)
2. **agente-energia** (ANEEL, State Grid — volume alto)
3. **agente-portos** (ANTAQ — consultoria frequente)
4. **agente-barragens** (ICOLD — risco alto)
5. **agente-aeroportos** (ANAC — menor volume, mas completo)

### 3.2 Documentação de Arquitetura — Atualizar para v5.0.1

**Arquivo em repo:**
- `sharepoint/00-arquitetura/INDICE-CANONICAL-v5.0.md` ← **USE ESTE — é o mais completo**

**Ação:** Renomear e publicar no SharePoint como v5.0.1:

```
00-arquitetura/INDICE-CANONICO-v5.0.1-LIVE.md
  (reflectir status "17 agentes em produção desde 2026-08-02")
```

**Seções críticas do INDICE que devem estar em SP:**
- Eixo S (Segmentos): confirma S1-S10 operacionais, S12/S13 propostos, S11 identificado
- Routing rules: padrões de menção para cada agente
- RAG collections: 5 coleções operacionais (san, ene, por, bar, editais)
- Model tiering: Haiku/Sonnet/Opus distribuição
- Gaps abertos: decisões pendentes que afetam operação (embedder, S11/S12/S13, RLS)

### 3.3 Tabela de Roteamento (sp_agent_routing)

**Status:** Tabela Supabase `sp_agent_routing` tem 9 linhas (S1-S10), confirmado por auditoria.

**Ação:** Documentar em SP (nova página ou wiki):

```markdown
# Roteamento de Agentes — Maestro

| Agente | Pasta SharePoint | Palavras-chave de routing | Status |
|--------|---|---|---|
| agente-saneamento | 01-agentes-fundamentais/agente-saneamento/ | saneamento, ETA, ETE, adutora, AySA, Lei 14.026 | ✅ Live |
| agente-energia | 01-agentes-fundamentais/agente-energia/ | transmissão, LT, subestação, ANEEL, ONS | ✅ Live |
| agente-portos | 01-agentes-fundamentais/agente-portos/ | porto, terminal, ANTAQ, dragagem, berço | ✅ Live |
| agente-aeroportos | 01-agentes-fundamentais/agente-aeroportos/ | aeroporto, pista, ANAC, TPS, TECA | ✅ Live |
| agente-barragens | 01-agentes-fundamentais/agente-barragens/ | barragem, CFRD, rejeitos, TSF, ICOLD | ✅ Live |
| (S12) agente-oleo-gas | (a criar) | (inativo até gate) | 🔲 Proposto |
| (S13) agente-edificacoes | (a criar) | (inativo até gate) | 🔲 Proposto |
```

---

## 4. REMAPEAMENTO DE DOCUMENTAÇÃO

### 4.1 Arquivos Desatualizados — Requer Correção

| Arquivo | Problema | Ação |
|---------|----------|------|
| `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` | v3.0.0 — anterior ao v5.0 | Substituir por INDICE-CANONICAL-v5.0.1 |
| `sharepoint/ARQUITETURA-AGENTES-IA-v5.0.0.md` | Design (22 jul) — pré-deployment | Substituir por v5.0.1 (02 ago LIVE) |
| `docs/DISCIPLINAS-D01-D20.md` | Usa numeração S divergente (Convenção B) | Corrigir para Convenção A (S6=Portos…S10=Barragens) |
| `docs/ATIVIDADES-A1-A10.md` | Mesma divergência | Corrigir numeração |

### 4.2 Novos Documentos a Criar em SP

| Documento | Propósito | Público |
|-----------|-----------|---------|
| `MANTA-v5.0.1-DEPLOYMENT-LIVE.md` | Status de produção, 17 agentes live | Interno — MN + DevOps |
| `RAG-COLLECTIONS-GUIDE.md` | 5 coleções (san, ene, por, bar, editais) | Interno — Agentes + Dev |
| `ROUTING-DECISION-TREE.md` | Árvore de decisão Maestro (intake Q1-Q4) | Usuários + Agentes |
| `PHASE-3-ROADMAP.md` | Plan para 9 novos agentes (Manta 17-25) | MN + Leadership |

---

## 5. MAPPING — SHAREPOINT → PRODUÇÃO

### 5.1 Onde Cada Agente Publica Seus Artefatos

```
SharePoint Manta Maestro (principal: /01-agentes-fundamentais/)

├── agente-saneamento/ (S8, ⭐ PRIORIDADE AYSÁ)
│   ├── SKILL.md ← v1.0.0 (2026-07-05)
│   ├── ref/ (SNIS, Lei 14.026, AySA, NBR 12211-12218, IWA)
│   └── prompts/ (15 exemplos de Q1-Q4)
│
├── agente-energia/ (S9, ⭐ ANEEL)
│   ├── SKILL.md ← v1.0.0
│   ├── ref/ (ANEEL, EPE, ONS, IEEE, IEC, R1-R5)
│   └── prompts/ (exemplos transmissão, geração, distribuição)
│
├── agente-portos/ (S6)
│   ├── SKILL.md ← v1.1.0 (2026-07-31)
│   ├── ref/ (ANTAQ, PIANC, ROM)
│   └── prompts/ (dragagem, berços, capacidade)
│
├── agente-aeroportos/ (S7)
│   ├── SKILL.md ← v1.0.0
│   ├── ref/ (ANAC, RBAC 154, ICAO Annex 14, FAA)
│   └── prompts/ (pistas, TPS, balizamento)
│
├── agente-barragens/ (S10)
│   ├── SKILL.md ← v1.0.0
│   ├── ref/ (ICOLD, CBDB, Lei 12.334, NBR 13028)
│   └── prompts/ (CFRD, rejeitos, PAE/PSB)
│
├── 02-agentes-horizontais/ (NOVO — a criar)
│   ├── agente-contratual/
│   │   └── SKILL.md (v pendente)
│   ├── agente-claims/
│   │   └── SKILL.md (v pendente)
│   ├── agente-orcamento/
│   │   └── SKILL.md (v pendente)
│   ├── ... (09 outros)
│   └── agente-arquiteto-ia/
│       └── SKILL.md (v pendente)
│
└── 00-arquitetura/
    ├── INDICE-CANONICO-v5.0.1-LIVE.md ← **NOVA VERSÃO**
    ├── MANTA-v5.0.1-DEPLOYMENT-LIVE.md ← **NOVO**
    ├── RAG-COLLECTIONS-GUIDE.md ← **NOVO**
    ├── ROUTING-DECISION-TREE.md ← **NOVO**
    └── PHASE-3-ROADMAP.md ← **NOVO**
```

### 5.2 Que Dados Vêm Para SP de Supabase

**Tabelas de referência (leitura):**
- `rag_collections` (5 linhas: san, ene, por, bar, editais)
- `sp_agent_routing` (9 linhas: S1-S10 routing rules)
- `maestro_routing_keywords` (50+ palavras-chave por agente)
- `manta_agent_capabilities` (17 agentes, ativo=true para S1-S10)

**Não sincronizamos automaticamente para SP** — apenas leitura via MCP. Atualizações de SKILL.md são feitas manualmente (git + upload SP).

---

## 6. DECISÕES PENDENTES QUE AFETAM SP

### 6.1 Embedder (G010) — Impacta RAG Collections

**Pergunta:** Usar `bge-small-en-v1.5` (384-d) ou `bge-m3` (1024-d)?

**Implicação para SP:**
- Se migrar para bge-m3: documentar em `RAG-COLLECTIONS-GUIDE.md` e atualizar `INDICE-CANONICO`
- Isso afeta documentação de performance (latência cache hits, índice HNSW)

**Status:** Pendente confirmação de embedder real em produção (ver `docs/EMBEDDER-DECISION.md` vs `docs/SUPABASE-PROJECT-AUDIT.md` — contradizem)

### 6.2 S11/S12/S13 — Impacta Numeração de Segmentos em SP

**Pergunta:** Manter Convenção A (S6=Portos…S10=Barragens, novos em S12/S13) ou adotar Convenção B (renumerar)?

**Status:** Convenção A adotada nesta consolidação. S12/S13 criados, pendente gate MN para ativar.

**Ação para SP:** 
- Usar Convenção A em todos os documentos (já está no INDICE)
- Quando S12/S13 forem aprovados: criar pastas `02-agentes-horizontais-propostos/agente-oleo-gas/` e `agente-edificacoes/`
- Até lá, documentar como "Propostos, não despacháveis"

### 6.3 Supabase Security (G012) — RLS em 3 Tabelas

**Achado:** `rag_collections`, `sp_agent_routing`, `maestro_routing_keywords` têm RLS desabilitado.

**Implicação para SP:** Não é um risco de exposição em SP (dados aqui são espelho, não sensível). Mas deve-se documentar em runbook de segurança.

---

## 7. CHECKLIST DE ATUALIZAÇÃO SHAREPOINT

- [ ] **Upload SKILL.md (5 arquivos prontos):**
  - [ ] agente-saneamento/SKILL.md ⭐
  - [ ] agente-energia/SKILL.md
  - [ ] agente-portos/SKILL.md
  - [ ] agente-barragens/SKILL.md
  - [ ] agente-aeroportos/SKILL.md

- [ ] **Criar pasta 02-agentes-horizontais/** em SP (subestrutura para 11 agentes)

- [ ] **Documentação de Arquitetura:**
  - [ ] Publicar INDICE-CANONICO-v5.0.1-LIVE.md (renomear de v5.0.md, adicionar status "LIVE")
  - [ ] Deletar ou arquivar ARQUITETURA-AGENTES-IA-v3.0.0.md e v5.0.0.md (desatualizadas)

- [ ] **Novos Documentos em SP:**
  - [ ] MANTA-v5.0.1-DEPLOYMENT-LIVE.md (status, 17 agentes, observability)
  - [ ] RAG-COLLECTIONS-GUIDE.md (5 coleções, performance, handoff hints)
  - [ ] ROUTING-DECISION-TREE.md (Maestro intake Q1-Q4, exemplos)
  - [ ] PHASE-3-ROADMAP.md (9 novos agentes Manta 17-25, timeline)

- [ ] **Corrigir Numeração em Repo (não SP direto, mas afeta documentação lida a partir de SP):**
  - [ ] `docs/DISCIPLINAS-D01-D20.md` — corrigir Convenção B → A
  - [ ] `docs/ATIVIDADES-A1-A10.md` — corrigir Convenção B → A
  - [ ] `.claude/agents/agente-aeroportos.md` (linha "S1–S11") → "S1–S10"

- [ ] **Tabela de Roteamento:**
  - [ ] Criar wiki/página em SP: "sp_agent_routing" mapping (9 linhas, keywords)

- [ ] **Gates Pendentes (Documentar em SP como "Decisões Abertas"):**
  - [ ] S12/S13 aprovação MN (RAG + routing + SP folder creation)
  - [ ] S11 formalização (gap G015, mesmo processo)
  - [ ] Embedder confirmação (docs divergência)
  - [ ] RLS habilitação (security gate)

---

## 8. CRONOGRAMA SUGERIDO

| Data | Tarefa | Responsável |
|------|--------|---|
| 2026-08-02 (hoje) | Upload 5 SKILL.md prontos | Manta Associados |
| 2026-08-02 | Publicar INDICE-CANONICO-v5.0.1-LIVE.md | MN/DevOps |
| 2026-08-03 | Criar pasta 02-agentes-horizontais/ | DevOps |
| 2026-08-05 | Publicar 4 novos documentos de arquitetura | MN |
| 2026-08-05 | Decisão MN: S12/S13 gate (sim/não/adiar) | MN |
| 2026-08-10 (se S12/S13 aprovado) | Criar RAG + routing keywords + SP folders | Dev |
| 2026-08-31 | Corrigir numeração em `docs/` (Convenção A) | Dev |

---

## 9. REFERÊNCIAS — O QUE ESTÁ ONDE

| Documento | Localização | Versão | Propósito |
|-----------|---|---|---|
| **INDICE-CANONICO** | `/sharepoint/00-arquitetura/INDICE-CANONICAL-v5.0.md` | v5.0 | Source of truth — 4 eixos, routing, gaps |
| **DEPLOYMENT REPORT** | `/DEPLOYMENT-REPORT-v5-0-PRODUCTION.md` | v5.0 | Auditoria live — 17 agentes, 9 migrations, 13 metrics |
| **RAG HIERARCHY GUIDE** | `/docs/README-RAG-HIERARCHY.md` | v1.0 | 5 coleções, performance, test queries |
| **EXECUTE SUMMARY** | `/docs/PHASE-2-SUMMARY.md` | v1.0 | Phase 1+2 deliverables (heartbeat, expert finder, etc.) |
| **Expert Finder** | `/docs/EXPERT-FINDER-v5.0.md` | v1.0 | Algoritmo blended scoring, circuit breaker |
| **SKILL.md Files** | `/sharepoint/01-agentes-fundamentais/agente-{x}/` | v1.0.0 | 5 agentes prontos para upload |
| **Supabase Audit** | `/docs/SUPABASE-PROJECT-AUDIT.md` | v1.0 | Auditoria real — 9 coleções RAG, 204 chunks confirmado |
| **CLAUDE.md Master** | `/CLAUDE.md` | v5.0.1 | Registry master — mantém em sincro com INDICE |

---

## 10. NOTAS DE PROVENIÊNCIA

Esta consolidação v5.0.1 reconcilia:

1. **v5.0.0 (2026-07-22, design):** 20 agentes em código, roteamento estático, documentação de arquitetura incompleta
2. **v5.0 (2026-07-31, investigação):** gaps formalizados (G010, G012, G014, G015), decisões pendentes documentadas, 4 eixos A/F/D linkados
3. **v5.0 (2026-08-02, deployment):** Phase 1+2 completas, 17 agentes LIVE em produção, observability ativa (13 métricas, 5 views), heartbeat + expert finder + composition orchestrator + RAG hierarchy + tracing

**Convergência:** Este documento consolida a realidade de produção (17 agentes operacionais, deployment confirmado) com a estrutura SharePoint (SKILL.md prontos, pastas de agentes, documentação canônica).

---

## 11. PRÓXIMAS FASES

**Phase 3 (Q4 2026, design complete, awaiting MN gate):** 9 novos agentes (Manta 17–25)

- P3-01: Risk & Compliance
- P3-02: Schedule Optimizer
- P3-03: Cost & Budget
- P3-04: ESG & Impact ← Agora operacional (Manta 20, v1.0, 2026-08-02)
- P3-05: Stakeholder Negotiation
- P3-06: Financial Structure
- P3-07: Performance Analytics
- P3-08: Procurement
- P3-09: Knowledge Graph

**Gate:** MN approval + architecture review (Manta 16 — arquiteto-IA)

---

**Preparado por:** Claude Code — Manta Maestro Consolidation  
**Sessão:** Phase 1 + Phase 2 + Deployment orchestration  
**Status:** Pronto para ação — Transferência a SharePoint

