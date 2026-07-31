# Eixo D — Disciplinas Técnicas (D01–D20)

Registro formal do **Eixo D (Disciplinas)** do sistema Manta Maestro,
complementar aos Eixos 1 (Horizontais/Agentes A1-A10), 2 (Verticais por
segmento S1-S11) e 3 (Ciclo de vida, 8 fases) descritos no `CLAUDE.md`
master.

Enquanto o Eixo 2 organiza o conhecimento por **segmento de infraestrutura**
(rodovias, portos, energia etc.), o Eixo D organiza o conhecimento por
**disciplina técnica transversal** — a competência de engenharia ou gestão
que é aplicada dentro de qualquer segmento, em intensidade variável.

Versão: **v1.0** (2026-07-31)
Autor: Manta 16 — arquiteto-ia (via Sonnet 5)
Status: 🆕 Documento novo — não substitui routing do Maestro (`CLAUDE.md`
Eixo 2), apenas complementa com a camada disciplinar.

---

## Convenção de aplicabilidade

Para cada disciplina, a aplicabilidade por segmento usa a escala:

- **●** Alta — disciplina crítica/estruturante no segmento
- **◐** Média — disciplina relevante, mas não determinante
- **○** Baixa/pontual — presente ocasionalmente ou em fases específicas
- **—** Não aplicável / marginal

Segmentos (Eixo 2, S1–S11):
`S1` Rodovias · `S2` OAE (pontes/viadutos) · `S3` Ferrovia · `S4` Metrô ·
`S5` Túneis · `S6` Edificações · `S7` Portos · `S8` Aeroportos ·
`S9` Saneamento · `S10` Energia · `S11` Barragens

---

## Índice

D01 Hidráulica · D02 Estrutural · D03 Geotecnia · D04 Pavimentação ·
D05 Elétrica · D06 Ambiental · D07 Cálculos Econômicos · D08 Planejamento ·
D09 Jurídico · D10 Comercial · D11 MEP · D12 HVAC · D13 Acústica ·
D14 Acessibilidade · D15 BIM · D16 Paisagismo · D17 TI/Telecom ·
D18 Comunicação · D19 RH · D20 Qualidade

---

## D01 — Hidráulica

Dimensionamento de sistemas de adução, redes pressurizadas e transientes
hidráulicos (golpe de aríete), com modelagem em regime permanente e
transitório usando Hazen-Williams/Darcy-Weisbach.

**Aplicabilidade:** S9 ● · S11 ● · S10 ◐ · S7 ◐ · S1 ◐ (drenagem) · S4 ◐
(rebaixamento de lençol) · S2 ○ · S3 ○ · S5 ○ · S6 ○ · S8 ○

**Normas-chave:** NBR 12211/12213/12214/12215/12218 (SAA/adutoras/EEE),
NBR 5626 (instalações prediais), Lei 14.026/2020 (marco legal saneamento)

**Ferramentas:** EPANET, Bentley WaterGEMS/HAMMER, AutoCAD Civil 3D
(SSA), planilhas de golpe de aríete (Allievi)

---

## D02 — Estrutural

Concepção e verificação estrutural em concreto armado/protendido e aço,
incluindo fundações profundas e rasas, sob ações estáticas e dinâmicas.

**Aplicabilidade:** S2 ● · S6 ● · S11 ● · S4 ◐ · S3 ◐ · S7 ◐ · S8 ◐ ·
S5 ◐ · S1 ○ · S9 ○ · S10 ○

**Normas-chave:** NBR 6118 (concreto), NBR 8800 (aço), NBR 6122
(fundações), NBR 9062 (pré-moldados), NBR 7187 (pontes de concreto)

**Ferramentas:** TQS, Eberick, SAP2000, ETABS, Autodesk Robot Structural
Analysis, CSiBridge

---

## D03 — Geotecnia

Investigação de subsolo (sondagens SPT, CPT), análise de estabilidade de
taludes e encostas, e quantificação de risco geotécnico associado.

