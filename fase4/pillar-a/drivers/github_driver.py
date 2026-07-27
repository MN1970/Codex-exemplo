"""GitHub platform driver."""

import asyncio
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

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


class GitHubDriver(BasePlatformDriver):
    """Driver for GitHub platform."""

    def __init__(self, config: PlatformConfig, token: Optional[str] = None):
        """Initialize GitHub driver.

        Args:
            config: Platform configuration
            token: GitHub API token
        """
        super().__init__(config, token)
        self._platform_type = PlatformType.GITHUB
        self._capabilities = [
            DriverCapability.PULL_REQUESTS,
            DriverCapability.ISSUES,
            DriverCapability.COMMITS,
            DriverCapability.WORKFLOWS,
            DriverCapability.WEBHOOKS,
            DriverCapability.STATUSES,
            DriverCapability.CHECKS,
            DriverCapability.DEPLOYMENTS,
            DriverCapability.ENVIRONMENTS,
            DriverCapability.DISCUSSIONS,
        ]
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "PAL-GithubDriver/1.0",
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
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments to pass to the session

        Returns:
            Response JSON data

        Raises:
            aiohttp.ClientError: If the request fails
        """
        session = await self._get_session()
        self._request_count += 1
        self._last_request_time = time.time()

        async with session.request(method, url, **kwargs) as response:
            if response.status == 404:
                raise ValueError(f"Resource not found: {url}")
            if response.status == 401:
                raise ValueError("Unauthorized: Invalid token")
            if response.status == 403:
                raise ValueError("Forbidden: Rate limit exceeded or permission denied")

            response.raise_for_status()
            return await response.json()

    async def get_repository_info(
        self, owner: str, repo: str
    ) -> RepositoryInfo:
        """Get GitHub repository information.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository information
        """
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}"
        data = await self._request("GET", url)

        return RepositoryInfo(
            owner=data["owner"]["login"],
            name=data["name"],
            url=data["html_url"],
            platform=PlatformType.GITHUB,
            is_private=data["private"],
            default_branch=data["default_branch"],
            has_wiki=data["has_wiki"],
            has_issues=data["has_issues"],
            has_discussions=data["has_discussions"],
        )

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 50,
    ) -> List[PullRequest]:
        """List GitHub pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state (open, closed, all)
            limit: Maximum number of results

        Returns:
            List of pull requests
        """
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "per_page": min(limit, 100),
            "sort": "updated",
            "direction": "desc",
        }

        prs = []
        async with await self._get_session() as _:
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
                        author=pr_data["user"]["login"],
                        created_at=pr_data["created_at"],
                        updated_at=pr_data["updated_at"],
                        merged_at=pr_data.get("merged_at"),
                        review_count=pr_data.get("review_comments", 0),
                        labels=[label["name"] for label in pr_data.get("labels", [])],
                    )
                )
        return prs

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> PullRequest:
        """Get a specific GitHub pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request information
        """
        url = (
            f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls/{pr_number}"
        )
        pr_data = await self._request("GET", url)

        # Get check runs count
        checks_url = (
            f"{self.config.base_url_api}/repos/{owner}/{repo}/"
            f"commits/{pr_data['head']['sha']}/check-runs"
        )
        try:
            checks_data = await self._request("GET", checks_url)
            check_runs = len(checks_data.get("check_runs", []))
        except Exception:
            check_runs = 0

        return PullRequest(
            id=pr_data["id"],
            number=pr_data["number"],
            title=pr_data["title"],
            description=pr_data["body"] or "",
            state=pr_data["state"],
            source_branch=pr_data["head"]["ref"],
            target_branch=pr_data["base"]["ref"],
            author=pr_data["user"]["login"],
            created_at=pr_data["created_at"],
            updated_at=pr_data["updated_at"],
            merged_at=pr_data.get("merged_at"),
            review_count=pr_data.get("review_comments", 0),
            check_runs=check_runs,
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
        """Create a GitHub pull request.

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
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/pulls"
        payload = {
            "title": title,
            "head": source_branch,
            "base": target_branch,
            "body": description,
        }

        pr_data = await self._request("POST", url, json=payload)
        pr = PullRequest(
            id=pr_data["id"],
            number=pr_data["number"],
            title=pr_data["title"],
            description=pr_data["body"] or "",
            state=pr_data["state"],
            source_branch=pr_data["head"]["ref"],
            target_branch=pr_data["base"]["ref"],
            author=pr_data["user"]["login"],
            created_at=pr_data["created_at"],
            updated_at=pr_data["updated_at"],
            labels=labels or [],
        )

        # Add labels if provided
        if labels:
            labels_url = (
                f"{self.config.base_url_api}/repos/{owner}/{repo}/"
                f"issues/{pr_data['number']}/labels"
            )
            await self._request("POST", labels_url, json={"labels": labels})

        return pr

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
            branch: Filter by branch
            limit: Maximum number of results

        Returns:
            List of commits
        """
        url = f"{self.config.base_url_api}/repos/{owner}/{repo}/commits"
        params = {
            "per_page": min(limit, 100),
        }
        if branch:
            params["sha"] = branch

        commits = []
        commit_data = await self._request("GET", url, params=params)
        for commit in commit_data:
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
        """List workflow runs.

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Filter by workflow ID
            status: Filter by status
            limit: Maximum number of results

        Returns:
            List of workflow runs
        """
        if workflow_id:
            url = (
                f"{self.config.base_url_api}/repos/{owner}/{repo}/"
                f"actions/workflows/{workflow_id}/runs"
            )
        else:
            url = f"{self.config.base_url_api}/repos/{owner}/{repo}/actions/runs"

        params = {"per_page": min(limit, 100)}
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
                    branch=run_data["head_branch"],
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
        """Create a webhook.

        Args:
            owner: Repository owner
            repo: Repository name
            url: Webhook URL
            events: List of events
            secret: Optional webhook secret

        Returns:
            Webhook information
        """
        webhook_url = (
            f"{self.config.base_url_api}/repos/{owner}/{repo}/hooks"
        )
        payload = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": url,
                "content_type": "json",
            },
        }
        if secret:
            payload["config"]["secret"] = secret

        data = await self._request("POST", webhook_url, json=payload)
        return {
            "id": data["id"],
            "url": data["url"],
            "events": data["events"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
        }

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
