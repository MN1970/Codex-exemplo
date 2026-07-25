# D7.1 — ESPECIFICAÇÃO TÉCNICA: HORIZONTAL GEOMETRY RESILIENTE

**Versão:** 1.0  
**Data:** 2026-07-25  
**Responsável:** Setor de Engenharia de Infraestrutura  
**Aplicação:** Rodovias e acessos com critérios sísmicos (PGA ≥ 0.1g)

---

## 1. INTRODUÇÃO E ESCOPO

Este documento estabelece parâmetros de projeto geométrico horizontal resiliente para infraestruturas viárias em zonas sísmicas. Os critérios incorporam multiplicadores de segurança que aumentam raios de curvatura, superelevação e distância de visibilidade conforme o nível de perigosidade sísmica (PGA — Peak Ground Acceleration).

**Objetivo:** Garantir que a geometria horizontal mantenha segurança operacional durante e pós-eventos sísmicos, especialmente em:
- Taludes de terraplenagem em curvas
- Áreas urbanas com espaço restrito (narrow ROW)
- Vias com fluxo de evacuação crítico

---

## 2. PARÂMETROS SÍSMICOS BASE

### 2.1 Classificação por PGA Zone

| PGA Zone | Intervalo PGA (g) | Classificação | Multiplicador Base | Aplicação |
|----------|-------------------|---------------|-------------------|-----------|
| Z0       | < 0.05            | Baixo risco   | 1.0 (sem ajuste)  | Interior, planaltos estáveis |
| Z1       | 0.05–0.10         | Risco moderado| 1.1               | Bordas cratônicas, SOB |
| Z2       | 0.10–0.15         | Risco elevado | 1.2               | Andes, estruturas frágeis |
| Z3       | 0.15–0.25         | Risco muito elevado | 1.25      | Subducção, falhas ativas |
| Z4       | ≥ 0.25            | Risco crítico | 1.3               | Zona de subducção próxima |

**Notas:**
- PGA obtida de Norma NBR 15421:2016 (mapa de perigosidade sísmica) ou mapas estaduais
- Valores referem-se ao período de retorno TR = 475 anos (50% probabilidade em 50 anos)
- Para estruturas críticas (hospitais, centros de controle), usar TR = 2475 anos

---

## 3. RAIOS DE CURVATURA — AJUSTE SÍSMICO

### 3.1 Fórmula Base

Raio mínimo de curvatura horizontal (NBR 11682 adaptada):

$$R_{min} = \frac{V^2}{127 \times (f + e_{max})}$$

Onde:
- **V** = velocidade de projeto (km/h)
- **f** = coeficiente de fricção lateral (0.10–0.15, conforme NBR 12241)
- **e_{max}** = superelevação máxima (%)
- **R_{min}** = raio mínimo (m)

### 3.2 Multiplicador Sísmico para Raio

$$R_{design} = R_{min} \times M_{seismic} \times K_{local}$$

Onde:
- **M_{seismic}** = multiplicador por PGA zone (Tabela 2.1: 1.0–1.3)
- **K_{local}** = fator de ajuste local:
  - K_{local} = 1.15 (narrow ROW, ROW < 30 m)
  - K_{local} = 1.0 (ROW > 50 m, espaço livre)
  - K_{local} = 1.10 (zona urbana, estruturas adjacentes)

### 3.3 Tabela de Raios Mínimos Sísmicos

Para V = 80 km/h, f = 0.12, e_{max} = 10%, com 10 m de ROW (narrow):

| PGA Zone | M_{seismic} | R_{min} base (m) | K_{local} | R_{design} (m) | Classe |
|----------|-------------|------------------|-----------|----------------|---------|
| Z0       | 1.0         | 320              | 1.0       | 320            | L1      |
| Z1       | 1.1         | 320              | 1.0       | 352            | L1      |
| Z2       | 1.2         | 320              | 1.15      | 441.6          | L2      |
| Z3       | 1.25        | 320              | 1.15      | 460            | L2      |
| Z4       | 1.3         | 320              | 1.15      | 478            | L3      |

**Interpretação:** Em zona Z4 com ROW estreita, aumentar raio de 320 m → 478 m (+49%)

---

## 4. SUPERELEVAÇÃO — AJUSTE SÍSMICO

### 4.1 Fórmula Base e Ajuste

Superelevação de projeto (NBR 11682):

$$e = \frac{V^2}{127 \times R} - f$$

Superelevação resiliente com ajuste sísmico:

$$e_{resilient} = e_{base} + \Delta e_{seismic}$$

