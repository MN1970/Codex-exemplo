"""
ML-based semantic routing classifier for Manta agents.
Uses TF-IDF vectorization and Logistic Regression to predict
the best agent(s) for a given query.

Usage:
    classifier = RoutingClassifier()
    classifier.train(agent_data)
    classifier.save_model()
    predictions = classifier.predict(query, top_k=3)
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import joblib
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class RoutingClassifier:
    """ML classifier for semantic routing to Manta agents."""

    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the routing classifier.

        Args:
            model_dir: Directory to store trained models. Defaults to ./models
        """
        self.model_dir = Path(model_dir or "./models")
        self.model_dir.mkdir(exist_ok=True)

        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words="english",
            min_df=1,
            max_df=0.9,
        )
        self.label_encoder = LabelEncoder()
        self.model = None
        self.agent_data = {}
        self.agent_keywords = {}
        self.metrics = {}

    def load_agent_data(self, data_file: str) -> Dict:
        """
        Load agent data from JSON file.

        Args:
            data_file: Path to routing_data.json

        Returns:
            Dictionary of agent data
        """
        with open(data_file, "r") as f:
            self.agent_data = json.load(f)

        logger.info(f"Loaded {len(self.agent_data)} agents from {data_file}")
        return self.agent_data

    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Prepare training data from agent keywords and descriptions.

        Returns:
            (texts, labels) - lists of concatenated text and agent slugs
        """
        texts = []
        labels = []

        for agent_slug, agent_info in self.agent_data.items():
            # Combine keywords and description
            keywords = " ".join(agent_info.get("keywords", []))
            description = agent_info.get("description", "")
            agent_name = agent_info.get("name", "")

            # Create combined text for this agent
            combined_text = f"{agent_name} {keywords} {description}"
            texts.append(combined_text)
            labels.append(agent_slug)

            # Store keywords for fallback matching
            self.agent_keywords[agent_slug] = agent_info.get("keywords", [])

        logger.info(
            f"Prepared {len(texts)} training samples ({len(set(labels))} unique agents)"
        )
        return texts, labels

    def train(self, agent_data_file: str, test_size: float = 0.0):
        """
        Train the routing classifier.

        Args:
            agent_data_file: Path to routing_data.json
            test_size: Proportion of data to use for testing (0.0 = no test)
        """
        # Load agent data
        self.load_agent_data(agent_data_file)

        # Prepare training data
        texts, labels = self.prepare_training_data()

        # Vectorize texts
        logger.info("Vectorizing text with TF-IDF...")
        X = self.vectorizer.fit_transform(texts)
        logger.info(f"Feature matrix shape: {X.shape}")

        # Encode labels
        y = self.label_encoder.fit_transform(labels)
        logger.info(f"Encoded labels: {len(self.label_encoder.classes_)} classes")

        # Train Logistic Regression
        logger.info("Training Logistic Regression classifier...")
        self.model = LogisticRegression(
            max_iter=1000,
            multi_class="multinomial",
            solver="lbfgs",
            random_state=42,
            verbose=1,
        )
        self.model.fit(X, y)

        # Calculate metrics on training data
        y_pred = self.model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y, y_pred, average="weighted", zero_division=0)

        self.metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "num_agents": len(self.label_encoder.classes_),
            "num_samples": len(texts),
        }

        logger.info(f"Training complete!")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1-Score: {f1:.4f}")

        # Print confusion matrix
        cm = confusion_matrix(y, y_pred)
        logger.info(f"Confusion matrix shape: {cm.shape}")

        # Print classification report
        logger.info(
            "Classification Report:\n"
            + classification_report(
                y, y_pred, target_names=self.label_encoder.classes_, zero_division=0
            )
        )

        return self.metrics

    def predict(
        self, query: str, top_k: int = 3, confidence_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Predict the best agents for a query.

        Args:
            query: Input query text
            top_k: Number of top predictions to return
            confidence_threshold: Minimum confidence score to include

        Returns:
            List of dicts with agent_slug, agent_name, and confidence
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        # Vectorize query
        X = self.vectorizer.transform([query])

        # Get predictions and probabilities
        y_pred = self.model.predict(X)[0]
        y_proba = self.model.predict_proba(X)[0]

        # Get top-k predictions
        top_indices = np.argsort(y_proba)[::-1][:top_k]

        results = []
        for idx in top_indices:
            confidence = float(y_proba[idx])
            if confidence >= confidence_threshold:
                agent_slug = self.label_encoder.classes_[idx]
                agent_name = self.agent_data[agent_slug]["name"]

                results.append(
                    {
                        "agent_slug": agent_slug,
                        "agent_name": agent_name,
                        "confidence": confidence,
                    }
                )

        logger.info(f"Predicted agents for '{query[:50]}...': {results}")
        return results

    def predict_with_fallback(
        self, query: str, top_k: int = 3, confidence_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Predict agents with fallback to keyword matching if confidence is low.

        Args:
            query: Input query text
            top_k: Number of top predictions to return
            confidence_threshold: Minimum confidence to skip keyword fallback

        Returns:
            List of dicts with agent_slug, agent_name, and confidence
        """
        # Get ML predictions
        ml_results = self.predict(query, top_k=top_k, confidence_threshold=0.0)

        # If top prediction is high confidence, return it
        if ml_results and ml_results[0]["confidence"] >= confidence_threshold:
            return ml_results[:top_k]

        # Fallback: keyword matching
        logger.info("Low confidence scores, falling back to keyword matching...")
        keyword_results = self._keyword_fallback(query, top_k)

        if keyword_results:
            logger.info(f"Keyword fallback results: {keyword_results}")
            return keyword_results

        # If no keyword matches, return ML results anyway
        logger.info("No keyword matches, returning ML predictions...")
        return ml_results[:top_k]

    def _keyword_fallback(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Fallback keyword matching when ML confidence is low.

        Args:
            query: Input query text
            top_k: Number of top results to return

        Returns:
            List of dicts with agent_slug, agent_name, and confidence
        """
        query_lower = query.lower()
        scores = {}

        for agent_slug, keywords in self.agent_keywords.items():
            # Count keyword matches
            match_count = sum(1 for kw in keywords if kw.lower() in query_lower)
            if match_count > 0:
                # Score based on match count and keyword rarity
                score = match_count / len(keywords) if keywords else 0
                scores[agent_slug] = score

        if not scores:
            return []

        # Sort by score descending
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for agent_slug, score in sorted_agents:
            agent_name = self.agent_data[agent_slug]["name"]
            results.append(
                {
                    "agent_slug": agent_slug,
                    "agent_name": agent_name,
                    "confidence": float(score),
                    "method": "keyword_match",
                }
            )

        return results

    def save_model(self, prefix: str = "routing_classifier"):
        """
        Save trained model, vectorizer, and label encoder.

        Args:
            prefix: Prefix for saved files
        """
        if self.model is None:
            raise RuntimeError("No model to save. Train first.")

        # Save model
        model_file = self.model_dir / f"{prefix}_model.pkl"
        joblib.dump(self.model, model_file)
        logger.info(f"Saved model to {model_file}")

        # Save vectorizer
        vectorizer_file = self.model_dir / f"{prefix}_vectorizer.pkl"
        joblib.dump(self.vectorizer, vectorizer_file)
        logger.info(f"Saved vectorizer to {vectorizer_file}")

        # Save label encoder
        encoder_file = self.model_dir / f"{prefix}_encoder.pkl"
        joblib.dump(self.label_encoder, encoder_file)
        logger.info(f"Saved label encoder to {encoder_file}")

        # Save agent keywords
        keywords_file = self.model_dir / f"{prefix}_keywords.json"
        with open(keywords_file, "w") as f:
            json.dump(self.agent_keywords, f, indent=2)
        logger.info(f"Saved agent keywords to {keywords_file}")

        # Save metrics
        metrics_file = self.model_dir / f"{prefix}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"Saved metrics to {metrics_file}")

    def load_model(self, prefix: str = "routing_classifier"):
        """
        Load trained model, vectorizer, and label encoder.

        Args:
            prefix: Prefix for saved files
        """
        # Load model
        model_file = self.model_dir / f"{prefix}_model.pkl"
        self.model = joblib.load(model_file)
        logger.info(f"Loaded model from {model_file}")

        # Load vectorizer
        vectorizer_file = self.model_dir / f"{prefix}_vectorizer.pkl"
        self.vectorizer = joblib.load(vectorizer_file)
        logger.info(f"Loaded vectorizer from {vectorizer_file}")

        # Load label encoder
        encoder_file = self.model_dir / f"{prefix}_encoder.pkl"
        self.label_encoder = joblib.load(encoder_file)
        logger.info(f"Loaded label encoder from {encoder_file}")

        # Load agent keywords
        keywords_file = self.model_dir / f"{prefix}_keywords.json"
        with open(keywords_file, "r") as f:
            self.agent_keywords = json.load(f)
        logger.info(f"Loaded agent keywords from {keywords_file}")

        # Load metrics
        metrics_file = self.model_dir / f"{prefix}_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                self.metrics = json.load(f)
            logger.info(f"Loaded metrics from {metrics_file}")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python routing_classifier.py <routing_data.json>")
        sys.exit(1)

    data_file = sys.argv[1]

    # Train classifier
    classifier = RoutingClassifier()
    metrics = classifier.train(data_file)

    # Save model
    classifier.save_model()

    # Test predictions
    test_queries = [
        "Preciso de ajuda com pavimento de rodovia e terraplenagem",
        "Análise de contrato de obra",
        "Barragem com spillway e rejeitos",
        "Estação de metrô com NATM",
        "Orçamento para projeto",
    ]

    print("\n" + "=" * 80)
    print("Testing predictions...")
    print("=" * 80)

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = classifier.predict_with_fallback(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(
                f"  {i}. {result['agent_name']} ({result['agent_slug']}) - "
                f"Confidence: {result['confidence']:.2%}"
            )
