# Manta Maestro — Operação v5.0.0

**Sincronização SharePoint:** 2026-07-27  
**Status:** ✅ Operacional — 20 agentes em produção  
**Última atualização SP:** 2026-07-22 (ARQUITETURA-AGENTES-IA-v5.0.0.md)

---

## Sumário Executivo

Manta Maestro é um **sistema multiagente orquestrado** especializado em infraestrutura. Consolidada em v5.0.0 com:

- **20 agentes operacionais** (11 horizontais + 9 verticais)
- **Router inteligente (Maestro/Manta 00)** com pattern-matching semântico
- **8 fases de ciclo de vida** suportadas por todos os agentes verticais
- **Suporte a 5 segmentos especializados** novos: Portos, Aeroportos, Saneamento, Energia, Barragens
- **RAG integrado** com 950+ documentos em 5 coleções Supabase
- **Consensus voting** para decisões críticas (MAESTRO-OS v6.0)

---

## 1. Arquitetura em 3 Eixos

### Eixo 1: Agentes Horizontais (11)

Transversais a todos os segmentos, cada um com especialidade horizontal:

| ID | Agente | Especialidade | Tier | Status |
|-----|--------|-------------|------|--------|
| 00 | maestro | Router semântico + intake | Haiku→Sonnet | ✅ V5.0 |
| 01 | claims | Sinistros, reclamações, garantias | Opus | ✅ V5.0 |
| 02 | contratual | Contratos, RDC, concorrências | Sonnet | ✅ V5.0 |
| 04 | imobiliário | Propriedades, zoneamento | Sonnet | ✅ V5.0 |
| 05 | orçamento | Custos, SICRO, composições | Sonnet | ✅ V5.0 |
| 06 | modelagem | BIM, FEA, simulação | Sonnet/Opus | ✅ V5.0 |
| 07 | cronograma | Planejamento, sequência | Sonnet | ✅ V5.0 |
| 13 | BD | Pipeline, negociação | Sonnet | ✅ V5.0 |
| 14 | apresentações | Decks, relatórios | Sonnet | ✅ V5.0 |
| 15 | advisory | Estratégia, valor | Sonnet/Opus | ✅ V5.0 |
| 16 | arquiteto-IA | Orquestração, workflows | Opus | ✅ V5.0 |

### Eixo 2: Agentes Verticais (9)

Especializados por segmento de infraestrutura:

**Existentes (S1–S4):**
- **S1 (Rodovia)** — Pavimentação, DNIT, terraplenagem
- **S2 (OAE)** — Pontes, viadutos, estruturas
- **S3 (Ferrovia)** — Via permanente, dormente, sinalização
- **S4 (Metrô)** — Estações, túneis, NATM, PSD

**Novos 🆕 (S6–S10):**
- **S6 (Portos)** — Terminais, berços, dragagem, contêineres (ANTAQ, PIANC)
- **S7 (Aeroportos)** — Pistas, taxiways, TPS, TECA (ANAC, RBAC, ICAO)
- **S8 (Saneamento)** 🔴 **PRIORIDADE AYSÁ** — ETA, ETE, adutoras (SNIS, Lei 14.026)
- **S9 (Energia)** 🔴 **PRIORIDADE ANEEL** — Transmissão (LT), subestações (R1–R5, ONS)
- **S10 (Barragens)** — Barragens, vertedouro, rejeitos (ICOLD, Lei 12.334)

### Eixo 3: Ciclo de Vida (8 fases)

Todos os verticais suportam as 8 fases:
1. **Estudo prévio** — Pré-viabilidade, EVTE
2. **Projeto básico** — Soluções, custos estimados
3. **Projeto executivo** — Detalhes, especificações
4. **Obra em execução** — Supervisão, fiscalização
5. **Operação & Manutenção** — Gestão de ativo
6. **Licitação/Competição** — Edital, RDC, concorrência
7. **Due Diligence / M&A** — Avaliação para transação
8. **Encerramento** — Descomissionamento, desativação

---

## 2. Sistema de Roteamento (Maestro)

Router semântico baseado em **pattern-matching** de menções:

```
S8 (Saneamento)   ← saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem|SNIS
S9 (Energia)      ← transmissão|LT|subestação|ANEEL|RAP|leilão|ONS|EPE
S6 (Portos)       ← porto|terminal|ANTAQ|dragagem|molhe|berço|calado
S7 (Aeroportos)   ← aeroporto|pista|ANAC|RBAC|ICAO|TPS|TECA|balizamento
S10 (Barragens)   ← barragem|vertedouro|CFRD|CCR|rejeitos|TSF|PNSB|ICOLD
S1 (Rodovia)      ← rodovia|pavimento|CBUQ|BGS|SICRO|DNIT
S2 (OAE)          ← ponte|viaduto|OAE|NBR 7187|estrutura|fundação
S3 (Ferrovia)     ← ferrovia|trilho|via permanente|dormente
S4 (Metrô)        ← metrô|estação|NATM|PSD|linha|VLT
```

**Tier escalation:** Haiku (roteamento rápido) → Sonnet (análise) → Opus (decisões críticas)

---

## 3. Retrieval Augmented Generation (RAG)

### Coleções Supabase (950+ docs)

| Coleção | Prefixo | Docs | Fontes |
|---------|---------|------|--------|
| **Saneamento** | san: | 200+ | SNIS, IWA, NBR 12211-12218, Lei 14.026, BNDES |
| **Energia** | ene: | 300+ | ANEEL, EPE (R1–R5), ONS, IEEE, State Grid |
| **Portos** | por: | 150+ | ANTAQ, PIANC, BNDES, editais TUP |
| **Aeroportos** | aer: | 120+ | ANAC/RBAC, ICAO Annex 14, FAA ACs |
| **Barragens** | bar: | 180+ | ICOLD, CBDB, SIGBM, Lei 12.334 |

