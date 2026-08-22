# Fontes — Estados Unidos

35 fontes catalogadas (`F-137` a `F-171`). O mercado americano interessa por três
motivos concretos, não por completude:

1. **É o único par comparável do Brasil no mesmo formato.** A estrutura
   estatística americana espelha a brasileira quase item por item, o que permite
   comparação de intensidade sem malabarismo metodológico.
2. **Resolve duas lacunas do piloto** — a premissa de horas por ano e a
   comparação internacional que não saiu.
3. **Tem dado de licitação real e aberto** em volume que não existe no Brasil.

## Os pares BR ↔ US

| Função | Brasil | Estados Unidos |
|---|---|---|
| Censo da construção (receita, pessoal, custo de material) | PAIC/IBGE `F-001` | **Economic Census — setor NAICS 23** `F-137` |
| Matriz de insumo-produto | IBGE `F-002` | **BEA Input-Output Accounts** `F-138` |
| Horas e ganhos na construção | CAGED/RAIS `F-008`,`F-009` | **BLS CES** `F-139` |
| Consumo de cimento | SNIC `F-063` | **PCA — Portland Cement Association** `F-155` |
| Consumo de aço | Instituto Aço Brasil `F-064` | **AISI / SMA** `F-156` |
| Frota e equipamento | Sobratema `F-068` | **AEM** `F-157` |
| Índice de custo de construção | INCC — FGV/IBRE `F-079` | **ENR CCI/BCI** `F-162`,`F-163` |
| Composições oficiais de obra | SICRO 4 `F-019` | **bid tabs** de DOTs `F-145`–`F-147` |

O par que fecha a comparação internacional é **CNAE 42 ↔ NAICS 237** (heavy and
civil engineering construction). Está registrado em
`../../data/consumos/crosswalk-cnae-setores.csv`, junto com o grau de aderência
de cada segmento.

## O aviso sobre o ENR — leia antes de usar

O **ENR Construction Cost Index** tem uma cesta física fixa e pública:

| Item | Quantidade |
|---|---|
| mão de obra comum | **200 horas** (média de 20 cidades, salário + encargos) |
| aço estrutural fabricado | **25 cwt** = 2.500 lb ≈ 1,13 t |
| cimento portland a granel | **1,128 t** |
| madeira 2x4 | **1.088 board feet** |

O **BCI** usa a mesma cesta de material trocando mão de obra comum por **mão de
obra qualificada** — a diferença CCI × BCI isola o efeito de qualificação.

**A tentação, e por que ela está errada.** A cesta parece um coeficiente de
consumo — 200 h de mão de obra por 1,128 t de cimento, etc. **Não é.** A ENR
mantém as quantidades **constantes por construção**, justamente para que a
variação do índice reflete só preço. A cesta foi desenhada para *rastrear preço*,
não para representar o mix de uma obra real.

Consequência prática: a razão 200 h ÷ 1,128 t ≈ 177 homem-hora por tonelada de
cimento **não é** um dado de produtividade. É um artefato da construção do
índice. Usar isso como referência de consumo produziria erro grosseiro.

O que o ENR CCI **é**: um deflator de custo de construção americano, excelente e
com série muito longa. Use como `deflator`, nunca como `coeficiente_fisico`.

Por isso `F-162` está cadastrado com `entrega = indice_macro` e `licenca =
cite_only`, e a advertência está no campo `notas` do próprio registro — quem
consultar o CSV encontra o aviso sem precisar deste documento.

## ENR Top 400 — o que de fato serve

O **Top 400 Contractors** `F-165` publica **receita por segmento de mercado**
(transporte, água, energia, industrial). Isso é um **denominador setorial
americano**, comparável ao recorte por segmento da PAIC — e portanto o insumo
certo para intensidade, ao contrário dos índices. Também é `cite_only`: usar para
dimensionar, não para copiar tabela.

## Por que a comparação internacional ainda não saiu

