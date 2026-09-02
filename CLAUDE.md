# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.4** (2026-08-31) — **Padrão Motiva ligado ao routing e aos
agentes de output**: nova keyword de cliente na seção ROUTING
(`Motiva|CCR Rodovias|SP-258|SP-330|Contorno Apucarana` → aplica
`docs/PADRAO-OUTPUT-MOTIVA.md` como co-agente de padrão de output) +
referência direta ao documento em `agente-orcamento.md`,
`agente-cronograma.md`, `agente-apresentacoes.md` e
`agente-contratual.md` (os 4 horizontais que de fato geram o
entregável EAP/cronograma/PPT/codificação). Upload dos templates para
o SharePoint da equipe segue pendente (ação manual — ver Gaps).

Consolida v5.3 (2026-08-30) — **Templates Motiva implementados**:
`docs/templates/EAP-PADRAO-MOTIVA.xlsx` e
`docs/templates/PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx`, aprovados
por MN, reproduzindo o padrão documentado em v5.2 (paleta neutra Manta
até confirmação da marca).

Consolida v5.2 (2026-08-30) — **Padrões de output por cliente**: nova
seção que referencia o padrão de entregável (EAP em Excel/PPT,
relatório, codificação de documentos, identidade visual) por cliente,
começando pela Motiva (ex-CCR Rodovias).

Consolida v5.1 (2026-08-02) — **Design Agents (P3-04): ESG/Impact Design Agent**.
Expande o framework com novo agente horizontal **Manta 20 (manta-20-esg)** —
assessment ESG, 4 dimensões (Ambiental/Social/Governança/Integração),
integração com S6–S10, RAG + compliance mapping.

Consolida v5.0.1 operacional (2026-07-31):
- **v5.0.0 operacional** (aprovado 2026-07-22): 20 agentes em produção,
  infraestrutura Maestro-OS v6.0 completa (APScheduler, ML, observability)
- **v5.0 consolidação** (2026-07-31): 4 eixos (S×A×F×D) formalizados,
  gaps G010/G012/G014 resolvidos, 15 Sonnets investigação paralela.

Tickets: `MNT-2026-CONSOLIDACAO-ARCH-V5` (operacional) +
`MNT-2026-P3-04-ESG-AGENT` + `MNT-2026-MOTIVA-258-PATTERN` (novo,
padrão de output por cliente).

> **Nota de proveniência**: este arquivo **reconcilia** dois work streams
> paralelos na mesma data:
> 1. **v5.0.0 (main, 22/07)** — implementação operacional aprovada com
>    todos os agentes em produção
> 2. **v5.0 (branch, 31/07)** — formalização de arquitetura com gaps
>    investigados e decisões explicitadas
> 
> Diferenças encontradas durante merge (numeração segmentos, status de
> produção) estão documentadas neste arquivo. Decisões divergentes foram
> preservadas em notas explícitas (ver "Eixo S", "Gaps abertos") em vez
> de silenciosamente alteradas.

---

## Sumário

