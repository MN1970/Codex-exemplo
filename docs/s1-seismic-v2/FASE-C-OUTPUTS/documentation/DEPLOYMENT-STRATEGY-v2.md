# Manta Maestro — Deployment Strategy Part 2
**Version:** 1.0 | **Date:** 2026-07-25

---

## PART 6: TESTING STRATEGY (UNIT, INTEGRATION, E2E)

### 6.1 Unit Testing

**Scope:** Individual agent functions (input validation, computation, output formatting)  
**Framework:** Jest + Supertest  
**Coverage Target:** >90% line coverage per agent  
**Execution:** Automated on each commit (CI/CD)

#### Test Cases by Agent

**Agent-05 (Orçamento): 45 test cases**
```javascript
describe('Agent-05: Orçamento', () => {
  describe('Input Validation', () => {
    test('SICRO code validation: valid format DNIT-YYYY-NNN', () => {});
    test('SICRO code validation: reject invalid format', () => {});
    test('WBS quantity validation: must be > 0', () => {});
    test('Contingency percent: must be 10-25%', () => {});
    test('Location factor: must be 0.8-1.5', () => {});
    test('Missing required field: throw 400 error', () => {});
  });
  
  describe('Cost Calculations', () => {
    test('Direct costs: sum of all line items', () => {});
    test('Indirect costs: calculated as % of direct', () => {});
    test('Contingency: applied to (direct + indirect)', () => {});
    test('Financing costs: calculated based on duration', () => {});
    test('Total project: sum all components', () => {});
    test('Inflation adjustment: linear by month', () => {});
  });
  
  describe('Sensitivity Analysis', () => {
    test('SICRO variance ±10%: output ranges correct', () => {});
    test('Duration variance ±3 months: cost impact', () => {});
    test('Contingency variance ±5%: result stability', () => {});
  });
  
  describe('Edge Cases', () => {
    test('Zero-duration project: no financing costs', () => {});
    test('Very large project: no overflow errors', () => {});
    test('Negative risk impact: treated as upside', () => {});
  });
});
```

**Agent-07 (Cronograma): 42 test cases**
```javascript
describe('Agent-07: Cronograma', () => {
  describe('Network Validation', () => {
    test('Detect circular dependencies: throw error', () => {});
    test('Detect orphaned activities: warn user', () => {});
    test('Validate predecessor relationships', () => {});
    test('Check for duplicate activity codes', () => {});
  });
  
  describe('Schedule Calculations', () => {
    test('Forward pass: correct early start/finish', () => {});
    test('Backward pass: correct late start/finish', () => {});
    test('Critical path: longest duration through network', () => {});
    test('Slack calculation: total and free', () => {});
    test('Project finish date: max activity finish', () => {});
  });
  
  describe('Resource Management', () => {
    test('Peak resource utilization: correct aggregation', () => {});
    test('Resource leveling: smooth curve without overallocation', () => {});
    test('Learning curve: productivity increases over time', () => {});
  });
  
  describe('Risk Scenarios', () => {
    test('Weather delay scenario: adds days to critical activities', () => {});
    test('Resource shortage: extends schedule', () => {});
    test('Probability weighting: E(X) calculation', () => {});
  });
});
```

**Agent-15 (Advisory): 38 test cases**
```javascript
describe('Agent-15: Advisory', () => {
  describe('Viability Scoring', () => {
    test('Score calculation: 8 factors weighted', () => {});
    test('Score range: 1-10 with mapping to colors', () => {});
    test('Risk trend: increasing/stable/decreasing', () => {});
  });
  
  describe('Risk Assessment', () => {
    test('Criticality = Probability × Impact', () => {});
    test('Top 3 risks: ranked by criticality', () => {});
    test('Residual risk: after mitigation', () => {});
    test('Risk register: complete and traceable', () => {});
  });
  
  describe('Recommendations', () => {
    test('Recommendation logic: based on viability score', () => {});
    test('Mitigation strategies: specific and actionable', () => {});
  });
});
```

