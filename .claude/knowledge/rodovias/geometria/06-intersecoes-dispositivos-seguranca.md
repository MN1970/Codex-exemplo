# Interseções, Dispositivos & Segurança em Rodovias

**Data**: 2026-08-03  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:intersecoes:*` | `rod:seguranca:*`  
**Normas**: DNIT ES 101/97, ABNT NBR 15895, NBR 14644, AASHTO

---

## 1. Classificação de Interseções

### 1.1 Em Nível (At-Grade)

```
Tipo              | Descrição                | Vd Máx | Fluxo Crítico
────────────────────────────────────────────────────────
Rotatória         | Circular, 1+ faixas     | 40 km/h | Moderado
T Simples         | Três ramos              | 60 km/h | Baixo
Cruz Simples      | Quatro ramos            | 60 km/h | Baixo
T Dupla           | Acesso por pistas duplas| 80 km/h | Alto
Y/Estrela         | Múltiplos ramos         | Variável| Variável
```

### 1.2 Desniveladas (Grade-Separated)

```
Tipo              | Nomenclatura   | Uso Típico       | Custo
─────────────────────────────────────────────────────
Trevo Completo    | Full Cloverleaf| BR × BR          | Muito Alto
Trevo Parcial     | PARCLO (A-D)   | BR × Estadual    | Alto
Diamante          | Diamond        | Via × Via        | Médio
Trombeta          | Trumpet        | Fim de via       | Médio
Giratorio Elevado | Roundabout Ele.| Espaço reduzido  | Alto

PARCLO Tipos:
├─ PARCLO A: 2 ramos superiores diretos
├─ PARCLO AB: 1 ramo direto + 1 semi-direto
├─ PARCLO B: Semi-diretos (melhor para terrenho ondulado)
└─ PARCLO D: Meia trombeta
```

---

## 2. Rotatórias (Roundabouts)

### 2.1 Elementos Geométricos

**Norma Principal**: DNIT ES 101/97, Item 6.1

```
             ┌─────────────────┐
             │   Entrada       │
             │   (Rampa 1:20)  │
             │                 │
    ┌────────┴────────────────┬┴──────────────┐
    │                         │               │
    │   ANEL GIRATÓRIO        │   Saída       │
    │   (Raio R_int)          │   (Rampa)     │
    │                         │               │
    └────────┬────────────────┼───────────────┘
             │                │
      R_ext (Raio Externo)
```

### 2.2 Dimensionamento

**Raio Externo (R_ext)**:
```
Vd (km/h) | R_ext (m) | Categoria          |
-----------|-----------|-------------------|
20-30      | 15-20     | Rotatória Compacta |
30-40      | 20-25     | Rotatória Pequena  |
40-50      | 25-35     | Rotatória Normal   |
50+        | 35+       | Rotatória Grande   |

Recomendação DNIT: R_ext ≥ 20m (segurança mínima)
```

**Raio Interno (R_int)**:
```
R_int = R_ext - Largura da Pista - Banqueta Interna

Exemplo:
R_ext = 30m
Largura pista = 8m (2 faixas × 4m)
Banqueta interna = 2m
R_int = 30 - 8 - 2 = 20m ✓
```

**Triângulo de Visibilidade**:
```
Entrada:
├─ d_parada para Vd = 30 km/h ≈ 25m
├─ d_parada para Vd = 40 km/h ≈ 35m
└─ Verificar visibilidade direta da ilha

Fórmula de Recuo:
f = R_int - √(R_int² - (d_parada/2)²)

Exemplo (R_int=20m, d=35m):
f = 20 - √(400 - 306) = 20 - √94 = 20 - 9.7 ≈ 10.3m
(Necessário recuo de banqueta de ~10m)
```

### 2.3 Movimentos Críticos

```
Movimento de Conflito    | Tipo            | Severidade
────────────────────────────────────────────────────
Entrada × Circulação     | Cruzamento      | Alta
Saída × Circulação       | Cruzamento      | Alta
Circulação × Circulação  | Tangencial      | Baixa
Pedestres × Entrada      | Cruzamento      | Alta
Bicicletas               | Faixa dedicada  | Média

Recomendação:
- Faixa de pedestre na entrada (zebra de 2-3m)
- Faixa de bicicleta em periferia (separada 0.5-1.0m)
- Tachões refletivos em todas as saídas
```

---

## 3. Interseções Desniveladas

### 3.1 Trevo Completo (Full Cloverleaf)

**Norma**: DNIT ES 101/97, Item 6.2 + AASHTO Green Book

```
Geometria:
└─ 4 quadrantes com rampas helicoidais
└─ Raio mínimo de rampa: 100-150m
└─ Superelevação em rampa: até 6% (para 30-40 km/h)

