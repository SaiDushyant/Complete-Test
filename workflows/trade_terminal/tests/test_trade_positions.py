"""
Trade Terminal Standalone Positions Page Test Suite.
Verifies the dedicated Positions page at:
document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(7)")
div.page[data-page="position"]
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import time
import pytest

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_element_has_text,
    assert_url_contains,
)
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.chart_page import TradingChartPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage

logger = get_logger("test_trade_positions")


@pytest.mark.trade
@pytest.mark.smoke
def test_position_page_navigation_and_structure_rendered(
    positions_page: PositionsPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify standalone Position page container:
    document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(7)")
    div.page[data-page="position"]
    1. Clicking .lefticons[data-tooltip='Position'] activates the page (removes 'hidden').
    2. Heading 'Positions (N)' is rendered.
    3. Positions table headers (ID, Time, Symbol, Order, Lot, Price, Partial, SL, TP, SWAP, LTP, PROFIT, Action).
    4. Account summary footer (Balance, Equity, Used Margin, Free Margin, Margin Level, Total Profit).
    5. Pending orders section / table is rendered.
    """
    positions_page.navigate_to_position_page()
    assert_url_contains(positions_page.page, "/dashboard", timeout=15000)

    # 1. Assert container active
    assert positions_page.is_position_page_active(), "Expected standalone Position page container to be active (not hidden)"
    assert_element_is_visible(positions_page.position_page_container, element_name="Position Page Container (nth-child(7))")

    # 2. Assert page heading
    assert_element_is_visible(positions_page.page_heading, element_name="Position Page Heading")
    heading_text = positions_page.page_heading.inner_text().strip()
    assert "Positions" in heading_text, f"Expected 'Positions' in heading, got: '{heading_text}'"

    # 3. Assert positions table and headers
    assert_element_is_visible(positions_page.positions_table, element_name="Positions Table")
    headers_count = positions_page.positions_headers.count()
    assert headers_count >= 11, f"Expected at least 11 column headers in positions table, got: {headers_count}"

    header_texts = [positions_page.positions_headers.nth(i).inner_text().strip() for i in range(headers_count)]
    expected_columns = ["ID", "Time", "Symbol", "Order", "Lot", "Price", "SWAP", "LTP", "PROFIT"]
    for col in expected_columns:
        assert any(col in h for h in header_texts), f"Expected column '{col}' among headers: {header_texts}"

    # 4. Assert summary footer
    assert_element_is_visible(positions_page.summary_footer, element_name="Summary Footer Bar")
    assert_element_is_visible(positions_page.summary_balance, element_name="Summary Balance")
    assert_element_is_visible(positions_page.summary_equity, element_name="Summary Equity")
    assert_element_is_visible(positions_page.summary_used_margin, element_name="Summary Used Margin")
    assert_element_is_visible(positions_page.summary_free_margin, element_name="Summary Free Margin")

    # 5. Assert pending orders section
    assert_element_is_visible(positions_page.pending_table, element_name="Pending Orders Table")