**Agent-02 (Contratual): 35 test cases**
- Clause presence checks (mandatory clauses)
- Fairness scoring (cost/risk allocation)
- Compliance validation (Brazilian law)
- Payment schedule analysis
- Enforceability checks

### 6.2 Integration Testing

**Scope:** Agent-to-agent communication, data flow across 4-agent pipeline  
**Framework:** Jest + API mocking (nock)  
**Test Scenarios:** 15 workflows

#### Workflow 1: Cost → Schedule → Advisory → Contract
```javascript
describe('Integration: Full 4-Agent Pipeline', () => {
  let projectId, costOutput, scheduleOutput, advisoryOutput;
  
  test('Step 1: Agent-05 generates cost forecast', async () => {
    const costInput = fixtures.costInput;
    costOutput = await agentCost.call(costInput);
    expect(costOutput.status).toBe('success');
    expect(costOutput.cost_forecast).toBeDefined();
    projectId = costOutput.project_id;
  });
  
  test('Step 2: Agent-07 receives cost output, generates schedule', async () => {
    const scheduleInput = {
      ...fixtures.scheduleInput,
      project_id: projectId,
      cost_data: costOutput.cost_forecast
    };
    scheduleOutput = await agentSchedule.call(scheduleInput);
    expect(scheduleOutput.status).toBe('success');
    expect(scheduleOutput.schedule_forecast).toBeDefined();
  });
  
  test('Step 3: Agent-15 receives cost & schedule, generates advisory', async () => {
    const advisoryInput = {
      ...fixtures.advisoryInput,
      project_id: projectId,
      cost_forecast: costOutput.cost_forecast,
      schedule_forecast: scheduleOutput.schedule_forecast
    };
    advisoryOutput = await agentAdvisory.call(advisoryInput);
    expect(advisoryOutput.status).toBe('success');
    expect(advisoryOutput.advisory_summary).toBeDefined();
  });
  
  test('Step 4: Agent-02 receives all prior outputs, generates contract assessment', async () => {
    const contractInput = {
      ...fixtures.contractInput,
      project_id: projectId,
      cost_forecast: costOutput.cost_forecast,
      schedule_forecast: scheduleOutput.schedule_forecast,
      advisory_summary: advisoryOutput.advisory_summary
    };
    const contractOutput = await agentContract.call(contractInput);
    expect(contractOutput.status).toBe('success');
    expect(contractOutput.contract_assessment).toBeDefined();
  });
});
```

#### Workflow 2-15: Additional scenarios
- Saneamento (S8) pipeline: cost → schedule → compliance check
- Energia (S9) pipeline: cost → feasibility → ANEEL compliance
- Missing data handling: fallback data injection
- Error propagation: error in step N stops pipeline
- Timeout handling: any agent >10s triggers fallback
- Cache validation: RAG data consistency
- Concurrent requests: 10 projects in parallel
- Data isolation: project A data doesn't leak to project B

### 6.3 End-to-End (E2E) Testing

**Scope:** Full user workflows in staging environment  
**Tools:** Cypress + Real Database  
**Scenarios:** 12 test cases  
**Duration:** 30-45 min per test run

