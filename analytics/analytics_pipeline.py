"""
Phase 4.2 Advanced Analytics — Data Collection & Aggregation Pipeline

Collects routing decisions, query patterns, costs, and user cohorts.
Feeds BI dashboards, predictive models, and performance monitoring.

Pipeline:
  1. Event capture (Maestro routing logs)
  2. Data validation & enrichment
  3. Aggregation (hourly, daily, weekly)
  4. Storage (Supabase + S3 parquet)
  5. Federation (multi-org rollup)

Cost tracking:
  - Per-query: model tokens × price per k tokens
  - Per-agent: sum(queries) × avg cost
  - Per-user: cohort-based consumption

Accuracy tracking:
  - Routing tier (correct agent selected)
  - User satisfaction (feedback loop)
  - Fallback rate (queries routed to human)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class RoutingOutcome(str, Enum):
    """Routing decision outcomes."""
    CORRECT = "correct"
    FALLBACK = "fallback"
    HUMAN_ESCALATION = "human_escalation"
    TIMEOUT = "timeout"
    ERROR = "error"


class UserCohort(str, Enum):
    """User segmentation for cohort analysis."""
    POWER_USER = "power_user"      # >100 queries/month
    ACTIVE = "active"               # 20-100 queries/month
    CASUAL = "casual"               # 1-20 queries/month
    INACTIVE = "inactive"           # 0 queries in 30 days


@dataclass
class RoutingEvent:
    """Single routing decision event."""
    event_id: str
    timestamp: datetime
    user_id: str
    organization_id: str
    query: str

    # Routing decision
    routed_agent: str
    routing_confidence: float
    routing_method: str  # "keyword", "vector", "llm_tiebreaker"

    # Outcome
    outcome: str  # RoutingOutcome
    feedback_score: Optional[float]  # 1-5 star rating (post-interaction)

    # Cost
    input_tokens: int
    output_tokens: int
    model_used: str
    cost_usd: float

    # Context
    phase: str  # "1", "2", "3", "4"
    region: str
    segment: str  # S1-S10, horizontals


@dataclass
class AggregatedMetrics:
    """Hourly/daily aggregated metrics."""
    period: str  # "hourly", "daily"
    timestamp: datetime
    organization_id: str

    # Volume
    total_queries: int
    unique_users: int

    # Accuracy
    routing_accuracy: float  # % correct
    feedback_avg: float  # avg satisfaction 1-5
    fallback_rate: float  # % human escalations

    # Cost
    total_cost_usd: float
    cost_per_query_usd: float
    tokens_total: int

    # Breakdown
    by_agent: Dict[str, int]  # agent → query count
    by_cohort: Dict[str, int]  # cohort → query count
    by_model: Dict[str, int]  # model → count


class RoutingEventTable(Base):
    """Supabase table: routing_events (time-series)."""
    __tablename__ = "routing_events"

    event_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, index=True)
    user_id = Column(String, index=True)
    organization_id = Column(String, index=True)
    query_hash = Column(String, index=True)
    routed_agent = Column(String, index=True)
    routing_confidence = Column(Float)
    routing_method = Column(String)
    outcome = Column(String)
    feedback_score = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    model_used = Column(String)
    cost_usd = Column(Float)
    phase = Column(String)
    region = Column(String)
    segment = Column(String)


class AggregatedMetricsTable(Base):
    """Supabase table: aggregated_metrics (daily/weekly rollup)."""
    __tablename__ = "aggregated_metrics"

    metric_id = Column(String, primary_key=True)
    period = Column(String)  # "daily", "weekly"
    timestamp = Column(DateTime, index=True)
    organization_id = Column(String, index=True)
    total_queries = Column(Integer)
    unique_users = Column(Integer)
    routing_accuracy = Column(Float)
    feedback_avg = Column(Float)
    fallback_rate = Column(Float)
    total_cost_usd = Column(Float)
    cost_per_query_usd = Column(Float)
    tokens_total = Column(Integer)
    metrics_json = Column(String)  # JSON: by_agent, by_cohort, by_model


class AnalyticsPipeline:
    """
    Main analytics pipeline: event capture → aggregation → storage.

    Usage:
        pipeline = AnalyticsPipeline(supabase_url, supabase_key)
        pipeline.ingest_event(routing_event)
        pipeline.aggregate_daily("org-123")
    """

    def __init__(self, db_url: str, supabase_client=None):
        """
        Args:
            db_url: PostgreSQL connection string
            supabase_client: optional supabase.Client for vector updates
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.supabase = supabase_client
        Base.metadata.create_all(self.engine)

    def ingest_event(self, event: RoutingEvent) -> bool:
        """
        Ingest a single routing event.

        Args:
            event: RoutingEvent dataclass

        Returns:
            True if successfully stored
        """
        try:
            session = self.Session()
            row = RoutingEventTable(**asdict(event))
            session.add(row)
            session.commit()
            session.close()
            logger.info(f"Ingested event {event.event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest event: {e}")
            return False

    def batch_ingest(self, events: List[RoutingEvent]) -> int:
        """
        Batch ingest multiple events (more efficient than single).

        Args:
            events: List of RoutingEvent objects

        Returns:
            Count of successfully ingested events
        """
        session = self.Session()
        count = 0
        try:
            for event in events:
                row = RoutingEventTable(**asdict(event))
                session.add(row)
                count += 1
            session.commit()
            logger.info(f"Batch ingested {count} events")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"Batch ingest failed: {e}")
            return 0
        finally:
            session.close()

    def calculate_routing_accuracy(self, org_id: str, hours: int = 24) -> float:
        """
        Calculate % of correctly routed queries (feedback score ≥ 4).

        Args:
            org_id: Organization ID
            hours: Look back window

        Returns:
            Accuracy percentage (0-100)
        """
        session = self.Session()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            total = session.query(RoutingEventTable).filter(
                RoutingEventTable.organization_id == org_id,
                RoutingEventTable.timestamp >= cutoff
            ).count()

            if total == 0:
                return 0.0

            correct = session.query(RoutingEventTable).filter(
                RoutingEventTable.organization_id == org_id,
                RoutingEventTable.timestamp >= cutoff,
                RoutingEventTable.feedback_score >= 4.0
            ).count()

            return (correct / total) * 100.0
        finally:
            session.close()

    def calculate_cost_per_query(self, org_id: str, days: int = 7) -> float:
        """
        Calculate average cost per query.

        Args:
            org_id: Organization ID
            days: Aggregation window

        Returns:
            USD cost per query
        """
        session = self.Session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            df = pd.read_sql_query(
                f"""
                SELECT SUM(cost_usd) as total_cost, COUNT(*) as query_count
                FROM routing_events
                WHERE organization_id = '{org_id}'
                AND timestamp >= '{cutoff}'
                """,
                self.engine
            )

            if df['query_count'].iloc[0] == 0:
                return 0.0

            return df['total_cost'].iloc[0] / df['query_count'].iloc[0]
        finally:
            session.close()

    def cohort_analysis(self, org_id: str, days: int = 30) -> Dict[str, int]:
        """
        Segment users into cohorts based on query volume.

        Returns:
            {cohort_name: user_count}
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        df = pd.read_sql_query(
            f"""
            SELECT user_id, COUNT(*) as query_count
            FROM routing_events
            WHERE organization_id = '{org_id}'
            AND timestamp >= '{cutoff}'
            GROUP BY user_id
            """,
            self.engine
        )

        def assign_cohort(count: int) -> str:
            if count > 100:
                return UserCohort.POWER_USER.value
            elif count >= 20:
                return UserCohort.ACTIVE.value
            elif count >= 1:
                return UserCohort.CASUAL.value
            else:
                return UserCohort.INACTIVE.value

        df['cohort'] = df['query_count'].apply(assign_cohort)
        return df['cohort'].value_counts().to_dict()

    def aggregate_daily(self, org_id: str, target_date: Optional[datetime] = None) -> AggregatedMetrics:
        """
        Compute daily aggregated metrics.

        Args:
            org_id: Organization ID
            target_date: Date to aggregate (default: yesterday)

        Returns:
            AggregatedMetrics dataclass
        """
        if target_date is None:
            target_date = datetime.utcnow() - timedelta(days=1)

        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        df = pd.read_sql_query(
            f"""
            SELECT *
            FROM routing_events
            WHERE organization_id = '{org_id}'
            AND timestamp >= '{start}' AND timestamp < '{end}'
            """,
            self.engine
        )

        if df.empty:
            return AggregatedMetrics(
                period="daily",
                timestamp=start,
                organization_id=org_id,
                total_queries=0,
                unique_users=0,
                routing_accuracy=0.0,
                feedback_avg=0.0,
                fallback_rate=0.0,
                total_cost_usd=0.0,
                cost_per_query_usd=0.0,
                tokens_total=0,
                by_agent={},
                by_cohort={},
                by_model={}
            )

        # Compute metrics
        total_queries = len(df)
        unique_users = df['user_id'].nunique()
        correct = (df['feedback_score'] >= 4.0).sum()
        routing_accuracy = (correct / total_queries * 100) if total_queries > 0 else 0.0
        feedback_avg = df['feedback_score'].mean() if 'feedback_score' in df else 0.0
        fallback_rate = (df['outcome'] == 'human_escalation').sum() / total_queries if total_queries > 0 else 0.0
        total_cost = df['cost_usd'].sum()
        cost_per_query = total_cost / total_queries if total_queries > 0 else 0.0
        tokens_total = df['input_tokens'].sum() + df['output_tokens'].sum()

        # Breakdowns
        by_agent = df['routed_agent'].value_counts().to_dict()
        by_model = df['model_used'].value_counts().to_dict()

        cohorts = {}
        for _, row in df.iterrows():
            cohort = UserCohort.CASUAL.value  # default
            cohorts[cohort] = cohorts.get(cohort, 0) + 1

        return AggregatedMetrics(
            period="daily",
            timestamp=start,
            organization_id=org_id,
            total_queries=total_queries,
            unique_users=unique_users,
            routing_accuracy=routing_accuracy,
            feedback_avg=feedback_avg,
            fallback_rate=fallback_rate,
            total_cost_usd=total_cost,
            cost_per_query_usd=cost_per_query,
            tokens_total=tokens_total,
            by_agent=by_agent,
            by_cohort=cohorts,
            by_model=by_model
        )

    def export_parquet(self, org_id: str, s3_bucket: str, days: int = 7):
        """
        Export aggregated metrics to S3 Parquet for BI tools.

        Args:
            org_id: Organization ID
            s3_bucket: S3 bucket name
            days: Look-back window
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        df = pd.read_sql_query(
            f"""
            SELECT *
            FROM routing_events
            WHERE organization_id = '{org_id}'
            AND timestamp >= '{cutoff}'
            """,
            self.engine
        )

        if df.empty:
            logger.warning(f"No data to export for {org_id}")
            return

        filename = f"s3://{s3_bucket}/analytics/{org_id}/{datetime.utcnow().isoformat()}.parquet"
        df.to_parquet(filename, engine='pyarrow', compression='snappy')
        logger.info(f"Exported {len(df)} rows to {filename}")

    def federation_rollup(self, org_ids: List[str]) -> AggregatedMetrics:
        """
        Aggregate metrics across multiple organizations (Phase 4.1).

        Args:
            org_ids: List of organization IDs

        Returns:
            Consolidated AggregatedMetrics
        """
        all_metrics = []
        for org_id in org_ids:
            metrics = self.aggregate_daily(org_id)
            all_metrics.append(metrics)

        # Rollup
        total_queries = sum(m.total_queries for m in all_metrics)
        unique_users = sum(m.unique_users for m in all_metrics)
        avg_accuracy = np.mean([m.routing_accuracy for m in all_metrics if m.total_queries > 0])
        avg_feedback = np.mean([m.feedback_avg for m in all_metrics if m.feedback_avg > 0])
        total_cost = sum(m.total_cost_usd for m in all_metrics)

        return AggregatedMetrics(
            period="daily",
            timestamp=datetime.utcnow(),
            organization_id="FEDERATION",
            total_queries=total_queries,
            unique_users=unique_users,
            routing_accuracy=avg_accuracy,
            feedback_avg=avg_feedback,
            fallback_rate=0.0,
            total_cost_usd=total_cost,
            cost_per_query_usd=total_cost / total_queries if total_queries > 0 else 0.0,
            tokens_total=sum(m.tokens_total for m in all_metrics),
            by_agent={},
            by_cohort={},
            by_model={}
        )
