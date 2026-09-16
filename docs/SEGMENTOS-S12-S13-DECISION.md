# Decisão — Segmentos S12 (Óleo & Gás) e S13 (Edificações)

**Gap**: G014 — citado em `CLAUDE.md` v5.0, seção "Gaps abertos" e
"Questionário de decisão para MN", item 2.
**Data**: 2026-07-31
**Autor**: Sonnet 12 (investigação via MCP Supabase, execução direta —
toda evidência abaixo vem de `list_projects`, `list_tables` e
`execute_sql` reais contra o projeto `manta-maestro`, sem dados
fabricados)
**Status**: Investigação concluída — recomendação pronta, aguarda gate
humano MN antes de aplicar a migração e fazer merge dos dois novos
agentes.

---

## 0. Resumo executivo

**S12 e S13 são segmentos reais, não erro de cadastro.** Ambos estão
registrados em `manta_agent_capabilities` (projeto Supabase
`ogxxgvgtulrbbppshjie`, tabela viva do Maestro) com `ativo = true`,
descrição de escopo coerente, tags de domínio consistentes e
delimitação explícita do que cada um NÃO cobre — características de um
registro deliberado, não de uma entrada acidental ou lixo de teste.

- **S12 = Óleo & Gás** — engenharia civil de downstream (refino) +
  midstream (dutovias, terminais). Explicitamente **não cobre**
  exploração/produção (reservatório, poço).
- **S13 = Edificações** — engenharia civil/estrutural de edificações
  (residencial, comercial, galpão, hospital, universidade, data
  center). Distinto de Manta 04 (Imobiliário), que é avaliação/negócio
  imobiliário, não projeto de edifício.

O gap real não é "esses segmentos existem por engano" — é que **foram
registrados na camada de capacidades (Supabase) sem passar pelo
checklist de formalização** que os 5 agentes S6–S10 da v4.2 seguiram
(agente `.md`, coleção RAG, rota SharePoint, palavra-chave de routing,
patch no `CLAUDE.md`, gate MN). Por isso o Maestro sabe que S12/S13
"existem" na camada de capacidades mas **não consegue rotear** nenhuma
consulta a eles hoje.

**Recomendação**: formalizar os dois (não remover). Este documento
entrega os dois artefatos que faltavam — `agente-oleo-gas.md` e
`agente-edificacoes.md` — e uma migração candidata para RAG/routing.
Falta apenas o gate humano MN para fechar o ciclo.

---

## 1. Metodologia

Evidência coletada nesta sessão, nesta ordem:

1. Varredura do repositório (`grep -ri` por `S12`, `S13`, `oleo`,
   `gás`, `edific`) — **zero ocorrências** em `CLAUDE.md`, `README.md`,
   `.claude/agents/*.md`, `sharepoint/**`, `supabase/migrations/*.sql`
   e `tests/routing/prompts.md`, confirmando o sintoma relatado no gap
   ("zero menção em qualquer arquivo").
2. `list_projects()` → identificado `manta-maestro`
   (`ogxxgvgtulrbbppshjie`, `sa-east-1`, `ACTIVE_HEALTHY`) como o único
   projeto Supabase ativo da organização.
3. `list_tables()` → confirmado que `rag_collections` (9 linhas),
   `sp_agent_routing` (9 linhas) e `maestro_routing_keywords` (50
   linhas) **não contêm** nenhuma entrada para S11, S12 ou S13.
4. `execute_sql` em `manta_agent_capabilities` → **achado central desta
   investigação**: a tabela tem 30 linhas, incluindo `agent_id` de
   `03-S1` até `03-S13` (13 verticais, não 10). Ver seção 2.

Nenhuma tabela de "segmentos" dedicada existe no schema — o que o gap
chama de "S12/S13 existem como segmentos ativos no Supabase" se refere,
na prática, a essas duas linhas em `manta_agent_capabilities`.

---

## 2. Evidência bruta — `manta_agent_capabilities`

Query: `SELECT agent_id, capability, descricao, tags, ativo,
registered_at FROM manta_agent_capabilities WHERE agent_id ~ '^03-S'`.

