"""
Maestro OS v6.0 — Queue Executor
Worker pool com controle de concorrência e rate limiting.
Máximo 8 agentes simultâneos, fila de até 16 tarefas.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, List, Dict
from datetime import datetime
from enum import Enum
import time


class TaskStatus(Enum):
    """Estados de uma tarefa."""
    QUEUED = "queued"             # Aguardando execução
    RUNNING = "running"           # Em execução
    COMPLETED = "completed"       # Completou com sucesso
    FAILED = "failed"             # Falhou
    RATE_LIMITED = "rate_limited" # Aguardando rate limit recovery


@dataclass
class TaskResult:
    """Resultado de execução de uma tarefa."""
    task_id: str
    agent_name: str
    status: TaskStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_secs: float = 0.0
    retries: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __repr__(self):
        return f"TaskResult({self.task_id}, {self.agent_name}, {self.status.value})"


@dataclass
class Task:
    """Uma tarefa a executar (agente invocado com contexto)."""
    task_id: str
    agent_name: str
    prompt: str                        # Instrução para o agente
    context: Dict[str, Any] = field(default_factory=dict)

    status: TaskStatus = TaskStatus.QUEUED
    result: Optional[TaskResult] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retries_left: int = 3

    def __hash__(self):
        return hash(self.task_id)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return self.task_id == other.task_id


class RateLimiter:
    """
    Gerenciador de rate limiting com exponential backoff.
    Quando 429 (throttled), aguarda e retorna com backoff.

    Estratégia:
    - Primeira falha 429: aguarda 2s
    - Segunda falha 429: aguarda 4s
    - Terceira falha 429: aguarda 8s
    - Quarta falha 429: aguarda 16s
    """

    def __init__(self, max_retries: int = 4):
        self.max_retries = max_retries
        self.consecutive_rate_limits = 0
        self.last_rate_limit_time = None

    async def wait_if_throttled(self) -> bool:
        """
        Aguarda exponential backoff se rate-limited.

        Returns:
            True se aguardou, False se sem throttle
        """
        if self.consecutive_rate_limits == 0:
            return False

        # Exponential backoff: 2s, 4s, 8s, 16s
        delay = 2 ** self.consecutive_rate_limits
        print(f"[RATE LIMIT] Aguardando {delay}s antes de retry "
              f"({self.consecutive_rate_limits}/{self.max_retries})...")
        await asyncio.sleep(delay)
        return True

    def record_rate_limit(self):
        """Registra ocorrência de rate limit 429."""
        self.consecutive_rate_limits = min(
            self.consecutive_rate_limits + 1,
            self.max_retries
        )
        self.last_rate_limit_time = datetime.utcnow().isoformat()

    def record_success(self):
        """Reset rate limiter após sucesso."""
        self.consecutive_rate_limits = 0

    def is_exhausted(self) -> bool:
        """Verifica se retries de rate limit foram esgotados."""
        return self.consecutive_rate_limits >= self.max_retries


class QueueExecutor:
    """
    Executor de tarefas com pool de workers e fila.

    Restrições:
    - Max 8 agentes simultâneos (concorrência na API Claude)
    - Fila até 16 tarefas
    - Rate limiting com exponential backoff

    Fluxo:
    1. task_queue ← Task(agent, prompt, context)
    2. Worker pool (até 8) puxa tarefas da fila
    3. Execute tarefa (invoke agent via Claude API)
    4. Se rate-limited: wait + retry
    5. Armazenar resultado em results dict
    """

    MAX_CONCURRENT_WORKERS = 8
    MAX_QUEUE_SIZE = 16
    DEFAULT_TIMEOUT_SECS = 300  # 5 minutos por tarefa

    def __init__(self, escalation_email: Optional[str] = None):
        """
        Inicializa executor de fila.

        Args:
            escalation_email: Email para escalação em caso de falhas
        """
        self.task_queue: asyncio.Queue[Task] = None  # Inicializa em start()
        self.results: Dict[str, TaskResult] = {}
        self.rate_limiter = RateLimiter()
        self.escalation_email = escalation_email or "maestro@manta.local"
        self.active_workers = 0

    async def start(self):
        """Inicia executor (cria fila)."""
        self.task_queue = asyncio.Queue(maxsize=self.MAX_QUEUE_SIZE)
        print(f"[QUEUE] Executor iniciado (max {self.MAX_CONCURRENT_WORKERS} workers, "
              f"fila {self.MAX_QUEUE_SIZE})")

    async def enqueue_task(self, task: Task) -> bool:
        """
        Enfileira uma tarefa.

        Args:
            task: Task para executar

        Returns:
            True se enfileirada, False se fila cheia
        """
        if self.task_queue is None:
            print("[ERROR] Executor não iniciado. Chame start() primeiro.")
            return False

        try:
            self.task_queue.put_nowait(task)
            task.status = TaskStatus.QUEUED
            print(f"[QUEUE] Tarefa enfileirada: {task.agent_name} ({task.task_id})")
            return True
        except asyncio.QueueFull:
            print(f"[ERROR] Fila cheia! Não pude enfileirar {task.agent_name} ({task.task_id})")
            return False

    async def _worker(self, worker_id: int):
        """
        Worker que processa tarefas da fila.

        Args:
            worker_id: ID do worker (1..MAX_CONCURRENT_WORKERS)
        """
        while True:
            try:
                # Aguardar tarefa (com timeout)
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                # Fila vazia, worker ociosa
                await asyncio.sleep(0.1)
                continue
            except asyncio.CancelledError:
                print(f"[WORKER {worker_id}] Cancelada")
                break

            # Executar tarefa
            await self._execute_task(task, worker_id)
            self.task_queue.task_done()

    async def _execute_task(self, task: Task, worker_id: int):
        """
        Executa uma tarefa individual com retry e rate limiting.

        Args:
            task: Task para executar
            worker_id: ID do worker
        """
        task.status = TaskStatus.RUNNING
        task.result = TaskResult(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )

        start_time = time.time()

        while task.retries_left > 0:
            try:
                # Aguardar rate limit se necessário
                if await self.rate_limiter.wait_if_throttled():
                    pass  # Já aguardou

                # Simular execução do agente
                # Em produção: chamar Claude API via MCP
                output = await self._invoke_agent(task, worker_id)

                # Sucesso
                task.result.status = TaskStatus.COMPLETED
                task.result.output = output
                task.result.retries = 3 - task.retries_left
                task.result.completed_at = datetime.utcnow().isoformat()
                task.result.duration_secs = time.time() - start_time
                task.status = TaskStatus.COMPLETED

                self.rate_limiter.record_success()

                print(f"[WORKER {worker_id}] ✓ {task.agent_name} completou "
                      f"({task.result.duration_secs:.1f}s)")
                self.results[task.task_id] = task.result
                return

            except Exception as e:
                error_str = str(e).lower()

                # Detectar rate limit 429
                if "429" in error_str or "throttled" in error_str or "rate" in error_str:
                    self.rate_limiter.record_rate_limit()
                    task.status = TaskStatus.RATE_LIMITED
                    task.retries_left -= 1
                    print(f"[WORKER {worker_id}] ⏳ Rate limited. Retries: {task.retries_left}")

                    if self.rate_limiter.is_exhausted():
                        # Retries esgotados
                        task.result.status = TaskStatus.FAILED
                        task.result.error = "Rate limit retries exhausted"
                        task.status = TaskStatus.FAILED
                        print(f"[WORKER {worker_id}] ✗ Rate limit retries exhausted para {task.agent_name}")
                        self.results[task.task_id] = task.result
                        return
                else:
                    # Outro erro
                    task.result.status = TaskStatus.FAILED
                    task.result.error = str(e)
                    task.result.retries = 3 - task.retries_left
                    task.result.completed_at = datetime.utcnow().isoformat()
                    task.result.duration_secs = time.time() - start_time
                    task.status = TaskStatus.FAILED
                    print(f"[WORKER {worker_id}] ✗ {task.agent_name} falhou: {e}")
                    self.results[task.task_id] = task.result
                    return

    async def _invoke_agent(self, task: Task, worker_id: int) -> str:
        """
        Invoca um agente (stub para Claude API).

        Simula latência de 1-3s. Em produção: chamar Claude via MCP.

        Args:
            task: Task com prompt
            worker_id: ID do worker

        Returns:
            Output do agente
        """
        # Simular latência de execução
        await asyncio.sleep(1 + (worker_id % 3) * 0.5)

        # Em produção, retornar output real do agente
        return f"Output from {task.agent_name}"

    async def execute_all(self, tasks: List[Task]) -> Dict[str, TaskResult]:
        """
        Executa todas tarefas e aguarda conclusão.

        Args:
            tasks: Lista de tarefas

        Returns:
            Dict {task_id: TaskResult}
        """
        # Iniciar workers
        await self.start()

        # Enfileirar todas tarefas
        for task in tasks:
            await self.enqueue_task(task)

        # Criar workers
        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(1, self.MAX_CONCURRENT_WORKERS + 1)
        ]

        print(f"[EXECUTOR] Iniciando {len(workers)} workers para {len(tasks)} tarefas...")

        # Aguardar todas tarefas completarem
        try:
            await self.task_queue.join()
        except asyncio.CancelledError:
            pass
        finally:
            # Cancelar workers
            for worker in workers:
                worker.cancel()

        # Aguardar workers finalizarem
        await asyncio.gather(*workers, return_exceptions=True)

        print(f"[EXECUTOR] Concluído. Resultados: {len(self.results)} tarefas")
        return self.results

    def get_results_summary(self) -> Dict[str, int]:
        """
        Retorna sumário de resultados.

        Returns:
            Dict com {status: count}
        """
        summary = {
            "total": len(self.results),
            "completed": sum(1 for r in self.results.values() if r.status == TaskStatus.COMPLETED),
            "failed": sum(1 for r in self.results.values() if r.status == TaskStatus.FAILED),
            "rate_limited": sum(1 for r in self.results.values() if r.status == TaskStatus.RATE_LIMITED),
        }
        return summary
