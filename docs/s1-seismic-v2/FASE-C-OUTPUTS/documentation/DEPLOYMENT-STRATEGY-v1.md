# Manta Maestro — Deployment Strategy & Handoff Specifications
**Version:** 1.0 | **Date:** 2026-07-25 | **Owner:** Manta Arquitecto-IA

---

## PART 1: DEPLOYMENT ROADMAP (SPRINTS 4–8)

### Sprint 4: Integration & Testing (November 2026)
**Duration:** 2 weeks | **Gate:** Technical readiness review

#### Week 1: Agent Integration Framework
- [ ] Finalize API contracts for agents 05, 07, 15, 02 (cost, schedule, advisory, contractual)
- [ ] Deploy Supabase collections for S6–S10 (portos, aeroportos, saneamento, energia, barragens)
- [ ] Set up agent communication bus (OpenAI Realtime → event-driven queue)
- [ ] Implement request/response JSON schema validation
- [ ] Create mock data generators (test fixtures for each agent input)
- [ ] Deploy integration test harness (Jest + supertest)
- [ ] Configure staging environment (parallel to production)

#### Week 2: Unit & Integration Testing
- [ ] Unit tests: 40+ test cases per agent (input validation, output formatting)
- [ ] Integration tests: 15+ workflows (cost → schedule → advisory → contract)
- [ ] Data flow tests: JSON payload tracing end-to-end
- [ ] Error scenario tests: missing data, timeout, API failures
- [ ] Performance tests: latency <2s per agent call, <5s orchestration
- [ ] Load test: 10 concurrent requests, sustained 100 RPS
- [ ] UAT environment spin-up (3 pilot orgs)

**Deliverables:**
- Integration test report (pass/fail rates, coverage %)
- Staging deployment checklist
- API specification document (OpenAPI 3.1)

---

### Sprint 5: UAT with 3 Pilots (December 2026)
**Duration:** 3 weeks | **Gate:** UAT sign-off from pilot orgs

#### Pilot Selection & Setup
- **Pilot A (Rodovia):** Existing customer (agente-infraestrutura S1 + cost/schedule)
- **Pilot B (Saneamento):** AySA early adopter (agente-saneamento S8 + cost/schedule)
- **Pilot C (Energia):** ANEEL/State Grid contact (agente-energia S9 + advisory)

#### Week 1: Pilot Data Onboarding
- [ ] Extract pilot project data (DWG, PDF, SICRO rates, network diagrams)
- [ ] Normalize into standard JSON schemas (project baseline, cost drivers, WBS, durations)
- [ ] Load into staging database
- [ ] Create 5–10 realistic scenarios per pilot (best case, worst case, risk case)
- [ ] Train pilot users (1.5-hour session per org)

#### Week 2: Workflows & Feedback
- [ ] Pilot A runs: project estimate → schedule forecast → risk advisory
- [ ] Pilot B runs: saneamento cost model → critical path analysis → compliance checks
- [ ] Pilot C runs: energy transmission analysis → schedule feasibility → contractual risk
- [ ] Collect feedback: usability, output accuracy, performance, edge cases
- [ ] Log issues (P0: blocker, P1: critical, P2: nice-to-have)
- [ ] Conduct weekly sync calls (Tue/Thu, 30 min each)

#### Week 3: Refinement & Sign-off
- [ ] Fix P0/P1 issues (target: 95% resolved)
- [ ] Validate outputs against pilot domain experts
- [ ] Update documentation based on feedback
- [ ] Obtain pilot sign-off (email approval from each org)
- [ ] Prepare go-live readiness report

**Deliverables:**
- UAT test cases (50+ scenarios documented)
- Feedback log & remediation tracker
- Pilot sign-off emails
- Go-live readiness assessment

---

### Sprint 6: Refinement & Final Testing (January 2027)
**Duration:** 2 weeks | **Gate:** Production readiness review

#### Week 1: Performance Tuning & Security
- [ ] Profile agent response times (identify bottlenecks)
- [ ] Optimize RAG query performance (vector similarity search <200ms)
- [ ] Implement caching for SICRO rates, norm references
- [ ] Security audit: input validation, SQL injection, prompt injection
- [ ] Set up monitoring/alerting (Datadog, New Relic)
- [ ] Implement circuit breaker pattern for external APIs
- [ ] Conduct penetration testing on agent APIs

