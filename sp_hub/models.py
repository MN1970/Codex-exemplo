"""Dataclasses compartilhados pelo SP Hub."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Priority(str, Enum):
    """Prioridade de um doc detectado, ecoando `sp_agent_feed.priority`."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

    @classmethod
    def coalesce(cls, values: list["Priority"]) -> "Priority":
        """Pega a maior prioridade em uma lista (alta > media > baixa)."""
        order = {cls.ALTA: 3, cls.MEDIA: 2, cls.BAIXA: 1}
        return max(values, key=lambda p: order[p]) if values else cls.MEDIA


@dataclass(frozen=True)
class ChangeEntry:
    """Uma linha de `sp_index` detectada como nova ou modificada."""

    doc_id: str
    doc_path: str
    doc_name: str
    file_ext: str | None
    updated_at: datetime
    drive_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def normalized_ext(self) -> str:
        """Extensão em lower-case sem ponto (ex.: 'pdf')."""
        if not self.file_ext:
            return ""
        return self.file_ext.lstrip(".").lower()


@dataclass(frozen=True)
class RoutingRule:
    """Uma linha de `sp_routing_rules`."""

    id: int
    rule_name: str
    path_pattern: str | None
    file_ext_pattern: str | None
    name_pattern: str | None
    target_agents: list[str]
    doc_type: str
    priority: Priority
    active: bool = True


@dataclass(frozen=True)
class RoutingDecision:
    """Resultado de aplicar todas as rules a um ChangeEntry."""

    doc: ChangeEntry
    target_agents: list[str]
    doc_type: str
    priority: Priority
    matched_rules: list[str]

    @property
    def has_targets(self) -> bool:
        return bool(self.target_agents)


@dataclass(frozen=True)
class FeedEntry:
    """Uma linha pronta para insert em `sp_agent_feed`."""

    agent_code: str
    doc_id: str
    doc_path: str
    doc_name: str
    doc_type: str
    file_ext: str | None
    priority: Priority
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        """Serializa para o formato de insert do supabase-py."""
        return {
            "agent_code": self.agent_code,
            "doc_id": self.doc_id,
            "doc_path": self.doc_path,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "file_ext": self.file_ext,
            "priority": self.priority.value,
            "status": "pending",
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class WriteRequest:
    """Payload de `M20.write(drive, path, content, metadata)`."""

    drive_id: str
    path: str
    content_b64: str
    content_type: str = "application/octet-stream"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Resultado de uma execução de `run_delta_sync`."""

    started_at: datetime
    completed_at: datetime | None = None
    changes_detected: int = 0
    feed_entries_inserted: int = 0
    rag_ingests_triggered: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if self.completed_at is None:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def status(self) -> str:
        if not self.completed_at:
            return "running"
        return "error" if self.errors else "success"

    def summary(self) -> str:
        return (
            f"[{self.status}] Δ={self.changes_detected} "
            f"feed={self.feed_entries_inserted} rag={self.rag_ingests_triggered} "
            f"err={len(self.errors)} in {self.duration_seconds:.2f}s"
        )

    def to_log_row(self) -> dict[str, Any]:
        return {
            "sync_type": "delta",
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": (self.completed_at or datetime.now(timezone.utc)).isoformat(),
            "docs_detected": self.changes_detected,
            "docs_routed": self.feed_entries_inserted,
            "docs_ingested_rag": self.rag_ingests_triggered,
            "errors": self.errors,
        }
