"""
Admin Portal Withdraw List (Payment Modes Configuration) Page Object.
Encapsulates navigation, tables, dropdowns, edit actions, and modals on https://stage.xtremenext.com/admin/Controlbase/managewithdraw.
Accessible via Admin Sidebar -> 'Withdraw List'.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminWithdrawListPage(BasePage):
    """Page object for Admin Console Withdraw List (Payment Modes) module."""

    URL_PATH = "/admin/Controlbase/managewithdraw"

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar & Sidebar Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Page Heading
        self.page_title_heading = page.locator("h4.page-title, .page-title, h3, h4").first

        # Top Action Button (Add Withdraw Payment Mode)
        self.add_withdraw_mode_button = page.locator("#addNew, a:has-text('Add Withdraw Payment Mode')").first

        # Search, Length & Pagination Controls
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first
        self.pagination_controls = page.locator("#datatable_paginate")
        self.pagination_info = page.locator("#datatable_info")

        # Table & Rows
        self.table = page.locator("table#datatable, table").first
        self.table_headers = page.locator("table#datatable thead th, table thead th")
        self.table_rows = page.locator("table#datatable tbody tr, table tbody tr")

        # Modal Dialog (#myModal - "Manage Withdraw Bank Details" or "Add Withdraw Payment Mode")
        self.modal = page.locator("#myModal")
        self.modal_title = self.modal.locator(".modal-title, #myModalLabel").first
        self.modal_close_button = self.modal.locator("button:has-text('Close')").first
        self.modal_cancel_button = self.modal.locator("button:has-text('Cancel')").first
        self.modal_save_button = self.modal.locator("#formSubmit, button:has-text('Save')").first
        self.modal_x_button = self.modal.locator("button.ux-card-close, button[aria-label='Close']").first

        # Modal Form Inputs
        self.modal_withdraw_name_input = self.modal.locator("#withdraw_name")
        self.modal_bank_detail_name_input = self.modal.locator("#withdraw_bank_detail_name")
        self.modal_add_bank_btn = self.modal.locator("#withdrawBankDetailAddBtn")

    def navigate(self) -> None:
        """Navigate directly to Withdraw List page."""
        parts = urlsplit(settings.admin_portal.base_url)
        target_url = f"{parts.scheme}://{parts.netloc}{self.URL_PATH}"
        self.goto(target_url)
        expect(self.table).to_be_visible(timeout=15000)
        expect(self.table_rows.first).to_be_visible(timeout=15000)

    def is_withdraw_list_displayed(self) -> bool:
        """Verify presence of withdraw list table and top action button."""
        return self.table.is_visible() and self.add_withdraw_mode_button.is_visible()

    def get_table_headers(self) -> List[str]:
        """Return list of column headers from the withdraw list table."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def sort_column(self, column_index: int) -> str:
        """Click column header to sort."""
        th = self.table_headers.nth(column_index)
        th.scroll_into_view_if_needed()
        th.click(force=True)
        self.page.wait_for_timeout(300)
        return self.table_headers.nth(column_index).get_attribute("class") or ""

    def get_entries_options(self) -> List[str]:
        """Return available entries per page options (10, 25, 50, 100)."""
        return [opt.inner_text().strip() for opt in self.entries_select.locator("option").all()]

    def select_entries(self, count: str) -> None:
        """Select number of entries to display."""
        self.entries_select.select_option(count)
        self.page.wait_for_timeout(500)

    def search(self, query: str) -> None:
        """Filter table rows using DataTables search box."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(600)

    def clear_search(self) -> None:
        """Clear search filter input."""
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return number of displayed rows in table."""
        return self.table_rows.count()

    def get_row_edit_button(self, row_index: int = 0) -> Locator:
        """Return Edit action button on a specific row."""
        return self.table_rows.nth(row_index).locator("a.btnEdit").first

    def open_edit_modal(self, row_index: int = 0) -> None:
        """Click Edit button on row to open Manage Withdraw Bank Details modal."""
        btn = self.get_row_edit_button(row_index)
        expect(btn).to_be_visible(timeout=5000)
        btn.click()
        expect(self.modal).to_be_visible(timeout=5000)
        expect(self.modal_title).to_have_text("Manage Withdraw Bank Details")

    def open_add_modal(self) -> None:
        """Open Add Withdraw Payment Mode modal dialog."""
        expect(self.add_withdraw_mode_button).to_be_visible()
        self.add_withdraw_mode_button.click()
        expect(self.modal).to_be_visible(timeout=5000)
        expect(self.modal_title).to_have_text("Add Withdraw Payment Mode")

    def close_modal(self) -> None:
        """Close modal dialog."""
        if self.modal_close_button.is_visible():
            self.modal_close_button.click()
        elif self.modal_cancel_button.is_visible():
            self.modal_cancel_button.click()
        elif self.modal_x_button.is_visible():
            self.modal_x_button.click()
        try:
            expect(self.modal).not_to_be_visible(timeout=5000)
        except Exception:
            self.page.evaluate("$('#myModal').modal('hide')")
            self.page.wait_for_timeout(500)

    def close_modal_via_x(self) -> None:
        """Close modal dialog via X button."""
        if self.modal_x_button.is_visible():
            self.modal_x_button.click()
        elif self.modal_close_button.is_visible():
            self.modal_close_button.click()
        try:
            expect(self.modal).not_to_be_visible(timeout=5000)
        except Exception:
            self.page.evaluate("$('#myModal').modal('hide')")
            self.page.wait_for_timeout(500)

    def fill_withdraw_mode_form(self, name: str) -> None:
        """Fill Name in Add Withdraw Payment Mode modal."""
        expect(self.modal).to_be_visible()
        self.modal_withdraw_name_input.fill(name)

    def get_withdraw_mode_form_values(self) -> Dict[str, str]:
        """Return dict of currently filled values in Add Withdraw Payment Mode modal."""
        return {
            "withdraw_name": self.modal_withdraw_name_input.input_value(),
        }

