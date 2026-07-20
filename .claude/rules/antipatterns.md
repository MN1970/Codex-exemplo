# Antipatterns — Recusas e Restrições

## Maestro v5 Forbidden Patterns

### 1. Swarm Autônomo
❌ **RECUSAR**: "Deixa 30 agentes decidirem sozinhos qual faz o trabalho"

**Por quê**: Sem orquestrador central, há race conditions, decisões conflitantes,
auditoria impossível.

**Alternativa**: Hub-and-spoke obrigatório. Maestro (orquestrador) decide rota,
agentes (workers) executam.

---

### 2. LLM em Loop Cron
❌ **RECUSAR**: "Agente roda queries diárias automaticamente sem entrada humana"

**Por quê**: Sem entrada humana, sem gate de parada. Custo imprevisível.

**Alternativa**: APScheduler com script determinístico. Se precisa LLM, é Haiku
(triagem) → output JSON → decisão humana → trigger.

---

### 3. Skill Executando SQL
❌ **RECUSAR**: "Agente executa `INSERT/UPDATE/DELETE` no banco direto"

**Por quê**: Skill não deve ter acesso ao banco. Viola a separação de camadas.

**Alternativa**: Skill → chamada HTTP a service → service → repo → SQL.

---

### 4. Frontend Chamando LLM
❌ **RECUSAR**: "React component importa `Anthropic` SDK e chama Claude direto"

**Por quê**: Expõe chaves API ao client. Sem auditoria. Sem rate limit.

**Alternativa**: Frontend → backend FastAPI → API Anthropic (centralizado).

---

### 5. Prompt Congelado em Código
❌ **RECUSAR**: "System prompt hardcoded em `agent.py` com `"""…"""`"

**Por quê**: Evoluir prompt exige redeploy. Sem versionamento.

**Alternativa**: Prompt em `CLAUDE.md` + skill .md + .env. Versionado em git.

---

### 6. Agente Team sem Auditoria
❌ **RECUSAR**: "Multi-agent framework (AutoGen, Crew) em produção sem logs estruturados"

**Por quê**: Sem log JSON estruturado, impossível auditar decisão. Sem transparência.

**Alternativa**: Hub-and-spoke com JSON estruturado de input/output por agente.
Log em Postgres. Auditoria por query_id.

---

### 7. Opus em Triagem
❌ **RECUSAR**: "Usar Opus 4.7 ($12/1M tokens) para classificar intent"

**Por quê**: Custo 5–10× maior. Latência 5–10× maior. Overkill.

**Alternativa**: Haiku 4.5 triagem (10ms, $0.80/1M tokens). Opus só para decisão final.

---

### 8. Reusable Skill em Production sem Testes
❌ **RECUSAR**: "Skill novo invocado diretamente sem tests/fixtures"

**Por quê**: Skill pode falhar silenciosamente. Sem visibilidade.

**Alternativa**: `pytest tests/skills/test_skill_name.py` antes de usar em prod.

---

### 9. Cache sem TTL
❌ **RECUSAR**: "Redis cache sem expiração"

**Por quê**: Dado obsoleto. Sem invalidação. Memory leak.

**Alternativa**: Sempre TTL. Para RAG: 24h. Para user prefs: 30 dias.

---

### 10. Embedding sem Normalização
❌ **RECUSAR**: "Voyage AI raw embeddings sem reranker para top-K"

**Por quê**: Similarity score bruto é ruim. False positives.

**Alternativa**: BM25 (keywords) + vector (semântica) + reranker (Sonnet) → top-2.

---

## Maestro v5 Approved Patterns

✅ **Hub-and-Spoke** — Orchestrator central + workers (agentes)

✅ **Model Tiering** — Haiku (triagem) → Sonnet (core) → Opus (decisão)

✅ **Deterministic Routing** — metadata → agent específico (não LLM)

✅ **Parallel Execution** — asyncio.gather com timeout

✅ **Structured Logging** — JSON audit log em Postgres

✅ **RAG Hybrid** — SQLite local + MCP fallback + hot reindex

✅ **Gate Humano** — em decisões irreversíveis (orçamento final, contrato)

✅ **Versionamento** — Skill .md + git + CLAUDE.md v5.0

---

## Validação Automática

Checklist antes de invocar agente:

- [ ] Metadata segment/phase extraído? → detectar tipo
- [ ] Intent classificado? → sugerir rotas
- [ ] RAG chunks injetados? → top-2 score ≥70
- [ ] Timeout configurado? → máximo 60s por agente
- [ ] Budget tokens estimado? → Haiku ~300, Sonnet ~2000, Opus ~5000
- [ ] Audit log pronto? → query_id + timestamp + user_id
- [ ] Erro handling? → retry com backoff exponencial (2s, 4s, 8s)

---

**Mantido por**: Manta Arquiteto IA (Manta 16)  
**Versão**: v5.0  
**Criado**: 2026-07-20
