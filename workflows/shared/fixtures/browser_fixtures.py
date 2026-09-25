"""
Centralized Browser and Context Fixtures for Workflow Testing.
Provides trace capture, automatic screenshot on failure, and viewport isolation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config.settings import settings
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.screenshot import capture_screenshot, sanitize_filename

logger = get_logger("browser_fixtures")


@pytest.fixture(scope="session")
def workflow_browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """
    Session-scoped Playwright Browser instance configured via settings.
    """
    logger.info(
        f"Launching {settings.browser.browser_type} (headless={settings.browser.headless}, slow_mo={settings.browser.slow_mo}ms)"
    )
    browser = playwright.chromium.launch(
        headless=settings.browser.headless,
        slow_mo=settings.browser.slow_mo,
    )
    yield browser
    logger.info("Closing session browser.")
    browser.close()


@pytest.fixture(scope="function")
def workflow_context(
    workflow_browser: Browser,
    request: pytest.FixtureRequest,
) -> Generator[BrowserContext, None, None]:
    """
    Function-scoped browser context with viewport configuration and tracing.
    """
    context = workflow_browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )

    # Start tracing if enabled in settings
    if settings.browser.trace_on_failure:
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    yield context

    # Test failure handling: save trace
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed and settings.browser.trace_on_failure:
        clean_name = sanitize_filename(request.node.name)
        trace_path = settings.traces_dir / f"trace_{clean_name}.zip"
        try:
            context.tracing.stop(path=str(trace_path))
            logger.info(f"Test failed. Trace saved to: {trace_path}")
        except Exception as e:
            logger.error(f"Failed to save trace: {e}")
    else:
        try:
            context.tracing.stop()
        except Exception:
            pass

    context.close()


@pytest.fixture(scope="function")
def workflow_page(
    workflow_context: BrowserContext,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    """
    Function-scoped fresh Playwright page with automatic screenshot on failure.
    """
    page = workflow_context.new_page()
    page.set_default_timeout(settings.browser.timeout)

    yield page

    # Screenshot on test failure
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed and settings.browser.screenshot_on_failure:
        capture_screenshot(
            page=page,
            test_name=request.node.name,
            suffix="failure",
            destination_dir=settings.screenshots_dir,
        )

    try:
        page.close()
    except Exception:
        pass
