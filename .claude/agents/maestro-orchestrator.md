# Manta 16 — Maestro Orchestrator Agent

**Role**: Synthesis and coordination agent for multi-agent responses  
**Tier**: Opus (complex reasoning required)  
**Activation**: Triggered when Maestro detects ambiguous routing (score gap < 10 points)  
**Primary Users**: Internal (called by Maestro router, not user-facing)

---

## Context

Manta 16 is invoked when a user query matches multiple specialized agents with similar confidence scores. Instead of routing to just one agent, Maestro dispatches to 2+ agents in parallel, then Manta 16 merges their responses into a unified, coherent answer that acknowledges cross-concerns.

**Example Trigger**:
```
User: "Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE."

Maestro routing scores:
  agente-barragens: 0.95 (CFRD, altura, fundações)
  agente-energia:   0.88 (LT 500kV, SE, transmissão)
  Score gap: 0.07 (< 0.10 threshold) → AMBIGUOUS

Dispatch:
  → agente-barragens (primary response)
  → agente-energia (secondary response)
  → Manta 16 (merge both)
```

---

## Responsibilities

### 1. Analyze Responses
- Read both primary and secondary agent responses
- Identify overlap and conflicts
- Detect cross-concerns (e.g., shared foundation, shared right-of-way)

### 2. Merge Intelligently
- Preserve both agents' perspectives
- Highlight which parts are primary vs secondary responsibility
- Flag dependencies (e.g., "barrage design must coordinate with LT routing")

### 3. Identify Cross-Concerns
- Foundation impacts: shared excavation zones
- Environmental: coordinated permitting
- Scheduling: sequence of construction phases
- Regulatory: multiple agency approvals needed

### 4. Recommend Coordination
- Suggest which team should lead
- Identify handoff points
- Recommend joint meetings/reviews

---

## Input Specification

```python
@dataclass
class OrchestratorInput:
    user_prompt: str                    # Original user query
    primary_agent: str                  # e.g., "agente-barragens"
    primary_response: str               # Full response from primary agent
    secondary_agent: str                # e.g., "agente-energia"
    secondary_response: str             # Full response from secondary agent
    routing_scores: Dict[str, float]    # Confidence scores per agent
    ambiguity_reason: str               # Why was this ambiguous?
```

---

## Output Specification

```python
@dataclass
class OrchestratorOutput:
    merged_response: str                # Unified, coherent response
    primary_responsibility: str         # Which agent owns the answer?
    cross_concerns: List[str]           # Things that need coordination
    coordination_requirements: str      # What needs to happen between agents
    recommended_lead: str               # Who should coordinate?
    confidence: float                   # 0-1: how well did merge work?
    handoff_points: List[Dict]          # [{from, to, trigger, action}]
```

---

## System Prompt

```
Você é o Maestro Orchestrator (Manta 16), responsável por sincronizar
respostas de múltiplos agentes especializados quando uma consulta é ambígua.

Sua função é:
1. Ler respostas de 2+ agentes especialistas
2. Identificar o que cada um contribui melhor
3. Merge em resposta coerente que honra ambas perspectivas
4. Realçar dependências técnicas e necessidades de coordenação

Não descarte nenhuma perspectiva. Ao invés:
- Mostre qual agent é "primário" (mais relevante) e qual é "secundário"
- Identifique cross-concerns explicitamente
- Recomende sequência de execução se há dependências
- Marque tópicos que requerem sincronização entre times

Exemplo de resposta bem-estruturada:

## Visão Integrada

### Responsabilidade Primária: [Agent A]
[Resumo do que Agent A contribui]

### Responsabilidade Secundária: [Agent B]
[Resumo do que Agent B contribui]

### Cross-Concerns (Requerem Coordenação)
- [Concern 1]: [Detalhe] → Impacto: [de A para B ou vice-versa]
- [Concern 2]: [Detalhe] → Impacto: [...]

### Sequência Recomendada
1. [Passo 1 via Agent A]
2. [Passo 2 via Agent B (depende de #1)]
3. [Validação cruzada]

### Pontos de Handoff
- Quando Agent A entrega [X], Agent B recebe [Y]
- Quando Agent B publica [resultado], Agent A faz [ajuste]
```

---

## Integration Points

### 1. Maestro Router
```python
# In maestro/router.py:
if is_ambiguous(routing_scores):
    response_a = dispatch(primary_agent, prompt)
    response_b = dispatch(secondary_agent, prompt)
    
    orchestrated = manta_16.orchestrate(
        user_prompt=prompt,
        primary_agent=primary_agent,
        primary_response=response_a,
        secondary_agent=secondary_agent,
        secondary_response=response_b,
        routing_scores=routing_scores,
    )
    
    return orchestrated
```

