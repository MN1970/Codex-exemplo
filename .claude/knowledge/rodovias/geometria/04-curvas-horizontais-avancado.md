# Geometria de Rodovias — Curvas Horizontais: Cálculos Avançados
## Clotóides, Raios Variáveis e Espirais Duplas

**Versão**: 1.0
**Data**: 2026-08-03
**Agente**: Manta 03-S1 (agente-infraestrutura)
**Prefixo RAG**: `rod:geom:clotoide`
**Complementa**: `01-elementos-geometricos.md`, `02-calculos-praticos.md`, `03-softwares-referencias.md`

> Este documento aprofunda o item 2.1.3 (Curvas de Transição) de
> `01-elementos-geometricos.md`. Os fundamentos de raio mínimo,
> superelevação básica e comprimento mínimo de clotóide **não são
> repetidos aqui** — apenas referenciados. O foco é o equacionamento
> completo da espiral de Euler (clotóide), a geometria de curvas
> compostas com raios variáveis e as configurações de espiral dupla
> (espiral-espiral e curvas reversas sem tangente).

---

## 1. Conceitos-chave

### 1.1 A clotóide como espiral de Euler

A clotóide (ou espiral de Euler/Cornu) é a curva de transição adotada
pela quase totalidade dos manuais de projeto geométrico rodoviário
(DNIT, AASHTO) porque sua curvatura varia **linearmente** com o
comprimento percorrido — o que produz uma variação de aceleração
centrípeta constante ao longo da transição (conforto ao dirigir) e
permite acoplar a rotação da superelevação de forma proporcional.

**Definição fundamental**:

```
R(l) × l = A²     (constante ao longo de toda a espiral)

Onde:
- l = comprimento percorrido a partir da origem da espiral (m)
- R(l) = raio de curvatura no ponto l (m)
- A = parâmetro da clotóide (m)
```

No ponto onde a espiral encontra a curva circular (l = Ls, R = R):

```
A² = R × Ls
A = √(R × Ls)
```

Esse é o mesmo parâmetro citado em `01-elementos-geometricos.md` —
aqui ele é tratado como **parâmetro de forma da família de curvas**,
não apenas como resultado de R e Ls fixos.

### 1.2 Nomenclatura dos pontos notáveis

```
TS  — Tangent to Spiral   (início da espiral, saindo da tangente)
SC  — Spiral to Curve     (fim da espiral / início do arco circular)
CS  — Curve to Spiral     (fim do arco circular / início da 2ª espiral)
ST  — Spiral to Tangent   (fim da 2ª espiral, entrando na tangente)
PI  — Ponto de Interseção das tangentes
PRC — Point of Reverse Curvature (ponto de curvatura reversa, usado
      em curvas em S)
```

Sequência padrão de uma curva com transição simétrica:
`TS → SC → CS → ST` (configuração **espiral-curva-espiral**, S-C-S).

### 1.3 Ângulo de espiral (θs)

```
θs = Ls / (2R)                    [radianos]
```

θs é o ângulo central varrido pela espiral, medido a partir da
tangente inicial. É o parâmetro que decide se ainda existe arco
circular entre as duas espirais (ver §1.6).

### 1.4 Coordenadas paramétricas da clotóide (série de Fresnel truncada)

Para qualquer ponto a uma distância `l` da origem da espiral (0 ≤ l ≤ Ls),
em relação ao sistema de eixos local (X = tangente, Y = perpendicular):

```
X(l) = l × [ 1 − θ²/10 + θ⁴/216 − θ⁶/9360 + ... ]
Y(l) = l × [ θ/3 − θ³/42 + θ⁵/1320 − ... ]

onde θ = l² / (2 × A²) = l / (2R_l),  com R_l = A²/l
```

No ponto final (l = Ls, θ = θs) essas expressões dão as coordenadas do
ponto **SC** — é a forma usada por DNIT/AASHTO para plantar a espiral
em campo (locação por coordenadas a cada estaca).

**Convergência**: a série truncada nos 2-3 primeiros termos já atende
à precisão de projeto (erro < 1 mm) para θs < 30°, faixa em que a
quase totalidade das clotóides rodoviárias opera. Para θs > 45°
(espirais muito "enroladas", raras em rodovias — mais comuns em
ferrovias ou rotatórias de raio muito pequeno) deve-se usar mais
termos ou integração numérica direta das integrais de Fresnel.

### 1.5 Deslocamento do arco circular (p, k)

A introdução da espiral "empurra" o arco circular para dentro em
relação à tangente. Esse deslocamento é quantificado por:

```
p = Y(Ls) − R × (1 − cos θs)     (afastamento radial / "shift")
k = X(Ls) − R × sen θs           (abscissa do centro deslocado)
```

