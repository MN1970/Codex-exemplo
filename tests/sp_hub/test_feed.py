"""Testes de feed — explosão de decisão por agente + sanitização R1."""

from datetime import datetime, timezone

from sp_hub.feed import decisions_to_feed
from sp_hub.models import ChangeEntry, Priority, RoutingDecision


def _decision(agents, path="02_CLIENTE/CCR/01_CONTRATO/x.pdf"):
    entry = ChangeEntry(
        doc_id="doc-1",
        doc_path=path,
        doc_name="x.pdf",
        file_ext="pdf",
        updated_at=datetime.now(timezone.utc),
    )
    return RoutingDecision(
        doc=entry,
        target_agents=agents,
        doc_type="contrato",
        priority=Priority.ALTA,
        matched_rules=["cliente_contrato"],
    )


def test_one_decision_becomes_n_feed_entries():
    entries = decisions_to_feed([_decision(["M1", "M2"])])
    assert [e.agent_code for e in entries] == ["M1", "M2"]
    assert all(e.doc_id == "doc-1" for e in entries)


def test_decision_without_targets_dropped():
    entries = decisions_to_feed([_decision([])])
    assert entries == []


def test_r1_sanitizes_cliente_segment():
    entries = decisions_to_feed(
        [_decision(["M1"], path="02_CLIENTE/CCR-Rodovias/01_CONTRATO/x.pdf")]
    )
    assert entries[0].doc_path == "02_CLIENTE/<CLIENTE>/01_CONTRATO/x.pdf"


def test_to_row_matches_supabase_shape():
    entries = decisions_to_feed([_decision(["M1"])])
    row = entries[0].to_row()
    assert row["status"] == "pending"
    assert row["priority"] == "alta"
    assert row["metadata"]["matched_rules"] == ["cliente_contrato"]
