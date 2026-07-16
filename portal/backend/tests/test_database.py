"""
Tests for database layer and ORM models.

This module tests:
- Database initialization and configuration
- SQLAlchemy ORM models
- Database session management
- Model validation and constraints
"""

import pytest
import os
import tempfile
from datetime import datetime
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.database import engine, SessionLocal, Base, init_db
from app.models import (
    Agent,
    AgentStatus,
    AgentTier,
    AgentEixo,
    ToolService,
    ServiceStatus,
    SyncEvent,
    SyncEventType,
    SyncDirection,
)
from app.models.knowledge import (
    KnowledgeDocument,
    KnowledgeChunk,
    ExternalSource,
    KnowledgeCategory,
    ExternalSourceType,
    ExternalSourceStatus,
)


class TestDatabaseInitialization:
    """Test database initialization"""

    def test_database_connection(self):
        """Test that database connection can be established"""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_tables_created(self):
        """Test that all required tables are created"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            "agents",
            "tool_services",
            "sync_events",
            "knowledge_documents",
            "knowledge_chunks",
            "external_sources",
        ]

        for table in required_tables:
            assert table in tables, f"Table {table} not found"

    def test_indexes_created(self):
        """Test that all indexes are created"""
        inspector = inspect(engine)

        # Check agents indexes
        agent_indexes = [idx.name for idx in inspector.get_indexes("agents")]
        assert "idx_agent_code" in agent_indexes
        assert "idx_agent_status" in agent_indexes

        # Check tool_services indexes
        tool_indexes = [idx.name for idx in inspector.get_indexes("tool_services")]
        assert "idx_tool_status" in tool_indexes
        assert "idx_tool_port" in tool_indexes

    def test_session_local_creation(self):
        """Test that SessionLocal can create sessions"""
        session = SessionLocal()
        assert session is not None
        assert isinstance(session, Session)
        session.close()


class TestAgentModel:
    """Test Agent ORM model"""

    def test_agent_creation(self):
        """Test creating an agent"""
        session = SessionLocal()
        agent = Agent(
            id="manta-08",
            name="Test Agent",
            code="Manta 08",
            eixo=AgentEixo.HORIZONTAL,
            tier=AgentTier.SONNET,
            status=AgentStatus.OPERACIONAL,
            aliases=["test-alias"],
            description="Test description",
        )
        session.add(agent)
        session.commit()

        # Retrieve and verify
        retrieved = session.query(Agent).filter(Agent.id == "manta-08").first()
        assert retrieved is not None
        assert retrieved.name == "Test Agent"
        assert retrieved.code == "Manta 08"
        assert retrieved.status == AgentStatus.OPERACIONAL

        session.delete(retrieved)
        session.commit()
        session.close()

    def test_agent_unique_code_constraint(self):
        """Test unique constraint on agent code"""
        session = SessionLocal()

        agent1 = Agent(
            id="agent-1",
            name="Agent 1",
            code="UNIQUE_CODE",
            eixo=AgentEixo.HORIZONTAL,
            tier=AgentTier.SONNET,
        )
        agent2 = Agent(
            id="agent-2",
            name="Agent 2",
            code="UNIQUE_CODE",  # Duplicate code
            eixo=AgentEixo.VERTICAL,
            tier=AgentTier.OPUS,
        )

        session.add(agent1)
        session.commit()

        session.add(agent2)
        with pytest.raises(Exception):  # SQLIntegrityError or similar
            session.commit()

        session.rollback()
        session.close()

    def test_agent_model_to_dict(self):
        """Test Agent.to_dict() method"""
        agent = Agent(
            id="manta-test",
            name="Test Agent",
            code="TEST",
            eixo=AgentEixo.HORIZONTAL,
            tier=AgentTier.HAIKU,
            status=AgentStatus.BETA,
        )

        agent_dict = agent.to_dict()
        assert agent_dict["id"] == "manta-test"
        assert agent_dict["name"] == "Test Agent"
        assert agent_dict["code"] == "TEST"
        assert agent_dict["eixo"] == "Horizontal"
        assert agent_dict["tier"] == "Haiku"
        assert agent_dict["status"] == "Beta"

    def test_agent_repr(self):
        """Test Agent.__repr__() method"""
        agent = Agent(
            id="manta-test",
            name="Test Agent",
            code="TEST",
            eixo=AgentEixo.HORIZONTAL,
            tier=AgentTier.HAIKU,
        )

        repr_str = repr(agent)
        assert "manta-test" in repr_str
        assert "TEST" in repr_str


class TestToolServiceModel:
    """Test ToolService ORM model"""

    def test_tool_service_creation(self):
        """Test creating a tool service"""
        session = SessionLocal()
        tool = ToolService(
            id="balanço",
            name="Balanço de Massa",
            port=8000,
            base_url="http://localhost:8000",
            status=ServiceStatus.HEALTHY,
            description="Mass balance analysis",
        )
        session.add(tool)
        session.commit()

        retrieved = session.query(ToolService).filter(ToolService.id == "balanço").first()
        assert retrieved is not None
        assert retrieved.name == "Balanço de Massa"
        assert retrieved.port == 8000

        session.delete(retrieved)
        session.commit()
        session.close()

    def test_tool_service_unique_port_constraint(self):
        """Test unique constraint on tool port"""
        session = SessionLocal()

        tool1 = ToolService(
            id="tool-1",
            name="Tool 1",
            port=9000,
            status=ServiceStatus.HEALTHY,
        )
        tool2 = ToolService(
            id="tool-2",
            name="Tool 2",
            port=9000,  # Duplicate port
            status=ServiceStatus.HEALTHY,
        )

        session.add(tool1)
        session.commit()

        session.add(tool2)
        with pytest.raises(Exception):
            session.commit()

        session.rollback()
        session.close()

    def test_tool_service_model_to_dict(self):
        """Test ToolService.to_dict() method"""
        tool = ToolService(
            id="test-tool",
            name="Test Tool",
            port=8888,
            status=ServiceStatus.DEGRADED,
            health_check_url="/api/health",
        )

        tool_dict = tool.to_dict()
        assert tool_dict["id"] == "test-tool"
        assert tool_dict["port"] == 8888
        assert tool_dict["status"] == "Degraded"


class TestSyncEventModel:
    """Test SyncEvent ORM model"""

    def test_sync_event_creation(self):
        """Test creating a sync event"""
        session = SessionLocal()
        event = SyncEvent(
            id="sync-001",
            event_type=SyncEventType.AGENT_REGISTERED,
            direction=SyncDirection.PULL,
            status="Success",
            source="manta-hub",
            items_synced=5,
        )
        session.add(event)
        session.commit()

        retrieved = session.query(SyncEvent).filter(SyncEvent.id == "sync-001").first()
        assert retrieved is not None
        assert retrieved.event_type == SyncEventType.AGENT_REGISTERED
        assert retrieved.items_synced == 5

        session.delete(retrieved)
        session.commit()
        session.close()

    def test_sync_event_model_to_dict(self):
        """Test SyncEvent.to_dict() method"""
        event = SyncEvent(
            id="sync-test",
            event_type=SyncEventType.TOOL_STATUS_CHANGED,
            direction=SyncDirection.BIDIRECTIONAL,
            status="Pending",
            source="local",
            items_synced=10,
            items_failed=2,
            items_skipped=0,
        )

        event_dict = event.to_dict()
        assert event_dict["id"] == "sync-test"
        assert event_dict["event_type"] == "ToolStatusChanged"
        assert event_dict["direction"] == "Bidirectional"
        assert event_dict["items_synced"] == 10


class TestKnowledgeDocumentModel:
    """Test KnowledgeDocument ORM model"""

    def test_knowledge_document_creation(self):
        """Test creating a knowledge document"""
        session = SessionLocal()
        doc = KnowledgeDocument(
            id="doc-001",
            title="Test Document",
            content="This is test content",
            category=KnowledgeCategory.DOCUMENTATION,
            eixo_tags=["S1", "S8"],
            agent_ids=["manta-03-s1", "manta-03-s8"],
            tags=["test", "example"],
        )
        session.add(doc)
        session.commit()

        retrieved = session.query(KnowledgeDocument).filter(KnowledgeDocument.id == "doc-001").first()
        assert retrieved is not None
        assert retrieved.title == "Test Document"
        assert "S1" in retrieved.eixo_tags

        session.delete(retrieved)
        session.commit()
        session.close()

    def test_knowledge_document_model_to_dict(self):
        """Test KnowledgeDocument.to_dict() method"""
        doc = KnowledgeDocument(
            id="doc-test",
            title="Test Doc",
            content="Content here",
            category=KnowledgeCategory.ROUTING_RULE,
            summary="Brief summary",
            eixo_tags=["Horizontal"],
        )

        doc_dict = doc.to_dict()
        assert doc_dict["id"] == "doc-test"
        assert doc_dict["title"] == "Test Doc"
        assert doc_dict["category"] == "Routing Rule"


class TestKnowledgeChunkModel:
    """Test KnowledgeChunk ORM model"""

    def test_knowledge_chunk_creation(self):
        """Test creating knowledge chunks with document relationship"""
        session = SessionLocal()

        # Create document first
        doc = KnowledgeDocument(
            id="doc-chunk-test",
            title="Document with Chunks",
            content="This is full content",
            category=KnowledgeCategory.DOCUMENTATION,
        )
        session.add(doc)
        session.flush()

        # Create chunks
        chunk1 = KnowledgeChunk(
            id="doc-chunk-test:0",
            doc_id="doc-chunk-test",
            chunk_text="First chunk",
            chunk_index=0,
            section_title="Section 1",
            token_count=10,
        )
        chunk2 = KnowledgeChunk(
            id="doc-chunk-test:1",
            doc_id="doc-chunk-test",
            chunk_text="Second chunk",
            chunk_index=1,
            section_title="Section 2",
            token_count=15,
        )

        session.add(chunk1)
        session.add(chunk2)
        session.commit()

        # Verify relationship
        retrieved_doc = session.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == "doc-chunk-test"
        ).first()
        assert len(retrieved_doc.chunks) == 2
        assert retrieved_doc.chunks[0].chunk_text == "First chunk"

        # Cleanup
        session.delete(retrieved_doc)
        session.commit()
        session.close()


class TestExternalSourceModel:
    """Test ExternalSource ORM model"""

    def test_external_source_creation(self):
        """Test creating external sources with document relationship"""
        session = SessionLocal()

        # Create document first
        doc = KnowledgeDocument(
            id="doc-external-test",
            title="Document with Links",
            content="Content with external links",
            category=KnowledgeCategory.REFERENCE,
        )
        session.add(doc)
        session.flush()

        # Create external sources
        source1 = ExternalSource(
            id="doc-external-test:0",
            doc_id="doc-external-test",
            url="https://example.com/doc1",
            title="External Reference 1",
            source_type=ExternalSourceType.DIRECT,
            status=ExternalSourceStatus.LIVE,
        )
        source2 = ExternalSource(
            id="doc-external-test:1",
            doc_id="doc-external-test",
            url="https://web.archive.org/web/2024/example.com/doc2",
            title="External Reference 2",
            source_type=ExternalSourceType.WAYBACK,
            status=ExternalSourceStatus.SNAPSHOT,
        )

        session.add(source1)
        session.add(source2)
        session.commit()

        # Verify relationship
        retrieved_doc = session.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == "doc-external-test"
        ).first()
        assert len(retrieved_doc.external_sources) == 2
        assert retrieved_doc.external_sources[0].url == "https://example.com/doc1"

        # Cleanup
        session.delete(retrieved_doc)
        session.commit()
        session.close()


class TestDatabaseRelationships:
    """Test relationships between models"""

    def test_knowledge_document_cascade_delete(self):
        """Test that deleting a document cascades to chunks and external sources"""
        session = SessionLocal()

        # Create a complete document with related data
        doc = KnowledgeDocument(
            id="doc-cascade-test",
            title="Cascade Test",
            content="Test content",
            category=KnowledgeCategory.DOCUMENTATION,
        )
        session.add(doc)
        session.flush()

        chunk = KnowledgeChunk(
            id="doc-cascade-test:0",
            doc_id="doc-cascade-test",
            chunk_text="Chunk text",
            chunk_index=0,
        )
        source = ExternalSource(
            id="doc-cascade-test:0",
            doc_id="doc-cascade-test",
            url="https://example.com",
            source_type=ExternalSourceType.DIRECT,
            status=ExternalSourceStatus.LIVE,
        )

        session.add(chunk)
        session.add(source)
        session.commit()

        # Verify all created
        assert session.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == "doc-cascade-test"
        ).first() is not None
        assert session.query(KnowledgeChunk).filter(
            KnowledgeChunk.id == "doc-cascade-test:0"
        ).first() is not None
        assert session.query(ExternalSource).filter(
            ExternalSource.id == "doc-cascade-test:0"
        ).first() is not None

        # Delete document
        session.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == "doc-cascade-test"
        ).delete()
        session.commit()

        # Verify cascade delete
        assert session.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == "doc-cascade-test"
        ).first() is None
        assert session.query(KnowledgeChunk).filter(
            KnowledgeChunk.id == "doc-cascade-test:0"
        ).first() is None
        assert session.query(ExternalSource).filter(
            ExternalSource.id == "doc-cascade-test:0"
        ).first() is None

        session.close()


class TestDatabaseMigrations:
    """Test database migration functionality"""

    def test_migration_files_exist(self):
        """Test that migration files exist"""
        migration_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "migrations",
            "versions"
        )
        migration_files = [
            "001_initial_schema.py",
            "002_add_knowledge_indexes.py",
        ]

        for migration_file in migration_files:
            path = os.path.join(migration_dir, migration_file)
            assert os.path.exists(path), f"Migration file {migration_file} not found"

    def test_alembic_config_exists(self):
        """Test that alembic.ini exists and is configured"""
        alembic_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "alembic.ini"
        )
        assert os.path.exists(alembic_path), "alembic.ini not found"

        # Verify configuration contains sqlalchemy.url
        with open(alembic_path, "r") as f:
            content = f.read()
            assert "sqlalchemy.url" in content


class TestDatabaseSession:
    """Test database session management"""

    def test_session_context_manager(self):
        """Test using session as a context manager"""
        # This would test the get_db() generator if used in FastAPI
        session = SessionLocal()
        try:
            assert session is not None
            assert isinstance(session, Session)
        finally:
            session.close()

    def test_session_rollback_on_error(self):
        """Test that session can rollback on error"""
        session = SessionLocal()

        agent = Agent(
            id="test-rollback",
            name="Test",
            code="ROLLBACK_TEST",
            eixo=AgentEixo.HORIZONTAL,
            tier=AgentTier.SONNET,
        )
        session.add(agent)
        session.commit()

        # Simulate an error and rollback
        try:
            # Try to add invalid data (this would be caught)
            raise Exception("Simulated error")
        except Exception:
            session.rollback()

        # Verify the transaction was rolled back
        session.close()

        # The agent should still be there from the committed transaction
        session = SessionLocal()
        retrieved = session.query(Agent).filter(Agent.id == "test-rollback").first()
        assert retrieved is not None

        # Cleanup
        session.delete(retrieved)
        session.commit()
        session.close()
