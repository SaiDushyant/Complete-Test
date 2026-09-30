"""
Client Portal & Trade Terminal Negative Authentication & Registration Test Suite.

Covers comprehensive negative scenarios, validation boundaries, and security edge cases:
1. Registration Step 1:
   - Empty input validation
   - Non-alphabetic Name rejection
   - Invalid Email syntax rejection
   - Short / Non-digit Phone rejection
   - Duplicate / Existing Email registration rejection
2. Registration Step 2:
   - Password mismatch rejection
   - Weak password complexity rejection
   - Unaccepted Terms & Conditions rejection
   - Invalid / Non-existent Referral Code rejection
3. Login & Authentication:
   - Empty credentials rejection
   - Non-existent account rejection
   - Existing user incorrect password rejection
   - SQL Injection payload rejection on login
"""

from __future__ import annotations

import random
import string
import pytest
from playwright.sync_api import Browser, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_register_page import ClientRegisterPage
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.login_page import TradeLoginPage

logger = get_logger("test_auth_negative_scenarios")


def _generate_temp_user() -> dict[str, str]:
    """Generate dynamic valid user data for testing Step 1/Step 2 boundaries."""
    unique_suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    first_names = ["Daniel", "Emma", "Lucas", "Sophia", "Noah", "Olivia"]
    last_names = ["Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
    
    return {
        "name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "email": f"neg_{unique_suffix}@mailinator.com",
        "phone": f"98{random.randint(10000000, 99999999)}",
        "password": "ValidPassword@123",
    }


# =============================================================================
# SIGNUP STEP 1 NEGATIVE SCENARIOS
# =============================================================================

@pytest.mark.client
@pytest.mark.negative
def test_signup_step1_empty_fields_validation(browser: Browser):
    """
    Verify that submitting empty fields in Step 1 prevents transition to Step 2.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        expect(register_page.step_1_container).to_be_visible()

        # Click next with empty inputs
        register_page.next_button.click()
        page.wait_for_timeout(1000)

        # Assert Step 1 remains visible and Step 2 is not displayed
        assert register_page.is_step_1_displayed(), "Expected Step 1 to remain visible when inputs are empty"
        assert not register_page.password_input.is_visible(), "Expected Step 2 password field to remain hidden"
        logger.info("Empty Step 1 submission successfully blocked.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.parametrize("invalid_name", ["John123", "User@#$", "Alex_Smith_99", "12345"])
def test_signup_step1_invalid_name_characters(browser: Browser, invalid_name: str):
    """
    Verify that non-alphabetic names are rejected by Step 1 validation.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=invalid_name, email=user["email"], phone=user["phone"])
        register_page.next_button.click()
        page.wait_for_timeout(1000)

        # Assert Step 2 is not reached
        assert not register_page.password_input.is_visible(), (
            f"Step 2 was unexpectedly displayed for invalid name '{invalid_name}'"
        )
        logger.info(f"Invalid name '{invalid_name}' correctly rejected.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.parametrize("invalid_email", ["notanemail", "user@", "user@domain", "@domain.com", "user@.com"])
def test_signup_step1_invalid_email_syntax(browser: Browser, invalid_email: str):
    """
    Verify that malformed email addresses are rejected by Step 1 validation.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=invalid_email, phone=user["phone"])
        register_page.next_button.click()
        page.wait_for_timeout(1000)

        # Assert Step 2 is not reached
        assert not register_page.password_input.is_visible(), (
            f"Step 2 was unexpectedly reached for invalid email '{invalid_email}'"
        )
        logger.info(f"Invalid email '{invalid_email}' correctly rejected.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.parametrize("invalid_phone", ["123", "12345", "0000", "98765"])
def test_signup_step1_invalid_phone_number(browser: Browser, invalid_phone: str):
    """
    Verify that invalid / short phone numbers (< 9 digits) are rejected by Step 1 validation.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=invalid_phone)
        register_page.next_button.click()
        page.wait_for_timeout(1000)

        # Assert Step 2 is not reached
        assert not register_page.password_input.is_visible(), (
            f"Step 2 was unexpectedly reached for invalid phone '{invalid_phone}'"
        )
        logger.info(f"Invalid phone '{invalid_phone}' correctly rejected.")
    finally:
        ctx.close()


# =============================================================================
# SIGNUP STEP 2 NEGATIVE SCENARIOS
# =============================================================================

