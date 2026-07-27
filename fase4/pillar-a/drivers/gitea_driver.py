"""Gitea platform driver."""

import asyncio
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import (
    BasePlatformDriver,
    PlatformType,
    DriverCapability,
    PlatformConfig,
    RepositoryInfo,
    PullRequest,
    CommitInfo,
    WorkflowRun,
)


class GiteaDriver(BasePlatformDriver):
    """Driver for Gitea platform."""

    def __init__(self, config: PlatformConfig, token: Optional[str] = None):
        """Initialize Gitea driver."""
        super().__init__(config, token)
        self._platform_type = PlatformType.GITEA
        self._capabilities = [
            DriverCapability.PULL_REQUESTS,
            DriverCapability.ISSUES,
            DriverCapability.COMMITS,
            DriverCapability.WEBHOOKS,
            DriverCapability.DEPLOYMENTS,
        ]
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "PAL-GiteaDriver/1.0",
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            timeout = aiohttp.ClientTimeout(seconds=self.config.timeout_seconds)
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(ssl=self.config.verify_ssl),
            )
        return self._session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
    )
    async def _request(self, method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        session = await self._get_session()
        self._request_count += 1
        self._last_request_time = time.time()

        async with session.request(method, url, **kwargs) as response:
            if response.status == 404:
                raise ValueError(f"Resource not found: {url}")
            if response.status == 401:
                raise ValueError("Unauthorized: Invalid token")
            if response.status == 403:
                raise ValueError("Forbidden: Permission denied")

            response.raise_for_status()
            return await response.json()

    async def get_repository_info(self, owner: str, repo: str) -> RepositoryInfo:
        """Get Gitea repository information."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}"
        data = await self._request("GET", url)

        return RepositoryInfo(
            owner=data["owner"]["username"],
            name=data["name"],
            url=data["html_url"],
            platform=PlatformType.GITEA,
            is_private=data["private"],
            default_branch=data["default_branch"],
            has_wiki=data["has_wiki"],
            has_issues=data["has_issues"],
            has_discussions=data.get("has_discussions", False),
        )

    async def list_pull_requests(
        self, owner: str, repo: str, state: str = "open", limit: int = 50
    ) -> List[PullRequest]:
        """List Gitea pull requests."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "limit": min(limit, 50), "sort": "recentupdate"}

        prs = []
        response_data = await self._request("GET", url, params=params)
        for pr_data in response_data:
            prs.append(
                PullRequest(
                    id=pr_data["id"],
                    number=pr_data["number"],
                    title=pr_data["title"],
                    description=pr_data["body"] or "",
                    state=pr_data["state"],
                    source_branch=pr_data["head"]["ref"],
                    target_branch=pr_data["base"]["ref"],
                    author=pr_data["user"]["username"],
                    created_at=pr_data["created_at"],
                    updated_at=pr_data["updated_at"],
                    merged_at=pr_data.get("merged_at"),
                    labels=[label["name"] for label in pr_data.get("labels", [])],
                )
            )
        return prs

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> PullRequest:
        """Get a specific Gitea pull request."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls/{pr_number}"
        pr_data = await self._request("GET", url)

        return PullRequest(
            id=pr_data["id"],
            number=pr_data["number"],
            title=pr_data["title"],
            description=pr_data["body"] or "",
            state=pr_data["state"],
            source_branch=pr_data["head"]["ref"],
            target_branch=pr_data["base"]["ref"],
            author=pr_data["user"]["username"],
            created_at=pr_data["created_at"],
            updated_at=pr_data["updated_at"],
            merged_at=pr_data.get("merged_at"),
            labels=[label["name"] for label in pr_data.get("labels", [])],
        )

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
        """Create a Gitea pull request."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls"
        payload = {
            "title": title,
            "head": source_branch,
            "base": target_branch,
            "body": description,
            "labels": [{"name": label} for label in (labels or [])],
        }

        pr_data = await self._request("POST", url, json=payload)
        return PullRequest(
            id=pr_data["id"],
            number=pr_data["number"],
            title=pr_data["title"],
            description=pr_data["body"] or "",
            state=pr_data["state"],
            source_branch=pr_data["head"]["ref"],
            target_branch=pr_data["base"]["ref"],
            author=pr_data["user"]["username"],
            created_at=pr_data["created_at"],
            updated_at=pr_data["updated_at"],
            labels=labels or [],
        )

    async def list_commits(
        self, owner: str, repo: str, branch: str = None, limit: int = 50
    ) -> List[CommitInfo]:
        """List commits in a repository."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/commits"
        params = {"limit": min(limit, 50)}
        if branch:
            params["sha"] = branch

        commits = []
        data = await self._request("GET", url, params=params)
        for commit in data:
            commits.append(
                CommitInfo(
                    sha=commit["sha"],
                    message=commit["commit"]["message"],
                    author=commit["commit"]["author"]["name"],
                    author_email=commit["commit"]["author"]["email"],
                    committed_at=commit["commit"]["author"]["date"],
                    parent_shas=[p["sha"] for p in commit.get("parents", [])],
                    url=commit["html_url"],
                )
            )
        return commits

    async def get_commit(self, owner: str, repo: str, sha: str) -> CommitInfo:
        """Get a specific commit."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/commits/{sha}"
        data = await self._request("GET", url)

        return CommitInfo(
            sha=data["sha"],
            message=data["commit"]["message"],
            author=data["commit"]["author"]["name"],
            author_email=data["commit"]["author"]["email"],
            committed_at=data["commit"]["author"]["date"],
            parent_shas=[p["sha"] for p in data.get("parents", [])],
            url=data["html_url"],
        )

    async def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: str = None,
        status: str = None,
        limit: int = 50,
    ) -> List[WorkflowRun]:
        """List workflow runs (Gitea Actions)."""
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/actions/runs"
        params = {"limit": min(limit, 50)}
        if status:
            params["status"] = status

        runs = []
        data = await self._request("GET", url, params=params)
        for run_data in data.get("workflow_runs", []):
            duration = 0
            if run_data.get("updated_at"):
                created = datetime.fromisoformat(
                    run_data["created_at"].replace("Z", "+00:00")
                )
                updated = datetime.fromisoformat(
                    run_data["updated_at"].replace("Z", "+00:00")
                )
                duration = int((updated - created).total_seconds())

            runs.append(
                WorkflowRun(
                    id=run_data["id"],
                    name=run_data["name"],
                    status=run_data["status"],
                    conclusion=run_data.get("conclusion"),
                    branch=run_data.get("head_branch", ""),
                    created_at=run_data["created_at"],
                    updated_at=run_data["updated_at"],
                    duration_seconds=duration,
                )
            )
        return runs

    async def create_webhook(
        self,
        owner: str,
        repo: str,
        url: str,
        events: List[str],
        secret: str = None,
    ) -> Dict[str, Any]:
        """Create a webhook."""
        webhook_url = f"{self.config.base_url_api}/repos/{owner}/{repo}/hooks"
        payload = {
            "type": "gitea",
            "config": {
                "url": url,
                "http_method": "POST",
                "content_type": "json",
            },
            "events": events,
            "active": True,
        }
        if secret:
            payload["config"]["secret"] = secret

        data = await self._request("POST", webhook_url, json=payload)
        return {
            "id": data["id"],
            "url": data["config"]["url"],
            "events": data["events"],
            "created_at": data.get("created_at"),
        }

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
