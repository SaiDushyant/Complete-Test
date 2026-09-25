"""
Client Portal Header Component.
Encapsulates all standard and interactive header controls:
- Navigation logo & dynamic page title
- Account switcher badge & 'SELECT ACCOUNT' dropdown
- Search bar (accounts, transactions, wallets)
- Sidebar collapse / expand toggle
- Dark / Light theme toggle
- Notifications drawer ('Security & Clearance Alerts', Refresh, 'MARK ALL READ', auto-close)
- Support Center drawer ('ACCOUNT / SESSION INFO', FAQ list, 'SETTINGS' redirect button, Close)
- Create Account modal ('LIVE ACCOUNT CREATION', Demo Account details, Copy link, Cancel)
- Logout action button
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import List
from playwright.sync_api import Locator, Page, expect


class ClientHeaderComponent:
    """Comprehensive header component shared across all Client Portal views."""

    def __init__(self, page: Page):
        self.page = page
        self.header_container = page.locator("header")
        self.logo_image = page.locator("header img.newmenu-img")
        self.menu_toggle_button = page.locator(
            "header button[title='Collapse menu'], header button[title='Expand menu'], header button[aria-label='Collapse menu']"
        )
        self.title_heading = page.locator("header h2")
        self.account_badge = page.locator("header button").filter(has_text="Acct:")
        self.search_input = page.locator("header input[placeholder*='Search accounts' i]")
        self.theme_toggle_button = page.locator("header button[title*='theme' i]")
        self.notifications_button = page.locator("header button[title*='notifications' i]")
        self.support_button = page.locator("header button[title*='support' i]")
        self.create_account_button = page.locator("header button").filter(has_text="CREATE ACCOUNT")
        self.logout_button = page.locator("header button[title*='Logout' i]")

        # =====================================================================
        # Dropdowns & Drawers & Modals
        # =====================================================================
        # 1. Account Switcher Dropdown
        self.account_switcher_dropdown = page.locator(
            "div.absolute, div.fixed"
        ).filter(has_text="SELECT ACCOUNT")

        # 2. Notifications Drawer
        self.notifications_drawer = page.locator(
            "div.fixed.inset-0.z-50"
        ).filter(has_text=re.compile(r"Security\s*&\s*Clearance\s*Alerts", re.I))
        self.notifications_mark_all_read_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"MARK\s*ALL\s*READ", re.I))
        self.notifications_refresh_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Refresh", re.I))

        # 3. Support Center Drawer
        self.support_drawer = page.locator(
            "div.fixed.inset-0.z-50"
        ).filter(has_text=re.compile(r"Support\s*Center", re.I))
        self.support_settings_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Settings", re.I))
        self.support_close_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Close", re.I))

        # 4. Create Account Modal
        self.create_account_modal = page.locator(
            "div.fixed.inset-0.z-50"
        ).filter(has_text=re.compile(r"Create\s*Account", re.I))
        self.create_account_cancel_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Cancel", re.I))
        self.create_account_copy_demo_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Copy", re.I))
        self.create_account_request_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Request\s*New\s*Account", re.I))
        self.create_account_demo_ready_btn = page.locator(
            "div.fixed.inset-0.z-50 button"
        ).filter(has_text=re.compile(r"Demo\s*Ready", re.I))

    def is_header_visible(self) -> bool:
        """Check if top navigation header is displayed."""
        try:
            self.header_container.first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def get_title_text(self) -> str:
        """Return the current page title displayed in the header."""
        return self.title_heading.first.inner_text().strip()

    def get_selected_account(self) -> str:
        """Extract and return selected account ID from the account badge."""
        badge_text = self.account_badge.first.inner_text().strip()
        match = re.search(r"\b(\d+)\b", badge_text)
        return match.group(1) if match else badge_text

    def assert_header_elements(self, expected_title: str | None = None) -> None:
        """
        Verify that all standard header elements are properly rendered:
        - Header container is visible
        - Title matches expected page title (if provided)
        - Search input is visible
        - Account badge with ID is displayed
        - Action buttons (CREATE ACCOUNT, Theme, Notifications, Support, Logout) are visible
        - Menu toggle is present
        """
        expect(self.header_container.first).to_be_visible(timeout=10000)
        if expected_title:
            expect(self.title_heading.first).to_have_text(expected_title, timeout=10000)
        expect(self.account_badge.first).to_be_visible(timeout=10000)
        expect(self.search_input.first).to_be_visible(timeout=10000)
        expect(self.create_account_button.first).to_be_visible(timeout=10000)
        expect(self.create_account_button.first).to_be_enabled()
        expect(self.theme_toggle_button.first).to_be_visible(timeout=10000)
        expect(self.notifications_button.first).to_be_visible(timeout=10000)
        expect(self.support_button.first).to_be_visible(timeout=10000)
        expect(self.logout_button.first).to_be_visible(timeout=10000)
        expect(self.menu_toggle_button.first).to_be_visible(timeout=10000)

    # =========================================================================
    # Header Search
    # =========================================================================
    def search(self, query: str) -> None:
        """Type search query into header search bar."""
        self.search_input.first.fill(query)

    def clear_search(self) -> None:
        """Clear the header search bar."""
        self.search_input.first.fill("")

    # =========================================================================
    # Sidebar Collapse / Expand
    # =========================================================================
    def toggle_sidebar(self) -> None:
        """Click the menu toggle button to collapse or expand the sidebar."""
        self.menu_toggle_button.first.click()
        self.page.wait_for_timeout(300)

    # =========================================================================
    # Theme Toggle
    # =========================================================================
    def toggle_theme(self) -> None:
        """Click theme toggle button to switch between dark and light themes."""
        self.theme_toggle_button.first.click()
        self.page.wait_for_timeout(300)

    # =========================================================================
    # Account Switcher
    # =========================================================================
    def open_account_switcher(self) -> None:
        """Click account badge to open 'SELECT ACCOUNT' dropdown."""
        self.account_badge.first.click()
        expect(self.account_switcher_dropdown.first).to_be_visible(timeout=5000)

    def select_account(self, account_id: str) -> None:
        """Select an account from the account switcher dropdown."""
        self.open_account_switcher()
        acct_option = self.account_switcher_dropdown.first.locator("button").filter(has_text=account_id)
        expect(acct_option.first).to_be_visible(timeout=5000)
        acct_option.first.click()
        self.page.wait_for_timeout(500)
        expect(self.account_badge.first).to_contain_text(account_id, timeout=5000)

    # =========================================================================
    # Notifications Drawer
    # =========================================================================
    def open_notifications(self) -> None:
        """Click bell icon to open notifications drawer."""
        self.notifications_button.first.click()
        expect(self.notifications_drawer.first).to_be_visible(timeout=5000)

    def click_notifications_mark_all_read(self) -> None:
        """Click 'MARK ALL READ' button inside the notifications drawer."""
        expect(self.notifications_mark_all_read_btn.first).to_be_visible(timeout=5000)
        self.notifications_mark_all_read_btn.first.click()
        self.page.wait_for_timeout(500)

    def close_notifications(self) -> None:
        """Close notifications drawer via top close button or escape."""
        if self.notifications_drawer.first.is_visible():
            close_btn = self.notifications_drawer.first.locator("button").first
            close_btn.click()
            self.page.wait_for_timeout(500)

    # =========================================================================
    # Support Center Drawer
    # =========================================================================
    def open_support(self) -> None:
        """Click support center icon to open Support Center drawer."""
        self.support_button.first.click()
        expect(self.support_drawer.first).to_be_visible(timeout=5000)

    def click_support_settings(self) -> None:
        """Click 'SETTINGS' button inside Support Center drawer to redirect to settings."""
        expect(self.support_settings_btn.first).to_be_visible(timeout=5000)
        self.support_settings_btn.first.click()
        self.page.wait_for_timeout(500)

    def close_support(self) -> None:
        """Close Support Center drawer via Close button."""
        if self.support_drawer.first.is_visible():
            expect(self.support_close_btn.first).to_be_visible(timeout=5000)
            self.support_close_btn.first.click()
            self.page.wait_for_timeout(500)

    # =========================================================================
    # Create Account Modal
    # =========================================================================
    def open_create_account_modal(self) -> None:
        """Click 'CREATE ACCOUNT' button to open creation modal."""
        self.create_account_button.first.click()
        expect(self.create_account_modal.first).to_be_visible(timeout=5000)

    def close_create_account_modal(self) -> None:
        """Click 'Cancel' button to dismiss Create Account modal."""
        if self.create_account_modal.first.is_visible():
            expect(self.create_account_cancel_btn.first).to_be_visible(timeout=5000)
            self.create_account_cancel_btn.first.click()
            self.page.wait_for_timeout(500)