#### Week 2: Documentation & Runbooks
- [ ] Complete API specification (all agent contracts)
- [ ] Write operational runbooks (deployment, troubleshooting, rollback)
- [ ] Create architecture decision records (ADRs)
- [ ] Finalize SLAs & error budgets
- [ ] Prepare on-call rotation guide
- [ ] Document known limitations & workarounds

**Deliverables:**
- Performance testing report (latency, throughput, P99 metrics)
- Security audit report
- Complete technical documentation (1000+ lines)
- Runbooks & troubleshooting guides

---

### Sprint 7: Documentation & Training (February 2027)
**Duration:** 2 weeks | **Gate:** Training completion

#### Week 1: Content Creation
- [ ] Record demo videos (5–10 min each: cost modeling, schedule, advisory flows)
- [ ] Create slide decks for 3 user cohorts (technical, domain, executive)
- [ ] Write user guides (agent-specific, step-by-step workflows)
- [ ] Build FAQ & troubleshooting knowledge base (Notion, Confluence)
- [ ] Prepare change log & release notes

#### Week 2: Training Delivery
- [ ] Internal training: Manta team (2 sessions, 2 hours each)
- [ ] Pilot org training: hands-on workshops (1.5 hours each)
- [ ] Customer success training: support team onboarding (1 hour)
- [ ] Collect training feedback & adjust materials
- [ ] Publish training materials to internal portal

**Deliverables:**
- Video tutorials (5–10 published)
- User guides (one per agent + integration guide)
- Training slide decks
- FAQ & knowledge base articles

---

### Sprint 8: Production Deployment (March–June 2027)
**Duration:** 4 weeks | **Gate:** Go-live approval from MN

#### Week 1: Pre-Production Staging
- [ ] Final smoke tests in staging (all 50+ go-live checklist items)
- [ ] Database migration dry-run (backup, restore test)
- [ ] Validate data integrity (cost, schedule, contract data samples)
- [ ] Prepare rollback artifacts (previous agent versions, database snapshots)
- [ ] Brief all stakeholders (deployment timeline, expected impact, support)

#### Week 2: Soft Launch (Limited Availability)
- [ ] Deploy to production in dark-launch mode (no customer traffic)
- [ ] Enable feature flags: agents initially OFF
- [ ] Monitor error rates, latency, resource utilization
- [ ] Run canary tests (10% of traffic to new agents, 90% to legacy)
- [ ] Collect 2–3 days of production telemetry

#### Week 3: Gradual Rollout
- [ ] Enable agent-05 (orçamento) for 25% of projects
- [ ] Enable agent-07 (cronograma) for 25% of projects
- [ ] Enable advisory & contractual agents for 50% of orgs
- [ ] Monitor closely (daily dashboards, automated alerts)
- [ ] Be ready to rollback if P0 issues detected

#### Week 4: Full Production
- [ ] Roll out to 100% of customers
- [ ] Retire legacy cost/schedule tools (with 2-week deprecation notice)
- [ ] Activate full support team availability (24/5 coverage)
- [ ] Start 3-month post-go-live monitoring

**Go-Live Criteria:**
- All UAT sign-offs obtained ✓
- Zero P0 issues in production ✓
- Performance meets SLAs (latency <2s) ✓
- Support team trained & ready ✓
- Rollback plan documented & tested ✓

---

## PART 2: HANDOFF SPECIFICATIONS (API CONTRACTS)

### Agent 05: Orçamento (Cost Modeling)

#### Input Contract
```json
{
  "project_id": "PRJ-2026-1234",
  "project_name": "Rodovia BR-101 Trecho 3",
  "segment": "S1",
  "phase": "projeto_executivo",
  "request_id": "req-uuid-8f3a9d2c",
  "timestamp": "2026-07-25T14:30:00Z",
  "cost_inputs": {
    "wbs": [
      {
        "code": "1.1.1",
        "description": "Terraplenagem",
        "unit": "m³",
        "quantity": 125000,
        "sicro_code": "DNIT-2023-001",
        "location_factor": 1.15,
        "seasonality_factor": 1.0
      }
    ],
    "global_parameters": {
      "project_duration_months": 24,
      "inflation_rate_annual": 0.065,
      "reference_date": "2026-07-01",
      "contingency_policy": "80_percentile",
      "contingency_percent": 15,
      "indirect_costs_percent": 12
    },
    "risk_adjustments": [
      {
        "risk_id": "R-001",
        "description": "Variação de SICRO",
        "impact_percent": -5,
        "probability": 0.6
      }
    ]
  }
}
```

