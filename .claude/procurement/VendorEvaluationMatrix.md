# Vendor Evaluation Matrix — Manta-24-Procurement

**Version:** 1.0.0  
**Date:** 2026-08-02  
**Purpose:** Comprehensive framework for scoring, ranking, and selecting suppliers based on multi-criteria decision analysis.

---

## 1. Evaluation Methodology

### 1.1 Scoring Model Overview

```
Final Score (100 points) = 
    Quality (40 points)
  + Cost (30 points)
  + Delivery (20 points)
  + Risk (10 points)
```

**Selection Rule:**
- Highest total score → RECOMMENDED supplier
- If tied: Apply price tiebreaker (lowest price wins)
- If still tied: Evaluate delivery flexibility (shortest lead time)

---

## 2. Detailed Scoring Dimensions

### 2.1 QUALITY DIMENSION (40 points total)

#### A. Certifications (10 points max)

| Certification | Weight | Points | Criteria |
|---|---|---|---|
| **INMETRO** | 4 pts | 4 | Current, valid, scope covers commodity |
| **ISO 9001:2015** | 3 pts | 3 | Current (dated ≤2024), manufacturer |
| **ISO 45001 / OHSAS 18001** | 2 pts | 2 | Workplace safety; demonstrates risk culture |
| **ABNT Standards** (commodity-specific) | 1 pt | 1 | e.g., ABNT NBR 8850 for towers; NBR 12211 for pipes |

**Scoring Rules:**
- All 4 certifications = 10 points
- 3 of 4 = 7 points
- 2 of 4 = 5 points
- 1 of 4 = 2 points
- 0 of 4 = 0 points (may auto-reject if INMETRO required)

---

#### B. Warranty Period (8 points max)

| Quoted Warranty | Points | Notes |
|---|---|---|
| ≥24 months parts + labor | 8 | Excellent confidence in product durability |
| 18 months parts + labor | 6 | Good standard |
| 12 months parts + labor | 4 | Acceptable baseline |
| <12 months | 1 | Risk flag; questionable quality confidence |

---

#### C. Defect Rate / Quality History (12 points max)

**Input:** Historical data from references or Serasa credit report

| Defect Rate | On-Time Delivery | Points | Notes |
|---|---|---|---|
| 0–2% defects | ≥95% | 12 | Excellent quality + reliability |
| 2–5% defects | 90–95% | 10 | Good quality, minor delays acceptable |
| 5–10% defects | 80–90% | 6 | Moderate; production variability |
| >10% defects | <80% | 2 | Poor quality; high rework risk |

**Data Collection:**
- Ask vendor: "3 similar projects in past 3 years — defect rate by project"
- Cross-reference with client references (phone call)
- Query supplier database (if repeat vendor): historical performance

---

#### D. References Strength (10 points max)

| # Similar Projects | Recency | Points | Scoring |
|---|---|---|---|
| ≥3 projects | Last 3 years | 10 | Strong track record |
| 2 projects | Last 3 years | 7 | Acceptable experience |
| 1 project | Last 3 years | 4 | Limited but confirmed |
| 0 projects | N/A | 0 | No reference; high risk |

**Quality of Reference:**
- Tier-1 client (Fortune 500, major contractor): +2 bonus points
- Government/BNDES project: +1 bonus point
- Negative reference (complaints, disputes): –5 points (may auto-reject)

---

### 2.2 COST DIMENSION (30 points total)

#### Price Benchmarking

**Step 1: Calculate Benchmark Price**

1. Collect all compliant quotes (Phase 1 pass)
2. Remove outliers (Q1, Q3 quartiles; discard ≤Q1–1.5×IQR or ≥Q3+1.5×IQR)
3. **Benchmark = median of remaining quotes**

**Example:**
```
Quotes: R$24,000, R$25,500, R$26,200, R$27,000, R$35,000 (outlier)
Median: R$25,850 (benchmark)
```

#### Price Scoring Formula

```
Price Score = 30 × (1 - |Quoted Price - Benchmark| / Benchmark)

Capped at 30 (no negative scores)
```

**Practical Scoring Table:**

| Quote vs. Benchmark | Score |
|---|---|
| Same as benchmark | 30 |
| +5% above | 28 |
| +10% above | 27 |
| +15% above | 25 |
| +20% above | 24 |
| +30% above | 21 |
| +50% above | 15 |
| +100% above (2×) | 0 |
| Below benchmark | 30 (tied win) |

**Scoring Rules:**
- Lowest price = 30 points (ties allowed)
- Price beyond +100% of benchmark = 0 points (likely rejected earlier for cost reasonableness)
- Include all costs: unit price + freight + insurance + taxes

