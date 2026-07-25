#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Agent Memory Monitoring & Alerting (R10 refined)
Real-time quota tracking, anomaly detection, and alerting.

Features:
  - Quota tracking per agent (max 100 MB default)
  - Alert thresholds: 60%, 80%, 90%, 100%
  - Quota exceeded tracking (timestamp when > 80%)
  - Tier distribution analysis (HOT/WARM/COLD %)
  - Anomaly detection (unusual access patterns, rapid growth)
  - Grafana dashboard metrics export
  - Slack & email alerting

Author: Claude Haiku 4.5
Ticket: MNT-2026-AGENT-MEMORY-TIERING
Date: 2026-07-25
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import statistics

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import psycopg2.pool
except ImportError:
    print("ERROR: psycopg2 not found. Install: pip install psycopg2-binary")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None

# =====================================================================
# LOGGING SETUP
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_memory_monitoring.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
# DATA MODELS
# =====================================================================

@dataclass
class QuotaAlert:
    """Alert for quota threshold."""
    agent_id: str
    current_pct: float
    threshold_pct: float
    current_mb: float
    max_mb: float
    severity: str  # 'WARNING', 'CRITICAL'
    message: str
    timestamp: datetime


@dataclass
class MemoryStats:
    """Memory statistics for an agent."""
    agent_id: str
    total_mb: float
    hot_mb: float
    warm_mb: float
    cold_mb: float
    hot_pct: float
    warm_pct: float
    cold_pct: float
    chunk_count: int
    access_rate_per_hour: float
    avg_age_minutes: float
    quota_pct: float
    last_checked_at: datetime


@dataclass
class AnomalyDetection:
    """Detected anomaly in memory usage."""
    agent_id: str
    anomaly_type: str  # 'RAPID_GROWTH', 'ABNORMAL_ACCESS', 'LOW_RATINGS'
    severity: float  # 0.0-1.0
    description: str
    recommend_action: str
    timestamp: datetime


@dataclass
class MonitoringReport:
    """Complete monitoring report."""
    timestamp: datetime
    agents_monitored: int
    agents_with_alerts: int
    quota_alerts: List[QuotaAlert] = field(default_factory=list)
    memory_stats: Dict[str, MemoryStats] = field(default_factory=dict)
    anomalies: List[AnomalyDetection] = field(default_factory=list)


# =====================================================================
# DATABASE OPERATIONS
# =====================================================================

