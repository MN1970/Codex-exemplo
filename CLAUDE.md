# CLAUDE.md — Manta Maestro (Agent Registry & Ecosystem Map)

> **Registro mestre de agentes, routing, RAG e infraestrutura do Manta Maestro.**  
> Este arquivo é a fonte de verdade referenciada por SKILL.md, runbooks operacionais, MCP servers e integração de terceiros.
>
> **Versão:** v4.3 (2026-07-27)  
> **Status:** ✅ Operacional & Documentado  
> **Maintainer:** Claude Code  
> **Ticket:** MNT-2026-KE-EMBEDDINGS-PARALLEL

---

## 📖 Como usar este documento

**Para implementadores:** Use a seção [Routing](#routing--maestro-manta-00) para determinar qual agente chamar e [Ciclo de Vida](#ciclo-de-vida--8-fases-standard) para entender fluxos.

**Para operadores:** Consulte [Matriz de Capacidades](#matriz-de-capacidades-agentes) para saber o que cada agente faz, [Deploy Checklist](#deploy-checklist-v43) para status.

**Para arquitetos:** Leia [Fluxo de Requisição](#fluxo-de-requisição-typical-user-flow) para arquitetura, [Integrações](#integrações--mcp-supabase-sharepoint) para plumbing.

**Para manutenção:** [Histórico](#histórico-de-versões) mostra evolução; [Links & Referências](#links--referências) aponta para documentação detalhada.

---

## 🎯 O que é Manta Maestro

Plataforma de agentes IA especializados para infraestrutura, saneamento, energia, portos, aeroportos e barragens. Cada agente:
- Conhece seu domínio (normas, métodos, custos, cronogramas)
- Busca em RAG contextualizado (5 coleções + 86 Knowledge Extractions)
- Roteia automaticamente via Maestro (Manta 00)
- Integra com Supabase (embeddings, metadata), SharePoint (documentos), MCP (ferramentas externas)

---

## 🗂️ Mapa Completo de Agentes — 20 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais, aplicáveis a qualquer segmento)

| Código | Agente | Aliases | Função | Tier | Status |
|--------|--------|---------|--------|------|--------|
| **Manta 00** | maestro | manta-router, router | Router inteligente (entrada primária) | Haiku→Sonnet | ✅ Operacional |
| **Manta 01** | claims | manta-claims, 02-C | Análise de claims, indenizações, sinistros | Opus | ✅ Operacional |
| **Manta 02** | contratual | manta-02 | Redação contratual, conformidade legal, negociação | Sonnet | ✅ Operacional |
| **Manta 04** | imobiliario | manta-04 | Avaliação imobiliária, zoneamento, propriedades | Sonnet | ✅ Operacional |
| **Manta 05** | orcamento | manta-05 | Orçamentação, custeio, composições SICRO | Sonnet | ✅ Operacional |
| **Manta 06** | modelagem | manta-06 | Modelagem financeira, VPL, TIR, cenários | Sonnet/Opus | ✅ Operacional |
| **Manta 07** | cronograma | manta-07 | Gestão de cronograma, PERT, Gantt, crítico | Sonnet | ✅ Operacional |
| **Manta 13** | bd | manta-13, business-dev | Business development, estratégia, prospecção | Sonnet | ✅ Operacional |
| **Manta 14** | apresentacoes | manta-14-pptx | Design de slides, powerpoint, storytelling visual | Sonnet | ✅ Operacional |
| **Manta 15** | advisory | manta-15 | Consultoria estratégica, roadmap, governança | Sonnet/Opus | ✅ Operacional |
| **Manta 16** | arquiteto-ia | manta-16-arq | Arquitetura de IA/agentes, design de prompts | Opus | ✅ Operacional |

### Eixo 2 — Verticais por segmento de infraestrutura (C3)

| Código | Segmento | Agente | RAG | Foco | Status |
|--------|----------|--------|-----|------|--------|
| **Manta 03-S1** | Rodovias | agente-infraestrutura (S1) | rodovias | Pavimentação, terraplenagem, DNIT, custos | ✅ Operacional |
| **Manta 03-S2** | OAE | agente-infraestrutura (S2) | oae | Pontes, viadutos, NBR 7187, fundações, licitação | ✅ Operacional |
| **Manta 03-S3** | Ferrovia | agente-infraestrutura (S3) | ferrovia | Via permanente, AMV, dormente, superestrutura | ✅ Operacional |
| **Manta 03-S4** | Metrô | agente-infraestrutura (S4) | metro | Estações, NATM, PSD, linha 4/5, sistemas | ✅ Operacional |
| **Manta 03-S5** | Túneis | agente-infraestrutura (S2+S4) | tunnels | Rodoviários (S2) + ferroviários (S4), NATM | ⚡ Parcial |
| **Manta 03-S6** | Portos | agente-portos | portos | ANTAQ, dragagem, berços, container, PIANC | 🆕 v4.2 |
| **Manta 03-S7** | Aeroportos | agente-aeroportos | aeroportos | ANAC, pistas, TPS, TECA, balizamento, ICAO | 🆕 v4.2 |
| **Manta 03-S8** | Saneamento | agente-saneamento | saneamento | ETA/ETE, adução, SNIS, Lei 14.026, AySA | 🆕 v4.2 — **PRIORIDADE** |
| **Manta 03-S9** | Energia | agente-energia | energia | Transmissão LT, ANEEL, RAP, ONS, leilão | 🆕 v4.2 — State Grid |
| **Manta 03-S10** | Barragens | agente-barragens | barragens | CFRD, CCR, rejeitos, Lei 12.334, ICOLD | 🆕 v4.2 |

---

## 🔄 Fluxo de Requisição (Typical User Flow)

```
User Input
   ↓
Manta 00 (Maestro)
   ├─ NLP: detecta segmento (saneamento? energia? rodovia?)
   ├─ Context: extrai fase (estudo prévio? projeto executivo? obra?)
   ├─ Lookup: routing table → agente correto
   └─→ Dispatch → Agente Vertical + Contexto
   
Agente Vertical (Ex: agente-saneamento)
   ├─ Parse: request → estrutura interna
   ├─ RAG: busca em coleção "saneamento" (hybrid search KE + rag_chunks)
   │        └─ match_kes_hybrid (pgvector, cosine similarity)
   ├─ Context: injeta normas SNIS, Lei 14.026, specs de cliente
   ├─ Generate: Claude Sonnet processa + formata resposta
   └─→ Output (laudo, parecer, planejamento, etc.)

Output
   ├─ Salvar em SharePoint (via MCP)
   ├─ Registrar audit em Supabase
   └─→ User
```

---

## 🎯 Ciclo de Vida — 8 fases standard

Todos os agentes verticais suportam 8 fases via intake questionnaire (Q2):

| # | Fase | Agentes | Entrada típica | Output típico |
|---|------|---------|-----------------|---------------|
| **1** | **Estudo prévio / EVTE** | Todos verticais | Descrição do projeto, contexto | Relatório de viabilidade técnica |
| **2** | **Projeto básico** | Todos verticais | Estudos anteriores, restrições | Anteprojeto, dimensionamentos |
| **3** | **Projeto executivo** | Todos verticais | Projeto básico aprovado | Projeto detalhado, desenhos, specs |
| **4** | **Obra em execução** | Todos verticais | Contrato, cronograma, KPIs | Relatórios de progresso, RDOs, mudanças |
| **5** | **Operação & manutenção** | Todos verticais | Obra entregue, manuais | Planos de O&M, KPIs operacionais |
| **6** | **Processo competitivo / licitação** | Manta 02 + vertical | Projeto executivo | Edital, critérios, análise de propostas |
| **7** | **Due diligence / M&A** | Manta 01, 15, 16 | Empresa/ativo para análise | Relatório DD, riscos, valuação |
| **8** | **Encerramento / descomissionamento** | Manta 01, 02, vertical | Fim de vida útil, regulatório | Plano de descomissionamento, passivos |

---

## 🗺️ Routing — Maestro (Manta 00) Regras

**Entrada:** texto livre do usuário  
**Output:** agente designado + contexto injetado

### Regras de roteamento (ordem de precedência)

```python
# 1. Saneamento (ETA, ETE, adutora, esgoto, água, AySA, SNIS)
IF "saneamento" OR "ETA" OR "ETE" OR "adutora" OR "esgoto" OR "água" OR "AySA" OR "SNIS"
   → agente-saneamento (S8) [PRIORIDADE AySA]

# 2. Energia (transmissão, LT, ANEEL, RAP, ONS, EPE, leilão)
IF "transmissão" OR "LT" OR "subestação" OR "ANEEL" OR "RAP" OR "ONS" OR "EPE" OR "leilão transmissão"
   → agente-energia (S9) [PRIORIDADE State Grid]

# 3. Portos (ANTAQ, dragagem, molhe, berço, contêiner, granel, hidrovia)
IF "porto" OR "terminal" OR "ANTAQ" OR "dragagem" OR "molhe" OR "berço" OR "contêiner" OR "granel"
   → agente-portos (S6)

# 4. Aeroportos (ANAC, pista, TPS, TECA, balizamento, ICAO)
IF "aeroporto" OR "pista" OR "ANAC" OR "TPS" OR "TECA" OR "balizamento" OR "ICAO"
   → agente-aeroportos (S7)

# 5. Barragens (CFRD, CCR, rejeitos, PNSB, ICOLD, Lei 12.334)
IF "barragem" OR "vertedouro" OR "CFRD" OR "CCR" OR "rejeitos" OR "PNSB" OR "ICOLD"
   → agente-barragens (S10)

# 6. Rodovia (pavimento, CBUQ, BGS, terraplenagem, DNIT, SICRO)
IF "rodovia" OR "pavimento" OR "CBUQ" OR "BGS" OR "terraplenagem" OR "DNIT" OR "SICRO"
   → agente-infraestrutura (S1)

# 7. OAE / Pontes (OAE, ponte, viaduto, NBR 7187, fundação, licitação)
IF "OAE" OR "ponte" OR "viaduto" OR "NBR 7187" OR "fundação" OR "estaqueamento"
   → agente-infraestrutura (S2)

# 8. Ferrovia (ferrovia, trilho, AMV, dormente, superestrutura)
IF "ferrovia" OR "trilho" OR "AMV" OR "dormente" OR "superestrutura"
   → agente-infraestrutura (S3)

# 9. Metrô (metrô, estação, NATM, PSD, linha 4, linha 5, VLT)
IF "metrô" OR "estação" OR "NATM" OR "PSD" OR "linha 4" OR "linha 5" OR "VLT"
   → agente-infraestrutura (S4)

# 10. Fallback: contexto não-verticalizado → horizontais
IF NOT (qualquer acima)
   IF "claim" OR "sinistro" OR "indenização"
      → manta-claims (01)
   ELIF "contrato" OR "legal" OR "compliance" OR "negociação"
      → manta-contratual (02)
   ELIF "orçamento" OR "SICRO" OR "custeio" OR "BDI"
      → manta-orcamento (05)
   ELIF "cronograma" OR "PERT" OR "Gantt" OR "crítico"
      → manta-cronograma (07)
   ELIF "financeiro" OR "VPL" OR "TIR" OR "NPV" OR "modelagem"
      → manta-modelagem (06)
   ELIF "imóvel" OR "zoneamento" OR "avaliação" OR "terreno"
      → manta-imobiliario (04)
   ELIF "apresentação" OR "PowerPoint" OR "slide" OR "visual"
      → manta-apresentacoes (14)
   ELIF "estratégia" OR "roadmap" OR "governança" OR "advisory"
      → manta-advisory (15)
   ELIF "IA" OR "agente" OR "prompt" OR "arquitetura"
      → manta-arquiteto-ia (16)
   ELSE
      → default: manta-maestro (00) [redirecionar com melhor contexto]
```

**Contexto injetado junto com routing:**
- Fase do ciclo de vida (1–8)
- Segmento + RAG coleção
- Tier do modelo (Haiku → Sonnet → Opus) baseado em complexidade
- Normas/leis aplicáveis

---

## 💾 RAG — Coleções em Supabase

**Projeto:** `ogxxgvgtulrbbppshjie`  
**Tabela:** `public.rag_chunks`, `public.ke_embeddings`  
**Retrieval:** `match_kes_hybrid()` (hybrid search: FTS + vector cosine)  
**Modelo:** BAAI/bge-small-en-v1.5 (384d, L2-normalized)

### Coleções por segmento

| Coleção | Tabela | Prefixo | Dimensões | Fontes | Status |
|---------|--------|---------|-----------|--------|--------|
| **saneamento** | rag_chunks | san: | 384 | SNIS, IWA, NBR 12211–12218, Lei 14.026, editais | 🆕 v4.2 |
| **energia** | rag_chunks | ene: | 384 | ANEEL editais, R1–R5 EPE, ONS, IEEE | 🆕 v4.2 |
| **portos** | rag_chunks | por: | 384 | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| **aeroportos** | rag_chunks | aer: | 384 | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| **barragens** | rag_chunks | bar: | 384 | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

### Knowledge Extractions (KE) — Indexação paralela

**Base:** 86 KEs (100% indexadas)  
**Modelo:** `BAAI/bge-small-en-v1.5` (384d, L2-normalized)  
**Retrieval:** vector similarity (`<=>` operator, cosine)

**Infraestrutura:** ✅ v4.3 Operacional
- **Orchestrator:** `scripts/parallel_ke_embeddings_indexer.py`
- **Fluxo:** discovery (SQL) → sharding (Python) → dispatch paralelo (N subagents) → verify (SQL)
- **Regras críticas:**
  - Modelo imutável: `BAAI/bge-small-en-v1.5` (384d) em coluna `embedding`
  - Normalização: L2 (`normalize_embeddings=True`)
  - Conflito: `ON CONFLICT DO NOTHING` (nunca sobrescrever)
  - Auditoria: `chunk_text` = texto completo usado para gerar embedding

**Documentação:**
- Runbook: [PARALLEL_KE_EMBEDDINGS.md](./PARALLEL_KE_EMBEDDINGS.md)
- Quick start: [README_KE_INDEXING.md](./README_KE_INDEXING.md)
- Demo: `scripts/run_ke_indexing_demo.py`

---

## 🔌 Integrações — MCP, Supabase, SharePoint

### MCP Servers (Tool access via Claude Code)

| MCP | Função | Tools | Status |
|-----|--------|-------|--------|
| **Supabase** | RAG, KE embeddings, metadata | execute_sql, apply_migration | ✅ v4.3 |
| **GitHub** | Versioning, PRs, issues | create_pull_request, get_file_contents | ✅ v4.3 |
| **SharePoint** | Documentos, pastas, colabs | upload, download, find, read_document | ✅ v4.2 |
| **Autodesk** | CAD/BIM/Civil 3D | read CAD, extract BIM, convert DXF | ⏳ v4.4 |

### Fluxo de integração típico

```
User Input
   ↓
Manta 00 (decide agente + contexto)
   ↓
Agente Vertical
   ├─ Supabase MCP: busca RAG (match_kes_hybrid)
   ├─ SharePoint MCP: lê desenho/especificação do projeto
   ├─ GitHub MCP: referencia normas publicadas no repo
   └─ (opcional) Autodesk MCP: extrai dados de DWG/RVT
   ↓
Claude (Claude Sonnet/Opus)
   ├─ Processa + gera resposta
   └─ Formata output (laudo, parecer, tabela, etc.)
   ↓
Output Channels
   ├─ Supabase: salva metadata + audit trail
   ├─ SharePoint: arquivo final para cliente
   ├─ GitHub: commitea documentação técnica
   └─ User: retorna resposta formatada
```

---

## 📊 Matriz de Capacidades — Agentes

Qual agente faz o quê? (x = simples, xx = moderado, xxx = especializado)

| Agente | Orçamentação | Cronograma | Contrato | Financeiro | Licitação | Claims | Design |
|--------|--------------|-----------|----------|-----------|-----------|--------|--------|
| **Manta 01** (claims) | — | — | xx | — | — | **xxx** | — |
| **Manta 02** (contratual) | — | — | **xxx** | x | xx | xx | — |
| **Manta 05** (orcamento) | **xxx** | x | — | x | x | — | — |
| **Manta 06** (modelagem) | xx | — | — | **xxx** | x | — | — |
| **Manta 07** (cronograma) | x | **xxx** | — | — | — | — | — |
| **Manta 14** (apresentacoes) | — | — | — | — | — | — | **xxx** |
| **Manta 15** (advisory) | xx | xx | x | xx | xx | x | x |
| **S1–S10** (verticais) | **xxx** | **xxx** | xx | xx | x | — | x |

---

## 📁 Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                                 # 📌 este arquivo (master registry v4.3)
├── MANTA_MAESTRO_v4.3.md                     # Visão geral do ecossistema
├── PARALLEL_KE_EMBEDDINGS.md                 # Runbook de indexação paralela de embeddings
├── README_KE_INDEXING.md                     # Quick start de indexação KE
├── .gitignore                                # Padrão Python/IDE
│
├── .claude/
│   └── agents/
│       ├── agente-portos.md                  # Manta 03-S6
│       ├── agente-aeroportos.md              # Manta 03-S7
│       ├── agente-saneamento.md              # Manta 03-S8 (PRIORIDADE AySA)
│       ├── agente-energia.md                 # Manta 03-S9 (State Grid)
│       └── agente-barragens.md               # Manta 03-S10
│
└── scripts/
    ├── parallel_ke_embeddings_indexer.py     # Orchestrador KE embeddings
    ├── run_ke_indexing_demo.py               # Demo end-to-end
    └── test_sql_generation.py                # Test SQL generation
```

**Este repositório (Codex-exemplo)** serve como:
- 📌 **Source-of-truth** para CLAUDE.md v4.2+
- 📦 **Versionamento canônico** de agentes S6–S10
- ⚙️ **Infraestrutura pronta-para-usar** (scripts KE embeddings)
- 📚 **Documentação detalhada** (runbooks, quick starts)

**Agentes existentes (Manta 00, 01, 02, 04–07, 13–16, S1–S4)** vivem no repositório operacional do Maestro (não incluído aqui).

---

## 🚀 Deploy Checklist v4.3

### ✅ v4.3 (Parallel KE Embeddings) — **COMPLETO**
- [x] Implementar `KeIndexerOrchestrator` (discovery, sharding, dispatch, verify)
- [x] Demo end-to-end com dados fictícios
- [x] Test de geração SQL
- [x] Runbook técnico + quick start
- [x] 86 KEs verificadas (100% indexadas)
- [x] Atualizar CLAUDE.md master (RAG — Knowledge Extractions)
- [x] Documentar modelo imutável + regras críticas
- [x] Criar MANTA_MAESTRO_v4.3.md (visão geral)
- [ ] Criar cron/webhook para discovery automático 1x/dia
- [ ] Dashboard de status de indexação (KEs/dia)
- [ ] Integração com aluci-guard para KEs que citam normas/leis

### ⏳ v4.2 (S6–S10) — **EM PROGRESSO**
- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Atualizar CLAUDE.md master (seção Agentes)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing` (SharePoint)
- [ ] Criar pastas SP para novos segmentos (03_Projetos/Saneamento, etc.)
- [ ] Registrar skills no catálogo central (skill registry)
- [ ] Testar routing do Maestro com prompts reais de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge para main

---

## 🔍 Troubleshooting & FAQs

### "Qual agente devo usar para X?"
→ Consulte [Routing](#routing--maestro-manta-00). Se não tiver certeza, comece com Manta 00 (maestro) e ele roteia.

### "Meu agente não encontrou informação no RAG"
→ Verifique:
1. Coleção está carregada? `SELECT COUNT(*) FROM rag_chunks WHERE prefix = 'san:'`
2. KE indexado? `SELECT COUNT(*) FROM ke_embeddings WHERE ke_codigo = 'KE-XXX'`
3. Query em português? Embeddings são PT-BR por padrão.

### "Quero adicionar um novo agente"
→ Siga [Arquitetura de Agentes](./MANTA_MAESTRO_v4.3.md#-arquitetura-v43). Template: `.claude/agents/agente-novo.md`

### "Como integrar com meu sistema?"
→ Use MCP Servers (Supabase, GitHub, SharePoint). Docs em [Integrações](#-integrações--mcp-supabase-sharepoint).

---

## 📞 Links & Referências

### Documentação Principal
- **[CLAUDE.md](./CLAUDE.md)** (este arquivo) — Master registry
- **[MANTA_MAESTRO_v4.3.md](./MANTA_MAESTRO_v4.3.md)** — Visão geral executiva do ecossistema
- **[PARALLEL_KE_EMBEDDINGS.md](./PARALLEL_KE_EMBEDDINGS.md)** — Runbook técnico de indexação KE
- **[README_KE_INDEXING.md](./README_KE_INDEXING.md)** — Quick start

### Agentes (Definições)
- **[agente-saneamento.md](./.claude/agents/agente-saneamento.md)** (S8)
- **[agente-energia.md](./.claude/agents/agente-energia.md)** (S9)
- **[agente-portos.md](./.claude/agents/agente-portos.md)** (S6)
- **[agente-aeroportos.md](./.claude/agents/agente-aeroportos.md)** (S7)
- **[agente-barragens.md](./.claude/agents/agente-barragens.md)** (S10)

### Scripts & Infraestrutura
- **[parallel_ke_embeddings_indexer.py](./scripts/parallel_ke_embeddings_indexer.py)** — Orchestrador principal
- **[run_ke_indexing_demo.py](./scripts/run_ke_indexing_demo.py)** — Demo (rodar para ver em ação)
- **[test_sql_generation.py](./scripts/test_sql_generation.py)** — Test de SQL

### Integração & Deployment
- **[PR #37](https://github.com/MN1970/Codex-exemplo/pull/37)** (Parallel KE Embeddings) — Branch: `claude/parallel-ke-embeddings-index-xdu98y`
- **Supabase Project:** `ogxxgvgtulrbbppshjie` (RAG + KE embeddings)
- **SharePoint:** `03_Projetos/` (Saneamento, Energia, Portos, Aeroportos, Barragens)

---

## 📋 Histórico de versões

- **v4.3** (2026-07-27) — **Parallel KE Embeddings & Ecosystem Map**
  - ✅ Infraestrutura de indexação paralela (discovery → sharding → dispatch → verify)
  - ✅ Orchestrator `KeIndexerOrchestrator` (206 linhas Python)
  - ✅ 86 KEs indexadas (100%), modelo BAAI/bge-small-en-v1.5 (384d, L2-normalized)
  - ✅ CLAUDE.md evoluído para source-of-truth integrado + fluxo de requisição
  - ✅ MANTA_MAESTRO_v4.3.md (visão geral executiva)
  - 📌 Ticket: MNT-2026-KE-EMBEDDINGS-PARALLEL

- **v4.2** (2026-07-05) — **Expansão S6–S10**
  - ✅ 5 novos agentes verticais (Portos, Aeroportos, Saneamento, Energia, Barragens)
  - ✅ 5 coleções RAG + segmento-específico
  - 📌 Ticket: MNT-2026-UPGRADE-AGENTS-S6S10

- **v4.1** (anterior) — **15 agentes (Horizontais + S1–S4)**
  - Baseline: 11 horizontais + 4 verticais (infraestrutura)

---

## 🎯 Próximos passos (Roadmap)

### Esta semana
- [ ] Merge de v4.3 (PR #37) para `main`
- [ ] Publicar MANTA_MAESTRO_v4.3.md para time operacional

### Próximas 2–4 semanas
- [ ] Integração de cron/webhook para discovery automático de KEs (1x/dia)
- [ ] Dashboard de status de indexação (KEs indexadas/día, trending)
- [ ] Integração com aluci-guard (audit de normas/leis em KEs)
- [ ] Completar deploy checklist v4.2 (RAG coleções, routing rules SP)

### Próximas 4–8 semanas (v4.4 Planejado)
- [ ] Integração Autodesk MCP (read CAD, extract BIM, convert DXF)
- [ ] Suporte para migração de modelo (bge-m3, 1024d, nova coluna)
- [ ] Bulk re-indexing (quando descrição de KE muda)

---

**Manta Maestro v4.3 está operacional e pronto para produção.** 🚀

Última atualização: 2026-07-27 | Mantido por: Claude Code | Ticket: MNT-2026-KE-EMBEDDINGS-PARALLEL
