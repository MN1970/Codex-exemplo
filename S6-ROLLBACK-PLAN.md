# S6 Rollback Plan — < 1h RTO
**Version: v5.0 | Agent: Manta 03-S6 (Portos) | Owner: mneves@mantaassociados.com**

Emergency rollback procedure for production incident. **Target RTO: < 60 minutes.**

---

## PRÉ-REQUISITOS PARA ROLLBACK

### Before Launch (Checklist before T+0)
- [ ] Backup of v4.9 RAG collection created
  ```bash
  pg_dump -h $SUPABASE_HOST -U postgres -d postgres -t "rag_*" \
    | gzip > backups/rag_v4.9_pre_s6_$(date +%s).sql.gz
  ```

- [ ] CLAUDE.md v4.2 backed up
  ```bash
  cp CLAUDE.md CLAUDE.md.v5.0.backup
  git show HEAD~1:CLAUDE.md > CLAUDE.md.v4.2.backup
  ```

- [ ] Skills v4.9 backed up
  ```bash
  [ -f .claude/agents/agente-portos.v4.9.md ] && \
    cp .claude/agents/agente-portos.v4.9.md .backup/
  ```

- [ ] VERSIONS.json v4.9 metadata preserved
  ```bash
  jq '.agente-portos.v4.9' VERSIONS.json > .backup/agente-portos.v4.9.versions.json
  ```

- [ ] Systemd/Docker stop script ready
  ```bash
  cat > scripts/emergency_stop.sh << 'EOF'
  #!/bin/bash
  echo "🛑 Emergency stop..."
  systemctl stop manta-scheduler
  # or: docker stop manta-scheduler
  sleep 2
  echo "✓ Scheduler stopped"
  EOF
  chmod +x scripts/emergency_stop.sh
  ```

---

## ROLLBACK DECISION CRITERIA

**Execute rollback immediately if ANY condition met:**

| Condition | Severity | Action |
|-----------|----------|--------|
| Routing accuracy < 60% | 🔴 Critical | ROLLBACK |
| Error rate > 10% | 🔴 Critical | ROLLBACK |
| Latency p95 > 20s | 🟡 High | Try disable R6, if no fix → ROLLBACK |
| Database unavailable | 🔴 Critical | ROLLBACK + restore backup |
| Data loss detected | 🔴 Critical | ROLLBACK + restore backup + audit |
| Security breach | 🔴 Critical | Kill all processes, ROLLBACK, investigate |
| Recurring timeouts | 🟡 High | Try increase timeout, if no fix → ROLLBACK |
| RAG completely empty | 🔴 Critical | ROLLBACK |

**Decision maker:** mneves@mantaassociados.com (MN)  
**Approval:** Slack #agent-ops or phone call (document in ROLLBACK_LOG.md)

---

## ROLLBACK PROCEDURE (Step-by-Step, < 60 min)

### STEP 1 — DECLARE INCIDENT & NOTIFY (5 min)

- [ ] **MN phones:** Team lead / ops engineer (if not MN)
  - Phrase: "S6 rollback initiated due to [REASON]"
  - Confirm: "Acknowledged, beginning rollback"

- [ ] **Slack #agent-ops Announcement:**
  ```
  🚨 **INCIDENT: S6 Rollback in Progress**
  
  Reason: [e.g., Routing accuracy < 60%, error rate > 10%]
  Decision: MN approved rollback
  ETA: < 60 min RTO
  Timeline: [start time]
  
  Status will be updated every 10 min.
  ---
  Rollback lead: [name]
  Support: MN on-call
  ```

- [ ] **Document in ROLLBACK_LOG.md:**
  ```markdown
  ## Rollback Event 001 (2026-07-25T14:30:00Z)
  
  Reason: Routing accuracy dropped to 58% after S6 launch
  Decision: MN approved
  Start time: 2026-07-25T14:30:00Z
  Expected end: 2026-07-25T15:30:00Z
  Lead: [operator name]
  ```

### STEP 2 — STOP PRODUCTION SERVICES (10 min)

- [ ] **Stop Scheduler (APScheduler):**
  ```bash
  systemctl stop manta-scheduler
  # or: docker stop manta-scheduler
  sleep 2
  systemctl status manta-scheduler | grep -i "inactive\|stopped"
  # Expected: "inactive (dead)" or "Exited (0)"
  ```

- [ ] **Disable Maestro Routing (S6):**
  ```bash
  python3 << 'EOF'
  import json
  with open('.claude/settings.json') as f:
      config = json.load(f)
  config['maestro_routing_enabled'] = True  # keep maestro enabled
  config['s6_enabled'] = False               # disable S6 only
  with open('.claude/settings.json', 'w') as f:
      json.dump(config, f, indent=2)
  print("✓ S6 disabled in maestro routing")
  EOF
  ```

