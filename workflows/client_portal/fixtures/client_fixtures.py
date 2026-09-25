"""
Client Portal Pytest Fixtures.
Provides isolated pages, authenticated sessions, page objects, and automated error monitors.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.client_portal.pages.profile_page import ClientProfilePage
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context
from workflows.shared.utils.error_monitor import ErrorMonitor


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
    """Unauthenticated page for Client Portal login and registration tests with error monitor."""
    if not hasattr(workflow_page, "error_monitor"):
        workflow_page.error_monitor = ErrorMonitor(workflow_page)
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
    """Pre-authenticated page instance with automated console, JS, and backend error monitoring."""
    page = authenticated_client_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    page.error_monitor = ErrorMonitor(page)
    yield page
    page.close()


@pytest.fixture(scope="function")
def client_error_monitor(authenticated_client_page: Page) -> ErrorMonitor:
    """Provide the active ErrorMonitor for the current test page."""
    return authenticated_client_page.error_monitor


@pytest.fixture(scope="function")
def client_login_page(client_page: Page) -> ClientLoginPage:
    """Provide an unauthenticated ClientLoginPage object."""
    return ClientLoginPage(client_page)


@pytest.fixture(scope="function")
def client_dashboard_page(authenticated_client_page: Page) -> ClientDashboardPage:
    """Provide an authenticated ClientDashboardPage object."""
    return ClientDashboardPage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_settings_page(authenticated_client_page: Page) -> ClientSettingsPage:
    """Provide an authenticated ClientSettingsPage object."""
    return ClientSettingsPage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_refer_earn_page(authenticated_client_page: Page) -> ClientReferEarnPage:
    """Provide an authenticated ClientReferEarnPage object."""
    return ClientReferEarnPage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_profile_page(authenticated_client_page: Page) -> ClientProfilePage:
    """Provide an authenticated ClientProfilePage object."""
    return ClientProfilePage(authenticated_client_page)


@pytest.fixture(scope="function")
def client_deposit_page(authenticated_client_page: Page) -> ClientDepositPage:
    """Provide an authenticated ClientDepositPage object."""
    return ClientDepositPage(authenticated_client_page)