**Aplicabilidade:** S1 ● · S3 ● · S11 ● · S2 ◐ · S4 ◐ · S7 ◐ · S10 ◐ ·
S5 ● · S6 ○ · S8 ○ · S9 ○

**Normas-chave:** NBR 6484 (SPT), NBR 8036 (sondagens para fundações),
NBR 11682 (estabilidade de encostas), Lei 12.334/2010 (PNSB —
barragens)

**Ferramentas:** Rocscience Slide2/Slide3, GeoStudio (SLOPE/W, SEEP/W),
Plaxis 2D/3D

---

## D04 — Pavimentação

Dimensionamento e execução de estruturas de pavimento (CBUQ, BGS,
base/sub-base) e terraplenagem associada, seguindo metodologia SICRO/DNIT.

**Aplicabilidade:** S1 ● · S8 ● · S7 ◐ · S3 ◐ · S6 ◐ (pátios/vias
internas) · S4 ○ · S2 ○ · S9 ○ · S5 ○ · S10 — · S11 —

**Normas-chave:** DNIT 031/ES (pavimentação flexível), método SICRO,
NBR 7207 (classificação de pavimentos), normas ANAC/ICAO Annex 14
(pavimento de pista)

**Ferramentas:** planilhas SICRO/SINAPI, Civil 3D (corredor/terraplenagem),
dosagem Marshall/Superpave, AASHTOWare Pavement ME

---

## D05 — Elétrica

Projetos de instalações elétricas de alta e baixa tensão, sistemas de
proteção, seletividade e aterramento/SPDA.

**Aplicabilidade:** S10 ● · S4 ● · S11 ● · S9 ◐ · S8 ◐ · S6 ◐ · S7 ◐ ·
S1 ○ · S2 ○ · S3 ○ · S5 ○

**Normas-chave:** NBR 5410 (BT), NBR 14039 (MT), NBR 5419 (SPDA), IEC
61850 (automação de subestações)

**Ferramentas:** ETAP, DIgSILENT PowerFactory, AutoCAD Electrical, PSS/E

---

## D06 — Ambiental

Estudos de impacto ambiental (EIA/RIMA), planos de mitigação e
compensação, e gestão de biodiversidade/áreas sensíveis ao longo do
licenciamento.

**Aplicabilidade:** S11 ● · S9 ● · S10 ● · S1 ● · S7 ◐ · S3 ◐ · S8 ◐ ·
S2 ◐ · S4 ◐ · S6 ○ · S5 ◐

**Normas-chave:** Resoluções CONAMA 001/1986 e 237/1997, Lei 6.938/1981
(PNMA), Lei 9.985/2000 (SNUC)

**Ferramentas:** QGIS, ArcGIS, plataformas de licenciamento ambiental
(IBAMA/órgãos estaduais), modelagem de dispersão/ruído

---

## D07 — Cálculos Econômicos

Avaliação de viabilidade econômico-financeira via VPL, TIR, payback e
análise de sensibilidade/Monte Carlo, subsidiando EVTE e decisões de
investimento.

**Aplicabilidade:** transversal a todos os segmentos na fase de
EVTE/licitação — S10 ● (leilões RAP) · S7 ● · S8 ● · S9 ● (PPP) · S1 ◐ ·
S2 ◐ · S3 ◐ · S4 ◐ · S11 ◐ · S6 ◐ · S5 ○

**Normas-chave:** Manual de EVTE do BNDES, metodologia TIR-BNDES, IN
05/EPE (estudos de transmissão)

**Ferramentas:** Excel + @Risk/Crystal Ball, Python (numpy-financial),
modelos de fluxo de caixa descontado proprietários Manta

---

## D08 — Planejamento

Elaboração e controle de cronograma físico-financeiro, alocação de
recursos, caminho crítico e gestão de riscos de prazo.

**Aplicabilidade:** transversal — alta em obras complexas: S2 ● · S4 ● ·
S11 ● · S1 ◐ · S3 ◐ · S7 ◐ · S8 ◐ · S9 ◐ · S10 ◐ · S6 ◐ · S5 ●

