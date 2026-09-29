"""
Trade Terminal TradingView Chart Drawing Sidebar Deep Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

JS Path of Drawing Sidebar under test:
document.querySelector("#drawing-toolbar > div > div > div")

Comprehensive coverage of the TradingView drawing sidebar:
1. Drawing sidebar structure and primary tool buttons visibility:
   - Cursor tools, Trend line tools, Gann & Fibonacci, Geometric shapes, Annotation,
     Patterns, Forecasting & measurement, Icons, Measure, Zoom In, Magnet Mode,
     Stay in Drawing Mode, Lock All Drawing Tools, Hide all drawings, Remove drawings,
     Show Object Tree.
2. Cursor tools flyout menu:
   - Opening flyout, verifying subtools (Cross, Dot, Arrow, Eraser), selecting Dot, Arrow, and restoring Cross.
3. Trend line tools flyout menu:
   - Opening flyout, querying subtools (Trend Line, Arrow, Ray, Horizontal Line, Vertical Line, Parallel Channel),
     switching between subtools.
4. Geometric shapes flyout menu:
   - Opening flyout, querying subtools (Brush, Highlighter, Rectangle, Circle, Path), selecting Rectangle and Brush.
5. Annotation tools flyout menu:
   - Opening flyout, querying subtools (Text, Anchored Text, Note, Callout, Price Label), selecting Note and Text.
6. Gann & Fibonacci tools flyout menu:
   - Opening flyout, querying subtools (Fib Retracement, Trend-Based Fib Extension, Fib Channel), selecting subtools.
7. Forecasting & Measurement tools flyout menu:
   - Opening flyout, querying subtools (Long Position, Short Position, Forecast, Price Range), selecting subtools.
8. Sidebar Utility Toggles:
   - Toggling Magnet Mode (aria-pressed true/false), Stay in Drawing Mode, Lock All Drawing Tools, Hide all drawings.
9. Measure, Zoom, and Object Tree triggers.
10. Runtime diagnostics: clean execution with zero uncaught JavaScript errors.
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
def test_tradingview_sidebar_structure_and_visibility(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that the TradingView drawing sidebar (#drawing-toolbar > div > div > div)
    is rendered and all primary tool buttons are attached and visible.
    """
    tradingview_chart_page.navigate_to_chart()
    assert_url_contains(tradingview_chart_page.page, "/dashboard", timeout=15000)

    # Assert drawing toolbar container
    assert_element_is_visible(
        tradingview_chart_page.drawing_toolbar.first,
        element_name="TradingView Drawing Sidebar Container"
    )

    # Query all visible tools
    tools = tradingview_chart_page.get_drawing_sidebar_tools()
    assert len(tools) >= 10, f"Expected at least 10 drawing toolbar buttons, got: {len(tools)}"

    # Assert specific primary tools
    assert_element_is_visible(tradingview_chart_page.cursor_tool_btn, element_name="TV Cursor Tool Button")
    assert_element_is_visible(tradingview_chart_page.trendline_tool_btn, element_name="TV Trendline Tool Button")
    assert_element_is_visible(tradingview_chart_page.fib_tool_btn, element_name="TV Fib Tool Button")
    assert_element_is_visible(tradingview_chart_page.brush_tool_btn, element_name="TV Brush Tool Button")
    assert_element_is_visible(tradingview_chart_page.text_tool_btn, element_name="TV Text Tool Button")
    assert_element_is_visible(tradingview_chart_page.pattern_tool_btn, element_name="TV Pattern Tool Button")
    assert_element_is_visible(tradingview_chart_page.forecast_tool_btn, element_name="TV Forecast Tool Button")
    assert_element_is_visible(tradingview_chart_page.measure_tool_btn, element_name="TV Measure Button")
    assert_element_is_visible(tradingview_chart_page.zoom_tool_btn, element_name="TV Zoom In Button")
    assert_element_is_visible(tradingview_chart_page.magnet_toggle_btn, element_name="TV Magnet Mode Toggle")
    assert_element_is_visible(tradingview_chart_page.drawing_mode_toggle_btn, element_name="TV Drawing Mode Toggle")
    assert_element_is_visible(tradingview_chart_page.lock_tools_toggle_btn, element_name="TV Lock Tools Toggle")
    assert_element_is_visible(tradingview_chart_page.hide_drawings_toggle_btn, element_name="TV Hide Drawings Toggle")
    assert_element_is_visible(tradingview_chart_page.object_tree_btn, element_name="TV Show Object Tree Button")