#### Output Contract
```json
{
  "request_id": "req-uuid-8f3a9d2c",
  "project_id": "PRJ-2026-1234",
  "status": "success",
  "timestamp": "2026-07-25T14:31:15Z",
  "cost_forecast": {
    "direct_costs": 2850000,
    "indirect_costs": 342000,
    "contingency": 427500,
    "total_base": 3619500,
    "financing_costs": 145000,
    "total_project": 3764500,
    "currency": "BRL",
    "reference_date": "2026-07-01"
  },
  "cost_breakdown": [
    {
      "code": "1.1.1",
      "description": "Terraplenagem",
      "quantity": 125000,
      "unit_rate": 22.8,
      "subtotal": 2850000,
      "source": "SICRO-2023"
    }
  ],
  "variance_analysis": {
    "vs_baseline": {
      "percent_variance": 8.5,
      "absolute_variance": 287000,
      "explanation": "Inflation adjustment + risk factor"
    }
  },
  "sensitivity_analysis": {
    "sicro_variance_10_percent": {
      "total_project": 4140950,
      "impact_percent": 10.0
    },
    "duration_variance_plus_3_months": {
      "total_project": 3921650,
      "impact_percent": 4.2
    }
  },
  "warnings": [],
  "data_quality_score": 0.96
}
```

#### Error Response
```json
{
  "request_id": "req-uuid-8f3a9d2c",
  "status": "error",
  "error_code": "INVALID_SICRO_CODE",
  "error_message": "SICRO code DNIT-2023-001 not found in database",
  "error_details": {
    "field": "cost_inputs.wbs[0].sicro_code",
    "expected_format": "DNIT-YYYY-NNN or SAGRIMA-YYYY-NNN",
    "suggestion": "Validate SICRO code or use generic rate estimation"
  }
}
```

---

### Agent 07: Cronograma (Schedule Management)

#### Input Contract
```json
{
  "project_id": "PRJ-2026-1234",
  "request_id": "req-uuid-9g4b0e3d",
  "timestamp": "2026-07-25T14:30:00Z",
  "schedule_inputs": {
    "network": {
      "activities": [
        {
          "code": "A-001",
          "description": "Limpeza e desmobilização",
          "duration_days": 30,
          "resource_requirement": "Operário (5 unidades)",
          "predecessor": [],
          "successor": ["A-002"],
          "criticality_flags": ["weather_dependent"]
        },
        {
          "code": "A-002",
          "description": "Terraplenagem",
          "duration_days": 360,
          "resource_requirement": "Operário (15 unidades), Escavadeira",
          "predecessor": ["A-001"],
          "successor": ["A-003"],
          "criticality_flags": ["high_duration", "resource_constrained"]
        }
      ],
      "milestones": [
        {
          "code": "M-001",
          "description": "30% Progresso",
          "target_date": "2027-02-01",
          "activity_code": "A-002",
          "tolerance_days": 15
        }
      ]
    },
    "resource_constraints": {
      "operario_available": 25,
      "escavadeira_available": 3,
      "crew_learning_curve": 0.95
    },
    "global_parameters": {
      "project_start_date": "2026-09-01",
      "weather_model": "BR_subtropical_summer",
      "productivity_adjustment": 0.90,
      "schedule_confidence": "baseline"
    }
  }
}
```

