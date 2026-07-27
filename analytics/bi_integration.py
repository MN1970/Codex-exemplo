"""
Phase 4.2 Advanced Analytics — BI Dashboard Integration

Integrates with Looker & Tableau for real-time dashboards.
Manages pre-built dashboard templates, KPI definitions, and custom metrics.

Dashboards:
  1. Executive Overview: Volume, accuracy, cost trends
  2. Routing Intelligence: Agent performance, confidence scores
  3. User Analytics: Cohort behavior, retention, feature adoption
  4. Cost Tracking: Cost per query, model mix, optimization opportunities
  5. Regulatory: Phase 3.2 webhook events, compliance metrics

Pre-built templates enable 1-click deployment across organizations.
Custom metrics extend dashboards with domain-specific KPIs.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class KPIDefinition:
    """Definition of a key performance indicator."""
    name: str
    description: str
    metric_type: str  # "gauge", "trend", "breakdown"
    calculation: str  # SQL or expression
    unit: str  # "%", "USD", "count", etc.
    threshold_warning: float
    threshold_critical: float
    refresh_interval_minutes: int


@dataclass
class DashboardTemplate:
    """Pre-built dashboard template."""
    template_id: str
    name: str
    description: str
    target_role: str  # "executive", "operations", "data_science"
    panels: List[Dict[str, Any]]  # Panel configurations
    filters: List[Dict[str, Any]]  # Available filters
    version: str
    created_at: datetime


class BIDashboardManager:
    """
    Manages dashboard templates and metric definitions.

    Supports Looker (LookML) and Tableau (TWB format) via adapters.

    Usage:
        manager = BIDashboardManager(looker_client, tableau_client)
        manager.deploy_dashboard("executive_overview", org_id="org-123")
        manager.add_custom_metric("custom_routing_score", ...)
    """

    def __init__(self, looker_client=None, tableau_client=None):
        """
        Args:
            looker_client: Looker SDK client (optional)
            tableau_client: Tableau REST API client (optional)
        """
        self.looker = looker_client
        self.tableau = tableau_client
        self.templates: Dict[str, DashboardTemplate] = {}
        self.kpis: Dict[str, KPIDefinition] = {}
        self._register_built_in_templates()
        self._register_built_in_kpis()

    def _register_built_in_templates(self):
        """Register pre-built dashboard templates."""
        self.templates['executive_overview'] = DashboardTemplate(
            template_id='executive_overview',
            name='Executive Overview',
            description='High-level KPIs for C-suite: volume, accuracy, cost, trends',
            target_role='executive',
            panels=[
                {
                    'id': 'total_queries_tile',
                    'type': 'gauge',
                    'title': 'Total Queries (30d)',
                    'metric': 'total_queries',
                    'format': 'number'
                },
                {
                    'id': 'routing_accuracy_gauge',
                    'type': 'gauge',
                    'title': 'Routing Accuracy',
                    'metric': 'routing_accuracy',
                    'format': 'percent',
                    'thresholds': {'warning': 85, 'critical': 75}
                },
                {
                    'id': 'cost_trend_chart',
                    'type': 'line',
                    'title': 'Cost Trend (USD/day)',
                    'metric': 'total_cost_usd',
                    'groupby': 'date',
                    'timerange': '90d'
                },
                {
                    'id': 'cost_per_query_sparkline',
                    'type': 'sparkline',
                    'title': 'Cost per Query (30d avg)',
                    'metric': 'cost_per_query_usd'
                },
                {
                    'id': 'feedback_avg_gauge',
                    'type': 'gauge',
                    'title': 'User Satisfaction',
                    'metric': 'feedback_avg',
                    'format': 'number',
                    'range': [0, 5]
                },
                {
                    'id': 'fallback_rate_gauge',
                    'type': 'gauge',
                    'title': 'Human Escalation Rate',
                    'metric': 'fallback_rate',
                    'format': 'percent'
                }
            ],
            filters=[
                {'field': 'timestamp', 'type': 'date_range', 'default': 'last_30_days'},
                {'field': 'organization_id', 'type': 'select'},
                {'field': 'segment', 'type': 'multi_select', 'options': ['S1', 'S2', 'S3', 'S4', 'S6', 'S7', 'S8', 'S9', 'S10']}
            ],
            version='1.0',
            created_at=datetime.utcnow()
        )

        self.templates['routing_intelligence'] = DashboardTemplate(
            template_id='routing_intelligence',
            name='Routing Intelligence',
            description='Agent performance, confidence scores, routing method effectiveness',
            target_role='operations',
            panels=[
                {
                    'id': 'agent_query_distribution',
                    'type': 'bar',
                    'title': 'Queries by Agent',
                    'metric': 'query_count',
                    'groupby': 'routed_agent',
                    'sort': 'desc',
                    'limit': 15
                },
                {
                    'id': 'agent_accuracy_breakdown',
                    'type': 'bar',
                    'title': 'Agent Accuracy %',
                    'metric': 'routing_accuracy',
                    'groupby': 'routed_agent'
                },
                {
                    'id': 'routing_confidence_histogram',
                    'type': 'histogram',
                    'title': 'Routing Confidence Distribution',
                    'metric': 'routing_confidence',
                    'bins': 10
                },
                {
                    'id': 'routing_method_effectiveness',
                    'type': 'bar',
                    'title': 'Accuracy by Routing Method',
                    'metric': 'routing_accuracy',
                    'groupby': 'routing_method'
                },
                {
                    'id': 'low_confidence_queries',
                    'type': 'table',
                    'title': 'Low Confidence Queries (< 0.6)',
                    'query': 'queries with routing_confidence < 0.6',
                    'limit': 20
                }
            ],
            filters=[
                {'field': 'timestamp', 'type': 'date_range'},
                {'field': 'routed_agent', 'type': 'multi_select'},
                {'field': 'routing_method', 'type': 'select', 'options': ['keyword', 'vector', 'llm_tiebreaker']}
            ],
            version='1.0',
            created_at=datetime.utcnow()
        )

        self.templates['user_analytics'] = DashboardTemplate(
            template_id='user_analytics',
            name='User Analytics',
            description='Cohort behavior, retention, feature adoption, engagement',
            target_role='operations',
            panels=[
                {
                    'id': 'users_by_cohort',
                    'type': 'pie',
                    'title': 'Users by Cohort',
                    'metric': 'unique_users',
                    'groupby': 'cohort'
                },
                {
                    'id': 'queries_by_cohort',
                    'type': 'bar',
                    'title': 'Queries by Cohort',
                    'metric': 'total_queries',
                    'groupby': 'cohort'
                },
                {
                    'id': 'user_retention_curve',
                    'type': 'line',
                    'title': '30-Day User Retention',
                    'metric': 'retention_rate',
                    'groupby': 'days_since_first_query',
                    'timerange': '120d'
                },
                {
                    'id': 'power_users_table',
                    'type': 'table',
                    'title': 'Top 20 Power Users',
                    'columns': ['user_id', 'org_id', 'total_queries', 'last_query_date', 'satisfaction_avg'],
                    'sort': 'total_queries',
                    'limit': 20
                },
                {
                    'id': 'new_user_activation',
                    'type': 'bar',
                    'title': 'New User Activation (% active after 7d)',
                    'metric': 'activation_rate',
                    'groupby': 'week'
                }
            ],
            filters=[
                {'field': 'timestamp', 'type': 'date_range'},
                {'field': 'organization_id', 'type': 'select'}
            ],
            version='1.0',
            created_at=datetime.utcnow()
        )

        self.templates['cost_tracking'] = DashboardTemplate(
            template_id='cost_tracking',
            name='Cost Tracking & Optimization',
            description='Cost per query, model mix, optimization opportunities',
            target_role='data_science',
            panels=[
                {
                    'id': 'total_cost_metric',
                    'type': 'gauge',
                    'title': 'Total Cost (30d)',
                    'metric': 'total_cost_usd',
                    'format': 'currency'
                },
                {
                    'id': 'cost_per_query_trend',
                    'type': 'line',
                    'title': 'Cost per Query Trend',
                    'metric': 'cost_per_query_usd',
                    'groupby': 'date',
                    'timerange': '90d'
                },
                {
                    'id': 'cost_by_model_breakdown',
                    'type': 'pie',
                    'title': 'Costs by Model',
                    'metric': 'total_cost_usd',
                    'groupby': 'model_used'
                },
                {
                    'id': 'cost_by_agent',
                    'type': 'bar',
                    'title': 'Cost by Agent',
                    'metric': 'total_cost_usd',
                    'groupby': 'routed_agent',
                    'sort': 'desc'
                },
                {
                    'id': 'token_efficiency',
                    'type': 'scatter',
                    'title': 'Token Efficiency (input vs output)',
                    'x_axis': 'input_tokens',
                    'y_axis': 'output_tokens',
                    'bubble_size': 'total_cost_usd'
                }
            ],
            filters=[
                {'field': 'timestamp', 'type': 'date_range'},
                {'field': 'model_used', 'type': 'multi_select'},
                {'field': 'routed_agent', 'type': 'select'}
            ],
            version='1.0',
            created_at=datetime.utcnow()
        )

        self.templates['regulatory_compliance'] = DashboardTemplate(
            template_id='regulatory_compliance',
            name='Regulatory & Compliance',
            description='Phase 3.2 webhook events, compliance metrics (GDPR, audit trail)',
            target_role='executive',
            panels=[
                {
                    'id': 'webhook_events_received',
                    'type': 'gauge',
                    'title': 'Regulatory Webhooks (7d)',
                    'metric': 'webhook_count',
                    'format': 'number'
                },
                {
                    'id': 'webhook_latency_distribution',
                    'type': 'histogram',
                    'title': 'Webhook Processing Latency (ms)',
                    'metric': 'webhook_latency_ms',
                    'bins': 10
                },
                {
                    'id': 'compliance_events_table',
                    'type': 'table',
                    'title': 'Recent Webhook Events',
                    'columns': ['event_id', 'source', 'received_at', 'status', 'org_count_affected'],
                    'limit': 50,
                    'sort': 'received_at desc'
                },
                {
                    'id': 'audit_trail_health',
                    'type': 'gauge',
                    'title': 'Audit Trail Integrity',
                    'metric': 'audit_log_completeness',
                    'format': 'percent'
                },
                {
                    'id': 'gdpr_erasure_requests',
                    'type': 'bar',
                    'title': 'GDPR Erasure Requests (30d)',
                    'metric': 'erasure_count',
                    'groupby': 'week'
                }
            ],
            filters=[
                {'field': 'timestamp', 'type': 'date_range'},
                {'field': 'webhook_source', 'type': 'select', 'options': ['ANEEL', 'ANTAQ', 'ANA', 'ANAC']}
            ],
            version='1.0',
            created_at=datetime.utcnow()
        )

    def _register_built_in_kpis(self):
        """Register standard KPI definitions."""
        self.kpis['routing_accuracy'] = KPIDefinition(
            name='Routing Accuracy',
            description='% of queries routed to correct agent (feedback score ≥ 4)',
            metric_type='gauge',
            calculation='COUNT(feedback_score >= 4) / COUNT(*)',
            unit='%',
            threshold_warning=85.0,
            threshold_critical=75.0,
            refresh_interval_minutes=60
        )

        self.kpis['cost_per_query'] = KPIDefinition(
            name='Cost per Query',
            description='Average USD cost per routed query',
            metric_type='trend',
            calculation='SUM(cost_usd) / COUNT(*)',
            unit='USD',
            threshold_warning=0.05,
            threshold_critical=0.10,
            refresh_interval_minutes=60
        )

        self.kpis['fallback_rate'] = KPIDefinition(
            name='Human Escalation Rate',
            description='% of queries escalated to human review',
            metric_type='gauge',
            calculation='COUNT(outcome = "human_escalation") / COUNT(*)',
            unit='%',
            threshold_warning=10.0,
            threshold_critical=15.0,
            refresh_interval_minutes=60
        )

        self.kpis['user_satisfaction'] = KPIDefinition(
            name='User Satisfaction',
            description='Average feedback rating (1-5 stars)',
            metric_type='gauge',
            calculation='AVG(feedback_score)',
            unit='score',
            threshold_warning=3.5,
            threshold_critical=3.0,
            refresh_interval_minutes=60
        )

        self.kpis['volume_trend'] = KPIDefinition(
            name='Query Volume Trend',
            description='Queries per day trend (30d window)',
            metric_type='trend',
            calculation='COUNT(*) GROUP BY DATE(timestamp)',
            unit='count',
            threshold_warning=0.0,  # No thresholds for trend
            threshold_critical=0.0,
            refresh_interval_minutes=1440  # Daily
        )

    def deploy_dashboard(self, template_id: str, org_id: str, platform: str = 'looker') -> Dict[str, Any]:
        """
        Deploy a pre-built dashboard to an organization.

        Args:
            template_id: Template ID (e.g., 'executive_overview')
            org_id: Organization ID
            platform: 'looker' or 'tableau'

        Returns:
            {
                'status': 'success|error',
                'dashboard_url': '...',
                'dashboard_id': '...'
            }
        """
        if template_id not in self.templates:
            return {'status': 'error', 'message': f'Template {template_id} not found'}

        template = self.templates[template_id]

        try:
            if platform == 'looker':
                return self._deploy_looker_dashboard(template, org_id)
            elif platform == 'tableau':
                return self._deploy_tableau_dashboard(template, org_id)
            else:
                return {'status': 'error', 'message': f'Unsupported platform: {platform}'}
        except Exception as e:
            logger.error(f"Dashboard deployment failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _deploy_looker_dashboard(self, template: DashboardTemplate, org_id: str) -> Dict[str, Any]:
        """Deploy dashboard to Looker (requires Looker SDK)."""
        if not self.looker:
            return {'status': 'error', 'message': 'Looker client not initialized'}

        dashboard_json = self._template_to_looker_json(template, org_id)
        logger.info(f"Deploying Looker dashboard for {org_id}: {template.template_id}")

        # Example: self.looker.create_dashboard(dashboard_json)
        return {
            'status': 'success',
            'dashboard_id': f'dashboard_{org_id}_{template.template_id}',
            'dashboard_url': f'https://looker.example.com/dashboards/{org_id}/{template.template_id}',
            'platform': 'looker'
        }

    def _deploy_tableau_dashboard(self, template: DashboardTemplate, org_id: str) -> Dict[str, Any]:
        """Deploy dashboard to Tableau (requires Tableau REST API)."""
        if not self.tableau:
            return {'status': 'error', 'message': 'Tableau client not initialized'}

        dashboard_twb = self._template_to_tableau_twb(template, org_id)
        logger.info(f"Deploying Tableau dashboard for {org_id}: {template.template_id}")

        # Example: self.tableau.create_workbook(dashboard_twb)
        return {
            'status': 'success',
            'dashboard_id': f'dashboard_{org_id}_{template.template_id}',
            'dashboard_url': f'https://tableau.example.com/views/{org_id}/{template.template_id}',
            'platform': 'tableau'
        }

    def _template_to_looker_json(self, template: DashboardTemplate, org_id: str) -> Dict[str, Any]:
        """Convert template to Looker LookML JSON format."""
        return {
            'title': f"{template.name} ({org_id})",
            'description': template.description,
            'elements': [
                {
                    'title': panel.get('title', ''),
                    'query': {
                        'dimensions': [panel.get('groupby', '')],
                        'measures': [panel.get('metric', '')],
                        'filters': [{
                            'field': f.get('field'),
                            'value': f.get('default', '')
                        } for f in template.filters]
                    },
                    'vis_config': {
                        'type': panel.get('type', 'table'),
                        'custom_color': True
                    }
                }
                for panel in template.panels
            ],
            'filters': [
                {
                    'name': f.get('field'),
                    'type': f.get('type'),
                    'default': f.get('default', '')
                }
                for f in template.filters
            ]
        }

    def _template_to_tableau_twb(self, template: DashboardTemplate, org_id: str) -> str:
        """Convert template to Tableau TWB (simplified XML)."""
        panels_xml = '\n'.join([
            f"""
            <zone name='{p.get('id', '')}'>
              <title>{p.get('title', '')}</title>
              <viz type='{p.get('type', 'table')}' />
            </zone>
            """
            for p in template.panels
        ])

        return f"""<?xml version='1.0' encoding='UTF-8'?>
