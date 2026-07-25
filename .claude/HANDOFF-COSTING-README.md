# Jericó Seismic-Resilient Redesign: Costing Specification Handoff

**For: Agente-05 (Orcamento)**  
**From: Infraestrutura Design Team (D6-D7 Deliverables)**  
**Date: July 25, 2026**  
**Status: Ready for Agente-05 Intake and Budget Baseline Approval**

---

## Overview

This package contains a complete costing specification for the Jericó seismic-resilient road redesign project, prepared by the Infrastructure Design Team (Geotechnical + Pavement Engineering) at the conclusion of Sprint 2-3 deliverables D6 (Geotechnical Design Basis) and D7 (Seismic-Resilient Pavement Strategy).

**Total Project Budget: BRL 35,800,000**  
**Duration: 22 months (3 design + 4 procurement + 15 execution)**  
**Risk Level: Medium-High (liquefaction index 0.48; seismic design mandatory)**

---

## File Structure

```
handoff-costing-specification-d6d7.json
├── metadata                          → Project identification, SICRO edition, classification
├── executive_summary                 → Budget overview, payment schedule, risk profile
├── sicro_rate_mapping               → 7 line items (piles, drainage, geotextile, slope, earthwork, CBUQ, base)
├── regional_multipliers             → MG 1.08x factor; labor 1.12x; equipment 1.06x
├── seismic_cost_adders              → 8-12% across components; 10.71% project-wide
├── contingency_guidelines           → 15% standard (5.24M); triggers for 20% if LI > 0.5
├── payment_schedule                 → Design (5%), Procurement (20%), Execution (75%)
├── budget_tracking_metrics          → EVM framework: PV, EV, AC, CPI, SPI, EAC
├── cost_control_procedures          → Change order workflow, contingency authorization levels
└── test_cases_and_cost_scenarios    → 10 detailed scenarios (±15% cost range)
```

---

## Key Numbers at a Glance

| Category | Amount (BRL) | % of Total |
|----------|--------------|-----------|
| **Geotechnical** | 25,820,000 | 72.2% |
| — Micro-piles (2,150 m @ 8,400/m) | 18,060,000 | 50.4% |
| — Deep drainage (450 m @ 9,200/m) | 4,140,000 | 11.6% |
| — Geotextile (35,000 m² @ 45/m²) | 1,575,000 | 4.4% |
| — Slope stabilization (2.4 km @ 850k/km) | 2,040,000 | 5.7% |
| **Pavement** | 9,980,000 | 27.9% |
| — Earthwork (22,100 m³ @ 125/m³) | 2,762,500 | 7.7% |
| — Elastic CBUQ (28,000 m² @ 285/m²) | 8,000,000 | 22.3% |
| — Base course (8,900 m³ @ 95/m³) | 845,500 | 2.4% |
| — (includes 15% seismic adder) | — | —  |
| **Contingency (15%)** | 5,240,000 | 14.6% |
| **Total Project** | **35,800,000** | **100%** |

---

## SICRO Rate Mapping (December 2024 Edition)

All unit rates sourced from **DNIT Banco de Preços** (December 1, 2024):

### Geotechnical Items

| Item | Code | Unit | Rate (Dec 2024) | Quantity | Total | Seismic Modifier |
|------|------|------|-----------------|----------|-------|------------------|
| Micro-pile drilling (150mm, 45° incline) | GEO-001-MP | m | 8,400 | 2,150 | 18.06M | 1.10x |
| Deep drainage (PVC + geotextile layer) | GEO-002-DD | m | 9,200 | 450 | 4.14M | 1.08x |
| Geotextile reinforcement (non-woven, 150 gsm) | GEO-003-GT | m² | 45 | 35,000 | 1.58M | 1.12x |
| Slope stabilization (micro-piles + shotcrete + anchors) | GEO-004-SS | km | 850,000 | 2.4 | 2.04M | 1.15x |

### Pavement Items

| Item | Code | Unit | Rate (Dec 2024) | Quantity | Total | Seismic Modifier |
|------|------|------|-----------------|----------|-------|------------------|
| Earthwork & compaction (95% Proctor) | PAV-001-EW | m³ | 125 | 22,100 | 2.76M | 1.05x |
| Elastic CBUQ, 50mm layer (SBS binder + interlayer) | PAV-002-CBUQ | m² | 285 | 28,000 | 8.00M | 1.15x |
| Base course, crushed stone (BGS cert.) | PAV-003-BC | m³ | 95 | 8,900 | 0.85M | 1.08x |

