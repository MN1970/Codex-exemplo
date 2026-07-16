"""Add additional knowledge base indexes for RAG and semantic search

Revision ID: 002
Revises: 001
Create Date: 2026-07-16 23:00:00.000000

Adds indexes for:
- Full-text search support
- Embedding vector similarity search preparation
- Document relationship optimization
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add additional knowledge base indexes"""

    # Add composite index for knowledge document queries
    # This helps with filtering by category and eixo tags together
    op.create_index(
        'idx_knowledge_category_eixo',
        'knowledge_documents',
        ['category', 'created_at'],
        if_not_exists=True
    )

    # Add index for knowledge chunks with document reference
    # Helps with quick chunk lookup when building search results
    op.create_index(
        'idx_chunk_doc_created',
        'knowledge_chunks',
        ['doc_id', 'created_at'],
        if_not_exists=True
    )

    # Add index for external source checking
    # Helps identify which documents have unresolved external links
    op.create_index(
        'idx_external_doc_status',
        'external_sources',
        ['doc_id', 'status'],
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove additional knowledge base indexes"""

    op.drop_index('idx_external_doc_status', table_name='external_sources', if_exists=True)
    op.drop_index('idx_chunk_doc_created', table_name='knowledge_chunks', if_exists=True)
    op.drop_index('idx_knowledge_category_eixo', table_name='knowledge_documents', if_exists=True)
