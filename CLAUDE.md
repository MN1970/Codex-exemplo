# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-08-22) — Eixo 4: allowlist de conectores MCP por
segmento (dados, gráficos, pesquisa) + rotina mensal de descoberta de
conectores.

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

## CONECTORES MCP — Allowlist por segmento (Eixo 4)

Regra geral: cada agente vertical só usa os conectores MCP listados na
allowlist abaixo, mais os generalistas do Eixo 1 (WebSearch, WebFetch,
Read/Grep/Glob/Bash). Para uma necessidade fora da lista, o agente
**sugere** (via `SuggestConnectors` / `SearchMcpRegistry`) e registra o
pedido na Fila de Conectores Pendentes — nunca ativa ou conecta um
serviço novo por conta própria. Aprovação final é sempre gate humano
(MN), conforme o pilar "Auditável" da arquitetura Manta.

| Segmento | Banco de dados | Gráficos / visualização | Pesquisa / dados externos |
|----------|----------------|--------------------------|----------------------------|
| S6 Portos | Supabase (coleção `portos`, RAG `por:`) | Skill `dataviz`, Skill `xlsx` | WebSearch, WebFetch, SharePoint (M365) |
| S7 Aeroportos | Supabase (coleção `aeroportos`, RAG `aer:`) | Skill `dataviz`, Skill `xlsx` | WebSearch, WebFetch, SharePoint (M365) |
| S8 Saneamento | Supabase (coleção `saneamento`, RAG `san:`) | Skill `dataviz`, Skill `xlsx` | WebSearch, WebFetch, SharePoint (M365) |
| S9 Energia | Supabase (coleção `energia`, RAG `ene:`) | Skill `dataviz`, Skill `xlsx` | WebSearch, WebFetch, SharePoint (M365) |
| S10 Barragens | Supabase (coleção `barragens`, RAG `bar:`) | Skill `dataviz`, Skill `xlsx` | WebSearch, WebFetch, SharePoint (M365) |

Notas:
- Acesso a Supabase é **somente leitura** (`list_tables`, `execute_sql`
  em modo consulta, `search_docs`) — nenhum agente vertical tem
  permissão de escrita/migração no banco; alterações de schema ficam
  com Manta 16 (arquiteto-ia).
- Skills de visualização/planilha (`dataviz`, `xlsx`) são invocadas via
  tool `Skill`, já adicionada ao frontmatter dos 5 agent.md dos
  segmentos S6-S10.
- SharePoint (M365) usa os caminhos já mapeados na tabela de routing
  acima (`03_Projetos/<Segmento>/*`).

### Fila de Conectores Pendentes

_(vazia — populada pela rotina mensal `manta-connector-scan` abaixo, ou
por pedido explícito de um agente vertical. Toda entrada precisa de
aprovação humana MN antes de entrar na allowlist.)_

| Data | Segmento | Conector sugerido | Motivo | Status |
|------|----------|--------------------|--------|--------|
| — | — | — | — | — |

### Rotina mensal — `manta-connector-scan`

- **Frequência**: mensal, 1º dia útil às 07h (America/Sao_Paulo).
- **Entrada**: allowlist atual (tabela acima) + resumo dos trabalhos em
  execução por segmento (sessões recentes, tickets MNT-*, itens do
  Deploy Checklist).
- **Ação**: para cada segmento ativo, consultar `SuggestConnectors` /
  `SearchMcpRegistry` com o contexto do trabalho e comparar contra a
  allowlist atual.
- **Saída**: proposta em Markdown adicionada à Fila de Conectores
  Pendentes desta seção (PR de atualização do CLAUDE.md) — **nunca**
  ativa ou conecta um serviço automaticamente.
- **Gate**: aprovação humana MN antes de qualquer conector sair da
  fila para a allowlist.

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar pastas SP para novos segmentos
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Testar routing do Maestro com prompts de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

## DEPLOY CHECKLIST v4.3

- [x] Adicionar seção "Conectores MCP — Allowlist por segmento" (Eixo 4)
- [x] Adicionar tool `Skill` + conectores Supabase/M365 somente-leitura
      ao frontmatter dos 5 agent.md (S6-S10)
- [x] Criar Routine mensal `manta-connector-scan`
- [ ] Primeira execução da Routine e revisão da Fila de Conectores
      Pendentes por MN
- [ ] Gate humano: aprovação MN antes de qualquer conector sair da fila

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

- **v4.3** (2026-08-22) — Eixo 4: allowlist de conectores MCP por
  segmento (banco de dados, gráficos/visualização, pesquisa) para os
  agentes S6-S10, Fila de Conectores Pendentes com gate humano, e
  Routine mensal `manta-connector-scan` para descobrir atualizações de
  conectores com base nos trabalhos em execução.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
