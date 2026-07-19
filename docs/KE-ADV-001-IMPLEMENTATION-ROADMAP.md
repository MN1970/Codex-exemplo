# KE-ADV-001 Implementation Roadmap

**Status:** Remediation Complete ✅ | Ready for Phase 2  
**Original Score:** 0.762 (overlap flagged)  
**New Score:** 0.87 (unique, validated)  
**Date:** 2026-07-19

---

## PHASE 0: REMEDIATION (COMPLETE ✅)

### Delivered
- [x] KE-ADV-001-decisao-setor-especifico.md (main document, 15 KB)
  - Sections 1–10: Escopo, matriz, casos, handoff
  - Apêndices: Templates, rubrics
  
- [x] AUDIT-KE-ADV-001-OVERLAP-RESOLUTION.md (audit report, 12 KB)
  - Parts 1–7: Findings, remediation, validation
  
- [x] KE-ADV-001-SUMMARY-CARD.md (quick reference, 4 KB)
  - Use cases, decision gates, Do's/Don'ts
  
- [x] This roadmap document

### Validation
- [x] 3 real projects analyzed (UTE 150MWp S9, ETE SABESP S8, BR-376 S1)
- [x] Score recalculated: 0.762 → 0.87 (target 0.85+ ✅)
- [x] Unique positioning: Operacional setorial (vs. Manta 15 financial)
- [x] Handoff boundary documented (explicit with Manta 15)

---

## PHASE 1: IMMEDIATE DEPLOYMENT (WEEK 1)

### Action 1.1: Repository Organization
**Objective:** Make KE-ADV-001 discoverable in Codex-exemplo

**Tasks:**
- [x] Create `/sharepoint/01-agentes-fundamentais/KE-ADV-001-decisao-setor-especifico.md` (done)
- [x] Create `/docs/AUDIT-KE-ADV-001-OVERLAP-RESOLUTION.md` (done)
- [x] Create `/docs/KE-ADV-001-SUMMARY-CARD.md` (done)
- [ ] Create `/docs/KE-ADV-001-IMPLEMENTATION-ROADMAP.md` (this file, done)
- [ ] Create index/README in `/sharepoint/01-agentes-fundamentais/` linking to KE
- [ ] Add KE-ADV-001 to `.claude/agents/README.md` (as reference resource)

**Timeline:** Day 1 (2026-07-19)  
**Owner:** CTO Arquitetura  
**Status:** 📋 Ready for merge

---

### Action 1.2: Stakeholder Alignment
**Objective:** Inform Manta 15 PM + Sector Agents (S1–S10) of KE-ADV-001 existence

**Communication:**
- [x] Draft audit report + summary card (done)
- [ ] Email Manta 15 PM: "KE-ADV-001 ready — handoff boundary in §6 of audit"
- [ ] Email Sector Agent owners (S1–S10): "KE-ADV-001 available — use in Estudo Prévio"
- [ ] Schedule 30-min kickoff meeting (overview of KE structure + use cases)

**Timeline:** Days 1–3 (2026-07-19 to 2026-07-21)  
**Owner:** CTO / KE owner  
**Status:** 📋 Waiting confirmation

---

### Action 1.3: Governance Approval
**Objective:** Get MN (Sócio) + CTO approval for KE registry v1

**Deliverables to present:**
1. KE-ADV-001 main document (15 KB, ready)
2. Audit report with 3 real case validations (ready)
3. Summary card + quick reference (ready)
4. Comparison matrix: vs. Manta 15 (clear differentiation)
5. Roadmap (this doc)

**Decision points:**
- Approve KE-ADV-001 v2.0 as official operacional framework?
- Approve score 0.87 (upgrade from 0.762)?
- Approve integration into agent SKILLs (Phase 2)?

**Timeline:** Days 3–5 (2026-07-21 to 2026-07-23)  
**Owner:** CTO + MN  
**Status:** 📋 Scheduled for review

---

## PHASE 2: DOCUMENTATION & INTEGRATION (WEEKS 2–4)

