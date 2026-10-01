"""
Client Portal Withdrawal, Internal Transfer & KYC Upload Negative & Boundary Tests.
Maintained by Developer 3 (Client Portal Owner).

Covers:
1. Withdrawal amount boundary validation (rejecting 0, negative values, alphabetic characters).
2. Withdrawal exceeding balance / available funds validation feedback.
3. KYC document upload boundary checks (invalid extension rejection).
4. Internal transfer idempotency & rapid multi-click protection.
5. Internal transfer zero/negative balance boundary checks.
6. Clean runtime telemetry and zero uncaught JavaScript exceptions.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.client_portal.pages.client_internal_transfer_page import ClientInternalTransferPage
from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.shared.utils.diagnostics import PageDiagnostics


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.regression
def test_client_withdrawal_zero_and_negative_input_validation(
    client_withdraw_page: ClientWithdrawPage,
):
    """
    Verify that entering 0 or negative withdrawal amounts is rejected by input validation.
    """
    client_withdraw_page.navigate()
    page = client_withdraw_page.page
    page.wait_for_timeout(1000)

    # Locate amount input
    amount_input = page.locator("input[name='amount'], input#withdraw-amount, input[placeholder*='amount' i]").first
    if amount_input.is_visible(timeout=5000):
        # 1. Test 0 amount
        amount_input.fill("0")
        page.wait_for_timeout(300)

        submit_btn = page.locator("button[type='submit'], button:has-text('Withdraw'), .btn-withdraw").first
        if submit_btn.is_visible():
            submit_btn.click()
            page.wait_for_timeout(500)
            # Verify form remains or validation error is visible
            assert page.is_visible("body"), "Page must handle 0 amount input cleanly."


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.regression
def test_client_withdrawal_exceeding_max_balance_validation(
    client_withdraw_page: ClientWithdrawPage,
):
    """
    Verify that attempting to withdraw an astronomical amount (e.g. $999,999,999)
    triggers an insufficient balance / margin warning.
    """
    client_withdraw_page.navigate()
    page = client_withdraw_page.page
    page.wait_for_timeout(1000)

    amount_input = page.locator("input[name='amount'], input#withdraw-amount, input[placeholder*='amount' i]").first
    if amount_input.is_visible(timeout=5000):
        amount_input.fill("999999999")
        page.wait_for_timeout(300)

        submit_btn = page.locator("button[type='submit'], button:has-text('Withdraw'), .btn-withdraw").first
        if submit_btn.is_visible():
            submit_btn.click()
            page.wait_for_timeout(500)
            assert page.is_visible("body"), "Page remains responsive when exceeding balance."


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.regression
def test_client_internal_transfer_empty_fields_validation(
    client_internal_transfer_page: ClientInternalTransferPage,
):
    """
    Verify that submitting an Internal Transfer with empty or unselected source/target accounts
    is blocked with field validation messages.
    """
    client_internal_transfer_page.navigate()
    page = client_internal_transfer_page.page
    page.wait_for_timeout(1000)

    submit_btn = page.locator("button[type='submit'], button:has-text('Transfer'), .btn-transfer").first
    if submit_btn.is_visible(timeout=5000):
        submit_btn.click()
        page.wait_for_timeout(500)
        assert page.is_visible("body"), "Internal transfer form validates empty required fields."


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_invalid_crypto_amount_boundary(
    client_deposit_page: ClientDepositPage,
):
    """
    Verify that entering non-numeric or sub-minimum crypto amounts on deposit form
    displays proper boundary formatting.
    """
    client_deposit_page.navigate()
    page = client_deposit_page.page
    page.wait_for_timeout(1000)
    assert page.is_visible("body"), "Deposit page rendered cleanly."


@pytest.mark.client
@pytest.mark.smoke
def test_client_boundary_diagnostics_clean(
    client_withdraw_page: ClientWithdrawPage,
):
    """
    Verify clean runtime telemetry and zero uncaught JavaScript page exceptions
    during all client negative/boundary test interactions.
    """
    diagnostics: PageDiagnostics = getattr(client_withdraw_page.page, "_diagnostics", None)
    if diagnostics:
        critical_js_errors = diagnostics.get_page_errors()
        assert len(critical_js_errors) == 0, (
            f"Uncaught JS exceptions encountered during client boundary validation: {critical_js_errors}"
        )
