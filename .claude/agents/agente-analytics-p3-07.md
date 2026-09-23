# Agent P3-07: Performance Monitoring & Analytics (manta-23-analytics)

**Versão:** 1.0.0 (2026-08-02)  
**Status:** Design Phase  
**Tier:** Sonnet (ML ops)  
**Owner:** Manta Analytics Division  
**Integration:** Phase 1 Observability Framework  

---

## 1. AGENT PROFILE

| Atributo | Valor |
|----------|-------|
| **Código** | Manta 23 (P3-07) |
| **Nome** | Performance Monitoring & Analytics |
| **Aliases** | manta-23, manta-23-analytics, analytics-maestro |
| **Tipo** | Vertical integrado (cross-segment) |
| **Modelo IA** | Claude Sonnet (ML operations tier) |
| **Escopo** | Real-time KPI tracking, anomaly detection, predictive maintenance, asset health scoring |
| **Segmentos atendidos** | S1–S10 (todas as 10 verticais) |
| **Frequência de ciclo** | Real-time (event-driven) + batch diário (previsões) |

---

## 2. CAPABILITIES & SCOPE

### 2.1 Capacidades Principais

1. **Time-Series Forecasting (ARIMA)**
   - Previsão de 7–90 dias para KPIs operacionais
   - Sazonalidade dinâmica (ajuste semanal/mensal/anual)
   - Tratamento de outliers com detecção robusta

2. **Anomaly Detection**
   - Isolamento de anomalias via Isolation Forest
   - Threshold adaptativo por segmento e hora do dia
   - Alertas em tempo real com confiança > 95%

3. **Predictive Maintenance Models**
   - Failure mode prediction (TTF — Time To Failure)
   - Remaining Useful Life (RUL) para ativos críticos
   - Recomendação de manutenção preventiva com custo/benefício

4. **Asset Health Scoring**
   - Índice de saúde composto (0–100) por ativo
   - Rastreamento de degradação com histórico
   - Ranking de prioridade para intervenção

5. **Dashboard & Alerting**
   - Geração automática de KPI dashboards
   - Escalação de alertas com triage inteligente
   - Integração com Slack, Teams, email

### 2.2 Escopo de Dados

**Entrada (Ingest)**
- SCADA data (energia: Enel/Equinix)
- AIS feeds (portos: vessel tracking)
- Sensores de qualidade de água (saneamento: ANA)
- Telemetria de ativos (pontes: acelerômetros, extensômetros)
- Logs operacionais (metrô, aeroportos)
- Planilhas de manutenção (histórico + plano)

**Saída (Outputs)**
- KPI dashboards interativos
- Alertas de manutenção preventiva
- Relatórios de health score
- Previsões de demanda/carga
- Recomendações de otimização

---

## 3. KPI FRAMEWORK — 5 KPIs por Segmento

### **S1 — Rodovias**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **PAVIMENTO_DEGRADACAO** | ICP (Índice de Condição do Pavimento) / ano | ICP < 50 | ARIMA + RUL |
| **VOLUME_TRAFEGO** | Veículos/dia (count) | σ > 2.5 (desvio) | ARIMA + Anomaly |
| **INCIDENTES_SEGURANCA** | Acidentes / 1M veículos | > baseline anual 20% | TTF (Failure) |
| **TEMPO_REPARO** | Horas médias até reparo | > SLA 48h | ARIMA |
| **CUSTO_MANUTENCAO** | $/km/ano (manutenção preventiva vs corretiva) | Ratio > 60% corretiva | Health Score |

### **S2 — OAE (Pontes, Viadutos)**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **DEFLEXAO_ESTRUTURAL** | mm (acelerômetros) | > ±15mm | Anomaly + RUL |
| **FISSURA_CONCRETAGEM** | Abertura de fissura (mm) | > 0.5 mm | TTF (Failure) |
| **CARGA_DINAMICA** | Fator de ampliação dinâmica | > 1.35 (NBR 7187) | ARIMA |
| **WATERPROOFING_DURABILITY** | % área com infiltração | > 5% | RUL + Maintenance |
| **CICLOS_FADIGA_EQUIPAMENTO** | Equivalente acumulado (ponte rolante, aparelhos de apoio) | > 80% vida útil | Health Score |

