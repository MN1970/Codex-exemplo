# Balanço de massas rodoviário — conceito e aplicação

Referência técnica Manta Associados · Manta 03-S1 (Rodovias) ·
disciplina D04 — Terraplenagem.

Parte 1 estabelece o conceito. Parte 2 aplica o conceito a um caso real
do acervo (BR-365/MG — Duplicação, EPR) e registra os pontos de
verificação encontrados.

---

## Parte 1 — Conceito

### 1.1 Definição

Balanço de massas é o estudo da **distribuição dos volumes de terra ao
longo do eixo**, confrontando o que o greide *produz* (cortes) com o que
ele *consome* (aterros), para decidir de onde sai e para onde vai cada
metro cúbico ao menor custo total de escavação + transporte +
compactação.

Não é cálculo de volume. Volume é quantitativo; balanço é **logística de
terra**. O produto do balanço não é "quantos m³", é "qual m³ vai para
qual aterro, por qual distância, a que custo".

### 1.2 Insumos

| Item | Origem |
|---|---|
| Volumes de corte/aterro por estaca | seções transversais × distância (média das áreas ou prismoidal) |
| Classificação do material | 1ª, 2ª e 3ª categoria — sondagens e inspeção |
| Fator de homogeneização (Fh) | densidade natural ÷ densidade compactada |
| Qualidade | ISC/expansão para corpo, camada final e regularização do subleito |

O **fator de homogeneização** é a fonte de erro mais comum. 1 m³ medido
no corte não vira 1 m³ de aterro: solo compacta, rocha empola. Balanço
feito em volume geométrico bruto está errado por construção.

Distinção que importa em auditoria: **Fh** é grandeza física, derivada de
densidades medidas em ensaio. Quando não há ensaio, o que se usa é um
**FC (fator de conversão) arbitrado** — número de projeto, não medida.
Chamar um FC arbitrado de Fh mascara a ausência de base experimental.

### 1.3 Diagrama de Brückner

No eixo x, as estacas; no eixo y, o **somatório acumulado** dos volumes
homogeneizados (corte positivo, aterro negativo).

- Trecho **ascendente = corte**; **descendente = aterro**.
- **Máximos e mínimos** = pontos de passagem corte↔aterro.
- Uma **horizontal (linha de compensação)** que corta a curva em dois
  pontos delimita trecho onde corte = aterro → volume **compensado**.
- A **área** entre a curva e a linha de compensação é o **momento de
  transporte** (m³·km) — proporcional ao custo de transportar.
- **DMT = momento ÷ volume compensado.**
- Curva **acima** da linha → transporte no sentido crescente das
  estacas; **abaixo** → sentido contrário.

### 1.4 Empréstimo, bota-fora e a distância econômica

Quando a compensação longitudinal não fecha:

- **Aterro > corte** → **empréstimo** (lateral ou jazida concentrada).
- **Corte > aterro** → **bota-fora / DME**, com licenciamento próprio.

A decisão é econômica, não geométrica. Existe uma **distância econômica
de transporte (DET)**: o ponto em que transportar 1 m³ longitudinalmente
custa o mesmo que escavar em empréstimo próximo e mandar o excedente
para bota-fora. Além da DET, compensar longitudinalmente destrói valor.

### 1.5 Barreiras — por que empréstimo e bota-fora coexistem

Um projeto pode apresentar, **simultaneamente**, empréstimo e bota-fora
em volume relevante, e isso não é erro. Ocorre quando o corredor tem
**barreiras** que impedem a transferência de material entre trechos:

- OAEs (não se transporta terra sobre ponte em construção);
- travessias, lacunas de projeto, interferências;
- restrições ambientais, de faixa ou de fases de obra.

Nesse caso o balanço deixa de ser um problema único e vira **N problemas
independentes**, um por trecho entre barreiras. O saldo *líquido* global
pode ser pequeno enquanto os movimentos *brutos* são grandes — e é o
bruto que se paga.

Corolário prático: sempre reportar o saldo líquido **e** os movimentos
brutos por trecho. Só o líquido esconde o custo; só o bruto esconde a
oportunidade de remover a barreira.

### 1.6 Restrições que quebram o balanço "de papel"

- **Qualidade** — 3ª categoria ou solo expansivo não serve para camada
  final, mesmo geometricamente disponível.
- **Umidade e sazonalidade** — solo acima da umidade ótima não compacta.
- **Sequenciamento** — o corte precisa existir *antes* do aterro que
  alimenta. Balanço geometricamente perfeito e cronologicamente
  impossível vira bota-espera e transporte duplo.
- **Faixa de domínio, desapropriação e licenças** de jazidas e DMEs.

Essas quatro são a origem mais frequente de pleito. Quando o balanço
executado diverge do de projeto, a diferença de momento (m³·km) é a base
quantitativa do reequilíbrio.

### 1.7 Produtos

- Quadro de Orientação de Terraplenagem (QOT) / distribuição de massas
- Diagrama de Brückner com linhas de compensação
- Volumes por categoria + DMTs por faixa
- Orçamento: escavação-carga-transporte + compactação, com o transporte
  precificado pela DMT (composições SICRO)

