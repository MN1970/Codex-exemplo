# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-07-06) — Manta 20 SP Hub v2.0 (evolução do
`agente-sp-indexer` v1.0 para Hub Central SharePoint com modos reativo /
proativo / escrita e alimentação por routing rules).

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos

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
| Manta 20 | sp-hub | manta-20, sp-hub, sp-indexer, sharepoint-hub | Sonnet | 🆕 v4.3 (evolução do sp-indexer v1.0) |

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
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

## ROUTING — Maestro (Manta 00)

Regra de roteamento atualizada para Q1 do intake:

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

# Roteamento p/ o SP Hub (Manta 20, v4.3)
IF menção a SharePoint|SP|indexar|delta|sp_agent_feed|sp_index|
   sp_routing_rules|sharepoint-map|sp_sync_log|MantaBase MCP|
   feed de documentos|roteamento SP|
   OU pedido de busca/leitura/escrita de arquivo no SharePoint
   → agente-sp-hub (Manta 20)
```

---

## SP HUB — Fluxo proativo (Manta 20 v2.0)

O Manta 20 opera em 3 modos e serve como ponto único de entrada/saída SP:

| Modo | Gatilho | Ação |
|------|---------|------|
| **Reativo** | Agente chama `M20.search()` ou `M20.read()` | `search_sp_index` (Supabase FTS pt) → `sharepoint_search` (fallback live) → devolve lista/conteúdo |
| **Proativo** | `daily_index.sh` + `delta_sync.py` detectam doc novo/modificado | Classifica (extensão + pasta + nome) → aplica `sp_routing_rules` → insere em `sp_agent_feed` (status `pending`); se prioridade `alta`, dispara ingest RAG via M18 |
| **Escrita** | Agente chama `M20.write(drive, path, content, metadata)` | PUT Graph API via Zapier → registra em `sp_sync_log` + atualiza `sp_index` |

**Protocolo inter-agente:** `M20.search(query, filters)`,
`M20.feed(agent_code)`, `M20.read(doc_id)`, `M20.write(drive, path, content)`.

**Regras** — R1: paths sanitizados antes de servir a outros agentes;
R7: selo ★☆☆ (busca) / ★★☆ (busca+classif+rota) / ★★★ (+RAG+validação).

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

---

## SHAREPOINT — Routing rules (sp_agent_routing / sp_routing_rules)

**Verticais S6–S10 (v4.2)** — regra por pasta em `sp_agent_routing`:

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

**SP Hub proativo (v4.3)** — 24 regras iniciais em `sp_routing_rules`
(migração `2026_07_06_v4_3_manta20_sphub.sql`) cobrindo:

- Pastas `02_CLIENTE/*/{01_CONTRATO,02_REC,03_PROPOSTA,04_PROJETO,05_MEDICAO,06_CORRESPONDENCIA,07_CRONOGRAMA}` → M1/M2/M3/M4/M7/M8.
- Extensões cross-folder (`.xer/.mpp` → M1+M3, `.dwg/.dxf` → M3+M4, `.ifc` → M4+M6, `.landxml` → M3, `.pdf` → M18).
- Nomes (`SICRO` → M7, `RDO` → M1+M7, `BM` → M7+M1, `TAC` → M1+M2, `PER` → M8+M3, `sondagem` → M4+M10, `batimetria` → M3-S6, `barragem` → M3-S10, `edital` → M8).

---

## DEPLOY CHECKLIST v4.3

- [x] Copiar 5 agent .md dos verticais S6–S10 para `.claude/agents/` (v4.2)
- [x] Criar agente-sp-hub.md em `.claude/agents/` (v4.3)
- [x] Aplicar patch no CLAUDE.md master (Manta 20 + routing SP Hub)
- [x] Implementar `sp_hub/` (Fase 2: delta_sync, classifier, router, feed + Fase 3: rag_bridge, write_gateway) — 36 testes pytest passando
- [x] Runbook operacional em `docs/RUNBOOK-SPHUB-FASE-2-3.md`
- [ ] Aplicar migração `2026_07_06_v4_3_manta20_sphub.sql` no Supabase (cria `sp_agent_feed`, `sp_routing_rules`, semeia 24 rules)
- [ ] Deploy MantaBase MCP no Railway (Fase 1 da spec)
- [ ] Configurar cron `sp_hub/daily_index.sh` + env vars (Fase 2, ver runbook §Fase 2)
- [ ] Ativar RAG bridge (`SP_HUB_RAG_ENDPOINT`) apontando para M18 (Fase 3, ver runbook §Fase 3 RAG)
- [ ] Configurar Zap + `SP_HUB_ZAPIER_WRITE_WEBHOOK` para o gateway de escrita (Fase 3, ver runbook §Fase 3 write)
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/` (inclui `agente-sp-hub/`)
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v2.0.0 → v2.1.0)
- [ ] Validar R7 ★★☆ com M1/M3/M8 (ver runbook §Validação)
- [ ] Validar R7 ★★★ (ciclo E2E doc → RAG → agente responde)
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                                        # este arquivo (master registry, v4.3)
├── pyproject.toml                                   # 🆕 v4.3 (pytest config para sp_hub)
├── docs/
│   ├── MANTA-20-SPHUB-SPEC-v2.0.md                 # 🆕 v4.3 spec canônica Manta 20
│   └── RUNBOOK-SPHUB-FASE-2-3.md                   # 🆕 v4.3 runbook operacional
├── .claude/
│   └── agents/
│       ├── agente-portos.md                        # S6 (v4.2)
│       ├── agente-aeroportos.md                    # S7 (v4.2)
│       ├── agente-saneamento.md                    # S8 (v4.2) — prioridade AySA
│       ├── agente-energia.md                       # S9 (v4.2) — ANEEL/State Grid
│       ├── agente-barragens.md                     # S10 (v4.2)
│       └── agente-sp-hub.md                        # 🆕 Manta 20 (v4.3)
├── sharepoint/
│   └── 01-agentes-fundamentais/
│       ├── agente-portos/…                         # v4.2
│       ├── agente-aeroportos/…                     # v4.2
│       ├── agente-saneamento/…                     # v4.2
│       ├── agente-energia/…                        # v4.2
│       ├── agente-barragens/…                      # v4.2
│       └── agente-sp-hub/                          # 🆕 v4.3
│           ├── SKILL.md
│           └── README.md
├── sp_hub/                                          # 🆕 v4.3 implementação Fases 2 e 3
│   ├── __init__.py
│   ├── models.py                                    # dataclasses + Priority + SyncResult
│   ├── db.py                                        # wrapper Supabase (Protocol para fake em teste)
│   ├── classifier.py                                # (path, name, ext) → doc_type
│   ├── router.py                                    # aplica sp_routing_rules → RoutingDecision
│   ├── feed.py                                      # RoutingDecision → FeedEntry (com R1 sanitize)
│   ├── delta_sync.py                                # entrypoint Fase 2 (python -m sp_hub.delta_sync)
│   ├── rag_bridge.py                                # Fase 3: Noop | Http | Queue bridge → M18
│   ├── write_gateway.py                             # Fase 3: M20.write() → Zapier → Graph API
│   ├── daily_index.sh                               # cron wrapper (sp_indexer + delta_sync)
│   └── README.md
├── tests/
│   └── sp_hub/                                      # 🆕 v4.3 pytest suite (36 testes, offline)
│       ├── conftest.py                              # FakeSupabase in-memory
│       ├── test_classifier.py
│       ├── test_router.py
│       ├── test_feed.py
│       ├── test_delta_sync.py
│       ├── test_rag_bridge.py
│       └── test_write_gateway.py
└── supabase/
    └── migrations/
        ├── 2026_07_05_v4_2_agents_s6_s10.sql       # v4.2
        └── 2026_07_06_v4_3_manta20_sphub.sql       # 🆕 v4.3
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.3** (2026-07-06) — **Manta 20 SP Hub v2.0**. Evolui o
  `agente-sp-indexer` v1.0 de indexador passivo para Hub Central
  SharePoint. 3 modos (reativo/proativo/escrita), protocolo inter-agente
  (`M20.search/feed/read/write`), 2 novas tabelas Supabase
  (`sp_agent_feed`, `sp_routing_rules`) + 24 routing rules iniciais.
  Inclui implementação Python completa em `sp_hub/` (Fase 2: `delta_sync`,
  `classifier`, `router`, `feed`; Fase 3: `rag_bridge`, `write_gateway`),
  cron `daily_index.sh`, 36 testes pytest passando com FakeSupabase
  in-memory, e runbook operacional em `docs/RUNBOOK-SPHUB-FASE-2-3.md`.
  Ticket MANTA-SPHUB-20260706-001.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
