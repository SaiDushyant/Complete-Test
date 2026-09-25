"""
Screenshot capture utility for workflow tests.
Safely saves full-page and element screenshots with sanitized filenames.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("screenshot_util")


def sanitize_filename(name: str) -> str:
    """Sanitize strings for safe cross-platform file naming."""
    sanitized = re.sub(r"[^\w\-_.]", "_", name)
    return re.sub(r"_+", "_", sanitized).strip("_")


def capture_screenshot(
    page: Page,
    test_name: str,
    suffix: str = "failure",
    full_page: bool = True,
    destination_dir: Optional[Path] = None,
) -> Path:
    """
    Capture and save a screenshot of the current page.
    """
    target_dir = destination_dir or settings.screenshots_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_test_name = sanitize_filename(test_name)
    clean_suffix = sanitize_filename(suffix)
    filename = f"{clean_test_name}_{clean_suffix}_{timestamp}.png"
    filepath = target_dir / filename

    try:
        page.screenshot(path=str(filepath), full_page=full_page)
        logger.info(f"Screenshot captured: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to capture screenshot for '{test_name}': {e}")
        return filepath


def capture_element_screenshot(
    locator: Locator,
    element_name: str,
    destination_dir: Optional[Path] = None,
) -> Optional[Path]:
    """
    Capture screenshot of a specific locator.
    """
    target_dir = destination_dir or settings.screenshots_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = sanitize_filename(element_name)
    filepath = target_dir / f"element_{clean_name}_{timestamp}.png"

    try:
        locator.screenshot(path=str(filepath))
        logger.info(f"Element screenshot captured: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to capture element screenshot '{element_name}': {e}")
        return None
