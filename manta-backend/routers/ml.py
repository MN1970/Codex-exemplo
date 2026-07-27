"""
routers/ml.py — Fine-tuning LoRA por segmento (Manta 03-S6..S10:
saneamento, energia, portos, aeroportos, barragens).

POST /ml/finetune {segment, epochs} dispara a pipeline de
ml/finetuning.py (load_base_model/prepare_dataset/create_trainer/
train/save_adapter) em background e devolve IMEDIATAMENTE o job criado
com status="queued" (202 Accepted) — o treino em si (transformers/peft/
torch) é bloqueante e pode levar minutos/horas com um modelo real, então
roda numa thread separada (`asyncio.to_thread`) para não travar o event
loop do FastAPI nem os demais requests.

GET /ml/finetune/{job_id} consulta o progresso (queued -> running ->
completed|failed) e GET /ml/finetune lista o histórico de jobs.

Persistência: usa `database.py` (SQLAlchemy async — a base "para
qualquer serviço novo", ver docstring de database.py) contra a tabela
`fine_tune_jobs` (migration 0005_finetune_jobs). Se o Postgres não
estiver acessível, degrada para um fallback em memória — mesmo padrão
já usado por routers/feedback.py e routers/executor.py — em vez de
falhar o request.
"""
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

import database
from ml.finetuning import DEFAULT_BASE_MODEL, SUPPORTED_SEGMENTS, run_finetuning_pipeline

logger = logging.getLogger("manta.ml.router")
router = APIRouter(prefix="/ml", tags=["ml"])

# Fallback em memória (não sobrevive a restart) — usado só quando
# database.SessionLocal não consegue falar com o Postgres.
_MEMORY_JOBS: Dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class FineTuneRequest(BaseModel):
    """Payload de POST /ml/finetune. `segment` e `epochs` são os dois
    campos pedidos pelo contrato do endpoint; os demais têm defaults
    sensatos e existem para permitir override sem quebrar o contrato
    mínimo `{segment, epochs}`."""

    segment: str = Field(..., description=f"Um de {SUPPORTED_SEGMENTS}")
    epochs: int = Field(3, ge=1, le=50, description="Sobrescreve num_epochs de fine_tune_config.yaml")
    base_model: Optional[str] = Field(
        None, description=f"Default: {DEFAULT_BASE_MODEL} (ou o `base_model` do segmento em fine_tune_config.yaml)"
    )
    use_quantization: bool = Field(
        True, description="4-bit QLoRA — requer GPU+bitsandbytes; ignorado quando demo_mode=True"
    )
    demo_mode: bool = Field(
        False,
        description=(
            "Roda a pipeline com um GPT-2 minúsculo construído offline (sem GPU/rede) "
            "em vez do Mistral-7B real — só para smoke test/CI, nunca produção "
            "(ver ml/finetuning.py::build_demo_base_model_and_tokenizer)."
        ),
    )
    org_id: Optional[str] = Field(None, description="Organização dona do job (opcional — catálogo global se omitido)")


class FineTuneJobOut(BaseModel):
    id: str
    org_id: Optional[str] = None
    segment: str
    base_model: str
    epochs: int
    status: str  # queued|running|completed|failed
    adapter_name: Optional[str] = None
    adapter_path: Optional[str] = None
    loss: Optional[float] = None
    perplexity: Optional[float] = None
    num_train_steps: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Persistência (Postgres via database.py, com fallback em memória)
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _create_job_record(job_id: str, payload: FineTuneRequest) -> dict:
    base_model = payload.base_model or DEFAULT_BASE_MODEL
    record = {
        "id": job_id,
        "org_id": payload.org_id,
        "segment": payload.segment,
        "base_model": base_model,
        "epochs": payload.epochs,
        "status": "queued",
        "adapter_name": None,
        "adapter_path": None,
        "loss": None,
        "perplexity": None,
        "num_train_steps": None,
        "error_message": None,
        "created_at": _now_iso(),
        "started_at": None,
        "completed_at": None,
    }
    try:
        async with database.SessionLocal() as session:
            job = database.FineTuneJob(
                id=job_id,
                org_id=payload.org_id,
                segment=payload.segment,
                base_model=base_model,
                epochs=payload.epochs,
                status="queued",
            )
            session.add(job)
            await session.commit()
    except Exception as e:  # noqa: BLE001 - degrade, não derrubar o request
        logger.warning("ml.finetune: DB indisponível ao criar job %s (%s) — usando fallback em memória", job_id, e)
        _MEMORY_JOBS[job_id] = record
    return record


async def _update_job(job_id: str, **fields) -> None:
    persisted = False
    try:
        async with database.SessionLocal() as session:
            job = await session.get(database.FineTuneJob, job_id)
            if job is not None:
                for key, value in fields.items():
                    setattr(job, key, value)
                await session.commit()
                persisted = True
    except Exception as e:  # noqa: BLE001 - degrade, não derrubar o job em background
        logger.warning("ml.finetune: DB indisponível ao atualizar job %s (%s)", job_id, e)

    if not persisted and job_id in _MEMORY_JOBS:
        for key, value in fields.items():
            _MEMORY_JOBS[job_id][key] = value.isoformat() if isinstance(value, datetime) else value


