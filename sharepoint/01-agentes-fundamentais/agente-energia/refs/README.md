# refs/ — agente-energia

Bibliografia mínima. RAG (`ene:*`) ingere estes documentos. Sub-prefixos
`ene:t:` (transmissão), `ene:d:` (distribuição), `ene:g:` (geração).

## Regulação — Brasil

- **ANEEL** — Agência Nacional de Energia Elétrica.
  - REN 583/2013 (procedimentos de rede)
  - REN 1000/2021 (procedimentos de distribuição — PRODIST)
  - REN 673/2015 (concessões de transmissão)
  - Editais de leilão de transmissão (2015-2026, base histórica de
    RAP × MVA·km).
- **ONS** — Operador Nacional do Sistema.
  - Procedimentos de Rede (submódulos 3.3, 3.6, 3.7, etc.).
  - Relatórios de operação anuais.
  - Diagramas do SIN.
- **EPE** — Empresa de Pesquisa Energética.
  - **PDE** — Plano Decenal de Expansão de Energia (anual).
  - **R1** — Estudos de Sistema.
  - **R2** — Projeto Básico Ambiental.
  - **R3** — Projeto Básico Eletromecânico.
  - **R4** — Relatório ANEEL para autorizar leilão.
  - **R5** — Edital de leilão.
- **CCEE** — Câmara de Comercialização de Energia Elétrica.
  - ACR (Ambiente Regulado) × ACL (Ambiente Livre).
  - MRE (Mecanismo de Realocação de Energia).

## Normas técnicas — BR

- **NBR 5422** — Projeto de linhas aéreas de transmissão (obrigatória
  BR, cálculo de faixa de servidão, distâncias mínimas).
- **NBR 6118** — Projeto de estruturas de concreto (fundações torre).
- **NBR 6122** — Projeto e execução de fundações.
- **NBR 6123** — Vento em edificações e estruturas (cargas em torres).
- **NBR 15992** — Cabos condutores nus.

## Normas técnicas — Internacional

- **IEEE Std 738** — Standard for Calculating the Current-Temperature
  Relationship of Bare Overhead Conductors (ampacidade).
- **IEEE Std 80** — Guide for Safety in AC Substation Grounding
  (malha de aterramento).
- **IEEE Std 81** — Guide for Measuring Earth Resistivity, Ground
  Impedance.
- **IEEE Std 605** — Guide for Design of Substation Rigid-Bus Structures.
- **IEC 60826** — Design criteria of overhead transmission lines.
- **IEC 60815** — Selection and dimensioning of high-voltage
  insulators (contaminação I-IV).
- **IEC 61850** — Communication networks and systems for power utility
  automation (digital substation).

## Software técnico

- **ANAREDE** — fluxo de potência (CEPEL).
- **ANATEM** — estabilidade eletromecânica (CEPEL).
- **ANAFAS** — análise de faltas (curto-circuito) (CEPEL).
- **PSSE** (Siemens) — estudos de sistema.
- **DIgSILENT PowerFactory** — estudos de sistema (comercial).
- **PLS-CADD** — projeto e otimização de LT (Power Line Systems).
- **CDEGS** — malha de aterramento (SES).

## Boletins CIGRÉ (referência internacional)

- SC B2 (Overhead Lines) — projeto e otimização.
- SC A3 (High Voltage Equipment).
- SC C4 (System Technical Performance).

## Editais e leilões

- Editais ANEEL de transmissão 2015-2026 (base para benchmark RAP).
- Projetos referenciais State Grid — HVDC Xingu-Estreito, Xingu-Terminal
  Rio (elos HVDC).
- Transmissoras líderes BR: ISA CTEEP, Alupar, Taesa, State Grid Brazil,
  Furnas.

## Convenções internas Manta

- Composições unitárias de torre + fundação + condutor + isolador
  (adaptado do SICRO + BID/PPP references).
- Modelo financeiro RAP × CAPEX (VPL, TIR, EBITDA) por tensão × km.
- Base histórica de projetos Manta em energia (RAG `ene:cases:*`).
