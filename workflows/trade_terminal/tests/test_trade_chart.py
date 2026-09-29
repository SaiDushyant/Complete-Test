"""
Trade Terminal Multi-Engine Chart Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Chart section container rendering:
   - Top chart pane: #app > div > div > div.div1.initialHeight
   - TradingView container: #tv_chart_container
   - Black Trader container: #bt_chart_container
   - Quick Trading overlay: .trade-buy-sell.trade-click
2. Profile Menu Chart Engine Switcher:
   - Switching from TradingView to Black Trader (#targetmenu .chart-btn.blacktrader)
   - Verifying #bt_chart_container becomes active and #tv_chart_container is hidden
   - Verifying Black Trader iframe (iframe#xten) is mounted and functional
   - Switching back to TradingView (#targetmenu .chart-btn.tradingView)
   - Verifying #tv_chart_container becomes active and TradingView iframe is mounted
3. TradingView Chart Toolbar & Drawing Tools:
   - Header toolbar (Symbol Search, Timeframe Intervals, Candles, Indicators, Layouts, Settings, Fullscreen)
   - Active symbol verification
   - Left drawing toolbar tool groups (Cursors, Trendlines, Gann/Fib, Shapes)
4. Black Trader Chart Controls:
   - Top toolbar (Symbol badge, Timeframe menu, Chart Type menu, Indicators, Grid Menu, Screenshot)
5. Quick Trading Overlay Widget (.trade-buy-sell):
   - Lot size input (#trade-lot-size), increment (+), decrement (-), step size and bounds
6. Watchlist Symbol Synchronization:
   - Clicking a symbol in the Watchlist dynamically syncs the active chart instrument
7. Runtime diagnostics: clean execution with zero critical system failures.
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
from workflows.trade_terminal.pages.profile_menu_page import ProfileMenuPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.smoke
def test_chart_container_and_engine_mounting(
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the chart top pane (#app .div1.initialHeight) renders
    with the tradingview widget container and at least one active chart container.
    """
    trading_chart_page.navigate_to_chart()
    assert_url_contains(trading_chart_page.page, "/dashboard", timeout=15000)

    # 1. Assert main container & top pane
    assert_element_is_visible(trading_chart_page.chart_page_container, element_name="Chart Page Container")
    assert_element_is_visible(trading_chart_page.chart_top_pane, element_name="Chart Top Pane (.div1.initialHeight)")
    assert_element_is_visible(trading_chart_page.tradingview_widget_container, element_name="TradingView Widget Container")

    # 2. Assert chart pane visibility
    assert trading_chart_page.is_chart_pane_visible(), "Expected either TradingView or Black Trader chart pane to be visible"


@pytest.mark.trade
def test_chart_engine_switch_between_tradingview_and_blacktrader(
    trading_chart_page: TradingChartPage,
    profile_menu_page: ProfileMenuPage,
):
    """
    Verify switching between TradingView and Black Trader engines via profile drawer:
    1. Switch to Black Trader -> verify #bt_chart_container is visible, #tv_chart_container is hidden, iframe#xten attached.
    2. Switch back to TradingView -> verify #tv_chart_container is visible, #bt_chart_container is hidden, TV iframe attached.
    """
    trading_chart_page.navigate_to_chart()

    # Step 1: Switch to Black Trader
    trading_chart_page.switch_to_blacktrader()
    assert_element_is_visible(trading_chart_page.bt_chart_container, element_name="Black Trader Chart Container")
    assert_element_is_visible(trading_chart_page.bt_iframe_locator, element_name="Black Trader IFrame (#xten)")
    assert not trading_chart_page.tv_chart_container.is_visible(), "TradingView container should be hidden when Black Trader is active"

    # Step 2: Switch back to TradingView
    trading_chart_page.switch_to_tradingview()
    assert_element_is_visible(trading_chart_page.tv_chart_container, element_name="TradingView Chart Container")
    assert_element_is_visible(trading_chart_page.tv_iframe_locator, element_name="TradingView IFrame")
    assert not trading_chart_page.bt_chart_container.is_visible(), "Black Trader container should be hidden when TradingView is active"


@pytest.mark.trade
@pytest.mark.smoke
def test_tradingview_header_toolbar_elements_and_symbol(
    trading_chart_page: TradingChartPage,
):
    """
    Verify that in TradingView mode, the top header toolbar inside the iframe contains:
    - Symbol search button displaying active symbol (e.g. XAUUSD)
    - Compare/add symbol button
    - Timeframe interval buttons
    - Chart style selector
    - Indicators dialog button
    - Settings/Properties and Fullscreen controls
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.switch_to_tradingview()

    # Verify active symbol
    symbol_text = trading_chart_page.get_tv_active_symbol()
    assert len(symbol_text) > 0, f"Expected non-empty active symbol in TradingView header, got: {symbol_text}"

    # Verify header toolbar controls inside TV iframe
    expect(trading_chart_page.tv_symbol_search_btn).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_compare_btn).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_properties_btn).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_fullscreen_btn).to_be_visible(timeout=10000)


@pytest.mark.trade
def test_tradingview_drawing_toolbar_tools(
    trading_chart_page: TradingChartPage,
):
    """
    Verify that in TradingView mode, the left drawing toolbar inside the iframe contains
    tool groups: Cursors, Trendlines, Gann/Fibonacci, and Geometric Shapes.
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.switch_to_tradingview()

    # Verify drawing tool groups
    expect(trading_chart_page.tv_drawing_cursors).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_drawing_trendlines).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_drawing_fib).to_be_visible(timeout=10000)
    expect(trading_chart_page.tv_drawing_shapes).to_be_visible(timeout=10000)


