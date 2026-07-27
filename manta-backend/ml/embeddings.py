"""
ml/embeddings.py — Geração de embeddings para o RAG (pgvector).

Usa Sentence Transformers (all-MiniLM-L6-v2) para gerar embeddings de
alta qualidade localmente — sem dependência de API externa (OpenAI/
Anthropic) para essa etapa. GPU acceleration ativada automaticamente se
disponível (CUDA/MPS), com fallback para CPU.

IMPORTANTE — dimensão do vetor: all-MiniLM-L6-v2 produz vetores de
dimensão 384 (EMBEDDING_DIMENSIONS abaixo). Isso precisa bater com:
  - config.Settings.embedding_model / embedding_dimensions (config.py)
  - database.EMBEDDING_DIM / RagChunk.embedding (database.py, ORM)
  - a coluna `vector(N)` criada pelas migrations Alembic
    (alembic/versions/0002_initial_schema.py + 0004_embedding_dim_384.py)
  - scripts/init.sql (bootstrap do schema legado usado por routers/rag.py)
Trocar de modelo de embedding por outro de dimensão diferente exige
atualizar TODOS esses pontos + uma migration Alembic nova (ALTER COLUMN
+ reindex do índice ivfflat) — nunca só este arquivo isoladamente,
senão o insert/select contra `vector(N)` falha com
`expected N dimensions, not M`.

Exports:
  - embed_text(text: str) -> List[float]               : embedding de um único texto
  - embed_texts(texts: List[str]) -> List[List[float]]  : embedding em batch (nome canônico)
  - embed_batch(texts: List[str]) -> List[List[float]]  : alias de embed_texts, mantido
    por compatibilidade com tasks/embed_rag_chunks.py (import histórico)
  - get_model_info() -> dict                            : info sobre o modelo carregado
"""
import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("manta.ml.embeddings")

# Nome do modelo e dimensão do vetor produzido — únicas constantes que
# precisam mudar ao trocar de modelo (ver aviso na docstring acima).
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# Singleton do modelo carregado em memória — carregado de forma lazy na
# primeira chamada a embed_text/embed_texts (evita pagar o custo de
# carregar o modelo em processos que nunca embarcam nada, ex.: workers
# de rotas não-RAG).
_model: SentenceTransformer | None = None
_model_device: str | None = None


def _get_device() -> str:
    """Detecta o dispositivo disponível: CUDA > MPS > CPU."""
    try:
        import torch

        if torch.cuda.is_available():
            logger.info("embeddings: CUDA detectado, usando GPU")
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            logger.info("embeddings: MPS detectado, usando GPU (Apple Silicon)")
            return "mps"
    except ImportError:
        pass
    logger.info("embeddings: usando CPU")
    return "cpu"


def _load_model() -> SentenceTransformer:
    """Carrega o modelo Sentence Transformers (all-MiniLM-L6-v2) com
    GPU acceleration se disponível. Chamado uma única vez — chamadas
    subsequentes devolvem o singleton já carregado."""
    global _model, _model_device
    if _model is not None:
        return _model

    device = _get_device()
    _model_device = device

    logger.info("embeddings: carregando %s (dimensão %d)...", EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSIONS)
    try:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        logger.info("embeddings: modelo carregado com sucesso")
    except Exception as e:
        logger.exception("embeddings: falha ao carregar modelo")
        raise RuntimeError(f"Falha ao carregar embedding model: {e}") from e

    return _model


async def embed_text(text: str) -> List[float]:
    """Gera um embedding para um único texto via Sentence Transformers.

    Args:
        text: Texto a embarcar (qualquer comprimento).

    Returns:
        Vetor de embedding como List[float] de dimensão EMBEDDING_DIMENSIONS (384).

    Raises:
        RuntimeError: Se o modelo falhar ao carregar/executar.
    """
    if not text or not text.strip():
        # Vetor zero para texto vazio (evita erros de embedding e
        # mantém a dimensão correta para o insert/pgvector).
        return [0.0] * EMBEDDING_DIMENSIONS

    try:
        model = _load_model()
        # Sentence Transformers retorna ndarray (dim,) para uma string única.
        embedding: np.ndarray = model.encode(
            text.strip(),
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalization — deixa cosine e dot product equivalentes
        )
        return embedding.tolist() if isinstance(embedding, np.ndarray) else list(embedding)
    except Exception as e:
        logger.exception("embeddings: falha ao embarcar texto")
        raise RuntimeError(f"Falha ao gerar embedding: {e}") from e


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Gera embeddings para múltiplos textos em batch (mais eficiente
    que N chamadas a embed_text — o encode em lote do Sentence
    Transformers reaproveita padding/paralelismo interno).

    Args:
        texts: Lista de textos a embarcar.

    Returns:
        Lista de vetores de embedding, cada um List[float] de dimensão
        EMBEDDING_DIMENSIONS (384), na MESMA ordem de `texts`. Textos
        vazios/whitespace recebem vetor zero no índice correspondente.

    Raises:
        RuntimeError: Se o modelo falhar ao carregar/executar.
    """
    if not texts:
        return []

    try:
        model = _load_model()

        # Filtra vazios antes de mandar pro modelo (evita desperdiçar
        # batch com strings vazias) e reintroduz vetores zero nos
        # índices originais depois — a ordem final tem que bater 1:1
        # com `texts`.
        embeddings_by_index: dict[int, List[float]] = {}
        non_empty_texts: List[str] = []
        non_empty_indices: List[int] = []

        for i, text in enumerate(texts):
            if text and text.strip():
                non_empty_texts.append(text.strip())
                non_empty_indices.append(i)
            else:
                embeddings_by_index[i] = [0.0] * EMBEDDING_DIMENSIONS

        if non_empty_texts:
            batch_embeddings: np.ndarray = model.encode(
                non_empty_texts,
                convert_to_numpy=True,
                batch_size=32,  # controla uso de memória em lotes grandes
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            for j, i in enumerate(non_empty_indices):
                row = batch_embeddings[j] if batch_embeddings.ndim > 1 else batch_embeddings
                embeddings_by_index[i] = row.tolist() if isinstance(row, np.ndarray) else list(row)

        # Reordena conforme o índice original (dict não garante ordem de inserção == ordem de texts).
        return [embeddings_by_index[i] for i in range(len(texts))]
    except Exception as e:
        logger.exception("embeddings: falha ao embarcar batch")
        raise RuntimeError(f"Falha ao gerar embeddings em batch: {e}") from e


# Alias de compatibilidade — tasks/embed_rag_chunks.py importa `embed_batch`;
# mantido para não quebrar esse import já existente. `embed_texts` é o
# nome canônico daqui em diante.
embed_batch = embed_texts


def get_model_info() -> dict:
    """Retorna informações sobre o modelo carregado (nome, dimensão,
    device, status)."""
    return {
        "model_name": EMBEDDING_MODEL_NAME,
        "dimensions": EMBEDDING_DIMENSIONS,
        "device": _model_device or "não carregado",
        "status": "carregado" if _model is not None else "não carregado",
    }
