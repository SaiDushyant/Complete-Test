"""
Admin Portal Private Copy Trading (Manage Private Copier) Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class PrivateCopyTradingPage(BasePage):
    """Page object for Admin Private Copy Trading (Manage Private Copier)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header navigation elements
        self.page_title = page.locator(".topbar-page-title")
        self.brand_logo = page.locator(".navbar-brand-box a.logo.admin-brand-logo")
        self.brand_logo_images = page.locator(".navbar-brand-box img")
        self.menu_button = page.locator("#vertical-menu-btn")
        self.theme_toggle = page.locator("#admin-theme-toggle")
        self.notification_button = page.locator("#page-header-notifications-dropdown")
        self.notification_count = page.locator("#notification-count")
        self.notification_menu = page.locator(".notification-menu")
        self.mark_all_read = page.locator("#markAllRead")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Top action button & modals
        self.create_copier_button = page.locator(
            "#addNewCopier, .private-copier-page-actions a#addNewCopier, a:has-text('Create Copier')"
        )
        self.create_copier_modal = page.locator("#myModal")
        self.create_copier_modal_title = page.locator("#myModalLabel")
        self.create_copier_form = page.locator("#formModal")
        self.create_copier_close_button = page.locator(
            "#myModal [data-bs-dismiss='modal'], #myModal [data-dismiss='modal'], #myModal .ux-card-close, #myModal button:has-text('Close')"
        )

        # Slave Accounts modal
        self.private_slaves_modal = page.locator("#privateSlavesModal")
        self.private_slaves_modal_title = page.locator("#privateSlavesModalLabel")
        self.private_slaves_modal_body = page.locator("#privateSlavesModalBody")
        self.private_slaves_close_button = page.locator(
            "#privateSlavesModal [data-bs-dismiss='modal'], #privateSlavesModal [data-dismiss='modal'], #privateSlavesModal .ux-card-close, #privateSlavesModal button:has-text('Close')"
        )

        # DataTable controls
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
        self.table_rows = page.locator("#datatable tbody tr:not(.child)")
        self.slaves_summary = page.locator("#datatable tbody tr .private-slave-summary")
        self.slaves_preview = page.locator("#datatable tbody tr .private-slave-preview")
        self.view_slaves_buttons = page.locator(
            "#datatable tbody tr button.btnPrivateSlaves"
        )
        self.dtr_controls = page.locator("#datatable tbody tr td.dtr-control")
        self.edit_buttons = page.locator("#datatable tbody tr .btnEdit")
        self.delete_buttons = page.locator("#datatable tbody tr .btnDelete")

        # DataTable status & pagination
        self.datatable_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_items = page.locator(
            "#datatable_paginate .pagination li.page-item"
        )
        self.pagination_previous = page.locator("#datatable_previous")
        self.pagination_next = page.locator("#datatable_next")
        self.pagination_active = page.locator(
            "#datatable_paginate .pagination li.page-item.active"
        )

        # Create/Edit Form Fields
        self.master_picker_wrap = page.locator("#masterPickerWrap")
        self.master_search_input = page.locator("#masterSearch")
        self.master_uid_input = page.locator("#masterUid")
        self.master_search_results = page.locator("#masterSearchResults")
        self.master_feedback = page.locator(".masterFeedback")
        self.slave_picker_wrap = page.locator("#slavePickerWrap")
        self.slave_search_input = page.locator("#slaveSearch")
        self.slave_search_results = page.locator("#slaveSearchResults")
        self.selected_slaves_wrap = page.locator("#selectedSlaves")
        self.slave_feedback = page.locator(".slaveFeedback")
        self.copy_type_dropdown = page.locator("#tradeMethod")
        self.multiplier_wrap = page.locator("#multiplierWrap")
        self.multiplier_input = page.locator("#multiplierValue")
        self.direction_normal_radio = page.locator("#directionNormal")
        self.direction_reverse_radio = page.locator("#directionReverse")
        self.form_save_button = page.locator("#formSubmit")

        # Slave Accounts List Elements
        self.slave_rows = page.locator("#privateSlavesModalBody .private-slave-row")
        self.slave_indices = page.locator("#privateSlavesModalBody .private-slave-index")

        # Confirmation Dialog
        self.alert_box = page.locator(".jconfirm-box")
        self.alert_cancel_button = page.locator(
            ".jconfirm-box button:has-text('Cancel'), .jconfirm-box .btn-default"
        )

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Private Copy Trading page and wait for loading."""
        private_copy_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/managePrivateCopier"
        )
        self.goto(private_copy_url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for loader to disappear and main topbar to be ready."""
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

    def is_page_displayed(self) -> bool:
        """Verify the Manage Private Copier heading is displayed."""
        return self.page_title.is_visible()

    def search(self, query: str) -> None:
        """Filter the table rows using the search box."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear the search input to reset the table rows."""
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return the number of data rows currently rendered."""
        return self.table_rows.count()

    def get_table_headers(self) -> list[str]:
        """Return non-empty column header texts in lowercase."""
        return [
            th.strip().casefold()
            for th in self.table_headers.all_inner_texts()
            if th.strip()
        ]

    def select_page_length(self, length: str) -> None:
        """Select number of entries to display from the length dropdown."""
        self.length_dropdown.select_option(str(length))
        self.page.wait_for_timeout(500)

    def open_create_copier_modal(self) -> None:
        """Click the Create Copier button to open the form modal."""
        self.create_copier_button.click()
        self.create_copier_modal.wait_for(state="visible", timeout=5000)

    def close_create_copier_modal(self) -> None:
        """Close the Create Copier form modal safely."""
        try:
            close_btn = self.create_copier_modal.locator(
                ".modal-footer button:has-text('Close'), button:has-text('Close'), .ux-card-close, [data-bs-dismiss='modal']"
            ).first
            if close_btn.is_visible():
                close_btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(400)
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
        self.page.wait_for_timeout(600)
        try:
            self.create_copier_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def open_view_slaves_modal(self, index: int = 0) -> None:
        """Click the View Slaves button on the specified row."""
        self.view_slaves_buttons.nth(index).click()
        self.private_slaves_modal.wait_for(state="visible", timeout=5000)

    def close_view_slaves_modal(self) -> None:
        """Close the Slave Accounts modal safely."""
        try:
            close_btn = self.private_slaves_modal.locator(
                ".modal-footer button:has-text('Close'), button:has-text('Close'), .ux-card-close, [data-bs-dismiss='modal']"
            ).first
            if close_btn.is_visible():
                close_btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(400)
        self.page.evaluate("""() => {
            const el = document.getElementById('privateSlavesModal');
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
        self.page.wait_for_timeout(600)
        try:
            self.private_slaves_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def toggle_responsive_row(self, index: int = 0) -> None:
        """Click the responsive dtr-control toggle on a row."""
        self.dtr_controls.nth(index).click()

    def get_info_text(self) -> str:
        """Return the DataTable info status text."""
        return self.datatable_info.inner_text().strip()

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

    def select_copy_type(self, copy_type_value: str) -> None:
        """Select copy type: balance, equity, or multiplier."""
        self.copy_type_dropdown.select_option(value=copy_type_value)
        self.page.wait_for_timeout(300)

    def select_direction(self, reverse: bool = False) -> None:
        """Select trading direction: Normal Copy or Reverse Copy."""
        if reverse:
            self.direction_reverse_radio.check()
        else:
            self.direction_normal_radio.check()
        self.page.wait_for_timeout(300)

    def open_edit_copier_modal(self, index: int = 0) -> None:
        """Click edit pencil icon on a data row."""
        self.edit_buttons.nth(index).click()
        self.create_copier_modal.wait_for(state="visible", timeout=5000)

    def get_slave_accounts_rows_count(self) -> int:
        """Return the number of slave account rows inside the slave list modal."""
        return self.slave_rows.count()

