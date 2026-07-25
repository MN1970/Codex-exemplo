# Sprint 2 Test Suite — Quick Start Guide

**Versão:** 1.0  
**Data:** 2026-07-25  
**Deliverable:** 30+ casos E2E + 10 exemplos detalhados  

---

## 📋 Sumário Executivo

### O que foi entregue

| Item | Quantidade | Status |
|------|-----------|--------|
| **Casos de teste** | 31 | ✅ Completo |
| **Exemplos detalhados** | 10 | ✅ Completo |
| **Fixtures GeoJSON** | 5 tipos | ✅ Completo |
| **Perfis SPT** | 5 variações | ✅ Completo |
| **Cenários PGA** | 5 casos | ✅ Completo |
| **Cobertura D6.1–D7.5** | 100% | ✅ Completo |

### Arquivos entregues

```
scratchpad/
├── SPRINT2_TEST_SUITE.md          # Documento completo (estrutura, casos, exemplos)
├── conftest.py                    # Fixtures pytest (dados, helpers)
├── test_examples_e2e.py           # 10 exemplos detalhados (pytest)
├── fixtures_geojson_spt.json      # Dados JSON (GeoJSON, SPT, PGA)
├── TEST_SUITE_QUICK_START.md      # Este arquivo
└── setup.fixtures.js              # Fixtures Jest (JavaScript)
```

---

## 🚀 Quick Start — Como rodar os testes

### Opção 1: Pytest (Python)

#### Setup inicial

```bash
# Clonar/navegar para repositório
cd /home/user/Codex-exemplo

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install pytest pytest-cov pytest-xdist pytest-benchmark

# (Opcional) Instalar mock frameworks
pip install pytest-mock responses
```

#### Rodar testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas E2E
pytest tests/e2e/test_examples_e2e.py -v

# Happy path
pytest tests/e2e/test_examples_e2e.py::TestExample1HappyPathJerico -v

# Edge cases
pytest tests/e2e/test_examples_e2e.py -k "edge_case" -v

# PGA extremo
pytest tests/e2e/test_examples_e2e.py::TestExample2PGAExtreme30000 -v

# Geometry constraints
pytest tests/e2e/test_examples_e2e.py -m geometry_constraint -v

# Com coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Performance (benchmark)
pytest tests/e2e/test_examples_e2e.py::TestExample10Performance -v --benchmark-only

# Verbose com timing
pytest tests/e2e/test_examples_e2e.py -v --tb=short --durations=10
```

#### Arquitetura pytest esperada

```
tests/
├── conftest.py                     # Fixtures compartilhadas ← USE ESTE
├── e2e/
│   └── test_examples_e2e.py        # 10 exemplos (mock implementations) ← USE ESTE
├── fixtures/
│   └── fixtures_geojson_spt.json   # Dados JSON ← USE ESTE
└── unit/
    ├── test_geotecnia.py
    ├── test_geometry.py
    └── test_constraints.py
```

### Opção 2: Jest (JavaScript)

#### Setup inicial

```bash
npm install --save-dev jest @testing-library/react

# (Opcional) TypeScript
npm install --save-dev ts-jest @types/jest
```

#### Rodar testes

```bash
# Todos os testes
npm test

# Apenas E2E
npm test -- e2e

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage

# Specific test
npm test -- test_happy_path_jerico
```

---

## 📊 Matriz de Cobertura — 31 Casos Teste

### Grupo 1: Happy Path (3 casos)

| ID | Descrição | Fixture | Status |
|----|-----------|---------|--------|
| HP-1 | Jericó nominal | `happy_path_jerico` | ✅ |
| HP-2 | Jericó + PGA moderado | `happy_path_jerico` | ✅ |
| HP-3 | Baseline nominal | `happy_path_jerico` | ✅ |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample1HappyPathJerico -v
```

### Grupo 2: SPT Outliers (5 casos)

