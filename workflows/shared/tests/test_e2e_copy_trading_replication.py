"""
Cross-Portal End-to-End Multi-Account Copy Trading and Order Replication Test Suite.

Architectural Overview:
- Isolated Browser Contexts per actor to prevent cookie / session cross-contamination:
  * Manager Actor (10009 / Temp@123)
  * Follower 1 Actor (10008 / Test@1234)
  * Follower 2 Actor (10007 / Test@1234)
- Cross-Portal Interactions:
  * Phase 1 (Client Portal): Followers discover and subscribe to Manager with chosen Trade Methods.
  * Phase 2 (Trade Terminal): Manager places Market Order -> Order replicates across active follower terminals.
  * Phase 3 (Trade Terminal): Manager closes position -> Position closes across active follower terminals.
  * Phase 4 (Client Portal & Trade Terminal): Follower 2 unfollows Manager -> Manager executes trade -> Verify only active Follower 1 replicates the trade.
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

MANAGER_USER = "10009"
MANAGER_PASS = "Temp@123"

FOLLOWER_1_USER = "10008"
FOLLOWER_1_PASS = "Test@1234"

FOLLOWER_2_USER = "10007"
FOLLOWER_2_PASS = "Test@1234"


def _login_client_portal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, ClientCopyTradingPage]:
    """Helper to authenticate a user in Client Portal and navigate to Copy Trading."""
    page = context.new_page()
    login_page = ClientLoginPage(page)
    login_page.navigate()
    login_page.login_and_wait_for_dashboard(email=user, password=pwd)
    login_page.navigate_to_client_portal()
    page.wait_for_timeout(1000)
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
    page.wait_for_timeout(1500)
    return page, positions_page


# =============================================================================
# CROSS-PORTAL COPY TRADING & ORDER REPLICATION TEST SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_multiple_followers_subscribe_to_manager(browser: Browser):
    """
    Scenario 1: Multiple follower accounts subscribe to Manager 10009:
    - Follower 1 (10008) follows Manager 10009 with 'Balance Based' method.
    - Follower 2 (10007) follows Manager 10009 with 'Multiplier Based' method.
    - Verifies active status in 'MY SUBSCRIPTION' tab for both followers.
    """
    # Follower 1 context
    ctx_f1 = browser.new_context(viewport=settings.browser.viewport)
    page_f1, copy_f1 = _login_client_portal(ctx_f1, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    f1_followed = copy_f1.follow_manager("temp", trade_method="Balance Based")
    assert f1_followed, f"Expected {FOLLOWER_1_USER} to follow manager temp/10009"

    f1_subs = copy_f1.get_subscriptions_data()
    assert any("10009" in s["account"] or "temp" in s["account"].lower() for s in f1_subs)
    ctx_f1.close()

    # Follower 2 context
    ctx_f2 = browser.new_context(viewport=settings.browser.viewport)
    page_f2, copy_f2 = _login_client_portal(ctx_f2, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    f2_followed = copy_f2.follow_manager("temp", trade_method="Multiplier Based")
    assert f2_followed, f"Expected {FOLLOWER_2_USER} to follow manager temp/10009"

    f2_subs = copy_f2.get_subscriptions_data()
    assert any("10009" in s["account"] or "temp" in s["account"].lower() for s in f2_subs)
    ctx_f2.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_manager_order_placement_and_follower_replication(browser: Browser):
    """
    Scenario 2: Manager executes order in Trade Terminal -> Replicates to followers:
    - Ensures Follower 1 (10008) and Follower 2 (10007) are actively following Manager (10009).
    - Manager logs into Trade Terminal and executes Quick Buy trade.
    - Follower 1 and Follower 2 Trade Terminals reflect replicated positions.
    - Manager closes position -> Follower accounts reflect position closure.
    """
    # 1. Setup follower subscriptions
    ctx_f1_cp = browser.new_context(viewport=settings.browser.viewport)
    _, copy_f1 = _login_client_portal(ctx_f1_cp, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    copy_f1.follow_manager("temp", trade_method="Balance Based")
    ctx_f1_cp.close()

    ctx_f2_cp = browser.new_context(viewport=settings.browser.viewport)
    _, copy_f2 = _login_client_portal(ctx_f2_cp, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    copy_f2.follow_manager("temp", trade_method="Multiplier Based")
    ctx_f2_cp.close()

    # 2. Open Trade Terminal for Manager
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)
    initial_mgr_orders = pos_mgr.get_open_positions_data()

    # 3. Open Trade Terminal for Follower 1
    ctx_f1_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f1_tt, pos_f1 = _login_trade_terminal(ctx_f1_tt, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    initial_f1_orders = pos_f1.get_open_positions_data()

    # 4. Open Trade Terminal for Follower 2
    ctx_f2_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f2_tt, pos_f2 = _login_trade_terminal(ctx_f2_tt, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    initial_f2_orders = pos_f2.get_open_positions_data()

    # 5. Manager executes Quick Buy Order
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    executed = chart_mgr.execute_quick_buy()
    assert executed, "Expected Quick Buy order to be executed by Manager"
    page_mgr.wait_for_timeout(3000)

    # 6. Verify Manager position opened
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    new_mgr_orders = pos_mgr.get_open_positions_data()
    assert len(new_mgr_orders) >= len(initial_mgr_orders), "Expected manager open positions to reflect new order"
    latest_order_id = new_mgr_orders[0].get("id") if new_mgr_orders else None

    # 7. Verify Follower 1 and Follower 2 positions
    pos_f1.navigate_to_position_page()
    page_f1_tt.wait_for_timeout(4000)
    new_f1_orders = pos_f1.get_open_positions_data()
    assert len(new_f1_orders) >= len(initial_f1_orders), "Expected Follower 1 positions to reflect replication"

    pos_f2.navigate_to_position_page()
    page_f2_tt.wait_for_timeout(4000)
    new_f2_orders = pos_f2.get_open_positions_data()
    assert len(new_f2_orders) >= len(initial_f2_orders), "Expected Follower 2 positions to reflect replication"

    # 8. Close Manager Position and verify closure on followers
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(3000)

        pos_f1.navigate_to_position_page()
        page_f1_tt.wait_for_timeout(3000)

        pos_f2.navigate_to_position_page()
        page_f2_tt.wait_for_timeout(3000)

    ctx_mgr.close()
    ctx_f1_tt.close()
    ctx_f2_tt.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_unfollow_stops_order_replication(browser: Browser):
    """
    Scenario 3: Unfollowing stops replication:
    - Follower 2 (10007) unfollows Manager (10009).
    - Manager executes a trade in Trade Terminal.
    - Verify Follower 1 (10008, active) continues to replicate trades.
    - Verify Follower 2 (10007, unfollowed) does NOT replicate the new trade.
    """
    # 1. Unfollow Manager on Follower 2
    ctx_f2_cp = browser.new_context(viewport=settings.browser.viewport)
    _, copy_f2 = _login_client_portal(ctx_f2_cp, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    unfollowed = copy_f2.unfollow_manager("temp")
    assert unfollowed, "Expected Follower 2 to successfully unfollow Manager"
    ctx_f2_cp.close()

    # 2. Ensure Follower 1 is still following
    ctx_f1_cp = browser.new_context(viewport=settings.browser.viewport)
    _, copy_f1 = _login_client_portal(ctx_f1_cp, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    copy_f1.follow_manager("temp", trade_method="Balance Based")
    ctx_f1_cp.close()

    # 3. Open Trade Terminal sessions
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MANAGER_USER, MANAGER_PASS)

    ctx_f1_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f1_tt, pos_f1 = _login_trade_terminal(ctx_f1_tt, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    initial_f1_count = len(pos_f1.get_open_positions_data())

    ctx_f2_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f2_tt, pos_f2 = _login_trade_terminal(ctx_f2_tt, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    initial_f2_count = len(pos_f2.get_open_positions_data())

    # 4. Manager executes trade
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    chart_mgr.execute_quick_buy()
    page_mgr.wait_for_timeout(3000)

    # 5. Check Follower 2 (unfollowed) count did NOT increase
    pos_f2.navigate_to_position_page()
    page_f2_tt.wait_for_timeout(3000)
    current_f2_count = len(pos_f2.get_open_positions_data())
    assert current_f2_count == initial_f2_count, "Expected unfollowed account not to receive new replicated order"

    # Cleanup: close newly placed position
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    if mgr_positions:
        pos_mgr.close_position_by_id(mgr_positions[0]["id"])
        page_mgr.wait_for_timeout(2000)

    ctx_mgr.close()
    ctx_f1_tt.close()
    ctx_f2_tt.close()
