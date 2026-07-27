# MAESTRO Monitoring & Alerting Setup — v6.0 Production

**Version:** 1.0  
**Date:** 2026-07-26  
**Status:** Production Ready  
**Compliance:** R1 (audit logging, no PII, no credentials in logs)  

---

## Executive Summary

This document defines the complete monitoring, alerting, and observability stack for Maestro OS v6.0 in production. The system monitors:

- **20 agent orchestration** (Manta 00–16 + S1–S11 verticals)
- **8-phase project lifecycle** (estudo prévio → descomissionamento)
- **Multi-agent consensus voting** and semantic routing
- **Token budget tracking** across LLM API calls
- **Queue management** for async workflows
- **Agent response SLAs** per segment (S1–S11)

Integration points:
- Prometheus (metrics collection)
- Grafana (dashboards)
- Supabase (custom events, webhooks)
- PagerDuty (incident routing)
- ELK Stack (log aggregation)
- Slack (operational alerts)

---

## 1. Architecture Overview

### 1.1 Monitoring Stack Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Maestro Application                        │
│  (20 agents × 8 phases × 11 segments = ~200 workflows)       │
└─────────┬──────────────────────────────────────────┬─────────┘
          │                                            │
      ┌───▼────────┐                       ┌──────────▼────────┐
      │  Metrics   │                       │   Event Emitter   │
      │ (Prometheus)                       │  (Supabase Fn)    │
      └───┬────────┘                       └──────────┬────────┘
          │                                            │
      ┌───▼────────────────────────────────────────────▼─────┐
      │              Time-Series Database                     │
      │   Prometheus + Supabase Vector (pgvector)            │
      └───┬────────────────────────────────────────────┬─────┘
          │                                            │
    ┌─────▼──────┐                          ┌─────────▼────────┐
    │   Grafana  │                          │   ELK Stack      │
    │ (Dashboards)                          │ (Logs Agg.)      │
    └─────┬──────┘                          └─────────┬────────┘
          │                                            │
    ┌─────┴────────────────┬──────────────────────────┴──────┐
    │                      │                                  │
┌───▼────────┐    ┌────────▼──────┐           ┌──────────────▼──┐
│  PagerDuty │    │  Slack Bot    │           │  Audit Log (SP) │
│  (Critical)│    │  (Operations) │           │  (Compliance)   │
└────────────┘    └───────────────┘           └─────────────────┘
```

### 1.2 Metrics Pipeline

```
Agent Execution
     ↓
[Prometheus Client Library]
     ↓
[Metrics Exporter (port 9090)]
     ↓
[Prometheus Server] (scrape interval: 15s)
     ↓
[Time-Series DB] (30 days raw, 1 year aggregated)
     ↓
[Alert Rules Evaluation] (every 30s)
     ↓
[Notification Routing] (PagerDuty, Slack, Email)
```

---

## 2. Prometheus Metrics Export

### 2.1 Core Metrics

All metrics are prefixed with `maestro_` and tagged with labels for agent, segment, phase.

#### Execution Metrics

```yaml
maestro_execution_time_seconds:
  type: Histogram
  description: "Time from request submission to agent response"
  buckets: [1, 2, 5, 10, 15, 30, 60, 120, 300]
  labels:
    - agent_id (e.g., "manta-03-s1", "manta-01")
    - segment (S1..S11)
    - phase (estudo_previo, projeto_basico, projeto_executivo, obra, om, licitacao, dd, encerramento)
    - complexity (simple, medium, complex)

maestro_execution_total:
  type: Counter
  description: "Total number of executions by outcome"
  labels:
    - agent_id
    - segment
    - outcome (success, failure, timeout, consensus_fail)

maestro_execution_errors_total:
  type: Counter
  description: "Total execution errors by category"
  labels:
    - agent_id
    - error_type (routing_error, consensus_fail, token_limit, timeout, validation_error)
    - severity (warning, error, critical)
```

#### Consensus Voting Metrics

```yaml
maestro_consensus_voting:
  type: Gauge
  description: "Current consensus voting metrics"
  labels:
    - agent_id
    - voting_round
  variants:
    - maestro_consensus_vote_count_total (votes cast)
    - maestro_consensus_agreement_ratio (% agreement)
    - maestro_consensus_round_time_seconds (voting latency)

maestro_consensus_rate:
  type: Gauge
  description: "Consensus achievement rate over last hour"
  labels:
    - agent_id
    - segment
  values: 0.0–1.0 (%)
```

#### Token Usage Metrics

```yaml
maestro_token_usage_total:
  type: Counter
  description: "Cumulative tokens consumed by agent"
  labels:
    - agent_id
    - model (claude-opus, claude-sonnet, claude-haiku)
    - token_type (input, output)

maestro_token_budget_ratio:
  type: Gauge
  description: "Ratio of consumed to allocated budget"
  labels:
    - agent_id
    - period (daily, monthly)
  values: 0.0–1.0 (%)

maestro_token_rate_per_minute:
  type: Gauge
  description: "Tokens consumed per minute (instantaneous)"
  labels:
    - agent_id
```

#### Queue Metrics

```yaml
maestro_queue_depth:
  type: Gauge
  description: "Number of pending tasks in queue"
  labels:
    - queue_type (execution, consensus, webhook)
    - segment

maestro_queue_wait_time_seconds:
  type: Histogram
  description: "Time spent waiting in queue before execution"
  buckets: [0.5, 1, 2, 5, 10, 30, 60]
  labels:
    - queue_type
    - segment

maestro_queue_dropped_total:
  type: Counter
  description: "Tasks dropped due to queue overflow"
  labels:
    - queue_type
    - reason (timeout, capacity, error)
```

#### Agent Response Metrics

```yaml
maestro_agent_response_time_seconds:
  type: Histogram
  description: "Time for agent to respond to single request"
  buckets: [0.1, 0.5, 1, 2, 5, 10, 15, 30, 60]
  labels:
    - agent_id
    - segment
    - request_type (query, validation, routing, consensus)

maestro_agent_availability:
  type: Gauge
  description: "Agent uptime percentage"
  labels:
    - agent_id
    - segment
  values: 0.0–1.0 (%)

maestro_agent_last_response_timestamp:
  type: Gauge
  description: "Unix timestamp of last successful response"
  labels:
    - agent_id
```

#### System Health Metrics

```yaml
maestro_api_requests_total:
  type: Counter
  description: "Total API requests by endpoint"
  labels:
    - endpoint (/agents, /execute, /routing, /consensus)
    - method (GET, POST)
    - status_code (200, 400, 403, 500)

maestro_database_connection_pool_size:
  type: Gauge
  description: "Active database connections"
  labels:
    - database (supabase, prometheus)

maestro_llm_api_calls_total:
  type: Counter
  description: "Calls to external LLM APIs"
  labels:
    - provider (anthropic)
    - model
    - status (success, rate_limit, error)

maestro_cache_hits_total:
  type: Counter
  description: "Cache hits (routing decisions, embeddings)"
  labels:
    - cache_type (routing, embedding, consensus)

maestro_cache_miss_ratio:
  type: Gauge
  description: "Ratio of cache misses to total lookups"
  labels:
    - cache_type
```

---

[Content truncated for space - continues with sections 2.2, 3, 4, 5, 6, 7, 8, 9, 10, and appendix...]

---

**Document Status:** Production Ready  
**Last Updated:** 2026-07-26  
**Next Review:** 2026-09-26 (quarterly)
