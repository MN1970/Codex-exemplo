"""
Maestro OS v6.0 — Registro de episódios de agente (aprendizado)

Converte `TaskResult` (queue_executor.py) em linhas da tabela Supabase
`agent_episodes` e grava via `supabase_client.insert_rows`.

Escopo desta primeira versão: só o que já é medido de verdade hoje pelo
orquestrador (agent_name, duration_secs, retries, status, error). Campos
do schema de `agent_episodes` que não têm fonte real ainda (quality_score,
tokens_consumed, model_used, self_critique, aluci_guard_pass,
consist_guard_pass) ficam None — melhor não preencher do que inventar um
valor. Preenchê-los é trabalho futuro (precisa medir tokens/modelo por
task no queue_executor, e integrar aluci-guard/consist-guard de verdade).

Promoção de um episódio para conhecimento em `manta_rag_chunks` continua
manual/revisada — este módulo não escreve em nenhuma tabela de RAG.
"""

import logging
from typing import Dict, List

from .queue_executor import Task, TaskResult, TaskStatus
from .supabase_client import insert_rows

logger = logging.getLogger("maestro.episode_recorder")

_MAX_TASK_DESCRIPTION_CHARS = 500


def _task_result_to_episode_row(task: Task, task_result: TaskResult, task_type: str) -> dict:
    lessons_learned: List[str] = []
    if task_result.error:
        lessons_learned.append(task_result.error)

    return {
        "agent_id": task_result.agent_name,
        "task_type": task_type,
        "task_description": task.prompt[:_MAX_TASK_DESCRIPTION_CHARS] if task.prompt else None,
        "iterations_needed": task_result.retries,
        "lessons_learned": lessons_learned,
        "duration_seconds": int(round(task_result.duration_secs)),
        "escalated_to_human": task_result.status == TaskStatus.FAILED,
    }


def record_fan_out_episodes(
    tasks: List[Task],
    task_results: Dict[str, TaskResult],
    task_type: str = "fan_out",
) -> None:
    """
    Grava um episódio por tarefa concluída no fan-out em `agent_episodes`.

    `tasks` é a lista original enviada a `queue_executor.execute_all` (dá
    acesso ao prompt, que `TaskResult` não carrega); `task_results` é o
    dict `{task_id: TaskResult}` retornado por `execute_all`.

    Best-effort: nunca lança. Se o Supabase não estiver configurado,
    é um no-op (ver `supabase_client.get_supabase_client`).
    """
    if not task_results:
        return

    tasks_by_id = {t.task_id: t for t in tasks}

    rows = []
    for task_id, task_result in task_results.items():
        task = tasks_by_id.get(task_id)
        if task is None:
            logger.warning("TaskResult sem Task original correspondente (task_id=%s) — pulando.", task_id)
            continue
        rows.append(_task_result_to_episode_row(task, task_result, task_type))

    ok = insert_rows("agent_episodes", rows)
    if ok:
        logger.info("Gravados %d episódio(s) em agent_episodes (task_type=%s).", len(rows), task_type)
