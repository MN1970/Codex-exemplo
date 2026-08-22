"""
Maestro OS v6.0 — Consensus Engine
Votação super-maioria (3/5) com subset-relevant voting, conflict resolution, e confidence weighting.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics


class ConsensusStatus(Enum):
    """Estados de uma decisão de consenso."""
    PENDING = "pending"           # Aguardando votos
    VOTING = "voting"             # Votos em progresso
    DECIDED = "decided"           # Consenso alcançado
    ESCALATED = "escalated"       # Escalado para humano
    TIED = "tied"                 # Empate (tie-break em progresso)


@dataclass
class Candidate:
    """Proposta de um agente para uma decisão."""
    agent_name: str
    value: any                     # Valor da proposta (ex: R$ 500M, 54 months)
    confidence: float              # Confiança 0..1
    reasoning: Optional[str] = None
    timestamp: Optional[str] = None

    def __hash__(self):
        return hash(self.agent_name)

    def __eq__(self, other):
        if not isinstance(other, Candidate):
            return False
        return self.agent_name == other.agent_name and self.value == other.value


@dataclass
class Vote:
    """Voto de um agente em uma proposta."""
    agent_name: str
    candidate_value: any           # Valor da proposta sendo votada
    confidence_in_vote: float      # Confiança do voto 0..1
    reasoning: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class ConsensusResult:
    """Resultado de uma decisão de consenso."""
    decision_aspect: str           # Ex: "orçamento", "cronograma", "risco"
    status: ConsensusStatus

    # Resultado (se decidido)
    consensus_value: Optional[any] = None
    consensus_confidence: Optional[float] = None
    winning_candidate: Optional[Candidate] = None

    # Auditoria
    votes: List[Vote] = None       # Votos individuais
    total_voters: int = 0
    votes_for_winner: int = 0
    threshold_required: int = 3    # 3/5

    # Escalação (se não decidido)
    escalation_reason: Optional[str] = None
    escalation_to: Optional[str] = None

    def __post_init__(self):
        if self.votes is None:
            self.votes = []


class ConsensusEngine:
    """
    Motor de consenso para votação super-maioria (3/5) em subset-relevant agents.

    Fluxo:
    1. Detectar aspecto (orçamento, cronograma, risco, etc)
    2. Coletar candidatos (propostas de agentes)
    3. Selecionar votantes relevantes (subset dos agentes)
    4. Executar votação (3/5 super-maioria)
    5. Resolver conflitos (tie-break, escalação)
    """

    # Threshold de votação: 3 de 5 votantes devem concordar
    VOTING_THRESHOLD = 3
    MIN_VOTERS_FOR_CONSENSUS = 5

    def __init__(self, escalation_email: Optional[str] = None):
        """
        Inicializa motor de consenso.

        Args:
            escalation_email: Email para escalação se consenso falhar
        """
        self.escalation_email = escalation_email or "maestro@manta.local"

    def determine_relevant_voters(
        self,
        aspect: str,
        available_agents: List[str],
        candidates: List[Candidate]
    ) -> List[str]:
        """
        Seleciona subset-relevant voters para um aspecto específico.

        Lógica: Apenas agentes que têm proposta para o aspecto votam.
        Justificativa: Evita overhead (16 agentes votando sobre tudo).

        Args:
            aspect: Nome do aspecto (ex: "orçamento")
            available_agents: Todos agentes disponíveis
            candidates: Propostas coletadas

        Returns:
            Lista de agentes elegíveis para votar
        """
        # Agentes com proposta automáticamente votam
        voters = set(c.agent_name for c in candidates)

        # Garantir mínimo de votantes para consensus
        if len(voters) < self.MIN_VOTERS_FOR_CONSENSUS:
            # Adicionar agentes especializados conforme aspecto
            specialist_map = {
                "orçamento": ["manta-05-orcamento", "manta-15-advisory"],
                "cronograma": ["manta-07-cronograma", "manta-01-claims"],
                "risco": ["manta-01-claims", "manta-15-advisory"],
                "contratual": ["manta-02-contratual", "manta-01-claims"],
            }

            specialists = specialist_map.get(aspect, [])
            for specialist in specialists:
                if specialist in available_agents and len(voters) < self.MIN_VOTERS_FOR_CONSENSUS:
                    voters.add(specialist)

        return sorted(list(voters))

    def group_candidates_by_value(
        self,
        candidates: List[Candidate]
    ) -> Dict[any, List[Candidate]]:
        """
        Agrupa candidatos pelo valor proposto.
        Candidatos com mesmo valor = voto único para esse grupo.

        Args:
            candidates: Lista de candidatos

        Returns:
            Dict {valor: [candidatos_para_esse_valor]}
        """
        grouped = {}
        for candidate in candidates:
            value_key = self._normalize_value(candidate.value)
            if value_key not in grouped:
                grouped[value_key] = []
            grouped[value_key].append(candidate)
        return grouped

    def _normalize_value(self, value: any) -> str:
        """Normaliza valor para comparação (ex: 500M == 500_000_000)."""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Remove caracteres especiais para comparação
            return value.replace(".", "").replace(",", "").replace("R$", "").strip()
        return str(value)

    def execute_vote(
        self,
        aspect: str,
        candidates: List[Candidate],
        votes: List[Vote]
    ) -> ConsensusResult:
        """
        Executa votação super-maioria (3/5) e retorna resultado.

        Fluxo:
        1. Agrupar candidatos por valor
        2. Contar votos para cada grupo
        3. Se algum grupo ≥ 3/5: consenso ✓
        4. Senão: tie-break ou escalação

        Args:
            aspect: Aspecto sendo votado (ex: "orçamento")
            candidates: Propostas disponíveis
            votes: Votos coletados dos agentes

        Returns:
            ConsensusResult com decisão ou escalação
        """
        if not votes:
            return ConsensusResult(
                decision_aspect=aspect,
                status=ConsensusStatus.PENDING,
                escalation_reason="Nenhum voto recebido",
                escalation_to=self.escalation_email
            )

        # Agrupar candidatos por valor
        grouped = self.group_candidates_by_value(candidates)

        # Contar votos para cada valor
        vote_counts = {}
        for value_key in grouped.keys():
            # Votos que escolheram esse valor
            votes_for_value = [v for v in votes
                               if self._normalize_value(v.candidate_value) == value_key]
            vote_counts[value_key] = votes_for_value

        # Encontrar vencedor
        winner_key = max(vote_counts.keys(),
                        key=lambda k: len(vote_counts[k]))
        winner_votes = vote_counts[winner_key]
        num_votes = len(winner_votes)
        total_voters = len(votes)

        # Verificar consenso (3/5)
        if num_votes >= self.VOTING_THRESHOLD:
            # CONSENSO ALCANÇADO
            winner_candidate = grouped[winner_key][0]  # Usar primeiro candidato do grupo

            # Calcular confidence média dos votos
            avg_confidence = statistics.mean([v.confidence_in_vote for v in winner_votes])

            return ConsensusResult(
                decision_aspect=aspect,
                status=ConsensusStatus.DECIDED,
                consensus_value=winner_candidate.value,
                consensus_confidence=avg_confidence,
                winning_candidate=winner_candidate,
                votes=winner_votes,
                total_voters=total_voters,
                votes_for_winner=num_votes,
                threshold_required=self.VOTING_THRESHOLD
            )
        else:
            # SEM CONSENSO: Escalação
            return self._escalate_decision(
                aspect=aspect,
                candidates=candidates,
                votes=votes,
                top_vote_count=num_votes
            )

    def _escalate_decision(
        self,
        aspect: str,
        candidates: List[Candidate],
        votes: List[Vote],
        top_vote_count: int
    ) -> ConsensusResult:
        """
        Escalona decisão para humano quando consenso falha.

        Cria relatório com:
        - Candidatos e propostas
        - Votos de cada agente
        - Por que não houve consenso
        """
        candidate_summary = "\n".join([
            f"  - {c.agent_name}: {c.value} (confiança {c.confidence})"
            for c in candidates
        ])

        votes_summary = "\n".join([
            f"  - {v.agent_name} votou em {v.candidate_value} (conf {v.confidence_in_vote})"
            for v in votes
        ])

        reason = (
            f"Consenso (3/5) não alcançado para aspecto '{aspect}'.\n"
            f"Votos recebidos: {top_vote_count}/5 (mínimo 3 requerido).\n\n"
            f"Candidatos:\n{candidate_summary}\n\n"
            f"Votos individuais:\n{votes_summary}"
        )

        return ConsensusResult(
            decision_aspect=aspect,
            status=ConsensusStatus.ESCALATED,
            votes=votes,
            total_voters=len(votes),
            votes_for_winner=top_vote_count,
            threshold_required=self.VOTING_THRESHOLD,
            escalation_reason=reason,
            escalation_to=self.escalation_email
        )

    def apply_confidence_weighting(
        self,
        votes: List[Vote],
        threshold: float = 0.7
    ) -> Tuple[List[Vote], List[Vote]]:
        """
        Filtra votos por confiança.
        Votos com confidence < threshold são flagged mas mantidos (auditoria).

        Args:
            votes: Votos a pesar
            threshold: Limite de confiança (0..1, default 0.7)

        Returns:
            (votos_altos_confidence, votos_baixos_confidence)
        """
        high_conf = [v for v in votes if v.confidence_in_vote >= threshold]
        low_conf = [v for v in votes if v.confidence_in_vote < threshold]
        return high_conf, low_conf

    def resolve_tie(
        self,
        tied_candidates: List[Candidate]
    ) -> Optional[Candidate]:
        """
        Resolve empate entre candidatos (tie-break) usando confidence média.

        Se 2+ candidatos têm mesmo número de votos:
        - Elevar o com confidence média maior

        Args:
            tied_candidates: Candidatos em empate

        Returns:
            Candidato vencedor do tie-break, ou None se empate permanece
        """
        if not tied_candidates:
            return None

        # Ordenar por confidence (descendente)
        sorted_candidates = sorted(
            tied_candidates,
            key=lambda c: c.confidence,
            reverse=True
        )

        # Retornar o com maior confidence
        return sorted_candidates[0]

    def format_result_for_audit(self, result: ConsensusResult) -> str:
        """
        Formata resultado de consenso para auditoria (log estruturado).
        """
        lines = [
            f"=== CONSENSO: {result.decision_aspect.upper()} ===",
            f"Status: {result.status.value}",
            f"Votantes: {result.total_voters}/{self.MIN_VOTERS_FOR_CONSENSUS}",
            f"Votos para vencedor: {result.votes_for_winner}/{result.threshold_required}",
        ]

        if result.status == ConsensusStatus.DECIDED:
            lines.extend([
                f"Valor consolidado: {result.consensus_value}",
                f"Confiança: {result.consensus_confidence:.2%}",
                f"Proposta vencedora: {result.winning_candidate.agent_name}",
            ])
        elif result.status == ConsensusStatus.ESCALATED:
            lines.extend([
                f"Escalação para: {result.escalation_to}",
                f"Motivo: {result.escalation_reason.split(chr(10))[0]}",
            ])

        return "\n".join(lines)
