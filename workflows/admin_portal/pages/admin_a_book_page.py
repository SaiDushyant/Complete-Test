"""
Admin Portal A Book Module Page Object (/admin/Controlbase/aBook).
Encapsulates navigation, summary metrics bar, table searching, account row details,
and Show Orders modal trigger for A Book accounts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminABookPage(BasePage):
    """Page Object for Admin Console A Book page."""

    URL_PATH = "/admin/Controlbase/aBook"

    def __init__(self, page: Page):
        super().__init__(page)

        # Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Heading & Action Buttons
        self.page_heading = page.locator(".page-title-box h4, h4.page-title, .card-title, h4:has-text('A Book')").first
        self.a_book_trade_btn = page.locator("button:has-text('A Book Trade'), a:has-text('A Book Trade')").first

        # Summary Bar Metrics
        self.summary_bar = page.locator(".card-body, .row, div:has-text('Balance:')").first
        self.stat_balance = page.locator("span:has-text('Balance'), div:has-text('Balance')").first
        self.stat_equity = page.locator("span:has-text('Equity'), div:has-text('Equity')").first
        self.stat_used_margin = page.locator("span:has-text('Used Margin'), div:has-text('Used Margin')").first
        self.stat_free_margin = page.locator("span:has-text('Free Margin'), div:has-text('Free Margin')").first
        self.stat_margin_level = page.locator("span:has-text('Margin Level'), div:has-text('Margin Level')").first
        self.stat_profit_loss = page.locator("span:has-text('Profit / Loss'), div:has-text('Profit')").first

        # Table & Export Buttons
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

        # Order Details Modal (#orderModal)
        self.order_modal = page.locator("#orderModal")
        self.order_modal_close_btn = page.locator("#orderModal .ux-order-close").first

    def navigate(self) -> None:
        """Navigate to A Book page."""
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
        """Wait for A Book table to be loaded."""
        expect(self.table).to_be_visible(timeout=timeout)
        self.page.wait_for_timeout(500)

    def search(self, query: str) -> None:
        """Search query in datatable search box."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_timeout(1000)

    def get_table_rows_count(self) -> int:
        """Return visible table row count."""
        rows = self.table_rows.all()
        if not rows:
            return 0
        text = rows[0].inner_text()
        if "No data available" in text or "Loading" in text or "No matching records" in text:
            return 0
        return len(rows)

    def open_show_orders(self, row_index: int = 0) -> None:
        """Click Show Orders for the specified row."""
        show_orders_btns = self.page.locator("#datatable tbody tr button.showOrders, button.showOrders")
        expect(show_orders_btns.nth(row_index)).to_be_visible(timeout=10000)
        show_orders_btns.nth(row_index).click()
        expect(self.order_modal).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(500)

    def close_order_modal(self) -> None:
        """Dismiss order modal cleanly using close button or Escape key."""
        close_btn = self.order_modal.locator(".ux-order-close, .close, .btn-close, button:has-text('Close')").first
        if close_btn.is_visible():
            try:
                close_btn.click()
            except Exception:
                self.page.keyboard.press("Escape")
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def get_summary_bar_metrics(self) -> Dict[str, float]:
        """Extract and parse summary bar metrics (Balance, Equity, Used Margin, Free Margin, Margin Level, Profit / Loss)."""
        return self.page.evaluate("""() => {
            const bodyText = document.body.innerText;
            const parseVal = (regex) => {
                const match = bodyText.match(regex);
                return match ? parseFloat(match[1].replace(/,/g, '')) : 0.0;
            };
            return {
                balance: parseVal(/Balance\\s*:\\s*\\$\\s*(-?[\\d,]+\\.\\d+)/i),
                equity: parseVal(/Equity\\s*:\\s*\\$\\s*(-?[\\d,]+\\.\\d+)/i),
                used_margin: parseVal(/Used Margin\\s*:\\s*\\$\\s*(-?[\\d,]+\\.\\d+)/i),
                free_margin: parseVal(/Free Margin\\s*:\\s*\\$\\s*(-?[\\d,]+\\.\\d+)/i),
                margin_level: parseVal(/Margin Level\\s*:\\s*(-?[\\d,]+\\.\\d+)%/i),
                profit_loss: parseVal(/Profit\\s*\\/\\s*Loss\\s*:\\s*\\$\\s*(-?[\\d,]+\\.\\d+)/i)
            };
        }""")

    def verify_summary_bar_math(self) -> Dict[str, Any]:
        """Verify mathematical relationships of summary bar metrics: Equity = Balance + PnL, Free Margin = Equity - Used Margin."""
        m = self.get_summary_bar_metrics()
        expected_equity = round(m["balance"] + m["profit_loss"], 2)
        equity_valid = abs(m["equity"] - expected_equity) < 0.10

        expected_free_margin = round(m["equity"] - m["used_margin"], 2)
        free_margin_valid = abs(m["free_margin"] - expected_free_margin) < 0.10

        margin_level_valid = True
        if m["used_margin"] > 0:
            expected_margin_level = round((m["equity"] / m["used_margin"]) * 100.0, 2)
            margin_level_valid = abs(m["margin_level"] - expected_margin_level) < 1.0

        return {
            "metrics": m,
            "equity_valid": equity_valid,
            "free_margin_valid": free_margin_valid,
            "margin_level_valid": margin_level_valid,
            "all_valid": equity_valid and free_margin_valid and margin_level_valid
        }

    def verify_table_rows_math(self) -> List[Dict[str, Any]]:
        """Verify for each row in datatable that Equity = Balance + Total PNL."""
        return self.page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll("#datatable tbody tr"));
            const results = [];
            for (const row of rows) {
                const tds = Array.from(row.querySelectorAll("td")).map(td => td.innerText.trim().replace(/,/g, ''));
                if (tds.length < 9 || tds[0].includes("No data")) continue;
                const balance = parseFloat(tds[4]) || 0.0;
                const equity = parseFloat(tds[5]) || 0.0;
                const total_pnl = parseFloat(tds[8]) || 0.0;
                const expected_equity = Math.round((balance + total_pnl) * 100) / 100;
                const is_valid = Math.abs(equity - expected_equity) < 0.10;
                results.push({
                    account_id: tds[2] || "",
                    balance: balance,
                    total_pnl: total_pnl,
                    equity: equity,
                    expected_equity: expected_equity,
                    is_valid: is_valid
                });
            }
            return results;
        }""")
