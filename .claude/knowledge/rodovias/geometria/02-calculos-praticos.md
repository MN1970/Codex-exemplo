# Geometria de Rodovias — Cálculos Práticos & Casos de Projeto

**Versão**: 1.0  
**Data**: 2026-08-03  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:calc`

---

## 1. Casos de Projeto Típicos

### Caso 1: Rodovia Federal (BR) — Classe I

**Entrada do Projeto**:
- Velocidade de projeto: **Vd = 100 km/h**
- Classe: **BR (Federal)**
- Topografia: **Ondulada**
- Volume: **3 milhões veículos/ano** → **~8,200 vpd** (veículos por dia)
- Pavimento: **CBUQ** (concreto betuminoso usinado a quente)

**Passo 1: Definir Padrões Geométricos**

| Elemento | Valor | Fonte |
|----------|-------|--------|
| Velocidade de projeto | 100 km/h | Entrada |
| Faixa de rolamento | 3.60 m | DNIT BR |
| Acostamento | 2.50 m | DNIT BR |
| Superelevação máxima | 0.08 (8%) | DNIT |
| Coeficiente atrito | 0.15 | Normal |
| Declividade máxima | 6% | Rodovia |

**Passo 2: Calcular Raio Mínimo para Curva Horizontal**

```
R_mín = V² / (127 × (e_máx + f))
R_mín = 100² / (127 × (0.08 + 0.15))
R_mín = 10000 / (127 × 0.23)
R_mín = 10000 / 29.21
R_mín = 342.3 m

Adotar: R = 350 m (arredonda para multiplo de 50m)
```

**Passo 3: Superelevação Efetiva para R = 350m**

```
e = V² / (127 × R) - f
e = 10000 / (127 × 350) - 0.15
e = 10000 / 44450 - 0.15
e = 0.225 - 0.15
e = 0.075 = 7.5%

Usar: e = 7.5% (dentro do máximo 8%)
```

**Passo 4: Comprimento de Transição (Clotóide)**

```
Parâmetro mínimo da clotóide:
A² = R × L_c

Comprimento mínimo:
L_mín = 0.036 × V³ / R
L_mín = 0.036 × (100)³ / 350
L_mín = 0.036 × 1000000 / 350
L_mín = 36000 / 350
L_mín = 102.9 m

Adotar: L_c = 110 m

Parâmetro A:
A² = 350 × 110 = 38500
A = 196.2 m
```

**Passo 5: Verificar Tangente Mínima Entre Curvas**

```
Comprimento mínimo tangente:
L_t = 0.28 × Vd
L_t = 0.28 × 100
L_t = 28 m

Se existir tangente com 50m, está OK.
```

**Passo 6: Distância de Visibilidade de Parada**

```
d_parada = V × 0.7 + V² / (254 × f)
d_parada = 100 × 0.7 + 10000 / (254 × 0.40)
d_parada = 70 + 10000 / 101.6
d_parada = 70 + 98.4
d_parada = 168.4 m
```

**Passo 7: Alinhamento Vertical — Rampa e Curva Vertical**

Exemplo: PI (ponto de interseção vertical) em elevação 450m, com rampa ascendente de 5%, seguida de rampa descendente de 4%.

```
Δi = |5% - (-4%)| = 9%

Comprimento mínimo de curva vertical:
L = (|Δi| × V²) / (395 + 2.6 × V)
L = (9 × 100²) / (395 + 2.6 × 100)
L = 90000 / (395 + 260)
L = 90000 / 655
L = 137.4 m

Adotar: L = 140 m (múltiplo de 20m)
```

**Passo 8: Seção Transversal Padrão**

```
Estrutura no trecho:

                  3.60m          2.50m
    ├─────────────────────────────────┤
    ├──────┬──────────┬──────┬────────┤
    ║ AC   │  Faixa 1 │ Faixa│  AC    ║
    ║ 2.5m │ 3.60m   │ 2  │ 2.5m   ║
    │      │ 3.60m   │      │        │
    └──────┴──────────┴──────┴────────┘
    
    Total de plataforma: 2.5 + 3.6 + 3.6 + 2.5 = 12.2m
    
    Inclinação transversal normal: 2% (centro para bordas)
    Em curva: superelevação 7.5% (5.5% de ambos lados do eixo)
```

---

### Caso 2: Rodovia Estadual — Classe II

**Entrada do Projeto**:
- Velocidade de projeto: **Vd = 80 km/h**
- Classe: **Estadual**
- Topografia: **Montanhosa**
- Volume: **400 mil veículos/ano** → **~1,100 vpd**
- Pavimento: **CBUQ 5cm**

**Passo 1-2: Padrões e Raio Mínimo**

| Elemento | Valor |
|----------|-------|
| Faixa | 3.30 m |
| Acostamento | 1.50 m |
| e_máx | 0.08 |
| f | 0.16 |

```
R_mín = 80² / (127 × (0.08 + 0.16))
R_mín = 6400 / (127 × 0.24)
R_mín = 6400 / 30.48
R_mín = 209.9 m

