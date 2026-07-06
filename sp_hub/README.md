# sp_hub — Manta 20 SP Hub v2.0

Implementação Python das Fases 2 e 3 da spec
[`docs/MANTA-20-SPHUB-SPEC-v2.0.md`](../docs/MANTA-20-SPHUB-SPEC-v2.0.md).

## Layout

```
sp_hub/
├── __init__.py        # exports públicos + versão
├── models.py          # ChangeEntry, RoutingRule, RoutingDecision, FeedEntry, SyncResult, WriteRequest, Priority
├── db.py              # wrapper Supabase (Protocol para permitir fake em teste)
├── classifier.py      # (path, name, ext) → doc_type (fallback quando router não decide)
├── router.py          # aplica sp_routing_rules → RoutingDecision (union agents, max priority)
├── feed.py            # RoutingDecision → FeedEntry[] (com sanitização R1)
├── delta_sync.py      # ENTRYPOINT Fase 2: sp_index Δ → route → sp_agent_feed (+ RAG opcional)
├── rag_bridge.py      # Fase 3: NoopRagBridge | HttpRagBridge | QueueRagBridge
├── write_gateway.py   # Fase 3: M20.write() → webhook Zapier → PUT Graph API + audit log
└── daily_index.sh     # cron wrapper (sp_indexer.py + python -m sp_hub.delta_sync)
```

## Uso — Fase 2 (delta + notificação)

```python
from sp_hub.db import supabase_client
from sp_hub.delta_sync import run_delta_sync

result = run_delta_sync(supabase_client())
print(result.summary())
# [success] Δ=12 feed=17 rag=8 err=0 in 1.34s
```

Ou via CLI: `python -m sp_hub.delta_sync`.

Ou via cron: `sp_hub/daily_index.sh` (roda `sp_indexer.py` antes se
`SP_INDEXER_PATH` estiver setado).

## Uso — Fase 3 (write gateway)

```python
from sp_hub.db import supabase_client
from sp_hub.models import WriteRequest
from sp_hub.write_gateway import WriteGateway

gw = WriteGateway(supabase_client())
result = gw.write(WriteRequest(
    drive_id="b!7wlZlI7tWU2o09im0xX4dSggtXaRRJ5LktNsMxjSZr8OGwV61sTwTqLCB0pYNM1D",
    path="/04_IA/outputs/relatorio_M1_202607.pdf",
    content_b64=base64_content,
    content_type="application/pdf",
    metadata={"origem": "M1", "ticket": "MANTA-123"},
))
```

## Variáveis de ambiente

| Var | Obrigatória | Descrição |
|-----|-------------|-----------|
| `SUPABASE_URL` | ✅ | URL do projeto Supabase. |
| `SUPABASE_SERVICE_KEY` | ✅ | Service role key (bypass RLS — insert em `sp_agent_feed`, `sp_sync_log`). |
| `SP_HUB_RAG_ENDPOINT` | opcional | Base URL do Manta 18. Se ausente, RAG bridge vira no-op (docs não são chunked automaticamente). |
| `SP_HUB_ZAPIER_WRITE_WEBHOOK` | ✅ para escrita | URL do webhook Zapier que executa o PUT no Graph API. |
| `SP_HUB_DELTA_LIMIT` | opcional | Máximo de docs processados por run (default 1000). |
| `SP_INDEXER_PATH` | opcional (só cron) | Path para o `sp_indexer.py` legado — se setado, roda antes do `delta_sync.py`. |
| `SP_HUB_VENV` | opcional (só cron) | Path para o venv Python. |

## Testes

```bash
pip install pytest
python -m pytest tests/sp_hub/ -v
# 36 passed in 0.08s
```

Os testes usam um `FakeSupabase` in-memory (ver `tests/sp_hub/conftest.py`).
Não requerem cliente Supabase real nem acesso de rede — 100% offline.

## Regras invariantes

- **R1 sanitização de path**: `feed.decisions_to_feed` substitui o segmento
  logo após `02_CLIENTE/` por `<CLIENTE>` antes de gravar no
  `sp_agent_feed`. Não é opcional.
- **R7 selo de qualidade**: cada operação registra em `sp_sync_log` o
  bastante para reconstruir o selo (docs detectados, roteados, ingeridos).
- **Idempotência**: rodar `delta_sync` duas vezes seguidas sem novas
  mudanças produz zero novos inserts. O índice único parcial
  `uniq_agent_feed_pending` protege contra duplicatas em `pending`.
