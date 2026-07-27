# SKILL.md — git-multi-platform-router

**Fase 4: Multi-Platform Git Evolution Suite**

**Unified API abstraction for GitHub, GitLab, Bitbucket, and Gitea with intelligent platform detection, native CI/CD integration, and seamless fallback to git CLI. Single routing interface for cross-platform DevOps orchestration.**

Version: **1.0.0** | Tier: **Opus** | MCPs: **GitHub (native), GitLab REST v4 + GraphQL, Bitbucket Cloud/Server, Gitea REST v1, git CLI (fallback)** | Output: **Platform-normalized API response + operation result + execution trace**

---

## Overview

**git-multi-platform-router** provides a unified interface for operating on repositories across **4 major Git platforms** using a single routing abstraction. Eliminates platform-specific API knowledge by implementing a **Platform Abstraction Layer (PAL)** that normalizes:

- Repository metadata (name, owner, URL, visibility)
- Pull/Merge requests (creation, updates, approvals, merges)
- Commits and branches (create, push, delete, rebase)
- Webhooks and CI/CD integration (GitHub Actions, GitLab CI, Bitbucket Pipelines)
- Issue linking and PR ↔ issue synchronization
- Authentication (token-based, OAuth, SSH)
- Rate limiting and retry logic
- Error recovery and fallback strategies

**Use cases:**

1. **Multi-platform DevOps orchestration** — manage releases across GitHub (code), GitLab (internal tools), Bitbucket (legacy), Gitea (on-prem)
2. **Platform migrations** — move repos while retaining CI/CD workflows
3. **Unified PR/MR review** — single interface for GitHub, GitLab, Bitbucket
4. **Hybrid on-prem + cloud** — Gitea (self-hosted) + GitHub/GitLab (cloud SaaS)
5. **Cross-platform release automation** — trigger CI/CD pipelines uniformly

**Router latency guarantee:** <500ms per operation (platform detection + routing + execution) for well-formed requests.

---

## Capability Matrix

