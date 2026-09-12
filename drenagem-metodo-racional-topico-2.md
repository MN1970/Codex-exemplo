# Drenagem — Tópico 2: Método Racional
## Cálculo de Vazão para Dimensionamento de Sistemas de Drenagem Rodoviária

**Versão:** 1.0  
**Data:** 2026-08-04  
**Contexto:** Projeto rodoviário federal Vd = 100 km/h  
**Norma referência:** DNIT ES 131/86 (Drenagem Superficial de Rodovias)  
**Aplicação:** Dimensionamento de bueiros, sarjetas, valetas, canaletas e sistemas de drenagem lateral

---

## 1. CONCEITOS FUNDAMENTAIS

### 1.1 O Método Racional: Princípios Gerais

O **Método Racional** é um procedimento determinístico para estimativa da vazão máxima de escoamento superficial em uma bacia hidrográfica ou área de contribuição, baseado na suposição de que:

1. A vazão máxima ocorre quando toda a bacia contribuinte está em regime permanente de chuva
2. O pico de vazão é proporcional à intensidade pluviométrica (I) e à área de drenagem (A)
3. Um fator de redução (Coeficiente de Escoamento C) contabiliza perdas por infiltração, armazenamento e interceptação vegetal

### 1.2 Equação Fundamental

$$Q = \frac{C \cdot I \cdot A}{360}$$

**Onde:**
- **Q** = Vazão de pico (m³/s)
- **C** = Coeficiente de escoamento ou deflúvio (adimensional, 0 ≤ C ≤ 1)
- **I** = Intensidade de precipitação (mm/h)
- **A** = Área de contribuição ou bacia hidráulica (hectares)
- **360** = Fator de conversão de unidades (mm/h × ha = m³/s quando dividido por 360)

**Nota:** A constante 360 resulta de:
- 1 mm/h × 1 ha = 0,001 m × 10.000 m² = 10 m³/h = 10/3600 m³/s ≈ 1/360 m³/s

### 1.3 Hipóteses e Limitações

| Hipótese | Validação | Limitação Prática |
|----------|-----------|-------------------|
| Chuva uniforme na bacia | Válida para A < 5 km² | Falha em bacias grandes (A > 50 km²) |
| Regime permanente | Válida em período constante | Não captura picos transitórios |
| C constante temporalmente | Aproximada | C varia com umidade antecedente do solo |
| Relação linear Q vs. I | Válida para solos homogêneos | Falha com variação estratigráfica |
| Tempo de concentração (Tc) determinístico | Válida para projeto | Requer calibração local |

**Recomendação DNIT ES 131/86:**
- Use Método Racional para A ≤ 2 km²
- Para A > 2 km² e < 10 km², combine com método da curva-número (SCS)
- Para A > 10 km², use modelos chuva-vazão (HEC-HMS) ou dados hidrológicos observados

---

## 2. COMPONENTES DA EQUAÇÃO

### 2.1 Coeficiente de Escoamento (C)

O coeficiente C representa a fração da precipitação que se converte em escoamento superficial direto, desconsiderando perdas por infiltração, evapotranspiração e armazenamento em depressões.

#### 2.1.1 Valores de C por Tipo de Superfície (DNIT ES 131/86, Tabela 1)

| Tipo de Superfície | C (mín) | C (típ) | C (máx) | Observações |
|-------------------|---------|---------|---------|-------------|
| Pavimento asfáltico/concreto | 0,70 | 0,85 | 0,95 | Muito impermeável; pequena infiltração |
| Macadame | 0,40 | 0,60 | 0,75 | Permeabilidade média |
| Solo descoberto compactado | 0,30 | 0,50 | 0,70 | Infiltração moderada |
| Solo natural (pastos, grama) | 0,10 | 0,35 | 0,50 | Alta infiltração; cobertura vegetal retém água |
| Floresta densa | 0,05 | 0,20 | 0,35 | Máxima interceptação; solos permeáveis |
| Superfícies arborizadas (parques) | 0,10 | 0,25 | 0,40 | Efeito de amortecimento |
| Telhados (zinco, telha) | 0,75 | 0,90 | 0,95 | Superfícies praticamente impermeáveis |