Onde **Δe_{seismic}** (incremento em %) é dado por:

| PGA Zone | Δe_{seismic} (%) | Justificativa |
|----------|------------------|---|
| Z0       | 0                | Sem ajuste |
| Z1       | +0.5             | Compensação de deslocamento transversal |
| Z2       | +1.0             | Aumento de força centrífuga em sismo |
| Z3       | +1.25            | Proteção contra deslizamento lateral |
| Z4       | +1.5             | Máximo recomendado (limite conforto) |

### 4.2 Limite Máximo de Superelevação

$$e_{max} = \min(e_{resilient}, 12\%)$$

Restrição prática: não exceder 12% para manutenção de tração em piso molhado.

### 4.3 Exemplo de Cálculo

Rodovia com V = 80 km/h, R = 400 m, f = 0.12, zona Z3:

1. Superelevação base: $e_{base} = \frac{80^2}{127 \times 400} - 0.12 = 0.125 - 0.12 = 0.005$ (0.5%)
2. Ajuste sísmico Z3: Δe = +1.25%
3. Superelevação resiliente: e_{resilient} = 0.5% + 1.25% = **1.75%**
4. Verificação: 1.75% < 12% ✓

---

## 5. DISTÂNCIA DE VISIBILIDADE — AJUSTE SÍSMICO

### 5.1 Aumento de Distância de Visibilidade

Distância de visibilidade de parada (NBR 11682):

$$D_v = \frac{V}{3.6} \times t + \frac{V^2}{254 \times d}$$

Onde:
- V = velocidade (km/h)
- t = tempo de percepção-reação (2.5 s)
- d = desaceleração (m/s²), typ. 3.5 m/s² (0.35g)

**Ajuste sísmico:**

$$D_{v,seismic} = D_v \times (1 + F_{vis})$$

Onde **F_{vis}** (fator de aumento) é:

| PGA Zone | F_{vis} (%) | Justificativa |
|----------|-------------|---|
| Z0       | 0           | Sem ajuste |
| Z1       | 5           | Aumento de 1.05x |
| Z2       | 10          | Aumento de 1.10x |
| Z3       | 12          | Aumento de 1.12x |
| Z4       | 15          | Aumento de 1.15x |

### 5.2 Verificação de Raio de Curvatura para Visibilidade

Para curvas, garantir que o raio de visibilidade interno (sem obstáculos) atenda:

$$R_{vis} \geq R_{design} \times \sqrt{\frac{D_{v,seismic}}{2 \times e_{resilient}}}$$

(Critério geométrico de curva vista)

---

## 6. TABELAS CONSOLIDADAS POR PGA ZONE

### Tabela 6.1: Fatores Sísmicos Consolidados

| PGA Zone | M_{raio} | Δe (%) | F_{vis} (%) | Aplicação |
|----------|----------|--------|-------------|-----------|
| Z0       | 1.0      | 0      | 0           | Sem ajuste |
| Z1       | 1.1      | 0.5    | 5           | Moderado |
| Z2       | 1.2      | 1.0    | 10          | Elevado |
| Z3       | 1.25     | 1.25   | 12          | Muito elevado |
| Z4       | 1.3      | 1.5    | 15          | Crítico |

### Tabela 6.2: Raios Mínimos para Diferentes Velocidades (Z2, K_{local}=1.0)

| Velocidade (km/h) | R_{min} (m) | R_{seismic} Z2 (m) | Incremento (%) |
|-------------------|-------------|-------------------|----------------|
| 40                | 80          | 96                | +20            |
| 60                | 180         | 216               | +20            |
| 80                | 320         | 384               | +20            |
| 100               | 500         | 600               | +20            |
| 120               | 720         | 864               | +20            |

---

## 7. ÁRVORE DE DECISÃO DE PROJETO

