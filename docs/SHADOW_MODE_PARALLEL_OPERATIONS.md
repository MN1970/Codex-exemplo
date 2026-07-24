# CAG Shadow Mode — Parallel Operations Guide

## Overview

**Parallel Shadow Mode** distributes log processing, analysis, and deployment across multiple workers and environments simultaneously for maximum throughput and minimal latency.

---

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│  Maestro Router (entrypoint)                            │
│  ├─ RAG Handler (sync)           ──→ User Response      │
│  └─ CAG Orchestrator (async)                            │
│     ├─ Intent Classifier                                │
│     ├─ Agent Selector                                   │
│     └─ Response Ranker                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
            ┌────────────────────────┐
            │  Shadow Results Buffer │ (100-item batches)
            └────────────────────────┘
                         ↓
      ┌──────────────────┬──────────────────┐
      ↓                  ↓
┌─────────────┐  ┌──────────────────┐
│ Log Flusher │  │  Analysis Engine │
│ (Threads)   │  │  (Processes)     │
│ 8 workers   │  │  4 workers       │
└─────────────┘  └──────────────────┘
      ↓                  ↓
[Supabase]         [Metrics/Trends]
[shadow_logs]      [Daily Stats]
```

### Processing Model

| Component | Type | Workers | Latency | Purpose |
|-----------|------|---------|---------|---------|
| **Log Flusher** | Thread Pool (I/O-bound) | 8 (default) | 5-10ms per batch | Writes to Supabase |
| **Analyzer** | Process Pool (CPU-bound) | 4 (default) | 10-50ms per batch | Computes metrics |
| **Aggregator** | Process Pool (CPU-bound) | 4 (default) | 20-100ms per batch | Daily rollups |

---

## 📊 Parallel Log Processing

### ShadowModeLogProcessor

Distributes batch processing across thread and process pools.

```python
from cag.shadow_mode.parallel_processor import ShadowModeLogProcessor

processor = ShadowModeLogProcessor(
    num_thread_workers=8,     # I/O workers for Supabase writes
    num_process_workers=4,    # CPU workers for analysis
    batch_size=100,           # logs per batch
    debug=False
)

# Process 1,000 shadow results in parallel
output = await processor.process_batch_async(
    shadow_results=results_list,
    operation='flush'  # or 'analyze', 'aggregate'
)

# Returns:
# {
#   'operation': 'flush',
#   'total_items': 1000,
#   'batches': 10,
#   'processed': 1000,
#   'duration_ms': 45.3,
#   'results': [...]
# }
```

### Operations

#### 1. Flush (Write to Supabase)

```python
output = await processor.process_batch_async(results, 'flush')
# Distributes across 8 I/O threads
# Each batch: 5-10ms (parallel)
# 1000 items: ~50ms total (vs 500ms sequential)
```

#### 2. Analyze (Compute Metrics)

```python
output = await processor.process_batch_async(results, 'analyze')
# Distributes across 4 CPU processes
# Computes: agent_match_rate, latency percentiles, error_rate
# Each batch: 10-50ms (parallel)
```

#### 3. Aggregate (Daily Rollup)

```python
output = await processor.process_batch_async(results, 'aggregate')
# Distributes across 4 CPU processes
# Creates daily_stats entries
# Each batch: 20-100ms (parallel)
```

### Batch Size Tuning

| Batch Size | I/O Time | CPU Time | Parallelism | Recommendation |
|-----------|----------|----------|-------------|-----------------|
| 10        | 1-2ms    | 2-5ms    | High        | Development |
| 50        | 3-5ms    | 5-15ms   | Medium      | Staging |
| 100       | 5-10ms   | 10-50ms  | Medium      | Production |
| 500       | 25-50ms  | 50-200ms | Low         | Data backfill |

**Default: 100 (optimal for production latency + throughput)**

---

## 🔍 Parallel Analysis

### ParallelAnalysisEngine

Analyzes shadow results across multiple dimensions simultaneously.

```python
from cag.shadow_mode.parallel_processor import ParallelAnalysisEngine

engine = ParallelAnalysisEngine(num_workers=4, debug=False)

# Analyze across all dimensions in parallel
output = await engine.analyze_parallel(
    shadow_results=results_list,
    analysis_dimensions=['accuracy', 'latency', 'errors', 'trends', 'agents']
)

