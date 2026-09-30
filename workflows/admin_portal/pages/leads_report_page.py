"""
Admin Portal Leads Report Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class LeadsReportPage(BasePage):
    """Page object for Admin Leads Report topbar, filters, table, and actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar elements (.navbar-header)
        self.page_title = page.locator(".topbar-page-title")
        self.brand_logo = page.locator(".navbar-brand-box a.logo.admin-brand-logo")
        self.brand_logo_images = page.locator(".navbar-brand-box img")
        self.logo_small = page.locator(".navbar-brand-box img.mainLogoSmall")
        self.logo_large = page.locator(".navbar-brand-box img.mainLogoLarge")
        self.menu_button = page.locator("#vertical-menu-btn")
        self.theme_toggle = page.locator("#admin-theme-toggle")
        self.theme_dark_icon = page.locator("#admin-theme-toggle svg.theme-dark-icon")
        self.theme_light_icon = page.locator("#admin-theme-toggle svg.theme-light-icon")
        self.notification_button = page.locator("#page-header-notifications-dropdown")
        self.notification_count = page.locator("#notification-count")
        self.notification_menu = page.locator(".notification-menu")
        self.mark_all_read = page.locator("#markAllRead")
        self.notification_items = page.locator(".notification-item")
        self.notification_empty_text = page.locator(".notification-list p")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_initials = page.locator("#page-header-user-dropdown .header-profile-initials")
        self.profile_topbar_name = page.locator("#page-header-user-dropdown span.fw-medium")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Filter Bar (.report-filter-bar)
        self.filter_bar = page.locator(".report-filter-bar")
        self.from_date_input = page.locator("#fromDate")
        self.to_date_input = page.locator("#toDate")
        self.employee_select = page.locator("#admin_id")
        self.lead_type_select = page.locator("#lead_type_id")
        self.filter_button = page.locator("#filterLeadReport")
        self.download_button = page.locator("#downloadLeadReport")

        # Main Table Card & DataTable controls
        self.table_card = page.locator(".card.report-table-card")
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.search_input = page.locator("#datatable_filter input, input[type='search'][aria-controls='datatable']")
        self.datatable = page.locator("table#datatable")
        self.table_headers = page.locator("table#datatable thead th")
        self.table_rows = page.locator("table#datatable tbody tr:not(:has(td.dataTables_empty))")
        self.empty_state_cell = page.locator("table#datatable tbody td.dataTables_empty")
        self.datatable_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_previous = page.locator("#datatable_previous")
        self.pagination_next = page.locator("#datatable_next")
        self.excel_button = page.locator(".buttons-excel")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Leads Report page and wait for loading."""
        report_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/report"
        )
        self.goto(report_url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

    def is_report_displayed(self) -> bool:
        """Verify the Leads Report heading is displayed."""
        return self.page_title.is_visible()

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
        """Return the data-layout-mode attribute of body."""
        return self.page.locator("body").get_attribute("data-layout-mode")

    def set_date_range(self, from_date: str, to_date: str) -> None:
        """Set the fromDate and toDate input fields."""
        self.from_date_input.fill(from_date)
        self.to_date_input.fill(to_date)

    def select_employee(self, value_or_label: str) -> None:
        """Select an employee option by value or visible label."""
        try:
            self.employee_select.select_option(value=value_or_label)
        except Exception:
            self.employee_select.select_option(label=value_or_label)

    def select_lead_type(self, value_or_label: str) -> None:
        """Select a lead type option by value or visible label."""
        try:
            self.lead_type_select.select_option(value=value_or_label)
        except Exception:
            self.lead_type_select.select_option(label=value_or_label)

    def click_filter(self) -> None:
        """Click the Filter button."""
        self.filter_button.click()
        self.page.wait_for_timeout(500)

    def search_table(self, query: str) -> None:
        """Filter the table rows using the search box."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear the search input."""
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return the count of rendered data rows."""
        return self.table_rows.count()

    def get_table_info_text(self) -> str:
        """Return the text in datatable_info."""
        return self.datatable_info.inner_text().strip()


