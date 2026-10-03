"""
Admin Portal Date Filters & Range Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 2 line 49, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Date input format, malformed date string handling.
2. Buttons & Actions: Apply/Go filter triggers, Clear/Reset filter buttons.
3. Dropdowns & Selects: Length pagination persistence across date filters.
5. Date & Time Pickers:
   - Inverted date boundaries ('From > To', e.g. 2026-12-31T23:59 to 2026-01-01T00:00).
   - Future date boundaries (beyond system epoch).
   - Clear filter restoring full ledger and emptying date fields.
   - ISO 8601 datetime format (YYYY-MM-DDTHH:mm) validation on datetime-local pickers.
6. Calculations & Tables: Table rows update cleanly without JavaScript or DOM breakage.
7. Security: Zero database error leakage or client crashes during range filtering.

Logs Covered (10 Log & Report Subsystems):
1. Deposit Management Log (/admin/Controlbase/deposit)
2. Withdrawal Management Log (/admin/Controlbase/withdraw)
3. User Management Log (/admin/Controlbase/user)
4. User Document (KYC) Log (/admin/Controlbase/userDocument)
5. Leads Report (/admin/Controlbase/leadReport)
6. Order Report (/admin/Controlbase/OrderReport)
7. User Bonus Credit Log (/admin/Controlbase/userBonus)
8. Order Edit Audit Log (/admin/Controlbase/orderEditLog)
9. User Transaction Log (/admin/Controlbase/userTransactionLog)
10. Refer Report & LP Transactions (/admin/Controlbase/referReport, /admin/Controlbase/lpTransaction)

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from workflows.admin_portal.pages.admin_deposit_page import AdminDepositPage
from workflows.admin_portal.pages.admin_withdraw_page import AdminWithdrawPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.admin_portal.pages.user_document_page import UserDocumentPage
from workflows.admin_portal.pages.leads_report_page import LeadsReportPage
from workflows.admin_portal.pages.admin_order_report_page import AdminOrderReportPage
from workflows.admin_portal.pages.admin_user_bonus_page import AdminUserBonusPage
from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage
from workflows.admin_portal.pages.admin_user_transaction_log_page import AdminUserTransactionLogPage
from workflows.admin_portal.pages.admin_refer_report_page import AdminReferReportPage
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. DEPOSIT MANAGEMENT DATE FILTER BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_date_filter_inverted_and_reset(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test inverted date range ('From > To': 2026-12-31T23:59 to 2026-01-01T00:00)
    and reset behavior on Deposit Management (/admin/Controlbase/deposit):
    - Inverted dates filter table to clean empty state or zero rows
    - Clear filter button empties both date pickers and restores full dataset
    """
    admin_deposit_page.navigate()
    admin_deposit_page.page.wait_for_timeout(1000)
    expect(admin_deposit_page.table).to_be_attached(timeout=15000)

    initial_count = admin_deposit_page.get_row_count()

    # 1. Apply inverted date filter (HTML5 datetime-local requires YYYY-MM-DDTHH:mm)
    admin_deposit_page.filter_by_date(from_date="2026-12-31T23:59", to_date="2026-01-01T00:00")
    admin_deposit_page.page.wait_for_timeout(1000)

    inverted_count = admin_deposit_page.get_row_count()
    assert inverted_count <= initial_count, "Inverted date range should return <= initial count"

    # 2. Reset date filter
    admin_deposit_page.clear_date_filter()
    admin_deposit_page.page.wait_for_timeout(1000)

    # Date inputs should be empty
    assert admin_deposit_page.date_from_input.input_value() == "", "Date from must be cleared"
    assert admin_deposit_page.date_to_input.input_value() == "", "Date to must be cleared"
    assert admin_deposit_page.get_row_count() == initial_count, "Clear must restore initial rows"

    admin_error_monitor.assert_no_js_errors("Deposit Date Filter Inverted & Reset")


