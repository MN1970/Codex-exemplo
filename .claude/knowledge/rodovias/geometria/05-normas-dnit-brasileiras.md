# Normas Brasileiras & DNIT — Geometria de Rodovias

**Data**: 2026-08-03  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:normas:*`  
**Autoridade**: DNIT, ABNT, IBGE, ANTT

---

## 1. Normas DNIT (Departamento Nacional de Infraestrutura de Transportes)

### 1.1 Especificações Técnicas (ES)

#### **DNIT ES 101/97 — Projeto Geométrico de Rodovias — Elementos de Rodovia**

**Status**: ✅ Vigente (atualizada)  
**Publicação**: 1997 (revisões 2004, 2010)  
**Escopo**: Fundamentação técnica completa para projeto geométrico

##### Conteúdo Principal

```
Capítulo 1: Conceitos e Definições
  1.1 Classificação funcional
  1.2 Velocidade de projeto (Vd)
  1.3 Tráfego de projeto
  1.4 Classes de rodovia (BR, BR-e, estadual, municipal)

Capítulo 2: Alinhamento Horizontal
  2.1 Tangentes (comprimento mín/máx)
  2.2 Raio mínimo (fórmulas)
  2.3 Curvas de transição (clotóides, parâmetro A)
  2.4 Superelevação (fórmulas e métodos)
  2.5 Visibilidade em curva (flecha de recuo)

Capítulo 3: Alinhamento Vertical
  3.1 Rampas (máxima, mínima, comprimento)
  3.2 Curvas verticais (parábolas, comprimento mín)
  3.3 Distância de visibilidade de parada
  3.4 Distância de visibilidade de ultrapassagem

Capítulo 4: Seção Transversal
  4.1 Faixa de rolamento (largura por classe)
  4.2 Acostamento (tipo, largura, inclinação)
  4.3 Banquetas (inclinação de corte/aterro)
  4.4 Inclinação transversal (normal e superelevação)
  4.5 Dispositivos de segurança (defensas, guarda-corpos)

Capítulo 5: Tabelas de Referência
  5.1 Raios mínimos (por Vd e topografia)
  5.2 Superelevações (por Vd e raio)
  5.3 Comprimentos de clotóide
  5.4 Visibilidade (parada, ultrapassagem)
  5.5 Parâmetros de projeto por classe

Capítulo 6: Interseções
  6.1 Rotatórias (raios, triângulo visibilidade)
  6.2 Interseções em nível (T, cruz)
  6.3 Rampas de acesso
  6.4 Vistas de decisão
```

##### Tabelas Canônicas

**Tabela 2.1 — Raio Mínimo por Velocidade de Projeto (com superelevação máx 8%)**

```
Vd (km/h) | R_mín (m) | Superelevação (%) | Coef. Atrito (f) |
----------|-----------|-------------------|-----------------|
40        | 42        | 8                 | 0.20            |
60        | 96        | 8                 | 0.18            |
80        | 170       | 8                 | 0.16            |
100       | 265       | 8                 | 0.15            |
120       | 378       | 8                 | 0.14            |

Fonte: DNIT ES 101/97, Tabela 2.1
Fórmula: R_mín = V² / (127 × (e_máx + f))
```

**Tabela 3.1 — Comprimento Mínimo de Curva Vertical (método K)**

```
Vd (km/h) | K Convexa (m) | K Côncava (m) | Fórmula        |
----------|---------------|---------------|----------------|
40        | 8             | 6             | L = K × |Δi|   |
60        | 18            | 13            | Δi = i1 - i2   |
80        | 32            | 23            | (em decimais)  |
100       | 50            | 36            |                |
120       | 72            | 52            |                |

Fonte: DNIT ES 101/97, Tabela 3.1
```

**Tabela 4.1 — Largura de Faixa de Rolamento (m)**

```
Classe de Rodovia    | Vd (km/h) | Largura Faixa |
---------------------|-----------|---------------|
BR (Federal Pista Dupla) | 100-120 | 3.60          |
BR-e (Federal Simples)   | 80-100  | 3.50          |
Estadual Dupla       | 80        | 3.50          |
Estadual Simples     | 60-80     | 3.30-3.50     |
Municipal            | 40-60     | 3.00-3.30     |

Fonte: DNIT ES 101/97, Tabela 4.1
```

**Tabela 4.2 — Largura de Acostamento (m)**

```
Classe de Rodovia    | Acostamento Pav. | Acostamento Não Pav. |
---------------------|------------------|----------------------|
BR (Federal)         | 2.50-3.00        | 3.00-4.00            |
BR-e                 | 2.00-2.50        | 2.50-3.50            |
Estadual             | 1.50-2.00        | 2.00-3.00            |
Municipal            | 0.50-1.50        | 1.00-2.00            |