- [ ] **Verify No New S6 Runs:**
  ```bash
  # Check Supabase for new S6 runs after stop time
  # SELECT COUNT(*) FROM agent_runs WHERE agent_id = 'manta-03-s6' AND created_at > NOW() - INTERVAL '5 min'
  # Expected: 0 (no new runs)
  ```

- [ ] **Pause Background Tasks (if still running):**
  ```bash
  # Kill any running jobs (if needed):
  pkill -f "rag_reindex_job|embedding_retrain_job|memory_purge_job"
  ```

### STEP 3 — REVERT CODE & CONFIGURATION (15 min)

- [ ] **Revert CLAUDE.md to v4.2:**
  ```bash
  git checkout HEAD~N CLAUDE.md  # or use backup
  # or: cp CLAUDE.md.v4.2.backup CLAUDE.md
  # Verify: grep "v4.2\|v5.0" CLAUDE.md | head -1
  ```

- [ ] **Revert Skills to v4.9:**
  ```bash
  # Check if v4.9 exists
  [ -f .backup/agente-portos.v4.9.md ] && \
    cp .backup/agente-portos.v4.9.md .claude/agents/agente-portos.v4.9.md
  
  # If git history available:
  git checkout HEAD~N .claude/agents/agente-portos.v4.9.md
  ```

- [ ] **Revert Settings.json Pinning:**
  ```bash
  python3 << 'EOF'
  import json
  with open('.claude/settings.json') as f:
      config = json.load(f)
  # Change S6 pin to v4.9
  config['skill_version_pin']['agente-portos'] = 'v4.9'
  config['s6_enabled'] = False
  with open('.claude/settings.json', 'w') as f:
      json.dump(config, f, indent=2)
  print("✓ S6 pinned to v4.9, disabled")
  EOF
  ```

- [ ] **Revert VERSIONS.json Checksums:**
  ```bash
  # Restore v4.9 checksum entry
  python3 << 'EOF'
  import json
  with open('VERSIONS.json') as f:
      versions = json.load(f)
  # Keep v5.0 for reference, but mark as rolled-back
  versions['agente-portos']['v5.0']['rolled_back_at'] = '2026-07-25T14:35:00Z'
  versions['agente-portos']['v5.0']['rolled_back_reason'] = 'routing accuracy < 60%'
  with open('VERSIONS.json', 'w') as f:
      json.dump(versions, f, indent=2)
  print("✓ VERSIONS.json updated")
  EOF
  ```

- [ ] **Git Revert Commit:**
  ```bash
  git revert --no-edit HEAD  # creates new commit that undoes S6 deploy
  # or: git reset --soft HEAD~1 (if not yet pushed)
  ```

### STEP 4 — RESTORE DATABASE (15 min)

- [ ] **Backup Current (Broken) State:**
  ```bash
  pg_dump -h $SUPABASE_HOST -U postgres -d postgres \
    | gzip > backups/rag_v5.0_failed_$(date +%s).sql.gz
  echo "✓ Failed v5.0 state backed up"
  ```

- [ ] **Check Backup Availability:**
  ```bash
  ls -lh backups/rag_v4.9_pre_s6_*.sql.gz | head -1
  # Expected: file exists and is recent (within 24h)
  ```

- [ ] **Restore v4.9 RAG Collections:**
  ```bash
  # Option A: Full restore from backup
  # gunzip < backups/rag_v4.9_pre_s6_XXXXX.sql.gz | psql -h $SUPABASE_HOST -U postgres -d postgres
  
  # Option B: Selective restore (if backup not available)
  # SQL to delete S6 artifacts:
  psql -h $SUPABASE_HOST -U postgres -d postgres << 'SQL'
  DELETE FROM rag_chunks WHERE collection LIKE 'por:v5.0%';
  DELETE FROM rag_metadata WHERE collection LIKE 'por:v5.0%';
  DELETE FROM rag_cache WHERE collection LIKE 'por:v5.0%';
  DELETE FROM agent_runs WHERE agent_id = 'manta-03-s6' AND created_at > NOW() - INTERVAL '2 hours';
  DELETE FROM agent_feedback WHERE run_id IN (SELECT run_id FROM agent_runs WHERE agent_id = 'manta-03-s6');
  VACUUM ANALYZE;
  SQL
  echo "✓ S6 artifacts removed"
  ```

- [ ] **Verify RAG Collections:**
  ```bash
  # Check that v4.9 collections are intact:
  psql -h $SUPABASE_HOST -U postgres -d postgres << 'SQL'
  SELECT collection, COUNT(*) as chunk_count FROM rag_chunks
    WHERE collection NOT LIKE 'por:v5.0%'
    GROUP BY collection ORDER BY collection;
  SQL
  # Expected: rod:v4.9, oae:v4.9, fer:v4.9, met:v4.9 with > 0 chunks
  ```

