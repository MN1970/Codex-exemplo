# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v5.4.4** (2026-09-08) — **a skill real de proposta mudou de
lugar de novo, no mesmo dia, e foi reaplicada**. Horas depois da
correção v5.4.2 (skill em `05-sub-skills/skill-proposta-comercial-
SKILL.md`), uma **outra sessão Claude** (Claude Desktop Windows)
tentou localizar a mesma skill, não encontrou o caminho e viu uma
estrutura totalmente diferente — essa confusão disparou, em paralelo
a esta sessão, um **saneamento estrutural real** do SharePoint
(`INDICE-CANONICAL.md` v1.1, §13), que fundiu o corpo operacional da
skill em `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md`
(v3.3.0) a partir de um pacote de conteúdo **anterior** à correção
v5.4.2 — ou seja, a segregação Tarifa×Success Fee, a exigibilidade por
formalização e a cláusula de juros de mora **ficaram órfãs** no
caminho antigo, que virou só um ponteiro de descontinuação. Reaplicadas
nesta sessão no novo caminho real como **v3.3.1** (16.191 bytes,
verificado por leitura pós-upload em 2026-09-08T00:48:09Z). Ver seção
"Modelo Mestre de Proposta" §3 e `docs/MODELO-MESTRE-PROPOSTA.md` §3
para o detalhe completo, incluindo o risco de **edição concorrente**
no SharePoint real (múltiplas sessões/processos editando a mesma
árvore no mesmo dia) — antes de editar essa skill de novo, sempre
reler o arquivo primeiro.

Consolida v5.4.3 (2026-09-07) — **fase 1 da reconciliação com o
SharePoint real: numeração de segmento corrigida**. A pedido do
usuário ("quero que os 2 se atualizem"), corrigida a numeração de
segmentos (Eixo S) para bater com o índice canônico real do SharePoint
(`INDICE-CANONICAL.md`): S1–S11, com Edificações=S6, Portos=S7,
Aeroportos=S8, Saneamento=S9, Energia=S10, **Barragens=S11** — a mesma
numeração que a v5.4.2/v5.0 chamavam de "Convenção B" e tratavam como
errada. A "Convenção A" (S6=Portos…S10=Barragens) usada até aqui não
tinha lastro real — a auditoria Supabase que a sustentava nunca foi
confirmada como infraestrutura real (ver
`docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`). Atualizadas as seções
"Eixo S", "Modelo de composição S.A.D", "Mapa completo de agentes",
"ROUTING", "RAG", "SharePoint routing rules", "Gaps abertos" e
"Questionário MN". **Não incluído nesta fase** (ver checklist e gap
dedicado): renumerar o frontmatter interno dos agentes `.md`, renomear
migrações SQL, e a reconciliação da infraestrutura Supabase/APScheduler/
ML fictícia — fases seguintes, ainda não escopadas.

Consolida v5.4.2 (2026-09-07) — **correção de premissa fabricada +
aplicação real** na skill `proposta-comercial`: a v5.4.1 (abaixo)
validava a skill contra dados nunca checados no SharePoint real (18
seções, "agente A7-bd", modo M6, proposta "MNT-2026-COM-1183_D"). Com
acesso real ao SharePoint (`SharePoint_Manta` MCP) confirmamos a skill
real (14 seções, M1–M5, referência MNT-2025-COM-1104) e **aplicamos
diretamente em produção** a ideia central da v5.4.1 — segregação
Tarifa×Success Fee, exigibilidade por formalização do evento-gatilho,
cláusula de juros de mora — no formato real da skill (resumo ≤1024
caracteres). Ver seção "Modelo Mestre de Proposta" e
`docs/MODELO-MESTRE-PROPOSTA.md`.

Consolida v5.4.1 (2026-09-01, **premissa não verificada — ver correção
acima**) — reconciliava trabalho de branch paralela: análise e
recomendação de modelo mestre de proposta técnico-comercial (variante
"M6", PTC-Infraestrutura/Concessão de grande porte), validada contra a
proposta "MNT-2026-COM-1183_D" e a skill `proposta-comercial`
("A7-bd"). Mantido como histórico — ver `docs/MODELO-MESTRE-PROPOSTA.md`
para o que era real e o que não era.

