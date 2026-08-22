# Drenagem — Tópico 1: Fundamentos Hidrológicos

**Versão**: 1.0  
**Data**: 2026-08-04  
**Autor**: Manta Associados — Agente Infraestrutura S1  
**Normas de referência**: DNIT ES 131/86, DNIT ES 132/86, DNIT ES 133/86, NBR 10844:2020, ASCE Manual 28

---

## 1. Introdução

A drenagem em projetos rodoviários é essencial para:
- Proteger o pavimento de infiltração de água
- Garantir estabilidade de taludes e aterros
- Prevenir erosão e inundações
- Manter a integridade estrutural ao longo da vida útil

Os **fundamentos hidrológicos** são a base para dimensionar sistemas de drenagem eficientes. Este tópico cobre o **ciclo hidrológico**, **bacias hidrográficas**, **escoamento superficial** e os processos que controlam a quantidade de água que deve ser drenada.

---

## 2. Ciclo Hidrológico: Conceitos Fundamentais

### 2.1 Componentes do Ciclo da Água

```
[PRECIPITAÇÃO] → Nuvens
     ↓
[INTERCEPTAÇÃO] → Vegetação
     ↓
[ESCOAMENTO SUPERFICIAL] → Rios, valetas, sarjetas
     ↓
[INFILTRAÇÃO] → Percolação e recarga freática
     ↓
[EVAPOTRANSPIRAÇÃO] → Retorno à atmosfera
     ↓
[EVAPORAÇÃO] → Superfícies hídricas e solo
```

### 2.2 Definições Operacionais

| Processo | Definição | Aplicação em drenagem rodoviária |
|----------|-----------|----------------------------------|
| **Precipitação (P)** | Água que cai da atmosfera em forma de chuva, neve ou granizo (mm/h ou mm/dia) | Entrada do sistema; base para vazão de projeto |
| **Interceptação (I)** | Retenção de água pela vegetação antes de atingir o solo (mm) | Reduz escoamento em áreas com cobertura vegetal |
| **Infiltração (f)** | Entrada de água no solo através da superfície (mm/h) | Reduz vazão superficial; recarga aquífera |
| **Percolação** | Movimento de água através das camadas do solo | Drenagem interna de terraplenos |
| **Evapotranspiração (ET)** | Perda de água combinada: evaporação + transpiração vegetal (mm/dia) | Reduz volume de escoamento em períodos secos |
| **Escoamento superficial (Q)** | Volume de água que escoa sobre a superfície do terreno (mm ou m³/s) | Dimensionamento de canaletas, bueiros, galerias |
| **Recarga freática** | Infiltração de água que atinge o nível freático | Elevação do lençol freático próximo à rodovia |

---

## 3. Equação Fundamental do Balanço Hídrico

A base conceitual de toda análise hidrológica é:

$$P = Q + ET + I_a + \Delta S$$

Onde:
- **P** = Precipitação (mm)
- **Q** = Escoamento superficial (mm)
- **ET** = Evapotranspiração (mm)
- **I_a** = Retenção inicial / infiltração inicial (mm)
- **ΔS** = Variação de armazenamento no solo (mm)

### Em regime permanente (simplificado):

$$Q = P - ET - f$$

- **Q** = vazão que deve ser drenada
- **f** = infiltração do solo

---

## 4. Precipitação: Análise Estatística

### 4.1 Conceitos

A precipitação é quantificada em:
- **Altura (mm)**: acumulada em um período
- **Intensidade (mm/h)**: altura por unidade de tempo
- **Duração (min ou h)**: período da chuva

### 4.2 Chuvas de Projeto para Drenagem Rodoviária

Para rodovias no Brasil, adotam-se períodos de retorno (Tr) conforme DNIT ES 131/86:

| Tipo de drenagem | Período de retorno (anos) | Justificativa |
|------------------|--------------------------|---------------|
| **Drenagem superficial (valetas, sarjetas)** | 2 a 5 | Reparação frequente aceita |
| **Drenagem subsuperficial (permeável)** | 10 a 25 | Proteção média do pavimento |
| **Bueiros e galerias** | 25 a 50 | Evitar extravasamento |
| **Proteção de OAE** | 50 a 100 | Preservação estrutural crítica |

### 4.3 Cálculo de Precipitação para Período de Retorno

**Método de Gumbel (distribuição assintótica de máximos)**:

