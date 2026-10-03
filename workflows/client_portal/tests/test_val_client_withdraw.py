"""
Client Portal Withdrawal & Payout Form Validation Test Suite.
Validates input boundaries, insufficient balance protection, zero/negative amounts,
and payout details input sanitization according to VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.shared.helpers.validation_payloads import (
    NUMERIC_BOUNDARY_VALUES,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_withdraw")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
def test_val_withdraw_submit_disabled_when_empty(client_withdraw_page: ClientWithdrawPage):
    """
    Verify that Request Withdraw button is disabled by default when amount is empty.
    """
    client_withdraw_page.navigate()
    assert client_withdraw_page.is_withdraw_displayed(), "Withdraw page not displayed"

    assert not client_withdraw_page.is_request_withdraw_enabled(), (
        "Request Withdraw button is unexpectedly enabled with empty amount!"
    )
    logger.info("Verified Request Withdraw button is disabled on empty form.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("invalid_amount", ["0", "-10", "-500"])
def test_val_withdraw_zero_and_negative_amounts(client_withdraw_page: ClientWithdrawPage, invalid_amount: str):
    """
    Verify zero and negative amounts prevent withdrawal submission or do not trigger OTP verification.
    """
    client_withdraw_page.navigate()
    client_withdraw_page.select_payment_method("Bank Transfer")
    client_withdraw_page.enter_withdraw_amount(invalid_amount)

    # Check if button is disabled or clicking it does not open OTP modal
    if client_withdraw_page.is_request_withdraw_enabled():
        client_withdraw_page.request_withdraw_button.click()
        client_withdraw_page.page.wait_for_timeout(1000)
        assert not client_withdraw_page.otp_modal.is_visible(), (
            f"Withdrawal OTP modal unexpectedly opened for invalid amount '{invalid_amount}'"
        )
    logger.info(f"Verified invalid withdrawal amount '{invalid_amount}' is blocked by validation.")


@pytest.mark.client
@pytest.mark.regression
def test_val_withdraw_amount_exceeding_available_balance(client_withdraw_page: ClientWithdrawPage):
    """
    Verify that entering an amount exceeding the withdrawable/available balance
    keeps the submit button disabled or alerts the user of insufficient funds.
    """
    client_withdraw_page.navigate()
    client_withdraw_page.select_payment_method("Bank Transfer")
    
    # Enter massive amount far exceeding any normal account balance
    excessive_amount = "999999999"
    client_withdraw_page.enter_withdraw_amount(excessive_amount)
    client_withdraw_page.page.wait_for_timeout(500)

    # Check if submit is blocked or if clicking triggers insufficient balance feedback
    if client_withdraw_page.is_request_withdraw_enabled():
        client_withdraw_page.click_request_withdraw()
        client_withdraw_page.page.wait_for_timeout(1000)
        # Verify OTP modal does NOT appear for excessive balance or an error message is visible
        has_error = (
            client_withdraw_page.page.locator("text=/insufficient|exceeds|not enough|invalid/i").is_visible()
            or not client_withdraw_page.otp_modal.is_visible()
        )
        assert has_error, "System unexpectedly permitted withdrawal exceeding account balance!"
    else:
        logger.info("Submit button correctly remained disabled for excessive withdrawal amount.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_withdraw_payout_details_xss_sanitization(
    client_withdraw_page: ClientWithdrawPage, payload: str, description: str
):
    """
    Verify that entering script/XSS payloads into bank payout fields is safely handled without script execution.
    """
    client_withdraw_page.navigate()
    client_withdraw_page.page.evaluate("window.xss_detected = 0;")

    # Fill bank details with payload
    client_withdraw_page.fill_bank_details(
        bank_name=f"Bank {payload}",
        account_number="1234567890",
        ifsc_code="TEST0123456",
        swift_code="TESTUS33",
        branch="Main Branch",
        location="New York",
    )

    client_withdraw_page.save_details()
    client_withdraw_page.page.wait_for_timeout(1000)

    is_triggered = client_withdraw_page.page.evaluate("() => window.xss_detected === 1")
    assert not is_triggered, f"XSS script executed during Bank Details submission with payload: {payload}"
    logger.info(f"Verified Payout Details safely sanitized XSS payload: {description}")