Consolida v5.4 (2026-08-31) — **Padrão Motiva ligado ao routing e aos
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
|---|---|---|---|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Imobiliário | *(sem agente vertical dedicado neste repositório)* | ⚠️ **Reclassificação pendente**: o índice canônico real trata Imobiliário como segmento vertical S5; este repositório trata "imobiliário" apenas como horizontal de negócio (Manta 04/`agente-imobiliario.md`). Decisão MN pendente sobre se cria vertical S5 dedicado ou mantém só o horizontal — fora do escopo desta correção de numeração (fase 1). |
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

```
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

### Verticais por segmento (C3) — 9 operacionais + 2 sem segmento confirmado

Numeração corrigida em 2026-09-07 para bater com o SharePoint real —
ver "Eixo S — Segmentos" para a explicação completa.

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| S5 | Imobiliário | *(sem agente vertical dedicado — ver nota em "Eixo S")* | ⚠️ Reclassificação pendente |
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
| óleo-gás | og: *(sugerido)* | ANP, API 650/653, ASME B31.3/4/8, NFPA 30, HAZOP | 🔲 Não criada — segmento sem numeração real confirmada (ver "Eixo S") |
| edificações | edi: *(sugerido)* | NBR 15575, LEED, BIM | 🔲 Não criada — segmento renumerado para S6, depende do gate MN |

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
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |
| agente-oleo-gas | 03_Projetos/OleoGas/* *(a criar)* | *.pdf, *.dwg, *.xlsx — 🔲 planejado, segmento sem numeração real confirmada |
| agente-edificacoes | 03_Projetos/Edificacoes/* *(a criar)* | *.pdf, *.dwg, *.xlsx — 🔲 planejado, segmento renumerado para S6, pendente gate MN |

---

## MODELO MESTRE DE PROPOSTA

> ⚠️ **Correção 2026-09-07**: a versão anterior desta seção (histórico
> abaixo) descrevia a skill `proposta-comercial` como tendo 18 seções,
> um "agente A7-bd" e um modo "M6" validado contra
> "MNT-2026-COM-1183_D" — nada disso bate com a skill real de
> produção. Com acesso real ao SharePoint (`SharePoint_Manta` MCP)
> nesta sessão, confirmamos que a skill real
> (`04_IA/Manta-Maestro/05-sub-skills/skill-proposta-comercial-SKILL.md`)
> tem **14 seções**, **5 modos (M1–M5)**, tabela de **12 níveis** e
> referência real **Hope PPP MNT-2025-COM-1104**; a revisão mais
> recente de MNT-2026-COM-1183 encontrada é **"_C"**, não "_D". Detalhe
> completo em `docs/MODELO-MESTRE-PROPOSTA.md`.

A ideia central (segregar **Tarifa** × **Success Fee** na seção de
Preço, definir a **exigibilidade do success fee** pela **formalização**
do evento-gatilho — economia de custo → aprovação de orçamento;
conquista → formalização da conquista; cronograma → marco formalmente
aprovado — nunca pela implementação física, e acrescentar cláusula de
**multa, juros de mora e correção monetária** por atraso de pagamento)
**já foi aplicada na skill real** em 2026-09-07, a pedido do usuário —
reescrita no formato verdadeiro dela.

> ⚠️ **A skill mudou de lugar de novo, no mesmo dia (2026-09-07/08)**:
> horas depois da correção acima, uma confusão de caminho reportada por
> outra sessão Claude disparou um saneamento estrutural real do
> SharePoint. A skill foi fundida em
> `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.0),
> puxando um pacote de conteúdo anterior à correção — **sem** as
> cláusulas acima. Reaplicadas nesta sessão como **v3.3.1** no novo
> caminho real (16.191 bytes, verificado por leitura pós-upload).
> `05-sub-skills/skill-proposta-comercial-SKILL.md` **não é mais a
> fonte** — virou um ponteiro de descontinuação. Detalhe completo em
> `docs/MODELO-MESTRE-PROPOSTA.md` §3. **O SharePoint real está sendo
> editado por múltiplas sessões em paralelo** — antes de editar essa
> skill de novo, sempre reler o arquivo primeiro.

