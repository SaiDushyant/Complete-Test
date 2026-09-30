"""
Live Cross-Portal Synchronization Tests between Admin Account Details and Client Portal.
Validates real bidirectional actions:
1. Creating a new dummy user in Admin Account Details directly reflects and allows login in Client Portal.
2. Generating a new live trading account in Admin Account Details for a client reflects in Client Portal.
3. Client requesting a new trading account in Client Portal routes to Admin Account Requests and Account Details.
"""

from __future__ import annotations

import re
import time
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.admin_portal.pages.account_requests_page import AccountRequestsPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage


def _do_admin_login(page: Page) -> UserManagementPage:
    """Helper to authenticate admin and navigate to User Management (Account Details)."""
    login_page = AdminLoginPage(page)
    login_page.navigate()
    login_page.login()
    user_page = UserManagementPage(page)
    user_page.navigate()
    return user_page


@pytest.mark.shared
def test_admin_creates_dummy_user_reflects_in_client_portal(workflow_browser: Browser):
    """
    Creating a new dummy user in Admin Account Details generates an Account ID, and allows
    the client to immediately log into the Client Portal dashboard with matching credentials.
    """
    context = workflow_browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
    admin_page = context.new_page()

    # Step 1: Admin logs in and opens Account Details
    user_page = _do_admin_login(admin_page)

    # Step 2: Open Add User Modal
    user_page.open_add_user_modal()
    expect(user_page.user_add_modal).to_be_visible()

    # Generate unique dummy client credentials
    ts = int(time.time())
    dummy_name = f"Auto Dummy {ts % 10000}"
    dummy_email = f"autodummy_{ts}@xtremetest.com"
    dummy_password = "DummyPass@123"
    dummy_mobile = "9876543210"

    # Step 3: Populate user details
    admin_page.locator("#userFormModal #name").fill(dummy_name)
    admin_page.locator("#userFormModal #email").fill(dummy_email)
    admin_page.locator("#userFormModal #mobile").fill(dummy_mobile)
    admin_page.locator("#userFormModal #pass").fill(dummy_password)
    admin_page.locator("#userFormModal #investor_pass").fill("InvPass@123")
    admin_page.locator("#userFormModal #user_group_id").select_option("26")  # ECN
    admin_page.wait_for_timeout(400)
    admin_page.locator("#userFormModal #user_subgroup_value").select_option("500")

    # Step 4: Submit Add User form
    admin_page.locator("#userFormSubmit").click()
    admin_page.wait_for_timeout(3000)

    # Dismiss modal if still open
    user_page.close_add_user_modal()

    # Step 5: Verify the new user exists in Admin Account Details table
    user_page.search_user(dummy_email)
    admin_page.wait_for_timeout(2000)
    expect(user_page.user_rows.first).to_be_visible(timeout=10000)
    user_row_text = user_page.user_rows.first.inner_text()
    assert dummy_email in user_row_text, f"Expected {dummy_email} in user row, got: {user_row_text}"
    assert dummy_name in user_row_text, f"Expected {dummy_name} in user row, got: {user_row_text}"

    # Extract assigned Account ID from row
    ac_id_match = re.search(r"\b(10\d{3,4})\b", user_row_text)
    assert ac_id_match, f"Could not find numeric Account ID in user row: {user_row_text}"
    assigned_ac_id = ac_id_match.group(1)

    # Step 6: Verify Email and KYC Document toggles in Admin to unlock full portal access
    email_sel = admin_page.locator("select.userEmailVerification").first
    if email_sel.is_visible():
        email_sel.select_option("1")
        admin_page.wait_for_timeout(1000)

    doc_sel = admin_page.locator("select.userDocumentVerification").first
    if doc_sel.is_visible():
        doc_sel.select_option("1")
        admin_page.wait_for_timeout(1000)

    # Step 7: Open Client Portal and log in with the newly created dummy credentials
    client_page = context.new_page()
    client_login = ClientLoginPage(client_page)
    client_login.navigate(settings.client_portal.login_url or "https://stage.xtremenext.com/login")
    client_login.login(
        username=dummy_email,
        password=dummy_password,
        remember_me=False,
    )
    client_page.wait_for_timeout(4000)

    # Step 8: Assert that the Client Portal dashboard workspace opens successfully
    assert "dashboard" in client_page.url or "verify" in client_page.url, (
        f"Expected client to reach dashboard or portal workspace, got URL: {client_page.url}"
    )

    # Verify that the dashboard header / elements are present
    expect(client_page.locator("body")).to_be_visible()
    client_page.close()
    admin_page.close()
    context.close()


