# Balanço de Massa & Movimento de Terra — Otimização de Custo de Transporte

**Data**: 2026-08-04  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:terraplenagem:*` | `rod:geom:bruckner:*`  
**Normas**: DNIT ES 101/97, Item 4 (Seção Transversal)

---

## 1. Conceito Fundamental: Balanço de Massa (Mass Balance)

### 1.1 Definição

Balanço de massa é o **estudo quantitativo de movimentos de terra** ao longo do projeto de uma rodovia, buscando:

```
Objetivo:
├─ Balancear volumes de corte (cut) com volumes de aterro (fill)
├─ Minimizar transporte de solo
├─ Reduzir custos de obra (transporte = até 40% do custo total)
├─ Otimizar a geometria do projeto

Equação Básica:
───────────────
Volume_Corte - Volume_Aterro = Empréstimo ou Bota-fora

Se Volume_Corte > Volume_Aterro → Material em excesso (bota-fora, vender)
Se Volume_Corte < Volume_Aterro → Necessário empréstimo de material
Se Volume_Corte ≈ Volume_Aterro → Projeto "balanceado" (ideal)
```

### 1.2 Fatores de Conversão (Fator de Empolamento)

Quando solo é escavado em corte, seu volume aumenta (empolamento):

```
Tipo de Solo | Densidade Natural | Fator Empolamento (FE) | Densidade Solto
─────────────────────────────────────────────────────────────────────────
Argila       | 1,600 kg/m³       | 1.30-1.40             | 2,080 kg/m³
Silte        | 1,400 kg/m³       | 1.25-1.35             | 1,750 kg/m³
Areia        | 1,500 kg/m³       | 1.10-1.20             | 1,650 kg/m³
Rocha        | 2,000 kg/m³       | 1.50-1.70             | 3,200 kg/m³

Exemplo:
Volume de corte = 100 m³ (argila)
FE = 1.35
Volume solto = 100 × 1.35 = 135 m³
→ Necessário transportar 135 m³, não 100 m³
```

### 1.3 Fator de Compactação

Ao compactar aterro, o volume se reduz:

```
Tipo de Solo | Grau de Compactação | Fator Compactação (FC)
─────────────────────────────────────────────────────────────
Ótimo        | 95-98% Proctor       | 0.85-0.90
Normal       | 90-95% Proctor       | 0.90-0.95
Reduzido     | 85-90% Proctor       | 0.95-1.00

Exemplo:
Volume de aterro solto necessário = 150 m³
Grau de compactação = 90% Proctor
FC = 0.92
Volume final compactado = 150 × 0.92 = 138 m³
```

---

## 2. Método de Brückner (Brückner's Method)

### 2.1 Histórico & Aplicação

**Criado por**: Leopold Brückner (1900s, Alemanha)  
**Aplicação**: Rodovias, ferrovias, canais  
**Princípio**: Visualizar movimento de terra ao longo do eixo da rodovia

```
Vantagem:
├─ Determinar otimamente a origem e destino de material
├─ Calcular distância média de transporte
├─ Minimizar custo de movimento de terra
├─ Identificar pontos econômicos (free haul limit)

Ferramenta:
└─ Diagrama de Brückner (curva acumulada de corte/aterro)
```

### 2.2 Construção do Diagrama de Brückner

**Passo 1: Cálculo de Seções Transversais**

Para cada estaca (a cada 20m ou 50m):
```
Entrada (estaca 0+000):
├─ Cota natural: 450.00m
├─ Cota de projeto: 450.50m
├─ Diferença: +0.50m (aterro)

├─ Largura plataforma: 12.2m
├─ Altura média seção: 0.50m
├─ Volume (prismático): 12.2 × 0.50 × 20m = 122 m³ (aterro)

Estaca 0+020:
├─ Cota natural: 451.00m
├─ Cota de projeto: 451.50m
├─ Diferença: +0.50m (aterro)
├─ Volume: 120 m³ (aterro)

