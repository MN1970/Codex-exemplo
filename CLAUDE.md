# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

**Versão:** **v5.0.1** (2026-07-26) — unificação de v5.0.0 (Drive B) com reconciliação canônica (Drive A). Consolida 20 agentes operacionais, RAG em bge-small-en-v1.5, e numeração S1–S11.

---

## SUMÁRIO EXECUTIVO

- **20 agentes operacionais:** 11 horizontais (atividades A) + 9 verticais (segmentos S1–S4, S6–S11)
- **RAG canonico:** BAAI/bge-small-en-v1.5 (384-d), Supabase pgvector
- **Router (Maestro):** roteamento semântico por padrão de menção
- **Ciclo de vida:** 8 fases suportadas por todos os verticais (estudo prévio → descomissionamento)
- **Integração SharePoint + GitHub:** Drive A canonico, estrutura S.A.D+F

---

## MAPA COMPLETO DE AGENTES — 20 operacionais, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional v5.0 |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional v5.0 |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional v5.0 |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional v5.0 |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional v5.0 |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional v5.0 |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional v5.0 |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional v5.0 |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional v5.0 |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional v5.0 |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional v5.0 |

### Eixo 2 — Verticais por segmento (S1–S11 — numeração canônica)

| Código | Segmento | Agente | Escopo | Status |
|--------|----------|--------|--------|--------|
| Manta 03-S1 | Rodovia | agente-infraestrutura (S1) | Pavimentação, DNIT, SICRO | ✅ Operacional |
| Manta 03-S2 | OAE | agente-infraestrutura (S2) | Pontes, viadutos, NBR 7187 | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | Via permanente, AMV | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | Estações, NATM, PSD | ✅ Operacional |
| Manta 03-S5 | Imobiliário | agente-imobiliario | Incorporação, zoneamento | ⚡ Dedicado |
| Manta 03-S6 | Edificações | agente-edificacoes | Arquitetura, MEP | 🆕 v5.0 |
| Manta 03-S7 | Portos | agente-portos | ANTAQ, dragagem, terminais | 🆕 v5.0 |
| Manta 03-S8 | Aeroportos | agente-aeroportos | ANAC, ICAO, TPS, TECA | 🆕 v5.0 |
| Manta 03-S9 | Saneamento | agente-saneamento | ETA, ETE, Lei 14.026 ⭐ AySA | 🆕 v5.0 |
| Manta 03-S10 | Energia | agente-energia | ANEEL, LT, subestações ⭐ | 🆕 v5.0 |
| Manta 03-S11 | Barragens | agente-barragens | ICOLD, PNSB, rejeitos | 🆕 v5.0 |

**Numeração canônica:**
- S1–S4: infraestrutura linear (rodovia, OAE, ferrovia, metrô)
- S5: imobiliário (propriedades, zoneamento)
- S6: edificações (construções civis)
- S7–S11: novos setores (portos, aeroportos, saneamento, energia, barragens)

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais (S1–S11) suportam trabalho em:
1. Estudo prévio / EVTEA
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção (O&M)
6. Licitação / competição
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## ROUTING — Maestro (Manta 00)

Roteamento semântico por padrão de menção. Numeração canônica S1–S11.

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS|Lei 14.026
   → agente-saneamento (S9) [PRIORIDADE]

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE|PDE|State Grid
   → agente-energia (S10) [PRIORIDADE]

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel|TUP
   → agente-portos (S7)

IF menção a aeroporto|pista pouso|ANAC|RBAC|ICAO|TPS|TECA|balizamento|PAPI|ILS
   → agente-aeroportos (S8)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF|alteamento
   → agente-barragens (S11)

IF menção a edificacao|construcao|arquitetura|estrutura MEP|projeto civil
   → agente-edificacoes (S6)

# Verticais S1–S4 existentes
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura (S1)

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário|fundação
   → agente-infraestrutura (S2)

IF menção a ferrovia|trilho|AMV|dormente|via permanente|sinalização
   → agente-infraestrutura (S3)

IF menção a metrô|estação|NATM|PSD|linha|VLT|tunelaria urbana
   → agente-infraestrutura (S4)
