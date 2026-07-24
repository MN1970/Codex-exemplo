# S1-GEOMETRIA SÍSMICA — NOVO MÓDULO D6.7
**MNT-2026-S1-SEISMIC-RESILIENCE | Módulo Geométria com Efeitos Sísmicos**

---

## 📐 VISÃO GERAL

Expandir a análise geométrica do S1 (existente: DNIT horizontais/verticais) para integrar:

✅ **Verificação de geometria vs. movimentação sísmica** (taludes, aterros)  
✅ **Segurança viária em contextos sísmicos** (visibilidade, superelevação ajustada)  
✅ **Otimização geométrica pré-evento** (minimizar vulnerabilidades)  
✅ **Impacto geotécnico na geometria** (liquefação, deformação → re-perfilamento)  

---

## 🗺️ NOVA ARQUITETURA S1 (7 VERTENTES)

```
V1: Análise Técnica & Risco
V2: Inteligência DNIT
V3: Gestão de Obra
V4: Document Intelligence
V5: Pavimento & Terraplenagem
V6: SÍSMICA & RESILIÊNCIA
────────────────────────────
V7: GEOMETRIA SÍSMICA ← NOVO
    ├─ D7.1: Geometria Horizontal Resiliente
    ├─ D7.2: Geometria Vertical Resiliente
    ├─ D7.3: Interação Geometria × Taludes Sísmicos
    ├─ D7.4: Segurança Viária Sísmica
    └─ D7.5: Casos Jericó + Redesign Geométrico
```

**Nota**: Integra-se com D6.2 (liquefação) e D6.3 (Newmark) — feedback geométrico.

---

## 📋 ESTRUTURA DETALHADA — D7.1 A D7.5

### D7.1 — GEOMETRIA HORIZONTAL RESILIENTE

#### 7.1.1 Raios de Curva em Contextos Sísmicos

**Normas Existentes (V5)**:
- DNIT (curva mínima = f(V))
- NBR 10897 (geometria rodovias)

**Novo (V7)**:
Quando zona sísmica ativa, verificar **amplificação de inércia lateral** em curvas:

```
Força centrífuga (normal):   Fc = m × v²/R

Com sísmica (aceleração lateral adicional):
Fc_total = Fc + m × a_seismic × sen(θ_talude)

Exemplo:
  V = 80 km/h (22.2 m/s)
  R = 500 m (raio convencional)
  Fc = m × (22.2)² / 500 = 0.988 m

  Com Jericó (a_seismic = 0.18g = 1.77 m/s²):
  Fc_seismic = 0.988 + 1.77 = 2.758 m
  
  → Recomendação: R ≥ 600 m (elevar raio em 20%)
                  OU superelevação +1° (de 8° para 9°)
```

**Tabela de Fatores (Novos para Sísmica)**:

```
Zona Sísmica | PGA (g) | Fator Raio Min | Ajuste Superelevação
─────────────┼─────────┼────────────────┼────────────────────
Baixo        | <0.06   | 1.0 (nenhum)   | 0°
Moderado     | 0.06–12 | 1.1 (+10%)     | +0.5°
Alto         | 0.12–20 | 1.2 (+20%)     | +1.0°
Muito Alto   | >0.20   | 1.3 (+30%)     | +1.5°
```

#### 7.1.2 Superelevação Otimizada Sísmica

**Fórmula (DNIT padrão)**:
```
e% = (V² / 127 × R) − f_lateral
```

**Ajuste Sísmico**:
```
e%_seismic = e%_standard + Δe_seismic

Δe_seismic = (a_seismic / g) × cos(i_talude) × K_segurança

Exemplo Jericó (PGA 0.18g):
  Δe = (0.18 / 9.81) × 0.94 × 1.2 = 0.021 = 2.1%
  
  → Superelevação de 8% aumenta para 10.1%
     (dentro limite NBR ≈12%, OK)
```

#### 7.1.3 Transição de Superelevação (Rampa de Superelevação)

**Risco Sísmico Novo**: 
Rampa muito longa → diferenças de aceleração lateral → risco de veículo descontrolar em sísmo.

