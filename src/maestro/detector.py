"""
Maestro OS v6.0 — Complexity Detector & Agent Pool Selector

Analisa descrição de projeto e decide:
1. Quantos segmentos (S1-S11) aplicáveis
2. Quantidades agentes horizontais (A1-A10) necessários
3. Pool total de agentes (8-16 dinâmico)
4. Ordem de execução (crítico primeiro)
5. Budget de tokens por agente
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import re

# ============================================
# 1. TYPE DEFINITIONS
# ============================================

class ComplexityLevel(Enum):
    SIMPLE = "simple"      # 1 segmento, 8 agentes total
    MEDIUM = "medium"      # 2-3 segmentos, 12 agentes total
    COMPLEX = "complex"    # 4+ segmentos, 16 agentes total


@dataclass
class DetectionResult:
    """Resultado da detecção de complexidade"""

    segments_detected: List[str]        # E.g., ['S6', 'S10', 'S9']
    num_segments: int
    complexity_level: ComplexityLevel

    # Agent pool
    agents_needed: int                  # Total agents 8-16
    agents_vertical: List[str]          # Segmento agents
    agents_horizontal: List[str]        # Atividade agents
    agents_pool: List[str]              # All agents in order (priority)

    # Budget
    token_budget: int                   # 300k-600k
    tokens_per_agent: int               # Budget / agents

    # Justification
    keywords_found: Dict[str, int]      # Matching patterns
    reasoning: str                      # Explanation


# ============================================
# 2. PATTERN MATCHING
# ============================================

SEGMENT_PATTERNS = {
    # S1: Rodovia
    "S1": {
        "keywords": [
            r"\brodovia\b", r"\bpavimentação\b", r"\bcbuq\b", r"\bbgs\b",
            r"\bdn[i-1]t\b", r"\bterraplenagem\b", r"\bsicro\b",
            r"\basfalto\b", r"\bacesso\b", r"\bestrada\b"
        ],
        "agent": "agente-infraestrutura-rodovias"
    },

    # S2: OAE (Obras de Arte Especiais)
    "S2": {
        "keywords": [
            r"\bponte\b", r"\bviaduto\b", r"\boae\b", r"\btúnel\b",
            r"\bfundação\b", r"\best(rut)?ura.*concreto\b", r"\bnbr\s*7187\b",
            r"\bcontraforte\b", r"\barco\b"
        ],
        "agent": "agente-infraestrutura-oae"
    },

    # S3: Ferrovia
    "S3": {
        "keywords": [
            r"\bferrovia\b", r"\btrilho\b", r"\bamv\b", r"\bvia\s+permanente\b",
            r"\bdormente\b", r"\bsinalização\b", r"\blocomotiva\b",
            r"\brampa\b", r"\bbalastro\b"
        ],
        "agent": "agente-infraestrutura-ferrovia"
    },

    # S4: Metrô
    "S4": {
        "keywords": [
            r"\bmetrô\b", r"\bestação\b", r"\bnatm\b", r"\bpsd\b",
            r"\bvlt\b", r"\bsubterrâneo\b", r"\btunelafia\b",
            r"\bcarril\b", r"\btrilho\b"
        ],
        "agent": "agente-infraestrutura-metro"
    },

    # S6: Edificações
    "S6": {
        "keywords": [
            r"\bedificação\b", r"\bconstrução\b", r"\barquitetura\b",
            r"\bmep\b", r"\binfra\b", r"\bentrepisos\b", r"\bfachada\b",
            r"\bprédio\b", r"\bcomercial\b"
        ],
        "agent": "agente-edificacoes"
    },

    # S7: Portos
    "S7": {
        "keywords": [
            r"\bporto\b", r"\bterminal\b", r"\bdragagem\b", r"\bmolhe\b",
            r"\bberço\b", r"\bcalado\b", r"\bcontêiner\b", r"\bgranel\b",
            r"\bcais\b", r"\bpier\b", r"\bpiér\b", r"\bantaq\b",
            r"\bretroárea\b", r"\btup\b", r"\bpianc\b"
        ],
        "agent": "agente-portos"
    },

    # S8: Aeroportos
    "S8": {
        "keywords": [
            r"\baeródromo\b", r"\baeropurto\b", r"\baeroporto\b",
            r"\bpista\b", r"\brwy\b", r"\btaxiway\b", r"\btwy\b",
            r"\banac\b", r"\bicao\b", r"\btps\b", r"\bteca\b",
            r"\bbalizamento\b", r"\bpapi\b", r"\bils\b",
            r"\bgateway\b", r"\bembarcador\b", r"\bjetway\b"
        ],
        "agent": "agente-aeroportos"
    },

    # S9: Saneamento
    "S9": {
        "keywords": [
            r"\bsaneamento\b", r"\beta\b", r"\bete\b", r"\badutor\b",
            r"\besgoto\b", r"\bdrenaem\b", r"\bdrenagem\b",
            r"\babasteciemnto\b", r"\bagua\b",
            r"\blei\s+14\.026\b", r"\baysा\b", r"\bsnis\b",
            r"\belevatória\b", r"\breservatório\b",
            r"\buasb\b", r"\bmbr\b", r"\blodo\b", r"\bdigestor\b"
        ],
        "agent": "agente-saneamento"
    },

    # S10: Energia
    "S10": {
        "keywords": [
            r"\benergia\b", r"\bgeração\b", r"\btransmissão\b", r"\bdistribuição\b",
            r"\blt\b", r"\bsubestação\b", r"\bse\b", r"\baneel\b",
            r"\brap\b", r"\bleilão\b", r"\bons\b", r"\bepe\b",
            r"\bpde\b", r"\btorre\b", r"\bestaiada\b", r"\bcabo\b",
            r"\bacsr\b", r"\bcaa\b", r"\batsr\b", r"\bmre\b",
            r"\bacr\b", r"\bacl\b", r"\bweg\b", r"\bstate\s+grid\b",
            r"\buhe\b", r"\bhydro\b", r"\beólica\b", r"\bpv\b",
            r"\bpch\b", r"\btérmica\b"
        ],
        "agent": "agente-energia"
    },

    # S11: Barragens
    "S11": {
        "keywords": [
            r"\bbarragem\b", r"\bvertedour\b", r"\bcfrd\b", r"\bccr\b",
            r"\brcc\b", r"\brejeito\b", r"\btsf\b", r"\bpnsb\b",
            r"\bicold\b", r"\bcbdb\b", r"\bdique\b", r"\bsigbm\b",
            r"\banm\b", r"\bana\b", r"\blei\s+12\.334\b",
            r"\bfundão\b", r"\bbrumadinho\b", r"\bdescomissionamento\b",
            r"\balteamento\b", r"\bfiltragem\b", r"\bdry\s+stack\b",
            r"\bpae\b", r"\bpaebm\b", r"\bzas\b", r"\bzss\b",
            r"\bhhp\b"
        ],
        "agent": "agente-barragens"
    }
}

ACTIVITY_PATTERNS = {
    # A1: Claims
    "A1": {
        "keywords": [
            r"\bclaim\b", r"\bpleito\b", r"\batraso\b", r"\bimprevisto\b",
            r"\bgeológico\b", r"\bcontingência\b"
        ],
        "agent": "manta-01-claims"
    },

    # A2: Contratual
    "A2": {
        "keywords": [
            r"\bcontrato\b", r"\bcontratuał\b", r"\bprocuramento\b",
            r"\blicitação\b", r"\bedital\b", r"\bcompliance\b",
            r"\btermos\b"
        ],
        "agent": "manta-02-contratual"
    },

    # A5: Orçamento
    "A5": {
        "keywords": [
            r"\borçamento\b", r"\bcusto\b", r"\bcomposição\b",
            r"\bsicro\b", r"\bbdi\b", r"\bencargos\b", r"\bpreço\b",
            r"\bunitário\b", r"\bquantitativo\b"
        ],
        "agent": "manta-05-orcamento"
    },

    # A6: Modelagem
    "A6": {
        "keywords": [
            r"\bmodelagem\b", r"\bbim\b", r"\bfea\b", r"\belementos\s+finitos\b",
            r"\bplaxis\b", r"\bgeostudio\b", r"\bflac\b",
            r"\b3d\b", r"\bcivil\s+3d\b", r"\brevit\b"
        ],
        "agent": "manta-06-modelagem"
    },

    # A7: Cronograma
    "A7": {
        "keywords": [
            r"\bcronograma\b", r"\bplanejamento\b", r"\btempo\b",
            r"\bcaminho\s+crítico\b", r"\bmarcos\b", r"\bfaseamento\b",
            r"\bmeses\b", r"\bduração\b"
        ],
        "agent": "manta-07-cronograma"
    },

    # A13: BD (Business Development)
    "A13": {
        "keywords": [
            r"\bparceria\b", r"\bfinanciamento\b", r"\binvestimento\b",
            r"\bbd\b", r"\bcomercial\b", r"\bnegócio\b"
        ],
        "agent": "manta-13-bd"
    },

    # A14: Apresentações
    "A14": {
        "keywords": [
            r"\bapresentação\b", r"\bslide\b", r"\bdeck\b", r"\bstakeholder\b",
            r"\bcomunicação\b", r"\breunião\b"
        ],
        "agent": "manta-14-apresentacoes"
    },

    # A15: Advisory
    "A15": {
        "keywords": [
            r"\badvisory\b", r"\bviabilidade\b", r"\bfinanceiro\b",
            r"\bmodelo\b", r"\broi\b", r"\bircb\b", r"\bfluxo\b",
            r"\bcaixa\b"
        ],
        "agent": "manta-15-advisory"
    }
}

BASE_HORIZONTAL_AGENTS = ["manta-01-claims", "manta-05-orcamento", "manta-07-cronograma", "manta-15-advisory"]

# ============================================
# 3. DETECTOR LOGIC
# ============================================

class ComplexityDetector:
    """Detecta complexidade e seleciona pool de agentes"""

    def __init__(self):
        self.keywords_found: Dict[str, int] = {}

    def detect(self, project_description: str) -> DetectionResult:
        """
        Analisa descrição e retorna configuração de agentes

        Args:
            project_description: String descrevendo o projeto

        Returns:
            DetectionResult com agentes e budget
        """

        # Normalize input
        text = project_description.lower()
        self.keywords_found = {}

        # 1. Detectar segmentos (S1-S11)
        segments_detected = self._detect_segments(text)

        # 2. Detectar atividades (A1-A10)
        activities_detected = self._detect_activities(text)

        # 3. Calcular complexidade
        complexity = self._calculate_complexity(len(segments_detected))

        # 4. Selecionar agentes
        agents_vertical = [SEGMENT_PATTERNS[s]["agent"] for s in segments_detected]
        agents_horizontal = self._select_horizontal_agents(
            activities_detected, complexity, len(segments_detected)
        )

        agents_pool = agents_vertical + agents_horizontal + ["maestro-router"]
        agents_total = len(agents_pool)

        # 5. Calcular budget de tokens
        token_budget = self._calculate_token_budget(agents_total)
        tokens_per_agent = token_budget // agents_total

        # 6. Gerar reasoning
        reasoning = self._generate_reasoning(
            segments_detected, activities_detected, complexity, agents_total
        )

        return DetectionResult(
            segments_detected=segments_detected,
            num_segments=len(segments_detected),
            complexity_level=complexity,
            agents_needed=agents_total,
            agents_vertical=agents_vertical,
            agents_horizontal=agents_horizontal,
            agents_pool=agents_pool,
            token_budget=token_budget,
            tokens_per_agent=tokens_per_agent,
            keywords_found=self.keywords_found,
            reasoning=reasoning
        )

    def _detect_segments(self, text: str) -> List[str]:
        """Detecta segmentos S1-S11"""
        detected = []

        for segment, patterns in SEGMENT_PATTERNS.items():
            for pattern in patterns["keywords"]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    detected.append(segment)
                    self.keywords_found[segment] = len(matches)
                    break

        return sorted(list(set(detected)))

    def _detect_activities(self, text: str) -> List[str]:
        """Detecta atividades A1-A10"""
        detected = []

        for activity, patterns in ACTIVITY_PATTERNS.items():
            for pattern in patterns["keywords"]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    detected.append(activity)
                    self.keywords_found[activity] = len(matches)
                    break

        return list(set(detected))

    def _calculate_complexity(self, num_segments: int) -> ComplexityLevel:
        """
        Calcula complexidade baseado em número de segmentos

        Simple: 1 segmento → 8 agentes
        Medium: 2-3 segmentos → 12 agentes
        Complex: 4+ segmentos → 16 agentes
        """
        if num_segments <= 1:
            return ComplexityLevel.SIMPLE
        elif num_segments <= 3:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.COMPLEX

    def _select_horizontal_agents(
        self,
        activities_detected: List[str],
        complexity: ComplexityLevel,
        num_segments: int
    ) -> List[str]:
        """Seleciona agentes horizontais baseado em complexidade e atividades"""

        # Base: sempre incluir A1, A5, A7, A15 (claims, orçamento, cronograma, advisory)
        selected = list(BASE_HORIZONTAL_AGENTS)

        # Add detected activities
        for activity in activities_detected:
            agent = ACTIVITY_PATTERNS[activity]["agent"]
            if agent not in selected:
                selected.append(agent)

        # Add based on complexity
        if complexity == ComplexityLevel.MEDIUM:
            # Add A6 (modelagem) for medium projects
            selected.append("manta-06-modelagem")
        elif complexity == ComplexityLevel.COMPLEX:
            # Add A6 (modelagem), A2 (contratual), A14 (apresentações) for complex
            selected.extend([
                "manta-06-modelagem",
                "manta-02-contratual",
                "manta-14-apresentacoes",
                "manta-13-bd"
            ])

        # Deduplicate and limit
        selected = list(set(selected))

        # Ensure we don't exceed max agents
        max_horizontal = 11
        return selected[:max_horizontal]

    def _calculate_token_budget(self, num_agents: int) -> int:
        """
        Calcula budget de tokens dinamicamente

        8 agentes: 300k
        12 agentes: 450k
        16 agentes: 600k

        Escala linear: ~37.5k por agente
        """
        return max(300_000, num_agents * 37_500)

    def _generate_reasoning(
        self,
        segments: List[str],
        activities: List[str],
        complexity: ComplexityLevel,
        num_agents: int
    ) -> str:
        """Gera explicação textual da decisão"""

        segment_names = ", ".join([
            SEGMENT_PATTERNS[s]["keywords"][0].strip(r"\b").replace(r"\b", "").title()
            for s in segments
        ])

        reasoning = f"""
