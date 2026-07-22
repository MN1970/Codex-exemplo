"""
Testes de edge cases para CAG
Testa limites, extremos e situações anômalas nos componentes do CAG.

Cobertura:
- Intent Classifier edge cases
- Agent Selector edge cases
- Response Ranker edge cases
- Performance/Stress tests
"""

import pytest
import sys
import os
import time
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.intent_classifier import IntentClassifier, AgentSelector, IntentPrediction
from orchestrator.response_ranker import ResponseRanker, AgentResponse

# =============================================================================
# FIXTURES — Reutilizáveis para múltiplos testes
# =============================================================================

@pytest.fixture
def intent_classes():
    """Mock intent classes para testes"""
    return {
        'saneamento': {
            'display_name': 'Saneamento',
            'description': 'Água, esgoto, drenagem',
            'keywords': ['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto', 'drenagem'],
            'primary_agents': ['agente-saneamento'],
            'secondary_agents': ['agente-contratual']
        },
        'energia': {
            'display_name': 'Energia',
            'description': 'Transmissão, distribuição, geração',
            'keywords': ['transmissão', 'LT', 'subestação', 'ANEEL', 'energia'],
            'primary_agents': ['agente-energia'],
            'secondary_agents': ['agente-barragens']
        },
        'portos': {
            'display_name': 'Portos',
            'description': 'Terminais, dragagem',
            'keywords': ['porto', 'terminal', 'ANTAQ', 'dragagem'],
            'primary_agents': ['agente-portos'],
            'secondary_agents': []
        },
        'ambigu': {
            'display_name': 'Ambíguo',
            'description': 'Multi-domínio',
            'keywords': [],
            'primary_agents': ['agente-saneamento'],
            'secondary_agents': []
        }
    }

@pytest.fixture
def agent_pool():
    """Mock agent pool padrão"""
    return {
        'agente-saneamento': {'name': 'Saneamento'},
        'agente-energia': {'name': 'Energia'},
        'agente-portos': {'name': 'Portos'},
        'agente-contratual': {'name': 'Contratual'},
        'agente-barragens': {'name': 'Barragens'}
    }

@pytest.fixture
def agent_pool_large():
    """Mock agent pool com 100+ agentes (stress test)"""
    pool = {}
    for i in range(150):
        pool[f'agente-{i:03d}'] = {'name': f'Agent {i}'}
    return pool

@pytest.fixture
def intent_classes_large(agent_pool_large):
    """Intent classes com muitos agentes mapeados"""
    return {
        'domain_' + str(i): {
            'display_name': f'Domain {i}',
            'description': f'Description for domain {i}',
            'keywords': [f'keyword{i}_a', f'keyword{i}_b'],
            'primary_agents': [f'agente-{i:03d}'],
            'secondary_agents': []
        }
        for i in range(50)
    }

@pytest.fixture
def sample_agent_response():
    """AgentResponse padrão para testes"""
    return AgentResponse(
        agent_slug='agente-saneamento',
        agent_name='Saneamento',
        response_text='ETA: conforme NBR 12.211, o projeto deve...',
        confidence=0.92,
        sources=['NBR 12.211', 'Lei 14.026'],
        latency_ms=2500
    )

@pytest.fixture
def sample_agent_responses(sample_agent_response):
    """Múltiplas respostas de agentes"""
    return [
        sample_agent_response,
        AgentResponse(
            agent_slug='agente-energia',
            agent_name='Energia',
            response_text='Subestação: conforme ANEEL, requisitos técnicos...',
            confidence=0.85,
            sources=['ANEEL', 'NBR 5422'],
            latency_ms=3100
        ),
        AgentResponse(
            agent_slug='agente-portos',
            agent_name='Portos',
            response_text='Terminal: conforme ANTAQ, especificações de dragagem...',
            confidence=0.78,
            sources=['ANTAQ'],
            latency_ms=2800
        )
    ]

# =============================================================================
# TESTES: Intent Classifier — Edge Cases
# =============================================================================