Referências: DNIT 106/2009-ES (cortes), DNIT 108/2009-ES (aterros),
Manual de Implantação Básica de Rodovia (IPR-742).

### 1.8 Nota — os dois modos Manta

"Balanço" cobre duas coisas distintas no fluxo interno:

- **Modo A — terraplenagem**: o descrito acima. Material do próprio
  corpo estradal, custo de origem ≈ 0; paga-se o movimento.
- **Modo B — pavimentação**: materiais nobres (brita, BGS, CBUQ). Custo
  posto na pista = FOB + frete × distância, escolhendo a fonte de menor
  custo final; solo local custo 0. Não há Brückner — há matriz
  origem-destino de fontes.

---

## Parte 2 — Aplicação: BR-365/MG, duplicação (EPR)

**Trecho** km 581+957 → 607+954 · 26,0 km · eixo P04-P87 · estaca de 20 m
(Est. 29097+18,13 → 30397+14,38) · 5 eixos modelados (CRESC, DECRESC,
RA, RB, Transição).

Fonte: `Balanco_Massa_BR365_Perguntas_Respostas_Rastreabilidade.xlsx`
(28/07/2026), abas *Matriz P-R-R* e *Seção a Seção*, consolidando o
pacote v2 e a análise ANA_12 (v12).

### 2.1 Volumes

| Grandeza | Pacote v2 (5 eixos) | ANA_12 |
|---|---|---|
| Corte | 820.097,1 m³ | 836.197,1 m³ |
| Aterro | 811.141,2 m³ | 821.326,2 m³ (FC 0,90) |
| Pavimento | 148.145,5 m³ | — |

Corte por eixo: CRESC 663.058,7 · DECRESC 150.218,8 · RA 5.774,1 ·
RB 975,6 · Transição 70,0 m³.

A diferença entre as duas colunas é conhecida e documentada: a ANA_12
inclui dispositivos (km 592 e 600) e corredores de apoio, que não são
estaqueados por bin.

Em volume **bruto** o trecho é quase neutro: corte − aterro = +8.955,9 m³
em 820 mil. É exatamente o caso da §1.5 — a neutralidade aparente
esconde o movimento real.

### 2.2 Fator de conversão

FC vigente **0,90** (recálculo de 22/07/2026, mantido na ANA_12).
Original do pacote: 1,00. Cenário de risco C3: 1,30.

Ressalva de rastreabilidade registrada na própria planilha: **não existe
Fh real**. Não há ensaio Proctor, densidade natural nem densidade máxima
seca no acervo — o 0,90 é FC arbitrado, não fator de homogeneização
medido (§1.2). A curva de Brückner por estação permanece na base FC 1,00
do pacote original, enquanto DMT, momento e custos vêm da ANA_12 em
FC 0,90. **As duas bases convivem no mesmo arquivo** e não devem ser
somadas ou comparadas diretamente.

### 2.3 Balanço por trecho

Barreiras que segmentam o corredor: OAEs em **km 594,3** e **km 596,5**,
e lacuna de projeto em **km 588,76–589,02**.

| Trecho | Residual (FC 0,90) | Situação | Compensação | DMT |
|---|---:|---|---:|---:|
| S1 | −58.477 m³ | déficit | 106.857 m³ | 4.067 m |
| S2 | +290.634 m³ | superávit | 72.870 m³ | 1.944 m |
| S3 | −118.117 m³ | déficit | 63.662 m³ | 394 m |
| S4 | +174 m³ | equilibrado | 295.180 m³ | 4.458 m |
| Locais (RA/RB/Transição) | −17.211 m³ | déficit | 6.820 m³ | — |

Compensação total 545.389 m³ · **DMT médio global 3.485 m**.

Resultado global: **empréstimo 176.592,86 m³ e bota-fora 290.807,05 m³
coexistem**. Saldo líquido = 114.214 m³ de superávit. O par
empréstimo/bota-fora é consequência direta das barreiras — S2 tem
290 mil m³ sobrando que não alcançam o déficit de S1 e S3.

Distribuição das seções no eixo CRESC: mista 782 · corte 270 ·
aterro 212 · passagem 10.

### 2.4 Momento e custo

| Item | Valor |
|---|---|
| Momento Brückner (corredor, FC 1,00) | 3.204.317,6 m³·km |
| Momento total C0 (FC 0,90, ANA_12) | 7.939.585,2 m³·km |
| Preço de transporte (SICRO OUT/2024) | R$ 2,70 /m³·km |
| **Custo de transporte C0** | **R$ 21.436.880** |
| Conformação de bota-fora (290.807 m³ × R$ 4) | R$ 1.163.228 |

Movimento C0: compensado 545.389 + empréstimo 176.593 + bota-fora
290.807 + CFT 122.537 m³ (DMT própria 0,5 km).

Cenários: **C0** jazida/BF fora da faixa, DMT 10 km, royalty R$ 15/m³ ·
**C1** 5 km · **C2** dentro da faixa de domínio, 1,0 km, royalty isento ·
**C3** FC 1,30 como proxy de empolamento/perdas (+ R$ 9,51 M vs C0).

