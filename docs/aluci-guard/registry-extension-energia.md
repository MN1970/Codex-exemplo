# Extensão do registry aluci-guard — Energia (Manta 03-S9)

Fonte: `/home/user/Codex-exemplo/sharepoint/01-agentes-fundamentais/agente-energia/SKILL.md`
(agente-energia, Manta 03-S9, v1.0.0, 2026-07-05)

## Compatível com schema atual (normas_abnt.py / leis_federais.py)

Todas as ocorrências abaixo são normas ABNT NBR citadas no SKILL.md
(seções "V2 — Inteligência Setorial / axes/01-normas.md" e "4. KNOWLEDGE
ENGINE (RAG) / Fontes iniciais"). Nenhuma lei federal brasileira (com
número, tipo "Lei nº X/AAAA") é citada no arquivo.

- `normas_abnt.py`:
  - código: `NBR 5422`
    descrição: "Projeto de linhas aéreas de transmissão de energia
    elétrica (LT) — citada como norma de traçado/dimensionamento de LT"
    status: a confirmar
  - código: `NBR 6118`
    descrição: "Norma de fundações/estruturas de concreto citada para
    fundação de torre e obras civis de SE"
    status: a confirmar
  - código: `NBR 6122`
    descrição: "Norma de projeto e execução de fundações, citada junto
    com NBR 6118 para fundação de torre"
    status: a confirmar
  - código: `NBR 6123`
    descrição: "Norma citada como fonte inicial do Knowledge Engine
    (RAG) do agente-energia, sem detalhamento adicional no SKILL.md"
    status: a confirmar

- `leis_federais.py`: nenhuma entrada — não há citação de lei federal
  com número no SKILL.md.

## Fora do schema atual (requer nova categoria de registry)

Referências a agências reguladoras, operadoras de sistema, normas
técnicas internacionais e entidades setoriais — não cabem em
`normas_abnt.py` (ABNT NBR) nem em `leis_federais.py` (lei federal
brasileira). Requer categoria nova de registry (ex.:
`normas_internacionais.py` ou `normas_setoriais.py`).

- `IEEE Std 738` — "ampacidade" de condutores nus (norma internacional
  IEEE), citada em axes/01-normas.md e na seção Knowledge Engine.
- `IEEE Std 80` (também referida como "IEEE 738/80" e "IEEE 80: tensão
  passo, toque") — norma internacional de aterramento/malha de
  aterramento de subestação, citada em axes/01-normas.md, na seção
  Knowledge Engine e em D08-malha-aterramento.md.
- `IEC 60826` — norma internacional de critérios de projeto estrutural
  de linhas de transmissão, citada em axes/01-normas.md e na seção
  Knowledge Engine.
- `IEC 61850` — norma internacional de redes de comunicação em
  subestações (SE digital / SCADA), citada em axes/05-tecnologia.md e
  em D10-sistema-scada.md.
- `ANEEL (REN)` — Agência Nacional de Energia Elétrica e suas
  Resoluções Normativas (REN vigentes); citada em axes/02-regulatorio.md,
  na seção Knowledge Engine ("ANEEL editais de leilão (2015-2026) + REN
  vigentes") e na regra de aluci-guard ("REN ANEEL correta?"). Nenhum
  número específico de REN é citado no SKILL.md.
- `EPE (R1-R5 / PDE)` — Empresa de Pesquisa Energética; relatórios de
  estudo R1 a R5 e Plano Decenal de Expansão (PDE), citados em
  axes/03-mercado.md e na seção Knowledge Engine ("EPE PDE + estudos
  R1-R5 públicos").
- `ONS (Procedimentos de Rede)` — Operador Nacional do Sistema Elétrico
  e seus Procedimentos de Rede, citados em axes/02-regulatorio.md e na
  seção Knowledge Engine ("ONS Procedimentos de Rede + relatórios de
  operação").
- `CCEE (ACR × ACL)` — Câmara de Comercialização de Energia Elétrica,
  citada em axes/02-regulatorio.md.
- `CIGRÉ (technical brochures)` — Conseil International des Grands
  Réseaux Électriques; citada em axes/06-academia.md e na seção
  Knowledge Engine ("CIGRÉ technical brochures (transmissão)").

## Observações

- Referências mencionadas no SKILL.md que **não** são normas/leis/códigos
  técnicos e por isso não foram classificadas em nenhuma das duas listas
  acima: `State Grid` (empresa, citada como referência de projeto HVDC
  Xingu-Estreito/Xingu-Terminal Rio), `ANATEM`/`ANAREDE`/`PSSE`
  (softwares de estudo elétrico), `CPFL R&D` e `IEEE PES` (entidades/
  programas institucionais citados em axes/06-academia.md, sem norma
  numerada associada), e `CREA-A` (registro profissional, não é norma
  técnica).
- Nenhuma entrada foi inventada: todas as referências acima aparecem
  textualmente no SKILL.md do agente-energia. Não foi feita nenhuma
  verificação externa de vigência ou existência real das normas listadas
  — o status "a confirmar" reflete apenas a ausência de acesso à base
  oficial ABNT/Planalto nesta etapa.
- Antes de popular `normas_abnt.py` com as 4 NBRs acima, recomenda-se
  confirmar o status de vigência de cada uma junto à ABNT, já que o
  SKILL.md não informa ano de edição/revisão.