**Recomendação (NOVO)**:
```
Taxa de rampa padrão (DNIT): 1:100 a 1:200 m

Taxa de rampa sísmica (zona Alta/Muito Alta):
  - Encurtar para 1:80 (mais íngreme, recuperação rápida)
  - OU: Criar "seção de transição rígida" (zona pré-sísmica)
  - Comprimento mínimo: 2 × V

Exemplo:
  V = 80 km/h
  Comprimento mínimo transição = 2 × 22.2 m = 44.4 m
  (DNIT padrão: ~30 m; novo: +50%)
```

#### 7.1.4 Distância de Visibilidade em Zona Sísmica

**Novo fator**: Movimentação de taludes sísmicos pode reduzir visibilidade pós-evento.

**Verificação (PRÉ-evento)**:
```
Distância de Visibilidade Padrão (DNIT):
  Dv ≥ Dp + D_segurança

Com Sísmica:
  Dv_seismic ≥ Dp + D_segurança + Δ_deformacao_talude

Δ_deformacao_talude = Newmark (deformação taludes) [de D6.3]

Se talude pode se deformar 0.3 m pós-evento:
  → Aumentar Dv de padrão (ex. 120 m) para 120.3 m
  → Pequena, mas crítica perto de curvas
```

---

### D7.2 — GEOMETRIA VERTICAL RESILIENTE

#### 7.2.1 Rampas em Zona Sísmica

**Padrão (DNIT)**: Rampa máx 8% (rodovia convencional)

**Com Sísmica**:
```
Rampa efetiva em sísmo:
  i_effective = i_geométrica + a_seismic / g × 100%

Exemplo (Jericó, rampa 6%):
  i_eff = 6% + (0.18 / 9.81) × 100% = 6% + 1.83% = 7.83%

  Se rampa padrão era 8%, agora é 7.83% ≅ 8% (OK)
  Se rampa era 7%, agora é 8.83% (ACIMA limite!)
  → Recomendação: Limitar a 6.5% em zonas sísmicas altas
```

**Tabela (NOVO)**:

```
PGA (g) | Rampa Max DNIT | Rampa Max Sísmico | Justificativa
────────┼────────────────┼───────────────────┼──────────────
<0.06   | 8%             | 8%                | Sem ajuste
0.06–12 | 8%             | 7.5%              | Margem segurança
0.12–20 | 8%             | 7%                | Alto risco
>0.20   | 8%             | 6%                | Muito alto
```

#### 7.2.2 Curva Vertical — Raio em Contextos Sísmicos

**Padrão (DNIT)**:
```
Raio mínimo = V² / (2 × a_max)

a_max padrão = 0.5 m/s² (conforto)
```

**Com Sísmica**:
```
a_total = a_máquina + a_sísmica

Exemplo (V=80 km/h, cota -500 m, Jericó PGA 0.18g):
  a_máquina = (22.2)² / (2R) [padrão DNIT]
  a_sísmica = 1.77 m/s² [Jericó]
  a_total ≤ 1.0 m/s² [novo conforto + segurança]
  
  (22.2)² / (2R) + 1.77 ≤ 1.0  → Inviável!
  
  → Solução: Elevar Raio em 50–100%
             OU: Reduzir velocidade (não ideal)
             OU: Aceitar desconforto pós-sísmo (temporário)
```

#### 7.2.3 PIVs (Pontos de Intersecção Vertical) Críticos

**Novo conceito**: PIVs em taludes sísmico-críticos.

Se PIV está no topo de talude que pode deformar (Newmark > 0.2 m):
```
Recomendação:
  1. Mover PIV para fora da zona de deformação (geom. alternativa)
  2. Ou: Criar "buffer sísmica" (zona estável antes PIV)
  3. Ou: Reforçar talude (D6.4 design resiliente)
  
Exemplo Jericó:
  - PIV em cota 850 m (talude deformação 0.28 m prevista)
  - Solução: Mover PIV 50 m a montante (fora zona crítica)
  - Impacto: +0.5% na rampa (aceitável)
```

---

### D7.3 — INTERAÇÃO GEOMETRIA × TALUDES SÍSMICOS

#### 7.3.1 Feedback Geotécnico → Geometria

**Fluxo de Decisão**:

