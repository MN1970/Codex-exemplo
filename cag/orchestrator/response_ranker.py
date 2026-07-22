"""
CAG Response Ranker — Compara respostas de múltiplos agentes e rankeia
Versão: 1.0
Ticket: MNT-2026-CAG-ML
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import anthropic

# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class AgentResponse:
    """Resposta de um agente"""
    agent_slug: str
    agent_name: str
    response_text: str
    confidence: float  # confiança do agente na resposta (0-1.0)
    sources: List[str]  # documentos RAG usados
    latency_ms: float  # quanto tempo levou

@dataclass
class RankedResponse:
    """Resposta ranqueada"""
    rank: int  # 1, 2, 3, ...
    agent_slug: str
    score: float  # 0-1.0: quanto ajuda responder a query
    relevance: float  # 0-1.0: relevância para a query
    completeness: float  # 0-1.0: cobre todos aspectos?
    accuracy: float  # 0-1.0: provavelmente correto?
    reasoning: str  # por quê este ranking?

# =============================================================================
# RESPONSE RANKER
# =============================================================================

class ResponseRanker:
    """
    Dado uma query + N respostas de agentes, rankeia qual é melhor.

    Usa Claude como juiz (LLM-as-a-judge) para avaliar:
    - Relevância da resposta
    - Completude (cobre todos aspectos da query?)
    - Acurácia (provavelmente correto?)
    - Integrabilidade com outras respostas
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def rank_responses(
        self,
        query: str,
        responses: List[AgentResponse]
    ) -> List[RankedResponse]:
        """
        Rankeia respostas de agentes.

        Estratégia:
        1. Prompt único para Claude comparar todas as respostas
        2. Claude retorna score para cada uma (0-1.0)
        3. Retorna em ordem descending

        Args:
            query: pergunta original do usuário
            responses: List[AgentResponse] das respostas dos agentes

        Returns:
            List[RankedResponse] ordenado por score (descending)
        """

        if not responses:
            return []

        if len(responses) == 1:
            # Se houver apenas 1 resposta, ela vence
            return [
                RankedResponse(
                    rank=1,
                    agent_slug=responses[0].agent_slug,
                    score=0.9,  # assume que é boa
                    relevance=0.9,
                    completeness=0.85,
                    accuracy=0.85,
                    reasoning="single response"
                )
            ]

        # =====================================================================
        # PASSO 1: Preparar prompt para Claude (LLM-as-a-judge)
        # =====================================================================
        responses_text = "\n".join([
            f"## Agente: {resp.agent_slug} (confiança: {resp.confidence:.2f})\n"
            f"{resp.response_text}\n"
            f"Fontes: {', '.join(resp.sources)}\n"
            f"---"
            for resp in responses
        ])

        prompt = f"""Você é um juiz de qualidade para respostas técnicas sobre infraestrutura.

Query do usuário:
"{query}"

Respostas de múltiplos agentes:
{responses_text}

Analise cada resposta considerando:
1. **Relevância**: quanto a resposta endereça a query original?
2. **Completude**: cobre todos os aspectos/perguntas implícitas?
3. **Acurácia**: provavelmente está correto? Usa normas/referencias válidas?
4. **Integração**: pode ser combinada com outras respostas?

Retorne um JSON com score para cada agente:
{{
    "rankings": [
        {{
            "agent_slug": "<agente>",
            "score": <0.0-1.0>,
            "relevance": <0.0-1.0>,
            "completeness": <0.0-1.0>,
            "accuracy": <0.0-1.0>,
            "reasoning": "<breve explicação>"
        }},
        ...
    ]
}}

IMPORTANTE: Retorne VÁLIDO JSON, sem markdown code blocks."""

        # =====================================================================
        # PASSO 2: Chamar Claude para rankear
        # =====================================================================
        try:
            response = self.client.messages.create(
                model="claude-opus-4-8",  # Usar Opus para melhor julgamento
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse resposta
            response_text = response.content[0].text
            result = json.loads(response_text)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Erro ao parsear ranking: {e}")
            # Fallback: ranking simples por confiança
            result = self._fallback_ranking(responses)

        # =====================================================================
        # PASSO 3: Converter para RankedResponse e ordenar
        # =====================================================================
        ranked = []
        for idx, item in enumerate(result.get('rankings', []), start=1):
            ranked.append(
                RankedResponse(
                    rank=idx,
                    agent_slug=item.get('agent_slug'),
                    score=item.get('score', 0.0),
                    relevance=item.get('relevance', 0.0),
                    completeness=item.get('completeness', 0.0),
                    accuracy=item.get('accuracy', 0.0),
                    reasoning=item.get('reasoning', '')
                )
            )

        # Sort by score descending
        return sorted(ranked, key=lambda r: r.score, reverse=True)

    def _fallback_ranking(self, responses: List[AgentResponse]) -> Dict:
        """Fallback ranking se Claude não conseguir responder."""
        return {
            'rankings': [
                {
                    'agent_slug': resp.agent_slug,
                    'score': resp.confidence,
                    'relevance': resp.confidence,
                    'completeness': resp.confidence * 0.8,
                    'accuracy': resp.confidence * 0.8,
                    'reasoning': 'fallback ranking (based on agent confidence)'
                }
                for resp in responses
            ]
        }

# =============================================================================
# RESPONSE SYNTHESIZER
# =============================================================================

class ResponseSynthesizer:
    """
    Sintetiza múltiplas respostas ranqueadas em uma resposta final integrada.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def synthesize(
        self,
        query: str,
        ranked_responses: List[RankedResponse],
        agent_responses: Dict[str, AgentResponse]  # {agent_slug: response}
    ) -> str:
        """
        Cria resposta final integrada.

        Estratégia:
        1. Toma top-2 respostas ranqueadas
        2. Prompt Claude para integrar/combinar
        3. Mantém citações de fontes

        Args:
            query: pergunta original
            ranked_responses: List[RankedResponse] já ranqueada
            agent_responses: Dict mapping agent_slug → full response

        Returns:
            Resposta final integrada como string
        """

        if not ranked_responses:
            return "Nenhuma resposta disponível."

        # Pegar top-2 respostas
        top_responses = ranked_responses[:2]

        # Construir contexto para síntese
        responses_context = ""
        for ranked in top_responses:
            agent_slug = ranked.agent_slug
            agent_resp = agent_responses.get(agent_slug)
            if agent_resp:
                responses_context += f"""
## {agent_resp.agent_name} (score: {ranked.score:.2f})
{agent_resp.response_text}
Fontes: {', '.join(agent_resp.sources)}

---
"""

        prompt = f"""Você é um redator técnico especializado em integrar respostas de múltiplos especialistas.

Query original do usuário:
"{query}"

Respostas de especialistas:
{responses_context}

Integre as respostas acima em uma resposta única, coerente e bem estruturada que:
1. Combine insights de ambos especialistas
2. Mantenha as citações de fontes (NBR, Lei, etc.)
3. Seja clara e concisa
4. Indique qual especialista foi consultado para cada seção
5. Destaque recomendações de integração (se aplicável)

Responda apenas com a resposta integrada, sem prefácios."""

        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

# =============================================================================
# ORQUESTRADOR CAG (integra tudo)
# =============================================================================

class CAGOrchestrator:
    """
    Orquestrador CAG: intent → agentes → respostas → rank → síntese.
    """

    def __init__(self):
        self.ranker = ResponseRanker()
        self.synthesizer = ResponseSynthesizer()

    async def orchestrate(
        self,
        query: str,
        selected_agents: List[str],  # agent slugs selecionados
        agent_responses_dict: Dict[str, AgentResponse]  # respostas dos agentes
    ) -> Dict:
        """
        Orquestra ranking e síntese.

        Returns:
            {
                'query': original query,
                'selected_agents': agentes usados,
                'rankings': List[RankedResponse],
                'final_response': resposta sintetizada,
                'sources': lista de fontes combinadas
            }
        """

        # Converter responses dict para list
        agent_responses = [
            agent_responses_dict[slug]
            for slug in selected_agents
            if slug in agent_responses_dict
        ]

        # Rankear
        rankings = self.ranker.rank_responses(query, agent_responses)

        # Sintetizar
        final_response = self.synthesizer.synthesize(
            query,
            rankings,
            agent_responses_dict
        )

        # Agregar fontes
        all_sources = set()
        for resp in agent_responses:
            all_sources.update(resp.sources)

        return {
            'query': query,
            'selected_agents': selected_agents,
            'rankings': [
                {
                    'rank': r.rank,
                    'agent': r.agent_slug,
                    'score': r.score,
                    'relevance': r.relevance,
                    'completeness': r.completeness,
                    'accuracy': r.accuracy,
                    'reasoning': r.reasoning
                }
                for r in rankings
            ],
            'final_response': final_response,
            'sources': list(all_sources)
        }

# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Mock responses
    responses = [
        AgentResponse(
            agent_slug="agente-saneamento",
            agent_name="Saneamento",
            response_text="ETA: conforme NBR 12.211, o projeto deve...",
            confidence=0.92,
            sources=["NBR 12.211", "Lei 14.026"],
            latency_ms=2500
        ),
        AgentResponse(
            agent_slug="agente-energia",
            agent_name="Energia",
            response_text="Subestação: conforme ANEEL, o projeto requer...",
            confidence=0.85,
            sources=["ANEEL", "NBR 5422"],
            latency_ms=3100
        )
    ]

    ranker = ResponseRanker()
    query = "Qual é a norma para ETA e subestação?"

    rankings = ranker.rank_responses(query, responses)
    print("Rankings:")
    for ranking in rankings:
        print(f"  Rank {ranking.rank}: {ranking.agent_slug} (score: {ranking.score:.2f})")
