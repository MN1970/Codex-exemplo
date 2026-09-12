#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Agent Memory Tiering (R10 refined)
Agent memory persistence with Hot/Warm/Cold lifecycle.

Implements 3-tier cache management:
  - HOT (in-process): last 100 completions, 30 min TTL
  - WARM (Supabase): agent_memory table, 480 min TTL
  - COLD (Archive): agent_memory_archive, 90 days retention

Lifecycle transitions:
  HOT → WARM: after 30 min inactivity
  WARM → COLD: after 480 min + user_rating < 2
  COLD → DELETE: after 90 days (GDPR)
  LRU Eviction: when quota > 80%

Author: Claude Haiku 4.5
Ticket: MNT-2026-AGENT-MEMORY-TIERING
Date: 2026-07-25
"""

import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import hashlib
import sys

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_batch
    import psycopg2.pool
except ImportError:
    print("ERROR: psycopg2 not found. Install: pip install psycopg2-binary")
    sys.exit(1)

# =====================================================================
# LOGGING SETUP
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_memory_tiering.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
# DATA MODELS
# =====================================================================

@dataclass
class MemoryEntry:
    """Represents a single memory cache entry."""
    id: str
    agent_id: str
    memory_key: str
    created_at: datetime
    last_access_at: datetime
    access_count: int
    user_rating: Optional[int]
    feedback_score: Optional[float]
    memory_size_bytes: int
    tier: str  # 'HOT', 'WARM', 'COLD'


@dataclass
class TieringMetrics:
    """Metrics for tiering operation."""
    agent_id: str
    from_tier: str
    to_tier: str
    moved_count: int
    freed_mb: float
    reason: str
    timestamp: datetime


@dataclass
class QuotaStatus:
    """Memory quota status for an agent."""
    agent_id: str
    max_memory_mb: float
    current_memory_mb: float
    hot_memory_mb: float
    warm_memory_mb: float
    cold_memory_mb: float
    quota_pct: float
    chunk_count: int
    last_checked_at: datetime


# =====================================================================
# DATABASE CONNECTION POOL
# =====================================================================

class MemoryTieringDB:
    """Database operations for memory tiering."""

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

    def promote_hot_to_warm(self, agent_id: Optional[str] = None) -> List[TieringMetrics]:
        """
        Promote HOT → WARM entries after 30 min inactivity.

        Args:
            agent_id: Specific agent or None for all agents

        Returns:
            List of tiering metrics
        """
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM promote_hot_to_warm()"
                cur.execute(query)
                results = cur.fetchall()

                metrics = []
                for row in results:
                    metrics.append(TieringMetrics(
                        agent_id=row['agent_id'],
                        from_tier='HOT',
                        to_tier='WARM',
                        moved_count=row['moved_count'],
                        freed_mb=float(row['freed_mb'] or 0),
                        reason='INACTIVITY',
                        timestamp=datetime.now()
                    ))

                logger.info(f"Promoted {sum(m.moved_count for m in metrics)} entries HOT→WARM")
                return metrics
        finally:
            self.return_conn(conn)

    def archive_warm_to_cold(self, agent_id: Optional[str] = None) -> List[TieringMetrics]:
        """
        Archive WARM → COLD entries after 480 min + low rating.

        Args:
            agent_id: Specific agent or None for all agents

        Returns:
            List of tiering metrics
        """
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if agent_id:
                    query = "SELECT * FROM archive_warm_to_cold(%s)"
                    cur.execute(query, (agent_id,))
                else:
                    # Archive all agents
                    agents = self._get_agents(conn)
                    for agent in agents:
                        cur.execute("SELECT * FROM archive_warm_to_cold(%s)", (agent,))

                results = cur.fetchall()
                metrics = []
                for row in results:
                    metrics.append(TieringMetrics(
                        agent_id=row['agent_id'],
                        from_tier='WARM',
                        to_tier='COLD',
                        moved_count=row['archived_count'],
                        freed_mb=float(row['freed_mb'] or 0),
                        reason='TTL_EXPIRED_OR_LOW_RATING',
                        timestamp=datetime.now()
                    ))

                logger.info(f"Archived {sum(m.moved_count for m in metrics)} entries WARM→COLD")
                return metrics
        finally:
            self.return_conn(conn)

    def purge_cold_tier(self, agent_id: Optional[str] = None) -> List[TieringMetrics]:
        """
        Purge COLD tier entries after 90 days (GDPR compliance).

        Args:
            agent_id: Specific agent or None for all agents

        Returns:
            List of purge metrics
        """
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if agent_id:
                    query = "SELECT * FROM purge_cold_tier(%s)"
                    cur.execute(query, (agent_id,))
                else:
                    agents = self._get_agents(conn)
                    for agent in agents:
                        cur.execute("SELECT * FROM purge_cold_tier(%s)", (agent,))

                results = cur.fetchall()
                metrics = []
                for row in results:
                    metrics.append(TieringMetrics(
                        agent_id=row['agent_id'],
                        from_tier='COLD',
                        to_tier='DELETED',
                        moved_count=row['purged_count'],
                        freed_mb=float(row['freed_mb'] or 0),
                        reason='GDPR_RETENTION_EXPIRED',
                        timestamp=datetime.now()
                    ))

                logger.info(f"Purged {sum(m.moved_count for m in metrics)} entries (COLD→DELETED)")
                return metrics
        finally:
            self.return_conn(conn)

    def lru_evict_quota_exceeded(self, agent_id: str) -> Optional[TieringMetrics]:
        """
        LRU eviction when quota > 80%.

        Args:
            agent_id: Agent to evict

        Returns:
            Eviction metrics or None if quota OK
        """
        conn = self.get_conn()
        try:
            quota = self.get_quota_status(agent_id)
            if quota.quota_pct < 80.0:
                logger.info(f"Agent {agent_id} quota {quota.quota_pct:.1f}% < 80%, no eviction needed")
                return None

            logger.warning(f"Agent {agent_id} quota {quota.quota_pct:.1f}% > 80%, triggering LRU eviction")

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM lru_evict_quota_exceeded(%s)"
                cur.execute(query, (agent_id,))
                result = cur.fetchone()

                if result:
                    return TieringMetrics(
                        agent_id=result['agent_id'],
                        from_tier='WARM/HOT',
                        to_tier='DELETED',
                        moved_count=result['evicted_count'],
                        freed_mb=float(result['freed_mb'] or 0),
                        reason='QUOTA_EXCEEDED_LRU',
                        timestamp=datetime.now()
                    )
        finally:
            self.return_conn(conn)

    def get_quota_status(self, agent_id: str) -> Optional[QuotaStatus]:
        """Get current quota status for an agent."""
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM agent_memory_quota WHERE agent_id = %s"
                cur.execute(query, (agent_id,))
                row = cur.fetchone()

                if row:
                    quota_pct = (float(row['current_memory_mb']) / float(row['max_memory_mb'])) * 100.0
                    return QuotaStatus(
                        agent_id=row['agent_id'],
                        max_memory_mb=float(row['max_memory_mb']),
                        current_memory_mb=float(row['current_memory_mb']),
                        hot_memory_mb=float(row['hot_memory_mb'] or 0),
                        warm_memory_mb=float(row['warm_memory_mb'] or 0),
                        cold_memory_mb=float(row['cold_memory_mb'] or 0),
                        quota_pct=quota_pct,
                        chunk_count=row['chunk_count'],
                        last_checked_at=row['last_checked_at']
                    )
        finally:
            self.return_conn(conn)

    def get_tier_statistics(self) -> Dict[str, Dict]:
        """Get tier statistics across all agents."""
        conn = self.get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                SELECT
                    tier,
                    COUNT(*) as count,
                    SUM(memory_size_bytes) / 1048576.0 as total_mb,
                    AVG(user_rating) as avg_rating,
                    MAX(last_access_at) as last_access
                FROM agent_memory
                GROUP BY tier
                ORDER BY tier
                """
                cur.execute(query)
                results = cur.fetchall()

                stats = {}
                for row in results:
                    stats[row['tier']] = {
                        'count': row['count'],
                        'total_mb': float(row['total_mb'] or 0),
                        'avg_rating': float(row['avg_rating'] or 0),
                        'last_access': row['last_access'].isoformat() if row['last_access'] else None
                    }

                return stats
        finally:
            self.return_conn(conn)

    def _get_agents(self, conn) -> List[str]:
        """Get list of all agents with memory entries."""
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT agent_id FROM agent_memory ORDER BY agent_id")
            return [row['agent_id'] for row in cur.fetchall()]

    def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Connection pool closed")


