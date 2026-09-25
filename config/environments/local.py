"""
Local Development Environment Profile.
"""

from config.environments.base import BaseEnvConfig


class LocalConfig(BaseEnvConfig):
    """Local environment configuration profile."""
    ENV_NAME = "local"
    TRADE_TERMINAL_URL = "http://localhost:3000/"
    ADMIN_PORTAL_URL = "http://localhost:8080/admin/Controlbase/Dashboard"
    CLIENT_PORTAL_URL = "http://localhost:3001/"
    SLOW_MO_MS = 100
