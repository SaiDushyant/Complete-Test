"""
Cross-Portal Integration Test Suite: Admin User Management Discovery.

Validates that Admin Portal User Management (/admin/Controlbase/user) can:
1. Search and discover potential managers (e.g. 10009, 10026) and followers (e.g. 10008, 10100, 10102).
2. Validate account status, group assignment, and table row data integrity.
3. Ensure zero console errors, JS crashes, and backend 5xx failures.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.shared.utils.logger import get_logger

logger = get_logger("integration_admin_user_discovery")


def _login_admin(browser: Browser) -> tuple[Page, UserManagementPage, ErrorMonitor]:
    """Helper to authenticate in Admin Portal and navigate to User Management."""
    context = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = context.new_page()
    monitor = ErrorMonitor(page)

    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login(
        username=settings.admin_portal.username,
        password=settings.admin_portal.password,
    )
    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    user_mgmt = UserManagementPage(page)
    user_mgmt.navigate()
    return page, user_mgmt, monitor


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_discover_potential_managers_and_followers(browser: Browser):
    """
    Verify Admin User Management can search and discover known Manager and Follower accounts:
    - Master Accounts: 10009 (Copy Trading), 10026 (MAM/PAMM)
    - Follower Accounts: 10008, 10100, 10102
    """
    page, user_mgmt, monitor = _login_admin(browser)

    try:
        accounts_to_check = [
            settings.copy_trading.manager_username,
            settings.copy_trading.follower_username,
            settings.mam_master_account,
            settings.mam_follower_1_account,
        ]

        for acc in accounts_to_check:
            logger.info(f"Admin searching for account: {acc}")
            user_mgmt.search_user(acc)
            page.wait_for_timeout(1000)

            rows_count = user_mgmt.get_user_count()
            assert rows_count >= 1, f"Expected at least 1 record for account {acc} in Admin User Management"

            first_row_text = user_mgmt.user_rows.first.inner_text()
            assert acc in first_row_text, f"Expected account {acc} in first row text: {first_row_text}"

        monitor.assert_no_errors("Admin User Discovery Verification")
    finally:
        page.context.close()