#### E2E Test 1: Create project → Cost estimate → Schedule → Go/No-Go decision
```javascript
describe('E2E: Complete project workflow', () => {
  before(() => {
    cy.visit('https://staging.manta-maestro.com');
    cy.login('test_user@manta.com', 'password');
  });
  
  it('User creates new project with baseline data', () => {
    cy.contains('button', 'New Project').click();
    cy.get('input[name="project_name"]').type('Rodovia BR-101');
    cy.get('select[name="segment"]').select('S1');
    cy.get('select[name="phase"]').select('projeto_executivo');
    cy.contains('button', 'Create').click();
    cy.contains('Project created successfully').should('be.visible');
  });
  
  it('User uploads cost data (WBS, SICRO codes)', () => {
    cy.contains('Cost').click();
    cy.get('input[type="file"]').selectFile('fixtures/wbs.xlsx');
    cy.contains('button', 'Upload').click();
    cy.get('.progress-bar').should('not.exist'); // wait for upload
    cy.contains('45 cost items loaded').should('be.visible');
  });
  
  it('User triggers cost forecast', () => {
    cy.contains('button', 'Generate Cost Forecast').click();
    cy.contains('Processing...').should('be.visible');
    cy.get('[data-testid="cost_forecast"]', { timeout: 10000 })
      .should('be.visible')
      .and('contain', '3.76M');
  });
  
  it('Cost forecast is accurate (within 5% of expected)', () => {
    cy.get('[data-testid="cost_total"]').then($el => {
      const actual = parseFloat($el.text());
      const expected = 3764500;
      expect(Math.abs(actual - expected) / expected).to.be.lessThan(0.05);
    });
  });
  
  it('User uploads network and generates schedule', () => {
    cy.contains('Schedule').click();
    cy.get('input[type="file"]').selectFile('fixtures/network.ms');
    cy.contains('button', 'Generate Schedule').click();
    cy.get('[data-testid="schedule_forecast"]', { timeout: 10000 })
      .should('be.visible');
  });
  
  it('Critical path and milestones are visible', () => {
    cy.get('[data-testid="critical_path"]')
      .should('contain', '714 days');
    cy.get('[data-testid="milestone_list"] li').should('have.length.greaterThan', 0);
  });
  
  it('User views advisory summary', () => {
    cy.contains('Advisory').click();
    cy.get('[data-testid="viability_score"]').should('contain', '7.8');
    cy.get('[data-testid="recommendation"]')
      .should('contain', 'Proceed with caution');
  });
  
  it('User exports full project report (PDF)', () => {
    cy.contains('button', 'Export Report').click();
    cy.readFile('cypress/downloads/project_report.pdf')
      .should('exist');
  });
});
```

#### E2E Test 2-12: Additional workflows
- Saneamento-specific workflow (ETA design, SNIS compliance)
- Energia-specific workflow (ANEEL RAP review)
- Multi-project comparison (3 alternatives)
- Concurrent project updates
- User permission boundaries (read-only vs edit)
- Error recovery (retry after API failure)
- Performance under load (100 concurrent users)
- Mobile responsiveness
- Dark mode rendering
- Internationalization (Portuguese + English)
- Accessibility (keyboard navigation, screen reader)
- Data export (Excel, PDF, JSON)

---

## PART 7: ROLLBACK PROCEDURES

### 7.1 Rollback Decision Tree

```
Production Issue Detected
    │
    ├─ P0 (Critical): Entire feature unavailable, >100 users impacted
    │   → IMMEDIATE rollback (decision time: <5 min)
    │
    ├─ P1 (High): Major degradation, >20 users impacted, workaround exists
    │   → Rollback OR hotfix (decision time: <30 min)
    │
    └─ P2 (Medium): Minor issue, <20 users impacted, workaround exists
        → Continue monitoring, plan fix in next sprint
```

### 7.2 Rollback Steps (Agent Deployment)

#### Phase 1: Preparation (Before Deployment)
```bash
# Day before deployment: Create backup artifacts

# 1. Snapshot current agent versions
aws s3 cp s3://manta-agents/agent-05/v3.2.1/ \
  s3://manta-agents-backup/pre-deployment-2027-03-01/agent-05/ --recursive
aws s3 cp s3://manta-agents/agent-07/v2.8.3/ \
  s3://manta-agents-backup/pre-deployment-2027-03-01/agent-07/ --recursive
aws s3 cp s3://manta-agents/agent-15/v2.5.0/ \
  s3://manta-agents-backup/pre-deployment-2027-03-01/agent-15/ --recursive
aws s3 cp s3://manta-agents/agent-02/v1.9.2/ \
  s3://manta-agents-backup/pre-deployment-2027-03-01/agent-02/ --recursive

# 2. Snapshot database schema
pg_dump --host=prod-db-master --username=admin \
  --dbname=manta_maestro --schema=public \
  > /backups/db-schema-pre-deploy-2027-03-01.sql

# 3. Snapshot database data (transactions, projects, costs)
pg_dump --host=prod-db-replica --username=readonly \
  --dbname=manta_maestro --data-only \
  > /backups/db-data-pre-deploy-2027-03-01.sql

# 4. Snapshot RAG collections (Supabase)
./scripts/export_rag_collections.sh > /backups/rag-2027-03-01.json

# 5. Document current SLAs
cat <<EOF > /backups/current-slas-2027-03-01.txt
Agent-05 latency: p50=850ms, p99=1800ms
Agent-07 latency: p50=1200ms, p99=2100ms
Agent-15 latency: p50=950ms, p99=1600ms
Agent-02 latency: p50=780ms, p99=1450ms
Error rate: <0.5%
Availability: 99.95%
EOF
```

