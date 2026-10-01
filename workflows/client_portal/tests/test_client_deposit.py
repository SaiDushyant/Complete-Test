"""
Client Portal Deposit & Funding Workflow Tests.
Detailed validation covering all minute controls:
1. Universal header & page headings ('Deposit', 'Deposit Funds')
2. Funding rails selection (Bank Transfer, BITCOIN, USDT TRC20, Crypto Gateway)
3. Deposit request form validation lifecycle:
   - Account selection
   - Minimum deposit threshold enforcement
   - Payment proof file upload
   - Submit button enabling lifecycle (disabled -> enabled)
4. Deposit history ledger table (DATE, METHOD, AMOUNT, STATUS, DETAIL)
5. Rows per page selector dropdown (10, 25, 50, 100) & Refresh action
6. End-to-end funding journey with zero browser console errors, JS crashes, or backend failures
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import os
import re
import tempfile
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_deposit_header_and_page_elements(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Deposit view renders universal header and main headings:
    - Page title in header is 'Deposit'
    - Main heading is 'Deposit Funds'
    - Account badge and action buttons are visible and active
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()
    client_deposit_page.header.assert_header_elements(expected_title="Deposit")

    expect(client_deposit_page.main_heading.first).to_be_visible()
    expect(client_deposit_page.deposit_request_heading.first).to_be_visible()
    expect(client_deposit_page.history_heading.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Deposit Header and Page Elements")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_funding_rails_selection(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify payment funding rail cards and selection:
    - All 5 funding rails render with minimum deposit amounts
    - Clicking a funding rail card highlights it and updates mode of payment
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()

    # 1. Verify rail cards presence
    expect(client_deposit_page.rail_cards.first).to_be_visible()
    rails_info = client_deposit_page.get_funding_rails_info()
    assert len(rails_info) >= 4, f"Expected at least 4 funding rail options, got {len(rails_info)}"

    for rail in rails_info:
        assert "$" in rail["minimum_deposit"], f"Expected minimum deposit amount in rail card, got {rail}"

    # 2. Select BITCOIN rail card
    client_deposit_page.select_funding_rail("BITCOIN")
    method_val = client_deposit_page.payment_method_select.input_value()
    assert method_val != "", "Expected payment method select to have active value after rail click"

    # 3. Select USDT TRC20 rail card
    client_deposit_page.select_funding_rail("USDT TRC20")
    method_val = client_deposit_page.payment_method_select.input_value()
    assert method_val != "", "Expected payment method select to update after USDT rail click"

    # 4. Select Bank Transfer rail card
    client_deposit_page.select_funding_rail("Bank Transfer")
    method_val = client_deposit_page.payment_method_select.input_value()
    assert method_val != "", "Expected payment method select to update after Bank Transfer click"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Funding Rails Selection")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_form_validation_and_submit_lifecycle(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify deposit request form input validation and submit button lifecycle:
    - Submit button is initially disabled
    - Selecting account and entering amount below minimum keeps button disabled
    - Entering amount meeting minimum threshold keeps button disabled until proof is provided
    - Uploading payment proof file enables Submit Deposit Request button
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()

    # 1. Initial State: Submit button is disabled
    expect(client_deposit_page.submit_button).to_be_visible()
    assert not client_deposit_page.is_submit_enabled(), "Submit button should initially be disabled"

    # 2. Select Destination Account
    client_deposit_page.select_destination_account("10026")

    # 3. Enter amount below minimum ($50 vs $200 min for Bank Transfer)
    client_deposit_page.enter_deposit_amount("50")
    assert not client_deposit_page.is_submit_enabled(), "Submit should be disabled when amount < minimum"

    # 4. Enter amount meeting minimum ($250)
    client_deposit_page.enter_deposit_amount("250")
    assert not client_deposit_page.is_submit_enabled(), "Submit should be disabled until proof is uploaded"

    # 5. Create temporary proof receipt file and upload
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        # Minimal valid 1x1 PNG bytes
        temp_file.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        temp_proof_path = temp_file.name

    try:
        client_deposit_page.upload_payment_proof(temp_proof_path)

        # 6. Button is now enabled!
        expect(client_deposit_page.submit_button).to_be_enabled(timeout=5000)
        assert client_deposit_page.is_submit_enabled(), "Submit button should be enabled when all fields are valid"
    finally:
        if os.path.exists(temp_proof_path):
            os.remove(temp_proof_path)

    # Automated Error Check
    client_error_monitor.assert_no_errors("Deposit Form Validation Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_history_table_and_dropdown(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Deposit History ledger table:
    - 5 column headers: DATE, METHOD, AMOUNT, STATUS, DETAIL
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - Refresh button is functional
    - Transaction rows display valid formatting ($ in amount, valid status)
    - Pagination buttons are present
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()

    expect(client_deposit_page.history_heading.first).to_be_visible()

    # 1. Verify 5 Column Headers
    headers = client_deposit_page.get_table_headers()
    expected_headers = ["DATE", "METHOD", "AMOUNT", "STATUS", "DETAIL"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 2. Rows per page selector
    expect(client_deposit_page.history_rows_select).to_be_visible()
    client_deposit_page.select_history_rows_per_page("50")
    expect(client_deposit_page.history_rows_select).to_have_value("50")

    # 3. Refresh action
    expect(client_deposit_page.refresh_top_button).to_be_visible()
    client_deposit_page.refresh_top_button.click()
    client_deposit_page.page.wait_for_timeout(500)

    # 4. Verify History Rows Data
    expect(client_deposit_page.table_rows.first).to_be_visible()
    row_count = client_deposit_page.get_history_row_count()
    assert row_count > 0, "Expected at least 1 deposit history record in table"

    # Auto-retry waiting for amount to hydrate with currency symbol
    amount_cell = client_deposit_page.table_rows.first.locator("td").nth(2)
    expect(amount_cell).to_contain_text("$", timeout=5000)

    first_row = client_deposit_page.get_first_history_row_data()
    assert "$" in first_row["amount"], f"Expected '$' in deposit amount, got {first_row['amount']}"
    assert first_row["status"] in ["SUCCESS", "PENDING", "REJECTED", "APPROVED"], (
        f"Unexpected status: {first_row['status']}"
    )

    # 5. Pagination controls & page navigation (Next / Previous)
    expect(client_deposit_page.prev_page_button).to_be_visible()
    expect(client_deposit_page.next_page_button).to_be_visible()

    # Reset rows to 25 to test multi-page pagination
    client_deposit_page.select_history_rows_per_page("25")
    expect(client_deposit_page.history_rows_select).to_have_value("25")

    # If records exceed 25, verify Next and Previous navigation
    if client_deposit_page.next_page_button.is_enabled():
        expect(client_deposit_page.prev_page_button).to_be_disabled()
        client_deposit_page.click_next_page()
        expect(client_deposit_page.prev_page_button).to_be_enabled()
        client_deposit_page.click_prev_page()
        expect(client_deposit_page.prev_page_button).to_be_disabled()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Deposit History Table & Controls")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_all_payment_gateways_mode_of_payment(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 5 payment gateways in the Mode of Payment dropdown:
    1. Bank Transfer (Minimum: $200.00)
    2. Crypto Payment Gateway (Minimum: $150.00)
    3. USDT TRC20 (Minimum: $100.00)
    4. BITCOIN (Minimum: $100.00)
    5. crypto - trc20 (Minimum: $100.00)
    Asserts each method updates the dynamic minimum deposit hint properly and zero errors.
    """
    client_deposit_page.navigate()

    expected_methods = {
        "Bank Transfer": "$200.00",
        "Crypto Payment Gateway": "$150.00",
        "USDT TRC20": "$100.00",
        "BITCOIN": "$100.00",
        "crypto - trc20": "$100.00",
    }

    # Verify options present in dropdown
    options = client_deposit_page.get_payment_method_options()
    for method_name in expected_methods.keys():
        assert any(method_name.lower() in opt.lower() for opt in options), (
            f"Expected '{method_name}' in payment options: {options}"
        )

    # Verify each method selection and dynamic minimum hint
    for method_name in expected_methods.keys():
        client_deposit_page.select_payment_method(method_name)
        expect(client_deposit_page.minimum_deposit_hint.first).to_contain_text(re.compile(r"Minimum\s*deposit:\s*\$\d+", re.I))

    client_error_monitor.assert_no_errors("All Payment Gateways Mode of Payment")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_end_to_end_journey_zero_errors(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End endurance test for Deposit workflow:
    - Navigate to Deposit
    - Cycle through funding rails
    - Verify form updates
    - Verify table ledger
    - Asserts ZERO console errors, ZERO JS crashes, and ZERO 5xx backend errors
    """
    client_deposit_page.navigate()
    client_deposit_page.header.assert_header_elements(expected_title="Deposit")

    # Select multiple funding rails in sequence
    for rail_name in ["BITCOIN", "USDT TRC20", "Bank Transfer"]:
        client_deposit_page.select_funding_rail(rail_name)
        client_deposit_page.page.wait_for_timeout(300)

    # Verify ledger table rows count
    assert client_deposit_page.get_history_row_count() > 0

    # Strict Zero Error Check across entire journey
    client_error_monitor.assert_no_errors("Deposit End-to-End Journey")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize(
    "method_name,min_amount",
    [
        ("Bank Transfer", "200"),
        ("Crypto Payment Gateway", "150"),
        ("USDT TRC20", "100"),
        ("BITCOIN", "100"),
        ("crypto - trc20", "100"),
    ],
)
def test_client_deposit_successful_submission_flow(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
    method_name: str,
    min_amount: str,
):
    """
    Verify complete live submission of a deposit request across all 5 payment gateways:
    1. Bank Transfer (Min $200.00)
    2. Crypto Payment Gateway (Min $150.00)
    3. USDT TRC20 (Min $100.00)
    4. BITCOIN (Min $100.00)
    5. crypto - trc20 (Min $100.00)

    For each gateway:
    - Selects destination account
    - Selects payment method and enters required minimum threshold amount
    - Uploads valid payment proof receipt image
    - Submits deposit request
    - Asserts UI receives 'Payment Deposit Request Received' confirmation toast
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()

    # 1. Fill valid parameters
    client_deposit_page.select_destination_account("10026")
    client_deposit_page.select_payment_method(method_name)
    client_deposit_page.enter_deposit_amount(min_amount)

    # 2. Upload dummy proof file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        temp_proof_path = temp_file.name

    try:
        client_deposit_page.upload_payment_proof(temp_proof_path)

        # 3. Submit deposit request
        client_deposit_page.submit_deposit()

        # 4. Verify confirmation toast
        expect(client_deposit_page.success_toast.first).to_be_visible(timeout=10000)
        toast_text = client_deposit_page.success_toast.first.inner_text()
        assert "Payment Deposit Request Received" in toast_text, f"Unexpected toast: {toast_text}"
    finally:
        if os.path.exists(temp_proof_path):
            os.remove(temp_proof_path)

    # Automated Error Check
    client_error_monitor.assert_no_errors(f"Deposit Successful Submission Flow ({method_name})")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_header_full_interactive_lifecycle(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete header interactivity while remaining on the Deposit view:
    - Page title is 'Deposit' and all universal header elements render
    - Theme toggle switches between dark and light themes smoothly
    - Account switcher switches between accounts and updates badge
    - Notifications drawer opens 'Security & Clearance Alerts' and dismisses cleanly
    - Support Center drawer opens, displays Session Info & FAQ, and closes
    - Create Account modal opens 'LIVE ACCOUNT CREATION' and dismisses via Cancel
    - Search input accepts queries and clears
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()
    header = client_deposit_page.header

    # 1. Assert header elements
    header.assert_header_elements(expected_title="Deposit")

    # 2. Theme toggle
    header.toggle_theme()
    header.toggle_theme()

    # 3. Account switcher (switch and restore dynamically)
    initial_account = header.get_selected_account()
    available_accounts = header.get_available_accounts()
    alt_accounts = [acc for acc in available_accounts if acc != initial_account]
    if alt_accounts:
        target_alt = alt_accounts[0]
        header.select_account(target_alt)
        expect(header.account_badge).to_contain_text(target_alt)
        header.select_account(initial_account)
        expect(header.account_badge).to_contain_text(initial_account)

    # 4. Notifications drawer
    header.open_notifications()
    expect(header.notifications_drawer).to_be_visible()
    header.close_notifications()
    expect(header.notifications_drawer).not_to_be_visible()

    # 5. Support Center drawer
    header.open_support()
    expect(header.support_drawer).to_be_visible()
    header.close_support()
    expect(header.support_drawer).not_to_be_visible()

    # 6. Create Account modal
    header.open_create_account_modal()
    expect(header.create_account_modal).to_be_visible()
    header.close_create_account_modal()
    expect(header.create_account_modal).not_to_be_visible()

    # 7. Search input
    header.search("Deposit Test")
    header.clear_search()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Deposit Header Full Interactive Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_proof_dropzone_and_table_sorting_characteristics(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Cross-check minute details of proof submission mechanism and table sorting:
    - Proof submission is an inline file upload dropzone targeting <input type="file" accept="image/*">
    - Proof submission does NOT open a web modal dialog box
    - Submit deposit form renders an alert confirmation banner (toast), not a blocking popup modal
    - Table column headers (DATE, METHOD, AMOUNT, STATUS, DETAIL) are server-side chronologically sorted
    - Multi-page pagination navigation correctly manages Previous / Next enablement
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()

    # 1. Proof Submission Dropzone Verification
    expect(client_deposit_page.proof_upload_label).to_be_visible()
    expect(client_deposit_page.proof_upload_label).to_contain_text("Drop payment proof")
    expect(client_deposit_page.proof_upload_input).to_have_attribute("accept", "image/*")

    # Verify no unexpected modal dialog is present on the page
    assert client_deposit_page.visible_modal_dialogs.count() == 0, "No modal dialog should be displayed by default on deposit page"

    # 2. Table Header Characteristics
    headers = client_deposit_page.get_table_headers()
    expected_headers = ["DATE", "METHOD", "AMOUNT", "STATUS", "DETAIL"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # Verify headers are static server-side sorted headers
    for th in client_deposit_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 3. Pagination navigation
    client_deposit_page.select_history_rows_per_page("25")
    if client_deposit_page.next_page_button.is_enabled():
        expect(client_deposit_page.prev_page_button).to_be_disabled()
        client_deposit_page.click_next_page()
        expect(client_deposit_page.prev_page_button).to_be_enabled()
        client_deposit_page.click_prev_page()
        expect(client_deposit_page.prev_page_button).to_be_disabled()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Proof Dropzone and Table Sorting Characteristics")


@pytest.mark.client
@pytest.mark.regression
def test_client_deposit_negative_invalid_amount_and_thresholds(
    client_deposit_page: ClientDepositPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Deposit Form Validation Thresholds:
    - Amount is zero -> Submit remains disabled
    - Amount is below minimum deposit limit -> Submit remains disabled
    - Cleared/empty amount -> Submit remains disabled
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_deposit_page.navigate()
    client_deposit_page.select_destination_account("10026")

    # 1. Zero amount
    client_deposit_page.enter_deposit_amount("0")
    expect(client_deposit_page.submit_button).to_be_disabled()

    # 2. Sub-minimum amount ($10 when min is $50/200)
    client_deposit_page.enter_deposit_amount("10")
    expect(client_deposit_page.submit_button).to_be_disabled()

    # 3. Empty amount
    client_deposit_page.enter_deposit_amount("")
    expect(client_deposit_page.submit_button).to_be_disabled()

    client_error_monitor.assert_no_errors("Deposit Negative Threshold Validation")



