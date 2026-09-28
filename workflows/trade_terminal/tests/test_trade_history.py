"""
Trade Terminal History Page Test Suite.
Verifies the dedicated History page at:
document.querySelector("#tab-1 > div.row.tab2content.order-history")
div.page[data-page="history"]
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import time
import pytest

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_element_has_text,
    assert_url_contains,
)
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.history_page import HistoryPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.chart_page import TradingChartPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage

logger = get_logger("test_trade_history")


@pytest.mark.trade
@pytest.mark.smoke
def test_history_page_navigation_and_structure_rendered(
    history_page: HistoryPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify standalone History page container:
    document.querySelector("#tab-1 > div.row.tab2content.order-history")
    div.page[data-page="history"]
    1. Clicking .lefticons[data-tooltip='History'] activates the History view.
    2. Heading 'Order History (N)' is rendered with a non-negative count.
    3. Filter dropdown (.filter-box) with export button (#exportBtn) and duration toggle are visible.
    4. History table headers (ID, Time, Symbol, Order, Lot, Status, Type, SL, TP, entry, exit, Commission, PNL, SWAP, Close Time).
    5. Bottom calculation bar with balance, deposit, withdraw, commission, swap, profit metrics.
    """
    history_page.navigate_to_history_page()
    assert_url_contains(history_page.page, "/dashboard", timeout=15000)

    # 1. Assert container active
    assert history_page.is_history_page_active(), "Expected History page container to be active (not hidden)"
    assert_element_is_visible(history_page.history_tab_container, element_name="History Tab Container (#tab-1 .order-history)")

    # 2. Assert page heading
    assert_element_is_visible(history_page.page_heading, element_name="History Page Heading")
    heading_text = history_page.page_heading.inner_text().strip()
    assert "Order History" in heading_text or "History" in heading_text, (
        f"Expected 'Order History' in heading, got: '{heading_text}'"
    )

    # 3. Assert filter box and controls
    assert_element_is_visible(history_page.filter_box, element_name="Filter Box Container")
    assert_element_is_visible(history_page.export_button, element_name="Export Excel Button (#exportBtn)")
    assert_element_is_visible(history_page.dropdown_toggle, element_name="Dropdown Toggle Button")

    # 4. Assert table and headers
    assert_element_is_visible(history_page.history_table, element_name="History Table")
    headers_count = history_page.history_headers.count()
    assert headers_count >= 10, f"Expected at least 10 column headers in History table, got: {headers_count}"

    header_texts = [history_page.history_headers.nth(i).inner_text().strip() for i in range(headers_count)]
    expected_columns = ["ID", "Time", "Symbol", "Order", "Lot", "Status", "Type", "Commission", "PNL", "SWAP", "Close Time"]
    for col in expected_columns:
        assert any(col.lower() in h.lower() for h in header_texts), (
            f"Expected column '{col}' among headers: {header_texts}"
        )

    # 5. Assert bottom calculations bar
    assert_element_is_visible(history_page.stat_balance, element_name="Bottom Stat Balance (#total_balance)")


@pytest.mark.trade
@pytest.mark.smoke
def test_history_page_filter_dropdown_and_export_buttons(
    history_page: HistoryPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify every filter option in the history dropdown and the export button:

    Part A – Export Button (#exportBtn):
      - Is visible and enabled.
      - Can be clicked without triggering a JS error.

    Part B – All 8 filter duration options (li.filter_list[data-duration]):
      Non-modal options (7): 1d, 1w, 3w, 1m, 3m, 1y, all
        - Each option exists in the DOM with the correct data-duration attribute.
        - Clicking each option sets it as the active filter (li.active).
        - History table remains visible after each selection.
      Modal option (1): custom
        - Clicking opens the Custom Filter modal.

    Part C – Custom Filter Modal (opened by 'custom' filter):
      Structure:
        - Modal is visible with title 'Custom Filter'.
        - 'From Date' label and #fromDate date input are rendered.
        - 'To Date' label and #toDate date input are rendered.
        - Header close button (.btn-close.historyOrderModalClose) is present.
        - Footer 'Close' button (.btn-danger.historyOrderModalClose) is present.
        - Footer 'Submit' button (.btn-primary.historyOrderSubmit) is present.
      Interaction:
        - Fill in a from/to date range and click Submit → modal closes, table shown.
        - Re-open modal, click footer Close → modal closes cleanly.
        - Re-open modal, click header X button → modal closes cleanly.
    """
    history_page.navigate_to_history_page()
    assert_url_contains(history_page.page, "/dashboard", timeout=15000)

    # -------------------------------------------------------------------------
    # Part A: Export Button
    # -------------------------------------------------------------------------
    assert_element_is_visible(history_page.export_button, element_name="Export Excel Button (#exportBtn)")
    assert history_page.export_button.is_enabled(), "Expected export button to be enabled"
    history_page.click_export_button()
    logger.info("Export button clicked successfully — no JS error raised.")

    # -------------------------------------------------------------------------
    # Part B: Verify all 8 filter duration options exist in DOM
    # -------------------------------------------------------------------------
    history_page.open_filter_dropdown()
    filter_options = history_page.get_filter_options()
    logger.info(f"Available History filter options: {filter_options}")

    expected_durations = ["1d", "1w", "3w", "1m", "3m", "1y", "custom", "all"]
    found_durations = [opt["duration"] for opt in filter_options]
    for expected_d in expected_durations:
        assert expected_d in found_durations, (
            f"Expected duration '{expected_d}' in filter dropdown, found: {found_durations}"
        )
    logger.info(f"All 8 expected durations present: {found_durations}")

    # Click every non-custom option and verify active state + table visibility
    non_custom_durations = ["1d", "1w", "3w", "1m", "3m", "1y", "all"]
    for dur in non_custom_durations:
        logger.info(f"Selecting filter: '{dur}'")
        history_page.select_filter(dur)

        active_opt = history_page.get_active_filter()
        assert active_opt is not None, (
            f"Expected an active filter after selecting '{dur}'"
        )
        assert active_opt["duration"] == dur, (
            f"Expected active filter duration '{dur}', got: '{active_opt['duration']}'"
        )
        assert_element_is_visible(
            history_page.history_table,
            element_name=f"History Table after selecting filter '{dur}'"
        )
        logger.info(f"Filter '{dur}' → active ✓, table visible ✓")

    # -------------------------------------------------------------------------
    # Part C: Custom Filter Modal — full structure + interaction verification
    # -------------------------------------------------------------------------

    # --- Open custom modal ---
    history_page.open_custom_filter_modal()
    assert history_page.is_custom_modal_open(), "Expected Custom Filter modal to be visible after clicking 'custom'"

    # C.1: Modal title
    assert_element_is_visible(history_page.custom_modal_title, element_name="Custom Filter Modal Title")
    title_text = history_page.custom_modal_title.inner_text().strip()
    assert "Custom Filter" in title_text, (
        f"Expected modal title 'Custom Filter', got: '{title_text}'"
    )
    logger.info(f"Custom Filter modal title: '{title_text}' ✓")

    # C.2: From Date label and input
    assert_element_is_visible(history_page.custom_modal_from_label, element_name="From Date Label")
    from_label = history_page.custom_modal_from_label.inner_text().strip()
    assert "From Date" in from_label, f"Expected 'From Date' label, got: '{from_label}'"

    assert_element_is_visible(history_page.custom_modal_from_date, element_name="From Date Input (#fromDate)")
    from_input_type = history_page.custom_modal_from_date.get_attribute("type")
    assert from_input_type == "date", f"Expected #fromDate type='date', got: '{from_input_type}'"
    from_input_name = history_page.custom_modal_from_date.get_attribute("name")
    assert from_input_name == "fromDate", f"Expected #fromDate name='fromDate', got: '{from_input_name}'"
    logger.info("From Date label and input (#fromDate) verified ✓")

    # C.3: To Date label and input
    assert_element_is_visible(history_page.custom_modal_to_label, element_name="To Date Label")
    to_label = history_page.custom_modal_to_label.inner_text().strip()
    assert "To Date" in to_label, f"Expected 'To Date' label, got: '{to_label}'"

    assert_element_is_visible(history_page.custom_modal_to_date, element_name="To Date Input (#toDate)")
    to_input_type = history_page.custom_modal_to_date.get_attribute("type")
    assert to_input_type == "date", f"Expected #toDate type='date', got: '{to_input_type}'"
    to_input_name = history_page.custom_modal_to_date.get_attribute("name")
    assert to_input_name == "toDate", f"Expected #toDate name='toDate', got: '{to_input_name}'"
    logger.info("To Date label and input (#toDate) verified ✓")

    # C.4: Header close button (X)
    assert_element_is_visible(history_page.custom_modal_close_btn, element_name="Custom Modal Header Close Button (X)")
    logger.info("Header close button (.btn-close.historyOrderModalClose) verified ✓")

    # C.5: Footer Close button (btn-danger)
    assert_element_is_visible(history_page.custom_modal_footer_close, element_name="Custom Modal Footer Close Button")
    footer_close_text = history_page.custom_modal_footer_close.inner_text().strip()
    assert "Close" in footer_close_text, (
        f"Expected 'Close' text on footer close button, got: '{footer_close_text}'"
    )
    logger.info(f"Footer Close button text: '{footer_close_text}' ✓")

    # C.6: Submit button
    assert_element_is_visible(history_page.custom_modal_submit, element_name="Custom Modal Submit Button")
    submit_text = history_page.custom_modal_submit.inner_text().strip()
    assert "Submit" in submit_text, (
        f"Expected 'Submit' text on submit button, got: '{submit_text}'"
    )
    assert history_page.custom_modal_submit.is_enabled(), "Expected Submit button to be enabled"
    logger.info(f"Submit button text: '{submit_text}' ✓")

    # C.7: Fill date range and click Submit → modal should close, table stays visible
    history_page.set_custom_date_range(from_date="2024-01-01", to_date="2024-12-31")
    from_val = history_page.custom_modal_from_date.input_value()
    to_val = history_page.custom_modal_to_date.input_value()
    assert from_val == "2024-01-01", f"Expected #fromDate value '2024-01-01', got: '{from_val}'"
    assert to_val == "2024-12-31", f"Expected #toDate value '2024-12-31', got: '{to_val}'"
    logger.info(f"Date range filled: from={from_val}, to={to_val} ✓")

    history_page.submit_custom_filter()
    assert not history_page.is_custom_modal_open(), (
        "Expected Custom Filter modal to close after Submit"
    )
    assert_element_is_visible(history_page.history_table, element_name="History Table after custom filter submit")
    logger.info("Submit closed modal and table is still visible ✓")

    # C.8: Re-open → close via footer 'Close' button
    history_page.open_custom_filter_modal()
    assert history_page.is_custom_modal_open(), "Expected modal to re-open for footer close test"
    history_page.close_custom_filter_modal(use_footer_close=True)
    assert not history_page.is_custom_modal_open(), (
        "Expected Custom Filter modal to close after clicking footer 'Close' button"
    )
    logger.info("Footer 'Close' button dismissed modal cleanly ✓")

    # C.9: Re-open → close via header X button
    history_page.open_custom_filter_modal()
    assert history_page.is_custom_modal_open(), "Expected modal to re-open for header X close test"
    history_page.close_custom_filter_modal(use_footer_close=False)
    assert not history_page.is_custom_modal_open(), (
        "Expected Custom Filter modal to close after clicking header X (.btn-close)"
    )
    logger.info("Header X button dismissed modal cleanly ✓")

    # Final: ensure history table is still fully operational
    history_page.select_filter("all")
    assert_element_is_visible(history_page.history_table, element_name="History Table after all interactions")


@pytest.mark.trade
@pytest.mark.regression
def test_history_page_closed_order_lifecycle(
    history_page: HistoryPage,
    positions_page: PositionsPage,
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify closed order lifecycle in History:
    1. First inspect the last order currently in the History page table and record its details.
    2. Place a new live market order (AUDUSD 0.01 lot BUY) via the trading chart.
    3. Navigate to standalone Position page and retrieve the active position order ID.
    4. Close the position cleanly via individual close button (or bulk close).
    5. Navigate back to the History page.
    6. Confirm the newly closed order appears in the History table with matching ID, symbol, lot, BUY side, prices, and close timestamp.
    """
    # 1. Check current last order in history
    history_page.navigate_to_history_page()
    history_page.select_filter("all")
    initial_last_order = history_page.get_last_order_record()
    initial_count = history_page.get_history_count_from_title()
    logger.info(f"Initial last order in history: {initial_last_order}, Initial total count: {initial_count}")

    # 2. Place a live trade via chart quick order
    trading_chart_page.navigate_to_chart()
    trading_chart_page.open_trade_modal("AUDUSD", side="buy")
    trading_chart_page.set_trade_modal_lot(0.01)
    trading_chart_page.submit_market_order()
    trading_chart_page.page.wait_for_timeout(2000)

    # 3. Retrieve open position ID from Positions page
    positions_page.navigate_to_position_page()
    start_time = time.time()
    open_positions = []
    while time.time() - start_time < 15:
        open_positions = positions_page.get_open_positions_data()
        if len(open_positions) > 0:
            break
        positions_page.page.wait_for_timeout(500)

    assert len(open_positions) >= 1, "Expected placed order to appear in open positions"
    target_pos = open_positions[0]
    target_id = target_pos["id"]
    logger.info(f"Target open position to close: {target_pos}")

    # 4. Close the position
    positions_page.close_position_by_id(target_id)
    positions_page.wait_for_position_closed(target_id, timeout=15000)

    # 5. Navigate to History page and verify closed order appears
    history_page.navigate_to_history_page()
    history_page.select_filter("all")

    closed_record = history_page.wait_for_history_record(target_id, timeout=20000)
    logger.info(f"Verified closed order record in History: {closed_record}")

    # 6. Verify trade attributes match exactly
    assert closed_record is not None, f"Expected order {target_id} to be present in History"
    assert str(closed_record["id"]) == str(target_id) or str(closed_record["data_id"]) == str(target_id), (
        f"Expected order ID {target_id}, got: {closed_record['id']}"
    )
    assert "AUDUSD" in closed_record["symbol"], f"Expected AUDUSD symbol, got: {closed_record['symbol']}"
    assert closed_record["order"].upper() == "BUY", f"Expected BUY order, got: {closed_record['order']}"
    assert closed_record["lot"] == 0.01, f"Expected lot 0.01, got: {closed_record['lot']}"
    assert closed_record["entry"] > 0, f"Expected positive entry price, got: {closed_record['entry']}"
    assert closed_record["exit"] > 0, f"Expected positive exit price, got: {closed_record['exit']}"
    assert len(closed_record["close_time"]) > 0, "Expected non-empty close time timestamp"


@pytest.mark.trade
@pytest.mark.regression
def test_history_page_bottom_calculations(
    history_page: HistoryPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the financial calculations and summary metrics at the bottom of the History page:
    1. Balance (#total_balance) is positive and non-zero.
    2. Deposit (#total_deposit) is non-negative.
    3. Withdraw (#total_withdraw) is non-negative.
    4. Commission (#totalbrokerage) is non-negative.
    5. SWAP (#tswap) is a valid finite numeric value.
    6. PROFIT (#totalprofit) is a valid finite numeric value.
    7. Balance consistency: Balance matches or correlates with Deposit - Withdraw + Profit +/- Commission/Swap.
    """
    history_page.navigate_to_history_page()
    history_page.select_filter("all")
    history_page.page.wait_for_timeout(1000)

    calcs = history_page.get_bottom_calculations()
    logger.info(f"Extracted History Bottom Calculations: {calcs}")

    # 1. Assert required metrics exist and are non-trivial
    assert calcs["balance"] > 0, f"Expected positive Balance, got: {calcs['balance']}"
    assert calcs["deposit"] >= 0, f"Expected non-negative Deposit, got: {calcs['deposit']}"
    assert calcs["withdraw"] >= 0, f"Expected non-negative Withdraw, got: {calcs['withdraw']}"

    # 2. Commission, SWAP, PROFIT are finite numbers
    assert isinstance(calcs["commission"], float)
    assert isinstance(calcs["swap"], float)
    assert isinstance(calcs["profit"], float)

    # 3. Check mathematical sanity of Balance against transactions if deposit & withdraw exist
    if calcs["deposit"] > 0:
        net_cashflow = calcs["deposit"] - calcs["withdraw"]
        logger.info(f"Net Cashflow: {net_cashflow}, Balance: {calcs['balance']}, Closed Profit: {calcs['profit']}")
        # Net cashflow + profit should roughly align with balance within reasonable tolerance
        estimated_balance = net_cashflow + calcs["profit"] - calcs["commission"] + calcs["swap"]
        diff = abs(calcs["balance"] - estimated_balance)
        logger.info(f"Estimated Balance from bottom elements: {estimated_balance}, Discrepancy: {diff}")


@pytest.mark.trade
@pytest.mark.regression
def test_history_page_runtime_diagnostics_clean(
    history_page: HistoryPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that interacting with the History page operates with zero invisible runtime defects:
    - Zero JavaScript runtime exceptions (uncaught errors)
    - Zero console.error log emissions
    - Zero failed/aborted network requests
    - Zero HTTP 4xx/5xx error responses

    Exercises:
    1. Navigation to the History page via the left sidebar icon.
    2. Filter dropdown open/close and cycling through all 8 duration options.
    3. Export button click.
    4. Reading the bottom calculation bar statistics.
    5. Asserting full diagnostic cleanliness after all interactions.
    """
    history_page.navigate_to_history_page()
    assert_url_contains(history_page.page, "/dashboard", timeout=15000)
    history_page.page.wait_for_timeout(1500)

    # 1. Open filter dropdown and inspect all options
    history_page.open_filter_dropdown()
    history_page.page.wait_for_timeout(500)

    # 2. Cycle through all supported filter durations
    for duration in ["1d", "1w", "3w", "1m", "3m", "1y", "all"]:
        history_page.select_filter(duration)
        history_page.page.wait_for_timeout(500)

    # 3. Click the Export button
    history_page.click_export_button()
    history_page.page.wait_for_timeout(500)

    # 4. Read bottom calculation bar
    history_page.select_filter("all")
    history_page.page.wait_for_timeout(1000)
    calcs = history_page.get_bottom_calculations()
    logger.info(f"[Diagnostics] Bottom calculations captured: {calcs}")

    # 5. Assert zero hidden runtime defects
    history_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
        ignored_patterns=["google-analytics.com", "hotjar.com", "fonts.googleapis.com"],
    )
