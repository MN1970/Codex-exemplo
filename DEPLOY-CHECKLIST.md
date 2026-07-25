# Deploy Checklist — v5.0 Quick Reference

**Print and check off as you deploy. Estimated time: 4–6 hours.**

---

## Pre-Deploy (48h before)

- [ ] Read CLAUDE.md v5.0 (sections P1–P8)
- [ ] Review DEPLOYMENT-GUIDE.md (phases 1–8)
- [ ] Review ROUTING-REFERENCE.md (R1 specification)
- [ ] Review ARQUITETURA-v5.0.md (8 pillars)
- [ ] Run `scripts/healthcheck.py` locally
  ```
  Expected: 0 critical issues, <5 warnings
  ```
- [ ] Validate VERSIONS.json syntax
  ```
  python3 -c "import json; json.load(open('VERSIONS.json'))"
  ```
- [ ] Backup existing RAG (v4.9) to S3
  ```
  aws s3 sync .claude/rag/ s3://manta-backup/rag-v4.9/ --exclude "*v5.0*"
  ```
- [ ] Create incident communication plan
  - Email template (T-24h, T-6h, T+0, T+24h)
  - Slack #agent-ops channel ready
  - Escalation contact (MN) confirmed

---

## Phase 1 — Architecture (48h before)

- [ ] Confirm CLAUDE.md includes 8 pilares section
- [ ] Confirm R1–R10 loops documented in maestro.v5.0.md
- [ ] Confirm 20-agent mapa with checksums in VERSIONS.json
- [ ] Validate tiering formula in tiering-audit.py matches CLAUDE.md apêndice
- [ ] Run architecture test
  ```bash
  python3 scripts/healthcheck.py
  # Verify: "Section found: OS 8 PILARES", "R1 — MAESTRO", etc.
  ```

---

## Phase 2 — RAG Collections (36h before)

- [ ] Create RAG directories
  ```bash
  mkdir -p .claude/rag/{san_v5.0,ene_v5.0,por_v5.0,aer_v5.0,bar_v5.0}
  ```

- [ ] Ingest sources for san:v5.0 (target: 2500 chunks)
  - [ ] SNIS documents
  - [ ] AySA documentation
  - [ ] NBR 12211-12218
  - [ ] Lei 14.026/2020
  - [ ] BNDES editais
  - [ ] Validate: reranker score > 0.5 on 10 test queries

- [ ] Ingest sources for ene:v5.0 (target: 3000 chunks)
  - [ ] ANEEL editais
  - [ ] EPE R1-R5 (Plano Decenal)
  - [ ] ONS documentation
  - [ ] IEEE standards
  - [ ] ABNT normas (NBR 60909, 61294)
  - [ ] Validate: reranker score > 0.5

- [ ] Ingest sources for por:v5.0 (target: 2000 chunks)
  - [ ] ANTAQ documentation
  - [ ] PIANC guidelines
  - [ ] BNDES editais portos
  - [ ] Validate: reranker score > 0.5

- [ ] Ingest sources for aer:v5.0 (target: 1800 chunks)
  - [ ] ANAC/RBAC
  - [ ] ICAO Annex 14
  - [ ] FAA Advisory Circulars
  - [ ] Validate: reranker score > 0.5

- [ ] Ingest sources for bar:v5.0 (target: 2200 chunks)
  - [ ] ICOLD publications
  - [ ] CBDB documentation
  - [ ] Lei 12.334/2010
  - [ ] Validate: reranker score > 0.5

- [ ] Run RAG reindex validation
  ```bash
  python3 scripts/rag-reindex.py
  # Expected output:
  # Collections processed: 9
  # Chunks indexed: 20500+
  # Embeddings validated: > 99%
  # Errors: 0
  ```

- [ ] Backup RAG v4.9 to S3 (if exists)
  ```bash
  aws s3 sync .claude/rag/ s3://manta-backup/rag-v4.9/ --exclude "*v5.0*"
  ```

---

## Phase 3 — Skill Versioning (24h before)