Detalhe e checklist real em `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`
(o addendum original de "18 seções/M6" está lá marcado como
histórico/não aplicável).

Pendências: (1) revisão jurídica dos percentuais padrão de multa/juros/
correção monetária antes do próximo uso real em proposta de cliente;
(2) confirmar se existe cópia local da skill sincronizada por
`Sync-MantaMaestro.ps1` que precise do mesmo texto, para não ser
sobrescrita no próximo sync a partir da máquina local do usuário; (3)
reconciliação arquitetural mais ampla entre este repositório e o
SharePoint real — ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.

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

- **🟡 Este repositório diverge do Manta Maestro real no SharePoint
  (encontrado em 2026-09-07 — numeração e embedder já corrigidos,
  resto aberto)**: com acesso real de leitura/escrita ao
  `SharePoint_Manta` MCP nesta sessão, confirmamos que a arquitetura
  real em produção (`09-base-conhecimento/INDICE-CANONICAL.md` +
  `00-arquitetura/manta-maestro-arquitetura-v3.0.md`/`v3.2.md` +
  `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md`) é **diferente**
  da descrita neste `CLAUDE.md` em vários pontos — já corrigidos: skill
  `proposta-comercial` (ver "Modelo Mestre de Proposta"), numeração de
  segmentos (ver "Eixo S — Segmentos"), embedder G010 (ver Gaps
  abertos). **Investigação mais funda revelou que o núcleo
  Supabase/RAG é real** (projeto `ogxxgvgtulrbbppshjie`, confirmado por
  chamadas reais de API), só com especificações diferentes das
  assumidas aqui (agendamento real é `cron` Linux, não APScheduler;
  nomes de tabela diferem em partes) — mas **sem evidência real
  encontrada** para ML routing/XGBoost, consensus voting, disaster
  recovery, Docker/K8s, "Maestro OS v6.0" e a numeração "20+ agentes
  Manta NN". Análise completa e o que falta investigar em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`. Ação: decisão MN sobre
  as próximas fases (numeração — concluída; embedder — concluído;
  renumerar frontmatter dos agentes, corrigir specs de Supabase/RAG, e
  decidir o destino do que não tem lastro real — ainda não escopadas).
- **S5 (Imobiliário) sem vertical dedicado**: o índice canônico real
  trata Imobiliário como segmento vertical S5; este repositório só tem
  "imobiliário" como horizontal de negócio (Manta 04). Decisão MN
  pendente sobre criar um vertical S5 dedicado ou manter só o
  horizontal — não resolvido na correção de numeração desta versão
  (fase 1 tratou só os segmentos que já tinham agente vertical
  correspondente).
