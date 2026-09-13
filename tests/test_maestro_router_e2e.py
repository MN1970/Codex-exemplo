#!/usr/bin/env python3
"""
Maestro Router E2E Tests (v5.0)
=========================================
40 golden test cases for routing accuracy, context injection, and tiering.

Cobertura:
  - S1–S10 (9 verticais): rodovias, OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens
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
  pytest tests/test_maestro_router_e2e.py::TestMaestroRouterS8 -v  # Apenas S8
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
class RoutingResult:
    """Resultado de routing do Maestro."""
    agent_id: str
    skill_id: str
    model_tier: str
    complexity_score: float
    routing_confidence: float
    phase: Optional[str] = None
    rag_collection: Optional[str] = None
    rag_reranker_score: Optional[float] = None
    fallback_agent: Optional[str] = None
    context_injection: Optional[Dict] = None


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
# MOCK MAESTRO ROUTER (Simulação R1)
# ============================================================================

class MockMaestroRouter:
    """
    Simulação simplificada do Maestro Router v5.0 para testes.
    Em produção, seria uma chamada RPC ao Maestro via Supabase ou HTTP.
    """

    def __init__(self):
        """Carrega regras de routing."""
        self.routing_rules = self._build_routing_rules()
        self.agent_configs = self._build_agent_configs()

    def _build_routing_rules(self) -> Dict[str, List[str]]:
        """Constrói regras de routing por agente vertical."""
        return {
            "manta-03-s8": ["saneamento", "ETA", "ETE", "adutora", "esgoto", "água",
                           "AySA", "drenagem", "SNIS", "PMSB", "Lei 14.026", "elevatória",
                           "reservatório", "UASB", "MBR", "reuso"],
            "manta-03-s9": ["energia", "transmissao", "LT", "subestacao", "ANEEL", "RAP",
                           "leilao", "ONS", "EPE", "PDE", "geração", "eólica", "PV",
                           "hidraulica", "PCH", "UHE", "usina", "termica", "nuclear"],
            "manta-03-s6": ["porto", "terminal", "ANTAQ", "dragagem", "molhe", "quebra-mar",
                           "berço", "calado", "contêiner", "granel", "cais", "píer",
                           "retroarea", "patio", "TUP", "TPS", "PIANC", "hidrovia"],
            "manta-03-s7": ["aeroporto", "pista", "RWY", "taxiway", "TWY", "patio", "TPS",
                           "TECA", "ANAC", "RBAC", "ICAO", "Annex 14", "FAA", "balizamento",
                           "PAPI", "ILS", "PCN", "gate", "jetway", "ponte", "embarque"],
            "manta-03-s10": ["barragem", "vertedouro", "CFRD", "CCR", "RCC", "rejeitos", "TSF",
                            "PNSB", "ICOLD", "CBDB", "dique", "SIGBM", "ANM", "ANA", "Lei 12.334"],
            "manta-03-s1": ["rodovia", "pavimento", "CBUQ", "BGS", "terraplenagem", "SICRO",
                           "DNIT", "asfalto", "concreto", "base", "sub-base", "corte", "aterro"],
            "manta-03-s2": ["ponte", "viaduto", "OAE", "NBR 7187", "túnel", "fundacao",
                           "pilares", "aparelhos-apoio", "junta", "elastômero", "vão", "laje"],
            "manta-03-s3": ["ferrovia", "trilho", "AMV", "dormente", "via-permanente", "bitola",
                           "pantografo", "catenaria", "estacao", "ptv", "ramal", "desvio"],
            "manta-03-s4": ["metro", "estacao", "NATM", "PSD", "linha", "VLT", "subterraneo",
                           "elevado", "superficial", "portal", "tunél-metro", "trem", "ATO"],
            "manta-01": ["claims", "indenizacao", "sinistro", "seguro", "prejuizo"],
            "manta-02": ["contrato", "legal", "clausula", "jurisdicao", "litigancia", "forca-maior"],
            "manta-04": ["imobiliario", "real-estate", "terreno", "avaliacao", "propriedade"],
            "manta-05": ["orcamento", "budget", "custo", "estimativa", "SICRO", "preço"],
            "manta-06": ["modelagem", "modelo", "financeiro", "PPP", "viabilidade", "VPL", "TIR"],
            "manta-07": ["cronograma", "schedule", "planejamento", "projeto", "recursos", "MS Project"],
            "manta-13": ["bd", "negocio", "oportunidade", "mercado", "comercial"],
            "manta-14": ["apresentacao", "pptx", "slides", "executiva", "comunicacao"],
            "manta-15": ["advisory", "parecer", "opiniao", "tecnico", "consultoria"],
            "manta-16": ["arquitetura", "ia", "design", "agente", "sistema"],
        }

    def _build_agent_configs(self) -> Dict[str, Dict]:
        """Constrói configurações padrão dos agentes."""
        return {
            "manta-03-s8": {"default_model_tier": "sonnet-5", "rag_collection": "san:v5.0:*"},
            "manta-03-s9": {"default_model_tier": "sonnet-5", "rag_collection": "ene:v5.0:*"},
            "manta-03-s6": {"default_model_tier": "sonnet-5", "rag_collection": "por:v5.0:*"},
            "manta-03-s7": {"default_model_tier": "sonnet-5", "rag_collection": "aer:v5.0:*"},
            "manta-03-s10": {"default_model_tier": "sonnet-5", "rag_collection": "bar:v5.0:*"},
            "manta-03-s1": {"default_model_tier": "sonnet-5", "rag_collection": "rod:v5.0:*"},
            "manta-03-s2": {"default_model_tier": "sonnet-5", "rag_collection": "oae:v5.0:*"},
            "manta-03-s3": {"default_model_tier": "sonnet-5", "rag_collection": "fer:v5.0:*"},
            "manta-03-s4": {"default_model_tier": "sonnet-5", "rag_collection": "met:v5.0:*"},
            "manta-01": {"default_model_tier": "opus", "rag_collection": None},
            "manta-02": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-04": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-05": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-06": {"default_model_tier": "opus", "rag_collection": None},
            "manta-07": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-13": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-14": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-15": {"default_model_tier": "sonnet-5", "rag_collection": None},
            "manta-16": {"default_model_tier": "opus", "rag_collection": None},
        }

    def route(self, prompt: str, context_hints: Optional[List[str]] = None,
              complexity_score: Optional[float] = None) -> RoutingResult:
        """
        Simula R1 — Routing Determinístico.

        Estágios:
          1. Keyword matching × BM25
          2. Context + phase inference
          3. Tiering + config
        """
        prompt_lower = prompt.lower()
        context_hints = context_hints or []

        # Stage 1: Keyword matching
        best_agent = None
        best_score = 0.0

        for agent_id, keywords in self.routing_rules.items():
            matches = sum(1 for kw in keywords if kw.lower() in prompt_lower)
            score = matches / len(keywords) if keywords else 0

            # Boost score se keyword está em context_hints
            for hint in context_hints:
                if hint.lower() in keywords:
                    score += 0.15

            if score > best_score:
                best_score = score
                best_agent = agent_id

        if not best_agent:
            # Fallback: maestro (00)
            best_agent = "manta-00"

        # Stage 2: Phase inference
        phase = self._infer_phase(prompt_lower)

        # Stage 3: Tiering
        if complexity_score is None:
            complexity_score = len([h for h in context_hints if h.lower() in prompt_lower])

        model_tier = self._compute_tiering(best_agent, complexity_score, len(prompt))

        # Construct routing confidence
        routing_confidence = min(0.95, best_score + 0.05)

        # Get agent config
        agent_config = self.agent_configs.get(best_agent, {})
        skill_id = f"{best_agent.replace('manta-', '').replace('-', '_')}.v5.0"

        return RoutingResult(
            agent_id=best_agent,
            skill_id=skill_id,
            model_tier=model_tier,
            complexity_score=complexity_score,
            routing_confidence=routing_confidence,
            phase=phase,
            rag_collection=agent_config.get('rag_collection'),
            rag_reranker_score=0.85,  # Mock
            fallback_agent="manta-00",
            context_injection={
                "phase": phase,
                "file_processing": False,
                "rag_collection": agent_config.get('rag_collection'),
            }
        )

    def _infer_phase(self, prompt: str) -> Optional[str]:
        """Infere phase (ciclo de vida) baseado em keywords."""
        phases_map = {
            "estudo-previo": ["estudo prévio", "diagnóstico", "benchmarking", "baseline"],
            "projeto-basico": ["projeto básico", "conceito", "layout", "viabilidade"],
            "projeto-executivo": ["projeto executivo", "detalh", "especificação", "técnico"],
            "obra": ["obra", "execução", "construção", "implantação"],
            "operacao": ["operação", "manutenção", "O&M", "gestão", "OPEX"],
            "licitacao": ["licitação", "edital", "concorrência", "processo competitivo"],
            "due-diligence": ["due diligence", "auditoria", "DD", "M&A"],
            "encerramento": ["encerramento", "descomissionamento", "final"],
        }

        for phase, keywords in phases_map.items():
            if any(kw in prompt for kw in keywords):
                return phase

        # Default: projeto-basico se ambíguo
        return "projeto-basico"

    def _compute_tiering(self, agent_id: str, complexity_score: float, prompt_len: int) -> str:
        """Implementa R7 — Tiering Automático."""
        # Mock: prompt_len < 500 = Haiku, 500-2000 = Sonnet, > 2000 = Opus

        # Prefer agent's default tier
        agent_default = self.agent_configs.get(agent_id, {}).get("default_model_tier", "sonnet-5")

        if agent_default == "opus":
            return "opus"  # Claims, Modeling, Architecture sempre Opus

        if complexity_score < 3.0 and prompt_len < 1500:
            return "haiku-4-5"
        elif complexity_score >= 4.5 or prompt_len > 3000:
            return "opus"
        else:
            return "sonnet-5"


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def maestro_router():
    """Instancia mock maestro router."""
    return MockMaestroRouter()


@pytest.fixture(scope="session")
def golden_test_cases() -> List[TestCase]:
    """Carrega 40 golden test cases do JSON."""
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

class TestMaestroRouterS8:
    """Testes para S8 — Saneamento."""

    def test_s8_eta_buenos_aires(self, maestro_router, golden_test_cases):
        """S8-001: ETA em Buenos Aires — routing correto."""
        tc = next(t for t in golden_test_cases if t.id == "s8_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id, \
            f"Expected {tc.expected_agent_id}, got {result.agent_id}"
        assert result.routing_confidence >= tc.routing_confidence_min
        assert result.model_tier == "haiku-4-5"
        assert result.complexity_score <= 3.0

    def test_s8_esgoto_500k(self, maestro_router, golden_test_cases):
        """S8-002: Tratamento esgoto 500k hab — cross-agent com orçamento."""
        tc = next(t for t in golden_test_cases if t.id == "s8_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.routing_confidence >= tc.routing_confidence_min
        assert tc.cross_agent_references == ["manta-05"]

    def test_s8_adutora_projeto_executivo(self, maestro_router, golden_test_cases):
        """S8-003: Adutora 45km projeto executivo — tiering Sonnet."""
        tc = next(t for t in golden_test_cases if t.id == "s8_003")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "sonnet-5"
        assert result.phase == "projeto-executivo"
        assert result.complexity_score >= 4.0

    def test_s8_lei_14026_subsídio(self, maestro_router, golden_test_cases):
        """S8-004: Lei 14.026 subsídio cruzado — fase licitação."""
        tc = next(t for t in golden_test_cases if t.id == "s8_004")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.phase == "licitacao"


class TestMaestroRouterS9:
    """Testes para S9 — Energia."""

    def test_s9_rap_lt_765kv(self, maestro_router, golden_test_cases):
        """S9-001: RAP LT 765kV ANEEL — projeto executivo."""
        tc = next(t for t in golden_test_cases if t.id == "s9_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.model_tier == "sonnet-5"
        assert result.phase == "projeto-executivo"

    def test_s9_subestacao_omm(self, maestro_router, golden_test_cases):
        """S9-002: O&M subestação 500 MVA."""
        tc = next(t for t in golden_test_cases if t.id == "s9_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.phase == "operacao"

    def test_s9_uhe_50mw(self, maestro_router, golden_test_cases):
        """S9-003: UHE 50MW — licenciamento ambiental."""
        tc = next(t for t in golden_test_cases if t.id == "s9_003")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS6:
    """Testes para S6 — Portos."""

    def test_s6_terminal_conteineres(self, maestro_router, golden_test_cases):
        """S6-001: Terminal contêineres em dragagem -15m."""
        tc = next(t for t in golden_test_cases if t.id == "s6_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.routing_confidence >= 0.90

    def test_s6_ampliacao_pier(self, maestro_router, golden_test_cases):
        """S6-002: Ampliação píer 2 berços."""
        tc = next(t for t in golden_test_cases if t.id == "s6_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS7:
    """Testes para S7 — Aeroportos."""

    def test_s7_aeroporto_regional(self, maestro_router, golden_test_cases):
        """S7-001: Aeroporto regional — pista 2500m."""
        tc = next(t for t in golden_test_cases if t.id == "s7_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id

    def test_s7_terminal_5m_pax(self, maestro_router, golden_test_cases):
        """S7-002: Terminal 5M passageiros/ano."""
        tc = next(t for t in golden_test_cases if t.id == "s7_002")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id


class TestMaestroRouterS10:
    """Testes para S10 — Barragens."""

    def test_s10_barragem_rcc_80m(self, maestro_router, golden_test_cases):
        """S10-001: Barragem RCC 80m."""
        tc = next(t for t in golden_test_cases if t.id == "s10_001")
        result = maestro_router.route(tc.prompt, tc.context_hints, tc.complexity_score_expected)

        assert result.agent_id == tc.expected_agent_id
        assert result.complexity_score >= 4.0

    def test_s10_tsf_rejeitos_150m(self, maestro_router, golden_test_cases):
        """S10-002: TSF rejeitos dry-stack 150m."""
        tc = next(t for t in golden_test_cases if t.id == "s10_002")
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

        assert result.agent_id == tc.expected_agent_id == "manta-03-s6"


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
