"""
Testes end-to-end para CAG
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.intent_classifier import IntentClassifier, AgentSelector
from orchestrator.response_ranker import ResponseRanker, AgentResponse

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def intent_classes():
    """Mock intent classes"""
    return {
        'saneamento': {
            'display_name': 'Saneamento',
            'description': 'Água, esgoto, drenagem',
            'keywords': ['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto', 'drenagem'],
            'primary_agents': ['agente-saneamento'],
            'secondary_agents': ['agente-energia', 'agente-contratual']
        },
        'energia': {
            'display_name': 'Energia',
            'description': 'Transmissão, distribuição, geração',
            'keywords': ['transmissão', 'LT', 'subestação', 'ANEEL', 'energia', 'geração'],
            'primary_agents': ['agente-energia'],
            'secondary_agents': ['agente-barragens', 'agente-contratual']
        },
        'portos': {
            'display_name': 'Portos',
            'description': 'Terminais, dragagem, molhes',
            'keywords': ['porto', 'terminal', 'ANTAQ', 'dragagem'],
            'primary_agents': ['agente-portos'],
            'secondary_agents': ['agente-contratual']
        },
        'ambigu': {
            'display_name': 'Ambíguo',
            'description': 'Multi-domínio',
            'keywords': [],
            'primary_agents': ['agente-saneamento', 'agente-energia'],
            'secondary_agents': []
        }
    }

@pytest.fixture
def agent_pool():
    """Mock agent pool"""
    return {
        'agente-saneamento': {},
        'agente-energia': {},
        'agente-portos': {},
        'agente-contratual': {},
        'agente-barragens': {}
    }

# =============================================================================
# TESTES: Intent Classifier
# =============================================================================

class TestIntentClassifier:

    def test_simple_keyword_match(self, intent_classes):
        """Test keyword matching para query simples"""
        classifier = IntentClassifier(intent_classes)
        query = "Qual é a norma para projeto de ETA?"

        prediction = classifier.classify(query)

        assert prediction.primary_intent == 'saneamento'
        assert prediction.confidence > 0.7
        assert 'ETA' in prediction.keywords_matched

    def test_ambiguous_query_multiple_keywords(self, intent_classes):
        """Test query ambígua com keywords de múltiplos intents"""
        classifier = IntentClassifier(intent_classes)
        query = "Saneamento com subestação de energia"

        prediction = classifier.classify(query)

        # Saneamento deve ser primary (aparece primeiro)
        assert prediction.primary_intent == 'saneamento'

        # Deve ter confiança média (ambíguo)
        assert 0.5 < prediction.confidence < 0.9

        # Deve ter detectado múltiplos keywords
        assert len(prediction.keywords_matched) >= 2

    def test_no_matching_keywords(self, intent_classes):
        """Test query sem keywords conhecidos"""
        classifier = IntentClassifier(intent_classes)
        query = "O que é um asteróide?"

        prediction = classifier.classify(query)

        # Deve cair em 'ambigu' (fallback)
        assert prediction.primary_intent == 'ambigu'
        assert len(prediction.keywords_matched) == 0

# =============================================================================
# TESTES: Agent Selector
# =============================================================================

class TestAgentSelector:

    def test_select_agents_high_confidence(self, intent_classes, agent_pool):
        """Test seleção de agentes com high confidence"""
        selector = AgentSelector(agent_pool, intent_classes)

        # Simular prediction com alta confiança
        from ml.intent_classifier import IntentPrediction
        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.95,
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Deve ter pelo menos 1 agente
        assert len(agents) >= 1

        # Primary agent deve ser selecionado
        assert agents[0].agent_slug == 'agente-saneamento'

    def test_select_agents_low_confidence(self, intent_classes, agent_pool):
        """Test seleção de agentes com low confidence (multiple agents)"""
        selector = AgentSelector(agent_pool, intent_classes)

        from ml.intent_classifier import IntentPrediction
        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.65,  # low confidence
            secondary_intents=[('energia', 0.55)],
            keywords_matched=['ETA', 'subestação'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Deve ter múltiplos agentes (primary + secondary)
        assert len(agents) >= 2

        # Scores devem ser descending
        assert agents[0].score >= agents[1].score

    def test_select_agents_filters_by_threshold(self, intent_classes, agent_pool):
        """Test que filtra agentes abaixo do threshold"""
        selector = AgentSelector(agent_pool, intent_classes)

        from ml.intent_classifier import IntentPrediction
        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.5,
            secondary_intents=[],
            keywords_matched=[],
            embedding=[0.1] * 100
        )

        # Com threshold alto, menos agentes
        agents_high_threshold = selector.select_agents(prediction, min_confidence=0.8)
        assert len(agents_high_threshold) == 0

        # Com threshold baixo, mais agentes
        agents_low_threshold = selector.select_agents(prediction, min_confidence=0.3)
        assert len(agents_low_threshold) > 0

# =============================================================================
# TESTES: Response Ranker (mock — não chama Claude API)
# =============================================================================

class TestResponseRanker:

    def test_rank_single_response(self):
        """Test ranking com apenas 1 resposta"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme NBR 12.211...',
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Qual é a norma para ETA?", responses)

        assert len(rankings) == 1
        assert rankings[0].agent_slug == 'agente-saneamento'
        assert rankings[0].score > 0.8

    def test_rank_multiple_responses(self):
        """Test ranking com múltiplas respostas"""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [
            Mock(text='{"rankings": [{"agent_slug": "agente-saneamento", "score": 0.95, "relevance": 0.95, "completeness": 0.90, "accuracy": 0.90, "reasoning": "Diretamente sobre ETA"}, {"agent_slug": "agente-energia", "score": 0.85, "relevance": 0.85, "completeness": 0.80, "accuracy": 0.85, "reasoning": "Sobre subestação, menos direto"}]}')
        ]

        with patch('orchestrator.response_ranker.anthropic.Anthropic') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.messages.create.return_value = mock_response

            ranker = ResponseRanker()

            responses = [
                AgentResponse(
                    agent_slug='agente-saneamento',
                    agent_name='Saneamento',
                    response_text='ETA: NBR 12.211 especifica...',
                    confidence=0.92,
                    sources=['NBR 12.211', 'Lei 14.026'],
                    latency_ms=2500
                ),
                AgentResponse(
                    agent_slug='agente-energia',
                    agent_name='Energia',
                    response_text='Subestação: ANEEL exige...',
                    confidence=0.85,
                    sources=['ANEEL', 'NBR 5422'],
                    latency_ms=3100
                )
            ]

            rankings = ranker.rank_responses(
                "Qual é a norma para ETA e subestação?",
                responses
            )

            # Deve ter 2 rankings
            assert len(rankings) == 2

            # Devem estar em ordem descending por score
            assert rankings[0].score >= rankings[1].score

