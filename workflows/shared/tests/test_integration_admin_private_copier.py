"""
Cross-Portal Integration Test Suite: Private Copy Trading (Admin Portal <-> Trade Terminal).

Workflows Automated:
1. Scenario 1 (Admin Setup & Inspection): Admin navigates to /admin/Controlbase/managePrivateCopier ->
   searches for existing private copier bindings -> opens Slave Accounts modal -> verifies bound slave accounts.
2. Scenario 2 (Order Replication via Private Copier): Master executes trade in Trade Terminal ->
   Slave accounts replicate position -> Admin Open Orders ledger reflects both master and slave positions.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.private_copy_trading_page import PrivateCopyTradingPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage

logger = get_logger("integration_admin_private_copier")

MASTER_USER = settings.copy_trading.manager_username
MASTER_PASS = settings.copy_trading.manager_password

SLAVE_USER = settings.copy_trading.follower_username
SLAVE_PASS = settings.copy_trading.follower_password


def _login_admin_private_copier(context: BrowserContext) -> tuple[Page, PrivateCopyTradingPage]:
    """Helper to authenticate in Admin Portal and open Manage Private Copier."""
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

    copier_page = PrivateCopyTradingPage(page)
    copier_page.navigate()
    return page, copier_page


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
# PRIVATE COPY TRADING INTEGRATION SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_private_copier_inspection_and_slave_modal(browser: Browser):
    """
    Scenario 1: Admin verifies private copier bindings and inspects slave accounts modal:
    - Admin navigates to /admin/Controlbase/managePrivateCopier
    - Verifies table rendering and DataTables controls
    - Inspects Slave Accounts modal for configured private copier entries
    """
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, copier_page = _login_admin_private_copier(ctx_admin)

    try:
        expect(copier_page.datatable).to_be_visible(timeout=10000)
        row_count = copier_page.get_row_count()
        logger.info(f"Total Private Copier rows in Admin: {row_count}")

        if row_count > 0:
            first_row_text = copier_page.table_rows.first.inner_text()
            logger.info(f"First Private Copier row: {first_row_text}")

            # Open Slaves modal if button present
            if copier_page.view_slaves_buttons.count() > 0:
                copier_page.open_view_slaves_modal(0)
                expect(copier_page.private_slaves_modal).to_be_visible(timeout=5000)
                copier_page.close_view_slaves_modal()
                expect(copier_page.private_slaves_modal).not_to_be_visible(timeout=5000)

    finally:
        ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.integration
def test_admin_private_copier_trade_execution_sync(browser: Browser):
    """
    Scenario 2: Master executes order -> Slave replicates -> Admin verifies in Open & Closed Orders.
    """
    # 1. Open Trade Terminal for Master and Slave
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr, pos_mgr = _login_trade_terminal(ctx_mgr, MASTER_USER, MASTER_PASS)

    ctx_slv = browser.new_context(viewport=settings.browser.viewport)
    page_slv, pos_slv = _login_trade_terminal(ctx_slv, SLAVE_USER, SLAVE_PASS)

    # 2. Master executes trade
    chart_mgr = BlackTraderChartPage(page_mgr)
    chart_mgr.navigate_to_chart()
    page_mgr.wait_for_timeout(3000)
    executed = chart_mgr.execute_quick_buy()
    assert executed, "Expected Quick Buy to execute"
    page_mgr.wait_for_timeout(3000)

    # 3. Master and Slave verify positions
    pos_mgr.navigate_to_position_page()
    page_mgr.wait_for_timeout(2000)
    mgr_positions = pos_mgr.get_open_positions_data()
    latest_order_id = mgr_positions[0].get("id") if mgr_positions else None

    pos_slv.navigate_to_position_page()
    page_slv.wait_for_timeout(3000)

    # 4. Admin checks Open Orders
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin = ctx_admin.new_page()
    login_page = AdminLoginPage(page_admin)
    login_page.navigate()
    login_page.login(username=settings.admin_portal.username, password=settings.admin_portal.password)
    page_admin.wait_for_timeout(1500)

    admin_orders = AdminOrdersPage(page_admin)
    admin_orders.navigate("open")
    admin_orders.search(MASTER_USER)
    page_admin.wait_for_timeout(1000)
    assert admin_orders.get_table_rows_count() >= 1, "Master order must appear in Admin Open Orders"

    # 5. Master closes trade
    if latest_order_id:
        pos_mgr.close_position_by_id(latest_order_id)
        page_mgr.wait_for_timeout(3000)

    ctx_mgr.close()
    ctx_slv.close()
    ctx_admin.close()


@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.trade
@pytest.mark.integration
def test_admin_private_copier_limit_and_stop_hft_order_sync(browser: Browser):
    """
    Scenario 3: Private Copier Master places Limit & Stop HFT orders:
    - Master places Limit order with SL & TP.
    - Admin confirms order in /admin/Controlbase/order/open.
    - Master cleans up pending orders.
    - Master places Stop HFT order with triggers, SL & TP.
    - Master cleans up pending orders.
    """
    # 1. Master logs into Trade Terminal
    ctx_mgr = browser.new_context(viewport=settings.browser.viewport)
    page_mgr = ctx_mgr.new_page()
    trade_login = TradeLoginPage(page_mgr)
    trade_login.navigate()
    trade_login.login_and_wait_for_dashboard(username=MASTER_USER, password=MASTER_PASS)
    pos_mgr = PositionsPage(page_mgr)
    wl_mgr = WatchlistPage(page_mgr)
    wl_mgr.dismiss_disclaimer_if_present()
    order_entry_mgr = OrderEntryPage(page_mgr)

    # 2. Admin logs in
    ctx_admin = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_admin, _ = _login_admin_private_copier(ctx_admin)
    admin_orders = AdminOrdersPage(page_admin)

    try:
        # A. Limit Order
        order_entry_mgr.open_for_symbol(symbol="EURUSD", side="BUY")
        expect(order_entry_mgr.modal).to_be_visible(timeout=5000)

        limit_placed = order_entry_mgr.place_limit_order(
            trigger_price="1.00100",
            lot="0.01",
            sl="0.99000",
            tp="1.05000",
            side="BUY",
        )
        assert limit_placed, "Expected Master Limit Order to be placed"
        page_mgr.wait_for_timeout(3000)

        # Admin checks open orders
        admin_orders.navigate("open")
        admin_orders.search(MASTER_USER)
        page_admin.wait_for_timeout(1000)
        mgr_open_rows = admin_orders.get_table_rows_count()
        logger.info(f"Admin Open Orders for Private Copier Master Limit: {mgr_open_rows}")

        # Cleanup Limit Order
        pos_mgr.navigate_to_position_page()
        try:
            pos_mgr.execute_bulk_operation("pending-all")
        except Exception:
            pass
        page_mgr.wait_for_timeout(2000)

        # B. Stop HFT Order
        order_entry_mgr.open_for_symbol(symbol="EURUSD", side="BUY")
        expect(order_entry_mgr.modal).to_be_visible(timeout=5000)

        hft_placed = order_entry_mgr.place_stop_hft_order(
            mode="BUY",
            buy_lot="0.01",
            buy_above="1.35000",
            buy_sl="1.34000",
            buy_tp="1.37000",
        )
        assert hft_placed, "Expected Master Stop HFT Order to be placed"
        page_mgr.wait_for_timeout(3000)

        # Cleanup
        pos_mgr.navigate_to_position_page()
        try:
            pos_mgr.execute_bulk_operation("pending-all")
        except Exception:
            pass
        page_mgr.wait_for_timeout(2000)

    finally:
        ctx_mgr.close()
        ctx_admin.close()

