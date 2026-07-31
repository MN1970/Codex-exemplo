# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.0** (2026-07-31) — consolidação v3.x (modelo conceitual de
4 eixos S×A×F×D) + v4.2 (expansão operacional S6–S10). Ticket
`MNT-2026-CONSOLIDACAO-ARCH-V5`.

> **Nota de proveniência**: esta revisão integra o "Dossiê HTML v2.0"
> (modelo de 4 eixos) ao estado operacional real do repositório
> (20 agentes, 9 coleções RAG confirmadas). Itens do dossiê que não
> puderam ser confirmados contra o estado operacional deste repo estão
> marcados explicitamente como **pendente de validação** — ver seção
> "Gaps abertos". Nenhum número não verificado foi apresentado aqui
> como fato consolidado.

---

## Sumário

1. [Modelo de 4 eixos (S×A×F×D)](#modelo-de-4-eixos-saf%C3%97d)
2. [Eixo S — Segmentos](#eixo-s--segmentos)
3. [Eixo A — Atividades](#eixo-a--atividades)
4. [Eixo F — Funcionais](#eixo-f--funcionais)
5. [Eixo D — Disciplinas](#eixo-d--disciplinas)
6. [Eixo temporal — Ciclo de vida](#eixo-temporal--ciclo-de-vida-8-fases)
7. [Modelo de composição S.A.D](#modelo-de-composição-sad)
8. [Mapa completo de agentes — 20 agentes](#mapa-completo-de-agentes--20-agentes)
9. [Routing — Maestro (Manta 00)](#routing--maestro-manta-00)
10. [RAG — Coleções em Supabase](#rag--coleções-em-supabase)
11. [SharePoint — Routing rules](#sharepoint--routing-rules-sp_agent_routing)
12. [Model tiering](#model-tiering)
13. [Gaps abertos / pendências](#gaps-abertos--pendências)
14. [Questionário de decisão para MN](#questionário-de-decisão-para-mn)
15. [Deploy checklist v5.0](#deploy-checklist-v50)
16. [Arquivos deste repositório](#arquivos-deste-repositório)
17. [Histórico de versões](#histórico-de-versões)

---

## Modelo de 4 eixos (S×A×F×D)

A v5.0 formaliza o modelo do dossiê v2.0: qualquer consulta ao Maestro
se posiciona na interseção de **4 eixos ortogonais**, mais um eixo
temporal auxiliar que se aplica a qualquer composição:

| Eixo | Pergunta que responde | Cardinalidade | Exemplos |
|------|------------------------|---------------|----------|
| **S** — Segmento | Qual o domínio de infraestrutura? | S1–S11 (+ S12/S13 TBD) | Rodovias, Portos, Saneamento |
| **A** — Atividade | Qual o tipo de entrega/trabalho? | A1–A10 | Orçamento, Cronograma, Claims |
| **F** — Funcional | Qual capacidade técnica transversal é usada? | F1–F8 | RAG/routing, SharePoint, Guardrails |
| **D** — Disciplina | Qual disciplina de engenharia/negócio? | D01–D20 | Hidráulica, Estrutural, Jurídico |
| *(temporal)* Ciclo de vida | Em que fase do projeto? | 8 fases | Projeto básico, Obra, DD |

Esta é uma **mudança de modelo, não de operação**: os 20 agentes atuais
(Eixo 1 "Horizontais" + Eixo 2 "Verticais" do v4.2) continuam existindo
e sendo os únicos executores reais. Os eixos A/F/D são uma camada de
**classificação e composição** por cima do registro de agentes — eles
não criam agentes novos por si só, mas orientam handoffs e contexto.
Compatibilidade com o routing v4.2 (por segmento/keyword) é mantida
integralmente — ver seção de Routing.

---

## Eixo S — Segmentos

Cobertura por segmento de infraestrutura. **Renumeração v5.0**: o
dossiê e o registro de produção do Maestro (skill `manta-maestro`,
v5.0.1) inserem **Edificações como novo S6**, deslocando Portos → S7,
Aeroportos → S8, Saneamento → S9, Energia → S10 e Barragens → S11.
Isso reconcilia a numeração deste repositório (que ainda usa S6=Portos
… S10=Barragens no v4.2) com a numeração já em produção.

> ⚠️ **Pendência de sincronização confirmada**: os arquivos
> `.claude/agents/agente-portos.md`, `agente-aeroportos.md`,
> `agente-saneamento.md`, `agente-energia.md` e `agente-barragens.md`
> **ainda trazem os códigos legados** (`Manta 03-S6` … `Manta 03-S10`)
> em frontmatter e corpo de texto — verificado por leitura direta
> destes 5 arquivos em 2026-07-31. Isso **não quebra o routing**
> porque o dispatch do Maestro é feito por *slug* de agente
> (`agente-portos`, `agente-energia`, …), não pelo número do
> segmento — mas os arquivos precisam de um patch de sincronização
> antes que a numeração S7–S11 abaixo seja citada externamente como
> definitiva. Ação de acompanhamento: abrir ticket para atualizar os
> 5 frontmatters (fora do escopo desta consolidação de CLAUDE.md).

| Código v5.0 | Código v4.2 (legado) | Segmento | Agente | Status |
|---|---|---|---|---|
| S1 | S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| **S6** | *(novo)* | **Edificações** | agente-edificacoes | 🔲 **Planejado** — não há `.claude/agents/agente-edificacoes.md` neste repo; segmento citado no registro de produção (skill `manta-maestro`), aguardando criação canônica aqui |
| S7 | S6 | Portos | agente-portos | ✅ Operacional (frontmatter ainda cita S6 — ver pendência acima) |
| S8 | S7 | Aeroportos | agente-aeroportos | ✅ Operacional (frontmatter ainda cita S7 — ver pendência acima) |
| S9 | S8 | Saneamento | agente-saneamento | ✅ Operacional — PRIORIDADE AySA (frontmatter ainda cita S8) |
| S10 | S9 | Energia | agente-energia | ✅ Operacional — ANEEL/State Grid (frontmatter ainda cita S9) |
| S11 | S10 | Barragens | agente-barragens | ✅ Operacional (frontmatter ainda cita S10) |
| S12 | — | **TBD** | — | 🟡 **Não resolvido** — candidato citado em investigação: Óleo & Gás. Sem agente, sem SKILL.md, sem entrada em routing. Decisão pendente MN (ver Gaps abertos, G014). |
| S13 | — | **TBD** | — | 🟡 **Não resolvido** — candidato não identificado com clareza (possível duplicata/erro de cadastro de Edificações). Decisão pendente MN antes de formalizar. |

---

## Eixo A — Atividades

Novo eixo formalizado nesta consolidação, descrevendo o **tipo de
entrega** independente do segmento. Cada atividade mapeia, quando
existente, para o agente horizontal (Eixo "Horizontais" da seção de
agentes) que a executa hoje.

| Código | Atividade | Agente horizontal correspondente | Status do mapeamento |
|--------|-----------|-----------------------------------|-----------------------|
| A1 | Proposta | Manta 13 (bd) + Manta 14 (apresentações) | ✅ Mapeado (2 agentes) |
| A2 | Quantidades | — | 🟡 Sem agente dedicado hoje; hoje coberto por skills (`cad-quantifier`, `evtea-quantifier`) invocadas dentro dos verticais |
| A3 | Orçamento | Manta 05 (orçamento) | ✅ Mapeado |
| A4 | Modelagem financeira | Manta 06 (modelagem) | ✅ Mapeado |
| A5 | Cronograma | Manta 07 (cronograma) | ✅ Mapeado |
| A6 | Contratual | Manta 02 (contratual) | ✅ Mapeado |
| A7 | Claims | Manta 01 (claims) | ✅ Mapeado |
| A8 | Advisory | Manta 15 (advisory) | ✅ Mapeado |
| A9 | Regulatório | — | 🟡 **Rubrica pendente** (assim descrito na investigação-fonte) — hoje disperso entre agentes verticais (ex.: ANEEL em Manta 03-S10, ANAC em Manta 03-S8); sem agente horizontal próprio |
| A10 | Risco | — | 🟡 Sem agente dedicado hoje; hoje coberto parcialmente por Manta 15 (advisory) e Manta 16 (arquiteto-ia) conforme o caso |

**Leitura prática**: A2, A9 e A10 são os três pontos em aberto do eixo
Atividades — não há agente horizontal 1:1 hoje. Antes de rotear uma
consulta classificada nessas atividades, o Maestro deve tratá-la como
handoff para o vertical de segmento (S) mais próximo, e não assumir um
agente horizontal inexistente.

---

## Eixo F — Funcionais

Capacidades técnicas transversais, usadas por qualquer agente
independentemente do segmento ou atividade. Mapeadas, quando possível,
para skills/sistemas já existentes no ecossistema Manta.

| Código | Funcional | Skill/sistema correspondente hoje |
|--------|-----------|-------------------------------------|
| F1 | IA (routing, model tiering) | Maestro (Manta 00) + lógica de routing desta seção |
| F2 | SharePoint (indexação, sync) | MCP `SharePoint_Manta` (leitura); escrita/upload ainda manual — ver Gaps abertos |
| F3 | Portal (web, SSO, permissões) | `portal-gestao-manta`, `portal-megaprojeto-builder`, `portal-metro-l4` (skills) |
| F4 | Extração (PDF/DWG parser) | `autodesk-toolkit`, `cqp-cad-bridge`, `evtea-extractor`, `pdf` (skills) |
| F5 | Notificação (email, Slack, webhook) | `slack-gif-creator` (parcial); notificação por e-mail/webhook **sem skill dedicada hoje** — gap |
| F6 | Trace (audit log, approval gates) | Gate humano MN nos deploy checklists (processo, não sistema); sem trilha de auditoria automatizada confirmada |
| F7 | Guardrails (validação, aluci-guard, consist-guard) | `aluci-guard`, `consist-guard`, `context-guardian` (skills) |
| F8 | Padronização (templates, estilos, nomenclatura) | `padrao-manta`, `cl-design`, `brand-guidelines` (skills) |

**Leitura prática**: F5 e F6 não têm skill/sistema dedicado confirmado
neste repositório — tratar como gap de implementação, não como
funcionalidade já disponível.

---

## Eixo D — Disciplinas

Disciplinas de engenharia e negócio, usadas como refinamento dentro de
qualquer segmento (S) ou atividade (A). Este eixo é o mais granular e
tipicamente aparece como o terceiro/quarto componente de uma
composição (ex.: `S9.A3.D07`).

**D01–D10 — Disciplinas clássicas**

| Código | Disciplina |
|--------|------------|
| D01 | Hidráulica |
| D02 | Estrutural |
| D03 | Geotecnia |
| D04 | Pavimentação |
| D05 | Eletromecânica |
| D06 | Ambiental |
| D07 | Financeiro |
| D08 | Planejamento |
| D09 | Jurídico |
| D10 | Comercial |

**D11–D20 — Disciplinas secundárias**

| Código | Disciplina |
|--------|------------|
| D11 | MEP (mecânica/elétrica/hidráulica predial) |
| D12 | HVAC |
| D13 | Acústica |
| D14 | Acessibilidade |
| D15 | BIM |
| D16 | Paisagismo |
| D17 | TI |
| D18 | Comunicação |
| D19 | RH |
| D20 | Qualidade |

> Este eixo é a formalização mais nova do modelo v5.0 e ainda **não
> possui rotina de validação automatizada** (nenhum teste de routing
> em `tests/routing/prompts.md` cobre disciplinas hoje — apenas
> segmentos). Tratar D01–D20 como taxonomia de apoio à composição, não
> como eixo com routing determinístico testado.

---

## Eixo temporal — Ciclo de vida (8 fases)

Mantido do v4.2 sem alteração — aplica-se a qualquer composição dos 4
eixos acima, via Q2 do intake:

1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## Modelo de composição S.A.D

Uma consulta resolve, na prática, como interseção de S (segmento),
A (atividade) e D (disciplina) — o eixo F entra como capacidade
utilizada internamente pelo agente despachado, não como parte do
endereçamento primário:

```
S9.A3.D07  = Saneamento + Orçamento + Financeiro
            → Manta 05 (agente-orcamento) com contexto de saneamento
              (RAG san:*, handoff de agente-saneamento)

S10.A7.D09 = Energia + Claims + Jurídico
            → Manta 01 (agente-claims) com contexto de energia
              (RAG ene:*, handoff de agente-energia)

S11.A5.D08 = Barragens + Cronograma + Planejamento
            → Manta 07 (agente-cronograma) com contexto de barragens
              (RAG bar:*, handoff de agente-barragens)
```

Cada composição pode ser delegada a 1+ agentes em paralelo (teto de 8
sub-agentes simultâneos, conforme prática já usada pelo Maestro).
Quando A cai em A2/A9/A10 (sem agente horizontal mapeado — ver Eixo A),
o dispatch primário deve ser o vertical de S, não um horizontal
inexistente.

---

## Mapa completo de agentes — 20 agentes

Contagem confirmada por leitura direta do repositório e da
`ARQUITETURA-AGENTES-IA.md` (SharePoint mirror): **11 horizontais + 9
verticais operacionais** = 20 agentes (S5 Túneis é parcial/coberto,
não conta como agente adicional; S6 Edificações é planejado, ainda não
implementado, também não soma ao total operacional de 20).

### Horizontais (transversais a todos os segmentos) — 11 agentes

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

### Verticais por segmento (C3) — 9 agentes operacionais + 1 parcial + 1 planejado

| Código v5.0 | Segmento | Agente | Status |
|--------|----------|--------|--------|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| S6 | Edificações | agente-edificacoes | 🔲 Planejado (sem arquivo canônico neste repo) |
| S7 | Portos | agente-portos | ✅ Operacional (criado 2026-07-05) |
| S8 | Aeroportos | agente-aeroportos | ✅ Operacional (criado 2026-07-05) |
| S9 | Saneamento | agente-saneamento | ✅ Operacional (criado 2026-07-05) — PRIORIDADE AySA |
| S10 | Energia | agente-energia | ✅ Operacional (criado 2026-07-05) — ANEEL/State Grid |
| S11 | Barragens | agente-barragens | ✅ Operacional (criado 2026-07-05) |

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento para Q1 do intake. **Inalterada em relação ao
v4.2** — o dispatch é por *slug* de agente (não por número de
segmento), portanto a renumeração S6→S7…S10→S11 do Eixo S não exige
mudança nestas regras:

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

**Casos ambíguos** (documentados em `tests/routing/prompts.md`, mantidos
sem alteração):
- UHE (barragem + LT + SE) → dispatch primário `agente-barragens` +
  handoff `agente-energia` (política ainda não formalizada — ver
  `tests/routing/prompts.md`, seção "Casos ambíguos").
- ETE + subestação → dispatch primário `agente-saneamento` + handoff
  `agente-energia`.
- Porto + pista de carga → dispatch primário `agente-portos` + handoff
  `agente-aeroportos`.
- Adutora atravessa barragem de rejeitos → `agente-saneamento` com
  consulta técnica ao `agente-barragens`.

---

## RAG — Coleções em Supabase

**Correção desta consolidação**: o CLAUDE.md v4.2 listava apenas as 5
coleções novas. A `ARQUITETURA-AGENTES-IA.md` (SharePoint, v2.0.0) e o
runbook de integração Cowork confirmam **9 coleções operacionais**
(4 pré-existentes + 5 do v4.2). Tabela completa abaixo:

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional (pré-existente) |
| oae | oae: | NBR 7187, 6118, 6122, PRL/RioSP | ✅ Operacional (pré-existente) |
| ferrovia | fer: | AREMA, DNIT ferroviário, concessionárias | ✅ Operacional (pré-existente) |
| metro | mtr: | ABNT NBR-NM, ARTESP, manual STM | ✅ Operacional (pré-existente) |
| portos | por: | ANTAQ, PIANC, ROM, editais BNDES | ✅ v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | ✅ v4.2 |
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, ERAS/AySA | ✅ v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE, IEC, NBR 5422 | ✅ v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, SNISB, Lei 12.334/14.066, NBR 13028/8681 | ✅ v4.2 |
| edificações | edi: | *(a definir)* | 🔲 Planejado — sem coleção criada, aguarda decisão sobre agente S6 |

Sub-prefixos de contexto (mantidos do v4.2):
- `san:br:` / `san:ar:` — saneamento por país (Brasil × Argentina AySA).
- `ene:t:` / `ene:d:` / `ene:g:` — energia por transmissão/distribuição/geração.
- `bar:c:` / `bar:t:` / `bar:e:` / `bar:r:` — barragens por tipologia
  (concreto × terra × enrocamento × rejeitos).

Migração canônica das 5 coleções v4.2:
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` — é uma
**migração candidata**, ainda não confirmada como aplicada em produção
(ver Gaps abertos, item de contagem de chunks).

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |
| agente-edificacoes | 03_Projetos/Edificacoes/* *(a criar)* | *.pdf, *.dwg, *.xlsx — 🔲 planejado |

Runbook de deploy manual (Supabase + SharePoint) em
`docs/DEPLOY-v4.2.md` — ainda referenciado, sem runbook v5.0 dedicado
até que S6/S12/S13 sejam resolvidos.

---

## MODEL TIERING

Mantido do v4.2 / `ARQUITETURA-AGENTES-IA.md` sem alteração:

| Tier | Modelo | Uso típico |
|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico |

O Maestro escala dinamicamente de tier dentro de uma sessão (Haiku →
Sonnet ao entrar no vertical → Opus se detectar complexidade — claim +
jurídico + técnico + financeiro no mesmo pleito).

---

## GAPS ABERTOS / PENDÊNCIAS

Itens levantados na investigação de consolidação que **não foram
resolvidos nesta revisão** — listados aqui como pendências rastreáveis,
não como fatos assumidos no corpo do documento acima:

- **Embedder**: há registro de decisão por `bge-m3` (1024-d) em
  paralelo a `bge-small-en-v1.5` (384-d) supostamente em produção.
  **Não verificado neste repositório** — nenhum dos dois é citado em
  nenhum arquivo de migração ou config aqui presente. Ação: auditar
  qual embedder está de fato em uso antes de documentar como decidido.
- **Contagem de chunks RAG**: há uma cifra de "204 chunks reais"
  circulando em material de investigação, contra um valor menor
  documentado anteriormente. **Nenhum dos dois números é verificável a
  partir dos arquivos deste repositório** (a migração SQL registra
  *coleções*, não *chunks*, e é candidata/não confirmada como aplicada).
  Ação: consultar `list_tables`/`execute_sql` no projeto Supabase real
  antes de citar qualquer contagem em documento canônico.
- **Projeto Supabase de referência**: há menção a um project ref que
  retornaria "permission denied" e a outros 3 projetos citados como
  inativos. **Não verificado nesta revisão** (nenhuma chamada MCP
  Supabase foi feita para confirmar) — tratar como hipótese a auditar,
  não como estado confirmado.
- **S12/S13**: sem definição. Candidato a S12 (Óleo & Gás) mencionado
  em material de investigação, sem SKILL.md, sem agente, sem entrada de
  routing. S13 sem candidato claro. Ver seção Eixo S.
- **S6 Edificações**: citado no registro de produção (skill
  `manta-maestro`) mas sem arquivo canônico `.claude/agents/` neste
  repositório. Tratar como planejado, não operacional.
- **Sincronização de numeração S nos frontmatters dos 5 agentes v4.2**:
  ver aviso na seção Eixo S.
- **F5 (Notificação) e F6 (Trace)**: sem skill/sistema dedicado
  confirmado — ver Eixo F.
- **A2 (Quantidades), A9 (Regulatório), A10 (Risco)**: sem agente
  horizontal dedicado — ver Eixo A.

---

## QUESTIONÁRIO DE DECISÃO PARA MN

1. **Embedder**: manter `bge-small` (econômico, já supostamente em
   produção) ou migrar para `bge-m3` (maior dimensionalidade/qualidade)?
   Requer auditoria prévia do estado real antes da decisão.
2. **S12/S13**: formalizar como novos segmentos (e com qual escopo) ou
   remover a referência? Depende de confirmar a origem do cadastro.
3. **S6 Edificações**: priorizar criação do agente/SKILL.md nesta
   sprint ou manter como planejado sem prazo?
4. **Supabase de referência (project ref citado como inacessível)**:
   referência morta a remover da documentação ou migração pendente a
   executar?
5. **Timeline de merge**: em qual sprint este v5.0 vai para `main`?
   (Consolidação registrada em 2026-07-31.)

---

## DEPLOY CHECKLIST v5.0

- [x] Consolidar modelo de 4 eixos (S×A×F×D) no CLAUDE.md master
- [x] Corrigir tabela de coleções RAG (9 confirmadas, não 5)
- [x] Registrar S6 (Edificações) e S12/S13 (TBD) no Eixo S
- [x] Mapear Eixo A (Atividades) aos agentes horizontais existentes
- [x] Mapear Eixo F (Funcionais) às skills/sistemas existentes
- [x] Documentar Eixo D (Disciplinas) D01-D20
- [ ] Sincronizar frontmatters dos 5 agentes v4.2 com numeração S7-S11
- [ ] Criar `agente-edificacoes.md` (S6) — decisão de prioridade pendente MN
- [ ] Resolver S12/S13 (questionário de decisão, item 2)
- [ ] Auditar embedder real em produção (bge-small vs bge-m3)
- [ ] Auditar contagem real de chunks RAG via Supabase MCP
- [ ] Auditar acessibilidade do projeto Supabase referenciado como indisponível
- [ ] Criar coleção RAG `edificacoes` (`edi:`) quando S6 for priorizado
- [ ] Rodar aluci-guard sobre este documento antes de merge
- [ ] Rodar consist-guard sobre este documento antes de merge
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                              # este arquivo (master registry, v5.0)
├── README.md
├── .claude/
│   └── agents/
│       ├── agente-portos.md               # S7 (frontmatter ainda cita S6 — pendente)
│       ├── agente-aeroportos.md           # S8 (frontmatter ainda cita S7 — pendente)
│       ├── agente-saneamento.md           # S9 — prioridade AySA (frontmatter ainda cita S8)
│       ├── agente-energia.md              # S10 — ANEEL/State Grid (frontmatter ainda cita S9)
│       └── agente-barragens.md            # S11 (frontmatter ainda cita S10 — pendente)
├── docs/
│   ├── DEPLOY-v4.2.md                     # runbook manual (Supabase + SharePoint)
│   └── COWORK-INTEGRATION.md              # runbook de integração Maestro ↔ Cowork
├── sharepoint/
│   ├── README.md
│   └── 00-arquitetura/
│       └── ARQUITETURA-AGENTES-IA.md      # v2.0.0 — pendente bump para v3.0.0 (4 eixos)
├── supabase/
│   └── migrations/
│       └── 2026_07_05_v4_2_agents_s6_s10.sql  # migração candidata, não confirmada como aplicada
└── tests/
    └── routing/
        └── prompts.md                     # smoke tests de routing por segmento
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, S1..S5) vivem no
repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais novos
(S7–S11) e do mapa de routing/eixos.

---

## Histórico de versões

- **v5.0** (2026-07-31) — consolidação do modelo de 4 eixos (S×A×F×D)
  do dossiê v3.x com o estado operacional v4.2. Adiciona Eixo A
  (Atividades A1-A10), Eixo F (Funcionais F1-F8), Eixo D (Disciplinas
  D01-D20). Renumera Eixo S para S1-S11 (Edificações inserido como S6,
  Barragens torna-se S11) mantendo compatibilidade de routing por
  slug de agente. Registra S12/S13 como TBD. Corrige tabela de
  coleções RAG (9 confirmadas, não 5). Documenta gaps abertos e
  questionário de decisão para MN em vez de resolvê-los
  unilateralmente. Ticket `MNT-2026-CONSOLIDACAO-ARCH-V5`.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