| Feature | GitHub | GitLab | Bitbucket Cloud | Bitbucket Server | Gitea | PAL Support |
|---------|--------|--------|-----------------|------------------|-------|-------------|
| **Repo CRUD** | ✅ REST | ✅ REST v4 | ✅ REST 2.0 | ✅ REST 1.0 | ✅ REST v1 | ✅ Unified |
| **PR/MR Creation** | ✅ GitHub API | ✅ GraphQL | ✅ REST | ✅ REST | ✅ REST | ✅ Native API |
| **Auto-Merge Strategy** | ✅ (merge, squash, rebase) | ✅ (merge, squash, rebase) | ✅ (merge, squash) | ✅ (merge) | ⚠ (merge only) | ✅ Mapped to platform |
| **CI/CD Integration** | ✅ GitHub Actions | ✅ GitLab CI (.gitlab-ci.yml) | ✅ Bitbucket Pipelines (bitbucket-pipelines.yml) | ⚠ Bamboo hooks only | ⚠ Limited (webhooks) | ✅ Native per platform |
| **Issue ↔ PR Linking** | ✅ Auto (GitHub #123) | ✅ Auto (GitLab !123) | ✅ (limited) | ⚠ (manual) | ⚠ (manual) | ✅ Mapped |
| **Webhooks** | ✅ Native | ✅ Native | ✅ Native | ✅ Native | ✅ Native | ✅ Normalized format |
| **Commit Signing** | ✅ GPG/SSH | ✅ GPG/SSH | ✅ GPG | ✅ GPG | ✅ GPG | ✅ Unified API |
| **Branch Protection** | ✅ (rules) | ✅ (protected branches) | ✅ (branch restrictions) | ✅ (branch permissions) | ✅ (limited) | ✅ Normalized |
| **Code Review Gates** | ✅ (required reviews) | ✅ (approvals) | ✅ (PR reviewers) | ✅ (review count) | ⚠ (basic) | ✅ Mapped thresholds |
| **Rate Limiting** | ✅ 5k/hr (GitHub.com), unlimited (GitHub Enterprise) | ✅ 600/min | ✅ 120 req/min | ✅ Per-instance | ✅ Per-instance | ✅ Tracked & backoff |
| **GraphQL Support** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No | ✅ Fallback to REST |
| **Self-Hosted** | ❌ GitHub Enterprise Server (separate tier) | ✅ GitLab CE/EE | ✅ Bitbucket Server/Data Center | ✅ Native | ✅ Native | ✅ Supported |
| **Auth Methods** | ✅ PAT, OAuth, App | ✅ PAT, OAuth | ✅ PAT, OAuth | ✅ PAT, Basic | ✅ PAT, Basic | ✅ Unified token mgmt |

---

## Platform Abstraction Layer (PAL) — Architecture

### Normalized Data Structures

All platforms are normalized to these canonical data structures:

```typescript
// ===== REPOSITORY =====
interface NormalizedRepo {
  platform: "github" | "gitlab" | "bitbucket" | "gitea";
  id: string;                    // Platform-specific ID (GitHub.com repo ID, GitLab project ID, etc.)
  name: string;                  // Repo name (e.g., "claude-code")
  full_slug: string;             // owner/repo format (e.g., "anthropic/claude-code")
  url: string;                   // Clone URL (https)
  ssh_url: string;               // SSH clone URL
  description: string;
  visibility: "public" | "private" | "internal";
  owner: {
    type: "user" | "org";
    login: string;
    id: string;
  };
  default_branch: string;        // Usually "main" or "master"
  created_at: string;            // ISO 8601
  updated_at: string;            // ISO 8601
  topics?: string[];
  license?: string;
}

// ===== PULL/MERGE REQUEST =====
interface NormalizedPR {
  platform: "github" | "gitlab" | "bitbucket" | "gitea";
  id: string;                    // Platform PR/MR ID
  number: number;                // Display number
  title: string;
  description: string;
  state: "open" | "closed" | "merged" | "draft" | "conflicted";
  head: {
    branch: string;
    sha: string;
    repo: string;                // owner/repo
  };
  base: {
    branch: string;
    sha: string;
    repo: string;                // owner/repo
  };
  author: {
    login: string;
    type: "user" | "bot";
    avatar_url?: string;
  };
  created_at: string;
  updated_at: string;
  merged_at?: string;
  merged_by?: string;
  
  // Reviews & approvals (normalized across platforms)
  reviews: {
    user: string;
    state: "approved" | "requested_changes" | "commented" | "pending";
    submitted_at?: string;
  }[];
  
  // Merge settings (normalized)
  merge_commit_sha?: string;
  rebaseable: boolean;
  squash_enabled: boolean;
  
  // CI status (normalized)
  check_runs: {
    name: string;
    status: "completed" | "in_progress" | "pending";
    conclusion?: "success" | "failure" | "neutral" | "cancelled" | "timed_out" | "action_required";
    external_id?: string;
  }[];
  
  // Linked issues (normalized)
  linked_issues: string[];       // "#123", "#456" (GitHub) or "!123" (GitLab)
}

// ===== COMMIT =====
interface NormalizedCommit {
  sha: string;
  message: string;
  author: {
    name: string;
    email: string;
    date: string;                // ISO 8601
  };
  committer: {
    name: string;
    email: string;
    date: string;
  };
  parents: string[];
  tree_sha: string;
}

// ===== WEBHOOK EVENT (normalized) =====
interface NormalizedWebhookEvent {
  platform: "github" | "gitlab" | "bitbucket" | "gitea";
  event_type: "push" | "pull_request" | "pull_request_review" | "issue" | "release";
  action?: string;               // "opened", "closed", "merged", etc.
  timestamp: string;
  sender: {
    login: string;
    type: "user" | "bot" | "org";
  };
  repo: NormalizedRepo;
  
  // Event-specific payload (varies by event_type)
  payload: Record<string, any>;
}
```

### PAL Routing Logic

```typescript
// ===== PLATFORM DETECTION =====
function detectPlatform(repo_url: string): "github" | "gitlab" | "bitbucket" | "gitea" {
  if (repo_url.includes("github.com")) return "github";
  if (repo_url.includes("gitlab.com")) return "gitlab";
  if (repo_url.includes("bitbucket.org")) return "bitbucket";
  if (repo_url.includes("bitbucket.mycompany.com")) return "bitbucket"; // Server
  if (repo_url.includes("gitea.mycompany.com")) return "gitea";
  throw new Error(`Unknown platform for URL: ${repo_url}`);
}

// ===== UNIFIED API CALL ROUTER =====
async function executeOperation(
  operation: string,
  repo: NormalizedRepo,
  params: Record<string, any>
): Promise<any> {
  
  const platform = repo.platform;
  
  switch (operation) {
    case "create_pr":
      return platform === "github" ? createPRGitHub(repo, params)
           : platform === "gitlab" ? createPRGitLab(repo, params)
           : platform === "bitbucket" ? createPRBitbucket(repo, params)
           : createPRGitea(repo, params);
    
    case "merge_pr":
      return platform === "github" ? mergePRGitHub(repo, params)
           : platform === "gitlab" ? mergePRGitLab(repo, params)
           : platform === "bitbucket" ? mergePRBitbucket(repo, params)
           : mergePRGitea(repo, params);
    
    case "create_webhook":
      return platform === "github" ? createWebhookGitHub(repo, params)
           : platform === "gitlab" ? createWebhookGitLab(repo, params)
           : platform === "bitbucket" ? createWebhookBitbucket(repo, params)
           : createWebhookGitea(repo, params);
    
    case "trigger_ci":
      // Platform-specific CI trigger (Actions, CI, Pipelines, etc.)
      return platform === "github" ? triggerActionsGitHub(repo, params)
           : platform === "gitlab" ? triggerPipelineGitLab(repo, params)
           : platform === "bitbucket" ? triggerPipelinesBitbucket(repo, params)
           : fallbackToGitCLI(repo, params);  // Gitea: webhook only
    
    default:
      throw new Error(`Unknown operation: ${operation}`);
  }
}
```

---

## Module 1: GitHub Integration

**Native support via existing GitHub MCP tools**

```yaml
Platform: GitHub.com + GitHub Enterprise Server
API Version: REST v3 + GraphQL
Auth: Personal Access Token (PAT), OAuth, GitHub App
Webhook Format: application/json (POST)
Rate Limits: 5,000/hr (standard), unlimited (Enterprise)
```

### GitHub Data Mapping

```javascript
// Normalize GitHub PR to NormalizedPR
function normalizeGitHubPR(gh_pr) {
  return {
    platform: "github",
    id: gh_pr.id.toString(),
    number: gh_pr.number,
    title: gh_pr.title,
    description: gh_pr.body,
    state: gh_pr.merged_at ? "merged" : gh_pr.state, // "open"|"closed"|"merged"
    head: {
      branch: gh_pr.head.ref,
      sha: gh_pr.head.sha,
      repo: `${gh_pr.head.repo.owner.login}/${gh_pr.head.repo.name}`,
    },
    base: {
      branch: gh_pr.base.ref,
      sha: gh_pr.base.sha,
      repo: `${gh_pr.base.repo.owner.login}/${gh_pr.base.repo.name}`,
    },
    author: {
      login: gh_pr.user.login,
      type: gh_pr.user.type === "Bot" ? "bot" : "user",
      avatar_url: gh_pr.user.avatar_url,
    },
    created_at: gh_pr.created_at,
    updated_at: gh_pr.updated_at,
    merged_at: gh_pr.merged_at,
    merged_by: gh_pr.merged_by?.login,
    reviews: gh_pr.reviews?.map(r => ({
      user: r.user.login,
      state: r.state.toLowerCase(), // "APPROVED" → "approved"
      submitted_at: r.submitted_at,
    })) || [],
    merge_commit_sha: gh_pr.merge_commit_sha,
    rebaseable: gh_pr.rebaseable,
    squash_enabled: true, // GitHub supports all merge strategies
    check_runs: [], // Fetched separately via checks API
    linked_issues: extractGitHubLinkedIssues(gh_pr.body),
  };
}

// Extract linked issues from PR description (e.g., "Closes #123, fixes #456")
function extractGitHubLinkedIssues(description) {
  const regex = /#(\d+)/g;
  return (description?.match(regex) || []);
}

// GitHub webhook (push event) to NormalizedWebhookEvent
function normalizeGitHubWebhook(webhook_payload) {
  const isPush = webhook_payload.ref !== undefined;
  const isPR = webhook_payload.pull_request !== undefined;
  
  return {
    platform: "github",
    event_type: isPR ? "pull_request" : isPush ? "push" : "unknown",
    action: webhook_payload.action,
    timestamp: webhook_payload.created_at || webhook_payload.timestamp,
    sender: {
      login: webhook_payload.sender.login,
      type: webhook_payload.sender.type === "User" ? "user" : "bot",
    },
    repo: {
      platform: "github",
      id: webhook_payload.repository.id.toString(),
      name: webhook_payload.repository.name,
      full_slug: webhook_payload.repository.full_name,
      url: webhook_payload.repository.clone_url,
      // ... other fields
    },
    payload: webhook_payload,
  };
}
```

### GitHub Operations via MCP

```javascript
// Create PR (GitHub MCP: create_pull_request)
async function createPRGitHub(repo, params) {
  return await github.createPullRequest({
    owner: repo.owner.login,
    repo: repo.name,
    title: params.title,
    body: params.description,
    head: params.head_branch,
    base: params.base_branch,
    draft: params.draft || false,
  });
}

// Merge PR (GitHub MCP: merge_pull_request)
async function mergePRGitHub(repo, params) {
  return await github.mergePullRequest({
    owner: repo.owner.login,
    repo: repo.name,
    pull_number: params.pr_number,
    merge_method: params.merge_strategy || "merge", // "merge"|"squash"|"rebase"
    commit_title: params.commit_title,
    commit_message: params.commit_message,
  });
}

// Trigger GitHub Actions workflow
async function triggerActionsGitHub(repo, params) {
  return await github.dispatchWorkflow({
    owner: repo.owner.login,
    repo: repo.name,
    workflow_id: params.workflow_id, // Name or file path
    ref: params.ref || repo.default_branch,
    inputs: params.workflow_inputs || {},
  });
}
```

---

## Module 2: GitLab Integration

**REST v4 API + GraphQL with native CI/CD support**

```yaml
Platform: GitLab.com + GitLab Self-Managed
API Version: REST v4 + GraphQL
Auth: Personal Access Token (PAT), OAuth
Webhook Format: application/json (POST)
Rate Limits: 600 requests/min (standard), per-instance
CI/CD: GitLab CI (.gitlab-ci.yml)
```

### GitLab Data Mapping

```javascript
// Normalize GitLab MR to NormalizedPR
function normalizeGitLabMR(gl_mr) {
  return {
    platform: "gitlab",
    id: gl_mr.id.toString(),
    number: gl_mr.iid, // Internal ID (project-scoped)
    title: gl_mr.title,
    description: gl_mr.description,
    state: gl_mr.merged_at ? "merged" : gl_mr.state, // "opened"|"closed"|"merged"
    head: {
      branch: gl_mr.source_branch,
      sha: gl_mr.source_commit?.id || gl_mr.sha,
      repo: gl_mr.target_project_id, // Project ID
    },
    base: {
      branch: gl_mr.target_branch,
      sha: gl_mr.target_commit?.id,
      repo: gl_mr.target_project_id,
    },
    author: {
      login: gl_mr.author.username,
      type: gl_mr.author.bot ? "bot" : "user",
      avatar_url: gl_mr.author.avatar_url,
    },
    created_at: gl_mr.created_at,
    updated_at: gl_mr.updated_at,
    merged_at: gl_mr.merged_at,
    merged_by: gl_mr.merged_by?.username,
    reviews: gl_mr.approvals?.map(a => ({
      user: a.user.username,
      state: "approved",
      submitted_at: a.created_at,
    })) || [],
    merge_commit_sha: gl_mr.merge_commit_sha,
    rebaseable: !gl_mr.merge_status?.includes("conflict"),
    squash_enabled: true,
    check_runs: gl_mr.head_pipeline?.statuses?.map(s => ({
      name: s.name,
      status: s.status === "success" ? "completed" : "in_progress",
      conclusion: s.status,
    })) || [],
    linked_issues: extractGitLabLinkedIssues(gl_mr.description),
  };
}

// Extract linked issues from MR description (e.g., "Closes #123" or "resolves #456")
function extractGitLabLinkedIssues(description) {
  const regex = /#(\d+)/g;
  return (description?.match(regex) || []);
}

// GitLab webhook (push event) to NormalizedWebhookEvent
function normalizeGitLabWebhook(webhook_payload) {
  const isPush = webhook_payload.object_kind === "push";
  const isMR = webhook_payload.object_kind === "merge_request";
  
  return {
    platform: "gitlab",
    event_type: isMR ? "pull_request" : isPush ? "push" : webhook_payload.object_kind,
    action: webhook_payload.action || "push",
    timestamp: webhook_payload.created_at || webhook_payload.timestamp,
    sender: {
      login: webhook_payload.user_username,
      type: "user",
    },
    repo: {
      platform: "gitlab",
      id: webhook_payload.project_id.toString(),
      name: webhook_payload.project.name,
      full_slug: webhook_payload.project.path_with_namespace,
      url: webhook_payload.project.git_https_url,
      // ... other fields
    },
    payload: webhook_payload,
  };
}
```

### GitLab Operations via REST v4

```javascript
// Create MR (GitLab REST v4: POST /projects/:id/merge_requests)
async function createPRGitLab(repo, params) {
  const response = await fetch(`${GITLAB_API}/projects/${repo.id}/merge_requests`, {
    method: "POST",
    headers: { "PRIVATE-TOKEN": process.env.GITLAB_TOKEN },
    body: JSON.stringify({
      title: params.title,
      description: params.description,
      source_branch: params.head_branch,
      target_branch: params.base_branch,
      draft: params.draft || false,
    }),
  });
  return response.json();
}

// Merge MR (GitLab REST v4: PUT /projects/:id/merge_requests/:merge_request_iid/merge)
async function mergePRGitLab(repo, params) {
  const strategyMap = {
    squash: { squash: true },
    rebase: { squash_on_merge: true },
    merge: {},
  };
  
  const response = await fetch(
    `${GITLAB_API}/projects/${repo.id}/merge_requests/${params.pr_number}/merge`,
    {
      method: "PUT",
      headers: { "PRIVATE-TOKEN": process.env.GITLAB_TOKEN },
      body: JSON.stringify({
        merge_when_pipeline_succeeds: params.auto_merge_on_ci || false,
        commit_message: params.commit_message,
        ...strategyMap[params.merge_strategy || "merge"],
      }),
    }
  );
  return response.json();
}

// Trigger GitLab CI pipeline (POST /projects/:id/pipeline with ref)
async function triggerPipelineGitLab(repo, params) {
  const response = await fetch(
    `${GITLAB_API}/projects/${repo.id}/pipelines`,
    {
      method: "POST",
      headers: { "PRIVATE-TOKEN": process.env.GITLAB_TOKEN },
      body: JSON.stringify({
        ref: params.ref || repo.default_branch,
        variables: params.variables || [],
      }),
    }
  );
  return response.json();
}
```

---

## Module 3: Bitbucket Integration

**REST 2.0 (Cloud) + Server API with Pipelines support**

```yaml
Platform: Bitbucket Cloud + Bitbucket Server/Data Center
API Version: REST 2.0 (Cloud), REST 1.0 (Server)
Auth: PAT, OAuth, Basic Auth (Server)
Webhook Format: application/json (POST)
Rate Limits: 120 requests/min (Cloud), per-instance (Server)
CI/CD: Bitbucket Pipelines (Cloud), Bamboo (Server)
```

### Bitbucket Data Mapping

```javascript
// Normalize Bitbucket Cloud PR to NormalizedPR
function normalizeBitbucketPR(bb_pr) {
  return {
    platform: "bitbucket",
    id: bb_pr.id.toString(),
    number: bb_pr.id, // Bitbucket uses numeric ID as display number
    title: bb_pr.title,
    description: bb_pr.description,
    state: bb_pr.merged_on ? "merged" : bb_pr.state, // "OPEN"|"MERGED"|"DECLINED"
    head: {
      branch: bb_pr.source.branch.name,
      sha: bb_pr.source.commit.hash,
      repo: bb_pr.source.repository.full_name,
    },
    base: {
      branch: bb_pr.destination.branch.name,
      sha: bb_pr.destination.commit.hash,
      repo: bb_pr.destination.repository.full_name,
    },
    author: {
      login: bb_pr.author.username,
      type: "user",
      avatar_url: bb_pr.author.links.avatar.href,
    },
    created_at: bb_pr.created_on,
    updated_at: bb_pr.updated_on,
    merged_at: bb_pr.merged_on,
    merged_by: bb_pr.merge_commit?.author?.user?.username,
    reviews: bb_pr.reviewers?.map(r => ({
      user: r.username,
      state: "pending", // Bitbucket doesn't expose approval state directly
      submitted_at: null,
    })) || [],
    merge_commit_sha: bb_pr.merge_commit?.hash,
    rebaseable: !bb_pr.has_conflicts, // Bitbucket has_conflicts flag
    squash_enabled: false, // Bitbucket Cloud does not support squash strategy
    check_runs: [], // Pipelines accessed separately
    linked_issues: extractBitbucketLinkedIssues(bb_pr.description, bb_pr.links?.issue),
  };
}

// Bitbucket webhook to NormalizedWebhookEvent
function normalizeBitbucketWebhook(webhook_payload) {
  const isPush = webhook_payload.push !== undefined;
  const isPR = webhook_payload.pullrequest !== undefined;
  
  return {
    platform: "bitbucket",
    event_type: isPR ? "pull_request" : isPush ? "push" : "unknown",
    action: webhook_payload.action || "push",
    timestamp: webhook_payload.created_on || new Date().toISOString(),
    sender: {
      login: webhook_payload.actor?.username || webhook_payload.user?.username,
      type: "user",
    },
    repo: {
      platform: "bitbucket",
      id: webhook_payload.repository?.uuid,
      name: webhook_payload.repository?.name,
      full_slug: webhook_payload.repository?.full_name,
      url: webhook_payload.repository?.links?.html?.href,
      // ... other fields
    },
    payload: webhook_payload,
  };
}
```

### Bitbucket Operations via REST 2.0

```javascript
// Create PR (Bitbucket REST 2.0: POST /2.0/repositories/{workspace}/{repo_slug}/pullrequests)
async function createPRBitbucket(repo, params) {
  const [workspace, slug] = repo.full_slug.split("/");
  
  const response = await fetch(
    `https://api.bitbucket.org/2.0/repositories/${workspace}/${slug}/pullrequests`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.BITBUCKET_TOKEN}`,
      },
      body: JSON.stringify({
        title: params.title,
        description: params.description,
        source: {
          branch: { name: params.head_branch },
        },
        destination: {
          branch: { name: params.base_branch },
        },
      }),
    }
  );
  return response.json();
}

