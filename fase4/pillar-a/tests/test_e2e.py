"""End-to-end integration tests."""

import pytest
from unittest.mock import AsyncMock, patch

from platform_abstraction_layer import PlatformAbstractionLayer, get_pal
from drivers.base import PlatformType
from tests.fixtures import GITHUB_REPO_RESPONSE


class TestPALIntegration:
    """Test PAL end-to-end integration."""

    @pytest.fixture
    def pal(self, tmp_path):
        """Create PAL instance with test config."""
        config_path = tmp_path / "config.yaml"
        config_content = """
platform_abstraction_layer:
  version: "1.0.0"
  detection:
    timeout_ms: 15000
    cache_ttl_seconds: 3600
    fallback_to_git_cli: true

  platforms:
    github:
      enabled: true
      api_version: "2022-11-28"
      base_urls:
        api: "https://api.github.com"
        web: "https://github.com"
      timeout_seconds: 30
      retry_attempts: 3
      retry_backoff_factor: 2.0
      rate_limit_handling: "backoff"
      capabilities: []

    gitlab:
      enabled: true
      api_version: "v4"
      base_urls:
        api: "https://gitlab.com/api/v4"
        web: "https://gitlab.com"
      timeout_seconds: 30
      retry_attempts: 3
      capabilities: []

    bitbucket:
      enabled: true
      api_version: "2.0"
      base_urls:
        api: "https://api.bitbucket.org/2.0"
        web: "https://bitbucket.org"
      timeout_seconds: 30
      capabilities: []

    gitea:
      enabled: true
      api_version: "1.0"
      base_urls:
        api: "https://gitea.example.com/api/v1"
        web: "https://gitea.example.com"
      timeout_seconds: 30
      capabilities: []

  authentication:
    token_env_prefix: "PLATFORM_TOKEN"
    webhook_secret_env_prefix: "WEBHOOK_SECRET"
    verify_ssl: true
    ca_bundle_path: null

  monitoring:
    health_check_interval_seconds: 60
    metrics_enabled: true
    trace_enabled: true
    log_level: "INFO"

  fallback:
    use_git_cli: true
    git_timeout_seconds: 10
    max_retries: 3
"""
        config_path.write_text(config_content)
        return PlatformAbstractionLayer(str(config_path))

    @pytest.mark.asyncio
    async def test_pal_initialization(self, pal):
        """Test PAL initialization."""
        assert pal is not None
        assert len(pal.drivers) == 4

    @pytest.mark.asyncio
    async def test_get_driver_github(self, pal):
        """Test getting GitHub driver."""
        driver = await pal.get_driver(PlatformType.GITHUB)
        assert driver is not None
        assert driver.platform_type == PlatformType.GITHUB

    @pytest.mark.asyncio
    async def test_get_driver_gitlab(self, pal):
        """Test getting GitLab driver."""
        driver = await pal.get_driver(PlatformType.GITLAB)
        assert driver is not None
        assert driver.platform_type == PlatformType.GITLAB

    @pytest.mark.asyncio
    async def test_get_driver_bitbucket(self, pal):
        """Test getting Bitbucket driver."""
        driver = await pal.get_driver(PlatformType.BITBUCKET)
        assert driver is not None
        assert driver.platform_type == PlatformType.BITBUCKET

    @pytest.mark.asyncio
    async def test_get_driver_gitea(self, pal):
        """Test getting Gitea driver."""
        driver = await pal.get_driver(PlatformType.GITEA)
        assert driver is not None
        assert driver.platform_type == PlatformType.GITEA

    @pytest.mark.asyncio
    async def test_detect_and_get_driver(self, pal):
        """Test platform detection and driver retrieval."""
        url = "https://github.com/octocat/Hello-World"

        driver, detection_time = await pal.detect_and_get_driver(url)

        assert driver is not None
        assert driver.platform_type == PlatformType.GITHUB
        assert detection_time < 15

    @pytest.mark.asyncio
    async def test_list_capabilities(self, pal):
        """Test listing platform capabilities."""
        capabilities = await pal.list_capabilities()

        assert "github" in capabilities
        assert "gitlab" in capabilities
        assert "bitbucket" in capabilities
        assert "gitea" in capabilities

        assert len(capabilities["github"]) > 0

    @pytest.mark.asyncio
    async def test_health_check_all(self, pal):
        """Test health check for all platforms."""
        health = await pal.health_check()

        assert "overall_status" in health
        assert "platforms" in health
        assert len(health["platforms"]) == 4

        for platform_name, status in health["platforms"].items():
            assert "status" in status

    @pytest.mark.asyncio
    async def test_invalid_platform_raises_error(self, pal):
        """Test that invalid platform raises error."""
        with pytest.raises(ValueError):
            await pal.get_driver(PlatformType("invalid"))

    @pytest.mark.asyncio
    async def test_detect_and_get_driver_invalid_url(self, pal):
        """Test detection with invalid URL."""
        with pytest.raises(ValueError):
            await pal.detect_and_get_driver("https://unknown-platform.com/repo")


class TestPALConvenience:
    """Test PAL convenience functions."""

    def test_get_pal_function(self):
        """Test get_pal convenience function."""
        pal = get_pal()
        assert pal is not None
        assert isinstance(pal, PlatformAbstractionLayer)
