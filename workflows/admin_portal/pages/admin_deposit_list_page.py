"""
Admin Portal Deposit List (Payment Modes Configuration) Page Object.
Encapsulates navigation, tables, dropdowns, edit actions, and modals on https://stage.xtremenext.com/admin/Controlbase/payment.
Accessible via Admin Sidebar -> 'Deposit List'.
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


class AdminDepositListPage(BasePage):
    """Page object for Admin Console Deposit List (Payment Configuration) module."""

    URL_PATH = "/admin/Controlbase/payment"

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar & Sidebar Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Page Heading
        self.page_title_heading = page.locator("h4.page-title, .page-title, h3, h4").first

        # Top Action Button (Add Deposit Option)
        self.add_deposit_option_button = page.locator("#addNew, a:has-text('Add Deposit Option')").first

        # Search, Length & Pagination Controls
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first
        self.pagination_controls = page.locator("#datatable_paginate")
        self.pagination_info = page.locator("#datatable_info")

        # Table & Rows
        self.table = page.locator("table#datatable, table").first
        self.table_headers = page.locator("table#datatable thead th, table thead th")
        self.table_rows = page.locator("table#datatable tbody tr, table tbody tr")

        # Modal Dialog (#myModal - "Payment Form")
        self.modal = page.locator("#myModal")
        self.modal_title = self.modal.locator(".modal-title, #myModalLabel").first
        self.modal_close_button = self.modal.locator("button:has-text('Close')").first
        self.modal_cancel_button = self.modal.locator("button:has-text('Cancel')").first
        self.modal_save_button = self.modal.locator("#formSubmit, button:has-text('Save')").first
        self.modal_x_button = self.modal.locator("button.ux-card-close, button[aria-label='Close']").first

        # Modal Form Inputs
        self.modal_display_name_input = self.modal.locator("#display_name")
        self.modal_bank_status_select = self.modal.locator("#update-bank-status")
        self.modal_code_input = self.modal.locator("#code")
        self.modal_disclaimer_input = self.modal.locator("#disclaimer")
        self.modal_minimum_amount_input = self.modal.locator("#minimum_amount")
        self.modal_bank_detail_name_input = self.modal.locator("#bank_detail_name")
        self.modal_bank_detail_remarks_input = self.modal.locator("#bank_detail_remarks")
        self.modal_bank_detail_add_btn = self.modal.locator("#bankDetailAddBtn")

    def navigate(self) -> None:
        """Navigate directly to Deposit List page."""
        parts = urlsplit(settings.admin_portal.base_url)
        target_url = f"{parts.scheme}://{parts.netloc}{self.URL_PATH}"
        self.goto(target_url)
        expect(self.table).to_be_visible(timeout=15000)
        expect(self.table_rows.first).to_be_visible(timeout=15000)

    def is_deposit_list_displayed(self) -> bool:
        """Verify presence of deposit list table and top action button."""
        return self.table.is_visible() and self.add_deposit_option_button.is_visible()

    def get_table_headers(self) -> List[str]:
        """Return list of column headers from the deposit list table."""
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
        """Click Edit button on row to open Payment Form modal."""
        btn = self.get_row_edit_button(row_index)
        expect(btn).to_be_visible(timeout=5000)
        btn.click()
        expect(self.modal).to_be_visible(timeout=5000)
        expect(self.modal_title).to_have_text("Payment Form")

    def open_add_modal(self) -> None:
        """Open Add Deposit Option modal dialog."""
        expect(self.add_deposit_option_button).to_be_visible()
        self.add_deposit_option_button.click()
        expect(self.modal).to_be_visible(timeout=5000)

    def close_modal(self) -> None:
        """Close modal dialog."""
        expect(self.modal_close_button).to_be_visible()
        self.modal_close_button.click()
        expect(self.modal).not_to_be_visible(timeout=5000)

    def close_modal_via_x(self) -> None:
        """Close modal dialog via X button."""
        expect(self.modal_x_button).to_be_visible()
        self.modal_x_button.click()
        expect(self.modal).not_to_be_visible(timeout=5000)

    def fill_payment_gateway_form(
        self,
        display_name: str,
        code: str,
        disclaimer: str,
        minimum_amount: str,
        image_path: str = None,
        header_image_path: str = None,
    ) -> None:
        """Fill Gateway configuration fields when is_bank = 0 in Payment Form modal."""
        expect(self.modal).to_be_visible()
        self.modal_bank_status_select.select_option("0")
        self.page.wait_for_timeout(300)
        self.modal_display_name_input.fill(display_name)
        self.modal_code_input.fill(code)
        self.modal_disclaimer_input.fill(disclaimer)
        self.modal_minimum_amount_input.fill(minimum_amount)
        if image_path:
            self.page.locator("#image").set_input_files(image_path)
        if header_image_path:
            self.page.locator("#header_image").set_input_files(header_image_path)

    def fill_payment_bank_form(
        self,
        display_name: str,
        minimum_amount: str,
        bank_detail_name: str,
        bank_detail_remarks: str,
    ) -> None:
        """Fill Bank Transfer configuration fields when is_bank = 1 in Payment Form modal."""
        expect(self.modal).to_be_visible()
        self.modal_bank_status_select.select_option("1")
        self.page.wait_for_timeout(300)
        self.modal_display_name_input.fill(display_name)
        self.modal_minimum_amount_input.fill(minimum_amount)
        self.modal_bank_detail_name_input.fill(bank_detail_name)
        self.modal_bank_detail_remarks_input.fill(bank_detail_remarks)
        self.modal_bank_detail_add_btn.click()
        self.page.wait_for_timeout(400)

    def get_payment_form_values(self) -> Dict[str, str]:
        """Return dict of currently filled values in Payment Form modal."""
        return {
            "display_name": self.modal_display_name_input.input_value(),
            "is_bank": self.modal_bank_status_select.input_value(),
            "minimum_amount": self.modal_minimum_amount_input.input_value(),
            "code": self.modal_code_input.input_value() if self.modal_code_input.is_visible() else "",
            "disclaimer": self.modal_disclaimer_input.input_value() if self.modal_disclaimer_input.is_visible() else "",
        }

