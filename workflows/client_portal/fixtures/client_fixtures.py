"""
Client Portal Pytest Fixtures.
Provides isolated pages, authenticated sessions, and page objects for Client Portal tests.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_watchlist_page import ClientWatchlistPage
from workflows.client_portal.pages.profile_page import ClientProfilePage
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context


def _perform_client_login(page: Page, creds) -> None:
    """Helper used to generate fresh Client authentication session."""
    login_page = ClientLoginPage(page)
    login_page.navigate(creds.login_url or creds.base_url)
    login_page.login(
        email=creds.username,
        password=creds.password,
        remember_me=True,
    )
    if creds.post_login_url_pattern:
        try:
            page.wait_for_url(creds.post_login_url_pattern, timeout=15000)
        except Exception:
            pass


@pytest.fixture(scope="function")
def client_page(workflow_page: Page) -> Page:
    """Unauthenticated page for Client Portal login and registration tests."""
    return workflow_page


@pytest.fixture(scope="function")
def authenticated_client_context(workflow_browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Browser context pre-authenticated for Client Portal workflows.
    Reuses auth_state_client.json or auth_state.json when valid.
    """
    context = ensure_authenticated_context(
        browser=workflow_browser,
        credentials=settings.client_portal,
        login_action_fn=_perform_client_login,
        auth_state_file=settings.client_portal.auth_state_path,
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def authenticated_client_page(authenticated_client_context: BrowserContext) -> Generator[Page, None, None]:
    """Pre-authenticated page instance for Client Portal workflow tests."""
    page = authenticated_client_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    yield page
    page.close()


@pytest.fixture(scope="function")
def client_login_page(client_page: Page) -> ClientLoginPage:
    """Provide an unauthenticated ClientLoginPage object."""
    return ClientLoginPage(client_page)


@pytest.fixture(scope="function")
def client_dashboard_page(authenticated_client_page: Page) -> ClientDashboardPage:
    """Provide an authenticated ClientDashboardPage object."""
    return ClientDashboardPage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_profile_page(authenticated_client_page: Page) -> ClientProfilePage:
    """Provide an authenticated ClientProfilePage object."""
    return ClientProfilePage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_watchlist_page(authenticated_client_page: Page) -> ClientWatchlistPage:
    """Provide an authenticated ClientWatchlistPage object."""
    return ClientWatchlistPage(authenticated_client_page)