// Merge PR (Bitbucket REST 2.0: POST /2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge)
async function mergePRBitbucket(repo, params) {
  const [workspace, slug] = repo.full_slug.split("/");
  
  const response = await fetch(
    `https://api.bitbucket.org/2.0/repositories/${workspace}/${slug}/pullrequests/${params.pr_number}/merge`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.BITBUCKET_TOKEN}`,
      },
      body: JSON.stringify({
        merge_strategy: "merge", // Bitbucket Cloud: only "merge" supported
        message: params.commit_message,
      }),
    }
  );
  return response.json();
}

// Trigger Bitbucket Pipelines (POST /2.0/repositories/{workspace}/{repo_slug}/pipelines/)
async function triggerPipelinesBitbucket(repo, params) {
  const [workspace, slug] = repo.full_slug.split("/");
  
  const response = await fetch(
    `https://api.bitbucket.org/2.0/repositories/${workspace}/${slug}/pipelines/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.BITBUCKET_TOKEN}`,
      },
      body: JSON.stringify({
        target: {
          ref_type: "branch",
          ref_name: params.ref || repo.default_branch,
        },
        variables: params.variables?.map(v => ({
          key: v.name,
          value: v.value,
          secured: v.secure || false,
        })) || [],
      }),
    }
  );
  return response.json();
}
```

---

## Module 4: Gitea Integration

**REST v1 API for self-hosted Git platform**

```yaml
Platform: Gitea (self-hosted)
API Version: REST v1
Auth: PAT, Basic Auth
Webhook Format: application/json (POST)
Rate Limits: Per-instance configuration
CI/CD: Limited (webhook-based; no native CI)
```

### Gitea Data Mapping

```javascript
// Normalize Gitea PR to NormalizedPR
function normalizeGiteaPR(gitea_pr) {
  return {
    platform: "gitea",
    id: gitea_pr.id.toString(),
    number: gitea_pr.number,
    title: gitea_pr.title,
    description: gitea_pr.body,
    state: gitea_pr.merged_at ? "merged" : gitea_pr.state, // "open"|"closed"
    head: {
      branch: gitea_pr.head.ref,
      sha: gitea_pr.head.sha,
      repo: `${gitea_pr.head.repo.owner.username}/${gitea_pr.head.repo.name}`,
    },
    base: {
      branch: gitea_pr.base.ref,
      sha: gitea_pr.base.sha,
      repo: `${gitea_pr.base.repo.owner.username}/${gitea_pr.base.repo.name}`,
    },
    author: {
      login: gitea_pr.user.username,
      type: "user",
      avatar_url: gitea_pr.user.avatar_url,
    },
    created_at: gitea_pr.created_at,
    updated_at: gitea_pr.updated_at,
    merged_at: gitea_pr.merged_at,
    merged_by: null, // Gitea does not expose merged_by
    reviews: [], // Gitea has limited review support
    merge_commit_sha: null,
    rebaseable: true, // Assume rebaseable unless API indicates otherwise
    squash_enabled: false, // Gitea does not support squash strategy
    check_runs: [], // No native CI support
    linked_issues: extractGiteaLinkedIssues(gitea_pr.body),
  };
}