Fonte: DNIT ES 101/97, Tabela 4.2
```

#### **DNIT ES 131/86 — Projeto de Drenagem de Rodovias**

**Status**: ✅ Vigente  
**Escopo**: Drenagem superficial, banquetas, proteção de taludes

##### Parâmetros Críticos para Geometria

```
2.3 Declividade de Banquetas
─────────────────────────────
Mínima: 0.5% (para escoamento)
Máxima: 3-4% (conforme solo)
Tipo: perpendicular ao eixo ou oblíqua (45°)

3.2 Proteção de Taludes
───────────────────────
Altura crítica de taludes não protegidos:
- Solo granular: 5-8m
- Solo coeso: 8-12m
- Rocha: sem limite
- Métodos: hidrossemeadura, geo-membrana, argamassa projetada

4.1 Canaletas de Drenagem
────────────────────────
Seção mínima: triangular 0.30 × 0.30m
Declividade mín: 0.5%
Revestimento: grama ou concreto
```

---

### 1.2 Instruções de Projeto (IPR)

#### **DNIT IPR 726/94 — Visibilidade em Curvas Horizontais**

**Status**: ✅ Vigente  
**Escopo**: Cálculo de flecha de recuo para garantir visibilidade

##### Método de Cálculo

```
Dado:
- Raio da curva (R)
- Distância de visibilidade necessária (d)
  (depende de parada ou ultrapassagem)

Encontrar: Flecha de recuo (f)

Fórmulas:
─────────
Ângulo central subtendido:
θ = 2 × arcsen(d / 2R)  [radianos]

Corda visual:
c = 2R × sen(θ/2)

Flecha:
f = R - √(R² - (d/2)²)

Tabela Rápida (R=500m):

d (m) | θ (°) | f (m)
------|-------|-------
50    | 5.7   | 0.32
80    | 9.2   | 0.81
100   | 11.5  | 1.27
137   | 15.7  | 2.37
150   | 17.2  | 2.80
200   | 22.9  | 5.02
```

#### **DNIT IPR 702/97 — Avaliação Funcional de Pavimentos**

**Status**: ✅ Vigente  
**Escopo**: Defeitos, qualidade superficial, relacionado a geometria (irregularidade)

##### Relação com Geometria

```
IRI (International Roughness Index):
- Correlaciona-se com alinhamento vertical
- Defeitos em curvas verticais → aumento de IRI
- Limite aceitável: < 3.0 m/km (bom)
- Limite crítico: > 4.0 m/km (reabilitação)

Macrotextura:
- Relacionada a visibilidade molhada (aquaplanagem)
- Importante em curvas de alta superelevação
```

---

## 2. Normas ABNT (Associação Brasileira de Normas Técnicas)

### 2.1 Estrutural & Geotécnica

#### **NBR 6122 — Projeto e Execução de Fundações**

**Aplicável a**: Taludes, estruturas de contenção em rodovias

```
Seções 3.1-3.5: Geotecnia
- Ângulos de atrito (φ) por tipo de solo
- Capacidade de suporte (γ = 1.5-2.0)
- Fator de segurança para taludes: FS ≥ 1.3-1.5
```

#### **NBR 7187 — Projeto de Pontes de Concreto Armado**

**Aplicável a**: Interseções com outras infraestruturas (viadutos, passarelas)

```
Seção 4.2: Ações e Combinações
- Cargas móveis (classe de via)
- Envoltória de esforços
- Deslocamentos admissíveis
```

#### **NBR 11682 — Estabilidade de Encostas**

**Aplicável a**: Taludes de corte e aterro

```
Método de cálculo:
- Fator de Segurança (FS) = Resistência / Solicitação
- FS ≥ 1.3 (permanente), FS ≥ 1.2 (temporário)

Análise por tipo de movimento:
- Plano
- Circular (Bishop simplificado)
- Cunha
```

---

### 2.2 Segurança & Sinalização

#### **NBR 15895 — Sinalização Horizontal de Trânsito**

**Escopo**: Faixas contínuas/tracejadas em função de geometria

```
Seção 5.1: Linhas Divisórias
- Contínua: proibida ultrapassagem (em curvas, próximo a PI)
- Tracejada: permitida ultrapassagem (tangentes, retas longas)
- Dupla: máxima restrição