`p` e `k` são usados para calcular a geometria completa da curva
composta espiral-círculo-espiral:

```
T (tangente total, do PI ao TS/ST) = (R + p) × tan(Δ/2) + k
E (distância externa, do PI ao ponto médio do arco) = (R + p) / cos(Δ/2) − R
Lc (comprimento do arco circular restante) = R × (Δ − 2θs)
L_total = 2 × Ls + Lc
```

Onde **Δ** é o ângulo de deflexão total no PI (mesmo ângulo central
usado nos exemplos de `02-calculos-praticos.md`).

### 1.6 Condição de existência do arco circular

```
SE  Δ > 2 × θs   →  existe arco circular (curva S-C-S clássica)
SE  Δ = 2 × θs   →  as duas espirais se encontram exatamente no ponto
                     de raio R — não há arco circular (curva "espiral-
                     espiral" ou S-S)
SE  Δ < 2 × θs   →  a espiral dimensionada para Ls não cabe no ângulo
                     disponível — é preciso reduzir Ls (e portanto A)
                     até que 2θs = Δ, redimensionando a curva como
                     espiral-espiral com raio de encontro R' > R
```

Essa condição (`Lc = R(Δ − 2θs) ≥ 0`) é a checagem central de todo
projeto de clotóide e deve ser a primeira verificação de qualquer
script de validação (§5).

### 1.7 Raios variáveis — curva composta (compound curve)

Uma **curva composta** é formada por dois (ou mais) arcos circulares
de raios diferentes, no mesmo sentido de curvatura, conectados
diretamente ou por uma clotóide de transição. É o mecanismo padrão
para reduzir progressivamente o raio (e a velocidade) em ramais de
interseção, alças de retorno e acessos, sem produzir um "salto" de
curvatura perceptível ao condutor.

**Regra prática de proporção entre raios** (AASHTO *A Policy on
Geometric Design of Highways and Streets* — "Green Book"; não há
norma DNIT específica sobre razão entre raios de curva composta):

```
Rodovia principal (pista aberta):  R1 / R2 ≤ 1.5
Ramais / alças de interseção:      R1 / R2 ≤ 2.0  (até 3.0 em casos extremos)

Onde R1 = raio do arco mais suave (anterior)
     R2 = raio do arco mais fechado (posterior)
```

Razões acima desse limite geram uma transição de curvatura brusca
demais para a percepção do condutor mesmo com clotóide intermediária
bem dimensionada — ver riscos em §4.

### 1.8 Espiral dupla — as duas configurações possíveis

O termo "espiral dupla" é usado no setor rodoviário para **duas
situações distintas**, que este documento trata separadamente para
evitar ambiguidade:

**(a) Espiral-espiral (S-S), sem arco circular central**
Caso-limite do §1.6 quando `Δ = 2θs`. Usada em curvas de pequena
deflexão onde inserir um arco circular mínimo obrigaria a um raio
maior que o desejável, ou em ramais de baixa velocidade onde a
curvatura continuamente variável melhora a trajetória natural do
veículo.

**(b) Curva reversa com espirais (S-curve / "double spiral reverse")**
Duas curvas circulares de **sentidos opostos** (uma para a direita,
outra para a esquerda), conectadas por espirais **sem trecho de
tangente reta entre elas**. O ponto de encontro é o PRC. Cada ramo
(TS-SC-CS-ST) é calculado de forma independente pelas fórmulas de
§1.3-1.5, com seu próprio R, Ls, A — mas a superelevação deve
transicionar de e₁ (inclinada para um lado) até e₂ (inclinada para o
lado oposto) passando por e=0 (seção plana) exatamente na vizinhança
do PRC, sem trecho de tangente para "descansar" essa transição.

Esta é a configuração de maior exigência de projeto entre as
abordadas neste documento — ver §3.3 e §4.

---

## 2. Exemplos práticos (cálculos numéricos)

Todos os exemplos abaixo foram recalculados com a série de Fresnel
truncada em 3 termos (precisão suficiente para θs < 30°, ver §1.4) e
conferidos numericamente. Valores em metros e graus decimais, salvo
indicação contrária.

### 2.1 Caso A — Espiral-Curva-Espiral (S-C-S), rodovia federal Vd=100 km/h

Continuação do Caso 1 de `02-calculos-praticos.md` (R = 350 m, Ls =
110 m), agora com o ângulo de deflexão Δ = 42°30′ = 42.5° explicitado
para fechar a geometria completa da curva.

**Dados de entrada**:
```
R  = 350 m
Ls = 110 m   (> L_mín = 102.9 m calculado em 02-calculos-praticos.md ✓)
Δ  = 42.5°
A  = √(350 × 110) = 196.2 m
```

