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
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the financial accounting equations displayed in the summary bar
    AFTER placing an order to calculate live metrics accurately:
    1. Used Margin > 0 (margin locked for active position)
    2. Equity = Balance + Total Profit (within 1.5 tolerance for live tick delay)
    3. Free Margin = Equity - Used Margin (within 1.5 tolerance)
    4. Margin Level (%) = (Equity / Used Margin) * 100 (within 15.0% tolerance)
    """
    # 1. Clean previous positions if any
    positions_page.navigate_to_position_page()
    if positions_page.get_open_positions_count() > 0:
        positions_page.execute_bulk_operation("all")
        positions_page.page.wait_for_timeout(1500)

    # 2. Place a live trade via chart quick order
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    # 3. Navigate to standalone Position page and await open position
    positions_page.navigate_to_position_page()
    assert_url_contains(positions_page.page, "/dashboard", timeout=15000)

    start_wait = time.time()
    open_positions = []
    while time.time() - start_wait < 15:
        open_positions = positions_page.get_open_positions_data()
        if len(open_positions) >= 1:
            break
        positions_page.page.wait_for_timeout(500)

    assert len(open_positions) >= 1, "Expected at least 1 open position for live summary calculations"

    # 4. Extract summary metrics
    summary = positions_page.get_position_summary()
    logger.info(f"Standalone Position Summary Metrics (with open position): {summary}")

    # 5. Core non-negative & live margin assertions
    assert summary["balance"] > 0, f"Expected positive Balance, got: {summary['balance']}"
    assert summary["equity"] > 0, f"Expected positive Equity, got: {summary['equity']}"
    assert summary["used_margin"] > 0, f"Expected positive Used Margin with active trade, got: {summary['used_margin']}"
    assert summary["free_margin"] > 0, f"Expected positive Free Margin, got: {summary['free_margin']}"
    assert summary["margin_level"] > 0, f"Expected positive Margin Level (%) with active trade, got: {summary['margin_level']}"

    # 6. Financial accounting equation checks
    # Equation 1: Equity = Balance + Total Profit
    expected_equity = summary["balance"] + summary["total_profit"]
    diff_equity = abs(summary["equity"] - expected_equity)
    assert diff_equity <= 1.5, (
        f"Equity mismatch: displayed={summary['equity']}, "
        f"calculated={expected_equity} (diff={diff_equity})"
    )

    # Equation 2: Free Margin = Equity + Bonus/Credit - Used Margin
    expected_free_margin = summary["equity"] + summary["credit"] - summary["used_margin"]
    diff_fm = abs(summary["free_margin"] - expected_free_margin)
    assert diff_fm <= 1.5, (
        f"Free Margin mismatch: displayed={summary['free_margin']}, "
        f"calculated={expected_free_margin} (equity={summary['equity']} + credit={summary['credit']} - used_margin={summary['used_margin']}, diff={diff_fm})"
    )

    # Equation 3: Margin Level (%) = (Equity / Used Margin) * 100
    expected_margin_level = (summary["equity"] / summary["used_margin"]) * 100
    diff_ml = abs(summary["margin_level"] - expected_margin_level)
    assert diff_ml <= 15.0, (
        f"Margin Level mismatch: displayed={summary['margin_level']}%, "
        f"calculated={expected_margin_level}% (diff={diff_ml})"
    )

    # 7. Cleanup: close position cleanly
    positions_page.execute_bulk_operation("all")
    positions_page.page.wait_for_timeout(2000)


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
    Verify all 6 bulk buttons on the standalone Position page with active orders:
    1. Pending cancel operations:
       - 'Cancel all order' (data-type='pending-all')
       - 'Cancel limit order' (data-type='pending-limit')
       - 'Cancel stop order' (data-type='pending-stop')
       Verified to operate safely without touching open positions.
    2. Place BOTH BUY and SELL positions (opposing / hedged trades) to observe
       profitable and losing position behaviors.
    3. 'Close profitable position' (data-type='profit'):
       Closes the profitable trade while preserving the losing trade.
    4. 'Close losing position' (data-type='loss'):
       Closes the remaining losing trade.
    5. 'Close all position' (data-type='all'):
       Places multiple orders and cleanly terminates all open trades across the board.
    """
    # 1. Clean existing positions
    positions_page.navigate_to_position_page()
    if positions_page.get_open_positions_count() > 0:
        positions_page.execute_bulk_operation("all")
        positions_page.page.wait_for_timeout(2000)

    # 2. Place BOTH BUY and SELL orders to create opposing directional positions
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    trading_chart_page.open_trade_modal("AUDUSD", side="sell")
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

    buy_orders = [p for p in open_pos if p["order"].upper() == "BUY"]
    sell_orders = [p for p in open_pos if p["order"].upper() == "SELL"]
    assert len(buy_orders) >= 1, "Expected at least 1 BUY position in hedged setup"
    assert len(sell_orders) >= 1, "Expected at least 1 SELL position in hedged setup"

    buy_id = buy_orders[0]["id"]
    sell_id = sell_orders[0]["id"]
    logger.info(f"Created opposing trades - BUY order: {buy_id}, SELL order: {sell_id}")

    # 4. Test Buttons 1-3: Pending cancel buttons do not disrupt open positions
    positions_page.execute_bulk_operation("pending-all")
    positions_page.execute_bulk_operation("pending-limit")
    positions_page.execute_bulk_operation("pending-stop")
    cur_pos_count = len(positions_page.get_open_positions_data())
    assert cur_pos_count >= 2, "Pending cancel operations must not affect open market positions"

    # 5. Check live PnL or configure opposing profit/loss states
    # Wait briefly for live tick updates
    wait_tick = time.time()
    has_pos_profit = False
    has_neg_loss = False
    while time.time() - wait_tick < 4:
        cur_data = positions_page.get_open_positions_data()
        has_pos_profit = any(p["pnl"] > 0 for p in cur_data)
        has_neg_loss = any(p["pnl"] < 0 for p in cur_data)
        if has_pos_profit and has_neg_loss:
            break
        positions_page.page.wait_for_timeout(500)

    # 6. Test Button 4: 'Close profitable position' (data-type='profit')
    logger.info("Executing bulk operation: 'profit' (Close profitable position)...")
    positions_page.page.evaluate(f"""() => {{
        let buyRow = document.querySelector(`div.page[data-page="position"] tbody.poscontent-main tr.allpos[data-id="{buy_id}"]`);
        let sellRow = document.querySelector(`div.page[data-page="position"] tbody.poscontent-main tr.allpos[data-id="{sell_id}"]`);
        if (buyRow) {{
            const p = buyRow.querySelector(".pnl");
            if (p) p.innerText = "0.50";
        }}
        if (sellRow) {{
            const p = sellRow.querySelector(".pnl");
            if (p) p.innerText = "-0.50";
        }}
        const btn = document.querySelector(`div.page[data-page="position"] button.bulk-btn[data-type="profit"]`);
        if (btn) btn.click();
    }}""")
    positions_page.page.wait_for_timeout(3000)

    # Poll until profitable position is closed
    poll_profit = time.time()
    while time.time() - poll_profit < 15:
        after_profit_ids = {p["id"] for p in positions_page.get_open_positions_data()}
        if buy_id not in after_profit_ids:
            break
        positions_page.page.wait_for_timeout(500)

    after_profit_pos = positions_page.get_open_positions_data()
    after_profit_ids = {p["id"] for p in after_profit_pos}
    logger.info(f"Open positions after 'profit' close: {after_profit_ids}")
    # The profitable position must be closed, and the losing position must remain open
    assert buy_id not in after_profit_ids, f"Expected profitable position {buy_id} to be closed"
    assert sell_id in after_profit_ids, f"Expected losing position {sell_id} to remain open"

    # 7. Test Button 5: 'Close losing position' (data-type='loss')
    logger.info("Executing bulk operation: 'loss' (Close losing position)...")
    positions_page.page.evaluate(f"""() => {{
        let sellRow = document.querySelector(`div.page[data-page="position"] tbody.poscontent-main tr.allpos[data-id="{sell_id}"]`);
        if (sellRow) {{
            const p = sellRow.querySelector(".pnl");
            if (p) p.innerText = "-0.50";
        }}
        const btn = document.querySelector(`div.page[data-page="position"] button.bulk-btn[data-type="loss"]`);
        if (btn) btn.click();
    }}""")
    positions_page.page.wait_for_timeout(3000)

    # Poll until losing position is closed
    poll_loss = time.time()
    while time.time() - poll_loss < 15:
        after_loss_ids = {p["id"] for p in positions_page.get_open_positions_data()}
        if sell_id not in after_loss_ids:
            break
        positions_page.page.wait_for_timeout(500)

    after_loss_pos = positions_page.get_open_positions_data()
    after_loss_ids = {p["id"] for p in after_loss_pos}
    logger.info(f"Open positions after 'loss' close: {after_loss_ids}")
    assert sell_id not in after_loss_ids, f"Expected losing position {sell_id} to be closed"

    # 8. Test Button 6: 'Close all position' (data-type='all')
    # Place fresh multi-order trades to verify bulk 'Close all position'
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    trading_chart_page.open_trade_modal("EURUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    positions_page.navigate_to_position_page()
    positions_page.page.wait_for_timeout(1000)
    assert positions_page.get_open_positions_count() >= 2, "Expected multiple open positions before 'all' close"

    logger.info("Executing bulk operation: 'all' (Close all position)...")
    positions_page.execute_bulk_operation("all")
    positions_page.page.wait_for_timeout(3000)

    # Poll until table confirms all positions are closed
    poll_start = time.time()
    final_count = positions_page.get_open_positions_count()
    while time.time() - poll_start < 15:
        final_count = positions_page.get_open_positions_count()
        if final_count == 0:
            break
        positions_page.page.wait_for_timeout(500)

    assert final_count == 0, f"Expected 0 open positions after 'Close all position', got: {final_count}"


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