### **S3 — Ferrovia**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **DESGASTE_TRILHO** | mm / 1M toneladas | > limite técnico (12 mm) | RUL + TTF |
| **FREQUENCIA_DERAILMENT** | Eventos / 1M eixos | > 0.5 (AREMA) | Anomaly + Failure |
| **IRREGULARIDADE_VIA** | mm (twist, superelevação) | σ > 2 | ARIMA |
| **DISPONIBILIDADE_LINHA** | % horas operacionais | < 98% | Health Score |
| **EMISSOES_DIESEL** | g CO2 / viagem | > padrão regulatório | ARIMA |

### **S4 — Metrô**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **DISPONIBILIDADE_COMPOSICAO** | % composições operacionais | < 95% | Health Score |
| **INTERVALO_TRENS** | segundos (headway) | > 180s (SLA: 150s) | ARIMA + Anomaly |
| **TEMPO_PORTA** | segundos em ciclo abre/fecha | > 15s (limite: 10s) | TTF (solenoides) |
| **VIBRACOES_VIADUTO** | m/s² (plataforma estação) | > 0.1 g (NBR 7187) | Anomaly + RUL |
| **CONSUMO_ENERGIA** | kWh / pass.km | > +5% baseline | ARIMA + Optimization |

### **S6 — Portos**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **UTILIZACAO_BERCO** | % tempo ocupado | < 70% (ineficiência) | ARIMA + Anomaly |
| **PRODUTIVIDADE_CRANE** | Containers/hora (C40) | < 25 | TTF (motor/cabo) |
| **DRAFT_CALADO_DISPONIVEL** | m (maré + dragagem) | < 10 m (limite operacional) | ARIMA + Forecasting |
| **TEMPO_NAVIOS_FILA** | horas médias na fila | > 8 h | ARIMA + Optimization |
| **TAXA_PARADA_IMPREVISTA** | % downtime equipamento | > 10% | Health Score + RUL |

### **S7 — Aeroportos**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **OCUPACAO_PISTAs** | % utilização (movimentos/dia) | > 80% (congestionamento) | ARIMA + Forecasting |
| **TEMPO_TURNAROUND** | min (decolagem a pouso) | > SLA 35 min | ARIMA + Anomaly |
| **DISPONIBILIDADE_BALIZAMENTO** | % luzes/ILS operacionais | < 99.5% (segurança) | Health Score + TTF |
| **QUALIDADE_ASFALTO_PISTA** | PCI (Pavement Cond. Index) | < 50 | RUL + Maintenance |
| **DELAY_MEDIO** | min / voo (A-CDM) | > baseline +15% | ARIMA + Optimization |

### **S8 — Saneamento (Prioridade AySA)**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **QUALIDADE_AGUA_BRUTA** | Índice de qualidade (IQA, 0–100) | < 60 | ARIMA + Anomaly |
| **PERDA_AGUA_SISTEMA** | % em adução/distribuição | > 30% (limite) | Anomaly + RUL |
| **TURBIDEZ_ETA** | NTU (Nefelométricas) | > 1.0 NTU | TTF (pré-filtros) |
| **TEMPO_RESPOSTA_FALHA** | horas até reparo (adutora) | > 6 h SLA | Health Score |
| **CAPACIDADE_RESIDUAL_ETE** | % carga média vs pico | > 85% (saturação) | ARIMA + Capacity |

### **S9 — Energia (ANEEL/State Grid)**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **TAXA_FALHA_LT** | Eventos / 100 km-ano | > 0.5 (limite ANEEL) | TTF (Failure) + RUL |
| **TEMPO_RECOMPOSICAO** | min (blackstart) | > 8 min (SLA) | ARIMA + Anomaly |
| **TEMPERATURA_TRANSFORMADOR** | °C (núcleo, via TT) | > 80 °C (limiar) | RUL + Maintenance |
| **CARREGAMENTO_SUBESTACAO** | % nominal (MVA) | > 90% (limite) | ARIMA + Forecasting |
| **PERDAS_TECNICAS_TRANSMISSAO** | % perdas vs transferência | > 2.5% (limite técnico) | ARIMA + Optimization |