Estaca 0+040 (passa de aterro para corte):
├─ Cota natural: 452.00m
├─ Cota de projeto: 451.00m
├─ Diferença: -1.00m (CORTE)
├─ Volume: 240 m³ (corte)
```

**Passo 2: Acumulação de Volumes**

```
Estaca  | Tipo      | Volume (m³) | Corte/Aterro | Volume Acumulado
────────────────────────────────────────────────────────────────────
0+000   | Aterro    | +122        | Aterro       | +122
0+020   | Aterro    | +120        | Aterro       | +242
0+040   | Corte     | -240        | Misto        | +2 (quase balança)
0+060   | Corte     | -250        | Corte        | -248
0+080   | Corte     | -260        | Corte        | -508
0+100   | Aterro    | +180        | Misto        | -328
0+120   | Aterro    | +190        | Aterro       | -138
0+140   | Aterro    | +200        | Aterro       | +62
```

**Passo 3: Plotar Diagrama de Brückner**

```
Volume Acumulado (m³)
                    
       +300 ┌─────────────────────
             │    
       +200 │     ╱────╲
             │    ╱      ╲
       +100 │───╱        ╲───────
             │  ╱          ╲    
         0  ├──────────────┬───── → Estaca
            │ 0+  20  40  60  80 100 120 140
        -100│              │╲
             │              │ ╲
        -200│              │  ╲────╱───
             │              │
        -300│              └────
             │
```

### 2.3 Interpretação do Diagrama

```
Regra de Leitura:
────────────────

1. Rampa Ascendente (↗): ATERRO (volume positivo)
2. Rampa Descendente (↘): CORTE (volume negativo)
3. Cruzamento do eixo (Y=0): Ponto de equilíbrio local

Exemplo BR-116:
├─ Estaca 0+000 a 0+020: Aterro (+242 m³)
├─ Estaca 0+020 a 0+140: Corte até -508 m³
├─ Estaca 0+140 a 0+200: Aterro restaura +62 m³
├─ Final: Volume acumulado = 0 (perfeito balanço!)
```

---

## 3. Cálculo de Distância Média de Transporte

### 3.1 Método de Brückner para Distância

A **distância média de transporte** é calculada pela área entre a curva de Brückner e a linha de compensação.

```
Fórmula:
────────
Distância Média (m) = Área do Diagrama / Volume Total Transportado

Exemplo:
├─ Área entre curva e eixo X (positiva) = 50,000 m³·m
├─ Volume total de aterro = 1,000 m³
├─ Distância Média = 50,000 / 1,000 = 50m

Interpretação:
└─ Material percorre em média 50m antes de ser depositado
```

### 3.2 Limites Econômicos (Free Haul Distance)

```
Free Haul Distance (FHD):
────────────────────────

Definição: Distância máxima que o material PODE ser transportado
           sem que seja mais econômico fazer bota-fora + empréstimo

Fórmula:
FHD = Custo de Bota-fora / (Custo de Transporte por m³ por km)

Exemplo:
├─ Custo bota-fora = R$ 50/m³
├─ Custo transporte = R$ 2.00/m³/km
├─ FHD = 50 / 2.00 = 25 km

Decisão:
└─ Se distância média > 25 km → Não compensa transportar
   └─ Fazer bota-fora local + buscar empréstimo em local mais próximo

Typical FHD valores:
├─ Rodovia rural: 20-50m
├─ Rodovia urbana: 100-200m (espaço limitado)
├─ Obra de larga escala: até 500m
```

---

## 4. Otimização de Custo de Transporte

### 4.1 Custo Total de Movimento de Terra

```
Custo Total = Custo_Escavação + Custo_Transporte + Custo_Aterro + Custo_BotaFora

Detalhamento:
─────────────

1. Escavação (Corte):
   C_escav = Volume_Corte × R$ 8.50/m³ (SICRO 03.01.01)

2. Transporte:
   C_transp = Volume × Distância_Média × R$ 2.00/m³/km

3. Aterro (Compactação):
   C_aterro = Volume_Aterro × R$ 12.00/m³ (SICRO 03.02.01)

4. Bota-fora (se material em excesso):
   C_bota = Volume_Excesso × R$ 50/m³

5. Empréstimo (se material insuficiente):
   C_emprés = Volume_Deficit × (R$ 35/m³ material + R$ 12/m³ aterro)
