# S6 Go-Live Checklist — Agente-Portos (Manta 03-S6)
**Version: v5.0 | Target Launch: 2026-07-25 | Owner: mneves@mantaassociados.com**

Checklist executável para lançamento de produção do Agente-Portos com 20 fases em 8–16 horas.
**Total de items: 127 | Estimated time: 4–6h | RTO: < 1h**

---

## FASE 0 — PRÉ-VÔO (24h antes — responsabilidade MN)

### Aprovação & Sign-off
- [ ] **MN Review:** CLAUDE.md v5.0 seção "Manta 03-S6 | Portos"
- [ ] **MN Review:** Routing rules R1 para keywords portuários (ANTAQ, molhe, berço, etc.)
- [ ] **MN Review:** RAG collection `por:v5.0:chunks` metadata (2000+ chunks ingestados)
- [ ] **MN Review:** Skill checksum em VERSIONS.json: `agente-portos.v5.0 = b7d3e5a2f1c4`
- [ ] **MN Approval:** Sign-off em `.github/DEPLOYMENT-APPROVALS.md` com timestamp
- [ ] **MN Escalation:** Confirmar contato telefônico direto para < 1h RTO

### Comunicação
- [ ] Enviar email T-24h a time Manta: "S6 Go-Live 2026-07-25 08:00 UTC"
  - Subject: `[GO-LIVE] Manta 03-S6 Agente-Portos v5.0 — 24h antes`
  - Recipients: mneves@, @mantaassociados.com (core team)
  - Anexar: GO-LIVE-RUNBOOK.md, ROLLBACK-PLAN.md (TL;DR)

---

## FASE 1 — PRÉ-DEPLOYMENT VALIDATION (T-6h, ~30 min)

### Code & Config
- [ ] **Git Status:** Repo limpo, sem uncommitted changes
  ```bash
  cd /home/user/Codex-exemplo
  git status
  # Expected: "nothing to commit, working tree clean"
  ```

- [ ] **CLAUDE.md Syntax:** Valida seções P1–P8, R1–R10
  ```bash
  python3 -c "
  import re
  with open('CLAUDE.md') as f:
      text = f.read()
  sections = ['OS 8 PILARES', 'R1 — MAESTRO', 'Manta 03-S6', 'por:v5.0']
  for sec in sections:
      assert sec in text, f'Missing: {sec}'
  print('✓ CLAUDE.md sections OK')
  "
  ```

- [ ] **VERSIONS.json Syntax:**
  ```bash
  python3 -c "import json; json.load(open('VERSIONS.json'))" && echo "✓ JSON valid"
  ```

- [ ] **Skill Checksum Validation:**
  ```bash
  md5sum .claude/agents/agente-portos.v5.0.md | awk '{print $1}'
  # Compare with VERSIONS.json: agente-portos.v5.0.checksum
  ```

- [ ] **Settings.json Pinning:**
  ```bash
  grep -A 20 "skill_version_pin" .claude/settings.json | grep "agente-portos.*v5.0"
  # Expected: "agente-portos": "v5.0"
  ```

### Database (Supabase)
- [ ] **Connection Test:** Valida acesso ao Supabase project
  ```bash
  # Se local Supabase:
  supabase status
  # Expected: "Supabase running" e local server URL
  ```

- [ ] **Schema Validation:** Tabelas `rag_chunks`, `rag_metadata`, `agent_runs`, `agent_feedback`
  ```bash
  # Usar supabase CLI ou SQL client:
  # SELECT table_name FROM information_schema.tables WHERE table_schema='public'
  # Expected tables: agent_runs, agent_feedback, agent_triggers, rag_chunks, rag_metadata, rag_cache
  ```

- [ ] **RLS Policies Check:** Verify Row-Level Security policies existem
  ```bash
  # SELECT * FROM pg_policies WHERE tablename IN ('agent_runs', 'rag_chunks')
  # Expected: >= 1 policy per table
  ```

### RAG Collection (S6 — Portos)
- [ ] **Collection Exists:** `por:v5.0:chunks` criada em Supabase
  ```bash
  # SELECT COUNT(*) FROM rag_chunks WHERE collection LIKE 'por:v5.0%'
  # Expected: >= 2000
  ```