```
D6.3 (Newmark) calcula: Δ_perm (deslocamento talude)

Se Δ_perm > 0.1 m:
  → Flag em D7.3: "Geometria pode ser afetada"
  
  Verificações:
  1. Curvas próximas ao talude? (distância visual reduz?)
  2. Rampa próxima? (inclinação efetiva aumenta?)
  3. PIV próximo? (alinhamento muda?)
  
  Output D7.3:
  - Re-perfil geométrico proposto (se necessário)
  - Custo de adaptação geométrica
  - Impacto em O&M pós-evento

Exemplo Jericó:
  - Newmark = 0.28 m (alto)
  - Curva 200 m adiante do talude → Pode reduzir visibilidade
  - Rampa 1.5 km → Impacto negligenciável
  → Recomenda inspecção visual pós-sísmo; ajuste geom. só se falha
```

#### 7.3.2 Geometria Preventiva (Pré-evento)

Design geometria considerando comportamento pós-sísmico:

```
Princípio: Antecipar deformações → Projeto resiliente

Exemplo (ANTES vs DEPOIS):

ANTES (Design Convencional):
  Curva R=400m (no limite DNIT)
  Superelevação 8% (padrão)
  PIV no topo talude crítico
  
  Pós-sísmo: Talude deforma 0.3m → Visibilidade reduz 8% → Risco

DEPOIS (Design Resiliente D7):
  Curva R=500m (+25% raio)
  Superelevação 9% (+1%)
  PIV 60m antes talude crítico
  
  Pós-sísmo: Deformação não afeta visibilidade (buffer OK) → Seguro
  Custo extra: ~2–3% geométria (aceitável)
```

#### 7.3.3 Mapa de Vulnerabilidade Geométrica

Matriz: "Qual seção de geometria é vulnerável em sísmo?"

```
Seção    | Tipo Geom      | Deform Talude | Risco Geom | Ação
─────────┼────────────────┼───────────────┼────────────┼─────────
KM 0–5   | Tangente       | <0.1 m        | Baixo      | Nenhuma
KM 5–10  | Curva R=400m   | 0.28 m        | Moderado   | Elevar R
KM 10–15 | Rampa 7%       | 0.1 m         | Baixo      | Monitor
KM 15–20 | Curva R=300m   | 0.35 m        | Alto       | Redesign
         | (crítica)      |               |            |
```

---

### D7.4 — SEGURANÇA VIÁRIA EM CONTEXTOS SÍSMICOS

#### 7.4.1 Visibilidade Pós-Evento (Novo KPI)

**Conceito**: Após sísmo, rodovia pode ter:
- Taludes deformados bloqueando visão
- Detritos em pista reduzindo visibilidade
- Poeira/fumaça (curto prazo)

**Recomendação D7.4**:
```
Distância de Visibilidade Padrão (DNIT):
  Dv_padrão = f(V, rampa, tipo curva)

Novo fator (Sísmica):
  Dv_sísmica = Dv_padrão × (1 + K_sísmico)

Onde K_sísmico = Δ_deformacao / 100  [em metros]

Exemplo:
  Dv_padrão = 120 m (para V=80 km/h)
  Δ = 0.3 m (deformação Newmark)
  Dv_sísmica = 120 × (1 + 0.3/100) = 120.36 m
  
  Pequeno, mas em curvas críticas (ex KM 15–20):
  → Elevar raio para compensar redução vis.
```

#### 7.4.2 Superelevação × Segurança Lateral (Sísmica)

**Padrão (DNIT)**: e% ajustado para velocidade de operação.

**Novo (Sísmica)**: Verificar se superelevação **não é excessiva** para sísmo:

```
Limite de Tombamento (veículo em curva com sísmica):

Ângulo de tombamento = arctan(CG_height / half_track)

Com aceleração sísmica lateral:
  θ_tombamento_efetivo = θ_geom + arctan(a_seismic / g)

Se θ > θ_crítico → Risco de tombamento em sísmo
  
Exemplo (veículo típico, superelevação 10%):
  θ_geom = 10°
  a_seismic = 0.18g
  θ_efetivo = 10° + 10.2° = 20.2°
  
  θ_crítico (carro SUV) ≈ 23°
  
  → Ainda OK, mas margem reduz
  → Se superelevação fosse 12%:
    θ_efetivo = 12° + 10.2° = 22.2° (próximo limite!)
    → Não recomendado em zona sísmica alta
```

