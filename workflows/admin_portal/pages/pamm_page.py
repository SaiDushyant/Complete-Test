"""
Admin Portal Manage PAMM Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class PammPage(BasePage):
    """Page object for Admin Manage PAMM topbar, table, and actions."""

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

        # Top action button & PAMM requests modal
        self.pamm_requests_button = page.locator("#showPammMasterRequests")
        self.pamm_request_count = page.locator("#pammMasterRequestCount")
        self.pamm_requests_modal = page.locator("#pammRequestsModal")
        self.pamm_requests_modal_title = page.locator("#pammRequestsModal .modal-title, #pammRequestsModalLabel")
        self.pamm_requests_table = page.locator("#pammMasterRequestsTable, #pammRequestsModal table")
        self.pamm_requests_table_headers = page.locator("#pammMasterRequestsTable thead th, #pammRequestsModal table thead th")
        self.pamm_requests_table_rows = page.locator("#pammMasterRequestsTable tbody tr, #pammRequestsModal table tbody tr")
        self.pamm_requests_approve_buttons = page.locator("button.btnApprovePammMaster")
        self.pamm_requests_reject_buttons = page.locator("button.btnRejectPammMaster")
        self.pamm_requests_refresh_button = page.locator("#refreshPammMasterRequests")
        self.pamm_requests_close_button = page.locator(
            "#pammRequestsModal button:has-text('Close'), #pammRequestsModal .ux-card-close, #pammRequestsModal [data-bs-dismiss='modal']"
        )

        # Main Table Card & DataTable controls
        self.table_card = page.locator(".card.pamm-table-card")
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.length_dropdown = page.locator(
            "#datatable_length select, select[name='datatable_length']"
        )
        self.search_input = page.locator(
            "#datatable_filter input, input[type='search'][aria-controls='datatable']"
        )

        # Main DataTable
        self.datatable = page.locator("#datatable")
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr:not(.report_user_row)")
        self.action_buttons = page.locator("#datatable tbody tr a.btnReport")
        self.edit_name_buttons = page.locator("#datatable tbody tr .btnNameEdit, #datatable tbody tr a.btnNameEdit")

        # Edit PAMM Name Modal (#myModalName)
        self.edit_name_modal = page.locator("#myModalName")
        self.edit_name_modal_title = page.locator("#myModalName .modal-title, #myModalName #myModalNameLabel")
        self.edit_name_input = page.locator("#myModalName #name")
        self.edit_name_submit_button = page.locator("#myModalName #formSubmitName, #myModalName button:has-text('Save')")
        self.edit_name_close_button = page.locator(
            "#myModalName button[data-bs-dismiss='modal'], #myModalName .ux-card-close, #myModalName button:has-text('Close')"
        )

        # Edit PAMM Share Modal (#myModal)
        self.pamm_share_modal = page.locator("#myModal")
        self.pamm_share_modal_title = page.locator("#myModal .modal-title, #myModal #myModalLabel")
        self.pamm_share_input = page.locator("#myModal #pamm_share")
        self.pamm_share_submit_button = page.locator("#myModal #formSubmit, #myModal button:has-text('Save')")
        self.pamm_share_close_button = page.locator(
            "#myModal button[data-bs-dismiss='modal'], #myModal .ux-card-close, #myModal button:has-text('Close')"
        )

        # DataTable status & pagination
        self.datatable_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_items = page.locator(
            "#datatable_paginate .pagination li.page-item"
        )
        self.pagination_active = page.locator(
            "#datatable_paginate .pagination li.page-item.active"
        )
        self.pagination_previous = page.locator("#datatable_previous")
        self.pagination_next = page.locator("#datatable_next")
        self.dtr_controls = page.locator("#datatable tbody tr td.dtr-control")

        # Followers Sub-table, Unfollow action & Alert Box
        self.followers_subtable = page.locator("table.report-inner-table")
        self.followers_subtable_headers = page.locator("table.report-inner-table thead th")
        self.followers_subtable_rows = page.locator("table.report-inner-table tbody tr")
        self.unfollow_buttons = page.locator("button.btnPammUnfollow, button:has-text('Unfollow')")
        self.alert_box = page.locator(".jconfirm-box")
        self.alert_content = page.locator(".jconfirm-box .jconfirm-content")
        self.alert_ok_button = page.locator(".jconfirm-box button:has-text('Ok'), .jconfirm-box .btn-default")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Manage PAMM page and wait for loading."""
        pamm_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/managePAMM"
        )
        self.goto(pamm_url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for page loader and topbar title to be ready."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        try:
            self.datatable.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        try:
            self.table_rows.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(400)

    def is_pamm_displayed(self) -> bool:
        """Verify the Manage PAMM heading and table are displayed."""
        return self.page_title.is_visible() and self.datatable.is_visible()

    def get_request_badge_count(self) -> int:
        """Return numeric count on the PAMM Requests badge."""
        text = self.pamm_request_count.inner_text().strip()
        return int(text) if text.isdigit() else 0

    def open_pamm_requests(self) -> None:
        """Click the PAMM Requests button to open modal."""
        self.pamm_requests_button.scroll_into_view_if_needed()
        self.pamm_requests_button.click()
        self.pamm_requests_modal.wait_for(state="visible", timeout=10000)

    def close_pamm_requests(self) -> None:
        """Close the PAMM Requests modal safely."""
        try:
            btn = self.pamm_requests_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('pammRequestsModal');
            if (el) {
                if (window.bootstrap && window.bootstrap.Modal) {
                    const inst = window.bootstrap.Modal.getInstance(el);
                    if (inst) inst.hide();
                }
                if (window.jQuery) {
                    window.jQuery(el).modal('hide');
                }
            }
        }""")
        self.page.wait_for_timeout(300)
        try:
            self.pamm_requests_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def search_pamm(self, query: str) -> None:
        """Filter the table rows using the search box."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear the search input."""
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return the number of data rows currently rendered."""
        return self.table_rows.count()

    def open_edit_pamm_name_modal(self, index: int = 0) -> None:
        """Click the PAMM name edit pencil button on a row."""
        btn = self.edit_name_buttons.nth(index)
        btn.scroll_into_view_if_needed()
        btn.click()
        self.edit_name_modal.wait_for(state="visible", timeout=10000)

    def close_edit_pamm_name_modal(self) -> None:
        """Safely dismiss the edit PAMM details modal."""
        try:
            btn = self.edit_name_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('myModalName');
            if (el) {
                if (window.bootstrap && window.bootstrap.Modal) {
                    const inst = window.bootstrap.Modal.getInstance(el);
                    if (inst) inst.hide();
                }
                if (window.jQuery) {
                    window.jQuery(el).modal('hide');
                }
            }
        }""")
        self.page.wait_for_timeout(300)
        try:
            self.edit_name_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def select_page_length(self, length: str) -> None:
        """Change the page length dropdown selection."""
        self.length_dropdown.select_option(length)
        self.page.wait_for_timeout(500)

    def dismiss_alert(self) -> None:
        """Click the Ok button on an alert dialog."""
        if self.alert_ok_button.is_visible():
            self.alert_ok_button.click()
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
        """Return the data-layout-mode attribute of body."""
        return self.page.locator("body").get_attribute("data-layout-mode")