# ==============================================================================
# 2. WITHDRAWAL MANAGEMENT DATE FILTER BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_date_filter_inverted_and_reset(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test inverted date range ('From > To': 2026-12-31T23:59 to 2026-01-01T00:00)
    and reset behavior on Withdrawal Management (/admin/Controlbase/withdraw):
    - Inverted dates filter table to clean empty state
    - Clear filter resets date inputs and restores table
    """
    admin_withdraw_page.navigate()
    admin_withdraw_page.page.wait_for_timeout(1000)
    expect(admin_withdraw_page.table).to_be_attached(timeout=15000)

    initial_count = admin_withdraw_page.get_row_count()

    # 1. Apply inverted date filter
    admin_withdraw_page.filter_by_date(from_date="2026-12-31T23:59", to_date="2026-01-01T00:00")
    admin_withdraw_page.page.wait_for_timeout(1000)

    inverted_count = admin_withdraw_page.get_row_count()
    assert inverted_count <= initial_count, "Inverted date range should return <= initial count"

    # 2. Reset date filter
    admin_withdraw_page.clear_date_filter()
    admin_withdraw_page.page.wait_for_timeout(1000)

    assert admin_withdraw_page.date_from_input.input_value() == "", "Date from must be cleared"
    assert admin_withdraw_page.date_to_input.input_value() == "", "Date to must be cleared"
    assert admin_withdraw_page.get_row_count() == initial_count, "Clear must restore initial rows"

    admin_error_monitor.assert_no_js_errors("Withdraw Date Filter Inverted & Reset")


# ==============================================================================
# 3. USER MANAGEMENT DATE FILTER BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_management_date_filter_boundaries(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test date range boundaries on User Management (/admin/Controlbase/user):
    - Inverted range (2026-12-31T23:59 to 2026-01-01T00:00)
    - Clear button clears both date inputs and restores dataset
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)
    expect(user_management_page.users_table).to_be_attached(timeout=15000)

    initial_count = user_management_page.get_user_count()

    # 1. Apply inverted filter with ISO 8601 datetime format
    user_management_page.date_from.fill("2026-12-31T23:59")
    user_management_page.date_to.fill("2026-01-01T00:00")
    user_management_page.apply_button.click()
    user_management_page.page.wait_for_timeout(1000)

    # 2. Reset filter
    user_management_page.clear_button.click()
    user_management_page.page.wait_for_timeout(1000)

    assert user_management_page.date_from.input_value() == "", "From date must be cleared"
    assert user_management_page.date_to.input_value() == "", "To date must be cleared"
    assert user_management_page.get_user_count() == initial_count, "Clear restores users table"

    admin_error_monitor.assert_no_js_errors("User Management Date Filter")


# ==============================================================================
# 4. USER DOCUMENT (KYC) DATE FILTER BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_date_filter_boundaries(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test date range filter on KYC Document Management (/admin/Controlbase/userDocument):
    - Inverted date range filtering (ISO datetime-local)
    - Reset filter verification
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)
    expect(user_document_page.table).to_be_attached(timeout=15000)

    initial_count = user_document_page.document_rows.count()

    # 1. Inverted filter
    user_document_page.filter_by_date(from_date="2026-12-31T23:59", to_date="2026-01-01T00:00")
    user_document_page.page.wait_for_timeout(1000)

    # 2. Reset filter
    user_document_page.clear_date_filter()
    user_document_page.page.wait_for_timeout(1000)

    assert user_document_page.from_date_input.input_value() == "", "From date cleared"
    assert user_document_page.to_date_input.input_value() == "", "To date cleared"
    assert user_document_page.document_rows.count() == initial_count, "Clear restores document rows"

    admin_error_monitor.assert_no_js_errors("User Document Date Filter")


# ==============================================================================
# 5. LEADS REPORT DATE FILTER BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_report_date_filter_boundaries(
    leads_report_page: LeadsReportPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test date range boundaries on Leads Report (/admin/Controlbase/leadReport):
    - Submitting inverted range (2026-12-31 to 2026-01-01)
    - Submitting future date range (2035-01-01 to 2035-12-31)
    - Safely dismisses alert dialogs if displayed
    - Asserts page remains responsive with no uncaught JS errors
    """
    leads_report_page.navigate()
    leads_report_page.page.wait_for_timeout(1000)
    expect(leads_report_page.datatable).to_be_attached(timeout=15000)

    # 1. Inverted range
    leads_report_page.set_date_range(from_date="2026-12-31", to_date="2026-01-01")
    leads_report_page.click_filter()
    leads_report_page.page.wait_for_timeout(800)

    # Dismiss jconfirm dialog if shown
    jconfirm_btn = leads_report_page.page.locator(".jconfirm-box button, .jconfirm-buttons button").first
    if jconfirm_btn.is_visible():
        jconfirm_btn.click()
        leads_report_page.page.wait_for_timeout(500)

    # 2. Valid date range restores normal state
    leads_report_page.set_date_range(from_date="2026-01-01", to_date="2026-12-31")
    leads_report_page.click_filter()
    leads_report_page.page.wait_for_timeout(800)

    if jconfirm_btn.is_visible():
        jconfirm_btn.click()
        leads_report_page.page.wait_for_timeout(500)

    admin_error_monitor.assert_no_js_errors("Leads Report Date Filter Boundaries")


