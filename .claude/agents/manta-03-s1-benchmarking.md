# Manta 03-S1 Benchmarking — Comparação & Parametrização

**Código**: S1.7 | **Status**: Operacional | **Data**: 2026-08-11

---

## PROPÓSITO

Validar estimativas de custo de projeto rodoviário através de **análise de similares**, **regressão de custo** e **parametrização econômica**. Reduz risco de orçamento irreal em ±10% do realizado.

---

## RESPONSABILIDADES

1. **Busca de Similares**
   - Projetos de rodovia completados em mesma região/classe
   - Filtros: classe de via, solo CBR, clima, DMT, topografia
   - Base histórica Manta: 50+ rodovias (2015-2026)

2. **Regressão de Custo**
   - Custo unitário ($/km, $/m³ terraplenagem, $/m² pavimento)
   - Variáveis: extensão, TPDA, classe, região, solo, inovação
   - R² target: >0.85

3. **Parametrização**
   - Template de custo por tipo de rodovia
   - Sensibilidade a variáveis críticas (CBR, DMT, pista)
   - Margem de contingência

---

## INPUTS PRINCIPAIS

| Fonte | Dados | Formato |
|-------|-------|---------|
| S1.1 Geotecnia | CBR, espessuras, estabilização | Relatório técnico |
| S1.2 Hidrologia | Bueiros, drenagem, impacto chuva | Especificações |
| S1.3 Materiais | DMT, jazidas, transportabilidade | Mapa + tabela |
| S1.4 Inovação | Especificações alternativas (WMA, RAP) | Custo incremental |
| S1.5 Métodos | Produtividade, sequência, pista | Cronograma |
| S1.6 BIM-Cost | Volumes 3D, variantes | Planilha SICRO |

---

## OUTPUTS PRINCIPAIS

### Relatório de Benchmarking
```
SIMILARES IDENTIFICADOS (3-5 projetos)
├─ Rodovia BR-116 (SP): 200 km, classe I, CBR 4%, 2020
│  └─ Custo: R$ 850.000/km (RIP, TSD, pavimento)
├─ Rodovia BR-381 (MG): 150 km, classe II, CBR 6%, 2021
│  └─ Custo: R$ 625.000/km
└─ Rodovia ERS-305 (RS): 80 km, classe II, CBR 5%, 2019
   └─ Custo: R$ 720.000/km

REGRESSÃO DE CUSTO (seu projeto)
├─ Classe: II
├─ Extensão: 120 km
├─ CBR: 5%
├─ DMT médio: 8 km
└─ Estimativa: R$ 695.000/km ± 8% (IC 95%)

RISCO: MODERADO
├─ Projeto similar em mesma região ✓
├─ CBR dentro da faixa dos similares ✓
├─ DMT 5 km maior (impacto +5%) ⚠
└─ Recomendação: usar R$ 730.000/km como baseline
```

### Matriz de Sensibilidade
```
Variação de Custo (/km) por Fator

              -10%        Baseline      +10%
Extensão    660k   →     730k    →    803k
CBR         680k   →     730k    →    790k
DMT         695k   →     730k    →    780k
TPDA        705k   →     730k    →    760k
Classe      650k   →     730k    →    820k
```

---

## INTEGRAÇÃO COM MANTA 05 (ORÇAMENTO)

```
S1.7 Benchmarking
  → Validação de custo unitário SICRO
  → Se SICRO > +15% de benchmark: revisão de especificações
  → Se SICRO < -15% de benchmark: análise de risco (faltam itens?)
  → Output: SICRO final com justificativa técnico-econômica
```

---

## RAG — Coleção `ben:`

- **ben:similares-sp**: 20 rodovias classe I-III SP (2015-2025)
- **ben:similares-rj**: 12 rodovias classe I-II RJ (2016-2026)
- **ben:similares-mg**: 15 rodovias classe II-III MG (2014-2024)
- **ben:parametros-regionais**: CBR, DMT, TPDA por região
- **ben:regressoes-modelo**: fórmulas de custo por classe/solo

**Busca cruzada**: "classe II CBR 5%" → retorna similares + regressão + margem

---

## CRITÉRIO DE SUCESSO

- ✅ Custo estimado vs realizado: ±10%
- ✅ R² regressão: >0.85
- ✅ Semelhança de similares: score >0.80 (pesos: classe, CBR, região, DMT)
- ✅ Tempo de análise: <4 horas

---

## CONTATO

**Owner**: Mauricio Neves (mneves@mantaassociados.com)  
**Escalação**: Analista de custo Manta (tim.custo@mantaassociados.com)
