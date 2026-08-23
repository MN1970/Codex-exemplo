# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.3** (2026-08-23) — review de arquitetura manta-arquiteto-ia
(Etapas 1-4, gate humano concluído): backend real de dispatch via Claude
Agent SDK (`backend/maestro_dispatch.py`), aluci-guard como hook
PreToolUse determinístico, e correção de 3 bugs reais pré-existentes na
suíte de testes (`tests/lib/agent_loader.py`, `pytest.ini`,
`.claude/agents/`) encontrados durante a implementação. Ver seção
"REVIEW DE ARQUITETURA — v5.3" abaixo.

Anterior: v5.2 (2026-08-22) — catálogo de fontes de receita setorial
(mão de obra, equipamento, aço, cimento) para os 8 segmentos S1-S10. Ver
`pesquisa-fontes/FONTES_RECEITA_SETORIAL.md`.

v5.1 (2026-08-02) — **Design Agents (P3-04): ESG/Impact Design Agent**.
Expande o framework com novo agente horizontal **Manta 20 (manta-20-esg)** —
assessment ESG, 4 dimensões (Ambiental/Social/Governança/Integração),
integração com S6–S10, RAG + compliance mapping.

Consolida v5.0.1 operacional (2026-07-31):
- **v5.0.0 operacional** (aprovado 2026-07-22): 20 agentes em produção,
  infraestrutura Maestro-OS v6.0 completa (APScheduler, ML, observability)
- **v5.0 consolidação** (2026-07-31): 4 eixos (S×A×F×D) formalizados,
  gaps G010/G012/G014 resolvidos, 15 Sonnets investigação paralela.