Vantagens:
✓ Sem conflitos de cruzamento (todos separados)
✓ Velocidade mantida (até 60 km/h)
✓ Fluxo contínuo em congestionamento

Desvantagens:
✗ Custo muito elevado (~R$ 80-120M)
✗ Espaço grande (500m × 500m mínimo)
✗ Área inutilizada em quadrantes

Aplicação:
→ BR × BR (federal × federal, alto volume)
→ São Paulo, RJ, MG apenas
```

**Seção Transversal Típica**:
```
Pista Principal: 7.20m (2 × 3.60m faixas)
Rampa: 6.00m (1 × 6m, 1 sentido)
Acostamento: 2.50m (ambos)
Total por nível: ~18m

Altura livre mínima: 4.50m (por DNIT)
```

### 3.2 PARCLO (Partial Cloverleaf)

**Melhor relação custo-benefício para BR × Estadual**

#### PARCLO A (Típico)
```
Quadrante Esquerdo:
├─ Rampa direta (LT turnoff)
└─ Fluxo contínuo

Quadrante Direito:
├─ Rampa semi-direta (via local collector)
└─ Passagem pela via transversal

Custo: ~R$ 45-60M/interseção
Aplicação: BR-116, BR-101 (duplicação)
```

**Dimensionamento**:
```
Rampa Direta:
- Raio mínimo: 150-200m
- Superelevação: 4-5%
- Vd: 60 km/h

Rampa Semi-Direta:
- Raio mínimo: 200-250m
- Superelevação: 3-4%
- Vd: 50 km/h (com desaceleração gradual)
```

#### PARCLO B (Terreno Montanhoso)
```
Ambas as rampas semi-diretas
└─ Melhor adaptação a topografia acidentada
└─ Rampas menores (~300m cada)
└─ Custo: ~R$ 35-50M
```

#### PARCLO AB & D
```
PARCLO AB:
├─ 1 rampa direta
└─ 1 rampa semi-direta
└─ Solução intermediária

PARCLO D (Meia Trombeta):
├─ Apenas 1 quadrante com rampa
├─ Outro quadrante com retorno via coletora
└─ Custo: ~R$ 25-35M (BR × municipal)
```

### 3.3 Interseção em Diamante (Diamond)

**Melhor para Via × Via (não BR × BR)**

```
Geometria:
└─ Aproximação vertical (V ou Y)
└─ Rotatória ou semaforização na transversal
└─ 2 rampas de ~300m cada

    BR
     │
   ┌─┴─┐
   │   │  ◄─ Rampas de acesso
   └─┬─┘
     │
  ─ ─ ─ ─  Via local (semaforizada)
     │
```

**Vantagens**:
- Custo: R$ 15-25M (43% de Trevo Completo)
- Espaço: ~250m × 250m
- Fácil de expandir para PARCLO depois
- Aplicação: BR × Estadual (volume moderado)

**Dimensionamento**:
```
Rampa:
├─ Comprimento: 300-400m
├─ Raio curva: 150-200m
├─ Superelevação: 4-5%
├─ Vd rampa: 50-60 km/h

Transversal (via local):
├─ Semaforização T-4 (ciclo 60-80s)
├─ Faixas: 2 (1 por sentido mín)
├─ Visibilidade: d ≥ 80m em ambas as direções
```

### 3.4 Trombeta (Trumpet)

**Para extremidades de via ou "Y" em terreno montanhoso**

```
Geometria:
└─ 1 rampa helicoidada (260-300m)
└─ Curvatura contínua (não muda de sentido)

Aplicação:
→ Fim de pista dupla (transição para simples)
→ Acesso a vale/serra (3D complexa)
→ Custo: R$ 20-30M
```

---

## 4. Normas de Segurança em Rodovias

### 4.1 Dispositivos de Contenção (Defensas)

**Norma Principal**: NBR 14644 — Balizamento de Rodovias

#### Tipos de Defensa

```
Tipo              | Material    | Uso                | Altura | Espaçamento
──────────────────────────────────────────────────────────────────
Defensa Metálica  | Aço galv.   | Curvas de alto      | 0.65m  | 0.30m
                  |             | risco (R < 250m)    |        |
