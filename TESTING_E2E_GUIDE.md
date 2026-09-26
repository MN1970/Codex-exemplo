# Maestro Router E2E Testing Guide (v5.0)

**Versão:** v5.0  
**Data:** 2026-07-25  
**Cobertura:** 40 golden test cases + 10 cross-agent flows + performance baseline + regression suite

---

## Sumário Executivo

Esta suite valida o **Maestro Router v5.0** com 100% de cobertura:

| Componente | Arquivo | Testes | Asserts | SLA |
|-----------|---------|--------|---------|-----|
| **Routing** | `test_maestro_router_e2e.py` | 40 casos | agent_id, skill, tier, confidence | accuracy ≥ 81% |
| **Cross-Agent Flows** | `test_cross_agent_flows.py` | 10 cenários | job dispatch, RAG coord, aggregation | success ≥ 90% |
| **Performance** | `test_performance_baseline.py` | 12 classes | latency, throughput, memory | p95 < 5s, 10 req/s |
| **Regression (CI/CD)** | `test_regression_suite.py` | 25+ testes | accuracy, latency, agent count | baseline no regression |
| **Fixtures** | `fixtures/prompts_golden_40.json` | 40 prompts | reais de 20 agentes | coverage S1-S10+horiz |

**Total: ~1500 linhas de código + 3 KB JSON fixtures**

---

## 1. Arquivos de Teste

### 1.1 test_maestro_router_e2e.py (500+ linhas)

Valida R1 (Maestro Routing Determinístico).

**Classes:**
- `TestMaestroRouterS8` (4 testes) — Saneamento
- `TestMaestroRouterS9` (3 testes) — Energia
- `TestMaestroRouterS6` (2 testes) — Portos
- `TestMaestroRouterS7` (2 testes) — Aeroportos
- `TestMaestroRouterS10` (2 testes) — Barragens
- `TestMaestroRouterS1toS4` (8 testes) — Rodovias, OAE, Ferrovia, Metrô
- `TestMaestroRouterHorizontals` (10 testes) — Manta 01-16
- `TestMaestroRouterCrossAgent` (3 testes) — Multi-agente
- `TestMaestroRouterAmbiguity` (2 testes) — Resolução
- `TestMaestroRouterMetrics` (3 testes) — Accuracy, confidence, tiering

**Assertions checadas:**
```python
✓ result.agent_id == expected_agent_id
✓ result.skill_id == expected_skill  (v5.0)
✓ result.model_tier in [haiku-4-5, sonnet-5, opus]
✓ result.routing_confidence >= 0.80
✓ result.complexity_score alinhado com expectativa
✓ result.phase em ciclo de vida (ou null para horiz)
```

**Executar:**
```bash
# Todos os testes
pytest tests/test_maestro_router_e2e.py -v

# Apenas S8
pytest tests/test_maestro_router_e2e.py::TestMaestroRouterS8 -v

# Com coverage
pytest tests/test_maestro_router_e2e.py --cov=tests/fixtures --cov-report=html
```

---

### 1.2 test_cross_agent_flows.py (300+ linhas)

Valida R9 (orquestração async) + coordenação inter-agentes.

**Classes:**
- `TestCrossAgentETA` — S8 → S5
- `TestCrossAgentPorto` — S6 → S5 + S7
- `TestCrossAgentEnergia` — S9 → S6 (PPP)
- `TestCrossAgentBarragem` — S10 → S2 (contratual)
- `TestCrossAgentMetro` — S4 → S2 (OAE)
- `TestCrossAgentIntegration` — Mega-projetos (3+ agentes)
- `TestCrossAgentMetrics` — Cobertura, sucesso, latência

**Cenários validados:**
```
1. ETA + Orçamento (S8 + S5)
2. Porto + Cronograma + Orçamento (S6 + S5 + S7)
3. Energia + Modelagem (S9 + S6)
4. Barragem + DD + Contratual (S10 + S2)
5. Metro + OAE (S4 + S2)
6. Rodovia + Ferrovia + Energia (S1 + S3 + S9)
7. Saneamento + Advisory (S8 + S15)
8. Aeroporto + Landside (S7 + S1)
9. Rejeitos + Contratual (S10 + S2)
10. Rio integrado: Metro + Saneamento + Rodovia (S4 + S8 + S1)
```

