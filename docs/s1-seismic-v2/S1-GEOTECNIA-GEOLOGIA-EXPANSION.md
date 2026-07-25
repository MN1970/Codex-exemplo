# DOMÍNIO GEOTECNIA & GEOLOGIA — S1-V6 SÍSMICA
**Módulo D6.2 extendido: Análise Geotécnica & Geológica Sísmica**

---

## 1. ESCOPO DE GEOTECNIA/GEOLOGIA EM S1-V6

### 1.1 O que já está em S1 (V4 — Document Intelligence)

✅ Leitura de sondagens (SPT, CPT)  
✅ Classificação SUCS básica  
✅ Análise de perfil geotécnico estático  
✅ Estabilidade estática de taludes (Bishop, Spencer)  
✅ Cálculo de recalque (assentamento)  
✅ Drenagem convencional  

### 1.2 O que NOVO em S1-V6 (Geotecnia Sísmica)

❌ **Propriedades dinâmicas** do solo (módulo cisalhante G, amortecimento ξ)  
❌ **Índice de liquefação** baseado em SPT + características geológicas  
❌ **Amplificação de sítio** (Vs30, efeito topográfico)  
❌ **Deformação permanente** pós-sísmica (Newmark + método Younes)  
❌ **Caracterização geológica sísmica** (idade, origem, estrutura de camadas)  
❌ **Comportamento cíclico** de solos sob carregamento sísmico  
❌ **Estabilidade geotécnica pós-evento** (redistribuição de poropressão, slope failure)  
❌ **Remediação geotécnica** (drenagem dinâmica, densificação, substituição)  

---

## 2. MÓDULO D6.2 ESTENDIDO — GEOTECNIA SÍSMICA

```
D6.2: Análise de Liquefação & Comportamento Geotécnico Sísmico
│
├─ D6.2.1: Caracterização Geológica para Sísmica
│   ├─ 6.2.1.1-age-deposits.md      (Quaternário, Terciário, Pré-Cambr.)
│   ├─ 6.2.1.2-origin-soils.md      (Aluvial, coluvial, residual, laterita)
│   ├─ 6.2.1.3-stratification.md    (Perfil sísmico: camadas, interfaces)
│   └─ 6.2.1.4-geologic-hazards.md  (Soft clays, sand lenses, aquitards)
│
├─ D6.2.2: Propriedades Dinâmicas do Solo
│   ├─ 6.2.2.1-gmax-shear.md        (Módulo cisalhante máximo, G_max)
│   ├─ 6.2.2.2-damping-ratio.md     (Amortecimento ξ, curva redução)
│   ├─ 6.2.2.3-spt-to-vs.md         (Correlação SPT ↔ Vs30 velocidade onda-S)
│   ├─ 6.2.2.4-liquefaction-susceptibility.md  (τ_cyc/σ'_v threshold)
│   └─ 6.2.2.5-cyclic-strength.md   (CRR — Cyclic Resistance Ratio)
│
├─ D6.2.3: Índice de Liquefação (v2 — estendido)
│   ├─ 6.2.3.1-tokimatsu-yoshida.md (Original 1983 + updates 2016)
│   ├─ 6.2.3.2-youd-perkins.md      (Curvas risco, PL index)
│   ├─ 6.2.3.3-spt-correction.md    (N60, N_cs, profundidade, stress)
│   ├─ 6.2.3.4-cyclic-stress-ratio.md (CSR = 0.65 × (a_max/g) × σ_v/σ'_v)
│   ├─ 6.2.3.5-regional-factors.md   (Saturação, NPT, densidade relativa)
│   └─ 6.2.3.6-risk-assessment.md   (PL < 0.1 = low, 0.1–0.3 = moderate, etc.)
│
├─ D6.2.4: Amplificação de Sítio & Efeitos Locais
│   ├─ 6.2.4.1-vs30-classification.md (Vs ≥1500m/s = rocha; <180m/s = solo mole)
│   ├─ 6.2.4.2-site-amplification.md  (Fa, Fv factors USGS/EC8)
│   ├─ 6.2.4.3-topographic-effects.md (Slopes, ridges: +20–30% Sa)
│   ├─ 6.2.4.4-ground-response.md     (1D equivalent-linear, DEEPSOIL)
│   └─ 6.2.4.5-microzoning.md         (Mapas suscetibilidade locais)
│
├─ D6.2.5: Deformação Permanente Geotécnica
│   ├─ 6.2.5.1-newmark-sliding.md    (Bloco deslizante, aceleração crítica)
│   ├─ 6.2.5.2-younes-method.md      (Permanent strain εp, integração tempo)
│   ├─ 6.2.5.3-talude-failure-modes.md (Planar, cunha, circular)
│   ├─ 6.2.5.4-aterro-settlement.md  (Recalque sísmico, redistribuição)
│   └─ 6.2.5.5-monitoring-post-seismic.md (Inclinômetro, pore pressure)
│
├─ D6.2.6: Remediação Geotécnica
│   ├─ 6.2.6.1-compaction-densification.md (Vibrofloatation, dynamic compaction)
│   ├─ 6.2.6.2-soil-replacement.md   (Escavação + aterro controlado)
│   ├─ 6.2.6.3-drainage-systems.md   (Dreno francês sísmico, PVD)
│   ├─ 6.2.6.4-geosynthetics.md      (Geotêxtil, geogrelha, geomembrana)
│   ├─ 6.2.6.5-pore-pressure-dissipation.md (Poro-pressão pós-evento)
│   └─ 6.2.6.6-cost-benefit.md       (Análise remediação vs redesign)
│
└─ D6.2.7: Casos de Estudo Geotécnicos
    ├─ 6.2.7.1-jerico-geotecnia.md  (Perfil, SPT, LI, recomendações)
    ├─ 6.2.7.2-ceara-sandy-soils.md (Solos arenosos, liquefação potencial)
    ├─ 6.2.7.3-es-soft-clays.md     (Argilas moles, amortecimento alto)
    ├─ 6.2.7.4-sp-residual-soils.md (Solos residuais, aterros históricos)
    └─ 6.2.7.5-latam-cases.md       (Peru, Colômbia, Argentina)
```

