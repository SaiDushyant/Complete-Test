"""
Admin Portal LP Transaction Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class LpTransactionPage(BasePage):
    """Page object for Admin LP Transaction topbar, heading, modal, and table."""

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

        # Page Heading & Actions
        self.heading = page.locator("h4.font-size-18, .page-title-box h4")
        self.add_transaction_button = page.locator("#addNew")

        # Add Transaction Modal (#myModal)
        self.transaction_modal = page.locator("#myModal")
        self.transaction_modal_title = page.locator("#myModal .modal-title")
        self.transaction_type_select = page.locator("#myModal #transaction_type")
        self.amount_input = page.locator("#myModal #amount")
        self.mode_of_payment_input = page.locator("#myModal #mode_of_payment")
        self.save_button = page.locator("#myModal #formSubmit")
        self.close_button = page.locator(
            "#myModal button:has-text('Close'), #myModal .ux-card-close, #myModal [data-bs-dismiss='modal']"
        )

        # Main Table Card & DataTables (#datatable_wrapper)
        self.table_card = page.locator(".card").filter(has=page.locator("#datatable_wrapper"))
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.datatable = page.locator("#datatable")
        self.length_dropdown = page.locator("#datatable_length select")
        self.search_input = page.locator("#datatable_filter input")
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr:not(:has(.dataTables_empty))")
        self.empty_state_cell = page.locator("#datatable tbody td.dataTables_empty")
        self.table_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.paginate_previous = page.locator("#datatable_previous")
        self.paginate_next = page.locator("#datatable_next")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin LP Transaction page and wait for loading."""
        lp_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/aBookBalanceTransaction"
        )
        self.goto(lp_url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

    def is_lp_transaction_displayed(self) -> bool:
        """Verify the LP Transaction heading is displayed."""
        return self.page_title.is_visible() and self.heading.is_visible()

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

    def open_add_transaction_modal(self) -> None:
        """Click Add Transaction button and wait for modal."""
        self.add_transaction_button.click()
        self.transaction_modal.wait_for(state="visible", timeout=5000)

    def close_add_transaction_modal(self) -> None:
        """Safely dismiss the Add Transaction modal."""
        try:
            btn = self.close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('myModal');
            if (el && window.jQuery) window.jQuery(el).modal('hide');
        }""")
        self.page.wait_for_timeout(300)
        try:
            self.transaction_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def search_table(self, query: str) -> None:
        """Fill search input and wait for DataTables filtering."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(400)

    def clear_search(self) -> None:
        """Clear search input and wait for DataTables to restore."""
        self.search_input.fill("")
        self.page.wait_for_timeout(400)

    def select_length(self, length: str) -> None:
        """Select number of entries to display from the length dropdown."""
        self.length_dropdown.select_option(value=length)
        self.page.wait_for_timeout(400)

    def get_row_count(self) -> int:
        """Return the number of data rows currently rendered."""
        return self.table_rows.count()

    def get_table_info_text(self) -> str:
        """Return the DataTables info text."""
        return self.table_info.inner_text().strip()

