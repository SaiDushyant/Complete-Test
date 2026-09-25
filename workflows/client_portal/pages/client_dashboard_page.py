"""
Client Portal Dashboard Page Object.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class ClientDashboardPage(BasePage):
    """Page object for Client Portal user dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.dashboard_container = page.locator(".dashboard-container, #dashboard, main, body")
        self.profile_link = page.locator("a[href*='profile'], [data-nav='profile'], .user-profile")
        self.account_summary_card = page.locator(".account-summary, .balance-card, .wallet-card")
        self.deposit_button = page.locator("a:has-text('Deposit'), button:has-text('Deposit')")
        self.withdraw_button = page.locator("a:has-text('Withdraw'), button:has-text('Withdraw')")

    def navigate(self) -> None:
        """Navigate to Client dashboard URL."""
        self.goto(settings.client_portal.base_url)

    def is_dashboard_displayed(self) -> bool:
        """Verify presence of client dashboard workspace."""
        return self.dashboard_container.first.is_visible()

    def navigate_to_profile(self) -> None:
        """Click user profile link."""
        # TODO (Developer 3): Confirm specific profile URL/selector
        if self.profile_link.first.is_visible():
            self.profile_link.first.click()
