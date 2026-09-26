# RFQ Template Generator — Manta-24-Procurement

**Version:** 1.0.0  
**Date:** 2026-08-02  
**Purpose:** Generate Request for Quotation (RFQ) documents automatically based on project scope, commodity type, and technical specifications.

---

## Template Library Overview

12 pre-configured templates covering major procurement categories:

| ID | Template Name | Commodity | Segment(s) | Lead Fields |
|----|---------------|-----------|-----------|------------|
| T-001 | Transmission Tower | Steel structures, galvanizing, transport | S9 (Energy) | Weight, paint code, delivery address |
| T-002 | Dredge Equipment | Cutter-suction, split hopper, crew | S6 (Ports) | Capacity m³/hr, fuel type, rental term |
| T-003 | SCADA System | Controllers, sensors, software, cloud | S8 (Saneamento) | Sensor count, uptime SLA, integration |
| T-004 | PVC Pipes | Pipe, fittings, jointing materials | S8 (Saneamento) | DN size, pressure rating, meter quantity |
| T-005 | Concrete Bulk | Ready-mix delivery, strength class | S1-S4 (General) | Volume m³, Fck, slump, distance |
| T-006 | Reinforcing Steel | Rebars, mesh, couplers | S1-S4 (General) | Nominal diameter, total mass, delivery |
| T-007 | Power Transformer | Oil-filled, capacity, cooling | S9 (Energy) | kVA, voltage levels, location, installation |
| T-008 | Valve Assembly | Gate, check, relief, industrial | S6, S8 (Multi) | Type, size, pressure rating, material |
| T-009 | Cable Supply | Copper, aluminum, insulation type | S9 (Energy), Industrial | Cross-section, length, installation |
| T-010 | Asphalt Mix | Warm-mix, plant mix, emulsion | S1 (Rodovia) | Volume, binder type, stockpile location |
| T-011 | Heavy Machinery Rental | Excavators, dozers, cranes | S1-S4 (Multi) | Equipment ID, term months, operator yes/no |
| T-012 | Geotechnical Materials | Geomembrane, geotextile | S1, S4, S8 (Multi) | Width, thickness, area m² |

---

## Template Structure (Standard RFQ)

Every RFQ follows this structure:

```
[RFQ DOCUMENT HEADER]
├─ Document ID & Revision
├─ Project info & contact
├─ Validity period (10 business days default)
├─ Submission instructions (email/portal/physical)
└─ Late bid handling policy

[SCOPE OF WORK / BILL OF MATERIALS]
├─ Line item numbering (01, 02, 03...)
├─ Item description (with ABNT references)
├─ Quantity & unit
├─ Unit spec (e.g., "Grade 50 galvanized, per ASTM A 123")
└─ Delivery schedule (dates or milestones)

[COMMERCIAL TERMS]
├─ Payment terms (e.g., "30 days net from delivery")
├─ Freight terms (FOB, CIF, DDP)
├─ Currency (BRL default, USD option)
├─ Price escalation clause (if >6 months)
└─ Warranty period (default: 12 months parts/labor)

[TECHNICAL REQUIREMENTS]
├─ Quality certifications (INMETRO, ISO, ABNT)
├─ Inspection/testing plan (third-party yes/no)
├─ Packaging & transport (damage protection specs)
├─ Storage requirements (temperature, humidity if applicable)
└─ As-built documentation (drawings, manuals, O&M)

[VENDOR SUBMISSION REQUIREMENTS]
├─ Completed quote form (attached)
├─ Company profile & certifications
├─ References (3 similar projects in past 3 years)
├─ Financial statement (balance sheet, last 2 years)
├─ Timeline commitment (delivery date, milestones)
└─ Signed declaration of competence

[EVALUATION CRITERIA]
├─ Technical compliance (pass/fail)
├─ Quality certifications (mandatory list)
├─ Delivery timeline (scored 0–20 points)
├─ Price (scored 0–30 points, benchmarked)
└─ Vendor stability (credit check, 0–10 points)

[LEGAL & COMPLIANCE]
├─ General conditions of purchase (payment, liability)
├─ Dispute resolution (mediation, arbitration)
├─ ABNT/INMETRO compliance attestation
├─ Confidentiality clause
└─ Tax responsibility (ICMS, PIS, COFINS rates by state)
```