Adotar: R = 220 m
```

**Passo 3: Superelevação**

```
e = 80² / (127 × 220) - 0.16
e = 6400 / 27940 - 0.16
e = 0.229 - 0.16
e = 0.069 = 6.9%

Usar: e = 7.0%
```

**Passo 4: Clotóide**

```
L_mín = 0.036 × 80³ / 220
L_mín = 0.036 × 512000 / 220
L_mín = 18432 / 220
L_mín = 83.8 m

Adotar: L_c = 90 m
A = √(220 × 90) = √19800 = 140.7 m
```

**Passo 5: Distância de Visibilidade**

```
d_parada = 80 × 0.7 + 80² / (254 × 0.40)
d_parada = 56 + 6400 / 101.6
d_parada = 56 + 63
d_parada = 119 m
```

**Passo 6: Rampa Máxima (Montanhosa)**

```
Rampa máxima permitida: 7% (topografia montanhosa)

Se rampa sobe 7% e desce 5%:
Δi = 12%
L = (12 × 80²) / (395 + 2.6 × 80)
L = 76800 / (395 + 208)
L = 76800 / 603
L = 127.4 m

Adotar: L = 130 m
```

---

## 2. Verificação de Visibilidade em Curva Horizontal

**Problema**: Verificar se a curva com R=500m, d_parada=137m tem visibilidade suficiente com talude de corte de 1:1.

**Solução**:

```
Ângulo central θ para visibilidade:
θ = 2 × arcsen(d / 2R)
θ = 2 × arcsen(137 / 1000)
θ = 2 × arcsen(0.137)
θ = 2 × 7.87°
θ = 15.74°

Flecha de recuo necessária:
f = R - √(R² - (d/2)²)
f = 500 - √(500² - 68.5²)
f = 500 - √(250000 - 4692)
f = 500 - √245308
f = 500 - 495.3
f = 4.7 m

Logo, é necessário um recuo de banqueta mínimo de 4.7m
para garantir visibilidade.
```

---

## 3. Cálculos de Superelevação — Perfil de Seção Transversal

**Entrada**: Curva com R=400m, Vd=100 km/h, largura de pavimento = 7.2m (2 faixas)

**Passo 1: Superelevação Global**

```
e = 100² / (127 × 400) - 0.15
e = 10000 / 50800 - 0.15
e = 0.197 - 0.15
e = 0.047 = 4.7%
```

**Passo 2: Transição de Superelevação**

Comprimento de transição (clotóide e tangente):
```
L_trans = (e × a) / (Δe/ΔL)

Onde:
- e = 0.047 (4.7%)
- a = 7.2 m (largura total pavimento)
- Δe/ΔL = 1/150 (máximo permitido)

L_trans = (0.047 × 7.2) / (1/150)
L_trans = 0.3384 / 0.00667
L_trans = 50.8 m

Adotar: L_trans = 60 m (tangente + parte de clotóide)
```

**Passo 3: Cota de Bordo (elevação em cada faixa)**

No meio da curva (seção transversal):

```
Seção de entrada (com superelevação):

Eixo (centro): elevação 0
Borda interna (lado côncavo): -1% × 3.6m = -0.036m
Borda externa (lado convexo): +4.7% × 3.6m = +0.169m

Total de desnível: 0.036 + 0.169 = 0.205m ≈ 20.5cm

Na prática, usa-se rotação de seção transversal:
- Meia largura gira para içar a borda externa
- Efeito visual: borda externa ~20cm acima da interna
```

---

## 4. Orçamento SICRO — Quantitativos Geométricos

**Exemplo para 1 km de rodovia federal (dupla, Vd=100 km/h)**

### 4.1 Pavimento e Acostamento

```
Largura de pavimento (2 faixas): 7.20 m
Acostamento por lado: 2.50 m × 2 = 5.00 m
Total faixa de rolamento: 7.20 + 5.00 = 12.20 m

Comprimento: 1000 m

Quantitativos:
- Pavimento CBUQ 5cm: 7.20 × 1000 = 7,200 m²
- Pavimento CBUQ 4cm (acostamento): 5.00 × 1000 = 5,000 m²
- BGS (base granular 15cm): 12.20 × 1000 = 12,200 m²
- Sub-base (se necessário): 12.20 × 1000 = 12,200 m²
```

### 4.2 Terraplenagem

```
Seção média de corte: 150 m² (varia por topografia)
Seção média de aterro: 100 m²

Quantitativos:
- Escavação/corte: 150 × 1000 = 150,000 m³
- Aterro/compactação: 100 × 1000 = 100,000 m³
- Empréstimo (se deficiente): ~20% do aterro = 20,000 m³
```

### 4.3 Bananquetas e Taludes

```
Talude médio: 1:1.5 (corte), 1:2 (aterro)

Comprimento de talude:
- Corte (altura média 8m): 8 × 1.5 = 12 m por lado
- Aterro (altura média 5m): 5 × 2 = 10 m por lado