```
INÍCIO: Projeto Horizontal em Zona Sísmica
├── [1] Classificar PGA Zone (NBR 15421)
│   ├── Z0 (< 0.05g) → M = 1.0 (aplicar padrão DNIT)
│   ├── Z1 (0.05–0.10g) → M = 1.1
│   ├── Z2 (0.10–0.15g) → M = 1.2
│   ├── Z3 (0.15–0.25g) → M = 1.25
│   └── Z4 (≥ 0.25g) → M = 1.3
│
├── [2] Definir Velocidade de Projeto (V)
│   ├── V ≤ 60 km/h → Raio base: DNIT tabela
│   ├── 60 < V ≤ 100 km/h → Raio base: DNIT tabela
│   └── V > 100 km/h → Raio base: especificar critério
│
├── [3] Avaliar Restrições de ROW
│   ├── ROW < 30 m → K_{local} = 1.15 (narrow)
│   │   ├── [3a] Possível aumentar R (superestrutura)?
│   │   │   ├── Sim → Aplicar M × K_{local}
│   │   │   └── Não → Diálogo com cliente (trade-off custo/segurança)
│   │   └── [3b] Necessário ajuste de superelevação?
│   │       └── Sim → Verificar e_{max} ≤ 12%
│   ├── 30 ≤ ROW ≤ 50 m → K_{local} = 1.10
│   └── ROW > 50 m → K_{local} = 1.0
│
├── [4] Calcular Raio Mínimo Resiliente
│   ├── R_{design} = R_{min} × M × K_{local}
│   └── Comparar com raios propostos em projeto
│
├── [5] Ajustar Superelevação
│   ├── e_{resilient} = e_{base} + Δe_{seismic}
│   ├── Verificar e_{resilient} ≤ 12%
│   └── Documentar justificativa se Δe ≠ 0
│
├── [6] Verificar Distância de Visibilidade
│   ├── Calcular D_{v,seismic} com F_{vis}
│   ├── Verificar sightline em curvas (sem obstáculos)
│   └── Se insuficiente → aumentar R ou remover obstáculos
│
├── [7] Caso de Uso: Área Urbana?
│   ├── Sim → K_{local} = 1.10 (já aplicado)
│   │   ├── Verificar interferência com estruturas
│   │   ├── Considerar fluxo de evacuação pós-sismo
│   │   └── Analisar aceleração lateral percebida (a_{lat} ≤ 0.2g)
│   └── Não → Aplicar critério campo aberto
│
└── [8] SAÍDA: Raio, superelevação e visibilidade validados
    └── Documentar em planta com anotações de perigosidade sísmica
```

---

## 8. CASOS DE EDGE — TRATAMENTO ESPECIAL

### 8.1 Narrow ROW (< 30 m)

**Cenário:** Acesso urbano ou retrofit com espaço limitado.

**Estratégias (em ordem de preferência):**

1. **Aumentar raio mesmo com ROW restrito**
   - Negociar desapropriação marginal (0.5–1.0 m)
   - Custo-benefício: segurança sísmica > custo de aquisição
   
2. **Reduzir velocidade de projeto**
   - V: 80 → 60 km/h → R_{min} reduz ~40%
   - Aplicável se fluxo permitir (via coletora, não arterial)
   
3. **Solução em taludes**
   - Muros de contenção inclinados (ângulo ajustado)
   - Evita alargamento horizontal
   - Custo: 30–50% mais que terraplenagem natural
   
4. **Última opção: Aceitar K_{local} = 1.15 com análise crítica**
   - Requer aprovação de cliente + revisão de segurança
   - Documentar em ART (Anotação de Responsabilidade Técnica)

**Exemplo de trade-off:**
- V = 80 km/h, Z3, ROW = 15 m
- R_{min} × 1.25 × 1.15 = 320 × 1.44 = 460 m
- **Alternativa:** V reduzido = 60 km/h → R_{min} = 180 m → 180 × 1.25 × 1.15 = 259 m (80% do custo, segurança aceitável)

---

### 8.2 Zona Urbana com Estruturas Adjacentes

**Cenário:** Rua em aglomeração urbana, casarões/prédios a ≤ 5 m do ROW.

**Ajustes:**

1. **K_{local} = 1.10** (já incorporado)
2. **Análise de aceleração lateral percebida:**
   - Limite: a_{lat} ≤ 0.2g (conforto de ocupantes em edificações)
   - Calcular: $a_{lat} = \frac{V^2}{R \times 127}$ (em g)
   - Se a_{lat} > 0.2g → aumentar R ou reduzir V
   
3. **Verificação de fluxo de evacuação pós-sismo**
   - Garantir que curva não crie gargalo
   - Raio > 200 m preferível (permite fluxo bidirecional em emergência)
   
4. **Gestão de águas de chuva em superelevação**
   - e_{resilient} elevada → drenagem crítica
   - Garantir sarjetas/drenos suficientes (não > 30 m sem caixa)

**Checklist urbano:**
- [ ] PGA Zone confirmada (mapas de microzonação se disponível)
- [ ] Estruturas críticas (hospitais, estações, escolas) em raio de 500 m?
- [ ] Fluxo de evacuação mapeado
- [ ] Drenagem superficial dimensionada para e_{resilient}
- [ ] Aprovação com prefeitura/concessionária local

