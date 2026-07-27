# Platform Abstraction Layer - API Reference

## Quick Start

```python
import asyncio
from platform_abstraction_layer import get_pal

async def main():
    # Initialize PAL
    pal = get_pal()
    
    # Detect platform and get driver
    url = "https://github.com/octocat/Hello-World"
    driver, detection_time = await pal.detect_and_get_driver(url)
    print(f"Detected: {driver.platform_type} in {detection_time:.2f}ms")
    
    # Get repository info
    repo = await driver.get_repository_info("octocat", "Hello-World")
    print(f"Repository: {repo.name} ({repo.platform})")
    
    # List pull requests
    prs = await driver.list_pull_requests("octocat", "Hello-World")
    print(f"Found {len(prs)} pull requests")
    
    # Clean up
    await pal.close_all()

asyncio.run(main())
```

## Module: `platform_abstraction_layer`

### Class: `PlatformAbstractionLayer`

Main service class for PAL.

#### Constructor

```python
PlatformAbstractionLayer(config_path: Optional[str] = None) → PlatformAbstractionLayer
```

**Parameters:**
- `config_path` (str, optional): Path to YAML configuration file. Defaults to `config_schema.yaml`.

**Example:**
```python
pal = PlatformAbstractionLayer("/etc/pal/config.yaml")
```

#### Methods

##### `get_driver`
```python
async def get_driver(platform: PlatformType) -> BasePlatformDriver
```

Get a driver for the specified platform.

**Parameters:**
- `platform` (PlatformType): Platform type (GITHUB, GITLAB, BITBUCKET, GITEA)

**Returns:**
- (BasePlatformDriver): Initialized platform driver

**Raises:**
- ValueError: If platform not available or not enabled

**Example:**
```python
driver = await pal.get_driver(PlatformType.GITHUB)
```

##### `detect_and_get_driver`
```python
async def detect_and_get_driver(url: str) → Tuple[BasePlatformDriver, float]
```

Detect platform from URL and get appropriate driver.

**Parameters:**
- `url` (str): Repository URL

**Returns:**
- (Tuple[BasePlatformDriver, float]): Driver and detection time in milliseconds

**Raises:**
- ValueError: If platform cannot be detected or driver not available

**Example:**
```python
driver, latency = await pal.detect_and_get_driver("https://github.com/user/repo")
print(f"Detected in {latency:.2f}ms")
```

##### `health_check`
```python
async def health_check() → Dict[str, Any]
```

Check health of all configured drivers.

**Returns:**
- (Dict): Health status with platform-specific information

**Example:**
```python
health = await pal.health_check()
print(f"Overall status: {health['overall_status']}")
for platform, status in health['platforms'].items():
    print(f"  {platform}: {status['status']}")
```

##### `list_capabilities`
```python
async def list_capabilities() → Dict[str, List[str]]
```

List capabilities for each available platform.

**Returns:**
- (Dict): Mapping of platform names to capability lists

**Example:**
```python
caps = await pal.list_capabilities()
# {'github': ['pull_requests', 'issues', ...], 'gitlab': [...]}
```

##### `close_all`
```python
async def close_all() → None
```

Close all driver connections.

---

## Module: `drivers`

### Class: `BasePlatformDriver` (Abstract)

Base class for all platform drivers. Do not instantiate directly.

### Class: `GitHubDriver(BasePlatformDriver)`

Driver for GitHub platform.

#### Methods

##### `get_repository_info`
```python
async def get_repository_info(owner: str, repo: str) → RepositoryInfo
```

Get GitHub repository information.

**Parameters:**
- `owner` (str): Repository owner/organization
- `repo` (str): Repository name

**Returns:**
- (RepositoryInfo): Repository metadata

**Example:**
```python
driver = await pal.get_driver(PlatformType.GITHUB)
repo = await driver.get_repository_info("torvalds", "linux")
print(f"{repo.owner}/{repo.name}")
```

##### `list_pull_requests`
```python
async def list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    limit: int = 50
) → List[PullRequest]
```

List GitHub pull requests.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `state` (str): Filter by state ("open", "closed", "all")
- `limit` (int): Maximum results (1-100)

**Returns:**
- (List[PullRequest]): List of pull requests

**Example:**
```python
prs = await driver.list_pull_requests("django", "django", state="open", limit=50)
for pr in prs:
    print(f"#{pr.number}: {pr.title}")
```

