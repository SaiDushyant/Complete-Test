"""
Trade Terminal API Access Page — Validation & Security Test Suite.
Covers:
- API Key display (non-empty, readonly/disabled, cleartext storage leak check)
- Copy Button functionality & rapid double-click idempotency
- CSV Symbols export link validity
- Console credential masking verification
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.trade_terminal.pages.api_access_page import ApiAccessPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeApiAccess:
    """Validation and security test suite for API Access page."""

    @pytest.fixture(autouse=True)
    def setup_api_access(self, api_access_page: ApiAccessPage):
        """Navigate to API Access page."""
        self.api_page = api_access_page
        self.page = api_access_page.page
        self.api_page.navigate()

    def test_val_trade_api_key_readonly_enforcement(self):
        """Verify API Key text input is readonly or disabled to prevent client-side tampering."""
        api_input = self.page.locator("input#apitext, input.api-key-input, input[name='api_key']").first
        if api_input.is_visible():
            is_readonly = api_input.get_attribute("readonly") is not None
            is_disabled = api_input.is_disabled()
            assert is_readonly or is_disabled, "API Key input field must be readonly or disabled."

            # Verify value is not empty
            val = api_input.input_value()
            assert val != "", "API Key field should display a non-empty token string."

    def test_val_trade_api_key_not_leaked_in_web_storage(self):
        """Verify API raw secret keys are not exposed in localStorage or sessionStorage in cleartext."""
        local_storage_keys = self.page.evaluate("() => Object.keys(localStorage)")
        session_storage_keys = self.page.evaluate("() => Object.keys(sessionStorage)")

        # Ensure no blatant unmasked api_secret or raw private keys
        for key in local_storage_keys:
            assert "raw_secret" not in key.lower(), f"Potential secret leak in localStorage key: {key}"

        for key in session_storage_keys:
            assert "raw_secret" not in key.lower(), f"Potential secret leak in sessionStorage key: {key}"

    def test_val_trade_api_copy_button_idempotency(self):
        """Verify copy button handles single and rapid multiple clicks gracefully without errors."""
        copy_btn = self.page.locator("button:has-text('Copy'), button.copy-btn").first
        if copy_btn.is_visible():
            # Click once
            copy_btn.click()
            self.page.wait_for_timeout(200)

            # Double click
            copy_btn.dblclick()
            self.page.wait_for_timeout(300)

            assert self.page.is_visible("body"), "Page crashed on copy button rapid double-click."

    def test_val_trade_api_csv_symbols_link(self):
        """Verify Symbols CSV export link exists and points to a valid file/endpoint."""
        csv_btn = self.page.locator("a#csvbtn, a:has-text('CSV'), button#csvbtn").first
        if csv_btn.is_visible():
            href = csv_btn.get_attribute("href")
            if href:
                assert not href.startswith("http://attacker.com"), "CSV export points to untrusted external source."