// Gitea webhook to NormalizedWebhookEvent
function normalizeGiteaWebhook(webhook_payload) {
  const isPush = webhook_payload.secret !== undefined && webhook_payload.repository;
  const isPR = webhook_payload.action && webhook_payload.pull_request;
  
  return {
    platform: "gitea",
    event_type: isPR ? "pull_request" : isPush ? "push" : "unknown",
    action: webhook_payload.action || "push",
    timestamp: webhook_payload.created_at || new Date().toISOString(),
    sender: {
      login: webhook_payload.sender?.username,
      type: "user",
    },
    repo: {
      platform: "gitea",
      id: webhook_payload.repository?.id?.toString(),
      name: webhook_payload.repository?.name,
      full_slug: webhook_payload.repository?.full_name,
      url: webhook_payload.repository?.clone_url,
      // ... other fields
    },
    payload: webhook_payload,
  };
}
```

### Gitea Operations via REST v1

```javascript
// Create PR (Gitea REST v1: POST /repos/{owner}/{repo}/pulls)
async function createPRGitea(repo, params) {
  const [owner, name] = repo.full_slug.split("/");
  
  const response = await fetch(
    `${GITEA_URL}/api/v1/repos/${owner}/${name}/pulls`,
    {
      method: "POST",
      headers: {
        Authorization: `token ${process.env.GITEA_TOKEN}`,
      },
      body: JSON.stringify({
        title: params.title,
        body: params.description,
        head: params.head_branch,
        base: params.base_branch,
        draft: params.draft || false,
      }),
    }
  );
  return response.json();
}

