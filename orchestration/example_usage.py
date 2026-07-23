#!/usr/bin/env python3
"""
Exemplo Completo — Orquestrador Manta Maestro v4.3
Demonstra todas as 5 recomendações de otimização em ação.
"""

import asyncio
import anthropic
from orchestrator import MantaOrchestrator, AgentTask, AgentType
from cache_manager import SharedCacheManager, SHARED_CONTEXTS
from maestro_router import MaestroRouter
from batch_detector import BatchDetector
from metrics import MetricsCollector


async def example_1_paralelismo():
    """
    EXEMPLO 1: Paralelismo Cross-Agente
    Executar 3 agentes em paralelo (5x mais rápido)
    """
    print("\n" + "="*70)
    print("EXEMPLO 1: PARALELISMO CROSS-AGENTE")
    print("="*70)

    client = anthropic.Anthropic()
    orchestrator = MantaOrchestrator(client, max_workers=3)

    tasks = [
        AgentTask(
            agent_type=AgentType.SANEAMENTO,
            documents=[
                "ETA Riachuelo: analise de qualidade de água",
                "ETE Peixoto: verificação de projeto"
            ],
            parallelizable=True,
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.ENERGIA,
            documents=[
                "LT 230kV: verificação de ampacidade",
                "Subestação: verificação de arranjo"
            ],
            parallelizable=True,
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.PORTOS,
            documents=[
                "Terminal de contêiner: verificação de dragagem"
            ],
            parallelizable=False,
            model="sonnet"
        )
    ]

    print("\n📋 Tarefas:")
    for task in tasks:
        print(f"  - {task.agent_type.value}: {len(task.documents)} docs")

    # result = await orchestrator.orchestrate(tasks)
    # orchestrator.print_summary(result)
    print("\n✅ (Simulado) Paralelismo ativado — 3 agentes rodando simultaneamente")


async def example_2_cache_compartilhado():
    """
    EXEMPLO 2: Cache Compartilhado
    Lei 14.026 é cachada uma vez, reutilizada por S8 e S6
    """
    print("\n" + "="*70)
    print("EXEMPLO 2: CACHE COMPARTILHADO")
    print("="*70)

    cache = SharedCacheManager()

    # Registrar Lei 14.026 (usada por Saneamento e Portos)
    cache.register_context(
        key="lei_14026",
        content="""
        Lei 14.026/2020 (100KB)
        - Universalização 99% água, 90% esgoto até 2033
        - Subsídio cruzado, regionalização, tarifa social
        - Regulação: ANA, ARSESP, agências estaduais
        """,
        agent_types=["S8", "S6"],
        ttl_seconds=3600
    )

    # Registrar ANEEL REN (usada por Energia)
    cache.register_context(
        key="aneel_ren",
        content="""
        ANEEL Resoluções (75KB)
        - RAP (Receita Anual Permitida)
        - Leilão de transmissão
        - Procedimentos de rede (ONS), MRE
        """,
        agent_types=["S9"],
        ttl_seconds=3600
    )

    print("\n📦 Cache Registrado:")
    print(f"  - lei_14026 (S8, S6)")
    print(f"  - aneel_ren (S9)")

    # S8 busca Lei 14.026
    print("\n🔍 S8 busca contexto:")
    context = cache.get_context("S8")
    if context:
        print(f"  ✅ Encontrado no cache (CACHE HIT)")
        print(f"  Economiza: ~100K tokens (~$0.30)")

    # S6 busca Lei 14.026
    print("\n🔍 S6 busca contexto:")
    context = cache.get_context("S6")
    if context:
        print(f"  ✅ Encontrado no cache (CACHE HIT)")
        print(f"  Economiza: ~100K tokens (~$0.30)")

    cache.print_status()