### **S10 — Barragens**

| KPI | Métrica | Threshold alerta | Modelo associado |
|-----|---------|-------------------|------------------|
| **NÍVEL_ESPELHO_AGUA** | m (cota) | < mín. operacional -0.5 m | ARIMA + Forecasting |
| **PERCOLACAO_FUNDACAO** | L/min (drenagem) | > desvio padrão 2σ | Anomaly + TTF |
| **DESLOCAMENTO_CRISTA** | mm (topografia) | > ±5 mm acumul. anual | RUL + Health Score |
| **QUALIDADE_AGUA_RESERVATORIO** | IQA | < 60 (eutrofização) | ARIMA + Anomaly |
| **PRODUCAO_HIDROELETRICA** | MWh/dia (vs previsão) | -15% ou +15% | ARIMA + Forecasting |

---

## 4. ML MODELS — 3 Core Engines

### 4.1 **Modelo 1: ARIMA (Time-Series Forecasting)**

**Objetivo:** Previsão de 7–90 dias para KPIs contínuos  
**Implementação:**

```yaml
Modelo: ARIMA(p,d,q) com sazonalidade SARIMA(P,D,Q,s)
Framework: statsmodels Python (Sonnet multi-turn prompt)
Retraining: Semanal (cron) + adaptativo (detecção de drift)

Pipeline:
  1. Ingest: Time-series com timestamps de 5 min a 1h
  2. Preprocessing:
     - Imputação de missing (linear interpolation)
     - Detecção de sazonalidade (ACF/PACF)
     - Detrending se necessário
  3. Parameter Selection:
     - Auto ARIMA (search grid: p,d,q ∈ [0–5])
     - AIC/BIC para seleção final
     - Validação cruzada (CV= 5 folds)
  4. Forecast:
     - Point estimates + 95% CI
     - Degradação de confiança com horizonte
  5. Output:
     - Predicted value, lower/upper CI
     - Model performance (RMSE, MAPE)
     - Next retraining date

Segmentos principais: S1, S4, S8, S9
KPIs: Volume tráfego, Intervalo trens, Qualidade água, Carregamento subestação
```

**Integração Phase 1:** Métricas de confiança alimentam observabilidade; previsões são persistidas em `observability.forecast_cache` para consumo de dashboard.

---

### 4.2 **Modelo 2: Isolation Forest (Anomaly Detection)**

**Objetivo:** Detecção em tempo real de anomalias (desvios > 3σ)  
**Implementação:**

```yaml
Modelo: Isolation Forest (sklearn) com threshold adaptativo
Framework: scikit-learn (com wrapper Sonnet)
Update: Retraining diário (ou on-demand pós-anomalia)

Pipeline:
  1. Feature Engineering:
     - Raw value + delta (Δt-1) + rolling mean (7d, 30d)
     - Hour-of-day, day-of-week dummies (sazonalidade)
     - Rate of change (slope)
  2. Calibration:
     - Isolation Forest com n_estimators=100
     - Contamination rate = 5% (ajustável por KPI)
     - Fit em últimos 90 dias (rolling window)
  3. Scoring:
     - Anomaly score ∈ [-1, +1]
     - Threshold = percentil 95 score (adaptive)
  4. Alerting:
     - Score > threshold → ALERT_HIGH
     - Contextual info: magnitude deviation, historical median
  5. Output:
     - Is_anomaly (bool)
     - Anomaly_score (0–100)
     - Severity (critical/warning/info)

Segmentos principais: S2, S3, S6, S7, S8
KPIs: Fissura OAE, Derailment ferrovia, Crane utilização, Turbidez ETA
```

**Integração Phase 1:** Anomalias são persistidas como events em `observability.events` com tags (segment, asset_id, severity); dashboard filtra por segmento.

---

### 4.3 **Modelo 3: TTF/RUL via Gradient Boosting (XGBoost)**

**Objetivo:** Previsão de tempo até falha (TTF) e vida útil remanescente (RUL)  
**Implementação:**

