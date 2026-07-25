# Multi-Agent Orchestration Tests — Manta Maestro v5.0

**Test suite for Maestro ambiguous routing** → **Manta 16 (Orchestrator)**

When routing confidence gap < 10 points between primary and secondary agent,
dispatch to both agents in parallel, then merge via Orchestrator Agent.

Rodar via:
```bash
python scripts/test_multiagent_dispatch.py tests/routing/test_multiagent_dispatch.md
```

---

## Test Data Schema

```python
@dataclass
class MultiAgentTestCase:
    prompt: str                         # user query
    primary_agent: str                  # expected primary (higher score)
    secondary_agent: str                # expected secondary (lower score)
    score_gap: float                    # confidence gap (primary - secondary)
    cross_concerns: List[str]           # expected coordination points
    expected_primary_resp_length: int    # approximate response length in tokens
    expected_secondary_resp_length: int
    expected_merge_length: int          # merged response token estimate
    merge_quality_target: float         # 0-1: expected merge coherence score
    handoff_pattern: str                # e.g., "barragem → energia", "saneamento → energia"
```

---

## Test Suite 1: Infrastructure + Energy (Cross-Segment Coordination)

### Case 1.1 — UHE + CFRD + LT (Dam + Transmission)

```
Prompt: "Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE.
         Estou avaliando a viabilidade técnica e cronograma integrado."

Primary: agente-barragens (score: 0.95)
  Keywords matched: CFRD (0.30), barragem (0.28), altura 100m (0.18), UHE (0.15), viabilidade (0.04)
  
Secondary: agente-energia (score: 0.88)
  Keywords matched: LT 500kV (0.32), transmissão (0.28), SE/subestação (0.18), cronograma (0.10)

Score gap: 0.07 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Primary Response (agente-barragens):
  - Estrutura CFRD: alturas até 110m, fundação e materialização
  - Hidrologia: vazão de projeto, sistema de vertimento
  - Cronograma fase barragem: escavação (12m), estrutura (18m), enchimento (6m)
  - Interface: definir cota de operação normal para interconexão com LT

Expected Secondary Response (agente-energia):
  - LT 500kV: traçado, torres estaiadas vs convencionais
  - Subestação: locação em nível de enchimento, equipamentos
  - Cronograma LT: fundações (8m), montagem (10m), energização (2m)
  - Restrição: LT fundações não podem estar em zona de escavação barragem

Cross-Concerns (Orchestrator must identify):
  ✓ Fundações compartilhadas: escavação barragem impacta locação SE
  ✓ Acesso de construção: pátio barragem + acesso SE usam mesma via?
  ✓ Enchimento vs energização: sequência crítica
  ✓ Direito de passagem: LT atravessa vale do reservatório

Recommended Sequence:
  1. Barragem: fase escavação (m0-m12)
  2. Energia: estudo traçado LT + locação SE (m2-m4, paralelo)
  3. Barragem: fundações + estrutura (m12-m30, com validação de cotas)
  4. Energia: fundações SE (m8-m14, após confirmação cotas barragem)
  5. Barragem: enchimento inicia (m30)
  6. Energia: montagem LT (m10-m20, após estrutura barragem)
  7. Energia: energização (m20, pós-enchimento parcial)

Handoff Points:
  - [m12] Barragem → Energia: "cotas de fundação SE definidas, elevação XYZ"
  - [m20] Energia → Barragem: "LT energizada, enchimento pode prosseguir"

Merge Quality Validation:
  ✓ Acknowledges both agents' perspectives (primary: CFRD design, secondary: LT routing)
  ✓ Highlights explicit handoff triggers with dates
  ✓ Identifies 4+ cross-concerns with impact direction (A→B or B→A)
  ✓ Recommends lead agent (Barragem = critical path owner)
  ✓ Response coherent + actionable
  ✓ No conflicts or contradictions between recommendations

Score: 0.85-0.95 (excellent)
```

### Case 1.2 — Adutora + Barragem (Water + Damming)