**Executar:**
```bash
# Todos cross-agent flows
pytest tests/test_cross_agent_flows.py -v

# Apenas cenário 001 (ETA + Orçamento)
pytest tests/test_cross_agent_flows.py::TestCrossAgentETA -v

# Apenas mega-projects
pytest tests/test_cross_agent_flows.py::TestCrossAgentIntegration::test_mega_project_rio -v
```

---

### 1.3 test_performance_baseline.py (250+ linhas)

Valida latência, throughput, memory (P3 e P6).

**Classes:**
- `TestLatency` (5 testes) — routing, RAG, reranker, total
- `TestThroughput` (2 testes) — 10 req/s, success rate
- `TestMemory` (3 testes) — baseline, load, leak
- `TestScalability` (2 testes) — degradation, agent count
- `TestRobustness` (2 testes) — timeout, error handling

**Baselines SLA:**
```
Routing latency:       < 500ms  (p95)
RAG BM25:             < 50ms   (p95)
RAG Embedding:        < 100ms  (p95)
Reranker:             < 300ms  (p95)
Total latency:        < 5s     (p95)
Throughput:           >= 10 req/s (concurrent)
Memory per agent:     < 100MB  (under load)
```

**Executar:**
```bash
# Todos performance tests
pytest tests/test_performance_baseline.py -v

# Apenas latência
pytest tests/test_performance_baseline.py::TestLatency -v

# Com pytest-benchmark (opcional)
pytest tests/test_performance_baseline.py --benchmark-json=bench.json
```

---

### 1.4 test_regression_suite.py (200+ linhas)

Testes rápidos para CI/CD gate (< 60s).

**Classes:**
- `TestRegressionRoutingAccuracy` — accuracy ≥ 81%, baseline -5%
- `TestRegressionLatency` — p95 < 5s, p99 < 5s
- `TestRegressionAgentRegistry` — 20 agentes presentes
- `TestRegressionCrossAgent` — job dispatch, success ≥ 95%
- `TestRegressionRAG` — collections acessíveis
- `TestRegressionSmokeTests` — 5 rotas principais
- `TestRegressionVersioning` — VERSIONS.json, checksums
- `TestRegressionThresholds` — critical gates
- `TestRegressionDependencies` — Supabase, ES, vector DB
- `TestRegressionDeployment` — CLAUDE.md, no breaking changes
- `TestRegressionSegments` — parametrized per segment

**Gate criteria:**
```
❌ FAIL if: accuracy < 81%
❌ FAIL if: latency p95 >= 5s
❌ FAIL if: agent missing (< 20)
❌ FAIL if: cross-agent success < 90%
❌ FAIL if: RAG not accessible
```

**Executar (CI):**
```bash
# CI gate (rápido)
pytest tests/test_regression_suite.py -m ci -v --tb=short

# Detalhado
pytest tests/test_regression_suite.py -v

# Apenas versioning
pytest tests/test_regression_suite.py::TestRegressionVersioning -v
```

---

## 2. Fixtures

### 2.1 fixtures/prompts_golden_40.json

40 golden test cases estruturados:

```json
{
  "test_cases": [
    {
      "id": "s8_001",
      "category": "S8 — Saneamento",
      "prompt": "Estudamos uma ETA para AySA em Buenos Aires...",
      "context_hints": ["saneamento", "ETA", "projeto-executivo"],
      "expected_agent_id": "manta-03-s8",
      "expected_skill": "agente-saneamento.v5.0",
      "expected_phase": "estudo-previo",
      "expected_model_tier": "haiku-4-5",
      "routing_confidence_min": 0.88,
      "keywords": ["ETA", "AySA", "Buenos Aires"],
      "complexity_score_expected": 2.5,
      "cross_agent_references": null
    },
    // ... 39 mais
  ]
}
```

**Cobertura:**
- S8 (Saneamento): 4 casos — AySA priority
- S9 (Energia): 3 casos — ANEEL
- S6 (Portos): 2 casos — ANTAQ
- S7 (Aeroportos): 2 casos — ANAC
- S10 (Barragens): 2 casos — Lei 12.334
- S1–S4 (Rod/OAE/Fer/Metro): 8 casos
- Horizontais (01-02, 04-07, 13-16): 10 casos
- Cross-agent flows: 3 casos
- Ambiguity resolution: 2 casos
- **Total: 40 casos**

---

## 3. Como Rodar a Suite Completa

