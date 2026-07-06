"""Testes do router — matching de path/ext/name + união de agentes + prioridade."""

from datetime import datetime, timezone

from sp_hub.models import ChangeEntry, Priority
from sp_hub.router import parse_rules, route


def _entry(**overrides) -> ChangeEntry:
    defaults = dict(
        doc_id="doc-1",
        doc_path="02_CLIENTE/CCR/04_PROJETO/geo.dwg",
        doc_name="geo.dwg",
        file_ext="dwg",
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return ChangeEntry(**defaults)


def test_folder_rule_matches(sample_rules):
    rules = parse_rules(sample_rules)
    entry = _entry(
        doc_path="02_CLIENTE/CCR/01_CONTRATO/contrato_v3.pdf",
        doc_name="contrato_v3.pdf",
        file_ext="pdf",
    )
    decision = route(entry, rules)
    assert "cliente_contrato" in decision.matched_rules
    assert set(decision.target_agents) >= {"M1", "M2"}
    assert decision.priority == Priority.ALTA


def test_multiple_rules_union_agents_and_max_priority(sample_rules):
    """DWG dentro de 04_PROJETO casa tanto cliente_projeto quanto ext_dwg_dxf."""
    rules = parse_rules(sample_rules)
    entry = _entry()  # 04_PROJETO/geo.dwg
    decision = route(entry, rules)
    assert {"cliente_projeto", "ext_dwg_dxf"} <= set(decision.matched_rules)
    assert set(decision.target_agents) == {"M3", "M4"}
    assert decision.priority == Priority.ALTA


def test_name_regex_matches_case_insensitive(sample_rules):
    rules = parse_rules(sample_rules)
    entry = _entry(
        doc_path="03_BIBLIOTECA/composicoes/SICRO_2024.pdf",
        doc_name="Sicro_2024_composicoes.pdf",
        file_ext="pdf",
    )
    decision = route(entry, rules)
    assert "name_sicro" in decision.matched_rules
    assert "M7" in decision.target_agents


def test_no_match_falls_back_to_classifier(sample_rules):
    rules = parse_rules(sample_rules)
    entry = _entry(
        doc_path="05_INTERNO/misc/leia_me.txt",
        doc_name="leia_me.txt",
        file_ext="txt",
    )
    decision = route(entry, rules)
    assert decision.matched_rules == []
    assert decision.target_agents == []
    assert decision.doc_type == "outros"
    assert decision.priority == Priority.MEDIA


def test_inactive_rule_ignored(sample_rules):
    sample_rules[0]["active"] = False  # cliente_contrato desligada
    rules = parse_rules(sample_rules)
    entry = _entry(
        doc_path="02_CLIENTE/CCR/01_CONTRATO/contrato_v3.pdf",
        doc_name="contrato_v3.pdf",
        file_ext="pdf",
    )
    decision = route(entry, rules)
    assert "cliente_contrato" not in decision.matched_rules


def test_ext_pattern_csv_list(sample_rules):
    rules = parse_rules(sample_rules)
    entry_dxf = _entry(
        doc_path="qualquer/lugar/plano.dxf", doc_name="plano.dxf", file_ext="dxf"
    )
    decision = route(entry_dxf, rules)
    assert "ext_dwg_dxf" in decision.matched_rules


def test_priority_coalesce_picks_higher():
    # Alta + Baixa deve resultar em Alta.
    assert Priority.coalesce([Priority.BAIXA, Priority.ALTA, Priority.MEDIA]) == Priority.ALTA


def test_glob_matches_star():
    """`*` casa qualquer coisa exceto `/`."""
    from sp_hub.router import _glob_match

    assert _glob_match("02_CLIENTE/*/01_CONTRATO/*", "02_CLIENTE/CCR/01_CONTRATO/x.pdf")
    assert not _glob_match(
        "02_CLIENTE/*/01_CONTRATO/*", "02_CLIENTE/CCR/subpasta/01_CONTRATO/x.pdf"
    )


def test_glob_double_star():
    """`**` casa qualquer coisa inclusive `/`."""
    from sp_hub.router import _glob_match

    assert _glob_match("02_CLIENTE/**/01_CONTRATO/*", "02_CLIENTE/CCR/sub/01_CONTRATO/x.pdf")