```
Prompt: "Temos uma adutora de 800mm que precisa atravessar uma barragem TSF existente.
         Como coordenamos o projeto estrutural da adutora com a estabilidade da barragem?"

Primary: agente-saneamento (score: 0.92)
  Keywords matched: adutora (0.30), 800mm (0.15), água (0.12), projeto (0.20), saneamento (0.15)
  
Secondary: agente-barragens (score: 0.84)
  Keywords matched: barragem (0.28), TSF (0.25), estabilidade (0.18), fundações (0.13)

Score gap: 0.08 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Cross-Concerns:
  ✓ Escavação adutora pode impactar berma da barragem
  ✓ Carga hidrostática adutora pressiona estrutura barragem
  ✓ Inspeção/manutenção adutora precisa coordenar com O&M barragem
  ✓ Alteamento futuro de barragem vs profundidade adutora

Handoff Pattern: saneamento (lead) → barragem (consulta estrutural)

Merge Quality Target: 0.80+
```

---

## Test Suite 2: Sanitation + Energy (Infrastructure Sharing)

### Case 2.1 — ETE + Subestação (Treatment + Grid Connection)

```
Prompt: "Vou construir uma ETE com gerador de backup 500kW conectado à subestação 13.8kV
         no mesmo canteiro. Preciso coordenar o projeto civil, elétrico e de drenagem."

Primary: agente-saneamento (score: 0.93)
  Keywords matched: ETE (0.35), tratamento (0.18), drenagem (0.15), projeto civil (0.15), canteiro (0.10)
  
Secondary: agente-energia (score: 0.89)
  Keywords matched: subestação (0.28), 13.8kV (0.25), gerador (0.18), conexão (0.18)

Score gap: 0.04 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Cross-Concerns:
  ✓ Drenagem ETE vs fundações SE: canaletas, sump pumps
  ✓ Trafo 500kVA (13.8kV → 440V para ETA equipamentos)
  ✓ Acesso simultâneo para construção: cronograma integrado
  ✓ Aterramento: sistema aterramento ETE deve coordenar com malha SE

Handoff Pattern: saneamento (lead, ~70%) → energia (20%) + coordenação (10%)

Merge Quality Target: 0.82+
```

### Case 2.2 — LT Através de ETA (Transmission via Water Plant)

```
Prompt: "Precisamos estender uma LT 230kV que atravessa a ETA existente.
         Como evitamos interferências eletromagnéticas com equipamentos de tratamento?"

Primary: agente-energia (score: 0.91)
  Keywords matched: LT 230kV (0.32), transmissão (0.20), eletromagnético (0.19), traçado (0.20)
  
Secondary: agente-saneamento (score: 0.85)
  Keywords matched: ETA (0.28), tratamento (0.20), interferência (0.18), equipamentos (0.19)

Score gap: 0.06 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Cross-Concerns:
  ✓ Blindagem eletrônica para sensores de pH, turbidez, dosagem de cloro
  ✓ Afastamento mínimo entre LT e eletrodos de processo
  ✓ Aterramento ETA isolado vs aterramento LT
  ✓ Ruído magnético em análises laboratoriais (proteção blindagem)

Handoff Pattern: energia (lead) → saneamento (EMC validation)

Merge Quality Target: 0.80+
```

---

## Test Suite 3: Ports + Aeronautics (Multimodal Facilities)

### Case 3.1 — Porto + Pátio Aéreo (Maritime + Air Cargo)

```
Prompt: "Terminal portuário regional no Amazonas quer adicionar pátio de carga aérea
         auxiliar (e-commerce). Como integro drenagem, acesso rodoviário e operações?"

Primary: agente-portos (score: 0.94)
  Keywords matched: porto (0.30), terminal (0.25), Amazonas (0.15), drenagem (0.12), acesso (0.12)
  
Secondary: agente-aeroportos (score: 0.87)
  Keywords matched: pátio aéreo (0.28), carga (0.20), aeroporto (0.18), operações (0.21)

Score gap: 0.07 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Cross-Concerns:
  ✓ Drenagem integrada: pátio portuário vs pátio aéreo (diferentes cotas)
  ✓ Segurança: isolamento de áreas de operação (porto vs aviação)
  ✓ Acesso rodoviário: pesado (contêineres) vs leve (vans de carga)
  ✓ Horário operacional: porto 24h vs aeroporto regional (6am-6pm)
  ✓ Balizamento/iluminação: LED compartilhado vs específico de pista

Handoff Pattern: portos (lead, ~65%) → aeroportos (35%), coordenação crítica

Merge Quality Target: 0.85+
```