---

## 3. HANDOFF COM AGENTES GEOTÉCNICOS

### 3.1 Arquitetura de integração (S1 ↔ Geotecnia)

Atualmente, **S1 não tem acesso a agente geotécnico especializado**. Solução:

```
S1-V6 (Rodovias Sísmicas)
├─ Q3 = Moderado+ risco sísmico?
│  └─ Ativa D6.2 (Geotecnia Sísmica — módulo interno)
│     ├─ Lê sondagens (SPT, CPT) do artefato
│     ├─ Classifica solos (SUCS)
│     ├─ Calcula LI (índice liquefação)
│     ├─ Se LI > 0.3 → ⚠️ Flag "recomenda-se handoff geotécnico"
│     └─ Gera recomendação básica (dreno, densificação, substituição)
│
└─ Se complexo (múltiplas camadas, poro-pressão incerta) 
   └─ Handoff-sugerido (não mandatório) a agente geotécnico externo
      (quando existir)
```

### 3.2 Escopo de D6.2 (interno S1) vs. Agente Geotécnico (futuro externo)

| Aspecto | S1-V6 (D6.2 interno) | Agente Geotécnico (futuro) |
|---------|--------------------|----|
| **Leitura de SPT** | ✅ Sim, básico | ✅ Sim, avançado |
| **Índice de Liquefação** | ✅ Sim (Tokimatsu) | ✅ Sim (multi-métodos) |
| **Amplificação de sítio** | ✅ Sim (tabela USGS) | ✅ Sim (ground response 1D/2D) |
| **Newmark (talude)** | ✅ Sim, método analítico | ✅ Sim, + FEM dinâmico |
| **Remediação básica** | ✅ Sim (recomendações) | ✅ Sim (design executivo) |
| **Análise poro-pressão** | ⚠️ Tabela LI | ✅ Sim, numérico (u2) |
| **Prospecção adicional** | ⚠️ Recomenda CPT/DMT | ✅ Sim, design investigação |
| **Modelagem FEM dinâmica** | ❌ Não | ✅ Sim (ABAQUS, FLAC) |

