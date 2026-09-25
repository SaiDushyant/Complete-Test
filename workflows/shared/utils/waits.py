"""
Playwright Dynamic Synchronization and Wait Utilities.
"""

from __future__ import annotations

import time
from typing import Callable, Optional

from playwright.sync_api import Locator, Page

from workflows.shared.constants.timeouts import (
    TIMEOUT_DEFAULT,
    TIMEOUT_INSTANT,
    TIMEOUT_NETWORK_IDLE,
    TIMEOUT_SHORT,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("waits_util")


def wait_for_network_idle(page: Page, timeout: int = TIMEOUT_NETWORK_IDLE) -> None:
    """
    Wait until network activity has subsided (no network connections for at least 500ms).
    """
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception as e:
        logger.warning(f"Network did not reach idle state within {timeout}ms: {e}")


def wait_for_dom_ready(page: Page, timeout: int = TIMEOUT_DEFAULT) -> None:
    """
    Wait until DOMContentLoaded load state is fired.
    """
    page.wait_for_load_state("domcontentloaded", timeout=timeout)


def wait_for_condition(
    condition_fn: Callable[[], bool],
    timeout_seconds: float = 10.0,
    interval_seconds: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """
    Poll an arbitrary boolean condition until it returns True or timeout is reached.
    """
    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        try:
            if condition_fn():
                return True
        except Exception:
            pass
        time.sleep(interval_seconds)

    raise TimeoutError(f"{error_message} (waited {timeout_seconds}s)")


def wait_for_element_state(
    locator: Locator,
    state: str = "visible",
    timeout: int = TIMEOUT_DEFAULT,
) -> None:
    """
    Wait for an element locator to transition into a specific state.
    Allowed states: 'attached', 'detached', 'visible', 'hidden'.
    """
    locator.wait_for(state=state, timeout=timeout)