#### Output Contract
```json
{
  "request_id": "req-uuid-9g4b0e3d",
  "project_id": "PRJ-2026-1234",
  "status": "success",
  "timestamp": "2026-07-25T14:33:45Z",
  "schedule_forecast": {
    "project_start": "2026-09-01",
    "project_finish": "2028-08-15",
    "total_duration_days": 714,
    "critical_path_length": 714,
    "critical_path_activities": ["A-002", "A-003", "A-004"],
    "slack_analysis": {
      "free_slack_days": 45,
      "total_slack_days": 45
    },
    "confidence_level": "baseline"
  },
  "activities": [
    {
      "code": "A-002",
      "description": "Terraplenagem",
      "early_start": "2026-10-01",
      "early_finish": "2027-11-30",
      "late_start": "2026-10-01",
      "late_finish": "2027-11-30",
      "slack": 0,
      "is_critical": true,
      "resource_utilization": {
        "operario": 15,
        "escavadeira": 2,
        "utilization_percent": 94
      }
    }
  ],
  "milestone_analysis": [
    {
      "code": "M-001",
      "description": "30% Progresso",
      "target_date": "2027-02-01",
      "forecast_date": "2027-02-08",
      "variance_days": 7,
      "status": "at_risk"
    }
  ],
  "resource_histogram": {
    "operario": {
      "peak_utilization": 18,
      "available": 25,
      "peak_date": "2027-05-01"
    }
  },
  "risk_scenarios": [
    {
      "scenario": "weather_delay_30_days",
      "new_finish_date": "2028-09-14",
      "delay_days": 30,
      "probability": 0.45
    }
  ]
}
```

---

### Agent 15: Advisory (Risk & Viability Analysis)

#### Input Contract
```json
{
  "project_id": "PRJ-2026-1234",
  "request_id": "req-uuid-1h5c1f4e",
  "timestamp": "2026-07-25T14:30:00Z",
  "advisory_inputs": {
    "project_status": {
      "phase": "projeto_executivo",
      "days_into_phase": 120,
      "phase_budget": 500000,
      "phase_actual_spend": 487000,
      "phase_planned_completion": "2026-10-15",
      "current_date": "2026-07-25"
    },
    "risks": [
      {
        "risk_id": "R-001",
        "category": "technical",
        "description": "Soil conditions worse than predicted in survey",
        "probability": 0.35,
        "impact_if_occurs": "30% cost increase",
        "mitigation": "Contingency provision (15%)"
      }
    ],
    "stakeholder_concerns": [
      "Community objections to project route",
      "Environmental licensing delays",
      "DNIT approval timeline"
    ]
  }
}
```

#### Output Contract
```json
{
  "request_id": "req-uuid-1h5c1f4e",
  "project_id": "PRJ-2026-1234",
  "status": "success",
  "timestamp": "2026-07-25T14:35:20Z",
  "advisory_summary": {
    "viability_score": 7.8,
    "viability_rating": "green",
    "recommendation": "Proceed with caution; monitor R-001 and environmental licensing closely",
    "key_risks": ["environmental_licensing", "soil_conditions", "community_objections"]
  },
  "risk_assessment": {
    "overall_risk_score": 4.2,
    "risk_trend": "stable",
    "top_3_risks": [
      {
        "rank": 1,
        "risk_id": "R-001",
        "description": "Soil conditions",
        "probability": 0.35,
        "impact": 0.8,
        "criticality": 0.28,
        "mitigation_effectiveness": 0.75,
        "residual_risk": 0.07
      }
    ]
  },
  "stakeholder_analysis": {
    "concerns_addressed": 2,
    "concerns_unmitigated": 1,
    "recommendation": "Accelerate environmental licensing review; engage community early"
  },
  "financial_health": {
    "budget_utilization": 0.974,
    "forecast_vs_budget": 0.98,
    "cash_flow_forecast": "adequate"
  }
}
```

---

### Agent 02: Contratual (Contract & Terms Analysis)

#### Input Contract
```json
{
  "project_id": "PRJ-2026-1234",
  "request_id": "req-uuid-2i6d2g5f",
  "timestamp": "2026-07-25T14:30:00Z",
  "contractual_inputs": {
    "project_scope": {
      "deliverables": ["Terraplenagem", "Drenagem", "Pavimentação"],
      "quality_standards": ["DNIT-ES 384/19", "ABNT NBR 7182"],
      "acceptance_criteria": "100% compliance with design and quality standards"
    },
    "commercial_terms": {
      "contract_value": 3764500,
      "payment_schedule": "monthly_milestone_based",
      "retention_percent": 10,
      "performance_bond": 380000,
      "advance_mobilization": 376450
    },
    "risk_allocation": {
      "cost_overrun_responsibility": "Contractor 100% first 5%, then 50/50",
      "schedule_delay_penalties": "0.5% per week, max 10%",
      "force_majeure_events": ["natural_disaster", "government_action"]
    }
  }
}
```

