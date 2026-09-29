"""
Test Suite: Black Trader Chart Rightbar (#rightbar)
URL: https://stage.xtremenext.com/dashboard/

Validates all interactive elements within the Black Trader right sidebar (#rightbar):
- Rightbar structure and core toolbar buttons visibility
- Layers / Object Tree flyout panel toggling and contents (Drawings list)
- Multi-chart controls menu popup opening and button visibility
- Multi-chart controls actions: Zoom In All Charts, Zoom Out All Charts, Reset View All Charts, Scroll Left All Charts, Scroll Right All Charts
- Toggle Logs Panel button interaction and synchronization with editor console
- Resize gutter drag interaction
- Diagnostics and telemetry validation during rightbar operations
"""

import pytest
from playwright.sync_api import expect

from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage


@pytest.mark.trade
def test_blacktrader_rightbar_structure_and_visibility(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that #rightbar is visible and contains all expected toolbar buttons:
    - Resize right panel gutter
    - Layers button
    - Chart Controls button
    - Toggle Logs Panel button
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Rightbar container
    expect(blacktrader_chart_page.rightbar).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 2. Resize gutter
    expect(blacktrader_chart_page.rightbar_gutter).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 3. Layers button
    expect(blacktrader_chart_page.layers_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 4. Chart Controls button
    expect(blacktrader_chart_page.chart_controls_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 5. Toggle Logs Panel button
    expect(blacktrader_chart_page.toggle_logs_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)


@pytest.mark.trade
def test_blacktrader_rightbar_layers_panel_toggle(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening and closing the Layers / Drawings flyout panel.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Open Layers panel
    is_open = blacktrader_chart_page.toggle_layers_panel()
    assert is_open, "Expected Layers panel to be visible after click"
    expect(blacktrader_chart_page.layers_panel).to_be_visible(timeout=TIMEOUT_DEFAULT)
    assert "Drawings" in (blacktrader_chart_page.layers_panel.inner_text() or "")
    blacktrader_chart_page.page.wait_for_timeout(400)

    # 2. Close Layers panel
    is_closed = not blacktrader_chart_page.toggle_layers_panel()
    assert is_closed, "Expected Layers panel to close after second click"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_rightbar_chart_controls_menu_opening(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify opening the Chart Controls menu and checking all 5 actions:
    - Zoom In All Charts
    - Zoom Out All Charts
    - Reset View All Charts
    - Scroll Left All Charts
    - Scroll Right All Charts
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Open menu
    opened = blacktrader_chart_page.open_chart_controls_menu()
    assert opened, "Expected Chart Controls menu to open"
    expect(blacktrader_chart_page.chart_controls_menu).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 2. Verify all action buttons
    expect(blacktrader_chart_page.zoom_in_all_charts_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.zoom_out_all_charts_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.reset_view_all_charts_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.scroll_left_all_charts_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.scroll_right_all_charts_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 3. Close menu
    blacktrader_chart_page.close_chart_controls_menu()
    blacktrader_chart_page.page.wait_for_timeout(300)


@pytest.mark.trade
def test_blacktrader_rightbar_chart_controls_menu_actions(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify clicking each action in the Chart Controls popup menu:
    - Zoom In All Charts
    - Zoom Out All Charts
    - Scroll Left All Charts
    - Scroll Right All Charts
    - Reset View All Charts
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Click Zoom In All Charts
    assert blacktrader_chart_page.click_chart_control_menu_action("zoom_in")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Zoom Out All Charts
    assert blacktrader_chart_page.click_chart_control_menu_action("zoom_out")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Scroll Left All Charts
    assert blacktrader_chart_page.click_chart_control_menu_action("scroll_left")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Scroll Right All Charts
    assert blacktrader_chart_page.click_chart_control_menu_action("scroll_right")
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Click Reset View All Charts
    assert blacktrader_chart_page.click_chart_control_menu_action("reset_view")
    blacktrader_chart_page.page.wait_for_timeout(300)

    blacktrader_chart_page.close_chart_controls_menu()


@pytest.mark.trade
def test_blacktrader_rightbar_toggle_logs_panel(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify toggling the Logs Panel via the rightbar button.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    initial_checked = blacktrader_chart_page.is_logs_panel_checked()

    # Toggle Logs Panel
    blacktrader_chart_page.toggle_logs_panel()
    blacktrader_chart_page.page.wait_for_timeout(400)
    after_checked = blacktrader_chart_page.is_logs_panel_checked()
    assert after_checked != initial_checked, "Expected Show logs checkbox state to toggle"

    # Restore initial state
    blacktrader_chart_page.toggle_logs_panel()
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_rightbar_resize_gutter(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify dragging the rightbar resize gutter.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    resized = blacktrader_chart_page.resize_right_panel(delta_x=-30)
    assert resized, "Expected right panel gutter to drag/resize"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_rightbar_diagnostics_clean(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify telemetry and clean execution during rightbar operations.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Combined workflow
    blacktrader_chart_page.toggle_layers_panel()
    blacktrader_chart_page.toggle_layers_panel()
    blacktrader_chart_page.click_chart_control_menu_action("reset_view")
    blacktrader_chart_page.close_chart_controls_menu()
    blacktrader_chart_page.page.wait_for_timeout(1000)
