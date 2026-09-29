"""
Admin Portal Topbar Component.
Encapsulates top navigation elements:
- Brand Logo
- Sidebar Hamburger Toggle (#vertical-menu-btn)
- Theme Toggle (#admin-theme-toggle)
- Notifications Bell & Dropdown (#page-header-notifications-dropdown)
- User Profile Dropdown (#page-header-user-dropdown)
- Logout Link
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage


class AdminTopbarComponent(BasePage):
    """Header topbar component across all Admin Portal pages."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.topbar = page.locator("header#page-topbar, .navbar-header").first
        self.menu_toggle_btn = page.locator("#vertical-menu-btn")
        self.theme_toggle_btn = page.locator("#admin-theme-toggle")
        self.notifications_btn = page.locator("#page-header-notifications-dropdown")
        self.notifications_dropdown = page.locator("#page-header-notifications-dropdown + .dropdown-menu")
        self.mark_all_read_btn = page.locator("#markAllRead")
        self.user_dropdown_btn = page.locator("#page-header-user-dropdown")
        self.logout_item = page.locator(".logout-item")

    def get_layout_mode(self) -> str:
        """Return current layout mode ('light' or 'dark')."""
        return self.page.evaluate("() => document.body.getAttribute('data-layout-mode') || 'light'")

    def toggle_theme(self) -> str:
        """Click theme switcher and return new data-layout-mode."""
        expect(self.theme_toggle_btn).to_be_visible(timeout=5000)
        mode_before = self.get_layout_mode()
        self.theme_toggle_btn.click()
        self.page.wait_for_timeout(300)
        mode_after = self.get_layout_mode()
        return mode_after

    def open_notifications(self) -> None:
        """Click notifications bell to expand notification dropdown."""
        expect(self.notifications_btn).to_be_visible(timeout=5000)
        if not self.notifications_dropdown.is_visible():
            self.notifications_btn.click()
            expect(self.notifications_dropdown).to_be_visible(timeout=5000)

    def close_notifications(self) -> None:
        """Close notifications dropdown if open."""
        if self.notifications_dropdown.is_visible():
            self.notifications_btn.click()
            expect(self.notifications_dropdown).not_to_be_visible(timeout=5000)

    def open_user_menu(self) -> None:
        """Open user profile dropdown menu."""
        expect(self.user_dropdown_btn).to_be_visible(timeout=5000)
        self.user_dropdown_btn.click()
        expect(self.logout_item).to_be_visible(timeout=5000)