#### Output Contract
```json
{
  "request_id": "req-uuid-2i6d2g5f",
  "project_id": "PRJ-2026-1234",
  "status": "success",
  "timestamp": "2026-07-25T14:37:50Z",
  "contract_assessment": {
    "enforceability_score": 8.9,
    "fairness_score": 7.2,
    "completeness_score": 8.5,
    "overall_assessment": "green_with_minor_observations"
  },
  "risk_analysis": [
    {
      "risk_type": "cost_overrun",
      "clause": "Cost overrun responsibility",
      "exposure": "High (first 5% on contractor)",
      "recommendation": "Contractor should secure contingency budget"
    }
  ],
  "compliance_checks": {
    "legal_framework": "Brazilian construction law (Lei 8.666/93)",
    "compliance_status": "compliant",
    "flagged_issues": []
  },
  "payment_schedule_analysis": {
    "total_payments": 3388050,
    "retention_holdback": 376450,
    "mobilization_advance": 376450,
    "cash_flow_profile": [
      {
        "month": 1,
        "amount": 376450,
        "type": "mobilization"
      }
    ]
  }
}
```

---

## PART 3: DATA FLOW DIAGRAMS

### Master Flow: Cost → Schedule → Advisory
```
┌─────────────────────────────────────────────────────────────────┐
│ MAESTRO (Router)                                                 │
│ Receives project baseline (JSON)                                 │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ├─ Validate input schema
           ├─ Extract project_id, segment, phase
           └─ Route to agents based on segment (S1–S10)
                 │
        ┌────────┼────────┬────────┬────────┐
        ▼        ▼        ▼        ▼        ▼
    ┌───────────────────────────────────────────┐
    │ AGENT-05 (Orçamento)                       │
    │ Input: WBS, SICRO codes, durations        │
    │ Output: Cost forecast, sensitivity        │
    │ Time: <2s                                  │
    └───────┬───────────────────────────────────┘
            │
            │ cost_forecast.json
            │ (total_project: 3.76M BRL)
            │
            ▼
    ┌───────────────────────────────────────────┐
    │ AGENT-07 (Cronograma)                      │
    │ Input: Network, resources, cost duration  │
    │ Output: Schedule, critical path, milestones
    │ Time: <2s                                  │
    └───────┬───────────────────────────────────┘
            │
            │ schedule_forecast.json
            │ (finish_date: 2028-08-15)
            │
            ▼
    ┌───────────────────────────────────────────┐
    │ AGENT-15 (Advisory)                        │
    │ Input: Cost, schedule, risks, status      │
    │ Output: Viability, risk score, recommendation
    │ Time: <3s                                  │
    └───────┬───────────────────────────────────┘
            │
            │ advisory_assessment.json
            │ (viability_score: 7.8)
            │
            ▼
    ┌───────────────────────────────────────────┐
    │ AGENT-02 (Contratual)                      │
    │ Input: Scope, cost, terms, risk allocation
    │ Output: Contract assessment, compliance   │
    │ Time: <2s                                  │
    └───────────────────────────────────────────┘
```

### Error Handling Flow
```
┌──────────────────────────────────────┐
│ Agent receives request                │
└────────────┬─────────────────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ Schema validation      │
    │ (JSON schema)          │
    └────────┬───────────────┘
             │
        ┌────┴────┐
        │          │
        ▼          ▼
     PASS      FAIL
     │         │
     │         └─→ Error response
     │             (HTTP 400)
     │
     ▼
┌────────────────────────────────────┐
│ Data normalization & enrichment     │
│ (RAG lookups, unit conversion)     │
└────────┬─────────────────────────────┘
         │
         ▼
    ┌────────────────────────┐
    │ Call external APIs     │
    │ (SICRO DB, LLM)        │
    └────────┬───────────────┘
             │
        ┌────┴────┐
        │          │
        ▼          ▼
     SUCCESS   TIMEOUT/FAIL
     │         │
     │         └─→ Circuit breaker
     │             ├─ Retry (exponential backoff)
     │             ├─ Fallback to cached data
     │             └─ Error response (HTTP 503)
     │
     ▼
┌────────────────────────────────────┐
│ Generate output JSON                │
│ (validation, formatting)            │
└────────┬─────────────────────────────┘
         │
         ▼
    ┌────────────────────────┐
    │ Return response        │
    │ (HTTP 200/4xx/5xx)    │
    └────────────────────────┘
```