```

### 4.2 Exemplo Prático: BR-116 (1km)

```
DADOS:
─────
Comprimento: 1000m
Corte total: 150,000 m³
Aterro total: 100,000 m³
Empréstimo necessário: 50,000 m³ (deficit)
Distância média corte → aterro: 300m
Distância média empréstimo: 2km

CÁLCULO SICRO 2026:
───────────────────

1. Escavação de corte:
   150,000 m³ × R$ 8.50/m³ = R$ 1,275,000

2. Transporte (corte → aterro):
   100,000 m³ × 0.3 km × R$ 2.00/m³/km = R$ 60,000
   
   (Nota: 50,000 m³ vão para bota-fora, não para aterro)

3. Bota-fora (material excedente):
   50,000 m³ × R$ 50/m³ = R$ 2,500,000
   
4. Aterro compactado (100,000 m³):
   100,000 m³ × R$ 12.00/m³ = R$ 1,200,000

5. Empréstimo (50,000 m³):
   Extração: 50,000 × R$ 35/m³ = R$ 1,750,000
   Transporte: 50,000 × 2.0 km × R$ 2.00/m³/km = R$ 200,000
   Aterro: 50,000 × R$ 12.00/m³ = R$ 600,000

SUBTOTAL EMPRÉSTIMO = R$ 2,550,000

TOTAL MOVIMENTO DE TERRA = R$ 1,275,000 + R$ 60,000 + R$ 2,500,000 
                         + R$ 1,200,000 + R$ 2,550,000
                         = R$ 8,585,000

Percentual do Custo Total da Rodovia:
├─ Custo total 1km (estimado): R$ 5.2M (dos documentos anteriores)
├─ Movimento terra: R$ 8.585M (parece alto)
├─ REVISAR: Este é um caso de deficit de material!
```

### 4.3 Cenários Otimizados

**Cenário 1: Balanceamento Perfeito (ideal)**

```
Corte = Aterro = 125,000 m³ (aplicar FE)
│
├─ Escavação: 125,000 × R$ 8.50 = R$ 1,062,500
├─ Transporte (300m médio): 125,000 × 0.3 × R$ 2.00 = R$ 75,000
├─ Aterro: 125,000 × R$ 12.00 = R$ 1,500,000
│
└─ TOTAL: R$ 2,637,500

Economia vs Cenário 1: R$ 8,585,000 - R$ 2,637,500 = R$ 5,947,500 (69% redução!)
```

**Cenário 2: Aproveitamento de Empréstimo Local**

```
Se houver bota-fora autorizado PRÓXIMO (500m vs 2km):

Empréstimo local (500m):
├─ Extração: 50,000 × R$ 35 = R$ 1,750,000
├─ Transporte: 50,000 × 0.5 × R$ 2.00 = R$ 50,000
├─ Aterro: 50,000 × R$ 12.00 = R$ 600,000
└─ Subtotal: R$ 2,400,000

Economia vs cenário anterior: R$ 2,550,000 - R$ 2,400,000 = R$ 150,000
```

---

## 5. Método Alternativo: Similaridade com Linha de Compensação

### 5.1 Análise de Compensação

Além de Brückner, usa-se a **linha de compensação** para definir seções de corte-aterro:

```
Conceito:
─────────
Uma linha horizontal no diagrama de Brückner que:
1. Toca os picos do diagrama (máximos de corte)
2. Minimiza a área total (menor distância média de transporte)

Procedimento:
─────────────
1. Plotar diagrama de Brückner (acumulado)
2. Ajustar uma linha horizontal que minimize movimento
3. Trechos acima da linha = Corte
4. Trechos abaixo = Aterro
5. Calcular distância média da área entre curva e linha

Exemplo Visual:
───────────────
      + 300  ╱────╲
             │      ╲
      + 200  │       ╲
             │  ├─────┤ Linha de Compensação
      + 100  │  │     ╲
             │──┼──────╲───
        0   ├──┴───────╲──┬── eixo X
             │          ╲ │
      - 100  │           ╲│
             │            │
      - 200  │            └──╱