**Normas-chave:** PMBOK (PMI), NBR ISO 21500 (gestão de projetos), EVM
(Earned Value Management)

**Ferramentas:** Primavera P6, MS Project, Power BI (dashboards de
S-curve)

---

## D09 — Jurídico

Estruturação e revisão de contratos, editais de licitação, compliance
regulatório e mecanismos de resolução de conflitos (mediação, arbitragem).

**Aplicabilidade:** transversal — alta em processos competitivos: S7 ● ·
S8 ● · S10 ● · S9 ◐ · S1 ◐ · S2 ◐ · S3 ◐ · S4 ◐ · S11 ◐ · S6 ○ · S5 ○

**Normas-chave:** Lei 14.133/2021 (licitações), Lei 8.987/1995
(concessões), Lei 12.462/2011 (RDC), Lei de Arbitragem 9.307/1996

**Ferramentas:** plataformas de gestão contratual, repositórios de
compliance, ferramentas de e-discovery para claims

---

## D10 — Comercial

Precificação de propostas, elaboração de submissões competitivas,
negociação e inteligência de mercado (business development).

**Aplicabilidade:** transversal a todos os segmentos na fase de captação
— intensidade equivalente em S1–S11, variando com o volume de
oportunidades ativas em cada segmento no momento

**Normas-chave:** não normativo por natureza; segue diretrizes internas
de pricing e políticas setoriais de cada regulador (ANTT, ANEEL, ANTAQ,
ANAC)

**Ferramentas:** CRM interno, bancos de preços SICRO/SINAPI, modelos de
proposta técnica/comercial Manta

---

## D11 — MEP

Coordenação integrada de sistemas mecânicos, elétricos e hidrossanitários
(mechanical/electrical/plumbing), evitando interferências entre
disciplinas.

**Aplicabilidade:** S6 ● · S8 ● · S4 ◐ · S7 ◐ · S9 ○ · S1 — · S2 ○ ·
S3 — · S5 ○ · S10 ○ · S11 ○

**Normas-chave:** NBR 16401 (AVAC), NBR 5626 (hidrossanitário), NBR 5410
(elétrica predial)

**Ferramentas:** Revit MEP, AutoCAD MEP, Navisworks (clash detection)

---

## D12 — HVAC

Projeto de ventilação, climatização e conforto térmico, incluindo
ventilação forçada em ambientes confinados (túneis, estações).

**Aplicabilidade:** S6 ● · S8 ● · S4 ● (ventilação de túnel/estação) ·
S7 ◐ · S5 ● · S9 ○ · S1 — · S2 — · S3 ○ · S10 ○ · S11 ○

**Normas-chave:** NBR 16401 (instalações de ar-condicionado), ASHRAE
62.1 (qualidade do ar interior), NFPA 130 (ventilação de metrô/túnel)

**Ferramentas:** Revit MEP, simulação CFD (Ansys Fluent), Carrier HAP

---

## D13 — Acústica

Projeto de isolamento e desempenho acústico, e mitigação de ruído em
infraestrutura linear e edificações.

**Aplicabilidade:** S6 ● · S4 ● · S8 ● · S1 ◐ (barreiras acústicas) ·
S3 ◐ · S7 ○ · S2 ○ · S9 — · S10 ○ · S11 — · S5 ◐

**Normas-chave:** NBR 10151 (avaliação de ruído), NBR 15575 (desempenho
de edificações), NBR 10152 (níveis de ruído para conforto)

**Ferramentas:** CadnaA, Odeon, medidores de nível de pressão sonora
(NPS) e software de mapa de ruído

---

## D14 — Acessibilidade

Aplicação de critérios de desenho universal e inclusão em edificações,
terminais e estações, garantindo rotas acessíveis.

**Aplicabilidade:** S6 ● · S8 ● · S4 ● (estações) · S7 ◐ · S9 ○ · S1 ○
(travessias) · S2 ○ · S3 ○ · S5 ○ · S10 — · S11 —

**Normas-chave:** NBR 9050 (acessibilidade), Lei Brasileira de Inclusão
13.146/2015, NBR 16537 (sinalização tátil)

