"""pgvector extension

Habilita a extensão `vector` (pgvector) — pré-requisito para a coluna
`rag_chunks.embedding` (migration 0002) e para o índice IVFFlat que a
acompanha. Precisa rodar ANTES do schema inicial porque o tipo `vector`
só existe depois de `CREATE EXTENSION`.

Requer que o Postgres tenha o pacote `pgvector` instalado no servidor
(a imagem `pgvector/pgvector:pg16` usada em docker-compose.yml já traz
isso pronto; em serviços gerenciados como Supabase/RDS, habilite a
extensão pelo painel ou confirme que ela está disponível antes de
rodar `alembic upgrade head`).

Revision ID: 0001_pgvector_extension
Revises:
Create Date: 2026-07-26
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_pgvector_extension"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # DROP EXTENSION falha se alguma tabela ainda tiver colunas `vector`
    # (rag_chunks.embedding, criada em 0002) — por isso o downgrade de
    # 0002 precisa rodar antes deste.
    op.execute("DROP EXTENSION IF EXISTS vector")
