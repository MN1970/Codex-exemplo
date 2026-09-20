#!/usr/bin/env python3
"""
Feedback Loop Job (R9) — Feedback extraction + retraining

Executa semanalmente (domingo @ 03:00 UTC):
1. Fetch user_ratings >= 4 from feedback since last week
2. Extract embedding "user_intent_vector" de queries com score alto
3. Fine-tune reranker cross-encoder com high-scoring queries
4. Update VERSIONS.json com novo checksum
5. Slack notification com métricas de retraining

Objetivo: Melhorar qualidade de reranking via feedback contínuo.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class FeedbackLoopExecutor:
    """
    Executa ciclo de feedback R9 para retraining de reranker.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        repo_root: Path = None
    ):
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        self.repo_root = repo_root or Path.cwd()
        self.versions_file = self.repo_root / "VERSIONS.json"

    def fetch_feedback_since(self, days: int = 7) -> List[Dict]:
        """
        Fetch feedback ratings >= 4 from past N days.

        Returns: List of {query, rating, agent_id, skill_id, rag_reranker_score}
        """
        logger.info(f"Fetching feedback ratings >= 4 from past {days} days...")

        # Mock implementation (real version would use Supabase)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)

        mock_feedback = [
            {
                "query": "Estudo prévio para ETA com 500k habitantes",
                "rating": 5,
                "agent_id": "manta-03-s8",
                "skill_id": "agente-saneamento.v5.0",
                "rag_reranker_score": 0.92,
                "created_at": (now - timedelta(days=3)).isoformat()
            },
            {
                "query": "Projeto executivo de transmissão ANEEL com cabo ACSR",
                "rating": 5,
                "agent_id": "manta-03-s9",
                "skill_id": "agente-energia.v5.0",
                "rag_reranker_score": 0.88,
                "created_at": (now - timedelta(days=2)).isoformat()
            },
            {
                "query": "Porto marítimo com dragagem e molhe quebra-mar",
                "rating": 4,
                "agent_id": "manta-03-s6",
                "skill_id": "agente-portos.v5.0",
                "rag_reranker_score": 0.85,
                "created_at": (now - timedelta(days=5)).isoformat()
            },
            {
                "query": "Barragem CFRD com descaracterização e TSF",
                "rating": 4,
                "agent_id": "manta-03-s10",
                "skill_id": "agente-barragens.v5.0",
                "rag_reranker_score": 0.81,
                "created_at": (now - timedelta(days=4)).isoformat()
            }
        ]

        logger.info(f"Found {len(mock_feedback)} high-rating feedback entries")
        return mock_feedback

    def extract_user_intent_vectors(self, feedback: List[Dict]) -> Dict:
        """
        Extract embeddings (user_intent_vector) from queries with rating >= 4.

        Returns: {
            "queries_processed": N,
            "unique_agents": [...],
            "avg_reranker_score": X.XX,
            "sample_vectors": [...]
        }
        """
        logger.info(f"Extracting user intent vectors from {len(feedback)} queries...")

        if not feedback:
            logger.warning("No feedback to process")
            return {
                "queries_processed": 0,
                "unique_agents": [],
                "avg_reranker_score": 0,
                "sample_vectors": []
            }

        # Mock: simulate embedding extraction
        unique_agents = list(set(f["agent_id"] for f in feedback))
        avg_score = sum(f.get("rag_reranker_score", 0) for f in feedback) / len(feedback)

        result = {
            "queries_processed": len(feedback),
            "unique_agents": unique_agents,
            "avg_reranker_score": avg_score,
            "sample_vectors": [
                {
                    "query": f["query"],
                    "agent_id": f["agent_id"],
                    "rating": f["rating"],
                    "reranker_score": f["rag_reranker_score"]
                }
                for f in feedback[:5]  # Top 5 samples
            ]
        }

        logger.info(f"Extracted vectors: {json.dumps(result, indent=2)}")
        return result

    def retrain_reranker(self, feedback_vectors: Dict) -> Dict:
        """
        Fine-tune cross-encoder reranker with high-scoring queries.

        Returns: {
            "training_status": "completed|skipped",
            "queries_used": N,
            "model_checkpoint": "path/to/checkpoint",
            "improvement_pct": X.XX
        }
        """
        logger.info("Fine-tuning reranker cross-encoder...")

        if feedback_vectors["queries_processed"] < 10:
            logger.warning("Insufficient feedback to retrain (need >= 10 queries)")
            return {
                "training_status": "skipped",
                "queries_used": feedback_vectors["queries_processed"],
                "reason": "Insufficient data"
            }

        # Mock: simulate retraining
        result = {
            "training_status": "completed",
            "queries_used": feedback_vectors["queries_processed"],
            "model_checkpoint": f"/tmp/reranker_checkpoint_{datetime.now().timestamp()}",
            "improvement_pct": 3.2  # Simulated improvement
        }

        logger.info(f"Retraining completed: {json.dumps(result, indent=2)}")
        return result

    def update_versions_checksum(self, training_result: Dict) -> bool:
        """
        Update VERSIONS.json with new reranker checksum.

        Returns: True if updated successfully
        """
        logger.info("Updating VERSIONS.json with new checksum...")

        try:
            with open(self.versions_file) as f:
                versions = json.load(f)
        except FileNotFoundError:
            logger.error(f"VERSIONS.json not found: {self.versions_file}")
            return False

        if training_result.get("training_status") != "completed":
            logger.info("Skipping checksum update (training not completed)")
            return True

        # Mock: compute new checksum
        new_checksum = hashlib.md5(
            json.dumps(training_result).encode()
        ).hexdigest()

        # Update reranker metadata
        if "reranker" not in versions:
            versions["reranker"] = {}

        versions["reranker"]["v5.0"] = {
            "checksum": new_checksum,
            "retrained_at": datetime.now(timezone.utc).isoformat(),
            "training_queries": training_result.get("queries_used", 0),
            "improvement_pct": training_result.get("improvement_pct", 0),
            "model_checkpoint": training_result.get("model_checkpoint", "")
        }

        # Save updated VERSIONS.json
        try:
            with open(self.versions_file, 'w') as f:
                json.dump(versions, f, indent=2)
            logger.info(f"✓ VERSIONS.json updated with checksum: {new_checksum[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to update VERSIONS.json: {e}")
            return False

    def send_slack_notification(self, report: Dict) -> None:
        """Send feedback loop report to Slack"""
        webhook = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook:
            logger.info("Slack webhook not configured, skipping notification")
            return

        try:
            import requests

            message = {
                "text": "Feedback Loop Completed (R9)",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Feedback Loop & Retraining (R9)*\n_Weekly execution completed_"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Feedback entries*\n{report.get('feedback_count', 0)}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Avg Reranker Score*\n{report.get('avg_reranker_score', 0):.2f}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Training Status*\n{report.get('training_status', 'unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Improvement*\n{report.get('improvement_pct', 0):.1f}%"
                            }
                        ]
                    }
                ]
            }

            requests.post(webhook, json=message)
            logger.info("Slack notification sent")
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}")

    def run(self) -> Dict:
        """
        Execute full feedback loop cycle.
        """
        logger.info("=" * 70)
        logger.info("FEEDBACK LOOP EXECUTION (R9)")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 70)

        # Step 1: Fetch feedback
        feedback = self.fetch_feedback_since(days=7)

        # Step 2: Extract vectors
        vectors = self.extract_user_intent_vectors(feedback)

        # Step 3: Retrain
        training_result = self.retrain_reranker(vectors)

        # Step 4: Update VERSIONS.json
        checksum_updated = self.update_versions_checksum(training_result)

        # Build report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback_count": len(feedback),
            "avg_reranker_score": vectors.get("avg_reranker_score", 0),
            "unique_agents": len(vectors.get("unique_agents", [])),
            "training_status": training_result.get("training_status", "unknown"),
            "improvement_pct": training_result.get("improvement_pct", 0),
            "checksum_updated": checksum_updated
        }

        logger.info("=" * 70)
        logger.info("FEEDBACK LOOP REPORT")
        logger.info(json.dumps(report, indent=2))
        logger.info("=" * 70)

        # Send notification
        self.send_slack_notification(report)

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Feedback Loop Job (R9)"
    )
    parser.add_argument(
        '--supabase-url',
        default=os.getenv('SUPABASE_URL'),
        help='Supabase URL'
    )
    parser.add_argument(
        '--supabase-key',
        default=os.getenv('SUPABASE_KEY'),
        help='Supabase API key'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root'
    )

    args = parser.parse_args()

    executor = FeedbackLoopExecutor(
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key,
        repo_root=args.repo_root
    )

    report = executor.run()
    return 0 if report.get("training_status") != "failed" else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
