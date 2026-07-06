"""Testes end-to-end do delta_sync com FakeSupabase in-memory."""

from datetime import datetime, timedelta, timezone

import pytest

from sp_hub.delta_sync import run_delta_sync
from sp_hub.models import Priority
from sp_hub.rag_bridge import RagBridge


class _RecordingRag:
    def __init__(self):
        self.calls = []

    def trigger_ingest(self, decision) -> None:
        self.calls.append(decision.doc.doc_id)


@pytest.fixture
def seeded_fake(fake_client, sample_rules):
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    now = datetime.now(timezone.utc)

    fake_client.seed("sp_routing_rules", sample_rules)
    fake_client.seed(
        "sp_sync_log",
        [
            {
                "status": "success",
                "completed_at": (yesterday - timedelta(hours=1)).isoformat(),
                "sync_type": "delta",
            }
        ],
    )
    fake_client.seed(
        "sp_index",
        [
            {
                "doc_id": "doc-contrato",
                "doc_path": "02_CLIENTE/CCR/01_CONTRATO/aditivo_5.pdf",
                "doc_name": "aditivo_5.pdf",
                "file_ext": "pdf",
                "drive_id": "drv-eng",
                "updated_at": now.isoformat(),
                "metadata": {},
            },
            {
                "doc_id": "doc-sicro",
                "doc_path": "03_BIBLIOTECA/composicoes/SICRO_2024.pdf",
                "doc_name": "SICRO_2024_composicoes.pdf",
                "file_ext": "pdf",
                "drive_id": "drv-bib",
                "updated_at": now.isoformat(),
                "metadata": {},
            },
            {
                # antigo — não deve ser detectado
                "doc_id": "doc-old",
                "doc_path": "02_CLIENTE/OEC/04_PROJETO/antigo.dwg",
                "doc_name": "antigo.dwg",
                "file_ext": "dwg",
                "drive_id": "drv-eng",
                "updated_at": (yesterday - timedelta(days=2)).isoformat(),
                "metadata": {},
            },
        ],
    )
    return fake_client


def test_run_delta_sync_only_detects_changes_after_last_sync(seeded_fake):
    rag = _RecordingRag()
    result = run_delta_sync(seeded_fake, rag_bridge=rag)

    assert result.status == "success"
    assert result.changes_detected == 2  # doc-old é ignorado


def test_run_delta_sync_inserts_feed_per_agent(seeded_fake):
    rag = _RecordingRag()
    run_delta_sync(seeded_fake, rag_bridge=rag)

    feed_rows = seeded_fake.tables.get("sp_agent_feed", [])
    agents_per_doc: dict[str, set[str]] = {}
    for row in feed_rows:
        agents_per_doc.setdefault(row["doc_id"], set()).add(row["agent_code"])

    # doc-contrato → M1 + M2 (rule cliente_contrato) + M18 (rule ext_pdf_generico).
    # A união de rules é intencional: PDFs sempre vão para o M18 fazer RAG ingest.
    assert {"M1", "M2"} <= agents_per_doc["doc-contrato"]
    assert "M7" in agents_per_doc["doc-sicro"]


def test_run_delta_sync_triggers_rag_only_for_high_priority(seeded_fake):
    rag = _RecordingRag()
    run_delta_sync(seeded_fake, rag_bridge=rag)

    # doc-contrato (alta) + doc-sicro (alta via name_sicro) → 2 ingests.
    assert set(rag.calls) == {"doc-contrato", "doc-sicro"}


def test_run_delta_sync_writes_sync_log(seeded_fake):
    rag = _RecordingRag()
    run_delta_sync(seeded_fake, rag_bridge=rag)

    logs = [r for r in seeded_fake.tables["sp_sync_log"] if r.get("sync_type") == "delta"]
    latest = max(logs, key=lambda r: r["completed_at"])
    assert latest["status"] == "success"
    assert latest["docs_detected"] == 2


def test_run_delta_sync_first_run_from_epoch(fake_client, sample_rules):
    """Sem histórico em sp_sync_log, delta_sync varre tudo do sp_index."""
    fake_client.seed("sp_routing_rules", sample_rules)
    fake_client.seed(
        "sp_index",
        [
            {
                "doc_id": "d1",
                "doc_path": "02_CLIENTE/X/01_CONTRATO/a.pdf",
                "doc_name": "a.pdf",
                "file_ext": "pdf",
                "updated_at": "2020-01-01T00:00:00+00:00",
                "metadata": {},
            }
        ],
    )
    rag = _RecordingRag()
    result = run_delta_sync(fake_client, rag_bridge=rag)
    assert result.changes_detected == 1


def test_run_delta_sync_idempotent_second_run(seeded_fake):
    """Segundo run sem novas mudanças produz zero novos inserts."""
    run_delta_sync(seeded_fake, rag_bridge=_RecordingRag())
    first_count = len(seeded_fake.tables.get("sp_agent_feed", []))

    # A entrada de log inserida marca "success" com completed_at = agora,
    # então a próxima run só vê docs com updated_at > agora (nenhum).
    result2 = run_delta_sync(seeded_fake, rag_bridge=_RecordingRag())
    assert result2.changes_detected == 0
    assert len(seeded_fake.tables.get("sp_agent_feed", [])) == first_count
