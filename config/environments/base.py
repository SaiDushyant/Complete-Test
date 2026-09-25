"""
Base Environment Profile.
Defines common configuration constants and schema across test environments.
"""

from typing import Dict, Any


class BaseEnvConfig:
    """Base environment configuration."""
    ENV_NAME = "base"
    DEFAULT_TIMEOUT_MS = 30000
    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 900
    SLOW_MO_MS = 0

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            "env_name": cls.ENV_NAME,
            "default_timeout_ms": cls.DEFAULT_TIMEOUT_MS,
            "viewport": {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT},
            "slow_mo_ms": cls.SLOW_MO_MS,
        }
