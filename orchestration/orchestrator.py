"""
Orquestrador Principal — Manta Maestro v4.3
Gerencia paralelismo cross-agente, cache compartilhado, batch API automático e métricas.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import time
from dataclasses import dataclass, asdict
from enum import Enum

from cache_manager import SharedCacheManager
from maestro_router import MaestroRouter
from batch_detector import BatchDetector
from metrics import MetricsCollector


class AgentType(Enum):
    """Tipos de agentes Manta"""
    SANEAMENTO = "S8"
    ENERGIA = "S9"
    PORTOS = "S6"
    AEROPORTOS = "S7"
    BARRAGENS = "S10"
    ORCAMENTO = "Manta-05"
    CRONOGRAMA = "Manta-07"


@dataclass
class AgentTask:
    """Definição de tarefa para agente"""
    agent_type: AgentType
    documents: List[str]
    context: Optional[Dict[str, str]] = None
    parallelizable: bool = False
    model: str = "sonnet"
    max_tokens: int = 2000


@dataclass
class OrchestrationResult:
    """Resultado da orquestração"""
    results: Dict[str, Any]
    metrics: Dict[str, Any]
    execution_time: float
    total_tokens: int
    total_cost: float
    cache_hits: int


class MantaOrchestrator:
    """Orquestrador principal do Manta Maestro"""

    def __init__(self, client, max_workers: int = 5):
        self.client = client
        self.max_workers = max_workers
        self.cache_manager = SharedCacheManager()
        self.router = MaestroRouter(client)
        self.batch_detector = BatchDetector()
        self.metrics = MetricsCollector()

    async def orchestrate(
        self, tasks: List[AgentTask], enable_batch: bool = True
    ) -> OrchestrationResult:
        """
        Orquestar múltiplas tarefas de agentes em paralelo

        Args:
            tasks: Lista de AgentTasks a executar
            enable_batch: Ativar Batch API automático para DD

        Returns:
            OrchestrationResult com resultados, métricas e timing
        """
        start_time = time.time()
        results = {}
        cache_hits = 0

        # 1. Roteamento inteligente (detectar paralelismo)
        routed_tasks = await self.router.route(tasks)

        # 2. Detectar se precisa Batch API
        batch_tasks = []
        parallel_tasks = []

        for task in routed_tasks:
            if enable_batch and self.batch_detector.should_use_batch(task):
                batch_tasks.append(task)
            else:
                parallel_tasks.append(task)

        # 3. Executar tarefas em paralelo (ThreadPoolExecutor)
        if parallel_tasks:
            results.update(
                await self._execute_parallel(parallel_tasks)
            )

        # 4. Executar tarefas em Batch API (background)
        if batch_tasks:
            batch_results = await self._execute_batch(batch_tasks)
            results.update(batch_results)

        # 5. Coletar métricas
        execution_time = time.time() - start_time
        metrics_data = self.metrics.get_summary()

        return OrchestrationResult(
            results=results,
            metrics=metrics_data,
            execution_time=execution_time,
            total_tokens=metrics_data.get("total_tokens", 0),
            total_cost=metrics_data.get("total_cost", 0.0),
            cache_hits=self.cache_manager.cache_hits,
        )

    async def _execute_parallel(
        self, tasks: List[AgentTask]
    ) -> Dict[str, Any]:
        """Executar tarefas em paralelo com ThreadPoolExecutor"""
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for i, task in enumerate(tasks):
                future = executor.submit(
                    self._execute_task,
                    task,
                    task_id=f"{task.agent_type.value}-{i}"
                )
                futures[future] = task

            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    results[task.agent_type.value] = result
                    self.metrics.record_task(
                        agent=task.agent_type.value,
                        tokens=result.get("tokens_used", 0),
                        latency=result.get("latency", 0),
                        cache_hit=result.get("cache_hit", False)
                    )
                except Exception as e:
                    results[task.agent_type.value] = {"error": str(e)}

        return results

    async def _execute_batch(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Executar tarefas via Batch API (50% desconto)"""
        batch_requests = []

        for i, task in enumerate(tasks):
            batch_requests.append({
                "custom_id": f"batch-{task.agent_type.value}-{i}",
                "params": {
                    "model": task.model,
                    "max_tokens": task.max_tokens,
                    "system": [
                        {
                            "type": "text",
                            "text": self.cache_manager.get_context(
                                task.agent_type.value
                            ),
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    "messages": [
                        {"role": "user", "content": doc}
                        for doc in task.documents
                    ]
                }
            })

        # Submeter batch
        batch = self.client.beta.messages.batches.create(
            requests=batch_requests
        )

        # Retornar resultado assíncrono
        return {
            "batch_id": batch.id,
            "status": "processing",
            "request_count": len(batch_requests),
            "discount": "50%"
        }

    def _execute_task(self, task: AgentTask, task_id: str) -> Dict[str, Any]:
        """Executar tarefa individual com cache compartilhado"""
        start = time.time()

        # 1. Buscar contexto compartilhado (cache)
        context = self.cache_manager.get_context(task.agent_type.value)
        cache_hit = context is not None

        if not context:
            context = task.context or {}

        # 2. Chamar modelo com prompt caching
        response = self.client.messages.create(
            model=task.model,
            max_tokens=task.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": context,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {"role": "user", "content": doc}
                for doc in task.documents
            ]
        )

        latency = time.time() - start

        # 3. Registrar no cache se sucesso
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self.cache_manager.record_usage(
            agent=task.agent_type.value,
            tokens=tokens_used
        )

        return {
            "task_id": task_id,
            "content": response.content[0].text,
            "tokens_used": tokens_used,
            "latency": latency,
            "cache_hit": cache_hit
        }

    def print_summary(self, result: OrchestrationResult) -> None:
        """Imprimir resumo de execução"""
        print("\n" + "="*60)
        print("📊 RESUMO DE ORQUESTRAÇÃO — Manta Maestro v4.3")
        print("="*60)
        print(f"⏱️  Tempo total:        {result.execution_time:.2f}s")
        print(f"🎯 Tokens processados: {result.total_tokens:,}")
        print(f"💰 Custo estimado:     ${result.total_cost:.4f}")
        print(f"💾 Cache hits:         {result.cache_hits}")
        print(f"📈 Economia:           ~{result.metrics.get('cache_savings_pct', 0):.0f}%")
        print("="*60)
        print("\nResultados por agente:")
        for agent, data in result.results.items():
            if isinstance(data, dict) and "error" not in data:
                print(f"  ✅ {agent:12s} — {data.get('tokens_used', 0)} tokens, {data.get('latency', 0):.2f}s")
            elif isinstance(data, dict) and "batch_id" in data:
                print(f"  ⏳ {agent:12s} — Batch {data['batch_id']} (50% desconto)")
            else:
                print(f"  ❌ {agent:12s} — Erro")
        print("="*60 + "\n")


# Exemplo de uso
if __name__ == "__main__":
    import anthropic

    client = anthropic.Anthropic()
    orchestrator = MantaOrchestrator(client, max_workers=5)

    # Definir tarefas
    tasks = [
        AgentTask(
            agent_type=AgentType.SANEAMENTO,
            documents=["ETA Riachuelo: analise de projeto", "ETE Peixoto: estudo prévio"],
            parallelizable=True,
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.ENERGIA,
            documents=["LT 230kV: traçado", "Subestação: arranjo"],
            parallelizable=True,
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.PORTOS,
            documents=["Terminal contêiner: DD"],
            parallelizable=False,
            model="opus"
        ),
    ]

    # Executar orquestração
    # result = asyncio.run(orchestrator.orchestrate(tasks))
    # orchestrator.print_summary(result)