---

#### Currency Handling

- **Quote in BRL:** Use as-is
- **Quote in USD:** Convert at Central Bank rate (date of quote); note in scorecard
- **Escalation clause:** If quote includes escalation >5 years, add cost of indexing to total

---

### 2.3 DELIVERY DIMENSION (20 points total)

#### A. Lead Time (12 points max)

**Step 1: Set Baseline**
- Project critical path: E.g., "LT tower delivery required by 2027-02-28"
- Safety buffer: Default 30 days before critical date
- **Baseline deadline = 2027-01-29**

**Step 2: Score Quoted Lead Times**

| Quoted Delivery | Points | Notes |
|---|---|---|
| On or before baseline | 12 | Excellent; meets critical path |
| 1–10 days late | 10 | Acceptable; minor buffer remains |
| 11–20 days late | 7 | Tight; reduced contingency |
| 21–40 days late | 4 | Risky; may impact downstream tasks |
| >40 days late | 0 | Unacceptable; breaks critical path |

---

#### B. Milestone Delivery (5 points max)

Does vendor offer phased delivery (e.g., 50% on date X, 50% on date Y)?

| Phased Schedule | Points | Notes |
|---|---|---|
| 3+ milestones (customized to project) | 5 | Excellent flexibility; de-risks project schedule |
| 2 milestones (default 50/50 split) | 3 | Standard; manageable inventory |
| Single delivery (all at once) | 1 | Inflexible; storage/installation pressure |

---

#### C. On-Time Delivery History (3 points max)

**Historical Performance:**

| OTD % from References | Points |
|---|---|
| ≥95% | 3 |
| 85–95% | 2 |
| <85% | 0 |

---

### 2.4 RISK DIMENSION (10 points total)

#### A. Geographic Risk (–3 max deduction)

| Supply Concentration | Deduction | Mitigation |
|---|---|---|
| 100% production in one state | –3 | Flag high; diversify suppliers |
| 75–99% in one region (e.g., São Paulo + Paraná) | –2 | Acceptable with backup supplier |
| <75% (multi-region or multi-country) | 0 | Low risk |

**Risk Scenario:** 2025 Paraná floods → 2 tower suppliers unable to deliver 60 days

---

#### B. Vendor Financial Health (–2 max deduction)

**Input:** Serasa/SPC credit check, balance sheet review

| Financial Score | Deduction | Notes |
|---|---|---|
| Serasa score ≥75 (excellent) | 0 | Low credit risk |
| Serasa score 50–75 (fair) | –1 | Monitor payment default risk |
| Serasa score <50 (poor) | –2 | High credit risk; require prepayment or letter of credit |

**Red Flags:**
- Negative equity (liabilities > assets)
- Revenue decline >30% YoY
- Pending lawsuits (pesquisar ORCA)

---

#### C. Supply Chain Concentration (–2 max deduction)

| Risk Type | Deduction |
|---|---|
| Single-source raw material (e.g., only 1 steel mill supplier) | –2 |
| Dependent on single subcontractor | –1 |
| Multiple suppliers, low switching cost | 0 |

---

#### D. Lead Time Buffer (–3 max deduction)

Does vendor quote include contingency for delays?

| Buffering | Deduction | Example |
|---|---|---|
| Quote includes 30+ days cushion above baseline | 0 | Quote 2027-02-28, baseline 2027-01-29 → +30 day buffer |
| Quote = baseline (no buffer) | –2 | Tight; one disruption = miss project |
| Quote < baseline | –3 | Auto-reject for critical path projects |

---

## 3. Master Vendor Scorecard (Example)