1. [Modelo de 4 eixos (S×A×F×D)](#modelo-de-4-eixos-saf%C3%97d)
2. [Eixo S — Segmentos](#eixo-s--segmentos)
3. [Eixo A — Atividades](#eixo-a--atividades)
4. [Eixo F — Funcionais](#eixo-f--funcionais)
5. [Eixo D — Disciplinas](#eixo-d--disciplinas)
6. [Eixo temporal — Ciclo de vida](#eixo-temporal--ciclo-de-vida-8-fases)
7. [Modelo de composição S.A.D](#modelo-de-composição-sad)
8. [Mapa completo de agentes — 20 operacionais + 2 propostos](#mapa-completo-de-agentes--20-operacionais--2-propostos)
9. [Routing — Maestro (Manta 00)](#routing--maestro-manta-00)
10. [RAG — Coleções em Supabase](#rag--coleções-em-supabase)
11. [SharePoint — Routing rules](#sharepoint--routing-rules-sp_agent_routing)
12. [Padrões de output por cliente](#padrões-de-output-por-cliente)
13. [Model tiering](#model-tiering)
14. [Gaps abertos / pendências](#gaps-abertos--pendências)
15. [Questionário de decisão para MN](#questionário-de-decisão-para-mn)
16. [Deploy checklist v5.0](#deploy-checklist-v50)
17. [Arquivos deste repositório](#arquivos-deste-repositório)
18. [Histórico de versões](#histórico-de-versões)

---

## Modelo de 4 eixos (S×A×F×D)

A v5.0 formaliza o modelo do dossiê/arquitetura v3.0.0: qualquer
consulta ao Maestro se posiciona na interseção de **4 eixos
ortogonais**, mais um eixo temporal auxiliar que se aplica a qualquer
composição:

| Eixo | Pergunta que responde | Cardinalidade | Exemplos |
|------|------------------------|---------------|----------|
| **S** — Segmento | Qual o domínio de infraestrutura? | S1–S10 operacionais (+ S11 identificado/não formalizado, S12/S13 propostos) | Rodovias, Portos, Saneamento |
| **A** — Atividade | Qual o tipo de entrega/trabalho? | A1–A10 | Orçamento, Cronograma, Claims |
| **F** — Funcional | Qual capacidade técnica transversal é usada? | F1–F8 | RAG/routing, SharePoint, Guardrails |
| **D** — Disciplina | Qual disciplina de engenharia/negócio? | D01–D20 | Hidráulica, Estrutural, Jurídico |
| *(temporal)* Ciclo de vida | Em que fase do projeto? | 8 fases | Projeto básico, Obra, DD |

Documentação completa de cada eixo A/F/D vive em documentos dedicados
(ver seção "Arquivos deste repositório"); este CLAUDE.md traz o
registro-índice e as tabelas de decisão que afetam routing. Isto é
uma **mudança de modelo, não de operação**: os 20 agentes atuais
continuam sendo os únicos executores reais — os eixos A/F/D são uma
camada de classificação/composição por cima do registro de agentes.

Documento de referência canônico e mais detalhado deste modelo:
`sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` **v3.0.0**
(2026-07-31, substitui v2.0.0).

---

## Eixo S — Segmentos

### ⚠️ Divergência de numeração encontrada e reconciliada nesta versão

Duas convenções de numeração circularam em paralelo nesta rodada de
consolidação:

- **Convenção A (mantida — adotada nesta versão)**: preserva a
  numeração legada do v4.2 sem alteração (S6=Portos … S10=Barragens) e
  **anexa** novos segmentos ao final (S12, S13). É o que está em
  `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` **v3.0.0**
  (documento de arquitetura dedicado, que registra explicitamente
  "Edificações... não faz parte do escopo S1-S10 desta versão"), e é o
  que está de fato implementado nos arquivos de agente mais recentes:
  `.claude/agents/agente-portos.md` (v1.1.0, ainda `Manta 03-S6`),
  `.claude/agents/agente-oleo-gas.md` (`Manta 03-S12`),
  `.claude/agents/agente-edificacoes.md` (`Manta 03-S13`).
- **Convenção B (descartada — não usar)**: renumera inserindo
  Edificações como novo S6 e desloca Portos→S7 … Barragens→S11. Esta
  convenção aparece em `docs/DISCIPLINAS-D01-D20.md`,
  `docs/ATIVIDADES-A1-A10.md` e numa menção isolada em
  `.claude/agents/agente-aeroportos.md` (linha "S1–S11"). **Nenhum
  agente vertical real usa essa numeração em seu próprio frontmatter.**

**Decisão de reconciliação (esta consolidação)**: adota-se a
**Convenção A**. Isso deixou de ser apenas uma escolha entre documentos
divergentes — `docs/SEGMENTOS-S12-S13-DECISION.md` (investigação G014,
Sonnet 12) consultou a **fonte de verdade real** (`execute_sql` contra
`manta_agent_capabilities` no projeto Supabase de produção,
`ogxxgvgtulrbbppshjie`) e confirmou que a tabela usa `agent_id` de
`03-S1` a `03-S13` na numeração **legada** (Portos=S6…Barragens=S10),
com `03-S11`, `03-S12` e `03-S13` já registrados com `ativo=true` desde
2026-07-12. A Convenção B (que este CLAUDE.md descartou) não tem
nenhum lastro em dado de produção — é uma teorização de documentação
escrita no mesmo dia, sem consulta ao banco. Os 3 documentos que usam a
Convenção B ficam **sinalizados como desatualizados** — ação de
correção pendente (ver Gaps abertos).

> ✅ **S11 identificado — não é mais "em aberto"**: a mesma investigação
> (`docs/SEGMENTOS-S12-S13-DECISION.md`, §2) encontrou `03-S11 =
> especialista-mineracao` (Mineração — cava/subterrânea/aluvionar;
> NRM/NR-22, SME/CIM/JORC/NI 43-101; TSF encaminha para S10/barragens),
> `ativo=true` em produção, no mesmo lote de registro que S12/S13.
> **Nenhum agente `.md`, RAG, rota SharePoint ou routing keyword existe
> para S11 ainda** — está na mesma situação em que S12/S13 estavam
> antes desta rodada: capacidade registrada, formalização pendente.
> Recomenda-se abrir um gap companheiro (sugestão do próprio documento
> de origem: **G015**) para tratar S11 com o mesmo processo usado para
> S12/S13 — não incluído nos entregáveis desta consolidação.

| Código | Segmento | Agente | Status |
|---|---|---|---|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| S6 | Portos | agente-portos | ✅ Operacional (v1.1.0, 2026-07-31) |
| S7 | Aeroportos | agente-aeroportos | ✅ Operacional |
| S8 | Saneamento | agente-saneamento | ✅ Operacional — PRIORIDADE AySA |
| S9 | Energia | agente-energia | ✅ Operacional — ANEEL/State Grid |
| S10 | Barragens | agente-barragens | ✅ Operacional |
| S11 | Mineração (cava/subterrânea/aluvionar; TSF encaminha para S10) | *(sem agente `.md` ainda)* | 🔵 **Identificado em produção** (`manta_agent_capabilities`, `ativo=true` desde 2026-07-12), **não formalizado** — sem agente, RAG, rota SP ou routing keyword. Sugerido G015 para tratamento (fora do escopo desta consolidação). |
| S12 | Óleo & Gás (downstream + midstream; **não cobre** E&P/reservatório) | agente-oleo-gas | 🟠 **Proposto** — `.claude/agents/agente-oleo-gas.md` criado 2026-07-31 a partir de `manta_agent_capabilities` confirmado; sem RAG, sem rota SharePoint, sem keyword de routing; migração candidata em `supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql`; **pendente gate humano MN** antes de virar operacional |
| S13 | Edificações (residencial, comercial, galpão, hospitalar, institucional, data center — distinto de Manta 04/Imobiliário, que é horizontal de negócio) | agente-edificacoes | 🟠 **Proposto** — `.claude/agents/agente-edificacoes.md` criado 2026-07-31 a partir de `manta_agent_capabilities` confirmado; sem RAG, sem rota SharePoint, sem keyword de routing; migração candidata em `supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql`; **pendente gate humano MN** antes de virar operacional |

Decisão completa (evidência, escopo, plano de formalização) em
`docs/SEGMENTOS-S12-S13-DECISION.md`.

---

## Eixo A — Atividades

Documentado por completo em `docs/ATIVIDADES-A1-A10.md` (v1.0,
2026-07-31) — descrição, entradas/saídas, critérios de aceitação,
metodologia e handoffs por atividade. Resumo:

| Código | Atividade | Agente(s) responsável(is) | Status do mapeamento |
|--------|-----------|-----------------------------|-----------------------|
| A1 | Proposta | Manta 13 (bd) + Manta 14 (apresentações) | ✅ Mapeado |
| A2 | Quantidades | Vertical do segmento (Manta 03-Sx) + skills de takeoff (`cad-quantifier`, `evtea-quantifier`) | ✅ Mapeado (sem agente horizontal dedicado — por natureza pertence ao vertical) |
| A3 | Orçamento | Manta 05 (orçamento) | ✅ Mapeado |
| A4 | Modelagem financeira | Manta 06 (modelagem) | ✅ Mapeado |
| A5 | Cronograma | Manta 07 (cronograma) | ✅ Mapeado |
| A6 | Contratual | Manta 02 (contratual) | ✅ Mapeado |
| A7 | Claims | Manta 01 (claims) | ✅ Mapeado |
| A8 | Advisory | Manta 15 (advisory) | ✅ Mapeado |
| A9 | Regulatório | *(sem agente horizontal dedicado)* | 🔴 **Rubrica pendente (TODO)** — hoje distribuído pelos verticais (ANEEL em S9, ANAC em S7 etc.) + suporte pontual de Manta 02/Manta 15. Decisão MN pendente: criar Manta-code dedicado ou manter distribuído. |
| A10 | Risco | Manta 15 (advisory) coordena consolidação; conteúdo vem de A1-A9 e S1-S13 | ⚠️ Processo transversal sem Manta-code próprio — **não interpretar como confirmação de um "Manta 17"** até registro formal aqui |

---

## Eixo F — Funcionais

Documentado por completo em `docs/FUNCIONAIS-F1-F8.md` (v1.0.0,
2026-07-31) — descrição, componentes, integrações, API/interface e
status por funcional. Resumo:

| Código | Funcional | Skill/sistema correspondente hoje |
|--------|-----------|-------------------------------------|
| F1 | IA (routing, model tiering) | Maestro (Manta 00) + lógica de routing desta seção |
| F2 | SharePoint (indexação, sync) | MCP `SharePoint_Manta` — leitura completa; escrita/upload disponível via tools do MCP, mas sync automático `.claude/agents/` ↔ SP ainda manual |
| F3 | Portal (web, SSO, permissões) | `portal-gestao-manta`, `portal-megaprojeto-builder`, `portal-metro-l4` |
| F4 | Extração (PDF/DWG parser) | `autodesk-toolkit`, `cqp-cad-bridge`, `evtea-extractor`, `pdf` |
| F5 | Notificação (email, Slack, webhook) | Routines (`send_later`, `create_trigger`), subscribe PR activity, `slack-gif-creator` (parcial) |
| F6 | Trace (audit log, approval gates) | `consist-guard` (rastreabilidade), histórico SharePoint, session logs, gate humano MN nos checklists |
| F7 | Guardrails (validação, aluci-guard, consist-guard) | `aluci-guard`, `consist-guard`, `context-guardian` |
| F8 | Padronização (templates, estilos, nomenclatura) | `padrao-manta`, `cl-design`, `brand-guidelines`, `docx`, `pptx`, `xlsx` |

---

## Eixo D — Disciplinas

Documentado por completo em `docs/DISCIPLINAS-D01-D20.md` (v1.0,
2026-07-31) — inclui matriz de aplicabilidade por segmento, normas-
chave e ferramentas por disciplina.

> ⚠️ **Nota de inconsistência conhecida**: `docs/DISCIPLINAS-D01-D20.md`
> usa a numeração de segmento da **Convenção B** (S6=Edificações …
> S11=Barragens — ver aviso no topo da seção "Eixo S" acima), que este
> CLAUDE.md **não adota**. A matriz de aplicabilidade por disciplina
> continua tecnicamente válida (as disciplinas em si não mudam), mas os
> códigos `Sx` nela **devem ser lidos mentalmente na Convenção A**
> (S6=Portos … S10=Barragens) até que o arquivo seja corrigido. Ação
> pendente — ver Gaps abertos.

**D01–D10 — Disciplinas clássicas**: Hidráulica, Estrutural,
Geotecnia, Pavimentação, Elétrica, Ambiental, Econômica/Financeiro,
Planejamento, Jurídico, Comercial.

**D11–D20 — Disciplinas secundárias**: MEP, HVAC, Acústica,
Acessibilidade, BIM, Paisagismo, TI, Comunicação, RH, Qualidade.

---

## Eixo temporal — Ciclo de vida (8 fases)

Mantido sem alteração — aplica-se a qualquer composição dos 4 eixos
acima, via Q2 do intake. Não é tratado como eixo ortogonal de
composição (qualquer combinação S.A.D pode, em princípio, ocorrer em
qualquer fase):

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

Exemplos de composição real (reproduzidos de
`ARQUITETURA-AGENTES-IA.md` v3.0.0, §2.6, já na Convenção A de
numeração):

```
S8.A3.D07  = Saneamento + Orçamento + Econômica
            → Manta 05 (agente-orcamento) com contexto de saneamento
              (RAG san:*, handoff de agente-saneamento)

S6.A2.D01  = Portos + Quantidades + Hidráulica
            → cubagem de dragagem do canal de acesso e bacia de evolução

S9.A6.D05  = Energia + Contratual + Elétrica
            → Manta 02 (contratual) com contexto de energia
              (RAG ene:*, handoff de agente-energia)

S10.A10.D02 = Barragens + Risco + Estrutural
            → matriz de risco de ruptura (PAE/PSB) com verificação
              estrutural CFRD/CCR
```

Regra prática: **S** decide o roteamento primário (agente vertical que
assume a sessão); **A** decide o handoff horizontal disparado; **D**
decide quais normas/RAG/skills de disciplina são carregadas; **F** pode
ser acionado a qualquer momento por qualquer agente, em qualquer
combinação S.A.D, sem alterar o dono da sessão. Cada composição pode
ser delegada a 1+ agentes em paralelo (teto de 8 sub-agentes
simultâneos).

---

## Mapa completo de agentes — 21 operacionais + 2 propostos

Contagem operacional confirmada: **12 horizontais + 9 verticais
operacionais** = 21 agentes (S5 Túneis é parcial, não conta como
agente adicional). Manta 20 (ESG) é agora **operacional v1.0** (P3-04 Design Agent).
S12 (Óleo & Gás) e S13 (Edificações) são **propostos**, não somam ao 
total operacional até gate MN.

### Horizontais (transversais a todos os segmentos) — 11 agentes

| Código | Agente | Arquivo | Aliases | Tier default | Status |
|--------|--------|---------|---------|--------------|--------|
| Manta 00 | maestro (router) | `maestro.v5.0.md` (spec de arquitetura — ver nota) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | `agente-claims.md` | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | `agente-contratual.md` | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | `agente-imobiliario.md` | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | `agente-orcamento.md` | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | `agente-modelagem.md` | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | `agente-cronograma.md` | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | `agente-bd.md` | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | `agente-apresentacoes.md` | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | `agente-advisory.md` | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | `agente-arquiteto-ia.md` | manta-15-arq | Opus | ✅ Operacional |
| Manta 20 | esg | `agente-esg.md` (spec de design, excluída do registro de teste — ver nota) | manta-20-esg, agente-esg | Sonnet | 🆕 v1.0 (P3-04 Design Agent) |

> **Nota sobre `maestro.v5.0.md` e `agente-esg.md`**: ambos vivem em
> `.claude/agents/` mas estão em `EXCLUDED_FROM_REGISTRY`
> (`tests/lib/agent_loader.py`) — o primeiro é a spec de arquitetura do
> router Manta 00 em formato de documento, não um subagente Claude
> Code; o segundo é a spec "Design Phase" do P3-04 (seções numeradas,
> ainda não convertida para o formato operacional de frontmatter +
> "Contexto de domínio" + "Handoff" usado pelos demais agentes). Os
> outros 4 agentes de Fase 3 (`agente-analytics-p3-07.md`,
> `agente-procurement-p3-08.md`, `manta-21-stakeholder.md`,
> `manta-25-kg.md`) estão na mesma situação — specs de design, não
> agentes operacionais — por isso não aparecem nas tabelas acima.

### Verticais por segmento (C3) — 9 operacionais + 1 parcial + 2 propostos

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial |
| S6 | Portos | agente-portos | ✅ Operacional |
| S7 | Aeroportos | agente-aeroportos | ✅ Operacional |
| S8 | Saneamento | agente-saneamento | ✅ Operacional — PRIORIDADE AySA |
| S9 | Energia | agente-energia | ✅ Operacional — ANEEL/State Grid |
| S10 | Barragens | agente-barragens | ✅ Operacional |
| S12 | Óleo & Gás | agente-oleo-gas | 🟠 Proposto — pendente gate MN |
| S13 | Edificações | agente-edificacoes | 🟠 Proposto — pendente gate MN |

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento para Q1 do intake. O dispatch é por **slug de
agente** (não por número de segmento) — por isso a numeração S6-S10 é
apenas rótulo informativo, sem efeito sobre esta lógica:

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

IF menção a biodiversidade|ambiental|ESG|carbono|offset|Mata Atlântica
   |Cerrado|Amazônia|mangue|APP|RL|IBAMA|social license|stakeholder
   |impacto comunitário|consulta prévia|FUNAI|carbon accounting|Net Zero
   |Escopo 1|Escopo 2|Escopo 3|GHG|compliance ESG|TCFD|SASB|GRI
   → manta-20-esg (co-agente com vertical do segmento em escopo)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4

IF menção a Motiva|CCR Rodovias|SP-258|SP-330|Contorno Apucarana
   → aplicar docs/PADRAO-OUTPUT-MOTIVA.md (padrão de output do cliente —
     co-agente com o vertical/horizontal em escopo, não substitui o
     dispatch primário por segmento). Ver seção "Padrões de output por
     cliente" e a referência em cada agente que gera o entregável
     (agente-orcamento, agente-cronograma, agente-apresentacoes,
     agente-contratual).
```

**S12/S13 ainda NÃO têm keyword de routing** (confirmado em
`agente-oleo-gas.md` e `agente-edificacoes.md`, seção "Ferramentas e
integrações" de cada um) — o Maestro não consegue despachar para esses
dois agentes hoje, mesmo que o usuário use as palavras-chave descritas
em seus frontmatters. Isso é esperado enquanto o status for "proposto".

**Casos ambíguos** (documentados em `tests/routing/prompts.md`, mantidos
sem alteração):
- UHE (barragem + LT + SE) → dispatch primário `agente-barragens` +
  handoff `agente-energia`.
- ETE + subestação → dispatch primário `agente-saneamento` + handoff
  `agente-energia`.
- Porto + pista de carga → dispatch primário `agente-portos` + handoff
  `agente-aeroportos`.
- Adutora atravessa barragem de rejeitos → `agente-saneamento` com
  consulta técnica ao `agente-barragens`.

---

## RAG — Coleções em Supabase

**9 coleções confirmadas por auditoria real** (não apenas por arquivo
de migração candidata) — ver `docs/SUPABASE-PROJECT-AUDIT.md`, que
executou `list_tables` no projeto `ogxxgvgtulrbbppshjie`
(`manta-maestro`, `sa-east-1`, `ACTIVE_HEALTHY`) e confirmou
`rag_collections` com 9 linhas, `sp_agent_routing` com 9 linhas,
`maestro_routing_keywords` com 50 linhas, `manta_rag_chunks` com 204
linhas e `manta_rag_documents` com 111 linhas.

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
| óleo-gás | og: *(sugerido)* | ANP, API 650/653, ASME B31.3/4/8, NFPA 30, HAZOP | 🔲 Não criada — depende do gate MN de S12 |
| edificações | edi: *(sugerido)* | NBR 15575, LEED, BIM | 🔲 Não criada — depende do gate MN de S13 |

Sub-prefixos de contexto (mantidos do v4.2):
- `san:br:` / `san:ar:` — saneamento por país (Brasil × Argentina AySA).
- `ene:t:` / `ene:d:` / `ene:g:` — energia por transmissão/distribuição/geração.
- `bar:c:` / `bar:t:` / `bar:e:` / `bar:r:` — barragens por tipologia.

> ⚠️ **Divergência de embedder não resolvida** — ver
> `docs/EMBEDDER-DECISION.md` (Sonnet 11) vs. achado em
> `docs/SUPABASE-PROJECT-AUDIT.md` §2.1 (Sonnet 13): o primeiro afirma
> que produção roda `bge-small-en-v1.5` (384-d) com 0% dos 204 chunks
> migrados para `bge-m3`; o segundo, lendo o comentário real da coluna
> em `manta_rag_chunks` via `list_tables`, encontrou o texto "Chunks
> com embeddings 1024d (bge-m3, canonical Maestro 2026-07-03)". Os dois
> documentos **não foram reconciliados entre si** nesta consolidação —
> ambos vêm de sessões diferentes no mesmo dia. Antes de agir sobre
> qualquer um dos dois, confirmar a dimensão real da coluna de vetor
> (`\d manta_rag_chunks` ou equivalente), não apenas o texto do
> comentário nem a descrição da skill. Ver Gaps abertos.

Migração candidata das 5 coleções v4.2:
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`.

---

## SHAREPOINT — Routing rules (sp_agent_routing)

Confirmado por auditoria real: tabela `sp_agent_routing` tem 9 linhas
em produção (ver seção RAG acima).

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |
| agente-oleo-gas | 03_Projetos/OleoGas/* *(a criar)* | *.pdf, *.dwg, *.xlsx — 🔲 planejado, pendente gate S12 |
| agente-edificacoes | 03_Projetos/Edificacoes/* *(a criar)* | *.pdf, *.dwg, *.xlsx — 🔲 planejado, pendente gate S13 |

---

## PADRÕES DE OUTPUT POR CLIENTE

Referências canônicas de formato de entregável (EAP em Excel/PPT,
relatório, codificação de documentos, identidade visual) por cliente,
levantadas do SharePoint. Todo agente vertical deve seguir o padrão do
cliente ao gerar output para ele.

| Cliente | Doc de referência | Status |
|---------|--------------------|--------|
| Motiva (ex-CCR Rodovias) | [`docs/PADRAO-OUTPUT-MOTIVA.md`](docs/PADRAO-OUTPUT-MOTIVA.md) · templates: [`EAP-PADRAO-MOTIVA.xlsx`](docs/templates/EAP-PADRAO-MOTIVA.xlsx), [`PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx`](docs/templates/PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx) | ✅ EAP Excel/PPT/relatório/codificação implementados (aprovado MN) · ✅ routing por cliente + referenciado em agente-orcamento/cronograma/apresentacoes/contratual · ⚠️ cores de marca não localizadas — templates usam paleta neutra Manta até confirmação · ⚠️ upload para o SharePoint da equipe ainda pendente (ação manual, MCP atual é read-only) |

---

## MODEL TIERING

| Tier | Modelo | Uso típico |
|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico |

O Maestro escala dinamicamente de tier dentro de uma sessão (Haiku →
Sonnet ao entrar no vertical → Opus se detectar complexidade).

---

## GAPS ABERTOS / PENDÊNCIAS

- **Numeração de segmento divergente (novo, encontrado nesta
  consolidação)**: `docs/DISCIPLINAS-D01-D20.md`,
  `docs/ATIVIDADES-A1-A10.md` e uma linha em
  `.claude/agents/agente-aeroportos.md` usam a Convenção B (S6=
  Edificações…S11=Barragens), incompatível com a Convenção A adotada
  neste CLAUDE.md e com os frontmatters reais dos agentes. Ação:
  corrigir esses 3 arquivos para a Convenção A, ou formalizar a
  Convenção B em todo o repositório — não ambas ao mesmo tempo.
- **S11 (Mineração) identificado mas não formalizado (G015)**: confirmado em
  produção (`manta_agent_capabilities`, `03-S11`, `ativo=true`), sem
  agente `.md`, RAG, rota SP ou routing keyword — mesma situação em que
  S12/S13 estavam antes desta rodada. **Documentação em `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md`** com roadmap de
  formalização. Ação: aprovação MN + checklist idêntico a S12/S13.
- **Embedder (G010)**: `docs/EMBEDDER-DECISION.md` recomenda migrar
  para `bge-m3`, partindo da premissa de que produção roda
  `bge-small-en-v1.5` com 0% migrado. `docs/SUPABASE-PROJECT-AUDIT.md`
  encontrou evidência (comentário de coluna via `list_tables`) sugerindo
  que o schema já é `bge-m3`/1024-d desde 2026-07-03. **Os dois
  documentos se contradizem e nenhum foi reconciliado com o outro**.
  Ação: verificar a dimensão real da coluna de embeddings antes de
  qualquer decisão ou migração.
- **Supabase — projeto `xgluoaaymbdzbbudnwrh` (G012)**: auditoria real
  (`docs/SUPABASE-PROJECT-AUDIT.md`) concluiu, com evidência de API,
  que é provavelmente referência morta (projeto não pertence à
  organização Supabase ativa da conta corporativa). **Confirmação
  humana (dashboard) ainda pendente** antes de remover a referência —
  ver action items AI-1 a AI-10 nesse documento.
- **RLS desabilitado em 3 tabelas públicas** (`rag_collections`,
  `sp_agent_routing`, `maestro_routing_keywords`) — achado de segurança
  correlato da auditoria G012, com SQL de remediação já redigido mas
  **não aplicado** (requer policies de leitura corretas antes de
  habilitar RLS, para não quebrar o acesso do próprio Maestro em
  runtime). Ver AI-6 em `docs/SUPABASE-PROJECT-AUDIT.md`.
- **3 projetos Supabase `INACTIVE`** (`manta-tocantins`,
  `manta-rodovias`, `manta-portal-piloto`) — decisão de consolidar,
  arquivar ou manter pendente MN (ver AI-7/AI-8 no mesmo documento).
- **A9 (Regulatório) e A10 (Risco)**: sem Manta-code horizontal
  dedicado — ver Eixo A.
- **S12/S13 sem RAG, sem rota SharePoint, sem keyword de routing** —
  agentes existem como arquivo, mas não são despacháveis pelo Maestro
  hoje.
- **Templates Motiva sem upload real para o SharePoint da equipe
  (novo)**: `docs/templates/EAP-PADRAO-MOTIVA.xlsx` e
  `PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx` existem versionados
  neste repositório e já estão referenciados no routing e nos agentes
  de output (v5.4), mas ainda não foram copiados para
  `sites/Engenharia/.../04_IA/Manta-Maestro/` onde a equipe de fato
  trabalha — o MCP SharePoint disponível hoje é somente leitura (mesma
  limitação já registrada em `docs/DEPLOY-v4.2.md`). Ação: alguém com
  acesso de escrita ao SharePoint sobe os 2 arquivos manualmente.
- **Cor institucional da Motiva não confirmada** — ver seção 5 de
  `docs/PADRAO-OUTPUT-MOTIVA.md`; templates usam paleta neutra Manta
  até confirmação do cliente.

---

## QUESTIONÁRIO DE DECISÃO PARA MN

1. **Numeração de segmento**: ratificar a Convenção A (mantida nesta
   versão) e corrigir os 3 arquivos com Convenção B, ou inverter a
   decisão e renumerar os agentes operacionais? Reverter os 5 agentes
   operacionais tem custo maior (frontmatters + RAG + SP já publicados
   sob S6-S10).
2. **S11 (Mineração)**: aprovar formalização (mesmo checklist de
   S12/S13 — agente `.md`, RAG, rota SP, routing keywords) e abrir o
   gap G015 correspondente, ou manter apenas como capacidade registrada
   sem agente despachável?
3. **S12 (Óleo & Gás) e S13 (Edificações)**: aprovar para operacional
   (criar RAG + rota SP + routing keywords) ou manter como proposta sem
   prazo?
4. **Embedder**: antes de decidir bge-small vs. bge-m3, confirmar a
   dimensão real da coluna de vetor em produção — a decisão atual
   (`docs/EMBEDDER-DECISION.md`) parte de uma premissa não verificada
   contra o achado da auditoria Supabase.
5. **Projeto Supabase `xgluoaa...`**: autorizar confirmação manual via
   dashboard (AI-1) antes de remover a referência do SKILL.md?
6. **Timeline de merge**: em qual sprint este v5.0 vai para `main`?

---

## DEPLOY CHECKLIST v5.0

Checklist completo e detalhado em `docs/DEPLOY-CHECKLIST-v5.0.md`
(herda o checklist v4.2, ainda com 8/10 itens pendentes fora do git, e
adiciona a sequência de consolidação/validação da v5.0). Resumo:

- [x] Consolidar modelo de 4 eixos (S×A×F×D) no CLAUDE.md master
- [x] Reconciliar divergência de numeração de segmento (Convenção A)
- [x] Corrigir tabela de coleções RAG com dados de auditoria real (9 confirmadas)
- [x] Registrar S12 (Óleo & Gás) e S13 (Edificações) como propostos
- [x] Identificar S11 (Mineração) a partir de `manta_agent_capabilities`
- [x] Linkar Eixo A/F/D aos documentos dedicados já produzidos
- [x] Corrigir numeração de segmento em `docs/DISCIPLINAS-D01-D20.md`, `docs/ATIVIDADES-A1-A10.md` e `agente-aeroportos.v5.0.md` (Convenção B → A)
- [x] Abrir gap G015 — documentação de formalização S11 (Mineração) em `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md`
- [ ] Reconciliar `docs/EMBEDDER-DECISION.md` com achado de
      `docs/SUPABASE-PROJECT-AUDIT.md` antes de decidir embedder
- [ ] Confirmar manualmente o destino do projeto `xgluoaa...` (AI-1)
- [ ] Aplicar RLS nas 3 tabelas expostas (AI-6)
- [ ] Criar RAG + rota SP + routing keywords para S12/S13 (se aprovado)
- [ ] Rodar aluci-guard sobre este documento antes de merge
- [ ] Rodar consist-guard sobre este documento antes de merge
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                              # este arquivo (master registry, v5.2)
├── README.md
├── .claude/
│   └── agents/
│       ├── agente-portos.md               # S6 (v1.1.0, revisado 2026-07-31)
│       ├── agente-aeroportos.md           # S7
│       ├── agente-saneamento.md           # S8 — prioridade AySA
│       ├── agente-energia.md              # S9 — ANEEL/State Grid
│       ├── agente-barragens.md            # S10
│       ├── agente-esg.md                  # Manta 20 — P3-04 Design Agent ESG (v1.0, 2026-08-02)
│       ├── agente-oleo-gas.md             # S12 — 🟠 proposto, pendente gate MN
│       └── agente-edificacoes.md          # S13 — 🟠 proposto, pendente gate MN
├── docs/
│   ├── PADRAO-OUTPUT-MOTIVA.md            # v5.2 — padrão de output cliente Motiva
│   ├── templates/
│   │   ├── EAP-PADRAO-MOTIVA.xlsx               # 🆕 v5.3 — template EAP (capa + hierarquia 4 níveis)
│   │   └── PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx  # 🆕 v5.3 — template capa/sumário/conteúdo
│   ├── ATIVIDADES-A1-A10.md               # Eixo A completo (rascunho p/ revisão MN)
│   ├── FUNCIONAIS-F1-F8.md                # Eixo F completo
│   ├── DISCIPLINAS-D01-D20.md             # Eixo D completo (⚠️ numeração de S divergente — ver Gaps)
│   ├── EMBEDDER-DECISION.md               # G010 — recomendação, pendente aprovação MN (⚠️ contradiz achado do audit — ver Gaps)
│   ├── SUPABASE-PROJECT-AUDIT.md          # G012 — auditoria real via MCP Supabase
│   ├── SEGMENTOS-S12-S13-DECISION.md      # G014 — investigação real via MCP Supabase; confirma S11/S12/S13
│   ├── SEGMENTO-S11-MINERACAO-GAP-G015.md # G015 — S11 (Mineração) identificado; roadmap formalização (novo, 2026-07-31)
│   ├── DEPLOY-CHECKLIST-v5.0.md           # checklist completo v4.2 + v5.0
│   ├── DEPLOY-v4.2.md                     # runbook manual (Supabase + SharePoint)
│   ├── COWORK-INTEGRATION.md              # runbook de integração Maestro ↔ Cowork
│   ├── PORTAL-BACKEND-PLANO.md            # MNT-2026-ARQ-0001 — backend do Portal IA (proposta)
│   └── portal-backend/
│       ├── schema-draft.sql               # anexo A — schema candidato (portal_core/docs/ai/ops)
│       └── api-contract.md                # anexo B — contrato /v1
├── sharepoint/
│   ├── README.md
│   └── 00-arquitetura/
│       └── ARQUITETURA-AGENTES-IA.md      # v3.0.0 — documento de arquitetura de referência (4 eixos)
├── supabase/
│   └── migrations/
│       ├── 2026_07_05_v4_2_agents_s6_s10.sql      # migração candidata v4.2
│       └── 2026_07_31_v4_3_agents_s12_s13.sql     # migração candidata v4.3 (S12/S13 RAG+routing)
└── tests/
    └── routing/
        └── prompts.md                     # smoke tests de routing por segmento
```

---

## Histórico de versões

- **v5.4** (2026-08-31) — **Padrão Motiva ligado ao routing e aos
  agentes de output** (aprovado por MN). Duas mudanças de
  comportamento, não só documentação:
  - Nova regra na seção ROUTING: menção a `Motiva`/`CCR Rodovias`/
    `SP-258`/`SP-330`/`Contorno Apucarana` aplica
    `docs/PADRAO-OUTPUT-MOTIVA.md` como co-agente de padrão de output,
    no mesmo estilo já usado para `manta-20-esg` — não substitui o
    dispatch primário por segmento.
  - Referência direta ao documento na seção "Ferramentas e
    integrações" dos 4 agentes horizontais que de fato produzem o
    entregável para a Motiva: `agente-orcamento.md` (EAP Excel),
    `agente-cronograma.md` (insumo do Planejamento Gerencial),
    `agente-apresentacoes.md` (PPT), `agente-contratual.md` (norma de
    codificação de documentos do cliente).
  - Ainda pendente (fora do alcance desta sessão): upload dos 2
    templates para o SharePoint real da equipe (`sites/Engenharia/
    .../04_IA/Manta-Maestro/`) — hoje só existem versionados neste
    repositório; e confirmação da cor institucional da Motiva (segue
    lacuna, ver seção 5 de `PADRAO-OUTPUT-MOTIVA.md`).
  Ticket `MNT-2026-MOTIVA-258-PATTERN`.
- **v5.3** (2026-08-30) — **Templates Motiva implementados** (aprovado
  por MN). Dois arquivos novos em `docs/templates/`:
  - `EAP-PADRAO-MOTIVA.xlsx` — aba Capa (bloco de cabeçalho + legenda
    de preenchimento automático/manual) e aba EAP (cabeçalho de 16
    colunas, hierarquia de 4 níveis com 2 itens-modelo, fórmulas de
    custo total/preço unitário/preço total/% — validadas com
    recálculo LibreOffice, 0 erros).
  - `PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx` — capa (versalete +
    campos Cliente/Elaboração/Status), slide de sumário com as 5
    seções documentadas e slide-modelo de conteúdo com o rodapé
    padrão `[Rodovia] · [Segmento] · MOTIVA · [Seção] · nº/total`
    (validado com `office/validate.py` e QA visual).
  - Paleta: grayscale neutro (padrão Manta) em ambos os arquivos —
    cor institucional da Motiva segue não confirmada (ver v5.2/seção
    5 de `PADRAO-OUTPUT-MOTIVA.md`); nota registrada no gerador e nas
    notas do orador da capa do PPTX para troca fácil quando a marca
    for confirmada. Ticket `MNT-2026-MOTIVA-258-PATTERN`.
- **v5.2** (2026-08-30) — padrão de output do cliente Motiva
  documentado (`docs/PADRAO-OUTPUT-MOTIVA.md`): formato de EAP em
  Excel (template v8, hierarquia de 4 níveis, código interno) e em
  PowerPoint, estrutura do relatório Caderno de Premissas FEL-1, norma
  de codificação de documentos CCR/Motiva. Cores de marca: lacuna
  confirmada em duas varreduras do SharePoint (geral e pastas
  "Material Recebido" de 10 projetos) — nenhum brandbook localizado.
  Ticket `MNT-2026-MOTIVA-258-PATTERN`.
- **v5.1** (2026-08-02) — **Design Agents — ESG/Impact (P3-04)**. Novo 
  agente horizontal Manta 20 (manta-20-esg): ESG assessment, 4 dimensões 
  (ambiental, social, governança, integração), integração co-agente com 
  S6–S10, RAG collections, compliance mapping, 3 casos uso, Carbon Roadmap. 
  Tier: Sonnet. Status: v1.0 operacional. Agentes totais: 21 (12 h + 9 v).
  Ticket `MNT-2026-P3-04-ESG-AGENT`.
- **v5.0.1** (2026-07-31) — **UNIFICADA**: merge de v5.0.0 operacional
  (aprovado 2026-07-22, 20 agentes, Maestro-OS v6.0) + v5.0 consolidação
  (2026-07-31, gaps formalizados, 4 eixos A/F/D, 15 Sonnets investigação).
  Este documento reconcilia ambos os work streams: infraestrutura em
  produção + documentação de decisões e gaps. Status: **Operacional com
  transparência de decisões** — ready para produção com rastreabilidade
  completa de divergências encontradas em paralelo no mesmo dia.
- **v5.0** (2026-07-31) — consolidação do modelo de 4 eixos (S×A×F×D)
  com o estado operacional v4.2 e com o trabalho paralelo produzido no
  mesmo branch nesta data (auditoria real Supabase, decisão de
  embedder, novos agentes S12/S13). Principais decisões desta
  consolidação:
  - Mantida a numeração legada de segmentos (S6=Portos…S10=Barragens),
    reconciliando uma divergência encontrada com 3 documentos que
    usavam uma renumeração diferente (sinalizados como pendentes de
    correção, não corrigidos automaticamente aqui) — decisão
    corroborada por consulta real a `manta_agent_capabilities` em
    produção (ver `docs/SEGMENTOS-S12-S13-DECISION.md`).
  - Registrados S12 (Óleo & Gás) e S13 (Edificações) como **propostos**
    (agentes criados, sem RAG/rota SP/routing — pendente gate MN),
    confirmados como capacidades reais (`ativo=true`) em
    `manta_agent_capabilities`, não erro de cadastro.
  - S11 (Mineração) identificado na mesma tabela de produção,
    `ativo=true` desde 2026-07-12, mas ainda sem agente/RAG/rota/
    routing — documentado como pendente de formalização (gap G015
    sugerido), não mais como "não atribuído".
  - Coleções RAG atualizadas com números de auditoria real (9
    coleções, 204 chunks, 111 documentos, confirmados via `list_tables`
    em produção) em vez de contagem estimada.
  - Divergência entre `EMBEDDER-DECISION.md` e o achado da auditoria
    Supabase sobre a dimensão real do embedder documentada como não
    resolvida, em vez de escolhida unilateralmente.
  - Eixos A, F e D linkados aos documentos dedicados já produzidos
    (`docs/ATIVIDADES-A1-A10.md`, `docs/FUNCIONAIS-F1-F8.md`,
    `docs/DISCIPLINAS-D01-D20.md`) em vez de duplicar o conteúdo aqui.
  Ticket `MNT-2026-CONSOLIDACAO-ARCH-V5`.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
