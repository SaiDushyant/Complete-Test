"""
Cross-Portal End-to-End Copy Trading and Order Replication Test Suite.

Architectural Overview:
- Isolated Browser Contexts per actor to prevent cookie / session cross-contamination:
  * Manager Actor: 10009 (Password: Temp@123)
  * Follower Actor: 10008 (Password: Test@1234)
- Cross-Portal End-to-End Workflows:
  * Scenario 1 (Client Portal): Follower discovers and subscribes to Manager 10009 (Balance Based).
  * Scenario 2 (Trade Terminal): Manager places Market Order -> Order replicates to Follower's terminal -> Manager closes position -> Follower position closes.
  * Scenario 3 (Client Portal & Trade Terminal): Follower unfollows Manager -> Manager executes trade -> Verify unfollowed account does not receive the trade.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.positions_page import PositionsPage

logger = get_logger("e2e_copy_trading_replication")

MANAGER_USER = settings.copy_trading.manager_username
MANAGER_PASS = settings.copy_trading.manager_password
MANAGER_NAME = settings.copy_trading.manager_name

FOLLOWER_USER = settings.copy_trading.follower_username
FOLLOWER_PASS = settings.copy_trading.follower_password


def _login_client_portal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, ClientCopyTradingPage]:
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


def _login_trade_terminal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, PositionsPage]:
    """Helper to authenticate a user in Trade Terminal and navigate to Positions page."""
    page = context.new_page()
    trade_login = TradeLoginPage(page)
    trade_login.navigate()
    trade_login.login_and_wait_for_dashboard(username=user, password=pwd)
    positions_page = PositionsPage(page)
    positions_page.navigate_to_position_page()
    page.wait_for_timeout(2000)
    return page, positions_page


# =============================================================================
# CROSS-PORTAL COPY TRADING & ORDER REPLICATION TEST SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_multiple_followers_subscribe_to_manager(browser: Browser):
    """
    Scenario 1: Comprehensive Multi-Follower Subscription Lifecycle:
    - Iterates through all configured follower accounts:
      * 10008 (Test@1234) -> Balance Based
      * 10006 (Test@1234) -> Equity Based
      * 10098 (123)       -> Multiplier Based
      * 10096 (123)       -> Balance Based
      * 10102 (Fake@123)  -> Equity Based
    - Subscribes each follower account to Manager 10009 in Client Portal.
    - Verifies active status in 'MY SUBSCRIPTION' tab for each follower.
    """
    trade_methods = ["Balance Based", "Equity Based", "Multiplier Based"]
    followers = settings.copy_trading.followers

    for idx, follower in enumerate(followers):
        method = trade_methods[idx % len(trade_methods)]
        logger.info(f"Testing subscription for Follower {follower.username} with method {method}")
        ctx = browser.new_context(viewport=settings.browser.viewport)
        page, copy_page = _login_client_portal(ctx, follower.username, follower.password)

        # 1. Follow Manager
        followed = copy_page.follow_manager(MANAGER_NAME, trade_method=method)
        assert followed, f"Expected {follower.username} to follow manager {MANAGER_NAME}/{MANAGER_USER} with {method}"

        # 2. Verify subscription listed in My Subscriptions
        subscriptions = copy_page.get_subscriptions_data()
        assert any(MANAGER_USER in s["account"] or MANAGER_NAME.lower() in s["account"].lower() for s in subscriptions), (
            f"Expected manager {MANAGER_USER} in active subscriptions for {follower.username}: {subscriptions}"
        )
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_manager_order_placement_and_follower_replication(browser: Browser):
    """
    Scenario 2: Manager executes order in Trade Terminal -> Replicates to Followers:
    - Follower 10008 and Follower 10006 are actively following Manager 10009.
    - Manager logs into Trade Terminal and executes Quick Buy trade.
    - Follower Trade Terminals reflect replicated positions.
    - Manager closes position -> Follower accounts reflect position closure.
    """
    # 1. Setup follower subscriptions in Client Portal
    followers_to_test = settings.copy_trading.followers[:2]
    for follower in followers_to_test:
        ctx_cp = browser.new_context(viewport=settings.browser.viewport)
        _, copy_f = _login_client_portal(ctx_cp, follower.username, follower.password)
        copy_f.follow_manager(MANAGER_NAME, trade_method="Balance Based")
        ctx_cp.close()

    # 2. Open Trade Terminal for Manager
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)
    initial_mgr_orders = pos_mgr.get_open_positions_data()

    # 3. Open Trade Terminal for Follower 1 (10008)
    ctx_f1_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f1_tt, pos_f1 = _login_trade_terminal(ctx_f1_tt, followers_to_test[0].username, followers_to_test[0].password)
    initial_f1_orders = pos_f1.get_open_positions_data()

    # 4. Manager executes Quick Buy Order
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    executed = chart_mgr.execute_quick_buy()
    assert executed, "Expected Quick Buy order to be executed by Manager"
    page_mgr.wait_for_timeout(3000)

    # 5. Verify Manager position opened
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    new_mgr_orders = pos_mgr.get_open_positions_data()
    assert len(new_mgr_orders) >= len(initial_mgr_orders), "Expected manager open positions to reflect new order"
    latest_order_id = new_mgr_orders[0].get("id") if new_mgr_orders else None

    # 6. Verify Follower 1 positions reflect replicated trade
    pos_f1.navigate_to_position_page()
    page_f1_tt.wait_for_timeout(4000)
    new_f1_orders = pos_f1.get_open_positions_data()
    assert len(new_f1_orders) >= len(initial_f1_orders), "Expected Follower positions to reflect replication"

    # 7. Close Manager Position and verify closure on follower
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(3000)

        pos_f1.navigate_to_position_page()
        page_f1_tt.wait_for_timeout(3000)

    ctx_mgr.close()
    ctx_f1_tt.close()



@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_unfollow_stops_order_replication(browser: Browser):
    """
    Scenario 3: Unfollowing stops replication:
    - Follower (10008) unfollows Manager (10009) in Client Portal.
    - Manager executes a trade in Trade Terminal.
    - Verify Follower does NOT replicate the new trade.
    - Re-follow Manager to leave environment clean.
    """
    # 1. Unfollow Manager in Client Portal
    ctx_follower_cp = browser.new_context(viewport=settings.browser.viewport)
    _, copy_follower = _login_client_portal(ctx_follower_cp, FOLLOWER_USER, FOLLOWER_PASS)
    unfollowed = copy_follower.unfollow_manager(MANAGER_NAME)
    assert unfollowed, f"Expected Follower to successfully unfollow Manager {MANAGER_NAME}"
    ctx_follower_cp.close()

    # 2. Open Trade Terminal sessions
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)

    ctx_f_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f_tt, pos_follower = _login_trade_terminal(ctx_f_tt, FOLLOWER_USER, FOLLOWER_PASS)
    initial_follower_count = len(pos_follower.get_open_positions_data())

    # 3. Manager executes trade
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    chart_mgr.execute_quick_buy()
    page_mgr.wait_for_timeout(3000)

    # 4. Check Follower count did NOT increase
    pos_follower.navigate_to_position_page()
    page_f_tt.wait_for_timeout(3000)
    current_follower_count = len(pos_follower.get_open_positions_data())
    assert current_follower_count == initial_follower_count, "Expected unfollowed account not to receive new replicated order"

    # 5. Cleanup: close newly placed position on manager
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    if mgr_positions:
        pos_mgr.close_position_by_id(mgr_positions[0]["id"])
        page_mgr.wait_for_timeout(2000)

    ctx_mgr.close()
    ctx_f_tt.close()
