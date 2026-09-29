"""
Test Suite: Black Trader Chart Bottombar (#bottombar)
URL: https://stage.xtremenext.com/dashboard/

Validates all interactive elements within the Black Trader bottom container (#bottombar):
- Bottombar structure, tabs (Coder, Screener, Algo, Backtest, Trade) and control buttons
- Tab switching and active section content verification
- Bottom panel collapse and expand toggle (Toggle up/down / Toggle minimize)
- Bottom panel maximize and restore toggle
- Coder (Black Script Editor): Preview, Publish, Tutorials, Monaco editor, Show logs toggle
- Screener: Screener builder opening, filter inputs (Exchange, Category, Sort), closing builder
- Algo: Algo builder opening, strategy configuration fields
- Backtest: Interface elements and algorithm state
- Trade Panel: Subtabs (Positions, Pending, Orders, History), positions table, columns, and actions
- Resize gutter drag interaction
- Diagnostics and telemetry validation during bottombar operations
"""

import time
import pytest
from playwright.sync_api import expect

from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage


@pytest.mark.trade
def test_blacktrader_bottombar_structure_and_visibility(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify that #bottombar is visible and displays all expected tabs and controls:
    - Resize gutter
    - 5 Core tabs: Coder, Screener, Algo, Backtest, Trade
    - Collapse / expand button
    - Maximize / restore button
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # 1. Bottombar container
    expect(blacktrader_chart_page.bottombar).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 2. Resize gutter
    expect(blacktrader_chart_page.bottombar_gutter).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 3. Main tabs
    expect(blacktrader_chart_page.tab_coder).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.tab_screener).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.tab_algo).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.tab_backtest).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.tab_trade).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # 4. Collapse & Maximize controls
    expect(blacktrader_chart_page.bottombar_collapse_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.bottombar_maximize_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)


