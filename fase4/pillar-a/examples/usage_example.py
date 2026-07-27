#!/usr/bin/env python3
"""Usage examples for Platform Abstraction Layer."""

import asyncio
import os
from platform_abstraction_layer import get_pal, PlatformAbstractionLayer
from drivers.base import PlatformType


async def example_1_basic_usage():
    """Example 1: Basic usage with automatic platform detection."""
    print("\n=== Example 1: Basic Usage ===")

    # Initialize PAL
    pal = get_pal()

    # Detect platform from URL
    url = "https://github.com/torvalds/linux"
    driver, detection_time = await pal.detect_and_get_driver(url)

    print(f"Detected platform: {driver.platform_type.value}")
    print(f"Detection time: {detection_time:.2f}ms")

    # Get repository info
    repo = await driver.get_repository_info("torvalds", "linux")
    print(f"\nRepository: {repo.owner}/{repo.name}")
    print(f"  Private: {repo.is_private}")
    print(f"  Default branch: {repo.default_branch}")
    print(f"  Has issues: {repo.has_issues}")

    await pal.close_all()


async def example_2_multi_platform():
    """Example 2: Working with multiple platforms."""
    print("\n=== Example 2: Multi-Platform Operations ===")

    pal = get_pal()

    repositories = [
        ("https://github.com/octocat/Hello-World", "octocat", "Hello-World"),
        ("https://gitlab.com/gitlab-examples/hello-world", "gitlab-examples", "hello-world"),
    ]

    for url, owner, repo in repositories:
        try:
            driver, latency = await pal.detect_and_get_driver(url)
            repo_info = await driver.get_repository_info(owner, repo)

            print(f"\n{repo_info.platform.value.upper()}: {repo_info.url}")
            print(f"  Detection: {latency:.2f}ms")
            print(f"  Default branch: {repo_info.default_branch}")

        except ValueError as e:
            print(f"\nError with {url}: {e}")

    await pal.close_all()


async def example_3_pull_requests():
    """Example 3: Working with pull requests."""
    print("\n=== Example 3: Pull Requests ===")

    pal = get_pal()
    driver = await pal.get_driver(PlatformType.GITHUB)

    # List open pull requests
    print("Fetching open PRs for octocat/Hello-World...")
    prs = await driver.list_pull_requests(
        "octocat", "Hello-World",
        state="open",
        limit=10
    )

    print(f"\nFound {len(prs)} open pull requests:")
    for pr in prs:
        print(f"  #{pr.number}: {pr.title}")
        print(f"    Author: {pr.author}")
        print(f"    State: {pr.state}")
        if pr.merged_at:
            print(f"    Merged: {pr.merged_at}")

    # Get specific pull request
    if prs:
        pr = prs[0]
        detailed_pr = await driver.get_pull_request("octocat", "Hello-World", pr.number)
        print(f"\nDetailed view of PR #{detailed_pr.number}:")
        print(f"  Title: {detailed_pr.title}")
        print(f"  Description: {detailed_pr.description[:100]}...")
        print(f"  Reviews: {detailed_pr.review_count}")

    await pal.close_all()


async def example_4_commits():
    """Example 4: Working with commits."""
    print("\n=== Example 4: Commits ===")

    pal = get_pal()
    driver = await pal.get_driver(PlatformType.GITHUB)

    # List recent commits
    print("Fetching recent commits from main branch...")
    commits = await driver.list_commits(
        "octocat", "Hello-World",
        branch="main",
        limit=5
    )

    print(f"\nFound {len(commits)} commits:")
    for commit in commits:
        print(f"\n  {commit.sha[:8]}: {commit.message.split(chr(10))[0]}")
        print(f"    Author: {commit.author} <{commit.author_email}>")
        print(f"    Date: {commit.committed_at}")
        print(f"    Parents: {', '.join([p[:8] for p in commit.parent_shas])}")

    # Get specific commit
    if commits:
        commit = commits[0]
        detailed = await driver.get_commit("octocat", "Hello-World", commit.sha)
        print(f"\nDetailed commit {detailed.sha[:8]}:")
        print(f"  Message:\n{detailed.message}")

    await pal.close_all()


async def example_5_workflows():
    """Example 5: Working with workflows/pipelines."""
    print("\n=== Example 5: Workflows/Pipelines ===")

    pal = get_pal()
    driver = await pal.get_driver(PlatformType.GITHUB)

    # List workflow runs
    print("Fetching workflow runs...")
    runs = await driver.list_workflow_runs(
        "octocat", "Hello-World",
        status="success",
        limit=5
    )

    print(f"\nFound {len(runs)} workflow runs:")
    for run in runs:
        print(f"\n  {run.name} (#{run.id})")
        print(f"    Status: {run.status}")
        if run.conclusion:
            print(f"    Conclusion: {run.conclusion}")
        print(f"    Branch: {run.branch}")
        print(f"    Duration: {run.duration_seconds}s")
        print(f"    Created: {run.created_at}")

    await pal.close_all()