Tickets: `MNT-2026-CONSOLIDACAO-ARCH-V5` (operacional) + `MNT-2026-P3-04-ESG-AGENT` (novo).

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
12. [Model tiering](#model-tiering)
13. [Gaps abertos / pendências](#gaps-abertos--pendências)
14. [Questionário de decisão para MN](#questionário-de-decisão-para-mn)
15. [Deploy checklist v5.0](#deploy-checklist-v50)
16. [Arquivos deste repositório](#arquivos-deste-repositório)
17. [Histórico de versões](#histórico-de-versões)

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

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims, agente-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual, agente-contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04, agente-imobiliario | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05, agente-orcamento | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06, agente-modelagem | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07, agente-cronograma | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev, agente-bd | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx, agente-apresentacoes | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory, agente-advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq, agente-arquiteto-ia | Opus | ✅ Operacional |
| Manta 20 | esg | manta-20-esg, agente-esg | Sonnet | 🆕 v1.0 (P3-04 Design Agent) |

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

## FONTES DE RECEITA SETORIAL — mão de obra, equipamento, aço, cimento

Catálogo de fontes (Brasil + exterior) para calcular consumo de mão de
obra/equipamento/aço/cimento a partir da RECEITA de projetos (complementa
o modelo baseado em CAPEX do "Livro Azul"): ver
[`pesquisa-fontes/FONTES_RECEITA_SETORIAL.md`](pesquisa-fontes/FONTES_RECEITA_SETORIAL.md).

Resumo — melhor fonte por segmento:

| Segmento | Melhor fonte Brasil | Melhor fonte exterior |
|---|---|---|
| Rodovias | ANTT (DFs + Plano de Contas + dados abertos) | Autostrade per l'Italia (ASPI) |
| Ferrovias | CVM/DFP (Rumo, MRS, VLI) | SEC EDGAR 10-K (Union Pacific, NS, CSX) |
| Portos | CVM (Santos Brasil, Wilson Sons) + ANTAQ Res. 49/2021 | *Port Economics, Management and Policy* (acadêmico) |
| Aeroportos | ANAC (DFs por concessão) | Fraport AG / ICAO |
| Saneamento | **SNIS** (FN005/FN010-014) | OFWAT (Reino Unido) |
| Metrôs | Metrô-SP/CMSP + MetrôRio (SETRAM-RJ) | **NTD/APTA** (EUA) |
| Energia | ANEEL CIEFSE/DCR + RI Taesa/CTEEP/Alupar | **FERC Form 1** (EUA) |
| Barragens | Vale/Samarco (custo de descaracterização) + ANM | ICMM/GISTM + literatura acadêmica |

Achado estrutural: nenhuma fonte de receita desagrega aço/cimento — isso
continua vindo do lado CAPEX (Matriz de Insumo-Produto do IBGE, já em uso).
Pendência: validar manualmente os números (WebFetch esteve bloqueado na
sessão de pesquisa) e rodar `aluci-guard` antes de uso oficial.

Agências reguladoras (Brasil): **ANTT** (rodovias/ferrovias), **ANEEL**
(energia), **ANAC** (aeroportos), **ANTAQ** (portos), **ANM** (barragens),
Ministério das Cidades/**SNIS** (saneamento) — lista completa com o que
cada uma publica em `pesquisa-fontes/FONTES_RECEITA_SETORIAL.md`.

MEF (Modelo Econômico-Financeiro) por segmento com os coeficientes já
aplicados em cascata (receita → mão de obra/material/serviços), 1 aba por
segmento: `pesquisa-fontes/MEF_Receita_Setorial.xlsx`.

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

## MODEL TIERING

| Tier | Modelo | Uso típico |
|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico |

O Maestro escala dinamicamente de tier dentro de uma sessão (Haiku →
Sonnet ao entrar no vertical → Opus se detectar complexidade).

---

## REVIEW DE ARQUITETURA — v5.3 (manta-arquiteto-ia, 2026-08-23)

Review de 4 etapas (Diagnóstico → Propostas → Implementação → Registro,
gate humano por proposta) aplicado ao próprio Manta Maestro. Ticket
implícito: fechar a lacuna "Maestro existe como especificação + sessões
manuais, não como serviço rodando" encontrada na Etapa 1.

**Etapa 2 (Propostas) → Etapa 3 (Implementação) — 4 propostas, todas
aprovadas por MN:**

1. **Backend real via Claude Agent SDK** — `backend/maestro_dispatch.py`
   (endpoint FastAPI `/maestro/dispatch` + `/maestro/agents`) e
   `backend/agent_registry.py` (parser de `.claude/agents/*.md`,
   promovido de `tests/lib/` para código de produção — único parser
   compartilhado entre backend e testes, evita divergência). Aplica
   tiering de `.claude/settings.json::model_defaults` por agente e usa
   o hook aluci-guard (item 2) como `PreToolUse`. **Não** duplica a
   infraestrutura de jobs agendados já existente
   (`scripts/apscheduler_setup.py`, `deploy/Dockerfile`) — aquela cobre
   rotação de secrets/reindex/purge; esta cobre o caminho
   prompt→routing→resposta que só existia como sessão manual.
   Limitação documentada no próprio módulo: `maestro.v5.0.md` (o router)
   não tem frontmatter YAML, então seu corpo é usado como system prompt
   bruto em vez de virar `AgentDefinition` como os verticais.
2. **aluci-guard como hook PreToolUse determinístico** —
   `.claude/hooks/pretooluse_aluci_guard.py`, registrado como step 4 em
   `.claude/settings.json::hooks.pre_tool_use.steps`. Bloqueia
   Write/Edit citando NBR/Lei/SICRO com formato implausível (dígitos
   fora de faixa, ano futuro). É uma checagem heurística de *formato*,
   não substitui a auditoria de conteúdo da skill `aluci-guard` nem de
   `scripts/ke_aluci_guard_audit.py`.
3. **Model tiering em código** — **retificada durante a implementação**:
   já existia, completa, em `.claude/settings.json::model_defaults`
   (`tier_horizontal`/`tier_vertical`, um model ID por agente). O
   diagnóstico original (Etapa 1) estava incompleto por não ter lido
   esse arquivo. O achado real e novo, registrado como gap em vez de
   corrigido por adivinhação, é outro: os model IDs pinados em
   `settings.json` (`claude-sonnet-5-20250701`, `claude-opus-5-20250701`)
   não correspondem aos nomes genéricos da tabela "Model Tiering" deste
   documento ("Claude Sonnet 4.6", "Claude Opus 4.7/4.8") — ver Gaps
   abertos.
4. **Normalizar sufixo `.v5.0.md`** — **proposta original retirada**:
   `docs/DEPLOYMENT-GUIDE.md` (Fase 3) e `VERSIONS.json` mostram que o
   sufixo é um mecanismo de versionamento/pin de produção intencional
   (checksum + `pinned_by: ["prod"]`), não uma inconsistência de nome —
   renomear os 6 arquivos pinados (`maestro`, `agente-saneamento`,
   `agente-energia`, `agente-portos`, `agente-aeroportos`,
   `agente-barragens`) quebraria esse mecanismo e uma cadeia de
   runbooks operacionais reais (`S6-GO-LIVE-CHECKLIST.md`,
   `S6-GO-LIVE-RUNBOOK.md`, `.github/DEPLOYMENT-APPROVALS.md`) que
   citam esses caminhos literalmente. **Fix real aplicado no lugar**:
   `Path.stem` só remove o `.md` final, então o slug computado por
   `tests/lib/agent_loader.py` (hoje `backend/agent_registry.py`) ficava
   `"agente-saneamento.v5.0"` em vez de `"agente-saneamento"`, quebrando
   `load_agent()` para os 6 arquivos pinados. Corrigido normalizando o
   slug (`_slug_from_stem`), sem tocar nos arquivos.

**Bugs pré-existentes encontrados e corrigidos durante a Etapa 3** (não
faziam parte de nenhuma das 4 propostas, mas bloqueavam a verificação
delas — corrigidos com o mesmo padrão de transparência deste
documento: achado real, não escondido):

- `tests/lib/agent_loader.py::load_all_agents()` derrubava a coleta
  inteira dos testes (`AgentParseError`) ao encontrar qualquer
  `.claude/agents/*.md` sem frontmatter YAML — e há 8 desses hoje
  (`agente-analytics-p3-07.md`, `agente-esg.md`,
  `agente-procurement-p3-08.md`, `example_background_agent_skill.md`,
  `maestro.v5.0.md`, `manta-21-stakeholder.md`, `manta-25-kg.md`,
  `sicro-similaridade-skill.md` — a maioria documentos de "Design
  Phase" estacionados em `.claude/agents/` antes de virarem agente
  real). Corrigido: ignora com aviso por padrão, `strict=True` restaura
  o comportamento antigo. **Antes desta correção, `tests/unit/` inteiro
  não rodava** — o que provavelmente também explica parte do "Agent
  Test Suite" vermelho no CI do `main` (além dos 2 YAML de workflow já
  diagnosticados em sessão anterior).
- `pytest.ini` não registrava os markers `ci`/`perf`/`integration`/
  `asyncio` (só `unit`/`smoke`/`rag`) — com `--strict-markers`, isso
  gerava `INTERNALERROR` (não uma falha de teste normal) assim que
  qualquer teste com nodeid contendo "cross_agent" era coletado (ex:
  `tests/test_cross_agent_flows.py`), derrubando a suíte inteira.
  Corrigido adicionando os 4 markers faltantes (o `conftest.py` já os
  registrava dinamicamente via `addinivalue_line`, mas isso não bastava
  sob `--strict-markers` nesta versão do pytest) + `pytest-asyncio` em
  `tests/requirements.txt` (estava só no `requirements.txt` raiz).
- `test_every_agent_file_is_registered_in_claude_md` (ficou mascarado
  pelo bug acima, nunca rodava) falhava de verdade: os 9 agentes
  horizontais legados (`agente-claims`, `agente-contratual`,
  `agente-imobiliario`, `agente-orcamento`, `agente-modelagem`,
  `agente-cronograma`, `agente-bd`, `agente-apresentacoes`,
  `agente-advisory`, `agente-arquiteto-ia`) são citados na tabela
  "Horizontais" deste CLAUDE.md só pelo nome curto ("claims",
  "contratual"...), nunca pelo slug de arquivo (`agente-claims.md`).
  Corrigido adicionando o slug como alias na coluna "Aliases" de cada
  linha (mesmo padrão já usado na linha do Manta 20/ESG).

**Cobertura de teste nova**: `tests/unit/test_agent_loader_versioning.py`
(regressão do bug de slug), `tests/unit/test_aluci_guard_hook.py`,
`tests/unit/test_maestro_dispatch.py` — todos sem rede/API key. Suíte
`tests/unit` completa: 190 passed (era impossível medir "completa"
antes desta Etapa 3, já que a coleta não terminava).

**Etapa 4 (Registro)**: esta seção. Ticket de referência:
`MNT-2026-ARQ-REVIEW-V5.3` (não existe ainda como ticket formal em
sistema externo — citado aqui só como identificador de rastreabilidade
interna ao repositório).

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
- **Model IDs divergentes entre CLAUDE.md e `.claude/settings.json`
  (novo, encontrado na Etapa 3 do review v5.3)**: a tabela "Model
  Tiering" deste documento usa nomes genéricos de linha de produto
  ("Claude Sonnet 4.6", "Claude Opus 4.7/4.8", "Claude Haiku 4.5"),
  enquanto `.claude/settings.json::model_defaults` pina IDs de modelo
  concretos (`claude-sonnet-5-20250701`, `claude-opus-5-20250701`,
  `claude-haiku-4-5-20251001`) — aparentemente uma geração adiante
  (Sonnet 5/Opus 5, não 4.6/4.7). Não sabemos qual dos dois documentos
  ficou desatualizado primeiro nem se a migração para a linha 5 já foi
  intencional e só não voltou para este CLAUDE.md — não resolvido aqui
  por adivinhação. Ação: confirmar com MN qual é a linha de modelo
  correta em produção hoje e atualizar o lado desatualizado.
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
├── CLAUDE.md                              # este arquivo (master registry, v5.3)
├── README.md
├── backend/                                # 🆕 v5.3 — Manta 00 como serviço (Proposta 1)
│   ├── agent_registry.py                  # parser único de .claude/agents/*.md (produção + testes)
│   └── maestro_dispatch.py                # FastAPI: /maestro/dispatch, /maestro/agents
├── pesquisa-fontes/
│   └── FONTES_RECEITA_SETORIAL.md         # fontes de receita setorial (v5.2)
├── .claude/
│   ├── hooks/
│   │   └── pretooluse_aluci_guard.py      # 🆕 v5.3 — aluci-guard determinístico (Proposta 2)
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
│   ├── ATIVIDADES-A1-A10.md               # Eixo A completo (rascunho p/ revisão MN)
│   ├── FUNCIONAIS-F1-F8.md                # Eixo F completo
│   ├── DISCIPLINAS-D01-D20.md             # Eixo D completo (⚠️ numeração de S divergente — ver Gaps)
│   ├── EMBEDDER-DECISION.md               # G010 — recomendação, pendente aprovação MN (⚠️ contradiz achado do audit — ver Gaps)
│   ├── SUPABASE-PROJECT-AUDIT.md          # G012 — auditoria real via MCP Supabase
│   ├── SEGMENTOS-S12-S13-DECISION.md      # G014 — investigação real via MCP Supabase; confirma S11/S12/S13
│   ├── SEGMENTO-S11-MINERACAO-GAP-G015.md # G015 — S11 (Mineração) identificado; roadmap formalização (novo, 2026-07-31)
│   ├── DEPLOY-CHECKLIST-v5.0.md           # checklist completo v4.2 + v5.0
│   ├── DEPLOY-v4.2.md                     # runbook manual (Supabase + SharePoint)
│   └── COWORK-INTEGRATION.md              # runbook de integração Maestro ↔ Cowork
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

- **v5.3** (2026-08-23) — **Review de arquitetura manta-arquiteto-ia
  concluído (Etapas 1-4, gate humano MN)**. Implementadas 3 das 4
  propostas originais: backend real de dispatch via Claude Agent SDK
  (`backend/maestro_dispatch.py` + `backend/agent_registry.py`),
  aluci-guard como hook PreToolUse determinístico
  (`.claude/hooks/pretooluse_aluci_guard.py`), e correção do bug real
  de resolução de slug para os 6 agentes pinados em produção
  (`agente-X.v5.0.md`). A 4ª proposta (renomear os arquivos pinados)
  foi **retirada** ao se descobrir, já na implementação, que o sufixo
  de versão é um mecanismo de produção intencional documentado em
  `docs/DEPLOYMENT-GUIDE.md` — não uma inconsistência. Também corrigidos,
  como efeito colateral necessário para conseguir rodar/verificar os
  testes: `pytest.ini` sem 4 markers usados por `conftest.py`
  (causava `INTERNALERROR`, não apenas falha, em qualquer coleta que
  tocasse `test_cross_agent_flows.py`), `tests/lib/agent_loader.py`
  derrubando a coleta inteira ao encontrar qualquer agente sem
  frontmatter (8 arquivos hoje), e 9 agentes horizontais legados sem
  o slug de arquivo citado neste CLAUDE.md. Novo gap registrado: IDs de
  modelo divergentes entre a tabela "Model Tiering" deste documento e
  `.claude/settings.json`. Ver seção "REVIEW DE ARQUITETURA — v5.3".
- **v5.2** (2026-08-22) — catálogo de fontes de receita setorial (mão de
  obra, equipamento, aço, cimento) para os 8 segmentos S1-S10 (Rodovias,
  Ferrovias, Portos, Aeroportos, Saneamento, Metrôs, Energia, Barragens),
  complementando o modelo baseado em CAPEX (Livro Azul). Ranking de
  melhor fonte Brasil × exterior por segmento + proposta de padronização.
  Ver `pesquisa-fontes/FONTES_RECEITA_SETORIAL.md`.
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
