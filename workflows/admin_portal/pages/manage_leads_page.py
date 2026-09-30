"""
Admin Portal Manage Leads Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class ManageLeadsPage(BasePage):
    """Page object for Admin Manage Leads topbar, actions, table, and modals."""

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

        # Actions Bar (.leads-page-actions)
        self.actions_bar = page.locator(".leads-page-actions")
        self.lead_types_button = page.locator("#manageLeadTypes")
        self.add_lead_button = page.locator("#addNew")
        self.bulk_upload_button = page.locator("#bulkUpload")
        self.permission_edit = page.locator("#editlead")
        self.permission_delete = page.locator("#deletelead")
        self.permission_settings = page.locator("#settingsLeadType")

        # 1. Lead Types Modal (#leadTypeModal)
        self.lead_types_modal = page.locator("#leadTypeModal")
        self.lead_types_modal_title = page.locator("#leadTypeModal .modal-title")
        self.lead_type_name_input = page.locator("#leadTypeModal #lead_type_name")
        self.lead_type_submit_button = page.locator("#leadTypeModal #leadTypeSubmit")
        self.lead_type_cancel_button = page.locator("#leadTypeModal #leadTypeCancel")
        self.lead_types_close_button = page.locator(
            "#leadTypeModal button:has-text('Close'), #leadTypeModal .ux-card-close, #leadTypeModal [data-bs-dismiss='modal']"
        )
        self.lead_types_table_rows = page.locator("#leadTypeModal table tbody tr")

        # 2. Add/Edit Lead Modal (#myModal)
        self.lead_modal = page.locator("#myModal")
        self.lead_modal_title = page.locator("#myModal .modal-title")
        self.lead_name_input = page.locator("#myModal #name")
        self.lead_email_input = page.locator("#myModal #email")
        self.lead_phone_input = page.locator("#myModal #phone")
        self.lead_admin_select = page.locator("#myModal #admin_id")
        self.lead_type_select = page.locator("#myModal #lead_type_id")
        self.lead_followup_input = page.locator("#myModal #followup_date")
        self.lead_description_input = page.locator("#myModal #discription")
        self.lead_submit_button = page.locator("#myModal #formSubmit")
        self.lead_close_button = page.locator(
            "#myModal button:has-text('Close'), #myModal .ux-card-close, #myModal [data-bs-dismiss='modal']"
        )

        # 3. Bulk Upload Modal (#bulkUploadModal)
        self.bulk_upload_modal = page.locator("#bulkUploadModal")
        self.bulk_upload_modal_title = page.locator("#bulkUploadModal .modal-title")
        self.bulk_file_input = page.locator("#bulkUploadModal #bulk_file")
        self.bulk_submit_button = page.locator("#bulkUploadModal #bulkFormSubmit")
        self.bulk_close_button = page.locator(
            "#bulkUploadModal button:has-text('Close'), #bulkUploadModal .ux-card-close, #bulkUploadModal [data-bs-dismiss='modal']"
        )

        # Main Table Card & DataTable controls
        self.table_card = page.locator(".card.leads-table-card")
        self.datatable_wrapper = page.locator("#datatable_wrapper")
        self.length_dropdown = page.locator("#datatable_length select, select[name='datatable_length']")
        self.search_input = page.locator("#datatable_filter input, input[type='search'][aria-controls='datatable']")
        self.datatable = page.locator("table#datatable")
        self.table_headers = page.locator("table#datatable thead th")
        self.table_rows = page.locator("table#datatable tbody tr:not(:has(td.dataTables_empty))")
        self.empty_state_cell = page.locator("table#datatable tbody td.dataTables_empty")
        self.edit_lead_buttons = page.locator("a.btnEdit, .btn.btnEdit")
        self.delete_lead_buttons = page.locator("a.BtnDelete, .btn.BtnDelete")
        self.datatable_info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.pagination_previous = page.locator("#datatable_previous")
        self.pagination_next = page.locator("#datatable_next")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin Manage Leads page and wait for loading."""
        leads_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/leads"
        )
        self.goto(leads_url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

    def is_leads_displayed(self) -> bool:
        """Verify the Manage Leads heading is displayed."""
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

    def open_lead_types_modal(self) -> None:
        """Click Lead Types button and wait for modal."""
        self.lead_types_button.click()
        self.lead_types_modal.wait_for(state="visible", timeout=5000)

    def close_lead_types_modal(self) -> None:
        """Safely dismiss the Lead Types modal."""
        try:
            btn = self.lead_types_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('leadTypeModal');
            if (el && window.jQuery) window.jQuery(el).modal('hide');
        }""")
        self.page.wait_for_timeout(300)
        try:
            self.lead_types_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def open_add_lead_modal(self) -> None:
        """Click Add Lead button and wait for modal."""
        self.add_lead_button.click()
        self.lead_modal.wait_for(state="visible", timeout=5000)

    def close_add_lead_modal(self) -> None:
        """Safely dismiss the Add Lead modal."""
        try:
            btn = self.lead_close_button.first
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
            self.lead_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def open_bulk_upload_modal(self) -> None:
        """Click Bulk Upload button and wait for modal."""
        self.bulk_upload_button.click()
        self.bulk_upload_modal.wait_for(state="visible", timeout=5000)

    def close_bulk_upload_modal(self) -> None:
        """Safely dismiss the Bulk Upload modal."""
        try:
            btn = self.bulk_close_button.first
            if btn.is_visible():
                btn.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const el = document.getElementById('bulkUploadModal');
            if (el && window.jQuery) window.jQuery(el).modal('hide');
        }""")
        self.page.wait_for_timeout(300)
        try:
            self.bulk_upload_modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def select_page_length(self, length: str) -> None:
        """Change the page length dropdown selection."""
        self.length_dropdown.select_option(length)
        self.page.wait_for_timeout(500)

    def search_leads(self, query: str) -> None:
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

    def open_edit_lead(self, index: int = 0) -> None:
        """Click edit pencil icon on a lead row."""
        self.edit_lead_buttons.nth(index).click()
        self.lead_modal.wait_for(state="visible", timeout=5000)


