"""
Maestro OS v6.0 — Workflow DSL Parser
Parser YAML → AST com validação de fases e agentes.
"""

import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class Phase(Enum):
    """Fases de execução de workflow."""
    FAN_OUT = "fan_out"             # Paralelo: invoca 8-16 agentes
    CONSENSUS = "consensus"         # Votação: 3/5 super-maioria
    AGGREGATE = "aggregate"         # Consolidação: DOCX + JSON + Matrix


@dataclass
class ProjectMetadata:
    """Metadados do projeto."""
    id: str
    type: str                       # 'porto', 'barragem', 'energia', 'multi_segment'
    title: str
    location: Optional[str] = None
    budget_range: Optional[str] = None  # '0-50M', '50-250M', '250M+'
    segments: List[str] = field(default_factory=list)  # ['S6', 'S10', 'S9']


@dataclass
class AgentDeclaration:
    """Declaração de agente no workflow."""
    name: str
    tier: str = "sonnet"            # 'haiku', 'sonnet', 'opus'
    rag_prefix: Optional[str] = None
    tools: List[str] = field(default_factory=lambda: ["Read", "Grep", "Bash"])


@dataclass
class FanOutPhase:
    """Fase de fan-out (paralelo)."""
    phase: Phase = Phase.FAN_OUT
    agents: List[str] = field(default_factory=list)  # ['agente-portos', 'agente-energia', ...]
    shared_context: Dict[str, Any] = field(default_factory=dict)
    prompts: Dict[str, str] = field(default_factory=dict)  # {agent_name: prompt}
    timeout_per_agent: str = "45min"
    store_outputs: bool = True


@dataclass
class Decision:
    """Decisão individual a votar."""
    aspect: str                     # 'orçamento', 'cronograma', 'risco'
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    voting_rule: str = "super_majority"
    threshold: int = 3              # 3/5
    consensus_prompt: str = ""
    fallback: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConsensusPhase:
    """Fase de consenso (votação)."""
    phase: Phase = Phase.CONSENSUS
    decisions: List[Decision] = field(default_factory=list)
    escalation_email: Optional[str] = None


@dataclass
class AggregatePhase:
    """Fase de agregação (consolidação)."""
    phase: Phase = Phase.AGGREGATE
    format: str = "docx"
    template: Optional[str] = None
    sections: List[Dict[str, Any]] = field(default_factory=list)
    output_path: str = "output"
    also_output: Optional[str] = None  # 'json', etc
    save_decision_trail: bool = True


@dataclass
class WorkflowDSL:
    """AST raiz de um workflow Maestro OS."""
    project: ProjectMetadata
    agents: List[AgentDeclaration]
    phase_1_fan_out: Optional[FanOutPhase] = None
    phase_2_consensus: Optional[ConsensusPhase] = None
    phase_3_aggregate: Optional[AggregatePhase] = None