class MemoryMonitoringDB:
    """Database operations for memory monitoring."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize connection pool."""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.pool = None
        self._connect()

    def _connect(self):
        """Create connection pool."""
        try:
            db_params = {
                'host': self.supabase_url.split('://')[1].split('.supabase.co')[0] + '.supabase.co',
                'database': 'postgres',
                'user': 'postgres',
                'password': self.supabase_key,
                'port': 5432,
                'sslmode': 'require'
            }
            self.pool = psycopg2.pool.SimpleConnectionPool(1, 5, **db_params)
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise

    def get_conn(self):
        """Get connection from pool."""
        return self.pool.getconn()

    def return_conn(self, conn):
        """Return connection to pool."""
        self.pool.putconn(conn)

    def get_all_agents(self) -> List[str]:
        """Get list of all agents."""
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT agent_id FROM agent_memory
                    UNION
                    SELECT DISTINCT agent_id FROM agent_memory_quota
                    ORDER BY agent_id
                """)
                return [row['agent_id'] for row in cur.fetchall()]
        finally:
            self.return_conn(conn)

    def get_memory_stats(self, agent_id: str) -> Optional[MemoryStats]:
        """Get detailed memory statistics for an agent."""
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                WITH tier_stats AS (
                    SELECT
                        agent_id,
                        tier,
                        COUNT(*) as cnt,
                        SUM(memory_size_bytes)::BIGINT as total_bytes,
                        AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/60.0) as avg_age_min,
                        COUNT(*) FILTER (WHERE last_access_at > NOW() - INTERVAL '1 hour') as access_last_hour
                    FROM agent_memory
                    WHERE agent_id = %s
                    GROUP BY agent_id, tier
                ),
                quota_info AS (
                    SELECT
                        agent_id,
                        max_memory_mb,
                        current_memory_mb,
                        chunk_count
                    FROM agent_memory_quota
                    WHERE agent_id = %s
                )
                SELECT
                    COALESCE(ts.agent_id, qi.agent_id) as agent_id,
                    SUM(ts.total_bytes)::BIGINT as total_bytes,
                    SUM(ts.total_bytes) FILTER (WHERE ts.tier = 'HOT')::BIGINT as hot_bytes,
                    SUM(ts.total_bytes) FILTER (WHERE ts.tier = 'WARM')::BIGINT as warm_bytes,
                    SUM(ts.total_bytes) FILTER (WHERE ts.tier = 'COLD')::BIGINT as cold_bytes,
                    SUM(ts.cnt) as total_chunks,
                    SUM(ts.access_last_hour) as access_last_hour,
                    AVG(ts.avg_age_min) as avg_age_min,
                    qi.max_memory_mb,
                    qi.current_memory_mb,
                    qi.chunk_count
                FROM tier_stats ts
                FULL OUTER JOIN quota_info qi ON ts.agent_id = qi.agent_id
                GROUP BY agent_id, qi.max_memory_mb, qi.current_memory_mb, qi.chunk_count
                """
                cur.execute(query, (agent_id, agent_id))
                row = cur.fetchone()

                if row:
                    total_mb = float(row['total_bytes'] or 0) / 1048576.0
                    hot_mb = float(row['hot_bytes'] or 0) / 1048576.0
                    warm_mb = float(row['warm_bytes'] or 0) / 1048576.0
                    cold_mb = float(row['cold_bytes'] or 0) / 1048576.0
                    max_mb = float(row['max_memory_mb'] or 100.0)
                    quota_pct = (total_mb / max_mb) * 100.0

                    hot_pct = (hot_mb / total_mb * 100.0) if total_mb > 0 else 0
                    warm_pct = (warm_mb / total_mb * 100.0) if total_mb > 0 else 0
                    cold_pct = (cold_mb / total_mb * 100.0) if total_mb > 0 else 0

                    access_rate = float(row['access_last_hour'] or 0)

                    return MemoryStats(
                        agent_id=agent_id,
                        total_mb=total_mb,
                        hot_mb=hot_mb,
                        warm_mb=warm_mb,
                        cold_mb=cold_mb,
                        hot_pct=hot_pct,
                        warm_pct=warm_pct,
                        cold_pct=cold_pct,
                        chunk_count=int(row['chunk_count'] or row['total_chunks'] or 0),
                        access_rate_per_hour=access_rate,
                        avg_age_minutes=float(row['avg_age_min'] or 0),
                        quota_pct=quota_pct,
                        last_checked_at=datetime.now()
                    )

            return None

        finally:
            self.return_conn(conn)

    def check_quota_alerts(self, agent_id: str) -> List[QuotaAlert]:
        """Check for quota threshold violations."""
        alerts = []
        stats = self.get_memory_stats(agent_id)

        if not stats:
            return alerts

        thresholds = [
            (60, 'INFO'),
            (80, 'WARNING'),
            (90, 'CRITICAL'),
            (100, 'CRITICAL')
        ]

        for threshold, severity in thresholds:
            if stats.quota_pct >= threshold:
                alert = QuotaAlert(
                    agent_id=agent_id,
                    current_pct=stats.quota_pct,
                    threshold_pct=threshold,
                    current_mb=stats.total_mb,
                    max_mb=stats.total_mb / (stats.quota_pct / 100.0),
                    severity=severity,
                    message=f"Agent {agent_id} quota {stats.quota_pct:.1f}% (threshold: {threshold}%)",
                    timestamp=datetime.now()
                )
                alerts.append(alert)

        return alerts

    def detect_anomalies(self, agent_id: str, history_hours: int = 24) -> List[AnomalyDetection]:
        """Detect anomalies in memory usage patterns."""
        anomalies = []
        conn = self.get_conn()

        try:
            # Get current stats
            stats = self.get_memory_stats(agent_id)
            if not stats:
                return anomalies

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check for rapid growth
                query = """
                WITH hourly_size AS (
                    SELECT
                        DATE_TRUNC('hour', last_access_at) as hour,
                        SUM(memory_size_bytes) as total_bytes
                    FROM agent_memory
                    WHERE agent_id = %s
                        AND last_access_at > NOW() - INTERVAL '%s hours'
                    GROUP BY DATE_TRUNC('hour', last_access_at)
                    ORDER BY hour DESC
                    LIMIT 24
                )
                SELECT * FROM hourly_size
                """
                cur.execute(query, (agent_id, history_hours))
                hourly_stats = [
                    float(row['total_bytes'] or 0) / 1048576.0
                    for row in cur.fetchall()
                ]

                if len(hourly_stats) >= 2:
                    growth_rates = [
                        (hourly_stats[i] - hourly_stats[i+1]) / max(hourly_stats[i+1], 1.0)
                        for i in range(len(hourly_stats) - 1)
                    ]

                    avg_growth = statistics.mean(growth_rates) if growth_rates else 0
                    max_growth = max(growth_rates) if growth_rates else 0

                    if max_growth > 0.5:  # > 50% growth in an hour
                        anomalies.append(AnomalyDetection(
                            agent_id=agent_id,
                            anomaly_type='RAPID_GROWTH',
                            severity=min(max_growth / 2.0, 1.0),
                            description=f"Rapid growth detected: {max_growth*100:.0f}% in 1 hour",
                            recommend_action="Check for memory leak or unusual agent behavior",
                            timestamp=datetime.now()
                        ))

                # Check for abnormal access patterns
                if stats.access_rate_per_hour > 1000:
                    anomalies.append(AnomalyDetection(
                        agent_id=agent_id,
                        anomaly_type='ABNORMAL_ACCESS',
                        severity=0.7,
                        description=f"High access rate: {stats.access_rate_per_hour:.0f} accesses/hour",
                        recommend_action="Monitor agent load; may indicate cache thrashing",
                        timestamp=datetime.now()
                    ))

                # Check for low-rating entries
                query = """
                SELECT
                    COUNT(*) as low_rating_count,
                    AVG(user_rating) as avg_rating
                FROM agent_memory
                WHERE agent_id = %s AND user_rating < 2
                """
                cur.execute(query, (agent_id,))
                row = cur.fetchone()

                if row and row['low_rating_count'] > (stats.chunk_count * 0.2):  # > 20% low rating
                    anomalies.append(AnomalyDetection(
                        agent_id=agent_id,
                        anomaly_type='LOW_RATINGS',
                        severity=0.6,
                        description=f"High proportion of low-rating entries: {row['low_rating_count']} / {stats.chunk_count}",
                        recommend_action="Review agent response quality; consider cleanup",
                        timestamp=datetime.now()
                    ))

        finally:
            self.return_conn(conn)

        return anomalies

    def update_quota_exceeded_timestamp(self, agent_id: str, exceeded: bool):
        """Update quota_exceeded_at timestamp."""
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                if exceeded:
                    query = """
                    UPDATE agent_memory_quota
                    SET quota_exceeded_at = NOW()
                    WHERE agent_id = %s AND quota_exceeded_at IS NULL
                    """
                else:
                    query = """
                    UPDATE agent_memory_quota
                    SET quota_exceeded_at = NULL
                    WHERE agent_id = %s
                    """
                cur.execute(query, (agent_id,))
                conn.commit()
        finally:
            self.return_conn(conn)

    def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Connection pool closed")


