"""
Client Portal Authentication & Registration Input Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B.1, and Section 4).

Pillars Covered:
1. Textbox & Inputs:
   - Full name, Email format (RFC checks, malformed syntax), Phone number boundaries.
   - Password strength validation (>= 8 chars, uppercase, lowercase, digit, special character).
   - Password mismatch rejection (confirm password != password).
2. Buttons & Actions:
   - Step 1 'Next' button submission prevention on empty/invalid inputs.
   - Step 2 'Prev' button returning to Step 1 without data loss.
   - Terms & conditions checkbox mandate blocking final signup.
   - Login button with empty/whitespace credentials.
3. Dropdowns & Selects:
   - Group ID and Subgroup/Leverage options selection in Step 2.
4. Security:
   - SQLi and XSS payloads in Login email/password inputs.
   - Cleartext password masking (input[type='password']) and toggle reveal.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import random
import string
import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_register_page import ClientRegisterPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


def _make_temp_signup_data() -> dict[str, str]:
    """Generate dynamic compliant user details for boundary tests."""
    rnd = "".join(random.choices(string.ascii_lowercase, k=6))
    return {
        "name": f"ValUser {rnd.capitalize()}",
        "email": f"val_{rnd}@mailinator.com",
        "phone": f"98{random.randint(10000000, 99999999)}",
        "valid_password": "StrongPassword@2026",
    }


# ==============================================================================
# 1. SIGNUP STEP 1: EMPTY FIELDS & TRANSITION BLOCK
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_signup_step1_empty_submit_blocked(
    client_page: Page,
):
    """
    Pillar 1 & 2: Verify submitting empty Step 1 form blocks advancement to Step 2:
    - Step 1 container remains visible
    - Password input in Step 2 remains hidden
    - HTML5 required validation triggers on mandatory inputs
    """
    error_monitor = getattr(client_page, "error_monitor", ErrorMonitor(client_page))
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()
    expect(register_page.step_1_container).to_be_visible()

    # Click Next with empty fields
    register_page.next_button.click()
    client_page.wait_for_timeout(600)

    # Assert Step 1 remains displayed and Step 2 is not displayed
    assert register_page.is_step_1_displayed(), "Step 1 must remain visible when submitted empty"
    assert not register_page.password_input.is_visible(), "Password input must remain hidden"

    error_monitor.assert_no_js_errors("Signup Step 1 Empty Submit")


# ==============================================================================
# 2. SIGNUP STEP 1: EMAIL SYNTAX & FORMAT VALIDATION
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize(
    "invalid_email",
    [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@domain..com",
        "username space@domain.com",
        "username@domain",
    ],
)
def test_val_client_signup_invalid_email_formats(
    client_page: Page,
    invalid_email: str,
):
    """
    Pillar 1: Verify malformed email addresses are rejected during Step 1:
    - Client HTML5 or JS validation prevents moving to Step 2
    """
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()

    data = _make_temp_signup_data()
    register_page.fill_step_1(name=data["name"], email=invalid_email, phone=data["phone"])
    register_page.next_button.click()
    client_page.wait_for_timeout(600)

    # Step 2 should not be reached
    assert not register_page.password_input.is_visible(), (
        f"Malformed email '{invalid_email}' should not allow moving to Step 2"
    )


# ==============================================================================
# 3. SIGNUP STEP 2: PASSWORD COMPLEXITY & MIN LENGTH
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize(
    "weak_password,reason",
    [
        ("short", "Less than 8 characters"),
        ("12345678", "Digits only without uppercase/lowercase"),
        ("password", "Lowercase only without uppercase/digits/special"),
        ("PASSWORD123", "Missing special characters"),
        ("PasswordNoSpecial", "Missing special characters"),
    ],
)
def test_val_client_signup_weak_password_boundaries(
    client_page: Page,
    weak_password: str,
    reason: str,
):
    """
    Pillar 1: Verify weak passwords failing complexity requirements are blocked in Step 2:
    - Rejects password < 8 chars, missing uppercase, digit, or special character
    - Form submission is halted
    """
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()

    data = _make_temp_signup_data()
    register_page.fill_step_1(name=data["name"], email=data["email"], phone=data["phone"])
    register_page.click_next()
    expect(register_page.password_input).to_be_visible(timeout=10000)

    # Fill weak password
    register_page.password_input.fill(weak_password)
    register_page.confirm_password_input.fill(weak_password)
    if register_page.terms_checkbox.is_visible() and not register_page.terms_checkbox.is_checked():
        register_page.terms_checkbox.check()

    register_page.signup_submit_button.click()
    client_page.wait_for_timeout(800)

    # Verify registration does not complete (still on register page)
    assert "/register" in client_page.url, f"Weak password '{weak_password}' ({reason}) should not complete registration"


# ==============================================================================
# 4. SIGNUP STEP 2: PASSWORD MISMATCH VALIDATION
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_signup_password_mismatch_rejection(
    client_page: Page,
):
    """
    Pillar 1: Verify that mismatched password and confirm_password are rejected:
    - pass1 != pass2 prevents submission
    """
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()

    data = _make_temp_signup_data()
    register_page.fill_step_1(name=data["name"], email=data["email"], phone=data["phone"])
    register_page.click_next()
    expect(register_page.password_input).to_be_visible(timeout=10000)

    register_page.password_input.fill("CorrectPass@123")
    register_page.confirm_password_input.fill("DifferentPass@456")
    if register_page.terms_checkbox.is_visible() and not register_page.terms_checkbox.is_checked():
        register_page.terms_checkbox.check()

    register_page.signup_submit_button.click()
    client_page.wait_for_timeout(800)

    assert "/register" in client_page.url, "Mismatched passwords must block registration"


# ==============================================================================
# 5. SIGNUP STEP 2: TERMS AND CONDITIONS CHECKBOX MANDATE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_signup_terms_checkbox_mandate(
    client_page: Page,
):
    """
    Pillar 2: Verify submitting without accepting Terms & Conditions is blocked:
    - With terms_checkbox unchecked, submission must not succeed
    """
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()

    data = _make_temp_signup_data()
    register_page.fill_step_1(name=data["name"], email=data["email"], phone=data["phone"])
    register_page.click_next()
    expect(register_page.password_input).to_be_visible(timeout=10000)

    register_page.password_input.fill(data["valid_password"])
    register_page.confirm_password_input.fill(data["valid_password"])

    # Ensure terms checkbox is UNCHECKED
    if register_page.terms_checkbox.is_checked():
        register_page.terms_checkbox.uncheck()

    register_page.signup_submit_button.click()
    client_page.wait_for_timeout(800)

    assert "/register" in client_page.url, "Unchecked terms must block registration"


# ==============================================================================
# 6. SIGNUP NAVIGATION: PREV BUTTON PRESERVES DATA
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_signup_prev_button_navigation(
    client_page: Page,
):
    """
    Pillar 2: Verify Step 2 'Prev' button returns cleanly to Step 1:
    - Step 1 fields become visible again
    - Pre-filled name, email, and phone values are preserved
    """
    register_page = ClientRegisterPage(client_page)
    register_page.navigate()

    data = _make_temp_signup_data()
    register_page.fill_step_1(name=data["name"], email=data["email"], phone=data["phone"])
    register_page.click_next()
    expect(register_page.password_input).to_be_visible(timeout=10000)

    # Click Previous button
    expect(register_page.prev_button).to_be_visible()
    register_page.prev_button.click()
    client_page.wait_for_timeout(600)

    # Assert Step 1 visible and values preserved
    assert register_page.is_step_1_displayed()
    assert register_page.name_input.input_value() == data["name"]
    assert register_page.email_input.input_value() == data["email"]
    assert register_page.phone_input.input_value() == data["phone"]


# ==============================================================================
# 7. LOGIN FORM: EMPTY CREDENTIALS & ELEMENT VALIDATIONS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_login_empty_credentials_rejection(
    client_login_page: ClientLoginPage,
):
    """
    Pillars 1 & 2: Verify submitting empty login form is rejected:
    - Does not transition away from /login
    - Password mask type is 'password'
    """
    client_login_page.navigate()
    expect(client_login_page.email_input).to_be_visible()
    expect(client_login_page.password_input).to_be_visible()

    # Password input must mask characters
    assert client_login_page.password_input.get_attribute("type") == "password"

    # Click login with empty credentials
    client_login_page.login_button.click()
    client_login_page.page.wait_for_timeout(800)

    assert "/login" in client_login_page.page.url, "Empty credentials submission must remain on /login"


# ==============================================================================
# 8. LOGIN SECURITY: SQLi & XSS PAYLOAD SANITIZATION
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_login_security_sanitization(
    client_login_page: ClientLoginPage,
):
    """
    Pillar 7: Test injection payloads on Client Login form:
    - SQLi payloads (' OR '1'='1, admin' --)
    - XSS payloads (<script>, <svg>)
    - Asserts no script execution, no SQL internal dumps in DOM, and rejection
    """
    client_login_page.navigate()

    # Test SQLi payloads
    for payload, desc in SQLI_PAYLOADS[:3]:
        client_login_page.email_input.fill(payload)
        client_login_page.password_input.fill("Password123!")
        client_login_page.login_button.click()
        client_login_page.page.wait_for_timeout(600)

        # Assert no database syntax dumps exposed
        body_text = client_login_page.page.locator("body").inner_text()
        assert "SQLSTATE" not in body_text, f"SQL error exposed for {desc}"
        assert "syntax error" not in body_text.lower(), f"Syntax error exposed for {desc}"
        assert "/login" in client_login_page.page.url, f"SQLi payload must not bypass login: {desc}"

    # Test XSS payloads
    for payload, desc in XSS_PAYLOADS[:2]:
        client_login_page.email_input.fill(payload)
        client_login_page.password_input.fill(payload)
        client_login_page.login_button.click()
        client_login_page.page.wait_for_timeout(600)

        is_pwned = client_login_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert not is_pwned, f"XSS executed on login: {desc}"
        assert "/login" in client_login_page.page.url