class WorkflowParser:
    """
    Parser de Workflow DSL YAML.

    Fluxo:
    1. parse(yaml_str) → WorkflowDSL (AST)
    2. validate(workflow) → ValidationResult
    3. Orchestrator executa
    """

    # Agentes conhecidos (validação)
    KNOWN_AGENTS = {
        # Horizontais
        "maestro", "manta-01-claims", "manta-02-contratual",
        "manta-04-imobiliario", "manta-05-orcamento", "manta-06-modelagem",
        "manta-07-cronograma", "manta-13-bd", "manta-14-apresentacoes",
        "manta-15-advisory", "manta-16-arquiteto-ia",
        # Verticais
        "agente-infraestrutura", "agente-edificacoes", "agente-portos",
        "agente-aeroportos", "agente-saneamento", "agente-energia", "agente-barragens",
        # Aliases
        "agente-portos", "agente-energia", "agente-saneamento",
    }

    # Tipos de projeto válidos
    VALID_PROJECT_TYPES = [
        "porto", "barragem", "energia", "rodovia", "metro",
        "aeroporto", "saneamento", "multi_segment"
    ]

    def parse(self, yaml_content: str) -> WorkflowDSL:
        """
        Parse YAML → AST (WorkflowDSL).

        Args:
            yaml_content: Conteúdo YAML do workflow

        Returns:
            WorkflowDSL (AST)

        Raises:
            ValueError: Se YAML inválido ou sintaxe incorreta
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML inválido: {e}")

        if not data:
            raise ValueError("Workflow vazio (YAML vazio)")

        # Parse project
        project_data = data.get("project", {})
        project = ProjectMetadata(
            id=project_data.get("id", "unknown"),
            type=project_data.get("type", "multi_segment"),
            title=project_data.get("title", "Untitled"),
            location=project_data.get("location"),
            budget_range=project_data.get("budget_range"),
            segments=project_data.get("segments", [])
        )

        # Parse agents
        agents_data = data.get("agents", [])
        agents = [
            AgentDeclaration(
                name=a.get("name"),
                tier=a.get("tier", "sonnet"),
                rag_prefix=a.get("rag_prefix"),
                tools=a.get("tools", ["Read", "Grep", "Bash"])
            )
            for a in agents_data
        ]

        # Parse phases
        phase_1 = self._parse_fan_out(data.get("phase_1_fan_out") or data.get("phase_1_parallel"))
        phase_2 = self._parse_consensus(data.get("phase_2_consensus"))
        phase_3 = self._parse_aggregate(data.get("phase_3_aggregate"))

        workflow = WorkflowDSL(
            project=project,
            agents=agents,
            phase_1_fan_out=phase_1,
            phase_2_consensus=phase_2,
            phase_3_aggregate=phase_3
        )

        return workflow

    def _parse_fan_out(self, data: Optional[Dict]) -> Optional[FanOutPhase]:
        """Parse fase fan-out."""
        if not data:
            return None

        return FanOutPhase(
            agents=data.get("agents", []),
            shared_context=data.get("shared_context", {}),
            prompts=data.get("prompts", {}),
            timeout_per_agent=data.get("timeout", "45min"),
            store_outputs=data.get("store_outputs", True)
        )

    def _parse_consensus(self, data: Optional[Dict]) -> Optional[ConsensusPhase]:
        """Parse fase consensus."""
        if not data:
            return None

        decisions = []
        for key, decision_data in data.items():
            if key.startswith("decision_"):
                decisions.append(Decision(
                    aspect=decision_data.get("aspect", ""),
                    candidates=decision_data.get("candidates", []),
                    voting_rule=decision_data.get("voting_rule", "super_majority"),
                    threshold=decision_data.get("threshold", 3),
                    consensus_prompt=decision_data.get("consensus_prompt", ""),
                    fallback=decision_data.get("fallback", {})
                ))

        return ConsensusPhase(decisions=decisions)

    def _parse_aggregate(self, data: Optional[Dict]) -> Optional[AggregatePhase]:
        """Parse fase aggregate."""
        if not data:
            return None

        return AggregatePhase(
            format=data.get("format", "docx"),
            template=data.get("template"),
            sections=data.get("sections", []),
            output_path=data.get("output_path", "output"),
            also_output=data.get("also_output"),
            save_decision_trail=data.get("save_decision_trail", True)
        )

    def validate(self, workflow: WorkflowDSL) -> Dict[str, List[str]]:
        """
        Valida workflow.

        Args:
            workflow: WorkflowDSL a validar

        Returns:
            Dict {error_type: [messages]} ou {} se válido
        """
        errors = {
            "project": [],
            "agents": [],
            "phases": [],
        }

        # Validar projeto
        if workflow.project.type not in self.VALID_PROJECT_TYPES:
            errors["project"].append(
                f"Tipo de projeto inválido: {workflow.project.type}. "
                f"Válidos: {', '.join(self.VALID_PROJECT_TYPES)}"
            )

        # Validar agentes
        for agent in workflow.agents:
            if agent.name not in self.KNOWN_AGENTS:
                errors["agents"].append(
                    f"Agente desconhecido: {agent.name}"
                )

        # Validar fases
        if not workflow.phase_1_fan_out:
            errors["phases"].append("Fase 1 (fan-out) é obrigatória")
        else:
            for agent in workflow.phase_1_fan_out.agents:
                if agent not in [a.name for a in workflow.agents]:
                    errors["phases"].append(
                        f"Agente '{agent}' em phase_1 não declarado"
                    )

        if workflow.phase_2_consensus:
            for decision in workflow.phase_2_consensus.decisions:
                if not decision.aspect:
                    errors["phases"].append("Decisão sem 'aspect' definido")
                if decision.threshold < 1:
                    errors["phases"].append(
                        f"Threshold inválido: {decision.threshold} (mínimo 1)"
                    )

        # Limpar dicts vazios
        return {k: v for k, v in errors.items() if v}

    def format_workflow_summary(self, workflow: WorkflowDSL) -> str:
        """Retorna sumário legível do workflow."""
        lines = [
            f"=== WORKFLOW: {workflow.project.title} ===",
            f"Tipo: {workflow.project.type}",
            f"Localização: {workflow.project.location or 'N/A'}",
            f"Segmentos: {', '.join(workflow.project.segments) or 'N/A'}",
            f"\nAgentes ({len(workflow.agents)}):",
        ]

        for agent in workflow.agents:
            lines.append(f"  - {agent.name} ({agent.tier})")

        lines.append("\nFases:")
        if workflow.phase_1_fan_out:
            lines.append(f"  1. Fan-out: {', '.join(workflow.phase_1_fan_out.agents)}")
        if workflow.phase_2_consensus:
            aspects = [d.aspect for d in workflow.phase_2_consensus.decisions]
            lines.append(f"  2. Consensus: {', '.join(aspects)}")
        if workflow.phase_3_aggregate:
            lines.append(f"  3. Aggregate: {workflow.phase_3_aggregate.format.upper()}")

        return "\n".join(lines)