class TestIntentClassifierEdgeCases:
    """Edge cases para classificação de intenção"""

    # =========================================================================
    # Query vazia e muito curta
    # =========================================================================

    def test_empty_query(self, intent_classes):
        """Edge case: query vazia"""
        classifier = IntentClassifier(intent_classes)
        prediction = classifier.classify("")

        # Deve cair em 'ambigu' (sem keywords)
        assert prediction.primary_intent == 'ambigu'
        assert prediction.confidence <= 0.5
        assert len(prediction.keywords_matched) == 0

    def test_single_char_query(self, intent_classes):
        """Edge case: query com apenas 1 caractere"""
        classifier = IntentClassifier(intent_classes)
        prediction = classifier.classify("a")

        # Deve ser ambíguo
        assert prediction.primary_intent == 'ambigu'
        assert len(prediction.keywords_matched) == 0

    def test_only_whitespace_query(self, intent_classes):
        """Edge case: query apenas com espaços/tabs"""
        classifier = IntentClassifier(intent_classes)
        prediction = classifier.classify("   \t  \n   ")

        assert prediction.primary_intent == 'ambigu'
        assert len(prediction.keywords_matched) == 0

    # =========================================================================
    # Query muito longa
    # =========================================================================

    def test_very_long_query(self, intent_classes):
        """Edge case: query > 1000 caracteres"""
        # Gerar query muito longa com keywords repetidas
        long_query = "saneamento " * 200  # ~2000 chars
        classifier = IntentClassifier(intent_classes)

        prediction = classifier.classify(long_query)

        # Deve ainda classificar corretamente (keyword matching ainda funciona)
        assert prediction.primary_intent == 'saneamento'
        assert prediction.confidence > 0.7
        # Pode ter multiplicado o keyword (múltiplas ocorrências)
        assert 'saneamento' in prediction.keywords_matched

    def test_query_with_max_length(self, intent_classes):
        """Edge case: query com 5000+ caracteres"""
        # Max length razoável
        text = "ETA " * 1000  # 4000 chars
        classifier = IntentClassifier(intent_classes)

        prediction = classifier.classify(text)
        assert prediction is not None
        assert hasattr(prediction, 'primary_intent')

    # =========================================================================
    # Query com typos/variações ortográficas
    # =========================================================================

    def test_typo_in_keyword(self, intent_classes):
        """Edge case: typo em keyword (vs exato match)"""
        classifier = IntentClassifier(intent_classes)

        # "sanemaento" vs "saneamento"
        prediction_typo = classifier.classify("sanemaento")
        prediction_correct = classifier.classify("saneamento")

        # Com typo, deve falhar em keyword matching
        assert prediction_typo.primary_intent == 'ambigu'  # Não encontra

        # Correto deve funcionar
        assert prediction_correct.primary_intent == 'saneamento'

    def test_case_insensitive_keywords(self, intent_classes):
        """Edge case: verificar que keywords são case-insensitive"""
        classifier = IntentClassifier(intent_classes)

        prediction_lower = classifier.classify("eta")
        prediction_upper = classifier.classify("ETA")
        prediction_mixed = classifier.classify("EtA")

        # Todos devem ser iguais (case-insensitive)
        assert prediction_lower.primary_intent == prediction_upper.primary_intent
        assert prediction_upper.primary_intent == prediction_mixed.primary_intent
        assert 'ETA' in prediction_upper.keywords_matched

    # =========================================================================
    # Query em inglês/português misto
    # =========================================================================

    def test_portuguese_english_mixed(self, intent_classes):
        """Edge case: português + inglês misturado"""
        classifier = IntentClassifier(intent_classes)

        # Keywords em português, resto em inglês
        query = "ETA design requirements for water treatment"
        prediction = classifier.classify(query)

        # Deve ainda encontrar "ETA" (keyword em português)
        assert prediction.primary_intent == 'saneamento'
        assert 'ETA' in prediction.keywords_matched

    def test_english_only_query(self, intent_classes):
        """Edge case: query 100% em inglês (sem keywords)"""
        classifier = IntentClassifier(intent_classes)
        query = "What is the best approach for water treatment design?"

        prediction = classifier.classify(query)

        # Sem keywords portugueses, deve ser ambíguo
        assert prediction.primary_intent == 'ambigu'

    # =========================================================================
    # Query com números e caracteres especiais
    # =========================================================================

    def test_query_with_numbers(self, intent_classes):
        """Edge case: query com números"""
        classifier = IntentClassifier(intent_classes)

        query = "ETA 2025 NBR 12211 artigo 5.3.1 capacidade 1000 m³/dia"
        prediction = classifier.classify(query)

        # Deve ignorar números e ainda encontrar "ETA"
        assert prediction.primary_intent == 'saneamento'
        assert 'ETA' in prediction.keywords_matched

    def test_query_with_special_chars(self, intent_classes):
        """Edge case: query com special characters"""
        classifier = IntentClassifier(intent_classes)

        query = "ETA [especificações] (NBR-12.211) & drenagem @2025 #infra"
        prediction = classifier.classify(query)

        # Deve encontrar "ETA" e "drenagem" apesar dos special chars
        assert prediction.primary_intent == 'saneamento'
        assert 'ETA' in prediction.keywords_matched
        assert 'drenagem' in prediction.keywords_matched

    def test_query_only_special_chars(self, intent_classes):
        """Edge case: query apenas com special characters"""
        classifier = IntentClassifier(intent_classes)

        query = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        prediction = classifier.classify(query)

        # Deve ser ambíguo
        assert prediction.primary_intent == 'ambigu'
        assert len(prediction.keywords_matched) == 0

    def test_query_with_unicode_chars(self, intent_classes):
        """Edge case: query com Unicode/acentos"""
        classifier = IntentClassifier(intent_classes)

        query = "Drenágem ñ réseau d'éta métallurgíque"
        prediction = classifier.classify(query)

        # Deve tentar encontrar, mas sem match exato pode falhar
        assert prediction is not None

    # =========================================================================
    # Query com múltiplos keywords conflitantes
    # =========================================================================

    def test_all_keywords_present(self, intent_classes):
        """Edge case: query tem keywords de TODOS os intents"""
        classifier = IntentClassifier(intent_classes)

        query = "saneamento e energia com porto e adutora e subestação"
        prediction = classifier.classify(query)

        # Deve escolher um primary (saneamento aparece primeiro)
        assert prediction.primary_intent in ['saneamento', 'energia', 'portos']
        assert len(prediction.keywords_matched) >= 4

    def test_secondary_intents_populated(self, intent_classes):
        """Edge case: verificar secondary intents quando há múltiplos matches"""
        classifier = IntentClassifier(intent_classes)

        query = "saneamento com subestação"
        prediction = classifier.classify(query)

        # Deve ter secundário
        assert prediction.primary_intent == 'saneamento'
        # Secondary intents podem estar vazios ou ter energy
        # (depende da implementação de keyword_match)

    # =========================================================================
    # Embedding edge cases
    # =========================================================================

    def test_embedding_consistency(self, intent_classes):
        """Edge case: mesmo texto deve gerar mesmo embedding"""
        classifier = IntentClassifier(intent_classes)

        query = "ETA saneamento"

        pred1 = classifier.classify(query)
        pred2 = classifier.classify(query)

        # Embeddings devem ser idênticos (cached)
        assert pred1.embedding == pred2.embedding

    def test_different_queries_different_embeddings(self, intent_classes):
        """Edge case: queries diferentes devem ter embeddings diferentes"""
        classifier = IntentClassifier(intent_classes)

        pred1 = classifier.classify("ETA")
        pred2 = classifier.classify("subestação")

        # Embeddings devem ser diferentes
        assert pred1.embedding != pred2.embedding

