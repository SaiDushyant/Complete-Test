"""
Admin Portal LP Commission Log Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class LpCommissionLogPage(BasePage):
    """Page object for Admin LP Commission Log topbar, controls, and table."""

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

        # Main Table Card & DataTables (#datatable_wrapper)
        self.table_card = page.locator(".card").filter(has=page.locator("#datatable_wrapper"))
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.datatable = page.locator("#datatable")
        self.length_dropdown = page.locator("#datatable_length select")
        self.export_buttons = page.locator(".dt-buttons button")
        self.tools_container = page.locator(".report-log-tools")
        self.csv_button = page.locator(".dt-buttons button.buttons-csv")
        self.pdf_button = page.locator(".dt-buttons button.buttons-pdf")
        self.print_button = page.locator(".dt-buttons button.buttons-print")
        self.search_input = page.locator("#datatable_filter input")
        self.scroll_head = page.locator(".dataTables_scrollHead")
        self.scroll_body = page.locator(".dataTables_scrollBody")
        self.table_headers = page.locator(".dataTables_wrapper thead th[tabindex='0']")
        self.table_rows = page.locator("#datatable tbody tr:not(:has(.dataTables_empty))")
        self.empty_state_cell = page.locator("#datatable tbody td.dataTables_empty")
        self.table_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.paginate_previous = page.locator("#datatable_previous")
        self.paginate_next = page.locator("#datatable_next")
        self.paginate_pages = page.locator("#datatable_paginate .paginate_button:not(.previous):not(.next)")
        self.paginate_ellipsis = page.locator("#datatable_ellipsis")
        self.active_page = page.locator("#datatable_paginate .paginate_button.active")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin LP Commission Log page and wait for loading."""
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/aBookLpBrokerageLog"
        )
        self.goto(url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

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

    def search_table(self, query: str) -> None:
        """Fill search input and wait for DataTables filtering."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear search input and wait for DataTables to restore."""
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def select_length(self, length: str) -> None:
        """Select number of entries to display from the length dropdown."""
        self.length_dropdown.select_option(value=length)
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return the number of data rows currently rendered."""
        return self.table_rows.count()

    def get_table_info_text(self) -> str:
        """Return the DataTables info text."""
        return self.table_info.inner_text().strip()

    def get_first_row_cells(self) -> list[str]:
        """Return text of all cells in the first rendered row."""
        return [td.inner_text().strip() for td in self.table_rows.first.locator("td").all()]

    def go_next_page(self) -> None:
        """Click Next in pagination."""
        self.paginate_next.locator("a").click()
        self.page.wait_for_timeout(500)

    def go_previous_page(self) -> None:
        """Click Previous in pagination."""
        self.paginate_previous.locator("a").click()
        self.page.wait_for_timeout(500)