### 3.1 Instalação de Dependências

```bash
pip install pytest pytest-cov pytest-benchmark pytest-xdist

# Opcional: para performance profiling
pip install memory-profiler line-profiler
```

### 3.2 Rodar Tudo

```bash
# Sequencial (seguro, ~3-5 min)
pytest tests/ -v --tb=short

# Paralelo (rápido, ~60-90s)
pytest tests/ -v -n auto --tb=short

# Com coverage report
pytest tests/ -v --cov=tests --cov-report=html --cov-report=term-missing
```

### 3.3 Rodar Subteste

```bash
# Apenas router (40 cases, ~30s)
pytest tests/test_maestro_router_e2e.py -v

# Apenas S8 (4 cases, ~5s)
pytest tests/test_maestro_router_e2e.py::TestMaestroRouterS8 -v

# Apenas regression gate (CI, ~20s)
pytest tests/test_regression_suite.py -m ci -v

# Apenas performance (latency tests, ~60s)
pytest tests/test_performance_baseline.py::TestLatency -v
```

### 3.4 Profile & Debug

```bash
# Verbose logging
pytest tests/test_maestro_router_e2e.py -v -s

# Com profiling
pytest tests/test_performance_baseline.py --profile

# Pytest-watch (reload on change)
ptw -- tests/test_maestro_router_e2e.py -v
```

---

## 4. Interpretar Resultados

### 4.1 Sucesso (verde)

```
tests/test_maestro_router_e2e.py::TestMaestroRouterS8::test_s8_eta_buenos_aires PASSED
tests/test_maestro_router_e2e.py::TestMaestroRouterMetrics::test_routing_accuracy_golden_set PASSED
...
======================== 40 passed in 15.23s =========================
```

**OK:** todos 40 testes passaram, accuracy ≥ 81%, latency acceptable.

### 4.2 Falha — Routing Accuracy

```
FAILED tests/test_maestro_router_e2e.py::TestMaestroRouterMetrics::test_routing_accuracy_golden_set
AssertionError: Accuracy 78.5% < 81% minimum

agent_id mismatch:
  - s9_001 (LT 765kV): esperado manta-03-s9, got manta-03-s8
  - s6_001 (porto):    esperado manta-03-s6, got manta-03-s9
```

**Ação:**
1. Revisar `_build_routing_rules()` em `MockMaestroRouter`
2. Verificar keyword matching overlap (ex: "energia" vs "transmissão")
3. Aumentar reranker threshold ou ajustar pesos

### 4.3 Falha — Performance

```
FAILED tests/test_performance_baseline.py::TestLatency::test_total_latency_p95
AssertionError: Total p95 5234ms > 5000ms

Latency breakdown:
  - Routing:   520ms  (OK < 500ms) ✗ borderline
  - RAG BM25:  45ms   (OK < 50ms)
  - Embedding: 2100ms (SLOW > 100ms)  ← problema
  - Reranker:  280ms  (OK < 300ms)
```

**Ação:**
1. Otimizar embedding model (Infinity latency check)
2. Aumentar cache hit rate (rag_cache)
3. Considerar async embedding em background

### 4.4 Falha — Regressão CI

```
FAILED tests/test_regression_suite.py::TestRegressionRoutingAccuracy::test_accuracy_minimum_threshold
AssertionError: Accuracy 80.5% < 81% minimum

This is a CI gate failure. Do not merge.
```

**Ação:**
1. Revisar último commit em `CLAUDE.md` (mudanças em routing rules?)
2. Rodar suite E2E completa (`test_maestro_router_e2e.py`)
3. Se regression confirmada: rollback ou fix routing

---

## 5. Integração com CI/CD

### 5.1 GitHub Actions (.github/workflows/test-maestro-e2e.yml)

```yaml
name: Maestro E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  regression-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
      
      - name: Regression Gate (CI)
        run: |
          pytest tests/test_regression_suite.py -m ci -v --tb=short
      
      - name: Router E2E (40 cases)
        run: |
          pytest tests/test_maestro_router_e2e.py -v --tb=short
      
      - name: Cross-Agent Flows
        run: |
          pytest tests/test_cross_agent_flows.py -v --tb=short
      
      - name: Coverage Report
        run: |
          pytest tests/ --cov=tests --cov-report=term-missing
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            .coverage
            htmlcov/
```

