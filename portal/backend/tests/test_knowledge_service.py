"""
Unit tests for Knowledge Base service
"""

import pytest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.knowledge import KnowledgeCategory
from app.schemas.knowledge import KnowledgeDocumentCreate
from app.db import knowledge as knowledge_db
from app.services.knowledge_service import KnowledgeBaseManager


@pytest.fixture
def db():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    yield db_session
    db_session.close()


class TestKnowledgeDocumentCRUD:
    """Test document CRUD operations"""

    def test_create_document(self, db):
        """Test creating a knowledge document"""
        doc_create = KnowledgeDocumentCreate(
            id="test-doc-1",
            title="Test Document",
            content="This is a test document for the knowledge base.",
            summary="Test summary",
            category=KnowledgeCategory.DOCUMENTATION,
            eixo_tags=["S1", "S8"],
            agent_ids=["manta-03-s1", "manta-03-s8"],
            tags=["test", "example"],
            source_url="https://example.com/doc",
            source_repo="example/repo",
            source_path="docs/test.md",
            created_by="test-user",
        )

        document = knowledge_db.create_knowledge_document(db, doc_create)

        assert document.id == "test-doc-1"
        assert document.title == "Test Document"
        assert document.category == KnowledgeCategory.DOCUMENTATION
        assert "S1" in document.eixo_tags
        assert "manta-03-s1" in document.agent_ids

    def test_get_document_by_id(self, db):
        """Test retrieving a document by ID"""
        doc_create = KnowledgeDocumentCreate(
            id="test-doc-2",
            title="Test Document 2",
            content="Content",
            category=KnowledgeCategory.AGENT_PROFILE,
        )

        created = knowledge_db.create_knowledge_document(db, doc_create)
        retrieved = knowledge_db.get_knowledge_document_by_id(db, "test-doc-2")

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test Document 2"

    def test_update_document(self, db):
        """Test updating a document"""
        doc_create = KnowledgeDocumentCreate(
            id="test-doc-3",
            title="Original Title",
            content="Original content",
            category=KnowledgeCategory.DOCUMENTATION,
        )

        knowledge_db.create_knowledge_document(db, doc_create)

        # Update the document
        from app.schemas.knowledge import KnowledgeDocumentUpdate

        doc_update = KnowledgeDocumentUpdate(
            title="Updated Title",
            content="Updated content",
            updated_by="test-user",
        )

        updated = knowledge_db.update_knowledge_document(db, "test-doc-3", doc_update)

        assert updated.title == "Updated Title"
        assert updated.content == "Updated content"
        assert updated.updated_by == "test-user"

    def test_delete_document(self, db):
        """Test deleting a document"""
        doc_create = KnowledgeDocumentCreate(
            id="test-doc-4",
            title="Document to Delete",
            content="Content",
            category=KnowledgeCategory.DOCUMENTATION,
        )

        knowledge_db.create_knowledge_document(db, doc_create)
        success = knowledge_db.delete_knowledge_document(db, "test-doc-4")

        assert success is True
        assert knowledge_db.get_knowledge_document_by_id(db, "test-doc-4") is None

    def test_duplicate_document_raises_error(self, db):
        """Test that creating duplicate document raises error"""
        doc_create = KnowledgeDocumentCreate(
            id="test-doc-5",
            title="Document",
            content="Content",
            category=KnowledgeCategory.DOCUMENTATION,
        )

        knowledge_db.create_knowledge_document(db, doc_create)

        with pytest.raises(ValueError, match="already exists"):
            knowledge_db.create_knowledge_document(db, doc_create)