#### 2.1.2 Coeficiente de Escoamento Ponderado para Bacias Heterogêneas

Quando a bacia drenante é composta por múltiplas superfícies:

$$C_{\text{médio}} = \frac{\sum (C_i \cdot A_i)}{\sum A_i}$$

**Exemplo de aplicação:** Para uma bacia com:
- 60% pavimento asfáltico (C = 0,85)
- 25% solo com grama (C = 0,35)
- 15% floresta (C = 0,20)

$$C_{\text{médio}} = \frac{(0,85 \times 60) + (0,35 \times 25) + (0,20 \times 15)}{100}$$
$$C_{\text{médio}} = \frac{51 + 8,75 + 3}{100} = 0,627 \approx 0,63$$

#### 2.1.3 Ajustes de C por Condições Especiais

**Tabela 2: Fatores de Correção para C**

| Condição | Fator de Correção | Justificativa |
|----------|-------------------|---------------|
| Chuva de projeto TR = 5 anos | ×0,95 | C menor em chuvas menos intensas |
| Chuva de projeto TR = 10 anos | ×1,00 | Referência (C nominal) |
| Chuva de projeto TR = 25 anos | ×1,05 | C aumenta com intensidade (saturação) |
| Chuva de projeto TR = 50 anos | ×1,10 | Solos próx. à saturação; menos infiltração |
| Chuva de projeto TR = 100 anos | ×1,15 | Todos os vazios preenchidos |
| Solo úmido antecedente | ×1,10 | Infiltração reduzida por saturação prévia |
| Solo seco antecedente | ×0,85 | Infiltração aumentada; vazios ainda disponíveis |

---

### 2.2 Intensidade de Precipitação (I)

A intensidade de precipitação é expressa em mm/h e obtida através de **curvas IDF** (Intensidade-Duração-Frequência) específicas da região.

#### 2.2.1 Curva IDF — Definição e Obtenção

Uma curva IDF relaciona:
- **I** = intensidade da chuva (mm/h)
- **D** = duração da chuva (min ou h)
- **TR** = período de retorno ou frequência (anos)

**Forma geral (Equação de Sherman ou Talbot):**

$$I = \frac{a}{(D + b)^c}$$

**Ou (Talbot modificado):**

$$I = \frac{K \cdot T_R^m}{(D + c)^n}$$

**Onde:**
- **K, m, n, a, b, c** = parâmetros calibrados para cada localidade
- **TR** = período de retorno (anos)

#### 2.2.2 Exemplo — Curva IDF Brasília (representativa para planalto central)

**Tabela 3: Intensidades IDF para Brasília-DF** (dados sintetizados de 30 anos de observação INMET)

| Duração (min) | TR=5a (mm/h) | TR=10a (mm/h) | TR=25a (mm/h) | TR=50a (mm/h) | TR=100a (mm/h) |
|---------------|--------------|---------------|---------------|---------------|----------------|
| 5 | 108 | 135 | 168 | 199 | 232 |
| 10 | 92 | 115 | 142 | 168 | 196 |
| 15 | 80 | 100 | 123 | 146 | 170 |
| 20 | 72 | 90 | 111 | 132 | 154 |
| 30 | 60 | 75 | 93 | 110 | 129 |
| 60 | 42 | 52 | 65 | 77 | 90 |
| 120 | 28 | 35 | 43 | 51 | 60 |

#### 2.2.3 Período de Retorno (TR) — Critério DNIT

**Tabela 4: Período de Retorno Recomendado — DNIT ES 131/86**

| Elemento de Drenagem | TR Recomendado | Justificativa |
|----------------------|----------------|-|
| Sarjeta de rodovia (classe C/D) | 5–10 anos | Baixa exposição de tráfego; falha ocasional tolerável |
| Valeta de boquete lateral | 5–10 anos | Funciona sem risco crítico mesmo em transbordamento |
| Bueiro simples (Ø ≤ 1,0 m) | 10–25 anos | Ponto crítico; falha causa alagamento |
| Bueiro duplo/múltiplo ou galeria | 25–50 anos | Infraestrutura crítica; risco de colapso |
| Ponte rodoviária (vão livre) | 50–100 anos | Obra de engenharia permanente; risco zero aceitável |
| Galeria urbana (drenagem pluvial) | 10–25 anos | Zona urbana; riscos à população |

