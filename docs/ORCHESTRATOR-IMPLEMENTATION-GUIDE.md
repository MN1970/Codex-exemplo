# Orchestrator Implementation Guide — Phase 2.2

**Target**: `manta-hub/maestro/orchestrator.py`  
**Tier**: Sonnet (orchestration logic)  
**Integration**: Maestro router (manta-hub/maestro/router.py)

This guide shows how to implement the Orchestrator Agent (Manta 16) in the maestro codebase.

---

## Overview

When Maestro router detects ambiguous routing (score gap < 10 points between primary and secondary agent):

```
User query
  ↓
Maestro router calculates scores for all agents
  ↓
IF max_score - second_score < 10:
    → AMBIGUOUS: dispatch BOTH agents in parallel
    → Orchestrator merges responses
ELSE:
    → route to primary agent only
```

---

## Implementation Structure

```python
# manta-hub/maestro/orchestrator.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

@dataclass
class OrchestratorInput:
    """Input to Orchestrator Agent."""
    user_prompt: str
    primary_agent: str
    primary_response: str
    secondary_agent: str
    secondary_response: str
    routing_scores: Dict[str, float]
    ambiguity_reason: str

@dataclass
class OrchestratorOutput:
    """Output from Orchestrator Agent."""
    merged_response: str
    primary_responsibility: str
    cross_concerns: List[str]
    coordination_requirements: str
    recommended_lead: str
    confidence: float
    handoff_points: List[Dict[str, Any]]

class MaestroOrchestrator:
    """Synthesize responses from multiple specialized agents."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic()
        self.model = model

    def orchestrate(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """
        Merge responses from 2+ agents into coherent output.

        Args:
            input_data: OrchestratorInput with both agent responses

        Returns:
            OrchestratorOutput with merged response
        """

        # Build system prompt (from .claude/agents/maestro-orchestrator.md)
        system_prompt = self._build_system_prompt()

        # Build user message with both agent responses
        user_message = f"""
Consulta original: "{input_data.user_prompt}"

Scores de roteamento:
- {input_data.primary_agent}: {input_data.routing_scores.get(input_data.primary_agent, 0):.2f} (PRIMÁRIO)
- {input_data.secondary_agent}: {input_data.routing_scores.get(input_data.secondary_agent, 0):.2f} (SECUNDÁRIO)

Razão ambiguidade: {input_data.ambiguity_reason}

Resposta do {input_data.primary_agent}:
{input_data.primary_response}

---

Resposta do {input_data.secondary_agent}:
{input_data.secondary_response}

---

Sua função: Sintetizar ambas respostas em resposta coerente e acionável.
Preservar ambas perspectivas, identificar cross-concerns, recomendar sequência.
"""

        # Call Sonnet with both responses
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        merged_text = response.content[0].text

        # Parse response (structured extraction)
        output = self._parse_orchestrator_response(
            merged_text,
            input_data.primary_agent,
            input_data.secondary_agent,
        )

        return output

    def _build_system_prompt(self) -> str:
        """Build system prompt from orchestrator spec."""
        return """Você é o Maestro Orchestrator (Manta 16), responsável por sincronizar
respostas de múltiplos agentes especializados quando uma consulta é ambígua.

Sua função é:
1. Ler respostas de 2+ agentes especialistas
2. Identificar o que cada um contribui melhor
3. Merge em resposta coerente que honra ambas perspectivas
4. Realçar dependências técnicas e necessidades de coordenação

Não descarte nenhuma perspectiva. Ao invés:
- Mostre qual agent é "primário" (mais relevante) e qual é "secundário"
- Identifique cross-concerns explicitamente (≥2 pontos de coordenação)
- Recomende sequência de execução se há dependências
- Marque tópicos que requerem sincronização entre times

Formato de resposta OBRIGATÓRIO:

## Visão Integrada

### Responsabilidade Primária: [Agent A]
[Resumo do que Agent A contribui — 2-3 parágrafos]

### Responsabilidade Secundária: [Agent B]
[Resumo do que Agent B contribui — 2-3 parágrafos]

### Cross-Concerns (Requerem Coordenação)
- [Concern 1]: [Detalhe de 1-2 linhas] → Impacto: [de A para B ou vice-versa]
- [Concern 2]: [Detalhe de 1-2 linhas] → Impacto: [...]
- [Concern 3+]: [...]

### Sequência Recomendada
1. [Passo 1 via Agent A] (duração estimada)
2. [Passo 2 via Agent B (depende de #1)] (duração)
3. [Passo 3] (validação/ajustes)
4. [...]

### Pontos de Handoff
- **[M0-M12]**: Quando Agent A entregar [X] → Agent B recebe [Y] e faz [Z]
- **[M12-M20]**: Quando Agent B publicar [resultado] → Agent A faz [ajuste]

---

Métricas de qualidade que você DEVE atender:
✓ Perspectivas: ambas reconhecidas; pesos justificados
✓ Cross-concerns: ≥2 identificados; direção de impacto clara
✓ Coordenação: handoff points timestamped; sequência não-contraditória
✓ Acionabilidade: usuário consegue implementar; sem linguagem vaga
✓ Coerência: fluxo lógico; sem conflitos ou repetição
"""

    def _parse_orchestrator_response(
        self,
        response_text: str,
        primary_agent: str,
        secondary_agent: str,
    ) -> OrchestratorOutput:
        """Parse Sonnet response into structured output."""

        # Simple parsing of markdown structure
        # In production, use more robust parsing (regex or LLM-assisted)

        def extract_section(text: str, header: str) -> str:
            """Extract content between headers."""
            try:
                start = text.index(f"### {header}")
                # Find next header or end
                rest = text[start + len(f"### {header}"):]
                next_header = rest.index("###")
                return rest[:next_header].strip()
            except (ValueError, IndexError):
                return ""

        primary_resp = extract_section(response_text, f"Responsabilidade Primária")
        secondary_resp = extract_section(response_text, f"Responsabilidade Secundária")
        cross_concerns_text = extract_section(response_text, "Cross-Concerns")
        coordination_text = extract_section(response_text, "Sequência Recomendada")
        handoff_text = extract_section(response_text, "Pontos de Handoff")

        # Extract cross-concerns as list
        cross_concerns = [
            line.strip("- ").split(":")[0].strip()
            for line in cross_concerns_text.split("\n")
            if line.startswith("-")
        ]

        # Parse handoff points
        handoff_points = [
            {
                "trigger": line.split(":")[0].strip("*"),
                "action": line.split(":")[1].strip() if ":" in line else ""
            }
            for line in handoff_text.split("\n")
            if line.startswith("-")
        ]

        # Determine lead agent (usually primary unless secondary owns critical path)
        lead = primary_agent  # Can be refined by parsing response text

        return OrchestratorOutput(
            merged_response=response_text,
            primary_responsibility=primary_resp,
            cross_concerns=cross_concerns,
            coordination_requirements=coordination_text,
            recommended_lead=lead,
            confidence=0.85,  # Can be refined by analyzing quality
            handoff_points=handoff_points,
        )

    def score_merge_quality(self, output: OrchestratorOutput) -> float:
        """Score merged response on quality rubric (0-1).

        Dimensions:
        - Perspective coverage (20%): both agents acknowledged?
        - Cross-concern identification (25%): ≥2 identified?
        - Coordination clarity (20%): handoff points timestamped?
        - Actionability (20%): user can implement?
        - Coherence (15%): logical flow?
        """
        score = 0.0

        # Perspective coverage
        if len(output.primary_responsibility) > 100 and len(output.coordination_requirements) > 50:
            score += 0.20

        # Cross-concern identification
        if len(output.cross_concerns) >= 2:
            score += 0.25
        elif len(output.cross_concerns) >= 1:
            score += 0.12

        # Coordination clarity
        if len(output.handoff_points) >= 2:
            score += 0.20

        # Actionability (check for vague language)
        vague_words = ["perhaps", "maybe", "might", "could", "possibly"]
        if not any(w in output.merged_response.lower() for w in vague_words):
            score += 0.20

        # Coherence (length and structure)
        if len(output.merged_response) > 500 and "###" in output.merged_response:
            score += 0.15

        return min(score, 1.0)
```

