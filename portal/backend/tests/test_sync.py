"""
Synchronization endpoint tests for Portal Master.
"""

import pytest


class TestSyncEndpoints:
    """Sync endpoint tests."""

    def test_sync_pull_endpoint_returns_200(self, client):
        """Test that sync pull endpoint returns 200."""
        response = client.post("/api/sync/pull")
        assert response.status_code == 200

    def test_sync_pull_returns_json(self, client):
        """Test that sync pull returns valid JSON."""
        response = client.post("/api/sync/pull")
        data = response.json()
        assert isinstance(data, dict)

    def test_sync_pull_has_status_field(self, client):
        """Test that sync pull response has status field."""
        response = client.post("/api/sync/pull")
        data = response.json()
        assert "status" in data

    def test_sync_pull_has_message_field(self, client):
        """Test that sync pull response has message field."""
        response = client.post("/api/sync/pull")
        data = response.json()
        assert "message" in data

    def test_sync_push_endpoint_returns_200(self, client):
        """Test that sync push endpoint returns 200."""
        response = client.post("/api/sync/push")
        assert response.status_code == 200

    def test_sync_push_returns_json(self, client):
        """Test that sync push returns valid JSON."""
        response = client.post("/api/sync/push")
        data = response.json()
        assert isinstance(data, dict)

    def test_sync_push_has_status_field(self, client):
        """Test that sync push response has status field."""
        response = client.post("/api/sync/push")
        data = response.json()
        assert "status" in data

    def test_sync_push_has_message_field(self, client):
        """Test that sync push response has message field."""
        response = client.post("/api/sync/push")
        data = response.json()
        assert "message" in data


class TestSyncPending:
    """Test that sync endpoints return pending status."""

    def test_sync_pull_status_is_pending(self, client):
        """Test that pull returns pending status."""
        response = client.post("/api/sync/pull")
        data = response.json()
        assert data.get("status") == "pending"

    def test_sync_push_status_is_pending(self, client):
        """Test that push returns pending status."""
        response = client.post("/api/sync/push")
        data = response.json()
        assert data.get("status") == "pending"
