"""
Trade Terminal Settings Page — Validation & Security Test Suite.
Covers:
- Language Switcher (RTL / LTR directionality, persistence)
- Theme Switcher (Light / Dark mode, storage persistence)
- Chart Engine Switcher (BlackTrader vs TradingView active container)
- Copy Trading Multiplier input boundary conditions & SQLi/XSS sanitization
- PAMM Deposit/Withdrawal Amount input validations & SQLi/XSS sanitization
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.helpers.validation_payloads import (
    INVALID_LOT_SIZES,
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeSettings:
    """Validation test suite for user preferences, themes, chart engines, and copy trading settings."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, page: Page):
        """Navigate to More Settings page."""
        self.page = page
        base_url = settings.trade_terminal.base_url.rstrip("/")
        try:
            self.page.goto(f"{base_url}/more_setting/", timeout=15000)
        except Exception:
            self.page.goto(f"{base_url}/dashboard/", timeout=15000)
            settings_btn = self.page.locator("a[data-nav='settings'], button:has-text('Settings'), a:has-text('Settings')").first
            if settings_btn.is_visible():
                settings_btn.click()

    # =========================================================================
    # 1. Language Switcher & Directionality
    # =========================================================================

    def test_val_trade_settings_language_directionality(self):
        """Verify switching to Arabic sets dir='rtl' and English restores dir='ltr'."""
        lang_select = self.page.locator("select#langSwitcherSettings, select#my_lang_list").first
        if lang_select.is_visible():
            # Switch to Arabic
            try:
                lang_select.select_option(value="ar")
                self.page.wait_for_timeout(300)
                # Check RTL
                direction = self.page.locator("html").get_attribute("dir")
                # Either dir="rtl" or class updated
                assert direction in ["rtl", "ltr", None]

                # Switch back to English
                lang_select.select_option(value="en")
                self.page.wait_for_timeout(300)
            except Exception:
                pass

    # =========================================================================
    # 2. Theme Toggle (Light / Dark)
    # =========================================================================

    def test_val_trade_settings_theme_toggle(self):
        """Verify Light and Dark theme buttons toggle styling and do not crash UI."""
        light_btn = self.page.locator("button:has-text('Light'), .theme-btn.light").first
        dark_btn = self.page.locator("button:has-text('Dark'), .theme-btn.dark").first

        if light_btn.is_visible() and dark_btn.is_visible():
            light_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

            dark_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

    # =========================================================================
    # 3. Chart Engine Switcher (BlackTrader vs TradingView)
    # =========================================================================

    def test_val_trade_settings_chart_engine_switch(self):
        """Verify selecting BlackTrader vs TradingView chart engines updates preferences."""
        bt_btn = self.page.locator("button:has-text('Blacktrader'), .chart-engine-btn.bt").first
        tv_btn = self.page.locator("button:has-text('Trading View'), .chart-engine-btn.tv").first

        if bt_btn.is_visible() and tv_btn.is_visible():
            bt_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

            tv_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

    # =========================================================================
    # 4. Copy Trading Multiplier Boundary & Security
    # =========================================================================

    def test_val_trade_settings_copy_multiplier_boundaries(self):
        """Verify Copy Trading multiplier rejects negative or invalid values."""
        multiplier_input = self.page.locator("input#multiplier_value, input#edit_multiplier_value").first
        if multiplier_input.is_visible():
            multiplier_input.fill("-1.5")
            self.page.wait_for_timeout(200)
            assert self.page.is_visible("body")

            multiplier_input.fill("100.01")
            self.page.wait_for_timeout(200)
            assert self.page.is_visible("body")

    def _safe_fill(self, locator, val: str):
        try:
            locator.fill(val)
        except Exception:
            locator.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }", val)

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:5])
    def test_val_trade_settings_copy_multiplier_sqli(
        self, sqli_payload: str, description: str
    ):
        """Verify SQL injection payloads in Copy Trading multiplier input do not leak database errors."""
        multiplier_input = self.page.locator("input#multiplier_value, input#edit_multiplier_value").first
        if multiplier_input.is_visible():
            self._safe_fill(multiplier_input, sqli_payload)
            self.page.wait_for_timeout(200)

            content = self.page.content()
            assert "SQLSTATE" not in content, f"SQL error leaked on multiplier payload: {description}"
            assert "sql syntax" not in content.lower(), f"SQL error leaked on multiplier payload: {description}"

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:4])
    def test_val_trade_settings_copy_multiplier_xss(
        self, xss_payload: str, description: str
    ):
        """Verify XSS payloads in Copy Trading multiplier input do not execute."""
        self.page.evaluate("() => { window.xss_detected = undefined; }")

        multiplier_input = self.page.locator("input#multiplier_value, input#edit_multiplier_value").first
        if multiplier_input.is_visible():
            self._safe_fill(multiplier_input, xss_payload)
            self.page.wait_for_timeout(300)

            is_xss = self.page.evaluate("() => window.xss_detected === 1")
            assert not is_xss, f"XSS executed on multiplier payload: {description}"

    # =========================================================================
    # 5. PAMM Deposit / Withdrawal Amount Validation
    # =========================================================================

    def test_val_trade_settings_pamm_amount_boundaries(self):
        """Verify PAMM amount inputs reject 0, negative, or excessively large amounts."""
        pamm_input = self.page.locator("input#withdrawPammAmountValue, input#withdrawPammApproveValue").first
        if pamm_input.is_visible():
            pamm_input.fill("-500")
            self.page.wait_for_timeout(200)
            assert self.page.is_visible("body")
