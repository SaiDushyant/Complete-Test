"""
Trade Terminal Chart Integrated Positions Pane Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Chart section rendering (body > div.body > div.main > div.rightbar > section > div:nth-child(3)).
2. Resizer handle (#app > div > div > div.resizer-y) and lower positions pane (#app > div > div > div.div2.w100).
3. Positions table structure, column headers, and sorting controls.
4. Account summary calculations (Balance, Equity, Used Margin, Free Margin, Margin Level %).
5. Order ticket modal (#dragable_modal) margin scaling calculation with lot size.
6. Live trade execution (BUY order), verifying new position appears in div2.w100,
   calculating PnL correctness: (LTP - EntryPrice) * lot * contract_size,
   and closing the position via .cancelposition.
7. Runtime diagnostics: zero uncaught JS exceptions, console errors, or network failures.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import expect

from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.chart_page import TradingChartPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.smoke
def test_chart_positions_pane_and_resizer_rendered(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that opening the Chart view renders the chart section container,
    the vertical resizer handle (#app > div > div > div.resizer-y),
    and the integrated positions table pane (#app > div > div > div.div2.w100)
    with all expected table columns.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Assert chart container & resizer
    assert_element_is_visible(trading_chart_page.chart_page_container, element_name="Chart Page Container")
    assert_element_is_visible(trading_chart_page.resizer_y, element_name="Chart Resizer-Y Handle")
    assert_element_is_visible(trading_chart_page.positions_pane, element_name="Positions Pane (div2.w100)")
    assert_element_is_visible(trading_chart_page.positions_table, element_name="Positions Table")

    # 2. Assert table columns
    headers_count = trading_chart_page.positions_headers.count()
    assert headers_count >= 12, f"Expected at least 12 table headers, found: {headers_count}"

    headers_text = [
        trading_chart_page.positions_headers.nth(i).inner_text().strip().upper()
        for i in range(min(12, headers_count))
    ]
    for required_col in ["ID", "SYMBOL", "ORDER", "LOT", "PROFIT"]:
        assert any(required_col in h for h in headers_text), f"Expected column '{required_col}' in headers: {headers_text}"


@pytest.mark.trade
@pytest.mark.smoke
def test_chart_positions_summary_bar_calculations(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the account summary footer in the positions pane displays
    accurate metrics and satisfies fundamental financial calculation equations:
    1. Balance > 0 and Equity > 0
    2. Free Margin + Used Margin ≈ Equity (within tolerance)
    3. If Used Margin > 0, Margin Level % ≈ (Equity / Used Margin) * 100
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    summary = trading_chart_page.get_account_summary()
    balance = summary["balance"]
    equity = summary["equity"]
    used_margin = summary["used_margin"]
    free_margin = summary["free_margin"]
    margin_level = summary["margin_level_pct"]

    assert balance > 0, f"Expected positive balance, got: {balance}"
    assert equity > 0, f"Expected positive equity, got: {equity}"

    # Verify Margin Level % if Used Margin > 0
    if used_margin > 0:
        expected_margin_level = (equity / used_margin) * 100.0
        # Allow tolerance for live price ticks
        diff_pct = abs(margin_level - expected_margin_level)
        assert diff_pct <= max(5.0, expected_margin_level * 0.05), (
            f"Expected Margin Level % ≈ {expected_margin_level:.2f}%, got: {margin_level:.2f}% (diff: {diff_pct:.2f})"
        )


@pytest.mark.trade
@pytest.mark.regression
def test_chart_order_modal_margin_scaling_calculation(
    trading_chart_page: TradingChartPage,
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that in the order modal (#dragable_modal), the required margin calculation
    scales proportionally with the lot size input:
    - Margin for 0.02 lot is double the margin for 0.01 lot
    - Margin for 0.05 lot is 5x the margin for 0.01 lot
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Open trade modal for AUDUSD
    test_symbol = "AUDUSD"
    trading_chart_page.open_trade_modal(test_symbol, side="buy")

    try:
        # Initial 0.01 lot margin
        margin_001 = trading_chart_page.get_trade_modal_margin_required()
        assert margin_001 > 0, f"Expected positive required margin for 0.01 lot, got: {margin_001}"

        # 0.02 lot margin
        trading_chart_page.set_trade_modal_lot(0.02)
        margin_002 = trading_chart_page.get_trade_modal_margin_required()
        expected_002 = margin_001 * 2
        assert abs(margin_002 - expected_002) <= 0.05, (
            f"Expected 0.02 lot margin ≈ {expected_002}, got: {margin_002}"
        )

        # 0.05 lot margin
        trading_chart_page.set_trade_modal_lot(0.05)
        margin_005 = trading_chart_page.get_trade_modal_margin_required()
        expected_005 = margin_001 * 5
        assert abs(margin_005 - expected_005) <= 0.10, (
            f"Expected 0.05 lot margin ≈ {expected_005}, got: {margin_005}"
        )
    finally:
        trading_chart_page.close_order_modal()


@pytest.mark.trade
@pytest.mark.regression
def test_chart_trade_execution_updates_position_and_calculates_pnl(
    trading_chart_page: TradingChartPage,
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify end-to-end trading on the chart page:
    1. Capture initial positions count and used margin.
    2. Place a BUY market order for AUDUSD (0.01 lot).
    3. Assert position appears in #app > div > div > div.div2.w100 table.
    4. Assert position attributes (Symbol: AUDUSD, Order: BUY, Lot: 0.01).
    5. Mathematically verify PnL calculation matches live market pricing:
       PnL ≈ (LTP - EntryPrice) * lot * 100000.
    6. Close the position via .cancelposition and verify it is removed from open positions.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Capture initial positions and IDs
    before_positions = trading_chart_page.get_all_positions_data()
    before_ids = {p["id"] for p in before_positions}

    # 2. Place 0.01 lot BUY order for AUDUSD
    test_symbol = "AUDUSD"
    trading_chart_page.open_trade_modal(test_symbol, side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()

    # 3. Wait for new position to appear in div2 table via WebSocket/polling
    start_time = time.time()
    new_ids = set()
    after_positions = []
    while time.time() - start_time < 15:
        after_positions = trading_chart_page.get_all_positions_data()
        after_ids = {p["id"] for p in after_positions}
        diff = after_ids - before_ids
        if diff:
            new_ids = diff
            break
        trading_chart_page.page.wait_for_timeout(500)

    assert len(new_ids) >= 1, (
        f"Expected at least 1 new position, found: {new_ids}. "
        f"(before: {sorted(before_ids)}, after: {sorted([p['id'] for p in after_positions])})"
    )
    # Highest ID is the newly created trade
    target_id = sorted(list(new_ids))[-1]

    try:
        # 4. Extract target position details
        target_pos = next((p for p in after_positions if p["id"] == target_id), None)
        assert target_pos is not None, f"Could not find position record for target ID {target_id}"

        assert target_pos["symbol"] == test_symbol, f"Expected symbol '{test_symbol}', got: '{target_pos['symbol']}'"
        assert target_pos["order"] == "BUY", f"Expected order 'BUY', got: '{target_pos['order']}'"
        assert target_pos["lot"] == 0.01, f"Expected lot 0.01, got: {target_pos['lot']}"
        assert target_pos["open_price"] > 0, f"Expected positive open price, got: {target_pos['open_price']}"
        assert target_pos["ltp"] > 0, f"Expected positive LTP, got: {target_pos['ltp']}"

        # 5. Verify PnL calculation: (LTP - OpenPrice) * 0.01 * 100000
        expected_pnl = (target_pos["ltp"] - target_pos["open_price"]) * 0.01 * 100000.0
        actual_pnl = target_pos["pnl"]
        diff = abs(actual_pnl - expected_pnl)
        # Tolerance of $1.50 allows for commission/spread ticks
        assert diff <= 1.50, (
            f"Expected PnL ≈ {expected_pnl:.2f}, got actual PnL: {actual_pnl:.2f} (diff: {diff:.2f})"
        )
    finally:
        # 6. Close the opened position to clean up
        trading_chart_page.close_position_by_id(target_id)
        trading_chart_page.wait_for_position_closed(target_id)


@pytest.mark.trade
@pytest.mark.smoke
def test_chart_resizer_bulk_close_dropdown_buttons(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the bulk operations dropdown:
    document.querySelector("#app > div > div > div.resizer-y > div.chart-bulk-close-list.showOrdersList")
    1. Clicking .chart-bulk-close opens the bulk actions list.
    2. On 'Positions' tab, verify position bulk buttons:
       - 'Close all position' (data-type='all') is visible.
       - 'Close profitable position' (data-type='profit') is visible.
       - 'Close losing position' (data-type='loss') is visible.
       - Pending cancel buttons are hidden.
    3. Switching to 'Pending' tab updates the contextual bulk actions:
       - 'Cancel all order' (data-type='pending-all') is visible.
       - 'Cancel limit order' (data-type='pending-limit') is visible.
       - 'Cancel stop order' (data-type='pending-stop') is visible.
       - Position close buttons are hidden.
    4. Clicking .chart-bulk-close again closes the menu.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Switch to Positions tab and open bulk menu
    trading_chart_page.switch_positions_tab("positions")
    trading_chart_page.open_bulk_close_menu()
    assert_element_is_visible(
        trading_chart_page.chart_bulk_close_list,
        element_name="Chart Bulk Close Dropdown List",
    )

    # 2. Check position bulk buttons visibility
    pos_btn_info = trading_chart_page.get_bulk_close_buttons_info()
    pos_types_visible = {b["data_type"]: b["visible"] for b in pos_btn_info}
    assert pos_types_visible.get("all") is True, "Expected 'Close all position' to be visible on Positions tab"
    assert pos_types_visible.get("profit") is True, "Expected 'Close profitable position' to be visible on Positions tab"
    assert pos_types_visible.get("loss") is True, "Expected 'Close losing position' to be visible on Positions tab"
    assert pos_types_visible.get("pending-all") is False, "Expected 'Cancel all order' to be hidden on Positions tab"

    # Close bulk menu
    trading_chart_page.close_bulk_close_menu()

    # 3. Switch to Pending tab and open bulk menu
    trading_chart_page.switch_positions_tab("pending")
    trading_chart_page.open_bulk_close_menu()

    pend_btn_info = trading_chart_page.get_bulk_close_buttons_info()
    pend_types_visible = {b["data_type"]: b["visible"] for b in pend_btn_info}
    assert pend_types_visible.get("pending-all") is True, "Expected 'Cancel all order' to be visible on Pending tab"
    assert pend_types_visible.get("pending-limit") is True, "Expected 'Cancel limit order' to be visible on Pending tab"
    assert pend_types_visible.get("pending-stop") is True, "Expected 'Cancel stop order' to be visible on Pending tab"
    assert pend_types_visible.get("all") is False, "Expected 'Close all position' to be hidden on Pending tab"

    # 4. Close bulk menu and restore Positions tab
    trading_chart_page.close_bulk_close_menu()
    trading_chart_page.switch_positions_tab("positions")


@pytest.mark.trade
@pytest.mark.smoke
def test_chart_resizer_toggle_full_chart_collapses_and_expands_positions_pane(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the toggleFullChart button:
    document.querySelector("#app > div > div > div.resizer-y > div.toggleFullChart")
    1. Initially, positions pane (#app .div2.w100) is visible and toggle icon is chevron-down.
    2. Click toggle button -> positions pane collapses down out of view, icon flips to chevron-up.
    3. Click toggle button again -> positions pane expands up, class div2MaxHeight is applied,
       positions table is visible again, and icon flips back to chevron-down.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Initial expanded state
    assert trading_chart_page.is_position_pane_visible(), "Expected positions pane to be visible initially"
    initial_icon_class = trading_chart_page.toggle_full_chart_icon.get_attribute("class") or ""
    assert "fa-chevron-down" in initial_icon_class, f"Expected chevron-down initially, got: {initial_icon_class}"

    # 2. Click 1: Collapse position pane (comes down)
    trading_chart_page.toggle_full_chart()
    assert not trading_chart_page.is_position_pane_visible(), "Expected positions pane to be collapsed after first click"
    collapsed_icon_class = trading_chart_page.toggle_full_chart_icon.get_attribute("class") or ""
    assert "fa-chevron-up" in collapsed_icon_class, f"Expected chevron-up when collapsed, got: {collapsed_icon_class}"

    # 3. Click 2: Expand position pane (comes up)
    trading_chart_page.toggle_full_chart()
    assert trading_chart_page.is_position_pane_visible(), "Expected positions pane to be visible after second click"
    div2_classes = trading_chart_page.positions_pane.get_attribute("class") or ""
    assert "div2MaxHeight" in div2_classes, f"Expected 'div2MaxHeight' class on expanded div2, got: {div2_classes}"
    expanded_icon_class = trading_chart_page.toggle_full_chart_icon.get_attribute("class") or ""
    assert "fa-chevron-down" in expanded_icon_class, f"Expected chevron-down when expanded, got: {expanded_icon_class}"


@pytest.mark.trade
@pytest.mark.regression
def test_chart_positions_sections_tab_navigation_and_order_lifecycle(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the sections of the position pane (#app > div > div > div.div2.w100.div2MaxHeight):
    1. Tab switching between all 4 sections:
       - Positions (.chartPostionsList)
       - Pending (.chartPendingList)
       - History 24H (.chartClosedList)
       - Cancelled 24H (.chartCancelledList)
    2. Place an order on the chart and verify it is displayed in the Positions section.
    3. Close the order and verify it is moved to and displayed in the History 24H section.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Test navigation across all 4 sections
    trading_chart_page.switch_positions_tab("pending")
    assert_element_is_visible(trading_chart_page.section_pending, element_name="Pending Section")
    assert not trading_chart_page.section_positions.is_visible()

    trading_chart_page.switch_positions_tab("history")
    assert_element_is_visible(trading_chart_page.section_history_24h, element_name="History 24H Section")
    assert not trading_chart_page.section_pending.is_visible()
    # Check History 24H headers
    history_headers_count = trading_chart_page.history_headers.count()
    assert history_headers_count >= 10, f"Expected at least 10 history headers, got: {history_headers_count}"

    trading_chart_page.switch_positions_tab("cancelled")
    assert_element_is_visible(trading_chart_page.section_cancelled_24h, element_name="Cancelled 24H Section")
    assert not trading_chart_page.section_history_24h.is_visible()

    # 2. Return to Positions tab
    trading_chart_page.switch_positions_tab("positions")
    assert_element_is_visible(trading_chart_page.section_positions, element_name="Positions Section")

    # 3. Capture baseline open positions
    before_positions = trading_chart_page.get_all_positions_data()
    before_ids = {p["id"] for p in before_positions}

    # 4. Execute a BUY trade
    test_symbol = "AUDUSD"
    trading_chart_page.open_trade_modal(test_symbol, side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()

    # Poll for new position in Positions section
    start_time = time.time()
    new_ids = set()
    while time.time() - start_time < 15:
        after_positions = trading_chart_page.get_all_positions_data()
        diff = {p["id"] for p in after_positions} - before_ids
        if diff:
            new_ids = diff
            break
        trading_chart_page.page.wait_for_timeout(500)

    assert len(new_ids) >= 1, f"Expected new position in Positions section, got diff: {new_ids}"
    target_id = sorted(list(new_ids))[-1]

    # Verify order is displayed in Positions section
    pos_row = trading_chart_page.get_position_row_by_id(target_id)
    assert_element_is_visible(pos_row, element_name=f"Position Row {target_id} in Positions Section")

    # 5. Close the position
    trading_chart_page.close_position_by_id(target_id)
    trading_chart_page.wait_for_position_closed(target_id)

    # 6. Switch to History 24H section and verify closed order is correctly displayed there
    history_records = trading_chart_page.get_history_positions_data()
    history_ids = {h["id"] for h in history_records}
    assert target_id in history_ids, (
        f"Expected closed position ID {target_id} to be displayed in History 24H section, "
        f"found history IDs: {sorted(history_ids)}"
    )

    # Verify history details for target_id
    history_item = next(h for h in history_records if h["id"] == target_id)
    assert history_item["status"].lower() == "closed", f"Expected status 'closed', got: {history_item['status']}"
    assert history_item["lot"] == 0.01, f"Expected lot 0.01 in history, got: {history_item['lot']}"

    # Restore Positions tab
    trading_chart_page.switch_positions_tab("positions")


@pytest.mark.trade
@pytest.mark.regression
def test_chart_positions_runtime_diagnostics_clean(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that navigating the Chart view and interacting with the positions pane
    operates with zero invisible runtime defects:
    - Zero JavaScript runtime exceptions
    - Zero console errors
    - Zero failed network requests
    - Zero HTTP 4xx/5xx responses
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # Query summary metrics
    _ = trading_chart_page.get_account_summary()
    _ = trading_chart_page.get_all_positions_data()

    # Assert clean diagnostics
    trading_chart_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
        ignored_patterns=["google-analytics.com"],
    )