**Note:** All rates include labor, materials, equipment, and 8-9% overhead. Monthly inflation adjustments applied via IGP-M index.

---

## Regional Cost Multipliers (Minas Gerais)

**Location:** Jericó (Serra da Mantiqueira region, 1,420m elevation, 180 km from Belo Horizonte)

### Composite Multiplier Breakdown

| Factor | Base | Adjustment | Result |
|--------|------|-----------|--------|
| Location (remoteness + terrain) | 1.00 | +4-2% | 1.04x |
| Infrastructure access | 1.00 | +2% | 1.02x |
| **Cumulative location multiplier** | — | — | **1.08x** |
| Labor (skill scarcity: geotechnical) | 1.00 | +12-15% | 1.12x-1.15x |
| Equipment rental (mobilization from BH) | 1.00 | +6% | 1.06x |
| **All-in regional multiplier** (location + labor) | — | — | **1.285x** |

**Interpretation:** Use the **1.08x location multiplier** for SICRO-based estimates. Labor costs automatically reflected in SICRO composition (already include regional rates). Equipment adds 6% to rental costs.

---

## Seismic Cost Adders (8-12% per component)

The Jericó project sits in a **moderate seismic hazard zone** (PGA = 0.15g at 475-year return period) with **HIGH liquefaction risk** (LI = 0.48, exceeds 0.40 threshold). Seismic design enhancements are **mandatory** per NBR 15953.

### Component-Level Adders

| Component | Base Cost | Enhancement | Adder % | Adder Amount | Total w/ Seismic |
|-----------|-----------|-------------|---------|--------------|------------------|
| Micro-piles | 18.06M | Inclined (45°) + enhanced reinforcement | 10% | 1.81M | 19.87M |
| Drainage | 4.14M | Dual-layer + seismic-rated connections | 8% | 0.33M | 4.47M |
| Geotextile | 1.58M | Seismic-grade + wider overlap (1.5m) | 12% | 0.19M | 1.77M |
| Slope stabilization | 2.04M | Dynamic anchor arrays | 15% | 0.31M | 2.35M |
| Elastic CBUQ pavement | 8.00M | SBS binder + interlayer mesh | 15% | 1.20M | 9.20M |
| **Cumulative** | **33.82M** | — | **10.71%** | **3.84M** | **37.66M** |

**Note:** Seismic adders cumulate to **10.71% project-wide**, within the 8-12% guideline for moderate-hazard zones. LI > 0.4 triggers additional 5-8% for enhanced geotechnical items (already included).

---

## Contingency Policy (15% Standard)

**Contingency Reserve: BRL 5,240,000 (15% of base 35.04M)**

### Allocation Rules

| Condition | Recommended Contingency | Jericó Status |
|-----------|------------------------|---------------|
| Design phase with limited site investigation | 20-25% | N/A (full investigation complete) |
| Design phase with detailed investigation | 15-18% | **APPLIED: 15%** |
| LI > 0.50 (very high liquefaction risk) | 20% | LI = 0.48 (below threshold) |
| LI 0.30–0.50 (moderate-high risk) | 15% | **APPLIED (LI = 0.48)** |
| Execution phase, 50%+ complete | 5-10% | Reduces over time |

### Contingency Release Schedule

Contingency held in reserve; released upon achievement of milestones:

| Milestone | Month | Amount Released | Cumulative Released | Remaining |
|-----------|-------|-----------------|---------------------|-----------|
| Initial reserve | 0 | — | — | 5.24M |
| Design phase complete (PE signed) | 3 | 0.80M | 0.80M | 4.44M |
| Procurement complete (all materials in warehouse) | 7 | 1.20M | 2.00M | 3.24M |
| Execution 50% complete | 15 | 1.50M | 3.50M | 1.74M |
| Execution 90% complete | 21 | 1.74M | 5.24M | 0 |

**Contingency Burn-Rate Tracking:** Monthly EVM report tracks cumulative contingency use. Alert trigger if burn > 50% before month 16.

---

## Payment Schedule (22 Months)

**Total Contract Value: BRL 35,800,000**

### Phase Breakdown

