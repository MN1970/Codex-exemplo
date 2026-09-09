# Geometria de Rodovias — Elementos Geométricos Fundamentais

**Versão**: 1.0  
**Data**: 2026-08-03  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:`

---

## 1. Classificação das Rodovias

### 1.1 Por Funcionalidade (DNIT)

| Classe | Descrição | Velocidade Diretriz | Volume/Ano |
|--------|-----------|-------------------|-----------|
| **BR** | Federal | 80-100 km/h | > 5M veículos |
| **BR-e** | Federal Estadual | 60-80 km/h | 1-5M veículos |
| **e** | Estadual | 60-80 km/h | 1-5M veículos |
| **Municipal** | Municipal | 40-60 km/h | < 1M veículos |

### 1.2 Por Projeto Geométrico (DNIT ES 131/86)

- **Rodovia de Pista Simples**: 1 faixa por sentido
- **Rodovia de Pista Dupla**: 2+ faixas por sentido (requer divisor central)
- **Rodovia em Gota**: transição entre simples e dupla

---

## 2. Alinhamento Horizontal

### 2.1 Elementos Componentes

```
[Tangente] → [Curva de Transição] → [Curva Circular] → [Curva de Transição] → [Tangente]
```

#### 2.1.1 Tangentes
- **Comprimento mínimo**: `Lmin = 0.28 × Vd` (Vd em km/h)
  - Exemplo: Vd = 80 km/h → Lmin = 22.4 m
- **Comprimento máximo**: `Lmax = 20 × Vd` (evita monotonia, reduz acidentes)

#### 2.1.2 Curvas Circulares
**Raio mínimo (sem superelevação)**:
```
R_mín = V² / (127 × f)
```
Onde:
- V = velocidade de projeto (km/h)
- f = coeficiente de atrito (0.15-0.20)

**Exemplos (Vd = 100 km/h, f = 0.15)**:
- Rmin = 100² / (127 × 0.15) = 426 m

**Raio mínimo com superelevação**:
```
R_mín = V² / (127 × (e_máx + f))
```
Onde:
- e_máx = superelevação máxima (0.08-0.10)

**Exemplos (Vd = 100 km/h, e_máx = 0.08, f = 0.15)**:
- Rmin = 100² / (127 × 0.23) = 343 m

#### 2.1.3 Curvas de Transição (Clotóide)

**Função**: Transição suave entre tangente (R=∞) e curva circular (R=cte)

**Parâmetro A (raio de transição)**:
```
A² = R × L_c

Onde:
- L_c = comprimento da clotóide (m)
- R = raio da curva circular (m)
```

**Comprimento mínimo da clotóide**:
```
L_mín = 0.036 × V³ / R

Exemplo: V=100 km/h, R=500m
L_mín = 0.036 × 100³ / 500 = 72 m
```

**Variação máxima de superelevação por metro**:
```
Δe/ΔL ≤ 1/150  (rodovia)
```

### 2.2 Superelevação (Inclinação Transversal em Curvas)

**Fórmula de projeto**:
```
e = (V² - 127 × R × f) / (127 × R)
```

**Valores Típicos** (DNIT):
| V (km/h) | f | e (%) |
|----------|---|-------|
| 40 | 0.20 | 2-4 |
| 60 | 0.18 | 3-6 |
| 80 | 0.16 | 4-7 |
| 100 | 0.15 | 5-8 |
| 120 | 0.14 | 6-9 |

**Comprimento de transição de superelevação**:
```
L_trans = (e_máx × a) / (Δe/ΔL)

Onde:
- a = largura do pavimento (m)
- Δe/ΔL = variação máxima (1/150)
```

---

## 3. Alinhamento Vertical

### 3.1 Elementos Componentes

```
[Tangente Vertical] → [Parábola Vertical] → [Tangente Vertical]
```

#### 3.1.1 Rampas
- **Rampa máxima**: 5-7% (depende de Vd e terreno)
- **Rampa mínima**: 0.5% (drenagem)

**Exemplo (Vd = 100 km/h, terreno montanhoso)**:
- i_máx = 6%
- Comprimento máximo rampa contínua: 1000m

#### 3.1.2 Curvas Verticais

**Tipos**:
- **Convexa** (topo): PIV acima dos PCs
- **Côncava** (vale): PIV abaixo dos PCs

**Comprimento mínimo da parábola**:
```
L = (|Δi| × V²) / (395 + 2.6 × V)

