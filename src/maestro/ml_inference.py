"""
Maestro OS v6.0 — ML Inference Engine
Real-time predictions: routing suggestions, duration estimates, risk alerts.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from .ml_features import ProjectFeatures, FeatureEngineer
from .ml_trainer import RoutingModel, DurationPredictor, RiskClassifier


@dataclass
class RoutingSuggestion:
    """Sugestão de roteamento (quais agentes)."""
    suggested_agents: List[str]
    confidence: float              # 0–1
    alternatives: List[Tuple[List[str], float]] = None  # [(agents, conf), ...]
    reasoning: str = ""

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


@dataclass
class DurationEstimate:
    """Estimativa de duração."""
    estimated_minutes: int
    estimated_hours: float         # For human readability
    confidence: float              # 0–1
    confidence_interval_mins: Tuple[int, int] = None  # (lower, upper)

    def __post_init__(self):
        self.estimated_hours = self.estimated_minutes / 60.0
        if self.confidence_interval_mins is None:
            # ±15% confidence interval
            margin = int(self.estimated_minutes * 0.15)
            self.confidence_interval_mins = (
                self.estimated_minutes - margin,
                self.estimated_minutes + margin
            )


@dataclass
class RiskAssessment:
    """Avaliação de risco."""
    risk_score: float              # 0–100
    risk_level: str                # 'low', 'medium', 'high'
    risk_factors: List[str]        # Fatores que contribuem
    mitigations: List[str]         # Sugestões de mitigação
    confidence: float              # 0–1

    @staticmethod
    def categorize_risk(score: float) -> str:
        """Categoriza score em nível."""
        if score < 30:
            return "low"
        elif score < 70:
            return "medium"
        else:
            return "high"


@dataclass
class InferenceResult:
    """Resultado completo de inferência."""
    project_id: str
    timestamp: str
    routing: RoutingSuggestion
    duration: DurationEstimate
    risk: RiskAssessment

    def to_summary(self) -> str:
        """Formata sumário legível."""
        return f"""
=== MAESTRO OS INFERENCE ===
Projeto: {self.project_id}

ROTEAMENTO:
  Agentes sugeridos: {', '.join(self.routing.suggested_agents)}
  Confiança: {self.routing.confidence:.1%}

DURAÇÃO:
  Estimado: {self.duration.estimated_hours:.1f} horas ({self.duration.estimated_minutes} min)
  Intervalo: {self.duration.confidence_interval_mins[0]}-{self.duration.confidence_interval_mins[1]} min
  Confiança: {self.duration.confidence:.1%}

RISCO:
  Score: {self.risk.risk_score:.0f}% ({self.risk.risk_level.upper()})
  Fatores: {', '.join(self.risk.risk_factors) if self.risk.risk_factors else 'N/A'}
  Confiança: {self.risk.confidence:.1%}