---

## Template T-001: Transmission Tower

### Sample Generated RFQ (Minimal)

```
═══════════════════════════════════════════════════════════════════════════════
REQUEST FOR QUOTATION (RFQ)
═══════════════════════════════════════════════════════════════════════════════

Document ID:        RFQ-2026-08-LT345-TOWERS-001
Revision:           A
Issue Date:         02 de agosto de 2026
Deadline:           13 de agosto de 2026, 17:00 BRT
Project:            Linha de Transmissão 345 kV — Trecho São Paulo–Rio de Janeiro
Client:             State Grid Brasil (State Grid de Energia)
Contact:            procurement@stategrid.com.br
Procurement Officer: Maria da Silva (msilva@stategrid.com.br, +55-11-3333-0001)

SUBMISSION METHOD:
  Email: rfq-submissions@stategrid.com.br
  Subject: "RFQ-2026-08-LT345-TOWERS-001 — [VENDOR NAME]"
  Attachments: Signed quote + certifications + references

───────────────────────────────────────────────────────────────────────────────
SCOPE OF WORK — BILL OF MATERIALS
───────────────────────────────────────────────────────────────────────────────

Item | Description | Quantity | Unit | Spec | Unit Price | Total Price
────┬─────────────┬──────────┬──────┬──────┬────────────┬──────────────
01  | Transmission Tower, Angle Steel | 200 | ea | CFRD design, grade 250 MPa, | | 
    | Type 2A (double-circuit, ABNT | | | galvanized per ASTM A 123 | | 
    | NBR 8850) | | | (85 μm min.) | | 
────┼─────────────┼──────────┼──────┼──────┼────────────┼──────────────
02  | Bolts & Hardware (galvanized) | 2000 | kg | M24, M27, hardness grade 8.8, | | 
    | | | | DIN 931, stainless washers | | 
────┼─────────────┼──────────┼──────┼──────┼────────────┼──────────────
03  | Paint (touch-up, each tower) | 200 | L | Epoxy ester, RAL 7035 light gray, | | 
    | | | | 2-coat system per NR-12 | | 
────┼─────────────┼──────────┼──────┼──────┼────────────┼──────────────
04  | Foundation Bolts & Sleeves | 800 | set | M45 stainless steel (A4-70), | | 
    | | | | per ABNT NBR 8800 | | 
────┼─────────────┼──────────┼──────┼──────┼────────────┼──────────────
   | | | | | SUB-TOTAL: | R$ ___________
   | | | | | Tax (ICMS 7%): | R$ ___________
   | | | | | Freight (FOB delivery): | R$ ___________
   | | | | | TOTAL PRICE: | R$ ___________

DELIVERY SCHEDULE:
  • Mobilization: within 30 days of purchase order
  • Delivery of first 50 towers: 90 days from order
  • Delivery of remaining 150 towers: 150 days from order
  • Installation support: as per project Gantt (separate labor contract)

───────────────────────────────────────────────────────────────────────────────
COMMERCIAL TERMS
───────────────────────────────────────────────────────────────────────────────

Currency:           Brazilian Real (BRL) or USD (quote both, we choose BRL conversion)
Payment Terms:      60 days net from delivery & inspection acceptance
Freight Terms:      FOB destination (vendor responsible for loss/damage in transit)
Price Validity:     90 days from quote date
Escalation Clause:  IPC-A (or mutually agreed index) if delivery >180 days
Warranty:           24 months parts & labor from final installation acceptance

───────────────────────────────────────────────────────────────────────────────
TECHNICAL REQUIREMENTS
───────────────────────────────────────────────────────────────────────────────

Quality Certifications (MANDATORY):
  ☑ INMETRO certification for structural steel (ABNT NBR 7007)
  ☑ ABNT NBR 8850 compliance for tower design
  ☑ Galvanizing per ASTM A 123 (coating thickness report required)
  ☑ ISO 9001:2015 manufacturer quality system
  ☑ OHSAS 18001 or ISO 45001 (workplace safety)

Inspection & Testing:
  • Third-party inspection (TPI) by DNV or similar Notified Body
  • Load testing: 10% of towers sample-tested to 1.25× design load
  • Coating thickness: minimum 85 μm (eddy-current gauge 3 points per tower)
  • Field inspection: Client engineer on-site 3 days/week during delivery

Documentation:
  • Mill certificates (steel grade, chemical analysis)
  • Galvanizing certificates (coating weight, thickness)
  • Assembly drawings (scaled 1:20, PDF + CAD dwg files)
  • Bolt torque specification document
  • O&M manual (Portuguese, 50 pages min.)
  • Spare parts list (10-year consumables)

Packaging & Transport:
  • Wrapped in plastic sheeting (UV-protected)
  • Wooden skids, strapped with nylon bands (no wire rope — corrosion risk)
  • Each package ≤ 25 tons (road transport limit in São Paulo)
  • Insurance: 110% of goods value, vendor responsibility

───────────────────────────────────────────────────────────────────────────────
VENDOR SUBMISSION REQUIREMENTS
───────────────────────────────────────────────────────────────────────────────

Deadline: 13 de agosto de 2026, 17:00 BRT (late submissions rejected)

Minimum Required Documents:
  ☐ Completed RFQ Quote Form (attached, page 3)
  ☐ INMETRO & ABNT compliance certificates (color scans)
  ☐ ISO 9001 / ISO 45001 certificates (current, signed)
  ☐ Company profile (A4 page max): name, CNPJ, established date, employees, locations
  ☐ Financial references (Serasa/SPC credit report dated <6 months)
  ☐ Three similar project references:
    ─ Client name & contact
    ─ Project description (tower type, quantity, date delivered)
    ─ On-time delivery yes/no
  ☐ Timeline commitment: delivery dates for each shipment (Gantt or table)
  ☐ Signed declaration: "We confirm technical & commercial capacity per RFQ-2026-08-LT345-TOWERS-001"
  ☐ Contact person: name, phone, email, signature

───────────────────────────────────────────────────────────────────────────────
EVALUATION CRITERIA & SCORING
───────────────────────────────────────────────────────────────────────────────

Evaluation Phases:

Phase 1 — TECHNICAL COMPLIANCE (Pass/Fail)
  ✓ All ABNT/INMETRO certifications present?
  ✓ Delivery timeline meets project schedule?
  ✓ All documentation requirements satisfied?
  → If any "No": Bid REJECTED

Phase 2 — QUALITY & CERTIFICATIONS (Scored 0–20 points)
  • ISO 9001 + ISO 45001: +5 points (all 3 certifications) / +3 (one missing)
  • Galvanizing: ASTM A 123 (≥85 μm) = +5 points; A 123-B (lower) = +2
  • 3+ similar projects (past 3 years) = +5 points; 1–2 projects = +2; 0 = 0
  • Financial health (Serasa score >75) = +5 points; <75 = 0
  Total: 20 points

Phase 3 — DELIVERY TIMELINE (Scored 0–20 points)
  • Baseline: 90 days (first 50 towers)
  • Quote ≤ 90 days: +20 points
  • Quote 91–120 days: +15 points
  • Quote 121–150 days: +10 points
  • Quote > 150 days: 0 points (unacceptable)

Phase 4 — PRICE (Scored 0–30 points)
  • Benchmark price: average of all compliant quotes
  • Lowest quote = +30 points
  • +10% above benchmark = +20 points
  • +20% above benchmark = +10 points
  • +30% above benchmark = 0 points

Phase 5 — SUPPLY CHAIN RISK (Scored 0–10 points)
  • Single-source risk: quote vendor has <30 employees = –3 points
  • Geographic concentration: 100% production in one state = –2 points
  • Delivery method: air freight = +0; sea+land = +5; land only = +2
  • Lead time buffer: quote + 30-day cushion available = +5 points; no buffer = 0

FINAL SCORE = Tech (20) + Delivery (20) + Price (30) + Risk (10) = 80 points max

SELECTION RULE:
  Highest-scored vendor = RECOMMENDED
  If tied: Select by lowest price

───────────────────────────────────────────────────────────────────────────────
LEGAL & COMPLIANCE
───────────────────────────────────────────────────────────────────────────────

General Conditions of Purchase:
  1. This RFQ is confidential. Vendor may not publish or share without written consent.
  2. All prices are fixed unless escalation clause (above) applies.
  3. Vendor liability capped at purchase price for defective goods.
  4. Brazilian law (Lei 14.026 + ABNT standards) governs this RFQ.

Payment & Dispute Resolution:
  • Disputes: first mediation (30 days), then arbitration (SAC — Câmara de Arbitragem)
  • Governing law: Brazilian law; venue: São Paulo, SP
  • Force majeure: "Natural disaster, pandemic, war" excuses delays >60 days

Tax Responsibility:
  • Vendor responsible for: ICMS (7% in SP), PIS (1.65%), COFINS (7.6%)
  • We will issue RPA (Recibo de Pagamento por Autônomo) if CNPJ not registered
  • Nota Fiscal (NF-e) required for all shipments

ABNT / INMETRO Compliance:
  • Vendor certifies all materials comply with ABNT NBR 7007, 8800, 8850
  • INMETRO mark visible on all structural steel packages
  • Any non-compliant delivery = 100% return cost borne by vendor

───────────────────────────────────────────────────────────────────────────────
APPENDIX — QUOTE FORM (VENDOR TO COMPLETE)
───────────────────────────────────────────────────────────────────────────────

Company: _________________________ | CNPJ: _________________
Contact: _________________________ | Phone: _________________

ITEM | UNIT PRICE (BRL) | DELIVERY DATE | NOTES
─────┼──────────────────┼───────────────┼────────────────────────
01   | R$ _____________ | _____________ | (e.g., "Grade 250 verified")
02   | R$ _____________ | _____________ |
03   | R$ _____________ | _____________ |
04   | R$ _____________ | _____________ |

TOTAL: R$ _____________

Signed: _________________________ | Date: _________________
        Authorized Representative

═══════════════════════════════════════════════════════════════════════════════
End of RFQ-2026-08-LT345-TOWERS-001
═══════════════════════════════════════════════════════════════════════════════
```