```
═════════════════════════════════════════════════════════════════════════════
RFQ-2026-08-LT345-TOWERS-001 — VENDOR EVALUATION RESULTS
═════════════════════════════════════════════════════════════════════════════

Evaluation Date: 2026-08-20
Evaluated By: Maria da Silva (Procurement Officer)
Total Compliant Quotes: 5
Benchmark Price: R$ 25,850/unit

─────────────────────────────────────────────────────────────────────────────
RANK 1: ESTRUTURAS METÁLICAS NORDESTE LTDA. (EMN)
─────────────────────────────────────────────────────────────────────────────

Company Profile:
  CNPJ: 12.345.678/0001-90
  Founded: 2008
  Employees: 150
  Locations: Recife (HQ), São Paulo (plant), Brasília (office)
  Serasa Score: 82 (Good)

QUALITY DIMENSION (40 points)
  Certifications (10):
    ✓ INMETRO structural steel                           +4 pts
    ✓ ISO 9001:2015 (manufacturer)                       +3 pts
    ✗ ISO 45001 (pending)                                +0 pts
    ✓ ABNT NBR 8850 compliance                           +1 pt
    Subtotal: 8 points

  Warranty Period (8):
    Offered: 24 months parts + 12 months labor           +8 pts
    Subtotal: 8 points

  Defect Rate & Quality (12):
    Historical defect rate: 2.5%
    On-time delivery: 96%
    Strength: 3 similar tower projects 2023–2025          +12 pts
    Subtotal: 12 points

  References (10):
    Project 1: LT 500kV (2025, Eletrobras) — Excellent ref
    Project 2: LT 345kV (2024, State Grid) — Excellent ref
    Project 3: Transmission substation (2023, ENEL) — Good ref
    Score: 10 + 2 bonus (Tier-1) = 12 pts (capped at 10)     +10 pts
    Subtotal: 10 points

  ➜ QUALITY SUBTOTAL: 8+8+12+10 = 38 points

COST DIMENSION (30 points)
  Quoted Price: R$ 25,850 (per unit)
  Benchmark Price: R$ 25,850
  Deviation: 0% (exactly at benchmark)
  
  Formula: 30 × (1 - 0/25850) = 30
  ➜ COST SUBTOTAL: 30 points

DELIVERY DIMENSION (20 points)
  Lead Time (12):
    Baseline deadline: 2027-01-29
    Quoted delivery: 2027-01-30 (1 day late)
    Score: 10 pts (acceptable; within 10-day window)
    Subtotal: 10 points

  Milestone Delivery (5):
    Phase 1: 100 towers by 2027-01-15
    Phase 2: 100 towers by 2027-02-15
    Score: 5 pts (2 milestones, customized)
    Subtotal: 5 points

  On-Time Delivery History (3):
    From references: 96% historical OTD
    Score: 3 pts
    Subtotal: 3 points

  ➜ DELIVERY SUBTOTAL: 10+5+3 = 18 points

RISK DIMENSION (10 points)
  Geographic Risk:
    Production: 60% Recife, 35% São Paulo, 5% subcontractors
    Multi-region spread; low concentration risk
    Deduction: 0 pts
    Subtotal: 0 pts

  Financial Health:
    Serasa score: 82 (excellent)
    Deduction: 0 pts
    Subtotal: 0 pts

  Supply Chain:
    Multiple steel suppliers (5+)
    No single-source dependency
    Deduction: 0 pts
    Subtotal: 0 pts

  Lead Time Buffer:
    Quote includes 30+ day buffer above baseline? Yes
    Deduction: 0 pts
    Subtotal: 0 pts

  ➜ RISK SUBTOTAL: 10 – 0 = 10 points

═════════════════════════════════════════════════════════════════════════════
FINAL SCORE (EMN): 38 + 30 + 18 + 10 = 96 / 100 points
═════════════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────────────
RANK 2: TUBOS E ESTRUTURAS BRASIL S.A. (TEB)
─────────────────────────────────────────────────────────────────────────────

Quoted Price: R$ 26,950 (+4.3% vs. benchmark)
QUALITY: 35 | COST: 27 | DELIVERY: 14 | RISK: 8
FINAL SCORE: 84 / 100 points

Key Flags:
  ✗ Missing ISO 45001 (–1 in quality)
  ✗ 1 tower project reference only (–3 in quality)
  ⚠ Quoted delivery 2027-02-05 (7 days late, –2 in delivery)
  ⚠ Geographic risk: 95% São Paulo production (–2 in risk)

───────────────────────────────────────────────────────────────────────────────
RANK 3: INTERNATIONAL STEEL SUPPLIERS INC. (Imported)
───────────────────────────────────────────────────────────────────────────────

Quoted Price: R$ 28,500 (+10.3% vs. benchmark)
QUALITY: 32 | COST: 24 | DELIVERY: 6 | RISK: 5
FINAL SCORE: 67 / 100 points

Key Flags:
  ✗ Foreign INMETRO certification (equivalent but not direct)
  ⚠ Lead time 120 days (Customs clearance adds risk)
  ⚠ Geographic risk: 100% imported (supply chain vulnerability)
  ✗ High cost (+10%)

Recommendation: Not recommended (shipping delays too risky for critical path)

─────────────────────────────────────────────────────────────────────────────
RANK 4: REGIONAL FABRICADORA (RFA)
─────────────────────────────────────────────────────────────────────────────

Quoted Price: R$ 24,500 (–5.2% vs. benchmark — LOWEST)
QUALITY: 20 | COST: 30 | DELIVERY: 8 | RISK: 3
FINAL SCORE: 61 / 100 points

REJECTION FLAGS:
  ✗ INMETRO certification: EXPIRED (2024-12-31)
  ✗ No ISO 9001 (small fabricator, <50 employees)
  ✗ Zero tower project references (auto-reject Phase 1 for lack of experience)
  ✗ Serasa score: 45 (poor credit; recommend prepayment or LC)

Recommendation: REJECT (Phase 1 — fails technical compliance)

─────────────────────────────────────────────────────────────────────────────
RANK 5: TORRES BRASIL LTDA. (TBL)
─────────────────────────────────────────────────────────────────────────────

Quoted Price: R$ 27,200 (+5.2% vs. benchmark)
QUALITY: 36 | COST: 26 | DELIVERY: 12 | RISK: 7
FINAL SCORE: 81 / 100 points

Key Flags:
  ✓ INMETRO + ISO 9001 + ISO 45001 (all certifications)
  ⚠ Only 1 tower reference (larger projects not attempted)
  ✗ Lead time 2027-02-12 (14 days late, –2 in delivery)
  ⚠ Geographic: 80% Paraná (concentrated region, –1 in risk)
  ⚠ Serasa: 68 (fair credit; monitor)

Recommendation: Not recommended (similar score to TEB, but higher price)

═════════════════════════════════════════════════════════════════════════════

FINAL RECOMMENDATION MATRIX

Rank | Vendor | Score | Status | Recommendation
─────┼────────┼───────┼────────┼────────────────────────────────────────
  1  | EMN    | 96    | ✓ PASS | APPROVE & NEGOTIATE (primary)
  2  | TEB    | 84    | ✓ PASS | Backup supplier (if EMN unavailable)
  3  | TBL    | 81    | ✓ PASS | Tertiary option (cost too high)
  4  | Intl   | 67    | ✓ PASS | Not recommended (lead time risk)
  5  | RFA    | 61    | ✗ FAIL | REJECTED (Phase 1 technical non-compliance)

═════════════════════════════════════════════════════════════════════════════

FINAL SELECTED VENDOR: ESTRUTURAS METÁLICAS NORDESTE LTDA. (EMN)

Score: 96 / 100 (98% of maximum)
Unit Price: R$ 25,850
Total Cost (200 towers): R$ 5,170,000
Delivery: 2027-01-30 (1 day late, acceptable)
Warranty: 24 months
Payment Terms: 60 days net from delivery
Quality Confidence: EXCELLENT
Risk Profile: LOW

NEXT STEPS:
  1. Send Notice of Award to EMN by 2026-08-22
  2. Negotiate final commercial terms (see attached proposed contract)
  3. Issue Purchase Order by 2026-08-31
  4. Schedule kickoff meeting with EMN within 2 weeks
  5. Establish inspection protocol (3 towers sample-tested, TPI by DNV)
  6. Set up SharePoint folder for document management

═════════════════════════════════════════════════════════════════════════════
```

