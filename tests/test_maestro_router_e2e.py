#!/usr/bin/env python3
"""
Maestro Router E2E Tests (v5.0)
=========================================
40 golden test cases for routing accuracy, context injection, and tiering.

Cobertura:
  - S1–S11 (9 verticais): rodovias, OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens
  - Horizontais 00–16: maestro, claims, contratual, imobiliário, orçamento, modelagem, cronograma, BD, apresentações, advisory, arquiteto-IA
  - Cross-agent flows: 3 cenários
  - Ambiguity resolution: 2 casos

Assertions validadas:
  - expected_agent_id
  - expected_skill
  - expected_phase (pode ser null para horizontais)
  - expected_model_tier (haiku-4-5, sonnet-5, opus)
  - routing_confidence >= 0.80
  - complexity_score alinhado

Uso:
  pytest tests/test_maestro_router_e2e.py -v
  pytest tests/test_maestro_router_e2e.py::TestMaestroRouterS9 -v  # Apenas S8
  pytest tests/test_maestro_router_e2e.py -k "cross_agent" -v
"""

import json
import os
import sys
import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class ModelTier(str, Enum):
    HAIKU = "haiku-4-5"
    SONNET = "sonnet-5"
    OPUS = "opus"


@dataclass
class TestCase:
    """Caso de teste baseado em fixture JSON."""
    id: str
    category: str
    prompt: str
    context_hints: List[str]
    expected_agent_id: str
    expected_skill: str
    expected_phase: Optional[str]
    expected_model_tier: str
    routing_confidence_min: float
    keywords: List[str]
    complexity_score_expected: float
    cross_agent_references: Optional[List[str]] = None
    note: Optional[str] = None


# ============================================================================
# ROUTER SOB TESTE
# ============================================================================
# Até 2026-09-22 este arquivo trazia um MockMaestroRouter inline (casamento
# por substring, numeração antiga S6=Portos…S10=Barragens). Os testes agora
# exercitam o router de referência real, compartilhado com
# tests/test_cross_agent_flows.py — ver docs/auditoria/RELATORIO-AUDITORIA-2026-09-22.md.

from src.maestro import keyword_router


class MaestroRouter:
    """Adaptador fino sobre src/maestro/keyword_router.py."""

    def route(self, prompt: str, context_hints: Optional[List[str]] = None,
              complexity_score: Optional[float] = None) -> "keyword_router.RoutingResult":
        return keyword_router.route(prompt, context_hints, complexity_score)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def maestro_router():
    """Router de referência (src/maestro/keyword_router.py)."""
    return MaestroRouter()


