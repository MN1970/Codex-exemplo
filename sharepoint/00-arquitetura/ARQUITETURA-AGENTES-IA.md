# ARQUITETURA-AGENTES-IA.md

**Sistema Manta Maestro — Arquitetura de Agentes IA**

- **Versão**: 3.0.0
- **Data**: 2026-07-31
- **Autor**: Manta Associados
- **Substitui**: v2.0.0 (2026-07-05)
- **Ticket**: MNT-2026-UPGRADE-ARCH-4EIXOS

## Sumário

- [1. Visão geral](#1-visão-geral)
- [2. 4 eixos ortogonais do sistema](#2-4-eixos-ortogonais-do-sistema)
  - [2.1 Eixo S — Segmentos verticais](#21-eixo-s--segmentos-verticais-10)
  - [2.2 Eixo A — Atividades](#22-eixo-a--atividades-10)
  - [2.3 Eixo F — Funcionais](#23-eixo-f--funcionais-8)
  - [2.4 Eixo D — Disciplinas](#24-eixo-d--disciplinas-20)
  - [2.5 Dimensão complementar — ciclo de vida (8 fases)](#25-dimensão-complementar--ciclo-de-vida-8-fases)
  - [2.6 Composição S.A.F.D — como os eixos se combinam](#26-composição-safd--como-os-eixos-se-combinam)
- [3. 5 camadas da arquitetura](#3-5-camadas-da-arquitetura)
- [4. Hub-and-spoke](#4-hub-and-spoke)
- [5. Model tiering](#5-model-tiering)
- [6. Routing do Maestro](#6-routing-do-maestro-manta-00)
- [7. Knowledge Engine (RAG)](#7-knowledge-engine-rag)
- [8. SharePoint routing](#8-sharepoint-routing)
- [9. Diagrama de fluxo](#9-diagrama-de-fluxo-agente-vertical)
- [10. Matriz de composição — casos de uso](#10-matriz-de-composição--casos-de-uso)
- [11. Changelog v2.0 → v3.0](#11-changelog-v20--v30)
- [12. Referências](#12-referências)

---

## 1. Visão geral

O **Manta Maestro** é o sistema de agentes IA da Manta Associados —
20 agentes especializados em engenharia de infraestrutura, cobrindo do
estudo prévio ao descomissionamento, organizados em um **hub-and-spoke**
com um router central (Manta 00, o Maestro).

A v2.0.0 promoveu os 5 agentes verticais **S6–S10** (Portos, Aeroportos,
Saneamento, Energia, Barragens) de "novos" para **operacional**,
completando a cobertura de 10 segmentos de infraestrutura.

A **v3.0.0** dá um passo além: em vez de tratar "agentes horizontais" e
"agentes verticais" como duas listas paralelas, o sistema passa a se
descrever como um **espaço de 4 eixos ortogonais — S × A × F × D**.
Toda consulta, laudo, orçamento ou claim que passa pelo Maestro pode
ser localizado nesse espaço de 4 coordenadas:

- **S** — em qual **segmento** de infraestrutura estamos (rodovia,
  porto, saneamento...)?
- **A** — qual **atividade de negócio** está sendo executada (proposta,
  orçamento, claim...)?
- **F** — qual **função de plataforma** está sendo usada (extração de
  dado, guardrail, notificação...)?
- **D** — qual **disciplina técnica de engenharia** está envolvida
  (hidráulica, estrutural, elétrica...)?

Essa mudança não substitui nenhum agente existente — ela **reclassifica**
os 20 agentes e as ~50 skills do catálogo em um sistema de coordenadas
único, o que permite compor consultas mais precisas (`S8.A3.D07`),
detectar lacunas de cobertura (célula da matriz sem agente/skill) e
padronizar o vocabulário usado em routing, RAG e SharePoint.

## 2. 4 eixos ortogonais do sistema

O sistema é ortogonal em **4 dimensões**. As três primeiras (S, A, F)
correspondem a *quem faz o quê* (segmento, atividade, função de
plataforma); a quarta (D) descreve *sobre qual disciplina técnica* o
trabalho recai. Uma quinta dimensão — o **ciclo de vida** (fase do
empreendimento) — permanece como atributo complementar de intake (Q2),
não ortogonal aos outros quatro (ver §2.5).

```
                    ┌─────────────┐
                    │      D      │  disciplina técnica
                    │ (20 opções) │  (hidráulica, estrutural, ...)
                    └──────┬──────┘
                           │
   ┌─────────────┐  ┌──────┴──────┐  ┌─────────────┐
   │      S      │  │             │  │      F      │
   │ (10 opções) │──┤   consulta  ├──│ (8 opções)  │
   │  segmento   │  │  no Maestro │  │  funcional  │
   └─────────────┘  │             │  └─────────────┘
                     └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │      A      │  atividade de negócio
                    │ (10 opções) │  (proposta, orçamento, ...)
                    └─────────────┘
```

### 2.1 Eixo S — Segmentos verticais (10)

Cada segmento concentra vocabulário, normas, cálculos e handoffs de
uma área de infraestrutura. Coberto pelos agentes **03-S1..S10**.

| Código | Segmento | Agente | Status |
|---|---|---|---|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial |
| S6 | Portos | agente-portos | ✅ Operacional |
| S7 | Aeroportos | agente-aeroportos | ✅ Operacional |
| S8 | Saneamento | agente-saneamento | ✅ Operacional — prioridade AySA |
| S9 | Energia | agente-energia | ✅ Operacional — ANEEL/State Grid |
| S10 | Barragens | agente-barragens | ✅ Operacional |

> Nota: o catálogo de skills já referencia um segmento adicional
> "Edificações" em discussões internas do Maestro v5. Ele **não** faz
> parte do escopo S1-S10 desta versão do documento; será incorporado
> em revisão futura quando o agente vertical correspondente for
> formalizado neste repositório.

### 2.2 Eixo A — Atividades (10)

O eixo A descreve **o que está sendo produzido/decidido**,
independente do segmento. Ele **substitui conceitualmente** o antigo
"Eixo 1 — Horizontais" da v2.0.0, mapeando cada atividade a um código
`A1..A10` que pode ser combinado com qualquer `S`.

| Código | Atividade | Descrição | Agente(s) primário(s) | Skills de apoio típicas |
|---|---|---|---|---|
| A1 | Proposta | Captação, proposta técnica e comercial, apresentações a cliente | Manta 13 (bd), Manta 14 (apresentações) | proposta-comercial, proposta-tecnica-rod, pptx |
| A2 | Quantidades | Levantamento de quantitativos (m, m², m³) a partir de projeto/CAD/edital | *(transversal — sem agente horizontal dedicado)* | cad-quantifier, evtea-quantifier, cqp-cad-bridge |
| A3 | Orçamento | Composição de custo, SICRO/SINAPI, orçamento paramétrico e analítico | Manta 05 (orçamento) | sicro-completo, sicro-composicoes, sicro-similaridade, xlsx |
| A4 | Modelagem | Modelagem financeira/econômica de projeto ou concessão | Manta 06 (modelagem) | xlsx, mk-manta |
| A5 | Cronograma | Planejamento, XER/MSP, curva S, análise de caminho crítico | Manta 07 (cronograma) | cronograma-toolkit, xer-msp-toolkit, xer-p6-analytics |
| A6 | Contratual | Gestão de contrato, editais, aditivos, FIDIC | Manta 02 (contratual) | ler-edital, ler-edital-aneel, docx |
| A7 | Claims | Reequilíbrio econômico-financeiro, disrupção, quantum | Manta 01 (claims) | conclusao-janelas, gr04-infraestrutura-pontes, mk-manta |
| A8 | Advisory | Aconselhamento estratégico, due diligence, M&A | Manta 15 (advisory) | mk-manta, manta-regis |
| A9 | Regulatório | Conformidade e interlocução com órgãos reguladores (ANEEL, ANTT, ANTAQ, ANAC, ANA) | *(transversal — coberto por advisory + verticais)* | ler-edital-aneel, aluci-guard |
| A10 | Risco | Matriz de risco, contingência, análise de sensibilidade | *(transversal — coberto por claims + advisory + arquiteto-ia)* | mk-manta, manta-arquiteto-ia |

**Reconciliação com o antigo Eixo Horizontais (v2.0.0)** — os 11
agentes horizontais continuam existindo; a tabela abaixo mostra como
cada um se posiciona no novo espaço A/F:

| Agente (v2.0.0) | Código A/F (v3.0.0) | Observação |
|---|---|---|
| Manta 00 maestro | F1 (IA) | O próprio motor de routing/orquestração — não é uma "atividade", é infraestrutura |
| Manta 01 claims | A7 | Mapeamento direto |
| Manta 02 contratual | A6 | Mapeamento direto |
| Manta 04 imobiliário | A1 + A9 | Aquisição fundiária tem componente de proposta/negociação (A1) e regulatório/desapropriação (A9) |
| Manta 05 orçamento | A3 | Mapeamento direto |
| Manta 06 modelagem | A4 | Mapeamento direto |
| Manta 07 cronograma | A5 | Mapeamento direto |
| Manta 13 bd | A1 | Mapeamento direto |
| Manta 14 apresentações | F8 + A1 | Entregável (PPTX) é padronização (F8) a serviço da atividade de proposta (A1) |
| Manta 15 advisory | A8 (+ A9/A10) | Advisory frequentemente também cobre regulatório e risco |
| Manta 16 arquiteto-ia | F1 | Meta-arquitetura de sistemas IA — função de plataforma, não atividade de engenharia |

### 2.3 Eixo F — Funcionais (8)

O eixo F descreve **capacidades de plataforma** que qualquer agente
(de qualquer S) pode invocar. São transversais por definição — não
têm "dono" de segmento nem de atividade.

| Código | Função | Descrição | Skills/MCP relacionados |
|---|---|---|---|
| F1 | IA | Orquestração de modelos, routing dinâmico de tier, meta-arquitetura de agentes | Manta 00 (maestro), Manta 16 (arquiteto-ia), model tiering (§5) |
| F2 | SharePoint | Leitura/escrita no repositório documental corporativo, metadados, versionamento | MCP `SharePoint_Manta` (find_item, upload_file, read_document, etc.), tabela `sp_agent_routing` |
| F3 | Portal | Dashboards e portais web de gestão de projeto/contrato para cliente interno/externo | portal-gestao-manta, portal-megaprojeto-builder, portal-metro-l4 |
| F4 | Extração | Parsing estruturado de PDF/CAD/planilha/edital em dado canônico (JSON) | evtea-extractor, ler-edital, ler-edital-aneel, cqp-cad-bridge, autodesk-toolkit |
| F5 | Notificação | Alertas de prazo, pendência, atividade de PR/issue, lembretes agendados | Routines (`send_later`, `create_trigger`), subscribe PR activity |
| F6 | Trace | Rastreabilidade de fonte, versionamento, log de sessão, cadeia de custódia documental | consist-guard (checagem de rastreabilidade), histórico SharePoint, session logs |
| F7 | Guardrails | Validação anti-alucinação e de consistência antes da publicação de um documento | aluci-guard, consist-guard, gate humano MN |
| F8 | Padronização | Identidade visual, templates corporativos, nomenclatura, formatos de entrega | padrao-manta, brand-guidelines, docx, pptx, xlsx |

### 2.4 Eixo D — Disciplinas (20)

O eixo D descreve **a disciplina técnica de engenharia** envolvida em
um cálculo, laudo ou parecer, independente de segmento ou atividade.
Um mesmo `D` pode aparecer em vários `S` (ex.: D02 estrutural aparece
em OAE, barragens e portos).

| Código | Disciplina | Exemplos de aplicação | Segmentos (S) típicos |
|---|---|---|---|
| D01 | Hidráulica | Drenagem, adutoras, vertedouro, calado | S1, S6, S8, S10 |
| D02 | Estrutural | NBR 6118/6122/7187, fundações, CFRD/CCR | S2, S6, S10 |
| D03 | Geotecnia | SPT, sondagem, estabilidade de talude | S1, S2, S3, S10 |
| D04 | Pavimentação | CBUQ, BGS, dimensionamento de pavimento | S1 |
| D05 | Elétrica | Subestação, LT, balizamento, SCADA | S4, S7, S9 |
| D06 | Ambiental | EIA/RIMA, licenciamento, compensação | Todos |
| D07 | Econômica | TIR, VPL, tarifa, viabilidade | S8, S9, todos via A3/A4 |
| D08 | Planejamento | PERT/CPM, curva S, marcos contratuais | Todos via A5 |
| D09 | Jurídica | Edital, aditivo, minuta contratual, FIDIC | Todos via A6/A7 |
| D10 | Comercial | Pricing, condições comerciais, negociação | Todos via A1 |
| D11 | MEP | Mecânica/elétrica/hidráulica predial | S6, S7 (terminais) |
| D12 | HVAC | Climatização de terminais e edificações | S7 |
| D13 | Acústica | Barreiras acústicas, ruído aeroportuário | S1, S7 |
| D14 | Acessibilidade | NBR 9050, acessibilidade em estações/terminais | S4, S7 |
| D15 | BIM | Modelagem IFC/Revit, clash detection | S2, S4, S6, S7 |
| D16 | Paisagismo | Urbanização, compensação paisagística | S1, S4 |
| D17 | TI | Infraestrutura de sistemas, RAG, integração | Todos (via F1-F8) |
| D18 | Comunicação | Relatórios executivos, comunicação de risco | Todos via A1/A8 |
| D19 | RH | Dotação de equipe, organograma de projeto | Todos |
| D20 | Qualidade | Controle de qualidade de obra, ensaios, ISO 9001 | Todos |

### 2.5 Dimensão complementar — ciclo de vida (8 fases)

O ciclo de vida do empreendimento continua sendo capturado no intake
(Q2), como nas versões anteriores. Ele **não** é tratado como um dos 4
eixos ortogonais porque toda combinação `S.A.F.D` pode, em princípio,
ocorrer em qualquer fase — é um atributo de contexto, não uma
dimensão independente de composição.

1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

### 2.6 Composição S.A.F.D — como os eixos se combinam

Uma consulta plenamente qualificada tem a forma `S<n>.A<n>.D<n>`
(com `F<n>` anexado quando uma função de plataforma específica é
acionada). `S` é sempre obrigatório; `A`, `F` e `D` são refinamentos
opcionais que o Maestro infere do texto da consulta ou do intake.

Exemplos de composição real:

| Código | Leitura | Caso de uso |
|---|---|---|
| `S8.A3.D07` | Saneamento + Orçamento + Econômica | Orçamento tarifário de ETE/ETA com cálculo de TIR do projeto (exemplo de referência do dossiê) |
| `S6.A2.D01` | Portos + Quantidades + Hidráulica | Cubagem de dragagem do canal de acesso e bacia de evolução |
| `S9.A6.D05` | Energia + Contratual + Elétrica | Minuta de concessão de LT/SE com cláusulas técnicas de RAP |
| `S10.A10.D02` | Barragens + Risco + Estrutural | Matriz de risco de ruptura (PAE/PSB) com verificação estrutural CFRD/CCR |
| `S2.A7.D02` | OAE + Claims + Estrutural | Claim de fundação de ponte fundamentado em perícia estrutural |
| `S1.A4.D04` | Rodovias + Modelagem + Pavimentação | Modelagem financeira de concessão considerando custo de CBUQ/BGS |
| `S7.A9.D06` | Aeroportos + Regulatório + Ambiental | Licenciamento ambiental de pista/TPS junto a ANAC e órgão ambiental |
| `S4.A5.D14` | Metrô + Cronograma + Acessibilidade | Cronograma de adequação de estações à NBR 9050 |
| `S3.A2.D03` | Ferrovia + Quantidades + Geotecnia | Volumes de terraplenagem de via permanente com base em sondagens SPT |
| `S8.F7` | Saneamento + Guardrails | `aluci-guard` obrigatório antes de publicar laudo técnico de ETE (nenhum `A`/`D` específico — F age sobre o documento inteiro) |
| `S9.F4` | Energia + Extração | `ler-edital-aneel` extraindo RAP-teto de edital de leilão de transmissão |

Regra prática: **S** decide o roteamento primário (qual agente
vertical assume a sessão); **A** decide qual handoff horizontal é
disparado; **D** decide quais normas/RAG/skills de disciplina são
carregadas; **F** pode ser acionado a qualquer momento por qualquer
agente, em qualquer combinação S.A.D, sem alterar o dono da sessão.

## 3. 5 camadas da arquitetura

```
┌────────────────────────────────────────────────────────────┐
│ C5 — Apresentação                                          │
│      artefatos React, memoriais DOCX, dashboards, PPTX     │
│      (materializa o eixo F — Portal/Padronização)          │
├────────────────────────────────────────────────────────────┤
│ C4 — Orquestração                                          │
│      Maestro (Manta 00) — router; sessões; handoffs        │
│      (materializa o eixo F — IA)                           │
├────────────────────────────────────────────────────────────┤
│ C3 — Agentes verticais (por segmento)                      │
│      Manta 03-S1..S10 (Rodovias..Barragens)                │
│      (materializa o eixo S)                                │
├────────────────────────────────────────────────────────────┤
│ C2 — Agentes horizontais (transversais)                    │
│      Manta 01/02/04-07/13-16 (claims, contratual, orçamento│
│      modelagem, cronograma, BD, PPT, advisory, arquiteto)  │
│      (materializa o eixo A, com apoio do eixo D)           │
├────────────────────────────────────────────────────────────┤
│ C1 — Skills reutilizáveis                                  │
│      SKILL.md registrados no catálogo, invocáveis por      │
│      qualquer agente. Ex.: aluci-guard, consist-guard,     │
│      padrao-manta, mk-manta, cad-quantifier.               │
│      (materializa o eixo F e fornece cálculo do eixo D)    │
├────────────────────────────────────────────────────────────┤
│ C0 — Dados                                                 │
│      Supabase (RAG chunks + routing tables), SharePoint    │
│      (projetos, SKILL.md, ARQUITETURA), storage por agente │
└────────────────────────────────────────────────────────────┘
```

## 4. Hub-and-spoke

Princípio de operação:

- **Maestro (C4) decide QUEM.** Recebe a consulta, identifica a
  coordenada `S.A.F.D` (palavras-chave + escala Q1-Q4 do intake) e
  despacha para 1 ou mais agentes de C2/C3.
- **Agente (C2/C3) decide CONTEÚDO.** Aplica conhecimento de domínio
  (disciplina `D`), interpreta o problema, define artefato, escolhe
  skills (`F`).
- **Skill (C1) EXECUTA.** Função pura: recebe entrada, produz saída.
  Sem estado próprio.

Handoffs entre agentes são declarativos: cada SKILL.md declara "quando
X aparecer, encaminhe para Y" — o Maestro é notificado e faz o
handoff sem passar pelo cliente. Na notação de eixos, um handoff é
uma mudança de `A` (ou de `S`, em casos ambíguos como UHE) mantendo a
mesma sessão de intake.

## 5. Model tiering

| Tier | Modelo | Uso típico | % de chamadas |
|---|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados | ~20% |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma | ~70% |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico | ~10% |

O Maestro faz **routing dinâmico de tier** dentro de uma sessão:
começa em Haiku para triagem, escala para Sonnet ao entrar no agente
vertical, e escala novamente para Opus se detectar complexidade
(claim + jurídico + técnico + financeiro no mesmo pleito — em
notação de eixos, uma coordenada que combina `A7` com múltiplos `D`
simultâneos costuma indicar necessidade de Opus).

## 6. Routing do Maestro (Manta 00)

Regra de dispatch Q1 (segmento — eixo S):

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

Após o dispatch primário por `S`, o Maestro faz uma **segunda
passada** para refinar `A` (que tipo de atividade — orçamento? claim?
contratual?) e opcionalmente `D` (qual disciplina de cálculo), e
apenas então decide se algum `F` precisa ser acionado antes de
entregar o artefato (ex.: `F7` guardrails sempre antes de publicar
laudo técnico).

**Casos ambíguos** (múltiplas regras de `S` aplicáveis):
- UHE (barragem + LT + SE) → dispatch primário `agente-barragens`
  + handoff a `agente-energia`.
- ETE + subestação → dispatch primário `agente-saneamento` + handoff
  a `agente-energia`.
- Porto + pista de carga → dispatch primário `agente-portos` +
  handoff a `agente-aeroportos`.
- Ver `tests/routing/prompts.md` no repo `Codex-exemplo` para lista
  atualizada de casos ambíguos e política.

## 7. Knowledge Engine (RAG)

Cada vertical carrega uma coleção RAG dedicada em Supabase, com
prefixo de storage único. As coleções indexam predominantemente
conteúdo do eixo **D** (normas técnicas de disciplina) filtrado pelo
prefixo do eixo **S** (segmento):

| Coleção | Prefixo | Fontes iniciais | Status |
|---|---|---|---|
| rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional |
| oae | oae: | NBR 7187, 6118, 6122, PRL/RioSP | ✅ Operacional |
| ferrovia | fer: | AREMA, DNIT ferroviário, concessionárias | ✅ Operacional |
| metro | mtr: | ABNT NBR-NM, ARTESP, manual STM | ✅ Operacional |
| portos | por: | ANTAQ, PIANC, ROM, editais BNDES | ✅ Operacional |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | ✅ Operacional |
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, ERAS/AySA | ✅ Operacional |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE, IEC | ✅ Operacional |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334, PNSB | ✅ Operacional |

Sub-prefixos de contexto:
- `san:br:` / `san:ar:` — saneamento por país (Brasil × Argentina AySA).
- `ene:t:` / `ene:d:` / `ene:g:` — energia por segmento (transmissão × distribuição × geração).
- `bar:c:` / `bar:t:` / `bar:e:` / `bar:r:` — barragens por tipologia
  (concreto × terra × enrocamento × rejeitos).

Migração canônica: `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`
no repo `Codex-exemplo`.

> Evolução prevista (não implementada nesta versão): coleções
> transversais por disciplina (`D`) — ex. `estrutural:*`,
> `economica:*` — para consulta cruzada entre segmentos sem depender
> do prefixo `S`. Registrar como item de backlog do Knowledge Engine.

## 8. SharePoint routing

Tabela `sp_agent_routing` mapeia cada agente vertical (eixo S) para
uma pasta canônica. É materialização direta da função **F2 —
SharePoint** do eixo funcional:

| Agente | Pasta SP | Padrões |
|---|---|---|
| agente-infraestrutura S1 | `03_Projetos/Rodovias/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S2 | `03_Projetos/OAE/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S3 | `03_Projetos/Ferrovia/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S4 | `03_Projetos/Metro/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-portos | `03_Projetos/Portos/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-aeroportos | `03_Projetos/Aeroportos/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-saneamento | `03_Projetos/Saneamento/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-energia | `03_Projetos/Energia/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-barragens | `03_Projetos/Barragens/*` | `*.pdf, *.dwg, *.xlsx` |

Cada agente vertical também tem sua pasta SKILL em
`01-agentes-fundamentais/agente-<slug>/` contendo:
- `SKILL.md` — definição canônica (frontmatter + intake + arquitetura).
- `README.md` — visão geral e onboarding.
- `refs/` — documentos técnicos de referência.
- `prompts/` — prompts amostrais e conversation starters.

## 9. Diagrama de fluxo — agente vertical

```
Usuário ─────► Maestro (Manta 00)
                   │
                   │ 1. Triagem (Haiku): identifica segmento (S/Q1),
                   │    fase (Q2), objetivo (A/Q3), formato dados (Q4)
                   ▼
              Agente vertical (ex.: agente-saneamento, S8)
                   │
                   │ 2. Ativa vertentes V1-V5 do SKILL.md
                   │    (Análise, Inteligência, Obra, DocIntel, Disciplinas)
                   │    — vertentes correspondem a subconjuntos de D
                   │
                   │ 3. Consulta RAG por prefixo S (ex.: san:*, san:ar:*)
                   │    filtrando por disciplina D quando aplicável
                   │
                   │ 4. Invoca skills (C1 / eixo F): aluci-guard (F7),
                   │    consist-guard (F7), cad-quantifier (F4),
                   │    padrao-manta (F8), etc.
                   │
                   │ 5. Decide handoffs de atividade (eixo A):
                   │    agente-05 (A3 orçamento), agente-07 (A5
                   │    cronograma), agente-contratual (A6),
                   │    agente-claims (A7), etc.
                   ▼
              Artefato (C5): React app + memorial DOCX
                   │
                   ▼
              Usuário ← resposta com fontes, quantitativos, risco
```

## 10. Matriz de composição — casos de uso

Exemplo de matriz reduzida cruzando `S` (linhas) com `A` (colunas)
para os segmentos S6-S10, mostrando onde já existe cobertura
operacional (✅), cobertura parcial via skill genérica (⚡) e lacuna
a endereçar (⬜):

| S \ A | A1 Proposta | A2 Quantid. | A3 Orçamento | A5 Cronog. | A6 Contratual | A7 Claims | A8 Advisory | A9 Regulat. |
|---|---|---|---|---|---|---|---|---|
| S6 Portos | ✅ | ✅ (cad-quantifier) | ✅ | ✅ | ✅ | ⚡ | ⚡ | ✅ |
| S7 Aeroportos | ✅ | ✅ | ✅ | ✅ | ✅ | ⚡ | ⚡ | ✅ |
| S8 Saneamento | ✅ | ✅ | ✅ | ✅ | ✅ | ⚡ | ✅ | ✅ |
| S9 Energia | ✅ | ✅ | ✅ | ✅ | ✅ | ⚡ | ✅ | ✅ |
| S10 Barragens | ✅ | ✅ | ✅ | ✅ | ✅ | ⚡ | ⚡ | ✅ |

Leitura: os handoffs de `A1` (proposta), `A3` (orçamento), `A5`
(cronograma) e `A6` (contratual) já estão validados para os 5
segmentos novos (S6-S10), pois reaproveitam os agentes horizontais
Manta 13/05/07/02 já operacionais desde v1.0.0. `A7` (claims) e `A8`
(advisory) ainda dependem de handoff manual — nenhum agente vertical
S6-S10 tem, até esta versão, histórico de claim próprio equivalente
ao acumulado por S1/S2 (rodovias/OAE); tratar como item de reforço
de treinamento/exemplos nas próximas revisões de SKILL.md.

Exemplos de sessão completa, com as 4 coordenadas explícitas:

1. **`S8.A3.F4.D07`** — Cliente AySA pede orçamento tarifário de nova
   ETE. Maestro despacha para `agente-saneamento` (S8) → handoff para
   `Manta 05` (A3, orçamento) → skill `F4` (extração) lê edital/EVTE
   → cálculo aplica disciplina `D07` (econômica, TIR/VPL) → `F7`
   (guardrails) valida normas SNIS citadas antes de publicar.

2. **`S2.A7.F7.D02`** — Claim de fundação de ponte. `agente-infraestrutura`
   (S2, OAE) → handoff para `Manta 01` (A7, claims) → disciplina `D02`
   (estrutural, NBR 6118/6122) fundamenta o quantum → `aluci-guard`
   (F7) audita normas citadas antes de fechar o parecer.

3. **`S9.F4.A6.D05`** — Leitura de edital ANEEL de leilão de
   transmissão. `agente-energia` (S9) aciona `ler-edital-aneel` (F4)
   para extrair RAP-teto → handoff para `Manta 02` (A6, contratual)
   para redigir minuta de participação, com disciplina `D05`
   (elétrica) validando parâmetros técnicos do anexo.

## 11. Changelog v2.0 → v3.0

### Adicionado
- **4 eixos ortogonais (S × A × F × D)** substituindo a leitura de
  "3 eixos" da v2.0.0: Segmentos, Atividades, Funcionais, Disciplinas.
- Tabela completa do **Eixo A** — 10 atividades (proposta, quantidades,
  orçamento, modelagem, cronograma, contratual, claims, advisory,
  regulatório, risco), com mapeamento explícito para os agentes
  horizontais existentes.
- Tabela completa do **Eixo F** — 8 funções de plataforma (IA,
  SharePoint, Portal, Extração, Notificação, Trace, Guardrails,
  Padronização), com mapeamento para skills/MCP existentes.
- Tabela completa do **Eixo D** — 20 disciplinas técnicas (hidráulica,
  estrutural, geotecnia, pavimentação, elétrica, ambiental, econômica,
  planejamento, jurídica, comercial, MEP, HVAC, acústica,
  acessibilidade, BIM, paisagismo, TI, comunicação, RH, qualidade).
- Notação de composição `S.A.F.D` com 11 exemplos de código completo
  (§2.6) e 3 exemplos de sessão passo a passo (§10).
- Matriz reduzida de cobertura S6-S10 × A1-A9 (§10), identificando
  lacunas de claims/advisory nos segmentos novos.
- Tabela de reconciliação "Horizontais (v2.0.0) → A/F (v3.0.0)".

### Mudado
- Seção 2 renomeada de "3 eixos do sistema" para "4 eixos ortogonais
  do sistema", com subseções 2.1-2.6.
- Ciclo de vida (8 fases) reclassificado de "Eixo 3" para "dimensão
  complementar" — atributo de intake, não eixo ortogonal de composição.
- Diagrama de fluxo (§9) e routing do Maestro (§6) anotados com
  referências às coordenadas S/A/F/D.
- Numeração de seções ajustada: nova seção 10 "Matriz de composição",
  changelog e referências deslocados para 11 e 12.

### Mantido (sem alteração)
- Estrutura de 5 camadas (C0-C5).
- Model tiering (Haiku → Sonnet → Opus).
- Padrão hub-and-spoke.
- Todos os 20 agentes (horizontais Manta 00/01/02/04-07/13-16 e
  verticais S1-S10).
- Coleções RAG e routing SharePoint (§7, §8) — sem mudança de schema
  nesta versão; evolução para coleções por disciplina (`D`) fica
  registrada como backlog.

## 12. Referências

- **Repositório mestre**: `MN1970/Codex-exemplo` (branch/PR:
  `claude/manta-agents-s6-s10-7qklcw`).
- **Mirror operacional**: `viniciusmagnos/manta-hub` (mesma branch,
  PR #3).
- **Registro completo dos 20 agentes**: `CLAUDE.md` no repo mestre.
- **Definições canônicas dos verticais**: `.claude/agents/*.md` no repo mestre.
- **SKILL.md em SP**: `Documentos Compartilhados/04_IA/Manta-Maestro/
  01-agentes-fundamentais/agente-*/SKILL.md`.
- **Coleções RAG**: Supabase (migração v4.2 já aplicada — ver §7).
- **Rotas SP**: tabela `sp_agent_routing` (ver §8).
- **Runbook de deploy v4.2**: `docs/DEPLOY-v4.2.md` no repo mestre.
- **Prompts de teste do routing**: `tests/routing/prompts.md` no repo mestre.
- **Dossiê de proposta dos 4 eixos (S×A×F×D)**: referência de origem
  desta revisão v3.0.0 — versionar cópia definitiva junto ao próximo
  ticket de deploy quando o dossiê for anexado formalmente ao repo.

---

_Documento vivo. Alterações via pull request no repo `MN1970/Codex-exemplo`,
aprovação MN, e re-upload aqui no SharePoint como nova versão._
