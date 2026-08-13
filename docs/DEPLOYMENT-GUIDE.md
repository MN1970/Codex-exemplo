# Deployment Guide — Manta Maestro v5.0

**Status:** Staging  
**Target Go-Live:** 2026-07-28  
**Owner:** mneves@mantaassociados.com  
**Support:** #agent-ops (Slack)

---

## Overview

This guide walks through deploying Manta Maestro v5.0, which introduces:
- 8 architectural pillars (deterministic routing, RAG hybrid, automatic tiering, observability)
- 5 new vertical agents (S6–S10: Portos, Aeroportos, Saneamento, Energia, Barragens)
- 6 new routing rules (R6–R10: reranking, tiering, fallback, feedback, memory purge)
- Skill versioning with checksums and RAG collections

**Migration path from v4.2:** See Phase 1–8 below.

---

## Pre-Deployment Checklist (T-48h)

- [ ] Read entire `CLAUDE.md` v5.0
- [ ] Review `ROUTING-REFERENCE.md` (R1 specification)
- [ ] Test `scripts/healthcheck.py` locally
- [ ] Validate `VERSIONS.json` checksums against `.claude/agents/`
- [ ] Backup existing RAG (v4.9) to S3
- [ ] Schedule notification email to team (T-24h, T-6h, T+0, T+24h)
- [ ] Prepare rollback script (Phase 8)

---

## Phase 1 — Architecture Validation (48h before)

**Goal:** Ensure all 8 pillars are documented and understood.

### Tasks

1. **Architecture document** — Confirm `.claude/agents/maestro.v5.0.md` includes:
   - R1 routing algorithm (3 stages: keyword + embedding + context)
   - R6–R10 loops (reranking, tiering, fallback, feedback, purge)
   - 20-agent mapa (11 horizontal + 9 vertical)
   - Skill versioning with VERSIONS.json

2. **Tiering formula** — Validate `compute_complexity_score()` in `tiering-audit.py`:
   - Keywords: 0–3 points
   - RAG reranker: 0–2 points
   - Files: 0–3 points
   - Cross-refs: 0–1 point
   - Phase multiplier: 0.5–1.3x

3. **Run `healthcheck.py`** — Should report:
   - ✓ All 20 skills with valid checksums
   - ✓ CLAUDE.md v5.0 structure
   - ⚠ (acceptable) RAG collections not yet indexed

```bash
cd /home/user/Codex-exemplo
python3 scripts/healthcheck.py
```

---

## Phase 2 — RAG Collections (36h before)

**Goal:** Index and validate 5 new RAG collections (S6–S10) + upgrade 4 existing.

### Tasks

1. **Create collection directories** (`.claude/rag/`):
   ```bash
   mkdir -p .claude/rag/{san_v5.0,ene_v5.0,por_v5.0,aer_v5.0,bar_v5.0}
   ```

2. **Ingest source documents** per collection:
   - **san:v5.0** — SNIS, AySA, NBR 12211-12218, Lei 14.026 (target: 2500 chunks)
   - **ene:v5.0** — ANEEL editais, EPE R1-R5, ONS (target: 3000 chunks)
   - **por:v5.0** — ANTAQ, PIANC, editais BNDES (target: 2000 chunks)
   - **aer:v5.0** — ANAC/RBAC, ICAO Annex 14, FAA ACs (target: 1800 chunks)
   - **bar:v5.0** — ICOLD, CBDB, Lei 12.334 (target: 2200 chunks)

   **Per-collection ingestión process:**
   ```
   1. Upload .pdf/.txt to .claude/rag/{prefix}_v5.0/
   2. OCR + chunk (512 tokens, 50% overlap)
   3. Embed via Infinity (intfloat/multilingual-e5-large-instruct)
   4. Save chunks.jsonl + metadata.json
   5. Validate: reranker score > 0.5 on 10 test queries
   ```

   **SLA:** Each collection ready ≤ 24h from approval.

3. **Validate RAG** — Run reindex:
   ```bash
   python3 scripts/rag-reindex.py
   # Output: collections_processed=9, chunks_indexed=20500+
   ```

4. **Backup RAG v4.9** (if exists):
   ```bash
   aws s3 sync .claude/rag/ s3://manta-backup/rag-v4.9/ --exclude "*v5.0*"
   ```

---

## Phase 3 — Skill Versioning (24h before)

**Goal:** Version all 20 agent skills, calculate checksums, pin to v5.0.

### Tasks