O salto de C0 para C2 é o argumento econômico central do trecho: é a
diferença entre tratar jazida e DME como externos ou internos à faixa.

### 2.5 Pontos de verificação

Três itens que precisam de resposta antes de o balanço fechar. Nenhum é
conclusão de erro — são inconsistências aritméticas ou lacunas que a
própria rastreabilidade da planilha permite isolar.

**PV-1 · Déficit dos eixos locais não aparece no empréstimo.**
O empréstimo declarado (176.592,86 m³) reproduz exatamente a soma dos
déficits de S1 e S3 (58.477 + 118.117 = 176.594 m³). O bota-fora
declarado (290.807,05 m³) reproduz a soma dos superávits de S2 e S4
(290.634 + 174 = 290.808 m³). O déficit dos eixos locais — RA −1.817,
RB −13.614, Transição −1.780, total **−17.211 m³** — não está em
nenhum dos dois. Ou é atendido por transferência de S2 (e então o
bota-fora deveria cair no mesmo montante), ou o empréstimo está
subestimado em 17.211 m³. Sob premissa C0 (DMT 10 km → R$ 27/m³ de
transporte + R$ 15/m³ de royalty), a segunda hipótese vale da ordem de
**R$ 0,7 M**.

**PV-2 · Faixas de DMT não cobrem a compensação.**
A soma dos volumes por faixa SICRO é 384.912 m³ (confere com o total
declarado no campo). A compensação Brückner é 545.389 m³. Faltam
**160.477 m³** sem faixa atribuída — cerca de 29% do compensado. Se as
faixas cobrem apenas as ondas do corredor principal e excluem os eixos
locais e a CFT, isso deve ser dito no campo; se não, há volume
compensado fora do enquadramento contratual de pagamento.

**PV-3 · Risco de 3ª categoria não resolvido.**
A premissa global do pacote é 85% 1ª / 10% 2ª / 5% 3ª, **não medida em
campo** — 41.005 m³ de 3ª categoria no C0. A estimativa alternativa,
por sondagens e perfil revisado, chega a **≈143.798 m³ (21,7% do corte
CRESC)** — 3,5× a premissa. O indício de campo sustenta a preocupação:
17 furos com recusa, dos quais **10 em 14 furos na zona de Araguari
(km 592,0–594,2)**, mais recusas em km 597,9. Divergência registrada e
não resolvida no acervo.

### 2.6 Lacunas do acervo

Registradas como **NÃO INFORMADO** pela regra R2 (não inventar dado):

- **Bloco 4 inteiro** — AASHTO, HRB/SUCS, IG, LL, LP, IP, umidade
  natural, umidade ótima, densidades natural e máxima seca, grau de
  compactação especificado, CBR/ISC e expansão. O acervo geotécnico tem
  **somente 214 furos a trado**, sem SPT e sem ensaio de laboratório.
  Bloqueio registrado: campanha SPT/mista + caracterização.
- **Fh, empolamento e contração** — dependem do item acima.
- **Decapagem / capa vegetal** — não calculada. Indício: camada vegetal
  é o material superficial em 101 dos 214 furos.
- **Equipamento de transporte** — o orçamento usa preço SICRO sem
  definição de frota.
- **Largura legal da faixa de domínio** — o DXF indica offsets de 35 m e
  10 m; não há documento normativo do acervo que confirme.

Divergência de cadastro registrada: 214 furos no acervo contra 215 no
LandXML Civil 3D — o furo TPF-ST-0062 não tem bloco no DWG.

### 2.7 Geometria adotada

Plataforma 24,30 m — pista dupla, 2×(2 faixas × 3,60 m + acostamento
2,50 m) + canteiro central 4,90 m; largura nominal da CFT por pista
12,20 m. Taludes de corte 1V:1,0H ou 1V:1,25H, banqueta i = −10%,
H máx 8,00 m. Taludes de aterro 1V:1,5H; talude do canteiro central
1V:6,0H.

---

## Rastreabilidade

| Fonte | Conteúdo |
|---|---|
| F1 | superfícies e perfis Civil 3D (TIN 516.632 pontos) |
| F2 | pacote v2 — volumes_base, eixos, bins (20 m), bruckner.curve, segments |
| F3 | ANA_12 (v12) — kpis, trechos, cenários, faixas_dmt, custos |
| F4 | LandXML — Alignment (staStart 581.958,13 m · length 25.996,25 m), Profile, CrossSect |
| F5 | sondagens a trado (214 furos) |
| F6 | system-memory / LOGs (23, 27, 28, 29, 32, 70, 73, 76) |
| F7 | pranchas F1 — seção-tipo e notas |
| F8 | censo DXF |

Ressalva estrutural (LOG 76): a curva de Brückner publicada **não foi
reproduzível** a partir dos bins e da geometria, com divergências de até
~118 mil m³. Os valores de momento, DMT e custo desta análise vêm do
recálculo da ANA_12 pelo motor original em FC 0,90, não da curva
publicada.
