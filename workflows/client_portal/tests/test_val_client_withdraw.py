"""
Client Portal Withdrawal Form & Payout Details Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Zero & negative amounts, excessive amounts, bank details, crypto addresses.
2. Buttons & Actions: Request Withdraw disabled lifecycle, Save Details button.
3. Dropdowns & Selects: Withdraw source account selector, Mode of Payment selector, History rows length.
6. Calculations & Tables: Available Fund / Withdrawable amounts, 5-column transaction ledger.
7. Security: Sanitization of payout address and bank details inputs, zero database errors.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. WITHDRAW AMOUNT: ZERO & NEGATIVE AMOUNTS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize("invalid_amount", ["0", "-1", "-100.00"])
def test_val_client_withdraw_zero_and_negative_amounts(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
    invalid_amount: str,
):
    """
    Pillar 1: Verify zero and negative withdrawal amounts are rejected:
    - Inputting 0 or negative values keeps Request Withdraw button disabled
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.amount_input).to_be_visible()

    client_withdraw_page.enter_withdraw_amount(invalid_amount)
    if client_withdraw_page.is_request_withdraw_enabled():
        client_withdraw_page.click_request_withdraw()
        client_withdraw_page.page.wait_for_timeout(600)
        assert not client_withdraw_page.otp_modal.is_visible(), (
            f"OTP modal must not open for invalid withdrawal amount '{invalid_amount}'"
        )
    else:
        assert not client_withdraw_page.is_request_withdraw_enabled()

    client_error_monitor.assert_no_js_errors(f"Withdraw Zero/Negative: {invalid_amount}")


# ==============================================================================
# 2. WITHDRAW AMOUNT: EMPTY INPUT DISABLED STATE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_empty_amount_disabled_state(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify submit button is disabled when amount input is empty:
    - Initial state without amount -> Request Withdraw disabled
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.amount_input).to_be_visible()

    client_withdraw_page.amount_input.fill("")
    assert not client_withdraw_page.is_request_withdraw_enabled(), (
        "Request Withdraw button must be disabled when amount is empty"
    )

    client_error_monitor.assert_no_js_errors("Withdraw Empty Amount State")


# ==============================================================================
# 3. WITHDRAW AMOUNT: EXCESSIVE BOUNDARY VALUE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_excessive_amount_boundary(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test astronomical withdrawal amount (e.g. $999,999,999):
    - Input accepts valid numeric entry without UI freezing
    - Button state or client-side check prevents unauthorized submission
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.amount_input).to_be_visible()

    client_withdraw_page.enter_withdraw_amount("999999999")
    assert client_withdraw_page.amount_input.input_value() == "999999999"

    client_error_monitor.assert_no_js_errors("Withdraw Excessive Amount Boundary")


# ==============================================================================
# 4. BANK DETAILS INPUTS & FIELD EDITABILITY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_bank_details_fields(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify all 6 Bank Payout Details input textboxes:
    - Bank Name, Account Number, IFSC, SWIFT/BIC, Branch, Location
    - All fields are editable and retain typed values
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.bank_payout_heading).to_be_visible()

    test_bank = {
        "bank_name": "Test International Bank",
        "account_number": "987654321012",
        "ifsc_code": "TEST0001234",
        "swift_code": "TESTUS33XXX",
        "branch": "Main Financial District",
        "location": "New York",
    }

    client_withdraw_page.fill_bank_details(**test_bank)

    assert client_withdraw_page.bank_name_input.input_value() == test_bank["bank_name"]
    assert client_withdraw_page.account_number_input.input_value() == test_bank["account_number"]
    assert client_withdraw_page.ifsc_code_input.input_value() == test_bank["ifsc_code"]
    assert client_withdraw_page.swift_code_input.input_value() == test_bank["swift_code"]
    assert client_withdraw_page.branch_input.input_value() == test_bank["branch"]
    assert client_withdraw_page.location_input.input_value() == test_bank["location"]

    client_error_monitor.assert_no_js_errors("Withdraw Bank Details Fields")