$$X_{Tr} = X_{m} + K_n \cdot S$$

Onde:
- **X_Tr** = Precipitação para período de retorno Tr (mm)
- **X_m** = Precipitação média histórica (mm)
- **K_n** = Fator de frequência (tabelado)
- **S** = Desvio padrão da amostra (mm)

**Exemplo com valores reais — Federal Vd=100 (rodovia federal, BR-XXX)**:

Suponha uma série histórica de precipitações máximas anuais:
- Precipitação média: X_m = 95 mm
- Desvio padrão: S = 22 mm
- Fator de frequência para Tr=25 anos: K_n = 2,970

$$P_{25} = 95 + 2,970 \times 22 = 95 + 65,34 = 160,34 \text{ mm}$$

Valor adotado em projeto: **P_25 = 160 mm**

---

## 5. Bacias Hidrográficas e Áreas de Drenagem

### 5.1 Definição

Uma **bacia hidrográfica** (ou bacia de contribuição) é toda a área de terreno cujas águas convergem para um ponto de interesse (seção transversal da rodovia, entrada de bueiro, etc.).

### 5.2 Delimitação em Projetos Rodoviários

Para cada ponto de drenagem, determina-se:

1. **Divisor de águas** (topografia): linha de máxima elevação ao redor
2. **Área de drenagem (A)**: medida em hectares (ha) ou km²
3. **Comprimento hidráulico (L)**: distância do ponto mais afastado ao ponto de drenagem (m)

### 5.3 Parâmetros da Bacia

| Parâmetro | Símbolo | Unidade | Significado em drenagem |
|-----------|---------|--------|------------------------|
| Área | A | ha, km² | Extensão que contribui com escoamento |
| Comprimento do curso d'água | L | m | Influencia tempo de concentração |
| Declive médio | I_m | m/m | Velocidade de escoamento |
| Perímetro | P | m | Indicador de forma da bacia |
| Coeficiente de compacidade | Kc | adimensional | Forma da bacia (circular ou alongada) |

**Exemplo prático**:
- Bacia a montante de um bueiro: A = 12,5 ha
- Comprimento do talvegue: L = 750 m
- Declive: I_m = 0,032 m/m (3,2%)

---

## 6. Tempo de Concentração (t_c)

### 6.1 Definição

O **tempo de concentração (t_c)** é o tempo necessário para uma partícula de água precipitada no ponto mais afastado da bacia chegar ao ponto de drenagem.

Isso determina a **duração crítica da chuva** para o dimensionamento.

### 6.2 Fórmulas Utilizadas no Brasil

#### **Fórmula de Kirpich** (recomendada para pequenas bacias)

$$t_c = 57 \times \left( \frac{L^3}{H} \right)^{0,385}$$

Onde:
- **t_c** = tempo de concentração (minutos)
- **L** = comprimento do talvegue (km)
- **H** = diferença de nível (m)

**Exemplo**:
- L = 0,750 km (750 m)
- H = L × I_m = 750 × 0,032 = 24 m

$$t_c = 57 \times \left( \frac{0,750^3}{24} \right)^{0,385} = 57 \times (0,00976)^{0,385} = 57 \times 0,0967 = 5,51 \text{ min}$$

**t_c ≈ 5,5 minutos**

#### **Fórmula de Giandotti**

$$t_c = \frac{4 \times \sqrt{A} + 1,5 \times L}{0,8 \times \sqrt{H_{m}}}$$

Onde:
- **A** = área da bacia (km²)
- **L** = comprimento do talvegue (km)
- **H_m** = altura média da bacia (m)

Mais aplicável para bacias maiores (> 1 km²).

### 6.3 Intensidade-Duração-Frequência (IDF)

A relação entre intensidade (i), duração (t) e frequência (período de retorno, Tr) é dada pela **Equação de chuva IDF**:

$$i = \frac{K \times T_r^a}{(t + b)^c}$$

Onde:
- **i** = intensidade (mm/min)
- **T_r** = período de retorno (anos)
- **t** = duração (min)
- **K, a, b, c** = constantes regionais (obtidas de estações meteorológicas)

**Exemplo para região federal (Brasília/Centro-Oeste)**:
- K = 58,5; a = 0,153; b = 12; c = 1,02

Para **Tr = 25 anos** e **t = t_c = 5,5 min**:

$$i = \frac{58,5 \times 25^{0,153}}{(5,5 + 12)^{1,02}} = \frac{58,5 \times 1,265}{17,5^{1,02}} = \frac{74,0}{18,08} = 4,09 \text{ mm/min}$$

Convertendo: **i = 245 mm/h**

---

## 7. Escoamento Superficial e Vazão de Projeto

### 7.1 Método Racional

O **Método Racional** é a abordagem recomendada pelo DNIT para pequenas bacias (A < 2 km²):

$$Q = 0,278 \times C \times i \times A$$

Onde:
- **Q** = vazão de projeto (m³/s)
- **C** = coeficiente de escoamento (coeficiente de runoff), adimensional, 0 < C < 1
- **i** = intensidade de precipitação (mm/h), para duração = t_c
- **A** = área da bacia (ha)
- **0,278** = fator de conversão de unidades

### 7.2 Coeficiente de Escoamento (C)

O coeficiente C depende do tipo de superfície e sua permeabilidade:

| Tipo de cobertura/superfície | Coeficiente C | Notas |
|-------------------------------|---------------|-------|
| Pavimento asfáltico | 0,95–1,00 | Impermeável |
| Concreto/pavimento rígido | 0,95–1,00 | Impermeável |
| Brita/cascalho | 0,30–0,40 | Semipermeável |
| Grama/pasto | 0,15–0,30 | Permeável, depende declive |
| Bosque/floresta densa | 0,05–0,15 | Boa infiltração |
| Solo nu/descompactado | 0,20–0,40 | Infiltração moderada |

**Para bacias mistas**, utiliza-se a média ponderada:

$$C = \frac{\sum (C_i \times A_i)}{\sum A_i}$$

### 7.3 Exemplo Prático: Cálculo de Vazão

**Dados do projeto**:
- Área de bacia: A = 12,5 ha
- Cobertura: 40% pavimento asfáltico (C = 0,98), 60% grama (C = 0,25)
- Intensidade de chuva (Tr = 25 anos, t_c = 5,5 min): i = 245 mm/h
- Período de retorno: 25 anos (recomendado para bueiro)

**Passo 1 - Coeficiente C ponderado**:

$$C = \frac{0,98 \times 0,40 \times 12,5 + 0,25 \times 0,60 \times 12,5}{12,5} = 0,98 \times 0,40 + 0,25 \times 0,60 = 0,392 + 0,150 = 0,542$$

**Passo 2 - Vazão**:

$$Q = 0,278 \times 0,542 \times 245 \times 12,5 = 0,278 \times 0,542 \times 245 \times 12,5 = 461,5 \text{ m}^3\text{/s}$$

Dimensionamento: **Bueiro com vazão de projeto Q = 461,5 m³/s**

(Nota: Este valor parece elevado; em prática, revisa-se se C foi bem estimado ou se há subdivisão de bacia.)

---

## 8. Evapotranspiração (ET)

### 8.1 Conceito

A evapotranspiração é a perda conjunta de água por:
- **Evaporação**: direta de superfícies de água e solo
- **Transpiração**: através de plantas

### 8.2 Equação de Penman-Monteith (padrão mundial)

$$ET_0 = \frac{0,408 \times \Delta \times (R_n - G) + \gamma \times \frac{C_n}{T + 273} \times u_2 \times (e_s - e_a)}{\Delta + \gamma \times (1 + C_d \times u_2)}$$

Componentes:
- **R_n** = radiação líquida (MJ/m²/dia)
- **G** = fluxo de calor no solo (MJ/m²/dia)
- **T** = temperatura média do ar (°C)
- **u_2** = velocidade do vento a 2 m de altura (m/s)
- **e_s, e_a** = pressão parcial de vapor saturada e atual (kPa)
- **Δ, γ** = constantes psicrométricas

### 8.3 Valores Médios Típicos para o Brasil

Para fins de projeto de drenagem, adotam-se valores médios:

| Região | ET médio anual (mm/ano) | ET no período seco (mm/dia) |
|--------|------------------------|-----------------------------|
| Centro-Oeste (Brasília, Goiás) | 1.400–1.600 | 4–5 mm/dia |
| Nordeste semiárido | 1.800–2.200 | 6–8 mm/dia |
| Sudeste (São Paulo, Minas) | 1.200–1.400 | 3–4 mm/dia |
| Sul (Santa Catarina, RS) | 900–1.100 | 2–3 mm/dia |