Todas as 13 linhas (`03-S1`…`03-S13`) têm o **mesmo** `registered_at` =
`2026-07-12 12:48:56` — indício de que foram inseridas em **um único
lote**, provavelmente um script de seed ou uma rodada de
auto-registro de capacidades (a tabela tem o comentário "Cada agente
registra suas habilidades quando entra em operação"), e não uma a uma
conforme cada agente era formalizado.

| `agent_id` | `capability` | `descricao` | `ativo` |
|---|---|---|---|
| 03-S10 | especialista-barragens | Barragens — concreto (CCR/CFRD), terra, enrocamento, rejeitos (TSF). Pós-Brumadinho. | true |
| **03-S11** | **especialista-mineracao** | **Mineração — cava/subterrânea/aluvionar. TSF encaminha para S10. NRM/NR-22 + SME/CIM/JORC/NI 43-101.** | **true** |
| **03-S12** | **especialista-oleo-gas** | **Óleo & Gás — engenharia CIVIL. Downstream (refino) + midstream (dutos) + terminais. NÃO cobre reservatório/poço.** | **true** |
| **03-S13** | **especialista-edificacoes** | **Edificações — vertical residencial/comercial + galpão + hospital/universidade. NBR 15575 (MCMV), LEED, BIM.** | **true** |

Tags registradas:
- `03-S12`: `petróleo`, `óleo e gás`, `ANP`, `gasoduto`, `refinaria`,
  `API 650`, `ANSI B31`, `NFPA 30`, `HAZOP`, `vertical`.
- `03-S13`: `edificação`, `torre`, `galpão`, `warehouse`, `data
  center`, `MCMV`, `NBR 15575`, `LEED`, `BIM`, `vertical`.

**Por que isso pesa a favor de "segmento real" e não "erro de
cadastro"**: uma entrada acidental (linha duplicada, teste manual,
typo) tende a ter descrição vazia, genérica ou copiada. Aqui, cada
linha tem descrição própria, tags de domínio específicas do setor e —
o ponto mais forte — **delimitação explícita de fronteira** ("NÃO
cobre reservatório/poço" em S12; "TSF encaminha para S10" em S11).
Ninguém escreve uma exclusão de escopo cuidadosa para uma linha lixo.

> **Achado colateral (fora do escopo direto de S12/S13, mas do mesmo
> lote)**: `03-S11` = **Mineração**, também `ativo=true`, também sem
> nenhuma menção em `CLAUDE.md`, `.claude/agents/`, SharePoint ou
> routing. É o mesmo problema estrutural de S12/S13. Recomenda-se abrir
> um gap companheiro (sugestão: **G015**) para tratar S11 com o mesmo
> processo — não incluído nos entregáveis deste documento porque G014
> definiu escopo apenas S12/S13, mas ignorá-lo deixaria uma terceira
> ponta solta idêntica às duas que este documento resolve.

---

## 3. S12 — Óleo & Gás: decisão

**Decisão: segmento novo, formalizar.**

Escopo final (baseado na `descricao`/tags registradas, não na sugestão
genérica do ticket do gap — ver nota de correção abaixo):

| Dentro do escopo | Fora do escopo |
|---|---|
| Refino (envoltória civil: tancagem, bacias de contenção, fundações de equipamentos) | Exploração sísmica, perfuração, completação de poço |
| Midstream: dutovias (oleoduto/gasoduto), estações de bombeio/compressão | Engenharia de reservatório |
| Terminais de estocagem e distribuição (TEs, GLP) | Plataforma offshore / FPSO (estrutura naval) |
| Distribuição: bases, pontos de entrega a granéis | Engenharia de processo de refino (PFD/P&ID) — cobre só a envoltória civil |

> **Nota de correção em relação ao briefing do gap**: o ticket original
> sugeria uma rubrica com "exploração, produção" no escopo. A evidência
> registrada em produção (`03-S12`) diz o oposto — exclui
> explicitamente reservatório/poço (upstream/E&P), porque essas
> disciplinas exigem engenharia de petróleo, não a engenharia
> civil/estrutural que é a competência real da Manta. Este documento
> segue a evidência do banco (fonte de verdade), não a sugestão inicial
> do ticket — reportando a divergência explicitamente em vez de
> silenciá-la.

Normas-chave confirmadas: ANP, API 650/653, ANSI/ASME B31.3/B31.4/B31.8,
NFPA 30/15/16, NR-20, NR-13, metodologia HAZOP.

Artefato entregue: **`.claude/agents/agente-oleo-gas.md`** (criado
nesta sessão, mesmo template dos agentes S6-S10 existentes).

---

## 4. S13 — Edificações: decisão

**Decisão: segmento novo, formalizar — mas com uma pendência de
governança a resolver antes do merge (seção 5).**

### 4.1 Diferenciação vs. Imobiliário

O ticket do gap pede para "clarear diferença vs. S6 (Imobiliário de
v4.2)". Correção factual: em nenhuma versão deste repositório
(`CLAUDE.md` v4.2 ou v5.0) "Imobiliário" foi codificado como `S6` — é
sempre **Manta 04**, um agente **horizontal** (Eixo 1), não um vertical
de segmento. A confusão provável é com a numeração alternativa citada
no skill `manta-maestro` (v5.0.1), que usa `S6` para **Edificações**
(não Imobiliário) — ver seção 5. De qualquer forma, a diferenciação de
fundo que importa é esta:

