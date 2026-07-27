"""Tests for platform drivers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from drivers.base import PlatformType, PlatformConfig, RepositoryInfo, PullRequest
from drivers import GitHubDriver, GitLabDriver, BitbucketDriver, GiteaDriver
from tests.fixtures import (
    GITHUB_REPO_RESPONSE,
    GITHUB_PR_RESPONSE,
    GITHUB_COMMIT_RESPONSE,
    GITLAB_PROJECT_RESPONSE,
    BITBUCKET_REPO_RESPONSE,
    GITEA_REPO_RESPONSE,
)


class TestGitHubDriver:
    """Test GitHub driver."""

    @pytest.fixture
    def config(self):
        """Create GitHub config."""
        return PlatformConfig(
            api_version="2022-11-28",
            base_url_api="https://api.github.com",
            base_url_web="https://github.com",
        )

    @pytest.fixture
    def driver(self, config):
        """Create GitHub driver."""
        return GitHubDriver(config, token="test-token")

    @pytest.mark.asyncio
    async def test_get_repository_info(self, driver):
        """Test getting repository information."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = GITHUB_REPO_RESPONSE

            repo_info = await driver.get_repository_info("octocat", "Hello-World")

            assert isinstance(repo_info, RepositoryInfo)
            assert repo_info.owner == "octocat"
            assert repo_info.name == "Hello-World"
            assert repo_info.platform == PlatformType.GITHUB
            assert repo_info.is_private is False
            assert repo_info.has_issues is True

    @pytest.mark.asyncio
    async def test_get_pull_request(self, driver):
        """Test getting a pull request."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = GITHUB_PR_RESPONSE

            pr = await driver.get_pull_request("octocat", "Hello-World", 1347)

            assert isinstance(pr, PullRequest)
            assert pr.number == 1347
            assert pr.title == "Amazing new feature"
            assert pr.state == "open"
            assert pr.author == "octocat"

    @pytest.mark.asyncio
    async def test_list_pull_requests(self, driver):
        """Test listing pull requests."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [GITHUB_PR_RESPONSE]

            prs = await driver.list_pull_requests("octocat", "Hello-World")

            assert isinstance(prs, list)
            assert len(prs) == 1
            assert prs[0].number == 1347

    @pytest.mark.asyncio
    async def test_get_commit(self, driver):
        """Test getting a commit."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = GITHUB_COMMIT_RESPONSE

            commit = await driver.get_commit(
                "octocat", "Hello-World", "6dcb09b5b57875f334f61aeae053e823e8ac3db6"
            )

            assert commit.sha == "6dcb09b5b57875f334f61aeae053e823e8ac3db6"
            assert commit.message == "Fix all the bugs"
            assert commit.author == "Monalisa Octocat"

    def test_capabilities(self, driver):
        """Test driver capabilities."""
        capabilities = driver.capabilities
        assert len(capabilities) > 0
        assert "pull_requests" in [c.value for c in capabilities]
        assert "commits" in [c.value for c in capabilities]

    def test_platform_type(self, driver):
        """Test platform type."""
        assert driver.platform_type == PlatformType.GITHUB


class TestGitLabDriver:
    """Test GitLab driver."""

    @pytest.fixture
    def config(self):
        """Create GitLab config."""
        return PlatformConfig(
            api_version="v4",
            base_url_api="https://gitlab.com/api/v4",
            base_url_web="https://gitlab.com",
        )

    @pytest.fixture
    def driver(self, config):
        """Create GitLab driver."""
        return GitLabDriver(config, token="test-token")

    @pytest.mark.asyncio
    async def test_get_repository_info(self, driver):
        """Test getting repository information."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = GITLAB_PROJECT_RESPONSE

            repo_info = await driver.get_repository_info("twitter", "flight")

            assert isinstance(repo_info, RepositoryInfo)
            assert repo_info.name == "Flight"
            assert repo_info.platform == PlatformType.GITLAB
            assert repo_info.has_issues is True

    def test_project_id_conversion(self, driver):
        """Test GitLab project ID conversion."""
        project_id = driver._get_project_id("owner", "repo")
        assert project_id == "owner%2Frepo"

    def test_platform_type(self, driver):
        """Test platform type."""
        assert driver.platform_type == PlatformType.GITLAB


class TestBitbucketDriver:
    """Test Bitbucket driver."""

    @pytest.fixture
    def config(self):
        """Create Bitbucket config."""
        return PlatformConfig(
            api_version="2.0",
            base_url_api="https://api.bitbucket.org/2.0",
            base_url_web="https://bitbucket.org",
        )

    @pytest.fixture
    def driver(self, config):
        """Create Bitbucket driver."""
        return BitbucketDriver(config, token="test-token")

    @pytest.mark.asyncio
    async def test_get_repository_info(self, driver):
        """Test getting repository information."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = BITBUCKET_REPO_RESPONSE

            repo_info = await driver.get_repository_info("octocat", "Hello-World")

            assert isinstance(repo_info, RepositoryInfo)
            assert repo_info.name == "Hello-World"
            assert repo_info.platform == PlatformType.BITBUCKET
            assert repo_info.is_private is False

    def test_platform_type(self, driver):
        """Test platform type."""
        assert driver.platform_type == PlatformType.BITBUCKET


class TestGiteaDriver:
    """Test Gitea driver."""

    @pytest.fixture
    def config(self):
        """Create Gitea config."""
        return PlatformConfig(
            api_version="1.0",
            base_url_api="https://gitea.example.com/api/v1",
            base_url_web="https://gitea.example.com",
        )

    @pytest.fixture
    def driver(self, config):
        """Create Gitea driver."""
        return GiteaDriver(config, token="test-token")

    @pytest.mark.asyncio
    async def test_get_repository_info(self, driver):
        """Test getting repository information."""
        with patch.object(driver, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = GITEA_REPO_RESPONSE

            repo_info = await driver.get_repository_info("octocat", "Hello-World")

            assert isinstance(repo_info, RepositoryInfo)
            assert repo_info.owner == "octocat"
            assert repo_info.name == "Hello-World"
            assert repo_info.platform == PlatformType.GITEA

    def test_platform_type(self, driver):
        """Test platform type."""
        assert driver.platform_type == PlatformType.GITEA


class TestDriverIntegration:
    """Test driver integration."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test driver health checks."""
        config = PlatformConfig(
            api_version="2022-11-28",
            base_url_api="https://api.github.com",
            base_url_web="https://github.com",
        )
        driver = GitHubDriver(config)

        health = driver.health_check()
        assert health["status"] == "healthy"
        assert health["platform"] == "github"
        assert "response_time_ms" in health

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test driver context manager."""
        config = PlatformConfig(
            api_version="2022-11-28",
            base_url_api="https://api.github.com",
            base_url_web="https://github.com",
        )

        with GitHubDriver(config) as driver:
            assert driver is not None
            assert driver.platform_type == PlatformType.GITHUB
