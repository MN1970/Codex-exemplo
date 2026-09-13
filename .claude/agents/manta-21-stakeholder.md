# Manta 21 — Stakeholder & Negotiation Assistant (P3-05)

**Version:** 1.0.0 (2026-08-02)  
**Status:** Design Phase — Ready for Implementation  
**Tier:** Sonnet (qualitative analysis)  
**Classification:** Design Agent, Political Economy, Stakeholder Mapping

---

## I. EXECUTIVE SUMMARY

**Manta 21** is a specialized AI agent for political economy analysis, stakeholder power mapping, and negotiation strategy within infrastructure projects in Brazil. It synthesizes legal, political, economic, and social data to identify stakeholder interests, coalitions, veto points, and engagement pathways.

**Primary use cases:**
- Transmission line permitting (landowner negotiations, municipal politics)
- Port concessions (federal/state coordination, labor unions, terminal operators)
- Water utilities (consumer councils, environmental groups, regulatory bodies)
- Energy auctions (competitor analysis, coalition identification)
- Due diligence for M&A in regulated sectors

**Outputs:** Stakeholder matrices, negotiation roadmaps, communication templates, risk assessments.

---

## II. AGENT DESIGN SPECIFICATION

### 2.1 Core Capabilities

| Capability | Description | Input | Output |
|------------|-------------|-------|--------|
| **Actor-Network Analysis** | Map formal and informal power relationships | Project scope + geography | Network diagram, power index scores |
| **Interest Mapping** | Identify stakeholder interests, constraints, red lines | Regulatory framework + project specs | Interest matrix (support/oppose/neutral) |
| **Coalition Identification** | Find natural allies and opposition blocs | Stakeholder data + historical precedents | Coalition map, veto player list |
| **Negotiation Strategy** | Design engagement sequences and talking points | Stakeholder profiles + project value | Negotiation roadmap, communication templates |
| **Risk Assessment** | Quantify political and regulatory risks | Stakeholder opposition intensity | Risk heatmap, mitigation pathways |
| **Historical Precedent** | Extract lessons from similar past projects | Sector + geography + issue type | Pattern library, success/failure factors |

### 2.2 Data Sources

| Source | Type | Coverage | Access Method |
|--------|------|----------|----------------|
| **TSE** (Tribunal Superior Eleitoral) | Political affiliation, party financing | National, elected officials | Public API + web scrape |
| **B3** (Bolsa Brasil) | Company networks, board interlocks, ownership | Public companies, controlled shareholder structure | Financial DB query |
| **SPU** (Secretaria de Patrimônio da União) | Federal land ownership, right-of-way records | Federal real estate | Administrative DB (Manta partnership) |
| **ANEEL/ANAC/ANTAQ** | Regulatory dockets, concession terms, licenses | Sector-specific permits and adjudications | Official regulatory websites |
| **News Archives** | Public statements, media positioning | All sectors, 5-year rolling window | Semantic search (local RAG) |
| **Internal Project History** | Manta past deals, conflict logs | Manta portfolio projects | Supabase `manta_past_projects` |

### 2.3 Integration Points

```
INPUT LAYER:
├─ Project Intake (scope, geography, sector, timeline)
├─ Geographic Boundaries (administrative/environmental zones)
├─ Regulatory Framework (applicable laws, licensing requirements)
├─ Opponent/Ally Signals (if known from scoping)
└─ Historical Precedents (similar past projects)

PROCESSING (Manta 21):
├─ Identify Stakeholder Universe (gov, private, civil society, media)
├─ Score Stakeholder Power (formal authority, financial leverage, veto points)
├─ Map Interest Alignment (cost-benefit per stakeholder, constraints)
├─ Identify Coalition Dynamics (allies, opposition, swing voters)
├─ Assess Negotiability (where flexibility exists)
└─ Design Engagement Sequence (phase-gate approach)

OUTPUT LAYER:
├─ Stakeholder Matrix (name, role, power, interest, communication lead)
├─ Negotiation Roadmap (engagement phases, decision gates, timeline)
├─ Communication Templates (sector-customized talking points)
├─ Risk Dashboard (opposition intensity, veto player checklist)
└─ Executive Summary (1-page recommendation)
```

### 2.4 Model Tier Rationale

**Sonnet (primary):** Qualitative analysis, historical pattern recognition, strategic language generation, multi-stakeholder synthesis.

**Fallback to Opus:** Complex coalition scenarios, adversarial negotiation simulation, legal/regulatory edge cases.

**Haiku (not used):** Insufficient nuance for political economy; risk of oversimplification in stakeholder interests.

---

## III. STAKEHOLDER PERSONAS (5 Archetypes)

### Persona 1: **Regulatory Authority / Gatekeeper**

