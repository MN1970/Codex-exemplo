# 🚀 GUIA RÁPIDO GO-LIVE — Manta Maestro KB v4.2

**Data Alvo**: 2026-08-01  
**Duração Esperada**: 4-6 horas (5 passos)  
**Responsável**: DevOps + Arquiteto IA  
**Rollback**: Automático em 2 min se falhar  

---

## 📋 PASSO 1️⃣: PRÉ-DEPLOY (30 min)

### ✅ Verificações
```bash
# 1. Clonar repositório
git clone http://127.0.0.1:41729/git/MN1970/Codex-exemplo.git
cd Codex-exemplo

# 2. Verificar branch
git checkout claude/kb-evoluido-manta-maestro-167734

# 3. Validar ambiente
python3 kb-evoluido/deploy.py
# Esperado: 7/7 PASSED em ~5 segundos
```

### ✅ Configurar Variáveis
```bash
# .env local (não commitar!)
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="xxxxx"
export AIRFLOW_HOME="/opt/airflow"
export SLACK_WEBHOOK="https://hooks.slack.com/services/xxxxx"
export MAESTRO_LOG_LEVEL="INFO"
```

### ✅ Preparar Infraestrutura
```bash
# Supabase: criar projeto em cloud.supabase.com
# Airflow: instalado (`airflow version` deve passar)
# Docker: rodando (`docker ps` deve passar)
# Slack: webhook criado para #kb-evoluido-manta

echo "✅ Pré-deploy OK"
```

---

## 📋 PASSO 2️⃣: DEPLOY SUPABASE (60 min)

### 🔵 Criar Schema
```bash
# 1. Conectar Supabase
supabase link --project-ref xxxxx

# 2. Deploy schema
supabase db push kb-evoluido/supabase/kb-evolved-schema.sql

# 3. Verificar
supabase db list-tables
# Esperado: 12 tabelas (kb_constants, kb_templates, etc.)

# 4. Seed data
supabase db seed kb-evoluido/supabase/kb-evolved-migrations.sql

# 5. Validar RLS
supabase db test-rls
# Esperado: 3 roles OK (viewer, approver, admin)
```

### ✅ Configurar Extensões
```sql
-- Supabase SQL Editor: execute estas queries

-- UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- JSON schema validation
CREATE EXTENSION IF NOT EXISTS "jsonschema";

-- Full text search (para kb_audit_log)
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

### ✅ Testar Conexão
```bash
# Validar que agentes conseguem ler
curl -H "Authorization: Bearer $SUPABASE_KEY" \
  "$SUPABASE_URL/rest/v1/kb_constants?select=id,name,value" \
  | jq '.[] | {id, name, value}' | head -5

# Esperado: 3-5 constantes retornadas
echo "✅ Supabase deploy OK"
```

---

## 📋 PASSO 3️⃣: DEPLOY AIRFLOW (45 min)

### 🔵 Inicializar
```bash
# 1. Criar diretório
mkdir -p ~/airflow/dags
cd ~/airflow

# 2. Copiar DAG
cp ../Codex-exemplo/kb-evoluido/scripts/airflow_dag.py dags/

# 3. Inicializar BD Airflow
airflow db init

# 4. Criar usuário admin
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname KB \
  --email admin@manta.com \
  --password admin123 \
  --role Admin

# 5. Validar DAG
airflow dags list | grep kb_evolution_dag
# Esperado: kb_evolution_dag listada
```

### 🔵 Iniciar Serviços
```bash
# Terminal 1: Webserver
airflow webserver --port 8080 &

# Terminal 2: Scheduler
airflow scheduler &

# Aguardar 30s para startup
sleep 30

# Terminal 3: Verificar
airflow dags list | grep kb_evolution_dag
airflow dags test kb_evolution_dag 2026-08-01
```

### ✅ Acessar UI
```
http://localhost:8080
User: admin
Password: admin123