async def example_3_roteamento_inteligente():
    """
    EXEMPLO 3: Roteamento Inteligente
    Maestro seleciona modelo otimizado (Haiku/Sonnet/Opus)
    """
    print("\n" + "="*70)
    print("EXEMPLO 3: ROTEAMENTO INTELIGENTE")
    print("="*70)

    client = anthropic.Anthropic()
    router = MaestroRouter(client)

    tasks = [
        AgentTask(
            agent_type=AgentType.SANEAMENTO,
            documents=["É ETA ou ETE?"],  # Curto = classificação
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.ENERGIA,
            documents=["LT 230kV: " + "análise " * 100],  # Médio = análise
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.PORTOS,
            documents=[f"Doc {i}" for i in range(50)],  # Grande = DD
            model="sonnet"
        )
    ]

    print("\n📋 Tarefas ANTES do roteamento:")
    for task in tasks:
        print(f"  - {task.agent_type.value:12s}: {len(task.documents)} docs, modelo:{task.model}")

    optimized = await router.route(tasks)

    print("\n📋 Tarefas DEPOIS do roteamento (otimizado):")
    router.print_analysis(optimized)


async def example_4_batch_api_automatico():
    """
    EXEMPLO 4: Batch API Automático
    Detecta automaticamente quando usar Batch API (50% desconto)
    """
    print("\n" + "="*70)
    print("EXEMPLO 4: BATCH API AUTOMÁTICO")
    print("="*70)

    detector = BatchDetector()

    # Cenário 1: Tarefa pequena (sem Batch)
    small_task = AgentTask(
        agent_type=AgentType.SANEAMENTO,
        documents=["ETA 1"],
        model="sonnet"
    )

    # Cenário 2: DD com muitos docs (com Batch)
    dd_task = AgentTask(
        agent_type=AgentType.SANEAMENTO,
        documents=[f"Concessionária {i}: DD financeira" for i in range(20)],
        model="opus",
        max_tokens=3000
    )

    print("\n📋 Tarefas analisadas:")

    print("\n1. Tarefa pequena:")
    print(f"   Documentos: {len(small_task.documents)}")
    print(f"   Usar Batch? {detector.should_use_batch(small_task)}")

    print("\n2. DD com 20 docs:")
    print(f"   Documentos: {len(dd_task.documents)}")
    print(f"   Usar Batch? {detector.should_use_batch(dd_task)}")

    detector.print_analysis(dd_task)


async def example_5_metricas():
    """
    EXEMPLO 5: Monitoramento & Métricas
    Rastreia performance, custo e identifica gargalos
    """
    print("\n" + "="*70)
    print("EXEMPLO 5: MONITORAMENTO & MÉTRICAS")
    print("="*70)

    metrics = MetricsCollector()

    # Simular tarefas
    print("\n📊 Registrando tarefas...")

    # S8 com cache
    metrics.record_task(agent="S8", tokens=5000, latency=2.5, cache_hit=True, model="sonnet")
    metrics.record_task(agent="S8", tokens=4800, latency=2.3, cache_hit=True, model="sonnet")

    # S9 sem cache
    metrics.record_task(agent="S9", tokens=6000, latency=3.1, cache_hit=False, model="sonnet")
    metrics.record_task(agent="S9", tokens=5900, latency=3.0, cache_hit=False, model="sonnet")

    # S6 com latência alta
    metrics.record_task(agent="S6", tokens=4500, latency=15.2, cache_hit=True, model="sonnet")

    # Imprimir relatório
    metrics.print_report()

    # Exportar
    # metrics.export_json("orchestration_metrics.json")


async def main():
    """Executar todos os exemplos"""
    print("\n\n")
    print("#" * 70)
    print("# ORQUESTRADOR INTELIGENTE — MANTA MAESTRO v4.3")
    print("# 5 Recomendações de Otimização")
    print("#" * 70)

    # Exemplo 1: Paralelismo
    await example_1_paralelismo()

    # Exemplo 2: Cache Compartilhado
    await example_2_cache_compartilhado()

    # Exemplo 3: Roteamento Inteligente
    await example_3_roteamento_inteligente()

    # Exemplo 4: Batch API Automático
    await example_4_batch_api_automatico()

    # Exemplo 5: Métricas
    await example_5_metricas()

    print("\n" + "#" * 70)
    print("# ✅ TODOS OS EXEMPLOS EXECUTADOS")
    print("#" * 70)
    print("\n📚 Próximos passos:")
    print("  1. Integrar orchestrator.py no seu pipeline Manta")
    print("  2. Registrar contextos compartilhados no cache")
    print("  3. Ativar monitoramento em produção")
    print("  4. Verificar economia em métricas.json\n")


if __name__ == "__main__":
    asyncio.run(main())