---

## Template T-003: SCADA System (Saneamento)

### Key Fields (Auto-Populated by Agent)

```
Commodity:        SCADA System (supervisory control + cloud)
Segment:          S8 — Saneamento
Project Context:  Estação de Tratamento de Água (ETA) — 5,000 m³/day

[AUTO-FILL]
Sensor count:     50 (extracted from ETA P&ID)
Uptime SLA:       99.5% (standard for ETA)
Integration:      Existing LIMS system (Oracle)
Support language: Portuguese
Warranty:         5 years (standard for water treatment)

[GENERATED BOM]
Item 01: Master Control Unit (PLC) — Siemens S7-1500 or equivalent (1 unit)
Item 02: Analog I/O Modules (50-sensor capacity) — 2 × AI16, 1 × AO8 (3 units)
Item 03: Communication Gateway — Ethernet industrial switch + VPN (1 unit)
Item 04: Sensors (flow, pH, turbidity, chlorine, pressure) — 50 units
Item 05: Cloud Platform License (5 years) — Microsoft Azure IoT or AWS
Item 06: Integration & Commissioning (2 weeks on-site) — 1 lot
Item 07: Training & Documentation (Portuguese) — 1 lot
Item 08: Maintenance & Support (5 years) — 1 lot

TOTAL COST TARGET: R$ 1,200,000 (budget constraint)
```