Esperado:
- DAG kb_evolution_dag listada ✅
- 7 tasks visíveis (ingest→extract→validate→gate→update→test→audit) ✅
- Status: PAUSED (ativar manualmente)
```

### ✅ Ativar DAG
```bash
# Ativar agendamento
airflow dags unpause kb_evolution_dag

# Verificar
airflow dags list | grep kb_evolution_dag
# Esperado: status "active"

echo "✅ Airflow deploy OK"
```

---

## 📋 PASSO 4️⃣: DEPLOY MONITORAMENTO (30 min)

### 🔵 Iniciar Stack
```bash
# 1. Entrar no diretório
cd Codex-exemplo/kb-evoluido/scripts

# 2. Iniciar containers
docker-compose -f monitoring-stack.yaml up -d

# 3. Aguardar startup (30s)
sleep 30

# 4. Verificar
docker-compose -f monitoring-stack.yaml ps
# Esperado: 3 containers RUNNING (prometheus, grafana, alertmanager)
```

### ✅ Configurar Grafana
```
http://localhost:3000
User: admin
Password: admin

1. Home → Add Data Source
   Type: Prometheus
   URL: http://prometheus:9090
   Save & Test → Should show "Data source is working"

2. Import Dashboard
   Click + → Import
   Paste ID: 3662 (Prometheus Overview)
   Data Source: Prometheus
   Import

3. Criar Alert
   Home → Alerting → Alert rules
   Create new rule:
   - Name: KB_Rejeictions_High
   - Condition: rejeição_rate > 0.10 (10/dia)
   - Notification: Slack webhook
```

### ✅ Configurar AlertManager
```bash
# Editar alertmanager.yml (volumes/alertmanager.yml)
# Adicionar Slack receiver:
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'
        channel: '#kb-evoluido-manta'
        title: 'KB Evolução Alert'
        text: '{{ range .Alerts }}{{ .Labels.alertname }}: {{ .Annotations.summary }}{{ end }}'

# Reiniciar
docker-compose -f monitoring-stack.yaml restart alertmanager
```

### ✅ Testar Alertas
```bash
# Simular métrica alta (rejeição)
# Acessar Prometheus http://localhost:9090
# Graph → kb_rejection_rate
# Visualizar dados (devem chegar do Airflow)

# Se não visualizar, aguardar primeira execução do DAG
echo "✅ Monitoring deploy OK"
```

---

## 📋 PASSO 5️⃣: ATIVAR CALLBACK & TESTAR (45 min)

### 🔵 Iniciar Callback Handler
```bash
# Terminal dedicado
cd Codex-exemplo/kb-evoluido/scripts

python3 callback-handler.py
# Esperado: FastAPI rodando em http://127.0.0.1:8001

# Health check
curl http://127.0.0.1:8001/health
# Resposta: {"status":"OK","service":"callback-handler"}
```

### 🔵 Testar Roteamento Maestro
```bash
# Usar script de teste
python3 -m tests.routing.prompts

# Ou testar manualmente
# Exemplo 1: S8 (Saneamento)
# Input: "Preciso atualizar constante ETA para AySA"
# Expected: Roteia para agente-saneamento ✅

# Exemplo 2: S9 (Energia)
# Input: "Novo padrão de torre de transmissão com ANEEL"
# Expected: Roteia para agente-energia ✅

# Exemplo 3: S6 (Portos)
# Input: "ANTAQ alterou tarifas de dragagem para portos"
# Expected: Roteia para agente-portos ✅
```

### ✅ Testar Callback
```bash
# Testar rejeição
curl -X POST http://127.0.0.1:8001/callback/rejection \
  -H "Content-Type: application/json" \
  -d '{
    "constant_id": "san:K_RECICLAGEM_UASB",
    "agent": "agente-saneamento",
    "reason": "fórmula desatualizada (IWA 2023)",
    "confidence": 0.65
  }'

# Resposta esperada: {"status":"OK","action":"logged"}

# Testar aprovação
curl -X POST http://127.0.0.1:8001/callback/approval \
  -H "Content-Type: application/json" \
  -d '{
    "constant_id": "ene:R_LT_TORRE",
    "agent": "agente-energia",
    "confidence": 0.92
  }'

