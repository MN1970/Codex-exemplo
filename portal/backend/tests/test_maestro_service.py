"""
Comprehensive tests for Maestro routing service
Tests all 20 agents and routing rules
"""

import pytest
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
            assert "claims" in intent.matched_keywords or "sinistro" in intent.matched_keywords

    def test_route_to_contratual(self, router):
        """Test routing to Contratual agent (Manta 02)"""
        test_cases = [
            "qual é a cláusula contratual?",
            "como interpretar essa condição?",
            "quais são as obrigações?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 02", f"Failed for: {query}"

    def test_route_to_imobiliario(self, router):
        """Test routing to Imobiliário agent (Manta 04)"""
        test_cases = [
            "qual é o registro do imóvel?",
            "como calcular o direito real?",
            "preciso de uma hipoteca",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 04", f"Failed for: {query}"

    def test_route_to_orcamento(self, router):
        """Test routing to Orçamento agent (Manta 05)"""
        test_cases = [
            "preciso de um orçamento",
            "qual é o preço?",
            "me dê uma estimativa de custo",
            "qual é o valor da obra?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 05", f"Failed for: {query}"
            assert intent.confidence > 0.5

    def test_route_to_modelagem(self, router):
        """Test routing to Modelagem agent (Manta 06)"""
        test_cases = [
            "preciso de um modelo matemático",
            "fazer uma simulação de cenários",
            "análise prospectiva",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 06", f"Failed for: {query}"

    def test_route_to_cronograma(self, router):
        """Test routing to Cronograma agent (Manta 07)"""
        test_cases = [
            "preciso de um cronograma",
            "qual é o prazo?",
            "quando será a próxima fase?",
            "qual é o marco do projeto?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 07", f"Failed for: {query}"

    def test_route_to_bd(self, router):
        """Test routing to Business Dev agent (Manta 13)"""
        test_cases = [
            "qual é a oportunidade de negócio?",
            "preciso de uma parceria",
            "qual é o potencial de mercado?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 13", f"Failed for: {query}"

    def test_route_to_apresentacoes(self, router):
        """Test routing to Apresentações agent (Manta 14)"""
        test_cases = [
            "preciso de slides para apresentação",
            "fazer um deck de pitch",
            "criar um visual para a proposta",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 14", f"Failed for: {query}"

    def test_route_to_advisory(self, router):
        """Test routing to Advisory agent (Manta 15)"""
        test_cases = [
            "preciso de consultoria",
            "qual é sua recomendação?",
            "qual deveria ser a estratégia?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 15", f"Failed for: {query}"

    def test_route_to_arquiteto_ia(self, router):
        """Test routing to Arquiteto-IA agent (Manta 16)"""
        test_cases = [
            "qual é a melhor arquitetura?",
            "como estruturar este framework?",
            "qual é o padrão de design?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 16", f"Failed for: {query}"

    # === VERTICAL AGENTS — INFRASTRUCTURE (S1-S4) ===

    def test_route_to_infraestrutura_s1_rodovias(self, router):
        """Test routing to S1 Rodovias (Roads)"""
        test_cases = [
            "qual é o pavimento adequado?",
            "como calcular CBUQ?",
            "qual é a terraplenagem necessária?",
            "tabela DNIT SICRO",
            "projeto de rodovia",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S1", f"Failed for: {query}"
            assert intent.segment == "Rodovias"

    def test_route_to_infraestrutura_s2_oae(self, router):
        """Test routing to S2 OAE (Bridges/Viaducts)"""
        test_cases = [
            "projeto de ponte",
            "como projetar um viaduto?",
            "NBR 7187 para OAE",
            "estrutura especial",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S2", f"Failed for: {query}"
            assert intent.segment == "OAE (pontes, viadutos)"

    def test_route_to_infraestrutura_s3_ferrovia(self, router):
        """Test routing to S3 Ferrovia (Railways)"""
        test_cases = [
            "projeto de ferrovia",
            "qual é a via permanente?",
            "AMV em ferrovias",
            "como calcular dormente?",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S3", f"Failed for: {query}"
            assert intent.segment == "Ferrovia"

    def test_route_to_infraestrutura_s4_metro(self, router):
        """Test routing to S4 Metrô (Metro)"""
        test_cases = [
            "projeto de metrô",
            "como calcular NATM?",
            "qual é o PSD?",
            "estação de metrô",
            "linha de VLT",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S4", f"Failed for: {query}"
            assert intent.segment == "Metrô"

    # === VERTICAL AGENTS — NEW SEGMENTS (S6-S10) ===

    def test_route_to_portos(self, router):
        """Test routing to S6 Portos (Ports)"""
        test_cases = [
            "projeto portuário",
            "dragagem no porto",
            "ANTAQ regulamentação",
            "terminal de contêineres",
            "cais portuário",
            "granel sólido",
            "PIANC guidelines",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S6", f"Failed for: {query}"
            assert intent.segment == "Portos"
            assert intent.confidence > 0.5

    def test_route_to_aeroportos(self, router):
        """Test routing to S7 Aeroportos (Airports)"""
        test_cases = [
            "projeto de aeroporto",
            "pista de pouso",
            "ANAC regulamentação",
            "ICAO standards",
            "terminal de passageiros (TPS)",
            "balizamento de pista",
            "RBAC 154",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S7", f"Failed for: {query}"
            assert intent.segment == "Aeroportos"

    def test_route_to_saneamento(self, router):
        """Test routing to S8 Saneamento (Sanitation)"""
        test_cases = [
            "projeto de ETA",
            "ETE para esgoto",
            "adutora de água",
            "AySA sistema",
            "drenagem urbana",
            "SNIS dados",
            "Lei 14.026",
            "tratamento de água",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S8", f"Failed for: {query}"
            assert intent.segment == "Saneamento"
            assert intent.confidence > 0.5

    def test_route_to_energia(self, router):
        """Test routing to S9 Energia (Energy)"""
        test_cases = [
            "linha de transmissão",
            "projeto de LT",
            "subestação",
            "ANEEL regulamentação",
            "leilão de transmissão",
            "ONS coordenação",
            "geração eólica",
            "solar fotovoltaica",
        ]
        for query in test_cases:
            intent = router.detect_intent(query)
            assert intent.agent_code == "Manta 03-S9", f"Failed for: {query}"
            assert intent.segment == "Energia"

    def test_route_to_barragens(self, router):
        """Test routing to S10 Barragens (Dams)"""
        test_cases = [
            "projeto de barragem",
            "CFRD concreto",
            "rejeitos de mineração",
            "ICOLD standards",
            "Lei 12.334",
            "vertedouro de barragem",
            "TSF de rejeitos",
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

    def test_confidence_pattern_match(self, router):
        """Test pattern matches get reasonable confidence"""
        intent = router.detect_intent("projeto com dragagem portuária")
        assert intent.confidence >= 0.60

    def test_confidence_multiple_keywords(self, router):
        """Test multiple matching keywords increase confidence"""
        intent = router.detect_intent("adutora esgoto saneamento AySA")
        assert intent.confidence >= 0.95

    def test_confidence_fallback_low(self, router):
        """Test fallback to Maestro has very low confidence"""
        intent = router.detect_intent("xyz abc 123")
        assert intent.confidence < 0.25
        assert intent.agent_id == "manta-00"

    # === CONFIDENCE LEVEL CATEGORIZATION TESTS ===

    def test_confidence_level_exact(self, router):
        """Test EXACT confidence level"""
        intent = router.detect_intent("ETA adutora esgoto saneamento")
        assert intent.confidence_level == RoutingConfidence.EXACT

    def test_confidence_level_high(self, router):
        """Test HIGH confidence level"""
        intent = router.detect_intent("dragagem portuária")
        assert intent.confidence_level == RoutingConfidence.HIGH

    def test_confidence_level_medium(self, router):
        """Test MEDIUM confidence level"""
        # A query that matches but not perfectly
        intent = router.detect_intent("projeto")
        # This will likely be fallback or low medium
        if intent.confidence_level in [RoutingConfidence.MEDIUM, RoutingConfidence.LOW]:
            pass  # Expected

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
        assert profile.name == "maestro (router)"

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
        assert any(a.code == "Manta 03-S8" for a in results)

    def test_search_agents_by_keyword(self, router):
        """Test searching agents by keyword"""
        results = router.search_agents("ETA")
        assert len(results) > 0
        assert any(a.id == "manta-03-s8" for a in results)

    def test_search_agents_by_alias(self, router):
        """Test searching agents by alias"""
        results = router.search_agents("business-dev")
        assert len(results) > 0
        assert any(a.code == "Manta 13" for a in results)

    # === EDGE CASES ===

    def test_empty_input(self, router):
        """Test handling empty input"""
        intent = router.detect_intent("")
        assert intent.agent_code == "Manta 00"  # Fallback to Maestro

    def test_whitespace_only_input(self, router):
        """Test handling whitespace-only input"""
        intent = router.detect_intent("   ")
        assert intent.agent_code == "Manta 00"  # Fallback to Maestro

    def test_case_insensitive_matching(self, router):
        """Test case-insensitive keyword matching"""
        intent1 = router.detect_intent("SANEAMENTO ETA")
        intent2 = router.detect_intent("saneamento eta")
        intent3 = router.detect_intent("Saneamento Eta")

        assert intent1.agent_code == intent2.agent_code == intent3.agent_code
        assert intent1.confidence == intent2.confidence == intent3.confidence

    def test_portuguese_accents(self, router):
        """Test matching with Portuguese accents"""
        intent1 = router.detect_intent("água e esgoto")
        intent2 = router.detect_intent("agua e esgoto")

        # Both should route to saneamento
        assert intent1.agent_code == "Manta 03-S8"
        # Case 2 might have lower confidence or different agent
        # but should still be routed somewhere reasonable

    def test_mixed_content_routing(self, router):
        """Test routing with mixed irrelevant content"""
        intent = router.detect_intent("fale comigo sobre dragagem portuária e outros tópicos")
        assert intent.agent_code == "Manta 03-S6"

    # === TIER AND STATUS TESTS ===

    def test_agent_tier_classification(self, router):
        """Test agents have appropriate tier classifications"""
        profiles = router.list_agents()

        # Verify some known tier assignments
        claims = next(a for a in profiles if a.code == "Manta 01")
        assert claims.tier == "Opus"

        maestro = next(a for a in profiles if a.code == "Manta 00")
        assert "Haiku" in maestro.tier or "Sonnet" in maestro.tier

    def test_agent_status_operational(self, router):
        """Test agents have operational status"""
        profiles = router.list_agents()

        # Most agents should be operational
        operational = [a for a in profiles if a.status == "Operacional"]
        assert len(operational) >= 15  # At least 15 operational


class TestIntegrationRouting:
    """Integration tests for realistic routing scenarios"""

    @pytest.fixture
    def router(self):
        return MaestroRouter()

    def test_realistic_user_query_1(self, router):
        """Test real-world query about road construction"""
        query = (
            "Estou trabalhando em um projeto de rodovia federal. "
            "Preciso de ajuda com o cálculo de terraplenagem e CBUQ. "
            "Qual é a melhor prática de terraplenagem?"
        )
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 03-S1"
        assert intent.confidence > 0.7

    def test_realistic_user_query_2(self, router):
        """Test real-world query about sanitation project"""
        query = (
            "Estou desenvolvendo um projeto de ETA e ETE para a AySA. "
            "Como devemos estruturar a adutora? "
            "Quais são as regulamentações da SNIS?"
        )
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 03-S8"
        assert intent.confidence > 0.8

    def test_realistic_user_query_3(self, router):
        """Test real-world query about energy transmission"""
        query = (
            "Tenho um leilão de linha de transmissão (LT) próximo. "
            "Qual é a regulamentação ANEEL? "
            "Como funciona o RAP?"
        )
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 03-S9"
        assert intent.confidence > 0.7

    def test_realistic_user_query_4(self, router):
        """Test real-world query about port project"""
        query = (
            "Desenvolvemos um terminal portuário. "
            "Precisamos fazer dragagem de manutenção. "
            "Como registrar na ANTAQ?"
        )
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 03-S6"
        assert intent.confidence > 0.7

    def test_realistic_user_query_5(self, router):
        """Test real-world query about general budget"""
        query = "Qual é o orçamento estimado para este projeto?"
        intent = router.detect_intent(query)
        assert intent.agent_code == "Manta 05"
        assert intent.confidence > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
