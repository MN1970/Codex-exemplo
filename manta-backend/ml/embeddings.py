"""
ml/embeddings.py — Geração de embeddings para o RAG (pgvector).

Skeleton: por padrão usa um embedding determinístico local (hash-based)
para que o serviço rode sem chave de API externa. Para produção, troque
`embed_text` pela chamada real (ex.: OpenAI, Voyage, Cohere) via
aiohttp, mantendo a assinatura async e a dimensão configurada em
`settings.embedding_dimensions`.
"""
import hashlib
import struct
from typing import List

from config import get_settings

settings = get_settings()


def _deterministic_vector(text: str, dimensions: int) -> List[float]:
    """Gera um vetor pseudo-aleatório determinístico a partir do hash
    do texto — apenas para o skeleton funcionar sem depender de um
    provedor externo de embeddings. NÃO usar em produção."""
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    values: List[float] = []
    while len(values) < dimensions:
        seed = hashlib.sha256(seed).digest()
        # 8 floats por bloco de 32 bytes (4 bytes cada, normalizados para [-1, 1])
        for i in range(0, len(seed), 4):
            if len(values) >= dimensions:
                break
            (raw,) = struct.unpack("I", seed[i:i + 4])
            values.append((raw / 0xFFFFFFFF) * 2 - 1)
    return values


async def embed_text(text: str) -> List[float]:
    """Interface async estável — troque o corpo por uma chamada real
    (aiohttp POST para o provedor de embeddings) mantendo a assinatura.
    """
    return _deterministic_vector(text, settings.embedding_dimensions)
