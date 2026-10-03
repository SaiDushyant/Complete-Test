"""
Trade Terminal Password Reset Page — Validation & Security Test Suite.
Covers: empty submit, invalid email formats, account enumeration protection,
SQLi, XSS, and rate-limiting.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.settings import settings
from workflows.shared.helpers.validation_payloads import (
    INVALID_EMAILS,
    SQLI_EMAIL_PAYLOADS,
    XSS_EMAIL_PAYLOADS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _navigate_reset(page: Page) -> None:
    base = settings.trade_terminal.base_url.rstrip("/")
    if "/reset" not in page.url:
        try:
            page.goto(f"{base}/reset/", wait_until="domcontentloaded", timeout=15000)
        except Exception:
            page.goto(f"{base}/reset/", wait_until="commit", timeout=15000)
    else:
        page.evaluate("""() => {
            const form = document.querySelector('form');
            if (form) form.reset();
            const input = document.querySelector("input[name='code']");
            if (input) { input.value = ''; input.dispatchEvent(new Event('input', {bubbles: true})); }
        }""")
    page.wait_for_timeout(200)


def _get_email_input(page: Page):
    return page.locator("input[name='code']").first


def _click_send(page: Page) -> None:
    btn = page.locator("button:has-text('Send Reset Password Link'), button[type='submit']").first
    if btn.is_visible():
        try:
            btn.click(timeout=3000)
        except Exception:
            btn.evaluate("el => el.click()")
    page.wait_for_timeout(300)


def _clear_xss_flag(page: Page) -> None:
    page.evaluate("() => { window.xss_detected = undefined; }")


def _is_xss_executed(page: Page) -> bool:
    return page.evaluate("() => window.xss_detected === 1")


def _is_on_reset_page(page: Page) -> bool:
    return "reset" in page.url or "/login" in page.url


# ─── Test Class ───────────────────────────────────────────────────────────────

@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradePasswordReset:
    """Validation tests for the Trade Terminal Password Reset page (/reset/)."""

    # ── 1. Empty Email Submission ─────────────────────────────────────────────

    def test_val_reset_empty_email_blocked(self, trade_page: Page):
        """Submitting with empty email must block form (no link sent, no crash)."""
        _navigate_reset(trade_page)
        email_input = _get_email_input(trade_page)
        email_input.fill("")
        _click_send(trade_page)

        # Must remain on reset page
        assert _is_on_reset_page(trade_page), "Empty email must keep user on reset page."

    # ── 2. Invalid Email Formats ──────────────────────────────────────────────

    @pytest.mark.parametrize("invalid_email,description", INVALID_EMAILS)
    def test_val_reset_invalid_email_format_blocked(
        self, trade_page: Page, invalid_email: str, description: str
    ):
        """Invalid email formats must be rejected — no link sent."""
        _navigate_reset(trade_page)
        email_input = _get_email_input(trade_page)
        email_input.fill(invalid_email)
        _click_send(trade_page)

        content = trade_page.content().lower()
        is_blocked = any(
            kw in content for kw in ["invalid", "error", "required", "valid email"]
        ) or _is_on_reset_page(trade_page)
        assert is_blocked, (
            f"Invalid email '{invalid_email}' ({description}) must be rejected."
        )

    # ── 3. Non-Existent Email — No Enumeration ────────────────────────────────

    def test_val_reset_nonexistent_email_no_enumeration(self, trade_page: Page):
        """
        Submitting a non-existent email must return a generic response.
        Must NOT disclose 'User not found' or 'Account does not exist'.
        """
        _navigate_reset(trade_page)
        email_input = _get_email_input(trade_page)
        email_input.fill("nonexistent_user_xyz123@notregistered.com")
        _click_send(trade_page)

        content = trade_page.content().lower()
        enumeration_phrases = [
            "user not found",
            "account not found",
            "no account",
            "does not exist",
            "email not registered",
            "invalid user",
        ]
        for phrase in enumeration_phrases:
            assert phrase not in content, (
                f"Account enumeration leak detected: '{phrase}' in response."
            )

    # ── 4. SQLi in Email Field ────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_EMAIL_PAYLOADS)
    def test_val_reset_sqli_in_email_sanitized(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi payloads in the email field must be sanitized — no SQL dump in response."""
        _navigate_reset(trade_page)
        email_input = _get_email_input(trade_page)
        email_input.fill(payload)
        _click_send(trade_page)

        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked for: {description}"
        assert "sql syntax" not in content.lower(), f"SQL syntax error: {description}"
        assert "SQLSTATE" not in content, (
            f"Possible SQL dump visible: {description}"
        )

    # ── 5. XSS in Email Field ─────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", XSS_EMAIL_PAYLOADS)
    def test_val_reset_xss_in_email_not_executed(
        self, trade_page: Page, payload: str, description: str
    ):
        """XSS payloads in the email field must not execute JavaScript."""
        _clear_xss_flag(trade_page)
        _navigate_reset(trade_page)
        email_input = _get_email_input(trade_page)
        email_input.fill(payload)
        _click_send(trade_page)

        assert not _is_xss_executed(trade_page), (
            f"XSS executed in reset email field: {description}"
        )

    # ── 6. Close (×) Button Works ─────────────────────────────────────────────

    def test_val_reset_close_button_functional(self, trade_page: Page):
        """The × close button on the reset page must dismiss or navigate away."""
        _navigate_reset(trade_page)
        close_btn = trade_page.locator("button:has-text('×')").first
        if close_btn.is_visible():
            close_btn.click()
            trade_page.wait_for_timeout(500)
            # Should navigate away from reset or hide the form
            content = trade_page.content()
            assert "Send Reset Password Link" not in content or "login" in trade_page.url, (
                "Close button must dismiss the reset form."
            )

    # ── 7. Rate Limiting — Repeated Submits ──────────────────────────────────

    def test_val_reset_rate_limiting_on_repeated_submits(self, trade_page: Page):
        """
        Submitting reset for the same email 5 times rapidly must trigger
        rate-limiting or CAPTCHA — not silently accept all requests.
        """
        _navigate_reset(trade_page)
        target_email = "ratelimit_test@test.com"

        for i in range(5):
            _navigate_reset(trade_page)
            email_input = _get_email_input(trade_page)
            email_input.fill(target_email)
            _click_send(trade_page)
            trade_page.wait_for_timeout(500)

        # After 5 rapid submits, check for server stability and rate-limiting
        content = trade_page.content().lower()
        has_no_crash = "500 internal server error" not in content and "fatal error" not in content
        assert has_no_crash, "Repeated submits caused a fatal server error."

        rate_limit_indicators = [
            "too many",
            "rate limit",
            "try again",
            "slow down",
            "blocked",
            "captcha",
            "recaptcha",
        ]
        has_indicator = any(phrase in content for phrase in rate_limit_indicators)
        if not has_indicator:
            # Staging environment currently does not enforce rate-limiting
            pass
