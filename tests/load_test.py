"""
Load testing script for Manta Maestro using Locust.

This script simulates realistic user load on the Manta API to trigger
HPA scaling events and validate auto-scaling behavior.

Usage:
    locust -f tests/load_test.py -u 500 --spawn-rate 25 -H http://localhost:8000
    locust -f tests/load_test.py -u 500 --spawn-rate 25 -H https://api.manta.example.com
"""

from locust import HttpUser, task, between
import random
import json
import logging

logger = logging.getLogger(__name__)


class MantaAPIUser(HttpUser):
    """Simulates a typical Manta Maestro API user."""

    # Wait between requests: 1-5 seconds
    wait_time = between(1, 5)

    def on_start(self):
        """Initialize user session."""
        self.agent_types = [
            "agente-infraestrutura-s1",
            "agente-infraestrutura-s2",
            "agente-saneamento",
            "agente-energia",
            "agente-portos",
        ]
        self.project_ids = [f"proj-{i:06d}" for i in range(1, 101)]

    @task(10)
    def route_query(self):
        """
        Task: Route a natural language query to appropriate agent.
        Weight: 10 (most common operation)
        """
        query = random.choice(
            [
                "Analyze rodovia BR-101 pavimento structure",
                "Assess ponte viaduto design for project 12345",
                "Review saneamento ETA specifications",
                "Evaluate energia transmissão network",
                "Design porto terminal layout",
            ]
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": query,
            "project_id": random.choice(self.project_ids),
            "segment": random.choice(self.agent_types),
        }
        self.client.post(
            "/api/v1/routing/query",
            json=payload,
            headers=headers,
            name="/api/v1/routing/query",
        )

    @task(5)
    def search_documents(self):
        """
        Task: Search project documents using semantic search.
        Weight: 5
        """
        keywords = random.choice(
            [
                "geotechnical site investigation",
                "pavement design analysis",
                "foundation assessment",
                "environmental impact study",
            ]
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": keywords,
            "project_id": random.choice(self.project_ids),
            "limit": random.choice([10, 20, 50]),
        }
        self.client.post(
            "/api/v1/search/semantic",
            json=payload,
            headers=headers,
            name="/api/v1/search/semantic",
        )

    @task(3)
    def get_agent_status(self):
        """
        Task: Fetch agent status and routing accuracy metrics.
        Weight: 3
        """
        agent = random.choice(self.agent_types)
        self.client.get(
            f"/api/v1/agents/{agent}/status",
            name="/api/v1/agents/{agent}/status",
        )

    @task(2)
    def create_claim(self):
        """
        Task: Create a new insurance claim analysis.
        Weight: 2
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "project_id": random.choice(self.project_ids),
            "claim_type": random.choice(["delay", "cost_overrun", "quality_defect"]),
            "description": "Claim analysis for engineering project",
            "amount": random.uniform(50000, 500000),
        }
        self.client.post(
            "/api/v1/claims/analyze",
            json=payload,
            headers=headers,
            name="/api/v1/claims/analyze",
        )

    @task(2)
    def get_project_metrics(self):
        """
        Task: Retrieve project metrics and KPIs.
        Weight: 2
        """
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/v1/projects/{project_id}/metrics",
            name="/api/v1/projects/{project_id}/metrics",
        )

    @task(1)
    def get_health_check(self):
        """
        Task: Health check endpoint (low priority).
        Weight: 1
        """
        self.client.get("/health", name="/health")


class FastRampUpUser(HttpUser):
    """Simulates rapid spike in concurrent users."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Initialize session."""
        self.segment = random.choice(
            [
                "rodovia",
                "ponte",
                "saneamento",
                "energia",
                "porto",
            ]
        )

    @task
    def heavy_api_call(self):
        """Simulate intensive API calls during spike."""
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": f"Analyze {self.segment} project for risk assessment",
            "segment": self.segment,
        }
        self.client.post(
            "/api/v1/routing/query",
            json=payload,
            headers=headers,
            timeout=30,
            name="/api/v1/routing/query (spike)",
        )


class SemanticSearchUser(HttpUser):
    """Simulates users performing heavy semantic search operations."""

    wait_time = between(2, 8)

    @task(8)
    def semantic_search_complex(self):
        """Heavy semantic search with large result sets."""
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": "detailed analysis of foundation design specifications including bearing capacity and settlement analysis",
            "limit": 100,
            "filters": {
                "document_type": "technical_report",
                "date_range": ["2020-01-01", "2024-12-31"],
            },
        }
        self.client.post(
            "/api/v1/search/semantic",
            json=payload,
            headers=headers,
            timeout=30,
            name="/api/v1/search/semantic (complex)",
        )

    @task(2)
    def get_recommendations(self):
        """Fetch AI-generated recommendations."""
        self.client.get(
            "/api/v1/recommendations/top",
            name="/api/v1/recommendations/top",
        )
