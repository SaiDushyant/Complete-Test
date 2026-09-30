"""
Admin Portal Book Report Page Object (/admin/Controlbase/bookReport).
Encapsulates Book type, Symbol name, and Status dropdown filters, datatable controls,
6-column book summary parsing, and report exports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminBookReportPage(BasePage):
    """Page Object representing Admin Portal Book Report page."""

    URL_PATH = "/admin/Controlbase/bookReport"

    def __init__(self, page: Page):
        super().__init__(page)

        # Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Top Filter Controls
        self.book_select = page.locator("select#book_id, select[name='book_id']").first
        self.symbol_select = page.locator("select#symbol_id, select[name='symbol_id']").first
        self.status_select = page.locator("select#table_name, select[name='table_name']").first
        self.filter_btn = page.locator("a#filterLeadReport, button#filterLeadReport, a:has-text('Filter'), button:has-text('Filter')").first
        self.refresh_btn = page.locator("a#refershBtn, button#refershBtn, a:has-text('Refresh'), button:has-text('Refresh')").first

        # Export Buttons & Length Dropdown
        self.export_csv_btn = page.locator(".dt-buttons button.buttons-csv, button.buttons-csv").first
        self.export_pdf_btn = page.locator(".dt-buttons button.buttons-pdf, button.buttons-pdf").first
        self.export_excel_btn = page.locator(".dt-buttons button.buttons-excel, button.buttons-excel").first
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first

        # Main Datatable (#datatable)
        self.table = page.locator("#datatable").first
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr")
        self.pagination_controls = page.locator("#datatable_paginate")

    def navigate(self) -> None:
        """Navigate to Book Report page."""
        parts = urlsplit(settings.admin_portal.base_url)
        url = f"{parts.scheme}://{parts.netloc}{self.URL_PATH}"
        try:
            self.goto(url, timeout=15000, wait_until="domcontentloaded")
        except Exception:
            try:
                self.goto(url, timeout=15000, wait_until="commit")
            except Exception:
                pass
        self.wait_for_table_loaded()

    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        """Wait for datatable to be visible."""
        expect(self.table).to_be_visible(timeout=timeout)
        self.page.wait_for_timeout(500)

    def dismiss_jconfirm_if_present(self) -> None:
        """Dismiss any alert dialog if present."""
        try:
            btn = self.page.locator(".jconfirm-buttons button, .jconfirm-box button").first
            if btn.is_visible():
                btn.click()
                self.page.wait_for_timeout(300)
        except Exception:
            pass

    def select_book_filter(self, book_text_or_val: str) -> None:
        """Select book type in Book dropdown."""
        expect(self.book_select).to_be_visible(timeout=10000)
        options = self.book_select.evaluate("el => Array.from(el.options).map(o => ({text: o.text.trim(), val: o.value}))")
        target_val = None
        for opt in options:
            if book_text_or_val.lower() in opt["text"].lower() or book_text_or_val.lower() == opt["val"].lower():
                target_val = opt["val"]
                break

        if target_val is not None:
            self.book_select.select_option(value=target_val)
            self.page.wait_for_timeout(300)

    def select_symbol_filter(self, symbol_name: str) -> None:
        """Select symbol in Symbol Name dropdown."""
        expect(self.symbol_select).to_be_visible(timeout=10000)
        options = self.symbol_select.evaluate("el => Array.from(el.options).map(o => ({text: o.text.trim(), val: o.value}))")
        target_val = None
        for opt in options:
            if symbol_name.lower() in opt["text"].lower() or symbol_name.lower() == opt["val"].lower():
                target_val = opt["val"]
                break

        if target_val is not None:
            self.symbol_select.select_option(value=target_val)
            self.page.wait_for_timeout(300)

    def select_status_filter(self, status: str = "Open") -> None:
        """Select order status ('Open' -> 'order', 'Closed' -> 'order_history')."""
        expect(self.status_select).to_be_visible(timeout=10000)
        val_map = {"open": "order", "closed": "order_history"}
        target_val = val_map.get(status.lower(), status)
        self.status_select.select_option(value=target_val)
        self.page.wait_for_timeout(300)

    def click_filter(self) -> None:
        """Click the Filter button and dismiss any alert dialog."""
        self.dismiss_jconfirm_if_present()
        expect(self.filter_btn).to_be_visible(timeout=10000)
        self.filter_btn.click()
        self.page.wait_for_timeout(500)
        self.dismiss_jconfirm_if_present()
        self.page.wait_for_timeout(500)

    def click_refresh(self) -> None:
        """Click the Refresh button and dismiss any alert dialog."""
        self.dismiss_jconfirm_if_present()
        expect(self.refresh_btn).to_be_visible(timeout=10000)
        self.refresh_btn.click()
        self.page.wait_for_timeout(500)
        self.dismiss_jconfirm_if_present()
        self.page.wait_for_timeout(500)

    def search(self, query: str) -> None:
        """Search query in datatable search box."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_timeout(1000)

    def get_table_headers(self) -> List[str]:
        """Return list of header names in Book Report table."""
        expect(self.table).to_be_visible(timeout=10000)
        headers = self.table_headers.all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_table_rows_count(self) -> int:
        """Return count of visible table rows."""
        rows = self.table_rows.all()
        if not rows:
            return 0
        text = rows[0].inner_text()
        if "No data available" in text or "Loading" in text or "No matching records" in text:
            return 0
        return len(rows)

    def get_book_report_records(self) -> List[Dict[str, str]]:
        """Extract all visible book summary records from datatable."""
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll("#datatable tbody tr");
            const records = [];
            for (const row of rows) {
                const tds = Array.from(row.querySelectorAll("td")).map(td => td.innerText.trim());
                if (tds.length < 4 || tds[0].includes("No data")) continue;
                records.push({
                    s_no: tds[0] || "",
                    book: tds[1] || "",
                    symbol: tds[2] || "",
                    buy: tds[3] || "",
                    sell: tds[4] || "",
                    total: tds[5] || ""
                });
            }
            return records;
        }""")