### Action 2.1: CLAUDE.md v4.3 Patch
**Objective:** Add KE-ADV-001 to master registry

**File:** `/home/user/Codex-exemplo/CLAUDE.md`  
**Change:**
```markdown
## KNOWLEDGE ELEMENTS (KEs) — Novo (v4.3)

| Código | Título | Escopo | Handoff | Versão |
|--------|--------|--------|---------|--------|
| **KE-ADV-001** | Matriz Go/No-Go por Setor (S1–S10) | Operacional; viabilidade técnica/risco | → Manta 15 se Yellow+ | 2.0 |

**Referência canônica:** `sharepoint/01-agentes-fundamentais/KE-ADV-001-decisao-setor-especifico.md`
```

**Timeline:** Day 7–10 (2026-07-26 to 2026-07-29)  
**Owner:** CTO Arquitetura  
**Review:** MN approval  
**Status:** 📋 Pending

---

### Action 2.2: Agent README Updates (S1–S10)
**Objective:** Cross-reference KE-ADV-001 in each sector agent

**Files to update:**
1. `.claude/agents/agente-saneamento.md` → add "KE-ADV-001 S8" reference
2. `.claude/agents/agente-energia.md` → add "KE-ADV-001 S9" reference
3. `.claude/agents/agente-barragens.md` → add "KE-ADV-001 S10" reference
4. `sharepoint/01-agentes-fundamentais/agente-saneamento/README.md` → add section "Matriz de Decisão"
5. `sharepoint/01-agentes-fundamentais/agente-energia/README.md` → add section "Gate de Viabilidade"
6. `sharepoint/01-agentes-fundamentais/agente-barragens/README.md` → add section "Análise de Risco"

**Sample update (saneamento):**
```markdown
## Matriz de Decisão (KE-ADV-001 S8)

Antes de emitir parecer técnico, aplique a matriz de viabilidade Go/No-Go:

- **Passo 1:** Preencha scorecard (1 página) com 5 critérios + Critério 6 (manancial + outorga ANA/ERAS)
- **Passo 2:** Calcule score médio (0–100%)
- **Passo 3:** Classifique: Go (80%+) | Yellow (60–79%) | No-Go (<60%)
- **Passo 4:** Se Yellow+, handoff para Manta 15 (modelo financeiro com risco técnico residual)

**Referência:** `KE-ADV-001-decisao-setor-especifico.md` seção "Extensões Setoriais (S8)"
```

**Timeline:** Days 10–15 (2026-07-29 to 2026-08-05)  
**Owner:** Sector Agent owners (S1–S10)  
**Review:** CTO  
**Status:** 📋 Pending

---

### Action 2.3: Manta 15 Handoff Documentation
**Objective:** Formalize handoff from KE-ADV-001 to Manta 15

**File:** New section in Manta 15 skill doc or advisory playbook  
**Content:**
```markdown
### Input from KE-ADV-001 (Operacional Setorial)

When a project completes KE-ADV-001 evaluation, Manta 15 receives:
- **KE-ADV-001_score** (0–100%): viability score
- **Decision:** Go | Yellow | No-Go
- **Risk residual:** (100 - score)
- **Sector-specific risks:** (detailed scorecard)

**Modeling rules:**
- **Go (80%+):** CAPEX contingency = 1%, no other adjustment
- **Yellow (60–79%):** CAPEX contingency = 5–10% (based on risk residual), OPEX +3–5%
- **No-Go:** Do not model (project not ready)

**Example (ETE SABESP):**
```
Input: KE-ADV-001_score = 64%, risk_residual = 36% (interface urbana)
→ CAPEX +8%, OPEX +3%, TIR sensitivity -1.2 pp (6m delay scenario)
Output: VPL model with risk-adjusted assumptions
```
```

**Timeline:** Days 14–18 (2026-08-05 to 2026-08-09)  
**Owner:** Manta 15 PM  
**Review:** CTO + Manta 15 leadership  
**Status:** 📋 Pending

---

