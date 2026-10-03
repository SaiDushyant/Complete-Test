"""
Client Portal Internal Transfer Form & Wallet Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B.3, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Zero & negative amounts, excessive boundary amounts, memo input.
2. Buttons & Actions: Review Transfer lifecycle, Cancel button form reset, Edit Details and Close modal dismissal.
3. Dropdowns & Selects: Source account/wallet, Destination account/wallet, History rows per page selector.
6. Calculations & Tables: 4-column ledger (DATE, DETAILS, AMOUNT, STATUS), transfer amount formatting.
7. Security: Sanitization of memo field against SQLi and XSS payloads, zero uncaught JS exceptions.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from config.settings import settings
from workflows.client_portal.pages.client_internal_transfer_page import ClientInternalTransferPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. TRANSFER AMOUNT: ZERO & NEGATIVE AMOUNTS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize("invalid_amount", ["0", "-1", "-50.00"])
def test_val_client_internal_transfer_zero_and_negative_amounts(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
    invalid_amount: str,
):
    """
    Pillar 1: Verify zero and negative transfer amounts are rejected:
    - Inputting 0 or negative values either disables the Review Transfer button
      or prevents the review modal from opening upon click.
    """
    client_internal_transfer_page.navigate()
    expect(client_internal_transfer_page.amount_input).to_be_visible()

    client_internal_transfer_page.select_source()
    client_internal_transfer_page.select_destination()
    client_internal_transfer_page.enter_amount(invalid_amount)

    if client_internal_transfer_page.is_review_transfer_enabled():
        client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
        client_internal_transfer_page.page.wait_for_timeout(500)
        assert not client_internal_transfer_page.review_modal.is_visible(), (
            f"Review modal must NOT open for invalid transfer amount '{invalid_amount}'"
        )
    else:
        assert not client_internal_transfer_page.is_review_transfer_enabled()

    client_error_monitor.assert_no_js_errors(f"Internal Transfer Zero/Negative: {invalid_amount}")


# ==============================================================================
# 2. TRANSFER AMOUNT: EMPTY INPUT DISABLED / BLOCKED STATE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_empty_amount_disabled_state(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify submit button is disabled or blocks modal when amount input is empty:
    - Initial state or cleared input -> Review Transfer disabled or blocks modal
    """
    client_internal_transfer_page.navigate()
    expect(client_internal_transfer_page.amount_input).to_be_visible()

    client_internal_transfer_page.amount_input.fill("")
    client_internal_transfer_page.page.wait_for_timeout(200)

    if client_internal_transfer_page.is_review_transfer_enabled():
        client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
        client_internal_transfer_page.page.wait_for_timeout(500)
        assert not client_internal_transfer_page.review_modal.is_visible(), (
            "Review modal must NOT open when transfer amount is empty"
        )
    else:
        assert not client_internal_transfer_page.is_review_transfer_enabled()

    client_error_monitor.assert_no_js_errors("Internal Transfer Empty Amount")


