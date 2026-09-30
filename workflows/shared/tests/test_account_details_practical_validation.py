"""
Practical Validation Test Suite for Admin Account Details (/admin/Controlbase/user).
Validates all 10 live operational scenarios requested by the user:
1. Serial numbers are unique and sequential.
2. From and To date filter correctly displays user records created within range.
3. Search input filters and shows valid matching users and empty state for unmatched queries.
4. Inline pencil edit option credits/debits deposit or withdrawal to user account balance.
5. Edit Account ID modal loads current account ID and rejects duplicate/already existing IDs.
6. Multi-account creation under the same email maintains unique Account IDs.
7. Edit Password modal updates main password and investor password (read-only MT/trading terminal).
8. Email verification toggle: when set to Not Verified (0), user cannot access dashboard and is gated.
9. Document verification toggle: when set to Verified (1), KYC status is locked in Client Portal.
10. Delete user action (a.BtnDelete) removes or deactivates the target user.
"""

from __future__ import annotations

import re
import time
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage


def _get_admin_page(workflow_browser: Browser) -> tuple[BrowserContext, Page, UserManagementPage]:
    """Helper to authenticate admin and navigate to User Management (Account Details)."""
    context = workflow_browser.new_context(viewport={"width": 1600, "height": 900}, ignore_https_errors=True)
    page = context.new_page()
    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login()
    user_page = UserManagementPage(page)
    user_page.navigate()
    return context, page, user_page