---

## 4. PARÂMETROS GEOTÉCNICOS CRÍTICOS PARA SÍSMICA

### 4.1 Propriedades Dinâmicas (tabela de solos típicos)

```
Classificação SUCS | Vs30 (m/s) | G_max (MPa) | ξ (%) | LI (típico) | Aplicação
────────────────────┼────────────┼─────────────┼───────┼─────────────┼──────────
GW / GP (seco)      | 600–900    | 80–150      | 2–5   | 0.0–0.1     | Cascalho
SW / SP (seco)      | 400–700    | 40–100      | 3–7   | 0.2–0.5     | Areia
SM (arenosiltoso)   | 300–500    | 25–60       | 4–8   | 0.3–0.6     | Areia + silte
SC (areia argilosa) | 250–450    | 20–50       | 5–10  | 0.4–0.7     | Areia + argila
ML (silte)          | 200–400    | 15–40       | 6–12  | 0.5–0.8     | Silte
CL (argila)         | 150–300    | 10–30       | 8–15  | 0.1–0.4     | Argila rígida
CH (argila mole)    | 100–200    | 5–20        | 10–20 | 0.0–0.2     | Argila blanda
MH (silte de alta) | 120–250    | 8–25        | 12–18 | 0.3–0.6     | Silte elástico
OH (argila org.)    | 80–150     | 3–15        | 15–25 | 0.0–0.1     | Argila orgânica
```

**Fonte**: USGS, NEHRP, Kramer (1996)

### 4.2 Fórmulas de Correlação SPT ↔ Vs30

Para estimativa rápida quando não há dados Vs:

```
Vs30 (m/s) = 60 × N_60^0.5 + 60  [Okada et al., 2003 — Japão]
Vs30 (m/s) = 62 × N_60^0.34 × D_m^0.16  [Imai & Tonouchi, 1982]
Vs30 (m/s) = 107 × N_SPT^0.25 + 60  [Boore, 2004 — USA]

Onde:
  N_60 = SPT N corrigido para 60% energia
  D_m = profundidade média (m)
  N_SPT = SPT bruto

Aplicação S1-V6: Ativar quando houver SPT sem Vs; retornar faixa (conservadora)
```

---

## 5. ÍNDICE DE LIQUEFAÇÃO (v2 — ESTENDIDO)

### 5.1 Fórmula Tokimatsu & Yoshida (1983) — Atualizada

```
LI = Σ [FL × (N1)60_cs]^-1.02 / 34 × PL

Onde:
  LI = Liquefaction Index (0–1; >0.1 = risco moderado+)
  FL = Factor de magnitude sísmica (Mw), tipicamente 0.85–1.0
  (N1)60_cs = SPT normalizado, corrigido para stress de confinamento
             (N1)60_cs = N_measured × (C_N) × (C_B) × (C_R) × (C_s)
             C_N = (Pa / σ'_v)^0.5  [normalização profundidade]
             C_B = (D_B / 1)^0.5 se D_B < 1m [efeito profundidade aterro]
             C_R = [ER / 60]  [energia]
             C_s = (τ_cyc / σ'_v)^-1.3  [stress normalization]
  
  PL = Liquefaction Potential Index
       PL = 100 × FL × [(N1)60_cs / 37.3]^-3.6  [se N < threshold]
       threshold ≈ 20 golpes → não liquefaz

Resultado:
  LI < 0.1     → Baixo risco (não recomenda remediação)
  0.1 < LI < 0.3 → Risco moderado (dreno francês, drenagem)
  0.3 < LI < 0.7 → Alto risco (densificação, substituição)
  LI > 0.7     → Muito alto (redesenho completo)
```

### 5.2 Matriz Regional de LI (Brazil)

Estimativa inicial por zona sísmica + tipo geológico:

```
Região         | Depósito Geológico  | PGA (g) | Tipo Solo Típico | LI Esperado
───────────────┼────────────────────┼─────────┼──────────────────┼────────────
Jericó (MG)    | Aluvial + coluvial  | 0.18    | SP, SM           | 0.25–0.45
Quixeramobim   | Aluvial quaternário | 0.15    | SW, SM           | 0.20–0.35
Linhares (ES)  | Aluvial costeiro    | 0.12    | CH (mole)        | 0.10–0.25
São Paulo      | Residual (cristal)  | 0.06    | CL (rígido)      | 0.05–0.15
Rio de Janeiro | Gnáiss, granito     | 0.08    | SC, ML           | 0.08–0.20
Ceará (interior)| Aluvial fluvial     | 0.12    | SP, SP-SM        | 0.22–0.40

Nota: Liquefi apenas em solos arenosos saturados (SP, SW, SM).
      Argilas (CL, CH) raramente liquefazem.
```

---

## 6. AMPLIFICAÇÃO DE SÍTIO (FATOR Fa & Fv)

### 6.1 Classificação NEHRP / ASCE 7 (simplificada)

```
Classe de Sítio | Vs30 Range (m/s) | Descrição | Fa (T=0.3s) | Fv (T=1.0s)
────────────────┼──────────────────┼───────────┼─────────────┼──────────
A               | >1500            | Rocha dura | 0.8         | 0.8
B               | 750–1500         | Rocha dura-moderada | 1.0 | 1.0
C               | 370–750          | Solo denso/ roc. mole | 1.2 | 1.7
D               | 180–370          | Solo mole | 1.6         | 2.4
E               | <180              | Solo muito mole | 2.0–2.5 | 3.5+
F               | Especial (liq.)   | Levanta investigação | — | —
```

**Aplicação S1-V6**: Estimar Vs30 via SPT → Classificar sítio → Obter Fa/Fv → Amplificar Sa

---

## 7. NEWMARK DEFORMAÇÃO — MÉTODO GEOTÉCNICO

### 7.1 Sliding Block Analysis (método simplificado)

```
Procedimento:
1) Calcular aceleração crítica (a_c) do talude
   a_c = (FS_static - 1) × g × tan(φ)
   
   FS_static = tan(φ) / tan(β)  [inclinado simples]
   
   Exemplo: φ = 35°, β = 30°
   FS_static = tan(35°) / tan(30°) = 0.700 / 0.577 = 1.21
   a_c = (1.21 - 1) × 9.8 × tan(35°) = 0.21 × 9.8 × 0.700 = 1.44 m/s²
   
2) Comparar com PGA (0.15–0.25 g para Jericó)
   Se PGA > a_c → bloco desliza → calcular Δ (deformação)
   
3) Integrar acelerograma sintético:
   Δ_perm = ∫∫ (a_input - a_c) dt² [apenas a > a_c]
   
4) Resultado: Deslocamento permanente em metros (tipicamente 0.05–0.5 m)
   Se Δ > 0.3 m → talude crítico → recomenda redesign
```

### 7.2 Exemplos Numéricos (Jericó)

```
Cenário 1: Talude natural (φ=35°, β=30°, FS=1.21)
──────────────────────────────────────────────
PGA = 0.18 g (Jericó)
a_c = 0.14 g (calc. acima, retificado)
Δ_perm = 0.28 m  ← Risco moderado (>0.15 m)
Recomendação: Dreno + reforço geotêxtil; monitorar pós-evento

Cenário 2: Aterro reforçado (φ=37°, FS=1.50 após reforço)
──────────────────────────────────────────────────────
a_c = (1.50 - 1) × 9.8 × tan(37°) = 0.50 × 9.8 × 0.754 = 3.69 m/s²
Δ_perm = 0.05 m  ← Risco baixo (<0.1 m)
Conclusão: Reforço foi efetivo

Cenário 3: Muro em gabiões (estrutura rígida, aceleração lateral)
────────────────────────────────────────────────────────────
Inércia lateral = M × (0.18 g) = 18% do peso
Momento tombamento = M × (0.18 g) × h_wall
Se h_wall = 5 m → momento é 0.9 × M (significativo)
Recomendação: Junta de dilatação sísmica a cada 5–10 m
```

---

## 8. REMEDIAÇÃO GEOTÉCNICA — OPÇÕES

### 8.1 Matriz de Remediação (por LI & FS)