| ID | Descrição | Fixture | Expected |
|----|-----------|---------|----------|
| SPT-1 | SPT = 0 (muito mole) | `spt_very_soft_soil` | Profundidade 4.5–7m |
| SPT-2 | SPT = 100 (rocha) | `spt_very_hard_soil` | Rockhammer, refusal |
| SPT-3 | Distribuição uniforme | `spt_uniform_distribution` | Comportamento linear |
| SPT-4 | Distribuição bimodal | `spt_bimodal_distribution` | Detecção layer intermediária |
| SPT-5 | Linear (0→16) | `spt_nominal_jerico` | Padrão esperado |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample3SPTZeroVerysoft -v
pytest tests/e2e/test_examples_e2e.py::TestExample4SPTHard100 -v
```

### Grupo 3: PGA Extremo (4 casos)

| ID | PGA (cm/s²) | Reduction Factor | Status |
|----|-------------|------------------|--------|
| PGA-1 | 0 | 1.00 | ✅ |
| PGA-2 | 150 | 1.00 | ✅ |
| PGA-3 | 3000 | 0.85 | ✅ |
| PGA-4 | 30000 | 0.65 | ✅ **Edge case** |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample2PGAExtreme30000 -v
pytest tests/e2e/test_examples_e2e.py::TestExample2PGAExtreme30000::test_pga_reduction_curve -v
```

### Grupo 4: Geometria Narrow (6 casos)

| ID | Descrição | Dimensões | Status |
|----|-----------|-----------|--------|
| GEO-1 | Lote estreito | 8m × 25m | ✅ |
| GEO-2 | L-shape irregular | 20×10 + 10×20 | ✅ |
| GEO-3 | Quadrado pequeno | 10m × 10m | ✅ |
| GEO-4 | Sliver | 30m × 0.5m | ✅ **Edge case** |
| GEO-5 | Polígono inválido | Auto-intersectante | ⚠️ Erro gracioso |
| GEO-6 | Altura mínima | 8m × 8m | ✅ |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample5NarrowGeometry -v
pytest tests/e2e/test_examples_e2e.py::TestExample6IrregularLotLShape -v
pytest tests/e2e/test_examples_e2e.py -m geometry_constraint -v
```

### Grupo 5: Constraints Solver (4 casos)

| ID | Cenário | Tipo de Conflito | Resolução |
|----|---------|------------------|-----------|
| CST-1 | Espaçamento mínimo (2m) | Conflito spacing | Reduzir piles |
| CST-2 | Lote 10×10 + min_spacing 3m | Overcrowding | Trade-off |
| CST-3 | Alinhamento colinear | Colinearity | Tolerância 0.2m |
| CST-4 | Infactível | Impossível → Falha | Erro + mensagem clara |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample7ConstraintSpacingConflict -v
```

### Grupo 6–7: Integração D6.1–D7.5 (5 casos)

| Deliverable | Descrição | Teste |
|------------|-----------|-------|
| **D6.1** | SPT → Estacas | Ex. 1, 3, 4 |
| **D6.2** | Estacas + PGA → Capacidade | Ex. 2 |
| **D6.3** | Capacidade + Constraints → Layout | Ex. 5–7 |
| **D7.1** | Layout → Otimização | Ex. 5–6 |
| **D7.3** | Layout → CAD/DXF | Included in Ex. 8 |
| **D7.4** | Layout → Relatório | Included in Ex. 8 |
| **D7.5** | v2 → v1 Compatibility | Ex. 8 |

### Grupo 8: Regressão v2 ↔ v1 (3 casos)

| ID | Cenário | Tolerância | Status |
|----|---------|-----------|--------|
| REG-1 | Output equivalência | < 10% diferença | ✅ |
| REG-2 | Diferenças toleradas | ≤ 5% | ✅ |
| REG-3 | Breaking changes | Log warnings | ⚠️ Apenas v2 features |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample8RegressionV2V1 -v
```

### Grupo 9: Patológicos (1 caso + 3 testes)

| ID | Entrada | Esperado | Status |
|----|---------|----------|--------|
| PATH-1 | `None` | `ValueError` | ✅ |
| PATH-2 | `{}` | `ValueError` | ✅ |
| PATH-3 | `{'spt_profile': []}` | `ValueError` | ✅ |
| PATH-4 | Tipo errado | `TypeError` | ✅ |

**Como rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample9PathologicalCases -v
```

---

## 🔍 10 Exemplos Detalhados

### Ex. 1: Happy Path — Jericó Nominal ✅

**Descri ção:**
```
Caso base: Jericó, SPT nominal, PGA=150 cm/s²
D6.1: SPT → recomendação helical, depth=3m, capacity=450 kN
D6.2: PGA=150 → redução 0% (nominal)
D6.3: Layout 4 piles, espaçamento 2m, feasible
D7.3: CAD com 3 layers (PILES, BOUNDARY, DIMENSIONS)
D7.4: Relatório completo
D7.5: v1 compatible
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample1HappyPathJerico::test_jerico_spt_to_piles -v
```

