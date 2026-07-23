"""
Gerenciador de Cache Compartilhado — Manta Maestro v4.3
Cache ephemeral compartilhado entre agentes (1h TTL em Opus/Sonnet)
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrada no cache compartilhado"""
    content: str
    agent_types: list  # Quais agentes usam este contexto
    created_at: datetime
    ttl_seconds: int = 3600  # 1 hora padrão
    size_tokens: int = 0

    @property
    def is_expired(self) -> bool:
        """Verificar se o cache expirou"""
        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry


class SharedCacheManager:
    """
    Gerencia cache compartilhado entre agentes.
    Evita re-processar contextos (leis, normas) usados por múltiplos agentes.
    """

    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.usage_stats: Dict[str, int] = {}

    def register_context(
        self,
        key: str,
        content: str,
        agent_types: list,
        ttl_seconds: int = 3600
    ) -> None:
        """
        Registrar contexto compartilhado (lei, norma, padrão).

        Args:
            key: Identificador único (ex: "lei_14026")
            content: Texto do contexto
            agent_types: Lista de agentes que usam [S8, S6, S9]
            ttl_seconds: Tempo de vida (padrão 1h)
        """
        self.cache[key] = CacheEntry(
            content=content,
            agent_types=agent_types,
            created_at=datetime.now(),
            ttl_seconds=ttl_seconds,
            size_tokens=len(content) // 4  # Estimativa: 1 token ≈ 4 chars
        )

    def get_context(self, agent_type: str) -> Optional[str]:
        """
        Obter contexto cachado para um agente.
        Retorna None se não existe ou expirou.

        Args:
            agent_type: Tipo do agente (S8, S6, S9, etc)

        Returns:
            Contexto cachado ou None
        """
        for key, entry in self.cache.items():
            # Verificar se expirou
            if entry.is_expired:
                del self.cache[key]
                continue

            # Verificar se agente usa este contexto
            if agent_type in entry.agent_types:
                self.cache_hits += 1
                return entry.content

        self.cache_misses += 1
        return None

    def record_usage(self, agent: str, tokens: int) -> None:
        """Registrar uso de tokens por agente"""
        self.usage_stats[agent] = self.usage_stats.get(agent, 0) + tokens

    def get_cache_hit_rate(self) -> float:
        """Calcular taxa de acerto do cache"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100

    def get_size_mb(self) -> float:
        """Obter tamanho total do cache em MB"""
        total_bytes = sum(
            len(entry.content.encode('utf-8'))
            for entry in self.cache.values()
        )
        return total_bytes / (1024 * 1024)

    def get_savings_estimate(self) -> Dict[str, any]:
        """Estimar economia com cache"""
        if self.cache_hits == 0:
            return {"savings_tokens": 0, "savings_pct": 0.0, "savings_usd": 0.0}

        # Estimativa: cada cache hit economiza ~50% tokens
        savings_tokens = self.cache_hits * 5000  # Estimativa média
        savings_pct = (self.cache_hits / (self.cache_hits + self.cache_misses)) * 100
        savings_usd = (savings_tokens / 1_000_000) * 3  # $3/1M tokens Sonnet

        return {
            "savings_tokens": savings_tokens,
            "savings_pct": savings_pct,
            "savings_usd": savings_usd
        }

    def print_status(self) -> None:
        """Imprimir status do cache"""
        print("\n📦 STATUS DO CACHE COMPARTILHADO")
        print(f"  Entradas:      {len(self.cache)}")
        print(f"  Tamanho:       {self.get_size_mb():.2f} MB")
        print(f"  Taxa de acerto: {self.get_cache_hit_rate():.1f}%")
        print(f"  Cache hits:    {self.cache_hits}")
        print(f"  Cache misses:  {self.cache_misses}")

        savings = self.get_savings_estimate()
        print(f"  Economia est:  {savings['savings_tokens']:,} tokens (~${savings['savings_usd']:.2f})")

        if self.usage_stats:
            print(f"  Uso por agente:")
            for agent, tokens in sorted(self.usage_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"    {agent:12s}: {tokens:,} tokens")
        print()


# Contextos pré-configurados por tipo de agente
SHARED_CONTEXTS = {
    "lei_14026": {
        "content": """Lei 14.026/2020 — Novo Marco Regulatório do Saneamento
        Universalização 99% água, 90% esgoto até 2033.
        Subsídio cruzado, regionalização, tarifa social.
        Regulação ANA, ARSESP, agências estaduais.""",
        "agents": ["S8", "S6"],  # Saneamento, Portos
        "ttl": 3600
    },
    "aneel_ren": {
        "content": """ANEEL Resoluções Normativas — Transmissão
        RAP (Receita Anual Permitida), leilão de transmissão.
        Procedimentos de rede (ONS), MRE, despacho centralizado.""",
        "agents": ["S9"],  # Energia
        "ttl": 3600
    },
    "icao_annex14": {
        "content": """ICAO Annex 14 — Aerodrome Design and Operations
        Dimensionamento de pista, RWY, TWY, RESA.
        Categoria de código (1A-4F), ACN-PCN.""",
        "agents": ["S7"],  # Aeroportos
        "ttl": 3600
    },
    "icold_bulletins": {
        "content": """ICOLD Bulletins 194, 164 — Dam Safety
        Rejeitos filtrados, CFRD, estabilidade.
        Análise de dam breach, monitoramento.""",
        "agents": ["S10"],  # Barragens
        "ttl": 3600
    },
    "pianc_guidelines": {
        "content": """PIANC Guidelines — Port Design
        Dragagem, amarração, cais, layout de terminal.
        Batimetria, correntes, marés, esteira.""",
        "agents": ["S6"],  # Portos
        "ttl": 3600
    }
}
