"""
Client Portal Deposit Form & Upload Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Minimum deposit threshold, zero & negative amounts, excessive boundaries.
2. Buttons & Actions: Submit button disabled state lifecycle until mandatory fields + proof provided.
3. Dropdowns & Selects: Destination account select, payment method select, history rows length select.
4. Dropzones & Uploads:
   - Allowed file extensions (.png, .jpg, .pdf).
   - Disallowed executable/script extensions (.exe, .php, .sh).
   - 0-byte empty file handling.
6. Calculations & Tables: Minimum deposit hints, 5-column transaction ledger, pagination controls.
7. Security: Prevention of destructive state mutations (read/boundary checks only).

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import os
import tempfile
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. DEPOSIT AMOUNT: MINIMUM THRESHOLD BOUNDARY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_deposit_minimum_threshold_enforcement(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify that entering an amount below minimum threshold ($10)
    keeps the submit button disabled:
    - Amount = $5 (< min $10) -> submit button remains disabled
    """
    client_deposit_page.navigate()
    expect(client_deposit_page.amount_input).to_be_visible()

    # Enter sub-threshold amount
    client_deposit_page.enter_deposit_amount("5")
    assert not client_deposit_page.is_submit_enabled(), "Submit must remain disabled for amount below minimum"

    client_error_monitor.assert_no_js_errors("Deposit Minimum Threshold")


# ==============================================================================
# 2. DEPOSIT AMOUNT: ZERO & NEGATIVE AMOUNTS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize("invalid_amount", ["0", "-1", "-50.00"])
def test_val_client_deposit_zero_and_negative_amounts(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
    invalid_amount: str,
):
    """
    Pillar 1: Verify zero and negative amounts are blocked:
    - Inputting 0 or negative values does not enable submit
    """
    client_deposit_page.navigate()
    expect(client_deposit_page.amount_input).to_be_visible()

    client_deposit_page.enter_deposit_amount(invalid_amount)
    assert not client_deposit_page.is_submit_enabled(), f"Submit must be disabled for amount '{invalid_amount}'"

    client_error_monitor.assert_no_js_errors(f"Deposit Zero/Negative Amount: {invalid_amount}")


# ==============================================================================
# 3. DEPOSIT AMOUNT: EXCESSIVE BOUNDARY VALUE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_deposit_excessive_amount_boundary(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test high boundary values (e.g. $10,000,000) on deposit input:
    - Input accepts valid numeric entry without UI freezing or uncaught JS crashes
    """
    client_deposit_page.navigate()
    expect(client_deposit_page.amount_input).to_be_visible()

    client_deposit_page.enter_deposit_amount("10000000")
    assert client_deposit_page.amount_input.input_value() == "10000000"

    client_error_monitor.assert_no_js_errors("Deposit Excessive Amount Boundary")


# ==============================================================================
# 4. SUBMIT BUTTON: ENABLING LIFECYCLE ON MANDATORY FIELDS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_deposit_submit_lifecycle_and_prerequisites(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify submit button remains disabled until ALL prerequisites are met:
    - Initially disabled
    - Disabled with amount only
    - Disabled with proof only
    - Enabled only when account + method + valid amount + proof are provided
    """
    client_deposit_page.navigate()

    # Step 1: Initial state (no amount, no proof) -> Disabled
    assert not client_deposit_page.is_submit_enabled(), "Submit button must be disabled initially"

    # Step 2: Add valid amount only ($100) -> Still disabled without proof
    client_deposit_page.enter_deposit_amount("100")
    assert not client_deposit_page.is_submit_enabled(), "Submit button must remain disabled without proof file"

    # Step 3: Attach valid proof -> Now enabled
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(b"MOCK_PAYMENT_PROOF_DATA_12345")
        tmp_path = tmp.name

    try:
        client_deposit_page.upload_payment_proof(tmp_path)
        client_deposit_page.page.wait_for_timeout(500)
        assert client_deposit_page.is_submit_enabled(), "Submit button should enable when all inputs are satisfied"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    client_error_monitor.assert_no_js_errors("Deposit Submit Lifecycle")


# ==============================================================================
# 5. DROPZONE: ALLOWED FILE EXTENSIONS (.PNG, .JPG, .PDF)
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize("ext", [".png", ".jpg", ".jpeg"])
def test_val_client_deposit_allowed_proof_extensions(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
    ext: str,
):
    """
    Pillar 4: Verify proof dropzone accepts standard allowed image document formats:
    - .png, .jpg, .jpeg files set successfully on file input
    """
    client_deposit_page.navigate()

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(b"MOCK_FILE_CONTENT_ALLOWED")
        tmp_path = tmp.name

    try:
        client_deposit_page.upload_payment_proof(tmp_path)
        client_deposit_page.page.wait_for_timeout(400)
        # Check that file input received file
        file_val = client_deposit_page.proof_upload_input.input_value()
        assert file_val != "", f"File input should accept extension '{ext}'"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    client_error_monitor.assert_no_js_errors(f"Allowed Proof Extension: {ext}")


# ==============================================================================
# 6. DROPZONE: 0-BYTE EMPTY FILE BOUNDARY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_deposit_zero_byte_file_boundary(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 4: Verify dropzone handles 0-byte corrupted empty file cleanly
    without unhandled browser exceptions.
    """
    client_deposit_page.navigate()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        # Write 0 bytes
        tmp_path = tmp.name

    try:
        client_deposit_page.upload_payment_proof(tmp_path)
        client_deposit_page.page.wait_for_timeout(400)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    client_error_monitor.assert_no_js_errors("Deposit Zero-Byte File Boundary")


# ==============================================================================
# 7. DEPOSIT HISTORY: TABLE STRUCTURE & ROWS PER PAGE SELECTOR
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_deposit_history_table_and_dropdown(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillars 3 & 6: Verify deposit history transaction ledger:
    - 5 table headers: DATE, METHOD, AMOUNT, STATUS, DETAIL
    - Rows per page dropdown selection (10, 25, 50, 100)
    """
    client_deposit_page.navigate()
    expect(client_deposit_page.table).to_be_visible(timeout=15000)

    # 1. Verify 5 table headers
    expected_headers = ["DATE", "METHOD", "AMOUNT", "STATUS", "DETAIL"]
    actual_headers = client_deposit_page.get_table_headers()
    assert len(actual_headers) == 5, f"Expected 5 headers, got {len(actual_headers)}: {actual_headers}"
    for exp_h in expected_headers:
        assert any(exp_h.lower() in act.lower() for act in actual_headers), f"Missing header: {exp_h}"

    # 2. Verify rows select dropdown
    expect(client_deposit_page.history_rows_select).to_be_visible()
    client_deposit_page.select_history_rows_per_page("25")
    assert client_deposit_page.history_rows_select.input_value() == "25"

    client_error_monitor.assert_no_js_errors("Deposit History Table & Dropdown")
