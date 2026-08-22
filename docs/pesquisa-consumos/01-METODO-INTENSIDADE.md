# Método — Intensidade de Insumo por Receita Setorial

## O que a base mede

Para um setor, um ano e um país:

```text
intensidade = quantidade física de insumo consumida
              ─────────────────────────────────────
              receita / valor de obra / CAPEX do setor
```

Oito famílias de insumo, vocabulário fechado:

| Família | Unidade |
| --- | --- |
| `mao_de_obra` | `pessoas-ano/R$ mi` e `hh/R$ mi` |
| `equipamentos` | `hm/R$ mi` ou `R$/R$ mi` |
| `aco` | `t/R$ mi` |
| `concreto` | `m3/R$ mi` |
| `cimento` | `t/R$ mi` |
| `agregados` | `t/R$ mi` |
| `combustivel` | `L/R$ mi` |
| `outros_materiais` | `R$/R$ mi` (residual, só valor) |

Preço **não** entra na base. Custo é derivado, e derivar é papel do
`manta-05 (orcamento)`.

## Rota direta

A fonte já publica quantidade física e receita **para o mesmo recorte**. Basta
dividir. `metodo = direto`.

Caso central: a **PAIC/IBGE** publica, por classe CNAE, o valor das obras e/ou
serviços e o pessoal ocupado. A divisão dá a intensidade de mão de obra sem
nenhuma premissa intermediária.

A **matriz de insumo-produto do IBGE** é a outra rota direta, e a melhor para
material: traz o coeficiente técnico de aço, cimento e aluguel de máquinas por
unidade de produção da construção.

## Rota indireta

A fonte dá a **estrutura de custo** (% por família) e o preço médio do insumo. A
quantidade física sai de:

```text
quantidade = receita × participação% ÷ preço unitário médio
```

`metodo = indireto`, e `memoria_calculo` passa a ser **obrigatório** — o
validador reprova a linha sem ela. Caso central: os pesos do **INCC (FGV/IBRE)**
cruzados com preço de aço (Instituto Aço Brasil), cimento (SNIC) e salário-hora
(CAGED/RAIS).

## Exemplo trabalhado — mão de obra em obras de infraestrutura

Dado da PAIC 2022 para o recorte CNAE 42 (obras de infraestrutura):

- valor das obras e/ou serviços: **R$ 147,8 bilhões**
- pessoal ocupado: **684,7 mil pessoas**

**Passo 1 — intensidade direta.**

```text
684.700 pessoas ÷ R$ 147.800 mi = 4,633 pessoas-ano por R$ 1 milhão
```

Linha `INT-C42-MAO_DE_OBRA-001`, `metodo = direto`, sem premissa nenhuma.

**Passo 2 — conversão para homem-hora.** Aqui entra premissa, e ela precisa
ficar visível:

```text
4,633 pessoas-ano/R$ mi × 1.800 h/ano = 8.339 hh por R$ 1 milhão
```

Linha `INT-C42-MAO_DE_OBRA-002`, `metodo = indireto`, com
`premissas = "1.800 h/ano (~220 dias úteis). PREMISSA MANTA, não é dado do IBGE."`

As 1.800 h/ano **não** vêm do IBGE. Trocar essa premissa reescala a linha
inteira, e é por isso que ela não pode ficar implícita.

**Passo 3 — leitura do resultado.** Comparando os três recortes de 2022:

| Recorte | pessoas-ano/R$ mi |
| --- | --- |
| 41 — construção de edifícios | 4,636 |
| 42 — obras de infraestrutura | 4,633 |
| 43 — serviços especializados | 7,329 |

Edificação e infraestrutura têm intensidade de mão de obra praticamente idêntica
por real faturado; serviços especializados são ~58% mais intensivos. Faz sentido:
serviço especializado é justamente a parcela que subcontrata mão de obra sem
carregar material e equipamento no próprio faturamento.

## As três disciplinas obrigatórias

Sem elas a base não presta, e o validador cobra as três.

### 1. Denominador declarado

São bases diferentes e **não se misturam na mesma linha**:

| `denominador` | O que é | Quem publica |
| --- | --- | --- |
| `valor_obras_paic` | valor das obras e/ou serviços executados por empresas formais | PAIC/IBGE |
| `receita_paic` | receita bruta/líquida das empresas | PAIC/IBGE |
| `capex_projeto` | investimento previsto ou realizado de um projeto | PPI, Novo PAC, INFRALATAM |
| `valor_obra_contratada` | valor do contrato | editais, TCU |
| `vbp` | valor bruto da produção | contas nacionais |

Misturar numerador de uma base com denominador de outra é o erro que inutiliza
esse tipo de trabalho — e é exatamente o que as duas linhas de material desta
base fazem hoje (cimento e aço do SNIC/Aço Brasil sobre valor da PAIC). Está
declarado no campo `premissas` de cada uma, como limite superior, não como valor
central.

### 2. Ano-base e deflator

Toda linha carrega `ano_base` e `deflator`. `nominal_corrente` significa valor do
próprio ano, sem deflacionamento — é uma escolha explícita, não uma omissão.
Série temporal sem deflator declarado é ruído.

