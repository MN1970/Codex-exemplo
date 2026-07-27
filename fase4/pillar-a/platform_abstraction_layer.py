"""Platform Abstraction Layer - Main service."""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

import yaml

from drivers.base import (
    BasePlatformDriver,
    PlatformType,
    DriverCapability,
    PlatformConfig,
)
from drivers import GitHubDriver, GitLabDriver, BitbucketDriver, GiteaDriver
from detection.platform_detector import PlatformDetector


logger = logging.getLogger(__name__)


class PlatformAbstractionLayer:
    """Main PAL service that routes operations to appropriate platform drivers."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize PAL.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.detector = PlatformDetector(
            use_git_cli_fallback=self.config["fallback"]["use_git_cli"]
        )
        self.drivers: Dict[PlatformType, BasePlatformDriver] = {}
        self._init_drivers()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "config_schema.yaml"
            )

        with open(config_path, "r") as f:
            full_config = yaml.safe_load(f)

        return full_config.get("platform_abstraction_layer", {})

    def _init_drivers(self):
        """Initialize platform drivers based on configuration."""
        platforms = self.config.get("platforms", {})

        for platform_name, platform_config in platforms.items():
            if not platform_config.get("enabled", False):
                continue

            platform_type = PlatformType(platform_name)

            # Get authentication token from environment
            token_env_var = (
                f"{self.config['authentication']['token_env_prefix']}_"
                f"{platform_name.upper()}"
            )
            token = os.getenv(token_env_var)

            # Create platform config
            config = PlatformConfig(
                api_version=platform_config["api_version"],
                base_url_api=platform_config["base_urls"]["api"],
                base_url_web=platform_config["base_urls"]["web"],
                timeout_seconds=platform_config.get("timeout_seconds", 30),
                retry_attempts=platform_config.get("retry_attempts", 3),
                retry_backoff_factor=platform_config.get("retry_backoff_factor", 2.0),
                rate_limit_handling=platform_config.get("rate_limit_handling", "backoff"),
                verify_ssl=self.config["authentication"].get("verify_ssl", True),
                ca_bundle_path=self.config["authentication"].get("ca_bundle_path"),
            )

            # Instantiate appropriate driver
            if platform_type == PlatformType.GITHUB:
                driver = GitHubDriver(config, token)
            elif platform_type == PlatformType.GITLAB:
                driver = GitLabDriver(config, token)
            elif platform_type == PlatformType.BITBUCKET:
                driver = BitbucketDriver(config, token)
            elif platform_type == PlatformType.GITEA:
                driver = GiteaDriver(config, token)
            else:
                logger.warning(f"Unsupported platform: {platform_name}")
                continue

            self.drivers[platform_type] = driver
            logger.info(f"Initialized driver for {platform_name}")

    async def get_driver(self, platform: PlatformType) -> BasePlatformDriver:
        """Get a driver for the specified platform.

        Args:
            platform: Platform type

        Returns:
            Platform driver instance

        Raises:
            ValueError: If platform not available
        """
        if platform not in self.drivers:
            raise ValueError(
                f"Driver not available for platform: {platform.value}. "
                f"Available: {[p.value for p in self.drivers.keys()]}"
            )

        return self.drivers[platform]

    async def detect_and_get_driver(
        self, url: str
    ) -> tuple[BasePlatformDriver, float]:
        """Detect platform from URL and get appropriate driver.

        Args:
            url: Repository URL

        Returns:
            Tuple of (driver, detection_time_ms)

        Raises:
            ValueError: If platform cannot be detected or driver not available
        """
        start_time = asyncio.get_event_loop().time()

        platform, detection_time = await self.detector.detect_from_url(url)
        driver = await self.get_driver(platform)

        total_time = (asyncio.get_event_loop().time() - start_time) * 1000

        logger.info(
            f"Detected platform {platform.value} for {url} "
            f"(detection: {detection_time:.2f}ms, total: {total_time:.2f}ms)"
        )

        return driver, detection_time

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all configured drivers.

        Returns:
            Health status dictionary
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {},
        }

        for platform, driver in self.drivers.items():
            try:
                health = driver.health_check()
                results["platforms"][platform.value] = {
                    "status": "healthy",
                    "capabilities": [c.value for c in driver.capabilities],
                    **health,
                }
            except Exception as e:
                results["platforms"][platform.value] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

        results["overall_status"] = (
            "healthy"
            if all(p["status"] == "healthy" for p in results["platforms"].values())
            else "degraded"
        )

        return results

    async def list_capabilities(self) -> Dict[str, List[str]]:
        """List capabilities for each available platform.

        Returns:
            Dictionary mapping platform names to capability lists
        """
        capabilities = {}

        for platform, driver in self.drivers.items():
            capabilities[platform.value] = [
                c.value for c in driver.capabilities
            ]

        return capabilities

    async def close_all(self):
        """Close all driver connections."""
        for driver in self.drivers.values():
            await driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            asyncio.run(self.close_all())
        except RuntimeError:
            pass


# Convenience function for quick access
def get_pal(config_path: Optional[str] = None) -> PlatformAbstractionLayer:
    """Get a PAL instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        PlatformAbstractionLayer instance
    """
    return PlatformAbstractionLayer(config_path)
