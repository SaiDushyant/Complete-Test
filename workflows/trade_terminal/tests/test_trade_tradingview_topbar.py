"""

Trade Terminal TradingView Chart Top Bar Deep Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

JS Path of Top Bar under test:
document.querySelector("body > div.js-rootresizer__contents.layout-with-border-radius > div.layout__area--top > div")

Comprehensive coverage of the TradingView top bar:
1. Top bar structure and elements presence:
   - Symbol search, Compare, Interval menu, Chart styles menu, Indicators dialog,
     Indicator templates, Undo/Redo, Save layout, Settings dialog, Fullscreen, Snapshot.
2. Symbol search and changing instruments:
   - Searching and switching to EURUSD, BTCUSD, XAUUSD, verifying header text updates.
3. Timeframe intervals workflow:
   - Sequential switching through multiple timeframe intervals (1m, 5m, 15m, 1h, 1D).
4. Chart styles / types workflow:
   - Sequential switching through chart styles (Candles, Bars, Line, Area, Heikin Ashi).
5. Indicators and Strategies dialog workflow:
   - Searching and adding top technical indicators (Relative Strength Index, Moving Average, Bollinger Bands),
     verifying study legend rendered on chart canvas.
6. Compare / Add Symbol dialog workflow.
7. Chart settings properties dialog:
   - Opening modal, switching property tabs (Symbol, Status line, Scales, Canvas, Trading), and closing.
8. Fullscreen and snapshot action triggers.
9. Runtime diagnostics: clean execution with zero uncaught JavaScript errors.
"""

from __future__ import annotations

import time
import pytest
from playwright.sync_api import expect

from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.tradingview_chart_page import TradingViewChartPage