| | Manta 04 — Imobiliário (horizontal) | S13 — Edificações (vertical) |
|---|---|---|
| Natureza | Negócio: avaliação de ativo, M&A imobiliário, land banking, feasibility financeira | Engenharia: projeto estrutural, fundações, sistemas prediais, desempenho (NBR 15575) |
| Atua em | Qualquer segmento vertical que envolva um ativo imobiliário (ex.: desapropriação para rodovia) | Apenas quando o **produto da consulta é o próprio edifício** |
| Overlap real | Nenhum direto — handoff pontual quando avaliação depende de orçamento de construção | Handoff pontual quando o cliente quer viabilidade financeira, não o projeto técnico |

**Conclusão**: não há redundância — nunca existiu, antes de S13, um
agente vertical que cobrisse a disciplina "projetar/construir um
edifício" (a família S1-S10 cobre rodovia/OAE/ferrovia/metrô/porto/
aeroporto/saneamento/energia/barragem — nenhuma delas é "prédio").

### 4.2 Escopo confirmado

Tipologias: residencial (unifamiliar, multifamiliar, MCMV faixas 1-4),
comercial (lajes corporativas, varejo), galpão logístico/industrial
leve (inclui envoltória civil de data center — não o projeto elétrico/
mecânico de TI), institucional (hospital, universidade).

Normas-chave: NBR 15575 (desempenho, referência para MCMV), NBR 6118,
NBR 8800, NBR 6120, LEED, BIM/Decreto 10.306/2020, NBR 9050
(acessibilidade).

Artefato entregue: **`.claude/agents/agente-edificacoes.md`** (criado
nesta sessão).

---

## 5. Achado crítico de reconciliação de numeração (correção necessária antes do merge)

Esta seção não estava no escopo original do ticket, mas é
**indispensável** para que a formalização de S12/S13 não piore a
confusão em vez de resolvê-la. Existem hoje, neste mesmo repositório e
no ecossistema Manta, **quatro numerações diferentes** para os
segmentos verticais, produzidas por sessões/documentos diferentes na
mesma janela de tempo (consolidação de 15 Sonnets, 2026-07-31):

| Fonte | S6 | S7 | S8 | S9 | S10 | S11 | S12 | S13 |
|---|---|---|---|---|---|---|---|---|
| **`manta_agent_capabilities` (Supabase, produção — fonte de verdade)** | Portos | Aeroportos | Saneamento | Energia | Barragens | Mineração | Óleo & Gás | Edificações |
| `CLAUDE.md` v4.2 (este repo, versão original) | Portos | Aeroportos | Saneamento | Energia | Barragens | *(não existe)* | *(não existe)* | *(não existe)* |
| `CLAUDE.md` v5.0 (este repo, rascunho de hoje) | **Edificações** (planejado) | Portos | Aeroportos | Saneamento | Energia | Barragens | TBD | TBD |
| `docs/ATIVIDADES-A1-A10.md` (este repo, rascunho de hoje) | Edificações | Portos | Aeroportos | Saneamento | Energia | Barragens | *(não citado)* | *(não citado)* |
| skill `manta-maestro` (descrição, v5.0.1) | Edificações | Portos | Aeroportos | Saneamento | Energia | Barragens | *(não citado)* | *(não citado)* |

