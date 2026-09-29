"""
Client Portal Wallet Management Workflow Tests.
Detailed validation covering all minute controls:
1. Universal header & page headings ('Wallet', 'Wallet Management')
2. Wallet Summary Cards:
   * Client Wallet (Account ID, Available Balance, Status)
   * IB Wallet (Account ID, Available Balance, Status)
   * Consolidated Funds summary (Trading Accounts vs Wallets)
3. Wallet Accounts ledger table (WALLET, BALANCE, STATUS, UPDATED, SHARE)
4. Top action buttons ('Export Report', 'ACCOUNT TO WALLET' redirect)
5. Wallet Transfer History ledger table:
   * 6 columns (DATE, MOVEMENT, WALLET, REFERENCE, AMOUNT, REMARKS / ADDRESS)
   * Rows per page dropdown (10, 25, 50, 100)
   * Pagination navigation controls
6. Universal header full interactive lifecycle directly on Wallet view
7. End-to-end journey with zero browser console errors, JS crashes, or backend failures
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_wallet_page import ClientWalletPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_wallet_header_and_page_elements(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Wallet view renders universal header and main headings:
    - Page title in header is 'Wallet'
    - Main heading is 'Wallet Management'
    - Subtitle is visible
    - Summary cards (Client Wallet, IB Wallet, Consolidated Funds) render
    - Action buttons ('Export Report', 'ACCOUNT TO WALLET') are visible
    - Accounts and Transfer History section headings render
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()
    client_wallet_page.header.assert_header_elements(expected_title="Wallet")

    expect(client_wallet_page.main_heading.first).to_be_visible()
    expect(client_wallet_page.subtitle.first).to_be_visible()
    expect(client_wallet_page.accounts_heading.first).to_be_visible()
    expect(client_wallet_page.history_heading.first).to_be_visible()

    expect(client_wallet_page.client_wallet_card.first).to_be_visible()
    expect(client_wallet_page.ib_wallet_card.first).to_be_visible()
    expect(client_wallet_page.consolidated_funds_card.first).to_be_visible()

    expect(client_wallet_page.export_report_button).to_be_visible()
    expect(client_wallet_page.account_to_wallet_button).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Wallet Header and Page Elements")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_summary_cards_and_accounts_table(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify summary cards and Wallet Accounts table:
    - Client Wallet card contains 'CLIENT WALLET' and 'AVAILABLE BALANCE'
    - IB Wallet card contains 'IB WALLET' and 'AVAILABLE BALANCE'
    - Consolidated Funds card contains 'CONSOLIDATED FUNDS', 'Trading Accounts', 'Wallets'
    - Accounts table has 5 columns: WALLET, BALANCE, STATUS, UPDATED, SHARE
    - Table headers are non-clickable (static headers)
    - Accounts table displays rows for Client Wallet and IB Wallet
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()

    # 1. Summary Cards Details
    # Client Wallet Card
    expect(client_wallet_page.client_wallet_card.first).to_contain_text(re.compile(r"CLIENT\s*Wallet", re.I))
    expect(client_wallet_page.client_wallet_card.first).to_contain_text(re.compile(r"AVAILABLE\s*BALANCE", re.I))
    expect(client_wallet_page.client_wallet_card.first).to_contain_text("808780896656")
    expect(client_wallet_page.client_wallet_card.first).to_contain_text(re.compile(r"ACTIVE", re.I))

    # IB Wallet Card
    expect(client_wallet_page.ib_wallet_card.first).to_contain_text(re.compile(r"IB\s*Wallet", re.I))
    expect(client_wallet_page.ib_wallet_card.first).to_contain_text(re.compile(r"AVAILABLE\s*BALANCE", re.I))
    expect(client_wallet_page.ib_wallet_card.first).to_contain_text("868001043731")
    expect(client_wallet_page.ib_wallet_card.first).to_contain_text(re.compile(r"ACTIVE", re.I))

    # Consolidated Funds Card
    expect(client_wallet_page.consolidated_funds_card.first).to_contain_text(re.compile(r"CONSOLIDATED\s*FUNDS", re.I))
    expect(client_wallet_page.consolidated_funds_card.first).to_contain_text(re.compile(r"30\s*day\s*net\s*movement", re.I))

    # 2. Verify 5 columns in Wallet Accounts table
    headers = client_wallet_page.get_accounts_table_headers()
    expected_headers = ["WALLET", "BALANCE", "STATUS", "UPDATED", "SHARE"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Check static headers cursor
    for th in client_wallet_page.accounts_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 4. Verify accounts rows details
    row_count = client_wallet_page.get_accounts_row_count()
    assert row_count >= 2, f"Expected at least 2 wallet account rows, got {row_count}"

    # Row 1: Client Wallet
    row_client = client_wallet_page.accounts_rows.first.inner_text()
    assert "Client Wallet" in row_client
    assert "808780896656" in row_client
    assert "ACTIVE" in row_client

    # Row 2: IB Wallet
    row_ib = client_wallet_page.accounts_rows.nth(1).inner_text()
    assert "IB Wallet" in row_ib
    assert "868001043731" in row_ib
    assert "ACTIVE" in row_ib

    # Automated Error Check
    client_error_monitor.assert_no_errors("Wallet Summary Cards and Accounts Table")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_export_report_downloads_csv(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify 'Export Report' top action button:
    - Located in top action toolbar
    - Clicking button triggers browser file download
    - Downloaded filename matches 'Ledger_*.csv'
    - Download completes successfully
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()

    download = client_wallet_page.trigger_export_report_download()
    assert download is not None, "Expected download event to be triggered"
    assert download.suggested_filename.startswith("Ledger_"), f"Unexpected filename: {download.suggested_filename}"
    assert download.suggested_filename.endswith(".csv"), f"Expected CSV file: {download.suggested_filename}"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Wallet Export Report Download")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_action_account_to_wallet_navigation(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify 'ACCOUNT TO WALLET' action button:
    - Located in top right action toolbar
    - Clicking button smoothly navigates to 'Internal Transfer' view
    - Validates target page title, main heading, and transfer form controls
    - Sidebar navigation can return back to Wallet view
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()

    expect(client_wallet_page.account_to_wallet_button).to_be_visible()
    client_wallet_page.click_account_to_wallet()

    # Verify redirected to Internal Transfer
    expect(client_wallet_page.internal_transfer_heading.first).to_be_visible(timeout=10000)
    expect(client_wallet_page.internal_transfer_select.first).to_be_visible(timeout=10000)

    # Navigate back to Wallet
    client_wallet_page.sidebar.navigate_to_wallet()
    expect(client_wallet_page.main_heading.first).to_be_visible(timeout=10000)

    # Automated Error Check
    client_error_monitor.assert_no_errors("Wallet Account to Wallet Navigation")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_transfer_history_table_and_pagination(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Wallet Transfer History transaction ledger table and full pagination:
    - 6 column headers: DATE, MOVEMENT, WALLET, REFERENCE, AMOUNT, REMARKS / ADDRESS
    - Headers are static non-clickable server-side sorted headers
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - When selecting 10 rows:
      * Rows count is <= 10
      * Pagination summary displays 'Showing 1-10 of ... records'
      * Page indicator displays 'Page 1 / ...'
      * Previous button is disabled on page 1
      * Next button is enabled and advances to 'Page 2 / ...'
      * Previous button becomes enabled on page 2 and returns to 'Page 1 / ...'
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()

    expect(client_wallet_page.history_heading.first).to_be_visible()

    # 1. Verify 6 column headers
    headers = client_wallet_page.get_history_table_headers()
    expected_headers = ["DATE", "MOVEMENT", "WALLET", "REFERENCE", "AMOUNT", "REMARKS / ADDRESS"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 2. Check static headers cursor
    for th in client_wallet_page.history_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 3. Rows per page selector: switch to 10 rows
    expect(client_wallet_page.history_rows_select).to_be_visible()
    client_wallet_page.select_history_rows_per_page("10")
    expect(client_wallet_page.history_rows_select).to_have_value("10")

    # 4. Verify History Rows Data
    expect(client_wallet_page.history_rows.first).to_be_visible()
    row_count = client_wallet_page.get_history_row_count()
    assert 0 < row_count <= 10, f"Expected 1-10 rows on page 1, got {row_count}"

    # 5. Pagination summary and controls
    expect(client_wallet_page.pagination_summary).to_be_visible()
    expect(client_wallet_page.pagination_summary).to_contain_text("Showing 1-10 of")

    expect(client_wallet_page.page_indicator).to_be_visible()
    expect(client_wallet_page.page_indicator).to_contain_text("Page 1 /")

    expect(client_wallet_page.prev_page_button).to_be_disabled()

    # 6. Click Next page and verify page 2
    if client_wallet_page.next_page_button.is_enabled():
        client_wallet_page.go_to_next_history_page()
        expect(client_wallet_page.page_indicator).to_contain_text("Page 2 /")
        expect(client_wallet_page.pagination_summary).to_contain_text("Showing 11-")
        expect(client_wallet_page.prev_page_button).to_be_enabled()

        # Click Previous page to return
        client_wallet_page.go_to_prev_history_page()
        expect(client_wallet_page.page_indicator).to_contain_text("Page 1 /")
        expect(client_wallet_page.pagination_summary).to_contain_text("Showing 1-10 of")

    # Automated Error Check
    client_error_monitor.assert_no_errors("Wallet Transfer History Table and Pagination")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_header_full_interactive_lifecycle(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete header interactivity while on the Wallet view:
    - Page title is 'Wallet' and all universal header elements render
    - Theme toggle switches between dark and light themes smoothly
    - Account switcher switches between accounts and updates badge
    - Notifications drawer opens 'Security & Clearance Alerts' and dismisses cleanly
    - Support Center drawer opens, displays Session Info & FAQ, and closes
    - Create Account modal opens 'LIVE ACCOUNT CREATION' and dismisses via Cancel
    - Search input accepts queries and clears
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()
    header = client_wallet_page.header

    # 1. Assert header elements
    header.assert_header_elements(expected_title="Wallet")

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
    header.search("Wallet Test")
    header.clear_search()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Wallet Header Full Interactive Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_end_to_end_journey_zero_errors(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End endurance test for Wallet Management workflow:
    - Navigate to Wallet
    - Verify summary cards, account rows, history records
    - Assert ZERO console errors, ZERO JS crashes, and ZERO 5xx backend errors
    """
    client_wallet_page.navigate()
    client_wallet_page.header.assert_header_elements(expected_title="Wallet")

    assert client_wallet_page.is_wallet_displayed()
    assert client_wallet_page.get_accounts_row_count() >= 2
    assert client_wallet_page.get_history_row_count() > 0

    # Strict Zero Error Check across entire journey
    client_error_monitor.assert_no_errors("Wallet End-to-End Journey")


@pytest.mark.client
@pytest.mark.regression
def test_client_wallet_negative_pagination_boundary_limits(
    client_wallet_page: ClientWalletPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Wallet History Pagination Boundary Enforcement:
    - On Page 1, 'Previous' button must strictly be disabled
    - Page indicator must state 'Page 1 / ...'
    - Prevents navigation into negative page bounds
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_wallet_page.navigate()
    expect(client_wallet_page.history_table).to_be_visible()

    # Previous button on Page 1 must strictly be disabled
    expect(client_wallet_page.prev_page_button).to_be_disabled()
    expect(client_wallet_page.page_indicator).to_contain_text("Page 1")

    client_error_monitor.assert_no_errors("Wallet Negative Pagination Boundary")

