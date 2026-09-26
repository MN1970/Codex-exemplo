# Registro de agentes do Manta Maestro — referência completa

> Extraído do `CLAUDE.md` na v5.5.0 (2026-09-26), sem alteração de
> conteúdo. O `CLAUDE.md` guarda só o núcleo (regras, planejador,
> catálogo compacto); este arquivo é lido **sob demanda**, quando a
> tarefa precisa do detalhe de eixos, routing, SharePoint ou padrões de
> output. Ver `docs/maestro/PLANEJADOR.md`.

## Modelo de 4 eixos (S×A×F×D)

A v5.0 formaliza o modelo do dossiê/arquitetura v3.0.0: qualquer
consulta ao Maestro se posiciona na interseção de **4 eixos
ortogonais**, mais um eixo temporal auxiliar que se aplica a qualquer
composição:

| Eixo | Pergunta que responde | Cardinalidade | Exemplos |
| --- | --- | --- | --- |
| **S** — Segmento | Qual o domínio de infraestrutura? | S1–S11 (numeração real do SharePoint, corrigida 2026-09-07; Óleo&Gás e Mineração sem S confirmado — ver "Eixo S") | Rodovias, Portos, Saneamento |
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

### ✅ Numeração corrigida em 2026-09-07 — adota a numeração real do SharePoint

> Esta seção usava até v5.4.2 uma numeração ("Convenção A": S6=Portos…
> S10=Barragens, com S11=Mineração/S12=Óleo&Gás/S13=Edificações como
> "propostos") que a própria versão anterior deste documento já
> reconhecia como divergente de uma "Convenção B" presente em 3
> arquivos do repositório. A "verificação" que sustentava a Convenção A
> na época consultava `manta_agent_capabilities` num projeto Supabase
> (`ogxxgvgtulrbbppshjie`) — **essa infraestrutura Supabase/RAG nunca
> foi confirmada como real**, faz parte da mesma divergência maior
> registrada em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`. Ou seja: a
> "fonte de verdade" citada para descartar a Convenção B era, ela
> mesma, não verificada.
>
> Em 2026-09-07, com acesso real (leitura/escrita) ao SharePoint da
> Manta via `SharePoint_Manta` MCP, lemos a fonte real —
> `Documentos Compartilhados/04_IA/Manta-Maestro/09-base-conhecimento/
> INDICE-CANONICAL.md` (índice canônico ativo, gerado 2026-07-11) — e
> confirmamos que a numeração real é **exatamente a "Convenção B"** que
> este arquivo havia descartado: **S1–S11**, com Edificações=S6 e
> Barragens=S11 (não S6=Portos/S10=Barragens). A tabela abaixo foi
> corrigida para bater com essa fonte real. Ver
> `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` para o restante da
> divergência (agentes, RAG, infraestrutura) ainda não reconciliado.

| Código | Segmento | Agente | Status |
| --- | --- | --- | --- |
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Imobiliário | `agente-S5-imobiliario` (real, SharePoint) | ✅ **Corrigido em 2026-09-11** — leitura ao vivo confirma que o vertical S5 já existe e é maduro (v3.0.0, 5 sub-agentes: viabilidade, incorporação/patrimônio de afetação, avaliação, gestão de empreendimento, exit/securitização). A frase anterior ("sem agente vertical dedicado... decisão MN pendente") estava desatualizada. Este repositório ainda não tem o arquivo espelhado localmente. **Decisão MN (2026-09-13)**: manter S5 (vertical) e Manta 04 (horizontal) coexistindo como estão hoje — sem reconciliação de escopo por enquanto. Ver `docs/PLANEJAMENTO-MANTA-MAESTRO.md` §2. |
| S6 | Edificações (residencial, comercial, galpão, hospitalar, institucional, data center) | agente-edificacoes | Renumerado de "S13" para **S6** (era tratado como "proposto"; no índice real não há essa distinção — ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` para o que ainda falta reconciliar em status/RAG/routing) |
| S7 | Portos | agente-portos | Renumerado de "S6" para **S7** |
| S8 | Aeroportos | agente-aeroportos | Renumerado de "S7" para **S8** |
| S9 | Saneamento | agente-saneamento | Renumerado de "S8" para **S9** — PRIORIDADE AySA |
| S10 | Energia | agente-energia | Renumerado de "S9" para **S10** — ANEEL/State Grid |
| S11 | Barragens | agente-barragens | Renumerado de "S10" para **S11** |

