# Deployment Checklist — Observabilidade P6

**Versão:** 2026-07-25  
**Ticket:** MNT-2026-MAESTRO-OBSERVABILITY-P6  
**Duração estimada:** 2-4 horas  
**Responsável:** DevOps + Maestro team

---

## PHASE 1 — Preparação (sem alteração em produção)

- [ ] **Validar dependências:**
  ```bash
  pip install supabase-py python-dotenv APScheduler pytz psycopg2-binary
  ```

- [ ] **Revisar arquivos criados:**
  - [ ] `supabase/migrations/2026_07_25_observability_maestro_runs.sql`
  - [ ] `scripts/setup_maestro_runs.py`
  - [ ] `.claude/hooks/subagentstop_maestro_observability.py`
  - [ ] `docs/grafana_maestro_dashboard.json`
  - [ ] `docs/OBSERVABILITY_P6_GUIDE.md`

- [ ] **Validar environment:**
  - [ ] `.env` contém `SUPABASE_URL`
  - [ ] `.env` contém `SUPABASE_KEY` (service_role)
  - [ ] `.env` contém `POSTGRES_CONNECTION_STRING` (opcional, para validações)
  - [ ] Supabase account acessível

- [ ] **Clonar repo para staging:**
  ```bash
  git clone <repo> /tmp/maestro-p6-staging
  cd /tmp/maestro-p6-staging
  ```

---

## PHASE 2 — Schema & Migrations (T-2h)

