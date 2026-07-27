"""Base driver for all platform implementations."""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


class PlatformType(str, Enum):
    """Enumeration of supported git platforms."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    GITEA = "gitea"


class DriverCapability(str, Enum):
    """Supported capabilities for each platform driver."""
    PULL_REQUESTS = "pull_requests"
    MERGE_REQUESTS = "merge_requests"
    ISSUES = "issues"
    COMMITS = "commits"
    WORKFLOWS = "workflows"
    PIPELINES = "pipelines"
    WEBHOOKS = "webhooks"
    STATUSES = "statuses"
    CHECKS = "checks"
    DEPLOYMENTS = "deployments"
    ENVIRONMENTS = "environments"
    DISCUSSIONS = "discussions"
    PACKAGES = "packages"
    ACTIONS = "actions"


@dataclass
class PlatformConfig:
    """Configuration for a platform driver."""
    api_version: str
    base_url_api: str
    base_url_web: str
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    rate_limit_handling: str = "backoff"
    verify_ssl: bool = True
    ca_bundle_path: Optional[str] = None


@dataclass
class RepositoryInfo:
    """Information about a repository."""
    owner: str
    name: str
    url: str
    platform: PlatformType
    is_private: bool
    default_branch: str
    has_wiki: bool
    has_issues: bool
    has_discussions: bool


@dataclass
class PullRequest:
    """Pull request information."""
    id: Union[int, str]
    number: int
    title: str
    description: str
    state: str  # open, closed, merged, draft
    source_branch: str
    target_branch: str
    author: str
    created_at: str
    updated_at: str
    merged_at: Optional[str] = None
    review_count: int = 0
    check_runs: int = 0
    labels: List[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class CommitInfo:
    """Commit information."""
    sha: str
    message: str
    author: str
    author_email: str
    committed_at: str
    parent_shas: List[str]
    url: str


@dataclass
class WorkflowRun:
    """Workflow/Pipeline run information."""
    id: Union[int, str]
    name: str
    status: str  # pending, running, success, failure, cancelled
    conclusion: Optional[str]
    branch: str
    created_at: str
    updated_at: str
    duration_seconds: int
    artifacts: int = 0


class BasePlatformDriver(ABC):
    """Abstract base driver for platform implementations."""

    def __init__(self, config: PlatformConfig, token: Optional[str] = None):
        """Initialize the driver.

        Args:
            config: Platform configuration
            token: Authentication token (optional)
        """
        self.config = config
        self.token = token
        self.session = None
        self._request_count = 0
        self._last_request_time = None
        self._capabilities: List[DriverCapability] = []

    @property
    def platform_type(self) -> PlatformType:
        """Get the platform type."""
        return self._platform_type

    @property
    def capabilities(self) -> List[DriverCapability]:
        """Get the driver's capabilities."""
        return self._capabilities

    def health_check(self) -> Dict[str, Any]:
        """Check platform API health.

        Returns:
            Health status information
        """
        return {
            "status": "healthy",
            "platform": self.platform_type.value,
            "response_time_ms": 0,
            "timestamp": time.time(),
        }

    @abstractmethod
    async def get_repository_info(
        self, owner: str, repo: str
    ) -> RepositoryInfo:
        """Get repository information.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository information
        """
        pass

    @abstractmethod
    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 50,
    ) -> List[PullRequest]:
        """List pull requests in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state (open, closed, all)
            limit: Maximum number of results

        Returns:
            List of pull requests
        """
        pass

    @abstractmethod
    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> PullRequest:
        """Get a specific pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request information
        """
        pass

    @abstractmethod
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = "",
        labels: List[str] = None,
    ) -> PullRequest:
        """Create a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            source_branch: Source branch name
            target_branch: Target branch name
            description: PR description
            labels: List of labels

        Returns:
            Created pull request
        """
        pass

    @abstractmethod
    async def list_commits(
        self,
        owner: str,
        repo: str,
        branch: str = None,
        limit: int = 50,
    ) -> List[CommitInfo]:
        """List commits in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Filter by branch (optional)
            limit: Maximum number of results

        Returns:
            List of commits
        """
        pass

    @abstractmethod
    async def get_commit(
        self, owner: str, repo: str, sha: str
    ) -> CommitInfo:
        """Get a specific commit.

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA

        Returns:
            Commit information
        """
        pass

    @abstractmethod
    async def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: str = None,
        status: str = None,
        limit: int = 50,
    ) -> List[WorkflowRun]:
        """List workflow runs.

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Filter by workflow ID (optional)
            status: Filter by status (optional)
            limit: Maximum number of results

        Returns:
            List of workflow runs
        """
        pass

    @abstractmethod
    async def create_webhook(
        self,
        owner: str,
        repo: str,
        url: str,
        events: List[str],
        secret: str = None,
    ) -> Dict[str, Any]:
        """Create a webhook.

        Args:
            owner: Repository owner
            repo: Repository name
            url: Webhook URL
            events: List of events to subscribe to
            secret: Optional webhook secret

        Returns:
            Webhook information
        """
        pass

    async def close(self):
        """Close the driver session."""
        if self.session:
            await self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            asyncio.run(self.close())
        except RuntimeError:
            pass