#### Phase 2: Immediate Rollback (If P0 Issue Within 1 Hour)

**Step 1: Stop New Deployments (0-2 minutes)**
```bash
# Disable all agent deployments in CI/CD
kubectl patch deployment agent-05 --type='json' \
  -p='[{"op":"replace","path":"/spec/replicas","value":0}]'
kubectl patch deployment agent-07 --type='json' \
  -p='[{"op":"replace","path":"/spec/replicas","value":0}]'
kubectl patch deployment agent-15 --type='json' \
  -p='[{"op":"replace","path":"/spec/replicas","value":0}]'
kubectl patch deployment agent-02 --type='json' \
  -p='[{"op":"replace","path":"/spec/replicas","value":0}]'

# Verify no pods running
kubectl get pods -n manta-agents | grep -E 'agent-(05|07|15|02)'
```

**Step 2: Restore Previous Agent Versions (2-5 minutes)**
```bash
# Pull previous versions from backup
aws s3 sync s3://manta-agents-backup/pre-deployment-2027-03-01/agent-05/ \
  s3://manta-agents/agent-05/ --delete

# Restart agents with previous version
kubectl rollout undo deployment agent-05 -n manta-agents
kubectl rollout undo deployment agent-07 -n manta-agents
kubectl rollout undo deployment agent-15 -n manta-agents
kubectl rollout undo deployment agent-02 -n manta-agents

# Wait for pods to be ready
kubectl rollout status deployment/agent-05 -n manta-agents
kubectl rollout status deployment/agent-07 -n manta-agents
kubectl rollout status deployment/agent-15 -n manta-agents
kubectl rollout status deployment/agent-02 -n manta-agents
```

**Step 3: Verify Service Health (5-10 minutes)**
```bash
# Check agent health endpoints
curl -s http://agent-05-service:8080/health
curl -s http://agent-07-service:8080/health
curl -s http://agent-15-service:8080/health
curl -s http://agent-02-service:8080/health

# Verify latency is within SLA
./scripts/verify-slas.sh --baseline /backups/current-slas-2027-03-01.txt

# Check error rates
curl -s http://metrics:9090/api/v1/query \
  'sum(rate(http_requests_total{job="agent-05"}[5m]))'
```

**Step 4: Notify Stakeholders (5-10 minutes)**
```bash
# Send alerts
./scripts/notify-slack.sh "ROLLBACK INITIATED: Agents reverted to v3.2.1 (05), v2.8.3 (07), v2.5.0 (15), v1.9.2 (02)"
./scripts/notify-email.sh --to "mneves@mantaassociados.com,support@manta.com" \
  --subject "Production Rollback: Agent Deployment Failed"

# Update status page
curl -X PATCH https://status.manta-maestro.com/api/v1/incidents/ongoing \
  -d '{"status": "investigating", "description": "Agent deployment rolled back"}'
```

**Step 5: Post-Incident Review (Within 24 hours)**
- Document what failed and why
- Schedule RCA (root cause analysis) meeting
- Plan fix and re-deployment

#### Phase 3: Database Rollback (If Data Corruption)

