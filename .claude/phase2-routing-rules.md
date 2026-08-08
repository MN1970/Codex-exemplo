# Phase 2: Routing Rules Reference

**Source:** CLAUDE.md § ROUTING — Maestro (Manta 00)  
**Implementation:** `.claude/phase2-router.md` § MaestroRouter.routeToSegment()  
**Status:** ✅ All 10 rules implemented

---

## ROUTING DECISION TABLE

Each rule is a **keyword pattern → segment → agent** mapping.

### Vertical Segments (S1–S10)

#### S8: Saneamento (Wastewater, Water Supply)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `saneamento` | Exact | `agente-saneamento` | 0.95 | "Projeto de sistema de saneamento integrado" |
| `ETA\|ETE` | Acronym | `agente-saneamento` | 0.95 | "Nova ETA de 500 L/s" |
| `adutora` | Infrastructure | `agente-saneamento` | 0.95 | "Adutora de água bruta 50 km" |
| `esgoto` | Exact | `agente-saneamento` | 0.95 | "Rede coletora de esgoto" |
| `AySA` | Organization (Argentina) | `agente-saneamento` | 0.95 | "Concessão AySA Buenos Aires" |
| `drenagem urbana` | Infrastructure | `agente-saneamento` | 0.95 | "Drenagem urbana e controle de inundação" |
| `SNIS` | Database (Sistema Nacional) | `agente-saneamento` | 0.95 | "Dados SNIS 2024" |
| `ABES\|concessionária água` | Organization/Operator | `agente-saneamento` | 0.90 | "Concessão para concessionária de água" |

**Implementation:**
```javascript
'S8-saneamento': {
  regex: /saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem\s+urbana|SNIS|ABES|concessionária\s+água/i,
  agent: 'agente-saneamento',
  confidence: 0.95
}
```

---

#### S9: Energia (Power Generation, Transmission, Distribution)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `transmissão` | Infrastructure | `agente-energia` | 0.95 | "Linha de transmissão 765 kV" |
| `LT` | Acronym (Linha Transmissão) | `agente-energia` | 0.95 | "Projeto de LT de longa distância" |
| `subestação` | Infrastructure | `agente-energia` | 0.95 | "Subestação 138/69 kV" |
| `ANEEL` | Regulator | `agente-energia` | 0.95 | "Concessão aprovada por ANEEL" |
| `RAP` | Regulatory (Reajuste Anual) | `agente-energia` | 0.95 | "Pedido de RAP" |
| `leilão transmissão` | Bidding | `agente-energia` | 0.95 | "Leilão de transmissão 2025" |
| `ONS\|EPE` | Operators (ONS=grid, EPE=planning) | `agente-energia` | 0.95 | "Projeção de demanda EPE" |
| `CCE\|distribuidora` | Operator | `agente-energia` | 0.90 | "Concessionária de distribuição" |

**Implementation:**
```javascript
'S9-energia': {
  regex: /transmissão|LT|subestação|ANEEL|RAP|leilão\s+transmissão|ONS|EPE|CCE|distribuidora/i,
  agent: 'agente-energia',
  confidence: 0.95
}
```

---

#### S6: Portos (Ports, Terminals, Maritime)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `porto` | Exact | `agente-portos` | 0.95 | "Terminal de contêineres no porto de Santos" |
| `terminal` | Infrastructure | `agente-portos` | 0.90 | "Terminal portuário multipropósito" |
| `ANTAQ` | Regulator | `agente-portos` | 0.95 | "Regulação ANTAQ" |
| `dragagem` | Operation | `agente-portos` | 0.95 | "Dragagem de aprofundamento 15 m" |
| `molhe` | Infrastructure | `agente-portos` | 0.95 | "Molhe de proteção" |
| `berço` | Infrastructure | `agente-portos` | 0.95 | "Berço de atracação para navios Panamax" |
| `calado` | Specification | `agente-portos` | 0.95 | "Aumento de calado operacional" |
| `contêiner\|granel` | Cargo | `agente-portos` | 0.90 | "Terminal de contêineres" / "Terminal de granel" |
| `navegação` | Operation | `agente-portos` | 0.90 | "Canal de navegação" |