Detected {len(segments)} segments: {segment_names}
Activities: {', '.join(activities) if activities else 'none specified'}
Complexity Level: {complexity.value}
→ Agent Pool: {num_agents} agents (8–16 dynamic scale)
→ Token Budget: {self._calculate_token_budget(num_agents):,} tokens
→ Execution Time Estimate: ~{max(8, 10 - len(segments))} minutes (vs serial ~{45 + len(segments) * 20} min)
        """
        return reasoning.strip()


# ============================================
# 4. TEST / EXAMPLE
# ============================================

if __name__ == "__main__":
    detector = ComplexityDetector()

    # Test cases
    test_cases = [
        "Porto terminal Paranaguá com dragagem, subestação 230kV, ETA e ETE",
        "Rodovia com pavimentação CBUQ e terraplenagem",
        "Hidrelétrica com barragem CFRD e linha de transmissão 500kV",
        "Complexo multi-modal: aeroporto, porto fluvial, rodovia de acesso, subestação, saneamento"
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test}")
        print(f"{'='*60}")

        result = detector.detect(test)
        print(f"Segments: {result.segments_detected}")
        print(f"Complexity: {result.complexity_level.value}")
        print(f"Agents: {result.agents_needed}")
        print(f"Token Budget: {result.token_budget:,}")
        print(f"Reasoning:\n{result.reasoning}")
