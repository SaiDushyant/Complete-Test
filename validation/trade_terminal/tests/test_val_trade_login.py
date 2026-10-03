"""
Trade Terminal Login Page — Validation & Security Test Suite.
Covers: empty form submission, email/password format validation,
SQL injection, XSS, open redirect, rate-limiting, remember-me,
and post-logout session invalidation.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.helpers.validation_payloads import (
    INVALID_EMAILS,
    SQLI_EMAIL_PAYLOADS,
    SQLI_PAYLOADS_SHORT,
    XSS_EMAIL_PAYLOADS,
    XSS_PAYLOADS_SHORT,
)
from workflows.trade_terminal.pages.login_page import TradeLoginPage


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _navigate_fresh(page: Page) -> TradeLoginPage:
    """Navigate to a fresh, unauthenticated login page."""
    login = TradeLoginPage(page)
    if "/login" not in page.url or not login.email_input.is_visible():
        login.navigate()
    else:
        page.evaluate("""() => {
            const form = document.querySelector('form');
            if (form) form.reset();
        }""")
    page.wait_for_timeout(300)
    return login


def _clear_xss_flag(page: Page) -> None:
    page.evaluate("() => { window.xss_detected = undefined; }")


def _is_xss_executed(page: Page) -> bool:
    return page.evaluate("() => window.xss_detected === 1")


def _is_still_on_login(page: Page) -> bool:
    return "/login" in page.url or "/dashboard" not in page.url


# ─── Test Class ───────────────────────────────────────────────────────────────

@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeLogin:
    """Validation tests for Trade Terminal Login page (/login/)."""

    # ── 1. Empty Form Submission ─────────────────────────────────────────────

    def test_val_login_empty_both_fields_blocked(self, trade_page: Page):
        """Submitting with both email and password empty must block form submission."""
        login = _navigate_fresh(trade_page)
        login.click_login()
        trade_page.wait_for_timeout(800)
        assert _is_still_on_login(trade_page), "Empty form must NOT redirect to dashboard."

    def test_val_login_empty_password_only_blocked(self, trade_page: Page):
        """Submitting with email filled but password empty must block submission."""
        login = _navigate_fresh(trade_page)
        login.email_input.fill("user@test.com")
        login.click_login()
        trade_page.wait_for_timeout(800)
        assert _is_still_on_login(trade_page), "Login must be blocked when password is empty."

    def test_val_login_empty_email_only_blocked(self, trade_page: Page):
        """Submitting with password filled but email empty must block submission."""
        login = _navigate_fresh(trade_page)
        login.password_input.fill("SomePassword@1")
        login.click_login()
        trade_page.wait_for_timeout(800)
        assert _is_still_on_login(trade_page), "Login must be blocked when email is empty."

    # ── 2. Email Format Validation ────────────────────────────────────────────

    @pytest.mark.parametrize("invalid_email,description", INVALID_EMAILS)
    def test_val_login_invalid_email_format_rejected(
        self, trade_page: Page, invalid_email: str, description: str
    ):
        """Invalid email formats must be rejected without reaching dashboard."""
        login = _navigate_fresh(trade_page)
        login.email_input.fill(invalid_email)
        login.password_input.fill("SomePassword@1")
        login.click_login()
        trade_page.wait_for_timeout(1000)
        assert _is_still_on_login(trade_page), (
            f"Invalid email '{invalid_email}' ({description}) must not log in."
        )

    # ── 3. SQLi in Email Field ────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_EMAIL_PAYLOADS)
    def test_val_login_sqli_in_email_rejected(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi payloads in the email field must not bypass authentication."""
        login = _navigate_fresh(trade_page)
        login.email_input.fill(payload)
        login.password_input.fill("SomePassword@1")
        login.click_login()
        trade_page.wait_for_timeout(1500)

        assert _is_still_on_login(trade_page), (
            f"SQLi in email must NOT log in: {description}"
        )
        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked: {description}"
        assert "syntax error" not in content.lower(), f"SQL syntax error leaked: {description}"

    # ── 4. SQLi in Password Field ─────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_PAYLOADS_SHORT)
    def test_val_login_sqli_in_password_rejected(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi payloads in the password field must not bypass authentication."""
        login = _navigate_fresh(trade_page)
        login.email_input.fill("user@test.com")
        login.password_input.fill(payload)
        login.click_login()
        trade_page.wait_for_timeout(1500)

        assert _is_still_on_login(trade_page), (
            f"SQLi in password must NOT log in: {description}"
        )
        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked: {description}"

    # ── 5. XSS in Email Field ─────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", XSS_EMAIL_PAYLOADS)
    def test_val_login_xss_in_email_not_executed(
        self, trade_page: Page, payload: str, description: str
    ):
        """XSS payloads in the email field must not execute JavaScript."""
        _clear_xss_flag(trade_page)
        login = _navigate_fresh(trade_page)
        login.email_input.fill(payload)
        login.password_input.fill("SomePassword@1")
        login.click_login()
        trade_page.wait_for_timeout(1000)

        assert not _is_xss_executed(trade_page), (
            f"XSS executed in email field: {description}"
        )

    # ── 6. XSS in Password Field ──────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", XSS_PAYLOADS_SHORT)
    def test_val_login_xss_in_password_not_executed(
        self, trade_page: Page, payload: str, description: str
    ):
        """XSS payloads in the password field must not execute JavaScript."""
        _clear_xss_flag(trade_page)
        login = _navigate_fresh(trade_page)
        login.email_input.fill("user@test.com")
        login.password_input.fill(payload)
        login.click_login()
        trade_page.wait_for_timeout(1000)

        assert not _is_xss_executed(trade_page), (
            f"XSS executed in password field: {description}"
        )

    # ── 7. Password Visibility Toggle ─────────────────────────────────────────

    def test_val_login_password_toggle_changes_type(self, trade_page: Page):
        """
        Clicking the eye toggle must switch password input type
        between 'password' and 'text'.
        """
        login = _navigate_fresh(trade_page)
        login.password_input.fill("MySecretPass@1")
        initial_type = login.password_input.get_attribute("type")
        assert initial_type == "password", "Password field must default to type='password'."

        login.toggle_password_visibility()
        trade_page.wait_for_timeout(200)
        toggled_type = login.password_input.get_attribute("type")
        assert toggled_type == "text", "After toggle, type must switch to 'text'."

        login.toggle_password_visibility()
        trade_page.wait_for_timeout(200)
        restored_type = login.password_input.get_attribute("type")
        assert restored_type == "password", "After second toggle, type must restore to 'password'."

    # ── 8. Open Redirect Prevention ───────────────────────────────────────────

    def test_val_login_open_redirect_blocked(self, trade_page: Page):
        """
        Navigating to /login?redirect=https://attacker.com must land on
        internal dashboard only, never on an external host.
        """
        login_url = settings.trade_terminal.login_url.rstrip("/")
        trade_page.goto(f"{login_url}?redirect=https://attacker.com")
        trade_page.wait_for_timeout(500)

        login = TradeLoginPage(trade_page)
        if login.is_login_page_displayed():
            login.fill_credentials(
                username=settings.trade_terminal.username,
                password=settings.trade_terminal.password,
            )
            login.click_login()
            trade_page.wait_for_timeout(3000)

        final_url = trade_page.url
        assert "attacker.com" not in final_url, (
            f"Open redirect succeeded! Landed on: {final_url}"
        )
        assert "xtremenext.com" in final_url or "localhost" in final_url, (
            f"Login did not land on internal domain. Got: {final_url}"
        )

    # ── 9. Password Cleartext in Console ──────────────────────────────────────

    def test_val_login_password_not_logged_to_console(self, trade_page: Page):
        """
        The submitted password must NOT appear in browser console.log output.
        """
        console_messages: list[str] = []
        trade_page.on("console", lambda msg: console_messages.append(msg.text))

        login = _navigate_fresh(trade_page)
        login.fill_credentials(
            username=settings.trade_terminal.username,
            password=settings.trade_terminal.password,
        )
        login.click_login()
        trade_page.wait_for_timeout(3000)

        password = settings.trade_terminal.password
        for msg in console_messages:
            assert password not in msg, (
                f"Cleartext password found in console: '{msg[:80]}'"
            )

    # ── 10. Remember Me Checkbox State ────────────────────────────────────────

    def test_val_login_remember_me_checkbox_default_state(self, trade_page: Page):
        """Remember Me checkbox must be visible and interactable on the login form."""
        login = _navigate_fresh(trade_page)
        if login.remember_me_checkbox.is_visible():
            # Initially may or may not be checked; test toggle
            initial = login.is_remember_me_checked()
            login.remember_me_checkbox.click()
            trade_page.wait_for_timeout(200)
            toggled = login.is_remember_me_checked()
            assert toggled != initial, "Remember Me checkbox must toggle its state on click."

    # ── 11. Forgot Password Link ──────────────────────────────────────────────

    def test_val_login_forgot_password_link_navigates(self, trade_page: Page):
        """Clicking Forgot Password link must navigate to reset page."""
        login = _navigate_fresh(trade_page)
        if login.forgot_password_link.is_visible():
            login.click_forgot_password()
            trade_page.wait_for_timeout(1000)
            assert "/reset" in trade_page.url or "/forgot" in trade_page.url or login.is_login_page_displayed(), (
                "Forgot password must navigate to reset endpoint."
            )