**Prática mais comum (rodovia federal):** TR = 10 anos para dimensionamento de bueiros e TR = 25 anos para galerias principais.

#### 2.2.4 Tempo de Concentração (Tc) — Escolha da Duração D

A duração da chuva de projeto (D) é igualada ao **tempo de concentração** (Tc), que é o tempo para a água da chuva, originária do ponto mais afastado da bacia, alcançar a seção de interesse.

$$D = T_c$$

**Fórmulas para Tc (solos brasileiros):**

**Tabela 5: Fórmulas de Tempo de Concentração**

| Fórmula | Expressão | Aplicação | Observação |
|---------|-----------|-----------|-----------|
| **Kirpich (1940)** | $T_c = 0,01947 \cdot L^{0,77} \cdot S^{-0,385}$ | Pequenas bacias (A < 0,5 km²) | L em m; S em m/m; Tc em min. Conservadora. |
| **SCS (1975)** | $T_c = \frac{(L/60 + 1,67)^{0,8}}{(1000/CN - 9)^{0,7} \cdot S^{0,5}}$ | Bacias 0,5–10 km² | Baseada em CN (curve number); precisa hidrologia local. |
| **FAA/DNIT** | $T_c = 2,5 + \frac{L}{120 + S}$ | Bacias < 5 km² | L em m; S em %; Tc em min. Prática brasileira. |
| **Ven Te Chow** | $T_c = 0,123 \cdot (L/S^{0,5})^{0,64}$ | Bacias médias (A < 50 km²) | L em km; S em m/m; Tc em h. Ajuste regional necessário. |

**Recomendação prática DNIT para rodovias:**
- Use **Kirpich** ou **FAA/DNIT** para pequenas bacias (< 2 km²)
- Valide com observação in loco: compare Tc calculado com tempo de percurso da água em vala/terreno

#### 2.2.5 Exemplo Numérico — Cálculo de Tc

**Dado:** Bacia lateral para bueiro em rodovia BR:
- Comprimento hidráulico: L = 450 m
- Declividade média: S = 5,5% = 0,055 m/m

**Método FAA/DNIT:**
$$T_c = 2,5 + \frac{450}{120 + 5,5} = 2,5 + \frac{450}{125,5} = 2,5 + 3,58 = 6,08 \text{ min}$$

Usar D ≈ 6 min (ou arredondar para 5 ou 10 min conforme disponibilidade de tabela IDF)

---

### 2.3 Área de Contribuição (A)

A área de contribuição é a área da bacia hidrográfica drenada até o ponto de interesse.

#### 2.3.1 Determinação da Área

**Métodos:**
1. **Cartas topográficas** (IBGE 1:50.000 ou 1:100.000): medir com planímetro ou dividers
2. **Imagens de satélite/Google Earth**: demarcar limite de bacia; medir digitalmente
3. **Levantamento topográfico/aerofotogrametria**: mais preciso para projetos críticos
4. **Software GIS** (QGIS, ArcGIS): integrar DEM (modelo digital de elevação) e traçar divisor de águas automaticamente

#### 2.3.2 Conversão de Unidades

$$A \text{ (hectares)} = A \text{ (km²)} \times 100$$
$$A \text{ (m²)} = A \text{ (hectares)} \times 10.000$$

**Exemplo:** Bacia de 2,5 km² = 250 hectares = 2.500.000 m²

#### 2.3.3 Limitações por Área

| Intervalo de A | Aplicabilidade do Método Racional | Observação |
|----------------|------------------------------------|-----------|
| A < 0,5 km² | Excelente; recomendado | Pequenas bacias urbanas, boquetes laterais |
| 0,5 ≤ A < 2 km² | Muito boa | Zona de conforto DNIT; boa correlação com medições |
| 2 ≤ A < 5 km² | Boa com ajustes | Introduzir fator de redução para não-uniformidade de chuva |
| 5 ≤ A < 10 km² | Restrita; combinar métodos | Usar Método Racional + SCS ou calibração local |
| A ≥ 10 km² | Não recomendado | Usar modelos hidrológicos chuva-vazão (HEC-HMS, MGB-IPH) |

