"""
CAG Orchestrator — Orquestrador principal que integra todos os componentes
"""

import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime

from .response_ranker import ResponseRanker, ResponseSynthesizer, AgentResponse, RankedResponse

# =============================================================================
# CAG ORCHESTRATOR PRINCIPAL
# =============================================================================

class CAGOrchestrator:
    """
    Orquestrador principal do CAG.

    Responsabilidades:
    1. Coordenar Intent Classifier → Agent Selector
    2. Disparar agentes em paralelo (abstrato - caller faz isso)
    3. Rankear respostas com ResponseRanker
    4. Sintetizar com ResponseSynthesizer
    5. Log em Supabase (futuro)
    """

    def __init__(self, debug: bool = False):
        self.ranker = ResponseRanker()
        self.synthesizer = ResponseSynthesizer()
        self.debug = debug
        self._query_cache = {}  # local cache para prototipagem

    async def orchestrate(
        self,
        query: str,
        selected_agents: List[str],
        agent_responses_dict: Dict[str, AgentResponse],
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Orquestra o fluxo completo: ranking + síntese + logging.

        Args:
            query: pergunta original do usuário
            selected_agents: lista de agent slugs selecionados
            agent_responses_dict: {agent_slug: AgentResponse}
            session_id: para rastrear sessão

        Returns:
            {
                'query': query original,
                'selected_agents': agentes usados,
                'rankings': List[RankedResponse formatada],
                'final_response': resposta sintetizada,
                'sources': list de fontes,
                'metadata': {
                    'timestamp': ISO timestamp,
                    'session_id': session_id,
                    'ranker_confidence': score geral,
                    'execution_time_ms': tempo total
                }
            }
        """
        import time
        start_time = time.time()

        # =====================================================================
        # PASSO 1: Validações
        # =====================================================================
        if not selected_agents:
            return {
                'error': 'No agents selected',
                'query': query
            }

        if not agent_responses_dict:
            return {
                'error': 'No agent responses provided',
                'query': query,
                'selected_agents': selected_agents
            }

        # =====================================================================
        # PASSO 2: Converter responses dict para list
        # =====================================================================
        agent_responses = [
            agent_responses_dict[slug]
            for slug in selected_agents
            if slug in agent_responses_dict
        ]

        if not agent_responses:
            return {
                'error': 'No matching responses for selected agents',
                'query': query,
                'selected_agents': selected_agents
            }

        # =====================================================================
        # PASSO 3: Rankear respostas
        # =====================================================================
        if self.debug:
            print(f"[CAG] Ranking {len(agent_responses)} responses...")

        rankings = self.ranker.rank_responses(query, agent_responses)

        # =====================================================================
        # PASSO 4: Sintetizar
        # =====================================================================
        if self.debug:
            print(f"[CAG] Synthesizing top responses...")

        final_response = self.synthesizer.synthesize(
            query,
            rankings,
            agent_responses_dict
        )

        # =====================================================================
        # PASSO 5: Agregação de fontes
        # =====================================================================
        all_sources = set()
        for resp in agent_responses:
            all_sources.update(resp.sources)

        # =====================================================================
        # PASSO 6: Calcular confiança geral
        # =====================================================================
        if rankings:
            avg_score = sum(r.score for r in rankings) / len(rankings)
        else:
            avg_score = 0.0

        # =====================================================================
        # PASSO 7: Log (futuro: Supabase)
        # =====================================================================
        elapsed_ms = (time.time() - start_time) * 1000

        log_entry = {
            'session_id': session_id or self._generate_session_id(),
            'query': query,
            'selected_agents': selected_agents,
            'rankings': [r.agent_slug for r in rankings],
            'avg_confidence': avg_score,
            'execution_time_ms': elapsed_ms,
            'timestamp': datetime.utcnow().isoformat()
        }

        if self.debug:
            print(f"[CAG] Log entry: {json.dumps(log_entry, indent=2)}")

        # =====================================================================
        # PASSO 8: Retornar resultado
        # =====================================================================
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
            'sources': sorted(list(all_sources)),
            'metadata': {
                'session_id': log_entry['session_id'],
                'timestamp': log_entry['timestamp'],
                'avg_confidence': avg_score,
                'execution_time_ms': elapsed_ms,
                'num_agents_consulted': len(agent_responses),
                'top_agent': rankings[0].agent_slug if rankings else None
            }
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _generate_session_id(self) -> str:
        """Gera session ID único"""
        import uuid
        return f"cag_{uuid.uuid4().hex[:12]}"

    def cache_query(
        self,
        query: str,
        result: Dict
    ) -> None:
        """Cache local de resultados (prototipagem)"""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        self._query_cache[query_hash] = {
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_cached_query(self, query: str) -> Optional[Dict]:
        """Recupera resultado em cache"""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return self._query_cache.get(query_hash, {}).get('result')

    def clear_cache(self) -> None:
        """Limpa cache local"""
        self._query_cache.clear()

# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def main():
        # Setup
        orchestrator = CAGOrchestrator(debug=True)

        query = "Qual é a norma para ETA e subestação?"
        selected_agents = ["agente-saneamento", "agente-energia"]
        agent_responses_dict = {
            "agente-saneamento": AgentResponse(
                agent_slug="agente-saneamento",
                agent_name="Saneamento",
                response_text="ETA conforme NBR 12.211...",
                confidence=0.92,
                sources=["NBR 12.211", "Lei 14.026"],
                latency_ms=2500
            ),
            "agente-energia": AgentResponse(
                agent_slug="agente-energia",
                agent_name="Energia",
                response_text="Subestação conforme ANEEL...",
                confidence=0.85,
                sources=["ANEEL", "NBR 5422"],
                latency_ms=3100
            )
        }

        # Execute
        result = await orchestrator.orchestrate(
            query=query,
            selected_agents=selected_agents,
            agent_responses_dict=agent_responses_dict,
            session_id="test-001"
        )

        print("\n" + "="*70)
        print("CAG ORCHESTRATION RESULT")
        print("="*70)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    asyncio.run(main())