- [ ] **Metadata Validation:** `rag_metadata` for `por:v5.0:*`
  ```bash
  # SELECT DISTINCT collection, version, checksum FROM rag_metadata
  #   WHERE collection LIKE 'por:v5.0%'
  # Expected: >= 50 metadata rows
  ```

- [ ] **Embedding Status:** Todos chunks com embeddings válidos
  ```bash
  # SELECT COUNT(*) FROM rag_chunks
  #   WHERE collection LIKE 'por:v5.0%' AND embedding IS NULL
  # Expected: 0 (nenhum chunk sem embedding)
  ```

- [ ] **Cache Limpo:** `rag_cache` vazio ou TTL expirado para old queries
  ```bash
  # DELETE FROM rag_cache WHERE created_at < NOW() - INTERVAL '7 days'
  # Expected: DELETE successful (or 0 rows if empty)
  ```

### Dependencies & Environment
- [ ] **Python Dependencies:**
  ```bash
  pip install -r requirements.txt --quiet
  # Expected: all packages installed (use venv if available)
  ```

- [ ] **API Keys:** `.env` ou environment vars configurados
  ```bash
  # Validar que existem:
  # - SUPABASE_URL
  # - SUPABASE_KEY
  # - ANTHROPIC_API_KEY (ou similar para LLM)
  # - ELASTICSEARCH_HOST (se usando BM25)
  ```

- [ ] **Elasticsearch (BM25):** Connection test (se aplicável)
  ```bash
  # curl http://localhost:9200/_cat/health
  # Expected: cluster status (green, yellow, red — qualquer um é OK se online)
  ```

### Tests
- [ ] **Routing Tests:** Valida S6 é routed para portuários
  ```bash
  python3 -m pytest tests/routing/test_s6_portos.py -v
  # Expected: >= 8 testes passing (keyword matching, embedding, phase inference)
  ```

- [ ] **RAG Query Tests:**
  ```bash
  python3 -m pytest tests/rag/test_s6_portos_rag.py -v
  # Expected: >= 5 testes (BM25, embedding, reranker, cache)
  ```

- [ ] **Tiering Tests:**
  ```bash
  python3 -m pytest tests/tiering/test_r7_complexity.py -v
  # Expected: >= 3 testes (Haiku < 2000 tokens, Sonnet 2k–10k, Opus > 10k)
  ```

---

## FASE 2 — PRÉ-DEPLOYMENT SIGN-OFF (T-5h, ~15 min)

### Manual Review Gate
- [ ] **Tech Lead Review:** Todos items Fase 1 completos + evidência de teste
  - Criar comment in `.github/DEPLOYMENT-APPROVALS.md` com timestamp
  - Format: `[PHASE-1-PASS] 2026-07-25T10:00:00Z — <reviewer name>`

- [ ] **MN Final Approval:** Confirma launch pode prosseguir
  - [ ] MN confirma por email ou Slack `#agent-ops`: "Approved for S6 go-live T-5h"
  - [ ] If MN não responder em 1h → escalate (fallback contact)

---

## FASE 3 — DATABASE MIGRATIONS (T-4h, ~30 min)