**Sem correspondência confirmada na numeração real** (índice canônico
vai só até S11): `agente-oleo-gas.md` (antigo "S12") e a "Mineração"
antes listada como "S11" neste arquivo. Nenhum dos dois aparece em
`INDICE-CANONICAL.md`. Não foram renumerados nem removidos — ficam
sinalizados como **sem segmento real confirmado**, aguardando decisão
MN (podem ser: (a) capacidades futuras ainda não formalizadas no
SharePoint, (b) conteúdo específico deste repositório sem
correspondência real, a descontinuar). `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md`
e `docs/SEGMENTOS-S12-S13-DECISION.md` documentam o raciocínio anterior
(hoje sabemos que a "fonte de verdade" que usavam — Supabase — não
estava confirmada) e são mantidos como histórico.

---

## Eixo A — Atividades

Documentado por completo em `docs/ATIVIDADES-A1-A10.md` (v1.0,
2026-07-31) — descrição, entradas/saídas, critérios de aceitação,
metodologia e handoffs por atividade. Resumo:

| Código | Atividade | Agente(s) responsável(is) | Status do mapeamento |
| --- | --- | --- | --- |
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
| --- | --- | --- |
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

> ✅ **Nota resolvida em 2026-09-07**: `docs/DISCIPLINAS-D01-D20.md` usa
> a numeração de segmento (S6=Edificações … S11=Barragens) que este
> `CLAUDE.md` **agora também adota** (ver "Eixo S — Segmentos") — era a
> numeração real do SharePoint o tempo todo. Nenhuma leitura mental de
> conversão é mais necessária: os códigos `Sx` desta matriz batem
> diretamente com a tabela de "Eixo S" acima.

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

Exemplos de composição (atualizados em 2026-09-07 para a numeração real
do SharePoint — ver "Eixo S — Segmentos"; os códigos S originais destes
exemplos, de `ARQUITETURA-AGENTES-IA.md` v3.0.0 §2.6, usavam a
numeração antiga já corrigida):

```text
S9.A3.D07  = Saneamento + Orçamento + Econômica
            → Manta 05 (agente-orcamento) com contexto de saneamento
              (RAG san:*, handoff de agente-saneamento)

S7.A2.D01  = Portos + Quantidades + Hidráulica
            → cubagem de dragagem do canal de acesso e bacia de evolução

S10.A6.D05 = Energia + Contratual + Elétrica
            → Manta 02 (contratual) com contexto de energia
              (RAG ene:*, handoff de agente-energia)

S11.A10.D02 = Barragens + Risco + Estrutural
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

## Mapa completo de agentes — 21 operacionais + 2 sem segmento confirmado

Contagem operacional confirmada: **12 horizontais + 9 verticais
operacionais** = 21 agentes. Manta 20 (ESG) é agora **operacional v1.0**
(P3-04 Design Agent). `agente-oleo-gas` e a "Mineração" (antigos
"S12"/"S11" desta numeração já corrigida) não têm segmento real
confirmado no SharePoint (`INDICE-CANONICAL.md` vai só até S11) — ver
nota em "Eixo S — Segmentos" e `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.
Não somam ao total operacional.

### Horizontais (transversais a todos os segmentos) — 11 agentes

| Código | Agente | Arquivo | Aliases | Tier default | Status |
| --- | --- | --- | --- | --- | --- |
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

### Verticais por segmento (C3) — 9 operacionais + 2 sem segmento confirmado

Numeração corrigida em 2026-09-07 para bater com o SharePoint real —
ver "Eixo S — Segmentos" para a explicação completa.

| Código | Segmento | Agente | Status |
| --- | --- | --- | --- |
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Imobiliário | `agente-S5-imobiliario` (real, SharePoint, v3.0.0) | ✅ Corrigido 2026-09-11 — ver nota em "Eixo S" |
| S6 | Edificações | agente-edificacoes | Renumerado de "S13" |
| S7 | Portos | agente-portos | Renumerado de "S6" |
| S8 | Aeroportos | agente-aeroportos | Renumerado de "S7" |
| S9 | Saneamento | agente-saneamento | Renumerado de "S8" — PRIORIDADE AySA |
| S10 | Energia | agente-energia | Renumerado de "S9" — ANEEL/State Grid |
| S11 | Barragens | agente-barragens | Renumerado de "S10" |
| *(sem S confirmado)* | Óleo & Gás | agente-oleo-gas | Sem segmento real confirmado — ver "Eixo S" |

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento para Q1 do intake. O dispatch é por **slug de
agente** (não por número de segmento) — por isso a numeração dos
segmentos (corrigida em 2026-09-07, ver "Eixo S") é apenas rótulo
informativo, sem efeito sobre esta lógica:

```text
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

**Edificações (S6) e Óleo & Gás (sem S confirmado) ainda NÃO têm
keyword de routing** (confirmado em `agente-edificacoes.md` e
`agente-oleo-gas.md`, seção "Ferramentas e integrações" de cada um) —
o Maestro não consegue despachar para esses dois agentes hoje, mesmo
que o usuário use as palavras-chave descritas em seus frontmatters.

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

## RAG — notas complementares

A tabela de coleções fica no `CLAUDE.md` (seção "RAG — Coleções em Supabase"). Notas que a acompanhavam:

**9 coleções confirmadas por auditoria real** (não apenas por arquivo
de migração candidata) — ver `docs/SUPABASE-PROJECT-AUDIT.md`, que
executou `list_tables` no projeto `ogxxgvgtulrbbppshjie`
(`manta-maestro`, `sa-east-1`, `ACTIVE_HEALTHY`) e confirmou
`rag_collections` com 9 linhas, `sp_agent_routing` com 9 linhas,
`maestro_routing_keywords` com 50 linhas, `manta_rag_chunks` com 204
linhas e `manta_rag_documents` com 111 linhas.
Sub-prefixos de contexto (mantidos do v4.2):

- `san:br:` / `san:ar:` — saneamento por país (Brasil × Argentina AySA).
- `ene:t:` / `ene:d:` / `ene:g:` — energia por transmissão/distribuição/geração.
- `bar:c:` / `bar:t:` / `bar:e:` / `bar:r:` — barragens por tipologia.

> ✅ **Divergência de embedder resolvida em 2026-09-07** — a arquitetura
> real (`09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md`, lida via
> `SharePoint_Manta` MCP) confirma `bge-small-en-v1.5` (384-d) como
> canônico (decisão de 26/07/2026); `bge-m3` foi avaliado em 24/07/2026
> e **rejeitado**. O comentário "1024d bge-m3" na coluna de
> `manta_rag_chunks` citado em `docs/SUPABASE-PROJECT-AUDIT.md` é de
> 03/07/2026 — anterior à decisão real, ficou desatualizado. Ver
> `docs/EMBEDDER-DECISION.md` e `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.