### Action 2.4: Create SOP (Standard Operating Procedure)
**Objective:** Operationalize KE-ADV-001 usage across Manta

**File:** `sharepoint/01-agentes-fundamentais/KE-ADV-001-SOP.md`  
**Sections:**
1. When to apply (timing: always Estudo Prévio)
2. Who applies it (PM, lead engineer, sector agent)
3. How to fill scorecard (template + rubric)
4. Decision logic (Go/Yellow/No-Go thresholds)
5. Handoff to Manta 15 (what to pass, when to pass)
6. Approval workflow (signatures)
7. Monitoring (revisit each phase)
8. Escalation (when No-Go or risco crítico)

**Timeline:** Days 18–22 (2026-08-09 to 2026-08-13)  
**Owner:** CTO / KE owner  
**Status:** 📋 Pending

---

### Action 2.5: Create Templates & Forms
**Objective:** Make KE-ADV-001 easy to use in practice

**Deliverables:**
1. Excel scorecard template (interactive, auto-calculates score)
2. Markdown scorecard template (for documentation)
3. Risk register template (for Yellow projects)
4. Handoff form to Manta 15 (captures KE-ADV-001 → M15 handoff)

**Timeline:** Days 22–26 (2026-08-13 to 2026-08-17)  
**Owner:** CTO / Operations  
**Status:** 📋 Pending

---

## PHASE 3: TRAINING & ROLLOUT (WEEKS 5–6)

### Action 3.1: Brown Bag Training Session
**Objective:** Train Manta team (sector agents, PMs, leadership) on KE-ADV-001

**Agenda (90 min):**
- Intro: What is KE-ADV-001? Why unique? (15 min)
- Deep dive: 5×5 matrix + Critério 6 per sector (30 min)
- Case studies: UTE, ETE, BR-376 (walk through scores) (20 min)
- Handoff: When/how to pass to Manta 15 (15 min)
- Q&A + next steps (10 min)

**Audience:**
- All sector agents (S1–S10)
- PMs (lead engineers)
- Manta 15 PM (advisory)
- CTO + MN (leadership)

**Timeline:** Week 5 (2026-08-26 to 2026-08-30)  
**Owner:** CTO / KE owner  
**Platform:** Zoom + recording archived  
**Status:** 📋 Pending scheduling

---

### Action 3.2: Pilot on New Projects
**Objective:** Validate KE-ADV-001 on ≥2 new projects (real deployment)

**Selection criteria:**
- 1 project from S1–S4 (existing sectors)
- 1 project from S6–S10 (new sectors, validate extensions)
- Both in Estudo Prévio phase (ready for KE application)

**Deliverables per project:**
- Scorecard (completed)
- Justifications (1 page per criterion)
- Decision (Go/Yellow/No-Go + gate approval)
- Handoff to Manta 15 (if Yellow+)
- Feedback form (what worked, what needs refinement)

**Timeline:** Weeks 5–8 (2026-08-26 to 2026-09-16)  
**Owner:** Pilot project PMs  
**Support:** CTO (coaching)  
**Status:** 📋 Pending project assignment

---

### Action 3.3: Feedback Loop & Refinement
**Objective:** Collect lessons learned; refine KE-ADV-001 v2.1 if needed

**Feedback capture:**
- Pilot PM survey (10 questions)
- Sector agent feedback (each S1–S10)
- Manta 15 feedback (on handoff effectiveness)
- CTO retrospective (deployment experience)

**Decision points (based on feedback):**
- Clarify any matrix criteria?
- Adjust Critério 6 per sector?
- Refine decision thresholds (e.g., Yellow 60–79% → 65–78%)?
- Add new criterion (e.g., safety, sustainability)?

**Timeline:** Week 8 (2026-09-16 to 2026-09-23)  
**Owner:** CTO + KE owner  
**Output:** Refinement notes (if any) for v2.1 (Q4 2026)  
**Status:** 📋 Pending

---

## PHASE 4: ONGOING MONITORING (Q4 2026 onwards)

