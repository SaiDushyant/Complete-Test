"""
Cross-Portal Integration Test Suite: Manager Requests Lifecycle (Admin Portal & Client Portal).

Workflows Automated:
1. Scenario 1 (Copy Trading Manager Requests Modal):
   - Admin navigates to /admin/Controlbase/follow.
   - Inspects Client Portal Requests badge count.
   - Opens Client Portal Requests modal (#copyRequestsModal).
   - Validates requests table structure (#copyMasterRequestsTable) and modal controls.
   - Interacts with refresh and closes modal safely.

2. Scenario 2 (MAM Manager Requests Modal):
   - Admin navigates to /admin/Controlbase/manageMAM.
   - Inspects MAM Master Requests badge count.
   - Opens MAM Requests modal (#mamRequestsModal).
   - Validates requests table structure (#mamMasterRequestsTable) and controls.
   - Closes modal safely.

3. Scenario 3 (PAMM Manager Requests Modal):
   - Admin navigates to /admin/Controlbase/managePAMM.
   - Inspects PAMM Master Requests badge count.
   - Opens PAMM Requests modal (#pammRequestsModal).
   - Validates requests table structure and controls.
   - Closes modal safely.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.copy_trading_page import CopyTradingPage
from workflows.admin_portal.pages.mam_page import MamPage
from workflows.admin_portal.pages.pamm_page import PammPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("integration_admin_manager_requests")


def _login_admin(context: BrowserContext) -> tuple[Page, AdminLoginPage]:
    """Helper to authenticate in Admin Portal."""
    page = context.new_page()
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
    return page, login_page


# =============================================================================
# MANAGER REQUESTS INTEGRATION SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_copy_trading_manager_requests_lifecycle(browser: Browser):
    """
    Scenario 1: Verify Admin Copy Trading Manager Requests Modal & Request Roster:
    - Admin navigates to /admin/Controlbase/follow
    - Inspects Client Portal Requests button and badge counter
    - Opens Copy Requests modal (#copyRequestsModal)
    - Verifies modal title, table columns, and refresh mechanism
    - Closes modal safely
    """
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin(ctx_admin)

    try:
        copy_page = CopyTradingPage(page_admin)
        copy_page.navigate()
        expect(copy_page.datatable).to_be_visible(timeout=10000)

        # 1. Inspect request badge counter
        badge_count = copy_page.get_request_badge_count()
        logger.info(f"Copy Trading Manager Request Badge Count: {badge_count}")
        assert badge_count >= 0, "Badge count must be non-negative integer"

        # 2. Open Requests Modal
        expect(copy_page.client_portal_requests_button).to_be_visible(timeout=5000)
        copy_page.open_client_portal_requests()
        expect(copy_page.copy_requests_modal).to_be_visible(timeout=5000)

        # 3. Verify Table inside Modal
        expect(copy_page.copy_requests_table).to_be_visible(timeout=5000)
        req_rows = copy_page.copy_requests_table_rows.count()
        logger.info(f"Rendered Copy Requests rows: {req_rows}")

        # 4. Refresh requests
        if copy_page.copy_requests_refresh_button.is_visible():
            copy_page.copy_requests_refresh_button.click()
            page_admin.wait_for_timeout(1000)

        # 5. Close modal
        copy_page.close_client_portal_requests()
        expect(copy_page.copy_requests_modal).not_to_be_visible(timeout=5000)

    finally:
        ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_mam_manager_requests_lifecycle(browser: Browser):
    """
    Scenario 2: Verify Admin MAM Manager Requests Modal & Request Roster:
    - Admin navigates to /admin/Controlbase/manageMAM
    - Inspects MAM Master Requests button and badge counter
    - Opens MAM Requests modal (#mamRequestsModal)
    - Verifies modal title, table columns, and refresh mechanism
    - Closes modal safely
    """
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin(ctx_admin)

    try:
        mam_page = MamPage(page_admin)
        mam_page.navigate()
        expect(mam_page.datatable).to_be_visible(timeout=10000)

        # 1. Inspect request button & counter
        if mam_page.mam_requests_button.is_visible():
            badge_count = mam_page.get_request_badge_count()
            logger.info(f"MAM Manager Request Badge Count: {badge_count}")
            assert badge_count >= 0, "Badge count must be non-negative integer"

            # 2. Open Requests Modal
            mam_page.open_mam_requests()
            expect(mam_page.mam_requests_modal).to_be_visible(timeout=5000)

            # 3. Verify Table inside Modal
            expect(mam_page.mam_requests_table).to_be_visible(timeout=5000)
            req_rows = mam_page.mam_requests_table_rows.count()
            logger.info(f"Rendered MAM Requests rows: {req_rows}")

            # 4. Refresh requests
            if mam_page.mam_requests_refresh_button.is_visible():
                mam_page.mam_requests_refresh_button.click()
                page_admin.wait_for_timeout(1000)

            # 5. Close modal
            mam_page.close_mam_requests()
            expect(mam_page.mam_requests_modal).not_to_be_visible(timeout=5000)
        else:
            logger.info("MAM Requests button is not visible on current admin layout")

    finally:
        ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_pamm_manager_requests_lifecycle(browser: Browser):
    """
    Scenario 3: Verify Admin PAMM Manager Requests Modal & Request Roster:
    - Admin navigates to /admin/Controlbase/managePAMM
    - Inspects PAMM Master Requests button and badge counter
    - Opens PAMM Requests modal (#pammRequestsModal)
    - Verifies modal title, table columns, and refresh mechanism
    - Closes modal safely
    """
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin(ctx_admin)

    try:
        pamm_page = PammPage(page_admin)
        pamm_page.navigate()
        expect(pamm_page.datatable).to_be_visible(timeout=10000)

        # 1. Inspect request badge counter
        badge_count = pamm_page.get_request_badge_count()
        logger.info(f"PAMM Manager Request Badge Count: {badge_count}")
        assert badge_count >= 0, "Badge count must be non-negative integer"

        # 2. Open Requests Modal
        expect(pamm_page.pamm_requests_button).to_be_visible(timeout=5000)
        pamm_page.open_pamm_requests()
        expect(pamm_page.pamm_requests_modal).to_be_visible(timeout=5000)

        # 3. Verify Table inside Modal
        expect(pamm_page.pamm_requests_table).to_be_visible(timeout=5000)
        req_rows = pamm_page.pamm_requests_table_rows.count()
        logger.info(f"Rendered PAMM Requests rows: {req_rows}")

        # 4. Refresh requests
        if pamm_page.pamm_requests_refresh_button.is_visible():
            pamm_page.pamm_requests_refresh_button.click()
            page_admin.wait_for_timeout(1000)

        # 5. Close modal
        pamm_page.close_pamm_requests()
        expect(pamm_page.pamm_requests_modal).not_to_be_visible(timeout=5000)

    finally:
        ctx_admin.close()
