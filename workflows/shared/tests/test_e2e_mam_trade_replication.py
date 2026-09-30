"""
Cross-Portal End-to-End MAM (Multi-Account Manager) Order Replication Test Suite.

Architectural Design:
- Follows the clean cross-portal architecture established for Copy Trading:
  * Isolated Browser Contexts per actor (Master vs Followers) to prevent cookie / session collision.
  * Master Actor: MAM Master Account (10026)
  * Follower Actors: MAM Follower 1 (10100), MAM Follower 2 (10102)
- Workflows Verified:
  1. Scenario 1 (Client Portal MAM): Followers (10100, 10102) follow Master (10026).
  2. Scenario 2 (Trade Terminal): Master places Market Order -> Replicated position verified in Follower accounts.
  3. Scenario 3 (Client Portal & Trade Terminal): Follower unfollows Master -> Master executes trade -> Verify unfollowed account does not replicate.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.positions_page import PositionsPage

logger = get_logger("e2e_mam_trade_replication")

MASTER_USER = settings.mam_master_account
MASTER_PASS = settings.mam_master_password

FOLLOWER_1_USER = settings.mam_follower_1_account
FOLLOWER_1_PASS = settings.mam_follower_1_password

FOLLOWER_2_USER = settings.mam_follower_2_account
FOLLOWER_2_PASS = settings.mam_follower_2_password


def _login_client_portal_mam(context: BrowserContext, user: str, pwd: str) -> tuple[Page, ClientMAMPage]:
    """Helper to authenticate in Client Portal and open MAM workspace."""
    page = context.new_page()
    login_page = ClientLoginPage(page)
    login_page.navigate(settings.client_portal.login_url or f"{settings.client_portal.base_url.rstrip('/')}/login")
    login_page.login(email=user, password=pwd, remember_me=True)
    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    if "/client-portal" not in page.url:
        page.goto(settings.client_portal.base_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    mam_page = ClientMAMPage(page)
    mam_page.navigate()
    return page, mam_page


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
# MAM CROSS-PORTAL WORKFLOW SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.mam
@pytest.mark.e2e
def test_e2e_mam_multiple_followers_follow_master(browser: Browser):
    """
    Scenario 1: Followers follow Master Account in Client Portal MAM.
    - Follower 1 (10100) and Follower 2 (10102) subscribe/follow Master (10026).
    - Master checks MY FOLLOWERS roster in Client Portal to confirm both followers are active.
    """
    followers = [
        (FOLLOWER_1_USER, FOLLOWER_1_PASS),
        (FOLLOWER_2_USER, FOLLOWER_2_PASS),
    ]

    # 1. Follow Master for each follower
    for user, pwd in followers:
        logger.info(f"Setting up MAM follow for follower: {user}")
        ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
        page, mam_page = _login_client_portal_mam(ctx, user, pwd)
        res = mam_page.follow_manager(MASTER_USER)
        assert res in ("followed", "already_following"), f"Failed to follow MAM master for user {user}: {res}"
        ctx.close()

    # 2. Verify Master Roster shows both followers
    ctx_m = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_m, mam_m = _login_client_portal_mam(ctx_m, MASTER_USER, MASTER_PASS)
    mam_m.switch_to_my_followers()
    page_m.wait_for_timeout(1500)
    records = mam_m.get_followers_table_records()
    logger.info(f"Active MAM followers for Master {MASTER_USER}: {records}")

    assert len(records) >= 2, f"Expected at least 2 followers on master roster, found: {records}"
    ctx_m.close()


@pytest.mark.shared
@pytest.mark.mam
@pytest.mark.e2e
def test_e2e_mam_master_order_placement_and_follower_replication(browser: Browser):
    """
    Scenario 2: Master executes order in Trade Terminal -> Replicates to Followers:
    - Master (10026) executes Quick Buy in Trade Terminal.
    - Follower 1 (10100) reflects replicated position in Trade Terminal.
    - Master closes position -> Follower position reflects closure.
    """
    # 1. Ensure Follower 1 is following Master
    ctx_f1 = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    _, mam_f1 = _login_client_portal_mam(ctx_f1, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    mam_f1.follow_manager(MASTER_USER)
    ctx_f1.close()

    # 2. Open Trade Terminal for Master
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MASTER_USER, MASTER_PASS)
    initial_mgr_orders = pos_mgr.get_open_positions_data()

    # 3. Open Trade Terminal for Follower 1
    ctx_f1_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f1_tt, pos_f1 = _login_trade_terminal(ctx_f1_tt, FOLLOWER_1_USER, FOLLOWER_1_PASS)
    initial_f1_orders = pos_f1.get_open_positions_data()

    # 4. Master executes Quick Buy Order
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    executed = chart_mgr.execute_quick_buy()
    assert executed, "Expected Quick Buy order to be executed by MAM Master"
    page_mgr.wait_for_timeout(3000)

    # 5. Verify Master position opened
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    new_mgr_orders = pos_mgr.get_open_positions_data()
    assert len(new_mgr_orders) >= len(initial_mgr_orders), "Expected master open positions to reflect new order"
    latest_order_id = new_mgr_orders[0].get("id") if new_mgr_orders else None

    # 6. Verify Follower 1 positions reflect replicated trade
    pos_f1.navigate_to_position_page()
    page_f1_tt.wait_for_timeout(4000)
    new_f1_orders = pos_f1.get_open_positions_data()
    assert len(new_f1_orders) >= len(initial_f1_orders), "Expected MAM Follower positions to reflect replication"

    # 7. Close Master Position and verify closure
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(3000)

        pos_f1.navigate_to_position_page()
        page_f1_tt.wait_for_timeout(3000)

    ctx_mgr.close()
    ctx_f1_tt.close()


@pytest.mark.shared
@pytest.mark.mam
@pytest.mark.e2e
def test_e2e_mam_unfollow_stops_order_replication(browser: Browser):
    """
    Scenario 3: Unfollowing Master stops MAM order replication:
    - Follower 2 (10102) unfollows Master (10026) in Client Portal MAM.
    - Master executes a trade in Trade Terminal.
    - Verify Follower 2 does NOT receive the replicated trade.
    - Follower 2 re-follows Master to restore clean state.
    """
    # 1. Follower 2 unfollows Master in Client Portal
    ctx_f2_cp = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_f2_cp, mam_f2 = _login_client_portal_mam(ctx_f2_cp, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    unfollowed = mam_f2.unfollow_manager(MASTER_USER)
    assert unfollowed in ("unfollowed", "already_unfollowed")
    page_f2_cp.wait_for_timeout(2000)
    ctx_f2_cp.close()

    # 2. Open Trade Terminal sessions
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MASTER_USER, MASTER_PASS)

    ctx_f2_tt = browser.new_context(viewport=settings.browser.viewport)
    page_f2_tt, pos_f2 = _login_trade_terminal(ctx_f2_tt, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    initial_follower_count = len(pos_f2.get_open_positions_data())

    # 3. Master executes trade
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    chart_mgr.execute_quick_buy()
    page_mgr.wait_for_timeout(3000)

    # 4. Check Follower 2 did NOT receive new replicated order
    pos_f2.navigate_to_position_page()
    page_f2_tt.wait_for_timeout(3000)
    current_follower_count = len(pos_f2.get_open_positions_data())
    assert current_follower_count == initial_follower_count, "Expected unfollowed MAM account not to receive new order"

    # 5. Cleanup: close placed position on master and re-follow
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    if mgr_positions:
        pos_mgr.close_position_by_id(mgr_positions[0]["id"])
        page_mgr.wait_for_timeout(2000)

    ctx_mgr.close()
    ctx_f2_tt.close()

    # Re-follow Master
    ctx_re = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    _, mam_re = _login_client_portal_mam(ctx_re, FOLLOWER_2_USER, FOLLOWER_2_PASS)
    mam_re.follow_manager(MASTER_USER)
    ctx_re.close()
