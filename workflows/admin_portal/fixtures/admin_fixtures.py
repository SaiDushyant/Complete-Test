"""
Admin Portal Pytest Fixtures.
Provides isolated pages, authenticated sessions, and page objects for Admin tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.admin_portal.pages.admin_dashboard_page import AdminDashboardPage
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context


LOGIN_RESULT_FILE = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "loginresult.txt"
)


def _write_login_result(status: str, reason: str = "") -> None:
    """Overwrite the Admin login result file."""
    LOGIN_RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    LOGIN_RESULT_FILE.write_text(
        f"Admin login result\n"
        f"Status: {status}\n"
        f"Reason: {reason}\n",
        encoding="utf-8",
    )


def _perform_admin_login(page: Page, creds) -> None:
    """Perform Admin login and write the result to loginresult.txt."""
    login_page = AdminLoginPage(page)

    try:
        login_page.navigate(creds.login_url or creds.base_url)
        login_page.login(
            username=creds.username,
            password=creds.password,
        )

        if creds.post_login_url_pattern:
            page.wait_for_url(
                creds.post_login_url_pattern,
                timeout=15000,
            )

        _write_login_result(
            "PASSED",
            "Admin dashboard opened successfully",
        )

    except Exception as exc:
        _write_login_result(
            "FAILED",
            str(exc),
        )
        raise


@pytest.fixture(scope="function")
def admin_page(workflow_page: Page) -> Page:
    """Unauthenticated page for Admin login/public flow testing."""
    return workflow_page


@pytest.fixture(scope="function")
def authenticated_admin_context(
    workflow_browser: Browser,
) -> Generator[BrowserContext, None, None]:
    """
    Browser context pre-authenticated with Admin Console permissions.
    Reuses auth_state_admin.json when valid.
    """
    context = ensure_authenticated_context(
        browser=workflow_browser,
        credentials=settings.admin_portal,
        login_action_fn=_perform_admin_login,
        auth_state_file=settings.admin_portal.auth_state_path,
    )

    yield context
    context.close()


@pytest.fixture(scope="function")
def authenticated_admin_page(
    authenticated_admin_context: BrowserContext,
) -> Generator[Page, None, None]:
    """Pre-authenticated page instance for Admin Console tests."""
    page = authenticated_admin_context.new_page()
    page.set_default_timeout(settings.browser.timeout)

    yield page
    page.close()


@pytest.fixture(scope="function")
def admin_login_page(
    admin_page: Page,
) -> AdminLoginPage:
    """Provide an unauthenticated AdminLoginPage object."""
    return AdminLoginPage(admin_page)


@pytest.fixture(scope="function")
def admin_dashboard_page(
    authenticated_admin_page: Page,
) -> AdminDashboardPage:
    """Provide an authenticated AdminDashboardPage object."""
    return AdminDashboardPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def user_management_page(
    authenticated_admin_page: Page,
) -> UserManagementPage:
    """Provide an authenticated UserManagementPage object."""
    return UserManagementPage(authenticated_admin_page)