# Guia de Integração — Orquestrador Inteligente Manta Maestro v4.3

Como integrar o sistema de orquestração inteligente ao seu pipeline Manta existente.

---

## 🚀 Instalação Rápida

### 1. Copiar arquivos

```bash
# Copiar pasta orchestration/ para seu projeto
cp -r orchestration/ /seu/projeto/manta/

# Instalar dependências (nenhuma adicional necessária, usa anthropic SDK)
```

### 2. Importar no seu código

```python
from orchestration import (
    MantaOrchestrator,
    AgentTask,
    AgentType,
    SharedCacheManager,
    MaestroRouter,
    BatchDetector,
    MetricsCollector,
)
```

---

## 📋 Integração por Componente

### A. Integrar Paralelismo Cross-Agente

**Antes (sequencial):**
```python
# Seu código atual
s8_result = agente_saneamento(docs1)
s9_result = agente_energia(docs2)
s6_result = agente_portos(docs3)
# Total: 30s (sequencial)
```

**Depois (paralelo com orquestrador):**
```python
from orchestration import MantaOrchestrator, AgentTask, AgentType
import anthropic
import asyncio

client = anthropic.Anthropic()
orchestrator = MantaOrchestrator(client, max_workers=5)

tasks = [
    AgentTask(agent_type=AgentType.SANEAMENTO, documents=[docs1]),
    AgentTask(agent_type=AgentType.ENERGIA, documents=[docs2]),
    AgentTask(agent_type=AgentType.PORTOS, documents=[docs3]),
]

result = asyncio.run(orchestrator.orchestrate(tasks))
# Total: 6s (paralelo) = 5x mais rápido!
```

---

### B. Integrar Cache Compartilhado

**Registrar uma vez:**
```python
from orchestration import SharedCacheManager, SHARED_CONTEXTS

cache = SharedCacheManager()

# Registrar Lei 14.026 (usada por S8 e S6)
cache.register_context(
    key="lei_14026",
    content=open("lei-14026.txt").read(),  # 100KB
    agent_types=["S8", "S6"],
    ttl_seconds=3600  # 1 hora
)
```

**Usar em agentes:**
```python
# S8 busca contexto
lei_context = cache.get_context("S8")
if lei_context:
    print("✅ Cache hit! Economiza ~100K tokens")

# S6 busca mesmo contexto
lei_context = cache.get_context("S6")
if lei_context:
    print("✅ Cache hit novamente!")

# Métricas
cache.print_status()  # Ver taxa de acerto
```

---

### C. Integrar Roteamento Inteligente

**Substituir seu roteador:**
```python
from orchestration import MaestroRouter

router = MaestroRouter(client)

# Suas tarefas
tasks = [
    AgentTask(agent_type=AgentType.SANEAMENTO, documents=["pergunta curta?"]),
    AgentTask(agent_type=AgentType.ENERGIA, documents=["análise longa..."] * 10),
]

# Otimizar automaticamente
optimized = asyncio.run(router.route(tasks))

# Resultado: modelos corretos selecionados
# - Task 1: "haiku" (rápido, pequeno)
# - Task 2: "sonnet" (balanço, análise)
```

---

### D. Integrar Batch API Automático

**Detectar automaticamente:**
```python
from orchestration import BatchDetector

detector = BatchDetector()

# Tarefa grande (50+ docs)
task = AgentTask(
    agent_type=AgentType.SANEAMENTO,
    documents=[f"Concessionária {i}" for i in range(100)],
    model="opus"
)

if detector.should_use_batch(task):
    print("✅ Usar Batch API (50% desconto)")
    batch = client.beta.messages.batches.create(requests=[...])
    # Latência: 30min-24h mas 50% mais barato
else:
    print("❌ Usar sequencial (resultado imediato)")
```

---

### E. Integrar Monitoramento & Métricas

**Rastrear performance:**
```python
from orchestration import MetricsCollector

metrics = MetricsCollector()

# Após cada tarefa
metrics.record_task(
    agent="S8",
    tokens=5000,
    latency=2.3,
    cache_hit=True,
    model="sonnet"
)

# Analisar
summary = metrics.get_summary()
print(f"Taxa de cache hit: {summary['cache_hit_rate']:.1f}%")

agent_stats = metrics.get_agent_stats()
print(f"S8 latência P95: {agent_stats['S8']['latency_p95']:.1f}ms")

# Identificar gargalos
bottlenecks = metrics.get_bottlenecks()
for issue in bottlenecks:
    print(f"⚠️  {issue['agent']}: {issue['recommendation']}")

# Exportar para análise
metrics.export_json("metrics.json")
metrics.print_report()
```

---

### F. Integrar Handoff Otimizado

**Coordenar transições entre agentes:**
```python
from orchestration import HandoffCoordinator

coordinator = HandoffCoordinator()

# Sugerir próximos agentes
next_agents = coordinator.suggest_next_agents("S8")
# Resultado: ["Manta-05", "Manta-07", "Manta-15"]

# Preparar handoff com contexto herdado
handoff = coordinator.prepare_handoff(
    source_agent="S8",
    target_agent="Manta-05",
    analysis_result=s8_analysis,
    inherited_cache={"lei_14026": "..."},
    context_tokens=5000  # Economiza $0.015
)

# Manta-05 usa contexto herdado
result = manta_05(
    doc=handoff.analysis_result,
    inherited_cache=handoff.inherited_cache
)
```