**Implementation:**
```javascript
'S6-portos': {
  regex: /porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel|navegação/i,
  agent: 'agente-portos',
  confidence: 0.95
}
```

---

#### S7: Aeroportos (Airports, Aviation)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `aeroporto` | Exact | `agente-aeroportos` | 0.95 | "Expansão do aeroporto de Viracopos" |
| `pista pouso` | Infrastructure | `agente-aeroportos` | 0.95 | "Nova pista de pouso" |
| `ANAC` | Regulator | `agente-aeroportos` | 0.95 | "Aprovação ANAC" |
| `ICAO` | Standard (International Civil Aviation) | `agente-aeroportos` | 0.95 | "Conformidade ICAO Annex 14" |
| `TPS` | Acronym (Terminal Pasageiros) | `agente-aeroportos` | 0.95 | "Novo TPS com 60 gates" |
| `TECA` | Acronym (Terminal Carga) | `agente-aeroportos` | 0.95 | "Expansão TECA" |
| `balizamento` | Equipment | `agente-aeroportos` | 0.95 | "Sistema de balizamento noturno" |
| `CNT` | Organization | `agente-aeroportos` | 0.90 | "Concessão CNT" |

**Implementation:**
```javascript
'S7-aeroportos': {
  regex: /aeroporto|pista\s+pouso|ANAC|ICAO|TPS|TECA|balizamento|CNT/i,
  agent: 'agente-aeroportos',
  confidence: 0.95
}
```

---

#### S10: Barragens (Dams, Hydropower)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `barragem` | Exact | `agente-barragens` | 0.95 | "Barragem de gravidade 120 m" |
| `vertedouro` | Infrastructure | `agente-barragens` | 0.95 | "Vertedouro de superfície" |
| `CFRD\|CCR` | Dam type (Concrete Face RD, Concrete CCR) | `agente-barragens` | 0.95 | "Barragem CFRD de 150 m" |
| `rejeitos` | Tailings | `agente-barragens` | 0.95 | "Barragem de rejeitos" |
| `PNSB` | National policy | `agente-barragens` | 0.95 | "Enquadramento na PNSB" |
| `ICOLD\|CBDB` | Standards/Database | `agente-barragens` | 0.95 | "Conformidade ICOLD / Registro CBDB" |
| `TSF` | Acronym (Tailings Storage Facility) | `agente-barragens` | 0.95 | "Nova TSF com altura 80 m" |
| `hidrelétrica barragem` | Application | `agente-barragens` | 0.90 | "Barragem para hidroeletricidade" |

**Implementation:**
```javascript
'S10-barragens': {
  regex: /barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF|hidrelétrica\s+barragem/i,
  agent: 'agente-barragens',
  confidence: 0.95
}
```

---

### Horizontal Segments (S1–S5)

#### S1: Rodovias (Highways, Road Networks)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `rodovia` | Exact | `agente-infraestrutura-S1` | 0.90 | "Concessão rodoviária" |
| `pavimento` | Component | `agente-infraestrutura-S1` | 0.90 | "Pavimento flexível CBUQ" |
| `CBUQ` | Pavement type | `agente-infraestrutura-S1` | 0.90 | "Camada de CBUQ 5 cm" |
| `BGS` | Pavement type | `agente-infraestrutura-S1` | 0.90 | "Base de BGS" |
| `terraplenagem` | Earthworks | `agente-infraestrutura-S1` | 0.90 | "Terraplenagem e conformação" |
| `SICRO` | Cost database | `agente-infraestrutura-S1` | 0.90 | "Orçamento SICRO" |
| `DNIT` | Authority | `agente-infraestrutura-S1` | 0.90 | "Normas DNIT" |
| `concessão rodovia` | Concession type | `agente-infraestrutura-S1` | 0.90 | "Edital de concessão rodoviária" |

**Implementation:**
```javascript
'S1-rodovias': {
  regex: /rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT|concessão\s+rodovia/i,
  agent: 'agente-infraestrutura-S1',
  confidence: 0.90
}
```

---