- [ ] **Verify No Orphaned Triggers:**
  ```bash
  psql -h $SUPABASE_HOST -U postgres -d postgres << 'SQL'
  SELECT * FROM agent_triggers WHERE trigger_id LIKE '%s6%' OR name LIKE '%portos%';
  -- Should be empty or marked as disabled
  SQL
  ```

### STEP 5 — VERIFY ROLLBACK (10 min)

- [ ] **Check Skills Reverted:**
  ```bash
  md5sum .claude/agents/agente-portos.v4.9.md
  # Should match v4.9 checksum in VERSIONS.json
  ```

- [ ] **Verify Maestro Routing (S6 Disabled):**
  ```bash
  python3 << 'EOF'
  from maestro import route
  prompt = "Porto de Santos projeto de dragagem"
  result = route(prompt)
  # Expected: either S1 (rodovias) or fallback, NOT S6
  assert result['agent_id'] != 'manta-03-s6', "S6 still routing!"
  print(f"✓ S6 disabled. Routed to: {result['agent_id']}")
  EOF
  ```

- [ ] **Test v4.9 RAG:**
  ```bash
  python3 << 'EOF'
  from rag import query_bm25
  # Test query for existing (non-S6) collection
  results = query_bm25("rodovia pavimento DNIT", collection="rod:v4.9:chunks")
  assert len(results) > 0
  print("✓ v4.9 RAG collections functional")
  EOF
  ```

- [ ] **Verify Database Integrity:**
  ```bash
  psql -h $SUPABASE_HOST -U postgres -d postgres << 'SQL'
  -- Check for data corruption
  SELECT COUNT(*) FROM agent_runs WHERE agent_id IS NULL;
  SELECT COUNT(*) FROM rag_chunks WHERE text IS NULL;
  SELECT COUNT(*) FROM agent_feedback WHERE run_id IS NULL;
  -- All should return 0
  SQL
  ```

### STEP 6 — RESTART SERVICES (10 min)

- [ ] **Restart Scheduler (with S6 disabled):**
  ```bash
  systemctl start manta-scheduler
  sleep 5
  systemctl status manta-scheduler
  # Expected: "active (running)"
  ```

- [ ] **Warm-up Requests (non-S6):**
  ```bash
  for i in 1 2 3; do
    python3 << EOF
  from maestro import process_prompt
  response = process_prompt(f"Warmup query {i} rodovia")
  assert response['status'] == 'success'
  assert response['agent_id'] != 'manta-03-s6'
  print(f"✓ Warmup {i} OK")
  EOF
  done
  ```

### STEP 7 — VERIFY PRODUCTION STABLE (10 min)

- [ ] **Health Check (Full System):**
  ```bash
  python3 scripts/healthcheck.py --full
  # Expected: all green (no critical, <5 warnings)
  ```

- [ ] **Monitor Logs for Errors:**
  ```bash
  # Check last 5 min for errors:
  grep -i "error\|fatal\|panic" logs/*.log | tail -20
  # Should show NO errors related to maestro/routing
  ```

- [ ] **Grafana Dashboard Check:**
  ```bash
  # Manual: Open Grafana and verify:
  # - Error rate back to < 1%
  # - Latency p95 < 5s
  # - S6 metrics GONE (no S6 runs visible)
  ```

### STEP 8 — POST-ROLLBACK COMMUNICATION (5 min)

- [ ] **Slack #agent-ops Final Status:**
  ```
  ✅ **S6 Rollback Complete**
  
  Timeline:
  - Start: 2026-07-25T14:30:00Z
  - End: 2026-07-25T14:55:00Z
  - Duration: 25 min
  - **RTO achieved: 25 min (target: 60 min)** ✓
  
  Actions taken:
  - Maestro S6 routing disabled
  - Skills reverted to v4.9
  - RAG v4.9 collections restored
  - APScheduler restarted
  
  Status: ✅ Production stable
  Error rate: 0.2% (normal)
  Latency: p95 = 3.2s (normal)
  
  Post-incident: Root cause analysis scheduled
  Next steps: MN to review incident + plan fixes
  ```

- [ ] **Email Notification:**
  - To: @mantaassociados.com
  - Subject: `[RESOLVED] Manta 03-S6 Rollback Complete`
  - Body: Include timeline, actions, and status

