# Fontes — Brasil

Catálogo legível por máquina: `../../data/consumos/registro-fontes.csv`
(171 fontes, BR + internacional). Este documento explica **o que cada camada
entrega** — que é a informação que evita o erro mais comum do projeto.

Cada fonte tem um campo `entrega`. Ele governa o que a fonte pode originar:

| `entrega` | Pode gerar linha de intensidade? |
| --- | --- |
| `coeficiente_fisico` | sim |
| `indice_macro` | sim, como deflator ou denominador auxiliar |
| `metodologia` | não — orienta o método |
| `custo_unitario_agregado` | **não** — o validador reprova |

Ministério, PPI, Novo PAC, BNDES e multilaterais são quase todos
`custo_unitario_agregado`: publicam CAPEX de projeto, não coeficiente de
composição. São **denominadores**, não numeradores. O validador transforma isso
em regra dura.

---

## Camada 1 — Estatística oficial (a espinha dorsal)

A única camada capaz de gerar tier A.

- **PAIC — Pesquisa Anual da Indústria da Construção (IBGE)** — `F-001`.
  A fonte mais importante do projeto. Publica valor das obras e/ou serviços,
  pessoal ocupado, salários, e custos e despesas por classe CNAE. Divide-se um
  pelo outro e sai a intensidade, sem premissa intermediária.
  Já extraída daqui a **estrutura de custos e despesas**: 2022 = 48,3% pessoal /
  37,4% materiais / 14,3% terceiros; 2023 = 49,0 / 35,9 / 15,1. Atenção ao
  denominador — é *custos e despesas*, não *valor das obras*.
- **Matriz de insumo-produto (IBGE)** — `F-002`. Coeficiente técnico de aço,
  cimento e aluguel de máquinas por unidade de produção da construção. É a rota
  que **resolve a ressalva da autoconstrução**, porque numerador e denominador
  saem do mesmo sistema de contas.
- **SIDRA (IBGE)** — `F-004`. **Tabela 1761** é a da PAIC por classe CNAE. É o
  desbloqueio de S6 e S10 (ambos em 42.91-0), S8 e S9 de uma só vez.
- **SINAPI (Caixa/IBGE)** — `F-006`. Composições com coeficiente explícito.
  Atenção: **embute perda de material**, ao contrário do SICRO.
- **CNAE 2.0 / CONCLA (IBGE)** — `F-007`. Classificação oficial. Necessária para
  validar o crosswalk.
- **Novo CAGED e RAIS (MTE)** — `F-008`, `F-009`. Emprego e horas contratadas por
  CNAE. É por aqui que se troca a premissa de 1.800 h/ano por dado observado.
- **PNAD Contínua (IBGE)** — `F-010`. Ocupação informal — relevante porque a PAIC
  cobre só empresas formais, e a diferença é grande na construção.
- **Contas Nacionais / FBCF em construção (IBGE)** — `F-003`. Denominador macro
  alternativo.
- Internacional na mesma camada: Eurostat `F-011`, OECD ICIO `F-012`, WIOD
  `F-013`, EXIOBASE `F-014`, UN IRP `F-015`, US Census `F-016`, BLS PPI `F-017`,
  INDEC ICC `F-018` (relevante para AySA).

## Camada 2 — Governo e planejamento setorial

44 fontes. Quase todas `custo_unitario_agregado` — denominadores de CAPEX.

**Metodologia e composição:** SICRO 4 `F-019` e o **MCIT/DNIT** `F-020` —
**esta é a única fonte do projeto efetivamente lida na origem** (via SharePoint,
`fonte_primaria_lida`). O *Manual de Custos de Infraestrutura de Transportes*,
2ª edição 2025, tem **oito volumes**: 01 Metodologia e Conceitos, 02 Mão de Obra,
03 Preços Referenciais, 04 **FIC — Fator de Influência de Chuvas**, 05 **FIT —
Fator de Interferência de Tráfego**, 06 Canteiro de Obras, 07 Administração
Local, 08 Mobilização e Desmobilização. A produtividade sai da **PEM — Produção
de Equipe Mecânica**. Os **coeficientes de consumo de material** estão nos
*cadernos técnicos* (memoriais de cálculo), não no manual. Âncora metodológica do
projeto, mesmo com rodovias fora do escopo de coleta.

