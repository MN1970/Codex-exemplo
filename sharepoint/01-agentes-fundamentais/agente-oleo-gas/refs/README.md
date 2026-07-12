# refs/ — agente-oleo-gas

Bibliografia mínima. RAG (`ogs:*`) ingere estes documentos. Sub-
prefixos `ogs:u:` (upstream superfície), `ogs:m:` (midstream dutos),
`ogs:r:` (refino/petroquímica), `ogs:t:` (terminal/armazenagem).

## Regulação — Brasil

- **ANP** — Agência Nacional do Petróleo, Gás Natural e Biocombustíveis.
  Marco: **Lei 9.478/1997**.
  - **Resolução ANP 6/2011** — armazenamento de combustíveis
    líquidos derivados de petróleo.
  - **Resolução ANP 41/2017** — atividade de revenda varejista de
    combustível.
  - **Resolução ANP 807/2020** — segurança operacional de
    instalações aquaviárias de movimentação e armazenamento.
  - **Resolução ANP 858/2022** — dutos terrestres para transporte
    (projeto, construção, operação, integridade).
  - **Portaria ANP 32** — bacia de contenção em tancagem.
  - Editais e autorizações para desinvestimento (Refap, Regap, Repar,
    Lubnor, refinarias regionais).
- **IBAMA** (federal), **CETESB** (SP), **INEA** (RJ), **CPRH** (PE) —
  licenciamento ambiental LP → LI → LO. EIA/RIMA + servidão para
  dutos.
- **PBQP-H** — Programa Brasileiro da Qualidade e Produtividade do
  Habitat (construção).
- **CREA / CONFEA** — responsabilidade técnica (ART).
- **CONAMA 001/1986** — EIA/RIMA; **CONAMA 237/1997** — licenciamento.

## Normas técnicas — Brasil

- **NBR 15280** (série) — Duto terrestre para transporte de petróleo,
  produtos e gás.
- **NBR 15417** — Sistemas de armazenagem em tanques atmosféricos.
- **NBR 6118** — Concreto estrutural (fundações pesadas).
- **NBR 6122** — Projeto e execução de fundações.
- **NBR 6123** — Vento em edificações e estruturas (tancagem, pipe-
  rack).
- **NBR IEC 60079** (série) — Atmosferas explosivas.
- **NBR 17505** — Armazenagem de líquidos inflamáveis e combustíveis
  (equivalente brasileiro do NFPA 30).
- **NBR 12712** — Projeto de sistemas de transmissão e distribuição
  de gás combustível (city gate, redes).

## Normas técnicas — Internacional

### API — American Petroleum Institute
- **API 650** — Welded Tanks for Oil Storage (tancagem atmosférica).
- **API 653** — Tank Inspection, Repair, Alteration and
  Reconstruction (tancagem em operação).
- **API 620** — Design and Construction of Large, Welded, Low-
  Pressure Storage Tanks (GLP refrigerado, LNG).
- **API 5L** — Line Pipe (tubos para duto).
- **API 570** — Piping Inspection Code.
- **API 579-1 / ASME FFS-1** — Fitness-For-Service (avaliação de
  defeitos).
- **API RP 14C** — Analysis, Design, Installation, and Testing of
  Safety Systems for Offshore Production Facilities.
- **API RP 500** — Classification of Locations for Electrical
  Installations at Petroleum Facilities Classified as Class I,
  Division 1 and Division 2.
- **API RP 505** — Recommended Practice for Classification of
  Locations for Electrical Installations at Petroleum Facilities
  Classified as Class I, Zone 0, Zone 1, and Zone 2.
- **API 580** — Risk-Based Inspection.
- **API 581** — Risk-Based Inspection Methodology.
- **API 686** — Recommended Practice for Machinery Installation
  and Installation Design.
- **API 2610** — Design, Construction, Operation, Maintenance,
  and Inspection of Terminal & Tank Facilities.
- **API RP 1110** — Pressure Testing of Steel Pipelines for the
  Transportation of Gas, Petroleum Gas, Hazardous Liquids, Highly
  Volatile Liquids, or Carbon Dioxide.

### ANSI / ASME — Piping codes
- **ASME B31.3** — Process Piping (refino, petroquímica).
- **ASME B31.4** — Pipeline Transportation Systems for Liquids and
  Slurries.
- **ASME B31.8** — Gas Transmission and Distribution Piping Systems.
- **ASME VIII** — Boiler & Pressure Vessel Code (vasos de pressão).

### ISO
- **ISO 3183** — Petroleum and natural gas industries — Steel pipe
  for pipeline transportation systems.
- **ISO 14224** — Petroleum, petrochemical and natural gas industries
  — Collection and exchange of reliability and maintenance data
  for equipment (RCM).
- **ISO 15589** — Cathodic protection of pipeline systems.

### NFPA — National Fire Protection Association
- **NFPA 30** — Flammable and Combustible Liquids Code.
- **NFPA 59A** — Standard for the Production, Storage, and Handling
  of Liquefied Natural Gas (LNG).
