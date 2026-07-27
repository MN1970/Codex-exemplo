"""
Phase 4.2 Advanced Analytics — Monitoring & Alerting

Real-time health checks, performance degradation detection,
automated incident escalation, and SLA monitoring.

Integrates with:
  - CloudWatch / Datadog (metrics)
  - PagerDuty (incident escalation)
  - Slack (notifications)
  - Email (critical alerts)

Checks:
  - Dashboard availability
  - Query latency p95
  - Routing accuracy
  - Cost anomalies
  - Webhook processing lag
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    PAGE = "page"  # Page on-call engineer


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    check_name: str
    status: str  # "pass", "warn", "fail"
    message: str
    timestamp: datetime
    metric_value: Optional[float]
    threshold: Optional[float]
    details: Dict[str, Any]


@dataclass
class Alert:
    """Alert event."""
    alert_id: str
    severity: str  # AlertSeverity
    title: str
    message: str
    check_name: str
    timestamp: datetime
    metric_value: Optional[float]
    context: Dict[str, Any]
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class HealthChecker:
    """
    Orchestrates health checks for all components.

    Runs on 5-minute interval, stores results for alerting.
    """

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results_history: List[HealthCheckResult] = []
        self.register_default_checks()

    def register_check(self, check_name: str, check_func: Callable) -> None:
        """
        Register a custom health check.

        Args:
            check_name: Name of check (e.g., "dashboard_availability")
            check_func: Function(Dict) -> HealthCheckResult
        """
        self.checks[check_name] = check_func
        logger.info(f"Registered health check: {check_name}")

    def register_default_checks(self):
        """Register built-in health checks."""
        self.register_check('dashboard_availability', self._check_dashboard_availability)
        self.register_check('query_latency', self._check_query_latency)
        self.register_check('routing_accuracy', self._check_routing_accuracy)
        self.register_check('cost_anomaly', self._check_cost_anomaly)
        self.register_check('webhook_lag', self._check_webhook_lag)
        self.register_check('database_connection', self._check_database_connection)

    def run_all_checks(self, context: Dict[str, Any]) -> List[HealthCheckResult]:
        """
        Run all registered health checks.

        Args:
            context: Shared context (db connection, metrics client, etc.)

        Returns:
            List of HealthCheckResult objects
        """
        results = []
        for check_name, check_func in self.checks.items():
            try:
                result = check_func(context)
                results.append(result)
                self.results_history.append(result)
            except Exception as e:
                logger.error(f"Health check '{check_name}' failed: {e}")
                results.append(HealthCheckResult(
                    check_name=check_name,
                    status='fail',
                    message=f"Check execution error: {str(e)}",
                    timestamp=datetime.utcnow(),
                    metric_value=None,
                    threshold=None,
                    details={'error': str(e)}
                ))

        return results

    @staticmethod
    def _check_dashboard_availability(context: Dict[str, Any]) -> HealthCheckResult:
        """Check if BI dashboards are reachable."""
        try:
            # Example: ping Looker/Tableau endpoints
            dashboard_endpoints = context.get('dashboard_endpoints', {})
            all_reachable = True
            failed_dashboards = []

            for platform, url in dashboard_endpoints.items():
                # In production: actual HTTP health check
                reachable = context.get(f'{platform}_available', True)
                if not reachable:
                    all_reachable = False
                    failed_dashboards.append(platform)

            status = 'pass' if all_reachable else 'warn'
            message = 'All dashboards available' if all_reachable else f"Dashboards unavailable: {failed_dashboards}"

            return HealthCheckResult(
                check_name='dashboard_availability',
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metric_value=len(dashboard_endpoints),
                threshold=None,
                details={'failed': failed_dashboards}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='dashboard_availability',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )

    @staticmethod
    def _check_query_latency(context: Dict[str, Any]) -> HealthCheckResult:
        """Check query latency p95."""
        try:
            p95_latency_ms = context.get('query_latency_p95_ms', 0)
            threshold_ms = 500  # Phase 3 SLA
            status = 'pass' if p95_latency_ms <= threshold_ms else 'warn'

            return HealthCheckResult(
                check_name='query_latency',
                status=status,
                message=f"p95 latency: {p95_latency_ms}ms (threshold: {threshold_ms}ms)",
                timestamp=datetime.utcnow(),
                metric_value=float(p95_latency_ms),
                threshold=float(threshold_ms),
                details={'p95_ms': p95_latency_ms, 'p99_ms': context.get('query_latency_p99_ms', 0)}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='query_latency',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )

    @staticmethod
    def _check_routing_accuracy(context: Dict[str, Any]) -> HealthCheckResult:
        """Check routing accuracy vs. threshold."""
        try:
            accuracy = context.get('routing_accuracy_pct', 0)
            threshold = 85.0  # Phase 1 gate
            status = 'pass' if accuracy >= threshold else 'warn'

            return HealthCheckResult(
                check_name='routing_accuracy',
                status=status,
                message=f"Routing accuracy: {accuracy:.1f}% (threshold: {threshold}%)",
                timestamp=datetime.utcnow(),
                metric_value=accuracy,
                threshold=threshold,
                details={'accuracy_pct': accuracy}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='routing_accuracy',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )

    @staticmethod
    def _check_cost_anomaly(context: Dict[str, Any]) -> HealthCheckResult:
        """Detect cost anomalies (unusual spike)."""
        try:
            current_cost = context.get('daily_cost_usd', 0)
            avg_cost = context.get('avg_daily_cost_usd', 0)

            if avg_cost == 0:
                return HealthCheckResult(
                    check_name='cost_anomaly',
                    status='pass',
                    message='No baseline for comparison',
                    timestamp=datetime.utcnow(),
                    metric_value=current_cost,
                    threshold=None,
                    details={}
                )

            cost_ratio = current_cost / avg_cost
            threshold_ratio = 1.5  # Alert if >50% above average
            status = 'pass' if cost_ratio < threshold_ratio else 'warn'

            return HealthCheckResult(
                check_name='cost_anomaly',
                status=status,
                message=f"Daily cost ${current_cost:.2f} (avg ${avg_cost:.2f}, ratio {cost_ratio:.2f})",
                timestamp=datetime.utcnow(),
                metric_value=cost_ratio,
                threshold=threshold_ratio,
                details={'current_usd': current_cost, 'avg_usd': avg_cost, 'ratio': cost_ratio}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='cost_anomaly',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )

    @staticmethod
    def _check_webhook_lag(context: Dict[str, Any]) -> HealthCheckResult:
        """Check Phase 3.2 regulatory webhook processing lag."""
        try:
            lag_minutes = context.get('webhook_max_lag_minutes', 0)
            threshold_minutes = 30  # Max acceptable lag
            status = 'pass' if lag_minutes <= threshold_minutes else 'warn'

            return HealthCheckResult(
                check_name='webhook_lag',
                status=status,
                message=f"Webhook processing lag: {lag_minutes}min (threshold: {threshold_minutes}min)",
                timestamp=datetime.utcnow(),
                metric_value=float(lag_minutes),
                threshold=float(threshold_minutes),
                details={'lag_minutes': lag_minutes, 'pending_webhooks': context.get('pending_webhooks', 0)}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='webhook_lag',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )

    @staticmethod
    def _check_database_connection(context: Dict[str, Any]) -> HealthCheckResult:
        """Check database connectivity and response time."""
        try:
            db_available = context.get('database_available', False)
            db_latency_ms = context.get('database_latency_ms', 0)
            threshold_ms = 100

            status = 'fail' if not db_available else ('pass' if db_latency_ms <= threshold_ms else 'warn')
            message = 'Database unreachable' if not db_available else f"Latency: {db_latency_ms}ms"

            return HealthCheckResult(
                check_name='database_connection',
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metric_value=float(db_latency_ms) if db_available else None,
                threshold=float(threshold_ms),
                details={'available': db_available, 'latency_ms': db_latency_ms}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name='database_connection',
                status='fail',
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                metric_value=None,
                threshold=None,
                details={}
            )


class AlertingEngine:
    """
    Generates and manages alerts based on health check results.

    Integrates with notification channels (Slack, email, PagerDuty).
    Handles alert deduplication and escalation.
    """

    def __init__(self):
        self.alerts: List[Alert] = []
        self.notification_handlers: Dict[AlertSeverity, List[Callable]] = {
            AlertSeverity.INFO: [],
            AlertSeverity.WARNING: [],
            AlertSeverity.CRITICAL: [],
            AlertSeverity.PAGE: []
        }
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_cooldown_minutes = 30

    def register_handler(self, severity: AlertSeverity, handler: Callable) -> None:
        """
        Register alert handler for severity level.

        Args:
            severity: AlertSeverity
            handler: Function(Alert) that sends notification
        """
        self.notification_handlers[severity].append(handler)
        logger.info(f"Registered alert handler for {severity}")

    def process_health_checks(self, results: List[HealthCheckResult]) -> List[Alert]:
        """
        Convert health check results to alerts.

        Args:
            results: List of HealthCheckResult

        Returns:
            List of Alert objects
        """
        new_alerts = []

        for result in results:
            if result.status == 'pass':
                continue

            # Determine severity
            if result.status == 'warn':
                severity = AlertSeverity.WARNING
            else:  # fail
                severity = AlertSeverity.CRITICAL

            # Check cooldown (deduplication)
            last_time = self.last_alert_time.get(result.check_name)
            if last_time and (datetime.utcnow() - last_time).seconds < self.alert_cooldown_minutes * 60:
                logger.debug(f"Alert cooldown active for {result.check_name}")
                continue

            # Create alert
            alert = Alert(
                alert_id=f"{result.check_name}_{datetime.utcnow().timestamp()}",
                severity=severity.value,
                title=f"{result.check_name.replace('_', ' ').title()} Alert",
                message=result.message,
                check_name=result.check_name,
                timestamp=datetime.utcnow(),
                metric_value=result.metric_value,
                context=result.details
            )

            new_alerts.append(alert)
            self.alerts.append(alert)
            self.last_alert_time[result.check_name] = datetime.utcnow()

            # Send notifications
            self._send_alert(alert)

        return new_alerts

    def _send_alert(self, alert: Alert) -> None:
        """Send alert via registered handlers."""
        severity = AlertSeverity(alert.severity)
        handlers = self.notification_handlers.get(severity, [])

        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def get_active_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts."""
        return [a for a in self.alerts if not a.acknowledged]

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.utcnow()
                return True
        return False


