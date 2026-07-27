# Platform Abstraction Layer (PAL) - Architecture Documentation

## Overview

The Platform Abstraction Layer (PAL) is a unified interface for multi-platform git operations, supporting GitHub, GitLab, Bitbucket, and Gitea with a single API.

### Design Goals

- **Platform agnostic**: Single interface for all git platforms
- **High performance**: < 15ms platform detection latency
- **Robust**: Retry logic, fallback mechanisms, comprehensive error handling
- **Scalable**: Async/await throughout, horizontal scaling support
- **Observable**: Built-in metrics, health checks, and logging

## Architecture Layers

```
┌─────────────────────────────────────────┐
│       Application Layer                  │
│   (Consumer of PAL services)            │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│   Platform Abstraction Layer (PAL)       │
│   - Route detection                      │
│   - Driver instantiation                 │
│   - Health monitoring                    │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Driver Base   │  │ Driver Base   │  │ Driver Base   │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ - Async I/O   │  │ - Async I/O   │  │ - Async I/O   │
│ - Retry logic │  │ - Retry logic │  │ - Retry logic │
│ - Caching     │  │ - Caching     │  │ - Caching     │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ GitHub API   │  │ GitLab API   │  │ Bitbucket    │
│ v2022-11-28  │  │ v4           │  │ API v2.0     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
    github.com         gitlab.com         bitbucket.org
```

## Core Components

### 1. Platform Detector (`detection/platform_detector.py`)

Detects which platform a repository URL belongs to.

**Features:**
- Pattern-based detection with precompiled regexes
- ~1-5ms detection latency (well below 15ms target)
- LRU caching with 1-hour TTL
- Git CLI fallback for local repositories

**Supported patterns:**
- GitHub: `github.com`, `raw.githubusercontent.com`, `api.github.com`
- GitLab: `gitlab.com`, `gitlab-ci.com`, `gitlab.io`
- Bitbucket: `bitbucket.org`, `bitbucket.io`
- Gitea: `gitea.io`, `gitea.*`

### 2. Driver Base (`drivers/base.py`)

Abstract base class defining the driver interface.

**Key interfaces:**
- `get_repository_info(owner, repo)` → RepositoryInfo
- `list_pull_requests(owner, repo, state, limit)` → List[PullRequest]
- `get_pull_request(owner, repo, pr_number)` → PullRequest
- `create_pull_request(owner, repo, title, source, target, description, labels)` → PullRequest
- `list_commits(owner, repo, branch, limit)` → List[CommitInfo]
- `get_commit(owner, repo, sha)` → CommitInfo
- `list_workflow_runs(owner, repo, workflow_id, status, limit)` → List[WorkflowRun]
- `create_webhook(owner, repo, url, events, secret)` → Dict

**Capabilities enumeration:**
- PULL_REQUESTS / MERGE_REQUESTS
- ISSUES
- COMMITS
- WORKFLOWS / PIPELINES
- WEBHOOKS
- STATUSES / CHECKS
- DEPLOYMENTS
- ENVIRONMENTS
- DISCUSSIONS
- PACKAGES

### 3. Platform-Specific Drivers

#### GitHub Driver (`drivers/github_driver.py`)
- API v2022-11-28
- Uses GitHub REST API v3
- Supports check runs, statuses, deployments
- Implementation: 450+ LOC

#### GitLab Driver (`drivers/gitlab_driver.py`)
- API v4
- Uses GitLab REST API
- Supports pipelines, environments, packages
- Implementation: 420+ LOC

#### Bitbucket Driver (`drivers/bitbucket_driver.py`)
- API v2.0
- Uses Bitbucket Cloud REST API
- Supports pipelines, deployments
- Implementation: 380+ LOC

#### Gitea Driver (`drivers/gitea_driver.py`)
- API v1.0
- Uses Gitea REST API
- Supports actions (self-hosted)
- Implementation: 360+ LOC

### 4. Platform Abstraction Layer Service (`platform_abstraction_layer.py`)

Main orchestrator service.

**Responsibilities:**
- Load and validate configuration
- Initialize platform drivers based on config
- Route requests to appropriate drivers
- Provide unified health checks
- Maintain capability registry