**Profile:**
- **Example:** ANEEL director (transmission line), ANAC (airport), ANTAQ (port)
- **Power:** Formal authority to approve/deny project, set terms of operation
- **Interest:** Regulatory compliance, sectoral development targets, political reputation
- **Constraints:** Public law, transparent decision-making, political pressure from elected officials

**Negotiation Stance:**
- Seeks: Clear technical documentation, alignment with national policy (PAC, decarbonization, etc.)
- Risks: Regulatory capture accusations, judicial challenges from opposition
- Engagement: Early consultation, formal written positions, technical working groups

**Communication Template:**
```
"[Project] aligns with [sector target from national plan].
We propose [technical solution] to address [regulatory concern].
Timeline: [formal process milestones]. Contact: [technical lead]."
```

**Case Example:** ANEEL transmission line approval (see Section V, Case 1)

---

### Persona 2: **Affected Landowner / Property Rights Claimant**

**Profile:**
- **Example:** Small farmer along pipeline corridor, indigenous land claim, riparian land owner
- **Power:** Asymmetric — low formal authority but high veto power (legal delays, media campaigns)
- **Interest:** Property preservation, fair compensation, project delay/cancellation if terms unfavorable
- **Constraints:** Limited legal resources, vulnerability to developer pressure, media vulnerability (reputational)

**Negotiation Stance:**
- Seeks: Fair-market valuation, relocation assistance, ongoing employment/partnership
- Risks: Legal challenges, social movement coalition, media coverage ("David vs. Goliath")
- Engagement: Early identification, needs assessment, transparent compensation mechanism

**Communication Template:**
```
"We recognize your [property right/livelihood] at risk.
Our offer: [compensation package] + [relocation/employment assistance] + [ongoing partnership if applicable].
Independent appraisal: [third-party valuation]. Timeline: [negotiation phases]."
```

**Case Example:** Porto concession landowner negotiations (see Section V, Case 2)

---

### Persona 3: **Environmental / Civil Society Advocate**

**Profile:**
- **Example:** NGO (APIB for indigenous rights, SOS Mata Atlântica for conservation), consumer council (ETA), labor union
- **Power:** Medium — legal standing for litigation, media amplification, coalition-building with other NGOs
- **Interest:** Environmental protection, social justice, democratic participation in decision-making
- **Constraints:** Funding scarcity, reliance on media/political allies, limited technical resources

**Negotiation Stance:**
- Seeks: Environmental impact mitigation, transparency, community participation in design/monitoring
- Risks: Project delay via injunction, reputational damage (ESG/sustainability concerns)
- Engagement: Early consultation, environmental steering committee, offset/mitigation packages

**Communication Template:**
```
"We share commitment to [sector decarbonization/social inclusion].
Project [environmental concern] can be mitigated via [offset/design change].
Propose: Environmental monitoring committee with NGO representation.
Timeline: [review period]. Contact: [community liaison]."
```

**Case Example:** Saneamento ETA consumer council (see Section V, Case 3)

---

### Persona 4: **Competing Commercial Operator**

**Profile:**
- **Example:** Incumbent utility company (energy, water), competing port terminal operator, rival airline/airport
- **Power:** High — market leverage, technical expertise, political connections, capital for lobbying
- **Interest:** Market share protection, access to contracts, technology standards favorable to incumbent
- **Constraints:** Regulatory oversight, antitrust exposure, customer retention pressures

**Negotiation Stance:**
- Seeks: Contractual terms favoring scale, interoperability standards, limited new competition
- Risks: Antitrust investigation, reputational damage (anti-competitive behavior), regulatory penalty
- Engagement: Bilateral negotiations, industry association coordination, regulatory dialogue

**Communication Template:**
```
"Competitor's proposal raises [antitrust/technical/operational] concern.
We propose [alternative structure] that serves market needs while preserving competition.
Industry precedent: [comparable transaction]. Technical compatibility: [standard]."
```

**Case Example:** Transmission operator (S.E.) opposed to independent line (see Section V, Case 1)

---

### Persona 5: **Political Decision-Maker / Elected Official**

**Profile:**
- **Example:** State governor, municipal mayor, federal deputy, city councilor
- **Power:** High — electoral legitimacy, budget allocation, regulatory approval, constituent pressure
- **Interest:** Electoral success, constituent satisfaction, political alignment, sectoral development
- **Constraints:** Re-election cycle, opposing party pressure, local vs. national priorities conflict

**Negotiation Stance:**
- Seeks: Visible economic benefits (jobs, tax revenue), minimal social conflict, political credit
- Risks: Opposition campaign ("sold out to corporations"), community backlash, electoral loss
- Engagement: Transparent public process, benefit-sharing agreements, political cover (bipartisan support)

