# Changelog

All notable changes to the Maestro OS project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.0.0] - 2026-07-27

### Added

- **Phase A: Maestro OS Core** — Dynamic agent scaling (8–16 agents), consensus voting (3/5 super-majority), queue executor with rate limiting, YAML DSL parser
- **Phase B: ML Pipeline** — XGBoost routing model, NN duration predictor, NN risk classifier, real-time inference with LRU cache
- **Phase C: Claude Code + Engenharia** — CAD integration, RAG retrieval, code execution sandbox, normative compliance checking, what-if scenario simulation
- **Phase D: Operational Readiness** — CI/CD automation (GitHub Actions), monitoring stack (Prometheus/Grafana/ELK/PagerDuty), incident management, disaster recovery

### Changed

- Maestro router upgraded from serial hub-and-spoke (v5.0.1) to parallel orchestration
- Agent pool expanded from 20 to support dynamic scaling up to 16 concurrent agents
- Consensus engine now uses super-majority voting (3/5) instead of simple voting

### Infrastructure

- **CI/CD Workflows**
  - maestro-ci.yml: Continuous integration with code quality, security scanning, tests
  - maestro-deploy.yml: Blue-green deployment with staging validation and approval gates
  - maestro-nightly.yml: Automated health checks and metrics collection

- **Monitoring**
  - Prometheus: 16 metric families, 25+ variants
  - Grafana: 4 dashboard sections (system health, consensus, agent performance, queue)
  - Alert routing: PagerDuty escalation, Slack notifications, ELK logging

- **Documentation**
  - Operations runbook with SLAs and procedures
  - Team training curriculum (12-topic certification)
  - Troubleshooting guides and incident response templates
  - Disaster recovery procedures (RTO 4h, RPO 1h)

### Fixed

- GitHub Actions workflow syntax (bash parameter expansion)
- Deployment validation checklist integration

## [5.0.1] - 2026-07-26

### Added

- Consolidated agent registry with 20 operationalagents (11 horizontal + 9 vertical S1–S11)
- Canonical RAG architecture (bge-small-en-v1.5, 384-d embeddings)
- 5 new vertical agents (S7–S11: Portos, Aeroportos, Saneamento, Energia, Barragens)

### Changed

- Unified CLAUDE.md master registry from two sources (Drive A + Drive B)
- Standardized segment numbering (S1–S11) across all agents
- Applied R1 compliance (no PII in audit logs)

## [5.0.0] - 2026-07-22

### Added

- 5 new segment agents (S6–S10): Portos, Aeroportos, Saneamento, Energia, Barragens
- Router intelligence for semantic pattern matching
- Support for 8 lifecycle phases (estudo prévio → descomissionamento)
- RAG with 5 collections (Saneamento, Energia, Portos, Aeroportos, Barragens)

---

**Validation:** All phases tested and integrated ✅
