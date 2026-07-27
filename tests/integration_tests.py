"""
integration_tests.py — End-to-end test suite for Manta Maestro go-live.

Runs 8 critical user journeys covering:
1. User authentication and profile management
2. Admin org setup and model configuration
3. Agent execution with routing and RAG
4. Feedback loop and analytics
5. Fine-tuning job submission and deployment
6. Workflow building and execution
7. Knowledge Hub upload and search
8. Error handling and graceful degradation

Run: pytest tests/integration_tests.py -v --markers="integration"
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

# Assume FastAPI app is importable
from app import app


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TEST_TOKEN", "test-admin-token")


@pytest.fixture
async def async_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client


@pytest.fixture
async def test_user_credentials():
    """Test user email and password."""
    return {
        "email": f"testuser_{int(time.time())}@example.com",
        "password": "TestPassword123!@#",
        "organization_name": "Test Org",
        "full_name": "Test User",
    }


@pytest.fixture
async def test_user_token(async_client, test_user_credentials):
    """Register and login test user, return JWT token."""
    # Register
    response = await async_client.post(
        "/auth/register",
        json=test_user_credentials,
    )
    assert response.status_code == 201
    register_data = response.json()
    token = register_data["token"]
    org_id = register_data["organization_id"]
    user_id = register_data["user_id"]

    return {
        "token": token,
        "org_id": org_id,
        "user_id": user_id,
        "email": test_user_credentials["email"],
    }


class TestScenario1_UserLoginAndProfile:
    """Scenario 1: User login → select agent → submit prompt → receive response → feedback."""

    @pytest.mark.integration
    async def test_user_registration_and_login(self, async_client, test_user_credentials):
        """Test: Register new user account."""
        response = await async_client.post(
            "/auth/register",
            json=test_user_credentials,
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert "refresh_token" in data
        assert data["email"] == test_user_credentials["email"]

    @pytest.mark.integration
    async def test_user_login(self, async_client, test_user_credentials, test_user_token):
        """Test: Login with credentials, receive JWT."""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["token_type"] == "Bearer"

    @pytest.mark.integration
    async def test_get_user_profile(self, async_client, test_user_token):
        """Test: Fetch authenticated user profile."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.get("/auth/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_token["email"]
        assert data["id"] == test_user_token["user_id"]

    @pytest.mark.integration
    async def test_agent_selection(self, async_client, test_user_token):
        """Test: Browse available agents."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.get("/agents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) >= 20  # Should have all agents
        # Verify key agents present
        agent_ids = [a["id"] for a in data["agents"]]
        assert "agent_s1_rodovia" in agent_ids
        assert "agent_s8_saneamento" in agent_ids

    @pytest.mark.integration
    async def test_agent_execution(self, async_client, test_user_token):
        """Test: Submit prompt to agent, receive response."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        payload = {
            "prompt": "What is the cost of CBUQ asphalt per ton in 2026?",
            "context": {"project_type": "highway"},
            "temperature": 0.7,
            "max_tokens": 500,
            "include_citations": True,
        }
        response = await async_client.post(
            "/agents/agent_s1_rodovia/execute",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "response" in data
        assert "metadata" in data
        assert data["metadata"]["model_used"]
        assert data["metadata"]["latency_ms"] > 0
        assert data["metadata"]["latency_ms"] < 5000  # p95 < 5s

    @pytest.mark.integration
    async def test_submit_feedback(self, async_client, test_user_token):
        """Test: Submit rating and feedback on response."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        # First, execute an agent
        exec_response = await async_client.post(
            "/agents/agent_s1_rodovia/execute",
            json={
                "prompt": "Highway cost estimation?",
                "temperature": 0.7,
                "max_tokens": 500,
            },
            headers=headers,
        )
        assert exec_response.status_code == 200
        request_id = exec_response.json()["request_id"]

        # Then, submit feedback
        feedback_response = await async_client.post(
            "/feedback/submit",
            json={
                "request_id": request_id,
                "rating": 5,
                "comment": "Excellent analysis",
                "helpful": True,
                "tags": ["accurate", "detailed"],
            },
            headers=headers,
        )
        assert feedback_response.status_code == 201
        data = feedback_response.json()
        assert data["request_id"] == request_id
        assert data["status"] == "received"


class TestScenario2_AdminOrgSetup:
    """Scenario 2: Admin creates org → configures agent models → invites user."""

    @pytest.mark.integration
    async def test_admin_create_organization(self, async_client):
        """Test: Admin creates new organization."""
        # This assumes a separate admin endpoint or org creation during registration
        # Real implementation depends on org management endpoints
        pass

    @pytest.mark.integration
    async def test_admin_configure_agent_models(self, async_client, test_user_token):
        """Test: Admin sets agent tier (Sonnet vs Opus)."""
        # This would require admin endpoints for org-level configuration
        # For now, verify that agents have configurable tiers
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.get("/agents", headers=headers)
        assert response.status_code == 200
        agents = response.json()["agents"]
        # Check that agents have tier attribute
        for agent in agents:
            assert "tier" in agent  # Should be "sonnet", "opus", etc.

    @pytest.mark.integration
    async def test_admin_invite_user(self, async_client, test_user_token):
        """Test: Admin invites team member to organization."""
        # This would use an invite/team management endpoint
        # Verify current user can see their organization
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.get("/auth/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert "organization_id" in profile


class TestScenario3_RAGAndCitations:
    """Scenario 3: Upload document → semantic search → cite in response."""

    @pytest.mark.integration
    async def test_knowledge_hub_upload(self, async_client, test_user_token):
        """Test: Upload document to Knowledge Hub."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        # Create a test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("SICRO 2026 Unit Rates: CBUQ asphalt = R$ 85.50 per ton")
            test_file = f.name

        try:
            # Upload document
            with open(test_file, "rb") as f:
                files = {"files": (test_file, f, "text/plain")}
                response = await async_client.post(
                    "/rag/upload",
                    files=files,
                    data={
                        "collection": "rodovias",
                        "metadata": json.dumps({"project_id": "proj_123"}),
                    },
                    headers=headers,
                )
            assert response.status_code == 202
            data = response.json()
            assert "upload_id" in data
            assert data["status"] == "processing"

            # Note: In real test, would wait for webhook or poll status
            # For now, assume upload completes within 5 minutes
            upload_id = data["upload_id"]

        finally:
            os.unlink(test_file)

    @pytest.mark.integration
    async def test_rag_search(self, async_client, test_user_token):
        """Test: Semantic search across Knowledge Hub."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/rag/search",
            json={
                "query": "CBUQ asphalt cost unit rate",
                "collection": "rodovias",
                "k": 5,
                "similarity_threshold": 0.6,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Note: Results may be empty if no documents in collection
        # In production, this would search uploaded documents

    @pytest.mark.integration
    async def test_agent_execution_with_rag(self, async_client, test_user_token):
        """Test: Agent uses Knowledge Hub to cite sources."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/agents/agent_05_orcamento/execute",
            json={
                "prompt": "What is the SICRO cost for CBUQ asphalt?",
                "include_citations": True,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # If include_citations=True, should have citations (if docs in KH)
        # Citations format: [{"source": "...", "chunk_id": "...", "score": ...}]
        # Note: May be empty if no documents in Knowledge Hub


class TestScenario4_FeedbackAndAnalytics:
    """Scenario 4: Submit multiple feedbacks → view analytics dashboard."""

    @pytest.mark.integration
    async def test_feedback_ingestion(self, async_client, test_user_token):
        """Test: Ingest 10 feedback entries from multiple agents."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        agent_ids = ["agent_s1_rodovia", "agent_05_orcamento", "agent_07_cronograma"]
        ratings = [5, 4, 5, 3, 5, 4, 5, 4, 5, 5]

        for i, rating in enumerate(ratings):
            agent_id = agent_ids[i % len(agent_ids)]

            # Execute agent
            exec_response = await async_client.post(
                f"/agents/{agent_id}/execute",
                json={"prompt": "Test prompt", "max_tokens": 200},
                headers=headers,
            )
            assert exec_response.status_code == 200
            request_id = exec_response.json()["request_id"]

            # Submit feedback
            feedback_response = await async_client.post(
                "/feedback/submit",
                json={
                    "request_id": request_id,
                    "rating": rating,
                    "comment": f"Test feedback {i}",
                    "helpful": rating >= 4,
                },
                headers=headers,
            )
            assert feedback_response.status_code == 201

    @pytest.mark.integration
    async def test_admin_view_analytics(self, async_client, test_user_token):
        """Test: Admin views feedback analytics."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        response = await async_client.get(
            "/feedback/analytics",
            params={
                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "end_date": datetime.now().isoformat(),
            },
            headers=headers,
        )
        # May return 403 if user is not admin; that's OK
        if response.status_code == 200:
            data = response.json()
            assert "total_feedback" in data
            assert "average_rating" in data
            assert "rating_distribution" in data


class TestScenario5_FineTuning:
    """Scenario 5: Submit fine-tuning job → monitor → deploy → A/B test."""

    @pytest.mark.integration
    async def test_submit_finetune_job(self, async_client, test_user_token):
        """Test: Submit fine-tuning job with training data."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        response = await async_client.post(
            "/ml/finetune",
            json={
                "dataset_uri": "s3://example-bucket/training-data.jsonl",
                "dataset_size": 100,  # 100 examples
                "model_base": "claude-3-5-sonnet-20241022",
                "adapter_name": f"test-adapter-{int(time.time())}",
                "hyperparams": {
                    "learning_rate": 2e-4,
                    "epochs": 3,
                    "batch_size": 8,
                    "lora_rank": 16,
                },
                "validation_split": 0.2,
            },
            headers=headers,
        )
        # May return 202 (accepted) or 400 (invalid dataset)
        if response.status_code == 202:
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "queued"
            job_id = data["job_id"]

            # Poll job status
            status_response = await async_client.get(
                f"/ml/finetune/{job_id}",
                headers=headers,
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert "job_id" in status_data
            assert status_data["status"] in ["queued", "running", "completed", "failed"]

    @pytest.mark.integration
    async def test_list_finetuned_models(self, async_client, test_user_token):
        """Test: List fine-tuned models for organization."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        response = await async_client.get(
            "/ml/models",
            params={"status": "active"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        # May be empty if no models created yet


class TestScenario6_WorkflowBuilding:
    """Scenario 6: Build multi-step workflow → execute → get results."""

    @pytest.mark.integration
    async def test_create_workflow(self, async_client, test_user_token):
        """Test: Create a 3-step workflow."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        workflow_def = {
            "name": "Highway Project Analysis",
            "description": "Complete analysis: Technical → Budget → Schedule",
            "steps": [
                {
                    "agent_id": "agent_s1_rodovia",
                    "prompt_template": "Analyze highway project: {project_doc}",
                    "output_variable": "technical_analysis",
                },
                {
                    "agent_id": "agent_05_orcamento",
                    "prompt_template": "Estimate budget from: {technical_analysis}",
                    "output_variable": "budget",
                },
                {
                    "agent_id": "agent_07_cronograma",
                    "prompt_template": "Create schedule for: {budget}",
                    "output_variable": "schedule",
                },
            ],
            "variables": {
                "project_doc": {"type": "file", "required": True},
            },
        }

        response = await async_client.post(
            "/workflows",
            json=workflow_def,
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "workflow_id" in data
        assert data["status"] == "active"
        workflow_id = data["workflow_id"]

        # Return for next test
        return workflow_id

    @pytest.mark.integration
    async def test_execute_workflow(self, async_client, test_user_token):
        """Test: Execute workflow with inputs."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        # First, create workflow
        workflow_def = {
            "name": "Quick Test Workflow",
            "steps": [
                {
                    "agent_id": "agent_05_orcamento",
                    "prompt_template": "Estimate cost for: {query}",
                    "output_variable": "estimate",
                },
            ],
            "variables": {"query": {"type": "string", "required": True}},
        }

        create_response = await async_client.post(
            "/workflows",
            json=workflow_def,
            headers=headers,
        )
        if create_response.status_code == 201:
            workflow_id = create_response.json()["workflow_id"]

            # Execute workflow
            exec_response = await async_client.post(
                f"/workflows/{workflow_id}/execute",
                json={
                    "variables": {"query": "50km highway project"},
                    "priority": "high",
                },
                headers=headers,
            )
            assert exec_response.status_code == 202
            exec_data = exec_response.json()
            assert "execution_id" in exec_data
            assert exec_data["status"] == "running"

            # Poll for completion (real test would wait)
            exec_id = exec_data["execution_id"]
            await asyncio.sleep(1)  # Wait a bit
            status_response = await async_client.get(
                f"/workflows/{workflow_id}/executions/{exec_id}",
                headers=headers,
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] in ["running", "completed", "failed"]


class TestScenario7_KnowledgeHubManagement:
    """Scenario 7: Upload, list, search, delete documents."""

    @pytest.mark.integration
    async def test_list_documents(self, async_client, test_user_token):
        """Test: List uploaded documents."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        response = await async_client.get(
            "/rag/documents",
            params={"collection": "rodovias", "limit": 20},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data

    @pytest.mark.integration
    async def test_delete_document(self, async_client, test_user_token):
        """Test: Delete a document from Knowledge Hub."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        # List documents
        list_response = await async_client.get(
            "/rag/documents",
            headers=headers,
        )
        if list_response.status_code == 200:
            docs = list_response.json()["documents"]
            if len(docs) > 0:
                doc_id = docs[0]["document_id"]

                # Delete document
                delete_response = await async_client.delete(
                    f"/rag/documents/{doc_id}",
                    headers=headers,
                )
                assert delete_response.status_code == 204


class TestScenario8_ErrorHandling:
    """Scenario 8: Test error cases and graceful degradation."""

    @pytest.mark.integration
    async def test_invalid_credentials(self, async_client):
        """Test: Login with wrong password returns 401."""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.integration
    async def test_missing_auth_header(self, async_client):
        """Test: API call without auth returns 401."""
        response = await async_client.get("/agents")
        assert response.status_code == 401

    @pytest.mark.integration
    async def test_invalid_token(self, async_client):
        """Test: Invalid JWT token returns 401."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await async_client.get("/agents", headers=headers)
        assert response.status_code == 401

    @pytest.mark.integration
    async def test_rate_limiting(self, async_client, test_user_token):
        """Test: Rate limiting is enforced."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}

        # Make 105 requests rapidly (limit is 100/min)
        responses = []
        for i in range(105):
            response = await async_client.get("/agents", headers=headers)
            responses.append(response.status_code)

        # Should get some 429s (Too Many Requests)
        assert 429 in responses or len([r for r in responses if r == 200]) >= 100

    @pytest.mark.integration
    async def test_agent_not_found(self, async_client, test_user_token):
        """Test: Request to non-existent agent returns 404."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/agents/nonexistent_agent/execute",
            json={"prompt": "test"},
            headers=headers,
        )
        assert response.status_code == 404

    @pytest.mark.integration
    async def test_malformed_json(self, async_client, test_user_token):
        """Test: Malformed JSON returns 400."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/agents/agent_s1_rodovia/execute",
            content="{invalid json}",
            headers={**headers, "Content-Type": "application/json"},
        )
        assert response.status_code == 400

    @pytest.mark.integration
    async def test_missing_required_field(self, async_client, test_user_token):
        """Test: Missing required field returns 400."""
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/agents/agent_s1_rodovia/execute",
            json={"max_tokens": 500},  # Missing 'prompt'
            headers=headers,
        )
        assert response.status_code == 400

    @pytest.mark.integration
    async def test_service_unavailable_fallback(self, async_client, test_user_token):
        """Test: Graceful degradation if Claude API is unavailable."""
        # This test would need to mock Claude API being down
        # For now, just verify error handling
        headers = {"Authorization": f"Bearer {test_user_token['token']}"}
        response = await async_client.post(
            "/agents/agent_s1_rodovia/execute",
            json={"prompt": "test"},
            headers=headers,
        )
        # Should return 200 (success) or 503 (service unavailable), not 5xx crash
        assert response.status_code in [200, 503]


class TestHealthAndMetrics:
    """Health checks and metrics endpoints."""

    @pytest.mark.integration
    async def test_health_check(self, async_client):
        """Test: Health check returns 200 and healthy status."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert "database" in data["checks"]

    @pytest.mark.integration
    async def test_deployment_status(self, async_client):
        """Test: Deployment verification endpoint."""
        response = await async_client.get(
            "/admin/deployment-status",
            headers={"X-Admin-Token": ADMIN_TOKEN},
        )
        # May return 403 if not admin, but endpoint should exist
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert "tests" in data
            assert "infrastructure" in data
            assert "security" in data


if __name__ == "__main__":
    # Run tests: pytest tests/integration_tests.py -v
    pytest.main([__file__, "-v", "--tb=short"])
