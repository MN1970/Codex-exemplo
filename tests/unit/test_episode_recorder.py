"""
Testes unitários — `src/maestro/episode_recorder.py` + `supabase_client.py`.

Cobre a primeira gravação real de telemetria do Maestro OS em
`agent_episodes` (até esta mudança, nada em `src/maestro/` escrevia em
nenhuma tabela Supabase — `SupabaseStateManager` em `mcp_tools.py` era
puro stub). Foco destes testes: (1) sem Supabase configurado, tudo é
no-op silencioso; (2) com um cliente mockado, o mapeamento Task/TaskResult
-> linha de `agent_episodes` está correto; (3) falha do cliente nunca
propaga para o chamador (best-effort).
"""

import pytest

from src.maestro import episode_recorder, supabase_client
from src.maestro.queue_executor import Task, TaskResult, TaskStatus

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_supabase_client_cache(monkeypatch):
    # Garante que cada teste começa sem cache de cliente e sem env vars
    # residuais de outro teste/da máquina local.
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    supabase_client.reset_client_cache_for_tests()
    yield
    supabase_client.reset_client_cache_for_tests()


class _FakeTable:
    def __init__(self, capture: list, raise_on_execute: bool = False):
        self._capture = capture
        self._raise_on_execute = raise_on_execute
        self._pending_rows = None

    def insert(self, rows):
        self._pending_rows = rows
        return self

    def execute(self):
        if self._raise_on_execute:
            raise RuntimeError("simulated Supabase API failure")
        self._capture.append(self._pending_rows)
        return {"data": self._pending_rows}


class _FakeSupabaseClient:
    def __init__(self, capture: list, raise_on_execute: bool = False):
        self._capture = capture
        self._raise_on_execute = raise_on_execute

    def table(self, name):
        assert name == "agent_episodes"
        return _FakeTable(self._capture, raise_on_execute=self._raise_on_execute)


def _make_task_and_result(task_id="task-1", agent_name="agente-saneamento",
                           status=TaskStatus.COMPLETED, error=None, retries=1,
                           duration_secs=3.5, prompt="Analise a ETE X"):
    task = Task(task_id=task_id, agent_name=agent_name, prompt=prompt)
    result = TaskResult(
        task_id=task_id,
        agent_name=agent_name,
        status=status,
        error=error,
        duration_secs=duration_secs,
        retries=retries,
    )
    return task, result


def test_get_supabase_client_returns_none_without_env_vars():
    assert supabase_client.get_supabase_client() is None


def test_insert_rows_is_noop_without_client():
    # Sem SUPABASE_URL/KEY configurados, insert_rows deve retornar False
    # (gravação não tentada) sem lançar exceção.
    ok = supabase_client.insert_rows("agent_episodes", [{"agent_id": "x"}])
    assert ok is False


def test_record_fan_out_episodes_is_silent_noop_without_supabase():
    task, result = _make_task_and_result()
    # Não deve lançar, mesmo sem Supabase configurado.
    episode_recorder.record_fan_out_episodes([task], {task.task_id: result})


def test_record_fan_out_episodes_maps_fields_correctly(monkeypatch):
    captured_batches = []
    fake_client = _FakeSupabaseClient(captured_batches)
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: fake_client)

    task, result = _make_task_and_result(
        agent_name="agente-energia",
        status=TaskStatus.COMPLETED,
        retries=2,
        duration_secs=12.4,
        prompt="Revisar RAP de LT 500kV" * 50,  # forçar truncamento
    )

    episode_recorder.record_fan_out_episodes([task], {task.task_id: result}, task_type="fan_out")

    assert len(captured_batches) == 1
    rows = captured_batches[0]
    assert len(rows) == 1
    row = rows[0]

    assert row["agent_id"] == "agente-energia"
    assert row["task_type"] == "fan_out"
    assert len(row["task_description"]) <= 500
    assert row["iterations_needed"] == 2
    assert row["duration_seconds"] == 12  # round(12.4) -> 12
    assert row["escalated_to_human"] is False
    assert row["lessons_learned"] == []


def test_record_fan_out_episodes_flags_failed_tasks_as_escalated(monkeypatch):
    captured_batches = []
    fake_client = _FakeSupabaseClient(captured_batches)
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: fake_client)

    task, result = _make_task_and_result(
        status=TaskStatus.FAILED,
        error="timeout ao chamar agente",
    )

    episode_recorder.record_fan_out_episodes([task], {task.task_id: result})

    row = captured_batches[0][0]
    assert row["escalated_to_human"] is True
    assert row["lessons_learned"] == ["timeout ao chamar agente"]


def test_record_fan_out_episodes_never_raises_when_supabase_api_fails(monkeypatch):
    fake_client = _FakeSupabaseClient(capture=[], raise_on_execute=True)
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: fake_client)

    task, result = _make_task_and_result()

    # Não deve lançar mesmo com a "API" falhando durante execute().
    episode_recorder.record_fan_out_episodes([task], {task.task_id: result})


def test_record_fan_out_episodes_skips_task_result_without_matching_task():
    task, result = _make_task_and_result(task_id="task-1")
    orphan_result = TaskResult(
        task_id="task-999",
        agent_name="agente-fantasma",
        status=TaskStatus.COMPLETED,
        duration_secs=1.0,
    )

    # Não deve lançar mesmo com um TaskResult sem Task correspondente.
    episode_recorder.record_fan_out_episodes(
        [task],
        {task.task_id: result, "task-999": orphan_result},
    )


def test_record_fan_out_episodes_empty_results_is_noop():
    episode_recorder.record_fan_out_episodes([], {})
