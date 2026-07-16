"""
Tests for JWT authentication middleware and token validation
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import jwt

from app.main import app
from app.core.config import get_security_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

client = TestClient(app)
settings = get_security_settings()


class TestPasswordHashing:
    """Tests for password hashing and verification"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)

        # Hashed password should not be the same as plain password
        assert hashed != password
        # Should be a bcrypt hash
        assert len(hashed) > 20

    def test_verify_correct_password(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_password_hashes_are_unique(self):
        """Test that the same password produces different hashes"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Different bcrypt salts produce different hashes
        assert hash1 != hash2


class TestTokenCreation:
    """Tests for JWT token creation"""

    def test_create_access_token(self):
        """Test creating an access token"""
        data = {"sub": "user-001", "username": "testuser", "role": "admin"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == "user-001"
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "admin"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_refresh_token(self):
        """Test creating a refresh token"""
        data = {"sub": "user-001", "username": "testuser"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == "user-001"
        assert decoded["type"] == "refresh"

    def test_access_token_expiration(self):
        """Test that access token includes expiration"""
        data = {"sub": "user-001"}
        token = create_access_token(data)

        decoded = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )

        # Token should expire in approximately 30 minutes
        now = datetime.now(timezone.utc).timestamp()
        exp = decoded["exp"]
        expected_exp = now + (30 * 60)

        # Allow 5 second tolerance for test execution time
        assert abs(exp - expected_exp) < 5


class TestPublicEndpoints:
    """Tests for public endpoints (no authentication required)"""

    def test_health_endpoint_without_token(self):
        """Test /api/health endpoint without authentication"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "portal-master"

    def test_config_endpoint_without_token(self):
        """Test /api/config endpoint without authentication"""
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()
        assert "adk_version" in data
        assert data["adk_version"] == 5
        assert "layers" in data
        assert len(data["layers"]) == 5

    def test_docs_endpoint_without_token(self):
        """Test /docs endpoint without authentication"""
        response = client.get("/docs")

        # Should be accessible without token
        assert response.status_code in [200, 307, 308]

    def test_openapi_endpoint_without_token(self):
        """Test /openapi.json endpoint without authentication"""
        response = client.get("/openapi.json")

        assert response.status_code == 200


class TestLoginEndpoint:
    """Tests for login endpoint"""

    def test_login_successful_admin(self):
        """Test successful login with admin credentials"""
        response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "admin123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 1800
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

    def test_login_successful_editor(self):
        """Test successful login with editor credentials"""
        response = client.post(
            "/api/auth/token",
            json={"username": "editor", "password": "editor123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "editor"

    def test_login_invalid_username(self):
        """Test login with invalid username"""
        response = client.post(
            "/api/auth/token",
            json={"username": "nonexistent", "password": "password123"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid username or password"

    def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid username or password"

    def test_login_missing_username(self):
        """Test login with missing username"""
        response = client.post(
            "/api/auth/token",
            json={"password": "password123"}
        )

        assert response.status_code in [422, 400]

    def test_login_missing_password(self):
        """Test login with missing password"""
        response = client.post(
            "/api/auth/token",
            json={"username": "admin"}
        )

        assert response.status_code in [422, 400]


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""

    def test_sync_pull_without_token(self):
        """Test /api/sync/pull without authentication"""
        response = client.post("/api/sync/pull")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_sync_push_without_token(self):
        """Test /api/sync/push without authentication"""
        response = client.post("/api/sync/push")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_sync_pull_with_invalid_token(self):
        """Test /api/sync/pull with invalid token"""
        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_sync_pull_with_valid_token(self):
        """Test /api/sync/pull with valid token"""
        # First, login to get token
        login_response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Now use the token
        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_sync_push_with_valid_token(self):
        """Test /api/sync/push with valid token"""
        # First, login to get token
        login_response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Now use the token
        response = client.post(
            "/api/sync/push",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200


class TestTokenVerification:
    """Tests for token verification endpoint"""

    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        # Create a token
        data = {"sub": "user-001", "role": "admin"}
        token = create_access_token(data)

        # Verify the token
        response = client.post(
            "/api/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["payload"]["sub"] == "user-001"
        assert data["payload"]["role"] == "admin"

    def test_verify_invalid_token(self):
        """Test verifying an invalid token"""
        response = client.post(
            "/api/auth/verify",
            json={"token": "invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"

    def test_verify_expired_token(self):
        """Test verifying an expired token"""
        # Create an expired token
        data = {"sub": "user-001", "role": "admin"}
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        to_encode = data.copy()
        to_encode.update({
            "exp": expired_time,
            "iat": datetime.now(timezone.utc),
        })
        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM
        )

        response = client.post(
            "/api/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Token has expired"


class TestTokenRefresh:
    """Tests for token refresh endpoint"""

    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # First, login to get tokens
        login_response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        # Refresh the token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 1800

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_refresh_with_access_token(self):
        """Test refresh with access token (should fail)"""
        # Create an access token
        data = {"sub": "user-001", "role": "admin"}
        access_token = create_access_token(data)

        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": access_token}
        )

        # Should fail because access token doesn't have type='refresh'
        assert response.status_code == 401


class TestAuthenticationHeader:
    """Tests for authentication header parsing"""

    def test_missing_bearer_prefix(self):
        """Test request with missing Bearer prefix"""
        token = create_access_token({"sub": "user-001"})

        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": token}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication header" in data["detail"]

    def test_invalid_bearer_format(self):
        """Test request with invalid Bearer format"""
        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": "Bearer token1 token2"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication header" in data["detail"]

    def test_empty_authorization_header(self):
        """Test request with empty Authorization header"""
        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": ""}
        )

        assert response.status_code == 401


class TestCurrentUserEndpoint:
    """Tests for /api/auth/me endpoint"""

    def test_get_current_user_success(self):
        """Test getting current user info with valid token"""
        # Login
        login_response = client.post(
            "/api/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_get_current_user_without_token(self):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_with_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid"}
        )

        assert response.status_code == 401


class TestRoleBasedAccess:
    """Tests for role-based access control"""

    @pytest.mark.skip(reason="Phase 2: Role-based endpoints not yet implemented")
    def test_viewer_cannot_access_admin_endpoint(self):
        """Test that viewer role cannot access admin endpoints"""
        # Login as viewer
        login_response = client.post(
            "/api/auth/token",
            json={"username": "viewer", "password": "viewer123"}
        )
        token = login_response.json()["access_token"]

        # Try to access admin endpoint (phase 2)
        response = client.post(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "newuser"}
        )

        assert response.status_code == 403

    def test_editor_can_access_protected_endpoint(self):
        """Test that editor role can access protected endpoints"""
        # Login as editor
        login_response = client.post(
            "/api/auth/token",
            json={"username": "editor", "password": "editor123"}
        )
        token = login_response.json()["access_token"]

        # Access sync endpoint (which requires auth)
        response = client.post(
            "/api/sync/pull",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should be successful (or at least not 403)
        assert response.status_code != 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