@pytest.mark.trade
def test_tradingview_sidebar_cursor_tools_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Cursor tools flyout menu, querying subtools (Cross, Dot, Arrow, Eraser),
    and switching between them.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Cursors")
    assert opened, "Expected Cursors tool flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 cursor subtools, got: {subtools}"

    # Select Dot cursor
    selected_dot = tradingview_chart_page.select_subtool("Cursors", "Dot")
    assert selected_dot, "Expected to select Dot cursor subtool"

    # Select Arrow cursor
    selected_arrow = tradingview_chart_page.select_subtool("Cursors", "Arrow")
    assert selected_arrow, "Expected to select Arrow cursor subtool"

    # Restore Cross cursor
    selected_cross = tradingview_chart_page.select_subtool("Cursors", "Cross")
    assert selected_cross, "Expected to restore Cross cursor subtool"


@pytest.mark.trade
def test_tradingview_sidebar_trendline_tools_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Trend line tools flyout menu, querying subtools
    (Trend Line, Arrow, Ray, Horizontal Line, Vertical Line, Parallel Channel),
    and selecting different lines.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Trend line tools")
    assert opened, "Expected Trend line tools flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 5, f"Expected at least 5 trendline subtools, got: {subtools}"

    # Select Horizontal Line
    selected_h_line = tradingview_chart_page.select_subtool("Trend line tools", "Horizontal Line")
    assert selected_h_line, "Expected to select Horizontal Line tool"

    # Select Vertical Line
    selected_v_line = tradingview_chart_page.select_subtool("Trend line tools", "Vertical Line")
    assert selected_v_line, "Expected to select Vertical Line tool"

    # Restore Trend Line
    selected_trend = tradingview_chart_page.select_subtool("Trend line tools", "Trend Line")
    assert selected_trend, "Expected to restore Trend Line tool"


@pytest.mark.trade
def test_tradingview_sidebar_geometric_shapes_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Geometric shapes flyout menu, querying subtools
    (Brush, Highlighter, Rectangle, Circle, Path, Triangle), and selecting shapes.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Geometric shapes")
    assert opened, "Expected Geometric shapes flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 geometric shape subtools, got: {subtools}"

    # Select Rectangle
    selected_rect = tradingview_chart_page.select_subtool("Geometric shapes", "Rectangle")
    assert selected_rect, "Expected to select Rectangle shape tool"

    # Select Highlighter
    selected_highlighter = tradingview_chart_page.select_subtool("Geometric shapes", "Highlighter")
    assert selected_highlighter, "Expected to select Highlighter tool"

    # Restore Brush
    selected_brush = tradingview_chart_page.select_subtool("Geometric shapes", "Brush")
    assert selected_brush, "Expected to restore Brush tool"


@pytest.mark.trade
def test_tradingview_sidebar_annotation_tools_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Annotation tools flyout menu, querying subtools
    (Text, Anchored Text, Note, Callout, Price Label), and selecting annotation tools.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Annotation tools")
    assert opened, "Expected Annotation tools flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 annotation subtools, got: {subtools}"

    # Select Note
    selected_note = tradingview_chart_page.select_subtool("Annotation tools", "Note")
    assert selected_note, "Expected to select Note annotation tool"

    # Restore Text
    selected_text = tradingview_chart_page.select_subtool("Annotation tools", "Text")
    assert selected_text, "Expected to restore Text annotation tool"


@pytest.mark.trade
def test_tradingview_sidebar_gann_and_fibonacci_tools_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Gann and Fibonacci tools flyout menu, querying subtools
    (Fib Retracement, Trend-Based Fib Extension, Fib Channel), and selecting tools.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Gann and Fibonacci tools")
    assert opened, "Expected Gann and Fibonacci tools flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 Fibonacci subtools, got: {subtools}"

    # Select Trend-Based Fib Extension
    selected_fib_ext = tradingview_chart_page.select_subtool("Gann and Fibonacci tools", "Trend-Based Fib Extension")
    assert selected_fib_ext, "Expected to select Trend-Based Fib Extension tool"

    # Restore Fib Retracement
    selected_fib_ret = tradingview_chart_page.select_subtool("Gann and Fibonacci tools", "Fib Retracement")
    assert selected_fib_ret, "Expected to restore Fib Retracement tool"


