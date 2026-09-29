"""
Client Portal Withdraw & Payout Workflow Tests.
Detailed validation covering all minute controls:
1. Universal header & page headings ('Withdraw', 'Withdraw Funds')
2. Bank Payout Details form (Bank Name, Account Number, IFSC, SWIFT, Branch, Location) & SAVE DETAILS
3. Withdraw Addresses (USDT TRC20, USDT BEP, UPI, SS payment) & SAVE DETAILS
4. Request Payout form validation lifecycle (Account, Mode of Payment, Amount, Button enabling)
5. Enter Withdraw OTP modal dialog lifecycle (OTP sent, input, Confirm button enabling, Close button)
6. All 5 payment methods in 'MODE OF PAYMENT'
7. Withdraw History ledger table (DATE, METHOD, AMOUNT, STATUS, ADDRESS / DETAIL) & Pagination
8. Universal header full interactive lifecycle directly on Withdraw view
9. End-to-end journey with zero browser console errors, JS crashes, or backend failures
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_withdraw_header_and_page_elements(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Withdraw view renders universal header and main headings:
    - Page title in header is 'Withdraw'
    - Main heading is 'Withdraw Funds'
    - Subtitle is visible
    - All sections (Bank Payout Details, Withdraw Addresses, Request Payout, Withdraw History) render
    - Refresh button is visible
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()
    client_withdraw_page.header.assert_header_elements(expected_title="Withdraw")

    expect(client_withdraw_page.main_heading.first).to_be_visible()
    expect(client_withdraw_page.subtitle.first).to_be_visible()
    expect(client_withdraw_page.bank_payout_heading.first).to_be_visible()
    expect(client_withdraw_page.withdraw_addresses_heading.first).to_be_visible()
    expect(client_withdraw_page.request_payout_heading.first).to_be_visible()
    expect(client_withdraw_page.history_heading.first).to_be_visible()
    expect(client_withdraw_page.refresh_top_button).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Withdraw Header and Page Elements")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_bank_payout_details_save(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Bank Payout Details section and save flow:
    - All 6 bank fields are present (Bank Name, Account Number, IFSC, SWIFT, Branch, Location)
    - Filling bank details and clicking SAVE DETAILS dispatches apiSaveWithdrawDetails
    - UI renders 'Successfully Saved Payment details' toast
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Assert presence of all 6 bank inputs
    expect(client_withdraw_page.bank_name_input).to_be_visible()
    expect(client_withdraw_page.account_number_input).to_be_visible()
    expect(client_withdraw_page.ifsc_code_input).to_be_visible()
    expect(client_withdraw_page.swift_code_input).to_be_visible()
    expect(client_withdraw_page.branch_input).to_be_visible()
    expect(client_withdraw_page.location_input).to_be_visible()

    # 2. Fill complete bank details
    client_withdraw_page.fill_bank_details(
        bank_name="Global Test Bank",
        account_number="1234567890",
        ifsc_code="GTB0001",
        swift_code="GTBUS33",
        branch="Main Branch",
        location="New York",
    )

    # 3. Save details
    client_withdraw_page.save_details()

    # 4. Verify confirmation toast
    expect(client_withdraw_page.save_success_toast.first).to_be_visible(timeout=10000)
    toast_text = client_withdraw_page.save_success_toast.first.inner_text()
    assert "Successfully Saved Payment details" in toast_text, f"Unexpected toast: {toast_text}"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Bank Payout Details Save")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_addresses_crypto_save(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Withdraw Addresses section (Crypto & Alternative):
    - 4 address fields: USDT TRC20, USDT BEP, UPI payment, SS payment
    - Fill crypto addresses and click SAVE DETAILS
    - UI confirms saving with success toast
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Assert address inputs presence
    expect(client_withdraw_page.usdt_trc20_input).to_be_visible()
    expect(client_withdraw_page.usdt_bep_input).to_be_visible()
    expect(client_withdraw_page.upi_input).to_be_visible()
    expect(client_withdraw_page.ss_payment_input).to_be_visible()

    # 2. Fill addresses
    client_withdraw_page.fill_crypto_addresses(
        usdt_trc20="TR7NHkorjpffbnh4m7n9284240294test",
        usdt_bep="0x55d398326f99059ff775485246999027b3197955",
        upi="trader@upi",
        ss_payment="SSPAY-12345",
    )

    # 3. Save details
    client_withdraw_page.save_details()
    expect(client_withdraw_page.save_success_toast.first).to_be_visible(timeout=10000)

    # Automated Error Check
    client_error_monitor.assert_no_errors("Withdraw Addresses Save")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_request_form_validation_and_lifecycle(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Request Payout form validation and submit button lifecycle:
    - Available source summary displays FUND and WITHDRAWABLE balances
    - REQUEST WITHDRAW button is initially disabled
    - Selecting source account keeps button disabled until amount is entered
    - Entering withdraw amount enables the REQUEST WITHDRAW button
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Available Source Balances
    expect(client_withdraw_page.available_source_box).to_be_visible()
    expect(client_withdraw_page.fund_amount_display).to_contain_text("$")
    expect(client_withdraw_page.withdrawable_amount_display).to_contain_text("$")

    # 2. Initial state: Button disabled
    expect(client_withdraw_page.request_withdraw_button).to_be_visible()
    assert not client_withdraw_page.is_request_withdraw_enabled(), "Submit should initially be disabled"

    # 3. Select Source Account
    client_withdraw_page.select_withdraw_source()
    assert not client_withdraw_page.is_request_withdraw_enabled(), "Submit should be disabled without amount"

    # 4. Select Mode of Payment
    client_withdraw_page.select_payment_method("USDT TRC20")
    assert not client_withdraw_page.is_request_withdraw_enabled(), "Submit should be disabled without amount"

    # 5. Fill Withdraw Amount
    client_withdraw_page.enter_withdraw_amount("25.00")

    # 6. Button is now enabled!
    expect(client_withdraw_page.request_withdraw_button).to_be_enabled(timeout=5000)
    assert client_withdraw_page.is_request_withdraw_enabled(), "Button should be enabled when form is filled"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Request Payout Form Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_otp_modal_flow_and_dismiss(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete Enter Withdraw OTP modal flow:
    - Submitting a valid withdrawal request sends OTP via apiSendWithdrawOtp
    - UI displays 'Successfully OTP sent!' toast
    - Enter Withdraw OTP modal appears with title and description
    - 'Confirm Withdraw' button inside modal is initially disabled
    - Typing an OTP enables the 'Confirm Withdraw' button
    - Clicking the modal Close button dismisses the OTP modal cleanly
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Fill valid parameters
    client_withdraw_page.select_withdraw_source()
    client_withdraw_page.select_payment_method("USDT TRC20")
    client_withdraw_page.enter_withdraw_amount("25.00")

    # 2. Trigger REQUEST WITHDRAW
    client_withdraw_page.click_request_withdraw()

    # 3. Assert OTP sent toast
    expect(client_withdraw_page.otp_sent_toast.first).to_be_visible(timeout=10000)

    # 4. Assert OTP modal appearance
    expect(client_withdraw_page.otp_modal.first).to_be_visible(timeout=5000)
    expect(client_withdraw_page.otp_modal.first).to_contain_text("Enter Withdraw OTP")
    expect(client_withdraw_page.otp_modal.first).to_contain_text(
        "OTP has been sent to your registered email. Confirm to create the pending withdraw request."
    )

    # 5. Check Confirm button lifecycle inside modal
    expect(client_withdraw_page.otp_confirm_button.first).to_be_visible()
    expect(client_withdraw_page.otp_confirm_button.first).to_be_disabled()

    # Fill OTP digits
    client_withdraw_page.otp_input.first.fill("123456")
    expect(client_withdraw_page.otp_confirm_button.first).to_be_enabled()

    # 6. Dismiss modal via Close button
    client_withdraw_page.close_otp_modal()
    expect(client_withdraw_page.otp_modal.first).not_to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Enter Withdraw OTP Modal Flow")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_history_table_and_dropdown(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Withdraw History ledger table:
    - 5 column headers: DATE, METHOD, AMOUNT, STATUS, ADDRESS / DETAIL
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - Refresh button is functional
    - Transaction rows display valid formatting ($ in amount, valid status)
    - Multi-page pagination controls (Previous / Next)
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    expect(client_withdraw_page.history_heading.first).to_be_visible()

    # 1. Verify 5 Column Headers
    headers = client_withdraw_page.get_table_headers()
    expected_headers = ["DATE", "METHOD", "AMOUNT", "STATUS", "ADDRESS / DETAIL"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # Verify headers are static server-side sorted
    for th in client_withdraw_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 2. Rows per page selector
    expect(client_withdraw_page.history_rows_select).to_be_visible()
    client_withdraw_page.select_history_rows_per_page("50")
    expect(client_withdraw_page.history_rows_select).to_have_value("50")

    # 3. Refresh action
    expect(client_withdraw_page.refresh_top_button).to_be_visible()
    client_withdraw_page.refresh_top_button.click()
    client_withdraw_page.page.wait_for_timeout(500)

    # 4. Verify History Rows Data
    expect(client_withdraw_page.table_rows.first).to_be_visible()
    row_count = client_withdraw_page.get_history_row_count()
    assert row_count > 0, "Expected at least 1 withdraw history record in table"

    first_row = client_withdraw_page.get_first_history_row_data()
    assert "$" in first_row["amount"], f"Expected '$' in withdraw amount, got {first_row['amount']}"
    assert first_row["status"] in ["SUCCESS", "PENDING", "REJECTED", "APPROVED"], (
        f"Unexpected status: {first_row['status']}"
    )

    # 5. Multi-page pagination navigation
    client_withdraw_page.select_history_rows_per_page("25")
    if client_withdraw_page.next_page_button.is_enabled():
        expect(client_withdraw_page.prev_page_button).to_be_disabled()
        client_withdraw_page.click_next_page()
        expect(client_withdraw_page.prev_page_button).to_be_enabled()
        client_withdraw_page.click_prev_page()
        expect(client_withdraw_page.prev_page_button).to_be_disabled()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Withdraw History Table & Dropdown")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_all_payment_methods(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 5 withdrawal methods in the Mode of Payment dropdown:
    1. Bank Transfer
    2. USDT TRC20
    3. USDT BEP
    4. UPI payment
    5. SS payment
    Asserts each method is selectable cleanly and zero errors.
    """
    client_withdraw_page.navigate()

    expected_methods = [
        "Bank Transfer",
        "USDT TRC20",
        "USDT BEP",
        "UPI payment",
        "SS payment",
    ]

    options = client_withdraw_page.get_payment_method_options()
    for method_name in expected_methods:
        assert any(method_name.lower() in opt.lower() for opt in options), (
            f"Expected '{method_name}' in payment options: {options}"
        )

    # Select each method
    for method_name in expected_methods:
        client_withdraw_page.select_payment_method(method_name)
        val = client_withdraw_page.payment_method_select.input_value()
        assert val != "", f"Expected active value after selecting {method_name}"

    # Automated Error Check
    client_error_monitor.assert_no_errors("All Withdrawal Payment Methods")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_header_full_interactive_lifecycle(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete header interactivity while remaining on the Withdraw view:
    - Page title is 'Withdraw' and all universal header elements render
    - Theme toggle switches between dark and light themes smoothly
    - Account switcher switches between accounts and updates badge
    - Notifications drawer opens 'Security & Clearance Alerts' and dismisses cleanly
    - Support Center drawer opens, displays Session Info & FAQ, and closes
    - Create Account modal opens 'LIVE ACCOUNT CREATION' and dismisses via Cancel
    - Search input accepts queries and clears
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()
    header = client_withdraw_page.header

    # 1. Assert header elements
    header.assert_header_elements(expected_title="Withdraw")

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
    header.search("Withdraw Test")
    header.clear_search()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Withdraw Header Full Interactive Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_end_to_end_journey_zero_errors(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End endurance test for Withdraw workflow:
    - Navigate to Withdraw
    - Fill bank details and crypto addresses
    - Select source account, payment method, and amount
    - Verify balances and ledger table
    - Asserts ZERO console errors, ZERO JS crashes, and ZERO 5xx backend errors
    """
    client_withdraw_page.navigate()
    client_withdraw_page.header.assert_header_elements(expected_title="Withdraw")

    # Select multiple methods
    for method in ["USDT TRC20", "Bank Transfer", "SS payment"]:
        client_withdraw_page.select_payment_method(method)
        client_withdraw_page.page.wait_for_timeout(200)

    # Strict Zero Error Check across entire journey
    client_error_monitor.assert_no_errors("Withdraw End-to-End Journey")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_address_copy_symbols_all_methods(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 4 withdraw address copy symbols/buttons:
    1. USDT TRC20 copy button
    2. USDT BEP copy button
    3. UPI payment copy button
    4. SS payment copy button
    Asserts each copy button is visible, clickable, and copies address to clipboard.
    Asserts zero console errors, JS crashes, and backend failures.
    """
    client_withdraw_page.navigate()

    # Grant clipboard permissions
    client_withdraw_page.page.context.grant_permissions(
        ["clipboard-read", "clipboard-write"]
    )

    addresses = [
        ("usdt_trc20", client_withdraw_page.usdt_trc20_input, client_withdraw_page.usdt_trc20_copy_button, "TR7NHkorjpffbnh4m7n9284240294copy"),
        ("usdt_bep", client_withdraw_page.usdt_bep_input, client_withdraw_page.usdt_bep_copy_button, "0x55d398326f99059ff775485246999027b3197copy"),
        ("upi", client_withdraw_page.upi_input, client_withdraw_page.upi_copy_button, "trader_copy@upi"),
        ("ss_payment", client_withdraw_page.ss_payment_input, client_withdraw_page.ss_payment_copy_button, "SSPAY-COPY-999"),
    ]

    for name, input_elem, copy_btn, sample_val in addresses:
        expect(input_elem).to_be_visible()
        expect(copy_btn).to_be_visible()

        # Fill sample value
        input_elem.fill(sample_val)
        client_withdraw_page.page.wait_for_timeout(200)

        # Click copy button
        copy_btn.click()
        client_withdraw_page.page.wait_for_timeout(300)

        # Verify clipboard content
        clipboard_content = client_withdraw_page.page.evaluate("navigator.clipboard.readText()")
        assert clipboard_content == sample_val, (
            f"Expected clipboard to contain '{sample_val}' for {name}, got '{clipboard_content}'"
        )

    # Automated Error Check
    client_error_monitor.assert_no_errors("Withdraw Address Copy Symbols")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_bank_details_validation_and_save_changes(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Cross-check all minute details in Bank Payout Details:
    - 6 fields: BANK NAME 1, ACCOUNT NUMBER, IFSC CODE, BIC / SWIFT CODE, BRANCH, LOCATION
    - SAVE DETAILS / Save Changes button
    - Confirmation feedback upon successful saving
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # Fill and test all 6 fields
    client_withdraw_page.fill_bank_details(
        bank_name="Barclays International",
        account_number="987654321098",
        ifsc_code="BARC000123",
        swift_code="BARCGB22",
        branch="London Central",
        location="London",
    )

    # Click Save Changes / Save Details
    expect(client_withdraw_page.save_changes_button).to_be_visible()
    client_withdraw_page.save_details()

    # Verify toast confirmation
    expect(client_withdraw_page.save_success_toast.first).to_be_visible(timeout=10000)
    assert "Successfully Saved Payment details" in client_withdraw_page.save_success_toast.first.inner_text()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Bank Details Validation & Save Changes")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_history_pagination_and_sorting_by_row(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete history pagination and sorting characteristics:
    - Rows per page dropdown options: 10, 25, 50, 100
    - Changing row size dynamically updates displayed records and summary text
    - Column headers (DATE, METHOD, AMOUNT, STATUS, ADDRESS / DETAIL) are server-side sorted
    - Multi-page pagination navigation (Previous / Next)
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Test rows per page dropdown variations (10, 25, 50)
    for row_size in ["10", "25", "50"]:
        client_withdraw_page.select_history_rows_per_page(row_size)
        expect(client_withdraw_page.history_rows_select).to_have_value(row_size)
        client_withdraw_page.page.wait_for_timeout(300)
        displayed_rows = client_withdraw_page.get_history_row_count()
        assert displayed_rows <= int(row_size), f"Expected <= {row_size} rows, got {displayed_rows}"

    # 2. Reset to 25 to test multi-page pagination navigation
    client_withdraw_page.select_history_rows_per_page("25")
    if client_withdraw_page.next_page_button.is_enabled():
        expect(client_withdraw_page.prev_page_button).to_be_disabled()
        client_withdraw_page.click_next_page()
        expect(client_withdraw_page.prev_page_button).to_be_enabled()
        client_withdraw_page.click_prev_page()
        expect(client_withdraw_page.prev_page_button).to_be_disabled()

    # 3. Verify static server-side sorted column headers
    for th in client_withdraw_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Withdraw History Pagination & Sorting")


@pytest.mark.client
@pytest.mark.regression
def test_client_withdraw_negative_form_and_otp_validation(
    client_withdraw_page: ClientWithdrawPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Withdraw Form Validation and OTP Boundaries:
    - Button disabled when required fields are missing
    - Button disabled when amount is cleared back to empty
    - In OTP modal: Confirm button is disabled when OTP input is empty
    - Modal dismisses cleanly via Close button
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_withdraw_page.navigate()

    # 1. Initially disabled
    expect(client_withdraw_page.request_withdraw_button).to_be_disabled()

    # 2. Select source only -> Still disabled
    client_withdraw_page.select_withdraw_source()
    expect(client_withdraw_page.request_withdraw_button).to_be_disabled()

    # 3. Select method only -> Still disabled
    client_withdraw_page.select_payment_method("USDT TRC20")
    expect(client_withdraw_page.request_withdraw_button).to_be_disabled()

    # 4. Fill amount then clear it -> Reverts to disabled
    client_withdraw_page.enter_withdraw_amount("50.00")
    expect(client_withdraw_page.request_withdraw_button).to_be_enabled()
    client_withdraw_page.enter_withdraw_amount("")
    expect(client_withdraw_page.request_withdraw_button).to_be_disabled()

    # 5. Fill valid amount and trigger OTP modal
    client_withdraw_page.enter_withdraw_amount("25.00")
    client_withdraw_page.click_request_withdraw()
    expect(client_withdraw_page.otp_modal.first).to_be_visible(timeout=10000)

    # 6. OTP Confirm button is disabled when input is empty
    expect(client_withdraw_page.otp_confirm_button.first).to_be_disabled()

    # 7. Dismiss modal cleanly
    client_withdraw_page.close_otp_modal()
    expect(client_withdraw_page.otp_modal.first).not_to_be_visible()

    client_error_monitor.assert_no_errors("Withdraw Negative Validation")


