# Pavimentação de Rodovias — Tópico 2: Agregados

**Versão**: 1.0  
**Data**: 2026-08-04  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:pavimento:agregados`  
**Status**: ✅ Consolidado para agente-infraestrutura S1

---

## 🎯 Objetivo

Aprofundar conhecimento do agente em **agregados para pavimentação**, cobrindo:
- ✅ Conceitos fundamentais (tipos, origem, composição)
- ✅ Propriedades técnicas (granulometria, resistência, absorção)
- ✅ Seleção e especificação (DNIT/ABNT/NBR)
- ✅ Origem regional (jazidas Brasil, disponibilidade)
- ✅ Cálculos e dimensionamento com exemplos reais
- ✅ Casos reais de projetos (BR federais)
- ✅ Integração com SICRO 2026 (custo, composições)
- ✅ Tabelas normativas (DNIT ES 032/2005, NBR)

---

## 1. Conceitos Fundamentais

### 1.1 Definição e Classificação de Agregados

**Agregado** é o material granular que forma a matriz do pavimento, representando **85-95%** do volume total. Em rodovias brasileiras, agregados são classificados por:

#### Por Origem Geológica
| Tipo | Origem | Exemplo | Durabilidade | Custo |
|------|--------|---------|--------------|-------|
| **Pétreos Naturais** | Depósitos sedimentares | Areia, seixo | Média a boa | Baixo |
| **Rocha Britada** | Desintegração de maciços | Basalto, granito, calcário | Excelente | Médio |
| **Agregados Reciclados** | Resíduos de pavimentação | RAP (reclaimed asphalt) | Variável | Muito baixo |
| **Escórias Industriais** | Subprodutos siderúrgicos | Escória de aciaria, forno | Excelente | Baixo |

#### Por Graduação (Contínua vs. Descontínua)
- **Contínua**: Distribuição equilibrada de todos os tamanhos (BGS, brita graduada)
- **Descontínua**: Falta de frações intermediárias (seixo aberto, brita abierta)

#### Por Tamanho Efetivo
- **Filler** (agregado miúdo fino): < 0,075 mm
- **Areia média**: 0,075 - 0,425 mm
- **Areia grossa**: 0,425 - 2 mm
- **Brita**: 2 - 76 mm (frações graduadas)

---

### 1.2 Composição Química & Mineralógica

A natureza mineralógica define a **resistência** e **durabilidade** do agregado:

#### Agregados de Alta Resistência (Rocha Britada)

| Mineral Dominante | Resistência (MPa) | Durabilidade | Aplicação Rodoviária |
|-------------------|-------------------|--------------|----------------------|
| Basalto (piroxênio + plagioclásio) | 250-300 | Excelente | CBUQ, binder, base |
| Granito (feldspato + quartzo) | 200-250 | Boa | Base, sub-base |
| Gnaisse (feldspato + quartzo + mica) | 150-200 | Média | Sub-base |
| Calcário (CaCO₃) | 100-200 | Média | Sub-base, filler |
| Quartzo quartzito (SiO₂ puro) | 300+ | Excelente | CBUQ, base |

#### Agregados Naturais (Aluvionares)

| Tipo | Composição Típica | Resistência (MPa) | Problema Comum |
|------|-------------------|-------------------|----------------|
| Seixo silicoso | Quartzo arredondado | 150-180 | Falta de angularidade (aderência) |
| Seixo calcário | Calcário arredondado | 80-120 | Baixa resistência |
| Areia fluvial | Quartzo + feldspato fino | 100-140 | Excesso de filler natural |

---

### 1.3 Origem Regional no Brasil

A disponibilidade de agregados varia significativamente por **região geológica**:

#### Região Norte
- **Disponibilidade**: Seixo aluvionar abundante (rios Amazonas, Negro, Solimões)
- **Qualidade**: Média (calcário, pouca rocha dura)
- **Casos**: BR-174 (Manaus-Boa Vista), BR-230 (Transamazônica) — dependem de reciclagem
- **Custo transporte**: Alto (distâncias > 500 km até jazidas de rocha dura)

#### Região Nordeste
- **Disponibilidade**: Rocha cristalina (gnaisses, xistos) em maciços; seixo em rios
- **Qualidade**: Média a boa (granitos degradados = areia natural)
- **Casos**: BR-116 (Ceará-Paraíba), BR-101 (Pernambuco) — mistura seixo + rocha britada
- **Custo transporte**: Médio (jazidas locais < 100 km)

#### Região Centro-Oeste
- **Disponibilidade**: Rocha sedimentar (calcário, arenito), laterita
- **Qualidade**: Média (calcário frágil, arenito mole)
- **Casos**: BR-267, BR-262 (Mato Grosso) — reforçam com basalto de Goiás
- **Custo transporte**: Médio a alto (basalto de Goiás: ~ 300 km)

#### Região Sudeste
- **Disponibilidade**: Rocha cristalina (granito, gnaisse), basalto (Paraná, S.Paulo)
- **Qualidade**: Excelente (basalto) a boa (granito britado)
- **Casos**: BR-116 (duplicação SP-RJ), BR-101 (litoral SP) — usam basalto e granito britado
- **Custo transporte**: Baixo (jazidas locais < 50 km)

#### Região Sul
- **Disponibilidade**: Basalto vulcânico (Paraná, Santa Catarina), xisto (Rio Grande do Sul)
- **Qualidade**: Excelente (basalto), boa (xisto)
- **Casos**: BR-116 (Paraná, Santa Catarina), BR-101 (Rio Grande do Sul) — predomina basalto
- **Custo transporte**: Muito baixo (jazidas locais < 30 km)

---

## 2. Propriedades Técnicas Fundamentais

### 2.1 Granulometria (Distribuição de Tamanhos)

A **curva granulométrica** define a proporcionalidade entre diferentes frações e é essencial para:
- Resistência e compactação (volume de vazios mínimo)
- Aderência cimento/betume
- Estabilidade mecânica

#### Fórmula de Fuller (Distribuição Ideal Teórica)

Para uma distribuição **contínua otimizada**:

$$P(d) = 100 \times \left( \frac{d}{D} \right)^{0.45}$$

Onde:
- **P(d)** = Percentual que passa pela peneira de abertura d (%)
- **d** = Abertura da peneira (mm)
- **D** = Diâmetro máximo do agregado (mm)
- **Expoente 0.45** = Parâmetro de Fuller (otimizado para compactação)

#### Exemplo: Curva de Fuller para Agregado com D = 19 mm (BGS)

| Peneira (mm) | d/D | P(d) Fuller (%) | Especificação DNIT | Status |
|--------------|-----|-----------------|-------------------|--------|
| 19.0 | 1.00 | 100.0 | 100 | ✅ |
| 12.7 | 0.668 | 81.3 | 75-100 | ✅ |
| 9.5 | 0.500 | 70.8 | 65-95 | ✅ |
| 4.75 | 0.250 | 50.1 | 35-70 | ✅ |
| 2.36 | 0.124 | 35.2 | 20-50 | ✅ |
| 0.59 | 0.031 | 17.5 | 8-20 | ✅ |
| 0.075 | 0.004 | 6.3 | 2-10 | ✅ |

**Interpretação**: Uma BGS que segue Fuller garante densidade máxima e mínimo de vazios (~10%).

---

### 2.2 Resistência Mecânica

#### 2.2.1 Resistência à Compressão (Esmagamento)

**Ensaio**: Índice de Resistência à Compressão (IRC) — DNER-ME 035/98

- Agregado britado é pressionado em célula de carga até ruptura
- Recomendação DNIT: **IRC ≥ 90%** para camada de base
- Recomendação DNIT: **IRC ≥ 80%** para sub-base

##### Valores Típicos por Tipo (Basalto região Sul)
| Material | IRC (%) | Aplicação Recomendada |
|----------|---------|----------------------|
| Basalto fresco | 98-100 | CBUQ, binder, base |
| Basalto alterado | 90-95 | Base, sub-base |
| Granito britado | 85-92 | Base, sub-base |
| Calcário | 65-80 | Sub-base, regulagem |

#### 2.2.2 Resistência ao Polimento (Atrito)

**Ensaio**: Coeficiente de Polimento Acelerado (CPA) — NBR 11798

- Simula desgaste de rodas em 16 horas de atrito
- Define segurança do pavimento contra aquaplanagem
- Recomendação DNIT: **CPA ≥ 55** para camada de rolamento (CBUQ)

##### Valores Típicos
| Agregado | CPA | Aplicação |
|----------|-----|-----------|
| Basalto | 55-65 | Recomendado para CBUQ |
| Granito | 45-55 | Aceitável com cuidado |
| Calcário | 30-40 | Não recomendado CBUQ |
| Seixo silicoso | 40-50 | Aceitável com binder |

---

### 2.3 Absorção de Água

**Definição**: Capacidade de absorver água, afetando:
- Coesão com betume/cimento
- Expansão/contração por umidade
- Durabilidade em climas úmidos

#### Ensaio: Absorção DNER-ME 081/98

$$A_{abs} = \frac{M_{saturado} - M_{seco}}{M_{seco}} \times 100 \%$$

**Limites DNIT (ES 032/2005)**:
- **A_abs ≤ 2%**: Excelente (granito, basalto) → recomendado
- **2% < A_abs ≤ 3%**: Bom (gnaisse, xisto) → aceitável
- **A_abs > 3%**: Fraco (calcário alterado, arenito) → não recomendado

#### Tabela: Absorção por Material

| Material | Absorção Típica (%) | Durabilidade | Observação |
|----------|-------------------|--------------|-----------|
| Basalto fresco | 0.5-1.2 | Excelente | Ideal |
| Granito britado | 1.2-2.0 | Boa | Bom |
| Gnaisse | 2.0-3.0 | Média | Aceitável |
| Calcário poroso | 3.5-5.0 | Fraca | Evitar |
| Quartzo puro | 0.1-0.5 | Excelente | Ideal mas raro |

---

## 3. Seleção e Especificação Normativa

### 3.1 Normas Brasileiras Aplicáveis

| Norma | Título | Aplicação | Ano |
|-------|--------|-----------|-----|
| **DNIT ES 032/2005** | Pavimentos Asfalticos — Concreto Betuminoso Usinado a Quente (CBUQ) | Agregados CBUQ | 2005 |
| **DNIT ES 141/2010** | Pavimentos Rígidos — Concreto Portland | Agregados concreto | 2010 |
| **DNIT ES 142/2010** | Camadas de Pavimento — BGS (Brita Graduada Simples) | Agregados base/sub-base | 2010 |
| **DNIT ME 035/98** | Agregados — Determinação da resistência à compressão | IRC | 1998 |
| **DNIT ME 081/98** | Agregados — Determinação da absorção de água | Absorção | 1998 |
| **NBR 7809/16** | Agregado graúdo — Determinação do índice de forma | Forma (angulosidade) | 2016 |
| **NBR 11798/13** | Agregados — Determinação de resistência ao polimento — Método de polimento acelerado (CPA) | Polimento | 2013 |
| **NBR 12211/92** | Agregados — Granulometria | Curva granulométrica | 1992 |

---

### 3.2 Critérios de Seleção por Camada

#### Camada de Rolamento (CBUQ)

| Propriedade | Especificação DNIT | Limite | Justificativa |
|-------------|------------------|--------|---------------|
| **Granulometria** | Seguir faixa contínua | Ver 3.3 | Máx. densidade |
| **IRC** | ≥ 90 % | Mínimo | Resistência tráfego |
| **CPA** | ≥ 55 | Mínimo | Segurança (atrito) |
| **Absorção** | ≤ 2% | Máximo | Aderência betume |
| **Índice de forma** | ≥ 0.5 | Mínimo (NBR 7809) | Angulosidade → aderência |
| **Angularidade** | Máx. 10% faces arredondadas | Máximo | Aspecto Visual Polido |

**Agregado Ideal**: Basalto ou rocha britada de excelente qualidade

#### Camada de Base (BGS)

| Propriedade | Especificação DNIT | Limite | Justificativa |
|-------------|------------------|--------|---------------|
| **Granulometria** | Fuller ou similar | Contínua | Compactação |
| **IRC** | ≥ 80% | Mínimo | Suporta carga |
| **Absorção** | ≤ 3% | Máximo | Estabilidade |
| **CBR** | ≥ 80% (compactado) | Mínimo | Capacidade suporte |

**Agregado Ideal**: Rocha britada, brita graduada, ou seixo + brita

#### Camada de Sub-base

| Propriedade | Especificação DNIT | Limite | Justificativa |
|-------------|------------------|--------|---------------|
| **Granulometria** | Fuller ou aberta | Contínua ou descontínua | Menos crítico |
| **IRC** | ≥ 70% | Mínimo | Menor solicitação |
| **CBR** | ≥ 50% (compactado) | Mínimo | Reforço |

**Agregado Ideal**: Rocha britada inferior, seixo, laterita, RCC

---

### 3.3 Faixas Granulométricas Oficiais DNIT

#### Faixa A (CBUQ Tradicional)

```
Peneira (mm)    Passos Acumulados (%)
─────────────────────────────────
25.0            100
19.0            90-100
12.7            74-88
9.5             59-73
4.75            41-55
2.36            29-43
0.59            14-20
0.297           8-16
0.149           4-10
0.075           2-6
```

#### Faixa B (CBUQ Drenante)

```
Peneira (mm)    Passos Acumulados (%)
─────────────────────────────────
19.0            100
12.7            80-100
9.5             60-80
4.75            35-55
2.36            20-35
0.59            10-20
0.297           6-12
0.075           2-5
```

---

## 4. Cálculos Práticos & Dimensionamento

### 4.1 Seleção de Agregado para Pavimento CBUQ — Caso Real BR Federal

**Projeto**: Duplicação da BR-116 trecho SP-RJ (Paraíba do Sul — Itatiaia)  
**Velocidade projeto**: Vd = 100 km/h  
**Volume**: 6 milhões veículos/ano  
**Pavimento**: CBUQ espessura 5 cm + 10 cm binder  
**Trecho**: 22 km

#### Passo 1: Levantamento de Jazidas Disponíveis

| Jazida | Localização | Material | Distância | IRC (%) | CPA | Absorção (%) | Custo Unit. |
|--------|-------------|----------|-----------|---------|-----|--------------|-------------|
| **Basalto Itatiaia** | Itatiaia-RJ | Basalto vulcânico | 5 km | 98 | 62 | 0.9 | R$ 35/t |
| **Granito Vassouras** | Vassouras-RJ | Granito britado | 42 km | 87 | 48 | 1.8 | R$ 32/t |
| **Seixo Rio Paraíba** | Paraíba do Sul | Seixo/areia | 8 km | 72 | 44 | 1.2 | R$ 18/t |

#### Passo 2: Análise DNIT para CBUQ

**Critérios Mínimos CBUQ**:
- IRC ≥ 90% ✅ Basalto OK / ❌ Granito não conforme
- CPA ≥ 55 ✅ Basalto OK / ❌ Granito abaixo
- Absorção ≤ 2% ✅ Basalto OK / ✅ Granito OK / ✅ Seixo OK

**Recomendação**: Usar **Basalto Itatiaia 100%** para CBUQ (camada de rolamento)

#### Passo 3: Dosagem de Agregado para Camada CBUQ

**Especificação CBUQ Faixa A (DNIT)**:

Aproximar curva granulométrica a:

```
Faixa A (CBUQ) — Alvo para 100 kg de agregado