### Schema Changes (Supabase)
- [ ] **Create `agent_runs` table** (se não existe)
  ```sql
  CREATE TABLE IF NOT EXISTS agent_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    model_tier TEXT DEFAULT 'sonnet',
    input_tokens INT,
    output_tokens INT,
    cost_usd NUMERIC(10, 6),
    latency_ms INT,
    status TEXT CHECK (status IN ('success', 'timeout', 'error')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] **Create `agent_feedback` table** (se não existe)
  ```sql
  CREATE TABLE IF NOT EXISTS agent_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES agent_runs(run_id),
    user_id TEXT,
    score INT CHECK (score BETWEEN 0 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] **Create `agent_triggers` table** (APScheduler persist)
  ```sql
  CREATE TABLE IF NOT EXISTS agent_triggers (
    trigger_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cron_expression TEXT,
    run_once_at TIMESTAMP,
    enabled BOOLEAN DEFAULT TRUE,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] **Create Indexes para Performance**
  ```sql
  CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_id ON agent_runs(agent_id);
  CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at ON agent_runs(created_at DESC);
  CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection ON rag_chunks(collection);
  CREATE INDEX IF NOT EXISTS idx_rag_cache_created_at ON rag_cache(created_at);
  ```

- [ ] **Enable RLS (Row-Level Security)**
  ```sql
  ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
  ALTER TABLE agent_feedback ENABLE ROW LEVEL SECURITY;
  -- Policy: usuários veem apenas seus próprios runs
  CREATE POLICY read_own_runs ON agent_runs
    FOR SELECT USING (user_id = auth.uid()::text OR auth.role() = 'service_role');
  ```

### Migration Execution
- [ ] **Run Migrations via Supabase CLI** (preferred)
  ```bash
  supabase migration new create_agent_tables
  # Edit migration file com SQL acima
  supabase migration up
  ```

- [ ] **Or via SQL Client** (if no CLI)
  ```bash
  # Import SQL script via pgAdmin ou psql:
  psql -h <SUPABASE_HOST> -U postgres -d postgres -f migrations/s6_go_live.sql
  ```

- [ ] **Validate Migration Success**
  ```bash
  # SELECT table_name FROM information_schema.tables WHERE table_schema='public'
  # Expected: agent_runs, agent_feedback, agent_triggers, rag_chunks, rag_metadata, rag_cache
  ```

- [ ] **Backup Post-Migration**
  ```bash
  # Backup Supabase usando pg_dump:
  pg_dump -h <HOST> -U postgres postgres > backups/supabase_post_s6_phase3_$(date +%s).sql
  ```

---

## FASE 4 — BACKGROUND TASKS SETUP (T-3h, ~45 min)

### APScheduler Configuration
- [ ] **APScheduler Installation**
  ```bash
  pip install apscheduler
  ```

- [ ] **Create APScheduler Script**
  ```bash
  # scripts/start_scheduler.py
  cat > scripts/start_scheduler.py << 'EOF'
  from apscheduler.schedulers.background import BackgroundScheduler
  import atexit
  import logging

  logging.basicConfig()
  logging.getLogger('apscheduler').setLevel(logging.INFO)

  scheduler = BackgroundScheduler()

  # R7: RAG reindex daily
  scheduler.add_job(
      func=rag_reindex_job,
      trigger="cron",
      hour=2, minute=0,
      id='rag_reindex_daily',
      name='RAG Reindex (daily 02:00 UTC)'
  )

  # R9: Embedding retrain (Sunday)
  scheduler.add_job(
      func=embedding_retrain_job,
      trigger="cron",
      day_of_week='sun', hour=3, minute=0,
      id='embedding_retrain_weekly',
      name='Embedding Retrain (weekly Sunday 03:00 UTC)'
  )

  # R10: Memory purge (daily)
  scheduler.add_job(
      func=memory_purge_job,
      trigger="cron",
      hour=3, minute=30,
      id='memory_purge_daily',
      name='Memory Purge (daily 03:30 UTC)'
  )

  scheduler.start()
  atexit.register(lambda: scheduler.shutdown())
  print("APScheduler started")
  EOF
  ```

- [ ] **Create Job Functions** (scripts/scheduler_jobs.py)
  ```python
  import supabase
  import logging

  logger = logging.getLogger(__name__)

  def rag_reindex_job():
      """R7: Reindex RAG collections daily"""
      logger.info("Starting RAG reindex")
      # TODO: Implement reindex logic
      logger.info("RAG reindex complete")

  def embedding_retrain_job():
      """R9: Retrain embeddings weekly from high-scoring feedback"""
      logger.info("Starting embedding retrain")
      # TODO: Fetch feedback score >= 4, retrain embedding
      logger.info("Embedding retrain complete")

  def memory_purge_job():
      """R10: Purge agent memory if > 100MB or > 30 days"""
      logger.info("Starting memory purge")
      # TODO: Delete old memory chunks
      logger.info("Memory purge complete")
  ```

### Systemd Service (Production)
- [ ] **Create Systemd Unit File** (`/etc/systemd/system/manta-scheduler.service`)
  ```ini
  [Unit]
  Description=Manta APScheduler Background Tasks
  After=network.target

  [Service]
  Type=simple
  User=manta
  WorkingDirectory=/home/manta/Codex-exemplo
  ExecStart=/usr/bin/python3 -m scripts.start_scheduler
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] **Enable & Start Service**
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable manta-scheduler
  sudo systemctl start manta-scheduler
  sudo systemctl status manta-scheduler
  # Expected: "active (running)"
  ```

- [ ] **Verify Logs**
  ```bash
  sudo journalctl -u manta-scheduler -f
  # Expected: "APScheduler started"
  ```

### Docker Setup (Alternative)
- [ ] **Create Dockerfile** (se preferred)
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["python3", "-m", "scripts.start_scheduler"]
  ```