```
LI       | FS static | Remediação Recomendada | Custo Relativo | Prazo
─────────┼───────────┼────────────────────────┼────────────────┼──────
0.1–0.3  | >1.3      | Drenagem (dreno frân.)| 1.5x           | 2–4 sem
0.3–0.5  | 1.2–1.3   | Dreno + densificação  | 3.0x           | 4–8 sem
0.5–0.7  | 1.0–1.2   | Substituição 50%      | 5.0x           | 8–12 sem
>0.7     | <1.0      | Redesign completo     | 8.0x+          | 12+ sem
```

### 8.2 Técnicas Geotécnicas

| Técnica | Aplicabilidade | Eficiência | Custo | Prazo | Notas |
|---------|---|---|---|---|---|
| **Dreno francês** | SP, SM, SW | LI ↓ 20–30% | 1.0x | 2–4 sem | Drenagem superficial |
| **Vibrofloatação** | SP, SW (seco) | LI ↓ 30–50% | 2.0x | 3–6 sem | Densificação dinâmica |
| **Dynamic Compaction** | SP, SM | LI ↓ 40–60% | 2.5x | 2–4 sem | Pesado; superficial (5m) |
| **PVD (Prefab Drains)** | CL, CH (mole) | u ↓ 50–70% | 3.0x | 6–12 sem | Poro-pressão inicial |
| **Soil Replacement** | Qualquer | LI → 0.0 | 5.0x | 8–16 sem | Escavação + aterro |
| **Geotêxtil Reforço** | Aterros, taludes | FS ↑ 15–25% | 1.5x | 2–4 sem | Resistência lateral |
| **Eletrosmose** | CH (muito mole) | Drenagem profunda | 4.0x | 12–24 sem | Lenta; especializada |
| **Grouting** | Fraturas, vazios | Estabiliza | 3.5x | 4–8 sem | Pré ou pós-evento |

---

## 9. INTELIGÊNCIA GEOLÓGICA (NOVA DIMENSÃO)

### 9.1 Mapeamento Geológico para Rodovias Sísmicas

S1-V6 deve integrar **mapeamento geológico** na análise:

```
Idade Geológica × Tipo Depósito × Contexto Sísmico
───────────────┼─────────────────┼───────────────────
Quaternário    | Aluvial         | ALTO RISCO (saturado, solto)
               | Coluvial        | MÉDIO RISCO (parcial saturação)
               | Eólico          | BAIXO RISCO (seco)
Terciário      | Sedimentar      | MÉDIO-ALTO (histórico soterrado)
               | Vulcânico       | BAIXO (rocha alterada, firme)
Pré-Cambro     | Metamórfico     | MUITO BAIXO (rocha sã)
               | Granítico       | MUITO BAIXO (residual ou sã)
```

### 9.2 Estrutura Geológica

**Aspectos críticos para sísmica**:

1. **Camadas**: Espessura, continuidade lateral, contraste de impedância
2. **Contatos**: Falhamentos ativos? Zonas de alteração?
3. **Drenagem natural**: Aquíferos, lentes argilosas impermeáveis
4. **História sísmica**: Já houve licuperação no passado? (evidência em depósitos)

**Output S1-V6**: Mapa geológico → LI regional → Zoneamento risco

---

## 10. SONDAGENS & INVESTIGAÇÃO GEOTÉCNICA

### 10.1 Programa de Prospecção Recomendado (por LI inicial)

```
LI estimado | SPT existente? | Investigação Recomendada | Custo
────────────┼────────────────┼──────────────────────────┼────────
< 0.1       | Sim            | Nenhuma adicional        | 0
0.1–0.3     | Sim            | CPT em 1–2 pontos        | 1.0x
            | Não            | SPT novo + CPT           | 2.5x
0.3–0.7     | Sim            | CPT + DMT, trincheiras   | 3.0x
            | Não            | SPT denso + CPT + DMT    | 4.0x
> 0.7       | Qualquer       | Investigação completa    | 5.0x+
            |                | (sondagem profunda, pz)  |
```

### 10.2 Ensaios Complementares (quando necessário)

