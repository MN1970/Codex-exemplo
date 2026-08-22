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

**Âncora com fonte para essa premissa.** O SIEC/CPTM (`F-173`, lido na origem)
declara **jornada de 44 horas semanais**, exceto onde convenção coletiva fixa
limite inferior. Isso dá 2.288 h/ano contratuais; descontando 30 dias de férias e
os feriados, chega-se a algo próximo de **2.000 h/ano** de horas pagas e
presentes. As 1.800 h/ano adotadas são, portanto, conservadoras e dentro da
faixa — mas quem quiser um número com fonte deve partir da jornada de 44 h e
declarar o desconto aplicado, ou usar o CAGED/RAIS (`F-008`, `F-009`) para horas
observadas em vez de contratuais.

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

## Hora produtiva × improdutiva, e perda embutida

Duas fontes brasileiras tratam isso explicitamente — e de formas diferentes, o
que importa na hora de comparar.

**SICRO/DNIT** (`F-019`, `F-020`) trata a perda de produtividade por **fatores
externos nomeados e separados** da composição: **FIC** (chuvas, Volume 04) e
**FIT** (tráfego, Volume 05). A produtividade da equipe vem da **PEM**.

**SIEC/CPTM** (`F-173`) resolve dentro do próprio vocabulário de insumo. São
seis tipos, e dois deles são a distinção que interessa:

| Tipo | Significado |
| --- | --- |
| `MOH` / `MOM` | mão de obra horista / mensalista |
| **`EQCH`** | **equipamento produtivo** |
| **`EQCI`** | **equipamento improdutivo** |
| `MAT` | material |
| `FEI` | fornecimento e instalação |
| `SERV` | composição auxiliar |

O manual dedica seções próprias a custo horário produtivo (§3.2.5) e improdutivo
(§3.2.6). Para a Fase 2, isso é melhor que o SICRO: a separação já vem no tipo do
insumo, não num fator aplicado depois.

**A diferença que quebra comparação.** O SIEC declara que seus coeficientes
**já embutem** duas coisas: as improdutividades inerentes à execução (paralisação
para instrução de equipe, deslocamento no canteiro) **e as perdas de material**
(cortes, transportes, reaproveitamentos). Ou seja, `perda_incluida = true` — como
SINAPI e BEDEC, e **ao contrário** do SICRO, que trata os fatores por fora.

Somar coeficiente SIEC com coeficiente SICRO sem declarar isso conta a perda uma
vez em um e duas vezes no outro. É o motivo de o schema da Fase 2 exigir os
campos `perda_incluida` e `hora_produtiva_apenas`.

---

## Compra direta × cadeia inteira — reconciliação com o Livro Azul

O portal **Livro Azul** da Manta (`F-181`) calcula intensidade física de cimento e
aço para 6 segmentos. Esta base calculou os mesmos dois insumos por outro
caminho. Os resultados divergem, e **entender por quê é mais útil que escolher um
dos dois**.

| Insumo | Esta base | Livro Azul | Gap |
| --- | --- | --- | --- |
| Cimento | 123,9 t/R$ mi (2024) | 109,13 t/R$ mi (2015) | **+13%** |
| Aço | 18,63 t/R$ mi (2024) | 4,656 t/R$ mi (2015) | **+300%** |

**Os métodos.** O Livro Azul usa a **Matriz de Insumo-Produto 2015 do IBGE**, aba
11 "Coeficientes técnicos — insumos nacionais (Bn)", coluna "4180 Construção",
conferida célula a célula: cimento = linhas 23001 (cimento puro, 1,3895%) + 23002
(artefatos de cimento, 3,5212%) = 4,9107% do valor da produção; aço = 24912
(semiacabados/laminados/tubos, 2,0664%) + 24922 (peças fundidas, 0,0286%) =
2,0950%. Esta base divide **consumo nacional aparente** — SNIC para cimento,
Instituto Aço Brasil para aço, com a participação de 37,3% da construção — pelo
valor das obras da PAIC.

**O ano-base agrava, não explica.** As duas linhas do portal estão a preços de
2015; as desta base, de 2024. R$ 1 milhão de 2015 compra **mais** insumo físico
que R$ 1 milhão de 2024, então o coeficiente de 2015 deveria ser o *maior* dos
dois. Ele é o menor. Corrigir o ano-base **aumenta** o gap. Quantificar exige o
deflator; sem ele, a comparação é só direcional.

**A explicação está na assimetria.** Se fosse erro de medição ou de denominador, os
dois insumos divergiriam parecido. Cimento fica em 13% e aço em 300% — e é isso
que identifica a causa:

- A **MIP** registra o que a construtora compra **diretamente** como produto de
  aço. Aço que chega à obra embutido em estrutura pré-fabricada, tubo ou
  pré-moldado é lançado em **outra linha** da matriz, não em 24912.
- O **Instituto Aço Brasil** atribui à construção **a cadeia inteira**: os 37,3%
  do consumo aparente incluem o aço que virou componente antes de chegar ao
  canteiro.
- No **cimento** isso quase não morde, porque cimento chega como cimento ensacado
  ou concreto usinado — pouca transformação intermediária. Daí os 13%.

Ou seja: **não há erro em nenhum dos dois.** São duas medidas de coisas
diferentes, e o cimento serve de controle que prova isso.

### Qual usar para qual pergunta

| Pergunta | Use | Por quê |
| --- | --- | --- |
| Quanto de material o setor vai **comprar** (mercado, cadeia de suprimentos) | atribuição de cadeia (Aço Brasil, SNIC) | captura todo o insumo que termina em obra, inclusive o embutido |
| Multiplicador econômico, insumo-produto, encadeamento setorial | **MIP/IBGE** | é consistente com o sistema de contas nacionais |
| Orçar uma obra | **nenhuma das duas** | usa-se composição bottom-up (SICRO, SIEC, SINAPI) |

### O que cada base adiciona à outra

O portal tem o denominador de CAPEX por segmento e a composição de custo por
setor, mas aplica **um coeficiente físico único** aos 6 segmentos — limitação que
ele próprio declara, porque a MIP trata "Construção" como atividade agregada
(CNAE 41–43). Esta base traz o método, o schema, o validador e a rota para
**intensidade diferenciada por setor**, via PAIC por classe CNAE (SIDRA 1761) e os
sistemas de custo por modal. E cobre S9 e S10, que o portal não inclui.

A ressalva do próprio portal merece registro, porque é honesta e relevante: o
coeficiente de cimento soma "artefatos de cimento", cujo valor inclui também
areia, brita, água e mão de obra da concreteira — convertido a toneladas pelo
preço do cimento puro, que é a escolha conservadora.

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
