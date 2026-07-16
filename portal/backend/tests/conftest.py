"""
Pytest configuration and fixtures for Portal Master.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
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
