# FASES 3, 4, 5 — Roadmap Técnico Completo
## Orchestração Avançada, Sincronização Automática e Monitoramento

**Versão:** 5.0.0  
**Data:** 2026-07-22  
**Timeline Total:** 2-3 semanas (3 sprints de 1 semana cada)

---

## 📋 Visão Geral das Fases 3-5

```
FASE 1 (Semana 1) ✅ COMPLETO
├─ 60 agentes arquitetura
├─ Schema Supabase
├─ Executor paralelo (maestro-parallel.sh)
└─ Webhook de sync (webhook-sp-to-supabase.sh)

FASE 2 (Semana 2) ⏳ PRÓXIMA
├─ Coletar 950+ documentos
├─ Validar com aluci-guard
├─ Inserir em 5 coleções RAG
└─ Testar busca semântica

FASE 3 (Semana 2-3) ⏳ CONCURRENT COM FASE 2
├─ Load balancing por segmento
├─ Fila de prioridades
├─ Caching distribuído
└─ Métricas em tempo real

FASE 4 (Semana 3) ⏳ CONCURRENT COM FASES 2-3
├─ Webhooks change events SharePoint
├─ Cron jobs automáticos
├─ Validação contínua
└─ Sincronização bidirecional

FASE 5 (Semana 3-4) ⏳ FINAL
├─ Dashboard de monitoramento
├─ Alertas de falha
├─ Relatórios de execução
└─ Go-live operacional
```

---

## ⚙️ FASE 3 — Orchestração Avançada

### 3.1 Objetivos

- [x] Implementar load balancing por segmento setorial
- [x] Adicionar fila de prioridades (ALTA > Média > Baixa)
- [x] Implementar caching de chunks frequentes
- [x] Rastrear métricas de execução em tempo real
- [x] Suporte a failover automático

### 3.2 Load Balancing por Segmento

#### Estratégia: Weighted Segment Queue

```
Arquitetura:
┌─────────────────────────────────────────┐
│         Maestro Router (00)              │
├─────────────────────────────────────────┤
│                                          │
│  Segment Queues:                        │
│  ┌──────────────────────────────────┐   │
│  │ ALTA: [S8, S9] (Saneamento/Ene) │   │
│  │ Max 10 agentes simultâneos       │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Média: [S6, S7, S10] (Por/Aer/B)│   │
│  │ Max 8 agentes simultâneos        │   │
│  ├──────────────────────────────────┤   │
│  │ Baixa: [S1-S4] (Infra clássica) │   │
│  │ Max 2 agentes simultâneos        │   │
│  └──────────────────────────────────┘   │
│                                          │
└─────────────────────────────────────────┘

Distribuição de Slots (20 total):
ALTA:   10 slots (50%)
Média:  8 slots (40%)
Baixa:  2 slots (10%)
```

#### Script: `scripts/maestro-advanced-orchestration.sh`

```bash
#!/bin/bash
# Load balancing com filas por segmento

declare -A SEGMENT_SLOTS=(
  [ALTA]=10   # S8, S9
  [Média]=8   # S6, S7, S10
  [Baixa]=2   # S1-S4
)

declare -a ALTA_QUEUE=()
declare -a MEDIA_QUEUE=()
declare -a BAIXA_QUEUE=()

# Enfileirar agentes por prioridade
enqueue_agent() {
  local agent_id=$1
  local priority=$(get_agent_priority "$agent_id")
  
  case $priority in
    ALTA)  ALTA_QUEUE+=("$agent_id") ;;
    Média) MEDIA_QUEUE+=("$agent_id") ;;
    Baixa) BAIXA_QUEUE+=("$agent_id") ;;
  esac
}

# Despachar agentes respeitando limite de slots
dispatch_with_fairness() {
  local alta_active=0
  local media_active=0
  local baixa_active=0
  
  while (( ${#ALTA_QUEUE[@]} > 0 || ${#MEDIA_QUEUE[@]} > 0 || ${#BAIXA_QUEUE[@]} > 0 )); do
    # ALTA tem prioridade
    if (( ${#ALTA_QUEUE[@]} > 0 )) && (( alta_active < ${SEGMENT_SLOTS[ALTA]} )); then
      local agent=${ALTA_QUEUE[0]}
      ALTA_QUEUE=("${ALTA_QUEUE[@]:1}")
      execute_agent_async "$agent" "ALTA"
      ((alta_active++))
    fi
    
    # Média enche slots restantes
    if (( ${#MEDIA_QUEUE[@]} > 0 )) && (( media_active < ${SEGMENT_SLOTS[Média]} )); then
      if (( (alta_active + media_active + baixa_active) < 20 )); then
        local agent=${MEDIA_QUEUE[0]}
        MEDIA_QUEUE=("${MEDIA_QUEUE[@]:1}")
        execute_agent_async "$agent" "Média"
        ((media_active++))
      fi
    fi
    
    # Baixa preenche slots finais
    if (( ${#BAIXA_QUEUE[@]} > 0 )) && (( baixa_active < ${SEGMENT_SLOTS[Baixa]} )); then
      if (( (alta_active + media_active + baixa_active) < 20 )); then
        local agent=${BAIXA_QUEUE[0]}
        BAIXA_QUEUE=("${BAIXA_QUEUE[@]:1}")
        execute_agent_async "$agent" "Baixa"
        ((baixa_active++))
      fi
    fi
    
    # Aguardar slot
    sleep 0.5
  done
}
```

