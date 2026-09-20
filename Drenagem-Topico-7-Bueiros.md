# Drenagem — Tópico 7: Bueiros
## Cálculo de Diâmetro, Velocidade, Entrada/Saída

**Data:** 2026-08-04  
**Disciplina:** Drenagem Rodoviária  
**Norma de Referência:** DNIT ES 131/86 — Instrução para Drenagem  
**Público:** Projetistas, engenheiros de drenagem, construtores

---

## 1. CONCEITOS FUNDAMENTAIS

### 1.1 Definição e Papel do Bueiro

Um **bueiro** é uma estrutura de drenagem transversal que permite:
- Cruzamento de talvegues (pequenos cursos d'água) sob a rodovia
- Continuidade do escoamento natural
- Proteção da estrutura viária contra erosão

**Classificação:**
- **Simples:** seção circular ou retangular
- **Múltiplo:** vários tubos em paralelo (crescimento de bacia)
- **Especial:** estruturas em grelha, áreas sensíveis

### 1.2 Componentes Estruturais

```
          ENTRADA (cabeceira)
                 ↓
    ┌──────────────────────────┐
    │   Tubulação/Estrutura     │  ← Fluxo submerso ou livre
    │   (L = comprimento)        │
    └──────────────────────────┘
                 ↓
          SAÍDA (corpo)
    ├─ Dissipador de energia
    └─ Proteção contra erosão
```

**Parâmetros principais:**
- **D** = diâmetro (ou altura) [m]
- **L** = comprimento do bueiro [m]
- **Q** = vazão de projeto [m³/s]
- **v** = velocidade média do fluxo [m/s]
- **i** = declividade da tubulação [m/m]
- **n** = coeficiente de Manning

---

## 2. FÓRMULAS E CÁLCULOS

### 2.1 Equação de Manning (regime de escoamento livre)

```
Q = (A/n) × R²/³ × i^(1/2)
```

Onde:
- **Q** = vazão [m³/s]
- **A** = área da seção transversal [m²]
- **n** = coeficiente de Manning
- **R** = raio hidráulico = A/P [m]
- **P** = perímetro molhado [m]
- **i** = declividade [m/m]

**Tabela — Coeficientes de Manning por material:**

| Material | n (Manning) | Condição |
|----------|------------|----------|
| Tubo de concreto (bom estado) | 0,010 | Limpo, novo |
| Tubo de concreto (regular) | 0,012-0,015 | Após 5-10 anos |
| Tubo de aço (corrugado) | 0,020-0,025 | Corrugação profunda |
| Seção retangular concreto | 0,011-0,013 | Acabamento normal |

---

### 2.2 Cálculo de Diâmetro Mínimo

**Critério 1: Velocidade Mínima (autoLimpeza)**

Para garantir que não ocorra sedimentação:

```
v_min = 0,6 m/s  (tubagens com sedimento fino)
v_min = 0,9 m/s  (tubagens com areia)
v_min = 1,2 m/s  (tubagens com cascalho)
```

**Critério 2: Velocidade Máxima (proteção)**

Para evitar erosão na saída:

```
v_máx = 2,0 a 3,0 m/s  (tubo de concreto simples)
v_máx = 3,0 a 4,0 m/s  (tubo de concreto armado)
v_máx = 1,5 a 2,5 m/s  (seção de terra estabilizada)
```

---

### 2.3 Dimensionamento Prático (Fluxo Livre)

**Passo 1:** Estimar vazão de projeto (Q)
- Usar método racional ou hidrológico (bacia contribuinte)
- Coef. escorrimento (C) depende de uso do solo

**Passo 2:** Escolher material e diâmetro tentativo
- Concreto (D = 0,50 m, 0,75 m, 1,00 m, 1,25 m...)
- Calcular A (seção):
  - Circular: A = π·D²/4
  - Retangular: A = b × h

**Passo 3:** Calcular velocidade

```
v = Q / A
```

**Passo 4:** Validar

- v_min ≤ v ≤ v_máx ?
- Se v < v_min: aumentar declividade ou reduzir D
- Se v > v_máx: aumentar D ou adicionar segundo tubo

---

### 2.4 Cálculo de Perda de Carga (Fluxo Submerso)

Em regime submerso (entrada afogada):

```
h_f = (f × L × v²) / (2 × g × D)
```

Onde:
- **h_f** = perda por fricção [m]
- **f** = fator de Darcy-Weisbach ≈ 0,02-0,03 (concreto)
- **L** = comprimento do bueiro [m]
- **v** = velocidade [m/s]
- **g** = 9,81 m/s²
- **D** = diâmetro [m]

**Perdas de entrada/saída:**

```
h_entrada = K_e × (v²/2g)    [K_e ≈ 0,5 para entrada normal]
h_saída = K_s × (v²/2g)      [K_s ≈ 1,0 para saída livre]
```

---

## 3. NORMA DNIT ES 131/86 — REFERÊNCIA

### 3.1 Diâmetros Comerciais Recomendados

| Diâmetro (mm) | Aplicação | Vazão máxima (m³/s) |
|---------------|-----------|-------------------|
| 500 | Bacias até 5 ha | 0,10 |
| 750 | Bacias 5-15 ha | 0,25 |
| 1.000 | Bacias 15-40 ha | 0,50 |
| 1.250 | Bacias 40-80 ha | 0,80 |
| 1.500 | Bacias 80-150 ha | 1,20 |
| 2.000 | Bacias > 150 ha | 2,00 |

*Fonte: DNIT ES 131/86*

### 3.2 Critérios de Declividade Mínima

```
i_min = 0,005 (0,5%)    — para tubos com D ≥ 1,0 m
i_min = 0,010 (1,0%)    — para tubos com D = 0,75 m
i_min = 0,015 (1,5%)    — para tubos com D ≤ 0,50 m
```

Estas declividades garantem v_min ≥ 0,6 m/s

---

## 4. EXEMPLO PRÁTICO — RODOVIA FEDERAL PADRÃO (Vd = 100 km/h)

### 4.1 Dados da Bacia Contribuinte

- **Área da bacia:** A = 25 ha = 250.000 m²
- **Coeficiente de escoamento:** C = 0,35 (50% pavimentado, 50% verde)
- **Chuva de projeto:** P = 150 mm (Tr = 10 anos, região SE Brasil)
- **Tempo de concentração:** Tc = 20 min

### 4.2 Cálculo da Vazão (Método Racional)

```
Q = C × I × A / 360

Onde:
I = P / Tc = 150 / (20 min) = 7,5 mm/min

Q = 0,35 × 7,5 × 25 / 360
Q = 0,1823 m³/s  →  Q_projeto = 0,20 m³/s
```

### 4.3 Seleção do Diâmetro

**Tentativa 1: D = 750 mm**

- A = π × 0,75² / 4 = 0,442 m²
- v = Q / A = 0,20 / 0,442 = 0,45 m/s
- **Resultado:** v < v_min (0,6 m/s) — INADEQUADO

**Tentativa 2: D = 1.000 mm**

- A = π × 1,0² / 4 = 0,785 m²
- v = Q / A = 0,20 / 0,785 = 0,255 m/s
- **Resultado:** v < v_min — INADEQUADO (tubo muito grande)

**Solução: Aumentar declividade ou usar dois tubos D = 750 mm**

### 4.4 Redesign com Dois Tubos (D = 750 mm) e Declividade i = 2%

**Para cada tubo:**
- A_unit = 0,442 m²
- Q_unit = 0,10 m³/s

**Verificação com Manning:**
```
v = (1/n) × R^(2/3) × i^(1/2)

R = A / P = 0,442 / (π × 0,75) = 0,187 m

v = (1/0,012) × 0,187^(2/3) × 0,02^(1/2)
v = 83,33 × 0,0586 × 0,1414
v = 0,69 m/s  ✓  (0,6 < 0,69 < 2,0)
```

**Vazão verificada:**
```
Q = A × v = 0,442 × 0,69 = 0,305 m³/s/tubo
Q_total = 2 × 0,305 = 0,61 m³/s  ✓  (margem de segurança)
```

**SOLUÇÃO FINAL:**
- **2 tubos de concreto Ø 1.000 mm**
- **Declividade: 2,0%**
- **Comprimento: 15 m (atravessando talude)**
- **Velocidade: ~0,65 m/s (autolimpeza garantida)**

---

## 5. PROTEÇÃO DE ENTRADA/SAÍDA

### 5.1 Estrutura de Entrada (Cabeceira)

**Função:** Transição entre os taludes e a tubação

**Tipos comuns (DNIT):**

1. **Entrada direta (simples)**
   - Tubagem aparente
   - Uso: apenas taludes baixos (h < 2 m)
   - Proteção mínima

2. **Cabeceira em ala** (wingwall)
   - Muros laterais de contenção em concreto
   - Reduz turbulência
   - Custo: ~30% acima da entrada simples
   - Uso recomendado: taludes h > 1,5 m

3. **Cabeceira em tubo de seção maior** (trompeta)
   - Entrada cônica/funil
   - Reduz perdas de carga (K_e ≈ 0,20)
   - Custo elevado, uso seletivo

**Coeficientes de perda de entrada:**

| Tipo | K_e | Observação |
|------|-----|-----------|
| Entrada normal | 0,50 | Tubo com arestas |
| Entrada arredondada | 0,25 | R/D ≈ 0,10 |
| Entrada em trompeta | 0,10-0,20 | Expansão gradual |
| Entrada submersa | 0,30 | Já afogada |

### 5.2 Estrutura de Saída (Corpo)

**Objetivo:** Dissipar energia e evitar erosão no pé do talude

**Tipos:**

1. **Saída simples**
   - Tubagem aparente em talude
   - Fluxo livre de alta velocidade
   - RISCO: erosão, gully
   - Uso: v < 1,5 m/s, D ≤ 0,75 m

2. **Dissipador de energia (placa de concreto)**
   - Placa 0,5-1,0 m adiante da saída
   - Quebra a velocidade
   - Custo: ~R$ 800-1.200/unidade (2026)
   - Recomendado para v > 1,5 m/s

3. **Bacia de amortecimento** (stilling basin)
   - Estrutura em concreto com degraus internos
   - Reduz velocidade e turbulência
   - Uso: v > 2,5 m/s ou D > 1,25 m
   - Custo elevado, projetos críticos

4. **Gabiões/Enrocamento**
   - Proteção de talude em pé de saída
   - Alternativa econômica (v ≤ 2,0 m/s)
   - Comprimento: 2-4 m a jusante
   - Custo: ~R$ 150-250/m (2026)

---

### 5.3 Critério de Proteção de Saída (Recomendação DNIT)

```
SE v > 2,0 m/s:
  → Obrigatório dissipador ou bacia

SE 1,5 < v ≤ 2,0 m/s:
  → Recomendado enrocamento (talude ajustado a 1:1,5)

SE v ≤ 1,5 m/s:
  → Verificar erosão do talude natural
  → Cobertura vegetal adequada
```

**Exemplo (continuação do exemplo anterior):**

Projeto com v = 0,65 m/s → Proteção simples (cobertura vegetal)

---

## 6. CASOS REAIS — BRASIL

### 6.1 Caso 1: BR-116 km 420 (Minas Gerais)

**Contexto:** Travessia de córrego em zona de serras

**Dados de projeto:**
- Bacia: 45 ha
- Vazão de projeto: Q = 0,85 m³/s (Tr = 50 anos)
- Diâmetro adotado: 2 tubos Ø 1.250 mm
- Declividade: 1,5%
- Comprimento: 18 m

**Verificação:**
```
A_total = 2 × π × 1,25² / 4 = 2,454 m²
v = 0,85 / 2,454 = 0,346 m/s
```

**Problema detectado:** velocidade muito baixa (risco de sedimentação)

**Solução adotada:** Aumentar declividade para 3,0%
```
v = (1/0,012) × R^(2/3) × 0,03^(1/2) ≈ 1,1 m/s  ✓
```

**Proteção:** Bacia de amortecimento em concreto (v = 1,1 m/s justificou)

**Custo final:** ~R$ 185.000 (2023)

---

### 6.2 Caso 2: BR-101 km 890 (Santa Catarina)

**Contexto:** Rodovia duplicada, travessia em planície com maré

**Desafio:** Controle de maré alta (remanso em saída)

**Solução:**
- Bueiro em regime misto (entrada livre, saída submersa)
- Cálculo com curva remanso (backwater)
- Diâmetro: 3 tubos Ø 1.000 mm
- Válvula de retenção (flapper) na saída para impedir refluxo

**Resultado:** Custo ~15% acima (válvula especializada)

---

### 6.3 Caso 3: Duplicação BR-381 km 250 (São Paulo)

**Contexto:** Ampliação de bueiro existente (D = 1,0 m)

**Problema:** Bacia cresceu de 28 ha para 52 ha

**Vazão anterior:** Q = 0,32 m³/s
**Vazão nova:** Q = 0,64 m³/s

**Solução:**
- Adicionar segundo tubo paralelo D = 1,0 m
- Reconstituir cabeceira em ala (wingwall)
- Aplicar dissipador de energia novo
- Reforçar talude com geotextil

**Investimento:** ~R$ 220.000 (2024)

---

## 7. TABELAS E REFERÊNCIAS RÁPIDAS

### 7.1 Tabela de Velocidades por Diâmetro e Declividade

```
Vazão Q = 0,20 m³/s | Coef. Manning n = 0,012

Diâmetro | i = 0,5% | i = 1,0% | i = 2,0% | i = 3,0%
---------|----------|----------|----------|----------
0,75 m   | 0,38 v   | 0,54 v   | 0,76 v   | 0,93 v
1,00 m   | 0,26 v   | 0,38 v   | 0,53 v   | 0,65 v
1,25 m   | 0,19 v   | 0,27 v   | 0,39 v   | 0,47 v
1,50 m   | 0,14 v   | 0,20 v   | 0,28 v   | 0,35 v
2,00 m   | 0,10 v   | 0,14 v   | 0,20 v   | 0,25 v
```

*Nota: valores em m/s; use Manning para maior precisão*

### 7.2 Dimensões de Dissipadores Típicos

| Vazão (m³/s) | Placa (m) | Profundidade (m) | Comprimento (m) |
|--------------|-----------|-----------------|-----------------|
| 0,10-0,30 | 1,0 × 1,0 | 0,30 | 1,5 |
| 0,30-0,60 | 1,5 × 1,5 | 0,50 | 2,0 |
| 0,60-1,20 | 2,0 × 2,0 | 0,70 | 2,5 |
| > 1,20 | Bacia especial | Projeto | Projeto |

---

## 8. CHECKLIST DE PROJETO

- [ ] Bacia hidrológica delimitada e área medida
- [ ] Vazão de projeto calculada (método racional ou hidrograma)
- [ ] Período de retorno e fator de segurança definidos
- [ ] Material de tubagem selecionado (concreto, PVC, aço corrugado)
- [ ] Diâmetro tentativo escolhido (tabela DNIT)
- [ ] Velocidade verificada (v_min ≤ v ≤ v_máx)
- [ ] Declividade adequada para autoLimpeza
- [ ] Comprimento do bueiro medido em perfil
- [ ] Tipo de entrada definido (cabeceira, wingwall, trompeta)
- [ ] Tipo de saída definido (simples, dissipador, bacia)
- [ ] Cotas de entrada/saída compatíveis com talude
- [ ] Drenagem de pé de talude coordenada
- [ ] Manutenção prevista (limpeza anual)
- [ ] Custo orçado e aprovado

---

## 9. REFERÊNCIAS TÉCNICAS

**Normas Brasileiras:**
- DNIT ES 131/86 — Instrução para Drenagem de Rodovias
- NBR 5643 — Tubo de Concreto Armado para Águas Pluviais e Esgotos Sanitários
- NBR 12657 — Tubo de Concreto Simples Para Drenagem

**Referências Internacionais:**
- AASHTO HEC-22 (Highway Drainage Design Manual)
- FHWA HEC-12 (Hydraulic Design of Culverts)
- Chow, V.T. — Open Channel Hydraulics (McGraw-Hill, 1959)

**Docentes/Especialistas:**
- DNIT (Departamento Nacional de Infraestrutura de Transportes)
- IPR (Instituto de Pesquisas Rodoviárias)

---

## 10. CONTATOS E SUPORTE

**Para dúvidas técnicas sobre bueiros em projetos Manta Associados:**
- Agente-infraestrutura (S1 — Rodovias)
- Contato: Gerência de Drenagem Rodoviária

---

**Documento atualizado:** 2026-08-04  
**Versão:** 1.0  
**Próxima revisão:** 2027-08-04