**Ferramentas:** checklists NBR 9050, clash detection BIM com parâmetros
de acessibilidade, maquetes de rota acessível

---

## D15 — BIM

Modelagem tridimensional, coordenação multidisciplinar, extração de
quantitativos e análises (4D/5D) sobre modelo federado.

**Aplicabilidade:** S2 ● · S4 ● · S6 ● · S11 ● · S1 ◐ · S3 ◐ · S7 ◐ ·
S8 ◐ · S5 ● · S9 ○ · S10 ○

**Normas-chave:** ISO 19650 / NBR ISO 19650 (gestão da informação), BIM
Decreto Federal 10.306/2020 (obras públicas)

**Ferramentas:** Autodesk Revit, Civil 3D, Navisworks, BIM 360/ACC,
Solibri

---

## D16 — Paisagismo

Design de áreas verdes, especificação vegetal, integração com drenagem
pluvial superficial e plano de manutenção paisagística.

**Aplicabilidade:** S6 ● · S1 ◐ (compensação/canteiro central) · S7 ○
(áreas de apoio) · S9 ○ · S11 ○ (recuperação de APP) · S2 — · S3 — ·
S4 ○ · S5 — · S8 ○ · S10 —

**Normas-chave:** NBR 16636 (arborização urbana), manuais de
recuperação de Área de Preservação Permanente (APP)

**Ferramentas:** AutoCAD Landscape, QGIS (análise de cobertura vegetal),
softwares de irrigação

---

## D17 — TI/Telecom

Projeto de redes de dados, cabeamento estruturado, sistemas SCADA e
cibersegurança de infraestrutura crítica.

**Aplicabilidade:** S4 ● (SCADA/CFTV) · S10 ● (automação de
subestações) · S8 ● · S7 ◐ · S9 ◐ · S11 ◐ · S6 ◐ · S1 ○ · S2 ○ ·
S3 ○ · S5 ○

**Normas-chave:** NBR 14565 (cabeamento estruturado), ISO/IEC 27001
(segurança da informação), IEC 62443 (cibersegurança industrial)

**Ferramentas:** plataformas SCADA (proprietárias por concessionária),
switches gerenciáveis, firewalls de rede OT/IT

---

## D18 — Comunicação

Gestão de engajamento de stakeholders, planos de comunicação social e
reporting executivo, especialmente relevante em projetos com forte
exposição pública.

**Aplicabilidade:** S11 ● · S9 ● · S10 ● (linhas/faixa de servidão) ·
S1 ◐ · S7 ◐ · S8 ◐ · S3 ◐ · S2 ○ · S4 ○ · S6 ○ · S5 ○

**Normas-chave:** exigências de Plano de Comunicação Social (PCS) em
licenciamento ambiental, requisitos de transparência em concessões
(Lei 8.987/1995)

**Ferramentas:** relatórios executivos padronizados Manta, canais
institucionais, plataformas de gestão de partes interessadas
(stakeholder registers)

---

## D19 — RH

Recrutamento, capacitação técnica e gestão de segurança e saúde
ocupacional (SSO) em canteiros de obra e operação.

**Aplicabilidade:** S1 ● · S2 ● · S3 ● · S11 ● · S4 ◐ · S5 ● · S7 ◐ ·
S8 ◐ · S6 ◐ · S9 ◐ · S10 ◐

**Normas-chave:** NR-18 (condições de segurança na construção civil),
NR-35 (trabalho em altura), NR-33 (espaços confinados), NR-10
(instalações elétricas)

**Ferramentas:** plataformas de gestão de SST, sistemas de treinamento
e-learning, controle de acesso biométrico a canteiro

---

## D20 — Qualidade

Controle de qualidade de execução, validação de ensaios, conformidade
normativa e certificação de sistemas de gestão.

**Aplicabilidade:** transversal — crítica onde a falha tem consequência
de segurança: S2 ● · S11 ● · S4 ● · S1 ◐ · S3 ◐ · S5 ● · S6 ◐ · S7 ◐ ·
S8 ◐ · S9 ◐ · S10 ◐