### Case 3.2 — Ampliação de Aeroporto com Acesso Portuário

```
Prompt: "Aeroporto regional planeja ampliação com TPS novo. Terminal tem acesso via rio
         e precisa de área de carga que integre operações portuárias (containers)."

Primary: agente-aeroportos (score: 0.89)
  Keywords matched: aeroporto (0.28), TPS (0.25), pista (0.15), ampliação (0.15), rio (0.06)
  
Secondary: agente-portos (score: 0.82)
  Keywords matched: rio (0.22), containers (0.25), carga (0.20), terminal (0.15)

Score gap: 0.07 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Expected Cross-Concerns:
  ✓ Acesso via rio: bacia de manobra vs operações TPS (conflito lateral)
  ✓ Zona de proteção pista vs doca portuária (separação mínima ICAO/PIANC)
  ✓ Equipamento de carga: containers requerem guindaste de porto (altura interferência?)

Merge Quality Target: 0.80+
```

---

## Test Suite 4: Demanding Real-World Scenarios

### Case 4.1 — Mineração + Barragem + Energia (3-Way Ambiguity)

```
Prompt: "Projeto de mineração com barragem TSF de rejeitos, drenagem para rio,
         e subestação 138kV para alimentar planta. Estou em fase de preliminar."

Primary: agente-barragens (score: 0.92)
  Keywords matched: barragem (0.28), TSF (0.28), rejeitos (0.25), mineração (0.11)
  
Secondary: agente-energia (score: 0.88)
  Keywords matched: subestação (0.25), 138kV (0.22), alimentação (0.20), planta (0.21)

Tertiary: agente-saneamento (score: 0.84)
  Keywords matched: drenagem (0.28), rio (0.20), rejeitos (0.18), descarga (0.18)

Score gaps: 0.04 (bag vs ene), 0.08 (ene vs san) → DISPATCH PRIMARY + SECONDARY
  (Note: saneamento may be engaged as tertiary if orchestrator identifies water/discharge angle)

Orchestrator Decision Logic:
  - Primary: barragens (leads, owns TSF design)
  - Secondary: energia (owns grid connection)
  - Tertiary consideration: saneamento (water quality/discharge) — may need 3-way orchestration

Expected Handoffs:
  1. Barragem → Energia: TSF cota define SE elevation
  2. Barragem → Saneamento: drenagem barragem vs efluente minério
  3. Energia → Saneamento: consumo água planta vs disponibilidade

Merge Quality Target: 0.78+ (higher difficulty; 3-way integration)
```

### Case 4.2 — Rodovia + Ponte + Rio + Dragagem (S1-S2-S6 Interaction)

```
Prompt: "Rodovia federal atravessa rio navegável com ponte de 150m. Rio tem restrição
         de profundidade (calado 2m). Preciso minimizar interferência com hidrovia."

Primary: agente-infraestrutura (S2 - OAE) (score: 0.90)
  Keywords matched: ponte (0.32), 150m (0.15), vão (0.18), estrutura (0.25)
  
Secondary: agente-portos (score: 0.86)
  Keywords matched: rio (0.25), navegável (0.28), calado (0.20), hidrovia (0.13)

Score gap: 0.04 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Cross-Concerns:
  ✓ Altura de gabarito: ponte clearance vs navio altura
  ✓ Fundações rio: pile driving pode impactar tráfego fluvial
  ✓ Dragagem canal: profundidade constante vs variação sazonal
  ✓ Proteção de pila: barreira flutuante vs marcação em navegação

Handoff Pattern: OAE (lead) ↔ Portos (high interaction)

Merge Quality Target: 0.80+
```

---

## Test Suite 5: Failure Cases (Negative Tests)

### Case 5.1 — False Ambiguity (High-Confidence Primary)

```
Prompt: "Preciso dimensionar o condutor ACSR para uma LT de 500kV, ampacidade ANEEL R5."

Primary: agente-energia (score: 0.96)
Secondary: agente-barragens (score: 0.78)

Score gap: 0.18 (> 0.10 threshold) → NOT AMBIGUOUS
  → Route ONLY to agente-energia (ignore barragens noise)
  
Validation:
  ✓ Orchestrator should NOT be triggered
  ✓ Routing decision goes direct to primary
  ✓ No false positive orchestration overhead
```