**If cost/schedule/advisory data corrupted:**
```bash
# 1. Stop all write operations
# (Feature flag: disable cost/schedule creation)
kubectl set env deployment/api-gateway \
  FEATURE_FLAG_DISABLE_WRITES=true

# 2. Restore from point-in-time backup
# (Assumes continuous WAL archiving enabled)
pg_restore --host=prod-db-master --username=admin \
  --dbname=manta_maestro --verbose \
  /backups/db-data-pre-deploy-2027-03-01.sql

# 3. Verify data integrity
./scripts/validate-data-integrity.sh

# 4. Re-enable writes
kubectl set env deployment/api-gateway \
  FEATURE_FLAG_DISABLE_WRITES=false
```

---

## PART 8: GO-LIVE CHECKLIST (50+ ITEMS)

### Pre-Deployment Phase

#### Infrastructure & Deployment (8 items)
- [ ] Production Kubernetes cluster: all nodes healthy, capacity >150% max load
- [ ] Database: master/replica replication lag <100ms
- [ ] Load balancer: configured for agent services (agent-05, 07, 15, 02)
- [ ] Auto-scaling policies: configured (min 2, max 10 pods per agent)
- [ ] Container registry: all agent images pushed and scanned for vulnerabilities
- [ ] DNS: agent hostnames resolve to load balancer IPs
- [ ] SSL certificates: valid for all agent domains (expiry >30 days)
- [ ] Backup infrastructure: daily snapshots enabled, restore test passed

#### Application Health (6 items)
- [ ] All unit tests passing (>90% code coverage)
- [ ] All integration tests passing (15 workflows, 0 failures)
- [ ] All E2E tests passing (12 scenarios, 0 failures)
- [ ] Performance tests: latency p99 <2s per agent, p99 <5s orchestration
- [ ] Load tests: sustained 100 RPS with <5% error rate
- [ ] Staging environment: identical to production, 72-hour soak test passed

#### Data & RAG (5 items)
- [ ] RAG collections loaded: all S1-S10 data present (500K+ documents)
- [ ] SICRO database: latest 2023 rates loaded, 15K+ entries
- [ ] Test data: 100 realistic projects created and validated
- [ ] Data migration: no data loss from legacy system
- [ ] Audit log: all RAG changes tracked and auditable

#### Documentation & Training (7 items)
- [ ] API specification: complete, all agents documented (OpenAPI 3.1)
- [ ] Runbooks: deployment, troubleshooting, rollback (>100 pages)
- [ ] User guides: one per agent, step-by-step workflows (<10 pages each)
- [ ] Training materials: videos (5), slides (3 decks), FAQs (20 items)
- [ ] Internal team training: completed (100% of ops/support staff)
- [ ] Pilot org training: completed (3 orgs, signed-off)
- [ ] Change log: release notes documented, approved by MN

#### Monitoring & Alerts (6 items)
- [ ] Datadog dashboards: deployed and tested (agent latency, error rate, throughput)
- [ ] Alert rules: configured (latency >3s, error rate >2%, availability <99.5%)
- [ ] Logging: all agents logging to ELK stack, queries validated
- [ ] APM instrumentation: agent dependencies traced end-to-end
- [ ] SLA tracking: baseline metrics documented and stored
- [ ] On-call rotation: calendar set up, escalation paths defined

#### Security & Compliance (5 items)
- [ ] Security audit: passed (no critical findings, P1/P2 issues documented)
- [ ] Penetration testing: passed (input validation, injection, SSRF)
- [ ] Data encryption: TLS 1.3 for all inter-service communication
- [ ] Access control: RBAC configured, least-privilege principle enforced
- [ ] Compliance: GDPR/LGPD data handling procedures documented