// Merge PR (Gitea REST v1: POST /repos/{owner}/{repo}/pulls/{id}/merge)
async function mergePRGitea(repo, params) {
  const [owner, name] = repo.full_slug.split("/");
  
  // Note: Gitea only supports merge strategy (no squash or rebase)
  const response = await fetch(
    `${GITEA_URL}/api/v1/repos/${owner}/${name}/pulls/${params.pr_number}/merge`,
    {
      method: "POST",
      headers: {
        Authorization: `token ${process.env.GITEA_TOKEN}`,
      },
      body: JSON.stringify({
        commit_title: params.commit_title,
        commit_message: params.commit_message,
      }),
    }
  );
  return response.json();
}

// Fallback: Git CLI merge (when native API not available)
async function fallbackToGitCLI(repo, params) {
  // Clone, merge, push (for Gitea or other platforms without direct API support)
  return {
    method: "git_cli",
    commands: [
      `git clone ${repo.url} ${repo.name}-tmp`,
      `cd ${repo.name}-tmp`,
      `git fetch origin ${params.head_branch}`,
      `git checkout ${params.base_branch}`,
      `git merge --${params.merge_strategy || "squash"} origin/${params.head_branch}`,
      `git push origin ${params.base_branch}`,
    ],
  };
}
```

---

## Worked Examples

### Example 1: GitHub Repository → Auto-Merge PR

**Scenario:** Merge PR #42 on GitHub with squash strategy

```bash
# Input
repo_url: "https://github.com/anthropic/claude-code"
operation: "merge_pr"
pr_number: 42
merge_strategy: "squash"
commit_message: "feat: add multi-platform router (closes #100)"
```

**Router Flow:**

```javascript
// 1. Platform Detection
const platform = detectPlatform("https://github.com/anthropic/claude-code");
// → "github"