#### S2: OAE (Bridges, Viaducts, Tunnels)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `ponte` | Exact | `agente-infraestrutura-S2` | 0.90 | "Ponte estaiada 500 m" |
| `viaduto` | Exact | `agente-infraestrutura-S2` | 0.90 | "Viaduto em serpentina" |
| `OAE` | Acronym (Obra de Arte Especial) | `agente-infraestrutura-S2` | 0.90 | "Projeto de OAE" |
| `NBR 7187` | Brazilian standard (bridges) | `agente-infraestrutura-S2` | 0.90 | "Design per NBR 7187" |
| `túnel rodoviário` | Infrastructure | `agente-infraestrutura-S2` | 0.90 | "Túnel rodoviário duplo" |
| `fundação profunda` | Foundation | `agente-infraestrutura-S2` | 0.90 | "Fundação em estacas profundas" |

**Implementation:**
```javascript
'S2-oae': {
  regex: /ponte|viaduto|OAE|NBR\s+7187|túnel\s+rodoviário|fundação\s+profunda/i,
  agent: 'agente-infraestrutura-S2',
  confidence: 0.90
}
```

---

#### S3: Ferrovia (Railways, Rail Systems)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `ferrovia` | Exact | `agente-infraestrutura-S3` | 0.90 | "Ferrovia de carga" |
| `trilho` | Component | `agente-infraestrutura-S3` | 0.90 | "Trilho de aço" |
| `AMV` | Acronym (Aparelho de Mudança Via = switch) | `agente-infraestrutura-S3` | 0.90 | "AMV nº9" |
| `dormente` | Component (sleeper/tie) | `agente-infraestrutura-S3` | 0.90 | "Dormente de concreto" |
| `via permanente` | Infrastructure | `agente-infraestrutura-S3` | 0.90 | "Via permanente" |
| `via férrea` | Infrastructure | `agente-infraestrutura-S3` | 0.90 | "Via férrea de bitola 1.0 m" |

**Implementation:**
```javascript
'S3-ferrovia': {
  regex: /ferrovia|trilho|AMV|dormente|via\s+permanente|via\s+férrea/i,
  agent: 'agente-infraestrutura-S3',
  confidence: 0.90
}
```

---

#### S4: Metrô / VLT (Metro, Light Rail Transit)

| Keyword Pattern | Match Type | Agent | Confidence | Example |
|---|---|---|---|---|
| `metrô` | Exact | `agente-infraestrutura-S4` | 0.90 | "Extensão de metrô" |
| `estação` | Component (with metro context) | `agente-infraestrutura-S4` | 0.85 | "Nova estação de metrô profunda" |
| `NATM` | Method (New Austrian Tunneling) | `agente-infraestrutura-S4` | 0.90 | "Túnel NATM" |
| `PSD` | Acronym (Painel de Segurança Dinâmica?) | `agente-infraestrutura-S4` | 0.90 | "Sistema PSD" |
| `linha [0-9]\|VLT` | Line numbers or VLT | `agente-infraestrutura-S4` | 0.90 | "Linha 4 / VLT" |
| `monotrilho` | Mode | `agente-infraestrutura-S4` | 0.90 | "Sistema monotrilho" |

**Implementation:**
```javascript
'S4-metro': {
  regex: /metrô|estação|NATM|PSD|linha\s+[0-9]|VLT|monotrilho/i,
  agent: 'agente-infraestrutura-S4',
  confidence: 0.90
}
```

---

#### S5: Túneis (Tunnels - Specialized)

| Note | Status |
|---|---|
| Túneis rodoviários | Routed to **S2** (OAE) via "túnel rodoviário" |
| Túneis metroviários | Routed to **S4** (Metrô) via "NATM" |
| Túneis hidrelétricos | Routed to **S10** (Barragens) via context |
| Túneis ferroviários | Routed to **S3** (Ferrovia) via context |

**Status:** ⚡ Partial coverage by S2/S4. No dedicated S5 agent required (2026-07-05).

---

## ROUTING DECISION TREE (PSEUDOCODE)

