"""Initial migration: Create agents table

Revision ID: 001
Revises:
Create Date: 2026-07-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('aliases', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('eixo', sa.String(50), nullable=False),
        sa.Column('tier', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='Operacional'),
        sa.Column('service_url', sa.String(500), nullable=True),
        sa.Column('routing_keywords', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    # Create indexes
    op.create_index('idx_agent_eixo_status', 'agents', ['eixo', 'status'])
    op.create_index('idx_agent_eixo_tier', 'agents', ['eixo', 'tier'])
    op.create_index('idx_agent_status', 'agents', ['status'])
    op.create_index('idx_agent_tier', 'agents', ['tier'])
    op.create_index('ix_agents_code', 'agents', ['code'])
    op.create_index('ix_agents_eixo', 'agents', ['eixo'])
    op.create_index('ix_agents_id', 'agents', ['id'])
    op.create_index('ix_agents_name', 'agents', ['name'])


def downgrade() -> None:
    # Drop all indexes
    op.drop_index('ix_agents_name', table_name='agents')
    op.drop_index('ix_agents_id', table_name='agents')
    op.drop_index('ix_agents_eixo', table_name='agents')
    op.drop_index('ix_agents_code', table_name='agents')
    op.drop_index('idx_agent_tier', table_name='agents')
    op.drop_index('idx_agent_status', table_name='agents')
    op.drop_index('idx_agent_eixo_tier', table_name='agents')
    op.drop_index('idx_agent_eixo_status', table_name='agents')
    # Drop table
    op.drop_table('agents')
