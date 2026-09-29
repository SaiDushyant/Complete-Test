"""
Client Portal Dashboard Page Object.
Encapsulates all dashboard workspace elements: summary metric cards (Total Funds, Account Balance,
Available Buffer, Active Referrals), Account Cash Flow period toggles, and workspace components.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Dict, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_dashboard_page")


class ClientDashboardPage(BasePage):
    """Page object for Client Portal main user dashboard workspace."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Universal Components
        self.header: ClientHeaderComponent = ClientHeaderComponent(page)
        self.sidebar: ClientSidebarComponent = ClientSidebarComponent(page)

        # Main Workspace Layout Containers
        self.dashboard_container: Locator = page.locator("main, .dashboard-container, #dashboard")
        self.overview_heading: Locator = page.locator("h1, h2, h3").filter(has_text="Dashboard Overview").first

        # 1. Summary Metric Cards
        self.total_funds_card: Locator = page.locator("div").filter(has_text="Total Funds").first
        self.account_balance_card: Locator = page.locator("div").filter(has_text="Account Balance").first
        self.available_buffer_card: Locator = page.locator("div").filter(has_text="Available Buffer").first
        self.active_referrals_card: Locator = page.locator("div").filter(has_text="Active Referrals").first
        self.summary_cards: Locator = page.locator("main div.grid > div, main .grid > div")

        # 2. Account Cash Flow Section & Controls
        self.cash_flow_container: Locator = page.locator("div").filter(has_text="Account Cash Flow").first
        self.cash_flow_heading: Locator = self.cash_flow_container.locator("h2, h3, div").filter(has_text="Account Cash Flow").first
        self.cash_flow_day_tab: Locator = page.locator("button:has-text('Day')").first
        self.cash_flow_week_tab: Locator = page.locator("button:has-text('Week')").first
        self.cash_flow_month_tab: Locator = page.locator("button:has-text('Month')").first
        self.cash_flow_period_buttons: Locator = page.locator("button:has-text('Day'), button:has-text('Week'), button:has-text('Month')")

    def navigate(self, url: Optional[str] = None) -> None:
        """Navigate to Client Portal Dashboard workspace."""
        target_url = url or f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            logger.info(f"Navigating to Client Portal Dashboard: {target_url}")
            self.goto(target_url)
        else:
            logger.info("Already on Client Portal, navigating to dashboard tab via sidebar...")
            self.sidebar.navigate_to_dashboard()

        # Settle on Dashboard
        expect(self.header.title_heading.first).to_have_text("Dashboard", timeout=20000)

    def is_dashboard_displayed(self) -> bool:
        """Verify presence and visibility of core dashboard components."""
        try:
            expect(self.header.title_heading.first).to_have_text("Dashboard", timeout=10000)
            return (
                self.header.is_header_visible()
                and self.sidebar.is_sidebar_visible()
                and self.total_funds_card.is_visible()
            )
        except Exception:
            return False

    def get_summary_card_values(self) -> Dict[str, str]:
        """Extract and return text contents from the 4 primary summary cards."""
        logger.info("Extracting summary metric card values from dashboard...")
        return {
            "total_funds": self.total_funds_card.inner_text().strip(),
            "account_balance": self.account_balance_card.inner_text().strip(),
            "available_buffer": self.available_buffer_card.inner_text().strip(),
            "active_referrals": self.active_referrals_card.inner_text().strip(),
        }

    def select_cash_flow_period(self, period: str) -> None:
        """Select period tab (Day, Week, Month) on the Account Cash Flow section."""
        period_lower = period.lower().strip()
        logger.info(f"Switching Account Cash Flow period to: {period}")

        tab = self.get_cash_flow_period_tab(period_lower)
        expect(tab).to_be_visible(timeout=10000)
        tab.click()
        self.page.wait_for_timeout(400)

    def get_cash_flow_period_tab(self, period: str) -> Locator:
        """Return the locator for the given cash flow period tab."""
        period_lower = period.lower().strip()
        if period_lower == "day":
            return self.cash_flow_day_tab
        elif period_lower == "week":
            return self.cash_flow_week_tab
        elif period_lower == "month":
            return self.cash_flow_month_tab
        raise ValueError(f"Unknown cash flow period '{period}'. Expected 'Day', 'Week', or 'Month'.")

    def is_cash_flow_container_visible(self) -> bool:
        """Return True if Account Cash Flow section is visible."""
        return self.cash_flow_container.is_visible()