──────────────────────────────────────────────────────────────────
Defensa de Pneu   | Pneu usado  | Proteção temporária | 0.50m  | 0.50m
                  | + correia   | (obra, evento)      |        |
──────────────────────────────────────────────────────────────────
Mureta/Guarda-   | Concreto    | Separação de nível  | 1.00m  | N/A
corpo             |             | (viadutos, pontes)  |        |
──────────────────────────────────────────────────────────────────
Tachão Refletivo  | Plástico    | Delimitação de      | 0.08m  | 0.50m
                  | + vidro     | faixa/saída         |        |
──────────────────────────────────────────────────────────────────
Defensa Rígida    | Concreto    | Separador central   | 0.80m  | Contínuo
                  | pré-moldado | (pista dupla)       |        |
```

#### Critérios de Instalação

```
DNIT ES 101/97 + NBR 14644:

1. Curvas Horizontais:
   ├─ R < 150m → Defensa obrigatória
   ├─ 150m ≤ R < 250m → Defensa recomendada
   └─ R ≥ 250m → Opcional (análise de risco)

2. Superelevação:
   ├─ e ≥ 6% → Defensa recomendada
   └─ e < 6% → Análise caso-a-caso

3. Tipo de Talude:
   ├─ Altura crítica > 5m → Defensa obrigatória
   ├─ Corpo de água adjacente → Defensa obrigatória
   └─ Rocha/solo estável → Opcional

Exemplo:
R = 200m, e = 5%, altura talude = 8m
→ Defensa OBRIGATÓRIA (R < 250m + altura > 5m)
```

### 4.2 Sinalização Horizontal (Faixas)

**Norma Principal**: ABNT NBR 15895 — Sinalização Horizontal

```
Tipo de Linha            | Código | Significado
──────────────────────────────────────────────────
Contínua Simples         | ───    | Proibida ultrapassagem
Contínua Dupla           | ═══    | Máxima restrição
Tracejada (curta)        | - - -  | Permitida ultrapassagem
Tracejada (longa)        | ─ ─ ─  | Fim próximo de proibição
Zigue-zague              | ∿ ∿ ∿  | Proibido parar/estacionar

Aplicação por Alinhamento:
──────────────────────────────────────────────────
Alinhamento              | Linha Recomendada
──────────────────────────────────────────────────
Tangente longa (>500m)   | Tracejada (ultrapassagem)
Curva com R < 250m       | Contínua (sem ultrapassagem)
Aproximação de PI        | Contínua (segurança)
Saída de curva           | Tracejada (após 50-100m)
Rampa > 6%              | Contínua (segurança)

Exemplo BR-116:
─ Tangente 800m: ─ ─ ─ ─ (tracejada)
─ Curva 200m: ─────────── (contínua)
─ Saída de curva 100m: ─ ─ ─ ─ (transição)
```

### 4.3 Sinalização Vertical (Placas)

```
Tipo                    | Distância Prévia | Vd
────────────────────────────────────────────
Curva à esquerda        | 150m             | 80 km/h
Curva à direita         | 150m             | 80 km/h
Curva dupla             | 150m (ambas)     | 60 km/h
Rampa (subida)          | 100m             | 60 km/h
Rampa (descida)         | 100m             | 80 km/h
Redução de velocidade   | 200m             | 40 km/h (zona)
────────────────────────────────────────────

Além disso:
├─ Quilometragem (a cada 100m)
├─ Emergência (SOS + distância)
├─ Limite de velocidade (permanente/variável)
└─ Informação (parada, combustível, etc)
```

### 4.4 Análise de Risco Geométrico (AIG)

**Metodologia DNIT para identificar pontos críticos**

```
Índice de Risco Geométrico = f(V_operada, R_atual, e_atual, visibilidade)

Classificação:
───────────────────────────────────────────────
Risco      | R_mín teórico | R_atual | Medidas
───────────────────────────────────────────────
Baixo      | 250m          | > 300m  | Nenhuma
Médio      | 200m          | 200-300m| Sinalização
Alto       | 150m          | 150-200m| Sinalização + Defensa
Crítico    | < 150m        | < 150m  | Defensa + Redução Vd + Projeto

Exemplo BR-116 SP (Vd=100 km/h):
┌─────────────────────────────────────────────┐
│ Estaca 150+000:                             │
│ R = 200m (Vd_teórico = 90 km/h)            │
│ V_operada ≈ 110 km/h (campo)                │
│ e = 5%, visibilidade < 137m                 │
│                                             │
│ RISCO: ALTO                                 │
│ Ação: Defensa + Placa "Curva Perigosa"      │
│       + Tacha refletiva 50m antes           │
└─────────────────────────────────────────────┘
```

---

## 5. Normas de Segurança Complementares

### 5.1 NBR 11682 — Estabilidade de Encostas

```
Fator de Segurança (FS):

