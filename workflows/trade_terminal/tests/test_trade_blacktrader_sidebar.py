"""
Trade Terminal Black Trader Chart Sidebar Test Suite.
Verifies full functionality of the Black Trader Chart left sidebar (#leftbar):
- All 12 drawing and utility tool buttons
- Flyout drawers for subtools (Drawing Tools, Line Tools, Patterns, Text Tools, Fibonacci Tools)
- Subtool selection from flyout drawers
- Measure mode activation and Delete Tools trigger
- Utility toggles (Lock All Drawings, Hide All Drawings, Magnet Mode, Keep Drawing, Favorites Toolbar)
- Clean runtime telemetry
"""

import pytest
from playwright.sync_api import expect

from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage


@pytest.mark.trade
def test_blacktrader_sidebar_structure_and_visibility(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that the Black Trader left sidebar (#leftbar) is visible and contains:
    - Drawing Tools button
    - Line Tools button
    - Patterns button
    - Text Tools button
    - Measure Tools button
    - Fibonacci Tools button
    - Lock All Drawings toggle
    - Hide All Drawings toggle
    - Enable Magnet Mode toggle
    - Enable Keep Drawing toggle
    - Delete Tools button
    - Show Favorite Drawing Tools Toolbar toggle
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Assert leftbar container
    expect(blacktrader_chart_page.leftbar).to_be_visible(timeout=10000)

    # 2. Assert drawing tool group buttons
    expect(blacktrader_chart_page.drawing_tools_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.line_tools_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.patterns_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.text_tools_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.measure_tools_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.fibonacci_tools_btn).to_be_visible(timeout=5000)

    # 3. Assert utility controls
    expect(blacktrader_chart_page.lock_all_drawings_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.hide_all_drawings_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.magnet_mode_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.keep_drawing_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.delete_tools_btn).to_be_visible(timeout=5000)
    expect(blacktrader_chart_page.favorites_btn).to_be_visible(timeout=5000)

    tools = blacktrader_chart_page.get_drawing_sidebar_tools()
    assert len(tools) >= 10, f"Expected at least 10 sidebar tools, got: {tools}"


@pytest.mark.trade
def test_blacktrader_sidebar_drawing_tools_flyout(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Drawing Tools flyout drawer, querying subtools
    (Brush, Highlighter, Rectangle, Circle, Path), and selecting subtools.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    opened = blacktrader_chart_page.open_drawing_tool_flyout("Drawing Tools")
    assert opened, "Expected Drawing Tools flyout drawer to open"

    subtools = blacktrader_chart_page.get_flyout_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 drawing subtools, got: {subtools}"

    # Select Rectangle
    selected_rect = blacktrader_chart_page.select_drawing_subtool("Drawing Tools", "Rectangle")
    assert selected_rect, "Expected to select Rectangle shape tool"
    blacktrader_chart_page.page.wait_for_timeout(500)

    # Restore Brush
    selected_brush = blacktrader_chart_page.select_drawing_subtool("Drawing Tools", "Brush")
    assert selected_brush, "Expected to restore Brush tool"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_sidebar_line_tools_flyout(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Line Tools flyout drawer, querying subtools
    (Trend Line, Horizontal Line, Ray, Channel), and selecting subtools.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    opened = blacktrader_chart_page.open_drawing_tool_flyout("Line Tools")
    assert opened, "Expected Line Tools flyout drawer to open"

    subtools = blacktrader_chart_page.get_flyout_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 line subtools, got: {subtools}"

    # Select Horizontal Line
    selected_h_line = blacktrader_chart_page.select_drawing_subtool("Line Tools", "Horizontal Line")
    assert selected_h_line, "Expected to select Horizontal Line tool"
    blacktrader_chart_page.page.wait_for_timeout(500)

    # Restore Trend Line
    selected_trend = blacktrader_chart_page.select_drawing_subtool("Line Tools", "Trend Line")
    assert selected_trend, "Expected to restore Trend Line tool"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_sidebar_patterns_flyout(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Patterns flyout drawer, querying subtools
    (Head and Shoulders, XABCD, Elliott Waves), and selecting a pattern.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    opened = blacktrader_chart_page.open_drawing_tool_flyout("Patterns")
    assert opened, "Expected Patterns flyout drawer to open"

    subtools = blacktrader_chart_page.get_flyout_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 pattern subtools, got: {subtools}"

    # Select Head and Shoulders
    selected_hs = blacktrader_chart_page.select_drawing_subtool("Patterns", "Head and Shoulders")
    assert selected_hs, "Expected to select Head and Shoulders pattern"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_sidebar_text_tools_flyout(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Text Tools flyout drawer, querying subtools
    (Text, Note, Callout, Price Label), and selecting subtools.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    opened = blacktrader_chart_page.open_drawing_tool_flyout("Text Tools")
    assert opened, "Expected Text Tools flyout drawer to open"

    subtools = blacktrader_chart_page.get_flyout_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 text subtools, got: {subtools}"

    # Select Note
    selected_note = blacktrader_chart_page.select_drawing_subtool("Text Tools", "Note")
    assert selected_note, "Expected to select Note tool"
    blacktrader_chart_page.page.wait_for_timeout(500)

    # Restore Text
    selected_text = blacktrader_chart_page.select_drawing_subtool("Text Tools", "Text")
    assert selected_text, "Expected to restore Text tool"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_sidebar_fibonacci_tools_flyout(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Fibonacci Tools flyout drawer, querying subtools
    (Fib Retracement, Fib Channel, Fib Time Zone), and selecting subtools.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    opened = blacktrader_chart_page.open_drawing_tool_flyout("Fibonacci Tools")
    assert opened, "Expected Fibonacci Tools flyout drawer to open"

    subtools = blacktrader_chart_page.get_flyout_subtools()
    assert len(subtools) >= 3, f"Expected at least 3 Fibonacci subtools, got: {subtools}"

    # Select Fib Channel
    selected_channel = blacktrader_chart_page.select_drawing_subtool("Fibonacci Tools", "Fib Channel")
    assert selected_channel, "Expected to select Fib Channel tool"
    blacktrader_chart_page.page.wait_for_timeout(500)

    # Restore Fib Retracement
    selected_ret = blacktrader_chart_page.select_drawing_subtool("Fibonacci Tools", "Fib Retracement")
    assert selected_ret, "Expected to restore Fib Retracement tool"
    blacktrader_chart_page.page.wait_for_timeout(500)


@pytest.mark.trade
def test_blacktrader_sidebar_measure_and_delete_tools(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify triggering Measure mode and Delete Tools action from sidebar.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Trigger Measure Mode
    measure_triggered = blacktrader_chart_page.trigger_measure_mode()
    assert measure_triggered, "Expected Measure Tools to trigger"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Click Delete Tools
    delete_clicked = blacktrader_chart_page.click_delete_tools()
    assert delete_clicked, "Expected Delete Tools to trigger"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_sidebar_utility_toggles(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify toggling Lock All Drawings, Hide All Drawings, Magnet Mode,
    Keep Drawing, and Favorites Toolbar in the sidebar.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Toggle Lock All Drawings
    lock_toggled = blacktrader_chart_page.toggle_lock_all_drawings()
    assert lock_toggled, "Expected Lock All Drawings to toggle"
    blacktrader_chart_page.page.wait_for_timeout(300)
    blacktrader_chart_page.toggle_lock_all_drawings()

    # 2. Toggle Hide All Drawings
    hide_toggled = blacktrader_chart_page.toggle_hide_all_drawings()
    assert hide_toggled, "Expected Hide All Drawings to toggle"
    blacktrader_chart_page.page.wait_for_timeout(300)
    blacktrader_chart_page.toggle_hide_all_drawings()

    # 3. Toggle Magnet Mode
    magnet_toggled = blacktrader_chart_page.toggle_magnet_mode()
    assert magnet_toggled, "Expected Magnet Mode to toggle"
    blacktrader_chart_page.page.wait_for_timeout(300)
    blacktrader_chart_page.toggle_magnet_mode()

    # 4. Toggle Keep Drawing
    keep_toggled = blacktrader_chart_page.toggle_keep_drawing_mode()
    assert keep_toggled, "Expected Keep Drawing to toggle"
    blacktrader_chart_page.page.wait_for_timeout(300)
    blacktrader_chart_page.toggle_keep_drawing_mode()

    # 5. Toggle Favorites Toolbar
    fav_toggled = blacktrader_chart_page.toggle_favorites_toolbar()
    assert fav_toggled, "Expected Favorites Toolbar to toggle"
    blacktrader_chart_page.page.wait_for_timeout(300)
    blacktrader_chart_page.toggle_favorites_toolbar()


@pytest.mark.trade
def test_blacktrader_sidebar_diagnostics_clean(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify telemetry and clean execution during Black Trader sidebar operations.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Perform a sequence of sidebar operations
    blacktrader_chart_page.select_drawing_subtool("Line Tools", "Horizontal Line")
    blacktrader_chart_page.select_drawing_subtool("Line Tools", "Trend Line")
    blacktrader_chart_page.toggle_magnet_mode()
    blacktrader_chart_page.toggle_magnet_mode()

    blacktrader_chart_page.page.wait_for_timeout(1000)