---

## 3. FÓRMULAS DERIVADAS E APLICAÇÕES

### 3.1 Fórmula Expandida com Fatores de Correção

Para análises mais rigorosas, é comum incluir fatores de segurança e ajuste:

$$Q = \frac{C_{\text{médio}} \cdot f_c \cdot I(D, T_R) \cdot A}{360}$$

**Onde:**
- **Cmédio** = coeficiente ponderado (seção 2.1.2)
- **fc** = fator de correção (Tabela 2)
- **I(D, TR)** = intensidade retirada da curva IDF em função de D e TR
- **A** = área em hectares

### 3.2 Vazão Específica (Descarga Unitária)

Para comparações entre bacias ou análises paramétricas:

$$q = \frac{Q}{A} = \frac{C \cdot I}{360} \text{ (m³/s/ha)}$$

A vazão específica é útil para:
- Verificar consistência entre projetos similares
- Detectar anomalias em estimativas
- Comparar com dados históricos regionais

**Exemplo:** Se q = 0,05 m³/s/ha e A = 100 ha, então Q = 5 m³/s.

### 3.3 Velocidade Média de Escoamento

Após estimar Q, calcula-se a velocidade necessária em canais/canaletas:

$$V = \frac{Q}{A_{\text{seção}}}$$

**Onde:**
- **V** = velocidade média (m/s)
- **Aseção** = área da seção transversal do canal/bueiro (m²)

Verificar se V atende limites DNIT:
- **Vmín** ≈ 0,60 m/s (risco de assoreamento)
- **Vmáx** ≈ 2,5–3,0 m/s para argila/macadame; até 4 m/s para concreto (risco de erosão)

---

## 4. EXEMPLOS NUMÉRICOS COM VALORES REAIS

### Exemplo 1: Boquete Lateral — Pequena Bacia (Vd = 100 km/h)

**Dados de projeto:**
- Localização: Rodovia BR-XXX, planalto central (similar Brasília)
- Vd (velocidade de projeto) = 100 km/h
- Comprimento de boquete até bueiro = 300 m
- Área de bacia lateral = 1,2 km² = 120 hectares
- Superfícies: 40% pasto (C = 0,35); 60% solo compactado (C = 0,50)
- Período de retorno desejado: TR = 10 anos (bueiro simples)
- Declividade média da bacia: S = 6%

**Passo 1: Calcular Cmédio**

$$C_{\text{médio}} = \frac{(0,35 \times 40) + (0,50 \times 60)}{100} = \frac{14 + 30}{100} = 0,44$$

**Passo 2: Estimar Tc**

Usando FAA/DNIT com L = 300 m e S = 6% = 0,06 m/m:

$$T_c = 2,5 + \frac{300}{120 + 6} = 2,5 + \frac{300}{126} = 2,5 + 2,38 = 4,88 \approx 5 \text{ min}$$

**Passo 3: Obter I da tabela IDF (Brasília, TR = 10a, D = 5 min)**

Interpolando Tabela 3: I ≈ 135 mm/h

**Passo 4: Aplicar Método Racional**

$$Q = \frac{C \cdot I \cdot A}{360} = \frac{0,44 \times 135 \times 120}{360}$$
$$Q = \frac{7.128}{360} = 19,8 \text{ m³/s}$$

**Resultado:** Vazão de projeto Q = **19,8 m³/s** ≈ 20 m³/s (valor de dimensionamento)

**Verificação com vazão específica:**
$$q = \frac{Q}{A} = \frac{19,8}{120} = 0,165 \text{ m³/s/ha}$$

Comparar com padrão regional (0,10–0,20 m³/s/ha para planalto): ✓ Consistente.

---

### Exemplo 2: Drenagem Urbana — Bacia Heterogênea Mista