class IncidentEscalation:
    """
    Manages incident escalation for critical issues.

    Escalates to on-call engineer if issue persists.
    """

    def __init__(self):
        self.escalation_config: Dict[str, Dict[str, Any]] = {
            'routing_accuracy': {
                'escalate_after_minutes': 15,
                'notify_channels': ['slack', 'email'],
                'page_after_minutes': 30
            },
            'database_connection': {
                'escalate_after_minutes': 5,
                'notify_channels': ['slack', 'email', 'pagerduty'],
                'page_after_minutes': 10
            },
            'cost_anomaly': {
                'escalate_after_minutes': 60,
                'notify_channels': ['slack', 'email'],
                'page_after_minutes': 120
            }
        }
        self.open_incidents: Dict[str, Dict[str, Any]] = {}

    def evaluate_escalation(self, alert: Alert) -> Optional[Dict[str, Any]]:
        """
        Determine if alert should escalate to incident.

        Args:
            alert: Alert object

        Returns:
            Escalation action or None
        """
        config = self.escalation_config.get(alert.check_name)
        if not config:
            return None

        incident_key = alert.check_name
        current_time = datetime.utcnow()

        if incident_key not in self.open_incidents:
            self.open_incidents[incident_key] = {
                'first_alert': current_time,
                'last_alert': current_time,
                'escalation_level': 0
            }
            return None

        incident = self.open_incidents[incident_key]
        time_since_first = (current_time - incident['first_alert']).total_seconds() / 60

        action = None

        # Level 1: Escalate to on-call
        if time_since_first >= config['escalate_after_minutes'] and incident['escalation_level'] < 1:
            action = {
                'type': 'escalate',
                'level': 1,
                'channels': config['notify_channels'],
                'severity': 'warning'
            }
            incident['escalation_level'] = 1

        # Level 2: Page on-call
        if time_since_first >= config['page_after_minutes'] and incident['escalation_level'] < 2:
            action = {
                'type': 'page',
                'level': 2,
                'channels': ['pagerduty'],
                'severity': 'critical'
            }
            incident['escalation_level'] = 2

        incident['last_alert'] = current_time
        return action

    def resolve_incident(self, check_name: str) -> bool:
        """Resolve open incident."""
        if check_name in self.open_incidents:
            del self.open_incidents[check_name]
            return True
        return False

    def get_open_incidents(self) -> Dict[str, Dict[str, Any]]:
        """Get currently open incidents."""
        return self.open_incidents.copy()