```

### 5.2 Múltiplas Linhas de Compensação

Para grandes trechos, usa-se **múltiplas seções de compensação**:

```
Exemplo: Rodovia com 10km de extensão

├─ Seção 1 (km 0-3): Balanceamento local
│  └─ Corte = Aterro (distância média 500m)
│
├─ Seção 2 (km 3-7): Corte principal com deficit
│  └─ Corte → Parte para aterro local
│  └─ Parte restante → bota-fora (distância 15km)
│
└─ Seção 3 (km 7-10): Aterro com empréstimo
   └─ Material local + empréstimo de bota-fora da Seção 2

Benefício:
└─ Reduz transporte de longa distância
└─ Otimiza uso de material local
```

---

## 6. Software de Cálculo: Brückner Digital

### 6.1 Integração em MX Road

```
MX Road > Earth Works > Mass Diagram:

1. Importar alinhamento H + perfil V
2. Definir seção transversal padrão
3. Gerar seções automáticas (a cada 20m)
4. Calcular volumes: Cut, Fill, Borrow, Waste
5. Plotar diagrama de Brückner automático
6. Ajustar linha de compensação (slider interativo)
7. Exportar relatório com:
   └─ Volumes totais
   └─ Distâncias médias
   └─ Custo estimado SICRO
   └─ Planilha Excel com seções
```

### 6.2 Excel/Python para Brückner Simplificado

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Dados de entrada
estacas = np.array([0, 20, 40, 60, 80, 100, 120, 140])
volumes = np.array([122, 120, -240, -250, -260, 180, 190, 200])  # m³

# Acumulação
volumes_acum = np.cumsum(volumes)

# Plotar
plt.figure(figsize=(12, 6))
plt.plot(estacas, volumes_acum, 'b-o', linewidth=2, markersize=8, label='Brückner')
plt.axhline(y=0, color='r', linestyle='--', label='Eixo X')
plt.grid(True, alpha=0.3)
plt.xlabel('Estaca (m)', fontsize=12)
plt.ylabel('Volume Acumulado (m³)', fontsize=12)
plt.title('Diagrama de Brückner - BR-116 Exemplo', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('bruckner_diagram.png', dpi=150)
plt.show()

# Cálculo de distância média (área do diagrama)
area = np.trapz(np.abs(volumes_acum), estacas)
volume_total = np.sum(np.abs(volumes[volumes < 0]))  # volume de corte
distancia_media = area / volume_total
print(f"Distância média de transporte: {distancia_media:.1f}m")
```

---

## 7. Checklist de Otimização

```
ANÁLISE DE MOVIMENTO DE TERRA:

Fase 1 — Diagnóstico:
□ Calcular volume de corte total
□ Calcular volume de aterro total
□ Identificar deficit ou superávit
□ Determinar FHD (free haul distance)

Fase 2 — Brückner:
□ Gerar diagrama de Brückner (MX Road ou manual)
□ Ajustar linha de compensação
□ Identificar pontos econômicos
□ Calcular distância média

Fase 3 — Cenários:
□ Cenário 1: Balanceamento perfeito
□ Cenário 2: Empréstimo local
□ Cenário 3: Bota-fora distante
□ Comparar custos de cada cenário

Fase 4 — Decisão:
□ Escolher cenário de menor custo
□ Especificar origem/destino de material
□ Incluir em orçamento SICRO
□ Documentar em memorial

Fase 5 — Obra:
□ Validar volumes em campo (seções topográficas)
□ Ajustar se desvios > 5%
□ Documentar origem/destino real
□ Atualizar custo final
```

---

## 8. Referências Normativas

| Norma | Assunto |
|-------|---------|
| **DNIT ES 101/97** | Seção Transversal (Item 4) |
| **DNIT IPR 702** | Avaliação de Pavimentos (drenagem relacionada) |
| **ABNT NBR 6122** | Geotecnia (compactação, aterro) |
| **SICRO DNIT** | Custos de escavação, transporte, aterro |

---

**Última atualização**: 2026-08-04  
**Prefixo RAG**: `rod:geom:terraplenagem:*` | `rod:geom:bruckner:*`  
**Status**: Pronto para integração no workflow