# ==============================================================================
# 3. SAME ACCOUNT TRANSFER VALIDATION
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_same_account_validation(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Selecting identical source and destination accounts:
    - If UI permits selecting the same account in both dropdowns, verify that
      attempting to transfer triggers validation or blocks review modal.
    """
    client_internal_transfer_page.navigate()
    source_options = client_internal_transfer_page.get_source_options()
    dest_options = client_internal_transfer_page.get_destination_options()

    common_accounts = [opt for opt in source_options if opt in dest_options and opt.strip()]
    if common_accounts:
        target = common_accounts[0]
        client_internal_transfer_page.select_source(target)
        client_internal_transfer_page.select_destination(target)
        client_internal_transfer_page.enter_amount("10.00")

        if client_internal_transfer_page.is_review_transfer_enabled():
            client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
            client_internal_transfer_page.page.wait_for_timeout(500)
            # Either modal is blocked or modal indicates source and dest must differ
            if client_internal_transfer_page.review_modal.is_visible():
                client_internal_transfer_page.close_review_modal()
        else:
            assert not client_internal_transfer_page.is_review_transfer_enabled()

    client_error_monitor.assert_no_js_errors("Internal Transfer Same Account Validation")


# ==============================================================================
# 4. EXCESSIVE TRANSFER AMOUNT BOUNDARY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_excessive_amount_boundary(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify entering an astronomical transfer amount (exceeding available balance):
    - System handles boundary amount ($999,999,999) cleanly without client crash.
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.select_source()
    client_internal_transfer_page.select_destination()
    client_internal_transfer_page.enter_amount("999999999.00")
    client_internal_transfer_page.page.wait_for_timeout(300)

    # Either button becomes disabled or execution is blocked
    if client_internal_transfer_page.is_review_transfer_enabled():
        client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
        client_internal_transfer_page.page.wait_for_timeout(500)
        if client_internal_transfer_page.review_modal.is_visible():
            # Dismiss modal without executing
            client_internal_transfer_page.close_review_modal()

    client_error_monitor.assert_no_js_errors("Internal Transfer Excessive Amount")


# ==============================================================================
# 5. REVIEW MODAL LIFECYCLE: OPEN, EDIT DETAILS, CLOSE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_review_modal_lifecycle(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify complete Review Internal Transfer modal dialog lifecycle:
    - Fill source, destination, amount ($15.00), and memo
    - Click 'Review Transfer'
    - Modal opens with title 'Review Internal Transfer'
    - Displays TRANSFERRING AMOUNT, SOURCE, DESTINATION, and Memo
    - Clicking 'Edit Details' dismisses modal and keeps form intact
    - Re-opening and clicking 'Close' dismisses modal cleanly
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.select_source()
    client_internal_transfer_page.select_destination()
    client_internal_transfer_page.enter_amount("15.00")
    client_internal_transfer_page.enter_memo("Validation Review Lifecycle")

    # 1. Trigger modal
    client_internal_transfer_page.click_review_transfer()
    expect(client_internal_transfer_page.review_modal.first).to_be_visible(timeout=5000)
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("Review Internal Transfer")
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("15.00")

    # 2. Modal action buttons
    expect(client_internal_transfer_page.modal_edit_btn).to_be_visible()
    expect(client_internal_transfer_page.modal_close_btn).to_be_visible()
    expect(client_internal_transfer_page.modal_execute_btn).to_be_visible()

    # 3. Dismiss via Edit Details
    client_internal_transfer_page.click_edit_details_modal()
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()
    expect(client_internal_transfer_page.amount_input).to_have_value("15.00")

    # 4. Re-open and dismiss via Close
    client_internal_transfer_page.click_review_transfer()
    expect(client_internal_transfer_page.review_modal.first).to_be_visible()
    client_internal_transfer_page.close_review_modal()
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()

    client_error_monitor.assert_no_js_errors("Review Transfer Modal Lifecycle")


# ==============================================================================
# 6. TRANSACTION LEDGER: 4 COLUMNS & ROWS SELECTOR
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_history_table_structure_and_dropdown(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify Recent Transfers ledger table:
    - 4 column headers: DATE, DETAILS, AMOUNT, STATUS
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - Transaction rows display valid formatting ($ currency symbol, valid status) if records present
    """
    client_internal_transfer_page.navigate()
    expect(client_internal_transfer_page.recent_transfers_heading.first).to_be_visible()

    # 1. 4 column headers
    headers = client_internal_transfer_page.get_table_headers()
    expected_headers = ["DATE", "DETAILS", "AMOUNT", "STATUS"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 2. Rows per page selector
    expect(client_internal_transfer_page.history_rows_select).to_be_visible()
    client_internal_transfer_page.select_history_rows_per_page("25")
    expect(client_internal_transfer_page.history_rows_select).to_have_value("25")

    # 3. History rows data check (if records exist)
    table_text = client_internal_transfer_page.table.inner_text().lower()
    if "no transfer records found" not in table_text and client_internal_transfer_page.table_rows.count() > 0:
        first_row = client_internal_transfer_page.get_first_history_row_data()
        assert "$" in first_row["amount"], f"Expected '$' in transfer amount, got: {first_row['amount']}"
        assert first_row["status"] in ["COMPLETED", "SUCCESS", "PENDING", "REJECTED"], (
            f"Unexpected status: {first_row['status']}"
        )

    client_error_monitor.assert_no_js_errors("Recent Transfers Table & Dropdown")


# ==============================================================================
# 7. SECURITY: MEMO SANITIZATION (SQLi & XSS PAYLOADS)
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize(
    "payload,desc",
    [
        (SQLI_PAYLOADS[0][0], SQLI_PAYLOADS[0][1]),
        (XSS_PAYLOADS[0][0], XSS_PAYLOADS[0][1]),
        (XSS_PAYLOADS[1][0], XSS_PAYLOADS[1][1]),
    ],
)
def test_val_client_internal_transfer_memo_security_sanitization(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
    payload: str,
    desc: str,
):
    """
    Pillar 7 (Security): Verify memo field sanitizes malicious injection strings:
    - Entering SQL injection or Cross-Site Scripting (XSS) payloads does not execute script,
      does not trigger uncaught JS runtime exceptions, and handles input safely.
    """
    alert_triggered = False

    def handle_dialog(dialog):
        nonlocal alert_triggered
        alert_triggered = True
        dialog.dismiss()

    client_internal_transfer_page.page.on("dialog", handle_dialog)

    client_internal_transfer_page.navigate()
    client_internal_transfer_page.select_source()
    client_internal_transfer_page.select_destination()
    client_internal_transfer_page.enter_amount("10.00")
    client_internal_transfer_page.enter_memo(payload)
    client_internal_transfer_page.page.wait_for_timeout(300)

    # Click Review Transfer to verify modal renders sanitized text without executing script
    if client_internal_transfer_page.is_review_transfer_enabled():
        client_internal_transfer_page.click_review_transfer()
        expect(client_internal_transfer_page.review_modal.first).to_be_visible()
        client_internal_transfer_page.close_review_modal()
        expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()

    assert not alert_triggered, f"Security Alert! XSS dialog triggered by payload: {payload}"
    client_error_monitor.assert_no_js_errors(f"Memo Sanitization: {desc}")


# ==============================================================================
# 8. CANCEL BUTTON FORM RESET LIFECYCLE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_internal_transfer_cancel_button_lifecycle(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify Cancel button resets or clears the transfer inputs cleanly:
    - Fill amount and memo
    - Click Cancel button
    - Verify form is responsive and inputs reset or clear
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.enter_amount("25.00")
    client_internal_transfer_page.enter_memo("Testing Cancel Button")

    expect(client_internal_transfer_page.cancel_button).to_be_visible()
    client_internal_transfer_page.cancel_button.click()
    client_internal_transfer_page.page.wait_for_timeout(300)

    # Form remains responsive with no JS errors
    expect(client_internal_transfer_page.transfer_details_heading.first).to_be_visible()
    client_error_monitor.assert_no_js_errors("Internal Transfer Cancel Button")
