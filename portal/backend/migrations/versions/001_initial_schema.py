"""Initial schema for Portal Master

Revision ID: 001
Revises:
Create Date: 2026-07-16 22:00:00.000000

Creates all base tables for:
- agents (Agent registry)
- tool_services (Tool service registry)
- sync_events (Synchronization event logs)
- knowledge_documents (Knowledge base documents)
- knowledge_chunks (Chunked content for search)
- external_sources (External resource links)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables"""

    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('aliases', sa.JSON(), nullable=True),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('eixo', sa.String(50), nullable=False),
        sa.Column('tier', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('service_url', sa.String(500), nullable=True),
        sa.Column('routing_keywords', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_agent_code')
    )
    op.create_index('idx_agent_code', 'agents', ['code'])
    op.create_index('idx_agent_eixo_status', 'agents', ['eixo', 'status'])
    op.create_index('idx_agent_eixo_tier', 'agents', ['eixo', 'tier'])
    op.create_index('idx_agent_status', 'agents', ['status'])
    op.create_index('idx_agent_tier', 'agents', ['tier'])
    op.create_index('idx_agent_name', 'agents', ['name'])

    # Create tool_services table
    op.create_table(
        'tool_services',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('version', sa.String(50), nullable=True),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('base_url', sa.String(500), nullable=True),
        sa.Column('health_check_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('last_health_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('health_check_interval_seconds', sa.Integer(), nullable=True),
        sa.Column('endpoints_json', sa.JSON(), nullable=True),
        sa.Column('config_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('port', name='uq_tool_port')
    )
    op.create_index('idx_tool_status', 'tool_services', ['status'])
    op.create_index('idx_tool_port', 'tool_services', ['port'])
    op.create_index('idx_tool_name', 'tool_services', ['name'])

    # Create sync_events table
    op.create_table(
        'sync_events',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('direction', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('source_system_id', sa.String(255), nullable=True),
        sa.Column('items_synced', sa.Integer(), nullable=True),
        sa.Column('items_failed', sa.Integer(), nullable=True),
        sa.Column('items_skipped', sa.Integer(), nullable=True),
        sa.Column('payload_json', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_json', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('triggered_by', sa.String(255), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_timestamp', 'sync_events', ['timestamp'])
    op.create_index('idx_sync_status', 'sync_events', ['status'])
    op.create_index('idx_sync_event_type', 'sync_events', ['event_type'])
    op.create_index('idx_sync_direction', 'sync_events', ['direction'])
    op.create_index('idx_sync_source', 'sync_events', ['source'])
    op.create_index('idx_sync_correlation_id', 'sync_events', ['correlation_id'])

    # Create knowledge_documents table
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.String(1000), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('eixo_tags', sa.JSON(), nullable=True),
        sa.Column('agent_ids', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('source_repo', sa.String(500), nullable=True),
        sa.Column('source_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_category', 'knowledge_documents', ['category'])
    op.create_index('idx_knowledge_eixo', 'knowledge_documents', ['category'])
    op.create_index('idx_knowledge_created_at', 'knowledge_documents', ['created_at'])
    op.create_index('idx_knowledge_title', 'knowledge_documents', ['title'])
    op.create_index('idx_knowledge_source_url', 'knowledge_documents', ['source_url'])

    # Create knowledge_chunks table
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.String(150), nullable=False),
        sa.Column('doc_id', sa.String(100), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('section_title', sa.String(500), nullable=True),
        sa.Column('embedding_vector', sa.String(5000), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['doc_id'], ['knowledge_documents.id'], ondelete='CASCADE')
    )
    op.create_index('idx_chunk_doc_id', 'knowledge_chunks', ['doc_id'])
    op.create_index('idx_chunk_index', 'knowledge_chunks', ['chunk_index'])

    # Create external_sources table
    op.create_table(
        'external_sources',
        sa.Column('id', sa.String(150), nullable=False),
        sa.Column('doc_id', sa.String(100), nullable=False),
        sa.Column('url', sa.String(2000), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('snapshot_url', sa.String(2000), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_status_code', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['doc_id'], ['knowledge_documents.id'], ondelete='CASCADE')
    )
    op.create_index('idx_external_doc_id', 'external_sources', ['doc_id'])
    op.create_index('idx_external_status', 'external_sources', ['status'])
    op.create_index('idx_external_checked_at', 'external_sources', ['last_checked_at'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index('idx_external_checked_at', table_name='external_sources')
    op.drop_index('idx_external_status', table_name='external_sources')
    op.drop_index('idx_external_doc_id', table_name='external_sources')
    op.drop_table('external_sources')

    op.drop_index('idx_chunk_index', table_name='knowledge_chunks')
    op.drop_index('idx_chunk_doc_id', table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')

    op.drop_index('idx_knowledge_source_url', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_title', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_created_at', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_eixo', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_category', table_name='knowledge_documents')
    op.drop_table('knowledge_documents')

    op.drop_index('idx_sync_correlation_id', table_name='sync_events')
    op.drop_index('idx_sync_source', table_name='sync_events')
    op.drop_index('idx_sync_direction', table_name='sync_events')
    op.drop_index('idx_sync_event_type', table_name='sync_events')
    op.drop_index('idx_sync_status', table_name='sync_events')
    op.drop_index('idx_sync_timestamp', table_name='sync_events')
    op.drop_table('sync_events')

    op.drop_index('idx_tool_name', table_name='tool_services')
    op.drop_index('idx_tool_port', table_name='tool_services')
    op.drop_index('idx_tool_status', table_name='tool_services')
    op.drop_table('tool_services')

    op.drop_index('idx_agent_name', table_name='agents')
    op.drop_index('idx_agent_tier', table_name='agents')
    op.drop_index('idx_agent_status', table_name='agents')
    op.drop_index('idx_agent_eixo_tier', table_name='agents')
    op.drop_index('idx_agent_eixo_status', table_name='agents')
    op.drop_index('idx_agent_code', table_name='agents')
    op.drop_table('agents')
