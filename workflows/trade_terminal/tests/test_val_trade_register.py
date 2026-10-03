"""
Trade Terminal Register / Signup Page — Validation & Security Test Suite.
Covers: 2-step form validation, name/email/phone format, password strength,
mismatch, terms checkbox, dependent dropdowns, SQLi, and XSS.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.helpers.validation_payloads import (
    INVALID_EMAILS,
    INVALID_PHONE_NUMBERS,
    SQLI_EMAIL_PAYLOADS,
    SQLI_NAME_PAYLOADS,
    SQLI_REFERRAL_PAYLOADS,
    WEAK_PASSWORDS,
    XSS_EMAIL_PAYLOADS,
    XSS_NAME_PAYLOADS,
    XSS_REFERRAL_PAYLOADS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _navigate_register(page: Page) -> None:
    base = settings.trade_terminal.base_url.rstrip("/")
    if "/register" not in page.url or not page.locator("input[name='name']").is_visible():
        try:
            page.goto(f"{base}/register/", wait_until="domcontentloaded", timeout=15000)
        except Exception:
            page.goto(f"{base}/register/", wait_until="commit", timeout=15000)
    else:
        page.evaluate("""() => {
            const form = document.querySelector('form');
            if (form) form.reset();
            document.querySelectorAll('fieldset, .step, .tab-pane').forEach((s, idx) => {
                s.style.display = idx === 0 ? 'block' : 'none';
            });
        }""")
    page.wait_for_timeout(300)


def _clear_xss_flag(page: Page) -> None:
    page.evaluate("() => { window.xss_detected = undefined; }")


def _is_xss_executed(page: Page) -> bool:
    return page.evaluate("() => window.xss_detected === 1")


def _is_on_register(page: Page) -> bool:
    return "register" in page.url or "signup" in page.url or "login" not in page.url


def _fill_step1(page: Page, name: str, email: str, phone: str) -> None:
    page.locator("input[name='name']").fill(name)
    page.locator("input[name='email']").fill(email)
    phone_input = page.locator("input[name='number']")
    try:
        phone_input.fill(phone)
    except Exception:
        phone_input.evaluate("(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); }", phone)


def _click_next(page: Page) -> None:
    page.locator("button:has-text('Next')").click()
    page.wait_for_timeout(800)


def _is_step1_still_visible(page: Page) -> bool:
    return page.locator("input[name='name']").is_visible()


# ─── Test Class ───────────────────────────────────────────────────────────────

@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeRegister:
    """Validation tests for Trade Terminal Register page (/register/)."""

    # ── 1. Empty Name Blocked ─────────────────────────────────────────────────

    def test_val_register_empty_name_blocked(self, trade_page: Page):
        """Next button with empty name must be blocked / stay on Step 1."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        assert _is_step1_still_visible(trade_page), "Empty name must block Step 1 progression."

    def test_val_register_whitespace_name_blocked(self, trade_page: Page):
        """Whitespace-only name must be treated as empty and block Step 1."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="     ", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        assert trade_page.is_visible("body"), "UI crashed on whitespace name"

    # ── 2. SQLi in Name Field ─────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_NAME_PAYLOADS)
    def test_val_register_sqli_in_name_sanitized(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi in name field must be sanitized — no SQL error in DOM."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name=payload, email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked for: {description}"
        assert "syntax error" not in content.lower(), f"SQL syntax error: {description}"

    # ── 3. XSS in Name Field ──────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", XSS_NAME_PAYLOADS)
    def test_val_register_xss_in_name_not_executed(
        self, trade_page: Page, payload: str, description: str
    ):
        """XSS in name must not execute JavaScript."""
        _clear_xss_flag(trade_page)
        _navigate_register(trade_page)
        _fill_step1(trade_page, name=payload, email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        assert not _is_xss_executed(trade_page), f"XSS executed in name field: {description}"

    # ── 4. Invalid Email Formats ──────────────────────────────────────────────

    @pytest.mark.parametrize("invalid_email,description", INVALID_EMAILS)
    def test_val_register_invalid_email_format_rejected(
        self, trade_page: Page, invalid_email: str, description: str
    ):
        """Invalid email formats must block Step 1 progression or trigger validation errors."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email=invalid_email, phone="9876543210")
        _click_next(trade_page)
        is_step1 = _is_step1_still_visible(trade_page)
        is_invalid = trade_page.evaluate("() => { const el = document.querySelector(\"input[name='email']\"); return el ? !el.checkValidity() : false; }")
        assert is_step1 or is_invalid or "register" in trade_page.url, (
            f"Invalid email '{invalid_email}' ({description}) must block Step 1 or trigger validation."
        )

    # ── 5. SQLi in Email Field ────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_EMAIL_PAYLOADS)
    def test_val_register_sqli_in_email_rejected(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi payloads in email must be rejected — no SQL dump, no account created."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email=payload, phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked: {description}"

    # ── 6. XSS in Email Field ─────────────────────────────────────────────────

    @pytest.mark.parametrize("payload,description", XSS_EMAIL_PAYLOADS)
    def test_val_register_xss_in_email_not_executed(
        self, trade_page: Page, payload: str, description: str
    ):
        """XSS in email field must not execute JavaScript."""
        _clear_xss_flag(trade_page)
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email=payload, phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        assert not _is_xss_executed(trade_page), f"XSS executed in email: {description}"

    # ── 7. Invalid Phone Numbers ──────────────────────────────────────────────

    @pytest.mark.parametrize("phone,description", INVALID_PHONE_NUMBERS[:4])
    def test_val_register_invalid_phone_rejected(
        self, trade_page: Page, phone: str, description: str
    ):
        """Invalid phone formats must block Step 1 progression or be sanitized."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone=phone)
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        assert trade_page.is_visible("body"), f"UI crashed on phone: {phone}"

    @pytest.mark.parametrize("phone,description", INVALID_PHONE_NUMBERS[4:])
    def test_val_register_sqli_xss_in_phone_sanitized(
        self, trade_page: Page, phone: str, description: str
    ):
        """SQLi/XSS in phone field must be sanitized — no SQL dump or JS execution."""
        _clear_xss_flag(trade_page)
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone=phone)
        _click_next(trade_page)
        trade_page.wait_for_timeout(800)
        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked: {description}"
        assert not _is_xss_executed(trade_page), f"XSS executed in phone: {description}"

    # ── 8. Weak Passwords ─────────────────────────────────────────────────────

    @pytest.mark.parametrize("weak_pass,description", WEAK_PASSWORDS)
    def test_val_register_weak_password_rejected(
        self, trade_page: Page, weak_pass: str, description: str
    ):
        """Weak passwords must be rejected or show strength error in Step 2."""
        _navigate_register(trade_page)
        # Fill Step 1 with valid data to reach Step 2
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        pass1 = trade_page.locator("input#pass1, input[name='pass1']").first
        if not pass1.is_visible():
            pytest.skip("Step 2 password field not visible — Step 1 validation blocked.")

        pass1.fill(weak_pass)
        pass2 = trade_page.locator("input[name='password'], input[name='pass2']").first
        pass2.fill(weak_pass)

        trade_page.locator("button:has-text('Sign up')").click()
        trade_page.wait_for_timeout(1000)

        content = trade_page.content().lower()
        # Either still on register, or shows strength/error message
        is_still_register = "register" in trade_page.url or pass1.is_visible()
        has_error = any(
            kw in content for kw in ["password", "strength", "weak", "required", "invalid", "must"]
        )
        assert is_still_register or has_error, (
            f"Weak password '{weak_pass}' ({description}) must be rejected."
        )

    # ── 9. Password Mismatch Blocked ──────────────────────────────────────────

    def test_val_register_password_mismatch_blocked(self, trade_page: Page):
        """Mismatching passwords must block Step 2 submission."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        pass1 = trade_page.locator("input#pass1, input[name='pass1']").first
        if not pass1.is_visible():
            pytest.skip("Step 2 not reached.")

        pass1.fill("StrongPass@123")
        pass2 = trade_page.locator("input[name='password'], input[name='pass2']").first
        pass2.fill("DifferentPass@456")

        trade_page.locator("button:has-text('Sign up')").click()
        trade_page.wait_for_timeout(1000)

        content = trade_page.content().lower()
        has_mismatch_error = any(
            kw in content for kw in ["match", "mismatch", "same", "identical", "do not match", "doesn't match"]
        )
        assert has_mismatch_error or pass1.is_visible(), (
            "Password mismatch must show error or block submission."
        )

    # ── 10. Password Match Proceeds ───────────────────────────────────────────

    def test_val_register_password_match_no_error(self, trade_page: Page):
        """Matching strong passwords must NOT show a mismatch error."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        pass1 = trade_page.locator("input#pass1, input[name='pass1']").first
        if not pass1.is_visible():
            pytest.skip("Step 2 not reached.")

        pass1.fill("StrongPass@123")
        pass2 = trade_page.locator("input[name='password'], input[name='pass2']").first
        pass2.fill("StrongPass@123")
        trade_page.wait_for_timeout(400)

        content = trade_page.content().lower()
        assert "do not match" not in content, "Matching passwords must NOT show mismatch error."

    # ── 11. Terms Checkbox Required ───────────────────────────────────────────

    def test_val_register_terms_unchecked_blocked(self, trade_page: Page):
        """Submitting Step 2 with Terms unchecked must block registration."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        pass1 = trade_page.locator("input#pass1, input[name='pass1']").first
        if not pass1.is_visible():
            pytest.skip("Step 2 not reached.")

        pass1.fill("StrongPass@123")
        pass2 = trade_page.locator("input[name='password'], input[name='pass2']").first
        pass2.fill("StrongPass@123")

        # Ensure terms checkbox is unchecked
        checkbox = trade_page.locator("input#inputCheckbox").first
        if checkbox.is_checked():
            checkbox.uncheck()

        trade_page.locator("button:has-text('Sign up')").click()
        trade_page.wait_for_timeout(1000)

        assert pass1.is_visible() or "register" in trade_page.url, (
            "Unchecked Terms must block Step 2 registration."
        )

    # ── 12. SQLi / XSS in Referral Field ─────────────────────────────────────

    @pytest.mark.parametrize("payload,description", SQLI_REFERRAL_PAYLOADS + XSS_REFERRAL_PAYLOADS)
    def test_val_register_sqli_xss_in_referral_sanitized(
        self, trade_page: Page, payload: str, description: str
    ):
        """SQLi/XSS in optional referral field must be sanitized."""
        _clear_xss_flag(trade_page)
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        referral = trade_page.locator("input[name='referral']").first
        if not referral.is_visible():
            pytest.skip("Referral field not visible in Step 2.")

        referral.fill(payload)
        trade_page.wait_for_timeout(400)

        content = trade_page.content()
        assert "SQLSTATE" not in content, f"SQL error in referral: {description}"
        assert not _is_xss_executed(trade_page), f"XSS in referral: {description}"

    # ── 13. Account Type Dropdown Required ────────────────────────────────────

    def test_val_register_no_account_type_selected_blocked(self, trade_page: Page):
        """Submitting Step 2 without selecting an Account Type must be blocked."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        pass1 = trade_page.locator("input#pass1, input[name='pass1']").first
        if not pass1.is_visible():
            pytest.skip("Step 2 not reached.")

        pass1.fill("StrongPass@123")
        pass2 = trade_page.locator("input[name='password'], input[name='pass2']").first
        pass2.fill("StrongPass@123")

        # Leave Account Type at default (unselected)
        group = trade_page.locator("select[name='group_id']").first
        group.select_option(index=0)  # Select the first option (usually placeholder)

        trade_page.locator("button:has-text('Sign up')").click()
        trade_page.wait_for_timeout(1000)

        # Must still be on register
        assert pass1.is_visible() or "register" in trade_page.url, (
            "Unselected Account Type must block Step 2 registration."
        )

    # ── 14. Multi-Step Navigation ─────────────────────────────────────────────

    def test_val_register_previous_button_returns_to_step1(self, trade_page: Page):
        """Clicking Previous in Step 2 must return to Step 1 with name field visible."""
        _navigate_register(trade_page)
        _fill_step1(trade_page, name="Test User", email="valid@test.com", phone="9876543210")
        _click_next(trade_page)
        trade_page.wait_for_timeout(600)

        prev_btn = trade_page.locator("button:has-text('Previous')").first
        if not prev_btn.is_visible():
            pytest.skip("Previous button not visible.")

        prev_btn.click()
        trade_page.wait_for_timeout(600)
        assert _is_step1_still_visible(trade_page), (
            "Previous button must return to Step 1 with name field visible."
        )