**Expected output:**
```
pile_type = 'helical'
depth_m = 3.0
bearing_capacity_kN = 450
feasible = True
```

---

### Ex. 2: PGA Extremo 30.000 cm/s² ⚠️ EDGE CASE

**Descrição:**
```
Caso severo: PGA = 30.000 cm/s² (sismo extremo, M8.5, d=5km)
D6.2: Redução dinâmica 35% (factor=0.65)
Dynamic capacity = 97 kN/pile (vs. 150 kN nominal)
Safety factor = 0.85 (abaixo de 1.3, requer mitigação)
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample2PGAExtreme30000 -v
```

**Parametrização:**
```
PGA=0 → factor=1.00
PGA=150 → factor=1.00
PGA=500 → factor=0.95
PGA=3000 → factor=0.85
PGA=30000 → factor=0.65  ← THIS
```

---

### Ex. 3: SPT = 0 (Solo Muito Mole) ⚠️ EDGE CASE

**Descrição:**
```
Soil stratification: argila mole SPT=0–3 (até 6m profundidade)
D6.1: Risco detectado = 'very_low_bearing_capacity'
Recomendação: Depth ≥ 4.5m, Capacity ≤ 45 kN
Aciona flag de risco para inspeção manual
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample3SPTZeroVerysoft -v
```

**Assertions:**
```
depth_m >= 4.5
bearing_capacity_kN <= 45
risk_flag == 'very_low_bearing_capacity'
min_spt == 0
```

---

### Ex. 4: SPT = 100 (Rocha/Muito Rígido) ⚠️ EDGE CASE

**Descrição:**
```
Solo muito rígido: rocha com SPT=100 (refusal esperado)
D6.1: Type = 'rockhammer', Depth = 2.0m, Capacity = 400+ kN
Refusal esperado → Engineering decision required
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample4SPTHard100 -v
```

**Assertions:**
```
pile_type == 'rockhammer'
depth_m <= 2.0
bearing_capacity_kN > 400
refusal_expected == True
```

---

### Ex. 5: Lote Estreito 8m × 25m ⚠️ GEOMETRY CONSTRAINT

**Descrição:**
```
Constraints: min_spacing=2m, setback=1.5m
Available width = 8 − 2(1.5) = 5m → max 2 columns
D6.3: Solver reduz para 2 colunas, 4 piles total
Validação: Nenhuma pile viola boundary
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample5NarrowGeometry -v
```

**Assertions:**
```
num_piles <= 6
piles_per_row <= 2  # max 2 columns
feasible == True
boundary_violations == 0
```

---

### Ex. 6: Lote em L (Irregular) ⚠️ GEOMETRY CONSTRAINT

**Descrição:**
```
Polígono em forma de L: 20×10 + 10×10 recortado
D7.1: Solver trata com recortes inteligentes
Validação: Point-in-polygon para cada pile
Total ~8 piles, respeitando L-shape
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample6IrregularLotLShape -v
```

**Assertions:**
```
All piles inside boundary (point_in_polygon)
boundary_violations == 0
feasible == True
```

---

### Ex. 7: Conflito de Espaçamento (Solver) 🔧 CONSTRAINT RESOLUTION

**Descrição:**
```
Cenário: Lote 10×10, min_spacing=3m, max_piles=3
Análise: Impossível colocar > 2 piles com spacing 3m
D6.3: Solver resolve → 2 piles (trade-off) OU aceita spacing=2.9m (tolerância)
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample7ConstraintSpacingConflict -v
```

**Assertions:**
```
num_piles <= 3
min_spacing >= 2.9m  (3m − 0.1m tolerance)
feasible == True
```

---

### Ex. 8: Regressão v2 ↔ v1 Compatibility 📊 REGRESSION

**Descrição:**
```
v1 baseline: Jericó, 4 piles, 600 kN total capacity
v2 output: Mesmo input
Validação: |v2_capacity − v1_capacity| / v1_capacity < 10%
Conversão v2 → v1.2 format
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample8RegressionV2V1 -v
```