---

## 🔗 Pipeline Completo

Integrar todos os 5 componentes numa pipeline real:

```python
import asyncio
import anthropic
from orchestration import (
    MantaOrchestrator,
    AgentTask,
    AgentType,
    SharedCacheManager,
    MaestroRouter,
    BatchDetector,
    MetricsCollector,
)
from orchestration import HandoffCoordinator

async def manta_saneamento_pipeline(documentos_eta):
    """Pipeline completo de saneamento com todas as otimizações"""
    
    client = anthropic.Anthropic()
    
    # Inicializar componentes
    orchestrator = MantaOrchestrator(client, max_workers=5)
    router = MaestroRouter(client)
    detector = BatchDetector()
    metrics = MetricsCollector()
    cache = SharedCacheManager()
    handoff = HandoffCoordinator()
    
    # 1. Registrar contexto compartilhado
    cache.register_context(
        key="lei_14026",
        content=open("lei-14026.txt").read(),
        agent_types=["S8", "S6"],
    )
    
    # 2. Preparar tarefas
    tasks = [
        AgentTask(
            agent_type=AgentType.SANEAMENTO,
            documents=documentos_eta,
            parallelizable=True,
            model="sonnet"
        )
    ]
    
    # 3. Rotear (selecionar modelos ótimos)
    tasks = await router.route(tasks)
    
    # 4. Executar em paralelo
    result = await orchestrator.orchestrate(
        tasks,
        enable_batch=detector.should_use_batch(tasks[0])
    )
    
    # 5. Registrar métricas
    metrics.record_task(
        agent="S8",
        tokens=result['total_tokens'],
        latency=result['execution_time'],
        cache_hit=result['cache_hits'] > 0
    )
    
    # 6. Handoff para Manta-05 (orçamento)
    handoff_data = handoff.prepare_handoff(
        source_agent="S8",
        target_agent="Manta-05",
        analysis_result=result['results']['S8']['content'],
        context_tokens=cache.usage_stats.get('S8', 0)
    )
    
    # 7. Imprimir resumo
    orchestrator.print_summary(result)
    metrics.print_report()
    
    return result

# Executar
resultado = asyncio.run(
    manta_saneamento_pipeline(["ETA Riachuelo doc1", "ETA Riachuelo doc2"])
)
```

---

## 📊 Visualizar Dashboard

Abrir no navegador:

```bash
python -m http.server 8000 --directory orchestration/
# Acessar: http://localhost:8000/dashboard.html
```

Dashboard mostra:
- ✅ Tempo total (vs sequencial)
- ✅ Tokens processados (economia com cache)
- ✅ Custo estimado (vs sem otimizações)
- ✅ Taxa de cache hit
- ✅ Performance por agente (latência P50/P95/P99)
- ✅ Gargalos identificados
- ✅ Recomendações automáticas

---

## 🎯 Checklist de Integração

- [ ] Copiar pasta `orchestration/` ao projeto
- [ ] Importar componentes desejados
- [ ] Ativar **paralelismo** (ThreadPoolExecutor)
- [ ] Registrar **contextos compartilhados** no cache
- [ ] Usar **roteamento inteligente** do Maestro
- [ ] Ativar **Batch API** para DD
- [ ] Implementar **monitoramento** de métricas
- [ ] Configurar **handoff** entre agentes
- [ ] Abrir **dashboard.html** para visualizar
- [ ] Testar pipeline end-to-end
- [ ] Validar economia (tempo, custo, tokens)
- [ ] Documentar padrões de uso no seu projeto

---

## 💡 Dicas de Otimização

### Melhor Paralelismo
- Use 5-10 workers (ajuste conforme capacidade)
- Agrupe tarefas independentes

### Melhor Cache
- Reutilize contextos > 10KB (economia > $0.001)
- Registre normas/leis reutilizadas 3+ vezes

### Melhor Batch API
- Use para DD com 50+ documentos
- Processe à noite (não urgente)
- Poupe até 50% em custos

### Melhor Roteamento
- Haiku para <5K tokens (rápido)
- Sonnet para 5-100K tokens (balanço)
- Opus para >100K tokens (preciso)

---

## 📚 Referências

- `orchestration/README.md` — Documentação técnica
- `orchestration/example_usage.py` — 5 exemplos práticos
- `orchestration/pipeline_real.py` — Caso de uso real (ETA)
- `docs/OPTIMIZATION-PATTERNS-MANTA.md` — Padrões de otimização
- `docs/MODEL-SPEEDS-PARALLEL-TOKENS.md` — Guia de velocidades

---

## 🚦 Próximos Passos

1. **Teste local** — Clone e rode `example_usage.py`
2. **Integre um agente** — Comece com S8 ou S9
3. **Ative paralelismo** — Meça ganhos de tempo
4. **Adicione cache** — Meça economia de tokens
5. **Implemente monitoramento** — Rastreie KPIs

---

**Status:** v4.3 (2026-07-23) — Sistema pronto para produção  
**Última atualização:** 2026-07-23  
**Suporte:** veja `orchestration/README.md`