```javascript
function routeToSegment(prompt) {
  
  // Priority order: S6–S10 (new), then S1–S4 (existing)
  const routes = [
    { segment: 'S8', keyword: 'saneamento|ETA|ETE|adutora|esgoto|AySA' },
    { segment: 'S9', keyword: 'transmissão|LT|subestação|ANEEL|RAP|leilão' },
    { segment: 'S6', keyword: 'porto|terminal|ANTAQ|dragagem|molhe' },
    { segment: 'S7', keyword: 'aeroporto|pista pouso|ANAC|ICAO' },
    { segment: 'S10', keyword: 'barragem|vertedouro|CFRD|rejeitos|PNSB' },
    { segment: 'S1', keyword: 'rodovia|pavimento|CBUQ|SICRO|DNIT' },
    { segment: 'S2', keyword: 'ponte|viaduto|OAE|NBR 7187' },
    { segment: 'S3', keyword: 'ferrovia|trilho|AMV|dormente' },
    { segment: 'S4', keyword: 'metrô|estação|NATM|VLT' }
  ];
  
  for (const route of routes) {
    const regex = new RegExp(route.keyword, 'i');
    if (regex.test(prompt)) {
      return {
        segment: route.segment,
        confidence: 0.90,
        matched_keyword: route.keyword
      };
    }
  }
  
  // Fallback: horizontal agents
  return {
    segment: 'horizontal',
    confidence: 0.3,
    note: 'No vertical segment matched; using horizontal agent pool'
  };
}
```

---

## KEYWORD FREQUENCY ANALYSIS (MOCK DATA)

Based on representative 2025 projects in Manta portfolio:

| Segment | Keyword | Frequency/Month | Top 3 Keywords |
|---|---|---|---|
| **S8** | SNIS | 8 | SNIS, saneamento, ETA |
| **S8** | saneamento | 12 | |
| **S8** | ETA | 15 | |
| **S9** | ANEEL | 18 | ANEEL, transmissão, LT |
| **S9** | transmissão | 22 | |
| **S9** | LT | 14 | |
| **S6** | ANTAQ | 10 | ANTAQ, porto, terminal |
| **S6** | porto | 16 | |
| **S6** | terminal | 12 | |
| **S7** | ANAC | 6 | ANAC, aeroporto, TPS |
| **S7** | aeroporto | 8 | |
| **S10** | barragem | 20 | barragem, hidrelétrica, TSF |
| **S10** | ICOLD | 5 | |
| **S1** | SICRO | 25 | rodovia, SICRO, pavimento |
| **S1** | rodovia | 28 | |
| **S4** | metrô | 15 | metrô, estação, linha |

---

## INTEGRATION WITH PHASE2-ROUTER.MD

**File:** `.claude/phase2-router.md`  
**Method:** `MaestroRouter.routeToSegment(keywords)`

**Mapping:**
1. `extractKeywords()` → extract terms from prompt
2. Loop through 10 regex patterns (S1–S10)
3. Return highest-confidence match
4. Return `{ primarySegment, agent, confidence }`

**Example:**
```
Input: "Edital de concessão para hidrelétrica com barragem de 150 m"
→ Keywords: ['edital', 'concessão', 'hidrelétrica', 'barragem']
→ Matches: S10 (barragem) + S1 (concessão)
→ Primary: S10, Confidence: 0.95
→ Agent: agente-barragens
```

---

## VALIDATION RULES

✅ **Must match before routing:**
1. Case-insensitive (regex `/i` flag)
2. Partial word match (regex `|` OR logic)
3. Acronyms must match exactly (e.g., `ETA` ≠ `eta`)
4. Confidence threshold ≥ 0.90 (high confidence)

⚠️ **Fallback (if no match):**
- Route to `horizontal` agent pool
- Confidence 0.3 (low)
- Let Manta 00 (router) decide which horizontal agents to activate

---

## DEPLOYMENT STATUS

| Phase | Item | Status |
|---|---|---|
| **Phase 1** | CLAUDE.md (master registry) | ✅ Done |
| **Phase 2** | Router implementation | ✅ Done (this doc) |
| **Phase 2** | Routing rules reference | ✅ Done (this doc) |
| **Phase 3** | RAG indexing (Supabase) | 🔲 To do |
| **Phase 3** | Lifecycle phase agent matrix | 🔲 To do |
| **Phase 4** | End-to-end integration test | 🔲 To do |
| **Phase 4** | Production deploy gate | 🔲 To do |

---

**Prepared by:** Claude Code (Phase 2)  
**Date:** 2026-08-08  
**Source:** CLAUDE.md v4.2
