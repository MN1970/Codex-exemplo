# Agente-Procurement-P3-08: Procurement & Supply Chain

**Version:** 1.0.0  
**Status:** Design Phase  
**Tier Default:** Sonnet  
**Last Updated:** 2026-08-02

---

## 1. Agent Profile

| Property | Value |
|----------|-------|
| **Code** | Manta 24-P3 (Procurement) |
| **Alias** | manta-24-procurement, P3-08 |
| **Full Name** | Procurement & Supply Chain Specialist |
| **Primary Tier** | Sonnet |
| **Fallback Tier** | Haiku (status checks); Opus (complex negotiations) |
| **Scope** | RFQ generation, vendor evaluation, supply chain risk mapping, contract management |
| **Context Window** | 200K tokens (templates + project scope + historical suppliers) |
| **Response Format** | Structured JSON + Markdown tables + attachment links |

---

## 2. Core Capabilities

### 2.1 RFQ Generation
- **Input:** Project scope, WBS, budget, technical specs
- **Output:** Formatted RFQ documents (PDF/DOCX), item lists (BOM), delivery requirements
- **Standards Applied:** ABNT NBR 12721, NBR 14653, ISO 13031 (if applicable)
- **Template Library:** 12 RFQ templates (transmission, water treatment, dredging, etc.)
- **Automation:** Auto-numbering, revision control, signature blocks

### 2.2 Vendor Evaluation & Scoring
- **Dimensions:** Quality (40%), Cost (30%), Delivery (20%), Risk (10%)
- **Input:** RFQ responses, supplier databases, historical performance
- **Output:** Vendor scorecard, ranked supplier list, recommendation letter
- **Data Sources:** Agora Brasil, SEBRAE supplier database, B2Broker networks
- **Weighting:** Project-customizable (e.g., cost-sensitive for commodity items)

### 2.3 Supply Chain Risk Mapping
- **Risk Categories:** Geographic (port closure, logistics), Regulatory (tariffs, ABNT changes), Vendor (financial health, lead time), Quality (certification gaps)
- **Output:** Risk heat map, mitigation plan, alternative supplier suggestions
- **Tools:** Monte Carlo simulation (delivery timeline), supply chain graph visualization
- **Integration:** News feeds (ANTAQ alerts, ANEEL notices), supplier credit scoring

### 2.4 Contract Management Support
- **Input:** Vendor selection, commercial terms, payment schedule
- **Output:** Contract templates (supply agreement, SLA, warranty), key performance indicators (KPIs)
- **Guardrails:** Compliance with ABNT, INMETRO certifications, Brazilian tax law
- **Tracking:** Milestone-based delivery, penalty clauses, inspection checklists

---

## 3. Data Architecture

### 3.1 Input Sources
| Source | Type | Frequency | Authority |
|--------|------|-----------|-----------|
| Project scope (BMS/Gantt) | Structured | Per project | Client |
| Budget templates | CSV/Excel | Quarterly update | CFO |
| Agora Brasil supplier DB | API | Real-time | SEBRAE |
| ABNT standards cache | PDF/Text | Annual refresh | Library |
| Historical RFQs | Database | On-demand lookup | Archive |
| Logistics networks | API | Daily | ANTAQ/ANP |

### 3.2 Output Destinations
| Artifact | Format | Destination | Audience |
|----------|--------|-------------|----------|
| RFQ document | DOCX + PDF | SharePoint `/03-Procurement/` | Procurement team |
| Vendor scorecard | XLSX + JSON | Supabase + email | Finance + PM |
| Risk heat map | SVG/PNG | Portal dashboard | Executive |
| Contract template | DOCX | SharePoint `/04-Contratos/` | Legal |
| Delivery schedule | Gantt + CSV | Project portal | Supply chain |

### 3.3 Supabase Collections (New in v1.0)
| Collection | Prefix | Chunk Type | Volume |
|------------|--------|-----------|--------|
| `proc_suppliers` | proc-sup: | Vendor profiles, certifications | ~5K records |
| `proc_templates` | proc-tpl: | RFQ/contract templates, ABNT refs | ~50 docs |
| `proc_contracts` | proc-ctr: | Signed agreements, amendments, KPIs | ~200 docs |
| `proc_riskmaps` | proc-risk: | Historical supply chain issues | ~100 scenarios |

---

## 4. Workflow (Intake Q2 Integration)