Para taludes em corte/aterro:
───────────────────────────────────────────
Condição                    | FS Mínimo
───────────────────────────────────────────
Permanente (longo prazo)    | 1.3-1.5
Temporário (construção)     | 1.2-1.3
Emergência (sismo)          | 1.0-1.1
───────────────────────────────────────────

Se FS < limite:
├─ Reduzir altura talude (degraus)
├─ Aumentar inclinação (1:1.5 → 1:2)
├─ Drenagem (interceptação de água)
├─ Contenção (geotêxtil, concreto)
└─ Monitoramento (piezômetros)
```

### 5.2 ABNT NBR 6123 — Ações do Vento

```
Aplicável a Viadutos e Estruturas:

Vento de projeto:
V_proj = 150 km/h (Brasil central)
V_proj = 170 km/h (litoral)

Coeficiente de forma (Cf):
├─ Ponte: Cf = 1.2-1.5
├─ Viaduto: Cf = 1.1-1.3
└─ Mureta: Cf = 1.0

Pressão de vento:
P = 0.613 × V² × Cf

Exemplo (V=150 km/h, Cf=1.3):
P = 0.613 × 150² × 1.3 = 17.9 kPa ≈ 1.8 t/m²

→ Estrutura deve resistir a 1.8 t/m² (momento fletor)
```

### 5.3 Iluminação (Pontos Críticos)

```
Norma: ABNT NBR 5101 (Iluminação Pública)

Pontos obrigatórios:
├─ Interseções desniveladas (entrada e saída)
├─ Curvas com R < 200m (e ≥ 6%)
├─ Pontes e viadutos (comprimento > 100m)
├─ Rampa > 7% (comprimento > 500m)
├─ Túneis (sempre)

Iluminância mínima:
├─ Curva crítica: E ≥ 20 lux
├─ Interseção: E ≥ 30 lux
├─ Normal: E ≥ 10 lux

Espaçamento de postes:
├─ Curva crítica: 25-30m
├─ Normal: 35-40m
└─ Economia (redução Vd): até 50m

Tipo de lâmpada:
├─ Sódio (60% uso, economia)
├─ LED (crescente, 30% economia vs sódio)
└─ Mercúrio (descontinuado)
```

---

## 6. Casos de Risco Crítico & Mitigação

### 6.1 Exemplo 1: Curva Perigosa (BR-116 SP)

```
Dados de Acidentes:
├─ 12 acidentes/ano em 2km
├─ 3 com vítima fatal
├─ Maioria: capotamento/saída da pista

Análise Geométrica:
├─ R = 180m (Vd=100 km/h → R_mín=265m)
├─ e = 4% (abaixo de 7.5% recomendado)
├─ Visibilidade = 100m (abaixo de 137m requerido)
├─ Talude de corte = 10m (altura crítica)

RISCO: CRÍTICO ⚠️

Plano de Mitigação:
1. Curto prazo (6 meses):
   ├─ Instalar defensa metálica dupla
   ├─ Placa "Curva Perigosa" 300m antes
   ├─ Tacha refletiva (alerta)
   ├─ Reduzir Vd para 80 km/h (sinalização)
   ├─ Iluminar trecho (12 postes LED)

2. Médio prazo (1-2 anos):
   ├─ Realizar AIG (análise integrada)
   ├─ Projeto de reconstrução (R→250m)
   ├─ Execução de ampliação de R

3. Orçamento estimado:
   ├─ Defensa: R$ 2.5M
   ├─ Sinalização: R$ 0.5M
   ├─ Iluminação: R$ 3.0M
   ├─ Subtotal (curto): R$ 6.0M
   ├─ Reconstrução (médio): R$ 45.0M
   └─ TOTAL: R$ 51.0M (para 2 km)
```

### 6.2 Exemplo 2: Interseção Crítica (BR-101 RJ)

```
Dados:
├─ Interseção BR × Estadual (acesso a Angra)
├─ 8 acidentes/ano
├─ 2 com vítima fatal (colisão T)

Problema:
├─ Interseção em nível (sem defensa)
├─ Visibilidade < 50m (curva horizontal próxima)
├─ Semaforização sem sincronização com BR

RISCO: CRÍTICO (colisão T) ⚠️