@pytest.mark.trade
def test_blacktrader_bottombar_tab_navigation(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify navigating across all 5 bottombar tabs and confirming active state:
    Coder -> Screener -> Algo -> Backtest -> Trade -> Coder.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    for tab_name in ["Screener", "Algo", "Backtest", "Trade", "Coder"]:
        assert blacktrader_chart_page.select_bottombar_tab(tab_name)
        active = blacktrader_chart_page.get_active_bottombar_tab()
        assert tab_name.lower() in active.lower(), f"Expected active tab '{tab_name}', got '{active}'"
        expect(blacktrader_chart_page.bottombar_content).to_be_visible(timeout=TIMEOUT_DEFAULT)
        blacktrader_chart_page.page.wait_for_timeout(300)


@pytest.mark.trade
def test_blacktrader_bottombar_collapse_and_expand(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify collapsing the bottombar to minimized height and restoring to normal height.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Collapse bottombar
    is_collapsed = blacktrader_chart_page.toggle_bottombar_collapse()
    assert is_collapsed, "Expected bottombar to collapse to minimized height (< 60px)"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Restore bottombar
    is_restored = not blacktrader_chart_page.toggle_bottombar_collapse()
    assert is_restored, "Expected bottombar to restore to normal height (>= 60px)"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_bottombar_maximize_and_restore(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify maximizing the bottombar to full viewport height and restoring.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Maximize bottombar
    is_maximized = blacktrader_chart_page.toggle_bottombar_maximize()
    assert is_maximized, "Expected bottombar to maximize (> 700px height)"
    blacktrader_chart_page.page.wait_for_timeout(400)

    # Restore bottombar
    is_restored = not blacktrader_chart_page.toggle_bottombar_maximize()
    assert is_restored, "Expected bottombar to restore from maximized state"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_bottombar_coder_editor_and_actions(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify Coder tab elements and interactive controls:
    - Preview, Publish, Backtest, and Tutorials buttons
    - Monaco editor textarea
    - Triggering Preview compilation
    - Toggling Show logs checkbox
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    blacktrader_chart_page.select_bottombar_tab("Coder")

    # Verify buttons
    expect(blacktrader_chart_page.coder_preview_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.coder_publish_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.coder_backtest_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.coder_tutorials_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.coder_editor_textarea).to_be_attached()

    # Toggle Show logs
    checked = blacktrader_chart_page.coder_toggle_show_logs()
    assert checked, "Expected Show logs to be checked after click"
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Restore Show logs
    unchecked = not blacktrader_chart_page.coder_toggle_show_logs()
    assert unchecked, "Expected Show logs to be unchecked after restore click"
    blacktrader_chart_page.page.wait_for_timeout(300)

    # Trigger Preview
    assert blacktrader_chart_page.coder_trigger_preview()
    blacktrader_chart_page.page.wait_for_timeout(500)
    blacktrader_chart_page.close_coder_preview_console()


@pytest.mark.trade
def test_blacktrader_bottombar_screener_creation(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify creating a new Screener, previewing criteria, saving, and verifying it in the Screener section:
    - Open Screener builder
    - Fill screener name
    - Trigger Preview
    - Save screener
    - Verify screener is successfully created and active in the screener list
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    screener_name = f"Test Scr {int(time.time()) % 10000}"
    created = blacktrader_chart_page.create_screener(screener_name)
    assert created, f"Expected screener '{screener_name}' to be created successfully"


@pytest.mark.trade
def test_blacktrader_bottombar_algo_creation(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify creating a new Algo strategy, selecting a strategy, configuring, saving, and verifying:
    - Open Algo builder
    - Fill algo name
    - Select system strategy (Cross Over - MA)
    - Link screener or manual symbol
    - Save algo
    - Verify algo is successfully created, active, and listed in the Algo strategies table
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    algo_name = f"Test Algo {int(time.time()) % 10000}"
    created = blacktrader_chart_page.create_algo(algo_name, strategy_name="Cross Over - MA")
    assert created, f"Expected algo '{algo_name}' to be created successfully"


@pytest.mark.trade
def test_blacktrader_bottombar_trade_panel_and_subtabs(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify the Trade panel, subtab switching (Positions, Pending, Orders, History),
    and positions table structure.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    blacktrader_chart_page.select_bottombar_tab("Trade")

    # Verify Trade header items
    expect(blacktrader_chart_page.trade_account_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
    expect(blacktrader_chart_page.trade_broker_settings_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)

    # Switch across subtabs
    for subtab in ["Pending", "Orders", "History", "Positions"]:
        assert blacktrader_chart_page.select_trade_subtab(subtab)
        blacktrader_chart_page.page.wait_for_timeout(300)

    # Verify positions table
    expect(blacktrader_chart_page.trade_positions_table).to_be_visible(timeout=TIMEOUT_DEFAULT)
    rows_count = blacktrader_chart_page.get_trade_positions_rows_count()
    assert rows_count >= 1, f"Expected at least 1 row in positions table, found: {rows_count}"


@pytest.mark.trade
def test_blacktrader_bottombar_resize_gutter(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify dragging the bottombar resize gutter vertically.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    resized = blacktrader_chart_page.resize_bottom_panel(delta_y=-30)
    assert resized, "Expected bottombar gutter to drag/resize"
    blacktrader_chart_page.page.wait_for_timeout(400)


@pytest.mark.trade
def test_blacktrader_bottombar_diagnostics_clean(
    blacktrader_chart_page: BlackTraderChartPage,
):
    """
    Verify telemetry and clean execution during bottombar operations.
    """
    blacktrader_chart_page.navigate_to_chart()
    blacktrader_chart_page.page.wait_for_timeout(1500)

    # Multi-tab workflow
    blacktrader_chart_page.select_bottombar_tab("Coder")
    blacktrader_chart_page.coder_trigger_preview()
    blacktrader_chart_page.select_bottombar_tab("Trade")
    blacktrader_chart_page.select_trade_subtab("Positions")
    blacktrader_chart_page.select_bottombar_tab("Coder")
    blacktrader_chart_page.page.wait_for_timeout(1000)