---

## PART 4: ERROR HANDLING & RESILIENCE

### Error Categories

| Code | Category | Examples | Handling | SLA |
|------|----------|----------|----------|-----|
| 400 | Input Validation | Missing SICRO, invalid JSON | Sync error response | <100ms |
| 404 | Not Found | SICRO code not in DB, project not found | Return empty result + suggestion | <500ms |
| 429 | Rate Limited | Too many requests to external API | Queue + retry with backoff | <5s |
| 503 | Service Unavailable | LLM API down, DB connection failure | Circuit breaker → fallback | <10s |
| 504 | Timeout | Agent takes >10s | Kill process, return partial result | <11s |

### Retry Strategy
```json
{
  "retry_policy": {
    "max_retries": 3,
    "backoff_strategy": "exponential",
    "initial_delay_ms": 100,
    "max_delay_ms": 5000,
    "multiplier": 2.0,
    "jitter": true
  },
  "circuit_breaker": {
    "failure_threshold": 5,
    "success_threshold": 2,
    "timeout_seconds": 60,
    "half_open_requests": 1
  }
}
```

### Fallback Data
```json
{
  "fallback_sicro_rates": {
    "DNIT-terraplenagem": 22.5,
    "DNIT-escavacao": 35.0,
    "DNIT-drenagem": 150.0
  },
  "fallback_schedule": {
    "assumption_duration_multiplier": 1.2,
    "assumption_contingency_percent": 20
  },
  "fallback_advisory": {
    "default_viability_score": 5.0,
    "recommendation": "Insufficient data; request additional information"
  }
}
```

---

## PART 5: VALIDATION RULES

### Cost Reasonableness Checks
```json
{
  "validation_rules": [
    {
      "rule_id": "COST-001",
      "name": "Cost per unit reasonableness",
      "check": "unit_rate between (SICRO_rate * 0.7) and (SICRO_rate * 1.5)",
      "severity": "warning",
      "example": "Terraplenagem at 30 BRL/m³ (SICRO: 22.8) → OK"
    },
    {
      "rule_id": "COST-002",
      "name": "Contingency adequacy",
      "check": "contingency_percent between 10 and 25",
      "severity": "warning"
    },
    {
      "rule_id": "COST-003",
      "name": "Indirect costs reasonableness",
      "check": "indirect_costs_percent between 8 and 15",
      "severity": "info"
    },
    {
      "rule_id": "COST-004",
      "name": "Project budget variance",
      "check": "forecast vs baseline variance < 20%",
      "severity": "critical",
      "action": "Require manual review if exceeded"
    }
  ]
}
```

### Schedule Feasibility Checks
```json
{
  "validation_rules": [
    {
      "rule_id": "SCHED-001",
      "name": "Activity duration reasonableness",
      "check": "duration <= 365 days OR flagged as multi-year",
      "severity": "warning"
    },
    {
      "rule_id": "SCHED-002",
      "name": "Critical path coverage",
      "check": "critical_path_length == total_duration OR flag inconsistency",
      "severity": "error"
    },
    {
      "rule_id": "SCHED-003",
      "name": "Milestone feasibility",
      "check": "milestone_date within activity early/late dates",
      "severity": "error"
    },
    {
      "rule_id": "SCHED-004",
      "name": "Resource constraint violation",
      "check": "peak_resource_utilization <= available_resources * 1.1",
      "severity": "warning"
    }
  ]
}
```

### Contract Enforceability Checks
```json
{
  "validation_rules": [
    {
      "rule_id": "CONTRACT-001",
      "name": "Mandatory clauses present",
      "check": "Includes payment schedule, retention, performance bond",
      "severity": "critical"
    },
    {
      "rule_id": "CONTRACT-002",
      "name": "Risk allocation fairness",
      "check": "Cost overrun split does not exceed 70/30 extremes",
      "severity": "warning"
    },
    {
      "rule_id": "CONTRACT-003",
      "name": "Force majeure definition",
      "check": "Clearly defines covered events and contractor obligations",
      "severity": "warning"
    }
  ]
}
```