| Ensaio | Objetivo | Aplicação S1-V6 |
|--------|----------|---|
| **CPT (Cone Penetration)** | Perfil contínuo, correlação Vs | Estimar Vs30; validar LI |
| **DMT (Dilatometer)** | Módulo, K0, OCR | Refinar G_max; estimar overconsolidation |
| **VS-Down / VS-Up** | Perfil Vs direto | Melhor Vs30 (ideal) |
| **Triaxial Cíclico** | Comportamento dinâmico | Validar CRR, G/G_max |
| **Ressonant Column** | G_max, ξ de baixa amplitude | Propriedades dinâmicas diretas |

---

## 11. CASOS DE ESTUDO GEOTÉCNICOS

### 11.1 Jericó 2024 — Análise Geotécnica Retrospectiva

```
Localização: Estrada MG-120 próx. Jericó, Minas Gerais
Evento: Sismo Mw 5.0 (2024-01-01)
PGA Estimada: 0.18–0.20 g

Geologia:
- Depósito aluvial quaternário (4–8 m)
- Perfil: Argila siltosa (CL, 2 m) + Areia siltosa (SM, 4 m) + Cascalho
- Nível freático: 1.5 m de profundidade
- Substrato: Gnaisse alterado (rocha mãe)

Sondagem SPT (pré-sismo):
Profundidade (m) | N (golpes) | Solo       | Classificação
─────────────────┼───────────┼────────────┼──────────────
0–2              | 4–6       | Argila     | CL
2–4              | 8–12      | Areia/silt | SM (crítico!)
4–6              | 15–18     | Cascalho   | GW
6+               | > 30      | Gnaisse    | Rocha

Cálculo LI:
(N1)60_cs (2–4 m) ≈ 10 (normalizado)
LI = 0.32 → RISCO MODERADO-ALTO

Previsão vs. Realidade:
- Predito: Liquefação potencial, assentamento 5–10 cm
- Observado: Pequenas fissuras, sem ruptura (talves LI foi superestimado)
  OU: Duração sísmica curta, PGA não atingiu pico contínuo

Lição: Incerteza em Jericó → necessário dado sísmico pós-evento (acelerograma)
```

### 11.2 Ceará — Solos Arenosos (Risco Alto)

```
Localização: Quixeramobim-Sobral, Ceará
PGA Histórica: 0.12–0.15 g (zona de risco moderado)
Geologia: Depósito fluvial quaternário, **areia fina e média predominante**

Perfil SPT:
0–2 m: N = 3–5 (areia fina muito fofa)
2–4 m: N = 6–10 (areia fina)
4–6 m: N = 12–15 (areia fina densa)
NPT: 1.2 m

LI (2–4 m) = 0.45 → RISCO ALTO
Recomendação: Dreno francês + densificação via dynamic compaction
```

### 11.3 Espírito Santo — Argilas Moles (Risco Baixo)

```
Localização: Linhares (zona costeira), ES
PGA: 0.10–0.12 g
Geologia: Aluvial costeiro, **argila mole e orgânica**

Perfil SPT:
0–2 m: N = 2–3 (argila muito mole, matéria orgânica)
2–4 m: N = 4–7 (argila mole)
4–6 m: N = 8–12 (argila rígida)
NPT: 0.8 m (muito saturado)

Análise Sísmica:
- Argila = baixa susceptibilidade liquefação (LI ~ 0.05)
- Risco maior: **Amplificação** (Vs30 ~120 m/s → Classe E → Fa ~2.0)
- Assentamento pós-sísmo por reconsolidação: 2–5 cm

Recomendação: Não remediação liquefação, mas design de pavimento flexível
             para acomodar deslocamentos pós-evento
```

---

## 12. RAG COLLECTION ROD:SEISM:GEO:* 