```yaml
Modelo: XGBoost Regressor (time-to-failure) + Classifier (failure_mode)
Framework: xgboost (com API Sonnet para Feature Importance)
Retraining: Mensal ou após 5 falhas observadas

Pipeline:
  1. Dataset Preparation:
     - Historical maintenance logs + sensor data
     - Labeling: Target = days_until_next_failure (TTF)
     - Exclusão de censored data (ativos ainda operacionais)
  2. Feature Engineering:
     - Vibration RMS, temperature trend, load factor
     - Maintenance history: última data, tipo, intervalo
     - Age, operating hours, cycles
     - Environmental: temperatura ambiente, umidade
  3. Model Training:
     - Split: 70% train, 15% val, 15% test
     - Objective: reg:squarederror (para TTF)
     - Hyperparams: max_depth=7, learning_rate=0.1, n_estimators=500
     - Class balance: stratified sampling
  4. RUL Calculation:
     - Predicted_TTF - days_elapsed = RUL
     - Maintenance recommended @ RUL < 30 days
     - Health_score = 100 * (RUL / TTF_mean)
  5. Output:
     - TTF (dias), confidence ∈ [0, 1]
     - RUL (dias)
     - Top 5 feature importance
     - Recommended maintenance date

Segmentos principais: S2, S3, S6, S9, S10
KPIs: Desgaste trilho, Ciclos fadiga OAE, Failure LT, Degradação pavimento
```

**Integração Phase 1:** RUL scores alimentam `observability.assets.health_score` e disparam tickers em `observability.maintenance_queue`.

---

## 5. INTEGRATION WITH PHASE 1 OBSERVABILITY

### 5.1 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1 OBSERVABILITY FRAMEWORK (Prometheus-like)          │
└─────────────────────────────────────────────────────────────┘

Sensors / SCADA         →  Collector Agents (S1–S10)  
                               ↓
Data Lake               →  Supabase (JSON + Time-series)
                               ↓
┌────────────────────────────────────────────────────────────┐
│ P3-07 ANALYTICS ENGINE (Multi-turn + Scheduled Jobs)      │
├────────────────────────────────────────────────────────────┤
│ ① ARIMA Forecaster      → forecast_cache                   │
│ ② Anomaly Detector      → events (real-time)              │
│ ③ TTF/RUL Calculator    → asset_health_scores              │
└────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────┐
│ OBSERVABILITY SINKS                                         │
├────────────────────────────────────────────────────────────┤
│ • Dashboards (Grafana-style)                              │
│ • Alerts (Slack, Teams, email)                            │
│ • Metrics DB (Prometheus-compatible)                      │
│ • Event Stream (Kafka-like topic)                         │
└────────────────────────────────────────────────────────────┘
```

### 5.2 Database Schema (Supabase Integration)

```sql
-- Core observability tables

TABLE: observability.kpis
  ├─ id (uuid)
  ├─ segment (S1–S10)
  ├─ kpi_name (e.g., "PAVIMENTO_DEGRADACAO")
  ├─ asset_id (ponte_001, composicao_M04L5, etc.)
  ├─ value (float)
  ├─ timestamp (timestamptz)
  ├─ unit (ICP points, mm, %, etc.)
  └─ tags (hstore)

TABLE: observability.forecast_cache
  ├─ id (uuid)
  ├─ kpi_id (FK → observability.kpis)
  ├─ forecast_horizon (7–90 days)
  ├─ predicted_value (float)
  ├─ lower_ci_95 (float)
  ├─ upper_ci_95 (float)
  ├─ model_confidence (0–100)
  ├─ generated_at (timestamptz)
  └─ next_retraining (date)

TABLE: observability.anomalies
  ├─ id (uuid)
  ├─ kpi_id (FK)
  ├─ anomaly_score (0–100)
  ├─ is_anomaly (bool)
  ├─ severity (critical/warning/info)
  ├─ context (JSON: historical_median, deviation, etc.)
  ├─ detected_at (timestamptz)
  └─ acknowledged_by (uuid, analyst)