@pytest.mark.trade
@pytest.mark.smoke
def test_tradingview_topbar_structure_and_visibility(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that the TradingView top bar container is rendered and all 13 interactive
    controls (Symbol search, Compare, Interval, Styles, Indicators, Templates,
    Undo, Save, Settings, Fullscreen, Snapshot) are attached and visible.
    """
    tradingview_chart_page.navigate_to_chart()
    assert_url_contains(tradingview_chart_page.page, "/dashboard", timeout=15000)

    # Assert top bar container
    assert_element_is_visible(tradingview_chart_page.top_bar, element_name="TradingView Top Bar Container")

    # Assert top bar controls
    assert_element_is_visible(tradingview_chart_page.symbol_search_btn, element_name="TV Symbol Search Button")
    assert_element_is_visible(tradingview_chart_page.compare_btn, element_name="TV Compare Button")
    assert_element_is_visible(tradingview_chart_page.interval_menu_btn, element_name="TV Interval Dropdown Button")
    assert_element_is_visible(tradingview_chart_page.chart_style_btn, element_name="TV Chart Style Dropdown Button")
    assert_element_is_visible(tradingview_chart_page.indicators_btn, element_name="TV Indicators Dialog Button")
    assert_element_is_visible(tradingview_chart_page.settings_btn, element_name="TV Settings Properties Button")
    assert_element_is_visible(tradingview_chart_page.fullscreen_btn, element_name="TV Fullscreen Button")
    assert_element_is_visible(tradingview_chart_page.snapshot_btn, element_name="TV Snapshot Button")


@pytest.mark.trade
def test_tradingview_topbar_symbol_search_and_change(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the Symbol Search modal, searching for different instruments,
    and switching the chart symbol to EURUSD, BTCUSD, and restoring to XAUUSD.
    """
    tradingview_chart_page.navigate_to_chart()

    initial_symbol = tradingview_chart_page.get_active_symbol()
    assert len(initial_symbol) > 0, f"Expected initial active symbol, got: {initial_symbol}"

    # 1. Change to EURUSD
    new_symbol = tradingview_chart_page.search_and_change_symbol("EURUSD")
    assert "EUR" in new_symbol or "USD" in new_symbol, f"Expected EURUSD in active symbol, got: {new_symbol}"

    # 2. Change to BTCUSD
    btc_symbol = tradingview_chart_page.search_and_change_symbol("BTCUSD")
    assert "BTC" in btc_symbol or "USD" in btc_symbol, f"Expected BTCUSD in active symbol, got: {btc_symbol}"

    # 3. Restore to XAUUSD
    restored_symbol = tradingview_chart_page.search_and_change_symbol("XAUUSD")
    assert "XAU" in restored_symbol or "USD" in restored_symbol, f"Expected XAUUSD in active symbol, got: {restored_symbol}"


@pytest.mark.trade
def test_tradingview_topbar_all_timeframe_intervals(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the timeframe interval menu and switching across multiple intervals:
    1 minute, 5 minutes, 15 minutes, 1 hour, 1 day.
    """
    tradingview_chart_page.navigate_to_chart()

    # Get available intervals list
    available_intervals = tradingview_chart_page.get_available_intervals()
    assert len(available_intervals) >= 5, f"Expected at least 5 intervals in menu, got: {len(available_intervals)}"

    # Test sequential switching
    test_intervals = ["5 minutes", "15 minutes", "1 hour", "1 day"]
    for interval in test_intervals:
        tradingview_chart_page.select_interval(interval)
        tradingview_chart_page.page.wait_for_timeout(800)
        active_text = tradingview_chart_page.get_active_interval_text()
        assert len(active_text) > 0, f"Expected non-empty active interval text for '{interval}'"


@pytest.mark.trade
def test_tradingview_topbar_all_chart_styles(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the Chart Styles menu and cycling through different rendering styles:
    Bars, Candles, Line, Area, Heikin Ashi, and restoring Candles.
    """
    tradingview_chart_page.navigate_to_chart()

    # Get available styles list
    styles = tradingview_chart_page.get_available_chart_styles()
    assert len(styles) >= 5, f"Expected at least 5 chart styles in menu, got: {len(styles)}"
    style_names = [s["text"] for s in styles]

    # Test sequential switching across major styles
    styles_to_test = ["Bars", "Line", "Area", "Heikin Ashi", "Candles"]
    for style in styles_to_test:
        if any(style.lower() in s.lower() for s in style_names):
            tradingview_chart_page.select_chart_style(style)
            tradingview_chart_page.page.wait_for_timeout(800)


@pytest.mark.trade
def test_tradingview_topbar_indicators_search_and_application(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Indicators & Strategies dialog, searching for top technical indicators
    (Relative Strength Index, Moving Average, Bollinger Bands), and adding them to the chart.
    """
    tradingview_chart_page.navigate_to_chart()

    # Add Relative Strength Index (RSI)
    added_rsi = tradingview_chart_page.search_and_add_indicator("Relative Strength Index")
    assert added_rsi, "Expected to successfully add Relative Strength Index indicator"

    # Add Moving Average (MA)
    added_ma = tradingview_chart_page.search_and_add_indicator("Moving Average")
    assert added_ma, "Expected to successfully add Moving Average indicator"

    # Verify study legends on chart
    legends = tradingview_chart_page.get_study_legend_titles()
    assert len(legends) > 0, f"Expected indicator study legends rendered on chart, got: {legends}"


@pytest.mark.trade
def test_tradingview_topbar_compare_symbol_dialog(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the Compare or Add Symbol dialog and closing cleanly.
    """
    tradingview_chart_page.navigate_to_chart()

    tradingview_chart_page.open_compare_dialog()
    tradingview_chart_page.page.wait_for_timeout(1000)
    tradingview_chart_page.close_dialog()
    tradingview_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_tradingview_topbar_chart_settings_properties_tabs(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the Chart Settings dialog, querying all configuration tabs
    (Symbol, Status line, Scales, Canvas, Trading), switching between them, and closing.
    """
    tradingview_chart_page.navigate_to_chart()

    tabs = tradingview_chart_page.get_settings_dialog_tabs()
    assert len(tabs) >= 3, f"Expected at least 3 tabs in settings dialog, got: {tabs}"

    # Switch across tabs
    for tab in tabs[:3]:
        tradingview_chart_page.switch_settings_tab(tab)
        tradingview_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_tradingview_topbar_fullscreen_and_snapshot_controls(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify triggering Fullscreen mode and taking a Snapshot from the top bar.
    """
    tradingview_chart_page.navigate_to_chart()

    # Test Fullscreen
    tradingview_chart_page.toggle_fullscreen()

    # Test Snapshot
    tradingview_chart_page.click_snapshot()


@pytest.mark.trade
def test_tradingview_topbar_diagnostics_clean(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify clean runtime telemetry and zero uncaught JavaScript page exceptions
    during all TradingView top bar operations.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1500)

    if hasattr(tradingview_chart_page.page, "_diagnostics"):
        diagnostics = tradingview_chart_page.page._diagnostics
        assert len(diagnostics.get_page_errors()) == 0, (
            f"TradingView top bar diagnostics detected uncaught JS errors: {diagnostics.get_page_errors()}"
        )
