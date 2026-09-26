# Histórico de versões do Manta Maestro

> Extraído do `CLAUDE.md` na v5.5.0 (2026-09-26), sem alteração de
> conteúdo. O `CLAUDE.md` mantém só a entrada da versão atual.

## Notas de consolidação (cabeçalho do CLAUDE.md até a v5.4.7)

Versão: **v5.4.7** (2026-09-11) — **reconciliação de conhecimento por
agente/segmento/disciplina**. Releitura ao vivo do `INDICE-CANONICAL.md`
real (v1.1) mostrou que o eixo S vai até **S14** (Túneis, Mineração,
Óleo e Gás), o eixo D até **D22** e o eixo A até **A11** — mais do que
este arquivo assumia. Uma primeira leitura interpretou os itens
marcados "a confirmar" nesses eixos como "vazios" e chegou a redigir 6
briefs de conhecimento novos para eles; uma auditoria seguinte, lendo
o SharePoint real pasta a pasta, encontrou o oposto — quase todos já
têm conteúdo maduro e versionado em produção (`agente-tuneis`,
`agente-mineracao`, `agente-oleo-gas`, `agente-S5-imobiliario`, skill
`fiscalizacao-obras` para A11, entre outros). Os 6 briefs foram
descartados. O achado que sobrou de valor real: um campo de código de
segmento legado (`manta_code`) nos 3 segmentos mais novos que colide
com o código real de outro segmento — risco de misroteamento em
produção, se o routing real ainda usar esse campo. Ver
`docs/PLANEJAMENTO-MANTA-MAESTRO.md` e "GAPS ABERTOS" para o detalhe
completo. Nada foi escrito na fonte real (SharePoint) nesta sessão.

Consolida v5.4.6 (2026-09-10) — **diretriz de posicionamento**: foco
na maturidade profissional da equipe Manta, com IA como apoio/
multiplicador (não substituição), para propostas do segmento
Infraestrutura. Registrada em `docs/MODELO-MESTRE-PROPOSTA.md`
("Diretriz de posicionamento (2026-09-10)"). É orientação de conteúdo
para propostas futuras — não altera nem alega nada sobre a skill de
produção.

Consolida v5.4.5 (2026-09-10) — **recorrência confirmada da
fabricação na skill real de proposta**. Investigação read-only via
`SharePoint_Manta` MCP confirmou que a seção "Variante Tipo A /
Concessão de Infraestrutura de Grande Porte", hoje viva em
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.5),
reproduz quase palavra-por-palavra o addendum fabricado deste
repositório (`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`), incluindo a
referência a uma revisão de proposta inexistente
(`MNT-2026-COM-1183_D` — só `_C_3` é encontrável). A própria fonte
canônica (`INDICE-CANONICAL.md` §13) admite que esse conteúdo "antes só
existia num pacote de skill fora do SharePoint, nunca escrito na
árvore" — ou seja, a correção de premissa da v5.4.2/v5.4.3 não impediu
uma recorrência por um caminho diferente (fusão de pacote externo no
saneamento estrutural de 2026-09-07, sem gate humano de verificação de
fonte primária). Detalhe completo, incluindo a comparação literal, em
`docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` (seção "Recorrência
confirmada — Variante Tipo A (2026-09-10)"). **Nenhuma escrita foi
feita na skill de produção** — recomendação registrada para o MN
revisar e corrigir diretamente.

Consolida v5.4.4 (2026-09-08) — **a skill real de proposta mudou de
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
>
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

## Histórico de versões

- **v5.4.7** (2026-09-11) — reconciliação de conhecimento por
  agente/segmento/disciplina (`docs/PLANEJAMENTO-MANTA-MAESTRO.md`).
  Re-verificação ao vivo do `INDICE-CANONICAL.md` real (v1.1) corrige
  leitura anterior: o eixo S vai até **S14** (não S11), o eixo D até
  **D22** (não D20) e o eixo A até **A11** (não A10). Uma primeira
  passada tratou os itens "a confirmar" desses eixos como vazios e
  redigiu 6 briefs de conhecimento novos (S12-Túneis, S13-Mineração,
  S14-Óleo e Gás, D21-Topografia/Geodésia, D22-Túneis,
  A11-Fiscalização + F9/F10); uma segunda auditoria, lendo o SharePoint
  real pasta a pasta, encontrou conteúdo maduro já em produção para
  quase todos eles (`agente-tuneis`, `agente-mineracao`,
  `agente-oleo-gas`, skill `fiscalizacao-obras`, `agente-S5-imobiliario`
  — este último nem estava no escopo original, achado incidental) — os
  6 briefs foram **descartados** por serem redundantes ou, no caso de
  F10, diretamente incorretos. Achado real que sobrou: um campo
  `manta_code` legado nos 3 segmentos mais novos colide com o código
  real de outro segmento (risco de misroteamento se o routing de
  produção ainda usar esse campo — ver "GAPS ABERTOS"). Consolida
  também a decisão já tomada de descartar a proposta de agente "Manta
  17/geotecnia" e uma correção ao guia de D03 (S12 não depende de D03
  como se pensou inicialmente). **Nada escrito na fonte real
  (SharePoint)** nesta sessão.
- **v5.4.6** (2026-09-10) — diretriz de posicionamento (MN): propostas
  de Infraestrutura devem destacar a maturidade profissional da equipe
  Manta primeiro, com a IA da Manta posicionada como apoio/multiplicador
  de produtividade — nunca como substituição da experiência técnica.
  Registrada em `docs/MODELO-MESTRE-PROPOSTA.md`; não altera a skill de
  produção.
- **v5.4.5** (2026-09-10) — investigação read-only confirmou
  recorrência da fabricação da skill `proposta-comercial`: a variante
  "Tipo A / Infraestrutura de Grande Porte" viva em produção (v3.3.5)
  reproduz o addendum fabricado deste repositório quase
  palavra-por-palavra, citando a mesma revisão inexistente
  `MNT-2026-COM-1183_D`. Documentado em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` e `docs/MODELO-MESTRE-PROPOSTA.md`.
  Nenhuma alteração feita na skill real — recomendação registrada para
  gate humano (MN).
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
