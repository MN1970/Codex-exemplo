# refs/ — agente-edificacoes

Bibliografia mínima que o agente assume. Colocar aqui os PDFs/DOCX
das fontes. O RAG (`edi:*`) ingere estes documentos para retrieval.

## Regulação — Brasil (normas técnicas)

### Estruturas
- **NBR 6118** — Projeto de estruturas de concreto (obrigatória BR).
- **NBR 8800** — Projeto de estruturas de aço e mistas.
- **NBR 6120** — Ações para o cálculo de estruturas de edificações.
- **NBR 6122** — Projeto e execução de fundações.
- **NBR 8681** — Ações e segurança nas estruturas (base).
- **NBR 15421** — Projeto sísmico de estruturas (relevante NE).
- **NBR 15961** / **NBR 15812** — Alvenaria estrutural (blocos de concreto
  e cerâmicos).

### Desempenho e habitação
- **NBR 15575** — Desempenho de edificações habitacionais (partes 1-6).
  **CRÍTICA para MCMV pós-2013** — níveis Mínimo, Intermediário,
  Superior; térmico, acústico, lumínico, estrutural, segurança contra
  incêndio, durabilidade, funcionalidade.

### Incêndio (SCI)
- **NBR 9077** — Saídas de emergência em edifícios.
- **NBR 14432** — Exigências de resistência ao fogo.
- **NBR 13714** — Sistemas de hidrantes e mangotinhos.
- **NBR 10897** — Chuveiros automáticos (sprinklers).
- **NBR 10898** — Iluminação de emergência.
- **IT-CBMESP** (SP) — Instruções Técnicas do Corpo de Bombeiros SP
  (IN 22/2015). Correspondentes por estado: **IT-CBMRJ, IT-CBMMG,
  IT-CBMPR, IT-CBMBA**.

### Instalações
- **NBR 5410** — Instalações elétricas de baixa tensão.
- **NBR 5419** — Proteção contra descargas atmosféricas (SPDA classes
  I-IV).
- **NBR 5626** — Instalação predial de água fria.
- **NBR 8160** — Sistemas prediais de esgoto sanitário.
- **NBR 10844** — Instalações prediais de águas pluviais.
- **NBR 15526** — Redes de distribuição interna para gases combustíveis.
- **NBR 16401** — Instalações de ar-condicionado.

### Envoltória e impermeabilização
- **NBR 9575** — Impermeabilização — seleção e projeto.
- **NBR 16015** — Fachadas com sistema ACM.
- **NBR 7199** — Vidros na construção civil.

## Regulação — Brasil (habitação social e mandatos)

- **Portaria MDR MCMV** — regras e faixas 1/2/3 (2023-2026).
- **Selo Casa Azul CAIXA** (2020) — 5 categorias (qualidade urbana,
  projeto, água, energia, materiais/gestão), 3 níveis (bronze, prata,
  ouro).
- **Decreto 10.306/2020** — Estratégia BIM BR, fases 1-3 (BIM em obras
  federais).
- **Caderno de Encargos CAIXA** (habitacional).
- **Caderno de Encargos MEC** (escolas padrão FNDE).

## Regulação — Internacional

- **ACI 318** — Building Code Requirements for Structural Concrete (EUA).
- **AISC 360** — Specification for Structural Steel Buildings.
- **Eurocode 2** (concreto), **Eurocode 3** (aço), **Eurocode 8** (sísmica).
- **ASCE 7** — Minimum Design Loads for Buildings.
- **IBC** — International Building Code (EUA, referência global).
- **NFPA 13** (sprinklers), **NFPA 101** (Life Safety Code).

## Certificações de sustentabilidade

- **LEED v4.1** (USGBC) — BD+C, ID+C, O+M, ND, Homes.
- **AQUA-HQE** (Fundação Vanzolini) — brasileira, HQE francesa.
- **Selo Casa Azul CAIXA** — 3 níveis para habitação popular.
- **EDGE** (IFC/Banco Mundial) — 20/20/20 (energia/água/materiais).
- **WELL** (IWBI) — foco em bem-estar e saúde ocupacional.
- **Living Building Challenge** — regenerativo (7 pétalas).

