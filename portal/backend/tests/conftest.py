"""
Pytest configuration and fixtures for Portal Master.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.core.database import Base, get_db, engine


@pytest.fixture(scope="function", autouse=True)
def reset_database(request):
    """Reset database before each test."""
    # Skip reset if test is using its own database setup (from test_agents_router.py)
    if 'db' in request.fixturenames and request.node.module.__name__ == 'tests.test_agents_router':
        yield
        return

    # Reset main database for other tests
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Engine might not be initialized yet
        pass

    yield

    try:
        # Cleanup after test
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass


@pytest.fixture
def auth_token():
    """Generate a valid JWT token for testing."""
    token = create_access_token(
        data={
            "sub": "test-user-123",
            "name": "Test User",
            "role": "admin"
        }
    )
    return token


@pytest.fixture
def client(auth_token):
    """FastAPI test client with authentication."""
    test_client = TestClient(app)
    # Add authorization header to all requests
    test_client.headers.update({
        "Authorization": f"Bearer {auth_token}"
    })
    return test_client


@pytest.fixture
def client_no_auth():
    """FastAPI test client without authentication (for testing auth failures)."""
    return TestClient(app)


@pytest.fixture
def sample_agent():
    """Sample agent data for testing."""
    return {
        "code": "Manta 01",
        "name": "claims",
        "aliases": ["02-C", "manta-claims"],
        "tier_default": "Opus",
        "status": "Operacional",
        "description": "Claims management agent"
    }


@pytest.fixture
def sample_tool():
    """Sample tool data for testing."""
    return {
        "id": "balanco",
        "name": "Balanço de Massa",
        "port": 8000,
        "status": "operational",
        "description": "Mass balance analysis tool"
    }
