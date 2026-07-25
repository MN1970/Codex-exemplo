# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
Saneamento, Energia, Barragens).

---

## MAPA COMPLETO DE AGENTES — 22 agentes, 2 eixos (taxonomia unificada v5.0)

**STATUS RECONCILIAÇÃO:** v4.2 → v5.0 (2026-07-25) — taxonomia unificada, nomenclatura consolidada, 03-S* → S*.

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| M00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| M01 | claims | claims, manta-claims, 02-C | Opus | ✅ Operacional |
| M02 | contratual | contratual, manta-02 | Sonnet | ✅ Operacional |
| M03 | bd | business-dev, manta-13 | Sonnet | ✅ Operacional |
| M04 | imobiliario | imobiliario, manta-04 | Sonnet | ✅ Operacional |
| M05 | orcamento | orcamento, manta-05 | Sonnet | ✅ Operacional |
| M06 | modelagem | modelagem, manta-06 | Sonnet/Opus | ✅ Operacional |
| M07 | cronograma | cronograma, manta-07 | Sonnet | ✅ Operacional |
| M08 | advisory | advisory, manta-advisory | Sonnet/Opus | ✅ Operacional |
| M09 | arquiteto-ia | arquiteto-ia, manta-arquiteto | Opus | ✅ Operacional |
| M10 | apresentacoes | apresentacoes, manta-14-pptx | Sonnet | ✅ Operacional |

### Eixo 2 — Setoriais (especializados por segmento)

| Código | Segmento | Agente | Status | Knowledge |
|--------|----------|--------|--------|-----------|
| S01 | Rodovias | agente-rodovias | ✅ Operacional | ✅ 9 KEs |
| S02 | OAE (pontes, viadutos) | agente-oae | ✅ Operacional | ✅ 5 KEs |
| S03 | Ferrovia | agente-ferrovia | ✅ Operacional | ⚠️ 5 KEs não-vetorizados |
| S04 | Metrô | agente-metro | ✅ Operacional | ✅ 5 KEs |
| S05 | Túneis | (coberto por S02/S04) | ⚡ Parcial | — |
| S06 | Portos | agente-portos | 🆕 2026-07-05 | ⚠️ 0 KEs |
| S07 | Aeroportos | agente-aeroportos | 🆕 2026-07-05 | ⚠️ 0 KEs |
| S08 | Saneamento | agente-saneamento | 🆕 2026-07-05 — **PRIORIDADE AySA** | ✅ 7 KEs |
| S09 | Energia | agente-energia | 🆕 2026-07-05 — ANEEL/State Grid | ⚠️ 5 KEs não-vetorizados |
| S10 | Barragens | agente-barragens | 🆕 2026-07-05 | ⚠️ 5 KEs não-vetorizados |

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

## ROUTING — Maestro (M00)

Regra de roteamento unificada com nomenclatura v5.0:

```
# Setores prioritários (novos + conhecimento vetorizado)
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → S08 (agente-saneamento) — PRIORIDADE AySA

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → S09 (agente-energia) — ANEEL/State Grid

# Infraestrutura clássica (operacional desde v4.0)
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → S01 (agente-rodovias)

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário|pré-moldado
   → S02 (agente-oae)

IF menção a ferrovia|trilho|AMV|dormente|via permanente|CPTM|Supervia
   → S03 (agente-ferrovia)

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT|transporte de massa
   → S04 (agente-metro)

# Portos, aeroportos, barragens (novos, sem conhecimento ainda)
IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → S06 (agente-portos) — conhecimento em construção

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → S07 (agente-aeroportos) — conhecimento em construção

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → S10 (agente-barragens) — conhecimento em construção
```

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

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

---

## DEPLOY CHECKLIST v5.0 (Reconciliação)

### Fase 1 — Unified Taxonomy
- [x] Criar `pk_agentes.json` (unified primary key mapping)
- [x] Atualizar CLAUDE.md com nova nomenclatura (03-S* → S*, Manta XX → MXX)
- [ ] Auditar divergências: database vs skills map vs CLAUDE.md
- [ ] Criar `RECONCILIACAO.md` (audit report + ações pendentes)

### Fase 2 — Migrate Database Schema
- [ ] Executar `2026_07_25_v5_0_reconciliation.sql` em Supabase
  - Rename `03-S*` → `S*` em `manta_agent_capabilities`
  - Remove guards (aluci-guard, consist-guard, context-guardian) da tabela agentes
  - Resolver colisão Manta 15 (M08 advisory + M09 arquiteto-ia)
- [ ] Update `sp_agent_routing` com novos agent_ids (S01-S10)
- [ ] Update `maestro_routing_keywords` com novos agent_ids

### Fase 3 — Update Agent .md Files
- [ ] Atualizar frontmatter nos agentes setoriais (incluir agent_id unificado)
- [ ] Atualizar agent names em `description` (03-S* → S*)

### Fase 4 — Skills Registry
- [ ] Move guards para skills table (se existir separada)
- [ ] Registrar skills (aluci-guard, consist-guard, context-guardian) em registry

### Fase 5 — Validation & Testing
- [ ] Executar routing tests contra Maestro com novos agent_ids
- [ ] Verificar cobertura de conhecimento (KEs) por agente
- [ ] Testar RolePickerAgent com novas rotas

### Fase 6 — Documentation & Sign-off
- [ ] Atualizar docs (ARQUITETURA-AGENTES-IA.md, runbooks SP)
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry v5.0)
├── pk_agentes.json                   # 🆕 Unified primary key mapping (v5.0)
├── RECONCILIACAO.md                  # 🆕 Audit report da migração 4.2→5.0
├── supabase/
│   └── migrations/
│       ├── 2026_07_05_v4_2_agents_s6_s10.sql   # v4.2 — RAG + routing
│       └── 2026_07_25_v5_0_reconciliation.sql  # 🆕 v5.0 — rename 03-S* → S*
└── .claude/
    └── agents/
        ├── agente-rodovias.md        # S01 — operacional
        ├── agente-oae.md             # S02 — operacional
        ├── agente-ferrovia.md        # S03 — operacional
        ├── agente-metro.md           # S04 — operacional
        ├── agente-portos.md          # S06 — novo (2026-07-05)
        ├── agente-aeroportos.md      # S07 — novo (2026-07-05)
        ├── agente-saneamento.md      # S08 — novo (2026-07-05), PRIORIDADE AySA
        ├── agente-energia.md         # S09 — novo (2026-07-05)
        └── agente-barragens.md       # S10 — novo (2026-07-05)
```

Os agentes horizontais (M00-M10) e a lógica do Maestro vivem no
repositório operacional. Este repositório (`Codex-exemplo`) é a
referência canônica para: (1) agentes setoriais (S01-S10), (2) routing
rules, (3) unified taxonomy v5.0 em `pk_agentes.json`.

---

## Histórico de versões

- **v5.0** (2026-07-25) — Reconciliação: taxonomia unificada, 03-S* → S*, guards removidos de agentes, colisão Manta 15 resolvida. Ticket: MNT-2026-AGENT-RECONCILIATION.
- **v4.2** (2026-07-05) — Expansão S6–S10 (Portos, Aeroportos, Saneamento, Energia, Barragens). 5 novos agentes verticais + 5 coleções RAG. Ticket: MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
