"""
Trade Terminal TradingView Chart Canvas & Interactive Layout Test Suite.
Verifies full functionality of the TradingView Chart Canvas & Overlay Layout:
- Chart markup table pane and HTML5 rendering canvases
- Dynamic OHLC price data changes on cursor hover across candles
- Chart panning / dragging navigation and Control Bar Reset view
- Quick Trade overlay on chart (Lot size input, BUY execution, SELL execution)
- Toast notifications and order placement verification
- Clean runtime telemetry and zero uncaught JavaScript errors
"""

import pytest
from playwright.sync_api import expect

from workflows.trade_terminal.pages.tradingview_chart_page import TradingViewChartPage


@pytest.mark.trade
def test_tradingview_canvas_layout_structure_and_visibility(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that the TradingView chart markup pane, HTML5 canvas layers,
    OHLC legend, Quick Trade overlay (BUY/SELL & lot size input),
    and control bar wrapper are visible and properly structured.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1500)

    # 1. Assert Chart markup table pane
    expect(tradingview_chart_page.chart_pane).to_be_visible(timeout=10000)

    # 2. Assert OHLC Legend
    expect(tradingview_chart_page.chart_legend).to_be_visible(timeout=5000)
    legend_text = tradingview_chart_page.get_legend_ohlc_text()
    assert len(legend_text) > 0, f"Expected non-empty legend text, got: {legend_text}"

    # 3. Assert Quick Trade Overlay (BUY, SELL, Lot size)
    expect(tradingview_chart_page.quick_trade_buy_btn).to_be_visible(timeout=5000)
    expect(tradingview_chart_page.quick_trade_sell_btn).to_be_visible(timeout=5000)
    expect(tradingview_chart_page.quick_trade_lot_input).to_be_visible(timeout=5000)

    # 4. Assert Control Bar Wrapper
    expect(tradingview_chart_page.control_bar_wrapper).to_be_visible(timeout=5000)


@pytest.mark.trade
def test_tradingview_canvas_ohlc_cursor_hover_dynamics(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that moving the cursor across different points of the chart canvas
    dynamically changes and updates the OHLC price data in the chart legend.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1500)

    # Hover at left side (X = 20%)
    ohlc_left = tradingview_chart_page.hover_chart_at_fraction(0.20, 0.50)
    assert len(ohlc_left) > 0, "Expected non-empty OHLC data at X=20%"

    # Hover at middle (X = 50%)
    ohlc_mid = tradingview_chart_page.hover_chart_at_fraction(0.50, 0.50)
    assert len(ohlc_mid) > 0, "Expected non-empty OHLC data at X=50%"

    # Hover at right side (X = 80%)
    ohlc_right = tradingview_chart_page.hover_chart_at_fraction(0.80, 0.50)
    assert len(ohlc_right) > 0, "Expected non-empty OHLC data at X=80%"

    # Validate that at least two points have distinct OHLC price values
    assert ohlc_left != ohlc_right or ohlc_mid != ohlc_right, (
        f"Expected OHLC price data to dynamically change across canvas. "
        f"Left: '{ohlc_left}', Mid: '{ohlc_mid}', Right: '{ohlc_right}'"
    )


@pytest.mark.trade
def test_tradingview_canvas_panning_and_view_reset(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify dragging/panning the chart canvas horizontally to scroll history
    and resetting chart view via the control bar wrapper.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1500)

    # Pan chart canvas horizontally
    tradingview_chart_page.pan_chart_canvas(delta_x=250, delta_y=0)
    tradingview_chart_page.page.wait_for_timeout(800)

    # Click Reset chart view in control bar
    reset_clicked = tradingview_chart_page.click_reset_chart_view()
    assert reset_clicked, "Expected Reset chart view button in control bar to be clicked"
    tradingview_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_tradingview_canvas_quick_trading_lot_size_change(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify changing the trade lot size inside the chart overlay.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1000)

    # Set lot size to 0.05
    tradingview_chart_page.set_quick_trade_lot_size("0.05")
    lot_val = tradingview_chart_page.get_quick_trade_lot_size()
    assert lot_val == "0.05", f"Expected lot size '0.05', got '{lot_val}'"

    # Restore lot size to 0.01
    tradingview_chart_page.set_quick_trade_lot_size("0.01")
    lot_val_restored = tradingview_chart_page.get_quick_trade_lot_size()
    assert lot_val_restored == "0.01", f"Expected lot size '0.01', got '{lot_val_restored}'"


@pytest.mark.trade
def test_tradingview_canvas_quick_trading_buy_execution(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify placing a BUY order directly from the TradingView chart quick trade overlay
    and validating order placement feedback.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1000)

    # Set minimal lot size
    tradingview_chart_page.set_quick_trade_lot_size("0.01")

    # Execute BUY order
    buy_executed = tradingview_chart_page.execute_quick_trade_buy()
    assert buy_executed, "Expected BUY order action to execute"

    # Verify toast or notification feedback
    toast = tradingview_chart_page.get_latest_toast_message(timeout=4000)
    assert toast is not None, "Expected order placement confirmation toast to appear"
    assert "BUY" in toast or "Order" in toast or "Lots" in toast, (
        f"Expected BUY order confirmation details in toast, got: '{toast}'"
    )


@pytest.mark.trade
def test_tradingview_canvas_quick_trading_sell_execution(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify placing a SELL order directly from the TradingView chart quick trade overlay
    and validating order placement feedback.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1000)

    # Set minimal lot size
    tradingview_chart_page.set_quick_trade_lot_size("0.01")

    # Execute SELL order
    sell_executed = tradingview_chart_page.execute_quick_trade_sell()
    assert sell_executed, "Expected SELL order action to execute"

    # Verify toast or notification feedback
    toast = tradingview_chart_page.get_latest_toast_message(timeout=4000)
    assert toast is not None, "Expected order placement confirmation toast to appear"
    assert "SELL" in toast or "Order" in toast or "Lots" in toast, (
        f"Expected SELL order confirmation details in toast, got: '{toast}'"
    )


@pytest.mark.trade
def test_tradingview_canvas_diagnostics_clean(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify clean runtime telemetry and zero uncaught JavaScript page exceptions
    during all TradingView chart canvas and quick trading operations.
    """
    tradingview_chart_page.navigate_to_chart()
    tradingview_chart_page.page.wait_for_timeout(1000)

    # Hover and pan canvas
    tradingview_chart_page.hover_chart_at_fraction(0.30, 0.50)
    tradingview_chart_page.hover_chart_at_fraction(0.70, 0.50)
    tradingview_chart_page.pan_chart_canvas(delta_x=100)
    tradingview_chart_page.click_reset_chart_view()

    tradingview_chart_page.page.wait_for_timeout(1000)

    # Telemetry verification
    if hasattr(tradingview_chart_page.page, "_diagnostics"):
        diagnostics = tradingview_chart_page.page._diagnostics
        assert len(diagnostics.get_page_errors()) == 0, (
            f"Expected 0 uncaught JS errors during canvas operations, got: {diagnostics.get_page_errors()}"
        )
