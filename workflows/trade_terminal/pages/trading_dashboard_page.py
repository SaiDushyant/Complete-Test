"""
Trade Terminal Trading Dashboard Page Object.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class TradingDashboardPage(BasePage):
    """Page object for Trade Terminal main dashboard workspace."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Dashboard elements (with fallback selectors)
        self.dashboard_container = page.locator(".dashboard-container, #dashboard, main, body")
        self.watchlist_panel = page.locator(".watchlist-panel, .watchlist-container, #watchlist")
        self.order_ticket_button = page.locator("button:has-text('New Order'), .btn-order, [data-action='new-order']")
        self.positions_tab = page.locator(".positions-tab, a:has-text('Positions'), [data-tab='positions']")
        self.user_menu = page.locator(".user-profile, .user-menu, [data-dropdown='user-menu']")

    def navigate(self) -> None:
        """Navigate to dashboard URL."""
        self.goto(settings.trade_terminal.base_url)

    def is_dashboard_displayed(self) -> bool:
        """Verify dashboard interface presence."""
        return self.dashboard_container.first.is_visible()

    def open_order_entry(self) -> None:
        """Open the order entry / ticket modal or panel."""
        # TODO (Developer 1): Update selector when order modal trigger is finalized
        if self.order_ticket_button.first.is_visible():
            self.order_ticket_button.first.click()

    def select_positions_tab(self) -> None:
        """Switch view to Positions tab."""
        # TODO (Developer 1): Connect to specific tab identifier in terminal
        if self.positions_tab.first.is_visible():
            self.positions_tab.first.click()
