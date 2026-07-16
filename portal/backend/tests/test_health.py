"""
Health check tests for Portal Master.
"""

import pytest


class TestHealth:
    """Health endpoint tests."""

    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_has_status_ok(self, client):
        """Test that health response has status ok."""
        response = client.get("/api/health")
        data = response.json()
        assert data.get("status") == "ok"

    def test_health_response_has_version(self, client):
        """Test that health response includes version."""
        response = client.get("/api/health")
        data = response.json()
        assert "version" in data
        assert "0.1.0" in data["version"]

    def test_health_response_has_service_name(self, client):
        """Test that health response includes service name."""
        response = client.get("/api/health")
        data = response.json()
        assert "service" in data
        assert "portal-master" in data["service"]


class TestConfig:
    """Configuration endpoint tests."""

    def test_config_endpoint_returns_200(self, client):
        """Test that config endpoint returns 200."""
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_config_response_has_adk_version(self, client):
        """Test that config has ADK version."""
        response = client.get("/api/config")
        data = response.json()
        assert data.get("adk_version") == 5

    def test_config_response_has_layers(self, client):
        """Test that config includes 5-layer architecture."""
        response = client.get("/api/config")
        data = response.json()
        assert "layers" in data
        assert len(data["layers"]) == 5

    def test_config_response_has_agent_count(self, client):
        """Test that config includes agent count."""
        response = client.get("/api/config")
        data = response.json()
        assert data.get("agent_count") == 20

    def test_config_response_has_tool_count(self, client):
        """Test that config includes tool count."""
        response = client.get("/api/config")
        data = response.json()
        assert data.get("tool_count") == 14