---

### 8.3 Taludes de Terraplenagem em Curva (Estabilidade)

**Cenário:** Escavação/aterro em curva horizontal com declividade transversal acentuada.

**Fator adicional: inclinação de talude** (β)

Para taludes > 45°, aplicar multiplicador adicional:

$$K_{talude} = 1 + 0.15 \times \left( \frac{\beta}{45°} \right)^{0.5}$$

Exemplo: β = 60° → K_{talude} = 1 + 0.15 × √(60/45) = 1.18

Raio final:
$$R_{final} = R_{min} \times M_{seismic} \times K_{local} \times K_{talude}$$

**Estudo de caso:**
- V = 60 km/h, Z2, ROW = 35 m, talude = 60°
- R_{min} = 180 m
- R_{final} = 180 × 1.2 × 1.10 × 1.18 = 283 m (+57% acima base)

**Medidas geotécnicas recomendadas:**
- Geotextil ou solo reforçado (FS contra deslizamento ≥ 1.5)
- Drenagem subsuperficial paralela ao talude
- Análise de liquefação se presença de solo saturado

---

## 9. FÓRMULAS CONSOLIDADAS — RESUMO

### 9.1 Raio Mínimo Resiliente (Fórmula Mestra)

$$\boxed{R_{design} = \frac{V^2}{127 \times (f + e_{base})} \times M_{seismic} \times K_{local} \times K_{talude}}$$

Parâmetros tabelados em seções 2.1, 4, 8.

### 9.2 Superelevação Resiliente

$$\boxed{e_{resilient} = e_{base} + \Delta e_{seismic} \leq 12\%}$$

Δe_{seismic} da Tabela 4.1.

### 9.3 Distância de Visibilidade Resiliente

$$\boxed{D_{v,seismic} = D_v \times (1 + F_{vis})}$$

F_{vis} da Tabela 5.1.

---

## 10. DOCUMENTAÇÃO E ANOTAÇÕES EM PROJETO

### 10.1 Planta com Anotações Obrigatórias

Cada curva horizontal deve conter:

```
CURVA 1:
├── PGA Zone: [Z1/Z2/Z3/Z4]
├── R: [medida] m | R_{design} exigido: [medida] m | Status: [✓ OK / ⚠ CRÍTICA]
├── e: [%] | e_{seismic}: [%] | Limite: 12%
├── D_v: [m] | D_{v,seismic}: [m] | Sightline: [✓ OK / ✗ OBSTÁCULO]
├── Tipo ROW: [Narrow/Normal/Aberto]
├── Observações: [Talude, estruturas adjacentes, restrições]
└── Responsável: [Nome] | Data: [YYYY-MM-DD]
```

### 10.2 Relatório Técnico de Justificativa

Quando M_{seismic} ≠ 1.0, preparar memorando incluindo:
1. Classificação de PGA (fonte: NBR 15421 / mapa estadual)
2. Justificativa de cada multiplicador aplicado (M, K_{local}, K_{talude})
3. Análise de alternativas consideradas (aumento ROW, redução V, etc.)
4. Custos incrementais
5. Aprovação do cliente e revisor técnico

---

## 11. VERIFICAÇÕES FINAIS — CHECKLIST

- [ ] PGA Zone classificada conforme NBR 15421 (ou norma vigente)
- [ ] Raio mínimo resiliente calculado e comparado com projeto
- [ ] Superelevação ajustada e verificada (≤ 12%)
- [ ] Distância de visibilidade atende critério sísmico
- [ ] ROW, talude e contexto urbano avaliados
- [ ] Trade-offs documentados e aprovados
- [ ] Anotações inseridas em planta
- [ ] ART assinada por responsável técnico
- [ ] Drenagem superficial dimensionada para e_{resilient}
- [ ] Fluxo de evacuação (se aplicável) validado

---

## REFERÊNCIAS NORMATIVAS

- **NBR 11682:2009** — Estabilidade de taludes
- **NBR 12241:2006** — Classificação técnica de rodovias
- **NBR 15421:2016** — Perigosidade sísmica — mapa de classificação
- **DNIT 106/2009-ES** — Estradas de rodagem — projeto geométrico
- **ABNT EB-1:2023** (proposto) — Resiliência de infraestruturas (em consulta pública)
- **ACI 341-23** — Earthquake-Resistant Concrete Buildings (referência internacional)

---

**Versão final:** 2026-07-25  
**Próxima revisão:** 2027-07-25 (ou após novo mapa de perigosidade sísmica)
