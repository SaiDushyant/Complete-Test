"""
Admin Portal User Management Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class UserManagementPage(BasePage):
    """Page object for Admin User Management topbar, actions, filters, and tables."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar elements (.navbar-header)
        self.topbar = page.locator("#page-topbar")
        self.navbar_header = page.locator(".navbar-header")
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
        self.notification_empty_text = page.locator(".notification-list p")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_initials = page.locator("#page-header-user-dropdown .header-profile-initials")
        self.profile_topbar_name = page.locator("#page-header-user-dropdown span.fw-medium")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Top Action Buttons (.user-page-actions)
        self.page_actions_container = page.locator(".user-page-actions")
        self.create_account_button = page.locator("#createAccount")
        self.add_user_button = page.locator("#addNew")
        self.refresh_button = page.locator("#refresh")
        self.refresh_icon = page.locator("#refresh svg.feather-refresh-ccw")

        # Hidden Permission Inputs
        self.edit_manage_user_input = page.locator("#editManageUser")
        self.delete_manage_user_input = page.locator("#deleteManageUser")
        self.change_balance_input = page.locator("#changeBalance")
        self.change_book_input = page.locator("#changeBook")
        self.change_manage_user_input = page.locator("#changeManageUser")
        self.cent_switch_enabled_input = page.locator("#centSwitchEnabled")

        # Modals triggered by actions
        self.create_account_modal = page.locator("#createAccountModal")
        self.create_account_modal_title = page.locator("#createAccountModal .modal-title")
        self.create_account_modal_close = page.locator(
            "#createAccountModal .ux-actions button:has-text('Close'), #createAccountModal .ux-card-close"
        )

        self.user_add_modal = page.locator("#userAddModal")
        self.user_add_modal_title = page.locator("#userAddModal .modal-title")
        self.user_add_modal_close = page.locator(
            "#userAddModal .ux-actions button:has-text('Close'), #userAddModal .ux-card-close"
        )

        # DataTable Card & Controls (.user-table-card)
        self.table_card = page.locator(".card.user-table-card")
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.length_dropdown = page.locator("#datatable_length select")
        self.export_buttons = page.locator(".dt-buttons button")
        self.csv_button = page.locator(".dt-buttons button.buttons-csv")
        self.pdf_button = page.locator(".dt-buttons button.buttons-pdf")
        self.excel_button = page.locator(".dt-buttons button.buttons-excel")

        # Date Filters
        self.date_filters_container = page.locator(".user-date-filters")
        self.date_from = page.locator("#from")
        self.date_to = page.locator("#to")
        self.apply_button = page.locator("#apply")
        self.clear_button = page.locator("#clear")

        # Search & Table
        self.search_input = page.locator("#datatable_filter input")
        self.users_table = page.locator("#datatable")
        self.table_headers = page.locator("#datatable thead th")
        self.user_rows = page.locator("#datatable tbody tr:not(:has(.dataTables_empty))")
        self.empty_state_cell = page.locator("#datatable tbody td.dataTables_empty")

        # Row dropdowns
        self.email_verification_selects = page.locator("select.userEmailVerification")
        self.doc_verification_selects = page.locator("select.userDocumentVerification")
        self.account_type_selects = page.locator("select.updateAccountType")
        self.user_status_selects = page.locator("select.updateUserStatus")
        self.user_book_selects = page.locator("select.userBook")

        # Pagination & Info
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
        """Navigate to the Admin User Management page."""
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/user"
        )
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
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        try:
            self.user_rows.first.wait_for(state="visible", timeout=timeout)
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

    def open_create_account_modal(self) -> None:
        """Click Create Account button and wait for modal to display."""
        self.create_account_button.click()
        self.create_account_modal.wait_for(state="visible", timeout=5000)
        self.page.wait_for_timeout(300)

    def close_create_account_modal(self) -> None:
        """Close the Create Account modal."""
        close_btn = self.create_account_modal.locator(".ux-actions button:has-text('Close'), .ux-card-close").first
        if close_btn.is_visible():
            close_btn.click()
        self.page.wait_for_timeout(500)
        try:
            self.create_account_modal.wait_for(state="hidden", timeout=3000)
        except Exception:
            self.page.evaluate("() => { if (window.jQuery) { window.jQuery('#createAccountModal').modal('hide'); } }")
            self.page.wait_for_timeout(300)

    def open_add_user_modal(self) -> None:
        """Click Add User button and wait for modal to display."""
        self.add_user_button.click()
        self.user_add_modal.wait_for(state="visible", timeout=5000)
        self.page.wait_for_timeout(300)

    def close_add_user_modal(self) -> None:
        """Close the Add User modal."""
        close_btn = self.user_add_modal.locator(".ux-actions button:has-text('Close'), .ux-card-close").first
        if close_btn.is_visible():
            close_btn.click()
        self.page.wait_for_timeout(500)
        try:
            self.user_add_modal.wait_for(state="hidden", timeout=3000)
        except Exception:
            self.page.evaluate("() => { if (window.jQuery) { window.jQuery('#userAddModal').modal('hide'); } }")
            self.page.wait_for_timeout(300)

    def click_refresh(self) -> None:
        """Click the refresh button."""
        self.refresh_button.click()
        self.page.wait_for_timeout(500)

    def select_page_length(self, length: str) -> None:
        """Select the number of entries from the dropdown."""
        self.length_dropdown.select_option(str(length))
        try:
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def search_user(self, query: str) -> None:
        """Search users by name or email."""
        self.search_input.fill(query)
        self.search_input.press("Enter")
        try:
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(600)

    def clear_search(self) -> None:
        """Clear search input."""
        self.search_input.fill("")
        self.search_input.press("Enter")
        try:
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(600)

    def get_user_count(self) -> int:
        """Return the number of users displayed in the table."""
        return self.user_rows.count()

    def get_table_info_text(self) -> str:
        """Return the table pagination status text."""
        return self.table_info.inner_text().strip()

    def click_next_page(self) -> None:
        """Click the Next pagination button."""
        self.paginate_next.click()
        try:
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_previous_page(self) -> None:
        """Click the Previous pagination button."""
        self.paginate_previous.click()
        try:
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
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
            self.page.locator("#datatable_processing").wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def get_active_page_number(self) -> str:
        """Get the current active page number text."""
        return self.active_page.inner_text().strip()

    def expand_row(self, row_index: int = 0) -> None:
        """Click the responsive dtr-control on a row to expand collapsed details."""
        control = self.user_rows.nth(row_index).locator(".dtr-control")
        control.click()
        self.page.wait_for_timeout(300)