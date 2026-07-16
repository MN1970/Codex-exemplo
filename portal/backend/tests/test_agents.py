"""
Agent registry tests for Portal Master.
"""

import pytest


class TestAgentRegistry:
    """Agent registry endpoint tests."""

    def test_list_agents_returns_200(self, client):
        """Test that list agents endpoint returns 200."""
        response = client.get("/api/agents")
        assert response.status_code == 200

    def test_list_agents_returns_json(self, client):
        """Test that list agents returns valid JSON."""
        response = client.get("/api/agents")
        data = response.json()
        assert isinstance(data, dict)

    def test_list_agents_has_agents_field(self, client):
        """Test that response has agents field."""
        response = client.get("/api/agents")
        data = response.json()
        assert "agents" in data

    def test_list_agents_has_count_field(self, client):
        """Test that response has count field."""
        response = client.get("/api/agents")
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)

    def test_list_agents_returns_empty_on_init(self, client):
        """Test that agents list is empty on init."""
        response = client.get("/api/agents")
        data = response.json()
        assert data["count"] == 0
        assert len(data["agents"]) == 0

    def test_list_agents_response_status(self, client):
        """Test that response includes status field."""
        response = client.get("/api/agents")
        data = response.json()
        assert "status" in data