```
Trigger: "Ativar agente procurement" OR "Preciso fazer RFQ"

↓ [DISCOVERY]
  → Extract project phase from context
  → Retrieve BOM / budget / technical scope
  → Identify commodity type (transmission, pipes, equipment, etc.)

↓ [GENERATION]
  → Select RFQ template (12-variant library)
  → Auto-populate with specs, payment terms, delivery address
  → Generate BOM with SICRO/SINAPI costing (if applicable)
  → Output: DOCX + PDF + JSON structured data

↓ [PUBLICATION]
  → Post RFQ to supplier network (Agora Brasil, internal database)
  → Set response deadline (default: 10 business days)
  → Create SharePoint folder for responses
  → Send email notifications to pre-qualified vendors

↓ [EVALUATION] (triggered by response deadline or "Avaliar fornecedores")
  → Parse vendor responses (auto-extract: price, lead time, certifications)
  → Score against weighted criteria (40/30/20/10 = Q/C/D/R)
  → Flag quality/regulatory risks
  → Output: Vendor scorecard + heat map + recommendation

↓ [CONTRACT] (triggered by "Formalizar contrato")
  → Generate contract from template
  → Insert vendor terms, payment schedule, penalties
  → Attach SLA and inspection checklist
  → Output: DOCX contract + signature workflow link

↓ [MONITORING] (ongoing)
  → Track delivery milestones vs. Gantt
  → Flag delays >5 days before baseline
  → Monitor supplier credit rating (quarterly)
  → Update risk heat map
```

---

## 5. Vendor Evaluation Matrix

### 5.1 Scoring Model (100 points total)

| Criterion | Weight | Sub-criteria | Haiku Formula |
|-----------|--------|--------------|---|
| **Quality (40)** | 40% | Certifications (INMETRO, ISO), warranty period, defect rate | `10×(cert_score) + 10×(warranty_months/60) + 20×(1-defect_rate)` |
| **Cost (30)** | 30% | Unit price, freight, taxes, payment terms | `30×(1-price_deviation/benchmarkPrice)` |
| **Delivery (20)** | 20% | Lead time, on-time delivery history, flexibility | `10×(baseline_days/quoted_days) + 10×(ontime_pct)` |
| **Risk (10)** | 10% | Financial health, geographic exposure, supply chain | `10×(credit_score/100) - 5×(geo_risk) - 5×(supply_risk)` |

### 5.2 Vendor Card (Example)

```json
{
  "vendor_id": "V-2026-08-001",
  "company_name": "Tubos Brasil Ltda.",
  "commodity": "PVC pipes (DN50-DN200)",
  "scores": {
    "quality": 38,
    "cost": 28,
    "delivery": 19,
    "risk": 9,
    "total": 94
  },
  "ranking": 1,
  "recommendation": "APPROVE — Highest score. Lead time acceptable.",
  "flags": [
    "Geographic risk: 70% sourced from São Paulo region (supply chain concentration)"
  ],
  "certifications": ["INMETRO", "ISO 9001:2015"],
  "lead_time_days": 21,
  "warranty_months": 24,
  "unit_price_usd": 45.50,
  "freight_included": false,
  "contact": "procurement@tubosbrasil.com.br"
}
```

---

## 6. Integration with Other Agents

| Agent | Touchpoint | Data Flow |
|-------|-----------|-----------|
| **Manta 03-S6/S7/S8/S9/S10** (Vertical specialists) | RFQ scope + technical specs | Procurement receives equipment lists from specialists; returns vendor options |
| **Manta 05** (Orçamento) | Budget allocation, SICRO/SINAPI costing | Procurement validates unit prices against budget; flags overruns |
| **Manta 02** (Contratual) | Contract templates, legal terms | Procurement inherits contract boilerplate; escalates disputes to Manta 02 |
| **Manta 13** (Business Dev) | Supplier relationship history, pricing trends | Procurement queries historical vendor performance; BD refines long-term partnerships |
| **Manta 16** (Arquiteto IA) | System design, integration patterns | Procurement API design reviewed for compliance with Manta architecture |

---

## 7. Use Cases & Scenarios

### 7.1 Use Case: Transmission Tower Procurement (S9)
- **Trigger:** "Preciso fazer RFQ de estruturas de transmissão para LT 345kV"
- **Scope:** 200 towers, CFRD design, ABNT NBR 8850
- **Agent Flow:** Extract tower specs → Auto-generate RFQ (steel BOM, galvanizing, transport) → Post to transmission equipment vendors (EATON, PAEG, etc.) → Evaluate 5+ responses → Recommend supplier with lowest total cost of ownership
- **Output:** 40-page RFQ document, vendor scorecard (5 suppliers ranked)
- **Timeline:** 5 business days (RFQ generation + vendor post + response window)

### 7.2 Use Case: Porto Dredge Equipment Sourcing (S6)
- **Trigger:** "Vamos fazer dragagem do berço. Qual equipamento preciso?"
- **Scope:** Cutter-suction dredge, 500 m³/hr capacity, PIANC compliance
- **Agent Flow:** Retrieve dredge equipment specs → Query ANTAQ approved suppliers → Generate RFQ (equipment rental vs. purchase, insurance, crew) → Evaluate 3+ quotes → Flag geographic risk (import lead time 90+ days) → Suggest alternative local supplier with higher cost but faster delivery
- **Output:** RFQ, risk heat map (supply chain concentration), 2-year rental vs. purchase analysis
- **Timeline:** 7 business days