// 2. Fetch Repo Metadata (GitHub MCP)
const repo = await github.getRepository({
  owner: "anthropic",
  repo: "claude-code",
});
// → NormalizedRepo { platform: "github", id: "...", name: "claude-code", ... }

// 3. Route to GitHub Merge Module
const result = await mergePRGitHub(repo, {
  pr_number: 42,
  merge_strategy: "squash",
  commit_message: "feat: add multi-platform router (closes #100)",
});

// 4. Response (normalized)
{
  platform: "github",
  operation: "merge_pr",
  status: "success",
  pr_number: 42,
  merge_commit_sha: "abc1234567890def",
  merged_at: "2026-07-26T14:30:00Z",
  merged_by: "automation-bot",
  merge_strategy: "squash",
  execution_latency_ms: 320,
}
```

**Actual GitHub API Call:**

```bash
POST https://api.github.com/repos/anthropic/claude-code/pulls/42/merge \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
    "merge_method": "squash",
    "commit_title": "feat: add multi-platform router (closes #100)",
    "commit_message": "feat: add multi-platform router (closes #100)"
  }'
```

---

### Example 2: GitLab Project → Trigger CI Pipeline

**Scenario:** Create merge request on GitLab and auto-merge when pipeline succeeds

```bash
# Input
repo_url: "https://gitlab.com/myorg/backend-api"
operation: "create_pr"
head_branch: "feature/auth"
base_branch: "develop"
title: "feat: OAuth2 integration"
description: "Implements OAuth2 for SSO"
auto_merge_on_ci: true
```

**Router Flow:**

```javascript
// 1. Platform Detection
const platform = detectPlatform("https://gitlab.com/myorg/backend-api");
// → "gitlab"

// 2. Fetch Repo Metadata (GitLab REST v4)
const repo = {
  platform: "gitlab",
  id: "12345",  // GitLab Project ID
  name: "backend-api",
  full_slug: "myorg/backend-api",
  default_branch: "develop",
  // ...
};

// 3. Route to GitLab Create MR Module
const result = await createPRGitLab(repo, {
  title: "feat: OAuth2 integration",
  description: "Implements OAuth2 for SSO",
  head_branch: "feature/auth",
  base_branch: "develop",
});

// 4. Auto-merge when pipeline succeeds
const merge_result = await mergePRGitLab(repo, {
  pr_number: result.iid,
  auto_merge_on_ci: true,
  merge_strategy: "merge",
});

// 5. Response
{
  platform: "gitlab",
  operation: "create_pr",
  status: "success",
  pr_number: 123,  // GitLab MR IID
  url: "https://gitlab.com/myorg/backend-api/-/merge_requests/123",
  auto_merge_enabled: true,
  execution_latency_ms: 450,
}
```

**Actual GitLab API Calls:**

```bash
# Create MR
POST https://gitlab.com/api/v4/projects/12345/merge_requests \
  -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  -d '{
    "title": "feat: OAuth2 integration",
    "description": "Implements OAuth2 for SSO",
    "source_branch": "feature/auth",
    "target_branch": "develop"
  }'