```

---

## RAG — Arquitetura canônica (bge-small-en-v1.5)

**Modelo:** BAAI/bge-small-en-v1.5 (embedding dimension 384)  
**Storage:** Supabase pgvector, tabela `ke_embeddings`, coluna `embedding vector(384)`  
**Status:** Canonizado em 26/07/2026 — 66/66 registros normalizados para nome canônico  
**Decisão:** migracao para bge-m3 (1024-d) foi avaliada em 24/07/2026 e **NÃO APROVADA** (sem ganho comprovado de qualidade de retrieval)

### Coleções documentais e setoriais

| Coleção | Prefixo | Segmento | Fontes | Volume |
|---------|---------|----------|--------|--------|
| Saneamento | san: | S9 | SNIS, IWA, NBR 12211-12218, Lei 14.026, BNDES | 200+ docs |
| Energia | ene: | S10 | ANEEL, EPE (R1-R5, PDE), ONS, IEEE, State Grid | 300+ docs |
| Portos | por: | S7 | ANTAQ, PIANC, BNDES, editais TUP | 150+ docs |
| Aeroportos | aer: | S8 | ANAC/RBAC, ICAO Annex 14, FAA ACs | 120+ docs |
| Barragens | bar: | S11 | ICOLD, CBDB, SIGBM, Lei 12.334 | 180+ docs |

**Coleções gerais:** projetos, composições (SICRO), propostas, contratos, normas técnicas.

---

## INTEGRAÇÃO SHAREPOINT — Estrutura canônica (Drive A)

```
04_IA/Manta-Maestro/                   [Drive A canonico — 26/07/2026]
├── 00-arquitetura/                    [este arquivo + historico v2..v3.2]
│   ├── CLAUDE.md (v5.0.1)
│   ├── manta-maestro-arquitetura-v5.0.md
│   ├── ARQUITETURA-AGENTES-IA-v5.0.0.md
│   ├── RAG_ARQUITETURA_CANONICA.md
│   └── _historico/                    [v2..v3.2]
│
├── 01-segmentos/                      [S1..S11]
├── 02-atividades/                     [A1..A10]
├── 03-funcionais/                     [F1..F9 — RAG em F1-ia/rag-retriever]
├── 04-disciplinas/                    [D01..D20]
├── 05-sub-skills/
├── 06-exemplares/
├── 07-execucoes/
├── 08-rubricas/
├── 09-base-conhecimento/              [referencias + RAG_ARQUITETURA_CANONICA.md]
└── 99-backup/ 99-meta/
```

### SharePoint — Routing para projetos

| Pasta SP | Segmento | Agente | Pattern | Prioridade |
|----------|----------|--------|---------|-----------|
| 03_Projetos/Saneamento/* | S9 | agente-saneamento | *.pdf, *.dwg, *.xlsx | 🔴 ALTA (AySA) |
| 03_Projetos/Energia/* | S10 | agente-energia | *.pdf, *.dwg, *.xlsx | 🔴 ALTA (ANEEL) |
| 03_Projetos/Portos/* | S7 | agente-portos | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Aeroportos/* | S8 | agente-aeroportos | *.pdf, *.dwg, *.xlsx | 🟡 Média |
| 03_Projetos/Barragens/* | S11 | agente-barragens | *.pdf, *.dwg, *.xlsx | 🟡 Média |

---

## DEPLOYMENT CHECKLIST v5.0.1

- [x] Promover arquitetura v5.0 ao Drive A canonico
- [x] Reconciliar numeração de segmentos para S1–S11
- [x] RAG canonico bge-small-en-v1.5 confirmado contra produção (26/07/2026)
- [x] Normalizar coluna `model` em `ke_embeddings` (8 registros divergentes corrigidos)
- [x] R1 aplicada (sem e-mail/nome pessoal/repo pessoal)
- [x] Criar 5 coleções RAG em Supabase
- [x] Inserir 5 routing rules em `sp_agent_routing`
- [x] Criar pastas SP para novos segmentos
- [x] Registrar skills no catálogo
- [x] Testar routing do Maestro com prompts
- [x] Upload dos SKILL.md para SP
- [x] Gate humano: aprovação MN
- [ ] Revisar `RAG_ARQUITETURA_CANONICA.md` para remover menção a bge-m3 como canônico
- [ ] Consolidar histórico de arquitetura (v2..v3.2) em `00-arquitetura/_historico/`

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry v5.0.1)
└── .claude/
    └── agents/
        ├── agente-portos.md          # 🆕 S7
        ├── agente-aeroportos.md      # 🆕 S8
        ├── agente-saneamento.md      # 🆕 S9 — prioridade AySA
        ├── agente-energia.md         # 🆕 S10 — ANEEL/State Grid
        └── agente-barragens.md       # 🆕 S11
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro (interno Manta). Este repositório
(`Codex-exemplo`) serve como referência canônica versionada dos agentes
verticais, matriz S.A.D+F e mapa de routing.

---

## Matriz de referência — S.A.D+F (base arquitetural)

A v5.0 expõe a visão operacional dessa matriz em 3 eixos:

- **Segmentos (S):** o CONTEXTO/cliente — S1–S11
- **Atividades (A):** o QUE se entrega — A1–A10 (claims, contratual, orçamento, modelagem, cronograma, BD, apresentações, advisory, arquiteto-IA)
- **Disciplinas (D) e Funcionais (F):** bibliotecas técnicas e serviços transversais

Detalhes em `00-arquitetura/RAG_ARQUITETURA_CANONICA.md`.

---

## Histórico de versões

- **v5.0.1** (2026-07-26) — **ATUAL**. Unificação de v5.0.0 (Drive B) com reconciliação canônica (Drive A). Numeração S1–S11, RAG bge-small-en-v1.5 (384-d), R1 aplicada. 20 agentes, 8 fases, 5 coleções RAG. Ticket MNT-2026-MAESTRO-UNIFICACAO.
- **v5.0.0** (2026-07-22) — Consolidou S6–S10 (portos, aeroportos, saneamento, energia, barragens). 20 agentes operacionais, router inteligente, suporte a 8 fases, RAG integrado. Origem: arquivo `ARQUITETURA-AGENTES-IA-v5.0.0.md`.
- **v4.2** (2026-07-05) — Expansão S6–S10 com numeração inicial (antes de reconciliação). Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.

---

## Suporte & Manutenção

**Mantido por:** mneves@mantaassociados.com  
**Repositório master:** `/Codex-exemplo` (GitHub)  
**Próximos passos:** v5.1 (Q3 2026) — integração com LLM multimodal

Documento assinado digitalmente.  
**Válido até:** 2027-07-26 (roadmap v5.x)

---

_Manta Maestro · Arquitetura v5.0.1 canônica (Drive A).  
Unificação de v5.0.0 (Drive B) com reconciliação de numeração, RAG canonico e R1.  
Kernel L4 R1–R5. — Manta Associados_