**Passo 1 — Ângulo de espiral**:
```
θs = Ls / (2R) = 110 / 700 = 0.15714 rad = 9.004°
```

**Passo 2 — Condição de existência do arco circular**:
```
2θs = 18.007° < Δ = 42.5°  →  existe arco circular (S-C-S válida)
```

**Passo 3 — Coordenadas do ponto SC (fim da 1ª espiral)**:
```
X = 109.73 m
Y = 5.752 m
```

**Passo 4 — Deslocamento do arco (p, k)**:
```
p = 1.439 m
k = 54.955 m
```

**Passo 5 — Geometria completa**:
```
Lc (arco circular)     = 350 × (0.74176 − 0.31429) = 149.62 m
T (tangente total)     = (350 + 1.439) × tan(21.25°) + 54.955 = 191.62 m
E (distância externa)  = (350 + 1.439) / cos(21.25°) − 350 = 27.08 m
L_total (curva completa) = 2×110 + 149.62 = 369.62 m
```

**Passo 6 — Estaqueamento** (adotando PI na estaca 10+000, Vd=100 km/h):
```
TS = PI − T          = 10+000 − 191.62 = 9+808.38
SC = TS + Ls          = 9+808.38 + 110  = 9+918.38
CS = SC + Lc           = 9+918.38 + 149.62 = 10+068.00
ST = CS + Ls           = 10+068.00 + 110  = 10+178.00
```

**Verificação da razão A/R** (regra prática internacional para boa
aparência visual da clotóide, ver §5.4): `A = 196.2` está no intervalo
recomendado `R/3 (116.7) ≤ A ≤ R (350)` → **OK**.

### 2.2 Caso B — Espiral-Espiral (S-S), sem arco circular

Interseção com deflexão pequena, Vd = 60 km/h (ramal de acesso),
R = 220 m, Δ = 15°.

**Passo 1 — Testar Ls mínima padrão contra a condição de existência**:
```
L_mín (fórmula padrão) = 0.036 × 60³ / 220 = 35.3 m
θs para Ls=90m (como no Caso 2 de 02-calculos-praticos.md) = 11.72°
2θs = 23.44° > Δ = 15°  →  NÃO existe arco circular com esse Ls
```
A espiral de 90 m "não cabe" nos 15° de deflexão disponíveis — é
preciso redimensionar como espiral-espiral.

**Passo 2 — Redimensionar como S-S**:
```
θs_max = Δ/2 = 7.5° = 0.13090 rad
Ls (necessária) = 2 × R × θs_max = 2 × 220 × 0.13090 = 57.60 m
A = √(220 × 57.60) = 112.57 m
```

**Passo 3 — Geometria resultante (Lc = 0 por definição)**:
```
T = 57.83 m
E = 2.53 m
L_total = 2 × 57.60 = 115.19 m
```

**Nota de projeto**: como Ls caiu de 90 m para 57.6 m, é obrigatório
reconferir o comprimento mínimo de clotóide para a velocidade real do
ramal (não da rodovia principal) e a taxa de variação de
superelevação (§3 de `01-elementos-geometricos.md`), pois um ramal de
acesso normalmente opera com Vd de 40-60 km/h, não 100 km/h.

### 2.3 Caso C — Curva composta de raios variáveis (alça de interseção)

Alça de retorno trevo, três arcos sucessivos R1 > R2 > R3, mesma
mão de direção, ligados por clotóides:

```
R1 = 180 m  (entrada, vindo da rodovia principal)
R2 = 100 m  (arco intermediário)
R3 = 45 m   (arco de raio mínimo, seção mais fechada do laço)
```

**Verificação de proporção entre arcos sucessivos** (limite AASHTO
para ramais, R1/R2 ≤ 2.0):
```
R1/R2 = 180/100 = 1.80  → dentro do limite (≤ 2.0) ✓
R2/R3 = 100/45  = 2.22  → FORA do limite (> 2.0) ✗
```

**Ação corretiva**: a transição R2→R3 excede a razão recomendada.
Duas soluções típicas:
1. Inserir um raio intermediário R2b ≈ 65-70 m entre R2 e R3
   (R2/R2b ≈ 1.5, R2b/R3 ≈ 1.5), ou
2. Alongar a clotóide de transição entre R2 e R3 para compensar
   parcialmente a percepção de salto de curvatura (mitiga, não
   elimina o problema de fundo).

A opção (1) é preferível sempre que o espaço físico da alça permitir.

### 2.4 Caso D — Curva reversa com espirais (S-curve), sem tangente

Retorno em desnível, Vd = 50 km/h, arco 1 à direita (R1 = 130 m),
arco 2 à esquerda (R2 = 150 m), sem tangente entre eles.