---

## Integration with Maestro Router

In `manta-hub/maestro/router.py`:

```python
from orchestrator import MaestroOrchestrator, OrchestratorInput

class MaestroRouter:
    def __init__(self):
        self.orchestrator = MaestroOrchestrator()
        # ... rest of initialization

    def route_and_respond(self, user_prompt: str) -> str:
        """Main routing logic."""

        # 1. Score all agents
        scores = self._score_agents(user_prompt)
        
        primary_agent = max(scores, key=scores.get)
        primary_score = scores[primary_agent]
        
        # Get runner-up
        remaining = {a: s for a, s in scores.items() if a != primary_agent}
        secondary_agent = max(remaining, key=remaining.get) if remaining else None
        secondary_score = remaining[secondary_agent] if secondary_agent else 0

        score_gap = primary_score - secondary_score

        # 2. Ambiguity check
        is_ambiguous = score_gap < 0.10  # 10% confidence gap

        if is_ambiguous and secondary_agent:
            # 3a. AMBIGUOUS: dispatch both in parallel
            primary_resp = self._dispatch(primary_agent, user_prompt)
            secondary_resp = self._dispatch(secondary_agent, user_prompt)

            # 4. Orchestrate
            input_data = OrchestratorInput(
                user_prompt=user_prompt,
                primary_agent=primary_agent,
                primary_response=primary_resp,
                secondary_agent=secondary_agent,
                secondary_response=secondary_resp,
                routing_scores=scores,
                ambiguity_reason=f"Score gap {score_gap:.2f} < 0.10",
            )

            output = self.orchestrator.orchestrate(input_data)

            # 5. Log metrics
            self._log_orchestration_event(
                user_prompt=user_prompt,
                primary_agent=primary_agent,
                secondary_agent=secondary_agent,
                score_gap=score_gap,
                merge_quality=self.orchestrator.score_merge_quality(output),
            )

            return output.merged_response

        else:
            # 3b. NOT AMBIGUOUS: route to primary only
            response = self._dispatch(primary_agent, user_prompt)
            
            # Log normal routing
            self._log_routing_event(
                user_prompt=user_prompt,
                routed_agent=primary_agent,
                confidence=primary_score,
            )

            return response

    def _score_agents(self, user_prompt: str) -> Dict[str, float]:
        """Score all agents for this prompt."""
        # Use existing routing keywords logic
        # Returns: {"agente-saneamento": 0.92, "agente-energia": 0.88, ...}
        pass

    def _dispatch(self, agent_slug: str, prompt: str) -> str:
        """Call specialized agent."""
        # Use existing dispatch logic
        pass

    def _log_orchestration_event(self, **kwargs):
        """Log to maestro_routing_trace."""
        # Insert to Supabase with is_ambiguous=true
        pass

    def _log_routing_event(self, **kwargs):
        """Log normal routing."""
        # Insert to maestro_routing_trace with is_ambiguous=false
        pass
```

