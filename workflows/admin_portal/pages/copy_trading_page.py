"""
Admin Portal Copy Trading Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class CopyTradingPage(BasePage):
    """Page object for Admin Copy Trading management and actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header elements
        self.page_title = page.locator(".topbar-page-title")
        self.brand_logo = page.locator(".navbar-brand-box a.logo.admin-brand-logo")
        self.brand_logo_images = page.locator(".navbar-brand-box img")
        self.menu_button = page.locator("#vertical-menu-btn")
        self.theme_toggle = page.locator("#admin-theme-toggle")
        self.notification_button = page.locator("#page-header-notifications-dropdown")
        self.notification_count = page.locator("#notification-count")
        self.notification_menu = page.locator(".notification-menu")
        self.mark_all_read = page.locator("#markAllRead")
        self.notification_items = page.locator(".notification-item")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Top action button & modal
        self.client_portal_requests_button = page.locator("#showCopyMasterRequests")
        self.copy_master_request_count = page.locator("#copyMasterRequestCount")
        self.copy_requests_modal = page.locator("#copyRequestsModal")
        self.copy_requests_modal_title = page.locator("#copyRequestsModalLabel")
        self.copy_requests_table = page.locator("#copyMasterRequestsTable")
        self.copy_requests_table_headers = page.locator("#copyMasterRequestsTable thead th")
        self.copy_requests_table_rows = page.locator("#copyMasterRequestsTable tbody tr")
        self.copy_requests_approve_buttons = page.locator(
            "#copyMasterRequestsTable button.btnApproveCopyMaster"
        )
        self.copy_requests_reject_buttons = page.locator(
            "#copyMasterRequestsTable button.btnRejectCopyMaster"
        )
        self.copy_requests_refresh_button = page.locator("#refreshCopyMasterRequests")
        self.copy_requests_close_button = page.locator(
            "#copyRequestsModal .modal-footer button:has-text('Close'), #copyRequestsModal .ux-card-close"
        )

        # DataTable controls
        self.length_dropdown = page.locator("select[name='datatable_length']")
        self.search_input = page.locator(
            "#datatable_filter input, input[type='search'][aria-controls='datatable']"
        )

        # Main DataTable
        self.datatable = page.locator("#datatable")
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr:not(.report_user_row)")
        self.action_buttons = page.locator("#datatable tbody tr a.btnReport")
        self.edit_name_buttons = page.locator("#datatable tbody tr button.btnNameEdit")

        # Edit Trader Modal
        self.edit_modal = page.locator("#myModal")
        self.edit_name_input = page.locator("#name")
        self.edit_fee_input = page.locator("#copy_trading_fee")
        self.edit_submit_button = page.locator("#formSubmit")
        self.edit_modal_close_button = page.locator(
            "#myModal button[data-bs-dismiss='modal'], #myModal .btn-close"
        )

        # DataTable status & pagination
        self.datatable_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_items = page.locator(
            "#datatable_paginate .pagination li.page-item"
        )
        self.dtr_controls = page.locator("#datatable tbody tr td.dtr-control")
        self.child_rows = page.locator("#datatable tbody tr.child")

        # Followers Sub-table & Alert Box
        self.followers_subtable = page.locator("table.report-inner-table")
        self.alert_box = page.locator(".jconfirm-box")
        self.alert_ok_button = page.locator(".jconfirm-box button:has-text('Ok')")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Copy Trading page and wait for AJAX to load."""
        copy_trading_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/follow"
        )
        self.goto(copy_trading_url)
        self.wait_for_table_loaded()

    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        """Wait for the AJAX loader to disappear and DataTable to initialize."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.datatable.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

    def is_copy_trading_displayed(self) -> bool:
        """Verify the Copy Trading heading and table are displayed."""
        return (
            self.page_title.is_visible()
            and self.datatable.is_visible()
        )

    def search_trader(self, query: str) -> None:
        """Filter the table rows using the search box."""
        self.search_input.fill(query)

    def get_row_count(self) -> int:
        """Return the number of data rows currently rendered."""
        return self.table_rows.count()

    def get_request_badge_count(self) -> int:
        """Return numeric count on the Client Portal Requests badge."""
        text = self.copy_master_request_count.inner_text().strip()
        return int(text) if text.isdigit() else 0

    def open_client_portal_requests(self) -> None:
        """Click the Client Portal Requests button to open modal."""
        self.client_portal_requests_button.click()

    def close_client_portal_requests(self) -> None:
        """Close the Client Portal Requests modal."""
        if self.copy_requests_close_button.first.is_visible():
            self.copy_requests_close_button.first.click()
        else:
            self.page.evaluate("$('#copyRequestsModal').modal('hide')")
        try:
            self.copy_requests_modal.wait_for(state="hidden", timeout=3000)
        except Exception:
            pass


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

    def open_edit_trader_modal(self, index: int = 0) -> None:
        """Click the edit pencil button on a trader row."""
        self.edit_name_buttons.nth(index).click()

    def close_edit_trader_modal(self) -> None:
        """Close the edit trader modal safely."""
        self.page.wait_for_timeout(500)
        self.page.evaluate("""() => {
            const el = document.getElementById('myModal');
            if (window.bootstrap && window.bootstrap.Modal) {
                const inst = window.bootstrap.Modal.getInstance(el);
                if (inst) {
                    inst.hide();
                    return;
                }
            }
            if (window.jQuery) {
                window.jQuery(el).modal('hide');
            }
        }""")
        try:
            self.edit_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass




    def toggle_responsive_row(self, index: int = 0) -> None:
        """Click the responsive dtr-control toggle on a row."""
        self.dtr_controls.nth(index).click()