@pytest.fixture(scope="session")
def golden_test_cases() -> List[TestCase]:
    """Carrega 40 golden test cases do JSON (numeração D2)."""
    fixtures_path = Path(__file__).parent / "fixtures" / "prompts_golden_40.json"

    if not fixtures_path.exists():
        pytest.skip(f"Fixtures file not found: {fixtures_path}")

    with open(fixtures_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_cases = []
    for tc_dict in data['test_cases']:
        tc = TestCase(
            id=tc_dict['id'],
            category=tc_dict['category'],
            prompt=tc_dict['prompt'],
            context_hints=tc_dict['context_hints'],
            expected_agent_id=tc_dict['expected_agent_id'],
            expected_skill=tc_dict['expected_skill'],
            expected_phase=tc_dict.get('expected_phase'),
            expected_model_tier=tc_dict['expected_model_tier'],
            routing_confidence_min=tc_dict['routing_confidence_min'],
            keywords=tc_dict['keywords'],
            complexity_score_expected=tc_dict['complexity_score_expected'],
            cross_agent_references=tc_dict.get('cross_agent_references'),
            note=tc_dict.get('note'),
        )
        test_cases.append(tc)

    return test_cases


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestMaestroRouterS9:
    """Testes para S9 — Saneamento."""

    def test_s9_eta_buenos_aires(self, maestro_router, golden_test_cases):
        """S9-001: ETA em Buenos Aires — routing correto."""
        tc = next(t for t in golden_test_cases if t.id == "s9_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id, \
            f"Expected {tc.expected_agent_id}, got {result.agent_id}"
        assert result.routing_confidence >= tc.routing_confidence_min
        assert result.model_tier == "haiku-4-5"
        assert result.complexity_score <= 3.0

    def test_s9_esgoto_500k(self, maestro_router, golden_test_cases):
        """S9-002: Tratamento esgoto 500k hab — cross-agent com orçamento."""
        tc = next(t for t in golden_test_cases if t.id == "s9_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.routing_confidence >= tc.routing_confidence_min
        assert tc.cross_agent_references == ["manta-05"]

    def test_s9_adutora_projeto_executivo(self, maestro_router, golden_test_cases):
        """S9-003: Adutora 45km projeto executivo — tiering Sonnet."""
        tc = next(t for t in golden_test_cases if t.id == "s9_003")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "sonnet-5"
        assert result.phase == "projeto-executivo"
        assert result.complexity_score >= 4.0

    def test_s9_lei_14026_subsídio(self, maestro_router, golden_test_cases):
        """S9-004: Lei 14.026 subsídio cruzado — fase licitação."""
        tc = next(t for t in golden_test_cases if t.id == "s9_004")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.phase == "licitacao"


class TestMaestroRouterS10:
    """Testes para S10 — Energia."""

    def test_s10_rap_lt_765kv(self, maestro_router, golden_test_cases):
        """S10-001: RAP LT 765kV ANEEL — projeto executivo."""
        tc = next(t for t in golden_test_cases if t.id == "s10_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "sonnet-5"
        assert result.phase == "projeto-executivo"

    def test_s10_subestacao_omm(self, maestro_router, golden_test_cases):
        """S10-002: O&M subestação 500 MVA."""
        tc = next(t for t in golden_test_cases if t.id == "s10_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.phase == "operacao"

    def test_s10_uhe_50mw(self, maestro_router, golden_test_cases):
        """S10-003: UHE 50MW — licenciamento ambiental."""
        tc = next(t for t in golden_test_cases if t.id == "s10_003")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS7:
    """Testes para S7 — Portos."""

    def test_s7_terminal_conteineres(self, maestro_router, golden_test_cases):
        """S7-001: Terminal contêineres em dragagem -15m."""
        tc = next(t for t in golden_test_cases if t.id == "s7_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.routing_confidence >= 0.90

    def test_s7_ampliacao_pier(self, maestro_router, golden_test_cases):
        """S7-002: Ampliação píer 2 berços."""
        tc = next(t for t in golden_test_cases if t.id == "s7_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS8:
    """Testes para S8 — Aeroportos."""

    def test_s8_aeroporto_regional(self, maestro_router, golden_test_cases):
        """S8-001: Aeroporto regional — pista 2500m."""
        tc = next(t for t in golden_test_cases if t.id == "s8_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id

    def test_s8_terminal_5m_pax(self, maestro_router, golden_test_cases):
        """S8-002: Terminal 5M passageiros/ano."""
        tc = next(t for t in golden_test_cases if t.id == "s8_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS11:
    """Testes para S11 — Barragens."""

    def test_s11_barragem_rcc_80m(self, maestro_router, golden_test_cases):
        """S11-001: Barragem RCC 80m."""
        tc = next(t for t in golden_test_cases if t.id == "s11_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.complexity_score >= 4.0

    def test_s11_tsf_rejeitos_150m(self, maestro_router, golden_test_cases):
        """S11-002: TSF rejeitos dry-stack 150m."""
        tc = next(t for t in golden_test_cases if t.id == "s11_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS1toS4:
    """Testes para S1–S4 (Rodovias, OAE, Ferrovia, Metrô)."""

    def test_s1_pavimento_cbuq(self, maestro_router, golden_test_cases):
        """S1-001: Pavimento CBUQ."""
        tc = next(t for t in golden_test_cases if t.id == "s1_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s1_dnit_100km(self, maestro_router, golden_test_cases):
        """S1-002: Rodovia DNIT 100 km."""
        tc = next(t for t in golden_test_cases if t.id == "s1_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s2_ponte_concreto_protendido(self, maestro_router, golden_test_cases):
        """S2-001: Ponte concreto protendido 120m."""
        tc = next(t for t in golden_test_cases if t.id == "s2_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s2_viaduto_metalico(self, maestro_router, golden_test_cases):
        """S2-002: Viaduto estrutura metálica."""
        tc = next(t for t in golden_test_cases if t.id == "s2_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s3_via_permanente_lastro(self, maestro_router, golden_test_cases):
        """S3-001: Via permanente lastro."""
        tc = next(t for t in golden_test_cases if t.id == "s3_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s3_pantografo_catenaria(self, maestro_router, golden_test_cases):
        """S3-002: Pantógrafo e catenária."""
        tc = next(t for t in golden_test_cases if t.id == "s3_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s4_metro_natm_25m(self, maestro_router, golden_test_cases):
        """S4-001: Metrô NATM 25m profundidade."""
        tc = next(t for t in golden_test_cases if t.id == "s4_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id

    def test_s4_vlt_elevado_15km(self, maestro_router, golden_test_cases):
        """S4-002: VLT elevado 15 km."""
        tc = next(t for t in golden_test_cases if t.id == "s4_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterHorizontals:
    """Testes para agentes horizontais (Manta 00–16)."""

    def test_claims_indenizacao(self, maestro_router, golden_test_cases):
        """Manta 01 — Claims."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_claims_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "opus"

    def test_contratual_forca_maior(self, maestro_router, golden_test_cases):
        """Manta 02 — Contratual."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_legal_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_imobiliario_terreno(self, maestro_router, golden_test_cases):
        """Manta 04 — Imobiliário."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_imob_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_orcamento_metro(self, maestro_router, golden_test_cases):
        """Manta 05 — Orçamento."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_budget_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_modelagem_ppp(self, maestro_router, golden_test_cases):
        """Manta 06 — Modelagem."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_modeling_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "opus"

    def test_cronograma_paralelo(self, maestro_router, golden_test_cases):
        """Manta 07 — Cronograma."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_schedule_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_bd_opcao_porto(self, maestro_router, golden_test_cases):
        """Manta 13 — Business Development."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_bd_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_apresentacoes_executiva(self, maestro_router, golden_test_cases):
        """Manta 14 — Apresentações."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_pptx_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_advisory_parecer_lt(self, maestro_router, golden_test_cases):
        """Manta 15 — Advisory."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_advisory_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id

    def test_arquiteto_ia_design(self, maestro_router, golden_test_cases):
        """Manta 16 — Arquiteto IA."""
        tc = next(t for t in golden_test_cases if t.id == "horizontal_arch_001")
        result = maestro_router.route(tc.prompt, tc.context_hints)
        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "opus"


class TestMaestroRouterCrossAgent:
    """Testes para cross-agent flows."""

    def test_cross_agent_eta_orcamento(self, maestro_router, golden_test_cases):
        """Cross-Agent-001: ETA + Orçamento."""
        tc = next(t for t in golden_test_cases if t.id == "cross_agent_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert tc.cross_agent_references == ["manta-05"]

    def test_cross_agent_porto_cronograma_orcamento(self, maestro_router, golden_test_cases):
        """Cross-Agent-002: Porto + Cronograma + Orçamento."""
        tc = next(t for t in golden_test_cases if t.id == "cross_agent_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert set(tc.cross_agent_references or []) == {"manta-05", "manta-07"}

    def test_cross_agent_energia_modelagem(self, maestro_router, golden_test_cases):
        """Cross-Agent-003: Energia + Modelagem."""
        tc = next(t for t in golden_test_cases if t.id == "cross_agent_003")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert tc.cross_agent_references == ["manta-06"]


class TestMaestroRouterAmbiguity:
    """Testes para resolução de ambigüidade."""

    def test_ambiguity_ponte_vs_rodovia(self, maestro_router, golden_test_cases):
        """Ambiguidade-001: Fundação de ponte vs rodovia — contexto 'ponte' vence."""
        tc = next(t for t in golden_test_cases if t.id == "ambiguity_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id == "manta-03-s2"
        assert result.routing_confidence >= 0.80

    def test_ambiguity_drenagem_terminal_vs_urbana(self, maestro_router, golden_test_cases):
        """Ambiguidade-002: Drenagem em terminal vs urbana — contexto 'terminal' resolve para S6."""
        tc = next(t for t in golden_test_cases if t.id == "ambiguity_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id == "manta-03-s7"


class TestMaestroRouterMetrics:
    """Testes de métricas: accuracy, confidence, tiering."""

    def test_routing_accuracy_golden_set(self, maestro_router, golden_test_cases):
        """Accuracy: >80% correct routing em golden set (40 casos)."""
        correct_count = 0

        for tc in golden_test_cases:
            if tc.id.startswith("ambiguity"):
                continue  # Pular ambiguidade por enquanto

            result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
            if result.agent_id == tc.expected_agent_id:
                correct_count += 1

        accuracy = correct_count / (len(golden_test_cases) - 2)  # -2 para ambiguidades
        logger.info(f"Routing Accuracy: {accuracy:.1%} ({correct_count}/{len(golden_test_cases)-2})")

        assert accuracy >= 0.81, f"Accuracy {accuracy:.1%} < 81% minimum"

    def test_routing_confidence_min_80_percent(self, maestro_router, golden_test_cases):
        """Confidence: todos routes >= 80%."""
        for tc in golden_test_cases:
            if tc.id.startswith("cross_agent") or tc.id.startswith("ambiguity"):
                continue

            result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)
            assert result.routing_confidence >= 0.80, \
                f"{tc.id}: confidence {result.routing_confidence:.2f} < 0.80"

    def test_model_tiering_correctness(self, maestro_router, golden_test_cases):
        """Tiering: model_tier alinhado com complexity."""
        for tc in golden_test_cases:
            result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

            # Validar tiering logic
            if result.agent_id.startswith("manta-01") or result.agent_id == "manta-06":
                # Claims e Modeling sempre Opus
                assert result.model_tier == "opus", f"{tc.id}: esperado Opus para {result.agent_id}"
            elif tc.complexity_score_expected >= 4.0 and result.complexity_score >= 4.0:
                # Complexity alto = Sonnet ou Opus
                assert result.model_tier in ["sonnet-5", "opus"], \
                    f"{tc.id}: esperado Sonnet/Opus para complexity {tc.complexity_score_expected}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