- **`agente-oleo-gas` e "Mineração" sem segmento real confirmado**: a
  numeração antiga tratava esses dois como "S12"/"S11" com base numa
  consulta a `manta_agent_capabilities` (Supabase) que nunca foi
  confirmada como infraestrutura real — ver
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`. O índice canônico real
  (`INDICE-CANONICAL.md`) vai só até S11=Barragens e não menciona
  Óleo&Gás nem Mineração. `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md` e
  `docs/SEGMENTOS-S12-S13-DECISION.md` mantidos como histórico do
  raciocínio anterior. Ação: decisão MN sobre formalizar essas
  capacidades no SharePoint real (se de fato existirem) ou
  descontinuar esse conteúdo do repositório.
- ~~**Embedder (G010)**~~ — **✅ resolvido em 2026-09-07** com decisão
  real: `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md` (SharePoint
  real, lido via `SharePoint_Manta` MCP) confirma que `bge-m3` foi
  avaliado em 24/07/2026 e **explicitamente rejeitado**, e
  `bge-small-en-v1.5` (384-d) foi **confirmado canônico em 26/07/2026**.
  O comentário de coluna que `docs/SUPABASE-PROJECT-AUDIT.md` citou
  como evidência de "schema já é bge-m3" é de 03/07/2026 — **anterior**
  à decisão real e ficou desatualizado, não reflete o estado atual.
  `docs/EMBEDDER-DECISION.md` (que recomendava migrar para bge-m3) e
  `docs/SUPABASE-PROJECT-AUDIT.md` foram corrigidos com essa
  informação. Achado relevante: **o projeto Supabase
  `ogxxgvgtulrbbppshjie` é real** (mesma conta `mneves@
  mantaassociados.com`, confirmado por chamadas reais de API na
  auditoria G012) — a infraestrutura RAG básica existe de verdade,
  ainda que com specs diferentes das assumidas em partes deste
  repositório. Ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.
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
- **Edificações (S6) e Óleo & Gás sem RAG, sem rota SharePoint, sem
  keyword de routing** — agentes existem como arquivo, mas não são
  despacháveis pelo Maestro hoje.
- **Templates Motiva sem upload real para o SharePoint da equipe**:
  `docs/templates/EAP-PADRAO-MOTIVA.xlsx` e
  `PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx` existem versionados
  neste repositório e já estão referenciados no routing e nos agentes
  de output (v5.4), mas ainda não foram copiados para
  `sites/Engenharia/.../04_IA/Manta-Maestro/` onde a equipe de fato
  trabalha. **Atualização 2026-09-07**: esta sessão passou a ter
  acesso real de escrita ao SharePoint (`SharePoint_Manta` MCP) — a
  limitação de "MCP somente leitura" registrada em `docs/DEPLOY-v4.2.md`
  não se aplica mais a partir de agora; o upload em si não foi feito
  nesta sessão (fora do escopo combinado, que era só a correção de
  numeração de segmento) mas deixou de depender de acesso externo.
- **Cor institucional da Motiva não confirmada** — ver seção 5 de
  `docs/PADRAO-OUTPUT-MOTIVA.md`; templates usam paleta neutra Manta
  até confirmação do cliente.

---

## QUESTIONÁRIO DE DECISÃO PARA MN

1. ~~**Numeração de segmento**~~ — **decidido em 2026-09-07**: adota-se
   a numeração real do SharePoint (`INDICE-CANONICAL.md`), a mesma que
   este arquivo chamava de "Convenção B". Aplicado nesta versão (ver
   "Eixo S — Segmentos"). Renumeração dos 5 agentes operacionais
   (frontmatter interno de cada `.md`) e da migração/RAG/rotas SP
   segue como próxima fase, ainda não feita.
2. **Óleo & Gás e Mineração sem segmento real confirmado**: formalizar
   como capacidades reais no SharePoint (agente `.md`, RAG, rota SP,
   routing keywords, com S confirmado) ou descontinuar esse conteúdo do
   repositório? A "fonte de verdade" usada anteriormente para
   justificá-los (Supabase `manta_agent_capabilities`) nunca foi
   confirmada como real — ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.
3. **S5 Imobiliário**: criar vertical dedicado (como no SharePoint
   real) ou manter só como horizontal (Manta 04, como hoje)?
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
- [x] ~~Reconciliar divergência de numeração de segmento (Convenção A)~~
      — **revertido em 2026-09-07**: a "Convenção A" era a numeração
      errada; a real (SharePoint) é a que este item chamava de
      "Convenção B". Ver checklist de correção logo abaixo.
- [x] Corrigir tabela de coleções RAG com dados de auditoria real (9 confirmadas — nota: fonte dessa "auditoria" é parte da infraestrutura Supabase ainda não confirmada como real, ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`)
- [x] ~~Registrar S12 (Óleo & Gás) e S13 (Edificações) como propostos~~ — Edificações renumerado para S6 (real); Óleo & Gás segue sem S confirmado
- [x] ~~Identificar S11 (Mineração) a partir de `manta_agent_capabilities`~~ — fonte não confirmada como real; S11 real é Barragens
- [x] Linkar Eixo A/F/D aos documentos dedicados já produzidos
- [x] ~~Corrigir numeração de segmento em `docs/DISCIPLINAS-D01-D20.md`, `docs/ATIVIDADES-A1-A10.md` e `agente-aeroportos.v5.0.md` (Convenção B → A)~~ — **não era necessário**: esses arquivos já usavam a numeração correta (real)
- [x] Abrir gap G015 — documentação de formalização S11 (Mineração) em `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md` (mantido como histórico)
- [ ] Reconciliar `docs/EMBEDDER-DECISION.md` com achado de
      `docs/SUPABASE-PROJECT-AUDIT.md` antes de decidir embedder
