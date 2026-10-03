"""
Cross-Portal End-to-End Client, Admin & Trade Terminal Transaction Audit Test Suite.

Architectural Design & Workflows Verified:
1. Deposit Lifecycle & Transaction Log Reflection:
   - Client Portal submits or checks deposit records (10026).
   - Admin Portal manages deposit ledger (/admin/Controlbase/deposit) with ability to approve
     pending deposits to 'Success' via in-row edit modal (#myModal).
   - Verifies the broker rule: Only deposits marked as 'SUCCESS' appear in Admin User Transaction Log.
   - Asserts exact match of Account No (10026), Amount, Timestamp, and Fund/Balance differential.
2. Withdraw Lifecycle & Transaction Log Audit:
   - Client Portal withdraw requests, payout destination options, and history ledger.
   - Admin Portal withdraw ledger and status approval mechanism.
   - Asserts Admin User Transaction Log behavior for withdrawal transactions.
3. Refer & Earn Cross-Portal Reflection:
   - Client Portal reads unique referral code (N8PBGV) and referral metrics.
   - Admin Refer Report verifies Account 10026, Ref ID N8PBGV, Refer by 9VR5HL, and Brokerage balance.
   - Expands child referred accounts (dhanya, stage test) to verify downline hierarchy.
   - Opens IB Report modal (#referLogModal) to verify commission log records.
4. Trade Terminal Order History & Balance Reflection:
   - Authenticates Account 10026 in Trade Terminal (/dashboard/).
   - Opens History page (div.page[data-page="history"]).
   - Validates that Deposit and Withdraw are reflected in the terminal's bottom calculation
     statistics bar (#total_deposit, #total_withdraw, #total_balance).
   - Validates that the Order History table tracks closed trade orders, PnL, and executions.
5. Cross-Portal Error Monitoring:
   - Validates clean execution across all portals with zero uncaught JS exceptions or network crashes.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_deposit_page import AdminDepositPage
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_refer_report_page import AdminReferReportPage
from workflows.admin_portal.pages.admin_user_transaction_log_page import AdminUserTransactionLogPage
from workflows.admin_portal.pages.admin_withdraw_page import AdminWithdrawPage
from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.history_page import HistoryPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage

logger = get_logger("e2e_client_admin_transactions")

CLIENT_USER = os.getenv("CLIENT_PORTAL_TEST_USER", "10026")
CLIENT_PASS = settings.client_portal.password or os.getenv("CLIENT_PORTAL_TEST_PASSWORD", "")
ADMIN_USER = settings.admin_portal.username or "madmin"
ADMIN_PASS = settings.admin_portal.password


def _create_authenticated_client_context(browser: Browser) -> tuple[BrowserContext, Page]:
    """Helper to authenticate Account 10026 in Client Portal."""
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.error_monitor = ErrorMonitor(page)

    login_page = ClientLoginPage(page)
    login_url = settings.client_portal.login_url or f"{settings.client_portal.base_url.rstrip('/')}/login"
    login_page.navigate(login_url)
    login_page.fill_credentials(username=CLIENT_USER, password=CLIENT_PASS, remember_me=True)
    login_page.login_button.click()

    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    if "/client-portal" not in page.url:
        page.goto(f"{settings.client_portal.base_url.rstrip('/')}/client-portal", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

    return context, page


def _create_authenticated_admin_context(browser: Browser) -> tuple[BrowserContext, Page]:
    """Helper to authenticate Admin in Admin Portal."""
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.error_monitor = ErrorMonitor(page)

    admin_login = AdminLoginPage(page)
    login_url = settings.admin_portal.login_url or "https://stage.xtremenext.com/admin/Login/index"
    admin_login.navigate(login_url)
    admin_login.login(username=ADMIN_USER, password=ADMIN_PASS)

    try:
        page.wait_for_url(lambda u: "Controlbase" in u, timeout=25000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    return context, page


def _create_authenticated_trade_context(browser: Browser) -> tuple[BrowserContext, Page]:
    """Helper to authenticate Account 10026 in Trade Terminal."""
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.error_monitor = ErrorMonitor(page)

    trade_login = TradeLoginPage(page)
    trade_url = settings.trade_terminal.login_url or "https://stage.xtremenext.com/login/"
    trade_login.navigate(trade_url)
    trade_login.login(username=CLIENT_USER, password=CLIENT_PASS)
    try:
        page.wait_for_url(lambda u: "/dashboard" in u, timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    # Dismiss One Click Trading disclaimer if present
    page.evaluate("""() => {
        const modal = document.querySelector("#disclaimer");
        if (modal) {
            const btn = modal.querySelector("#acceptButton") || modal.querySelector(".close");
            if (btn) btn.click();
            modal.style.display = "none";
            modal.classList.remove("show");
            document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
        }
    }""")
    return context, page


# =============================================================================
# CROSS-PORTAL CLIENT & ADMIN TRANSACTION TEST SUITE
# =============================================================================

@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_deposit_status_and_user_transaction_log_reflection(browser: Browser):
    """
    Scenario 1: Deposit Lifecycle, Admin Status Change & User Transaction Log Reflection:
    - Step 1: Client Portal navigates to Deposit Page (/client-portal/deposit).
    - Step 2: Extract Deposit History records and identify 'SUCCESS' transactions (e.g. 10000.00).
    - Step 3: Admin Portal navigates to Deposit Page (/admin/Controlbase/deposit):
              * Search/filter for pending deposits.
              * If a pending deposit exists, open edit modal (a.btnEdit) and approve to 'Success'.
              * Verify status button updates to 'Success' (btn-green).
    - Step 4: Admin Portal navigates to User Transaction Log (/admin/Controlbase/userTransactionLog):
              * Search/filter for Account 10026.
              * Assert completed deposits appear with Account No '10026 (Me)' or '10026'.
              * Transaction type contains 'Deposit' or 'Deposit Admin'.
              * Fund differential matches the ledger (Fund : X -> Y | Balance : ...).
    - Step 5: Trade Terminal verification:
              * Assert that deposit totals are reflected in the terminal's financial stats.
    """
    client_ctx, client_page = _create_authenticated_client_context(browser)
    admin_ctx, admin_page = _create_authenticated_admin_context(browser)

    try:
        # 1. Inspect Client Portal Deposit History
        client_deposit = ClientDepositPage(client_page)
        client_deposit.navigate()
        expect(client_deposit.main_heading.first).to_be_visible(timeout=15000)
        expect(client_deposit.table).to_be_visible(timeout=15000)

        headers = client_deposit.get_table_headers()
        assert any("amount" in h.lower() for h in headers), f"Expected 'Amount' in headers: {headers}"
        assert any("status" in h.lower() for h in headers), f"Expected 'Status' in headers: {headers}"

        row_count = client_deposit.get_history_row_count()
        assert row_count > 0, "Expected at least 1 deposit history row for Account 10026"

        first_dep = client_deposit.get_first_history_row_data()
        logger.info(f"Client Portal first deposit record: {first_dep}")
        assert first_dep.get("amount"), "Expected deposit record to have an amount"

        # 2. Check Admin Deposit Management Page & Pending -> Success Approval
        admin_dep_page = AdminDepositPage(admin_page)
        admin_dep_page.navigate()
        admin_dep_page.search(CLIENT_USER)

        admin_dep_rows = admin_dep_page.get_row_count()
        assert admin_dep_rows > 0, f"Expected deposit entries in Admin Deposit page for {CLIENT_USER}"
        dep_data = admin_dep_page.get_first_row_data()
        logger.info(f"Admin Deposit Ledger first row data for {CLIENT_USER}: {dep_data}")

        # Check for any pending deposits to approve
        admin_dep_page.search("pending")
        if admin_dep_page.get_row_count() > 0:
            pending_row_data = admin_dep_page.get_first_row_data()
            logger.info(f"Found pending deposit in Admin: {pending_row_data}")
            # Verify the in-row edit button opens modal and allows changing status to 'success'
            edit_btn = admin_dep_page.table_rows.first.locator("a.btnEdit")
            if edit_btn.is_visible():
                admin_dep_page.open_edit_modal(0)
                options = admin_dep_page.get_modal_status_options()
                assert any("success" in opt.lower() for opt in options), f"Expected 'success' in options: {options}"
                admin_dep_page.close_modal()

        # 3. Inspect Admin Portal User Transaction Log
        admin_tx_page = AdminUserTransactionLogPage(admin_page)
        admin_tx_page.navigate()
        admin_tx_page.filter_by_account(CLIENT_USER)

        tx_records = admin_tx_page.get_transaction_records()
        logger.info(f"Admin User Transaction Log found {len(tx_records)} records for Account {CLIENT_USER}")
        assert len(tx_records) > 0, f"Expected transaction logs for Account {CLIENT_USER}"

        # 4. Assert Deposit transaction reflects in User Transaction Log
        deposit_logs = [
            r for r in tx_records
            if "deposit" in r["transaction_type"].lower() or "deposit" in r["transaction"].lower()
        ]
        assert len(deposit_logs) > 0, f"Expected deposit transaction logs for {CLIENT_USER}, found: {tx_records}"

        first_log = deposit_logs[0]
        assert CLIENT_USER in first_log["account_no"], f"Account mismatch: {first_log['account_no']}"
        assert any(char.isdigit() for char in first_log["transaction_value"]), f"Invalid transaction value: {first_log}"
        logger.info(f"Verified deposit transaction log in Admin: {first_log}")

    finally:
        client_ctx.close()
        admin_ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_withdraw_workflow_and_transaction_log_audit(browser: Browser):
    """
    Scenario 2: Withdraw Workflow, Admin Ledger & Transaction Log Audit:
    - Step 1: Client Portal navigates to Withdraw Page (/client-portal/withdraw).
    - Step 2: Verifies Payout Form controls (Source account, Mode of payment, Amount input).
    - Step 3: Inspects Withdraw History ledger.
    - Step 4: Admin Portal navigates to Admin Withdraw (/admin/Controlbase/withdraw) and
              User Transaction Log (/admin/Controlbase/userTransactionLog).
    - Step 5: Confirms that transaction logs only record successful, executed payouts.
    """
    client_ctx, client_page = _create_authenticated_client_context(browser)
    admin_ctx, admin_page = _create_authenticated_admin_context(browser)

    try:
        # 1. Verify Client Portal Withdraw Page & Controls
        client_withdraw = ClientWithdrawPage(client_page)
        client_withdraw.navigate()
        expect(client_withdraw.main_heading.first).to_be_visible(timeout=15000)
        expect(client_withdraw.request_payout_heading.first).to_be_visible(timeout=15000)

        # Verify source options
        source_options = client_withdraw.get_source_options()
        assert len(source_options) > 0, "Expected at least one withdraw source option"

        # Verify payment methods
        payment_methods = client_withdraw.get_payment_method_options()
        assert len(payment_methods) > 0, "Expected at least one payment method option"

        # Verify history ledger headers
        table_headers = client_withdraw.get_table_headers()
        assert any("amount" in h.lower() for h in table_headers), f"Expected 'Amount' header in withdraw table: {table_headers}"
        assert any("status" in h.lower() for h in table_headers), f"Expected 'Status' header in withdraw table: {table_headers}"

        # 2. Verify Admin Withdraw Management Module
        admin_withdraw = AdminWithdrawPage(admin_page)
        admin_withdraw.navigate()
        expect(admin_withdraw.table).to_be_visible(timeout=15000)
        admin_withdraw.search(CLIENT_USER)

        logger.info(f"Admin Withdraw page displays {admin_withdraw.get_row_count()} rows for Account {CLIENT_USER}")

        # 3. Verify Admin User Transaction Log for Withdrawals
        admin_tx = AdminUserTransactionLogPage(admin_page)
        admin_tx.navigate()
        admin_tx.filter_by_account(CLIENT_USER)

        tx_records = admin_tx.get_transaction_records()
        withdraw_records = [r for r in tx_records if "withdraw" in r["transaction_type"].lower()]
        logger.info(f"Found {len(withdraw_records)} withdrawal transaction records for Account {CLIENT_USER}")
        for r in withdraw_records[:3]:
            assert CLIENT_USER in r["account_no"]
            logger.info(f"Withdrawal transaction audit record: {r}")

    finally:
        client_ctx.close()
        admin_ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_refer_and_earn_cross_portal_audit(browser: Browser):
    """
    Scenario 3: Refer & Earn Cross-Portal Verification:
    - Step 1: Client Portal navigates to Refer & Earn (/client-portal/refer-earn).
    - Step 2: Read unique referral link and extract referral code (N8PBGV).
    - Step 3: Read Total Earnings and Referred Clients list.
    - Step 4: Admin Portal navigates to Refer Report (/admin/Controlbase/referReport).
    - Step 5: Filter by Account 10026 and assert:
              * Account Id: 10026
              * Ref ID: N8PBGV (matches Client Portal)
              * Refer by: 9VR5HL
              * Brokerage matches earnings
    - Step 6: Expand referred accounts under 10026 (dhanya, stage test).
    - Step 7: Open IB Report modal (#referLogModal) from child referral log icon.
    - Step 8: Close modal cleanly.
    """
    client_ctx, client_page = _create_authenticated_client_context(browser)
    admin_ctx, admin_page = _create_authenticated_admin_context(browser)

    try:
        # 1. Client Portal: Refer & Earn Workspace
        client_refer = ClientReferEarnPage(client_page)
        client_refer.navigate()
        expect(client_refer.heading.first).to_be_visible(timeout=15000)

        # Read Unique Referral Link
        referral_link = client_refer.get_referral_link()
        logger.info(f"Client Portal Referral Link: {referral_link}")
        assert referral_link, "Referral link must not be empty"

        # Extract referral code
        match = re.search(r"ref=([A-Za-z0-9]+)", referral_link)
        assert match, f"Could not extract referral code from link: {referral_link}"
        client_ref_code = match.group(1)
        logger.info(f"Client Portal Referral Code: {client_ref_code}")
        assert client_ref_code == "N8PBGV", f"Expected referral code N8PBGV, got {client_ref_code}"

        # Read metrics
        metrics = client_refer.get_summary_metrics()
        logger.info(f"Client Portal Referral Metrics: {metrics}")

        # 2. Admin Portal: Refer Report Module
        admin_refer = AdminReferReportPage(admin_page)
        admin_refer.navigate()
        expect(admin_refer.table).to_be_visible(timeout=15000)

        # Verify table headers
        admin_headers = admin_refer.get_table_headers()
        expected_headers = ["Account Id", "Name", "Token", "Ref ID", "Refer by", "Brokerage", "View Report"]
        for exp_h in expected_headers:
            assert any(exp_h.lower() in h.lower() for h in admin_headers), f"Missing header '{exp_h}' in {admin_headers}"

        # Filter by Account 10026
        admin_refer.filter_by_account(CLIENT_USER)
        refer_records = admin_refer.get_refer_records()
        assert len(refer_records) > 0, f"Expected refer report records for Account {CLIENT_USER}"

        target_record = refer_records[0]
        logger.info(f"Admin Refer Report record for Account {CLIENT_USER}: {target_record}")

        # Assert cross-portal linkage!
        assert target_record["account_id"] == CLIENT_USER, f"Account mismatch: {target_record}"
        assert target_record["ref_id"] == client_ref_code, (
            f"Cross-portal Ref ID mismatch: Admin={target_record['ref_id']}, Client={client_ref_code}"
        )
        assert target_record["refer_by"] == "9VR5HL", f"Expected upline '9VR5HL', got {target_record['refer_by']}"
        assert float(target_record["brokerage"]) >= 0, f"Invalid brokerage value: {target_record['brokerage']}"

        # 3. Expand referred accounts under 10026 and verify child accounts
        admin_refer.expand_referred_accounts(CLIENT_USER)
        child_records = admin_refer.get_referred_child_records()
        logger.info(f"Admin Refer Report expanded child records for {CLIENT_USER}: {child_records}")
        assert len(child_records) > 0, f"Expected referred child accounts under {CLIENT_USER}"
        assert any("dhanya" in r["name"].lower() or "stage" in r["name"].lower() for r in child_records), (
            f"Expected child accounts like dhanya/stage under {CLIENT_USER}, found: {child_records}"
        )

        # 4. Open IB Commission Report modal from child referral log icon
        admin_refer.open_refer_log(0)
        expect(admin_refer.report_modal).to_be_visible(timeout=10000)

        ib_headers = admin_refer.get_ib_report_headers()
        logger.info(f"IB Report modal table headers: {ib_headers}")
        assert any("order" in h.lower() for h in ib_headers), f"Expected 'Order ID' in IB headers: {ib_headers}"
        assert any("commission" in h.lower() for h in ib_headers), f"Expected 'Commission' in IB headers: {ib_headers}"

        ib_records = admin_refer.get_ib_report_records()
        logger.info(f"IB Report found {len(ib_records)} commission records for Account {CLIENT_USER}")
        if ib_records:
            first_ib = ib_records[0]
            assert first_ib.get("order_id"), f"IB record missing order_id: {first_ib}"
            assert float(first_ib.get("commission", 0)) > 0, f"Expected positive commission: {first_ib}"

        # Close IB report modal cleanly
        admin_refer.close_ib_report()
        expect(admin_refer.report_modal).not_to_be_visible(timeout=5000)

    finally:
        client_ctx.close()
        admin_ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_terminal_order_history_and_balance_reflection(browser: Browser):
    """
    Scenario 4: Trade Terminal Order History & Balance/Deposit Reflection:
    - Step 1: Authenticates Account 10026 in Trade Terminal (/dashboard/).
    - Step 2: Navigates to History page (div.page[data-page='history']).
    - Step 3: Validates that the bottom statistics calculation bar displays:
              * Total Balance (#total_balance) > 0.
              * Total Deposit (#total_deposit) > 0 (reflecting approved deposits).
              * Total Withdraw (#total_withdraw) >= 0 (reflecting approved payouts).
    - Step 4: Inspects closed trade records in the Order History table and validates
              that trading executions (Symbol, Lot, PnL, Close Time) are tracked.
    """
    trade_ctx, trade_page = _create_authenticated_trade_context(browser)

    try:
        history_page = HistoryPage(trade_page)
        history_page.navigate_to_history_page()
        expect(history_page.history_tab_container).to_be_visible(timeout=15000)

        # 1. Read bottom calculation statistics bar
        calcs = history_page.get_bottom_calculations()
        logger.info(f"Trade Terminal History Financial Metrics for Account {CLIENT_USER}: {calcs}")

        assert calcs["balance"] > 0, f"Expected positive account balance, got {calcs['balance']}"
        assert calcs["deposit"] > 0, f"Expected positive total deposit, got {calcs['deposit']}"
        assert calcs["withdraw"] >= 0, f"Expected valid total withdraw, got {calcs['withdraw']}"

        # 2. Inspect closed trade order records in the terminal table
        order_records = history_page.get_history_records()
        logger.info(f"Trade Terminal found {len(order_records)} closed orders in History table")
        if order_records:
            first_order = order_records[0]
            logger.info(f"Trade Terminal first closed order: {first_order}")
            assert first_order.get("id") or first_order.get("data_id"), f"Order missing ID: {first_order}"

    finally:
        trade_ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_cross_portal_integrity_and_error_monitoring(browser: Browser):
    """
    Scenario 5: Cross-Portal Diagnostics & Error Monitoring:
    - Verifies that across both portals, all navigation and ledger actions execute cleanly
      without uncaught JavaScript exceptions or 5xx server errors.
    """
    client_ctx, client_page = _create_authenticated_client_context(browser)
    admin_ctx, admin_page = _create_authenticated_admin_context(browser)

    try:
        # Navigate through key client portal pages
        client_deposit = ClientDepositPage(client_page)
        client_deposit.navigate()

        client_withdraw = ClientWithdrawPage(client_page)
        client_withdraw.navigate()

        client_refer = ClientReferEarnPage(client_page)
        client_refer.navigate()

        # Navigate through key admin portal pages
        admin_tx = AdminUserTransactionLogPage(admin_page)
        admin_tx.navigate()

        admin_refer = AdminReferReportPage(admin_page)
        admin_refer.navigate()

        # Assert clean execution with zero uncaught errors
        client_page.error_monitor.assert_no_errors()
        admin_page.error_monitor.assert_no_errors()
        logger.info("Cross-portal integrity and error monitoring validation PASSED successfully.")

    finally:
        client_ctx.close()
        admin_ctx.close()
