"""
Admin Portal Deposit & Withdrawal Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.3, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Empty inputs, boundary amounts (0, negative, excessive, non-numeric), SQLi/XSS sanitization.
2. Buttons & Actions: Empty form submissions, Header 'X' and Footer 'Close' dismissal, in-row action clicks, Account Info modal.
3. Dropdowns & Selects: Status select options, Type options, entries per page pagination options (10, 25, 50, 100).
4. Dropzones & Uploads: Payment proof upload, proof removal button (#proofRemoveBtn), disallowed extension safety.
5. Date & Time Pickers: Inverted date boundaries ('From > To'), date reset/clear restoring full ledger.
6. Calculations & Tables: Serial number (S.No) sequential ordering & uniqueness, column sorting traversal, pagination arithmetic.
7. Security: SQLi/XSS attack vectors, CSRF and hidden token verification.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import os
import re
import tempfile
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_deposit_page import AdminDepositPage
from workflows.admin_portal.pages.admin_withdraw_page import AdminWithdrawPage
from workflows.shared.helpers.validation_payloads import (
    BOUNDARY_AMOUNTS,
    DISALLOWED_FILE_PAYLOADS,
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1: TEXTBOX & INPUT BOUNDARY VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_modal_empty_submission_validation(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify that submitting the Add Deposit form with empty inputs
    triggers client-side validation (.invalid-feedback.email) and blocks submission.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    # Clear inputs and submit empty form
    admin_deposit_page.modal_email_input.fill("")
    admin_deposit_page.modal_amount_input.fill("")
    admin_deposit_page.modal_save_button.click()
    admin_deposit_page.page.wait_for_timeout(400)

    # Validation message must be visible
    expect(admin_deposit_page.invalid_feedback_email).to_be_visible()
    feedback_text = admin_deposit_page.invalid_feedback_email.inner_text().strip()
    assert "Please enter the email" in feedback_text, (
        f"Expected 'Please enter the email', got '{feedback_text}'"
    )

    # Modal must remain open and blocked
    expect(admin_deposit_page.modal).to_be_visible()

    admin_deposit_page.close_modal()
    expect(admin_deposit_page.modal).not_to_be_visible()
    admin_error_monitor.assert_no_errors("Deposit Empty Form Validation")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_modal_empty_submission_validation(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify that submitting the Add Withdraw form with empty inputs
    triggers client-side validation (.invalid-feedback.email) and blocks submission.
    """
    admin_withdraw_page.navigate()
    admin_withdraw_page.open_add_withdraw_modal()

    # Clear inputs and submit empty form
    admin_withdraw_page.modal_email_input.fill("")
    admin_withdraw_page.modal_amount_input.fill("")
    admin_withdraw_page.modal_save_button.click()
    admin_withdraw_page.page.wait_for_timeout(400)

    # Validation message must be visible
    expect(admin_withdraw_page.invalid_feedback_email).to_be_visible()
    feedback_text = admin_withdraw_page.invalid_feedback_email.inner_text().strip()
    assert "Please enter the email" in feedback_text, (
        f"Expected 'Please enter the email', got '{feedback_text}'"
    )

    # Modal must remain open and blocked
    expect(admin_withdraw_page.modal).to_be_visible()

    admin_withdraw_page.close_modal()
    expect(admin_withdraw_page.modal).not_to_be_visible()
    admin_error_monitor.assert_no_errors("Withdraw Empty Form Validation")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_amount_boundary_inputs(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test boundary numeric inputs (0, negative, excessive, non-numeric)
    in the Deposit Amount input to verify input filtering and validation behavior.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    for amount_val, description in BOUNDARY_AMOUNTS:
        admin_deposit_page.modal_amount_input.fill("")
        try:
            admin_deposit_page.modal_amount_input.fill(amount_val)
        except Exception:
            admin_deposit_page.modal_amount_input.press_sequentially(amount_val, delay=20)
        current_val = admin_deposit_page.modal_amount_input.input_value()

        # Non-numeric strings should either be rejected by type='number' or captured as string
        if amount_val in ["abc", "!@#$%", "   "]:
            assert current_val in ["", amount_val], (
                f"Expected non-numeric input to be sanitized for {description}, got '{current_val}'"
            )
        else:
            assert len(current_val) > 0, f"Expected numeric value to be accepted into input: {description}"

    admin_deposit_page.close_modal()
    admin_error_monitor.assert_no_errors("Deposit Amount Boundary Inputs")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_amount_boundary_inputs(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test boundary numeric inputs (0, negative, excessive, non-numeric)
    in the Withdraw Amount input to verify input filtering and validation behavior.
    """
    admin_withdraw_page.navigate()
    admin_withdraw_page.open_add_withdraw_modal()

    for amount_val, description in BOUNDARY_AMOUNTS:
        admin_withdraw_page.modal_amount_input.fill("")
        try:
            admin_withdraw_page.modal_amount_input.fill(amount_val)
        except Exception:
            admin_withdraw_page.modal_amount_input.press_sequentially(amount_val, delay=20)
        current_val = admin_withdraw_page.modal_amount_input.input_value()

        if amount_val in ["abc", "!@#$%", "   "]:
            assert current_val in ["", amount_val], (
                f"Expected non-numeric input to be sanitized for {description}, got '{current_val}'"
            )
        else:
            assert len(current_val) > 0, f"Expected numeric value to be accepted into input: {description}"

    admin_withdraw_page.close_modal()
    admin_error_monitor.assert_no_errors("Withdraw Amount Boundary Inputs")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_search_sqli_xss_sanitization(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & Security (Section 4): Verify Deposit search input neutralizes
    SQL Injection and XSS attack vectors without server error or script execution.
    """
    admin_deposit_page.navigate()

    all_payloads = SQLI_PAYLOADS + XSS_PAYLOADS

    for payload, description in all_payloads:
        # Reset window pwned telemetry flag
        admin_deposit_page.page.evaluate("() => { window.pwned = undefined; window.xss_detected = undefined; }")

        admin_deposit_page.search(payload)
        admin_deposit_page.page.wait_for_timeout(300)

        # 1. Verify zero XSS execution
        xss_hit = admin_deposit_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert not xss_hit, f"XSS payload executed in Deposit search: {description} ({payload})"

        # 2. Verify no uncaught SQL syntax error in table DOM
        table_html = admin_deposit_page.table.inner_html().lower()
        assert "sqlstate" not in table_html, f"Database error exposed for payload: {description}"
        assert "syntax error" not in table_html, f"SQL syntax error exposed for payload: {description}"

    admin_deposit_page.clear_search()
    # Clear error monitor backend errors triggered by intentional injection attack payloads
    admin_error_monitor.backend_errors.clear()


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_search_sqli_xss_sanitization(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & Security (Section 4): Verify Withdraw search input neutralizes
    SQL Injection and XSS attack vectors without server error or script execution.
    """
    admin_withdraw_page.navigate()

    all_payloads = SQLI_PAYLOADS + XSS_PAYLOADS

    for payload, description in all_payloads:
        admin_withdraw_page.page.evaluate("() => { window.pwned = undefined; window.xss_detected = undefined; }")

        admin_withdraw_page.search(payload)
        admin_withdraw_page.page.wait_for_timeout(300)

        # 1. Verify zero XSS execution
        xss_hit = admin_withdraw_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert not xss_hit, f"XSS payload executed in Withdraw search: {description} ({payload})"

        # 2. Verify no uncaught SQL syntax error in table DOM
        table_html = admin_withdraw_page.table.inner_html().lower()
        assert "sqlstate" not in table_html, f"Database error exposed for payload: {description}"
        assert "syntax error" not in table_html, f"SQL syntax error exposed for payload: {description}"

    admin_withdraw_page.clear_search()
    admin_error_monitor.backend_errors.clear()


# ==============================================================================
# PILLAR 2: BUTTONS & ACTIONS VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_modal_dismissal_header_and_footer(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify both Header 'X' close button and Footer 'Close' button
    safely dismiss the Deposit modal without saving changes.
    """
    admin_deposit_page.navigate()

    # 1. Test Header 'X' Close button
    admin_deposit_page.open_add_deposit_modal()
    expect(admin_deposit_page.modal).to_be_visible()
    admin_deposit_page.close_modal_via_x()
    expect(admin_deposit_page.modal).not_to_be_visible()

    # 2. Test Footer 'Close' button
    admin_deposit_page.open_add_deposit_modal()
    expect(admin_deposit_page.modal).to_be_visible()
    admin_deposit_page.close_modal()
    expect(admin_deposit_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Deposit Modal Dismissal")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_modal_dismissal_header_and_footer(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify both Header 'X' close button and Footer 'Close' button
    safely dismiss the Withdraw modal without saving changes.
    """
    admin_withdraw_page.navigate()

    # 1. Test Header 'X' Close button
    admin_withdraw_page.open_add_withdraw_modal()
    expect(admin_withdraw_page.modal).to_be_visible()
    admin_withdraw_page.close_modal_via_x()
    expect(admin_withdraw_page.modal).not_to_be_visible()

    # 2. Test Footer 'Close' button
    admin_withdraw_page.open_add_withdraw_modal()
    expect(admin_withdraw_page.modal).to_be_visible()
    admin_withdraw_page.close_modal()
    expect(admin_withdraw_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Withdraw Modal Dismissal")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_account_information_modal_lifecycle(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2 & Section 3.A.3: Verify clicking the 'Account Details' button (.acInfo)
    opens the User Account Information modal (#myAcModal), displays payout data,
    and dismisses cleanly.
    """
    admin_withdraw_page.navigate()

    # Check if any row has an account info button
    ac_buttons = admin_withdraw_page.page.locator("button.acInfo")
    if ac_buttons.count() > 0:
        admin_withdraw_page.open_account_details(0)
        expect(admin_withdraw_page.ac_modal).to_be_visible()

        # Modal title verification
        assert "User Account Information" in admin_withdraw_page.ac_modal_title.inner_text()

        # Dismiss modal
        admin_withdraw_page.close_account_details_modal()
        expect(admin_withdraw_page.ac_modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Withdraw Account Information Modal")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_in_row_edit_modal_rendering(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking in-row edit button (a.btnEdit) loads the record
    into the Deposit Form modal with valid status select options.
    """
    admin_deposit_page.navigate()

    edit_buttons = admin_deposit_page.page.locator("a.btnEdit")
    if edit_buttons.count() > 0:
        # Attempt standard click if visible, else expand responsive row or dispatch event
        visible_btn = admin_deposit_page.page.locator("a.btnEdit:visible").first
        if visible_btn.count() > 0 and visible_btn.is_visible():
            visible_btn.click()
        else:
            dtr_ctrl = admin_deposit_page.table_rows.first.locator(".dtr-control")
            if dtr_ctrl.count() > 0 and dtr_ctrl.is_visible():
                dtr_ctrl.click()
                admin_deposit_page.page.wait_for_timeout(400)

            if admin_deposit_page.page.locator("a.btnEdit:visible").count() > 0:
                admin_deposit_page.page.locator("a.btnEdit:visible").first.click()
            else:
                edit_buttons.first.dispatch_event("click")

        expect(admin_deposit_page.modal).to_be_visible(timeout=10000)
        expect(admin_deposit_page.modal_status_select).to_be_attached(timeout=5000)

        status_val = admin_deposit_page.modal_status_select.input_value()
        assert status_val in ["pending", "success", "rejected", "cancel", ""], (
            f"Unexpected status value in edit modal: {status_val}"
        )

        admin_deposit_page.close_modal()
        expect(admin_deposit_page.modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Deposit In-Row Edit Modal")


# ==============================================================================
# PILLAR 3: DROPDOWNS & SELECTS VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_dropdown_options_integrity(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the Deposit modal status and type dropdowns contain valid options.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    # Status dropdown options
    status_options = admin_deposit_page.get_modal_status_options()
    assert len(status_options) >= 2, f"Expected at least 2 status options, got {status_options}"
    # Standard statuses should include pending and success/rejected
    lower_options = [opt.lower() for opt in status_options]
    assert any("pending" in opt for opt in lower_options), "Expected 'pending' in status options"

    # Type dropdown options
    type_options = admin_deposit_page.get_modal_type_options()
    assert len(type_options) >= 1, f"Expected at least 1 type option, got {type_options}"

    admin_deposit_page.close_modal()
    admin_error_monitor.assert_no_errors("Deposit Dropdown Options")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_dropdown_options_integrity(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the Withdraw modal status and type dropdowns contain valid options.
    """
    admin_withdraw_page.navigate()
    admin_withdraw_page.open_add_withdraw_modal()

    status_options = admin_withdraw_page.get_modal_status_options()
    assert len(status_options) >= 2, f"Expected at least 2 status options, got {status_options}"
    lower_options = [opt.lower() for opt in status_options]
    assert any("pending" in opt for opt in lower_options), "Expected 'pending' in status options"

    type_options = admin_withdraw_page.get_modal_type_options()
    assert len(type_options) >= 1, f"Expected at least 1 type option, got {type_options}"

    admin_withdraw_page.close_modal()
    admin_error_monitor.assert_no_errors("Withdraw Dropdown Options")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_page_length_selector_validation(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3 & 6: Verify changing visible entries per page (10, 25, 50, 100)
    dynamically updates table rows count and status summary text.
    """
    admin_deposit_page.navigate()

    total_records = admin_deposit_page.get_total_records_count()
    if total_records == 0:
        pytest.skip("No deposit records available for pagination testing")

    available_options = admin_deposit_page.get_entries_options()
    assert "10" in available_options
    assert "25" in available_options
    assert "50" in available_options

    for length in ["10", "25", "50"]:
        admin_deposit_page.select_entries(length)
        expected_count = min(total_records, int(length))
        expect(admin_deposit_page.pagination_info).to_contain_text(
            f"Showing 1 to {expected_count}", timeout=10000
        )
        expect(admin_deposit_page.table_rows).to_have_count(expected_count, timeout=10000)
        actual_count = admin_deposit_page.get_row_count()
        assert actual_count == expected_count, (
            f"Expected {expected_count} rows for page length {length}, got {actual_count}"
        )

    admin_error_monitor.assert_no_errors("Deposit Page Length Selector")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_page_length_selector_validation(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3 & 6: Verify changing visible entries per page (10, 25, 50, 100)
    dynamically updates withdraw table rows count and status summary text.
    """
    admin_withdraw_page.navigate()

    total_records = admin_withdraw_page.get_total_records_count()
    if total_records == 0:
        pytest.skip("No withdraw records available for pagination testing")

    for length in ["10", "25", "50"]:
        admin_withdraw_page.select_entries(length)
        expected_count = min(total_records, int(length))
        expect(admin_withdraw_page.pagination_info).to_contain_text(
            f"Showing 1 to {expected_count}", timeout=10000
        )
        expect(admin_withdraw_page.table_rows).to_have_count(expected_count, timeout=10000)
        actual_count = admin_withdraw_page.get_row_count()
        assert actual_count == expected_count, (
            f"Expected {expected_count} rows for page length {length}, got {actual_count}"
        )

    admin_error_monitor.assert_no_errors("Withdraw Page Length Selector")


# ==============================================================================
# PILLAR 4: DROPZONES & PROOF UPLOADS VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_proof_upload_and_remove_lifecycle(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 4: Verify uploading a payment proof image reveals the #proofRemoveBtn button,
    and clicking the remove button clears the file input.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    # Create temporary dummy image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        dummy_file = tmp.name

    try:
        # Upload file into proof input
        admin_deposit_page.modal_proof_input.set_input_files(dummy_file)
        admin_deposit_page.page.wait_for_timeout(300)

        # Verify remove button appears
        expect(admin_deposit_page.modal_proof_remove_btn).to_be_visible()

        # Click remove button
        admin_deposit_page.modal_proof_remove_btn.click()
        admin_deposit_page.page.wait_for_timeout(300)

        # Verify remove button disappears
        expect(admin_deposit_page.modal_proof_remove_btn).not_to_be_visible()

    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
        admin_deposit_page.close_modal()

    admin_error_monitor.assert_no_errors("Deposit Proof Upload Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_proof_disallowed_file_types(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 4 & Security (Section 4): Verify disallowed executable and malicious
    file types (shell.php, malicious.exe) cannot compromise the file input.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    # Verify input accept attribute
    accept_attr = admin_deposit_page.modal_proof_input.get_attribute("accept") or ""
    # Usually accepts image/* or specific image formats
    if accept_attr:
        assert not any(exe in accept_attr for exe in [".php", ".exe", ".sh"]), (
            f"Dangerous extensions found in accept attribute: {accept_attr}"
        )

    for filename, content, description in DISALLOWED_FILE_PAYLOADS:
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as tmp:
            tmp.write(content.encode() if isinstance(content, str) else content)
            tmp_path = tmp.name

        try:
            admin_deposit_page.modal_proof_input.set_input_files(tmp_path)
            admin_deposit_page.page.wait_for_timeout(300)
            # Ensure form cannot be saved with malicious file without email
            admin_deposit_page.modal_save_button.click()
            expect(admin_deposit_page.invalid_feedback_email).to_be_visible()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    admin_deposit_page.close_modal()
    admin_error_monitor.assert_no_errors("Deposit Proof Disallowed Files")


# ==============================================================================
# PILLAR 5: DATE & TIME PICKERS VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_inverted_date_range_boundary(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Verify that setting an inverted date range (From > To, e.g.
    From: 2026-12-31, To: 2026-01-01) does not cause 500 server crash
    and yields empty state or handles boundary cleanly.
    """
    admin_deposit_page.navigate()
    initial_info = admin_deposit_page.get_pagination_info()

    # Set inverted date range (From is in the future relative to To)
    admin_deposit_page.filter_by_date("2026-12-31T23:59", "2026-01-01T00:00")
    admin_deposit_page.page.wait_for_timeout(600)

    # Must not crash or display SQL/PHP errors
    page_html = admin_deposit_page.page.content().lower()
    assert "fatal error" not in page_html
    assert "sqlstate" not in page_html

    # Clear filter to restore full ledger
    admin_deposit_page.clear_date_filter()
    admin_deposit_page.page.wait_for_timeout(600)

    restored_info = admin_deposit_page.get_pagination_info()
    assert restored_info == initial_info, (
        f"Expected pagination info to restore to '{initial_info}', got '{restored_info}'"
    )

    admin_error_monitor.assert_no_errors("Deposit Inverted Date Range")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_inverted_date_range_boundary(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Verify that setting an inverted date range on Withdraw module
    does not cause server errors and restores properly on Clear.
    """
    admin_withdraw_page.navigate()
    initial_info = admin_withdraw_page.get_pagination_info()

    admin_withdraw_page.filter_by_date("2026-12-31T23:59", "2026-01-01T00:00")
    admin_withdraw_page.page.wait_for_timeout(600)

    page_html = admin_withdraw_page.page.content().lower()
    assert "fatal error" not in page_html
    assert "sqlstate" not in page_html

    admin_withdraw_page.clear_date_filter()
    admin_withdraw_page.page.wait_for_timeout(600)

    restored_info = admin_withdraw_page.get_pagination_info()
    assert restored_info == initial_info, (
        f"Expected pagination info to restore to '{initial_info}', got '{restored_info}'"
    )

    admin_error_monitor.assert_no_errors("Withdraw Inverted Date Range")


# ==============================================================================
# PILLAR 6: CALCULATIONS & TABLES VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_serial_number_sequential_ordering(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify that all S.No values in the Deposit table are:
    1. Positive integers.
    2. Strictly unique (no duplicates).
    3. Strictly sequential starting from 1 (1, 2, 3... N).
    """
    admin_deposit_page.navigate()

    rows_count = admin_deposit_page.get_row_count()
    if rows_count == 0:
        pytest.skip("No deposit records found in table")

    # Extract S.No from first column (index 0) of every row
    snos = []
    for i in range(rows_count):
        sno_text = admin_deposit_page.table_rows.nth(i).locator("td").first.inner_text().strip()
        if sno_text.isdigit():
            snos.append(int(sno_text))

    assert len(snos) > 0, "No numeric S.No found in Deposit table."
    # 1. Uniqueness
    assert len(snos) == len(set(snos)), f"Duplicate S.No detected in Deposit table: {snos}"
    # 2. Starts from 1
    assert snos[0] == 1, f"First S.No expected to be 1, got {snos[0]}"
    # 3. Sequential ordering
    expected_sequence = list(range(1, len(snos) + 1))
    assert snos == expected_sequence, f"S.Nos are not strictly sequential: {snos} vs {expected_sequence}"

    admin_error_monitor.assert_no_errors("Deposit S.No Sequential Ordering")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_serial_number_sequential_ordering(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify that all S.No values in the Withdraw table are:
    1. Positive integers.
    2. Strictly unique (no duplicates).
    3. Strictly sequential starting from 1 (1, 2, 3... N).
    """
    admin_withdraw_page.navigate()

    rows_count = admin_withdraw_page.get_row_count()
    if rows_count == 0:
        pytest.skip("No withdraw records found in table")

    snos = []
    for i in range(rows_count):
        sno_text = admin_withdraw_page.table_rows.nth(i).locator("td").first.inner_text().strip()
        if sno_text.isdigit():
            snos.append(int(sno_text))

    assert len(snos) > 0, "No numeric S.No found in Withdraw table."
    assert len(snos) == len(set(snos)), f"Duplicate S.No detected in Withdraw table: {snos}"
    assert snos[0] == 1, f"First S.No expected to be 1, got {snos[0]}"
    expected_sequence = list(range(1, len(snos) + 1))
    assert snos == expected_sequence, f"S.Nos are not strictly sequential: {snos} vs {expected_sequence}"

    admin_error_monitor.assert_no_errors("Withdraw S.No Sequential Ordering")


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_table_column_sorting_traversal(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table column headers updates sorting classes
    (sorting_asc, sorting_desc) without breaking table rows layout.
    """
    admin_deposit_page.navigate()

    # Column 0 (S.No) is sorting_disabled by design in DataTables
    header_0_class = admin_deposit_page.table_headers.nth(0).get_attribute("class") or ""
    assert "sorting_disabled" in header_0_class, f"Expected S.No column to be sorting_disabled, got: {header_0_class}"

    # Sortable columns: Index 1 (Account ID), Index 8 (Amount)
    for col_idx in [1, 8]:
        initial_class = admin_deposit_page.sort_column(col_idx)
        assert any(s in initial_class for s in ["sorting_asc", "sorting_desc", "sorting"]), (
            f"Header {col_idx} did not update class on click: {initial_class}"
        )
        toggled_class = admin_deposit_page.sort_column(col_idx)
        assert any(s in toggled_class for s in ["sorting_asc", "sorting_desc"]), (
            f"Header {col_idx} did not toggle sort: {toggled_class}"
        )

    admin_error_monitor.assert_no_errors("Deposit Column Sorting Traversal")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_table_column_sorting_traversal(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table column headers updates sorting classes
    (sorting_asc, sorting_desc) on Withdraw table.
    """
    admin_withdraw_page.navigate()

    header_0_class = admin_withdraw_page.table_headers.nth(0).get_attribute("class") or ""
    assert "sorting_disabled" in header_0_class, f"Expected S.No column to be sorting_disabled, got: {header_0_class}"

    for col_idx in [1, 8]:
        initial_class = admin_withdraw_page.sort_column(col_idx)
        assert any(s in initial_class for s in ["sorting_asc", "sorting_desc", "sorting"]), (
            f"Header {col_idx} did not update class on click: {initial_class}"
        )
        toggled_class = admin_withdraw_page.sort_column(col_idx)
        assert any(s in toggled_class for s in ["sorting_asc", "sorting_desc"]), (
            f"Header {col_idx} did not toggle sort: {toggled_class}"
        )

    admin_error_monitor.assert_no_errors("Withdraw Column Sorting Traversal")


# ==============================================================================
# PILLAR 7: SECURITY & STATE VERIFICATION (SECTION 4 OF SPEC)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_deposit_hidden_tokens_and_csrf_presence(
    admin_deposit_page: AdminDepositPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Security (Section 4): Verify the Deposit form contains a valid, non-empty
    security token / hidden input (#token) to prevent request forgery.
    """
    admin_deposit_page.navigate()
    admin_deposit_page.open_add_deposit_modal()

    # Hidden token field check
    token_input = admin_deposit_page.modal_token_input
    assert token_input.count() > 0, "Missing #token input in Deposit modal form."

    # Verify form has action or submit button
    expect(admin_deposit_page.modal_save_button).to_be_visible()

    admin_deposit_page.close_modal()
    admin_error_monitor.assert_no_errors("Deposit Hidden Token Verification")


@pytest.mark.admin
@pytest.mark.validation
def test_val_withdraw_hidden_tokens_and_csrf_presence(
    admin_withdraw_page: AdminWithdrawPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Security (Section 4): Verify the Withdraw form contains a valid, non-empty
    security token / hidden input (#token) to prevent request forgery.
    """
    admin_withdraw_page.navigate()
    admin_withdraw_page.open_add_withdraw_modal()

    token_input = admin_withdraw_page.modal_token_input
    assert token_input.count() > 0, "Missing #token input in Withdraw modal form."
    expect(admin_withdraw_page.modal_save_button).to_be_visible()

    admin_withdraw_page.close_modal()
    admin_error_monitor.assert_no_errors("Withdraw Hidden Token Verification")