## Data Models

### RepositoryInfo
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

### PullRequest
```python
@dataclass
class PullRequest:
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
```

### CommitInfo
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

### WorkflowRun
```python
@dataclass
class WorkflowRun:
    id: Union[int, str]
    name: str
    status: str  # pending, running, success, failure, cancelled
    conclusion: Optional[str]
    branch: str
    created_at: str
    updated_at: str
    duration_seconds: int
    artifacts: int = 0
```

## Retry and Error Handling Strategy

### Retry Logic
- **Max attempts**: 3 (configurable)
- **Backoff strategy**: Exponential (2s, 4s, 8s)
- **Retryable errors**: Network timeouts, transient API errors
- **Non-retryable**: 401 (auth), 404 (not found)

### Error Mapping
```
GitHub 401 → ValueError("Unauthorized: Invalid token")
GitHub 403 → ValueError("Forbidden: Rate limit exceeded")
GitHub 404 → ValueError("Resource not found")
```

### Fallback Mechanism
- Git CLI fallback for repository detection
- Timeout: 10 seconds per git command
- Max retries: 3

## Performance Characteristics

### Detection Latency
- Pattern matching: ~0.1ms per pattern (precompiled regex)
- Cache hit: <1ms
- Cache miss: <5ms
- Target: <15ms ✓

### API Call Latency
- GitHub (US): 100-300ms
- GitLab (EU): 150-400ms
- Bitbucket: 120-350ms
- Gitea (self-hosted): 50-200ms

### Memory Footprint
- Base PAL instance: ~5MB
- Per driver: ~2MB
- Cache (100 entries): ~100KB
- Total (4 drivers + cache): ~13MB

## Configuration Schema

See `config_schema.yaml` for full schema. Key sections:

```yaml
platform_abstraction_layer:
  detection:
    timeout_ms: 15000
    cache_ttl_seconds: 3600
  platforms:
    github:
      enabled: true
      api_version: "2022-11-28"
      base_urls:
        api: "https://api.github.com"
        web: "https://github.com"
  authentication:
    token_env_prefix: "PLATFORM_TOKEN"
  fallback:
    use_git_cli: true
```

## Integration Points

### Pillar A → Pillar D Integration
- PAL provides normalized repository metadata
- Drivers expose platform-specific capabilities
- Webhook creation for event routing
- Commit/PR data for policy evaluation

### Monitoring & Observability
- Health check endpoint: `/health`
- Metrics: request count, latency, error rates
- Structured logging with correlation IDs
- Platform-specific rate limit tracking

## Testing Strategy

### Unit Tests (70% coverage)
- Platform detector: `test_detection.py`
- Driver interfaces: `test_drivers.py`
- Data model validation

### Integration Tests (20% coverage)
- Multi-driver operations
- Config loading and validation
- Error handling paths

### E2E Tests (10% coverage)
- Full workflow simulation
- Docker/Kubernetes deployment
- Multi-platform detection

## Deployment Scenarios

### Development
```bash
docker-compose up pal-service
docker-compose run pal-test  # Run tests
```

### Production (Kubernetes)
```bash
kubectl apply -f deployment/kubernetes/
kubectl scale deployment pal-service --replicas=5
```

### Performance Tuning
- Increase driver timeout for slow networks
- Adjust retry backoff for high-latency APIs
- Enable request caching for repeated queries
- Use connection pooling for high-throughput scenarios

## Security Considerations

### Authentication
- Tokens stored in environment variables
- Never logged or exposed in error messages
- Optional webhook secret validation

### Network
- HTTPS/TLS verification enabled by default
- Custom CA bundle support for self-hosted platforms
- Rate limit respect to prevent DDoS

### Data
- No sensitive data cached
- Minimal request/response logging
- RBAC-compatible for Kubernetes

## Future Enhancements

### Phase 4.2
- Request caching layer (Redis support)
- Rate limit prediction and throttling
- Platform-specific batch operations

### Phase 4.3
- GraphQL driver abstraction
- Webhook event normalization
- Policy engine integration

### Phase 4.4
- Multi-account support
- Platform federation (GitOps)
- Advanced analytics dashboard