**Dados:**
- Zona urbana em região metropolitana
- Área total = 0,35 km² = 35 hectares
- Composição:
  - 50% pavimento/telhados (C = 0,90)
  - 30% solos compactados (ruas/estacionamentos; C = 0,60)
  - 20% áreas verdes (parques, praças; C = 0,25)
- Período de retorno: TR = 10 anos (galeria pluvial urbana)
- Localização: Rio de Janeiro (região costeira)
- Comprimento hidráulico: L = 800 m; S = 3,5%

**Passo 1: Cmédio**

$$C_{\text{médio}} = \frac{(0,90 \times 50) + (0,60 \times 30) + (0,25 \times 20)}{100}$$
$$C_{\text{médio}} = \frac{45 + 18 + 5}{100} = 0,68$$

**Passo 2: Tc (FAA/DNIT)**

$$T_c = 2,5 + \frac{800}{120 + 3,5} = 2,5 + \frac{800}{123,5} = 2,5 + 6,48 = 8,98 \approx 9 \text{ min}$$

**Passo 3: I da curva IDF — Rio de Janeiro (TR = 10a, D = 9 min)**

Usando dados INMET-RJ sintetizados: I ≈ 110 mm/h (região costeira tem intensidades menores que planalto)

**Passo 4: Vazão**

$$Q = \frac{0,68 \times 110 \times 35}{360} = \frac{2.618}{360} = 7,27 \text{ m³/s}$$

**Resultado:** Q ≈ **7,3 m³/s** (dimensionar galeria para este valor)

---

### Exemplo 3: Bueiro em Rodovia Federal — Influência do TR

**Cenário:** Mesmo boquete do Exemplo 1, mas variando TR

| TR (anos) | I (mm/h) | C (ajustado) | Q (m³/s) | Observação |
|-----------|----------|--------------|----------|-----------|
| 5 | 110 | 0,42 | 16,7 | Enchente rara; transbordamento ocasional |
| **10** | **135** | **0,44** | **19,8** | **Prática DNIT — recomendado** |
| 25 | 167 | 0,46 | 26,4 | Maior segurança; dimensiona bueiro maior |
| 50 | 199 | 0,48 | 31,9 | Risco muito baixo; sobre-dimensionamento |

**Interpretação:** Escolher TR = 10 anos balanceia custo vs. segurança para rodovia federal.

---

## 5. TABELAS NORMATIVAS — DNIT ES 131/86

### Tabela 6: Coeficientes de Escoamento Recomendados — Resumo DNIT

| Tipologia | C (mín) | C (máx) | Nota DNIT |
|-----------|---------|---------|----------|
| Via urbana pavimentada | 0,80 | 0,95 | Incluir sarjetas e meios-fios |
| Estacionamento de veículos | 0,75 | 0,85 | Considerar zona de filtração se houver |
| Vias de terra/macadame | 0,50 | 0,70 | Usar valor mínimo se solo de má drenagem |
| Terrenos com grama natural | 0,20 | 0,40 | Solos bem drenados usar C = 0,25 |
| Encostas com cobertura vegetal | 0,10 | 0,30 | Florestas naturais usar C ≤ 0,15 |
| Topos de corte (rocha exposta) | 0,85 | 0,95 | Praticamente impermeável |
| Valetas de boquete (terra ou grama) | 0,30 | 0,50 | Infiltração em valeta reduz deflúvio |
| Taludes com grama plantada | 0,25 | 0,45 | Depende de ano de plantio e manutenção |

### Tabela 7: Critérios Mínimos de Projeto — DNIT ES 131/86

| Elemento | Critério | Limite/Observação |
|----------|----------|-------------------|
| **Velocidade mínima em canais** | Vmín | 0,60 m/s (previne assoreamento) |
| **Velocidade máxima** | Vmáx | 2,5 m/s (terra); 3,5 m/s (concreto) |
| **Declividade mínima de sarjeta** | Smín | 0,5% (urbano); 0,3% (rodovia) |
| **Declividade máxima de valeta** | Smáx | 6–8% (controlar erosão com proteção) |
| **Altura de água máxima em sarjeta** | h | 0,20–0,30 m (não obstruir circulação) |
| **Borda livre em canal** | BL | 0,30 m (mín.) para sistema aberto; 1,0 m para fechado |
| **Período de retorno (bueiro)** | TR | 10–25 anos (conforme tipo de via) |
| **Período de retorno (galeria)** | TR | 25–50 anos (obra crítica) |