**Assertions:**
```
v1_output.version == 'v1.2'
capacity_diff_pct < 10
'piles' in v1_output
'metadata' in v1_output
```

---

### Ex. 9: Patológicos (Entrada Vazia) ⚠️ ERROR HANDLING

**Descrição:**
```
Testa tratamento gracioso de inputs inválidos:
- None
- {} (vazio)
- spt_profile = []
- spt_profile = None
Esperado: ValueError/TypeError com mensagem clara
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample9PathologicalCases -v
```

**Parametrização:**
```python
@pytest.mark.parametrize("invalid_input,expected_error", [
    (None, ValueError),
    ({}, ValueError),
    ({'spt_profile': []}, ValueError),
    ({'spt_profile': None}, ValueError),
])
```

---

### Ex. 10: Performance — 1000 Piles 🚀 BENCHMARK

**Descrição:**
```
Stress test: Solver com 1000 piles em lote grande
D7.1: Deve completar em < 30 segundos
Throughput: ~ 33 piles/segundo
Memory: < 500 MB
```

**Rodar:**
```bash
pytest tests/e2e/test_examples_e2e.py::TestExample10Performance -v
```

**Assertions:**
```
elapsed < 30.0s
num_piles > 0
feasible == True
throughput ~ 33 piles/s
```

---

## 📈 Coverage Report

### Por Deliverable

| D | Casos | % | Status |
|---|-------|---|--------|
| D6.1 | 8 | 26% | ✅ |
| D6.2 | 5 | 16% | ✅ |
| D6.3 | 8 | 26% | ✅ |
| D7.1 | 3 | 10% | ✅ |
| D7.3 | 1 | 3% | ✅ |
| D7.4 | 1 | 3% | ✅ |
| D7.5 | 3 | 10% | ✅ |
| **Total** | **31** | **100%** | ✅ |

### Por Categoria

| Categoria | Casos | % |
|-----------|-------|---|
| Happy Path | 3 | 10% |
| Edge Cases | 10 | 32% |
| Constraints | 4 | 13% |
| Integration | 8 | 26% |
| Regression | 3 | 10% |
| Performance | 1 | 3% |
| Pathological | 2 | 6% |

---

## 🛠️ Setup para Integração CI/CD

### GitHub Actions

```yaml
name: Sprint 2 Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov pytest-xdist
      - name: Run tests
        run: |
          pytest tests/e2e/ -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitLab CI

```yaml
test:
  image: python:3.11
  script:
    - pip install pytest pytest-cov
    - pytest tests/ --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## 📚 Referências e Documentação

1. **SPRINT2_TEST_SUITE.md** — Especificação completa (este repo)
2. **conftest.py** — Fixtures pytest
3. **test_examples_e2e.py** — 10 exemplos implementados
4. **fixtures_geojson_spt.json** — Dados de teste
5. **D6.1–D7.5 Design Specs** — Requisitos (fora deste escopo)

---

## ✅ Checklist de Implementação

- [x] Estrutura test suite definida (pytest + Jest)
- [x] 31 casos teste especificados
- [x] 10 exemplos detalhados implementados
- [x] Fixtures GeoJSON criados
- [x] Perfis SPT variados
- [x] Casos PGA (0, 150, 500, 3000, 30000)
- [x] Geometrias (narrow, irregular, sliver)
- [x] Constraints solver tests
- [x] Regressão v2 ↔ v1
- [x] Pathological case handling
- [x] Performance benchmarks
- [x] Documentação completa
- [x] Fixtures fixtures_geojson_spt.json
- [x] Setup CI/CD guidance
- [ ] Deploy em ambiente CI (fora deste escopo)

---

## 🎯 Próximos Passos

1. **Integrar com codebase real:**
   - Colocar `conftest.py` em `tests/`
   - Colocar `test_examples_e2e.py` em `tests/e2e/`
   - Adaptar mocks para implementações reais

2. **Rodar suite completa:**
   ```bash
   pytest tests/e2e/ -v --cov=src --html=report.html
   ```

3. **Coletar baseline v1:**
   - Guardar saídas v1 em `fixtures/v1_baseline_outputs.json`
   - Usar para regressão v2

4. **Adicionar mais casos conforme necessário**

---

**Status:** ✅ ENTREGUE  
**Autor:** Test Automation Framework (Sprint 2)  
**Data:** 2026-07-25  
**Versão:** 1.0
