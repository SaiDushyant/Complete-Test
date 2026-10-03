"""
Pytest Fixtures for Mock Testing.
Provides mock_router, mock_page, and isolated browser context fixtures.
"""

from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.shared.mocks.mock_router import MockRouter


@pytest.fixture
def mock_router(request: pytest.FixtureRequest) -> Generator[MockRouter, None, None]:
    """
    Function-scoped MockRouter attached to the page instance used by the test.
    Prefers 'workflow_page' if requested in the test, otherwise falls back to 'mock_page' or 'page'.
    Automatically unregisters all active route intercepts upon test teardown.
    """
    if "workflow_page" in request.fixturenames:
        active_page = request.getfixturevalue("workflow_page")
    elif "mock_page" in request.fixturenames:
        active_page = request.getfixturevalue("mock_page")
    elif "page" in request.fixturenames:
        active_page = request.getfixturevalue("page")
    else:
        active_page = request.getfixturevalue("workflow_page")

    router = MockRouter(active_page)
    yield router
    router.clear()


@pytest.fixture
def mock_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Fresh, unauthenticated browser context isolated for mock testing.
    """
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    yield context
    context.close()


@pytest.fixture
def mock_page(mock_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Fresh, isolated Page instance with an active MockRouter fixture.
    """
    page = mock_context.new_page()
    yield page
    page.close()