Onde:
- Δi = diferença de rampas (%)
- V = velocidade de projeto (km/h)
```

**Exemplos**:
- V = 100 km/h, Δi = 5%: L = (5 × 100²) / (395 + 260) = 137 m
- V = 80 km/h, Δi = 8%: L = (8 × 80²) / (395 + 208) = 100 m

**Distância de visibilidade mínima**:
- **Frenagem**: `d_f = V² / (254 × f)` → V=100 km/h, f=0.4 → d_f = 98 m
- **Ultrapassagem**: `d_u ≈ 6 × V` → V=100 km/h → d_u = 600 m

---

## 4. Seção Transversal

### 4.1 Componentes Básicos

```
    Acostamento         Pavimento          Acostamento
    |------|  Faixa  |---------|  Faixa  |--------|
           ↑ 2-3m  |           |           |         ↑ 2-3m
                   ← borda → ← borda →
                  
     [Drenagem]    [Tráfego]     [Drenagem]
```

### 4.2 Faixa de Rolamento

**Largura de faixa** (DNIT):
| Classe | Velocidade | Largura Faixa |
|--------|-----------|---------------|
| BR (Federal) | 100 km/h | 3.60 m |
| BR-e | 80 km/h | 3.50 m |
| Estadual | 60-80 km/h | 3.30-3.50 m |
| Municipal | 40-60 km/h | 3.00-3.30 m |

**Número de faixas**:
- Pista simples: 2 faixas (1 por sentido)
- Pista dupla: 2-3 faixas por sentido (com linha tracejada/contínua)

### 4.3 Acostamento

**Funções**:
- Parada de emergência
- Drenagem lateral
- Suporte estrutural (efeito de borda)

**Largura** (DNIT):
| Classe | Acostamento |
|--------|-----------|
| BR | 2.5-3.0 m |
| BR-e | 2.0-2.5 m |
| Estadual | 1.5-2.0 m |
| Municipal | 0.5-1.5 m |

**Tipo de revestimento**:
- Pavimento (CBUQ/PB): "acostamento pavimentado"
- Brita/Asfalto Diluído: "acostamento parcialmente pavimentado"
- Solo/Brita: "acostamento não pavimentado"

### 4.4 Inclinação Transversal

**Normal (tangente horizontal)**:
- Pista única: 2-3% (para centro)
- Pista dupla com divisor: 2% cada lado (para bordas externas)

**Em curva horizontal**:
- Superelevação: até 8-10% (conforme raio)

### 4.5 Banquetas de Corte e Aterro

**Inclinação de talude (corte)**:
```
1:m (altura 1m, afastamento m metros)

Exemplos:
- Solo: 1:1 a 1:1.5 (45-33°)
- Rocha: 1:0.5 a 1:1 (63-45°)
```

**Inclinação de aterro**:
```
Exemplos:
- Material comum: 1:1.5 a 1:2 (33-27°)
- Argila: 1:2 a 1:3 (27-18°)
```

---

## 5. Distâncias de Visibilidade

### 5.1 Visibilidade de Parada

```
d_parada = d_reação + d_frenagem

d_reação = V × t_r  (t_r ≈ 2.5s)
d_frenagem = V² / (254 × f)

Total: d_parada = V × 0.7 + V² / (254 × f)
```

**Exemplos**:
| V (km/h) | d_parada (m) |
|----------|--------------|
| 40 | 28 |
| 60 | 53 |
| 80 | 89 |
| 100 | 137 |
| 120 | 198 |

### 5.2 Visibilidade de Ultrapassagem

```
d_ultrapassagem ≈ 6 × V (aproximado)
                ≈ 9 × V (conservador)
```

**Mínimo DNIT**: distância para ultrapassar com segurança 1 veículo.

### 5.3 Visibilidade em Curva Horizontal

**Corda de visibilidade** (D):
```
D = 2 × R × sen(Θ/2)

Onde Θ = ângulo central para distância de parada d:
Θ = 2 × arcsen(d / 2R)
```

**Flecha de recuo** (necessária para corte):
```
f = R - √(R² - (d/2)²)