**Communication Template:**
```
"Project brings [X jobs, Y tax revenue, Z infrastructure] to [municipality].
Public process: [transparent milestones]. Local benefit: [education jobs, local content, apprenticeships].
Political support: [cross-party backing, governor endorsement if applicable]."
```

**Case Example:** Municipal permitting for transmission line (see Section V, Case 1)

---

## IV. NEGOTIATION FRAMEWORK

### 4.1 Five-Phase Engagement Model

#### **PHASE 1: STAKEHOLDER MAPPING (Weeks 1-3)**

**Objective:** Complete actor census, power analysis, interest baseline.

**Activities:**
1. Conduct stakeholder universe scan
   - Identify all formal stakeholders (regulators, license-holders, concessionaires)
   - Identify informal stakeholders (NGOs, community leaders, media)
   - Use SPU/B3/TSE data to map property interests, corporate control, political affiliations
   
2. Assess each stakeholder's power base
   - Formal authority (regulatory veto, licensing control, budgetary authority)
   - Market leverage (market share, control of critical infrastructure)
   - Social power (community mobilization, media reach, international pressure)
   
3. Initial interest assessment
   - Survey regulatory positions from existing filings
   - Review past press statements from likely allies/opposition
   - Identify constraints that may limit negotiability

**Deliverable:** Stakeholder Universe Map (50-100 actors), Power Index Ranking

**Risk:** Incomplete actor identification → missed coalition blockers. **Mitigation:** Cross-check multiple data sources, interview project team for blind spots.

---

#### **PHASE 2: COALITION MAPPING (Weeks 4-6)**

**Objective:** Identify natural coalitions, veto players, swing voters, critical dependencies.

**Activities:**
1. Cluster stakeholders by interest alignment
   - Pro-project bloc (developer, certain regulators, businesses seeking investment)
   - Opposition bloc (environmental NGOs, property-rights groups, competing operators)
   - Swing voters (unaligned elected officials, media, undecided regulators)
   
2. Identify veto players
   - Which stakeholders can unilaterally block project via legal challenge, regulatory refusal, or media campaign?
   - What is their credibility/track record?
   
3. Historical precedent analysis
   - Similar past projects: Which coalitions formed? Which actors switched sides?
   - Success factors: How did winning coalitions manage opposition?

**Deliverable:** Coalition Landscape Matrix, Veto Player Checklist, Historical Playbook

**Risk:** Oversimplification (assuming static coalition). **Mitigation:** Plan for coalition evolution; identify trigger points (e.g., environmental impact study release) where positions may shift.

---

#### **PHASE 3: NEGOTIATION SEQUENCING (Weeks 7-10)**

**Objective:** Design engagement order that builds momentum, isolates hard blockers, neutralizes swing voters.

**Activities:**
1. Sequence stakeholder engagement by negotiability + impact
   - **First:** High-impact, high-negotiability stakeholders (e.g., state environmental agency seeking credible mitigation)
   - **Second:** Medium-impact stakeholders, build momentum
   - **Third:** Hard blockers (engage late, with full coalition aligned against them)
   
2. Identify decision gates + leverage points
   - Where does regulatory approval cascade (e.g., municipal → state → federal)?
   - Where can early wins create path dependencies (e.g., environmental approval unlocks political support)?
   
3. Design communication sequencing
   - Phase-specific messaging (e.g., infrastructure benefits in Phase 1, environmental mitigation in Phase 2)
   - Identify communication lead for each stakeholder group
   - Pre-brief allied stakeholders before joint meetings

**Deliverable:** Negotiation Roadmap (timeline, stakeholder sequence, decision gates), Communication Lead Assignments

**Risk:** Uncontrolled message leakage → opposition pre-empts engagement. **Mitigation:** Strict confidentiality protocols, staggered disclosure, legal review of positions before release.

---

#### **PHASE 4: TARGETED ENGAGEMENT (Weeks 11-24)**

**Objective:** Execute negotiation roadmap, secure written positions, neutralize opposition.

**Activities:**
1. Bilateral negotiations with key stakeholders
   - Regulatory authorities: Technical working groups, impact assessment co-design
   - Landowners: Appraisal process, relocation assistance, profit-sharing (if applicable)
   - NGOs: Environmental steering committee, offset packages, monitoring protocols
   - Competitors: Regulatory dialogue, interoperability agreements
   
2. Coalition management
   - Brief pro-project stakeholders before opposition engagement
   - Identify swing voters early, design customized offers
   - Isolate hard blockers (reduce negotiation bandwidth on lost causes)
   
3. Public engagement (if applicable)
   - Transparent project webpage, community meetings, media engagement
   - Respond to opposition claims with factual rebuttals

