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
from workflows.shared.utils.diagnostics import PageDiagnostics
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.screenshot import capture_screenshot, sanitize_filename

logger = get_logger("browser_fixtures")


@pytest.fixture(scope="session")
def workflow_browser(
    playwright: Playwright,
    pytestconfig: pytest.Config,
) -> Generator[Browser, None, None]:
    """
    Session-scoped Playwright Browser instance configured via settings and CLI flags.
    Respects --headed and --slowmo CLI flags, as well as BROWSER_HEADLESS / BROWSER_SLOW_MO env vars.
    """
    # 1. Determine headless mode: CLI flag --headed takes precedence, then settings / env vars
    headed_flag = False
    try:
        headed_flag = bool(pytestconfig.getoption("--headed"))
    except Exception:
        pass

    headless = False if headed_flag else settings.browser.headless

    # 2. Determine slow_mo: CLI flag --slowmo takes precedence, then settings / env vars
    slow_mo = settings.browser.slow_mo
    try:
        cli_slowmo = pytestconfig.getoption("--slowmo")
        if cli_slowmo is not None:
            slow_mo = int(cli_slowmo)
    except Exception:
        pass

    # If running headed and slow_mo is 0, introduce a reasonable 300ms delay so interactions can be observed
    if not headless and slow_mo == 0:
        env_slow_mo = os.getenv("BROWSER_SLOW_MO")
        if env_slow_mo is not None:
            try:
                slow_mo = int(env_slow_mo)
            except ValueError:
                slow_mo = 300
        else:
            slow_mo = 300

    logger.info(
        f"Launching {settings.browser.browser_type} (headless={headless}, slow_mo={slow_mo}ms)"
    )
    browser = playwright.chromium.launch(
        headless=headless,
        slow_mo=slow_mo,
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
    Function-scoped fresh Playwright page with automatic runtime diagnostics,
    console monitoring, network tracking, and screenshot/log capture on failure.
    """
    page = workflow_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    diagnostics = PageDiagnostics(page)
    page._diagnostics = diagnostics

    yield page

    # Screenshot and diagnostics capture on test failure
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed:
        if settings.browser.screenshot_on_failure:
            capture_screenshot(
                page=page,
                test_name=request.node.name,
                suffix="failure",
                destination_dir=settings.screenshots_dir,
            )
        try:
            diag_path = diagnostics.save_report(
                test_name=request.node.name,
                destination_dir=settings.diagnostics_dir,
            )
            logger.info(f"Saved failure diagnostic telemetry to: {diag_path}")
            if diagnostics.has_errors():
                logger.error(
                    f"Diagnostic errors detected during failed test '{request.node.name}':\n"
                    f"{diagnostics.format_report()}"
                )
        except Exception as e:
            logger.error(f"Failed to save diagnostic telemetry: {e}")

    try:
        page.close()
    except Exception:
        pass
