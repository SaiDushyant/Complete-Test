"""
Staging Environment Profile.
"""

from config.environments.base import BaseEnvConfig


class StagingConfig(BaseEnvConfig):
    """Staging environment configuration settings."""
    ENV_NAME = "staging"
    TRADE_TERMINAL_URL = "https://stage.xtremenext.com/"
    ADMIN_PORTAL_URL = "https://stage.xtremenext.com/admin/Controlbase/Dashboard"
    CLIENT_PORTAL_URL = "https://stage.xtremenext.com/"