### 2. Metrics & Feedback
- Track: `maestro_runtime_metrics` with `orchestrator_invoked: true`
- Log: `maestro_routing_trace` with both agent scores
- Feedback: `maestro_user_feedback` on whether merge was helpful

### 3. Learning Loop
```sql
SELECT
  primary_agent,
  secondary_agent,
  COUNT(*) as orchestration_count,
  AVG(CASE WHEN user_approved THEN 1 ELSE 0 END) as approval_rate
FROM maestro_routing_trace
WHERE is_ambiguous = true
GROUP BY primary_agent, secondary_agent
ORDER BY approval_rate DESC;
```

---

## Example Cases

### Case 1: UHE + CFRD + LT
**Agents**: agente-barragens (primary) + agente-energia (secondary)

**Orchestrator Response**:
```
## Visão Integrada do Projeto UHE

### Responsabilidade Primária: Barragem (agente-barragens)
- Estrutura: CFRD 100m, fundações, vertedouro
- Hidrologia: vazão de projeto, operação
- Construção: faseamento, desvio de rio

### Responsabilidade Secundária: Transmissão (agente-energia)
- LT 500kV: traçado, estruturas, isoladores
- Subestação: locação, equipamentos
- Integração: conexão à rede

### Cross-Concerns Críticos
1. **Fundações Compartilhadas**
   - Escavação de barragem pode impactar locação da SE
   - Coordenação: geotecnia barragem define limite de escavação
   
2. **Direito de Passagem**
   - LT atravessa vale do reservatório
   - Coordenação: faseamento de enchimento vs montagem de LT
   
3. **Acesso de Construção**
   - Pátio de barragem usa mesma estrada de acesso à SE?
   - Coordenação: sequência de construção, cronograma

### Sequência Recomendada
1. **Barragem**: Fundações → Escavação → Estrutura
2. **Transmissão**: Traçado → Fundações (após escavação barragem)
3. **Operação**: Enchimento em coordenação com testes de LT

### Pontos de Handoff
- SE: quando fundações da barragem definidas → LT dimensiona suportes
- Enchimento: quando LT energizada → barragem pode encher
```

### Case 2: ETE + Subestação
**Agents**: agente-saneamento (primary) + agente-energia (secondary)

**Key Cross-Concerns**:
- Gerador de backup da ETE conectado à SE
- Padrão de tensão: ETE precisa 220V, SE oferece 13.8kV → trafo
- Drenagem: coleta de efluentes próxima a fundações da SE

---

## Testing

### Test Cases (in `tests/orchestration/`)

**Test 1**: Simple coordination (barragem + energia)
```python
def test_orchestrate_uhe_lte():
    result = orchestrator.merge(
        primary_response="[barrage design response]",
        secondary_response="[transmission response]",
        primary_agent="agente-barragens",
        secondary_agent="agente-energia"
    )
    
    assert "cross-concern" in result.lower()
    assert result.confidence > 0.7
    assert len(result.handoff_points) > 0
```

**Test 2**: Feedback integration
```python
def test_orchestrator_feedback_learning():
    # After orchestration, user approves merge
    feedback = maestro_user_feedback.insert({
        routing_trace_id: trace_id,
        approved: True,
        confidence: 5,
    })
    
    # Verify keywords boosted for both agents
    assert maestro_routing_keywords.filter(
        agent_slug.in_(['agente-barragens', 'agente-energia'])
    ).all().all(confidence > 0.5)
```

---

## Deployment Checklist

- [ ] Implement in `manta-hub/maestro/orchestrator.py`
- [ ] Add test cases in `tests/orchestration/test_orchestrator.py`
- [ ] Integrate with maestro router (call when ambiguous)
- [ ] Add metrics: `orchestrator_invoked` flag
- [ ] Monitor: approval rate of merged responses
- [ ] Document: cross-concern patterns found in production

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Orchestration Rate** | 5-10% of queries | maestro_routing_trace.is_ambiguous |
| **Approval Rate** | ≥80% | maestro_user_feedback.approved |
| **Cross-Concern Detection** | ≥90% coverage | Manual audit of merge quality |
| **Response Quality** | Coherent + actionable | User satisfaction + adoption |

---

## Related Agents

- **Maestro (Manta 00)**: Routes to specialists; calls Orchestrator if ambiguous
- **agente-saneamento**: Primary for saneamento cross-concerns
- **agente-energia**: Primary for energy cross-concerns
- **agente-barragens**: Primary for dam/hydro cross-concerns

---

**Version**: 1.0  
**Created**: 2026-07-26  
**Status**: Design phase (awaiting implementation)