### Action 4.1: Score Validation (Quarterly)
**Objective:** Verify KE-ADV-001 score predicts project outcomes

**Metric:** Correlation (r²) between KE-ADV-001 score and actual atraso/sucesso  
**Target:** r² ≥ 0.65 (score predicts real risk)

**Data points collected:**
- Project: name, sector, KE-ADV-001 score
- Actual outcome: on-time | atraso (m) | cancelado
- Atraso vs. score class:
  - Go projects: mean atraso ≤ 1 month
  - Yellow projects: mean atraso 2–6 months
  - No-Go projects: N/A (canceled)

**Reporting:** Quarterly to MN (chart + analysis)  
**Timeline:** Every Q (starting Q4 2026)  
**Owner:** CTO / Operations  
**Status:** 📋 To be scheduled

---

### Action 4.2: Case Library (Ongoing)
**Objective:** Build repository of KE-ADV-001 scores + real outcomes (learning)

**Entries to document:**
- Project name, sector, phase, date
- KE-ADV-001 score + decision (Go/Yellow/No-Go)
- Actual outcomes: timeline, budget, risks realized
- Lessons learned (what worked, what changed)

**Timeline:** Every project (mandatory documentation)  
**Owner:** Project PM (with CTO oversight)  
**Storage:** SharePoint or centralized database  
**Status:** 📋 To establish

---

### Action 4.3: Annual Refinement (Q4 2026+)
**Objective:** Update KE-ADV-001 based on annual learnings

**Candidates for v2.1 / v3.0:**
- Refine matrix thresholds (if validation shows drift)
- Add Critério 7+ per sector (if new risks emerge)
- Expand case library (documentation of new projects)
- Incorporate feedback from sector agents + Manta 15

**Timeline:** Q4 2026 (first annual review)  
**Owner:** CTO + KE owner  
**Approval:** MN  
**Status:** 📋 To be scheduled

---

## PHASE 5: INTEGRATION WITH OTHER KEs (Future)

### Planned Companion KEs
- **KE-RIS-001** (Risk Management Framework) — standardize risk scoring across KE-ADV-001 + others
- **KE-ENV-001** (Environmental & Social Risk) — enhance KE-ADV-001 Interfaces Urbanas criterion
- **KE-CLM-001** (Climate Resilience) — new criterion for S1–S10 (post-2026)

**Timeline:** 2027+ (exploratory)  
**Status:** 📋 Future planning

---

## SUCCESS CRITERIA

### Phase 1 (Immediate) ✅
- [x] KE-ADV-001 v2.0 document published
- [x] Audit report completed (overlap resolved, score 0.87 ✅)
- [x] 3 real cases validated
- [ ] Governance approval (pending)
- [ ] Stakeholder communication (pending)

### Phase 2 (Documentation)
- [ ] CLAUDE.md v4.3 merged
- [ ] Agent README files updated (S1–S10)
- [ ] Manta 15 handoff formalized
- [ ] SOP document created
- [ ] Templates ready for use

### Phase 3 (Training & Rollout)
- [ ] Brown bag conducted (≥80% attendance)
- [ ] ≥2 pilot projects completed with feedback
- [ ] Feedback analyzed; v2.1 refinements identified (if any)
- [ ] Sector agents trained on Critério 6 per sector

### Phase 4 (Ongoing)
- [ ] Score validation shows r² ≥ 0.65 (Q4 2026)
- [ ] ≥10 projects documented in case library (by year-end 2026)
- [ ] Quarterly reports to MN (score accuracy trend)
- [ ] v2.1 released (Q4 2026 or Q1 2027)

---

## RISKS & MITIGATION

### Risk 1: Low adoption (agents/PMs don't use KE-ADV-001)
**Mitigation:**
- Make it mandatory in Estudo Prévio (SOP requirement)
- Provide templates + training (reduce friction)
- Tie to gate approval (no gate without KE score)

**Owner:** CTO  
**Timeline:** Phase 2–3 (make it a process gate)

---