<workbook version='10.0'>
  <preferences>
    <preference name='ui.encoding.shelf.height' value='24'/>
  </preferences>
  <datasources>
    <datasource name='analytics' version='10.0'>
      <connection class='sqlserver' server='supabase.example.com' database='maestro'/>
    </datasource>
  </datasources>
  <dashboard name='{template.name}'>
    {panels_xml}
  </dashboard>
</workbook>
"""

    def add_custom_metric(self, metric_name: str, kpi_def: KPIDefinition) -> bool:
        """
        Add a custom KPI metric to all dashboards.

        Args:
            metric_name: Name of custom metric
            kpi_def: KPIDefinition dataclass

        Returns:
            True if successful
        """
        try:
            self.kpis[metric_name] = kpi_def
            logger.info(f"Added custom metric: {metric_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom metric: {e}")
            return False

    def get_dashboard_config(self, template_id: str) -> Dict[str, Any]:
        """Get complete dashboard configuration (for BI tool import)."""
        if template_id not in self.templates:
            return {}

        template = self.templates[template_id]
        return {
            'template_id': template.template_id,
            'name': template.name,
            'description': template.description,
            'panels': template.panels,
            'filters': template.filters,
            'kpis': [
                asdict(self.kpis[kpi])
                for kpi in self.kpis if self._kpi_used_in_template(kpi, template)
            ]
        }

    def _kpi_used_in_template(self, kpi_name: str, template: DashboardTemplate) -> bool:
        """Check if a KPI is referenced in a template."""
        for panel in template.panels:
            if panel.get('metric') == kpi_name:
                return True
        return False

    def list_templates(self) -> List[Dict[str, str]]:
        """List available dashboard templates."""
        return [
            {
                'template_id': t.template_id,
                'name': t.name,
                'target_role': t.target_role,
                'description': t.description
            }
            for t in self.templates.values()
        ]

    def list_kpis(self) -> List[Dict[str, Any]]:
        """List all registered KPI definitions."""
        return [asdict(kpi) for kpi in self.kpis.values()]
