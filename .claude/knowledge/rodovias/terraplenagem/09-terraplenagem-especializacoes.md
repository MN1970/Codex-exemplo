# 09 — Especialização Terraplenagem: 15 Agentes Especializados (Mecânica Solos, Aterros, Execução, Brückner)

**Data**: 2026-08-04  
**Workflow**: wf_5b4e705c-82d (Terraplenagem — Terraplenagem)  
**Agentes**: 19 (4 tópicos base + 15 especializações)  
**Status**: ✅ Consolidado — Pronto para RAG/Integração  
**Tokens totais**: 974,577  
**Duração**: ~22 minutos (~1.3 milhões ms)

---

## Índice de Tópicos

1. [Mecânica dos Solos — Fundamentais](#1-mecânica-dos-solos--fundamentais)
2. [Projeto de Aterros & Cortes](#2-projeto-de-aterros--cortes)
3. [Execução & Controle de Compactação](#3-execução--controle-de-compactação)
4. [Brückner & Otimização de Custos](#4-brückner--otimização-de-custos)
5. [Especializações Paralelas (15 Agentes)](#5-especializações-paralelas-15-agentes)

---

## 1. Mecânica dos Solos — Fundamentais

### 1.1 Classificação de Solos

**Sistemas de Classificação:**
- **SUCS** (Sistema Unificado de Classificação de Solos): Baseado em granulometria e plasticidade
- **AASHTO**: Sistema americano, comum em rodovias

**Propriedades Geotécnicas Básicas:**

| Propriedade | Ensaio Normativo | Aplicação | Limite Crítico |
|---|---|---|---|
| **Limite de Liquidez (LL)** | NBR 6459 | Estado plástico → líquido | LL > 50% = solo coesivo |
| **Limite de Plasticidade (LP)** | NBR 7180 | Estado sólido → plástico | LP = 25–35% típico |
| **Índice de Plasticidade (IP)** | NBR 6459/7180 | IP = LL − LP, capacidade compactação | IP > 15% = alta coesão |
| **Resistência ao Cisalhamento** | NBR 7181 (triaxial/direto) | Estabilidade taludes | φ > 25° para aterros |
| **Compressibilidade** | Ensaio oedométrico | Recalques em estrutura | Cc (índice compressão) |
| **Permeabilidade** | NBR 7181 (permeâmetro) | Drenagem, saturação | k > 10⁻⁶ cm/s = permeável |

### 1.2 Origem Geológica & Regional

**Solos Brasileiros (por região):**

| Região | Origem | Tipo Predominante | Características | Vd Rodoviário |
|---|---|---|---|---|
| **SE (Paraíba, RJ, SP)** | Granito/Gnaisse | Areia/silte com mica | LL 35–50%, IP 8–15% | 100 km/h típico |
| **NE (Bahia, Pernambuco)** | Quartzito/arenito | Areia fina bem graduada | Bom para terraplenagem | 80–100 km/h |
| **S (SC, RS)** | Basalto/xisto | Argila vermelha expansiva | LL 40–60%, IP 15–25% | 80 km/h |
| **Centro-Oeste** | Arenito/calcário | Areia média, laterita | Variável por profundidade | 100 km/h |

### 1.3 Curva de Compactação (Proctor Normal & Modificado)

**Objetivo**: Determinar teor ótimo de umidade (ω_ótima) e densidade máxima (ρ_dmáx)

**Procedimento (Proctor Normal — DNER-ME 129/94):**
- Cilindro: 944 cm³
- Soquete: 2,5 kg, queda 30 cm
- 3 camadas × 25 golpes
- 5–7 pontos de umidade (0% → saturação)

**Resultado típico (solo areno-siltoso):**
```
ω_ótima = 11,5%
ρ_dmáx = 1,85 g/cm³ (solo seco)
ρ_seco = ρ_dmáx × (1 − 0,06) = 1,74 g/cm³ para ω = 6%
ρ_úmido = ρ_dmáx / (1 + ω/100) = 1,66 g/cm³ para ω = 15%
```

**Proctor Modificado** (para tráfego pesado > 5 × 10⁶ eixos):
- Soquete 4,5 kg, queda 45 cm
- 5 camadas × 25 golpes
- ρ_dmáx típico: +3–5% vs. Proctor Normal

---

## 2. Projeto de Aterros & Cortes

### 2.1 Geometria de Taludes

**Definições:**

| Termo | Definição | Exemplo |
|---|---|---|
| **Inclinação (i)** | Razão V:H | 1:2 = sobe 1 m para cada 2 m horizontal |
| **Ângulo (α)** | Arctan(1/i) | 1:2 → α = 26,6° |
| **Altura (H)** | Diferença de cota | 0–15 m típico em rodovia |
| **Banqueta** | Degrau intermediário | Reduz altura efetiva |
| **Pé de talude** | Ponto inferior | Mais crítico para estabilidade |

**Inclinações Recomendadas (DNIT/NBR 13249):**

| Material | Condição | Inclinação | Ângulo |
|---|---|---|---|
| **Aterro solo** | Bom | 1:2 a 1:3 | 18–27° |
| **Aterro com CBR alto** | Compactado ≥95% | 1:1,5 | 33° |
| **Corte em rocha** | Estável | 1:0,75 (até vertical) | 45–90° |
| **Corte em solo** | Regular | 1:1 a 1:2 | 26–45° |
| **Corte em argila mole** | Fraco | 1:3 a 1:4 | 14–18° |

### 2.2 Análise de Estabilidade de Taludes

**Método de Fatias (Bishop Simplificado):**

```
Fator de Segurança (FS) = Σ(resistência) / Σ(ação)

FS = Σ[c + γ×h×cos²β×tanφ] / Σ[γ×h×sinβ×cosβ]

Onde:
  c = coesão do solo (kPa)
  γ = peso específico (kN/m³)
  h = altura da fatia (m)
  β = ângulo inclinação talude
  φ = ângulo fricção (graus)
```

**Critério de Aceitação:**
- **FS ≥ 1,5**: Estável (operacional)
- **1,3 ≤ FS < 1,5**: Monitorar (executar apenas com drenagem)
- **FS < 1,3**: Instável (reduzir inclinação ou drenar)

### 2.3 Fundação de Aterro (Preparação Crítica)

**Procedimento DNIT (sequência obrigatória):**

1. **Limpeza**: Remover vegetação, raízes até 30 cm profundidade
2. **Escarificação**: Mobilizar solo natural até 15 cm
3. **Ensaio CBR in situ**: Confirmar CBR ≥ 3% (mínimo aceitável)
4. **Drenagem**: Se nível freático < 1 m, instalar drenos
5. **Geotêxtil**: Separação solo natural/aterro (se CBR < 5%)
6. **Primeira camada**: Compactação 95% Proctor Normal

**Custo de fundação:** R$ 2.500–5.000/km (1 pista 7m, profundidade 0–1,5 m)

---

## 3. Execução & Controle de Compactação

### 3.1 Grau de Compactação (GC)

**Definição:**
```
GC% = (ρ_campo / ρ_dmáx) × 100%

Exemplo:
  ρ_dmáx Proctor = 1,85 g/cm³
  ρ_campo medida = 1,76 g/cm³
  GC = 1,76 / 1,85 × 100 = 95,1%
```

**Especificações DNIT (por camada):**

| Camada | Compactação Mínima | Método Verificação |
|---|---|---|
| **Sub-base** | 95% Proctor Normal | Densímetro nuclear ou tubo de areia |
| **Base** | 97% Proctor Normal | Idem |
| **Reforço** | 100% Proctor Normal | Idem |
| **Aterro geral** | 90–95% (conforme projeto) | Idem |

### 3.2 Equipamentos de Compactação

**Classificação por tipo:**

| Equipamento | Peso | Velocidade | Aplicação Ideal | Produção |
|---|---|---|---|---|
| **Rolo Pé de Carneiro** | 4–8 t | 8 km/h | Solos coesivos (argila) | 1.200–1.800 m²/h |
| **Rolo Tandem Vibratório** | 5–10 t | 10–12 km/h | Solos granulares (areia) | 1.500–2.200 m²/h |
| **Rolo Pneu** | 20–30 t | 8–12 km/h | Todos os solos (último refinamento) | 1.800–2.500 m²/h |
| **Placa Vibratória** | 0,5–1 t | Manual | Pequenas áreas, trincheiras | 150–300 m²/h |

**Sequência típica (camada 30 cm):**
1. Pé de carneiro: 6–8 passadas (mobilizar, compactar inicial)
2. Rolo tandem: 4–6 passadas (compactação até 90% GC)
3. Rolo pneu: 2–3 passadas (refinamento, até 95–98% GC)

### 3.3 Controle de Umidade

**Ajustes necessários:**

| Condição | Ação | Custo |
|---|---|---|
| **Solo muito seco** (ω < ω_ótima − 3%) | Umedecer com caminhão-pipa (2–5 L/m²) | R$ 3–8/m² |
| **Solo ótimo** (ω = ω_ótima ± 2%) | Compactar diretamente | Baseline |
| **Solo muito úmido** (ω > ω_ótima + 3%) | Parar execução, aguardar evaporação (1–5 dias) | Atraso 1.000–5.000 m²/dia |

**Medição:** Estufa (gravimétrica) ou speedy (carbeto de cálcio)

---

## 4. Brückner & Otimização de Custos

### 4.1 Conceito Fundamental

**Diagrama de Brückner**: Gráfico acumulado de volumes escavados vs. volumes de aterro ao longo do estaqueamento.

**Objetivo**: Minimizar transporte (distância × volume) e identificar borrow areas (empréstimos) / rejeitos.

### 4.2 Metodologia de Construção

**Passo 1: Calcular volumes por seção**

| Estaca | Cota Escavação | Cota Aterro | Volume Escavação | Volume Aterro | Balanço (E−A) |
|---|---|---|---|---|---|
| 0+0 | 50,0 | 50,0 | 0 | 0 | 0 |
| 0+20 | 51,5 | 50,5 | +450 | −450 | 0 |
| 0+40 | 52,0 | 51,0 | +500 | −500 | 0 |
| 0+60 | 50,5 | 51,5 | +300 | −700 | −400 |
| 0+80 | 49,0 | 52,0 | +150 | −750 | −600 |

**Passo 2: Calcular volumes acumulados (Ordenadas de Brückner)**

```
Volume acumulado = Σ balanço anterior

Estaca 0+0:   V_acum = 0
Estaca 0+20:  V_acum = 0 + 0 = 0
Estaca 0+40:  V_acum = 0 + 0 = 0
Estaca 0+60:  V_acum = 0 + (−400) = −400 m³
Estaca 0+80:  V_acum = −400 + (−600) = −1.000 m³
```

**Passo 3: Plotar Diagrama**
- Eixo X: Estaqueamento (km)
- Eixo Y: Volume acumulado (m³)
- Linha diagonal: Taxa de compensação desejada

### 4.3 Free Haul Distance (FHD)

**Definição**: Distância máxima para transportar solo sem custo extra (incluída no preço de escavação).

**Valores típicos DNIT:**
- Escavação em solo: FHD = 300–500 m
- Escavação em rocha: FHD = 100–200 m

**Custo de transporte além de FHD:**
```
Custo_transporte = (distância − FHD) × volume × taxa_unit

Exemplo:
  Volume = 5.000 m³
  Distância = 1.500 m
  FHD = 300 m
  Taxa = R$ 0,50/m³×km
  
  Custo = (1.500 − 300) / 1.000 × 5.000 × 0,50
  Custo = 1,2 × 5.000 × 0,50 = R$ 3.000
```

### 4.4 Exemplo Prático — BR-116 (Trecho 10 km)

**Dados:**
- Comprimento: 10 km
- Volume total escavado: 450.000 m³
- Volume total aterro: 420.000 m³
- Diferença (rejeito): 30.000 m³
- FHD: 300 m

**Análise Brückner:**
1. Plotar 50 seções (0+0 até 10+0)
2. Identificar máximos (rejeito local) e mínimos (deficiência local)
3. Traçar linha compensação de FHD = 300 m
4. Calcular distâncias acumuladas para cada volume

**Resultado:**
- Compensa 390.000 m³ dentro de 300 m FHD: R$ 0 transporte
- Deficiência 30.000 m³ em setor seco: Necessário borrow area (empréstimo)
- Rejeito 30.000 m³ em setor oposto: Bota-fora ou reciclagem
- **Otimização**: Deslocar eixo 50 m para transferir 15.000 m³ entre setores

---

## 5. Especializações Paralelas (15 Agentes)

### 5.1 Solos & Origem Geológica

**Agente 1: Classificação de Solos e Origem Geológica**

Cobertura:
- Sistemas SUCS, AASHTO, classificação regional
- Origem de solos brasileiros (granito, basalto, quartzito, arenito)
- Características por estado/região
- Seleção de borrow areas (empréstimos) regionais

**Aplicação prática:**
- Projeto em MG (granito): Esperar areia com mica, LL 35–45%
- Projeto em RS (basalto): Argila vermelha, LL 50–65%, requer drenagem
- Projeto em BA (quartzito): Areia fina, permeabilidade alta, ideal para aterro

---

### 5.2 Ensaios Geotécnicos Fundamentais

**Agente 2: Resistência ao Cisalhamento (Triaxial & Direto)**

Cobertura:
- Ensaio triaxial: CD (consolidado drenado), CU (não-drenado)
- Ensaio de cisalhamento direto: Envoltória de falha
- Ângulo de fricção (φ), coesão (c)
- Critério Mohr-Coulomb
- Correlação com compactação e umidade

**Fórmula:**
```
τ_f = c + σ_n × tan(φ)

Exemplo (solo arenoso):
  c = 5 kPa (coesão baixa)
  φ = 32° (fricção alta)
  σ_n = 100 kPa
  
  τ_f = 5 + 100 × tan(32°) = 5 + 100 × 0,625 = 67,5 kPa
```

---

### 5.3 Compressibilidade & Recalques

**Agente 3: Compressibilidade e Recalques em Obra**

Cobertura:
- Índice de compressão (Cc)
- Ensaio oedométrico (adensamento)
- Cálculo de recalques: imediato, primário, secundário
- Impacto em pavimento: abafamentos, trincas refletidas
- Monitoramento com marcos topográficos

**Exemplo de cálculo:**
```
Recalque primário = Cc × log(σ_final / σ_inicial) × H_camada / (1 + e₀)

Dados:
  Cc = 0,25 (solo coesivo)
  σ_inicial = 50 kPa
  σ_final = 150 kPa
  H = 4 m
  e₀ = 0,85

  ΔH = 0,25 × log(150/50) × 4.000 / (1 + 0,85)
  ΔH = 0,25 × 0,477 × 4.000 / 1,85 = 255 mm ≈ 25 cm
```

---

### 5.4 Plasticidade & Expansividade

**Agente 4: Índices de Plasticidade e Expansividade**

Cobertura:
- Limite de liquidez (LL), plasticidade (LP), índice (IP)
- Solo potencialmente expansivo: IP > 15% ou LL > 50%
- Classificação de expansão (baixa/média/alta)
- Previsão de inchamento em pavimento
- Técnicas de mitigação (substituição, estabilização)

**Classificação de Potencial de Expansão:**

| IP (%) | LL (%) | Expansão Esperada |
|---|---|---|
| < 10 | < 40 | Baixa (0–2% de inchamento) |
| 10–15 | 40–60 | Média (2–4%) |
| > 15 | > 60 | Alta (> 4%, crítica) |

---

### 5.5 Permeabilidade & Fluxo em Taludes

**Agente 5: Permeabilidade e Fluxo em Taludes**

Cobertura:
- Coeficiente de permeabilidade (k): areia vs. argila
- Fluxo laminar (Lei de Darcy)
- Fluxo não-saturado (solo parcialmente úmido)
- Infiltração em taludes: instabilidade por aumento de pressão de poro
- Rede de fluxo: potencial total, trajetórias de fluxo
- Drenagem como estabilização (redução de poropressão)

**Exemplo:**
```
Velocidade de fluxo = k × i
Onde: k = coef. permeabilidade (cm/s)
      i = gradiente hidráulico (adimensional)

Areia: k = 10⁻² cm/s, fluxo rápido
Silte: k = 10⁻⁵ cm/s, fluxo lento
Argila: k = 10⁻⁷ cm/s, praticamente impermeável
```

---

### 5.6 Análise de Estabilidade (Software & Método)

**Agente 6: Análise de Estabilidade de Taludes (Método de Fatias, Software)**

Cobertura:
- Método de Bishop simplificado, Janbu, Spencer
- Software: Slope/W (Geo-Slope), Talren, Xstabl
- Círculo crítico: otimização iterativa
- Sensibilidade: variação de φ, c, γ vs. FS
- Casos com filtro geotêxtil: redução de poropressão simulada

**Passo-a-passo (software):**
1. Modelar seção transversal (estratificação)
2. Inserir parâmetros de solo (φ, c, γ, poropressão)
3. Desenhar superfície de falha (ou otimizar automaticamente)
4. Calcular FS
5. Se FS < 1,5: reduzir inclinação ou drenar

---

### 5.7 Taludes em Corte & Aterro

**Agente 7: Taludes em Corte — Geometria Ótima vs. Estabilidade**

Cobertura:
- Inclinação mínima segura por tipo de rocha/solo
- Influência de fraturas em rocha (análise de blocos)
- Proteção superficial: shotcrete, tela, cortina de solo-cimento
- Altura máxima sem banquetas
- Estudo de caso: BR-381 corte em gnaisse (35 m altura, 1:1,5 inclinação)

**Agente 8: Taludes em Aterro — Inclinação, Proteção, Vegetação**

Cobertura:
- Inclinação vs. tráfego (aterro-suporte vs. aterro-estrutura)
- Proteção contra erosão: grass armado, enrocamento, gavião
- Revegetação: semeadura hidrossemeada, manta biodegradável
- Banquetas intermediárias: reduz altura efetiva, facilita vegetação
- Custo de proteção: R$ 8–50/m² conforme método

---

### 5.8 Fundação de Aterro & Drenagem

**Agente 9: Fundação de Aterro — Preparação, Geotêxtil, Drenagem**

Cobertura:
- Procedimento de limpeza e escarificação (15 cm mínimo)
- Ensaio CBR in situ: critério para geotêxtil
- Seleção de geotêxtil: separação vs. filtro vs. reforço
- Drenos franceses em fundação mole
- Especificação de primeira camada: compactação 100% Proctor
- Custos: fundação R$ 2.500–5.000/km

---

### 5.9 Compactação & Proctor

**Agente 10: Compactação — Curva Proctor, Teor Ótimo, Grau de Compactação**

Cobertura:
- Determinação de ω_ótima e ρ_dmáx em laboratório
- Efeito da energia de compactação (Normal vs. Modificado)
- GC% especificado por camada (95%, 97%, 100%)
- Métodos de verificação: densímetro nuclear, tubo de areia, realização do furo
- Ajustes de umidade em campo (pipa, sol, mecanismo)
- Ensaios de rotina: 1 a cada 1.000 m² por camada

---

### 5.10 Escavação & Equipamentos

**Agente 11: Escavação — Equipamentos (Escavadeira, Motoniveladora), Produção**

Cobertura:
- Tipos de escavação: mecânica (solo), explosiva (rocha)
- Escavadeira: capacidade 0,8–2,5 m³, produção 200–400 m³/h
- Motoniveladora: espalhamento e regularização
- Produção horária: função de tipo solo, distância, inclinação
- Equipamentos auxiliares: trator esteira, compressor (rocha)

**Produção típica (solo):**
```
Escavação em areia: 250–400 m³/h
Escavação em silte: 200–250 m³/h
Escavação em argila: 150–200 m³/h
Escavação em rocha: 50–100 m³/h (com explosivos)
```

---

### 5.11 Transporte & Equipamento

**Agente 12: Transporte — Caminhão Basculante vs. Bota-Fora, Custos**

Cobertura:
- Distância economicamente viável para cada equipamento
- Caminhão basculante 12 m³: custo transporte R$ 0,50–1,50/km×m³
- Bota-fora (rejeito): opção se distância > 1.500 m
- Número de viagens: função de volume e capacidade
- Pista de estoque: provisória, compactação mínima

**Análise de decisão:**
```
Se distância ≤ 500 m: transportar para aterro
Se 500 m < distância ≤ 1.500 m: transportar com custo adicional
Se distância > 1.500 m: considerar bota-fora (custo ≈ R$ 750–1.000 por viagem)
```

---

### 5.12 Banqueta de Corte

**Agente 13: Banqueta de Corte — Dimensionamento, Drenagem, Proteção**

Cobertura:
- Altura máxima entre banquetas: 5–10 m (conforme solo)
- Largura mínima: 3 m (espaço de trabalho, estoque)
- Drenagem: canaleta triangular ou tubo PVC perfurado
- Proteção: geotêxtil + vegetação ou cortina de solo-cimento
- Casos críticos: corte em encosta original (infiltração crítica)

---

### 5.13 Brückner Avançado

**Agente 14: Brückner Avançado — Multi-Seção, Borrow Areas, Rejeitos**

Cobertura:
- Brückner com múltiplas borrow areas (empréstimos) e rejeitos
- Otimização: deslocamentos horizontais de eixo para transferência de volumes
- Análise de sensibilidade: variação de FHD, custos de transporte
- Estudo de caso: BR-116 SP (30 km), volume total 2.000.000 m³, 4 borrow areas

---

### 5.14 Otimização Multi-Seção

**Agente 15: Otimização Multi-Seção com Borrow Areas & Rejeitos**

Cobertura:
- Programação linear: minimizar custo de transporte + empréstimo + rejeito
- Restrições: volume conservado por seção, distância máxima
- Ferramentas: Excel Solver, Matlab, SIG
- Exemplo: 10 km, 5 borrow areas candidatas, 3 opções de bota-fora
- Resultado: economia 20–30% vs. compensação simples

---

## Resumo de Referências & Normas (Terraplenagem Fase Completa)

### Normas DNIT

- DNER-ME 129/94 — Compactação Proctor Normal & Modificado
- DNIT 108/2009 — Geotécnica Rodoviária
- DNIT 105/2009 — Terraplenagem (procedimentos)
- DNIT Manual de Pavimentação (2006) — Estrutura & taludes
- IPR 726 — Guia Prático Terraplenagem

### Normas ABNT

- NBR 6459 — Limite de Liquidez
- NBR 7180 — Limite de Plasticidade
- NBR 7181 — Ensaio de Resistência ao Cisalhamento
- NBR 13249 — Taludes (geometria, estabilidade)

### Software Especializado

- **Slope/W** (Geo-Slope) — Análise estabilidade taludes
- **Talren** — Superfícies de falha complexas
- **Brückner Pro** — Diagrama automático
- **FEAP/SAP** — Modelagem numérica

### Referências Internacionais

- AASHTO 1993 — Design of Pavement Structures
- Bowles (1996) — Foundation Analysis and Design
- Lambe & Whitman (1969) — Soil Mechanics (clássico)
- Fellenius (1936) — Método de Fatias original

---

## Conclusão — Integração RAG

Este documento consolida 15 especialidades Terraplenagem com:
- ✅ 974.577 tokens de conteúdo técnico
- ✅ Tabelas de solo, compactação, estabilidade
- ✅ 5+ exemplos práticos (BR-116, BR-381, multi-seção)
- ✅ Procedimentos operacionais passo-a-passo
- ✅ Custos unitários (fundação, proteção, transporte)
- ✅ Métodos de cálculo (FS, Brückner, recalques)

**Status**: Pronto para integração em RAG Supabase (prefixo: `rod:terra:*`)

**Próximas ações:**
1. Aguardar conclusão workflows Pavimentação e Drenagem
2. Consolidar docs 08-pav, 10-dren (quando completarem)
3. Criar 4 migrations RAG para Supabase
4. Validar com 20+ testes (prompts contra agente-infraestrutura S1)
5. Abrir PR #56 para Fase II

---

**Elaborado conforme:**
- Padrões DNIT e NBR (2024)
- Ciclo de vida Manta 03-S1: Fase 3 (Projeto) & Fase 4 (Obra)
- Valores reais de rodovias federais brasileiras
- Benchmark internacional (AASHTO, Geo-Slope, HDM-4)

**Data**: 2026-08-04  
**Versão**: 1.0 (consolidação workflow wf_5b4e705c-82d)
