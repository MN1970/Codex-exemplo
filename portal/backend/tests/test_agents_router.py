"""
Unit tests for Agent router
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.agent import Agent, AgentStatus, AgentTier, AgentEixo
from app.db.agent import create_agent
from app.schemas.agent import AgentCreate


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create test client with overridden dependency"""
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_agent(db):
    """Create a sample agent for testing"""
    agent_create = AgentCreate(
        id="test-agent-1",
        name="Test Agent",
        code="TEST-001",
        aliases=["test", "agent-1"],
        description="A test agent",
        eixo=AgentEixo.HORIZONTAL,
        tier=AgentTier.SONNET,
        status=AgentStatus.OPERACIONAL,
        service_url="http://localhost:8001",
        routing_keywords=["test", "sample"],
        created_by="test-user",
    )
    return create_agent(db, agent_create)


class TestAgentListEndpoint:
    """Tests for GET /api/agents"""

    def test_list_agents_empty(self, client):
        """Test listing agents when database is empty"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["agents"] == []
        assert data["limit"] == 100
        assert data["offset"] == 0

    def test_list_agents_with_data(self, client, sample_agent):
        """Test listing agents with data"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["agents"]) == 1
        assert data["agents"][0]["code"] == "TEST-001"

    def test_list_agents_with_pagination(self, client, db):
        """Test pagination of agents"""
        # Create multiple agents
        for i in range(5):
            agent_create = AgentCreate(
                id=f"agent-{i}",
                name=f"Agent {i}",
                code=f"AG{i:03d}",
                aliases=[],
                description=f"Test agent {i}",
                eixo=AgentEixo.HORIZONTAL,
                tier=AgentTier.SONNET,
                status=AgentStatus.OPERACIONAL,
                service_url=None,
                routing_keywords=[],
            )
            create_agent(db, agent_create)

        # Test first page
        response = client.get("/api/agents?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["agents"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

        # Test second page
        response = client.get("/api/agents?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["agents"]) == 2
        assert data["offset"] == 2

    def test_list_agents_filter_by_eixo(self, client, db):
        """Test filtering agents by eixo"""
        # Create agents with different eixo
        for eixo in [AgentEixo.HORIZONTAL, AgentEixo.VERTICAL]:
            agent_create = AgentCreate(
                id=f"agent-{eixo.value}",
                name=f"Agent {eixo.value}",
                code=f"AG-{eixo.value[:3]}",
                aliases=[],
                description=f"Agent for {eixo.value}",
                eixo=eixo,
                tier=AgentTier.SONNET,
                status=AgentStatus.OPERACIONAL,
                service_url=None,
                routing_keywords=[],
            )
            create_agent(db, agent_create)

        response = client.get("/api/agents?eixo=horizontal")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["agents"][0]["eixo"] == "Horizontal"

    def test_list_agents_filter_by_status(self, client, db):
        """Test filtering agents by status"""
        # Create agents with different status
        for status in [AgentStatus.OPERACIONAL, AgentStatus.BETA]:
            agent_create = AgentCreate(
                id=f"agent-{status.value}",
                name=f"Agent {status.value}",
                code=f"AG-{status.value[:3]}",
                aliases=[],
                description=f"Agent with {status.value}",
                eixo=AgentEixo.HORIZONTAL,
                tier=AgentTier.SONNET,
                status=status,
                service_url=None,
                routing_keywords=[],
            )
            create_agent(db, agent_create)

        response = client.get("/api/agents?status=Beta")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["agents"][0]["status"] == "Beta"

    def test_list_agents_invalid_eixo(self, client):
        """Test filtering with invalid eixo"""
        response = client.get("/api/agents?eixo=invalid")
        assert response.status_code == 422

    def test_list_agents_invalid_status(self, client):
        """Test filtering with invalid status"""
        response = client.get("/api/agents?status=InvalidStatus")
        assert response.status_code == 422

    def test_list_agents_search(self, client, sample_agent):
        """Test searching agents"""
        response = client.get("/api/agents?search=TEST")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["agents"][0]["code"] == "TEST-001"

        # Search with non-matching term
        response = client.get("/api/agents?search=NONEXISTENT")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestAgentDetailEndpoint:
    """Tests for GET /api/agents/{agent_id}"""

    def test_get_agent_success(self, client, sample_agent):
        """Test getting an existing agent"""
        response = client.get(f"/api/agents/{sample_agent.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["agent"]["id"] == "test-agent-1"
        assert data["agent"]["code"] == "TEST-001"
        assert data["agent"]["name"] == "Test Agent"

    def test_get_agent_not_found(self, client):
        """Test getting a non-existent agent"""
        response = client.get("/api/agents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCreateAgentEndpoint:
    """Tests for POST /api/agents"""

    def test_create_agent_success(self, client, db):
        """Test creating a new agent"""
        payload = {
            "id": "new-agent",
            "name": "New Agent",
            "code": "NEW-001",
            "aliases": ["new", "agent"],
            "description": "A new agent",
            "eixo": "Horizontal",
            "tier": "Sonnet",
            "status": "Operacional",
            "service_url": "http://localhost:8001",
            "routing_keywords": ["new", "test"],
            "created_by": "test-user",
        }
        response = client.post("/api/agents", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["agent"]["id"] == "new-agent"
        assert data["agent"]["code"] == "NEW-001"
        assert data["agent"]["name"] == "New Agent"

    def test_create_agent_duplicate_id(self, client, sample_agent):
        """Test creating agent with duplicate ID"""
        payload = {
            "id": "test-agent-1",  # Same as sample_agent
            "name": "Duplicate Agent",
            "code": "DUP-001",
            "aliases": [],
            "description": "A duplicate agent",
            "eixo": "Horizontal",
            "tier": "Sonnet",
            "status": "Operacional",
            "service_url": None,
            "routing_keywords": [],
        }
        response = client.post("/api/agents", json=payload)
        assert response.status_code == 409  # Conflict

    def test_create_agent_duplicate_code(self, client, sample_agent):
        """Test creating agent with duplicate code"""
        payload = {
            "id": "different-agent",
            "name": "Different Agent",
            "code": "TEST-001",  # Same as sample_agent
            "aliases": [],
            "description": "A different agent with same code",
            "eixo": "Horizontal",
            "tier": "Sonnet",
            "status": "Operacional",
            "service_url": None,
            "routing_keywords": [],
        }
        response = client.post("/api/agents", json=payload)
        assert response.status_code == 409  # Conflict

    def test_create_agent_missing_required_field(self, client):
        """Test creating agent with missing required field"""
        payload = {
            "id": "incomplete-agent",
            "name": "Incomplete Agent",
            # Missing 'code' field
            "eixo": "Horizontal",
            "tier": "Sonnet",
        }
        response = client.post("/api/agents", json=payload)
        assert response.status_code == 422  # Validation error


class TestUpdateAgentEndpoint:
    """Tests for PATCH /api/agents/{agent_id}"""

    def test_update_agent_success(self, client, sample_agent):
        """Test updating an agent"""
        payload = {
            "name": "Updated Agent",
            "status": "Beta",
            "description": "Updated description",
        }
        response = client.patch(f"/api/agents/{sample_agent.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["agent"]["name"] == "Updated Agent"
        assert data["agent"]["status"] == "Beta"
        assert data["agent"]["description"] == "Updated description"

    def test_update_agent_partial(self, client, sample_agent):
        """Test partial update (only update some fields)"""
        original_code = sample_agent.code
        payload = {
            "name": "Partially Updated Agent",
        }
        response = client.patch(f"/api/agents/{sample_agent.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["agent"]["name"] == "Partially Updated Agent"
        assert data["agent"]["code"] == original_code  # Code should not change

    def test_update_agent_not_found(self, client):
        """Test updating a non-existent agent"""
        payload = {"name": "Updated Name"}
        response = client.patch("/api/agents/nonexistent", json=payload)
        assert response.status_code == 404

    def test_update_agent_empty_payload(self, client, sample_agent):
        """Test updating with empty payload"""
        payload = {}
        response = client.patch(f"/api/agents/{sample_agent.id}", json=payload)
        assert response.status_code == 200
        # Agent should be unchanged


class TestDeleteAgentEndpoint:
    """Tests for DELETE /api/agents/{agent_id}"""

    def test_delete_agent_success(self, client, sample_agent, db):
        """Test deleting (archiving) an agent"""
        response = client.delete(f"/api/agents/{sample_agent.id}")
        assert response.status_code == 204

        # Verify agent is marked as INATIVO (soft delete)
        agent = db.query(Agent).filter(Agent.id == sample_agent.id).first()
        assert agent is not None
        assert agent.status == AgentStatus.INATIVO

    def test_delete_agent_not_found(self, client):
        """Test deleting a non-existent agent"""
        response = client.delete("/api/agents/nonexistent")
        assert response.status_code == 404


class TestAgentSearchEndpoints:
    """Tests for specialized search endpoints"""

    def test_get_agents_by_eixo(self, client, db):
        """Test GET /api/agents/search/by-eixo/{eixo}"""
        # Create agents with different eixo
        for eixo in [AgentEixo.HORIZONTAL, AgentEixo.VERTICAL]:
            agent_create = AgentCreate(
                id=f"agent-{eixo.value}",
                name=f"Agent {eixo.value}",
                code=f"AG-{eixo.value[:3]}",
                aliases=[],
                description=f"Agent for {eixo.value}",
                eixo=eixo,
                tier=AgentTier.SONNET,
                status=AgentStatus.OPERACIONAL,
                service_url=None,
                routing_keywords=[],
            )
            create_agent(db, agent_create)

        response = client.get("/api/agents/search/by-eixo/horizontal")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["agents"][0]["eixo"] == "Horizontal"

    def test_get_agents_by_status(self, client, db):
        """Test GET /api/agents/search/by-status/{status}"""
        # Create agents with different status
        for status in [AgentStatus.OPERACIONAL, AgentStatus.BETA]:
            agent_create = AgentCreate(
                id=f"agent-{status.value}",
                name=f"Agent {status.value}",
                code=f"AG-{status.value[:3]}",
                aliases=[],
                description=f"Agent with {status.value}",
                eixo=AgentEixo.HORIZONTAL,
                tier=AgentTier.SONNET,
                status=status,
                service_url=None,
                routing_keywords=[],
            )
            create_agent(db, agent_create)

        response = client.get("/api/agents/search/by-status/operacional")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["agents"][0]["status"] == "Operacional"