- [ ] **Build & Run**
  ```bash
  docker build -t manta-scheduler:v5.0 .
  docker run -d --name manta-scheduler \
    -e SUPABASE_URL=$SUPABASE_URL \
    -e SUPABASE_KEY=$SUPABASE_KEY \
    manta-scheduler:v5.0
  ```

---

## FASE 5 — SKILL DEPLOYMENT (T-2h, ~30 min)

### Skill Files
- [ ] **Verify Skill Exists:** `.claude/agents/agente-portos.v5.0.md`
  ```bash
  ls -lh .claude/agents/agente-portos.v5.0.md
  # Expected: file exists, size > 10KB
  ```

- [ ] **Checksum Validation:** MD5 match com VERSIONS.json
  ```bash
  actual=$(md5sum .claude/agents/agente-portos.v5.0.md | awk '{print $1}')
  expected=$(grep -A 5 '"v5.0"' VERSIONS.json | grep checksum | awk -F'"' '{print $4}')
  [ "$actual" = "$expected" ] && echo "✓ Checksum match" || echo "✗ Mismatch!"
  ```

- [ ] **Backup Old Version:** Arquivar v4.9
  ```bash
  [ -f .claude/agents/agente-portos.v4.9.md ] && \
    cp .claude/agents/agente-portos.v4.9.md .claude/agents/.backup/agente-portos.v4.9.md.$(date +%s)
  ```

- [ ] **Settings.json Pinning:** Confirm v5.0 pin
  ```bash
  jq '.skill_version_pin."agente-portos"' .claude/settings.json
  # Expected: "v5.0"
  ```

### Linked Documentation
- [ ] **Skill Linked to RAG:** Verify `por:v5.0:chunks` referenciada em agente-portos.v5.0.md
  ```bash
  grep -i "por:v5.0" .claude/agents/agente-portos.v5.0.md
  # Expected: >= 1 match (e.g., "rag_collection: por:v5.0:*")
  ```

- [ ] **VERSIONS.json Linked:** Checksum + deprecation noted
  ```bash
  jq '.agente-portos' VERSIONS.json | head -20
  # Expected: v5.0 + checksum, v4.9 marked deprecated_at
  ```

---

## FASE 6 — MAESTRO ROUTING RULES (T-1h 30m, ~30 min)

### Keyword Rules (R1)
- [ ] **Verify S6 Keywords in maestro.v5.0.md:**
  ```bash
  grep -A 10 "# S6 — PORTOS" .claude/agents/maestro.v5.0.md
  # Expected: {porto|terminal|ANTAQ|dragagem|molhe|berço|...}
  ```

- [ ] **Confidence Score Formula Exists:**
  ```bash
  grep -A 20 "score = 0.4 × keyword_relevance" CLAUDE.md
  # Expected: confidence score formula
  ```

### Embedding Model
- [ ] **Embedding Model Available:** Infinity (Hugging Face) ou similar
  ```bash
  # Test embedding endpoint:
  curl -s http://localhost:8000/embed \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"text": "porto ANTAQ terminal"}' | jq .
  # Expected: embeddings array
  ```