##### `get_pull_request`
```python
async def get_pull_request(
    owner: str,
    repo: str,
    pr_number: int
) → PullRequest
```

Get a specific GitHub pull request.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `pr_number` (int): Pull request number

**Returns:**
- (PullRequest): Pull request details

**Example:**
```python
pr = await driver.get_pull_request("octocat", "Hello-World", 1347)
print(f"State: {pr.state}, Author: {pr.author}")
```

##### `create_pull_request`
```python
async def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    source_branch: str,
    target_branch: str,
    description: str = "",
    labels: List[str] = None
) → PullRequest
```

Create a GitHub pull request.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `title` (str): PR title
- `source_branch` (str): Source branch name
- `target_branch` (str): Target branch name
- `description` (str): PR description
- `labels` (List[str]): Labels to apply

**Returns:**
- (PullRequest): Created pull request

**Requires:** Authentication token

**Example:**
```python
pr = await driver.create_pull_request(
    "myorg", "myrepo",
    title="Fix: Update dependencies",
    source_branch="feature/deps",
    target_branch="main",
    description="Updates to latest stable versions",
    labels=["dependencies", "enhancement"]
)
```

##### `list_commits`
```python
async def list_commits(
    owner: str,
    repo: str,
    branch: str = None,
    limit: int = 50
) → List[CommitInfo]
```

List commits in a repository.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `branch` (str): Filter by branch
- `limit` (int): Maximum results

**Returns:**
- (List[CommitInfo]): List of commits

**Example:**
```python
commits = await driver.list_commits("octocat", "Hello-World", branch="main")
```

##### `get_commit`
```python
async def get_commit(
    owner: str,
    repo: str,
    sha: str
) → CommitInfo
```

Get a specific commit.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `sha` (str): Commit SHA

**Returns:**
- (CommitInfo): Commit details

**Example:**
```python
commit = await driver.get_commit("octocat", "Hello-World", "6dcb09b5...")
print(f"{commit.author}: {commit.message}")
```

##### `list_workflow_runs`
```python
async def list_workflow_runs(
    owner: str,
    repo: str,
    workflow_id: str = None,
    status: str = None,
    limit: int = 50
) → List[WorkflowRun]
```

List GitHub Actions workflow runs.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `workflow_id` (str): Filter by workflow
- `status` (str): Filter by status
- `limit` (int): Maximum results

**Returns:**
- (List[WorkflowRun]): Workflow runs

**Example:**
```python
runs = await driver.list_workflow_runs("octocat", "Hello-World", status="success")
```

##### `create_webhook`
```python
async def create_webhook(
    owner: str,
    repo: str,
    url: str,
    events: List[str],
    secret: str = None
) → Dict[str, Any]
```

Create a GitHub webhook.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `url` (str): Webhook URL
- `events` (List[str]): Events to subscribe to
- `secret` (str): Optional webhook secret

**Returns:**
- (Dict): Webhook information

**Requires:** Authentication token

**Example:**
```python
webhook = await driver.create_webhook(
    "myorg", "myrepo",
    url="https://example.com/webhook",
    events=["push", "pull_request"],
    secret="my-secret"
)
```

---

### Class: `GitLabDriver(BasePlatformDriver)`

Driver for GitLab platform. Similar interface to GitHub, with differences:
- Merge requests instead of pull requests
- Pipelines instead of workflows
- Uses different state values ("opened", "merged", "closed")

### Class: `BitbucketDriver(BasePlatformDriver)`

Driver for Bitbucket platform.

### Class: `GiteaDriver(BasePlatformDriver)`

Driver for Gitea platform (self-hosted or gitea.io).

---

## Module: `detection`

### Class: `PlatformDetector`

Platform detection service with caching.

#### Constructor

```python
PlatformDetector(use_git_cli_fallback: bool = True)
```

#### Methods

##### `detect_from_url`
```python
async def detect_from_url(url: str) → Tuple[PlatformType, float]
```

Detect platform from repository URL.

**Parameters:**
- `url` (str): Repository URL (https or git@)

**Returns:**
- (Tuple[PlatformType, float]): Platform and detection time (ms)

**Raises:**
- ValueError: If platform cannot be detected

**Performance:**
- Cache hit: <1ms
- Cache miss: <5ms
- Typical: <15ms

**Example:**
```python
detector = PlatformDetector()
platform, latency = await detector.detect_from_url("https://github.com/user/repo")
print(f"Detected {platform.value} in {latency:.2f}ms")
```