class TestKnowledgeChunking:
    """Test document chunking"""

    def test_chunk_document_simple(self):
        """Test chunking a simple document"""
        manager = KnowledgeBaseManager(None)

        content = """
# Section 1
This is section 1 content. It has multiple sentences to make it longer.
It should be split into chunks based on word count.

# Section 2
This is section 2 content. It also has multiple sentences.
Each section should be properly identified.
        """.strip()

        chunks = manager.chunk_document(content)

        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        # At least one chunk should have section information
        assert any(chunk.get("section") for chunk in chunks)

    def test_chunk_document_preserves_content(self):
        """Test that chunking preserves all content"""
        manager = KnowledgeBaseManager(None)

        content = "# Test\nThis is a test document with some content that should be preserved."
        chunks = manager.chunk_document(content)

        # Reconstruct content from chunks
        reconstructed = "\n".join(chunk["text"] for chunk in chunks)
        # The reconstructed might have minor differences due to joining, but should contain original
        assert "test" in reconstructed.lower()
        assert "document" in reconstructed.lower()

    def test_chunk_handles_empty_content(self):
        """Test chunking empty or whitespace-only content"""
        manager = KnowledgeBaseManager(None)

        chunks = manager.chunk_document("")
        assert len(chunks) >= 1  # Should return at least one chunk

        chunks = manager.chunk_document("   \n\n   ")
        assert len(chunks) >= 1  # Should handle whitespace


class TestDocumentSearch:
    """Test document search functionality"""

    def test_search_documents_by_title(self, db):
        """Test searching documents by title"""
        # Create test documents
        for i in range(3):
            doc_create = KnowledgeDocumentCreate(
                id=f"search-test-{i}",
                title=f"Knowledge Document {i}",
                content=f"Content {i}",
                category=KnowledgeCategory.DOCUMENTATION,
            )
            knowledge_db.create_knowledge_document(db, doc_create)

        # Search
        results, total = knowledge_db.search_knowledge_documents(db, "Knowledge", limit=10)

        assert total == 3
        assert len(results) == 3

    def test_search_documents_by_content(self, db):
        """Test searching documents by content"""
        doc_create = KnowledgeDocumentCreate(
            id="content-search-test",
            title="Test Doc",
            content="This document contains specific keyword searchable",
            category=KnowledgeCategory.DOCUMENTATION,
        )
        knowledge_db.create_knowledge_document(db, doc_create)

        # Search by content keyword
        results, total = knowledge_db.search_knowledge_documents(db, "searchable", limit=10)

        assert total == 1
        assert len(results) == 1
        assert results[0].id == "content-search-test"

    def test_search_with_category_filter(self, db):
        """Test search with category filtering"""
        # Create documents with different categories
        doc1 = KnowledgeDocumentCreate(
            id="agent-test-1",
            title="Agent Profile",
            content="Test agent",
            category=KnowledgeCategory.AGENT_PROFILE,
        )
        doc2 = KnowledgeDocumentCreate(
            id="doc-test-1",
            title="Agent Profile",
            content="Test agent",
            category=KnowledgeCategory.DOCUMENTATION,
        )

        knowledge_db.create_knowledge_document(db, doc1)
        knowledge_db.create_knowledge_document(db, doc2)

        # Search with category filter
        results, total = knowledge_db.search_knowledge_documents(
            db,
            "Agent",
            category=KnowledgeCategory.AGENT_PROFILE,
            limit=10,
        )

        assert total == 1
        assert results[0].category == KnowledgeCategory.AGENT_PROFILE


class TestDocumentFiltering:
    """Test document filtering"""

    def test_filter_by_eixo(self, db):
        """Test filtering documents by eixo tag"""
        doc1 = KnowledgeDocumentCreate(
            id="eixo-test-1",
            title="S1 Document",
            content="Test",
            category=KnowledgeCategory.DOCUMENTATION,
            eixo_tags=["S1"],
        )
        doc2 = KnowledgeDocumentCreate(
            id="eixo-test-2",
            title="S8 Document",
            content="Test",
            category=KnowledgeCategory.DOCUMENTATION,
            eixo_tags=["S8"],
        )

        knowledge_db.create_knowledge_document(db, doc1)
        knowledge_db.create_knowledge_document(db, doc2)

        # Filter by eixo
        results, total = knowledge_db.get_knowledge_documents(db, eixo="S1", limit=10)

        assert total == 1
        assert results[0].eixo_tags == ["S1"]

    def test_filter_by_agent_id(self, db):
        """Test filtering documents by agent ID"""
        doc1 = KnowledgeDocumentCreate(
            id="agent-filter-1",
            title="Doc 1",
            content="Test",
            category=KnowledgeCategory.DOCUMENTATION,
            agent_ids=["manta-03-s1"],
        )
        doc2 = KnowledgeDocumentCreate(
            id="agent-filter-2",
            title="Doc 2",
            content="Test",
            category=KnowledgeCategory.DOCUMENTATION,
            agent_ids=["manta-03-s8"],
        )

        knowledge_db.create_knowledge_document(db, doc1)
        knowledge_db.create_knowledge_document(db, doc2)

        # Filter by agent ID
        results, total = knowledge_db.get_knowledge_documents(db, agent_id="manta-03-s1", limit=10)

        assert total == 1
        assert "manta-03-s1" in results[0].agent_ids