| Phase | Duration | Scheduled Cost | % of Total | Payment Terms |
|-------|----------|-----------------|-----------|----------------|
| **Design** | 3 months | 1.20M | 3.35% | 50% advance (day 1) + 50% upon PE completion |
| **Procurement** | 4 months | 2.80M | 7.82% | 50% order placement + 50% upon delivery + QA |
| **Execution** | 15 months | 31.80M | 88.83% | Monthly progress; 2% retention until +12 months post-completion |
| **Total** | **22 months** | **35.80M** | **100%** | — |

### Monthly Cash Flow (Execution Phase, Representative)

Execution is the long pole in the tent:

- **Months 8–12:** Mobilization & geotechnical prep (6–20% progress)
  - Monthly invoices: 0.64M–2.23M
- **Months 13–15:** Main earthwork & pavement (45–80% progress)
  - Monthly invoices: 4.77M (peak)
- **Months 16–22:** Finishes & closeout (95–100% progress)
  - Monthly invoices: 1.59M–1.75M

**Retention (2% hold):** 0.636M held per invoice; released 12 months after project completion + zero defects certified.

---

## Budget Tracking Metrics (Earned Value Management)

### Framework: PMBOK 6th Edition (Adapted for Construction)

**Key Metrics:**

| Metric | Formula | Target | Interpretation |
|--------|---------|--------|-----------------|
| **Planned Value (PV)** | Cumulative scheduled amount to date | Baseline | "What we planned to spend by now" |
| **Earned Value (EV)** | PV × (% actual progress / % planned progress) | ≥ PV | "What we've actually earned by now" |
| **Actual Cost (AC)** | Sum of invoices paid + retention held | ≤ EV | "What we've actually spent" |
| **Schedule Variance (SV)** | EV − PV | ≥ 0 | >0 = ahead; <0 = behind |
| **Cost Variance (CV)** | EV − AC | ≥ 0 | >0 = under budget; <0 = over budget |
| **Cost Performance Index (CPI)** | EV / AC | ≥ 0.98 | <0.98 triggers cost control review |
| **Schedule Performance Index (SPI)** | EV / PV | ≥ 0.95 | <0.95 triggers schedule recovery plan |
| **Estimate at Completion (EAC)** | BAC / CPI | ≤ BAC | Projected final cost if trend continues |
| **Variance at Completion (VAC)** | BAC − EAC | ≥ 0 | Projected final cost variance |

### Variance Thresholds & Escalation

| Metric | Threshold | Trigger Action |
|--------|-----------|----------------|
| **Cost Variance (CV)** | < −1.79M (−5%) | Cost control review + change order process |
| **Schedule Variance (SV)** | < −1.75M (−5%) | Schedule recovery plan + resource reallocation |
| **Budget at Completion (EAC > BAC + 3%)** | > 36.87M | Escalate to Agente-05 for contingency approval |
| **Contingency Burn Rate** | > 50% before month 16 | Contingency release review + cost rebaseline |

### Monthly Reporting

Agente-05 issues **monthly cost report** (1st Tuesday of each month):
- Cumulative PV, EV, AC
- CPI, SPI trends
- EAC update
- Contingency balance and burn rate
- Variance analysis (cost + schedule)
- Change order log (pending + approved)

---

## Cost Control Procedures

### Change Order Process (COR Workflow)

**Trigger:** Scope change, unforeseen field condition, or design revision approved by engineering.

**Workflow:**
1. **Submission** (T+5 days): Contractor submits Change Order Request (COR) with cost + schedule impact
2. **Technical Review** (T+5 days): Design/Engineering agent verifies scope feasibility
3. **Cost Review** (T+5 days): Agente-05 validates cost against SICRO or market quotes
4. **Risk Review** (if CO > 2.5% of contingency): Escalate to Agente-15 (Advisory) for seismic/geotechnical impact
5. **Approval** (T+10 days): PM approves if CO < 5% of contingency (2.62M); else escalate to Owner
6. **Issuance**: CO issued in writing; contractor notified within 10 business days

**Markup Rules:**
- Standard CO (fixed price): 8% overhead + 5% profit = 13% total markup
- T&M CO (< 500k only): Labor @ base rate + 35% | Materials @ invoice + 15% | Equipment @ rental + 20%

**Authorization Limits:**
- **Level 1 (Site Engineer):** <100k (minor field conditions)
- **Level 2 (PM):** 100k–500k (subsurface/material issues)
- **Level 3 (Agente-05):** 500k–2.5M (formal cost control + baseline rebaseline)
- **Level 4 (Escalation):** >2.5M or cumulative >10% of base contract

---

## Test Cases & Cost Scenarios (10 + Sensitivity)