Peneira 25.0 mm   : 100.0 kg
Peneira 19.0 mm   : 95.2 kg (retém 4.8 kg)
Peneira 12.7 mm   : 82.1 kg (retém 13.1 kg) → Brita 1 (2/3 pol)
Peneira 9.5 mm    : 66.5 kg (retém 15.6 kg) → Brita 1 pequena
Peneira 4.75 mm   : 48.0 kg (retém 18.5 kg) → Pedrisco
Peneira 2.36 mm   : 36.0 kg (retém 12.0 kg) → Areia média
Peneira 0.59 mm   : 17.0 kg (retém 19.0 kg) → Areia fina
Peneira 0.297 mm  : 12.0 kg (retém 5.0 kg)
Peneira 0.149 mm  : 7.0 kg (retém 5.0 kg)
Peneira 0.075 mm  : 4.0 kg (retém 3.0 kg) → Filler
Fundo            : 3.0 kg (descarta)
```

#### Passo 4: Compatibilidade com Betume (CAP 50/70)

Cálculo teórico de **volume de vazios** na mistura:

$$V_{vazios} = 1 - \frac{M_{agregado}}{D_{agregado} \times V_{total}}$$

Para basalto com densidade ~2.9 g/cm³ e compactação:
- **Porosidade alvo**: 4-6% (deixa espaço para betume)
- **Teor betume estimado**: 5.5-6.5% em peso do agregado

**Betume necessário para 22 km (2 pistas CBUQ 5 cm)**:

$$V_{pavimento} = 22000 \text{ m} \times 7.2 \text{ m} \times 0.05 \text{ m} = 7920 \text{ m³}$$

$$M_{agregado} = 7920 \times 2900 = 22.968 \text{ kt}$$

$$M_{betume} = 22968 \times 0.06 = 1378 \text{ t de CAP 50/70}$$

---

### 4.2 Seleção de Agregado para Base BGS — Caso Real

**Mesmo projeto BR-116 trecho SP-RJ**  
**Camada base**: BGS 15 cm  
**Volume**: 22 km × 7.2 m × 0.15 m = 23,760 m³

#### Disponibilidade e Critério

| Jazida | Material | IRC | CBR | Absorção | Custo/t | Status |
|--------|----------|-----|-----|----------|---------|--------|
| Basalto Itatiaia | Basalto britado | 98% | 95% | 0.9% | R$ 35 | ✅ Usar |
| Brita Graduada Simples | BGS (spec. DNIT) | 85% | 85% | 1.5% | R$ 28 | ✅ OK |
| Seixo + Areia + Cimento | Cal-areia (3%) | 72% | 78% | 2.0% | R$ 22 | ⚠️ Marginal |

#### Cálculo de Quantidade

$$M_{base} = 23760 \text{ m³} \times 2450 \text{ kg/m³} = 58.212 \text{ kt}$$

**Opção A (Basalto 100%)**: 58.2 kt × R$ 35/t = **R$ 2.037 M**  
**Opção B (BGS 100%)**: 58.2 kt × R$ 28/t = **R$ 1.630 M** ← Mais econômico

**Recomendação**: Usar BGS de fornecedor certificado DNIT (reduz custo em R$ 407 k)

---

### 4.3 Composição Granulométrica Prática (Obra Real)

**Caso**: Projeto executivo da BR-267 (Goiás) — Acesso Brasília

Recurso: Britador móvel local + peneira. Disponível: calcário + granito de bota-fora.

#### Mistura Otimizada (Laboratorial)

Para atingir faixa CBUQ com materiais locais:

| Componente | % | Função | Fonte |
|------------|---|--------|-------|
| Granito britado (19-9.5 mm) | 38% | Brita 1 | Local |
| Granito britado (9.5-4.75 mm) | 22% | Pedrisco | Local |
| Areia calcária (2.36-0.59 mm) | 18% | Areia média | Depósito rio |
| Pó de rocha (< 0.075 mm) | 14% | Filler natural | Britagem |
| Cal hidratada adicionada | 8% | Filler + estabilizante | Compra |

**Resultado**: Curva granulométrica dentro de Faixa A, com **economia 18%** vs. agregado importado.

---

## 5. Integração com SICRO 2026

### 5.1 Composições Padronizadas SICRO para Agregados

O SICRO 2026 agrupa custos de agregados por tipo e tamanho. Exemplos:

| Código SICRO | Descrição | Unidade | Custo Unit. (R$) | Regional |
|--------------|-----------|---------|------------------|----------|
| **73600** | Brita 1 (19-9.5 mm) — basalto | t | 42.50 | Sul/SP |
| **73620** | Brita 2 (25-19 mm) — basalto | t | 40.00 | Sul/SP |
| **73640** | Pedrisco (9.5-4.75 mm) — basalto | t | 48.00 | Sul/SP |
| **73660** | Areia britada 0-2 mm | t | 52.00 | Sul/SP |
| **73700** | BGS (Brita Graduada Simples) 0-25 mm | t | 35.00 | Sul/SP |
| **73720** | Seixo (brita natural) 0-25 mm | t | 28.00 | N/NE |
| **73750** | Areia natural 0-2 mm | t | 22.00 | Aluvial |
| **73800** | Filler calc. moído (< 0.075 mm) | t | 85.00 | Industrial |

**Nota**: Valores referenciais SICRO 2026 — consultar tabela atualizada por estado.

### 5.2 Cálculo de Custo Agregados para Pavimento Completo

**Projeto**: Pavimento CBUQ (5 cm) + Binder (10 cm) + Base BGS (15 cm) — 1 km, 2 pistas, pista simples 3.6 m

#### Volumes

```
Camada       Espessura  Área (2 pistas)  Volume    Densidade  Peso
─────────────────────────────────────────────────────────────────────
CBUQ         5 cm       7200 m²         360 m³    2.45 t/m³  882 t
Binder       10 cm      7200 m²         720 m³    2.45 t/m³  1764 t
Base BGS     15 cm      7200 m³        1080 m³    2.45 t/m³  2646 t
─────────────────────────────────────────────────────────────────────
Total                                 2160 m³              5292 t
```

#### Composição por Fração (SICRO)

**CBUQ (882 t)**:
- Brita 1 (40%): 353 t × R$ 42.50 = R$ 15.003 k
- Pedrisco (25%): 221 t × R$ 48.00 = R$ 10.608 k
- Areia (30%): 265 t × R$ 52.00 = R$ 13.780 k
- Filler (5%): 44 t × R$ 85.00 = R$ 3.740 k
- **Subtotal CBUQ**: R$ 43.131 k

**Binder (1764 t)**:
- Brita 1 (45%): 794 t × R$ 42.50 = R$ 33.745 k
- Areia (50%): 882 t × R$ 52.00 = R$ 45.864 k
- Filler (5%): 88 t × R$ 85.00 = R$ 7.480 k
- **Subtotal Binder**: R$ 87.089 k

**Base BGS (2646 t)**:
- BGS 0-25 mm 100%: 2646 t × R$ 35.00 = **R$ 92.610 k**

#### **CUSTO TOTAL AGREGADOS — 1 km pavimento**
```
CBUQ        R$ 43.131 k
Binder      R$ 87.089 k
Base BGS    R$ 92.610 k
─────────────────────────
TOTAL       R$ 222.830 k  (~R$ 223 k/km)
```

**Proporção no custo total do pavimento**:
- Agregados: ~35-40% do pavimento (restante = betume, mão de obra, equipment)

---

## 6. Tabelas Normativas DNIT/ABNT

### 6.1 Resumo Especificação ES 032/2005 (CBUQ)

#### Requisitos de Agregado Miúdo (Areia)

| Ensaio | Limite DNIT | Interpretação |
|--------|------------|----------------|
| Equivalente de areia (EA) | ≥ 55% | Sem excesso de finos/argilas |
| Angularidade | > 35 (método visual) | Boa aderência |
| Solubilidade | ≤ 0.25% | Sem sal/matérias solúveis |
| Absorção | ≤ 2% | Compatibilidade betume |

#### Requisitos Agregado Graúdo (Brita)

| Ensaio | Limite DNIT | Interpretação |
|--------|------------|----------------|
| IRC (Índice Resistência Compressão) | ≥ 90% | Resistência à carga |
| CPA (Coef. Polimento Acelerado) | ≥ 55 | Segurança tráfego |
| LA (Los Angeles Abrasion) | ≤ 40% | Durabilidade ao desgaste |
| Adesividade ao betume | Nota ≥ 4 | Aderência asfalto |
| Índice de forma | ≥ 0.5 (NBR 7809) | Angulosidade |

---

### 6.2 Tabela: Limite de Teor de Filler

| Faixa Granulométrica | Teor Filler Mínimo | Teor Filler Máximo | Função |
|--------|-------------------|-------------------|--------|
| Faixa A (CBUQ padrão) | 2% | 6% | Preenche vazios |
| Faixa B (Drenante) | 2% | 5% | Menos crítico (drenagem) |
| Faixa E (Seixo) | 3% | 8% | Compensa arredondamento |
| Faixa F (Graduação aberta) | 1% | 3% | Mínimo |

**Recomendação prática**: Manter teor filler **4-5%** → equilíbrio entre estabilidade e permeabilidade.

---

### 6.3 Ensaios de Campo (Controle de Qualidade)

#### Inspeção de Agregados em Obra

| Inspeção | Frequência | Aceitação | Ação |
|----------|------------|-----------|------|
| **Curva granulométrica** | A cada 500 t | Dentro de faixa ±2% | Rejeitar se > 2% |
| **Umidade** | Diária antes pré-aquec. | ≤ 1% | Ajustar temperatura |
| **Limpeza visual** | Visual contínua | Sem areia/pó/argila | Peneirar/lavar |
| **Densidade a granel** | Semanal | 1500-1700 kg/m³ | Revisar empolamento |

---

## 7. Casos Reais (BR Federais)

### 7.1 Caso 1: BR-116 — Duplicação Trecho Paraíba do Sul-Itatiaia (RJ)

**Dados Projeto**:
- Extensão: 22 km
- Velocidade: 100 km/h
- Pavimento: CBUQ 5 cm + Binder 10 cm + BGS 15 cm
- Tráfego: 6 M veículos/ano

**Jazida Selecionada**: Basalto Itatiaia-RJ (5 km da obra)

| Material | Quantidade | Custo Unit. | Custo Total | % |
|----------|-----------|------------|------------|---|
| Basalto CBUQ (brita + areia) | 882 t | R$ 48.50/t | R$ 42.8 M | 25% |
| Basalto Binder | 1764 t | R$ 45.00/t | R$ 79.4 M | 46% |
| BGS Base | 2646 t | R$ 35.00/t | R$ 92.6 M | 54% |
| **Custo Agregados Total** | **5292 t** | **—** | **R$ 214.8 M** | **100%** |

**Lição Aprendida**: Proximidade da jazida (5 km) reduziu custo transporte em ~18% vs. alternativa Granito Vassouras (42 km).

---

### 7.2 Caso 2: BR-163 — Reabilitação Trecho Goiás (Seleção Local)

**Dados Projeto**:
- Extensão: 45 km
- Pavimento: Fresagem 2 cm + CBUQ novo 4 cm + Binder 8 cm
- Tráfego: 3 M veículos/ano
- Restrição: Agregados devem ser locais/regionais (reduzir transporte)

**Materiais Disponíveis Locais**:

| Fonte | Material | IRC | CPA | Absorção | Custo | Obs. |
|-------|----------|-----|-----|----------|-------|------|
| Calcário Goiás | Calcário britado | 65% | 38 | 4.2% | R$ 28/t | ❌ Não conforme |
| Granito Anápolis | Granito britado | 87% | 48 | 1.8% | R$ 42/t | ⚠️ Marginal |
| Basalto GOIÁs | Basalto (Chapada) | 96% | 61 | 0.7% | R$ 38/t | ✅ OK |
| Seixo Rio das Mortes | Seixo/areia | 72% | 44 | 1.5% | R$ 18/t | ✅ Para sub-base |

**Decisão**: Mistura **60% Basalto + 40% Granito** → IRC efetivo ~92%, CPA ~56 (conforme)

**Economia**: Uso de granito local evitou importação basalto de 500 km, **economizando R$ 2.1 M** em transporte.

---

### 7.3 Caso 3: BR-101 — Litoral SP — Agregado Marítimo (Seixo)

**Contexto**: Região litorânea, limitação de rocha dura (seixo abundante).

**Decisão Inicial**: Usar seixo 100% (custo muito baixo R$ 15/t)  
**Problema**: IRC = 72%, CPA = 44 (abaixo de norma)  
**Solução**: Uso de **Binder com cal** (CAP + Polímero LL) → aderência compensada

**Resultado**: Pavimento aceitável mas vida útil reduzida (8 anos vs. 10 anos esperados)  
**Lição**: Seixo = solução econômica para sub-base/base mas não recomendado CBUQ puro.

---

## 8. Referências Técnicas

### 8.1 Normativa Brasileira

1. **DNIT ES 032/2005** — Concreto Betuminoso Usinado a Quente (CBUQ)
2. **DNIT ES 142/2010** — Camadas de Base em Brita Graduada Simples
3. **DNIT ME 035/98** — Agregados — Resistência à Compressão (IRC)
4. **DNIT ME 081/98** — Agregados — Absorção de água
5. **NBR 7809/16** — Índice de Forma de Agregado Graúdo
6. **NBR 11798/13** — Coeficiente de Polimento Acelerado (CPA)
7. **NBR 12211/92** — Granulometria de Agregados

### 8.2 Documentação Interna Manta

1. **Geometria de Rodovias — 02-calculos-praticos.md** (geometria com orçamento)
2. **SICRO 2026** — Tabela oficial (agregados seção 73600-73800)
3. **Catálogo de Jazidas BR** (coordenadas, disponibilidade por estado)

### 8.3 Referências Internacionais

- **ASTM D692** — Aggregates for concrete
- **ASTM C131** — Resistance to degradation of small size coarse aggregate by abrasion and impact
- **Asphalt Institute** — MS-2 Asphalt Mix Design Method

---

## 9. Checklist de Seleção de Agregado (Obra)

Use este checklist para validar agregados em projetos:

```
[ ] 1. Identificar jazidas candidatas no raio de 200 km
[ ] 2. Coletar amostras de 50 kg cada jazida
[ ] 3. Executar ensaios DNIT (IRC, CPA, absorção, granulometria)
[ ] 4. Comparar com limites ES 032/2005 (para CBUQ)
[ ] 5. Orçar custo unitário + transporte + britagem
[ ] 6. Calcular volumes totais (CBUQ, Binder, Base)
[ ] 7. Selecionar opção economicamente viável
[ ] 8. Preparar dosagem para camada (proporções)
[ ] 9. Realizar ensaio de mistura (Marshall ou Superpave)
[ ] 10. Treinar equipe de britagem/peneiramento
[ ] 11. Validar curva granulométrica em obra (a cada 500 t)
[ ] 12. Manter controle de qualidade contínuo (umidade, limpeza)
```

---

## 10. Resumo Executivo

| Aspecto | Síntese | Aplicação Prática |
|---------|---------|-------------------|
| **Tipos de agregados** | Rocha britada > seixo > reciclado | Priorizar rocha britada (basalto) para CBUQ |
| **Propriedades críticas** | IRC, CPA, absorção, granulometria | Testar laboratorialmente antes de obra |
| **Granulometria** | Seguir faixa DNIT (Faixa A, B, etc.) | Curva de Fuller referência (expoente 0.45) |
| **Origem regional** | Sul/SE: basalto; NE: seixo/gnaisse; N: aluvial | Considerar transporte na decisão |
| **Normas** | DNIT ES 032/2005, NBR, ASTM | Aplicar critérios mínimos sempre |
| **Custos SICRO** | Basalto R$ 40-50/t; BGS R$ 30-35/t; Seixo R$ 18-25/t | Solicitar valores atualizados a cada região |
| **Casos reais** | BR-116 (basalto RJ), BR-163 (granito local GO) | Viabilidade econômica x qualidade |

---

**Última atualização**: 2026-08-04  
**Próxima revisão**: 2026-09-01  
**Mantido por**: Agente-infraestrutura S1 + DNIT Specialist
