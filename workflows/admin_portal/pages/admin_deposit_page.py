"""
Admin Portal Deposit Module Page Object.
Encapsulates all controls, buttons, table ledgers, search/filters, export buttons,
pagination, sorting, and modal actions on https://stage.xtremenext.com/admin/Controlbase/deposit.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
from typing import Dict, List
from playwright.sync_api import Download, Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminDepositPage(BasePage):
    """Page object for Admin Console Deposit management module."""

    URL_PATH = "/admin/Controlbase/deposit"

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar & Sidebar Navigation Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Page Heading
        self.page_title_heading = page.locator("h4.page-title, .page-title, h3, h4").filter(
            has_text=re.compile(r"Deposit\s*Details", re.I)
        )

        # Top Action & Export Buttons
        self.add_deposit_button = page.locator("#addNew")
        self.export_buttons = page.locator(".dt-buttons button")
        self.export_csv_button = page.locator(".dt-buttons button.buttons-csv").first
        self.export_pdf_button = page.locator(".dt-buttons button.buttons-pdf").first
        self.export_excel_button = page.locator(".dt-buttons button.buttons-excel").first

        # Date Range Filter & Search Controls
        self.date_from_input = page.locator("#from")
        self.date_to_input = page.locator("#to")
        self.apply_filter_button = page.locator("#apply")
        self.clear_filter_button = page.locator("#clear")
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first

        # Deposit Ledger Table
        self.table = page.locator("table#datatable, table").first
        self.table_headers = page.locator("table#datatable thead th, table thead th")
        self.table_rows = page.locator("table#datatable tbody tr, table tbody tr")

        # Entries Length Selector & Pagination Controls
        self.entries_select = page.locator("select[name='datatable_length']").first
        self.pagination_controls = page.locator("#datatable_paginate, .dataTables_paginate")
        self.pagination_info = page.locator("#datatable_info")
        self.pagination_prev_button = page.locator("#datatable_paginate li.previous a, #datatable_paginate a:has-text('Previous')").first
        self.pagination_next_button = page.locator("#datatable_paginate li.next a, #datatable_paginate a:has-text('Next')").first

        # Modal Dialog (#myModal - "Deposit Form")
        self.modal = page.locator("#myModal")
        self.modal_title = page.locator("#myModalLabel")
        self.modal_close_button = self.modal.locator("button:has-text('Close')").first
        self.modal_x_button = self.modal.locator("button.ux-card-close, button[aria-label='Close']").first
        self.modal_save_button = self.modal.locator("#formSubmit")

        # Modal Form Fields
        self.modal_email_input = self.modal.locator("#email")
        self.modal_token_input = self.modal.locator("#token")
        self.modal_datetime_input = self.modal.locator("#t")
        self.modal_method_input = self.modal.locator("#method")
        self.modal_amount_input = self.modal.locator("#amount")
        self.modal_proof_input = self.modal.locator("#proof")
        self.modal_proof_remove_btn = self.modal.locator("#proofRemoveBtn")
        self.modal_status_select = self.modal.locator("#status_change")
        self.modal_type_select = self.modal.locator("#type")
        self.modal_reason_textarea = self.modal.locator("#Reason")

    def navigate(self) -> None:
        """Navigate directly to Admin Deposit module."""
        from urllib.parse import urlsplit
        parts = urlsplit(settings.admin_portal.base_url)
        target_url = f"{parts.scheme}://{parts.netloc}{self.URL_PATH}"
        self.goto(target_url)
        expect(self.table).to_be_visible(timeout=15000)
        expect(self.table_rows.first).to_be_visible(timeout=15000)
        expect(self.add_deposit_button).to_be_visible(timeout=10000)

    def is_deposit_page_displayed(self) -> bool:
        """Verify presence of deposit page table and top action button."""
        return self.table.is_visible() and self.add_deposit_button.is_visible()

    def get_table_headers(self) -> List[str]:
        """Return list of column headers from the deposit table."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def sort_column(self, column_index: int) -> str:
        """Scroll column header into view, click to sort, and return updated class attribute."""
        th = self.table_headers.nth(column_index)
        th.scroll_into_view_if_needed()
        th.click(force=True)
        self.page.wait_for_timeout(300)
        return self.table_headers.nth(column_index).get_attribute("class") or ""

    def get_export_button_labels(self) -> List[str]:
        """Return list of export button labels (e.g. ['CSV', 'PDF', 'Excel'])."""
        return [btn.inner_text().strip() for btn in self.export_buttons.all()]

    def export_csv(self) -> Download:
        """Click CSV export button and return Download object."""
        expect(self.export_csv_button).to_be_visible()
        with self.page.expect_download(timeout=10000) as download_info:
            self.export_csv_button.click()
        return download_info.value

    def export_pdf(self) -> Download:
        """Click PDF export button and return Download object."""
        expect(self.export_pdf_button).to_be_visible()
        with self.page.expect_download(timeout=10000) as download_info:
            self.export_pdf_button.click()
        return download_info.value

    def export_excel(self) -> Download:
        """Click Excel export button and return Download object."""
        expect(self.export_excel_button).to_be_visible()
        with self.page.expect_download(timeout=10000) as download_info:
            self.export_excel_button.click()
        return download_info.value

    def filter_by_date(self, from_date: str, to_date: str) -> None:
        """Set date inputs and click 'Go' filter button."""
        self.date_from_input.fill(from_date)
        self.date_to_input.fill(to_date)
        self.apply_filter_button.click()
        self.page.wait_for_timeout(500)

    def clear_date_filter(self) -> None:
        """Click 'Clear' filter button to reset date range."""
        self.clear_filter_button.click()
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

    def get_pagination_info(self) -> str:
        """Return pagination summary text (e.g. 'Showing 1 to 50 of 456 entries')."""
        return self.pagination_info.inner_text().strip()

    def get_total_records_count(self) -> int:
        """Parse total records count from pagination summary text."""
        info = self.get_pagination_info()
        match = re.search(r"of\s+([\d,]+)\s+entries", info, re.I)
        if match:
            return int(match.group(1).replace(",", ""))
        return self.get_row_count()

    def go_to_page(self, page_number: int) -> None:
        """Click pagination page link."""
        link = self.page.locator(f"#datatable_paginate a:has-text('{page_number}')").first
        expect(link).to_be_visible()
        link.click()
        self.page.wait_for_timeout(500)

    def go_to_next_page(self) -> None:
        """Click Next pagination link."""
        expect(self.pagination_next_button).to_be_visible()
        self.pagination_next_button.click()
        self.page.wait_for_timeout(500)

    def go_to_previous_page(self) -> None:
        """Click Previous pagination link."""
        expect(self.pagination_prev_button).to_be_visible()
        self.pagination_prev_button.click()
        self.page.wait_for_timeout(500)

    def get_first_row_data(self) -> Dict[str, str]:
        """Extract data fields from the first table row."""
        if self.table_rows.count() == 0:
            return {}
        cells = [td.inner_text().strip() for td in self.table_rows.first.locator("td").all()]
        headers = self.get_table_headers()
        data = {}
        for idx, h in enumerate(headers):
            if idx < len(cells):
                data[h] = cells[idx]
        return data

    def open_add_deposit_modal(self) -> None:
        """Click 'Add Deposit' button to open modal."""
        expect(self.add_deposit_button).to_be_visible()
        self.add_deposit_button.click()
        expect(self.modal).to_be_visible(timeout=5000)
        expect(self.modal_title).to_have_text("Deposit Form")

    def close_modal(self) -> None:
        """Click Close button inside modal dialog."""
        if self.modal_close_button.is_visible():
            self.modal_close_button.click()
        elif self.modal_x_button.is_visible():
            self.modal_x_button.click()
        try:
            expect(self.modal).not_to_be_visible(timeout=5000)
        except Exception:
            self.page.evaluate("$('#myModal').modal('hide')")
            self.page.wait_for_timeout(500)

    def close_modal_via_x(self) -> None:
        """Click 'X' icon inside modal dialog header."""
        if self.modal_x_button.is_visible():
            self.modal_x_button.click()
        elif self.modal_close_button.is_visible():
            self.modal_close_button.click()
        try:
            expect(self.modal).not_to_be_visible(timeout=5000)
        except Exception:
            self.page.evaluate("$('#myModal').modal('hide')")
            self.page.wait_for_timeout(500)

    def get_row_status_button(self, row_index: int = 0) -> Locator:
        """Return status button Locator from a specific table row."""
        return self.table_rows.nth(row_index).locator("button.fundStatusButtom").first

    def get_entries_options(self) -> List[str]:
        """Return available rows per page entries options (10, 25, 50, 100)."""
        return [opt.inner_text().strip() for opt in self.entries_select.locator("option").all()]

    def select_entries(self, count: str) -> None:
        """Select number of entries to display."""
        self.entries_select.select_option(count)
        self.page.wait_for_timeout(500)

    def get_modal_status_options(self) -> List[str]:
        """Return options available in modal status_change dropdown."""
        return [opt.inner_text().strip() for opt in self.modal_status_select.locator("option").all()]

    def get_modal_type_options(self) -> List[str]:
        """Return options available in modal type dropdown."""
        return [opt.inner_text().strip() for opt in self.modal_type_select.locator("option").all()]

    def fill_deposit_form(
        self,
        email: str,
        datetime_val: str,
        method: str,
        amount: str,
        status: str = "pending",
        reason: str = "Deposit verification",
        proof_path: str = None,
    ) -> None:
        """Fill all input fields and upload proof in Deposit Form modal."""
        expect(self.modal).to_be_visible()
        self.modal_email_input.fill(email)
        self.modal_datetime_input.fill(datetime_val)
        self.modal_method_input.fill(method)
        self.modal_amount_input.fill(amount)
        if status:
            self.modal_status_select.select_option(status)
        self.modal_reason_textarea.fill(reason)
        if proof_path:
            self.modal_proof_input.set_input_files(proof_path)
            expect(self.modal_proof_remove_btn).to_be_visible(timeout=5000)

    def get_deposit_form_values(self) -> Dict[str, str]:
        """Return dict of currently filled values in Deposit Form modal."""
        return {
            "email": self.modal_email_input.input_value(),
            "datetime": self.modal_datetime_input.input_value(),
            "method": self.modal_method_input.input_value(),
            "amount": self.modal_amount_input.input_value(),
            "status": self.modal_status_select.input_value(),
            "reason": self.modal_reason_textarea.input_value(),
        }

    def open_edit_modal(self, row_index: int = 0) -> None:
        """Click in-row edit button (a.btnEdit) to open #myModal for a pending deposit."""
        edit_btn = self.table_rows.nth(row_index).locator("a.btnEdit").first
        expect(edit_btn).to_be_visible(timeout=10000)
        edit_btn.click()
        expect(self.modal).to_be_visible(timeout=10000)
        expect(self.modal_status_select).to_be_visible(timeout=5000)

    def change_status_and_save(self, new_status: str = "success") -> None:
        """Change status dropdown in the edit modal and submit form."""
        expect(self.modal_status_select).to_be_visible(timeout=5000)
        self.modal_status_select.select_option(new_status.lower())
        self.modal_save_button.click()
        self.page.wait_for_timeout(1000)
        confirm_btn = self.page.locator(".jconfirm-buttons button, button.btn-green:has-text('Thank You!'), .swal2-confirm")
        if confirm_btn.is_visible(timeout=3000):
            confirm_btn.click()
            self.page.wait_for_timeout(1000)
        self.modal.wait_for(state="hidden", timeout=10000)

