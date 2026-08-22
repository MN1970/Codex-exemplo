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
- **Matriz de insumo-produto (IBGE)** — `F-002`. Coeficiente técnico de aço,
  cimento e aluguel de máquinas por unidade de produção da construção. É a rota
  que **resolve a ressalva da autoconstrução**, porque numerador e denominador
  saem do mesmo sistema de contas.
- **SIDRA (IBGE)** — `F-004`. Onde vivem as tabelas da PAIC por classe. É o
  desbloqueio de S6, S8 e S9.
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

**Metodologia e composição:** SICRO 4 `F-019` e o **MCIT/DNIT** `F-020`. O SICRO
é a única fonte brasileira que documenta produtividade de equipe mecânica e
separa hora produtiva de improdutiva via FIT/FIU. Âncora metodológica do projeto,
mesmo com rodovias fora do escopo de coleta.

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
