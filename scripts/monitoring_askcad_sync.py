#!/usr/bin/env python3
"""
Monitoring and alerting for AskCAD sync operations.

Phase 3.4 - AskCAD Persona Sync
Part 4: Monitoring & Alerting

Track sync success rate, detect failures, identify version mismatches,
and maintain audit trail. Integrates with standard monitoring systems.

Usage:
    monitor = SyncMonitor()
    monitor.start_monitoring()
    monitor.check_health()
    monitor.generate_report()
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SyncEvent:
    """Record of a sync operation"""
    timestamp: str
    agent_code: str
    operation: str  # sync, verify, rollback
    status: str     # success, failed, warning
    version: str
    content_hash: str
    message: str
    duration_ms: int
    changes_count: int = 0
    error_details: Optional[str] = None
    audit_id: str = field(default_factory=lambda: "")

    def __post_init__(self):
        if not self.audit_id:
            content = f"{self.timestamp}{self.agent_code}{self.status}"
            self.audit_id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class HealthMetrics:
    """Health metrics for sync operations"""
    total_syncs: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    total_agents: int = 0
    active_agents: int = 0
    avg_sync_time_ms: float = 0.0
    success_rate: float = 0.0
    version_mismatches: int = 0
    last_check: str = ""
    alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Alert:
    """Alert notification"""
    timestamp: str
    severity: AlertSeverity
    agent_code: Optional[str]
    title: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    action_required: bool = False


class SyncMonitor:
    """Monitor AskCAD sync operations"""

    def __init__(
        self,
        db_path: str = '.askcad/sync_monitor.db',
        audit_log_path: str = '.askcad/audit_trail.jsonl',
        version_history_path: str = '.askcad/version_history.json'
    ):
        """
        Initialize sync monitor.

        Args:
            db_path: SQLite database for metrics
            audit_log_path: JSONL file for audit trail
            version_history_path: Version history file
        """
        self.db_path = Path(db_path)
        self.audit_log_path = Path(audit_log_path)
        self.version_history_path = Path(version_history_path)
        self.alerts: List[Alert] = []
        self.events: List[SyncEvent] = []

        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"Initialized SyncMonitor (DB: {self.db_path})")

    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                audit_id TEXT UNIQUE NOT NULL,
                agent_code TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                version TEXT,
                content_hash TEXT,
                message TEXT,
                duration_ms INTEGER,
                changes_count INTEGER DEFAULT 0,
                error_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_agent (agent_code),
                INDEX idx_timestamp (timestamp),
                INDEX idx_status (status)
            )
        """)

        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                agent_code TEXT,
                title TEXT NOT NULL,
                description TEXT,
                action_required BOOLEAN DEFAULT 0,
                resolved BOOLEAN DEFAULT 0,
                resolved_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_severity (severity),
                INDEX idx_agent (agent_code),
                INDEX idx_resolved (resolved)
            )
        """)

        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_syncs INTEGER,
                successful_syncs INTEGER,
                failed_syncs INTEGER,
                total_agents INTEGER,
                active_agents INTEGER,
                avg_sync_time_ms REAL,
                success_rate REAL,
                version_mismatches INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_timestamp (timestamp)
            )
        """)

        conn.commit()
        conn.close()

    def record_sync(self, event: SyncEvent) -> str:
        """Record a sync event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sync_events
                (timestamp, audit_id, agent_code, operation, status, version,
                 content_hash, message, duration_ms, changes_count, error_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.timestamp, event.audit_id, event.agent_code,
                event.operation, event.status, event.version,
                event.content_hash, event.message, event.duration_ms,
                event.changes_count, event.error_details
            ))

            conn.commit()
            self.events.append(event)

            # Write to audit trail
            self._write_audit_trail(event)

            logger.info(
                f"Recorded sync event: {event.agent_code} "
                f"({event.operation} - {event.status})"
            )

            return event.audit_id

        except Exception as e:
            logger.error(f"Failed to record sync event: {e}")
            raise
        finally:
            conn.close()

    def _write_audit_trail(self, event: SyncEvent) -> None:
        """Write event to audit trail (JSONL format)"""
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(asdict(event), default=str) + '\n')

    def check_health(self, time_window_hours: int = 24) -> Tuple[HealthMetrics, List[Alert]]:
        """
        Check overall health of sync operations.

        Args:
            time_window_hours: Time window for metrics (default 24 hours)

        Returns:
            Tuple of (HealthMetrics, list of Alert objects)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = (datetime.now() - timedelta(hours=time_window_hours)).isoformat()

        # Get sync metrics
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(duration_ms) as avg_duration
            FROM sync_events
            WHERE timestamp >= ?
        """, (cutoff_time,))

        total, successful, failed, avg_duration = cursor.fetchone()
        total = total or 0
        successful = successful or 0
        failed = failed or 0
        avg_duration = avg_duration or 0

        # Get unique agents
        cursor.execute("""
            SELECT COUNT(DISTINCT agent_code)
            FROM sync_events
            WHERE timestamp >= ?
        """, (cutoff_time,))

        total_agents = cursor.fetchone()[0] or 0

        # Get version mismatches
        cursor.execute("""
            SELECT COUNT(DISTINCT agent_code)
            FROM sync_events
            WHERE status = 'warning'
                AND timestamp >= ?
        """, (cutoff_time,))

        version_mismatches = cursor.fetchone()[0] or 0

        conn.close()

        # Calculate metrics
        success_rate = (successful / total * 100) if total > 0 else 0
        active_agents = total_agents

        metrics = HealthMetrics(
            total_syncs=total,
            successful_syncs=successful,
            failed_syncs=failed,
            total_agents=total_agents,
            active_agents=active_agents,
            avg_sync_time_ms=avg_duration,
            success_rate=success_rate,
            version_mismatches=version_mismatches,
            last_check=datetime.now().isoformat()
        )

        # Generate alerts based on metrics
        alerts = self._generate_health_alerts(metrics)
        self.alerts.extend(alerts)

        return metrics, alerts

    def _generate_health_alerts(self, metrics: HealthMetrics) -> List[Alert]:
        """Generate alerts based on health metrics"""
        alerts = []

        # Check success rate
        if metrics.total_syncs > 0 and metrics.success_rate < 95:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity=AlertSeverity.WARNING,
                agent_code=None,
                title="Low sync success rate",
                description=f"Success rate is {metrics.success_rate:.1f}% "
                           f"({metrics.successful_syncs}/{metrics.total_syncs})",
                metrics=asdict(metrics),
                action_required=True
            ))

        # Check for failures
        if metrics.failed_syncs > 0:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity=AlertSeverity.ERROR,
                agent_code=None,
                title="Sync failures detected",
                description=f"{metrics.failed_syncs} failed syncs in the last 24 hours",
                metrics=asdict(metrics),
                action_required=True
            ))

        # Check for version mismatches
        if metrics.version_mismatches > 0:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity=AlertSeverity.WARNING,
                agent_code=None,
                title="Version mismatches detected",
                description=f"{metrics.version_mismatches} agents with version mismatches",
                metrics=asdict(metrics),
                action_required=False
            ))

        # Check sync time
        if metrics.avg_sync_time_ms > 5000:  # 5 seconds
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity=AlertSeverity.WARNING,
                agent_code=None,
                title="High average sync time",
                description=f"Average sync time is {metrics.avg_sync_time_ms:.0f}ms",
                metrics=asdict(metrics),
                action_required=False
            ))

        return alerts

    def detect_version_mismatches(self) -> List[Tuple[str, str, str]]:
        """
        Detect version mismatches between local and AskCAD.

        Returns:
            List of (agent_code, local_version, askcad_version) tuples
        """
        if not self.version_history_path.exists():
            return []

        mismatches = []
        history = json.loads(self.version_history_path.read_text())

        for agent_code, versions in history.items():
            if not versions:
                continue

            latest_version = versions[-1]
            # In real implementation, would check against AskCAD API
            # For now, just flag if multiple recent versions exist
            if len(versions) > 1:
                prev_version = versions[-2]
                if latest_version['version'] != prev_version['version']:
                    mismatches.append((
                        agent_code,
                        prev_version['version'],
                        latest_version['version']
                    ))

        return mismatches

    def get_sync_history(
        self,
        agent_code: Optional[str] = None,
        operation: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get sync history with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM sync_events WHERE 1=1"
        params = []

        if agent_code:
            query += " AND agent_code = ?"
            params.append(agent_code)

        if operation:
            query += " AND operation = ?"
            params.append(operation)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def record_alert(self, alert: Alert) -> None:
        """Record an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sync_alerts
                (timestamp, severity, agent_code, title, description, action_required)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp, alert.severity.value, alert.agent_code,
                alert.title, alert.description, alert.action_required
            ))
            conn.commit()
            logger.info(f"Recorded alert: {alert.title} ({alert.severity.value})")
        finally:
            conn.close()

    def resolve_alert(self, alert_id: int) -> None:
        """Resolve an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE sync_alerts
                SET resolved = 1, resolved_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), alert_id))
            conn.commit()
        finally:
            conn.close()

    def save_metrics_snapshot(self) -> None:
        """Save current metrics snapshot to database"""
        metrics, _ = self.check_health()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO health_metrics
                (timestamp, total_syncs, successful_syncs, failed_syncs,
                 total_agents, active_agents, avg_sync_time_ms, success_rate,
                 version_mismatches)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metrics.total_syncs,
                metrics.successful_syncs,
                metrics.failed_syncs,
                metrics.total_agents,
                metrics.active_agents,
                metrics.avg_sync_time_ms,
                metrics.success_rate,
                metrics.version_mismatches
            ))
            conn.commit()
        finally:
            conn.close()

    def generate_report(self, hours: int = 24) -> str:
        """Generate monitoring report"""
        metrics, alerts = self.check_health(time_window_hours=hours)
        mismatches = self.detect_version_mismatches()

        lines = [
            "=" * 70,
            f"ASKCAD SYNC MONITORING REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            "HEALTH METRICS (last 24 hours)",
            "-" * 70,
            f"Total Syncs:           {metrics.total_syncs}",
            f"Successful:            {metrics.successful_syncs}",
            f"Failed:                {metrics.failed_syncs}",
            f"Success Rate:          {metrics.success_rate:.1f}%",
            f"Active Agents:         {metrics.active_agents}/{metrics.total_agents}",
            f"Avg Sync Time:         {metrics.avg_sync_time_ms:.0f}ms",
            f"Version Mismatches:    {metrics.version_mismatches}",
            "",
        ]

        if alerts:
            lines.extend([
                "ALERTS",
                "-" * 70,
            ])
            for alert in alerts:
                severity_icon = {
                    AlertSeverity.INFO: "ℹ",
                    AlertSeverity.WARNING: "⚠",
                    AlertSeverity.ERROR: "✗",
                    AlertSeverity.CRITICAL: "🔴"
                }.get(alert.severity, "?")

                lines.append(
                    f"{severity_icon} [{alert.severity.value.upper()}] "
                    f"{alert.title}"
                )
                lines.append(f"   {alert.description}")

            lines.append("")

        if mismatches:
            lines.extend([
                "VERSION MISMATCHES",
                "-" * 70,
            ])
            for agent, local_ver, askcad_ver in mismatches:
                lines.append(
                    f"  {agent:25} Local: {local_ver:10} AskCAD: {askcad_ver:10}"
                )
            lines.append("")

        # Recent events
        history = self.get_sync_history(limit=10)
        if history:
            lines.extend([
                "RECENT SYNC EVENTS (last 10)",
                "-" * 70,
            ])
            for event in history:
                status_icon = "✓" if event['status'] == 'success' else "✗"
                lines.append(
                    f"{status_icon} {event['timestamp'][:19]} | "
                    f"{event['agent_code']:20} | {event['operation']:10} | "
                    f"{event['status']:10} | {event['duration_ms']:5}ms"
                )
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def export_metrics(self, output_file: str) -> None:
        """Export metrics to JSON file"""
        metrics, alerts = self.check_health()

        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(metrics),
            'alerts': [asdict(a) for a in alerts],
            'recent_events': self.get_sync_history(limit=50)
        }

        Path(output_file).write_text(json.dumps(data, indent=2, default=str))
        logger.info(f"Metrics exported to {output_file}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor AskCAD sync operations'
    )
    parser.add_argument(
        'command',
        choices=['health', 'history', 'mismatches', 'report', 'export'],
        help='Monitoring command'
    )
    parser.add_argument(
        '--agent-code',
        help='Filter by agent code'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Time window in hours'
    )
    parser.add_argument(
        '--output',
        help='Output file for export'
    )
    parser.add_argument(
        '--db-path',
        default='.askcad/sync_monitor.db',
        help='Database path'
    )

    args = parser.parse_args()

    monitor = SyncMonitor(db_path=args.db_path)

    if args.command == 'health':
        metrics, alerts = monitor.check_health(time_window_hours=args.hours)
        print(json.dumps(asdict(metrics), indent=2, default=str))

    elif args.command == 'history':
        history = monitor.get_sync_history(
            agent_code=args.agent_code,
            limit=50
        )
        print(json.dumps(history, indent=2))

    elif args.command == 'mismatches':
        mismatches = monitor.detect_version_mismatches()
        for agent, local, askcad in mismatches:
            print(f"{agent:25} {local:10} → {askcad:10}")

    elif args.command == 'report':
        print(monitor.generate_report(hours=args.hours))

    elif args.command == 'export':
        if not args.output:
            print("Error: --output required for export")
            import sys
            sys.exit(1)
        monitor.export_metrics(args.output)


if __name__ == '__main__':
    import sys
    main()
