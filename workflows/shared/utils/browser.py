"""
Browser and Context Management Helpers.
Provides cross-portal utilities for context creation, cookie clearing,
tab management, and viewport adjustments.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.shared.constants.viewports import VIEWPORTS
from workflows.shared.utils.logger import get_logger

logger = get_logger("browser_util")


def set_viewport_by_name(page: Page, viewport_name: str) -> None:
    """
    Dynamically set the page viewport to a recognized named breakpoint.
    Supported names: 'sm', 'md', 'lg', 'xl', '2xl'.
    """
    if viewport_name not in VIEWPORTS:
        raise ValueError(f"Unknown viewport '{viewport_name}'. Supported: {list(VIEWPORTS.keys())}")
    dimensions = VIEWPORTS[viewport_name]
    page.set_viewport_size(dimensions)
    logger.info(f"Viewport adjusted to '{viewport_name}' ({dimensions['width']}x{dimensions['height']})")


def clear_context_storage(context: BrowserContext) -> None:
    """
    Clear all cookies and local storage for test isolation.
    """
    context.clear_cookies()
    logger.info("Cleared browser context cookies.")


def get_all_page_urls(context: BrowserContext) -> List[str]:
    """
    Return URLs of all currently open pages/tabs in the context.
    """
    return [p.url for p in context.pages]


def close_extra_tabs(context: BrowserContext, keep_page: Page) -> None:
    """
    Close all open tabs except the designated primary page.
    """
    for page in context.pages:
        if page != keep_page:
            try:
                page.close()
            except Exception:
                pass
