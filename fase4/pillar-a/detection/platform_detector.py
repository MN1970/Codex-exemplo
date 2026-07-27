"""Platform detection service."""

import asyncio
import re
import subprocess
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

from drivers.base import PlatformType


class PlatformDetector:
    """Detects the git platform from various inputs (URL, config, etc).

    Target latency: < 15ms
    """

    # Precompiled patterns for fast matching
    PATTERNS = {
        PlatformType.GITHUB: [
            r"github\.com",
            r"raw\.githubusercontent\.com",
            r"api\.github\.com",
        ],
        PlatformType.GITLAB: [
            r"gitlab\.com",
            r"gitlab-ci\.com",
            r"gitlab\.io",
        ],
        PlatformType.BITBUCKET: [
            r"bitbucket\.org",
            r"bitbucket\.io",
        ],
        PlatformType.GITEA: [
            r"gitea\.io",
            r"gitea",
        ],
    }

    # Precompile patterns for performance
    _compiled_patterns = {
        platform: [re.compile(pattern) for pattern in patterns]
        for platform, patterns in PATTERNS.items()
    }

    # Cache for detected platforms
    _cache: Dict[str, Tuple[PlatformType, float]] = {}
    _cache_ttl = 3600  # 1 hour

    def __init__(self, use_git_cli_fallback: bool = True):
        """Initialize platform detector.

        Args:
            use_git_cli_fallback: Whether to use git CLI as fallback
        """
        self.use_git_cli_fallback = use_git_cli_fallback
        self._detection_times: Dict[str, float] = {}

    async def detect_from_url(self, url: str) -> Tuple[PlatformType, float]:
        """Detect platform from URL.

        Args:
            url: Git URL or web URL

        Returns:
            Tuple of (platform, detection_time_ms)

        Raises:
            ValueError: If platform cannot be detected
        """
        start_time = time.time()

        # Check cache first
        cache_key = f"url:{url}"
        if cache_key in self._cache:
            cached_platform, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                elapsed = (time.time() - start_time) * 1000
                return cached_platform, elapsed

        # Normalize URL
        url_normalized = url.lower().strip()

        # Try pattern matching
        platform = self._match_patterns(url_normalized)
        if platform:
            elapsed = (time.time() - start_time) * 1000
            self._cache[cache_key] = (platform, time.time())
            return platform, elapsed

        # Fallback: parse domain
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            platform = self._match_patterns(domain)
            if platform:
                elapsed = (time.time() - start_time) * 1000
                self._cache[cache_key] = (platform, time.time())
                return platform, elapsed
        except Exception:
            pass

        elapsed = (time.time() - start_time) * 1000
        raise ValueError(f"Cannot detect platform from URL: {url} (took {elapsed:.2f}ms)")

    async def detect_from_remote(
        self, remote_url: str = "origin"
    ) -> Tuple[PlatformType, float]:
        """Detect platform from git remote.

        Args:
            remote_url: Git remote name (default: origin)

        Returns:
            Tuple of (platform, detection_time_ms)

        Raises:
            ValueError: If platform cannot be detected
        """
        start_time = time.time()

        # Check cache
        cache_key = f"remote:{remote_url}"
        if cache_key in self._cache:
            cached_platform, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                elapsed = (time.time() - start_time) * 1000
                return cached_platform, elapsed

        try:
            # Get remote URL from git config
            result = subprocess.run(
                ["git", "config", "--get", f"remote.{remote_url}.url"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                raise ValueError(f"Cannot get remote URL: {remote_url}")

            git_url = result.stdout.strip()
            platform, elapsed_detection = await self.detect_from_url(git_url)

            elapsed = (time.time() - start_time) * 1000
            self._cache[cache_key] = (platform, time.time())

            return platform, elapsed

        except subprocess.TimeoutExpired:
            elapsed = (time.time() - start_time) * 1000
            raise ValueError(f"Timeout detecting remote (took {elapsed:.2f}ms)")
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            raise ValueError(
                f"Cannot detect platform from remote: {e} (took {elapsed:.2f}ms)"
            )

    async def detect_from_config(
        self, config: Dict[str, Any]
    ) -> Tuple[PlatformType, float]:
        """Detect platform from configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (platform, detection_time_ms)

        Raises:
            ValueError: If platform cannot be detected
        """
        start_time = time.time()

        # Try explicit platform specification
        if "platform" in config:
            platform_name = config["platform"].lower()
            try:
                platform = PlatformType(platform_name)
                elapsed = (time.time() - start_time) * 1000
                return platform, elapsed
            except ValueError:
                pass

        # Try URL from config
        if "url" in config:
            platform, _ = await self.detect_from_url(config["url"])
            elapsed = (time.time() - start_time) * 1000
            return platform, elapsed

        elapsed = (time.time() - start_time) * 1000
        raise ValueError(
            f"Cannot detect platform from config (took {elapsed:.2f}ms)"
        )

    def _match_patterns(self, text: str) -> Optional[PlatformType]:
        """Match text against precompiled patterns.

        Args:
            text: Text to match

        Returns:
            Detected platform or None
        """
        for platform, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return platform
        return None

    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics.

        Returns:
            Dictionary of detection stats
        """
        return {
            "cache_size": len(self._cache),
            "cache_ttl_seconds": self._cache_ttl,
            "detection_times": self._detection_times,
        }

    def clear_cache(self):
        """Clear the detection cache."""
        self._cache.clear()
        self._detection_times.clear()