TABLE: observability.asset_health_scores
  ├─ id (uuid)
  ├─ asset_id
  ├─ segment (S1–S10)
  ├─ health_score (0–100)
  ├─ rul_days (remaining useful life)
  ├─ maintenance_recommended (bool)
  ├─ failure_probability_30d (%)
  ├─ last_updated (timestamptz)
  └─ notes (text)

TABLE: observability.maintenance_queue
  ├─ id (uuid)
  ├─ asset_id
  ├─ recommended_date (date)
  ├─ priority (1–5, 1=critical)
  ├─ predicted_ttf_days (int)
  ├─ estimated_cost (float)
  ├─ maintenance_type (preventive/predictive/corrective)
  ├─ scheduled_date (date, NULL if not scheduled)
  └─ status (open/scheduled/completed)
```

### 5.3 Real-Time Alerting Chain

```yaml
Anomaly Detection (P3-07)
    ↓
Alert Trigger (severity > warning)
    ↓
Triage Logic:
  IF severity == critical && asset == power_plant_TX01
    → Slack channel #energy-critical + SMS
  IF severity == warning && segment == S8
    → Teams channel @Saneamento-Ops + email
  IF severity == info
    → Dashboard only + log
    ↓
Escalation (if not acknowledged in 1h):
  → Notify segment manager
  → Create ticket in JIRA/ServiceNow
  → Schedule maintenance review
