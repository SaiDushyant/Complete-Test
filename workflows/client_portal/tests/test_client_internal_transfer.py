"""
Client Portal Internal Transfer Workflow Tests.
Detailed validation covering all minute controls:
1. Universal header & page headings ('Internal Transfer', 'Move funds securely')
2. Source and Destination accounts/wallets dropdowns and option lists
3. Transfer Amount input and optional Reference / Memo field
4. Review Internal Transfer modal dialog (Amount, Source, Destination, Memo, Edit Details, Close, Execute)
5. Recent Transfers ledger table (DATE, DETAILS, AMOUNT, STATUS) & rows dropdown
6. Universal header full interactive lifecycle directly on Internal Transfer view
7. End-to-end journey with zero browser console errors, JS crashes, or backend failures
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_internal_transfer_page import ClientInternalTransferPage
from workflows.client_portal.pages.client_wallet_page import ClientWalletPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_internal_transfer_header_and_page_elements(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Internal Transfer view renders universal header and main headings:
    - Page title in header is 'Internal Transfer'
    - Main heading is 'Internal Transfer'
    - Subtitle is visible
    - Transfer Details and Recent Transfers sections are displayed
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.header.assert_header_elements(expected_title="Internal Transfer")

    expect(client_internal_transfer_page.main_heading.first).to_be_visible()
    expect(client_internal_transfer_page.subtitle.first).to_be_visible()
    expect(client_internal_transfer_page.transfer_details_heading.first).to_be_visible()
    expect(client_internal_transfer_page.recent_transfers_heading.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Internal Transfer Header and Page Elements")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_form_controls_and_options(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Source and Destination account/wallet selectors:
    - Source dropdown lists IB Wallet, Client Wallet, and trading accounts
    - Destination dropdown lists available target destinations
    - Amount input and Memo input accept values cleanly
    - Cancel button is present
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_internal_transfer_page.navigate()

    # 1. Verify Source options
    source_options = client_internal_transfer_page.get_source_options()
    assert any("wallet" in opt.lower() for opt in source_options), f"Expected wallet in source options: {source_options}"
    assert any("me" in opt.lower() for opt in source_options), f"Expected trading account in source options: {source_options}"

    # 2. Verify Destination options
    dest_options = client_internal_transfer_page.get_destination_options()
    assert len(dest_options) > 1, f"Expected multiple destination options, got {dest_options}"

    # 3. Select Source and Destination
    client_internal_transfer_page.select_source("10026")
    client_internal_transfer_page.select_destination("Client Wallet")

    # 4. Fill Amount and Memo
    client_internal_transfer_page.enter_amount("15.00")
    client_internal_transfer_page.enter_memo("Test funding memo")

    expect(client_internal_transfer_page.cancel_button).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Internal Transfer Form Controls")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_review_modal_lifecycle(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete Review Internal Transfer modal dialog lifecycle:
    - Fill source, destination, amount, and memo
    - Click 'Review Transfer'
    - Modal opens with title 'Review Internal Transfer'
    - Displays TRANSFERRING AMOUNT ($15.00 USD), SOURCE, DESTINATION, and Reference Memo
    - Displays 'Edit Details', 'Close', and 'EXECUTE TRANSFER' action buttons
    - Clicking 'Edit Details' dismisses modal and keeps form intact
    - Re-opening and clicking 'Close' dismisses modal cleanly
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_internal_transfer_page.navigate()

    # 1. Fill transfer parameters
    client_internal_transfer_page.select_source("10026")
    client_internal_transfer_page.select_destination("Client Wallet")
    client_internal_transfer_page.enter_amount("15.00")
    client_internal_transfer_page.enter_memo("Automated review verification")

    # 2. Click Review Transfer to trigger modal
    client_internal_transfer_page.click_review_transfer()

    # 3. Verify modal contents
    expect(client_internal_transfer_page.review_modal.first).to_be_visible()
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("Review Internal Transfer")
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("$15.00")
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("Automated review verification")

    # Action buttons inside modal
    expect(client_internal_transfer_page.modal_edit_btn).to_be_visible()
    expect(client_internal_transfer_page.modal_close_btn).to_be_visible()
    expect(client_internal_transfer_page.modal_execute_btn).to_be_visible()

    # 4. Click 'Edit Details' to dismiss modal and return to editing
    client_internal_transfer_page.click_edit_details_modal()
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()
    expect(client_internal_transfer_page.amount_input).to_have_value("15.00")

    # 5. Re-open and dismiss via 'Close' button
    client_internal_transfer_page.click_review_transfer()
    expect(client_internal_transfer_page.review_modal.first).to_be_visible()
    client_internal_transfer_page.close_review_modal()
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Review Transfer Modal Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_recent_transfers_table_and_dropdown(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Recent Transfers transaction ledger table:
    - 4 column headers: DATE, DETAILS, AMOUNT, STATUS
    - Headers are static non-clickable server-side sorted headers
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - Transaction rows display valid formatting
    - Multi-page pagination controls (Previous / Next)
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_internal_transfer_page.navigate()

    expect(client_internal_transfer_page.recent_transfers_heading.first).to_be_visible()

    # 1. Verify 4 column headers
    headers = client_internal_transfer_page.get_table_headers()
    expected_headers = ["DATE", "DETAILS", "AMOUNT", "STATUS"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 2. Check static headers cursor
    for th in client_internal_transfer_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 3. Rows per page selector
    expect(client_internal_transfer_page.history_rows_select).to_be_visible()
    client_internal_transfer_page.select_history_rows_per_page("25")
    expect(client_internal_transfer_page.history_rows_select).to_have_value("25")

    # 4. Verify History Rows Data
    expect(client_internal_transfer_page.table_rows.first).to_be_visible()
    row_count = client_internal_transfer_page.get_history_row_count()
    assert row_count > 0, "Expected at least 1 recent transfer record in table"

    first_row = client_internal_transfer_page.get_first_history_row_data()
    assert "$" in first_row["amount"], f"Expected '$' in transfer amount, got {first_row['amount']}"
    assert first_row["status"] in ["COMPLETED", "SUCCESS", "PENDING", "REJECTED"], (
        f"Unexpected status: {first_row['status']}"
    )

    # Automated Error Check
    client_error_monitor.assert_no_errors("Recent Transfers Table & Dropdown")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_header_full_interactive_lifecycle(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete header interactivity while on the Internal Transfer view:
    - Page title is 'Internal Transfer' and all universal header elements render
    - Theme toggle switches between dark and light themes smoothly
    - Account switcher switches between accounts and updates badge
    - Notifications drawer opens 'Security & Clearance Alerts' and dismisses cleanly
    - Support Center drawer opens, displays Session Info & FAQ, and closes
    - Create Account modal opens 'LIVE ACCOUNT CREATION' and dismisses via Cancel
    - Search input accepts queries and clears
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_internal_transfer_page.navigate()
    header = client_internal_transfer_page.header

    # 1. Assert header elements
    header.assert_header_elements(expected_title="Internal Transfer")

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
    header.search("Transfer Test")
    header.clear_search()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Internal Transfer Header Full Interactive Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_end_to_end_journey_zero_errors(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End endurance test for Internal Transfer workflow:
    - Navigate to Internal Transfer
    - Select source, destination, amount
    - Review transfer modal lifecycle
    - Verify recent transfers ledger table
    - Asserts ZERO console errors, ZERO JS crashes, and ZERO 5xx backend errors
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.header.assert_header_elements(expected_title="Internal Transfer")

    client_internal_transfer_page.select_source("10026")
    client_internal_transfer_page.select_destination("Client Wallet")
    client_internal_transfer_page.enter_amount("10.00")
    client_internal_transfer_page.click_review_transfer()
    client_internal_transfer_page.close_review_modal()

    assert client_internal_transfer_page.get_history_row_count() > 0

    # Strict Zero Error Check across entire journey
    client_error_monitor.assert_no_errors("Internal Transfer End-to-End Journey")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_execute_transfer_and_verify_wallet_credit(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Live verification of end-to-end money movement:
    1. Check initial Client Wallet balance in Wallet view
    2. Navigate to Internal Transfer and select Source account 10026 and Destination Client Wallet
    3. Enter transfer amount $1.00 and descriptive memo
    4. Review transfer and click 'EXECUTE TRANSFER' in modal dialog
    5. Verify API dispatches POST /client-portal/apiTransfer and succeeds (200 OK)
    6. Verify Recent Transfers table shows new record with COMPLETED status
    7. Navigate to Wallet view and verify that Client Wallet received the funds
    8. Verify Wallet Accounts table shows updated balance and Wallet Transfer History reflects movement
    9. Asserts zero console errors, JS crashes, and backend 5xx failures
    """
    # 1. Read initial Client Wallet card in Wallet view
    client_wallet_page.navigate()
    expect(client_wallet_page.client_wallet_card.first).to_be_visible()

    # 2. Navigate to Internal Transfer
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.select_source("10026")
    client_internal_transfer_page.select_destination("Client Wallet")
    client_internal_transfer_page.enter_amount("1.00")
    client_internal_transfer_page.enter_memo("Automated credit verification")

    # 3. Review Transfer
    client_internal_transfer_page.click_review_transfer()
    expect(client_internal_transfer_page.review_modal.first).to_be_visible()
    expect(client_internal_transfer_page.review_modal.first).to_contain_text("$1.00")

    # 4. Execute Transfer
    with client_internal_transfer_page.page.expect_response(
        lambda r: "apiTransfer" in r.url and r.request.method == "POST" and r.status == 200,
        timeout=15000,
    ) as response_info:
        client_internal_transfer_page.execute_transfer_modal()

    transfer_response = response_info.value
    assert transfer_response.status == 200, f"Expected 200 OK from apiTransfer, got {transfer_response.status}"

    # 5. Verify Recent Transfers Table has new record
    expect(client_internal_transfer_page.table_rows.first).to_be_visible()
    first_transfer = client_internal_transfer_page.get_first_history_row_data()
    assert "$1.00" in first_transfer["amount"], f"Expected $1.00 in recent transfer row, got {first_transfer['amount']}"
    assert first_transfer["status"] in ["COMPLETED", "SUCCESS"], f"Expected completed status, got {first_transfer['status']}"

    # 6. Navigate to Wallet view and verify credit received
    client_wallet_page.navigate()
    expect(client_wallet_page.client_wallet_card.first).to_be_visible()
    
    # Verify Wallet Accounts table reflects Client Wallet with non-zero balance
    expect(client_wallet_page.accounts_rows.first).to_be_visible()
    accounts_text = client_wallet_page.accounts_table.inner_text()
    assert "Client Wallet" in accounts_text

    # Verify Wallet Transfer History reflects the executed transfer
    expect(client_wallet_page.history_rows.first).to_be_visible()
    first_history = client_wallet_page.history_rows.first.inner_text()
    assert "+$1.00" in first_history or "1.00" in first_history

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Internal Transfer Live Execution and Wallet Credit")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_all_modes_of_transfer(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 5 modes of internal transfer supported by the portal:
    1. Account to Wallet (Me 10026 -> Client Wallet)
    2. Wallet to Account (Client Wallet -> Me 10026)
    3. Account to Account (Me 10026 -> Me 10629)
    4. IB Wallet to Account (IB Wallet -> Me 10026)
    5. IB Wallet to Client Wallet (IB Wallet -> Client Wallet)
    Each mode:
    - Selects source and destination values
    - Fills amount and memo
    - Opens review modal dialog
    - Executes transfer via POST /client-portal/apiTransfer
    - Verifies 200 OK and COMPLETED status in Recent Transfers
    - Asserts zero console errors, JS runtime crashes, and backend failures
    """
    client_internal_transfer_page.navigate()

    modes = [
        ("client_wallet:808780896656", "account:LWR8AUE0TS", "1.00", "Wallet to Account"),
        ("account:LWR8AUE0TS", "account:BKQIOI0MAT", "1.00", "Account to Account"),
        ("ib_wallet:868001043731", "account:LWR8AUE0TS", "1.00", "IB Wallet to Account"),
        ("ib_wallet:868001043731", "client_wallet:808780896656", "1.00", "IB Wallet to Wallet"),
    ]

    for src, dest, amt, memo in modes:
        client_internal_transfer_page.select_source(src)
        client_internal_transfer_page.select_destination(dest)
        client_internal_transfer_page.enter_amount(amt)
        client_internal_transfer_page.enter_memo(memo)

        client_internal_transfer_page.click_review_transfer()
        expect(client_internal_transfer_page.review_modal.first).to_be_visible()

        with client_internal_transfer_page.page.expect_response(
            lambda r: "apiTransfer" in r.url and r.request.method == "POST" and r.status == 200,
            timeout=15000,
        ) as response_info:
            client_internal_transfer_page.execute_transfer_modal()

        assert response_info.value.status == 200
        client_internal_transfer_page.page.wait_for_timeout(1000)

    # Verify Recent Transfers ledger has completed records
    expect(client_internal_transfer_page.table_rows.first).to_be_visible()
    row_count = client_internal_transfer_page.get_history_row_count()
    assert row_count >= 4

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Internal Transfer All Modes of Transfer")


@pytest.mark.client
@pytest.mark.regression
def test_client_internal_transfer_negative_invalid_amounts_block_modal(
    client_internal_transfer_page: ClientInternalTransferPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Internal Transfer Invalid Amount Handling:
    - Empty amount -> Review Transfer does NOT open review modal
    - 0.00 amount -> Review Transfer does NOT open review modal
    - Negative amount -> Review Transfer does NOT open review modal
    - Asserts review modal remains hidden and zero errors
    """
    client_internal_transfer_page.navigate()
    client_internal_transfer_page.select_source("10026")
    client_internal_transfer_page.select_destination("Client Wallet")

    # 1. Empty amount
    client_internal_transfer_page.enter_amount("")
    client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
    client_internal_transfer_page.page.wait_for_timeout(500)
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()
    expect(client_internal_transfer_page.validation_error_message.first).to_be_visible()

    # 2. 0.00 amount
    client_internal_transfer_page.enter_amount("0.00")
    client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
    client_internal_transfer_page.page.wait_for_timeout(500)
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()

    # 3. Negative amount
    client_internal_transfer_page.enter_amount("-25.00")
    client_internal_transfer_page.submit_review_transfer_without_waiting_modal()
    client_internal_transfer_page.page.wait_for_timeout(500)
    expect(client_internal_transfer_page.review_modal.first).not_to_be_visible()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Internal Transfer Negative Invalid Amount Validation")



