"""
Comprehensive tests for Maestro routing service
Tests all 20 agents and routing rules
"""

import pytest
import sys
import os

# Add the app directory to the path to allow direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.maestro_service import MaestroRouter, RoutingRule
from app.models.maestro import (
    RoutingIntent,
    AgentProfile,
    RoutingConfidence,
)


class TestMaestroRouter:
    """Test suite for Maestro routing service"""

    @pytest.fixture
    def router(self):
        """Create router instance"""
        return MaestroRouter()

    def test_router_initialization(self, router):
        """Test router initializes with all 20 agents"""
        assert len(router.ROUTING_RULES) == 20
        assert "maestro" in router.ROUTING_RULES
        assert "saneamento" in router.ROUTING_RULES
        assert "energia" in router.ROUTING_RULES

    def test_pattern_compilation(self, router):
        """Test all patterns compile without errors"""
        assert len(router._compiled_patterns) == 20
        for rule_key in router.ROUTING_RULES.keys():
            assert rule_key in router._compiled_patterns

    # === HORIZONTAL AGENTS TESTS ===

    def test_route_to_maestro(self, router):
        """Test routing to Maestro (Manta 00)"""
        intent = router.detect_intent("qual agente devo usar?")
        assert intent.agent_code == "Manta 00"
        assert intent.agent_id == "manta-00"
        assert intent.agent_name == "maestro (router)"

    def test_route_to_claims(self, router):
        """Test routing to Claims agent (Manta 01)"""
        test_cases = [
            "tenho uma disputa contratual",
            "como processar um sinistro?",
            "qual é meu direito de indenização?",
            "litígio com cliente",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 01", f"Failed for: {query}"

    def test_route_to_contratual(self, router):
        """Test routing to Contratual agent (Manta 02)"""
        query = "qual é a cláusula contratual?"
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 02"

    def test_route_to_orcamento(self, router):
        """Test routing to Orçamento agent (Manta 05)"""
        test_cases = [
            "preciso de um orçamento",
            "qual é o preço?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 05", f"Failed for: {query}"
            assert intent.confidence > 0.5

    def test_route_to_cronograma(self, router):
        """Test routing to Cronograma agent (Manta 07)"""
        query = "preciso de um cronograma"
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 07"

    # === VERTICAL AGENTS — NEW SEGMENTS (S6-S10) ===

    def test_route_to_saneamento(self, router):
        """Test routing to S8 Saneamento (Sanitation)"""
        test_cases = [
            "projeto de ETA",
            "ETE para esgoto",
            "adutora de água",
            "AySA sistema",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S8", f"Failed for: {query}"
            assert intent.segment == "Saneamento"

    def test_route_to_energia(self, router):
        """Test routing to S9 Energia (Energy)"""
        test_cases = [
            "linha de transmissão",
            "projeto de LT",
            "subestação",
            "ANEEL regulamentação",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S9", f"Failed for: {query}"
            assert intent.segment == "Energia"

    def test_route_to_portos(self, router):
        """Test routing to S6 Portos (Ports)"""
        test_cases = [
            "terminal portuário",
            "dragagem no porto",
            "ANTAQ regulamentação",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S6", f"Failed for: {query}"
            assert intent.segment == "Portos"

    def test_route_to_aeroportos(self, router):
        """Test routing to S7 Aeroportos (Airports)"""
        test_cases = [
            "projeto de aeroporto",
            "pista de pouso",
            "ANAC regulamentação",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S7", f"Failed for: {query}"
            assert intent.segment == "Aeroportos"

    def test_route_to_barragens(self, router):
        """Test routing to S10 Barragens (Dams)"""
        test_cases = [
            "projeto de barragem",
            "CFRD concreto",
            "rejeitos de mineração",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S10", f"Failed for: {query}"
            assert intent.segment == "Barragens"

    # === CONFIDENCE SCORING TESTS ===

    def test_confidence_exact_match(self, router):
        """Test exact keyword matches get high confidence"""
        intent = router.detect_intent("ETA ETE saneamento")
        assert intent.confidence >= 0.85

    def test_confidence_fallback_low(self, router):
        """Test fallback to Maestro has very low confidence"""
        intent = router.detect_intent("xyz abc 123")
        assert intent.confidence < 0.25
        assert intent.agent_id == "manta-00"

    def test_confidence_level_exact(self, router):
        """Test EXACT confidence level"""
        intent = router.detect_intent("ETA adutora esgoto saneamento")
        assert intent.confidence_level == RoutingConfidence.EXACT

    def test_confidence_level_fallback(self, router):
        """Test FALLBACK confidence level"""
        intent = router.detect_intent("random text no matching keywords")
        assert intent.confidence_level == RoutingConfidence.FALLBACK

    # === EIXO CLASSIFICATION TESTS ===

    def test_horizontal_agent_eixo(self, router):
        """Test horizontal agents are classified correctly"""
        intent = router.detect_intent("orçamento")
        assert intent.eixo == "Horizontal"

    def test_vertical_agent_eixo(self, router):
        """Test vertical agents are classified correctly"""
        intent = router.detect_intent("ETA saneamento")
        assert intent.eixo == "Vertical"
        assert intent.segment is not None

    # === AGENT LISTING TESTS ===

    def test_list_all_agents(self, router):
        """Test listing all agents"""
        agents = router.list_agents()
        assert len(agents) == 20
        assert all(isinstance(a, AgentProfile) for a in agents)

    def test_list_agents_by_eixo_horizontal(self, router):
        """Test filtering agents by Horizontal eixo"""
        agents = router.list_agents_by_eixo("Horizontal")
        assert len(agents) == 11  # 11 horizontal agents
        assert all(a.eixo == "Horizontal" for a in agents)

    def test_list_agents_by_eixo_vertical(self, router):
        """Test filtering agents by Vertical eixo"""
        agents = router.list_agents_by_eixo("Vertical")
        assert len(agents) == 9  # 4 S1-S4 + 5 S6-S10
        assert all(a.eixo == "Vertical" for a in agents)

    # === AGENT PROFILE TESTS ===

    def test_get_agent_profile_maestro(self, router):
        """Test getting Maestro agent profile"""
        profile = router.get_agent_profile("manta-00")
        assert profile is not None
        assert profile.code == "Manta 00"

    def test_get_agent_profile_saneamento(self, router):
        """Test getting Saneamento agent profile"""
        profile = router.get_agent_profile("manta-03-s8")
        assert profile is not None
        assert profile.code == "Manta 03-S8"
        assert profile.segment == "Saneamento"

    def test_get_agent_profile_not_found(self, router):
        """Test getting non-existent agent profile"""
        profile = router.get_agent_profile("manta-99")
        assert profile is None

    # === AGENT SEARCH TESTS ===

    def test_search_agents_by_name(self, router):
        """Test searching agents by name"""
        results = router.search_agents("saneamento")
        assert len(results) > 0
        assert any(a.id == "manta-03-s8" for a in results)

    def test_search_agents_by_code(self, router):
        """Test searching agents by code"""
        results = router.search_agents("Manta 03-S8")
        assert len(results) > 0

    # === EDGE CASES ===

    def test_empty_input(self, router):
        """Test handling empty input"""
        intent = router.detect_intent("")
        assert intent.agent_code == "Manta 00"  # Fallback to Maestro

    def test_case_insensitive_matching(self, router):
        """Test case-insensitive keyword matching"""
        intent1 = router.detect_intent("SANEAMENTO ETA")
        intent2 = router.detect_intent("saneamento eta")
        intent3 = router.detect_intent("Saneamento Eta")

        assert intent1.agent_code == intent2.agent_code == intent3.agent_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