```
Prefixo: rod:seism:geo:

├─ rod:seism:geo:norm:      (Normas geotécnicas sísmicas)
│  ├─ NBR 8681, 15421
│  ├─ ASCE 7 (seção geotecnia)
│  ├─ ISO 14383 (geotech)
│  └─ EC8 (Part 5 — foundations)
│
├─ rod:seism:geo:props:     (Propriedades dinâmicas de solos)
│  ├─ Vs30 correlations
│  ├─ G_max, damping curves
│  ├─ CRR (cyclic resistance)
│  └─ SPT corrections
│
├─ rod:seism:geo:liq:       (Liquefaction)
│  ├─ Tokimatsu & Yoshida (1983, updated 2016)
│  ├─ Youd et al. (2001)
│  ├─ Regional LI tables (Brazil)
│  └─ Case histories
│
├─ rod:seism:geo:amp:       (Site amplification)
│  ├─ NEHRP classification
│  ├─ Fa, Fv factors
│  ├─ Ground response (1D, equiv-linear)
│  └─ Topographic effects
│
├─ rod:seism:geo:deform:    (Permanent deformation)
│  ├─ Newmark sliding block
│  ├─ Younes method (εp)
│  ├─ Slope failure modes
│  └─ Settlement (Δy)
│
├─ rod:seism:geo:remediat: (Remediation)
│  ├─ Vibrofloatation
│  ├─ Dynamic compaction
│  ├─ Drainage systems
│  ├─ Geosynthetics
│  └─ Cost-benefit matrix
│
└─ rod:seism:geo:cases:    (Casos geotécnicos)
   ├─ Jericó detailed geotech
   ├─ Ceará (sandy soils)
   ├─ ES (soft clays)
   └─ LATAM benchmarks
```

---

## 13. MATRIZ DE DECISÃO GEOTÉCNICA

Quando usuário insere SPT/classificação solo, S1-V6 segue árvore:

```
Usuário → S1: "Análise sísmica para talude em Jericó"
             ↓
Q3 = Alto risco? → SIM → ATIVA D6.2 (Geotecnia)
             ↓
Tem dados SPT? ─┬─ SIM → Calcula LI (Tokimatsu)
               │         ├─ LI < 0.1 → "Baixo risco, nenhuma remediação"
               │         ├─ 0.1 < LI < 0.3 → "Dreno francês recomendado"
               │         ├─ 0.3 < LI < 0.7 → "Densificação + dreno"
               │         └─ LI > 0.7 → "⚠️ Redesign; handoff geotécnico"
               │
               └─ NÃO → Recomenda prospecção SPT + estima LI regional
                         ├─ Depósito aluvial? → LI típico 0.20–0.50
                         ├─ Solo residual? → LI típico 0.05–0.15
                         └─ Argila mole? → LI típico 0.00–0.10

Se LI > 0.3 & múltiplas camadas:
  → Flag "Análise 1D ground response recomendada"
  → Sugerir handoff a geotécnico (futuro) ou CPT para refinamento
```

---

## 14. DELIVERABLES GEOTÉCNIA (V6)

### Em S1-V6 (Interno)

- [ ] D6.2.1–D6.2.7 (8 módulos geotecnia sísmica)
- [ ] Calculadora LI (SPT input → índice output)
- [ ] Tabela remediação (LI × FS → técnica + custo)
- [ ] Casos Jericó, Ceará, ES detalhados
- [ ] Abas artefato: "Geotecnia Sísmica" + "Amplificação Sítio"

### Futuros (Agente Geotécnico externo — roadmap v3.0)

- Modelagem FEM dinâmica (FLAC, ABAQUS)
- Investigação geotécnica avançada (design)
- Análise 2D/3D ground response
- Validação poro-pressão (elementos finitos)

---

## RESUMO: GEOTECNIA EM S1-V6

✅ **D6.2 estendido** cobre:
- Índice liquefação (Tokimatsu v2)
- Amplificação sítio (Fa/Fv NEHRP)
- Deformação Newmark (taludes)
- Remediação (dreno, densif., substituição)
- Casos Jericó + Ceará + ES

✅ **Handoff futuro** a agente geotécnico (quando existir) para:
- Modelagem numérica dinâmica
- Design executivo de remediação
- Investigação avançada

✅ **RAG** rod:seism:geo:* com 8 sub-coleções

✅ **Artefato** com 2 novas abas geotécnicas

**Meta Q2 2027**: S1-V6 será referência em análise geotécnica sísmica de rodovias brasileiras 🏆

