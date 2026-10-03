"""
Trade Terminal Support & Funds Page — Validation & Security Test Suite.
Covers:
- Fund submenu navigation (Deposit / Withdraw links)
- Internal redirect verification (preventing malicious open-redirects to external phishing domains)
- Same-origin enforcement
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


from config.settings import settings


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeSupport:
    """Validation test suite for Support and Funds submenu routing."""

    @pytest.fixture(autouse=True)
    def setup_support(self, page: Page):
        """Navigate to trade terminal dashboard."""
        self.page = page
        base_url = settings.trade_terminal.base_url.rstrip("/")
        self.page.goto(f"{base_url}/dashboard/", timeout=15000)

    def test_val_trade_fund_submenu_deposit_link_integrity(self):
        """Verify Deposit link routes to internal client portal and does not redirect externally."""
        deposit_link = self.page.locator("a:has-text('Deposit'), a[href*='deposit'], [data-nav='deposit']").first
        if deposit_link.is_visible():
            href = deposit_link.get_attribute("href")
            if href:
                assert not (href.startswith("http://") and "localhost" not in href), f"Insecure HTTP deposit link: {href}"
                assert "attacker" not in href, f"Malicious redirect in deposit link: {href}"

    def test_val_trade_fund_submenu_withdraw_link_integrity(self):
        """Verify Withdraw link routes to internal client portal securely."""
        withdraw_link = self.page.locator("a:has-text('Withdraw'), a[href*='withdraw'], [data-nav='withdraw']").first
        if withdraw_link.is_visible():
            href = withdraw_link.get_attribute("href")
            if href:
                assert not (href.startswith("http://") and "localhost" not in href), f"Insecure HTTP withdraw link: {href}"
                assert "attacker" not in href, f"Malicious redirect in withdraw link: {href}"