**Deliverable:** Stakeholder Agreements (written positions), Coalition Stability Index, Opposition Risk Dashboard

**Risk:** Bilateral agreements conflict at integration point. **Mitigation:** Lawyer review of all written positions, master agreement (umbrella document reconciling individual commitments).

---

#### **PHASE 5: FORMALIZATION & EXECUTION (Weeks 25-52)**

**Objective:** Secure formal approvals, execute agreements, manage post-approval opposition.

**Activities:**
1. Formal regulatory approvals
   - Submit consolidated applications with all stakeholder support letters
   - Prepare for judicial review / regulatory appeals
   
2. Agreement execution
   - Final compensation packages, relocation assistance, partnership agreements
   - Bond/escrow arrangements (if applicable)
   
3. Post-approval opposition management
   - Monitor court challenges, media campaigns
   - Sustain coalition momentum (briefs in litigation, regulatory comment periods)

**Deliverable:** Regulatory Approvals, Executed Agreements, Judicial Defense Strategy

---

### 4.2 Negotiation Tactics by Stakeholder Type

| Stakeholder | Opening Position | Concession Sequence | Red Lines | Communication Frequency |
|------------|------------------|-------------------|-----------|-----------------------|
| **Regulator** | Demand full technical spec | Clarifications on technical detail → design modifications → timeline extension | Integrity of approval process, compliance with law | Weekly technical meetings; monthly executive updates |
| **Landowner** | Demand relocation + premium | Market appraisal → relocation bonus → ongoing employment/profit-sharing | Homestead preservation (if culturally significant) | Bi-weekly; final agreement 30-day period |
| **NGO** | Demand project halt | Environmental impact mitigation → monitoring committee → offset funding | Protected area boundary | Monthly; escalate to mediation if no movement |
| **Competitor** | Demand market concessions (price cap, unbundling) | Technical interoperability → industry standard adoption → limited capacity sharing | Margin compression beyond X% | Quarterly industry meetings |
| **Politician** | Demand visible local benefit | Job commitments → apprenticeship program → local content requirements | Fiscal impact on municipal budget | Quarterly; pre-election surge to 2-3x frequency |

---

## V. CASE STUDIES (3 Infrastructure Scenarios)

### CASE 1: Transmission Line Permitting (LT 500 kV, São Paulo → Mato Grosso)

**Project Context:**
- **Scope:** 1,200 km high-voltage transmission line to evacuate wind/solar generation from Mato Grosso to São Paulo load center
- **Regulatory:** ANEEL approval required; state and municipal environmental licenses; indigenous land easement (if applicable)
- **Timeline:** 24 months (scoping) + 12 months (construction)
- **Estimated Value:** USD 800 million
- **Developer:** Transmission company (consortium of utilities + infrastructure fund)

#### **PHASE 1: Stakeholder Mapping**

**Stakeholder Universe (37 actors identified):**

| Group | # | Key Actors | Power Index |
|-------|---|-----------|-------------|
| Federal Regulator | 2 | ANEEL (3/5), EPE (2/5) | High |
| State/Municipal | 6 | SP State Env. Sec. (3/5), Govt. Paraná (2/5), Municipal mayors (1/5 each) | Medium |
| Property Rights | 12 | Large landowners (3/5), Farmer associations (2/5), indigenous communities (4/5) | Medium-High |
| Environmental | 8 | APIB (3/5), Greenpeace (2/5), local conservation NGOs (1/5 each) | Medium |
| Competing Utilities | 4 | Incumbent transmission operator (4/5), Distributor SP (3/5), generators (2/5) | High |
| Media / Political | 5 | State deputies (2/5), journalists (1/5), local influencers (1/5) | Low-Medium |

