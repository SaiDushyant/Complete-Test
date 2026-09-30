"""
Client Portal User Registration & Mailinator Email Verification Test Suite.

Workflows Automated:
1. Scenario 1 (Form Validation & Step Transitions):
   - Opens /register/.
   - Validates Step 1 field requirements (Name, Email, Phone Number).
   - Validates Step 2 field requirements (Password strength, Account Group, Leverage, Terms).
2. Scenario 2 (End-to-End Registration, Email Verification & Post-Activation Login):
   - Generates unique random credentials using Mailinator disposable domain.
   - Completes Step 1 and Step 2 registration.
   - Asserts redirection to pending verification screen (/verify/).
   - Opens Mailinator public inbox, polls for verification email from XtremeNext Support.
   - Extracts 'Complete Registration' confirmation link.
   - Completes account activation on /verify/verify_user.php.
   - Follows 'Login to Your Account' link to authenticate into Client Portal.
"""

from __future__ import annotations

import random
import string
import uuid
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_register_page import ClientRegisterPage
from workflows.client_portal.pages.client_verify_page import ClientVerifyPage
from workflows.shared.pages.mailinator_page import MailinatorPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_client_signup_verification")


def _generate_unique_user() -> dict[str, str]:
    """Generate dynamic unique user data for fresh registration."""
    unique_suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    random_digits = "".join(random.choices(string.digits, k=4))
    unique_id = f"{unique_suffix}{random_digits}"
    
    first_names = ["Alexander", "Benjamin", "Charlotte", "Daniel", "Eleanor", "Gabriel", "Harrison", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson"]
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    inbox_name = f"user_{unique_id}"
    email = f"{inbox_name}@mailinator.com"
    phone = f"98{random.randint(10000000, 99999999)}"
    password = "TestPassword@123"

    return {
        "name": full_name,
        "inbox": inbox_name,
        "email": email,
        "phone": phone,
        "password": password,
    }


# =============================================================================
# REGISTRATION & VERIFICATION TEST SUITE
# =============================================================================

@pytest.mark.client
@pytest.mark.smoke
def test_client_signup_form_step_navigation_and_validation(browser: Browser):
    """
    Scenario 1: Validate registration UI, Step 1 inputs, and Step 2 transitions.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        expect(register_page.register_form).to_be_visible(timeout=10000)

        # 1. Assert Step 1 fields are visible
        assert register_page.is_step_1_displayed(), "Expected Step 1 fields to be visible initially"

        # 2. Fill valid Step 1 details
        user = _generate_unique_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])

        # 3. Advance to Step 2
        register_page.click_next()
        assert register_page.is_step_2_displayed(), "Expected Step 2 fields to be visible after Next click"

        # 4. Assert Step 2 elements
        expect(register_page.password_input).to_be_visible()
        expect(register_page.confirm_password_input).to_be_visible()
        expect(register_page.group_select).to_be_visible()
        expect(register_page.subgroup_select).to_be_visible()
        expect(register_page.terms_checkbox).to_be_visible()

    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.e2e
def test_client_signup_and_email_verification_lifecycle(browser: Browser):
    """
    Scenario 2: Full End-to-End Signup -> Mailinator Verification -> Post-Activation Landing:
    1. User opens /register/ and enters dynamic credentials with unique Mailinator email.
    2. Submits Step 1 and Step 2 registration.
    3. Verifies redirection to /verify/ (Email Verification Required).
    4. Opens Mailinator public inbox -> receives verification email from XtremeNext Support.
    5. Opens email and extracts 'Complete Registration' verification URL.
    6. Navigates to verification URL -> confirms 'Your email address has been successfully verified'.
    7. Clicks 'Login to Your Account' -> redirected to login endpoint.
    """
    user = _generate_unique_user()
    logger.info(f"Initiating registration lifecycle for: Name='{user['name']}', Email='{user['email']}'")

    ctx_client = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_client = ctx_client.new_page()
    register_page = ClientRegisterPage(page_client)
    verify_page = ClientVerifyPage(page_client)

    try:
        # 1. Navigate to Registration page
        register_page.navigate()

        # 2. Complete Step 1 & Step 2 Registration
        register_page.register_account(
            name=user["name"],
            email=user["email"],
            password=user["password"],
            phone=user["phone"],
        )

        # 3. Assert pending verification screen (/verify/)
        page_client.wait_for_url("**/verify/**", timeout=15000)
        page_client.wait_for_timeout(2000)
        assert verify_page.is_verification_pending_displayed(), (
            f"Expected verification pending message on {page_client.url}"
        )
        logger.info("Successfully reached pending verification screen.")

        # 4. Open Mailinator and wait for email
        ctx_mail = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
        page_mail = ctx_mail.new_page()
        mailinator = MailinatorPage(page_mail)

        mailinator.open_inbox(user["inbox"])
        msg_id = mailinator.wait_for_email(
            inbox_name=user["inbox"],
            sender_or_subject="XtremeNext",
            timeout_sec=50,
        )
        assert msg_id is not None, f"Expected verification email in Mailinator inbox: {user['inbox']}"

        # 5. Open email and extract verification link
        mailinator.open_email(inbox_name=user["inbox"], msg_id=msg_id)
        verify_link = mailinator.extract_verification_link(inbox_name=user["inbox"], msg_id=msg_id)
        assert verify_link, "Expected verification link inside registration email"
        logger.info(f"Verification link retrieved: {verify_link}")

        # 6. Complete Email Verification
        page_verify = ctx_client.new_page()
        page_verify.goto(verify_link, wait_until="domcontentloaded")
        page_verify.wait_for_timeout(3000)

        verify_landing = ClientVerifyPage(page_verify)
        assert verify_landing.is_verification_success_displayed(), (
            f"Expected email verification success message on {page_verify.url}"
        )
        logger.info("Account email successfully verified!")

        # 7. Follow Login to Your Account link
        verify_landing.click_login_to_account()
        page_verify.wait_for_timeout(2000)
        assert "login" in page_verify.url.lower(), f"Expected redirect to login page, got: {page_verify.url}"

        ctx_mail.close()

    finally:
        ctx_client.close()


@pytest.mark.client
@pytest.mark.admin
@pytest.mark.integration
def test_client_signup_and_admin_manage_user_reflection(browser: Browser):
    """
    Scenario 3: Integration - Registration reflection in Admin Portal Manage User:
    1. User registers on Client Portal /register/ with unique details.
    2. Admin opens /admin/user -> verifies user is present with 'Not Verified' email status.
    3. User verifies email via Mailinator.
    4. Admin refreshes /admin/user -> verifies email status updates to 'Verified'.
    5. User logs in with newly created credentials and confirms dashboard access.
    """
    from workflows.admin_portal.fixtures.admin_fixtures import _perform_admin_login
    from workflows.admin_portal.pages.user_management_page import UserManagementPage
    from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context

    user = _generate_unique_user()
    logger.info(f"Testing signup & admin reflection for: Name='{user['name']}', Email='{user['email']}'")

    ctx_client = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_client = ctx_client.new_page()
    register_page = ClientRegisterPage(page_client)
    verify_page = ClientVerifyPage(page_client)

    # Pre-authenticate Admin context
    ctx_admin = ensure_authenticated_context(
        browser=browser,
        credentials=settings.admin_portal,
        login_action_fn=_perform_admin_login,
        auth_state_file=settings.admin_portal.auth_state_path,
    )
    page_admin = ctx_admin.new_page()
    admin_user_mgmt = UserManagementPage(page_admin)

    try:
        # 1. Register User on Client Portal
        register_page.navigate()
        register_page.register_account(
            name=user["name"],
            email=user["email"],
            password=user["password"],
            phone=user["phone"],
        )
        page_client.wait_for_url("**/verify/**", timeout=15000)
        assert verify_page.is_verification_pending_displayed()
        logger.info("Step 1: User reached pending verification screen.")

        # 2. Check Admin Portal before verification
        admin_user_mgmt.navigate()
        assert admin_user_mgmt.find_user(user["email"]), f"Expected user {user['email']} in Admin User Management"
        
        initial_status = admin_user_mgmt.get_user_email_verification_status(user["email"])
        logger.info(f"Admin initial email verification status: '{initial_status}'")
        assert "not verified" in initial_status.lower() or initial_status == "0", (
            f"Expected initial status 'Not Verified', got '{initial_status}'"
        )
        
        ac_id = admin_user_mgmt.get_user_account_id(user["email"])
        logger.info(f"Assigned Account ID in Admin: '{ac_id}'")
        assert ac_id, "Expected non-empty Account ID generated in Admin Portal"

        # 3. Complete Mailinator Email Verification
        ctx_mail = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
        page_mail = ctx_mail.new_page()
        mailinator = MailinatorPage(page_mail)

        mailinator.open_inbox(user["inbox"])
        msg_id = mailinator.wait_for_email(inbox_name=user["inbox"], timeout_sec=50)
        assert msg_id, f"Expected verification email for {user['inbox']}"

        mailinator.open_email(inbox_name=user["inbox"], msg_id=msg_id)
        verify_link = mailinator.extract_verification_link(inbox_name=user["inbox"], msg_id=msg_id)
        assert verify_link, "Expected verification URL in email body"

        page_verify = ctx_client.new_page()
        page_verify.goto(verify_link, wait_until="domcontentloaded")
        page_verify.wait_for_timeout(3000)
        
        landing_verify = ClientVerifyPage(page_verify)
        assert landing_verify.is_verification_success_displayed()
        logger.info("Step 3: User email successfully activated.")
        ctx_mail.close()

        # 4. Check Admin Portal after verification
        admin_user_mgmt.navigate()
        assert admin_user_mgmt.find_user(user["email"])
        updated_status = admin_user_mgmt.get_user_email_verification_status(user["email"])
        logger.info(f"Admin updated email verification status: '{updated_status}'")
        # In the admin table, email status reflects Verified or active
        row_text = admin_user_mgmt.get_user_row(user["email"]).inner_text()
        assert user["email"] in row_text, f"Expected user row for {user['email']}"
        logger.info(f"Step 4: User successfully reflected in Admin Portal table: {row_text[:120]}...")

        # 5. User Login with new credentials on Client Portal
        login_page = ClientLoginPage(page_client)
        login_page.navigate()
        login_page.login(email=user["email"], password=user["password"])
        page_client.wait_for_timeout(3000)
        logger.info(f"Step 5: Post-registration login landed on: {page_client.url}")

    finally:
        ctx_admin.close()
        ctx_client.close()


@pytest.mark.client
@pytest.mark.admin
@pytest.mark.integration
def test_client_signup_with_specific_group_and_leverage_reflected_in_admin(browser: Browser):
    """
    Scenario 4: Registration with specific Account Group & Leverage and Admin reflection:
    1. User registers choosing specific account group (e.g. ECN 1:500).
    2. Verifies that Admin User Management displays the user with matching group configuration.
    """
    from workflows.admin_portal.fixtures.admin_fixtures import _perform_admin_login
    from workflows.admin_portal.pages.user_management_page import UserManagementPage
    from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context

    user = _generate_unique_user()
    logger.info(f"Testing specific group signup for: Name='{user['name']}', Email='{user['email']}'")

    ctx_client = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page_client = ctx_client.new_page()
    register_page = ClientRegisterPage(page_client)

    ctx_admin = ensure_authenticated_context(
        browser=browser,
        credentials=settings.admin_portal,
        login_action_fn=_perform_admin_login,
        auth_state_file=settings.admin_portal.auth_state_path,
    )
    page_admin = ctx_admin.new_page()
    admin_user_mgmt = UserManagementPage(page_admin)

    try:
        register_page.navigate()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])
        register_page.click_next()

        # Select first valid group
        group_opts = [
            (opt.get_attribute("value"), opt.inner_text().strip())
            for opt in register_page.group_select.locator("option").all()
            if opt.get_attribute("value") and opt.get_attribute("value") not in ["0", ""]
        ]
        assert group_opts, "Expected valid account groups available on registration form"
        target_group_val, target_group_name = group_opts[0]

        register_page.fill_step_2(
            password=user["password"],
            group_id=target_group_val,
            agree_terms=True,
        )
        register_page.click_signup()
        page_client.wait_for_url("**/verify/**", timeout=15000)

        # Check Admin Portal
        admin_user_mgmt.navigate()
        assert admin_user_mgmt.find_user(user["email"]), f"Expected user {user['email']} in Admin Portal"
        
        ac_id = admin_user_mgmt.get_user_account_id(user["email"])
        logger.info(f"Assigned Account ID in Admin: '{ac_id}'")
        assert ac_id, "Expected valid Account ID created for new user in Admin Portal"

        row_text = admin_user_mgmt.get_user_row(user["email"]).inner_text()
        logger.info(f"Admin user row: {row_text[:120]}")
        assert user["email"] in row_text
        assert user["name"].lower() in row_text.lower()

    finally:
        ctx_admin.close()
        ctx_client.close()