**Normas-chave:** ISO 9001 (SGQ), NBR 5674 (manutenção de edificações),
PBQP-H (qualidade habitacional), programas de ensaios acreditados
(RBC/INMETRO)

**Ferramentas:** software de gestão da qualidade (não conformidades,
ações corretivas), checklists de inspeção, laudos de ensaio
laboratorial

---

## Matriz-resumo Disciplina × Segmento

| Disciplina | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D01 Hidráulica | ◐ | ○ | ○ | ◐ | ○ | ○ | ◐ | ○ | ● | ◐ | ● |
| D02 Estrutural | ○ | ● | ◐ | ◐ | ◐ | ● | ◐ | ◐ | ○ | ○ | ● |
| D03 Geotecnia | ● | ◐ | ● | ◐ | ● | ○ | ◐ | ○ | ○ | ◐ | ● |
| D04 Pavimentação | ● | ○ | ◐ | ○ | ○ | ◐ | ◐ | ● | ○ | — | — |
| D05 Elétrica | ○ | ○ | ○ | ● | ○ | ◐ | ◐ | ◐ | ◐ | ● | ● |
| D06 Ambiental | ● | ◐ | ◐ | ◐ | ◐ | ○ | ◐ | ◐ | ● | ● | ● |
| D07 Econômico | ◐ | ◐ | ◐ | ◐ | ○ | ◐ | ● | ● | ● | ● | ◐ |
| D08 Planejamento | ◐ | ● | ◐ | ● | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ● |
| D09 Jurídico | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ● | ● | ◐ | ● | ◐ |
| D10 Comercial | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ |
| D11 MEP | — | ○ | — | ◐ | ○ | ● | ◐ | ● | ○ | ○ | ○ |
| D12 HVAC | — | — | ○ | ● | ● | ● | ◐ | ● | ○ | ○ | ○ |
| D13 Acústica | ◐ | ○ | ◐ | ● | ◐ | ● | ○ | ● | — | ○ | — |
| D14 Acessibilidade | ○ | ○ | ○ | ● | ○ | ● | ◐ | ● | ○ | — | — |
| D15 BIM | ◐ | ● | ◐ | ● | ● | ● | ◐ | ◐ | ○ | ○ | ● |
| D16 Paisagismo | ◐ | — | — | ○ | — | ● | ○ | ○ | ○ | — | ○ |
| D17 TI/Telecom | ○ | ○ | ○ | ● | ○ | ◐ | ◐ | ● | ◐ | ● | ◐ |
| D18 Comunicação | ◐ | ○ | ◐ | ○ | ○ | ○ | ◐ | ◐ | ● | ● | ● |
| D19 RH | ● | ● | ● | ◐ | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ● |
| D20 Qualidade | ◐ | ● | ◐ | ● | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ● |

---

## Notas de integração com o Eixo 2 (routing)

- O routing do Maestro (`CLAUDE.md`, seção "ROUTING — Maestro") decide
  **qual agente vertical (S1-S11)** atende um pedido. O Eixo D não altera
  esse routing — é uma camada de referência que os próprios agentes
  verticais consultam para saber **quais especialistas/disciplinas**
  mobilizar dentro de um projeto já atribuído a um segmento.
- Disciplinas com aplicabilidade "●" em múltiplos segmentos (D08
  Planejamento, D09 Jurídico, D19 RH, D20 Qualidade) são candidatas
  naturais a agentes horizontais dedicados (Eixo 1), caso a demanda
  justifique — hoje cobertas de forma distribuída pelos agentes
  verticais e pelo Manta 15 (advisory).
- Este documento não substitui o `CLAUDE.md` master nem exige alteração
  do DEPLOY CHECKLIST v4.2. É referência complementar do Eixo D.

---

## Histórico de versões

- **v1.0** (2026-07-31) — criação do documento, 20 disciplinas (D01–D20),
  aplicabilidade mapeada contra os 11 segmentos verticais (S1–S11).