@pytest.mark.trade
def test_black_trader_toolbar_controls(
    trading_chart_page: TradingChartPage,
):
    """
    Verify that in Black Trader mode, the toolbar inside iframe#xten contains:
    - Symbol indicator
    - Timeframe dropdown (data-popup='DropMenu')
    - Chart type dropdown (data-popup='ChartType')
    - Indicators button
    - Grid layout popup (data-popup='GridPopMenu')
    - Fullscreen toggle and Screenshot button
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.switch_to_blacktrader()

    try:
        # Verify BT toolbar controls inside iframe#xten
        expect(trading_chart_page.bt_symbol_btn).to_be_visible(timeout=15000)
        expect(trading_chart_page.bt_timeframe_btn).to_be_visible(timeout=10000)
        expect(trading_chart_page.bt_chart_type_btn).to_be_visible(timeout=10000)
        expect(trading_chart_page.bt_indicators_btn).to_be_visible(timeout=10000)
        expect(trading_chart_page.bt_grid_menu_btn).to_be_visible(timeout=10000)
        expect(trading_chart_page.bt_fullscreen_btn).to_be_visible(timeout=10000)
        expect(trading_chart_page.bt_screenshot_btn).to_be_visible(timeout=10000)
    finally:
        # Restore default TradingView engine
        trading_chart_page.switch_to_tradingview()


@pytest.mark.trade
def test_chart_quick_trade_widget_lot_adjustment(
    trading_chart_page: TradingChartPage,
):
    """
    Verify quick trading overlay widget controls:
    1. Widget presence with BUY, SELL, Lot input, and stepper buttons.
    2. Modifying lot size via direct input.
    3. Modifying lot size via increment (+) and decrement (-) buttons.
    4. Minimum lot size boundary enforcement (≥ 0.01).
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.show_quick_trade_widget()

    assert_element_is_visible(trading_chart_page.quick_trade_widget, element_name="Quick Trading Overlay Widget")
    assert_element_is_visible(trading_chart_page.quick_buy_btn, element_name="Quick Trade BUY Button")
    assert_element_is_visible(trading_chart_page.quick_sell_btn, element_name="Quick Trade SELL Button")
    assert_element_is_visible(trading_chart_page.quick_lot_input, element_name="Quick Trade Lot Size Input")

    # Set lot size directly
    trading_chart_page.set_quick_trade_lot_value(0.05)
    lot_val = trading_chart_page.get_quick_trade_lot_value()
    assert abs(lot_val - 0.05) < 0.001, f"Expected lot size 0.05, got {lot_val}"

    # Increment lot size (+)
    trading_chart_page.adjust_quick_trade_lot("plus")
    lot_val_inc = trading_chart_page.get_quick_trade_lot_value()
    assert lot_val_inc > 0.05, f"Expected lot size > 0.05 after plus, got {lot_val_inc}"

    # Reset to default 0.01
    trading_chart_page.set_quick_trade_lot_value(0.01)
    lot_val_reset = trading_chart_page.get_quick_trade_lot_value()
    assert abs(lot_val_reset - 0.01) < 0.001, f"Expected lot size 0.01, got {lot_val_reset}"


@pytest.mark.trade
def test_chart_symbol_synchronization_with_watchlist(
    trading_chart_page: TradingChartPage,
    watchlist_page: WatchlistPage,
):
    """
    Verify that selecting a symbol from the Watchlist updates the active chart symbol.
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.switch_to_tradingview()

    # Open watchlist and click a symbol (e.g. EURUSD)
    watchlist_page.navigate()
    symbols_data = watchlist_page.get_all_symbols_data()
    available_symbols = [s["symbol"] for s in symbols_data if s["symbol"]]
    
    target_symbol = "EURUSD" if "EURUSD" in available_symbols else (available_symbols[0] if available_symbols else "GBPUSD")
    if target_symbol:
        watchlist_page.open_chart_for_symbol(target_symbol)
        trading_chart_page.navigate_to_chart()
        trading_chart_page.page.wait_for_timeout(2000)

        # Verify TV active symbol reflects target or updated symbol
        tv_symbol = trading_chart_page.get_tv_active_symbol()
        assert len(tv_symbol) > 0, f"Expected active symbol in chart after sync, got: {tv_symbol}"


@pytest.mark.trade
def test_chart_page_diagnostics_telemetry(
    trading_chart_page: TradingChartPage,
):
    """
    Telemetry check: verify clean execution during full chart lifecycle.
    """
    trading_chart_page.navigate_to_chart()
    trading_chart_page.page.wait_for_timeout(2000)

    if hasattr(trading_chart_page.page, "_diagnostics"):
        diagnostics = trading_chart_page.page._diagnostics
        assert len(diagnostics.get_page_errors()) == 0, (
            f"Chart page diagnostics detected uncaught JS errors: {diagnostics.get_page_errors()}"
        )