---

## Generator Algorithm (Pseudo-Code)

```python
def generate_rfq(
    commodity_type: str,      # "transmission_tower", "dredge", etc.
    project_scope: dict,      # {bom, budget, timeline, location}
    client_info: dict         # {name, contact, delivery_address}
) → (rfq_docx, rfq_json):
    
    # Step 1: Select template
    template = TEMPLATE_LIBRARY[commodity_type]  # T-001, T-002, ...
    
    # Step 2: Extract specs from project scope
    bom_items = parse_bom(project_scope['bill_of_materials'])
    budget = project_scope['budget_allocated']
    timeline = project_scope['project_timeline']
    
    # Step 3: Auto-populate header
    rfq['doc_id'] = f"RFQ-{date.year}-{timeline.month:02d}-{project_code}-{seq:03d}"
    rfq['issue_date'] = today()
    rfq['deadline'] = today() + timedelta(days=10)
    rfq['client'] = client_info['name']
    rfq['contact'] = client_info['procurement_officer']
    
    # Step 4: Generate BOM section
    rfq['bom'] = []
    for (idx, item) in enumerate(bom_items):
        bom_line = {
            'line_no': f"{idx+1:02d}",
            'description': f"{item['name']} ({item['spec']})",
            'quantity': item['qty'],
            'unit': item['unit'],
            'spec_ref': f"ABNT {item['abnt_standard']}" if item['abnt_standard'] else "",
            'unit_price_placeholder': "R$ ___________",
            'total_price_placeholder': "R$ ___________"
        }
        rfq['bom'].append(bom_line)
    
    # Step 5: Auto-calculate benchmark price (if historical data exists)
    benchmark_price = query_historical_quotes(commodity_type, bom_items)
    rfq['benchmark_note'] = f"Historical average: R$ {benchmark_price:,.2f}"
    
    # Step 6: Populate delivery schedule
    rfq['delivery_schedule'] = calculate_milestones(timeline, bom_items)
    
    # Step 7: Insert ABNT compliance checklist
    rfq['abnt_checks'] = template['mandatory_standards']
    rfq['inmetro_required'] = check_inmetro_mandate(commodity_type)
    
    # Step 8: Set payment terms (default: 60 days net)
    rfq['payment_terms'] = "60 days net from delivery & acceptance"
    rfq['currency'] = "BRL (or USD quoted separately)"
    
    # Step 9: Scoring matrix (weighted by commodity_type)
    rfq['evaluation_weights'] = template['scoring_model']  # {quality, cost, delivery, risk}
    
    # Step 10: Render to DOCX + JSON
    docx_buffer = render_to_docx(rfq, template['style_guide'])
    json_export = to_json(rfq)
    
    # Step 11: Save to SharePoint
    sp_path = f"/03-Procurement/RFQs/{project_code}/{rfq['doc_id']}"
    upload_to_sharepoint(docx_buffer, json_export, sp_path)
    
    return (docx_buffer, json_export)
```

