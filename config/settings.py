"""
Central Configuration Management for UI Regression and Workflow Testing.

Provides typed, validated configuration parameters loaded from environment variables
(.env file) with graceful fallbacks for backward compatibility with the existing
crawler and comparer setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Automatically load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _get_bool(key: str, default: bool = False) -> bool:
    """Helper to parse boolean values from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "on")


def _get_int(key: str, default: int) -> int:
    """Helper to parse integer values from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class PortalCredentials:
    """Credentials and endpoints for an individual portal."""
    base_url: str
    username: str
    password: str
    login_url: str = ""
    post_login_url_pattern: str = ""
    auth_state_path: Path = field(default_factory=lambda: ROOT_DIR / "auth" / "auth_state.json")


@dataclass(frozen=True)
class BrowserSettings:
    """Browser launch and execution parameters."""
    browser_type: str = "chromium"
    headless: bool = True
    slow_mo: int = 0
    timeout: int = 30000  # ms
    viewport_width: int = 1280
    viewport_height: int = 900
    screenshot_on_failure: bool = True
    trace_on_failure: bool = True
    video_recording: bool = False

    @property
    def viewport(self) -> Dict[str, int]:
        return {"width": self.viewport_width, "height": self.viewport_height}


@dataclass
class Settings:
    """
    Unified Application and Test Framework Settings.
    Exposes portal settings, browser settings, and file paths.
    """
    env_name: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "staging").lower())
    root_dir: Path = ROOT_DIR

    # Path directories
    auth_dir: Path = ROOT_DIR / "auth"
    reports_dir: Path = ROOT_DIR / "reports"
    workflow_reports_dir: Path = ROOT_DIR / "reports" / "workflows"
    ui_regression_reports_dir: Path = ROOT_DIR / "reports" / "ui_regression"
    screenshots_dir: Path = ROOT_DIR / "reports" / "workflows" / "screenshots"
    traces_dir: Path = ROOT_DIR / "reports" / "workflows" / "traces"

    # Browser Execution Settings
    browser: BrowserSettings = field(init=False)

    # Portal Specific Configurations
    trade_terminal: PortalCredentials = field(init=False)
    admin_portal: PortalCredentials = field(init=False)
    client_portal: PortalCredentials = field(init=False)

    # Legacy / Crawler & Comparer URLs for backward compatibility
    baseline_url: str = field(init=False)
    live_url: str = field(init=False)
    enable_trade_tests: bool = field(init=False)

    def __post_init__(self):
        # 1. Initialize Directories
        for directory in [
            self.auth_dir,
            self.reports_dir,
            self.workflow_reports_dir,
            self.ui_regression_reports_dir,
            self.screenshots_dir,
            self.traces_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # 2. Browser Settings
        headless = _get_bool("BROWSER_HEADLESS", _get_bool("CRAWLER_HEADLESS", True))
        slow_mo = _get_int("BROWSER_SLOW_MO", 0)
        timeout = _get_int("BROWSER_TIMEOUT", _get_int("CRAWLER_TIMEOUT", 30000))
        viewport_w = _get_int("VIEWPORT_WIDTH", 1280)
        viewport_h = _get_int("VIEWPORT_HEIGHT", 900)
        screenshot_on_failure = _get_bool("SCREENSHOT_ON_FAILURE", True)
        trace_on_failure = _get_bool("TRACE_ON_FAILURE", True)
        video_recording = _get_bool("VIDEO_RECORDING", False)

        self.browser = BrowserSettings(
            browser_type=os.getenv("BROWSER_TYPE", "chromium").lower(),
            headless=headless,
            slow_mo=slow_mo,
            timeout=timeout,
            viewport_width=viewport_w,
            viewport_height=viewport_h,
            screenshot_on_failure=screenshot_on_failure,
            trace_on_failure=trace_on_failure,
            video_recording=video_recording,
        )

        # 3. Baseline & Live URL (Crawler compatibility)
        self.baseline_url = os.getenv("BASELINE_URL") or os.getenv("BASE_URL", "https://stage.xtremenext.com/")
        self.live_url = os.getenv("LIVE_URL", self.baseline_url)
        self.enable_trade_tests = _get_bool("ENABLE_TRADE_TESTS", False)

        # 4. Trade Terminal Settings
        trade_url = (
            os.getenv("TRADE_TERMINAL_URL")
            or os.getenv("BASELINE_URL")
            or os.getenv("BASE_URL", "https://stage.xtremenext.com/")
        )
        trade_username = (
            os.getenv("TRADE_USERNAME")
            or os.getenv("BASELINE_TEST_USER_EMAIL")
            or os.getenv("TEST_USER_EMAIL", "")
        )
        trade_password = (
            os.getenv("TRADE_PASSWORD")
            or os.getenv("BASELINE_TEST_USER_PASSWORD")
            or os.getenv("TEST_USER_PASSWORD", "")
        )
        trade_auth_state = self.auth_dir / "auth_state_trade.json"
        # Fallback to root auth_state.json if present
        if (self.root_dir / "auth_state.json").exists() and not trade_auth_state.exists():
            trade_auth_state = self.root_dir / "auth_state.json"

        self.trade_terminal = PortalCredentials(
            base_url=trade_url,
            username=trade_username,
            password=trade_password,
            login_url=os.getenv("TRADE_LOGIN_URL") or f"{trade_url.rstrip('/')}/login/",
            post_login_url_pattern=os.getenv("TRADE_POST_LOGIN_URL_PATTERN", "**/dashboard**"),
            auth_state_path=trade_auth_state,
        )

        # 5. Admin Portal Settings
        admin_url = (
            os.getenv("ADMIN_PORTAL_URL")
            or os.getenv("BASELINE_ADMIN_BASE_URL")
            or os.getenv("ADMIN_BASE_URL", "https://stage.xtremenext.com/admin/Controlbase/Dashboard")
        )
        admin_login = (
            os.getenv("ADMIN_LOGIN_URL")
            or os.getenv("BASELINE_ADMIN_LOGIN_URL", "https://stage.xtremenext.com/admin/Login/index")
        )
        admin_username = (
            os.getenv("ADMIN_USERNAME")
            or os.getenv("BASELINE_ADMIN_USER_USERNAME", "madmin")
        )
        admin_password = (
            os.getenv("ADMIN_PASSWORD")
            or os.getenv("BASELINE_ADMIN_USER_PASSWORD", "")
        )
        admin_auth_state = self.auth_dir / "auth_state_admin.json"
        if (self.root_dir / "auth_state_admin.json").exists() and not admin_auth_state.exists():
            admin_auth_state = self.root_dir / "auth_state_admin.json"

        self.admin_portal = PortalCredentials(
            base_url=admin_url,
            username=admin_username,
            password=admin_password,
            login_url=admin_login,
            post_login_url_pattern=os.getenv("ADMIN_POST_LOGIN_URL_PATTERN", "**/admin/Controlbase/**"),
            auth_state_path=admin_auth_state,
        )

        # 6. Client Portal Settings
        client_url = (
            os.getenv("CLIENT_PORTAL_URL")
            or os.getenv("BASELINE_URL")
            or os.getenv("BASE_URL", "https://stage.xtremenext.com/")
        )
        client_username = (
            os.getenv("CLIENT_USERNAME")
            or os.getenv("BASELINE_TEST_USER_EMAIL")
            or os.getenv("TEST_USER_EMAIL", "")
        )
        client_password = (
            os.getenv("CLIENT_PASSWORD")
            or os.getenv("BASELINE_TEST_USER_PASSWORD")
            or os.getenv("TEST_USER_PASSWORD", "")
        )
        client_auth_state = self.auth_dir / "auth_state_client.json"
        if (self.root_dir / "auth_state.json").exists() and not client_auth_state.exists():
            client_auth_state = self.root_dir / "auth_state.json"

        self.client_portal = PortalCredentials(
            base_url=client_url,
            username=client_username,
            password=client_password,
            login_url=os.getenv("CLIENT_LOGIN_URL", client_url),
            post_login_url_pattern=os.getenv("CLIENT_POST_LOGIN_URL_PATTERN", "**/dashboard**"),
            auth_state_path=client_auth_state,
        )


# Singleton instance for easy import across fixtures and pages
settings = Settings()