Hidrossemeadura/proteção:
- Talude corte: 12 × 1000 = 12,000 m²
- Talude aterro: 10 × 1000 = 10,000 m²
- Total: 22,000 m²
```

### 4.4 Serviços Geométricos (Auxiliares)

```
- Limpeza e desmatamento: 1000 m × 50m faixa = 50,000 m²
- Compactação de subleito: 12.20 × 1000 = 12,200 m²
- Drenagem superficial (banquetas): 1000 m × 2 = 2000 m
```

### 4.5 Cotação SICRO (Exemplo de Preço — Fevereiro 2026)

Tabela simplificada de custos unitários SICRO:

| Item | Unidade | Custo SICRO | Quantidade | Total |
|------|---------|-----------|-----------|--------|
| Escavação/corte | m³ | R$ 8.50 | 150,000 | R$ 1,275,000 |
| Aterro comp. | m³ | R$ 12.00 | 100,000 | R$ 1,200,000 |
| CBUQ 5cm | m² | R$ 95.00 | 7,200 | R$ 684,000 |
| CBUQ 4cm (AC) | m² | R$ 85.00 | 5,000 | R$ 425,000 |
| BGS 15cm | m² | R$ 35.00 | 12,200 | R$ 427,000 |
| Hidrossemeadura | m² | R$ 2.50 | 22,000 | R$ 55,000 |
| Drenagem | m | R$ 150.00 | 2,000 | R$ 300,000 |
| **SUBTOTAL** | | | | **R$ 4,366,000** |
| **Margem/lucro (+20%)** | | | | **R$ 873,200** |
| **TOTAL (1 km)** | | | | **~R$ 5,239,200** |

**Custo/km: R$ 5.2 M** (para rodovia federal dupla, terreno ondulado)

---

## 5. Exemplo Real: BR-116 (Trecho SP-MG)

**Dados Históricos Reais** (consultar DNIT/bancos de dados):

| Parâmetro | Valor |
|-----------|-------|
| Velocidade de projeto | 100 km/h |
| Extensão total | 1,360 km |
| Raios mínimos adotados | 350-500m |
| Superelevação média | 5-7% |
| Declive máximo | 6% |
| Curvas de transição | Clotóide (A=150-200m) |
| Seção transversal | 12.2m pavimento + acostamentos |
| Pavimento | CBUQ 5cm + BGS 20cm |
| Status | Duplicação 80% (2024) |

**Lições**:
- Rodovias federais duplas usam R ≥ 350m
- Superelevação varia conforme micro-topografia
- Aderência ao DNIT ES 101 é obrigatória
- Orçamento SICRO é crítico para viabilidade

---

## 6. Ferramentas Digitais & Softwares

### 6.1 MX Road (Bentley)

```
Entrada:
- Alinhamento horizontal (dwg/xml)
- Perfil vertical
- Seção transversal padrão
- Cotas de projeto

Saída:
- Relatório geométrico (DNIT-compatível)
- Quantitativos de terraplenagem
- Perfil de superelevação
- Desenhos automatizados (plantas/seções)
```

### 6.2 Civil 3D (Autodesk)

```
Fluxo:
1. Importar topografia (survey/drone)
2. Criar alinhamento horizontal
3. Criar perfil vertical (linhas e parábolas)
4. Definir seção transversal tipo
5. Gerar corridors (superfícies de projeto)
6. Extrair quantitativos
7. Exportar para dwg/pdf
```

### 6.3 Python Scripts (Customização)

Exemplo: calcular raio mínimo iterativamente

```python
def raio_minimo(vd, e_max=0.08, f=0.15):
    """Calcula raio mínimo em metros"""
    return (vd ** 2) / (127 * (e_max + f))

# Tabela de raios para várias velocidades
for vd in [40, 60, 80, 100, 120]:
    r = raio_minimo(vd)
    print(f"Vd={vd} km/h → R_mín={r:.1f}m")
```

---

## 7. Referências Normativas Citadas

| Norma | Assunto |
|-------|---------|
| DNIT ES 101/97 | Projeto Geométrico — Elemento de Rodovia |
| DNIT IPR 726 | Visibilidade em Curvas Horizontais |
| DNIT IPR 702 | Avaliação Funcional Pavimentos |
| ABNT NBR 6123 | Forças Devidas ao Vento em Edificações/Estruturas |
| ABNT NBR 15895 | Sinalização Horizontal |
| SICRO DNIT | Tabela de Custos de Obras |

---

## 8. Checklist de Validação Geométrica

- [ ] Vd definida conforme classe da rodovia
- [ ] R ≥ R_mín para todas as curvas
- [ ] Superelevação e e_máx verificadas
- [ ] Clotóides dimensionadas (L_mín respeitado)
- [ ] Tangentes verificadas (L_mín/L_máx)
- [ ] Distância de visibilidade de parada OK
- [ ] Curvas verticais em parábola (não reta)
- [ ] Comprimento de transição de superelevação OK
- [ ] Seção transversal dimensionada
- [ ] Drenagem superficial (declividade ≥0.5%)
- [ ] Taludes (inclinações por tipo de solo)
- [ ] SICRO aplicado (quantitativos/custos)
- [ ] Memoriais e desenhos per DNIT

