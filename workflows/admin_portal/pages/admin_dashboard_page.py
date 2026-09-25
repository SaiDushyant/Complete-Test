"""
Admin Portal Dashboard Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class AdminDashboardPage(BasePage):
    """Page object for Admin Console main dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.sidebar_nav = page.locator(
            ".sidebar, #sidebar-menu, .vertical-menu, nav"
        )
        self.header_navbar = page.locator(
            ".navbar, .page-header, header"
        )
        self.users_menu_item = page.locator(
            "a[href*='Users'], a:has-text('Users'), [data-nav='users']"
        )
        self.reports_menu_item = page.locator(
            "a[href*='Reports'], a:has-text('Reports')"
        )
        self.dashboard_widgets = page.locator(
            ".card, .widget, .page-content"
        )

        self.dashboard_title = page.locator(
            ".topbar-page-title, .topbar-title-source h4"
        )
        self.kpi_cards = page.locator(
            ".kpi-card"
        )
        self.kpi_labels = page.locator(
            ".kpi-card .kpi-label"
        )
        self.kpi_values = page.locator(
            ".kpi-card .counter-value"
        )
        self.book_headings = page.locator(
            ".book-group-heading"
        )
        self.deposit_withdraw_chart = page.locator(
            "#depositWithdrawTrendChart .apexcharts-svg"
        )
        self.book_compare_chart = page.locator(
            "#bookCompareChart .apexcharts-svg"
        )
        self.chart_legend_text = page.locator(
            ".apexcharts-legend-text"
        )

        self.profile_button = page.locator(
            "#page-header-user-dropdown"
        )
        self.profile_menu = page.locator(
            ".profile-menu"
        )
        self.profile_name = page.locator(
            ".profile-menu .fw-bold"
        )
        self.profile_role = page.locator(
            ".profile-menu small"
        )
        self.logout_link = page.locator(
            ".profile-menu .logout-item"
        )
        self.theme_toggle = page.locator(
            "#admin-theme-toggle"
        )
        self.notification_button = page.locator(
            "#page-header-notifications-dropdown"
        )
        self.notification_menu = page.locator(
            ".notification-menu"
        )
        self.notification_count = page.locator(
            "#notification-count"
        )
        self.mark_all_read = page.locator(
            "#markAllRead"
        )
        self.menu_button = page.locator(
            "#vertical-menu-btn"
        )

    def navigate(self) -> None:
        """Navigate to the Admin dashboard."""
        self.goto(settings.admin_portal.base_url)

    def is_dashboard_displayed(self) -> bool:
        """Verify Admin navigation or dashboard content is visible."""
        return (
            self.sidebar_nav.first.is_visible()
            or self.header_navbar.first.is_visible()
        )

    def open_profile_menu(self) -> None:
        """Open the Admin profile menu."""
        self.profile_button.click()

    def get_theme_mode(self) -> str | None:
        """Return the current Admin theme mode."""
        return self.page.locator("body").get_attribute(
            "data-layout-mode"
        )

    def toggle_theme(self) -> None:
        """Switch the Admin theme."""
        self.theme_toggle.click()

    def navigate_to_user_management(self) -> None:
        """Navigate to User Management."""
        if self.users_menu_item.first.is_visible():
            self.users_menu_item.first.click()