- [ ] Confirmar manualmente o destino do projeto `xgluoaa...` (AI-1)
- [ ] Aplicar RLS nas 3 tabelas expostas (AI-6)
- [ ] Criar RAG + rota SP + routing keywords para Edificações (S6) e Óleo & Gás (se aprovado)
- [ ] Rodar aluci-guard sobre este documento antes de merge
- [ ] Rodar consist-guard sobre este documento antes de merge
- [ ] Gate humano: aprovação MN antes de merge

### Correção de numeração de segmento (2026-09-07, fase 1 da reconciliação com o SharePoint real)

- [x] Ler `INDICE-CANONICAL.md` real via `SharePoint_Manta` MCP e
      confirmar a numeração real (S1–S11, Edificações=S6…Barragens=S11)
- [x] Reescrever tabela "Eixo S — Segmentos" com a numeração real
- [x] Atualizar "Mapa completo de agentes" (verticais), "Modelo de
      composição S.A.D", "ROUTING", "RAG", "SharePoint routing rules"
      com os novos códigos
- [x] Remover a nota de "inconsistência" em Eixo D (os arquivos já
      estavam certos)
- [x] Atualizar Gaps abertos e Questionário MN
- [ ] Renumerar o frontmatter interno dos 5 agentes verticais afetados
      (`agente-portos.md` S6→S7, `agente-aeroportos.md` S7→S8,
      `agente-saneamento.md` S8→S9, `agente-energia.md` S9→S10,
      `agente-barragens.md` S10→S11, `agente-edificacoes.md` S13→S6) —
      **fora do escopo desta fase**, próxima fase da reconciliação
- [ ] Renomear/atualizar migrações SQL e nomes de arquivo que citam a
      numeração antiga (`2026_07_05_v4_2_agents_s6_s10.sql`,
      `2026_07_31_v4_3_agents_s12_s13.sql`) — fora do escopo desta fase
- [ ] Reconciliação mais ampla (infraestrutura Supabase/APScheduler/ML
      fictícia vs. estrutura real de `SKILL.md`) — ver
      `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, fases seguintes ainda
      não escopadas

---

## Arquivos deste repositório

```
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

- **v5.4.4** (2026-09-08) — **skill real de proposta mudou de lugar de
  novo e foi reaplicada, segunda rodada no mesmo dia**. Horas depois
  da v5.4.2 aplicar a correção em `05-sub-skills/skill-proposta-
  comercial-SKILL.md` (809 bytes), outra sessão Claude (Claude Desktop
  Windows) tentou localizar essa mesma skill e não encontrou o
  caminho, encontrando uma estrutura de pastas totalmente diferente
  (`02-agentes-horizontais/agente-bd`, vazia). Isso disparou, em
  paralelo a esta sessão, um saneamento estrutural real do SharePoint
  (documentado em `09-base-conhecimento/INDICE-CANONICAL.md` v1.1,
  §13), que fundiu o corpo operacional da skill em
  `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.0, a
  partir de um pacote de conteúdo externo **anterior** à correção da
  v5.4.2) e transformou o caminho antigo num ponteiro de
  descontinuação. A correção da v5.4.2 ficou órfã. Reaplicada nesta
  mesma sessão no novo caminho real como **v3.3.1** (16.191 bytes,
  verificado por leitura pós-upload em 2026-09-08T00:48:09Z),
  preservando o corpo operacional completo já consolidado pelo
  saneamento (numeração, tabela de 13 perfis, dados fixos do
  proponente, estrutura de 18 seções + Anexo, variante "Tipo A") e
  reinserindo a segregação Tarifa×Success Fee, a exigibilidade por
  formalização do evento-gatilho e a cláusula de juros de
  mora/multa/correção monetária. Detalhe completo em
  `docs/MODELO-MESTRE-PROPOSTA.md` §3. Achado novo e relevante:
  **o SharePoint real está sendo editado por múltiplas
  sessões/processos em paralelo no mesmo dia** — antes de editar essa
  skill de novo, sempre reler o arquivo primeiro (risco de edição
  concorrente, documentado também em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`).