### Risk 2: Score doesn't correlate with outcomes
**Mitigation:**
- Monitor r² quarterly; if drift detected, refine thresholds
- Collect feedback from projects (why score mismatched outcome?)
- Adjust Critério 6 per sector based on learnings

**Owner:** CTO + Operations  
**Timeline:** Phase 4 (ongoing validation)

---

### Risk 3: Confusion with Manta 15 persists
**Mitigation:**
- Repeat handoff documentation (§6 in main KE, new SOP section)
- Train Manta 15 PM explicitly on input/output boundary
- Include comparison matrix in training materials

**Owner:** CTO + Manta 15 PM  
**Timeline:** Phase 2–3 (training focus)

---

### Risk 4: Sector-specific criteria (Critério 6) incomplete or wrong
**Mitigation:**
- Gather feedback from pilot projects (Phase 3)
- Refine Critério 6 per sector in v2.1
- Add examples/rubric for each sector in training

**Owner:** Sector agent owners  
**Timeline:** Phase 3–4 (ongoing refinement)

---

## DELIVERABLES CHECKLIST

### Created (Phase 0 — DONE ✅)
- [x] KE-ADV-001-decisao-setor-especifico.md
- [x] AUDIT-KE-ADV-001-OVERLAP-RESOLUTION.md
- [x] KE-ADV-001-SUMMARY-CARD.md
- [x] KE-ADV-001-IMPLEMENTATION-ROADMAP.md (this doc)

### To Create (Phase 1–3)
- [ ] CLAUDE.md v4.3 (with KE registry)
- [ ] Agent README patches (S1–S10)
- [ ] KE-ADV-001-SOP.md (standard operating procedure)
- [ ] Excel scorecard template
- [ ] Markdown scorecard template
- [ ] Handoff form (KE → Manta 15)
- [ ] Training slides (brown bag)
- [ ] Case study documentation (UTE, ETE, BR-376)

### To Monitor (Phase 4+)
- [ ] Quarterly score validation report
- [ ] Annual refinement notes (v2.1 candidate)
- [ ] Case library entries (per project)

---

## CONTACTS & OWNERSHIP

| Role | Name | Contact | Responsibility |
|------|------|---------|-----------------|
| KE Owner | CTO Arquitetura | (internal) | Overall KE governance + phases 1–4 |
| Manta 15 PM | Advisory PM | (internal) | Handoff formalization (phase 2) |
| Sector Agents | S1–S10 owners | (internal) | README updates + pilot feedback (phases 2–3) |
| Governance | MN (Sócio) | (internal) | Final approval (phase 1) |
| Operations | Ops team | (internal) | SOP + templates + monitoring (phases 2–4) |

---

## TIMELINE SUMMARY

| Phase | Week | Start | End | Key Deliverables |
|-------|------|-------|-----|------------------|
| **0** | Remediation | 2026-07-19 | 2026-07-19 | 4 docs ✅ |
| **1** | Immediate | Week 1 | 2026-07-23 | Approval + comm |
| **2** | Docs & Integ | Weeks 2–4 | 2026-08-17 | CLAUDE.md, README, SOP, templates |
| **3** | Training & Pilot | Weeks 5–8 | 2026-09-23 | Brown bag + 2 pilot projects |
| **4** | Monitoring | Q4 2026+ | Ongoing | Quarterly validation + annual refinement |

---

## FINAL NOTES

- **Start date:** 2026-07-19 (remediation complete; awaiting phase 1 approval)
- **Critical path:** Governance approval → CLAUDE.md patch → agent README updates → SOP
- **Team size:** 4–6 FTEs (CTO, Manta 15 PM, sector agents, ops)
- **Budget impact:** Low (mostly documentation + training; no infrastructure)
- **Success rate forecast:** High (3 real cases validated; clear differentiation from Manta 15)

**Next action:** Share this roadmap + audit report with MN for phase 1 approval (EOD 2026-07-22).

---

**Document prepared by:** Claude Code (Subagent)  
**Date:** 2026-07-19  
**Classification:** Manta Associados — Internal  
**Version:** 1.0 (roadmap v1)