1. **Copy skills to v5.0**:
   ```bash
   # New agents (S6–S10)
   cp .claude/agents/agente-saneamento.md .claude/agents/agente-saneamento.v5.0.md
   cp .claude/agents/agente-energia.md .claude/agents/agente-energia.v5.0.md
   cp .claude/agents/agente-portos.md .claude/agents/agente-portos.v5.0.md
   cp .claude/agents/agente-aeroportos.md .claude/agents/agente-aeroportos.v5.0.md
   cp .claude/agents/agente-barragens.md .claude/agents/agente-barragens.v5.0.md

   # Upgrade existing (S1–S4 + horizontals)
   cp .claude/agents/agente-rodovias.md .claude/agents/agente-rodovias.v5.0.md
   cp .claude/agents/agente-oae.md .claude/agents/agente-oae.v5.0.md
   # ... (14 total)
   ```

2. **Generate checksums**:
   ```bash
   for file in .claude/agents/*.v5.0.md; do
     echo "$file: $(md5sum "$file")"
   done > checksums.txt
   ```

3. **Update VERSIONS.json** with checksums:
   ```json
   {
     "agent_skills": {
       "agente-saneamento": {
         "v5.0": {
           "checksum": "f1a3d2b4c5e7a8b9c1d2e3f4a5b6c7d8",
           "pinned_by": ["prod"]
         }
       }
     }
   }
   ```

4. **Pin skills in `.claude/settings.json`**:
   ```json
   {
     "skill_version_pin": {
       "agente-saneamento": "v5.0",
       "agente-energia": "v5.0",
       // ... all 20 agents
     }
   }
   ```

5. **Mark v4.9 as deprecated**:
   ```json
   {
     "v4.9": {
       "deprecated_at": "2026-07-25T14:32:00Z",
       // ... grace period 30 days
     }
   }
   ```

---

## Phase 4 — Observability Setup (12h before)

**Goal:** Enable run tracking, Grafana dashboards, Slack alerts.

### Tasks

1. **Create Supabase tables**:
   ```sql
   -- agent_runs: immutable log of all executions
   CREATE TABLE agent_runs (
     id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
     run_id UUID UNIQUE NOT NULL,
     agent_id TEXT NOT NULL,
     model_tier TEXT,
     input_tokens INT,
     output_tokens INT,
     cost_usd DECIMAL(8,4),
     latency_ms INT,
     status TEXT CHECK (status IN ('success', 'timeout', 'error')),
     created_at TIMESTAMP DEFAULT NOW()
   );

   -- agent_feedback: user ratings post-run
   CREATE TABLE agent_feedback (
     id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
     run_id UUID UNIQUE REFERENCES agent_runs(run_id),
     feedback_score INT CHECK (feedback_score BETWEEN 0 AND 5),
     user_comment TEXT,
     created_at TIMESTAMP DEFAULT NOW()
   );

   -- agent_triggers: APScheduler job scheduling
   CREATE TABLE agent_triggers (
     id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
     trigger_id UUID UNIQUE NOT NULL,
     name TEXT NOT NULL,
     cron_expression TEXT,
     enabled BOOLEAN DEFAULT TRUE,
     created_at TIMESTAMP DEFAULT NOW(),
     next_run_at TIMESTAMP
   );
   ```

2. **Setup Grafana dashboards**:
   - Cost per agent per day (bar chart)
   - Latency p50/p95/p99 (line chart)
   - Error rate by segment (gauge)
   - Feedback score trend (3-month rolling)
   - Model tier distribution (pie chart)