- **v5.4.3** (2026-09-07) — **fase 1 da reconciliação com o SharePoint
  real: numeração de segmento corrigida**, a pedido do usuário. A
  numeração real (`INDICE-CANONICAL.md`, lido via `SharePoint_Manta`
  MCP) é S1–S11 com Edificações=S6, Portos=S7, Aeroportos=S8,
  Saneamento=S9, Energia=S10, Barragens=S11 — exatamente a numeração
  que este arquivo vinha chamando de "Convenção B" e tratando como
  errada desde a v5.0. A "Convenção A" (S6=Portos…S10=Barragens) que
  este arquivo adotava não tinha lastro real: a auditoria Supabase
  citada para justificá-la nunca foi confirmada como infraestrutura
  real (ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`). `agente-
  oleo-gas` e a "Mineração" (antigos "S12"/"S11") não têm segmento
  real confirmado — o índice canônico não os menciona. Atualizadas as
  seções "Eixo S", "Modelo de composição S.A.D", "Mapa completo de
  agentes", "ROUTING", "RAG", "SharePoint routing rules", "Gaps
  abertos", "Questionário MN" e "Deploy checklist". Não incluído nesta
  fase: renumerar o frontmatter interno dos agentes `.md`, renomear
  migrações SQL, ou reconciliar a infraestrutura Supabase/APScheduler/
  ML fictícia — fases seguintes da reconciliação, ainda não escopadas
  (ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`).
- **v5.4.2** (2026-09-07) — **correção da v5.4.1 + aplicação real na
  skill de produção**. A v5.4.1 (abaixo) partia de uma premissa nunca
  verificada contra o SharePoint real: skill de 18 seções, modo "M6",
  proposta de referência "MNT-2026-COM-1183_D". Com acesso real de
  leitura/escrita ao SharePoint (`SharePoint_Manta` MCP) nesta sessão,
  confirmamos a skill real
  (`04_IA/Manta-Maestro/05-sub-skills/skill-proposta-comercial-SKILL.md`):
  14 seções, modos M1–M5 (sem M6), tabela de 12 níveis, referência real
  Hope PPP MNT-2025-COM-1104 (revisão mais recente de MNT-2026-COM-1183
  encontrada é "_C", não "_D"). A ideia central da v5.4.1 — segregar
  Tarifa × Success Fee, exigibilidade do success fee pela formalização
  do evento-gatilho (economia de custo → aprovação de orçamento;
  conquista → formalização da conquista; cronograma → marco aprovado —
  nunca pela implementação física), e cláusula de multa/juros de
  mora/correção monetária por atraso de pagamento — foi reescrita no
  formato real (resumo compacto ≤1024 caracteres) e **aplicada
  diretamente na skill de produção** (upload verificado, 809 bytes),
  a pedido do usuário. Detalhe em `docs/MODELO-MESTRE-PROPOSTA.md` e
  `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` (addendum original
  marcado como histórico). Reconciliação arquitetural mais ampla
  (segmentos S1–S13 deste repositório vs. S1–S11 reais, "20+
  agentes"/RAG Supabase fictícios vs. estrutura real de `SKILL.md`)
  registrada como gap separado em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, não resolvida nesta
  versão.
- **v5.4.1** (2026-09-01, **premissa não verificada — ver correção na
  v5.4.2**) — análise e recomendação de modelo mestre de proposta
  técnico-comercial (variante "M6", PTC-Infraestrutura/Concessão de
  grande porte), validada contra a proposta "MNT-2026-COM-1183_D" e a
  skill `proposta-comercial` ("A7-bd"). Addendum M6
  (`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`) segregava Tarifa ×
  Success Fee na Seção 12, definia exigibilidade do success fee por
  formalização do evento-gatilho (economia de custo, conquista ou
  cronograma) e acrescentava cláusula de multa/juros de mora/correção
  monetária por atraso de pagamento na Seção 13. Mantido como
  histórico — a lógica das cláusulas em si seguiu válida e orientou a
  v5.4.2, mas a skill real tem estrutura diferente (14 seções, M1–M5).
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