- **NFPA 11** — Standard for Low-, Medium-, and High-Expansion Foam.

### IEC — International Electrotechnical Commission
- **IEC 60079** (série) — Explosive atmospheres:
  - **60079-10-1** — Classificação de áreas (gás).
  - **60079-14** — Instalações elétricas em áreas classificadas.
  - **60079-17** — Inspeção e manutenção.
- **IEC 61511** — Functional Safety — Safety Instrumented Systems
  for the process industry sector (SIS/SIF/SIL 1-4).
- **IEC 61508** — Functional Safety of Electrical/Electronic/
  Programmable Electronic Safety-related Systems (base do 61511).

### OSHA
- **OSHA 1910.119** — Process Safety Management of Highly Hazardous
  Chemicals (PSM) — 14 elementos, base de HAZOP + LOPA.

## Livros técnicos de referência

- **Bausbacher, E.** — *Process Plant Layout and Piping Design*
  (Prentice Hall) — layout de refinaria, plot plan, pipe-rack.
- **Perry, R. H.; Green, D. W.** — *Perry's Chemical Engineers'
  Handbook* (McGraw-Hill) — referência universal.
- **Peters, M. S.; Timmerhaus, K. D.** — *Plant Design and Economics
  for Chemical Engineers* (McGraw-Hill) — CAPEX/OPEX de plantas.
- **CCPS** (Center for Chemical Process Safety, AIChE) — *Guidelines
  for Hazard Evaluation Procedures*, *Layer of Protection Analysis*.
- **Sherali & Al-Khayyal** — *Piping and Pipeline Engineering*.
- **Nayyar, M. L.** — *Piping Handbook* (McGraw-Hill).
- **Escoe, K.** — *Piping and Pipelines Assessment Guide* (RBI).

## Softwares (referência — Manta não faz processo)

- **PDMS / E3D** (AVEVA), **SmartPlant 3D** (Hexagon) — modelagem 3D
  de planta. Manta apoia review de layout.
- **CAESAR II**, **AutoPIPE**, **ROHR2** — análise de flexibilidade
  de tubulação.
- **HYSYS** (Aspen), **PIPESIM** (Schlumberger) — simulação de
  processo (Manta **não** faz simulação — apoia review).
- **PHAST** (DNV), **FLACS** (Gexcon) — dispersão de nuvem tóxica/
  inflamável (Manta usa e comenta).
- **PLS-CADD** — projeto de duto aéreo (raro em O&G).
- **AutoCAD Plant 3D**, **Bentley OpenPlant** — plantas 2D + iso.

## Casos brasileiros documentados

### Refinarias Petrobras
- **Comperj** (Complexo Petroquímico do Rio de Janeiro, Itaboraí-RJ).
- **Rnest** (Refinaria Abreu e Lima, Ipojuca-PE).
- **Replan** (Paulínia-SP) — maior refinaria BR.
- **Reduc** (Duque de Caxias-RJ).
- **Rlam** (Landulpho Alves, Mataripe-BA) — vendida à Acelen.
- **Regap** (Betim-MG), **Repar** (Araucária-PR), **Refap** (Canoas-
  RS), **Recap** (Capuava-SP), **Rpbc** (Cubatão-SP), **Lubnor**
  (Fortaleza-CE).

### Petroquímica
- **Braskem** — polos de Duque de Caxias (RJ), Camaçari (BA),
  Triunfo (RS), Mauá (SP).

### Gasodutos
- **GASBOL** — Bolívia-Brasil, 3.150 km, TBG.
- **Rota 3** — pré-sal (Cabiúnas → Comperj), 355 km.
- **Rota 4** — pré-sal, em projeto.
- **GASENE** — Cabiúnas (RJ) → Catu (BA), 1.400 km.
- **Gasyrg** — Yacuiba (BOL) → Rio Grande (ARG), ampliação.

### Terminais aquaviários
- **TA-Cabiúnas** (Macaé-RJ) — recebimento gás/óleo pré-sal.
- **TA-Guararema** (SP) — Osbra/Osrio.
- **TA-São Sebastião** (SP).
- **TA-Barra do Riacho** (ES).
- **TA-São Francisco do Sul** (SC).

### Distribuidoras
- **Ultra** (Ultragaz, Ipiranga), **Raízen** (JV Shell + Cosan),
  **Vibra** (ex-BR Distribuidora), **Comgás** (distribuidora de gás
  natural SP).

## Convenções internas Manta

- Composições unitárias — tanque m³ × Ø, duto km × polegada × classe
  (150/300/600/900), pipe-rack ton, fundação pesada m³ concreto +
  taxa de armadura.
- Modelo financeiro CAPEX × EBITDA × VPL/TIR — R$/bpd (refino),
  R$/m³ (tancagem), R$/MMm³/d (compressão), R$/km-polegada (duto).
- Benchmarks Petrobras + Braskem + desinvestimentos ANP.
- Base histórica de projetos Manta em O&G (RAG `ogs:cases:*`).