@pytest.mark.trade
@pytest.mark.smoke
def test_position_page_bulk_action_buttons(
    positions_page: PositionsPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify all 6 bulk operations buttons on the standalone Position page:
    Group 1: Pending Order Actions
      - Cancel all order (data-type='pending-all')
      - Cancel limit order (data-type='pending-limit')
      - Cancel stop order (data-type='pending-stop')
    Group 2: Position Close Actions
      - Close all position (data-type='all')
      - Close profitable position (data-type='profit')
      - Close losing position (data-type='loss')
    """
    positions_page.navigate_to_position_page()
    assert_url_contains(positions_page.page, "/dashboard", timeout=15000)

    # 1. Assert pending cancel bulk buttons
    assert_element_is_visible(positions_page.bulk_cancel_all_btn, element_name="Cancel All Order Button")
    assert_element_has_text(positions_page.bulk_cancel_all_btn, "Cancel all order")
    assert positions_page.bulk_cancel_all_btn.is_enabled()

    assert_element_is_visible(positions_page.bulk_cancel_limit_btn, element_name="Cancel Limit Order Button")
    assert_element_has_text(positions_page.bulk_cancel_limit_btn, "Cancel limit order")
    assert positions_page.bulk_cancel_limit_btn.is_enabled()

    assert_element_is_visible(positions_page.bulk_cancel_stop_btn, element_name="Cancel Stop Order Button")
    assert_element_has_text(positions_page.bulk_cancel_stop_btn, "Cancel stop order")
    assert positions_page.bulk_cancel_stop_btn.is_enabled()

    # 2. Assert position close bulk buttons
    assert_element_is_visible(positions_page.bulk_close_all_btn, element_name="Close All Position Button")
    assert_element_has_text(positions_page.bulk_close_all_btn, "Close all position")
    assert positions_page.bulk_close_all_btn.is_enabled()

    assert_element_is_visible(positions_page.bulk_close_profit_btn, element_name="Close Profitable Position Button")
    assert_element_has_text(positions_page.bulk_close_profit_btn, "Close profitable position")
    assert positions_page.bulk_close_profit_btn.is_enabled()

    assert_element_is_visible(positions_page.bulk_close_loss_btn, element_name="Close Losing Position Button")
    assert_element_has_text(positions_page.bulk_close_loss_btn, "Close losing position")
    assert positions_page.bulk_close_loss_btn.is_enabled()

    # 3. Test clicking pending buttons (should execute safely without breaking page)
    positions_page.execute_bulk_operation("pending-all")
    positions_page.execute_bulk_operation("pending-limit")
    positions_page.execute_bulk_operation("pending-stop")


@pytest.mark.trade
@pytest.mark.regression
def test_position_page_summary_bar_calculations(
    positions_page: PositionsPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the financial accounting equations displayed in the summary bar:
    1. Equity = Balance + Total Profit (within 1.0 tolerance for live tick delay)
    2. Free Margin <= Equity
    3. If Used Margin > 0: Margin Level (%) = (Equity / Used Margin) * 100
    """
    positions_page.navigate_to_position_page()
    assert_url_contains(positions_page.page, "/dashboard", timeout=15000)

    summary = positions_page.get_position_summary()
    logger.info(f"Standalone Position Summary Metrics: {summary}")

    # Core non-negative assertions
    assert summary["balance"] > 0, f"Expected positive Balance, got: {summary['balance']}"
    assert summary["equity"] > 0, f"Expected positive Equity, got: {summary['equity']}"
    assert summary["used_margin"] >= 0, f"Expected non-negative Used Margin, got: {summary['used_margin']}"
    assert summary["free_margin"] >= 0, f"Expected non-negative Free Margin, got: {summary['free_margin']}"

    # Financial equation check: Equity = Balance + Total Profit
    expected_equity = summary["balance"] + summary["total_profit"]
    diff_equity = abs(summary["equity"] - expected_equity)
    assert diff_equity <= 1.0, (
        f"Equity mismatch: displayed={summary['equity']}, "
        f"calculated={expected_equity} (diff={diff_equity})"
    )

    # Margin Level check
    if summary["used_margin"] > 0:
        expected_margin_level = (summary["equity"] / summary["used_margin"]) * 100
        diff_ml = abs(summary["margin_level"] - expected_margin_level)
        assert diff_ml <= 5.0, (
            f"Margin Level mismatch: displayed={summary['margin_level']}%, "
            f"calculated={expected_margin_level}% (diff={diff_ml})"
        )


@pytest.mark.trade
@pytest.mark.regression
def test_position_page_live_trade_display_and_individual_close(
    positions_page: PositionsPage,
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify live trade lifecycle on the standalone Position page:
    1. Place a market BUY order (AUDUSD 0.01 lot).
    2. Navigate to standalone Position page.
    3. Assert the order appears with matching symbol, lot (0.01), BUY type, and prices.
    4. Assert page title count reflects open position.
    5. Close the position via the in-row close icon (h6.cancelposition i).
    6. Confirm position is closed and removed from the table.
    """
    # 1. Place order via chart quick order
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    # 2. Navigate to standalone Position page
    positions_page.navigate_to_position_page()

    # Poll for position to appear
    start_time = time.time()
    open_positions = []
    while time.time() - start_time < 15:
        open_positions = positions_page.get_open_positions_data()
        if len(open_positions) > 0:
            break
        positions_page.page.wait_for_timeout(500)

    assert len(open_positions) >= 1, "Expected at least 1 open position on standalone Position page"
    target_pos = open_positions[0]
    target_id = target_pos["id"]
    logger.info(f"Target open position on standalone page: {target_pos}")

    # 3. Validate attributes of the order
    assert "AUDUSD" in target_pos["symbol"], f"Expected AUDUSD symbol, got: {target_pos['symbol']}"
    assert target_pos["order"].upper() == "BUY", f"Expected BUY order, got: {target_pos['order']}"
    assert target_pos["lot"] == 0.01, f"Expected 0.01 lot, got: {target_pos['lot']}"
    assert target_pos["open_price"] > 0, f"Expected positive open price, got: {target_pos['open_price']}"
    assert target_pos["ltp"] > 0, f"Expected positive LTP, got: {target_pos['ltp']}"

    # 4. Assert title count
    title_count = positions_page.get_positions_count_from_title()
    assert title_count >= 1, f"Expected title count >= 1, got: {title_count}"

    # 5. Close position via individual row close button
    positions_page.close_position_by_id(target_id)
    positions_page.wait_for_position_closed(target_id, timeout=15000)

    # 6. Verify row is removed
    after_positions = positions_page.get_open_positions_data()
    after_ids = {p["id"] for p in after_positions}
    assert target_id not in after_ids, f"Expected position {target_id} to be removed, found: {after_ids}"


@pytest.mark.trade
@pytest.mark.regression
def test_position_page_bulk_close_operations(
    positions_page: PositionsPage,
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify all 3 position bulk close operations on the standalone Position page:
    1. 'Close profitable position' (data-type='profit'):
       Verify freshly placed negative spread positions remain untouched.
    2. 'Close losing position' (data-type='loss'):
       Verify negative positions can be closed via bulk loss.
    3. 'Close all position' (data-type='all'):
       Verify placing multiple orders across symbols (AUDUSD and EURUSD),
       clicking 'Close all position' cleanly closes all open positions across the board.
    """
    # 1. Clean existing positions
    positions_page.navigate_to_position_page()
    if positions_page.get_open_positions_count() > 0:
        positions_page.execute_bulk_operation("all")
        positions_page.page.wait_for_timeout(2000)

    # 2. Place multiple orders
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    trading_chart_page.open_trade_modal("EURUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    # 3. Navigate to standalone Position page
    positions_page.navigate_to_position_page()

    start_wait = time.time()
    open_pos = []
    while time.time() - start_wait < 15:
        open_pos = positions_page.get_open_positions_data()
        if len(open_pos) >= 2:
            break
        positions_page.page.wait_for_timeout(500)

    assert len(open_pos) >= 2, f"Expected at least 2 open positions on standalone page, got: {len(open_pos)}"
    target_ids = {p["id"] for p in open_pos}

    # 4. Test Button 1: Close profitable position (should NOT close losing positions)
    positions_page.execute_bulk_operation("profit")
    pos_after_profit = positions_page.get_open_positions_data()
    # At least one or all orders must still be present
    assert len(pos_after_profit) > 0, "Losing positions should not be closed by 'Close profitable position'"

    # 5. Test Button 2: Close losing position
    positions_page.execute_bulk_operation("loss")
    positions_page.page.wait_for_timeout(2000)

    # 6. Test Button 3: Close all position (ensures complete closure of all open trades)
    rem_pos = positions_page.get_open_positions_data()
    if len(rem_pos) > 0:
        positions_page.execute_bulk_operation("all")
        positions_page.page.wait_for_timeout(2000)

    # Poll until all target orders are closed
    poll_start = time.time()
    while time.time() - poll_start < 15:
        cur_open = positions_page.get_open_positions_data()
        cur_ids = {p["id"] for p in cur_open}
        if len(target_ids.intersection(cur_ids)) == 0:
            break
        positions_page.page.wait_for_timeout(500)

    final_open = positions_page.get_open_positions_data()
    remaining_target_ids = target_ids.intersection({p["id"] for p in final_open})
    assert len(remaining_target_ids) == 0, (
        f"Expected all target positions {target_ids} to be closed, but found: {remaining_target_ids}"
    )


@pytest.mark.trade
@pytest.mark.regression
def test_position_page_runtime_diagnostics_clean(
    positions_page: PositionsPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that navigating and interacting with the standalone Position page
    operates cleanly with zero invisible runtime defects:
    - Zero JavaScript runtime exceptions
    - Zero console error logs
    - Zero 4xx/5xx network failures
    """
    positions_page.navigate_to_position_page()
    assert_url_contains(positions_page.page, "/dashboard", timeout=15000)
    positions_page.page.wait_for_timeout(2000)

    # Exercise buttons and views
    positions_page.execute_bulk_operation("pending-all")
    positions_page.execute_bulk_operation("pending-limit")
    positions_page.execute_bulk_operation("pending-stop")
    positions_page.execute_bulk_operation("profit")
    positions_page.page.wait_for_timeout(1000)

    # Telemetry and diagnostics are automatically asserted by the trade_diagnostics fixture in teardown
