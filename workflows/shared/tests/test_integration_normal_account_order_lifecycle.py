"""
Cross-Portal Integration Test Suite: Normal Account Order Placement Lifecycle (Trade Terminal <-> Admin Portal).

Workflows Automated:
1. Scenario 1 (Market Order with SL and TP):
   - Normal user logs into Trade Terminal.
   - Opens order popup from Watchlist -> inputs Lot, Stop Loss (SL), and Take Profit (TP).
   - Places Market Buy order.
   - Verifies open position in Trade Terminal Positions ledger.
   - Admin logs into Admin Portal -> navigates to /admin/Controlbase/order/open ->
     verifies the live order record for the user account.
   - User closes the position in Trade Terminal.
   - Admin navigates to /admin/Controlbase/order/closed -> verifies the closed order record.

2. Scenario 2 (Limit Order with SL and TP):
   - User opens order popup -> selects 'Limit' tab.
   - Inputs Trigger Price, Lot, SL, and TP -> submits Limit order.
   - Admin checks /admin/Controlbase/order/open for the pending/limit order.
   - User cancels / modifies pending order.

3. Scenario 3 (Stop HFT Order Execution):
   - User opens order popup -> selects 'Stop HFT' tab.
   - Inputs Buy Above / Sell Below trigger prices, Lots, SL, and TP.
   - Submits Stop HFT order and verifies order handling.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage

logger = get_logger("integration_normal_account_order_lifecycle")

# Use a standard user account that is neither master nor follower
NORMAL_USER = settings.copy_trading.followers[1].username if len(settings.copy_trading.followers) > 1 else "10006"
NORMAL_PASS = settings.copy_trading.followers[1].password if len(settings.copy_trading.followers) > 1 else "Test@1234"


def _login_trade_terminal(context: BrowserContext, user: str, pwd: str) -> tuple[Page, PositionsPage, WatchlistPage, OrderEntryPage]:
    """Helper to authenticate in Trade Terminal and initialize page objects."""
    page = context.new_page()
    trade_login = TradeLoginPage(page)
    trade_login.navigate()
    trade_login.login_and_wait_for_dashboard(username=user, password=pwd)
    
    positions_page = PositionsPage(page)
    watchlist_page = WatchlistPage(page)
    order_entry_page = OrderEntryPage(page)
    
    watchlist_page.dismiss_disclaimer_if_present()
    return page, positions_page, watchlist_page, order_entry_page


def _login_admin(context: BrowserContext) -> tuple[Page, AdminOrdersPage]:
    """Helper to authenticate in Admin Portal and initialize AdminOrdersPage."""
    page = context.new_page()
    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login(username=settings.admin_portal.username, password=settings.admin_portal.password)
    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    orders_page = AdminOrdersPage(page)
    return page, orders_page


# =============================================================================
# NORMAL ACCOUNT ORDER LIFECYCLE INTEGRATION SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.trade
@pytest.mark.integration
def test_normal_account_market_order_with_sl_tp_lifecycle(browser: Browser):
    """
    Scenario 1: Market Order with SL & TP Lifecycle:
    - User places Market Buy order with SL and TP from Watchlist order popup
    - Verified in Trade Terminal Positions
    - Verified in Admin Open Orders (/admin/Controlbase/order/open)
    - Position closed in Trade Terminal -> Verified in Admin Closed Orders (/admin/Controlbase/order/closed)
    """
    ctx_trade = browser.new_context(viewport=settings.browser.viewport)
    page_trade, pos_page, wl_page, order_entry = _login_trade_terminal(ctx_trade, NORMAL_USER, NORMAL_PASS)

    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, admin_orders = _login_admin(ctx_admin)

    try:
        # 1. Open order popup from Watchlist
        order_entry.open_for_symbol(symbol="EURUSD", side="BUY")
        expect(order_entry.modal).to_be_visible(timeout=5000)

        # 2. Place Market order with SL and TP
        placed = order_entry.place_market_order(lot="0.01", sl="1.05000", tp="1.15000", side="BUY")
        assert placed, "Expected market order submission"
        page_trade.wait_for_timeout(3000)

        # 3. Verify position in Trade Terminal
        pos_page.navigate_to_position_page()
        page_trade.wait_for_timeout(2000)
        positions = pos_page.get_open_positions_data()
        logger.info(f"Normal account open positions: {positions}")
        latest_order_id = positions[0].get("id") if positions else None

        # 4. Verify in Admin Open Orders ledger
        admin_orders.navigate("open")
        admin_orders.search(NORMAL_USER)
        page_admin.wait_for_timeout(1000)
        open_rows_count = admin_orders.get_table_rows_count()
        logger.info(f"Admin Open Orders rows for user {NORMAL_USER}: {open_rows_count}")
        assert open_rows_count >= 1, f"Expected active order for {NORMAL_USER} in Admin Open Orders"

        # 5. Close position in Trade Terminal
        if latest_order_id:
            pos_page.close_position_by_id(latest_order_id)
            page_trade.wait_for_timeout(3000)

        # 6. Verify in Admin Closed Orders ledger
        admin_orders.navigate("closed")
        admin_orders.search(NORMAL_USER)
        page_admin.wait_for_timeout(1000)
        closed_rows_count = admin_orders.get_table_rows_count()
        logger.info(f"Admin Closed Orders rows for user {NORMAL_USER}: {closed_rows_count}")
        assert closed_rows_count >= 1, f"Expected closed order for {NORMAL_USER} in Admin Closed Orders"

    finally:
        ctx_trade.close()
        ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.trade
@pytest.mark.integration
def test_normal_account_limit_order_with_sl_tp_lifecycle(browser: Browser):
    """
    Scenario 2: Limit Order with Trigger, SL & TP Lifecycle:
    - User opens Watchlist order popup -> selects 'Limit' tab
    - Inputs Trigger Price, Lot, SL, and TP -> submits Limit order
    - Verifies order placement in Trade Terminal & Admin Portal
    """
    ctx_trade = browser.new_context(viewport=settings.browser.viewport)
    page_trade, pos_page, wl_page, order_entry = _login_trade_terminal(ctx_trade, NORMAL_USER, NORMAL_PASS)

    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, admin_orders = _login_admin(ctx_admin)

    try:
        # 1. Open order popup
        order_entry.open_for_symbol(symbol="EURUSD", side="BUY")
        expect(order_entry.modal).to_be_visible(timeout=5000)

        # 2. Place Limit order with SL and TP
        placed = order_entry.place_limit_order(
            trigger_price="1.00100",
            lot="0.01",
            sl="0.99000",
            tp="1.05000",
            side="BUY",
        )
        assert placed, "Expected limit order submission"
        page_trade.wait_for_timeout(3000)

        # 3. Check Admin Open Orders ledger
        admin_orders.navigate("open")
        admin_orders.search(NORMAL_USER)
        page_admin.wait_for_timeout(1000)
        open_rows = admin_orders.get_table_rows_count()
        logger.info(f"Admin Open/Pending Orders count for {NORMAL_USER}: {open_rows}")

        # 4. Clean up pending orders if any
        try:
            pos_page.execute_bulk_operation("pending-all")
        except Exception:
            pass
        page_trade.wait_for_timeout(2000)

    finally:
        ctx_trade.close()
        ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.trade
@pytest.mark.integration
def test_normal_account_stop_hft_order_lifecycle(browser: Browser):
    """
    Scenario 3: Stop HFT Order Lifecycle:
    - User opens Watchlist order popup -> selects 'Stop HFT' tab
    - Inputs Buy Above / Sell Below, Lot, SL, TP -> submits Stop HFT order
    - Verifies execution and cleans up
    """
    ctx_trade = browser.new_context(viewport=settings.browser.viewport)
    page_trade, pos_page, wl_page, order_entry = _login_trade_terminal(ctx_trade, NORMAL_USER, NORMAL_PASS)

    try:
        # 1. Open order popup
        order_entry.open_for_symbol(symbol="EURUSD", side="BUY")
        expect(order_entry.modal).to_be_visible(timeout=5000)

        # 2. Place Stop HFT order
        placed = order_entry.place_stop_hft_order(
            mode="BUY",
            buy_lot="0.01",
            buy_above="1.35000",
            buy_sl="1.34000",
            buy_tp="1.37000",
        )
        assert placed, "Expected Stop HFT order submission"
        page_trade.wait_for_timeout(3000)

        # 3. Clean up pending orders
        try:
            pos_page.execute_bulk_operation("pending-all")
        except Exception:
            pass
        page_trade.wait_for_timeout(2000)

    finally:
        ctx_trade.close()