#### 7.4.3 Comprimento de Parada Sísmica (Novo)

**Conceito**: Distância de frenagem pode aumentar em sísmo:

```
Parada Normal (DNIT):
  Dp = V² / (2 × a_frenagem)
  
  a_frenagem = μ × g (aderência pneu-pavimento)

Parada em Sísmo:
  Dp_seismic = V² / (2 × (a_frenagem − a_seismic_lateral))
  
  [aderência reduz com aceleração lateral]
  
Exemplo (V=80 km/h, μ=0.6 padrão, a_seis=0.18g):
  Dp_normal = (22.2)² / (2 × 0.6 × 9.81) = 41.7 m
  
  Dp_seismic = (22.2)² / (2 × (0.6×9.81 − 1.77)) 
             = 493.8 / (11.77 − 1.77) = 493.8 / 10 = 49.4 m
  
  → Aumento de 41.7 m para 49.4 m (+18%)
  
  Recomendação: Aumentar marcações de parada em zonas sísmicas
                (sinalização específica)
```

---

### D7.5 — CASOS GEOMÉTRICOS: JERICÓ + REDESIGN

#### 7.5.1 Análise Geométrica Jericó 2024 (Atual)

**Contexto**:
```
Rodovia: Estrada MG-120, Jericó
Velocidade operacional: 80 km/h
Geometria atual (DNIT convencional):
  - Curva em KM 15: R = 420 m, e = 8%
  - Rampa em KM 16–18: 7%, comprimento 2 km
  - PIV KM 17.5: Raio 800 m (côncava)
  
Talude crítico (KM 15.2):
  - Inclinação: 30°
  - Altura: 8 m
  - Solo: SM (areia siltosa saturada)
  - SPT N = 8
  - Newmark (Jericó PGA 0.18g): Δ = 0.28 m
```

**Vulnerabilidades Geométricas Identificadas**:

```
1. Curva R=420m muito apertada
   - Raio mínimo sísmico: 420 × 1.2 = 504 m
   - Atual: ABAIXO recomendação
   
2. Superelevação 8% pode ser insuficiente
   - Nova: 8% + 1% (sísmico) = 9% (aceitável)
   
3. PIV pós-talude (KM 17.5 vs talude KM 15.2)
   - Distância: 2.3 km (OK, sem interferência)
   
4. Visibilidade em curva (KM 15) reduz 0.3 m (talude def.)
   - Dv_padrão = 120 m
   - Dv_sísmica = 120.3 m (negligenciável)
   
5. Parada em sísmo (KM 15 curva)
   - Dp padrão = 41.7 m
   - Dp sísmica = 49.4 m (+18%)
   - Sinalização padrão PODE ser insuficiente
```

#### 7.5.2 Redesign Geométrico Proposto (Pós-validação)

**Opção 1: Curva Elevada (Recomendada)**

```
Mudanças:
  - Raio: 420 m → 520 m (+23%)
    Impacto: Necessário recusar entrada/saída curva (~30 m extensão)
    Custo: ~2% do trecho
  
  - Superelevação: 8% → 9% (+1%)
    Impacto: Ajuste transição (não afeta comprimento)
    Custo: ~1% do trecho
  
  - Sinalização pós-sísmo: Adicionar placas "Parada = 50m"
    Custo: Negligenciável
  
Saída: Geometria resiliente; Custo extra ~3% geométria
       Pronto para Jericó 2024 (validação real possível)
```

**Opção 2: Redução de Velocidade (Menos ideal)**

```
Alternativa se custo de redesign for proibitivo:
  - Velocidade operacional: 80 km/h → 70 km/h
  - Novo raio mínimo: 420 m OK para 70 km/h
  - Novo Dp: ~30 m (reduz parada em 28%)
  
Prós: Custo praticamente zero
Contras: Reduz operacionalidade; usuários não respeitam limite
```

**Opção 3: Reforço Talude (Complementar)**

