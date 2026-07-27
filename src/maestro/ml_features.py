"""
Maestro OS v6.0 — ML Features & Data Pipeline
Feature engineering for routing model, duration predictor, risk classifier.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class ProjectComplexity(Enum):
    """Complexidade de projeto (alvo para classificação)."""
    SIMPLE = "simple"              # 1 segmento, 8 agentes
    MEDIUM = "medium"              # 2-3 segmentos, 12 agentes
    COMPLEX = "complex"            # 4+ segmentos, 16 agentes


class BudgetRange(Enum):
    """Faixa orçamentária."""
    SMALL = "0-50M"                # < R$ 50M
    MEDIUM = "50-250M"             # R$ 50–250M
    LARGE = "250M+"                # > R$ 250M


@dataclass
class ProjectFeatures:
    """
    Features de um projeto para ML.

    Utilizado por:
    - Routing model: qual combinação de agentes?
    - Duration predictor: quanto tempo levará?
    - Risk classifier: qual risco (0–100%)?
    """

    # Identificação
    project_id: str
    project_type: str              # 'porto', 'barragem', 'energia', 'multi_segment', etc
    title: str

    # Complexidade & Escopo
    num_segments: int              # Quantos segmentos (S1–S11) envolvidos?
    segments: List[str]            # Ex: ['S7', 'S10', 'S9']
    complexity_level: str           # 'simple', 'medium', 'complex'

    # Orçamento
    budget_range: str              # '0-50M', '50-250M', '250M+'
    budget_numeric: Optional[float] = None  # Em reais (se conhecido)

    # Localização & Contexto
    location: Optional[str] = None
    is_urban: bool = False
    is_coastal: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Histórico & Similaridade
    similar_projects_count: int = 0  # Projetos similares no histórico
    similar_avg_duration_days: Optional[int] = None
    similar_avg_cost: Optional[float] = None

    # Características Técnicas
    has_geotechnical_risk: bool = False
    has_environmental_constraints: bool = False
    has_indigenous_land: bool = False
    is_regulated_sector: bool = False  # ANEEL, ANTAQ, etc

    # Cronograma
    timeline_months: Optional[int] = None
    has_seasonal_constraints: bool = False

    # Execução Prévia
    is_follow_up_project: bool = False
    previous_phase: Optional[str] = None  # 'estudo_previo', 'projeto_basico', etc

    def to_feature_vector(self) -> List[float]:
        """
        Converte features para vetor numérico para ML.

        Ordem importante: deve ser consistente entre treinamento e inferência.

        Returns:
            List[float] com features normalizadas
        """
        vector = [
            # Complexidade (one-hot encoded)
            1.0 if self.complexity_level == "simple" else 0.0,
            1.0 if self.complexity_level == "medium" else 0.0,
            1.0 if self.complexity_level == "complex" else 0.0,

            # Num segmentos (0-5 range, normalized)
            min(self.num_segments / 5.0, 1.0),

            # Budget range (one-hot encoded)
            1.0 if self.budget_range == "0-50M" else 0.0,
            1.0 if self.budget_range == "50-250M" else 0.0,
            1.0 if self.budget_range == "250M+" else 0.0,

            # Budget numeric (log-normalized, R$ 0-1B range)
            math.log10(max(self.budget_numeric or 10_000_000, 10_000_000) / 10_000_000) / 3.0 if self.budget_numeric else 0.0,

            # Localização & Contexto
            1.0 if self.is_urban else 0.0,
            1.0 if self.is_coastal else 0.0,

            # Histórico
            min(self.similar_projects_count / 10.0, 1.0),

            # Características Técnicas
            1.0 if self.has_geotechnical_risk else 0.0,
            1.0 if self.has_environmental_constraints else 0.0,
            1.0 if self.has_indigenous_land else 0.0,
            1.0 if self.is_regulated_sector else 0.0,

            # Cronograma
            min((self.timeline_months or 12) / 60.0, 1.0),  # 0-60 meses range
            1.0 if self.has_seasonal_constraints else 0.0,

            # Execução Prévia
            1.0 if self.is_follow_up_project else 0.0,
        ]

        return vector

    @property
    def feature_count(self) -> int:
        """Total de features numéricas."""
        return len(self.to_feature_vector())


@dataclass
class ExecutionTrace:
    """
    Traço de execução de um projeto (histórico para treinamento).
    Armazenado em Supabase para feedback loop.
    """

    # Identificação
    project_id: str
    execution_id: str
    timestamp: str                 # ISO 8601

    # Features de entrada (snapshot no início)
    input_features: ProjectFeatures

    # Saídas reais (ground truth)
    actual_complexity: str         # 'simple', 'medium', 'complex'
    actual_agents_selected: List[str]  # Agentes que realmente foram selecionados
    actual_duration_minutes: int   # Tempo real de execução
    actual_cost: Optional[float] = None

    # Métricas de Qualidade
    consensus_rate: float = 0.0    # % decisões auto-resolvidas
    escalations_count: int = 0
    errors_count: int = 0

    # Índice de Sucesso
    success: bool = True           # Completou sem falhas críticas
    satisfaction_score: Optional[float] = None  # 1-5 (cliente)

    def to_training_record(self) -> Dict:
        """Converte trace para record de treinamento."""
        return {
            "features": self.input_features.to_feature_vector(),
            "target_complexity": self.actual_complexity,
            "target_duration": self.actual_duration_minutes,
            "target_cost": self.actual_cost,
            "agents_count": len(self.actual_agents_selected),
            "consensus_rate": self.consensus_rate,
            "success": self.success,
        }


class FeatureEngineer:
    """
    Engenheiro de features para ML pipeline.

    Responsabilidades:
    - Extrair features de descrição textual de projeto
    - Normalizar features para vetor numérico
    - Gerar features derivadas (lat/lon → is_coastal, etc)
    """

    # Keyword mappings para detectar características
    COASTAL_KEYWORDS = ["porto", "marinha", "costa", "litoral", "oceano", "mar"]
    URBAN_KEYWORDS = ["cidade", "urbano", "metrô", "metro", "metropolitana", "cidade"]
    GEOTECHNICAL_KEYWORDS = ["barragem", "fundação", "escavação", "solo", "túnel"]
    REGULATED_KEYWORDS = ["aneel", "antaq", "anac", "ana", "lei 12.334", "pnsb"]
    ENVIRONMENTAL_KEYWORDS = ["ambiental", "eia", "rima", "licença", "sustentabilidade"]

    # Mapeamento de tipos de projeto → complexidade default
    COMPLEXITY_BY_TYPE = {
        "rodovia": "simple",
        "pontes": "medium",
        "porto": "medium",
        "energia": "complex",
        "barragem": "complex",
        "multi_segment": "complex",
        "metro": "complex",
    }

    # Mapeamento de segmentos → estimativa de duração
    DURATION_BY_SEGMENT = {
        "S1": 24,  # Rodovia: 24 meses
        "S2": 30,  # OAE: 30 meses
        "S3": 36,  # Ferrovia: 36 meses
        "S4": 42,  # Metrô: 42 meses
        "S6": 18,  # Edificações: 18 meses
        "S7": 48,  # Portos: 48 meses
        "S8": 36,  # Aeroportos: 36 meses
        "S9": 24,  # Saneamento: 24 meses
        "S10": 30, # Energia: 30 meses
        "S11": 40, # Barragens: 40 meses
    }

    @staticmethod
    def infer_characteristics(project_description: str) -> Dict[str, bool]:
        """
        Infere características booleanas da descrição textual.

        Args:
            project_description: Descrição do projeto

        Returns:
            Dict com {is_urban, is_coastal, has_geotechnical_risk, etc}
        """
        desc_lower = project_description.lower()

        return {
            "is_urban": any(kw in desc_lower for kw in FeatureEngineer.URBAN_KEYWORDS),
            "is_coastal": any(kw in desc_lower for kw in FeatureEngineer.COASTAL_KEYWORDS),
            "has_geotechnical_risk": any(kw in desc_lower for kw in FeatureEngineer.GEOTECHNICAL_KEYWORDS),
            "has_environmental_constraints": any(kw in desc_lower for kw in FeatureEngineer.ENVIRONMENTAL_KEYWORDS),
            "is_regulated_sector": any(kw in desc_lower for kw in FeatureEngineer.REGULATED_KEYWORDS),
        }

    @staticmethod
    def estimate_duration_from_segments(segments: List[str]) -> int:
        """
        Estima duração esperada baseado em segmentos.

        Args:
            segments: Lista de códigos de segmento ['S7', 'S10', 'S9']

        Returns:
            Duração estimada em minutos (paralelo: max, serial: soma)
        """
        if not segments:
            return 600  # 10 minutos default

        # Estimar duração paralela (max de todos + overhead)
        max_duration = max(
            FeatureEngineer.DURATION_BY_SEGMENT.get(s, 24)
            for s in segments
        )

        # Adicionar overhead de paralelismo (fan-out, consensus, aggregate)
        overhead_minutes = 50  # 50 minutos para fan-out + consensus + aggregate

        return max_duration + overhead_minutes

    @staticmethod
    def suggest_similar_projects(
        features: ProjectFeatures,
        historical_traces: List[ExecutionTrace]
    ) -> Tuple[List[ExecutionTrace], float]:
        """
        Encontra projetos similares no histórico.

        Similaridade baseada em:
        - Mesmo complexidade_level
        - Mesmo budget_range
        - Mesmos segmentos (ou overlap significativo)

        Args:
            features: Features do projeto atual
            historical_traces: Histórico de execuções

        Returns:
            (similar_projects, avg_similarity_score)
        """
        similar = []

        for trace in historical_traces:
            # Score de similaridade
            score = 0.0

            # Mesma complexidade: +0.4
            if trace.input_features.complexity_level == features.complexity_level:
                score += 0.4

            # Mesmo budget_range: +0.3
            if trace.input_features.budget_range == features.budget_range:
                score += 0.3

            # Overlap de segmentos: +0.3
            overlap = len(set(features.segments) & set(trace.input_features.segments))
            segment_sim = overlap / max(len(features.segments), 1)
            score += segment_sim * 0.3

            if score >= 0.5:  # Threshold para similaridade
                similar.append((trace, score))

        similar.sort(key=lambda x: x[1], reverse=True)
        traces = [t[0] for t in similar[:10]]  # Top 10
        avg_score = sum(s[1] for s in similar[:10]) / max(len(similar), 1) if similar else 0.0

        return traces, avg_score
