"""
Admin Portal B Book User Margin Page Object (/admin/Controlbase/bBookUserMargin).
Encapsulates navigation, summary metrics bar, searching, column verification,
row extraction, and report export actions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminBBookUserMarginPage(BasePage):
    """Page Object representing Admin Portal B Book User Margin page."""

    URL_PATH = "/admin/Controlbase/bBookUserMargin"

    def __init__(self, page: Page):
        super().__init__(page)

        # Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Summary Bar & Controls
        self.stat_used_margin = page.locator("span:has-text('Total Used Margin'), div:has-text('Total Used Margin')").first
        self.stat_total_pnl = page.locator("span:has-text('Total P/L'), div:has-text('Total P/L')").first

        # Export Buttons & Search
        self.export_csv_btn = page.locator(".dt-buttons button.buttons-csv, button.buttons-csv").first
        self.export_pdf_btn = page.locator(".dt-buttons button.buttons-pdf, button.buttons-pdf").first
        self.export_excel_btn = page.locator(".dt-buttons button.buttons-excel, button.buttons-excel").first
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first

        # Main Table Ledger (#datatable)
        self.table = page.locator("#datatable").first
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr")
        self.pagination_controls = page.locator("#datatable_paginate")

    def navigate(self) -> None:
        """Navigate to B Book User Margin page."""
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

    def get_table_headers(self) -> List[str]:
        """Return table header column names."""
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

    def get_user_margin_row_data(self, account_id: str) -> Optional[Dict[str, str]]:
        """Find and return user margin row dictionary for account_id."""
        self.search(account_id)
        rows = self.table_rows.all()
        if not rows or self.get_table_rows_count() == 0:
            return None

        for row in rows:
            tds = row.locator("td").all_inner_texts()
            if len(tds) >= 8:
                row_acc_id = tds[2].strip()
                if str(account_id) in row_acc_id or str(account_id) in "".join(tds):
                    return {
                        "user_id": tds[0].strip(),
                        "customer_name": tds[1].strip(),
                        "account_id": row_acc_id,
                        "fund": tds[3].strip(),
                        "balance": tds[4].strip(),
                        "equity": tds[5].strip(),
                        "margin_level": tds[6].strip(),
                        "group_name": tds[7].strip(),
                        "total_pnl": tds[8].strip() if len(tds) > 8 else "",
                    }
        return None
