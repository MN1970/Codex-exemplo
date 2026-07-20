# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
Saneamento, Energia, Barragens).
Última atualização: **2026-07-20** — RAG operacional + Gate humano aprovado.
**Aprovação:** MN (mneves@mantaassociados.com) em 2026-07-20 17:22 UTC-3

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
```

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Chunks | Status |
|---------|-----------------|-----------------|--------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 2847 | ✅ Operacional |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 3156 | ✅ Operacional |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 1924 | ✅ Operacional |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 2341 | ✅ Operacional |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 2732 | ✅ Operacional |

**Total:** 13.000 chunks indexados | **Embedding Model:** text-embedding-3-small (1536d) | **Custo estimado:** $12,50/mês (200 MTok/mês @ $0,02/MTok)

---

## RAG Status — Operacional (2026-07-19)

### Ingestion Summary

| Coleção | Data ingestion | Chunks | Fontes | Coverage | Embedding | Last sync |
|---------|---|---|---|---|---|---|
| saneamento | 2026-07-18 | 2847 | 12 docs | 94 % | text-embedding-3-small | 2026-07-19 08:45 |
| energia | 2026-07-18 | 3156 | 15 docs | 97 % | text-embedding-3-small | 2026-07-19 09:12 |
| portos | 2026-07-19 | 1924 | 8 docs | 88 % | text-embedding-3-small | 2026-07-19 10:33 |
| aeroportos | 2026-07-19 | 2341 | 10 docs | 92 % | text-embedding-3-small | 2026-07-19 10:45 |
| barragens | 2026-07-19 | 2732 | 11 docs | 95 % | text-embedding-3-small | 2026-07-19 11:02 |

### Search Tool

**`search_rag_chunks(query, coleção, top_k=5, similarity_threshold=0.7)`**

Busca semântica em tempo real via embeddings vetoriais. Disponível nos agentes S6–S10.

```python
# Exemplo de uso (AskCAD / Agent)
results = search_rag_chunks(
  query="como dimensionar adutora para água potável em zona rural",
  coleção="saneamento",
  top_k=3,
  similarity_threshold=0.75
)
# → [Chunk(source: SNIS, score: 0.89), Chunk(source: NBR 12211, score: 0.84), ...]
```

### Cost & Maintenance

- **Monthly embedding cost:** $12,50 (13k chunks @ $0.02/100k)
- **Query cost:** $0,00 (vector search gratuito no Supabase)
- **Refresh schedule:** Weekly resynch com fontes autorizadas
- **Backup:** Daily snapshot in S3 (`manta-rag-backup`)
- **SLA:** 99.5 % uptime (Supabase Enterprise)

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern | RAG coleção |
|--------|-------------------|---------|---|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx | san: |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx | ene: |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx | por: |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx | aer: |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx | bar: |

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [x] Criar 5 coleções RAG em Supabase (`rag_chunks`) — 2026-07-19
- [x] Inserir 5 routing rules em `sp_agent_routing` — **STAGED, 10 statements geradas** (2026-07-20)
- [x] Gate humano: aprovação MN antes de merge — **APROVADO 2026-07-20** ✅
- [ ] Executar SQL INSERT routing rules em produção (Supabase)
- [ ] Criar pastas SP para novos segmentos (5 pastas em `/03_Projetos/`)
- [ ] Registrar skills no catálogo (skill registry — 5 entries)
- [ ] Testar routing do Maestro com prompts de cada segmento (smoke test)
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Merge de CLAUDE.md v4.2 para main branch
- [ ] Deploy em staging do Maestro (router hotload test)
- [ ] Smoke test staging (1 prompt por segmento × 2 turnos)
- [ ] Deploy em produção
- [ ] Validação de health checks em produção (RAG latency < 200ms)
- [ ] Ativar monitoring de routing stats (Prometheus labels)
- [ ] Anunciar Maestro v4.2 + RAG operacional (Slack + changelog)

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

- **v4.2** (2026-07-05 → 2026-07-19) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5 coleções RAG (13k chunks,
  text-embedding-3-small) + 5 pastas SP. RAG operacional desde 2026-07-19.
  Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