### Case 5.2 — Conflicting Recommendations

```
Prompt: "Construir ETA com adutora que atravessa barragem TSF existente, minimizando
         custo e prazo. Agentes divergem em prioridade técnica vs cronograma."

Primary: agente-saneamento (score: 0.90) — recommends "bypipa isolada" (custo)
Secondary: agente-barragens (score: 0.87) — recommends "integral ao dique" (segurança)

Score gap: 0.03 (< 0.10 threshold) → AMBIGUOUS → dispatch both

Conflict Resolution in Merge:
  ✗ Orchestrator must NOT hide disagreement
  ✓ Orchestrator MUST make explicit which recommendation owns priority
  ✓ Flag tradeoff to user: "Safety > Cost, recommend integrated"
  ✓ Document both viewpoints + recommendation rationale

Merge Quality Target: 0.75+ (conflict explicitly managed)
```

---

## Orchestration Quality Rubric

Every merged response must achieve ≥0.75 on this rubric:

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| **Perspective Coverage** | 20% | Both agents' viewpoints acknowledged + weighted by relevance |
| **Cross-Concern Identification** | 25% | ≥2 explicit cross-concerns + impact direction (A→B or B→A) |
| **Coordination Clarity** | 20% | Handoff points timestamped; sequence non-contradictory |
| **Actionability** | 20% | User can implement recommendations; no vague language |
| **Coherence** | 15% | Response flows logically; no conflicts or repetition |

---

## Testing Harness (Python)

```python
# scripts/test_multiagent_dispatch.py

import json
from anthropic import Anthropic
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class OrchestratorTestResult:
    test_case_id: str
    prompt: str
    primary_agent: str
    secondary_agent: str
    primary_response: str
    secondary_response: str
    merged_response: str
    merge_score: float  # 0-1
    cross_concerns_detected: int
    handoff_points: int
    passed: bool  # merge_score >= target
    latency_ms: float

def score_merge(merged_response: str, expected_concerns: List[str]) -> float:
    """Score merged response on quality rubric."""
    # LLM-assisted grading: call Claude with rubric
    # Return 0-1 score
    pass

def run_orchestration_test(test_case) -> OrchestratorTestResult:
    """Run single orchestration test."""
    # 1. Dispatch primary agent
    primary_resp = dispatch_agent(test_case.primary_agent, test_case.prompt)
    
    # 2. Dispatch secondary agent
    secondary_resp = dispatch_agent(test_case.secondary_agent, test_case.prompt)
    
    # 3. Call Orchestrator (Manta 16) to merge
    merged = call_orchestrator(
        user_prompt=test_case.prompt,
        primary_agent=test_case.primary_agent,
        primary_response=primary_resp,
        secondary_agent=test_case.secondary_agent,
        secondary_response=secondary_resp,
    )
    
    # 4. Score merge quality
    score = score_merge(merged, test_case.expected_cross_concerns)
    
    # 5. Return result
    return OrchestratorTestResult(
        test_case_id=test_case.id,
        prompt=test_case.prompt,
        primary_agent=test_case.primary_agent,
        secondary_agent=test_case.secondary_agent,
        primary_response=primary_resp,
        secondary_response=secondary_resp,
        merged_response=merged,
        merge_score=score,
        passed=(score >= test_case.merge_quality_target),
    )
```

---

## Success Metrics (Phase 2.2)

| Metric | Target | Validation |
|--------|--------|------------|
| **Orchestration Rate** | 5–10% of queries | Queries with score gap < 10 |
| **Merge Quality** | ≥80% of cases score ≥0.80 | Rubric scoring |
| **Cross-Concern Detection** | ≥90% | Manual audit of 10 cases |
| **Approval Rate** | ≥80% | User feedback on merged response |
| **Latency (3-way)** | <1500ms (p95) | Primary + secondary dispatch + merge |

---

**Last Updated**: 2026-07-26  
**Status**: Ready for orchestration.py implementation  
**Next**: Implement manta-hub/maestro/orchestrator.py + integrate with maestro router
