"""
Admin Portal Symbol List Page Object.
Handles Symbol List Datatable (#datatable), Edit Modal (#myModal), and Bulk Upload Modal (#swapModal).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List
from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage


class AdminSymbolListPage(BasePage):
    """Page object for Admin Symbol List table, edit modal, and bulk upload modal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Page Header & Action Controls
        self.page_title = page.locator("h4.font-size-18:has-text('Symbol List')")
        self.sample_excel_button = page.locator("a.btn.btn-primary[href*='sample.xlsx']")
        self.bulk_upload_button = page.locator("button.bulkUpload")
        self.edit_symbols_hidden_input = page.locator("#editSymbols")

        # Datatable & Main Layout Locators (#datatable)
        self.table = page.locator("#datatable")
        self.table_wrapper = page.locator("#datatable_wrapper")
        self.headers = page.locator("#datatable thead tr th")
        self.rows = page.locator("#datatable tbody tr")

        # Datatable Controls
        self.entries_select = page.locator("select[name='datatable_length']")
        self.search_input = page.locator("#datatable_filter input")
        self.info_status = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.previous_button = page.locator("#datatable_previous")
        self.next_button = page.locator("#datatable_next")
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty")
        self.edit_buttons = page.locator("a.btnEdit")

        # Edit Symbol Form Modal (#myModal)
        self.edit_modal = page.locator("#myModal")
        self.edit_modal_title = page.locator("#myModal #myModalLabel")
        self.edit_modal_close_button = page.locator(
            "#myModal button.ux-card-close, #myModal button[data-bs-dismiss='modal'], #myModal button:has-text('Close')"
        )
        self.edit_form_submit_button = page.locator("#formSubmit")

        # Edit Form Input Fields
        self.symbol_name_input = page.locator("#symbol_name")
        self.brokerage_input = page.locator("#brokerage")
        self.abook_buy_swap_input = page.locator("#abook_buy_swap_points")
        self.abook_sell_swap_input = page.locator("#abook_sell_swap_points")
        self.bbook_buy_swap_input = page.locator("#bbook_buy_swap_points")
        self.bbook_sell_swap_input = page.locator("#bbook_sell_swap_points")

        # Bulk Upload Modal (#swapModal)
        self.bulk_modal = page.locator("#swapModal")
        self.bulk_modal_title = page.locator("#swapModal #myModalLabel")
        self.bulk_file_input = page.locator("#swapModal #file")
        self.bulk_form_submit_button = page.locator("#bulkSubmit")
        self.bulk_modal_close_button = page.locator(
            "#swapModal button.ux-card-close, #swapModal button[data-bs-dismiss='modal'], #swapModal button:has-text('Close')"
        )

    def wait_for_table_load(self, timeout: int = 10000) -> None:
        """Wait for the datatable rows or empty message to be attached in DOM."""
        try:
            self.page.wait_for_selector("#datatable tbody tr", state="attached", timeout=timeout)
        except Exception:
            pass

    def navigate(
        self,
        url: str = "https://stage.xtremenext.com/admin/Controlbase/symbolList",
    ) -> None:
        """Navigate to the Symbol List page and wait for table load."""
        candidate_urls = [
            url,
            "https://stage.xtremenext.com/admin/Controlbase/symbolList",
            "https://stage.xtremenext.com/admin/Controlbase/symbols",
            "https://stage.xtremenext.com/admin/Controlbase/symbol",
        ]
        for cand in candidate_urls:
            try:
                self.goto(cand)
                if not (self.page.locator("h1:has-text('404')").is_visible() or "Not Found" in self.page.title()):
                    break
            except Exception:
                continue
        self.wait_for_table_load()


    def is_table_displayed(self) -> bool:
        """Verify presence of datatable and search controls."""
        return self.table.is_visible() and self.search_input.is_visible()

    def search_symbol(self, query: str) -> None:
        """Filter table by search query."""
        self.clear_and_fill("#datatable_filter input", query)

    def clear_search(self) -> None:
        """Clear search input."""
        self.search_input.clear()

    def get_header_titles(self) -> List[str]:
        """Return list of table column headers."""
        return [header.inner_text().strip() for header in self.headers.all() if header.inner_text().strip()]

    def get_row_count(self) -> int:
        """Return total visible row count in table."""
        return self.rows.count()

    def select_page_length(self, value: str) -> None:
        """Select entries dropdown option (10, 25, 50, 100)."""
        self.select_option("select[name='datatable_length']", value=value)

    def open_first_edit_modal(self) -> None:
        """Click the first Edit button to open the Edit Symbol modal."""
        if self.edit_buttons.count() > 0:
            self.edit_buttons.first.click(force=True)

    def open_bulk_upload_modal(self) -> None:
        """Click the Bulk upload button to open the Swap Data modal."""
        btn = self.page.locator("button.bulkUpload, button:has-text('Bulk upload')")
        if btn.count() > 0:
            btn.first.click(force=True)


    def is_edit_modal_visible(self) -> bool:
        """Check if the edit symbol modal (#myModal) is visible."""
        return self.edit_modal.is_visible()

    def is_bulk_modal_visible(self) -> bool:
        """Check if the bulk upload modal (#swapModal) is visible."""
        return self.bulk_modal.is_visible()