async def example_6_capabilities():
    """Example 6: Checking platform capabilities."""
    print("\n=== Example 6: Platform Capabilities ===")

    pal = get_pal()

    # List capabilities for all platforms
    capabilities = await pal.list_capabilities()

    print("\nAvailable capabilities by platform:")
    for platform, caps in capabilities.items():
        print(f"\n{platform.upper()}:")
        for cap in sorted(caps):
            print(f"  ✓ {cap}")

    # Check health
    health = await pal.health_check()
    print(f"\nOverall health: {health['overall_status']}")

    for platform, status in health['platforms'].items():
        health_symbol = "✓" if status['status'] == "healthy" else "✗"
        print(f"  {health_symbol} {platform}: {status['status']}")

    await pal.close_all()


async def example_7_error_handling():
    """Example 7: Error handling and fallbacks."""
    print("\n=== Example 7: Error Handling ===")

    pal = get_pal()

    # Try to detect invalid URL
    print("Attempting to detect invalid platform...")
    try:
        driver, _ = await pal.detect_and_get_driver("https://unknown-platform.com/repo")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")

    # Try to access non-existent repository
    print("\nAttempting to access non-existent repository...")
    driver = await pal.get_driver(PlatformType.GITHUB)
    try:
        # Note: requires valid GitHub token for some platforms
        repo = await driver.get_repository_info("this-user-probably", "does-not-exist-xyz")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")

    await pal.close_all()


async def example_8_custom_config():
    """Example 8: Using custom configuration."""
    print("\n=== Example 8: Custom Configuration ===")

    # You can pass custom config path
    config_path = os.path.join(os.path.dirname(__file__), "../config_schema.yaml")

    pal = PlatformAbstractionLayer(config_path)

    print("PAL initialized with custom configuration")
    print(f"Loaded {len(pal.drivers)} platform drivers")

    for platform, driver in pal.drivers.items():
        print(f"  - {platform.value}")

    await pal.close_all()


async def example_9_batch_operations():
    """Example 9: Batch operations efficiently."""
    print("\n=== Example 9: Batch Operations ===")

    pal = get_pal()
    driver = await pal.get_driver(PlatformType.GITHUB)

    repositories = [
        ("octocat", "Hello-World"),
        ("torvalds", "linux"),
        ("django", "django"),
    ]

    print("Fetching repository info for multiple repos...")

    # Create multiple concurrent requests
    tasks = [
        driver.get_repository_info(owner, repo)
        for owner, repo in repositories
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    print(f"\nFetched {len([r for r in results if not isinstance(r, Exception)])} repos:")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  ✗ {repositories[i][0]}/{repositories[i][1]}: {result}")
        else:
            print(f"  ✓ {result.owner}/{result.name} ({result.default_branch})")

    await pal.close_all()


async def example_10_creating_pr():
    """Example 10: Creating a pull request (requires auth)."""
    print("\n=== Example 10: Creating Pull Request ===")

    # Note: This requires a valid GitHub token
    # Set PLATFORM_TOKEN_GITHUB environment variable

    pal = get_pal()
    driver = await pal.get_driver(PlatformType.GITHUB)

    if not os.getenv("PLATFORM_TOKEN_GITHUB"):
        print("Skipped: PLATFORM_TOKEN_GITHUB not set")
        await pal.close_all()
        return

    print("Attempting to create pull request...")
    print("(This is a dry-run example - adjust parameters for your repository)")

    try:
        pr = await driver.create_pull_request(
            owner="your-org",
            repo="your-repo",
            title="feat: New feature",
            source_branch="feature/new-feature",
            target_branch="main",
            description="## Changes\n- Added new functionality\n- Updated tests",
            labels=["enhancement", "automated"]
        )

        print(f"✓ Created PR: {pr.url}")
        print(f"  Number: {pr.number}")
        print(f"  State: {pr.state}")

    except ValueError as e:
        print(f"Note: {e}")

    await pal.close_all()


async def main():
    """Run all examples."""
    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Multi-Platform", example_2_multi_platform),
        ("Pull Requests", example_3_pull_requests),
        ("Commits", example_4_commits),
        ("Workflows", example_5_workflows),
        ("Capabilities", example_6_capabilities),
        ("Error Handling", example_7_error_handling),
        ("Custom Config", example_8_custom_config),
        ("Batch Operations", example_9_batch_operations),
        ("Creating PR", example_10_creating_pr),
    ]

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   Platform Abstraction Layer - Usage Examples                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    for name, func in examples:
        try:
            await func()
        except Exception as e:
            print(f"\n⚠ Error in {name}: {e}")

        # Add separator
        print("\n" + "─" * 70)


if __name__ == "__main__":
    asyncio.run(main())