- [ ] **Update ROLLBACK_LOG.md:**
  ```markdown
  ## Rollback Event 001 (2026-07-25T14:30:00Z)
  
  Reason: Routing accuracy dropped to 58% after S6 launch
  Decision: MN approved at T+10min
  Start time: 2026-07-25T14:30:00Z
  End time: 2026-07-25T14:55:00Z
  Duration: 25 min
  RTO: 25 min (target: 60 min) ✓
  
  Lead: [operator name]
  
  Actions:
  - ✓ Maestro S6 routing disabled
  - ✓ Skills reverted to v4.9
  - ✓ RAG collections restored from backup
  - ✓ Scheduler restarted
  
  Verification:
  - ✓ v4.9 RAG functional
  - ✓ Health check OK
  - ✓ No errors in logs
  - ✓ Grafana metrics normal
  
  Status: COMPLETE (2026-07-25T14:55:00Z)
  ```

---

## POST-ROLLBACK ANALYSIS (Next 24h)

### Root Cause Analysis
- [ ] **Collect Logs & Metrics:**
  ```bash
  # Export agent_runs for S6 (v5.0 deployment):
  psql -h $SUPABASE_HOST -U postgres -d postgres << 'SQL' > s6_v5.0_runs.csv
  SELECT run_id, agent_id, model_tier, latency_ms, status, error_message, created_at
    FROM agent_runs
    WHERE agent_id = 'manta-03-s6'
    ORDER BY created_at DESC
    LIMIT 100;
  SQL
  ```

- [ ] **Analyze Routing Accuracy:**
  ```bash
  python3 << 'EOF'
  import pandas as pd
  runs = pd.read_csv('s6_v5.0_runs.csv')
  print(f"Total S6 runs: {len(runs)}")
  print(f"Success: {(runs['status'] == 'success').sum()}")
  print(f"Errors: {(runs['status'] == 'error').sum()}")
  print(f"Timeouts: {(runs['status'] == 'timeout').sum()}")
  print(f"Avg latency: {runs['latency_ms'].mean():.0f}ms")
  EOF
  ```

- [ ] **Review Error Messages:**
  ```bash
  grep "error_message" s6_v5.0_runs.csv | sort | uniq -c | sort -rn | head -5
  # Identify top 5 error categories
  ```

### Issue Categories

**If issue is:** → **Action:**

| Issue | Root Cause | Fix for Re-Launch |
|-------|-----------|-------------------|
| Routing accuracy low | Keyword rules incomplete or embedding OOD | Re-validate keyword list; retrain embedding |
| RAG empty/broken | Ingestion failed or checkpoint issue | Re-ingest `por:v5.0:chunks` from source docs |
| Tiering wrong | Complexity formula bug or weights off | Review formula, validate with test cases |
| Reranker failing | Model timeout or unavailable | Increase timeout, or disable reranker initial |
| Fallback cascading too much | Timeout threshold too aggressive | Increase timeout_sec in fallback-config |

---

## PREVENT FUTURE INCIDENTS

### Immediate (before re-launch attempt)
- [ ] Fix root cause (see issue categories above)
- [ ] Run extended test suite: `pytest tests/ -v --tb=short`
- [ ] Increase monitoring thresholds: routing accuracy trigger at 75% (not 60%)

### Longer-term (architectural)
- [ ] Add **canary deployment**: Route 5% of S6 queries to v5.0, 95% to v4.9
- [ ] Implement **automated rollback**: If routing accuracy drops > 10% in 5 min, auto-rollback
- [ ] Add **staging environment**: Full v5.0 test in staging before prod launch
- [ ] **A/B test framework**: Compare v4.9 vs v5.0 latency/accuracy side-by-side

---

## EMERGENCY CONTACTS

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Decision Maker | MN | mneves@mantaassociados.com | [fill in] |
| Tech Lead | [Fill in] | [email] | [phone] |
| DBA | [Fill in] | [email] | [phone] |
| DevOps | [Fill in] | [email] | [phone] |

---

## ROLLBACK TIMING ESTIMATE

| Step | Time (min) | Cumulative |
|------|----------|-----------|
| 1. Declare incident | 5 | 5 |
| 2. Stop services | 10 | 15 |
| 3. Revert code | 15 | 30 |
| 4. Restore database | 15 | 45 |
| 5. Verify rollback | 10 | 55 |
| 6. Restart services | 10 | 65 |
| 7. Verify production | 10 | 75 |
| 8. Communicate | 5 | 80 |
| **Total (Buffer included)** | — | **< 60 min** ✓ |

---

## SIGN-OFF

**Prepared by:** Claude AI (Codex-exemplo Agent)  
**Date:** 2026-07-25  
**Reviewed by:** _____________________ (Tech Lead)  
**Approved by:** _____________________ (MN)  

**Timestamp of approval:** _____________________

---

**End of S6 Rollback Plan**