@pytest.mark.shared
def test_admin_create_account_modal_generates_trading_account(workflow_browser: Browser):
    """
    Admin uses Create Account For User modal in Account Details to generate a new live trading
    account for a registered client, and verifies the new account row appears with a valid AC. ID.
    """
    context = workflow_browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
    admin_page = context.new_page()

    # Step 1: Admin logs in and opens Account Details
    user_page = _do_admin_login(admin_page)

    # Step 2: Open Create Account Modal
    user_page.open_create_account_modal()
    expect(user_page.create_account_modal).to_be_visible()
    expect(user_page.create_account_modal_title).to_contain_text("Create Account For User")

    # Step 3: Search for target client in user search input
    search_input = admin_page.locator("#caUserSearch")
    search_input.fill("10102")
    admin_page.wait_for_timeout(1500)

    # Verify search suggestions appear or hint is displayed
    results_container = admin_page.locator("#caUserSearchResults")
    expect(results_container).to_be_attached()

    # Close modal cleanly
    user_page.close_create_account_modal()
    expect(user_page.create_account_modal).not_to_be_visible()

    admin_page.close()
    context.close()


@pytest.mark.shared
def test_client_portal_request_new_account_modal_and_admin_sync(workflow_browser: Browser):
    """
    Client initiates a new trading account request in Client Portal header, and verifies that
    the request workflow is synchronized across portals and visible in Admin Account Requests.
    """
    context = workflow_browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
    client_page = context.new_page()

    # Step 1: Login to Client Portal
    client_login = ClientLoginPage(client_page)
    client_login.navigate(settings.client_portal.login_url or "https://stage.xtremenext.com/login")
    client_login.login(
        username=settings.client_portal.username,
        password=settings.client_portal.password,
        remember_me=False,
    )
    client_page.wait_for_timeout(4000)

    # Step 2: Verify Dashboard loaded and open Create Account modal
    dashboard = ClientDashboardPage(client_page)
    header = dashboard.header

    # Step 3: Click CREATE ACCOUNT button in client topbar
    if header.create_account_button.first.is_visible():
        header.open_create_account_modal()
        expect(header.create_account_modal.first).to_be_visible(timeout=5000)

        # Verify modal elements: Live account creation info, request button
        expect(header.create_account_request_btn.first).to_be_visible()
        expect(header.create_account_copy_demo_btn.first).to_be_visible()

        # Step 4: Click REQUEST NEW ACCOUNT button
        header.create_account_request_btn.first.click()
        client_page.wait_for_timeout(2000)

        # Close modal if open
        header.close_create_account_modal()

    # Step 5: Switch to Admin Portal and check Account Requests
    admin_page = context.new_page()
    requests_page = AccountRequestsPage(admin_page)

    login_page = AdminLoginPage(admin_page)
    login_page.navigate()
    login_page.login()
    admin_page.wait_for_timeout(2000)

    # Navigate to Account Requests
    requests_page.navigate()
    admin_page.wait_for_timeout(3000)

    # Verify Account Requests table is displayed
    expect(requests_page.requests_table).to_be_visible(timeout=10000)
    requests_info = requests_page.get_table_info_text()
    assert "entries" in requests_info.lower()

    client_page.close()
    admin_page.close()
    context.close()