---

## 4. Scoring Rubric Quick Reference

### Scoring Scale
- **90–100:** Excellent (recommend approval)
- **80–89:** Good (acceptable with minor risk)
- **70–79:** Fair (conditions apply; consider alternatives)
- **60–69:** Poor (only if other options exhausted)
- **<60:** Reject (fails technical or business criteria)

### Auto-Reject Criteria (Phase 1)
- Missing mandatory INMETRO or ABNT certifications (commodity-dependent)
- No references for similar projects
- Delivery date breaks critical path (>40 days late)
- Serasa score <40 + Serasa negative listing + pending legal disputes

### Escalation Rules
- Score 90–100: Approve (procurement authority)
- Score 80–89: Approve with conditions (CFO review if cost >10% above budget)
- Score 60–79: Require VP approval
- Score <60: Require C-level approval or re-bid

---

## 5. Weighted Scoring by Commodity Type

Some commodities may require different weights:

| Commodity | Quality | Cost | Delivery | Risk |
|---|---|---|---|---|
| **Transmission Tower** (our example) | 40% | 30% | 20% | 10% |
| **SCADA System** (S8) | 50% | 25% | 15% | 10% | (quality > cost) |
| **Dredge Equipment** (S6) | 35% | 35% | 20% | 10% | (cost-sensitive) |
| **Concrete (commodity)** | 20% | 60% | 15% | 5% | (price-driven) |
| **Pipe Network** (critical infrastructure) | 45% | 20% | 25% | 10% | (quality + delivery) |

---

**End of Vendor Evaluation Matrix**