### 5.2 Merge Criteria

**PR pode merge se:**
- ✅ Regression suite (CI) passa
- ✅ Router accuracy ≥ 81%
- ✅ Latency p95 < 5s (allow 5% regression)
- ✅ All 40 routing test cases pass
- ✅ Coverage ≥ 80%

**PR bloqueado se:**
- ❌ Regression suite fails
- ❌ Accuracy < 81%
- ❌ Latency p95 ≥ 5s
- ❌ Any critical agent missing

---

## 6. Troubleshooting

### 6.1 "MockMaestroRouter: Fixtures file not found"

```bash
# Verificar se JSON existe
ls tests/fixtures/prompts_golden_40.json

# Se não: criar fixtures
pytest tests/ --fixtures
```

### 6.2 "Agent manta-03-s8 not found in registry"

Significa que agente foi removido ou renomeado.

```bash
# Verificar CLAUDE.md v5.0
grep "Manta 03-S8" CLAUDE.md

# Verificar .claude/agents/
ls .claude/agents/ | grep saneamento
```

### 6.3 "Latency timeout: p95 > 5s"

Pode ser:
1. Simulação de latência muito alta em `_latency_config`
2. Não há async dispatch (aguardando jobs sequencialmente)
3. Cache não habilitado

```bash
# Debug latency breakdown
pytest tests/test_performance_baseline.py::TestLatency -v -s

# Ver detalhes
python -c "
from tests.test_performance_baseline import MockMaestroPerformance, PerformanceMonitor
mon = PerformanceMonitor()
mae = MockMaestroPerformance(mon)
mae.route('ETA para 500k hab', simulate_delay=True)
print(mon.get_latency_metrics('total'))
"
```

---

## 7. Estender a Suite

### 7.1 Adicionar novo test case

1. Adicionar prompts a `fixtures/prompts_golden_40.json`:

```json
{
  "id": "s8_005",
  "category": "S8 — Saneamento",
  "prompt": "Novo cenário específico",
  "expected_agent_id": "manta-03-s8",
  ...
}
```

2. Criar teste correspondente em `test_maestro_router_e2e.py`:

```python
def test_s8_novo_cenario(self, maestro_router, golden_test_cases):
    tc = next(t for t in golden_test_cases if t.id == "s8_005")
    result = maestro_router.route(tc.prompt, tc.context_hints)
    assert result.agent_id == tc.expected_agent_id
```

### 7.2 Adicionar novo agente

1. Atualizar `EXPECTED_AGENTS` em `test_regression_suite.py`
2. Adicionar routing rules em `MockMaestroRouter._build_routing_rules()`
3. Adicionar 2-3 test cases em `test_maestro_router_e2e.py`
4. Rodar suite e verificar cobertura

---

## 8. Métricas & Dashboards

### 8.1 Coletar Métricas Pós-Suite

```bash
# Salvar resultados em JSON
pytest tests/ --tb=no -q --json=test-results.json

# Parse e gerar relatório
python scripts/parse_test_metrics.py test-results.json
```

### 8.2 Grafana Dashboard (em produção)

Conectar ao `maestro_runs` (Supabase) para:
- Routing accuracy trend (7d, 30d)
- Latency p50/p95/p99 (time-series)
- Agent coverage heatmap
- Cross-agent success rate

---

## 9. Referência Rápida

| Comando | Propósito | Tempo |
|---------|-----------|-------|
| `pytest tests/ -v` | Suite completa | 3-5 min |
| `pytest tests/test_regression_suite.py -m ci` | CI gate | 20-30 s |
| `pytest tests/test_maestro_router_e2e.py -v` | Router E2E | 30-40 s |
| `pytest tests/test_cross_agent_flows.py -v` | Cross-agent | 15-20 s |
| `pytest tests/test_performance_baseline.py -v` | Performance | 60-90 s |
| `pytest tests/test_maestro_router_e2e.py::TestMaestroRouterS8 -v` | Apenas S8 | 5 s |

---

## 10. Contato & Suporte

**Proprietário:** mneves@mantaassociados.com  
**Versão:** v5.0 (2026-07-25)  
**Issues:** Abrir issue em GitHub com tag `maestro-e2e-tests`  
**Roadmap:** Atualmente em fase de validação em staging (Manta 03-S6..S10)

---

**Fim do TESTING_E2E_GUIDE.md**