Migração candidata das 5 coleções v4.2:
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`.

---

## SHAREPOINT — Routing rules (sp_agent_routing)

Confirmado por auditoria real: tabela `sp_agent_routing` tem 9 linhas
em produção (ver seção RAG acima).

| Agente | Pasta SP sugerida | Pattern |
| --- | --- | --- |
| agente-saneamento | `03_Projetos/Saneamento/*` | `*.pdf`, `*.dwg`, `*.xlsx` |
| agente-energia | `03_Projetos/Energia/*` | `*.pdf`, `*.dwg`, `*.xlsx` |
| agente-portos | `03_Projetos/Portos/*` | `*.pdf`, `*.dwg`, `*.xlsx` |
| agente-aeroportos | `03_Projetos/Aeroportos/*` | `*.pdf`, `*.dwg`, `*.xlsx` |
| agente-barragens | `03_Projetos/Barragens/*` | `*.pdf`, `*.dwg`, `*.xlsx` |
| agente-oleo-gas | `03_Projetos/OleoGas/*` *(a criar)* | `*.pdf`, `*.dwg`, `*.xlsx` — 🔲 planejado, segmento sem numeração real confirmada |
| agente-edificacoes | `03_Projetos/Edificacoes/*` *(a criar)* | `*.pdf`, `*.dwg`, `*.xlsx` — 🔲 planejado, segmento renumerado para S6, pendente gate MN |

---

## PADRÕES DE OUTPUT POR CLIENTE

Referências canônicas de formato de entregável (EAP em Excel/PPT,
relatório, codificação de documentos, identidade visual) por cliente,
levantadas do SharePoint. Todo agente vertical deve seguir o padrão do
cliente ao gerar output para ele.

| Cliente | Doc de referência | Status |
| --- | --- | --- |
| Motiva (ex-CCR Rodovias) | [`docs/PADRAO-OUTPUT-MOTIVA.md`](docs/PADRAO-OUTPUT-MOTIVA.md) · templates: [`EAP-PADRAO-MOTIVA.xlsx`](docs/templates/EAP-PADRAO-MOTIVA.xlsx), [`PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx`](docs/templates/PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx) | ✅ EAP Excel/PPT/relatório/codificação implementados (aprovado MN) · ✅ routing por cliente + referenciado em agente-orcamento/cronograma/apresentacoes/contratual · ⚠️ cores de marca não localizadas — templates usam paleta neutra Manta até confirmação · ⚠️ upload para o SharePoint da equipe ainda pendente (ação manual, MCP atual é read-only) |

---

## MODEL TIERING

| Tier | Modelo | Uso típico |
| --- | --- | --- |
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico |

O Maestro escala dinamicamente de tier dentro de uma sessão (Haiku →
Sonnet ao entrar no vertical → Opus se detectar complexidade).

---

## Arquivos deste repositório

```text
Codex-exemplo/
├── CLAUDE.md                              # este arquivo (master registry, v5.2)
├── README.md
├── .claude/
│   └── agents/
│       ├── agente-portos.md               # S7 real (frontmatter interno ainda diz S6 — renumeração pendente, ver Deploy checklist)
│       ├── agente-aeroportos.md           # S8 real (frontmatter interno ainda diz S7 — renumeração pendente)
│       ├── agente-saneamento.md           # S9 real (frontmatter interno ainda diz S8 — renumeração pendente) — prioridade AySA
│       ├── agente-energia.md              # S10 real (frontmatter interno ainda diz S9 — renumeração pendente) — ANEEL/State Grid
│       ├── agente-barragens.md            # S11 real (frontmatter interno ainda diz S10 — renumeração pendente)
│       ├── agente-esg.md                  # Manta 20 — P3-04 Design Agent ESG (v1.0, 2026-08-02)
│       ├── agente-oleo-gas.md             # sem segmento real confirmado (frontmatter interno ainda diz S12)
│       └── agente-edificacoes.md          # S6 real (frontmatter interno ainda diz S13 — renumeração pendente)
├── docs/
│   ├── PADRAO-OUTPUT-MOTIVA.md            # v5.2 — padrão de output cliente Motiva
│   ├── templates/
│   │   ├── EAP-PADRAO-MOTIVA.xlsx               # 🆕 v5.3 — template EAP (capa + hierarquia 4 níveis)
│   │   └── PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx  # 🆕 v5.3 — template capa/sumário/conteúdo
│   ├── ATIVIDADES-A1-A10.md               # Eixo A completo (rascunho p/ revisão MN)
│   ├── FUNCIONAIS-F1-F8.md                # Eixo F completo
│   ├── DISCIPLINAS-D01-D20.md             # Eixo D completo (✅ numeração de S já era a real — resolvido 2026-09-07)
│   ├── EMBEDDER-DECISION.md               # G010 — recomendação, pendente aprovação MN (⚠️ contradiz achado do audit — ver Gaps)
│   ├── SUPABASE-PROJECT-AUDIT.md          # G012 — auditoria real via MCP Supabase
│   ├── SEGMENTOS-S12-S13-DECISION.md      # G014 — investigação real via MCP Supabase; confirma S11/S12/S13
│   ├── SEGMENTO-S11-MINERACAO-GAP-G015.md # G015 — S11 (Mineração) identificado; roadmap formalização (novo, 2026-07-31)
│   ├── MODELO-MESTRE-PROPOSTA.md          # 🆕 v5.4.2 — corrigido: skill real tem 14 seções/M1-M5, não 18/M6 (2026-09-07)
│   ├── PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md # 🆕 v5.4.2 — addendum M6 original marcado histórico; mudança já aplicada na skill real
│   ├── GAP-RECONCILIACAO-SHAREPOINT-REAL.md # 🔴 novo, crítico — repositório diverge do Manta Maestro real (SharePoint), decisão MN pendente
│   ├── DEPLOY-CHECKLIST-v5.0.md           # checklist completo v4.2 + v5.0
│   ├── DEPLOY-v4.2.md                     # runbook manual (Supabase + SharePoint)
│   ├── COWORK-INTEGRATION.md              # runbook de integração Maestro ↔ Cowork
│   ├── PLANEJAMENTO-MANTA-MAESTRO.md      # 🆕 2026-09-11 — relatório de reconciliação (achados reais vs. suposições, ver §1-3)
│   ├── D03-GEOTECNIA-APLICACAO-PROJETOS-MANTA.md # 🆕 2026-09-11 — guia prático (D03 real, não um agente novo)
│   └── MATRIZ-CONHECIMENTO-POR-AGENTE.md  # 🆕 2026-09-11 — conhecimento essencial dos 21+ agentes (hipótese, não cruzada linha a linha com o real)
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
