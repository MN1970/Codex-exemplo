"""
tasks/embed_rag_chunks.py — Background task para embarcar chunks RAG.

Processa chunks na tabela `rag_chunks` que ainda não possuem embedding
(embedding IS NULL), embarcar em batches de 32 e escrever os vetores
pgvector na coluna `embedding`.

Usado por:
  - Cron job (scheduler externo, ex.: APScheduler, Celery)
  - Endpoint manual POST /admin/tasks/embed-chunks
  - Lifespan da app (startup sync inicial)

Exemplo de uso:
  ```python
  import asyncio
  from pg_pool import get_pool
  from tasks.embed_rag_chunks import embed_rag_chunks_task

  async def main():
      pool = await get_pool()
      result = await embed_rag_chunks_task(pool, batch_size=32, limit=None)
      print(f"Embarque concluído: {result}")

  asyncio.run(main())
  ```
"""
import asyncio
import logging
from typing import Any

import asyncpg

from ml.embeddings import embed_batch

logger = logging.getLogger("manta.tasks.embed_rag_chunks")


async def embed_rag_chunks_task(
    pool: asyncpg.Pool,
    batch_size: int = 32,
    limit: int | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Processa chunks sem embedding em batches.

    Algoritmo:
    1. Conta chunks com embedding IS NULL
    2. Carrega até `limit` chunks (ou todos se None)
    3. Embarcar em batches de `batch_size`
    4. Escrever vetores pgvector na tabela
    5. Log de progresso a cada batch

    Args:
        pool: asyncpg.Pool conectado ao Postgres.
        batch_size: Quantidade de chunks a embarcar por iteração (padrão 32).
        limit: Máximo de chunks a processar (None = sem limite).
        verbose: Se True, loga progresso detalhado.

    Returns:
        dict com estatísticas:
          - processed: Quantidade de chunks embarrados (sucesso)
          - failed: Quantidade de chunks falhados (retentar manualmente)
          - pending: Chunks com embedding IS NULL ainda restantes
          - total_before: Chunks sem embedding no início
    """
    async with pool.acquire() as conn:
        # Count chunks sem embedding antes de começar
        total_before: int = await conn.fetchval(
            "SELECT COUNT(*) FROM rag_chunks WHERE embedding IS NULL"
        )
        if verbose:
            logger.info(f"embed_rag_chunks: {total_before} chunks pendentes de embarque")

        if total_before == 0:
            return {
                "processed": 0,
                "failed": 0,
                "pending": 0,
                "total_before": 0,
                "message": "Nenhum chunk pendente",
            }

        processed = 0
        failed = 0

        # Processa em batches
        while True:
            # Carrega próximo batch de IDs + conteúdo
            fetch_limit = batch_size if limit is None else min(batch_size, limit - processed)
            if fetch_limit <= 0:
                break

            rows = await conn.fetch(
                """
                SELECT id, content
                FROM rag_chunks
                WHERE embedding IS NULL
                ORDER BY created_at ASC
                LIMIT $1
                """,
                fetch_limit,
            )

            if not rows:
                break

            chunk_ids = [r["id"] for r in rows]
            texts = [r["content"] or "" for r in rows]

            if verbose:
                logger.info(f"embed_rag_chunks: processando batch de {len(rows)} chunks (IDs {chunk_ids[0]}-{chunk_ids[-1]})")

            # Embarcar em batch
            try:
                embeddings = await embed_batch(texts)
            except Exception as e:
                logger.exception("embed_rag_chunks: falha ao embarcar batch")
                failed += len(rows)
                continue

            # Escrever na BD (pgvector)
            async with conn.transaction():
                for chunk_id, embedding in zip(chunk_ids, embeddings, strict=False):
                    try:
                        await conn.execute(
                            """
                            UPDATE rag_chunks
                            SET embedding = $1::vector
                            WHERE id = $2
                            """,
                            embedding,
                            chunk_id,
                        )
                        processed += 1
                    except Exception as e:
                        logger.exception(f"embed_rag_chunks: falha ao atualizar chunk {chunk_id}")
                        failed += 1

            if verbose:
                logger.info(f"embed_rag_chunks: {processed} chunks processados, {failed} falhados")

            # Respeta `limit` se configurado
            if limit is not None and processed >= limit:
                break

        # Count pendentes após conclusão
        pending: int = await conn.fetchval(
            "SELECT COUNT(*) FROM rag_chunks WHERE embedding IS NULL"
        )

    if verbose:
        logger.info(
            f"embed_rag_chunks: tarefa concluída — "
            f"processados={processed}, falhados={failed}, pendentes={pending}"
        )

    return {
        "processed": processed,
        "failed": failed,
        "pending": pending,
        "total_before": total_before,
    }


async def embed_rag_chunks_command(pool: asyncpg.Pool) -> None:
    """Wrapper CLI/script para embed_rag_chunks_task (loga tudo)."""
    result = await embed_rag_chunks_task(pool, batch_size=32, limit=None, verbose=True)
    print(f"\nResultado final: {result}")
