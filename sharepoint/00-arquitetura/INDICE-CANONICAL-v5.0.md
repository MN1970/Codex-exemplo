# ÍNDICE CANÔNICO — Manta Maestro v5.0

**Source of truth único da arquitetura de agentes IA da Manta Associados.**

- **Versão**: v5.0
- **Data**: 2026-07-31
- **Autor**: Sonnet 14 (consolidação final da rodada "15 Sonnets")
- **Ticket**: `MNT-2026-CONSOLIDACAO-ARCH-V5`
- **Substitui**: este documento é, a partir de agora, a referência canônica
  única. Os documentos abaixo permanecem no repositório como fonte
  detalhada por eixo, mas **em caso de conflito, este arquivo prevalece**:
  - `CLAUDE.md` (raiz) — registro operacional, contém uma revisão v5.0
    paralela e **parcialmente divergente** desta (ver nota de proveniência
    e Seção 8.2).
  - `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` (v2.0.0)
  - `docs/DISCIPLINAS-D01-D20.md`, `docs/FUNCIONAIS-F1-F8.md`,
    `docs/ATIVIDADES-A1-A10.md`
  - `docs/EMBEDDER-DECISION.md`, `docs/SUPABASE-PROJECT-AUDIT.md`,
    `docs/DEPLOY-CHECKLIST-v5.0.md`

---

## Nota de proveniência e método

Este documento consolida os outputs de uma rodada de 15 sessões Sonnet
disparadas em 2026-07-31 (ticket `MNT-2026-CONSOLIDACAO-ARCH-V5`), mais
o estado herdado da v4.2 (2026-07-05) e da v1.0/v4.1 (2026-06-24).
Durante a consolidação foram encontrados **dois conjuntos de artefatos
mutuamente inconsistentes** produzidos na mesma rodada — isso é
esperado em uma consolidação de 15 sessões paralelas e é tratado aqui
como achado de auditoria, não escondido:

1. Uma revisão paralela do próprio `CLAUDE.md` (encontrada já em
   andamento no working tree, não commitada) que **renumerou** o Eixo
   S — inserindo "Edificações" como novo S6 e deslocando Portos → S7,
   Aeroportos → S8, Saneamento → S9, Energia → S10, Barragens → S11 —
   com base na descrição da skill `manta-maestro` (v5.0.1), um texto de
   catálogo, não uma fonte de schema/dados.
2. Dois novos agentes verticais (`agente-oleo-gas.md`, S12;
   `agente-edificacoes.md`, S13) e uma migração Supabase candidata
   (`2026_07_31_v4_3_agents_s12_s13.sql`) que **preservam a numeração
   original** (S6=Portos…S10=Barragens, inalterada) e afirmam, citando
   consulta direta e ao vivo à tabela `manta_agent_capabilities`
   (Supabase, projeto `ogxxgvgtulrbbppshjie`), que os `agent_id`
   `03-S12` e `03-S13` **já existem e estão ativos** desde 2026-07-12.

Estes dois conjuntos não podem estar ambos corretos ao mesmo tempo. A
Seção 1 (Eixo S) e a Seção 8.2 explicam o critério usado para decidir
qual tratar como base e por quê, e listam a divergência como decisão
pendente de confirmação formal por MN — **nenhuma renumeração é tratada
aqui como fato consumado.**

Convenção de status usada em todo o documento: ✅ Operacional · ⚡ Parcial
· 🔲 Planejado/Proposto · 🟡 Gap/pendência · 🔴 Bloqueante.

---

## Sumário