#### Support & Communication (5 items)
- [ ] Support ticket system: configured, SLA times set (P0: 1h, P1: 4h, P2: 24h)
- [ ] War room: Slack channel created (#manta-agents-war-room)
- [ ] Escalation contacts: list created and distributed (MN, tech lead, ops)
- [ ] Maintenance window: communicated to all customers (email + portal)
- [ ] Rollback decision criteria: documented and approved

---

### Deployment Phase

#### Pre-Flight Checks (4 items)
- [ ] All pre-deployment checklist items: completed (50/50 ✓)
- [ ] Smoke test in staging: passed (all agents responding)
- [ ] Production database backup: completed and verified
- [ ] Rollback artifacts: staged and tested

#### Deployment Execution (6 items)
- [ ] Deploy agent-05 (orçamento): to 25% canary, verify latency/errors
- [ ] Deploy agent-07 (cronograma): to 25% canary, verify latency/errors
- [ ] Deploy agent-15 (advisory): to 50% canary, verify latency/errors
- [ ] Deploy agent-02 (contratual): to 50% canary, verify latency/errors
- [ ] Monitor for 30 min: latency p99 <2s, error rate <0.5%, no P0 issues
- [ ] Gradual rollout: increase traffic to 100% over 4 hours

#### Post-Deployment Verification (5 items)
- [ ] Production agents: all responding, health check: OK
- [ ] Latency: p50 <1s, p99 <2s per agent (matches staging)
- [ ] Error rate: <0.5% (matches baseline)
- [ ] Customer projects: cost/schedule/advisory data flowing correctly
- [ ] RAG data: queries responding, fallback data available

---

### Post-Go-Live Phase (Week 1)

#### Monitoring & Support (5 items)
- [ ] War room: active monitoring (24/5 coverage)
- [ ] Customer feedback: tracked (forum, email, support tickets)
- [ ] Incident response: any P0 resolved <1h, P1 resolved <4h
- [ ] Performance trending: latency/error rate stable
- [ ] Data quality: cost/schedule forecasts validated against 10 pilot projects

#### Documentation Updates (3 items)
- [ ] Known issues log: updated daily with workarounds
- [ ] FAQ: answers to customer questions documented
- [ ] Runbook updates: based on actual issues encountered

#### Team Handoff (3 items)
- [ ] Knowledge transfer: ops team fully trained and independent
- [ ] On-call rotation: successfully executed first week
- [ ] Escalation contacts: successfully contacted for test issue

---

## PART 9: POST-GO-LIVE SUPPORT (3-MONTH MONITORING)

### Month 1: Stabilization Phase

**Week 1: Crisis Management**
- Daily standup (9 AM): all hands, 15 min
- P0 response time: <30 min, resolution <1 hour
- Metrics review: latency, error rate, throughput
- Customer feedback: live Q&A in Slack (#manta-agents-general)
- Action items: log all bugs, categorize by severity

**Week 2-4: Refinement**
- Twice-weekly standups (Mon/Thu)
- P1 issues: resolution target <4 hours
- Performance optimization: identify bottlenecks, apply fixes
- Documentation updates: based on customer questions
- Pilot org check-ins: satisfaction survey, NPS scoring

### Month 2: Optimization Phase

**Focus:** Improve performance, reduce error rate, increase adoption
- Weekly standups (Mon)
- Latency optimization: identify agents >1.5s p99, apply caching
- Error analysis: top 5 failure modes, root cause analysis
- Customer training: webinar series (4 sessions, 1 per segment)
- Documentation: user guides expanded, FAQ consolidated

### Month 3: Transition Phase

**Focus:** Hand off to operations, prepare for next sprint
- Bi-weekly standups (Mon, alternate weeks)
- SLA review: compare actual vs target, document variances
- Team competency check: on-call team ready for independence
- Lessons learned: retrospective with dev team, implement improvements
- Success metrics: adoption rate, NPS, cost accuracy (within 5% of forecast)

### Key Metrics (Tracked Daily)

```json
{
  "availability": {
    "target": "99.95%",
    "tracking": "error_rate * 100",
    "alert_threshold": "<99.50%"
  },
  "latency": {
    "agent_05": {
      "p50_target_ms": 850,
      "p99_target_ms": 2000,
      "alert_threshold_p99_ms": 3000
    },
    "agent_07": {
      "p50_target_ms": 1200,
      "p99_target_ms": 2100,
      "alert_threshold_p99_ms": 3200
    },
    "agent_15": {
      "p50_target_ms": 950,
      "p99_target_ms": 1600,
      "alert_threshold_p99_ms": 2400
    },
    "agent_02": {
      "p50_target_ms": 780,
      "p99_target_ms": 1450,
      "alert_threshold_p99_ms": 2200
    }
  },
  "error_rate": {
    "target": "<0.5%",
    "alert_threshold": ">1.0%"
  },
  "data_quality": {
    "cost_accuracy": "within ±5% of manual estimates",
    "schedule_accuracy": "within ±7% of baseline",
    "advisory_recommendations": "alignment with domain experts >85%"
  }
}
```

---

## PART 10: TRAINING MATERIALS OUTLINE

### 10.1 Video Tutorials (5 videos, 5-10 min each)

**Video 1: Agent-05 Cost Modeling Workflow (7 min)**
- Scenario: First-time user creates cost estimate for rodovia project
- Topics: WBS structure, SICRO codes, contingency policy, sensitivity analysis
- Demo: Upload cost data → Generate forecast → Export report
- Link to: User Guide (Agent-05)

**Video 2: Agent-07 Schedule Management (8 min)**
- Scenario: Scheduler creates network diagram and critical path analysis
- Topics: Activity definition, predecessor relationships, resource constraints, leveling
- Demo: Import MS Project → Generate schedule → Analyze critical path
- Link to: User Guide (Agent-07)

**Video 3: Agent-15 Advisory & Risk Management (6 min)**
- Scenario: PM reviews project viability score and risks
- Topics: Viability scoring, risk register, mitigation strategies, recommendations
- Demo: View advisory dashboard → Track risks → Export risk register
- Link to: User Guide (Agent-15)

**Video 4: Multi-Agent Integration (9 min)**
- Scenario: Project manager runs full 4-agent workflow
- Topics: Data flow from cost → schedule → advisory → contract
- Demo: Create project → Cost forecast → Schedule → Advisory → Contract assessment
- Link to: Integration Guide

**Video 5: Troubleshooting & Error Recovery (6 min)**
- Scenario: Common issues and how to resolve them
- Topics: Missing SICRO codes, data validation errors, timeout handling, rollback
- Demo: Various error scenarios and recovery procedures
- Link to: Troubleshooting Guide

### 10.2 Slide Decks (3 presentations, 60-90 min each)

**Deck 1: Agent Overview & Architecture (Tech Team)**
- Slide 1-5: Manta Maestro architecture, agent roles, data flow
- Slide 6-10: Agent-05, 07, 15, 02 APIs and contracts
- Slide 11-15: Error handling, resilience, monitoring
- Slide 16-20: Deployment strategy, rollback procedures
- Slide 21-25: Q&A, technical deep dives

**Deck 2: Agent Usage Guide (Domain Users)**
- Slide 1-3: Welcome, agenda, objectives
- Slide 4-8: What each agent does, typical workflows
- Slide 9-15: Cost modeling (step-by-step)
- Slide 16-22: Schedule management (step-by-step)
- Slide 23-28: Risk advisory (step-by-step)
- Slide 29-35: Best practices, tips & tricks
- Slide 36-40: Q&A, hands-on exercises

**Deck 3: Executive Overview (C-Suite)**
- Slide 1-2: Business impact, value proposition
- Slide 3-5: Problem statement (before Manta)
- Slide 6-8: Solution (Manta agents)
- Slide 9-12: Key benefits (faster estimates, better forecasts, lower risk)
- Slide 13-15: Adoption roadmap, success metrics
- Slide 16-18: ROI, business case
- Slide 19-20: Q&A, next steps

### 10.3 User Guides (4 guides, 8-12 pages each)

**Guide 1: Agent-05 User Guide (Cost Modeling)**
- Chapter 1: Overview (what, why, when)
- Chapter 2: Input data requirements (WBS, SICRO, location factor)
- Chapter 3: Running cost forecast (step-by-step)
- Chapter 4: Interpreting results (cost breakdown, sensitivity)
- Chapter 5: Advanced topics (custom rates, inflation, financing)
- Chapter 6: FAQ & troubleshooting (common errors)

**Guide 2: Agent-07 User Guide (Schedule Management)**
- Chapter 1: Overview
- Chapter 2: Network input (activities, relationships, durations)
- Chapter 3: Running schedule (step-by-step)
- Chapter 4: Interpreting results (critical path, slack, milestones)
- Chapter 5: Advanced topics (resource leveling, productivity, risk)
- Chapter 6: FAQ & troubleshooting

**Guide 3: Agent-15 User Guide (Risk Advisory)**
- Chapter 1: Overview
- Chapter 2: Input requirements (project status, risks, concerns)
- Chapter 3: Running advisory (step-by-step)
- Chapter 4: Interpreting results (viability score, risk assessment)
- Chapter 5: Advanced topics (mitigation strategies, recommendations)
- Chapter 6: FAQ & troubleshooting

**Guide 4: Integration & Workflow Guide**
- Chapter 1: End-to-end project workflow (cost → schedule → advisory → contract)
- Chapter 2: Data flow between agents
- Chapter 3: Multi-project comparison
- Chapter 4: Exporting reports (PDF, Excel, JSON)
- Chapter 5: Troubleshooting workflow issues
- Chapter 6: Best practices for different project types (S1-S10)

### 10.4 Knowledge Base (FAQ + Troubleshooting, 20+ articles)

**Frequently Asked Questions**
1. "What data do I need to provide?" (cost, schedule, risks)
2. "How accurate are the forecasts?" (±5% for cost, ±7% for schedule)
3. "Can I modify agent outputs?" (yes, all outputs are editable)
4. "How do I export reports?" (PDF, Excel, JSON formats)
5. "What if my SICRO code isn't found?" (fallback to generic rates)
6. "Can agents handle project changes?" (yes, re-run with updated data)
7. "How long does each agent take?" (<2s typical)
8. "Can I run agents in offline mode?" (no, requires cloud connection)
9. "What about data privacy?" (GDPR/LGPD compliant, encryption)
10. "Who do I contact for support?" (support@manta.com, Slack #support)

**Troubleshooting Articles**
1. "Agent-05 returned 'SICRO code not found' error"
   - Root cause: SICRO code format incorrect or outdated
   - Solution: Use 2023 format (DNIT-2023-NNN) or generic rate
   
2. "Agent-07 detected circular dependencies"
   - Root cause: Activity predecessor/successor relationships invalid
   - Solution: Review network diagram, fix cycle
   
3. "Agent-15 viability score is red (4.2/10)"
   - Root cause: Multiple risks with high criticality
   - Solution: Review risk mitigation strategies, escalate to PM
   
4. "Forecast takes >5 seconds (timeout warning)"
   - Root cause: Large project (1000+ activities), slow RAG queries
   - Solution: Break project into phases, or use simplified mode
   
5. "Data not flowing between agents"
   - Root cause: Intermediate agent failed or timed out
   - Solution: Check error logs, verify project data integrity
   
6. "Agent output differs from my manual estimate"
   - Root cause: Different assumptions (duration, contingency, rates)
   - Solution: Adjust inputs to match assumptions, run sensitivity analysis
   
7. "Can't login to staging environment"
   - Root cause: User credentials or role permissions
   - Solution: Contact IT (it-support@manta.com)
   
8. "Export to PDF is blank or corrupted"
   - Root cause: Large report, browser memory limit
   - Solution: Export Excel first, convert to PDF separately
   
9. "Pilot org still seeing old agent version"
   - Root cause: Browser cache, CloudFlare cache
   - Solution: Hard refresh (Ctrl+Shift+R), clear cache
   
10. "Performance is slow (latency >3s)"
    - Root cause: External API slowdown or network congestion
    - Solution: Wait 5 min and retry, escalate if persistent

---

**End of Deployment Strategy Document**

**File Location:** `/tmp/claude-0/.../DEPLOYMENT-STRATEGY-v1.md` (Part 1)  
**File Location:** `/tmp/claude-0/.../DEPLOYMENT-STRATEGY-v2.md` (Part 2)

**Total Lines:** 2,100+ across both files  
**Status:** Ready for implementation, all sections complete