- [ ] **Aplicar migration SQL:**
  ```bash
  supabase db push
  # ou manualmente:
  psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_observability_maestro_runs.sql
  ```

  **Validar:**
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name LIKE 'maestro_%';
  -- Esperado: maestro_runs, maestro_runs_archive, maestro_feedback
  ```

- [ ] **Validar indexes:**
  ```bash
  python scripts/setup_maestro_runs.py --init
  # Deve retornar: ✓ Schema validado com sucesso
  ```

- [ ] **Validar RLS policies:**
  ```bash
  psql "$SUPABASE_DB_URL" -c "
    SELECT policyname, tablename 
    FROM pg_policies 
    WHERE tablename LIKE 'maestro_%';"
  # Esperado: 6 policies (select_own, no_update, no_delete, insert_service, feedback_*)
  ```

- [ ] **Validar views analíticas:**
  ```bash
  psql "$SUPABASE_DB_URL" -c "
    SELECT viewname FROM pg_views 
    WHERE schemaname = 'public' 
    AND viewname LIKE 'vw_%';"
  # Esperado: vw_cost_by_agent_daily, vw_latency_by_agent, etc.
  ```

---

## PHASE 3 — Testes (T-1h)

- [ ] **Health check completo:**
  ```bash
  python scripts/setup_maestro_runs.py --health-check
  ```

  **Esperado output:**
  ```
  ======================================================
  MAESTRO RUNS — HEALTH CHECK
  ======================================================
  ✓ PASS: Schema
  ✓ PASS: Indexes
  ✓ PASS: RLS Policies
  ✓ PASS: Mock Insert
  ======================================================
  Result: 4/4 checks passed
  ✓ Health check PASSED
  ```

- [ ] **Teste mock de run:**
  ```bash
  python .claude/hooks/subagentstop_maestro_observability.py
  ```

  **Esperado:**
  ```
  ✓ Run gravada com sucesso: [UUID]
  (agent=manta-03-s8, status=success, cost=$0.000150)
  ```

- [ ] **Query de validação:**
  ```bash
  psql "$SUPABASE_DB_URL" << 'EOF'
  SELECT COUNT(*) as total_runs, 
         SUM(cost_usd) as total_cost,
         AVG(latency_ms) as avg_latency_ms
  FROM maestro_runs
  WHERE status = 'success';
  EOF
  ```

- [ ] **Testar archive (simulação):**
  ```bash
  # Inserir run "antiga" com created_at = 91 dias atrás
  psql "$SUPABASE_DB_URL" << 'EOF'
  INSERT INTO maestro_runs (
    user_id, session_id, agent_id, skill_id, model_tier,
    input_tokens, output_tokens, cost_usd, latency_ms, 
    status, routing_confidence, created_at
  ) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test-old-run',
    'manta-test',
    'test.v5.0',
    'haiku-4-5',
    100, 50, 0.00005, 1000,
    'success', 0.9,
    NOW() - INTERVAL '91 days'
  );
  EOF

  # Executar archive
  python scripts/setup_maestro_runs.py --archive --days-threshold 90

  # Validar que run foi arquivada
  psql "$SUPABASE_DB_URL" -c "
    SELECT is_archived FROM maestro_runs 
    WHERE session_id = 'test-old-run';"
  # Esperado: is_archived = true
  ```

---

## PHASE 4 — Integração Hook (T-30min)

- [ ] **Configurar hook em `.claude/settings.json`:**

  ```json
  {
    "hooks": {
      "SubagentStop": {
        "enabled": true,
        "handler": "./.claude/hooks/subagentstop_maestro_observability.py",
        "async": true,
        "timeout_ms": 5000,
        "retry": {
          "max_attempts": 2,
          "backoff_ms": 1000
        }
      }
    }
  }
  ```

- [ ] **Testar hook com mock event:**
  ```bash
  python -c "
  import sys
  sys.path.insert(0, '.claude/hooks')
  from subagentstop_maestro_observability import on_subagent_stop
  
  event = {
      'agent_id': 'manta-03-s8',
      'skill_id': 'agente-saneamento.v5.0',
      'session_id': 'hook-test-001',
      'user_id': '550e8400-e29b-41d4-a716-446655440000',
      'model_tier': 'haiku-4-5',
      'input_tokens': 500,
      'output_tokens': 200,
      'latency_ms': 1500,
      'status': 'success',
      'context': {
          'phase': 'projeto-basico',
          'routing_confidence': 0.85,
          'rag_collection': 'san:v5.0:chunks',
          'rag_reranker_score': 0.75,
          'complexity_score': 1.5,
          'fallback_model': None,
          'keywords_matched': 2
      }
  }
  
  result = on_subagent_stop(event)
  print(f'Hook result: {result}')
  print('Success!' if result['success'] else 'Failed!')
  "
  ```

---

## PHASE 5 — Grafana Setup (T-20min)

- [ ] **Configurar data source Supabase no Grafana:**

  ```bash
  # 1. Abrir Grafana
  open http://localhost:3000
  # (ou seu Grafana URL)

  # 2. Configuration → Data Sources → New
  # Type: PostgreSQL
  # Host: db.xxxxx.supabase.co
  # Port: 5432
  # Database: postgres
  # User: postgres
  # Password: [SUPABASE_PASSWORD]
  # SSL Mode: require
  # Name: "Supabase Maestro"
  # Test & Save
  ```

- [ ] **Importar dashboard:**

  ```bash
  # Grafana → Dashboards → Import
  # Upload: docs/grafana_maestro_dashboard.json
  # Select data source: "Supabase Maestro"
  # Import
  ```

- [ ] **Validar painéis:**
  - [ ] "Custo por Agente" — mostra dados agregados
  - [ ] "Taxa de Erro" — tabela com agent_id, error_rate_pct
  - [ ] "Latência (p50/p95/p99)" — gráfico de barras
  - [ ] "Feedback Distribution" — pie chart
  - [ ] "Model Tier Distribution" — pie/donut chart
  - [ ] "Top 10 Runs" — tabela com run_ids

- [ ] **Configurar refresh interval:**
  - [ ] Dashboard → Settings → Refresh interval: 30s
  - [ ] Save dashboard

---

## PHASE 6 — APScheduler Jobs (T-15min)

- [ ] **Instalar APScheduler:**
  ```bash
  pip install APScheduler pytz
  ```

- [ ] **Testar job de archive:**
  ```bash
  python scripts/setup_maestro_runs.py --archive --days-threshold 90
  # Esperado: ✓ X runs arquivadas com sucesso
  ```

- [ ] **Iniciar scheduler em background (ou systemd):**

  **Opção 1: Background direto**
  ```bash
  nohup python scripts/setup_maestro_runs.py --schedule-jobs > /tmp/maestro_scheduler.log 2>&1 &
  echo $! > /tmp/maestro_scheduler.pid
  ```

  **Opção 2: Systemd (produção)**
  ```bash
  sudo tee /etc/systemd/system/maestro-scheduler.service > /dev/null << 'EOF'
  [Unit]
  Description=Maestro Scheduler (P6 Observabilidade)
  After=network.target

  [Service]
  Type=simple
  User=maestro
  WorkingDirectory=/app
  ExecStart=/usr/bin/python3 /app/scripts/setup_maestro_runs.py --schedule-jobs
  Restart=always
  RestartSec=10
  StandardOutput=journal
  StandardError=journal

  [Install]
  WantedBy=multi-user.target
  EOF

  sudo systemctl daemon-reload
  sudo systemctl enable maestro-scheduler
  sudo systemctl start maestro-scheduler
  sudo systemctl status maestro-scheduler
  ```

- [ ] **Validar scheduler está rodando:**
  ```bash
  # Verificar log
  tail -f /tmp/maestro_scheduler.log
  # ou
  journalctl -u maestro-scheduler -f
  ```

---

## PHASE 7 — Alertas Slack (Opcional) (T-10min)

- [ ] **Configurar webhook Slack:**

  ```bash
  # 1. Criar Slack app: https://api.slack.com/apps
  # 2. Ativar "Incoming Webhooks"
  # 3. Gerar webhook URL para #agent-ops
  # 4. Adicionar a .env:
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
  ```

- [ ] **Adicionar alerta ao APScheduler:**

  ```python
  # scripts/setup_maestro_runs.py (dentro de schedule_background_jobs)

  def job_alert_errors():
      errors = supabase.rpc('get_error_stats_last_hour').execute()
      if errors.data:
          msg = "🚨 Maestro Error Alert\n"
          for row in errors.data:
              msg += f"- {row['agent_id']}: {row['error_count']} erros/hora\n"
          
          import requests
          requests.post(
              os.getenv('SLACK_WEBHOOK_URL'),
              json={'text': msg}
          )

  scheduler.add_job(job_alert_errors, 'interval', minutes=5)
  ```

---

## PHASE 8 — Documentação & Runbook (T-10min)

- [ ] **Atualizar README com link para P6:**
  ```markdown
  ## Observabilidade (P6)
  - Dashboard: [Grafana Maestro](http://grafana/d/maestro-observability-p6)
  - Schema: `docs/OBSERVABILITY_P6_GUIDE.md`
  - Deployment: `docs/DEPLOYMENT_P6_CHECKLIST.md`
  ```

- [ ] **Criar runbook de troubleshooting:**
  ```markdown
  # Troubleshooting P6

  ## Query: Listar erros da última hora
  SELECT run_id, agent_id, status, error_message, latency_ms
  FROM maestro_runs
  WHERE created_at > NOW() - INTERVAL '1 hour'
    AND status IN ('error', 'timeout')
  ORDER BY created_at DESC;

  ## Query: Custo total por agente hoje
  SELECT agent_id, COUNT(*) as run_count, SUM(cost_usd) as total_cost
  FROM maestro_runs
  WHERE DATE(created_at) = CURRENT_DATE
  GROUP BY agent_id
  ORDER BY total_cost DESC;

  ## Alert: Erro rate > 5%
  SELECT * FROM vw_error_rate_by_agent WHERE error_rate_pct > 5;
  ```

- [ ] **Commit changes:**
  ```bash
  git add supabase/migrations/ scripts/ .claude/hooks/ docs/
  git commit -m "feat(P6): Observabilidade maestro_runs — append-only logging + Grafana dashboard"
  git push origin main
  ```

---

## PHASE 9 — Go-Live (T+0)

- [ ] **Último health check:**
  ```bash
  python scripts/setup_maestro_runs.py --health-check
  # Esperado: ✓ All checks passed
  ```

- [ ] **Monitorar por 1 hora:**
  - [ ] Grafana dashboard carregando dados
  - [ ] Sem erros em logs (APScheduler, Supabase)
  - [ ] Runs sendo gravadas corretamente

- [ ] **Notificar team:**
  ```
  Slack #agent-ops:
  ✅ P6 Observabilidade (maestro_runs) ativado
  - Log imutável append-only
  - Dashboard: [link]
  - Archive diário: 02:00 UTC
  - Runbook: docs/OBSERVABILITY_P6_GUIDE.md
  ```

---

## PHASE 10 — Pós-Launch (24–72h)

- [ ] **Monitorar métricas:**
  - [ ] Error rate < 1% por agente
  - [ ] Latência p99 < 10s
  - [ ] Custo médio < $0.01 por run
  - [ ] Dashboard latência < 2s

- [ ] **Coletar feedback:**
  - [ ] Maestro team: usabilidade do schema?
  - [ ] Product: satisfação (feedback score)?
  - [ ] DevOps: observabilidade adequada?

- [ ] **Ajustar alertas:**
  - [ ] Thresholds de error rate (hoje: > 5%)
  - [ ] Thresholds de timeout rate (hoje: > 2%)
  - [ ] Thresholds de latência p99 (hoje: > 30s)

- [ ] **Agendar gate humano (MN approval):**
  - Reunião: 72h após launch
  - Feedback de usuários
  - Decisão: keep ou rollback

---

## ROLLBACK (if needed)

Se problemas críticos detectados:

```bash
# Step 1: Desativar hook SubagentStop
# Editar .claude/settings.json:
# "hooks.SubagentStop.enabled": false

# Step 2: Parar scheduler
systemctl stop maestro-scheduler

# Step 3: Remover migration (se necessário)
# Nota: Schema não tem UP/DOWN automático em Supabase
# Executar manualmente em psql:
psql $SUPABASE_DB_URL << 'EOF'
DROP TABLE maestro_feedback CASCADE;
DROP TABLE maestro_runs_archive CASCADE;
DROP TABLE maestro_runs CASCADE;
DROP FUNCTION archive_old_maestro_runs();
DROP FUNCTION calculate_run_cost(TEXT, INT, INT);
-- Drop views
DROP VIEW vw_cost_by_agent_daily;
DROP VIEW vw_latency_by_agent;
DROP VIEW vw_error_rate_by_agent;
DROP VIEW vw_model_tier_distribution;
DROP VIEW vw_feedback_distribution;
DROP VIEW vw_top_cost_runs;
EOF

# Step 4: Commit rollback
git revert <commit-P6>
git push origin main

# Step 5: Notificar
Slack #agent-ops: ❌ P6 rolled back — reason: [issue]
```

---

## SLA & Métricas de Sucesso

| Métrica | Target | Limite |
|---------|--------|--------|
| Health check pass | 100% | 0 falhas |
| Dashboard latência | < 2s | 5s |
| Archive completude | 100% | 0 runs perdidas |
| RLS enforcement | 100% | 0 data leaks |
| Hook success rate | > 99% | < 1 erro/1000 |
| Cost accuracy | ±0.1% | ±1% |

---

## Contatos & Escalação

| Papel | Responsável | Slack | Escalação |
|-------|-------------|-------|-----------|
| Maestro Lead | MN (mneves@) | @mneves | Arquiteto IA |
| DevOps | [TBD] | @devops | VP Eng |
| Database | [TBD] | @dba | VP Eng |

---

## Documentação de Referência

- [P6 Guide](./OBSERVABILITY_P6_GUIDE.md)
- [Schema SQL](../supabase/migrations/2026_07_25_observability_maestro_runs.sql)
- [Setup Script](../scripts/setup_maestro_runs.py)
- [Hook Code](./../.claude/hooks/subagentstop_maestro_observability.py)
- [Grafana Dashboard](./grafana_maestro_dashboard.json)

---

**Versão:** 2026-07-25 | **Status:** Production-ready | **Aprovação:** Pendente (MN) | **ETA Deploy:** 2h
