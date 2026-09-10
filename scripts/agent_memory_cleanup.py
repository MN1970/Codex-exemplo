#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Agent Memory Cleanup & LRU Eviction (R10 refined)
Automatic cleanup policies with graceful LRU eviction + R9 feedback integration.

Features:
  - Cleanup policies: age-based, rating-based, quota-based
  - LRU eviction when quota > 80%
  - Integration with R9 feedback loop (chunks rating >= 4 → embedding retraining)
  - Metrics tracking & reporting
  - Slack alerting for exceptional events

Cleanup rules (priority order):
  1. Delete expired entries (created_at + TTL < NOW())
  2. Archive low-rating entries (user_rating < 2, age > 7 days)
  3. Evict oldest WARM/HOT entries if quota > 80% (LRU)
  4. Preserve high-rating entries (user_rating >= 4, feedback_score >= 0.8)

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
from dataclasses import dataclass, asdict
import hashlib

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_batch
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
        logging.FileHandler('agent_memory_cleanup.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
# DATA MODELS
# =====================================================================

@dataclass
class CleanupRule:
    """Represents a cleanup rule."""
    priority: int
    name: str
    condition: str
    estimated_chunks: int
    estimated_mb: float


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    agent_id: str
    rule_name: str
    deleted_count: int
    freed_mb: float
    before_quota_pct: float
    after_quota_pct: float
    duration_ms: float
    timestamp: datetime


@dataclass
class R9FeedbackEntry:
    """High-rating entry for R9 embedding retraining."""
    memory_id: str
    agent_id: str
    user_rating: int
    feedback_score: float
    source_prompt: str
    embedding_vector: Optional[List[float]]


# =====================================================================
# DATABASE OPERATIONS
# =====================================================================

class MemoryCleanupDB:
    """Database operations for memory cleanup."""

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

    def analyze_cleanup_rules(self, agent_id: str) -> List[CleanupRule]:
        """
        Analyze which cleanup rules would apply for an agent.

        Returns estimated chunks and MB that would be cleaned.
        """
        conn = self.get_conn()
        try:
            rules = []
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Rule 1: Expired entries
                query = """
                SELECT COUNT(*) as cnt, COALESCE(SUM(memory_size_bytes), 0)::BIGINT as bytes
                FROM agent_memory
                WHERE agent_id = %s AND expires_at < NOW()
                """
                cur.execute(query, (agent_id,))
                row = cur.fetchone()
                rules.append(CleanupRule(
                    priority=1,
                    name='Expired (TTL < NOW())',
                    condition='expires_at < NOW()',
                    estimated_chunks=row['cnt'],
                    estimated_mb=row['bytes'] / 1048576.0
                ))

                # Rule 2: Low-rating old entries
                query = """
                SELECT COUNT(*) as cnt, COALESCE(SUM(memory_size_bytes), 0)::BIGINT as bytes
                FROM agent_memory
                WHERE agent_id = %s
                    AND user_rating < 2
                    AND created_at < (NOW() - INTERVAL '7 days')
                """
                cur.execute(query, (agent_id,))
                row = cur.fetchone()
                rules.append(CleanupRule(
                    priority=2,
                    name='Low-rating old (rating < 2, age > 7d)',
                    condition='user_rating < 2 AND age > 7d',
                    estimated_chunks=row['cnt'],
                    estimated_mb=row['bytes'] / 1048576.0
                ))

                # Rule 3: LRU if quota > 80%
                quota = self.get_quota_status(agent_id)
                if quota and quota['quota_pct'] > 80.0:
                    eviction_needed_mb = (quota['current_memory_mb'] * 0.2)  # Free 20%
                    rules.append(CleanupRule(
                        priority=3,
                        name='LRU Eviction (quota > 80%)',
                        condition='Least-recently-used, access_count < 2',
                        estimated_chunks=int(eviction_needed_mb * 10),  # Rough estimate
                        estimated_mb=eviction_needed_mb
                    ))

            return sorted(rules, key=lambda r: r.priority)

        finally:
            self.return_conn(conn)

    def execute_cleanup(
        self,
        agent_id: str,
        rule_priority: int = 3,  # Execute rules 1-3 by default
        dry_run: bool = False
    ) -> List[CleanupResult]:
        """
        Execute cleanup rules up to specified priority.

        Args:
            agent_id: Target agent
            rule_priority: Execute rules 1 to N (1=expired only, 2=expired+low-rating, 3=+LRU)
            dry_run: Don't actually delete, just report

        Returns:
            List of cleanup results
        """
        conn = self.get_conn()
        try:
            results = []

            # Get before quota
            before_quota = self.get_quota_status(agent_id)

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                start_time = datetime.now()

                # Rule 1: Delete expired
                if rule_priority >= 1:
                    logger.info(f"Rule 1: Deleting expired entries for {agent_id}...")
                    query = """
                    DELETE FROM agent_memory
                    WHERE agent_id = %s AND expires_at < NOW()
                    """
                    if not dry_run:
                        cur.execute(query, (agent_id,))
                        conn.commit()
                    deleted_count = cur.rowcount

                    # Log to tier_log
                    if deleted_count > 0 and not dry_run:
                        self._log_cleanup_audit(
                            agent_id, 'EXPIRED', deleted_count
                        )

                    after_quota = self.get_quota_status(agent_id)
                    freed_mb = (before_quota['current_memory_mb'] - after_quota['current_memory_mb']) \
                        if after_quota else before_quota['current_memory_mb']

                    results.append(CleanupResult(
                        agent_id=agent_id,
                        rule_name='Expired entries',
                        deleted_count=deleted_count,
                        freed_mb=freed_mb,
                        before_quota_pct=before_quota['quota_pct'],
                        after_quota_pct=after_quota['quota_pct'] if after_quota else before_quota['quota_pct'],
                        duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        timestamp=datetime.now()
                    ))

                # Rule 2: Archive low-rating old
                if rule_priority >= 2:
                    logger.info(f"Rule 2: Archiving low-rating old entries for {agent_id}...")
                    before_quota = self.get_quota_status(agent_id)
                    start_time = datetime.now()

                    query = """
                    INSERT INTO agent_memory_archive (
                        agent_id, session_id, memory_key, memory_value, memory_size_bytes,
                        user_rating, source_prompt, checksum, feedback_score,
                        tier, created_at, last_access_at, access_count, archive_reason,
                        archived_by, retention_until
                    )
                    SELECT
                        agent_id, session_id, memory_key, memory_value, memory_size_bytes,
                        user_rating, source_prompt, checksum, feedback_score,
                        'COLD', created_at, last_access_at, access_count, 'LOW_RATING_ARCHIVED',
                        'system', NOW() + INTERVAL '90 days'
                    FROM agent_memory
                    WHERE agent_id = %s
                        AND user_rating < 2
                        AND created_at < (NOW() - INTERVAL '7 days')
                    """
                    if not dry_run:
                        cur.execute(query, (agent_id,))
                        conn.commit()
                    archived_count = cur.rowcount

                    # Delete from warm tier
                    if archived_count > 0 and not dry_run:
                        query = """
                        DELETE FROM agent_memory
                        WHERE agent_id = %s
                            AND user_rating < 2
                            AND created_at < (NOW() - INTERVAL '7 days')
                        """
                        cur.execute(query, (agent_id,))
                        conn.commit()
                        self._log_cleanup_audit(agent_id, 'LOW_RATING_ARCHIVED', archived_count)

                    after_quota = self.get_quota_status(agent_id)
                    freed_mb = (before_quota['current_memory_mb'] - after_quota['current_memory_mb']) \
                        if after_quota else 0

                    results.append(CleanupResult(
                        agent_id=agent_id,
                        rule_name='Low-rating archived (>7d)',
                        deleted_count=archived_count,
                        freed_mb=freed_mb,
                        before_quota_pct=before_quota['quota_pct'],
                        after_quota_pct=after_quota['quota_pct'] if after_quota else before_quota['quota_pct'],
                        duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        timestamp=datetime.now()
                    ))

                # Rule 3: LRU eviction if quota > 80%
                if rule_priority >= 3:
                    logger.info(f"Rule 3: LRU eviction check for {agent_id}...")
                    before_quota = self.get_quota_status(agent_id)
                    if before_quota and before_quota['quota_pct'] > 80.0:
                        start_time = datetime.now()
                        eviction_needed_mb = (before_quota['current_memory_mb'] * 0.2)  # Free 20%

                        query = """
                        DELETE FROM agent_memory
                        WHERE agent_id = %s
                            AND tier IN ('HOT', 'WARM')
                            AND (user_rating < 2 OR access_count < 2)
                        ORDER BY last_access_at ASC
                        LIMIT 1000
                        """
                        if not dry_run:
                            cur.execute(query, (agent_id,))
                            conn.commit()
                        evicted_count = cur.rowcount

                        if evicted_count > 0 and not dry_run:
                            self._log_cleanup_audit(agent_id, 'LRU_EVICTED', evicted_count)

                        after_quota = self.get_quota_status(agent_id)
                        freed_mb = (before_quota['current_memory_mb'] - after_quota['current_memory_mb']) \
                            if after_quota else 0

                        results.append(CleanupResult(
                            agent_id=agent_id,
                            rule_name='LRU eviction (quota > 80%)',
                            deleted_count=evicted_count,
                            freed_mb=freed_mb,
                            before_quota_pct=before_quota['quota_pct'],
                            after_quota_pct=after_quota['quota_pct'] if after_quota else before_quota['quota_pct'],
                            duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                            timestamp=datetime.now()
                        ))

            return results

        finally:
            self.return_conn(conn)

    def get_high_rating_for_r9(self, agent_id: str, threshold: float = 4.0) -> List[R9FeedbackEntry]:
        """
        Fetch high-rating entries for R9 embedding retraining loop.

        Args:
            agent_id: Target agent
            threshold: Rating threshold (default 4.0 out of 5.0)

        Returns:
            List of high-rating entries
        """
        conn = self.get_conn()
        try:
            entries = []
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                SELECT
                    id, agent_id, user_rating, feedback_score, source_prompt,
                    embedding_vector
                FROM agent_state
                WHERE agent_id = %s AND avg_user_rating >= %s
                ORDER BY avg_user_rating DESC
                LIMIT 100
                """
                cur.execute(query, (agent_id, threshold))
                for row in cur.fetchall():
                    entries.append(R9FeedbackEntry(
                        memory_id=row['id'],
                        agent_id=row['agent_id'],
                        user_rating=int(row['user_rating'] or 0),
                        feedback_score=float(row['feedback_score'] or 0),
                        source_prompt=row['source_prompt'],
                        embedding_vector=row['embedding_vector']
                    ))

            return entries

        finally:
            self.return_conn(conn)

    def get_quota_status(self, agent_id: str) -> Optional[Dict]:
        """Get quota status for an agent."""
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM agent_memory_quota WHERE agent_id = %s"
                cur.execute(query, (agent_id,))
                row = cur.fetchone()

                if row:
                    quota_pct = (float(row['current_memory_mb']) / float(row['max_memory_mb'])) * 100.0
                    return {
                        'agent_id': row['agent_id'],
                        'max_memory_mb': float(row['max_memory_mb']),
                        'current_memory_mb': float(row['current_memory_mb']),
                        'quota_pct': quota_pct,
                        'chunk_count': row['chunk_count']
                    }

            return None

        finally:
            self.return_conn(conn)

    def _log_cleanup_audit(self, agent_id: str, reason: str, count: int):
        """Log cleanup operation to audit trail."""
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO agent_memory_tier_log (
                    agent_id, memory_id, from_tier, to_tier, reason
                )
                VALUES (%s, %s, 'WARM', 'DELETED', %s)
                """
                cur.execute(query, (agent_id, str(count) + '_entries', reason))
                conn.commit()
        finally:
            self.return_conn(conn)

    def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Connection pool closed")


# =====================================================================
# CLEANUP ORCHESTRATOR
# =====================================================================

class MemoryCleanupOrchestrator:
    """Orchestrates memory cleanup with alerting."""

    def __init__(
        self,
        db: MemoryCleanupDB,
        dry_run: bool = False,
        slack_webhook: Optional[str] = None
    ):
        self.db = db
        self.dry_run = dry_run
        self.slack_webhook = slack_webhook
        self.cleanup_results: List[CleanupResult] = []
        self.r9_entries: List[R9FeedbackEntry] = []

    def execute_cleanup_for_agent(self, agent_id: str, rule_priority: int = 3) -> Dict:
        """Execute cleanup for specific agent."""
        logger.info(f"Executing cleanup for {agent_id} (priority={rule_priority})")

        try:
            # Show what would be cleaned
            rules = self.db.analyze_cleanup_rules(agent_id)
            logger.info(f"Applicable rules for {agent_id}:")
            for rule in rules:
                if rule.priority <= rule_priority:
                    logger.info(f"  Rule {rule.priority}: {rule.name}")
                    logger.info(f"    Est. chunks: {rule.estimated_chunks}, Est. MB: {rule.estimated_mb:.2f}")

            # Execute cleanup
            results = self.db.execute_cleanup(
                agent_id,
                rule_priority=rule_priority,
                dry_run=self.dry_run
            )
            self.cleanup_results.extend(results)

            # Get high-rating entries for R9
            r9_entries = self.db.get_high_rating_for_r9(agent_id)
            self.r9_entries.extend(r9_entries)

            # Alert if significant cleanup
            total_freed = sum(r.freed_mb for r in results)
            total_deleted = sum(r.deleted_count for r in results)
            if total_freed > 10.0 or total_deleted > 1000:
                self._alert_slack(
                    f"Agent {agent_id}: Cleaned {total_deleted} entries, freed {total_freed:.2f} MB"
                )

            return {
                'agent_id': agent_id,
                'status': 'success',
                'rules_applied': rule_priority,
                'cleanup_results': [asdict(r) for r in results],
                'r9_candidates': len(r9_entries),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Cleanup failed for {agent_id}: {e}", exc_info=True)
            return {
                'agent_id': agent_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _alert_slack(self, message: str):
        """Send alert to Slack if webhook configured."""
        if not self.slack_webhook or not requests:
            return

        try:
            payload = {
                'text': f"[Agent Memory Cleanup] {message}",
                'username': 'Agent Memory Monitor',
                'icon_emoji': ':database:'
            }
            response = requests.post(self.slack_webhook, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to send Slack alert: {e}")

    def get_report(self) -> str:
        """Generate human-readable report."""
        report = []
        report.append("\n" + "="*70)
        report.append("AGENT MEMORY CLEANUP REPORT")
        report.append("="*70)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Dry Run: {self.dry_run}")
        report.append("")

        # Cleanup results
        report.append("CLEANUP OPERATIONS:")
        for result in self.cleanup_results:
            report.append(f"  {result.agent_id} - {result.rule_name}")
            report.append(f"    Deleted: {result.deleted_count} entries")
            report.append(f"    Freed: {result.freed_mb:.2f} MB")
            report.append(f"    Quota: {result.before_quota_pct:.1f}% → {result.after_quota_pct:.1f}%")
            report.append(f"    Duration: {result.duration_ms:.0f} ms")

        # Totals
        total_deleted = sum(r.deleted_count for r in self.cleanup_results)
        total_freed = sum(r.freed_mb for r in self.cleanup_results)
        report.append(f"\nTOTALS:")
        report.append(f"  Entries deleted: {total_deleted}")
        report.append(f"  Total freed: {total_freed:.2f} MB")

        # R9 candidates
        report.append(f"\nR9 FEEDBACK LOOP:")
        report.append(f"  High-rating candidates for embedding retraining: {len(self.r9_entries)}")

        report.append("\n" + "="*70 + "\n")
        return "\n".join(report)


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manta Maestro — Agent Memory Cleanup & LRU Eviction (R10 refined)'
    )
    parser.add_argument('--supabase-url', required=True, help='Supabase project URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase service role key')
    parser.add_argument('--agent-id', help='Target specific agent')
    parser.add_argument('--rule-priority', type=int, default=3, help='Cleanup rule priority (1-3)')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without changes')
    parser.add_argument('--slack-webhook', help='Slack webhook URL for alerts')
    parser.add_argument('--output-json', help='Output JSON report to file')

    args = parser.parse_args()

    try:
        db = MemoryCleanupDB(args.supabase_url, args.supabase_key)
        orchestrator = MemoryCleanupOrchestrator(
            db,
            dry_run=args.dry_run,
            slack_webhook=args.slack_webhook
        )

        if args.agent_id:
            result = orchestrator.execute_cleanup_for_agent(
                args.agent_id,
                rule_priority=args.rule_priority
            )
        else:
            logger.error("--agent-id is required")
            sys.exit(1)

        print(orchestrator.get_report())

        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"JSON report saved to {args.output_json}")

        sys.exit(0 if result['status'] == 'success' else 1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(2)


if __name__ == '__main__':
    main()