```
Arco 1 (direita):
  e1_máx = 8%  (padrão DNIT para R baixo)
  Ls1 (mín, V=50) = 0.036 × 50³/130 = 34.6 m → adotar Ls1 = 40 m
  θs1 = 40/(2×130) = 0.1538 rad = 8.81°
  A1 = √(130×40) = 72.1 m

Arco 2 (esquerda):
  e2_máx = 8%
  Ls2 (mín, V=50) = 0.036 × 50³/150 = 30.0 m → adotar Ls2 = 40 m
  θs2 = 40/(2×150) = 0.1333 rad = 7.64°
  A2 = √(150×40) = 77.5 m
```

**Verificação crítica no PRC** — transição de superelevação:
```
No arco 1, a seção termina com e1 = +8% (inclinada para dentro do
arco 1). No arco 2, a seção começa com e2 = −8% (inclinada para o
lado oposto). A variação total no PRC é:

Δe_PRC = e1 − (−e2) = 8% − (−8%) = 16 pontos percentuais

Comprimento necessário para essa transição (mesma fórmula de
01-elementos-geometricos.md §2.1, com a = 7.2 m e taxa 1/150):

L_trans_PRC = (0.16 × 7.2) / (1/150) = 1.152 / 0.00667 = 172.8 m
```

Como não há tangente entre os arcos, essa transição de 172,8 m
**precisa caber dentro dos 80 m disponíveis** (Ls1 + Ls2 = 40+40 = 80
m) — o que **não cabe**. Isso é um alerta de projeto real e recorrente
em curvas reversas: o comprimento de espiral dimensionado apenas pelo
critério dinâmico (L_mín) é insuficiente para a transição de
superelevação quando não há tangente de alívio.

**Ação corretiva**: aumentar Ls1 e Ls2 até que `Ls1 + Ls2 ≥
L_trans_PRC`, ou reduzir e_máx adotado em um dos arcos, ou (melhor
prática) recalcular a partir da taxa de variação de superelevação
como variável de projeto e derivar Ls mínimo por esse critério, não
pelo critério dinâmico isolado — ver §5.5.

---

## 3. Tabelas de referência (parâmetros normalizados DNIT/AASHTO)

### 3.1 Comprimento mínimo de clotóide L_mín = 0.036·V³/R (m)

| R (m) \ V (km/h) | 60 | 80 | 100 | 120 |
|---|---|---|---|---|
| 150 | 51.8 | 122.9 | 240.0 | 414.7 |
| 220 | 35.3 | 83.8 | 163.6 | 282.5 |
| 350 | 22.2 | 52.7 | 102.9 | 177.7 |
| 500 | 15.6 | 36.9 | 72.0 | 124.4 |
| 800 | 9.7 | 23.0 | 45.0 | 77.8 |

### 3.2 Parâmetro A recomendado (regra prática internacional)

Não há tabela DNIT específica para o intervalo recomendado de A; a
prática consolidada em manuais internacionais (AASHTO Green Book,
literatura de projeto geométrico) recomenda:

```
R/3  ≤  A  ≤  R
```

| R (m) | A_mín (R/3) | A_máx (R) |
|---|---|---|
| 150 | 50.0 | 150.0 |
| 220 | 73.3 | 220.0 |
| 350 | 116.7 | 350.0 |
| 500 | 166.7 | 500.0 |

A abaixo de R/3 → clotóide "curta demais", transição perceptível
como quase abrupta. A acima de R → clotóide "longa demais" para o
raio, aparência de traçado sinuoso sem ganho de conforto proporcional.

### 3.3 Razão máxima entre raios de curva composta (AASHTO)

| Situação | Razão R_maior / R_menor máxima |
|---|---|
| Rodovia principal, pista aberta | 1.5 |
| Ramais e alças de interseção | 2.0 |
| Caso extremo (avaliação caso a caso) | 3.0 |

### 3.4 Ângulo de espiral θs — faixa usual em projeto rodoviário

| Faixa de θs | Situação típica |
|---|---|
| < 15° | Espiral curta, S-C-S com arco circular longo — mais comum |
| 15°–30° | Espiral longa em relação ao arco — verificar existência do arco (§1.6) |
| ≥ Δ/2 | Limite de espiral-espiral (S-S), Lc = 0 |
| > 30-45° | Raro em rodovias; comum em geometrias de raio muito pequeno (rotatórias, pátios) — usar mais termos da série de Fresnel |

### 3.5 Superelevação máxima por classe (referência DNIT, já citada em `01-elementos-geometricos.md`)

| Classe | e_máx |
|---|---|
| BR (relevo plano/ondulado) | 8% |
| BR (relevo montanhoso) / ramais | 10% |
| Rotatórias e alças de baixa velocidade | pode-se adotar e negativo/zero por segurança operacional |