"""


class MLInferenceEngine:
    """
    Motor de inferência para predições em tempo real.

    Fluxo:
    1. Receber descrição de projeto
    2. Feature engineering (ProjectFeatures)
    3. Invocar 3 modelos em paralelo
    4. Agregador de resultados
    5. Retornar recomendações estruturadas

    Latência alvo: <100ms por predição
    """

    def __init__(
        self,
        routing_model: RoutingModel,
        duration_model: DurationPredictor,
        risk_model: RiskClassifier,
        cache_size: int = 1000
    ):
        """
        Inicializa engine de inferência.

        Args:
            routing_model: Modelo XGBoost de roteamento
            duration_model: Modelo NN de duração
            risk_model: Modelo NN de risco
            cache_size: Tamanho do cache LRU para inferências
        """
        self.routing_model = routing_model
        self.duration_model = duration_model
        self.risk_model = risk_model
        self.cache = {}  # {project_id: InferenceResult}
        self.cache_size = cache_size

    def predict(
        self,
        project_id: str,
        project_description: str,
        features: Optional[ProjectFeatures] = None,
        use_cache: bool = True
    ) -> InferenceResult:
        """
        Prediz roteamento, duração e risco para um projeto.

        Args:
            project_id: ID do projeto
            project_description: Descrição textual
            features: ProjectFeatures (se já extraídas)
            use_cache: Usar cache se disponível

        Returns:
            InferenceResult com recomendações
        """
        # Verificar cache
        if use_cache and project_id in self.cache:
            return self.cache[project_id]

        # Feature engineering
        if features is None:
            features = self._extract_features(project_id, project_description)

        # Converter para vetor
        feature_vector = features.to_feature_vector()

        # Inferências em paralelo (simulado)
        routing_result = self._predict_routing(feature_vector, features)
        duration_result = self._predict_duration(feature_vector, features)
        risk_result = self._predict_risk(feature_vector, features)

        # Agregador
        inference = InferenceResult(
            project_id=project_id,
            timestamp=datetime.utcnow().isoformat(),
            routing=routing_result,
            duration=duration_result,
            risk=risk_result
        )

        # Cachear
        self._cache_put(project_id, inference)

        return inference

    def _extract_features(
        self,
        project_id: str,
        description: str
    ) -> ProjectFeatures:
        """Extrai features de descrição textual."""
        # Stub: inferir com heurísticas
        characteristics = FeatureEngineer.infer_characteristics(description)

        return ProjectFeatures(
            project_id=project_id,
            project_type="multi_segment",
            title=description[:100],
            num_segments=2,
            segments=["S7", "S10"],
            complexity_level="medium",
            budget_range="250M+",
            **characteristics
        )

    def _predict_routing(
        self,
        feature_vector: List[float],
        features: ProjectFeatures
    ) -> RoutingSuggestion:
        """Prediz combinação de agentes."""
        # Invocar modelo
        agents = self.routing_model.predict(feature_vector)

        # Reasoning
        reasoning = (
            f"Detectados {len(features.segments)} segmentos: {', '.join(features.segments)}. "
            f"Complexidade {features.complexity_level} → {len(agents)} agentes selecionados."
        )

        return RoutingSuggestion(
            suggested_agents=agents,
            confidence=0.82,
            reasoning=reasoning,
            alternatives=[
                (agents[:-1], 0.75),  # Alternativa com 1 menos agente
            ]
        )

    def _predict_duration(
        self,
        feature_vector: List[float],
        features: ProjectFeatures
    ) -> DurationEstimate:
        """Prediz duração de execução."""
        # Invocar modelo
        estimated_mins = self.duration_model.predict(feature_vector)

        return DurationEstimate(
            estimated_minutes=estimated_mins,
            confidence=0.85
        )

    def _predict_risk(
        self,
        feature_vector: List[float],
        features: ProjectFeatures
    ) -> RiskAssessment:
        """Prediz score de risco."""
        # Invocar modelo
        risk_score = self.risk_model.predict(feature_vector)

        # Extrair fatores
        risk_factors = []
        if features.has_geotechnical_risk:
            risk_factors.append("Risco geotécnico (barragem/fundação)")
        if features.has_environmental_constraints:
            risk_factors.append("Restrições ambientais (EIA/licença)")
        if features.is_coastal:
            risk_factors.append("Localização costeira (dragagem, salinidade)")

        # Sugestões de mitigação
        mitigations = []
        if features.has_geotechnical_risk:
            mitigations.append("Realizar sondagens adicionais (SPT/CPT)")
        if features.has_environmental_constraints:
            mitigations.append("Iniciar EIA antecipadamente (4+ meses)")
        if features.similar_projects_count < 3:
            mitigations.append("Buscar projetos similares para benchmarking")

        return RiskAssessment(
            risk_score=risk_score,
            risk_level=RiskAssessment.categorize_risk(risk_score),
            risk_factors=risk_factors,
            mitigations=mitigations,
            confidence=0.80
        )

    def _cache_put(self, project_id: str, result: InferenceResult):
        """Armazena resultado em cache (LRU)."""
        self.cache[project_id] = result

        # Limpar cache se cheio
        if len(self.cache) > self.cache_size:
            # Remove item mais antigo (simples FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

    def batch_predict(
        self,
        projects: List[Tuple[str, str]]
    ) -> Dict[str, InferenceResult]:
        """
        Prediz múltiplos projetos em paralelo.

        Args:
            projects: Lista de (project_id, description)

        Returns:
            Dict {project_id: InferenceResult}
        """
        results = {}
        for project_id, description in projects:
            results[project_id] = self.predict(project_id, description)
        return results

    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        return {
            "cache_size": len(self.cache),
            "max_size": self.cache_size,
            "utilization": len(self.cache) / self.cache_size if self.cache_size > 0 else 0,
        }

    def clear_cache(self):
        """Limpa cache."""
        self.cache.clear()


class InferenceService:
    """
    Serviço de alto nível para inferência Maestro OS.

    Responsabilidades:
    - Gerenciar modelos (carregamento, atualização)
    - Coordenar inferências
    - Logging e auditoria
    - Integração com Supabase para feedback
    """

    def __init__(
        self,
        routing_model: RoutingModel,
        duration_model: DurationPredictor,
        risk_model: RiskClassifier
    ):
        self.engine = MLInferenceEngine(routing_model, duration_model, risk_model)
        self.inference_log = []

    def infer(
        self,
        project_id: str,
        project_description: str
    ) -> InferenceResult:
        """
        Realiza inferência e registra em log.

        Args:
            project_id: ID do projeto
            project_description: Descrição

        Returns:
            InferenceResult
        """
        result = self.engine.predict(project_id, project_description)

        # Log para auditoria
        self.inference_log.append({
            "timestamp": result.timestamp,
            "project_id": project_id,
            "routing_agents": len(result.routing.suggested_agents),
            "duration_minutes": result.duration.estimated_minutes,
            "risk_score": result.risk.risk_score,
        })

        return result

    def get_recent_inferences(self, limit: int = 100) -> List[Dict]:
        """Retorna inferências recentes."""
        return self.inference_log[-limit:]
