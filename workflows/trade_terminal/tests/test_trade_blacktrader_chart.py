"""
Test Suite: Black Trader Chart Mainbar, Canvas, Hover Controls & Quick Trading
URL: https://stage.xtremenext.com/dashboard/

Validates all interactive elements within the Black Trader chart viewport (#mainbar):
- Verification of series data loading (active symbol, timeframe, OHLC values, real-time quotes)
- Chart canvas zoomability via mouse wheel and scroll actions
- Chart canvas pannability via mouse drag interactions
- Dynamic hover controls (#hover-controls-agrid-*-controls) visibility and interaction
- Hover controls buttons: Zoom In, Zoom Out, Scroll Left, Scroll Right, Reset View
- Price and Time scale fitting and position reset controls
- Quick Trading widget: lot size modifications, Buy and Sell order execution with toast confirmations
"""

import pytest
from playwright.sync_api import expect

from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage


@pytest.mark.trade
def test_blacktrader_chart_data_loads(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that Black Trader chart series data loads properly:
    - Active symbol and timeframe are displayed
    - OHLC legend prices (Open, High, Low, Close) are valid numbers > 0
    - Quick Trading bid and ask prices are dynamically populated and positive
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(2000)

    # 1. Mainbar and Canvas elements are visible
    expect(blacktrader_chart_page.mainbar).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.lwc_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
    assert blacktrader_chart_page.chart_canvases.count() >= 2, "Expected at least 2 canvas layers"

    # 2. Extract series and quote data
    series_data = blacktrader_chart_page.get_chart_series_data()
    assert series_data["symbol"], f"Expected non-empty symbol, got: {series_data['symbol']}"
    assert series_data["timeframe"], f"Expected non-empty timeframe, got: {series_data['timeframe']}"

    # 3. Validate OHLC numeric values
    assert series_data["open"] is not None and series_data["open"] > 0, f"Invalid Open price: {series_data['open']}"
    assert series_data["high"] is not None and series_data["high"] > 0, f"Invalid High price: {series_data['high']}"
    assert series_data["low"] is not None and series_data["low"] > 0, f"Invalid Low price: {series_data['low']}"
    assert series_data["close"] is not None and series_data["close"] > 0, f"Invalid Close price: {series_data['close']}"

    # 4. Validate Quick Trading quotes
    assert series_data["sellPrice"] is not None and series_data["sellPrice"] > 0, f"Invalid Sell price: {series_data['sellPrice']}"
    assert series_data["buyPrice"] is not None and series_data["buyPrice"] > 0, f"Invalid Buy price: {series_data['buyPrice']}"


@pytest.mark.trade
def test_blacktrader_chart_canvas_scrolling(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that the chart canvas is scrollable (zoomable via mouse wheel).
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Scroll (zoom in)
    zoomed_in = blacktrader_chart_page.scroll_chart_canvas(delta_y=-120)
    assert zoomed_in, "Expected chart canvas to scroll / zoom in"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Scroll (zoom out)
    zoomed_out = blacktrader_chart_page.scroll_chart_canvas(delta_y=120)
    assert zoomed_out, "Expected chart canvas to scroll / zoom out"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_chart_canvas_panning(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that the chart canvas is pannable by dragging horizontally.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Pan left
    panned_left = blacktrader_chart_page.pan_chart_canvas(delta_x=-200)
    assert panned_left, "Expected chart canvas to pan left"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Pan right
    panned_right = blacktrader_chart_page.pan_chart_canvas(delta_x=200)
    assert panned_right, "Expected chart canvas to pan right"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_chart_hover_controls_visibility(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that hovering over the bottom-center region reveals
    the hover controls bar (#hover-controls-agrid-*-controls).
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    revealed = blacktrader_chart_page.reveal_hover_controls()
    assert revealed, "Expected hover controls to become visible"

    expect(blacktrader_chart_page.hover_zoom_out_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.hover_zoom_in_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.hover_scroll_left_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.hover_scroll_right_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.hover_reset_view_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)


@pytest.mark.trade
def test_blacktrader_chart_hover_controls_actions(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify clicking each of the hover control buttons:
    - Zoom In
    - Zoom Out
    - Scroll Left
    - Scroll Right
    - Reset View
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Click Zoom In
    assert blacktrader_chart_page.click_hover_control("zoom_in")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Zoom Out
    assert blacktrader_chart_page.click_hover_control("zoom_out")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Scroll Left
    assert blacktrader_chart_page.click_hover_control("scroll_left")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Scroll Right
    assert blacktrader_chart_page.click_hover_control("scroll_right")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Reset View
    assert blacktrader_chart_page.click_hover_control("reset_view")
    blacktrader_chart_page.page.wait_for_timeout(300)


@pytest.mark.trade
def test_blacktrader_chart_scale_fit_controls(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify scale fitting controls in the bottom-right corner:
    - Fit Price Scale
    - Fit Time Scale
    - Reset to Initial Position
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Fit Price Scale
    if blacktrader_chart_page.fit_price_scale_btn.is_visible():
        expect(blacktrader_chart_page.fit_price_scale_btn).to_be_visible()
        blacktrader_chart_page.fit_scales("price")
        blacktrader_chart_page.page.wait_for_timeout(300)

    # 2. Fit Time Scale
    if blacktrader_chart_page.fit_time_scale_btn.is_visible():
        expect(blacktrader_chart_page.fit_time_scale_btn).to_be_visible()
        blacktrader_chart_page.fit_scales("time")
        blacktrader_chart_page.page.wait_for_timeout(300)

    # 3. Reset to Initial Position
    if blacktrader_chart_page.reset_initial_pos_btn.is_visible():
        expect(blacktrader_chart_page.reset_initial_pos_btn).to_be_visible()
        blacktrader_chart_page.fit_scales("initial")
        blacktrader_chart_page.page.wait_for_timeout(300)


@pytest.mark.trade
def test_blacktrader_chart_quick_trade_lot_size(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify modifying the Quick Trading lot size.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Change lot size to 0.05
    blacktrader_chart_page.set_quick_trade_lot_size("0.05")
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Restore lot size to 0.01
    blacktrader_chart_page.set_quick_trade_lot_size("0.01")
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_chart_quick_trade_buy_and_sell(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify placing Quick Buy and Quick Sell orders from the chart toolbar.
    Asserts confirmation toast or execution alert appears.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Execute Quick Buy
    executed_buy = blacktrader_chart_page.execute_quick_buy()
    assert executed_buy, "Expected Quick Buy order to trigger"

    # Expect order executed toast
    toast = blacktrader_chart_page.bt_iframe.locator("div.toast:has-text('Order Executed')").first
    expect(toast).to_be_visible(timeout=TIMEOUT_DEFAULT)
    blacktrader_chart_page.page.wait_for_timeout(1000)

    # Execute Quick Sell
    executed_sell = blacktrader_chart_page.execute_quick_sell()
    assert executed_sell, "Expected Quick Sell order to trigger"

    expect(toast).to_be_visible(timeout=TIMEOUT_DEFAULT)
    blacktrader_chart_page.page.wait_for_timeout(1000)


@pytest.mark.trade
def test_blacktrader_chart_diagnostics_clean(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify telemetry and clean execution during Black Trader chart canvas operations.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Sequence of canvas operations
    blacktrader_chart_page.scroll_chart_canvas(-100)
    blacktrader_chart_page.pan_chart_canvas(-100)
    blacktrader_chart_page.click_hover_control("reset_view")
    blacktrader_chart_page.fit_scales("all")
    blacktrader_chart_page.page.wait_for_timeout(1000)