---

## Usage Example (Agent Interaction)

```
User: "Preciso fazer RFQ de estruturas de transmissão para LT 345kV. 200 torres, 
       CFRD design, prazo de entrega 90 dias máximo. Budget: R$5.2M."

Agent:
  1. Recognizes commodity → "transmission_tower" → Template T-001
  2. Extracts specs:
     - BOM: 200 towers, 2000 kg bolts, 200 L paint, 800 sleeves
     - Budget: R$5.2M (≈ R$26K/tower avg benchmark)
     - Timeline: 90 days max for 1st shipment
  3. Auto-generates RFQ:
     - Doc ID: RFQ-2026-08-LT345-TOWERS-001
     - Deadline: 13 de agosto 2026 (10 business days)
     - BOM pre-filled with specs, ABNT refs
     - Scoring: Technical (20) + Delivery (20) + Price (30) + Risk (10)
  4. Output: RFQ.docx (35 pages), RFQ.json (structured data)
  5. Publishing: Saved to SharePoint, posted to Agora Brasil API

User reviews draft → approves → agent sends to 5 pre-qualified vendors → deadline 
→ agent evaluates responses → scorecard generated.
```

---

## Integration with Vendor Database

```json
{
  "vendor_id": "V-2026-08-001",
  "company_name": "Estruturas Metálicas Nordeste Ltda.",
  "commodity_codes": ["transmission_tower", "structures_steel"],
  "certifications": {
    "INMETRO": true,
    "ISO_9001": true,
    "ISO_45001": false,
    "ABNT_NBR_8850": true
  },
  "historical_quotes": [
    {
      "rfq_id": "RFQ-2025-11-LT500-TOWERS-001",
      "quoted_price": 28500,
      "actual_price_per_unit": 27200,
      "on_time_delivery": true,
      "quality_issues": 0,
      "payment_on_time": true
    }
  ],
  "suggested_for_rfq": true,
  "last_contact": "2026-08-01",
  "notification_preference": "email:rfq@metallicasestruturasne.com.br"
}
```

---

## Quality Gates

- **Mandatory ABNT refs:** Auto-validated before RFQ publish
- **Budget alignment:** Total BOM cost flagged if >110% of allocated budget
- **Delivery feasibility:** Checked against supplier lead-time database
- **Compliance:** INMETRO/ISO requirements verified per commodity type

---

**End of RFQ Template Generator**
