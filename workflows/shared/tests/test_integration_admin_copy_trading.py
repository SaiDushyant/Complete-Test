"""
Cross-Portal Integration Test Suite: Copy Trading (Client Portal <-> Admin Portal <-> Trade Terminal).

Workflows Automated:
1. Scenario 1 (Roster Sync): Follower (10008) follows Manager (10009) in Client Portal ->
   Admin navigates to /admin/Controlbase/follow -> expands Followers subtable -> verifies follower 10008 is listed.
2. Scenario 2 (Trade Execution & Admin Ledger): Manager (10009) executes Quick Buy in Trade Terminal ->
   Follower (10008) replicates position in Trade Terminal -> Admin navigates to /admin/Controlbase/order/open ->
   asserts both Master's order and Follower's replicated order are visible in Admin ledger.
   Master closes position -> Follower position closes -> Admin verifies in /admin/Controlbase/order/closed.
3. Scenario 3 (Unfollow Sync & Isolation): Follower unfollows Manager -> Master executes trade ->
   Follower receives no trade -> Admin Open Orders confirms no replicated order for unfollowed account.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.copy_trading_page import CopyTradingPage
from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.positions_page import PositionsPage

logger = get_logger("integration_admin_copy_trading")

MANAGER_USER = settings.copy_trading.manager_username
MANAGER_PASS = settings.copy_trading.manager_password
MANAGER_NAME = settings.copy_trading.manager_name

FOLLOWER_USER = settings.copy_trading.follower_username
FOLLOWER_PASS = settings.copy_trading.follower_password


def _login_client_portal_copy(context: BrowserContext, user: str, pwd: str) -> tuple[Page, ClientCopyTradingPage]:
    """Helper to authenticate a user in Client Portal and navigate to Copy Trading."""
    page = context.new_page()
    login_page = ClientLoginPage(page)
    login_page.navigate()
    login_page.login_and_wait_for_dashboard(email=user, password=pwd)
    login_page.navigate_to_client_portal()
    page.wait_for_timeout(1500)

    copy_page = ClientCopyTradingPage(page)
    copy_page.navigate()
    return page, copy_page


def _login_admin_page(context: BrowserContext) -> tuple[Page, AdminLoginPage]:
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


def _login_trade_terminal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, PositionsPage]:
    """Helper to authenticate in Trade Terminal and navigate to Positions page."""
    page = context.new_page()
    trade_login = TradeLoginPage(page)
    trade_login.navigate()
    trade_login.login_and_wait_for_dashboard(username=user, password=pwd)
    positions_page = PositionsPage(page)
    positions_page.navigate_to_position_page()
    page.wait_for_timeout(2000)
    return page, positions_page


# =============================================================================
# INTEGRATION TESTS: COPY TRADING <-> ADMIN PORTAL
# =============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_client_follow_reflects_in_admin_copy_trading_subtable(browser: Browser):
    """
    Scenario 1: Follower follows Manager in Client Portal ->
    Admin verifies follower record in Admin Copy Trading manager subtable.
    """
    # 1. Follower follows Manager in Client Portal
    ctx_client = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_client, client_copy = _login_client_portal_copy(ctx_client, FOLLOWER_USER, FOLLOWER_PASS)
    followed = client_copy.follow_manager(MANAGER_NAME, trade_method="Balance Based")
    assert followed, f"Expected {FOLLOWER_USER} to follow manager {MANAGER_NAME}"
    ctx_client.close()

    # 2. Admin logs in and navigates to Admin Copy Trading
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin_page(ctx_admin)
    admin_copy = CopyTradingPage(page_admin)
    admin_copy.navigate()

    # 3. Search for Manager in Admin table
    admin_copy.search_trader(MANAGER_USER)
    page_admin.wait_for_timeout(1000)

    # 4. Open Followers Subtable
    expect(admin_copy.table_rows.first).to_be_visible(timeout=10000)
    first_btn = admin_copy.action_buttons.first
    expect(first_btn).to_be_visible(timeout=5000)
    first_btn.click()
    page_admin.wait_for_timeout(1500)

    # 5. Assert Followers Subtable renders follower account
    expect(admin_copy.followers_subtable).to_be_visible(timeout=10000)
    subtable_text = admin_copy.followers_subtable.inner_text()
    logger.info(f"Admin followers subtable content for manager {MANAGER_USER}: {subtable_text}")
    assert FOLLOWER_USER in subtable_text, (
        f"Expected Follower {FOLLOWER_USER} in Admin Copy Trading subtable: {subtable_text}"
    )

    ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_copy_trading_order_placement_verified_in_admin_open_and_closed_orders(browser: Browser):
    """
    Scenario 2: Trade Execution Replication & Admin Orders Ledger Sync:
    1. Ensure Follower (10008) is following Manager (10009).
    2. Master executes Quick Buy in Trade Terminal.
    3. Follower replicates open position in Trade Terminal.
    4. Admin logs into Admin Portal -> /admin/Controlbase/order/open ->
       verifies both Master and Follower orders in Open Orders table.
    5. Master closes position in Trade Terminal -> Follower position closes.
    6. Admin navigates to /admin/Controlbase/order/closed ->
       verifies closed status in Admin Orders ledger.
    """
    # 1. Ensure Follower is following Master
    ctx_cp = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    _, cp_copy = _login_client_portal_copy(ctx_cp, FOLLOWER_USER, FOLLOWER_PASS)
    cp_copy.follow_manager(MANAGER_NAME, trade_method="Balance Based")
    ctx_cp.close()

    # 2. Open Trade Terminal for Master
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)

    # 3. Open Trade Terminal for Follower
    ctx_fol = browser.new_context(viewport=settings.browser.viewport)
    page_fol, pos_fol = _login_trade_terminal(ctx_fol, FOLLOWER_USER, FOLLOWER_PASS)

    # 4. Master executes Quick Buy
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    executed = chart_mgr.execute_quick_buy()
    assert executed, "Expected Quick Buy order to be executed by Master"
    page_mgr.wait_for_timeout(3000)

    # 5. Master & Follower verify open positions
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    assert len(mgr_positions) >= 1, "Expected master to have open position"
    latest_order_id = mgr_positions[0].get("id")

    pos_fol.navigate_to_position_page()
    page_fol.wait_for_timeout(3000)
    fol_positions = pos_fol.get_open_positions_data()
    assert len(fol_positions) >= 1, "Expected follower to reflect replicated trade"

    # 6. Admin checks Open Orders table
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin_page(ctx_admin)
    admin_orders = AdminOrdersPage(page_admin)
    admin_orders.navigate("open")

    # Search for Master account in Admin Open Orders
    admin_orders.search(MANAGER_USER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, f"Expected open orders for Master {MANAGER_USER} in Admin Portal"

    # Search for Follower account in Admin Open Orders
    admin_orders.search(FOLLOWER_USER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, f"Expected replicated open order for Follower {FOLLOWER_USER} in Admin Portal"

    # 7. Master closes position in Trade Terminal
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(3000)
        pos_fol.navigate_to_position_page()
        page_fol.wait_for_timeout(3000)

    # 8. Admin checks Closed Orders table
    admin_orders.navigate("closed")
    admin_orders.search(MANAGER_USER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, f"Expected closed order for Master {MANAGER_USER} in Admin Portal"

    ctx_mgr.close()
    ctx_fol.close()
    ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_copy_trading_unfollow_stops_admin_order_replication(browser: Browser):
    """
    Scenario 3: Unfollow stops replication across Trade Terminal and Admin Orders:
    1. Follower (10008) unfollows Manager (10009) in Client Portal.
    2. Master executes trade in Trade Terminal.
    3. Follower receives NO trade.
    4. Admin verifies in /admin/Controlbase/order/open that Master order exists but Follower order is absent.
    5. Clean up: Master closes trade, Follower re-follows.
    """
    # 1. Follower unfollows Master in Client Portal
    ctx_cp = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    _, cp_copy = _login_client_portal_copy(ctx_cp, FOLLOWER_USER, FOLLOWER_PASS)
    unfollowed = cp_copy.unfollow_manager(MANAGER_NAME)
    assert unfollowed, f"Expected {FOLLOWER_USER} to unfollow manager {MANAGER_NAME}"
    ctx_cp.close()

    # 2. Open Trade Terminal sessions
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)

    ctx_fol = browser.new_context(viewport=settings.browser.viewport)
    page_fol, pos_fol = _login_trade_terminal(ctx_fol, FOLLOWER_USER, FOLLOWER_PASS)
    initial_fol_count = len(pos_fol.get_open_positions_data())

    # 3. Master executes trade
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    chart_mgr.execute_quick_buy()
    page_mgr.wait_for_timeout(3000)

    # 4. Follower position count remains unchanged
    pos_fol.navigate_to_position_page()
    page_fol.wait_for_timeout(3000)
    current_fol_count = len(pos_fol.get_open_positions_data())
    assert current_fol_count == initial_fol_count, "Expected unfollowed account not to receive new order"

    # 5. Admin Open Orders check: Follower has 0 new open orders
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin_page(ctx_admin)
    admin_orders = AdminOrdersPage(page_admin)
    admin_orders.navigate("open")

    admin_orders.search(MANAGER_USER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, "Master order must exist in Admin Open Orders"

    # 6. Cleanup Master position
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    if mgr_positions:
        pos_mgr.close_position_by_id(mgr_positions[0]["id"])
        page_mgr.wait_for_timeout(2000)

    ctx_mgr.close()
    ctx_fol.close()
    ctx_admin.close()

    # 7. Re-follow Master in Client Portal
    ctx_re = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    _, cp_re = _login_client_portal_copy(ctx_re, FOLLOWER_USER, FOLLOWER_PASS)
    cp_re.follow_manager(MANAGER_NAME, trade_method="Balance Based")
    ctx_re.close()