Solução:
├─ Construir PARCLO A ou Diamante
├─ Raio rampa ≥ 200m
├─ Superelevação rampa 4%
├─ Iluminação completa

Cronograma:
├─ Projeto executivo: 4 meses
├─ Obra: 18 meses
├─ Custo: R$ 55-75M (PARCLO)

Ação imediata:
├─ Defensa temporária (pneu)
├─ Sinalização reforçada
├─ Redução Vd na entrada
```

---

## 7. Checklist de Segurança Geométrica

```
AUDITORIA DE SEGURANÇA GEOMÉTRICA

Alinhamento Horizontal:
□ R ≥ R_mín para Vd (DNIT ES 101/97)
□ Superelevação e ≤ 8% (10% exceção montanha)
□ Clotóide L ≥ L_mín
□ Tangente L_mín ≤ L ≤ L_máx
□ Visibilidade de parada ≥ d_mín
□ Triângulo de visibilidade verificado
□ Defensa instalada (se R < 250m)
□ Sinalização horizontal (contínua em curva)
□ Sinalização vertical 150m antes

Alinhamento Vertical:
□ Rampa i_máx ≤ permitido
□ Curva vertical em parábola
□ d_parada ≥ mínimo (tabela DNIT)
□ Iluminação (se e > 6% e R < 200m)
□ Drenagem superficial (i ≥ 0.5%)
□ Proteção de talude (altura > 5m)

Seção Transversal:
□ Largura faixa = classe rodovia
□ Acostamento conforme padrão
□ Inclinação transversal 2-3%
□ Superelevação transição OK

Interseção:
□ Tipo adequado (nível vs desnível)
□ Raios entrada ≥ mínimo
□ Triângulo visibilidade claro
□ Semaforização ou rotatória (nível)
□ Iluminação (mínimo entrada/saída)
□ Faixa pedestre (se necessário)

Segurança:
□ Defensa metálica (onde crítico)
□ Sinalização horizontal
□ Sinalização vertical (150m antes)
□ Tacha refletiva (mudança de direção)
□ Iluminação (pontos críticos)
□ Guardrail/mureta (altura > 5m)

Documentação:
□ Memorial descritivo DNIT
□ Análise de risco geométrico (AIG)
□ Projeto executivo conforme padrão
□ Aprovação DNIT (se federal)
□ Relatório de inspeção pré-obra
```

---

## 8. Referências Normativas Completas

| Norma | Assunto | Escopo |
|-------|---------|--------|
| **DNIT ES 101/97** | Projeto Geométrico | Alinhamento H, V, seção, interseção |
| **DNIT ES 131/86** | Drenagem | Banqueta, proteção talude |
| **ABNT NBR 14644** | Balizamento | Defensa, tacha, tachão |
| **ABNT NBR 15895** | Sinalização Horizontal | Faixa, contínua, tracejada |
| **ABNT NBR 5101** | Iluminação Pública | Postes, lâmpada, E mínima |
| **ABNT NBR 11682** | Estabilidade Encosta | FS, talude, drenagem |
| **ABNT NBR 6123** | Ações do Vento | Estrutura, pressão |
| **AASHTO Green Book** | Policy on Roadway Design | Padrão internacional (comparação) |
| **Resolução ANTT 1623** | Instruções Técnicas | Conformidade DNIT |

---

## 9. Integração com Agente-infraestrutura S1

### Prompts de Teste

```
1. "Qual tipo de interseção devo usar para BR × Estadual em tereno 
   ondulado, com volume 500k veículos/ano?"
   → Resposta: PARCLO A ou B (diamante não, volume alto)

2. "Uma curva tem R=200m e Vd=100 km/h. Precisa defensa?"
   → Resposta: SIM (R < 250m obrigatório conforme NBR 14644)

3. "Qual é o fator de segurança mínimo para talude com FS=1.25?"
   → Resposta: NÃO CONFORMIDADE (FS < 1.3 permanente)
   → Solução: Reduzir altura ou aumentar inclinação

4. "Tenho uma rampa em PARCLO com 300m. Qual superelevação usar?"
   → Resposta: e = 4-5% (rampa semi-direta PARCLO B)

5. "Qual é o espaçamento recomendado de defensa metálica?"
   → Resposta: 0.30m (conforme NBR 14644)
```

---

**Última atualização**: 2026-08-03  
**Prefixo RAG**: `rod:geom:intersecoes:*` | `rod:seguranca:*`  
**Status**: Pronto para consolidação no workflow
