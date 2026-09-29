"""
Admin Portal Dashboard Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminDashboardPage(BasePage):
    """Page object for Admin Console main dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Topbar & Sidebar components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Admin layout indicators
        self.sidebar_nav = page.locator(".sidebar, #sidebar-menu, .vertical-menu, nav")
        self.header_navbar = page.locator(".navbar, .page-header, header")
        self.users_menu_item = page.locator("a[href*='Users'], a:has-text('Users'), [data-nav='users']")
        self.reports_menu_item = page.locator("a[href*='Reports'], a:has-text('Reports')")
        self.dashboard_widgets = page.locator(".card, .widget, .page-content")

    def navigate(self) -> None:
        """Navigate to Admin dashboard."""
        self.goto(settings.admin_portal.base_url)
        expect(self.sidebar_nav.first).to_be_visible(timeout=15000)

    def is_dashboard_displayed(self) -> bool:
        """Verify presence of admin navigation sidebar or header."""
        return self.sidebar_nav.first.is_visible() or self.header_navbar.first.is_visible()

    def navigate_to_deposit_via_sidebar(self) -> None:
        """Navigate from dashboard to Deposit page using sidebar."""
        self.sidebar.navigate_to_deposit()

    def navigate_to_withdrawal_via_sidebar(self) -> None:
        """Navigate from dashboard to Withdrawal page using sidebar."""
        self.sidebar.navigate_to_withdrawal()

    def navigate_to_deposit_list_via_sidebar(self) -> None:
        """Navigate from dashboard to Deposit List page using sidebar."""
        self.sidebar.navigate_to_deposit_list()

    def navigate_to_withdraw_list_via_sidebar(self) -> None:
        """Navigate from dashboard to Withdraw List page using sidebar."""
        self.sidebar.navigate_to_withdraw_list()

    def navigate_to_user_management(self) -> None:
        """Click User Management link in navigation."""
        if self.users_menu_item.first.is_visible():
            self.users_menu_item.first.click()
