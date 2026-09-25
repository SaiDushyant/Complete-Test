"""
Production Environment Profile.
"""

from config.environments.base import BaseEnvConfig


class ProductionConfig(BaseEnvConfig):
    """Production environment configuration profile."""
    ENV_NAME = "production"
    TRADE_TERMINAL_URL = "https://trade.xtremenext.com/"
    ADMIN_PORTAL_URL = "https://admin.xtremenext.com/admin/Controlbase/Dashboard"
    CLIENT_PORTAL_URL = "https://portal.xtremenext.com/"
