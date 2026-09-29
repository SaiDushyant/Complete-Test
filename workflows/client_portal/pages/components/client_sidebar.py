"""
Client Portal Sidebar Navigation Component.
Encapsulates all view tabs inside #sidebar-nav.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_sidebar")


class ClientSidebarComponent(BasePage):
    """Sidebar navigation component for switching views in the Client Portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.sidebar_container = page.locator("#sidebar-nav, aside, [aria-label='Client portal navigation']")
        self.dashboard_tab = self.sidebar_container.get_by_role("button", name="Dashboard")
        self.deposit_tab = self.sidebar_container.get_by_role("button", name="Deposit")
        self.withdraw_tab = self.sidebar_container.get_by_role("button", name="Withdraw")
        self.internal_transfer_tab = self.sidebar_container.get_by_role("button", name="Internal Transfer")
        self.wallet_tab = self.sidebar_container.get_by_role("button", name="Wallet")
        self.copy_trading_tab = self.sidebar_container.get_by_role("button", name="Copy Trading")
        self.mam_tab = self.sidebar_container.get_by_role("button", name="MAM")
        self.pamm_tab = self.sidebar_container.get_by_role("button", name="PAMM")
        self.refer_earn_tab = self.sidebar_container.get_by_role("button", name="Refer & Earn")
        self.settings_tab = self.sidebar_container.get_by_role("button", name="Settings")

    def is_sidebar_visible(self) -> bool:
        """Check if sidebar navigation container is visible."""
        try:
            self.sidebar_container.first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def navigate_to_dashboard(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.dashboard_tab.first).to_be_visible(timeout=10000)
        self.dashboard_tab.first.click()

    def navigate_to_deposit(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.deposit_tab.first).to_be_visible(timeout=10000)
        self.deposit_tab.first.click()

    def navigate_to_withdraw(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.withdraw_tab.first).to_be_visible(timeout=10000)
        self.withdraw_tab.first.click()

    def navigate_to_internal_transfer(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.internal_transfer_tab.first).to_be_visible(timeout=10000)
        self.internal_transfer_tab.first.click()

    def navigate_to_wallet(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.wallet_tab.first).to_be_visible(timeout=10000)
        self.wallet_tab.first.click()

    def navigate_to_copy_trading(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.copy_trading_tab.first).to_be_visible(timeout=10000)
        self.copy_trading_tab.first.click()

    def navigate_to_mam(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.mam_tab.first).to_be_visible(timeout=10000)
        self.mam_tab.first.click()

    def navigate_to_pamm(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.pamm_tab.first).to_be_visible(timeout=10000)
        self.pamm_tab.first.click()

    def navigate_to_refer_earn(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.refer_earn_tab.first).to_be_visible(timeout=10000)
        self.refer_earn_tab.first.click()

    def navigate_to_settings(self) -> None:
        expect(self.sidebar_container.first).to_be_visible(timeout=15000)
        expect(self.settings_tab.first).to_be_visible(timeout=10000)
        self.settings_tab.first.click()
