#!/usr/bin/env python3
"""
Phase 2.2: Maestro Orchestrator Agent (Manta 16)
Multi-agent response synthesis and cross-concern identification.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

import anthropic

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorInput:
    """Input specification for orchestrator."""
    user_prompt: str
    primary_agent: str
    primary_response: str
    secondary_agent: str
    secondary_response: str
    routing_scores: Dict[str, float]
    ambiguity_reason: str = ""


@dataclass
class HandoffPoint:
    """Handoff between two agents."""
    from_agent: str
    to_agent: str
    trigger: str
    action: str


@dataclass
class OrchestratorOutput:
    """Output specification for orchestrator."""
    merged_response: str
    primary_responsibility: str
    secondary_responsibility: str
    cross_concerns: List[str]
    coordination_requirements: str
    recommended_lead: str
    confidence: float
    handoff_points: List[HandoffPoint]
    timestamp: str


class MaestroOrchestrator:
    """Multi-agent response synthesizer."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize orchestrator with Anthropic client."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-1-20250805"

    def _build_orchestration_prompt(self, orchestrator_input: OrchestratorInput) -> str:
        """Build the system prompt for orchestration."""
        return f"""Você é o Maestro Orchestrator (Manta 16), responsável por sincronizar
respostas de múltiplos agentes especializados quando uma consulta é ambígua.

Sua função é:
1. Ler respostas de 2+ agentes especialistas
2. Identificar o que cada um contribui melhor
3. Fazer merge em resposta coerente que honra ambas perspectivas
4. Realçar dependências técnicas e necessidades de coordenação

IMPORTANTE: Não descarte nenhuma perspectiva. Ao invés:
- Mostre qual agent é "primário" (mais relevante) e qual é "secundário"
- Identifique cross-concerns explicitamente
- Recomende sequência de execução se há dependências
- Marque tópicos que requerem sincronização entre times

CONSULTA ORIGINAL DO USUÁRIO:
{orchestrator_input.user_prompt}

SCORES DE ROTEAMENTO:
{json.dumps(orchestrator_input.routing_scores, indent=2)}

RAZÃO DA AMBIGÜIDADE:
{orchestrator_input.ambiguity_reason}

---

RESPOSTA DO AGENTE PRIMÁRIO ({orchestrator_input.primary_agent}):
{orchestrator_input.primary_response}

RESPOSTA DO AGENTE SECUNDÁRIO ({orchestrator_input.secondary_agent}):
{orchestrator_input.secondary_response}

---

Agora, analise ambas respostas e crie uma RESPOSTA INTEGRADA que:
1. Resume o que cada agente contribui
2. Identifica 3-5 "cross-concerns" (pontos de coordenação necessária)
3. Propõe sequência de execução e handoff points
4. Indica qual agente deve liderar o projeto

Estruture sua resposta assim:

## Visão Integrada

### Responsabilidade Primária: {orchestrator_input.primary_agent}
[Resumo do que este agent contribui, 2-3 parágrafos]

### Responsabilidade Secundária: {orchestrator_input.secondary_agent}
[Resumo do que este agent contribui, 2-3 parágrafos]

### Cross-Concerns (Requerem Coordenação)
- [Concern 1]: [Detalhe técnico] → Impacto: [interdependência]
- [Concern 2]: [Detalhe técnico] → Impacto: [interdependência]
- [Concern 3]: [Detalhe técnico] → Impacto: [interdependência]

### Sequência Recomendada
1. [Passo 1]
2. [Passo 2]
3. [Validação]

### Pontos de Handoff
1. Quando {orchestrator_input.primary_agent} entrega [X], {orchestrator_input.secondary_agent} recebe [Y]
2. Quando {orchestrator_input.secondary_agent} entrega [Z], {orchestrator_input.primary_agent} faz [ação]

### Agente Recomendado para Liderar
[Nome do agente] deve coordenar porque [razão breve]
"""

    def _parse_orchestrator_response(self, response_text: str, orchestrator_input: OrchestratorInput) -> OrchestratorOutput:
        """Parse orchestrator response into structured output."""
        # Extract sections from response
        cross_concerns = []
        coordination_text = ""
        handoff_text = ""
        lead_agent = ""

        lines = response_text.split("\n")
        current_section = None

        for line in lines:
            if "### Cross-Concerns" in line:
                current_section = "cross_concerns"
            elif "### Sequência Recomendada" in line:
                current_section = "sequence"
            elif "### Pontos de Handoff" in line:
                current_section = "handoff"
            elif "### Agente Recomendado para Liderar" in line:
                current_section = "lead"
            elif line.startswith("###"):
                current_section = None

            if current_section == "cross_concerns" and line.startswith("-"):
                cross_concerns.append(line.lstrip("- ").strip())
            elif current_section == "sequence":
                coordination_text += line + "\n"
            elif current_section == "handoff":
                handoff_text += line + "\n"
            elif current_section == "lead":
                if line.strip() and not line.startswith("#"):
                    lead_agent = line.strip()

        # Extract handoff points
        handoff_points = []
        for line in handoff_text.split("\n"):
            if line.strip() and (line.startswith("1.") or line.startswith("2.") or "quando" in line.lower()):
                # Parse simple handoff format
                handoff_points.append(HandoffPoint(
                    from_agent=orchestrator_input.primary_agent,
                    to_agent=orchestrator_input.secondary_agent,
                    trigger="Phase transition",
                    action=line.strip(),
                ))

        # Determine confidence based on response structure
        confidence = 0.8 if len(cross_concerns) >= 3 else 0.6

        return OrchestratorOutput(
            merged_response=response_text,
            primary_responsibility=orchestrator_input.primary_agent,
            secondary_responsibility=orchestrator_input.secondary_agent,
            cross_concerns=cross_concerns[:5],
            coordination_requirements=coordination_text.strip(),
            recommended_lead=lead_agent or orchestrator_input.primary_agent,
            confidence=confidence,
            handoff_points=handoff_points,
            timestamp=datetime.utcnow().isoformat(),
        )

    def orchestrate(self, orchestrator_input: OrchestratorInput) -> OrchestratorOutput:
        """Orchestrate multi-agent responses into unified answer."""
        logger.info(f"Orchestrating responses from {orchestrator_input.primary_agent} and {orchestrator_input.secondary_agent}")

        # Build orchestration prompt
        system_prompt = self._build_orchestration_prompt(orchestrator_input)

        # Call Claude to orchestrate
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": "Agora realize a síntese: crie a resposta integrada conforme especificado."
                }
            ],
        )

        # Extract response text
        response_text = response.content[0].text

        # Parse into structured output
        orchestrator_output = self._parse_orchestrator_response(response_text, orchestrator_input)

        logger.info(f"Orchestration complete. Cross-concerns identified: {len(orchestrator_output.cross_concerns)}")

        return orchestrator_output

    def to_dict(self, output: OrchestratorOutput) -> Dict:
        """Convert output to dictionary for JSON serialization."""
        return {
            "merged_response": output.merged_response,
            "primary_responsibility": output.primary_responsibility,
            "secondary_responsibility": output.secondary_responsibility,
            "cross_concerns": output.cross_concerns,
            "coordination_requirements": output.coordination_requirements,
            "recommended_lead": output.recommended_lead,
            "confidence": output.confidence,
            "handoff_points": [
                {
                    "from_agent": hp.from_agent,
                    "to_agent": hp.to_agent,
                    "trigger": hp.trigger,
                    "action": hp.action,
                }
                for hp in output.handoff_points
            ],
            "timestamp": output.timestamp,
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test case: UHE + CFRD + LT
    test_input = OrchestratorInput(
        user_prompt="Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE.",
        primary_agent="agente-barragens",
        primary_response="""
        A barragem CFRD (Concrete Face Rockfill Dam) de 100m é viável neste contexto.
        Recomendações:
        1. Fundações: Escavação até rocha sã, limpeza de fraturas
        2. Estrutura: Face de concreto 60cm, enrocamento T1/T2
        3. Vertedouro: Dimensionado para Q100
        """,
        secondary_agent="agente-energia",
        secondary_response="""
        A LT 500kV é apropriada para esta capacidade de UHE.
        Recomendações:
        1. Traçado: Evita ocupação da cota do reservatório
        2. Estruturas: Torres auto-portantes para vãos de 400m
        3. Subestação: Locada em cota elevada para segurança hidrológica
        """,
        routing_scores={"agente-barragens": 0.95, "agente-energia": 0.88},
        ambiguity_reason="Consulta abrange tanto barragem quanto transmissão com scores similares",
    )

    orchestrator = MaestroOrchestrator()
    result = orchestrator.orchestrate(test_input)

    print("\n=== Orchestrator Output ===")
    print(f"Primary Responsibility: {result.primary_responsibility}")
    print(f"Secondary Responsibility: {result.secondary_responsibility}")
    print(f"Cross-Concerns: {result.cross_concerns}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"\nMerged Response:\n{result.merged_response}")