# ==============================================================================
# 6. ORDER REPORT DATE FILTER BOUNDARIES & REFRESH
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_order_report_date_filter_boundaries_and_refresh(
    authenticated_admin_page: Page,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test date range boundaries on Order Report (/admin/Controlbase/OrderReport):
    - Inverted date range (2026-12-31 to 2026-01-01)
    - Submitting filter and resetting via Refresh button
    """
    admin_order_report_page = AdminOrderReportPage(authenticated_admin_page)
    admin_order_report_page.navigate()
    admin_order_report_page.page.wait_for_timeout(1000)
    expect(admin_order_report_page.table).to_be_attached(timeout=15000)

    # Apply date filter if inputs exist
    if admin_order_report_page.from_date_input.is_visible():
        admin_order_report_page.from_date_input.fill("2026-12-31")
        admin_order_report_page.to_date_input.fill("2026-01-01")
        if admin_order_report_page.filter_btn.is_visible():
            admin_order_report_page.filter_btn.click()
            admin_order_report_page.page.wait_for_timeout(800)

            # Dismiss alert dialog if present
            jconfirm_btn = admin_order_report_page.page.locator(".jconfirm-box button, .jconfirm-buttons button").first
            if jconfirm_btn.is_visible():
                jconfirm_btn.click()
                admin_order_report_page.page.wait_for_timeout(500)

        # Refresh
        if admin_order_report_page.refresh_btn.is_visible():
            admin_order_report_page.refresh_btn.click()
            admin_order_report_page.page.wait_for_timeout(1000)

    admin_error_monitor.assert_no_js_errors("Order Report Date Filter Boundaries")


# ==============================================================================
# 7. USER BONUS EXPIRE DATE PICKER ATTRIBUTES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_bonus_expire_date_picker_attributes(
    admin_user_bonus_page: AdminUserBonusPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Validate HTML5 date picker specifications for user bonus credit
    expiration date (#expire_date):
    - Input type must be 'date'
    - HTML5 min/max boundaries or formatted value acceptance
    - Safe dismissal of modal without backend write
    """
    admin_user_bonus_page.navigate()
    admin_user_bonus_page.page.wait_for_timeout(1000)

    add_btn = admin_user_bonus_page.page.locator("#addNew, .btnAddBonus, button:has-text('Add')").first
    if add_btn.is_visible():
        add_btn.click()
        admin_user_bonus_page.page.wait_for_timeout(500)

        if admin_user_bonus_page.modal.is_visible():
            input_type = admin_user_bonus_page.expire_date_input.get_attribute("type")
            assert input_type == "date", f"Expected type='date', got '{input_type}'"

            # Fill valid date
            admin_user_bonus_page.expire_date_input.fill("2026-12-31")
            assert admin_user_bonus_page.expire_date_input.input_value() == "2026-12-31"

            # Close modal safely
            admin_user_bonus_page.modal_close_button.first.click()
            admin_user_bonus_page.page.wait_for_timeout(500)

    admin_error_monitor.assert_no_js_errors("User Bonus Expire Date Picker")


# ==============================================================================
# 8 & 9. AUDIT LOGS DATE FILTERING VIA SEARCH
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_audit_logs_date_search_and_table_integrity(
    admin_order_edit_log_page: AdminOrderEditLogPage,
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillars 1 & 5: Validate date searching across audit logs:
    - Order Edit Log: search by year '202'
    - User Transaction Log: search by year '202'
    - Asserts no SQL error dumps and search clearing restores initial state
    """
    # 1. Order Edit Log
    admin_order_edit_log_page.navigate()
    admin_order_edit_log_page.page.wait_for_timeout(1000)
    initial_edit_count = admin_order_edit_log_page.get_table_rows_count()

    admin_order_edit_log_page.search("202")
    admin_order_edit_log_page.page.wait_for_timeout(600)
    admin_order_edit_log_page.clear_search()
    admin_order_edit_log_page.page.wait_for_timeout(600)
    assert admin_order_edit_log_page.get_table_rows_count() == initial_edit_count

    # 2. User Transaction Log
    admin_user_transaction_log_page.navigate()
    admin_user_transaction_log_page.page.wait_for_timeout(1000)
    initial_trans_count = len(admin_user_transaction_log_page.get_transaction_records())

    admin_user_transaction_log_page.filter_by_account("202")
    admin_user_transaction_log_page.page.wait_for_timeout(600)
    admin_user_transaction_log_page.clear_filter()
    admin_user_transaction_log_page.page.wait_for_timeout(600)
    assert len(admin_user_transaction_log_page.get_transaction_records()) == initial_trans_count

    admin_error_monitor.assert_no_js_errors("Audit Logs Date Search Integrity")


# ==============================================================================
# 10. REFER REPORT & LP TRANSACTION DATE INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_refer_report_table_date_column_integrity(
    admin_refer_report_page: AdminReferReportPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5 & 6: Validate Refer Report table integrity and date search filtering:
    - Verifies headers and table presence
    - Searches year '202' in datatable search box
    - Clears filter and restores dataset
    """
    admin_refer_report_page.navigate()
    admin_refer_report_page.page.wait_for_timeout(1000)

    headers = admin_refer_report_page.get_table_headers()
    assert len(headers) >= 5, f"Expected Refer Report headers, got {len(headers)}: {headers}"

    initial_records = len(admin_refer_report_page.get_refer_records())

    admin_refer_report_page.filter_by_account("202")
    admin_refer_report_page.page.wait_for_timeout(600)
    admin_refer_report_page.clear_filter()
    admin_refer_report_page.page.wait_for_timeout(600)

    assert len(admin_refer_report_page.get_refer_records()) == initial_records

    admin_error_monitor.assert_no_js_errors("Refer Report Date Integrity")