**Denominadores de CAPEX:** Novo PAC `F-021`, portal PPI `F-036`, BNDES `F-037`,
PNL `F-022`, PELT `F-023`.

**Por setor prioritário:**

| Setor | Fontes-chave |
| --- | --- |
| S6 Portos | Planos Mestres Portuários `F-024`, PNLP `F-025`, estudos de arrendamento ANTAQ `F-039` |
| S7 Aeroportos | estudos de concessão ANAC `F-026` — **essencial**, porque não há classe CNAE |
| S8 Saneamento | PLANSAB `F-027`, SNIS `F-043`, tabelas SABESP `F-057`, SANEPAR `F-058`, COPASA `F-059`; **AySA `F-061`** e ERAS `F-062` para a Argentina |
| S9 Energia | PDE `F-028`, relatórios R1–R5 de leilão `F-030`, módulos de custo ANEEL `F-031`, Eletrobras `F-060` |
| S10 Barragens | SNISB/ANA `F-041`, SIGBM/ANM `F-042`, PISF `F-032`, Codevasf `F-033`, DNOCS `F-034` |

**Fonte pouco usada e de alto valor:** os **EVTEAs da Infra S.A.** `F-035`
trazem orçamento referencial de obra linear em formato aberto.

**TCU `F-044` e CGU `F-047`** são atípicas e valiosas: acórdãos de fiscalização
trazem curva ABC e produtividade **discutida em contraditório técnico** — ou seja,
coeficiente que já sobreviveu a questionamento. Raro.

**Tabelas estaduais** com composição e coeficiente: DER-SP `F-048`, DER-PR
`F-049`, SETOP/MG `F-050`, ORSE `F-051`, SEINFRA-CE `F-052`, EMOP-RJ `F-053`,
SUDECAP `F-054`, CPOS `F-055`, AGETOP `F-056`.

**Nota AySA (prioridade):** o *análisis de precios* dos pliegos argentinos
publica coeficiente explícito de mano de obra, equipo e material — formato mais
rico que o edital brasileiro típico. É a melhor porta de entrada para S8 na
Argentina.

## Sistemas de custo referencial por segmento — um por modal

Achado da rodada de 2026-08-22: o Brasil tem **um sistema de custo referencial
por modal**, não só o SICRO. Cada um publica cadernos de composição, e é ali que
vive o coeficiente de consumo. Esta é a rota mais direta para intensidade
**diferenciada por setor** — que é justamente o que a MIP agregada do IBGE não
entrega.

| Segmento | Sistema | Onde está o coeficiente | Acesso |
| --- | --- | --- | --- |
| S1/S2 rodovias e OAE | **SICRO** (DNIT) `F-019`/`F-020` | cadernos técnicos / memoriais de cálculo | ✅ **lido** via SharePoint |
| S3 ferrovia | **SICFER** (ANTT) `F-172` | V5 Materiais; V6 Manuais Técnicos, Conteúdo 02 Superestrutura | portal ANTT (egress bloqueia) |
| S4 metrô | **SIEC** (CPTM) `F-173` | Caderno de Composições de Serviços + Caderno de Insumos | ✅ SharePoint da Manta |
| S8 saneamento | SINAPI `F-006` + SABESP/SANEPAR/COPASA `F-057`–`F-059` | composições | portais (egress bloqueia) |
| S9 energia | **ANEEL BPR** `F-174` | quantidades de materiais por módulo de LT e de SE | dados abertos, CSV |
| S10 barragens | **Eletrobras OPE** `F-175` | composições por componente de UHE | acervo Eletrobras |

Notas que mudam o valor de cada um:

- **ANEEL BPR** `F-174` é o achado mais forte. Está em **dados abertos, em CSV**,
  e a metodologia "traz a descrição das **quantidades de materiais**, equipamentos
  e serviços" — portanto coeficiente físico, não só preço. Modular: subestação em
  Módulo de Infraestrutura, de Manobra e de Equipamento; LT parametrizada por
  tecnologia (CC/CA), classe de tensão, tipo de circuito, estrutura, fundação,
  cabo condutor, arranjo e cabo para-raios. Há CSV dedicado de *estrutura em aço*.
  Usar junto com o PRORET Submódulo 9.7 `F-178`, que define a atualização por
  índices parametrizados.
- **SIEC** `F-173` é o único **já acessível** além do SICRO: o manual está no
  SharePoint da Manta em `01_BIBLIOTECA/01_ORÇAMENTO/01.05_BASE ORÇAMENTOS/SIEC/`.
- **Eletrobras OPE** `F-175` é a melhor fonte encontrada para S10: orçamento
  sintético de viabilidade com composições por componente de UHE — barragem,
  tomada de água, conduto forçado, casa de força. Par documental com o MCSE.
- **SICFER** `F-172` é o análogo ferroviário direto do SICRO, com 9+ volumes.
  Não está no SharePoint; depende de acesso ao portal da ANTT.

## Atualização do coeficiente-âncora de insumo-produto

A MIP oficial mais recente do IBGE é a de **2015** (Contas Nacionais nº 62) —
`F-002`. Para quem precisa de série mais nova, o **NEREUS/USP** `F-177` estima
matrizes **anuais** (série 2010–2018 localizada), com trabalho equivalente no
IE/UFRJ. É estimativa acadêmica (tier C), não estatística oficial, mas é a única
forma de sair de 2015 sem esperar a próxima MIP do IBGE.

---

## Camada 3 — Associações e institutos setoriais

Onde está a **quantidade física** que a estatística oficial não abre.

- **SNIC** `F-063` — consumo aparente de cimento. Série mensal longa.
- **Instituto Aço Brasil** `F-064` — consumo aparente de aço e participação da
  construção civil.
- **CBIC Dados** `F-067` — consolidador de cimento, aço, emprego e custo. Atalho
  para várias séries de uma vez.
- **Sobratema** `F-068` — *Estudo do Mercado Brasileiro de Equipamentos para
  Construção*. **A melhor fonte brasileira de frota e hora-máquina.** Licenciada;
  verificar se a Manta assina.
- **CBDB** `F-074` — indispensável para S10, já que a CNAE não tem classe de
  barragem.
- Ainda: ABCP `F-065`, ABRAMAT `F-066`, ABIMAQ `F-069`, ABDIB `F-070`, CNI
  `F-071`, SindusCon/CUB `F-072`, ABES `F-073`, ABCE `F-075`, ABPv `F-076`,
  IBRACON `F-077`, ABMS/ABGE `F-078`.

## Camada 4 — Índices e pesquisa econômica

- **INCC (FGV/IBRE)** `F-079` — os **pesos por família de insumo** são o insumo
  direto da rota indireta. Prioridade alta.
- IGP-DI/IGP-M `F-080` como deflator; Sondagem da Construção `F-081`.
- FGV Projetos `F-082` e **FGV CERI** `F-083` para custo de concessão.
- **FIPE-USP** `F-084` e **FIA** `F-085`.

## Camada 5 — Academia

- **Poli-USP / PCC** `F-086` — referência nacional de **perdas de material em
  canteiro e produtividade de mão de obra** (linha de pesquisa Agopyan/Souza).
  A diferença entre perda de norma e perda medida chega a dezenas de pontos
  percentuais, e nenhuma tabela oficial captura isso.
- **NORIE/UFRGS** `F-089` (Formoso) complementa em perdas e Lean.
- **COPPE/UFRJ** `F-090` para portos e geotecnia; **IPT** `F-087`;
  **EESC-USP** `F-088` para barragens e estruturas.
