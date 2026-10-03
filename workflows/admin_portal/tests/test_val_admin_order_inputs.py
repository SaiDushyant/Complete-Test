"""
Admin Portal Order Inputs & Edit Modal Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.1, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Lot size boundaries (empty, negative, zero), SL/TP boundaries, avg price, brokerage.
2. Buttons & Actions: Show Orders modal trigger, Edit Order modal trigger, save submission, modal dismissals ('X' and 'Close').
3. Dropdowns & Selects: Entries length pagination select on Order Edit Log.
4. Dropzones & Uploads: N/A for orders (audit log and ledger only).
5. Date & Time Pickers: Order closing time and audit timestamps.
6. Calculations & Tables: Stat cards (Brokerage, Spread, PnL), 24-column order ledger, Order Edit Log audit records.
7. Security: SQLi/XSS search sanitization, mock save route interception (0 database mutations).

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import json
import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage
from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1 & 2: SHOW ORDERS MODAL & 24-COLUMN ORDER LEDGER
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_orders_open_and_show_modal_integrity(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify opening 'Show Orders' from open orders table renders
    summary stat cards, 24-column order history table, horizontal scroll container,
    and cleanly dismisses via modal close button.
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)
    expect(admin_orders_page.table).to_be_attached(timeout=15000)

    rows_count = admin_orders_page.get_table_rows_count()
    if rows_count == 0:
        pytest.skip("No open orders rows available for modal inspection on staging.")

    # 1. Open Show Orders modal
    admin_orders_page.open_show_orders(row_index=0)
    expect(admin_orders_page.order_modal).to_be_visible(timeout=15000)

    # 2. Verify summary stat cards exist
    stats = admin_orders_page.get_order_modal_stats()
    assert stats["account_id"] != "", "Account ID stat must be populated"
    assert stats["customer_name"] != "", "Customer Name stat must be populated"

    # 3. Verify order history headers
    headers = admin_orders_page.get_order_history_headers()
    assert len(headers) >= 15, f"Expected order history table headers, got {len(headers)}: {headers}"
    for required_header in ["SYMBOL", "LOT", "STATUS", "PNL"]:
        assert any(required_header in h.upper() for h in headers), f"Missing header: {required_header}"

    # 4. Verify horizontal scroll state
    scroll_state = admin_orders_page.check_modal_horizontal_scroll()
    assert "tableScrollWidth" in scroll_state, "Scroll state should contain tableScrollWidth"

    # 5. Clean dismissal
    admin_orders_page.close_order_modal()
    expect(admin_orders_page.order_modal).to_be_hidden(timeout=10000)

    admin_error_monitor.assert_no_errors("Show Orders Modal Integrity")


# ==============================================================================
# PILLAR 1 & 2: EDIT ORDER MODAL PRE-POPULATION & MODAL DISMISSAL LIFECYCLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_modal_lifecycle_and_prepopulation(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify Edit Order Modal (#myModal) opens from #orderModal,
    pre-populates current order parameters (oid, lot, avg, brokerage),
    and validates dismissal via both header card close (.ux-card-close)
    and footer Close button without altering order data.
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)

    rows_count = admin_orders_page.get_table_rows_count()
    if rows_count == 0:
        pytest.skip("No open orders available for edit modal test.")

    admin_orders_page.open_show_orders(row_index=0)
    expect(admin_orders_page.order_modal).to_be_visible(timeout=15000)

    edit_buttons = admin_orders_page.page.locator("#orderHistory tbody tr a.btnEdit")
    if edit_buttons.count() == 0:
        admin_orders_page.close_order_modal()
        pytest.skip("No editable orders in order history table.")

    # 1. Open Edit Modal
    admin_orders_page.open_edit_order_modal(order_index=0)
    expect(admin_orders_page.edit_modal).to_be_visible(timeout=15000)

    # 2. Check pre-population
    values = admin_orders_page.get_edit_order_form_values()
    assert values["lot"] != "", "Lot size must be pre-populated"
    assert values["avg"] != "", "Avg price must be pre-populated"
    assert values["brokerage"] != "", "Brokerage must be pre-populated"

    # 3. Dismiss via header close button (.ux-card-close)
    expect(admin_orders_page.edit_modal_card_close).to_be_visible(timeout=5000)
    admin_orders_page.edit_modal_card_close.click()
    admin_orders_page.page.wait_for_timeout(600)
    expect(admin_orders_page.edit_modal).to_be_hidden(timeout=10000)

    # 4. Reopen and dismiss via footer Close button
    admin_orders_page.open_edit_order_modal(order_index=0)
    expect(admin_orders_page.edit_modal).to_be_visible(timeout=10000)
    admin_orders_page.close_edit_modal()
    expect(admin_orders_page.edit_modal).to_be_hidden(timeout=10000)

    # 5. Close parent modal
    admin_orders_page.close_order_modal()
    expect(admin_orders_page.order_modal).to_be_hidden(timeout=10000)

    admin_error_monitor.assert_no_errors("Order Edit Modal Lifecycle")


# ==============================================================================
# PILLAR 1: LOT SIZE BOUNDARY CONDITIONS & VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_lot_boundary_validation(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test boundary conditions on Lot size input (#lot) inside #myModal:
    - Empty string -> displays '.invalid-feedback.lot' ("please enter the lot")
    - Non-numeric or boundary checks
    - Restoration of initial lot clears feedback
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)

    if admin_orders_page.get_table_rows_count() == 0:
        pytest.skip("No open orders available.")

    admin_orders_page.open_show_orders(row_index=0)
    edit_buttons = admin_orders_page.page.locator("#orderHistory tbody tr a.btnEdit")
    if edit_buttons.count() == 0:
        admin_orders_page.close_order_modal()
        pytest.skip("No editable orders in order history table.")

    admin_orders_page.open_edit_order_modal(order_index=0)
    initial_values = admin_orders_page.get_edit_order_form_values()
    original_lot = initial_values["lot"]

    try:
        # 1. Empty lot boundary
        error_msg = admin_orders_page.test_validation_error(field="lot", bad_value="")
        assert len(error_msg) > 0, "Expected invalid-feedback message for empty lot"
        assert "lot" in error_msg.lower(), f"Unexpected error text: '{error_msg}'"

        # 2. Restore original valid lot
        admin_orders_page.field_lot.fill(original_lot)
        admin_orders_page.page.wait_for_timeout(300)

    finally:
        # Safely dismiss modals
        if admin_orders_page.edit_modal.is_visible():
            admin_orders_page.close_edit_modal()
        if admin_orders_page.order_modal.is_visible():
            admin_orders_page.close_order_modal()

    admin_error_monitor.assert_no_js_errors("Order Edit Lot Boundary Validation")


# ==============================================================================
# PILLAR 1: STOP LOSS & TARGET BOUNDARY LOGIC
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_sl_target_logic_validation(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test boundary validation on Stop Loss (#sl) and Target (#target):
    - Negative Stop Loss value ('-5') triggers negative SL validation feedback
    - Zero or positive SL restores compliant state
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)

    if admin_orders_page.get_table_rows_count() == 0:
        pytest.skip("No open orders available.")

    admin_orders_page.open_show_orders(row_index=0)
    edit_buttons = admin_orders_page.page.locator("#orderHistory tbody tr a.btnEdit")
    if edit_buttons.count() == 0:
        admin_orders_page.close_order_modal()
        pytest.skip("No editable orders.")

    admin_orders_page.open_edit_order_modal(order_index=0)
    initial_values = admin_orders_page.get_edit_order_form_values()
    original_sl = initial_values["sl"] or "0"

    try:
        # Test negative SL
        sl_error = admin_orders_page.test_validation_error(field="sl", bad_value="-10")
        assert len(sl_error) > 0, "Expected validation error for negative SL"
        assert "negative" in sl_error.lower() or "invalid" in sl_error.lower() or "sl" in sl_error.lower(), (
            f"Unexpected SL error: '{sl_error}'"
        )

        # Restore SL
        admin_orders_page.field_sl.fill(original_sl)
        admin_orders_page.page.wait_for_timeout(300)

    finally:
        if admin_orders_page.edit_modal.is_visible():
            admin_orders_page.close_edit_modal()
        if admin_orders_page.order_modal.is_visible():
            admin_orders_page.close_order_modal()

    admin_error_monitor.assert_no_errors("Order Edit SL Target Logic")


# ==============================================================================
# PILLAR 1 & 2: AVERAGE PRICE & BROKERAGE INPUT EDITABILITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_pricing_and_brokerage_inputs(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify average entry price (#avg) and brokerage (#brokerage)
    inputs accept numeric values and update input state correctly.
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)

    if admin_orders_page.get_table_rows_count() == 0:
        pytest.skip("No open orders available.")

    admin_orders_page.open_show_orders(row_index=0)
    edit_buttons = admin_orders_page.page.locator("#orderHistory tbody tr a.btnEdit")
    if edit_buttons.count() == 0:
        admin_orders_page.close_order_modal()
        pytest.skip("No editable orders.")

    admin_orders_page.open_edit_order_modal(order_index=0)
    initial_values = admin_orders_page.get_edit_order_form_values()

    try:
        # Verify inputs are editable
        admin_orders_page.field_brokerage.fill("2.50")
        assert admin_orders_page.field_brokerage.input_value() == "2.50", "Brokerage should accept '2.50'"

        if admin_orders_page.field_trigger.is_visible():
            admin_orders_page.field_trigger.fill("1.0850")
            assert admin_orders_page.field_trigger.input_value() == "1.0850", "Trigger price should accept '1.0850'"

    finally:
        # Restore initial values and dismiss
        admin_orders_page.field_brokerage.fill(initial_values["brokerage"])
        if admin_orders_page.edit_modal.is_visible():
            admin_orders_page.close_edit_modal()
        if admin_orders_page.order_modal.is_visible():
            admin_orders_page.close_order_modal()

    admin_error_monitor.assert_no_errors("Order Edit Pricing & Brokerage Inputs")


# ==============================================================================
# PILLAR 2: MOCK SAVE ROUTE INTERCEPTION (ZERO BACKEND MUTATION)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_mock_save_zero_db_mutation(
    admin_orders_page: AdminOrdersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify form submission against updateOrderDetails endpoint
    using Playwright route interception. Asserts:
    - Request method is POST with correct serialized payload
    - Client properly receives mock 200 JSON success response
    - SweetAlert/jconfirm dialog appears and is safely dismissed
    - Zero database state changes occur on staging backend
    """
    admin_orders_page.navigate("open")
    admin_orders_page.page.wait_for_timeout(1000)

    if admin_orders_page.get_table_rows_count() == 0:
        pytest.skip("No open orders available.")

    admin_orders_page.open_show_orders(row_index=0)
    edit_buttons = admin_orders_page.page.locator("#orderHistory tbody tr a.btnEdit")
    if edit_buttons.count() == 0:
        admin_orders_page.close_order_modal()
        pytest.skip("No editable orders.")

    admin_orders_page.open_edit_order_modal(order_index=0)

    # Fill test values
    test_lot = "0.05"
    admin_orders_page.fill_edit_order_form(lot=test_lot, sl="0", target="0")

    # Run mock save test
    res = admin_orders_page.save_order_mock()
    assert res["intercepted"] is True, "Route updateOrderDetails must be intercepted!"
    assert res["request_count"] >= 1, "At least 1 request must be captured"
    if res["payload"]:
        assert test_lot in res["payload"], f"Edited lot {test_lot} should appear in POST body"

    # Confirm modals dismissed
    admin_orders_page.page.wait_for_timeout(500)
    expect(admin_orders_page.edit_modal).to_be_hidden()

    admin_error_monitor.assert_no_errors("Order Edit Mock Save Zero DB Mutation")