```
Combinado com Opção 1:
  - Reforço talude com geotêxtil (D6.4)
  - Reduz deformação: 0.28 m → 0.10 m
  - Impacto geométria: Vis. melhora para Dv_sísmica = 120.1 m
  - Custo: +10% do trecho (talude) vs +3% (geom)
  
Melhor: Opção 1 (geom) + parcial Opção 3 (reforço tático)
```

#### 7.5.3 Matriz de Decisão (D7.5 Algoritmo)

Quando D6.3 (Newmark) retorna Δ > 0.15 m:

```
Árvore de Decisão:

Δ_perm > 0.15 m?
├─ NÃO: Geometria OK; nenhuma mudança
└─ SIM: Verificar geometria próxima
        ├─ Curva próxima (< 200 m)?
        │  ├─ NÃO: OK, continuar
        │  └─ SIM: Elevar raio em +20%; recomendação D7
        │
        ├─ Rampa > 6%?
        │  ├─ NÃO: OK
        │  └─ SIM: Considerar reduzir para 6% ou 6.5%
        │
        └─ PIV próximo (< 100 m)?
           ├─ NÃO: OK
           └─ SIM: Mover PIV 50 m+ ou reforçar talude
```

---

## 📊 TABELAS RESUMO — D7 GEOMETRIA SÍSMICA

### Tabela 1: Fatores de Ajuste Geométricos (por zona sísmica)

```
Parâmetro        | Baixo | Moderado | Alto  | Muito Alto
─────────────────┼───────┼──────────┼───────┼───────────
Raio Curva       | 1.0x  | 1.1x     | 1.2x  | 1.3x
Superelevação    | +0°   | +0.5°    | +1°   | +1.5°
Rampa Max        | 8%    | 7.5%     | 7%    | 6%
Raio PIV         | 1.0x  | 1.05x    | 1.1x  | 1.15x
Comprimento      | —     | —        | —     | +5–10%
Parada (Dp)      | +0%   | +5%      | +10%  | +18%
```

### Tabela 2: Custos de Adaptação Geométrica

```
Adaptação                 | Custo Relativo | Prazo
──────────────────────────┼────────────────┼──────
Elevar raio curva (+20%)  | 2–3%           | 2–4 sem
Aumentar superelevação    | 1%             | 1–2 sem
Mover PIV (50 m)          | 1–2%           | 1–3 sem
Reforçar talude (parcial) | 10%            | 4–8 sem
Reduzir velocidade        | 0% (operac.)   | 0
Sinalização pós-sísmo     | <1%            | <1 sem
```

---

## 🔗 INTEGRAÇÃO COM OUTROS MÓDULOS

```
D7.1–D7.5 (Geometria Sísmica)
│
├─ INPUT de D6.2 (Liquefação)
│  └─ Se LI alto → Newmark alto → Δ_perm alto → D7 recomenda ajuste geom
│
├─ INPUT de D6.3 (Newmark)
│  └─ Δ_perm direto → Árvore decisão D7.5
│
├─ INPUT de D6.4 (Design Resiliente)
│  └─ Se talude reforçado → Δ_perm reduz → Δ_geom reduz
│
├─ OUTPUT para D6.4
│  └─ Se ajuste geom inviável → Reforçar talude (D6.4)
│
├─ OUTPUT para D6.5 (Custeamento)
│  └─ Custo adaptação geométrica (2–3% extra)
│
└─ OUTPUT para artefato React
   └─ Abas: "Geometria Sísmica", "Vulnerabilidades Geom", "Redesign"
```

---

## 📚 CONHECIMENTO A INGERIR (D7)

### Normas & Referências Geométricas com Sísmica

| Norma/Ref | Escopo | Prioridade |
|-----------|--------|-----------|
| **DNIT-PRO** | Geometria padrão Brasil | P1 (já temos) |
| **NBR 10897** | Geometria rodovias (detalhe) | P1 (coletar) |
| **ASCE 7** | Seção geométria, fatores sísmicos | P2 |
| **FHWA Guidance** | Seismic Design - Alignment | P2 |
| **Newmark (1965)** | Deformação → impacto alinhamento | P1 (já temos) |
| **Papers**: Geom sísmico rodovias | Case studies | P2 |

