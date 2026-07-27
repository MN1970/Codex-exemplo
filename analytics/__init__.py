"""
Phase 4.2 Advanced Analytics — Public API

Main exports for common use cases.
"""

__version__ = '1.0.0'
__author__ = 'Manta Associados'

# Core pipeline
from analytics.analytics_pipeline import (
    AnalyticsPipeline,
    RoutingEvent,
    RoutingOutcome,
    UserCohort,
    AggregatedMetrics
)

# BI Integration
from analytics.bi_integration import (
    BIDashboardManager,
    KPIDefinition,
    DashboardTemplate
)

# Predictive Models
from analytics.predictive_models import (
    VolumeForecaster,
    DriftDetector,
    AnomalyDetector,
    ModelEvaluator,
    PredictiveModelManager
)

# Monitoring & Alerting
from analytics.monitoring import (
    HealthChecker,
    AlertingEngine,
    Alert,
    AlertSeverity,
    HealthCheckResult,
    IncidentEscalation,
    NotificationHandlers
)

__all__ = [
    'AnalyticsPipeline',
    'RoutingEvent',
    'RoutingOutcome',
    'UserCohort',
    'AggregatedMetrics',
    'BIDashboardManager',
    'KPIDefinition',
    'DashboardTemplate',
    'VolumeForecaster',
    'DriftDetector',
    'AnomalyDetector',
    'ModelEvaluator',
    'PredictiveModelManager',
    'HealthChecker',
    'AlertingEngine',
    'Alert',
    'AlertSeverity',
    'HealthCheckResult',
    'IncidentEscalation',
    'NotificationHandlers'
]
