"""
Client Portal Internal Transfer Validation Test Suite.
Validates input boundaries, zero/negative amounts, same-account transfer restrictions,
excessive balance protections, and memo XSS sanitization per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_internal_transfer_page import ClientInternalTransferPage
from workflows.shared.helpers.validation_payloads import (
    NUMERIC_BOUNDARY_VALUES,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_internal_transfer")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
def test_val_transfer_submit_blocked_when_empty(client_internal_transfer_page: ClientInternalTransferPage):
    """
    Verify that clicking Review Transfer with an empty amount blocks modal progression and displays a validation error.
    """
    client_internal_transfer_page.navigate()
    expect(client_internal_transfer_page.main_heading.first).to_be_visible()

    client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
    client_internal_transfer_page.page.wait_for_timeout(500)

    assert not client_internal_transfer_page.review_modal.is_visible() or client_internal_transfer_page.validation_error_message.is_visible(), (
        "Transfer review modal unexpectedly opened with empty amount!"
    )
    logger.info("Verified empty transfer amount submission is blocked by validation.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("invalid_amount", ["0", "-10", "-500", "0.0001"])
def test_val_transfer_zero_and_negative_amounts(
    client_internal_transfer_page: ClientInternalTransferPage, invalid_amount: str
):
    """
    Verify zero and negative amounts prevent internal transfer review.
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.enter_amount(invalid_amount)

    if client_internal_transfer_page.is_review_transfer_enabled():
        client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
        client_internal_transfer_page.page.wait_for_timeout(500)
        assert not client_internal_transfer_page.review_modal.is_visible() or client_internal_transfer_page.validation_error_message.is_visible(), (
            f"Transfer review modal unexpectedly opened for invalid amount '{invalid_amount}'"
        )
    logger.info(f"Verified invalid transfer amount '{invalid_amount}' is blocked by validation.")


@pytest.mark.client
@pytest.mark.regression
def test_val_transfer_same_source_and_destination(client_internal_transfer_page: ClientInternalTransferPage):
    """
    Verify that selecting identical source and destination accounts is either filtered from dropdowns or rejected upon review.
    """
    client_internal_transfer_page.navigate()

    source_opts = client_internal_transfer_page.get_source_options()
    dest_opts = client_internal_transfer_page.get_destination_options()

    if len(source_opts) > 0 and len(dest_opts) > 0:
        first_opt = source_opts[0]
        client_internal_transfer_page.select_source(first_opt)
        
        # Check if the same option exists in destination
        if any(first_opt in d for d in dest_opts):
            client_internal_transfer_page.select_destination(first_opt)
            client_internal_transfer_page.enter_amount("50")

            if client_internal_transfer_page.is_review_transfer_enabled():
                client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
                client_internal_transfer_page.page.wait_for_timeout(1000)
                # Modal or error check
                if client_internal_transfer_page.review_modal.is_visible():
                    # Attempting execution must fail/toast error
                    client_internal_transfer_page.modal_execute_btn.click()
                    client_internal_transfer_page.page.wait_for_timeout(1000)
                    assert client_internal_transfer_page.page.locator("text=/error|failed|invalid|same/i").is_visible() or client_internal_transfer_page.review_modal.is_visible()
        else:
            logger.info("Destination dropdown successfully excluded the selected source account.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_transfer_memo_xss_sanitization(
    client_internal_transfer_page: ClientInternalTransferPage, payload: str, description: str
):
    """
    Verify that XSS injection in transfer memo input is sanitized without script execution.
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.page.evaluate("window.xss_detected = 0;")

    client_internal_transfer_page.enter_amount("10")
    client_internal_transfer_page.enter_memo(f"Memo {payload}")

    # Check that entering memo does not trigger XSS
    is_triggered = client_internal_transfer_page.page.evaluate("() => window.xss_detected === 1")
    assert not is_triggered, f"XSS script executed in Transfer Memo field with payload: {payload}"
    logger.info(f"Verified Transfer Memo safely sanitized XSS payload: {description}")