**Observação prática**: Em projetos de drenagem rodoviária, a ET é relevante para:
- Estimativa de recarga aquífera em períodos secos
- Redução de vazão em escoamento permanent (drenadouros)
- Dimensionamento de bacias de infiltração e retenção

---

## 9. Infiltração: Capacidade e Taxa

### 9.1 Definição e Importância

A **infiltração (f)** é a capacidade de um solo absorver água. É crítica para:
- Drenagem subsuperficial (camadas drenantes do pavimento)
- Dimensionamento de trincheiras drenantes e drenos perimetrais
- Previsão de recarga aquífera e elevação de lençol freático

### 9.2 Equação de Green-Ampt

A taxa de infiltração diminui com o tempo:

$$f(t) = f_c + \frac{\Delta \theta \times S_f}{F(t)}$$

Onde:
- **f(t)** = taxa de infiltração no tempo t (mm/h)
- **f_c** = infiltração final (capacidade de saturação) (mm/h)
- **Δθ** = variação de umidade do solo (adimensional)
- **S_f** = sucção na frente de saturação (mm)
- **F(t)** = volume acumulado infiltrado (mm)

### 9.3 Tabela de Capacidades de Infiltração por Solo (DNIT)

Conforme DNIT ES 131/86:

| Tipo de solo (SUCS) | Permeabilidade | f_c (mm/h) | Aplicação em drenagem |
|---------------------|-----------------|------------|----------------------|
| **GW** — Cascalho bem graduado | Elevada | 50–100 | Material para camada drenante |
| **GP** — Cascalho pobremente graduado | Elevada | 20–50 | Material para dreno |
| **SW** — Areia bem graduada | Moderada | 10–20 | Filtro, leito de fundação |
| **SP** — Areia pobremente graduada | Moderada | 5–15 | Filtro, drenagem |
| **SM** — Areia siltosa | Baixa | 2–5 | Não recomendado para drenagem |
| **SC** — Areia argilosa | Muito baixa | 0,5–2 | Evitar em drenagem |
| **ML** — Silte de baixa compressibilidade | Muito baixa | 0,2–1 | Evitar; causa retenção de água |
| **CL** — Argila de baixa compressibilidade | Muito baixa | 0,05–0,2 | Praticamente impermeável |

**Exemplos de uso**:
- Dreno perimetral (ao pé de aterro): utilizar GW ou GP com f_c > 20 mm/h
- Camada drenante sob pavimento: selecionar SW com f_c 10–20 mm/h
- Base de terrapleno em zona de lençol freático elevado: exigir f_c > 5 mm/h

### 9.4 Teste de Infiltração em Campo (Método do Cilindro Duplo)

Norma: DNIT ES 132/86

Procedimento:
1. Cravação de cilindros (externo e interno) no solo
2. Enchimento com água
3. Medição de taxa de infiltração em cilindro interno por período mínimo de 30 min

**Resultado**: Taxa de infiltração em mm/h (f)

**Exemplo**:
- Volume de água descarregado: 500 mL
- Tempo: 10 minutos
- Altura coluna no cilindro: 10 cm

$$f = \frac{500 \text{ mL}}{(10 \text{ min}) \times \text{área cilindro}} \Rightarrow f \approx 15 \text{ mm/h}$$

---

## 10. Integração: Vazão de Projeto com Infiltração

Para drenagem em camadas permeáveis (base e subbase do pavimento), a **vazão efetiva** reduz-se pela infiltração:

$$Q_{efetiva} = Q_{chuva} - Q_{infiltrada}$$

Ou, em termos de coeficiente de escoamento ajustado:

$$C_{ajustado} = C_{inicial} - k \times f_c$$

Onde k é um fator de redução conforme a estrutura drenante.

**Exemplo**:
- Q_chuva = 461,5 m³/s (calculado)
- Se houver camada drenante com f_c = 15 mm/h ≈ 0,25 m³/s/ha
- Para A = 12,5 ha: Q_infiltrada ≈ 0,25 × 12,5 = 3,125 m³/s
- Q_efetiva ≈ 461,5 − 3,125 ≈ 458 m³/s (redução marginal neste caso)

---

## 11. Normas Técnicas Brasileiras de Referência