### 3. Moeda e paridade

`BRL`, `USD`, `USD_PPC`, `EUR`, `ARS`. Comparação internacional em dólar nominal
engana muito entre países de custo de mão de obra distinto: a intensidade em
`hh/US$ mi` de um país de salário baixo parece altíssima sem que a produtividade
física seja diferente. Para comparar produtividade, use `USD_PPC`; para comparar
custo, use `USD`.

O validador cobra coerência: unidade em `R$` exige `moeda = BRL`.

## A ressalva da autoconstrução

O consumo nacional aparente de cimento e de aço inclui **autoconstrução** e obra
executada fora do universo de empresas formais que a PAIC mede. Dividir consumo
nacional por receita da PAIC portanto **superestima** a intensidade da construção
formal.

As duas linhas de material desta base (`INT-CF-CIMENTO-001`, `INT-CF-ACO-001`)
são **limite superior**, e o campo `premissas` diz isso. Corrigir exige a matriz
de insumo-produto (F-002), que resolve o problema por construção porque numerador
e denominador vêm do mesmo sistema de contas.

## Taxonomia de custo do SICRO como ponte

O SICRO organiza custo direto em equipamentos, mão de obra e materiais, e é a
única fonte brasileira que trata explicitamente a perda de produtividade por
fatores nomeados. Verificado no manual primário (MCIT 2ª edição, Volume 01,
2025, 111 p., aprovado pela Diretoria Colegiada do DNIT em 21/10/2025):

- **PEM — Produção de Equipe Mecânica** (§3.3.4) é o mecanismo de produtividade;
  §3.3.2 define o *ciclo do serviço* e §3.3.3 o *líder da produção da equipe*.
- **FIC — Fator de Influência de Chuvas** (Volume 04, em dois tomos).
- **FIT — Fator de Interferência de Tráfego** (Volume 05).
- As composições têm **parcela horária e parcela unitária** (Figura 3).
- Os **cadernos técnicos** (memoriais de cálculo) é que trazem "as condições de
  contorno adotadas nos cálculos dos **consumos dos materiais** e da **produção
  horária dos serviços**" — ou seja, é ali, não no manual, que vivem os
  coeficientes de consumo.

Isso faz do SICRO a ponte natural entre esta base top-down e a Fase 2 bottom-up.
RSMeans e BEDEC não têm equivalente declarado de FIC/FIT.

## Estrutura de custo — e a armadilha do denominador

`estrutura-custo-setor.csv` guarda participação percentual por família. É o
insumo da rota indireta e, sozinha, já responde perguntas de dimensionamento.

Dado extraído da PAIC:

| Componente | 2022 | 2023 |
| --- | --- | --- |
| Despesas de pessoal | 48,3% | 49,0% |
| Custo dos materiais de construção | 37,4% | 35,9% |
| Obras e serviços de terceiros | 14,3% | 15,1% |

**A armadilha.** Esse bloco tem denominador `custos_despesas_paic`. Existe outro
bloco, do mesmo ano e da mesma fonte, com denominador `valor_obras_paic`, onde
remunerações são **18,1%**. Os dois números descrevem coisas diferentes:

- 48,3% = participação no **custo total declarado** pelas empresas;
- 18,1% = participação no **valor das obras executadas**.

Somar ou comparar os dois é erro. Por isso o arquivo tem coluna `denominador`
obrigatória, e o validador usa `(setor, ano, denominador, fonte)` como chave do
bloco de 100% — sem o denominador na chave, os dois blocos de 2022 somariam 200%
e o validador aprovaria.

**Segunda leitura, menos óbvia.** Os 14–15% de *obras e serviços de terceiros*
contêm mão de obra subcontratada. Logo os 48,3% de despesas de pessoal
**subestimam** a intensidade real de trabalho do setor. É coerente com o que as
intensidades diretas mostram: serviços especializados (CNAE 43) têm 7,329
pessoas-ano por R$ mi contra 4,633 da infraestrutura — a mão de obra que a
construtora não carrega na folha aparece no faturamento de quem subcontrata.

---

## Tiers de qualidade

| Tier | Critério |
| --- | --- |
| **A** | estatística oficial com quantidade e receita no mesmo recorte (PAIC lida no SIDRA, MIP/IBGE, Eurostat, OECD ICIO) |
| **B** | publicação institucional ou de associação setorial (SNIC, Aço Brasil, CBIC, Sobratema, FGV/IBRE, Banco Mundial, BID) |
| **C** | literatura acadêmica |
| **D** | fonte única, projeto isolado, **ou dado não verificado contra a fonte primária** |

Regra de agregação: faixa P10/P50/P90 só se publica com **≥ 3 observações
independentes de tier A ou B**. Abaixo disso, valor indicativo, e é proibido usar
sozinho para orçar.

O campo `verificacao` é ortogonal ao tier e mais duro que ele:
`fonte_primaria_lida` só quando alguém abriu o documento. `snippet_busca`
significa que o número veio de resultado de busca — útil para ordem de grandeza,
inaceitável em entregável de cliente.