##### `detect_from_remote`
```python
async def detect_from_remote(remote_url: str = "origin") → Tuple[PlatformType, float]
```

Detect platform from git remote.

**Parameters:**
- `remote_url` (str): Git remote name

**Returns:**
- (Tuple[PlatformType, float]): Platform and detection time

**Raises:**
- ValueError: If git command fails

**Example:**
```python
platform, latency = await detector.detect_from_remote("origin")
```

##### `detect_from_config`
```python
async def detect_from_config(config: Dict[str, Any]) → Tuple[PlatformType, float]
```

Detect platform from configuration dict.

**Parameters:**
- `config` (Dict): Configuration with "platform" or "url" keys

**Returns:**
- (Tuple[PlatformType, float]): Platform and detection time

---

## Data Types

### PlatformType (Enum)
```python
class PlatformType(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    GITEA = "gitea"
```

### DriverCapability (Enum)
```python
class DriverCapability(str, Enum):
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
```

### RepositoryInfo (Dataclass)
```python
@dataclass
class RepositoryInfo:
    owner: str
    name: str
    url: str
    platform: PlatformType
    is_private: bool
    default_branch: str
    has_wiki: bool
    has_issues: bool
    has_discussions: bool
```

### PullRequest (Dataclass)
```python
@dataclass
class PullRequest:
    id: Union[int, str]
    number: int
    title: str
    description: str
    state: str  # "open", "closed", "merged", "draft"
    source_branch: str
    target_branch: str
    author: str
    created_at: str
    updated_at: str
    merged_at: Optional[str] = None
    review_count: int = 0
    check_runs: int = 0
    labels: List[str] = None
```

### CommitInfo (Dataclass)
```python
@dataclass
class CommitInfo:
    sha: str
    message: str
    author: str
    author_email: str
    committed_at: str
    parent_shas: List[str]
    url: str
```

### WorkflowRun (Dataclass)
```python
@dataclass
class WorkflowRun:
    id: Union[int, str]
    name: str
    status: str  # "pending", "running", "success", "failure", "cancelled"
    conclusion: Optional[str]
    branch: str
    created_at: str
    updated_at: str
    duration_seconds: int
    artifacts: int = 0
```

---

## Error Handling

### Common Exceptions

```python
ValueError
  ├─ "Unauthorized: Invalid token" → 401 Authentication
  ├─ "Forbidden: Rate limit exceeded" → 403 Rate limit
  ├─ "Resource not found" → 404 Not found
  ├─ "Cannot detect platform" → Detection failed
  └─ "Driver not available" → Platform not configured
```

### Example Error Handling

```python
try:
    repo = await driver.get_repository_info("invalid", "repo")
except ValueError as e:
    if "not found" in str(e):
        print("Repository does not exist")
    elif "Unauthorized" in str(e):
        print("Invalid or missing authentication token")
    else:
        raise
```

---

## Configuration

See `config_schema.yaml` for complete configuration reference.

### Environment Variables

```bash
# Authentication tokens
PLATFORM_TOKEN_GITHUB=ghp_...
PLATFORM_TOKEN_GITLAB=glpat-...
PLATFORM_TOKEN_BITBUCKET=...
PLATFORM_TOKEN_GITEA=...

# Webhook secrets
WEBHOOK_SECRET_GITHUB=...
WEBHOOK_SECRET_GITLAB=...
```

### Loading Custom Config

```python
pal = PlatformAbstractionLayer("/path/to/custom-config.yaml")
```

---

## Performance Tips

### Caching
- Detection is cached for 1 hour by default
- Clear cache: `detector.clear_cache()`

### Batch Operations
```python
# Efficient
prs = await driver.list_pull_requests("owner", "repo", limit=100)

# Less efficient
for i in range(1, 101):
    pr = await driver.get_pull_request("owner", "repo", i)
```

### Connection Reuse
```python
# Good: reuse driver instance
driver = await pal.get_driver(PlatformType.GITHUB)
for repo in repos:
    info = await driver.get_repository_info(owner, repo)
    
# Bad: new driver per operation
for repo in repos:
    driver = await pal.get_driver(PlatformType.GITHUB)
    info = await driver.get_repository_info(owner, repo)
```

---

## See Also

- [Architecture Documentation](architecture.md)
- [Deployment Guide](deployment_guide.md)
- [Configuration Reference](../config_schema.yaml)
