# Shadow Mode Pre-Flight Checklist — Jul 21 (1 day before)

**Go/No-Go Decision**: Must complete by 18:00 UTC Jul 21  
**Deployment Window**: Jul 22 00:00–06:00 UTC  
**Rollback Available Until**: Aug 21 23:59 UTC

---

## ✈️ PHASE 1: Code Readiness (1 hour)

### Git & Build
- [ ] Branch `claude/manta-maestro-cag-ml-8wdrg4` is on `main`
  ```bash
  git log --oneline -1
  # Expected: Latest commit from this branch
  ```

- [ ] All 91 tests passing locally
  ```bash
  python -m pytest cag/tests/ -v
  # Expected: 91 passed in X.XXs
  ```

- [ ] CI workflow green on latest push
  - [ ] test.yml job passed
  - [ ] No red status checks

- [ ] Docker image builds cleanly
  ```bash
  docker build -t manta/cag-shadow-mode:v1.0 .
  # Expected: Successfully built [hash]
  ```

- [ ] requirements.txt installs without errors
  ```bash
  pip install -r requirements.txt
  # Expected: Successfully installed [packages]
  ```

**Owner**: Backend lead | **Sign-off**: \_\_\_\_\_\_\_\_\_\_\_

---

## 🗄️ PHASE 2: Database Readiness (45 min)

### Supabase Setup (Staging)
- [ ] Connect to staging Supabase
  ```bash
  export SUPABASE_URL="https://xxxxx.supabase.co"
  export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  ```

- [ ] Migration file exists and validated
  ```bash
  ls -la supabase/migrations/2026_07_22_v1_0_shadow_mode.sql
  wc -l supabase/migrations/2026_07_22_v1_0_shadow_mode.sql
  # Expected: ~410 lines
  ```

- [ ] Dry run migration on staging
  ```bash
  supabase db push --dry-run
  # Review changes, no errors
  ```

- [ ] Apply to staging
  ```bash
  supabase db push --remote
  # Expected: Migration applied successfully
  ```

- [ ] Verify tables in staging
  ```sql
  SELECT tablename FROM pg_tables 
  WHERE tablename LIKE 'cag_shadow_%';
  -- Expected: cag_shadow_config, cag_shadow_daily_stats, cag_shadow_logs
  ```

- [ ] Verify config table populated
  ```sql
  SELECT COUNT(*) FROM cag_shadow_config;
  -- Expected: 9 rows (enabled, start_date, end_date, buffer_size, agent_match_threshold, 
  --                    latency_threshold_pct, error_threshold, comparison_mode, debug_logging)
  ```

- [ ] Test daily stats function
  ```sql
  INSERT INTO cag_shadow_logs (
    session_id, query, timestamp, rag_agent, rag_latency_ms, 
    rag_confidence, rag_response_text, cag_selected_agents, 
    cag_latency_ms, cag_avg_confidence, cag_final_response, 
    agent_match, confidence_delta, latency_delta_ms, latency_delta_pct
  ) VALUES (
    'test-001', 'Test query', NOW(), 'agente-saneamento', 
    1000, 0.85, 'Test RAG response', ARRAY['agente-saneamento'], 
    1050, 0.88, 'Test CAG response', TRUE, 0.03, 50, 5.0
  );
  
  SELECT fn_compute_shadow_daily_stats(CURRENT_DATE);
  
  SELECT * FROM cag_shadow_daily_stats WHERE date_bucket = CURRENT_DATE;
  -- Expected: One row with computed stats
  ```

- [ ] Cleanup test data
  ```sql
  DELETE FROM cag_shadow_logs WHERE session_id = 'test-001';
  DELETE FROM cag_shadow_daily_stats WHERE date_bucket = CURRENT_DATE;
  ```

**Owner**: DBA | **Sign-off**: \_\_\_\_\_\_\_\_\_\_\_

---

## 🔧 PHASE 3: Infrastructure Readiness (30 min)

### Environment & Secrets
- [ ] Production Supabase credentials available (not in git)
  ```bash
  echo $SUPABASE_URL | grep -q "supabase.co" && echo "✓ URL set"
  echo $SUPABASE_KEY | wc -c | grep -q "^[2-9][0-9][0-9]" && echo "✓ KEY set"
  ```

- [ ] Anthropic API key available
  ```bash
  echo $ANTHROPIC_API_KEY | wc -c | grep -q "^[2-9][0-9][0-9]" && echo "✓ API key set"
  ```

- [ ] Environment variables documented in `.env.example`
  ```bash
  grep -E "SUPABASE|ANTHROPIC|SHADOW" .env.example
  # Expected: All required vars listed with descriptions
  ```

### Kubernetes Readiness
- [ ] Namespace exists
  ```bash
  kubectl get namespace manta-shadow-mode 2>/dev/null || \
    kubectl create namespace manta-shadow-mode
  ```

