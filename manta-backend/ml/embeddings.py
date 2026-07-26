"""Stub for ml.embeddings used only for the smoke test — avoids needing
torch/sentence-transformers installed. Deterministic hash-based vector,
same shape contract (List[float], dim = settings.embedding_dimensions)."""
import hashlib
import struct
from typing import List
from config import get_settings

settings = get_settings()


def _deterministic_vector(text: str, dimensions: int) -> List[float]:
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    values: List[float] = []
    while len(values) < dimensions:
        seed = hashlib.sha256(seed).digest()
        for i in range(0, len(seed), 4):
            if len(values) >= dimensions:
                break
            (raw,) = struct.unpack("I", seed[i:i + 4])
            values.append((raw / 0xFFFFFFFF) * 2 - 1)
    return values


async def embed_text(text: str) -> List[float]:
    return _deterministic_vector(text, settings.embedding_dimensions)