---

## 4. Casos de uso, quando aplicar, limitações e riscos

### 4.1 Espiral simples (S-C-S) — caso padrão

**Quando aplicar**: toda curva horizontal de rodovia classe I/II com
Vd ≥ 60 km/h e R abaixo do limiar em que a transição se torna
imperceptível (na prática, sempre que R < ~2 a 3× o raio mínimo da
classe). É a configuração-padrão coberta em `01` e `02`.

**Limitação**: exige espaço para dois trechos de transição além do
arco circular; em interseções compactas ou faixas de domínio
restritas pode não haver espaço suficiente — nesse caso, avaliar S-S
(§4.2) ou reduzir Ls ao mínimo técnico (nunca abaixo de L_mín).

### 4.2 Espiral-espiral (S-S)

**Quando aplicar**: deflexões pequenas (Δ tipicamente < 20-25°) em
ramais de baixa velocidade, onde inserir arco circular obrigaria
raio maior que o desejável ou espaço insuficiente. Também usada
deliberadamente em desenhos de "curvatura continuamente variável"
buscando trajetória mais natural em ramais de interseções tipo trevo.

**Risco**: como não há arco circular de raio constante, **não existe
"raio de projeto" único da curva** — o raio mínimo efetivo ocorre no
ponto de encontro das duas espirais (l = Ls, R = A²/Ls). Todo cálculo
de raio mínimo (§1 de `01-elementos-geometricos.md`) deve ser
verificado nesse ponto, não em um raio nominal "desejado".

### 4.3 Curva composta de raios variáveis

**Quando aplicar**: alças de interseção, ramais de saída/entrada,
rotatórias de acesso — qualquer situação em que o veículo precisa
reduzir de velocidade de forma progressiva ao longo de uma sequência
de curvas no mesmo sentido.

**Risco principal**: violação da razão R_maior/R_menor (§3.3) produz
"efeito surpresa" — o condutor entra na curva mais fechada sem
percepção prévia adequada da redução de raio, aumentando risco de
saída de pista. Esse é um dos padrões de acidente mais documentados
em ramais de interseções trevo mal dimensionadas.

**Limitação prática**: cada arco da composta precisa, individualmente,
atender R_mín para a velocidade operacional esperada naquele ponto
específico da alça (não a Vd da rodovia principal) — isso exige um
perfil de velocidade de projeto ao longo da alça, não um valor único.

### 4.4 Curva reversa com espirais (S-curve sem tangente)

**Quando aplicar**: retornos em desnível, ramais de interseções
tipo diamante/trombeta, acessos onde não há espaço para tangente
entre duas curvas de sentidos opostos.

**Risco principal (já demonstrado no Caso D, §2.4)**: o comprimento
de espiral dimensionado apenas pelo critério dinâmico L_mín
frequentemente **não é suficiente** para acomodar a transição de
superelevação completa (que precisa passar de +e para −e sem trecho
de alívio). Subdimensionar essa transição resulta em:
- Seção com drenagem inadequada perto do PRC (declividade transversal
  próxima de zero em trecho sem declividade longitudinal suficiente
  → empoçamento);
- Variação de força centrípeta perceptível como "solavanco" lateral
  no PRC, mesmo com a geometria em planta matematicamente contínua;
- Necessidade de reduzir a Vd operacional da curva reversa em relação
  à Vd nominal da via — deve ser sinalizada.

**Limitação**: o dimensionamento de Ls em curva reversa **deve ser
verificado pelos dois critérios** (dinâmico E superelevação), sempre
adotando o maior valor resultante — nunca apenas o critério dinâmico
tradicional de L_mín = 0.036V³/R.

### 4.5 Risco transversal a todas as configurações — consistência de traçado

Independentemente da configuração escolhida, o projetista deve
verificar a **Curvature Diagram** (diagrama de curvatura acumulada ao
longo do eixo, disponível em MX Road/Civil 3D — ver
`03-softwares-referencias.md` §1.1) para garantir que não haja
descontinuidades de curvatura entre elementos consecutivos além das
proporções recomendadas neste documento.

---

## 5. Scripts de validação (Python)

Implementação de referência para verificação automática dos casos
descritos em §1-4. Depende apenas de `math` (biblioteca padrão).