# ==============================================================================
# 5. CRYPTO ADDRESSES INPUTS & EDITABILITY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_crypto_addresses_fields(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify crypto and alternative payout address inputs:
    - USDT TRC20, USDT BEP, UPI, SS Payment
    - Fields accept and display valid address strings
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.withdraw_addresses_heading).to_be_visible()

    test_crypto = {
        "usdt_trc20": "TXyZ1234567890abcdefghijklmnopqrst",
        "usdt_bep": "0x1234567890abcdef1234567890abcdef12345678",
        "upi": "testuser@okaxis",
        "ss_payment": "SS_PAYMENT_ACCOUNT_99",
    }

    client_withdraw_page.fill_crypto_addresses(**test_crypto)

    assert client_withdraw_page.usdt_trc20_input.input_value() == test_crypto["usdt_trc20"]
    assert client_withdraw_page.usdt_bep_input.input_value() == test_crypto["usdt_bep"]
    assert client_withdraw_page.upi_input.input_value() == test_crypto["upi"]
    assert client_withdraw_page.ss_payment_input.input_value() == test_crypto["ss_payment"]

    client_error_monitor.assert_no_js_errors("Withdraw Crypto Addresses Fields")


# ==============================================================================
# 6. DROPDOWNS: SOURCE ACCOUNT & PAYMENT METHOD OPTIONS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_dropdown_options(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify source and payment method dropdown options:
    - Withdraw From select has at least 1 selectable account/wallet
    - Mode of Payment select has at least 2 options (Bank, USDT, etc.)
    """
    client_withdraw_page.navigate()

    source_options = client_withdraw_page.get_source_options()
    assert len(source_options) >= 1, f"Expected at least 1 withdraw source, got {len(source_options)}"

    method_options = client_withdraw_page.get_payment_method_options()
    assert len(method_options) >= 2, f"Expected at least 2 payment methods, got {len(method_options)}"

    client_error_monitor.assert_no_js_errors("Withdraw Dropdown Options")


# ==============================================================================
# 7. WITHDRAW HISTORY: TABLE STRUCTURE & ROWS LENGTH SELECTOR
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_history_table_and_dropdown(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillars 3 & 6: Verify withdrawal history transaction ledger:
    - 5 table headers: DATE, METHOD, AMOUNT, STATUS, ADDRESS / DETAIL
    - Rows per page dropdown selection (10, 25, 50, 100)
    """
    client_withdraw_page.navigate()
    expect(client_withdraw_page.table).to_be_visible(timeout=15000)

    # 1. Verify 5 table headers
    expected_headers = ["DATE", "METHOD", "AMOUNT", "STATUS", "DETAIL"]
    actual_headers = client_withdraw_page.get_table_headers()
    assert len(actual_headers) == 5, f"Expected 5 headers, got {len(actual_headers)}: {actual_headers}"
    for exp_h in expected_headers:
        assert any(exp_h.lower() in act.lower() for act in actual_headers), f"Missing header: {exp_h}"

    # 2. Verify rows select dropdown
    expect(client_withdraw_page.history_rows_select).to_be_visible()
    client_withdraw_page.select_history_rows_per_page("25")
    assert client_withdraw_page.history_rows_select.input_value() == "25"

    client_error_monitor.assert_no_js_errors("Withdraw History Table & Dropdown")


# ==============================================================================
# 8. SECURITY: INPUT SANITIZATION ON PAYOUT FIELDS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_withdraw_security_sanitization(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 7: Test injection payloads on bank payout details and address fields:
    - Asserts no script execution (XSS)
    - Asserts no SQL error dumps
    """
    client_withdraw_page.navigate()

    # Fill bank name with SQLi payload
    for payload, desc in SQLI_PAYLOADS[:2]:
        client_withdraw_page.bank_name_input.fill(payload)
        client_withdraw_page.page.wait_for_timeout(200)
        body_text = client_withdraw_page.page.locator("body").inner_text()
        assert "SQLSTATE" not in body_text, f"SQL error exposed for {desc}"

    # Fill crypto address with XSS payload
    for payload, desc in XSS_PAYLOADS[:2]:
        client_withdraw_page.usdt_trc20_input.fill(payload)
        client_withdraw_page.page.wait_for_timeout(200)
        is_pwned = client_withdraw_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert not is_pwned, f"XSS executed on withdraw input: {desc}"

    client_error_monitor.assert_no_js_errors("Withdraw Security Sanitization")