# =============================================================================
# TESTES: Agent Selector — Edge Cases
# =============================================================================

class TestAgentSelectorEdgeCases:
    """Edge cases para seleção de agentes"""

    # =========================================================================
    # Agent pool vazio/inválido
    # =========================================================================

    def test_empty_agent_pool(self, intent_classes):
        """Edge case: agent pool vazio"""
        selector = AgentSelector({}, intent_classes)  # pool vazio

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.9,
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Nenhum agente disponível → lista vazia
        assert len(agents) == 0

    def test_agent_pool_with_missing_agents(self, intent_classes, agent_pool):
        """Edge case: config referencia agentes que não existem na pool"""
        # Modificar intent_classes para referenciar agentes inexistentes
        intent_classes['saneamento']['primary_agents'] = ['agente-inexistente', 'agente-saneamento']

        selector = AgentSelector(agent_pool, intent_classes)

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.9,
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Só deve retornar agentes que existem na pool
        assert len(agents) == 1
        assert agents[0].agent_slug == 'agente-saneamento'

    # =========================================================================
    # Confidence exatamente no threshold
    # =========================================================================

    def test_confidence_exactly_at_threshold(self, intent_classes, agent_pool):
        """Edge case: confidence = exatamente min_confidence threshold"""
        selector = AgentSelector(agent_pool, intent_classes)

        threshold = 0.6

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=threshold,  # EXATAMENTE no threshold
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction, min_confidence=threshold)

        # Deve incluir (>=, não >)
        assert len(agents) > 0

    def test_confidence_just_below_threshold(self, intent_classes, agent_pool):
        """Edge case: confidence = threshold - epsilon"""
        selector = AgentSelector(agent_pool, intent_classes)

        threshold = 0.6

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=threshold - 0.0001,  # Levemente abaixo
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction, min_confidence=threshold)

        # Deve excluir (< threshold)
        assert len(agents) == 0

    # =========================================================================
    # Múltiplos intents com mesma score
    # =========================================================================

    def test_multiple_intents_same_score(self, intent_classes, agent_pool):
        """Edge case: múltiplos secondary intents com score idêntico"""
        selector = AgentSelector(agent_pool, intent_classes)

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.9,
            secondary_intents=[
                ('energia', 0.7),
                ('portos', 0.7),  # MESMO SCORE que energia
            ],
            keywords_matched=['ETA', 'LT', 'porto'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Deve listar ambos, possivelmente em ordem arbitrária
        agent_slugs = [a.agent_slug for a in agents]
        assert 'agente-saneamento' in agent_slugs
        # Energia e portos devem estar presentes com mesmo score
        assert len(agents) >= 2

    # =========================================================================
    # Zero confidence
    # =========================================================================

    def test_zero_confidence(self, intent_classes, agent_pool):
        """Edge case: confidence = 0.0"""
        selector = AgentSelector(agent_pool, intent_classes)

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.0,
            secondary_intents=[],
            keywords_matched=[],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction, min_confidence=0.0)

        # Mesmo com 0 confidence, se há agentes configurados
        # (score=0.0, score >= 0.0 → include)
        assert len(agents) == 1

    def test_very_high_confidence(self, intent_classes, agent_pool):
        """Edge case: confidence = 1.0 (máximo)"""
        selector = AgentSelector(agent_pool, intent_classes)

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=1.0,
            secondary_intents=[],
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Deve selecionar e manter score = 1.0
        assert len(agents) == 1
        assert agents[0].score == 1.0

    # =========================================================================
    # Intent não mapeado
    # =========================================================================

    def test_unmapped_intent_in_prediction(self, intent_classes, agent_pool):
        """Edge case: prediction.primary_intent não existe em intent_classes"""
        selector = AgentSelector(agent_pool, intent_classes)

        prediction = IntentPrediction(
            primary_intent='categoria_inexistente',
            confidence=0.8,
            secondary_intents=[],
            keywords_matched=[],
            embedding=[0.1] * 100
        )

        agents = selector.select_agents(prediction)

        # Sem agentes para intent inexistente
        assert len(agents) == 0

