"""
Admin Portal Order Edit Log Page Object (/admin/Controlbase/orderEditLog).
Encapsulates audit log datatable controls, search filtering, export buttons (CSV, PDF, Print),
and audit log record extraction.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from urllib.parse import urlsplit
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminOrderEditLogPage(BasePage):
    """Page Object representing Admin Portal Order Edit Log page."""

    URL_PATH = "/admin/Controlbase/orderEditLog"

    def __init__(self, page: Page):
        super().__init__(page)

        # Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Datatable Controls & Export Buttons
        self.table = page.locator("#datatable").first
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr")
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first
        self.info = page.locator("#datatable_info").first
        self.pagination = page.locator("#datatable_paginate").first
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty").first

        # Export Buttons
        self.csv_button = page.locator(".dt-buttons button.buttons-csv, button.buttons-csv").first
        self.pdf_button = page.locator(".dt-buttons button.buttons-pdf, button.buttons-pdf").first
        self.print_button = page.locator(".dt-buttons button.buttons-print, button.buttons-print").first

    def navigate(self) -> None:
        """Navigate to Order Edit Log page."""
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

    def search(self, query: str) -> None:
        """Search query in datatable search box."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_timeout(1000)

    def clear_search(self) -> None:
        """Clear search query in datatable search box."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.page.wait_for_timeout(500)

    def get_table_headers(self) -> List[str]:
        """Return list of header names in Order Edit Log table."""
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

    def get_edit_log_records(self) -> List[Dict[str, str]]:
        """Extract all visible edit log records from datatable."""
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll("#datatable tbody tr");
            const records = [];
            for (const row of rows) {
                const tds = Array.from(row.querySelectorAll("td")).map(td => td.innerText.trim());
                if (tds.length < 3 || tds[0].includes("No data")) continue;
                records.push({
                    s_no: tds[0] || "",
                    admin_user: tds[1] || "",
                    order_id: tds[2] || "",
                    field_name: tds[3] || "",
                    old_value: tds[4] || "",
                    new_value: tds[5] || "",
                    time: tds[6] || ""
                });
            }
            return records;
        }""")