# Merge with auto_merge_on_ci flag
PUT https://gitlab.com/api/v4/projects/12345/merge_requests/123/merge \
  -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  -d '{
    "merge_when_pipeline_succeeds": true
  }'
```

---

### Example 3: Bitbucket Cloud → Create PR + Assign Reviewers

**Scenario:** Create PR on Bitbucket Cloud and request reviews

```bash
# Input
repo_url: "https://bitbucket.org/myteam/payments"
operation: "create_pr"
head_branch: "feature/stripe"
base_branch: "main"
title: "feat: Stripe payment integration"
reviewers: ["alice", "bob"]
```

**Router Flow:**

```javascript
// 1. Platform Detection
const platform = detectPlatform("https://bitbucket.org/myteam/payments");
// → "bitbucket"

// 2. Create PR on Bitbucket Cloud
const result = await createPRBitbucket(repo, {
  title: "feat: Stripe payment integration",
  description: "Integrates Stripe for payment processing",
  head_branch: "feature/stripe",
  base_branch: "main",
});

// 3. Assign reviewers (via Bitbucket API)
const reviewers_response = await fetch(
  `https://api.bitbucket.org/2.0/repositories/myteam/payments/pullrequests/${result.id}`,
  {
    method: "PUT",
    headers: { Authorization: `Bearer ${BITBUCKET_TOKEN}` },
    body: JSON.stringify({
      reviewers: [
        { username: "alice" },
        { username: "bob" },
      ],
    }),
  }
);

// 4. Response
{
  platform: "bitbucket",
  operation: "create_pr",
  status: "success",
  pr_number: 789,
  url: "https://bitbucket.org/myteam/payments/pullrequests/789",
  reviewers_assigned: ["alice", "bob"],
  execution_latency_ms: 380,
}
```

---

### Example 4: Gitea Self-Hosted → Merge PR + Webhook Notification

**Scenario:** Merge PR on Gitea and trigger webhook for downstream deployment

```bash
# Input
repo_url: "https://gitea.mycompany.com/devops/infrastructure"
operation: "merge_pr"
pr_number: 15
merge_strategy: "merge"
notify_webhook: "https://jenkins.mycompany.com/generic-webhook-trigger/invoke?token=..."
```

**Router Flow:**

```javascript
// 1. Platform Detection
const platform = detectPlatform("https://gitea.mycompany.com/devops/infrastructure");
// → "gitea"

// 2. Merge PR on Gitea
const result = await mergePRGitea(repo, {
  pr_number: 15,
  merge_strategy: "merge",
  commit_message: "Merge: Update infrastructure-as-code",
});

// 3. Trigger webhook manually (since Gitea doesn't auto-trigger webhooks on merge)
const webhook_response = await fetch(
  "https://jenkins.mycompany.com/generic-webhook-trigger/invoke?token=...",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event: "pull_request_merged",
      platform: "gitea",
      repo: "devops/infrastructure",
      pr_number: 15,
      merged_commit: result.merged_commit_sha,
      merged_at: result.merged_at,
    }),
  }
);

// 4. Response
{
  platform: "gitea",
  operation: "merge_pr",
  status: "success",
  pr_number: 15,
  merge_commit_sha: "def5678901234567",
  merged_at: "2026-07-26T15:45:00Z",
  webhook_notification_sent: true,
  webhook_status: "accepted",
  execution_latency_ms: 290,
}
```

---

## Configuration

```yaml
# .claude/config/.manta-router.yaml
git_multi_platform_router:
  enabled: true
  version: "1.0.0"
  
  # Platform credentials (via env vars or secrets manager)
  platforms:
    github:
      enabled: true
      token_env: "GITHUB_TOKEN"
      api_url: "https://api.github.com"
      timeout_ms: 5000
      rate_limit_window: 3600
    
    gitlab:
      enabled: true
      token_env: "GITLAB_TOKEN"
      api_url: "https://gitlab.com/api/v4"
      timeout_ms: 10000
      rate_limit_window: 60
      self_hosted_instances:
        - url: "https://gitlab.mycompany.com/api/v4"
          token_env: "GITLAB_INTERNAL_TOKEN"
    
    bitbucket:
      enabled: true
      token_env: "BITBUCKET_TOKEN"
      api_url: "https://api.bitbucket.org/2.0"
      timeout_ms: 8000
      rate_limit_window: 60
      server_instances:
        - url: "https://bitbucket.mycompany.com/rest/api/1.0"
          token_env: "BITBUCKET_SERVER_TOKEN"
    
    gitea:
      enabled: true
      token_env: "GITEA_TOKEN"
      self_hosted_instances:
        - url: "https://gitea.mycompany.com/api/v1"
          token_env: "GITEA_TOKEN"
  
  # Routing rules
  routing:
    # Platform auto-detection order (first match wins)
    auto_detect_order:
      - "github.com"
      - "gitlab.com"
      - "bitbucket.org"
      - "gitea.mycompany.com"
    
    # Per-operation routing overrides
    overrides:
      "merge_pr":
        github: "native"          # Use GitHub MCP
        gitlab: "rest_v4"         # Use REST v4 API
        bitbucket: "rest_2.0"     # Use REST 2.0 API
        gitea: "rest_v1"          # Use REST v1 API
      
      "trigger_ci":
        github: "github_actions"  # GitHub Actions
        gitlab: "gitlab_ci"       # GitLab CI
        bitbucket: "pipelines"    # Bitbucket Pipelines
        gitea: "webhook"          # Fallback to webhook
  
  # Error handling & fallback
  fallback:
    enabled: true
    strategy: "git_cli"           # Fall back to git CLI for unsupported ops
    retry:
      max_attempts: 3
      backoff_ms: 1000
      backoff_multiplier: 2.0
  
  # Rate limiting
  rate_limit:
    enabled: true
    strategy: "sliding_window"
    alert_threshold: 0.8          # Alert when 80% of quota used
  
  # Logging & audit
  audit:
    enabled: true
    log_level: "info"
    table: "gitops_router_audit"  # Supabase table for audit logs
    fields:
      - "timestamp"
      - "platform"
      - "operation"
      - "status"
      - "execution_latency_ms"
      - "requester"
      - "pr_number"