# Returns: {accuracy, latency, errors, trends, agents, summary}
```

### Analysis Dimensions

#### 1. Accuracy

```python
output['accuracy'] = {
    'agent_match_rate': 0.882,      # % CAG primary = RAG primary
    'total_queries': 18734
}
```

#### 2. Latency

```python
output['latency'] = {
    'rag_p50_ms': 1234,
    'rag_p95_ms': 2400,
    'rag_p99_ms': 3100,
    'cag_p50_ms': 1280,
    'cag_p95_ms': 2500,
    'cag_p99_ms': 3200
}
```

#### 3. Errors

```python
output['errors'] = {
    'error_count': 10,              # Total errors
    'error_rate': 0.000533          # % of queries
}
```

#### 4. Trends

```python
output['trends'] = {
    'daily_trend': {
        '2026-07-22': {'queries': 500, 'match_rate': 0.88},
        '2026-07-23': {'queries': 650, 'match_rate': 0.89},
        ...
    }
}
```

#### 5. Agents

```python
output['agents'] = {
    'agents': {
        'agente-saneamento': {
            'total_queries': 9000,
            'match_rate': 0.91
        },
        'agente-energia': {
            'total_queries': 8000,
            'match_rate': 0.85
        },
        ...
    }
}
```

### Performance

Parallel analysis speeds up by factor of N (number of workers):

| Dimension Count | Sequential | Parallel (4 workers) | Speedup |
|-----------------|-----------|----------------------|---------|
| 1 | 500ms | 500ms | 1.0x |
| 2 | 1000ms | 600ms | 1.7x |
| 5 | 2500ms | 800ms | 3.1x |

---

## 🚀 Parallel Deployment

### Multi-Environment Deployment

Deploy shadow mode to **staging → canary → production** in parallel.

```yaml
# .claude/shadow_mode/parallel_deployment.yaml

environments:
  staging:
    workers: 2
    regions: [us-east-1]
  canary:
    workers: 2
    regions: [eu-west-1]
  production:
    workers: 8
    regions: [us-east-1, eu-west-1]

parallel_jobs:
  deploy_code: [staging, production, canary]
  apply_migrations: [staging, production, canary]
  setup_monitoring: [staging, production, canary]
  test_all_environments: [staging, production, canary]
  enable_shadow_mode: [staging, production, canary]
```

### Deployment Flow (Parallel)

```
┌─────────────────┐
│  Code Ready     │
└────────┬────────┘
         │
    ┌────┴────┬────────┬─────────┐
    ↓         ↓        ↓         ↓
 [Deploy]  [Deploy]  [Deploy]  [Deploy]
 Staging   Canary    Prod1     Prod2
    │         │        │         │
    ├────┬────┼────┬───┼────┬────┤
    ↓    ↓    ↓    ↓   ↓    ↓    ↓
 [Apply Migrations] (parallel, 3 envs)
 [Setup Monitoring] (parallel, 3 envs)
 [Run Tests]        (parallel, 3 envs)
 [Enable Feature]   (parallel, 3 envs)
    │    │    │    │   │    │    │
    └────┴────┴────┴───┴────┴────┘
         All Ready
```

### CI/CD Pipeline (Parallel)

10 jobs run in parallel:

1. **Test Matrix** (Python 3.10/3.11/3.12) — 3 parallel
2. **Lint Parallel** (Pylint/Black/mypy) — 3 parallel
3. **Validate Migrations** — 1 job
4. **Build Docker** — 1 job (multi-arch)
5. **Validate Docs** — 2 parallel
6. **Integration Tests** (staging/canary/prod) — 3 parallel
7. **Benchmarking** — 1 job
8. **Coverage Report** — 1 job
9. **Deploy Staging** — 1 job
10. **Status Report** — 1 job (final)

**Total CI duration: ~5-10 minutes (vs 30+ sequential)**

---

## 📈 Scaling Guidelines

### For High-Volume Shadow Mode (100K+ queries/day)

**Recommended Configuration:**

```python
processor = ShadowModeLogProcessor(
    num_thread_workers=16,     # ↑ More I/O parallelism
    num_process_workers=8,     # ↑ More CPU parallelism
    batch_size=250,            # ↑ Larger batches
    debug=False
)