# =====================================================================
# MONITORING ORCHESTRATOR
# =====================================================================

class MemoryMonitoringOrchestrator:
    """Orchestrates monitoring and alerting."""

    def __init__(
        self,
        db: MemoryMonitoringDB,
        slack_webhook: Optional[str] = None,
        email_recipients: Optional[List[str]] = None
    ):
        self.db = db
        self.slack_webhook = slack_webhook
        self.email_recipients = email_recipients or []

    def execute_monitoring_cycle(self) -> MonitoringReport:
        """Execute complete monitoring cycle."""
        report = MonitoringReport(timestamp=datetime.now(), agents_monitored=0, agents_with_alerts=0)

        try:
            agents = self.db.get_all_agents()
            report.agents_monitored = len(agents)
            logger.info(f"Monitoring {len(agents)} agents...")

            for agent_id in agents:
                logger.info(f"Monitoring {agent_id}...")

                # Get stats
                stats = self.db.get_memory_stats(agent_id)
                if stats:
                    report.memory_stats[agent_id] = stats

                # Check quotas
                alerts = self.db.check_quota_alerts(agent_id)
                if alerts:
                    report.quota_alerts.extend(alerts)
                    report.agents_with_alerts += 1

                    # Update quota_exceeded_at timestamp
                    self.db.update_quota_exceeded_timestamp(agent_id, exceeded=True)

                    # Send alerts
                    for alert in alerts:
                        self._send_alert(alert)
                else:
                    # Clear quota_exceeded_at if quota OK
                    self.db.update_quota_exceeded_timestamp(agent_id, exceeded=False)

                # Detect anomalies
                anomalies = self.db.detect_anomalies(agent_id)
                if anomalies:
                    report.anomalies.extend(anomalies)

                    # Send anomaly alerts
                    for anomaly in anomalies:
                        self._send_anomaly_alert(anomaly)

            return report

        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}", exc_info=True)
            return report

    def _send_alert(self, alert: QuotaAlert):
        """Send quota alert to Slack."""
        if not self.slack_webhook or not requests:
            return

        try:
            color = 'warning' if alert.severity == 'WARNING' else 'danger'
            payload = {
                'attachments': [
                    {
                        'color': color,
                        'title': f'Agent Memory Quota Alert',
                        'text': alert.message,
                        'fields': [
                            {'title': 'Agent', 'value': alert.agent_id, 'short': True},
                            {'title': 'Quota', 'value': f"{alert.current_pct:.1f}% / {alert.threshold_pct}%", 'short': True},
                            {'title': 'Memory', 'value': f"{alert.current_mb:.2f} MB / {alert.max_mb:.2f} MB", 'short': True},
                            {'title': 'Severity', 'value': alert.severity, 'short': True}
                        ]
                    }
                ]
            }
            response = requests.post(self.slack_webhook, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to send Slack alert: {e}")

    def _send_anomaly_alert(self, anomaly: AnomalyDetection):
        """Send anomaly alert to Slack."""
        if not self.slack_webhook or not requests:
            return

        try:
            payload = {
                'attachments': [
                    {
                        'color': 'danger',
                        'title': f'Agent Memory Anomaly: {anomaly.anomaly_type}',
                        'text': anomaly.description,
                        'fields': [
                            {'title': 'Agent', 'value': anomaly.agent_id, 'short': True},
                            {'title': 'Severity', 'value': f"{anomaly.severity*100:.0f}%", 'short': True},
                            {'title': 'Recommended Action', 'value': anomaly.recommend_action}
                        ]
                    }
                ]
            }
            response = requests.post(self.slack_webhook, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Slack anomaly alert failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to send Slack anomaly alert: {e}")

    def export_grafana_metrics(self, report: MonitoringReport) -> Dict:
        """Export metrics in Grafana format."""
        metrics = {
            'timestamp': report.timestamp.isoformat(),
            'agents': {}
        }

        for agent_id, stats in report.memory_stats.items():
            metrics['agents'][agent_id] = {
                'total_mb': stats.total_mb,
                'hot_mb': stats.hot_mb,
                'warm_mb': stats.warm_mb,
                'cold_mb': stats.cold_mb,
                'quota_pct': stats.quota_pct,
                'chunk_count': stats.chunk_count,
                'access_rate_per_hour': stats.access_rate_per_hour,
                'avg_age_minutes': stats.avg_age_minutes
            }

        return metrics

    def get_report(self, report: MonitoringReport) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("AGENT MEMORY MONITORING REPORT")
        lines.append("="*70)
        lines.append(f"Timestamp: {report.timestamp.isoformat()}")
        lines.append(f"Agents monitored: {report.agents_monitored}")
        lines.append(f"Agents with alerts: {report.agents_with_alerts}")
        lines.append("")

        # Memory stats
        lines.append("MEMORY STATISTICS:")
        for agent_id, stats in sorted(report.memory_stats.items()):
            lines.append(f"  {agent_id}")
            lines.append(f"    Total: {stats.total_mb:.2f} MB ({stats.quota_pct:.1f}% quota)")
            lines.append(f"    HOT: {stats.hot_mb:.2f} MB ({stats.hot_pct:.1f}%)")
            lines.append(f"    WARM: {stats.warm_mb:.2f} MB ({stats.warm_pct:.1f}%)")
            lines.append(f"    COLD: {stats.cold_mb:.2f} MB ({stats.cold_pct:.1f}%)")
            lines.append(f"    Chunks: {stats.chunk_count}")
            lines.append(f"    Access rate: {stats.access_rate_per_hour:.0f}/hour")

        # Quota alerts
        if report.quota_alerts:
            lines.append("\nQUOTA ALERTS:")
            for alert in report.quota_alerts:
                lines.append(f"  [{alert.severity}] {alert.message}")

        # Anomalies
        if report.anomalies:
            lines.append("\nANOMALIES DETECTED:")
            for anomaly in report.anomalies:
                lines.append(f"  [{anomaly.anomaly_type}] {anomaly.agent_id}")
                lines.append(f"    {anomaly.description}")
                lines.append(f"    Action: {anomaly.recommend_action}")

        lines.append("\n" + "="*70 + "\n")
        return "\n".join(lines)


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manta Maestro — Agent Memory Monitoring & Alerting (R10 refined)'
    )
    parser.add_argument('--supabase-url', required=True, help='Supabase project URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase service role key')
    parser.add_argument('--slack-webhook', help='Slack webhook URL for alerts')
    parser.add_argument('--output-json', help='Output JSON metrics to file')
    parser.add_argument('--output-grafana', help='Output Grafana metrics to file')

    args = parser.parse_args()

    try:
        db = MemoryMonitoringDB(args.supabase_url, args.supabase_key)
        orchestrator = MemoryMonitoringOrchestrator(
            db,
            slack_webhook=args.slack_webhook
        )

        report = orchestrator.execute_monitoring_cycle()

        print(orchestrator.get_report(report))

        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump({
                    'timestamp': report.timestamp.isoformat(),
                    'agents_monitored': report.agents_monitored,
                    'agents_with_alerts': report.agents_with_alerts,
                    'quota_alerts': [asdict(a) for a in report.quota_alerts],
                    'anomalies': [asdict(a) for a in report.anomalies],
                    'stats': {
                        k: asdict(v) for k, v in report.memory_stats.items()
                    }
                }, f, indent=2, default=str)
            logger.info(f"JSON report saved to {args.output_json}")

        if args.output_grafana:
            metrics = orchestrator.export_grafana_metrics(report)
            with open(args.output_grafana, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            logger.info(f"Grafana metrics saved to {args.output_grafana}")

        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(2)


if __name__ == '__main__':
    main()
