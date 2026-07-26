# Manta Backend

Backend FastAPI async do Manta Maestro (Agent Registry). Expõe o
registro de 20 agentes, o motor de roteamento (Q1 do intake), as
coleções RAG (Supabase pgvector) e feedback de uso, conforme descrito
no `CLAUDE.md` master do repositório.

## Rodar localmente (sem Docker)

```bash
cd manta-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Sem um Postgres rodando, a app ainda sobe — endpoints que dependem de
banco (rag/query, feedback com persistência) degradam para 503 ou
fallback em memória; tudo o resto (agents, routing, docs) funciona
normalmente.

## Rodar com Docker Compose (app + Postgres/pgvector)

```bash
cd manta-backend
docker compose up --build
```

## Poetry (alternativa ao pip)

```bash
cd manta-backend
poetry install
poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `GET /` — status básico
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc
- `GET /agents` — registro dos 20 agentes (Eixos 1 e 2)
- `GET /agents/lifecycle` — 8 fases do ciclo de vida (Eixo 3)
- `POST /routing/classify` — classifica texto livre → agente vertical
- `GET /rag/collections` — 5 coleções RAG (saneamento, energia, portos, aeroportos, barragens)
- `POST /rag/query` — busca semântica pgvector (requer DB)
- `POST /feedback` — registra feedback de uso de um agente
- `GET /admin/health` — health check (app + DB)
- `POST /admin/token` — emite JWT de dev (`admin`/`admin` → role admin)
- `GET /admin/deploy-checklist` — checklist de deploy v4.2 (requer auth)

## Estrutura

```
manta-backend/
├── app.py            # FastAPI app + lifespan (DB pool, aiohttp session)
├── config.py         # Settings (pydantic-settings)
├── database.py       # Pool asyncpg + dependencies
├── auth.py           # JWT + role gate
├── routers/
│   ├── agents.py
│   ├── rag.py
│   ├── routing.py
│   ├── feedback.py
│   └── admin.py
├── mcp/
│   └── client.py      # Cliente async (aiohttp) para o gateway MCP
├── ml/
│   └── embeddings.py   # Geração de embeddings (stub determinístico)
├── scripts/init.sql    # Bootstrap do Postgres local (docker-compose)
├── pyproject.toml      # Poetry
├── requirements.txt    # pip
├── Dockerfile
└── docker-compose.yml
```