### Estratégia de Busca

1. **Detecção de segmento** → determina coleção primária
2. **Busca semântica** → top-k documentos (k=5-10)
3. **Ranking por relevância** → ordenação por BM25 + embedding
4. **Integração no contexto** → passagem ao agente com citações

---

## 4. MAESTRO-OS v6.0 — Sistema Técnico

### Camadas Arquiteturais

| Camada | Responsabilidade | Componentes |
|--------|------------------|-------------|
| **Intake** | Recebimento requisições | Maestro router, parsing |
| **Routing** | Despacho para agente | Pattern-matching, heurísticas |
| **Agentes** | Execução especializada | 20 agentes (H + V) |
| **RAG** | Contexto documental | 5 coleções Supabase |
| **Consensus** | Votação em decisões | 3/5 voters (Maestro-OS v6) |
| **Storage** | Persistência | SharePoint + GitHub + Supabase |
| **Output** | Formatação resultados | Docs, relatórios, parecer |

### Consensus Voting (Maestro-OS v6.0)

Para decisões críticas (orçamento, cronograma, risco):

- **Múltiplos agentes votam** em candidatos (3-5 propostas)
- **Threshold:** 3/5 votos para decisão (60% maioria)
- **Escalation:** <60% → revisão humana
- **Rastreabilidade:** Audit trail de cada voto

### ML Routing & Duration Prediction

- **Modelo:** Ensemble (XGBoost + Neural Net)
- **Features:** Tipo projeto, segmentos, complexidade, custo
- **Accuracy:** 75%+ routing, RMSE ±20% duração
- **Retraining:** Quinzenal com traces históricos

---

## 5. Integração com SharePoint

### Estrutura de Pastas

```
04_IA/Manta-Maestro/
├── 00-arquitetura/
│   ├── ARQUITETURA-AGENTES-IA-v5.0.0.md ← Master v5.0
│   ├── MAESTRO-OS-v6-DEVELOPER.md ← Tech guide
│   ├── MAESTRO-OS-v6-API.md ← REST API
│   └── ROUTING-RULES-v5.0.md
│
├── 01-agentes-fundamentais/
│   ├── SKILL.md (11 horizontais)
│   └── [Skill cards]
│
├── 02-agentes-verticais/
│   ├── AGENTE-S6-PORTOS.md
│   ├── AGENTE-S7-AEROPORTOS.md
│   ├── AGENTE-S8-SANEAMENTO.md (⭐ AYSÁ)
│   ├── AGENTE-S9-ENERGIA.md (⭐ ANEEL)
│   └── AGENTE-S10-BARRAGENS.md
│
├── 03-rag-referencias/
│   ├── san/ (200+ docs saneamento)
│   ├── ene/ (300+ docs energia)
│   ├── por/ (150+ docs portos)
│   ├── aer/ (120+ docs aeroportos)
│   └── bar/ (180+ docs barragens)
│
└── 04-operacional/
    ├── INTAKE-PROCESSO-v5.0.md
    ├── ROUTING-LOG-2026.xlsx
    ├── DEPLOYMENT-CHECKLIST-v5.0.md (✅ COMPLETO)
    └── RELEASES-v5.0.md
```

### Routing para SharePoint

| Pasta SP | Agente | Padrão | Prioridade |
|----------|--------|--------|-----------|
| 03_Projetos/Saneamento/* | agente-saneamento (S8) | *.pdf, *.dwg, *.xlsx | 🔴 Alta (AYSÁ) |
| 03_Projetos/Energia/* | agente-energia (S9) | *.pdf, *.dwg, *.xlsx | 🔴 Alta (ANEEL) |
| 03_Projetos/Portos/* | agente-portos (S6) | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Aeroportos/* | agente-aeroportos (S7) | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Barragens/* | agente-barragens (S10) | *.pdf, *.dwg, *.xlsx | 🟡 Média |

---

## 6. Operação & Manutenção

### Health Check

```bash
# Verificar status de agentes
curl https://maestro-api.manta.local/health/agents

# Listar últimas execuções
curl https://maestro-api.manta.local/execution/latest?limit=10

# RAG — verificar índices Supabase
curl https://maestro-api.manta.local/rag/collections/stats
```

### Métricas de Sucesso

- **Routing accuracy:** >75%
- **Consensus convergence:** <15% escalation
- **Average response time:** <5min (horizontais), <10min (verticais)
- **Token efficiency:** <150k tokens/projeto (target)
- **RAG recall:** >0.8 (top-5)

### Escalation Policy

| Cenário | Ação |
|---------|------|
| Consensus <60% | Escalação para MN (humano review) |
| Agent timeout (>30s) | Retry com Sonnet (vs. Haiku) |
| Token budget exceeded | Sumarizar outputs, split em subtarefas |
| RAG recall <0.6 | Complementar com web search |

---

## 7. Roadmap v5.1+ (Q3 2026)

- [ ] Multimodal support (imagens CAD/PDF)
- [ ] Integração com APS/ACC (Autodesk)
- [ ] Prompt caching para projetos recorrentes
- [ ] Fine-tuning per-segment (especialização)
- [ ] Extended consensus (7 voters, weighted voting)
- [ ] Suporte a Português BR + English

---

## Suporte & Manutenção

**Mantido por:** mneves@mantaassociados.com  
**Repositório:** `/Codex-exemplo` (GitHub)  
**Base de conhecimento:** SP `04_IA/Manta-Maestro/`  
**Documentação técnica:** MAESTRO-OS-v6-DEVELOPER.md (SP)

---

**Documento consolidado:** 2026-07-27  
**Validade:** até 2027-07-27 (roadmap v5.1)  
**Assinado:** Manta IA Team
