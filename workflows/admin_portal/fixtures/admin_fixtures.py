"""
Admin Portal Pytest Fixtures.
Provides isolated pages, authenticated sessions, and page objects for Admin tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.admin_portal.pages.admin_dashboard_page import AdminDashboardPage
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_settings_page import AdminSettingsPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context
from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage
from workflows.admin_portal.pages.admin_cron_jobs_page import AdminCronJobsPage
from workflows.admin_portal.pages.admin_lp_execution_config_page import (
    AdminLpExecutionConfigPage,
)
from workflows.admin_portal.pages.admin_user_transaction_log_page import AdminUserTransactionLogPage
from workflows.admin_portal.pages.admin_oxapay_page import AdminOxapayPage
from workflows.admin_portal.pages.admin_user_order_report_page import AdminUserOrderReportPage  
from workflows.admin_portal.pages.admin_refer_report_page import AdminReferReportPage
def _perform_admin_login(page: Page, creds) -> None:
    """Helper used to generate fresh Admin authentication session."""
    login_page = AdminLoginPage(page)
    login_page.navigate(creds.login_url or creds.base_url)
    login_page.login(
        username=creds.username,
        password=creds.password,
    )
    if creds.post_login_url_pattern:
        try:
            page.wait_for_url(creds.post_login_url_pattern, timeout=15000)
        except Exception:
            pass


@pytest.fixture(scope="function")
def admin_page(workflow_page: Page) -> Page:
    """Unauthenticated page for Admin login/public flow testing."""
    return workflow_page


@pytest.fixture(scope="function")
def authenticated_admin_context(workflow_browser: Browser) -> Generator[BrowserContext, None, None]:
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
def authenticated_admin_page(authenticated_admin_context: BrowserContext) -> Generator[Page, None, None]:
    """Pre-authenticated page instance for Admin Console tests."""
    page = authenticated_admin_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    yield page
    page.close()


@pytest.fixture(scope="function")
def admin_login_page(admin_page: Page) -> AdminLoginPage:
    """Provide an unauthenticated AdminLoginPage object."""
    return AdminLoginPage(admin_page)


@pytest.fixture(scope="function")
def admin_dashboard_page(authenticated_admin_page: Page) -> AdminDashboardPage:
    """Provide an authenticated AdminDashboardPage object."""
    return AdminDashboardPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def user_management_page(authenticated_admin_page: Page) -> UserManagementPage:
    """Provide an authenticated UserManagementPage object."""
    return UserManagementPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_settings_page(authenticated_admin_page: Page) -> AdminSettingsPage:
    """Provide an authenticated AdminSettingsPage object."""
    return AdminSettingsPage(authenticated_admin_page)
@pytest.fixture(scope="function")
def admin_cron_jobs_page(
    authenticated_admin_page: Page,
) -> AdminCronJobsPage:
    return AdminCronJobsPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_lp_execution_config_page(
    authenticated_admin_page: Page,
) -> AdminLpExecutionConfigPage:
    return AdminLpExecutionConfigPage(authenticated_admin_page)

@pytest.fixture(scope="function")
def admin_oxapay_page(
    authenticated_admin_page: Page,
) -> AdminOxapayPage:
    return AdminOxapayPage(authenticated_admin_page)

@pytest.fixture(scope="function")
def admin_user_order_report_page(
    authenticated_admin_page: Page,
) -> AdminUserOrderReportPage:
    return AdminUserOrderReportPage(authenticated_admin_page)

@pytest.fixture(scope="function")
def admin_refer_report_page(
    authenticated_admin_page: Page,
) -> AdminReferReportPage:
    return AdminReferReportPage(authenticated_admin_page)

from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage


# in workflows/admin_portal/fixtures/admin_fixtures.py

@pytest.fixture(scope="function")
def admin_order_edit_log_page(
    authenticated_admin_page: Page,
) -> AdminOrderEditLogPage:
    return AdminOrderEditLogPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_user_transaction_log_page(
    authenticated_admin_page: Page,
) -> AdminUserTransactionLogPage:
    return AdminUserTransactionLogPage(authenticated_admin_page)


from workflows.admin_portal.pages.admin_active_users_page import AdminActiveUsersPage


@pytest.fixture(scope="function")
def admin_active_users_page(
    authenticated_admin_page: Page,
) -> AdminActiveUsersPage:
    return AdminActiveUsersPage(authenticated_admin_page)


from workflows.admin_portal.pages.admin_user_bonus_page import AdminUserBonusPage


@pytest.fixture(scope="function")
def admin_user_bonus_page(
    authenticated_admin_page: Page,
) -> AdminUserBonusPage:
    return AdminUserBonusPage(authenticated_admin_page)


from workflows.admin_portal.pages.admin_symbol_configuration_page import (
    AdminSymbolConfigurationPage,
)


@pytest.fixture(scope="function")
def admin_symbol_configuration_page(
    authenticated_admin_page: Page,
) -> AdminSymbolConfigurationPage:
    return AdminSymbolConfigurationPage(authenticated_admin_page)


from workflows.admin_portal.pages.admin_symbol_list_page import AdminSymbolListPage


@pytest.fixture(scope="function")
def admin_symbol_list_page(
    authenticated_admin_page: Page,
) -> AdminSymbolListPage:
    return AdminSymbolListPage(authenticated_admin_page)


from workflows.admin_portal.pages.admin_user_group_page import AdminUserGroupPage


@pytest.fixture(scope="function")
def admin_user_group_page(
    authenticated_admin_page: Page,
) -> AdminUserGroupPage:
    return AdminUserGroupPage(authenticated_admin_page)