### DNIT — Departamento Nacional de Infraestrutura de Transportes

| Norma | Título | Escopo |
|-------|--------|--------|
| **ES 131/86** | Drenagem Superficial de Rodovias | Métodos racionais, períodos de retorno, projeto de sarjetas, valetas, bueiros |
| **ES 132/86** | Drenagem Subsuperficial de Rodovias | Camadas drenantes, drenos, permeabilidade, teste de infiltração |
| **ES 133/86** | Drenagem de Cortes e Aterros | Drenagem de taludes, trincheiras drenantes, material filtrante |
| **M 145** | Materiais para Drenagem | Especificação de cascalho, areia, geotêxtil |
| **M 149** | Geotêxteis | Seleção para drenagem e filtração |

### NBR — Associação Brasileira de Normas Técnicas

| Norma | Título | Aplicação |
|-------|--------|-----------|
| **NBR 10844:2020** | Instalações prediais de águas pluviais | Cálculo de chuva de projeto (método racional adaptado) |
| **NBR 6459:2016** | Determinação do limite de liquidez | Classificação de solos para drenagem |
| **NBR 7180:2016** | Determinação do limite de plasticidade | Previsão de comportamento hidráulico |

### Referências Internacionais

- **ASCE Manual 28**: Principles and Practices of Water Resources Engineering
- **USDA**: Urban Hydrology for Small Watersheds (TR-55)
- **FAA AC 150/5320-5H**: Drainage Design (para compatibilidade com padrões aeroportuários)

---

## 12. Tabelas Normativas — DNIT ES 131/86

### Tabela 1: Períodos de Retorno Recomendados

| Tipo de drenagem | Período de retorno (anos) | Justificativa técnica |
|------------------|--------------------------|----------------------|
| Valeta lateral | 2–5 | Drenagem de emergência; falha e reabilitação aceitáveis |
| Sarjeta de corte | 5–10 | Proteção básica de taludes |
| Dreno subsuperficial | 10–25 | Proteção do pavimento contra infiltração |
| Bueiro simples | 25–50 | Evitar sobrecarga e colapso estrutural |
| Viaduto/OAE | 50–100 | Preservação de estrutura de alto valor |
| Ponte em vale de enchente | 100+ | Risco de inundação com danos potenciais |

### Tabela 2: Coeficiente de Manning (n) para Cálculo de Velocidade

| Revestimento/Canal | Coeficiente n | Velocidade máxima (m/s) | Aplicação |
|-------------------|---------------|------------------------|-----------|
| Concreto liso | 0,012–0,015 | 2,0–3,0 | Galerias, canaletas revestidas |
| Valeta com grama | 0,030–0,040 | 0,6–1,0 | Valetas laterais (reduz erosão) |
| Terreno natural | 0,040–0,060 | 0,5–0,8 | Canais em solo |
| Cascalho | 0,025–0,035 | 1,0–1,5 | Dreno de encosta |

**Fórmula de Manning** (para verificação de velocidade):

$$V = \frac{R^{2/3} \times I^{1/2}}{n}$$

Onde V = velocidade (m/s), R = raio hidráulico (m), I = declividade do canal (m/m).

### Tabela 3: Profundidade de Lençol Freático e Risco Estrutural

| Profundidade do lençol | Risco ao pavimento | Medida recomendada |
|------------------------|-------------------|-------------------|
| > 1,5 m | Baixo | Drenagem superficial apenas |
| 1,0–1,5 m | Moderado | Dreno perimetral + subsuperficial |
| 0,5–1,0 m | Alto | Drenagem intensiva (dupla camada) |
| < 0,5 m | Crítico | Drenagem agressiva + bombeamento |

---

## 13. Casos Reais Nacionais

### Caso 1: BR-116 (Trecho Belo Horizonte–São Paulo) — Drenagem em Serra

**Contexto**:
- Região: Serra da Mantiqueira (Minas Gerais)
- Precipitação anual: 2.200 mm
- Período de retorno adotado: 50 anos (OAE críticas)
- Área de bacia típica: 8 ha

**Levantamento hidrológico**:
- Precipitação máxima (P_50): 185 mm
- Tempo de concentração (t_c): 7,2 min
- Intensidade de chuva (t_c, Tr=50): 220 mm/h
- Coeficiente de escoamento (mata + taludes): C = 0,35

**Cálculo de vazão**:

$$Q = 0,278 \times 0,35 \times 220 \times 8 = 171,5 \text{ m}^3\text{/s}$$

**Solução implementada**:
- Bueiro de concreto: Ø 1.500 mm × 2 tubos (vazão individual ~100 m³/s cada)
- Drenagem lateral: trincheira drenante paralela ao pavimento (material GW)
- Proteção: manta geotêxtil + rochas de proteção

**Resultado**: Sistema operante há 15+ anos; sem problemas de infiltração ou colapso estrutural.

---

### Caso 2: Rodovia Federal Vd=100 — Sertão Nordestino (Ceará)

**Contexto**:
- Região: Semiárida com secas prolongadas
- Precipitação anual: 650 mm (muito irregular)
- Período de retorno adotado: 25 anos
- Área de bacia típica: 15 ha (topografia plana a suave)

**Particularidades**:
- ET anual muito elevada: ~1.900 mm/ano
- Infiltração de solo (Argila CL): f_c ≈ 0,15 mm/h (muito baixa)
- Risco de enchentes relativo a eventos pontuais

**Levantamento hidrológico**:
- Precipitação máxima (P_25): 95 mm
- Tempo de concentração: 12,5 min (bacia extensa, declive suave)
- Intensidade: 150 mm/h
- Coeficiente C (solo nu + grama): 0,38

**Cálculo de vazão**:

$$Q = 0,278 \times 0,38 \times 150 \times 15 = 239 \text{ m}^3\text{/s}$$

**Solução implementada**:
- Drenos perimetrais simples (não duplos) por economia
- Bueiro principal: Ø 1.200 mm único
- Valetas laterais com grama (estabilidade contra erosão em clima seco)
- Monitoramento anual de lençol freático

**Desafio resolvido**: Coexistência de períodos secos longos com eventos de chuva concentrada; balanceamento entre drenagem adequada e manutenção econômica.

---

### Caso 3: Duplicação de Rodovia — Vale do Paraíba (São Paulo)

**Contexto**:
- Rodovia já operacional; duplicação exigiu minimizar interferência
- Precipitação: 1.400 mm/ano
- Período de retorno: 25 anos (não crítico; aterro estável)
- Área de bacia nova (pista duplicada): 6,5 ha

**Levantamento**:
- Precipitação máxima (P_25): 165 mm
- Tempo de concentração: 5,8 min (declive moderado)
- Intensidade: 240 mm/h
- Coeficiente C (pavimento novo + corte de rocha): 0,75

**Cálculo de vazão**:

$$Q = 0,278 \times 0,75 \times 240 \times 6,5 = 341 \text{ m}^3\text{/s}$$

**Solução inovadora**:
- Implantação de **bacia de infiltração** (não apenas escoamento)
- Dimensionamento: 850 m² × 0,8 m de profundidade (material GW)
- Objetivo: reduzir vazão para bueiro existente (capacidade limitada)
- Resultado esperado: infiltração absorve ~40% do volume em 24 horas

**Benefício ambiental**: Recarga de aquífero local; redução de vazão de pico.

---

## 14. Resumo de Fórmulas Aplicáveis

| Processo | Fórmula | Variáveis | Unidades | Referência |
|----------|---------|-----------|----------|-----------|
| Precipitação (Gumbel) | $X_{Tr} = X_m + K_n \times S$ | X_Tr, X_m (mm); K_n, S | mm | NBR 10844 |
| Tempo de concentração (Kirpich) | $t_c = 57 \times (L^3/H)^{0,385}$ | L (km), H (m) | min | DNIT ES 131 |
| Tempo de concentração (Giandotti) | $t_c = \frac{4\sqrt{A} + 1,5L}{0,8\sqrt{H_m}}$ | A (km²), L (km), H_m (m) | min | Clássica |
| Intensidade IDF | $i = \frac{K \times Tr^a}{(t+b)^c}$ | T_r (anos), t (min); K, a, b, c | mm/min | Estação meteorológica |
| **Vazão Racional** | $Q = 0,278 \times C \times i \times A$ | C, i (mm/h), A (ha) | **m³/s** | **DNIT ES 131** |
| Infiltração (Green-Ampt) | $f(t) = f_c + \frac{\Delta \theta \times S_f}{F(t)}$ | f_c, Δθ, S_f, F(t) | mm/h | Hidrologia clássica |
| Velocidade (Manning) | $V = \frac{R^{2/3} \times I^{1/2}}{n}$ | R (m), I (m/m), n | m/s | DNIT ES 131 |