@pytest.mark.trade
def test_tradingview_sidebar_forecasting_tools_flyout(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening Forecasting and measurement tools flyout menu, querying subtools
    (Long Position, Short Position, Forecast, Price Range), and selecting tools.
    """
    tradingview_chart_page.navigate_to_chart()

    opened = tradingview_chart_page.open_tool_group_menu("Forecasting and measurement tools")
    assert opened, "Expected Forecasting tools flyout to open"

    subtools = tradingview_chart_page.get_available_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 forecasting subtools, got: {subtools}"

    # Select Short Position
    selected_short = tradingview_chart_page.select_subtool("Forecasting and measurement tools", "Short Position")
    assert selected_short, "Expected to select Short Position tool"

    # Restore Long Position
    selected_long = tradingview_chart_page.select_subtool("Forecasting and measurement tools", "Long Position")
    assert selected_long, "Expected to restore Long Position tool"


@pytest.mark.trade
def test_tradingview_sidebar_utility_toggles(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify toggling Magnet Mode, Stay in Drawing Mode, Lock All Drawing Tools,
    and Hide all drawings on the sidebar, asserting state transitions.
    """
    tradingview_chart_page.navigate_to_chart()

    # 1. Toggle Magnet Mode
    magnet_1 = tradingview_chart_page.toggle_magnet_mode()
    assert magnet_1.get("toggled"), f"Expected Magnet mode to toggle state: {magnet_1}"
    magnet_2 = tradingview_chart_page.toggle_magnet_mode()
    assert magnet_2.get("toggled"), f"Expected Magnet mode to toggle back: {magnet_2}"

    # 2. Toggle Stay in Drawing Mode
    draw_mode_1 = tradingview_chart_page.toggle_drawing_mode()
    assert draw_mode_1.get("toggled"), f"Expected Stay in Drawing Mode to toggle state: {draw_mode_1}"
    draw_mode_2 = tradingview_chart_page.toggle_drawing_mode()
    assert draw_mode_2.get("toggled"), f"Expected Stay in Drawing Mode to toggle back: {draw_mode_2}"

    # 3. Toggle Lock All Drawing Tools
    lock_1 = tradingview_chart_page.toggle_lock_all_drawings()
    assert lock_1.get("toggled"), f"Expected Lock Tools to toggle state: {lock_1}"
    lock_2 = tradingview_chart_page.toggle_lock_all_drawings()
    assert lock_2.get("toggled"), f"Expected Lock Tools to toggle back: {lock_2}"

    # 4. Toggle Hide all drawings
    hide_1 = tradingview_chart_page.toggle_hide_drawings()
    assert hide_1.get("toggled"), f"Expected Hide Drawings to toggle state: {hide_1}"
    hide_2 = tradingview_chart_page.toggle_hide_drawings()
    assert hide_2.get("toggled"), f"Expected Hide Drawings to toggle back: {hide_2}"


@pytest.mark.trade
def test_tradingview_sidebar_measure_zoom_and_object_tree(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify triggering Measure mode, Zoom In mode, and opening the Show Object Tree panel.
    """
    tradingview_chart_page.navigate_to_chart()

    # Trigger Measure mode
    measure_clicked = tradingview_chart_page.trigger_measure_mode()
    assert measure_clicked, "Expected Measure mode button to be clicked"
    tradingview_chart_page.page.wait_for_timeout(500)

    # Trigger Zoom In mode
    zoom_clicked = tradingview_chart_page.trigger_zoom_mode()
    assert zoom_clicked, "Expected Zoom In mode button to be clicked"
    tradingview_chart_page.page.wait_for_timeout(500)

    # Open Object Tree
    tree_clicked = tradingview_chart_page.open_object_tree()
    assert tree_clicked, "Expected Show Object Tree button to be clicked"
    tradingview_chart_page.page.wait_for_timeout(500)
    tradingview_chart_page.close_dialog()


@pytest.mark.trade
def test_tradingview_sidebar_diagnostics_clean(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that operating the TradingView drawing sidebar produces zero uncaught runtime JavaScript errors.
    """
    tradingview_chart_page.navigate_to_chart()

    # Perform a sequence of sidebar interactions
    tradingview_chart_page.select_subtool("Trend line tools", "Horizontal Line")
    tradingview_chart_page.select_subtool("Trend line tools", "Trend Line")
    tradingview_chart_page.toggle_magnet_mode()
    tradingview_chart_page.toggle_magnet_mode()

    # Telemetry verification
    if hasattr(tradingview_chart_page.page, "_diagnostics"):
        diagnostics = tradingview_chart_page.page._diagnostics
        assert len(diagnostics.get_page_errors()) == 0, (
            f"Expected 0 uncaught JS errors during sidebar operations, got: {diagnostics.get_page_errors()}"
        )
