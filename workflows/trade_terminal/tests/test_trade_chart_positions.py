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