---

## 6. CASOS REAIS DE APLICAÇÃO

### Caso 6.1: Bueiro Simples — Rodovia BR-381 (MG)

**Contexto:** Via de elevado padrão; tráfego 15.000 veículos/dia; Vd = 100 km/h.

**Levantamento de campo:**
- Bacia lateral medida em ortofotos IBGE: A = 2,8 km² = 280 ha
- Superfícies: 45% pasto (C = 0,30); 35% solo com cultivo (C = 0,40); 20% floresta ciliar (C = 0,15)
- Declividade média estimada: S = 4,2%
- Comprimento do escoamento: L ≈ 900 m

**Cálculos:**

1. **Cmédio:**
$$C = \frac{(0,30 \times 45) + (0,40 \times 35) + (0,15 \times 20)}{100} = \frac{13,5 + 14 + 3}{100} = 0,305 \approx 0,31$$

2. **Tc (FAA/DNIT):**
$$T_c = 2,5 + \frac{900}{120 + 4,2} = 2,5 + 7,18 = 9,68 \approx 10 \text{ min}$$

3. **I (Minas Gerais, TR = 10a, D = 10 min):** I ≈ 112 mm/h (região de transição planalto-litoral)

4. **Q:**
$$Q = \frac{0,31 \times 112 \times 280}{360} = \frac{9.705,6}{360} = 27,0 \text{ m³/s}$$

**Decisão de projeto:** Especificar bueiro duplo 1,0 m ou triplo 0,80 m para absorver Q = 27 m³/s mantendo V < 2,5 m/s.

---

### Caso 6.2: Drenagem de Canteiro Central — Rodovia Urbana (SP)

**Contexto:** Rodovia em zona urbana densa (RMSP); canteiro com áreas verdes; Vd = 80 km/h.

**Dados:**
- Setor drenado: 450 m de canteiro; largura efetiva = 6 m
- Área de contribuição = 450 × 6 = 2.700 m² = 0,27 ha
- Superfícies: 60% asfalto/concreto (C = 0,85); 40% áreas verdes (C = 0,30)
- Declividade longitudinal: S = 1,2%

**Projeto de canaleta (drenagem do canteiro):**

1. **Cmédio:**
$$C = 0,60 \times 0,85 + 0,40 \times 0,30 = 0,51 + 0,12 = 0,63$$

2. **Tc (muito curto; assumir 3 min para área urbana compacta)**

3. **I (RMSP, TR = 10a, D = 3 min):** I ≈ 160 mm/h (região com IDF elevada)

4. **Q:**
$$Q = \frac{0,63 \times 160 \times 0,27}{360} = \frac{27,216}{360} = 0,076 \text{ m³/s} = 76 \text{ L/s}$$

**Projeto:** Canaleta triangular de concreto com:
- Profundidade h = 0,30 m; base b = 0,50 m
- Seção = 0,5 × 0,30/2 = 0,075 m² ≈ Q/V = 0,076/1,5 ✓ OK
- Declividade = 1,2% garante V = 1,5 m/s (ideal, entre 0,6–2,5 m/s)

---

### Caso 6.3: Bacia de Infiltração — Projeto Sustentável (DF)

**Contexto:** Estacionamento com drenagem de baixo impacto (LID — Low Impact Development); A = 0,08 ha.

**Objetivo:** Reduzir vazão de pico por infiltração no solo.

**Dados:**
- Área impermeável (asfalto): 0,08 ha; C = 0,90
- Solo subjacente: areia fina com cascalho; infiltração k = 25 mm/h
- Periodo de retorno: TR = 10 anos; Brasília

**Análise sem LID (canaleta convencional):**

Tc = 2 min (área pequena, urbana); I ≈ 150 mm/h

