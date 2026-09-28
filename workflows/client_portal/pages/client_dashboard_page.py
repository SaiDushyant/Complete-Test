"""
Client Portal Dashboard Page Object.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage


class ClientDashboardPage(BasePage):
    """Page object for Client Portal user dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Main workspace containers
        self.dashboard_container = page.locator("main")
        self.overview_heading = page.locator("h1, h2, h3").filter(has_text="Dashboard Overview")

        # Summary Cards
        self.total_funds_card = page.locator("div").filter(has_text="Total Funds").first
        self.account_balance_card = page.locator("div").filter(has_text="Account Balance").first
        self.available_buffer_card = page.locator("div").filter(has_text="Available Buffer").first
        self.active_referrals_card = page.locator("div").filter(has_text="Active Referrals").first

        # Account Cash Flow section
        self.cash_flow_container = page.locator("div").filter(has_text="Account Cash Flow").first
        self.cash_flow_day_tab = page.locator("button:has-text('Day')")
        self.cash_flow_week_tab = page.locator("button:has-text('Week')")
        self.cash_flow_month_tab = page.locator("button:has-text('Month')")

    def navigate(self) -> None:
        """Navigate to Client Portal Dashboard."""
        if "/client-portal" not in self.page.url:
            self.goto(settings.client_portal.base_url)
        else:
            self.sidebar.navigate_to_dashboard()
        expect(self.header.title_heading.first).to_have_text("Dashboard", timeout=20000)

    def is_dashboard_displayed(self) -> bool:
        """Verify presence of client dashboard workspace."""
        try:
            expect(self.header.title_heading.first).to_have_text("Dashboard", timeout=10000)
            return self.header.is_header_visible() and self.sidebar.is_sidebar_visible()
        except Exception:
            return False

    def get_summary_card_values(self) -> dict[str, str]:
        """Extract text values from the 4 summary cards."""
        return {
            "total_funds": self.total_funds_card.inner_text(),
            "account_balance": self.account_balance_card.inner_text(),
            "available_buffer": self.available_buffer_card.inner_text(),
            "active_referrals": self.active_referrals_card.inner_text(),
        }

    def select_cash_flow_period(self, period: str) -> None:
        """Select period tab (Day, Week, Month) on the Account Cash Flow section."""
        period_lower = period.lower()
        if period_lower == "day":
            self.cash_flow_day_tab.first.click()
        elif period_lower == "week":
            self.cash_flow_week_tab.first.click()
        elif period_lower == "month":
            self.cash_flow_month_tab.first.click()
        else:
            raise ValueError(f"Unknown cash flow period '{period}'. Use 'Day', 'Week', or 'Month'.")

    def get_cash_flow_period_tab(self, period: str) -> Locator:
        """Return the locator for the given cash flow period tab."""
        period_lower = period.lower()
        if period_lower == "day":
            return self.cash_flow_day_tab.first
        elif period_lower == "week":
            return self.cash_flow_week_tab.first
        elif period_lower == "month":
            return self.cash_flow_month_tab.first
        raise ValueError(f"Unknown cash flow period '{period}'. Use 'Day', 'Week', or 'Month'.")

