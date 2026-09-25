"""
Shared Authentication Fixture Helpers.
Handles reusable login flows and session state caching for workflow tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import PortalCredentials, settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("auth_fixtures")


def ensure_authenticated_context(
    browser: Browser,
    credentials: PortalCredentials,
    login_action_fn,
    auth_state_file: Path,
) -> BrowserContext:
    """
    Ensure a browser context has valid authentication state.
    Reuses cached auth_state JSON file if valid; otherwise performs login and caches state.
    """
    auth_state_file.parent.mkdir(parents=True, exist_ok=True)

    if auth_state_file.exists() and auth_state_file.stat().st_size > 0:
        logger.info(f"Reusing existing auth state: {auth_state_file}")
        try:
            context = browser.new_context(
                storage_state=str(auth_state_file),
                viewport=settings.browser.viewport,
                ignore_https_errors=True,
            )
            return context
        except Exception as e:
            logger.warning(f"Failed to restore auth state ({e}). Re-authenticating...")

    # Create fresh context and authenticate
    logger.info(f"Creating fresh authenticated context for: {credentials.base_url}")
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()

    try:
        login_action_fn(page, credentials)
        context.storage_state(path=str(auth_state_file))
        logger.info(f"Saved fresh authentication state to: {auth_state_file}")
    finally:
        page.close()

    return context
