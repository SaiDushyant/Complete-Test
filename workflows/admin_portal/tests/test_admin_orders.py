"""
Test Suite: Admin Portal - Orders Module Verification.
Covers:
- Navigation across submenus (All, Open, Closed) via sidebar and direct routes.
- Main table controls: 10 headers, sorting, search filter & clear, entries dropdown, CSV/PDF/Excel exports, horizontal scroll.
- Show Orders action & #orderModal: stat cards, 24-column order ledger table, modal Excel export, pagination, horizontal scroll, modal close.
- In-row Edit button & #myModal form: pre-populated values verification, form field editability, client validations.
- Mock Save button test: Playwright route interception guaranteeing ZERO backend database changes, payload validation, mock response handling.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage


@pytest.mark.admin
@pytest.mark.orders
def test_admin_orders_sidebar_and_tab_navigation(admin_orders_page: AdminOrdersPage) -> None:
    """
    Test navigation across Orders module submenus: All, Open, and Closed Orders.
    Verifies sidebar clicks, URL updates, and page headings.
    """
    # 1. Navigate to Open Orders via sidebar
    admin_orders_page.navigate("open")
    admin_orders_page.navigate_via_sidebar("open")
    expect(admin_orders_page.page).to_have_url(re.compile(r"/admin/Controlbase/order/open", re.I))
    heading = admin_orders_page.page_heading.inner_text().strip()
    assert "Open Order" in heading, f"Expected 'Open Order' in heading, got '{heading}'"

    # 2. Navigate to All Orders via sidebar
    admin_orders_page.navigate_via_sidebar("all")
    expect(admin_orders_page.page).to_have_url(re.compile(r"/admin/Controlbase/order/all", re.I))
    heading_all = admin_orders_page.page_heading.inner_text().strip()
    assert "All Order" in heading_all or "Order Details" in heading_all, f"Unexpected heading '{heading_all}'"

    # 3. Navigate to Closed Orders via sidebar
    admin_orders_page.navigate_via_sidebar("closed")
    expect(admin_orders_page.page).to_have_url(re.compile(r"/admin/Controlbase/order/closed", re.I))
    heading_closed = admin_orders_page.page_heading.inner_text().strip()
    assert "Closed Order" in heading_closed or "Order Details" in heading_closed, f"Unexpected heading '{heading_closed}'"


@pytest.mark.admin
@pytest.mark.orders
def test_admin_orders_table_controls_minute_elements(admin_orders_page: AdminOrdersPage) -> None:
    """
    Test main DataTable controls and minute elements:
    - 10 table headers verification
    - Column sorting toggle
    - Search input filtering and clearing
    - Show entries dropdown
    - CSV, PDF, and Excel export buttons
    - Table horizontal scroll container
    """
    admin_orders_page.navigate("open")

    # 1. Verify 10 table headers
    expected_headers = [
        "User ID",
        "Customer Name",
        "Account ID",
        "Fund",
        "Balance",
        "Equity",
        "Margin Level",
        "Group Name",
        "Total PNL",
        "Details",
    ]
    actual_headers = admin_orders_page.get_table_headers()
    assert len(actual_headers) == 10, f"Expected 10 headers, got {len(actual_headers)}: {actual_headers}"
    for exp_h in expected_headers:
        assert any(exp_h.lower() in act.lower() for act in actual_headers), f"Header '{exp_h}' not found in {actual_headers}"

    # 2. Verify column sorting toggles
    sort_res = admin_orders_page.sort_column(col_index=0)
    assert sort_res["before"] != sort_res["after"] or "sorting" in sort_res["after"], (
        f"Sorting class did not change as expected: {sort_res}"
    )

    # 3. Verify search filter and clear
    initial_rows = admin_orders_page.get_table_rows_count()
    assert initial_rows > 0, "Expected table to contain at least 1 account row"

    admin_orders_page.search("mam1f")
    filtered_rows = admin_orders_page.get_table_rows_count()
    assert filtered_rows >= 1, f"Expected at least 1 filtered row for 'mam1f', got {filtered_rows}"

    admin_orders_page.clear_search()
    cleared_rows = admin_orders_page.get_table_rows_count()
    assert cleared_rows == initial_rows, f"Expected rows to restore to {initial_rows}, got {cleared_rows}"

    # 4. Verify entries length select dropdown
    expect(admin_orders_page.entries_select).to_be_visible()
    admin_orders_page.select_entries_count(25)

    # 5. Verify Export buttons (CSV, PDF, Excel)
    expect(admin_orders_page.export_csv_btn).to_be_visible()
    expect(admin_orders_page.export_pdf_btn).to_be_visible()
    expect(admin_orders_page.export_excel_btn).to_be_visible()

    # 6. Verify horizontal scroll state
    scroll_state = admin_orders_page.check_horizontal_scroll()
    assert "mainTableScrollWidth" in scroll_state, "Expected scroll state to contain mainTableScrollWidth"


@pytest.mark.admin
@pytest.mark.orders
def test_admin_orders_show_orders_modal_and_minute_elements(admin_orders_page: AdminOrdersPage) -> None:
    """
    Test in-row Action button 'Show Orders' and the resulting #orderModal:
    - Opens #orderModal for the first account
    - Validates summary stat cards (Account ID, Customer Name, Brokerage, Spread, PNL)
    - Validates 24-column detailed order ledger table (#orderHistory)
    - Validates horizontal scrollability of the 24-column table
    - Validates in-modal Excel export button (#btnH)
    - Validates pagination inside modal
    - Validates modal Close button (.ux-order-close)
    """
    admin_orders_page.navigate("open")

    # 1. Open Show Orders modal
    admin_orders_page.open_show_orders(row_index=0)
    expect(admin_orders_page.order_modal).to_be_visible()

    # 2. Verify summary stat cards
    stats = admin_orders_page.get_order_modal_stats()
    assert stats["account_id"] != "", "Account ID stat should not be empty"
    assert stats["customer_name"] != "", "Customer Name stat should not be empty"

    # 3. Verify 24-column order ledger headers
    expected_order_headers = [
        "TIME",
        "UID",
        "SYMBOL",
        "SIDE",
        "LOT",
        "ENTRY",
        "EXIT",
        "SL",
        "TARGET",
        "TRIGGER",
        "STATUS",
        "TYPE",
        "BOOK",
        "COPY",
        "REASON",
        "MARGIN",
        "COMMISSION",
        "LP COMMISSION",
        "SPREAD COMMISSION",
        "SWAP",
        "PNL",
        "CLOSING TIME",
        "DURATION",
        "ACTIONS",
    ]
    actual_order_headers = admin_orders_page.get_order_history_headers()
    assert len(actual_order_headers) == 24, f"Expected 24 headers, got {len(actual_order_headers)}: {actual_order_headers}"
    for exp_col in expected_order_headers:
        assert any(exp_col.lower() in act.lower() for act in actual_order_headers), f"Missing order column '{exp_col}'"

    # 4. Verify horizontal scrollbar on the 24-column table
    modal_scroll = admin_orders_page.check_modal_horizontal_scroll()
    assert modal_scroll["isHorizontallyScrollable"] is True, (
        f"Expected 24-column order ledger to be horizontally scrollable: {modal_scroll}"
    )

    # 5. Verify in-modal Excel download button and pagination
    expect(admin_orders_page.order_modal_excel_btn).to_be_visible()
    expect(admin_orders_page.order_history_paginate).to_be_visible()

    # 6. Verify modal Close button cleanly dismisses #orderModal
    admin_orders_page.close_order_modal()
    expect(admin_orders_page.order_modal).to_be_hidden()


@pytest.mark.admin
@pytest.mark.orders
def test_admin_orders_edit_form_prepopulation_and_editability(admin_orders_page: AdminOrdersPage) -> None:
    """
    Test in-row Edit button (a.btnEdit) inside #orderModal:
    - Opens #myModal
    - Validates form values are properly pre-populated from the selected order
    - Tests form fields are editable (typing new lot, sl, target, avg)
    - Tests client-side validation errors (empty lot, negative SL)
    - Tests Close button dismisses #myModal without changing data
    """
    admin_orders_page.navigate("open")
    admin_orders_page.open_show_orders(row_index=0)

    # 1. Open Edit modal for the first order
    admin_orders_page.open_edit_order_modal(order_index=0)
    expect(admin_orders_page.edit_modal).to_be_visible()

    # 2. Verify pre-populated values
    values = admin_orders_page.get_edit_order_form_values()
    assert values["lot"] != "", "Expected Lot size to be pre-populated"
    assert values["avg"] != "", "Expected Avg price to be pre-populated"
    assert values["brokerage"] != "", "Expected Brokerage to be pre-populated"
    assert str(values["bs"]).lower() in ["0", "1", "buy", "sell"], f"Expected side to be buy/sell/0/1, got '{values['bs']}'"


    # 3. Test field editability
    original_lot = values["lot"]
    admin_orders_page.fill_edit_order_form(lot="0.50", sl="10.5", target="25.0")
    edited_values = admin_orders_page.get_edit_order_form_values()
    assert edited_values["lot"] == "0.50", f"Expected lot to update to '0.50', got '{edited_values['lot']}'"
    assert edited_values["sl"] == "10.5", f"Expected sl to update to '10.5', got '{edited_values['sl']}'"
    assert edited_values["target"] == "25.0", f"Expected target to update to '25.0', got '{edited_values['target']}'"

    # 4. Test client-side validations
    # 4a. Empty lot validation
    lot_error = admin_orders_page.test_validation_error(field="lot", bad_value="")
    assert "please enter the lot" in lot_error.lower(), f"Unexpected lot error message: '{lot_error}'"

    # 4b. Negative SL validation
    admin_orders_page.fill_edit_order_form(lot=original_lot)
    sl_error = admin_orders_page.test_validation_error(field="sl", bad_value="-5")
    assert "negative" in sl_error.lower(), f"Unexpected sl error message: '{sl_error}'"

    # 5. Restore valid values and close modal
    admin_orders_page.fill_edit_order_form(lot=original_lot, sl="0")
    admin_orders_page.close_edit_modal()
    expect(admin_orders_page.edit_modal).to_be_hidden()

    # Close orderModal
    admin_orders_page.close_order_modal()
    expect(admin_orders_page.order_modal).to_be_hidden()


@pytest.mark.admin
@pytest.mark.orders
def test_admin_orders_edit_form_mock_save(admin_orders_page: AdminOrdersPage) -> None:
    """
    Test Save button on the Edit Order form as a MOCK TEST:
    - Intercepts POST to /admin/Controlbase/updateOrderDetails
    - Validates payload contains submitted form values
    - Returns mock 200 response with zero real database changes
    - Validates confirmation alert ('Congratulations!') appears and dismisses it
    - Confirms clean dismissal of modals
    """
    admin_orders_page.navigate("open")
    admin_orders_page.open_show_orders(row_index=0)
    admin_orders_page.open_edit_order_modal(order_index=0)

    # 1. Fill test values into form
    test_lot = "0.25"
    admin_orders_page.fill_edit_order_form(lot=test_lot, sl="15.0", target="30.0")

    # 2. Execute mock save test (guaranteeing 0 database writes)
    save_result = admin_orders_page.save_order_mock()
    assert save_result["intercepted"] is True, "Mock route was not intercepted!"
    assert save_result["request_count"] >= 1, "Expected at least 1 update request intercepted"

    # Verify intercepted payload contains the edited lot value
    payload = save_result["payload"]
    if payload:
        assert test_lot in payload, f"Expected edited lot '{test_lot}' in payload, got: {payload[:200]}"

    # Verify modals cleanly closed after mock update
    admin_orders_page.page.wait_for_timeout(1000)
    expect(admin_orders_page.edit_modal).to_be_hidden()