## BIM (Modelagem)

- **ISO 19650** partes 1-2 (organização e digitalização — BIM).
- **IFC 4.3** (buildingSMART).
- **NBR 15965** — Sistema de classificação da informação da
  construção.
- **BIM Fóruns Brasil** (SBTA).

## Livros de referência

- McCormac / Brown — *Design of Reinforced Concrete* (concreto).
- Salmon / Johnson — *Steel Structures: Design and Behavior* (aço).
- Ching — *Building Construction Illustrated* (didático).
- Ferraz — *Fundações Rasas e Profundas* (BR).
- Velloso / Lopes — *Fundações* (COPPE/UFRJ).
- Souza / Ripper — *Patologia, Recuperação e Reforço de Estruturas de
  Concreto* (retrofit).
- Neufert — *Arte de Projetar em Arquitetura* (programa e antropometria).

## Softwares esperados (consumo de arquivo)

- **Revit / RVT** + **IFC 4.3** — BIM (residencial, comercial, hospital).
- **ArchiCAD** — BIM (mais comum em arquitetos independentes).
- **AECOsim / Bentley** — infraestrutura + edificação.
- **Tekla Structures** — estrutura de aço detalhada.
- **TQS / Eberick** — cálculo estrutural concreto (BR).
- **SAP2000 / ETABS / CSiBridge** — análise estrutural (torres altas).
- **IDEA StatiCa** — ligações metálicas.
- **Navisworks / Solibri** — clash detection BIM.
- **ifcopenshell** — parsing IFC programático (backend Manta IFC).

## Bases de custos

- **SINAPI** — CAIXA + IBGE (mensal, 27 UFs, desonerada/onerada,
  regimes SD/CD/SE).
- **TCPO** — Editora Pini (composições unitárias).
- **CUB** — Sinduscon estadual (custo unitário básico R$/m²).
- **SICRO** — DNIT (obras rodoviárias, referência para edificações
  administrativas do DNIT).

## Casos brasileiros de referência por tipologia

- **Residencial popular (MCMV)**: MRV, Tenda, Direcional, Cury —
  faixas 1/2/3.
- **Residencial médio/alto**: Cyrela (Living, Class), Even, Tegra,
  Vitacon (compactos SP), Trisul, Direcional Setin.
- **Alto padrão / luxo**: JHSF Cidade Jardim, JHSF Fasano, Alphaville,
  Melnick Even.
- **Corporativo AAA**: B3 (SP), Faria Lima Iguatemi, JK 1455, Vila
  Olímpia lajes puras.
- **Uso misto**: Faria Lima Business Park, JHSF Boa Vista (retrofit),
  Iguatemi Alphaville.
- **Galpão logístico**: Log CP (BR-affiliate GLP), Bresco, Golgi,
  BRPR/Tellus, GLP Brasil.
- **Data center**: Ascenty (São Paulo, Rio), Odata (SP), Equinix (SP,
  RJ), Angola Cables Fortaleza.
- **Hospital privado**: Albert Einstein Morumbi (SP), Sírio-Libanês
  Bela Vista (SP), Rede D'Or expansões, Oswaldo Cruz (SP).
- **Universidade**: Insper (SP), FGV (SP/RJ), Estácio, PUC-RS.
- **Retrofit histórico**: Farol Santander (SP), Copan (SP — manutenção),
  Cais do Sertão (Recife).

## Convenções internas Manta

- Template PQ_SUPRIMENTOS adaptado para edificação (fundação → casca →
  vedações → MEP → acabamento).
- Composições unitárias TCPO + SINAPI + próprias.
- Checklists por tipologia (MCMV faixa 2, torre AAA, galpão WT, data
  center TIER III, hospital 300 leitos).
- Base histórica de projetos Manta em edificações (RAG `edi:cases:*`).
- Rubricas SINAPI mais relevantes por etapa (aço CA-50, concreto usinado
  25/30/35/40 MPa, bloco cerâmico/concreto, revestimento cerâmico,
  esquadria alumínio, ACM, curtain wall).