- [ ] Secrets created
  ```bash
  kubectl get secrets -n manta-shadow-mode | grep -E "supabase|anthropic"
  # Expected: At least supabase-secret and anthropic-secret
  ```

- [ ] ConfigMap ready
  ```bash
  kubectl get configmap -n manta-shadow-mode shadow-mode-config
  # Expected: ConfigMap exists with debug_logging=false
  ```

- [ ] Deployment manifest reviewed
  ```bash
  cat k8s/shadow-mode-deployment.yaml | grep -E "image:|replicas:|resources:"
  # Verify: appropriate image tag, 2-3 replicas, resource limits set
  ```

**Owner**: DevOps lead | **Sign-off**: \_\_\_\_\_\_\_\_\_\_\_

---

## 📋 PHASE 4: Documentation & Communication (15 min)

### Internal Docs Ready
- [ ] Deployment checklist complete ([DEPLOYMENT_CHECKLIST_JUL22.md](./DEPLOYMENT_CHECKLIST_JUL22.md))
- [ ] Operations guide published ([SHADOW_MODE_OPERATIONS.md](./SHADOW_MODE_OPERATIONS.md))
- [ ] Rollback procedure documented and tested
- [ ] Alert thresholds configured in monitoring

### Stakeholder Notification
- [ ] Announcement sent to #maestro-cag
  ```
  📢 Shadow Mode Deployment Tomorrow (Jul 22 00:00 UTC)
  
  ✅ 91 tests passing
  ✅ DB migration ready
  ✅ All systems go
  
  🔍 What to expect:
  - Parallel CAG vs RAG comparison for 30 days
  - Zero impact to users (RAG still returned)
  - New logs in cag_shadow_logs
  - Daily metrics in cag_shadow_daily_stats
  
  ⚠️ Monitoring: Active throughout 30-day window
  
  Contact: @DevOps if issues
  ```

- [ ] On-call schedule updated
- [ ] War room Slack channel created (#shadow-mode-incident if needed)
- [ ] MN informed and approved

**Owner**: Product Manager | **Sign-off**: \_\_\_\_\_\_\_\_\_\_\_

---

## ✅ FINAL SIGN-OFF (All roles)

### Gate Criteria
All of the following must be checked:
- [ ] Code: All tests passing, CI green
- [ ] Database: Migration tested on staging, tables verified
- [ ] Infrastructure: Secrets, configs, K8s ready
- [ ] Documentation: Guides complete, team notified
- [ ] Decision: MN approved deployment

### Sign-Off Table

| Role | Name | Timestamp | Status |
|------|------|-----------|--------|
| Backend Lead | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | ✓ GO / ✗ NO-GO |
| DBA | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | ✓ GO / ✗ NO-GO |
| DevOps Lead | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | ✓ GO / ✗ NO-GO |
| Product Manager | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | ✓ GO / ✗ NO-GO |
| MN (Final Decision) | \_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_ | ✓ APPROVED / ✗ DENIED |

---

## 🚨 IF ANY SIGN-OFF IS "NO-GO"

**DO NOT DEPLOY ON JUL 22**

### Remediation Steps
1. Identify blocker(s)
2. Document in ticket (link here): `MNT-XXXX-SHADOW-BLOCKER`
3. Fix or defer
4. Re-run pre-flight checklist
5. Request new sign-offs

### Rescheduling
- **Option A**: Delay 24-48 hours, re-run this checklist
- **Option B**: Reduce scope (defer secondary agents), deploy core only
- **Option C**: Extend deadline to next week

**DO NOT bypass this gate.**

---

## 🎯 Deployment Command (Reference)

On Jul 22 00:00 UTC, authorized person runs:

```bash
# 1. Production migration
supabase db push --remote  # Uses production connection

# 2. Deploy image
kubectl set image deployment/shadow-mode-main \
  shadow-mode=manta/cag-shadow-mode:v1.0 \
  -n manta-shadow-mode

# 3. Wait & verify
kubectl rollout status deployment/shadow-mode-main -n manta-shadow-mode --timeout=5m

# 4. Enable flag
psql $PROD_SUPABASE_DB -c "
  UPDATE cag_shadow_config 
  SET value = 'true' 
  WHERE key = 'enabled' AND value = 'false';"

# 5. Check logs
kubectl logs -f deployment/shadow-mode-main -n manta-shadow-mode --tail=50

echo "✅ Deployment complete. Monitoring shadow mode logs..."
```

---

**Pre-Flight Checklist Created**: 2026-07-20  
**Target Deployment**: Jul 22 00:00 UTC  
**30-Day Window Ends**: Aug 21 23:59 UTC  
**Final GO/NO-GO**: Required by Jul 21 18:00 UTC