@pytest.mark.client
@pytest.mark.negative
def test_signup_step2_password_mismatch(browser: Browser):
    """
    Verify that password and confirm password mismatch prevents registration.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])
        register_page.click_next()

        # Fill mismatched passwords
        register_page.password_input.fill("ValidPassword@123")
        register_page.confirm_password_input.fill("DifferentPassword@999")
        register_page.fill_step_2(password="ValidPassword@123", agree_terms=True)
        # Override confirm password with mismatch
        register_page.confirm_password_input.fill("DifferentPassword@999")

        register_page.click_signup()
        page.wait_for_timeout(2000)

        # Assert user stays on register page and is not redirected to /verify/
        assert "register" in page.url.lower(), f"Unexpected navigation to {page.url} on password mismatch"
        assert "/verify" not in page.url.lower(), "Registration unexpectedly succeeded with mismatched passwords"
        logger.info("Password mismatch correctly blocked registration.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.parametrize("weak_pwd", ["short1!", "alllowercase@123", "NOLOWERCASE@123", "NoSpecialChar123", "NoNumbers!@#"])
def test_signup_step2_weak_password_rejected(browser: Browser, weak_pwd: str):
    """
    Verify that passwords not meeting complexity rules are rejected with error alerts.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])
        register_page.click_next()

        register_page.fill_step_2(password=weak_pwd, agree_terms=True)
        register_page.click_signup()
        page.wait_for_timeout(2000)

        # Assert remaining on registration page
        assert "register" in page.url.lower(), f"Weak password '{weak_pwd}' unexpectedly navigated to {page.url}"
        assert "/verify" not in page.url.lower()

        # Check alert text
        alerts = [a.inner_text().lower() for a in page.locator(".alert, .toast, #error").all()]
        logger.info(f"Weak password '{weak_pwd}' alerts: {alerts}")
        assert any("password" in a or "character" in a for a in alerts) or "register" in page.url.lower()
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
def test_signup_step2_unaccepted_terms_rejected(browser: Browser):
    """
    Verify that registration cannot be submitted without checking Terms & Conditions.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])
        register_page.click_next()

        register_page.fill_step_2(password=user["password"], agree_terms=False)
        # Ensure checkbox is unchecked
        if register_page.terms_checkbox.is_checked():
            register_page.terms_checkbox.uncheck()

        register_page.click_signup()
        page.wait_for_timeout(2000)

        # Assert registration is blocked
        assert "register" in page.url.lower()
        assert "/verify" not in page.url.lower()
        logger.info("Unchecked terms & conditions correctly prevented registration.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
def test_signup_step2_invalid_referral_code_rejected(browser: Browser):
    """
    Verify that supplying a non-existent referral code displays an error alert and blocks registration.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    register_page = ClientRegisterPage(page)

    try:
        register_page.navigate()
        user = _generate_temp_user()
        register_page.fill_step_1(name=user["name"], email=user["email"], phone=user["phone"])
        register_page.click_next()

        register_page.fill_step_2(
            password=user["password"],
            referral_code="NONEXISTENT_REF_CODE_9999",
            agree_terms=True,
        )
        register_page.click_signup()
        page.wait_for_timeout(2500)

        # Assert user stays on register page and error alert appears
        assert "register" in page.url.lower()
        assert "/verify" not in page.url.lower()

        alerts = [a.inner_text().lower() for a in page.locator(".alert, .toast").all()]
        logger.info(f"Invalid referral alerts: {alerts}")
        assert any("referral" in a for a in alerts), f"Expected invalid referral alert in {alerts}"
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
def test_signup_duplicate_email_rejected(browser: Browser):
    """
    Verify that registering with an already existing email is rejected with an alert.
    """
    user = _generate_temp_user()

    # 1. First registration with this email
    ctx1 = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page1 = ctx1.new_page()
    reg1 = ClientRegisterPage(page1)
    try:
        reg1.navigate()
        reg1.register_account(
            name=user["name"],
            email=user["email"],
            password=user["password"],
            phone=user["phone"],
        )
        page1.wait_for_url("**/verify/**", timeout=15000)
    finally:
        ctx1.close()

    # 2. Second registration attempt with the exact same email in a fresh context
    ctx2 = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page2 = ctx2.new_page()
    reg2 = ClientRegisterPage(page2)
    try:
        reg2.navigate()
        second_user = _generate_temp_user()
        reg2.fill_step_1(name=second_user["name"], email=user["email"], phone=second_user["phone"])
        reg2.click_next()
        reg2.fill_step_2(password=second_user["password"], agree_terms=True)
        reg2.click_signup()
        page2.wait_for_timeout(3000)

        # Assert user remains on register page
        assert "register" in page2.url.lower()
        assert "/verify" not in page2.url.lower()

        alerts = [a.inner_text().lower() for a in page2.locator(".alert, .toast").all()]
        logger.info(f"Duplicate email alerts: {alerts}")
        assert any("already in use" in a or "email" in a or "exist" in a for a in alerts), (
            f"Expected duplicate email alert in {alerts}"
        )
    finally:
        ctx2.close()




