"""
Client Portal Authentication & Registration Input Validation Test Suite.

Covers:
1. Registration Form Password Mismatch Validation.
2. Registration Terms & Conditions Checkbox Mandatory Enforcement.
3. Cross-Site Scripting (XSS) Sanitization on Registration Input Fields.
4. SQL Injection (SQLi) Authentication Bypass Neutralization on Login Form.
5. Empty and Whitespace Form Submission Rejection.

Reference: docs/VALIDATION_TESTING_SPECIFICATION.md Section 3B & Section 4
"""

from __future__ import annotations

import time
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_register_page import ClientRegisterPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_AUTH_PAYLOADS,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_auth_inputs")


@pytest.mark.client
@pytest.mark.regression
def test_val_registration_password_mismatch(browser: Browser):
    """
    Verify that entering non-matching passwords on Registration Step 2 prevents submission
    and raises validation alert/error.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    reg_page = ClientRegisterPage(page)

    try:
        reg_page.navigate()
        ts = int(time.time())
        reg_page.fill_step_1(name="Alexander Taylor", email=f"val_{ts}@mailinator.com", phone="9876543210")
        reg_page.click_next()

        # Fill mismatched passwords
        page.fill("#pass1", "ValidPassword@123")
        page.fill("#pass2", "MismatchedPassword@999")
        page.check("#inputCheckbox")

        # Submit
        page.click("button.savebut, button[type='submit']:has-text('Sign up')")
        page.wait_for_timeout(2000)

        # Assert registration did NOT succeed and user remains on register page or shows error
        assert "register" in page.url or "verify" not in page.url.lower(), (
            f"Expected registration to be blocked due to password mismatch, but landed on: {page.url}"
        )
        logger.info("Verified password mismatch validation prevents registration submission.")

    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.regression
def test_val_registration_terms_unchecked(browser: Browser):
    """
    Verify that submitting registration with Terms & Conditions checkbox unchecked blocks submission.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    reg_page = ClientRegisterPage(page)

    try:
        reg_page.navigate()
        ts = int(time.time())
        reg_page.fill_step_1(name="Alexander Taylor", email=f"val_{ts}@mailinator.com", phone="9876543210")
        reg_page.click_next()

        page.fill("#pass1", "ValidPassword@123")
        page.fill("#pass2", "ValidPassword@123")

        # Explicitly uncheck terms checkbox
        terms_cb = page.locator("#inputCheckbox")
        if terms_cb.is_checked():
            terms_cb.uncheck()

        page.click("button.savebut, button[type='submit']:has-text('Sign up')")
        page.wait_for_timeout(2000)

        # Must not navigate away to verify screen
        assert "verify" not in page.url.lower(), "Registration proceeded with unchecked Terms checkbox!"
        logger.info("Verified Terms & Conditions mandatory checkbox blocks registration.")

    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS)
def test_val_registration_xss_sanitization(browser: Browser, payload: str, description: str):
    """
    Verify that entering XSS payloads in registration fields does not execute JavaScript.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    reg_page = ClientRegisterPage(page)

    try:
        reg_page.navigate()

        # Inject payload into Full Name input
        page.fill("#name", payload)
        page.fill("#email", f"xss_{int(time.time())}@testcorp.com")
        page.fill("#number", "9876543210")

        # Evaluate if script executed
        xss_executed = page.evaluate("() => window.xss_detected === 1 || window.xss_detected === true")
        assert not xss_executed, f"XSS payload executed in DOM: {description} ({payload})"

        # Click next to test step transition with payload
        page.click("button.next-btn")
        page.wait_for_timeout(1000)

        xss_executed_post = page.evaluate("() => window.xss_detected === 1 || window.xss_detected === true")
        assert not xss_executed_post, f"XSS payload executed after Next click: {description}"
        logger.info(f"Verified XSS payload safely sanitized: {description}")

    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", SQLI_AUTH_PAYLOADS)
def test_val_login_sqli_authentication_bypass(browser: Browser, payload: str, description: str):
    """
    Verify that SQL injection payloads in Login form are neutralized:
    1. Authentication is denied.
    2. No database error signatures (SQLSTATE, syntax error) leaked.
    3. User is not authenticated.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()

        # Inject SQLi payload into username/email and password
        login_page.email_input.fill(payload)
        login_page.password_input.fill(payload)
        login_page.login_button.click()
        page.wait_for_timeout(2500)

        # 1. Assert user was NOT authenticated to dashboard
        assert "dashboard" not in page.url.lower(), f"SQLi authentication bypass occurred with payload: {payload}"

        # 2. Assert no database crash strings dumped to page body
        body_text = page.locator("body").inner_text().lower()
        for error_sig in ["sqlstate", "syntax error", "mysql_", "pdoexception", "unhandled exception"]:
            assert error_sig not in body_text, f"Database error signature '{error_sig}' leaked in response for: {description}"

        logger.info(f"Verified SQLi authentication bypass blocked: {description}")

    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.regression
def test_val_login_empty_and_whitespace_submission(browser: Browser):
    """
    Verify that submitting empty or pure whitespace credentials on the Login form is rejected.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()

        # 1. Empty Submission
        login_page.email_input.fill("")
        login_page.password_input.fill("")
        login_page.login_button.click()
        page.wait_for_timeout(1500)
        assert "dashboard" not in page.url.lower(), "Empty credentials unexpectedly logged in!"

        # 2. Whitespace Submission
        login_page.email_input.fill("   ")
        login_page.password_input.fill("   ")
        login_page.login_button.click()
        page.wait_for_timeout(1500)
        assert "dashboard" not in page.url.lower(), "Whitespace credentials unexpectedly logged in!"

        logger.info("Verified empty and whitespace login submissions correctly rejected.")

    finally:
        ctx.close()