- [ ] Copy all skills to v5.0 (20 total)
  ```bash
  # S6–S10 (new)
  cp .claude/agents/agente-{saneamento,energia,portos,aeroportos,barragens}.md \
     .claude/agents/agente-{saneamento,energia,portos,aeroportos,barragens}.v5.0.md

  # S1–S4 + horizontals (upgraded)
  cp .claude/agents/agente-*.md .claude/agents/agente-*.v5.0.md  # Check count: 20 files
  ```

- [ ] Generate checksums
  ```bash
  for file in .claude/agents/*.v5.0.md; do
    echo "$file: $(md5sum "$file")"
  done > /tmp/checksums.txt
  ```

- [ ] Update VERSIONS.json with checksums (verify in file)
  - [ ] All 20 agents have v5.0 entries with valid checksums
  - [ ] All 9 RAG collections have v5.0 entries with checksums
  - [ ] v4.9/v4.2 entries marked deprecated_at

- [ ] Create `.claude/settings.json` with skill pins
  ```json
  {
    "skill_version_pin": {
      "maestro": "v5.0",
      "agente-saneamento": "v5.0",
      ... (20 total)
    }
  }
  ```

- [ ] Validate settings.json syntax
  ```bash
  python3 -c "import json; json.load(open('.claude/settings.json'))"
  ```

---

## Phase 4 — Observability (12h before)

- [ ] Create Supabase tables
  ```sql
  -- See DEPLOYMENT-GUIDE.md Phase 4 for exact schema
  CREATE TABLE agent_runs (...)
  CREATE TABLE agent_feedback (...)
  CREATE TABLE agent_triggers (...)
  ```

- [ ] Validate table creation
  ```bash
  psql -c "SELECT * FROM agent_runs LIMIT 0;"
  ```

- [ ] Setup Grafana dashboards
  - [ ] Cost per agent per day
  - [ ] Latency p50/p95/p99
  - [ ] Error rate by segment
  - [ ] Feedback score trend
  - [ ] Model tier distribution