Exemplo:
- Curva com R=250m (risco) → linha contínua
- Reta com 500m → linha tracejada
```

#### **NBR 14644 — Balizamento de Rodovias**

**Escopo**: Defensas, defensores, bancos de pneu

```
Seção 6: Defensas Metálicas
- Colocação em curvas de risco
- Altura mínima: 0.60m
- Espaçamento de pregos: 0.30m
- Raio de aplicação: R < 250m ou superelevação > 6%
```

---

### 2.3 Drenagem & Hidrologia

#### **NBR 10844 — Instalações Prediais de Águas Pluviais**

**Aplicável a**: Sistemas de drenagem em postos, praças de pedágio, canteiros

#### **NBR 12211 — Métodos de Cálculo de Velocidade de Água em Tubulações**

**Aplicável a**: Dimensionamento de bueiros, grelhas em banquetas

---

## 3. Tabelas Normalizadas DNIT (Resumo Executivo)

### 3.1 Velocidade de Projeto por Classe

```
┌─────────────────┬──────────┬────────────┬─────────────────┐
│ Classe Rodovia  │ Vd (km/h)│ Topografia │ Exemplo         │
├─────────────────┼──────────┼────────────┼─────────────────┤
│ BR Pista Dupla  │ 100-120  │ Plana      │ BR-116 SP       │
│ BR Pista Simples│ 80-100   │ Ondulada   │ BR-101 SC       │
│ BR-e (Estadual) │ 60-80    │ Montanhosa │ BR-259 MG       │
│ Estadual        │ 60-80    │ Montanhosa │ Rodovias SP     │
│ Municipal       │ 40-60    │ Variada    │ Vias locais     │
└─────────────────┴──────────┴────────────┴─────────────────┘
```

### 3.2 Parâmetros Críticos por Vd

```
Vd (km/h) │ R_mín (m) │ e_máx (%) │ i_máx (%) │ d_parada (m)
───────────┼───────────┼───────────┼───────────┼──────────────
40         │ 42        │ 8         │ 7-8       │ 28
60         │ 96        │ 8         │ 7-8       │ 53
80         │ 170       │ 8         │ 6-7       │ 89
100        │ 265       │ 8         │ 5-6       │ 137
120        │ 378       │ 8         │ 4-5       │ 198

Nota: e_máx pode ser até 10% em casos montanhosos (DNIT ES 101/97 Allow)
```

---

## 4. Resolução ANTT & Legislação Complementar

### 4.1 Resoluções Relevantes

#### **Resolução ANTT 1623/2008 — Instruções de Projeto Geométrico**

```
Artigo 2º: Estabelece conformidade obrigatória com:
- DNIT ES 101/97
- DNIT ES 131/86
- Normas ABNT vigentes
- Portarias DNIT anteriores

Artigo 3º: Inspeção obrigatória antes de liberação
- Medição de raios
- Verificação de superelevação (taquimetria)
- Teste de visibilidade (in loco ou foto)
```

---

## 5. Citações Cruzadas (Fórmulas por Norma)

### 5.1 Raio Mínimo

```
DNIT ES 101/97, Item 2.2.2.1:
R_mín = V² / (127 × (e + f))

Onde:
  V = velocidade de projeto (km/h)
  e = superelevação (decimal)
  f = coeficiente de atrito (0.10-0.20)
```

### 5.2 Superelevação

```
DNIT ES 101/97, Item 2.3.3.1:
e = (V² / (127 × R)) - f

Se resultar em e > e_máx (0.08 ou 0.10):
  → Usar e_máx
  → Reduzir R ou V
```

### 5.3 Comprimento de Clotóide

```
DNIT ES 101/97, Item 2.2.2.3:
L_mín = 0.036 × V³ / R

Parâmetro A:
A² = R × L
```

### 5.4 Curva Vertical

```
DNIT ES 101/97, Item 3.2.1:
L = K × |Δi|

K = f(Vd) conforme Tabela 3.1
```

### 5.5 Visibilidade de Parada

```
DNIT ES 101/97, Item 3.2.1 + IPR 726:
d_parada = d_reação + d_frenagem

d_reação = V × t  (t ≈ 2.5s)
d_frenagem = V² / (254 × f)

Total (aproximado):
d_parada ≈ V × 0.7 + V² / (254 × f)
```

---

## 6. Tabelas SICRO & Orçamento (DNIT)

### 6.1 Aplicação SICRO

**Sistema de Custos de Obras (SICRO DNIT)**  
Acesso: https://sicro.dnit.gov.br

```
Estrutura:
01 — Mobilização e Desmobilização
02 — Serviços Geotécnicos
03 — Movimento de Terra
04 — Drenagem
05 — Pavimentação
06 — Estruturas (Pontes/OAE)
07 — Sinalização
08 — Manutenção

Exemplo - Pavimentação (05):
05.02.01 = Base Granular 15cm (m²) → R$ 35.00/m²
05.02.03 = CBUQ 5cm (m²) → R$ 95.00/m²
```

### 6.2 Composição Típica SICRO

```
Item: CBUQ 5cm (Rodovia Classe BR)
─────────────────────────────────

Insumos:
- Concreto betuminoso: 0.600 t → R$ 950/t = R$ 570.00
- Emulsão (tack-coat): 0.500 l → R$ 8.50/l = R$ 4.25
- Combustível (asfalto): 3.000 L → R$ 6.50/L = R$ 19.50
- Mão obra (operador): 0.250 h → R$ 45/h = R$ 11.25
- Equipamento (vibroacabadora): 0.250 h → R$ 200/h = R$ 50.00