A tabela deixa claro: **a única fonte com evidência de execução real
(linhas em tabela de produção, `ativo=true`, timestamp de registro) é a
primeira** — as outras três são teorizações de documentação, e duas
delas (`CLAUDE.md` v5.0 e `ATIVIDADES-A1-A10.md`) foram escritas *hoje*,
citando a *descrição* da skill `manta-maestro` como se fosse a fonte
autoritativa, **sem consultar o banco real** (o próprio `CLAUDE.md`
v5.0 admite isso na seção "Gaps abertos": *"nenhuma chamada MCP
Supabase foi feita para confirmar"*).

**Recomendação**: tratar `manta_agent_capabilities` como fonte de
verdade e **reverter a hipótese de renumeração** do `CLAUDE.md` v5.0
(a seção "Eixo S — Segmentos" que insere Edificações como novo S6 e
desloca Portos→S7...Barragens→S11). Isso deve ser feito pelo dono da
consolidação v5.0 (não neste documento, para não conflitar com um
arquivo em edição concorrente) — mas o achado precisa chegar a essa
pessoa antes do merge. Ação sugerida: registrar como item explícito do
"Questionário de decisão para MN" (já existe espaço — ver item 2, que
este documento responde) e adicionar um item novo sobre a renumeração
divergente.

---

## 6. Impacto e plano de formalização

### 6.1 Já entregue nesta sessão

- `.claude/agents/agente-oleo-gas.md` — agente S12 completo (contexto,
  ordem canônica, handoffs, delimitação de escopo).
- `.claude/agents/agente-edificacoes.md` — agente S13 completo,
  incluindo a tabela de diferenciação vs. Manta 04.
- `supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql` — migração
  **candidata** (não aplicada) para as 2 coleções RAG, 2 rotas
  SharePoint e 15 palavras-chave de routing que faltam.

### 6.2 Pendente (gate humano / fora do alcance de execução direta)

- [ ] MN aprova o escopo de S12 (nota da seção 3) e S13.
- [ ] MN decide sobre a reconciliação de numeração (seção 5) antes do
  merge do `CLAUDE.md` v5.0.
- [ ] Aplicar `2026_07_31_v4_3_agents_s12_s13.sql` em produção (mesmo
  fluxo do runbook `docs/DEPLOY-v4.2.md`).
- [ ] Criar pastas SharePoint `03_Projetos/{OleoGas,Edificacoes}/` e
  `01-agentes-fundamentais/agente-{oleo-gas,edificacoes}/`.
- [ ] Escrever e subir os 2 `SKILL.md` para SharePoint.
- [ ] Adicionar blocos "S12 — Óleo & Gás" e "S13 — Edificações" a
  `tests/routing/prompts.md`.
- [ ] Abrir gap companheiro (G015 sugerido) para o achado de S11
  (Mineração) — mesmo padrão, não resolvido aqui por estar fora do
  escopo declarado de G014.
- [ ] Achado correlato de segurança (já registrado por outra
  investigação desta consolidação, `docs/SUPABASE-PROJECT-AUDIT.md`
  AI-6): `rag_collections`, `sp_agent_routing` e
  `maestro_routing_keywords` estão com RLS **desabilitado** — qualquer
  linha inserida pela migração deste documento herda essa exposição
  até o AI-6 ser executado. Não é motivo para adiar S12/S13, mas deve
  ser lembrado ao aplicar a migração.

### 6.3 Se a decisão fosse "remover" (não é a recomendação, registrado por completude)

Caso o MN julgue que S12/S13 foram registrados por engano (ex.: rodada
de teste que não deveria ter sido promovida com `ativo=true`), o
rollback é: `UPDATE manta_agent_capabilities SET ativo=false WHERE
agent_id IN ('03-S12','03-S13')` (preferível a `DELETE`, para manter
histórico) e descartar os dois arquivos de agente e a migração criados
nesta sessão. Dado o nível de detalhe e a delimitação de escopo já
presentes nas descrições registradas (seção 2), esta investigação
**não encontrou evidência que sustente essa hipótese** — mas o caminho
fica documentado caso surjam informações novas.

---

## 7. Recomendação final

**Formalizar S12 (Óleo & Gás) e S13 (Edificações) como segmentos
verticais operacionais**, seguindo o mesmo checklist usado para S6-S10
na v4.2:

1. Aceitar os dois `agente-*.md` entregues nesta sessão como ponto de
   partida (revisão técnica de conteúdo ainda cabe ao especialista de
   domínio antes do merge — este documento não substitui esse review).
2. Aplicar a migração candidata `2026_07_31_v4_3_agents_s12_s13.sql`
   após aprovação MN.
3. Resolver a colisão de numeração (seção 5) **antes** de publicar
   qualquer número de segmento externamente — o risco não é técnico
   (o routing funciona por slug, não por número), é de comunicação e
   auditoria futura.
4. Tratar S11 (Mineração) em ticket separado, mesma lógica.

Não há base factual para tratar S12/S13 como erro de cadastro — a
única coisa "errada" foi o processo (capacidade registrada sem passar
pelo checklist de documentação), não a existência do segmento.

---

## Histórico

- **2026-07-31** — versão inicial. Investigação executada por Sonnet
  12 em resposta ao gap G014, no contexto da consolidação de 15 Sonnets
  do dia. Entrega: este documento + 2 agentes `.md` + 1 migração
  candidata. Aguarda gate humano MN (itens da seção 6.2).
