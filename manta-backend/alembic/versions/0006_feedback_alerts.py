"""feedback_alerts — analytics e alertas automáticos por baixo desempenho

Cria a tabela `feedback_alerts` (database.FeedbackAlert) usada por
tasks/feedback_analytics.py para armazenar alertas disparados quando um
agente cai abaixo do threshold de rating médio (padrão 3.5 stars). A
tarefa semanal de analytics detecta agentes com avg_rating < 3.5 por 2
semanas consecutivas e insere alerta aqui, registrando ação tomada
(slack_notified, retraining_job_submitted, etc.).

Revision ID: 0006_feedback_alerts
Revises: 0005_finetune_jobs
Create Date: 2026-07-27
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_feedback_alerts"
down_revision: str | None = "0005_finetune_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_slug", sa.String(100), nullable=False),
        sa.Column("avg_rating", sa.Float(), nullable=False),
        sa.Column("feedback_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend", sa.String(20), nullable=False, server_default="down"),
        sa.Column("threshold", sa.Float(), nullable=False, server_default="3.5"),
        sa.Column("action_taken", sa.String(100), nullable=False),
        sa.Column("metadata", JSONB(), nullable=False, server_default="'{}'::jsonb"),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_alerts_org_id", "feedback_alerts", ["org_id"])
    op.create_index("ix_feedback_alerts_agent_id", "feedback_alerts", ["agent_id"])
    op.create_index("ix_feedback_alerts_agent_slug", "feedback_alerts", ["agent_slug"])
    op.create_index("ix_feedback_alerts_triggered_at", "feedback_alerts", ["triggered_at"])


def downgrade() -> None:
    op.drop_index("ix_feedback_alerts_triggered_at", table_name="feedback_alerts")
    op.drop_index("ix_feedback_alerts_agent_slug", table_name="feedback_alerts")
    op.drop_index("ix_feedback_alerts_agent_id", table_name="feedback_alerts")
    op.drop_index("ix_feedback_alerts_org_id", table_name="feedback_alerts")
    op.drop_table("feedback_alerts")
