# Manta 03-S1-BENCHMARK — Histórico de Custos & Parametrização (Rodovias)

**Versão:** 1.0 | **Data:** 2026-08-11 | **Status:** 🆕 Operacional

Módulo de benchmarking histórico para estimativa paramétrica de custos em rodovias brasileiras. Integra banco de dados de projetos 2015–2026, análise de variância, regressão de custos e ajuste regional via SICRO.

---

## 1. COMPETÊNCIAS CORE

### 1.1 Banco de Dados Histórico
- **Acervo:** Mínimo 50 rodovias licenciadas/concluídas (2015–2026)
- **Campos:** Custos realizado vs orçado, desvios %, duração, atrasos, fatores externos (chuva, mudanças, contingências)
- **Normalização:** Valores em R$/km, R$/m³ escavação, R$/ton pavimentação (base ano 2026)
- **Rastreabilidade:** Link para editais BNDES, TCU, propostas técnicas

### 1.2 Parametrização por Tipo de Terreno
| Terreno | Descrição | Fator custo | Produtividade excav. |
|---------|-----------|-------------|---------------------|
| Plano | -5% a +5% elevação, solos granulares | 1.0× | 800–1200 m³/dia |
| Montanhoso | +5% a +20% elevação, rocha, escavação | 1.25–1.40× | 300–600 m³/dia |
| Semi-árido | Terrenos lateríticos, pouca água | 0.95× (material) | 600–900 m³/dia |
| Amazônico | Altos índices pluviométricos, dispersão, sazonalidade | 1.30–1.50× (logística) | 200–400 m³/dia |

### 1.3 Índices de Produtividade
- **Escavação em rocha:** 300–500 m³/dia (com desmonte)
- **Escavação em solo:** 600–1200 m³/dia
- **Pavimentação CBUQ:** 600–1000 ton/dia
- **Aterro e compactação:** 1500–2500 m³/dia
- **Serviços de drenagem:** 2–5 km/dia (canaleta/bueiro)

### 1.4 Comparação com Similares
- Busca por: classe (BR-XXX, SP-XX), região, época (margem ±5 anos), terreno equivalente
- Desvio máximo aceitável: ±20% (se >20%, escalar para análise de causa)
- Output: matriz de 3–5 rodovias mais próximas + custo mediano/desvio padrão

### 1.5 Análise de Variância
**Decomposição de desvios** (Realizado vs Orçado):
- ΔCusto unitário (SICRO, mercado, compras)
- ΔVolume de trabalho (retrabalho, mudanças de escopo)
- ΔProdutividade (chuva, turnover, aprendizado)
- ΔCustos indiretos (canteiro, administração)

**Saída:** Gráfico de Pareto (80/20) + recomendações para próximos projetos

### 1.6 Regressão de Custos Paramétrica
**Modelo base:** Y = a + b₁×L + b₂×T + b₃×A + ε

Onde:
- Y = Custo total (R$ milhões)
- L = Comprimento (km)
- T = Fator terreno (1.0, 1.25, 1.40, 1.50)
- A = Afastamento de centro urbano (binária: 0=próximo, 1=distante)

**Calibração:** Mínimo 20 projetos similares; R² ≥ 0.75

### 1.7 Ajuste SICRO por Região
- Base: SICRO mensal oficial (DNIT)
- Índices adicionais: desoneração estadual, logística local (frete rodoviário), sazonalidade
- Aplicação: multiplicador ao custo paramétrico base
- Vigência: reavaliação trimestral

### 1.8 Fatores de Risco Históricos
- **Atraso cronológico:** Média +22% em rodovias federais (TCU 2015–2025)
- **Retrabalho:** +8% em terrenos montanhosos (NBR 13133)
- **Mudanças de escopo:** +5–15% (depende de fase: projeto básico vs executivo)
- **Contingência climática:** +10–20% em Amazônia/Sul (junho–outubro)

---

## 2. IMPACTO EM CUSTOS

| Aplicação | Ganho esperado | Exemplo |
|-----------|----------------|---------|
| Estimativa preliminar vs benchmark | ±10–15% acurácia | Custo projetado R$ 500M → realizado R$ 485M (intervalo 425–575M) |
| Parametrização por terreno | Antecipa desafios | Montanha → pré-aloca +30% em escavação/contenção |
| Transparência com empreiteiro | Negociação 8–12% melhor | Concorrência equitativa; reduz litígio |
| Lições aprendidas | -5% no projeto seguinte | Evita mesmas contingências |

---

## 3. INTAKE QUESTÕES

**Trigger no Maestro:** Se usuário mencionar qualquer uma:
- "custo similar", "benchmark", "comparação", "rodovia parecida"
- "estimar parametricamente", "quanto deve custar"
- "desvio orçado", "por que custou mais", "análise de variância"
- "terreno similar", "montanhoso", "semi-árido", "risco de custo"