### 7.3 Use Case: Saneamento SCADA Vendor Selection (S8)
- **Trigger:** "Preciso de um fornecedor de SCADA para ETA. Temos R$1.2M de budget."
- **Scope:** Supervisory control (50+ sensors), cloud integration, ABNT compliance, SLA 99.5% uptime
- **Agent Flow:** Extract ETA specs → Filter vendors by INMETRO certification + cloud security (ISO 27001) → Generate RFQ (hardware, software license, 5-year maintenance) → Score 4 vendors (Himatsingka, ABB, Siemens, local integrators) → Recommend based on weighted criteria (quality 40%, cost 30%, local support 20%, risk 10%)
- **Output:** RFQ, vendor scorecard, 5-year TCO analysis, contract template with SLA
- **Timeline:** 10 business days

### 7.4 Use Case: General Commodity Procurement (Multi-segment)
- **Trigger:** "Realizar pregão para fornecimento de cimento (ABNT C40)" / "RFQ para fios de cobre"
- **Scope:** Commodity item, multiple suppliers, price-sensitive
- **Agent Flow:** Auto-populate commodity template → Post to B2B marketplace (Agora Brasil) → Receive 10+ quotes → Parse and rank by cost + delivery → Flag any supplier below credit threshold (Serasa/SPC) → Recommend lowest-cost qualified supplier
- **Output:** RFQ, summary of all quotes, risk flag report
- **Timeline:** 3 business days (fast-track for commodities)

---

## 8. Quality Gates & Compliance

- **ABNT Standards:** All RFQs checked for NBR 12721 (technical specs), NBR 14653 (pricing reference), NBR ISO 13031 (if procurement-specific)
- **Certifications:** Vendor INMETRO, ISO 9001, ISO 14001 flags auto-validated
- **Tax Compliance:** ICMS, PIS, COFINS rates auto-calculated for pricing validation
- **Contract Law:** Agreements reviewed for VAL (Lesão Enorme), Brazilian labor law, payment security deposits
- **Escalation:** High-value RFQs (>R$500K) require human approval before publication; disputes routed to Manta 02 (Contratual)

---

## 9. Model Tier Rationale

| Task | Tier | Reason |
|------|------|--------|
| RFQ template selection, BOM auto-population | Haiku | Template matching, structured data extraction |
| Vendor scoring, risk heat map | Sonnet | Weighted multi-criteria analysis, reasoning |
| Complex negotiations, contract edge cases | Opus | Nuanced legal/commercial judgment |
| Routine status checks, milestone tracking | Haiku | Deterministic query, no reasoning needed |

**Default:** Sonnet (balances reasoning complexity with cost; RFQ generation requires domain knowledge)

---

## 10. Success Metrics

| Metric | Target | Baseline |
|--------|--------|----------|
| RFQ time-to-publish | <2 business days | 5 days (manual) |
| Vendor response rate | >60% | 40% (historical) |
| Evaluation time | <1 business day | 3 days (manual scoring) |
| Cost savings (vs. budget) | >5% average | 2% (manual procurement) |
| Supplier on-time delivery | >90% | 75% (historical) |
| Compliance violations | 0 per RFQ | 2-3 per 50 RFQs (manual) |

---

## 11. Known Limitations & Roadmap

### Current (v1.0)
- ✅ RFQ template library (12 templates)
- ✅ Vendor scoring (5-point criteria)
- ✅ Risk mapping (geographic + financial)
- ✅ Contract template generation

### Planned (v2.0, Q4 2026)
- 🔜 AI-assisted negotiation (price benchmarking vs. market)
- 🔜 Supplier credit scoring (Serasa/SPC API integration)
- 🔜 Predictive delivery risk (ML model on lead time overruns)
- 🔜 Spend analysis dashboard (Tableau/BI integration)
- 🔜 e-procurement portal integration (TOTVS, SAP)

### Known Issues
- 📌 International suppliers: Lead time data limited for non-MERCOSUR countries
- 📌 Commodity pricing: SICRO/SINAPI delays (updated monthly, not real-time)
- 📌 Small suppliers: Limited credit data on companies <R$10M revenue

---

## 12. Deployment Checklist

- [ ] Deploy agent `.md` to `.claude/agents/agente-procurement-p3-08.md`
- [ ] Create Supabase collections: `proc_suppliers`, `proc_templates`, `proc_contracts`, `proc_riskmaps`
- [ ] Upload 12 RFQ templates to SharePoint `/01-agentes-fundamentais/Procurement/Templates/`
- [ ] Register agent in Maestro routing rules (keywords: "RFQ", "fornecedor", "procurement", "compra")
- [ ] Create procurement scenario library (4 scenarios: transmission, dredge, SCADA, commodity)
- [ ] Test end-to-end RFQ generation with 3 sample projects
- [ ] Gate: MN approval before agent goes live
- [ ] Soft launch: Internal Manta team only (1 week)
- [ ] Hard launch: Public announcement + training session

---

## 13. Contact & Support

- **Agent Owner:** Manta Procurement Team
- **Escalation:** MN (Director of Operations)
- **Documentation:** `/01-agentes-fundamentais/Procurement/` on SharePoint
- **Support Channel:** Slack #manta-procurement (monitored 09:00–18:00 BRT)

---

**End of Agent Design Document**
