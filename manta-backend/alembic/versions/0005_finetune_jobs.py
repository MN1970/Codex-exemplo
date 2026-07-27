"""fine_tune_jobs — tracking assíncrono do POST /ml/finetune

Cria a tabela `fine_tune_jobs` (database.FineTuneJob) usada por
`routers/ml.py::POST /ml/finetune {segment, epochs}` para acompanhar o
job de fine-tuning LoRA disparado em background (ver
ml/finetuning.py::run_finetuning_pipeline). Mesmo desenho org_id
opcional de `ml_models` (0002_initial_schema): nulo = job fora de um
contexto multi-org (CLI/dev), preenchido = job de uma organização
específica.

Revision ID: 0005_finetune_jobs
Revises: 0004_embedding_dim_384
Create Date: 2026-07-26
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_finetune_jobs"
down_revision: str | None = "0004_embedding_dim_384"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fine_tune_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("segment", sa.String(50), nullable=False),
        sa.Column("base_model", sa.String(255), nullable=False, server_default="mistralai/Mistral-7B-v0.1"),
        sa.Column("epochs", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("adapter_name", sa.String(255), nullable=True),
        sa.Column("adapter_path", sa.String(512), nullable=True),
        sa.Column("loss", sa.Float(), nullable=True),
        sa.Column("perplexity", sa.Float(), nullable=True),
        sa.Column("num_train_steps", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_fine_tune_jobs_org_id", "fine_tune_jobs", ["org_id"])
    op.create_index("ix_fine_tune_jobs_segment", "fine_tune_jobs", ["segment"])
    op.create_index("ix_fine_tune_jobs_status", "fine_tune_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_fine_tune_jobs_status", table_name="fine_tune_jobs")
    op.drop_index("ix_fine_tune_jobs_segment", table_name="fine_tune_jobs")
    op.drop_index("ix_fine_tune_jobs_org_id", table_name="fine_tune_jobs")
    op.drop_table("fine_tune_jobs")
