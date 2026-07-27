"""
Fine-Tuning LoRA Job Manager for Manta vertical agents.

Exposes a FineTuneJobManager class that wraps ml/finetuning.py::run_finetuning_pipeline
and coordinates with database.py::FineTuneJob for state management, metrics tracking,
and persistent logging.

Segmentos suportados (Manta 03-S6..S10):
  - saneamento: ETA, ETE, adutora, SNIS, Lei 14.026, AySA priority
  - energia: transmissão, subestação, ANEEL, RAP, leilão
  - portos: ANTAQ, dragagem, terminal, berço
  - aeroportos: ANAC, pista, TPS, balizamento
  - barragens: CFRD, CCR, rejeitos, PNSB, CBDB

Usage (CLI):
    python -m manta_backend.tasks.finetune_job \\
        --segment saneamento \\
        --epochs 3 \\
        --lr 1e-4 \\
        --job-dir ./fine_tune_jobs

Usage (programmatic):
    manager = FineTuneJobManager(segment="saneamento", epochs=3)
    result = manager.run()
    print(result.metrics)

Estado da máquina:
    CREATED -> QUEUED -> RUNNING -> (COMPLETED | FAILED)

Cada transição persiste em fine_tune_jobs/saneamento_{timestamp}.json
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import yaml

logger = logging.getLogger("manta.tasks.finetune_job")

# Paths
TASK_DIR = Path(__file__).parent
BACKEND_DIR = TASK_DIR.parent
ML_DIR = BACKEND_DIR / "ml"
DATA_DIR = BACKEND_DIR / "data"
JOBS_DIR = BACKEND_DIR / "fine_tune_jobs"

# Ensure job output directory exists
JOBS_DIR.mkdir(exist_ok=True, parents=True)

# Add backend to path for imports
sys.path.insert(0, str(BACKEND_DIR))


class JobStatus(str, Enum):
    """Estados do job de fine-tuning."""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobEvent(str, Enum):
    """Eventos que ocorrem durante a execução do job."""
    STARTED = "started"
    TRAINING = "training"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FineTuneJobMetrics:
    """Métricas coletadas ao final do treino."""
    segment: str
    base_model: str
    loss: float
    perplexity: float
    epoch: float
    num_train_steps: int
    learning_rate: float
    total_time_seconds: float
    adapter_path: Optional[str] = None
    adapter_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FineTuneJobResult:
    """Resultado completo da execução do job."""
    job_id: str
    segment: str
    status: JobStatus
    metrics: Optional[FineTuneJobMetrics] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    output_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "segment": self.segment,
            "status": self.status.value,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "output_dir": self.output_dir,
        }


class FineTuneJobManager:
    """Gerenciador de jobs de fine-tuning com persistência e monitoramento."""

    def __init__(
        self,
        segment: str,
        epochs: int = 3,
        learning_rate: Optional[float] = None,
        base_model: Optional[str] = None,
        use_quantization: bool = True,
        demo_mode: bool = False,
        job_id: Optional[str] = None,
        job_dir: Optional[Path] = None,
    ):
        """
        Initialize job manager.

        Args:
            segment: um de (saneamento|energia|portos|aeroportos|barragens)
            epochs: número de épocas de treino
            learning_rate: learning rate (usa config YAML se None)
            base_model: nome do modelo base (usa default se None)
            use_quantization: usar 4-bit QLoRA
            demo_mode: rodar com GPT-2 offline (teste/CI)
            job_id: ID do job (gera novo se None)
            job_dir: diretório para persistência (default JOBS_DIR)
        """
        self.job_id = job_id or str(uuid4())
        self.segment = segment
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.base_model = base_model
        self.use_quantization = use_quantization
        self.demo_mode = demo_mode

        self.job_dir = Path(job_dir or JOBS_DIR)
        self.job_dir.mkdir(exist_ok=True, parents=True)

        self.status = JobStatus.CREATED
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.events: List[Dict[str, Any]] = []
        self.metrics: Optional[FineTuneJobMetrics] = None
        self.error_message: Optional[str] = None

        logger.info(
            "FineTuneJobManager initialized: job_id=%s, segment=%s, epochs=%d, demo_mode=%s",
            self.job_id,
            self.segment,
            self.epochs,
            self.demo_mode,
        )

    def _log_event(self, event: JobEvent, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra um evento do job."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event.value,
            "status": self.status.value,
            "details": details or {},
        }
        self.events.append(record)
        logger.info("Job event: %s (%s)", event.value, self.status.value)

    def _update_status(self, status: JobStatus) -> None:
        """Atualiza o status do job."""
        old_status = self.status
        self.status = status
        logger.info("Job status changed: %s -> %s", old_status.value, status.value)

    def _persist_state(self) -> str:
        """Persiste o estado atual do job em JSON."""
        state = {
            "job_id": self.job_id,
            "segment": self.segment,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "base_model": self.base_model,
            "use_quantization": self.use_quantization,
            "demo_mode": self.demo_mode,
            "events": self.events,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "error_message": self.error_message,
        }

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{self.segment}_{self.job_id}_{timestamp}.json"
        filepath = self.job_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        logger.info("Job state persisted: %s", filepath)
        return str(filepath)

    def run(self) -> FineTuneJobResult:
        """
        Executa o pipeline de fine-tuning de ponta a ponta.

        Returns:
            FineTuneJobResult com status, métricas e caminho do adapter
        """
        self._update_status(JobStatus.QUEUED)
        self._log_event(JobEvent.STARTED)
        self._persist_state()

        start_time = time.time()

        try:
            self._log_event(JobEvent.TRAINING, {"segment": self.segment, "epochs": self.epochs})
            self._update_status(JobStatus.RUNNING)
            self._persist_state()

            # Importa e chama a pipeline de fine-tuning
            from ml.finetuning import run_finetuning_pipeline

            logger.info(
                "Starting fine-tuning pipeline: segment=%s, epochs=%d, demo_mode=%s",
                self.segment,
                self.epochs,
                self.demo_mode,
            )

            finetuning_result = run_finetuning_pipeline(
                segment=self.segment,
                epochs=self.epochs,
                base_model_name=self.base_model,
                use_quantization=self.use_quantization,
                demo_mode=self.demo_mode,
            )

            # Extrai métricas do resultado
            self.metrics = FineTuneJobMetrics(
                segment=self.segment,
                base_model=finetuning_result.base_model,
                loss=finetuning_result.metrics.loss,
                perplexity=finetuning_result.metrics.perplexity,
                epoch=finetuning_result.metrics.epoch,
                num_train_steps=finetuning_result.metrics.num_train_steps,
                learning_rate=finetuning_result.metrics.learning_rate,
                total_time_seconds=finetuning_result.metrics.total_time_seconds,
                adapter_path=finetuning_result.adapter_path,
                adapter_name=Path(finetuning_result.adapter_path).name if finetuning_result.adapter_path else None,
            )

            elapsed_seconds = time.time() - start_time

            self._log_event(JobEvent.SAVING, {"adapter_path": finetuning_result.adapter_path})
            self._update_status(JobStatus.COMPLETED)
            self.completed_at = datetime.now(timezone.utc).isoformat()

            logger.info(
                "Fine-tuning completed successfully: loss=%.4f, perplexity=%.4f, time=%.1fs",
                self.metrics.loss,
                self.metrics.perplexity,
                elapsed_seconds,
            )

            self._log_event(JobEvent.COMPLETED, self.metrics.to_dict())
            self._persist_state()

            return FineTuneJobResult(
                job_id=self.job_id,
                segment=self.segment,
                status=self.status,
                metrics=self.metrics,
                created_at=self.created_at,
                completed_at=self.completed_at,
                output_dir=str(self.job_dir),
            )

        except Exception as e:
            elapsed_seconds = time.time() - start_time
            self.error_message = str(e)
            self._log_event(JobEvent.FAILED, {"error": str(e), "elapsed_seconds": elapsed_seconds})
            self._update_status(JobStatus.FAILED)
            self.completed_at = datetime.now(timezone.utc).isoformat()

            logger.error(
                "Fine-tuning failed after %.1fs: %s",
                elapsed_seconds,
                e,
                exc_info=True,
            )
            self._persist_state()

            return FineTuneJobResult(
                job_id=self.job_id,
                segment=self.segment,
                status=self.status,
                error_message=self.error_message,
                created_at=self.created_at,
                completed_at=self.completed_at,
                output_dir=str(self.job_dir),
            )

    async def run_async(self) -> FineTuneJobResult:
        """Versão assíncrona do run() para integração com FastAPI."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run)

    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Carrega estado de um arquivo JSON persisted."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