This specification includes **10 detailed test cases** covering:

1. **Balanced (Recommended)** — Primary baseline; 35.8M
2. **Conservative (Maximum Resilience)** — Full seismic + redundancy; 41.3M (+15.3%)
3. **Optimized (Value Engineering)** — Minimal seismic; 30.8M (−14.0%, NOT RECOMMENDED)
4. **Material Cost Surge** — +15% binder/geotextile; 36.9M (+3.0%)
5. **Labor Cost Escalation** — +18% geotechnical labor; 37.3M (+4.1%)
6. **Deeper Liquefaction Discovery** — LI → 0.62; 39.4M (+9.9%)
7. **Execution Productivity Loss** — 20% weather delay; 36.4M (+1.6%)
8. **Seismic Design Update** — PGA 0.15g → 0.18g; 37.0M (+3.5%)
9. **Regional Multiplier Sensitivity** — MG ±2%; 35.1M–36.5M (±2.1%)
10. **Cash Flow & Financing** — NPV analysis at 8.5% cost of capital; 35.3M (present value)

**Cost Range:** BRL 30.8M (optimistic, not recommended) to BRL 41.3M (conservative, over-designed)  
**Recommended Range:** BRL 35.0M–37.5M (85–95% confidence band)

---

## Handoff Checklist for Agente-05

- [ ] Validate all SICRO rates against latest DNIT Banco de Preços (December 2024)
- [ ] Confirm regional multipliers (1.08x MG) with market surveys (obtain 3 quotes per line item)
- [ ] Establish cost baseline freeze policy: Design PE completion (Oct 2026) = design cost lock
- [ ] Lock material prices (elastic binder, geotextile, PVC pipe) by end of month 2 (Sept 2026)
- [ ] Set up contingency reserve tracking dashboard (monthly burn rate + release authorization)
- [ ] Configure EVM system (PV, EV, AC, CPI, SPI, EAC) in project management tool
- [ ] Prepare change order templates and authorization workflow documentation
- [ ] Coordinate with Finance for payment processing (15-day SLA target)
- [ ] Schedule monthly cost reviews (1st Tuesday of each month, 60 minutes)
- [ ] Prepare contingency release criteria memo for Owner signature

---

## Critical Risk Factors (Agente-05 Monitoring Required)

1. **Material supply chain** (elastomeric binder: global commodity risk; only 2 suppliers in MG)
2. **Geotechnical labor availability** (skill scarcity in micro-pile installation; recommend early contractor engagement)
3. **Seismic design parameter update** (USGS/CPRM may revise PGA; risk of +3% cost adder)
4. **Weather impact on execution** (June–August monsoon season; risk of 20% productivity loss)
5. **Regional inflation** (IGP-M indexing may exceed 3% quarterly; monitor IPCA/INPC)
6. **Liquefaction investigation findings** (additional borings may reveal LI > 0.55; triggers 20% contingency)

**Monthly Escalation Reviews:** Agente-05 to flag any of above during cost report (1st Tuesday).

---

## Integration with Manta Architecture

This handoff document is compatible with:

- **Agente-05 (Orcamento)** — Budget baseline, payment schedule, contingency management
- **Agente-15 (Advisory)** — Risk review for COs > 2.5M or cost variance > 5%
- **Maestro (Manta-00)** — Escalation routing for multi-agent cost control decisions
- **Manta-03-S2 (Infraestrutura, Geotechnical)** — Design change coordination, seismic adder updates
- **Agente-07 (Cronograma)** — Schedule-cost integration; payment schedule alignment

---

## References

- **SICRO December 2024 Edition** (DNIT Banco de Preços)
- **NBR 15953** — Seismic Design for Roadways and Structures
- **Jericó Geotechnical Investigation Report** (v2, July 2026)
- **Jericó Projeto Executivo** (planned October 2026)
- **PMBOK 6th Edition** — Earned Value Management framework
- **IGP-M Index** — Monthly inflation adjustment schedule

---

## Questions or Clarifications?

Contact the **Infraestrutura Design Team (D6-D7 Lead)** or **Maestro (routing agent)** for:
- SICRO rate questions or market validation
- Seismic design parameter updates
- Geotechnical site investigation findings
- Changes to scope or design assumptions

**Prepared by:** Infraestrutura Design Team  
**Date:** July 25, 2026  
**Next Review:** October 1, 2026 (upon PE completion and cost baseline freeze)