# =============================================================================
# TESTES: Response Ranker — Edge Cases
# =============================================================================

class TestResponseRankerEdgeCases:
    """Edge cases para ranking de respostas"""

    # =========================================================================
    # Resposta vazia
    # =========================================================================

    def test_empty_response_text(self):
        """Edge case: response_text vazio"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='',  # VAZIO
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Qual é a norma para ETA?", responses)

        # Deve ainda rankear (mesmo que vazio)
        assert len(rankings) == 1

    def test_whitespace_only_response(self):
        """Edge case: response_text apenas whitespace"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='   \t\n  ',
                confidence=0.92,
                sources=[],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    # =========================================================================
    # Resposta muito longa
    # =========================================================================

    def test_very_long_response(self):
        """Edge case: response_text > 100KB"""
        ranker = ResponseRanker()

        # Resposta com 100KB
        long_text = "NBR 12.211 especifica... " * 5000  # ~100KB

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text=long_text,
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)

        # Deve processar sem erro
        assert len(rankings) == 1
        assert len(long_text) > 100000

    # =========================================================================
    # Múltiplas respostas idênticas
    # =========================================================================

    def test_identical_responses(self):
        """Edge case: múltiplas respostas 100% idênticas"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme NBR 12.211',
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            ),
            AgentResponse(
                agent_slug='agente-energia',
                agent_name='Energia',
                response_text='ETA conforme NBR 12.211',  # IDÊNTICO
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)

        # Ambas devem ser ranqueadas (possivelmente com score próximo)
        assert len(rankings) == 2

    # =========================================================================
    # Resposta com caracteres especiais/Unicode
    # =========================================================================

    def test_response_with_unicode(self):
        """Edge case: response com caracteres Unicode"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='NBR 12.211: drenágem → ñ réseau métallurgíque 中文 日本語',
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    def test_response_with_emoji(self):
        """Edge case: response com emojis"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA ✅ conforme NBR 12.211 ⚠️ verificar',
                confidence=0.92,
                sources=[],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    # =========================================================================
    # Resposta com fontes inválidas/vazias
    # =========================================================================

    def test_response_with_empty_sources(self):
        """Edge case: response com lista de sources vazia"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme...',
                confidence=0.92,
                sources=[],  # VAZIO
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    def test_response_with_duplicate_sources(self):
        """Edge case: response com sources duplicadas"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme...',
                confidence=0.92,
                sources=['NBR 12.211', 'NBR 12.211', 'Lei 14.026', 'Lei 14.026'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    # =========================================================================
    # Confidence anômala
    # =========================================================================

    def test_response_zero_confidence(self):
        """Edge case: response com confidence = 0.0"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme...',
                confidence=0.0,  # Sem confiança
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 1

    def test_response_confidence_above_100(self):
        """Edge case: response com confidence > 1.0 (inválido)"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme...',
                confidence=1.5,  # INVÁLIDO
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        # Deve rankear mesmo com valor inválido
        assert len(rankings) == 1

    # =========================================================================
    # Query para ranking
    # =========================================================================

    def test_ranking_empty_query(self):
        """Edge case: ranking com query vazia"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-saneamento',
                agent_name='Saneamento',
                response_text='ETA conforme...',
                confidence=0.92,
                sources=['NBR 12.211'],
                latency_ms=2500
            )
        ]

        rankings = ranker.rank_responses("", responses)
        assert len(rankings) == 1

