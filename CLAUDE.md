# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.0** (2026-08-23) — reconciliação de numeração com
manta-maestro v5.0.1 (adiciona S6-Edificações) + expansão de detalhe
arquitetural (camadas, hub-and-spoke, model tiering, casos ambíguos).

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

Numeração alinhada à v5.0.1 (S1-S5 mantidos; S6 reservado para
Edificações; Portos/Aeroportos/Saneamento/Energia/Barragens
renumerados S6-S10 → S7-S11).

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Edificações | agente-edificacoes | 🆕 Planejado — agente ainda não criado neste repo |
| Manta 03-S7 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S9 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S10 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S11 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

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

Regra de roteamento atualizada para Q1 do intake (numeração v5.0):

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S9)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S10)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S7)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S8)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S11)

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

Não há regra IF para S6-Edificações — o agente ainda não existe neste
repo (ver checklist de deploy).

---

## CASOS AMBÍGUOS / HANDOFFS

Prompts com palavras-chave de mais de um segmento. O Maestro despacha
para o agente **primário** (mais específico) e sinaliza handoff
declarativo para o secundário.

| Caso | Prompt exemplo | Primário | Handoff |
|------|-----------------|----------|---------|
| UHE (barragem + LT + SE) | "Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE." | agente-barragens (S11) | agente-energia (S10) |
| ETE + subestação | "A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro." | agente-saneamento (S9) | agente-energia (S10) |
| Porto + pista de carga aérea | "Porto arrendado no Amazonas com pátio + pista para carga aérea auxiliar." | agente-portos (S7) | agente-aeroportos (S8) |
| Adutora atravessando barragem de rejeitos | "Adutora atravessa uma barragem de rejeitos existente." | agente-saneamento (S9) | consulta técnica a agente-barragens (S11) |

Ver `tests/routing/prompts.md` para a lista completa de prompts de
smoke test (ainda com numeração S6-S10 antiga — pendente de
atualização, ver checklist).

---

## ARQUITETURA — 5 camadas (C0-C5)

```
C5 — Apresentação      artefatos React, memoriais DOCX, dashboards, PPTX
C4 — Orquestração      Maestro (Manta 00) — router; sessões; handoffs
C3 — Verticais         Manta 03-S1..S11 (Rodovias..Barragens;
                       S6-Edificações planejado)
C2 — Horizontais       Manta 01/02/04-07/13-16 (claims, contratual,
                       orçamento, modelagem, cronograma, BD, PPT,
                       advisory, arquiteto)
C1 — Skills            SKILL.md do catálogo, invocáveis por qualquer
                       agente (aluci-guard, consist-guard, padrao-manta,
                       cad-quantifier, etc.)
C0 — Dados             Supabase (RAG chunks + routing tables),
                       SharePoint (projetos, SKILL.md, ARQUITETURA)
```

## HUB-AND-SPOKE

- **Maestro (C4) decide QUEM** — aplica routing rules (keywords +
  intake Q1-Q4) e despacha para 1+ agentes de C2/C3.
- **Agente (C2/C3) decide CONTEÚDO** — aplica conhecimento de domínio,
  define artefato, escolhe skills.
- **Skill (C1) EXECUTA** — função pura, sem estado próprio.

Handoffs são declarativos: cada SKILL.md declara "quando X aparecer,
encaminhe para Y"; o Maestro faz o handoff sem passar pelo cliente.

## MODEL TIERING

| Tier | Modelo | Uso típico | % de chamadas |
|------|--------|------------|----------------|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados | ~20% |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma | ~70% |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico | ~10% |

Escalonamento dinâmico dentro da mesma sessão: começa em Haiku para
triagem, escala para Sonnet ao entrar no agente vertical, e escala
novamente para Opus se detectar complexidade (claim + jurídico +
técnico + financeiro no mesmo pleito). O tiering é por tipo de tarefa,
não por segmento.

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

## DEPLOY CHECKLIST v5.0

- [x] Copiar 5 agent .md para `.claude/agents/` (v4.2)
- [x] Aplicar patch no CLAUDE.md master (seção Agentes) (v4.2)
- [x] Escrever migração Supabase candidata (`2026_07_05_v4_2_agents_s6_s10.sql`)
- [x] Escrever prompts de teste de routing (`tests/routing/prompts.md`)
- [x] Identificar site SharePoint canônico (`sites/Engenharia`)
- [x] Renumeração S6→S11 aplicada no `CLAUDE.md` e nos 5 `.claude/agents/*.md` (esta rodada)
- [ ] Gate humano: aprovação MN antes de merge dos PRs
- [ ] Aplicar migração Supabase (`rag_collections` + `sp_agent_routing`)
- [ ] Criar as 10 pastas SP (5 agentes em `01-agentes-fundamentais/` + 5 projetos em `03_Projetos/`)
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Escrever e fazer upload dos 5 `SKILL.md` em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Executar testes de routing (rodar prompts de `tests/routing/prompts.md`, registrar resultados)
- [ ] Propagar renumeração S6→S11 para artefatos ainda com numeração antiga: `sharepoint/01-agentes-fundamentais/agente-*/SKILL.md`, `docs/DEPLOY-v4.2.md`, `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`, `tests/routing/prompts.md`, `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` (todos ainda referenciam S6-S10 antigo — não foram tocados nesta rodada)
- [ ] Criar `agente-edificacoes.md` (S6) e sua regra de routing quando o agente for priorizado

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # S7 (era S6 até v4.2)
        ├── agente-aeroportos.md      # S8 (era S7 até v4.2)
        ├── agente-saneamento.md      # S9 — prioridade AySA (era S8 até v4.2)
        ├── agente-energia.md         # S10 — ANEEL/State Grid (era S9 até v4.2)
        └── agente-barragens.md       # S11 (era S10 até v4.2)
```

`agente-edificacoes.md` (S6) ainda não existe neste repo — ver
checklist de deploy.

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S5) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v5.0** (2026-08-23) — reconciliação de numeração com manta-maestro
  v5.0.1: Portos/Aeroportos/Saneamento/Energia/Barragens renumerados
  S6-S10 → S7-S11; reservado S6 para Edificações (planejado, agente
  ainda não criado). Adicionadas seções de arquitetura (5 camadas,
  hub-and-spoke, model tiering) e "Casos ambíguos / handoffs". Nenhum
  agente novo criado nesta rodada — apenas renumeração e documentação.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