$$Q = \frac{0,90 \times 150 \times 0,08}{360} = \frac{10,8}{360} = 0,030 \text{ m³/s} = 30 \text{ L/s}$$

**Análise com LID (bacia de infiltração):**

A bacia de infiltração reduz efetivamente C devido à retenção:
- Profundidade da bacia: h = 0,50 m
- Volume armazenado: V_arm = 0,08 ha × 0,50 m = 400 m³ (muito grande; escala 1:200 = 2 m³)
- Capacidade de infiltração durante chuva: q_inf = 25 mm/h × 0,08 ha = 0,020 m³/s = 20 L/s
- Vazão de pico reduzida: Q_LID = 30 – 20 = 10 L/s (redução de 67%)

**Benefício:** Reduzir dimensionamento da canaleta jusante; compatibilizar com capacidade da galeria existente.

---

## 7. VERIFICAÇÕES E CONTROLES DE QUALIDADE

### 7.1 Sanidade de Resultados

Antes de adotar Q calculado, validar:

| Controle | Verificação | Ação |
|----------|-------------|------|
| **Vazão específica** | q = Q/A ∈ [0,05; 0,30] m³/s/ha | Se q < 0,05 ou q > 0,30, revisar C e I |
| **Coeficiente C** | C ∈ [0,1; 0,95] | Se C < 0,05, bacia é drenada (inadequado); se C > 1,0, erro de cálculo |
| **Duração D = Tc** | Tc ∈ [3 min; 30 min] | Se Tc < 3, usar 3 min (limite hidrológico); se Tc > 30, verificar se A > 10 km² |
| **Intensidade I** | I deve estar em tabela IDF regional | Se I indisponível, coletar dados INMET ou extrapolar curva |
| **Área A** | A ∈ [0,05; 5] ha para Método Racional puro | Se A > 5 ha, adicionar fator de redução ou usar outro método |
| **Velocidade no canal** | V_cálc ∈ [0,6; 3,5] m/s | Se V < 0,6, risco de assoreamento; se V > 3,5, proteção contra erosão |

### 7.2 Comparação com Dados Históricos Regionais

Quando disponíveis:
- Comparar Q estimado com vazões máximas observadas em estações fluviométricas próximas
- Ajustar C iterativamente até consonância com dados
- Documentar diferenças e justificar (mudanças de uso de solo, urbanização, etc.)

### 7.3 Análise de Sensibilidade

Verificar impacto de variações em C e I:

$$\Delta Q = Q \cdot \left( \frac{\Delta C}{C} + \frac{\Delta I}{I} \right)$$

**Exemplo:** Se C = 0,50 (±10%) e I = 120 mm/h (±15%), Q varia de –20% a +30%. Dimensionar com margem de segurança (usar Q × 1,2).

---

## 8. REFERÊNCIAS BIBLIOGRÁFICAS

### Normativas Brasileiras

1. **DNIT (1986).** ES 131/86 — *Drenagem Superficial de Rodovias*. Departamento Nacional de Infraestrutura de Transportes.

2. **ABNT (2004).** NBR 10844 — *Instalações prediais de águas pluviais*. Associação Brasileira de Normas Técnicas.

3. **ABNT (2007).** NBR 12.211–12.218 — *Saneamento — Drenagem urbana*. Série de normas de projeto e execução.

### Hidrologia e Método Racional

4. **Tucci, C. E. M. (2015).** *Hidrologia: Ciência e Aplicação* (4ª ed.). EDUFRGS, Porto Alegre.
   - Cap. 7: Método Racional e aplicações em pequenas bacias.

5. **Chow, V. T.; Maidment, D. R.; Mays, L. W. (1988).** *Applied Hydrology*. McGraw-Hill, New York.
   - Cap. 6: Design flood frequency; Método Racional (pp. 192–226).

6. **McCuen, R. H. (2005).** *Hydrologic Analysis and Design* (3ª ed.). Prentice Hall.
   - Cap. 5: Rational Method; time of concentration (pp. 107–155).

### Curvas IDF Brasil

