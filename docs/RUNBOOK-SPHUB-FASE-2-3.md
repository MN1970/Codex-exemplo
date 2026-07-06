# Runbook — Ativação das Fases 2 e 3 do SP Hub

Guia operacional para colocar as Fases 2 (delta + notificação) e 3
(RAG bridge + escrita) do Manta 20 em produção. Complementa a spec
canônica [`MANTA-20-SPHUB-SPEC-v2.0.md`](MANTA-20-SPHUB-SPEC-v2.0.md).

Ticket: `MANTA-SPHUB-20260706-001`.

---

## Pré-requisitos

- [x] v4.3 mergeada em `main` (esta PR).
- [x] Migração `2026_07_06_v4_3_manta20_sphub.sql` aplicada no Supabase
      kwuubcnedqtapvykmyye (cria `sp_agent_feed`, `sp_routing_rules`,
      seed de 24 routing rules).
- [ ] `sp_indexer.py` (v4.2) rodando ao menos 1x recentemente — precisa
      existir `sp_index` populado para o `delta_sync` ter o que
      comparar. Se `sp_indexer.py` ainda vive num repo separado
      ("Claude Code repo"), aponte `SP_INDEXER_PATH` para ele.

---

## Fase 2 — Ativação do delta sync

### Passo 1. Instalar as dependências no VPS

```bash
cd /opt/manta-hub                 # ou wherever este repo mora
python -m venv .venv
. .venv/bin/activate
pip install supabase pytest       # supabase-py + pytest para smoke
```

### Passo 2. Configurar env vars

```bash
sudo tee /etc/manta/sp_hub.env <<'EOF'
SUPABASE_URL=https://kwuubcnedqtapvykmyye.supabase.co
SUPABASE_SERVICE_KEY=<pegar do painel Supabase>
SP_HUB_RAG_ENDPOINT=                       # deixar vazio nesta fase
SP_HUB_DELTA_LIMIT=1000
SP_INDEXER_PATH=/opt/manta-legacy/sp_indexer.py   # opcional
SP_HUB_VENV=/opt/manta-hub/.venv
EOF
sudo chmod 600 /etc/manta/sp_hub.env
```

### Passo 3. Primeira execução manual (dry-run mental)

```bash
set -a; . /etc/manta/sp_hub.env; set +a
cd /opt/manta-hub
python -m sp_hub.delta_sync
```

Saída esperada:
```
[success] Δ=<N> feed=<M> rag=0 err=0 in 1.34s
```

Onde:
- Δ (`changes_detected`) = docs em `sp_index` com `updated_at > último sync com status='success'`.
  Na primeira run, o baseline é epoch (1970-01-01), então varre tudo o que
  o `sp_indexer` já indexou.
- feed (`feed_entries_inserted`) = linhas gravadas em `sp_agent_feed` (uma por par doc×agente).
- rag = 0 porque `SP_HUB_RAG_ENDPOINT` está vazio (Noop bridge).

Verificar no Supabase:
```sql
SELECT agent_code, count(*), max(detected_at) 
  FROM sp_agent_feed WHERE status='pending' GROUP BY agent_code;
```
Deve mostrar M1..M18 com contagens plausíveis.

### Passo 4. Configurar o cron

```bash
sudo tee /etc/cron.hourly/sp_hub <<'EOF'
#!/usr/bin/env bash
set -a; . /etc/manta/sp_hub.env; set +a
/opt/manta-hub/sp_hub/daily_index.sh >> /var/log/sp_hub.log 2>&1
EOF
sudo chmod +x /etc/cron.hourly/sp_hub
```

### Passo 5. Validação com M1, M3, M8 (checklist Fase 2 da spec)

Rodar prompts de teste no Maestro:

| Agente | Prompt | Esperado |
|--------|--------|----------|
| M1 Claims | "Manta 20, tem TAC novo no cliente CCR?" | Devolve linhas do `sp_agent_feed` com `agent_code='M1'` + `doc_type='aditivo_contrato'` (via rule `name_tac`). |
| M3 Rodovias | "Tem projeto DWG novo nesta semana?" | Devolve entries com `agent_code='M3'` + `doc_type ∈ {projeto, projeto_cad}` — vem de `cliente_projeto` OU `ext_dwg_dxf`. |
| M8 BD | "Novos editais para responder?" | Entries com `agent_code='M8'` + `doc_type ∈ {edital, proposta, per}`. |

Cada validação bem-sucedida marca o item correspondente no checklist v4.3.

---

## Fase 3 — RAG bridge (Manta 18)

### Passo 1. Definir o endpoint do M18

Duas opções:

**A. HTTP direto** (recomendada se o M18 tem um endpoint sempre disponível):
```
SP_HUB_RAG_ENDPOINT=https://m18.internal.mantaassociados.com
```
O `delta_sync` faz `POST {endpoint}/api/ingest` com payload
`{doc_id, doc_path, doc_name, doc_type, file_ext, drive_id, priority, target_agents}`.

