"""
Orquestrador Inteligente — Manta Maestro v4.3

Pacote com todas as otimizações de velocidade, cache e paralelismo para agentes.

Módulos:
  - orchestrator.py: Orquestrador principal (paralelismo cross-agente)
  - cache_manager.py: Cache compartilhado entre agentes
  - maestro_router.py: Roteamento inteligente com detecção de modelo
  - batch_detector.py: Detecção automática de Batch API
  - metrics.py: Monitoramento e coleta de métricas

Exemplo:
    from orchestrator import MantaOrchestrator, AgentTask, AgentType

    orchestrator = MantaOrchestrator(client)
    tasks = [AgentTask(...), ...]
    result = await orchestrator.orchestrate(tasks)
"""

from orchestrator import MantaOrchestrator, AgentTask, AgentType, OrchestrationResult
from cache_manager import SharedCacheManager, SHARED_CONTEXTS
from maestro_router import MaestroRouter, TaskType
from batch_detector import BatchDetector, BatchCriteria
from metrics import MetricsCollector, TaskMetrics

__version__ = "4.3.0"
__all__ = [
    "MantaOrchestrator",
    "AgentTask",
    "AgentType",
    "OrchestrationResult",
    "SharedCacheManager",
    "SHARED_CONTEXTS",
    "MaestroRouter",
    "TaskType",
    "BatchDetector",
    "BatchCriteria",
    "MetricsCollector",
    "TaskMetrics",
]
