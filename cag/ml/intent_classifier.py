"""
CAG Intent Classifier — Classifica query do usuário em intenção de domínio
Versão: 1.0 (prototipagem com keyword matching + Claude embeddings)
Ticket: MNT-2026-CAG-ML
"""

import json
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import anthropic

# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class IntentPrediction:
    """Resultado da classificação de intenção"""
    primary_intent: str  # 'saneamento', 'energia', etc.
    confidence: float  # 0-1.0
    secondary_intents: List[Tuple[str, float]]  # [(intent, confidence), ...]
    keywords_matched: List[str]
    embedding: List[float]  # para análise posterior
    cache_hit: bool = False

@dataclass
class AgentScore:
    """Score de um agente para uma intenção"""
    agent_slug: str
    score: float  # 0-1.0
    reason: str  # ex: "primary agent for saneamento"

# =============================================================================
# INTENT CLASSIFIER
# =============================================================================

class IntentClassifier:
    """
    Classifica intenção usando:
    1. Keyword matching (fast, determinístico)
    2. Claude embeddings (slow, semântico)
    3. Hybrid scoring
    """

    def __init__(self, intent_classes: Dict, threshold: float = 0.6):
        """
        Args:
            intent_classes: dict de {intent_label: IntentClass}
            threshold: confiança mínima para incluir como secondary
        """
        self.intent_classes = intent_classes
        self.threshold = threshold
        self.client = anthropic.Anthropic()
        self._embedding_cache = {}  # cache de embeddings locais

    def classify(self, query: str) -> IntentPrediction:
        """
        Classifica query em intenção de domínio.

        Fluxo:
        1. Keyword matching → fast intents
        2. Claude embedding → semântico
        3. Hybrid score → resultado final
        """

        # =====================================================================
        # PASSO 1: KEYWORD MATCHING (fast path)
        # =====================================================================
        keyword_matches = self._keyword_match(query)

        if keyword_matches:
            primary_intent = keyword_matches[0][0]  # intent com mais keywords
            primary_confidence = keyword_matches[0][1]
            secondary_intents = keyword_matches[1:]
        else:
            primary_intent = 'ambigu'
            primary_confidence = 0.5
            secondary_intents = []

        # =====================================================================
        # PASSO 2: SEMANTIC EMBEDDING (LLM-based)
        # =====================================================================
        embedding = self._get_embedding(query)

        # Rerank com embedding (futura: fine-tuning com classifier dedicado)
        semantic_score = self._semantic_score(
            query,
            primary_intent,
            embedding
        )

        # Blend: 70% keyword + 30% semantic
        final_confidence = 0.7 * primary_confidence + 0.3 * semantic_score

        return IntentPrediction(
            primary_intent=primary_intent,
            confidence=min(final_confidence, 1.0),
            secondary_intents=secondary_intents,
            keywords_matched=list(set(
                self._extract_keywords(query)
            )),
            embedding=embedding,
            cache_hit=False
        )

    # =========================================================================
    # PRIVATE: Keyword Matching
    # =========================================================================

    def _keyword_match(self, query: str) -> List[Tuple[str, float]]:
        """
        Busca keywords em intent_classes e retorna ranking.

        Returns:
            [(intent, confidence), ...] ordenado por confiança
        """
        matches = {}
        query_lower = query.lower()

        for intent_label, intent_class in self.intent_classes.items():
            keywords = intent_class.get('keywords', [])
            matches_count = sum(
                1 for kw in keywords
                if kw.lower() in query_lower
            )

            if matches_count > 0:
                # Confidence = (keywords matched) / (total keywords)
                confidence = min(matches_count / max(len(keywords), 1), 1.0)
                matches[intent_label] = confidence

        # Sort by confidence descending
        return sorted(
            matches.items(),
            key=lambda x: x[1],
            reverse=True
        )

    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai keywords do usuário encontrados em qualquer intent"""
        query_lower = query.lower()
        found_keywords = []

        for intent_class in self.intent_classes.values():
            for kw in intent_class.get('keywords', []):
                if kw.lower() in query_lower:
                    found_keywords.append(kw)

        return found_keywords

    # =========================================================================
    # PRIVATE: Semantic Scoring (Claude Embeddings)
    # =========================================================================

    def _get_embedding(self, text: str) -> List[float]:
        """
        Gera embedding via Claude API (real implementation).
        Nota: Anthropic API não tem endpoint de embedding ainda (2026-07-22).
        Esta é uma stub que retorna vector mock.

        Futura: usar Anthropic Embeddings API quando disponível,
        ou integrar com OpenAI Embeddings / Hugging Face.
        """
        # TODO: Substituir por real embedding API quando disponível
        cache_key = hashlib.sha256(text.encode()).hexdigest()

        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        # STUB: mock embedding (1536 dims como OpenAI)
        import hashlib
        seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % 10000
        import random
        random.seed(seed)
        embedding = [random.gauss(0, 1) for _ in range(1536)]

        # Normalize
        norm = (sum(x**2 for x in embedding) ** 0.5)
        embedding = [x / norm for x in embedding]

        self._embedding_cache[cache_key] = embedding
        return embedding

    def _semantic_score(
        self,
        query: str,
        primary_intent: str,
        embedding: List[float]
    ) -> float:
        """
        Usa Claude para dar um "segundo voto" na classificação.

        Prompt: "Dada a query [query], qual segmento técnico tem mais afinidade?"
        Retorna: confiança 0-1.0
        """
        # Construir descrições dos intents
        intent_descriptions = "\n".join([
            f"- {label}: {ic.get('display_name')} — {ic.get('description')}"
            for label, ic in self.intent_classes.items()
        ])

        prompt = f"""Você é um classificador de intenções para projetos de infraestrutura.