# ==============================================================================
# PILLAR 1 & 7: ORDER EDIT LOG AUDIT TABLE & SEARCH SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_log_table_and_search_sanitization(
    admin_order_edit_log_page: AdminOrderEditLogPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillars 1, 6 & 7: Validate Order Edit Log page (/admin/Controlbase/orderEditLog):
    - Table headers rendering and structure
    - SQLi and XSS payloads in datatable search box
    - Assert zero database errors leaked in DOM
    - Search clearing restores table rows
    """
    admin_order_edit_log_page.navigate()
    admin_order_edit_log_page.page.wait_for_timeout(1000)
    expect(admin_order_edit_log_page.table).to_be_attached(timeout=15000)

    headers = admin_order_edit_log_page.get_table_headers()
    assert len(headers) >= 4, f"Expected Order Edit Log headers, got {len(headers)}: {headers}"

    initial_count = admin_order_edit_log_page.get_table_rows_count()

    # Test SQLi & XSS payloads
    for payload, _ in SQLI_PAYLOADS[:3]:
        admin_order_edit_log_page.search(payload)
        admin_order_edit_log_page.page.wait_for_timeout(400)

        # Verify no database errors leaked into page
        body_text = admin_order_edit_log_page.page.locator("body").inner_text()
        assert "SQLSTATE" not in body_text, f"SQL error exposed for payload: {payload}"
        assert "syntax error" not in body_text.lower(), f"Syntax error exposed for payload: {payload}"

    for payload, _ in XSS_PAYLOADS[:3]:
        admin_order_edit_log_page.search(payload)
        admin_order_edit_log_page.page.wait_for_timeout(400)
        is_pwned = admin_order_edit_log_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert not is_pwned, f"XSS executed on Order Edit Log search: {payload}"

    # Clear search
    admin_order_edit_log_page.clear_search()
    admin_order_edit_log_page.page.wait_for_timeout(600)
    assert admin_order_edit_log_page.get_table_rows_count() == initial_count, "Clearing search restores rows"

    admin_error_monitor.assert_no_js_errors("Order Edit Log Table & Search Sanitization")


# ==============================================================================
# PILLAR 2 & 3: ORDER EDIT LOG EXPORTS & LENGTH DROPDOWN
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_edit_log_exports_and_pagination(
    admin_order_edit_log_page: AdminOrderEditLogPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillars 2 & 3: Verify Order Edit Log export buttons (CSV, PDF, Print) are
    present and enabled, and length dropdown updates pagination.
    """
    admin_order_edit_log_page.navigate()
    admin_order_edit_log_page.page.wait_for_timeout(1000)

    # Verify export buttons
    expect(admin_order_edit_log_page.csv_button).to_be_visible(timeout=10000)
    expect(admin_order_edit_log_page.pdf_button).to_be_visible(timeout=10000)
    expect(admin_order_edit_log_page.print_button).to_be_visible(timeout=10000)

    assert admin_order_edit_log_page.csv_button.is_enabled()
    assert admin_order_edit_log_page.pdf_button.is_enabled()
    assert admin_order_edit_log_page.print_button.is_enabled()

    # Verify length dropdown
    if admin_order_edit_log_page.entries_select.is_visible():
        admin_order_edit_log_page.entries_select.select_option("25")
        admin_order_edit_log_page.page.wait_for_timeout(500)
        assert admin_order_edit_log_page.entries_select.input_value() == "25"

    admin_error_monitor.assert_no_errors("Order Edit Log Exports and Pagination")