# =====================================================================
# TIERING ORCHESTRATOR
# =====================================================================

class MemoryTieringOrchestrator:
    """Orchestrates memory tiering lifecycle."""

    def __init__(self, db: MemoryTieringDB, dry_run: bool = False, verbose: bool = False):
        self.db = db
        self.dry_run = dry_run
        self.verbose = verbose
        self.metrics_log: List[TieringMetrics] = []

    def execute_tiering_cycle(self, agent_id: Optional[str] = None) -> Dict:
        """
        Execute full tiering cycle:
        1. Promote HOT → WARM (30 min)
        2. Archive WARM → COLD (480 min + low rating)
        3. Purge COLD (90 days)
        4. LRU eviction (quota > 80%)
        """
        logger.info(f"Starting tiering cycle (dry_run={self.dry_run})")

        try:
            # Step 1: HOT → WARM
            logger.info("Step 1/4: Promoting HOT → WARM...")
            hot_to_warm = self.db.promote_hot_to_warm(agent_id)
            self.metrics_log.extend(hot_to_warm)

            # Step 2: WARM → COLD
            logger.info("Step 2/4: Archiving WARM → COLD...")
            warm_to_cold = self.db.archive_warm_to_cold(agent_id)
            self.metrics_log.extend(warm_to_cold)

            # Step 3: COLD → DELETE
            logger.info("Step 3/4: Purging COLD tier...")
            cold_purge = self.db.purge_cold_tier(agent_id)
            self.metrics_log.extend(cold_purge)

            # Step 4: LRU eviction if needed
            if agent_id:
                logger.info("Step 4/4: Checking quota for LRU eviction...")
                lru = self.db.lru_evict_quota_exceeded(agent_id)
                if lru:
                    self.metrics_log.append(lru)
            else:
                logger.info("Step 4/4: Skipping LRU (per-agent operation)")

            # Gather final stats
            stats = self.db.get_tier_statistics()
            logger.info(f"Tier statistics: {json.dumps(stats, indent=2)}")

            return {
                'status': 'success',
                'dry_run': self.dry_run,
                'metrics': [asdict(m) for m in self.metrics_log],
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Tiering cycle failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_report(self) -> str:
        """Generate human-readable report."""
        report = []
        report.append("\n" + "="*70)
        report.append("AGENT MEMORY TIERING REPORT")
        report.append("="*70)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Dry Run: {self.dry_run}")
        report.append("")

        # Metrics summary
        report.append("METRICS SUMMARY:")
        for metric in self.metrics_log:
            report.append(f"  {metric.agent_id}: {metric.from_tier}→{metric.to_tier}")
            report.append(f"    Moved: {metric.moved_count} entries")
            report.append(f"    Freed: {metric.freed_mb:.2f} MB")
            report.append(f"    Reason: {metric.reason}")

        # Totals
        total_moved = sum(m.moved_count for m in self.metrics_log)
        total_freed = sum(m.freed_mb for m in self.metrics_log)
        report.append(f"\nTOTALS:")
        report.append(f"  Entries moved: {total_moved}")
        report.append(f"  Total freed: {total_freed:.2f} MB")

        report.append("\n" + "="*70 + "\n")
        return "\n".join(report)


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manta Maestro — Agent Memory Tiering (R10 refined)'
    )
    parser.add_argument(
        '--supabase-url',
        required=True,
        help='Supabase project URL'
    )
    parser.add_argument(
        '--supabase-key',
        required=True,
        help='Supabase service role key'
    )
    parser.add_argument(
        '--agent-id',
        help='Target specific agent (default: all agents)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose logging'
    )
    parser.add_argument(
        '--output-json',
        help='Output JSON report to file'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        db = MemoryTieringDB(args.supabase_url, args.supabase_key)
        orchestrator = MemoryTieringOrchestrator(
            db,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        result = orchestrator.execute_tiering_cycle(args.agent_id)

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