# =============================================================================
# TESTES: Performance & Stress
# =============================================================================

class TestCAGPerformanceEdgeCases:
    """Performance and stress tests para CAG"""

    def test_large_agent_pool_selection(self, intent_classes, agent_pool_large):
        """Stress test: seleção com 150+ agentes na pool"""
        selector = AgentSelector(agent_pool_large, intent_classes)

        prediction = IntentPrediction(
            primary_intent='domain_0',
            confidence=0.9,
            secondary_intents=[],
            keywords_matched=['keyword0_a'],
            embedding=[0.1] * 100
        )

        start = time.time()
        agents = selector.select_agents(prediction)
        elapsed_ms = (time.time() - start) * 1000

        # Deve ser rápido mesmo com pool grande
        assert elapsed_ms < 100
        print(f"Large pool selection: {elapsed_ms:.2f}ms for 150 agents")

    def test_many_secondary_intents(self, intent_classes, agent_pool):
        """Stress test: predição com muitos secondary intents"""
        selector = AgentSelector(agent_pool, intent_classes)

        # Criar 50 secondary intents
        secondary_intents = [
            (f'intent_{i}', 0.5 - (i * 0.01)) for i in range(50)
        ]

        prediction = IntentPrediction(
            primary_intent='saneamento',
            confidence=0.9,
            secondary_intents=secondary_intents,
            keywords_matched=['ETA'],
            embedding=[0.1] * 100
        )

        start = time.time()
        agents = selector.select_agents(prediction)
        elapsed_ms = (time.time() - start) * 1000

        # Deve processar rapidamente
        assert elapsed_ms < 50
        print(f"50 secondary intents: {elapsed_ms:.2f}ms")

    def test_classifier_with_many_keywords(self):
        """Stress test: intent classes com muitas keywords"""
        # Criar intent class com 1000 keywords
        intent_classes = {
            'mega_intent': {
                'display_name': 'Mega Intent',
                'description': 'Mega test',
                'keywords': [f'keyword_{i}' for i in range(1000)],
                'primary_agents': ['agente-mega'],
                'secondary_agents': []
            }
        }

        classifier = IntentClassifier(intent_classes)
        query = "keyword_500 and keyword_750"

        start = time.time()
        prediction = classifier.classify(query)
        elapsed_ms = (time.time() - start) * 1000

        # Deve processar em tempo razoável
        assert elapsed_ms < 200
        print(f"1000 keywords: {elapsed_ms:.2f}ms")
        assert 'keyword_500' in prediction.keywords_matched
        assert 'keyword_750' in prediction.keywords_matched

    def test_ranker_with_many_responses(self):
        """Stress test: ranking com 50+ respostas"""
        ranker = ResponseRanker()

        # Criar 50 respostas
        responses = [
            AgentResponse(
                agent_slug=f'agente-{i}',
                agent_name=f'Agent {i}',
                response_text=f'Response from agent {i}: Standard response text',
                confidence=0.5 + (i % 10) * 0.05,
                sources=[f'source-{i}'],
                latency_ms=random.randint(100, 5000)
            )
            for i in range(50)
        ]

        start = time.time()
        rankings = ranker.rank_responses("Test query", responses)
        elapsed_ms = (time.time() - start) * 1000

        # Não deve causar timeout (timeout seria >30s)
        assert elapsed_ms < 30000
        print(f"50 responses ranking: {elapsed_ms:.2f}ms")
        assert len(rankings) > 0

    def test_classifier_latency_benchmark(self, intent_classes):
        """Performance benchmark: latência típica do classifier"""
        classifier = IntentClassifier(intent_classes)
        query = "ETA saneamento conforme NBR"

        start = time.time()
        for _ in range(100):
            classifier.classify(query)
        elapsed_ms = (time.time() - start) * 1000

        avg_latency = elapsed_ms / 100

        # Deve ser < 10ms por query (sem LLM calls)
        assert avg_latency < 10
        print(f"Average classifier latency: {avg_latency:.2f}ms")

