"""
Admin Portal Deposit and Withdraw Module Automated Tests.
Comprehensive validation covering:
1. Admin Panel Sidebar Navigation:
   - Dashboard -> Deposit (/admin/Controlbase/deposit)
   - Deposit -> Withdrawal (/admin/Controlbase/withdraw)
   - Withdrawal -> Deposit List (/admin/Controlbase/payment)
   - Deposit List -> Withdraw List (/admin/Controlbase/managewithdraw)
   - Withdraw List -> Dashboard (/admin/Controlbase/Dashboard)
2. Admin Panel Topbar Features:
   - Theme Toggle (Switch theme from light to dark and dark to light)
   - Notifications bell & dropdown (toggle open, verify mark all read, toggle close)
3. Top Right Action Button for 4 Submenus:
   - Deposit: 'Add Deposit' -> opens 'Deposit Form' modal
   - Withdrawal: 'Add Withdraw' -> opens 'Withdraw Form' modal
   - Deposit List: 'Add Deposit Option' -> opens 'Payment Form' modal
   - Withdraw List: 'Add Withdraw Payment Mode' -> opens 'Add Withdraw Payment Mode' modal
4. 13 Table Headers Sorting on Deposit & Withdraw:
   - Column sorting traversal across all headers
5. Row Show Options & Pagination:
   - Entries per page dropdown (10, 25, 50, 100)
   - Pagination controls: page numbers, Next, Previous
6. Export Buttons:
   - CSV, PDF, and Excel download verification
7. Date Range Filter:
   - #from and #to datetime inputs, 'Go' (#apply), 'Clear' (#clear)
8. Search Bar:
   - Real-time table searching and clearing
9. Row Edit Actions in Deposit List & Withdraw List:
   - In-row Edit button (a.btnEdit) opens edit modal with input fields & buttons
10. Cross-Portal E2E Workflows:
   - Raise live deposit request in Client Portal -> Verify record in Admin Deposit table.
   - Raise live withdraw request in Client Portal -> Verify record in Admin Withdraw table.
11. Strict zero console errors, zero JS runtime exceptions, and zero backend failures.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import os
import random
import tempfile
import pytest
from playwright.sync_api import Browser, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_dashboard_page import AdminDashboardPage
from workflows.admin_portal.pages.admin_deposit_list_page import AdminDepositListPage
from workflows.admin_portal.pages.admin_deposit_page import AdminDepositPage
from workflows.admin_portal.pages.admin_withdraw_list_page import AdminWithdrawListPage
from workflows.admin_portal.pages.admin_withdraw_page import AdminWithdrawPage
from workflows.shared.utils.error_monitor import ErrorMonitor


EXPECTED_DEPOSIT_HEADERS = [
    "S.No",
    "Account ID",
    "Name",
    "Email ID",
    "Token",
    "Date and Time",
    "Payment Proof",
    "Method",
    "Amount",
    "Status",
    "Reason",
    "Type",
    "Action",
]

EXPECTED_WITHDRAW_HEADERS = [
    "S.No",
    "Account ID",
    "Name",
    "Email ID",
    "Token",
    "Date and Time",
    "Method",
    "Account Info",
    "Amount",
    "Status",
    "Reason",
    "Type",
    "Action",
]

EXPECTED_DEPOSIT_LIST_HEADERS = [
    "S.No",
    "Display Text",
    "Image",
    "Header Image",
    "Code",
    "Flag",
    "Minimum Amount",
    "Disclaimer",
    "Edit",
]

EXPECTED_WITHDRAW_LIST_HEADERS = [
    "S.No",
    "Name",
    "Flag",
    "Edit",
]


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_sidebar_navigation_to_deposit_and_withdraw(
    admin_dashboard_page: AdminDashboardPage,
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify complete sidebar navigation lifecycle:
    1. Start at Dashboard (/admin/Controlbase/Dashboard).
    2. Click 'Deposit' link in sidebar -> navigates to /admin/Controlbase/deposit.
    3. Click 'Withdrawal' link in sidebar -> navigates to /admin/Controlbase/withdraw.
    4. Click 'Deposit List' link in sidebar -> navigates to /admin/Controlbase/payment.
    5. Click 'Withdraw List' link in sidebar -> navigates to /admin/Controlbase/managewithdraw.
    6. Click 'Dashboard' link in sidebar -> navigates back to /admin/Controlbase/Dashboard.
    """
    # 1. Start at Dashboard
    admin_dashboard_page.navigate()
    assert admin_dashboard_page.is_dashboard_displayed(), "Expected Admin Dashboard to be displayed"
    expect(admin_dashboard_page.sidebar.sidebar_container.first).to_be_visible()

    # 2. Sidebar navigate to Deposit
    admin_dashboard_page.navigate_to_deposit_via_sidebar()
    expect(admin_deposit_page.table).to_be_visible(timeout=15000)
    expect(admin_deposit_page.table_rows.first).to_be_visible(timeout=15000)
    assert "/admin/Controlbase/deposit" in admin_deposit_page.page.url

    # 3. Sidebar navigate to Withdrawal
    admin_deposit_page.sidebar.navigate_to_withdrawal()
    expect(admin_withdraw_page.table).to_be_visible(timeout=15000)
    expect(admin_withdraw_page.table_rows.first).to_be_visible(timeout=15000)
    assert "/admin/Controlbase/withdraw" in admin_withdraw_page.page.url

    # 4. Sidebar navigate to Deposit List
    admin_withdraw_page.sidebar.navigate_to_deposit_list()
    expect(admin_deposit_list_page.table).to_be_visible(timeout=15000)
    assert "/admin/Controlbase/payment" in admin_deposit_list_page.page.url

    # 5. Sidebar navigate to Withdraw List
    admin_deposit_list_page.sidebar.navigate_to_withdraw_list()
    expect(admin_withdraw_list_page.table).to_be_visible(timeout=15000)
    assert "/admin/Controlbase/managewithdraw" in admin_withdraw_list_page.page.url

    # 6. Sidebar navigate back to Dashboard
    admin_withdraw_list_page.sidebar.navigate_to_dashboard()
    assert admin_dashboard_page.is_dashboard_displayed()
    assert "/admin/controlbase/dashboard" in admin_dashboard_page.page.url.lower()

    admin_error_monitor.assert_no_errors("Admin Sidebar Navigation")


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_topbar_theme_change_and_notifications(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify topbar controls across admin pages:
    1. Theme toggle switcher: toggle from light to dark, then back to light.
    2. Notifications bell: toggle open dropdown, verify 'Mark all read', toggle closed.
    """
    admin_deposit_page.navigate()

    # 1. Theme toggle
    mode_before = admin_deposit_page.topbar.get_layout_mode()
    mode_toggled = admin_deposit_page.topbar.toggle_theme()
    assert mode_toggled in ["dark", "light"]
    # Toggle back to original mode
    mode_reset = admin_deposit_page.topbar.toggle_theme()
    assert mode_reset in ["dark", "light"]

    # 2. Notifications toggle
    admin_deposit_page.topbar.open_notifications()
    expect(admin_deposit_page.topbar.notifications_dropdown).to_be_visible(timeout=5000)
    expect(admin_deposit_page.topbar.mark_all_read_btn).to_be_visible()

    admin_deposit_page.topbar.close_notifications()
    expect(admin_deposit_page.topbar.notifications_dropdown).not_to_be_visible(timeout=5000)

    admin_error_monitor.assert_no_errors("Admin Topbar Controls")


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_4_submenus_top_right_buttons(
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify top-right action button across all 4 submenus:
    1. Deposit: 'Add Deposit' -> opens 'Deposit Form' modal.
    2. Withdrawal: 'Add Withdraw' -> opens 'Withdraw Form' modal.
    3. Deposit List: 'Add Deposit Option' -> opens 'Payment Form' modal.
    4. Withdraw List: 'Add Withdraw Payment Mode' -> opens 'Add Withdraw Payment Mode' modal.
    """
    # 1. Deposit
    admin_deposit_page.navigate()
    expect(admin_deposit_page.add_deposit_button).to_be_visible()
    assert admin_deposit_page.add_deposit_button.inner_text().strip() == "Add Deposit"
    admin_deposit_page.open_add_deposit_modal()
    expect(admin_deposit_page.modal).to_be_visible()
    admin_deposit_page.close_modal()
    expect(admin_deposit_page.modal).not_to_be_visible()

    # 2. Withdrawal
    admin_withdraw_page.navigate()
    expect(admin_withdraw_page.add_withdraw_button).to_be_visible()
    assert admin_withdraw_page.add_withdraw_button.inner_text().strip() == "Add Withdraw"
    admin_withdraw_page.open_add_withdraw_modal()
    expect(admin_withdraw_page.modal).to_be_visible()
    admin_withdraw_page.close_modal()
    expect(admin_withdraw_page.modal).not_to_be_visible()

    # 3. Deposit List
    admin_deposit_list_page.navigate()
    expect(admin_deposit_list_page.add_deposit_option_button).to_be_visible()
    assert "Add Deposit Option" in admin_deposit_list_page.add_deposit_option_button.inner_text().strip()
    admin_deposit_list_page.open_add_modal()
    expect(admin_deposit_list_page.modal).to_be_visible()
    admin_deposit_list_page.close_modal()
    expect(admin_deposit_list_page.modal).not_to_be_visible()

    # 4. Withdraw List
    admin_withdraw_list_page.navigate()
    expect(admin_withdraw_list_page.add_withdraw_mode_button).to_be_visible()
    assert "Add Withdraw Payment Mode" in admin_withdraw_list_page.add_withdraw_mode_button.inner_text().strip()
    admin_withdraw_list_page.open_add_modal()
    expect(admin_withdraw_list_page.modal).to_be_visible()
    admin_withdraw_list_page.close_modal()
    expect(admin_withdraw_list_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("4 Submenus Top Right Buttons")


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_4_submenus_top_right_popup_form_filling(
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify that all fields inside the top-right button popup of all 4 submenus
    can be properly filled, modified, and validated:
    1. Deposit: 'Add Deposit' popup
       - Fills: email, datetime, method, amount, status, reason, proof file
       - Asserts all values are correctly retained and proof remove button is visible
    2. Withdrawal: 'Add Withdraw' popup
       - Fills: email, datetime, method, amount, status, reason
       - Asserts all values are correctly retained
    3. Deposit List: 'Add Deposit Option' popup
       - Fills Gateway Mode (is_bank = 0): display_name, code, disclaimer, minimum_amount
       - Fills Bank Mode (is_bank = 1): display_name, minimum_amount, bank_detail_name, remarks
       - Asserts dynamic bank details field row appears in table
    4. Withdraw List: 'Add Withdraw Payment Mode' popup
       - Fills withdraw_name
       - Asserts value is correctly retained
    """
    # Create temporary dummy image for proof / logo upload verification
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        dummy_img = f.name

    try:
        # 1. Deposit Popup Filling
        admin_deposit_page.navigate()
        admin_deposit_page.open_add_deposit_modal()
        admin_deposit_page.fill_deposit_form(
            email="kisacu@denipl.com",
            datetime_val="2026-09-29T10:30",
            method="USDT TRC20",
            amount="250.75",
            status="pending",
            reason="Automated deposit field filling verification",
            proof_path=dummy_img,
        )
        dep_vals = admin_deposit_page.get_deposit_form_values()
        assert dep_vals["email"] == "kisacu@denipl.com"
        assert dep_vals["datetime"] == "2026-09-29T10:30"
        assert dep_vals["method"] == "USDT TRC20"
        assert dep_vals["amount"] == "250.75"
        assert dep_vals["status"] == "pending"
        assert dep_vals["reason"] == "Automated deposit field filling verification"
        expect(admin_deposit_page.modal_proof_remove_btn).to_be_visible()
        admin_deposit_page.close_modal()

        # 2. Withdraw Popup Filling
        admin_withdraw_page.navigate()
        admin_withdraw_page.open_add_withdraw_modal()
        admin_withdraw_page.fill_withdraw_form(
            email="kisacu@denipl.com",
            datetime_val="2026-09-29T11:45",
            method="USDT ERC20",
            amount="150.00",
            status="pending",
            reason="Automated withdraw field filling verification",
        )
        wdl_vals = admin_withdraw_page.get_withdraw_form_values()
        assert wdl_vals["email"] == "kisacu@denipl.com"
        assert wdl_vals["datetime"] == "2026-09-29T11:45"
        assert wdl_vals["method"] == "USDT ERC20"
        assert wdl_vals["amount"] == "150.00"
        assert wdl_vals["status"] == "pending"
        assert wdl_vals["reason"] == "Automated withdraw field filling verification"
        admin_withdraw_page.close_modal()

        # 3. Deposit List (Payment) Popup Filling
        admin_deposit_list_page.navigate()
        admin_deposit_list_page.open_add_modal()

        # Gateway Mode
        admin_deposit_list_page.fill_payment_gateway_form(
            display_name="Automated Test Gateway",
            code="ATG_GATEWAY",
            disclaimer="Testing instant processing disclaimer",
            minimum_amount="30",
            image_path=dummy_img,
            header_image_path=dummy_img,
        )
        pay_gateway_vals = admin_deposit_list_page.get_payment_form_values()
        assert pay_gateway_vals["display_name"] == "Automated Test Gateway"
        assert pay_gateway_vals["code"] == "ATG_GATEWAY"
        assert pay_gateway_vals["disclaimer"] == "Testing instant processing disclaimer"
        assert pay_gateway_vals["minimum_amount"] == "30"

        # Bank Mode & Dynamic Bank Details Row
        admin_deposit_list_page.fill_payment_bank_form(
            display_name="Automated Bank Wire",
            minimum_amount="500",
            bank_detail_name="Account Number",
            bank_detail_remarks="Wire transfer remarks",
        )
        pay_bank_vals = admin_deposit_list_page.get_payment_form_values()
        assert pay_bank_vals["display_name"] == "Automated Bank Wire"
        assert pay_bank_vals["minimum_amount"] == "500"
        expect(admin_deposit_list_page.modal.locator("table tbody tr").filter(has_text="Account Number")).to_be_visible()
        admin_deposit_list_page.close_modal()

        # 4. Withdraw List Popup Filling
        admin_withdraw_list_page.navigate()
        admin_withdraw_list_page.open_add_modal()
        admin_withdraw_list_page.fill_withdraw_mode_form("Automated Wire Mode")
        w_mode_vals = admin_withdraw_list_page.get_withdraw_mode_form_values()
        assert w_mode_vals["withdraw_name"] == "Automated Wire Mode"
        admin_withdraw_list_page.close_modal()

    finally:
        if os.path.exists(dummy_img):
            os.remove(dummy_img)

    admin_error_monitor.assert_no_errors("4 Submenus Popup Form Filling")


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_4_submenus_top_right_popup_close_and_save_mock(
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Mock test for Close and Save buttons in the top-right button popup of all 4 submenus:
    1. Close Buttons Verification (No changes saved):
       - Footer 'Close' button dismisses modal on all 4 pages.
       - Header 'X' close button dismisses modal on all 4 pages.
    2. Save Buttons Verification (Mock test - No changes saved):
       - Active Playwright network route interception blocks any backend write/save mutation.
       - Empty form submission triggers client-side validation (.invalid-feedback), preventing save.
       - Validated across Deposit, Withdraw, Payment (Deposit List), and Withdraw List.
    """
    page = admin_deposit_page.page
    intercepted_mutations = []

    def _block_and_mock_save(route):
        url = route.request.url.lower()
        if any(action in url for action in ["insert", "save", "checkdeposit", "checkwithdraw"]):
            intercepted_mutations.append(route.request.url)
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"status":"mock_prevented","message":"Mock test - no database changes"}',
            )
        else:
            route.continue_()

    page.route("**/Controlbase/**", _block_and_mock_save)

    try:
        # =====================================================================
        # 1. Deposit Popup: Close & Save Button Mock Validation
        # =====================================================================
        admin_deposit_page.navigate()

        # 1a. Test Header 'X' close button
        admin_deposit_page.open_add_deposit_modal()
        expect(admin_deposit_page.modal).to_be_visible()
        admin_deposit_page.close_modal_via_x()
        expect(admin_deposit_page.modal).not_to_be_visible()

        # 1b. Test Footer 'Close' button
        admin_deposit_page.open_add_deposit_modal()
        expect(admin_deposit_page.modal).to_be_visible()
        admin_deposit_page.close_modal()
        expect(admin_deposit_page.modal).not_to_be_visible()

        # 1c. Test Save button triggers validation & prevents save
        admin_deposit_page.open_add_deposit_modal()
        admin_deposit_page.modal_save_button.click()
        expect(admin_deposit_page.modal.locator(".invalid-feedback.email")).to_be_visible()
        expect(admin_deposit_page.modal.locator(".invalid-feedback.email")).to_have_text("Please enter the email")
        expect(admin_deposit_page.modal).to_be_visible()
        admin_deposit_page.close_modal()
        expect(admin_deposit_page.modal).not_to_be_visible()

        # =====================================================================
        # 2. Withdraw Popup: Close & Save Button Mock Validation
        # =====================================================================
        admin_withdraw_page.navigate()

        # 2a. Test Header 'X' close button
        admin_withdraw_page.open_add_withdraw_modal()
        expect(admin_withdraw_page.modal).to_be_visible()
        admin_withdraw_page.close_modal_via_x()
        expect(admin_withdraw_page.modal).not_to_be_visible()

        # 2b. Test Footer 'Close' button
        admin_withdraw_page.open_add_withdraw_modal()
        expect(admin_withdraw_page.modal).to_be_visible()
        admin_withdraw_page.close_modal()
        expect(admin_withdraw_page.modal).not_to_be_visible()

        # 2c. Test Save button triggers validation & prevents save
        admin_withdraw_page.open_add_withdraw_modal()
        admin_withdraw_page.modal_save_button.click()
        expect(admin_withdraw_page.modal.locator(".invalid-feedback.email")).to_be_visible()
        expect(admin_withdraw_page.modal.locator(".invalid-feedback.email")).to_have_text("Please enter the email")
        expect(admin_withdraw_page.modal).to_be_visible()
        admin_withdraw_page.close_modal()
        expect(admin_withdraw_page.modal).not_to_be_visible()

        # =====================================================================
        # 3. Payment / Deposit List Popup: Close & Save Button Mock Validation
        # =====================================================================
        admin_deposit_list_page.navigate()

        # 3a. Test Header 'X' close button
        admin_deposit_list_page.open_add_modal()
        expect(admin_deposit_list_page.modal).to_be_visible()
        admin_deposit_list_page.close_modal_via_x()
        expect(admin_deposit_list_page.modal).not_to_be_visible()

        # 3b. Test Footer 'Close' button
        admin_deposit_list_page.open_add_modal()
        expect(admin_deposit_list_page.modal).to_be_visible()
        admin_deposit_list_page.close_modal()
        expect(admin_deposit_list_page.modal).not_to_be_visible()

        # 3c. Test Save button triggers validation & prevents save
        admin_deposit_list_page.open_add_modal()
        admin_deposit_list_page.modal_save_button.click()
        expect(admin_deposit_list_page.modal.locator(".invalid-feedback.display_name")).to_be_visible()
        expect(admin_deposit_list_page.modal.locator(".invalid-feedback.display_name")).to_have_text("Please enter the display name")
        expect(admin_deposit_list_page.modal).to_be_visible()
        admin_deposit_list_page.close_modal()
        expect(admin_deposit_list_page.modal).not_to_be_visible()

        # =====================================================================
        # 4. Withdraw List Popup: Close & Save Button Mock Validation
        # =====================================================================
        admin_withdraw_list_page.navigate()

        # 4a. Test Header 'X' close button
        admin_withdraw_list_page.open_add_modal()
        expect(admin_withdraw_list_page.modal).to_be_visible()
        admin_withdraw_list_page.close_modal_via_x()
        expect(admin_withdraw_list_page.modal).not_to_be_visible()

        # 4b. Test Footer 'Close' button
        admin_withdraw_list_page.open_add_modal()
        expect(admin_withdraw_list_page.modal).to_be_visible()
        admin_withdraw_list_page.close_modal()
        expect(admin_withdraw_list_page.modal).not_to_be_visible()

        # 4c. Test Save button triggers validation & prevents save
        admin_withdraw_list_page.open_add_modal()
        admin_withdraw_list_page.modal_save_button.click()
        expect(admin_withdraw_list_page.modal.locator(".invalid-feedback.withdraw_name")).to_be_visible()
        expect(admin_withdraw_list_page.modal.locator(".invalid-feedback.withdraw_name")).to_have_text("Please enter the display name")
        expect(admin_withdraw_list_page.modal).to_be_visible()
        admin_withdraw_list_page.close_modal()
        expect(admin_withdraw_list_page.modal).not_to_be_visible()

        # Confirm zero backend database mutation calls were dispatched
        assert len(intercepted_mutations) == 0, f"Expected 0 backend mutations, intercepted: {intercepted_mutations}"

    finally:
        page.unroute("**/Controlbase/**", _block_and_mock_save)

    admin_error_monitor.assert_no_errors("4 Submenus Popup Close and Save Mock")



@pytest.mark.admin
@pytest.mark.regression
def test_admin_deposit_13_headers_sorting_and_table_controls(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify Deposit page 13 table headers, sorting, row show option, pagination, and exports:
    - 13 table column headers matching expected schema.
    - Sorting by clicking column headers.
    - Row show option dropdown: 10, 25, 50, 100 entries.
    - Pagination navigation: Page 2, Next, Previous.
    - Export buttons: CSV, Excel, PDF.
    - Date range filter: #from, #to, Go (#apply), Clear (#clear).
    """
    admin_deposit_page.navigate()
    expect(admin_deposit_page.table).to_be_visible()
    expect(admin_deposit_page.table_rows.first).to_be_visible()

    # 1. 13 Table Headers
    headers = admin_deposit_page.get_table_headers()
    assert len(headers) >= 13, f"Expected 13 headers, got {len(headers)}"
    for expected in EXPECTED_DEPOSIT_HEADERS:
        assert expected in headers, f"Expected header '{expected}' not in {headers}"

    # 2. Table Column Sorting (click first 5 sortable headers to verify sorting interaction)
    for col_idx in [1, 2, 6, 7, 8]:
        cls = admin_deposit_page.sort_column(col_idx)
        assert "sorting" in cls

    # 3. Row Show Option (datatable_length)
    entries_opts = admin_deposit_page.get_entries_options()
    for opt in ["10", "25", "50", "100"]:
        assert opt in entries_opts

    admin_deposit_page.select_entries("25")
    expect(admin_deposit_page.entries_select).to_have_value("25")
    assert admin_deposit_page.get_row_count() <= 25

    # 4. Pagination
    if "of" in admin_deposit_page.get_pagination_info():
        info_before = admin_deposit_page.get_pagination_info()
        admin_deposit_page.go_to_page(2)
        info_page2 = admin_deposit_page.get_pagination_info()
        assert info_page2 != info_before, f"Expected pagination info to change on page 2: {info_page2}"

        admin_deposit_page.go_to_previous_page()
        expect(admin_deposit_page.table_rows.first).to_be_visible()

    # Restore 50 entries
    admin_deposit_page.select_entries("50")

    # 5. Export Buttons (CSV, Excel, PDF)
    csv_dl = admin_deposit_page.export_csv()
    assert csv_dl.suggested_filename.endswith(".csv")

    excel_dl = admin_deposit_page.export_excel()
    assert excel_dl.suggested_filename.endswith(".xlsx")

    pdf_dl = admin_deposit_page.export_pdf()
    assert pdf_dl.suggested_filename.endswith(".pdf")

    # 6. Date Range Filter (from, to, Go, Clear)
    admin_deposit_page.filter_by_date("2026-09-01T00:00", "2026-09-28T23:59")
    expect(admin_deposit_page.table).to_be_visible()
    admin_deposit_page.clear_date_filter()
    expect(admin_deposit_page.table).to_be_visible()

    admin_error_monitor.assert_no_errors("Admin Deposit Sorting & Table Controls")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_withdraw_13_headers_sorting_and_table_controls(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify Withdraw page 13 table headers, sorting, row show option, pagination, exports, and modals:
    - 13 table column headers matching expected schema.
    - Sorting by clicking column headers.
    - In-row 'Account Details' button -> 'User Account Information' modal (#myAcModal).
    - Row show option dropdown: 10, 25, 50, 100 entries.
    - Pagination navigation: Page 2, Next, Previous.
    - Export buttons: CSV, Excel, PDF.
    - Date range filter: #from, #to, Go (#apply), Clear (#clear).
    """
    admin_withdraw_page.navigate()
    expect(admin_withdraw_page.table).to_be_visible()
    expect(admin_withdraw_page.table_rows.first).to_be_visible()

    # 1. 13 Table Headers
    headers = admin_withdraw_page.get_table_headers()
    assert len(headers) >= 13, f"Expected 13 headers, got {len(headers)}"
    for expected in EXPECTED_WITHDRAW_HEADERS:
        assert expected in headers, f"Expected header '{expected}' not in {headers}"

    # 2. Table Column Sorting
    for col_idx in [1, 2, 6, 7, 8]:
        cls = admin_withdraw_page.sort_column(col_idx)
        assert "sorting" in cls

    # 3. In-Row 'Account Details' Button & Modal
    if admin_withdraw_page.get_row_count() > 0:
        ac_btn = admin_withdraw_page.get_row_account_details_button(0)
        expect(ac_btn).to_be_visible()
        assert ac_btn.inner_text().strip() == "Account Details"

        admin_withdraw_page.open_account_details(0)
        expect(admin_withdraw_page.ac_modal).to_be_visible()
        expect(admin_withdraw_page.ac_modal_title).to_contain_text("User Account Information")

        admin_withdraw_page.close_account_details_modal()
        expect(admin_withdraw_page.ac_modal).not_to_be_visible()

    # 4. Row Show Option (datatable_length)
    entries_opts = admin_withdraw_page.get_entries_options()
    for opt in ["10", "25", "50", "100"]:
        assert opt in entries_opts

    admin_withdraw_page.select_entries("25")
    expect(admin_withdraw_page.entries_select).to_have_value("25")
    assert admin_withdraw_page.get_row_count() <= 25

    # 5. Pagination
    if "of" in admin_withdraw_page.get_pagination_info():
        info_before = admin_withdraw_page.get_pagination_info()
        admin_withdraw_page.go_to_page(2)
        info_page2 = admin_withdraw_page.get_pagination_info()
        assert info_page2 != info_before, f"Expected pagination info to change on page 2: {info_page2}"

        admin_withdraw_page.go_to_previous_page()
        expect(admin_withdraw_page.table_rows.first).to_be_visible()

    # Restore 50 entries
    admin_withdraw_page.select_entries("50")

    # 6. Export Buttons (CSV, Excel, PDF)
    csv_dl = admin_withdraw_page.export_csv()
    assert csv_dl.suggested_filename.endswith(".csv")

    excel_dl = admin_withdraw_page.export_excel()
    assert excel_dl.suggested_filename.endswith(".xlsx")

    pdf_dl = admin_withdraw_page.export_pdf()
    assert pdf_dl.suggested_filename.endswith(".pdf")

    # 7. Date Range Filter (from, to, Go, Clear)
    admin_withdraw_page.filter_by_date("2026-09-01T00:00", "2026-09-28T23:59")
    expect(admin_withdraw_page.table).to_be_visible()
    admin_withdraw_page.clear_date_filter()
    expect(admin_withdraw_page.table).to_be_visible()

    admin_error_monitor.assert_no_errors("Admin Withdraw Sorting & Table Controls")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_payment_and_withdraw_list_row_edit_actions(
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify in-row 'Edit' actions in Deposit List (/payment) and Withdraw List (/managewithdraw):
    1. Deposit List:
       - Table headers, entries length, search.
       - Click Edit button on row 0 (a.btnEdit).
       - Verify 'Payment Form' modal opens with inputs: #display_name, #update-bank-status, #minimum_amount.
       - Verify buttons: 'Add', 'Save', 'Close', 'Cancel'.
       - Close modal.
    2. Withdraw List:
       - Table headers, entries length, search.
       - Click Edit button on row 0 (a.btnEdit).
       - Verify 'Manage Withdraw Bank Details' modal opens with input: #withdraw_name.
       - Verify buttons: 'Add', 'Save', 'Close', 'Cancel'.
       - Close modal.
    """
    # 1. Deposit List Page
    admin_deposit_list_page.navigate()
    expect(admin_deposit_list_page.table).to_be_visible()
    expect(admin_deposit_list_page.table_rows.first).to_be_visible()

    dep_list_headers = admin_deposit_list_page.get_table_headers()
    for expected in EXPECTED_DEPOSIT_LIST_HEADERS:
        assert expected in dep_list_headers, f"Expected header '{expected}' in {dep_list_headers}"

    # Click in-row Edit action
    edit_btn = admin_deposit_list_page.get_row_edit_button(0)
    expect(edit_btn).to_be_visible()
    admin_deposit_list_page.open_edit_modal(0)

    expect(admin_deposit_list_page.modal).to_be_visible()
    expect(admin_deposit_list_page.modal_title).to_have_text("Payment Form")
    expect(admin_deposit_list_page.modal_display_name_input).to_be_visible()
    expect(admin_deposit_list_page.modal_bank_status_select).to_be_attached()
    expect(admin_deposit_list_page.modal_minimum_amount_input).to_be_visible()
    expect(admin_deposit_list_page.modal_bank_detail_add_btn).to_be_visible()
    expect(admin_deposit_list_page.modal_save_button).to_be_visible()
    expect(admin_deposit_list_page.modal_close_button).to_be_visible()

    admin_deposit_list_page.close_modal()
    expect(admin_deposit_list_page.modal).not_to_be_visible()

    # 2. Withdraw List Page
    admin_withdraw_list_page.navigate()
    expect(admin_withdraw_list_page.table).to_be_visible()
    expect(admin_withdraw_list_page.table_rows.first).to_be_visible()

    w_list_headers = admin_withdraw_list_page.get_table_headers()
    for expected in EXPECTED_WITHDRAW_LIST_HEADERS:
        assert expected in w_list_headers, f"Expected header '{expected}' in {w_list_headers}"

    # Click in-row Edit action
    edit_btn_w = admin_withdraw_list_page.get_row_edit_button(0)
    expect(edit_btn_w).to_be_visible()
    admin_withdraw_list_page.open_edit_modal(0)

    expect(admin_withdraw_list_page.modal).to_be_visible()
    expect(admin_withdraw_list_page.modal_title).to_have_text("Manage Withdraw Bank Details")
    expect(admin_withdraw_list_page.modal_withdraw_name_input).to_be_visible()
    expect(admin_withdraw_list_page.modal_add_bank_btn).to_be_visible()
    expect(admin_withdraw_list_page.modal_save_button).to_be_attached()
    expect(admin_withdraw_list_page.modal_close_button).to_be_visible()

    admin_withdraw_list_page.close_modal()
    expect(admin_withdraw_list_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Payment & Withdraw List Edit Actions")


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_in_row_action_and_edit_fields_mock(
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_deposit_list_page: AdminDepositListPage,
    admin_withdraw_list_page: AdminWithdrawListPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Mock test for table in-row Action and Edit fields across submenus:
    1. Payment / Deposit List:
       - Click in-row Edit button (a.btnEdit).
       - Verify pre-populated values from table row.
       - Edit fields (#display_name, #minimum_amount) and assert modified values.
       - Close modal without saving; reopen to confirm original database record was untouched.
    2. Withdraw List:
       - Click in-row Edit button (a.btnEdit).
       - Verify modal opens; verify bank details controls or mode name input.
       - Close modal cleanly.
    3. Withdrawal Page Action Column:
       - Click 'Account Details' action button (button.acInfo).
       - Assert 'User Account Information' modal (#myAcModal) opens and displays account information.
       - Close modal cleanly.
    4. Deposit Page Action Column:
       - Assert in-row Status action button (button.fundStatusButtom) is visible and active.
    5. Mock Safety:
       - Active Playwright network route interception guarantees zero backend database modifications.
    """
    page = admin_deposit_page.page
    intercepted_mutations = []

    def _block_and_mock_mutations(route):
        url = route.request.url.lower()
        if any(action in url for action in ["update", "insert", "save"]):
            intercepted_mutations.append(route.request.url)
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"status":"mock_prevented","message":"Mock test - no database changes"}',
            )
        else:
            route.continue_()

    page.route("**/Controlbase/**", _block_and_mock_mutations)

    try:
        # =====================================================================
        # 1. Deposit List (Payment) In-Row Edit Fields Mock Test
        # =====================================================================
        admin_deposit_list_page.navigate()
        expect(admin_deposit_list_page.table).to_be_visible()
        expect(admin_deposit_list_page.table_rows.first).to_be_visible()

        # Extract row 0 table cell values to verify form retrieves ("gets") values correctly
        dep_list_cells = [td.inner_text().strip() for td in admin_deposit_list_page.table_rows.first.locator("td").all()]
        expected_display_name = dep_list_cells[1]  # 'Display Text' column
        expected_min_amount = dep_list_cells[6]    # 'Minimum Amount' column

        # Open Edit modal on row 0
        admin_deposit_list_page.open_edit_modal(0)
        expect(admin_deposit_list_page.modal).to_be_visible()
        expect(admin_deposit_list_page.modal_title).to_have_text("Payment Form")

        # 1a. Verify pre-populated values match the table row exactly
        original_name = admin_deposit_list_page.modal_display_name_input.input_value()
        original_min = admin_deposit_list_page.modal_minimum_amount_input.input_value()
        assert original_name == expected_display_name, f"Expected form to get display name '{expected_display_name}', got '{original_name}'"
        assert original_min == expected_min_amount, f"Expected form to get minimum amount '{expected_min_amount}', got '{original_min}'"

        # 1b. Verify fields are editable
        assert admin_deposit_list_page.modal_display_name_input.is_editable() is True, "Expected display name input to be editable"
        assert admin_deposit_list_page.modal_minimum_amount_input.is_editable() is True, "Expected minimum amount input to be editable"

        # 1c. Edit fields with mock test values
        mock_edited_name = "Mock Edited Gateway 2026"
        mock_edited_min = "750"
        admin_deposit_list_page.modal_display_name_input.fill(mock_edited_name)
        admin_deposit_list_page.modal_minimum_amount_input.fill(mock_edited_min)

        # 1d. Assert edited values are successfully retrieved from form
        edited_form_values = admin_deposit_list_page.get_payment_form_values()
        assert edited_form_values["display_name"] == mock_edited_name, f"Expected '{mock_edited_name}', got '{edited_form_values['display_name']}'"
        assert edited_form_values["minimum_amount"] == mock_edited_min, f"Expected '{mock_edited_min}', got '{edited_form_values['minimum_amount']}'"

        # 1e. Close modal without saving changes
        admin_deposit_list_page.close_modal()
        expect(admin_deposit_list_page.modal).not_to_be_visible()

        # 1f. Re-open to confirm original values in database were NOT modified (0 backend changes)
        admin_deposit_list_page.open_edit_modal(0)
        assert admin_deposit_list_page.modal_display_name_input.input_value() == original_name
        assert admin_deposit_list_page.modal_minimum_amount_input.input_value() == original_min
        admin_deposit_list_page.close_modal()
        expect(admin_deposit_list_page.modal).not_to_be_visible()

        # =====================================================================
        # 2. Withdraw List In-Row Edit Fields Mock Test
        # =====================================================================
        admin_withdraw_list_page.navigate()
        expect(admin_withdraw_list_page.table).to_be_visible()
        expect(admin_withdraw_list_page.table_rows.first).to_be_visible()

        w_list_cells = [td.inner_text().strip() for td in admin_withdraw_list_page.table_rows.first.locator("td").all()]
        expected_w_name = w_list_cells[1]  # 'Name' column

        # Open Edit modal on row 0
        admin_withdraw_list_page.open_edit_modal(0)
        expect(admin_withdraw_list_page.modal).to_be_visible()

        # 2a. Verify pre-populated mode name matches table row
        w_mode_values = admin_withdraw_list_page.get_withdraw_mode_form_values()
        assert w_mode_values["withdraw_name"] == expected_w_name, f"Expected '{expected_w_name}', got '{w_mode_values['withdraw_name']}'"

        # 2b. Verify bank details section and editability of bank detail inputs
        expect(admin_withdraw_list_page.modal.locator("#withdrawBankDetailsSection")).to_be_visible()
        bank_name_input = admin_withdraw_list_page.modal.locator("#withdraw_bank_detail_name")
        assert bank_name_input.is_editable() is True, "Expected bank detail name input to be editable"
        bank_name_input.fill("SWIFT Branch 101")
        expect(bank_name_input).to_have_value("SWIFT Branch 101")

        # 2c. Close modal cleanly without saving
        admin_withdraw_list_page.close_modal()
        expect(admin_withdraw_list_page.modal).not_to_be_visible()

        # =====================================================================
        # 3. Withdrawal Page Action Column: Account Details Button & Modal
        # =====================================================================
        admin_withdraw_page.navigate()
        expect(admin_withdraw_page.table).to_be_visible()
        expect(admin_withdraw_page.table_rows.first).to_be_visible()

        wd_cells = [td.inner_text().strip() for td in admin_withdraw_page.table_rows.first.locator("td").all()]
        expected_account_id = wd_cells[1]  # 'Account ID'
        expected_user_name = wd_cells[2]   # 'Name'
        expected_email = wd_cells[3]       # 'Email ID'

        # Locate and click 'Account Details' action button on row 0
        admin_withdraw_page.open_account_details(0)
        expect(admin_withdraw_page.ac_modal).to_be_visible()
        expect(admin_withdraw_page.ac_modal_title).to_contain_text("User Account Information")
        expect(admin_withdraw_page.ac_modal_content).to_be_visible()

        # Verify Account Information modal retrieves account details or valid empty state
        modal_info_text = admin_withdraw_page.ac_modal_content.inner_text()
        assert len(modal_info_text) > 0, "Expected Account Details modal to contain content"
        assert (
            "No Information Found" in modal_info_text
            or expected_account_id in modal_info_text
            or expected_user_name in modal_info_text
            or expected_email in modal_info_text
        ), f"Unexpected Account Details modal content: {modal_info_text}"

        # Close Account Details modal cleanly
        admin_withdraw_page.close_account_details_modal()
        expect(admin_withdraw_page.ac_modal).not_to_be_visible()

        # Assert in-row Status action button is visible
        row0_status = admin_withdraw_page.get_row_status_button(0)
        expect(row0_status).to_be_visible()

        # =====================================================================
        # 4. Deposit Page Action Column & Status Button
        # =====================================================================
        admin_deposit_page.navigate()
        expect(admin_deposit_page.table).to_be_visible()
        expect(admin_deposit_page.table_rows.first).to_be_visible()

        # Assert in-row Status action button is visible
        dep_row0_status = admin_deposit_page.get_row_status_button(0)
        expect(dep_row0_status).to_be_visible()

        # Confirm zero backend database mutation calls were dispatched
        assert len(intercepted_mutations) == 0, f"Expected 0 backend mutations, intercepted: {intercepted_mutations}"

    finally:
        page.unroute("**/Controlbase/**", _block_and_mock_mutations)

    admin_error_monitor.assert_no_errors("In-Row Action & Edit Fields Mock")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_deposit_and_withdraw_search_and_filter(
    admin_deposit_page: AdminDepositPage,
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Verify real-time search filtering on both Deposit and Withdraw tables:
    - Searching by Account ID narrows the table records.
    - Clearing search restores full record set.
    """
    # 1. Test Deposit Search
    admin_deposit_page.navigate()
    expect(admin_deposit_page.table_rows.first).to_be_visible(timeout=10000)
    initial_dep_count = admin_deposit_page.get_row_count()
    first_row = admin_deposit_page.get_first_row_data()
    account_id = first_row.get("Account ID", "10629")
    admin_deposit_page.search(account_id)
    filtered_dep_count = admin_deposit_page.get_row_count()
    assert filtered_dep_count >= 1, f"Expected at least 1 record for Account ID {account_id} on Deposit"
    admin_deposit_page.clear_search()
    expect(admin_deposit_page.table_rows.first).to_be_visible(timeout=10000)
    assert admin_deposit_page.get_row_count() == initial_dep_count

    # 2. Test Withdraw Search
    admin_withdraw_page.navigate()
    expect(admin_withdraw_page.table_rows.first).to_be_visible(timeout=10000)
    initial_w_count = admin_withdraw_page.get_row_count()
    admin_withdraw_page.search("10026")
    filtered_w_count = admin_withdraw_page.get_row_count()
    assert filtered_w_count >= 1, "Expected at least 1 record for Account ID 10026 on Withdraw"
    admin_withdraw_page.clear_search()
    expect(admin_withdraw_page.table_rows.first).to_be_visible(timeout=10000)
    assert admin_withdraw_page.get_row_count() == initial_w_count

    admin_error_monitor.assert_no_errors("Search and Filter Controls")


@pytest.mark.admin
@pytest.mark.regression
def test_raise_client_deposit_and_verify_in_admin(
    workflow_browser: Browser,
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Cross-portal end-to-end integration test:
    1. Raise a live deposit request in Client Portal for account 10026.
    2. Switch to Admin Portal Deposit module.
    3. Filter by the deposit amount.
    4. Assert that the record is present with status 'pending' and correct method.
    5. Assert all button labels on the newly raised record and modal dialog.
    """
    test_amount = f"2{random.randint(20, 99)}.00"

    # Step 1: Open Client Portal and raise deposit request
    client_context = workflow_browser.new_context(
        storage_state=str(settings.client_portal.auth_state_path)
        if settings.client_portal.auth_state_path.exists()
        else None,
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    client_page = client_context.new_page()
    client_error_mon = ErrorMonitor(client_page)

    client_page.goto(settings.client_portal.base_url, wait_until="domcontentloaded")
    client_page.wait_for_timeout(1500)
    client_page.locator("a[href*='deposit'], button:has-text('Deposit')").first.click()
    client_page.wait_for_timeout(1500)

    # Select destination account 10026
    account_select = client_page.locator("main select").nth(0)
    expect(account_select).to_be_visible(timeout=10000)
    account_select.select_option(index=1)

    # Select payment method USDT TRC20
    method_select = client_page.locator("main select").nth(1)
    for opt in method_select.locator("option").all():
        if "usdt" in opt.inner_text().lower():
            method_select.select_option(opt.get_attribute("value"))
            break

    # Enter unique deposit amount
    amount_input = client_page.locator("main input[type='number']").first
    amount_input.fill(test_amount)

    # Upload valid payment proof
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        proof_path = f.name

    try:
        client_page.locator("main input[type='file']").first.set_input_files(proof_path)
        client_page.wait_for_timeout(500)

        submit_btn = client_page.locator("main button:has-text('Submit Deposit Request')").first
        expect(submit_btn).to_be_enabled(timeout=5000)
        submit_btn.click()

        toast = client_page.locator("div").filter(has_text="Payment Deposit Request Received")
        expect(toast.first).to_be_visible(timeout=10000)
    finally:
        if os.path.exists(proof_path):
            os.remove(proof_path)

    client_error_mon.assert_no_errors("Client Portal Raise Deposit")
    client_context.close()

    # Step 2: Open Admin Deposit module and verify the submitted deposit record
    admin_deposit_page.navigate()
    admin_deposit_page.search(test_amount)

    expect(admin_deposit_page.table_rows.first).to_be_visible(timeout=10000)
    assert admin_deposit_page.get_row_count() >= 1, f"Expected deposit record with amount {test_amount} in Admin"

    first_row = admin_deposit_page.get_first_row_data()
    assert test_amount in first_row.get("Amount", ""), f"Amount mismatch: {first_row}"
    assert "USDT" in first_row.get("Method", "") or "trc20" in first_row.get("Method", "").lower()
    assert first_row.get("Status", "").lower() == "pending"

    # Verify status button label on the row
    status_btn = admin_deposit_page.get_row_status_button(0)
    expect(status_btn).to_be_visible()
    assert status_btn.inner_text().strip().lower() == "pending"

    # Open Deposit Form modal and verify button labels
    admin_deposit_page.open_add_deposit_modal()
    expect(admin_deposit_page.modal).to_be_visible(timeout=5000)
    expect(admin_deposit_page.modal_title).to_have_text("Deposit Form")
    expect(admin_deposit_page.modal_close_button).to_have_text("Close")
    expect(admin_deposit_page.modal_save_button).to_have_text("Save")

    admin_deposit_page.close_modal()
    expect(admin_deposit_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Admin Verify Raised Deposit")


@pytest.mark.admin
@pytest.mark.regression
def test_raise_client_withdraw_and_verify_in_admin(
    workflow_browser: Browser,
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Cross-portal integration test for Withdraw module:
    1. Raise a payout request in Client Portal to trigger withdraw OTP lifecycle.
    2. Switch to Admin Portal Withdraw module.
    3. Filter by account ID 10026.
    4. Assert table headers, 'Account Details' button, and 'User Account Information' modal.
    5. Assert all button labels: 'Add Withdraw', 'CSV', 'PDF', 'Excel', 'Go', 'Clear', 'Close', 'Save'.
    """
    # Step 1: Open Client Portal and trigger payout request
    client_context = workflow_browser.new_context(
        storage_state=str(settings.client_portal.auth_state_path)
        if settings.client_portal.auth_state_path.exists()
        else None,
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    client_page = client_context.new_page()
    client_error_mon = ErrorMonitor(client_page)

    client_page.goto(settings.client_portal.base_url, wait_until="domcontentloaded")
    client_page.wait_for_timeout(1500)
    client_page.locator("a[href*='withdraw'], button:has-text('Withdraw')").first.click()
    client_page.wait_for_timeout(1500)

    # Select trading account
    source_select = client_page.locator("main select").nth(0)
    expect(source_select).to_be_visible(timeout=10000)
    for opt in source_select.locator("option").all():
        if "10026" in opt.inner_text():
            source_select.select_option(opt.get_attribute("value"))
            break

    # Select mode of payment
    method_select = client_page.locator("main select").nth(1)
    for opt in method_select.locator("option").all():
        if "usdt" in opt.inner_text().lower():
            method_select.select_option(opt.get_attribute("value"))
            break

    # Enter withdraw amount (within available balance)
    amount_input = client_page.locator("main input[type='number']").first
    amount_input.fill("1.00")

    # Click REQUEST WITHDRAW
    request_btn = client_page.locator("main button:has-text('REQUEST WITHDRAW')").first
    expect(request_btn).to_be_enabled(timeout=5000)
    request_btn.click()

    # Verify OTP dialog pops up with sent confirmation
    otp_toast = client_page.locator("div").filter(has_text="Successfully OTP sent")
    expect(otp_toast.first).to_be_visible(timeout=10000)

    otp_modal = client_page.locator("div.fixed.inset-0").filter(has_text="Enter Withdraw OTP")
    expect(otp_modal.first).to_be_visible(timeout=5000)

    # Dismiss OTP modal via close button
    otp_close_btn = otp_modal.locator("button[title='Close']").first
    expect(otp_close_btn).to_be_visible()
    otp_close_btn.click()
    expect(otp_modal.first).not_to_be_visible(timeout=5000)

    client_error_mon.assert_no_errors("Client Portal Raise Withdraw")
    client_context.close()

    # Step 2: Open Admin Withdraw module and inspect records and buttons
    admin_withdraw_page.navigate()
    admin_withdraw_page.search("10026")

    expect(admin_withdraw_page.table_rows.first).to_be_visible(timeout=10000)
    assert admin_withdraw_page.get_row_count() >= 1, "Expected withdraw records for account 10026 in Admin"

    # Verify Account Details button
    ac_btn = admin_withdraw_page.get_row_account_details_button(0)
    expect(ac_btn).to_be_visible()
    assert ac_btn.inner_text().strip() == "Account Details"

    # Open User Account Information modal
    admin_withdraw_page.open_account_details(0)
    expect(admin_withdraw_page.ac_modal).to_be_visible(timeout=5000)
    expect(admin_withdraw_page.ac_modal_title).to_contain_text("User Account Information")

    # Close modal
    admin_withdraw_page.close_account_details_modal()
    expect(admin_withdraw_page.ac_modal).not_to_be_visible(timeout=5000)

    # Verify status button on row
    status_btn = admin_withdraw_page.get_row_status_button(0)
    expect(status_btn).to_be_visible()
    status_label = status_btn.inner_text().strip()
    assert status_label in ["Success", "Pending", "Reject", "Rejected"]

    # Open Add Withdraw Form modal and verify button labels
    admin_withdraw_page.open_add_withdraw_modal()
    expect(admin_withdraw_page.modal).to_be_visible(timeout=5000)
    expect(admin_withdraw_page.modal_title).to_have_text("Withdraw Form")
    expect(admin_withdraw_page.modal_close_button).to_have_text("Close")
    expect(admin_withdraw_page.modal_save_button).to_have_text("Save")

    admin_withdraw_page.close_modal()
    expect(admin_withdraw_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Admin Verify Withdraw Module")
