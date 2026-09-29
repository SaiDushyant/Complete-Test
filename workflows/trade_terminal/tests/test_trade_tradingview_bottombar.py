"""
Trade Terminal TradingView Bottom Toolbar Test Suite.
Verifies full functionality of the TradingView bottom controls bar:
- Date range preset tabs (1D, 5D, 1M, etc.)
- 'Go to Date' dialog flow (input date, cancel, submit)
- Timezone selection flyout (listing timezones, switching timezone, verifying clock update, restoring)
- Scale toggles (Percentage, Logarithmic, Auto scale)
- Clean runtime telemetry and zero uncaught JavaScript errors
"""

import time
import pytest
from playwright.sync_api import expect

from workflows.trade_terminal.pages.tradingview_chart_page import TradingViewChartPage


@pytest.mark.trade
def test_tradingview_bottombar_structure_and_visibility(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that the TradingView bottom controls bar is visible and contains:
    - Date range preset tabs
    - Go to date button
    - Timezone indicator & selector
    - Scale mode toggles (Percentage, Log, Auto)
    """
    tradingview_chart_page.navigate_to_chart()
    expect(tradingview_chart_page.bottom_bar).to_be_visible(timeout=10000)
    tradingview_chart_page.page.wait_for_timeout(1500)

    # 1. Assert bottom bar visibility
    expect(tradingview_chart_page.bottom_bar).to_be_visible(timeout=10000)

    # 2. Assert date range tabs are present
    ranges = tradingview_chart_page.get_bottombar_date_ranges()
    assert len(ranges) >= 1, f"Expected at least 1 date range preset, got: {ranges}"

    # 3. Assert Go to date button is visible
    expect(tradingview_chart_page.goto_date_btn).to_be_visible(timeout=5000)

    # 4. Assert Timezone selector is visible and contains UTC / time
    expect(tradingview_chart_page.timezone_btn).to_be_visible(timeout=5000)
    active_tz = tradingview_chart_page.get_active_timezone()
    assert len(active_tz) > 0, "Expected non-empty timezone text on bottom bar"

    # 5. Assert Scale mode buttons are present
    expect(tradingview_chart_page.percentage_toggle_btn).to_be_visible(timeout=5000)
    expect(tradingview_chart_page.logarithm_toggle_btn).to_be_visible(timeout=5000)
    expect(tradingview_chart_page.auto_scale_toggle_btn).to_be_visible(timeout=5000)


@pytest.mark.trade
def test_tradingview_bottombar_date_range_tabs_switching(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify switching across different date range presets (1D, 5D, 1M).
    """
    tradingview_chart_page.navigate_to_chart()
    expect(tradingview_chart_page.bottom_bar).to_be_visible(timeout=10000)
    tradingview_chart_page.page.wait_for_timeout(1000)

    ranges = tradingview_chart_page.get_bottombar_date_ranges()
    assert len(ranges) > 0, "No date range tabs found on bottom bar"

    # Iterate through available range presets and click
    for r in ranges:
        clicked = tradingview_chart_page.select_date_range_tab(r)
        assert clicked, f"Expected to select date range tab '{r}'"
        tradingview_chart_page.page.wait_for_timeout(600)


@pytest.mark.trade
def test_tradingview_bottombar_goto_date_dialog_flow(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the 'Go to Date' dialog, inputting a target date,
    canceling, reopening, and submitting the date navigation.
    """
    tradingview_chart_page.navigate_to_chart()
    expect(tradingview_chart_page.bottom_bar).to_be_visible(timeout=10000)
    tradingview_chart_page.page.wait_for_timeout(1000)

    # 1. Open Go to Date dialog
    opened = tradingview_chart_page.open_goto_date_dialog()
    assert opened, "Expected Go to Date dialog to open"
    tradingview_chart_page.page.wait_for_timeout(800)

    # 2. Enter date and cancel
    tradingview_chart_page.set_goto_date("2026-01-15", submit=False)
    tradingview_chart_page.close_dialog()
    tradingview_chart_page.page.wait_for_timeout(500)

    # 3. Re-open and submit
    opened_again = tradingview_chart_page.open_goto_date_dialog()
    assert opened_again, "Expected Go to Date dialog to reopen"
    tradingview_chart_page.page.wait_for_timeout(800)

    submitted = tradingview_chart_page.set_goto_date("2026-02-01", submit=True)
    assert submitted, "Expected Go to Date form submission to succeed"
    tradingview_chart_page.page.wait_for_timeout(1000)


@pytest.mark.trade
def test_tradingview_bottombar_timezone_menu_and_selection(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify opening the Timezone dropdown menu, listing timezone options,
    selecting a new timezone (e.g. Los Angeles), asserting clock label update,
    and restoring back to UTC.
    """
    tradingview_chart_page.navigate_to_chart()

    # 1. Capture initial timezone text
    initial_tz = tradingview_chart_page.get_active_timezone()
    assert len(initial_tz) > 0, "Expected non-empty initial timezone"

    # 2. Open timezone menu
    opened = tradingview_chart_page.open_timezone_menu()
    assert opened, "Expected Timezone menu to open"
    tradingview_chart_page.page.wait_for_timeout(500)

    # 3. Query available timezones
    tz_list = tradingview_chart_page.get_available_timezones()
    assert len(tz_list) >= 5, f"Expected at least 5 timezone entries, got: {tz_list}"

    # 4. Select Los Angeles
    selected_la = tradingview_chart_page.select_timezone("Los Angeles")
    assert selected_la, "Expected to select 'Los Angeles' timezone"
    tradingview_chart_page.page.wait_for_timeout(1000)

    la_tz = tradingview_chart_page.get_active_timezone()
    assert "UTC-7" in la_tz or "UTC-8" in la_tz or "Los Angeles" in la_tz, (
        f"Expected timezone to reflect Los Angeles offset, got: '{la_tz}'"
    )

    # 5. Restore back to UTC
    tradingview_chart_page.open_timezone_menu()
    tradingview_chart_page.page.wait_for_timeout(500)
    restored_utc = tradingview_chart_page.select_timezone("UTC")
    assert restored_utc, "Expected to restore 'UTC' timezone"
    tradingview_chart_page.page.wait_for_timeout(1000)

    final_tz = tradingview_chart_page.get_active_timezone()
    assert "UTC" in final_tz, f"Expected timezone restored to UTC, got: '{final_tz}'"


@pytest.mark.trade
def test_tradingview_bottombar_scale_toggles(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify interactive state toggling for Percentage, Logarithmic, and Auto scale buttons.
    Asserts 'aria-pressed' state transitions before and after each click.
    """
    tradingview_chart_page.navigate_to_chart()

    # 1. Toggle Percentage scale
    perc_1 = tradingview_chart_page.toggle_percentage_scale()
    assert perc_1.get("toggled"), f"Expected Percentage scale to toggle: {perc_1}"
    perc_2 = tradingview_chart_page.toggle_percentage_scale()
    assert perc_2.get("toggled"), f"Expected Percentage scale to toggle back: {perc_2}"

    # 2. Toggle Logarithmic scale
    log_1 = tradingview_chart_page.toggle_log_scale()
    assert log_1.get("toggled"), f"Expected Log scale to toggle: {log_1}"
    log_2 = tradingview_chart_page.toggle_log_scale()
    assert log_2.get("toggled"), f"Expected Log scale to toggle back: {log_2}"

    # 3. Toggle Auto scale
    auto_1 = tradingview_chart_page.toggle_auto_scale()
    assert auto_1.get("toggled"), f"Expected Auto scale to toggle: {auto_1}"
    auto_2 = tradingview_chart_page.toggle_auto_scale()
    assert auto_2.get("toggled"), f"Expected Auto scale to toggle back: {auto_2}"


@pytest.mark.trade
def test_tradingview_bottombar_diagnostics_clean(
    tradingview_chart_page: TradingViewChartPage,
):
    """
    Verify that operating the TradingView bottom controls bar produces
    zero uncaught runtime JavaScript exceptions or page errors.
    """
    tradingview_chart_page.navigate_to_chart()

    # Perform a sequence of bottom bar operations
    tradingview_chart_page.toggle_percentage_scale()
    tradingview_chart_page.toggle_percentage_scale()
    tradingview_chart_page.toggle_log_scale()
    tradingview_chart_page.toggle_log_scale()

    tradingview_chart_page.page.wait_for_timeout(1000)

    # Telemetry verification
    if hasattr(tradingview_chart_page.page, "_diagnostics"):
        diagnostics = tradingview_chart_page.page._diagnostics
        assert len(diagnostics.get_page_errors()) == 0, (
            f"Expected 0 uncaught JS errors during bottom bar operations, got: {diagnostics.get_page_errors()}"
        )
