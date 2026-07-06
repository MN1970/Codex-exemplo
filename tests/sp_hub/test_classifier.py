"""Testes de classifier — precedência name > ext > folder > fallback."""

from sp_hub.classifier import classify


def test_name_rule_beats_folder_and_ext():
    result = classify(
        path="03_BIBLIOTECA/normas/SICRO_2024.pdf",
        name="SICRO_2024_composicoes.pdf",
        ext=".pdf",
    )
    assert result == "composicao_custo"


def test_ext_rule_when_no_name_match():
    result = classify(
        path="02_CLIENTE/CCR/04_PROJETO/geometrico.dwg",
        name="geometrico.dwg",
        ext="dwg",
    )
    assert result == "projeto_cad"


def test_folder_rule_when_no_name_no_ext_match():
    result = classify(
        path="02_CLIENTE/EGTC/05_MEDICAO/BM_202607.xlsx",
        name="BM_202607.xlsx",
        ext="xlsx",
    )
    assert result == "boletim_medicao"


def test_folder_only_fallback():
    result = classify(
        path="02_CLIENTE/OEC/06_CORRESPONDENCIA/oficio_042.docx",
        name="oficio_042.docx",
        ext="docx",
    )
    assert result == "correspondencia"


def test_unknown_returns_outros():
    result = classify(
        path="05_INTERNO/misc/foo.zip",
        name="foo.zip",
        ext="zip",
    )
    assert result == "outros"


def test_case_insensitive_name_rules():
    result = classify(
        path="qualquer/lugar",
        name="Sondagem_SPT_BR116.pdf",
        ext="pdf",
    )
    assert result == "sondagem"


def test_ifc_variants_all_map_to_modelo_bim():
    for ext in ("ifc", "ifczip", "ifcxml", ".IFC"):
        assert classify("qualquer", "modelo.ifc", ext) == "modelo_bim"
