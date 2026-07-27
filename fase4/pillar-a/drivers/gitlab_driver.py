"""GitLab platform driver."""

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


class GitLabDriver(BasePlatformDriver):
    """Driver for GitLab platform."""

    def __init__(self, config: PlatformConfig, token: Optional[str] = None):
        """Initialize GitLab driver.

        Args:
            config: Platform configuration
            token: GitLab API token
        """
        super().__init__(config, token)
        self._platform_type = PlatformType.GITLAB
        self._capabilities = [
            DriverCapability.MERGE_REQUESTS,
            DriverCapability.ISSUES,
            DriverCapability.COMMITS,
            DriverCapability.PIPELINES,
            DriverCapability.WEBHOOKS,
            DriverCapability.DEPLOYMENTS,
            DriverCapability.ENVIRONMENTS,
            DriverCapability.DISCUSSIONS,
            DriverCapability.PACKAGES,
        ]
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "PAL-GitLabDriver/1.0",
            }
            if self.token:
                headers["PRIVATE-TOKEN"] = self.token

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

    def _get_project_id(self, owner: str, repo: str) -> str:
        """Convert owner/repo to GitLab project ID."""
        return f"{owner}%2F{repo}"

    async def get_repository_info(
        self, owner: str, repo: str
    ) -> RepositoryInfo:
        """Get GitLab repository information."""
        project_id = self._get_project_id(owner, repo)
        url = f"{self.config.base_url_api}/projects/{project_id}"
        data = await self._request("GET", url)

        return RepositoryInfo(
            owner=data["path_with_namespace"].split("/")[0],
            name=data["name"],
            url=data["web_url"],
            platform=PlatformType.GITLAB,
            is_private=data["visibility"] != "public",
            default_branch=data["default_branch"],
            has_wiki=data["wiki_enabled"],
            has_issues=data["issues_enabled"],
            has_discussions=data.get("discussions_enabled", False),
        )

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "opened",
        limit: int = 50,
    ) -> List[PullRequest]:
        """List GitLab merge requests."""
        project_id = self._get_project_id(owner, repo)
        url = f"{self.config.base_url_api}/projects/{project_id}/merge_requests"
        params = {
            "state": state,
            "per_page": min(limit, 100),
            "order_by": "updated_at",
            "sort": "desc",
        }

        prs = []
        response_data = await self._request("GET", url, params=params)
        for mr_data in response_data:
            prs.append(
                PullRequest(
                    id=mr_data["id"],
                    number=mr_data["iid"],
                    title=mr_data["title"],
                    description=mr_data["description"] or "",
                    state=mr_data["state"],
                    source_branch=mr_data["source_branch"],
                    target_branch=mr_data["target_branch"],
                    author=mr_data["author"]["username"],
                    created_at=mr_data["created_at"],
                    updated_at=mr_data["updated_at"],
                    merged_at=mr_data.get("merged_at"),
                    labels=[label for label in mr_data.get("labels", [])],
                )
            )
        return prs

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> PullRequest:
        """Get a specific GitLab merge request."""
        project_id = self._get_project_id(owner, repo)
        url = (
            f"{self.config.base_url_api}/projects/{project_id}/"
            f"merge_requests/{pr_number}"
        )
        mr_data = await self._request("GET", url)

        return PullRequest(
            id=mr_data["id"],
            number=mr_data["iid"],
            title=mr_data["title"],
            description=mr_data["description"] or "",
            state=mr_data["state"],
            source_branch=mr_data["source_branch"],
            target_branch=mr_data["target_branch"],
            author=mr_data["author"]["username"],
            created_at=mr_data["created_at"],
            updated_at=mr_data["updated_at"],
            merged_at=mr_data.get("merged_at"),
            review_count=len(mr_data.get("approvals", {}).get("approved_by", [])),
            labels=[label for label in mr_data.get("labels", [])],
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
        """Create a GitLab merge request."""
        project_id = self._get_project_id(owner, repo)
        url = (
            f"{self.config.base_url_api}/projects/{project_id}/merge_requests"
        )
        payload = {
            "title": title,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "description": description,
        }
        if labels:
            payload["labels"] = ",".join(labels)

        mr_data = await self._request("POST", url, json=payload)
        return PullRequest(
            id=mr_data["id"],
            number=mr_data["iid"],
            title=mr_data["title"],
            description=mr_data["description"] or "",
            state=mr_data["state"],
            source_branch=mr_data["source_branch"],
            target_branch=mr_data["target_branch"],
            author=mr_data["author"]["username"],
            created_at=mr_data["created_at"],
            updated_at=mr_data["updated_at"],
            labels=labels or [],
        )

    async def list_commits(
        self,
        owner: str,
        repo: str,
        branch: str = None,
        limit: int = 50,
    ) -> List[CommitInfo]:
        """List commits in a repository."""
        project_id = self._get_project_id(owner, repo)
        url = f"{self.config.base_url_api}/projects/{project_id}/repository/commits"
        params = {"per_page": min(limit, 100)}
        if branch:
            params["ref_name"] = branch

        commits = []
        commit_data = await self._request("GET", url, params=params)
        for commit in commit_data:
            commits.append(
                CommitInfo(
                    sha=commit["id"],
                    message=commit["message"],
                    author=commit["author_name"],
                    author_email=commit["author_email"],
                    committed_at=commit["created_at"],
                    parent_shas=commit.get("parent_ids", []),
                    url=commit["web_url"],
                )
            )
        return commits

    async def get_commit(
        self, owner: str, repo: str, sha: str
    ) -> CommitInfo:
        """Get a specific commit."""
        project_id = self._get_project_id(owner, repo)
        url = (
            f"{self.config.base_url_api}/projects/{project_id}/"
            f"repository/commits/{sha}"
        )
        data = await self._request("GET", url)

        return CommitInfo(
            sha=data["id"],
            message=data["message"],
            author=data["author_name"],
            author_email=data["author_email"],
            committed_at=data["created_at"],
            parent_shas=data.get("parent_ids", []),
            url=data["web_url"],
        )

    async def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: str = None,
        status: str = None,
        limit: int = 50,
    ) -> List[WorkflowRun]:
        """List pipeline runs."""
        project_id = self._get_project_id(owner, repo)
        url = f"{self.config.base_url_api}/projects/{project_id}/pipelines"
        params = {"per_page": min(limit, 100), "order_by": "updated_at", "sort": "desc"}
        if status:
            params["status"] = status

        runs = []
        data = await self._request("GET", url, params=params)
        for pipeline in data:
            duration = 0
            if pipeline.get("updated_at"):
                created = datetime.fromisoformat(
                    pipeline["created_at"].replace("Z", "+00:00")
                )
                updated = datetime.fromisoformat(
                    pipeline["updated_at"].replace("Z", "+00:00")
                )
                duration = int((updated - created).total_seconds())

            runs.append(
                WorkflowRun(
                    id=pipeline["id"],
                    name=f"Pipeline {pipeline['id']}",
                    status=pipeline["status"],
                    conclusion=None,
                    branch=pipeline.get("ref", ""),
                    created_at=pipeline["created_at"],
                    updated_at=pipeline["updated_at"],
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
        project_id = self._get_project_id(owner, repo)
        webhook_url = (
            f"{self.config.base_url_api}/projects/{project_id}/hooks"
        )
        payload = {
            "url": url,
            "push_events": "push_events" in events,
            "issues_events": "issues" in events,
            "merge_requests_events": "merge_request" in events,
            "wiki_page_events": "wiki" in events,
            "pipeline_events": "pipeline" in events,
            "token": secret or "",
        }

        data = await self._request("POST", webhook_url, json=payload)
        return {
            "id": data["id"],
            "url": data["url"],
            "events": events,
            "created_at": data["created_at"],
        }

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