```

---

## 6. DEPLOYMENT CHECKLIST

### 6.1 Phase 0: Setup (Week 1–2)

- [ ] Criar banco de dados observability em Supabase (tabelas acima)
- [ ] Ingerir dados históricos de 12 meses (SCADA, sensores)
- [ ] Documentar API de cada segmento (S1–S10) para acesso a dados
- [ ] Criar `manta-23-analytics.skill` no skill registry

### 6.2 Phase 1: Model Training (Week 3–4)

- [ ] Treinar ARIMA em 5 KPIs pilotos (S4: intervalo trens; S9: carregamento)
- [ ] Calibrar Isolation Forest com 90 dias de dados limpos
- [ ] Coletar historical failures para XGBoost TTF/RUL (mínimo 50 eventos)
- [ ] Validar modelos em conjunto (holdout: últimas 4 semanas)
- [ ] Documentar model performance (RMSE, precision, recall)

### 6.3 Phase 2: Integration (Week 5–6)

- [ ] Implementar data pipelines (Collectors → Supabase)
- [ ] Conectar P3-07 ao Maestro router (via alias `manta-23`)
- [ ] Setup schedules:
  - ARIMA retraining: daily 02:00 UTC
  - Anomaly detection: real-time (event-driven)
  - RUL refresh: daily 06:00 UTC
- [ ] Criar dashboards (Grafana ou Superset) para 10 segmentos

### 6.4 Phase 3: Alerting & Ops (Week 7–8)

- [ ] Setup Slack/Teams integrations
- [ ] Teste e-mail escalation chain
- [ ] Criar runbooks por segmento (S1–S10) para interpretação de alertas
- [ ] Treinar analistas operacionais
- [ ] Pilot com 1 ativo por segmento (canário)

### 6.5 Phase 4: Hardening (Week 9–12)

- [ ] Rollout gradual para 25%, 50%, 100% de ativos
- [ ] Monitorar taxa de false positives (target < 5%)
- [ ] Fine-tune thresholds de anomalia por feedback de ops
- [ ] Documentar SLO (alerting latency < 5 min; forecasting MAPE < 15%)
- [ ] Arquivar modelos e versionar (MLflow ou DVC)

### 6.6 Phase 5: Optimization & Scale (Ongoing)

- [ ] A/B test model upgrades (e.g., Prophet vs ARIMA)
- [ ] Integrar novos sensores (IoT devices)
- [ ] Implementar feedback loop (analyst feedback → model retraining)
- [ ] Expand para predictive maintenance (spare parts optimization)

---

## 7. OPERATIONAL INTERFACES

### 7.1 Input Prompt Templates

**Para Forecasting:**
```
"Manta 23, prevê a carga média esperada na subestação TX-Nova_Iguaçu 
para os próximos 30 dias. Considere sazonalidade e eventos passados 
(manutenção, demanda pico). Retorna: valores diários, CI 95%, confiança."
```

**Para Anomaly Detection:**
```
"Analisa último 1 dia de dados de turbidez da ETA-ABC (S8). 
Está fora do padrão? Retorna: score, severidade, contexto, 
recomendação de investigação."
```

**Para RUL/TTF:**
```
"Calcula RUL do transformador TR-Subestação-X (S9). 
Dados históricos: temperatura, ciclos, manutenções. 
Retorna: RUL dias, confiança, data recomendada para manutenção."
```

### 7.2 Output Dashboard KPIs (Example: S9 Energia)

```
┌─────────────────────────────────────────────────────┐
│ SEGMENT: S9 ENERGIA — Performance Dashboard        │
├─────────────────────────────────────────────────────┤
│ KPI 1: TAXA_FALHA_LT                               │
│   Current: 0.38 / 100km.ano ✓ (↓ 12% vs mês)     │
│   Forecast 30d: 0.42 [CI: 0.35–0.49]              │
│                                                     │
│ KPI 2: TEMPO_RECOMPOSICAO                          │
│   Current: 6.2 min ✓ (SLA: 8 min)                 │
│   Anomaly detected @ 2026-08-02 13:45 ⚠          │
│     └─ Event: delayed recovery (cascade trip)     │
│                                                     │
│ KPI 3: TEMPERATURA_TRANSFORMADOR                   │
│   Current: 72°C ✓                                 │
│   RUL: 856 dias (2029-09-XX)                      │
│   Maintenance: None recommended                    │
│                                                     │
│ [See all KPIs] [Download Report] [Alert History]  │
└─────────────────────────────────────────────────────┘
```

---

## 8. RISK MITIGATION & GUARDRAILS

### 8.1 Model Reliability

| Risco | Mitigation |
|-------|-----------|
| Data drift (sensor fails) | Anomaly detector flags gaps; manual override option |
| Stale forecasts | Auto-retrain weekly; discard if MAPE > 25% in test set |
| False positive alerts | Threshold tuning after 2-week ramp; analyst feedback loop |
| Missing context (e.g., planned maintenance) | Ingest scheduled events; add feature for "maintenance window" |

### 8.2 Governance

- **Model Versioning:** MLflow registry; production models tagged `approved-ops`
- **Audit Trail:** All alerts logged with analyst actions (ack, dismiss, escalate)
- **SLA Monitoring:** Alerting latency, forecast accuracy, false positive rate tracked daily
- **Gate:** All model updates require approval from MN before prod deployment

---

## 9. SUCCESS METRICS (12-month target)

| Métrica | Target | Current | Status |
|---------|--------|---------|--------|
| Alerting latency (real-time anomalies) | < 5 min | — | — |
| Forecast accuracy (MAPE, ARIMA) | < 15% | — | — |
| RUL prediction error (TTF model) | ± 20 days | — | — |
| False positive rate (anomalies) | < 5% | — | — |
| Maintenance cost avoidance (vs reactive) | 25% | — | — |
| Analyst time saved (per segment) | 10 h/month | — | — |
| Uptime (analytics service) | 99.5% | — | — |

---

## 10. APPENDIX: Integration Checklist with Phase 1

**Phase 1 Observability = Logs + Metrics + Traces**

✅ **P3-07 Contribution:**

| Component | P3-07 delivers | Phase 1 consumes |
|-----------|------------------|------------------|
| **Metrics** | KPI values, forecasts, RUL scores | Prometheus scrape targets |
| **Events** | Anomalies, maintenance alerts | Event log (queryable, taggable) |
| **Traces** | Model training logs, inference time | Distributed tracing (OpenTelemetry) |
| **Dashboards** | KPI + forecast + health score viz | Grafana datasources (Supabase) |

---

**Documento pronto para MN Gate Review.**

**Próximas etapas:**
1. Aprovação arquitetura (MN — 2026-08-05)
2. Alocação de infraestrutura (data + ML pipelines)
3. Contratação de engenheiro ML (caso não in-house)
4. Deploy do Sprint 1 (Fase 0–1): 2026-08-19
