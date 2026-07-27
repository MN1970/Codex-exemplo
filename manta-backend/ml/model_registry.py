"""
Model Registry for tracking fine-tuned LoRA adapters.

SQLAlchemy ORM for storing adapter metadata, training history, and S3 locations.
Provides methods for version control, adapter loading, and segment-specific queries.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class MLModelVersion(Base):
    """
    ORM model for tracking fine-tuned model adapters.
    """
    __tablename__ = "ml_model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String(50), nullable=False, index=True)
    base_model = Column(String(255), nullable=False)
    adapter_name = Column(String(255), nullable=False, unique=True)
    adapter_path = Column(String(512), nullable=False)
    accuracy = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    perplexity = Column(Float, nullable=True)
    num_training_steps = Column(Integer, nullable=True)
    learning_rate = Column(Float, nullable=True)
    trained_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    s3_location = Column(String(512), nullable=True)
    tags = Column(Text, nullable=True)  # JSON-serialized tags
    notes = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "segment": self.segment,
            "base_model": self.base_model,
            "adapter_name": self.adapter_name,
            "adapter_path": self.adapter_path,
            "accuracy": self.accuracy,
            "loss": self.loss,
            "perplexity": self.perplexity,
            "num_training_steps": self.num_training_steps,
            "learning_rate": self.learning_rate,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "s3_location": self.s3_location,
            "tags": self.tags,
            "notes": self.notes,
        }


class AdapterStorage(ABC):
    """Abstract base class for adapter storage backends."""

    @abstractmethod
    def save(self, local_path: str, adapter_name: str) -> str:
        """Save adapter and return storage location."""
        pass

    @abstractmethod
    def load(self, location: str, local_path: str) -> None:
        """Load adapter from storage."""
        pass

    @abstractmethod
    def delete(self, location: str) -> None:
        """Delete adapter from storage."""
        pass


class LocalAdapterStorage(AdapterStorage):
    """Local filesystem storage for adapters."""

    def __init__(self, base_dir: str = "./lora_adapters"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalAdapterStorage initialized at: {self.base_dir}")

    def save(self, local_path: str, adapter_name: str) -> str:
        """
        Save adapter locally.

        Args:
            local_path: Source path of the adapter
            adapter_name: Name of the adapter

        Returns:
            Storage location (local path)
        """
        source = Path(local_path)
        dest = self.base_dir / adapter_name

        if not source.exists():
            raise FileNotFoundError(f"Source path not found: {local_path}")

        # Copy adapter
        import shutil
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest)

        logger.info(f"Adapter saved to: {dest}")
        return str(dest)

    def load(self, location: str, local_path: str) -> None:
        """
        Load adapter from local storage.

        Args:
            location: Storage location (local path)
            local_path: Destination path
        """
        source = Path(location)
        dest = Path(local_path)

        if not source.exists():
            raise FileNotFoundError(f"Location not found: {location}")

        import shutil
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest)

        logger.info(f"Adapter loaded from: {location}")

    def delete(self, location: str) -> None:
        """Delete adapter from local storage."""
        import shutil
        path = Path(location)
        if path.exists():
            shutil.rmtree(path)
            logger.info(f"Adapter deleted: {location}")


class S3AdapterStorage(AdapterStorage):
    """AWS S3 storage for adapters."""

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        try:
            import boto3
            self.s3_client = boto3.client("s3", region_name=region)
            self.bucket_name = bucket_name
            logger.info(f"S3AdapterStorage initialized for bucket: {bucket_name}")
        except ImportError:
            raise ImportError("boto3 required for S3 storage. Install: pip install boto3")

    def save(self, local_path: str, adapter_name: str) -> str:
        """Save adapter to S3."""
        import os

        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Source path not found: {local_path}")

        s3_prefix = f"adapters/{adapter_name}"

        # Upload all files in adapter directory
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(local_path)
                s3_key = f"{s3_prefix}/{relative_path}"

                self.s3_client.upload_file(
                    str(file_path),
                    self.bucket_name,
                    s3_key,
                )
                logger.info(f"Uploaded {s3_key} to S3")

        s3_location = f"s3://{self.bucket_name}/{s3_prefix}"
        logger.info(f"Adapter saved to S3: {s3_location}")
        return s3_location

    def load(self, location: str, local_path: str) -> None:
        """Load adapter from S3."""
        import os

        dest = Path(local_path)
        dest.mkdir(parents=True, exist_ok=True)

        # Parse S3 location
        if location.startswith("s3://"):
            parts = location.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ""
        else:
            bucket = self.bucket_name
            prefix = location

        # List and download objects
        response = self.s3_client.list_objects_v2(
            Bucket=bucket, Prefix=prefix
        )

        if "Contents" not in response:
            raise FileNotFoundError(f"No objects found at: {location}")

        for obj in response["Contents"]:
            key = obj["Key"]
            relative_key = key[len(prefix):].lstrip("/")
            local_file = dest / relative_key

            local_file.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(bucket, key, str(local_file))
            logger.info(f"Downloaded {key} from S3")

    def delete(self, location: str) -> None:
        """Delete adapter from S3."""
        # Parse S3 location
        if location.startswith("s3://"):
            parts = location.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ""
        else:
            bucket = self.bucket_name
            prefix = location

        # List and delete objects
        response = self.s3_client.list_objects_v2(
            Bucket=bucket, Prefix=prefix
        )

        if "Contents" in response:
            for obj in response["Contents"]:
                self.s3_client.delete_object(Bucket=bucket, Key=obj["Key"])
                logger.info(f"Deleted {obj['Key']} from S3")


class ModelRegistry:
    """
    Registry for managing fine-tuned model adapters.
    """

    def __init__(
        self,
        db_url: str = "sqlite:///./manta_ml_registry.db",
        storage: Optional[AdapterStorage] = None,
    ):
        """
        Initialize model registry.

        Args:
            db_url: Database URL (SQLAlchemy format)
            storage: AdapterStorage backend (defaults to LocalAdapterStorage)
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        self.storage = storage or LocalAdapterStorage()
        logger.info(f"ModelRegistry initialized with DB: {db_url}")

    def _get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def save_adapter(
        self,
        segment: str,
        base_model: str,
        adapter_name: str,
        local_path: str,
        accuracy: Optional[float] = None,
        loss: Optional[float] = None,
        perplexity: Optional[float] = None,
        num_training_steps: Optional[int] = None,
        learning_rate: Optional[float] = None,
        tags: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> MLModelVersion:
        """
        Save adapter metadata and copy to storage.

        Args:
            segment: Domain segment (saneamento, energia, etc)
            base_model: Base model name (e.g., mistralai/Mistral-7B-v0.1)
            adapter_name: Unique adapter identifier
            local_path: Local path to adapter directory
            accuracy: Optional accuracy metric
            loss: Training loss
            perplexity: Perplexity metric
            num_training_steps: Number of training steps
            learning_rate: Learning rate used
            tags: JSON-serialized tags
            notes: Additional notes

        Returns:
            MLModelVersion object
        """
        session = self._get_session()

        try:
            # Save to storage
            storage_location = self.storage.save(local_path, adapter_name)

            # Create registry entry
            model_version = MLModelVersion(
                segment=segment,
                base_model=base_model,
                adapter_name=adapter_name,
                adapter_path=storage_location,
                accuracy=accuracy,
                loss=loss,
                perplexity=perplexity,
                num_training_steps=num_training_steps,
                learning_rate=learning_rate,
                s3_location=storage_location if storage_location.startswith("s3://") else None,
                tags=tags,
                notes=notes,
            )

            session.add(model_version)
            session.commit()

            logger.info(
                f"Adapter saved: segment={segment}, "
                f"adapter_name={adapter_name}, location={storage_location}"
            )

            return model_version

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving adapter: {e}")
            raise
        finally:
            session.close()

    def load_adapter(
        self,
        adapter_name: str,
        local_path: str,
    ) -> None:
        """
        Load adapter from registry to local path.

        Args:
            adapter_name: Adapter identifier
            local_path: Destination local path
        """
        session = self._get_session()

        try:
            model_version = session.query(MLModelVersion).filter_by(
                adapter_name=adapter_name
            ).first()

            if not model_version:
                raise ValueError(f"Adapter not found: {adapter_name}")

            self.storage.load(model_version.adapter_path, local_path)
            logger.info(f"Adapter loaded: {adapter_name} -> {local_path}")

        finally:
            session.close()

    def get_adapter(self, adapter_name: str) -> Optional[MLModelVersion]:
        """
        Get adapter metadata.

        Args:
            adapter_name: Adapter identifier

        Returns:
            MLModelVersion or None
        """
        session = self._get_session()

        try:
            model_version = session.query(MLModelVersion).filter_by(
                adapter_name=adapter_name
            ).first()
            return model_version
        finally:
            session.close()

    def list_versions(
        self,
        segment: Optional[str] = None,
        base_model: Optional[str] = None,
        limit: int = 100,
    ) -> List[MLModelVersion]:
        """
        List adapter versions.

        Args:
            segment: Filter by segment
            base_model: Filter by base model
            limit: Maximum results

        Returns:
            List of MLModelVersion objects
        """
        session = self._get_session()

        try:
            query = session.query(MLModelVersion)

            if segment:
                query = query.filter_by(segment=segment)
            if base_model:
                query = query.filter_by(base_model=base_model)

            versions = query.order_by(
                MLModelVersion.trained_at.desc()
            ).limit(limit).all()

            return versions

        finally:
            session.close()

    def get_best_adapter(
        self,
        segment: str,
        metric: str = "accuracy",
    ) -> Optional[MLModelVersion]:
        """
        Get best performing adapter for a segment.

        Args:
            segment: Domain segment
            metric: Metric to sort by (accuracy, perplexity, loss)

        Returns:
            MLModelVersion or None
        """
        session = self._get_session()

        try:
            query = session.query(MLModelVersion).filter_by(segment=segment)

            if metric == "accuracy":
                query = query.order_by(MLModelVersion.accuracy.desc())
            elif metric == "perplexity":
                query = query.order_by(MLModelVersion.perplexity.asc())
            elif metric == "loss":
                query = query.order_by(MLModelVersion.loss.asc())

            best = query.first()
            return best

        finally:
            session.close()

    def delete_adapter(self, adapter_name: str) -> bool:
        """
        Delete adapter from registry and storage.

        Args:
            adapter_name: Adapter identifier

        Returns:
            True if deleted, False if not found
        """
        session = self._get_session()

        try:
            model_version = session.query(MLModelVersion).filter_by(
                adapter_name=adapter_name
            ).first()

            if not model_version:
                return False

            # Delete from storage
            self.storage.delete(model_version.adapter_path)

            # Delete from registry
            session.delete(model_version)
            session.commit()

            logger.info(f"Adapter deleted: {adapter_name}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting adapter: {e}")
            raise
        finally:
            session.close()

    def export_metrics(
        self,
        segment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Export adapter metrics as dictionaries.

        Args:
            segment: Optional segment filter

        Returns:
            List of adapter metadata dictionaries
        """
        versions = self.list_versions(segment=segment, limit=1000)
        return [v.to_dict() for v in versions]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example usage
    registry = ModelRegistry()

    # List all versions
    versions = registry.list_versions()
    for v in versions:
        print(v.to_dict())

    # Get best adapter for saneamento
    best = registry.get_best_adapter("saneamento", metric="accuracy")
    if best:
        print(f"Best adapter: {best.adapter_name}")
