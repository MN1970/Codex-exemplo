"""
tests/test_agents.py — Suíte do catálogo de agentes e do endpoint de
invocação (streaming SSE) usado pelo Canvas.

Roda sem Postgres: `app.state.db_pool` não é configurado no app de
teste, então `invoke_agent`/`list_agent_sessions` caem no fallback em
memória (mesmo caminho de `routers/feedback.py`).
"""
import httpx
import pytest
from fastapi import FastAPI

from routers.agents import router as agents_router


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(agents_router)
    return app


@pytest.fixture
async def client(test_app: FastAPI):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


async def test_list_agents_includes_slug(client: httpx.AsyncClient):
    resp = await client.get("/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) >= 20
    slugs = {a["slug"] for a in agents}
    assert "agente-saneamento" in slugs
    assert "maestro" in slugs


async def test_get_agent_by_slug_or_code(client: httpx.AsyncClient):
    by_slug = await client.get("/agents/agente-portos")
    assert by_slug.status_code == 200
    assert by_slug.json()["code"] == "Manta 03-S6"

    by_code = await client.get("/agents/Manta 00")
    assert by_code.status_code == 200
    assert by_code.json()["slug"] == "maestro"


async def test_get_agent_unknown_returns_404(client: httpx.AsyncClient):
    resp = await client.get("/agents/nao-existe")
    assert resp.status_code == 404


async def test_invoke_unknown_agent_returns_404(client: httpx.AsyncClient):
    resp = await client.post("/agents/nao-existe/invoke", json={"prompt": "oi"})
    assert resp.status_code == 404


def _parse_sse(raw: str) -> list[tuple[str, dict]]:
    events = []
    for block in raw.strip("\n").split("\n\n"):
        if not block.strip():
            continue
        event_line, data_line = block.split("\n", 1)
        event = event_line.removeprefix("event: ")
        data = data_line.removeprefix("data: ")
        import json

        events.append((event, json.loads(data)))
    return events


async def test_invoke_streams_sse_and_saves_session(client: httpx.AsyncClient):
    resp = await client.post(
        "/agents/agente-saneamento/invoke",
        json={"prompt": "resuma o edital AySA", "user_email": "mneves@mantaassociados.com"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    events = _parse_sse(resp.text)
    kinds = [e for e, _ in events]
    assert kinds[0] == "meta"
    assert kinds[-1] == "done"
    assert "chunk" in kinds

    meta = events[0][1]
    assert meta["agent_slug"] == "agente-saneamento"

    done = events[-1][1]
    assert done["session_id"] == meta["session_id"]
    assert "resuma o edital AySA" in done["full_response"]

    # As sessões persistem (fallback em memória, sem pool configurado)
    # e ficam consultáveis via GET /agents/{slug}/sessions.
    sessions_resp = await client.get("/agents/agente-saneamento/sessions")
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    assert any(s["id"] == meta["session_id"] for s in sessions)
    assert sessions[0]["user_email"] == "mneves@mantaassociados.com"