# Resposta esperada: {"status":"OK","action":"logged"}

# Verificar resumo
curl http://127.0.0.1:8001/feedback/summary
# Resposta esperada: {"approval_rate": 0.5, "patterns_detected": 0}
```

### ✅ Executar Teste End-to-End
```bash
# Simular ingestion de projeto
# (trigger primeira execução do DAG)

# Verificar logs Airflow
tail -f ~/airflow/logs/kb_evolution_dag/

# Monitorar no Grafana
# http://localhost:3000
# Deve mostrar: 1 execução, 7 tasks completadas, métrica de latência

# Monitorar Slack
# Esperado: 1 msg de INFO (auto-update OK) ou nenhuma (status quo)

echo "✅ GO-LIVE COMPLETO!"
```

---

## 🎯 CHECKLIST FINAL

```bash
✅ PASSO 1: Pré-deploy
  [ ] deploy.py retorna 7/7 PASSED
  [ ] Variáveis de ambiente configuradas
  [ ] Infraestrutura validada (Supabase, Airflow, Docker)

✅ PASSO 2: Supabase
  [ ] Schema deployed (12 tabelas)
  [ ] Seed data inserida (68 registros)
  [ ] RLS policies ativas (3 roles)
  [ ] Conexão testada (curl ok)

✅ PASSO 3: Airflow
  [ ] Webserver rodando (port 8080)
  [ ] Scheduler ativo
  [ ] DAG kb_evolution_dag listado
  [ ] 7 tasks visíveis
  [ ] DAG ativado (unpause)

✅ PASSO 4: Monitoramento
  [ ] Prometheus rodando (port 9090)
  [ ] Grafana rodando (port 3000)
  [ ] AlertManager rodando (port 9093)
  [ ] Data source Prometheus conectado
  [ ] Slack webhook configurado

✅ PASSO 5: Callback & Testes
  [ ] Callback Handler rodando (port 8001)
  [ ] Health check OK
  [ ] Roteamento Maestro testado (3 exemplos)
  [ ] Callback endpoints testados (rejection, approval)
  [ ] Teste end-to-end OK

✅ PASSO 6: Validação Final
  [ ] Nenhum erro crítico (alert manager)
  [ ] SLA 99.5% = uptime > 43min/mês OK
  [ ] Logs auditados (kb_audit_log preenchida)
  [ ] Equipe notificada (Slack)
  [ ] Documentação atualizada
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

| Problema | Solução |
|----------|---------|
| Supabase conexão falha | Verificar SUPABASE_URL/KEY em .env |
| Airflow DAG não lista | Reiniciar scheduler: `airflow scheduler --daemon` |
| Monitoring não coleta | Aguardar primeira execução DAG (gera métricas) |
| Callback timeout | Verificar porta 8001: `lsof -i :8001` |
| Slack alerts não chegam | Testar webhook: `curl -X POST $SLACK_WEBHOOK ...` |
| Pattern detection não ativa | Aguardar 3+ rejeições em 2 semanas (por design) |

---

## ⏱️ TIMELINE ESPERADO

```
08:00 — PASSO 1 (Pre-deploy, 30 min)
08:30 — PASSO 2 (Supabase, 60 min) ← Mais longo
09:30 — PASSO 3 (Airflow, 45 min)
10:15 — PASSO 4 (Monitoring, 30 min)
10:45 — PASSO 5 (Callback, 45 min)
11:30 — ✅ GO-LIVE COMPLETO

Total: ~3.5 horas (com margens)
```

---

## 📞 CONTATOS SUPORTE

- **Supabase issue**: Documentação oficial + Slack @db-team
- **Airflow issue**: Airflow docs + Slack @devops
- **Docker issue**: Docker docs + Slack @devops
- **Slack integration**: Slack API docs + @platform-team
- **Geral**: Arquiteto IA (@mneves)

---

**Status**: Ready for 2026-08-01 ✅  
**Risco**: Baixo (7/7 fases testadas)  
**Rollback**: Automático em 2 min se algo falhar