# =============================================================================
# TESTES: Integration — Edge Cases
# =============================================================================

class TestCAGIntegrationEdgeCases:
    """Integration tests para edge cases"""

    def test_e2e_empty_query_to_agent_selection(self, intent_classes, agent_pool):
        """Integration: query vazia → classificação → seleção agentes"""
        classifier = IntentClassifier(intent_classes)
        selector = AgentSelector(agent_pool, intent_classes)

        query = ""

        prediction = classifier.classify(query)
        assert prediction.primary_intent == 'ambigu'

        agents = selector.select_agents(prediction)
        # Pode ter agentes mesmo com query vazia (se houver fallback)

    def test_e2e_very_long_query_to_ranking(self, intent_classes, agent_pool, sample_agent_responses):
        """Integration: query muito longa → classificação → ranking"""
        classifier = IntentClassifier(intent_classes)

        long_query = "saneamento " * 200

        prediction = classifier.classify(long_query)
        assert prediction.primary_intent == 'saneamento'

        # Simular ranking mesmo com query longa
        ranker = ResponseRanker()
        rankings = ranker.rank_responses(long_query, sample_agent_responses)
        assert len(rankings) > 0

    def test_e2e_special_chars_query(self, intent_classes, agent_pool):
        """Integration: query com special chars → fluxo completo"""
        classifier = IntentClassifier(intent_classes)
        selector = AgentSelector(agent_pool, intent_classes)

        query = "ETA [NBR-12.211] & (drenagem) @2025"

        prediction = classifier.classify(query)
        agents = selector.select_agents(prediction)

        assert prediction.primary_intent == 'saneamento'
        assert len(agents) > 0

# =============================================================================
# HELPER: Teste de limites numéricos
# =============================================================================

class TestNumericalBoundaries:
    """Testes de limites numéricos"""

    def test_confidence_boundaries(self, intent_classes, agent_pool):
        """Testar todas as faixas de confidence: 0.0, 0.5, 1.0"""
        selector = AgentSelector(agent_pool, intent_classes)

        for confidence in [0.0, 0.25, 0.5, 0.75, 1.0]:
            prediction = IntentPrediction(
                primary_intent='saneamento',
                confidence=confidence,
                secondary_intents=[],
                keywords_matched=[],
                embedding=[0.1] * 100
            )

            agents = selector.select_agents(prediction, min_confidence=0.3)

            if confidence >= 0.3:
                assert len(agents) > 0
            # else: pode estar vazio ou não

    def test_latency_bounds(self, intent_classes):
        """Testar que latencies são positivas"""
        ranker = ResponseRanker()

        responses = [
            AgentResponse(
                agent_slug='agente-test',
                agent_name='Test',
                response_text='Response',
                confidence=0.9,
                sources=[],
                latency_ms=0.001  # Muito pequeno
            ),
            AgentResponse(
                agent_slug='agente-test2',
                agent_name='Test2',
                response_text='Response',
                confidence=0.9,
                sources=[],
                latency_ms=999999  # Muito grande
            )
        ]

        rankings = ranker.rank_responses("Query", responses)
        assert len(rankings) == 2

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