Segmentos disponíveis:
{intent_descriptions}

Query do usuário: "{query}"

Qual segmento técnico é mais apropriado para esta query?
Responda em JSON:
{{
    "intent": "<intent_label>",
    "confidence": <0.0 a 1.0>,
    "reasoning": "<breve explicação>"
}}
"""

        # TODO: chamar Claude API com token caching (se disponível)
        # Por enquanto, retornar 0.5 (neutro)
        return 0.5

# =============================================================================
# AGENT SELECTOR (usa IntentPrediction para escolher agentes)
# =============================================================================

class AgentSelector:
    """
    Dado uma IntentPrediction, seleciona quais agentes vão responder.
    """

    def __init__(self, agent_pool: Dict, intent_classes: Dict):
        """
        Args:
            agent_pool: dict de {agent_slug: AgentConfig}
            intent_classes: dict de {intent_label: IntentClass}
        """
        self.agent_pool = agent_pool
        self.intent_classes = intent_classes

    def select_agents(
        self,
        prediction: IntentPrediction,
        min_confidence: float = 0.6
    ) -> List[AgentScore]:
        """
        Seleciona agentes baseado na IntentPrediction.

        Estratégia:
        1. Pega primary intent → seleciona primary_agents
        2. Se confidence > 0.8, para aqui
        3. Se confidence < 0.8, adiciona secondary_agents
        4. Se houver secondary_intents, adiciona agentes deles também

        Returns:
            Agentes ordenados por score (descending)
        """
        selected = {}

        # =====================================================================
        # PASSO 1: Primary agents (primary intent)
        # =====================================================================
        primary_intent_class = self.intent_classes.get(
            prediction.primary_intent,
            {}
        )
        primary_agents = primary_intent_class.get('primary_agents', [])

        for agent_slug in primary_agents:
            if agent_slug in self.agent_pool:
                selected[agent_slug] = AgentScore(
                    agent_slug=agent_slug,
                    score=prediction.confidence,
                    reason=f"primary agent for {prediction.primary_intent}"
                )

        # =====================================================================
        # PASSO 2: Secondary agents (se low confidence ou multiple intents)
        # =====================================================================
        if prediction.confidence < 0.8 or prediction.secondary_intents:
            secondary_agents = primary_intent_class.get(
                'secondary_agents',
                []
            )
            for agent_slug in secondary_agents:
                if agent_slug not in selected and agent_slug in self.agent_pool:
                    selected[agent_slug] = AgentScore(
                        agent_slug=agent_slug,
                        score=prediction.confidence * 0.7,  # Penalizar secondary
                        reason=f"secondary agent for {prediction.primary_intent}"
                    )

            # Secondary intents
            for sec_intent, sec_confidence in prediction.secondary_intents:
                sec_intent_class = self.intent_classes.get(sec_intent, {})
                sec_primary = sec_intent_class.get('primary_agents', [])
                for agent_slug in sec_primary:
                    if agent_slug not in selected and agent_slug in self.agent_pool:
                        selected[agent_slug] = AgentScore(
                            agent_slug=agent_slug,
                            score=sec_confidence * 0.8,
                            reason=f"primary agent for secondary intent {sec_intent}"
                        )

        # =====================================================================
        # PASSO 3: Filter por min_confidence e sort
        # =====================================================================
        filtered = [
            agent for agent in selected.values()
            if agent.score >= min_confidence
        ]

        # Sort by score descending
        return sorted(filtered, key=lambda a: a.score, reverse=True)

# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Mock intent classes
    intent_classes = {
        'saneamento': {
            'display_name': 'Saneamento',
            'description': 'Água, esgoto, drenagem',
            'keywords': ['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto'],
            'primary_agents': ['agente-saneamento'],
            'secondary_agents': ['agente-energia', 'agente-contratual']
        },
        'energia': {
            'display_name': 'Energia',
            'description': 'Transmissão, distribuição, geração',
            'keywords': ['transmissão', 'LT', 'subestação', 'ANEEL'],
            'primary_agents': ['agente-energia'],
            'secondary_agents': ['agente-barragens', 'agente-contratual']
        }
    }

    agent_pool = {
        'agente-saneamento': {},
        'agente-energia': {},
        'agente-contratual': {}
    }

    # Classificar query
    classifier = IntentClassifier(intent_classes)
    query = "Estou fazendo um projeto de saneamento com uma subestação de energia. Qual é a norma?"

    prediction = classifier.classify(query)
    print(f"Query: {query}")
    print(f"Primary intent: {prediction.primary_intent} (confidence: {prediction.confidence:.2f})")
    print(f"Secondary intents: {prediction.secondary_intents}")
    print(f"Keywords matched: {prediction.keywords_matched}")

    # Selecionar agentes
    selector = AgentSelector(agent_pool, intent_classes)
    agents = selector.select_agents(prediction)
    print(f"\nSelected agents:")
    for agent in agents:
        print(f"  - {agent.agent_slug}: {agent.score:.2f} ({agent.reason})")