Tentei fechar `mao_de_obra` para NAICS 237 e comparar com o CNAE 42 brasileiro
(4,633 pessoas-ano por R$ mi). Consegui o **numerador**: 1.097,1 mil postos em
NAICS 237 em 2022.

Faltou o **denominador**. As duas candidatas que apareceram não servem:

- *Value of construction put in place* (Census `F-016`) — obtive US$ 133,6 bi de
  rodovia em 2022, mas é **gasto por categoria de obra**, não receita de
  estabelecimento, e cobre só parte do escopo de NAICS 237.
- Receita de NAICS 237 do Economic Census — é a base correta (tabela
  **EC2223KOB**, *value of business done*), e não veio nos resultados de busca.

Cruzar emprego de NAICS 237 com gasto do VIP seria exatamente o erro de
denominador que este projeto existe para evitar — bases diferentes, escopos
diferentes. **Preferi não calcular.**

Com acesso à rede, é trabalho de minutos: abrir `data.census.gov`, tabela
`EC2223KOB` (value of business done por kind of business) ou `EC2223BASIC`
(summary statistics), recorte NAICS 237. Aí a linha sai com `metodo = direto`,
`tier = A` e `verificacao = fonte_primaria_lida` — qualidade que nenhuma linha
brasileira desta base tem hoje.

## A premissa de horas por ano

As linhas em `hh/R$ mi` da base usam **1.800 h/ano**, premissa Manta arbitrada e
declarada em `premissas`. O **BLS CES** `F-139` resolve isso do lado americano
com dado observado (tabelas B-7a/B-7b, horas semanais médias de *production and
nonsupervisory employees* na construção).

Do que consegui: **38,3 h/semana em Nova York** e **37,6 h/semana em Washington**
em 2024 — ambos estaduais. O valor nacional não veio, e **não vou extrapolar de
dois estados**.

Registro o que isso sugere sem transformar em dado: ~38 h/semana implica algo
próximo de 1.950–1.980 h/ano, acima das 1.800 h que adotei. Mas o regime de
trabalho americano não é o brasileiro, e a premissa brasileira tem de sair do
**CAGED/RAIS** (`F-008`, `F-009`), não do BLS.

## O melhor dado aberto do mundo para custo de obra

As **bid tabulations** de DOTs estaduais — Caltrans `F-145`, TxDOT `F-146`,
FDOT `F-147` — publicam **quantidade e preço unitário reais de milhares de
contratos**, item por item. Não existe equivalente brasileiro de escala e
abertura comparáveis.

Não entram nesta base (são preço, e a base é de consumo físico), mas são a
matéria-prima da **Fase 2 bottom-up**, e servem de contraprova para coeficiente
derivado de composição referencial como o SICRO. O **FHWA NHCCI** `F-143` é o
índice construído sobre esse dado.

## Fontes federais por setor prioritário

| Setor | Fonte americana |
|---|---|
| S6 Portos | USACE MII `F-118` e CWCCIS `F-148`; AAPA `F-158`. Dragagem é bem documentada pelo USACE |
| S7 Aeroportos | FAA `F-120`; ACRP via TRB `F-151` |
| S8 Saneamento | EPA CWNS `F-149` e DWINSA `F-150`; AWWA `F-160` |
| S9 Energia | EIA `F-152`; NREL ATB `F-112`; WECC e MISO (ver `03-FONTES-INTERNACIONAIS.md`) |
| S10 Barragens | USBR `F-119`; USACE `F-118`; **ASDSO `F-159`** — custo de reabilitação de barragem por porte, dado escasso em qualquer país |

## Índices comerciais — todos cite-only

ENR CCI/BCI/Cost Reports/Top Lists `F-162`–`F-166`, Turner Building Cost Index
`F-167`, Mortenson `F-168`, Rider Levett Bucknall `F-169`, Dodge `F-170`,
FMI `F-171`.

Vários publicam o valor de manchete abertamente, mas a base e a metodologia são
proprietárias. Como são todos `indice_macro` ou `custo_unitario_agregado`, o
validador já os impede de gerar linha de intensidade — a regra de licença é a
segunda barreira, não a única.
