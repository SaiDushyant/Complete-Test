"""
Admin Portal Account Requests Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class AccountRequestsPage(BasePage):
    """Page object for Admin Account Requests topbar, actions, filters, and tables."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar elements (.navbar-header)
        self.topbar = page.locator("#page-topbar")
        self.navbar_header = page.locator(".navbar-header")
        self.page_title = page.locator(".topbar-page-title")
        self.brand_logo = page.locator(".navbar-brand-box a.logo.admin-brand-logo")
        self.brand_logo_images = page.locator(".navbar-brand-box img")
        self.logo_small = page.locator(".navbar-brand-box .logo-sm img.mainLogoSmall")
        self.logo_large = page.locator(".navbar-brand-box .logo-lg img.mainLogoLarge")
        self.logo_text = page.locator(".navbar-brand-box .logo-txt.mainProjectName")
        self.menu_button = page.locator("#vertical-menu-btn")
        self.theme_toggle = page.locator("#admin-theme-toggle")
        self.theme_dark_icon = page.locator("#admin-theme-toggle svg.theme-dark-icon")
        self.theme_light_icon = page.locator("#admin-theme-toggle svg.theme-light-icon")
        self.notification_button = page.locator("#page-header-notifications-dropdown")
        self.notification_count = page.locator("#notification-count")
        self.notification_menu = page.locator(".notification-menu")
        self.mark_all_read = page.locator("#markAllRead")
        self.notification_empty_text = page.locator(".notification-list p")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_initials = page.locator("#page-header-user-dropdown .header-profile-initials")
        self.profile_topbar_name = page.locator("#page-header-user-dropdown span.fw-medium")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Page Heading & Controls
        self.card_heading = page.locator("h4, .card-title").filter(has_text=re.compile(r"Client Account Creation Requests", re.I))
        self.refresh_button = page.locator("#refreshAccountRequests, button:has-text('Refresh')")

        # DataTable Card & Controls (#clientAccountRequestsTable)
        self.datatable_wrapper = page.locator("#clientAccountRequestsTable_wrapper, .dataTables_wrapper")
        self.length_dropdown = page.locator("select[name='clientAccountRequestsTable_length'], .dataTables_length select")
        self.search_input = page.locator("#clientAccountRequestsTable_filter input, .dataTables_filter input")
        self.requests_table = page.locator("#clientAccountRequestsTable")
        self.table_headers = page.locator("#clientAccountRequestsTable thead th")
        self.request_rows = page.locator("#clientAccountRequestsTable tbody tr:not(:has(.dataTables_empty))")
        self.empty_state_cell = page.locator("#clientAccountRequestsTable tbody td.dataTables_empty")

        # Status Badges & Action Buttons
        self.status_badges = page.locator(".request-status")
        self.approve_buttons = page.locator("button.btnApproveAccountRequest")
        self.reject_buttons = page.locator("button.btnRejectAccountRequest")

        # Pagination & Info
        self.table_info = page.locator("#clientAccountRequestsTable_info, .dataTables_info")
        self.pagination = page.locator("#clientAccountRequestsTable_paginate, .dataTables_paginate")
        self.paginate_previous = page.locator("#clientAccountRequestsTable_previous, .paginate_button.previous")
        self.paginate_next = page.locator("#clientAccountRequestsTable_next, .paginate_button.next")
        self.active_page = page.locator(".paginate_button.active")

        # Loader
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Account Requests page."""
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/clientAccountRequests"
        )
        if "/admin/Controlbase/clientAccountRequests" not in self.page.url:
            self.goto(url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear, page title to be visible, and datatable to load."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        try:
            self.request_rows.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(300)

    def open_notifications(self) -> None:
        """Open the notifications dropdown."""
        self.notification_button.click()

    def open_profile_menu(self) -> None:
        """Open the admin user profile menu."""
        self.profile_button.click()

    def toggle_theme(self) -> None:
        """Click the theme switch button."""
        self.theme_toggle.click()

    def get_theme_mode(self) -> str | None:
        """Return the current data-layout-mode attribute of the body tag."""
        return self.page.locator("body").get_attribute("data-layout-mode")

    def click_refresh(self) -> None:
        """Click the refresh button."""
        self.refresh_button.click()
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def select_page_length(self, length: str) -> None:
        """Select the number of entries from the dropdown."""
        self.length_dropdown.select_option(str(length))
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def search_request(self, query: str) -> None:
        """Search requests by name, email, or account ID."""
        self.search_input.fill(query)
        self.search_input.press("Enter")
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear the search input."""
        self.search_input.fill("")
        self.search_input.press("Enter")
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def get_request_count(self) -> int:
        """Return the number of requests displayed in the table."""
        return self.request_rows.count()

    def get_table_info_text(self) -> str:
        """Return the table pagination status text."""
        return self.table_info.inner_text().strip()

    def click_next_page(self) -> None:
        """Click the Next pagination button."""
        self.paginate_next.click()
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_previous_page(self) -> None:
        """Click the Previous pagination button."""
        self.paginate_previous.click()
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_page_number(self, page_num: int) -> None:
        """Click a specific page number link in the pagination controls."""
        page_btn = self.pagination.locator(
            "li.paginate_button:not(.previous):not(.next) a"
        ).filter(has_text=re.compile(rf"^\s*{page_num}\s*$"))
        page_btn.scroll_into_view_if_needed()
        page_btn.click()
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def get_active_page_number(self) -> str:
        """Get the current active page number text."""
        return self.active_page.inner_text().strip()

    def sort_column_by_name(self, column_name: str) -> None:
        """Click a column header to toggle sorting."""
        header = self.table_headers.filter(has_text=re.compile(rf"^\s*{re.escape(column_name)}\s*$", re.I))
        header.click()
        try:
            self.page.locator("#clientAccountRequestsTable_processing, .dataTables_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

