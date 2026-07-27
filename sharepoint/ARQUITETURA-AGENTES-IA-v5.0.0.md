# ARQUITETURA-AGENTES-IA v5.0.0

**Manta Maestro** — Sistema de Agentes IA da Manta Associados

**Versão:** 5.0.0 (2026-07-22)  
**Status:** Operacional  
**Última atualização:** 2026-07-22  
**Mantido por:** mneves@mantaassociados.com

---

## 📋 Sumário Executivo

A v5.0.0 consolida a expansão S6–S10 (Portos, Aeroportos, Saneamento, Energia, Barragens) com:
- **20 agentes operacionais** (11 horizontais + 9 verticais por segmento)
- **5 novos agentes verticais** especializados em infraestrutura setorial
- **Router inteligente (Maestro)** com regras de roteamento por padrão de menção
- **Suporte a 8 fases** de ciclo de vida de projetos
- **RAG integrado** com 5 coleções temáticas em Supabase
- **Integração com SharePoint** e workflows de intake

---

## 1. ARQUITETURA GERAL

### 1.1 Três eixos de organização

**Eixo 1:** Agentes horizontais (11) — maestro, claims, contratual, imobiliário, orçamento, modelagem, cronograma, BD, apresentações, advisory, arquiteto-IA

**Eixo 2:** Agentes verticais (9) — S1-S4 (rodovia, OAE, ferrovia, metrô) + S6-S10 (portos, aeroportos, saneamento, energia, barragens)

**Eixo 3:** Ciclo de vida (8 fases) — estudo prévio, projeto básico, projeto executivo, obra em execução, operação &amp; manutenção, licitação/competição, due diligence, encerramento

### 1.2 Camadas técnicas

| Camada | Responsabilidade | Componentes |
|--------|------------------|-------------|
| **Intake** | Recebimento de requisições | Maestro router, parsing semântico |
| **Routing** | Despacho para agente correto | Regras pattern-matching, heurísticas |
| **Agentes** | Execução de tarefas especializadas | 20 agentes (horizontais + verticais) |
| **RAG** | Contexto temático e documental | 5 coleções Supabase (san:, ene:, por:, aer:, bar:) |
| **Storage** | Persistência e versionamento | SharePoint + GitHub + Supabase |
| **Saída** | Formatação de resultados | Docs, relatórios, parecer técnico |

---

## 2. CATÁLOGO COMPLETO DE AGENTES (20 OPERACIONAIS)

### 2.1 Eixo 1: Agentes Horizontais (11)

| Código | Agente | Especialidade | Tier | Status |
|--------|--------|---------------|------|--------|
| **00** | maestro (router) | Intake + routing semântico | Haiku→Sonnet | ✅ V5.0 |
| **01** | claims | Reclamações / sinistros / garantias | Opus | ✅ V5.0 |
| **02** | contratual | Contratos, RDC, concorrências | Sonnet | ✅ V5.0 |
| **04** | imobiliário | Propriedades, zoneamento, ocupação | Sonnet | ✅ V5.0 |
| **05** | orçamento | Custos, composições, licitação | Sonnet | ✅ V5.0 |
| **06** | modelagem | BIM, análise estrutural, simulação | Sonnet/Opus | ✅ V5.0 |
| **07** | cronograma | Planejamento, sequência, recursos | Sonnet | ✅ V5.0 |
| **13** | BD | Oportunidades, pipeline, negociação | Sonnet | ✅ V5.0 |
| **14** | apresentações | Decks, relatórios executivos, pitch | Sonnet | ✅ V5.0 |
| **15** | advisory | Estratégia, direcionamento, valor | Sonnet/Opus | ✅ V5.0 |
| **16** | arquiteto-IA | Design de workflows, orquestração | Opus | ✅ V5.0 |

### 2.2 Eixo 2: Agentes Verticais (9)

**S1 (Rodovia)** - Pavimentação, terraplenagem, drenagem, DNIT  
**S2 (OAE)** - Estruturas, fundações, cálculo estrutural  
**S3 (Ferrovia)** - Via permanente, sinalização, estações  
**S4 (Metrô)** - Estações, túneis, sistemas, sinalização  
**S6 (Portos)** 🆕 - Terminais, berços, dragagem, contêineres  
**S7 (Aeroportos)** 🆕 - Pistas, taxiways, TPS, TECA, balizamento  
**S8 (Saneamento)** 🆕 ⭐ PRIORIDADE AYSÁ - ETA, ETE, adutoras, distribuição  
**S9 (Energia)** 🆕 ⭐ PRIORIDADE ANEEL - Transmissão (LT), subestações, geração  
**S10 (Barragens)** 🆕 - Barragens, vertedouro, rejeitos, descomissionamento

---

## 3. ROUTING — MAESTRO (MANTA 00)

Roteamento inteligente baseado em padrões de menção:

- **Saneamento (S8):** menção a ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
- **Energia (S9):** menção a transmissão|LT|subestação|ANEEL|RAP|leilão|ONS|EPE
- **Portos (S6):** menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado
- **Aeroportos (S7):** menção a aeroporto|pista|ANAC|RBAC|ICAO|TPS|TECA|balizamento
- **Barragens (S10):** menção a barragem|vertedouro|CFRD|rejeitos|TSF|PNSB|ICOLD
- **Rodovia (S1):** menção a rodovia|pavimento|CBUQ|SICRO|DNIT
- **OAE (S2):** menção a ponte|viaduto|NBR 7187|estrutura|fundação
- **Ferrovia (S3):** menção a ferrovia|trilho|via permanente|dormente
- **Metrô (S4):** menção a metrô|estação|NATM|PSD|linha|VLT

---

## 4. CICLO DE VIDA (8 FASES)

Todos os agentes verticais (S1–S10) suportam trabalho em todas as 8 fases:

1. **Estudo prévio** — Pré-viabilidade, EVTE, conceitual
2. **Projeto básico** — Definição de soluções, custos estimados
3. **Projeto executivo** — Detalhamento completo, especificações
4. **Obra em execução** — Supervisão de implantação, fiscalização
5. **Operação &amp; Manutenção** — Gestão de ativo em funcionamento
6. **Licitação/Competição** — Edital, concorrência, RDC
7. **Due diligence / M&amp;A** — Avaliação para transação
8. **Encerramento** — Descomissionamento, desativação

---

## 5. RETRIEVAL AUGMENTED GENERATION (RAG)

### 5.1 Coleções em Supabase

| Coleção | Prefixo | Volumes | Status |
|---------|---------|---------|--------|
| Saneamento | san: | 200+ docs | ✅ V5.0 |
| Energia | ene: | 300+ docs | ✅ V5.0 |
| Portos | por: | 150+ docs | ✅ V5.0 |
| Aeroportos | aer: | 120+ docs | ✅ V5.0 |
| Barragens | bar: | 180+ docs | ✅ V5.0 |

### 5.2 Fontes iniciais

**Saneamento (san:)** — SNIS, IWA, NBR 12211-12218, Lei 14.026, BNDES  
**Energia (ene:)** — ANEEL, EPE (R1-R5, PDE), ONS, IEEE, State Grid  
**Portos (por:)** — ANTAQ, PIANC, BNDES, editais TUP  
**Aeroportos (aer:)** — ANAC/RBAC, ICAO Annex 14, FAA ACs  
**Barragens (bar:)** — ICOLD, CBDB, SIGBM, Lei 12.334

---

## 6. INTEGRAÇÃO COM SHAREPOINT

### 6.1 Estrutura de pastas

```
04_IA/Manta-Maestro/
├── 00-arquitetura/
│   ├── ARQUITETURA-AGENTES-IA-v5.0.0.md ← Este arquivo
│   ├── ROUTING-RULES-v5.0.md
│   └── CICLO-DE-VIDA-v5.0.md
├── 01-agentes-fundamentais/ [11 SKILL.md]
├── 02-agentes-verticais/ [9 AGENTE.md]
├── 03-rag-referencias/ [5 coleções: san/, ene/, por/, aer/, bar/]
└── 04-operacional/
    ├── INTAKE-PROCESSO-v5.0.md
    ├── ROUTING-LOG-2026.xlsx
    ├── DEPLOYMENT-CHECKLIST-v5.0.md
    └── RELEASES-v5.0.md
```

### 6.2 Routing para SharePoint

| Pasta SP | Agente | Padrão | Prioridade |
|----------|--------|--------|-----------|
| 03_Projetos/Saneamento/* | agente-saneamento (S8) | *.pdf, *.dwg, *.xlsx | 🔴 Alta (AYSÁ) |
| 03_Projetos/Energia/* | agente-energia (S9) | *.pdf, *.dwg, *.xlsx | 🔴 Alta (ANEEL) |
| 03_Projetos/Portos/* | agente-portos (S6) | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Aeroportos/* | agente-aeroportos (S7) | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Barragens/* | agente-barragens (S10) | *.pdf, *.dwg, *.xlsx | 🟡 Média |

---

## 7. DEPLOYMENT CHECKLIST v5.0 (✅ COMPLETO)

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master
- [x] Criar 5 coleções RAG em Supabase ← **NOVO v5.0**
- [x] Inserir 5 routing rules em `sp_agent_routing` ← **NOVO v5.0**
- [x] Criar pastas SP para novos segmentos ← **NOVO v5.0**
- [x] Registrar skills no catálogo (skill registry) ← **NOVO v5.0**
- [x] Testar routing do Maestro com prompts ← **NOVO v5.0**
- [x] Upload dos SKILL.md para SP ← **NOVO v5.0**
- [x] Atualizar ARQUITETURA-AGENTES-IA.md (v1.0.0 → v5.0.0) ← **NOVO v5.0**
- [x] Gate humano: aprovação MN antes de merge ← **APROVADO**

---

## 8. SUPORTE &amp; MANUTENÇÃO

**Mantido por:** mneves@mantaassociados.com  
**Repositório master:** `/Codex-exemplo` (GitHub)  
**Próximos passos:** v5.1 (Q3 2026) — integração com LLM multimodal

---

**Documento assinado digitalmente — ARQUITETURA-AGENTES-IA v5.0.0**  
Gerado: 2026-07-22 | Válido até: 2027-07-22 (roadmap)