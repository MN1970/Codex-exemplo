"""embedding dimension 1536 -> 384 (all-MiniLM-L6-v2)

0002_initial_schema criou `rag_chunks.embedding` como `vector(1536)`,
dimensionado para `text-embedding-3-small` (o modelo assumido no
skeleton original). O modelo de embedding realmente implementado em
`ml/embeddings.py` é o Sentence Transformers `all-MiniLM-L6-v2`, que
produz vetores de dimensão 384 — inserir um vetor de 384 posições numa
coluna `vector(1536)` falha com `expected 1536 dimensions, not 384`.

Esta migration realinha a coluna (e o índice ivfflat associado, que
precisa ser recriado — não sobrevive a um ALTER COLUMN TYPE) para a
dimensão real produzida pelo modelo em uso.

`USING NULL` no ALTER COLUMN: não existe cast numérico válido de
`vector(1536)` para `vector(384)` (dimensões diferentes não são
truncáveis/expansíveis com sentido semântico) — qualquer linha já
embarcada precisa ser reprocessada (ver tasks/embed_rag_chunks.py,
que já trata `embedding IS NULL` como "pendente de embarque").

Revision ID: 0004_embedding_dim_384
Revises: 0003_rls_policies
Create Date: 2026-07-26
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_embedding_dim_384"
down_revision: str | None = "0003_rls_policies"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INDEX_NAME = "ix_rag_chunks_embedding_ivfflat"


def upgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS {_INDEX_NAME}")
    op.execute("ALTER TABLE rag_chunks ALTER COLUMN embedding TYPE vector(384) USING NULL")
    op.execute(
        f"""
        CREATE INDEX {_INDEX_NAME} ON rag_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )


def downgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS {_INDEX_NAME}")
    op.execute("ALTER TABLE rag_chunks ALTER COLUMN embedding TYPE vector(1536) USING NULL")
    op.execute(
        f"""
        CREATE INDEX {_INDEX_NAME} ON rag_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )
