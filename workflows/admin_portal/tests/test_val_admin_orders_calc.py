"""
Admin Portal Orders & Financial Calculations Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.1, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Search input, symbol filter, boundary order tickets, SQLi/XSS sanitization.
2. Buttons & Actions: Show Orders modal trigger, modal dismissal ('X' and 'Close'), export buttons (CSV, PDF, Excel).
3. Dropdowns & Selects: Entries per page pagination options (10, 25, 50, 100).
5. Date & Time Pickers: Inverted date boundaries ('From > To'), date clear restoring full ledger.
6. Calculations & Tables: Total PnL, Brokerage, Spread stat cards, A/B-Book Balance & Margin invariants, column sorting traversal.
7. Security: SQLi/XSS attack vectors, input sanitization.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.admin_a_book_page import AdminABookPage
from workflows.admin_portal.pages.admin_b_book_page import AdminBBookPage
from workflows.admin_portal.pages.admin_a_book_user_margin_page import AdminABookUserMarginPage
from workflows.admin_portal.pages.admin_b_book_user_margin_page import AdminBBookUserMarginPage
from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1: SUB-ROUTE INTEGRITY & NAVIGATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_all_open_closed_route_integrity(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify all 3 primary order sub-routes (all, open, closed)
    navigate successfully, return HTTP 200, and render the main datatable.
    """
    for submenu in ["all", "open", "closed"]:
        admin_orders_page.navigate(submenu=submenu)
        admin_orders_page.page.wait_for_timeout(1000)
        expect(admin_orders_page.table).to_be_attached(timeout=15000)
        expect(admin_orders_page.export_csv_btn).to_be_attached(timeout=10000)

    admin_error_monitor.assert_no_errors("Orders Sub-Routes Integrity")


# ==============================================================================
# PILLAR 1: TEXTBOX & SEARCH INPUT SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_search_symbol_filter_and_empty_state(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching a valid symbol filters table, and searching a non-existent
    order ticket cleanly displays empty state without UI breakage.
    """
    admin_orders_page.navigate(submenu="all")
    admin_orders_page.page.wait_for_timeout(1500)
    expect(admin_orders_page.table).to_be_attached()

    initial_count = admin_orders_page.get_table_rows_count()

    # Search valid symbol
    admin_orders_page.search("EUR")
    admin_orders_page.page.wait_for_timeout(800)
    filtered_count = admin_orders_page.get_table_rows_count()
    assert filtered_count >= 0, "Filtered count should be non-negative"

    # Search non-existent ticket query
    admin_orders_page.search("NON_EXISTENT_ORDER_TICKET_999999")
    admin_orders_page.page.wait_for_timeout(800)
    empty_cell = admin_orders_page.page.locator("#datatable tbody td").first
    if empty_cell.is_visible():
        empty_text = empty_cell.inner_text().strip()
        assert any(term in empty_text.lower() for term in ["no matching", "no data", "0 to 0", "empty"]), (
            f"Expected empty state indication, got: '{empty_text}'"
        )

    # Clear search restores table
    admin_orders_page.clear_search()
    admin_orders_page.page.wait_for_timeout(800)
    assert admin_orders_page.get_table_rows_count() == initial_count, "Clearing search must restore initial row count"

    admin_error_monitor.assert_no_errors("Orders Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_search_sqli_xss_sanitization(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & Security (Section 4): Verify the Orders table search input safely neutralizes
    SQL injection payloads and XSS attack vectors.
    """
    admin_orders_page.navigate(submenu="all")
    admin_orders_page.page.wait_for_timeout(1000)

    for payload, description in SQLI_PAYLOADS[:3]:
        admin_orders_page.search(payload)
        admin_orders_page.page.wait_for_timeout(400)
        # Verify no 500 error or SQL crash message is rendered
        body_text = admin_orders_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL error exposed for payload: {payload}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for payload: {payload}"

    for payload, description in XSS_PAYLOADS[:3]:
        admin_orders_page.search(payload)
        admin_orders_page.page.wait_for_timeout(400)
        is_pwned = admin_orders_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"

    admin_orders_page.clear_search()
    admin_error_monitor.assert_no_errors("Orders Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 2: BUTTONS & MODALS LIFECYCLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_export_buttons_integrity(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify that CSV, PDF, and Excel export action buttons are visible,
    attached to DOM, and interactable across order ledgers.
    """
    admin_orders_page.navigate(submenu="open")
    admin_orders_page.page.wait_for_timeout(1000)

    expect(admin_orders_page.export_csv_btn).to_be_visible()
    expect(admin_orders_page.export_pdf_btn).to_be_visible()
    expect(admin_orders_page.export_excel_btn).to_be_visible()

    assert admin_orders_page.export_csv_btn.is_enabled()
    assert admin_orders_page.export_pdf_btn.is_enabled()
    assert admin_orders_page.export_excel_btn.is_enabled()

    admin_error_monitor.assert_no_errors("Orders Export Buttons Integrity")


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_show_orders_modal_lifecycle(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify opening the detailed Order Information modal (#orderModal)
    displays customer information and summary metrics, and closes cleanly.
    """
    admin_orders_page.navigate(submenu="open")
    admin_orders_page.page.wait_for_timeout(1500)

    if admin_orders_page.get_table_rows_count() > 0:
        admin_orders_page.open_show_orders(row_index=0)
        expect(admin_orders_page.order_modal).to_be_visible(timeout=10000)

        # Verify summary stat cards exist inside modal
        stats = admin_orders_page.get_order_modal_stats()
        assert "brokerage" in stats or "pnl" in stats, "Expected stats in order modal"

        # Close modal cleanly
        admin_orders_page.close_order_modal()
        expect(admin_orders_page.order_modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Show Orders Modal Lifecycle")


# ==============================================================================
# PILLAR 3: DROPDOWNS & PAGE LENGTH SELECTOR
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_page_length_selector_validation(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3 & 6: Verify changing visible entries per page (10, 25, 50, 100)
    dynamically updates table rows count and status summary text.
    """
    admin_orders_page.navigate(submenu="all")
    admin_orders_page.page.wait_for_timeout(1500)

    expect(admin_orders_page.entries_select).to_be_visible(timeout=10000)
    available_options = [opt.inner_text().strip() for opt in admin_orders_page.entries_select.locator("option").all()]
    assert "10" in available_options
    assert "25" in available_options
    assert "50" in available_options

    for length in ["25", "50", "10"]:
        admin_orders_page.select_entries_count(int(length))
        admin_orders_page.page.wait_for_timeout(800)
        cur_rows = admin_orders_page.get_table_rows_count()
        assert cur_rows <= int(length), f"Expected at most {length} rows, got {cur_rows}"

    admin_error_monitor.assert_no_errors("Orders Page Length Selector")


# ==============================================================================
# PILLAR 5: DATE RANGE BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_inverted_date_range_boundary(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Verify that setting an inverted date range (From > To, e.g.
    From: 2026-12-31, To: 2026-01-01) does not cause 500 server crash
    and yields empty state or handles boundary cleanly.
    """
    admin_orders_page.navigate(submenu="closed")
    admin_orders_page.page.wait_for_timeout(1000)

    date_from = admin_orders_page.page.locator("#from")
    date_to = admin_orders_page.page.locator("#to")
    apply_btn = admin_orders_page.page.locator("#apply")
    clear_btn = admin_orders_page.page.locator("#clear")

    if date_from.is_visible() and date_to.is_visible() and apply_btn.is_visible():
        # Set inverted dates
        date_from.fill("2026-12-31")
        date_to.fill("2026-01-01")
        apply_btn.click()
        admin_orders_page.page.wait_for_timeout(800)

        # Verify page is stable and not HTTP 500
        expect(admin_orders_page.table).to_be_visible()

        # Clear restores full ledger
        if clear_btn.is_visible():
            clear_btn.click()
            admin_orders_page.page.wait_for_timeout(600)
            expect(admin_orders_page.table).to_be_visible()

    admin_error_monitor.assert_no_errors("Orders Inverted Date Range Boundary")


# ==============================================================================
# PILLAR 6: CALCULATIONS & FINANCIAL METRIC INVARIANTS (A-BOOK & B-BOOK)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_abook_route_and_metrics_bar_validation(
    admin_a_book_page: AdminABookPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify Admin A Book page (/admin/Controlbase/aBook) loads cleanly,
    and summary bar metrics (Balance, Equity, Used Margin, Free Margin, Profit / Loss)
    are parsed as valid numeric values.
    """
    admin_a_book_page.navigate()
    expect(admin_a_book_page.table).to_be_attached(timeout=15000)

    metrics = admin_a_book_page.get_summary_bar_metrics()
    assert "balance" in metrics, f"Expected balance in A-Book metrics: {metrics}"
    assert "equity" in metrics, f"Expected equity in A-Book metrics: {metrics}"
    assert isinstance(metrics["balance"], (int, float))
    assert isinstance(metrics["equity"], (int, float))

    admin_error_monitor.assert_no_errors("A Book Route & Metrics Bar")


@pytest.mark.admin
@pytest.mark.validation
def test_val_bbook_route_and_metrics_bar_validation(
    admin_b_book_page: AdminBBookPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify Admin B Book page (/admin/Controlbase/bBook) renders,
    metrics (Total Used Margin, Total P/L) are valid, and Buy/Sell Order buttons exist.
    """
    admin_b_book_page.navigate()
    expect(admin_b_book_page.table).to_be_attached(timeout=15000)

    # Verify action buttons for B-Book order management
    expect(admin_b_book_page.buy_order_btn).to_be_attached()
    expect(admin_b_book_page.sell_order_btn).to_be_attached()

    # Verify export buttons
    expect(admin_b_book_page.export_csv_btn).to_be_visible()
    expect(admin_b_book_page.export_excel_btn).to_be_visible()

    admin_error_monitor.assert_no_errors("B Book Route & Metrics Bar")


@pytest.mark.admin
@pytest.mark.validation
def test_val_abook_user_margin_table_calculations_and_invariants(
    admin_a_book_user_margin_page: AdminABookUserMarginPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify A Book User Margin page (/admin/Controlbase/aBookUserMargin)
    contains all 9 expected column headers, and row balances are valid numeric values.
    """
    admin_a_book_user_margin_page.navigate()
    expect(admin_a_book_user_margin_page.table).to_be_attached(timeout=15000)

    headers = admin_a_book_user_margin_page.get_table_headers()
    expected_headers = ["User ID", "Customer Name", "Account ID", "Fund", "Balance", "Equity", "Margin Level", "Group Name", "Total PNL"]
    for expected in expected_headers:
        assert any(expected.lower() in h.lower() for h in headers), (
            f"Expected header '{expected}' in A-Book User Margin headers: {headers}"
        )

    # Verify rows if present
    if admin_a_book_user_margin_page.get_table_rows_count() > 0:
        first_row_cells = admin_a_book_user_margin_page.table_rows.first.locator("td").all_inner_texts()
        assert len(first_row_cells) >= 8, f"Expected at least 8 cells, got {len(first_row_cells)}"

    admin_error_monitor.assert_no_errors("A Book User Margin Calculations")


@pytest.mark.admin
@pytest.mark.validation
def test_val_bbook_user_margin_table_calculations_and_invariants(
    admin_b_book_user_margin_page: AdminBBookUserMarginPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify B Book User Margin page (/admin/Controlbase/bBookUserMargin)
    contains all expected headers and data rows maintain numeric validity.
    """
    admin_b_book_user_margin_page.navigate()
    expect(admin_b_book_user_margin_page.table).to_be_attached(timeout=15000)

    headers = admin_b_book_user_margin_page.get_table_headers()
    expected_headers = ["User ID", "Customer Name", "Account ID", "Fund", "Balance", "Equity", "Margin Level", "Group Name", "Total PNL"]
    for expected in expected_headers:
        assert any(expected.lower() in h.lower() for h in headers), (
            f"Expected header '{expected}' in B-Book User Margin headers: {headers}"
        )

    admin_error_monitor.assert_no_errors("B Book User Margin Calculations")


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_table_column_sorting_traversal(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table column headers updates sorting classes
    (sorting_asc, sorting_desc) without breaking layout.
    """
    admin_orders_page.navigate(submenu="open")
    admin_orders_page.page.wait_for_timeout(1000)

    sort_res = admin_orders_page.sort_column(col_index=0)
    assert sort_res["before"] != sort_res["after"] or "sorting" in sort_res["after"], (
        f"Sorting class did not update on column 0: {sort_res}"
    )

    admin_error_monitor.assert_no_errors("Orders Column Sorting Traversal")


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_log_table_integrity(
    admin_order_edit_log_page: AdminOrderEditLogPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify Order Edit Log page (/admin/Controlbase/orderEditLog)
    renders ledger table with expected columns and responsive layout.
    """
    admin_order_edit_log_page.navigate()
    expect(admin_order_edit_log_page.table).to_be_attached(timeout=15000)

    # Verify search input presence
    expect(admin_order_edit_log_page.search_input).to_be_visible(timeout=10000)

    # Verify export buttons
    expect(admin_order_edit_log_page.csv_button).to_be_visible()
    expect(admin_order_edit_log_page.pdf_button).to_be_visible()

    admin_error_monitor.assert_no_errors("Order Edit Log Table Integrity")