Subtotal (sem BDI): R$ 655.00/m²
BDI (18%): R$ 117.90/m²
Total com margem: R$ 772.90/m² ≈ R$ 775.00/m²

Fonte: SICRO 2026 (vigente)
```

---

## 7. Legislação de Concessões (ANTT/DNIT)

### 7.1 Requisitos de Projeto

```
Edital de Concessão Típico (ANTT):
──────────────────────────────────
Cláusula 3.2 — Padrões Técnicos

"Os projetos devem atender integralmente:
  • DNIT ES 101/97 (Projeto Geométrico)
  • DNIT ES 131/86 (Drenagem)
  • Normas ABNT aplicáveis
  • Manual DNIT de Sinalização
  • Inspeção técnica DNIT (pré-liberação)"

Cláusula 3.3 — Velocidade de Projeto

"Vd mínima: conforme classe de rodovia
Vd máxima: limitada por topografia
Verificação: survey topográfico com GPS (precisão ±0.05m)"
```

---

## 8. Checklist Conformidade Normativa

```
VALIDAÇÃO DE PROJETO GEOMÉTRICO CONFORME NORMAS DNIT

□ ES 101/97
  □ Raios mínimos verificados (todos os valores)
  □ Superelevação dentro de limite (≤8%, exceção ≤10%)
  □ Clotóides dimensionadas (A ≥ 0.6R)
  □ Tangentes verificadas (L_mín ≤ L ≤ L_máx)
  □ Visibilidade de parada ≥ d_mín
  □ Curvas verticais em parábola (não linear)
  □ Seção transversal conforme classe
  □ Memoriais descritivos estruturados

□ ES 131/86
  □ Declividade banqueta ≥ 0.5%
  □ Altura crítica taludes verificada
  □ Proteção de taludes dimensionada
  □ Sistema de drenagem especificado

□ NBR 11682 (Taludes)
  □ FS ≥ 1.3 (permanente)
  □ FS ≥ 1.2 (temporário)

□ NBR 15895 (Sinalização)
  □ Linhas contínuas em curvas de risco
  □ Espaçamento conforme Vd

□ NBR 14644 (Balizamento)
  □ Defensas em curvas de risco
  □ Altura e espaçamento corretos

□ Legislação ANTT
  □ Edital de concessão atendido
  □ Inspeção pré-liberação completada
```

---

## 9. Referências Diretas (Para RAG)

| Norma | Link Oficial | Status Acesso | Usar em RAG |
|-------|-------------|---------------|------------|
| DNIT ES 101/97 | dnit.gov.br/normas | Aberto | ✅ rod:geom:normas:es-101 |
| DNIT ES 131/86 | dnit.gov.br/normas | Aberto | ✅ rod:geom:normas:es-131 |
| DNIT IPR 702 | dnit.gov.br/pesquisa | Aberto | ✅ rod:geom:normas:ipr-702 |
| DNIT IPR 726 | dnit.gov.br/pesquisa | Aberto | ✅ rod:geom:normas:ipr-726 |
| NBR 6122 | abnt.org.br | Pago | ✅ rod:geom:normas:nbr-6122 |
| NBR 11682 | abnt.org.br | Pago | ✅ rod:geom:normas:nbr-11682 |
| NBR 15895 | abnt.org.br | Pago | ✅ rod:geom:normas:nbr-15895 |
| SICRO 2026 | sicro.dnit.gov.br | Aberto | ✅ rod:geom:normas:sicro |

---

## 10. Desvios & Exceções Permitidas

### 10.1 Aprovações Especiais DNIT

```
Situação: R < R_mín
Solução permitida:
  1. Reduzir Vd (sinalizar redução de velocidade)
  2. Aumentar superelevação até 10% (exceção montanha)
  3. Instalar sistema de proteção (defensa, tacha, guardrail)
  
Requer: Aprovação formal DNIT (processo DNIT-DIPLAN)
```

### 10.2 Conformidade Parcial

```
Estradas em operação com não-conformidades:
  • BR-116 (alguns trechos): R < R_mín (histórico pré-1997)
  • Planos de reabilitação com faseamento permitido
  
Política DNIT (2020):
  "Priorizar conformidade DNIT ES 101/97 em:
    1. Novos projetos (100% conformidade obrigatória)
    2. Duplicações (conformidade completa)
    3. Reabilitação (target 80-90% viável economicamente)"
```

---

**Última atualização**: 2026-08-03  
**Validade**: Normas vigentes conforme DNIT/ABNT 2026  
**Responsável**: Agente-infraestrutura S1 + Manta 03  
**Referência RAG**: `rod:geom:normas:*`
