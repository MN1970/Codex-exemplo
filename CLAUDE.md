# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-07-23) — expansão S6–S10 + otimizações de velocidade/tokens.

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
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Portos | agente-portos | ✅ S6 otimizado (2026-07-23) |
| Manta 03-S7 | Aeroportos | agente-aeroportos | ✅ S7 otimizado (2026-07-23) |
| Manta 03-S8 | Saneamento | agente-saneamento | ✅ S8 otimizado — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | ✅ S9 otimizado — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | ✅ S10 otimizado (2026-07-23) |

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

## DEPLOY CHECKLIST v4.3

### v4.2 (Infraestrutura básica — 2026-07-05)
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

### v4.3 (Otimizações — 2026-07-23)
- [x] Adicionar seção "Capacidades de Otimização" aos 5 agentes (S6-S10)
- [x] Criar `OPTIMIZATION-PATTERNS-MANTA.md` (guia consolidado)
- [x] Documentar paralelismo (ThreadPoolExecutor, 5-10 workers)
- [x] Documentar prompt caching (ephemeral, 1h TTL)
- [x] Documentar Batch API (50% desconto para 1K+ reqs)
- [x] Documentar token counting (estimativa antes de enviar)
- [x] Criar benchmark table por agente (Haiku/Sonnet/Opus)
- [ ] Implementar exemplo Python end-to-end (paralelismo + cache)
- [ ] Implementar exemplo TypeScript end-to-end
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                              # este arquivo (master registry)
├── docs/
│   ├── MODEL-SPEEDS-PARALLEL-TOKENS.md    # 🆕 Guia de modelos e velocidades
│   └── OPTIMIZATION-PATTERNS-MANTA.md     # 🆕 Padrões de otimização (v4.3)
└── .claude/
    └── agents/
        ├── agente-portos.md               # ✅ S6 (otimizado v4.3)
        ├── agente-aeroportos.md           # ✅ S7 (otimizado v4.3)
        ├── agente-saneamento.md           # ✅ S8 — prioridade AySA (otimizado v4.3)
        ├── agente-energia.md              # ✅ S9 — ANEEL/State Grid (otimizado v4.3)
        └── agente-barragens.md            # ✅ S10 (otimizado v4.3)
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.3** (2026-07-23) — Otimizações de velocidade e tokens. Seção "Capacidades de Otimização" adicionada aos 5 agentes S6-S10. Novo guia `OPTIMIZATION-PATTERNS-MANTA.md` com padrões de paralelismo (ThreadPoolExecutor), prompt caching (ephemeral), Batch API (50% off) e token counting. Benchmarks esperados: 4-5x mais rápido em análises paralelas; 85-90% economia com caching.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
