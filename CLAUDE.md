# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
Saneamento, Energia, Barragens).

**Versão v5.0 (PROTOTIPAGEM)**: CAG (Custom Agent Group) — orquestração
inteligente com ML. Branch: `claude/manta-maestro-cag-ml-8wdrg4`.

---

## MAPA COMPLETO DE AGENTES — 19 agentes, 3 eixos

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

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via intake Q2:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## CAG — Custom Agent Group (v5.0 PROTOTIPAGEM)

### O que é CAG

**CAG** é a próxima geração de roteamento no Maestro — em vez de
**1 agente responder por keywords**, **múltiplos agentes competem em
paralelo** com ML decidindo qual(is) responder melhor.

**Fluxo CAG vs RAG (v4.2):**

| Fase | RAG (v4.2) | CAG (v5.0) |
|------|-----------|-----------|
| **Input** | Query usuário | Query usuário |
| **Classificação** | Keywords determinísticos | ML intent classifier |
| **Seleção** | 1 agente (IF/ELSE) | N agentes (0.6+ score) |
| **Execução** | Sequencial | **Paralelo** |
| **RAG** | Busca docs (sim) | Busca docs (cada agente) |
| **Ranking** | Não tem | LLM judge (sim) |
| **Síntese** | Não | Integrada |
| **Feedback** | Manual (keywords) | Automático (matriz) |

### Componentes CAG

1. **Intent Classifier** (`cag/ml/intent_classifier.py`)
   - Embedding + keywords → P(saneamento), P(energia), etc.
   - Fine-tune contínuo com histórico de queries

2. **Agent Selector** (`cag/ml/intent_classifier.py`)
   - Toma IntentPrediction → seleciona top-N agentes (threshold 0.6+)
   - Exemplo: "ETA+LT" → [agente-saneamento (0.92), agente-energia (0.85)]

3. **Response Ranker** (`cag/orchestrator/response_ranker.py`)
   - Claude-as-a-judge compara N respostas
   - Outputs: relevância, completude, acurácia (0-1.0)

4. **Response Synthesizer** (`cag/orchestrator/response_ranker.py`)
   - Integra top-2 respostas em 1 texto coerente
   - Mantém citações de fontes

### Schema Supabase para CAG

Tabelas criadas em `cag/schemas/cag_schema.sql`:

- `cag_intent_models` — registro de classificadores treinados
- `cag_agent_scores` — matriz de hits/misses por (agent, intent)
- `cag_feedback_logs` — quando usuário marca "útil" ou "não"
- `cag_routing_metrics` — dashboard de acurácia por dia
- `cag_agent_pool` — registro de agentes participantes
- `cag_intent_classes` — mapeamento (intent → agentes)
- `cag_query_cache` — cache de embeddings + predicções

### Implementação em Fases

**Fase 1: Shadow (seu branch — v5.0-alpha)**
- ✅ Schema Supabase pronto
- ✅ Intent Classifier implementado (keyword + semantic)
- ✅ Agent Selector implementado
- ✅ Response Ranker + Synthesizer implementados
- 🚧 Testes com queries reais (histórico)
- 🚧 Fine-tuning do classifier

**Fase 2: Pilot (após merge)**
- ⏳ CAG roda em paralelo com v4.2 (não substitui)
- ⏳ Logs: quando CAG vs v4.2 discordam
- ⏳ Retraining semanal do classifier

**Fase 3: GA (produção)**
- ⏳ CAG é default; v4.2 fallback
- ⏳ Feedback loop contínuo

### Exemplo: Query Ambígua

**Query**: "Estou fazendo um projeto de saneamento com uma subestação de energia.
Qual é a norma de projeto para a ETA e qual impacto na estrutura?"

**RAG v4.2** (sequencial):
```
Maestro: "saneamento" apareceu primeiro → agente-saneamento
Resposta 1: ETA + normas de saneamento (tempo: 4s)
Handoff manual: "vou encaminhar para energia"
Resposta 2: Subestação + normas de energia (tempo: 4s, após resposta 1)
Usuário: vê 2 blocos separados, tem que sintetizar sozinho
Total: 8 segundos
```

**CAG v5.0** (paralelo + rank + síntese):
```
Intent Classifier: P(saneamento)=0.92, P(energia)=0.85 → ambos selecionados
Agente-saneamento + Agente-energia rodam PARALELO (2-3 segundos)
Response Ranker: compara → saneamento (0.92) é primária, energia (0.85) é complementar
Response Synthesizer: integra ambas em 1 resposta coerente
Usuário: resposta única integrada com scoring visível
Total: 5 segundos (-38%)
```

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento atualizada para Q1 do intake. **Nota:** Manta 03-S5 (Túneis) foi consolidado em S2 (OAE) e S4 (Metrô) para eliminar redundância.

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S10)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4
```

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211–12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, EPE Planos Decenais, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [x] Corrigir inconsistências: rubrica órfã S5 removida, formatos unificados
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing` (tabela sp_agent_routing)
- [ ] Criar pastas SP para novos segmentos (03_Projetos/Saneamento, Energia, Portos, Aeroportos, Barragens)
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Testar routing do Maestro com prompts de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # 🆕 S6
        ├── agente-aeroportos.md      # 🆕 S7
        ├── agente-saneamento.md      # 🆕 S8 — prioridade AySA
        ├── agente-energia.md         # 🆕 S9 — ANEEL/State Grid
        └── agente-barragens.md       # 🆕 S10
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
