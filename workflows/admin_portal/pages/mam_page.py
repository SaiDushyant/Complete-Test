"""
Admin Portal Manage MAM Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class MamPage(BasePage):
    """Page object for Admin Manage MAM management, requests, and table actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header elements
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

        # Top action button & requests modal
        self.mam_requests_button = page.locator("#showMamMasterRequests")
        self.mam_request_count = page.locator("#mamMasterRequestCount")
        self.mam_requests_modal = page.locator("#mamRequestsModal")
        self.mam_requests_modal_title = page.locator("#mamRequestsModalLabel")
        self.mam_requests_table = page.locator("#mamMasterRequestsTable")
        self.mam_requests_table_headers = page.locator("#mamMasterRequestsTable thead th")
        self.mam_requests_table_rows = page.locator("#mamMasterRequestsTable tbody tr")
        self.mam_requests_approve_buttons = page.locator(
            "#mamMasterRequestsTable button.btnApproveCopyMaster, "
            "#mamMasterRequestsTable button.btnApproveMAMMaster, "
            "#mamMasterRequestsTable button:has-text('Approve')"
        )
        self.mam_requests_reject_buttons = page.locator(
            "#mamMasterRequestsTable button.btnRejectCopyMaster, "
            "#mamMasterRequestsTable button.btnRejectMAMMaster, "
            "#mamMasterRequestsTable button:has-text('Reject')"
        )
        self.mam_requests_refresh_button = page.locator(
            "#refreshMamMasterRequests, #refreshCopyMasterRequests, #mamRequestsModal button:has-text('Refresh')"
        )
        self.mam_requests_close_button = page.locator(
            "#mamRequestsModal .modal-footer button:has-text('Close'), "
            "#mamRequestsModal button:has-text('Close'), "
            "#mamRequestsModal [data-bs-dismiss='modal'], "
            "#mamRequestsModal .ux-card-close"
        )

        # DataTable card & controls
        self.table_card = page.locator(".card.mam-table-card")
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

        # Edit MAM Details Modal (#myModal)
        self.edit_modal = page.locator("#myModal")
        self.edit_modal_title = page.locator("#myModal .modal-title, #myModal #myModalLabel")
        self.edit_name_input = page.locator("#myModal #name")
        self.edit_submit_button = page.locator("#myModal #formSubmit")
        self.edit_modal_close_button = page.locator(
            "#myModal button[data-bs-dismiss='modal'], #myModal .ux-card-close, #myModal button:has-text('Close')"
        )

        # Edit MAM Share Modal (#myModal_mam)
        self.mam_share_modal = page.locator("#myModal_mam")
        self.mam_share_title = page.locator("#myModal_mam .modal-title, #myModal_mam #myModalLabel")
        self.mam_share_input = page.locator("#myModal_mam #mam_share")
        self.mam_share_submit_button = page.locator("#myModal_mam #formSubmit, #myModal_mam button:has-text('Save')")
        self.mam_share_close_button = page.locator(
            "#myModal_mam button[data-bs-dismiss='modal'], #myModal_mam .ux-card-close, #myModal_mam button:has-text('Close')"
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
        self.edit_mam_share_buttons = page.locator(".btnEdit_mam")
        self.unfollow_buttons = page.locator("button.btnMamUnfollow")
        self.alert_box = page.locator(".jconfirm-box")
        self.alert_content = page.locator(".jconfirm-box .jconfirm-content")
        self.alert_ok_button = page.locator(".jconfirm-box button:has-text('Ok'), .jconfirm-box .btn-default")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Manage MAM page and wait for loading."""
        mam_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/manageMAM"
        )
        self.goto(mam_url)
        self.wait_for_table_loaded()

    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        """Wait for the AJAX loader to disappear and DataTable to initialize."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        try:
            self.datatable.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def is_mam_displayed(self) -> bool:
        """Verify the Manage MAM heading and table are displayed."""
        return self.page_title.is_visible() and self.datatable.is_visible()

    def search_mam(self, query: str) -> None:
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

    def get_request_badge_count(self) -> int:
        """Return numeric count on the MAM Requests badge."""
        text = self.mam_request_count.inner_text().strip()
        return int(text) if text.isdigit() else 0

    def open_mam_requests(self) -> None:
        """Click the MAM Requests button to open modal."""
        self.mam_requests_button.click()
        self.mam_requests_modal.wait_for(state="visible", timeout=5000)

    def close_mam_requests(self) -> None:
        """Close the MAM Requests modal safely."""
        try:
            btn = self.mam_requests_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(400)
        self.page.evaluate("""() => {
            const el = document.getElementById('mamRequestsModal');
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
        self.page.wait_for_timeout(500)
        try:
            self.mam_requests_modal.wait_for(state="hidden", timeout=5000)
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

    def toggle_responsive_row(self, index: int = 0) -> None:
        """Click the responsive dtr-control toggle on a row."""
        self.dtr_controls.nth(index).click()

    def open_edit_mam_modal(self, index: int = 0) -> None:
        """Click the MAM name edit pencil button on a row."""
        self.edit_name_buttons.nth(index).click()
        self.edit_modal.wait_for(state="visible", timeout=5000)

    def close_edit_mam_modal(self) -> None:
        """Safely dismiss the edit MAM details modal."""
        try:
            btn = self.edit_modal_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('myModal');
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
            self.edit_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def open_edit_mam_share_modal(self, index: int = 0) -> None:
        """Click the edit MAM share pencil icon inside the followers subtable."""
        self.edit_mam_share_buttons.nth(index).click()
        self.mam_share_modal.wait_for(state="visible", timeout=5000)

    def close_edit_mam_share_modal(self) -> None:
        """Safely dismiss the edit MAM share modal."""
        try:
            btn = self.mam_share_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('myModal_mam');
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
            self.mam_share_modal.wait_for(state="hidden", timeout=5000)
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