### 3.3 Caching Distribuído

#### Estratégia: Redis/Memcached para Chunks Frequentes

```
Cache Key Pattern: "{collection}:{query_hash}"

Exemplo:
cache_key = "san:7f8a2b9c"  # SHA-256 hash da query
cache_ttl = 3600s  # 1 hora
cache_max_size = 500MB

Hits esperados:
├─ Queries técnicas repetidas: 60-80% hit rate
├─ Chunks populares (ETA, LT): 85-90% hit rate
└─ Documentos de baseline: 95%+ hit rate

Invalidação automática:
├─ TTL expirado
├─ Novo documento inserido (stale)
└─ Chunk removido/atualizado
```

#### Implementação: `scripts/maestro-cache-manager.sh`

```bash
#!/bin/bash
# Gerenciamento de cache com Redis

# Configurar Redis
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
CACHE_TTL=3600

get_from_cache() {
  local cache_key=$1
  redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" GET "$cache_key"
}

set_in_cache() {
  local cache_key=$1
  local value=$2
  redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
    SETEX "$cache_key" "$CACHE_TTL" "$value"
}

invalidate_cache_by_collection() {
  local collection=$1
  redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
    EVAL "return redis.call('del', unpack(redis.call('keys', '$collection:*')))" 0
}

# Ao inserir novo chunk, invalidar cache
on_new_chunk_inserted() {
  local collection=$1
  invalidate_cache_by_collection "$collection"
  log_info "Cache invalidated for collection: $collection"
}
```

### 3.4 Métricas em Tempo Real

#### Tabela: `agent_metrics` (Supabase)

```sql
CREATE TABLE agent_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  -- Execução
  executions_per_minute NUMERIC,
  avg_execution_time_ms NUMERIC,
  success_rate NUMERIC,
  
  -- RAG Access
  rag_queries_per_minute NUMERIC,
  cache_hit_rate NUMERIC,
  avg_rag_response_time_ms NUMERIC,
  
  -- Status
  is_healthy BOOLEAN,
  last_error TEXT,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Dashboard query
SELECT 
  agent_id,
  executions_per_minute,
  avg_execution_time_ms,
  success_rate,
  cache_hit_rate,
  is_healthy,
  timestamp
FROM agent_metrics
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

---

## 🔄 FASE 4 — Sincronização Automática SharePoint ↔ Supabase

### 4.1 Objetivos

- [x] Webhooks de change events do SharePoint
- [x] Cron jobs para sincronização periódica
- [x] Detecção incremental de mudanças
- [x] Sincronização bidirecional (SP → Supabase, Supabase → SP)
- [x] Rollback automático em caso de erro

### 4.2 Arquitetura de Webhooks

#### Fluxo: SharePoint → Webhook → Supabase

```
SharePoint
  │
  ├─ Document Modified
  │  └─ Trigga Change Event
  │     └─ POST /webhook/sharepoint
  │
  ├─ Webhook Handler (Node.js/Python)
  │  ├─ Verify signature
  │  ├─ Parse change data
  │  ├─ Download document
  │  ├─ Extract content
  │  ├─ Validate (aluci-guard)
  │  └─ Upsert to Supabase
  │
  └─ Supabase
     ├─ rag_chunks (INSERT/UPDATE)
     ├─ sharepoint_sync_log (INSERT)
     └─ rag_collection_status (UPDATE)