def main():
    """Entry point CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fine-tuning LoRA manager for Manta vertical agents"
    )
    parser.add_argument(
        "--segment",
        type=str,
        required=True,
        choices=["saneamento", "energia", "portos", "aeroportos", "barragens"],
        help="Vertical segment for fine-tuning",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=None,
        help="Learning rate (uses config YAML if not specified)",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default=None,
        help="Base model name (uses config if not specified)",
    )
    parser.add_argument(
        "--no-quantization",
        action="store_true",
        help="Disable 4-bit QLoRA (default: enabled)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with offline GPT-2 (for testing without GPU)",
    )
    parser.add_argument(
        "--job-dir",
        type=str,
        default=None,
        help="Directory for job persistence (default: ./fine_tune_jobs)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 80)
    logger.info("Manta Fine-Tuning Job Manager")
    logger.info("=" * 80)
    logger.info(f"Segment:       {args.segment}")
    logger.info(f"Epochs:        {args.epochs}")
    logger.info(f"LR:            {args.lr}")
    logger.info(f"Base model:    {args.base_model or '(from config)'}")
    logger.info(f"Quantization:  {'disabled' if args.no_quantization else 'enabled'}")
    logger.info(f"Demo mode:     {args.demo}")
    logger.info(f"Job dir:       {args.job_dir or '(default)'}")
    logger.info("=" * 80)

    try:
        manager = FineTuneJobManager(
            segment=args.segment,
            epochs=args.epochs,
            learning_rate=args.lr,
            base_model=args.base_model,
            use_quantization=not args.no_quantization,
            demo_mode=args.demo,
            job_dir=Path(args.job_dir) if args.job_dir else None,
        )

        result = manager.run()

        logger.info("=" * 80)
        logger.info("Job Summary")
        logger.info("=" * 80)
        logger.info(f"Job ID:        {result.job_id}")
        logger.info(f"Status:        {result.status.value}")
        logger.info(f"Created:       {result.created_at}")
        logger.info(f"Completed:     {result.completed_at}")

        if result.metrics:
            logger.info("=" * 80)
            logger.info("Metrics")
            logger.info("=" * 80)
            logger.info(f"Loss:          {result.metrics.loss:.6f}")
            logger.info(f"Perplexity:    {result.metrics.perplexity:.4f}")
            logger.info(f"Train steps:   {result.metrics.num_train_steps}")
            logger.info(f"Total time:    {result.metrics.total_time_seconds:.1f}s")
            logger.info(f"Adapter:       {result.metrics.adapter_path}")

        if result.error_message:
            logger.error(f"Error: {result.error_message}")
            return 1

        logger.info("=" * 80)
        logger.info("Job completed successfully")
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