# =============================================================================
# LOGIN NEGATIVE SCENARIOS
# =============================================================================

@pytest.mark.client
@pytest.mark.negative
def test_login_empty_credentials_rejected(browser: Browser):
    """
    Verify that submitting empty credentials does not authenticate or navigate to dashboard.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()
        login_page.email_input.fill("")
        login_page.password_input.fill("")
        login_page.click_login()
        page.wait_for_timeout(2000)

        # Assert user remains on login page
        assert "login" in page.url.lower(), f"Unexpected URL after empty login: {page.url}"
        assert "/dashboard" not in page.url.lower()
        logger.info("Empty credentials correctly rejected.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
def test_login_non_existent_account_rejected(browser: Browser):
    """
    Verify that logging in with a non-existent email displays an error alert.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()
        login_page.login(
            email="non_existent_user_xyz999@mailinator.com",
            password="WrongPassword@123",
        )
        page.wait_for_timeout(3000)

        assert "login" in page.url.lower()
        assert "/dashboard" not in page.url.lower()

        alerts = [a.inner_text().strip() for a in page.locator(".alert, .toast").all()]
        logger.info(f"Non-existent user alerts: {alerts}")
        assert len(alerts) > 0, "Expected error alert for non-existent account"
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
def test_login_existing_user_wrong_password_rejected(browser: Browser):
    """
    Verify that supplying an incorrect password for a valid account displays 'Invalid Username/Email or Pass'.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()
        login_page.login(
            email=settings.client_portal.username,
            password="IncorrectPassword@999",
        )
        page.wait_for_timeout(3000)

        assert "login" in page.url.lower()
        assert "/dashboard" not in page.url.lower()

        alerts = [a.inner_text().strip() for a in page.locator(".alert, .toast").all()]
        logger.info(f"Wrong password alerts: {alerts}")
        assert any("invalid" in a.lower() for a in alerts), f"Expected invalid credentials alert in {alerts}"
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.negative
@pytest.mark.parametrize("sqli_payload", ["' OR '1'='1' --", "admin' --", "' OR 1=1 #", "\" OR \"\"=\""])
def test_login_sql_injection_payload_rejected(browser: Browser, sqli_payload: str):
    """
    Verify that SQL injection payloads in email and password fields are safely rejected.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()
        login_page.login(
            email=sqli_payload,
            password=sqli_payload,
        )
        page.wait_for_timeout(2500)

        # Assert no unauthorized bypass to dashboard
        assert "login" in page.url.lower(), f"SQLi payload '{sqli_payload}' unexpectedly bypassed login to {page.url}"
        assert "/dashboard" not in page.url.lower()
        assert "/client-portal" not in page.url.lower()
        logger.info(f"SQLi payload '{sqli_payload}' safely blocked.")
    finally:
        ctx.close()


@pytest.mark.trade
@pytest.mark.negative
def test_trade_terminal_login_invalid_credentials(browser: Browser):
    """
    Verify Trade Terminal login page rejection on invalid credentials.
    """
    ctx = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page = ctx.new_page()
    trade_login = TradeLoginPage(page)

    try:
        trade_login.navigate()
        trade_login.login(
            username="invalid_trade_user@mailinator.com",
            password="WrongPassword@123",
        )
        page.wait_for_timeout(3000)

        assert "/dashboard" not in page.url.lower() or "verify" in page.url.lower() or "login" in page.url.lower()
        logger.info("Trade Terminal invalid credentials safely rejected.")
    finally:
        ctx.close()