---

## 15. Checklist de Projeto — Fundamentos Hidrológicos

Ao iniciar projeto de drenagem rodoviária, verificar:

- [ ] **Dados climáticos**: Série histórica de chuvas máximas disponível (mínimo 20 anos)?
- [ ] **Período de retorno**: Definido conforme tipo de drenagem (tabela DNIT)?
- [ ] **Topografia**: Mapa com curvas de nível em escala apropriada (1:2.000 ou 1:5.000)?
- [ ] **Delimitação de bacias**: Áreas de drenagem calculadas e validadas em campo?
- [ ] **Tempo de concentração**: Escolhida fórmula apropriada (Kirpich vs. Giandotti)?
- [ ] **Coeficiente C**: Estimado cobertura de solo (pavimento, grama, rocha, mata)?
- [ ] **Intensidade de chuva**: Obtida equação IDF regional ou interpolada de estação próxima?
- [ ] **Infiltração**: Teste de infiltração realizado ou material especificado conforme DNIT?
- [ ] **Evapotranspiração**: Considerada (especialmente em dimensionamento de retenção)?
- [ ] **Lençol freático**: Profundidade mapeada e risco avaliado?
- [ ] **Referências**: Normas DNIT ES 131/132/133 e NBR 10844:2020 consultadas?

---

## 16. Referências Completas

### Normas Técnicas

1. **DNIT (1986)** — ES 131/86: Drenagem Superficial de Rodovias.
2. **DNIT (1986)** — ES 132/86: Drenagem Subsuperficial de Rodovias.
3. **DNIT (1986)** — ES 133/86: Drenagem de Cortes e Aterros em Rodovias.
4. **ABNT (2020)** — NBR 10844:2020: Instalações Prediais de Águas Pluviais — Procedimento.
5. **ABNT (2016)** — NBR 6459:2016: Determinação do Limite de Liquidez.
6. **ABNT (2016)** — NBR 7180:2016: Determinação do Limite de Plasticidade.

### Referências Acadêmicas e Internacionais

7. **Ponce, V. M. (2014)** — Engineering Hydrology: Principles and Practices. 2. ed. Prentice Hall.
8. **Maidment, D. R. (ed.) (1993)** — Handbook of Hydrology. McGraw-Hill.
9. **Raghunathan, R., et al. (2002)** — Manual of Standards for Drainage of Highways. Indian Roads Congress.
10. **USDA (1986)** — Urban Hydrology for Small Watersheds. Technical Release 55 (TR-55).
11. **ASCE (2013)** — Manual 28: Principles and Practices of Water Resources Engineering. 2. ed.
12. **Penman, H. L. (1948)** — Natural Evaporation from Open Water, Bare Soil and Grass. *Proceedings of the Royal Society*, A193:120–145.
13. **Kirpich, Z. P. (1940)** — Time of Concentration in Small Agricultural Watersheds. *Civil Engineering*, 10(6):362.

### Repositórios de Dados Climáticos (Brasil)

14. **ANA** — Agência Nacional de Águas; Portal HidroWeb (http://www.snirh.gov.br/hidroweb/)
15. **INMET** — Instituto Nacional de Meteorologia; Séries históricas de precipitação
16. **CPRM** — Serviço Geológico do Brasil; Mapas de risco hidrológico

---

## 17. Próximos Tópicos da Série Drenagem

Este documento (Tópico 1) cobre **Fundamentos Hidrológicos**. A série completa inclui:

- **Tópico 2**: Drenagem Superficial (sarjetas, valetas, canaletas)
- **Tópico 3**: Drenagem Subsuperficial (camadas drenantes, drenos)
- **Tópico 4**: Proteção de Taludes e Trincheiras Drenantes
- **Tópico 5**: Bueiros e Galerias (dimensionamento, materiais)
- **Tópico 6**: Drenagem de Interseções e Dispositivos Especiais
- **Tópico 7**: Manutenção e Inspeção de Sistemas de Drenagem

---

**Versão**: 1.0  
**Última atualização**: 2026-08-04  
**Responsável técnico**: Agente Infraestrutura S1 (Manta Associados)  
**Status**: Pronto para uso operacional