- [ ] **Test Embedding Similarity (S6 vs Other Segments)**
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
  prompt = "Projeto de terminal portuário em Santos com dragagem"
  embedding = model.encode(prompt)
  # Test similarity:
  # - agente-portos: expected > 0.85
  # - agente-saneamento: expected < 0.5
  # - agente-energia: expected < 0.4
  ```

### BM25 Index
- [ ] **BM25 Index Built:** `por:v5.0:*` indexed in Elasticsearch/similar
  ```bash
  # Elasticsearch query:
  curl -s http://localhost:9200/por_v5.0/_count | jq .count
  # Expected: > 2000 (number of chunks indexed)
  ```

- [ ] **Test BM25 Query:**
  ```bash
  curl -s -X GET "localhost:9200/por_v5.0/_search" \
    -H 'Content-Type: application/json' \
    -d '{"query": {"match": {"text": "ANTAQ dragagem"}}, "size": 5}' | jq .hits.total
  # Expected: >= 1 hit
  ```

### Reranker (R6)
- [ ] **Reranker Model Available:** Cross-encoder fine-tuned
  ```bash
  # Test reranker endpoint:
  curl -s http://localhost:8001/rerank \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "query": "dragagem de canal de acesso",
      "texts": ["chunk1 about dragagem", "chunk2 about energia"]
    }' | jq .
  # Expected: scores array [0.92, 0.15]
  ```

---

## FASE 7 — TIERING & FALLBACK SETUP (T-1h, ~30 min)

### R7: Complexity Score
- [ ] **Validate Complexity Formula:**
  ```bash
  python3 << 'EOF'
  def compute_complexity(input_tokens, keywords_matched, rag_score_max, files, cross_refs, phase=None):
      score = min(keywords_matched * 1.0, 3.0)
      if rag_score_max > 0.7:
          score += 2.0
      elif rag_score_max > 0.5:
          score += 1.0
      score += min(files * 1.5, 3.0)
      if cross_refs > 0:
          score += 1.0
      multipliers = {
          "estudo-previo": 0.5, "projeto-basico": 0.8,
          "projeto-executivo": 1.2, "obra": 1.0,
          "operacao": 0.7, "licitacao": 1.1,
          "due-diligence": 1.3, "encerramento": 0.9
      }
      if phase in multipliers:
          score *= multipliers[phase]
      return min(score, 10.0)

  # Test cases:
  assert compute_complexity(1200, 2, 0.88, 0, 0, "projeto-executivo") < 5.0
  assert compute_complexity(15000, 4, 0.92, 2, 1, "licitacao") > 6.0
  print("✓ Complexity formula OK")
  EOF
  ```

- [ ] **Model Tiering Decision Tree:**
  ```python
  if input_tokens < 2000 and complexity < 3:
      model = "haiku-4-5"
  elif input_tokens < 10000 and complexity < 6:
      model = "sonnet-5"
  else:
      model = "opus-5"
  ```

### R8: Fallback Configuration
- [ ] **Fallback Cascade Defined:** Haiku → Sonnet → Opus
  ```bash
  cat > .claude/fallback-config.json << 'EOF'
  {
    "haiku": {
      "timeout_sec": 60,
      "fallback_to": "sonnet",
      "reduce_max_tokens": 1500
    },
    "sonnet": {
      "timeout_sec": 120,
      "fallback_to": "opus",
      "reduce_max_tokens": 1000
    },
    "opus": {
      "timeout_sec": 180,
      "fallback_to": null
    }
  }
  EOF
  ```

- [ ] **Fallback Hook Implementation:**
  ```python
  # Pseudo-code in maestro.v5.0.md or agent harness
  def run_with_fallback(prompt, initial_model):
      try:
          return run_agent(prompt, model=initial_model, timeout=60)
      except TimeoutError:
          logger.warning(f"Timeout on {initial_model}, cascading to fallback")
          fallback = fallback_config[initial_model]['fallback_to']
          return run_agent(prompt, model=fallback, max_tokens=1500)
  ```

---

## FASE 8 — PRÉ-LAUNCH TESTING (T-30m, ~45 min)

### Functional Tests
- [ ] **Routing Test #1: Basic S6 Match**
  ```bash
  python3 << 'EOF'
  from maestro import route
  prompt = "Desenvolver projeto de terminal portuário em Santos"
  result = route(prompt)
  assert result['agent_id'] == 'manta-03-s6', f"Got {result['agent_id']}"
  print("✓ Test 1 passed")
  EOF
  ```

- [ ] **Routing Test #2: Phase Inference**
  ```bash
  python3 << 'EOF'
  from maestro import route
  prompt = "Projeto executivo detalhado com estrutura, cronograma e orçamento"
  result = route(prompt)
  assert result['phase'] == 'projeto-executivo'
  print("✓ Test 2 passed")
  EOF
  ```

- [ ] **Routing Test #3: Fallback Agent (Ambiguity)**
  ```bash
  python3 << 'EOF'
  from maestro import route
  prompt = "Como fazer um contrato portuário?"  # ambiguous: portos + legal
  result = route(prompt)
  assert result.get('fallback_agent') is not None or result['routing_confidence'] < 0.75
  print("✓ Test 3 passed")
  EOF
  ```

- [ ] **RAG Test #1: BM25 Query**
  ```bash
  python3 << 'EOF'
  from rag import query_bm25
  results = query_bm25("dragagem canal de acesso", collection="por:v5.0:chunks")
  assert len(results) > 0, "No BM25 results"
  assert results[0]['score'] > 0.5
  print(f"✓ Test 4 passed (top score: {results[0]['score']})")
  EOF
  ```

- [ ] **RAG Test #2: Embedding Query**
  ```bash
  python3 << 'EOF'
  from rag import query_embedding
  results = query_embedding("ANTAQ terminal de contêineres", collection="por:v5.0:chunks")
  assert len(results) > 0
  print(f"✓ Test 5 passed (top score: {results[0]['score']})")
  EOF
  ```

- [ ] **RAG Test #3: Reranker**
  ```bash
  python3 << 'EOF'
  from rag import query_with_rerank
  results = query_with_rerank("molhe quebra-mar PIANC", collection="por:v5.0:chunks", top_k=5)
  assert len(results) > 0
  assert results[0]['rerank_score'] > 0.5
  print(f"✓ Test 6 passed (rerank score: {results[0]['rerank_score']})")
  EOF
  ```

- [ ] **Tiering Test #1: Haiku Route**
  ```bash
  python3 << 'EOF'
  from tiering import compute_tier
  tier = compute_tier(input_tokens=1500, keywords_matched=1, rag_score=0.6, files=0, cross_refs=0)
  assert tier == 'haiku'
  print("✓ Test 7 passed")
  EOF
  ```

- [ ] **Tiering Test #2: Sonnet Route**
  ```bash
  python3 << 'EOF'
  from tiering import compute_tier
  tier = compute_tier(input_tokens=5000, keywords_matched=3, rag_score=0.85, files=1, cross_refs=0)
  assert tier == 'sonnet'
  print("✓ Test 8 passed")
  EOF
  ```

- [ ] **Tiering Test #3: Opus Route**
  ```bash
  python3 << 'EOF'
  from tiering import compute_tier
  tier = compute_tier(input_tokens=12000, keywords_matched=5, rag_score=0.95, files=2, cross_refs=2)
  assert tier == 'opus'
  print("✓ Test 9 passed")
  EOF
  ```

### Integration Tests
- [ ] **E2E Test #1: Maestro → S6 → LLM**
  ```bash
  python3 << 'EOF'
  from maestro import process_prompt
  response = process_prompt(
      prompt="Qual é o processo de dragagem em ANTAQ?",
      user_id="test@mantaassociados.com"
  )
  assert 'run_id' in response
  assert response['agent_id'] == 'manta-03-s6'
  assert response['status'] == 'success'
  print(f"✓ Test 10 passed (run_id: {response['run_id']})")
  EOF
  ```

- [ ] **E2E Test #2: With File Processing**
  ```bash
  python3 << 'EOF'
  from maestro import process_prompt
  response = process_prompt(
      prompt="Análise de projeto executivo",
      user_id="test@mantaassociados.com",
      files=[{"name": "projeto.dwg", "size_mb": 1.2}]
  )
  assert response['file_processing'] == True
  assert response['context_window_tokens'] >= 8000
  print("✓ Test 11 passed")
  EOF
  ```

### Performance Tests
- [ ] **Latency Baseline (Sonnet):**
  ```bash
  python3 << 'EOF'
  import time
  from maestro import process_prompt
  start = time.time()
  response = process_prompt("Test prompt")
  latency_ms = (time.time() - start) * 1000
  print(f"Latency: {latency_ms:.0f}ms (target: < 8s)")
  # Expected: < 8000ms
  EOF
  ```

- [ ] **Throughput Test (5 concurrent):**
  ```bash
  python3 << 'EOF'
  import concurrent.futures
  from maestro import process_prompt
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
      futures = [ex.submit(process_prompt, f"Test {i}") for i in range(5)]
      results = [f.result() for f in concurrent.futures.as_completed(futures)]
  assert len(results) == 5
  print(f"✓ Throughput test passed (5 concurrent)")
  EOF
  ```

### Monitoring & Alerts (Dry-run)
- [ ] **Slack Notification Test:**
  ```bash
  curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{
      "text": "🔄 S6 Go-Live Pre-Launch Test",
      "blocks": [{
        "type": "section",
        "text": {"type": "mrkdwn", "text": "S6 dry-run test complete ✓"}
      }]
    }'
  ```

- [ ] **Grafana Dashboard Accessible:**
  ```bash
  curl -s http://grafana.manta.local/api/health | jq .
  # Expected: "ok"
  ```

---

## FASE 9 — FINAL APPROVAL GATE (T-15m)

### MN Final Check
- [ ] **MN Sign-off:** Approva all Phases 1–8
  - [ ] Email confirm: "Approved S6 Launch" by mneves@
  - [ ] Or Slack #agent-ops react with ✓ emoji

- [ ] **Incident Response Ready:**
  - [ ] MN reachable by phone/mobile
  - [ ] Rollback plan printed/accessible
  - [ ] Escalation contacts in Slack pinned message

---

## FASE 10 — GO-LIVE (T+0, Launch Window)

### Pre-Flight (5 min antes)
- [ ] **Stop Active Transactions:**
  ```bash
  # Pause any active background jobs
  systemctl pause manta-scheduler  # or docker pause
  ```

- [ ] **Final Health Check:**
  ```bash
  python3 scripts/healthcheck.py --quick
  # Expected: all green
  ```

- [ ] **Slack Announcement:**
  ```bash
  # Post in #agent-ops:
  # 🚀 **S6 GO-LIVE in 5 minutes**
  # Agent: Manta 03-S6 (Portos)
  # Status: Ready
  # RTO: < 1h
  ```

### Deployment (10 min)
- [ ] **Merge CLAUDE.md v5.0:**
  ```bash
  git add CLAUDE.md VERSIONS.json .claude/agents/agente-portos.v5.0.md .claude/settings.json
  git commit -m "Deploy S6 v5.0: agente-portos with RAG por:v5.0:*, maestro R1 routing, tiering R7, fallback R8"
  git push origin main
  ```

- [ ] **Activate Scheduler:**
  ```bash
  systemctl resume manta-scheduler  # or docker unpause
  sleep 5
  systemctl status manta-scheduler  # verify running
  ```

- [ ] **Enable Maestro Routing:**
  ```bash
  python3 -c "
  import json
  with open('.claude/settings.json') as f:
      config = json.load(f)
  config['maestro_routing_enabled'] = True
  config['s6_enabled'] = True
  with open('.claude/settings.json', 'w') as f:
      json.dump(config, f, indent=2)
  print('✓ Maestro routing + S6 enabled')
  "
  ```

- [ ] **Warm-up Queries (3 requests):**
  ```bash
  for i in 1 2 3; do
    python3 << EOF
  from maestro import process_prompt
  response = process_prompt(f"Test warmup query {i}")
  print(f"Warmup {i}: {response['status']}")
  EOF
  done
  # Expected: 3x "success"
  ```

### Go-Live Confirmation (5 min)
- [ ] **Production Validation:**
  - [ ] S6 responds to portuário keywords
  - [ ] Routing accuracy > 75% (spot check 10 queries)
  - [ ] Latency p50 < 5s, p95 < 8s
  - [ ] No errors in logs: `grep -i error logs/*.log | wc -l`

- [ ] **Slack Announcement (LIVE):**
  ```bash
  # Post in #agent-ops:
  # ✅ **S6 IS LIVE**
  # Manta 03-S6 (Agente-Portos) v5.0 deployed
  # Routing: ✓ | Latency: ✓ | Errors: 0
  # Monitoring: Grafana dashboard active
  # Support: MN on-call
  ```

- [ ] **Send Email:** T+0 notification to @mantaassociados.com
  - Subject: `[LIVE] Manta 03-S6 Agente-Portos v5.0 is now in production`
  - Body: Include link to monitoring, rollback plan, and support contact

---

## FASE 11–20 — POST-LAUNCH (T+1h through T+72h)

*(Covered in POST-LAUNCH-MONITORING.md)*

### Immediate (T+1h)
- [ ] **Grafana Check:** Cost, latency, error rate normal
- [ ] **Logs Review:** No critical errors
- [ ] **User Feedback:** Any issues reported in Slack?

### Short-Term (T+6h)
- [ ] **First RAG Reindex:** Trigger R7 job (if not automatic)
- [ ] **Cost Analysis:** Early estimate of S6 runs cost
- [ ] **Latency Histogram:** P50/P95/P99 within SLA

### Medium-Term (T+24h)
- [ ] **Daily Report:** Cost, runs, errors, feedback (see template)
- [ ] **Feedback Collection:** Any score < 3? Investigate
- [ ] **Rollback Decision Point:** Go/No-Go based on metrics

---

## ROLLBACK TRIGGER (Decision Tree)

**STOP and ROLLBACK if ANY of these conditions met:**

1. **Routing Accuracy < 70%:**
   - More than 30% of portuário queries routed to wrong agent
   - Action: Execute ROLLBACK-PLAN.md immediately

2. **Error Rate > 5%:**
   - More than 5% of runs fail with error
   - Action: Check logs, if unfixable → ROLLBACK

3. **Latency p95 > 15s:**
   - 95th percentile latency exceeds SLA by 2x
   - Action: Disable reranker (R6), test; if still high → ROLLBACK

4. **Cost Anomaly:**
   - S6 cost per run > 3x baseline (e.g., > $0.50/run on Opus)
   - Action: Check tiering formula (R7), if bug → ROLLBACK

5. **Database Corruption:**
   - agent_runs, rag_chunks unavailable or corrupted
   - Action: Immediate ROLLBACK + restore from backup

6. **Security Incident:**
   - Unauthorized access, data leak, or suspicious activity
   - Action: Kill process, isolate database, execute ROLLBACK

---

## TROUBLESHOOTING QUICK REFERENCE

| Issue | Cause | Fix |
|-------|-------|-----|
| S6 not routing | Keyword rule missing or embedding OOD | Re-run embedding, validate BM25 index |
| RAG returns empty | Collection not indexed | Check `por:v5.0:chunks` count in DB |
| High latency | Reranker timeout | Disable R6, or increase timeout |
| Tiering wrong | Complexity formula bug | Validate with test cases, patch formula |
| Fallback cascading too much | Timeout threshold too low | Increase timeout_sec in fallback-config.json |
| Scheduler not running | Systemd/Docker failed | `systemctl status` or `docker logs` |
| Slack alerts not firing | Webhook URL wrong | Re-verify SLACK_WEBHOOK_URL env var |

---

## SIGN-OFF

**Prepared by:** Claude AI (Codex-exemplo Agent)  
**Date:** 2026-07-25  
**Version:** v5.0 (S6 Go-Live)  
**Approval by:** _____________________ (MN name)  
**Timestamp:** _____________________ (date/time)

**Approver email:** mneves@mantaassociados.com  
**Incident contact:** [Fill in: phone/mobile for < 1h RTO]

---

**End of S6 Go-Live Checklist**
