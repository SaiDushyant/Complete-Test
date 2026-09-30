"""
Admin Portal Role Permission Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class RolePermissionPage(BasePage):
    """Page object for Admin Role Permission topbar, actions, modals, and table."""

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

        # Page Actions & Hidden Permissions
        self.page_actions = page.locator(".role-page-actions")
        self.add_role_button = page.locator("#addNew")
        self.edit_role_perm_hidden = page.locator("#editrolePermission")
        self.delete_role_perm_hidden = page.locator("#deleterolePermission")
        self.edit_perm_hidden = page.locator("#editPermission")

        # Table Card & DataTable Controls
        self.table_card = page.locator(".role-table-card")
        self.table_wrapper = page.locator("#datatable_wrapper")
        self.table = page.locator("#datatable")
        self.table_headers = page.locator("#datatable thead th")
        self.role_rows = page.locator("#datatable tbody tr:not(:has(.dataTables_empty))")
        self.empty_row = page.locator("#datatable tbody tr:has(.dataTables_empty), #datatable tbody tr:has-text('No matching records found')")
        self.length_select = page.locator("select[name='datatable_length']")
        self.search_input = page.locator("#datatable_filter input")
        self.table_info = page.locator("#datatable_info")

        # Modals & Dialogs
        self.role_modal = page.locator("#myModal")
        self.role_modal_title = page.locator("#myModal .modal-title")
        self.role_modal_input = page.locator("#myModal input[name='role_name']")
        self.role_modal_close = page.locator("#myModal .close, #myModal [data-bs-dismiss='modal'], #myModal [data-dismiss='modal'], #myModal button:has-text('Close')")
        self.role_modal_save = page.locator("#myModal button:has-text('Save')")

        self.swal_popup = page.locator(".swal2-popup")
        self.swal_title = page.locator(".swal2-title")
        self.swal_cancel_button = page.locator("button.swal2-cancel, button:has-text('No, cancel!')")
        self.swal_confirm_button = page.locator("button.swal2-confirm, button:has-text('Yes, delete it!')")

        # Row Action Controls
        self.edit_name_buttons = page.locator("a.btnNameEdit")
        self.edit_permission_links = page.locator("#datatable tbody tr td a:has(i.mdi-book-edit-outline)")
        self.delete_buttons = page.locator("a.BtnDelete")

        # Pagination
        self.pagination = page.locator("#datatable_paginate")
        self.previous_page_button = page.locator("#datatable_paginate li#datatable_previous")
        self.next_page_button = page.locator("#datatable_paginate li#datatable_next")
        self.active_page_button = page.locator("#datatable_paginate li.active")

        # Loader
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Role Permission page."""
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/rolePermission"
        )
        if "/admin/Controlbase/rolePermission" not in self.page.url:
            self.goto(url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title/table to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        try:
            self.role_rows.first.wait_for(state="visible", timeout=timeout)
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

    def search_role(self, query: str) -> None:
        """Type search query into table filter."""
        self.search_input.click()
        self.search_input.fill("")
        self.search_input.press_sequentially(query, delay=40)
        self.search_input.press("Enter")
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear search filter."""
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.page.wait_for_timeout(500)

    def select_page_length(self, length: str) -> None:
        """Change visible entries per page."""
        self.length_select.select_option(length)
        self.page.wait_for_timeout(400)