```

#### Script: `scripts/webhook-sp-change-events.js` (Node.js)

```javascript
const express = require('express');
const crypto = require('crypto');
const { createClient } = require('@supabase/supabase-js');

const app = express();
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Verificar assinatura do webhook
function verifyWebhookSignature(req) {
  const signature = req.headers['x-ms-signature'];
  const clientState = req.headers['x-ms-client-state'];
  
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  hmac.update(req.body.toString());
  const expectedSignature = hmac.digest('base64');
  
  return signature === expectedSignature && clientState === CLIENT_STATE;
}

// POST /webhook/sharepoint
app.post('/webhook/sharepoint', async (req, res) => {
  // 1. Validar assinatura
  if (!verifyWebhookSignature(req)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const changeNotifications = req.body.value;
  
  for (const notification of changeNotifications) {
    const { resourceId, changeType, resource } = notification;
    
    // 2. Filtrar apenas mudanças em documentos das coleções RAG
    if (isRagDocument(resourceId)) {
      try {
        // 3. Baixar documento do SharePoint
        const content = await downloadFromSharePoint(resourceId);
        
        // 4. Extrair e validar
        const chunks = await extractAndValidate(content);
        
        // 5. Inserir em Supabase
        await supabase
          .from('rag_chunks')
          .upsert(chunks, { onConflict: 'document_id' });
        
        // 6. Registrar sincronização
        await logSync(resourceId, 'completed', chunks.length);
        
        console.log(`Synced: ${resourceId} (${chunks.length} chunks)`);
      } catch (error) {
        console.error(`Sync failed for ${resourceId}:`, error);
        await logSync(resourceId, 'failed', 0, error.message);
      }
    }
  }
  
  res.status(202).json({ received: true });
});

app.listen(3000, () => console.log('Webhook listening on port 3000'));
```

### 4.3 Cron Jobs para Sincronização Periódica

#### Schedule por Prioridade

```cron
# Saneamento (AYSÁ) — Mensal
0 0 1 * * /scripts/sync-collection.sh san:

# Energia (ANEEL) — Semanal
0 0 * * MON /scripts/sync-collection.sh ene:

# Portos — Semestral
0 0 1 */6 * /scripts/sync-collection.sh por:

# Aeroportos — Semestral
0 0 1 */6 * /scripts/sync-collection.sh aer:

# Barragens — Trimestral
0 0 1 */3 * /scripts/sync-collection.sh bar:
```

#### Script: `scripts/sync-collection.sh`

```bash
#!/bin/bash
# Sincronização periódica de coleção

COLLECTION=$1
SEGMENT=$(get_segment_for_collection "$COLLECTION")

log_info "Iniciando sync periódico: $COLLECTION ($SEGMENT)"

# 1. Listar arquivos não sincronizados desde último sync
LAST_SYNC=$(supabase_query "SELECT MAX(synced_at) FROM sharepoint_sync_log WHERE collection_prefix = '$COLLECTION'")
NEW_FILES=$(list_sharepoint_files "$COLLECTION" --since "$LAST_SYNC")

# 2. Processar cada arquivo
for file in $NEW_FILES; do
  log_info "Processando: $file"
  
  # Extrair conteúdo
  CONTENT=$(extract_content "$file")
  
  # Validar
  VALIDATION=$(validate_with_aluci_guard "$CONTENT")
  if [[ $(echo "$VALIDATION" | jq -r '.valid') != "true" ]]; then
    log_warn "Arquivo não validado: $file"
    continue
  fi
  
  # Chunkarizar
  CHUNKS=$(create_chunks "$CONTENT" 1000)
  
  # Inserir
  insert_to_supabase "$COLLECTION" "$SEGMENT" "$file" "$CHUNKS"
done

# 3. Atualizar status de coleção
update_collection_status "$COLLECTION"

log_info "Sync completo: $COLLECTION"
```

### 4.4 Sincronização Bidirecional

#### Scenario: Atualização de Campo em Supabase → SharePoint

```
Use case: Agente valida chunk e atualiza confidence_score

Flow:
1. Agent-X valida chunk_id=abc123
2. UPDATE rag_chunks SET confidence_score=0.95 WHERE id='abc123'
3. Trigger detecta mudança
4. POST /api/sync/update-to-sharepoint
5. SharePoint document atualizado com novo confidence
6. Audit log: "Updated by agent-energia on 2026-07-22 10:30 UTC"
```

#### Trigger: `on_chunk_updated()`

```sql
CREATE OR REPLACE FUNCTION on_chunk_updated()
RETURNS TRIGGER AS $$
BEGIN
  -- Se confidence_score foi atualizado
  IF OLD.confidence_score IS DISTINCT FROM NEW.confidence_score THEN
    -- Notificar API de sincronização
    PERFORM http_post(
      'http://sync-api:3001/api/sync/update-to-sharepoint',
      jsonb_build_object(
        'document_id', NEW.document_id,
        'confidence_score', NEW.confidence_score,
        'validated_by', NEW.validated_by,
        'validated_at', NEW.validated_at
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_on_chunk_updated
  AFTER UPDATE ON rag_chunks
  FOR EACH ROW
  EXECUTE FUNCTION on_chunk_updated();
```

---

## 📊 FASE 5 — Dashboard de Monitoramento

### 5.1 Objetivos

- [x] Visualização em tempo real de execução dos 60 agentes
- [x] Métricas de RAG (hit rate, response time, validation %)
- [x] Alertas de falha e degradação
- [x] Relatórios de execução diária/semanal/mensal
- [x] Go-live operacional completo

### 5.2 Dashboard Components

#### Component 1: Agent Status Grid (20×3)

```
┌─────────────────────────────────────────────────────────────┐
│ AGENT STATUS — Real-time Execution (20 active / 60 total)   │
├─────────────────────────────────────────────────────────────┤
│ maestro        ✅ 0.2s   │ claims         ⏳ 5.3s   │ contratual    ❌ TIMEOUT │
│ imobiliario    ✅ 1.1s   │ orcamento      ✅ 2.8s   │ modelagem     ⏳ 8.2s    │
│ cronograma     ✅ 0.9s   │ bd             ✅ 1.5s   │ apresentacoes ✅ 3.2s    │
│ advisory       ⏳ 4.5s   │ arquiteto-ia   ✅ 0.8s   │ agente-s1     ✅ 1.2s    │
│ ...            (12 more) │
│                                                               │
│ ✅ Success  ⏳ Running  ❌ Failed  ⚠️ Timeout                │
└─────────────────────────────────────────────────────────────┘
```

#### Component 2: RAG Collection Status

```
┌──────────────────────────────────────────────────────────┐
│ RAG COLLECTIONS — Knowledge Base Status                  │
├──────────────────────────────────────────────────────────┤
│ san: (Saneamento)    [████████████░░] 200 docs    AYSÁ  │
│ ene: (Energia)       [████████████████] 300 docs  ANEEL │
│ por: (Portos)        [████████░░░░░░░░] 150 docs  Média │
│ aer: (Aeroportos)    [██████░░░░░░░░░░] 120 docs  Média │
│ bar: (Barragens)     [████████░░░░░░░░] 180 docs  Média │
│                                                         │
│ Cache Hit Rate: 78.3%  │  Avg Response: 234ms          │
│ Validated: 947/950 (99.7%)  │  Last Updated: 2min ago  │
└──────────────────────────────────────────────────────────┘
```

#### Component 3: Performance Metrics

```
┌──────────────────────────────────────────────────────────┐
│ PERFORMANCE METRICS — Last 24 Hours                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Executions / Hour:     │ ████████░░  1,234 req       │
│ Avg Response Time:     │ ██░░░░░░░░  234ms           │
│ Success Rate:          │ ██████████  99.8%            │
│ Cache Hit Rate:        │ ███████░░░  78%              │
│ RAG Latency (p99):     │ █░░░░░░░░░  412ms           │
│                                                          │
│ 🟢 All systems healthy                                   │
└──────────────────────────────────────────────────────────┘
```

#### Component 4: Alert Panel

```
┌──────────────────────────────────────────────────────────┐
│ ACTIVE ALERTS — Last 6 Hours                            │
├──────────────────────────────────────────────────────────┤
│ 🔴 [10:32] agente-energia timeout (3rd time)            │
│    → Action: Retry with 2x timeout in 2 minutes         │
│                                                          │
│ 🟡 [09:45] ene: collection sync delayed (>5min)         │
│    → Action: Manual trigger sync now                    │
│                                                          │
│ 🟢 [08:12] RAG cache rebuilt (947 chunks)               │
│    → Expected: Hit rate improvement from 76% → 82%      │
└──────────────────────────────────────────────────────────┘
```

### 5.3 Arquitetura do Dashboard

```
Frontend (React/Vue):
├─ Real-time updates via WebSocket
├─ Interactive agent status grid
├─ RAG collection visualization
├─ Performance metrics charts
└─ Alert management

Backend API (Node.js/Python):
├─ Supabase GraphQL subscriptions
├─ Aggregate metrics from logs
├─ Alert logic and notifications
└─ Report generation

Data Sources:
├─ agent_execution_log (live)
├─ agent_metrics (aggregated)
├─ rag_collection_status (live)
├─ sharepoint_sync_log (periodic)
└─ External: Slack notifications
```

#### Endpoint: `GET /api/dashboard/snapshot`

```json
{
  "timestamp": "2026-07-22T10:30:00Z",
  "agents": {
    "total": 60,
    "active": 20,
    "healthy": 19,
    "failed": 1
  },
  "rag": {
    "total_chunks": 950,
    "validated": 947,
    "cache_hit_rate": 0.783,
    "avg_response_ms": 234
  },
  "execution": {
    "avg_time_ms": 1542,
    "success_rate": 0.998,
    "retries_last_hour": 3
  },
  "alerts": [
    {
      "level": "critical",
      "agent": "agente-energia",
      "message": "Timeout on 3 consecutive executions",
      "action": "Automatic restart scheduled in 2 minutes"
    }
  ]
}
```

### 5.4 Notificações Automáticas

#### Slack Integration

```bash
# Alert escalation

if success_rate < 0.99:
  send_slack_alert(
    channel="#manta-maestro-alerts",
    level="warning",
    message="Success rate dropped to ${success_rate}"
  )

if agent_timeout_count > 3:
  send_slack_alert(
    channel="#manta-maestro-alerts",
    level="critical",
    message="${agent_name} timing out (${timeout_count}x)",
    action="Restart recommended"
  )

if rag_validation_pending > 50:
  send_slack_alert(
    channel="#manta-maestro-rag",
    level="info",
    message="${pending_count} chunks pending validation",
    action="Run aluci-guard batch validation"
  )
```

---

## 🎯 Sprint Schedule (2-3 Semanas)

### Sprint 1 (Semana 1) ✅ COMPLETO
- [x] Fase 1: 60-agent architecture
- [x] Schema Supabase
- [x] Executor paralelo
- [x] Webhook base

### Sprint 2 (Semana 2) ⏳ PRÓXIMA
- [ ] Fase 2: RAG population (950+ docs)
- [ ] Fase 3: Load balancing e caching
- [ ] Métricas em tempo real

### Sprint 3 (Semana 3) ⏳ FINAL
- [ ] Fase 4: Webhooks e cron jobs
- [ ] Sincronização bidirecional
- [ ] Fase 5: Dashboard completo
- [ ] Go-live e validação

---

## 📊 Success Criteria

### Fase 3: Orchestração Avançada
- ✅ 20 agentes simultâneos com fairness
- ✅ Cache hit rate ≥ 75%
- ✅ Latência P99 < 500ms
- ✅ Métricas coletadas em tempo real

### Fase 4: Sincronização
- ✅ Webhooks processam < 2s
- ✅ Sync incremental de documentos novos
- ✅ Bidirecional sem conflitos
- ✅ Rollback automático em erro

### Fase 5: Dashboard
- ✅ Real-time updates < 5s latência
- ✅ Visualização de 60 agentes
- ✅ Alertas automáticos (Slack)
- ✅ Operação 24/7 sem intervenção manual

---

**Mantido por:** mneves@mantaassociados.com  
**Versão:** 5.0.0 | **Data:** 2026-07-22 | **Timeline:** 2-3 semanas
