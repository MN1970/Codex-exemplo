"""Bitbucket platform driver."""

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


class BitbucketDriver(BasePlatformDriver):
    """Driver for Bitbucket platform."""

    def __init__(self, config: PlatformConfig, token: Optional[str] = None):
        """Initialize Bitbucket driver."""
        super().__init__(config, token)
        self._platform_type = PlatformType.BITBUCKET
        self._capabilities = [
            DriverCapability.PULL_REQUESTS,
            DriverCapability.ISSUES,
            DriverCapability.COMMITS,
            DriverCapability.PIPELINES,
            DriverCapability.WEBHOOKS,
            DriverCapability.DEPLOYMENTS,
            DriverCapability.ENVIRONMENTS,
        ]
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "PAL-BitbucketDriver/1.0",
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

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
        """Get Bitbucket repository information."""
        url = f"{self.config.base_url_api}/repositories/{owner}/{repo}"
        data = await self._request("GET", url)

        return RepositoryInfo(
            owner=data["project"]["key"],
            name=data["slug"],
            url=data["links"]["html"][0]["href"],
            platform=PlatformType.BITBUCKET,
            is_private=data["is_private"],
            default_branch=data["mainbranch"]["name"],
            has_wiki=False,
            has_issues=False,
            has_discussions=False,
        )

    async def list_pull_requests(
        self, owner: str, repo: str, state: str = "OPEN", limit: int = 50
    ) -> List[PullRequest]:
        """List Bitbucket pull requests."""
        url = f"{self.config.base_url_api}/repositories/{owner}/{repo}/pullrequests"
        params = {"state": state, "pagelen": min(limit, 50), "sort": "-updated_on"}

        prs = []
        response_data = await self._request("GET", url, params=params)
        for pr_data in response_data.get("values", []):
            prs.append(
                PullRequest(
                    id=pr_data["id"],
                    number=pr_data["id"],
                    title=pr_data["title"],
                    description=pr_data.get("description", "") or "",
                    state=pr_data["state"],
                    source_branch=pr_data["source"]["branch"]["name"],
                    target_branch=pr_data["destination"]["branch"]["name"],
                    author=pr_data["author"]["username"],
                    created_at=pr_data["created_on"],
                    updated_at=pr_data["updated_on"],
                    merged_at=pr_data.get("merge_commit", {}).get("hash"),
                    review_count=len(pr_data.get("reviewers", [])),
                )
            )
        return prs

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> PullRequest:
        """Get a specific Bitbucket pull request."""
        url = (
            f"{self.config.base_url_api}/repositories/{owner}/{repo}/"
            f"pullrequests/{pr_number}"
        )
        pr_data = await self._request("GET", url)

        return PullRequest(
            id=pr_data["id"],
            number=pr_data["id"],
            title=pr_data["title"],
            description=pr_data.get("description", "") or "",
            state=pr_data["state"],
            source_branch=pr_data["source"]["branch"]["name"],
            target_branch=pr_data["destination"]["branch"]["name"],
            author=pr_data["author"]["username"],
            created_at=pr_data["created_on"],
            updated_at=pr_data["updated_on"],
            merged_at=pr_data.get("merge_commit", {}).get("hash"),
            review_count=len(pr_data.get("reviewers", [])),
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
        """Create a Bitbucket pull request."""
        url = (
            f"{self.config.base_url_api}/repositories/{owner}/{repo}/pullrequests"
        )
        payload = {
            "title": title,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": target_branch}},
            "description": description,
        }

        pr_data = await self._request("POST", url, json=payload)
        return PullRequest(
            id=pr_data["id"],
            number=pr_data["id"],
            title=pr_data["title"],
            description=pr_data.get("description", "") or "",
            state=pr_data["state"],
            source_branch=pr_data["source"]["branch"]["name"],
            target_branch=pr_data["destination"]["branch"]["name"],
            author=pr_data["author"]["username"],
            created_at=pr_data["created_on"],
            updated_at=pr_data["updated_on"],
            labels=labels or [],
        )

    async def list_commits(
        self, owner: str, repo: str, branch: str = None, limit: int = 50
    ) -> List[CommitInfo]:
        """List commits in a repository."""
        url = f"{self.config.base_url_api}/repositories/{owner}/{repo}/commits"
        params = {"pagelen": min(limit, 50)}
        if branch:
            params["include"] = branch

        commits = []
        data = await self._request("GET", url, params=params)
        for commit in data.get("values", []):
            commits.append(
                CommitInfo(
                    sha=commit["hash"],
                    message=commit["message"],
                    author=commit["author"]["user"]["display_name"],
                    author_email=commit["author"]["raw"].split("<")[1].rstrip(">"),
                    committed_at=commit["date"],
                    parent_shas=[p["hash"] for p in commit.get("parents", [])],
                    url=commit["links"]["html"]["href"],
                )
            )
        return commits

    async def get_commit(self, owner: str, repo: str, sha: str) -> CommitInfo:
        """Get a specific commit."""
        url = (
            f"{self.config.base_url_api}/repositories/{owner}/{repo}/commit/{sha}"
        )
        data = await self._request("GET", url)

        return CommitInfo(
            sha=data["hash"],
            message=data["message"],
            author=data["author"]["user"]["display_name"],
            author_email=data["author"]["raw"].split("<")[1].rstrip(">"),
            committed_at=data["date"],
            parent_shas=[p["hash"] for p in data.get("parents", [])],
            url=data["links"]["html"]["href"],
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
        url = (
            f"{self.config.base_url_api}/repositories/{owner}/{repo}/"
            f"pipelines"
        )
        params = {"pagelen": min(limit, 50), "sort": "-created_on"}

        runs = []
        data = await self._request("GET", url, params=params)
        for pipeline in data.get("values", []):
            duration = 0
            if pipeline.get("completed_on"):
                created = datetime.fromisoformat(
                    pipeline["created_on"].replace("Z", "+00:00")
                )
                completed = datetime.fromisoformat(
                    pipeline["completed_on"].replace("Z", "+00:00")
                )
                duration = int((completed - created).total_seconds())

            runs.append(
                WorkflowRun(
                    id=pipeline["uuid"],
                    name=f"Pipeline {pipeline['uuid']}",
                    status=pipeline["state"],
                    conclusion=pipeline.get("result", {}).get("name"),
                    branch=pipeline.get("target", {}).get("ref_name", ""),
                    created_at=pipeline["created_on"],
                    updated_at=pipeline.get("completed_on", pipeline["created_on"]),
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
        webhook_url = (
            f"{self.config.base_url_api}/repositories/{owner}/{repo}/hooks"
        )
        payload = {
            "description": "PAL Webhook",
            "url": url,
            "active": True,
            "events": events,
        }

        data = await self._request("POST", webhook_url, json=payload)
        return {
            "id": data["uuid"],
            "url": data["url"],
            "events": data["events"],
            "created_at": data.get("created_on"),
        }

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