async def _get_job(job_id: str) -> Optional[dict]:
    try:
        async with database.SessionLocal() as session:
            job = await session.get(database.FineTuneJob, job_id)
            if job is not None:
                return job.to_dict()
    except Exception as e:  # noqa: BLE001
        logger.warning("ml.finetune: DB indisponível ao ler job %s (%s)", job_id, e)
    return _MEMORY_JOBS.get(job_id)


async def _list_jobs(segment: Optional[str], limit: int) -> List[dict]:
    try:
        async with database.SessionLocal() as session:
            stmt = select(database.FineTuneJob).order_by(database.FineTuneJob.created_at.desc()).limit(limit)
            if segment:
                stmt = stmt.where(database.FineTuneJob.segment == segment)
            rows = (await session.execute(stmt)).scalars().all()
            return [r.to_dict() for r in rows]
    except Exception as e:  # noqa: BLE001
        logger.warning("ml.finetune: DB indisponível ao listar jobs (%s)", e)

    jobs = list(_MEMORY_JOBS.values())
    if segment:
        jobs = [j for j in jobs if j["segment"] == segment]
    return sorted(jobs, key=lambda j: j["created_at"], reverse=True)[:limit]


# ---------------------------------------------------------------------------
# Job em background
# ---------------------------------------------------------------------------


async def _run_finetune_job(job_id: str, payload: FineTuneRequest) -> None:
    """Corpo do job assíncrono: roda `run_finetuning_pipeline()` (
    bloqueante — transformers/peft/torch) numa thread separada via
    `asyncio.to_thread`, para não travar o event loop nem os outros
    requests da API enquanto o treino roda, e reflete status/métricas
    de volta no registro do job conforme progride."""
    await _update_job(job_id, status="running", started_at=datetime.now(timezone.utc))
    try:
        result = await asyncio.to_thread(
            run_finetuning_pipeline,
            segment=payload.segment,
            epochs=payload.epochs,
            base_model_name=payload.base_model,
            use_quantization=payload.use_quantization,
            demo_mode=payload.demo_mode,
        )
        await _update_job(
            job_id,
            status="completed",
            base_model=result.base_model,
            adapter_name=Path(result.adapter_path).name,
            adapter_path=result.adapter_path,
            loss=result.metrics.loss,
            perplexity=result.metrics.perplexity,
            num_train_steps=result.metrics.num_train_steps,
            completed_at=datetime.now(timezone.utc),
        )
        logger.info("ml.finetune: job %s concluído — adapter em %s", job_id, result.adapter_path)
    except Exception as e:  # noqa: BLE001 - job em background: falha vira status="failed", nunca uma exceção solta
        logger.error("ml.finetune: job %s falhou: %s", job_id, e, exc_info=True)
        await _update_job(job_id, status="failed", error_message=str(e), completed_at=datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/finetune",
    response_model=FineTuneJobOut,
    status_code=202,
    summary="Dispara fine-tuning LoRA assíncrono para um segmento",
    description=(
        "Cria um job de fine-tuning (status=queued) e dispara o treino em "
        "background — o request volta imediatamente, sem esperar o treino "
        "terminar. Consulte o progresso em GET /ml/finetune/{job_id}."
    ),
)
async def create_finetune_job(payload: FineTuneRequest) -> FineTuneJobOut:
    if payload.segment not in SUPPORTED_SEGMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Segmento desconhecido: {payload.segment!r}. Use um de {SUPPORTED_SEGMENTS}",
        )

    job_id = str(uuid4())
    record = await _create_job_record(job_id, payload)

    # Dispara o job e não espera (fire-and-forget) — a referência da
    # task é mantida em app.state pelo lifespan? Não: BackgroundTasks do
    # FastAPI seria cancelada se o worker reciclar a conexão; usamos
    # asyncio.create_task diretamente (sobrevive ao fim do request,
    # mesma vida do event loop do processo) e o resultado só é lido de
    # volta via _get_job()/_list_jobs(), nunca aguardado aqui.
    asyncio.create_task(_run_finetune_job(job_id, payload))

    logger.info(
        "ml.finetune: job %s criado (segment=%s, epochs=%d, demo_mode=%s)",
        job_id, payload.segment, payload.epochs, payload.demo_mode,
    )
    return FineTuneJobOut(**record)


@router.get("/finetune/{job_id}", response_model=FineTuneJobOut, summary="Status de um job de fine-tuning")
async def get_finetune_job(job_id: str) -> FineTuneJobOut:
    record = await _get_job(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")
    return FineTuneJobOut(**record)


@router.get("/finetune", response_model=List[FineTuneJobOut], summary="Lista jobs de fine-tuning")
async def list_finetune_jobs(segment: Optional[str] = None, limit: int = 20) -> List[FineTuneJobOut]:
    records = await _list_jobs(segment, limit)
    return [FineTuneJobOut(**r) for r in records]