1. [Mapa de 4 eixos (S × A × F × D)](#1-mapa-de-4-eixos-s--a--f--d)
2. [Routing — Maestro (Manta 00)](#2-routing--maestro-manta-00)
3. [Model tiering](#3-model-tiering)
4. [Pipeline de fases (INTAKE → READ → PLAN → EXECUTE → DELIVER)](#4-pipeline-de-fases-intake--read--plan--execute--deliver)
5. [Paralelismo e pool de agentes](#5-paralelismo-e-pool-de-agentes)
6. [Histórico de versões](#6-histórico-de-versões)
7. [Checklist de deploy v5.0](#7-checklist-de-deploy-v50)
8. [Decisões pendentes](#8-decisões-pendentes)
9. [Apêndice — mapa de arquivos fonte](#9-apêndice--mapa-de-arquivos-fonte)

---

## 1. Mapa de 4 eixos (S × A × F × D)

Qualquer consulta ao Maestro se posiciona na interseção de 4 eixos
ortogonais, mais um eixo temporal (ciclo de vida) que se aplica a
qualquer composição. Esta é a formalização v5.0 do modelo de 3 eixos da
v4.2 — **os 20 agentes que executam de fato não mudam**; A/F/D são uma
camada de classificação/composição por cima do registro de agentes.

| Eixo | Pergunta que responde | Cardinalidade | Fonte detalhada |
|---|---|---|---|
| **S** — Segmento | Qual domínio de infraestrutura? | 11 linhas (10 confirmadas + 1 de candidatos) | esta seção |
| **A** — Atividade | Qual tipo de entrega/trabalho? | 10 (A1–A10) | `docs/ATIVIDADES-A1-A10.md` |
| **F** — Funcional | Qual capacidade técnica transversal? | 8 (F1–F8) | `docs/FUNCIONAIS-F1-F8.md` |
| **D** — Disciplina | Qual disciplina de engenharia/negócio? | 20 (D01–D20) | `docs/DISCIPLINAS-D01-D20.md` |
| *(temporal)* Ciclo de vida | Em que fase do projeto? | 8 fases | Eixo 3 original (v1.0/v4.2, inalterado) |

Modelo de composição (exemplo de leitura S.A.D, com F como capacidade
interna usada pelo agente despachado, não parte do endereçamento
primário):

```
S8.A3.D07  = Saneamento + Orçamento + Financeiro
           → Manta 05 (orçamento) com contexto de saneamento
             (RAG san:*, handoff de agente-saneamento)

S9.A7.D09  = Energia + Claims + Jurídico
           → Manta 01 (claims) com contexto de energia
             (RAG ene:*, handoff de agente-energia)

S10.A5.D08 = Barragens + Cronograma + Planejamento
           → Manta 07 (cronograma) com contexto de barragens
             (RAG bar:*, handoff de agente-barragens)
```

### 1.1. Eixo S — Segmentos (11 linhas)

**Base adotada nesta consolidação**: a numeração de produção S1–S10
(idêntica à v4.2, **sem renumeração**), confirmada de forma independente
por seis artefatos do repositório (CLAUDE.md v4.2 original, `ARQUITETURA-AGENTES-IA.md`
v2.0.0, os 5 `.claude/agents/agente-*.md`, a migração SQL v4.2, os
mirrors de `SKILL.md` em SharePoint e os `tests/routing/prompts.md`),
mais os dois novos candidatos S12/S13 confirmados por consulta direta e
ao vivo à tabela `manta_agent_capabilities` no Supabase. A alternativa —
renumerar S6→S7…S10→S11 e inserir Edificações como S6 — apoia-se apenas
na descrição textual da skill `manta-maestro` (metadado de catálogo, não
verificado contra schema/dados) e é tratada como **não adotada** até
confirmação MN (ver Seção 8.2).

| S | Segmento | Agente | Status |
|---|---|---|---|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial — coberto por S2/S4, não é agente distinto |
| S6 | Portos | agente-portos | ✅ Operacional (criado 2026-07-05) |
| S7 | Aeroportos | agente-aeroportos | ✅ Operacional (criado 2026-07-05) |
| S8 | Saneamento | agente-saneamento | ✅ Operacional (criado 2026-07-05) — PRIORIDADE AySA |
| S9 | Energia | agente-energia | ✅ Operacional (criado 2026-07-05) — ANEEL/State Grid |
| S10 | Barragens | agente-barragens | ✅ Operacional (criado 2026-07-05) |
| **S11 / S12 / S13** | Candidatos em avaliação | S11 não atribuído · S12 `agente-oleo-gas` · S13 `agente-edificacoes` | 🔲 **Proposto** — arquivos `.claude/agents/` já escritos (versão 1.0.0, status "proposto — pendente gate MN"); **sem** RAG, **sem** rota SharePoint aplicada, **sem** keyword de routing ativa em produção (migração candidata escrita, não aplicada). Ver Seção 8.2 para o dossiê completo. |

**Contagem de agentes operacionais (20, inalterada da v4.2)**: 11
horizontais (Manta 00, 01, 02, 04–07, 13–16) + 9 verticais distintos
operacionais (S1–S4, S6–S10; S5 é parcial e não soma). S12/S13 **não**
entram nesse total de 20 — são propostas, não agentes ativos no
routing de produção.

### 1.2. Eixo A — Atividades (10 linhas)

Tipo de entrega/trabalho, independente do segmento — o mesmo A-code se
aplica a uma proposta de rodovia ou de barragem. Fonte completa (rubrica,
entradas/saídas, critérios de aceitação, handoffs) em
`docs/ATIVIDADES-A1-A10.md` (995 linhas, já com matriz de
entradas/saídas cruzada A×A).

| A | Atividade | Agente responsável | Status |
|---|---|---|---|
| A1 | Proposta | Manta 13 (bd) + Manta 14 (apresentações) | ✅ Definida |
| A2 | Quantidades | Agente vertical do segmento + skills de takeoff (`cad-quantifier`, `evtea-quantifier`) | ✅ Definida |
| A3 | Orçamento | Manta 05 (orçamento) | ✅ Definida |
| A4 | Modelagem financeira | Manta 06 (modelagem) | ✅ Definida |
| A5 | Cronograma | Manta 07 (cronograma) | ✅ Definida |
| A6 | Contratual | Manta 02 (contratual) | ✅ Definida |
| A7 | Claims | Manta 01 (claims) | ✅ Definida |
| A8 | Advisory | Manta 15 (advisory) | ✅ Definida |
| A9 | Regulatório | **sem agente horizontal dedicado** — hoje distribuído pelos verticais (ANEEL em S9, ANAC em S7, ANTAQ em S6 etc.) | 🟡 Rubrica pendente — TODO, aguarda decisão MN (criar "Manta XX — regulatório" ou manter distribuído) |
| A10 | Risco | Manta 15 (advisory) coordena a consolidação (matriz 5×5); sem Manta-code próprio | 🟡 Processo transversal sem agente dedicado — não tratar como "Manta 17" sem registro formal |

**Leitura prática**: A2 tem agente (o vertical do segmento), mas não um
horizontal dedicado — funciona por design. A9 e A10 são os dois gaps
reais do eixo: nenhuma consulta deve assumir um agente horizontal
inexistente para essas atividades.

### 1.3. Eixo F — Funcionais (8 linhas)

Capacidades técnicas transversais usadas por qualquer agente,
independente de segmento ou atividade. Fonte completa (descrição,
componentes, integrações, exemplo de uso, API/interface) em
`docs/FUNCIONAIS-F1-F8.md` (734 linhas).

| F | Funcional | Componentes-chave | Status |
|---|---|---|---|
| F1 | IA (routing, model tiering, scaling, prompting) | Router Manta 00, tiering Haiku→Sonnet→Opus, biblioteca de prompts Q1-Q4 | ✅ Operacional |
| F2 | SharePoint (indexação, sync, storage, permissões, versioning) | `sp_agent_routing`, MCP `SharePoint_Manta`, versionamento nativo SP | ⚡ Parcial — leitura completa; escrita/criação das pastas da expansão v4.2 ainda pendente |
| F3 | Portal (web, SSO, RBAC) | `portal-gestao-manta`, `portal-megaprojeto-builder`, `portal-metro-l4` | 🔲 Planejado/parcial — portais existem como artefatos independentes; SSO/RBAC centralizados não consolidados |
| F4 | Extração (parser PDF/DWG, OCR, NLP, validation) | `pdf`, `autodesk-toolkit`, `cqp-cad-bridge`, `evtea-extractor`, `ler-edital`, `ler-edital-aneel`, `cad-quantifier` | ✅ Operacional — cobertura desigual por segmento (forte em S1/S2/S9; fraca em S6/S7/S10) |
| F5 | Notificação (email, Slack, webhook, subscriptions) | Routines (`create_trigger`/`send_later`), webhook de PR/issue, templates (`morning`, `internal-comms`) | ⚡ Parcial — agendamento e webhook de PR reais; envio ativo de e-mail/Slack não existe como tool |
| F6 | Trace (audit log, approval gates, versioning, history) | Gate humano MN, versionamento Git/PR, rollback documentado em migrações | ✅ Operacional para Git/PR; ⚡ parcial para audit log agregado (hoje disperso entre Git/SP/checklists) |
| F7 | Guardrails (validação de referências, consistência, coesão) | `aluci-guard`, `consist-guard`, `context-guardian` | ✅ Operacional — uso por convenção/gatilho, não é hook obrigatório de pipeline ainda |
| F8 | Padronização (style guide, templates, nomenclatura) | `padrao-manta`, `cl-design`, `brand-guidelines`, templates (`docx`, `pptx`, `xlsx`) | ✅ Operacional — sem linter automático de conformidade ainda |

**Leitura prática**: F5 e F6 são os dois gaps de implementação real do
eixo (existe processo/convenção, não existe sistema dedicado). F3 é o
mais distante de "operacional pleno" — hoje é um conjunto de artefatos
independentes, não uma plataforma única com SSO/RBAC.

### 1.4. Eixo D — Disciplinas (20 linhas)

Disciplinas de engenharia/negócio que atravessam qualquer segmento, em
intensidade variável. Fonte completa (descrição, normas-chave,
ferramentas, matriz de aplicabilidade Disciplina × Segmento) em
`docs/DISCIPLINAS-D01-D20.md` (428 linhas).

> ⚠️ **Ressalva de numeração**: a matriz de aplicabilidade em
> `docs/DISCIPLINAS-D01-D20.md` foi escrita usando o esquema de
> renumeração do Eixo S **não adotado** por esta consolidação (S6 =
> Edificações, S7 = Portos … S11 = Barragens — ver Seção 1.1 e 8.2).
> A lista de disciplinas abaixo (nomes, normas, ferramentas) é válida e
> reutilizável; a matriz de aplicabilidade por segmento naquele
> documento precisa ser reindexada para S1–S10 (numeração de produção)
> antes de ser citada externamente como definitiva.

| D | Disciplina | Normas-chave (amostra) |
|---|---|---|
| D01 | Hidráulica | NBR 12211-12218, NBR 5626, Lei 14.026/2020 |
| D02 | Estrutural | NBR 6118, NBR 8800, NBR 6122, NBR 7187 |
| D03 | Geotecnia | NBR 6484, NBR 8036, NBR 11682, Lei 12.334/2010 |
| D04 | Pavimentação | DNIT 031/ES, método SICRO, NBR 7207 |
| D05 | Elétrica | NBR 5410, NBR 14039, NBR 5419, IEC 61850 |
| D06 | Ambiental | CONAMA 001/1986 e 237/1997, Lei 6.938/1981, Lei 9.985/2000 |
| D07 | Cálculos Econômicos | Manual de EVTE BNDES, metodologia TIR-BNDES, IN 05/EPE |
| D08 | Planejamento | PMBOK, NBR ISO 21500, EVM |
| D09 | Jurídico | Lei 14.133/2021, Lei 8.987/1995, Lei 12.462/2011, Lei 9.307/1996 |
| D10 | Comercial | diretrizes internas de pricing; sem normativo próprio |
| D11 | MEP | NBR 16401, NBR 5626, NBR 5410 |
| D12 | HVAC | NBR 16401, ASHRAE 62.1, NFPA 130 |
| D13 | Acústica | NBR 10151, NBR 15575, NBR 10152 |
| D14 | Acessibilidade | NBR 9050, Lei 13.146/2015, NBR 16537 |
| D15 | BIM | ISO 19650 / NBR ISO 19650, Decreto 10.306/2020 |
| D16 | Paisagismo | NBR 16636, manuais de recuperação de APP |
| D17 | TI/Telecom | NBR 14565, ISO/IEC 27001, IEC 62443 |
| D18 | Comunicação | Plano de Comunicação Social (licenciamento), Lei 8.987/1995 |
| D19 | RH | NR-18, NR-35, NR-33, NR-10 |
| D20 | Qualidade | ISO 9001, NBR 5674, PBQP-H, RBC/INMETRO |

**Leitura prática**: D08 (Planejamento), D09 (Jurídico), D19 (RH) e D20
(Qualidade) são as disciplinas com aplicabilidade "alta" no maior número
de segmentos — candidatas naturais a agente horizontal dedicado se a
demanda um dia justificar (hoje cobertas de forma distribuída pelos
verticais e por Manta 15/advisory). Nenhuma rotina de teste de routing
cobre disciplinas hoje (`tests/routing/prompts.md` testa apenas
segmentos) — tratar D01–D20 como taxonomia de apoio à composição, não
como eixo com routing determinístico testado.

---

## 2. Routing — Maestro (Manta 00)

Regra de dispatch Q1 (segmento), **numeração de produção S1–S10, sem
alteração em relação à v4.2**:

```
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)

IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S10)

# Candidatos S12/S13 — keywords escritas em migração candidata
# (2026_07_31_v4_3_agents_s12_s13.sql), NÃO aplicadas em produção:
IF menção a petróleo|óleo e gás|gasoduto|oleoduto|dutovia|refinaria|ANP|API 650|HAZOP
   → agente-oleo-gas (S12) — 🔲 proposto, routing inativo até migração aplicada

IF menção a edificação|galpão|warehouse|data center|MCMV|NBR 15575|LEED|BIM de edificação
   → agente-edificacoes (S13) — 🔲 proposto, routing inativo até migração aplicada
```

**Casos ambíguos** (documentados em `tests/routing/prompts.md`, política
ainda não formalizada para todos):
- UHE (barragem + LT + SE) → dispatch primário `agente-barragens` +
  handoff `agente-energia`.
- ETE + subestação → dispatch primário `agente-saneamento` + handoff
  `agente-energia`.
- Porto + pista de carga aérea auxiliar → dispatch primário
  `agente-portos` + handoff `agente-aeroportos`.
- Adutora atravessa barragem de rejeitos → `agente-saneamento` com
  consulta técnica ao `agente-barragens`.
- Terminal aquaviário de granel líquido (óleo & gás) → dispatch
  primário `agente-oleo-gas` (quando ativo) + handoff `agente-portos`
  quando há cais/píer dedicado — caso novo, ainda **não** incluído em
  `tests/routing/prompts.md`.

**Critério de aprovação de routing**: ≥ 90% dos prompts de teste
caindo no agente esperado (`docs/DEPLOY-v4.2.md`, seção 5). Cobertura
atual de testes: S1–S10 (`tests/routing/prompts.md`); S12/S13 ainda sem
suite de teste — ação pendente (Seção 7).

---

## 3. Model tiering

| Tier | Modelo | Uso típico | % de chamadas |
|---|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados | ~20% |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma | ~70% |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico | ~10% |

O Maestro escala dinamicamente de tier **dentro de uma mesma sessão**:
começa em Haiku para triagem (Q1–Q4 do intake), escala para Sonnet ao
entrar no agente vertical/horizontal designado, e escala novamente para
Opus se detectar complexidade composta (ex.: claim + jurídico + técnico
+ financeiro no mesmo pleito, ou M&A/due diligence de alto valor).

Tiers default por agente (consistentes com o frontmatter `model:` dos
`.claude/agents/*.md` e a tabela de agentes horizontais):

- **Haiku→Sonnet**: Manta 00 (maestro/router) — único agente que
  começa deliberadamente em tier baixo.
- **Sonnet**: Manta 02, 04, 05, 07, 13, 14 e todos os verticais S1–S10
  (incl. S12/S13 propostos, `model: sonnet` no frontmatter).
- **Sonnet/Opus** (conforme complexidade): Manta 06 (modelagem
  financeira — M&A/concessões de longo prazo escalam), Manta 15
  (advisory — pareceres de alto risco reputacional escalam).
- **Opus** (default): Manta 01 (claims), Manta 16 (arquiteto-ia).

Este tiering é aplicado **por convenção documental** (frontmatter dos
agentes); o scaling dinâmico dentro de uma sessão depende do
orquestrador de runtime do Maestro, que está fora deste repositório
(este repositório é o registro versionado, não o runtime).

---

## 4. Pipeline de fases (INTAKE → READ → PLAN → EXECUTE → DELIVER)

Formalização v5.0 do fluxo de execução de uma consulta, uma vez que o
Maestro já decidiu **quem** atende (Seção 2). Este pipeline descreve
**como** o agente designado processa o pedido internamente, mapeado
sobre os Funcionais (Eixo F) já existentes — não introduz sistemas
novos, apenas nomeia e ordena o que já acontece hoje de forma implícita.

```
┌─────────┐   ┌──────┐   ┌──────┐   ┌─────────┐   ┌─────────┐
│ INTAKE  │──▶│ READ │──▶│ PLAN │──▶│ EXECUTE │──▶│ DELIVER │
└─────────┘   └──────┘   └──────┘   └─────────┘   └─────────┘
     │            │           ▲          │             │
     │ F1         │ F2/F4     │          │ F4/D-eixo   │ F7→F8→F6
     ▼            ▼           │          ▼             ▼
  Q1-Q4        SharePoint     │      composição       gate
  intake        + extração    │      S.A.D +          humano
  (Haiku)       (Sonnet)      │      handoffs         (MN)
                              │
                    ┌─────────┴─────────┐
                    │  RE-PLAN LOOP      │
                    │  disparado quando  │
                    │  READ ou EXECUTE   │
                    │  revelam fato novo │
                    │  que invalida o    │
                    │  plano em curso    │
                    └────────────────────┘
```

1. **INTAKE** (F1, tier Haiku) — classificação Q1 (segmento), Q2 (fase
   do ciclo de vida), Q3 (objetivo), Q4 (formato de dados). Produz
   `{ agente_primario, agentes_handoff[], tier, fase_ciclo_vida,
   confidence }` (contrato já documentado em F1).
2. **READ** (F2 + F4, tier Sonnet) — leitura da fonte documental
   (SharePoint via F2) e extração estruturada (parsers de F4: `pdf`,
   `autodesk-toolkit`, `ler-edital`, `evtea-extractor` etc.). Campo
   ausente/ilegível vira `null` + flag `"a_confirmar"`, nunca valor
   inventado (contrato de erro já documentado em F4).
3. **PLAN** — o agente vertical/horizontal designado decompõe o pedido
   em composições S.A.D (Seção 1), decide quais disciplinas (D) e
   handoffs (para outros A/S) são necessários, e — quando o volume
   justifica — despacha sub-agentes em paralelo (Seção 5).
4. **EXECUTE** — produção do conteúdo técnico-primário: cálculo,
   redação, quantitativo, orçamento, cronograma, parecer — usando as
   disciplinas (D) e skills relevantes.
5. **DELIVER** (F7 → F8 → F6) — antes de qualquer output virar
   entregável oficial: **F7** (guardrails: `aluci-guard` +
   `consist-guard`) valida referências e consistência; **F8**
   (`padrao-manta`) aplica forma/identidade visual; **F6** registra o
   evento e aciona o gate humano MN quando aplicável. Nenhuma etapa
   pula F7 antes de F6 — pular guardrails antes de publicar é
   considerado desvio de processo (já documentado em F7).

### Re-plan loop

Se **READ** ou **EXECUTE** revelam um fato novo que invalida premissas
do PLAN em curso — exemplos reais já observados nesta própria rodada de
consolidação:
- um extrator encontra um valor que contradiz o briefing inicial (ex.:
  edital revisado depois do briefing);
- `aluci-guard`/`consist-guard` (F7) rejeita uma referência ou uma
  inconsistência numérica que exige reabrir o cálculo, não apenas
  corrigir o texto;
- uma consulta a sistema vivo (Supabase, SharePoint) contradiz o que a
  documentação estática assumia — como aconteceu nesta consolidação: a
  auditoria Supabase (Seção 8.3) encontrou evidência de que o embedder
  em produção já não é o que a documentação descrevia;

o fluxo **retorna a PLAN**, não avança para EXECUTE/DELIVER com a
premissa quebrada. O re-plan é registrado (F6) como evento — não é
silencioso. Esta é a mesma disciplina que os guardrails de F7 e o gate
humano de F6 já impõem no fechamento de documentos; o pipeline apenas
nomeia o ciclo explicitamente para que replanejar não seja tratado como
falha do agente, mas como comportamento esperado diante de fato novo.

---

## 5. Paralelismo e pool de agentes

- **Teto de 8 sub-agentes simultâneos** por composição/sessão — mesmo
  limite já em prática no Maestro hoje (citado no modelo de composição
  S.A.D da v5.0 e consistente com o padrão de dispatch de sub-agentes
  observado nas ferramentas de orquestração deste ambiente). Acima
  desse teto, o agente coordenador (tipicamente o vertical de maior
  prioridade na composição, ou Manta 15/advisory em sínteses A10)
  serializa o excedente em lotes, em vez de despachar tudo de uma vez.
- **Pool de agentes** — os 20 agentes operacionais (Seção 1.1/1.2) mais
  os candidatos S12/S13 formam o pool endereçável pelo Maestro. Cada
  sub-agente despachado dentro do teto de 8 herda o contexto de sessão
  (Q1–Q4, composição S.A.D já resolvida) e reporta de volta ao
  coordenador, não diretamente ao usuário — o coordenador consolida
  (padrão hub-and-spoke: "Maestro decide QUEM, agente decide CONTEÚDO,
  skill EXECUTA").
- **Critério de paralelização** — dois ou mais A-codes/D-codes
  independentes dentro da mesma composição S (ex.: A2-Quantidades e
  A9-Regulatório rodando em paralelo sobre o mesmo S8-Saneamento) são
  candidatos naturais a sub-agentes simultâneos; A-codes com
  dependência direta de handoff (ex.: A3-Orçamento depende da saída de
  A2-Quantidades — ver matriz de entradas/saídas em
  `docs/ATIVIDADES-A1-A10.md`) **não** paralelizam entre si — rodam em
  sequência dentro do teto.
- **Skills (Eixo C1 do modelo de 5 camadas em `ARQUITETURA-AGENTES-IA.md`)**
  não contam para o teto de 8 — são invocadas de forma síncrona dentro
  da execução de um único (sub-)agente, não são despachadas como
  processos paralelos independentes.
- **Gap de implementação**: este teto e a lógica de pool são práticas
  observadas/documentadas nesta consolidação, não um sistema de fila
  formalizado com métricas (throughput, tempo de espera por slot). Não
  há, neste repositório, telemetria de uso real do paralelismo — ação
  pendente listada na Seção 7.

---

## 6. Histórico de versões

Duas linhas de versionamento coexistiam no repositório antes desta
consolidação — o `CLAUDE.md` versiona o **sistema** (v4.1 → v4.2) e o
`ARQUITETURA-AGENTES-IA.md` versiona a **si mesmo como documento**
(v1.0.0 → v2.0.0), cobrindo o mesmo conteúdo em datas coincidentes. A
partir da v5.0, este arquivo (`INDICE-CANONICAL-v5.0.md`) unifica as
duas linhas sob um único contador de versão do sistema.

| Versão (unificada) | Data | Escopo |
|---|---|---|
| **v1.0** | 2026-06-24 | Baseline: 15 agentes (11 horizontais + S1–S4 verticais). Registrado como `ARQUITETURA-AGENTES-IA.md` v1.0.0 e como "v4.1" no `CLAUDE.md`. |
| **v4.1** | (mesma baseline) | Nomenclatura do `CLAUDE.md` para o mesmo estado de v1.0 — 15 agentes, sem S5–S10. |
| **v4.2** | 2026-07-05 | Expansão S6–S10 (Portos, Aeroportos, Saneamento, Energia, Barragens) — 5 agentes verticais novos + 5 coleções RAG + 5 pastas SP. Total: 20 agentes. `ARQUITETURA-AGENTES-IA.md` bump para v2.0.0. Ticket `MNT-2026-UPGRADE-AGENTS-S6S10`. |
| **v5.0** | 2026-07-31 | Esta consolidação. Formaliza o modelo de 4 eixos (S×A×F×D) sobre os 20 agentes existentes (sem alterar routing/numeração de produção S1–S10); documenta S12/S13 (Óleo & Gás, Edificações) como candidatos confirmados em `manta_agent_capabilities` mas **não** operacionais (sem RAG/SharePoint/routing aplicados); resolve/registra a divergência de numeração encontrada entre duas revisões paralelas da rodada (Seção 8.2); consolida achados de auditoria Supabase e a decisão de embedder em aberto (Seção 8.1/8.3); unifica os dois contadores de versão anteriores. Ticket `MNT-2026-CONSOLIDACAO-ARCH-V5`. **Este arquivo substitui `CLAUDE.md` e `ARQUITETURA-AGENTES-IA.md` como referência canônica** — os dois permanecem no repositório como fonte operacional/histórica, atualizados para apontar para cá. |

---

## 7. Checklist de deploy v5.0

Herda integralmente as pendências não resolvidas da v4.2 (nenhuma foi
fechada apenas por este documento existir) e adiciona o checklist da
própria rodada de consolidação.

### 7.1. Herdado da v4.2 — ainda pendente

- [ ] Criar 5 coleções RAG em Supabase (`saneamento`, `energia`,
  `portos`, `aeroportos`, `barragens`) — migração candidata pronta em
  `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar 5 pastas SharePoint de projeto (`03_Projetos/<Segmento>/`)
- [ ] Upload dos 5 `SKILL.md` (já escritos em
  `sharepoint/01-agentes-fundamentais/agente-*/SKILL.md`) para o
  SharePoint real
- [ ] Testar routing do Maestro com os prompts de
  `tests/routing/prompts.md` em ambiente de produção
- [ ] Gate humano: aprovação MN antes de merge

### 7.2. Novo desta consolidação (v5.0)

- [ ] **Resolver a divergência de numeração do Eixo S** (Seção 1.1 e
  8.2) — decidir formalmente entre manter S1–S10 + S12/S13 (adotado
  aqui) ou a renumeração S1–S11 com Edificações como S6, e **corrigir
  todos os artefatos divergentes** (a revisão paralela do `CLAUDE.md`
  em andamento, a matriz de `docs/DISCIPLINAS-D01-D20.md`)
- [ ] Publicar `docs/SEGMENTOS-S12-S13-DECISION.md` — arquivo
  **referenciado** por `agente-oleo-gas.md` e `agente-edificacoes.md`
  mas que **ainda não existe** no repositório; esta Seção 8.2 supre o
  conteúdo no interim, mas o arquivo dedicado deveria ser criado para
  manter a referência cruzada válida
  - [ ] Este documento formal só deve ser criado **após aprovação MN**
    (§4 do questionário de decisão — Seção 8.2), não antes; criar o
    arquivo antes da decisão apenas formalizaria uma proposta como se
    fosse decisão
- [ ] Aplicar `supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql`
  (RAG `oleo-gas`/`edificacoes` + routing) — **somente se** MN decidir
  formalizar S12/S13 nesta sprint (Seção 8.2, questão 3)
- [ ] Estender `tests/routing/prompts.md` com casos S12/S13 (e o caso
  ambíguo "terminal aquaviário de granel líquido" — Seção 2)
- [ ] Auditar o embedder real em produção e reconciliar com a evidência
  encontrada nesta rodada (Seção 8.1) — a tabela `manta_rag_chunks` já
  traz comentário indicando `bge-m3`/1024-d desde 2026-07-03, o que
  contradiz a suposição de "ainda em bge-small" usada em
  `docs/EMBEDDER-DECISION.md`
- [ ] Confirmar contagem real de chunks RAG via `list_tables`/
  `execute_sql` no Supabase (`ogxxgvgtulrbbppshjie`) antes de citar
  qualquer número em documento externo
- [ ] Investigar o projeto Supabase `xgluoaaymbdzbbudnwrh` referenciado
  como inacessível (AI-1/AI-5 de `docs/SUPABASE-PROJECT-AUDIT.md`)
- [ ] Aplicar RLS + policies nas 3 tabelas Supabase expostas
  (`rag_collections`, `sp_agent_routing`, `maestro_routing_keywords`) —
  achado de segurança 🔴 da auditoria (AI-6, Seção 8.3)
- [ ] Decidir destino de `manta-rodovias` e `manta-portal-piloto`
  (projetos Supabase `INACTIVE`) e checar `manta-tocantins` antes de
  qualquer consolidação (AI-7/AI-8)
- [ ] Redigir e aprovar política de multi-project Supabase (ADR, AI-9)
- [ ] Validar rubricas A9/A10 (sem agente horizontal — Seção 1.2) com
  MN antes de publicar `docs/ATIVIDADES-A1-A10.md` como SKILL.md formal
- [ ] Reindexar a matriz de `docs/DISCIPLINAS-D01-D20.md` para a
  numeração de produção (S1–S10) adotada aqui
- [ ] Rodar `aluci-guard` sobre este documento antes de merge
- [ ] Rodar `consist-guard` sobre este documento antes de merge
- [ ] Gate humano final: aprovação MN antes de considerar a v5.0
  encerrada — nenhum item acima substitui essa aprovação

### 7.3. Critérios de aceitação (herdados de `docs/DEPLOY-CHECKLIST-v5.0.md`)

- **Routing**: ≥ 90% dos prompts de teste caem no agente esperado;
  casos ambíguos documentados e decididos explicitamente.
- **Guardrails**: zero referências fabricadas (`aluci-guard`); estrutura
  íntegra e sem pendências abertas (`consist-guard`).
- **Merges**: `Codex-exemplo` e `manta-hub` sincronizados — nenhum
  merge de um sem o outro.
- **Supabase**: coleções e routing rules confirmadas via query
  pós-deploy; rollback testado antes de aplicar em produção.
- **Gate humano final MN**: aprovação explícita registrada — nenhum
  item técnico substitui essa aprovação.

---

## 8. Decisões pendentes

Três frentes levantadas nesta rodada que **não foram resolvidas** aqui
— documentadas como pendências rastreáveis com recomendação técnica,
não como decisões já tomadas.

### 8.1. Embedder — bge-m3 vs. bge-small-en-v1.5 (gap G010)

**Situação conforme `docs/EMBEDDER-DECISION.md`** (autor: Sonnet 11):
existe uma decisão registrada em 22/07/2026 adotando `bge-m3` (1024-d,
multilíngue) como embedder canônico, mas o pipeline de produção
supostamente ainda gerava embeddings com `bge-small-en-v1.5` (384-d,
monolíngue-inglês) — 0 de 204 chunks migrados. A recomendação daquele
documento é migrar para `bge-m3`, pelo desalinhamento de idioma
(corpus majoritariamente PT/ES) e pelo baixo custo de migração (204
chunks).

**Achado que contradiz essa premissa** (`docs/SUPABASE-PROJECT-AUDIT.md`,
autor: Sonnet 13, via `list_tables` real no projeto
`ogxxgvgtulrbbppshjie`): o comentário da tabela `manta_rag_chunks` em
produção registra **"Chunks com embeddings 1024d (bge-m3, canonical
Maestro 2026-07-03)"** — ou seja, há evidência direta de schema de que
a migração para `bge-m3` **já ocorreu** em 2026-07-03, antes mesmo da
"decisão" de 22/07/2026 citada no outro documento. Isso sugere que a
sequência real dos eventos é: migração técnica em 03/07 → decisão
formal (redundante?) em 22/07 → e a documentação (skill `manta-maestro`,
que descreve "bge-small-en-v1.5 384d") nunca foi atualizada para
refletir nem uma coisa nem outra.

**Decisão pendente**: antes de executar qualquer roadmap de migração
(o de `docs/EMBEDDER-DECISION.md` §5.2), é preciso **reconciliar qual
dos dois relatos é o estado real atual** — rodar uma query direta
(`SELECT embedding IS NOT NULL, vector_dims(embedding) FROM
manta_rag_chunks LIMIT 5` ou equivalente) para confirmar dimensão e
não-nulidade antes de assumir que uma migração ainda precisa ser feita.
Se a coluna 1024-d já está populada, o trabalho remanescente é
**apenas documental** (atualizar a skill `manta-maestro` e este índice),
não uma migração de dados.

- [ ] Executar a query de confirmação acima antes de qualquer ação.
- [ ] Se confirmado bge-m3/1024-d já populado: fechar G010 como
  "documentação desatualizada", atualizar a skill `manta-maestro` e
  remover o roadmap de migração de `docs/EMBEDDER-DECISION.md` (ou
  marcá-lo como historicamente já executado).
- [ ] Se **não** confirmado (schema tem coluna 1024-d mas ainda vazia,
  por exemplo): seguir o roadmap de `docs/EMBEDDER-DECISION.md` §5.2
  como planejado, com aprovação MN prévia.

### 8.2. S11/S12/S13 — segmentos candidatos e conflito de numeração

**O que é fato, confirmado por consulta direta ao Supabase**
(`agente-oleo-gas.md`, `agente-edificacoes.md`, migração
`2026_07_31_v4_3_agents_s12_s13.sql`): a tabela `manta_agent_capabilities`
já tem os registros `agent_id = '03-S12'` (Óleo & Gás) e `agent_id =
'03-S13'` (Edificações), `ativo = true`, registrados em 2026-07-12 —
**antes** desta rodada de consolidação. Nenhum dos dois tem, hoje, RAG
collection, rota SharePoint ou keyword de routing aplicada — o Maestro
não consegue de fato despachar para eles.

**Diferenciação de escopo** (já madura nos dois `.claude/agents/*.md`
novos):

| | Manta 03-S12 — Óleo & Gás | Manta 03-S13 — Edificações |
|---|---|---|
| Cobre | Downstream (refino) + midstream (dutovias, terminais) — engenharia civil/estrutural | Residencial, comercial, galpão/industrial leve, hospitalar, institucional, data center (envoltória civil) |
| Não cobre | Upstream/E&P (reservatório, perfuração, completação, FPSO) | Avaliação de imóvel/negócio (isso é Manta 04), projeto elétrico/mecânico de TI de data center |
| Normas-chave | ANP, API 650/653, ANSI/ASME B31.3/4/8, NFPA 30/15/16, NR-20/13, HAZOP | NBR 15575, NBR 6118/8800/6120, LEED, Decreto 10.306/2020 (BIM), NBR 9050 |
| RAG proposto | `oleo-gas` (`og:`) | `edificacoes` (`edi:`) |
| Diferenciação crítica | vs. engenharia de petróleo (upstream) — fora do escopo Manta | vs. **Manta 04 (Imobiliário)** — Manta 04 é negócio/avaliação, S13 é projeto/engenharia; não há redundância real |

**O conflito descoberto nesta consolidação**: uma revisão paralela do
`CLAUDE.md` (não commitada, encontrada em andamento no working tree)
adotou uma numeração **diferente** — inseriu "Edificações" como **S6**
(deslocando Portos→S7 … Barragens→S11) — citando a descrição da skill
`manta-maestro` (v5.0.1) como fonte. Essa é a mesma disciplina
(Edificações) recebendo **dois códigos diferentes** (S6 numa fonte, S13
noutra) em documentos escritos no mesmo dia. O próprio
`agente-edificacoes.md` já sinaliza essa colisão e pede reconciliação
MN antes de formalizar.

**Por que esta consolidação adota S12/S13 (não a renumeração S6–S11)**:
a evidência de S12/S13 vem de consulta **ao vivo a uma tabela de
banco de produção** (`manta_agent_capabilities`, registrada em
2026-07-12 — antes desta rodada, não uma proposta desta rodada); a
evidência da renumeração S6–S11 vem de um **texto de descrição de
skill** (metadado de catálogo, sem query a schema/dados que a
sustente). Dados de produção pesam mais que texto de catálogo não
verificado — mas isso **não é decisão final**, é o critério usado para
não travar esta consolidação; a decisão formal cabe a MN.

**Questionário de decisão para MN**:
1. Confirmar a numeração de produção: manter S1–S10 (inalterado) +
   S12 (Óleo & Gás) + S13 (Edificações), como adotado aqui — ou migrar
   para o esquema S1–S11 com Edificações em S6? Se migrar, todos os
   artefatos afetados (CLAUDE.md, ARQUITETURA-AGENTES-IA.md, 5
   frontmatters de agente, `docs/DISCIPLINAS-D01-D20.md`,
   SharePoint, RAG, routing) precisam de patch coordenado — não é uma
   troca de um único arquivo.
2. Priorizar a formalização de S12 e/ou S13 nesta sprint (aplicar a
   migração `2026_07_31_v4_3_agents_s12_s13.sql`, criar pastas
   SharePoint, ativar routing) ou manter como proposto sem prazo?
3. Confirmar se **S11** (não atribuído em nenhum documento revisado)
   é de fato uma lacuna intencional ou um terceiro candidato ainda não
   documentado — nenhuma fonte consultada nesta auditoria atribui
   conteúdo a S11.
4. Aprovar a criação formal de `docs/SEGMENTOS-S12-S13-DECISION.md`
   como o documento de reconciliação definitivo, substituindo esta
   Seção 8.2 como fonte detalhada (mantendo este índice apenas com o
   resumo e o link).

### 8.3. Supabase — projeto de referência, segurança e política multi-project

Achados de `docs/SUPABASE-PROJECT-AUDIT.md` (Sonnet 13, via chamadas
reais `list_organizations`/`list_projects`/`get_project`/`list_tables`/
`get_advisors` no MCP Supabase):

- **Projeto ativo confirmado**: `manta-maestro`
  (`ogxxgvgtulrbbppshjie`, `sa-east-1`, `ACTIVE_HEALTHY`) — 34 tabelas,
  319 linhas em tabelas de RAG core, 9 `rag_collections`, 9
  `sp_agent_routing`, 50 `maestro_routing_keywords`.
- **Referência morta**: `xgluoaaymbdzbbudnwrh` (citada em SKILL.md do
  SharePoint como o projeto do Maestro, região `us-east-2`, ~221
  registros) retorna "permission denied" — não pertence à organização
  Supabase da conta corporativa (`umlmzpmdgffaiwpxyflb`, único projeto
  em `sa-east-1`×4). Hipótese mais provável: projeto legado de outra
  conta/org, substituído pelo `manta-maestro` atual. **Não confirmado
  com certeza absoluta** — requer acesso humano ao dashboard Supabase
  (AI-1).
- **3 projetos `INACTIVE`** na mesma organização, todos no plano free:
  `manta-tocantins` (mais antigo, possível vínculo com o contrato
  CT5500097701 — checar antes de descartar), `manta-rodovias`,
  `manta-portal-piloto` (pilotos de curta duração, candidatos a
  desativação).
- **🔴 Achado de segurança (não era o escopo original da auditoria, mas
  crítico)**: RLS **desabilitado** em 3 tabelas públicas expostas a
  `anon`/`authenticated` via PostgREST — `rag_collections`,
  `sp_agent_routing`, `maestro_routing_keywords`. Qualquer cliente com
  a chave `anon` do projeto tem leitura **e escrita** nessas tabelas de
  routing/coleções hoje. SQL de remediação já redigido (ver AI-6 em
  `docs/SUPABASE-PROJECT-AUDIT.md`, seção 4) — não aplicado
  automaticamente porque exige policies corretas para não quebrar o
  acesso legítimo do próprio Maestro.

**Decisão pendente para MN**:
1. Confirmar/descartar `xgluoaaymbdzbbudnwrh` (AI-1, AI-5) e atualizar o
   `SKILL.md` do SharePoint que ainda o referencia (AI-3).
2. Aprovar a aplicação de RLS + policies nas 3 tabelas expostas — este
   é o item de maior severidade de todo o Eixo 8 e não depende de
   nenhuma outra decisão para ser executado (AI-6).
3. Decidir destino de `manta-rodovias`/`manta-portal-piloto`
  (desativar/deletar) e checar `manta-tocantins` antes de qualquer
  consolidação (AI-7/AI-8).
4. Aprovar um ADR curto de política multi-project Supabase (AI-9),
   para que o próximo "`xgluoaa...`" não se repita.

---

## 9. Apêndice — mapa de arquivos fonte

```
Codex-exemplo/
├── CLAUDE.md                                    # registro operacional; contém revisão v5.0
│                                                 # paralela e divergente desta (ver Seção 8.2)
├── README.md
├── .claude/agents/
│   ├── agente-portos.md                         # S6, operacional
│   ├── agente-aeroportos.md                     # S7, operacional
│   ├── agente-saneamento.md                     # S8, operacional — prioridade AySA
│   ├── agente-energia.md                        # S9, operacional — ANEEL/State Grid
│   ├── agente-barragens.md                      # S10, operacional
│   ├── agente-oleo-gas.md                       # S12, proposto — pendente gate MN
│   └── agente-edificacoes.md                    # S13, proposto — pendente gate MN
├── docs/
│   ├── DEPLOY-v4.2.md                           # runbook manual v4.2 (Supabase + SharePoint)
│   ├── COWORK-INTEGRATION.md                    # runbook de integração Maestro ↔ Cowork
│   ├── DEPLOY-CHECKLIST-v5.0.md                 # checklist da rodada de 15 Sonnets
│   ├── DISCIPLINAS-D01-D20.md                   # Eixo D completo (matriz precisa reindexação)
│   ├── FUNCIONAIS-F1-F8.md                      # Eixo F completo
│   ├── ATIVIDADES-A1-A10.md                     # Eixo A completo
│   ├── EMBEDDER-DECISION.md                     # gap G010 — ver Seção 8.1
│   └── SUPABASE-PROJECT-AUDIT.md                # gap G012 — ver Seção 8.3
├── sharepoint/
│   ├── README.md
│   ├── 00-arquitetura/
│   │   ├── ARQUITETURA-AGENTES-IA.md            # v2.0.0 — documento anterior, mantido
│   │   └── INDICE-CANONICAL-v5.0.md             # este arquivo — canônico a partir de agora
│   └── 01-agentes-fundamentais/
│       └── agente-{portos,aeroportos,saneamento,energia,barragens}/
│           ├── SKILL.md
│           ├── README.md
│           ├── refs/
│           └── prompts/
├── supabase/migrations/
│   ├── 2026_07_05_v4_2_agents_s6_s10.sql        # candidata, S6-S10 (não confirmada aplicada)
│   └── 2026_07_31_v4_3_agents_s12_s13.sql       # candidata, S12/S13 (não aplicada)
└── tests/routing/
    └── prompts.md                               # smoke tests S1-S10 (S12/S13 ainda não cobertos)
```

**Regra de precedência**: em qualquer divergência de conteúdo entre os
arquivos acima e este índice, **este índice prevalece** até que os
demais sejam corrigidos/reconciliados conforme o checklist da Seção 7.
Este documento não deleta nem sobrescreve os arquivos-fonte — eles
continuam existindo como material de apoio detalhado por eixo.

---

_Documento vivo. Alterações via pull request neste repositório,
validação `aluci-guard` + `consist-guard`, e aprovação MN (gate humano)
antes de qualquer merge — mesmo padrão de governança já em uso em
`docs/DEPLOY-v4.2.md` e `docs/DEPLOY-CHECKLIST-v5.0.md`._