Exemplo: R=500m, d=137m
f = 500 - √(500² - 68.5²) = 500 - 499.5 ≈ 0.5m
```

---

## 6. Interseções

### 6.1 Rotatórias

**Raio externo mínimo**:
- R_ext ≥ 15-20m (dependendo de Vd)

**Raio da ilha central**:
- R_int = 6-8m (rodovia simples)
- R_int = 10-15m (rodovia dupla)

**Ângulo de entrada (deflexão)**:
- Mínimo 20° para segurança

### 6.2 Interseções em Nível (T, Cruz)

**Triângulo de Visibilidade**:
```
d_parada = largura do triângulo seguro
d_parada = profundidade do triângulo seguro
```

**Rampas de acesso**:
- Máximo 8-10% (curta)
- Tangente mínima: 30m

---

## 7. Ferramentas de Cálculo

### 7.1 Software Padrão DNIT/Manta

- **MX Road** (Bentley): alinhamento H/V, perfil de superelevação, seção transversal
- **AutoCAD Civil 3D**: desenho e cálculo automático
- **ESTAESTRADA** (DNIT): relatórios normativos
- **Google Earth Pro**: levantamento topográfico inicial

### 7.2 Parâmetros de Entrada Típicos

```
Intake do agente-infraestrutura S1:

1. Velocidade de projeto (Vd): 40-120 km/h
2. Classe de rodovia: BR, BR-e, estadual, municipal
3. Topografia: plana, ondulada, montanhosa
4. Tipo de veículo crítico: veículo leve, ônibus, caminhão
5. Volume de tráfego: VDMA ou classificação
6. Coeficiente de atrito: f = 0.15-0.20 (tangente)
7. Superelevação máxima: e_máx = 0.08-0.10
```

---

## 8. Normas de Referência

| Norma | Título | Escopo |
|-------|--------|--------|
| **DNIT ES 101/97** | Projeto Geométrico | Rodovias |
| **DNIT ES 131/86** | Projeto de Drenagem | Águas pluviais |
| **DNIT IPR 702** | Avaliação Funcional de Pavimentos | Defeitos |
| **DNIT IPR 726** | Visibilidade em Curvas | Cálculos |
| **NBR 6123** | Forças Devidas ao Vento | Viadutos/OAE |
| **ABNT NBR 15895** | Sinalização Horizontal | Faixas/Marcas |
| **ABNT NBR 14644** | Balizamento | Defensas/Tachas |

---

## 9. Anexos — Fórmulas Rápidas

### 9.1 Cálculo de Raio Mínimo
```
R_mín = V² / (127 × (e + f))

Atalho para f=0.15:
V (km/h) | e=0.04 | e=0.06 | e=0.08 |
40       | 55    | 48    | 42    |
60       | 124   | 108   | 96    |
80       | 221   | 191   | 170   |
100      | 344   | 296   | 265   |
120      | 496   | 425   | 376   |
```

### 9.2 Comprimento de Curva Vertical
```
L = |Δi| × K

K (tabela DNIT):
V (km/h) | Convexa | Côncava |
40       | 8      | 6      |
60       | 18     | 13     |
80       | 32     | 23     |
100      | 50     | 36     |
120      | 72     | 52     |
```

### 9.3 Superelevação
```
e(%) = 100 × (V² / (127 × R) - 0.15)

Exemplo: V=100, R=400m
e = 100 × (10000 / (127 × 400) - 0.15)
e = 100 × (0.1965 - 0.15) = 4.65%
```

---

## 10. Checklist de Projeto Geométrico

- [ ] Velocidade de projeto definida
- [ ] Raios mínimos verificados (todas as curvas)
- [ ] Superelevação calculada e verificada
- [ ] Comprimentos de tangente (mín/máx) OK
- [ ] Distância de visibilidade adequada
- [ ] Seção transversal dimensionada
- [ ] Perfil vertical com curvas em parábola
- [ ] Banquetas e taludes (inclinações)
- [ ] Acostamento dimensionado
- [ ] Drenagem superficial (declividade mínima)
- [ ] Interseções com triângulos de visibilidade
- [ ] Memoriais descritivos e desenhos conforme DNIT