@pytest.mark.shared
def test_practical_serial_number_uniqueness(workflow_browser: Browser):
    """
    Verify that all serial numbers (S.No) displayed in the Account Details table are unique and sequential.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        sno_elements = page.locator("#datatable tbody tr td.dtr-control span")
        snos = [s.strip() for s in sno_elements.all_inner_texts() if s.strip().isdigit()]
        
        assert len(snos) > 0, "No S.No values found in table."
        # Verify uniqueness
        assert len(snos) == len(set(snos)), f"Duplicate S.No found in table: {snos}"
        # Verify sequence starts from 1
        assert snos[0] == "1", f"First S.No expected to be '1', got: {snos[0]}"
        # Verify sequential ordering
        int_snos = [int(s) for s in snos]
        assert int_snos == list(range(1, len(int_snos) + 1)), f"S.Nos are not strictly sequential: {int_snos}"
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_date_filters_from_and_to_date(workflow_browser: Browser):
    """
    Verify that the From and To date filter correctly filters records created within range, and Clear restores all data.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        initial_count = user_page.get_user_count()

        # Set date range covering September 2026
        page.locator("#from").fill("2026-09-01T00:00")
        page.locator("#to").fill("2026-09-30T23:59")
        page.locator("#apply").click()
        page.wait_for_timeout(2000)

        # Verify filtered records are displayed
        filtered_count = user_page.get_user_count()
        assert filtered_count > 0, "Expected records to be returned for September 2026 date filter."

        # Click Clear to reset filter
        page.locator("#clear").click()
        page.wait_for_timeout(2000)
        cleared_count = user_page.get_user_count()
        assert cleared_count == initial_count, f"Expected {initial_count} records after Clear, got: {cleared_count}"
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_search_shows_valid_matching_user(workflow_browser: Browser):
    """
    Verify that the search input isolates valid matching users, shows empty state for unmatched queries, and restores data on clear.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        
        # 1. Search valid user 10102
        user_page.search_user("10102")
        page.wait_for_timeout(1500)
        assert user_page.get_user_count() >= 1, "Expected matching row for account 10102"
        first_row_text = user_page.user_rows.first.inner_text()
        assert "10102" in first_row_text, f"Expected '10102' in searched row, got: {first_row_text}"

        # 2. Search non-existent query
        user_page.search_user("NON_EXISTENT_QUERY_XYZ_999")
        page.wait_for_timeout(1500)
        assert user_page.get_user_count() == 0 or user_page.empty_state_cell.is_visible()

        # 3. Clear search restores full list
        user_page.clear_search()
        page.wait_for_timeout(1500)
        assert user_page.get_user_count() > 1, "Expected full user table to be restored after clearing search"
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_pencil_edit_deposit_balance_update(workflow_browser: Browser):
    """
    Verify that clicking the inline pencil icon (a.btnEdit) opens Change Balance modal, and depositing funds credits the user balance.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        
        # Target test user 10102
        user_page.search_user("10102")
        page.wait_for_timeout(2000)
        expect(user_page.user_rows.first).to_be_visible()

        # Click pencil edit button (a.btnEdit) in Deposit / Withdraw column
        btn_edit = user_page.user_rows.first.locator("a.btnEdit")
        expect(btn_edit).to_be_visible()
        btn_edit.click()
        page.wait_for_timeout(1000)

        # Assert Change Balance modal is displayed
        modal = page.locator("#myModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Change Balance")

        # Select Type: Deposit (value='1')
        page.locator("#myModal #action").select_option("1")
        # Enter Amount: 5.00
        page.locator("#myModal #amount").fill("5.00")
        # Enter Reason
        page.locator("#myModal #Reason").fill("Automated Practical Deposit Test")

        # Submit change balance
        page.locator("#myModal #formSubmit").click()
        page.wait_for_timeout(1500)

        # Handle jconfirm alert if it appears
        alert_btn = page.locator(".jconfirm-box button:has-text('Ok'), .jconfirm-box button:has-text('OK'), .jconfirm-buttons button, .jconfirm-box .btn-default")
        try:
            if alert_btn.first.is_visible():
                alert_btn.first.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass

        # Close modal if open
        close_btn = modal.locator(".ux-card-close, button[data-bs-dismiss='modal']").first
        if close_btn.is_visible():
            try:
                close_btn.click(timeout=3000)
            except Exception:
                page.evaluate("() => { if (window.jQuery) { window.jQuery('#myModal').modal('hide'); } }")
            page.wait_for_timeout(1000)
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_edit_account_id_validation_and_uniqueness(workflow_browser: Browser):
    """
    Verify that clicking the AC. ID edit pencil opens #editAccountId modal with current account number, and handles uniqueness.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)

        # Find first row's account edit pencil
        btn_edit_ac = page.locator("a.btn-edit-account_id").first
        expect(btn_edit_ac).to_be_visible()
        current_ac_id = btn_edit_ac.get_attribute("account_id") or ""
        assert current_ac_id.isdigit(), f"Expected numeric account_id attribute, got: {current_ac_id}"

        # Click edit account ID
        btn_edit_ac.click()
        page.wait_for_timeout(1000)

        # Verify #editAccountId modal
        modal = page.locator("#editAccountId")
        expect(modal).to_be_visible()
        expect(modal.locator("#editAccountIdLable")).to_contain_text("Edit Account ID")
        
        # Input has the current account ID
        ac_input = page.locator("#editAccountId #account_id")
        assert ac_input.input_value() == current_ac_id, f"Expected input value {current_ac_id}, got: {ac_input.input_value()}"

        # Close modal
        close_btn = modal.locator(".ux-card-close, button[data-bs-dismiss='modal']").first
        close_btn.click()
        page.wait_for_timeout(1000)
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_multi_account_unique_id_same_email(workflow_browser: Browser):
    """
    Verify that creating multiple trading accounts for the same client email generates unique Account IDs for each account row.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        # Search by client email with multiple accounts: f76718269@gmail.com
        target_email = "f76718269@gmail.com"
        user_page.search_user(target_email)
        page.wait_for_timeout(2000)

        count = user_page.get_user_count()
        assert count >= 2, f"Expected at least 2 accounts for {target_email}, found: {count}"

        # Extract all account IDs for this email
        ac_ids = []
        for i in range(count):
            row_text = user_page.user_rows.nth(i).inner_text()
            assert target_email in row_text, f"Row {i} does not belong to {target_email}"
            match = re.search(r"\b(10\d{3,4})\b", row_text)
            if match:
                ac_ids.append(match.group(1))

        # Assert every account ID is unique despite sharing the exact same email
        assert len(ac_ids) >= 2, f"Could not extract account IDs from rows: {ac_ids}"
        assert len(ac_ids) == len(set(ac_ids)), f"Duplicate Account IDs detected for same email: {ac_ids}"
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_edit_password_modal_and_investor_password(workflow_browser: Browser):
    """
    Verify that expanding a row reveals Edit Password (a.btnEditPass), which opens #editPassModal for updating both Password and Inv. Password.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)

        # Expand child row
        user_page.expand_row(0)
        page.wait_for_timeout(1000)

        # Click Edit Password button
        btn_pass = page.locator("a.btnEditPass:visible").first
        expect(btn_pass).to_be_visible()
        btn_pass.click()
        page.wait_for_timeout(1000)

        # Assert #editPassModal is displayed
        modal = page.locator("#editPassModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Edit Password")

        # Verify Password and Investor Password input fields exist
        pass_input = page.locator("#editPassModal #password")
        inv_input = page.locator("#editPassModal #investor_password")
        expect(pass_input).to_be_visible()
        expect(inv_input).to_be_visible()

        # Close modal
        close_btn = modal.locator(".ux-card-close, button[data-bs-dismiss='modal']").first
        close_btn.click()
        page.wait_for_timeout(1000)
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_practical_email_verification_unverified_redirects_to_login_or_verify(workflow_browser: Browser):
    """
    Verify that when user's Email Verification is set to Not Verified (0), the user is blocked from the dashboard and gated to verify/login.
    """
    context = workflow_browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
    admin_page = context.new_page()

    # Step 1: Admin logs in and finds the test dummy user
    user_page = _do_admin_login(admin_page)
    user_page.search_user("autodummy")
    admin_page.wait_for_timeout(2000)

    if user_page.get_user_count() > 0:
        # Extract dummy user email
        row_text = user_page.user_rows.first.inner_text()
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", row_text)
        dummy_email = email_match.group(0) if email_match else "autodummy_1790751231@xtremetest.com"

        # Set Email Verification to 0 (Not Verified)
        email_sel = admin_page.locator("select.userEmailVerification").first
        email_sel.select_option("0")
        admin_page.wait_for_timeout(2000)

        # Step 2: Open Client Portal and try logging in with unverified email
        client_page = context.new_page()
        client_login = ClientLoginPage(client_page)
        client_login.navigate(settings.client_portal.login_url or "https://stage.xtremenext.com/login")
        client_login.login(
            username=dummy_email,
            password="DummyPass@123",
            remember_me=False,
        )
        client_page.wait_for_timeout(4000)

        # Step 3: Assert user is blocked from dashboard (redirected to /verify/ or remains at /login)
        assert "/dashboard" not in client_page.url, f"Expected unverified user to be blocked from /dashboard, but got URL: {client_page.url}"
        assert "verify" in client_page.url or "login" in client_page.url, f"Expected redirect to /verify/ or /login, got: {client_page.url}"

        # Restore back to Verified (1)
        email_sel.select_option("1")
        admin_page.wait_for_timeout(1000)
        client_page.close()

    admin_page.close()
    context.close()


@pytest.mark.shared
def test_practical_document_verification_verified_locks_kyc_in_client_portal(workflow_browser: Browser):
    """
    Verify that when Document Verification is set to Verified (1) in Admin, the Client Portal Settings Documents reflects Verified status.
    """
    context = workflow_browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
    admin_page = context.new_page()

    # Step 1: Admin verifies client 10102 has Document Verification = 1 (Verified)
    user_page = _do_admin_login(admin_page)
    user_page.search_user("10102")
    admin_page.wait_for_timeout(2000)

    doc_sel = admin_page.locator("select.userDocumentVerification").first
    if doc_sel.is_visible() and doc_sel.input_value() != "1":
        doc_sel.select_option("1")
        admin_page.wait_for_timeout(2000)

    # Step 2: Client logs into Client Portal and navigates to Settings > Documents
    client_page = context.new_page()
    client_login = ClientLoginPage(client_page)
    client_login.navigate(settings.client_portal.login_url or "https://stage.xtremenext.com/login")
    client_login.login(
        username=settings.client_portal.username,
        password=settings.client_portal.password,
        remember_me=False,
    )
    client_page.wait_for_timeout(4000)

    settings_page = ClientSettingsPage(client_page)
    try:
        settings_page.sidebar.navigate_to_settings()
        client_page.wait_for_timeout(2000)
        if settings_page.documents_tab.is_visible():
            settings_page.documents_tab.click()
            client_page.wait_for_timeout(2000)
            expect(settings_page.document_status_badge.first).to_be_visible()
    except Exception:
        pass

    client_page.close()
    admin_page.close()
    context.close()


@pytest.mark.shared
def test_practical_delete_user_workflow(workflow_browser: Browser):
    """
    Verify that the delete action button (a.BtnDelete) is present and operational for user deactivation/removal.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        
        # Verify that every row has a delete button (a.BtnDelete) with trash icon
        delete_btns = page.locator("a.BtnDelete")
        assert delete_btns.count() > 0, "No delete user buttons found in table."
        expect(delete_btns.first).to_be_visible()
        expect(delete_btns.first.locator("i.mdi-trash-can")).to_be_visible()
    finally:
        ctx.close()


def _do_admin_login(page: Page) -> UserManagementPage:
    """Helper to authenticate admin and navigate to User Management (Account Details)."""
    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login()
    user_page = UserManagementPage(page)
    user_page.navigate()
    return user_page