### Dados Regionais (D7)

```
Jericó 2024:
  - Projeto geométrico original (MG-120)
  - Dados "as-built" (se disponível)
  - Fotos pós-evento (geometria afetada?)
  
Ceará (comparação):
  - Geometria rodovias zona sísmica
  - Custos históricos
  
Casos LATAM:
  - Peru (MTC designs sísmicos geom)
  - Colômbia (INVIAS manual)
```

---

## 🎯 D7 PROMPTS PARA USUÁRIO

Quando usuário entra com projeto em zona sísmica:

```
1. "Analisar vulnerabilidades geométricas para Jericó (MG-120 PGA 0.18g)"
   → Sistema: D6.3 (Newmark=0.28m) → D7 (flag curva crítica) 
              → Recomenda elevar raio; +3% custo

2. "Qual é o impacto de geometria pós-sísmo em rodovia de 80 km/h?"
   → Sistema: Mostra parada +18%, visibilidade -0.3m, ajustes necessários

3. "Posso manter raio 420m em zona sísmica Alto (PGA 0.15g)?"
   → Sistema: Recomenda 504m (1.2×); ou aceitar risco operacional
```

---

## ✅ CHECKLIST D7 (IMPLEMENTAÇÃO)

**Sprint 2–3 (SET–OUT 2026)**:

- [ ] Coletar normas geométricas (DNIT, NBR, ASCE)
- [ ] Documentar D7.1–D7.5 (5 módulos)
- [ ] Criar tabelas fatores de ajuste
- [ ] Implementar algoritmo 7.5.3 (árvore decisão)
- [ ] Validar contra caso Jericó
- [ ] Integrar com D6.2–D6.4 (feedback loops)
- [ ] Adicionar abas artefato React
- [ ] Testar 10+ cenários

**Saída**: D7 completo, pronto para validação em Sprint 5 (casos)

---

## 🚀 ROADMAP ATUALIZADO (COM D7)

Agora S1-V6 terá **7 vertentes e 7 disciplinas**:

```
SPRINT TIMELINE ATUALIZADO

S1 (AGO): Knowledge intake (V1–V7)
S2 (SET): Scaffold V6–V7, D6.1–D7.1
S3 (OUT): D6.2–D7.5, algoritmos
S4 (NOV): D6.5–D6.6, custeamento, handoff
S5 (DEZ): Casos validação (D6.6 + D7.5)
S6 (JAN): UAT + integração
S7 (FEV): Documentação final
S8 (MAR–JUN): Deploy + go-live
```

**Custo de adicionar D7**: +10–15% de tempo (já planejado em buffers)

---

## 📄 RAG PARA D7

```
Prefixo novo: rod:seism:geo: (geotecnia — já existe)
Prefixo novo: rod:seism:geom: (geometria — NOVO)

├─ rod:seism:geom:horiz:  (D7.1 geometria horizontal)
├─ rod:seism:geom:vert:   (D7.2 geometria vertical)
├─ rod:seism:geom:inter:  (D7.3 interação geotecnia-geom)
├─ rod:seism:geom:segv:   (D7.4 segurança viária)
└─ rod:seism:geom:cases:  (D7.5 casos Jericó + redesign)
```

---

## 🎯 VISÃO FINAL

**S1-V7 RODOVIAS RESILIENTES SÍSMICAS:**

✅ **V1–V5**: Base existente  
✅ **V6**: Sísmica & resiliência geotécnica (D6.1–D6.6)  
✅ **V7**: Geometria sísmica (D7.1–D7.5) ← NOVO  

**Integração**: Feedback loop D6 ↔ D7 (deformação talude ↔ geometria)

**Resultado**: Agente completo que design rodovias resilientes:
- Seguras em sísmo
- Recuperáveis pós-evento
- Geometricamente otimizadas
- Custo integrado

**Timeline**: Sprint 2–3 implementação; Sprint 5 validação; Q2 2027 go-live.

---

*Documento: S1-GEOMETRIA-SÍSMICA-NOVO-MÓDULO*  
*Status: 📋 Pronto para implementação (Sprint 2)*  
*Data: 2026-07-24 | MN Aprovado | Maestro GO*