```python
"""
validador_curvas_avancadas.py
Validação de clotóides, curvas compostas e espirais duplas
conforme DNIT IPR-706 / AASHTO Green Book.
Agente: Manta 03-S1 — prefixo RAG rod:geom:clotoide
"""

import math


def parametro_A(R: float, Ls: float) -> float:
    """A² = R × Ls"""
    return math.sqrt(R * Ls)


def comprimento_minimo_clotoide(V: float, R: float) -> float:
    """L_mín = 0.036 × V³ / R  (critério dinâmico, DNIT/AASHTO)"""
    return 0.036 * V**3 / R


def angulo_espiral(Ls: float, R: float) -> float:
    """θs em radianos"""
    return Ls / (2 * R)


def coordenadas_espiral(l: float, R: float, Ls: float) -> tuple:
    """
    X(l), Y(l) via série de Fresnel truncada (3 termos).
    Válido para θ < ~30°; para ângulos maiores, aumentar termos
    ou integrar numericamente as integrais de Fresnel.
    """
    A2 = R * Ls  # = A²
    theta = l**2 / (2 * A2)
    X = l * (1 - theta**2 / 10 + theta**4 / 216)
    Y = l * (theta / 3 - theta**3 / 42 + theta**5 / 1320)
    return X, Y


def deslocamento_p_k(R: float, Ls: float) -> tuple:
    """Retorna (p, k) — deslocamento do arco circular."""
    theta_s = angulo_espiral(Ls, R)
    X, Y = coordenadas_espiral(Ls, R, Ls)
    p = Y - R * (1 - math.cos(theta_s))
    k = X - R * math.sin(theta_s)
    return p, k


def geometria_curva_transicao(R: float, Ls: float, delta_graus: float) -> dict:
    """
    Geometria completa de uma curva S-C-S (ou S-S, se Lc <= 0).
    delta_graus = ângulo de deflexão total no PI.
    """
    theta_s = angulo_espiral(Ls, R)
    delta = math.radians(delta_graus)
    p, k = deslocamento_p_k(R, Ls)

    Lc = R * (delta - 2 * theta_s)
    modo = "S-C-S" if Lc > 1e-6 else "S-S (sem arco circular)"
    Lc = max(Lc, 0.0)

    T = (R + p) * math.tan(delta / 2) + k
    E = (R + p) / math.cos(delta / 2) - R
    A = parametro_A(R, Ls)

    return {
        "modo": modo,
        "theta_s_graus": math.degrees(theta_s),
        "p": p, "k": k,
        "Lc": Lc, "T": T, "E": E, "A": A,
        "L_total": 2 * Ls + Lc,
    }


def redimensionar_espiral_espiral(R: float, delta_graus: float) -> float:
    """
    Quando 2*theta_s > delta com o Ls desejado, recalcula o Ls que
    faz a curva se tornar exatamente espiral-espiral (Lc = 0).
    """
    theta_s_max = math.radians(delta_graus) / 2
    return 2 * R * theta_s_max


def verificar_parametro_A(R: float, Ls: float) -> dict:
    """Checa A contra a faixa prática R/3 <= A <= R (regra internacional,
    não há tabela DNIT específica — ver §3.2 do documento)."""
    A = parametro_A(R, Ls)
    a_min, a_max = R / 3, R
    return {"A": A, "faixa_ok": a_min <= A <= a_max,
            "A_min_recomendado": a_min, "A_max_recomendado": a_max}


def verificar_razao_raios_compostos(R_maior: float, R_menor: float,
                                     contexto: str = "ramal") -> dict:
    """
    contexto = "pista_aberta" (limite 1.5) ou "ramal" (limite 2.0).
    AASHTO Green Book — sem norma DNIT específica equivalente.
    """
    razao = R_maior / R_menor
    limite = 1.5 if contexto == "pista_aberta" else 2.0
    return {"razao": razao, "limite": limite, "ok": razao <= limite}


def comprimento_transicao_superelevacao(e: float, largura_pav: float,
                                         taxa_max: float = 1 / 150) -> float:
    """L_trans = (e × a) / (Δe/ΔL) — mesma fórmula de 01-elementos-geometricos.md"""
    return (e * largura_pav) / taxa_max


def validar_curva_reversa(R1: float, Ls1: float, e1: float,
                           R2: float, Ls2: float, e2: float,
                           largura_pav: float,
                           taxa_max: float = 1 / 150) -> dict:
    """
    Verifica se a soma das espirais (sem tangente entre elas) é
    suficiente para a transição completa de superelevação no PRC.
    """
    delta_e = e1 + e2  # de +e1 até -e2, variação total
    L_trans_necessario = comprimento_transicao_superelevacao(
        delta_e, largura_pav, taxa_max)
    L_disponivel = Ls1 + Ls2
    return {
        "L_trans_necessario": L_trans_necessario,
        "L_disponivel": L_disponivel,
        "ok": L_disponivel >= L_trans_necessario,
        "deficit": max(0.0, L_trans_necessario - L_disponivel),
    }


def relatorio_validacao(V: float, R: float, Ls: float, delta_graus: float,
                         e: float, largura_pav: float,
                         contexto_composta: str = None,
                         R_par: float = None) -> None:
    """Relatório-texto agregando todas as checagens desta curva."""
    print(f"--- Validação de curva: R={R}m, Ls={Ls}m, Δ={delta_graus}°, V={V}km/h ---")

    Lmin = comprimento_minimo_clotoide(V, R)
    print(f"L_mín (dinâmico) = {Lmin:.1f} m  |  Ls adotado = {Ls} m  "
          f"| {'OK' if Ls >= Lmin else 'FALHA — Ls insuficiente'}")

    a_check = verificar_parametro_A(R, Ls)
    print(f"A = {a_check['A']:.1f} m  (faixa recomendada "
          f"{a_check['A_min_recomendado']:.1f}–{a_check['A_max_recomendado']:.1f} m)  "
          f"| {'OK' if a_check['faixa_ok'] else 'ATENÇÃO — fora da faixa'}")

    geo = geometria_curva_transicao(R, Ls, delta_graus)
    print(f"Modo: {geo['modo']}  |  θs = {geo['theta_s_graus']:.2f}°  "
          f"|  Lc = {geo['Lc']:.1f} m  |  T = {geo['T']:.1f} m  |  E = {geo['E']:.1f} m")

    if geo["modo"].startswith("S-S"):
        Ls_ajustado = redimensionar_espiral_espiral(R, delta_graus)
        print(f"  → Redimensionar Ls para {Ls_ajustado:.1f} m para fechar "
              f"a geometria espiral-espiral exatamente.")

    if contexto_composta and R_par:
        maior, menor = max(R, R_par), min(R, R_par)
        razao = verificar_razao_raios_compostos(maior, menor, contexto_composta)
        print(f"Razão R_maior/R_menor = {razao['razao']:.2f} "
              f"(limite {razao['limite']}) "
              f"| {'OK' if razao['ok'] else 'FALHA — reduzir salto de curvatura'}")


if __name__ == "__main__":
    # Reproduz o Caso A (§2.1) deste documento
    relatorio_validacao(V=100, R=350, Ls=110, delta_graus=42.5,
                        e=0.075, largura_pav=7.2)

    print()
    # Reproduz o Caso D (§2.4) — curva reversa
    reversa = validar_curva_reversa(R1=130, Ls1=40, e1=0.08,
                                     R2=150, Ls2=40, e2=0.08,
                                     largura_pav=7.2)
    print("--- Validação de curva reversa (S-curve) ---")
    print(reversa)
```