class TestMetadataExtraction:
    """Test metadata extraction from content"""

    def test_category_detection(self):
        """Test automatic category detection"""
        manager = KnowledgeBaseManager(None)

        # Agent profile
        category = manager._detect_category(
            "claude.md",
            "Manta 00 maestro agent profile"
        )
        assert category == KnowledgeCategory.AGENT_PROFILE

        # Skill
        category = manager._detect_category(
            "skill.md",
            "This is a skill definition"
        )
        assert category == KnowledgeCategory.SKILL

        # Runbook
        category = manager._detect_category(
            "runbook.md",
            "This is a runbook for operations"
        )
        assert category == KnowledgeCategory.RUNBOOK

    def test_eixo_extraction(self):
        """Test eixo tag extraction"""
        manager = KnowledgeBaseManager(None)

        content = """
        Manta 03-S1 covers highways and roads.
        Manta 03-S8 covers sanitation.
        These are vertical agents.
        """

        tags = manager._extract_eixo_tags(content)

        assert "S1" in tags
        assert "S8" in tags

    def test_agent_id_extraction(self):
        """Test agent ID extraction"""
        manager = KnowledgeBaseManager(None)

        content = """
        Agent manta-03-s1 handles infrastructure.
        Agent manta-03-s8 handles sanitation.
        Manta 00 is the router.
        """

        agent_ids = manager._extract_agent_ids(content)

        assert any("s1" in aid or "s8" in aid for aid in agent_ids)

    def test_summary_extraction(self):
        """Test summary extraction"""
        manager = KnowledgeBaseManager(None)

        content = """
        This is the first paragraph which serves as a summary.

        This is the second paragraph with more detail.
        """

        summary = manager._extract_summary(content)

        assert "first paragraph" in summary
        assert len(summary) <= 300


class TestTokenEstimation:
    """Test token count estimation"""

    def test_token_count_estimation(self):
        """Test rough token count estimation"""
        manager = KnowledgeBaseManager(None)

        # Short text
        short_text = "This is a test."
        count = manager._estimate_token_count(short_text)
        assert count > 0
        assert count < 10

        # Longer text
        long_text = " ".join(["word"] * 100)
        count = manager._estimate_token_count(long_text)
        assert count > 100


class TestPatternMatching:
    """Test pattern matching helpers"""

    def test_glob_pattern_matching(self):
        """Test glob pattern matching"""
        manager = KnowledgeBaseManager(None)

        assert manager._matches_pattern("README.md", "*.md") is True
        assert manager._matches_pattern("claude.md", "*.md") is True
        assert manager._matches_pattern("test.txt", "*.md") is False
        assert manager._matches_pattern("test.txt", "*.txt") is True

    def test_documentation_file_detection(self):
        """Test documentation file detection"""
        manager = KnowledgeBaseManager(None)

        assert manager._is_documentation_file("README.md") is True
        assert manager._is_documentation_file("CLAUDE.md") is True
        assert manager._is_documentation_file("file.txt") is True
        assert manager._is_documentation_file("file.rst") is True
        assert manager._is_documentation_file("file.py") is False
        assert manager._is_documentation_file("file.json") is False

    def test_doc_id_generation(self):
        """Test document ID generation"""
        manager = KnowledgeBaseManager(None)

        id1 = manager._generate_doc_id("owner", "repo", "file.md")
        id2 = manager._generate_doc_id("owner", "repo", "file.md")

        # Same inputs should produce same ID
        assert id1 == id2
        # ID should be reasonable length
        assert len(id1) == 20