class NotificationHandlers:
    """Built-in notification handlers for common channels."""

    @staticmethod
    def slack_handler(webhook_url: str) -> Callable:
        """Create Slack notification handler."""
        def handler(alert: Alert) -> None:
            payload = {
                'text': f":warning: {alert.title}",
                'blocks': [
                    {
                        'type': 'header',
                        'text': {'type': 'plain_text', 'text': alert.title}
                    },
                    {
                        'type': 'section',
                        'text': {'type': 'mrkdwn', 'text': alert.message}
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"*Severity:* {alert.severity}\n*Time:* {alert.timestamp.isoformat()}"
                            }
                        ]
                    }
                ]
            }
            # In production: requests.post(webhook_url, json=payload)
            logger.info(f"Slack notification: {alert.title}")
        return handler

    @staticmethod
    def email_handler(smtp_config: Dict[str, str]) -> Callable:
        """Create email notification handler."""
        def handler(alert: Alert) -> None:
            # In production: use smtplib/email
            logger.info(f"Email notification: {alert.title}")
        return handler

    @staticmethod
    def pagerduty_handler(api_key: str) -> Callable:
        """Create PagerDuty page handler."""
        def handler(alert: Alert) -> None:
            # In production: PagerDuty API trigger
            logger.info(f"PagerDuty page triggered: {alert.title}")
        return handler