7. **Marcuzzo, F. F. N.; Andrade, L. R.; Melo, D. C. R. (2011).** "Índices de precipitação máxima em 24 horas e relação com o comportamento do relevo no Brasil." *Revista Brasileira de Climatologia*, 8, 17–36.

8. **INMET (2023).** *Banco de Dados Meteorológicos para Pesquisa e Ensino (BDMEP)*. Instituto Nacional de Meteorologia. http://www.inmet.gov.br

### Drenagem Rodoviária Específica

9. **DER-SP (2018).** *Manual de Drenagem de Rodovias*. Departamento de Estradas de Rodagem do Estado de São Paulo.

10. **CEMAT/UFRGS (2005).** "Drenagem de Rodovias: Diretrizes Técnicas." Revista de Engenharia da UFRGS, Porto Alegre.

### Métodos Alternativos (complementares)

11. **Poff, N. L.; Hart, D. D. (2002).** "How dams vary and why it matters for the emerging science of dam removal." *BioScience*, 52(8), 659–668.
    - Impacto ambiental de drenagem; referência para estudos de impacto.

12. **SCS (Soil Conservation Service, 1972).** *National Engineering Handbook: Section 4 Hydrology*.
    - Curva-número; alternativa ao Método Racional para bacias médias.

---

## 9. RESUMO EXECUTIVO — FLUXOGRAMA DE CÁLCULO

```
PROJETO DE DRENAGEM — MÉTODO RACIONAL

┌─ Levantamento topográfico e de solos
│  ├─ Área de bacia (A, hectares)
│  ├─ Superfícies (pavimento, solo, vegetal)
│  └─ Declividade média (S, %)

├─ Definir período de retorno (TR)
│  ├─ Bueiro simples: TR = 10 a
│  ├─ Galeria principal: TR = 25–50 a
│  └─ Obra de arte especial: TR = 50–100 a

├─ Calcular tempo de concentração (Tc)
│  ├─ Usar fórmula FAA/DNIT ou Kirpich
│  └─ D ← Tc (duração de chuva)

├─ Obter coeficiente C
│  ├─ Identificar superfícies (% pavimento, solo, grama, floresta)
│  ├─ Usar Tabela 1 (C por tipo)
│  └─ Ponderar: C_médio = Σ(C_i × A_i) / Σ A_i

├─ Consultar curva IDF regional
│  ├─ I(D, TR) → tabela ou gráfico local
│  └─ Interpolação se necessário

├─ Aplicar fórmula:
│  └─ Q = (C × I × A) / 360  [m³/s]

├─ Verificações:
│  ├─ q = Q/A ∈ [0,05; 0,30] m³/s/ha
│  ├─ C ∈ [0,1; 0,95]
│  ├─ V_canal = Q / A_seção ∈ [0,6; 3,5] m/s
│  └─ Comparar com dados regionais

└─ Dimensionar elemento de drenagem (bueiro, galeria, sarjeta)
   com Q de projeto
```

---

## 10. APÊNDICE — TABELA ISOIETA (exemplo)

**Tabela A1: Isoietas de Precipitação Máxima em 24h — Brasil**

| Região | Pmáx 10 anos (mm) | Pmáx 25 anos (mm) | Fonte/Período |
|--------|-------------------|-------------------|---------------|
| Brasília-DF | 95–110 | 120–135 | INMET, 1961–2020 |
| São Paulo-SP | 85–100 | 105–125 | DAEE, 1960–2015 |
| Rio de Janeiro-RJ | 100–120 | 125–150 | Marinha do Brasil, 1961–2020 |
| Belo Horizonte-MG | 80–95 | 100–120 | CPRM, 1961–2020 |
| Manaus-AM | 110–140 | 140–170 | INMET, 1961–2020 (chuvas intensas) |
| Fortaleza-CE | 70–85 | 85–105 | FUNCEME, 1965–2020 (semiárido) |

**Nota:** Valores são indicativos. Sempre consultar dados locais de estação meteorológica ou base INMET antes de projeto.

---

**FIM DO DOCUMENTO**  
Preparado para: Manta Associados  
Versão de trabalho: 1.0 — disponível para revisão técnica e feedback