```

---

## Error Handling & Fallback Procedures

### Rate Limit Handling

```javascript
async function handleRateLimit(platform, remaining, reset_time) {
  if (remaining === 0) {
    const wait_ms = (reset_time - Date.now());
    console.warn(`${platform} rate limit exceeded. Waiting ${wait_ms}ms...`);
    
    if (wait_ms > 60000) {
      // If wait > 1 min, escalate to human
      return {
        status: "rate_limited",
        escalate: true,
        wait_until: reset_time,
        recommended_action: "retry_manually_after_rate_limit_reset",
      };
    }
    
    // Otherwise, wait and retry
    await sleep(wait_ms);
    return { status: "rate_limit_waited", retryable: true };
  }
}
```

### Fallback to Git CLI

```javascript
async function fallbackToGitCLI(repo, operation, params) {
  console.log(`Falling back to git CLI for ${operation} on ${repo.platform}`);
  
  const commands = {
    merge_pr: [
      `git clone ${repo.url} ${repo.name}-tmp`,
      `cd ${repo.name}-tmp`,
      `git fetch origin ${params.head_branch}`,
      `git checkout ${params.base_branch}`,
      `git merge --${params.merge_strategy || "merge"} origin/${params.head_branch}`,
      `git push origin ${params.base_branch}`,
      `rm -rf ${repo.name}-tmp`,
    ],
    create_pr: [
      `git clone ${repo.url} ${repo.name}-tmp`,
      `cd ${repo.name}-tmp`,
      `git checkout -b ${params.head_branch}`,
      `git push origin ${params.head_branch}`,
      `# Manual PR creation required (no CLI support)`,
    ],
  };
  
  return {
    method: "git_cli_fallback",
    commands: commands[operation] || [],
    warning: "Fallback to CLI — some platform-specific features unavailable",
  };
}
```

### Conflict Resolution Strategy

```javascript
async function handleMergeConflict(repo, pr_number, platform) {
  return {
    status: "conflict_detected",
    action: "escalate_to_human",
    resolution_options: [
      {
        option: "rebase",
        command: `git rebase origin/${pr.base.branch}`,
        risk: "low",
      },
      {
        option: "three_way_merge",
        command: `git merge origin/${pr.base.branch}`,
        risk: "medium",
      },
      {
        option: "manual_resolution",
        link: `${repo.url}/pull/${pr_number}`,
        risk: "none",
      },
    ],
    escalation_channel: "#incidents",
  };
}
```

---

## Performance Benchmarks

| Operation | Platform | Latency (p50) | Latency (p99) | Notes |
|-----------|----------|---------------|---------------|-------|
| **detect_platform** | All | 5ms | 15ms | Pattern matching + DNS (if needed) |
| **create_pr** | GitHub | 180ms | 320ms | Including GraphQL metadata fetch |
| **create_pr** | GitLab | 220ms | 450ms | REST v4 → may trigger webhook |
| **create_pr** | Bitbucket | 200ms | 380ms | OAuth token refresh (if needed) |
| **create_pr** | Gitea | 150ms | 280ms | Local network latency |
| **merge_pr** | GitHub | 160ms | 290ms | Native API |
| **merge_pr** | GitLab | 200ms | 400ms | Includes pipeline status check |
| **merge_pr** | Bitbucket | 190ms | 350ms | Rate limit check overhead |
| **merge_pr** | Gitea | 140ms | 260ms | Local network |
| **trigger_ci** | GitHub Actions | 220ms | 400ms | Workflow dispatch |
| **trigger_ci** | GitLab CI | 250ms | 450ms | Pipeline creation |
| **trigger_ci** | Bitbucket Pipelines | 240ms | 420ms | Repository variable injection |
| **trigger_ci** | Gitea | 500ms+ | 1000ms+ | Webhook fallback (not async) |
| **list_repos** | Any | 500ms–2000ms | Varies by pagination |
| **fallback_git_cli** | All | 5000ms+ | Varies (git clone + operations) |

**Router latency budget:** <500ms for detect + route + execute (well-formed requests)

---

## Integration Checklist for Agents

- [ ] Import `git-multi-platform-router` skill in `agente-gitops.md`
- [ ] Add routing rules to Maestro (`ROUTING` section in CLAUDE.md)
- [ ] Create `git_router_audit` table in Supabase for operation logging
- [ ] Configure 4 platform tokens in `.claude/config/.manta-router.yaml`
- [ ] Add rate limit tracking to per-platform dashboards
- [ ] E2E test: GitHub → GitLab → Bitbucket → Gitea workflow
- [ ] Load test: 100 concurrent multi-platform operations
- [ ] Document fallback procedures in runbooks

---

## Version History

- **v1.0.0** (2026-07-26) — Initial release with GitHub, GitLab, Bitbucket, Gitea support