---

## Testing Strategy

```python
# tests/test_orchestrator.py

import pytest
from maestro.orchestrator import MaestroOrchestrator, OrchestratorInput

def test_orchestrate_uhe_cfrd_lte():
    """Test orchestration of UHE + CFRD + LT case."""
    
    input_data = OrchestratorInput(
        user_prompt="Preciso projetar UHE com CFRD de 100m e LT 500kV até SE.",
        primary_agent="agente-barragens",
        primary_response="[barragem response with CFRD design...]",
        secondary_agent="agente-energia",
        secondary_response="[transmission response with LT routing...]",
        routing_scores={
            "agente-barragens": 0.95,
            "agente-energia": 0.88,
        },
        ambiguity_reason="Score gap 0.07 < 0.10",
    )

    orchestrator = MaestroOrchestrator()
    output = orchestrator.orchestrate(input_data)

    # Assertions
    assert "Responsabilidade Primária" in output.merged_response
    assert "Cross-Concerns" in output.merged_response
    assert len(output.cross_concerns) >= 2
    assert len(output.handoff_points) >= 1
    assert output.confidence >= 0.75

def test_false_ambiguity_not_triggered():
    """Test that non-ambiguous cases don't trigger orchestrator."""
    
    # High-confidence primary (gap > 0.10) should NOT orchestrate
    # This test is in router, not orchestrator
    pass

def test_merge_quality_scoring():
    """Test quality rubric evaluation."""
    
    output = OrchestratorOutput(
        merged_response="[well-structured response]",
        primary_responsibility="[substantial text]",
        cross_concerns=["Concern 1", "Concern 2", "Concern 3"],
        coordination_requirements="[detailed sequencing]",
        recommended_lead="agente-barragens",
        confidence=0.85,
        handoff_points=[{"trigger": "M12", "action": "..."}],
    )

    orchestrator = MaestroOrchestrator()
    score = orchestrator.score_merge_quality(output)

    assert score >= 0.75, f"Quality score {score} below target 0.75"
```

---

## Deployment Checklist

- [ ] Implement `orchestrator.py` in `manta-hub/maestro/`
- [ ] Integrate with `router.py` (ambiguity detection + dispatch)
- [ ] Add Sonnet model dispatch in agent registry
- [ ] Create test cases (test_orchestrator.py)
- [ ] Test with 5+ real-world ambiguous prompts
- [ ] Configure Supabase logging (maestro_routing_trace)
- [ ] Monitor orchestration rate (target: 5-10% of queries)
- [ ] Monitor approval rate (target: ≥80% user satisfaction)
- [ ] Iterate on merge quality based on feedback

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Orchestration Rate** | 5-10% | queries with score gap < 10 |
| **Merge Quality Score** | ≥0.75 avg | rubric evaluation |
| **Approval Rate** | ≥80% | maestro_user_feedback.approved |
| **Latency (3-way)** | <1500ms (p95) | primary + secondary + merge |
| **Cross-Concern Detection** | ≥90% | manual audit |

---

**Status**: Ready for implementation  
**Owner**: Maestro team (manta-hub)  
**Timeline**: Phase 2.2 (Aug 10-31)