→ **Ação:** Redirecionar para Manta 03-S1-BENCHMARK (ativar via manta-06 ou manta-05)

---

## 4. INTEGRAÇÃO COM OUTROS AGENTES

| Agente | Fluxo | Input | Output |
|--------|-------|-------|--------|
| **Manta 05 (Orçamento)** | Validação de BDI, contingências | Estimativa preliminar | Intervalo confiável, desvios esperados |
| **Manta 06 (Modelagem)** | Simulação de risco (Monte Carlo) | Variância histórica, fatores | Curva P10–P90, distribuição de custos |
| **Manta 13 (Business Dev)** | Análise de oportunidade em licitação | Preço base, mercado | Margem recomendada, probabilidade sucesso |

---

## 5. FONTES RAG & COLEÇÃO SUPABASE

| Fonte | Prefixo | Exemplo | Status |
|-------|---------|---------|--------|
| Banco interno Manta | **rod:** | `rod:proj-2024-br116-sp`, `rod:proj-2021-sp225-serra` | ✅ 45+ projetos indexados |
| Editais BNDES (propostas) | **rod-edital:** | Orçamentos divulgados, custo base | ⚡ Parcial (ultrasecretaria) |
| Publicações TCU/STN | **rod-tcu:** | Relatórios de auditoria, desvios | ✅ 50+ acórdãos 2018–2026 |
| SICRO históricos | **rod-sicro:** | Séries mensais 2015–2026 | ✅ Atualizado mensalmente |
| Estudos mercado (CNI, FIPE) | **rod-market:** | Índices econômicos, logística, combustível | ✅ Trimestral |

---

## 6. ROADMAP DE IMPLEMENTAÇÃO

| Trimestre | Milestone | Responsável | Status |
|-----------|-----------|-------------|--------|
| **Q3 2026** | Setup banco histórico (50+ projetos), análise de desvios iniciais | Manta 03-S1 team | 🔄 Em progresso |
| **Q4 2026** | Modelos de regressão calibrados (L × T → custo), validação R² | Data science | 🔲 Planejado |
| **Q1 2027** | Parametrização por região (SICRO ajustado, fatores logística) | Manta 05 + S1 | 🔲 Planejado |
| **Q2 2027** | Dashboard de benchmarking (busca automática similares, alerta >20% variância) | Plataforma | 🔲 Planejado |

---

## 7. ESTRUTURA DE DADOS (Schema)

```yaml
Projeto:
  id: "rod-proj-2024-br116-sp"
  nome: "BR-116 Contorno SP — Pavimentação"
  data_conclusao: 2024-06-15
  estado: "SP"
  classificacao: "BR-XXX (federal)" | "SP-XX (estadual)"
  
  Geometria:
    comprimento_km: 42.5
    tipo_terreno: "montanhoso"      # plano | montanhoso | semi-árido | amazônico
    elevacao_media_m: 620
    curvatura_media: 8.2             # graus por km
    
  Custos:
    valor_orcado_r_mi: 285.0
    valor_realizado_r_mi: 312.5
    variancia_pct: +9.6
    custo_unitario_r_km: 7.35        # (realizado / comprimento)
    sicro_base: "SICRO-202406"
    
  Cronograma:
    duracao_planejada_meses: 36
    duracao_realizada_meses: 42
    atraso_dias: 180
    
  Fatores_Externos:
    dias_chuva_perdidos: 45
    mudancas_escopo: true            # retrabalho adicional
    contingencias_acionadas: 3        # número de eventos
    
  Referencia_RAG:
    fonte_custo: "rod-edital:2022-licit-001"
    nota_auditoria: "rod-tcu:2025-acordo-3421"
```

**Exemplo de entrada (usuário):**
```
"Estou estimando uma rodovia estadual de 35 km no interior de MG, 
 terreno montanhoso com curvas. Tenho orçamento preliminar de R$ 200M. 
 É viável?"
```

**Saída esperada (Manta 03-S1-BENCHMARK):**
```
Similares encontrados (3 rodovias):
  1. SP-225 Serra (2019): 38 km, montanhoso → R$ 7.8M/km = R$ 296M total
  2. MG-010 Araxá (2020): 32 km, montanhoso → R$ 7.2M/km = R$ 230M total
  3. RJ-116 Petrópolis (2018): 41 km, montanhoso → R$ 8.1M/km = R$ 332M total

Estimativa paramétrica (regressão):
  Custo esperado: R$ 240–260M (intervalo 90%)
  Seu orçamento: R$ 200M → ALERTA: -15% vs benchmark

Recomendação: Escalonar para análise de risco (Manta 06) ou revisar escopo.
```

---

## CONTATO & SUPORTE

- **Curador:** Manta 03-S1 Infrastructure Agent
- **Escalação:** Manta 16 (Arquiteto-IA) para validação metodológica
- **Feedback:** MN (Mauricio Neves) para decisões de priorização