- [ ] Setup Slack alerts (#agent-ops)
  - [ ] Error spike (> 3 timeouts/hour)
  - [ ] Cost spike (> 20% daily)
  - [ ] Feedback drop (avg < 3.0/5)
  - [ ] Deprecation warnings (15d, 7d, 1d before EOL)

---

## Phase 5 — Tiering & Fallback (6h before)

- [ ] Run tiering audit
  ```bash
  python3 scripts/tiering-audit.py
  # Expected: accuracy > 95%
  # If < 95%: adjust weights in CLAUDE.md apêndice and retry
  ```

- [ ] Test fallback cascade (R8)
  - [ ] Simulate Sonnet timeout after 60s
  - [ ] Verify re-submission with Opus tier
  - [ ] Verify context preservation (RAG results carried over)
  - [ ] Verify cost logging

- [ ] Deploy R7 tiering hook (PreToolUse)
  - [ ] Add compute_complexity_score() to maestro
  - [ ] Test on 10 sample prompts
  - [ ] Verify tiering decisions logged to agent_runs

---

## Phase 6 — Integration Tests (2h before)

- [ ] Test 1: Saneamento (S8) routing
  ```
  Input: "Estudamos uma ETA para AySA em Buenos Aires"
  Expected agent: agente-saneamento
  Expected phase: estudo-previo
  Expected tier: haiku-4-5
  Expected RAG: san:v5.0:chunks
  ✓ Pass
  ```

- [ ] Test 2: Cross-agent (S9 + 05)
  ```
  Input: "Qual o custo de uma subestação 138kV?"
  Expected agent: agente-energia (primary)
  Expected refs: agente-orcamento (secondary)
  Expected tier: sonnet-5 (cross-ref detected)
  ✓ Pass
  ```

- [ ] Test 3: File processing
  ```
  Input: [projeto.dwg (2.5MB)] + "Análise estrutural"
  Expected: file_processing=true, window_tokens=5000+
  Expected tier: sonnet-5 (file handling)
  ✓ Pass
  ```

- [ ] Test 4: Fallback cascade
  ```
  Input: Large query (15k tokens)
  Expected: Initial tier Opus
  Simulate timeout after 60s
  Expected: Fallback alert sent
  Expected: Log entry with timeout=true
  ✓ Pass
  ```

- [ ] Test 5: Feedback loop
  ```
  Input: Rate 5 previous runs (scores 4–5)
  Expected: Entries logged in agent_feedback
  Weekly trigger enabled for embedding retraining
  ✓ Pass
  ```

- [ ] Run integration test suite
  ```bash
  pytest tests/integration/ -v
  # Expected: 5/5 tests pass
  ```

---

## Phase 7 — Go-Live (T+0)

**DO NOT PROCEED IF ANY PREVIOUS PHASE INCOMPLETE**

- [ ] Merge to main
  ```bash
  git add CLAUDE.md VERSIONS.json .claude/ scripts/ docs/ DEPLOY-CHECKLIST.md
  git commit -m "Deploy v5.0: 8 pillars, 5 new agents (S6-S10), R6-R10 loops"
  git push origin main
  ```

- [ ] Activate RAG collections (Supabase)
  ```sql
  UPDATE rag_collections SET active = TRUE WHERE version = 'v5.0';
  ```

- [ ] Activate R1 routing (Maestro)
  - [ ] Deploy maestro.v5.0.md
  - [ ] Update routing keywords for S6–S10
  - [ ] Test with 10 sample prompts (1 per segment)
  ```
  ✓ S1 (rodovias)
  ✓ S2 (OAE)
  ✓ S3 (ferrovia)
  ✓ S4 (metrô)
  ✓ S6 (portos)
  ✓ S8 (saneamento)
  ✓ S9 (energia)
  ✓ S10 (barragens)
  ✓ Horizontal (claims)
  ✓ Horizontal (contratual)
  ```

- [ ] Enable R6–R10 loops
  - [ ] R6 reranker (cross-encoder inference)
  - [ ] R7 tiering hook (PreToolUse)
  - [ ] R8 fallback handler (exception)
  - [ ] R9 feedback survey (post-run)
  - [ ] R10 memory purge (APScheduler)

- [ ] Activate APScheduler triggers
  ```python
  create_trigger("rag-reindex-daily", "0 2 * * *", "Reindex RAG v5.0")
  create_trigger("embedding-retraining", "0 3 * * 0", "Fine-tune embedding")
  create_trigger("agent-memory-purge", "30 3 * * *", "Purge agent memory")
  ```

- [ ] Monitor for 1 hour
  - [ ] Grafana dashboard live
  - [ ] #agent-ops Slack receiving data
  - [ ] No critical alerts
  - [ ] Sample 5 requests from each agent (success)

- [ ] Send announcement
  ```
  Email subject: "Manta Maestro v5.0 — Live"
  Slack: Post to #agent-ops with summary
  Include: Support contact, rollback instructions, runbook link
  ```

---

## Phase 8 — Post-Launch (24–72h)

### Monitoring (continuous)

- [ ] Cost per run: target $0.05–$0.08
  - [ ] Check Grafana: Cost/day trending correctly
  - [ ] No cost spike (> 2x baseline)

- [ ] Latency p95: target < 5s
  - [ ] Check Grafana: Latency trending down (vs v4.2)
  - [ ] No latency spike (> 10s)

- [ ] Error rate: target < 1%
  - [ ] Check logs: No systemic errors
  - [ ] RAG failures < 1%
  - [ ] Tiering failures < 0.5%

- [ ] Feedback score: target ≥ 4.0/5
  - [ ] Collect user ratings
  - [ ] Average score ≥ 4.0
  - [ ] No score drift downward

### Validation (first 24h)

- [ ] Cost comparison
  ```bash
  SELECT 
    agent_id,
    COUNT(*) as runs,
    AVG(cost_usd) as avg_cost,
    SUM(cost_usd) as total_cost
  FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '1 day'
  GROUP BY agent_id;
  # Expected: costs 30–45% lower than v4.2 baseline
  ```

- [ ] Latency comparison
  ```bash
  SELECT 
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
  FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '1 day';
  # Expected: p95 < 5s, p99 < 8s
  ```

- [ ] Error analysis
  ```bash
  SELECT status, COUNT(*) as count
  FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '1 day'
  GROUP BY status;
  # Expected: success > 99%, timeout < 0.5%, error < 0.5%
  ```

- [ ] RAG validation
  ```bash
  SELECT 
    agent_id,
    COUNT(*) as runs,
    SUM(CASE WHEN rag_hit = true THEN 1 ELSE 0 END) as hits,
    100.0 * SUM(CASE WHEN rag_hit = true THEN 1 ELSE 0 END) / COUNT(*) as hit_rate
  FROM agent_runs
  WHERE created_at > NOW() - INTERVAL '1 day'
  GROUP BY agent_id;
  # Expected: hit_rate > 70% for each agent
  ```

### Adjustments (if needed)

- [ ] Tiering too aggressive (too much Haiku)
  - Increase complexity threshold: 3.0 → 3.5
  - Re-run tiering-audit.py to validate

- [ ] Tiering too conservative (too much Opus)
  - Decrease threshold: 6.0 → 5.5
  - Re-run tiering-audit.py to validate

- [ ] RAG miss rate high (< 50%)
  - Re-run rag-reindex.py (force reindex)
  - Check embedding model quality
  - Review low-scoring chunks in query results

- [ ] Feedback score low (< 3.5)
  - Review agent-specific error logs
  - Check if particular agent skills degraded
  - Consider manual skill review or training

### Gate Approval (48h after go-live)

- [ ] Compile Grafana metrics screenshot
- [ ] Request approval from @mneves
  ```
  Ticket: MNT-2026-UPGRADE-AGENTS-V5
  Status: ✓ Production (stable 24h+)
  Metrics attached
  Approval: [date/time]
  ```

- [ ] Once approved, **REMOVE ROLLBACK WINDOW**
  - Archive rollback.py to backup
  - Mark Phase 8 alternative as no longer available
  - Send final notification: "v5.0 stable, no rollback window"

---

## If Issues Arise — ROLLBACK (< 1h RTO)

**Only if critical issues: > 10% error rate, < 2.0 feedback, cost > 3x baseline**

- [ ] Revert CLAUDE.md
  ```bash
  git revert HEAD
  git checkout v4.2 -- CLAUDE.md
  git push origin main
  ```

- [ ] Disable R6–R10 (keep R1–R5)
  - [ ] Comment out R6 reranker
  - [ ] Comment out R7 tiering hook
  - [ ] Comment out R8 fallback
  - [ ] Comment out R9 feedback
  - [ ] Comment out R10 purge

- [ ] Restore RAG v4.9
  ```bash
  aws s3 sync s3://manta-backup/rag-v4.9/ .claude/rag/
  ```

- [ ] Revert skill pins
  ```json
  {
    "skill_version_pin": {
      "maestro": "v4.2",
      ... all v4.2
    }
  }
  ```

- [ ] Log post-mortem
  ```bash
  cat > ROLLBACK_LOG.md << EOF
  ## Rollback — v5.0 → v4.2
  - Timestamp: [date/time]
  - Reason: [error rate / cost / feedback issue]
  - RTO: [X minutes]
  - Root cause analysis: TBD
  - Next steps: TBD
  EOF
  ```

- [ ] Notify team
  ```
  Slack: "Rolled back to v4.2 due to [reason]. RTO: X min."
  Email: mneves + full team with post-mortem
  ```

---

## Sign-Off

**Deployment started:** _________________ (date/time)
**Deployed by:** _________________ (name)
**Phase 7 completed:** ☐ Yes (time: ______)
**Phase 8 gate approved:** ☐ Yes (date: ______) | ☐ No (reason: ______)
**Support contact:** mneves@mantaassociados.com
**Slack channel:** #agent-ops

---

**End of Deploy Checklist v5.0**