### 5.1 Pseudocódigo de decisão (fluxo resumido para intake do agente)

```
ENTRADA: R, Ls (ou V para calcular Ls mínimo), Δ, tipo_de_curva

1. Calcular θs = Ls / (2R)
2. SE 2θs < Δ:
     → curva S-C-S padrão; calcular Lc, T, E, L_total (§1.5)
   SENÃO:
     → recalcular Ls para condição S-S (θs = Δ/2, §5 redimensionar_espiral_espiral)
     → avisar usuário que não há trecho circular
3. Verificar Ls ≥ L_mín(V, R) [critério dinâmico]
4. Verificar A dentro de R/3 ≤ A ≤ R [regra prática]
5. SE curva composta (múltiplos raios):
     → verificar razão R_maior/R_menor ≤ 1.5 (pista aberta) ou ≤ 2.0 (ramal)
6. SE curva reversa (sem tangente entre arcos opostos):
     → calcular L_trans_necessário (transição de superelevação e1→-e2)
     → verificar Ls1 + Ls2 ≥ L_trans_necessário
     → SE falhar: aumentar Ls1/Ls2 ou reduzir e_máx adotado
7. Emitir relatório com estaqueamento (TS, SC, CS, ST) e status de cada checagem
```

---

## 6. Referências (normas citadas)

| Referência | Título / Escopo | Uso neste documento |
|---|---|---|
| **DNIT IPR-706** (1999) | Manual de Projeto Geométrico de Rodovias Rurais | Fórmulas de comprimento mínimo de clotóide, superelevação, base de todo o capítulo |
| **DNIT IPR-726** | Diretrizes Básicas para Estudos e Projetos Rodoviários | Enquadramento de fase de projeto e escopo geométrico |
| **AASHTO — *A Policy on Geometric Design of Highways and Streets*** (Green Book) | Referência internacional de projeto geométrico | Fórmulas de espiral (X, Y, p, k, T, E), razão entre raios de curva composta, regra prática de A/R — **usada por não haver equivalente DNIT específico para esses itens** |
| **NBR 15486** | Segurança no trânsito — distâncias de visibilidade (citada em `rodovias` SKILL.md, D-02) | Não trata de clotóides — mencionada apenas para deixar explícito que a geometria de espiral **não é objeto de NBR ABNT específica** |
| SICRO (DNIT) | Sistema de custos de obras | Fora do escopo deste documento (ver `02-calculos-praticos.md` §4) |

