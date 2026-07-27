"""
Active Learning Framework for Pillar D
Implements uncertainty sampling (75-85% coverage) and feedback loop
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UncertaintySamplingStrategy(Enum):
    """Uncertainty sampling strategies"""
    MARGIN_SAMPLING = "margin_sampling"  # 1 - margin between top 2 classes
    ENTROPY_SAMPLING = "entropy_sampling"  # Shannon entropy
    LEAST_CONFIDENCE = "least_confidence"  # 1 - max probability
    VOTE_ENTROPY = "vote_entropy"  # Entropy across ensemble predictions


@dataclass
class QueryInstance:
    """Instance queued for human labeling"""
    instance_id: str
    feature_vector: np.ndarray
    uncertainty_score: float
    strategy_used: UncertaintySamplingStrategy
    ensemble_prediction: float
    rf_prediction: float
    xgb_prediction: float
    created_at: str


@dataclass
class FeedbackRecord:
    """Record of feedback from human annotation"""
    instance_id: str
    true_label: int
    predicted_label: int
    uncertainty_score: float
    feedback_timestamp: str
    feedback_source: str  # "human", "automated", "oracle"
    confidence: float = 1.0  # Confidence in the feedback


class ActiveLearningManager:
    """
    Manages active learning loop for model improvement
    Target: 75-85% coverage with strategic sampling
    """

    def __init__(
        self,
        uncertainty_threshold: float = 0.4,
        batch_size: int = 100,
        target_coverage: float = 0.80,
        strategy: UncertaintySamplingStrategy = UncertaintySamplingStrategy.ENTROPY_SAMPLING,
    ):
        self.uncertainty_threshold = uncertainty_threshold
        self.batch_size = batch_size
        self.target_coverage = target_coverage
        self.strategy = strategy

        self.unlabeled_pool = []
        self.labeled_pool = []
        self.pending_feedback = []
        self.feedback_history = []

    def compute_uncertainty(
        self,
        rf_proba: np.ndarray,
        xgb_proba: np.ndarray,
        ensemble_proba: np.ndarray,
    ) -> np.ndarray:
        """Compute uncertainty scores based on strategy"""
        if self.strategy == UncertaintySamplingStrategy.MARGIN_SAMPLING:
            return self._margin_sampling(ensemble_proba)

        elif self.strategy == UncertaintySamplingStrategy.ENTROPY_SAMPLING:
            return self._entropy_sampling(ensemble_proba)

        elif self.strategy == UncertaintySamplingStrategy.LEAST_CONFIDENCE:
            return self._least_confidence(ensemble_proba)

        elif self.strategy == UncertaintySamplingStrategy.VOTE_ENTROPY:
            return self._vote_entropy(rf_proba, xgb_proba)

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    @staticmethod
    def _margin_sampling(proba: np.ndarray) -> np.ndarray:
        """Margin between 0.5 and prediction"""
        return np.abs(proba - 0.5)

    @staticmethod
    def _entropy_sampling(proba: np.ndarray) -> np.ndarray:
        """Shannon entropy"""
        # Convert to probabilities for both classes
        p0 = 1 - proba
        p1 = proba

        # Avoid log(0)
        p0 = np.clip(p0, 1e-10, 1.0)
        p1 = np.clip(p1, 1e-10, 1.0)

        entropy = -(p0 * np.log2(p0) + p1 * np.log2(p1))
        return entropy / 1.0  # Normalize to [0, 1]

    @staticmethod
    def _least_confidence(proba: np.ndarray) -> np.ndarray:
        """1 - max probability"""
        return 1 - np.maximum(proba, 1 - proba)

    @staticmethod
    def _vote_entropy(rf_proba: np.ndarray, xgb_proba: np.ndarray) -> np.ndarray:
        """Entropy of disagreement between models"""
        # Voting: count votes for class 1
        votes = (rf_proba > 0.5).astype(int) + (xgb_proba > 0.5).astype(int)
        vote_proba = votes / 2.0  # 0, 0.5, or 1

        # Entropy
        p0 = 1 - vote_proba
        p1 = vote_proba

        p0 = np.clip(p0, 1e-10, 1.0)
        p1 = np.clip(p1, 1e-10, 1.0)

        entropy = -(p0 * np.log2(p0) + p1 * np.log2(p1))
        return entropy / 1.0

    def select_for_labeling(
        self,
        X: pd.DataFrame,
        rf_predictions: np.ndarray,
        xgb_predictions: np.ndarray,
        ensemble_predictions: np.ndarray,
        instance_ids: List[str],
        batch_size: Optional[int] = None,
    ) -> List[QueryInstance]:
        """
        Select instances with highest uncertainty for labeling
        Returns batch of QueryInstance objects ready for human annotation
        """
        batch_size = batch_size or self.batch_size

        # Compute uncertainties
        uncertainties = self.compute_uncertainty(
            rf_predictions, xgb_predictions, ensemble_predictions
        )

        # Filter by threshold
        above_threshold = uncertainties >= self.uncertainty_threshold
        candidate_indices = np.where(above_threshold)[0]

        logger.info(
            f"Selected {len(candidate_indices)} candidates "
            f"from {len(X)} ({100*len(candidate_indices)/len(X):.1f}%) "
            f"with uncertainty >= {self.uncertainty_threshold}"
        )

        # Sort by uncertainty (highest first)
        sorted_indices = candidate_indices[np.argsort(uncertainties[candidate_indices])[::-1]]

        # Take top batch_size
        selected_indices = sorted_indices[:batch_size]

        # Create query instances
        query_batch = []
        for idx in selected_indices:
            query = QueryInstance(
                instance_id=instance_ids[idx],
                feature_vector=X.iloc[idx].values,
                uncertainty_score=float(uncertainties[idx]),
                strategy_used=self.strategy,
                ensemble_prediction=float(ensemble_predictions[idx]),
                rf_prediction=float(rf_predictions[idx]),
                xgb_prediction=float(xgb_predictions[idx]),
                created_at=datetime.now().isoformat(),
            )
            query_batch.append(query)

        self.pending_feedback.extend(query_batch)

        logger.info(
            f"Created batch of {len(query_batch)} instances for labeling "
            f"(uncertainty range: {uncertainties[selected_indices].min():.4f} - "
            f"{uncertainties[selected_indices].max():.4f})"
        )

        return query_batch

    def add_feedback(
        self,
        instance_id: str,
        true_label: int,
        feedback_source: str = "human",
        confidence: float = 1.0,
    ) -> bool:
        """Add feedback for a pending query instance"""
        # Find in pending feedback
        pending_idx = None
        for i, query in enumerate(self.pending_feedback):
            if query.instance_id == instance_id:
                pending_idx = i
                break

        if pending_idx is None:
            logger.warning(f"Instance {instance_id} not found in pending feedback")
            return False

        query = self.pending_feedback.pop(pending_idx)

        # Create feedback record
        feedback = FeedbackRecord(
            instance_id=instance_id,
            true_label=true_label,
            predicted_label=int(query.ensemble_prediction >= 0.5),
            uncertainty_score=query.uncertainty_score,
            feedback_timestamp=datetime.now().isoformat(),
            feedback_source=feedback_source,
            confidence=confidence,
        )

        self.feedback_history.append(feedback)
        self.labeled_pool.append((query.feature_vector, true_label))

        logger.info(
            f"Feedback added for {instance_id}: "
            f"true={true_label}, predicted={feedback.predicted_label}, "
            f"uncertainty={query.uncertainty_score:.4f}"
        )

        return True

    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback received"""
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "accuracy": 0.0,
                "coverage": 0.0,
                "pending_feedback": len(self.pending_feedback),
            }

        feedback = self.feedback_history

        # Accuracy
        correct = sum(
            f.true_label == f.predicted_label for f in feedback
        )
        accuracy = correct / len(feedback) if feedback else 0.0

        # Coverage of uncertainty
        avg_uncertainty = np.mean([f.uncertainty_score for f in feedback])

        return {
            "total_feedback": len(feedback),
            "accuracy": accuracy,
            "avg_uncertainty": avg_uncertainty,
            "pending_feedback": len(self.pending_feedback),
            "labeled_pool_size": len(self.labeled_pool),
            "feedback_sources": {
                source: sum(1 for f in feedback if f.feedback_source == source)
                for source in set(f.feedback_source for f in feedback)
            },
        }

    def is_target_coverage_reached(self) -> bool:
        """Check if target coverage is reached"""
        if not self.labeled_pool:
            return False

        coverage = len(self.feedback_history) / (len(self.feedback_history) + len(self.pending_feedback) + 1)
        return coverage >= self.target_coverage

    def get_labeled_data_for_retraining(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get labeled feedback data for model retraining"""
        if not self.labeled_pool:
            return np.array([]), np.array([])

        X = np.array([x for x, _ in self.labeled_pool])
        y = np.array([y for _, y in self.labeled_pool])

        logger.info(f"Prepared {len(X)} labeled instances for retraining")
        return X, y

    def reset_pending(self):
        """Clear pending feedback (e.g., after batch expires)"""
        cleared = len(self.pending_feedback)
        self.pending_feedback.clear()
        logger.info(f"Cleared {cleared} pending feedback instances")


class FeedbackAccumulator:
    """Accumulates feedback over time with quality metrics"""

    def __init__(self, min_feedback_for_retraining: int = 100):
        self.min_feedback = min_feedback_for_retraining
        self.feedback_buffer = []
        self.quality_scores = []

    def add_feedback_batch(self, feedbacks: List[FeedbackRecord]):
        """Add batch of feedback records"""
        for f in feedbacks:
            self.feedback_buffer.append(f)
            # Quality score: 1 if correct, 0 otherwise
            quality = 1.0 if f.true_label == f.predicted_label else 0.0
            self.quality_scores.append(quality * f.confidence)

    def is_ready_for_retraining(self) -> bool:
        """Check if accumulated feedback is ready for retraining"""
        return len(self.feedback_buffer) >= self.min_feedback

    def get_quality_report(self) -> Dict:
        """Get report on feedback quality"""
        if not self.quality_scores:
            return {
                "total_feedback": 0,
                "average_quality": 0.0,
                "quality_std": 0.0,
            }

        quality_array = np.array(self.quality_scores)
        return {
            "total_feedback": len(self.quality_scores),
            "average_quality": float(np.mean(quality_array)),
            "quality_std": float(np.std(quality_array)),
            "min_quality": float(np.min(quality_array)),
            "max_quality": float(np.max(quality_array)),
        }

    def get_retraining_data(self) -> Tuple[List[FeedbackRecord], List]:
        """Get accumulated feedback for retraining"""
        data = self.feedback_buffer.copy()
        self.feedback_buffer.clear()
        self.quality_scores.clear()
        return data, self.quality_scores


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Pillar D — Active Learning Framework")
    print("=" * 80)

    # Simulate predictions
    n_samples = 500
    rf_proba = np.random.uniform(0, 1, n_samples)
    xgb_proba = np.random.uniform(0, 1, n_samples)
    ensemble_proba = 0.65 * rf_proba + 0.35 * xgb_proba

    # Create dummy features
    X = pd.DataFrame(np.random.randn(n_samples, 50), columns=[f"feat_{i}" for i in range(50)])
    instance_ids = [f"instance_{i}" for i in range(n_samples)]

    # Initialize active learning
    print("\n[1/3] Initializing Active Learning Manager...")
    al_manager = ActiveLearningManager(
        uncertainty_threshold=0.3,
        batch_size=50,
        target_coverage=0.80,
        strategy=UncertaintySamplingStrategy.ENTROPY_SAMPLING,
    )
    print(f"  Strategy: {al_manager.strategy.value}")
    print(f"  Uncertainty threshold: {al_manager.uncertainty_threshold}")
    print(f"  Target coverage: {al_manager.target_coverage}")

    # Select for labeling
    print("\n[2/3] Selecting instances for labeling...")
    query_batch = al_manager.select_for_labeling(
        X, rf_proba, xgb_proba, ensemble_proba, instance_ids, batch_size=50
    )
    print(f"  Selected {len(query_batch)} instances")
    print(f"  Avg uncertainty: {np.mean([q.uncertainty_score for q in query_batch]):.4f}")

    # Add feedback
    print("\n[3/3] Adding feedback...")
    for i, query in enumerate(query_batch):
        # Simulate feedback: correct 80% of the time
        true_label = query.ensemble_prediction > 0.5
        if np.random.random() > 0.8:
            true_label = 1 - true_label
        al_manager.add_feedback(query.instance_id, int(true_label))

    summary = al_manager.get_feedback_summary()
    print(f"  Feedback summary:")
    print(f"    Total feedback: {summary['total_feedback']}")
    print(f"    Accuracy: {summary['accuracy']:.4f}")
    print(f"    Avg uncertainty: {summary['avg_uncertainty']:.4f}")
    print(f"    Pending feedback: {summary['pending_feedback']}")

    print("\n✓ Active Learning Framework operational!")
