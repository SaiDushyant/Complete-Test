"""
Admin Portal User Document Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class UserDocumentPage(BasePage):
    """Page object for Admin User Document topbar, actions, filters, modals, and tables."""

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

        # Page Actions & Hidden Permission Flags
        self.page_actions = page.locator(".user-document-page-actions")
        self.add_document_button = page.locator("#addNew")
        self.edit_user_doc_hidden = page.locator("#editUserDoc")
        self.delete_user_doc_hidden = page.locator("#deleteUserDoc")
        self.verify_user_doc_hidden = page.locator("#verifyUserDoc")
        self.remarks_user_doc_hidden = page.locator("#remarksUserDoc")

        # Table Card & Controls
        self.table_card = page.locator(".user-document-table-card")
        self.table_wrapper = page.locator("#datatable_wrapper")
        self.table = page.locator("#datatable")
        self.table_headers = page.locator("#datatable thead th")
        self.document_rows = page.locator("#datatable tbody tr:not(:has(.dataTables_empty))")
        self.empty_row = page.locator("#datatable tbody tr:has(.dataTables_empty), #datatable tbody tr:has-text('No data available in table')")
        self.length_select = page.locator("select[name='datatable_length']")
        self.table_info = page.locator("#datatable_info")
        self.processing = page.locator("#datatable_processing")

        # Date Filters & Search
        self.from_date_input = page.locator("#from")
        self.to_date_input = page.locator("#to")
        self.apply_button = page.locator("#apply")
        self.clear_button = page.locator("#clear")
        self.search_input = page.locator("#datatable_filter input")

        # Row Action Controls
        self.verification_dropdowns = page.locator("select.userDocumentVerification")
        self.remark_buttons = page.locator("a.btnRemark")
        self.edit_buttons = page.locator("a.btnEdit")
        self.delete_buttons = page.locator("a.BtnDelete")
        self.responsive_controls = page.locator("#datatable tbody tr td.dtr-control")

        # Modals
        self.document_modal = page.locator("#myModal")
        self.document_modal_title = page.locator("#myModal .modal-title")
        self.document_modal_close = page.locator("#myModal .ux-card-close, #myModal button:has-text('Close')")
        
        self.remark_modal = page.locator("#remarkModal")
        self.remark_modal_title = page.locator("#remarkModal .modal-title")
        self.remark_modal_textarea = page.locator("#remarkModal #remark")
        self.remark_modal_close = page.locator("#remarkModal .ux-card-close, #remarkModal button:has-text('Close')")
        
        self.delete_modal = page.locator("#deleteModal")
        self.delete_modal_title = page.locator("#deleteModal .modal-title")
        self.delete_modal_close = page.locator("#deleteModal .ux-card-close, #deleteModal button:has-text('Close')")

        self.confirm_dialog = page.locator(".jconfirm-box")
        self.confirm_dialog_close = page.locator(".jconfirm-box .btn, .jconfirm-box button")

        # Pagination
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_items = page.locator("#datatable_paginate .pagination li")
        self.previous_page_button = page.locator("#datatable_paginate li#datatable_previous")
        self.next_page_button = page.locator("#datatable_paginate li#datatable_next")
        self.active_page_button = page.locator("#datatable_paginate li.active")

        # Loader
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin User Document page with standard wide desktop viewport."""
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/userDocument"
        )
        if "/admin/Controlbase/userDocument" not in self.page.url:
            self.goto(url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear, page title to be visible, and table to load."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.wait_for_table_loaded(timeout=timeout)
        try:
            self.document_rows.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(300)

    def wait_for_table_loaded(self, timeout: int = 10000) -> None:
        """Wait for the DataTables processing indicator to disappear."""
        try:
            self.processing.wait_for(state="hidden", timeout=timeout)
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

    def select_page_length(self, length: str) -> None:
        """Change visible entries per page."""
        self.length_select.select_option(length)
        self.wait_for_table_loaded()

    def search_document(self, query: str) -> None:
        """Type search query into table filter and wait for table to update."""
        self.search_input.click()
        self.search_input.fill("")
        self.search_input.press_sequentially(query, delay=40)
        self.search_input.press("Enter")
        self.wait_for_table_loaded()

    def clear_search(self) -> None:
        """Clear search filter and wait for table to reload."""
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.wait_for_table_loaded()

    def filter_by_date(self, from_date: str, to_date: str) -> None:
        """Apply date range filter."""
        self.from_date_input.fill(from_date)
        self.to_date_input.fill(to_date)
        self.apply_button.click()
        self.wait_for_table_loaded()

    def clear_date_filter(self) -> None:
        """Reset date range filter."""
        self.clear_button.click()
        self.wait_for_table_loaded()

    def click_page_number(self, page_num: int | str) -> None:
        """Click a specific pagination page link."""
        self.page.locator(f"#datatable_paginate a.page-link:has-text('{page_num}')").click()
        self.wait_for_table_loaded()

    def click_next_page(self) -> None:
        """Click Next pagination link."""
        self.next_page_button.locator("a").click()
        self.wait_for_table_loaded()

    def click_previous_page(self) -> None:
        """Click Previous pagination link."""
        self.previous_page_button.locator("a").click()
        self.wait_for_table_loaded()