**Nota de rastreabilidade importante**: não existe, até a data deste
documento, uma norma ABNT NBR dedicada ao equacionamento de clotóides
ou curvas compostas. O equacionamento apresentado (§1) é o padrão
internacional (AASHTO), historicamente incorporado pela metodologia
do DNIT IPR-706. Qualquer citação futura de uma "NBR de clotóides" em
laudos ou pareceres deve ser tratada como suspeita e verificada antes
do uso (ver skill `aluci-guard`).

---

## 7. Testes sugeridos (validação deste conteúdo)

### 7.1 Testes de recuperação (RAG)

Perguntas que este documento deve responder corretamente quando
consultado via busca semântica (prefixo `rod:geom:clotoide`):

1. "Qual o parâmetro A de uma clotóide com R=350m e Ls=110m?"
   → esperado: A ≈ 196.2 m (§2.1, §5).
2. "Quando uma curva não tem arco circular entre as espirais?"
   → esperado: explicação da condição Δ = 2θs (§1.6) + exemplo do Caso B (§2.2).
3. "Qual a razão máxima entre raios de uma curva composta em um ramal de interseção?"
   → esperado: 2.0 (até 3.0 em casos extremos), fonte AASHTO (§3.3, §6).
4. "Como dimensionar a transição de superelevação em uma curva reversa sem tangente?"
   → esperado: cálculo do Δe no PRC e comparação com Ls1+Ls2 (§2.4, §4.4).
5. "Existe NBR para clotóide?"
   → esperado: resposta negativa explícita, com referência a DNIT IPR-706/AASHTO (§6).

### 7.2 Testes numéricos (executar o script de §5)

```python
# Teste 1 — parâmetro A do Caso A
assert abs(parametro_A(350, 110) - 196.21) < 0.1

# Teste 2 — condição espiral-espiral do Caso B
theta_s_90 = angulo_espiral(90, 220)
assert 2 * math.degrees(theta_s_90) > 15  # confirma que Ls=90 não cabe em Δ=15°

Ls_ajustado = redimensionar_espiral_espiral(220, 15)
assert abs(Ls_ajustado - 57.6) < 0.5

# Teste 3 — razão de raios do Caso C (deve falhar entre R2 e R3)
r23 = verificar_razao_raios_compostos(100, 45, contexto="ramal")
assert r23["ok"] is False

# Teste 4 — déficit de transição de superelevação do Caso D (deve falhar)
reversa = validar_curva_reversa(130, 40, 0.08, 150, 40, 0.08, 7.2)
assert reversa["ok"] is False
assert reversa["deficit"] > 0
```

### 7.3 Teste de consistência cruzada com os documentos anteriores

- [ ] O valor de L_mín para V=100/R=350 neste documento (102.9 m, §3.1)
      é idêntico ao calculado em `02-calculos-praticos.md` (Caso 1).
- [ ] O valor de A=140.7 m para R=220/Ls=90 (Caso 2 de `02-calculos-praticos.md`)
      é reproduzido exatamente pela função `parametro_A` deste documento.
- [ ] Nenhuma fórmula deste documento contradiz as fórmulas básicas de
      `01-elementos-geometricos.md` — este documento apenas estende.

### 7.4 Teste de revisão humana (gate obrigatório)

Antes de este documento ser referenciado em qualquer laudo, claim ou
orçamento real (não apenas como base de conhecimento RAG), submeter à
skill `aluci-guard` para auditoria de referências normativas e, em
seguida, a aprovação humana conforme o checklist de deploy do
`CLAUDE.md` master (item "Gate humano: aprovação MN antes de merge").

---

## Checklist de aplicação — curvas avançadas

- [ ] Determinado se a curva é S-C-S, S-S, composta ou reversa
- [ ] θs calculado e condição de existência do arco circular verificada
- [ ] Ls ≥ L_mín (critério dinâmico) **e** Ls ≥ L_trans (critério de
      superelevação, obrigatório em curvas reversas)
- [ ] Parâmetro A dentro da faixa prática recomendada (R/3 a R)
- [ ] Se curva composta: razão entre raios sucessivos dentro do limite
      (1.5 pista aberta / 2.0 ramal)
- [ ] Estaqueamento (TS, SC, CS, ST, PRC) calculado e conferido
- [ ] Curvature Diagram revisado em MX Road/Civil 3D sem
      descontinuidades anormais
- [ ] Referências normativas conferidas (nenhuma NBR fabricada para
      clotóide/curva composta — usar DNIT IPR-706 e AASHTO Green Book)