engine = ParallelAnalysisEngine(
    num_workers=8,             # ↑ More analysis workers
    debug=False
)
```

### Resource Requirements

| Queries/day | Thread Workers | Process Workers | Memory | CPU |
|------------|-----------------|-----------------|--------|-----|
| 10K        | 2 | 1 | 512MB | 0.5 |
| 100K       | 8 | 4 | 2GB | 2 |
| 1M         | 16 | 8 | 4GB | 4 |

---

## 🔧 Usage Examples

### Example 1: Daily Batch Processing

```python
import asyncio
from cag.shadow_mode.parallel_processor import ShadowModeLogProcessor

async def daily_batch_process():
    processor = ShadowModeLogProcessor(
        num_thread_workers=8,
        num_process_workers=4,
        batch_size=100
    )

    # Fetch all logs from previous day
    results = supabase.query(
        "SELECT * FROM cag_shadow_logs WHERE date(timestamp) = CURRENT_DATE - 1"
    )

    # Process in parallel: flush old data, analyze new metrics
    flush_task = processor.process_batch_async(results, 'flush')
    analyze_task = processor.process_batch_async(results, 'analyze')

    flush_output, analyze_output = await asyncio.gather(flush_task, analyze_task)

    print(f"Flushed {flush_output['processed']} logs")
    print(f"Analyzed in {analyze_output['duration_ms']:.1f}ms")

    processor.shutdown()

asyncio.run(daily_batch_process())
```

### Example 2: Real-Time Analysis

```python
async def realtime_analysis():
    engine = ParallelAnalysisEngine(num_workers=4)

    # Stream results every 5 minutes
    while True:
        results = await get_last_n_results(500)

        analysis = await engine.analyze_parallel(results)

        # Check GO criteria
        if (analysis['accuracy']['agent_match_rate'] >= 0.85 and
            analysis['latency']['cag_p95_ms'] <= analysis['latency']['rag_p95_ms'] * 1.10):
            print("✅ GO criteria met!")
        else:
            print("⚠️ Monitoring needed")

        await asyncio.sleep(300)  # 5 min

asyncio.run(realtime_analysis())
```

### Example 3: Parallel Multi-Environment Deploy

```bash
#!/bin/bash

# Deploy to staging, canary, prod in parallel
(deploy_to staging) &
(deploy_to canary) &
(deploy_to production) &

wait
echo "✅ All environments deployed"
```

---

## 📊 Monitoring Parallel Operations

### Metrics to Track

```python
# Log processor throughput
shadow_logs_processed_per_sec = processed_count / duration_sec

# Analysis latency
analysis_dimension_latency_ms = {
    'accuracy': 50,
    'latency': 80,
    'errors': 30,
    'trends': 200,
    'agents': 120
}

# Worker pool utilization
thread_pool_active = active_thread_count / total_thread_workers
process_pool_active = active_process_count / total_process_workers
```

### Performance Targets

| Operation | Target | Alert > |
|-----------|--------|---------|
| Flush 100 logs | 10ms | 50ms |
| Analyze 100 logs | 30ms | 100ms |
| Full analysis (5 dims) | 200ms | 500ms |
| Deploy all envs | 5 min | 15 min |

---

## 🛠️ Troubleshooting

### Issue: Slow Flush Performance

```
Symptom: Flushing 100 logs takes >50ms
Cause: Thread pool contention or Supabase latency spike
Fix:
  1. Increase num_thread_workers (4 → 8 → 16)
  2. Check Supabase performance metrics
  3. Reduce batch_size (100 → 50) for faster individual batches
```

### Issue: CPU Spike During Analysis

```
Symptom: 100% CPU utilization, analysis hangs
Cause: Process pool overwhelmed by large batches
Fix:
  1. Reduce batch_size (100 → 50)
  2. Increase num_process_workers (4 → 8)
  3. Stagger analysis requests (don't start all at once)
```

### Issue: Memory Leak in Long-Running Processor

```
Symptom: Memory grows over 30 days
Cause: Results not being garbage collected
Fix:
  1. Call processor.shutdown() when done
  2. Clear results_buffer periodically
  3. Limit total batch queue depth
```

---

## 📚 References

- **Implementation**: `cag/shadow_mode/parallel_processor.py`
- **Tests**: `cag/tests/test_parallel_processor.py`
- **Deployment**: `cag/shadow_mode/parallel_deployment.yaml`
- **CI/CD**: `.github/workflows/cag_shadow_mode_parallel.yml`
