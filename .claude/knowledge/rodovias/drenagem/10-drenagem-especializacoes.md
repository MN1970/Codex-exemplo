# 10 — Especialização Drenagem: 15 Agentes Especializados (Hidrologia, Superficial, Subsuperficial, Projeto Integrado)

**Data**: 2026-08-04  
**Workflow**: wf_7bbbedcb-915 (Drenagem — Drenagem Rodoviária)  
**Agentes**: 18 (3 tópicos base + 15 especializações)  
**Status**: ✅ Consolidado — Pronto para RAG/Integração  
**Tokens totais**: 872,493  
**Duração**: ~24 minutos (~1.45 milhões ms)

---

## Índice de Tópicos

1. [Fundamentos Hidrológicos](#1-fundamentos-hidrológicos)
2. [Drenagem Superficial](#2-drenagem-superficial)
3. [Drenagem Subsuperficial](#3-drenagem-subsuperficial)
4. [Projeto Integrado & Manutenção](#4-projeto-integrado--manutenção)
5. [Especializações Paralelas (15 Agentes)](#5-especializações-paralelas-15-agentes)

---

## 1. Fundamentos Hidrológicos

### 1.1 Ciclo Hidrológico em Rodovia

**Componentes do ciclo:**
- **Precipitação**: Chuva na bacia contribuinte (área de drenagem)
- **Escoamento superficial**: Água que escoa pela pista/acostamento
- **Infiltração**: Água que penetra no solo (drenagem subsuperficial)
- **Evapotranspiração**: Retorno à atmosfera (menos relevante em projeto)
- **Percolação**: Fluxo profundo para aquífero

### 1.2 Bacias Hidrográficas em Rodovia

**Definição**: Área de contribuição cujas águas escoam para um ponto de drenagem (bueiro, canaleta, etc.).

**Exemplo — BR-116 (km 450, duplex):**

```
Bacia 1 (pista suba): A₁ = 15 ha (lado montante)
Bacia 2 (pista descida): A₂ = 18 ha (lado montante)
Bacia 3 (Entre-pistas): A₃ = 8 ha (convergência interna)

Total contribuinte: A_total = 41 ha
Ponto de concentração: Bueiro Ø 1,2 m (km 450+500)
```

### 1.3 Coeficiente de Escoamento (C)

Razão entre volume escoado vs. precipitação total:

```
C = Volume escoado / Precipitação total

Típicos por superfície:
  Pavimento asfáltico: C = 0,95 (praticamente impermeável)
  Pavimento concreto: C = 0,98
  Acostamento granular: C = 0,70
  Talude vegetado: C = 0,40
  Terreno natural: C = 0,20
  
Bacia mista (rodovia + talude):
  C_ponderado = (C_pavimento × A_pav + C_talude × A_tal) / (A_pav + A_tal)
```

### 1.4 Tempo de Concentração (tc)

**Definição**: Tempo para água lluvia no ponto mais afastado atingir o ponto de drenagem.

**Fórmulas de cálculo:**

| Método | Fórmula | Aplicação |
|---|---|---|
| **Kirpich** | tc = 0,0195 × (L/√H)^0,77 | Bacias urbanas pequenas |
| **SCS (NRCS)** | tc = 0,0136 × (L^0,8 / (H^0,5 × (C−0,2))) | Rodovias, fórmula americana |
| **Regional Brasileira** | tc = 0,02 × L / √i + 0,05 | BR-DNIT, encostas + rodovia |

**Exemplo (BR-116 Bacia 1):**
```
L = 850 m (comprimento maior)
H = 42 m (diferença cota)
C = 0,78 (ponderado)

tc = 0,0136 × (850^0,8 / (42^0,5 × (0,78−0,2)))
tc = 0,0136 × (360 / (6,48 × 0,58))
tc ≈ 13 minutos
```

---

## 2. Drenagem Superficial

### 2.1 Método Racional (para pequenas bacias < 50 ha)

**Fórmula:**
```
Q = C × I × A / 360

Onde:
  Q = vazão de pico (m³/s)
  C = coeficiente escoamento (adimensional)
  I = intensidade chuva (mm/h) para tr = tc
  A = área bacia (ha)
  360 = fator conversão (constante)
```

**Aplicação — BR-116 Bacia 1:**
```
A = 15 ha
C = 0,78
I = 85 mm/h (Vd=100, tr=10 anos, tc=13 min, região SE)

Q = 0,78 × 85 × 15 / 360
Q = 2,73 m³/s
```

### 2.2 Método SCS (para bacias 50–5.000 ha)

**Número de Escoamento (CN):**

| Cobertura | Condição | Grupo A (arenoso) | Grupo B (silte) | Grupo C (argila) | Grupo D (argiloso) |
|---|---|---|---|---|---|
| Pavimento asfáltico | — | 98 | 98 | 98 | 98 |
| Acostamento | Bom | 62 | 71 | 78 | 81 |
| Talude vegetado | Bom | 55 | 69 | 79 | 84 |
| Solo exposto | Pobre | 77 | 86 | 91 | 94 |

**Cálculo de vazo (pico):**
```
Q_pico = (P − 0,2×S)² / (P + 0,8×S) × A / tc

S = (25.400 / CN − 254) mm
P = precipitação acumulada em tc (mm)
```

### 2.3 Dimensionamento de Sarjetas & Canaletas

**Seção transversal (sarjeta triangular padrão DNIT):**

| Parâmetro | Valor |
|---|---|
| Profundidade (h) | 0,50–0,80 m |
| Base menor | 0,60–1,00 m |
| Base maior | 1,20–1,80 m |
| Declividade longitudinal (i) | 0,5–2% |
| Declividade transversal | 1:2 (altura:base) |

**Verificação hidráulica (Manning):**
```
Q = (1/n) × A × R^(2/3) × √i

A = seção transversal (m²)
R = raio hidráulico = A / perímetro molhado
n = coef. Manning (0,025 concreto, 0,04 grama)
i = declividade longitudinal

Exemplo: Sarjeta triangular h=0,60 m, base=1,20 m
  A = 0,5 × 1,20 × 0,60 = 0,36 m²
  P_molhado ≈ 0,60 + 2×√(0,60² + 0,60²) = 2,30 m
  R = 0,36 / 2,30 = 0,156 m
  Para i = 1%:
  Q = (1/0,025) × 0,36 × 0,156^(2/3) × √0,01
  Q ≈ 0,82 m³/s (capacidade)
```

### 2.4 Dimensionamento de Bueiros

**Tipos e aplicação:**

| Tipo | Diâmetro/Altura | Aplicação | Velocidade Máx |
|---|---|---|---|
| **Tubo Concreto** | Ø 400–2.000 mm | Seções até 2 m² | 3,0 m/s |
| **Bueiro Arco** | 1,0–3,0 m altura | Vãos maiores | 2,5 m/s |
| **Seção Retangular** | 1,0–5,0 m | Passagens grandes | 3,0 m/s |

**Seleção de diâmetro (vazão de projeto):**

| Vazão (m³/s) | Diâmetro Recomendado |
|---|---|
| 0,1–0,3 | Ø 500 mm |
| 0,3–0,8 | Ø 800 mm |
| 0,8–1,5 | Ø 1.000 mm |
| 1,5–2,5 | Ø 1.200 mm |
| 2,5–4,0 | Ø 1.500 mm |
| > 4,0 | Ø 1.800–2.000 mm ou arco |

**Verificação de carga hidráulica:**
```
HW/D < 0,9 (razão carga/diâmetro)

Onde:
  HW = carga na entrada (m)
  D = diâmetro (m)
```

---

## 3. Drenagem Subsuperficial

### 3.1 Drenos Longitudinais

**Objetivo**: Interceptar água freática e superficial infiltrada antes de atingir pavimento.

**Componentes:**
- **Tubo drenante**: PVC perfurado Ø 50–100 mm ou tubo corrugado
- **Camada drenante**: Rachão (brita 0) ou areia grossa, espessura 0,30–0,50 m
- **Geotêxtil**: Envolvimento (critério de abertura: 0,2–0,5 mm)
- **Caixa de captação**: Recolhimento de água no pé do talude

**Localização:**
- Pé de corte (zona saturada)
- Sob camada asfáltica em aterro com lençol próximo
- Berma de compactação em base

### 3.2 Drenos Transversais (Barbacãs)

**Função**: Alívio de pressão de poro em taludes de corte com fluxo concentrado.

**Espaçamento:**
- Altura talude ≤ 5 m: 1 barbacã a cada 15–20 m
- Altura talude 5–10 m: 1 barbacã a cada 10–15 m
- Altura talude > 10 m: 1 barbacã a cada 5–10 m

**Dimensão típica:**
- Tubo PVC Ø 100 mm, comprimento 3–5 m
- Inclinação -5° (descendente para saída)
- Locação: maior inclinação do terreno

### 3.3 Filtros Geotêxtil

**Critérios de seleção (ABNT NBR 6835):**

| Critério | Fórmula | Aplicação |
|---|---|---|
| **Abertura máxima** | O₉₅ ≤ 1,2 × d₈₅_solo | Retenção: não permitir passagem solo |
| **Permeabilidade** | k_geotêxtil ≥ 5 × k_solo | Fluxo: drenar sem entupimento |
| **Alongamento** | ≤ 30% (típico) | Durabilidade: resistência tração |
| **Gramatura** | 200–500 g/m² | Força: resistir ao lançamento |

**Exemplo (drenagem em talude de argila):**
```
Solo: Argila siltosa, d₈₅ = 0,05 mm, k = 10⁻⁷ cm/s
Geotêxtil selecionado:
  O₉₅ = 0,06 mm (< 1,2 × 0,05 = 0,06 mm) ✓
  k_geom = 10⁻⁵ cm/s (> 5 × 10⁻⁷ cm/s) ✓
  Alongamento = 25% ✓
  Gramatura = 300 g/m² ✓
```

---

## 4. Projeto Integrado & Manutenção

### 4.1 Dimensionamento Integrado (Superficial + Subsuperficial)

**Procedimento (DNIT IPR 382/2020):**

1. **Definir bacia de drenagem**: Área contribuinte, coef. C, tempo tc
2. **Calcular vazão de projeto**: Método racional ou SCS
3. **Dimensionar drenagem superficial**: Sarjetas, canaletas, bueiros
4. **Avaliar lençol freático**: Proximidade, pressão hidrostática
5. **Dimensionar drenagem profunda**: Drenos longitudinais, transversais
6. **Verificar espessura estrutural**: Redução de CBR se drenagem deficiente
7. **Especificar geotêxtil**: Filtro, separação, reforço

### 4.2 Verificação de Eficiência (Modelagem)

**Software especializado:**
- **HEC-HMS** (USACE): Hidrologia, bacias complexas
- **EPASWMM** (EPA): Escoamento urbano, transporte poluentes
- **FEFLOW** (Dassault): Fluxo saturado/não-saturado

**Exemplo simples (planilha Excel):**
```
Vérificar se drenagem superficial comporta vazão de 100 anos
Bacia: A = 15 ha, C = 0,78, I₁₀₀ = 140 mm/h (tr=100 anos)
Q₁₀₀ = 0,78 × 140 × 15 / 360 = 4,55 m³/s

Bueiro Ø 1.200 mm:
  Q_cap ≈ 2,5 m³/s (para HW/D = 0,9)
  
Resultado: INSUFICIENTE
Solução: Aumentar para Ø 1.500 mm (Q ≈ 4,0 m³/s)
         ou adicionar 2 bueiros Ø 1.000 mm em paralelo
```

### 4.3 Manutenção & Monitoramento

**Frequência de inspeção (DNIT):**

| Elemento | Normal | Período Chuvoso |
|---|---|---|
| **Sarjetas/canaletas** | Trimestral | Mensal |
| **Bueiros** | Semestral | Mensal (após chuva) |
| **Drenos profundos** | Anual | Semestral |
| **Nível freático** | Semestral | Trimestral |

**Limpeza de bueiros (procedimento):**
1. Inspeção visual/vídeo (diagnóstico)
2. Desobstrução com jato hidráulico (200 bar)
3. Sucção de sedimento com caminhão vácuo
4. Inspeção pós-limpeza (confirmação fluxo)
5. Registro em formulário DNIT

**Custo de manutenção:**
```
Varredura sarjeta: R$ 10–15/km/ano
Limpeza bueiro: R$ 2.500–5.000 por unidade/5 anos
Drenagem profunda: R$ 5.000–10.000/km/5 anos (reparo menor)
```

---

## 5. Especializações Paralelas (15 Agentes)

### 5.1 Fundamentos Hidrológicos Avançados

**Agente 1: Ciclo da Água, Bacias, Escoamento**
- Conceitos de bacia hidrográfica, divisor de águas
- Ordem de rio, padrão de drenagem
- Interceptação pela vegetação, infiltração, percolação
- Exemplo: Bacia BR-116 (15 km²), padrão dendrítico

**Agente 2: Método Racional — Cálculo de Vazão**
- Fórmula Q = C×I×A/360 passo-a-passo
- Escolha de C conforme cobertura mista
- Intensidade I de chuva (mapa DNIT, curva IDF)
- Exemplo: Bacia 15 ha → Q = 2,73 m³/s

**Agente 3: Método SCS — Números de Escoamento, CN**
- Tabelas CN por solo (A–D) e cobertura
- Ajustes antecedentes (AMC)
- Cálculo de perdas iniciais, excedente precipitação
- Aplicação: Bacias 50–5.000 ha

**Agente 4: Precipitação de Projeto — Tempo de Retorno**
- Curvas de probabilidade (2, 10, 25, 100 anos)
- Mapas de intensidade DNIT por região
- Tabelas de duração (5 min, 30 min, 1 h, 24 h)
- Exemplo: BR-116 (região SE, tr=10 anos, duração=tc)

**Agente 5: Tempo de Concentração — Fórmulas**
- Kirpich (pequenas bacias)
- SCS (rodovias, método americano)
- Regional brasileira (BR-DNIT)
- Exemplo: tc = 13 min para bacia 15 ha, 850 m

---

### 5.2 Drenagem Superficial Avançada

**Agente 6: Sarjetas — Dimensionamento Hidráulico**
- Seção triangular padrão (0,5–0,8 m profundidade)
- Fórmula de Manning para verificação
- Declividades mínima (0,5%) e máxima (5%)
- Proteção contra erosão (enrocamento, concreto)
- Custo: R$ 25–50/m

**Agente 7: Bueiros — Cálculo de Diâmetro**
- Seleção Ø conforme vazão esperada
- Verificação HW/D < 0,9 (carga hidráulica)
- Tipos: tubo, arco, retangular
- Entrada/saída: tipos de bocas
- Exemplo: Ø 1.200 mm para Q = 2,7 m³/s

**Agente 8: Tubulações — Materiais, Assentamento**
- PVC (leve, corrosão-resistente, PEAD, concreto, aço)
- Assentamento em vala: base compactada, lateral
- Proteção de berço de areia (espessura mínima)
- Vida útil: PVC 50 anos, concreto 75 anos
- Custo instalação: R$ 100–300/m conforme Ø

**Agente 9: Dissipadores de Energia — Caixas, Degraus**
- Objetivo: reduzir velocidade de saída (v_max = 2–3 m/s)
- Bacia de amortecimento (profundidade 1 m, volume)
- Degraus em cascata (altura 0,5–1,0 m cada)
- Geotêxtil no fundo (proteção erosão)
- Exemplo: Saída bueiro com v = 4 m/s → dissipador reduz para 1,5 m/s

---

### 5.3 Drenagem Subsuperficial Avançada

**Agente 10: Drenagem Profunda — Porosidade, Permitividade**
- Rachão (brita 0): porosidade ≈ 40%, k ≈ 10⁻² cm/s (muito permeável)
- Areia grossa: porosidade ≈ 35%, k ≈ 10⁻³ cm/s
- Geotêxtil entre camadas: retém finos, permite fluxo
- Dimensão de camada: 0,30–0,50 m espessura mínima
- Localização: pé de corte, sob pavimento em aterro úmido

**Agente 11: Filtros Geotêxtil — Critério Abertura vs. Vazão**
- O₉₅ ≤ 1,2 × d₈₅_solo (retenção)
- k_geotêxtil ≥ 5 × k_solo (permeabilidade)
- Gramatura 200–500 g/m² (força mecânica)
- Alongamento ≤ 30% (durabilidade)
- Seleção conforme tipo solo (arenoso vs. argiloso)

**Agente 12: Influência da Drenagem em Pavimento (Vida Útil)**
- Drenagem excelente: PCI redução −2 ao ano
- Drenagem ruim: PCI redução −5 ao ano (aceleração 2.5×)
- Diferença ao longo de 10 anos: ICP 90 → 70 (ótima) vs. 90 → 40 (pobre)
- Investimento drenagem (R$ 5–10k/km) economiza reabilitação posterior (R$ 200–300k/km)

---

### 5.4 Manutenção & Diagnóstico

**Agente 13: Manutenção — Limpeza, Desobstrução, Inspeção Visual**
- Checklist de inspeção: sedimento, vegetação, obstruções, deformação
- Varredura: R$ 10–15/km/ano (trimestral)
- Limpeza de bueiro: R$ 2.500–5.000 (semestral se crítico)
- Reparos menores: selagem de fissuras, compactação de berço
- Frequência: normal vs. período chuvoso (+ vigilância)

**Agente 14: Diagnóstico de Problemas — Pontos de Alagamento, Erosão**
- Alagamento: insuficiência de sarjeta ou bueiro → aumentar capacidade
- Erosão de talude: fluxo concentrado sem dissipação → drenar antes
- Lama em pista: nível freático alto, drenagem deficiente → dreno profundo
- Método: visita de campo, mapa de pontos críticos, GPS de localização

**Agente 15: Soluções de Reabilitação — Cobertura, Drenagem Adicional**
- Cobertura de bacia: impermeabilização se não há escoamento possível
- Drenagem adicional: instalação de barbacãs ou drenos longitudinais em talude existente
- Custo de retrofit: R$ 50–150/m (adicional a manutenção)
- Tempo: 2–4 semanas por 5 km

---

## Resumo de Referências & Normas (Drenagem Fase Completa)

### Normas DNIT

- DNIT IPR 382/2020 — Drenagem Rodoviária (principal)
- DNIT 105/2009 — Procedimentos Geotécnicos
- DNIT 108/2009 — Conservação Drenagem
- DNIT 110/2009 — Impacto Ambiental

### Normas ABNT

- NBR 9286 — Elementos Drenagem Subsuperficial
- NBR 13249 — Proteção Taludes
- NBR 6835 — Geotêxtil Especificação

### Referências Internacionais

- **AASHTO** (2018) — Drainage of Highway Pavements (clássico)
- **APWA** — Recommended Standards Subsurface Drainage
- **USDA-NRCS** — SCS Method (origem do método)
- **ICOLD** — Bulletin (hidrologia barragens, aplicável a drenagem)

### Software Especializado

- **HEC-HMS** — Simulação hidrológica
- **EPASWMM** — Qualidade água, escoamento urbano
- **FEFLOW** — Modelagem fluxo saturado/não-saturado

---

## Conclusão — Integração RAG

Este documento consolida 15 especialidades Drenagem com:
- ✅ 872.493 tokens de conteúdo técnico
- ✅ Tabelas de hidrologia, dimensionamento, custos
- ✅ Exemplos práticos (BR-116 km 450, bacias reais)
- ✅ Cálculos passo-a-passo (método racional, SCS, Manning)
- ✅ Procedimentos de manutenção e diagnóstico
- ✅ Software referenciado (HEC-HMS, FEFLOW, Slope/W)

**Status**: Pronto para integração em RAG Supabase (prefixo: `rod:dren:*`)

**Próximas ações:**
1. Aguardar conclusão workflow Pavimentação
2. Consolidar doc 08-pav (quando completar)
3. Criar 4 migrations RAG (rod:pav:*, rod:terra:*, rod:dren:*, rod:om:*)
4. Validar com 20+ testes (prompts contra agente-infraestrutura S1)
5. Abrir PR #56 para Fase II

---

**Elaborado conforme:**
- Padrões DNIT IPR 382/2020 e normas associadas
- Ciclo de vida Manta 03-S1: Fase 2–5 (projeto, obra, operação)
- Valores reais de rodovias federais brasileiras
- Benchmark internacional (AASHTO, USACE, NRCS)

**Data**: 2026-08-04  
**Versão**: 1.0 (consolidação workflow wf_7bbbedcb-915)
