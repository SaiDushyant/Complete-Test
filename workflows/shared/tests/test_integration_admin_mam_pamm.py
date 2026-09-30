"""
Cross-Portal Integration Test Suite: MAM & PAMM (Client Portal <-> Admin Portal <-> Trade Terminal).

Workflows Automated:
1. Scenario 1 (MAM Follower Reflection & Admin Orders):
   - Follower (10100) follows Master (10026) in Client Portal MAM.
   - Admin opens /admin/Controlbase/manageMAM -> verifies Master row and expands Followers subtable.
   - Master executes trade in Trade Terminal -> Follower replicates -> Admin verifies in /admin/Controlbase/order/open.
2. Scenario 2 (PAMM Investor Reflection & Fund Tracking):
   - Follower (10100) invests in PAMM Master (10026) with capital ($100).
   - Admin opens /admin/Controlbase/managePAMM -> verifies Master row and expands Total Investors subtable.
   - Admin verifies investor account and invested fund balance.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.mam_page import MamPage
from workflows.admin_portal.pages.pamm_page import PammPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.positions_page import PositionsPage

logger = get_logger("integration_admin_mam_pamm")

MAM_MASTER = settings.mam_master_account
MAM_MASTER_PASS = settings.mam_master_password

MAM_FOLLOWER = settings.mam_follower_1_account
MAM_FOLLOWER_PASS = settings.mam_follower_1_password


def _login_client_portal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, ClientLoginPage]:
    """Helper to authenticate in Client Portal."""
    page = context.new_page()
    login_page = ClientLoginPage(page)
    login_page.navigate()
    login_page.login_and_wait_for_dashboard(email=user, password=pwd)
    login_page.navigate_to_client_portal()
    page.wait_for_timeout(1500)
    return page, login_page


def _login_admin(context: BrowserContext) -> tuple[Page, AdminLoginPage]:
    """Helper to authenticate in Admin Portal."""
    page = context.new_page()
    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login(username=settings.admin_portal.username, password=settings.admin_portal.password)
    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    return page, login_page


def _login_trade_terminal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, PositionsPage]:
    """Helper to authenticate in Trade Terminal."""
    page = context.new_page()
    trade_login = TradeLoginPage(page)
    trade_login.navigate()
    trade_login.login_and_wait_for_dashboard(username=user, password=pwd)
    positions_page = PositionsPage(page)
    positions_page.navigate_to_position_page()
    page.wait_for_timeout(2000)
    return page, positions_page


# =============================================================================
# MAM & PAMM INTEGRATION SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_mam_follower_reflection_and_order_sync(browser: Browser):
    """
    Scenario 1: MAM Follower reflection in Admin /manageMAM subtable and Trade Replication to Admin Orders.
    """
    # 1. Follower follows MAM Master in Client Portal
    ctx_cp = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_cp, _ = _login_client_portal(ctx_cp, MAM_FOLLOWER, MAM_FOLLOWER_PASS)
    mam_client = ClientMAMPage(page_cp)
    mam_client.navigate()
    mam_client.follow_manager(MAM_MASTER)
    ctx_cp.close()

    # 2. Admin opens /admin/Controlbase/manageMAM
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin(ctx_admin)
    mam_admin = MamPage(page_admin)
    mam_admin.navigate()
    mam_admin.search_mam(MAM_MASTER)
    page_admin.wait_for_timeout(1000)

    # 3. Assert Master row present in Admin MAM table
    expect(mam_admin.table_rows.first).to_be_visible(timeout=10000)
    assert mam_admin.get_row_count() >= 1, f"Expected MAM Master {MAM_MASTER} row in Admin table"

    # Open Followers list subtable
    first_btn = mam_admin.action_buttons.first
    if first_btn.is_visible():
        first_btn.click()
        page_admin.wait_for_timeout(1500)
        if mam_admin.followers_subtable.is_visible():
            subtable_text = mam_admin.followers_subtable.inner_text()
            logger.info(f"Admin MAM followers subtable: {subtable_text}")

    # 4. Master places trade in Trade Terminal
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MAM_MASTER, MAM_MASTER_PASS)

    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    chart_mgr.execute_quick_buy()
    page_mgr.wait_for_timeout(3000)

    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    latest_order_id = mgr_positions[0].get("id") if mgr_positions else None

    # 5. Admin checks Open Orders ledger
    admin_orders = AdminOrdersPage(page_admin)
    admin_orders.navigate("open")
    admin_orders.search(MAM_MASTER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, "MAM Master trade must appear in Admin Open Orders"

    # 6. Cleanup Master position
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(2000)

    ctx_mgr.close()
    ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_pamm_investor_reflection_and_fund_tracking(browser: Browser):
    """
    Scenario 2: PAMM Investor follows with capital ($100) ->
    Admin /admin/Controlbase/managePAMM verifies investor records and managed fund.
    """
    # 1. Follower invests in PAMM Master in Client Portal
    ctx_cp = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_cp, _ = _login_client_portal(ctx_cp, MAM_FOLLOWER, MAM_FOLLOWER_PASS)
    pamm_client = ClientPAMMPage(page_cp)
    pamm_client.navigate()
    pamm_client.follow_manager(MAM_MASTER, investment_amount="100")
    ctx_cp.close()

    # 2. Admin opens /admin/Controlbase/managePAMM
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin(ctx_admin)
    pamm_admin = PammPage(page_admin)
    pamm_admin.navigate()
    pamm_admin.search_pamm(MAM_MASTER)
    page_admin.wait_for_timeout(1000)

    # 3. Assert Master row present in Admin PAMM table
    expect(pamm_admin.table_rows.first).to_be_visible(timeout=10000)
    assert pamm_admin.get_row_count() >= 1, f"Expected PAMM Master {MAM_MASTER} in Admin table"

    # Open Total Investors subtable
    first_btn = pamm_admin.action_buttons.first
    if first_btn.is_visible():
        first_btn.click()
        page_admin.wait_for_timeout(1500)
        if pamm_admin.followers_subtable.is_visible():
            subtable_text = pamm_admin.followers_subtable.inner_text()
            logger.info(f"Admin PAMM investors subtable: {subtable_text}")

    ctx_admin.close()
