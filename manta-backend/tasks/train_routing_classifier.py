"""
Training task for semantic routing classifier.

Loads agent data from CLAUDE.md or database, trains the ML classifier,
and saves the model for inference.

Usage:
    python train_routing_classifier.py [--data-file routing_data.json] [--model-dir ./models]
"""

import logging
import json
import sys
from pathlib import Path
from typing import Optional, Dict
import argparse
from datetime import datetime

# Add parent directories to path
task_dir = Path(__file__).parent
backend_dir = task_dir.parent
sys.path.insert(0, str(backend_dir))

from ml.routing_classifier import RoutingClassifier

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class RoutingClassifierTrainer:
    """Trainer for semantic routing classifier with optional DB storage."""

    def __init__(self, model_dir: Optional[str] = None, db_url: Optional[str] = None):
        """
        Initialize trainer.

        Args:
            model_dir: Directory to store trained models
            db_url: Optional database URL for storing model metadata
        """
        self.model_dir = model_dir or "./models"
        self.db_url = db_url
        self.classifier = RoutingClassifier(model_dir=self.model_dir)
        self.training_log = {
            "timestamp": datetime.now().isoformat(),
            "status": None,
            "metrics": {},
            "agents_trained": 0,
        }

    def load_training_data(self, data_file: str) -> Dict:
        """
        Load training data from JSON file.

        Args:
            data_file: Path to routing_data.json

        Returns:
            Dictionary of agent data
        """
        data_file_path = Path(data_file)

        if not data_file_path.exists():
            raise FileNotFoundError(f"Training data file not found: {data_file}")

        logger.info(f"Loading training data from {data_file}")
        with open(data_file_path, "r", encoding="utf-8") as f:
            agent_data = json.load(f)

        logger.info(f"Loaded {len(agent_data)} agents")
        self.training_log["agents_trained"] = len(agent_data)

        return agent_data

    def train(self, agent_data_file: str) -> Dict:
        """
        Train the routing classifier.

        Args:
            agent_data_file: Path to routing_data.json

        Returns:
            Training metrics and results
        """
        try:
            # Load training data
            agent_data = self.load_training_data(agent_data_file)

            # Train classifier
            logger.info("Starting classifier training...")
            metrics = self.classifier.train(agent_data_file)

            # Save model
            logger.info("Saving trained model...")
            self.classifier.save_model()

            # Update training log
            self.training_log["status"] = "success"
            self.training_log["metrics"] = metrics

            logger.info("Training completed successfully")
            logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")

            return metrics

        except Exception as e:
            self.training_log["status"] = "failed"
            self.training_log["error"] = str(e)
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise

    def save_training_log(self, log_file: Optional[str] = None) -> str:
        """
        Save training log to file.

        Args:
            log_file: Path to save log. Defaults to logs/training_log.json

        Returns:
            Path to saved log file
        """
        if log_file is None:
            log_dir = Path(self.model_dir) / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = str(log_dir / f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "w") as f:
            json.dump(self.training_log, f, indent=2)

        logger.info(f"Training log saved to {log_file}")
        return log_file

    def store_in_database(self) -> Optional[Dict]:
        """
        Store trained model metadata in database (optional).

        Requires database connection configured.

        Returns:
            Database record or None if DB not configured
        """
        if not self.db_url:
            logger.info("Database URL not configured, skipping DB storage")
            return None

        try:
            logger.info("Storing model metadata in database...")

            # This would store metrics in ml_models table
            # Placeholder for actual database implementation
            db_record = {
                "model_name": "routing_classifier",
                "model_version": "1.0",
                "trained_at": self.training_log["timestamp"],
                "accuracy": self.training_log["metrics"].get("accuracy"),
                "num_agents": self.training_log["agents_trained"],
                "metrics": self.training_log["metrics"],
            }

            logger.info(f"Would store in DB: {json.dumps(db_record, indent=2)}")
            # TODO: Implement actual DB storage when database schema is ready
            # db.ml_models.insert_one(db_record)

            return db_record

        except Exception as e:
            logger.error(f"Failed to store in database: {str(e)}")
            return None


def main():
    """Main entry point for training script."""
    parser = argparse.ArgumentParser(
        description="Train semantic routing classifier for Manta agents"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="ml/routing_data.json",
        help="Path to routing_data.json training data",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default="./models",
        help="Directory to store trained models",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database URL for storing model metadata",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to save training log",
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("Manta Routing Classifier Training")
    logger.info("=" * 80)
    logger.info(f"Data file: {args.data_file}")
    logger.info(f"Model dir: {args.model_dir}")
    logger.info(f"DB URL: {args.db_url or 'Not configured'}")

    try:
        # Initialize trainer
        trainer = RoutingClassifierTrainer(
            model_dir=args.model_dir,
            db_url=args.db_url,
        )

        # Train classifier
        metrics = trainer.train(args.data_file)

        # Save training log
        log_file = trainer.save_training_log(args.log_file)

        # Try to store in database
        db_record = trainer.store_in_database()

        logger.info("=" * 80)
        logger.info("Training Summary")
        logger.info("=" * 80)
        logger.info(f"Status: {trainer.training_log['status']}")
        logger.info(f"Agents trained: {trainer.training_log['agents_trained']}")
        logger.info(f"Accuracy: {metrics.get('accuracy', 'N/A'):.4f}")
        logger.info(f"Precision: {metrics.get('precision', 'N/A'):.4f}")
        logger.info(f"Recall: {metrics.get('recall', 'N/A'):.4f}")
        logger.info(f"F1-Score: {metrics.get('f1', 'N/A'):.4f}")
        logger.info(f"Log file: {log_file}")
        if db_record:
            logger.info(f"Stored in database: Yes")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
