"""
routers/feedback.py — Captura de feedback de uso dos agentes
(thumbs up/down, comentário livre), para loop de melhoria contínua do
Maestro. Persiste em Postgres (tabela `agent_feedback`); se o DB não
estiver disponível, aceita o feedback em memória (fallback dev-only)
em vez de falhar o request.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from pg_pool import acquire_optional

logger = logging.getLogger("manta.feedback")
router = APIRouter(prefix="/feedback", tags=["feedback"])

# Fallback em memória, apenas para o skeleton funcionar sem banco.
_MEMORY_STORE: List["FeedbackRecord"] = []


class FeedbackIn(BaseModel):
    agent_code: str
    rating: int = Field(..., ge=-1, le=1, description="-1 = ruim, 0 = neutro, 1 = bom")
    comment: Optional[str] = None
    user_email: Optional[str] = None


class FeedbackRecord(FeedbackIn):
    id: str
    created_at: datetime


@router.post("", response_model=FeedbackRecord, summary="Registra feedback sobre um agente")
async def submit_feedback(payload: FeedbackIn, request: Request) -> FeedbackRecord:
    record = FeedbackRecord(
        id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )

    async with acquire_optional(request) as conn:
        if conn is not None:
            await conn.execute(
                """
                INSERT INTO agent_feedback (id, agent_code, rating, comment, user_email, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                record.id, record.agent_code, record.rating,
                record.comment, record.user_email, record.created_at,
            )
        else:
            logger.info("feedback: DB indisponível, guardando em memória (%s)", record.id)
            _MEMORY_STORE.append(record)

    return record


@router.get("", response_model=List[FeedbackRecord], summary="Lista feedback recente (fallback em memória)")
async def list_feedback(limit: int = 50) -> List[FeedbackRecord]:
    return _MEMORY_STORE[-limit:]
