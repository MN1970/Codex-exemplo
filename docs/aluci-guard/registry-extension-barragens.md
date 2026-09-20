# Extensão do registry aluci-guard — Barragens (Manta 03-S10)

Fonte: `/home/user/Codex-exemplo/sharepoint/01-agentes-fundamentais/agente-barragens/SKILL.md`
(agente-barragens v1.0.0, 2026-07-05).

## Compatível com schema atual (normas_abnt.py / leis_federais.py)

- **Lei 12.334/2010** — descrição no SKILL.md: lei-base da segurança de
  barragens no Brasil, citada junto com a Lei 14.066/2020 como marco
  "pós-Brumadinho" (Seção 4, Fontes iniciais; também referida pela sigla
  PNSB — Política Nacional de Segurança de Barragens — na frontmatter).
  → entrada para `leis_federais.py`. Status a confirmar.

- **Lei 14.066/2020** — descrição no SKILL.md: lei citada em conjunto com
  a Lei 12.334/2010 como alteração legislativa pós-Brumadinho (Seção 4,
  Fontes iniciais). → entrada para `leis_federais.py`. Status a confirmar.

- **NBR 13028** — descrição no SKILL.md: norma ABNT aplicável a barragens
  de rejeitos, citada em `axes/01-normas.md` e na Seção 4 (Fontes
  iniciais) e na Regra 6 (`aluci-guard` — checar se norma existe).
  → entrada para `normas_abnt.py`. Status a confirmar.

- **NBR 8681** — descrição no SKILL.md: norma ABNT referente a "ações"
  (ações e segurança nas estruturas), citada em `axes/01-normas.md` e na
  Seção 4 (Fontes iniciais). → entrada para `normas_abnt.py`. Status a
  confirmar.

- **NBR 6122** — descrição no SKILL.md: norma ABNT de fundações, citada
  como "ABNT 6122" em `axes/01-normas.md` e como "NBR 6122 (fundações)"
  na Seção 4 (Fontes iniciais). → entrada para `normas_abnt.py`. Status a
  confirmar.

## Fora do schema atual (requer nova categoria de registry)

- **ICOLD Bulletin 194** — citado duas vezes com descrições distintas:
  "194 rejeitos filtrados" (Seção 3, V2/axes/06-academia.md) e "194 seg."
  [segurança] (Seção 4, Fontes iniciais) — possível inconsistência interna
  do próprio SKILL.md quanto ao tema do boletim 194. Requer categoria
  nova de registry (ex.: `normas_internacionais.py`).

- **ICOLD Bulletin 164** — descrito como referente a CFRD (barragens de
  enrocamento com face de concreto), citado na Seção 3 (V2/axes/06) e na
  Seção 4 (Fontes iniciais). Requer categoria nova de registry (ex.:
  `normas_internacionais.py`).

- **ICOLD Bulletin 72** — descrito como referente a "seleção de
  materiais", citado na Seção 3 (V2/axes/06-academia.md). Requer
  categoria nova de registry (ex.: `normas_internacionais.py`).

- **CBDB (Comitê Brasileiro de Barragens)** — citado como fonte de
  "cadernos técnicos + guias" (Seção 2/V2, Seção 4 Fontes iniciais,
  Seção 5 aba "Inteligência Setorial"), sem número de documento
  específico. Requer categoria nova de registry (ex.:
  `normas_setoriais.py`).

- **ANM Res. 95/2022** — descrita no SKILL.md como norma da Agência
  Nacional de Mineração regulando descaracterização e inspeções de
  barragens de mineração (Seção 3/axes/02-regulatorio.md, Seção 4 Fontes
  iniciais, Regra especial 12). É uma resolução de agência reguladora,
  não uma lei federal numerada nem norma ABNT — requer categoria nova de
  registry (ex.: `normas_setoriais.py`).

- **SNISB (ANA)** — Sistema Nacional de Informações sobre Segurança de
  Barragens, descrito no SKILL.md como "banco nacional de barragens" da
  ANA (Seção 3/axes/02-regulatorio.md, Seção 4 Fontes iniciais, Q4 do
  intake, módulo `bar-doc-sigbm.md`). É um sistema/banco de dados de
  agência, não uma norma ou lei — requer categoria nova de registry (ex.:
  `normas_setoriais.py`).

- **SIGBM (ANM)** — Sistema Integrado de Gestão de Barragens de
  Mineração, citado como fonte de relatório no Q4 do intake e no módulo
  `bar-doc-sigbm.md` ("extração de relatório SIGBM/SNISB"). Sistema de
  agência reguladora, não norma/lei — requer categoria nova de registry
  (ex.: `normas_setoriais.py`).

- **USACE/FEMA (HHP framework)** — citado na Seção 4 (Fontes iniciais)
  como referência de framework de agências norte-americanas (US Army
  Corps of Engineers / Federal Emergency Management Agency). Requer
  categoria nova de registry (ex.: `normas_internacionais.py`).

## Observações

- **PNSB** (Política Nacional de Segurança de Barragens) aparece na
  frontmatter do SKILL.md como sigla de gatilho de ativação do agente,
  mas não é uma referência normativa distinta — corresponde à política
  instituída pela Lei 12.334/2010, já listada acima. Não foi tratada como
  entrada separada para evitar duplicação.
- Os "Relatórios oficiais Fundão (2015) e Brumadinho (2019)" citados na
  Seção 4 (Fontes iniciais) são relatórios de investigação de acidentes,
  não normas/leis/códigos verificáveis por um registry de aluci-guard —
  não foram incluídos em nenhuma das duas listas por não se
  enquadrarem como referência normativa/legal/técnica no sentido do
  registry (não têm "código" nem "status vigente/revogada").
  Software citado no SKILL.md (PLAXIS, GeoStudio, FLAC, HEC-RAS,
  DAMBRK, Flow-3D) e métodos de cálculo (Bishop, Morgenstern, Spencer)
  também foram excluídos pelo mesmo motivo.
- Nenhuma norma foi verificada quanto à existência real ou vigência —
  todas as entradas foram extraídas literalmente do texto do SKILL.md,
  conforme escopo desta tarefa.