**B. Fila Supabase** (recomendada quando o M18 tem cron próprio e não HTTP):
Não seta `SP_HUB_RAG_ENDPOINT`; em vez disso, injeta `QueueRagBridge`
manualmente:

```python
from sp_hub.db import supabase_client
from sp_hub.delta_sync import run_delta_sync
from sp_hub.rag_bridge import QueueRagBridge

client = supabase_client()
run_delta_sync(client, rag_bridge=QueueRagBridge(client))
```

Requer que exista a tabela `rag_ingest_queue` (não coberta pela migração
v4.3 — criar em migração separada quando adotar a opção B).

### Passo 2. Smoke test

```bash
export SP_HUB_RAG_ENDPOINT=https://m18.internal.mantaassociados.com
python -m sp_hub.delta_sync
```

Esperado: `rag=<K>` onde K = número de decisões `priority='alta'`.

Verificar no M18 se os docs chegaram (endpoint `/api/documents/recent`
ou equivalente).

---

## Fase 3 — Gateway de escrita

### Passo 1. Criar o Zap no Zapier

- **Trigger**: Webhook by Zapier — Catch Raw Hook.
- **Action 1**: Microsoft OneDrive/SharePoint (ou HTTP request custom
  para `PUT https://graph.microsoft.com/v1.0/drives/{{drive_id}}/root:/{{path}}:/content`).
- **Payload esperado** (JSON):
  ```json
  {
    "drive_id": "b!...",
    "path": "/04_IA/outputs/arquivo.pdf",
    "content_type": "application/pdf",
    "content_b64": "<base64>",
    "metadata": {"origem": "M1", "ticket": "MANTA-123"}
  }
  ```
- **Response**: Retornar `{file_id, web_url}` da Graph API.

### Passo 2. Configurar o webhook URL

```bash
sudo sed -i 's|^SP_HUB_ZAPIER_WRITE_WEBHOOK=.*|SP_HUB_ZAPIER_WRITE_WEBHOOK=https://hooks.zapier.com/hooks/catch/xxxxx/yyyyy/|' /etc/manta/sp_hub.env
```

### Passo 3. Smoke test

```python
import base64
from sp_hub.db import supabase_client
from sp_hub.models import WriteRequest
from sp_hub.write_gateway import WriteGateway

gw = WriteGateway(supabase_client())
result = gw.write(WriteRequest(
    drive_id="b!7wlZlI7tWU2o09im0xX4dSggtXaRRJ5LktNsMxjSZr8OGwV61sTwTqLCB0pYNM1D",
    path="/04_IA/outputs/smoke_test.txt",
    content_b64=base64.b64encode(b"hello from SP Hub").decode("ascii"),
    content_type="text/plain",
    metadata={"origem": "smoke_test"},
))
print(result)
```

Verificar:
1. Arquivo aparece no SP em `04_IA/outputs/smoke_test.txt`.
2. Linha em `sp_sync_log` com `sync_type='write'`, `status='success'`.
3. Próxima execução do `sp_indexer.py` pega o arquivo e o inclui em `sp_index`.

---

## Rollback

- **Desligar cron**: `sudo rm /etc/cron.hourly/sp_hub`.
- **Zerar feed pendente** (dev only):
  ```sql
  UPDATE sp_agent_feed SET status='cancelled' WHERE status='pending';
  ```
- **Desativar RAG bridge**: unset `SP_HUB_RAG_ENDPOINT`.
- **Desativar escrita**: unset `SP_HUB_ZAPIER_WRITE_WEBHOOK`.

Nenhum drop de tabela — a migração v4.3 traz um bloco DOWN comentado só
para casos extremos.

---

## R7 — Selo de qualidade

| Selo | Como validar |
|------|--------------|
| ★☆☆ Básico | `M20.search()` reativa devolve lista de docs. |
| ★★☆ Padrão | `delta_sync` roda no cron; `sp_agent_feed` cresce; agentes M1/M3/M8 encontram docs pendentes. |
| ★★★ Avançado | ★★☆ + `rag=<K>` maior que zero + M18 responde queries usando docs recém-indexados + validação humana de 3 respostas. |

---

## Métricas de saúde (dashboards sugeridos)

```sql
-- Rate de sync
SELECT date_trunc('hour', completed_at) as bucket,
       count(*) filter (WHERE status='success') AS ok,
       count(*) filter (WHERE status='error') AS err
  FROM sp_sync_log
 WHERE sync_type='delta'
   AND completed_at > now() - interval '7 days'
 GROUP BY 1 ORDER BY 1;

-- Backlog por agente
SELECT agent_code, priority, count(*)
  FROM sp_agent_feed
 WHERE status='pending'
 GROUP BY agent_code, priority
 ORDER BY agent_code, priority;

-- Rules mais acionadas
SELECT rule_name, count(*)
  FROM (
    SELECT jsonb_array_elements_text(metadata->'matched_rules') AS rule_name
      FROM sp_agent_feed
     WHERE detected_at > now() - interval '7 days'
  ) t
 GROUP BY rule_name ORDER BY 2 DESC;
```