**Power Analysis:**
- **Veto Players:** ANEEL (regulatory approval), indigenous communities (if land involved, constitutional protection), SP state environmental secretary
- **Critical Allies:** EPE (state electricity planner, needs this line for grid stability), large landowners (if compensated, won't organize opposition)
- **Swing Voters:** Incumbent transmission operator (could support if offered interoperability concession), state deputies (need to see local jobs)

#### **PHASE 2: Coalition Mapping**

**Pro-Project Coalition:**
- ANEEL (priority: grid stability + renewable integration)
- Renewable generators (eager to evacuate power)
- Infrastructure investors (seeking long-term contracted returns)
- Federal government (PAC-aligned, decarbonization target)
- **Coalition Strength:** Stable (aligned financial incentives)

**Opposition Coalition (Initial):**
- Incumbent transmission operator (market share threat)
- APIB (indigenous land protection)
- Local landowners concerned about easement (pre-compensation negotiations)
- **Coalition Strength:** Fragile (different interests could be separated)

**Swing Voters:**
- State environmental agency (could be neutral if environmental protocol strong)
- Municipal governments (want jobs + tax base, but fear land acquisition costs)

**Historical Precedent:** 2015 Madeira Transmission Line (LT 2,100 km, Rondônia → São Paulo)
- **Success factors:** Early indigenous consultation (2 years), environmental monitoring committee, local content requirement (70% in operations phase)
- **Opposition:** APIB (lasted 18 months, resolved via revenue-sharing), farmers (resolved via negotiated easement prices 20% above market)
- **Lesson:** Indigenous veto can be neutralized with revenue-sharing; farmer opposition manageable with fair compensation

#### **PHASE 3: Negotiation Sequencing**

**Week 1-4: Regulatory Alignment**
- ANEEL technical working group (establish technical baseline, timeline)
- EPE coordination (confirm grid need, timeline)
- **Objective:** Secure regulatory support in writing

**Week 5-8: Indigenous Consultation**
- APIB negotiation (early engagement, revenue-sharing offer)
- Affected communities (identify direct easement holders, negotiate compensation)
- **Objective:** Neutralize strongest opposition via precedent-based revenue model

**Week 9-12: Environmental Mitigation**
- State environmental agency (impact assessment, monitoring protocol)
- Conservation NGOs (offset opportunities, environmental steering committee)
- **Objective:** Convert opposition to neutral/supportive via credible mitigation

**Week 13-18: Property Rights Negotiation**
- Farmer associations (easement compensation, below-ground preservation rights)
- Large landowners (individual negotiations, profit-sharing for easement access)
- **Objective:** Secure written letters of support from 90%+ of affected landowners

**Week 19-24: Political & Market**
- Municipal governments (local benefit agreements, apprenticeships)
- Incumbent operator (interoperability concession, capacity-sharing)
- State deputies (public announcement of project)
- **Objective:** Final coalition lock-in before regulatory filing

#### **PHASE 4: Targeted Engagement Outcomes**

**ANEEL Technical Working Group:**
- Outcome: Baseline design approved; environmental protocol agreed
- Risk managed: Regulatory uncertainty → eliminated via early co-design

**Indigenous Communities (APIB):**
- Offer: 0.5% of annual transmission revenue for 30 years + community development fund (USD 5M/year)
- Precedent: Madeira model, indexed to inflation
- Outcome: APIB letter of support (written Sept. 2025)
- Risk managed: Veto power neutralized

**Environmental NGOs:**
- Offer: Environmental Steering Committee (quarterly meetings, real-time monitoring, halt provision if thresholds exceeded)
- Offset: 500 hectares of Amazon forest protection (fund indigenous land reserve expansion)
- Outcome: Greenpeace neutral stance, local NGOs supportive
- Risk managed: Media campaign risk → eliminated

**Farmer Associations:**
- Offer: Easement compensation 25% above state average + agricultural preservation covenants
- Benefit: 200 construction jobs + 30 permanent operations jobs in region
- Outcome: Farmer association endorsement letter + individual farmer agreements
- Risk managed: Grassroots opposition → eliminated

**Incumbent Transmission Operator:**
- Offer: Preferential access to transmission capacity (100 MW reserved at discounted tariff)
- Benefit: Transition pathway as grid modernizes
- Outcome: Neutral stance, no opposition litigation
- Risk managed: Competitor blocking → eliminated

**State Deputies & Municipal Governments:**
- Offer: Local employment target (60% of construction workforce from municipalities), apprenticeship program (50 youth/year × 3 years)
- Benefit: Visible jobs + skills training, tax base expansion
- Outcome: Public announcement, political endorsement
- Risk managed: Electoral pressure → neutralized

#### **PHASE 5: Regulatory Approval & Execution**

**Timeline:**
- Month 12: ANEEL formal approval (based on consolidated stakeholder support)
- Month 12-18: Environmental licensing (state + federal)
- Month 18-24: Land acquisition + easement execution
- Month 24+: Construction

**Risk Dashboard at Approval:**
- Regulatory approval risk: **LOW** (coalition support de-risked regulatory uncertainty)
- Property rights risk: **LOW** (95% of landowners signed easement letters)
- Environmental litigation risk: **LOW** (environmental committee in place, NGO endorsement)
- Indigenous litigation risk: **LOW** (revenue-sharing agreement precedent-based)
- Competing operator risk: **LOW** (interoperability concession attractive to incumbent)

**Overall Project Risk:** Reduced from **MEDIUM** (pre-negotiation) to **LOW** via systematic coalition management.

---

### CASE 2: Port Concession (Multipurpose Terminal, Rio Grande, Brazil)

**Project Context:**
- **Scope:** Greenfield multipurpose terminal (containers, breakbulk, liquid bulk) at Porto do Rio Grande, southern Brazil
- **Regulatory:** ANTAQ (federal concession), municipal permit, labor agreement
- **Timeline:** 36 months (concession preparation) + 60 months (construction)
- **Estimated Value:** USD 1.2 billion investment, 40-year concession
- **Developer:** International port operator consortium

#### **Stakeholder Mapping Highlights**

**Veto Players:**
1. **ANTAQ** (federal authority) — Must approve concession terms, environmental compliance
2. **Municipal Government (Rio Grande)** — Land availability, labor laws, local content
3. **Existing Port Authority (SUEZ/Local)** — Operational coordination, labor force
4. **Port Workers Union** — Labor agreement, job security, union recognition
5. **Fishing Communities** — Environmental impact on fish stocks, coastal livelihoods

**Power Ranking:**
| Stakeholder | Power | Interest | Negotiability |
|------------|-------|---------|---------------|
| ANTAQ | 5/5 | Sectoral growth, fiscal returns | High (standardized concession terms) |
| Municipal Govt | 4/5 | Tax revenue, jobs, urban development | High (benefit-sharing agreements) |
| Port Authority | 3/5 | Operational coordination | Medium (institutional turf) |
| Workers Union | 3/5 | Job security, wages, union recognition | Medium (precedent-based labor terms) |
| Fishing Communities | 2/5 | Environmental protection, coastal access | Medium-High (reputational/legal risk) |
| NGOs (environmental) | 2/5 | Marine ecosystem protection | Medium (mitigation via environmental plan) |

#### **Coalition Analysis**

**Pro-Development:**
- ANTAQ (sectoral growth, foreign direct investment)
- Port operator (market opportunity)
- Municipal government (tax revenue + employment)
- Business associations (shipper/logistics demand)

**Opposition/Swing:**
- Port workers union (employment concerns, demanding union security)
- Fishing communities (livelihoods at risk)
- Environmental NGOs (marine habitat, dredging impact)

**Historical Precedent:** Paranaguá Multipurpose Terminal (2010-2015)
- **Opposition:** Fishing communities + environmental NGOs (9-month campaign)
- **Resolution:** Environmental Steering Committee, seasonal dredging protocol, USD 3M marine ecosystem restoration fund
- **Workers:** 80% of new jobs reserved for local unions, union recognition agreement

#### **Engagement Strategy**

**PHASE 1-2: Government & Labor Alignment (Months 1-6)**
- ANTAQ concession dialogue (standardized terms, 40-year model)
- Municipal government (local benefit agreement, land provision)
- Port workers union (employment guarantee letter, wage parity with comparable terminals)

**PHASE 3: Environmental Mitigation (Months 7-12)**
- Fishing community consultation (livelihood impact assessment)
- Environmental NGOs (marine protection protocol, restoration fund)
- Environmental impact statement co-design

**PHASE 4: Tender Preparation (Months 13-24)**
- Formal stakeholder agreements executed
- Union labor contract signed (model: Paranaguá precedent)
- Municipal zoning/permits finalized

**PHASE 5: Concession Execution (Months 25-36+)**
- ANTAQ formal approval
- Concession agreement signed
- Construction begins

#### **Negotiation Outcomes (Projected)**

**Municipal Government:**
- Offer: 5% of concessionaire gross revenue (estimated USD 15M/year at full capacity) + 300 permanent construction jobs + apprenticeships
- Outcome: Municipal endorsement, land provision secured

**Port Workers Union:**
- Offer: 85% of new permanent jobs reserved for local union workers + wage parity with Porto de Santos + union recognition agreement
- Outcome: Union support letter, labor peace agreement

**Fishing Communities:**
- Offer: USD 5M marine ecosystem restoration fund + seasonal dredging protocol (June-Nov only, preserve breeding season) + fisherman hiring preference (100 apprenticeships/year)
- Outcome: Community letter of support, environmental monitoring seat

**Environmental NGOs:**
- Offer: Environmental Steering Committee (quarterly reviews), science-based monitoring, marine reserve expansion (2,000 hectares, state-funded)
- Outcome: Neutral-to-supportive stance, no litigation

**Risk Reduction:**
- Labor conflict risk: **MEDIUM** → **LOW** (union agreement in hand)
- Environmental litigation: **MEDIUM** → **LOW** (mitigation plan approved by stakeholders)
- Municipal obstruction: **LOW** → **MINIMAL** (benefit-sharing attractive)

---

### CASE 3: Water Utility (ETA — Estação de Tratamento de Água) Expansion, São Paulo Metro

**Project Context:**
- **Scope:** ETA expansion (capacity +30%) serving metropolitan São Paulo, 20M people
- **Regulatory:** SABESP (state utility), municipal coordination, consumer council (ETA)
- **Timeline:** 24 months (planning) + 30 months (construction)
- **Estimated Value:** USD 300 million
- **Developer:** SABESP (state water utility)

#### **Stakeholder Mapping**

**Unique Complexity:** High consumer salience (water is essential service), large consumer council with legal standing, environmental protection groups (water source protection).

**Veto Players:**
1. **Municipal Government** — Land provision, local environmental permit
2. **Consumer Council (ETA)** — Legal standing to challenge rate increases, consumer representation
3. **Environmental NGOs** — Water source protection (Cantareira system), aquifer recharge
4. **Civil Society** — Community mobilization (water price sensitive for low-income populations)

#### **Phase 2: Coalition Dynamics**

**Pro-Expansion:**
- SABESP (operational necessity, regulatory pressure to increase coverage)
- State government (PAC-aligned infrastructure)
- Federal regulator (ANA — National Water Agency, supports supply expansion)

**Opposition:**
- Consumer council (demands rate cap, opposes cost pass-through to consumers)
- Environmental NGOs (prefer water conservation over expansion)
- Low-income community groups (fear price increase)

**Swing Voters:**
- Municipal government (wants water security but fears political backlash on rates)
- Engineering associations (technology debate: expand capacity vs. reduce demand via conservation)

#### **Historical Precedent: Cantareira Expansion (2012-2018)**

**Challenge:** Expanding water system while maintaining affordability for 20M people + environmental protection.

**Resolution:**
- Rate structure: Tiered pricing (lowest tier subsidized for low-income households, higher tiers full cost)
- Environmental offset: Cantareira watershed protection fund (USD 50M, state budget)
- Consumer engagement: ETA quarterly meetings, transparent cost accounting
- Outcome: Consumer council supported expansion after rate tiering secured

**Lesson:** Rate design is **key lever** for consumer council buy-in; environmental protection fund neutralizes NGO opposition.

#### **Engagement Strategy for New ETA**

**PHASE 1-2: Consumer & Environmental Alignment (Months 1-6)**

**Consumer Council Engagement:**
- Demand: Rate structure maintains affordability for low-income households
- Offer: Tiered rate design (bottom tier subsidized, cost recovery from higher consumption users)
- Mechanism: Transparent rate-setting process (quarterly council reviews)
- Outcome: Consumer council endorsement of expansion (conditional on rate tiering)

**Environmental NGO Engagement:**
- Demand: Water source protection, reduced demand via conservation program
- Offer: Conservation program budget (USD 10M over 5 years), watershed protection fund (USD 25M state-funded)
- Mechanism: Environmental Steering Committee, water saving targets (5% per capita by year 5)
- Outcome: Environmental NGO neutral-to-supportive, conservation targets built into SABESP KPIs

**PHASE 3-4: Implementation**

**Outcomes (Projected):**
- ETA expansion approved by consumer council + regulators
- Rate structure protects low-income households (bottom 40% price increase capped at 2%/year)
- Water conservation program targets met (5% per capita savings by 2030)
- Environmental fund supports Cantareira watershed restoration
- Overall: Risk of consumer strike/political backlash → eliminated via rate design + conservation co-investment

**Risk Dashboard:**
- Consumer council opposition: **MEDIUM** → **LOW** (rate tiering removes financial burden from vulnerable populations)
- Environmental litigation: **MEDIUM** → **LOW** (watershed protection fund + conservation targets aligned)
- Political backlash (pricing): **HIGH** → **MEDIUM** (tiered structure, conservation visibility, transparent process)

---

## VI. IMPLEMENTATION ROADMAP

### 6.1 Manta 21 Deployment

**Sprint 1 (Weeks 1-2):** Agent framework + RAG integration
- [ ] Integrate TSE political data API (party affiliations, campaign finance)
- [ ] Integrate B3 corporate network data (board interlocks, ownership structures)
- [ ] Build local RAG on past 50 Manta projects (lessons learned, stakeholder patterns)

**Sprint 2 (Weeks 3-4):** Stakeholder mapping engine
- [ ] Automated stakeholder universe scan (regulatory + media sources)
- [ ] Power index scoring model (authority + leverage + social reach)
- [ ] Coalition detection algorithm (interest clustering)

**Sprint 3 (Weeks 5-6):** Negotiation planning tools
- [ ] Engagement sequencing logic (negotiability + impact ranking)
- [ ] Communication template library (sector-customized messaging)
- [ ] Decision gate framework (regulatory milestones, triggering events)

**Sprint 4 (Weeks 7-8):** Risk dashboard + execution support
- [ ] Risk heatmap visualization (opposition intensity by stakeholder)
- [ ] Veto player checklist (ongoing compliance checks)
- [ ] Judicial defense strategy templates (litigation prep)

### 6.2 Integration with Manta Ecosystem

| Component | Integration Point | Data Flow |
|-----------|------------------|-----------|
| **Maestro (Manta 00)** | Router: Projects involving stakeholder complexity → route to Manta 21 | Project scope + geography |
| **Manta 03-S* (Vertical Agents)** | Support: Manta 21 provides stakeholder roadmap for each sector agent | Sector-specific regulatory contacts |
| **Supabase RAG** | Historical: Project outcomes, stakeholder behaviors, negotiation precedents | Query: sector + geography + issue type |
| **SharePoint** | Input: Stakeholder contact database, project histories | Output: Stakeholder matrix, engagement roadmap |
| **Portal IA** | User interface: Project teams access Manta 21 via portal intake | Project intake form (scope, geography, timeline) |

### 6.3 Validation & QA

**Pre-Launch Testing:**
- [ ] Retro-analysis: Apply Manta 21 to 5 past Manta projects, verify stakeholder identification accuracy
- [ ] Stakeholder Persona Testing: Validate 5 personas against actual project stakeholders (interview 20 real stakeholders)
- [ ] Engagement Roadmap Validation: Compare Manta 21 sequencing vs. actual timeline from past projects
- [ ] Communication Template Testing: Have experienced project leads rate template quality (usefulness, sector fit)

**Success Criteria:**
- Stakeholder identification accuracy: ≥90% (matches actual actors involved)
- Power index ranking correlation: ≥0.85 (ranked actors correlate with actual decision influence)
- Engagement roadmap quality: ≥4/5 rating from experienced PM team
- Risk dashboard predictability: ≥80% of flagged veto players actually intervened

---

## VII. DELIVERABLES & FORMATS

### Output Suite (per project engagement):

1. **Stakeholder Universe Map** (visual network diagram + spreadsheet)
   - 50-150 actors, power index, interest alignment, communication lead
   
2. **Coalition Landscape Matrix** (strategic narrative + visual)
   - Pro/anti/swing blocs, veto players, leverage points, coalition stability score
   
3. **Negotiation Roadmap** (timeline + decision gates)
   - 5-phase plan with stakeholder sequence, engagement tactics, contingencies
   
4. **Communication Templates** (sector-customized language bank)
   - 20-30 templates (regulatory, landowner, NGO, competitor, politician)
   
5. **Risk Dashboard** (heatmap + mitigation action plan)
   - Opposition intensity by stakeholder, veto player checklist, judicial defense strategy

---

## VIII. SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Stakeholder Buy-In** | ≥85% of identified stakeholders provide written support | Signed letters / formal positions |
| **Negotiation Time** | Reduce from 36 to 24 months via front-loaded engagement | Project timeline comparison |
| **Litigation Risk** | ≤2 major injunctions filed post-approval | Court filings count |
| **Cost Overruns** | Reduce delay-related costs by ≥30% | Cost baseline vs. actual |
| **Environmental/Social Compliance** | 100% of EIS + stakeholder agreements honored | Audit trail + monitoring reports |

---

## IX. GOVERNANCE & ESCALATION

**Manta 21 Governance:**
- **Owner:** Manta Political Economy & Stakeholder Practice Lead
- **Escalation:** If veto player intransigent → escalate to project sponsor + chief legal officer
- **Periodic Review:** Coalition stability check every 6 weeks during active engagement
- **Post-Mortem:** After regulatory approval or project termination, capture lessons to RAG for future projects

---

## X. APPENDIX: RAG SOURCES BY SECTOR

### Saneamento (Water/Wastewater)
- SNIS (Sistema Nacional de Informações sobre Saneamento)
- NBR 12.211-12.218 (design standards)
- Lei 14.026/2020 (universal sanitation law)
- ANA (National Water Agency) regulatory decisions
- Past ETA conflicts (precedent library)

### Energia (Energy)
- ANEEL regulatory dockets (transmission licensing)
- EPE-R1/R5 documents (grid expansion needs)
- B3 balance sheets (competing utilities)
- Leilão reports (transmission auction histories)

### Portos (Ports)
- ANTAQ concession terms (comparative benchmark)
- PIANC port design standards
- Past concessionaire labor agreements
- Port worker union positions (historical)

### Rodovias (Highways)
- DNIT stakeholder databases
- Farmer associations (landowner contacts)
- SICRO cost databases (economic impact calculations)
- Past toll negotiation histories

---

**End of Agent Design Specification**

---

**Document Control:**
- **Version:** 1.0.0
- **Date:** 2026-08-02
- **Status:** Ready for Implementation Review
- **Next Review:** Post-first 3 pilot projects (Q4 2026)
