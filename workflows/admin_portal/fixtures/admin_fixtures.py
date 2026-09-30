"""
Admin Portal Pytest Fixtures.
Provides isolated pages, authenticated sessions, and page objects for Admin tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config.settings import settings
from workflows.admin_portal.pages.account_requests_page import AccountRequestsPage
from workflows.admin_portal.pages.admin_active_users_page import AdminActiveUsersPage
from workflows.admin_portal.pages.admin_cron_jobs_page import AdminCronJobsPage
from workflows.admin_portal.pages.admin_dashboard_page import AdminDashboardPage
from workflows.admin_portal.pages.admin_deposit_list_page import AdminDepositListPage
from workflows.admin_portal.pages.admin_deposit_page import AdminDepositPage
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_lp_execution_config_page import AdminLpExecutionConfigPage
from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.admin_oxapay_page import AdminOxapayPage
from workflows.admin_portal.pages.admin_refer_report_page import AdminReferReportPage
from workflows.admin_portal.pages.admin_settings_page import AdminSettingsPage
from workflows.admin_portal.pages.admin_symbol_configuration_page import AdminSymbolConfigurationPage
from workflows.admin_portal.pages.admin_symbol_list_page import AdminSymbolListPage
from workflows.admin_portal.pages.admin_user_bonus_page import AdminUserBonusPage
from workflows.admin_portal.pages.admin_user_group_page import AdminUserGroupPage
from workflows.admin_portal.pages.admin_user_order_report_page import AdminUserOrderReportPage
from workflows.admin_portal.pages.admin_user_transaction_log_page import AdminUserTransactionLogPage
from workflows.admin_portal.pages.admin_withdraw_list_page import AdminWithdrawListPage
from workflows.admin_portal.pages.admin_withdraw_page import AdminWithdrawPage
from workflows.admin_portal.pages.copy_trading_page import CopyTradingPage
from workflows.admin_portal.pages.leads_report_page import LeadsReportPage
from workflows.admin_portal.pages.lp_commission_log_page import LpCommissionLogPage
from workflows.admin_portal.pages.lp_execution_config_page import LpExecutionConfigPage
from workflows.admin_portal.pages.lp_transaction_page import LpTransactionPage
from workflows.admin_portal.pages.mam_page import MamPage
from workflows.admin_portal.pages.manage_leads_page import ManageLeadsPage
from workflows.admin_portal.pages.manager_management_page import ManagerManagementPage
from workflows.admin_portal.pages.manager_user_management_page import ManagerUserManagementPage
from workflows.admin_portal.pages.pamm_page import PammPage
from workflows.admin_portal.pages.private_copy_trading_page import PrivateCopyTradingPage
from workflows.admin_portal.pages.role_permission_page import RolePermissionPage
from workflows.admin_portal.pages.user_document_page import UserDocumentPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.fixture(scope="session")
def workflow_browser(
    playwright: Playwright,
    pytestconfig: pytest.Config,
) -> Generator[Browser, None, None]:
    """
    Session-scoped Playwright Browser instance for Admin Portal tests.
    Respects pytest CLI flags (--headed, --slowmo) as well as settings.
    """
    is_headed = bool(getattr(pytestconfig.option, "headed", False))
    slow_mo_val = getattr(pytestconfig.option, "slowmo", 0) or settings.browser.slow_mo

    headless = False if is_headed else settings.browser.headless

    browser = playwright.chromium.launch(
        headless=headless,
        slow_mo=slow_mo_val,
    )
    yield browser
    browser.close()


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


# =============================================================================
# ADMIN PAGE OBJECT FIXTURES
# =============================================================================

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
def copy_trading_page(authenticated_admin_page: Page) -> CopyTradingPage:
    """Provide an authenticated CopyTradingPage object."""
    return CopyTradingPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def private_copy_trading_page(authenticated_admin_page: Page) -> PrivateCopyTradingPage:
    """Provide an authenticated PrivateCopyTradingPage object."""
    return PrivateCopyTradingPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def mam_page(authenticated_admin_page: Page) -> MamPage:
    """Provide an authenticated MamPage object."""
    return MamPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def pamm_page(authenticated_admin_page: Page) -> PammPage:
    """Provide an authenticated PammPage object."""
    return PammPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def leads_report_page(authenticated_admin_page: Page) -> LeadsReportPage:
    """Provide an authenticated LeadsReportPage object."""
    return LeadsReportPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def manage_leads_page(authenticated_admin_page: Page) -> ManageLeadsPage:
    """Provide an authenticated ManageLeadsPage object."""
    return ManageLeadsPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def lp_transaction_page(authenticated_admin_page: Page) -> LpTransactionPage:
    """Provide an authenticated LpTransactionPage object."""
    return LpTransactionPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def lp_commission_log_page(authenticated_admin_page: Page) -> LpCommissionLogPage:
    """Provide an authenticated LpCommissionLogPage object."""
    return LpCommissionLogPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def lp_execution_config_page(authenticated_admin_page: Page) -> LpExecutionConfigPage:
    """Provide an authenticated LpExecutionConfigPage object."""
    return LpExecutionConfigPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def account_requests_page(authenticated_admin_page: Page) -> AccountRequestsPage:
    """Provide an authenticated AccountRequestsPage object."""
    return AccountRequestsPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def user_document_page(authenticated_admin_page: Page) -> UserDocumentPage:
    """Provide an authenticated UserDocumentPage object."""
    return UserDocumentPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def role_permission_page(authenticated_admin_page: Page) -> RolePermissionPage:
    """Provide an authenticated RolePermissionPage object."""
    return RolePermissionPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def manager_user_management_page(authenticated_admin_page: Page) -> ManagerUserManagementPage:
    """Provide an authenticated ManagerUserManagementPage object."""
    return ManagerUserManagementPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def manager_management_page(authenticated_admin_page: Page) -> ManagerManagementPage:
    """Provide an authenticated ManagerManagementPage object."""
    return ManagerManagementPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_settings_page(authenticated_admin_page: Page) -> AdminSettingsPage:
    """Provide an authenticated AdminSettingsPage object."""
    return AdminSettingsPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_cron_jobs_page(authenticated_admin_page: Page) -> AdminCronJobsPage:
    """Provide an authenticated AdminCronJobsPage object."""
    return AdminCronJobsPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_lp_execution_config_page(authenticated_admin_page: Page) -> AdminLpExecutionConfigPage:
    """Provide an authenticated AdminLpExecutionConfigPage object."""
    return AdminLpExecutionConfigPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_oxapay_page(authenticated_admin_page: Page) -> AdminOxapayPage:
    """Provide an authenticated AdminOxapayPage object."""
    return AdminOxapayPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_user_order_report_page(authenticated_admin_page: Page) -> AdminUserOrderReportPage:
    """Provide an authenticated AdminUserOrderReportPage object."""
    return AdminUserOrderReportPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_refer_report_page(authenticated_admin_page: Page) -> AdminReferReportPage:
    """Provide an authenticated AdminReferReportPage object."""
    return AdminReferReportPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_order_edit_log_page(authenticated_admin_page: Page) -> AdminOrderEditLogPage:
    """Provide an authenticated AdminOrderEditLogPage object."""
    return AdminOrderEditLogPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_user_transaction_log_page(authenticated_admin_page: Page) -> AdminUserTransactionLogPage:
    """Provide an authenticated AdminUserTransactionLogPage object."""
    return AdminUserTransactionLogPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_active_users_page(authenticated_admin_page: Page) -> AdminActiveUsersPage:
    """Provide an authenticated AdminActiveUsersPage object."""
    return AdminActiveUsersPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_user_bonus_page(authenticated_admin_page: Page) -> AdminUserBonusPage:
    """Provide an authenticated AdminUserBonusPage object."""
    return AdminUserBonusPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_symbol_configuration_page(authenticated_admin_page: Page) -> AdminSymbolConfigurationPage:
    """Provide an authenticated AdminSymbolConfigurationPage object."""
    return AdminSymbolConfigurationPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_symbol_list_page(authenticated_admin_page: Page) -> AdminSymbolListPage:
    """Provide an authenticated AdminSymbolListPage object."""
    return AdminSymbolListPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_user_group_page(authenticated_admin_page: Page) -> AdminUserGroupPage:
    """Provide an authenticated AdminUserGroupPage object."""
    return AdminUserGroupPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_deposit_page(authenticated_admin_page: Page) -> AdminDepositPage:
    """Provide an authenticated AdminDepositPage object."""
    return AdminDepositPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_withdraw_page(authenticated_admin_page: Page) -> AdminWithdrawPage:
    """Provide an authenticated AdminWithdrawPage object."""
    return AdminWithdrawPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_deposit_list_page(authenticated_admin_page: Page) -> AdminDepositListPage:
    """Provide an authenticated AdminDepositListPage object."""
    return AdminDepositListPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_withdraw_list_page(authenticated_admin_page: Page) -> AdminWithdrawListPage:
    """Provide an authenticated AdminWithdrawListPage object."""
    return AdminWithdrawListPage(authenticated_admin_page)


@pytest.fixture(scope="function")
def admin_orders_page(authenticated_admin_page: Page) -> AdminOrdersPage:
    """Provide an authenticated AdminOrdersPage object."""
    return AdminOrdersPage(authenticated_admin_page)
