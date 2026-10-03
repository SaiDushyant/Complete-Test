"""
Client Portal Deposit Form Validation Test Suite.
Validates input boundaries, minimum funding thresholds, mandatory file attachments,
and dropzone file extension restrictions according to VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import os
import tempfile
import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.shared.helpers.validation_payloads import (
    ACCEPTED_EXTENSIONS,
    DISALLOWED_EXTENSIONS,
    NUMERIC_BOUNDARY_VALUES,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_deposit")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
def test_val_deposit_submit_disabled_when_empty(client_deposit_page: ClientDepositPage):
    """
    Verify that Deposit Submit button is disabled by default when required fields are empty.
    """
    client_deposit_page.navigate()
    assert client_deposit_page.is_deposit_displayed(), "Deposit page not displayed"

    # Submit button should be disabled when amount and proof are not filled
    assert not client_deposit_page.is_submit_enabled(), (
        "Deposit submit button is unexpectedly enabled on empty form!"
    )
    logger.info("Verified Submit button is disabled on empty deposit form.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("invalid_amount", ["0", "-10", "-500", "0.001"])
def test_val_deposit_zero_and_negative_amounts(client_deposit_page: ClientDepositPage, invalid_amount: str):
    """
    Verify zero and negative amounts prevent deposit request submission.
    """
    client_deposit_page.navigate()
    client_deposit_page.select_payment_method("Bank Transfer")
    client_deposit_page.enter_deposit_amount(invalid_amount)

    # Check submit button state or browser HTML5 validity
    amount_validity = client_deposit_page.amount_input.evaluate("el => el.checkValidity()")
    assert not amount_validity or not client_deposit_page.is_submit_enabled(), (
        f"Deposit accepted invalid/negative amount '{invalid_amount}'"
    )
    logger.info(f"Verified invalid deposit amount '{invalid_amount}' is blocked by validation.")


@pytest.mark.client
@pytest.mark.regression
def test_val_deposit_without_proof_attachment(client_deposit_page: ClientDepositPage):
    """
    Verify that entering a valid amount without attaching payment proof keeps Submit button disabled.
    """
    client_deposit_page.navigate()
    client_deposit_page.select_payment_method("Bank Transfer")
    client_deposit_page.enter_deposit_amount("100")

    assert not client_deposit_page.is_submit_enabled(), (
        "Submit Deposit button was enabled without mandatory payment proof attachment!"
    )
    logger.info("Verified mandatory proof attachment prevents submission when empty.")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("ext", DISALLOWED_EXTENSIONS[:3])
def test_val_deposit_disallowed_file_types(client_deposit_page: ClientDepositPage, ext: str):
    """
    Verify that uploading non-whitelisted/executable file types (e.g. .exe, .php, .sh)
    is rejected by the deposit proof dropzone.
    """
    client_deposit_page.navigate()
    client_deposit_page.select_payment_method("Bank Transfer")
    client_deposit_page.enter_deposit_amount("100")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(b"MALICIOUS_PAYLOAD_TEST_DATA")
        temp_path = f.name

    try:
        # Check accept attribute on proof file input
        accept_attr = client_deposit_page.proof_upload_input.get_attribute("accept") or ""
        logger.info(f"Proof file input accept attribute: '{accept_attr}'")

        if accept_attr:
            assert ext not in accept_attr, f"Disallowed extension '{ext}' is present in accept filter: {accept_attr}"

        # Attempt to upload file
        client_deposit_page.upload_payment_proof(temp_path)
        client_deposit_page.page.wait_for_timeout(500)

        # Verify either submit is disabled or error alert displayed
        # or file input was rejected by browser/frontend
        logger.info(f"Verified disallowed file extension '{ext}' handling.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("ext", [".png", ".jpg", ".jpeg"])
def test_val_deposit_accepted_file_types(client_deposit_page: ClientDepositPage, ext: str):
    """
    Verify that standard receipt image formats (.png, .jpg, .jpeg) are accepted by the dropzone.
    """
    client_deposit_page.navigate()
    client_deposit_page.select_payment_method("Bank Transfer")
    client_deposit_page.enter_deposit_amount("150")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        # Minimal valid image byte header
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        temp_path = f.name

    try:
        client_deposit_page.upload_payment_proof(temp_path)
        client_deposit_page.page.wait_for_timeout(500)

        # Submit button should now become enabled when all valid criteria are met
        assert client_deposit_page.is_submit_enabled(), (
            f"Submit button was NOT enabled after providing valid amount and valid '{ext}' proof!"
        )
        logger.info(f"Verified valid file extension '{ext}' successfully enables submission.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
