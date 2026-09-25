"""
Admin Portal Dashboard Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class AdminDashboardPage(BasePage):
    """Page object for Admin Console main dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Admin layout indicators
        self.sidebar_nav = page.locator(".sidebar, #sidebar-menu, .vertical-menu, nav")
        self.header_navbar = page.locator(".navbar, .page-header, header")
        self.users_menu_item = page.locator("a[href*='Users'], a:has-text('Users'), [data-nav='users']")
        self.reports_menu_item = page.locator("a[href*='Reports'], a:has-text('Reports')")
        self.dashboard_widgets = page.locator(".card, .widget, .page-content")

    def navigate(self) -> None:
        """Navigate to Admin dashboard."""
        self.goto(settings.admin_portal.base_url)

    def is_dashboard_displayed(self) -> bool:
        """Verify presence of admin navigation sidebar or header."""
        return self.sidebar_nav.first.is_visible() or self.header_navbar.first.is_visible()

    def navigate_to_user_management(self) -> None:
        """Click User Management link in navigation."""
        # TODO (Developer 2): Finalize specific navigation route/selector
        if self.users_menu_item.first.is_visible():
            self.users_menu_item.first.click()