# =============================================================================
# TESTES: Integration (Intent → Selector → Response)
# =============================================================================

class TestCAGIntegration:

    def test_e2e_simple_query(self, intent_classes, agent_pool):
        """Test fluxo completo para query simples"""
        classifier = IntentClassifier(intent_classes)
        selector = AgentSelector(agent_pool, intent_classes)

        query = "Qual é a norma para ETA?"

        # 1. Classificar
        prediction = classifier.classify(query)
        assert prediction.primary_intent == 'saneamento'

        # 2. Selecionar agentes
        agents = selector.select_agents(prediction)
        assert len(agents) > 0
        assert agents[0].agent_slug == 'agente-saneamento'

    def test_e2e_ambiguous_query(self, intent_classes, agent_pool):
        """Test fluxo completo para query ambígua"""
        classifier = IntentClassifier(intent_classes)
        selector = AgentSelector(agent_pool, intent_classes)

        query = "Saneamento com subestação: qual norma para ETA e impacto estrutural?"

        # 1. Classificar
        prediction = classifier.classify(query)
        assert 0.5 < prediction.confidence < 1.0

        # 2. Selecionar agentes
        agents = selector.select_agents(prediction)

        # Deve ter múltiplos agentes para query ambígua
        assert len(agents) >= 1

        # Verificar que scores são reasonáveis
        for agent in agents:
            assert 0.0 <= agent.score <= 1.0

# =============================================================================
# TESTES: Benchmark (performance)
# =============================================================================

class TestCAGPerformance:

    def test_classifier_latency(self, intent_classes):
        """Test latência do classifier"""
        import time
        classifier = IntentClassifier(intent_classes)

        query = "Saneamento com energia e portos"
        start = time.time()
        prediction = classifier.classify(query)
        elapsed_ms = (time.time() - start) * 1000

        # Deve ser rápido (< 200ms sem LLM API calls)
        assert elapsed_ms < 200
        print(f"Classifier latency: {elapsed_ms:.1f}ms")

    def test_selector_latency(self, intent_classes, agent_pool):
        """Test latência do selector"""
        import time
        selector = AgentSelector(agent_pool, intent_classes)

        from ml.intent_classifier import IntentPrediction
        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.9,
            secondary_intents=[('energia', 0.7)],
            keywords_matched=['ETA', 'LT'],
            embedding=[0.1] * 100
        )

        start = time.time()
        agents = selector.select_agents(prediction)
        elapsed_ms = (time.time() - start) * 1000

        # Deve ser muito rápido (< 10ms)
        assert elapsed_ms < 10
        assert len(agents) > 0
        print(f"Selector latency: {elapsed_ms:.1f}ms")

# =============================================================================
# MAIN (para rodar localmente)
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
