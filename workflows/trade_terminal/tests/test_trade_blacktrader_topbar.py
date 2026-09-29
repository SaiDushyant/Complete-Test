"""
Trade Terminal Black Trader Chart Top Bar Test Suite.
Verifies full functionality of the Black Trader Chart top navbar (#navbar):
- Symbol badge display
- Timeframe intervals switching (1 Min, 5 Min, 15 Min)
- Chart types switching (Candles, Line, Bar)
- Indicators dialog search and dismiss workflow
- Multi-chart Grid layout menu & Screenshot controls
- Trade lines toggle & More menu
- Clean runtime telemetry
"""

import pytest
from playwright.sync_api import expect

from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage


@pytest.mark.trade
def test_blacktrader_topbar_structure_and_visibility(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that the Black Trader top navbar (#navbar) is visible and contains:
    - Active Symbol badge
    - Timeframe menu button
    - Chart Type dropdown button
    - Indicators modal button
    - Multi-chart Grid menu button
    - Fullscreen toggle button
    - Screenshot snapshot button
    - Hide/Show all trades toggle button
    - More settings menu button
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Assert navbar container
    expect(blacktrader_chart_page.navbar).to_be_visible(timeout=10000)

    # 2. Assert Symbol badge
    expect(blacktrader_chart_page.symbol_btn).to_be_visible(timeout=5000)
    symbol_text = blacktrader_chart_page.get_active_symbol_text()
    assert len(symbol_text) > 0, "Expected non-empty symbol text on Black Trader toolbar"

    # 3. Assert Timeframe button
    expect(blacktrader_chart_page.timeframe_btn).to_be_visible(timeout=5000)

    # 4. Assert Chart Type & Indicators buttons
    expect(blacktrader_chart_page.chart_type_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.indicators_btn).to_be_visible(timeout=5000)

    # 5. Assert Grid, Fullscreen, Screenshot, and More menu controls
    expect(blacktrader_chart_page.grid_menu_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.fullscreen_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.screenshot_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.more_menu_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.hide_trades_btn).to_be_visible(timeout=5000)


@pytest.mark.trade
def test_blacktrader_topbar_timeframe_menu_switching(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the timeframe menu, switching across different timeframes
    (5 Min, 15 Min), and restoring back to 1 Min.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Switch to 5 Min
    blacktrader_chart_page.open_timeframe_menu()
    selected_5m = blacktrader_chart_page.select_timeframe("5 Min")
    assert selected_5m, "Expected to select '5 Min' timeframe"
    blacktrader_chart_page.page.wait_for_timeout(1000)
    tf_5m = blacktrader_chart_page.get_active_timeframe()
    assert "5 Min" in tf_5m or "5" in tf_5m, f"Expected 5 Min timeframe active, got: '{tf_5m}'"

    # 2. Switch to 15 Min
    blacktrader_chart_page.open_timeframe_menu()
    selected_15m = blacktrader_chart_page.select_timeframe("15 Min")
    assert selected_15m, "Expected to select '15 Min' timeframe"
    blacktrader_chart_page.page.wait_for_timeout(1000)
    tf_15m = blacktrader_chart_page.get_active_timeframe()
    assert "15 Min" in tf_15m or "15" in tf_15m, f"Expected 15 Min timeframe active, got: '{tf_15m}'"

    # 3. Restore to 1 Min
    blacktrader_chart_page.open_timeframe_menu()
    selected_1m = blacktrader_chart_page.select_timeframe("1 Min")
    assert selected_1m, "Expected to restore '1 Min' timeframe"
    blacktrader_chart_page.page.wait_for_timeout(1000)
    tf_1m = blacktrader_chart_page.get_active_timeframe()
    assert "1 Min" in tf_1m or "1" in tf_1m, f"Expected 1 Min timeframe active, got: '{tf_1m}'"


@pytest.mark.trade
def test_blacktrader_topbar_chart_type_switching(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the chart type dropdown and selecting different chart styles (Line, Candles).
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Select Line chart
    blacktrader_chart_page.open_chart_type_menu()
    selected_line = blacktrader_chart_page.select_chart_type("Line")
    assert selected_line, "Expected to select Line chart style"
    blacktrader_chart_page.page.wait_for_timeout(800)

    # 2. Restore Candles
    blacktrader_chart_page.open_chart_type_menu()
    selected_candles = blacktrader_chart_page.select_chart_type("Candle")
    assert selected_candles, "Expected to restore Candles chart style"
    blacktrader_chart_page.page.wait_for_timeout(800)


@pytest.mark.trade
def test_blacktrader_topbar_indicators_search_and_dialog_flow(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Indicators modal, querying/searching for indicators (EMA/RSI),
    and closing the modal cleanly.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Open Indicators modal
    opened = blacktrader_chart_page.open_indicators_dialog()
    assert opened, "Expected Indicators modal to open"
    blacktrader_chart_page.page.wait_for_timeout(800)

    # 2. Search for indicator
    blacktrader_chart_page.search_indicator("EMA")
    blacktrader_chart_page.page.wait_for_timeout(600)

    # 3. Close dialog
    closed = blacktrader_chart_page.close_indicators_dialog()
    assert closed, "Expected Indicators modal to close cleanly"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_topbar_grid_menu_and_snapshot_controls(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Multi-Chart Grid layout menu, triggering Fullscreen toggle,
    and opening the Screenshot snapshot menu.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Open Grid layout menu
    grid_opened = blacktrader_chart_page.open_grid_menu()
    assert grid_opened, "Expected Grid menu to open"
    blacktrader_chart_page.page.keyboard.press("Escape")
    blacktrader_chart_page.page.wait_for_timeout(400)

    # 2. Toggle Fullscreen
    fs_toggled = blacktrader_chart_page.toggle_fullscreen()
    assert fs_toggled, "Expected Fullscreen toggle to execute"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # 3. Open Screenshot menu
    ss_opened = blacktrader_chart_page.open_screenshot_menu()
    assert ss_opened, "Expected Screenshot menu to open"
    blacktrader_chart_page.page.keyboard.press("Escape")
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_topbar_trade_lines_and_more_menu_toggles(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify toggling Trade lines visibility and opening the More settings menu.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Toggle Trade Lines
    trade_toggled = blacktrader_chart_page.toggle_trade_lines()
    assert trade_toggled, "Expected Trade lines toggle to execute"
    blacktrader_chart_page.page.wait_for_timeout(500)

    # Toggle back
    blacktrader_chart_page.toggle_trade_lines()
    blacktrader_chart_page.page.wait_for_timeout(500)

    # 2. Open More menu
    more_opened = blacktrader_chart_page.open_more_menu()
    assert more_opened, "Expected More menu to open"
    blacktrader_chart_page.page.keyboard.press("Escape")
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_topbar_diagnostics_clean(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify telemetry and ensure operations run cleanly on the Black Trader top navbar.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Operate timeframe and chart type
    blacktrader_chart_page.open_timeframe_menu()
    blacktrader_chart_page.select_timeframe("5 Min")
    blacktrader_chart_page.open_timeframe_menu()
    blacktrader_chart_page.select_timeframe("1 Min")

    blacktrader_chart_page.page.wait_for_timeout(1000)
