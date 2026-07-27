"""Tests for platform detection."""

import asyncio
import pytest

from detection.platform_detector import PlatformDetector
from drivers.base import PlatformType


@pytest.mark.asyncio
class TestPlatformDetector:
    """Test platform detection functionality."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return PlatformDetector()

    async def test_detect_github_from_url(self, detector):
        """Test GitHub detection from URL."""
        urls = [
            "https://github.com/octocat/Hello-World",
            "git@github.com:octocat/Hello-World.git",
            "https://api.github.com/repos/octocat/Hello-World",
            "https://raw.githubusercontent.com/octocat/Hello-World/main/README.md",
        ]

        for url in urls:
            platform, elapsed = await detector.detect_from_url(url)
            assert platform == PlatformType.GITHUB
            assert elapsed < 15, f"Detection took {elapsed:.2f}ms (> 15ms)"

    async def test_detect_gitlab_from_url(self, detector):
        """Test GitLab detection from URL."""
        urls = [
            "https://gitlab.com/octocat/hello-world",
            "git@gitlab.com:octocat/hello-world.git",
            "https://gitlab.io/octocat/hello-world",
        ]

        for url in urls:
            platform, elapsed = await detector.detect_from_url(url)
            assert platform == PlatformType.GITLAB
            assert elapsed < 15, f"Detection took {elapsed:.2f}ms (> 15ms)"

    async def test_detect_bitbucket_from_url(self, detector):
        """Test Bitbucket detection from URL."""
        urls = [
            "https://bitbucket.org/octocat/hello-world",
            "git@bitbucket.org:octocat/hello-world.git",
        ]

        for url in urls:
            platform, elapsed = await detector.detect_from_url(url)
            assert platform == PlatformType.BITBUCKET
            assert elapsed < 15, f"Detection took {elapsed:.2f}ms (> 15ms)"

    async def test_detect_gitea_from_url(self, detector):
        """Test Gitea detection from URL."""
        urls = [
            "https://gitea.io/octocat/hello-world",
            "https://gitea.example.com/octocat/hello-world",
        ]

        for url in urls:
            platform, elapsed = await detector.detect_from_url(url)
            assert platform == PlatformType.GITEA
            assert elapsed < 15, f"Detection took {elapsed:.2f}ms (> 15ms)"

    async def test_cache_functionality(self, detector):
        """Test caching improves detection time."""
        url = "https://github.com/octocat/Hello-World"

        # First detection
        platform1, time1 = await detector.detect_from_url(url)

        # Second detection (should hit cache)
        platform2, time2 = await detector.detect_from_url(url)

        assert platform1 == platform2
        assert time2 <= time1, "Cached detection should be faster or equal"

    async def test_invalid_url_raises_error(self, detector):
        """Test that invalid URLs raise errors."""
        with pytest.raises(ValueError):
            await detector.detect_from_url("https://unknown-platform.com/repo")

    async def test_cache_stats(self, detector):
        """Test cache statistics."""
        await detector.detect_from_url("https://github.com/octocat/repo1")
        await detector.detect_from_url("https://gitlab.com/octocat/repo2")

        stats = detector.get_detection_stats()
        assert stats["cache_size"] == 2
        assert "cache_ttl_seconds" in stats

    async def test_clear_cache(self, detector):
        """Test cache clearing."""
        await detector.detect_from_url("https://github.com/octocat/repo1")
        assert detector.get_detection_stats()["cache_size"] == 1

        detector.clear_cache()
        assert detector.get_detection_stats()["cache_size"] == 0

    async def test_detection_latency_batch(self, detector):
        """Test detection latency for batch operations."""
        urls = [
            "https://github.com/octocat/repo1",
            "https://gitlab.com/octocat/repo2",
            "https://bitbucket.org/octocat/repo3",
            "https://gitea.io/octocat/repo4",
        ]

        times = []
        for url in urls:
            _, elapsed = await detector.detect_from_url(url)
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert max_time < 15, f"Max detection time {max_time:.2f}ms exceeds 15ms"
        print(f"Average detection time: {avg_time:.2f}ms, Max: {max_time:.2f}ms")


class TestDetectionPerformance:
    """Test detection performance metrics."""

    def test_pattern_matching_performance(self):
        """Test pattern matching performance."""
        detector = PlatformDetector()

        # Test pattern matching on various inputs
        test_cases = [
            ("github.com", PlatformType.GITHUB),
            ("gitlab.com", PlatformType.GITLAB),
            ("bitbucket.org", PlatformType.BITBUCKET),
            ("gitea.io", PlatformType.GITEA),
        ]

        import time
        start = time.time()
        for text, expected_platform in test_cases * 1000:
            result = detector._match_patterns(text)
            assert result == expected_platform

        elapsed = (time.time() - start) * 1000
        avg_per_match = elapsed / (len(test_cases) * 1000)

        assert avg_per_match < 0.1, f"Pattern matching too slow: {avg_per_match:.4f}ms per match"
        print(f"Pattern matching: {avg_per_match:.4f}ms per match ({elapsed:.2f}ms total)")