3. **Configure Slack alerts** (to #agent-ops):
   - **Error spike:** > 3 timeouts/hour in one agent
   - **Cost spike:** > 20% over budget
   - **Feedback drop:** avg score < 3.0 (7-day rolling)
   - **Deprecation:** v4.9 skills nearing end of grace period (15, 7, 1 day before)

---

## Phase 5 — Tiering & Fallback (6h before)

**Goal:** Validate R7 complexity score, test R8 fallback cascade.

### Tasks

1. **Validate tiering formula**:
   ```bash
   python3 scripts/tiering-audit.py
   # Expected output: accuracy > 95%
   # If < 95%, adjust complexity_score weights in CLAUDE.md apêndice
   ```

2. **Test fallback cascade** (R8):
   - Simulate Sonnet timeout after 60s
   - Verify re-submission with fallback tier (Opus)
   - Check context injection (previous RAG results preserved)
   - Validate cost logging

   **Mock test (in maestro.v5.0.md):**
   ```python
   # Simulate timeout
   if latency_ms > 60000:
       log_timeout(run_id, agent_id, model_tier)
       context = preserve_context()
       model_tier = "opus-5"
       resubmit(prompt, context, model_tier, max_tokens=1500)
   ```

3. **Deploy R7 hook** (PreToolUse):
   - Add `compute_complexity_score()` to maestro
   - Hook runs on every prompt entry
   - Logs tiering decision to `agent_runs`

---

## Phase 6 — Integration Tests (2h before)

**Goal:** End-to-end validation of routing, RAG, tiering, feedback.

### Test Cases

**Test 1: Saneamento (S8) prompt**
```
Input: "Estudamos uma ETA para AySA em Buenos Aires, precisamos do básico"
Expected:
  - Agent: agente-saneamento (S8)
  - Phase: estudo-previo (inferred)
  - Tier: Haiku 4.5 (input < 2000, complexity < 3)
  - RAG collection: san:v5.0:chunks
  - Top-3 results: AySA docs, Lei 14.026, SNIS
```

**Test 2: Cross-agent (Energia + Orçamento)**
```
Input: "Qual o custo de uma subestação 138kV para State Grid?"
Expected:
  - Primary agent: agente-energia (S9)
  - Secondary ref: agente-orcamento (05)
  - Tier: Sonnet 5 (cross-ref detected)
  - Feedback integration: rate response, logs to agent_feedback
```

**Test 3: File processing (multi-file)**
```
Input: [projeto.dwg (2.5MB), edital.pdf (1.8MB)] + "Análise estrutural"
Expected:
  - File processing flag: true
  - Allocated tokens: 8000 (vs default 4000)
  - Tier: Sonnet 5 (file_to_process=2, complexity+=3)
```

**Test 4: Fallback cascade (R8)**
```
Input: Large query (15k tokens) to agente-energia
Expected:
  - Initial tier: Opus 5
  - Simulate timeout after 60s
  - Fallback triggered, no re-tier (already at max)
  - Alert sent to #agent-ops
  - Log entry: status="timeout", fallback_attempted=true
```

**Test 5: Feedback loop (R9)**
```
Input: Rate 5 previous runs with scores 4–5
Expected:
  - Entries logged in agent_feedback
  - Weekly: embedding model fine-tune initiated
  - Checksum update in VERSIONS.json
  - Slack notification: "Embedding model v5.1 staged"
```

### Run Tests
```bash
# Unit tests (Python)
python3 -m pytest tests/ -v

# Integration test script (pseudo)
for test in tests/test-case-*.sh; do
  bash "$test"
done
```

---

## Phase 7 — Go-Live (T+0)

**Checklist (execute in order):**

1. **Merge to main**:
   ```bash
   git add CLAUDE.md VERSIONS.json .claude/ scripts/ docs/
   git commit -m "Deploy v5.0: 8 pillars, 5 new agents (S6-S10), R6-R10 loops"
   git push origin main
   ```

2. **Activate RAG collections** (in Supabase):
   ```sql
   UPDATE rag_collections SET active = TRUE WHERE version = 'v5.0';
   ```

3. **Activate R1 routing rules** (Maestro):
   - Deploy `.claude/agents/maestro.v5.0.md`
   - Update routing table with S6–S10 keywords
   - Test with 10 sample prompts per segment

4. **Enable R6–R10 loops**:
   - Enable R6 reranker (cross-encoder inference)
   - Enable R7 tiering hook (PreToolUse)
   - Enable R8 fallback (exception handler)
   - Enable R9 feedback (post-run survey)
   - Enable R10 memory purge (APScheduler)

5. **Activate APScheduler triggers**:
   ```python
   # rag-reindex: daily 02:00 UTC
   create_trigger("rag-reindex-daily", "0 2 * * *", "Reindex RAG v5.0")
   
   # embedding-retrain: weekly Sunday 03:00 UTC
   create_trigger("embedding-retraining", "0 3 * * 0", "Fine-tune embedding")
   
   # memory-purge: daily 03:30 UTC
   create_trigger("agent-memory-purge", "30 3 * * *", "Purge agent memory")
   ```

6. **Monitor (1 hour)**:
   - Watch Grafana dashboard (cost, latency, errors)
   - Check #agent-ops for alerts
   - Verify RAG collections responding
   - Sample 5 requests from each agent

7. **Announce** (email + Slack):
   ```
   Subject: Manta Maestro v5.0 — Live

   v5.0 is now in production. Key changes:
   - 5 new vertical agents (S6–S10)
   - Automatic tiering (Haiku→Sonnet→Opus)
   - Enhanced routing with RAG reranker
   - Full observability (run tracking, costs, feedback)

   See DEPLOYMENT-GUIDE.md for details.
   Support: #agent-ops
   Rollback: See Phase 8 (last 24h window)
   ```

---

## Phase 8 — Post-Launch (24–72h)

### Monitoring (continuous)

| Metric | Target | Alert threshold |
|--------|--------|-----------------|
| Avg latency | < 5s | > 10s |
| Error rate | < 1% | > 3% |
| Cost/run | $0.02–$0.15 | > 2x baseline |
| Feedback score | ≥ 4.0/5 | < 3.5 |
| RAG hit rate | > 70% | < 50% |

### Validation (first 24h)

- [ ] Cost per agent within ±10% of baseline
- [ ] Latency p95 improved (tiering savings expected)
- [ ] Feedback score stable (≥ 4.0)
- [ ] RAG queries returning relevant results (R6 validation)
- [ ] No alerts in #agent-ops (besides expected deprecation warnings)

### Adjustments (if needed)

- **Tiering too aggressive (too much Haiku):** Increase complexity threshold (3.0 → 3.5)
- **Tiering too conservative (too much Opus):** Decrease threshold (6.0 → 5.5)
- **RAG miss rate high:** Retrigger `rag-reindex.py`, validate embeddings
- **Feedback score low:** Check agent skill quality, run `embedding-retraining`

### Gate (48h after go-live)

Request approval from @mneves via:
```
Ticket MNT-2026-UPGRADE-AGENTS-V5
Status: ✓ Production (stable)
Metrics: [attach Grafana screenshot]
Approval: [date/time]
```

Once approved, remove rollback window (Phase 8 end).

---

## Phase 8 Alternative — ROLLBACK

**If critical issues (> 10% error rate, < 2.0 feedback, cost > 3x baseline):**

### Steps (< 1 hour RTO)

1. **Revert CLAUDE.md**:
   ```bash
   git revert HEAD
   git checkout v4.2 -- CLAUDE.md
   ```

2. **Disable R6–R10**:
   ```bash
   # In maestro.v5.0.md: comment out R6–R10 hooks
   # Keep R1–R5 active (backward compatible)
   ```

3. **Restore RAG v4.9**:
   ```bash
   aws s3 sync s3://manta-backup/rag-v4.9/ .claude/rag/ --exclude "*v5.0*"
   ```

4. **Revert skill pins**:
   ```json
   {
     "skill_version_pin": {
       "agente-saneamento": "v4.2",
       // ... all v4.2 versions
     }
   }
   ```

5. **Deactivate new agents** (S6–S10):
   ```bash
   # Remove S6–S10 from maestro routing rules
   # Keep S1–S4 + horizontals
   ```

6. **Log post-mortem**:
   ```bash
   cat > ROLLBACK_LOG.md << EOF
   ## Rollback — v5.0 → v4.2
   - Timestamp: 2026-07-28T16:45:00Z
   - Reason: [error rate > 10%]
   - RTO: 47 minutes
   - Root cause: [to be investigated]
   - Next steps: [action items]
   EOF
   ```

7. **Notify team**:
   ```
   Slack #agent-ops: "Rolled back to v4.2 due to [reason]. RTO: 47min."
   Email: mneves + team with post-mortem
   ```

### Investigation & Retry

- Review logs in `agent_runs` table (error details)
- Identify issue (R6 reranker? R7 formula? RAG quality?)
- Fix in staging
- Retry deployment in 48h (after fixes validate)

---

## Reference: Health Checks

Run before/after deployment:

```bash
# Pre-deploy
python3 scripts/healthcheck.py
# Expected: 0 critical issues, <5 warnings

# Post-deploy (1h after go-live)
python3 scripts/healthcheck.py
# Expected: same as pre-deploy

# Tiering validation
python3 scripts/tiering-audit.py
# Expected: accuracy > 95%

# RAG status
python3 scripts/rag-reindex.py
# Expected: 9 collections, 20500+ chunks indexed
```

---

## Runbook — Debugging Common Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| High latency (> 10s) | Check R7 tiering, Sonnet timeout | Adjust complexity threshold, increase Opus allocation |
| RAG miss rate | Check embedding model, reranker score | Retrigger `rag-reindex.py`, validate chunk quality |
| Cost spike | Tiering too aggressive (Opus overflow) | Lower complexity threshold, prioritize Haiku |
| Feedback score < 3 | Agent skill quality or routing errors | Review agent-specific error logs, retrain embedding |
| Deprecation warnings | Skills still pinned to v4.9 | Update `skill_version_pin` in settings.json |

---

## Support & Contact

- **Slack:** #agent-ops
- **Email:** mneves@mantaassociados.com
- **Documentation:** `/home/user/Codex-exemplo/docs/`
- **Issues:** Create ticket in MNT-2026 epic
- **Escalation:** MN (final approval)

---

**Fin — Deployment Guide v5.0**
